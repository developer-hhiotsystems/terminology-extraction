# Month 2: SQLite FTS5 Full-Text Search Implementation
## Weeks 5-6 - Production-Ready Search

**Date:** 2025-10-19
**Phase:** Month 2 - Weeks 5-6
**Estimated Time:** 20 hours
**Goal:** Implement advanced full-text search using SQLite FTS5

---

## 📋 Why SQLite FTS5?

### ✅ Perfect for Your Use Case

**Corporate Environment Benefits:**
- ✅ **File-based** - Easy deployment, no server needed
- ✅ **No installation** - FTS5 is built into SQLite 3.9.0+
- ✅ **No admin rights** - Works with existing setup
- ✅ **Production-ready** - Used by Firefox, Chrome, iOS apps
- ✅ **MS SQL Server later** - Easy migration path when needed

**Technical Benefits:**
- ✅ **Fast** - Handles millions of rows efficiently
- ✅ **Bilingual** - Supports English + German tokenization
- ✅ **Advanced features** - Ranking, stemming, phrase search, wildcards
- ✅ **Low memory** - Efficient indexing algorithm
- ✅ **ACID compliant** - Transactional consistency

**Current Limitations (SQLite without FTS):**
- ❌ Basic LIKE queries: `WHERE term LIKE '%temperature%'`
- ❌ No relevance ranking
- ❌ No stemming (temperature vs temperatures)
- ❌ Slow on 10,000+ terms
- ❌ No phrase search
- ❌ Full table scans

**With FTS5:**
- ✅ Intelligent matching with ranking
- ✅ Stemming support (run → running → runs)
- ✅ 10-100x faster searches
- ✅ Phrase search: `"exact phrase"`
- ✅ Boolean operators: `term1 AND term2 OR term3`
- ✅ Indexed searches (no table scans)

---

## 🎯 Implementation Goals

### Week 5: FTS5 Setup & Basic Search (10 hours)
1. **Create FTS5 virtual table** (2 hours)
   - Design FTS5 schema
   - Create virtual table with proper tokenizers
   - Configure for English/German

2. **Populate FTS5 index** (2 hours)
   - Migrate existing 3,210 terms to FTS5
   - Create automatic sync triggers
   - Verify data integrity

3. **Implement basic search API** (2 hours)
   - Create `/api/search/fulltext` endpoint
   - Basic keyword search
   - Return results with metadata

4. **Add ranking and relevance** (2 hours)
   - Implement BM25 ranking algorithm
   - Sort by relevance score
   - Highlight matched terms

5. **Testing and validation** (2 hours)
   - Test search accuracy
   - Verify ranking
   - Performance testing

### Week 6: Advanced Search Features (10 hours)
1. **Phrase search and wildcards** (2 hours)
   - Exact phrase matching: `"temperature control"`
   - Prefix search: `temp*`
   - Complex queries: `(temp* OR heat) AND control`

2. **Domain filtering** (2 hours)
   - Filter by domain tags
   - Combine FTS with SQL WHERE clauses
   - Multi-domain search

3. **Language-specific search** (2 hours)
   - English-only search
   - German-only search
   - Bilingual search with language detection

4. **Search API optimization** (2 hours)
   - Pagination for large result sets
   - Query caching
   - Search suggestions/autocomplete

5. **Documentation and benchmarking** (2 hours)
   - API documentation
   - Performance benchmarks
   - User guide

---

## 🏗️ SQLite FTS5 Architecture

### Current Schema (SQLite without FTS)
```sql
CREATE TABLE glossary_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT NOT NULL,
    definitions JSON NOT NULL,
    language TEXT NOT NULL,
    -- ... other fields
);

-- Current search (slow, no ranking)
SELECT * FROM glossary_entries
WHERE term LIKE '%temperature%'
   OR json_extract(definitions, '$[0].text') LIKE '%temperature%';
```

