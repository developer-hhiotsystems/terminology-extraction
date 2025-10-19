@echo off
REM ============================================================================
REM Start Frontend Server (Vite on port 3000)
REM ============================================================================

title Glossary App - Frontend Server

echo.
echo ============================================================================
echo           STARTING FRONTEND SERVER
echo ============================================================================
echo.

REM Go to project root (2 levels up from scripts/startup/)
cd /d "%~dp0"
cd ..\..
cd src\frontend

echo.
echo Starting Vite dev server on port 3000...
echo.
echo ============================================================================
echo FRONTEND RUNNING - Keep this window OPEN!
echo ============================================================================
echo.
echo You should see:
echo   - "VITE v5.x.x ready in XXX ms"
echo   - "Local: http://localhost:3000/"
echo.
echo Press Ctrl+C to stop the frontend server
echo ============================================================================
echo.

call npm run dev

pause
