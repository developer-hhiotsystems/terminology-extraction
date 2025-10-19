@echo off
REM ========================================================================
REM   AUTOMATIC ERROR FIX - Starts Backend Server
REM ========================================================================

echo.
echo ========================================================================
echo                    FIXING ALL UI ERRORS
echo ========================================================================
echo.
echo The issue: Backend server is not running
echo The fix: Starting backend server now...
echo.
echo ========================================================================
echo.

echo [1/3] Checking Python environment...
if exist venv\Scripts\python.exe (
    echo     ✓ Python virtual environment found
) else (
    echo     ❌ ERROR: Virtual environment not found!
    echo     Please run: python -m venv venv
    pause
    exit /b 1
)
echo.

echo [2/3] Starting Backend Server on http://localhost:9123
echo.
echo IMPORTANT: Keep this window OPEN!
echo The backend server must stay running for the app to work.
echo.
echo To stop the server: Press Ctrl+C
echo.
echo ========================================================================
echo.

venv\Scripts\python.exe src\backend\app.py

pause
