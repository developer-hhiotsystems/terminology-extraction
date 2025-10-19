# Quick Start After PC Restart

## 🚀 3-Step Quick Start

### **Step 1: Start Backend** (Terminal 1)

Open Command Prompt and run:

```cmd
cd "C:\Users\devel\Coding Projects\Glossary APP"
venv\Scripts\python.exe src\backend\app.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:9123
```

✅ **Keep this window OPEN!**

---

### **Step 2: Start Frontend** (Terminal 2 - NEW window)

Open a NEW Command Prompt and run:

```cmd
cd "C:\Users\devel\Coding Projects\Glossary APP\src\frontend"
npm run dev
```

**Expected output:**
```
Local:   http://localhost:3000/
```

✅ **Keep this window OPEN too!**

---

### **Step 3: Test in Browser**

Open your browser to:
```
http://localhost:3000
```

**You should see:**
- ✅ Glossary App homepage
- ✅ No console errors
- ✅ Data loads when you click "Glossary"
- ✅ Search works

---

## ✅ Success Checklist

- [ ] Backend terminal shows "Uvicorn running"
- [ ] Frontend terminal shows "Local: http://localhost:3000"
- [ ] Browser loads http://localhost:3000 without errors
- [ ] Backend health check works: http://localhost:9123/health

---

## ❌ If Still Not Working

Run these commands to check:

**Check ports:**
```cmd
netstat -ano | findstr :9123
netstat -ano | findstr :3000
```

**Check backend health:**
```cmd
curl http://localhost:9123/health
```

If you see any errors, note them and we'll debug!

---

**For full details, see:** `CURRENT_STATUS_AND_PROBLEMS.md`
