"""
Admin API router - Administrative operations
Handles database reset and other admin functions
Version: 2.0.0
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from pathlib import Path
import shutil

from src.backend.database import get_db
from src.backend.models import GlossaryEntry, UploadedDocument, DocumentType
from src.backend.schemas import (
    MessageResponse,
    DocumentTypeResponse,
    DocumentTypeCreate,
    DocumentTypeUpdate
)
from typing import List

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
)

# Upload directory configuration
UPLOAD_DIR = Path("./data/uploads")


@router.delete("/reset-database", response_model=MessageResponse)
async def reset_database(db: Session = Depends(get_db)):
    """
    **WARNING: This will delete ALL data from the database!**

    Resets the database by:
    - Deleting all glossary entries
    - Deleting all uploaded documents
    - Removing all uploaded files from disk

    This operation cannot be undone!
    """
    try:
        # Count entries before deletion
        glossary_count = db.query(GlossaryEntry).count()
        documents_count = db.query(UploadedDocument).count()

        # Delete all uploaded files from disk
        files_deleted = 0
        if UPLOAD_DIR.exists():
            for file_path in UPLOAD_DIR.glob("*"):
                if file_path.is_file():
                    try:
                        file_path.unlink()
                        files_deleted += 1
                    except Exception as e:
                        import logging
                        logging.getLogger(__name__).warning(f"Failed to delete file {file_path}: {e}")

        # Delete all database records
        db.query(GlossaryEntry).delete()
        db.query(UploadedDocument).delete()

        # Commit the changes
        db.commit()

        # Reset auto-increment IDs (SQLite specific)
        try:
            db.execute(text("DELETE FROM sqlite_sequence WHERE name='glossary_entries'"))
            db.execute(text("DELETE FROM sqlite_sequence WHERE name='uploaded_documents'"))
            db.commit()
        except Exception as e:
            # This is not critical, so just log it
            import logging
            logging.getLogger(__name__).debug(f"Could not reset auto-increment: {e}")

        return MessageResponse(
            message=f"Database reset successful. Deleted {glossary_count} glossary entries, "
                   f"{documents_count} documents, and {files_deleted} files from disk."
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database reset failed: {str(e)}"
        )


@router.get("/stats", response_model=dict)
async def get_database_stats(db: Session = Depends(get_db)):
    """
    Get database statistics

    Returns counts of:
    - Total glossary entries
    - Total uploaded documents
    - Entries by language
    - Entries by validation status
    - Entries by source
    - Recent activity
    """
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func

        # Total counts
        total_entries = db.query(GlossaryEntry).count()
        total_documents = db.query(UploadedDocument).count()

        # Count by language (only include languages that have entries)
        entries_by_language = {}
        language_counts = db.query(
            GlossaryEntry.language,
            func.count(GlossaryEntry.id)
        ).group_by(GlossaryEntry.language).all()

        for lang, count in language_counts:
            if count > 0:
                entries_by_language[lang] = count

        # Count by validation status
        entries_by_validation = {}
        validation_counts = db.query(
            GlossaryEntry.validation_status,
            func.count(GlossaryEntry.id)
        ).group_by(GlossaryEntry.validation_status).all()

        for status, count in validation_counts:
            if count > 0:
                entries_by_validation[status] = count

        # Count by source (only include sources that have entries)
        entries_by_source = {}
        source_counts = db.query(
            GlossaryEntry.source,
            func.count(GlossaryEntry.id)
        ).group_by(GlossaryEntry.source).all()

        for source, count in source_counts:
            if count > 0:
                entries_by_source[source] = count

        # Recent activity
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())

        # Last entry created
        last_entry = db.query(GlossaryEntry).order_by(
            GlossaryEntry.creation_date.desc()
        ).first()

        # Last document uploaded
        last_document = db.query(UploadedDocument).order_by(
            UploadedDocument.uploaded_at.desc()
        ).first()

        # Count entries created today
        entries_today = db.query(GlossaryEntry).filter(
            GlossaryEntry.creation_date >= today_start
        ).count()

        # Count documents uploaded today
        documents_today = db.query(UploadedDocument).filter(
            UploadedDocument.uploaded_at >= today_start
        ).count()

        # Count uploaded files on disk
        files_on_disk = 0
        if UPLOAD_DIR.exists():
            files_on_disk = len([f for f in UPLOAD_DIR.glob("*") if f.is_file()])

        return {
            "total_glossary_entries": total_entries,
            "total_documents": total_documents,
            "files_on_disk": files_on_disk,
            "entries_by_language": entries_by_language,
            "entries_by_source": entries_by_source,
            "entries_by_validation_status": entries_by_validation,
            "recent_activity": {
                "last_entry_created": last_entry.creation_date.isoformat() if last_entry else None,
                "last_document_uploaded": last_document.uploaded_at.isoformat() if last_document else None,
                "entries_created_today": entries_today,
                "documents_uploaded_today": documents_today,
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database stats: {str(e)}"
        )


# DocumentType Management Endpoints

@router.get("/document-types", response_model=List[DocumentTypeResponse])
async def list_document_types(db: Session = Depends(get_db)):
    """
    List all document types (bilingual: EN/DE)

    Returns all available document type classifications
    """
    try:
        document_types = db.query(DocumentType).order_by(DocumentType.code).all()
        return document_types
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list document types: {str(e)}"
        )


@router.get("/document-types/{type_id}", response_model=DocumentTypeResponse)
async def get_document_type(type_id: int, db: Session = Depends(get_db)):
    """
    Get specific document type by ID
    """
    document_type = db.query(DocumentType).filter(DocumentType.id == type_id).first()

    if not document_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document type with id {type_id} not found"
        )

    return document_type


@router.post("/document-types", response_model=DocumentTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_document_type(
    document_type: DocumentTypeCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new document type

    - **code**: Unique type code (e.g., "manual", "specification")
    - **label_en**: English label
    - **label_de**: German label
    - **description**: Optional description
    """
    # Check if code already exists
    existing = db.query(DocumentType).filter(DocumentType.code == document_type.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Document type with code '{document_type.code}' already exists"
        )

    try:
        db_document_type = DocumentType(
            code=document_type.code,
            label_en=document_type.label_en,
            label_de=document_type.label_de,
            description=document_type.description
        )

        db.add(db_document_type)
        db.commit()
        db.refresh(db_document_type)

        return db_document_type
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create document type: {str(e)}"
        )


