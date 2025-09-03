# 🔧 **SarvanOM Environment Variables Reference**

## 📋 **OVERVIEW**

This document provides a comprehensive reference for all environment variables used in the SarvanOM platform. Variables are organized by service category and include default values, validation requirements, and production considerations.

**Environment File**: All variables should be defined in the root `.env` file.

---

## 🚨 **CRITICAL PRODUCTION VARIABLES** 

### **ArangoDB Configuration (Phase I1 - BLOCKING)**

These variables are **REQUIRED** for Knowledge Graph functionality. Missing or incorrect values will cause 401 authentication errors.

```bash
# ArangoDB Connection (REQUIRED)
ARANGODB_URL=http://localhost:8529                    # ArangoDB server URL
ARANGODB_USERNAME=root                                # Database username  
ARANGODB_PASSWORD=your_secure_password_here           # Database password
ARANGODB_DATABASE=sarvanom_kg                         # Database name

# ArangoDB Performance Tuning (OPTIONAL)
ARANGODB_CONNECTION_TIMEOUT=10                        # Connection timeout (seconds)
ARANGODB_PROBE_TIMEOUT=0.3                           # Health probe timeout (seconds)
ARANGODB_WARMUP_ENABLED=true                         # Enable background warmup
```

**Validation Requirements**:
- `ARANGODB_URL`: Must be valid HTTP/HTTPS URL
- `ARANGODB_PASSWORD`: Required for production (no empty passwords)
- `ARANGODB_DATABASE`: Must contain only alphanumeric characters and underscores

### **Vector Database Configuration (Phase I2 - BLOCKING)**

These variables control vector search performance and cold-start elimination.

```bash
# Primary Vector Database (Production)
QDRANT_URL=http://localhost:6333                      # Qdrant server URL
QDRANT_API_KEY=                                       # Qdrant API key (if required)
VECTOR_COLLECTION_NAME=sarvanom_embeddings            # Collection name

# Development Vector Database (Alternative)
VECTOR_DB_PROVIDER=qdrant                             # Options: qdrant, chroma
CHROMA_PERSIST_DIRECTORY=./chroma_db                  # Chroma storage path

# Vector Performance Tuning (Phase I2)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2  # Embedding model
EMBEDDING_CACHE_SIZE=1000                             # LRU cache size
EMBEDDING_CACHE_TTL=3600                              # Cache TTL (seconds)
VECTOR_WARMUP_ENABLED=true                            # Enable startup warmup
```

---

## 🤖 **LLM PROVIDER CONFIGURATION**

### **Primary LLM Providers**

```bash
# OpenAI (GPT Models)
OPENAI_API_KEY=sk-your_openai_key_here                # OpenAI API key
OPENAI_MAX_RPM=500                                    # Requests per minute limit
OPENAI_MAX_TPM=90000                                  # Tokens per minute limit

# Anthropic (Claude Models) 
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here      # Anthropic API key
ANTHROPIC_MAX_RPM=100                                 # Requests per minute limit
ANTHROPIC_MAX_TPM=40000                               # Tokens per minute limit

# Local/Free Providers
OLLAMA_BASE_URL=http://localhost:11434                # Ollama server URL
HUGGINGFACE_API_TOKEN=hf_your_token_here              # HuggingFace API token
```

### **LLM Routing Configuration**

```bash
# Provider Selection Policy
PRIORITIZE_FREE_MODELS=true                           # Free-first routing
USE_DYNAMIC_SELECTION=true                            # Complexity-based routing

# Role-Based Model Assignment
LLM_FAST=ollama:llama3:8b                            # Fast responses
LLM_QUALITY=anthropic:claude-3-5-sonnet             # High-quality outputs
LLM_LONG=openai:gpt-4o                               # Large context
LLM_REASONING=openai:o1-preview                      # Complex reasoning
LLM_TOOL=openai:gpt-4o                               # Function calling

# Circuit Breaker Configuration
CIRCUIT_BREAKER_ENABLED=true                          # Enable circuit breakers
CIRCUIT_FAILURE_THRESHOLD=5                          # Failures before opening
CIRCUIT_TIMEOUT=60                                    # Recovery timeout (seconds)
```

