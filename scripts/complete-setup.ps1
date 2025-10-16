# Master setup script to guide through all remaining setup tasks
# Run from project root

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Complete Setup Wizard" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Set-Location "C:\Users\devel\Coding Projects\Glossary APP"

Write-Host "This wizard will guide you through all remaining setup tasks:`n" -ForegroundColor White
Write-Host "  1. C++ Build Tools (for spaCy, lxml)" -ForegroundColor Gray
Write-Host "  2. Docker Desktop + Neo4j" -ForegroundColor Gray
Write-Host "  3. DeepL API Configuration" -ForegroundColor Gray
Write-Host "  4. IATE Dataset Download" -ForegroundColor Gray
Write-Host "  5. Final Verification`n" -ForegroundColor Gray

$continue = Read-Host "Continue with setup? (y/n)"
if ($continue -ne 'y') {
    Write-Host "`nSetup cancelled.`n" -ForegroundColor Yellow
    exit 0
}

# Task 1: C++ Build Tools
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Task 1/4: C++ Build Tools" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$doCpp = Read-Host "Install C++ Build Tools? (y/n/skip)"
if ($doCpp -eq 'y') {
    & ".\scripts\install-cpp-tools.ps1"
    Write-Host "`nC++ Build Tools setup completed." -ForegroundColor Green
    Write-Host "Press Enter to continue to next task..." -ForegroundColor Yellow
    Read-Host
} elseif ($doCpp -eq 'skip') {
    Write-Host "[SKIP] C++ Build Tools - you can install later`n" -ForegroundColor Yellow
}

# Task 2: Docker + Neo4j
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Task 2/4: Docker Desktop & Neo4j" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$doDocker = Read-Host "Setup Docker Desktop and Neo4j? (y/n/skip)"
if ($doDocker -eq 'y') {
    & ".\scripts\setup-docker.ps1"
    Write-Host "`nDocker & Neo4j setup completed." -ForegroundColor Green
    Write-Host "Press Enter to continue to next task..." -ForegroundColor Yellow
    Read-Host
} elseif ($doDocker -eq 'skip') {
    Write-Host "[SKIP] Docker & Neo4j - you can install later`n" -ForegroundColor Yellow
}

# Task 3: DeepL API
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Task 3/4: DeepL API Configuration" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$doDeepL = Read-Host "Configure DeepL API? (y/n/skip)"
if ($doDeepL -eq 'y') {
    & .\venv\Scripts\python ".\scripts\configure-deepl.py"
    Write-Host "`nDeepL API setup completed." -ForegroundColor Green
    Write-Host "Press Enter to continue to next task..." -ForegroundColor Yellow
    Read-Host
} elseif ($doDeepL -eq 'skip') {
    Write-Host "[SKIP] DeepL API - you can configure later`n" -ForegroundColor Yellow
}

# Task 4: IATE Dataset
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Task 4/4: IATE Dataset Download" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$doIATE = Read-Host "Download IATE Dataset? (y/n/skip)"
if ($doIATE -eq 'y') {
    & .\venv\Scripts\python ".\scripts\download-iate.py"
    Write-Host "`nIATE Dataset setup completed." -ForegroundColor Green
    Write-Host "Press Enter to continue to verification..." -ForegroundColor Yellow
    Read-Host
} elseif ($doIATE -eq 'skip') {
    Write-Host "[SKIP] IATE Dataset - you can download later`n" -ForegroundColor Yellow
}

# Final Verification
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Final Verification" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Running automated setup verification...`n" -ForegroundColor White
& .\venv\Scripts\python setup-check.py

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Setup Wizard Complete!" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Review: docs\SETUP-COMPLETE.md" -ForegroundColor White
Write-Host "  2. Test backend: python src\backend\app.py" -ForegroundColor White
Write-Host "  3. Test frontend: npm start" -ForegroundColor White
Write-Host "  4. Begin Phase 1 development`n" -ForegroundColor White

$openDocs = Read-Host "Open SETUP-COMPLETE.md? (y/n)"
if ($openDocs -eq 'y') {
    Start-Process "docs\SETUP-COMPLETE.md"
}

Write-Host "`nSetup complete! Happy coding!`n" -ForegroundColor Green
