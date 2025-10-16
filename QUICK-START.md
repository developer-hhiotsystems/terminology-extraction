# Quick Start Guide

Get up and running in 5 minutes.

---

## 🚀 On Your Development Computer (Here)

**Already done!** Project is set up and on GitHub.

To make changes:
```bash
# Make changes to code
git add .
git commit -m "Description of changes"
git push origin master
```

---

## 💼 On Your Company Computer (Testing)

### First Time Setup (5 minutes):

**1. Open VS Code**

**2. Clone project:**
```bash
# In VS Code terminal (Ctrl+`)
git clone https://github.com/developer-hhiotsystems/terminology-extraction.git
cd terminology-extraction
```

**3. Run automated setup:**
```bash
.\setup-windows.ps1
```

This will:
- ✅ Check Python, Node.js, Git
- ✅ Create virtual environment (just a folder, NOT Docker)
- ✅ Install 41 Python packages
- ✅ Install 1,764 Node packages
- ✅ Create .env configuration
- ✅ Setup SQLite database

**4. Install VS Code extensions:**
- Click "Install All" when prompted
- Or see: `docs/VSCODE-SETUP.md`

**Done!** Setup complete.

---

## 🧪 Testing Backend

**In VS Code terminal:**
```bash
# Activate virtual environment (auto-activates usually)
.\venv\Scripts\activate

# Start backend server
python src\backend\app.py
```

**Test it:**
- Open browser: http://localhost:8000/health
- Should see: `{"status": "healthy"}`

**Stop server:** `Ctrl+C`

---

## 🎨 Testing Frontend

**In NEW terminal (Ctrl+Shift+\`):**
```bash
npm start
```

**Should automatically open:** http://localhost:3000

**Features to test:**
- ✅ Upload page
- ✅ Glossary management
- ✅ Dark theme
- ✅ Responsive design

**Stop server:** `Ctrl+C`

---

## ✅ Run All Tests

**In terminal:**
```bash
# Activate venv if not already
.\venv\Scripts\activate

# Run all tests
pytest tests/ -v
```

**Expected:**
```
6 passed, 1 skipped in 0.XX s
```

---

## 🔄 Daily Workflow

### On Development Computer:
```bash
# 1. Make changes
# 2. Test locally
python src\backend\app.py  # Test backend
npm start                  # Test frontend

# 3. Commit and push
git add .
git commit -m "Description"
git push origin master
```

### On Company Computer:
```bash
# 1. Pull latest changes
git pull origin master

# 2. Test
.\venv\Scripts\activate
python src\backend\app.py  # Test backend
npm start                  # Test frontend (new terminal)

# 3. Report any issues
```

---

## 🐛 If Something Goes Wrong

**Run diagnostic:**
```bash
python setup-check.py
```

**See error solutions:**
- Check: `TROUBLESHOOTING.md`
- Check: `docs/COMPANY-COMPUTER-SETUP.md`
- Or generate automatic error report (already happens during setup)

---

## 📚 More Documentation

- **VS Code Setup**: `docs/VSCODE-SETUP.md`
- **No-Docker Guide**: `docs/NO-DOCKER-SETUP.md`
- **Company Setup**: `docs/COMPANY-COMPUTER-SETUP.md`
- **Troubleshooting**: `TROUBLESHOOTING.md`

---

## ⚡ Super Quick Testing (No Installation)

**Just want to see if code runs on company computer?**

**Minimal test:**
```bash
# Clone
git clone https://github.com/developer-hhiotsystems/terminology-extraction.git
cd terminology-extraction

# Setup
.\setup-windows.ps1

# Quick health check
python setup-check.py
```

**If all checks pass ✅** → Full setup successful!

---

**That's it!** Simple and fast. 🎉
