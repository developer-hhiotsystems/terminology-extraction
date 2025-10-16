# Quick Reference Card - Print This!

**Keep this open while setting up on company computer.**

---

## 🎯 The 5 Essential Commands

### 1️⃣ Clone Project
```powershell
cd ~
git clone https://github.com/developer-hhiotsystems/terminology-extraction.git
cd terminology-extraction
code .
```

### 2️⃣ Install Extensions
**Click notification: "Install All"**
*(Or: Extensions icon → @recommended → Install All)*

### 3️⃣ Run Setup
```powershell
.\setup-windows.ps1
```
*Takes 5-10 minutes. Wait for all [OK] messages.*

### 4️⃣ Select Python Interpreter
**Click bottom-left corner → Choose: `venv`**
*(Or: Ctrl+Shift+P → "Python: Select Interpreter" → venv)*

### 5️⃣ Test Everything
```powershell
# Terminal 1: Backend
python src\backend\app.py
# → Visit: http://localhost:8000/health

# Terminal 2: Frontend
npm start
# → Opens: http://localhost:3000

# Run Tests
pytest tests/ -v
# → Should see: 6 passed, 1 skipped
```

---

## ✅ Success Checklist

- [ ] Terminal shows: `(venv) PS C:\...>`
- [ ] Bottom-left shows: `Python ('venv')`
- [ ] Backend responds at port 8000
- [ ] Frontend opens at port 3000
- [ ] Tests pass

**All checked? You're done!** 🎉

---

## 🆘 Quick Fixes

| Problem | Fix |
|---------|-----|
| Scripts disabled | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Port in use | `netstat -ano \| findstr :8000` then `taskkill /PID [number] /F` |
| No (venv) | Close/reopen terminal or reload VS Code |
| No extensions notification | Extensions icon → @recommended → Install All |
| Python not found | Install from python.org, check "Add to PATH" |

---

## 📄 Full Guides Available

- **VSCODE-FOOLPROOF-GUIDE.md** ← Complete step-by-step (11 steps)
- **QUICK-START.md** ← 5-minute overview
- **TROUBLESHOOTING.md** ← All error solutions
- **docs/COMPANY-COMPUTER-SETUP.md** ← Company-specific

---

## 📞 If Stuck

**Generate error report:**
```powershell
python scripts/report-issue.py
```

**Send to:** developer.hh-iot-systems@outlook.com

---

**Repository:** https://github.com/developer-hhiotsystems/terminology-extraction

**This card has everything you need!** ✅
