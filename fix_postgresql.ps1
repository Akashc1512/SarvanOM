# Quick PostgreSQL Fix Script for SarvanOM
# Run this script as Administrator

Write-Host "🔧 PostgreSQL Quick Fix for SarvanOM" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "❌ This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "💡 Right-click on PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Running as Administrator" -ForegroundColor Green

# Step 1: Start PostgreSQL Service
Write-Host "`n🔧 Step 1: Starting PostgreSQL service..." -ForegroundColor Yellow
try {
    Start-Service -Name "postgresql-x64-17" -ErrorAction Stop
    Write-Host "✅ PostgreSQL service started successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to start PostgreSQL service: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 You may need to reinstall PostgreSQL" -ForegroundColor Yellow
}

# Step 2: Add PostgreSQL to PATH
Write-Host "`n🔧 Step 2: Adding PostgreSQL to PATH..." -ForegroundColor Yellow
$postgresBinPath = "C:\Program Files\PostgreSQL\17\bin"
if (Test-Path $postgresBinPath) {
    $env:PATH += ";$postgresBinPath"
    Write-Host "✅ Added PostgreSQL bin to PATH" -ForegroundColor Green
} else {
    Write-Host "❌ PostgreSQL bin directory not found at: $postgresBinPath" -ForegroundColor Red
    Write-Host "💡 Please verify PostgreSQL installation" -ForegroundColor Yellow
}

# Step 3: Test psql command
Write-Host "`n🔧 Step 3: Testing psql command..." -ForegroundColor Yellow
$psqlPath = Get-Command psql -ErrorAction SilentlyContinue
if ($psqlPath) {
    Write-Host "✅ psql command found at: $($psqlPath.Source)" -ForegroundColor Green
    $version = & psql --version 2>&1
    Write-Host "📊 Version: $version" -ForegroundColor Cyan
} else {
    Write-Host "❌ psql command not found" -ForegroundColor Red
    Write-Host "💡 Please add PostgreSQL bin to PATH permanently" -ForegroundColor Yellow
}

# Step 4: Test connection
Write-Host "`n🔧 Step 4: Testing PostgreSQL connection..." -ForegroundColor Yellow
try {
    $testResult = & psql -h localhost -p 5432 -U postgres -d postgres -c "SELECT version();" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL connection successful!" -ForegroundColor Green
        Write-Host "📊 Server info: $testResult" -ForegroundColor Cyan
    } else {
        Write-Host "❌ PostgreSQL connection failed" -ForegroundColor Red
        Write-Host "💡 Error: $testResult" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Cannot test connection - psql not available" -ForegroundColor Red
}

# Step 5: Provide next steps
Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
Write-Host "==============" -ForegroundColor Yellow
Write-Host "1. If connection successful, create database and user:" -ForegroundColor White
Write-Host "   psql -U postgres -h localhost" -ForegroundColor Cyan
Write-Host "   CREATE DATABASE sarvanom_db;" -ForegroundColor Cyan
Write-Host "   CREATE USER sarvanom_user WITH PASSWORD 'your_password';" -ForegroundColor Cyan
Write-Host "   GRANT ALL PRIVILEGES ON DATABASE sarvanom_db TO sarvanom_user;" -ForegroundColor Cyan
Write-Host "   \q" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Update your .env file:" -ForegroundColor White
Write-Host "   DATABASE_URL=postgresql://sarvanom_user:your_password@localhost:5432/sarvanom_db" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Test the new connection:" -ForegroundColor White
Write-Host "   psql -h localhost -p 5432 -U sarvanom_user -d sarvanom_db" -ForegroundColor Cyan

Write-Host "`n✅ Quick fix completed!" -ForegroundColor Green
Write-Host "🎯 Follow the next steps above to complete setup" -ForegroundColor Green 