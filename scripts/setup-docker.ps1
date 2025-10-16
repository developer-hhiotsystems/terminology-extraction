# PowerShell script to guide Docker Desktop installation and Neo4j setup

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Docker Desktop & Neo4j Setup Helper" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if Docker is installed
Write-Host "Checking for Docker Desktop..." -ForegroundColor White

try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Docker Desktop is installed: $dockerVersion" -ForegroundColor Green

        # Check if Docker is running
        Write-Host "`nChecking if Docker is running..." -ForegroundColor White
        $dockerInfo = docker info 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Docker is running" -ForegroundColor Green

            # Check if Neo4j container exists
            Write-Host "`nChecking for Neo4j container..." -ForegroundColor White
            Set-Location "C:\Users\devel\Coding Projects\Glossary APP"

            $neo4jContainer = docker ps -a --filter "name=glossary-neo4j" --format "{{.Names}}" 2>$null

            if ($neo4jContainer) {
                Write-Host "[INFO] Neo4j container found: $neo4jContainer" -ForegroundColor Yellow

                $containerStatus = docker ps --filter "name=glossary-neo4j" --format "{{.Status}}" 2>$null
                if ($containerStatus) {
                    Write-Host "[OK] Neo4j is running: $containerStatus" -ForegroundColor Green
                } else {
                    Write-Host "[WARN] Neo4j container exists but is not running" -ForegroundColor Yellow
                    $start = Read-Host "Start Neo4j container? (y/n)"
                    if ($start -eq 'y') {
                        Write-Host "`nStarting Neo4j container..." -ForegroundColor Cyan
                        docker-compose -f docker-compose.dev.yml up -d
                        Start-Sleep -Seconds 10
                        Write-Host "[OK] Neo4j started" -ForegroundColor Green
                    }
                }
            } else {
                Write-Host "[INFO] Neo4j container not found. Creating..." -ForegroundColor Yellow
                $create = Read-Host "Create and start Neo4j container? (y/n)"
                if ($create -eq 'y') {
                    Write-Host "`nCreating Neo4j container..." -ForegroundColor Cyan
                    docker-compose -f docker-compose.dev.yml up -d

                    if ($LASTEXITCODE -eq 0) {
                        Write-Host "[OK] Neo4j container created and started" -ForegroundColor Green
                        Write-Host "`nWaiting for Neo4j to be ready..." -ForegroundColor Cyan
                        Start-Sleep -Seconds 15
                    }
                }
            }

            # Test Neo4j connection
            Write-Host "`nTesting Neo4j connection..." -ForegroundColor White
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:7474" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
                Write-Host "[OK] Neo4j is accessible at http://localhost:7474" -ForegroundColor Green
                Write-Host "`nNeo4j Browser Login:" -ForegroundColor Cyan
                Write-Host "  URL: http://localhost:7474" -ForegroundColor White
                Write-Host "  Username: neo4j" -ForegroundColor White
                Write-Host "  Password: devpassword`n" -ForegroundColor White

                $openBrowser = Read-Host "Open Neo4j Browser? (y/n)"
                if ($openBrowser -eq 'y') {
                    Start-Process "http://localhost:7474"
                }
            } catch {
                Write-Host "[WARN] Cannot connect to Neo4j at http://localhost:7474" -ForegroundColor Yellow
                Write-Host "Container may still be starting up. Wait 30 seconds and try again.`n" -ForegroundColor Yellow
            }

        } else {
            Write-Host "[WARN] Docker Desktop is installed but not running" -ForegroundColor Yellow
            Write-Host "`nPlease start Docker Desktop from:" -ForegroundColor White
            Write-Host "  - Start Menu > Docker Desktop" -ForegroundColor Gray
            Write-Host "  - Wait for the whale icon in system tray" -ForegroundColor Gray
            Write-Host "  - Run this script again`n" -ForegroundColor Gray
        }

        exit 0
    }
} catch {
    # Docker not found
}

Write-Host "[INFO] Docker Desktop is not installed`n" -ForegroundColor Yellow

# Check Windows version
$osVersion = [System.Environment]::OSVersion.Version
$isWindows10Plus = $osVersion.Major -ge 10

if (-not $isWindows10Plus) {
    Write-Host "[ERROR] Docker Desktop requires Windows 10 or later" -ForegroundColor Red
    Write-Host "Your version: Windows $($osVersion.Major).$($osVersion.Minor)`n" -ForegroundColor Red
    exit 1
}

Write-Host "Installation Options:" -ForegroundColor Cyan
Write-Host "1. Docker Desktop (Recommended)" -ForegroundColor White
Write-Host "   - Requires Windows 10/11 Pro, Enterprise, or Education" -ForegroundColor Gray
Write-Host "   - Or Windows 10/11 Home with WSL 2" -ForegroundColor Gray
Write-Host "   - Download: https://www.docker.com/products/docker-desktop/" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Neo4j Desktop (No Docker required)" -ForegroundColor White
Write-Host "   - Standalone application" -ForegroundColor Gray
Write-Host "   - Easier for beginners" -ForegroundColor Gray
Write-Host "   - Download: https://neo4j.com/download/" -ForegroundColor Gray
Write-Host ""

$choice = Read-Host "Which option would you like? (1/2/s to skip)"

switch ($choice) {
    '1' {
        Write-Host "`nOpening Docker Desktop download page..." -ForegroundColor Cyan
        Start-Process "https://www.docker.com/products/docker-desktop/"
        Write-Host "`nInstallation Steps:" -ForegroundColor Yellow
        Write-Host "1. Download Docker Desktop for Windows" -ForegroundColor White
        Write-Host "2. Run the installer" -ForegroundColor White
        Write-Host "3. Enable WSL 2 backend if prompted" -ForegroundColor White
        Write-Host "4. Restart your computer" -ForegroundColor White
        Write-Host "5. Start Docker Desktop" -ForegroundColor White
        Write-Host "6. Run this script again to setup Neo4j`n" -ForegroundColor White
    }
    '2' {
        Write-Host "`nOpening Neo4j Desktop download page..." -ForegroundColor Cyan
        Start-Process "https://neo4j.com/download/"
        Write-Host "`nInstallation Steps:" -ForegroundColor Yellow
        Write-Host "1. Download Neo4j Desktop" -ForegroundColor White
        Write-Host "2. Install and launch Neo4j Desktop" -ForegroundColor White
        Write-Host "3. Create a new project" -ForegroundColor White
        Write-Host "4. Create a new database (set password to 'devpassword')" -ForegroundColor White
        Write-Host "5. Start the database" -ForegroundColor White
        Write-Host "6. Update .env file with connection details`n" -ForegroundColor White

        Write-Host "Neo4j Desktop Configuration:" -ForegroundColor Cyan
        Write-Host "  In .env file, set:" -ForegroundColor White
        Write-Host "  NEO4J_URI=bolt://localhost:7687" -ForegroundColor Gray
        Write-Host "  NEO4J_USER=neo4j" -ForegroundColor Gray
        Write-Host "  NEO4J_PASSWORD=devpassword`n" -ForegroundColor Gray
    }
    's' {
        Write-Host "`nSkipping Docker installation.`n" -ForegroundColor Yellow
    }
    default {
        Write-Host "`nInvalid choice. Exiting.`n" -ForegroundColor Red
    }
}
