#!/usr/bin/env python3
"""
Create comprehensive .env.example file for SarvanOM project.

This script generates a complete .env.example file with all possible
environment variables, their descriptions, and default values.
"""

import os
from pathlib import Path

def create_env_example():
    """Create comprehensive .env.example file."""
    
    env_content = """# =============================================================================
# SarvanOM Environment Configuration Template
# =============================================================================
# 
# Copy this file to .env and fill in your actual values.
# NEVER commit .env files to version control - they contain secrets!
#
# This template includes all possible environment variables.
# Required variables are marked with [REQUIRED].
# Optional variables have default values shown.

# =============================================================================
# 1. CORE APPLICATION SETTINGS
# =============================================================================

# Application Environment [REQUIRED]
APP_ENV=development  # development, testing, staging, production
DEBUG=true  # Set to false in production
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
TESTING=false

# Application Metadata
APP_NAME=Universal Knowledge Platform
APP_VERSION=2.4.0
SERVICE_NAME=sarvanom-backend

# =============================================================================
# 2. SECURITY CONFIGURATION
# =============================================================================

# JWT Settings [REQUIRED for production]
JWT_SECRET_KEY=your-super-secret-jwt-key-here-minimum-32-characters
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000
CORS_CREDENTIALS=true

# Security Features
SECURITY_HEADERS_ENABLED=true
ENABLE_API_KEYS=true

# =============================================================================
# 3. DATABASE CONFIGURATION
# =============================================================================

# Primary Database [REQUIRED]
DATABASE_URL=postgresql://postgres:password@localhost:5432/sarvanom
# Alternative formats:
# DATABASE_URL=mysql://user:pass@localhost:3306/sarvanom
# DATABASE_URL=sqlite:///dev.db

# Database Connection Pooling
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30

# PostgreSQL Specific (if not using DATABASE_URL)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sarvanom
DB_USER=postgres
DB_PASSWORD=password

# =============================================================================
# 4. CACHE CONFIGURATION
# =============================================================================

# Redis [REQUIRED]
REDIS_URL=redis://localhost:6379/0
# Alternative formats:
# REDIS_URL=redis://user:pass@localhost:6379/0
# REDIS_URL=rediss://user:pass@localhost:6379/0  # SSL

# Redis Specific (if not using REDIS_URL)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Cache Settings
CACHE_TTL_DEFAULT=300
CACHE_TTL_USER=600
CACHE_TTL_QUERY=3600
REDIS_POOL_SIZE=10

# =============================================================================
# 5. AI PROVIDER CONFIGURATION
# =============================================================================

# OpenAI [Optional - for OpenAI models]
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_ORGANIZATION=org-your-organization-id
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Anthropic [Optional - for Claude models]
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
ANTHROPIC_MAX_TOKENS=2000
ANTHROPIC_TEMPERATURE=0.7

# Hugging Face [Optional - for free models]
HUGGINGFACE_WRITE_TOKEN=hf-your-write-token-here
HUGGINGFACE_READ_TOKEN=hf-your-read-token-here
HUGGINGFACE_API_KEY=hf-your-api-key-here
HUGGINGFACE_MODEL=microsoft/DialoGPT-medium

# Ollama [Optional - for local models]
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Model Selection
USE_DYNAMIC_SELECTION=true
PRIORITIZE_FREE_MODELS=true

# =============================================================================
# 6. VECTOR DATABASE CONFIGURATION
# =============================================================================

# Vector Database Provider
VECTOR_DB_PROVIDER=qdrant  # qdrant, pinecone, weaviate, milvus, meilisearch

# Qdrant [Default]
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_COLLECTION=sarvanom_vectors
QDRANT_PORT=6333

# Pinecone [Alternative]
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=saravanom-pinecone

# Vector Database Generic
VECTOR_DB_URL=http://localhost:6333
VECTOR_DB_API_KEY=

# Embedding Settings
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536

# =============================================================================
# 7. SEARCH CONFIGURATION
# =============================================================================

# MeiliSearch [REQUIRED]
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_MASTER_KEY=your-meilisearch-master-key-here
MEILISEARCH_API_KEY=
MEILISEARCH_INDEX=knowledge_base

# Elasticsearch [Optional]
ELASTICSEARCH_URL=http://localhost:9200

# =============================================================================
# 8. KNOWLEDGE GRAPH CONFIGURATION
# =============================================================================

# ArangoDB [REQUIRED]
ARANGODB_URL=http://localhost:8529
ARANGODB_USERNAME=root
ARANGODB_PASSWORD=
ARANGODB_DATABASE=knowledge_graph

# SPARQL Endpoint [Optional]
SPARQL_ENDPOINT=http://localhost:7200/repositories/knowledge

# =============================================================================
# 9. MICROSERVICES CONFIGURATION
# =============================================================================

# Service URLs (for microservices architecture)
AUTH_SERVICE_URL=http://localhost:8001
SEARCH_SERVICE_URL=http://localhost:8002
SYNTHESIS_SERVICE_URL=http://localhost:8003
FACTCHECK_SERVICE_URL=http://localhost:8004
ANALYTICS_SERVICE_URL=http://localhost:8005

# Service Secrets
AUTH_SERVICE_SECRET=
SEARCH_SERVICE_SECRET=
SYNTHESIS_SERVICE_SECRET=
FACTCHECK_SERVICE_SECRET=
ANALYTICS_SERVICE_SECRET=

# =============================================================================
# 10. PERFORMANCE & RATE LIMITING
# =============================================================================

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
MAX_REQUEST_SIZE_MB=10

# Agent Settings
AGENT_TIMEOUT_SECONDS=30
AGENT_MAX_RETRIES=3
AGENT_BACKOFF_FACTOR=2.0

# Query Settings
QUERY_CACHE_TTL_SECONDS=3600
QUERY_MAX_LENGTH=2000
QUERY_MIN_CONFIDENCE=0.7

# Worker Settings
WORKER_PROCESSES=2
WORKER_THREADS=2
MAX_MEMORY_USAGE_MB=1024
GARBAGE_COLLECTION_INTERVAL=300

# =============================================================================
# 11. MONITORING & OBSERVABILITY
# =============================================================================

# Metrics
METRICS_ENABLED=true
METRICS_PORT=9090

# Tracing
ENABLE_TRACING=false
JAEGER_AGENT_HOST=localhost
JAEGER_AGENT_PORT=6831

# Sentry [Optional]
SENTRY_DSN=your-sentry-dsn-here
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1

# Health Checks
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10

# =============================================================================
# 12. FEATURE FLAGS
# =============================================================================

# Development Features
MOCK_AI_RESPONSES=true
SKIP_AUTHENTICATION=true
ENABLE_DEBUG_ENDPOINTS=true
AUTO_RELOAD=true
TEST_MODE=false
MOCK_PROVIDERS=true

# Production Features
BACKUP_ENABLED=true
AUDIT_LOG_ENABLED=true
SECURITY_HEADERS_ENABLED=true

# =============================================================================
# 13. EXTERNAL INTEGRATIONS
# =============================================================================

# SMTP (for email notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true

# File Storage
STORAGE_TYPE=local  # local, s3, gcs
STORAGE_BUCKET=sarvanom-uploads

# =============================================================================
# 14. DOCKER CONFIGURATION
# =============================================================================

# Docker Settings
DOCKER_ENABLED=true
DOCKER_NETWORK=sarvanom-network

# Docker Service URLs
BACKEND_URL=http://sarvanom_backend:8000
POSTGRES_URL=postgresql://postgres:password@postgres:5432/sarvanom_db
REDIS_URL=redis://redis:6379/0
MEILISEARCH_URL=http://meilisearch:7700
ARANGODB_URL=http://arangodb:8529
QDRANT_URL=http://qdrant:6333
OLLAMA_URL=http://ollama:11434

# =============================================================================
# 15. CIRCUIT BREAKER SETTINGS
# =============================================================================

# Circuit Breaker Configuration
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60

# Connection Pool Settings
MAX_CONNECTIONS=100
MAX_KEEPALIVE_TIME=300

# =============================================================================
# 16. SESSION & CACHE SETTINGS
# =============================================================================

# Session Management
SESSION_TTL_SECONDS=86400  # 24 hours
CACHE_TTL_SECONDS=3600  # 1 hour

# =============================================================================
# NOTES
# =============================================================================
#
# 1. For production deployment:
#    - Set APP_ENV=production
#    - Set DEBUG=false
#    - Set LOG_LEVEL=WARNING
#    - Ensure all [REQUIRED] variables are set
#    - Use strong, unique secrets for JWT_SECRET_KEY
#    - Use SSL/TLS for all database connections
#
# 2. For development:
#    - Most defaults are suitable
#    - Mock providers can be enabled for testing
#    - Debug endpoints can be enabled
#
# 3. For testing:
#    - Set APP_ENV=testing
#    - Use in-memory databases where possible
#    - Enable mock providers
#
# 4. Security checklist:
#    - [ ] JWT_SECRET_KEY is set and secure
#    - [ ] Database passwords are strong
#    - [ ] API keys are valid and have appropriate permissions
#    - [ ] CORS origins are properly configured
#    - [ ] No secrets are committed to version control
#
# 5. Performance tuning:
#    - Adjust pool sizes based on your infrastructure
#    - Monitor memory usage and adjust MAX_MEMORY_USAGE_MB
#    - Tune rate limits based on expected load
#    - Configure appropriate timeouts for your network
"""
    
    # Write to .env.example
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Created comprehensive .env.example file")
    print("📝 Copy this file to .env and fill in your actual values")
    print("🔒 Remember: NEVER commit .env files to version control!")

if __name__ == "__main__":
    create_env_example() 