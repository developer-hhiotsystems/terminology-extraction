@echo off
title Stopping Glossary App...

echo.
echo ========================================
echo   STOPPING ALL SERVERS
echo ========================================
echo.

echo Killing all Python processes...
taskkill /F /IM python.exe /T
echo.

echo Killing all Node processes...
taskkill /F /IM node.exe /T
echo.

echo ========================================
echo   ALL SERVERS STOPPED!
echo ========================================
echo.
pause