### New Schema (With FTS5)
```sql
-- Original table remains unchanged
CREATE TABLE glossary_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT NOT NULL,
    definitions JSON NOT NULL,
    language TEXT NOT NULL,
    -- ... other fields
);

-- NEW: FTS5 virtual table (index only, no data duplication)
CREATE VIRTUAL TABLE glossary_fts USING fts5(
    term,                    -- Indexed for search
    definition_text,         -- Extracted definition text
    language,                -- For language filtering
    domain_tags,            -- For domain filtering
    content='glossary_entries',  -- Links to original table
    content_rowid='id',         -- Maps to glossary_entries.id
    tokenize='porter unicode61 remove_diacritics 2'  -- English stemming
);

-- Automatic sync triggers
CREATE TRIGGER glossary_fts_insert AFTER INSERT ON glossary_entries BEGIN
    INSERT INTO glossary_fts(rowid, term, definition_text, language, domain_tags)
    VALUES (
        new.id,
        new.term,
        json_extract(new.definitions, '$[0].text'),
        new.language,
        COALESCE(json_extract(new.domain_tags, '$'), '')
    );
END;

CREATE TRIGGER glossary_fts_update AFTER UPDATE ON glossary_entries BEGIN
    UPDATE glossary_fts
    SET term = new.term,
        definition_text = json_extract(new.definitions, '$[0].text'),
        language = new.language,
        domain_tags = COALESCE(json_extract(new.domain_tags, '$'), '')
    WHERE rowid = new.id;
END;

CREATE TRIGGER glossary_fts_delete AFTER DELETE ON glossary_entries BEGIN
    DELETE FROM glossary_fts WHERE rowid = old.id;
END;

-- Fast search with ranking (BM25 algorithm)
SELECT
    ge.*,
    fts.rank AS relevance_score
FROM glossary_fts fts
JOIN glossary_entries ge ON fts.rowid = ge.id
WHERE glossary_fts MATCH 'temperature control'
ORDER BY fts.rank
LIMIT 10;
```

---

## 🔍 FTS5 Search Features

### 1. Basic Keyword Search
```sql
-- Simple keyword
SELECT * FROM glossary_fts WHERE glossary_fts MATCH 'temperature';

-- Multiple keywords (implicit AND)
SELECT * FROM glossary_fts WHERE glossary_fts MATCH 'temperature control';
```

### 2. Boolean Operators
```sql
-- AND operator
SELECT * FROM glossary_fts WHERE glossary_fts MATCH 'temperature AND control';

-- OR operator
SELECT * FROM glossary_fts WHERE glossary_fts MATCH 'temperature OR heat';

-- NOT operator
SELECT * FROM glossary_fts WHERE glossary_fts MATCH 'temperature NOT sensor';

-- Complex queries
SELECT * FROM glossary_fts
WHERE glossary_fts MATCH '(temperature OR heat) AND (control OR regulation)';
```

### 3. Phrase Search
```sql
-- Exact phrase
SELECT * FROM glossary_fts WHERE glossary_fts MATCH '"temperature control"';

-- Phrase with wildcards
SELECT * FROM glossary_fts WHERE glossary_fts MATCH '"temperature *"';
```

### 4. Prefix Search (Wildcards)
```sql
-- Prefix matching
SELECT * FROM glossary_fts WHERE glossary_fts MATCH 'temp*';

-- Finds: temperature, temporal, template, etc.
```

### 5. Column-Specific Search
```sql
-- Search only in term column
SELECT * FROM glossary_fts WHERE glossary_fts MATCH 'term:temperature';

-- Search only in definitions
SELECT * FROM glossary_fts WHERE glossary_fts MATCH 'definition_text:sensor';
```

### 6. Ranking and Relevance
```sql
-- BM25 ranking (higher = more relevant)
SELECT
    term,
    bm25(glossary_fts) AS score
FROM glossary_fts
WHERE glossary_fts MATCH 'temperature'
ORDER BY score;

-- Custom ranking weights
SELECT
    term,
    bm25(glossary_fts, 10.0, 5.0) AS score  -- Weight term column higher
FROM glossary_fts
WHERE glossary_fts MATCH 'temperature'
ORDER BY score;
```

### 7. Snippets and Highlighting
```sql
-- Extract context snippet
SELECT
    term,
    snippet(glossary_fts, 1, '<b>', '</b>', '...', 15) AS snippet
FROM glossary_fts
WHERE glossary_fts MATCH 'temperature'
LIMIT 5;

-- Result: "...for <b>temperature</b> control in..."
```

---

## 📁 Implementation Files

### Phase 1: Database Schema (2 hours)

