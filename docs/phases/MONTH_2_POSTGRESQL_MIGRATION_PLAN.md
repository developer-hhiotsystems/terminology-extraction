# Month 2: PostgreSQL Migration Plan
## Weeks 5-6 - Architecture Upgrade

**Date:** 2025-10-19
**Phase:** Month 2 - Weeks 5-6
**Estimated Time:** 40 hours
**Goal:** Migrate from SQLite to PostgreSQL with full-text search and normalized schema

---

## 📋 Migration Overview

### Why PostgreSQL?

**Current Limitations (SQLite):**
- ❌ Limited full-text search (basic LIKE queries only)
- ❌ No advanced indexing (GIN, GiST for JSON/text)
- ❌ Single-writer concurrency bottleneck
- ❌ Limited JSON query capabilities
- ❌ No tsvector/tsquery for multi-language search
- ❌ Poor performance with 10,000+ entries

**PostgreSQL Benefits:**
- ✅ Full-text search with tsvector/tsquery (English + German)
- ✅ Advanced indexing (GIN for JSON, GiST for full-text)
- ✅ Multi-version concurrency control (MVCC)
- ✅ Rich JSON operators (->>, @>, etc.)
- ✅ Normalized schema with foreign keys
- ✅ Production-ready for 100,000+ entries
- ✅ Better query optimization
- ✅ Point-in-time recovery and replication

---

## 🎯 Migration Goals

### Week 5: Schema & Migration (20 hours)
1. Design normalized PostgreSQL schema
2. Implement SQLAlchemy models for PostgreSQL
3. Create migration scripts (SQLite → PostgreSQL)
4. Test data integrity after migration
5. Update database configuration

### Week 6: Full-Text Search & Performance (20 hours)
1. Implement tsvector columns for English/German
2. Create GIN indexes for full-text search
3. Build advanced search API with ranking
4. Performance benchmarking (SQLite vs PostgreSQL)
5. Documentation and deployment guide

---

## 📊 Current Database Schema (SQLite)

```sql
-- Current SQLite schema
CREATE TABLE glossary_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT NOT NULL,
    definitions JSON NOT NULL,  -- Array of {text, source_doc_id, is_primary}
    language TEXT NOT NULL,     -- 'en' or 'de'
    source TEXT NOT NULL,       -- 'internal', 'NAMUR', etc.
    source_document TEXT,
    domain_tags JSON,           -- Array of strings
    validation_status TEXT DEFAULT 'pending',
    sync_status TEXT DEFAULT 'pending_sync',
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(term, language, source)
);

CREATE TABLE uploaded_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_type TEXT,
    upload_status TEXT DEFAULT 'pending',
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    processing_metadata JSON,
    document_number TEXT,
    document_type_id INTEGER,
    document_link TEXT,
    FOREIGN KEY (document_type_id) REFERENCES document_types(id)
);

CREATE TABLE term_document_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    glossary_entry_id INTEGER NOT NULL,
    document_id INTEGER NOT NULL,
    frequency INTEGER DEFAULT 1,
    page_numbers JSON,
    context_excerpts JSON,
    extraction_confidence JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (glossary_entry_id) REFERENCES glossary_entries(id),
    FOREIGN KEY (document_id) REFERENCES uploaded_documents(id)
);
```

**Problems:**
- JSON stored as text (no indexing, slow queries)
- No full-text search indexes
- No proper foreign key constraints
- Denormalized definitions array

---

## 🏗️ Proposed PostgreSQL Schema (Normalized)

