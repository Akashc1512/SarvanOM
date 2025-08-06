# Configuration Management Guide

## Overview

The Universal Knowledge Platform now features a comprehensive, environment-based configuration management system that follows MAANG (Meta, Amazon, Apple, Netflix, Google) best practices for security, validation, and environment handling.

## Features

### ✅ **Environment-Based Configuration**
- **Development**: Debug mode, local databases, mock providers
- **Testing**: Mock AI responses, test databases, authentication bypass
- **Staging**: Production-like with monitoring, real providers
- **Production**: Full security, cloud databases, real providers

### ✅ **Secure Secrets Management**
- Environment variables for all secrets
- Automatic secret masking in logs
- No hardcoded secrets in code
- Secure defaults for all environments

### ✅ **Configuration Validation**
- Type validation for all settings
- Environment-specific validation rules
- Clear error messages for missing config
- Automatic validation on startup

### ✅ **Environment Variable Precedence**
- Environment variables override config files
- Config files override defaults
- Clear precedence hierarchy
- Easy to override for testing

## Quick Start

### 1. Set Environment

```bash
# Development (default)
export APP_ENV=development

# Testing
export APP_ENV=testing

# Staging
export APP_ENV=staging

# Production
export APP_ENV=production
```

### 2. Copy Environment Template

```bash
# Copy the example environment file
cp env.example .env

# Edit with your actual values
nano .env
```

### 3. Set Required Environment Variables

```bash
# Core settings
export APP_ENV=development
export LOG_LEVEL=INFO

# Database
export DATABASE_URL=sqlite:///dev.db

# Redis
export REDIS_URL=redis://localhost:6379/0

# AI Providers (optional for development)
export OPENAI_API_KEY=your_openai_key_here
export ANTHROPIC_API_KEY=your_anthropic_key_here

# Security
export JWT_SECRET_KEY=$(openssl rand -hex 32)

# Vector Database
export VECTOR_DB_URL=http://localhost:6333
export VECTOR_DB_API_KEY=your_vector_db_key_here

# Search Engine
export MEILISEARCH_URL=http://localhost:7700
export MEILISEARCH_MASTER_KEY=your_meilisearch_key_here

# Knowledge Graph
export ARANGODB_URL=http://localhost:8529
export ARANGODB_USERNAME=root
export ARANGODB_PASSWORD=your_arangodb_password_here
```

## Environment-Specific Configuration

### Development Environment

**File**: `config/development.yaml`

**Features**:
- ✅ Debug mode enabled
- ✅ Auto-reload enabled
- ✅ Local databases (SQLite)
- ✅ Debug endpoints enabled
- ✅ Detailed logging
- ✅ Mock providers available
- ✅ Lower rate limits for testing

**Required Variables**:
```bash
APP_ENV=development
DATABASE_URL=sqlite:///dev.db
REDIS_URL=redis://localhost:6379/0
```

### Testing Environment

**File**: `config/testing.yaml`

**Features**:
- ✅ Mock AI responses enabled
- ✅ Authentication bypassed
- ✅ Test databases
- ✅ Debug endpoints enabled
- ✅ Mock providers enabled
- ✅ High rate limits for testing

**Required Variables**:
```bash
APP_ENV=testing
DATABASE_URL=sqlite:///test.db
REDIS_URL=redis://localhost:6379/1
```

### Staging Environment

**File**: `config/staging.yaml`

**Features**:
- ❌ Debug mode disabled
- ❌ Auto-reload disabled
- ✅ Production-like databases
- ❌ Debug endpoints disabled
- ✅ Real providers
- ✅ Monitoring enabled
- ✅ Security features enabled

**Required Variables**:
```bash
APP_ENV=staging
DATABASE_URL=postgresql://user:password@staging-db:5432/sarvanom
REDIS_URL=redis://staging-redis:6379/0
JWT_SECRET_KEY=your_jwt_secret_here
```

### Production Environment

**File**: `config/production.yaml`

**Features**:
- ❌ Debug mode disabled
- ❌ Auto-reload disabled
- ✅ Production databases
- ❌ Debug endpoints disabled
- ✅ Real providers
- ✅ Full monitoring
- ✅ All security features
- ✅ Backup enabled
- ✅ Audit logging enabled

