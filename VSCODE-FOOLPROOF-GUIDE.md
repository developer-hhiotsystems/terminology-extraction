# VS Code Foolproof Setup Guide

**Follow these steps EXACTLY in order. Don't skip any step.**

---

## 📋 Before You Start

**Required software (install first if missing):**
- Python 3.10+ → https://www.python.org/downloads/
- Node.js 18+ → https://nodejs.org/
- Git → https://git-scm.com/downloads
- VS Code → https://code.visualstudio.com/

---

## STEP 1: Open VS Code

1. Click Windows Start button
2. Type: `Visual Studio Code`
3. Press Enter

**You should see:** VS Code opens (blue icon)

---

## STEP 2: Open Terminal in VS Code

1. Look at the top menu bar
2. Click: **Terminal**
3. Click: **New Terminal**

**You should see:** A terminal panel appears at the bottom with `PS C:\Users\YourName>`

**If you see CMD instead of PowerShell:**
- Click the dropdown arrow (▼) next to the + symbol
- Select: **PowerShell**

---

## STEP 3: Clone the Project

**In the terminal (bottom panel), type this EXACTLY:**

```powershell
cd ~
```

**Press Enter**

**Then type:**

```powershell
git clone https://github.com/developer-hhiotsystems/terminology-extraction.git
```

**Press Enter**

**You should see:**
```
Cloning into 'terminology-extraction'...
Receiving objects: 100% (XX/XX), done.
```

**If it asks for username/password:**
- Username: `developer-hhiotsystems`
- Password: Use a **Personal Access Token** (see "STEP 3B" below if needed)

---

### STEP 3B: If Git Asks for Password (ONLY IF NEEDED)

**Create a Personal Access Token:**

