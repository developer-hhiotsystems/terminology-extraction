@echo off
REM Quick Start Script for Testing Glossary App
REM This script starts the backend server

echo ========================================================================
echo           GLOSSARY APP - STARTING BACKEND SERVER
echo ========================================================================
echo.

echo Step 1: Activating Python virtual environment...
call venv\Scripts\activate
echo Virtual environment activated!
echo.

echo Step 2: Starting Backend Server on http://localhost:9123
echo.
echo NOTE: Keep this window open while testing!
echo.
echo To stop the server: Press Ctrl+C
echo.
echo ========================================================================
echo.

venv\Scripts\python.exe src\backend\app.py