**File: `scripts/create_fts5_index.sql`**
```sql
-- Create FTS5 virtual table
CREATE VIRTUAL TABLE IF NOT EXISTS glossary_fts USING fts5(
    term,
    definition_text,
    language UNINDEXED,
    domain_tags UNINDEXED,
    content='glossary_entries',
    content_rowid='id',
    tokenize='porter unicode61 remove_diacritics 2'
);

-- Triggers for automatic synchronization
CREATE TRIGGER IF NOT EXISTS glossary_fts_insert
AFTER INSERT ON glossary_entries BEGIN
    INSERT INTO glossary_fts(rowid, term, definition_text, language, domain_tags)
    VALUES (
        new.id,
        new.term,
        (SELECT json_extract(value, '$.text')
         FROM json_each(new.definitions)
         WHERE json_extract(value, '$.is_primary') = 1
         LIMIT 1),
        new.language,
        COALESCE((SELECT group_concat(value) FROM json_each(new.domain_tags)), '')
    );
END;

CREATE TRIGGER IF NOT EXISTS glossary_fts_update
AFTER UPDATE ON glossary_entries BEGIN
    UPDATE glossary_fts
    SET term = new.term,
        definition_text = (SELECT json_extract(value, '$.text')
                          FROM json_each(new.definitions)
                          WHERE json_extract(value, '$.is_primary') = 1
                          LIMIT 1),
        language = new.language,
        domain_tags = COALESCE((SELECT group_concat(value) FROM json_each(new.domain_tags)), '')
    WHERE rowid = new.id;
END;

CREATE TRIGGER IF NOT EXISTS glossary_fts_delete
AFTER DELETE ON glossary_entries BEGIN
    DELETE FROM glossary_fts WHERE rowid = old.id;
END;

-- Populate FTS5 with existing data
INSERT INTO glossary_fts(rowid, term, definition_text, language, domain_tags)
SELECT
    id,
    term,
    (SELECT json_extract(value, '$.text')
     FROM json_each(definitions)
     WHERE json_extract(value, '$.is_primary') = 1
     LIMIT 1),
    language,
    COALESCE((SELECT group_concat(value) FROM json_each(domain_tags)), '')
FROM glossary_entries;
```

---

### Phase 2: Python Integration (2 hours)

**File: `src/backend/database.py` (Update)**
```python
def initialize_fts5():
    """Initialize FTS5 full-text search index"""
    from pathlib import Path
    import sqlite3

    db_path = Path('./data/glossary.db')
    if not db_path.exists():
        return

    conn = sqlite3.connect(str(db_path))

    # Read and execute FTS5 schema
    with open('scripts/create_fts5_index.sql') as f:
        fts5_schema = f.read()
        conn.executescript(fts5_schema)

    conn.commit()
    conn.close()

    logger.info("FTS5 full-text search index initialized")

# Add to startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Glossary Application...")
    initialize_database()
    initialize_fts5()  # Add FTS5 initialization
    # ... rest of startup
```

---

### Phase 3: Search API (4 hours)

