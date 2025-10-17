# Glossary Management System - Startup Script (Windows PowerShell)
# Starts both backend and frontend servers

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Glossary Management System Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path ".\venv\Scripts\python.exe")) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create it first: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "[OK] Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js not found! Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Check if frontend dependencies are installed
if (-Not (Test-Path ".\src\frontend\node_modules")) {
    Write-Host "[INFO] Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location ".\src\frontend"
    npm install
    Set-Location "..\..\"
    Write-Host "[OK] Frontend dependencies installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting servers..." -ForegroundColor Cyan
Write-Host ""

# Kill any existing Python processes
Write-Host "[INFO] Cleaning up existing processes..." -ForegroundColor Yellow
taskkill /F /IM python.exe 2>$null | Out-Null
Start-Sleep -Seconds 1

# Start Backend Server
Write-Host "[1/2] Starting Backend Server (FastAPI)..." -ForegroundColor Cyan
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & ".\venv\Scripts\python.exe" "src\backend\app.py"
}
Write-Host "  -> Backend PID: $($backendJob.Id)" -ForegroundColor Gray
Write-Host "  -> API: http://localhost:8000" -ForegroundColor Green
Write-Host "  -> Docs: http://localhost:8000/docs" -ForegroundColor Green
Start-Sleep -Seconds 3

# Start Frontend Server
Write-Host ""
Write-Host "[2/2] Starting Frontend Server (React + Vite)..." -ForegroundColor Cyan
Set-Location ".\src\frontend"
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "$using:PWD\src\frontend"
    npm run dev
}
Write-Host "  -> Frontend PID: $($frontendJob.Id)" -ForegroundColor Gray
Write-Host "  -> UI: http://localhost:3000" -ForegroundColor Green
Set-Location "..\..\"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Servers Started Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "API Docs:     http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "Frontend UI:  http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop all servers" -ForegroundColor Cyan
Write-Host ""

# Monitor jobs
try {
    while ($true) {
        Start-Sleep -Seconds 1

        # Check if jobs are still running
        if ($backendJob.State -ne 'Running') {
            Write-Host "[ERROR] Backend server stopped unexpectedly!" -ForegroundColor Red
            break
        }
        if ($frontendJob.State -ne 'Running') {
            Write-Host "[ERROR] Frontend server stopped unexpectedly!" -ForegroundColor Red
            break
        }
    }
} finally {
    Write-Host ""
    Write-Host "Shutting down servers..." -ForegroundColor Yellow
    Stop-Job -Job $backendJob, $frontendJob
    Remove-Job -Job $backendJob, $frontendJob
    taskkill /F /IM python.exe 2>$null | Out-Null
    taskkill /F /IM node.exe 2>$null | Out-Null
    Write-Host "All servers stopped." -ForegroundColor Green
}
