================================================================================
  TERMINOLOGY EXTRACTION - INSTALLATION GUIDE
================================================================================

Quick installation guide for company computer testing.

================================================================================
  STEP 1: CLONE PROJECT
================================================================================

Open VS Code and press Ctrl+` (open terminal), then run:

    git clone https://github.com/developer-hhiotsystems/terminology-extraction.git
    cd terminology-extraction

================================================================================
  STEP 2: RUN AUTOMATED SETUP
================================================================================

Run the automated setup script:

    .\setup-windows.ps1

This script will automatically:
  [1/8] Check Python 3.10+, Node.js 18+, Git
  [2/8] Create virtual environment (venv folder - NOT Docker!)
  [3/8] Install 41 Python packages
  [4/8] Install 1,764 Node.js packages
  [5/8] Create .env configuration file
  [6/8] Create data directories
  [7/8] Verify setup status
  [8/8] Show next steps

Time: 3-5 minutes

If errors occur, the script automatically generates: setup-error-report.md

================================================================================
  STEP 3: INSTALL VS CODE EXTENSIONS
================================================================================

When you open the project in VS Code, you'll see:

    "This workspace has extension recommendations"

Click: "Install All"

Extensions installed (12 total):
  - Python (language support)
  - Pylance (type checking)
  - ESLint (JavaScript linting)
  - Prettier (code formatting)
  - React Snippets (React development)
  - GitLens (Git features)
  - Test Explorer (visual test runner)
  - And 5 more...

================================================================================
  STEP 4: SELECT PYTHON INTERPRETER
================================================================================

After extensions install:

  1. Click Python version in bottom-left corner
     OR
     Press Ctrl+Shift+P and type "Python: Select Interpreter"

  2. Choose: ./venv/Scripts/python.exe

  3. Terminal should now show: (venv) prefix

================================================================================
  STEP 5: TEST BACKEND
================================================================================

In terminal (Ctrl+`):

    .\venv\Scripts\activate
    python src\backend\app.py

Expected output:
    INFO:     Uvicorn running on http://127.0.0.1:8000

Test in browser:
    http://localhost:8000/health

Should show:
    {"status": "healthy"}

Stop server: Ctrl+C

================================================================================
  STEP 6: TEST FRONTEND
================================================================================

