@echo off
REM Automated Database Backup Script for Windows
REM Runs the Python backup script with default settings

echo ================================================================================
echo Glossary Database Backup - Windows
echo ================================================================================
echo.

REM Change to project directory
cd /d "%~dp0\.."

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run backup script with compression and verification
python scripts\backup_database.py --compress --verify

REM Check exit code
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Backup failed!
    echo Check logs/backup.log for details
    pause
    exit /b 1
)

echo.
echo Backup completed successfully!
echo.

REM List recent backups
python scripts\backup_database.py --list

echo.
echo ================================================================================
pause
