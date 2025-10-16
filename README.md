# Glossary Extraction & Validation Application

**Status**: Phase 1 Ready ✓
**Version**: 1.0.0
**Last Updated**: October 16, 2025

> **🚀 New to this project?** Start here: **[START-HERE.md](START-HERE.md)**
>
> **💼 Setting up on company computer?** Follow: **[VSCODE-FOOLPROOF-GUIDE.md](VSCODE-FOOLPROOF-GUIDE.md)**
>
> **⚡ Need quick reference?** Use: **[QUICK-REFERENCE-CARD.md](QUICK-REFERENCE-CARD.md)**

---

## Overview

A comprehensive glossary extraction and validation application that automatically extracts terminology from PDF documents, validates against IATE (Inter-Active Terminology for Europe), and provides interactive graph-based exploration.

### Key Features
- PDF terminology extraction with NLP
- IATE terminology validation
- Interactive graph visualization (Neo4j)
- Multi-language translation support (DeepL)
- WCAG 2.1 AA compliant UI
- SQLite + Neo4j dual storage
- Comprehensive test coverage

## Quick Start

### Prerequisites Met ✓
- Python 3.13.9
- Node.js v22.18.0
- Virtual environment with 39 packages
- 1,764 npm packages installed

### Start Development

**Backend (Terminal 1):**
```bash
cd "C:\Users\devel\Coding Projects\Glossary APP"
.\venv\Scripts\activate
python src\backend\app.py
```
Visit: http://localhost:8000/health

**Frontend (Terminal 2):**
```bash
cd "C:\Users\devel\Coding Projects\Glossary APP"
npm start
```
Visit: http://localhost:3000

**Tests (Terminal 3):**
```bash
.\venv\Scripts\activate
pytest tests/ -v --cov
```

## Setup Status

### ✅ Completed (Phase 1 Ready)
- [x] Project structure created
- [x] Python backend environment (39 packages)
- [x] Node.js frontend environment (1,764 packages)
- [x] Configuration files (.env, docker-compose.yml)
- [x] Skeleton application code
- [x] Unit tests (6 passed, 1 skipped)
- [x] Verification scripts
- [x] Comprehensive documentation

### ⚠️ Optional (Phase 2 Prerequisites)
- [ ] C++ Build Tools (for spaCy, lxml)
- [ ] Docker Desktop (for Neo4j)
- [ ] DeepL API key
- [ ] IATE dataset (~500 MB)

**Run to check status:**
```bash
.\venv\Scripts\python setup-check.py
```

## Automated Setup Scripts

### Master Setup Wizard
```powershell
.\scripts\complete-setup.ps1
```
Guides you through all remaining setup tasks.

### Individual Scripts

**C++ Build Tools:**
```powershell
.\scripts\install-cpp-tools.ps1
```

**Docker & Neo4j:**
```powershell
.\scripts\setup-docker.ps1
```

**DeepL API:**
```bash
.\venv\Scripts\python scripts\configure-deepl.py
```

**IATE Dataset:**
```bash
.\venv\Scripts\python scripts\download-iate.py
```

**SQLite Backup:**
```bash
.\venv\Scripts\python scripts\backup-sqlite.py backup
```

**Neo4j Initialization:**
```bash
.\venv\Scripts\python scripts\init-neo4j.py
```

## Project Structure

```
Glossary APP/
├── src/
│   ├── backend/          # FastAPI application
│   │   ├── modules/      # Feature modules (Phase 1+)
│   │   ├── app.py        # Main application
│   │   └── config.py     # Configuration
│   └── frontend/         # React application
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   ├── App.js    # WCAG-compliant theme
│       │   └── index.js
│       └── public/
├── tests/
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── e2e/             # Cypress E2E tests (Phase 3)
├── data/
│   ├── iate/           # IATE dataset
│   ├── uploads/        # User uploaded PDFs
│   └── glossary.db     # SQLite database
├── backups/
│   ├── sqlite/         # Database backups
│   └── neo4j/          # Graph database backups
├── scripts/            # Utility scripts
├── docs/               # Documentation
└── venv/              # Python virtual environment
```

## Documentation

### Setup Guides (Start Here!)

| Document | Best For | Time |
|----------|----------|------|
| **[START-HERE.md](START-HERE.md)** ⭐ | Master index - choose your guide | 2 min |
| **[VSCODE-FOOLPROOF-GUIDE.md](VSCODE-FOOLPROOF-GUIDE.md)** | Step-by-step setup (beginners) | 20-30 min |
| **[QUICK-START.md](QUICK-START.md)** | Quick setup (intermediate) | 10-15 min |
| **[QUICK-REFERENCE-CARD.md](QUICK-REFERENCE-CARD.md)** | Commands only (experts) | 5-10 min |
| **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** | Error solutions | As needed |

### VS Code Setup

| Document | Purpose |
|----------|---------|
| [docs/VSCODE-SETUP.md](docs/VSCODE-SETUP.md) | Complete VS Code guide |
| [docs/EXTENSIONS-SUMMARY.md](docs/EXTENSIONS-SUMMARY.md) | Extension reference |
| [docs/COMPANY-COMPUTER-SETUP.md](docs/COMPANY-COMPUTER-SETUP.md) | Company environment |

### Technical Documentation

