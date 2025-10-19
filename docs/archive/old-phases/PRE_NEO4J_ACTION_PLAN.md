# Pre-Neo4j Action Plan
**Priority-Ordered Task List**

## Critical Blockers (Fix Immediately) 🔴

### 1. Fix Failing Unit Tests (4 hours)
**Status:** 7/53 tests failing
**Impact:** Blocks all development

**Files to Fix:**
```
tests/unit/test_api_glossary.py
tests/unit/test_models.py
```

**Root Cause:** Tests use old schema with single `definition` field instead of new `definitions` JSON array.

**Example Fix:**
```python
# OLD
entry = GlossaryEntry(
    term="Test Term",
    definition="Single definition string",
    language="en"
)

# NEW
entry = GlossaryEntry(
    term="Test Term",
    definitions=[{
        "text": "Definition text",
        "is_primary": True,
        "source_doc_id": None
    }],
    language="en"
)
```

---

### 2. Fix TypeScript Compilation Errors (3 hours)
**Status:** 8 errors, build failing
**Impact:** Frontend cannot deploy

**Errors to Fix:**

1. **Duplicate function implementations** (2 errors)
   - File: `src/api/client.ts` lines 156, 172
   - Remove duplicate function declarations

2. **Type mismatches** (6 errors)
   - `Documents.tsx:290` - Add `processing_time` to `DocumentProcessResponse` type
   - `DocumentUpload.tsx:69` - Rename `file` to `files`
   - `TermRelationships.tsx` - Use public methods instead of private `client` property

---

### 3. Remove Security Vulnerabilities (1 hour)
**Status:** Hard-coded credentials in production code
**Impact:** Security risk

**Changes:**
```python
# config.py - BEFORE
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "devpassword")  # BAD
DEBUG = os.getenv("DEBUG", "True").lower() == "true"  # BAD

# config.py - AFTER
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")  # Fail if not set
if NEO4J_PASSWORD is None:
    raise ValueError("NEO4J_PASSWORD environment variable required")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"  # Default False
```

---

### 4. Replace Print Statements with Logging (2 hours)
**Status:** 34 print() calls across codebase
**Impact:** Cannot control log levels in production

**Steps:**
1. Create `src/backend/logging_config.py`
2. Replace all print() statements
3. Configure log rotation

**Example:**
```python
# BEFORE
print(f"Database initialized: {config.DATABASE_URL}")

# AFTER
import logging
logger = logging.getLogger(__name__)
logger.info(f"Database initialized: {config.DATABASE_URL}")
```

---

## High Priority (Fix This Week) 🟡

### 5. Update Deprecated APIs (2 hours)
**Status:** 8 deprecation warnings
**Impact:** Will break in future library versions

**Changes:**

**Pydantic (2 instances):**
```python
# schemas.py - BEFORE
definitions: List[DefinitionObject] = Field(..., min_items=1)

# schemas.py - AFTER
definitions: List[DefinitionObject] = Field(..., min_length=1)
```

**FastAPI (2 instances):**
```python
# app.py - BEFORE
@app.on_event("startup")
async def startup_event():
    initialize_database()

# app.py - AFTER
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield

app = FastAPI(lifespan=lifespan)
```

**Query Parameters (2 instances):**
```python
# glossary.py - BEFORE
format: str = Query(..., regex="^(csv|excel|json)$")

# glossary.py - AFTER
format: str = Query(..., pattern="^(csv|excel|json)$")
```

---

### 6. Add Router Integration Tests (8 hours)
**Status:** Router coverage 16-29%
**Impact:** High risk of API bugs

**New Test Files:**
```
tests/integration/test_glossary_router.py
tests/integration/test_documents_router.py
tests/integration/test_admin_router.py
tests/integration/test_export_workflow.py
```

**Test Scenarios:**
- Create → Read → Update → Delete workflows
- File upload → Processing → Term extraction
- Export to CSV, Excel, JSON
- Error handling and validation

---

### 7. Create Constants Module (1 hour)
**Status:** Magic strings throughout code
**Impact:** Maintainability, typo errors

