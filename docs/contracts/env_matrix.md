# Environment Contract Matrix

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE CONTRACT**  
**Purpose**: Comprehensive matrix of existing keys, new keys allowed, and deprecation policy

---

## 📋 **Existing Environment Variables (v1)**

### **AI Provider Configuration**
| Variable | Status | Type | Required | Description | Example |
|----------|--------|------|----------|-------------|---------|
| `OPENAI_API_KEY` | ✅ **CANONICAL** | String | Yes | OpenAI API key | `sk-...` |
| `ANTHROPIC_API_KEY` | ✅ **CANONICAL** | String | Yes | Anthropic API key | `sk-ant-...` |
| `HUGGINGFACE_API_TOKEN` | ✅ **CANONICAL** | String | Yes | HuggingFace API token | `hf_...` |
| `OLLAMA_BASE_URL` | ✅ **CANONICAL** | String | No | Ollama server URL | `http://localhost:11434` |

### **Database Configuration**
| Variable | Status | Type | Required | Description | Example |
|----------|--------|------|----------|-------------|---------|
| `DATABASE_URL` | ✅ **CANONICAL** | String | Yes | Primary database connection | `postgresql://...` |
| `REDIS_URL` | ✅ **CANONICAL** | String | Yes | Redis cache connection | `redis://localhost:6379/0` |
| `VECTOR_DB_URL` | ✅ **CANONICAL** | String | Yes | Qdrant vector database URL | `http://localhost:6333` |
| `VECTOR_DB_API_KEY` | ✅ **CANONICAL** | String | No | Qdrant API key | `qdrant_key_...` |

### **Search & Knowledge Graph**
| Variable | Status | Type | Required | Description | Example |
|----------|--------|------|----------|-------------|---------|
| `MEILISEARCH_URL` | ✅ **CANONICAL** | String | Yes | Meilisearch server URL | `http://localhost:7700` |
| `MEILISEARCH_MASTER_KEY` | ✅ **CANONICAL** | String | Yes | Meilisearch master key | `master_key_...` |
| `ARANGODB_URL` | ✅ **CANONICAL** | String | Yes | ArangoDB server URL | `http://localhost:8529` |
| `ARANGODB_USERNAME` | ✅ **CANONICAL** | String | Yes | ArangoDB username | `root` |
| `ARANGODB_PASSWORD` | ✅ **CANONICAL** | String | Yes | ArangoDB password | `arangodb` |
| `ARANGODB_DATABASE` | ✅ **CANONICAL** | String | Yes | ArangoDB database name | `knowledge_graph` |

### **Security & Authentication**
| Variable | Status | Type | Required | Description | Example |
|----------|--------|------|----------|-------------|---------|
| `JWT_SECRET_KEY` | ✅ **CANONICAL** | String | Yes | JWT signing secret | `jwt_secret_...` |
| `AUTH_SERVICE_SECRET` | ✅ **CANONICAL** | String | Yes | Auth service secret | `auth_secret_...` |
| `SEARCH_SERVICE_SECRET` | ✅ **CANONICAL** | String | Yes | Search service secret | `search_secret_...` |
| `SYNTHESIS_SERVICE_SECRET` | ✅ **CANONICAL** | String | Yes | Synthesis service secret | `synthesis_secret_...` |
| `FACTCHECK_SERVICE_SECRET` | ✅ **CANONICAL** | String | Yes | Fact-check service secret | `factcheck_secret_...` |
| `ANALYTICS_SERVICE_SECRET` | ✅ **CANONICAL** | String | Yes | Analytics service secret | `analytics_secret_...` |

### **Service URLs**
| Variable | Status | Type | Required | Description | Example |
|----------|--------|------|----------|-------------|---------|
| `AUTH_SERVICE_URL` | ✅ **CANONICAL** | String | Yes | Auth service endpoint | `https://auth.sarvanom.com` |
| `SEARCH_SERVICE_URL` | ✅ **CANONICAL** | String | Yes | Search service endpoint | `https://search.sarvanom.com` |
| `SYNTHESIS_SERVICE_URL` | ✅ **CANONICAL** | String | Yes | Synthesis service endpoint | `https://synthesis.sarvanom.com` |
| `FACTCHECK_SERVICE_URL` | ✅ **CANONICAL** | String | Yes | Fact-check service endpoint | `https://factcheck.sarvanom.com` |
| `ANALYTICS_SERVICE_URL` | ✅ **CANONICAL** | String | Yes | Analytics service endpoint | `https://analytics.sarvanom.com` |

### **Monitoring & Observability**
| Variable | Status | Type | Required | Description | Example |
|----------|--------|------|----------|-------------|---------|
| `SENTRY_DSN` | ✅ **CANONICAL** | String | No | Sentry error tracking DSN | `https://...@sentry.io/...` |
| `JAEGER_AGENT_HOST` | ✅ **CANONICAL** | String | No | Jaeger tracing agent host | `localhost` |
| `JAEGER_AGENT_PORT` | ✅ **CANONICAL** | String | No | Jaeger tracing agent port | `6831` |

---

## 🆕 **New v2 Environment Variables**

