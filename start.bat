@echo off
REM Glossary Management System - Startup Script (Windows CMD)
REM Starts both backend and frontend servers

echo ========================================
echo   Glossary Management System Startup
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please create it first: python -m venv venv
    exit /b 1
)

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found! Please install Node.js first.
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [OK] Node.js version: %NODE_VERSION%

REM Check if frontend dependencies are installed
if not exist "src\frontend\node_modules" (
    echo [INFO] Installing frontend dependencies...
    cd src\frontend
    call npm install
    cd ..\..
    echo [OK] Frontend dependencies installed
)

echo.
echo Starting servers...
echo.

REM Kill existing processes
echo [INFO] Cleaning up existing processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 1 /nobreak >nul

REM Start Backend Server in new window
echo [1/2] Starting Backend Server (FastAPI)...
start "Glossary Backend" cmd /k "venv\Scripts\python.exe src\backend\app.py"
echo   -^> API: http://localhost:8000
echo   -^> Docs: http://localhost:8000/docs
timeout /t 3 /nobreak >nul

REM Start Frontend Server in new window
echo.
echo [2/2] Starting Frontend Server (React + Vite)...
cd src\frontend
start "Glossary Frontend" cmd /k "npm run dev"
cd ..\..
echo   -^> UI: http://localhost:3000

echo.
echo ========================================
echo   Servers Started Successfully!
echo ========================================
echo.
echo Backend API:  http://localhost:8000
echo API Docs:     http://localhost:8000/docs
echo Frontend UI:  http://localhost:3000
echo.
echo Check the new windows for server output
echo Close those windows to stop the servers
echo.
pause
