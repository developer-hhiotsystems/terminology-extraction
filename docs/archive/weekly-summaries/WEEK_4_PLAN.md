# Week 4 Plan: Code Quality & Standards
## Completing Month 1 Foundation

**Date:** 2025-10-19
**Phase:** Month 1 - Week 4 (Final)
**Estimated Time:** 7 hours
**Goal:** Complete Month 1 foundation by addressing code quality, deprecations, and security

---

## 📋 Week 4 Overview

Week 4 completes the Month 1 foundation by addressing technical debt, improving code maintainability, and ensuring production readiness before tackling Month 2's architectural changes.

**Why Week 4 Before Month 2?**
- Eliminate magic strings that make refactoring harder
- Fix deprecated FastAPI APIs before PostgreSQL migration
- Secure file uploads before production deployment
- Clean codebase makes Month 2 architecture work safer

---

## 🎯 Week 4 Objectives

### 1. **Create Constants Module** (2 hours)
**Problem:** Magic strings scattered throughout codebase make refactoring error-prone

**Current Issues:**
```python
# In multiple files:
language="en"  # Repeated everywhere
language="de"  # Repeated everywhere
source="internal"  # Magic string
source="pdf"  # Magic string
```

**Solution: `src/backend/constants.py`**
```python
# Language constants
LANG_ENGLISH = "en"
LANG_GERMAN = "de"
SUPPORTED_LANGUAGES = [LANG_ENGLISH, LANG_GERMAN]

# Source constants
SOURCE_INTERNAL = "internal"
SOURCE_PDF = "pdf"
SOURCE_MANUAL = "manual"

# Validation constants
MIN_TERM_LENGTH = 2
MAX_TERM_LENGTH = 200
MIN_DEFINITION_LENGTH = 10

# File upload constants
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = [".pdf"]
UPLOAD_DIR = "data/uploads"

# Pagination constants
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 1000

# Neo4j constants
NEO4J_TIMEOUT = 30
NEO4J_MAX_RETRY = 3
```

**Files to Update:**
- `src/backend/services/term_validator.py` - Use constants for validation
- `src/backend/services/pdf_extractor.py` - Use file constants
- `src/backend/services/term_extractor.py` - Use language constants
- `src/backend/routers/glossary.py` - Use pagination constants
- `src/backend/routers/documents.py` - Use upload constants
- `src/backend/schemas.py` - Use constants in Pydantic validators
- `tests/unit/*.py` - Use constants in all tests

**Impact:**
- ✅ Eliminates ~50 magic strings
- ✅ Single source of truth for configuration
- ✅ Easier refactoring (change once, apply everywhere)
- ✅ Better IDE autocomplete and type safety

---

### 2. **Fix Deprecated FastAPI APIs** (2 hours)
**Problem:** Using deprecated `@app.on_event()` that will be removed in FastAPI 1.0

**Current Code (app.py:45-60):**
```python
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Glossary Application...")
    # Startup logic

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Glossary Application...")
    # Cleanup logic
```

**Deprecated Warning:**
```
DeprecationWarning: on_event is deprecated, use lifespan event handlers instead
```

**Solution: Use `lifespan` Context Manager**
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Starting Glossary Application...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Database: {settings.database_url}")

    # Initialize services
    if settings.neo4j_enabled:
        neo4j_service = Neo4jService()
        await neo4j_service.connect()

    yield  # Application runs here

    # Shutdown logic
    logger.info("Shutting down Glossary Application...")
    if settings.neo4j_enabled:
        await neo4j_service.close()

app = FastAPI(
    title="Glossary API",
    version="1.0.0",
    lifespan=lifespan  # Use lifespan parameter
)
```

**Benefits:**
- ✅ Future-proof for FastAPI 1.0
- ✅ Better resource management with context managers
- ✅ Clearer startup/shutdown lifecycle
- ✅ Eliminates deprecation warnings

---

### 3. **Secure File Upload Validation** (2 hours)
**Problem:** File upload validation needs hardening for production

**Current Issues:**
```python
# src/backend/routers/documents.py:50
# Only checks file extension, not content type
# No size validation
# No virus scanning preparation
# No rate limiting
```

**Security Enhancements:**

#### a) **Content Type Validation**
```python
from fastapi import UploadFile, HTTPException
import magic  # python-magic library

