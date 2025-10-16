# Company Computer Setup Guide (Testing Environment)

**Purpose**: Setup testing environment on restricted company computer
**Development**: This computer (main)
**Testing**: Company computer (clone from GitHub)

---

## 🎯 Workflow Overview

```
This Computer (Development)          Company Computer (Testing)
├── Write code                       ├── Clone from GitHub
├── Test locally                     ├── Install dependencies
├── Commit to Git                    ├── Test application
└── Push to GitHub          ───────> └── Verify functionality
```

---

## 📋 Prerequisites on Company Computer

Check if these are available:
- [ ] Git (check: `git --version`)
- [ ] Python 3.10+ (check: `python --version`)
- [ ] Node.js 18+ (check: `node --version`)
- [ ] VS Code installed
- [ ] Internet access to github.com
- [ ] Permission to install Python/Node packages

---

## 🚀 Step-by-Step Setup on Company Computer

### Step 1: Open VS Code

1. Launch VS Code
2. Press `Ctrl+Shift+P` (Command Palette)
3. Type: `Git: Clone`
4. Paste: `https://github.com/developer-hhiotsystems/terminology-extraction.git`
5. Choose a location (e.g., `C:\Users\YourName\Projects\`)
6. Click "Open" when prompted

**Alternative (Terminal):**
```bash
cd C:\Users\YourName\Projects
git clone https://github.com/developer-hhiotsystems/terminology-extraction.git
cd terminology-extraction
code .
```

---

### Step 2: Open Integrated Terminal in VS Code

Press `` Ctrl+` `` (backtick) or:
- Menu: View → Terminal

---

### Step 3: Create Python Virtual Environment

In VS Code terminal:

```bash
python -m venv venv
```

Wait for it to complete (~30 seconds)

---

### Step 4: Activate Virtual Environment

**Windows PowerShell (VS Code default):**
```powershell
.\venv\Scripts\Activate.ps1
```

**If you get execution policy error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

**Windows CMD:**
```cmd
.\venv\Scripts\activate.bat
```

**Git Bash:**
```bash
source venv/Scripts/activate
```

You should see `(venv)` in your terminal prompt.

---

### Step 5: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements-core.txt
```

**Time**: 2-3 minutes
**Expected**: ~41 packages installed

---

### Step 6: Install Node.js Dependencies

```bash
npm install
```

**Time**: 3-5 minutes
**Expected**: ~1,764 packages installed

**If restricted on company network:**
```bash
# Use company npm registry if available
npm config set registry https://your-company-registry
npm install
```

---

### Step 7: Create Environment File

```bash
copy .env.example .env
```

**Or manually:**
1. Right-click `.env.example` in VS Code
2. Choose "Copy"
3. Right-click in Explorer → Paste
4. Rename to `.env`

---

### Step 8: Verify Setup

```bash
python setup-check.py
```

**Expected output:**
```
Required: 5/5 passed
[OK] Minimum requirements met - ready for Phase 1 development
```

---

### Step 9: Test Backend

Open Terminal 1 in VS Code:

```bash
.\venv\Scripts\activate
python src\backend\app.py
```

**Expected:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Test in browser:**
- Open: http://localhost:8000
- Should see: API information JSON
- Open: http://localhost:8000/health
- Should see: `{"status": "healthy"}`

---

### Step 10: Test Frontend

Open Terminal 2 in VS Code (Click `+` in terminal panel):

```bash
npm start
```

**Expected:**
- Browser opens automatically to http://localhost:3000
- Shows "Welcome to Glossary App" with dark theme

---

## ✅ Success Checklist

- [ ] Repository cloned in VS Code
- [ ] Python virtual environment created
- [ ] 41 Python packages installed
- [ ] 1,764 Node packages installed
- [ ] `.env` file created
- [ ] `setup-check.py` shows 5/5 passed
- [ ] Backend starts on port 8000
- [ ] Frontend opens in browser on port 3000
- [ ] Health endpoint returns JSON

---

## 🔄 Daily Testing Workflow

### On Development Computer (This One):

```bash
# After making changes:
git add .
git commit -m "Add feature X"
git push
```

### On Company Computer (Testing):

```bash
# Get latest changes:
git pull

# If package.json or requirements changed:
npm install
pip install -r requirements-core.txt

# Test backend:
.\venv\Scripts\activate
python src\backend\app.py

# Test frontend (new terminal):
npm start
```

---

## 🚨 Common Issues on Restricted Computers

### Issue 1: PowerShell Execution Policy

**Error:** "cannot be loaded because running scripts is disabled"

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### Issue 2: Git Authentication

**Error:** "Authentication failed"

**Solution:** Use Personal Access Token
1. Generate token: https://github.com/settings/tokens
2. When git asks for password, paste the token

**Or configure credential helper:**
```bash
git config --global credential.helper wincred
```

---

### Issue 3: NPM Behind Corporate Proxy

**Error:** "ECONNREFUSED" or timeout

**Solution:**
```bash
npm config set proxy http://proxy.company.com:8080
npm config set https-proxy http://proxy.company.com:8080
npm config set strict-ssl false  # Only if needed

npm install
```

---

### Issue 4: Python SSL Certificates

**Error:** "SSL: CERTIFICATE_VERIFY_FAILED"

**Solution:**
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements-core.txt
```

---

### Issue 5: Port 8000 or 3000 Already in Use

**Error:** "Address already in use"

**Solution - Find and kill process:**

**PowerShell:**
```powershell
# Find process on port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

**Or use different ports:**

Backend (edit `src/backend/app.py`):
```python
uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
```

Frontend (add to `package.json`):
```json
"scripts": {
  "start": "PORT=3001 react-scripts start"
}
```

---

### Issue 6: VS Code Not Finding Python

**Solution:**

1. Press `Ctrl+Shift+P`
2. Type: `Python: Select Interpreter`
3. Choose: `.\venv\Scripts\python.exe`

---

### Issue 7: Node Modules Access Denied

**Error:** "EPERM: operation not permitted"

**Solution:**
```bash
# Close VS Code
# Delete node_modules folder
# Reopen VS Code
npm install
```

---

## 🔒 What to Do If Installations Are Blocked

### Python Packages Blocked:

**Option 1:** Download packages locally on this computer
```bash
pip download -r requirements-core.txt -d packages
# Copy "packages" folder to company computer
pip install --no-index --find-links=packages -r requirements-core.txt
```

**Option 2:** Use virtual environment from USB
- Copy entire `venv` folder to USB
- Copy to company computer
- Activate normally

---

### Node Packages Blocked:

**Option 1:** Copy node_modules
```bash
# On this computer after npm install:
# Copy entire "node_modules" folder to USB
# Paste in company computer project folder
```

**Option 2:** Use npm pack
```bash
npm pack
# Copy .tgz file to company computer
npm install ./terminology-extraction-1.0.0.tgz
```

---

## 📊 Minimal Testing Setup (If Restricted)

If you can't install everything, minimum requirements:

**Must Have:**
- Git (clone repository)
- Python 3.10+ (run backend)
- pip (install Python packages)

**Can Skip (Phase 1):**
- Node.js/npm (if only testing backend)
- Docker (Neo4j not needed for Phase 1)
- spaCy/lxml (Phase 2 only)

**Test backend only:**
```bash
git clone https://github.com/developer-hhiotsystems/terminology-extraction.git
cd terminology-extraction
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements-core.txt
python src\backend\app.py
```

Visit: http://localhost:8000/health

---

## 💡 VS Code Tips for Testing

### Recommended Extensions:
- Python (Microsoft)
- Pylance
- Git Graph
- REST Client (test API endpoints)

### Split Terminal:
- Click split icon in terminal panel
- Run backend in left, frontend in right

### Quick Commands:
- `Ctrl+Shift+P` → Command Palette
- `` Ctrl+` `` → Toggle Terminal
- `Ctrl+B` → Toggle Sidebar
- `Ctrl+K Ctrl+O` → Open Folder

### Testing API in VS Code:

Create `test.http` file:
```http
### Test Health Endpoint
GET http://localhost:8000/health

### Test Root
GET http://localhost:8000/
```

Click "Send Request" above each line.

---

## 📝 Quick Reference Card

**Setup (First Time):**
```bash
git clone https://github.com/developer-hhiotsystems/terminology-extraction.git
cd terminology-extraction
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements-core.txt
npm install
copy .env.example .env
python setup-check.py
```

**Test Backend:**
```bash
.\venv\Scripts\activate
python src\backend\app.py
```

**Test Frontend:**
```bash
npm start
```

**Update (Daily):**
```bash
git pull
pip install -r requirements-core.txt  # If changed
npm install                            # If changed
```

---

## ⏱️ Time Estimates

- Clone repository: 1-2 minutes
- Create venv: 30 seconds
- Install Python packages: 2-3 minutes
- Install Node packages: 3-5 minutes
- Create .env: 10 seconds
- Verify setup: 30 seconds

**Total First Time**: 10-15 minutes
**Daily Updates**: 1-2 minutes

---

## 🆘 If Something Goes Wrong

1. **Check setup-check.py output**
   ```bash
   python setup-check.py
   ```

2. **Verify Git status**
   ```bash
   git status
   git log --oneline -5
   ```

3. **Check installed packages**
   ```bash
   pip list
   npm list --depth=0
   ```

4. **Test Python imports**
   ```bash
   python -c "import fastapi, neo4j, pytest; print('OK')"
   ```

5. **Check ports**
   ```bash
   netstat -ano | findstr :8000
   netstat -ano | findstr :3000
   ```

---

## 📞 Contact

If you encounter issues on the company computer:
- Check this guide first
- Review `docs/SETUP-SUMMARY.md`
- Run `python setup-check.py` for diagnostics

---

## ✅ Success Criteria

You're ready to test when:
- [ ] `python setup-check.py` shows 5/5 passed
- [ ] Backend starts without errors
- [ ] Can access http://localhost:8000/health
- [ ] Frontend opens in browser
- [ ] No critical errors in console

---

**Ready to test on company computer? Follow the steps above!** 🚀
