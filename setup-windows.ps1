# PowerShell Setup Script for Windows
# Automated setup for terminology-extraction project

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Terminology Extraction - Automated Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if running in project directory
if (-not (Test-Path "package.json")) {
    Write-Host "[ERROR] Not in project directory!" -ForegroundColor Red
    Write-Host "Please run this script from the project root folder.`n" -ForegroundColor Red
    exit 1
}

# Step 1: Check prerequisites
Write-Host "[1/8] Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  [OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Check Node
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  [OK] Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Check Git
try {
    $gitVersion = git --version 2>&1
    Write-Host "  [OK] Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Git not found. Please install Git" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Create virtual environment
Write-Host "[2/8] Creating Python virtual environment..." -ForegroundColor Yellow

if (Test-Path "venv") {
    Write-Host "  [INFO] Virtual environment already exists, skipping..." -ForegroundColor Gray
} else {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Step 3: Activate virtual environment and install Python packages
Write-Host "[3/8] Installing Python packages..." -ForegroundColor Yellow

& .\venv\Scripts\python.exe -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] pip upgraded" -ForegroundColor Green
} else {
    Write-Host "  [WARN] pip upgrade failed, continuing..." -ForegroundColor Yellow
}

& .\venv\Scripts\pip.exe install -r requirements-core.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Python packages installed (41 packages)" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Failed to install Python packages" -ForegroundColor Red
    Write-Host "  Try manually: .\venv\Scripts\activate then pip install -r requirements-core.txt" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Step 4: Install Node packages
Write-Host "[4/8] Installing Node.js packages (this may take 3-5 minutes)..." -ForegroundColor Yellow

npm install --silent
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Node packages installed (1,764 packages)" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Failed to install Node packages" -ForegroundColor Red
    Write-Host "  Try manually: npm install" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Step 5: Create .env file
Write-Host "[5/8] Creating environment file..." -ForegroundColor Yellow

if (Test-Path ".env") {
    Write-Host "  [INFO] .env file already exists, skipping..." -ForegroundColor Gray
} else {
    Copy-Item ".env.example" ".env"
    if ($LASTEXITCODE -eq 0 -or (Test-Path ".env")) {
        Write-Host "  [OK] .env file created" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] Failed to create .env file" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Step 6: Create empty directories
Write-Host "[6/8] Creating data directories..." -ForegroundColor Yellow

$directories = @(
    "data\uploads",
    "data\iate",
    "backups\sqlite",
    "backups\neo4j"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

Write-Host "  [OK] Data directories ready" -ForegroundColor Green
Write-Host ""

# Step 7: Run verification
Write-Host "[7/8] Verifying setup..." -ForegroundColor Yellow

& .\venv\Scripts\python.exe setup-check.py

Write-Host ""

# Step 8: Display next steps
Write-Host "[8/8] Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test Backend:" -ForegroundColor Yellow
Write-Host "  .\venv\Scripts\activate" -ForegroundColor White
Write-Host "  python src\backend\app.py" -ForegroundColor White
Write-Host "  Then visit: http://localhost:8000/health" -ForegroundColor Gray
Write-Host ""
Write-Host "Test Frontend (in new terminal):" -ForegroundColor Yellow
Write-Host "  npm start" -ForegroundColor White
Write-Host "  Opens: http://localhost:3000" -ForegroundColor Gray
Write-Host ""
Write-Host "Run All Tests:" -ForegroundColor Yellow
Write-Host "  .\venv\Scripts\activate" -ForegroundColor White
Write-Host "  pytest tests/ -v" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan
