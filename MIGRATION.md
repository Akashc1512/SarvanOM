# Project Migration Guide

This document outlines the migration from the old monolithic structure to the new MAANG-level monorepo structure.

## Overview

The project has been restructured from a monolithic FastAPI application to a microservices architecture with clear separation of concerns.

## New Structure

```
universal-knowledge-hub/
├── .github/                          # CI/CD workflows
├── .vscode/                          # IDE configuration
├── docs/                             # Documentation
├── infrastructure/                   # Infrastructure as Code
├── services/                         # Microservices
│   ├── api-gateway/                  # API Gateway service
│   ├── auth-service/                 # Authentication service
│   ├── search-service/               # Search & retrieval
│   ├── synthesis-service/            # AI synthesis
│   ├── factcheck-service/            # Fact checking
│   └── analytics-service/            # Analytics & metrics
├── shared/                           # Shared libraries
│   ├── core/                         # Core utilities
│   ├── models/                       # Data models
│   ├── config/                       # Configuration
│   └── middleware/                   # Shared middleware
├── frontend/                         # Next.js application
├── tests/                            # All tests
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   ├── e2e/                         # End-to-end tests
│   └── performance/                  # Performance tests
├── scripts/                          # Build & deployment scripts
├── config/                           # Configuration files
├── .env.template                     # Environment template
├── pyproject.toml                    # Python project config
├── package.json                      # Root package.json for monorepo
├── docker-compose.yml                # Local development
├── Makefile                          # Build automation
└── README.md                         # Project overview
```

## File Migration Mapping

### API Files → Services

#### API Gateway Service (`services/api-gateway/`)
- `api/main.py` → `services/api-gateway/main.py`
- `api/main_simple.py` → `services/api-gateway/main_simple.py`
- `api/main_secure.py` → `services/api-gateway/main_secure.py`
- `api/main_v2.py` → `services/api-gateway/main_v2.py`
- `api/versioning.py` → `services/api-gateway/versioning.py`
- `api/versioning_v2.py` → `services/api-gateway/versioning_v2.py`
- `api/endpoints_v1.py` → `services/api-gateway/endpoints_v1.py`
- `api/endpoints_v2.py` → `services/api-gateway/endpoints_v2.py`
- `api/realtime.py` → `services/api-gateway/realtime.py`
- `api/docs.py` → `services/api-gateway/docs.py`
- `api/routes/` → `services/api-gateway/routes/`

#### Auth Service (`services/auth-service/`)
- `api/auth.py` → `services/auth-service/auth.py`
- `api/auth_secure.py` → `services/auth-service/auth_secure.py`
- `api/user_management.py` → `services/auth-service/user_management.py`
- `api/user_management_v2.py` → `services/auth-service/user_management_v2.py`
- `api/security.py` → `services/auth-service/security.py`
- `api/validators.py` → `services/auth-service/validators.py`

#### Search Service (`services/search-service/`)
- `agents/retrieval_agent.py` → `services/search-service/retrieval_agent.py`

#### Synthesis Service (`services/synthesis-service/`)
- `agents/synthesis_agent.py` → `services/synthesis-service/synthesis_agent.py`
- `agents/citation_agent.py` → `services/synthesis-service/citation_agent.py`
- `api/ml_integration.py` → `services/synthesis-service/ml_integration.py`
- `api/recommendation_service.py` → `services/synthesis-service/recommendation_service.py`

#### Fact Check Service (`services/factcheck-service/`)
- `agents/factcheck_agent.py` → `services/factcheck-service/factcheck_agent.py`

#### Analytics Service (`services/analytics-service/`)
- `api/analytics.py` → `services/analytics-service/analytics.py`
- `api/analytics_v2.py` → `services/analytics-service/analytics_v2.py`
- `api/monitoring.py` → `services/analytics-service/monitoring.py`
- `api/metrics.py` → `services/analytics-service/metrics.py`
- `api/health_checks.py` → `services/analytics-service/health_checks.py`
- `api/feedback_storage.py` → `services/analytics-service/feedback_storage.py`
- `api/integration_layer.py` → `services/analytics-service/integration_layer.py`
- `api/integration_monitor.py` → `services/analytics-service/integration_monitor.py`

### Shared Libraries (`shared/`)

#### Core Utilities (`shared/core/`)
- `api/cache.py` → `shared/core/cache.py`
- `api/rate_limiter.py` → `shared/core/rate_limiter.py`
- `api/connection_pool.py` → `shared/core/connection_pool.py`
- `api/performance.py` → `shared/core/performance.py`
- `api/retry_logic.py` → `shared/core/retry_logic.py`
- `api/shutdown_handler.py` → `shared/core/shutdown_handler.py`
- `api/patterns/` → `shared/core/patterns/`
- `agents/base_agent.py` → `shared/core/base_agent.py`
- `agents/data_models.py` → `shared/core/data_models.py`
- `agents/llm_client.py` → `shared/core/llm_client.py`

#### Configuration (`shared/config/`)
- `api/config.py` → `shared/config/config.py`
- `api/models.py` → `shared/config/models.py`
- `api/exceptions.py` → `shared/config/exceptions.py`

#### Models (`shared/models/`)
- `api/database/` → `shared/models/`

#### Middleware (`shared/middleware/`)
- `api/middleware/` → `shared/middleware/`

### Infrastructure (`infrastructure/`)

#### Kubernetes (`infrastructure/kubernetes/`)
- `k8s/` → `infrastructure/kubernetes/`

#### Monitoring (`infrastructure/monitoring/`)
- `monitoring/` → `infrastructure/monitoring/`

#### Terraform (`infrastructure/terraform/`)
- `infrastructure/terraform/` → `infrastructure/terraform/` (already in place)

