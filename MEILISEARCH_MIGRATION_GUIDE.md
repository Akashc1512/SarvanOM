# 🚀 Meilisearch Migration Guide - Zero-Budget Elasticsearch Alternative

## 📋 Overview

This guide helps you migrate from Elasticsearch to **Meilisearch**, a lightning-fast, zero-budget search engine written in Rust. Meilisearch provides excellent search capabilities with minimal resource usage and zero licensing costs.

## 🎯 Why Meilisearch?

| Feature | Elasticsearch | Meilisearch |
|---------|---------------|-------------|
| **Cost** | Expensive licensing | 100% Free & Open Source |
| **Performance** | Good | Lightning fast (Rust) |
| **Setup** | Complex | Single binary |
| **Resource Usage** | High (Java) | Low (Rust) |
| **API** | Complex REST | Simple REST |
| **Typo Tolerance** | Limited | Excellent |
| **Real-time** | Yes | Yes |

## 🚀 Quick Start

### 1. Start Meilisearch

```bash
# Using Docker (recommended)
docker run -p 7700:7700 getmeili/meilisearch:latest

# Or use our setup script
chmod +x scripts/setup_meilisearch.sh
./scripts/setup_meilisearch.sh
```

### 2. Test the Integration

```bash
# Run the integration test
python test_meilisearch_integration.py
```

### 3. Update Environment Variables

```bash
# Add to your .env file
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_MASTER_KEY=your-master-key-here  # Optional
MEILISEARCH_INDEX=knowledge_base
```

## 🔧 Migration Steps

### Step 1: Install Meilisearch

#### Option A: Docker (Recommended)
```bash
# Pull the image
docker pull getmeili/meilisearch:latest

# Run Meilisearch
docker run -d \
  --name sarvanom-meilisearch \
  -p 7700:7700 \
  -v meilisearch_data:/meili_data \
  getmeili/meilisearch:latest
```

#### Option B: Binary Installation
```bash
# Download Meilisearch binary
curl -L https://install.meilisearch.com | sh

# Start Meilisearch
./meilisearch --http-addr 0.0.0.0:7700
```

### Step 2: Update Your Code

The migration is **seamless** - we've already updated your code to use Meilisearch:

1. **Hybrid Retrieval Engine**: Now uses `MeilisearchEngine` instead of `ElasticsearchEngine`
2. **Same API**: Maintains compatibility with existing `RetrievalSource.ELASTICSEARCH`
3. **Same Results**: Returns the same data structure as before

### Step 3: Update Docker Compose

Replace Elasticsearch with Meilisearch in your `docker-compose.yml`:

```yaml
# Remove this section
# elasticsearch:
#   image: docker.elastic.co/elasticsearch/elasticsearch:8.15.0
#   ...

# Add this section
meilisearch:
  image: getmeili/meilisearch:latest
  container_name: sarvanom-meilisearch
  ports:
    - "7700:7700"
  volumes:
    - meilisearch_data:/meili_data
  restart: unless-stopped
  networks:
    - knowledge-hub-network
```

### Step 4: Update Environment Variables

```bash
# Remove Elasticsearch variables (optional)
# ELASTICSEARCH_URL=
# ELASTICSEARCH_USERNAME=
# ELASTICSEARCH_PASSWORD=

# Add Meilisearch variables
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_MASTER_KEY=your-master-key-here  # Optional
MEILISEARCH_INDEX=knowledge_base
```

## 📊 Performance Comparison

### Resource Usage
- **Elasticsearch**: ~2GB RAM minimum, ~4GB recommended
- **Meilisearch**: ~512MB RAM, scales efficiently

### Search Speed
- **Elasticsearch**: 50-200ms typical
- **Meilisearch**: 10-50ms typical

### Setup Time
- **Elasticsearch**: 10-30 minutes
- **Meilisearch**: 2-5 minutes

## 🔍 API Comparison

### Search Request

**Elasticsearch:**
```json
POST /knowledge_base/_search
{
  "query": {
    "multi_match": {
      "query": "artificial intelligence",
      "fields": ["title^2", "content"]
    }
  },
  "size": 10
}
```

**Meilisearch:**
```json
POST /indexes/knowledge_base/search
{
  "q": "artificial intelligence",
  "limit": 10
}
```

### Add Documents

**Elasticsearch:**
```json
POST /knowledge_base/_doc
{
  "title": "AI Basics",
  "content": "Artificial Intelligence fundamentals...",
  "tags": ["AI", "technology"]
}
```

**Meilisearch:**
```json
POST /indexes/knowledge_base/documents
[
  {
    "id": "1",
    "title": "AI Basics",
    "content": "Artificial Intelligence fundamentals...",
    "tags": ["AI", "technology"]
  }
]
```

