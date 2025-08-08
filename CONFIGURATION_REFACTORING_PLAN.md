# Configuration Refactoring Plan - Remove Hard-coded Values

## Overview
This document outlines the comprehensive plan to remove all hard-coded secrets and configuration values from the sarvanom project and implement proper environment-based configuration management.

## Current State Analysis

### ✅ Already Properly Configured
- Main configuration classes (`CentralConfig`, `EnvironmentManager`)
- Most API keys and secrets are environment-based
- Database connection strings are configurable
- JWT secrets are environment-based

### ❌ Issues Found
1. **Hard-coded service URLs** in `environment_manager.py`
2. **Hard-coded localhost defaults** in configuration files
3. **Hard-coded ports** in some connection strings
4. **Test files** with hard-coded URLs (acceptable for tests)

## Refactoring Plan

### Phase 1: Service URL Configuration
**Files to update:**
- `shared/core/config/environment_manager.py`
- `shared/core/config/central_config.py`

**Changes:**
- Replace hard-coded localhost URLs with environment variables
- Add proper defaults for development
- Ensure production uses environment variables

### Phase 2: Connection String Refactoring
**Files to update:**
- `shared/core/connection_pool.py`
- `services/api_gateway/main.py`

**Changes:**
- Remove hard-coded localhost:port combinations
- Use environment variables for all connection parameters
- Add proper validation for required environment variables

### Phase 3: Environment Variable Documentation
**Files to create/update:**
- `.env.example` (comprehensive template)
- `README.md` (environment setup instructions)
- `docker-compose.yml` (environment variable examples)

### Phase 4: Validation and Testing
**Files to create:**
- Configuration validation scripts
- Environment variable check scripts
- Security audit scripts

## Implementation Steps

### Step 1: Update Environment Manager
Replace hard-coded service URLs with environment variables:

```python
# Before
auth_service_url: str = "http://localhost:8001"

# After
auth_service_url: str = Field(
    default="http://localhost:8001",
    description="Auth service URL"
)
```

### Step 2: Update Central Config
Ensure all defaults are environment-configurable:

```python
# Before
qdrant_url: HttpUrl = Field(
    default="http://localhost:6333",
    description="Qdrant server URL"
)

# After
qdrant_url: HttpUrl = Field(
    default_factory=lambda: os.getenv("QDRANT_URL", "http://localhost:6333"),
    description="Qdrant server URL"
)
```

### Step 3: Create Comprehensive .env.example
Document all required environment variables:

```bash
# Core Application
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/sarvanom
REDIS_URL=redis://localhost:6379/0

# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Vector Databases
QDRANT_URL=http://localhost:6333
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-east-1

# Search
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_MASTER_KEY=...

# Knowledge Graph
ARANGODB_URL=http://localhost:8529
ARANGODB_USERNAME=root
ARANGODB_PASSWORD=
ARANGODB_DATABASE=knowledge_graph

# Security
JWT_SECRET_KEY=your-secret-key-here

# Services
AUTH_SERVICE_URL=http://localhost:8001
SEARCH_SERVICE_URL=http://localhost:8002
SYNTHESIS_SERVICE_URL=http://localhost:8003
FACTCHECK_SERVICE_URL=http://localhost:8004
ANALYTICS_SERVICE_URL=http://localhost:8005
```

### Step 4: Update Docker Configuration
Ensure Docker Compose uses environment variables:

```yaml
version: '3.8'
services:
  backend:
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      # ... all other environment variables
```

## Security Considerations

### ✅ Implemented
- Secrets are masked in logs
- Environment variable precedence
- Secure defaults for development
- Configuration validation

### 🔄 To Implement
- Environment variable validation on startup
- Required vs optional environment variables
- Production environment checks
- Secret rotation support

## Testing Strategy

### Unit Tests
- Configuration loading tests
- Environment variable validation tests
- Default value tests
- Security masking tests

### Integration Tests
- Full configuration loading
- Environment variable precedence
- Docker environment testing

### Security Tests
- Secret exposure prevention
- Configuration validation
- Environment variable sanitization

## Migration Guide

### For Developers
1. Copy `.env.example` to `.env`
2. Fill in required environment variables
3. Run configuration validation script
4. Start development server

### For Production
1. Set all required environment variables
2. Run production validation script
3. Verify no hard-coded values in logs
4. Deploy with environment-based configuration

## Success Criteria

- [ ] No hard-coded secrets in source code
- [ ] All configuration values use environment variables
- [ ] Comprehensive `.env.example` file
- [ ] Configuration validation on startup
- [ ] Security audit passes
- [ ] All tests pass with environment-based config
- [ ] Docker deployment works with environment variables
- [ ] Documentation updated with setup instructions

## Timeline

- **Phase 1**: Service URL refactoring (1 day)
- **Phase 2**: Connection string refactoring (1 day)
- **Phase 3**: Documentation and examples (1 day)
- **Phase 4**: Testing and validation (1 day)
- **Total**: 4 days for complete refactoring

## Risk Mitigation

1. **Backward Compatibility**: Maintain default values for development
2. **Gradual Migration**: Update one component at a time
3. **Comprehensive Testing**: Test all configuration scenarios
4. **Documentation**: Clear migration guide for developers
5. **Validation**: Automated checks for missing environment variables 