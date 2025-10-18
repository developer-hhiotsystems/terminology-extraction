# Phase 3.8: Multi-Document Term Tracking - Test Plan

## Test Execution Date
Generated: 2025-10-18

## Overview
Comprehensive test plan for Phase 3.8 features:
- Multi-document term tracking with multiple definitions
- Document detail page with PDF viewer
- DocumentType management UI
- Bilingual support (EN/DE)

## Test Environment
- **Backend**: http://localhost:9123
- **Frontend**: http://localhost:3001
- **Database**: SQLite (./data/glossary.db)
- **Status**: Both servers running and healthy

## Feature 1: DocumentType Management (Admin Tab)

### Test 1.1: List Document Types
**Endpoint**: `GET /api/admin/document-types`
**Expected**: Return list of pre-seeded document types with bilingual labels

**Pre-seeded Types**:
1. Manual (Handbuch)
2. Specification (Spezifikation)
3. Standard (Norm)
4. Procedure (Verfahrensanweisung)
5. Guideline (Richtlinie)
6. Report (Bericht)
7. Drawing (Zeichnung)
8. Other (Sonstiges)

**Status**: ✅ PASSED - 8 document types returned

### Test 1.2: Create New Document Type
**Endpoint**: `POST /api/admin/document-types`
**Payload**:
```json
{
  "code": "test_doc",
  "label_en": "Test Document",
  "label_de": "Testdokument",
  "description": "Created for testing Phase 3.8"
}
```
**Expected**:
- Status 200
- Return created document type with ID
- Include creation timestamp

**Status**: PENDING

### Test 1.3: Update Document Type
**Endpoint**: `PUT /api/admin/document-types/{id}`
**Payload**:
```json
{
  "label_en": "Updated Test Document",
  "label_de": "Aktualisiertes Testdokument",
  "description": "Updated description"
}
```
**Expected**:
- Status 200
- Code field should remain unchanged (immutable)
- Labels and description updated

**Status**: PENDING

### Test 1.4: Delete Document Type
**Endpoint**: `DELETE /api/admin/document-types/{id}`
**Expected**:
- Status 200 for unused types
- Status 400 if documents reference this type

**Status**: PENDING

### Test 1.5: UI Navigation
**Steps**:
1. Navigate to http://localhost:3001/admin
2. Verify "Document Types Management" section exists
3. Verify table displays all document types
4. Click "Add Document Type" button
5. Fill form and submit
6. Verify new type appears in table

**Status**: PENDING

## Feature 2: Multi-Document Term Tracking

### Test 2.1: Create Glossary Entry with Single Definition
**Endpoint**: `POST /api/glossary`
**Payload**:
```json
{
  "term": "Reactor",
  "language": "en",
  "source": "internal",
  "definitions": [
    {
      "text": "A vessel designed to contain chemical reactions",
      "is_primary": true
    }
  ],
  "domain_tags": ["chemical", "process"]
}
```
**Expected**:
- Status 200
- Definitions stored as JSON array
- Primary definition marked

**Status**: PENDING

### Test 2.2: Add Second Definition from Different Document
**Scenario**: Same term appears in second document with different definition
**Endpoint**: `PUT /api/glossary/{id}`
**Payload**:
```json
{
  "definitions": [
    {
      "text": "A vessel designed to contain chemical reactions",
      "source_doc_id": 1,
      "is_primary": true
    },
    {
      "text": "Equipment for controlled nuclear fission",
      "source_doc_id": 2,
      "is_primary": false
    }
  ]
}
```
**Expected**:
- Both definitions displayed in glossary list
- Primary badge shown on first definition
- Source document ID visible

**Status**: PENDING

### Test 2.3: Glossary List Display
**URL**: http://localhost:3001/
**Verify**:
- Multiple definitions displayed in separate boxes
- Primary definition has blue badge and gradient background
- Secondary definitions have gray border
- Source document ID shown for each definition

**Status**: PENDING

## Feature 3: Document Detail Page

### Test 3.1: Upload PDF Document
**Endpoint**: `POST /api/documents/upload`
**File**: Test PDF from test-data/ folder
**Expected**:
- Status 200
- Return document metadata
- File stored in ./data/uploads/

**Status**: PENDING

### Test 3.2: Process Document for Term Extraction
**Endpoint**: `POST /api/documents/{id}/process`
**Payload**:
```json
{
  "auto_extract_terms": true,
  "language": "en"
}
```
**Expected**:
- Status 200
- Terms extracted and saved to glossary
- TermDocumentReference junction records created

**Status**: PENDING

### Test 3.3: View Document Detail Page
**URL**: http://localhost:3001/documents/{id}
**Verify**:
- Document metadata displayed (filename, size, status, type, dates)
- PDF viewer iframe loads successfully
- Fallback option available
- Related terms section shows extracted glossary entries
- Each term links back to glossary
- Delete button works

**Status**: PENDING

### Test 3.4: PDF Viewer Functionality
**Verify**:
- PDF loads in iframe
- PDF is scrollable and zoomable
- "Open in new tab" button works
- Viewer toggle between iframe/fallback works

**Status**: PENDING

### Test 3.5: Navigation from Document List
**Steps**:
1. Navigate to http://localhost:3001/documents
2. Verify document filenames are clickable links
3. Click a document link
4. Verify navigation to /documents/{id}
5. Verify document detail page loads

**Status**: PENDING

## Feature 4: Term-Document Relationships

### Test 4.1: TermDocumentReference Junction Table
**SQL Query**:
```sql
SELECT * FROM term_document_reference WHERE term_id = ?
```
**Expected**:
- Multiple rows for terms in multiple documents
- Correct document_id and term_id associations

**Status**: PENDING