**Required Variables**:
```bash
APP_ENV=production
DATABASE_URL=postgresql://user:password@prod-db:5432/sarvanom
REDIS_URL=redis://prod-redis:6379/0
JWT_SECRET_KEY=your_jwt_secret_here
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

## Configuration Sources

The system loads configuration from multiple sources in this order:

1. **Environment-Specific Defaults** (built into code)
2. **Configuration Files** (`config/{environment}.yaml`)
3. **Environment Variables** (highest precedence)

### Configuration Files

Create environment-specific configuration files in the `config/` directory:

```yaml
# config/development.yaml
name: "development"
debug: true
log_level: "DEBUG"
database_url: "sqlite:///dev.db"
redis_url: "redis://localhost:6379/0"
# ... other settings
```

### Environment Variables

All configuration can be overridden via environment variables:

```bash
# Override any setting
export LOG_LEVEL=DEBUG
export RATE_LIMIT_PER_MINUTE=120
export MAX_REQUEST_SIZE_MB=50
export CACHE_TTL_SECONDS=1800
```

## Security Features

### Secret Management

**Never commit secrets to version control!**

```bash
# ✅ Good - Use environment variables
export OPENAI_API_KEY=sk-1234567890abcdef

# ❌ Bad - Don't hardcode in files
OPENAI_API_KEY=sk-1234567890abcdef
```

### Secret Masking

Secrets are automatically masked in logs:

```python
# Secrets are masked in logs
config_dict = env_config.to_dict(include_secrets=False)
# Result: {"openai_api_key": "***REDACTED***"}

# Include secrets only when needed
config_dict = env_config.to_dict(include_secrets=True)
# Result: {"openai_api_key": "sk-1234567890abcdef"}
```

### Environment Validation

Each environment has specific validation rules:

```python
# Production requires certain settings
if env_manager.is_production():
    if not env_config.database_url:
        raise ValueError("DATABASE_URL required in production")
    if not env_config.jwt_secret_key:
        raise ValueError("JWT_SECRET_KEY required in production")
```

## Testing Configuration

### Run Configuration Tests

```bash
# Test all environments
python scripts/test_configuration_management.py

# Test specific environment
python scripts/test_configuration_management.py production
```

### Test Environment Switching

```bash
# Test development
APP_ENV=development python -m pytest

# Test production
APP_ENV=production python -m pytest
```

### Validate Configuration

```bash
# Check configuration
python -c "
from shared.core.config.environment_manager import get_environment_manager
env_manager = get_environment_manager()
print(f'Environment: {env_manager.environment.value}')
print(f'Config: {env_manager.get_config().name}')
"
```

## Environment Variables Reference

### Core Application

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_ENV` | Environment name | `development` | ✅ |
| `LOG_LEVEL` | Logging level | `INFO` | ❌ |
| `DEBUG` | Debug mode | `false` | ❌ |
| `TEST_MODE` | Testing mode | `false` | ❌ |

### Database Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | Database connection URL | `sqlite:///dev.db` | ✅ |
| `DB_POOL_SIZE` | Connection pool size | `5` | ❌ |
| `DB_MAX_OVERFLOW` | Max overflow connections | `10` | ❌ |
| `DB_POOL_TIMEOUT` | Pool timeout (seconds) | `30` | ❌ |

### Cache Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` | ✅ |
| `CACHE_TTL_SECONDS` | Cache TTL (seconds) | `3600` | ❌ |
| `SESSION_TTL_SECONDS` | Session TTL (seconds) | `86400` | ❌ |

### AI/LLM Providers

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | `null` | ❌ |
| `ANTHROPIC_API_KEY` | Anthropic API key | `null` | ❌ |
| `OLLAMA_ENABLED` | Enable Ollama | `true` | ❌ |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` | ❌ |

### Security

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `JWT_SECRET_KEY` | JWT signing key | `null` | ✅ (prod) |
| `CORS_ORIGINS` | Allowed CORS origins | `[]` | ❌ |
| `RATE_LIMIT_PER_MINUTE` | Rate limit per minute | `60` | ❌ |

### Performance

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MAX_REQUEST_SIZE_MB` | Max request size (MB) | `10` | ❌ |
| `WORKER_PROCESSES` | Number of worker processes | `2` | ❌ |
| `WORKER_THREADS` | Number of worker threads | `2` | ❌ |
| `MAX_MEMORY_USAGE_MB` | Max memory usage (MB) | `1024` | ❌ |

### Monitoring

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `METRICS_ENABLED` | Enable metrics | `true` | ❌ |
| `METRICS_PORT` | Metrics port | `9090` | ❌ |
| `ENABLE_TRACING` | Enable tracing | `false` | ❌ |
| `SENTRY_DSN` | Sentry DSN | `null` | ❌ |

