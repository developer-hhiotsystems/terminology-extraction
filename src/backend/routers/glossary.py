"""
Glossary API router - CRUD endpoints for glossary entries
Implements RESTful API for terminology management
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from src.backend.database import get_db
from src.backend.models import GlossaryEntry
from src.backend.schemas import (
    GlossaryEntryCreate,
    GlossaryEntryUpdate,
    GlossaryEntryResponse,
    ErrorResponse
)


router = APIRouter(
    prefix="/api/glossary",
    tags=["glossary"],
    responses={404: {"model": ErrorResponse}}
)


@router.post(
    "",
    response_model=GlossaryEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new glossary entry",
    responses={
        201: {"description": "Glossary entry created successfully"},
        409: {"description": "Entry already exists (duplicate term+language+source)"}
    }
)
async def create_glossary_entry(
    entry: GlossaryEntryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new glossary entry.

    - **term**: The terminology term (required)
    - **definition**: Definition of the term (required)
    - **language**: Language code - 'de' or 'en' (required)
    - **source**: Source of the term (default: 'internal')
    - **source_document**: Path to source document (optional)
    - **domain_tags**: List of domain tags (optional)
    """
    # Check for duplicate (term + language + source must be unique)
    existing = db.query(GlossaryEntry).filter(
        GlossaryEntry.term == entry.term,
        GlossaryEntry.language == entry.language,
        GlossaryEntry.source == entry.source
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Entry '{entry.term}' already exists for language '{entry.language}' from source '{entry.source}'"
        )

    # Create new entry
    db_entry = GlossaryEntry(
        term=entry.term,
        definition=entry.definition,
        language=entry.language,
        source=entry.source,
        source_document=entry.source_document,
        domain_tags=entry.domain_tags
    )

    try:
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        return db_entry
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Database constraint violation - entry may already exist"
        )


@router.get(
    "",
    response_model=List[GlossaryEntryResponse],
    summary="Get all glossary entries with optional filters"
)
async def get_glossary_entries(
    language: Optional[str] = Query(None, pattern="^(de|en)$", description="Filter by language"),
    source: Optional[str] = Query(None, description="Filter by source"),
    validation_status: Optional[str] = Query(None, description="Filter by validation status"),
    skip: int = Query(0, ge=0, description="Number of entries to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of entries to return"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all glossary entries with optional filtering.

    - **language**: Filter by language (de or en)
    - **source**: Filter by source (internal, NAMUR, DIN, ASME, IEC, IATE)
    - **validation_status**: Filter by validation status
    - **skip**: Pagination - number of entries to skip
    - **limit**: Pagination - maximum entries to return (default: 100, max: 1000)
    """
    query = db.query(GlossaryEntry)

    # Apply filters
    if language:
        query = query.filter(GlossaryEntry.language == language)
    if source:
        query = query.filter(GlossaryEntry.source == source)
    if validation_status:
        query = query.filter(GlossaryEntry.validation_status == validation_status)

    # Apply pagination
    entries = query.offset(skip).limit(limit).all()
    return entries


@router.get(
    "/search",
    response_model=List[GlossaryEntryResponse],
    summary="Search glossary entries by term or definition"
)
async def search_glossary_entries(
    query: str = Query(..., min_length=1, description="Search query string"),
    language: Optional[str] = Query(None, pattern="^(de|en)$", description="Filter by language"),
    db: Session = Depends(get_db)
):
    """
    Search glossary entries by term or definition.

    - **query**: Search string (searches in both term and definition)
    - **language**: Optional language filter
    """
    search_query = db.query(GlossaryEntry).filter(
        (GlossaryEntry.term.contains(query)) |
        (GlossaryEntry.definition.contains(query))
    )

    if language:
        search_query = search_query.filter(GlossaryEntry.language == language)

    results = search_query.all()
    return results


@router.get(
    "/{entry_id}",
    response_model=GlossaryEntryResponse,
    summary="Get a specific glossary entry by ID"
)
async def get_glossary_entry(
    entry_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific glossary entry by its ID.

    - **entry_id**: The unique identifier of the glossary entry
    """
    entry = db.query(GlossaryEntry).filter(GlossaryEntry.id == entry_id).first()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Glossary entry with id {entry_id} not found"
        )

    return entry


@router.put(
    "/{entry_id}",
    response_model=GlossaryEntryResponse,
    summary="Update an existing glossary entry"
)
async def update_glossary_entry(
    entry_id: int,
    entry_update: GlossaryEntryUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing glossary entry.

    - **entry_id**: The unique identifier of the entry to update
    - All fields are optional - only provided fields will be updated
    """
    db_entry = db.query(GlossaryEntry).filter(GlossaryEntry.id == entry_id).first()

    if not db_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Glossary entry with id {entry_id} not found"
        )

    # Update only provided fields
    update_data = entry_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_entry, field, value)

    try:
        db.commit()
        db.refresh(db_entry)
        return db_entry
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Database constraint violation - check unique constraints"
        )


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a glossary entry"
)
async def delete_glossary_entry(
    entry_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a glossary entry by its ID.

    - **entry_id**: The unique identifier of the entry to delete
    """
    db_entry = db.query(GlossaryEntry).filter(GlossaryEntry.id == entry_id).first()

    if not db_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Glossary entry with id {entry_id} not found"
        )

    db.delete(db_entry)
    db.commit()
    return None
