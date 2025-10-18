@echo off
REM Start both Backend and Frontend in development mode
REM Does NOT require Administrator privileges

setlocal
cd /d "%~dp0\.."

echo ========================================
echo   Glossary App - Full Dev Environment
echo ========================================
echo.

REM Check if processes are already running
echo [1/4] Checking for running processes...

REM Check backend
netstat -ano | findstr :9123 >nul 2>&1
if %errorlevel% equ 0 (
    echo WARNING: Port 9123 already in use - backend may already be running
    echo Please close existing backend window or run dev-stop.bat first
    echo.
    choice /C YN /M "Continue anyway"
    if errorlevel 2 goto :end
)

REM Check frontend
netstat -ano | findstr :3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo WARNING: Port 3000 already in use - frontend may already be running
    echo Please close existing frontend window or manually close it
    echo.
    choice /C YN /M "Continue anyway"
    if errorlevel 2 goto :end
)

REM Start backend in new window
echo [2/4] Starting backend server...
start "Glossary Backend" cmd /k "cd /d "%CD%" && venv\Scripts\activate && uvicorn src.backend.app:app --host 0.0.0.0 --port 9123 --reload"
timeout /t 5 /nobreak >nul

REM Start frontend in new window
echo [3/4] Starting frontend server...
start "Glossary Frontend" cmd /k "cd /d "%CD%\src\frontend" && npm run dev"
timeout /t 3 /nobreak >nul

echo [4/4] Verifying servers...
timeout /t 3 /nobreak >nul

curl -s http://localhost:9123/health >nul 2>&1
if errorlevel 1 (
    echo WARNING: Backend may not be ready yet ^(check "Glossary Backend" window^)
) else (
    echo Backend: http://localhost:9123 - READY
)

echo.
echo ========================================
echo   Development Environment Started
echo ========================================
echo.
echo Backend:  http://localhost:9123
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:9123/docs
echo.
echo Both servers are running in separate windows.
echo To stop: Close the windows or press Ctrl+C in each
echo ========================================
echo.

:end
endlocal
