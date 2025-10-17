@echo off
REM Stop both Backend and Frontend servers
REM Does NOT require Administrator privileges

echo ========================================
echo   Stopping Development Environment
echo ========================================
echo.

echo Instructions to stop servers:
echo.
echo 1. Close the "Glossary Backend" console window
echo 2. Close the "Glossary Frontend" console window
echo.
echo OR press Ctrl+C in each window
echo.
echo If windows are not responding, you can:
echo - Right-click window title bar ^> Close
echo - Use Task Manager to end the processes
echo.
echo ========================================
echo.

REM Try gentle shutdown without force (no admin needed)
echo Attempting to close windows...
taskkill /FI "WINDOWTITLE eq Glossary Backend*" >nul 2>&1
taskkill /FI "WINDOWTITLE eq Glossary Frontend*" >nul 2>&1

echo.
echo If servers are still running, please close them manually.
echo.
