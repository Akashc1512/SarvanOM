# =============================================================================
# SarvanOM Critical Setup Steps for E2E Testing
# =============================================================================
# This script handles all critical cleanup steps before E2E testing
# =============================================================================

Write-Host "🚨 SarvanOM Critical Setup Steps for E2E Testing" -ForegroundColor Red
Write-Host "=================================================================" -ForegroundColor Red
Write-Host ""

# Step 1: Check Docker Desktop Status
Write-Host "Step 1: Checking Docker Desktop Status..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker is available" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker is not available. Please start Docker Desktop first." -ForegroundColor Red
        Write-Host "   - Open Docker Desktop from Start Menu" -ForegroundColor Cyan
        Write-Host "   - Wait for the whale icon to appear in system tray" -ForegroundColor Cyan
        Write-Host "   - Make sure it shows 'Docker Desktop is running'" -ForegroundColor Cyan
        exit 1
    }
} catch {
    Write-Host "❌ Docker command failed. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Step 2: Verify .env.docker exists
Write-Host "`nStep 2: Verifying environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env.docker") {
    Write-Host "✅ .env.docker file exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env.docker file not found. Creating from template..." -ForegroundColor Yellow
    if (Test-Path "env.docker.template") {
        Copy-Item "env.docker.template" ".env.docker"
        Write-Host "✅ .env.docker created from template" -ForegroundColor Green
    } else {
        Write-Host "❌ env.docker.template not found!" -ForegroundColor Red
        exit 1
    }
}

# Step 3: Create data directories
Write-Host "`nStep 3: Setting up data directories..." -ForegroundColor Yellow
$dataDirs = @(
    "data/postgres",
    "data/redis", 
    "data/meilisearch",
    "data/arangodb",
    "data/arangodb-apps",
    "data/qdrant",
    "data/ollama"
)

foreach ($dir in $dataDirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        Write-Host "✅ Created $dir" -ForegroundColor Green
    } else {
        Write-Host "✅ $dir already exists" -ForegroundColor Green
    }
}

# Step 4: Start Docker Compose Services
Write-Host "`nStep 4: Starting Docker Compose services..." -ForegroundColor Yellow
Write-Host "This may take several minutes for all services to start..." -ForegroundColor Cyan

try {
    docker compose --env-file .env.docker up --build -d
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker Compose services started successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to start Docker Compose services" -ForegroundColor Red
        Write-Host "Check the error messages above and ensure Docker Desktop is running" -ForegroundColor Cyan
        exit 1
    }
} catch {
    Write-Host "❌ Error starting Docker Compose services" -ForegroundColor Red
    exit 1
}

# Step 5: Wait for services to be healthy
Write-Host "`nStep 5: Waiting for services to be healthy..." -ForegroundColor Yellow
Write-Host "This may take 2-3 minutes for all services to be ready..." -ForegroundColor Cyan

$maxAttempts = 30
$attempt = 0
$healthyServices = 0

while ($attempt -lt $maxAttempts) {
    $attempt++
    Write-Host "Attempt $attempt/$maxAttempts - Checking service health..." -ForegroundColor Cyan
    
    try {
        $services = docker compose ps --format json | ConvertFrom-Json
        $runningServices = ($services | Where-Object { $_.State -eq "running" }).Count
        $totalServices = $services.Count
        
        Write-Host "   Running: $runningServices/$totalServices services" -ForegroundColor White
        
        if ($runningServices -eq $totalServices) {
            Write-Host "✅ All services are running!" -ForegroundColor Green
            break
        }
        
        Start-Sleep -Seconds 10
    } catch {
        Write-Host "   Still waiting for services to start..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    }
}

if ($attempt -eq $maxAttempts) {
    Write-Host "⚠️  Timeout waiting for services. Some services may still be starting." -ForegroundColor Yellow
}

# Step 6: Preload Ollama Models
Write-Host "`nStep 6: Preloading Ollama models..." -ForegroundColor Yellow
Write-Host "This step downloads the LLM model (may take 5-10 minutes)..." -ForegroundColor Cyan

try {
    Write-Host "Pulling Mistral model for Ollama..." -ForegroundColor Cyan
    docker exec sarvanom-ollama ollama pull mistral
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Mistral model downloaded successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Failed to download Mistral model. You can download it manually later." -ForegroundColor Yellow
        Write-Host "   Run: docker exec sarvanom-ollama ollama pull mistral" -ForegroundColor Cyan
    }
} catch {
    Write-Host "⚠️  Could not preload Ollama models. Container may not be ready yet." -ForegroundColor Yellow
}

# Step 7: Verify ArangoDB Configuration
Write-Host "`nStep 7: Verifying ArangoDB configuration..." -ForegroundColor Yellow

try {
    $arangodbResponse = Invoke-WebRequest -Uri "http://localhost:8529/_api/version" -TimeoutSec 10 -ErrorAction SilentlyContinue
    if ($arangodbResponse.StatusCode -eq 200) {
        Write-Host "✅ ArangoDB is responding" -ForegroundColor Green
    } else {
        Write-Host "⚠️  ArangoDB responded with status: $($arangodbResponse.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  ArangoDB not responding yet. It may still be starting up." -ForegroundColor Yellow
}

# Step 8: Run Health Check
Write-Host "`nStep 8: Running comprehensive health check..." -ForegroundColor Yellow

try {
    python test_docker_health.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ All services are healthy!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Some services may have issues. Check the health report above." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Could not run health check. Make sure Python and required packages are installed." -ForegroundColor Yellow
}

# Step 9: Display Service URLs
Write-Host "`nStep 9: Service Access Information" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "Frontend:     http://localhost:3000" -ForegroundColor Green
Write-Host "Backend API:  http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs:     http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Ollama:       http://localhost:11434" -ForegroundColor Green
Write-Host "Meilisearch:  http://localhost:7700" -ForegroundColor Green
Write-Host "ArangoDB:     http://localhost:8529" -ForegroundColor Green
Write-Host "Qdrant:       http://localhost:6333" -ForegroundColor Green
Write-Host ""

# Step 10: Next Steps
Write-Host "Step 10: Next Steps for E2E Testing" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "1. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host "2. Test the API at http://localhost:8000/docs" -ForegroundColor White
Write-Host "3. Monitor logs: docker compose logs -f" -ForegroundColor White
Write-Host "4. Check health: .\docker-windows.bat health" -ForegroundColor White
Write-Host "5. Run tests: .\docker-windows.bat test" -ForegroundColor White
Write-Host ""

Write-Host "🎉 Critical setup steps completed!" -ForegroundColor Green
Write-Host "Your SarvanOM environment is ready for E2E testing." -ForegroundColor Green 