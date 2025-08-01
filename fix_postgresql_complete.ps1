# Complete PostgreSQL Fix Script for SarvanOM
# Run this script as Administrator

Write-Host "🔧 Complete PostgreSQL Fix for SarvanOM" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "❌ This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "💡 Right-click on PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Running as Administrator" -ForegroundColor Green

# Step 1: Check PostgreSQL installation
Write-Host "`n🔧 Step 1: Checking PostgreSQL installation..." -ForegroundColor Yellow
$postgresBinPath = "C:\Program Files\PostgreSQL\17\bin"
$postgresDataPath = "C:\Program Files\PostgreSQL\17\data"

if (Test-Path $postgresBinPath) {
    Write-Host "✅ PostgreSQL bin directory found" -ForegroundColor Green
} else {
    Write-Host "❌ PostgreSQL bin directory not found" -ForegroundColor Red
    Write-Host "💡 Please reinstall PostgreSQL" -ForegroundColor Yellow
    exit 1
}

# Step 2: Add PostgreSQL to PATH
Write-Host "`n🔧 Step 2: Adding PostgreSQL to PATH..." -ForegroundColor Yellow
$env:PATH += ";$postgresBinPath"
Write-Host "✅ Added PostgreSQL bin to PATH" -ForegroundColor Green

# Step 3: Check if data directory exists and is initialized
Write-Host "`n🔧 Step 3: Checking PostgreSQL data directory..." -ForegroundColor Yellow
if (Test-Path $postgresDataPath) {
    Write-Host "✅ PostgreSQL data directory found" -ForegroundColor Green
    
    # Check if data directory is initialized
    $pgHbaFile = Join-Path $postgresDataPath "pg_hba.conf"
    if (Test-Path $pgHbaFile) {
        Write-Host "✅ PostgreSQL data directory is initialized" -ForegroundColor Green
    } else {
        Write-Host "❌ PostgreSQL data directory is not initialized" -ForegroundColor Red
        Write-Host "🔧 Initializing PostgreSQL data directory..." -ForegroundColor Yellow
        
        try {
            & "$postgresBinPath\initdb.exe" -D $postgresDataPath -U postgres --pwprompt
            Write-Host "✅ PostgreSQL data directory initialized successfully" -ForegroundColor Green
        } catch {
            Write-Host "❌ Failed to initialize PostgreSQL data directory" -ForegroundColor Red
            Write-Host "💡 Error: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "❌ PostgreSQL data directory not found" -ForegroundColor Red
    Write-Host "🔧 Creating and initializing PostgreSQL data directory..." -ForegroundColor Yellow
    
    try {
        New-Item -ItemType Directory -Path $postgresDataPath -Force
        & "$postgresBinPath\initdb.exe" -D $postgresDataPath -U postgres --pwprompt
        Write-Host "✅ PostgreSQL data directory created and initialized" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to create/initialize PostgreSQL data directory" -ForegroundColor Red
        Write-Host "💡 Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Step 4: Configure PostgreSQL for local connections
Write-Host "`n🔧 Step 4: Configuring PostgreSQL for local connections..." -ForegroundColor Yellow
$pgHbaFile = Join-Path $postgresDataPath "pg_hba.conf"
$postgresqlConfFile = Join-Path $postgresDataPath "postgresql.conf"

if (Test-Path $pgHbaFile) {
    # Backup original file
    $backupFile = "$pgHbaFile.backup"
    if (-not (Test-Path $backupFile)) {
        Copy-Item $pgHbaFile $backupFile
        Write-Host "✅ Created backup of pg_hba.conf" -ForegroundColor Green
    }
    
    # Add local connection rules
    $pgHbaContent = @"
# PostgreSQL Client Authentication Configuration File
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust
host    all             all             127.0.0.1/32            trust
host    all             all             ::1/128                 trust
"@
    
    try {
        Set-Content -Path $pgHbaFile -Value $pgHbaContent -Force
        Write-Host "✅ Updated pg_hba.conf for local connections" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to update pg_hba.conf" -ForegroundColor Red
    }
}

# Step 5: Start PostgreSQL service
Write-Host "`n🔧 Step 5: Starting PostgreSQL service..." -ForegroundColor Yellow
try {
    Start-Service -Name "postgresql-x64-17" -ErrorAction Stop
    Write-Host "✅ PostgreSQL service started successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to start PostgreSQL service: $($_.Exception.Message)" -ForegroundColor Red
    
    # Try manual start
    Write-Host "🔧 Trying manual PostgreSQL start..." -ForegroundColor Yellow
    try {
        & "$postgresBinPath\pg_ctl.exe" start -D $postgresDataPath -s
        Write-Host "✅ PostgreSQL started manually!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Manual start also failed" -ForegroundColor Red
        Write-Host "💡 You may need to reinstall PostgreSQL" -ForegroundColor Yellow
    }
}

# Step 6: Test connection
Write-Host "`n🔧 Step 6: Testing PostgreSQL connection..." -ForegroundColor Yellow
Start-Sleep -Seconds 3  # Give service time to start

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

# Step 7: Create database and user
Write-Host "`n🔧 Step 7: Creating database and user..." -ForegroundColor Yellow
try {
    # Create database
    $createDbResult = & psql -h localhost -p 5432 -U postgres -d postgres -c "CREATE DATABASE sarvanom_db;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database 'sarvanom_db' created successfully!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Database creation result: $createDbResult" -ForegroundColor Yellow
    }
    
    # Create user
    $createUserResult = & psql -h localhost -p 5432 -U postgres -d postgres -c "CREATE USER sarvanom_user WITH PASSWORD 'sarvanom_password';" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ User 'sarvanom_user' created successfully!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ User creation result: $createUserResult" -ForegroundColor Yellow
    }
    
    # Grant privileges
    $grantResult = & psql -h localhost -p 5432 -U postgres -d sarvanom_db -c "GRANT ALL PRIVILEGES ON DATABASE sarvanom_db TO sarvanom_user;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Privileges granted successfully!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Privilege grant result: $grantResult" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Failed to create database/user: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 8: Test new connection
Write-Host "`n🔧 Step 8: Testing new connection..." -ForegroundColor Yellow
try {
    $testNewConnection = & psql -h localhost -p 5432 -U sarvanom_user -d sarvanom_db -c "SELECT current_database(), current_user;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ New connection test successful!" -ForegroundColor Green
        Write-Host "📊 Connection info: $testNewConnection" -ForegroundColor Cyan
    } else {
        Write-Host "❌ New connection test failed: $testNewConnection" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Cannot test new connection" -ForegroundColor Red
}

# Step 9: Provide .env configuration
Write-Host "`n📋 Step 9: .env Configuration" -ForegroundColor Yellow
Write-Host "=============================" -ForegroundColor Yellow
Write-Host "Add this line to your .env file:" -ForegroundColor White
Write-Host "DATABASE_URL=postgresql://sarvanom_user:sarvanom_password@localhost:5432/sarvanom_db" -ForegroundColor Cyan

Write-Host "`n✅ Complete PostgreSQL fix completed!" -ForegroundColor Green
Write-Host "🎯 PostgreSQL should now be working for your SarvanOM application!" -ForegroundColor Green 