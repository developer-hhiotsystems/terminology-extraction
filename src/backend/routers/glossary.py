"""
Glossary API router - CRUD endpoints for glossary entries
Implements RESTful API for terminology management
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import csv
import json
import io
from datetime import datetime

from src.backend.database import get_db
from src.backend.base_models import GlossaryEntry
from src.backend.schemas import (
    GlossaryEntryCreate,
    GlossaryEntryUpdate,
    GlossaryEntryResponse,
    ErrorResponse
)

# Try importing pandas for Excel support
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


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
    # Convert definitions from Pydantic models to dicts for JSON storage
    definitions_json = [def_obj.model_dump() for def_obj in entry.definitions]

    db_entry = GlossaryEntry(
        term=entry.term,
        definitions=definitions_json,
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

    Search is case-insensitive and supports partial matches (wildcard).

    - **query**: Search string (searches in both term and definition)
    - **language**: Optional language filter
    """
    # Add wildcards for partial matching
    search_pattern = f"%{query}%"

    # Use ilike for case-insensitive search
    # Note: definitions is now a JSON field, so search only in term
    search_query = db.query(GlossaryEntry).filter(
        GlossaryEntry.term.ilike(search_pattern)
    )

    if language:
        search_query = search_query.filter(GlossaryEntry.language == language)

    results = search_query.all()
    return results


@router.get(
    "/count",
    summary="Get total count of glossary entries"
)
async def get_glossary_count(
    language: Optional[str] = Query(None, pattern="^(de|en)$", description="Filter by language"),
    source: Optional[str] = Query(None, description="Filter by source"),
    validation_status: Optional[str] = Query(None, description="Filter by validation status"),
    db: Session = Depends(get_db)
):
    """
    Get total count of glossary entries with optional filtering.
    Useful for pagination calculations.

    - **language**: Filter by language (de or en)
    - **source**: Filter by source
    - **validation_status**: Filter by validation status
    """
    query = db.query(GlossaryEntry)

    # Apply same filters as get_glossary_entries
    if language:
        query = query.filter(GlossaryEntry.language == language)
    if source:
        query = query.filter(GlossaryEntry.source == source)
    if validation_status:
        query = query.filter(GlossaryEntry.validation_status == validation_status)

    count = query.count()
    return {"total": count}


@router.get(
    "/export",
    summary="Export glossary entries to CSV, Excel, or JSON"
)
async def export_glossary(
    format: str = Query(..., pattern="^(csv|excel|json)$", description="Export format: csv, excel, or json"),
    language: Optional[str] = Query(None, pattern="^(de|en)$", description="Filter by language"),
    source: Optional[str] = Query(None, description="Filter by source"),
    validation_status: Optional[str] = Query(None, description="Filter by validation status"),
    db: Session = Depends(get_db)
):
    """
    Export glossary entries in various formats.

    - **format**: Export format (csv, excel, json)
    - **language**: Optional language filter
    - **source**: Optional source filter
    - **validation_status**: Optional validation status filter

    Returns a downloadable file in the requested format.
    """
    # Build query with filters
    query = db.query(GlossaryEntry)

    if language:
        query = query.filter(GlossaryEntry.language == language)
    if source:
        query = query.filter(GlossaryEntry.source == source)
    if validation_status:
        query = query.filter(GlossaryEntry.validation_status == validation_status)

    entries = query.all()

    if not entries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No entries found matching the criteria"
        )

    # Convert to dict format
    data = []
    for entry in entries:
        # Extract primary definition text for export, or join all definitions
        primary_def = next((d for d in (entry.definitions or []) if d.get('is_primary')), None)
        all_definitions = "; ".join([d.get('text', '') for d in (entry.definitions or [])])

        data.append({
            "id": entry.id,
            "term": entry.term,
            "definition": primary_def.get('text', '') if primary_def else all_definitions,
            "all_definitions": all_definitions,
            "language": entry.language,
            "source": entry.source,
            "source_document": entry.source_document,
            "validation_status": entry.validation_status,
            "sync_status": entry.sync_status,
            "domain_tags": json.dumps(entry.domain_tags) if entry.domain_tags else "[]",
            "creation_date": entry.creation_date.isoformat() if entry.creation_date else "",
            "updated_at": entry.updated_at.isoformat() if entry.updated_at else ""
        })

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Export based on format
    if format == "csv":
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=glossary_export_{timestamp}.csv"}
        )

    elif format == "json":
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        return StreamingResponse(
            iter([json_str]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=glossary_export_{timestamp}.json"}
        )

    elif format == "excel":
        if not PANDAS_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Excel export not available. Install pandas and openpyxl packages."
            )

        # Create DataFrame
        df = pd.DataFrame(data)

        # Write to Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Glossary')

        output.seek(0)
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=glossary_export_{timestamp}.xlsx"}
        )


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


@router.post(
    "/bulk-update",
    summary="Bulk update validation status for multiple entries"
)
async def bulk_update_entries(
    entry_ids: List[int] = Query(..., description="List of entry IDs to update"),
    validation_status: str = Query(..., pattern="^(pending|validated|rejected)$", description="New validation status"),
    db: Session = Depends(get_db)
):
    """
    Update validation status for multiple glossary entries at once.

    - **entry_ids**: List of entry IDs to update
    - **validation_status**: New validation status (pending, validated, rejected)

    Returns the number of updated entries.
    """
    if not entry_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No entry IDs provided"
        )

    # Update entries
    updated_count = db.query(GlossaryEntry).filter(
        GlossaryEntry.id.in_(entry_ids)
    ).update(
        {"validation_status": validation_status},
        synchronize_session=False
    )

    db.commit()

    return {
        "message": f"Successfully updated {updated_count} entries",
        "updated_count": updated_count,
        "validation_status": validation_status
    }