### Tests (`tests/`)

#### Unit Tests (`tests/unit/`)
- `test_*.py` (root) → `tests/unit/`

#### Integration Tests (`tests/integration/`)
- `tests/test_*.py` → `tests/integration/`

#### Performance Tests (`tests/performance/`)
- `tests/performance/` → `tests/performance/` (already in place)

### Scripts (`scripts/`)
- `scripts/` → `scripts/` (already in place)
- `*.sh` (root) → `scripts/`

### Configuration Files
- `env.example` → `.env.template`
- `requirements*.txt` → Consolidated into `pyproject.toml`
- `production.env.example` → Removed (use `.env.template`)

## Import Path Updates

### Old Imports → New Imports

#### API Gateway
```python
# Old
from api.main import app
from api.config import settings

# New
from services.api_gateway.main import app
from shared.core.api.config import settings
```

#### Auth Service
```python
# Old
from api.auth import authenticate_user
from api.user_management import create_user

# New
from services.auth_service.auth import authenticate_user
from services.auth_service.user_management import create_user
```

#### Shared Libraries
```python
# Old
from api.cache import Cache
from agents.base_agent import BaseAgent

# New
from shared.core.cache import Cache
from shared.core.agents.base_agent import BaseAgent
```

## Environment Configuration

### Environment Variables
- Single source of truth: `.env.template`
- Removed redundant files: `env.template`, `production.env.example`
- All services use the same environment configuration

### Configuration Management
- Centralized in `shared/config/`
- Service-specific configs in respective service directories
- Environment-specific overrides through `.env` files

## Development Workflow Changes

### Package Management
- **Before**: Multiple `requirements*.txt` files
- **After**: Single `pyproject.toml` with optional dependencies

### Installation
```bash
# Before
pip install -r requirements.txt
pip install -r requirements-dev.txt

# After
pip install -e .[dev,test,security]
```

### Running Services
```bash
# Before
python -m uvicorn api.main:app --reload

# After
npm run dev:backend  # Starts API Gateway
# Or individual services:
make start:api-gateway
make start:auth-service
```

### Testing
```bash
# Before
pytest tests/

# After
npm run test:unit
npm run test:integration
npm run test:e2e
npm run test:performance
```

## Docker Changes

### Multi-Service Architecture
- Each service has its own Dockerfile
- `docker-compose.yml` orchestrates all services
- Shared volumes for development
- Service-specific environment variables

### Development vs Production
- Development: `docker-compose.yml`
- Production: `docker-compose.prod.yml` (to be created)

## Migration Checklist

### For Developers

1. **Update Import Paths**
   - [ ] Update all Python imports to use new structure
   - [ ] Update relative imports in moved files
   - [ ] Update import statements in tests

2. **Environment Setup**
   - [ ] Copy `.env.template` to `.env`
   - [ ] Configure environment variables
   - [ ] Update service URLs in frontend

3. **Dependencies**
   - [ ] Install new dependencies: `pip install -e .[dev,test,security]`
   - [ ] Install Node.js dependencies: `npm install`

4. **Testing**
   - [ ] Run unit tests: `npm run test:unit`
   - [ ] Run integration tests: `npm run test:integration`
   - [ ] Verify all tests pass

5. **Development**
   - [ ] Start development servers: `npm run dev`
   - [ ] Verify all services start correctly
   - [ ] Test API endpoints

### For DevOps

1. **Infrastructure**
   - [ ] Update CI/CD pipelines for new structure
   - [ ] Update deployment scripts
   - [ ] Update monitoring configurations

2. **Docker**
   - [ ] Build Docker images: `make docker-build`
   - [ ] Test Docker Compose setup: `make docker-up`
   - [ ] Verify all services in containers

3. **Monitoring**
   - [ ] Update service discovery
   - [ ] Update health check endpoints
   - [ ] Update logging configurations

## Breaking Changes

### API Endpoints
- Service-specific endpoints now have different base URLs
- API Gateway routes requests to appropriate services
- Authentication handled by Auth Service

### Configuration
- Environment variables may have changed names
- Service-specific configs moved to individual services
- Shared configs in `shared/config/`

### Database
- Database models moved to `shared/models/`
- Service-specific models in respective services
- Migration scripts may need updates

## Rollback Plan

If issues arise during migration:

1. **Immediate Rollback**
   ```bash
   git checkout main
   git revert <migration-commit>
   ```

2. **Gradual Migration**
   - Keep old structure in parallel
   - Migrate services one by one
   - Use feature flags for gradual rollout

3. **Database Rollback**
   ```bash
   # Restore database from backup
   # Revert migration scripts
   ```

## Support

For migration issues:

1. Check the logs: `make logs`
2. Verify service health: `make monitor:health`
3. Run tests: `make test`
4. Check configuration: `make setup`

## Next Steps

1. **Immediate**
   - [ ] Update all import paths
   - [ ] Test all services
   - [ ] Update documentation

2. **Short Term**
   - [ ] Add service-specific Dockerfiles
   - [ ] Create production Docker Compose
   - [ ] Update CI/CD pipelines

3. **Long Term**
   - [ ] Implement service mesh
   - [ ] Add service discovery
   - [ ] Implement distributed tracing
   - [ ] Add service-specific monitoring

## Benefits of New Structure

1. **Scalability**: Easy to add new services
2. **Maintainability**: Clear separation of concerns
3. **Testing**: Organized test structure
4. **Deployment**: Service-specific deployments
5. **Development**: Faster builds, better caching
6. **Team Collaboration**: Clear ownership boundaries
7. **MAANG Standards**: Follows industry best practices 