@router.put("/document-types/{type_id}", response_model=DocumentTypeResponse)
async def update_document_type(
    type_id: int,
    document_type: DocumentTypeUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing document type

    All fields are optional
    """
    db_document_type = db.query(DocumentType).filter(DocumentType.id == type_id).first()

    if not db_document_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document type with id {type_id} not found"
        )

    # Check if code is being changed and if new code already exists
    if document_type.code and document_type.code != db_document_type.code:
        existing = db.query(DocumentType).filter(DocumentType.code == document_type.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Document type with code '{document_type.code}' already exists"
            )

    try:
        # Update fields if provided
        if document_type.code is not None:
            db_document_type.code = document_type.code
        if document_type.label_en is not None:
            db_document_type.label_en = document_type.label_en
        if document_type.label_de is not None:
            db_document_type.label_de = document_type.label_de
        if document_type.description is not None:
            db_document_type.description = document_type.description

        db.commit()
        db.refresh(db_document_type)

        return db_document_type
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update document type: {str(e)}"
        )


@router.delete("/document-types/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document_type(type_id: int, db: Session = Depends(get_db)):
    """
    Delete a document type

    **Warning:** This will fail if any documents reference this type
    """
    db_document_type = db.query(DocumentType).filter(DocumentType.id == type_id).first()

    if not db_document_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document type with id {type_id} not found"
        )

    # Check if any documents are using this type
    documents_using_type = db.query(UploadedDocument).filter(
        UploadedDocument.document_type_id == type_id
    ).count()

    if documents_using_type > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete document type: {documents_using_type} document(s) are using it"
        )

    try:
        db.delete(db_document_type)
        db.commit()
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document type: {str(e)}"
        )
