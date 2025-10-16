# Installation Guide

Quick guide to get started on your company computer.

---

## 📁 Installation Documentation

All installation guides are in the **`installation/`** folder:

### Start Here:
📖 **[installation/START-HERE.txt](installation/START-HERE.txt)** - Navigation guide to all installation docs

### Main Guides:
- **[installation/README.txt](installation/README.txt)** - Complete installation guide (15 pages)
- **[installation/CHECKLIST.txt](installation/CHECKLIST.txt)** - Printable step-by-step checklist ⭐ PRINT THIS!
- **[installation/QUICK-REFERENCE.txt](installation/QUICK-REFERENCE.txt)** - Command reference card ⭐ KEEP HANDY!

---

## ⚡ Super Quick Start (3 Commands)

```bash
# 1. Clone
git clone https://github.com/developer-hhiotsystems/terminology-extraction.git
cd terminology-extraction

# 2. Setup (automated - takes 3-5 minutes)
.\setup-windows.ps1

# 3. Open in VS Code
code .
```

Then:
1. Install VS Code extensions (click "Install All")
2. Select Python interpreter: `./venv/Scripts/python.exe`
3. Test: `python src\backend\app.py`

**Done!** 🎉

---

## 📋 What to Print

For easiest installation experience, print these:

1. **[installation/CHECKLIST.txt](installation/CHECKLIST.txt)** - Follow step-by-step
2. **[installation/QUICK-REFERENCE.txt](installation/QUICK-REFERENCE.txt)** - Command reference

---

## 🎯 Installation Steps Overview

1. **Clone repository** from GitHub
2. **Run setup script** (automatic - 3-5 minutes)
3. **Install VS Code extensions** (click "Install All")
4. **Select Python interpreter** (`./venv/Scripts/python.exe`)
5. **Test backend** (`python src\backend\app.py`)
6. **Test frontend** (`npm start` in new terminal)
7. **Run tests** (`pytest tests/ -v`)

**Expected time:** 8-10 minutes

---

## ✅ System Requirements

**Required:**
- ✅ Windows 10/11
- ✅ Python 3.10+
- ✅ Node.js 18+
- ✅ Git 2.x+
- ✅ VS Code (recommended)

**NOT Required:**
- ❌ Docker (not needed!)
- ❌ Neo4j (optional)
- ❌ Admin rights (usually)

---

## 🚀 Quick Commands

```bash
# Clone project
git clone https://github.com/developer-hhiotsystems/terminology-extraction.git
cd terminology-extraction

# Run setup
.\setup-windows.ps1

# Start backend
.\venv\Scripts\activate
python src\backend\app.py

# Start frontend (new terminal)
npm start

# Run tests
pytest tests/ -v

# Check setup status
python setup-check.py
```

---

## 🧪 Verify Installation

After installation, test these:

**Backend health check:**
```
http://localhost:8000/health
```
Should show: `{"status": "healthy"}`

**Frontend UI:**
```
http://localhost:3000
```
Should load application with dark theme

**Tests:**
```bash
pytest tests/ -v
```
Should show: `6 passed, 1 skipped`

---

## 🐛 If Something Goes Wrong

**Automatic error reporting:**
- Setup script automatically creates `setup-error-report.md` on failure

**Troubleshooting guides:**
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- [docs/COMPANY-COMPUTER-SETUP.md](docs/COMPANY-COMPUTER-SETUP.md) - Company-specific
- [docs/VSCODE-SETUP.md](docs/VSCODE-SETUP.md) - VS Code extensions

**Get help:**
- Email: developer.hh-iot-systems@outlook.com
- GitHub: https://github.com/developer-hhiotsystems/terminology-extraction/issues

---

## 📚 All Documentation

### Installation (in `installation/` folder):
- **START-HERE.txt** - Guide to guides
- **README.txt** - Full installation guide
- **CHECKLIST.txt** - Printable checklist
- **QUICK-REFERENCE.txt** - Command reference

### Quick Guides (root folder):
- **INSTALLATION.md** (this file) - Quick overview
- **QUICK-START.md** - 5-minute guide
- **TROUBLESHOOTING.md** - Common issues

