"""
SQLAlchemy database models for Glossary Extraction & Validation API
Implements data model from PRT-v2.2.md Section 9
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, JSON, ForeignKey,
    CheckConstraint, Index, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class GlossaryEntry(Base):
    """
    Core glossary entry model
    Stores terminology with definitions, metadata, and validation status
    """
    __tablename__ = "glossary_entries"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Core Fields
    term = Column(String(255), nullable=False)
    definitions = Column(
        JSON,
        nullable=False,
        doc="Array of definition objects: [{text, source_doc_id, is_primary}, ...]"
    )
    language = Column(
        String(2),
        nullable=False,
        doc="ISO 639-1 language code: 'de' or 'en'"
    )

    # Source Information
    source = Column(
        String(50),
        nullable=False,
        default="internal",
        doc="Source: 'internal', 'NAMUR', 'DIN', 'ASME', 'IEC'"
    )
    source_document = Column(String(500), nullable=True)

    # Timestamps
    creation_date = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Classification
    domain_tags = Column(JSON, nullable=True, doc="Array of domain classification tags")

    # Validation Status
    validation_status = Column(
        String(20),
        nullable=False,
        default="pending"
    )

    # Neo4j Sync Status
    sync_status = Column(
        String(20),
        nullable=False,
        default="pending_sync"
    )

    # Constraints
    __table_args__ = (
        # Unique constraint: same term in same language from same source must be unique
        UniqueConstraint('term', 'language', 'source', name='uq_term_lang_source'),

        # Check constraint: language must be 'de' or 'en'
        CheckConstraint("language IN ('de', 'en')", name='ck_language'),

        # Check constraint: validation_status must be valid
        CheckConstraint(
            "validation_status IN ('pending', 'validated', 'rejected')",
            name='ck_validation_status'
        ),

        # Check constraint: source must be valid
        CheckConstraint(
            "source IN ('internal', 'NAMUR', 'DIN', 'ASME', 'IEC', 'IATE')",
            name='ck_source'
        ),

        # Check constraint: sync_status must be valid
        CheckConstraint(
            "sync_status IN ('pending_sync', 'synced', 'sync_failed')",
            name='ck_sync_status'
        ),

        # Performance indexes
        Index('idx_glossary_entry_term_lang', 'term', 'language'),
        Index('idx_glossary_entry_source', 'source'),
        Index('idx_glossary_entry_validation', 'validation_status'),
        Index('idx_glossary_entry_sync', 'sync_status'),
    )

    def __repr__(self):
        return f"<GlossaryEntry(id={self.id}, term='{self.term}', lang='{self.language}')>"


class TerminologyCache(Base):
    """
    Cache for external API responses (IATE, DeepL, etc.)
    Reduces API calls and improves performance
    """
    __tablename__ = "terminology_cache"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Cache Key
    api_name = Column(String(50), nullable=False, doc="API name: 'IATE', 'DeepL', etc.")
    query_key = Column(String(500), nullable=False, doc="Query string or hash")

    # Cache Data
    response_data = Column(JSON, nullable=False, doc="Cached API response")

    # Timestamp
    cached_at = Column(DateTime, nullable=False, default=func.now())

    # Optional expiration (can be used for cache invalidation)
    expires_at = Column(DateTime, nullable=True)

    # Constraints
    __table_args__ = (
        # Composite index for fast cache lookups
        Index('idx_cache_api_query', 'api_name', 'query_key'),
        Index('idx_cache_expires', 'expires_at'),
    )

    def __repr__(self):
        return f"<TerminologyCache(api='{self.api_name}', key='{self.query_key[:30]}...')>"


class SyncLog(Base):
    """
    Sync log for tracking Neo4j synchronization attempts
    Used for retry logic and failure analysis
    """
    __tablename__ = "sync_logs"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Reference to glossary entry
    glossary_entry_id = Column(Integer, nullable=False)

    # Sync Status
    sync_status = Column(
        String(20),
        nullable=False,
        doc="Status: 'pending', 'success', 'failed'"
    )

    # Error Information
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True, doc="Detailed error information")

    # Timestamp
    attempted_at = Column(DateTime, nullable=False, default=func.now())

    # Retry Information
    retry_count = Column(Integer, nullable=False, default=0)
    next_retry_at = Column(DateTime, nullable=True)

    # Constraints
    __table_args__ = (
        # Check constraint: sync_status must be valid
        CheckConstraint(
            "sync_status IN ('pending', 'success', 'failed')",
            name='ck_sync_log_status'
        ),

        # Performance indexes
        Index('idx_sync_log_entry', 'glossary_entry_id'),
        Index('idx_sync_log_status', 'sync_status'),
        Index('idx_sync_log_retry', 'next_retry_at'),
    )

    def __repr__(self):
        return f"<SyncLog(id={self.id}, entry_id={self.glossary_entry_id}, status='{self.sync_status}')>"


class DocumentType(Base):
    """
    Document type classification (bilingual: EN/DE)
    Admin-manageable via Admin tab
    """
    __tablename__ = "document_types"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Type Code (unique identifier)
    code = Column(String(50), nullable=False, unique=True, doc="Unique code: 'manual', 'specification', etc.")

    # Bilingual Labels
    label_en = Column(String(100), nullable=False, doc="English label")
    label_de = Column(String(100), nullable=False, doc="German label")

    # Optional Description
    description = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    documents = relationship("UploadedDocument", back_populates="document_type")

    # Constraints
    __table_args__ = (
        Index('idx_document_type_code', 'code'),
    )

    def __repr__(self):
        return f"<DocumentType(code='{self.code}', en='{self.label_en}', de='{self.label_de}')>"


class UploadedDocument(Base):
    """
    Metadata for uploaded PDF documents
    Tracks document processing status and metadata
    """
    __tablename__ = "uploaded_documents"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # File Information
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False, unique=True)
    file_size = Column(Integer, nullable=False, doc="File size in bytes")
    file_type = Column(String(100), nullable=False, doc="MIME type")

    # Document Metadata
    document_number = Column(String(100), nullable=True, unique=True, doc="Unique document number (can be empty)")
    document_type_id = Column(Integer, ForeignKey('document_types.id'), nullable=True, doc="Foreign key to DocumentType")
    document_link = Column(String(1000), nullable=True, doc="External link (URL, UNC path, file path)")

    # Upload Status
    upload_status = Column(
        String(20),
        nullable=False,
        default="pending"
    )

    # Timestamps
    uploaded_at = Column(DateTime, nullable=False, default=func.now())
    processed_at = Column(DateTime, nullable=True)

    # Processing Information
    processing_metadata = Column(
        JSON,
        nullable=True,
        doc="Processing details: pages, extracted terms, errors, etc."
    )

    # User Information (optional, for future multi-user support)
    uploaded_by = Column(String(255), nullable=True)

    # Relationships
    document_type = relationship("DocumentType", back_populates="documents")
    term_references = relationship("TermDocumentReference", back_populates="document")

    # Constraints
    __table_args__ = (
        # Check constraint: upload_status must be valid
        CheckConstraint(
            "upload_status IN ('pending', 'processing', 'completed', 'failed')",
            name='ck_upload_status'
        ),

        # Performance indexes
        Index('idx_uploaded_doc_status', 'upload_status'),
        Index('idx_uploaded_doc_date', 'uploaded_at'),
        Index('idx_uploaded_doc_number', 'document_number'),
        Index('idx_uploaded_doc_type', 'document_type_id'),
    )

    def __repr__(self):
        return f"<UploadedDocument(id={self.id}, filename='{self.filename}', status='{self.upload_status}')>"


class TermDocumentReference(Base):
    """
    Junction table tracking which documents contain which terms
    Stores rich metadata per term-document relationship
    """
    __tablename__ = "term_document_references"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    glossary_entry_id = Column(Integer, ForeignKey('glossary_entries.id'), nullable=False)
    document_id = Column(Integer, ForeignKey('uploaded_documents.id'), nullable=False)

    # Rich Metadata
    frequency = Column(Integer, nullable=False, default=1, doc="How many times term appears in document")
    page_numbers = Column(JSON, nullable=True, doc="Array of page numbers where term appears")
    context_excerpts = Column(JSON, nullable=True, doc="Array of text excerpts showing term in context")
    extraction_confidence = Column(
        JSON,
        nullable=True,
        doc="Confidence scores from extraction: {overall: 0.95, source: 'regex'}"
    )

    # Timestamp
    created_at = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    glossary_entry = relationship("GlossaryEntry", backref="document_references")
    document = relationship("UploadedDocument", back_populates="term_references")

    # Constraints
    __table_args__ = (
        # Ensure same term-document pair is unique
        UniqueConstraint('glossary_entry_id', 'document_id', name='uq_term_document'),

        # Performance indexes
        Index('idx_term_doc_ref_entry', 'glossary_entry_id'),
        Index('idx_term_doc_ref_document', 'document_id'),
        Index('idx_term_doc_ref_frequency', 'frequency'),
    )

    def __repr__(self):
        return f"<TermDocumentReference(entry_id={self.glossary_entry_id}, doc_id={self.document_id}, freq={self.frequency})>"


# Database initialization helper
def init_db(engine):
    """
    Initialize database by creating all tables

    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.create_all(bind=engine)