| Document | Purpose |
|----------|---------|
| [PRT-v2.2.md](docs/PRT-v2.2.md) | Product requirements |
| [IMPLEMENTATION-STRATEGY-v1.1.md](docs/IMPLEMENTATION-STRATEGY-v1.1.md) | 12-week roadmap |
| [docs/NO-DOCKER-SETUP.md](docs/NO-DOCKER-SETUP.md) | No-Docker architecture |
| [REMAINING-SETUP-TASKS.md](docs/REMAINING-SETUP-TASKS.md) | Phase 2 prerequisites |

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Database**: SQLite (WAL mode) + Neo4j 5
- **PDF Processing**: pdfplumber 0.10.3
- **NLP**: spaCy 3.7.2 (Phase 2)
- **Translation**: DeepL API 1.19.1
- **Testing**: pytest 7.4.3, mutmut 2.4.4

### Frontend
- **Framework**: React 18.3.1
- **UI Library**: Material-UI 5.18.0 (WCAG 2.1 AA)
- **Graph Viz**: vis-network 9.1.9
- **Testing**: Cypress 13.17.0, Pact

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Database**: Neo4j Community Edition (Docker)
- **Version Control**: Git

## Development Workflow

### Phase 1: Core Infrastructure (Weeks 1-2) ✓ Ready
- SQLite schema design
- FastAPI CRUD endpoints
- React file upload UI
- Unit test framework

**Can start immediately!**

### Phase 2: NLP & Extraction (Weeks 3-6)
**Prerequisites needed:**
- C++ Build Tools → `.\scripts\install-cpp-tools.ps1`
- Docker + Neo4j → `.\scripts\setup-docker.ps1`
- IATE dataset → `.\venv\Scripts\python scripts\download-iate.py`

### Phase 3: Validation & UX (Weeks 7-9.5)
- DeepL API → `.\venv\Scripts\python scripts\configure-deepl.py`
- Mutation testing
- Contract testing (Pact)

### Phase 4: Polish & Deploy (Weeks 10-12)
- E2E testing (Cypress)
- Docker production build
- CI/CD automation

## Testing

### Run All Tests
```bash
.\venv\Scripts\pytest tests/ -v --cov
```

### Run by Type
```bash
# Unit tests only
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# With coverage report
pytest tests/ --cov=src/backend --cov-report=html
```

### Automated Test Suite
```bash
.\venv\Scripts\python scripts\run-all-tests.py
```

## Current Test Status
```
6 passed, 1 skipped (Neo4j connection requires Docker)
Required: 5/5 components passed ✓
Optional: 0/4 components (Phase 2 prerequisites)
```

## Known Issues

### Python 3.13 Compatibility
- SQLAlchemy 2.0.23 has compatibility issues with Python 3.13
- Workaround: Tests use mocking until fixed
- Alternative: Downgrade to Python 3.11/3.12 for full compatibility

### NPM Vulnerabilities
- 14 vulnerabilities (dev dependencies only)
- Status: Acceptable for development
- Impact: None on production build
- Action: Optional `npm audit fix --force`

## Environment Variables

Configuration in `.env` file:

```bash
# Database
DATABASE_URL=sqlite:///./data/glossary.db
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=devpassword

# APIs
DEEPL_API_KEY=your-api-key-here

# Paths
IATE_DATASET_PATH=./data/iate/IATE_export.tbx
UPLOAD_DIR=./data/uploads

# Server
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:3000
```

See `.env.example` for full configuration options.

## API Endpoints

### Current (Phase 1)
- `GET /` - API information
- `GET /health` - Health check

### Planned (Phase 1+)
- `POST /upload` - Upload PDF
- `GET /entries` - List glossary entries
- `GET /entries/{id}` - Get entry details
- `PUT /entries/{id}` - Update entry
- `DELETE /entries/{id}` - Delete entry
- `POST /extract` - Extract terms from PDF
- `POST /validate` - Validate against IATE
- `GET /graph` - Get graph data

Full API documentation: http://localhost:8000/docs (when running)

## Database Schema

### SQLite Tables
- `GlossaryEntry` - Extracted terms
- `UploadedDocument` - PDF metadata
- `SyncLog` - Neo4j sync tracking
- `TerminologyCache` - DeepL translations

### Neo4j Graph
- `(:Term)` - Terminology nodes
- `(:Domain)` - Subject domains
- `(:Entry)` - Glossary entries
- `[RELATED_TO]` - Term relationships
- `[BELONGS_TO]` - Domain membership

## Contributing

### Code Style
- Python: PEP 8
- JavaScript: Airbnb style guide
- Max file size: 500 lines
- Test coverage: 70% minimum (MVP)

### Commit Messages
```
feat: Add PDF upload endpoint
fix: Correct Neo4j sync retry logic
docs: Update API documentation
test: Add unit tests for extraction
```

## Support & Resources

### Installation Help
- C++ Build Tools: `docs\REMAINING-SETUP-TASKS.md`
- Docker Setup: `docs\REMAINING-SETUP-TASKS.md`
- Neo4j Guide: https://graphacademy.neo4j.com/

### Development Help
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- Material-UI: https://mui.com/
- Neo4j: https://neo4j.com/docs/

### Troubleshooting
1. Run environment check: `.\venv\Scripts\python setup-check.py`
2. Check Python packages: `.\venv\Scripts\pip list`
3. Check Node packages: `npm list --depth=0`
4. Review logs in backend/frontend terminals

## License

[Your License Here]

## Authors

- [Your Name/Team]

---

**Ready to develop?**

```bash
# Start backend
.\venv\Scripts\activate
python src\backend\app.py

# Start frontend (new terminal)
npm start
```

**Need help with remaining setup?**

```powershell
.\scripts\complete-setup.ps1
```

**Check documentation:**

```bash
start docs\SETUP-COMPLETE.md
```