---

## 🔍 **SEARCH & RETRIEVAL CONFIGURATION**

### **Meilisearch (Keyword Search)**

```bash
# Meilisearch Connection
MEILI_URL=http://localhost:7700                       # Meilisearch server URL
MEILI_MASTER_KEY=your_meilisearch_master_key          # Master key for authentication

# Search Performance
SEARCH_RESULTS_LIMIT=20                              # Default result limit
SEARCH_TIMEOUT=5000                                  # Search timeout (ms)
```

### **External Search APIs**

```bash
# Free-Tier Search APIs (Zero-Budget)
BRAVE_SEARCH_API_KEY=                                # Brave Search API (optional)
SERPAPI_API_KEY=                                     # SerpAPI key (optional)

# Search Rate Limiting
SEARCH_RATE_LIMIT_RPM=60                             # Requests per minute
SEARCH_RATE_LIMIT_BURST=10                          # Burst allowance
```

---

## 🔐 **SECURITY & PERFORMANCE**

### **Security Configuration**

```bash
# Rate Limiting
RATE_LIMIT_RPM=60                                    # Global rate limit (per IP)
RATE_LIMIT_BURST=10                                  # Burst allowance

# Security Headers
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
TRUSTED_HOSTS=localhost,127.0.0.1,yourdomain.com
CSP_POLICY=default-src 'self'                        # Content Security Policy

# Input Validation
MAX_QUERY_LENGTH=2000                                # Maximum query length
MAX_UPLOAD_SIZE=50MB                                 # File upload limit
```

### **Performance & Monitoring**

```bash
# Performance Budgets (Phase E2)
MAX_RESPONSE_TIME_S=3                                # E2E response time budget
MAX_VECTOR_TIME_S=2                                  # Vector search budget  
MAX_KG_TIME_S=1.5                                   # Knowledge graph budget

# Telemetry & Observability
ROUTING_TELEMETRY_ENABLED=true                       # Enable router metrics
PERFORMANCE_LOGGING_ENABLED=true                     # Enable perf logging
STRUCTURED_LOGGING=true                              # Use structured logs

# Health Check Configuration
HEALTH_CHECK_INTERVAL=30                             # Health check interval (seconds)
STARTUP_TIMEOUT=60                                   # Startup timeout (seconds)
```

---

## 📊 **OPTIONAL SERVICE CONFIGURATION**

### **Development & Testing**

```bash
# Environment Mode
NODE_ENV=development                                  # Environment mode
DEBUG=true                                           # Enable debug mode
TESTING=false                                        # Testing mode flag

# Development Tools
HOT_RELOAD=true                                      # Enable hot reload
MOCK_EXTERNAL_APIS=false                             # Mock external services
DEV_CORS_ENABLED=true                                # Development CORS
```

### **Background Processing**

```bash
# Task Queue Configuration
CELERY_BROKER_URL=redis://localhost:6379/0          # Celery broker URL
TASK_QUEUE_ENABLED=true                              # Enable background tasks
MAX_WORKER_THREADS=4                                 # Worker thread limit
```

### **Caching**

```bash
# Redis Cache (Optional)
REDIS_URL=redis://localhost:6379/1                   # Redis cache URL
CACHE_TTL=3600                                       # Default cache TTL
CACHE_MAX_SIZE=1000                                  # Max cache entries

# In-Memory Cache
MEMORY_CACHE_ENABLED=true                            # Enable memory cache
MEMORY_CACHE_SIZE=500                                # Memory cache size
```

---

## ✅ **VALIDATION & VERIFICATION**

### **Environment Variable Checklist**

Use this checklist to verify your environment configuration:

#### **🚨 Critical (Production Blocking)**
- [ ] `ARANGODB_URL` - Valid URL, server accessible
- [ ] `ARANGODB_USERNAME` - Valid database user
- [ ] `ARANGODB_PASSWORD` - Non-empty, secure password
- [ ] `ARANGODB_DATABASE` - Database exists or can be created
- [ ] `VECTOR_DB_PROVIDER` - Set to `qdrant` for production
- [ ] `QDRANT_URL` - Qdrant server accessible

