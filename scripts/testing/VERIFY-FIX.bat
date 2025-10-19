@echo off
REM ========================================================================
REM   VERIFY THE FIX - Check if backend is running
REM ========================================================================

echo.
echo ========================================================================
echo                    VERIFYING BACKEND SERVER
echo ========================================================================
echo.

echo Checking if backend is running on port 9123...
echo.

curl -s http://localhost:9123/health > temp_health.txt 2>nul

if %ERRORLEVEL% EQU 0 (
    echo ========================================================================
    echo                    ✅ SUCCESS!
    echo ========================================================================
    echo.
    echo Backend server is running correctly!
    echo.
    type temp_health.txt
    echo.
    echo.
    echo Next steps:
    echo   1. Go to your browser at http://localhost:3000
    echo   2. Press F5 to refresh
    echo   3. All errors should be GONE!
    echo.
    echo ========================================================================
) else (
    echo ========================================================================
    echo                    ❌ BACKEND NOT RUNNING
    echo ========================================================================
    echo.
    echo Backend server is still not running.
    echo.
    echo To fix:
    echo   1. Run: FIX-ALL-ERRORS.bat
    echo   2. Leave that window open
    echo   3. Run this script again to verify
    echo.
    echo ========================================================================
)

del temp_health.txt 2>nul

echo.
pause
