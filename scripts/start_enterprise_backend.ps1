# SarvanOM Enterprise Backend Startup Script (PowerShell)
# MAANG/OpenAI/Perplexity Standards Implementation

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "monitoring", "health", "status", "stop", "restart")]
    [string]$Command = "start"
)

# Configuration
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ComposeFile = Join-Path $ProjectRoot "docker-compose.enterprise.yml"
$EnvFile = Join-Path $ProjectRoot ".env.docker"
$LogDir = Join-Path $ProjectRoot "logs"
$DataDir = Join-Path $ProjectRoot "data"

# Service ports
$GatewayPort = 8000
$AuthPort = 8001
$SearchPort = 8002
$SynthesisPort = 8003
$FactCheckPort = 8004
$RetrievalPort = 8005
$NginxPort = 80
$RedisPort = 6379
$PostgresPort = 5432
$QdrantPort = 6333
$MeilisearchPort = 7700

# Monitoring ports
$PrometheusPort = 9090
$GrafanaPort = 3000
$JaegerPort = 16686

# Functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check Docker - try multiple methods
    $dockerFound = $false
    
    # Method 1: Try direct docker command
    try {
        docker --version | Out-Null
        $dockerFound = $true
        Write-Info "Docker found via PATH"
    }
    catch {
        Write-Info "Docker not found in PATH, trying alternative methods..."
    }
    
    # Method 2: Try Docker Desktop executable
    if (-not $dockerFound) {
        try {
            & "C:\Program Files\Docker\Docker\resources\bin\docker.exe" --version | Out-Null
            $dockerFound = $true
            Write-Info "Docker found via Docker Desktop executable"
            # Add to PATH for this session
            $env:PATH += ";C:\Program Files\Docker\Docker\resources\bin"
        }
        catch {
            Write-Info "Docker Desktop executable not found"
        }
    }
    
    # Method 3: Check if Docker Desktop is running
    if (-not $dockerFound) {
        $dockerProcesses = Get-Process -Name "*docker*" -ErrorAction SilentlyContinue
        if ($dockerProcesses) {
            Write-Info "Docker Desktop processes detected, attempting to use Docker..."
            $dockerFound = $true
            # Try to set PATH to common Docker locations
            $possiblePaths = @(
                "C:\Program Files\Docker\Docker\resources\bin",
                "C:\Program Files\Docker\Docker",
                "$env:USERPROFILE\AppData\Local\Docker\cli-plugins"
            )
            foreach ($path in $possiblePaths) {
                if (Test-Path $path) {
                    $env:PATH += ";$path"
                    break
                }
            }
        }
    }
    
    if (-not $dockerFound) {
        Write-Error "Docker is not accessible. Please ensure Docker Desktop is running and try again."
        Write-Info "You can also try running: Start-Process 'C:\Program Files\Docker\Docker\Docker Desktop.exe'"
        exit 1
    }
    
    # Test Docker functionality
    try {
        docker info | Out-Null
        Write-Success "Docker is accessible and running"
    }
    catch {
        Write-Error "Docker is installed but not responding. Please ensure Docker Desktop is fully started."
        Write-Info "Try restarting Docker Desktop and wait for it to fully initialize."
        exit 1
    }
    
    # Check Docker Compose
    try {
        docker-compose --version | Out-Null
        Write-Success "Docker Compose is available"
    }
    catch {
        try {
            docker compose version | Out-Null
            Write-Success "Docker Compose (v2) is available"
        }
        catch {
            Write-Error "Docker Compose is not available. Please install Docker Compose."
            exit 1
        }
    }
    
    Write-Success "Prerequisites check passed"
}

function New-Directories {
    Write-Info "Creating necessary directories..."
    
    $directories = @(
        $LogDir,
        $DataDir,
        (Join-Path $ProjectRoot "nginx\ssl"),
        (Join-Path $ProjectRoot "monitoring\grafana\dashboards"),
        (Join-Path $ProjectRoot "monitoring\grafana\datasources")
    )
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Success "Directories created"
}

function Test-Environment {
    Write-Info "Checking environment configuration..."
    
    if (!(Test-Path $EnvFile)) {
        Write-Warning "Environment file not found. Creating default .env.docker..."
        
        $envContent = @"
# SarvanOM Enterprise Environment Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database Configuration
POSTGRES_DB=sarvanom_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Redis Configuration
REDIS_URL=redis://redis:6379

# Vector Database Configuration
QDRANT_URL=http://qdrant:6333
MEILI_MASTER_KEY=your_master_key_here

# Monitoring Configuration
GRAFANA_PASSWORD=admin

# API Configuration
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10

# Security Configuration
JWT_SECRET_KEY=your_jwt_secret_here
CORS_ORIGINS=http://localhost:3000,https://sarvanom.com

# LLM Configuration
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
OLLAMA_BASE_URL=http://localhost:11434

# HuggingFace Configuration
HUGGINGFACE_API_KEY=your_huggingface_key_here
"@
        
        $envContent | Out-File -FilePath $EnvFile -Encoding UTF8
        Write-Warning "Please update $EnvFile with your actual configuration values"
    }
    
    Write-Success "Environment configuration checked"
}

