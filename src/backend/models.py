"""
SQLAlchemy database models for Glossary Extraction & Validation API
Implements data model from PRT-v2.2.md Section 9
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, JSON,
    CheckConstraint, Index, UniqueConstraint
)
from sqlalchemy.orm import declarative_base
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
    definition = Column(Text, nullable=False)
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
    )

    def __repr__(self):
        return f"<UploadedDocument(id={self.id}, filename='{self.filename}', status='{self.upload_status}')>"


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