**New File:**
```python
# src/backend/constants.py
from enum import Enum

class ValidationStatus(str, Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"

class Source(str, Enum):
    INTERNAL = "internal"
    NAMUR = "NAMUR"
    DIN = "DIN"
    ASME = "ASME"
    IEC = "IEC"
    IATE = "IATE"

class SyncStatus(str, Enum):
    PENDING_SYNC = "pending_sync"
    SYNCED = "synced"
    SYNC_FAILED = "sync_failed"
```

**Update:**
- models.py - Use enums in constraints
- routers - Use enums in queries
- schemas.py - Use enums in validation

---

## Medium Priority (Before Neo4j) 🟢

### 8. Add PDF Extraction Tests (4 hours)
**Status:** pdf_extractor.py only 15% coverage
**Impact:** PDF upload bugs

**New Test File:**
```python
# tests/unit/test_pdf_extractor.py

def test_extract_text_from_valid_pdf():
    """Test successful text extraction"""

def test_extract_text_handles_corrupted_pdf():
    """Test error handling for invalid PDFs"""

def test_extract_text_by_page():
    """Test page-by-page extraction"""

def test_validate_pdf_size_limit():
    """Test file size validation"""
```

---

### 9. Extract Export Logic to Service (4 hours)
**Status:** Business logic mixed in router
**Impact:** Code organization, testability

**New File:**
```python
# src/backend/services/export_service.py

class ExportService:
    @staticmethod
    def export_to_csv(entries: List[GlossaryEntry]) -> str:
        """Export entries to CSV format"""
        ...

    @staticmethod
    def export_to_excel(entries: List[GlossaryEntry]) -> BytesIO:
        """Export entries to Excel format"""
        ...

    @staticmethod
    def export_to_json(entries: List[GlossaryEntry]) -> str:
        """Export entries to JSON format"""
        ...
```

---

### 10. Add File Upload Validation (3 hours)
**Status:** No file type or size validation
**Impact:** Security risk, storage issues

**Changes to documents.py:**
```python
ALLOWED_EXTENSIONS = {'.pdf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def validate_upload_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Invalid file type: {ext}")

    # Check size
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")

    # Sanitize filename
    safe_name = secure_filename(file.filename)
    return safe_name
```

---

## Effort Summary

| Priority | Tasks | Estimated Hours |
|----------|-------|-----------------|
| Critical 🔴 | 4 tasks | 10 hours |
| High 🟡 | 4 tasks | 13 hours |
| Medium 🟢 | 3 tasks | 11 hours |
| **TOTAL** | **11 tasks** | **34 hours** |

---

## Success Criteria

### Before Neo4j Integration:
- [ ] All tests passing (53/53)
- [ ] Test coverage ≥ 60%
- [ ] No TypeScript compilation errors
- [ ] No security vulnerabilities
- [ ] No print() statements
- [ ] No deprecated API usage
- [ ] Frontend builds successfully

### Quality Gates:
- [ ] No hard-coded credentials
- [ ] All magic strings replaced with constants
- [ ] Structured logging configured
- [ ] File upload validation implemented
- [ ] Integration tests for core workflows

---

## Recommended Approach

### Week 1: Critical Fixes
**Days 1-2 (10 hours):**
- Fix failing tests (4h)
- Fix TypeScript errors (3h)
- Remove security issues (1h)
- Replace print statements (2h)

**Deliverable:** Clean test suite, secure code, proper logging

---

### Week 2: High Priority
**Days 3-4 (13 hours):**
- Update deprecated APIs (2h)
- Add router integration tests (8h)
- Create constants module (1h)
- Update code to use constants (2h)

**Deliverable:** Future-proof APIs, better test coverage

---

### Week 3: Medium Priority (Optional)
**Days 5-6 (11 hours):**
- Add PDF extraction tests (4h)
- Extract export service (4h)
- Add file upload validation (3h)

**Deliverable:** Production-ready, well-tested codebase

---

## After Completion

You will have:
- ✓ All tests passing
- ✓ Secure configuration
- ✓ Proper logging
- ✓ Clean, maintainable code
- ✓ 60%+ test coverage
- ✓ Working frontend build
- ✓ Ready for Neo4j integration

**Total Timeline:** 2-3 weeks (part-time) or 1 week (full-time)
**Confidence Level:** HIGH - Clear tasks, known solutions, manageable scope
