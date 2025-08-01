#!/bin/bash
# Setup Meilisearch - Zero-budget Elasticsearch alternative
# Created: January 2025

echo "🔍 Setting up Meilisearch (Elasticsearch alternative)..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Pull and run Meilisearch
echo "📦 Pulling Meilisearch Docker image..."
docker pull getmeili/meilisearch:latest

echo "🚀 Starting Meilisearch..."
docker run -d \
  --name sarvanom-meilisearch \
  -p 7700:7700 \
  -v meilisearch_data:/meili_data \
  getmeili/meilisearch:latest

echo "⏳ Waiting for Meilisearch to start..."
sleep 5

# Test connection
if curl -s http://localhost:7700/health > /dev/null; then
    echo "✅ Meilisearch is running at http://localhost:7700"
    echo ""
    echo "📝 Update your .env file:"
    echo "   MEILISEARCH_URL=http://localhost:7700"
    echo "   MEILISEARCH_MASTER_KEY=your-master-key-here  # Optional"
    echo ""
    echo "🔧 Available endpoints:"
    echo "   - Health: http://localhost:7700/health"
    echo "   - Indexes: http://localhost:7700/indexes"
    echo "   - Search: POST http://localhost:7700/indexes/knowledge_base/search"
    echo ""
    echo "📚 Quick start:"
    echo "   1. Create index: curl -X POST 'http://localhost:7700/indexes' -H 'Content-Type: application/json' -d '{\"uid\": \"knowledge_base\", \"primaryKey\": \"id\"}'"
    echo "   2. Add documents: curl -X POST 'http://localhost:7700/indexes/knowledge_base/documents' -H 'Content-Type: application/json' -d '[{\"id\": \"1\", \"title\": \"Sample\", \"content\": \"Sample content\"}]'"
    echo "   3. Search: curl -X POST 'http://localhost:7700/indexes/knowledge_base/search' -H 'Content-Type: application/json' -d '{\"q\": \"sample\"}'"
else
    echo "❌ Failed to connect to Meilisearch"
    echo "💡 Try running: docker logs sarvanom-meilisearch"
fi

echo ""
echo "🎉 Meilisearch setup complete!"
echo "💡 To stop: docker stop sarvanom-meilisearch"
echo "💡 To remove: docker rm sarvanom-meilisearch" 