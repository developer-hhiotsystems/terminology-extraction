# PRT Changelog: v2.0 → v2.1 → v2.2

**Last Updated**: October 16, 2025
**Updated By**: Claude (Anthropic)
**Reason**: Critical gaps identified for agentic development with Claude-Flow, then expert review fixes

---

## Summary of Changes

This update addresses **5 critical gaps** between the original PRT v2.0 and the concurrent execution requirements from CLAUDE.md (global configuration). The changes ensure successful implementation using Claude-Flow orchestration and agentic development patterns.

---

## 🚨 Critical Update #1: Concurrent Execution Strategy

### Issue
- **v2.0**: Section 18 (Implementation Plan) used sequential step numbering (1.1.1 → 1.1.2 → 1.2.1), suggesting waterfall approach
- **CLAUDE.md requirement**: "ALL operations MUST be concurrent/parallel in a single message"
- **Conflict**: No explicit guidance on how to spawn agents concurrently or batch operations

### Changes in v2.1
**Section 17 - Agentic Development Strategy**:
- Added **"Concurrent Execution Pattern (CRITICAL)"** subsection
- Included code examples showing correct (✅) vs wrong (❌) concurrent execution
- Defined "GOLDEN RULE: All related operations in a single message"

**Section 18 - Implementation Plan**:
- Restructured each phase with **"Concurrent Agent Spawn (Message N)"** blocks
- Example:
  ```javascript
  [Message 1 - Phase 1 Initialization]:
    Task("Python Developer", "Steps 1.1.1-1.1.2...", "backend-dev")
    Task("Database Engineer", "Setup schemas...", "code-analyzer")
    TodoWrite { todos: [6+ items...] }
    Bash "mkdir -p src/{backend,frontend,database,tests}"
  ```
- Added mandatory batching for TodoWrite, file operations, and agent spawning

### Impact
- **High**: Without this, agents would run sequentially, violating CLAUDE.md requirements and breaking swarm coordination

---

## 🚨 Critical Update #2: Agent Role Mapping

### Issue
- **v2.0**: Section 16 listed human-like roles (Python Developer, NLP Specialist) without mapping to Claude-Flow agent types
- **CLAUDE.md**: Lists 54 agent types (`coder`, `researcher`, `backend-dev`, `tdd-london-swarm`, etc.)
- **Gap**: No clear mapping between PRT roles and which Claude-Flow agent to spawn

### Changes in v2.1
**Section 16 - Development Team Roles & Agent Mapping**:
- Added table with 4 columns:
  1. PRT Role (human role from v2.0)
  2. Claude-Flow Agent Type(s) (which agent to spawn)
  3. Primary Responsibilities
  4. Tools/Technologies

- Example mapping:
  | PRT Role | Claude-Flow Agent Type | Responsibilities |
  |----------|------------------------|------------------|
  | Python Developer | `backend-dev`, `coder` | FastAPI, Neo4j integration |
  | Unit Testing Engineer | `tester`, `tdd-london-swarm` | TDD, pytest, mutation testing |

- Added note: "Use **Claude Code's Task tool** to spawn agents (not MCP tools)"

### Impact
- **High**: Without this, developers would not know which agent type to spawn for each task, causing implementation delays

---

## 🚨 Critical Update #3: TDD Clarification

### Issue
- **v2.0**: Section 13 mentioned "Block merges if coverage < threshold" (implies CI/CD gates)
- **v2.0**: Section 18 Phase 4 titled "Testing & Polish (Weeks 8-10)" suggested testing happens at the END
- **Conflict**: If testing is Phase 4, how do earlier milestones require ≥80% coverage?
- **SPARC/CLAUDE.md**: Promotes Test-Driven Development (TDD - tests FIRST)

### Changes in v2.1
**Section 13 - Unit Testing & CI/CD Integration**:
- Added **"Test-Driven Development (TDD) Approach"** subsection
- Clarified: "Write tests FIRST before implementation code"
- Defined TDD cycle: Red-Green-Refactor
- Explained: "Tests are integrated into **every phase** (Phases 1-3), not just Phase 4"
- Phase 4 redefined as: "Comprehensive test EXPANSION, E2E, mutation testing"

