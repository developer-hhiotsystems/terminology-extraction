"""
Pydantic schemas for request/response validation
Defines data models for API endpoints
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.backend.constants import (
    LANGUAGE_PATTERN,
    ALLOWED_SOURCES,
    VALIDATION_STATUS_PATTERN,
    SYNC_STATUS_PATTERN,
    DEFAULT_SOURCE,
    DEFAULT_LANGUAGE
)


class DefinitionObject(BaseModel):
    """Schema for a single definition object"""
    text: str = Field(..., min_length=1, description="Definition text")
    source_doc_id: Optional[int] = Field(None, description="Source document ID")
    is_primary: bool = Field(default=False, description="Whether this is the primary definition")


class GlossaryEntryBase(BaseModel):
    """Base schema for glossary entry with common fields"""
    term: str = Field(..., min_length=1, max_length=255, description="The terminology term")
    definitions: List[DefinitionObject] = Field(..., min_length=1, description="Array of definition objects")
    language: str = Field(..., pattern=LANGUAGE_PATTERN, description="Language code: 'de' or 'en'")
    source: str = Field(default=DEFAULT_SOURCE, description="Source of the term")
    source_document: Optional[str] = Field(None, max_length=500, description="Source document path")
    domain_tags: Optional[List[str]] = Field(None, description="Domain classification tags")

    @field_validator('source')
    @classmethod
    def validate_source(cls, v):
        """Validate source is one of allowed values"""
        if v not in ALLOWED_SOURCES:
            raise ValueError(f"Source must be one of: {', '.join(ALLOWED_SOURCES)}")
        return v


class GlossaryEntryCreate(GlossaryEntryBase):
    """Schema for creating a new glossary entry"""
    pass


class GlossaryEntryUpdate(BaseModel):
    """Schema for updating an existing glossary entry (all fields optional)"""
    term: Optional[str] = Field(None, min_length=1, max_length=255)
    definitions: Optional[List[DefinitionObject]] = Field(None, min_length=1)
    language: Optional[str] = Field(None, pattern=LANGUAGE_PATTERN)
    source: Optional[str] = None
    source_document: Optional[str] = Field(None, max_length=500)
    domain_tags: Optional[List[str]] = None
    validation_status: Optional[str] = Field(None, pattern=VALIDATION_STATUS_PATTERN)
    sync_status: Optional[str] = Field(None, pattern=SYNC_STATUS_PATTERN)

    @field_validator('source')
    @classmethod
    def validate_source(cls, v):
        """Validate source if provided"""
        if v is not None:
            if v not in ALLOWED_SOURCES:
                raise ValueError(f"Source must be one of: {', '.join(ALLOWED_SOURCES)}")
        return v


class GlossaryEntryResponse(GlossaryEntryBase):
    """Schema for glossary entry response"""
    id: int
    validation_status: str
    sync_status: str
    creation_date: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}  # Enables ORM mode for SQLAlchemy models


class GlossaryEntryList(BaseModel):
    """Schema for list of glossary entries"""
    items: List[GlossaryEntryResponse]
    total: int


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str


class MessageResponse(BaseModel):
    """Schema for simple message responses"""
    message: str


# Document Upload Schemas

class DocumentUploadResponse(BaseModel):
    """Schema for document upload response"""
    id: int
    filename: str
    file_path: str
    file_size: int
    upload_status: str
    uploaded_at: datetime
    processing_metadata: Optional[dict] = None
    document_number: Optional[str] = None
    document_type_id: Optional[int] = None
    document_link: Optional[str] = None

    model_config = {"from_attributes": True}


class DocumentProcessRequest(BaseModel):
    """Schema for document processing request"""
    extract_terms: bool = Field(default=True, description="Extract terms using NLP")
    auto_validate: bool = Field(default=False, description="Auto-validate extracted terms")
    language: str = Field(default=DEFAULT_LANGUAGE, pattern=LANGUAGE_PATTERN, description="Document language")
    source: str = Field(default=DEFAULT_SOURCE, description="Source classification")

    @field_validator('source')
    @classmethod
    def validate_source(cls, v):
        """Validate source if provided"""
        if v not in ALLOWED_SOURCES:
            raise ValueError(f"Source must be one of: {', '.join(ALLOWED_SOURCES)}")
        return v


class DocumentProcessResponse(BaseModel):
    """Schema for document processing response"""
    document_id: int
    status: str
    extracted_text_length: int
    terms_extracted: int
    terms_saved: int
    processing_time_seconds: float
    errors: Optional[List[str]] = None


class DocumentUpdateRequest(BaseModel):
    """Schema for updating document metadata"""
    document_number: Optional[str] = Field(None, max_length=100, description="Unique document number")
    document_type_id: Optional[int] = Field(None, description="Document type ID")
    document_link: Optional[str] = Field(None, max_length=1000, description="External link (URL, UNC path, file path)")


class DocumentListResponse(BaseModel):
    """Schema for document list response"""
    id: int
    filename: str
    file_size: int
    upload_status: str
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    document_number: Optional[str] = None
    document_type_id: Optional[int] = None
    document_link: Optional[str] = None

    model_config = {"from_attributes": True}


class BatchUploadResult(BaseModel):
    """Schema for individual file upload result in batch"""
    filename: str
    success: bool
    document: Optional[DocumentUploadResponse] = None
    error: Optional[str] = None


class BatchUploadResponse(BaseModel):
    """Schema for batch upload response"""
    total_files: int
    successful: int
    failed: int
    results: List[BatchUploadResult]


# DocumentType Schemas

class DocumentTypeBase(BaseModel):
    """Base schema for document type"""
    code: str = Field(..., min_length=1, max_length=50, description="Unique type code")
    label_en: str = Field(..., min_length=1, max_length=100, description="English label")
    label_de: str = Field(..., min_length=1, max_length=100, description="German label")
    description: Optional[str] = Field(None, description="Optional description")


class DocumentTypeCreate(DocumentTypeBase):
    """Schema for creating a new document type"""
    pass


class DocumentTypeUpdate(BaseModel):
    """Schema for updating a document type (all fields optional)"""
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    label_en: Optional[str] = Field(None, min_length=1, max_length=100)
    label_de: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class DocumentTypeResponse(DocumentTypeBase):
    """Schema for document type response"""
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# TermDocumentReference Schemas

class TermDocumentReferenceResponse(BaseModel):
    """Schema for term-document reference response"""
    id: int
    glossary_entry_id: int
    document_id: int
    frequency: int
    page_numbers: Optional[List[int]] = None
    context_excerpts: Optional[List[str]] = None
    extraction_confidence: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}
