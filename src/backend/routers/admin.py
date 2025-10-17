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
from src.backend.models import GlossaryEntry, UploadedDocument
from src.backend.schemas import MessageResponse

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
                        print(f"Warning: Failed to delete file {file_path}: {e}")

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
            print(f"Note: Could not reset auto-increment: {e}")

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
            UploadedDocument.upload_date.desc()
        ).first()

        # Count entries created today
        entries_today = db.query(GlossaryEntry).filter(
            GlossaryEntry.creation_date >= today_start
        ).count()

        # Count documents uploaded today
        documents_today = db.query(UploadedDocument).filter(
            UploadedDocument.upload_date >= today_start
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
                "last_document_uploaded": last_document.upload_date.isoformat() if last_document else None,
                "entries_created_today": entries_today,
                "documents_uploaded_today": documents_today,
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database stats: {str(e)}"
        )