1. Open browser → https://github.com/settings/tokens
2. Click: **Generate new token (classic)**
3. Give it a name: `Company Computer`
4. Check the box: **repo** (includes all repo permissions)
5. Scroll down → Click: **Generate token**
6. **COPY the token immediately** (you won't see it again!)
7. Use this token as your password when git asks

---

## STEP 4: Open the Project Folder

**In VS Code terminal, type:**

```powershell
cd terminology-extraction
```

**Press Enter**

**Then type:**

```powershell
code .
```

**Press Enter**

**You should see:**
- Either VS Code reloads showing the project
- OR a new VS Code window opens with the project

**Look at the left sidebar** - you should see folders like:
- src
- tests
- docs
- node_modules (might appear later)
- etc.

---

## STEP 5: Install Extensions (IMPORTANT!)

**Within 10 seconds, you should see a blue notification in the bottom-right corner:**

> "This workspace has extension recommendations."

**Two buttons appear:**
- [Install All] [Show Recommendations]

**Click: "Install All"**

**You should see:**
- Extensions panel opens on the left
- 12 extensions start installing (showing progress spinners)
- Wait for ALL to finish (green checkmarks appear)

---

### STEP 5B: If You Don't See the Notification

**No problem, do this manually:**

1. Look at the left sidebar (vertical icons)
2. Click the **Extensions icon** (looks like 4 squares, one separated)
3. In the search box at the top, type: `@recommended`
4. You'll see "WORKSPACE RECOMMENDATIONS" section
5. Click the **cloud download icon** next to "WORKSPACE RECOMMENDATIONS"
6. Click: **Install All Workspace Recommendations**

**Wait for all 12 extensions to finish installing** (green checkmarks)

---

## STEP 6: Run the Setup Script

**In the terminal (bottom panel), type EXACTLY:**

```powershell
.\setup-windows.ps1
```

**Press Enter**

**You should see:**

```
========================================
Terminology Extraction - Automated Setup
========================================

[1/8] Checking prerequisites...
  [OK] Python found: Python 3.10.x
  [OK] Node.js found: v18.x.x
  [OK] Git found: git version 2.x.x

[2/8] Creating Python virtual environment...
  [OK] Virtual environment created

[3/8] Installing Python packages...
  [OK] Python packages installed (41 packages)

[4/8] Installing Node.js packages (this may take 3-5 minutes)...
  [OK] Node packages installed (1,764 packages)

[5/8] Creating environment file...
  [OK] .env file created

[6/8] Creating data directories...
  [OK] Data directories ready

[7/8] Verifying setup...
  [Verification results appear here]

[8/8] Setup complete!

========================================
Next Steps:
========================================
```

**This takes 5-10 minutes.** Watch for [OK] messages. All should be green.

---

### STEP 6B: If PowerShell Script is Blocked

**If you see this error:**
```
cannot be loaded because running scripts is disabled on this system
```

**Fix it:**

1. In terminal, type:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

2. Press Enter

3. Type: `Y` (for Yes)

4. Press Enter

5. Now run setup again:
```powershell
.\setup-windows.ps1
```

---

## STEP 7: Select Python Interpreter

**Look at the BOTTOM-LEFT corner of VS Code.**

You should see something like:
```
🐍 Python 3.10.x 64-bit
```

**Click on it.**

**A menu appears at the top** showing Python versions.

**Look for and click:**
```
Python 3.10.x ('venv': venv) .\venv\Scripts\python.exe
```

**The one that says "venv" in it!**

**You should see:** The bottom-left now shows `('venv')` or similar

---

### STEP 7B: If You Don't See Python in Bottom-Left

**Do this:**

1. Press: `Ctrl+Shift+P` (all three keys together)
2. A search box appears at the top
3. Type: `Python: Select Interpreter`
4. Click on that option when it appears
5. Look for: `.\venv\Scripts\python.exe` or `('venv')`
6. Click it

---

## STEP 8: Verify Terminal Shows (venv)

**Look at your terminal** (bottom panel).

You should see:
```
(venv) PS C:\Users\...\terminology-extraction>
```

**The `(venv)` at the start is IMPORTANT** - it means the virtual environment is active.

**If you DON'T see (venv):**

1. Close the current terminal (click the trash icon)
2. Open a new terminal: **Terminal → New Terminal**
3. You should now see `(venv)` appear

---

## STEP 9: Test Backend

**In the terminal, type:**

```powershell
python src\backend\app.py
```

**Press Enter**

**You should see:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Now open your browser:**
- Go to: `http://localhost:8000/health`

**You should see:**
```json
{"status":"healthy"}
```

**✅ BACKEND WORKS!**

**Go back to VS Code and stop the server:**
- Click in the terminal
- Press: `Ctrl+C`

---

## STEP 10: Test Frontend

**Open a NEW terminal:**
1. Click the **+** symbol at the top-right of the terminal panel
2. Make sure it says PowerShell

**In this NEW terminal, type:**

```powershell
npm start
```

**Press Enter**

**You should see:**
```
Compiled successfully!

You can now view glossary-app-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

**Your browser should automatically open to: http://localhost:3000**

**You should see:**
- A dark-themed application
- "Glossary Extraction & Validation" title
- Upload section or main page

**✅ FRONTEND WORKS!**

**To stop it:**
- Go back to VS Code
- Click in the second terminal (the one running npm)
- Press: `Ctrl+C`

---

## STEP 11: Run Tests

**In the terminal (make sure you see `(venv)`), type:**

```powershell
pytest tests/ -v
```

**Press Enter**

**You should see:**
```
========================== test session starts ==========================
tests/unit/test_example.py::test_example PASSED
tests/integration/test_example.py::test_integration PASSED
...
========================== 6 passed, 1 skipped in X.XXs ==========================
```

**✅ TESTS PASS!**

---

## 🎉 SUCCESS! Everything Works!

**You have successfully:**
- ✅ Cloned the project
- ✅ Installed VS Code extensions
- ✅ Run the setup script
- ✅ Selected the Python interpreter
- ✅ Tested the backend (port 8000)
- ✅ Tested the frontend (port 3000)
- ✅ Run all tests

**The project is fully working on your company computer!**

---

## 📸 Visual Checklist

**Your VS Code should look like this:**

**LEFT SIDEBAR:**
- Explorer icon (files) at top
- 12+ extensions installed

**BOTTOM-LEFT CORNER:**
- Shows: `🐍 Python 3.10.x ('venv')`

**BOTTOM PANEL (Terminal):**
- Shows: `(venv) PS C:\Users\...\terminology-extraction>`

**FOLDER STRUCTURE (Left panel):**
```
terminology-extraction/
├── src/
│   ├── backend/
│   └── frontend/
├── tests/
├── docs/
├── venv/          ← This folder exists
├── node_modules/  ← This folder exists
├── package.json
├── requirements-core.txt
└── setup-windows.ps1
```

---

## 🆘 If Something Goes Wrong

### Problem: "Python not found"

**Solution:**
1. Install Python from: https://www.python.org/downloads/
2. During installation, CHECK: "Add Python to PATH"
3. Restart VS Code
4. Try again from STEP 6

---

### Problem: "Node not found"

**Solution:**
1. Install Node.js from: https://nodejs.org/
2. Choose LTS version (left button)
3. Restart VS Code
4. Try again from STEP 6

---

### Problem: "Git not found"

**Solution:**
1. Install Git from: https://git-scm.com/downloads
2. Use all default options during installation
3. Restart VS Code
4. Try again from STEP 3

---

### Problem: Setup script has errors

**What to do:**
1. The script automatically creates: `setup-error-report.md`
2. Find this file in the project folder
3. Open it and read the error
4. Check: `TROUBLESHOOTING.md` for solutions

---

### Problem: Backend says "Port 8000 already in use"

**Solution:**

**Find what's using port 8000:**
```powershell
netstat -ano | findstr :8000
```

**Kill that process:**
```powershell
taskkill /PID [number] /F
```
(Replace `[number]` with the PID from previous command)

**Try starting backend again:**
```powershell
python src\backend\app.py
```

---

### Problem: Frontend says "Port 3000 already in use"

**Solution:**
- Same as above, but use `:3000` instead of `:8000`

---

### Problem: Extensions don't install

**Solution:**
1. Check internet connection
2. Try installing ONE extension manually:
   - Click Extensions icon (left sidebar)
   - Search: `Python`
   - Find: "Python" by Microsoft
   - Click: Install
3. If this works, install the others manually:
   - Pylance
   - ESLint
   - Prettier
   - ES7+ React/Redux/GraphQL snippets

---

### Problem: Can't see (venv) in terminal

**Solution:**
1. Close VS Code completely
2. Open VS Code again
3. Open project folder: **File → Open Folder** → Choose `terminology-extraction`
4. Open new terminal: **Terminal → New Terminal**
5. Should now show `(venv)`

---

### Problem: Tests fail

**Check you're in the right directory:**
```powershell
pwd
```

**Should show:**
```
Path
----
C:\Users\YourName\terminology-extraction
```

**If not, navigate there:**
```powershell
cd ~\terminology-extraction
```

**Try tests again:**
```powershell
pytest tests/ -v
```

---

## 📞 Still Stuck?

**Generate an automatic error report:**

```powershell
python scripts/report-issue.py
```

**This creates: `issue-report.md`**

**Send it to:**
- Email: developer.hh-iot-systems@outlook.com
- Or create GitHub issue: https://github.com/developer-hhiotsystems/terminology-extraction/issues/new

---

## 📚 Additional Help Files

**If you want more details:**

- `QUICK-START.md` - Fast overview
- `docs/VSCODE-SETUP.md` - Detailed VS Code guide
- `docs/COMPANY-COMPUTER-SETUP.md` - Company-specific instructions
- `docs/NO-DOCKER-SETUP.md` - Architecture explanation
- `TROUBLESHOOTING.md` - Common errors and solutions

---

## ✅ Final Checklist

**Before you finish, verify:**

- [ ] VS Code is open with the project folder
- [ ] Left sidebar shows project files
- [ ] 12 extensions installed (Extensions icon → @installed)
- [ ] Bottom-left shows Python with '(venv)'
- [ ] Terminal shows `(venv)` prefix
- [ ] `venv/` folder exists in project
- [ ] `node_modules/` folder exists in project
- [ ] Backend runs on port 8000 without errors
- [ ] Frontend runs on port 3000 and opens in browser
- [ ] Tests run and pass (6 passed, 1 skipped)

**ALL CHECKED? Perfect! Setup complete!** 🎉

---

**This guide is foolproof. Follow every step in order. Don't skip steps. You'll succeed!** ✅
