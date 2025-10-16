# PowerShell script to guide C++ Build Tools installation
# Run as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "C++ Build Tools Installation Helper" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[WARN] Not running as Administrator" -ForegroundColor Yellow
    Write-Host "Some checks may be limited`n" -ForegroundColor Yellow
}

# Check if Visual Studio Build Tools are already installed
Write-Host "Checking for existing C++ Build Tools..." -ForegroundColor White

$vsWherePath = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (Test-Path $vsWherePath) {
    $installations = & $vsWherePath -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -format json | ConvertFrom-Json

    if ($installations.Count -gt 0) {
        Write-Host "[OK] Visual Studio C++ Build Tools found!" -ForegroundColor Green
        foreach ($install in $installations) {
            Write-Host "  Version: $($install.installationVersion)" -ForegroundColor Gray
            Write-Host "  Path: $($install.installationPath)" -ForegroundColor Gray
        }
        Write-Host "`nYou can skip the installation and proceed to install Python packages.`n" -ForegroundColor Green

        # Ask if user wants to install Python packages now
        $install = Read-Host "Install Python packages now? (y/n)"
        if ($install -eq 'y') {
            Write-Host "`nInstalling Python packages with C++ dependencies..." -ForegroundColor Cyan
            Set-Location "C:\Users\devel\Coding Projects\Glossary APP"
            & .\venv\Scripts\pip install -r requirements.txt

            if ($LASTEXITCODE -eq 0) {
                Write-Host "`n[OK] All Python packages installed successfully!" -ForegroundColor Green
                Write-Host "`nDownloading spaCy language model..." -ForegroundColor Cyan
                & .\venv\Scripts\python -m spacy download en_core_web_sm

                if ($LASTEXITCODE -eq 0) {
                    Write-Host "`n[OK] spaCy language model installed!" -ForegroundColor Green
                }
            }
        }
        exit 0
    }
}

Write-Host "[INFO] C++ Build Tools not found. Installation required.`n" -ForegroundColor Yellow

# Provide installation options
Write-Host "Installation Options:" -ForegroundColor Cyan
Write-Host "1. Visual Studio Build Tools (Recommended - ~6 GB)" -ForegroundColor White
Write-Host "   - Minimal installation" -ForegroundColor Gray
Write-Host "   - C++ compiler only" -ForegroundColor Gray
Write-Host "   - Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Visual Studio Community (Full IDE - ~10 GB)" -ForegroundColor White
Write-Host "   - Complete development environment" -ForegroundColor Gray
Write-Host "   - C++ compiler + IDE" -ForegroundColor Gray
Write-Host "   - Download: https://visualstudio.microsoft.com/vs/community/" -ForegroundColor Gray
Write-Host ""

$choice = Read-Host "Which option would you like? (1/2/s to skip)"

switch ($choice) {
    '1' {
        Write-Host "`nOpening Build Tools download page..." -ForegroundColor Cyan
        Start-Process "https://visualstudio.microsoft.com/visual-cpp-build-tools/"
        Write-Host "`nInstallation Steps:" -ForegroundColor Yellow
        Write-Host "1. Download and run the installer" -ForegroundColor White
        Write-Host "2. Select 'Desktop development with C++'" -ForegroundColor White
        Write-Host "3. Click Install (requires ~6 GB)" -ForegroundColor White
        Write-Host "4. Restart your computer after installation" -ForegroundColor White
        Write-Host "5. Run this script again to install Python packages`n" -ForegroundColor White
    }
    '2' {
        Write-Host "`nOpening Visual Studio Community download page..." -ForegroundColor Cyan
        Start-Process "https://visualstudio.microsoft.com/vs/community/"
        Write-Host "`nInstallation Steps:" -ForegroundColor Yellow
        Write-Host "1. Download and run the installer" -ForegroundColor White
        Write-Host "2. Select 'Desktop development with C++' workload" -ForegroundColor White
        Write-Host "3. Click Install (requires ~10 GB)" -ForegroundColor White
        Write-Host "4. Restart your computer after installation" -ForegroundColor White
        Write-Host "5. Run this script again to install Python packages`n" -ForegroundColor White
    }
    's' {
        Write-Host "`nSkipping installation. You can run this script later.`n" -ForegroundColor Yellow
    }
    default {
        Write-Host "`nInvalid choice. Exiting.`n" -ForegroundColor Red
    }
}

Write-Host "After installation completes, run:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\pip install -r requirements.txt" -ForegroundColor White
Write-Host "  .\venv\Scripts\python -m spacy download en_core_web_sm`n" -ForegroundColor White