**File: `src/backend/routers/search.py` (New)**
```python
"""
Full-Text Search API using SQLite FTS5
Provides advanced search with ranking, phrase search, and filtering
"""
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
import logging

from src.backend.database import get_db
from src.backend.constants import LANG_ENGLISH, LANG_GERMAN
from src.backend.models import GlossaryEntry

router = APIRouter(prefix="/api/search", tags=["search"])
logger = logging.getLogger(__name__)


@router.get("/fulltext")
async def fulltext_search(
    query: str = Query(..., min_length=2, description="Search query"),
    language: Optional[str] = Query(None, pattern="^(en|de)$", description="Filter by language"),
    domain: Optional[str] = Query(None, description="Filter by domain tag"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Results offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Full-text search with SQLite FTS5

    Features:
    - Relevance ranking (BM25 algorithm)
    - Phrase search: "exact phrase"
    - Wildcards: temp*
    - Boolean operators: temperature AND control
    - Language filtering
    - Domain filtering

    Examples:
    - Simple: temperature
    - Phrase: "temperature control"
    - Boolean: (temperature OR heat) AND control
    - Wildcard: temp*
    - Column-specific: term:temperature
    """
    try:
        # Build FTS5 query
        fts_query = query.strip()

        # Build SQL query with FTS5
        sql = """
        SELECT
            ge.id,
            ge.term,
            ge.definitions,
            ge.language,
            ge.source,
            ge.domain_tags,
            ge.validation_status,
            bm25(glossary_fts) AS relevance_score,
            snippet(glossary_fts, 1, '<mark>', '</mark>', '...', 32) AS snippet
        FROM glossary_fts fts
        JOIN glossary_entries ge ON fts.rowid = ge.id
        WHERE glossary_fts MATCH :query
        """

        # Add language filter
        if language:
            sql += " AND ge.language = :language"

        # Add domain filter (if domain tags contain the specified domain)
        if domain:
            sql += " AND EXISTS (SELECT 1 FROM json_each(ge.domain_tags) WHERE value = :domain)"

        # Order by relevance
        sql += " ORDER BY relevance_score LIMIT :limit OFFSET :offset"

        # Execute query
        params = {"query": fts_query, "limit": limit, "offset": offset}
        if language:
            params["language"] = language
        if domain:
            params["domain"] = domain

        result = db.execute(text(sql), params)
        rows = result.fetchall()

        # Format results
        results = []
        for row in rows:
            results.append({
                "id": row[0],
                "term": row[1],
                "definitions": row[2],
                "language": row[3],
                "source": row[4],
                "domain_tags": row[5],
                "validation_status": row[6],
                "relevance_score": abs(row[7]),  # BM25 is negative, convert to positive
                "snippet": row[8]
            })

        # Get total count (without limit/offset)
        count_sql = """
        SELECT COUNT(*)
        FROM glossary_fts fts
        JOIN glossary_entries ge ON fts.rowid = ge.id
        WHERE glossary_fts MATCH :query
        """
        if language:
            count_sql += " AND ge.language = :language"
        if domain:
            count_sql += " AND EXISTS (SELECT 1 FROM json_each(ge.domain_tags) WHERE value = :domain)"

        count_params = {"query": fts_query}
        if language:
            count_params["language"] = language
        if domain:
            count_params["domain"] = domain

        total = db.execute(text(count_sql), count_params).scalar()

        return {
            "query": query,
            "total": total,
            "count": len(results),
            "limit": limit,
            "offset": offset,
            "results": results
        }

    except Exception as e:
        logger.error(f"FTS5 search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/suggest")
async def search_suggestions(
    query: str = Query(..., min_length=1, description="Partial query for suggestions"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get search suggestions using FTS5 prefix search

    Returns matching terms for autocomplete
    """
    try:
        # Use prefix search with FTS5
        sql = """
        SELECT DISTINCT
            ge.term,
            ge.language
        FROM glossary_fts fts
        JOIN glossary_entries ge ON fts.rowid = ge.id
        WHERE glossary_fts MATCH :query || '*'
        ORDER BY bm25(glossary_fts)
        LIMIT :limit
        """

        result = db.execute(text(sql), {"query": query.strip(), "limit": limit})
        suggestions = [{"term": row[0], "language": row[1]} for row in result.fetchall()]

        return {
            "query": query,
            "suggestions": suggestions
        }

    except Exception as e:
        logger.error(f"Suggestion error: {e}")
        raise HTTPException(status_code=500, detail=f"Suggestion error: {str(e)}")
```

---

## 📊 Performance Benchmarks

### Expected Performance Improvements

**Current (LIKE queries):**
```sql
-- Slow: Full table scan
SELECT * FROM glossary_entries
WHERE term LIKE '%temperature%';
-- Time: ~500ms for 10,000 terms
```

**With FTS5:**
```sql
-- Fast: Indexed search
SELECT * FROM glossary_fts
WHERE glossary_fts MATCH 'temperature';
-- Time: ~5-10ms for 10,000 terms
```

**Performance Gains:**
- **10-100x faster** searches
- **Constant time** regardless of result set size
- **Efficient** memory usage
- **Scalable** to millions of terms

---

## ✅ Success Criteria

| Objective | Target | Measurement |
|-----------|--------|-------------|
| **FTS5 setup** | Working index | Query returns results |
| **Sync working** | Auto-updates | Insert/update/delete syncs to FTS5 |
| **Basic search** | Keyword search | Returns ranked results |
| **Phrase search** | Exact phrases | `"exact match"` works |
| **Wildcards** | Prefix search | `temp*` returns temp* terms |
| **Performance** | 10x faster | Benchmark comparison |
| **Documentation** | API docs | Complete search guide |

---

## 🎉 Deliverables

### Code Files:
```
scripts/
└── create_fts5_index.sql          [NEW] FTS5 schema and triggers

src/backend/
├── database.py                     [MODIFIED] Add initialize_fts5()
└── routers/
    └── search.py                   [NEW] Full-text search API

tests/
└── test_fts5_search.py            [NEW] FTS5 search tests

docs/
├── MONTH_2_SQLITE_FTS5_PLAN.md    [NEW] This document
└── FTS5_SEARCH_API_GUIDE.md       [NEW] User guide
```

---

## 🚀 Next Steps

1. **Create FTS5 schema** (scripts/create_fts5_index.sql)
2. **Update database.py** (initialize_fts5())
3. **Create search API** (routers/search.py)
4. **Populate FTS5** with 3,210 existing terms
5. **Test search** functionality
6. **Benchmark** performance
7. **Document** API

**Ready to implement!**
