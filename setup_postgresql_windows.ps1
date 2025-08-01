# PostgreSQL Setup Script for Windows
# This script helps set up PostgreSQL for SarvanOM

Write-Host "🐘 PostgreSQL Setup for SarvanOM" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Check if PostgreSQL is already installed
$postgresService = Get-Service -Name "*postgres*" -ErrorAction SilentlyContinue

if ($postgresService) {
    Write-Host "✅ PostgreSQL service found: $($postgresService.Name)" -ForegroundColor Green
    
    # Try to start the service
    try {
        Start-Service -Name $postgresService.Name -ErrorAction Stop
        Write-Host "✅ PostgreSQL service started successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to start PostgreSQL service: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "💡 You may need to run this script as Administrator" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ PostgreSQL service not found" -ForegroundColor Red
    Write-Host "📥 Please install PostgreSQL first:" -ForegroundColor Yellow
    Write-Host "   1. Download from: https://www.postgresql.org/download/windows/" -ForegroundColor Cyan
    Write-Host "   2. Run the installer as Administrator" -ForegroundColor Cyan
    Write-Host "   3. Use default port 5432" -ForegroundColor Cyan
    Write-Host "   4. Set password for postgres user" -ForegroundColor Cyan
    Write-Host "   5. Run this script again" -ForegroundColor Cyan
}

# Check if psql is available
$psqlPath = Get-Command psql -ErrorAction SilentlyContinue
if ($psqlPath) {
    Write-Host "✅ psql command found at: $($psqlPath.Source)" -ForegroundColor Green
} else {
    Write-Host "❌ psql command not found in PATH" -ForegroundColor Red
    Write-Host "💡 Add PostgreSQL bin directory to PATH:" -ForegroundColor Yellow
    Write-Host "   C:\Program Files\PostgreSQL\17\bin" -ForegroundColor Cyan
}

# Test connection
Write-Host "`n🔍 Testing PostgreSQL connection..." -ForegroundColor Yellow
try {
    $testConnection = & psql -h localhost -p 5432 -U postgres -d postgres -c "SELECT version();" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL connection successful!" -ForegroundColor Green
        Write-Host "📊 Server info: $testConnection" -ForegroundColor Cyan
    } else {
        Write-Host "❌ PostgreSQL connection failed" -ForegroundColor Red
        Write-Host "💡 Error: $testConnection" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Cannot test connection - psql not available" -ForegroundColor Red
}

# Setup instructions
Write-Host "`n📋 Manual Setup Instructions:" -ForegroundColor Yellow
Write-Host "=============================" -ForegroundColor Yellow
Write-Host "1. Install PostgreSQL:" -ForegroundColor White
Write-Host "   - Download from: https://www.postgresql.org/download/windows/" -ForegroundColor Cyan
Write-Host "   - Run installer as Administrator" -ForegroundColor Cyan
Write-Host "   - Use default settings (port 5432)" -ForegroundColor Cyan
Write-Host "   - Set password for postgres user" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Create database and user:" -ForegroundColor White
Write-Host "   - Open Command Prompt as Administrator" -ForegroundColor Cyan
Write-Host "   - Run: createdb sarvanom_db" -ForegroundColor Cyan
Write-Host "   - Run: createuser -P sarvanom_user" -ForegroundColor Cyan
Write-Host "   - Enter password when prompted" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Grant privileges:" -ForegroundColor White
Write-Host "   - Run: psql -d sarvanom_db -c 'GRANT ALL PRIVILEGES ON DATABASE sarvanom_db TO sarvanom_user;'" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Update your .env file:" -ForegroundColor White
Write-Host "   DATABASE_URL=postgresql://sarvanom_user:your_password@localhost:5432/sarvanom_db" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Test connection:" -ForegroundColor White
Write-Host "   psql -h localhost -p 5432 -U sarvanom_user -d sarvanom_db" -ForegroundColor Cyan

Write-Host "`n🎯 Next Steps:" -ForegroundColor Green
Write-Host "===============" -ForegroundColor Green
Write-Host "1. Install PostgreSQL if not already installed" -ForegroundColor White
Write-Host "2. Create the database and user" -ForegroundColor White
Write-Host "3. Update your .env file with the database URL" -ForegroundColor White
Write-Host "4. Test the connection" -ForegroundColor White
Write-Host "5. Run your SarvanOM application" -ForegroundColor White

Write-Host "`n✅ Setup script completed!" -ForegroundColor Green 