```sql
-- PostgreSQL schema with normalization and full-text search

-- 1. Glossary entries table (core terms)
CREATE TABLE glossary_entries (
    id SERIAL PRIMARY KEY,
    term VARCHAR(255) NOT NULL,
    language VARCHAR(2) NOT NULL CHECK (language IN ('en', 'de')),
    source VARCHAR(50) NOT NULL,
    source_document VARCHAR(500),
    domain_tags TEXT[],  -- PostgreSQL native array
    validation_status VARCHAR(20) DEFAULT 'pending' CHECK (validation_status IN ('pending', 'validated', 'rejected')),
    sync_status VARCHAR(20) DEFAULT 'pending_sync' CHECK (sync_status IN ('pending_sync', 'synced', 'sync_failed')),

    -- Full-text search columns
    search_vector_en TSVECTOR,  -- English full-text search
    search_vector_de TSVECTOR,  -- German full-text search

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_term_lang_source UNIQUE (term, language, source)
);

-- 2. Definitions table (normalized, one-to-many)
CREATE TABLE definitions (
    id SERIAL PRIMARY KEY,
    glossary_entry_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    source_doc_id INTEGER,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (glossary_entry_id) REFERENCES glossary_entries(id) ON DELETE CASCADE,
    FOREIGN KEY (source_doc_id) REFERENCES uploaded_documents(id) ON DELETE SET NULL
);

-- 3. Uploaded documents table
CREATE TABLE uploaded_documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(100),
    upload_status VARCHAR(20) DEFAULT 'pending' CHECK (upload_status IN ('pending', 'processing', 'completed', 'failed')),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,
    processing_metadata JSONB,  -- PostgreSQL native JSON with indexing
    document_number VARCHAR(100),
    document_type_id INTEGER,
    document_link VARCHAR(1000),

    FOREIGN KEY (document_type_id) REFERENCES document_types(id) ON DELETE SET NULL
);

-- 4. Document types table
CREATE TABLE document_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    label_en VARCHAR(100) NOT NULL,
    label_de VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Term-document references table (many-to-many)
CREATE TABLE term_document_references (
    id SERIAL PRIMARY KEY,
    glossary_entry_id INTEGER NOT NULL,
    document_id INTEGER NOT NULL,
    frequency INTEGER DEFAULT 1,
    page_numbers INTEGER[],  -- PostgreSQL native array
    context_excerpts TEXT[],  -- PostgreSQL native array
    extraction_confidence JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (glossary_entry_id) REFERENCES glossary_entries(id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES uploaded_documents(id) ON DELETE CASCADE,
    CONSTRAINT unique_entry_document UNIQUE (glossary_entry_id, document_id)
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Full-text search indexes (GIN - Generalized Inverted Index)
CREATE INDEX idx_glossary_fts_en ON glossary_entries USING GIN(search_vector_en);
CREATE INDEX idx_glossary_fts_de ON glossary_entries USING GIN(search_vector_de);

-- Regular B-tree indexes
CREATE INDEX idx_glossary_term ON glossary_entries(term);
CREATE INDEX idx_glossary_language ON glossary_entries(language);
CREATE INDEX idx_glossary_source ON glossary_entries(source);
CREATE INDEX idx_glossary_validation_status ON glossary_entries(validation_status);
CREATE INDEX idx_glossary_created_at ON glossary_entries(created_at DESC);

-- Definitions indexes
CREATE INDEX idx_definitions_entry_id ON definitions(glossary_entry_id);
CREATE INDEX idx_definitions_is_primary ON definitions(is_primary) WHERE is_primary = TRUE;

-- Document indexes
CREATE INDEX idx_documents_upload_status ON uploaded_documents(upload_status);
CREATE INDEX idx_documents_uploaded_at ON uploaded_documents(uploaded_at DESC);
CREATE INDEX idx_documents_document_number ON uploaded_documents(document_number);

-- JSONB indexes for processing_metadata
CREATE INDEX idx_documents_metadata ON uploaded_documents USING GIN(processing_metadata);

-- Reference indexes
CREATE INDEX idx_references_entry_id ON term_document_references(glossary_entry_id);
CREATE INDEX idx_references_document_id ON term_document_references(document_id);

-- =============================================================================
-- TRIGGERS FOR AUTOMATIC TSVECTOR UPDATE
-- =============================================================================

-- Function to update search vectors
CREATE OR REPLACE FUNCTION update_glossary_search_vectors()
RETURNS TRIGGER AS $$
BEGIN
    -- Update English search vector (term + definitions)
    IF NEW.language = 'en' THEN
        NEW.search_vector_en := to_tsvector('english',
            COALESCE(NEW.term, '') || ' ' ||
            COALESCE((SELECT string_agg(text, ' ') FROM definitions WHERE glossary_entry_id = NEW.id), '')
        );
    END IF;

    -- Update German search vector (term + definitions)
    IF NEW.language = 'de' THEN
        NEW.search_vector_de := to_tsvector('german',
            COALESCE(NEW.term, '') || ' ' ||
            COALESCE((SELECT string_agg(text, ' ') FROM definitions WHERE glossary_entry_id = NEW.id), '')
        );
    END IF;

    -- Update timestamp
    NEW.updated_at := CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger on INSERT and UPDATE
CREATE TRIGGER trg_update_search_vectors
    BEFORE INSERT OR UPDATE ON glossary_entries
    FOR EACH ROW
    EXECUTE FUNCTION update_glossary_search_vectors();

-- Trigger to update search vectors when definitions change
CREATE OR REPLACE FUNCTION update_entry_search_on_definition_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Update the parent glossary entry's search vectors
    UPDATE glossary_entries
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = COALESCE(NEW.glossary_entry_id, OLD.glossary_entry_id);

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_definition_changes
    AFTER INSERT OR UPDATE OR DELETE ON definitions
    FOR EACH ROW
    EXECUTE FUNCTION update_entry_search_on_definition_change();
```

