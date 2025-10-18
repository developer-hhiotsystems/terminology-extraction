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
from src.backend.models import UploadedDocument, GlossaryEntry, TermDocumentReference
from src.backend.schemas import (
    DocumentUploadResponse,
    DocumentProcessRequest,
    DocumentProcessResponse,
    DocumentListResponse,
    DocumentUpdateRequest,
    MessageResponse,
    GlossaryEntryCreate,
    BatchUploadResponse,
    BatchUploadResult
)
from src.backend.services.pdf_extractor import PDFExtractor
from src.backend.services.term_extractor import TermExtractor
from src.backend.services.term_validator import create_strict_validator

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


@router.post("/upload-batch", response_model=BatchUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_documents_batch(
    files: List[UploadFile] = File(..., description="Multiple PDF files to upload"),
    db: Session = Depends(get_db)
):
    """
    Upload multiple PDF documents in batch

    - **files**: List of PDF files (max 50MB each, max 20 files per batch)

    Returns results for all uploaded files (success/failure for each)
    """
    MAX_BATCH_SIZE = 20

    if len(files) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many files. Maximum batch size: {MAX_BATCH_SIZE}"
        )

    results = []
    successful = 0
    failed = 0

    for file in files:
        try:
            # Validate file extension
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                results.append(BatchUploadResult(
                    filename=file.filename,
                    success=False,
                    error=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
                ))
                failed += 1
                continue

            # Read file to check size
            file_content = await file.read()
            file_size = len(file_content)

            if file_size > MAX_FILE_SIZE:
                results.append(BatchUploadResult(
                    filename=file.filename,
                    success=False,
                    error=f"File too large. Max: {MAX_FILE_SIZE / 1024 / 1024}MB"
                ))
                failed += 1
                continue

            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            safe_filename = f"{timestamp}_{file.filename}"
            file_path = UPLOAD_DIR / safe_filename

            # Save file
            with open(file_path, "wb") as f:
                f.write(file_content)

            # Create database entry
            db_document = UploadedDocument(
                filename=file.filename,
                file_path=str(file_path),
                file_size=file_size,
                file_type=file.content_type or "application/pdf",
                upload_status="pending",
                processing_metadata={"original_filename": file.filename, "batch_upload": True}
            )

            db.add(db_document)
            db.commit()
            db.refresh(db_document)

            results.append(BatchUploadResult(
                filename=file.filename,
                success=True,
                document=DocumentUploadResponse.model_validate(db_document)
            ))
            successful += 1

        except Exception as e:
            results.append(BatchUploadResult(
                filename=file.filename,
                success=False,
                error=str(e)
            ))
            failed += 1
            # Rollback transaction for this file
            db.rollback()

    return BatchUploadResponse(
        total_files=len(files),
        successful=successful,
        failed=failed,
        results=results
    )


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
        # Extract text from PDF page-by-page for better tracking
        pdf_extractor = PDFExtractor()
        extraction_result = pdf_extractor.extract_text_by_page(document.file_path)

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

        # Combine all page texts for term extraction
        pages_data = extraction_result["pages"]
        extracted_text = "\n\n".join([page["text"] for page in pages_data])
        extracted_text_length = len(extracted_text)

        # Extract terms if requested
        if process_request.extract_terms and extracted_text:
            # Use strict validator for higher quality term extraction
            strict_validator = create_strict_validator(language=process_request.language)
            term_extractor = TermExtractor(language=process_request.language, validator=strict_validator)
            extracted_terms = term_extractor.extract_terms(
                text=extracted_text,
                min_term_length=3,
                max_term_length=100,
                min_frequency=1,  # Changed from 2 to 1 to extract terms from shorter documents
                pages_data=pages_data  # Pass page data for page number tracking
            )

            terms_extracted = len(extracted_terms)

            # Save terms to glossary with document references
            for term_data in extracted_terms:
                try:
                    # Generate definition using NLP patterns (Phase 2) with fallback to context (Phase 1)
                    definition_text = term_extractor.generate_definition(
                        term_data["term"],
                        term_data.get("context", ""),
                        term_data.get("complete_sentence", ""),
                        term_data.get("pages", []),
                        full_text=extracted_text  # Pass full text for NLP pattern matching
                    )

                    # Check if term already exists
                    existing = db.query(GlossaryEntry).filter(
                        GlossaryEntry.term == term_data["term"],
                        GlossaryEntry.language == process_request.language,
                        GlossaryEntry.source == process_request.source
                    ).first()

                    if not existing:
                        # Create new glossary entry with definitions array
                        glossary_entry = GlossaryEntry(
                            term=term_data["term"],
                            definitions=[{
                                "text": definition_text,
                                "source_doc_id": document_id,
                                "is_primary": True
                            }],
                            language=process_request.language,
                            source=process_request.source,
                            source_document=document.filename,
                            validation_status="validated" if process_request.auto_validate else "pending",
                            domain_tags=["extracted"]
                        )

                        db.add(glossary_entry)
                        db.flush()  # Get the ID without committing
                        terms_saved += 1
                        glossary_entry_id = glossary_entry.id
                    else:
                        glossary_entry_id = existing.id

                        # Add new definition to existing entry if it doesn't already exist from this doc
                        existing_defs = existing.definitions if existing.definitions else []
                        has_def_from_doc = any(d.get("source_doc_id") == document_id for d in existing_defs)

                        if not has_def_from_doc:
                            # Set all existing definitions to is_primary=False if this is the first one
                            for def_obj in existing_defs:
                                def_obj["is_primary"] = False

                            existing_defs.append({
                                "text": definition_text,
                                "source_doc_id": document_id,
                                "is_primary": len(existing_defs) == 0  # Primary if it's the first definition
                            })
                            existing.definitions = existing_defs

                    # Create or update TermDocumentReference
                    term_doc_ref = db.query(TermDocumentReference).filter(
                        TermDocumentReference.glossary_entry_id == glossary_entry_id,
                        TermDocumentReference.document_id == document_id
                    ).first()

                    if not term_doc_ref:
                        # Create new reference
                        term_doc_ref = TermDocumentReference(
                            glossary_entry_id=glossary_entry_id,
                            document_id=document_id,
                            frequency=term_data.get("frequency", 1),
                            page_numbers=term_data.get("pages", []),
                            context_excerpts=[term_data.get("context", "")][:3],  # Limit to 3 contexts
                            extraction_confidence={
                                "overall": 0.85,  # Default confidence
                                "source": "regex_extraction"
                            }
                        )
                        db.add(term_doc_ref)
                    else:
                        # Update existing reference
                        term_doc_ref.frequency = term_data.get("frequency", 1)
                        if term_data.get("pages"):
                            term_doc_ref.page_numbers = term_data.get("pages", [])
                        if term_data.get("context"):
                            contexts = term_doc_ref.context_excerpts or []
                            if term_data["context"] not in contexts:
                                contexts.append(term_data["context"])
                            term_doc_ref.context_excerpts = contexts[:3]  # Limit to 3

                except Exception as e:
                    errors.append(f"Failed to save term '{term_data['term']}': {str(e)}")

            db.commit()

        # Update document status
        document.upload_status = "completed"
        document.processed_at = datetime.now()
        document.processing_metadata = {
            **document.processing_metadata,
            "pages": extraction_result.get("total_pages", 0),
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


@router.put("/{document_id}", response_model=DocumentUploadResponse)
async def update_document(
    document_id: int,
    update_data: DocumentUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update document metadata (number, type, link)

    - **document_id**: ID of document to update
    - **document_number**: Optional unique document number
    - **document_type_id**: Optional document type ID
    - **document_link**: Optional external link (URL, UNC path, file path)
    """
    document = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found"
        )

    # Update only provided fields
    update_dict = update_data.model_dump(exclude_unset=True)

    # Check for duplicate document_number if being updated
    if 'document_number' in update_dict and update_dict['document_number']:
        existing = db.query(UploadedDocument).filter(
            UploadedDocument.document_number == update_dict['document_number'],
            UploadedDocument.id != document_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Document number '{update_dict['document_number']}' already exists"
            )

    for field, value in update_dict.items():
        setattr(document, field, value)

    try:
        db.commit()
        db.refresh(document)
        return document
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update document: {str(e)}"
        )


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