### Detailed Guides (in `docs/` folder):
- **COMPANY-COMPUTER-SETUP.md** - Company environment
- **VSCODE-SETUP.md** - VS Code extensions
- **EXTENSIONS-SUMMARY.md** - Extensions list
- **NO-DOCKER-SETUP.md** - No-Docker architecture
- **GITHUB-SETUP.md** - Git/GitHub setup

---

## 💼 For Company Computer Testing

**First time setup:**
1. Read: [installation/README.txt](installation/README.txt)
2. Print: [installation/CHECKLIST.txt](installation/CHECKLIST.txt)
3. Follow checklist step-by-step
4. Keep: [installation/QUICK-REFERENCE.txt](installation/QUICK-REFERENCE.txt) handy

**Daily testing:**
```bash
git pull origin master              # Get latest changes
.\venv\Scripts\activate             # Activate environment
python src\backend\app.py           # Test backend
npm start                           # Test frontend (new terminal)
```

---

## 🎯 Success Indicators

Installation is successful when:

- ✅ Setup script completes without errors
- ✅ Backend starts and health check works
- ✅ Frontend loads at http://localhost:3000
- ✅ Tests pass (6 passed, 1 skipped)
- ✅ VS Code shows (venv) in terminal
- ✅ 12 VS Code extensions installed

---

## 🔄 What Happens During Setup

The automated setup script (`setup-windows.ps1`) does:

1. ✅ Checks Python, Node.js, Git are installed
2. ✅ Creates virtual environment (venv folder)
3. ✅ Installs 41 Python packages
4. ✅ Installs 1,764 Node.js packages
5. ✅ Creates .env configuration file
6. ✅ Creates data directories
7. ✅ Verifies setup status
8. ✅ Shows next steps

**Time:** 3-5 minutes

**If error:** Automatically creates `setup-error-report.md`

---

## 🚫 What You DON'T Need

This project works WITHOUT:

- ❌ Docker
- ❌ Containers
- ❌ Neo4j (optional only)
- ❌ Special permissions
- ❌ Complex configuration

**Why?** Uses SQLite (file-based database) and Python virtual environment (just a folder).

100% company-friendly! ✅

See: [docs/NO-DOCKER-SETUP.md](docs/NO-DOCKER-SETUP.md) for details.

---

## 📞 Contact & Support

**Repository:**
https://github.com/developer-hhiotsystems/terminology-extraction

**Submit Issues:**
https://github.com/developer-hhiotsystems/terminology-extraction/issues

**Email:**
developer.hh-iot-systems@outlook.com

**When requesting help, include:**
- `setup-error-report.md` (if setup failed)
- Output of `python setup-check.py`
- Error messages (full text)
- System info (OS, Python version, Node version)

---

## 🎓 Recommended Installation Approach

**Best practice:**

1. **Print** these documents:
   - [installation/CHECKLIST.txt](installation/CHECKLIST.txt) - follow along
   - [installation/QUICK-REFERENCE.txt](installation/QUICK-REFERENCE.txt) - commands

2. **Open** on screen:
   - [installation/README.txt](installation/README.txt) - detailed instructions

3. **During installation:**
   - Check off items in CHECKLIST.txt
   - Use QUICK-REFERENCE.txt for commands
   - Refer to README.txt for details

4. **If issues:**
   - Check `setup-error-report.md` (auto-generated)
   - Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
   - Contact support with error report

---

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Clone repository | 1 minute |
| Run setup script | 3-5 minutes |
| Install VS Code extensions | 2 minutes |
| Test backend | 30 seconds |
| Test frontend | 1 minute |
| Run tests | 30 seconds |
| **Total** | **8-10 minutes** |

Behind corporate proxy: Add 5-10 minutes

---

## 🎉 Ready to Start?

**Open:** [installation/START-HERE.txt](installation/START-HERE.txt)

Or jump straight to: [installation/README.txt](installation/README.txt)

Good luck! 🚀

---

**Last Updated:** 2025-10-16
**Version:** 1.0.0
