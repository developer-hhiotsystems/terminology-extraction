# GitHub Setup & Deployment Guide

**Repository**: `developer-hhiotsystems/terminology-extraction`
**Date**: October 16, 2025

---

## Step 1: Create GitHub Repository

### Option A: Via GitHub Website (Recommended)

1. **Go to GitHub**
   - Visit: https://github.com/new
   - Login with: `developer-hhiotsystems`

2. **Create Repository**
   - Repository name: `terminology-extraction`
   - Description: `Glossary extraction and validation application with NLP, Neo4j graph database, and IATE terminology validation`
   - Visibility: **Public** or **Private** (your choice)
   - ❌ **DO NOT** initialize with README (we already have one)
   - ❌ **DO NOT** add .gitignore (we already have one)
   - ❌ **DO NOT** add license yet

3. **Click "Create repository"**

### Option B: Via GitHub CLI (If you have `gh` installed)

```bash
gh repo create terminology-extraction --public --description "Glossary extraction and validation application"
```

---

## Step 2: Push Your Code to GitHub

After creating the repository on GitHub, run these commands:

```bash
cd "C:\Users\devel\Coding Projects\Glossary APP"

# Add GitHub as remote
git remote add origin https://github.com/developer-hhiotsystems/terminology-extraction.git

# Verify remote was added
git remote -v

# Push to GitHub (first time)
git push -u origin master
```

### If prompted for authentication:

**Option 1: GitHub Personal Access Token (Recommended)**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name: "Terminology Extraction Development"
4. Select scopes: `repo` (full control of private repositories)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)
7. Use the token as your password when pushing

**Option 2: GitHub Desktop**
- Install GitHub Desktop: https://desktop.github.com/
- Login and it handles authentication automatically

---

## Step 3: Verify Upload

1. Visit: https://github.com/developer-hhiotsystems/terminology-extraction
2. You should see:
   - ✓ README.md displayed
   - ✓ 45 files committed
   - ✓ All documentation in `docs/` folder
   - ✓ Source code in `src/` folder
   - ✓ Scripts in `scripts/` folder

---

## What Gets Pushed to GitHub ✓

### Included (45 files):
- ✓ All source code (`src/backend/`, `src/frontend/`)
- ✓ All documentation (`docs/` - 11 files)
- ✓ All automation scripts (`scripts/` - 8 files)
- ✓ Configuration templates (`.env.example`, `docker-compose.dev.yml`)
- ✓ Python requirements (`requirements.txt`, `requirements-core.txt`)
- ✓ Node.js configuration (`package.json`, `package-lock.json`)
- ✓ Test framework (`tests/` - unit, integration, e2e)
- ✓ Setup verification (`setup-check.py`)
- ✓ README and .gitignore

### Excluded (via .gitignore):
- ✗ `venv/` - Virtual environment (will be recreated)
- ✗ `node_modules/` - Node packages (will be reinstalled)
- ✗ `.env` - Your secrets (NEVER commit this!)
- ✗ `data/` - Uploaded files and databases
- ✗ `backups/` - Database backups
- ✗ `*.db` - SQLite database files
- ✗ `__pycache__/` - Python cache
- ✗ `.pytest_cache/` - Test cache

---

## Step 4: Setup on Second Computer

### Quick Setup (10-15 minutes)

**1. Clone Repository**
```bash
cd "path/to/your/projects"
git clone https://github.com/developer-hhiotsystems/terminology-extraction.git
cd terminology-extraction
```

**2. Install Python Dependencies**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell/CMD:
.\venv\Scripts\activate

# Windows Git Bash:
source venv/Scripts/activate

# Install packages
pip install --upgrade pip
pip install -r requirements-core.txt
```

**3. Install Node.js Dependencies**
```bash
npm install
```

**4. Configure Environment**
```bash
# Copy environment template
copy .env.example .env

# Edit .env with your settings (optional for Phase 1)
notepad .env
```

**5. Verify Setup**
```bash
# Check Python packages
python setup-check.py

