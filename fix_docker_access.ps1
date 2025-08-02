# =============================================================================
# Fix Docker Desktop Access Issues
# =============================================================================

Write-Host "🔧 Fixing Docker Desktop Access Issues..." -ForegroundColor Yellow
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if ($isAdmin) {
    Write-Host "✅ Running as Administrator" -ForegroundColor Green
} else {
    Write-Host "⚠️  Not running as Administrator" -ForegroundColor Yellow
    Write-Host "   This may cause Docker access issues" -ForegroundColor Yellow
}

Write-Host ""

# Try different methods to access Docker
Write-Host "Testing Docker access methods..." -ForegroundColor Cyan

# Method 1: Direct path with quotes
Write-Host "Method 1: Direct path..." -ForegroundColor White
try {
    $dockerVersion = & "C:\Program Files\Docker\Docker\resources\bin\docker.exe" --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker accessible via direct path" -ForegroundColor Green
        $dockerPath = "C:\Program Files\Docker\Docker\resources\bin\docker.exe"
    } else {
        Write-Host "❌ Direct path failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Direct path failed with error" -ForegroundColor Red
}

# Method 2: Using Start-Process
Write-Host "Method 2: Start-Process..." -ForegroundColor White
try {
    $result = Start-Process -FilePath "C:\Program Files\Docker\Docker\resources\bin\docker.exe" -ArgumentList "--version" -Wait -PassThru -NoNewWindow -RedirectStandardOutput "temp_docker_version.txt" -RedirectStandardError "temp_docker_error.txt"
    if ($result.ExitCode -eq 0) {
        Write-Host "✅ Docker accessible via Start-Process" -ForegroundColor Green
        $dockerMethod = "Start-Process"
    } else {
        Write-Host "❌ Start-Process failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Start-Process failed with error" -ForegroundColor Red
}

# Method 3: Check if Docker Desktop service is running
Write-Host "Method 3: Checking Docker Desktop service..." -ForegroundColor White
try {
    $dockerService = Get-Service -Name "*Docker*" -ErrorAction SilentlyContinue
    if ($dockerService) {
        Write-Host "✅ Docker services found:" -ForegroundColor Green
        $dockerService | ForEach-Object { Write-Host "   - $($_.Name): $($_.Status)" -ForegroundColor White }
    } else {
        Write-Host "❌ No Docker services found" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Could not check Docker services" -ForegroundColor Red
}

Write-Host ""

# Provide solutions
Write-Host "Solutions to try:" -ForegroundColor Yellow
Write-Host "================" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Run PowerShell as Administrator:" -ForegroundColor Cyan
Write-Host "   - Right-click PowerShell in Start Menu" -ForegroundColor White
Write-Host "   - Select 'Run as administrator'" -ForegroundColor White
Write-Host "   - Navigate to project directory" -ForegroundColor White
Write-Host "   - Run: .\setup_critical_steps.ps1" -ForegroundColor Green
Write-Host ""
Write-Host "2. Restart Docker Desktop:" -ForegroundColor Cyan
Write-Host "   - Right-click Docker Desktop icon in system tray" -ForegroundColor White
Write-Host "   - Select 'Restart'" -ForegroundColor White
Write-Host "   - Wait for it to fully restart" -ForegroundColor White
Write-Host ""
Write-Host "3. Use Command Prompt instead:" -ForegroundColor Cyan
Write-Host "   - Open Command Prompt as Administrator" -ForegroundColor White
Write-Host "   - Navigate to project directory" -ForegroundColor White
Write-Host "   - Run: docker compose --env-file .env.docker up --build -d" -ForegroundColor Green
Write-Host ""
Write-Host "4. Use the Windows batch file:" -ForegroundColor Cyan
Write-Host "   - Open Command Prompt" -ForegroundColor White
Write-Host "   - Navigate to project directory" -ForegroundColor White
Write-Host "   - Run: .\docker-windows.bat up" -ForegroundColor Green
Write-Host ""

# Alternative approach using batch file
Write-Host "Alternative: Using Windows Batch File" -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host "If PowerShell continues to have issues, use the batch file:" -ForegroundColor White
Write-Host ""
Write-Host "1. Open Command Prompt (not PowerShell)" -ForegroundColor Cyan
Write-Host "2. Navigate to: C:\Users\horiz\OneDrive\ドキュメント\sarvanom" -ForegroundColor White
Write-Host "3. Run: .\docker-windows.bat setup" -ForegroundColor Green
Write-Host "4. Then run: .\docker-windows.bat up" -ForegroundColor Green
Write-Host ""

# Create a simple batch file alternative
Write-Host "Creating alternative batch file..." -ForegroundColor Yellow
$batchContent = @"
@echo off
echo Starting SarvanOM Docker services...
echo.
echo Checking Docker...
docker --version
if %errorlevel% neq 0 (
    echo ERROR: Docker not accessible
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo.
echo Starting services...
docker compose --env-file .env.docker up --build -d
if %errorlevel% equ 0 (
    echo.
    echo Services started successfully!
    echo.
    echo Access your services at:
    echo   Frontend: http://localhost:3000
    echo   Backend:  http://localhost:8000
    echo   Ollama:   http://localhost:11434
    echo.
    echo Run '.\docker-windows.bat health' to check service health
) else (
    echo Failed to start services
    pause
)
"@

$batchContent | Out-File -FilePath "start_services.bat" -Encoding ASCII
Write-Host "✅ Created start_services.bat as alternative" -ForegroundColor Green

Write-Host ""
Write-Host "Quick Test Commands:" -ForegroundColor Yellow
Write-Host "===================" -ForegroundColor Yellow
Write-Host "Try these commands to test Docker access:" -ForegroundColor White
Write-Host ""
Write-Host "1. Test Docker version:" -ForegroundColor Cyan
Write-Host "   docker --version" -ForegroundColor Green
Write-Host ""
Write-Host "2. Test Docker info:" -ForegroundColor Cyan
Write-Host "   docker info" -ForegroundColor Green
Write-Host ""
Write-Host "3. Test Docker Compose:" -ForegroundColor Cyan
Write-Host "   docker compose version" -ForegroundColor Green
Write-Host ""

Write-Host "If none of these work, try restarting Docker Desktop completely." -ForegroundColor Red 