# SarvanOM Service Management Script
# This script helps manage Docker services efficiently for development

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "clean")]
    [string]$Action = "status"
)

Write-Host "🐳 SarvanOM Service Manager" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

switch ($Action) {
    "start" {
        Write-Host "🚀 Starting essential services..." -ForegroundColor Green
        docker-compose up -d
        Write-Host "✅ Services started successfully!" -ForegroundColor Green
        Write-Host "📊 Available services:" -ForegroundColor Yellow
        Write-Host "   - PostgreSQL (Port 5432)"
        Write-Host "   - Qdrant (Port 6333)" 
        Write-Host "   - Meilisearch (Port 7700)"
        Write-Host ""
        Write-Host "💡 To start backend/frontend services, run:" -ForegroundColor Cyan
        Write-Host "   docker-compose -f docker-compose.dev.yml up -d"
    }
    
    "stop" {
        Write-Host "🛑 Stopping all services..." -ForegroundColor Yellow
        docker-compose down
        docker-compose -f docker-compose.dev.yml down
        Write-Host "✅ All services stopped!" -ForegroundColor Green
    }
    
    "restart" {
        Write-Host "🔄 Restarting services..." -ForegroundColor Yellow
        docker-compose down
        docker-compose up -d
        Write-Host "✅ Services restarted!" -ForegroundColor Green
    }
    
    "status" {
        Write-Host "📊 Service Status:" -ForegroundColor Yellow
        docker-compose ps
        Write-Host ""
        Write-Host "💡 Resource Usage:" -ForegroundColor Cyan
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    }
    
    "logs" {
        Write-Host "📋 Recent logs:" -ForegroundColor Yellow
        docker-compose logs --tail=20
    }
    
    "clean" {
        Write-Host "🧹 Cleaning up Docker resources..." -ForegroundColor Yellow
        docker system prune -f
        docker volume prune -f
        Write-Host "✅ Cleanup completed!" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Cyan
Write-Host "   - Run services locally: python -m services.synthesis.main"
Write-Host "   - Check resource usage: docker stats"
Write-Host "   - View logs: docker-compose logs [service_name]"
Write-Host "   - Stop all: docker-compose down"