### **Model Orchestration**
| Variable | Type | Default | Required | Description | Example |
|----------|------|---------|----------|-------------|---------|
| `MODEL_AUTO_UPGRADE_ENABLED` | Boolean | `true` | No | Enable auto model upgrades | `true` |
| `MODEL_DISCOVERY_CRON` | String | `weekly` | No | Model discovery schedule | `weekly` |
| `MODEL_EVAL_SAMPLE_RATE` | Float | `0.05` | No | Model evaluation sample rate | `0.05` |
| `MODEL_CANARY_TRAFFIC_RATE` | Float | `0.1` | No | Canary traffic percentage | `0.1` |

### **Lane Budgets (v2 SLOs)**
| Variable | Type | Default | Required | Description | Example |
|----------|------|---------|----------|-------------|---------|
| `LANE_BUDGET_SIMPLE_MS` | Integer | `5000` | No | Simple query budget (5s) | `5000` |
| `LANE_BUDGET_TECHNICAL_MS` | Integer | `7000` | No | Technical query budget (7s) | `7000` |
| `LANE_BUDGET_RESEARCH_MS` | Integer | `10000` | No | Research query budget (10s) | `10000` |
| `LANE_BUDGET_MULTIMEDIA_MS` | Integer | `10000` | No | Multimedia query budget (10s) | `10000` |
| `SLA_TTFT_MAX_MS` | Integer | `1500` | No | Time to first token max | `1500` |
| `SLA_ORCHESTRATOR_RESERVE_MS` | Integer | `500` | No | Orchestrator reserve time | `500` |

### **Retrieval & Index Fabric**
| Variable | Type | Default | Required | Description | Example |
|----------|------|---------|----------|-------------|---------|
| `VECTOR_COLLECTION_NAME` | String | `sarvanom_vectors` | No | Qdrant collection name | `sarvanom_vectors` |
| `MEILI_INDEX_NAME` | String | `sarvanom_documents` | No | Meilisearch index name | `sarvanom_documents` |
| `KG_COLLECTION_NAME` | String | `sarvanom_entities` | No | ArangoDB collection name | `sarvanom_entities` |
| `FUSION_ALGORITHM` | String | `rrf` | No | Result fusion algorithm | `rrf` |
| `CITATION_MIN_CONFIDENCE` | Float | `0.7` | No | Minimum citation confidence | `0.7` |

### **External Feeds**
| Variable | Type | Default | Required | Description | Example |
|----------|------|---------|----------|-------------|---------|
| `NEWS_FEED_TIMEOUT_MS` | Integer | `800` | No | News feed timeout | `800` |
| `MARKETS_FEED_TIMEOUT_MS` | Integer | `800` | No | Markets feed timeout | `800` |
| `FEED_CACHE_TTL_SECONDS` | Integer | `300` | No | Feed cache TTL | `300` |
| `NEWS_API_KEY` | String | - | No | News API key | `news_api_key_...` |
| `MARKETS_API_KEY` | String | - | No | Markets API key | `markets_api_key_...` |

### **Observability & Monitoring**
| Variable | Type | Default | Required | Description | Example |
|----------|------|---------|----------|-------------|---------|
| `METRICS_ENABLED` | Boolean | `true` | No | Enable metrics collection | `true` |
| `TRACING_ENABLED` | Boolean | `true` | No | Enable distributed tracing | `true` |
| `LOG_LEVEL` | String | `INFO` | No | Logging level | `INFO` |
| `PROMETHEUS_PORT` | Integer | `9090` | No | Prometheus metrics port | `9090` |
| `GRAFANA_PORT` | Integer | `3000` | No | Grafana dashboard port | `3000` |

### **Security & Privacy**
| Variable | Type | Default | Required | Description | Example |
|----------|------|---------|----------|-------------|---------|
| `CORS_ORIGINS` | String | `*` | No | CORS allowed origins | `https://sarvanom.com` |
| `RATE_LIMIT_PER_MINUTE` | Integer | `60` | No | Rate limit per minute | `60` |
| `MAX_REQUEST_SIZE_MB` | Integer | `10` | No | Max request size in MB | `10` |
| `SECURITY_HEADERS_ENABLED` | Boolean | `true` | No | Enable security headers | `true` |
| `PII_REDACTION_ENABLED` | Boolean | `true` | No | Enable PII redaction | `true` |

---

## ⚠️ **Aliases & Deprecations**

### **Identified Aliases (v1 → v2)**
| Alias | Canonical | Status | Action | Grace Period |
|-------|-----------|--------|--------|--------------|
| `MEILI_MASTER_KEY` | `MEILISEARCH_MASTER_KEY` | ⚠️ **ALIAS** | Support both | 2 cycles |
| `QDRANT_URL` | `VECTOR_DB_URL` | ⚠️ **ALIAS** | Support both | 2 cycles |
| `QDRANT_API_KEY` | `VECTOR_DB_API_KEY` | ⚠️ **ALIAS** | Support both | 2 cycles |

