# =============================================================================
# Docker Desktop Status Check
# =============================================================================

Write-Host "🔍 Checking Docker Desktop Status..." -ForegroundColor Yellow
Write-Host ""

# Check if Docker Desktop is running
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker is available" -ForegroundColor Green
        Write-Host "   Version: $dockerVersion" -ForegroundColor White
    } else {
        Write-Host "❌ Docker is not available" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Docker command failed" -ForegroundColor Red
}

Write-Host ""

# Check Docker info
try {
    $dockerInfo = docker info 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker Desktop is running" -ForegroundColor Green
        Write-Host ""
        Write-Host "Docker Information:" -ForegroundColor Cyan
        Write-Host "==================" -ForegroundColor Cyan
        $dockerInfo | Select-Object -First 10 | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
    } else {
        Write-Host "❌ Docker Desktop is not running" -ForegroundColor Red
        Write-Host ""
        Write-Host "Troubleshooting Steps:" -ForegroundColor Yellow
        Write-Host "=====================" -ForegroundColor Yellow
        Write-Host "1. Open Docker Desktop from Start Menu" -ForegroundColor White
        Write-Host "2. Wait for the whale icon to appear in system tray" -ForegroundColor White
        Write-Host "3. Make sure it shows 'Docker Desktop is running'" -ForegroundColor White
        Write-Host "4. If it's already running, try restarting Docker Desktop" -ForegroundColor White
        Write-Host "5. Check Windows Services for 'Docker Desktop Service'" -ForegroundColor White
        Write-Host ""
        Write-Host "Alternative: Run PowerShell as Administrator" -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ Could not get Docker info" -ForegroundColor Red
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "===========" -ForegroundColor Cyan
Write-Host "If Docker is running, you can now run:" -ForegroundColor White
Write-Host "  .\setup_critical_steps.ps1" -ForegroundColor Green
Write-Host ""
Write-Host "Or use the batch file:" -ForegroundColor White
Write-Host "  .\docker-windows.bat up" -ForegroundColor Green 