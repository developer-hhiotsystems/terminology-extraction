@echo off
REM Stop Backend Server Script

echo ========================================
echo   Stopping Glossary Backend
echo ========================================
echo.

echo Terminating Python processes...
taskkill /F /FI "WINDOWTITLE eq Glossary Backend*" >nul 2>&1
taskkill /F /FI "IMAGENAME eq python.exe" /FI "COMMANDLINE eq *app.py*" >nul 2>&1
taskkill /F /FI "IMAGENAME eq python.exe" /FI "COMMANDLINE eq *uvicorn*" >nul 2>&1

echo.
echo Backend stopped successfully
echo.
