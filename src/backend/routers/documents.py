"""
Document management endpoints
Handles PDF upload, processing, and term extraction
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import time
import shutil
from datetime import datetime

from src.backend.database import get_db
from src.backend.models import UploadedDocument, GlossaryEntry
from src.backend.schemas import (
    DocumentUploadResponse,
    DocumentProcessRequest,
    DocumentProcessResponse,
    DocumentListResponse,
    MessageResponse,
    GlossaryEntryCreate
)
from src.backend.services.pdf_extractor import PDFExtractor
from src.backend.services.term_extractor import TermExtractor

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Upload directory configuration
UPLOAD_DIR = Path("./data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(..., description="PDF file to upload"),
    db: Session = Depends(get_db)
):
    """
    Upload a PDF document for processing

    - **file**: PDF file (max 50MB)

    Returns document metadata with upload status
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read file to check size
    file_content = await file.read()
    file_size = len(file_content)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename

    # Save file
    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Create database entry
    db_document = UploadedDocument(
        filename=file.filename,
        file_path=str(file_path),
        file_size=file_size,
        file_type=file.content_type or "application/pdf",
        upload_status="pending",
        processing_metadata={"original_filename": file.filename}
    )

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return db_document


@router.post("/{document_id}/process", response_model=DocumentProcessResponse)
async def process_document(
    document_id: int,
    process_request: DocumentProcessRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Process uploaded PDF document to extract terms

    - **document_id**: ID of uploaded document
    - **extract_terms**: Whether to extract terms using NLP
    - **auto_validate**: Auto-validate extracted terms
    - **language**: Document language (de/en)
    - **source**: Source classification

    Returns processing results with extracted terms count
    """
    # Get document
    document = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found"
        )

    if document.upload_status == "processing":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document is already being processed"
        )

    # Update status to processing
    document.upload_status = "processing"
    db.commit()

    start_time = time.time()
    errors = []
    extracted_text_length = 0
    terms_extracted = 0
    terms_saved = 0

    try:
        # Extract text from PDF
        pdf_extractor = PDFExtractor()
        extraction_result = pdf_extractor.extract_text(document.file_path)

        if not extraction_result["success"]:
            errors.append(f"PDF extraction failed: {extraction_result['error']}")
            document.upload_status = "failed"
            document.processing_metadata = {
                **document.processing_metadata,
                "errors": errors
            }
            db.commit()

            return DocumentProcessResponse(
                document_id=document_id,
                status="failed",
                extracted_text_length=0,
                terms_extracted=0,
                terms_saved=0,
                processing_time_seconds=time.time() - start_time,
                errors=errors
            )

        extracted_text = extraction_result["text"]
        extracted_text_length = len(extracted_text)

        # Extract terms if requested
        if process_request.extract_terms and extracted_text:
            term_extractor = TermExtractor(language=process_request.language)
            extracted_terms = term_extractor.extract_terms(
                text=extracted_text,
                min_term_length=3,
                max_term_length=100,
                min_frequency=2
            )

            terms_extracted = len(extracted_terms)

            # Save terms to glossary
            for term_data in extracted_terms:
                try:
                    # Check if term already exists
                    existing = db.query(GlossaryEntry).filter(
                        GlossaryEntry.term == term_data["term"],
                        GlossaryEntry.language == process_request.language,
                        GlossaryEntry.source == process_request.source
                    ).first()

                    if not existing:
                        # Generate definition from context
                        definition = term_extractor.generate_definition(
                            term_data["term"],
                            term_data.get("context", "")
                        )

                        # Create glossary entry
                        glossary_entry = GlossaryEntry(
                            term=term_data["term"],
                            definition=definition,
                            language=process_request.language,
                            source=process_request.source,
                            source_document=document.filename,
                            validation_status="validated" if process_request.auto_validate else "pending",
                            domain_tags=["extracted"]
                        )

                        db.add(glossary_entry)
                        terms_saved += 1

                except Exception as e:
                    errors.append(f"Failed to save term '{term_data['term']}': {str(e)}")

            db.commit()

        # Update document status
        document.upload_status = "completed"
        document.processed_at = datetime.now()
        document.processing_metadata = {
            **document.processing_metadata,
            "pages": extraction_result.get("pages", 0),
            "text_length": extracted_text_length,
            "terms_extracted": terms_extracted,
            "terms_saved": terms_saved,
            "language": process_request.language,
            "source": process_request.source,
            "errors": errors if errors else None
        }
        db.commit()

        processing_time = time.time() - start_time

        return DocumentProcessResponse(
            document_id=document_id,
            status="completed",
            extracted_text_length=extracted_text_length,
            terms_extracted=terms_extracted,
            terms_saved=terms_saved,
            processing_time_seconds=round(processing_time, 2),
            errors=errors if errors else None
        )

    except Exception as e:
        errors.append(str(e))
        document.upload_status = "failed"
        document.processing_metadata = {
            **document.processing_metadata,
            "errors": errors
        }
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(e)}"
        )


@router.get("", response_model=List[DocumentListResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all uploaded documents

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    documents = db.query(UploadedDocument)\
        .order_by(UploadedDocument.uploaded_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

    return documents


@router.get("/{document_id}", response_model=DocumentUploadResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get specific document by ID"""
    document = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found"
        )

    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete document and associated file

    - **document_id**: ID of document to delete
    """
    document = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found"
        )

    # Delete physical file
    try:
        file_path = Path(document.file_path)
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        # Log error but continue with database deletion
        print(f"Warning: Failed to delete file {document.file_path}: {e}")

    # Delete database record
    db.delete(document)
    db.commit()

    return None