async def validate_pdf_file(file: UploadFile) -> None:
    """Comprehensive PDF file validation"""

    # 1. Check file extension
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files allowed")

    # 2. Check MIME type
    if file.content_type != 'application/pdf':
        raise HTTPException(400, "Invalid content type")

    # 3. Check file size
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)  # Reset

    if size > MAX_UPLOAD_SIZE:
        raise HTTPException(413, f"File too large (max {MAX_UPLOAD_SIZE/1024/1024}MB)")

    # 4. Verify PDF magic bytes
    header = await file.read(4)
    await file.seek(0)

    if header != b'%PDF':
        raise HTTPException(400, "Invalid PDF file (corrupted or not a PDF)")
```

#### b) **Rate Limiting**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/upload", status_code=201)
@limiter.limit("5/minute")  # Max 5 uploads per minute per IP
async def upload_document(file: UploadFile):
    await validate_pdf_file(file)
    # Process upload
```

#### c) **Secure File Storage**
```python
import uuid
from pathlib import Path

def get_secure_upload_path(filename: str) -> Path:
    """Generate secure upload path with UUID"""
    # Prevent directory traversal attacks
    safe_filename = Path(filename).name
    unique_name = f"{uuid.uuid4()}_{safe_filename}"
    return Path(UPLOAD_DIR) / unique_name
```

**Dependencies to Add:**
```bash
pip install python-magic slowapi
```

**Tests to Create:**
- `test_upload_validation.py` (15 tests)
  - Test file size limits
  - Test content type validation
  - Test PDF magic bytes verification
  - Test malicious filename handling
  - Test rate limiting

**Impact:**
- ✅ Prevents malicious file uploads
- ✅ Protects against DoS via large files
- ✅ Rate limiting prevents abuse
- ✅ Production-ready security

---

### 4. **Update Documentation** (1 hour)
**Goal:** Ensure all documentation reflects current state

**Documentation Updates:**

#### a) **Update Main README.md**
```markdown
# Glossary Application

A bilingual (English/German) technical glossary management system with AI-powered term extraction.

## Features
- ✅ PDF document processing with OCR normalization
- ✅ Bilingual term extraction (English/German)
- ✅ Prevention-first data quality (1,300+ bad terms prevented)
- ✅ 91 comprehensive tests (100% pass rate, 60% coverage)
- ✅ Automated CI/CD pipeline (GitHub Actions)
- ✅ React TypeScript frontend
- ✅ FastAPI backend with SQLite

## Quick Start
\`\`\`bash
# Backend
cd src/backend
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm de_core_news_sm
python app.py

# Frontend
cd src/frontend
npm install
npm run dev
\`\`\`

## Testing
\`\`\`bash
pytest tests/ -v
\`\`\`

## Quality Metrics
- **Test Coverage:** 60% (91 tests)
- **Database Quality:** 100% clean (3,210 terms)
- **Prevention Rate:** 1,300+ bad terms prevented per extraction
- **CI/CD:** Automated on every commit
```

#### b) **Create API_DOCUMENTATION.md**
```markdown
# API Documentation

## Endpoints

### Glossary
- `GET /api/glossary` - List all entries (paginated)
- `POST /api/glossary` - Create new entry
- `PUT /api/glossary/{id}` - Update entry
- `DELETE /api/glossary/{id}` - Delete entry
- `GET /api/glossary/search` - Search entries

### Documents
- `POST /api/documents/upload` - Upload PDF
- `GET /api/documents` - List documents
- `DELETE /api/documents/{id}` - Delete document

### Admin
- `DELETE /api/admin/reset-database` - Reset database
- `GET /api/health` - Health check

## Schemas
[Full OpenAPI schema available at /docs]
```

#### c) **Create CONTRIBUTING.md**
```markdown
# Contributing Guide

## Development Workflow
1. Create feature branch from `master`
2. Write tests first (TDD approach)
3. Implement feature
4. Ensure all tests pass (91/91)
5. Create pull request

## Code Quality Standards
- ✅ 100% test pass rate
- ✅ Use constants (no magic strings)
- ✅ Type hints on all functions
- ✅ Logging (not print statements)
- ✅ Follow prevention-first approach

## Testing Requirements
- Unit tests for all new services
- Integration tests for API endpoints
- Coverage must not decrease
```

**Files to Create/Update:**
- `README.md` (update)
- `docs/API_DOCUMENTATION.md` (new)
- `CONTRIBUTING.md` (new)
- `docs/ARCHITECTURE.md` (new)

---

## 📊 Week 4 Success Criteria

