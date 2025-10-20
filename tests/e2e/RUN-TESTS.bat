@echo off
echo ========================================
echo Glossary APP - E2E Test Suite
echo ========================================
echo.

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing dependencies...
    call npm install
    echo.
)

REM Create screenshot directories if they don't exist
if not exist "test-screenshots\" mkdir test-screenshots
if not exist "test-screenshots\success\" mkdir test-screenshots\success
if not exist "test-screenshots\failures\" mkdir test-screenshots\failures
if not exist "test-screenshots\test\" mkdir test-screenshots\test

echo Checking if servers are running...
echo.
echo Expected:
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:9123
echo.

REM Check frontend
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Frontend not running on http://localhost:3000
    echo Please start the frontend: cd src/frontend ^&^& npm run dev
    echo.
    pause
    exit /b 1
)
echo [OK] Frontend is running

REM Check backend
curl -s http://localhost:9123 >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Backend not running on http://localhost:9123
    echo Please start the backend: cd backend ^&^& python run_backend.py
    echo.
    pause
    exit /b 1
)
echo [OK] Backend is running
echo.

echo Starting E2E Test Suite...
echo ========================================
echo.

REM Run tests
call npm test

echo.
echo ========================================
echo Test run completed!
echo.
echo Check results in:
echo   - test-results-consolidated.json
echo   - test-screenshots\ folder
echo.
pause
