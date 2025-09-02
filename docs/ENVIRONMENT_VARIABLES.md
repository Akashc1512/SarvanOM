# 🔧 Environment Variables Configuration

This document provides comprehensive configuration for all environment variables used in SarvanOM.

## 🏗️ **Phase I1: ArangoDB Configuration (NEW)**

### **ArangoDB Connection Settings**
```bash
# ArangoDB Knowledge Graph Database
ARANGODB_URL=http://localhost:8529          # ArangoDB server URL
ARANGODB_USERNAME=root                       # ArangoDB username
ARANGODB_PASSWORD=                           # ArangoDB password (empty for local dev)
ARANGODB_DATABASE=sarvanom_kg               # ArangoDB database name

# ArangoDB Performance Settings  
ARANGODB_CONNECTION_TIMEOUT=10              # Connection timeout in seconds
ARANGODB_QUERY_TIMEOUT=30                   # Query timeout in seconds
ARANGODB_MAX_CONNECTIONS=10                 # Maximum connection pool size
```

### **Production ArangoDB Settings**
```bash
# For production environments
ARANGODB_URL=http://your-arangodb-server:8529
ARANGODB_USERNAME=sarvanom_user
ARANGODB_PASSWORD=your_secure_password_here
ARANGODB_DATABASE=sarvanom_production_kg
ARANGODB_CONNECTION_TIMEOUT=5
ARANGODB_QUERY_TIMEOUT=15
ARANGODB_MAX_CONNECTIONS=20
```

## 🤖 **LLM Provider Configuration (Phases B1-B2)**

### **Provider Order System**
```bash
# Centralized provider order (free-first by default)
LLM_PROVIDER_ORDER=ollama,huggingface,openai,anthropic,local_stub

# Zero-budget optimization
PRIORITIZE_FREE_MODELS=true
USE_DYNAMIC_SELECTION=true
```

### **Role-Based Model Selection**
```bash
# Format: "provider:model" - multiple providers with commas
LLM_FAST=ollama:llama3:8b,openai:gpt-4o-mini
LLM_QUALITY=anthropic:claude-3-5-sonnet,openai:gpt-4o  
LLM_LONG=anthropic:claude-3-opus,openai:gpt-4o
LLM_REASONING=anthropic:claude-3-opus,openai:o1-preview
LLM_TOOL=openai:gpt-4o,anthropic:claude-3-5-sonnet
```

### **Enhanced Router Configuration (Phase I3)**
```bash
# Policy-based routing
PRIORITIZE_FREE_MODELS=true
AUTO_ESCALATE_COMPLEXITY=true
CIRCUIT_BREAKER_ENABLED=true

# Budget caps and rate limiting
OPENAI_MAX_RPM=500              # Requests per minute
OPENAI_MAX_TPM=10000           # Tokens per minute
ANTHROPIC_MAX_RPM=200          # Requests per minute  
ANTHROPIC_MAX_TPM=8000         # Tokens per minute
HUGGINGFACE_MAX_RPM=100        # Free tier limit
OLLAMA_MAX_RPM=1000            # Local - no real limit

# Circuit breaker settings
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT_SECONDS=60

# Router telemetry
ROUTING_TELEMETRY_ENABLED=true
TELEMETRY_BUFFER_SIZE=1000
```

### **LLM Provider Credentials**
```bash
# Free/Local Providers (Recommended)
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3
OLLAMA_TIMEOUT=30

HUGGINGFACE_WRITE_TOKEN=your_huggingface_token_here

# Paid Providers (Fallback Only)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## 🗄️ **Database Configuration**

### **Primary Database**
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/sarvanom_db
```

### **Redis Cache**
```bash
REDIS_URL=redis://localhost:6379/0
```

### **Vector Database**
```bash
# Qdrant (Production)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_COLLECTION_NAME=sarvanom_embeddings

# Chroma (Development)
CHROMA_DB_PATH=./data/chroma
CHROMA_COLLECTION_NAME=sarvanom_dev

# Vector DB Settings
VECTOR_DB_PROVIDER=qdrant
USE_VECTOR_DB=true
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```

### **Search Engine**
```bash
# Meilisearch
MEILISEARCH_URL=http://localhost:7700
MEILI_MASTER_KEY=your_meilisearch_master_key_here
MEILISEARCH_INDEX=sarvanom_documents
```

## 🌐 **Application Settings**

### **Core Settings**
```bash
NODE_ENV=development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
STRUCTURED_LOGGING=true
```

