# Final PostgreSQL Fix Script for SarvanOM
# Run this script as Administrator

Write-Host "🔧 Final PostgreSQL Fix for SarvanOM" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "❌ This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "💡 Right-click on PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Running as Administrator" -ForegroundColor Green

# Step 1: Stop any running PostgreSQL processes
Write-Host "`n🔧 Step 1: Stopping PostgreSQL processes..." -ForegroundColor Yellow
try {
    Stop-Service -Name "postgresql-x64-17" -Force -ErrorAction SilentlyContinue
    Write-Host "✅ PostgreSQL service stopped" -ForegroundColor Green
} catch {
    Write-Host "ℹ️ PostgreSQL service was not running" -ForegroundColor Cyan
}

# Kill any remaining PostgreSQL processes
try {
    Get-Process -Name "postgres" -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "✅ Killed any remaining PostgreSQL processes" -ForegroundColor Green
} catch {
    Write-Host "ℹ️ No PostgreSQL processes found" -ForegroundColor Cyan
}

# Step 2: Fix permissions and recreate data directory
Write-Host "`n🔧 Step 2: Fixing permissions and recreating data directory..." -ForegroundColor Yellow
$postgresPath = "C:\Program Files\PostgreSQL\17"
$postgresDataPath = "$postgresPath\data"

# Take ownership and grant permissions
try {
    & takeown /f "$postgresPath" /r /d y
    Write-Host "✅ Took ownership of PostgreSQL directory" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Could not take ownership: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Grant full permissions
try {
    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    & icacls "$postgresPath" /grant "${currentUser}:(OI)(CI)F" /t
    Write-Host "✅ Granted full permissions to $currentUser" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Could not grant permissions: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Remove existing data directory completely
if (Test-Path $postgresDataPath) {
    try {
        Remove-Item $postgresDataPath -Recurse -Force
        Write-Host "✅ Removed existing data directory" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to remove data directory: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "🔧 Trying to force remove..." -ForegroundColor Yellow
        try {
            & cmd /c "rmdir /s /q `"$postgresDataPath`""
            Write-Host "✅ Force removed data directory" -ForegroundColor Green
        } catch {
            Write-Host "❌ Could not remove data directory" -ForegroundColor Red
        }
    }
}

# Create new data directory
try {
    New-Item -ItemType Directory -Path $postgresDataPath -Force
    Write-Host "✅ Created new data directory" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create data directory: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 3: Initialize PostgreSQL data directory properly
Write-Host "`n🔧 Step 3: Initializing PostgreSQL data directory..." -ForegroundColor Yellow
$postgresBinPath = "$postgresPath\bin"

try {
    # Set environment variables
    $env:PGDATA = $postgresDataPath
    $env:PGHOST = "localhost"
    $env:PGPORT = "5432"
    
    # Initialize with trust authentication
    Write-Host "🔧 Running initdb with trust authentication..." -ForegroundColor Yellow
    & "$postgresBinPath\initdb.exe" -D $postgresDataPath -U postgres --auth=trust --encoding=UTF8 --locale=C
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL data directory initialized successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to initialize PostgreSQL data directory" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error during initialization: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 4: Configure PostgreSQL for local connections
Write-Host "`n🔧 Step 4: Configuring PostgreSQL for local connections..." -ForegroundColor Yellow
$pgHbaFile = Join-Path $postgresDataPath "pg_hba.conf"

if (Test-Path $pgHbaFile) {
    # Create a simple pg_hba.conf for local development
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
        Write-Host "❌ Failed to update pg_hba.conf: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "❌ pg_hba.conf not found after initialization" -ForegroundColor Red
    exit 1
}

# Step 5: Start PostgreSQL manually
Write-Host "`n🔧 Step 5: Starting PostgreSQL..." -ForegroundColor Yellow
try {
    # Start PostgreSQL manually
    & "$postgresBinPath\pg_ctl.exe" start -D $postgresDataPath -s -w
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL started successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to start PostgreSQL" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error starting PostgreSQL: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 6: Wait and test connection
Write-Host "`n🔧 Step 6: Testing PostgreSQL connection..." -ForegroundColor Yellow
Start-Sleep -Seconds 3  # Give service time to start

try {
    $testResult = & "$postgresBinPath\psql.exe" -h localhost -p 5432 -U postgres -d postgres -c "SELECT version();" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL connection successful!" -ForegroundColor Green
        Write-Host "📊 Server info: $testResult" -ForegroundColor Cyan
    } else {
        Write-Host "❌ PostgreSQL connection failed" -ForegroundColor Red
        Write-Host "💡 Error: $testResult" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Cannot test connection: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 7: Create database and user
Write-Host "`n🔧 Step 7: Creating database and user..." -ForegroundColor Yellow
try {
    # Create database
    $createDbResult = & "$postgresBinPath\psql.exe" -h localhost -p 5432 -U postgres -d postgres -c "CREATE DATABASE sarvanom_db;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database 'sarvanom_db' created successfully!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Database creation result: $createDbResult" -ForegroundColor Yellow
    }
    
    # Create user
    $createUserResult = & "$postgresBinPath\psql.exe" -h localhost -p 5432 -U postgres -d postgres -c "CREATE USER sarvanom_user WITH PASSWORD 'sarvanom_password';" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ User 'sarvanom_user' created successfully!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ User creation result: $createUserResult" -ForegroundColor Yellow
    }
    
    # Grant privileges
    $grantResult = & "$postgresBinPath\psql.exe" -h localhost -p 5432 -U postgres -d sarvanom_db -c "GRANT ALL PRIVILEGES ON DATABASE sarvanom_db TO sarvanom_user;" 2>&1
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
    $testNewConnection = & "$postgresBinPath\psql.exe" -h localhost -p 5432 -U sarvanom_user -d sarvanom_db -c "SELECT current_database(), current_user;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ New connection test successful!" -ForegroundColor Green
        Write-Host "📊 Connection info: $testNewConnection" -ForegroundColor Cyan
    } else {
        Write-Host "❌ New connection test failed: $testNewConnection" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Cannot test new connection: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 9: Provide .env configuration
Write-Host "`n📋 Step 9: .env Configuration" -ForegroundColor Yellow
Write-Host "=============================" -ForegroundColor Yellow
Write-Host "Add this line to your .env file:" -ForegroundColor White
Write-Host "DATABASE_URL=postgresql://sarvanom_user:sarvanom_password@localhost:5432/sarvanom_db" -ForegroundColor Cyan

Write-Host "`n✅ Final PostgreSQL fix completed!" -ForegroundColor Green
Write-Host "🎯 PostgreSQL should now be working for your SarvanOM application!" -ForegroundColor Green 