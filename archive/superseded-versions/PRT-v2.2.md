# Product Requirements Template (PRT)
**Project Name**: Glossary Extraction & Validation App
**Version**: 2.2
**Objective**:
Develop a guided software tool that extracts, validates, compares, and translates glossary entries from internal technical documents (German and English), resulting in a clean bilingual glossary aligned with international standards and "gold standard" sources (NAMUR, DIN, ASME). A Neo4j graph database visualizes term-standard relationships to enhance validation and analysis.

## 1. Purpose
The application supports engineering and documentation teams in extracting, validating, and harmonizing bilingual terminology from internal technical standards. It addresses misleading translations, inconsistent terminology, and non-standard language by guiding users through a structured workflow. The resulting glossary aligns with international references (IEC Electropedia, IEV-Wörterbuch, IATE) and authoritative "gold standards" (NAMUR, DIN, ASME), with Neo4j enabling visualization of term-standard relationships for compliance and analysis.

## 2. Scope
**Included**:
- Upload and process German and English documents independently
- Import NAMUR, DIN, ASME, and other standards (PDF/TBX files) as gold standards via GUI
- Extract glossary entries using NLP or rule-based logic
- Validate entries manually and via external databases or gold standards
- Translate missing entries where only one language is available
- Compare and merge bilingual entries, prioritizing gold standards
- Visualize term-standard relationships in a Neo4j graph
- Export final glossary to standard formats (CSV, Excel, JSON, XML)
**Not Included (Initial Version)**:
- Real-time collaboration or cloud sync
- Automatic glossary generation without user validation
- Full integration with enterprise systems (e.g., SharePoint)

## 3. Functional Requirements
**Document Ingestion Module**
- Upload German and/or English PDF documents (support text-based and scanned PDFs via OCR; handle tables/multi-columns)
- Import NAMUR, DIN, ASME, and other standards (PDF/TBX) as gold standards via GUI
- Extract raw text using PDF parsing libraries or TBX parsers
**Glossary Extraction Module**
- Detect term-definition pairs using NLP (e.g., for unstructured text) or rule-based logic (e.g., for structured sections like headings)
- Store entries in separate German and English source tables and Neo4j graph
**Validation Module**
- Manual review of glossary entries (side-by-side comparison with external matches or NAMUR/DIN/ASME gold standards)
- Lookup and validation against IEC Electropedia, IEV-Wörterbuch, IATE cached dataset, cached gold standards, and Neo4j relationships
- Mark entries as "validated" before matching
**Translation Module**
- Identify entries that exist in only one language
- Translate missing terms using DeepL (with caching) or Microsoft Translator (with fallback to manual input or gold standards)
- Allow manual review and correction of translations
**Glossary Comparison Module**
- Match validated German and English entries, prioritizing NAMUR/DIN/ASME gold standards and Neo4j relationships
- Flag inconsistent or misleading translations
- Suggest corrections or allow manual resolution
**Glossary Builder Module**
- Merge validated entries into a bilingual glossary, favoring gold standard terms
- Export to CSV, Excel, JSON, or XML (TBX-compliant)
- Optionally store locally or in internal repositories
**Graph Visualization Module**
- Populate Neo4j with Term and Standard nodes, linked by relationships (e.g., DEFINED_BY, SYNONYM)
- Display interactive graph in GUI (nodes: terms/standards; edges: relationships)
- Support queries like "Show terms linked to ASME"
**Error Handling & Logging**
- Handle failed uploads, parsing errors, API failures, and Neo4j connectivity gracefully (e.g., offline mocks)
- Log user actions, system events, and graph updates for audit and debugging

## 4. Non-Functional Requirements
- **Usability**: Intuitive UI with a dark theme (default) for technical users, with minimal training (e.g., complete workflow in <10 min after 30-min tutorial). Support customizable dialog background colors via a Settings interface, company logo upload (PNG), WCAG 2.1 AA compliance (contrast ratios ≥4.5:1), and interactive graph visualization. Include progress indicators for long tasks (e.g., PDF/TBX parsing, graph population, exports).
- **Performance**: Process 100-page PDFs in <60 sec; handle up to 1,000 glossary entries; Neo4j queries return in <2 sec for 10,000 nodes.
- **Reliability**: Ensure glossary and graph integrity during edits and exports
- **Extensibility**: Modular design for future enhancements
- **Offline Capability**: Operate without mandatory cloud dependencies (use local mocks, TerminologyCache, Neo4j caching)
- **Security**: Local file encryption (AES-256), access control (OAuth/role-based), secure Neo4j access
- **Compliance**: GDPR or internal data handling policies

## 5. Advanced Features
- AI-driven term suggestions (e.g., auto-complete from external DBs or NAMUR/DIN/ASME)
- Batch processing for multiple documents
- User feedback loop (flag incorrect entries, rate translations)
- Domain-specific profiles (filter/prioritize terms by engineering domains)
- Graph-based analytics (e.g., "Find terms shared by DIN and ASME")

## 6. User Roles
- **Editor**: Upload documents, import gold standards, extract/edit glossary entries, manage graph
- **Reviewer**: Validate entries, comment on translations, view graph
- **Viewer**: View and export final glossary, view graph

**Permissions Matrix**:

| Role     | Upload/Extract/Import Standards | Edit Entries | Validate/Comment | View/Export/Graph |
|----------|--------------------------------|--------------|------------------|-------------------|
| Editor   | Yes                            | Yes          | Yes              | Yes               |
| Reviewer | No                             | No           | Yes              | Yes               |
| Viewer   | No                             | No           | No               | Yes               |