## Troubleshooting

### Common Issues

#### 1. Configuration Not Loading

```bash
# Check environment variable
echo $APP_ENV

# Check config file exists
ls config/

# Check environment manager
python -c "
from shared.core.config.environment_manager import get_environment_manager
print(get_environment_manager().environment.value)
"
```

#### 2. Missing Required Variables

```bash
# Check required variables for production
APP_ENV=production python -c "
from shared.core.config.environment_manager import EnvironmentManager
env_manager = EnvironmentManager()
print('Required variables:')
print('- DATABASE_URL:', bool(env_manager.get_config().database_url))
print('- REDIS_URL:', bool(env_manager.get_config().redis_url))
print('- JWT_SECRET_KEY:', bool(env_manager.get_config().jwt_secret_key))
"
```

#### 3. Secret Not Masked

```python
# Check secret masking
from shared.core.config.environment_manager import get_environment_manager
env_config = get_environment_manager().get_config()
config_dict = env_config.to_dict(include_secrets=False)
print("Secrets masked:", "***REDACTED***" in str(config_dict))
```

### Debug Configuration

```python
# Debug configuration loading
import logging
logging.basicConfig(level=logging.DEBUG)

from shared.core.config.environment_manager import EnvironmentManager
env_manager = EnvironmentManager()
print(env_manager.get_config_summary())
```

## Best Practices

### 1. Environment-Specific Settings

```bash
# Development
export APP_ENV=development
export DEBUG=true
export LOG_LEVEL=DEBUG

# Production
export APP_ENV=production
export DEBUG=false
export LOG_LEVEL=WARNING
```

### 2. Secret Management

```bash
# Generate secure secrets
export JWT_SECRET_KEY=$(openssl rand -hex 32)
export AUTH_SERVICE_SECRET=$(openssl rand -hex 32)

# Use different secrets per environment
export DATABASE_URL=postgresql://dev:dev@localhost:5432/dev_db  # dev
export DATABASE_URL=postgresql://prod:prod@prod-db:5432/prod_db  # prod
```

### 3. Configuration Validation

```python
# Validate configuration on startup
from shared.core.config.environment_manager import get_environment_manager
env_manager = get_environment_manager()
env_config = env_manager.get_config()

# Check required settings
if env_manager.is_production():
    assert env_config.database_url, "DATABASE_URL required in production"
    assert env_config.jwt_secret_key, "JWT_SECRET_KEY required in production"
```

### 4. Environment Switching

```bash
# Test different environments
for env in development testing staging production; do
    echo "Testing $env environment:"
    APP_ENV=$env python -c "
from shared.core.config.environment_manager import get_environment_manager
env_manager = get_environment_manager()
print(f'  Environment: {env_manager.environment.value}')
print(f'  Debug: {env_manager.get_config().debug}')
"
done
```

## Migration Guide

### From Old Configuration

1. **Update environment variables**:
   ```bash
   # Old
   export ENVIRONMENT=development
   
   # New
   export APP_ENV=development
   ```

2. **Move configuration to files**:
   ```bash
   # Create config files
   mkdir -p config
   cp old_config.yaml config/development.yaml
   ```

3. **Update imports**:
   ```python
   # Old
   from services.api_gateway.di.config import get_config_manager
   
   # New
   from shared.core.config.environment_manager import get_environment_manager
   from services.api_gateway.di.config import get_config_manager
   ```

### Testing Migration

```bash
# Test old vs new configuration
python scripts/test_configuration_management.py

# Compare configuration loading
python -c "
# Old way
from services.api_gateway.di.config import get_config_manager
old_config = get_config_manager()

# New way
from shared.core.config.environment_manager import get_environment_manager
new_config = get_environment_manager()

print('Migration successful:', old_config is not None and new_config is not None)
"
```

## Conclusion

The new configuration management system provides:

- ✅ **Environment-based configuration** with clear defaults
- ✅ **Secure secrets management** with automatic masking
- ✅ **Configuration validation** with clear error messages
- ✅ **Environment variable precedence** for easy overrides
- ✅ **Comprehensive testing** with validation scripts
- ✅ **Production-ready security** with proper defaults
- ✅ **Easy migration** from existing systems

This system follows MAANG best practices and provides a robust foundation for managing configuration across all environments. 


