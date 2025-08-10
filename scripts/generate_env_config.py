#!/usr/bin/env python3
"""
Environment Configuration Generator for Sarvanom
Generates secure .env and .env.docker files with proper keys and configurations.
"""

import secrets
import os
from pathlib import Path


def generate_secure_keys():
    """Generate secure keys for JWT and Meilisearch."""
    return {
        'jwt_secret': secrets.token_urlsafe(64),
        'meili_master_key': secrets.token_urlsafe(32),
        'session_secret': secrets.token_urlsafe(32),
        'api_key': secrets.token_urlsafe(32)
    }


def create_env_development():
    """Create .env file for development."""
    keys = generate_secure_keys()
    
    env_content = f"""# =============================================================================
# Universal Knowledge Platform - Development Environment Configuration
# =============================================================================
# ⚠️  SECURITY WARNING: This is a development .env file with secure defaults.
# For production, generate new secrets and configure all required variables.
# =============================================================================

# =============================================================================
# 1. CORE APPLICATION SETTINGS
# =============================================================================
APP_ENV=development
APP_NAME=Universal Knowledge Platform
APP_VERSION=1.0.0
APP_DOMAIN=localhost
SERVICE_NAME=sarvanom

# Logging configuration
LOG_LEVEL=DEBUG
DEBUG=true
LOG_FORMAT=text

# =============================================================================
# 2. SECURITY CONFIGURATION
# =============================================================================

# JWT Configuration - SECURE KEYS GENERATED
JWT_SECRET_KEY={keys['jwt_secret']}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Session Configuration
SESSION_SECRET_KEY={keys['session_secret']}

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000

# Security Features
SECURITY_HEADERS_ENABLED=false

# =============================================================================
# 3. DATABASE CONFIGURATION
# =============================================================================

# Primary Database (PostgreSQL)
DATABASE_URL=postgresql://postgres:password@localhost:5432/sarvanom

# Redis Cache
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# =============================================================================
# 4. AI PROVIDER CONFIGURATION
# =============================================================================

# OpenAI Configuration
# OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# Anthropic Configuration
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
ANTHROPIC_MAX_TOKENS=2000

# =============================================================================
# 5. VECTOR DATABASE CONFIGURATION
# =============================================================================

# Qdrant Vector Database
VECTOR_DB_URL=http://localhost:6333
# VECTOR_DB_API_KEY=your_qdrant_api_key_here

# =============================================================================
# 6. SEARCH CONFIGURATION
# =============================================================================

# Meilisearch Configuration - SECURE KEY GENERATED
MEILISEARCH_URL=http://localhost:7700
MEILI_MASTER_KEY={keys['meili_master_key']}

# =============================================================================
# 7. KNOWLEDGE GRAPH CONFIGURATION
# =============================================================================

# ArangoDB Configuration
ARANGODB_URL=http://localhost:8529
ARANGO_URL=http://localhost:8529
ARANGODB_USERNAME=root
ARANGO_USERNAME=root
ARANGODB_PASSWORD=sarvanom123
ARANGO_PASSWORD=sarvanom123
ARANGODB_DATABASE=knowledge_graph

# =============================================================================
# 8. MONITORING & OBSERVABILITY
# =============================================================================

# Metrics and Monitoring
METRICS_ENABLED=true
METRICS_PORT=9090

# Distributed Tracing
ENABLE_TRACING=false
JAEGER_AGENT_HOST=localhost
JAEGER_AGENT_PORT=6831

# Error Tracking
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1

# =============================================================================
# 9. PERFORMANCE & SCALING CONFIGURATION
# =============================================================================

# Rate Limiting
RATE_LIMIT_PER_MINUTE=1000
MAX_REQUEST_SIZE_MB=50

# Caching
CACHE_TTL_SECONDS=1800
SESSION_TTL_SECONDS=3600

# Database Connection Pooling
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30

# Worker Configuration
WORKER_PROCESSES=2
WORKER_THREADS=4
MAX_MEMORY_USAGE_MB=1024

# Agent Configuration
AGENT_TIMEOUT_SECONDS=60
AGENT_MAX_RETRIES=3
AGENT_BACKOFF_FACTOR=2.0

# Query Configuration
QUERY_CACHE_TTL_SECONDS=1800
QUERY_MAX_LENGTH=5000
QUERY_MIN_CONFIDENCE=0.5

# =============================================================================
# 10. DEVELOPMENT FEATURE FLAGS
# =============================================================================

# Development Features
MOCK_AI_RESPONSES=false
SKIP_AUTHENTICATION=false
ENABLE_DEBUG_ENDPOINTS=true
AUTO_RELOAD=true
TEST_MODE=false
MOCK_PROVIDERS=false

# Production Features
BACKUP_ENABLED=false
AUDIT_LOG_ENABLED=true

# =============================================================================
# 11. CACHE CONFIGURATION
# =============================================================================

# Global cache settings
CACHE_ENABLED=true
CACHE_BACKEND=memory
CACHE_DEFAULT_TTL_SECONDS=300
CACHE_MAX_MEMORY_MB=500
CACHE_CLEANUP_INTERVAL_SECONDS=60

# Cache level configurations
CACHE_QUERY_RESULTS_ENABLED=true
CACHE_QUERY_RESULTS_TTL_SECONDS=600
CACHE_EMBEDDINGS_ENABLED=true
CACHE_EMBEDDINGS_TTL_SECONDS=3600
CACHE_LLM_RESPONSES_ENABLED=true
CACHE_LLM_RESPONSES_TTL_SECONDS=300

# =============================================================================
# 12. DEVELOPMENT-SPECIFIC SETTINGS
# =============================================================================

# Hot Reloading
DEV_HOT_RELOAD=true
DEV_DEBUG_SQL=false
DEV_SHOW_ERROR_DETAILS=true
DEV_MOCK_EXTERNAL_APIS=true
DEV_BYPASS_RATE_LIMITS=true

# Health Check Configuration
HEALTH_CHECK_INTERVAL=60
HEALTH_CHECK_TIMEOUT=10

# =============================================================================
# 13. LLM CONFIGURATION
# =============================================================================

# Dynamic model selection
USE_DYNAMIC_SELECTION=true
PRIORITIZE_FREE_MODELS=true

# Local LLM (Ollama)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Timeout settings [[memory:5673626]]
LLM_TIMEOUT_SECONDS=15
API_TIMEOUT_SECONDS=15
"""
    
    return env_content


