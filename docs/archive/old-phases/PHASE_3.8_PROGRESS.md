# Phase 3.8: Multi-Document Term Tracking

**Status:** In Progress
**Started:** 2025-10-17
**Last Updated:** 2025-10-17

---

## Overview

Implementing comprehensive multi-document term tracking system to address the question: "If a term exists in 2 documents, how will it be displayed?"

## Design Decisions Made

### Decision 1: Definition Handling
**Choice:** Option B - Store all definitions as array
**Implementation:** JSON field `definitions` with structure:
```json
[
  {
    "text": "Definition text here",
    "source_doc_id": 123,
    "is_primary": true
  }
]
```

**Future Enhancement:** LLM-assisted definition merging (documented in FUTURE_IMPROVEMENTS.md)

### Decision 2: Document Types
**Choice:** Bilingual (EN/DE), Admin-manageable via Admin tab
**Default Types:** 8 types seeded:
- manual, specification, standard, procedure, guideline, report, drawing, other

### Decision 3: Document Number
**Choice:** Unique or empty (nullable with unique constraint)

### Decision 4: Link Validation
**Choice:** Flexible validation - Accept URLs, UNC paths, file:// paths

### Decision 5: Document Detail Page
**Choice:** Option C - Dedicated page `/documents/:id` with embedded PDF viewer

### Decision 6: PDF Display Method
**Choice:** Option C - PDF.js with native iframe fallback

---

## Database Changes

### ✅ COMPLETED

#### 1. DocumentType Table (NEW)
```python
- id: Integer (PK)
- code: String(50) (unique)
- label_en: String(100)
- label_de: String(100)
- description: Text (optional)
- created_at: DateTime
```

#### 2. TermDocumentReference Table (NEW)
```python
- id: Integer (PK)
- glossary_entry_id: Integer (FK → glossary_entries.id)
- document_id: Integer (FK → uploaded_documents.id)
- frequency: Integer
- page_numbers: JSON (array)
- context_excerpts: JSON (array)
- extraction_confidence: JSON (object)
- created_at: DateTime
- UNIQUE(glossary_entry_id, document_id)
```

#### 3. UploadedDocument Table (MODIFIED)
**Added Fields:**
- `document_number`: String(100), nullable, unique
- `document_type_id`: Integer (FK → document_types.id)
- `document_link`: String(1000), nullable

**Added Relationships:**
- `document_type`: relationship to DocumentType
- `term_references`: relationship to TermDocumentReference

#### 4. GlossaryEntry Table (MODIFIED)
**Changed Field:**
- `definition`: Text → `definitions`: JSON (array of definition objects)

**Added Relationships:**
- `document_references`: backref from TermDocumentReference

---

## Code Changes

### ✅ COMPLETED

#### 1. models.py
- Added DocumentType model with bilingual support
- Added TermDocumentReference junction table model
- Modified UploadedDocument model (3 new fields)
- Modified GlossaryEntry (definition → definitions)
- Added seed_document_types() function with 8 default types
- Added ForeignKey and relationship imports

#### 2. schemas.py
- Added DefinitionObject schema
- Modified GlossaryEntryBase (definitions array)
- Modified GlossaryEntryUpdate (definitions array)
- Added DocumentType schemas (Base, Create, Update, Response)
- Added TermDocumentReferenceResponse schema
- Updated DocumentUploadResponse (3 new fields)
- Updated DocumentListResponse (3 new fields)

#### 3. reset_database.py (NEW)
- Created database reset script
- Drops all tables
- Recreates with new schema
- Seeds default document types
- ASCII-safe output (no emoji encoding issues)

#### 4. Database Reset
Successfully executed:
```bash
[OK] All tables dropped
[OK] All tables created
[OK] Seeded 8 document types
[OK] Database reset complete!
```

---

## Remaining Tasks

### 🚧 IN PROGRESS

#### 1. Update Document Processing Logic
**File:** `src/backend/routers/documents.py`
**Location:** Lines 184-210 (current duplicate detection logic)

**Changes Needed:**
- Create TermDocumentReference for BOTH new AND existing terms
- Store multiple definitions in definitions array
- Track frequency, page numbers, context excerpts per document
- Set extraction_confidence metadata

#### 2. Create Admin API Endpoints
**File:** New or `src/backend/routers/admin.py`

**Endpoints Needed:**
- `GET /api/admin/document-types` - List all types
- `GET /api/admin/document-types/:id` - Get single type
- `POST /api/admin/document-types` - Create new type
- `PUT /api/admin/document-types/:id` - Update type
- `DELETE /api/admin/document-types/:id` - Delete type

#### 3. Build Document Detail Page
**File:** New `src/frontend/src/pages/DocumentDetail.tsx`

**Features Needed:**
- Route: `/documents/:id`
- Display all document attributes (number, type, link, size, etc.)
- Embedded PDF viewer (PDF.js with iframe fallback)
- List of extracted terms from this document
- Clickable links (internal and external)

#### 4. Update Glossary Display
**File:** `src/frontend/src/components/GlossaryList.tsx`

**Features Needed:**
- Display all documents containing each term
- Show frequency and page numbers per document
- Clickable internal links (to document detail page)
- Clickable external links (document_link field, open in new tab)
- Display all definition variants

---

## Testing Plan

### Phase 1: Backend Testing
1. Test document type CRUD via admin endpoints
2. Upload test PDF and verify TermDocumentReference creation
3. Test term appearing in multiple documents
4. Verify definitions array structure
5. Test document number uniqueness

### Phase 2: Frontend Testing
1. Test document detail page with PDF embedding
2. Test clickable links (internal and external)
3. Test glossary display with multiple document sources
4. Test admin tab for document type management

### Phase 3: Integration Testing
1. Upload same term in 2+ documents
2. Verify all documents shown in glossary view
3. Verify clickable links work correctly
4. Test PDF viewer fallback mechanism

---

## Files Modified

**Backend:**
- `src/backend/models.py` - Database models
- `src/backend/schemas.py` - Pydantic schemas
- `src/backend/reset_database.py` - NEW file

**Frontend:**
- (Pending) `src/frontend/src/pages/DocumentDetail.tsx` - NEW
- (Pending) `src/frontend/src/components/GlossaryList.tsx` - TO MODIFY
- (Pending) Admin tab component - TBD

**Documentation:**
- `docs/FUTURE_IMPROVEMENTS.md` - NEW file
- `docs/PHASE_3.8_PROGRESS.md` - This file

---

## Database Reset Command

To reset database with new schema:
```bash
powershell -Command "& '.\venv\Scripts\python.exe' 'src\backend\reset_database.py'"
```

---

## Next Steps

1. Update document processing logic (documents.py lines 184-210)
2. Create DocumentType admin API endpoints
3. Build DocumentDetail page component with PDF.js
4. Update GlossaryList to show all document sources
5. Test complete workflow end-to-end

---

**Last Review:** 2025-10-17
**Progress:** ~75% complete (Database layer ✓, Backend API ✓, Frontend pending)
