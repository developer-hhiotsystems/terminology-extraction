@echo off
REM ============================================================================
REM Start Backend Server (FastAPI on port 9123)
REM ============================================================================

title Glossary App - Backend Server

echo.
echo ============================================================================
echo           STARTING BACKEND SERVER
echo ============================================================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting FastAPI backend on port 9123...
echo.
echo ============================================================================
echo BACKEND RUNNING - Keep this window OPEN!
echo ============================================================================
echo.
echo You should see:
echo   - "All routers loaded. Total routes: 39"
echo   - "Uvicorn running on http://0.0.0.0:9123"
echo   - "Application startup complete"
echo.
echo Press Ctrl+C to stop the backend server
echo ============================================================================
echo.

python src\backend\app.py

pause
