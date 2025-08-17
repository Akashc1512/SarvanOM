#!/usr/bin/env powershell
<#
.SYNOPSIS
    Comprehensive SarvanOM Backend Startup Script
    MAANG/OpenAI/Perplexity Standards Implementation
    August 16, 2025

.DESCRIPTION
    This script starts all backend services and verifies their status
    following MAANG/OpenAI/Perplexity enterprise standards.
#>

param(
    [switch]$SkipDocker,
    [switch]$ForceRestart,
    [switch]$VerifyOnly
)

# Color functions
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Header { param($Message) Write-Host "`n🔥 $Message" -ForegroundColor Magenta }

Write-Header "SARVANOM COMPREHENSIVE BACKEND STARTUP"
Write-Host "MAANG/OpenAI/Perplexity Standards - August 16, 2025" -ForegroundColor Gray
Write-Host "=" * 70

# Check prerequisites
function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check Python environment
    if (Test-Path "venv\Scripts\Activate.ps1") {
        Write-Success "Python virtual environment found"
    } else {
        Write-Error "Python virtual environment not found"
        return $false
    }
    
    # Check Docker
    if (-not $SkipDocker) {
        try {
            $dockerVersion = docker --version 2>$null
            if ($dockerVersion) {
                Write-Success "Docker found: $dockerVersion"
            } else {
                Write-Warning "Docker not accessible - will skip Docker services"
                $SkipDocker = $true
            }
        } catch {
            Write-Warning "Docker not accessible - will skip Docker services"
            $SkipDocker = $true
        }
    }
    
    # Check Ollama
    try {
        $ollamaList = ollama list 2>$null
        if ($ollamaList) {
            Write-Success "Ollama found and accessible"
        } else {
            Write-Warning "Ollama not accessible"
        }
    } catch {
        Write-Warning "Ollama not accessible"
    }
    
    return $true
}

# Start Docker services
function Start-DockerServices {
    if ($SkipDocker) {
        Write-Warning "Skipping Docker services"
        return
    }
    
    Write-Info "Starting Docker services..."
    
    # Stop existing services if force restart
    if ($ForceRestart) {
        Write-Info "Stopping existing services..."
        docker-compose down 2>$null
    }
    
    # Start core services
    Write-Info "Starting core infrastructure services..."
    docker-compose up -d postgres redis qdrant meilisearch arangodb 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker services started successfully"
    } else {
        Write-Error "Failed to start Docker services"
        return $false
    }
    
    # Wait for services to be ready
    Write-Info "Waiting for services to be ready..."
    Start-Sleep -Seconds 15
    
    return $true
}

# Start Ollama service
function Start-OllamaService {
    Write-Info "Checking Ollama service..."
    
    try {
        $ollamaList = ollama list 2>$null
        if ($ollamaList) {
            Write-Success "Ollama service is running"
            Write-Info "Available models:"
            $ollamaList | ForEach-Object { Write-Host "   - $_" -ForegroundColor Gray }
        } else {
            Write-Warning "Ollama service not accessible"
        }
    } catch {
        Write-Warning "Ollama service not accessible"
    }
}

# Start Python backend
function Start-PythonBackend {
    Write-Info "Starting Python backend services..."
    
    # Activate virtual environment
    Write-Info "Activating Python virtual environment..."
    & "venv\Scripts\Activate.ps1"
    
    # Set environment variables
    $env:PYTHONPATH = "."
    $env:USE_DYNAMIC_SELECTION = "true"
    $env:PRIORITIZE_FREE_MODELS = "true"
    
    # Start backend on different ports
    $ports = @(8000, 8001, 8002, 8003, 8004, 8005, 8006)
    
    foreach ($port in $ports) {
        Write-Info "Starting backend on port $port..."
        
        $job = Start-Job -ScriptBlock {
            param($port)
            $env:PYTHONPATH = "."
            $env:USE_DYNAMIC_SELECTION = "true"
            $env:PRIORITIZE_FREE_MODELS = "true"
            python -c "import uvicorn; from services.gateway.main import app; print('🚀 Starting SarvanOM Backend on port $port...'); uvicorn.run(app, host='127.0.0.1', port=$port, log_level='info')"
        } -ArgumentList $port
        
        Start-Sleep -Seconds 3
    }
    
    Write-Success "Python backend services started"
}

# Verify services
function Test-ServiceHealth {
    Write-Header "VERIFYING SERVICE HEALTH"
    
    $services = @{
        "PostgreSQL" = @{Port = 5432; URL = "postgresql://postgres:password@localhost:5432/sarvanom"}
        "Redis" = @{Port = 6379; URL = "redis://localhost:6379/0"}
        "Qdrant" = @{Port = 6333; URL = "http://localhost:6333/health"}
        "Meilisearch" = @{Port = 7700; URL = "http://localhost:7700/version"}
        "ArangoDB" = @{Port = 8529; URL = "http://localhost:8529/_api/version"}
        "Ollama" = @{Port = 11434; URL = "http://localhost:11434/api/tags"}
    }
    
    foreach ($service in $services.GetEnumerator()) {
        $name = $service.Key
        $config = $service.Value
        
        Write-Info "Testing $name..."
        
        # Check port
        $portCheck = netstat -an 2>$null | Select-String ":$($config.Port)\s"
        if ($portCheck) {
            Write-Success "$name port $($config.Port) is listening"
        } else {
            Write-Warning "$name port $($config.Port) is not listening"
        }
        
        # Test connection if possible
        if ($config.URL -like "http*") {
            try {
                $response = Invoke-WebRequest -Uri $config.URL -TimeoutSec 5 -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    Write-Success "$name connection successful"
                } else {
                    Write-Warning "$name returned status $($response.StatusCode)"
                }
            } catch {
                Write-Warning "$name connection failed"
            }
        }
    }
}

# Run comprehensive test
function Test-ComprehensiveBackend {
    Write-Header "RUNNING COMPREHENSIVE BACKEND TEST"
    
    # Activate virtual environment
    & "venv\Scripts\Activate.ps1"
    
    # Set environment variables
    $env:PYTHONPATH = "."
    
    # Run the comprehensive test
    Write-Info "Running comprehensive backend test..."
    python test_all_components_final.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Comprehensive test completed"
    } else {
        Write-Error "Comprehensive test failed"
    }
}

# Main execution
function Main {
    Write-Header "STARTING SARVANOM BACKEND"
    
    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-Error "Prerequisites check failed"
        exit 1
    }
    
    # Start services
    if (-not $VerifyOnly) {
        # Start Docker services
        Start-DockerServices
        
        # Start Ollama service
        Start-OllamaService
        
        # Start Python backend
        Start-PythonBackend
        
        # Wait for services to be ready
        Write-Info "Waiting for all services to be ready..."
        Start-Sleep -Seconds 10
    }
    
    # Verify services
    Test-ServiceHealth
    
    # Run comprehensive test
    Test-ComprehensiveBackend
    
    Write-Header "BACKEND STARTUP COMPLETE"
    Write-Success "SarvanOM backend is ready!"
    Write-Info "Check the test results above for detailed status"
}

# Execute main function
Main