## 7. Technology Stack
- **Frontend**: React (Material-UI for dark theme; react-dropzone for PDF/TBX uploads; react-image for logo PNG; vis.js/Reagraph for graph visualization)
- **Backend**: FastAPI (Python 3.10+)
- **Data**: SQLite or H2 (glossary storage, TerminologyCache; CSV/Excel for exports); Neo4j Community Edition (term-standard relationships)
- **PDF Parsing**: pdfplumber (text, tables, multi-column), Tesseract for OCR (scanned)
- **TBX Parsing**: lxml (for NAMUR/DIN/ASME TBX imports)
- **NLP**: spaCy (term extraction, fuzzy matching)
- **Translation**: DeepL API with caching (500k chars/month free tier)
- **Validation**: IATE cached dataset (quarterly TBX/CSV imports from https://iate.europa.eu/download-iate), IEC Electropedia (investigate unofficial API or web scraping), NAMUR/DIN/ASME gold standards
- **String Similarity**: python-Levenshtein, jellyfish
- **Graph DB**: Neo4j (neo4j-driver for queries, Cypher for graph operations)
- **Testing**: pytest (backend), Jest (frontend), Cypress (E2E), axe-core (accessibility), pact-python (contract testing)
- **Dependencies**: numpy, exposed (if H2), styled-components (UI customization), neo4j-driver
- **AI Integration**: Claude AI (via API/desktop app) for code generation; MCP for file/DB access; Cursor, Aider, Zed, or VS Code with Claude extension
- **Browser Integration**: Microsoft Edge Web MCP extension for web-based automation (e.g., terminology lookups)

## 8. Workflow Summary

### Workflow A: Internal Document Processing
1. Upload German/English PDF → Extract terms → Store as `source='internal'` in SQLite and Neo4j
2. Validate against gold standards (cached in TerminologyCache) and Neo4j relationships
3. Translate missing entries
4. Match and compare validated entries

### Workflow B: Gold Standard Import
1. User opens **Settings → Import Gold Standards**
2. Upload NAMUR/DIN/ASME file (PDF or TBX)
3. Select standard type from dropdown (NAMUR, DIN, ASME)
4. System processes:
   - **If PDF**: Extract terms → Store in TerminologyCache + Create Neo4j Standard node
   - **If TBX**: Parse directly → Store in TerminologyCache + Create Neo4j Standard node
   - Mark all entries with `source='NAMUR'/'DIN'/'ASME'`
5. Gold standard terms are **read-only**, used for validation only

### Workflow C: Complete Glossary Pipeline
- Extract & validate internal documents (Workflow A)
- Import gold standards (Workflow B)
- Match bilingual entries, prioritizing gold standards and Neo4j relationships
- Visualize term-standard relationships in Neo4j graph
- Review inconsistencies and finalize glossary
- Export or store glossary

**Text-Based Workflow Diagram**:
```
[Start]
  |
  +--> [Workflow A: Upload Internal PDF (de/en)] --> [Parse Text (pdfplumber/OCR)]
  |         |
  |         v
  |    [Extract Terms (spaCy/rules)] --> [Store in SQLite (source='internal') & Neo4j Term nodes]
  |
  +--> [Workflow B: Import Gold Standard (NAMUR/DIN/ASME)]
            |
            +--> [If PDF] --> [Parse & Extract] --> [Store in TerminologyCache & Neo4j Standard node]
            |
            +--> [If TBX] --> [Parse TBX] --> [Store in TerminologyCache & Neo4j Standard node]
  |
  v
[Manual Validate (side-by-side w/ TerminologyCache/Neo4j/IATE)] --> [Translate Missing (DeepL)]
  |
  v
[Compare/Merge (flag inconsistencies, prioritize gold standards)] --> [Visualize Graph (Neo4j)]
  |
  v
[Build Glossary] --> [Export (TBX/CSV/Excel/JSON)]
  |
  v
[End: Audit Log]
```

## 9. Data Model Overview

### Database Architecture
1. **SQLite/H2** = Source of truth for glossary data (GlossaryEntry, GlossaryMatch, GlossaryVersion, TerminologyCache, SyncLog, UploadedDocument)
2. **Neo4j** = Derived visualization layer (Term nodes synced from GlossaryEntry; Standard nodes from gold standard imports)

### Sync Strategy
- **SQLite → Neo4j (One-Way Sync)**:
  - When GlossaryEntry created → CREATE Term node in Neo4j (via API trigger)
  - When GlossaryEntry updated → MERGE Term node properties
  - When gold standard imported → CREATE Standard node + DEFINED_BY relationship
  - Neo4j is **read-only from UI perspective** (users query/visualize, not edit directly)
  - Sync jobs run: On-demand (after extraction/validation) or scheduled (hourly batch)

### Neo4j Setup
- **Deployment**: Docker container `neo4j:5.x-community`
- **Connection**: `bolt://localhost:7687`
- **Credentials**: Environment variables (`NEO4J_USER`, `NEO4J_PASSWORD`)
- **Initialization**: Auto-create constraints (UNIQUE on Term.id, Standard.id) on first run
- **Backup**: Weekly exports via `neo4j-admin dump`, daily SQLite backups (30-day retention)

### SQLite Entities
**GlossaryEntry**
- Attributes: `id`, `term`, `definition`, `language` (CHECK: 'de' or 'en'), `source_document`, `creation_date`, `updated_at`, `domain_tags`, `validation_status` (CHECK: 'pending' or 'validated'), `source` (CHECK: 'internal', 'NAMUR', 'DIN', 'ASME'), `sync_status` (CHECK: 'pending_sync', 'synced', 'sync_failed')
- Constraints: UNIQUE(term, language, source), NOT NULL on term, definition, language, validation_status, source
- Indexes: idx_glossary_entry_term_lang (term, language), idx_glossary_entry_source (source), idx_glossary_entry_validation (validation_status)

**GlossaryMatch**
- Attributes: `de_entry_id`, `en_entry_id`, `match_quality` (score), `inconsistency_flags`, `source_priority` (1.5 for NAMUR/DIN/ASME)
- Indexes: idx_glossary_match_quality (match_quality)

**GlossaryVersion**
- Attributes: `version_id`, `timestamp`, `changes_summary`, `user_id`

**TerminologyCache**
- Attributes: `term`, `definition`, `language`, `source` (CHECK: 'NAMUR', 'DIN', 'ASME', 'IATE', 'IEC', 'DeepL'), `last_updated`
- Indexes: idx_terminology_cache_term_source (term, source)

**SyncLog** (NEW in v2.2)
- Attributes: `id`, `entry_id` (FK to GlossaryEntry), `sync_status` (CHECK: 'pending', 'success', 'failed'), `retry_count` (default 0), `last_attempt` (timestamp), `error_message`, `created_at`
- Purpose: Track SQLite↔Neo4j sync failures with retry logic (max 3 retries, exponential backoff)
- Indexes: idx_synclog_status (sync_status), idx_synclog_entry (entry_id)

**UploadedDocument** (NEW in v2.2)
- Attributes: `id`, `filename`, `file_size`, `upload_date`, `file_type` (PDF/TBX), `language`, `source_type` ('internal', 'NAMUR', 'DIN', 'ASME'), `processing_status` (CHECK: 'pending', 'processing', 'completed', 'failed'), `error_log`
- Purpose: Track uploaded files for audit and retry
- Indexes: idx_uploaded_doc_status (processing_status), idx_uploaded_doc_date (upload_date)

### Neo4j Graph Model
**Nodes**:
- **Term**: `id`, `term`, `definition`, `language`, `validation_status`, `domain_tags`
- **Standard**: `id`, `name` (e.g., 'ASME Y14.5'), `version`, `file_source`
- **Domain**: `id`, `name` (e.g., 'Mechanical Engineering')

**Relationships**:
- **DEFINED_BY**: `(Term)-[:DEFINED_BY]->(Standard)` - Links term to authoritative source
- **SYNONYM**: `(Term)-[:SYNONYM]->(Term)` - Connects equivalent terms across languages
- **DOMAIN**: `(Term)-[:DOMAIN]->(Domain)` - Categorizes terms by engineering domain
- **TRANSLATED_FROM**: `(Term)-[:TRANSLATED_FROM {method: 'DeepL'}]->(Term)` - Tracks translation origin

**Sync Details**:
- Term nodes sync with GlossaryEntry via `id` (1:1 mapping)
- Standard nodes created from uploaded NAMUR/DIN/ASME files (no SQLite equivalent)
- Sync trigger: After GlossaryEntry INSERT/UPDATE, call `sync_to_neo4j_with_retry(entry_id)` with retry logic (SyncLog tracking)

**Neo4j Indexes** (NEW in v2.2):
```cypher
CREATE INDEX term_name_idx IF NOT EXISTS FOR (t:Term) ON (t.term);
CREATE INDEX term_language_idx IF NOT EXISTS FOR (t:Term) ON (t.language);
CREATE INDEX standard_name_idx IF NOT EXISTS FOR (s:Standard) ON (s.name);
CREATE INDEX domain_name_idx IF NOT EXISTS FOR (d:Domain) ON (d.name);
CREATE CONSTRAINT term_id_unique IF NOT EXISTS FOR (t:Term) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT standard_id_unique IF NOT EXISTS FOR (s:Standard) REQUIRE s.id IS UNIQUE;
```

**Relationships**:
- One GlossaryEntry can link to another via GlossaryMatch
- Multiple GlossaryEntry records belong to one GlossaryVersion
- Term nodes can have multiple DEFINED_BY, SYNONYM, DOMAIN relationships

**Storage Limits**: Max 10,000 glossary entries (SQLite); retain 10 versions; cache 50,000 gold standard terms (SQLite); Neo4j supports 10,000 Term nodes, 100 Standard nodes

**Backup Strategy** (NEW in v2.2):
- Daily SQLite backups via cron job (`scripts/backup_sqlite.sh`) with 30-day retention
- Weekly Neo4j dumps via `neo4j-admin dump`
- Optional: S3 upload for offsite backup

## 10. System Architecture Overview
The app is a modular, extensible system guiding users through glossary extraction, validation, translation, merging, and visualization of term-standard relationships. It uses FastAPI, React, SQLite/H2, and Neo4j, ensuring clarity, maintainability, and scalability.

**Frontend Layer**
- **Technology**: React
- **Features**:
  - File upload (react-dropzone for PDFs/TBX)
  - Gold standard import via Settings UI (NAMUR/DIN/ASME)
  - Glossary review/editing with dark theme (Material-UI)
  - Validation/translation controls (side-by-side with gold standards)
  - Graph visualization (vis.js/Reagraph for Neo4j)
  - Export options (CSV, Excel, JSON, TBX)
  - Logo upload (PNG, header/settings)
  - Settings for dialog colors and standards import
  - **ProgressIndicator** component (NEW in v2.2): Reusable progress bar with determinate/indeterminate modes for PDF/TBX parsing, graph population, exports
  - WCAG 2.1 AA compliance

**Backend Layer**
- **Technology**: FastAPI
- **Modules**:
  - PDF Parser: Extracts text from documents and NAMUR/DIN/ASME PDFs (pdfplumber)
  - TBX Parser: Parses NAMUR/DIN/ASME TBX files
  - Glossary Extractor: Identifies term-definition pairs (NLP/rules)
  - Validator: Checks terms against IEC, IATE cached dataset, cached gold standards, Neo4j
  - Translator: Uses DeepL API with caching for missing entries
  - Glossary Matcher: Links de/en terms, prioritizes gold standards/graph
  - Glossary Builder: Merges entries into bilingual glossary
  - Graph Manager: Populates/queries Neo4j for term-standard relationships (with retry logic)

**Data Layer**
- **Technology**: SQLite or H2; Neo4j
- **Entities**: GlossaryEntry, GlossaryMatch, GlossaryVersion, TerminologyCache, SyncLog, UploadedDocument (SQLite); Term, Standard nodes (Neo4j)
- **Purpose**: Stores glossary data, versions, cached gold standards, sync logs, and graph relationships

**Integration Layer**
- **Services**: IEC Electropedia, IEV-Wörterbuch, IATE cached dataset, DeepL API, Microsoft Translator, NAMUR/DIN/ASME (PDF/TBX), Neo4j
- **Features**: Handle rate limits with offline caching (TerminologyCache, Neo4j)

**Data Flow**
- Upload documents/standards → Parse terms → Store in SQLite/Neo4j
- Validate against gold standards/Neo4j → Translate missing terms
- Match bilingual terms, prioritize gold standards/graph → Visualize relationships
- Merge and export glossary

**Design Principles**
- Modularity: Independent, reusable modules
- Transparency: Traceable entries and relationships (metadata, versions)
- User Control: Manual review for validation/translation
- Scalability: Supports enhancements (e.g., clustering, domains)

**Deployment**
- Hybrid (local default, cloud optional)
- Requirements: Python 3.10+, Node.js, Neo4j Community Edition
- Updates: Manual or via package manager

## 11. Development Guidelines
- **Single Responsibility**: Each module does one task well
- **Loose Coupling**: Minimize inter-module dependencies
- **Clear Interfaces**: Well-defined APIs/functions
- **Test Isolation**: Mock dependencies for unit tests
- **Code Reusability**: Utility modules for shared logic
- **Documentation**: Docstrings and usage examples
- **AI-Assisted Coding**: Use Claude for modular code, ISO/Neo4j alignment; review manually
- **Tool Integration**: MCP for Claude to access files (PDF/TBX), databases (SQLite/Neo4j), APIs

## 12. Development Phases
- **Pre-Phase**: Ground truth NLP corpus creation, Neo4j bootcamp (0.5 weeks)
- **Phase 1**: Document Ingestion & Extraction (2 weeks)
- **Phase 2**: Validation, Translation & Graph Setup (4 weeks)
- **Phase 3**: Comparison & Builder (2.5 weeks)
- **Phase 4**: Testing & Polish (3 weeks)
- **Total Timeline**: 12 weeks

## 13. Unit Testing & CI/CD Integration

### Test-Driven Development (TDD) Approach
This project follows **Test-Driven Development (TDD, London School)** methodology:
- **Write tests FIRST** before implementation code for all features
- **Red-Green-Refactor** cycle: Write failing test → Implement feature → Refactor
- Tests are integrated into **every phase** (Phases 1-3), not just Phase 4
- Phase 4 focuses on **comprehensive test expansion**, E2E testing, and mutation testing
- **Exception**: NLP extraction uses **characterization testing** (manual ground truth creation first, then tests)

### Testing Strategy Per Phase
**Phase 1-3 (Development)**:
- Each step includes: "**Tests FIRST**: Write [test type]" → "**Then**: Implement [feature]"
- Unit tests written alongside feature code (not after)
- Integration tests after module completion

**Phase 4 (Testing & Polish)**:
- Expand test coverage to ≥85-90%
- Add E2E tests (Cypress), accessibility tests (axe-core), mutation tests (mutmut)
- Performance testing and optimization

### Coverage Requirements
- **≥90%** for critical modules (glossary/graph integrity, data sync)
- **≥80%** for core logic (NLP extraction, validation, translation)
- **≥70%** for UI components (React)

### CI/CD Gates
- Block merges if coverage < threshold
- Run tests on every commit/pull request
- **Test Types**: Unit (pytest), integration, E2E (Cypress), accessibility (axe-core), mutation (mutmut), contract (pact-python)
- **Goals**: Ensure correctness, catch regressions, support CI/CD

### Mutation Testing (UPDATED in v2.2)
- **Target**: ≥70% mutation score (mutmut, Stryker) for MVP
- Document acceptable surviving mutants (logging, error messages)
- Target 80% in post-MVP Phase 5 after user feedback

## 14. Unit Testing Strategy
- TBX Compliance: Validate exports against ISO 30042
- Accessibility: WCAG 2.1 AA via axe-core
- Gold Standard: Verify NAMUR/DIN/ASME parsing/validation
- Graph: Test Neo4j node/relationship creation and queries
- Data Sync: Test SQLite ↔ Neo4j synchronization accuracy with retry logic
- Contract Testing: pact-python for frontend/backend API contract validation

## 15. Future Enhancements
- User feedback loop (flag/rate entries)
- Domain-specific profiles
- Glossary consistency checker
- Plugin/API mode (e.g., SharePoint, COMOS)
- Graph analytics (e.g., cross-standard term analysis)
- Additional languages
- Change impact analysis
- Governance workflow (draft-review-approve)
- Full theme editor
- Browser automation via MCP
- AI-powered term clustering (Chroma/Vectara)
- Voice-controlled UI
- Glossary diff viewer

## 16. Development Team Roles & Agent Mapping

This project uses **agentic development** with Claude-Flow coordination. Each human role maps to Claude-Flow agent types for concurrent execution.

| PRT Role | Claude-Flow Agent Type(s) | Primary Responsibilities | Tools/Technologies |
|----------|---------------------------|--------------------------|-------------------|
| **Python Developer** | `backend-dev`, `coder` | Core FastAPI logic, Neo4j integration, SQLAlchemy models | FastAPI, SQLAlchemy, neo4j-driver, Python 3.10+ |
| **NLP Specialist** | `researcher`, `ml-developer` | Term extraction algorithms, spaCy pipelines, fuzzy matching | spaCy, NLTK, regex, NLP models |
| **Database Engineer** | `code-analyzer`, `system-architect` | SQLite/H2 schemas, Neo4j graph design, Cypher queries, data sync | SQLite, Neo4j, Cypher, database migrations |
| **Unit Testing Engineer** | `tester`, `tdd-london-swarm` | TDD implementation, pytest suites, mutation testing, mocking | pytest, Jest, mutmut, unittest.mock |
| **React Frontend Developer** | `coder` (frontend focus) | React UI, Material-UI theming, graph visualization, WCAG compliance | React, Material-UI, vis.js/Reagraph, axe-core |
| **Integration Engineer** | `api-docs`, `backend-dev` | External API integration (DeepL, IATE, IEC), error handling | requests, API clients, REST/TBX |
| **DevOps Engineer** | `cicd-engineer`, `devops` | Docker setup, CI/CD pipelines, Neo4j deployment, monitoring | Docker, GitHub Actions, Neo4j, Sentry |
| **Project Coordinator** | `task-orchestrator`, `sparc-coord` | Workflow orchestration, milestone tracking, agent handoffs | Claude-Flow, MCP, project management |

### Agent Execution Notes
- Use **Claude Code's Task tool** to spawn agents concurrently (not MCP tools)
- MCP tools (`swarm_init`, `agent_spawn`) are for coordination topology only
- Each agent runs hooks for coordination (pre-task, post-edit, post-task)
- All agents follow TDD methodology (tests first, then code)

## 17. Agentic Development Strategy

### Core Principles
- **Task Decomposition**: Break features into 1-2 day tasks (~1k-2k tokens for Claude)
- **Agent Handoff Protocols**: Clear task boundaries, output contracts between agents
- **Testing Contracts**: Every agent writes tests first (TDD), ensuring integration safety
- **Agent Registry**: Track which agent handles which module/feature
- **Traceability**: Log all agent actions for audit and debugging

### Concurrent Execution Pattern (CRITICAL)
**GOLDEN RULE**: All related operations MUST be executed in a **single message** for parallel coordination.

**Mandatory Execution Pattern**:
```javascript
// ✅ CORRECT: Single message with all concurrent operations
[Message 1 - Phase 1 Initialization]:
  // Spawn ALL agents for Phase 1 in parallel
  Task("Python Developer", "Initialize FastAPI with /health endpoint, SQLAlchemy models, neo4j-driver. Follow TDD: write pytest first (Section 18 Steps 1.1.1-1.1.2)", "backend-dev")
  Task("Database Engineer", "Setup SQLite schemas (GlossaryEntry, TerminologyCache, SyncLog, UploadedDocument) and Neo4j constraints (Term, Standard). Write migration tests first.", "code-analyzer")
  Task("Unit Testing Engineer", "Create pytest framework, setup mocks for external APIs (IATE, DeepL), configure coverage reporting.", "tester")

  // Batch ALL todos in ONE call
  TodoWrite { todos: [
    {content: "Initialize FastAPI skeleton", status: "in_progress", activeForm: "Initializing FastAPI skeleton"},
    {content: "Setup SQLite database schemas", status: "in_progress", activeForm: "Setting up SQLite database schemas"},
    {content: "Configure Neo4j connection", status: "in_progress", activeForm: "Configuring Neo4j connection"},
    {content: "Create pytest framework", status: "in_progress", activeForm: "Creating pytest framework"},
    {content: "Write API endpoint tests", status: "pending", activeForm: "Writing API endpoint tests"},
    {content: "Implement file upload endpoints", status: "pending", activeForm: "Implementing file upload endpoints"}
  ]}

  // Parallel file operations
  Bash "mkdir -p src/{backend,frontend,database,tests}"
  Write "src/backend/app.py"
  Write "src/database/models.py"
  Write "tests/test_app.py"

// ❌ WRONG: Multiple sequential messages
Message 1: Task("agent 1")
Message 2: Task("agent 2")  // BREAKS PARALLEL COORDINATION!
Message 3: TodoWrite { todos: [...] }
```

### Claude Integration
- **Code Generation**: Use Claude with prompts per Section 18 (1-2 day granular tasks)
- **MCP for File/DB Access**:
  - Filesystem: PDF/TBX/logo handling
  - SQLite: Glossary/cache queries
  - Neo4j: Graph queries via Cypher
  - Git: Version control
  - Fetch/Puppeteer: Fallback for terminology lookups
  - Others (e.g., Sentry, Chroma) for monitoring/enhancements

### Agent Coordination Hooks
Every agent spawned via Task tool MUST execute:

**Before Work**:
```bash
npx claude-flow@alpha hooks pre-task --description "[task description]"
npx claude-flow@alpha hooks session-restore --session-id "swarm-[phase-id]"
```

**During Work**:
```bash
npx claude-flow@alpha hooks post-edit --file "[file]" --memory-key "swarm/[agent]/[step]"
npx claude-flow@alpha hooks notify --message "[what was completed]"
```

**After Work**:
```bash
npx claude-flow@alpha hooks post-task --task-id "[task-id]"
npx claude-flow@alpha hooks session-end --export-metrics true
```

## 18. Implementation Plan

### Overview
- **Methodology**: Agile with TDD (Test-Driven Development, London School)
- **Granularity**: 1-2 day tasks (~1k-2k tokens for Claude prompts)
- **Total Timeline**: 12 weeks (includes Pre-Phase)
- **Execution**: Concurrent agent spawning per phase (Section 17)

### Pre-Phase: Setup (Week 0 - 0.5 weeks)
**Objectives**:
- ✅ Create ground truth NLP corpus (500 term-definition pairs)
- ✅ Database Engineer completes Neo4j bootcamp (GraphAcademy)
- ✅ Download IATE TBX/CSV dataset
- ✅ Setup local Neo4j Community Edition
- ✅ Install all dependencies (pdfplumber, neo4j-driver, deepl)
- ✅ Create backup scripts and test restore procedure
- ✅ Generate Docker secrets for credentials
- ✅ Review and approve PRT v2.2 and IMPLEMENTATION-STRATEGY v1.1

### Phase 1: Document Ingestion & Extraction (Weeks 1-2)

**Concurrent Agent Spawn (Message 1)**:
```javascript
Task("Python Developer", "Steps 1.1.1-1.1.2: TDD approach - write pytest first, then implement FastAPI skeleton with /health, SQLAlchemy models (including SyncLog, UploadedDocument), neo4j-driver", "backend-dev")
Task("Database Engineer", "Step 1.1.2: TDD - write schema tests, then setup SQLite (GlossaryEntry, TerminologyCache, SyncLog, UploadedDocument) with indexes and Neo4j (Term, Standard nodes with constraints)", "code-analyzer")
Task("Unit Testing Engineer", "Create pytest framework, setup mocks for Neo4j/APIs, configure coverage ≥80%, setup pact-python for contract testing", "tester")
```

**Step 1.1.1**: Initialize FastAPI repo (app.py, /health endpoint, neo4j-driver)
  - **Tests FIRST**: Write pytest for /health endpoint (status 200, response schema)
  - **Prompt**: "Create FastAPI app skeleton with /health endpoint, include neo4j-driver (Section 7)."
  - **Then**: Implement FastAPI app with endpoint

**Step 1.1.2**: Setup SQLite/H2 (GlossaryEntry, TerminologyCache, SyncLog, UploadedDocument) and Neo4j (Term, Standard nodes)
  - **Tests FIRST**: Unit tests for model creation, CRUD operations, Neo4j constraints, indexes
  - **Prompt**: "Implement SQLAlchemy models for GlossaryEntry/TerminologyCache/SyncLog/UploadedDocument with CHECK constraints and indexes. Setup Neo4j schema for Term/Standard nodes with UNIQUE constraints and indexes (Section 9)."
  - **Then**: Implement database models and Neo4j schema

**Concurrent Agent Spawn (Message 2)**:
```javascript
Task("Python Developer", "Steps 1.2.1-1.2.2: TDD - write endpoint tests, then implement /upload-document and /import-standard with progress indicators", "backend-dev")
Task("NLP Specialist", "Step 1.3.1: Characterization testing - manually extract terms from 10 sample PDFs, record ground truth, THEN write tests, THEN implement spaCy extractor (≥75% F1 score)", "researcher")
Task("Database Engineer", "Step 1.3.2: TDD - write sync tests with retry logic, then implement SQLite↔Neo4j sync trigger with SyncLog tracking", "code-analyzer")
```

**Step 1.2.1**: Add /upload-document, /import-standard endpoints (separate internal vs gold standards)
  - **Tests FIRST**: Integration test with mock PDF/TBX files, verify tagging logic
  - **Prompt**: "Add FastAPI endpoints: `/upload-document` (for internal PDFs, params: file, language) and `/import-standard` (for NAMUR/DIN/ASME, params: file, standard_type, file_format). Include progress updates (Section 8 Workflows A & B)."
  - **Then**: Implement upload/import endpoints with proper tagging

**Step 1.2.2**: Implement text extraction (pdfplumber, lxml, Tesseract)
  - **Tests FIRST**: Pytest with sample PDFs (text-based, scanned, tables) and TBX files
  - **Prompt**: "Write function to extract text from PDF using pdfplumber (with table/multi-column support) and TBX (lxml), with Tesseract OCR fallback for scanned PDFs."
  - **Then**: Implement extraction functions

**Step 1.3.1**: NLP extraction (spaCy) - Characterization Testing
  - **Characterization Tests**: Manually extract terms from 10 sample PDFs, record ground truth (tests/fixtures/nlp_ground_truth.json), **THEN** write tests against ground truth, **THEN** implement automated extractor
  - **Prompt**: "Using spaCy and ground truth from tests/fixtures/nlp_ground_truth.json, create term-definition pair extractor for unstructured text. Target: ≥75% F1 score (precision + recall). Use NLP/rules hybrid approach."
  - **Then**: Implement spaCy-based extraction
  - **Tests**: Compare extracted terms to ground truth, assert F1 ≥ 0.75

**Step 1.3.2**: Store terms in SQLite/Neo4j with sync and retry logic
  - **Tests FIRST**: Integration tests (text → SQLite → Neo4j, verify sync accuracy, test retry on failure)
  - **Prompt**: "Connect extractor to DB: Save document terms as GlossaryEntry (source='internal'), gold standards as TerminologyCache (source='NAMUR'/'DIN'/'ASME'), populate Neo4j Term/Standard nodes with DEFINED_BY relationships. Implement one-way sync with retry logic (sync_to_neo4j_with_retry, max 3 retries, exponential backoff, SyncLog tracking) (Section 9)."
  - **Then**: Implement database storage and sync logic

**Milestone 1**: Upload PDFs/TBX via separate workflows (A & B), verify extraction in SQLite/Neo4j, test sync accuracy with retry, check progress indicators (coverage ≥80%)

---

### Phase 2: Validation, Translation & Graph Setup (Weeks 3-6 - 4 weeks)

**Concurrent Agent Spawn (Message 3)**:
```javascript
Task("Python Developer", "Steps 2.1.1-2.1.2: TDD - write validation endpoint tests with mocks, then implement /validate-term with TerminologyCache/Neo4j/IATE cached dataset integration", "backend-dev")
Task("Integration Engineer", "Step 2.1.2: TDD - write IATE importer tests, then implement IATE TBX/CSV dataset importer (quarterly imports), investigate IEC API or implement web scraping fallback", "api-docs")
Task("Unit Testing Engineer", "Expand test coverage for validation/translation flows, add mutation testing, create E2E smoke test for upload workflow", "tester")
```

**Step 2.1.1**: Add /validate-term endpoint (query TerminologyCache/Neo4j, IATE cached dataset)
  - **Tests FIRST**: Pytest with mocks for IATE cache queries, TerminologyCache queries, Neo4j Cypher queries
  - **Prompt**: "Implement FastAPI endpoint to mark terms as validated, query TerminologyCache/Neo4j for NAMUR/DIN/ASME matches, query IATE cached dataset. Prioritize gold standards (Section 9)."
  - **Then**: Implement validation endpoint

**Step 2.1.2**: Integrate IATE cached dataset, IEC API (investigate), DeepL API with caching
  - **Tests FIRST**: Integration tests for IATE dataset import, API mocks, fallback to cache on timeout
  - **Prompt**: "Implement IATE TBX/CSV dataset importer (import into TerminologyCache with source='IATE'). Investigate IEC Electropedia API (browser DevTools, XHR analysis) or implement web scraping (Playwright). Implement DeepL client with translation caching. Handle errors (rate limits, timeouts), prioritize TerminologyCache/Neo4j for NAMUR/DIN/ASME."
  - **Then**: Implement IATE importer, IEC client/scraper, DeepL with caching

**Concurrent Agent Spawn (Message 4)**:
```javascript
Task("Python Developer", "Steps 2.2.1-2.2.2: TDD - write translation tests, then implement DeepL integration with caching and gold standard fallback", "backend-dev")
Task("React Frontend Developer", "Steps 2.3.1-2.3.3: TDD - write Jest/axe-core tests, then implement React app with dark theme (WCAG-compliant contrast), Settings UI (color picker, logo, gold standard import), ProgressIndicator component", "coder")
Task("React Frontend Developer", "Step 2.3.2: TDD - write component tests, then create validation view with API fetch and gold standard side-by-side comparison", "coder")
```

**Step 2.2.1**: Translation logic (DeepL with caching, gold standard fallback)
  - **Tests FIRST**: Unit tests for translation with mock DeepL API, cache hit/miss, fallback to TerminologyCache
  - **Prompt**: "Create function to translate missing terms using DeepL API with caching (store in TerminologyCache with source='DeepL'), fallback to NAMUR/DIN/ASME TerminologyCache or manual input if API fails."
  - **Then**: Implement translation function with caching

**Step 2.2.2**: Manual correction UI integration
  - **Tests FIRST**: Integration tests for translation flow (API → cache → DB → Neo4j sync)
  - **Prompt**: "Integrate translation with SQLite updates and Neo4j sync for manual corrections. Add TRANSLATED_FROM relationship (Section 9)."
  - **Then**: Implement correction workflow

**Step 2.3.1**: Setup React app (Material-UI, vis.js/Reagraph, WCAG, ProgressIndicator)
  - **Tests FIRST**: Jest for dark theme rendering, axe-core for WCAG 2.1 AA compliance (contrast ≥4.5:1, disabled text ≥7.5:1, borders ≥3.5:1)
  - **Prompt**: "Generate React boilerplate with Material-UI dark theme (custom palette with WCAG-compliant contrast ratios), vis.js for Neo4j graph visualization, ProgressIndicator component (linear/circular, determinate/indeterminate), WCAG-compliant (Section 4, 10)."
  - **Then**: Implement React app skeleton

**Step 2.3.2**: Add upload/validation/graph views
  - **Tests FIRST**: React Testing Library for component rendering, API fetch mocks, pact-python contract tests
  - **Prompt**: "Create React component for term validation with API fetch (contract tested with pact-python), side-by-side gold standard matches from TerminologyCache, and Neo4j graph visualization (Section 10)."
  - **Then**: Implement validation UI components

**Step 2.3.3**: Settings UI (color picker, logo upload, gold standard import)
  - **Tests FIRST**: Jest for state management, axe-core for accessibility, file upload mocks
  - **Prompt**: "Add Settings component with: (1) color picker for dialog backgrounds, (2) PNG logo upload (max 1MB), (3) gold standard import (PDF/TBX with dropdown for NAMUR/DIN/ASME), WCAG-compliant (Section 4, 8)."
  - **Then**: Implement Settings UI

**Concurrent Agent Spawn (Message 5)**:
```javascript
Task("Python Developer", "Step 2.3.4: TDD - write endpoint tests for paginated Neo4j queries, then implement /graph-query endpoint with Cypher (pagination support)", "backend-dev")
Task("React Frontend Developer", "Step 2.3.4: TDD - write graph component tests, then implement Neo4j visualization with vis.js/Reagraph (infinite scroll/pagination)", "coder")
Task("Database Engineer", "Optimize Neo4j indexing for 10,000 nodes, write performance tests (target <2 sec queries)", "code-analyzer")
```

**Step 2.3.4**: Neo4j query endpoint and graph UI with pagination
  - **Tests FIRST**: Pytest for /graph-query endpoint (pagination, standard filter), Jest for graph component rendering
  - **Prompt**: "Generate FastAPI endpoint `/graph-query` with Cypher query support (e.g., 'Show terms linked to ASME'), pagination (offset/limit, default 500 nodes), standard filter. Create React component for Neo4j term-standard graph visualization using vis.js/Reagraph with infinite scroll (Section 9)."
  - **Then**: Implement graph query endpoint with pagination and UI

**Milestone 2**: Validate/translate terms with DeepL caching, import gold standards via Settings, view Neo4j graph with pagination, verify WCAG accessibility (contrast, keyboard nav) and sync accuracy, E2E smoke test passes (coverage ≥80%)

---

### Phase 3: Comparison & Builder (Weeks 7-8.5 - 2.5 weeks)

**Concurrent Agent Spawn (Message 6)**:
```javascript
Task("Python Developer", "Steps 3.1.1-3.1.2: TDD - write matching tests with gold standard prioritization, then implement matcher and TBX exporter with ISO 30042 validation", "backend-dev")
Task("React Frontend Developer", "Steps 3.2.1-3.2.2: TDD - write comparison view tests, then implement UI with flags, progress indicators, export buttons", "coder")
Task("Integration Engineer", "Step 3.1.2: Validate TBX exports against ISO 30042 schema (xmllint/lxml), add ISO 12620 metadata", "api-docs")
```

**Step 3.1.1**: Matching logic (prioritize gold standards/Neo4j)
  - **Tests FIRST**: Pytest for match quality scoring, gold standard prioritization (source_priority 1.5), fuzzy matching
  - **Prompt**: "Implement term matching algorithm for de/en pairs using spaCy similarity + python-Levenshtein/jellyfish. Prioritize NAMUR/DIN/ASME (source_priority=1.5) and Neo4j SYNONYM relationships over internal terms (Section 9)."
  - **Then**: Implement matching algorithm

**Step 3.1.2**: Builder/export (TBX XML with ISO 30042 compliance)
  - **Tests FIRST**: Schema validation tests against ISO 30042 TBX-Core (xmllint/lxml)
  - **Prompt**: "Create TBX-compliant XML exporter from SQLite GlossaryEntry. Include ISO 12620 metadata (martif, termEntry, langSet, tig), multilingual entries. Validate against ISO 30042 schema (Section 20)."
  - **Then**: Implement TBX exporter

**Step 3.2.1**: Comparison views (flags, progress indicators)
  - **Tests FIRST**: Jest for rendering flags, progress bar updates
  - **Prompt**: "Build React view for glossary comparison with inconsistency flags (red for score <0.7), progress bar for processing, NAMUR/DIN/ASME/Neo4j prioritization indicators (green badges) (Section 8)."
  - **Then**: Implement comparison UI

**Step 3.2.2**: Export UI (format buttons)
  - **Tests FIRST**: E2E Cypress test for export flow (click button → download file → verify format)
  - **Prompt**: "Add export buttons in React for CSV/Excel/JSON/TBX formats, calling backend `/export` endpoint, with ProgressIndicator component (Section 4)."
  - **Then**: Implement export UI

**Milestone 3**: Compare/merge bilingual entries, export to all formats (CSV, Excel, JSON, TBX), verify Neo4j graph compliance and ISO 30042 TBX validation (xmllint passes), verify progress indicators update correctly (coverage ≥85%)

---

### Phase 4: Testing & Polish (Weeks 9-11.5 - 3 weeks)

**Concurrent Agent Spawn (Message 7)**:
```javascript
Task("Unit Testing Engineer", "Step 4.1.1: Expand test coverage to ≥90% for critical modules (PDF/TBX Parser, Neo4j Graph Manager, SQLite↔Neo4j sync). Add mutation tests (mutmut, target 70%)", "tdd-london-swarm")
Task("Unit Testing Engineer", "Step 4.1.2: Create Cypress E2E tests for full workflow (upload → validate → export → graph visualization), including gold standard import", "tester")
Task("React Frontend Developer", "Step 4.2.1: Polish UI - enhance dark mode contrast (WCAG fixes), improve Neo4j graph interaction features (zoom, filter, search)", "coder")
```

**Step 4.1.1**: Unit tests for all modules (include Neo4j)
  - **Prompt**: "Generate comprehensive Pytest suite for: (1) PDF/TBX Parser (handle tables, multi-columns, OCR), (2) Neo4j Graph Manager (node creation, Cypher queries, sync accuracy, retry logic), (3) NAMUR/DIN/ASME parsing/validation. Add mutation testing with mutmut (target 70% mutation score, document surviving mutants) (Section 14)."
  - **Tests**: Achieve ≥90% coverage for critical modules

**Step 4.1.2**: Integration/E2E tests (Cypress for UI/graph)
  - **Prompt**: "Create Cypress tests for: (1) Upload internal PDF → extract → validate, (2) Import NAMUR/DIN/ASME via Settings → verify TerminologyCache, (3) Translate → match → export → verify file, (4) Neo4j graph visualization with pagination (query 'Show terms linked to ASME') (Section 8 Workflows A-C)."
  - **Tests**: E2E test suite runs in CI/CD

**Concurrent Agent Spawn (Message 8)**:
```javascript
Task("React Frontend Developer", "Step 4.2.1: Refactor React for WCAG 2.1 AA (axe-core audits, fix contrast issues), enhance Neo4j graph (add search, filtering, layout options)", "coder")
Task("Python Developer", "Step 4.2.2: Optimize PDF/TBX parsing for 100-page docs (<60 sec), Neo4j queries for 10,000 nodes (<2 sec). Write performance tests", "backend-dev")
Task("DevOps Engineer", "Steps 4.3.1-4.3.2: Implement structured logging (Winston/structlog), create Docker setup (FastAPI + React + Neo4j) with health checks and Docker secrets, write smoke tests", "cicd-engineer")
```

**Step 4.2.1**: Polish UI (dark theme WCAG, graph enhancements)
  - **Prompt**: "Refactor React for: (1) Better dark mode contrast (WCAG 2.1 AA, ≥4.5:1 text, ≥7.5:1 disabled text, ≥3.5:1 borders), (2) Enhanced Neo4j graph visualization (search terms, filter by standard, layout algorithms: force-directed, hierarchical, radial). Run axe-core in Jest (Section 4)."
  - **Tests**: Axe-core accessibility tests in Jest (0 violations)

**Step 4.2.2**: Optimize performance (chunked parsing, Neo4j queries)
  - **Prompt**: "Optimize: (1) PDF/TBX extraction for 100-page documents (target <60 sec via chunking/streaming), (2) Neo4j Cypher queries for 10,000 Term nodes (target <2 sec via indexing, EXPLAIN analysis). Write performance tests (pytest-benchmark, Neo4j EXPLAIN) (Section 4)."
  - **Tests**: Performance benchmarks (pytest-benchmark, Neo4j EXPLAIN)

**Step 4.3.1**: Error handling/logs (gold standards, Neo4j)
  - **Prompt**: "Implement structured logging (Winston for FastAPI, console for React) for: (1) All endpoints (gold standard import, validation, export), (2) Neo4j connection errors, (3) API failures (IATE, DeepL), (4) Sync retry failures. Log to Sentry via MCP (Section 3)."
  - **Tests**: Tests for error paths (mock failures, verify logs)

**Step 4.3.2**: Deployment (Docker with health checks and secrets)
  - **Prompt**: "Create Docker Compose setup: (1) FastAPI backend with health check (curl /health), (2) React frontend (served via Nginx) with health check, (3) Neo4j Community Edition (bolt://localhost:7687) with health check (cypher-shell). Include Docker secrets for NEO4J_PASSWORD, DEEPL_API_KEY. Enable SQLite WAL mode for concurrency (Section 9)."
  - **Tests**: Smoke tests in container (health checks pass, DB connectivity verified)

**Milestone 4**: Full app walkthrough (all workflows A-C), verify: (1) Custom theme/logo, (2) Offline mode with TerminologyCache, (3) WCAG 2.1 AA accessibility (0 axe-core violations), (4) Neo4j graph visualization with pagination/search/filter, (5) TBX ISO 30042 compliance, (6) Docker health checks and secrets working, (7) Mutation testing ≥70% (coverage ≥85%)

---

### Post-Implementation
- **Retrospective (Week 12)**: Review TDD effectiveness, agent coordination, identify bottlenecks; plan Section 15 enhancements
- **Monitoring**: Integrate Sentry (MCP) for production logs, Neo4j monitoring dashboard

## 19. Acceptance Criteria
- Upload German/English PDFs via Workflow A; extract entries (≥75% F1 score)
- Import NAMUR/DIN/ASME (PDF/TBX) via Workflow B (Settings UI with dropdown)
- Validate entries against IEC/IATE cached dataset/gold standards/Neo4j (≥90% match rate)
- Translate missing terms with DeepL caching and manual correction
- Export glossary to CSV, Excel, JSON, TBX (ISO 30042 compliant, xmllint passes)
- Visualize term-standard relationships in Neo4j graph (interactive, pagination, <2 sec queries)
- Version entries and relationships, auditable (GlossaryVersion table)
- Offline operation with TerminologyCache/Neo4j caching, GDPR compliance
- UI: Dark theme (WCAG 2.1 AA, ≥4.5:1 contrast, ≥7.5:1 disabled text), logo upload (PNG, 1MB), customizable dialog colors, ProgressIndicator component, gold standard import, graph visualization with search/filter
- Data integrity: Sync retry logic works (SyncLog tracks failures), daily SQLite backups run
- Security: Docker secrets for credentials, SQLite WAL mode enabled
- Testing: ≥90% coverage (critical), ≥70% mutation score, 0 axe-core violations, contract tests pass

## 20. Standards Alignment
**ISO Standards**:
- ISO 26162-1:2019, 26162-2:2019, 26162-3:2023 (terminology DBs)
- ISO 30042:2019 (TBX)
- ISO 12620:2019 (data categories)
- ISO 704:2022 (concept systems, aligned with NAMUR/DIN/ASME/Neo4j)
- Others: ISO 1087, 860, 10241-1/2, 12199, 12200, 6156
**Gold Standards**: NAMUR, DIN, ASME (e.g., Y14.5, B31.3)
**TBX Compliance**: TBX-Core, XML export, ISO 12620 metadata, multilingual entries
**Graph Compliance**: Neo4j relationships align with ISO 704 (e.g., DEFINED_BY)

## 21. Stakeholder List
- Engineering Teams: Term extraction/validation/graph visualization
- Documentation Teams: Glossary accuracy
- Project Sponsors: Standards alignment
- IT/Security: GDPR, Neo4j security
- Consultants: NLP/standards/graph DB expertise

## 22. Risk Assessment
- **NLP Accuracy**: Mitigate with hybrid NLP/rules, characterization testing (ground truth), manual review, Neo4j validation
- **API Downtime**: Offline mocks, TerminologyCache, IATE cached dataset, Neo4j caching, DeepL caching
- **User Adoption**: Usability testing, intuitive GUI/graph
- **Scalability**: Chunked processing, Neo4j indexing (10,000 nodes), pagination
- **UI/Graph Errors**: Validate uploads, test WCAG/graph rendering
- **Neo4j Learning Curve**: Use Community Edition, Claude Cypher queries, GraphAcademy training
- **Data Sync Failures**: Implement retry logic (SyncLog) for SQLite↔Neo4j sync, monitor with logs, Sentry alerts
- **DeepL API Limits**: Caching reduces calls (500k chars/month free tier sufficient)

## 23. Glossary
- **GlossaryEntry**: Term/definition record (SQLite source of truth)
- **TBX**: TermBase eXchange format (ISO 30042)
- **NLP**: Natural Language Processing
- **IATE**: EU Terminology database (cached dataset, not API)
- **Gold Standard**: NAMUR, DIN, ASME authoritative sources (read-only, prioritized in matching)
- **Neo4j**: Graph database for term-standard relationship visualization
- **TDD**: Test-Driven Development (London School - write tests first)
- **Characterization Testing**: Manual ground truth creation first, then tests (for NLP)
- **Sync**: One-way data flow from SQLite → Neo4j for visualization (with retry logic)
- **SyncLog**: Table tracking sync failures for recovery

## 24. Open Questions
- Additional languages? (Planned in Section 15 enhancements)
- Deployment model? (Hybrid: local default, cloud optional)
- Enterprise integrations? (API hooks in Section 15 future enhancements)
- Document volume? (100 docs/month, 50MB max; standards 10MB max)
- Glossary/graph maintenance? (Documentation teams via Editor role)
- Neo4j volume? (10,000 Term nodes, 100 Standard nodes - Section 9 limits)
- Database choice? (SQLite recommended for simplicity; H2 if Java ecosystem integration needed)

## 25. References
- IEC Electropedia: https://www.electropedia.org/
- IEV-Wörterbuch: https://www.electropedia.org/iev/
- IATE: https://iate.europa.eu/ (cached dataset: https://iate.europa.eu/download-iate)
- NAMUR: https://www.namur.net/en/publications/
- DIN: https://www.din.de/en
- ASME: https://www.asme.org/codes-standards
- Neo4j: https://neo4j.com/docs/, GraphAcademy: https://graphacademy.neo4j.com/
- ISO Standards: https://www.iso.org/standards.html
- DeepL: https://www.deepl.com/docs-api/
- Microsoft Translator: https://learn.microsoft.com/en-us/azure/ai-services/translator/
- GitHub: https://github.com/NCIOCPL/glossary-app, https://github.com/diegoberaldin/MetaTerm
- Claude: https://www.anthropic.com/claude
- MCP: https://modelcontextprotocol.io/
- Claude-Flow: https://github.com/ruvnet/claude-flow
- Tools: Cursor (https://cursor.sh/), Aider (https://aider.chat/), Zed (https://zed.dev/), vis.js (https://visjs.org/), Reagraph (https://reagraph.dev/)

## 26. Revision History
- **Version 1.0**: Initial draft (Oct 1, 2025; User)
- **Version 1.1-1.8**: Added details, Claude/MCP, ASME, GUI (Oct 16, 2025; Grok)
- **Version 1.9**: Added Neo4j for term-standard visualization (Oct 16, 2025; Grok)
- **Version 2.0**: Consolidated, refined for Claude, finalized for development (Oct 16, 2025; Grok)
- **Version 2.1**: Critical updates for agentic development (Oct 16, 2025; Claude)
  - Added concurrent execution strategy (Section 17)
  - Mapped PRT roles to Claude-Flow agent types (Section 16)
  - Clarified TDD approach throughout phases (Section 13, 18)
  - Detailed Neo4j sync architecture (Section 9)
  - Separated gold standard import workflow (Section 8)
- **Version 2.2**: Expert review fixes incorporated (Oct 16, 2025; Claude)
  - Extended timeline from 10 weeks to 12 weeks (added Pre-Phase 0.5 weeks, Phase 2 +0.5, Phase 3 +0.5, Phase 4 +0.5)
  - **Section 7 (Technology Stack)**: Replaced "PyPDF2 or pdfplumber" with "pdfplumber (text, tables, multi-column)", updated Translation/Validation to DeepL with caching + IATE cached dataset + IEC investigation, added python-Levenshtein, jellyfish, pact-python
  - **Section 9 (Data Model)**: Added SyncLog table (sync failure tracking with retry logic), UploadedDocument table (file metadata tracking), added indexes (idx_glossary_entry_term_lang, idx_terminology_cache_term_source, etc.), added CHECK constraints (language, source, validation_status), enhanced GlossaryEntry with sync_status/updated_at, added Neo4j indexes (term_name_idx, term_language_idx, etc.), added backup strategy (daily SQLite backups with 30-day retention, weekly Neo4j dumps)
  - **Section 10 (Frontend)**: Added ProgressIndicator component to component list
  - **Section 12 (Development Phases)**: Updated timeline (Pre-Phase 0.5 + Phase 1: 2 + Phase 2: 4 + Phase 3: 2.5 + Phase 4: 3 = 12 weeks)
  - **Section 13 (Testing)**: Updated mutation testing target from 80% to 70% for MVP, added pact-python contract testing, added characterization testing note for NLP
  - **Section 18 (Implementation Plan)**: Updated total timeline to 12 weeks, added Pre-Phase (Week 0), updated Step 1.2.2 to pdfplumber only, updated Step 1.3.1 to characterization testing approach, updated Step 2.1.2 to IATE cached dataset + IEC investigation, added E2E smoke tests in Phase 2, added retry logic to Step 1.3.2, added pagination to Step 2.3.4, added Docker health checks and secrets to Step 4.3.2
  - Based on 8 expert agent reviews (A1-A8): Backend (A1), NLP (A2), Database (A3), Testing (A4), Frontend (A5), Integration (A6), DevOps (A7), Coordinator (A8)