### Test 4.2: Glossary Entry Shows All Source Documents
**Scenario**: Term "Valve" appears in 3 documents
**Expected**:
- Glossary entry shows 3 definitions
- Each definition tagged with source_doc_id
- Primary definition marked
- Clicking source link navigates to document detail

**Status**: PENDING

## Feature 5: Form Handling and Data Validation

### Test 5.1: GlossaryEntryForm - Create Mode
**URL**: http://localhost:3001/ (click "Add Entry")
**Verify**:
- Form accepts single definition text
- On submit, wraps in array format with is_primary: true
- Success toast notification appears

**Status**: PENDING

### Test 5.2: GlossaryEntryForm - Edit Mode
**Verify**:
- Extracts primary definition for editing
- Displays in textarea
- On submit, updates definitions array
- Preserves non-primary definitions

**Status**: PENDING

### Test 5.3: DocumentType Form Validation
**Verify**:
- All required fields (code, label_en, label_de) validated
- Code field disabled in edit mode
- Form prevents duplicate codes
- Success/error toasts appear

**Status**: PENDING

## Feature 6: CSS Styling and UI/UX

### Test 6.1: Multi-Definition Display Styling
**Verify**:
- `.entry-definitions` container has proper spacing
- `.definition-item.primary` has blue left border and gradient
- `.primary-badge` displays correctly
- `.definition-source` text is italic and gray

**Status**: PENDING

### Test 6.2: Document Detail Page Layout
**Verify**:
- Responsive grid layout
- Cards have proper shadows and borders
- PDF viewer height is 800px
- Metadata grid adapts to screen size

**Status**: PENDING

### Test 6.3: Admin Panel Layout
**Verify**:
- Document types table is scrollable
- Modal overlays properly
- Form inputs have proper spacing
- Action buttons aligned correctly

**Status**: PENDING

## Feature 7: API Response Validation

### Test 7.1: Definition Schema Validation
**Verify API Returns**:
```typescript
interface DefinitionObject {
  text: string;
  source_doc_id?: number;
  is_primary: boolean;
}
```
**Status**: PENDING

### Test 7.2: DocumentType Schema Validation
**Verify API Returns**:
```typescript
interface DocumentType {
  id: number;
  code: string;
  label_en: string;
  label_de: string;
  description?: string;
  created_at: string;
}
```
**Status**: ✅ PASSED

## Integration Tests

### Integration Test 1: End-to-End Multi-Document Workflow
**Steps**:
1. Upload Document A with term "Valve"
2. Process Document A (extract "Valve" with definition 1)
3. Upload Document B with term "Valve"
4. Process Document B (extract "Valve" with definition 2)
5. Verify glossary entry for "Valve" has 2 definitions
6. Navigate to Document A detail page
7. Verify "Valve" appears in related terms
8. Click "Valve" link to navigate to glossary
9. Verify both definitions displayed

**Status**: PENDING

### Integration Test 2: DocumentType CRUD Full Cycle
**Steps**:
1. Create new document type via UI
2. Upload document and assign new type
3. Update document type labels
4. Verify document shows updated type
5. Attempt to delete type (should fail)
6. Delete document
7. Delete document type (should succeed)

**Status**: PENDING

## Performance Tests

### Performance Test 1: Large Definition Arrays
**Scenario**: Glossary entry with 10+ definitions
**Verify**:
- UI renders without lag
- All definitions visible
- Scrolling smooth

**Status**: PENDING

### Performance Test 2: PDF Viewer Load Time
**Scenario**: Load 5MB+ PDF file
**Verify**:
- Loads within 3 seconds
- No console errors
- Browser memory stable

**Status**: PENDING

## Browser Compatibility

### Browsers to Test
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if available)

**Features to Verify**:
- PDF iframe embedding
- Modal dialogs
- CSS grid/flexbox layouts
- Toast notifications
- React Router navigation

## Regression Tests

### Regression Test 1: Existing Glossary Features
**Verify**:
- Search functionality still works
- Pagination still works
- Filters still work
- Export functionality still works
- Bulk operations still work

**Status**: PENDING

### Regression Test 2: Existing Document Features
**Verify**:
- Document upload still works
- Document list still works
- Document deletion still works

**Status**: PENDING

## Test Data Requirements

### Required Test Files
1. **test-doc-a.pdf** - Contains terms: Reactor, Valve, Pressure
2. **test-doc-b.pdf** - Contains terms: Reactor, Valve, Temperature
3. **test-doc-c.pdf** - Contains terms: Valve, Flow, Control

### Expected Outcomes
- Reactor: 2 definitions (from A and B)
- Valve: 3 definitions (from A, B, and C)
- Pressure: 1 definition (from A)
- Temperature: 1 definition (from B)
- Flow: 1 definition (from C)
- Control: 1 definition (from C)

## Success Criteria

✅ **Phase 3.8 is considered COMPLETE when**:
1. All API endpoints return expected responses
2. All UI components render correctly
3. Multi-document term tracking works as specified
4. PDF viewer displays documents
5. DocumentType CRUD operations work
6. No console errors or warnings
7. All integration tests pass
8. Documentation is updated

## Test Execution Log

### Session 1: 2025-10-18
- [x] Backend health check - PASSED
- [x] DocumentType API list - PASSED (8 types)
- [ ] DocumentType CRUD operations
- [ ] Document upload and processing
- [ ] Multi-definition display
- [ ] PDF viewer functionality
- [ ] End-to-end integration tests

## Notes
- Database is currently empty (clean state for testing)
- All pre-seeded DocumentTypes are present
- Frontend running on port 3001 (port 3000 was in use)
- Backend running on port 9123
- All previous HMR updates successful