#### **🤖 LLM Integration**
- [ ] At least one LLM provider key configured
- [ ] `OLLAMA_BASE_URL` - Ollama server running (for free-first routing)
- [ ] Provider rate limits appropriate for usage

#### **🔍 Search Services**
- [ ] `MEILI_MASTER_KEY` - Meilisearch authentication
- [ ] Search APIs configured (optional but recommended)

#### **🔐 Security**
- [ ] `RATE_LIMIT_RPM` - Appropriate for expected traffic
- [ ] `CORS_ALLOWED_ORIGINS` - Only trusted domains
- [ ] `TRUSTED_HOSTS` - Only trusted hosts

### **Environment Validation Commands**

```bash
# Check critical environment variables
python -c "
import os
critical_vars = ['ARANGODB_URL', 'ARANGODB_PASSWORD', 'VECTOR_DB_PROVIDER']
missing = [var for var in critical_vars if not os.getenv(var)]
if missing:
    print(f'❌ Missing critical variables: {missing}')
else:
    print('✅ All critical variables configured')
"

# Test ArangoDB connection
python -c "
from shared.core.services.arangodb_service import get_arangodb_health
import asyncio
result = asyncio.run(get_arangodb_health())
print(f'ArangoDB Status: {result.get(\"status\", \"unknown\")}')
"
```

---

## 🚨 **TROUBLESHOOTING**

### **Common Environment Issues**

| **Issue** | **Symptoms** | **Solution** |
|-----------|--------------|--------------|
| ArangoDB 401 Errors | KG queries fail with authentication error | Verify `ARANGODB_PASSWORD` is correct |
| Vector Cold Start | First vector query >5s | Enable `VECTOR_WARMUP_ENABLED=true` |
| LLM Provider Errors | No LLM responses | Check API keys and rate limits |
| Health Check Failures | `/health` returns unhealthy | Verify service URLs and credentials |

### **Phase I1 Specific Checks**

```bash
# Verify ArangoDB environment variables
echo "ARANGODB_URL: ${ARANGODB_URL}"
echo "ARANGODB_USERNAME: ${ARANGODB_USERNAME}"  
echo "ARANGODB_PASSWORD: [REDACTED]"
echo "ARANGODB_DATABASE: ${ARANGODB_DATABASE}"

# Test ArangoDB connection
curl -X GET "${ARANGODB_URL}/_api/version" \
  -u "${ARANGODB_USERNAME}:${ARANGODB_PASSWORD}"
```

---

## 📝 **ENVIRONMENT FILE TEMPLATE**

Copy this template to create your `.env` file:

```bash
# ===============================================
# SarvanOM Environment Configuration
# ===============================================

# Phase I1: ArangoDB (CRITICAL)
ARANGODB_URL=http://localhost:8529
ARANGODB_USERNAME=root
ARANGODB_PASSWORD=your_secure_password_here
ARANGODB_DATABASE=sarvanom_kg
ARANGODB_WARMUP_ENABLED=true

# Phase I2: Vector Database (CRITICAL)  
VECTOR_DB_PROVIDER=qdrant
QDRANT_URL=http://localhost:6333
EMBEDDING_CACHE_SIZE=1000
VECTOR_WARMUP_ENABLED=true

# LLM Providers (Choose your providers)
OPENAI_API_KEY=sk-your_openai_key_here
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here
OLLAMA_BASE_URL=http://localhost:11434
HUGGINGFACE_API_TOKEN=hf_your_token_here

# Search Services
MEILI_URL=http://localhost:7700
MEILI_MASTER_KEY=your_meilisearch_master_key

# Free-First Routing
PRIORITIZE_FREE_MODELS=true
USE_DYNAMIC_SELECTION=true

# Security
RATE_LIMIT_RPM=60
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Performance
CIRCUIT_BREAKER_ENABLED=true
ROUTING_TELEMETRY_ENABLED=true
```

---

**Last Updated**: Current Session  
**Document Version**: 1.0 - Phase I1 Production Readiness  
**Next Update**: Phase I2 - Vector Database Configuration