### **Deprecation Policy**
1. **Announcement**: Add deprecation notice to alias
2. **Alias Support**: Continue supporting alias during grace period
3. **Warning Logs**: Log deprecation warnings when alias is used
4. **Grace Period**: 2 release cycles (approximately 2 months)
5. **Removal**: Remove alias support after grace period

### **Deprecation Implementation**
```python
# Example: Environment variable alias support
import os
import warnings

def get_env_var(key, default=None):
    """Get environment variable with alias support"""
    
    # Check canonical key first
    value = os.getenv(key, default)
    if value is not None:
        return value
    
    # Check for aliases
    aliases = {
        'MEILISEARCH_MASTER_KEY': 'MEILI_MASTER_KEY',
        'VECTOR_DB_URL': 'QDRANT_URL',
        'VECTOR_DB_API_KEY': 'QDRANT_API_KEY'
    }
    
    if key in aliases:
        alias_key = aliases[key]
        alias_value = os.getenv(alias_key)
        if alias_value is not None:
            warnings.warn(
                f"Environment variable '{alias_key}' is deprecated. "
                f"Use '{key}' instead.",
                DeprecationWarning,
                stacklevel=2
            )
            return alias_value
    
    return default
```

---

## 🔒 **Security Considerations**

### **Sensitive Variables**
| Variable | Sensitivity | Handling | Example |
|----------|-------------|----------|---------|
| `*_API_KEY` | 🔴 **HIGH** | Encrypted at rest, masked in logs | `sk-...` |
| `*_SECRET` | 🔴 **HIGH** | Encrypted at rest, never logged | `secret_...` |
| `*_PASSWORD` | 🔴 **HIGH** | Encrypted at rest, masked in logs | `password_...` |
| `*_TOKEN` | 🟡 **MEDIUM** | Masked in logs | `token_...` |
| `*_URL` | 🟢 **LOW** | Can be logged (no credentials) | `http://localhost:6333` |

### **Environment Variable Validation**
```python
# env_validation.py
import os
import re
from typing import Dict, List, Optional

class EnvironmentValidator:
    """Validate environment variables for security and correctness"""
    
    SENSITIVE_PATTERNS = [
        r'.*_API_KEY$',
        r'.*_SECRET$',
        r'.*_PASSWORD$',
        r'.*_TOKEN$'
    ]
    
    REQUIRED_VARS = [
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY',
        'DATABASE_URL',
        'REDIS_URL',
        'VECTOR_DB_URL',
        'MEILISEARCH_URL',
        'MEILISEARCH_MASTER_KEY',
        'ARANGODB_URL',
        'ARANGODB_USERNAME',
        'ARANGODB_PASSWORD',
        'ARANGODB_DATABASE',
        'JWT_SECRET_KEY'
    ]
    
    def validate_environment(self) -> Dict[str, List[str]]:
        """Validate all environment variables"""
        errors = []
        warnings = []
        
        # Check required variables
        for var in self.REQUIRED_VARS:
            if not os.getenv(var):
                errors.append(f"Required environment variable '{var}' is not set")
        
        # Check sensitive variables
        for key, value in os.environ.items():
            if self._is_sensitive(key) and not value:
                warnings.append(f"Sensitive environment variable '{key}' is empty")
        
        return {
            'errors': errors,
            'warnings': warnings
        }
    
    def _is_sensitive(self, key: str) -> bool:
        """Check if environment variable is sensitive"""
        return any(re.match(pattern, key) for pattern in self.SENSITIVE_PATTERNS)
```

---

## 📊 **Environment Variable Matrix Summary**

### **Statistics**
- **Total Existing Variables**: 25+
- **Total New v2 Variables**: 20+
- **Total Variables**: 45+
- **Aliases to Support**: 3
- **Deprecation Grace Period**: 2 cycles

### **Categories**
- **AI Provider**: 4 variables
- **Database**: 6 variables
- **Search & KG**: 6 variables
- **Security**: 6 variables
- **Service URLs**: 5 variables
- **Monitoring**: 3 variables
- **Model Orchestration**: 4 variables
- **Lane Budgets**: 6 variables
- **Retrieval**: 5 variables
- **External Feeds**: 5 variables
- **Observability**: 5 variables
- **Security & Privacy**: 5 variables

---

## 🎯 **Implementation Checklist**

### **Phase 1: Existing Variables**
- [ ] Validate all existing environment variables
- [ ] Document all current usage patterns
- [ ] Identify any missing variables

### **Phase 2: New v2 Variables**
- [ ] Add new model orchestration variables
- [ ] Add new lane budget variables
- [ ] Add new retrieval variables
- [ ] Add new external feed variables

### **Phase 3: Alias Support**
- [ ] Implement alias support for deprecated variables
- [ ] Add deprecation warnings
- [ ] Set up grace period tracking

### **Phase 4: Validation**
- [ ] Implement environment variable validation
- [ ] Add security checks
- [ ] Add required variable checks

---

## 📚 **References**

- Environment Inventory: `docs/env_inventory.md`
- Naming Conventions: `docs/contracts/naming_map.md`
- v2 Documentation: `03_env_contract.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This environment contract matrix is the single source of truth for all environment variables in SarvanOM v2.*
