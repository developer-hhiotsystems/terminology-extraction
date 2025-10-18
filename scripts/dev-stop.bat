@echo off
REM Stop both Backend and Frontend servers
REM Kills processes by port number for precise targeting

echo ========================================
echo   Stopping Development Environment
echo ========================================
echo.

REM Function to kill process by port
REM Kill backend on port 9123
echo [1/3] Stopping backend (Port 9123)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :9123 ^| findstr LISTENING') do (
    echo   - Found process PID: %%a
    taskkill /F /PID %%a /T >nul 2>&1
    if %errorlevel% equ 0 (
        echo   - Backend process %%a stopped
    )
)

REM Kill frontend on port 3000
echo [2/3] Stopping frontend (Port 3000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
    echo   - Found process PID: %%a
    taskkill /F /PID %%a /T >nul 2>&1
    if %errorlevel% equ 0 (
        echo   - Frontend process %%a stopped
    )
)

REM Verify ports are released
echo [3/3] Verifying ports are free...
timeout /t 2 /nobreak >nul

netstat -ano | findstr :9123 >nul 2>&1
if %errorlevel% equ 0 (
    echo   - WARNING: Port 9123 still in use
    echo   - Try running: for /f "tokens=5" %%a in ('netstat -ano ^| findstr :9123') do taskkill /F /PID %%a
) else (
    echo   - Port 9123 is now free
)

netstat -ano | findstr :3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo   - WARNING: Port 3000 still in use
    echo   - Try running: for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do taskkill /F /PID %%a
) else (
    echo   - Port 3000 is now free
)

echo.
echo ========================================
echo   Development Environment Stopped
echo ========================================
echo.