---

## 🔄 Migration Strategy

### Phase 1: Setup PostgreSQL (2 hours)

**1.1 Install PostgreSQL**
```bash
# Windows
# Download from https://www.postgresql.org/download/windows/
# Or use Docker:
docker run --name glossary-postgres -e POSTGRES_PASSWORD=glossary -e POSTGRES_DB=glossary -p 5432:5432 -d postgres:16

# Verify installation
psql -U postgres -c "SELECT version();"
```

**1.2 Create Database & User**
```sql
CREATE DATABASE glossary;
CREATE USER glossary_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE glossary TO glossary_user;

-- Connect to glossary database
\c glossary

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO glossary_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO glossary_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO glossary_user;
```

**1.3 Update Configuration**
```python
# src/backend/constants.py
DATABASE_URL_POSTGRESQL = "postgresql://glossary_user:password@localhost:5432/glossary"

# .env file
DATABASE_URL=postgresql://glossary_user:password@localhost:5432/glossary
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=glossary
POSTGRES_USER=glossary_user
POSTGRES_PASSWORD=secure_password_here
```

---

### Phase 2: SQLAlchemy Models (4 hours)

**2.1 Update models.py for PostgreSQL**
```python
# Changes needed:
# - Use postgresql.ARRAY instead of JSON for arrays
# - Add TSVECTOR columns
# - Normalize definitions into separate table
# - Add proper foreign key relationships
# - Use JSONB instead of JSON
```

**2.2 Create Alembic migrations**
```bash
# Install Alembic
pip install alembic psycopg2-binary

# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial PostgreSQL schema"

# Apply migration
alembic upgrade head
```

---

### Phase 3: Data Migration Script (6 hours)

**3.1 Export from SQLite**
```python
# scripts/export_sqlite_data.py
import sqlite3
import json
from pathlib import Path

def export_sqlite_data():
    """Export all data from SQLite to JSON"""
    conn = sqlite3.connect('./data/glossary.db')
    conn.row_factory = sqlite3.Row

    # Export glossary entries
    entries = conn.execute('SELECT * FROM glossary_entries').fetchall()
    with open('./data/sqlite_export_entries.json', 'w') as f:
        json.dump([dict(row) for row in entries], f, indent=2)

    # Export documents
    documents = conn.execute('SELECT * FROM uploaded_documents').fetchall()
    with open('./data/sqlite_export_documents.json', 'w') as f:
        json.dump([dict(row) for row in documents], f, indent=2)

    # Export references
    refs = conn.execute('SELECT * FROM term_document_references').fetchall()
    with open('./data/sqlite_export_references.json', 'w') as f:
        json.dump([dict(row) for row in refs], f, indent=2)

    conn.close()
```

