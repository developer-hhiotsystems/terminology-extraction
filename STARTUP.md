# Glossary Management System - Startup Guide

Quick guide to start the full-stack application.

## Prerequisites

- Python 3.8+ with virtual environment
- Node.js 16+ and npm
- Git (optional)

## Quick Start

### Windows (PowerShell) - Recommended
```powershell
.\start.ps1
```

### Windows (CMD)
```cmd
start.bat
```

### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

## What the Scripts Do

1. ✓ Check for virtual environment
2. ✓ Check for Node.js installation
3. ✓ Install frontend dependencies (if needed)
4. ✓ Clean up existing processes
5. ✓ Start Backend Server (FastAPI on port 8000)
6. ✓ Start Frontend Server (React on port 3000)
7. ✓ Display access URLs

## Access Points

Once started, access the application at:

- **Frontend UI:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **API Health Check:** http://localhost:8000/health

## Manual Startup

If you prefer to start servers manually:

### Backend (Terminal 1)
```bash
# Windows
.\venv\Scripts\activate
python src\backend\app.py

# Linux/Mac
source venv/bin/activate
python src/backend/app.py
```

### Frontend (Terminal 2)
```bash
cd src/frontend
npm install  # First time only
npm run dev
```

## Stopping the Servers

### Using Startup Scripts
- **PowerShell:** Press `Ctrl+C`
- **CMD (start.bat):** Close the server windows
- **Bash (start.sh):** Press `Ctrl+C`

### Manual Stop
```bash
# Windows
taskkill /F /IM python.exe
taskkill /F /IM node.exe

# Linux/Mac
pkill -f "python.*app.py"
pkill -f "vite"
```

## Troubleshooting

### Port Already in Use

**Backend (8000):**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill
```

**Frontend (3000):**
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill
```

### Virtual Environment Not Found

Create it:
```bash
python -m venv venv
```

Install backend dependencies:
```bash
# Windows
.\venv\Scripts\activate
pip install -r requirements-core.txt

# Linux/Mac
source venv/bin/activate
pip install -r requirements-core.txt
```

### Node Modules Not Found

Install frontend dependencies:
```bash
cd src/frontend
npm install
```

### Backend Won't Start

Check Python version:
```bash
python --version  # Should be 3.8+
```

Check if dependencies are installed:
```bash
.\venv\Scripts\pip list  # Windows
./venv/bin/pip list      # Linux/Mac
```

### Frontend Won't Start

Check Node.js version:
```bash
node --version  # Should be 16+
npm --version
```

Clear npm cache:
```bash
cd src/frontend
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

## Development Workflow

1. **Start servers:** Run startup script
2. **Access UI:** Open http://localhost:3000
3. **Make changes:** Edit code (auto-reload enabled)
4. **Test API:** Use http://localhost:8000/docs
5. **Stop servers:** Ctrl+C or close windows

## Production Build

### Frontend
```bash
cd src/frontend
npm run build
# Output in dist/
```

### Backend
Already production-ready. For deployment:
```bash
pip install gunicorn  # Linux
uvicorn src.backend.app:app --host 0.0.0.0 --port 8000
```

## Features Available

### Glossary Management
- View all entries (Grid view)
- Search by term/definition
- Filter by language (EN/DE)
- Filter by source
- Create new entries
- Edit entries
- Delete entries

### PDF Processing
- Upload PDF documents (Drag & drop)
- Configure processing options
- Extract terms automatically
- View processing results
- Manage documents

## Next Steps

1. Upload a PDF document
2. Process it to extract terms
3. Review extracted terms in glossary
4. Edit/validate terms
5. Export or integrate with other systems

## Support

- **Documentation:** See README.md files
- **API Docs:** http://localhost:8000/docs
- **Frontend Guide:** src/frontend/README.md
- **Backend Guide:** src/backend/README.md (if exists)

## System Requirements

**Minimum:**
- 2GB RAM
- 500MB disk space
- Modern web browser

**Recommended:**
- 4GB+ RAM
- 1GB+ disk space
- Chrome/Firefox/Edge (latest)

---

**Happy Coding!** 🚀
