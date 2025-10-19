@echo off
REM ============================================================================
REM Start ALL Servers - Backend + Frontend
REM ============================================================================

title Glossary App - Starting All Servers

echo.
echo ============================================================================
echo           GLOSSARY APP - STARTING ALL SERVERS
echo ============================================================================
echo.
echo This will open 2 windows:
echo   1. Backend Server (FastAPI on port 9123)
echo   2. Frontend Server (Vite on port 3000)
echo.
echo Keep BOTH windows open while using the app!
echo ============================================================================
echo.

cd /d "%~dp0"

echo [1/2] Starting Backend Server...
start "Glossary Backend (Port 9123)" /D "%~dp0" START-BACKEND.bat

echo.
echo Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak >nul

echo.
echo [2/2] Starting Frontend Server...
start "Glossary Frontend (Port 3000)" /D "%~dp0" START-FRONTEND.bat

echo.
echo ============================================================================
echo           SERVERS STARTING...
echo ============================================================================
echo.
echo Two windows have been opened:
echo   - Backend Server (port 9123)
echo   - Frontend Server (port 3000)
echo.
echo Wait ~10 seconds for both servers to fully start, then open:
echo   http://localhost:3000
echo.
echo To stop servers: Close both server windows or press Ctrl+C in each
echo ============================================================================
echo.

timeout /t 3 >nul
exit
