@echo off
title Starting Glossary App...

cd /d "%~dp0"

echo.
echo ========================================
echo   STARTING GLOSSARY APP
echo ========================================
echo.

REM Kill any existing processes
echo Cleaning up old processes...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start Backend
echo Starting Backend...
start "Backend - DO NOT CLOSE" cmd /k "cd /d "%~dp0" && venv\Scripts\activate && uvicorn src.backend.app:app --host 0.0.0.0 --port 9123 --reload"
timeout /t 5 /nobreak >nul

REM Start Frontend
echo Starting Frontend...
start "Frontend - DO NOT CLOSE" cmd /k "cd /d "%~dp0\src\frontend" && npm run dev"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   SERVERS STARTED!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:9123
echo.
echo KEEP THE 2 NEW WINDOWS OPEN!
echo Close THIS window - it's safe.
echo.
pause