def create_env_docker():
    """Create .env.docker file for Docker deployments."""
    keys = generate_secure_keys()
    
    env_docker_content = f"""# =============================================================================
# Universal Knowledge Platform - Docker Environment Configuration
# =============================================================================
# This file contains environment variables for Docker Compose deployments
# =============================================================================

# =============================================================================
# 1. CORE APPLICATION SETTINGS
# =============================================================================
APP_ENV=development
APP_NAME=Universal Knowledge Platform
APP_VERSION=1.0.0
SERVICE_NAME=sarvanom

# =============================================================================
# 2. SECURITY CONFIGURATION
# =============================================================================

# JWT Configuration - SECURE KEYS FOR DOCKER
JWT_SECRET_KEY={keys['jwt_secret']}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Session Configuration
SESSION_SECRET_KEY={keys['session_secret']}

# =============================================================================
# 3. DATABASE CONFIGURATION (DOCKER SERVICES)
# =============================================================================

# PostgreSQL (Docker service)
DATABASE_URL=postgresql://postgres:sarvanom123@postgres:5432/sarvanom
POSTGRES_DB=sarvanom
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sarvanom123

# Redis (Docker service)
REDIS_URL=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# =============================================================================
# 4. SEARCH CONFIGURATION (DOCKER SERVICES)
# =============================================================================

# Meilisearch (Docker service) - SECURE KEY GENERATED
MEILISEARCH_URL=http://meilisearch:7700
MEILI_MASTER_KEY={keys['meili_master_key']}
MEILI_ENV=development

# =============================================================================
# 5. VECTOR DATABASE CONFIGURATION (DOCKER SERVICES)
# =============================================================================

# Qdrant (Docker service)
VECTOR_DB_URL=http://qdrant:6333
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# =============================================================================
# 6. KNOWLEDGE GRAPH CONFIGURATION (DOCKER SERVICES)
# =============================================================================

# ArangoDB (Docker service)
ARANGODB_URL=http://arangodb:8529
ARANGO_URL=http://arangodb:8529
ARANGODB_USERNAME=root
ARANGO_USERNAME=root
ARANGODB_PASSWORD=sarvanom123
ARANGO_PASSWORD=sarvanom123
ARANGODB_DATABASE=knowledge_graph

# =============================================================================
# 7. AI PROVIDER CONFIGURATION
# =============================================================================

# OpenAI Configuration
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# Anthropic Configuration
ANTHROPIC_MODEL=claude-3-sonnet-20240229
ANTHROPIC_MAX_TOKENS=2000

# Local LLM (Ollama in Docker)
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama2

# =============================================================================
# 8. LOGGING & MONITORING
# =============================================================================
LOG_LEVEL=INFO
DEBUG=false
METRICS_ENABLED=true

# =============================================================================
# 9. DEVELOPMENT FLAGS
# =============================================================================
MOCK_AI_RESPONSES=false
SKIP_AUTHENTICATION=false
ENABLE_DEBUG_ENDPOINTS=false

# Dynamic model selection
USE_DYNAMIC_SELECTION=true
PRIORITIZE_FREE_MODELS=true

# =============================================================================
# 10. PERFORMANCE SETTINGS
# =============================================================================
CACHE_ENABLED=true
CACHE_BACKEND=redis
WORKER_PROCESSES=2
WORKER_THREADS=4

# Timeout settings [[memory:5673626]]
LLM_TIMEOUT_SECONDS=15
API_TIMEOUT_SECONDS=15
"""
    
    return env_docker_content


def main():
    """Generate environment configuration files."""
    print("🔐 Generating secure environment configuration files...")
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    # Generate .env content
    env_content = create_env_development()
    
    # Generate .env.docker content
    env_docker_content = create_env_docker()
    
    # Print the configurations (since we can't write .env files directly)
    print("\n" + "="*80)
    print("📝 .env FILE CONTENT (Copy this to your .env file):")
    print("="*80)
    print(env_content)
    
    print("\n" + "="*80)
    print("📝 .env.docker FILE CONTENT (Copy this to your .env.docker file):")
    print("="*80)
    print(env_docker_content)
    
    print("\n" + "="*80)
    print("✅ SECURE CONFIGURATION GENERATED!")
    print("="*80)
    print("📋 Next steps:")
    print("1. Copy the above content to .env and .env.docker files")
    print("2. Add your API keys (OpenAI, Anthropic, etc.) if needed")
    print("3. Adjust any environment-specific settings")
    print("4. Run 'docker-compose up' to start services")
    print("\n🔐 All keys are cryptographically secure and unique!")


if __name__ == "__main__":
    main()