## 🛠️ Advanced Configuration

### Index Settings

```python
# Configure searchable attributes
await engine._configure_index()

# This sets up:
# - Searchable: title, content, tags
# - Filterable: tags, created_at
# - Sortable: created_at, updated_at
```

### Custom Scoring

```python
# Meilisearch uses built-in scoring
# You can customize ranking rules:
ranking_rules = [
    "words",
    "typo", 
    "proximity",
    "attribute",
    "sort",
    "exactness"
]
```

## 🔒 Security

### Production Setup

```bash
# Generate a master key
openssl rand -hex 32

# Start with master key
docker run -d \
  --name sarvanom-meilisearch \
  -p 7700:7700 \
  -e MEILI_MASTER_KEY=your-generated-key \
  -v meilisearch_data:/meili_data \
  getmeili/meilisearch:latest
```

### Environment Variables

```bash
# .env file
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_MASTER_KEY=your-generated-key
MEILISEARCH_INDEX=knowledge_base
```

## 📈 Monitoring

### Health Check
```bash
curl http://localhost:7700/health
```

### Index Statistics
```bash
curl http://localhost:7700/indexes/knowledge_base/stats
```

### System Information
```bash
curl http://localhost:7700/version
```

## 🧪 Testing

### Run Integration Tests
```bash
python test_meilisearch_integration.py
```

### Manual Testing
```bash
# Test search
curl -X POST 'http://localhost:7700/indexes/knowledge_base/search' \
  -H 'Content-Type: application/json' \
  -d '{"q": "artificial intelligence"}'
```

## 🔄 Data Migration

### From Elasticsearch to Meilisearch

```python
import asyncio
from elasticsearch import Elasticsearch
from services.search_service.core.meilisearch_engine import MeilisearchEngine, MeilisearchDocument

async def migrate_data():
    # Connect to Elasticsearch
    es = Elasticsearch(['http://localhost:9200'])
    
    # Connect to Meilisearch
    meili = MeilisearchEngine()
    
    # Get all documents from Elasticsearch
    response = es.search(
        index="knowledge_base",
        body={"query": {"match_all": {}}, "size": 1000}
    )
    
    # Convert to Meilisearch format
    documents = []
    for hit in response['hits']['hits']:
        doc = MeilisearchDocument(
            id=hit['_id'],
            title=hit['_source'].get('title', ''),
            content=hit['_source'].get('content', ''),
            tags=hit['_source'].get('tags', [])
        )
        documents.append(doc)
    
    # Add to Meilisearch
    await meili.add_documents(documents)
    print(f"Migrated {len(documents)} documents")

# Run migration
asyncio.run(migrate_data())
```

## 🚨 Troubleshooting

### Common Issues

1. **Meilisearch not starting**
   ```bash
   # Check logs
   docker logs sarvanom-meilisearch
   
   # Check if port is available
   netstat -an | grep 7700
   ```

2. **Connection refused**
   ```bash
   # Ensure Meilisearch is running
   curl http://localhost:7700/health
   
   # Check Docker container
   docker ps | grep meilisearch
   ```

3. **Search not working**
   ```bash
   # Check if index exists
   curl http://localhost:7700/indexes
   
   # Check index settings
   curl http://localhost:7700/indexes/knowledge_base/settings
   ```

### Performance Issues

1. **Slow searches**: Check if index is properly configured
2. **High memory usage**: Monitor with `docker stats`
3. **No results**: Verify documents are indexed correctly

## 📚 Additional Resources

- [Meilisearch Documentation](https://docs.meilisearch.com/)
- [Meilisearch GitHub](https://github.com/meilisearch/meilisearch)
- [REST API Reference](https://docs.meilisearch.com/reference/api/)
- [Community Discord](https://discord.gg/meilisearch)

## ✅ Migration Checklist

- [ ] Install Meilisearch
- [ ] Update environment variables
- [ ] Test basic functionality
- [ ] Run integration tests
- [ ] Update Docker Compose
- [ ] Migrate existing data (if any)
- [ ] Update monitoring/alerting
- [ ] Remove Elasticsearch dependencies
- [ ] Update documentation
- [ ] Deploy to production

## 🎉 Benefits After Migration

1. **Zero Licensing Costs**: 100% free and open source
2. **Better Performance**: Faster search results
3. **Lower Resource Usage**: Less memory and CPU
4. **Simpler Setup**: Single binary installation
5. **Better Typo Tolerance**: More forgiving search
6. **Real-time Updates**: Instant index updates

---

**🎯 Result**: You now have a powerful, free search engine that's faster and more efficient than Elasticsearch! 