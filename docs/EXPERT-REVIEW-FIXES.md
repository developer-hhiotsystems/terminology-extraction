# Expert Review Fixes - Comprehensive Action Plan
**Version**: 1.0
**Date**: October 16, 2025
**Decision**: Option B - 12-Week Timeline with All Features
**Status**: Pre-Implementation Fix Document

---

## Executive Summary

8 specialized agents reviewed PRT v2.1 and IMPLEMENTATION-STRATEGY.md. This document consolidates **all critical fixes** that must be implemented before Phase 1 coding begins.

**Timeline Decision**: 12 weeks (extended from 10 weeks) to accommodate:
- All features from PRT v2.1 (TBX export, user roles, custom themes, 3 graph layouts)
- Comprehensive testing (TDD + E2E + mutation testing)
- Proper infrastructure (backups, security, monitoring)

---

## 🚨 CRITICAL FIXES (Must Complete Before Phase 1)

### 1. Database Architecture Fixes (Agent A3)

#### 1.1 Add SQLite Backup Strategy
**Current Gap**: No backup for source of truth database
**Fix Location**: PRT Section 9, IMPLEMENTATION-STRATEGY Section 8

**Implementation**:
```sql
-- Daily SQLite backup script (scripts/backup_sqlite.sh)
#!/bin/bash
BACKUP_DIR=/backups/sqlite
DATE=$(date +%Y%m%d_%H%M%S)

sqlite3 /app/data/glossary.db ".backup $BACKUP_DIR/glossary_$DATE.db"
sqlite3 /app/data/cache.db ".backup $BACKUP_DIR/cache_$DATE.db"

# Retention: 30 days
find $BACKUP_DIR -name "*.db" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/glossary_$DATE.db s3://glossary-backups/
```

**Docker Compose Addition**:
```yaml
services:
  backup:
    image: alpine:latest
    command: /bin/sh -c "crond -f"
    volumes:
      - ./scripts:/scripts
      - ./data:/app/data
      - ./backups:/backups
    environment:
      - BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
```

**Testing**: Restore backup to test environment weekly

---

#### 1.2 Add SyncLog Table for Sync Failure Tracking
**Current Gap**: No recovery mechanism for SQLite↔Neo4j sync failures
**Fix Location**: PRT Section 9, Step 1.3.2

**Schema Addition**:
```sql
CREATE TABLE SyncLog (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entry_id INTEGER NOT NULL REFERENCES GlossaryEntry(id),
  sync_status TEXT NOT NULL CHECK(sync_status IN ('pending', 'success', 'failed')),
  retry_count INTEGER DEFAULT 0,
  last_attempt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  error_message TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_synclog_status ON SyncLog(sync_status);
CREATE INDEX idx_synclog_entry ON SyncLog(entry_id);
```

**Implementation**:
```python
# src/backend/modules/graph_manager.py
def sync_to_neo4j_with_retry(entry_id: int, max_retries=3):
    for attempt in range(max_retries):
        try:
            # Perform sync
            with neo4j_driver.session() as session:
                session.run("MERGE (t:Term {id: $id}) SET ...", id=entry_id)

            # Log success
            db.execute("INSERT INTO SyncLog (entry_id, sync_status) VALUES (?, 'success')", entry_id)
            return True
        except Exception as e:
            # Log failure
            db.execute(
                "INSERT INTO SyncLog (entry_id, sync_status, retry_count, error_message) VALUES (?, 'failed', ?, ?)",
                entry_id, attempt + 1, str(e)
            )
            time.sleep(2 ** attempt)  # Exponential backoff

    # Alert after 3 failures
    sentry.capture_message(f"Neo4j sync failed for entry {entry_id} after 3 retries")
    return False
```

---

#### 1.3 Add Missing Indexes
**Current Gap**: No performance optimization for 10,000 entries
**Fix Location**: PRT Section 9, Step 1.1.2