**Section 18 - Implementation Plan (Every Step)**:
- Added **"Tests FIRST"** before **"Then"** implementation for EVERY step
- Example:
  ```
  Step 1.1.1: Initialize FastAPI
    - **Tests FIRST**: Write pytest for /health endpoint (status 200)
    - **Prompt**: "Create FastAPI app skeleton..."
    - **Then**: Implement FastAPI app with endpoint
  ```

**Section 18 Phase Descriptions**:
- Phase 1-3: "TDD approach - write tests first, then implement"
- Phase 4: "Expand test coverage, add E2E/mutation tests"

### Impact
- **High**: Ensures code quality from start, prevents technical debt, aligns with SPARC methodology

---

## 🚨 Critical Update #4: Neo4j Sync Architecture

### Issue
- **v2.0**: Section 9 described Neo4j nodes (Term, Standard) and SQLite tables (GlossaryEntry)
- **Ambiguity**: Which is the source of truth? How are they kept in sync? Are there sync conflicts?
- **Missing**: Connection details, sync strategy, conflict resolution

### Changes in v2.1
**Section 9 - Data Model Overview**:
- Added **"Database Architecture"** subsection:
  1. SQLite/H2 = Source of truth for glossary data
  2. Neo4j = Derived visualization layer (read-only from UI)

- Added **"Sync Strategy"** subsection:
  - One-way sync: SQLite → Neo4j
  - Triggers: After GlossaryEntry INSERT/UPDATE → call `sync_to_neo4j(entry_id)`
  - Neo4j is read-only (users query/visualize, not edit directly)
  - Sync timing: On-demand (after extraction/validation) or scheduled (hourly batch)

- Added **"Neo4j Setup"** subsection:
  - Deployment: Docker `neo4j:5.x-community`
  - Connection: `bolt://localhost:7687`
  - Credentials: Environment variables (`NEO4J_USER`, `NEO4J_PASSWORD`)
  - Initialization: Auto-create UNIQUE constraints on Term.id, Standard.id
  - Backup: Weekly `neo4j-admin dump`

- Added **"Sync Details"** to graph model:
  - Term nodes sync with GlossaryEntry via `id` (1:1 mapping)
  - Standard nodes created from NAMUR/DIN/ASME uploads (no SQLite equivalent)

### Impact
- **Medium**: Prevents data inconsistency bugs, clarifies implementation approach, reduces Neo4j learning curve

---

## 🚨 Critical Update #5: Gold Standard Import Workflow

### Issue
- **v2.0**: Section 8 Workflow Summary mixed internal documents and gold standards:
  - "Upload PDF (de/en) or NAMUR/DIN/ASME" (implies same process)
- **v2.0**: Section 18 Step 1.2.1: "Add /upload-pdf, /upload-tbx endpoints (tag gold standards)"
  - What does "tag" mean? User input? Filename detection?
- **Ambiguity**: How does user distinguish "internal PDF" from "NAMUR PDF" during upload? Are they validated differently?

