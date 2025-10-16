@echo off
REM Batch Script Setup for Windows
REM Automated setup for terminology-extraction project

echo.
echo ========================================
echo Terminology Extraction - Automated Setup
echo ========================================
echo.

REM Check if in project directory
if not exist package.json (
    echo [ERROR] Not in project directory!
    echo Please run this script from the project root folder.
    echo.
    pause
    exit /b 1
)

REM Step 1: Check prerequisites
echo [1/8] Checking prerequisites...

python --version >nul 2>&1
if errorlevel 1 (
    echo   [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)
echo   [OK] Python found

node --version >nul 2>&1
if errorlevel 1 (
    echo   [ERROR] Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)
echo   [OK] Node.js found

git --version >nul 2>&1
if errorlevel 1 (
    echo   [ERROR] Git not found. Please install Git
    pause
    exit /b 1
)
echo   [OK] Git found
echo.

REM Step 2: Create virtual environment
echo [2/8] Creating Python virtual environment...

if exist venv (
    echo   [INFO] Virtual environment already exists, skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo   [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo   [OK] Virtual environment created
)
echo.

REM Step 3: Install Python packages
echo [3/8] Installing Python packages...

call .\venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
.\venv\Scripts\pip.exe install -r requirements-core.txt
if errorlevel 1 (
    echo   [ERROR] Failed to install Python packages
    echo   Try manually: .\venv\Scripts\activate then pip install -r requirements-core.txt
    pause
    exit /b 1
)
echo   [OK] Python packages installed (41 packages)
echo.

REM Step 4: Install Node packages
echo [4/8] Installing Node.js packages (this may take 3-5 minutes)...

call npm install
if errorlevel 1 (
    echo   [ERROR] Failed to install Node packages
    echo   Try manually: npm install
    pause
    exit /b 1
)
echo   [OK] Node packages installed (1,764 packages)
echo.

REM Step 5: Create .env file
echo [5/8] Creating environment file...

if exist .env (
    echo   [INFO] .env file already exists, skipping...
) else (
    copy .env.example .env >nul
    echo   [OK] .env file created
)
echo.

REM Step 6: Create directories
echo [6/8] Creating data directories...

if not exist data\uploads mkdir data\uploads
if not exist data\iate mkdir data\iate
if not exist backups\sqlite mkdir backups\sqlite
if not exist backups\neo4j mkdir backups\neo4j

echo   [OK] Data directories ready
echo.

REM Step 7: Verify setup
echo [7/8] Verifying setup...

.\venv\Scripts\python.exe setup-check.py
echo.

REM Step 8: Complete
echo [8/8] Setup complete!
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo.
echo Test Backend:
echo   .\venv\Scripts\activate
echo   python src\backend\app.py
echo   Then visit: http://localhost:8000/health
echo.
echo Test Frontend (in new terminal):
echo   npm start
echo   Opens: http://localhost:3000
echo.
echo Run All Tests:
echo   .\venv\Scripts\activate
echo   pytest tests/ -v
echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
pause