# Should show: Required: 5/5 passed
```

**6. Test Backend**
```bash
.\venv\Scripts\activate
python src\backend\app.py
```
Visit: http://localhost:8000/health

**7. Test Frontend (new terminal)**
```bash
npm start
```
Visit: http://localhost:3000

---

## Full Setup with Phase 2 Prerequisites

If you want full capabilities on the second computer:

```bash
# After basic setup above, run:
.\venv\Scripts\activate
python scripts\complete-setup.ps1
```

This will guide you through:
1. C++ Build Tools installation
2. Docker Desktop + Neo4j setup
3. DeepL API configuration
4. IATE dataset download

---

## Typical Workflow After Setup

### Daily Development

**First Computer (Main Development):**
```bash
# Make changes to code
# Test locally
git add .
git commit -m "Description of changes"
git push
```

**Second Computer (Testing):**
```bash
# Get latest changes
git pull

# Reinstall if package.json changed
npm install
pip install -r requirements-core.txt

# Test
python src\backend\app.py
npm start
```

### Branch Workflow (Recommended for features)

```bash
# Create feature branch
git checkout -b feature/new-endpoint

# Make changes and commit
git add .
git commit -m "Add new endpoint"

# Push feature branch
git push -u origin feature/new-endpoint

# Merge when ready (via GitHub PR or locally)
git checkout master
git merge feature/new-endpoint
git push
```

---

## Important Files Comparison

| File | First Computer | Second Computer | Sync? |
|------|----------------|-----------------|-------|
| Source code | ✓ | ✓ | Yes (Git) |
| Documentation | ✓ | ✓ | Yes (Git) |
| `venv/` | ✓ | ✓ | No (recreate) |
| `node_modules/` | ✓ | ✓ | No (npm install) |
| `.env` | ✓ | ✓ | No (manual copy) |
| `data/` | ✓ | ✗ | No (local only) |
| Database files | ✓ | ✗ | No (local only) |

**Note**: Database files and uploaded PDFs are NOT synced via Git. They stay on each computer independently.

---

## Troubleshooting

### Authentication Issues

**Problem**: Git push asks for password
**Solution**: Use Personal Access Token (see Step 2 above)

### Clone Fails

**Problem**: Repository not found
**Solution**:
1. Verify repository exists: https://github.com/developer-hhiotsystems/terminology-extraction
2. Check you're logged in to correct GitHub account
3. Verify spelling of username and repository name

### Setup Fails on Second Computer

**Problem**: Dependencies won't install
**Solution**:
```bash
# Check Python version (need 3.10+)
python --version

# Check Node version (need 18+)
node --version

# If wrong version, install correct version first
```

### Virtual Environment Issues

**Problem**: Can't activate venv
**Solution**:
```powershell
# Windows PowerShell may need this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again:
.\venv\Scripts\activate
```

---

## Repository Settings (Optional but Recommended)

### Add Repository Topics
Go to: https://github.com/developer-hhiotsystems/terminology-extraction

Add topics:
- `glossary`
- `terminology`
- `nlp`
- `neo4j`
- `fastapi`
- `react`
- `iate`
- `pdf-extraction`

### Add README Badges

Add to top of README.md:
```markdown
![Python](https://img.shields.io/badge/python-3.13-blue)
![Node](https://img.shields.io/badge/node-22.18-green)
![Tests](https://img.shields.io/badge/tests-6%20passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
```

### Enable GitHub Actions (Future)

For automated testing on push:
- Create `.github/workflows/tests.yml`
- Will be added in Phase 3

---

## Security Reminders

### ⚠️ NEVER Commit These Files:
- ❌ `.env` (contains secrets)
- ❌ `*.db` (database files)
- ❌ `data/uploads/*` (user uploaded files)
- ❌ API keys or passwords
- ❌ Personal access tokens

### ✓ Safe to Commit:
- ✓ `.env.example` (template without secrets)
- ✓ Source code
- ✓ Documentation
- ✓ Configuration templates
- ✓ Test files

**Already protected by .gitignore!**

---

## Quick Reference Commands

```bash
# Check status
git status

# See what changed
git diff

# Add all changes
git add .

# Commit with message
git commit -m "Your message"

# Push to GitHub
git push

# Get latest from GitHub
git pull

# See commit history
git log --oneline

# Create new branch
git checkout -b branch-name

# Switch branch
git checkout master

# See all branches
git branch -a
```

---

## Next Steps

1. ✅ Push code to GitHub (see Step 2)
2. ✅ Clone on second computer (see Step 4)
3. ✅ Verify both computers work
4. 🚀 Start Phase 1 development
5. 📝 Commit changes regularly
6. 🔄 Keep both computers in sync with `git pull`

---

**GitHub Repository**: https://github.com/developer-hhiotsystems/terminology-extraction

**Ready to push?** Run the commands from Step 2!