### Changes in v2.1
**Section 8 - Workflow Summary**:
- Split into **3 distinct workflows**:
  - **Workflow A: Internal Document Processing** (user's internal PDFs, source='internal')
  - **Workflow B: Gold Standard Import** (NAMUR/DIN/ASME via Settings UI, source='NAMUR'/'DIN'/'ASME')
  - **Workflow C: Complete Glossary Pipeline** (combines A + B)

- **Workflow B details**:
  1. User opens "Settings → Import Gold Standards"
  2. Upload file (PDF or TBX)
  3. Select standard type from **dropdown** (NAMUR, DIN, ASME)
  4. System processes based on file type:
     - PDF: Extract → TerminologyCache + Neo4j Standard node
     - TBX: Parse → TerminologyCache + Neo4j Standard node
  5. Gold standard terms are **read-only**, used for validation only

**Section 18 Step 1.2.1**:
- Split into **2 separate endpoints**:
  - `/upload-document` (for internal PDFs, params: file, language)
  - `/import-standard` (for gold standards, params: file, standard_type, file_format)
- Clarified tagging: User selects from dropdown, not automatic detection

**Updated Text-Based Workflow Diagram**:
- Added branching for Workflow A vs Workflow B
- Shows separate paths for internal vs gold standard documents

### Impact
- **Medium**: Prevents UX confusion, clarifies implementation requirements, ensures proper data categorization

---

## Additional Minor Updates

### Section 9 - Data Model
- Added **TRANSLATED_FROM** relationship to Neo4j graph model:
  - `(Term)-[:TRANSLATED_FROM {method: 'DeepL'}]->(Term)`
  - Tracks translation origin for auditability

### Section 13 - Testing Strategy
- Added subsection: **"Testing Strategy Per Phase"**
  - Phase 1-3: Unit/integration tests alongside development
  - Phase 4: E2E, accessibility, mutation, performance tests

### Section 14 - Unit Testing Strategy
- Added: "Data Sync: Test SQLite ↔ Neo4j synchronization accuracy"

### Section 17 - Agent Coordination Hooks
- Added code blocks for mandatory hooks:
  - Before Work: `pre-task`, `session-restore`
  - During Work: `post-edit`, `notify`
  - After Work: `post-task`, `session-end`

### Section 18 - All Phase Steps
- Every step now follows format:
  1. **Tests FIRST**: [specific test description]
  2. **Prompt**: [Claude prompt for agent]
  3. **Then**: [implementation action]

### Section 19 - Acceptance Criteria
- Updated: "Import NAMUR/DIN/ASME (PDF/TBX) via Workflow B (Settings UI with dropdown)"
- Added: "Visualize term-standard relationships in Neo4j graph (interactive, <2 sec queries)"

### Section 24 - Open Questions
- Added: "Database choice? (SQLite recommended for simplicity; H2 if Java ecosystem integration needed)"

### Section 26 - References
- Added: Claude-Flow GitHub link (https://github.com/ruvnet/claude-flow)

### Section 26 - Revision History
- Added v2.1 entry with summary of 5 critical updates

---

## Migration Guide: Implementing with v2.1

### For Developers Starting Implementation

1. **Read Section 17 First**: Understand concurrent execution pattern (CRITICAL)
2. **Reference Section 16 Table**: Know which Claude-Flow agent to spawn for each task
3. **Follow Section 18 TDD Format**: Always write tests FIRST
4. **Use Section 8 Workflows A/B/C**: Separate internal documents from gold standards
5. **Implement Section 9 Sync Strategy**: One-way SQLite → Neo4j, read-only graph

### Key Behavioral Changes from v2.0

| Aspect | v2.0 Behavior | v2.1 Behavior |
|--------|---------------|---------------|
| Agent Spawning | Not specified | Concurrent in single message (Section 17) |
| Testing | Phase 4 only | TDD from Phase 1 (Section 13, 18) |
| Gold Standards | Same as internal docs | Separate workflow via Settings UI (Section 8) |
| Neo4j Sync | Not defined | One-way SQLite → Neo4j (Section 9) |
| Agent Types | Human roles only | Mapped to Claude-Flow agents (Section 16) |

---

## Validation Checklist

Before starting implementation, ensure:
- [ ] You understand concurrent execution pattern (Section 17)
- [ ] You can map each task to a Claude-Flow agent type (Section 16)
- [ ] You know TDD workflow (tests first, then code - Section 13)
- [ ] You can distinguish Workflow A (internal) from Workflow B (gold standards - Section 8)
- [ ] You understand Neo4j is read-only, synced from SQLite (Section 9)
- [ ] You have Neo4j Community Edition installed or Docker ready (Section 9)

---

## Questions or Issues?

If you encounter ambiguities not resolved by v2.1, please:
1. Check CLAUDE.md (global configuration) for overriding rules
2. Refer to Claude-Flow docs: https://github.com/ruvnet/claude-flow
3. Consult Section 25 (References) for ISO standards, tool documentation
4. Document the issue for potential v2.2 update

---

---

# PRT Changelog: v2.1 → v2.2

**Date**: October 16, 2025
**Updated By**: Claude (Anthropic) with 8 Expert Agents (A1-A8)
**Reason**: Expert review identified production readiness gaps, integration issues, and testing improvements

---

## Summary of Changes

This update addresses **expert review findings** from 8 specialized agents who reviewed PRT v2.1 and IMPLEMENTATION-STRATEGY.md. The changes ensure production-ready implementation with proper infrastructure, realistic testing targets, and comprehensive error handling.

**Key Decision**: Extended timeline from **10 weeks to 12 weeks** to accommodate all features with proper quality assurance.

---

## 🚨 Critical Update #1: Database Infrastructure Hardening

### Issues Identified by Agent A3 (Database Engineer)
- **v2.1**: No backup strategy for SQLite (source of truth database)
- **v2.1**: No recovery mechanism for SQLite↔Neo4j sync failures
- **v2.1**: Missing performance indexes for 10,000 entries
- **v2.1**: No schema constraints to prevent invalid data
- **v2.1**: Risk of corruption under concurrent writes

### Changes in v2.2

**Section 9 - Data Model Overview**:
- Added **SyncLog table** for tracking sync failures:
  ```sql
  CREATE TABLE SyncLog (
    id INTEGER PRIMARY KEY,
    entry_id INTEGER REFERENCES GlossaryEntry(id),
    sync_status TEXT CHECK(sync_status IN ('pending', 'success', 'failed')),
    retry_count INTEGER DEFAULT 0,
    last_attempt TIMESTAMP,
    error_message TEXT
  );
  ```
- Added **UploadedDocument table** for file metadata tracking
- Added comprehensive **indexes**:
  - `idx_glossary_entry_term_lang` ON (term, language)
  - `idx_terminology_cache_term_source` ON (term, source)
  - `idx_synclog_status` ON (sync_status)
- Added **CHECK constraints**:
  - `language CHECK(language IN ('de', 'en'))`
  - `source CHECK(source IN ('internal', 'NAMUR', 'DIN', 'ASME'))`
  - `validation_status CHECK(validation_status IN ('pending', 'validated'))`
- Added **UNIQUE constraint**: `UNIQUE(term, language, source)` to prevent duplicates
- Enhanced GlossaryEntry with `sync_status`, `updated_at` fields

**Section 9 - Backup Strategy**:
- **Daily SQLite backups**: Cron job via `scripts/backup_sqlite.sh` with 30-day retention
- **Weekly Neo4j dumps**: `neo4j-admin dump` with 8-week retention
- **Testing**: Weekly restore to test environment for verification
- **Offsite storage**: Optional S3 upload for long-term backups

**Section 9 - SQLite WAL Mode**:
```python
# Enable Write-Ahead Logging for concurrent writes
cursor.execute("PRAGMA journal_mode=WAL")
cursor.execute("PRAGMA synchronous=NORMAL")
cursor.execute("PRAGMA foreign_keys=ON")
```

**Section 9 - Neo4j Indexes**:
```cypher
CREATE INDEX term_name_idx IF NOT EXISTS FOR (t:Term) ON (t.term);
CREATE INDEX term_language_idx IF NOT EXISTS FOR (t:Term) ON (t.language);
CREATE CONSTRAINT term_id_unique IF NOT EXISTS FOR (t:Term) REQUIRE t.id IS UNIQUE;
```

**Step 1.3.2 - Sync Retry Logic**:
```python
def sync_to_neo4j_with_retry(entry_id: int, max_retries=3):
    for attempt in range(max_retries):
        try:
            # Perform sync
            return True
        except Exception as e:
            db.execute("INSERT INTO SyncLog (...) VALUES (...)")
            time.sleep(2 ** attempt)  # Exponential backoff
    sentry.capture_message(f"Sync failed after 3 retries")
```

### Impact
- **High**: Prevents data loss, enables recovery from sync failures, improves performance, ensures data integrity

---

## 🚨 Critical Update #2: Integration Layer Fixes

### Issues Identified by Agent A6 (Integration Engineer)
- **v2.1**: IATE has no public API (PRT incorrectly assumed API exists)
- **v2.1**: PyPDF2 poor at extracting tables/multi-column text
- **v2.1**: DeepL 500k chars/month limit will be hit quickly without caching

### Changes in v2.2

**Section 7 - Technology Stack**:
- **Before**: "requests for IATE/IEC"
- **After**: "IATE cached dataset (quarterly TBX/CSV imports from https://iate.europa.eu/download-iate), IEC Electropedia (investigate unofficial API or web scraping)"

- **Before**: "PyPDF2 or pdfplumber"
- **After**: "pdfplumber (text, tables, multi-column support), Tesseract for OCR"

- **Before**: "DeepL/Microsoft Translator APIs"
- **After**: "DeepL API with caching (500k chars/month free tier)"

**Section 9 - TerminologyCache Enhancement**:
- Added `source` field supports: `'IATE'`, `'IEC'`, `'DeepL'` (in addition to NAMUR/DIN/ASME)
- Purpose: Cache IATE dataset, IEC lookups, DeepL translations

**Step 2.1.2 - IATE Importer**:
```python
def import_iate_dataset(tbx_file_path: str):
    """Import IATE TBX dataset into TerminologyCache"""
    tree = etree.parse(tbx_file_path)
    for term_entry in tree.xpath("//termEntry"):
        # Extract German/English terms
        # Store in TerminologyCache with source='IATE'
```

**Step 1.2.2 - PDF Extraction**:
```python
import pdfplumber

def extract_text_from_pdf(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        text_parts = []
        for page in pdf.pages:
            text_parts.append(page.extract_text())
            # Extract tables separately
            for table in page.extract_tables():
                table_text = "\n".join(" | ".join(row) for row in table)
                text_parts.append(table_text)
        return "\n".join(text_parts)
```

**Step 2.2.1 - DeepL Caching**:
```python
def translate(self, text: str, source_lang: str, target_lang: str) -> str:
    # Check cache first
    cached = db.query(TerminologyCache).filter_by(
        term=text, language=target_lang, source='DeepL'
    ).first()
    if cached:
        return cached.definition

    # Call DeepL API, then cache result
    translation = deepl_client.translate_text(...)
    db.add(TerminologyCache(term=text, definition=translation, source='DeepL'))
```

### Impact
- **High**: Enables offline validation (IATE cached), improves PDF extraction quality, reduces API costs

---

## 🚨 Critical Update #3: Frontend Enhancements

### Issues Identified by Agent A5 (React Frontend Developer)
- **v2.1**: Progress indicators mentioned but no component definition
- **v2.1**: Material-UI default disabled text/borders fail WCAG 2.1 AA (contrast ratios too low)
- **v2.1**: 10k Neo4j nodes may exceed 2 sec load time without pagination

### Changes in v2.2

**Section 10 - Frontend Components**:
- Added **ProgressIndicator component**:
  ```javascript
  export default function ProgressIndicator({
    mode = 'determinate', // 'determinate' | 'indeterminate'
    value = 0, // 0-100
    label = '',
    variant = 'linear' // 'linear' | 'circular'
  })
  ```
  - Supports determinate (0-100%) and indeterminate (spinner) modes
  - Used for PDF/TBX parsing, graph population, exports

**Step 2.3.1 - WCAG-Compliant Theme**:
```javascript
const darkTheme = createTheme({
  palette: {
    text: {
      disabled: 'rgba(255, 255, 255, 0.5)', // FIX: 7.5:1 contrast (was 0.38 = 4.1:1)
    },
  },
  components: {
    MuiOutlinedInput: {
      styleOverrides: {
        notchedOutline: {
          borderColor: 'rgba(255, 255, 255, 0.3)', // FIX: 3.5:1 contrast (was 0.23)
        },
      },
    },
  },
});
```

**Step 2.3.4 - Backend Pagination**:
```python
@app.get("/graph-query")
async def query_graph(offset: int = 0, limit: int = 500, standard_filter: Optional[str] = None):
    query = "MATCH (t:Term)-[r:DEFINED_BY]->(s:Standard) RETURN t, r, s SKIP $offset LIMIT $limit"
    # Returns 500 nodes per query
```

**Step 2.3.4 - Frontend Infinite Scroll**:
```javascript
const [offset, setOffset] = useState(0);
useEffect(() => {
  fetch(`/graph-query?offset=${offset}&limit=500`)
    .then(r => r.json())
    .then(data => setGraphData(prev => ({
      nodes: [...prev.nodes, ...data.nodes],
      edges: [...prev.edges, ...data.edges]
    })));
}, [offset]);
```

### Impact
- **Medium**: Improves UX (progress feedback), ensures WCAG compliance (avoids legal risks), enables smooth graph rendering

---

## 🚨 Critical Update #4: DevOps & Deployment

### Issues Identified by Agent A7 (DevOps Engineer)
- **v2.1**: No Docker health checks (services can crash silently)
- **v2.1**: Passwords visible in `docker inspect` (security risk)
- **v2.1**: SQLite risk of corruption under concurrent writes

### Changes in v2.2

**Section 9 - Docker Health Checks**:
```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  neo4j:
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "${NEO4J_PASSWORD}", "RETURN 1"]
      interval: 30s
```

**Section 9 - Docker Secrets**:
```bash
# Generate secrets
echo "your_neo4j_password" | docker secret create neo4j_password -
echo "your_deepl_key" | docker secret create deepl_api_key -
```

```yaml
services:
  backend:
    secrets:
      - neo4j_password
      - deepl_api_key
    environment:
      - NEO4J_PASSWORD_FILE=/run/secrets/neo4j_password
      - DEEPL_API_KEY_FILE=/run/secrets/deepl_api_key
```

```python
# Backend reads secrets
def read_secret(secret_name: str) -> str:
    secret_file = os.getenv(f"{secret_name}_FILE")
    if secret_file and os.path.exists(secret_file):
        with open(secret_file) as f:
            return f.read().strip()
    return os.getenv(secret_name)
```

**Step 1.1.2 - SQLite WAL Mode**:
```python
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")  # Enable Write-Ahead Logging
    cursor.close()
```

### Impact
- **High**: Improves reliability (health checks catch failures), enhances security (secrets not exposed), prevents corruption

---

## 🚨 Critical Update #5: Testing Strategy Refinement

### Issues Identified by Agent A4 (Unit Testing Engineer)
- **v2.1**: 80% mutation testing target too ambitious for first implementation
- **v2.1**: E2E tests deferred to Phase 4 too risky (integration issues caught late)
- **v2.1**: Risk of mock drift between backend (A1) and frontend (A5)

### Changes in v2.2

**Section 13 - Mutation Testing**:
- **Before**: "≥80% mutation score"
- **After**: "≥70% mutation score for MVP, document acceptable surviving mutants (logging, error messages), target 80% in post-MVP Phase 5"

**Phase 2 - E2E Smoke Tests**:
- Added **Step 2.1.2 - E2E Smoke Test** (run in Phase 2, not Phase 4):
  ```javascript
  describe('Smoke Test: Upload Workflow', () => {
    it('uploads internal PDF and displays extracted terms', () => {
      cy.visit('http://localhost:3000');
      cy.get('input[type="file"]').selectFile('fixtures/sample_de.pdf');
      cy.get('button').contains('Upload').click();
      cy.get('.progress-indicator', { timeout: 60000 }).should('not.exist');
      cy.get('.terms-list').should('contain', 'Ventil');
    });
  });
  ```

**Section 13 - Contract Testing**:
- Added **Pact** for API contract validation:
  ```javascript
  await provider.addInteraction({
    uponReceiving: 'a request for term validation',
    withRequest: { method: 'POST', path: '/validate-term', body: {...} },
    willRespondWith: { status: 200, body: {...} }
  });
  ```
- Prevents mock drift: A5 (frontend) and A1 (backend) contracts must match

### Impact
- **Medium**: Realistic testing targets (70% achievable), early integration issue detection (smoke tests in Phase 2), API contract safety

---

## 🚨 Critical Update #6: NLP Characterization Testing

### Issues Identified by Agent A2 (NLP Specialist)
- **v2.1**: "Write tests FIRST" impossible for NLP (can't predict extraction results before implementation)
- **v2.1**: No dataset to measure 80% extraction accuracy claim

### Changes in v2.2

**Pre-Phase (Week 0) - Ground Truth Corpus**:
- A2 creates **NLP ground truth corpus**:
  - Collect 50 German + 50 English sample documents (NAMUR/DIN/ASME excerpts)
  - Manually annotate 500 term-definition pairs
  - Store in `tests/fixtures/nlp_ground_truth.json`

**Step 1.3.1 - Characterization Testing**:
- **Before**: "Tests FIRST: Unit tests for extraction rules"
- **After**: "Characterization Tests: A2 manually extracts terms from 10 sample PDFs using spaCy interactively, records ground truth, **THEN** writes tests against ground truth, **THEN** implements automated extractor"

**Test Implementation**:
```python
def test_extraction_meets_f1_threshold(ground_truth):
    extractor = NLPExtractor()
    total_tp = total_fp = total_fn = 0
    for sample in ground_truth['samples']:
        extracted = extractor.extract(f"tests/fixtures/{sample['document']}")
        expected = set(t['term'] for t in sample['terms'])
        tp = len(set(extracted) & expected)
        fp = len(set(extracted) - expected)
        fn = len(expected - set(extracted))
        total_tp += tp; total_fp += fp; total_fn += fn

    precision = total_tp / (total_tp + total_fp)
    recall = total_tp / (total_tp + total_fn)
    f1 = 2 * (precision * recall) / (precision + recall)
    assert f1 >= 0.75, f"F1 score {f1:.2f} below threshold 0.75"
```

**Section 13 - TDD Exception**:
- Added note: "**Exception**: NLP extraction uses **characterization testing** (manual ground truth creation first, then tests)"

### Impact
- **High**: Realistic NLP testing approach, measurable accuracy targets, prevents false precision claims

---

## 🚨 Critical Update #7: Timeline Extension

### Issues Identified by Agent A8 (Project Coordinator)
- **v2.1**: 10 weeks insufficient for all features + TDD + infrastructure
- **Analysis**: Ground truth corpus creation, backup setup, security hardening need dedicated time

### Changes in v2.2

**Section 12 - Development Phases**:
- **Before**: 10 weeks (Phase 1: 2 + Phase 2: 3.5 + Phase 3: 2 + Phase 4: 2.5)
- **After**: 12 weeks (Pre-Phase: 0.5 + Phase 1: 2 + Phase 2: 4 + Phase 3: 2.5 + Phase 4: 3)

**Rationale**:
- **Pre-Phase** (+0.5 weeks): Ground truth corpus creation, Neo4j bootcamp, IATE dataset download
- **Phase 2** (+0.5 weeks): Frontend complexity (ProgressIndicator, WCAG fixes, E2E smoke tests)
- **Phase 3** (+0.5 weeks): TBX ISO 30042 validation
- **Phase 4** (+0.5 weeks): Security hardening (Docker secrets), monitoring setup (Sentry, structured logging)

### Impact
- **High**: Realistic timeline, prevents rushed implementation, ensures quality

---

## 🚨 Critical Update #8: Pre-Phase Checklist

### Issues Identified by Agent A8 (Project Coordinator)
- **v2.1**: No clear checklist for Week 0 setup tasks
- **Risk**: Agents start Phase 1 without prerequisites (Neo4j knowledge, IATE dataset, backup scripts)

### Changes in v2.2

**Section 23 - Pre-Phase 1 Checklist (Week 0)**:
- [ ] **A2**: Create ground truth NLP corpus (500 term-definition pairs from 50 German + 50 English NAMUR/DIN/ASME excerpts) → `tests/fixtures/nlp_ground_truth.json`
- [ ] **A3**: Complete Neo4j bootcamp (GraphAcademy "Neo4j Fundamentals" course, ~8 hours)
- [ ] **A6**: Download IATE TBX/CSV dataset from https://iate.europa.eu/download-iate
- [ ] **A7**: Setup local Neo4j Community Edition for development (Docker)
- [ ] **A7**: Install all dependencies (pdfplumber, neo4j-driver, deepl, lxml, pytesseract, pdf2image)
- [ ] **A7**: Create `scripts/backup_sqlite.sh` and test restore procedure
- [ ] **A7**: Generate Docker secrets for NEO4J_PASSWORD, DEEPL_API_KEY
- [ ] **A7**: Create `.env.example` with all environment variables documented
- [ ] **A8**: Review and approve updated PRT v2.2 (this document)
- [ ] **A8**: Review and approve IMPLEMENTATION-STRATEGY v1.1 (12-week timeline)

### Impact
- **Medium**: Clear prerequisites, prevents blocked agents, ensures readiness for Phase 1

---

## Additional Minor Updates

### Section 16 - Agent IDs
- Added agent IDs (A1-A8) for easier reference in prompts and coordination hooks

### Section 18 - All Implementation Steps
- Updated Step 1.1.2: Added SyncLog, UploadedDocument to database models
- Updated Step 1.2.2: Changed from PyPDF2 to pdfplumber
- Updated Step 1.3.1: Changed from pure TDD to characterization testing
- Updated Step 1.3.2: Added retry logic with SyncLog tracking
- Updated Step 2.1.2: Changed from IATE API to IATE cached dataset importer
- Updated Step 2.2.1: Added DeepL caching logic
- Updated Step 2.3.1: Added WCAG-compliant theme overrides
- Updated Step 2.3.4: Added pagination to /graph-query endpoint
- Updated Phase 2: Added E2E smoke test task
- Updated Step 4.3.2: Added Docker health checks and secrets

### Section 19 - Acceptance Criteria
- Added: "Sync retry logic works (SyncLog tracks failures)"
- Added: "Automated backups (SQLite daily, Neo4j weekly)"
- Added: "Docker deployment with health checks"
- Added: "Docker secrets for credentials"
- Added: "Contract tests (Pact) for API mocks"
- Added: "Mutation testing ≥70%"

### Section 22 - Risk Assessment
- Added: "DeepL API Limits: Caching reduces calls (500k chars/month free tier sufficient)"
- Updated: "API Downtime: ... IATE cached dataset, DeepL caching"

### Section 24 - Glossary
- Added: **Characterization Testing** - Manual exploration → ground truth recording → test creation → implementation (for NLP)
- Added: **F1 Score** - Harmonic mean of precision and recall (NLP accuracy metric)
- Added: **WAL Mode** - Write-Ahead Logging (SQLite concurrency/corruption prevention)
- Added: **Pact** - Contract testing framework (prevent mock drift)

### Section 25 - References
- Added: pdfplumber (https://github.com/jsvine/pdfplumber)
- Added: Pact (https://docs.pact.io/)
- Updated: Neo4j (added GraphAcademy link)

---

## Migration Guide: Implementing with v2.2

### For Developers Starting Implementation

1. **Complete Pre-Phase Checklist (Section 23)**: Week 0 setup is mandatory
2. **Review Expert Review Fixes (EXPERT-REVIEW-FIXES.md)**: Understand all 7 critical updates
3. **Follow IMPLEMENTATION-STRATEGY v1.1**: 12-week timeline with concurrent execution
4. **Use Characterization Testing for NLP**: Don't force TDD on unpredictable algorithms
5. **Setup Infrastructure First**: Backups, Docker secrets, health checks before coding

### Key Behavioral Changes from v2.1

| Aspect | v2.1 Behavior | v2.2 Behavior |
|--------|---------------|---------------|
| **Timeline** | 10 weeks | 12 weeks (Pre-Phase + 4 phases) |
| **PDF Parsing** | PyPDF2 or pdfplumber | pdfplumber only (tables/multi-column) |
| **IATE Integration** | API (incorrect) | Cached dataset (quarterly imports) |
| **Sync Failures** | No recovery | SyncLog table + retry logic (3x, exponential backoff) |
| **Docker** | Basic setup | Health checks + Docker secrets |
| **Mutation Testing** | 80% target | 70% for MVP |
| **NLP Testing** | Pure TDD (impossible) | Characterization testing (ground truth first) |
| **E2E Tests** | Phase 4 only | Smoke tests in Phase 2, full E2E in Phase 4 |
| **Contract Testing** | Not specified | Pact for API mock validation |

---

## Validation Checklist

Before starting Phase 1 implementation, ensure:
- [ ] Pre-Phase Checklist (Section 23) completed (all 10 items)
- [ ] You understand database architecture (SQLite source of truth, Neo4j read-only visualization)
- [ ] You know sync retry logic (SyncLog table, 3 retries, exponential backoff)
- [ ] You have IATE cached dataset downloaded and know import procedure
- [ ] You understand characterization testing for NLP (ground truth first, then tests)
- [ ] You know Docker secrets pattern (NEO4J_PASSWORD_FILE, DEEPL_API_KEY_FILE)
- [ ] You can implement SQLite WAL mode (PRAGMA journal_mode=WAL)
- [ ] You understand WCAG fixes (disabled text ≥7.5:1, borders ≥3.5:1 contrast)
- [ ] You know pagination pattern for Neo4j graph (500 nodes/query, infinite scroll)
- [ ] You can write Pact contract tests (prevent mock drift)

---

## Questions or Issues?

If you encounter ambiguities not resolved by v2.2, please:
1. Check **EXPERT-REVIEW-FIXES.md** for detailed implementation guidance
2. Check **IMPLEMENTATION-STRATEGY v1.1** for 12-week timeline and phase breakdowns
3. Check **CLAUDE.md** (global configuration) for overriding rules
4. Refer to Claude-Flow docs: https://github.com/ruvnet/claude-flow
5. Consult Section 25 (References) for tool-specific documentation
6. Document the issue for potential v2.3 update

---

**End of Changelog (v2.1 → v2.2)**