function Start-Services {
    Write-Info "Starting SarvanOM Enterprise Backend..."
    
    # Start core services
    docker-compose -f $ComposeFile up -d redis, postgres, qdrant, meilisearch
    
    Write-Info "Waiting for infrastructure services to be ready..."
    Start-Sleep -Seconds 10
    
    # Start application services
    docker-compose -f $ComposeFile up -d auth, search, synthesis, fact-check, retrieval, gateway
    
    Write-Info "Waiting for application services to be ready..."
    Start-Sleep -Seconds 15
    
    # Start load balancer
    docker-compose -f $ComposeFile up -d nginx
    
    Write-Success "All services started"
}

function Wait-ForService {
    param(
        [string]$ServiceName,
        [int]$Port,
        [int]$MaxAttempts = 30
    )
    
    Write-Info "Waiting for $ServiceName to be ready on port $Port..."
    
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$Port/health" -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Success "$ServiceName is ready"
                return $true
            }
        }
        catch {
            # Service not ready yet
        }
        
        Write-Info "Attempt $attempt/$MaxAttempts : $ServiceName not ready yet..."
        Start-Sleep -Seconds 2
    }
    
    Write-Error "$ServiceName failed to start within expected time"
    return $false
}

function Test-Health {
    Write-Info "Performing health checks..."
    
    $services = @(
        @{Name="Gateway"; Port=$GatewayPort},
        @{Name="Auth"; Port=$AuthPort},
        @{Name="Search"; Port=$SearchPort},
        @{Name="Synthesis"; Port=$SynthesisPort},
        @{Name="Fact-Check"; Port=$FactCheckPort},
        @{Name="Retrieval"; Port=$RetrievalPort},
        @{Name="Nginx"; Port=$NginxPort}
    )
    
    $failedServices = @()
    
    foreach ($service in $services) {
        if (!(Wait-ForService -ServiceName $service.Name -Port $service.Port)) {
            $failedServices += $service.Name
        }
    }
    
    if ($failedServices.Count -eq 0) {
        Write-Success "All services are healthy"
        return $true
    }
    else {
        Write-Error "The following services failed health checks: $($failedServices -join ', ')"
        return $false
    }
}

function Start-Monitoring {
    Write-Info "Starting monitoring stack..."
    
    docker-compose -f $ComposeFile --profile monitoring up -d
    
    Write-Info "Waiting for monitoring services to be ready..."
    Start-Sleep -Seconds 10
    
    Write-Success "Monitoring stack started"
    Write-Info "Prometheus: http://localhost:$PrometheusPort"
    Write-Info "Grafana: http://localhost:$GrafanaPort (admin/admin)"
    Write-Info "Jaeger: http://localhost:$JaegerPort"
}

function Show-Status {
    Write-Info "SarvanOM Enterprise Backend Status:"
    Write-Host ""
    
    # Service status
    docker-compose -f $ComposeFile ps
    
    Write-Host ""
    Write-Info "Service URLs:"
    Write-Host "  🌐 Main API: http://localhost:$NginxPort"
    Write-Host "  🔍 API Gateway: http://localhost:$GatewayPort"
    Write-Host "  📚 API Documentation: http://localhost:$GatewayPort/docs"
    Write-Host "  🔐 Authentication: http://localhost:$AuthPort"
    Write-Host "  🔎 Search: http://localhost:$SearchPort"
    Write-Host "  🧠 Synthesis: http://localhost:$SynthesisPort"
    Write-Host "  ✅ Fact Check: http://localhost:$FactCheckPort"
    Write-Host "  📖 Retrieval: http://localhost:$RetrievalPort"
    Write-Host ""
    
    Write-Info "Infrastructure:"
    Write-Host "  🗄️  PostgreSQL: localhost:$PostgresPort"
    Write-Host "  🔄 Redis: localhost:$RedisPort"
    Write-Host "  🧮 Qdrant: localhost:$QdrantPort"
    Write-Host "  🔍 Meilisearch: localhost:$MeilisearchPort"
    Write-Host ""
    
    Write-Info "Monitoring:"
    Write-Host "  📊 Prometheus: http://localhost:$PrometheusPort"
    Write-Host "  📈 Grafana: http://localhost:$GrafanaPort"
    Write-Host "  🔍 Jaeger: http://localhost:$JaegerPort"
    Write-Host ""
    
    Write-Info "Health Check:"
    Write-Host "  curl http://localhost/health"
    Write-Host ""
}

function Stop-Services {
    Write-Info "Cleaning up..."
    docker-compose -f $ComposeFile down --remove-orphans
    Write-Success "Cleanup completed"
}

# Main execution
Write-Host "🚀 SarvanOM Enterprise Backend Startup" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

switch ($Command) {
    "start" {
        Test-Prerequisites
        New-Directories
        Test-Environment
        Start-Services
        if (Test-Health) {
            Show-Status
            Write-Success "SarvanOM Enterprise Backend is ready!"
        }
        else {
            Write-Error "Some services failed to start properly"
            exit 1
        }
    }
    "monitoring" {
        Start-Monitoring
    }
    "health" {
        Test-Health
    }
    "status" {
        Show-Status
    }
    "stop" {
        Stop-Services
    }
    "restart" {
        Stop-Services
        Start-Sleep -Seconds 2
        & $PSCommandPath "start"
    }
    default {
        Write-Host "Usage: $PSCommandPath {start|monitoring|health|status|stop|restart}"
        Write-Host ""
        Write-Host "Commands:"
        Write-Host "  start      - Start all services"
        Write-Host "  monitoring - Start monitoring stack"
        Write-Host "  health     - Perform health checks"
        Write-Host "  status     - Show service status"
        Write-Host "  stop       - Stop all services"
        Write-Host "  restart    - Restart all services"
        exit 1
    }
}
