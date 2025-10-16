@echo off
REM Quick Issue Reporter - Run this if you encounter errors

echo.
echo ========================================
echo Issue Reporter - Collecting Information
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo.
    echo Please provide this information manually:
    echo - Operating System: %OS%
    echo - Error message you received
    echo - What you were trying to do
    echo.
    echo Send this to: developer.hh-iot-systems@outlook.com
    echo.
    pause
    exit /b 1
)

REM Run the report generator
python scripts\report-issue.py

REM Open the report file
if exist issue-report.md (
    echo.
    echo Opening report file...
    notepad issue-report.md
)

pause