**3.2 Import to PostgreSQL**
```python
# scripts/import_to_postgresql.py
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def import_to_postgresql():
    """Import data from JSON to PostgreSQL"""
    engine = create_engine(DATABASE_URL_POSTGRESQL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Import entries with normalized definitions
    with open('./data/sqlite_export_entries.json') as f:
        entries = json.load(f)

    for entry in entries:
        # Create glossary entry
        db_entry = GlossaryEntry(
            id=entry['id'],
            term=entry['term'],
            language=entry['language'],
            # ... other fields
        )
        session.add(db_entry)

        # Create separate definition records
        definitions = json.loads(entry['definitions'])
        for def_obj in definitions:
            db_def = Definition(
                glossary_entry_id=entry['id'],
                text=def_obj['text'],
                source_doc_id=def_obj.get('source_doc_id'),
                is_primary=def_obj.get('is_primary', False)
            )
            session.add(db_def)

    session.commit()
```

---

### Phase 4: Full-Text Search Implementation (8 hours)

**4.1 Search API with Ranking**
```python
# src/backend/routers/search.py

@router.get("/search/fulltext")
async def fulltext_search(
    query: str = Query(..., min_length=2),
    language: str = Query("en", pattern="^(en|de)$"),
    limit: int = Query(50, le=1000),
    db: Session = Depends(get_db)
):
    """
    Full-text search with ranking

    Uses PostgreSQL tsvector and tsquery for intelligent search:
    - Stemming (running → run)
    - Ranking by relevance
    - Phrase search ("exact phrase")
    - Boolean operators (term1 & term2 | term3)
    """
    # Build tsquery
    search_vector_col = (
        GlossaryEntry.search_vector_en if language == 'en'
        else GlossaryEntry.search_vector_de
    )

    # PostgreSQL full-text search with ranking
    results = db.query(
        GlossaryEntry,
        func.ts_rank(search_vector_col, func.to_tsquery(language, query)).label('rank')
    ).filter(
        search_vector_col.op('@@')(func.to_tsquery(language, query))
    ).order_by(
        desc('rank')
    ).limit(limit).all()

    return {
        "query": query,
        "language": language,
        "total": len(results),
        "results": [
            {
                "entry": entry,
                "relevance_score": rank,
                "highlight": ts_headline(entry.term, query)
            }
            for entry, rank in results
        ]
    }
```

**4.2 Advanced Search Features**
- Fuzzy search with trigram similarity
- Multi-language search
- Domain filtering
- Source filtering
- Date range filtering

---

### Phase 5: Performance Testing (6 hours)

**5.1 Benchmark Queries**
```python
# scripts/benchmark_databases.py

import time
from statistics import mean

def benchmark_sqlite():
    """Benchmark SQLite queries"""
    conn = sqlite3.connect('./data/glossary.db')

    queries = [
        "SELECT * FROM glossary_entries WHERE term LIKE '%temperature%'",
        "SELECT * FROM glossary_entries WHERE language = 'en' LIMIT 100",
        "SELECT COUNT(*) FROM glossary_entries",
    ]

    timings = []
    for query in queries:
        start = time.time()
        conn.execute(query).fetchall()
        timings.append(time.time() - start)

    return mean(timings)

def benchmark_postgresql():
    """Benchmark PostgreSQL queries with full-text search"""
    # Similar but with tsvector queries
    pass

# Compare results
sqlite_time = benchmark_sqlite()
postgres_time = benchmark_postgresql()
print(f"SQLite avg: {sqlite_time:.4f}s")
print(f"PostgreSQL avg: {postgres_time:.4f}s")
print(f"Speed improvement: {sqlite_time / postgres_time:.2f}x")
```

**Expected Performance Gains:**
- Full-text search: 10-50x faster
- JSON queries: 5-10x faster
- Large result sets: 3-5x faster
- Complex joins: 2-4x faster

---

### Phase 6: Testing & Documentation (4 hours)

