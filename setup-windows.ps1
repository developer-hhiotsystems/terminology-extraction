# PowerShell Setup Script for Windows
# Automated setup with automatic error reporting

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Terminology Extraction - Automated Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Global error tracking
$script:setupErrors = @()
$script:setupLog = @()

function Log-Step {
    param($message, $color = "White")
    Write-Host $message -ForegroundColor $color
    $script:setupLog += "$(Get-Date -Format 'HH:mm:ss') | $message"
}

function Log-Error {
    param($step, $error)
    $errorInfo = @{
        Step = $step
        Error = $error
        Time = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    }
    $script:setupErrors += $errorInfo
    Log-Step "[ERROR] $step failed: $error" "Red"
}

function Generate-ErrorReport {
    $report = @"
# Automated Error Report

**Generated**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**Script**: setup-windows.ps1

## Errors Encountered

"@

    foreach ($err in $script:setupErrors) {
        $report += @"

### $($err.Step)
**Time**: $($err.Time)
**Error**:
``````
$($err.Error)
``````

"@
    }

    $report += @"

## System Information

- **OS**: $([System.Environment]::OSVersion.VersionString)
- **PowerShell**: $($PSVersionTable.PSVersion)
- **Python**: $(try { python --version 2>&1 } catch { "Not found" })
- **Node.js**: $(try { node --version 2>&1 } catch { "Not found" })
- **Git**: $(try { git --version 2>&1 } catch { "Not found" })

## Setup Log

``````
$($script:setupLog -join "`n")
``````

## Next Steps

1. Check TROUBLESHOOTING.md for common solutions
2. Review error messages above
3. Submit issue: https://github.com/developer-hhiotsystems/terminology-extraction/issues/new
4. Or email: developer.hh-iot-systems@outlook.com

## Attach This Report

Include this file when requesting help.
"@

    return $report
}

# Check if running in project directory
if (-not (Test-Path "package.json")) {
    Write-Host "[ERROR] Not in project directory!" -ForegroundColor Red
    Write-Host "Please run this script from the project root folder.`n" -ForegroundColor Red

    # Generate error report
    Log-Error "Pre-check" "Not in project directory"
    $report = Generate-ErrorReport
    $reportPath = Join-Path $PWD "setup-error-report.md"
    Set-Content -Path $reportPath -Value $report
    Write-Host "`nError report saved to: $reportPath" -ForegroundColor Yellow

    exit 1
}

# Step 1: Check prerequisites
Log-Step "[1/8] Checking prerequisites..." "Yellow"

# Check Python
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Log-Step "  [OK] Python found: $pythonVersion" "Green"
    } else {
        throw "Python command failed"
    }
} catch {
    Log-Error "Prerequisites" "Python not found. Please install Python 3.10+ from https://www.python.org/downloads/"
    $report = Generate-ErrorReport
    Set-Content -Path "setup-error-report.md" -Value $report
    Write-Host "`nError report saved: setup-error-report.md" -ForegroundColor Yellow
    Write-Host "Please install Python and try again.`n" -ForegroundColor Yellow
    exit 1
}

# Check Node
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Log-Step "  [OK] Node.js found: $nodeVersion" "Green"
    } else {
        throw "Node command failed"
    }
} catch {
    Log-Error "Prerequisites" "Node.js not found. Please install Node.js 18+ from https://nodejs.org/"
    $report = Generate-ErrorReport
    Set-Content -Path "setup-error-report.md" -Value $report
    Write-Host "`nError report saved: setup-error-report.md" -ForegroundColor Yellow
    Write-Host "Please install Node.js and try again.`n" -ForegroundColor Yellow
    exit 1
}