### **Security**
```bash
SECRET_KEY=your_secret_key_here_change_in_production
JWT_SECRET=your_jwt_secret_here_change_in_production
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### **Performance**
```bash
STREAM_MAX_SECONDS=60
MAX_REQUEST_SIZE=10485760
MAX_QUERY_LENGTH=1000
RATE_LIMIT_PER_MINUTE=1000
```

## 📊 **Monitoring & Observability**

### **OpenTelemetry**
```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_SERVICE_NAME=sarvanom
```

### **Prometheus**
```bash
PROMETHEUS_PORT=9090
```

### **Connection Pooling**
```bash
CONNECTION_POOL_SIZE=10
CONNECTION_POOL_TIMEOUT=30.0
MAX_KEEPALIVE_TIME=300
```

### **Circuit Breakers**
```bash
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60
```

## 🔍 **Web Search Configuration**

```bash
# Free Sources (Recommended)
BRAVE_SEARCH_API_KEY=your_brave_search_api_key_here

# Paid Fallback
SERPAPI_KEY=your_serpapi_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here
```

## 🎨 **Frontend Configuration**

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development
NEXT_PUBLIC_APP_NAME=SarvanOM
```

## 🧪 **Development & Testing**

### **Feature Flags**
```bash
ENABLE_VECTOR_SEARCH=true
ENABLE_KNOWLEDGE_GRAPH=true
ENABLE_WEB_SEARCH=true
ENABLE_FACT_CHECKING=true
ENABLE_REAL_TIME_COLLABORATION=false
```

### **Development Settings**
```bash
TESTING=false
BACKUP_ENABLED=false
AUDIT_LOG_ENABLED=true
SECURITY_HEADERS_ENABLED=false
MOCK_AI_RESPONSES=false
SKIP_AUTHENTICATION=true
ENABLE_DEBUG_ENDPOINTS=true
AUTO_RELOAD=true
TEST_MODE=false
MOCK_PROVIDERS=false
```

## 🐳 **Docker Compose Overrides**

For Docker Compose deployments, override these variables:

```bash
# Service URLs for Docker
OLLAMA_BASE_URL=http://sarvanom-ollama:11434
QDRANT_URL=http://sarvanom-qdrant:6333
MEILISEARCH_URL=http://sarvanom-meilisearch:7700
ARANGODB_URL=http://sarvanom-arangodb:8529
DATABASE_URL=postgresql://postgres:password@sarvanom-postgres:5432/sarvanom_db
REDIS_URL=redis://sarvanom-redis:6379/0
```

## 🔒 **Production Security Checklist**

When deploying to production, ensure:

1. ✅ Generate strong `SECRET_KEY` and `JWT_SECRET` values
2. ✅ Set proper `ARANGODB_PASSWORD` 
3. ✅ Configure all API keys for LLM providers
4. ✅ Set `ENVIRONMENT=production`
5. ✅ Set `DEBUG=false`
6. ✅ Configure proper `CORS_ORIGINS`
7. ✅ Enable `SECURITY_HEADERS_ENABLED=true`
8. ✅ Set `SKIP_AUTHENTICATION=false`
9. ✅ Configure proper `DATABASE_URL` and `REDIS_URL`
10. ✅ Set up monitoring with proper `OTEL_EXPORTER_OTLP_ENDPOINT`

## 📋 **Quick Start Template**

Copy this template to your `.env` file:

```bash
# Core
NODE_ENV=development
DEBUG=true
SECRET_KEY=dev_secret_key_change_in_production
JWT_SECRET=dev_jwt_secret_change_in_production

# ArangoDB (Phase I1)
ARANGODB_URL=http://localhost:8529
ARANGODB_USERNAME=root
ARANGODB_PASSWORD=
ARANGODB_DATABASE=sarvanom_kg

# LLM Providers (Phases B1-B2)
LLM_PROVIDER_ORDER=ollama,huggingface,openai,anthropic,local_stub
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
PRIORITIZE_FREE_MODELS=true

# Databases
DATABASE_URL=postgresql://postgres:password@localhost:5432/sarvanom_db
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
MEILISEARCH_URL=http://localhost:7700

# Add your API keys here (optional for zero-budget mode)
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here
# HUGGINGFACE_WRITE_TOKEN=your_token_here
```

---

**Note**: This configuration supports the zero-budget optimization strategy where the system works without paid API keys while gracefully upgrading when premium providers are available.