**6.1 PostgreSQL-Specific Tests**
```python
# tests/integration/test_postgresql_features.py

def test_fulltext_search_english():
    """Test English full-text search with ranking"""
    results = search_fulltext(query="temperature control", language="en")
    assert len(results) > 0
    assert results[0]['relevance_score'] > 0.5

def test_fulltext_search_german():
    """Test German full-text search"""
    results = search_fulltext(query="Temperaturregelung", language="de")
    assert len(results) > 0

def test_jsonb_indexing():
    """Test JSONB query performance"""
    # Should use GIN index
    pass

def test_array_operations():
    """Test PostgreSQL array operations"""
    # Test domain_tags array queries
    pass
```

**6.2 Documentation**
- PostgreSQL setup guide
- Migration guide from SQLite
- Full-text search API documentation
- Performance tuning guide

---

## 📁 Deliverables

### Week 5 Deliverables:
```
src/backend/
├── models.py                       [MODIFIED] PostgreSQL models
├── database.py                     [MODIFIED] PostgreSQL connection
├── config.py                       [MODIFIED] PostgreSQL config
└── alembic/                        [NEW] Migration management
    └── versions/
        └── 001_initial_postgresql.py

scripts/
├── export_sqlite_data.py           [NEW] Export from SQLite
├── import_to_postgresql.py         [NEW] Import to PostgreSQL
└── verify_migration.py             [NEW] Verify data integrity

tests/integration/
└── test_postgresql_migration.py   [NEW] Migration tests

docs/
└── POSTGRESQL_SETUP_GUIDE.md       [NEW] Setup instructions
```

### Week 6 Deliverables:
```
src/backend/routers/
└── search.py                       [NEW] Full-text search API

scripts/
├── benchmark_databases.py          [NEW] Performance comparison
└── create_postgresql_indexes.sql  [NEW] Index creation

tests/integration/
└── test_fulltext_search.py         [NEW] FTS tests

docs/
├── FULLTEXT_SEARCH_GUIDE.md        [NEW] Search documentation
├── PERFORMANCE_BENCHMARKS.md       [NEW] Benchmark results
└── MONTH_2_COMPLETION_SUMMARY.md   [NEW] Summary
```

---

## ⏱️ Time Breakdown

| Phase | Task | Estimated Time |
|-------|------|----------------|
| **Phase 1** | PostgreSQL setup | 2 hours |
| **Phase 2** | SQLAlchemy models update | 4 hours |
| **Phase 3** | Data migration scripts | 6 hours |
| **Phase 4** | Full-text search implementation | 8 hours |
| **Phase 5** | Performance testing | 6 hours |
| **Phase 6** | Testing & documentation | 4 hours |
| **Buffer** | Troubleshooting & refinement | 10 hours |
| **Total** | **40 hours** | |

---

## ✅ Success Criteria

| Objective | Target | Measurement |
|-----------|--------|-------------|
| **Migration complete** | 100% data migrated | All 3,210 terms in PostgreSQL |
| **Data integrity** | 0 data loss | Verification script passes |
| **Full-text search** | Working for EN/DE | Search API returns ranked results |
| **Performance** | 5x faster searches | Benchmark comparison |
| **Tests passing** | 100% pass rate | All 87+ tests pass with PostgreSQL |
| **Documentation** | Complete setup guide | Others can replicate setup |

---

## 🎯 Expected Outcomes

### Technical Improvements:
- ✅ Full-text search with relevance ranking
- ✅ 5-10x faster search queries
- ✅ Normalized schema (definitions as separate table)
- ✅ Advanced JSON querying with JSONB
- ✅ Better concurrency (no single-writer bottleneck)
- ✅ Production-ready for 100,000+ terms

### Architecture Improvements:
- ✅ Proper foreign key constraints
- ✅ Automatic tsvector updates via triggers
- ✅ Indexed arrays for performance
- ✅ Point-in-time recovery capability
- ✅ Horizontal scalability with replication

---

## 🚀 Next Steps After Migration

After successful PostgreSQL migration, Month 2 can continue with:

**Week 7: Relationship Extraction** (20 hours)
- spaCy dependency parsing
- Extract term relationships (USES, PART_OF, etc.)
- Store relationships in database
- Visualization API

**Week 8: UI/UX Improvements** (20 hours)
- Enhanced search interface
- Relationship visualization
- Performance optimizations
- Mobile responsiveness

---

**Ready to begin PostgreSQL migration!**
