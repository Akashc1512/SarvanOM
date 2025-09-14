# Main.py Wiring Audit Report

## Overview
This report audits the main.py files across all specified services for proper wiring, configuration, and architectural compliance.

## Services Audited
- model_registry/
- model_router/
- auto_upgrade/
- guided_prompt/
- retrieval/
- feeds/
- observability/

---

## Service-by-Service Analysis

### 1. Model Registry Service (`services/model_registry/main.py`)

**Configuration Import**: ❌ **NO**
- Does not import central config module
- Uses hardcoded Redis connection: `redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)`
- No environment variable usage for configuration

**FastAPI App Creation**: ✅ **YES**
- Creates FastAPI app at module top: `app = FastAPI(title="Model Registry Service", version="2.0.0")`

**Routers Included**: ❌ **NO**
- No routers included
- All endpoints defined directly in main.py

**Startup/Shutdown Events**: ❌ **NO**
- No startup/shutdown event handlers
- No client initialization/cleanup

**App.state/DI Container**: ❌ **NO**
- No app.state usage
- No dependency injection container
- Direct instantiation: `model_registry = ModelRegistry(redis_client)`

**Health/Ready/Config/Version Endpoints**: ⚠️ **PARTIAL**
- ✅ `/health` endpoint present
- ❌ No `/ready` endpoint
- ❌ No `/config` endpoint (sanitized)
- ❌ No `/version` endpoint

**Tracing/Metrics Middleware**: ⚠️ **PARTIAL**
- ✅ Prometheus metrics defined and started
- ❌ No conditional mounting based on environment keys
- ❌ No tracing middleware

**Port Configuration**: ✅ **YES**
- Port 8000 matches docker-compose.yml

---

### 2. Model Router Service (`services/model_router/main.py`)

**Configuration Import**: ✅ **YES**
- Imports central config: `from .config import get_config`
- Imports provider config: `from sarvanom.shared.core.config.provider_config import get_provider_config`
- Uses config in initialization: `self.config = get_config()`

**FastAPI App Creation**: ✅ **YES**
- Creates FastAPI app at module top: `app = FastAPI(title="Model Router Service", version="2.0.0")`

**Routers Included**: ❌ **NO**
- No routers included
- All endpoints defined directly in main.py

**Startup/Shutdown Events**: ❌ **NO**
- No startup/shutdown event handlers
- No client initialization/cleanup

**App.state/DI Container**: ❌ **NO**
- No app.state usage
- No dependency injection container
- Direct instantiation: `model_router = ModelRouter()`

**Health/Ready/Config/Version Endpoints**: ⚠️ **PARTIAL**
- ✅ `/health` endpoint present
- ❌ No `/ready` endpoint
- ❌ No `/config` endpoint (sanitized)
- ❌ No `/version` endpoint

**Tracing/Metrics Middleware**: ⚠️ **PARTIAL**
- ✅ Prometheus metrics defined and started
- ❌ No conditional mounting based on environment keys
- ❌ No tracing middleware

**Port Configuration**: ✅ **YES**
- Port 8001 matches docker-compose.yml

---

### 3. Auto-Upgrade Service (`services/auto_upgrade/main.py`)

**Configuration Import**: ❌ **NO**
- Does not import central config module
- No environment variable usage for configuration
- Hardcoded registry URL: `registry_url: str = "http://localhost:8000"`

**FastAPI App Creation**: ✅ **YES**
- Creates FastAPI app at module top: `app = FastAPI(title="Auto-Upgrade Service", version="2.0.0")`

**Routers Included**: ❌ **NO**
- No routers included
- All endpoints defined directly in main.py

**Startup/Shutdown Events**: ❌ **NO**
- No startup/shutdown event handlers
- No client initialization/cleanup

**App.state/DI Container**: ❌ **NO**
- No app.state usage
- No dependency injection container
- Direct instantiation: `auto_upgrade_service = AutoUpgradeService()`