Open NEW terminal (Ctrl+Shift+`):

    npm start

Should automatically open: http://localhost:3000

Test features:
  - Upload page (dark theme)
  - Glossary management
  - Responsive design
  - WCAG 2.1 AA accessibility

Stop server: Ctrl+C

================================================================================
  STEP 7: RUN TESTS
================================================================================

In terminal with venv activated:

    pytest tests/ -v

Expected result:
    6 passed, 1 skipped in 0.XX s

================================================================================
  WHAT YOU DON'T NEED
================================================================================

  X Docker - NOT NEEDED!
  X Neo4j - Optional only
  X Containers - NOT USED!
  X Special permissions - Standard setup only

This project uses:
  - SQLite (file-based database)
  - Python virtual environment (just a folder)
  - Standard Node.js packages

100% company-friendly!

================================================================================
  TROUBLESHOOTING
================================================================================

Problem: "Python not found"
Solution: Install Python 3.10+ from https://www.python.org/downloads/
          Check "Add Python to PATH" during installation

Problem: "Node not found"
Solution: Install Node.js 18+ from https://nodejs.org/

Problem: "Cannot run scripts" (PowerShell)
Solution: Run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Problem: "Port already in use"
Solution:
    netstat -ano | findstr :8000
    taskkill /PID [number] /F

Problem: Behind corporate proxy
Solution: See docs/COMPANY-COMPUTER-SETUP.md for proxy configuration

For more help: See TROUBLESHOOTING.md

================================================================================
  AUTOMATIC ERROR REPORTING
================================================================================

If setup fails, the script automatically creates:

    setup-error-report.md

This file contains:
  - Exact error message
  - System information
  - Setup log with timestamps
  - Suggested solutions
  - Links to submit issue

You can:
  1. Read it for solutions
  2. Submit to: https://github.com/developer-hhiotsystems/terminology-extraction/issues
  3. Email: developer.hh-iot-systems@outlook.com

================================================================================
  FILE STRUCTURE
================================================================================

After installation:

terminology-extraction/
├── installation/           ← You are here
│   ├── README.txt         ← This file
│   └── CHECKLIST.txt      ← Step-by-step checklist
│
├── src/
│   ├── backend/           ← FastAPI backend (Python)
│   └── frontend/          ← React frontend (JavaScript)
│
├── tests/                 ← Test files (pytest)
├── docs/                  ← Full documentation
├── data/                  ← SQLite database location
├── venv/                  ← Virtual environment (created by setup)
├── node_modules/          ← Node packages (created by setup)
│
├── setup-windows.ps1      ← Main setup script
├── setup-windows.bat      ← Alternative batch script
├── setup-check.py         ← Verify installation status
├── QUICK-START.md         ← 5-minute guide
├── TROUBLESHOOTING.md     ← Common issues and solutions
└── .env                   ← Configuration (created by setup)

================================================================================
  DAILY WORKFLOW
================================================================================

Development Computer (coding):
  1. Make changes
  2. Test locally
  3. git add .
  4. git commit -m "Description"
  5. git push origin master

Company Computer (testing):
  1. git pull origin master
  2. Test backend: python src\backend\app.py
  3. Test frontend: npm start (in new terminal)
  4. Report any issues

================================================================================
  VERIFICATION CHECKLIST
================================================================================

After installation, verify:

  [ ] Python version: python --version (should be 3.10+)
  [ ] Node version: node --version (should be 18+)
  [ ] Virtual environment exists: ls venv
  [ ] Python packages: .\venv\Scripts\pip list (41 packages)
  [ ] Node packages: npm list --depth=0 (1,764 packages)
  [ ] Database: ls data (should see glossary.db after first run)
  [ ] VS Code extensions: 12 installed
  [ ] Python interpreter selected: bottom-left shows "./venv/Scripts/python.exe"
  [ ] Backend health check: http://localhost:8000/health works
  [ ] Frontend loads: http://localhost:3000 opens
  [ ] Tests pass: pytest shows 6 passed, 1 skipped

All checked? Installation successful!

================================================================================
  DOCUMENTATION FILES
================================================================================

Quick References:
  - installation/README.txt       ← This file (start here)
  - installation/CHECKLIST.txt    ← Printable checklist
  - QUICK-START.md                ← 5-minute guide

Setup Guides:
  - docs/COMPANY-COMPUTER-SETUP.md  ← Company environment specific
  - docs/VSCODE-SETUP.md            ← VS Code extensions guide
  - docs/NO-DOCKER-SETUP.md         ← No-Docker architecture
  - docs/GITHUB-SETUP.md            ← Git/GitHub instructions

Reference:
  - docs/EXTENSIONS-SUMMARY.md      ← VS Code extensions summary
  - TROUBLESHOOTING.md              ← Common problems and solutions
  - README.md                       ← Project overview

================================================================================
  SYSTEM REQUIREMENTS
================================================================================

Required:
  - Windows 10/11
  - Python 3.10 or higher
  - Node.js 18 or higher
  - Git 2.x or higher
  - VS Code (recommended)
  - 2 GB free disk space
  - Internet connection (for initial setup)

Optional:
  - Docker (NOT needed, completely optional)
  - Neo4j (NOT needed, SQLite works great)

================================================================================
  GETTING HELP
================================================================================

If stuck:

  1. Check: TROUBLESHOOTING.md (common solutions)
  2. Check: docs/COMPANY-COMPUTER-SETUP.md (company-specific issues)
  3. Run: python setup-check.py (diagnostic check)
  4. Review: setup-error-report.md (if setup failed)
  5. Submit issue: https://github.com/developer-hhiotsystems/terminology-extraction/issues
  6. Email: developer.hh-iot-systems@outlook.com

Include the setup-error-report.md file when requesting help!

================================================================================
  SUCCESS!
================================================================================

If you can:
  - Start backend (python src\backend\app.py)
  - See health check (http://localhost:8000/health)
  - Start frontend (npm start)
  - See UI (http://localhost:3000)
  - Run tests (pytest tests/ -v)

Then installation is COMPLETE! Ready to develop and test!

================================================================================
  PROJECT INFORMATION
================================================================================

Project: Terminology Extraction & Validation System
Repository: https://github.com/developer-hhiotsystems/terminology-extraction
Developer: developer-hhiotsystems
Email: developer.hh-iot-systems@outlook.com

Technology Stack:
  - Backend: Python 3.10+, FastAPI, SQLAlchemy
  - Frontend: React 18, Material-UI, Axios
  - Database: SQLite (file-based, no Docker)
  - Testing: pytest, Cypress, React Testing Library
  - Translation: DeepL API
  - Validation: IATE terminology database

Features:
  - PDF document upload and parsing
  - Automated terminology extraction (NLP)
  - Translation management (DeepL)
  - IATE validation
  - Dark theme UI (WCAG 2.1 AA)
  - Fully accessible
  - No Docker required

================================================================================

Last Updated: 2025-10-16
Version: 1.0.0

For latest version, run: git pull origin master

================================================================================
