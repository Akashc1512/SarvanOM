# Universal Knowledge Hub - Development Scripts for Windows PowerShell
# Usage: .\scripts\dev.ps1 [command]

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

# Simple command dispatcher
switch ($Command) {
    "help" {
        Write-Host "Universal Knowledge Hub - Available Commands:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Setup:" -ForegroundColor Yellow
        Write-Host "  install     - Install all dependencies"
        Write-Host "  setup       - Complete project setup"
        Write-Host ""
        Write-Host "Development:" -ForegroundColor Yellow
        Write-Host "  dev         - Start development servers"
        Write-Host "  dev:frontend- Start frontend only"
        Write-Host "  dev:backend - Start backend only"
        Write-Host ""
        Write-Host "Testing:" -ForegroundColor Yellow
        Write-Host "  test        - Run all tests"
        Write-Host "  test:unit   - Run unit tests"
        Write-Host ""
        Write-Host "Code Quality:" -ForegroundColor Yellow
        Write-Host "  lint        - Run linting"
        Write-Host "  format      - Format code"
        Write-Host ""
        Write-Host "Services:" -ForegroundColor Yellow
        Write-Host "  start:api-gateway    - Start API Gateway"
        Write-Host "  start:auth-service   - Start Auth service"
        Write-Host "  start:search-service - Start Search service"
        Write-Host "  start:synthesis-service - Start Synthesis service"
        Write-Host "  start:factcheck-service - Start Fact Check service"
        Write-Host "  start:analytics-service - Start Analytics service"
    }
    
    "install" {
        Write-Host "Installing Node.js dependencies..." -ForegroundColor Green
        npm install
        Write-Host "Installing Python dependencies..." -ForegroundColor Green

        .venv\Scripts\pip install -e .[dev,test,security]
        Write-Host "Installation complete!" -ForegroundColor Green
    }
    
    "setup" {
        Write-Host "Setting up project..." -ForegroundColor Green
        npm install
        .venv\Scripts\pip install -e .[dev,test,security]
        if (!(Test-Path ".env")) {
            Copy-Item ".env.template" ".env"
            Write-Host "Created .env file from template. Please configure your environment variables." -ForegroundColor Yellow
        }
        Write-Host "Setup complete!" -ForegroundColor Green
    }
    
    "dev" {
        Write-Host "Starting development servers..." -ForegroundColor Green
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev:frontend"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev:backend"
    }
    
    "dev:frontend" {
        Write-Host "Starting frontend development server..." -ForegroundColor Green
        npm run dev:frontend
    }
    
    "dev:backend" {
        Write-Host "Starting backend development server..." -ForegroundColor Green
        npm run dev:backend
    }
    
    "test" {
        Write-Host "Running all tests..." -ForegroundColor Green
        npm run test
    }
    
    "test:unit" {
        Write-Host "Running unit tests..." -ForegroundColor Green
        npm run test:unit
    }
    
    "lint" {
        Write-Host "Running linting..." -ForegroundColor Green
        npm run lint
    }
    
    "format" {
        Write-Host "Formatting code..." -ForegroundColor Green
        npm run format
    }
    
    { $_ -like "start:*" } {
        $serviceName = $Command -replace "start:", ""
        Write-Host "Starting $serviceName..." -ForegroundColor Green
        npm run $Command
    }
    
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Run '.\scripts\dev.ps1 help' for available commands" -ForegroundColor Yellow
    }
} 