| Objective | Deliverable | Success Metric |
|-----------|-------------|----------------|
| **Constants module** | `src/backend/constants.py` | 50+ magic strings eliminated |
| **FastAPI upgrade** | `app.py` with lifespan | No deprecation warnings |
| **Upload security** | Validated upload handler | 15 security tests passing |
| **Documentation** | README, API docs, CONTRIBUTING | Complete and accurate |
| **All tests passing** | 91+ tests | 100% pass rate maintained |

---

## 📁 Week 4 Deliverables

### Code Files:
```
src/backend/
├── constants.py                    [NEW] Central constants module
├── app.py                          [MODIFIED] Lifespan event handlers
├── routers/
│   └── documents.py                [MODIFIED] Secure upload validation
├── services/
│   ├── term_validator.py           [MODIFIED] Use constants
│   ├── pdf_extractor.py            [MODIFIED] Use constants
│   └── term_extractor.py           [MODIFIED] Use constants
└── schemas.py                      [MODIFIED] Use constants

tests/unit/
└── test_upload_validation.py       [NEW] 15 security tests

docs/
├── API_DOCUMENTATION.md            [NEW] API reference
├── ARCHITECTURE.md                 [NEW] System architecture
└── WEEK_4_COMPLETION_SUMMARY.md    [NEW] Week 4 summary

README.md                           [MODIFIED] Updated quick start
CONTRIBUTING.md                     [NEW] Contribution guide
```

---

## ⏱️ Time Breakdown

| Task | Estimated Time | Details |
|------|----------------|---------|
| **Create constants module** | 2 hours | Create file, update 10+ files, update tests |
| **Fix deprecated APIs** | 2 hours | Implement lifespan, test startup/shutdown |
| **Secure file uploads** | 2 hours | Validation, rate limiting, 15 tests |
| **Update documentation** | 1 hour | README, API docs, CONTRIBUTING |
| **Total** | **7 hours** | Complete Month 1 foundation |

---

## 🎯 Impact of Week 4

### Code Quality:
- **Before:** 50+ magic strings, deprecated APIs, basic upload validation
- **After:** Constants module, modern FastAPI, production-ready security

### Maintainability:
- **Before:** Hard to refactor (magic strings everywhere)
- **After:** Single source of truth, easy to modify

### Security:
- **Before:** Basic file extension check only
- **After:** Multi-layer validation, rate limiting, secure storage

### Production Readiness:
- **Before:** Development-grade code
- **After:** Production-ready with proper standards

---

## 🚀 After Week 4: Ready for Month 2

With Week 4 complete, the codebase will have:
- ✅ Clean code (no magic strings, modern APIs)
- ✅ Production security (validated uploads, rate limiting)
- ✅ Comprehensive tests (100+ tests expected)
- ✅ Complete documentation (API, architecture, contributing)
- ✅ Solid foundation for Month 2 architecture changes

**Month 2 Preview (Weeks 5-8):**
- **Weeks 5-6:** PostgreSQL migration with full-text search (40h)
- **Week 7:** Relationship extraction with spaCy (20h)
- **Week 8:** UI/UX improvements for graph visualization (20h)

---

## ✅ Week 4 Checklist

- [ ] Create `src/backend/constants.py` with all constants
- [ ] Update all files to use constants (services, routers, schemas, tests)
- [ ] Replace `@app.on_event()` with `lifespan` context manager
- [ ] Implement secure file upload validation
- [ ] Add `python-magic` and `slowapi` dependencies
- [ ] Create `tests/unit/test_upload_validation.py` (15 tests)
- [ ] Update `README.md` with current features and quick start
- [ ] Create `docs/API_DOCUMENTATION.md`
- [ ] Create `CONTRIBUTING.md`
- [ ] Create `docs/ARCHITECTURE.md`
- [ ] Run full test suite (expect 106 tests passing)
- [ ] Create `docs/WEEK_4_COMPLETION_SUMMARY.md`
- [ ] Commit Week 4 changes to git

---

## 📞 Decision Time

**You have completed Week 1-3 of Month 1. Ready to proceed with Week 4?**

Week 4 is recommended because:
- ✅ Completes Month 1 foundation (only 7 hours)
- ✅ Makes Month 2 architecture work safer
- ✅ Achieves production-ready code quality
- ✅ Natural progression in roadmap

**Alternative Options:**
- **Skip to Month 2** - PostgreSQL migration (40h) - More ambitious
- **Expand testing** - Router integration tests (8h) - Optional enhancement
- **Deploy MVP** - Production deployment (20-30h) - Requires Month 2 first

**Recommendation:** Complete Week 4 to finish Month 1 strong, then tackle Month 2's architecture improvements with a clean, well-tested foundation.

---

**Ready to begin Week 4?**
