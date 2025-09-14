# Environment Variables Inventory

**Date**: September 9, 2025  
**Status**: ✅ **UPDATED FOR PR-1** - Centralized provider configuration implemented  
**Source**: Centralized configuration system in `sarvanom/shared/core/config/provider_config.py`

---

## 📋 **Centralized Provider Configuration (PR-1 Implementation)**

### **AI Provider Configuration**
| Variable | Status | Description | Required | Implementation |
|----------|--------|-------------|----------|----------------|
| `OPENAI_API_KEY` | ✅ **CANONICAL** | OpenAI API key for GPT models | Yes | Centralized config |
| `ANTHROPIC_API_KEY` | ✅ **CANONICAL** | Anthropic API key for Claude models | Yes | Centralized config |
| `HUGGINGFACE_API_KEY` | ✅ **CANONICAL** | HuggingFace API key (general) | No | Centralized config |
| `HUGGINGFACE_READ_TOKEN` | ✅ **CANONICAL** | HuggingFace read/inference token | No | Centralized config |
| `HUGGINGFACE_WRITE_TOKEN` | ✅ **CANONICAL** | HuggingFace write/publish token | No | Centralized config |
| `GEMINI_API_KEY` | ✅ **CANONICAL** | Google Gemini API key for vision/LMM | No | Centralized config |
| `OLLAMA_BASE_URL` | ✅ **CANONICAL** | Ollama local server URL | No | Service-specific config |

### **Search & Retrieval Providers**
| Variable | Status | Description | Required | Implementation |
|----------|--------|-------------|----------|----------------|
| `BRAVE_SEARCH_API_KEY` | ✅ **CANONICAL** | Brave Search API key (preferred) | Yes* | Centralized config |
| `SERPAPI_KEY` | ✅ **CANONICAL** | SerpAPI key (fallback) | Yes* | Centralized config |
| `GUARDIAN_OPEN_PLATFORM_KEY` | ✅ **CANONICAL** | Guardian Open Platform API key | Yes* | Centralized config |
| `NEWSAPI_KEY` | ✅ **CANONICAL** | NewsAPI key (fallback) | Yes* | Centralized config |
| `ALPHAVANTAGE_KEY` | ✅ **CANONICAL** | Alpha Vantage API key (preferred) | Yes* | Centralized config |
| `FINNHUB_KEY` | ✅ **CANONICAL** | Finnhub API key (optional) | No | Centralized config |
| `FMP_API_KEY` | ✅ **CANONICAL** | Financial Modeling Prep API key | No | Centralized config |
| `YOUTUBE_API_KEY` | ✅ **CANONICAL** | YouTube Data API key | No | Centralized config |

### **Feature Flags**
| Variable | Status | Description | Required | Implementation |
|----------|--------|-------------|----------|----------------|
| `KEYLESS_FALLBACKS_ENABLED` | ✅ **CANONICAL** | Enable keyless fallbacks for providers | No (default: true) | Centralized config |

### **Database Configuration**
| Variable | Status | Description | Required |
|----------|--------|-------------|----------|
| `DATABASE_URL` | ✅ **EXISTS** | Primary database connection string | Yes |
| `REDIS_URL` | ✅ **EXISTS** | Redis cache connection string | Yes |
| `VECTOR_DB_URL` | ✅ **EXISTS** | Qdrant vector database URL | Yes |
| `VECTOR_DB_API_KEY` | ✅ **EXISTS** | Qdrant API key (optional for local) | No |

### **Search & Knowledge Graph**
| Variable | Status | Description | Required |
|----------|--------|-------------|----------|
| `MEILISEARCH_URL` | ✅ **EXISTS** | Meilisearch server URL | Yes |
| `MEILISEARCH_MASTER_KEY` | ✅ **EXISTS** | Meilisearch master key | Yes |
| `ARANGODB_URL` | ✅ **EXISTS** | ArangoDB server URL | Yes |
| `ARANGODB_USERNAME` | ✅ **EXISTS** | ArangoDB username | Yes |
| `ARANGODB_PASSWORD` | ✅ **EXISTS** | ArangoDB password | Yes |
| `ARANGODB_DATABASE` | ✅ **EXISTS** | ArangoDB database name | Yes |

### **Security & Authentication**
| Variable | Status | Description | Required |
|----------|--------|-------------|----------|
| `JWT_SECRET_KEY` | ✅ **EXISTS** | JWT signing secret | Yes |
| `AUTH_SERVICE_SECRET` | ✅ **EXISTS** | Auth service secret | Yes |
| `SEARCH_SERVICE_SECRET` | ✅ **EXISTS** | Search service secret | Yes |
| `SYNTHESIS_SERVICE_SECRET` | ✅ **EXISTS** | Synthesis service secret | Yes |
| `FACTCHECK_SERVICE_SECRET` | ✅ **EXISTS** | Fact-check service secret | Yes |
| `ANALYTICS_SERVICE_SECRET` | ✅ **EXISTS** | Analytics service secret | Yes |

