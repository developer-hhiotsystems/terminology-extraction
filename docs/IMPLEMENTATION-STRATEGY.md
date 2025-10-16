# Implementation Strategy: Glossary Extraction & Validation App
**Version**: 1.0
**Based on**: PRT v2.1
**Date**: October 16, 2025
**Project**: Glossary Extraction & Validation App

---

## Executive Summary

This implementation strategy provides a comprehensive roadmap for developing a bilingual glossary extraction and validation application using **agentic development with Claude-Flow orchestration**. The project follows **Test-Driven Development (TDD, London School)** methodology across a **10-week timeline** with **8 specialized agent roles** working concurrently.

### Key Metrics
- **Timeline**: 10 weeks (4 phases)
- **Agent Roles**: 8 (mapped to Claude-Flow agent types)
- **Test Coverage**: ≥90% critical modules, ≥80% core logic
- **Technology Stack**: FastAPI + React + SQLite + Neo4j
- **Concurrent Execution**: Mandatory (CLAUDE.md compliance)
- **Standards Compliance**: ISO 30042 (TBX), ISO 704, WCAG 2.1 AA

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Agent Team Structure](#2-agent-team-structure)
3. [Development Phases](#3-development-phases)
4. [Concurrent Execution Strategy](#4-concurrent-execution-strategy)
5. [Technology Decisions](#5-technology-decisions)
6. [Risk Mitigation](#6-risk-mitigation)
7. [Quality Assurance](#7-quality-assurance)
8. [Deployment Strategy](#8-deployment-strategy)
9. [Success Metrics](#9-success-metrics)

---

## 1. Project Overview

### 1.1 Objective
Develop a guided software tool that extracts, validates, compares, and translates bilingual glossary entries from technical documents (German and English), aligned with international standards (IEC Electropedia, IATE) and gold standards (NAMUR, DIN, ASME), with Neo4j graph visualization of term-standard relationships.

### 1.2 Core Workflows

**Workflow A: Internal Document Processing**
- Upload German/English PDFs → Extract terms (spaCy/NLP) → Store in SQLite (source='internal') + Neo4j
- Validate against gold standards (TerminologyCache) and Neo4j relationships
- Translate missing entries (DeepL API)
- Match bilingual pairs with quality scoring

**Workflow B: Gold Standard Import**
- Settings UI → Upload NAMUR/DIN/ASME (PDF/TBX) → Select type from dropdown
- Extract/parse → Store in TerminologyCache + Neo4j Standard node
- Read-only gold standard terms for validation prioritization

**Workflow C: Complete Pipeline**
- Combine Workflows A + B → Match/compare → Visualize Neo4j graph → Export (CSV/Excel/JSON/TBX)

### 1.3 Architecture Principles

**Database Strategy**:
- **SQLite**: Source of truth (GlossaryEntry, GlossaryMatch, GlossaryVersion, TerminologyCache)
- **Neo4j**: Read-only visualization layer (Term/Standard nodes, DEFINED_BY relationships)
- **Sync**: One-way SQLite → Neo4j (on-demand after extraction/validation)

**Design Patterns**:
- **Modularity**: Independent, reusable backend modules (PDF Parser, NLP Extractor, Validator, Translator, Graph Manager)
- **User Control**: Manual review gates for validation/translation (no auto-generation without approval)
- **Offline-First**: Local mocks, TerminologyCache, Neo4j caching for API downtime resilience

---

## 2. Agent Team Structure

### 2.1 Agent Role Mapping

Based on PRT v2.1 Section 16, here's the complete agent team with execution responsibilities:

| Agent ID | PRT Role | Claude-Flow Type | Primary Responsibilities | Phase Focus |
|----------|----------|------------------|--------------------------|-------------|
| **A1** | Python Developer | `backend-dev` | FastAPI endpoints, SQLAlchemy models, Neo4j driver integration | 1, 2, 3 |
| **A2** | NLP Specialist | `researcher` | spaCy term extraction, fuzzy matching, NLP pipeline optimization | 1 |
| **A3** | Database Engineer | `code-analyzer` | SQLite/H2 schemas, Neo4j graph design, Cypher queries, sync logic | 1, 2, 4 |
| **A4** | Unit Testing Engineer | `tdd-london-swarm` | TDD implementation, pytest/Jest suites, mutation testing (mutmut) | 1, 2, 3, 4 |
| **A5** | React Frontend Developer | `coder` | React UI, Material-UI theming, vis.js/Reagraph graph viz, WCAG | 2, 3, 4 |
| **A6** | Integration Engineer | `api-docs` | DeepL/IATE/IEC API clients, TBX parser, error handling | 2, 3 |
| **A7** | DevOps Engineer | `cicd-engineer` | Docker Compose, CI/CD pipelines, Neo4j deployment, monitoring | 4 |
| **A8** | Project Coordinator | `task-orchestrator` | Milestone tracking, agent handoffs, TodoWrite management | 1, 2, 3, 4 |

### 2.2 Agent Coordination Protocol

**Every agent spawned via Claude Code Task tool MUST execute:**

**Before Work** (pre-task hook):
```bash
npx claude-flow@alpha hooks pre-task --description "[Agent A1: Initialize FastAPI]"
npx claude-flow@alpha hooks session-restore --session-id "swarm-phase1"
```

**During Work** (post-edit hook):
```bash
npx claude-flow@alpha hooks post-edit --file "src/backend/app.py" --memory-key "swarm/A1/step-1.1.1"
npx claude-flow@alpha hooks notify --message "Completed FastAPI /health endpoint with tests"
```

**After Work** (post-task hook):
```bash
npx claude-flow@alpha hooks post-task --task-id "A1-step-1.1.1"
npx claude-flow@alpha hooks session-end --export-metrics true
```

---

## 3. Development Phases

### 3.1 Phase 1: Document Ingestion & Extraction (Weeks 1-2)

**Objectives**:
- ✅ Upload PDFs/TBX via separate workflows (internal vs gold standards)
- ✅ Extract terms using PyPDF2/Tesseract (PDF) and lxml (TBX)
- ✅ Implement spaCy NLP extraction for term-definition pairs
- ✅ Store in SQLite (GlossaryEntry, TerminologyCache) + Neo4j (Term, Standard nodes)
- ✅ Setup SQLite ↔ Neo4j one-way sync

**Concurrent Agent Execution (Message 1)**:
```javascript
[Single Message - Phase 1 Initialization]:
  Task("Python Developer (A1)",
    "TDD: Write pytest for /health endpoint, then initialize FastAPI app with SQLAlchemy models (GlossaryEntry, TerminologyCache), neo4j-driver. Steps 1.1.1-1.1.2",
    "backend-dev")

  Task("Database Engineer (A3)",
    "TDD: Write schema migration tests, then setup SQLite schemas (GlossaryEntry, TerminologyCache, GlossaryMatch, GlossaryVersion) and Neo4j constraints (UNIQUE on Term.id, Standard.id). Configure bolt://localhost:7687. Step 1.1.2",
    "code-analyzer")

  Task("Unit Testing Engineer (A4)",
    "Create pytest framework with mocks for Neo4j (neo4j-driver), DeepL, IATE. Setup coverage reporting (≥80% target). Configure mutmut for mutation testing. Phase 1 tests",
    "tester")

  TodoWrite { todos: [
    {content: "Initialize FastAPI skeleton with /health", status: "in_progress", activeForm: "Initializing FastAPI skeleton"},
    {content: "Setup SQLite database schemas", status: "in_progress", activeForm: "Setting up SQLite database schemas"},
    {content: "Configure Neo4j connection and constraints", status: "in_progress", activeForm: "Configuring Neo4j connection"},
    {content: "Create pytest framework with mocks", status: "in_progress", activeForm: "Creating pytest framework"},
    {content: "Implement /upload-document endpoint", status: "pending", activeForm: "Implementing /upload-document endpoint"},
    {content: "Implement /import-standard endpoint", status: "pending", activeForm: "Implementing /import-standard endpoint"},
    {content: "Build PDF text extraction (PyPDF2 + Tesseract)", status: "pending", activeForm: "Building PDF text extraction"},
    {content: "Build TBX parser (lxml)", status: "pending", activeForm: "Building TBX parser"},
    {content: "Implement spaCy term extraction", status: "pending", activeForm: "Implementing spaCy term extraction"},
    {content: "Create SQLite↔Neo4j sync trigger", status: "pending", activeForm: "Creating SQLite↔Neo4j sync trigger"}
  ]}

  Bash "mkdir -p src/{backend,frontend,database,tests,config,scripts}"
  Write "src/backend/app.py"
  Write "src/backend/models.py"
  Write "src/database/neo4j_schema.cypher"
  Write "tests/conftest.py"
```

**Concurrent Agent Execution (Message 2)**:
```javascript
[Single Message - Phase 1 Upload/Extraction]:
  Task("Python Developer (A1)",
    "TDD: Write endpoint tests with mock files, then implement /upload-document (params: file, language) for Workflow A and /import-standard (params: file, standard_type, file_format) for Workflow B. Add progress indicators. Steps 1.2.1",
    "backend-dev")

  Task("Python Developer (A1)",
    "TDD: Write extraction tests with sample PDFs/TBX, then implement text extraction: PyPDF2/pdfplumber for PDFs, Tesseract for scanned OCR, lxml for TBX parsing. Handle tables/multi-columns. Step 1.2.2",
    "backend-dev")

  Task("NLP Specialist (A2)",
    "TDD: Write extraction tests with sample unstructured text, then implement spaCy term-definition extractor using hybrid NLP/rules. Support German and English models. Step 1.3.1",
    "researcher")

  Task("Database Engineer (A3)",
    "TDD: Write sync tests (SQLite→Neo4j accuracy), then implement sync_to_neo4j(entry_id) function. Create DEFINED_BY relationships when gold standards imported. Step 1.3.2",
    "code-analyzer")
```

**Milestone 1 Criteria**:
- [ ] /health endpoint returns 200
- [ ] /upload-document accepts PDF, tags as source='internal'
- [ ] /import-standard accepts PDF/TBX, tags as source='NAMUR'/'DIN'/'ASME'
- [ ] PyPDF2 extracts text from 100-page PDF in <60 sec
- [ ] Tesseract OCR fallback works for scanned PDFs
- [ ] lxml parses TBX with ISO 12620 metadata
- [ ] spaCy extracts ≥80% of term-definition pairs (manual validation)
- [ ] SQLite stores GlossaryEntry with correct source field
- [ ] Neo4j Term nodes created with UNIQUE id constraint
- [ ] sync_to_neo4j() maintains 1:1 mapping (SQLite ↔ Neo4j)
- [ ] Test coverage ≥80% for all Phase 1 modules

---

### 3.2 Phase 2: Validation, Translation & Graph Setup (Weeks 3-5.5)

**Objectives**:
- ✅ Validate terms against TerminologyCache, Neo4j, and external APIs (IATE, IEC)
- ✅ Translate missing entries (DeepL) with gold standard fallback
- ✅ Build React UI with dark theme, Settings UI (logo, gold standard import)
- ✅ Implement Neo4j graph visualization (vis.js/Reagraph)
- ✅ Ensure WCAG 2.1 AA compliance (contrast ≥4.5:1, axe-core tests)

**Concurrent Agent Execution (Message 3)**:
```javascript
[Single Message - Phase 2 Validation/Translation]:
  Task("Python Developer (A1)",
    "TDD: Write /validate-term endpoint tests with TerminologyCache/Neo4j mocks, then implement validation logic. Query TerminologyCache (NAMUR/DIN/ASME priority), Neo4j SYNONYM relationships, mock IATE API. Steps 2.1.1",
    "backend-dev")

  Task("Integration Engineer (A6)",
    "TDD: Write API client tests with mocks (rate limits, timeouts), then implement requests-based IATE/IEC clients. Prioritize TerminologyCache before external calls. Add offline fallback. Step 2.1.2",
    "api-docs")

  Task("Python Developer (A1)",
    "TDD: Write translation tests with DeepL mock, then implement translate_missing() function. Fallback to TerminologyCache (NAMUR/DIN/ASME) if API fails. Support manual input. Steps 2.2.1-2.2.2",
    "backend-dev")

  Task("Unit Testing Engineer (A4)",
    "Expand pytest coverage for validation/translation flows. Add integration tests for API fallback logic. Target ≥85% coverage. Phase 2 tests",
    "tester")

  TodoWrite { todos: [
    {content: "Implement /validate-term endpoint with cache priority", status: "in_progress", activeForm: "Implementing /validate-term endpoint"},
    {content: "Build IATE/IEC API clients with fallback", status: "in_progress", activeForm: "Building IATE/IEC API clients"},
    {content: "Implement DeepL translation with gold standard fallback", status: "in_progress", activeForm: "Implementing DeepL translation"},
    {content: "Setup React app boilerplate (Material-UI)", status: "pending", activeForm: "Setting up React app boilerplate"},
    {content: "Create Settings UI (color picker, logo, gold standard import)", status: "pending", activeForm: "Creating Settings UI"},
    {content: "Build validation view with API fetch", status: "pending", activeForm: "Building validation view"},
    {content: "Implement Neo4j graph visualization (vis.js)", status: "pending", activeForm: "Implementing Neo4j graph visualization"},
    {content: "Run axe-core accessibility tests (WCAG 2.1 AA)", status: "pending", activeForm: "Running axe-core accessibility tests"}
  ]}
```

**Concurrent Agent Execution (Message 4)**:
```javascript
[Single Message - Phase 2 Frontend Development]:
  Task("React Frontend Developer (A5)",
    "TDD: Write Jest tests for dark theme rendering (contrast ≥4.5:1), then create React boilerplate with Material-UI dark theme, vis.js for graph viz. Run axe-core for WCAG compliance. Step 2.3.1",
    "coder")

  Task("React Frontend Developer (A5)",
    "TDD: Write React Testing Library tests for validation component, then implement term validation view with: (1) API fetch to /validate-term, (2) side-by-side gold standard matches, (3) Neo4j relationship display. Step 2.3.2",
    "coder")

  Task("React Frontend Developer (A5)",
    "TDD: Write Jest state tests and axe-core accessibility tests, then create Settings component: (1) color picker for dialog backgrounds, (2) PNG logo upload (max 1MB), (3) gold standard import (dropdown: NAMUR/DIN/ASME, accept PDF/TBX). Step 2.3.3",
    "coder")

  Task("Python Developer (A1)",
    "TDD: Write /graph-query endpoint tests with Cypher mocks, then implement Neo4j query endpoint (support queries like 'Show terms linked to ASME'). Return nodes/edges JSON. Step 2.3.4 (backend)",
    "backend-dev")

  Task("React Frontend Developer (A5)",
    "TDD: Write graph component tests (node/edge rendering), then implement Neo4j visualization using vis.js or Reagraph. Support zoom, pan, node click (show term details). Step 2.3.4 (frontend)",
    "coder")

  Task("Database Engineer (A3)",
    "Optimize Neo4j: Create indexes on Term.term, Standard.name. Test Cypher query performance for 10,000 nodes (target <2 sec). Write performance benchmarks. Step 2.3.4 (optimization)",
    "code-analyzer")
```

**Milestone 2 Criteria**:
- [ ] /validate-term queries TerminologyCache before IATE
- [ ] IATE/IEC clients handle rate limits with 3-retry logic
- [ ] DeepL translates German→English with 95% accuracy (sample validation)
- [ ] Manual correction UI updates SQLite + syncs to Neo4j
- [ ] React app loads with dark theme (Material-UI default palette)
- [ ] Settings UI: color picker changes dialog background
- [ ] Settings UI: logo upload displays PNG in header (max 1MB enforced)
- [ ] Settings UI: gold standard import workflow (dropdown, file upload, progress bar)
- [ ] Validation view shows side-by-side: (1) internal term, (2) gold standard match, (3) confidence score
- [ ] Neo4j graph renders 1,000 nodes in <2 sec (vis.js/Reagraph)
- [ ] /graph-query endpoint returns Cypher results as JSON
- [ ] axe-core tests pass (0 violations for WCAG 2.1 AA)
- [ ] Test coverage ≥80% (backend), ≥70% (frontend)

---

### 3.3 Phase 3: Comparison & Builder (Weeks 6-7)

**Objectives**:
- ✅ Match bilingual German/English terms with quality scoring
- ✅ Prioritize gold standards (NAMUR/DIN/ASME) with source_priority=1.5
- ✅ Build TBX-compliant XML exporter (ISO 30042)
- ✅ Create comparison UI with inconsistency flags and progress indicators
- ✅ Export to CSV, Excel, JSON formats

**Concurrent Agent Execution (Message 5)**:
```javascript
[Single Message - Phase 3 Matching/Export]:
  Task("Python Developer (A1)",
    "TDD: Write matching tests with gold standard priority (source_priority=1.5), then implement match_bilingual_terms() algorithm. Use fuzzy matching (spaCy similarity) + Neo4j SYNONYM relationships. Flag inconsistencies (score <0.7). Step 3.1.1",
    "backend-dev")

  Task("Integration Engineer (A6)",
    "TDD: Write TBX schema validation tests (ISO 30042), then implement TBX XML exporter. Include ISO 12620 metadata (martif, termEntry, langSet, tig). Support multilingual entries. Step 3.1.2",
    "api-docs")

  Task("React Frontend Developer (A5)",
    "TDD: Write Jest tests for comparison view rendering (flags, progress bar), then implement UI: (1) Display de/en pairs, (2) Show inconsistency flags (red for score <0.7), (3) Highlight gold standard matches (green badge), (4) Progress bar for matching. Step 3.2.1",
    "coder")

  Task("React Frontend Developer (A5)",
    "TDD: Write E2E Cypress test for export flow (click button → download → verify), then add export UI: (1) Format buttons (CSV/Excel/JSON/TBX), (2) Call /export endpoint with format param, (3) Progress indicator, (4) Download link. Step 3.2.2",
    "coder")

  Task("Unit Testing Engineer (A4)",
    "Write integration tests for matching algorithm (test 100 de/en pairs, verify gold standard priority). Add E2E Cypress test for full workflow: upload → validate → match → export. Phase 3 tests",
    "tester")

  TodoWrite { todos: [
    {content: "Implement bilingual matching algorithm with fuzzy logic", status: "in_progress", activeForm: "Implementing bilingual matching algorithm"},
    {content: "Build TBX XML exporter (ISO 30042 compliant)", status: "in_progress", activeForm: "Building TBX XML exporter"},
    {content: "Create comparison view with inconsistency flags", status: "in_progress", activeForm: "Creating comparison view"},
    {content: "Add export UI with format buttons (CSV/Excel/JSON/TBX)", status: "in_progress", activeForm: "Adding export UI"},
    {content: "Validate TBX exports against ISO 30042 schema", status: "pending", activeForm: "Validating TBX exports"},
    {content: "Write E2E Cypress tests for export workflow", status: "pending", activeForm: "Writing E2E Cypress tests"}
  ]}
```

**Milestone 3 Criteria**:
- [ ] Matching algorithm prioritizes gold standards (source_priority=1.5)
- [ ] Fuzzy matching uses spaCy similarity + Neo4j SYNONYM (threshold ≥0.7)
- [ ] Inconsistencies flagged for manual review (score <0.7)
- [ ] TBX export validates against ISO 30042 schema (xmllint or lxml validation)
- [ ] Exported TBX includes ISO 12620 metadata (martif, termEntry, langSet, tig)
- [ ] Comparison view displays 1,000 pairs with <1 sec load time
- [ ] Inconsistency flags render with red badge, gold standard matches with green
- [ ] Export buttons download files in correct format (CSV/Excel verified with pandas)
- [ ] Progress indicators update during matching (0% → 100%)
- [ ] E2E Cypress test covers: upload → validate → match → export → verify file
- [ ] Test coverage ≥85% (backend), ≥75% (frontend)

---

### 3.4 Phase 4: Testing & Polish (Weeks 8-10)

**Objectives**:
- ✅ Expand test coverage to ≥90% (critical modules), ≥85% (core logic)
- ✅ Add E2E Cypress tests for all workflows (A, B, C)
- ✅ Run mutation testing (mutmut) for regression detection
- ✅ Optimize performance (PDF parsing <60 sec, Neo4j queries <2 sec)
- ✅ Enhance UI (WCAG 2.1 AA, graph interaction features)
- ✅ Deploy with Docker Compose (FastAPI + React + Neo4j)

**Concurrent Agent Execution (Message 6)**:
```javascript
[Single Message - Phase 4 Comprehensive Testing]:
  Task("Unit Testing Engineer (A4)",
    "Expand pytest coverage: (1) PDF/TBX Parser (test tables, multi-columns, OCR), (2) Neo4j Graph Manager (Cypher queries, sync accuracy), (3) NAMUR/DIN/ASME parsing. Run mutmut for mutation testing (target 80% mutation score). Step 4.1.1",
    "tdd-london-swarm")

  Task("Unit Testing Engineer (A4)",
    "Create comprehensive Cypress E2E suite: (1) Workflow A (upload internal PDF → extract → validate), (2) Workflow B (import NAMUR via Settings → verify cache), (3) Workflow C (translate → match → export → graph viz). Step 4.1.2",
    "tester")

  Task("React Frontend Developer (A5)",
    "Run axe-core audits, fix WCAG violations. Enhance graph: (1) Search terms by name, (2) Filter by standard (NAMUR/DIN/ASME), (3) Layout algorithms (force-directed, hierarchical). Step 4.2.1",
    "coder")

  Task("Python Developer (A1)",
    "Optimize: (1) PDF parsing for 100-page docs (chunked processing, target <60 sec), (2) Neo4j queries for 10,000 nodes (indexing, EXPLAIN analysis, target <2 sec). Write pytest-benchmark performance tests. Step 4.2.2",
    "backend-dev")

  TodoWrite { todos: [
    {content: "Expand pytest coverage to ≥90% (critical modules)", status: "in_progress", activeForm: "Expanding pytest coverage"},
    {content: "Run mutmut mutation testing (target 80% score)", status: "in_progress", activeForm: "Running mutmut mutation testing"},
    {content: "Create Cypress E2E tests for Workflows A/B/C", status: "in_progress", activeForm: "Creating Cypress E2E tests"},
    {content: "Fix WCAG 2.1 AA violations (axe-core)", status: "in_progress", activeForm: "Fixing WCAG violations"},
    {content: "Enhance Neo4j graph (search, filter, layouts)", status: "pending", activeForm: "Enhancing Neo4j graph"},
    {content: "Optimize PDF parsing (<60 sec for 100 pages)", status: "pending", activeForm: "Optimizing PDF parsing"},
    {content: "Optimize Neo4j queries (<2 sec for 10k nodes)", status: "pending", activeForm: "Optimizing Neo4j queries"},
    {content: "Implement structured logging (Winston/structlog)", status: "pending", activeForm: "Implementing structured logging"},
    {content: "Create Docker Compose setup (FastAPI/React/Neo4j)", status: "pending", activeForm: "Creating Docker Compose setup"},
    {content: "Run smoke tests in Docker containers", status: "pending", activeForm: "Running smoke tests in containers"}
  ]}
```

**Concurrent Agent Execution (Message 7)**:
```javascript
[Single Message - Phase 4 DevOps/Deployment]:
  Task("DevOps Engineer (A7)",
    "Implement structured logging: (1) Winston for FastAPI (JSON format), (2) console.log for React (development), (3) Sentry integration via MCP for production errors. Log: endpoints, Neo4j errors, API failures. Step 4.3.1",
    "cicd-engineer")

  Task("DevOps Engineer (A7)",
    "Create Docker Compose: (1) FastAPI service (port 8000), (2) React service (Nginx, port 3000), (3) Neo4j Community Edition (bolt://7687, http://7474). Include .env for NEO4J_USER, NEO4J_PASSWORD, API keys. Step 4.3.2",
    "cicd-engineer")

  Task("DevOps Engineer (A7)",
    "Write smoke tests: (1) Health check endpoints (/health, /docs), (2) Neo4j connectivity (CREATE/MATCH test node), (3) File upload (mock PDF). Run in CI/CD (GitHub Actions). Step 4.3.2",
    "cicd-engineer")

  Task("Unit Testing Engineer (A4)",
    "Final coverage report: Verify ≥90% critical (glossary/graph), ≥85% core, ≥75% UI. Generate HTML report (pytest-cov, Jest --coverage). Document uncovered edge cases. Phase 4 final validation",
    "tester")
```

**Milestone 4 Criteria**:
- [ ] Test coverage: ≥90% (PDF Parser, Neo4j Manager, sync logic), ≥85% (validation, translation, matching), ≥75% (React components)
- [ ] Mutation testing: ≥80% mutation score (mutmut)
- [ ] E2E Cypress: Workflow A (internal upload), Workflow B (gold standard import), Workflow C (full pipeline) all pass
- [ ] WCAG 2.1 AA: 0 axe-core violations (contrast ≥4.5:1, keyboard navigation, ARIA labels)
- [ ] Neo4j graph: Search by term name, filter by standard, 3 layout algorithms (force, hierarchical, radial)
- [ ] Performance: 100-page PDF parsed in <60 sec (chunked processing verified)
- [ ] Performance: Neo4j query for 10,000 nodes returns <2 sec (EXPLAIN shows index usage)
- [ ] Logging: All endpoints log to Winston (JSON), errors sent to Sentry
- [ ] Docker Compose: `docker-compose up` starts all services (FastAPI, React, Neo4j)
- [ ] Smoke tests: Health checks pass, Neo4j connectivity verified, mock upload succeeds
- [ ] CI/CD: GitHub Actions runs tests on PR, blocks merge if coverage <85%

---

## 4. Concurrent Execution Strategy

### 4.1 GOLDEN RULE (from CLAUDE.md)

**"1 MESSAGE = ALL RELATED OPERATIONS"**

All concurrent operations MUST be batched in a **single message**:
- ✅ **Task tool calls**: Spawn ALL agents for a phase in one message
- ✅ **TodoWrite**: Batch ALL todos (5-10+ items) in one call
- ✅ **File operations**: All reads/writes/edits together
- ✅ **Bash commands**: All terminal operations together

### 4.2 Correct Pattern Example

```javascript
// ✅ CORRECT: Single message with all Phase 1 initialization
[Message 1]:
  Task("Python Developer", "...", "backend-dev")
  Task("Database Engineer", "...", "code-analyzer")
  Task("Unit Testing Engineer", "...", "tester")
  TodoWrite { todos: [10 items...] }
  Bash "mkdir -p src/{backend,frontend,database,tests}"
  Write "src/backend/app.py"
  Write "src/database/models.py"
  Write "tests/conftest.py"
```

### 4.3 Wrong Pattern Example

```javascript
// ❌ WRONG: Multiple sequential messages
Message 1: Task("Python Developer", "...", "backend-dev")
Message 2: Task("Database Engineer", "...", "code-analyzer")  // BREAKS COORDINATION!
Message 3: TodoWrite { todos: [...] }
Message 4: Write "src/backend/app.py"
```

### 4.4 Agent Handoff Protocol

When agents complete interdependent tasks:

1. **Agent A1** completes FastAPI endpoints → Posts to memory via `post-edit` hook
2. **Agent A5** reads from memory → Uses endpoint schemas for React fetch calls
3. **Agent A3** waits for A1's DB models → Implements Neo4j sync based on SQLAlchemy schema

Memory keys: `swarm/[agent-id]/[step-id]` (e.g., `swarm/A1/step-1.1.1`)

---

## 5. Technology Decisions

### 5.1 Database Choice: SQLite (Recommended)

**Rationale**:
- ✅ Simpler setup (no separate DB server)
- ✅ Portable (single file, easy backups)
- ✅ Sufficient for 10,000 glossary entries (PRT limit)
- ✅ Python native support (sqlite3, SQLAlchemy)
- ❌ H2 only if Java ecosystem integration required (not applicable here)

**Decision**: Use **SQLite** for GlossaryEntry, GlossaryMatch, GlossaryVersion, TerminologyCache

### 5.2 Graph Visualization: vis.js (Recommended)

**Comparison**:

| Feature | vis.js | Reagraph |
|---------|--------|----------|
| Maturity | ✅ Stable, widely used | ⚠️ Newer library |
| Customization | ✅ Extensive (physics, clustering) | ✅ Good (React-native) |
| Performance | ✅ Handles 10,000+ nodes | ⚠️ Optimized for <5,000 nodes |
| React Integration | ⚠️ Requires wrapper | ✅ Native React components |
| Documentation | ✅ Comprehensive | ⚠️ Growing |

**Decision**: Use **vis.js** for Phase 2-3, consider Reagraph in future if React-native integration needed

### 5.3 State Management: React Context (Recommended)

**Rationale**:
- ✅ No external dependencies (built-in React)
- ✅ Sufficient for app state (current glossary, selected standard, UI settings)
- ✅ Easier testing (no Redux boilerplate)
- ❌ Redux/Zustand only if complex state mutations or time-travel debugging required

**Decision**: Use **React Context** for theme settings, user preferences, current workflow state

### 5.4 Neo4j Deployment: Docker (Recommended)

**Docker Compose Setup**:
```yaml
version: '3.8'
services:
  neo4j:
    image: neo4j:5.x-community
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=${NEO4J_USER}/${NEO4J_PASSWORD}
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
```

**Rationale**: Isolated environment, easy setup, consistent across dev/prod

---

## 6. Risk Mitigation

### 6.1 NLP Accuracy (<80% extraction rate)

**Mitigation**:
- ✅ Hybrid approach: NLP (spaCy) + rule-based (regex for structured sections)
- ✅ Manual review gate: Users validate extracted terms before matching
- ✅ Neo4j validation: Cross-check with SYNONYM relationships from gold standards
- ✅ Iterative improvement: Log failed extractions for model retraining

### 6.2 API Downtime (IATE, DeepL, IEC)

**Mitigation**:
- ✅ Offline mocks: Pytest fixtures with realistic API responses
- ✅ TerminologyCache: Pre-load NAMUR/DIN/ASME (50,000 terms) for offline validation
- ✅ Neo4j caching: Store previous API results as Term nodes
- ✅ Retry logic: 3 retries with exponential backoff (1s, 2s, 4s)
- ✅ Fallback: Manual input UI if all APIs fail

### 6.3 Neo4j Learning Curve

**Mitigation**:
- ✅ Use Neo4j Community Edition (free, well-documented)
- ✅ Claude-generated Cypher queries: Agents use PRT prompts for query construction
- ✅ Training: 2-day Neo4j basics workshop (Cypher, indexing, EXPLAIN)
- ✅ Templates: Pre-built Cypher queries for common operations (CREATE Term, MATCH SYNONYM)

### 6.4 Data Sync Failures (SQLite ↔ Neo4j)

**Mitigation**:
- ✅ Retry logic: If sync fails, retry 3x before alerting
- ✅ Monitoring: Log all sync operations (Winston/structlog)
- ✅ Idempotent sync: MERGE instead of CREATE (prevent duplicates)
- ✅ Manual resync: Admin UI button to force full SQLite → Neo4j resync

### 6.5 WCAG Compliance Gaps

**Mitigation**:
- ✅ axe-core integration: Run in Jest tests (Phase 2+)
- ✅ Manual audits: Use browser extensions (WAVE, Lighthouse) for visual checks
- ✅ Keyboard navigation: Test all UI flows without mouse
- ✅ Screen reader: Test with NVDA/JAWS for critical workflows

---

## 7. Quality Assurance

### 7.1 Test-Driven Development (TDD)

**Workflow** (every step in Section 18):
1. **Red**: Write failing test (pytest or Jest)
2. **Green**: Implement minimal code to pass test
3. **Refactor**: Optimize code, ensure tests still pass

**Example** (Step 1.1.1):
```python
# tests/test_app.py (RED)
def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

# src/backend/app.py (GREEN)
@app.get("/health")
def health():
    return {"status": "healthy"}

# (REFACTOR) - Add logging, environment checks
```

### 7.2 Coverage Targets

| Module Type | Coverage Target | Tools |
|-------------|-----------------|-------|
| Critical (glossary/graph integrity, sync) | ≥90% | pytest-cov, mutmut |
| Core logic (validation, translation, matching) | ≥85% | pytest-cov |
| UI components (React) | ≥75% | Jest --coverage |
| E2E workflows | 100% (all workflows) | Cypress |

### 7.3 Mutation Testing

**Tool**: mutmut (Python), Stryker (JavaScript)

**Target**: ≥80% mutation score (Phase 4)

**Process**:
1. Run mutmut: `mutmut run --paths-to-mutate=src/backend`
2. Identify surviving mutants (untested edge cases)
3. Add tests to kill mutants
4. Re-run until ≥80% mutation score

### 7.4 Accessibility Testing

**Tools**:
- **Automated**: axe-core (Jest integration), Lighthouse (CI/CD)
- **Manual**: WAVE browser extension, NVDA screen reader

**Checklist**:
- [ ] Contrast ratios ≥4.5:1 (WCAG 2.1 AA)
- [ ] Keyboard navigation (Tab, Enter, Esc work for all UI)
- [ ] ARIA labels (buttons, forms, graphs)
- [ ] Screen reader: All workflows completable without visuals

---

## 8. Deployment Strategy

### 8.1 Local Development

**Setup**:
```bash
# Backend
cd src/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload

# Frontend
cd src/frontend
npm install
npm start

# Neo4j (Docker)
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5-community
```

### 8.2 Docker Compose (Production)

**File**: `docker-compose.yml`
```yaml
version: '3.8'
services:
  backend:
    build: ./src/backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./glossary.db
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=${NEO4J_USER}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - DEEPL_API_KEY=${DEEPL_API_KEY}
    depends_on:
      - neo4j
    volumes:
      - ./data:/app/data

  frontend:
    build: ./src/frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=${NEO4J_USER}/${NEO4J_PASSWORD}
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs

volumes:
  neo4j_data:
  neo4j_logs:
```

**Deploy**:
```bash
# Set environment variables
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=secure_password
export DEEPL_API_KEY=your_key_here

# Start all services
docker-compose up -d

# Verify health
curl http://localhost:8000/health
curl http://localhost:3000
```

### 8.3 CI/CD Pipeline (GitHub Actions)

**File**: `.github/workflows/ci.yml`
```yaml
name: CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          cd src/backend
          pip install -r requirements.txt

      - name: Run pytest
        run: |
          cd src/backend
          pytest --cov=. --cov-report=html --cov-fail-under=85

      - name: Run mutmut
        run: |
          cd src/backend
          mutmut run --paths-to-mutate=src

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install frontend deps
        run: |
          cd src/frontend
          npm install

      - name: Run Jest
        run: |
          cd src/frontend
          npm test -- --coverage --coverageThreshold='{"global":{"lines":75}}'

      - name: Run Cypress E2E
        run: |
          cd src/frontend
          npm run cypress:run

      - name: Block merge if coverage < threshold
        run: |
          echo "Coverage check passed"
```

**Gate**: Merge blocked if:
- pytest coverage <85% (backend)
- Jest coverage <75% (frontend)
- Any Cypress E2E test fails
- mutmut mutation score <80%

---

## 9. Success Metrics

### 9.1 Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Test Coverage** | ≥90% (critical), ≥85% (core), ≥75% (UI) | pytest-cov, Jest --coverage |
| **Mutation Score** | ≥80% | mutmut, Stryker |
| **PDF Parsing Speed** | <60 sec (100 pages) | pytest-benchmark |
| **Neo4j Query Speed** | <2 sec (10k nodes) | Cypher EXPLAIN, timing logs |
| **WCAG Compliance** | 0 violations (AA) | axe-core, Lighthouse |
| **NLP Extraction Rate** | ≥80% accuracy | Manual validation (100 samples) |
| **API Uptime** | ≥99% (with cache fallback) | Sentry error logs |

### 9.2 User Experience Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Workflow Completion Time** | <10 min (after 30-min tutorial) | User testing (5 participants) |
| **Inconsistency Detection** | ≥90% flagged correctly | Manual review (100 pairs) |
| **Gold Standard Match Rate** | ≥90% (NAMUR/DIN/ASME priority) | Validation against source docs |
| **Export Format Validity** | 100% (TBX ISO 30042 compliant) | xmllint schema validation |
| **Graph Visualization Usability** | 4.5/5 rating | User survey (SUS score) |

### 9.3 Project Metrics

| Metric | Target | Status |
|--------|--------|--------|
| **Timeline** | 10 weeks (4 phases) | On track (Gantt chart) |
| **Agent Utilization** | 8 agents, ≥80% concurrent execution | Monitor via TodoWrite completion rates |
| **Code Quality** | 0 critical Sonar issues | SonarQube scans |
| **Documentation** | 100% API endpoints documented | Swagger/OpenAPI validation |
| **Deployment Success** | <5 min Docker Compose startup | Smoke tests in CI/CD |

---

## Appendix A: File Organization

Following CLAUDE.md requirements (no root folder saves):

```
/src
  /backend
    app.py                    # FastAPI main
    models.py                 # SQLAlchemy models
    /modules
      pdf_parser.py           # PDF extraction
      tbx_parser.py           # TBX extraction
      nlp_extractor.py        # spaCy term extraction
      validator.py            # Validation logic
      translator.py           # DeepL integration
      matcher.py              # Bilingual matching
      graph_manager.py        # Neo4j sync
    requirements.txt
  /frontend
    /src
      App.jsx                 # Main React component
      /components
        ValidationView.jsx    # Term validation UI
        SettingsUI.jsx        # Settings (logo, gold standards)
        GraphVisualization.jsx # Neo4j graph (vis.js)
        ComparisonView.jsx    # Bilingual comparison
    package.json
  /database
    neo4j_schema.cypher       # Neo4j constraints/indexes
    sqlite_init.sql           # SQLite schema
/tests
  /unit
    test_pdf_parser.py
    test_nlp_extractor.py
    test_validator.py
  /integration
    test_api_endpoints.py
    test_neo4j_sync.py
  /e2e
    test_workflow_a.spec.js   # Cypress: Internal upload
    test_workflow_b.spec.js   # Cypress: Gold standard import
    test_workflow_c.spec.js   # Cypress: Full pipeline
  conftest.py                 # Pytest fixtures
/docs
  PRT-v2.0.md                 # Original PRT
  PRT-v2.1.md                 # Updated PRT
  PRT-CHANGELOG.md            # Version changes
  IMPLEMENTATION-STRATEGY.md  # This document
  API.md                      # API documentation
/config
  .env.example                # Environment variables template
  docker-compose.yml          # Docker orchestration
/scripts
  setup.sh                    # Initial setup script
  resync_neo4j.py             # Manual SQLite→Neo4j resync
```

---

## Appendix B: Agent Spawn Commands

### Phase 1 - Message 1
```javascript
Task("Python Developer (A1)", "TDD: Write pytest for /health, then initialize FastAPI with SQLAlchemy (GlossaryEntry, TerminologyCache), neo4j-driver. Steps 1.1.1-1.1.2", "backend-dev")
Task("Database Engineer (A3)", "TDD: Write schema tests, then setup SQLite (GlossaryEntry, TerminologyCache, GlossaryMatch, GlossaryVersion) and Neo4j (UNIQUE on Term.id, Standard.id). Step 1.1.2", "code-analyzer")
Task("Unit Testing Engineer (A4)", "Create pytest framework with Neo4j/DeepL/IATE mocks. Setup coverage (≥80%). Configure mutmut. Phase 1 tests", "tester")
TodoWrite { todos: [10 items from Phase 1...] }
Bash "mkdir -p src/{backend,frontend,database,tests,config,scripts}"
Write "src/backend/app.py"
Write "src/backend/models.py"
Write "src/database/neo4j_schema.cypher"
Write "tests/conftest.py"
```

### Phase 2 - Message 3
```javascript
Task("Python Developer (A1)", "TDD: Write /validate-term tests with mocks, then implement validation with TerminologyCache/Neo4j priority. Steps 2.1.1", "backend-dev")
Task("Integration Engineer (A6)", "TDD: Write API client tests, then implement IATE/IEC clients with TerminologyCache fallback. Step 2.1.2", "api-docs")
Task("Python Developer (A1)", "TDD: Write translation tests, then implement DeepL with gold standard fallback. Steps 2.2.1-2.2.2", "backend-dev")
Task("Unit Testing Engineer (A4)", "Expand pytest for validation/translation. Target ≥85% coverage. Phase 2 tests", "tester")
TodoWrite { todos: [8 items from Phase 2...] }
```

(Continue for Phase 3 Message 5, Phase 4 Message 6-7...)

---

**End of Implementation Strategy v1.0**

**Ready to proceed?** Review this strategy, then begin Phase 1 concurrent agent execution.
