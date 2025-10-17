# Glossary App - Development Scripts

This directory contains convenient scripts for managing the development environment.

## Quick Start

### Start Everything
```bash
# Start both backend and frontend servers
scripts\dev-start.bat
```

### Stop Everything
```bash
# Stop all running servers
scripts\dev-stop.bat
```

## Individual Scripts

### Backend Management

#### `backend-dev.bat`
Starts the backend development server with hot reload enabled.

**Features:**
- Automatically stops any existing backend processes
- Activates virtual environment
- Starts uvicorn with `--reload` flag
- Monitors `src\backend` directory for changes
- Auto-reloads on file changes

**Usage:**
```bash
scripts\backend-dev.bat
```

**Output:**
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

#### `backend-stop.bat`
Stops all running backend processes.

**Usage:**
```bash
scripts\backend-stop.bat
```

### Full Stack Management

#### `dev-start.bat`
Starts both backend and frontend in separate windows.

**What it does:**
1. Cleans up any existing processes
2. Starts backend with hot reload
3. Starts frontend dev server (Vite)
4. Verifies both servers are running

**Windows Opened:**
- "Glossary Backend" - Backend server console
- "Glossary Frontend" - Frontend dev server console

#### `dev-stop.bat`
Stops both backend and frontend servers.

## Hot Reload Features

### Backend Hot Reload
The backend uses uvicorn's `--reload` feature which automatically:
- Watches for file changes in `src/backend/`
- Reloads the server when Python files are modified
- Preserves database connections
- No manual restart needed!

**Watched directories:**
- `src/backend/routers/`
- `src/backend/services/`
- `src/backend/*.py`

### Frontend Hot Reload
The frontend uses Vite which provides:
- Instant hot module replacement (HMR)
- Fast refresh for React components
- No page reload needed for most changes

## Troubleshooting

### Backend won't start
```bash
# 1. Stop all processes
scripts\backend-stop.bat

# 2. Check if port 8000 is in use
netstat -ano | findstr :8000

# 3. Kill process if needed
taskkill /F /PID <PID>

# 4. Start backend
scripts\backend-dev.bat
```

### Frontend won't start
```bash
# 1. Stop frontend
taskkill /F /FI "IMAGENAME eq node.exe"

# 2. Clear node_modules if needed
cd src\frontend
rmdir /s /q node_modules
npm install

# 3. Start frontend
npm run dev
```

### Hot reload not working

**Backend:**
- Ensure you're using `backend-dev.bat` (not `python src\backend\app.py`)
- Check that files are being saved in `src/backend/` directory
- Look for syntax errors in console output

**Frontend:**
- Vite should auto-reload
- Check browser console for errors
- Try hard refresh (Ctrl+F5)

### Changes not reflecting

**Backend:**
1. Check console for reload messages
2. Verify file was saved
3. Check for Python syntax errors
4. Restart backend if needed: `scripts\backend-dev.bat`

**Frontend:**
1. Check browser console
2. Verify file was saved
3. Try hard refresh (Ctrl+F5)
4. Check Vite console for errors

## Development Workflow

### Recommended Daily Workflow

**Morning:**
```bash
# Start everything
scripts\dev-start.bat
```

**During Development:**
- Edit files normally
- Backend auto-reloads on save
- Frontend hot-reloads instantly
- No manual restarts needed!

**End of Day:**
```bash
# Stop everything
scripts\dev-stop.bat
```

### Making Backend Changes

1. Edit any file in `src/backend/`
2. Save the file
3. Watch console - should see: `Reloading...`
4. Test changes immediately

**Example:**
```python
# src/backend/routers/admin.py
# Make your changes and save
# Backend automatically reloads within 1-2 seconds
```

### Making Frontend Changes

1. Edit any file in `src/frontend/src/`
2. Save the file
3. Browser updates instantly
4. No refresh needed (HMR)

## Port Configuration

| Service  | Port | URL                     |
|----------|------|-------------------------|
| Backend  | 8000 | http://localhost:8000   |
| Frontend | 3000 | http://localhost:3000   |
| API Docs | 8000 | http://localhost:8000/docs |

## Environment Variables

Backend uses these environment variables (optional):
```bash
DATABASE_URL=sqlite:///./data/glossary.db
UPLOAD_DIR=./data/uploads
MAX_UPLOAD_SIZE=52428800
ENVIRONMENT=development
```

Frontend uses:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Advanced Usage

### Custom Port for Backend
Edit `scripts\backend-dev.bat`:
```batch
uvicorn src.backend.app:app --host 0.0.0.0 --port 8080 --reload
```

### Custom Port for Frontend
Edit `src\frontend\vite.config.ts`:
```typescript
server: {
  port: 3001
}
```

### Debug Mode
For detailed logs:
```bash
# Backend with debug logging
uvicorn src.backend.app:app --reload --log-level debug

# Frontend with debug
npm run dev -- --debug
```

## Tips

1. **Always use the scripts** - They handle cleanup automatically
2. **Keep console windows open** - You'll see errors immediately
3. **Watch for reload messages** - Confirms hot reload is working
4. **Use API docs** - http://localhost:8000/docs is always up-to-date
5. **Check health endpoint** - http://localhost:8000/health for quick status

## Need Help?

1. Check console output for errors
2. Review troubleshooting section above
3. Ensure virtual environment is activated
4. Verify all dependencies are installed:
   ```bash
   # Backend
   pip install -r requirements-core.txt

   # Frontend
   cd src/frontend
   npm install
   ```