def drop_db(engine):
    """
    Drop all database tables (use with caution!)

    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.drop_all(bind=engine)


def seed_document_types(session):
    """
    Seed the database with default document types (bilingual: EN/DE)

    Args:
        session: SQLAlchemy session instance
    """
    default_types = [
        {
            "code": "manual",
            "label_en": "Manual",
            "label_de": "Handbuch",
            "description": "User manuals, instruction manuals, operating manuals"
        },
        {
            "code": "specification",
            "label_en": "Specification",
            "label_de": "Spezifikation",
            "description": "Technical specifications, product specifications"
        },
        {
            "code": "standard",
            "label_en": "Standard",
            "label_de": "Norm",
            "description": "Industry standards (DIN, ISO, IEC, ASME, NAMUR, etc.)"
        },
        {
            "code": "procedure",
            "label_en": "Procedure",
            "label_de": "Verfahrensanweisung",
            "description": "Standard operating procedures, work instructions"
        },
        {
            "code": "guideline",
            "label_en": "Guideline",
            "label_de": "Richtlinie",
            "description": "Guidelines, best practices, recommendations"
        },
        {
            "code": "report",
            "label_en": "Report",
            "label_de": "Bericht",
            "description": "Technical reports, analysis reports, test reports"
        },
        {
            "code": "drawing",
            "label_en": "Drawing",
            "label_de": "Zeichnung",
            "description": "Technical drawings, CAD drawings, schematics"
        },
        {
            "code": "other",
            "label_en": "Other",
            "label_de": "Sonstiges",
            "description": "Other document types not covered by standard categories"
        }
    ]

    for type_data in default_types:
        # Check if type already exists
        existing = session.query(DocumentType).filter(
            DocumentType.code == type_data["code"]
        ).first()

        if not existing:
            doc_type = DocumentType(**type_data)
            session.add(doc_type)

    session.commit()
    import logging
    logging.getLogger(__name__).info(f"Seeded {len(default_types)} document types")