**SQLite Indexes**:
```sql
-- Add to database/sqlite_init.sql
CREATE INDEX idx_glossary_entry_term_lang ON GlossaryEntry(term, language);
CREATE INDEX idx_glossary_entry_source ON GlossaryEntry(source);
CREATE INDEX idx_glossary_entry_validation ON GlossaryEntry(validation_status);
CREATE INDEX idx_terminology_cache_term_source ON TerminologyCache(term, source);
CREATE INDEX idx_glossary_match_quality ON GlossaryMatch(match_quality);
```

**Neo4j Indexes** (add to `database/neo4j_schema.cypher`):
```cypher
-- Auto-create on first run
CREATE INDEX term_name_idx IF NOT EXISTS FOR (t:Term) ON (t.term);
CREATE INDEX term_language_idx IF NOT EXISTS FOR (t:Term) ON (t.language);
CREATE INDEX standard_name_idx IF NOT EXISTS FOR (s:Standard) ON (s.name);
CREATE INDEX domain_name_idx IF NOT EXISTS FOR (d:Domain) ON (d.name);
CREATE CONSTRAINT term_id_unique IF NOT EXISTS FOR (t:Term) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT standard_id_unique IF NOT EXISTS FOR (s:Standard) REQUIRE s.id IS UNIQUE;
```

---

#### 1.4 Add Schema Constraints
**Current Gap**: No data validation at database level
**Fix Location**: PRT Section 9

**Enhanced GlossaryEntry Schema**:
```sql
CREATE TABLE GlossaryEntry (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  term TEXT NOT NULL,
  definition TEXT NOT NULL,
  language TEXT NOT NULL CHECK(language IN ('de', 'en')),
  source_document TEXT,
  creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP,
  domain_tags TEXT,  -- JSON array
  validation_status TEXT NOT NULL DEFAULT 'pending' CHECK(validation_status IN ('pending', 'validated')),
  source TEXT NOT NULL CHECK(source IN ('internal', 'NAMUR', 'DIN', 'ASME')),
  version INTEGER DEFAULT 1,
  last_synced_at TIMESTAMP,
  sync_status TEXT DEFAULT 'pending_sync' CHECK(sync_status IN ('pending_sync', 'synced', 'sync_failed')),
  UNIQUE(term, language, source)  -- Prevent duplicates
);
```

---

### 2. Integration Fixes (Agent A6)

