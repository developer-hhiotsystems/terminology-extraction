"""
Pydantic schemas for request/response validation
Defines data models for API endpoints
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class GlossaryEntryBase(BaseModel):
    """Base schema for glossary entry with common fields"""
    term: str = Field(..., min_length=1, max_length=255, description="The terminology term")
    definition: str = Field(..., min_length=1, description="Definition of the term")
    language: str = Field(..., pattern="^(de|en)$", description="Language code: 'de' or 'en'")
    source: str = Field(default="internal", description="Source of the term")
    source_document: Optional[str] = Field(None, max_length=500, description="Source document path")
    domain_tags: Optional[List[str]] = Field(None, description="Domain classification tags")

    @field_validator('source')
    @classmethod
    def validate_source(cls, v):
        """Validate source is one of allowed values"""
        allowed_sources = ['internal', 'NAMUR', 'DIN', 'ASME', 'IEC', 'IATE']
        if v not in allowed_sources:
            raise ValueError(f"Source must be one of: {', '.join(allowed_sources)}")
        return v


class GlossaryEntryCreate(GlossaryEntryBase):
    """Schema for creating a new glossary entry"""
    pass


class GlossaryEntryUpdate(BaseModel):
    """Schema for updating an existing glossary entry (all fields optional)"""
    term: Optional[str] = Field(None, min_length=1, max_length=255)
    definition: Optional[str] = Field(None, min_length=1)
    language: Optional[str] = Field(None, pattern="^(de|en)$")
    source: Optional[str] = None
    source_document: Optional[str] = Field(None, max_length=500)
    domain_tags: Optional[List[str]] = None
    validation_status: Optional[str] = Field(None, pattern="^(pending|validated|rejected)$")
    sync_status: Optional[str] = Field(None, pattern="^(pending_sync|synced|sync_failed)$")

    @field_validator('source')
    @classmethod
    def validate_source(cls, v):
        """Validate source if provided"""
        if v is not None:
            allowed_sources = ['internal', 'NAMUR', 'DIN', 'ASME', 'IEC', 'IATE']
            if v not in allowed_sources:
                raise ValueError(f"Source must be one of: {', '.join(allowed_sources)}")
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
