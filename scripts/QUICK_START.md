# Quick Start Guide

## No Administrator Rights Required!

All scripts work without Administrator/elevated privileges.

---

## Option 1: Start Everything (Recommended)

```bash
scripts\dev-start.bat
```

**What it does**:
- Checks if ports 8000 and 3000 are available
- Starts backend in window: "Glossary Backend"
- Starts frontend in window: "Glossary Frontend"
- Shows you the URLs

**To stop**:
- Close both console windows (X button or Ctrl+C)
- Or run `scripts\dev-stop.bat` for instructions

---

## Option 2: Start Manually (More Control)

### Backend (Terminal 1):
```bash
scripts\backend-dev.bat
```

### Frontend (Terminal 2):
```bash
cd src\frontend
npm run dev
```

**To stop**: Press Ctrl+C in each terminal

---

## ⚠️ Troubleshooting

### "Port already in use" error

**Backend (port 8000)**:
1. Close the "Glossary Backend" window
2. Or check Task Manager → Details → look for `python.exe`
3. End the python.exe process that's using port 8000

**Frontend (port 3000)**:
1. Close the "Glossary Frontend" window
2. Or check Task Manager → Details → look for `node.exe`
3. End the node.exe process that's using port 3000

### "Cannot find module" error

**Backend**:
```bash
cd "C:\Users\devel\Coding Projects\Glossary APP"
venv\Scripts\activate
pip install -r requirements-core.txt
```

**Frontend**:
```bash
cd "C:\Users\devel\Coding Projects\Glossary APP\src\frontend"
npm install
```

### Scripts won't run

Make sure you're in the project root:
```bash
cd "C:\Users\devel\Coding Projects\Glossary APP"
scripts\dev-start.bat
```

---

## Daily Workflow

### Morning - Start Work
```bash
# From project root
scripts\dev-start.bat

# Wait for both windows to show "ready"
# Open http://localhost:3000
```

### During Day - Make Changes
- Edit any file in `src/backend/` → Backend auto-reloads
- Edit any file in `src/frontend/src/` → Frontend auto-updates
- **No manual restarts needed!**

### Evening - End Work
- Close the "Glossary Backend" window
- Close the "Glossary Frontend" window
- Done!

---

## Company Computer Setup

Since you won't have Administrator rights:

### First Time Setup:
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Install backend dependencies
venv\Scripts\activate
pip install -r requirements-core.txt

# 3. Install frontend dependencies
cd src\frontend
npm install
```

### Daily Usage:
```bash
# Just use the scripts - no admin needed!
scripts\dev-start.bat
```

**Important**: The scripts check for port availability instead of forcefully killing processes, so they work without admin rights.

---

## URLs Reference

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Main application |
| Backend API | http://localhost:8000 | API endpoints |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Health Check | http://localhost:8000/health | Backend status |

---

## Port Configuration

If you need to change ports (e.g., company firewall):

### Backend Port (default: 8000)
Edit: `src/backend/config.py`
```python
API_PORT = 8080  # Change to desired port
```

### Frontend Port (default: 3000)
Edit: `src/frontend/vite.config.ts`
```typescript
server: {
  port: 3001  // Change to desired port
}
```

Then update `VITE_API_BASE_URL` in `src/frontend/.env`:
```bash
VITE_API_BASE_URL=http://localhost:8080
```

---

## Need Help?

1. Check console windows for error messages
2. Verify ports are not in use: `netstat -ano | findstr :8000`
3. Review full documentation: `scripts/README.md`
4. Check project progress: `docs/DEVELOPMENT_PROGRESS.md`