### **Service URLs**
| Variable | Status | Description | Required |
|----------|--------|-------------|----------|
| `AUTH_SERVICE_URL` | ✅ **EXISTS** | Auth service endpoint | Yes |
| `SEARCH_SERVICE_URL` | ✅ **EXISTS** | Search service endpoint | Yes |
| `SYNTHESIS_SERVICE_URL` | ✅ **EXISTS** | Synthesis service endpoint | Yes |
| `FACTCHECK_SERVICE_URL` | ✅ **EXISTS** | Fact-check service endpoint | Yes |
| `ANALYTICS_SERVICE_URL` | ✅ **EXISTS** | Analytics service endpoint | Yes |

### **Monitoring & Observability**
| Variable | Status | Description | Required |
|----------|--------|-------------|----------|
| `SENTRY_DSN` | ✅ **EXISTS** | Sentry error tracking DSN | No |
| `JAEGER_AGENT_HOST` | ✅ **EXISTS** | Jaeger tracing agent host | No |
| `JAEGER_AGENT_PORT` | ✅ **EXISTS** | Jaeger tracing agent port | No |

---

## 🔍 **Environment Variables from v2 Documentation (03_env_contract.md)**

### **Known Keys (From v1 Logs)**
| Variable | Status | Description | Notes |
|----------|--------|-------------|-------|
| `HUGGINGFACE_API_TOKEN` | ✅ **CONFIRMED** | HuggingFace API token | Matches current config |
| `OLLAMA_BASE_URL` | ✅ **CONFIRMED** | Ollama base URL | Matches current config |
| `MEILI_MASTER_KEY` | ⚠️ **ALIAS** | Meilisearch master key | Should be `MEILISEARCH_MASTER_KEY` |
| `ARANGODB_URL` | ✅ **CONFIRMED** | ArangoDB URL | Matches current config |
| `ARANGODB_USERNAME` | ✅ **CONFIRMED** | ArangoDB username | Matches current config |
| `ARANGODB_PASSWORD` | ✅ **CONFIRMED** | ArangoDB password | Matches current config |
| `ARANGODB_DATABASE` | ✅ **CONFIRMED** | ArangoDB database | Matches current config |
| `QDRANT_URL` | ⚠️ **ALIAS** | Qdrant URL | Should be `VECTOR_DB_URL` |
| `QDRANT_API_KEY` | ⚠️ **ALIAS** | Qdrant API key | Should be `VECTOR_DB_API_KEY` |
| `VECTOR_COLLECTION_NAME` | ✅ **EXISTS** | Vector collection name | Present in config |

### **SLA/Budget Related (From v1)**
| Variable | Status | Description | Notes |
|----------|--------|-------------|-------|
| `SLA_GLOBAL_MS` | ❌ **MISSING** | Global SLA timeout | Need to add for v2 |
| `SLA_ORCHESTRATOR_RESERVE_MS` | ❌ **MISSING** | Orchestrator reserve time | Need to add for v2 |
| `SLA_LLM_MS` | ❌ **MISSING** | LLM processing timeout | Need to add for v2 |
| `SLA_WEB_MS` | ❌ **MISSING** | Web retrieval timeout | Need to add for v2 |
| `SLA_VECTOR_MS` | ❌ **MISSING** | Vector search timeout | Need to add for v2 |
| `SLA_KG_MS` | ❌ **MISSING** | Knowledge graph timeout | Need to add for v2 |
| `SLA_YT_MS` | ❌ **MISSING** | YouTube processing timeout | Need to add for v2 |
| `SLA_TTFT_MAX_MS` | ❌ **MISSING** | Time to first token max | Need to add for v2 |
| `MODE_DEFAULT` | ❌ **MISSING** | Default query mode | Need to add for v2 |
| `GLOBAL_SEARCH_TIMEOUT_MS` | ❌ **MISSING** | Global search timeout | Need to add for v2 |

---

## 🆕 **New v2 Keys (To Be Added)**

### **Model Orchestration**
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MODEL_AUTO_UPGRADE_ENABLED` | Enable auto model upgrades | `true` | No |
| `MODEL_DISCOVERY_CRON` | Model discovery schedule | `weekly` | No |

### **Lane Budgets (v2 SLOs)**
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LANE_BUDGET_SIMPLE_MS` | Simple query budget | `5000` | No |
| `LANE_BUDGET_TECHNICAL_MS` | Technical query budget | `7000` | No |
| `LANE_BUDGET_RESEARCH_MS` | Research query budget | `10000` | No |
| `LANE_BUDGET_MULTIMEDIA_MS` | Multimedia query budget | `10000` | No |

---

## ⚠️ **Aliases & Deprecations**

### **Identified Aliases**
- `MEILI_MASTER_KEY` → `MEILISEARCH_MASTER_KEY` (standardize to latter)
- `QDRANT_URL` → `VECTOR_DB_URL` (standardize to latter)
- `QDRANT_API_KEY` → `VECTOR_DB_API_KEY` (standardize to latter)

### **Deprecation Policy**
- All aliases will be supported during v2 transition
- Deprecation warnings will be logged
- Full migration to canonical names by v2.1

---

## 📊 **Summary**

**Total Environment Variables**: 25+ identified  
**Existing Keys**: 20+ confirmed  
**Missing v2 Keys**: 12+ to be added  
**Aliases to Standardize**: 3 identified  

**Status**: ✅ **READY FOR v2 ENVIRONMENT CONTRACT IMPLEMENTATION**

---

*This inventory will be updated as the v2 environment contract is implemented.*
