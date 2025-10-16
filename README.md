# Glossary Extraction & Validation Application

**Automated terminology extraction and validation system for multilingual glossaries.**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://react.dev/)

---

## 🚀 Quick Start

### **New to this project?**

📂 **Go to: [`setup/`](setup/)** folder for complete installation guides

Or run the automated setup:

```bash
git clone https://github.com/developer-hhiotsystems/terminology-extraction.git
cd terminology-extraction
.\setup-windows.ps1
```

**That's it!** Setup takes 3-5 minutes.

---

## 📋 What This Application Does

### **Main Features:**
- 📄 Upload PDF/DOCX/Excel documents
- 🔍 Automatic terminology extraction using NLP
- ✅ Validation against IATE (EU terminology database)
- 🌐 Multi-language translation (DeepL API)
- 📊 Interactive glossary management
- 💾 Export in multiple formats

### **Target Users:**
- Translators
- Terminology managers
- Documentation teams
- Language service providers

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLite** - File-based database (no Docker needed!)
- **Neo4j** - Graph database (optional)
- **spaCy** - NLP for term extraction
- **DeepL API** - Translation services

### Frontend
- **React 18** - UI framework
- **Material-UI** - Component library (WCAG 2.1 AA compliant)
- **Dark theme** - Eye-friendly interface

### Testing
- **pytest** - Backend testing
- **Cypress** - Frontend E2E testing
- **Coverage**: 70%+ target

---

## 📁 Project Structure

```
terminology-extraction/
├── setup/                  ← START HERE for installation
│   ├── START-HERE.txt     → Navigation guide
│   ├── README.txt         → Full installation instructions
│   ├── CHECKLIST.txt      → Printable step-by-step guide
│   └── QUICK-REFERENCE.txt → Command reference
│
├── src/
│   ├── backend/           → FastAPI application (Python)
│   └── frontend/          → React application (JavaScript)
│
├── tests/                 → pytest tests
├── docs/                  → Documentation
├── scripts/               → Utility scripts
│
├── setup-windows.ps1      → Automated setup script
├── setup-check.py         → Verify installation
└── README.md              → This file
```

---

## 💻 Development

### Start Backend:
```bash
.\venv\Scripts\activate
python src\backend\app.py
```
**Opens at:** http://localhost:8000

**API Docs:** http://localhost:8000/docs

### Start Frontend:
```bash
npm start
```
**Opens at:** http://localhost:3000

### Run Tests:
```bash
pytest tests/ -v
```

---

## 📚 Documentation

### Installation Guides:
| Guide | Description | Time |
|-------|-------------|------|
| [setup/README.txt](setup/README.txt) | Complete installation guide | 15 min |
| [setup/CHECKLIST.txt](setup/CHECKLIST.txt) | Printable step-by-step checklist | - |
| [setup/QUICK-REFERENCE.txt](setup/QUICK-REFERENCE.txt) | Command reference card | - |

### Quick References:
- [docs/guides/QUICK-START.md](docs/guides/QUICK-START.md) - 5-minute overview
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Common issues
- [docs/guides/VSCODE-FOOLPROOF-GUIDE.md](docs/guides/VSCODE-FOOLPROOF-GUIDE.md) - VS Code setup

### Technical Documentation:
- [docs/PRT-v2.2.md](docs/PRT-v2.2.md) - Product requirements
- [docs/IMPLEMENTATION-STRATEGY-v1.1.md](docs/IMPLEMENTATION-STRATEGY-v1.1.md) - Development roadmap
- [docs/NO-DOCKER-SETUP.md](docs/NO-DOCKER-SETUP.md) - No-Docker architecture

---

## ✅ System Requirements

**Required:**
- Windows 10/11
- Python 3.10+
- Node.js 18+
- Git
- 2 GB free disk space

**NOT Required:**
- ❌ Docker (optional only)
- ❌ Neo4j (optional only)
- ❌ Admin rights (usually)

**Works completely without Docker!** Uses SQLite for 95% of features.

---

## 🧪 Current Status

**Phase 1: Complete ✅**
- ✅ Backend API (FastAPI)
- ✅ Frontend UI (React)
- ✅ SQLite database
- ✅ File upload system
- ✅ Basic CRUD operations
- ✅ Testing framework (6 passed, 1 skipped)

**Phase 2: In Progress 🔄**
- NLP terminology extraction
- IATE validation
- Translation integration
- Graph visualization

---

## 🐛 Troubleshooting

**Setup failed?**
- Check: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- Review: `setup-error-report.md` (auto-generated on errors)
- Run: `python setup-check.py` (diagnostic check)

**Need help?**
- GitHub Issues: https://github.com/developer-hhiotsystems/terminology-extraction/issues
- Email: developer.hh-iot-systems@outlook.com

---

## 🔄 Daily Workflow

### Development Computer:
```bash
# Make changes, test, commit
git add .
git commit -m "Description"
git push origin master
```

### Company Computer (Testing):
```bash
# Pull latest changes
git pull origin master

# Test backend
.\venv\Scripts\activate
python src\backend\app.py

# Test frontend (new terminal)
npm start
```

---

## 🎯 API Endpoints

### Current (Phase 1):
- `GET /` - API information
- `GET /health` - Health check

### Planned (Phase 2):
- `POST /upload` - Upload documents
- `GET /entries` - List glossary entries
- `POST /extract` - Extract terminology
- `POST /validate` - Validate against IATE
- `POST /translate` - Translate terms

**Full API docs:** http://localhost:8000/docs (when backend is running)

---

## 🤝 Contributing

### Code Style:
- Python: PEP 8
- JavaScript: Airbnb style guide
- Max file size: 500 lines
- Test coverage: 70%+ minimum

### Commit Format:
```
feat: Add PDF upload endpoint
fix: Correct validation logic
docs: Update API documentation
test: Add unit tests for extraction
```

---

## 📄 License

[Your License Here]

---

## 👥 Authors

- Developer: developer-hhiotsystems
- Email: developer.hh-iot-systems@outlook.com
- Repository: https://github.com/developer-hhiotsystems/terminology-extraction

---

## 🎉 Ready to Start?

### **Installation:**
1. Go to [`setup/`](setup/) folder
2. Read `START-HERE.txt`
3. Follow installation guide
4. Run `.\setup-windows.ps1`

### **Quick Test:**
```bash
# Clone project
git clone https://github.com/developer-hhiotsystems/terminology-extraction.git
cd terminology-extraction

# Run setup (3-5 minutes)
.\setup-windows.ps1

# Test backend
.\venv\Scripts\activate
python src\backend\app.py
# Visit: http://localhost:8000/health

# Test frontend (new terminal)
npm start
# Opens: http://localhost:3000
```

**Everything works! No Docker needed!** 🚀

---

**Questions?** Check the [`setup/`](setup/) folder for complete guides!

**Last Updated:** 2025-10-16 | **Version:** 1.0.0
