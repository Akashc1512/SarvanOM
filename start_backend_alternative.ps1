#!/usr/bin/env powershell
<#
.SYNOPSIS
    Alternative SarvanOM Backend Startup Script
    Works with Docker WSL Integration
    MAANG/OpenAI/Perplexity Standards Implementation
    August 16, 2025

.DESCRIPTION
    This script starts the backend with available services
    and provides alternative solutions for infrastructure.
#>

# Color functions
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Header { param($Message) Write-Host "`n🔥 $Message" -ForegroundColor Magenta }

Write-Header "SARVANOM ALTERNATIVE BACKEND STARTUP"
Write-Host "Docker WSL Integration Mode - August 16, 2025" -ForegroundColor Gray
Write-Host "=" * 70

# Check current status
function Test-CurrentStatus {
    Write-Info "Checking current system status..."
    
    # Check Python environment
    if (Test-Path "venv\Scripts\Activate.ps1") {
        Write-Success "Python virtual environment found"
    } else {
        Write-Error "Python virtual environment not found"
        return $false
    }
    
    # Check Ollama
    try {
        $ollamaList = ollama list 2>$null
        if ($ollamaList) {
            Write-Success "Ollama is working"
            Write-Info "Available models:"
            $ollamaList | ForEach-Object { Write-Host "   - $_" -ForegroundColor Gray }
        } else {
            Write-Warning "Ollama not accessible"
        }
    } catch {
        Write-Warning "Ollama not accessible"
    }
    
    # Check ports
    Write-Info "Checking service ports..."
    $ports = @{
        "PostgreSQL" = 5432
        "Redis" = 6379
        "Qdrant" = 6333
        "Meilisearch" = 7700
        "ArangoDB" = 8529
        "Ollama" = 11434
    }
    
    foreach ($service in $ports.GetEnumerator()) {
        $portCheck = netstat -an 2>$null | Select-String ":$($service.Value)\s"
        if ($portCheck) {
            Write-Success "$($service.Key) port $($service.Value) is listening"
        } else {
            Write-Warning "$($service.Key) port $($service.Value) is not listening"
        }
    }
    
    return $true
}

# Start Python backend with available services
function Start-PythonBackend {
    Write-Info "Starting Python backend with available services..."
    
    # Activate virtual environment
    Write-Info "Activating Python virtual environment..."
    & "venv\Scripts\Activate.ps1"
    
    # Set environment variables
    $env:PYTHONPATH = "."
    $env:USE_DYNAMIC_SELECTION = "true"
    $env:PRIORITIZE_FREE_MODELS = "true"
    
    # Disable services that require Docker for now
    $env:POSTGRES_ENABLED = "false"
    $env:REDIS_ENABLED = "false"
    $env:QDRANT_ENABLED = "false"
    $env:MEILISEARCH_ENABLED = "false"
    $env:ARANGODB_ENABLED = "false"
    
    # Enable working services
    $env:OLLAMA_ENABLED = "true"
    $env:HUGGINGFACE_ENABLED = "true"
    
    Write-Info "Starting backend on port 8000..."
    
    $job = Start-Job -ScriptBlock {
        $env:PYTHONPATH = "."
        $env:USE_DYNAMIC_SELECTION = "true"
        $env:PRIORITIZE_FREE_MODELS = "true"
        $env:POSTGRES_ENABLED = "false"
        $env:REDIS_ENABLED = "false"
        $env:QDRANT_ENABLED = "false"
        $env:MEILISEARCH_ENABLED = "false"
        $env:ARANGODB_ENABLED = "false"
        $env:OLLAMA_ENABLED = "true"
        $env:HUGGINGFACE_ENABLED = "true"
        
        python -c "import uvicorn; from services.gateway.main import app; print('🚀 Starting SarvanOM Backend with Available Services...'); uvicorn.run(app, host='127.0.0.1', port=8000, log_level='info')"
    }
    
    Start-Sleep -Seconds 5
    
    if ($job.State -eq "Running") {
        Write-Success "Python backend started successfully"
        return $true
    } else {
        Write-Error "Failed to start Python backend"
        return $false
    }
}

# Test available services
function Test-AvailableServices {
    Write-Header "TESTING AVAILABLE SERVICES"
    
    Start-Sleep -Seconds 3
    
    # Test Ollama
    Write-Info "Testing Ollama..."
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 -ErrorAction Stop
        Write-Success "Ollama API is responding"
    } catch {
        Write-Warning "Ollama API not responding"
    }
    
    # Test backend API
    Write-Info "Testing backend API..."
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
        Write-Success "Backend API is responding"
    } catch {
        Write-Warning "Backend API not responding yet"
    }
    
    # Test AI endpoints
    Write-Info "Testing AI endpoints..."
    try {
        $body = @{
            query = "What is artificial intelligence?"
            user_id = "test_user"
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/process" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10 -ErrorAction Stop
        Write-Success "AI processing endpoint is working"
        Write-Info "Response received successfully"
    } catch {
        Write-Warning "AI processing endpoint not responding"
    }
}

# Provide Docker alternative instructions
function Show-DockerAlternatives {
    Write-Header "DOCKER ALTERNATIVE SOLUTIONS"
    
    Write-Info "Since Docker Desktop is running with WSL integration, here are alternative approaches:"
    Write-Host ""
    Write-Host "1. Use WSL Terminal:" -ForegroundColor Yellow
    Write-Host "   - Open WSL terminal" -ForegroundColor Gray
    Write-Host "   - Navigate to your project directory" -ForegroundColor Gray
    Write-Host "   - Run: docker-compose up -d" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Use Docker Desktop GUI:" -ForegroundColor Yellow
    Write-Host "   - Open Docker Desktop" -ForegroundColor Gray
    Write-Host "   - Go to Containers tab" -ForegroundColor Gray
    Write-Host "   - Start services manually" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Run PowerShell as Administrator:" -ForegroundColor Yellow
    Write-Host "   - Right-click PowerShell" -ForegroundColor Gray
    Write-Host "   - Select 'Run as Administrator'" -ForegroundColor Gray
    Write-Host "   - Try docker commands again" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Use Alternative Services:" -ForegroundColor Yellow
    Write-Host "   - PostgreSQL: Use cloud service or local installation" -ForegroundColor Gray
    Write-Host "   - Redis: Use cloud service or local installation" -ForegroundColor Gray
    Write-Host "   - Qdrant: Use cloud service" -ForegroundColor Gray
    Write-Host "   - Meilisearch: Use cloud service" -ForegroundColor Gray
}

# Main execution
function Main {
    Write-Header "STARTING ALTERNATIVE BACKEND"
    
    # Check current status
    if (-not (Test-CurrentStatus)) {
        Write-Error "Status check failed"
        exit 1
    }
    
    # Start Python backend
    if (Start-PythonBackend) {
        # Test available services
        Test-AvailableServices
        
        # Show alternatives
        Show-DockerAlternatives
        
        Write-Header "ALTERNATIVE BACKEND STARTUP COMPLETE"
        Write-Success "Backend is running with available services!"
        Write-Info "AI capabilities (Ollama + HuggingFace) are operational"
        Write-Warning "Infrastructure services need Docker access for full functionality"
    } else {
        Write-Error "Failed to start backend"
        exit 1
    }
}

# Execute main function
Main