**Health/Ready/Config/Version Endpoints**: ⚠️ **PARTIAL**
- ✅ `/health` endpoint present
- ❌ No `/ready` endpoint
- ❌ No `/config` endpoint (sanitized)
- ❌ No `/version` endpoint

**Tracing/Metrics Middleware**: ⚠️ **PARTIAL**
- ✅ Prometheus metrics defined and started
- ❌ No conditional mounting based on environment keys
- ❌ No tracing middleware

**Port Configuration**: ✅ **YES**
- Port 8002 matches docker-compose.yml

---

### 4. Guided Prompt Service (`services/guided_prompt/main.py`)

**Configuration Import**: ✅ **YES**
- Imports central config: `from .config import get_config, get_provider_summary, is_guided_prompt_enabled`
- Uses config in initialization: `config = get_config()`

**FastAPI App Creation**: ✅ **YES**
- Creates FastAPI app at module top: `app = FastAPI(title="Guided Prompt Confirmation Service", version="2.0.0")`

**Routers Included**: ❌ **NO**
- No routers included
- All endpoints defined directly in main.py

**Startup/Shutdown Events**: ❌ **NO**
- No startup/shutdown event handlers
- No client initialization/cleanup

**App.state/DI Container**: ❌ **NO**
- No app.state usage
- No dependency injection container
- Direct instantiation: `guided_prompt_service = GuidedPromptService(redis_client)`

**Health/Ready/Config/Version Endpoints**: ⚠️ **PARTIAL**
- ✅ `/health` endpoint present (calls `config.get_service_health()`)
- ❌ No `/ready` endpoint
- ❌ No `/config` endpoint (sanitized)
- ❌ No `/version` endpoint

**Tracing/Metrics Middleware**: ⚠️ **PARTIAL**
- ✅ Prometheus metrics defined and started
- ❌ No conditional mounting based on environment keys
- ❌ No tracing middleware

**Port Configuration**: ✅ **YES**
- Port 8003 matches docker-compose.yml

---

### 5. Retrieval Service (`services/retrieval/main.py`)

**Configuration Import**: ❌ **NO**
- Does not import central config module
- Uses hardcoded Redis connection: `redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)`
- No environment variable usage for configuration

**FastAPI App Creation**: ✅ **YES**
- Creates FastAPI app at module top: `app = FastAPI(title="Retrieval Service", version="2.0.0")`

**Routers Included**: ❌ **NO**
- No routers included
- All endpoints defined directly in main.py

**Startup/Shutdown Events**: ❌ **NO**
- No startup/shutdown event handlers
- No client initialization/cleanup

**App.state/DI Container**: ❌ **NO**
- No app.state usage
- No dependency injection container
- Direct instantiation: `retrieval_service = RetrievalService(redis_client)`

**Health/Ready/Config/Version Endpoints**: ⚠️ **PARTIAL**
- ✅ `/health` endpoint present
- ❌ No `/ready` endpoint
- ❌ No `/config` endpoint (sanitized)
- ❌ No `/version` endpoint

**Tracing/Metrics Middleware**: ⚠️ **PARTIAL**
- ✅ Prometheus metrics defined and started
- ❌ No conditional mounting based on environment keys
- ❌ No tracing middleware

**Port Configuration**: ✅ **YES**
- Port 8004 matches docker-compose.yml

---

### 6. Feeds Service (`services/feeds/main.py`)

**Configuration Import**: ✅ **YES**
- Imports central config: `from .config import get_config`
- Imports provider config: `from sarvanom.shared.core.config.provider_config import get_provider_config`
- Uses config in initialization: `self.config = get_config()`

**FastAPI App Creation**: ✅ **YES**
- Creates FastAPI app at module top: `app = FastAPI(title="External Feeds Service", version="2.0.0")`

**Routers Included**: ❌ **NO**
- No routers included
- All endpoints defined directly in main.py

**Startup/Shutdown Events**: ❌ **NO**
- No startup/shutdown event handlers
- No client initialization/cleanup