# Check Git
try {
    $gitVersion = git --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Log-Step "  [OK] Git found: $gitVersion" "Green"
    } else {
        throw "Git command failed"
    }
} catch {
    Log-Error "Prerequisites" "Git not found. Please install Git from https://git-scm.com/downloads"
    $report = Generate-ErrorReport
    Set-Content -Path "setup-error-report.md" -Value $report
    Write-Host "`nError report saved: setup-error-report.md" -ForegroundColor Yellow
    Write-Host "Please install Git and try again.`n" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Step 2: Create virtual environment
Log-Step "[2/8] Creating Python virtual environment..." "Yellow"

if (Test-Path "venv") {
    Log-Step "  [INFO] Virtual environment already exists, skipping..." "Gray"
} else {
    try {
        python -m venv venv
        if ($LASTEXITCODE -eq 0) {
            Log-Step "  [OK] Virtual environment created" "Green"
        } else {
            throw "venv creation returned error code $LASTEXITCODE"
        }
    } catch {
        Log-Error "Virtual Environment" $_.Exception.Message
        $report = Generate-ErrorReport
        Set-Content -Path "setup-error-report.md" -Value $report
        Write-Host "`nError report saved: setup-error-report.md" -ForegroundColor Yellow
        Write-Host "Check TROUBLESHOOTING.md for solutions.`n" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""

# Step 3: Activate virtual environment and install Python packages
Log-Step "[3/8] Installing Python packages..." "Yellow"

try {
    & .\venv\Scripts\python.exe -m pip install --upgrade pip --quiet 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Log-Step "  [OK] pip upgraded" "Green"
    } else {
        Log-Step "  [WARN] pip upgrade failed, continuing..." "Yellow"
    }

    $pipOutput = & .\venv\Scripts\pip.exe install -r requirements-core.txt 2>&1
    if ($LASTEXITCODE -eq 0) {
        Log-Step "  [OK] Python packages installed (41 packages)" "Green"
    } else {
        throw "pip install failed: $pipOutput"
    }
} catch {
    Log-Error "Python Packages" $_.Exception.Message
    $report = Generate-ErrorReport
    Set-Content -Path "setup-error-report.md" -Value $report
    Write-Host "`nError report saved: setup-error-report.md" -ForegroundColor Yellow
    Write-Host "`nPossible solutions:" -ForegroundColor Yellow
    Write-Host "  1. Behind proxy? Set: `$env:HTTP_PROXY='http://proxy:port'" -ForegroundColor Gray
    Write-Host "  2. SSL issues? Try: pip install --trusted-host pypi.org ..." -ForegroundColor Gray
    Write-Host "  3. See TROUBLESHOOTING.md for more solutions`n" -ForegroundColor Gray
    exit 1
}

Write-Host ""

# Step 4: Install Node packages
Log-Step "[4/8] Installing Node.js packages (this may take 3-5 minutes)..." "Yellow"

try {
    $npmOutput = npm install 2>&1
    if ($LASTEXITCODE -eq 0) {
        Log-Step "  [OK] Node packages installed (1,764 packages)" "Green"
    } else {
        throw "npm install failed: $npmOutput"
    }
} catch {
    Log-Error "Node Packages" $_.Exception.Message
    $report = Generate-ErrorReport
    Set-Content -Path "setup-error-report.md" -Value $report
    Write-Host "`nError report saved: setup-error-report.md" -ForegroundColor Yellow
    Write-Host "`nPossible solutions:" -ForegroundColor Yellow
    Write-Host "  1. Behind proxy? Run: npm config set proxy http://proxy:port" -ForegroundColor Gray
    Write-Host "  2. Clear cache: npm cache clean --force" -ForegroundColor Gray
    Write-Host "  3. See TROUBLESHOOTING.md for more solutions`n" -ForegroundColor Gray
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
if ($script:setupErrors.Count -eq 0) {
    Log-Step "[8/8] Setup complete!" "Green"
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

    # Save success log
    $successLog = "Setup completed successfully at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n`n"
    $successLog += $script:setupLog -join "`n"
    Set-Content -Path "setup-success.log" -Value $successLog
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Setup encountered errors!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error report generated: setup-error-report.md" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "What to do:" -ForegroundColor Yellow
    Write-Host "  1. Review setup-error-report.md" -ForegroundColor White
    Write-Host "  2. Check TROUBLESHOOTING.md for solutions" -ForegroundColor White
    Write-Host "  3. Submit issue: https://github.com/developer-hhiotsystems/terminology-extraction/issues/new" -ForegroundColor White
    Write-Host ""
}
