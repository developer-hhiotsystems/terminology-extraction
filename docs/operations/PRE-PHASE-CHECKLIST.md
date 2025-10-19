# Pre-Phase Checklist: Week 0 Setup

**Project**: Glossary Extraction & Validation App
**Version**: 1.0 (for PRT v2.2)
**Date**: October 16, 2025
**Duration**: 0.5 weeks (2.5 days)
**Purpose**: Prepare all prerequisites before Phase 1 implementation begins

---

## Overview

This checklist ensures all 8 agents have the tools, knowledge, and resources needed to begin concurrent development in Phase 1. **No agent should start Phase 1 work until all items are completed.**

**Why Pre-Phase Matters**:
- Prevents blocked agents (e.g., A3 can't optimize Neo4j without Cypher knowledge)
- Ensures measurable NLP accuracy (ground truth corpus required)
- Enables offline development (IATE cached dataset, backup scripts)
- Establishes security baseline (Docker secrets, WAL mode)

---

## ✅ Checklist Items

### 1. NLP Ground Truth Corpus Creation

**Owner**: Agent A2 (NLP Specialist)
**Duration**: 1 day
**Tools**: NAMUR/DIN/ASME PDF samples, text editor, spaCy

**Task**:
1. Collect 50 German + 50 English sample documents (NAMUR/DIN/ASME excerpts or similar technical standards)
2. Manually read each document and annotate 500 term-definition pairs (250 German, 250 English)
3. Store annotations in `tests/fixtures/nlp_ground_truth.json` with format:
   ```json
   {
     "samples": [
       {
         "document": "namur_sample_01.pdf",
         "language": "de",
         "terms": [
           {
             "term": "Druckbehälter",
             "definition": "Ein Behälter zur Aufnahme von Gasen oder Flüssigkeiten unter Druck"
           },
           {
             "term": "Ventil",
             "definition": "Eine Armatur zum Steuern von Durchfluss"
           }
         ]
       },
       {
         "document": "din_sample_01.pdf",
         "language": "en",
         "terms": [
           {
             "term": "Pressure Vessel",
             "definition": "A container designed to hold gases or liquids at pressure"
           }
         ]
       }
     ]
   }
   ```
4. Validate JSON structure (no syntax errors)
5. Commit file to Git: `git add tests/fixtures/nlp_ground_truth.json && git commit -m "Add NLP ground truth corpus (500 pairs)"`

**Acceptance Criteria**:
- [ ] File `tests/fixtures/nlp_ground_truth.json` exists
- [ ] Contains exactly 500 term-definition pairs (250 German, 250 English)
- [ ] All terms have non-empty `term` and `definition` fields
- [ ] JSON is valid (no syntax errors)
- [ ] Documents represent realistic technical standards (NAMUR/DIN/ASME style)

**Rationale**: Enables characterization testing for NLP extraction (Step 1.3.1). Without this, A2 cannot write tests with measurable F1 score target (≥75%).

---

### 2. Neo4j Bootcamp Completion

**Owner**: Agent A3 (Database Engineer)
**Duration**: 1 day (8 hours)
**Tools**: Neo4j GraphAcademy (https://graphacademy.neo4j.com/)

**Task**:
1. Complete **"Neo4j Fundamentals"** course (3 hours):
   - Graph database concepts (nodes, relationships, properties)
   - Cypher query language basics (CREATE, MATCH, MERGE)
   - Indexes and constraints (UNIQUE, performance optimization)
2. Complete **"Cypher Query Tuning"** course (2 hours):
   - EXPLAIN and PROFILE commands
   - Index usage patterns
   - Query optimization for 10,000+ nodes
3. Complete **"Python Driver" tutorial** (1 hour):
   - Connect to Neo4j via `neo4j-driver`
   - Execute Cypher queries from Python
   - Transaction management
4. Document learnings in `docs/NEO4J-BOOTCAMP-NOTES.md`:
   - Key Cypher patterns for this project (CREATE Term, MERGE relationships, MATCH with pagination)
   - Performance tips (when to use indexes, EXPLAIN analysis)
   - Common errors and solutions
5. Create sample queries file `database/sample_queries.cypher`:
   ```cypher
   // Create Term node
   CREATE (t:Term {id: 1, term: 'Ventil', definition: 'Eine Armatur...', language: 'de'})

   // Query terms by language (using index)
   MATCH (t:Term) WHERE t.language = 'de' RETURN t

   // Paginated query (500 nodes)
   MATCH (t:Term)-[r:DEFINED_BY]->(s:Standard)
   RETURN t, r, s
   SKIP 0 LIMIT 500
   ```

**Acceptance Criteria**:
- [ ] A3 completes all 3 courses (certificates or screenshots)
- [ ] File `docs/NEO4J-BOOTCAMP-NOTES.md` exists with ≥500 words
- [ ] File `database/sample_queries.cypher` exists with ≥5 example queries
- [ ] A3 can explain: (1) When to use MERGE vs CREATE, (2) How to optimize queries with EXPLAIN, (3) How to create indexes
- [ ] A3 successfully connects to local Neo4j from Python and runs test query

**Rationale**: Prevents Neo4j learning curve delays in Phase 1. A3 needs Cypher fluency for Steps 1.1.2, 1.3.2, 2.3.4.

---

### 3. IATE Dataset Download

**Owner**: Agent A6 (Integration Engineer)
**Duration**: 0.5 days
**Tools**: Web browser, wget/curl

**Task**:
1. Navigate to https://iate.europa.eu/download-iate
2. Download latest **TBX export** (or CSV if TBX unavailable):
   - File size: Expect ~500MB-2GB compressed
   - Language pair: German-English (de-en)
3. Extract to `data/iate/` directory:
   ```bash
   mkdir -p data/iate
   cd data/iate
   wget https://iate.europa.eu/download/.../iate_export.tbx.zip
   unzip iate_export.tbx.zip
   ```
4. Verify extraction:
   ```bash
   file iate_export.tbx  # Should show "XML document text"
   head -n 50 iate_export.tbx  # Preview first 50 lines
   ```
5. Document import procedure in `docs/IATE-IMPORT-GUIDE.md`:
   - Download URL and date
   - File format (TBX or CSV)
   - Expected term count (estimate: 8 million multilingual entries, ~500k German-English pairs)
   - Import command for Step 2.1.2 (will be implemented later)
6. Add `.gitignore` entry:
   ```bash
   echo "data/iate/*.tbx" >> .gitignore
   echo "data/iate/*.csv" >> .gitignore
   ```

**Acceptance Criteria**:
- [ ] Directory `data/iate/` exists
- [ ] IATE dataset file (TBX or CSV) downloaded and extracted
- [ ] File `docs/IATE-IMPORT-GUIDE.md` exists with download URL, date, format, estimated term count
- [ ] File is valid XML (TBX) or CSV (no corruption)
- [ ] .gitignore excludes large IATE files from version control

**Rationale**: Enables offline validation in Phase 2 (Step 2.1.2). Without cached IATE dataset, A6 cannot implement validation logic.

---

### 4. Local Neo4j Setup

**Owner**: Agent A7 (DevOps Engineer)
**Duration**: 0.5 days
**Tools**: Docker, docker-compose

**Task**:
1. Pull Neo4j Community Edition image:
   ```bash
   docker pull neo4j:5-community
   ```
2. Create `docker-compose.neo4j-dev.yml` for local development:
   ```yaml
   version: '3.8'
   services:
     neo4j:
       image: neo4j:5-community
       ports:
         - "7474:7474"  # HTTP (Neo4j Browser)
         - "7687:7687"  # Bolt (Python driver)
       environment:
         - NEO4J_AUTH=neo4j/devpassword
         - NEO4J_dbms_memory_heap_max__size=2G
         - NEO4J_dbms_memory_pagecache_size=1G
       volumes:
         - neo4j_dev_data:/data
         - neo4j_dev_logs:/logs
       healthcheck:
         test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "devpassword", "RETURN 1"]
         interval: 10s
         timeout: 5s
         retries: 5

   volumes:
     neo4j_dev_data:
     neo4j_dev_logs:
   ```
3. Start Neo4j:
   ```bash
   docker-compose -f docker-compose.neo4j-dev.yml up -d
   ```
4. Verify Neo4j running:
   - Open browser: http://localhost:7474
   - Login: neo4j / devpassword
   - Run test query: `RETURN 1`
5. Test Python connection:
   ```python
   from neo4j import GraphDatabase

   driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "devpassword"))
   with driver.session() as session:
       result = session.run("RETURN 1 AS num")
       print(result.single()["num"])  # Should print: 1
   driver.close()
   ```

**Acceptance Criteria**:
- [ ] File `docker-compose.neo4j-dev.yml` exists
- [ ] Neo4j container running (check: `docker ps | grep neo4j`)
- [ ] Neo4j Browser accessible at http://localhost:7474
- [ ] Health check passes (cypher-shell returns 1)
- [ ] Python `neo4j-driver` successfully connects and runs query

**Rationale**: Required for all Phase 1+ work involving Neo4j (Steps 1.1.2, 1.3.2, 2.3.4, etc.). Without local instance, A3 cannot develop/test Cypher queries.

---

### 5. Dependency Installation

**Owner**: Agent A7 (DevOps Engineer)
**Duration**: 0.5 days
**Tools**: pip, npm

**Task**:
1. Create `requirements.txt` (Python backend):
   ```txt
   fastapi==0.104.1
   uvicorn==0.24.0
   sqlalchemy==2.0.23
   neo4j==5.14.0
   pdfplumber==0.10.3
   pytesseract==0.3.10
   pdf2image==1.16.3
   lxml==4.9.3
   spacy==3.7.2
   deepl==1.16.0
   python-Levenshtein==0.23.0
   jellyfish==1.0.3
   pact-python==2.0.1
   pytest==7.4.3
   pytest-cov==4.1.0
   mutmut==2.4.4
   sentry-sdk==1.38.0
   ```
2. Install Python dependencies:
   ```bash
   cd src/backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python -m spacy download de_core_news_sm  # German NLP model
   python -m spacy download en_core_web_sm  # English NLP model
   ```
3. Create `package.json` (React frontend):
   ```json
   {
     "name": "glossary-app-frontend",
     "version": "1.0.0",
     "dependencies": {
       "react": "^18.2.0",
       "react-dom": "^18.2.0",
       "@mui/material": "^5.14.18",
       "@emotion/react": "^11.11.1",
       "@emotion/styled": "^11.11.0",
       "react-dropzone": "^14.2.3",
       "vis-network": "^9.1.9",
       "axios": "^1.6.2"
     },
     "devDependencies": {
       "@pact-foundation/pact": "^12.1.0",
       "jest": "^29.7.0",
       "@testing-library/react": "^14.1.2",
       "cypress": "^13.6.0",
       "axe-core": "^4.8.3"
     }
   }
   ```
4. Install Node dependencies:
   ```bash
   cd src/frontend
   npm install
   ```
5. Verify installations:
   ```bash
   # Python
   python -c "import fastapi, neo4j, pdfplumber, spacy, deepl; print('Python deps OK')"

   # Node
   npm list react @mui/material cypress
   ```

**Acceptance Criteria**:
- [ ] File `requirements.txt` exists with all 16+ packages
- [ ] File `package.json` exists with all dependencies
- [ ] Python venv created, all packages installed (no errors)
- [ ] spaCy German and English models downloaded
- [ ] Node modules installed (no errors)
- [ ] Import test commands succeed (Python and Node)

**Rationale**: Prevents "missing package" errors during Phase 1. All agents need these dependencies to run their code.

---

### 6. SQLite Backup Script

**Owner**: Agent A7 (DevOps Engineer)
**Duration**: 0.5 days
**Tools**: bash, cron, sqlite3

**Task**:
1. Create `scripts/backup_sqlite.sh`:
   ```bash
   #!/bin/bash
   # SQLite Backup Script - Runs daily at 2 AM via cron
   # Retention: 30 days

   BACKUP_DIR="/backups/sqlite"
   DATE=$(date +%Y%m%d_%H%M%S)
   DB_PATH="/app/data/glossary.db"
   CACHE_DB_PATH="/app/data/cache.db"

   # Create backup directory
   mkdir -p $BACKUP_DIR

   # Backup glossary database
   if [ -f "$DB_PATH" ]; then
       sqlite3 "$DB_PATH" ".backup $BACKUP_DIR/glossary_$DATE.db"
       echo "[$(date)] Glossary DB backed up: $BACKUP_DIR/glossary_$DATE.db"
   else
       echo "[$(date)] ERROR: $DB_PATH not found"
   fi

   # Backup cache database
   if [ -f "$CACHE_DB_PATH" ]; then
       sqlite3 "$CACHE_DB_PATH" ".backup $BACKUP_DIR/cache_$DATE.db"
       echo "[$(date)] Cache DB backed up: $BACKUP_DIR/cache_$DATE.db"
   fi

   # Remove backups older than 30 days
   find $BACKUP_DIR -name "*.db" -mtime +30 -delete
   echo "[$(date)] Old backups cleaned (retention: 30 days)"

   # Optional: Upload to S3
   # aws s3 cp $BACKUP_DIR/glossary_$DATE.db s3://glossary-backups/
   ```
2. Make executable:
   ```bash
   chmod +x scripts/backup_sqlite.sh
   ```
3. Test backup script:
   ```bash
   # Create dummy database
   mkdir -p /app/data
   sqlite3 /app/data/glossary.db "CREATE TABLE test (id INTEGER);"

   # Run backup
   ./scripts/backup_sqlite.sh

   # Verify backup created
   ls -lh /backups/sqlite/
   ```
4. Test restore procedure:
   ```bash
   # Restore from backup
   LATEST_BACKUP=$(ls -t /backups/sqlite/glossary_*.db | head -n 1)
   cp "$LATEST_BACKUP" /app/data/glossary_restored.db

   # Verify restore
   sqlite3 /app/data/glossary_restored.db "SELECT name FROM sqlite_master WHERE type='table';"
   ```
5. Document in `docs/BACKUP-RESTORE-GUIDE.md`:
   - Backup schedule (daily at 2 AM)
   - Retention policy (30 days)
   - Manual backup command
   - Restore procedure

**Acceptance Criteria**:
- [ ] File `scripts/backup_sqlite.sh` exists and is executable
- [ ] Script runs without errors on test database
- [ ] Backup file created in `/backups/sqlite/` directory
- [ ] Restore procedure tested and documented
- [ ] File `docs/BACKUP-RESTORE-GUIDE.md` exists with clear instructions

**Rationale**: Prevents data loss. Critical for production deployment (Step 4.3.2). Weekly restore tests ensure backups are valid.

---

### 7. Docker Secrets Generation

**Owner**: Agent A7 (DevOps Engineer)
**Duration**: 0.25 days
**Tools**: Docker, openssl

**Task**:
1. Generate NEO4J_PASSWORD secret:
   ```bash
   # Generate strong password
   NEO4J_PASS=$(openssl rand -base64 32)
   echo "$NEO4J_PASS" | docker secret create neo4j_password -
   ```
2. Generate DEEPL_API_KEY secret:
   ```bash
   # Use actual DeepL API key (free tier: https://www.deepl.com/pro-api)
   # For development, use placeholder
   echo "YOUR_DEEPL_API_KEY_HERE" | docker secret create deepl_api_key -
   ```
3. Verify secrets created:
   ```bash
   docker secret ls
   # Should show: neo4j_password, deepl_api_key
   ```
4. Document in `.env.example`:
   ```bash
   # .env.example
   # DO NOT commit actual values to Git!

   # Neo4j Configuration
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=<use_docker_secret_or_set_here_for_dev>

   # DeepL API Configuration
   DEEPL_API_KEY=<get_from_https://www.deepl.com/pro-api>

   # SQLite Configuration
   DATABASE_URL=sqlite:///./data/glossary.db

   # Application Configuration
   LOG_LEVEL=INFO
   SENTRY_DSN=<optional_for_error_tracking>
   ```
5. Add to `.gitignore`:
   ```bash
   echo ".env" >> .gitignore
   echo "*.db" >> .gitignore
   echo "/backups/" >> .gitignore
   ```

**Acceptance Criteria**:
- [ ] Docker secrets `neo4j_password` and `deepl_api_key` created
- [ ] `docker secret ls` shows both secrets
- [ ] File `.env.example` exists with all environment variables documented
- [ ] `.gitignore` excludes `.env`, `*.db`, `/backups/`
- [ ] Documentation explains: (1) How to generate secrets, (2) How backend reads secrets from files

**Rationale**: Security best practice. Prevents password exposure in `docker inspect` (Section 9 fix from v2.2). Required for Step 4.3.2.

---

### 8. Environment Variables Documentation

**Owner**: Agent A7 (DevOps Engineer)
**Duration**: 0.25 days
**Tools**: Text editor

**Task**:
1. Create comprehensive `.env.example` (completed in Task 7)
2. Create `docs/ENVIRONMENT-VARIABLES.md`:
   ```markdown
   # Environment Variables Reference

   ## Required Variables

   ### NEO4J_USER
   - **Description**: Neo4j database username
   - **Default**: `neo4j`
   - **Example**: `NEO4J_USER=neo4j`

   ### NEO4J_PASSWORD
   - **Description**: Neo4j database password (read from Docker secret)
   - **Default**: None (must be set)
   - **Docker Secret**: Use `NEO4J_PASSWORD_FILE=/run/secrets/neo4j_password`
   - **Local Dev**: Set directly in `.env`

   ### DEEPL_API_KEY
   - **Description**: DeepL translation API key
   - **How to Get**: Sign up at https://www.deepl.com/pro-api (500k chars/month free)
   - **Docker Secret**: Use `DEEPL_API_KEY_FILE=/run/secrets/deepl_api_key`
   - **Local Dev**: Set directly in `.env`

   ### DATABASE_URL
   - **Description**: SQLite database path
   - **Default**: `sqlite:///./data/glossary.db`
   - **Example**: `DATABASE_URL=sqlite:///./data/glossary.db`

   ## Optional Variables

   ### LOG_LEVEL
   - **Description**: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
   - **Default**: `INFO`

   ### SENTRY_DSN
   - **Description**: Sentry error tracking DSN (optional)
   - **Default**: None (error tracking disabled)

   ## Docker Secrets Pattern

   Backend reads secrets from files:
   \`\`\`python
   def read_secret(secret_name: str) -> str:
       secret_file = os.getenv(f"{secret_name}_FILE")
       if secret_file and os.path.exists(secret_file):
           with open(secret_file) as f:
               return f.read().strip()
       return os.getenv(secret_name)
   \`\`\`
   ```

**Acceptance Criteria**:
- [ ] File `docs/ENVIRONMENT-VARIABLES.md` exists with ≥200 words
- [ ] All required variables documented (NEO4J_USER, NEO4J_PASSWORD, DEEPL_API_KEY, DATABASE_URL)
- [ ] Docker secrets pattern explained with code example
- [ ] "How to Get" instructions provided for DeepL API key

**Rationale**: Prevents confusion during deployment. All agents need to know which environment variables are required and where to get credentials.

---

### 9. PRT v2.2 Review & Approval

**Owner**: Agent A8 (Project Coordinator)
**Duration**: 0.5 days
**Tools**: Text editor, diff tool

**Task**:
1. Read `docs/PRT-v2.2.md` (full document, all 27 sections)
2. Review changes from v2.1 (see `docs/PRT-CHANGELOG.md` for summary)
3. Verify critical fixes integrated:
   - [ ] SyncLog table for sync failure tracking (Section 9)
   - [ ] UploadedDocument table for file metadata (Section 9)
   - [ ] pdfplumber for PDF parsing (Section 7)
   - [ ] IATE cached dataset approach (Section 7, Step 2.1.2)
   - [ ] DeepL caching (Section 9, Step 2.2.1)
   - [ ] ProgressIndicator component (Section 10)
   - [ ] WCAG-compliant theme overrides (Step 2.3.1)
   - [ ] Neo4j pagination (Step 2.3.4)
   - [ ] Docker health checks and secrets (Section 9)
   - [ ] Characterization testing for NLP (Step 1.3.1)
   - [ ] Pre-Phase Checklist (Section 23)
4. Check for ambiguities or missing information:
   - Can each step be implemented without additional research?
   - Are all Claude prompts clear and actionable?
   - Are acceptance criteria measurable?
5. Approve PRT v2.2:
   - If no issues: Create approval file `docs/PRT-v2.2-APPROVED.md` with date/signature
   - If issues: Document in `docs/PRT-v2.2-REVIEW-NOTES.md`, request clarifications

**Acceptance Criteria**:
- [ ] A8 has read full PRT v2.2 document (all 27 sections)
- [ ] All 10 critical fixes verified present
- [ ] File `docs/PRT-v2.2-APPROVED.md` created (or review notes if issues found)
- [ ] No blocking ambiguities remain

**Rationale**: Ensures all agents are working from the same, approved specification. Prevents scope creep and conflicting implementations.

---

### 10. IMPLEMENTATION-STRATEGY v1.1 Review & Approval

**Owner**: Agent A8 (Project Coordinator)
**Duration**: 0.5 days
**Tools**: Text editor

**Task**:
1. Read `docs/IMPLEMENTATION-STRATEGY-v1.1.md` (full document)
2. Verify 12-week timeline breakdown:
   - Pre-Phase: 0.5 weeks
   - Phase 1: 2 weeks
   - Phase 2: 4 weeks
   - Phase 3: 2.5 weeks
   - Phase 4: 3 weeks
3. Check agent assignments:
   - Are all 8 agents (A1-A8) assigned to appropriate tasks?
   - Are concurrent execution examples correct?
   - Do TodoWrite batches include 5-10+ items?
4. Verify milestone criteria align with PRT v2.2 acceptance criteria
5. Check technology decisions:
   - SQLite confirmed (not H2)
   - vis.js recommended for graph visualization
   - React Context for state management
6. Approve strategy:
   - Create `docs/IMPLEMENTATION-STRATEGY-v1.1-APPROVED.md`

**Acceptance Criteria**:
- [ ] A8 has read full IMPLEMENTATION-STRATEGY v1.1 document
- [ ] 12-week timeline verified (matches PRT v2.2 Section 12)
- [ ] All agent assignments reviewed
- [ ] File `docs/IMPLEMENTATION-STRATEGY-v1.1-APPROVED.md` created
- [ ] No blocking concerns remain

**Rationale**: Ensures realistic timeline and proper agent coordination. Prevents timeline underestimation and phase delays.

---

## 📊 Progress Tracking

**Status**: Use checkboxes above to track completion

**Team Coordination**:
- A2, A3, A6, A7 work in parallel (Tasks 1-7)
- A8 reviews after all technical tasks done (Tasks 9-10)
- Daily standup: Each agent reports completion status

**Risk Mitigation**:
- If Task 3 (IATE download) fails due to website downtime: Use cached sample dataset (50k terms) as temporary placeholder
- If Task 2 (Neo4j bootcamp) delayed: A3 can start with Neo4j documentation, complete courses asynchronously
- If Task 1 (ground truth corpus) incomplete: Use smaller corpus (250 pairs) for initial development, expand later

---

## 🚀 Ready to Start Phase 1?

**Checklist Summary**:
- [ ] All 10 tasks completed (checkboxes above)
- [ ] All files committed to Git
- [ ] Neo4j running locally (http://localhost:7474 accessible)
- [ ] Python and Node dependencies installed
- [ ] Backup script tested and documented
- [ ] PRT v2.2 and IMPLEMENTATION-STRATEGY v1.1 approved

**Next Steps**:
1. **Message 1 (Phase 1)**: Spawn agents A1, A3, A4 concurrently for Phase 1 initialization (see IMPLEMENTATION-STRATEGY v1.1 Section 3.2)
2. **TodoWrite**: Batch all Phase 1 todos in one call
3. **File operations**: Create all skeleton files in parallel

**If Not Ready**:
- Identify blocking tasks (tasks with most checkboxes unchecked)
- Assign additional resources to complete blockers
- Escalate to A8 if external dependencies blocked (e.g., IATE website down)

---

**End of Pre-Phase Checklist**

**Last Updated**: October 16, 2025
**Version**: 1.0 (for PRT v2.2)