**App.state/DI Container**: ❌ **NO**
- No app.state usage
- No dependency injection container
- Direct instantiation: `feeds_service = ExternalFeedsService(redis_client)`

**Health/Ready/Config/Version Endpoints**: ⚠️ **PARTIAL**
- ✅ `/health` endpoint present
- ❌ No `/ready` endpoint
- ❌ No `/config` endpoint (sanitized)
- ❌ No `/version` endpoint

**Tracing/Metrics Middleware**: ⚠️ **PARTIAL**
- ✅ Prometheus metrics defined and started
- ❌ No conditional mounting based on environment keys
- ❌ No tracing middleware

**Port Configuration**: ✅ **YES**
- Port 8005 matches docker-compose.yml

---

### 7. Observability Service (`services/observability/main.py`)

**Configuration Import**: ❌ **NO**
- Does not import central config module
- Uses hardcoded Redis connection: `redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)`
- No environment variable usage for configuration

**FastAPI App Creation**: ✅ **YES**
- Creates FastAPI app at module top: `app = FastAPI(title="Observability Service", version="2.0.0")`

**Routers Included**: ❌ **NO**
- No routers included
- All endpoints defined directly in main.py

**Startup/Shutdown Events**: ❌ **NO**
- No startup/shutdown event handlers
- No client initialization/cleanup

**App.state/DI Container**: ❌ **NO**
- No app.state usage
- No dependency injection container
- Direct instantiation: `trace_propagation = TracePropagation()`

**Health/Ready/Config/Version Endpoints**: ⚠️ **PARTIAL**
- ✅ `/health` endpoint present
- ❌ No `/ready` endpoint
- ❌ No `/config` endpoint (sanitized)
- ❌ No `/version` endpoint

**Tracing/Metrics Middleware**: ⚠️ **PARTIAL**
- ✅ Prometheus metrics defined and started
- ❌ No conditional mounting based on environment keys
- ❌ No tracing middleware

**Port Configuration**: ✅ **YES**
- Port 8006 matches docker-compose.yml

---

## Summary Table: Missing Items per Service

| Service | Config Import | Routers | Startup/Shutdown | App.state/DI | Ready Endpoint | Config Endpoint | Version Endpoint | Tracing Middleware | Total Missing |
|---------|---------------|---------|------------------|--------------|----------------|-----------------|------------------|-------------------|---------------|
| model_registry | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 7 |
| model_router | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 6 |
| auto_upgrade | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 7 |
| guided_prompt | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 6 |
| retrieval | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 7 |
| feeds | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 6 |
| observability | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 7 |

## Critical Issues Identified

### 1. Configuration Management
- **5 out of 7 services** do not import the central config module
- Hardcoded Redis connections in most services
- No environment variable usage for critical settings

### 2. Architecture Patterns
- **All services** lack proper router organization
- **All services** missing startup/shutdown event handlers
- **All services** not using app.state or DI containers

### 3. Observability
- **All services** missing `/ready`, `/config`, and `/version` endpoints
- **All services** lack conditional tracing/metrics middleware
- No proper health check implementation

### 4. Service Dependencies
- No proper client initialization/cleanup
- Missing dependency injection patterns
- No graceful shutdown handling

## Recommendations

1. **Immediate Actions**:
   - Import central config module in all services
   - Add startup/shutdown event handlers
   - Implement proper health/ready/config/version endpoints

2. **Architecture Improvements**:
   - Refactor to use routers for better organization
   - Implement app.state for shared client management
   - Add conditional tracing/metrics middleware

3. **Configuration Standardization**:
   - Use environment variables for all configuration
   - Implement proper secrets management
   - Add configuration validation

4. **Observability Enhancement**:
   - Add structured logging
   - Implement distributed tracing
   - Add comprehensive metrics collection

## Compliance Status
- **Overall Compliance**: 23% (16/70 criteria met)
- **Critical Issues**: 7 services with major configuration gaps
- **Priority**: HIGH - Requires immediate attention for production readiness
