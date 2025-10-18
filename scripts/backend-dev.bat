@echo off
REM Backend Development Server Script
REM Does NOT require Administrator privileges

setlocal
cd /d "%~dp0\.."

echo ========================================
echo   Glossary App - Backend Dev Server
echo ========================================
echo.

REM Check if port 9123 is already in use
echo Checking if port 9123 is available...
netstat -ano | findstr :9123 >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo ERROR: Port 9123 is already in use!
    echo.
    echo Please close any existing backend process first:
    echo 1. Close the "Glossary Backend" window if running
    echo 2. Or check Task Manager for python.exe processes
    echo.
    pause
    exit /b 1
)

echo Port 9123 is available
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo Please ensure venv exists at: %CD%\venv
    pause
    exit /b 1
)

echo Starting backend with hot reload...
echo.
echo Backend URL: http://localhost:9123
echo API Docs:    http://localhost:9123/docs
echo Health:      http://localhost:9123/health
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start uvicorn with hot reload
uvicorn src.backend.app:app --host 0.0.0.0 --port 9123 --reload

endlocal
