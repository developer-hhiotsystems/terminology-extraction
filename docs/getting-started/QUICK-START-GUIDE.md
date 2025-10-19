# 🚀 Quick Start Guide - Glossary App

**Last Updated:** 2025-10-19

---

## ⚡ **Option 1: Start Everything (Recommended)**

### **Double-click this file:**
```
START-ALL-SERVERS.bat
```

**What happens:**
- Opens 2 windows (Backend + Frontend)
- Wait ~10 seconds for both to start
- Open browser: http://localhost:3000
- **Done!** 🎉

---

## 🔧 **Option 2: Start Servers Individually**

### **Step 1: Start Backend (First!)**
Double-click:
```
START-BACKEND.bat
```

**Wait for:**
```
✅ "All routers loaded. Total routes: 39"
✅ "Uvicorn running on http://0.0.0.0:9123"
✅ "Application startup complete"
```

### **Step 2: Start Frontend (Second!)**
Double-click:
```
START-FRONTEND.bat
```

**Wait for:**
```
✅ "Local: http://localhost:3000/"
```

### **Step 3: Open Browser**
```
http://localhost:3000
```

---

## 📋 **Manual Command Line Start**

### **Terminal 1 - Backend:**
```cmd
cd "C:\Users\devel\Coding Projects\Glossary APP"
venv\Scripts\python.exe src\backend\app.py
```

### **Terminal 2 - Frontend:**
```cmd
cd "C:\Users\devel\Coding Projects\Glossary APP\src\frontend"
npm run dev
```

---

## ✅ **Success Checklist**

### **Backend Running:**
- [ ] Terminal shows "Total routes: 39"
- [ ] Terminal shows "Uvicorn running on http://0.0.0.0:9123"
- [ ] http://localhost:9123/health returns JSON (test in browser)

### **Frontend Running:**
- [ ] Terminal shows "Local: http://localhost:3000/"
- [ ] http://localhost:3000 shows the app homepage

### **Both Connected:**
- [ ] No "Failed to load" errors in browser
- [ ] Glossary data loads when you click "Glossary"
- [ ] No red errors in browser console (F12)

---

## ⚠️ **Troubleshooting**

### **Problem: "Port already in use"**

**Check what's on the port:**
```cmd
netstat -ano | findstr :9123
netstat -ano | findstr :3000
```

**Kill the process (replace XXXX with PID from above):**
```cmd
taskkill /F /PID XXXX
```

### **Problem: Backend won't start**

**Error: "ModuleNotFoundError"**
- Make sure you're in the correct directory
- Make sure virtual environment is activated
- Try: `venv\Scripts\pip install -r requirements.txt`

**Error: "Address already in use"**
- Another backend instance is running
- Check for python.exe processes: `tasklist | findstr python`
- Kill them: `taskkill /F /IM python.exe`

### **Problem: Frontend won't start**

**Error: "npm not found"**
- Install Node.js: https://nodejs.org/

**Error: "Cannot find module"**
- Run: `npm install` in `src/frontend` directory

**Error: "Port 3000 is already in use"**
- Kill the process: `taskkill /F /PID XXXX`
- Or change port in `src/frontend/vite.config.ts`

---

## 🛑 **How to Stop Servers**

### **If using .bat files:**
- Close the terminal windows
- Or press **Ctrl+C** in each window

### **If using command line:**
- Press **Ctrl+C** in each terminal

### **Nuclear option (kill all):**
```cmd
taskkill /F /IM python.exe /T
taskkill /F /IM node.exe /T
```

---

## 🎯 **New Features Accessible After Integration**

Once both servers are running, navigate to:

### **1. 🔍 Search** (http://localhost:3000/search)
- FTS5 full-text search (10.6x faster!)
- Real-time autocomplete
- 4 search modes: Simple, Phrase, Boolean, Wildcard
- Advanced filters

### **2. ✨ Enhanced View** (http://localhost:3000/enhanced-glossary)
- Bilingual cards (EN/DE side-by-side)
- Term detail modal
- Bulk operations (select, export, delete)
- Upload progress tracking

### **3. 🕸️ Relationships** (http://localhost:3000/relationships)
- Interactive graph visualization
- D3.js force-directed layout
- Relationship extraction via NLP
- Zoom, pan, drag nodes

---

## 📁 **File Locations**

```
Glossary APP/
├── START-ALL-SERVERS.bat       ⭐ Start everything (recommended)
├── START-BACKEND.bat            🔧 Start backend only
├── START-FRONTEND.bat           🔧 Start frontend only
├── QUICK-START-GUIDE.md         📖 This file
├── src/
│   ├── backend/
│   │   └── app.py               🐍 Backend entry point
│   └── frontend/
│       └── package.json         📦 Frontend configuration
└── venv/                        🔧 Python virtual environment
```

---

## 🆘 **Getting Help**

### **Check Backend Health:**
```
http://localhost:9123/health
```

Should return:
```json
{
  "status": "healthy",
  "database": {
    "status": "connected"
  }
}
```

### **Check API Documentation:**
```
http://localhost:9123/docs
```

Interactive API documentation (Swagger UI)

### **Check for Errors:**
1. Open browser console (F12)
2. Look for red errors
3. Check Network tab for failed requests

---

## 📊 **System Requirements**

- **Python:** 3.8+ (with virtual environment)
- **Node.js:** 16+ (with npm)
- **OS:** Windows (tested on Windows 10/11)
- **RAM:** 2GB minimum
- **Disk:** 500MB for dependencies

---

## ✨ **Next Steps**

Once servers are running:

1. **Test the features:**
   - Click through all navigation links
   - Try searching
   - Upload a PDF
   - Explore relationships

2. **Read the docs:**
   - `docs/INTEGRATION_COMPLETE.md` - Full feature list
   - `docs/PHASE_A_COMPLETION_GUIDE.md` - Search features
   - `docs/PHASE_B_COMPLETION_GUIDE.md` - UI/UX features
   - `docs/PHASE_C_COMPLETION_GUIDE.md` - Relationships

3. **Enjoy your app!** 🎉

---

**Happy glossary building!** 🚀
