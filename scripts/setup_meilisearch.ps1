# Setup Meilisearch - Zero-budget Elasticsearch alternative for Windows
# Created: January 2025

Write-Host "🔍 Setting up Meilisearch (Elasticsearch alternative)..." -ForegroundColor Green

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    Write-Host "   Visit: https://docs.docker.com/desktop/install/windows-install/" -ForegroundColor Yellow
    exit 1
}

# Check if Docker is running
try {
    docker ps | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Stop existing container if running
Write-Host "🛑 Stopping existing Meilisearch container..." -ForegroundColor Yellow
docker stop sarvanom-meilisearch 2>$null
docker rm sarvanom-meilisearch 2>$null

# Pull Meilisearch image
Write-Host "📦 Pulling Meilisearch Docker image..." -ForegroundColor Yellow
docker pull getmeili/meilisearch:latest

# Start Meilisearch
Write-Host "🚀 Starting Meilisearch..." -ForegroundColor Yellow
docker run -d `
  --name sarvanom-meilisearch `
  -p 7700:7700 `
  -v meilisearch_data:/meili_data `
  getmeili/meilisearch:latest

# Wait for Meilisearch to start
Write-Host "⏳ Waiting for Meilisearch to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test connection
try {
    $response = Invoke-RestMethod -Uri "http://localhost:7700/health" -Method Get -TimeoutSec 10
    Write-Host "✅ Meilisearch is running at http://localhost:7700" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Update your .env file:" -ForegroundColor Cyan
    Write-Host "   MEILISEARCH_URL=http://localhost:7700" -ForegroundColor White
    Write-Host "   MEILISEARCH_MASTER_KEY=your-master-key-here  # Optional" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Available endpoints:" -ForegroundColor Cyan
    Write-Host "   - Health: http://localhost:7700/health" -ForegroundColor White
    Write-Host "   - Indexes: http://localhost:7700/indexes" -ForegroundColor White
    Write-Host "   - Search: POST http://localhost:7700/indexes/knowledge_base/search" -ForegroundColor White
    Write-Host ""
    Write-Host "📚 Quick start with PowerShell:" -ForegroundColor Cyan
    Write-Host "   1. Create index:" -ForegroundColor White
    Write-Host "      Invoke-RestMethod -Uri 'http://localhost:7700/indexes' -Method Post -ContentType 'application/json' -Body '{\"uid\": \"knowledge_base\", \"primaryKey\": \"id\"}'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   2. Add documents:" -ForegroundColor White
    Write-Host "      Invoke-RestMethod -Uri 'http://localhost:7700/indexes/knowledge_base/documents' -Method Post -ContentType 'application/json' -Body '[{\"id\": \"1\", \"title\": \"Sample\", \"content\": \"Sample content\"}]'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   3. Search:" -ForegroundColor White
    Write-Host "      Invoke-RestMethod -Uri 'http://localhost:7700/indexes/knowledge_base/search' -Method Post -ContentType 'application/json' -Body '{\"q\": \"sample\"}'" -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed to connect to Meilisearch" -ForegroundColor Red
    Write-Host "💡 Try running: docker logs sarvanom-meilisearch" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Meilisearch setup complete!" -ForegroundColor Green
Write-Host "💡 To stop: docker stop sarvanom-meilisearch" -ForegroundColor Cyan
Write-Host "💡 To remove: docker rm sarvanom-meilisearch" -ForegroundColor Cyan
Write-Host ""
Write-Host "🧪 Run the integration test:" -ForegroundColor Cyan
Write-Host "   python test_meilisearch_integration.py" -ForegroundColor White 