# Phase 2: PDF Upload and Term Extraction

**Date:** 2025-10-17
**Status:** Implemented - Ready for Testing

## Overview

Phase 2 adds PDF document upload, text extraction, and automated term extraction using NLP. Users can upload PDF documents, extract text content, and automatically populate the glossary with technical terminology.

## New Features

### 1. PDF Text Extraction Service
- **Service:** `src/backend/services/pdf_extractor.py`
- **Library:** pdfplumber
- **Features:**
  - Extract text from all pages
  - Page-by-page extraction with error handling
  - PDF validation
  - Metadata extraction

### 2. Term Extraction Service
- **Service:** `src/backend/services/term_extractor.py`
- **Library:** spaCy (with pattern-based fallback)
- **Features:**
  - NLP-based term extraction using noun phrases and named entities
  - Pattern-based extraction (capitalizedterms, acronyms)
  - Frequency analysis with minimum threshold
  - Context extraction for each term
  - Auto-generated definitions from context

### 3. Document Management Endpoints

#### POST /api/documents/upload
Upload a PDF document for processing
- **Max file size:** 50MB
- **Allowed formats:** .pdf
- **Returns:** Document metadata with unique ID

**Request:**
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "id": 1,
  "filename": "document.pdf",
  "file_path": "./data/uploads/20251017_140000_document.pdf",
  "file_size": 245678,
  "upload_status": "pending",
  "uploaded_at": "2025-10-17T14:00:00",
  "processing_metadata": {
    "original_filename": "document.pdf"
  }
}
```

#### POST /api/documents/{document_id}/process
Process uploaded PDF to extract and save terms
- **extract_terms:** Extract terms using NLP (default: true)
- **auto_validate:** Auto-validate extracted terms (default: false)
- **language:** Document language - 'de' or 'en' (default: 'en')
- **source:** Source classification (default: 'internal')

**Request:**
```bash
curl -X POST http://localhost:8000/api/documents/1/process \
  -H "Content-Type: application/json" \
  -d '{
    "extract_terms": true,
    "auto_validate": false,
    "language": "en",
    "source": "internal"
  }'
```

**Response:**
```json
{
  "document_id": 1,
  "status": "completed",
  "extracted_text_length": 15234,
  "terms_extracted": 45,
  "terms_saved": 38,
  "processing_time_seconds": 2.34,
  "errors": null
}
```

#### GET /api/documents
List all uploaded documents with pagination

**Request:**
```bash
curl http://localhost:8000/api/documents?skip=0&limit=10
```

**Response:**
```json
[
  {
    "id": 1,
    "filename": "document.pdf",
    "file_size": 245678,
    "upload_status": "completed",
    "uploaded_at": "2025-10-17T14:00:00",
    "processed_at": "2025-10-17T14:00:05"
  }
]
```

#### GET /api/documents/{document_id}
Get specific document details

#### DELETE /api/documents/{document_id}
Delete document and associated file

## Database Updates

### UploadedDocument Table
Already defined in Phase 1, now actively used:
- `id` - Primary key
- `filename` - Original filename
- `file_path` - Server file path
- `file_size` - File size in bytes
- `file_type` - MIME type
- `upload_status` - pending | processing | completed | failed
- `uploaded_at` - Upload timestamp
- `processed_at` - Processing completion timestamp
- `processing_metadata` - JSON with processing details
- `uploaded_by` - User identifier (optional)

### GlossaryEntry Updates
New field usage:
- `source_document` - Now populated with PDF filename
- `domain_tags` - Includes ["extracted"] tag for auto-extracted terms

## Processing Pipeline

### 1. Upload
```
User uploads PDF → Validate file → Save to disk → Create DB record → Return document ID
```

### 2. Processing
```
Get document → Extract PDF text → Extract terms with NLP →
Check for duplicates → Generate definitions → Save to glossary →
Update document status
```

### 3. Term Extraction Algorithm
```
1. Load PDF with pdfplumber
2. Extract text from all pages
3. If spaCy available:
   - Extract noun phrases
   - Extract named entities
   - Filter by length (3-50 chars)
4. Else (fallback):
   - Extract capitalized terms
   - Extract acronyms
   - Extract hyphenated terms
5. Count frequencies (min 2 occurrences)
6. Extract context for each term
7. Generate definition from context
8. Save unique terms to glossary
```

## File Structure

### New Files
```
src/backend/services/
├── __init__.py
├── pdf_extractor.py       # PDF text extraction
└── term_extractor.py      # NLP term extraction

src/backend/routers/
└── documents.py           # Document management endpoints