#### 2.1 Replace IATE API with Cached Datasets
**Current Gap**: PRT assumes IATE has public API (it doesn't)
**Fix Location**: PRT Section 7, Steps 2.1.1-2.1.2

**PRT Section 7 Update**:
```markdown
**Before**:
- Translation/Validation: DeepL/Microsoft Translator APIs, requests for IATE/IEC

**After**:
- Translation: DeepL API with caching (500k chars/month free tier)
- Validation:
  - IATE cached dataset (quarterly TBX/CSV imports from https://iate.europa.eu/download-iate)
  - IEC Electropedia (investigate unofficial API, fallback to web scraping or cached dataset)
  - NAMUR/DIN/ASME gold standards (PDF/TBX imports)
```

**Implementation**:
```python
# src/backend/modules/iate_importer.py
def import_iate_dataset(tbx_file_path: str):
    """Import IATE TBX dataset into TerminologyCache"""
    tree = etree.parse(tbx_file_path)

    for term_entry in tree.xpath("//termEntry"):
        # Extract German term
        de_term = term_entry.xpath(".//langSet[@xml:lang='de']//term/text()")
        de_def = term_entry.xpath(".//langSet[@xml:lang='de']//descrip[@type='definition']/text()")

        # Extract English term
        en_term = term_entry.xpath(".//langSet[@xml:lang='en']//term/text()")
        en_def = term_entry.xpath(".//langSet[@xml:lang='en']//descrip[@type='definition']/text()")

        # Store in TerminologyCache
        if de_term and de_def:
            db.execute(
                "INSERT INTO TerminologyCache (term, definition, language, source, last_updated) VALUES (?, ?, 'de', 'IATE', ?)",
                de_term[0], de_def[0], datetime.now()
            )

        if en_term and en_def:
            db.execute(
                "INSERT INTO TerminologyCache (term, definition, language, source, last_updated) VALUES (?, ?, 'en', 'IATE', ?)",
                en_term[0], en_def[0], datetime.now()
            )
```

**Step 2.1.2 Update**:
```markdown
**Before**:
Step 2.1.2: Integrate IATE/DeepL APIs, TerminologyCache/Neo4j

**After**:
Step 2.1.2: Integrate IATE cached dataset, IEC API (investigate), DeepL API
- Download IATE TBX/CSV exports quarterly
- Import into TerminologyCache with source='IATE'
- Investigate IEC Electropedia API (browser DevTools, XHR analysis)
- If IEC API unavailable, implement web scraping (Playwright) or use cached dataset
- Implement DeepL client with translation caching
```

---

#### 2.2 Replace PyPDF2 with pdfplumber
**Current Gap**: PyPDF2 poor at tables/multi-column extraction
**Fix Location**: PRT Section 7, Step 1.2.2

**PRT Section 7 Update**:
```markdown
**Before**:
- PDF Parsing: PyPDF2 or pdfplumber (text), Tesseract for OCR (scanned)

**After**:
- PDF Parsing: pdfplumber (text, tables, multi-column), Tesseract for OCR (scanned)
```

**requirements.txt Update**:
```
# Remove: PyPDF2==3.0.1
# Add: pdfplumber==0.10.3
pdfplumber==0.10.3
pytesseract==0.3.10
pdf2image==1.16.3
```

**Implementation**:
```python
# src/backend/modules/pdf_parser.py
import pdfplumber
import pytesseract
from pdf2image import convert_from_path

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text with table/multi-column support"""
    with pdfplumber.open(pdf_path) as pdf:
        # Detect if scanned (heuristic: <100 chars on first page)
        first_page_text = pdf.pages[0].extract_text()

        if len(first_page_text) < 100:
            # Scanned PDF - use Tesseract OCR
            images = convert_from_path(pdf_path)
            return "\n".join(pytesseract.image_to_string(img, lang='deu+eng') for img in images)
        else:
            # Text-based PDF - use pdfplumber
            text_parts = []
            for page in pdf.pages:
                # Extract regular text
                text_parts.append(page.extract_text())

                # Extract tables separately
                tables = page.extract_tables()
                for table in tables:
                    # Convert table to text (term | definition format)
                    table_text = "\n".join(" | ".join(row) for row in table)
                    text_parts.append(table_text)

            return "\n".join(text_parts)
```

---

#### 2.3 Add Translation Caching
**Current Gap**: DeepL 500k chars/month limit will be hit quickly
**Fix Location**: Step 2.2.2

**Implementation**:
```python
# src/backend/modules/translator.py
class DeepLTranslator:
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        # Check cache first
        cached = db.query(TerminologyCache).filter_by(
            term=text,
            language=target_lang,
            source='DeepL'
        ).first()

        if cached:
            return cached.definition

        # Call DeepL API
        try:
            result = deepl_client.translate_text(text, source_lang=source_lang.upper(), target_lang=target_lang.upper())
            translation = result.text

            # Cache result
            db.add(TerminologyCache(
                term=text,
                definition=translation,
                language=target_lang,
                source='DeepL',
                last_updated=datetime.now()
            ))
            db.commit()

            return translation
        except Exception as e:
            # Fallback to gold standards
            fallback = db.query(TerminologyCache).filter(
                TerminologyCache.term.like(f"%{text}%"),
                TerminologyCache.language == target_lang,
                TerminologyCache.source.in_(['NAMUR', 'DIN', 'ASME'])
            ).first()

            if fallback:
                return fallback.definition

            raise e
```

---

### 3. Frontend Fixes (Agent A5)

#### 3.1 Add ProgressIndicator Component
**Current Gap**: Progress indicators mentioned but no component
**Fix Location**: PRT Section 10, Phase 2

**Add to PRT Section 10**:
```markdown
**Frontend Layer Components**:
- File upload (react-dropzone for PDFs/TBX)
- Gold standard import via Settings UI (NAMUR/DIN/ASME)
- Glossary review/editing with dark theme (Material-UI)
- Validation/translation controls (side-by-side with gold standards)
- Graph visualization (vis.js/Reagraph for Neo4j)
- Export options (CSV, Excel, JSON, TBX)
- Logo upload (PNG, header/settings)
- Settings for dialog colors and standards import
- **ProgressIndicator** (NEW): Reusable progress bar with determinate/indeterminate modes
- WCAG 2.1 AA compliance
```

**Implementation**:
```javascript
// src/frontend/components/ProgressIndicator.jsx
import React from 'react';
import { LinearProgress, CircularProgress, Typography, Box } from '@mui/material';

export default function ProgressIndicator({
  mode = 'determinate', // 'determinate' | 'indeterminate'
  value = 0, // 0-100
  label = '',
  variant = 'linear' // 'linear' | 'circular'
}) {
  if (variant === 'circular') {
    return (
      <Box display="flex" flexDirection="column" alignItems="center">
        <CircularProgress variant={mode} value={value} />
        {label && <Typography variant="caption" mt={1}>{label}</Typography>}
      </Box>
    );
  }

  return (
    <Box width="100%">
      <Box display="flex" justifyContent="space-between" mb={1}>
        <Typography variant="body2">{label}</Typography>
        {mode === 'determinate' && <Typography variant="body2">{value}%</Typography>}
      </Box>
      <LinearProgress variant={mode} value={value} />
    </Box>
  );
}
```

---

#### 3.2 Fix Material-UI WCAG Contrast Issues
**Current Gap**: Disabled text/borders fail WCAG 2.1 AA
**Fix Location**: Step 2.3.1

**Custom Theme**:
```javascript
// src/frontend/theme.js
import { createTheme } from '@mui/material/styles';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
    text: {
      primary: 'rgba(255, 255, 255, 0.95)', // 15.8:1 contrast
      secondary: 'rgba(255, 255, 255, 0.7)', // 12.6:1 contrast
      disabled: 'rgba(255, 255, 255, 0.5)', // FIX: 7.5:1 contrast (was 0.38 = 4.1:1)
    },
  },
  components: {
    MuiOutlinedInput: {
      styleOverrides: {
        notchedOutline: {
          borderColor: 'rgba(255, 255, 255, 0.3)', // FIX: 3.5:1 contrast (was 0.23 = 2.4:1)
        },
      },
    },
  },
});

export default darkTheme;
```

---

#### 3.3 Add Backend Pagination for Graph
**Current Gap**: 10k nodes may exceed 2 sec load time
**Fix Location**: Step 2.3.4

**Backend Endpoint**:
```python
# src/backend/app.py
@app.get("/graph-query")
async def query_graph(
    offset: int = 0,
    limit: int = 500,
    standard_filter: Optional[str] = None
):
    """Paginated graph query"""
    with neo4j_driver.session() as session:
        # Build Cypher query
        query = """
        MATCH (t:Term)-[r:DEFINED_BY]->(s:Standard)
        """
        if standard_filter:
            query += " WHERE s.name = $standard"

        query += """
        RETURN t, r, s
        SKIP $offset LIMIT $limit
        """

        result = session.run(query, offset=offset, limit=limit, standard=standard_filter)

        nodes = []
        edges = []
        for record in result:
            term = record['t']
            standard = record['s']
            rel = record['r']

            nodes.append({"id": term['id'], "label": term['term'], "type": "Term"})
            nodes.append({"id": standard['id'], "label": standard['name'], "type": "Standard"})
            edges.append({"from": term['id'], "to": standard['id'], "label": "DEFINED_BY"})

        return {"nodes": nodes, "edges": edges, "total": get_total_count(standard_filter)}
```

**Frontend Implementation**:
```javascript
// src/frontend/components/GraphVisualization.jsx
const [offset, setOffset] = useState(0);
const [limit] = useState(500);

useEffect(() => {
  fetch(`/graph-query?offset=${offset}&limit=${limit}`)
    .then(r => r.json())
    .then(data => {
      // Append to existing graph (infinite scroll)
      setGraphData(prev => ({
        nodes: [...prev.nodes, ...data.nodes],
        edges: [...prev.edges, ...data.edges]
      }));
    });
}, [offset]);

// Load more on scroll/zoom
const handleLoadMore = () => setOffset(prev => prev + limit);
```

---

### 4. DevOps Fixes (Agent A7)

#### 4.1 Add Docker Health Checks
**Current Gap**: Services can crash silently
**Fix Location**: docker-compose.yml

**Updated docker-compose.yml**:
```yaml
version: '3.8'
services:
  backend:
    build: ./src/backend
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    environment:
      - DATABASE_URL=sqlite:///./data/glossary.db
      - NEO4J_URI=bolt://neo4j:7687
    volumes:
      - ./data:/app/data
    depends_on:
      neo4j:
        condition: service_healthy

  frontend:
    build: ./src/frontend
    ports:
      - "3000:80"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3
    depends_on:
      - backend

  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"
      - "7687:7687"
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "${NEO4J_PASSWORD}", "RETURN 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    environment:
      - NEO4J_AUTH=${NEO4J_USER}/${NEO4J_PASSWORD}
      - NEO4J_dbms_memory_heap_max__size=4G
      - NEO4J_dbms_memory_pagecache_size=2G
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs

volumes:
  neo4j_data:
  neo4j_logs:
```

---

#### 4.2 Add Docker Secrets
**Current Gap**: Passwords visible in `docker inspect`
**Fix Location**: docker-compose.yml, PRT Section 9

**Create secrets**:
```bash
# Generate secrets
echo "your_neo4j_password" | docker secret create neo4j_password -
echo "your_deepl_key" | docker secret create deepl_api_key -
```

**Updated docker-compose.yml**:
```yaml
services:
  backend:
    # ... other config ...
    secrets:
      - neo4j_password
      - deepl_api_key
    environment:
      - NEO4J_PASSWORD_FILE=/run/secrets/neo4j_password
      - DEEPL_API_KEY_FILE=/run/secrets/deepl_api_key

secrets:
  neo4j_password:
    external: true
  deepl_api_key:
    external: true
```

**Backend Update**:
```python
# src/backend/config.py
import os

def read_secret(secret_name: str) -> str:
    """Read Docker secret or fallback to env var"""
    secret_file = os.getenv(f"{secret_name}_FILE")
    if secret_file and os.path.exists(secret_file):
        with open(secret_file) as f:
            return f.read().strip()
    return os.getenv(secret_name)

NEO4J_PASSWORD = read_secret("NEO4J_PASSWORD")
DEEPL_API_KEY = read_secret("DEEPL_API_KEY")
```

---

#### 4.3 Enable SQLite WAL Mode
**Current Gap**: Risk of corruption under concurrent writes
**Fix Location**: Step 1.1.2

**Implementation**:
```python
# src/backend/database.py
from sqlalchemy import create_engine, event

engine = create_engine(
    "sqlite:///./data/glossary.db",
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")  # Enable Write-Ahead Logging
    cursor.execute("PRAGMA synchronous=NORMAL")  # Balance safety/performance
    cursor.execute("PRAGMA foreign_keys=ON")  # Enforce FK constraints
    cursor.close()
```

---

### 5. Testing Strategy Fixes (Agent A4)

#### 5.1 Add E2E Smoke Tests in Phase 2
**Current Gap**: E2E deferred to Phase 4 too risky
**Fix Location**: Phase 2 Message 4

**Add to Phase 2**:
```javascript
// tests/e2e/smoke.spec.js (Phase 2, after upload endpoint ready)
describe('Smoke Test: Upload Workflow', () => {
  it('uploads internal PDF and displays extracted terms', () => {
    cy.visit('http://localhost:3000');
    cy.get('input[type="file"]').selectFile('fixtures/sample_de.pdf');
    cy.get('button').contains('Upload').click();

    // Wait for extraction
    cy.get('.progress-indicator', { timeout: 60000 }).should('not.exist');

    // Verify terms displayed
    cy.get('.terms-list').should('contain', 'Ventil'); // German term
  });
});
```

---

#### 5.2 Lower Mutation Testing Target to 70%
**Current Gap**: 80% too ambitious for first implementation
**Fix Location**: PRT Section 13, Phase 4 Step 4.1.1

**Update PRT Section 13**:
```markdown
**Before**:
- Mutation testing ≥80% mutation score (mutmut, Stryker)

**After**:
- Mutation testing ≥70% mutation score (mutmut, Stryker) for MVP
- Document acceptable surviving mutants (logging, error messages)
- Target 80% in post-MVP Phase 5 after user feedback
```

---

#### 5.3 Add Contract Testing (Pact)
**Current Gap**: Risk of mock drift between A1 (backend) and A5 (frontend)
**Fix Location**: Phase 2 Step 2.1.1

**Implementation**:
```javascript
// tests/contract/api.contract.test.js
const { Pact } = require('@pact-foundation/pact');

describe('API Contract: /validate-term', () => {
  const provider = new Pact({
    consumer: 'React Frontend',
    provider: 'FastAPI Backend',
    port: 8080,
  });

  beforeAll(() => provider.setup());
  afterAll(() => provider.finalize());

  it('returns validation result with gold standard match', async () => {
    await provider.addInteraction({
      state: 'term exists in database',
      uponReceiving: 'a request for term validation',
      withRequest: {
        method: 'POST',
        path: '/validate-term',
        body: { term: 'Ventil', language: 'de' }
      },
      willRespondWith: {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
        body: {
          term: 'Ventil',
          goldStandardMatch: { source: 'NAMUR', score: 0.95 },
          validationStatus: 'validated'
        },
      },
    });

    // Frontend code uses this contract for mock
    const response = await fetch('http://localhost:8080/validate-term', {
      method: 'POST',
      body: JSON.stringify({ term: 'Ventil', language: 'de' })
    });

    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data.goldStandardMatch.score).toBe(0.95);

    await provider.verify();
  });
});
```

**Add to requirements.txt**:
```
pact-python==2.0.1  # Backend
```

**Add to package.json**:
```json
"devDependencies": {
  "@pact-foundation/pact": "^12.1.0"
}
```

---

### 6. NLP Fixes (Agent A2)

#### 6.1 Create Ground Truth Validation Corpus
**Current Gap**: No dataset to measure 80% extraction accuracy
**Fix Location**: Pre-Phase 1 (Week 0)

**Action Items**:
1. Collect 50 German + 50 English sample documents (NAMUR/DIN/ASME excerpts)
2. Human annotates 500 term-definition pairs (ground truth)
3. Store in `tests/fixtures/nlp_ground_truth.json`:
```json
{
  "samples": [
    {
      "document": "namur_sample_01.pdf",
      "language": "de",
      "terms": [
        {"term": "Druckbehälter", "definition": "Ein Behälter zur Aufnahme von Gasen oder Flüssigkeiten..."},
        {"term": "Ventil", "definition": "Eine Armatur zum Steuern von Durchfluss..."}
      ]
    }
  ]
}
```

---

#### 6.2 Replace Pure TDD with Characterization Tests for NLP
**Current Gap**: Can't write failing test before knowing expected output
**Fix Location**: PRT Step 1.3.1

**Update Step 1.3.1**:
```markdown
**Before**:
Step 1.3.1: NLP extraction (spaCy)
- **Tests FIRST**: Unit tests for extraction rules (term-definition pattern matching)
- **Prompt**: "Using spaCy, create term-definition pair extractor..."

**After**:
Step 1.3.1: NLP extraction (spaCy) - Characterization Testing
- **Characterization Tests**: A2 manually extracts terms from 10 sample PDFs using spaCy interactively, records ground truth (expected terms), **THEN** writes tests against ground truth, **THEN** implements automated extractor
- **Prompt**: "Using spaCy and ground truth from tests/fixtures/nlp_ground_truth.json, create term-definition pair extractor. Target: ≥75% F1 score (precision + recall)."
- **Tests**: Compare extracted terms to ground truth, assert F1 ≥ 0.75
```

**Test Implementation**:
```python
# tests/unit/test_nlp_extractor.py
import pytest
import json

@pytest.fixture
def ground_truth():
    with open('tests/fixtures/nlp_ground_truth.json') as f:
        return json.load(f)

def test_extraction_meets_f1_threshold(ground_truth):
    extractor = NLPExtractor()

    total_tp = total_fp = total_fn = 0

    for sample in ground_truth['samples']:
        pdf_path = f"tests/fixtures/{sample['document']}"
        extracted = extractor.extract(pdf_path)
        expected = set(t['term'] for t in sample['terms'])

        # True positives, false positives, false negatives
        tp = len(set(extracted) & expected)
        fp = len(set(extracted) - expected)
        fn = len(expected - set(extracted))

        total_tp += tp
        total_fp += fp
        total_fn += fn

    # Calculate F1 score
    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    assert f1 >= 0.75, f"F1 score {f1:.2f} below threshold 0.75"
```

---

### 7. Timeline Adjustment (Agent A8)

#### 7.1 Extend to 12 Weeks
**Rationale**: Accommodate all features + TDD overhead + infrastructure setup

**Updated Timeline**:
| Phase | Weeks | Changes from 10-Week Plan |
|-------|-------|---------------------------|
| **Pre-Phase (Setup)** | 0.5 weeks | NEW: Ground truth corpus creation, A3 Neo4j bootcamp |
| **Phase 1** | 2 weeks | +1 day for database fixes (backups, indexes, SyncLog) |
| **Phase 2** | 4 weeks | +0.5 weeks (was 3.5) for frontend complexity |
| **Phase 3** | 2.5 weeks | +0.5 weeks (was 2) for TBX validation |
| **Phase 4** | 3 weeks | +0.5 weeks (was 2.5) for security hardening, monitoring setup |
| **TOTAL** | **12 weeks** | +2 weeks from original 10-week plan |

---

## 📋 Pre-Phase 1 Checklist (Week 0)

Before spawning agents for Phase 1, complete these tasks:

- [ ] Create ground truth NLP corpus (500 term-definition pairs)
- [ ] A3 completes Neo4j bootcamp (GraphAcademy course, 1 week)
- [ ] Download IATE TBX/CSV dataset from https://iate.europa.eu/download-iate
- [ ] Setup local Neo4j Community Edition for development
- [ ] Install all dependencies (pdfplumber, neo4j-driver, deepl, etc.)
- [ ] Create `scripts/backup_sqlite.sh` and test restore procedure
- [ ] Generate Docker secrets for NEO4J_PASSWORD, DEEPL_API_KEY
- [ ] Create `.env.example` with all environment variables documented
- [ ] Review and approve updated PRT v2.2 (to be created)
- [ ] Review and approve IMPLEMENTATION-STRATEGY v1.1 (to be created)

---

## 🚀 Next Steps

1. **Update PRT v2.2**: Incorporate all fixes from this document
2. **Update IMPLEMENTATION-STRATEGY v1.1**: Adjust to 12-week timeline
3. **Create Phase Gate Checklist**: Mandatory verification points between phases
4. **Begin Phase 1**: After approval of PRT v2.2 and completion of Week 0 checklist

---

**End of Expert Review Fixes Document**