data/uploads/              # PDF upload directory
docs/PHASE2_PDF_PROCESSING.md  # This file
```

### Modified Files
```
src/backend/app.py         # Added documents router
src/backend/schemas.py     # Added document schemas
```

## Dependencies

### Required (already in requirements-core.txt)
- pdfplumber==0.10.3 - PDF text extraction
- python-multipart==0.0.6 - File upload support

### Optional (for enhanced NLP)
- spacy - NLP processing
  - en_core_web_sm - English model
  - de_core_news_sm - German model

**Note:** Currently uses pattern-based fallback when spaCy unavailable

## Testing

### Manual Testing

1. **Upload a PDF:**
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@test.pdf"
```

2. **Process the PDF:**
```bash
curl -X POST http://localhost:8000/api/documents/1/process \
  -H "Content-Type: application/json" \
  -d '{"extract_terms": true, "language": "en"}'
```

3. **Check extracted terms:**
```bash
curl http://localhost:8000/api/glossary?source=internal
```

4. **List documents:**
```bash
curl http://localhost:8000/api/documents
```

### Via Swagger UI
1. Navigate to http://localhost:8000/docs
2. Find "documents" section
3. Test each endpoint interactively

## Configuration

### File Upload Limits
```python
UPLOAD_DIR = "./data/uploads"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".pdf"}
```

### Term Extraction Parameters
```python
min_term_length = 3       # Minimum chars
max_term_length = 50      # Maximum chars
min_frequency = 2         # Minimum occurrences
context_length = 100      # Context window chars
```

## Error Handling

### Upload Errors
- `400 Bad Request` - Invalid file type
- `413 Request Entity Too Large` - File exceeds 50MB
- `500 Internal Server Error` - Save failed

### Processing Errors
- `404 Not Found` - Document ID doesn't exist
- `409 Conflict` - Document already processing
- `500 Internal Server Error` - Extraction/processing failed

All errors include descriptive `detail` messages

## API Response Schemas

### DocumentUploadResponse
```python
{
  "id": int,
  "filename": str,
  "file_path": str,
  "file_size": int,
  "upload_status": str,  # pending | processing | completed | failed
  "uploaded_at": datetime,
  "processing_metadata": dict | null
}
```

### DocumentProcessResponse
```python
{
  "document_id": int,
  "status": str,
  "extracted_text_length": int,
  "terms_extracted": int,
  "terms_saved": int,
  "processing_time_seconds": float,
  "errors": list[str] | null
}
```

## Future Enhancements

- [ ] Batch document processing
- [ ] OCR support for scanned PDFs (pytesseract)
- [ ] Custom term extraction rules
- [ ] Background task processing with Celery
- [ ] Document preview/thumbnail generation
- [ ] Multi-language NLP models
- [ ] Term relationship detection
- [ ] Definition quality scoring

## Integration Notes

### With Phase 1 (CRUD API)
- Extracted terms automatically populate glossary
- Duplicate detection prevents redundant entries
- Source document tracked in `source_document` field

### With Phase 3 (React Frontend - Planned)
- File upload component with drag-and-drop
- Processing progress indicators
- Term review and validation UI
- Bulk term approval/rejection

### With Phase 4 (Neo4j Graph - Planned)
- Terms auto-synced to graph database
- Relationship extraction from document context
- Visual term network exploration

## Troubleshooting

### spaCy Warning
```
spaCy not available, using pattern-based extraction
```
**Solution:** Install spaCy and language models
```bash
pip install spacy
python -m spacy download en_core_web_sm
python -m spacy download de_core_news_sm
```

### Auto-reload Not Working
Uvicorn's auto-reload may not detect changes immediately on Windows.
**Solution:** Manually restart server:
```bash
taskkill /F /IM python.exe
.\\venv\\Scripts\\python src\\backend\\app.py
```

### Upload Directory Missing
**Solution:** Directory created automatically, or run:
```bash
mkdir data\uploads
```

## Performance

### Benchmarks (Estimated)
- **Small PDF (1-5 pages):** ~0.5-1s processing time
- **Medium PDF (10-20 pages):** ~2-4s processing time
- **Large PDF (50+ pages):** ~10-15s processing time

### Optimization Tips
- Set `min_frequency` higher for long documents
- Use `auto_validate: true` to skip manual review
- Process documents asynchronously (future enhancement)

## Security Considerations

- File type validation prevents malicious uploads
- File size limit prevents DOS attacks
- Unique filenames prevent overwrite attacks
- File path sanitization prevents directory traversal
- Upload directory isolated from application code

## License & Attribution

- pdfplumber: MIT License
- spaCy: MIT License

---

**Status:** Implementation Complete ✅
**Next Phase:** React Frontend Development
