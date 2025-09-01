"""
Central Configuration Management - Eliminates Hard-coded Values.

This module provides a unified configuration system that loads all settings
from environment variables or configuration files, eliminating hard-coded
values throughout the codebase.

Features:
    - Environment-based configuration loading
    - Type-safe configuration with validation
    - Secure secrets management
    - Centralized default values
    - Configuration hot-reloading
    - Environment-specific overrides

Security:
    - No hard-coded secrets
    - Environment variable precedence
    - Secure defaults for development
    - Configuration validation

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    1.0.0 (2024-12-28)
"""

import os
import json
import secrets
import hashlib
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, ClassVar
from functools import lru_cache
from enum import Enum
from datetime import datetime, timezone
import warnings

from pydantic import (
    Field,
    field_validator,
    model_validator,
    SecretStr,
    HttpUrl,
    PostgresDsn,
    RedisDsn,
    conint,
    confloat,
    ValidationInfo,
    ConfigDict,
)
from pydantic_settings import BaseSettings
import structlog

logger = structlog.get_logger(__name__)


class Environment(str, Enum):
    """Application environment types."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

    @classmethod
    def from_string(cls, env: str) -> "Environment":
        """Create Environment from string."""
        try:
            return cls(env.lower())
        except ValueError:
            logger.warning(f"Unknown environment '{env}', defaulting to development")
            return cls.DEVELOPMENT


class SecretVaultType(str, Enum):
    """Types of secret vaults supported."""
    ENVIRONMENT = "environment"  # Environment variables (default)
    FILE = "file"  # Encrypted file storage
    AZURE_KEYVAULT = "azure_keyvault"
    AWS_SECRETS = "aws_secrets"
    HASHICORP_VAULT = "hashicorp_vault"


class LogLevel(str, Enum):
    """Logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    @classmethod
    def from_string(cls, level: str) -> "LogLevel":
        """Create LogLevel from string (case-insensitive)."""
        try:
            return cls(level.upper())
        except ValueError:
            logger.warning(f"Unknown log level '{level}', defaulting to INFO")
            return cls.INFO


# Custom types
Port = conint(ge=1, le=65535)
Percentage = confloat(ge=0.0, le=1.0)


class ConfigurationAuditor:
    """Audits configuration changes for security compliance."""
    
    def __init__(self, audit_file: str = "logs/config_audit.jsonl"):
        self.audit_file = Path(audit_file)
        self.audit_file.parent.mkdir(exist_ok=True)
    
    def log_access(self, config_key: str, environment: str, access_type: str):
        """Log configuration access."""
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": environment,
            "config_key": config_key,
            "access_type": access_type,
            "process_id": os.getpid(),
        }
        
        with open(self.audit_file, "a") as f:
            f.write(json.dumps(audit_entry) + "\n")
    
    def log_change(self, config_key: str, environment: str, old_value_hash: str, new_value_hash: str):
        """Log configuration changes."""
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": environment,
            "config_key": config_key,
            "change_type": "update",
            "old_value_hash": old_value_hash,
            "new_value_hash": new_value_hash,
            "process_id": os.getpid(),
        }
        
        with open(self.audit_file, "a") as f:
            f.write(json.dumps(audit_entry) + "\n")


class SecureSettings(BaseSettings):
    """Base settings with security features."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Custom JSON encoders for security - removed for Pydantic V2 compatibility
        # Use model_serializer instead
    )

    def dict(self, **kwargs) -> Dict[str, Any]:
        """Convert to dictionary with optional secret masking."""
        include_secrets = kwargs.pop("include_secrets", False)
        data = super().dict(**kwargs)

        if not include_secrets:
            data = self._mask_secrets(data)

        return data

    def _mask_secrets(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive values in configuration."""
        secret_fields = [
            "jwt_secret_key",
            "openai_api_key",
            "anthropic_api_key",
            "vector_db_api_key",
            "meilisearch_master_key",
            "arangodb_password",
            "redis_password",
            "postgres_password",
            "sentry_dsn",
            "aws_access_key_id",
            "aws_secret_access_key",
            "smtp_password",
        ]

        for field in secret_fields:
            if field in data and data[field]:
                data[field] = "***REDACTED***"

        return data
    
    def _hash_value(self, value: str) -> str:
        """Create hash of value for auditing (not storing the actual value)."""
        return hashlib.sha256(value.encode()).hexdigest()[:16]

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Override model_dump to mask secrets."""
        d = super().model_dump(**kwargs)
        return self._mask_secrets(d)


class CentralConfig(SecureSettings):
    """
    Central configuration that eliminates all hard-coded values.

    This configuration class loads all settings from environment variables
    and provides secure defaults for development environments.
    """

    # =============================================================================
    # 1. CORE APPLICATION SETTINGS
    # =============================================================================

    # Environment and metadata
    environment: Environment = Field(
        default=Environment.DEVELOPMENT, description="Application environment"
    )
    app_name: str = Field(
        default="Universal Knowledge Platform", description="Application name"
    )
    app_version: str = Field(default="1.0.0", description="Application version")
    service_name: str = Field(default="sarvanom-backend", description="Service name")

    # Debug and logging
    debug: bool = Field(default=False, description="Debug mode")
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    log_format: str = Field(default="json", description="Log format")
    log_file: Optional[Path] = Field(default=None, description="Log file path")

    @field_validator("log_level", mode="before")
    @classmethod
    def validate_log_level(cls, v: Any) -> LogLevel:
        """Validate and convert log level to proper case."""
        if isinstance(v, str):
            return LogLevel.from_string(v)
        return v

    # =============================================================================
    # 2. SECURITY CONFIGURATION
    # =============================================================================

    # JWT settings
    jwt_secret_key: SecretStr = Field(
        default_factory=lambda: SecretStr(secrets.token_urlsafe(32)),
        description="JWT signing key",
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: conint(ge=1) = Field(
        default=30, description="Access token expiration"
    )
    jwt_refresh_token_expire_days: conint(ge=1) = Field(
        default=30, description="Refresh token expiration"
    )

    # CORS settings
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ],
        description="Allowed CORS origins",
    )
    cors_credentials: bool = Field(
        default=True, description="Allow credentials in CORS"
    )

    # Security features
    security_headers_enabled: bool = Field(
        default=True, description="Enable security headers"
    )
    enable_api_keys: bool = Field(
        default=True, description="Enable API key authentication"
    )
    
    # Enhanced security features (from enhanced_config.py)
    secret_vault_type: SecretVaultType = Field(
        default=SecretVaultType.ENVIRONMENT, description="Secret vault type"
    )
    audit_enabled: bool = Field(
        default=True, description="Enable configuration auditing"
    )
    rotate_secrets: bool = Field(
        default=False, description="Enable secret rotation"
    )
    max_requests_per_minute: conint(ge=1) = Field(
        default=60, description="Max requests per minute"
    )
    max_tokens_per_minute: conint(ge=1) = Field(
        default=10000, description="Max tokens per minute"
    )
    enable_rate_limiting: bool = Field(
        default=True, description="Enable rate limiting"
    )
    enable_security_scanning: bool = Field(
        default=True, description="Enable security scanning"
    )
    blocked_keywords: List[str] = Field(
        default_factory=lambda: ["malicious", "attack", "exploit"], 
        description="Blocked keywords"
    )

    # =============================================================================
    # 3. DATABASE CONFIGURATION
    # =============================================================================

    # Primary database
    database_url: Optional[str] = Field(
        default=None, description="Database connection URL"
    )
    postgres_host: str = Field(default="localhost", description="PostgreSQL host")
    postgres_port: Port = Field(default=5432, description="PostgreSQL port")
    postgres_db: str = Field(default="sarvanom", description="PostgreSQL database")
    postgres_user: str = Field(default="postgres", description="PostgreSQL username")
    postgres_password: Optional[SecretStr] = Field(
        default=None, description="PostgreSQL password"
    )

    # Database connection pooling
    database_pool_size: conint(ge=1) = Field(default=20, description="DB pool size")
    database_max_overflow: conint(ge=0) = Field(
        default=10, description="DB max overflow"
    )
    database_pool_timeout: conint(ge=1) = Field(
        default=30, description="DB pool timeout"
    )

    # =============================================================================
    # 4. CACHE CONFIGURATION
    # =============================================================================

    # Redis settings
    redis_url: Optional[RedisDsn] = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )
    redis_password: Optional[SecretStr] = Field(
        default=None, description="Redis password"
    )
    redis_pool_size: conint(ge=1) = Field(default=10, description="Redis pool size")

    # Cache TTL settings
    cache_ttl_default: conint(ge=0) = Field(
        default=300, description="Default cache TTL"
    )
    cache_ttl_user: conint(ge=0) = Field(default=600, description="User cache TTL")
    cache_ttl_query: conint(ge=0) = Field(default=3600, description="Query cache TTL")

    # =============================================================================
    # 5. AI PROVIDER CONFIGURATION
    # =============================================================================

    # OpenAI
    openai_api_key: Optional[SecretStr] = Field(
        default=None, description="OpenAI API key"
    )
    openai_organization: Optional[str] = Field(
        default=None, description="OpenAI organization ID"
    )
    openai_model: str = Field(default="gpt-4o-mini", description="Default OpenAI model")
    openai_max_tokens: conint(ge=1) = Field(default=2000, description="Max tokens")
    openai_temperature: confloat(ge=0.0, le=2.0) = Field(
        default=0.7, description="Temperature"
    )
    openai_embedding_model: str = Field(
        default="text-embedding-3-small", description="OpenAI embedding model"
    )

    # Anthropic
    anthropic_api_key: Optional[SecretStr] = Field(
        default=None, description="Anthropic API key"
    )
    anthropic_model: str = Field(
        default="claude-3-haiku-20240307", description="Default Anthropic model"
    )

    # Azure OpenAI
    azure_openai_api_key: Optional[SecretStr] = Field(
        default=None, description="Azure OpenAI API key"
    )
    azure_openai_endpoint: Optional[HttpUrl] = Field(
        default=None, description="Azure OpenAI endpoint"
    )
    azure_openai_deployment_name: Optional[str] = Field(
        default=None, description="Azure OpenAI deployment name"
    )

    # Google AI
    google_api_key: Optional[SecretStr] = Field(
        default=None, description="Google AI API key"
    )
    google_model: str = Field(default="gemini-pro", description="Default Google model")

    # Ollama (Local Models - FREE)
    ollama_enabled: bool = Field(default=True, description="Enable Ollama provider")
    ollama_base_url: HttpUrl = Field(
        default="http://localhost:11434", description="Ollama server URL"
    )
    ollama_model: str = Field(default="llama3.2:3b", description="Default Ollama model")

    # Hugging Face (API Models - FREE)
    huggingface_write_token: Optional[SecretStr] = Field(
        default=None, description="Hugging Face write token"
    )
    huggingface_read_token: Optional[SecretStr] = Field(
        default=None, description="Hugging Face read token"
    )
    huggingface_api_key: Optional[SecretStr] = Field(
        default=None, description="Hugging Face API key (legacy)"
    )
    huggingface_model: str = Field(
        default="microsoft/DialoGPT-medium", description="Default Hugging Face model"
    )

    # Model Selection Configuration
    use_dynamic_selection: bool = Field(
        default=True, description="Enable dynamic model selection"
    )
    prioritize_free_models: bool = Field(
        default=True, description="Prioritize free models"
    )

    # =============================================================================
    # 6. VECTOR DATABASE CONFIGURATION
    # =============================================================================

    # Qdrant
    qdrant_url: HttpUrl = Field(
        default="http://localhost:6333", description="Qdrant server URL"
    )
    qdrant_api_key: Optional[SecretStr] = Field(
        default=None, description="Qdrant API key"
    )
    qdrant_collection: str = Field(
        default="sarvanom_vectors", description="Qdrant collection name"
    )
    qdrant_port: Port = Field(default=6333, description="Qdrant port")

    # Pinecone
    pinecone_api_key: Optional[SecretStr] = Field(
        default=None, description="Pinecone API key"
    )
    pinecone_environment: str = Field(
        default="us-east-1", description="Pinecone environment"
    )
    pinecone_index_name: str = Field(
        default="saravanom-pinecone", description="Pinecone index name"
    )

    # Vector database provider
    vector_db_provider: str = Field(default="inmemory", description="Vector DB provider")
    use_vector_db: bool = Field(default=False, description="Enable vector database")
    vector_db_url: Optional[HttpUrl] = Field(
        default="http://localhost:6333", description="Vector database URL"
    )
    vector_db_api_key: Optional[SecretStr] = Field(
        default=None, description="Vector DB API key"
    )

    # Embedding settings
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", description="Embedding model"
    )
    embedding_dimension: conint(ge=1) = Field(
        default=384, description="Embedding dimension"
    )

    # =============================================================================
    # 7. SEARCH CONFIGURATION
    # =============================================================================

    # MeiliSearch
    meilisearch_url: HttpUrl = Field(
        default="http://localhost:7700", description="MeiliSearch server URL"
    )
    meilisearch_master_key: Optional[SecretStr] = Field(
        default=None, description="MeiliSearch master key"
    )
    meilisearch_api_key: Optional[SecretStr] = Field(
        default=None, description="MeiliSearch API key"
    )
    meilisearch_index: str = Field(
        default="sarvanom_documents", description="MeiliSearch index name"
    )

    # =============================================================================
    # 8. KNOWLEDGE GRAPH CONFIGURATION
    # =============================================================================

    # ArangoDB
    arango_url: HttpUrl = Field(
        default="http://localhost:8529", description="ArangoDB server URL"
    )
    arango_username: str = Field(default="root", description="ArangoDB username")
    arango_password: Optional[SecretStr] = Field(
        default=None, description="ArangoDB password"
    )
    arango_database: str = Field(
        default="knowledge_graph", description="ArangoDB database name"
    )
    arango_host: str = Field(default="localhost", description="ArangoDB host")
    arango_port: Port = Field(default=8529, description="ArangoDB port")

    # GraphDB/Neo4j
    sparql_endpoint: HttpUrl = Field(
        default="http://localhost:7200/repositories/knowledge",
        description="SPARQL endpoint URL",
    )

    # =============================================================================
    # 9. MONITORING & OBSERVABILITY
    # =============================================================================

    # Metrics
    metrics_enabled: bool = Field(default=True, description="Enable Prometheus metrics")
    metrics_port: Port = Field(default=9090, description="Metrics port")

    # Tracing
    enable_tracing: bool = Field(
        default=False, description="Enable distributed tracing"
    )
    jaeger_agent_host: str = Field(default="localhost", description="Jaeger agent host")
    jaeger_agent_port: Port = Field(default=6831, description="Jaeger agent port")

    # Sentry
    sentry_dsn: Optional[SecretStr] = Field(default=None, description="Sentry DSN")
    sentry_traces_sample_rate: Percentage = Field(
        default=0.1, description="Sentry traces sample rate"
    )
    sentry_profiles_sample_rate: Percentage = Field(
        default=0.1, description="Sentry profiles sample rate"
    )

    # Health checks
    health_check_interval: conint(ge=1) = Field(
        default=30, description="Health check interval"
    )
    health_check_timeout: conint(ge=1) = Field(
        default=10, description="Health check timeout"
    )

    # =============================================================================
    # 10. MICROSERVICES CONFIGURATION
    # =============================================================================

    # Service URLs
    auth_service_url: HttpUrl = Field(
        default="http://localhost:8001", description="Auth service URL"
    )
    search_service_url: HttpUrl = Field(
        default="http://localhost:8002", description="Search service URL"
    )
    synthesis_service_url: HttpUrl = Field(
        default="http://localhost:8003", description="Synthesis service URL"
    )
    factcheck_service_url: HttpUrl = Field(
        default="http://localhost:8004", description="Fact-check service URL"
    )
    analytics_service_url: HttpUrl = Field(
        default="http://localhost:8005", description="Analytics service URL"
    )

    # Service secrets
    auth_service_secret: SecretStr = Field(
        default_factory=lambda: SecretStr(secrets.token_urlsafe(32)),
        description="Auth service secret",
    )
    search_service_secret: SecretStr = Field(
        default_factory=lambda: SecretStr(secrets.token_urlsafe(32)),
        description="Search service secret",
    )
    synthesis_service_secret: SecretStr = Field(
        default_factory=lambda: SecretStr(secrets.token_urlsafe(32)),
        description="Synthesis service secret",
    )
    factcheck_service_secret: SecretStr = Field(
        default_factory=lambda: SecretStr(secrets.token_urlsafe(32)),
        description="Fact-check service secret",
    )
    analytics_service_secret: SecretStr = Field(
        default_factory=lambda: SecretStr(secrets.token_urlsafe(32)),
        description="Analytics service secret",
    )

    # =============================================================================
    # 11. AGENT CONFIGURATION
    # =============================================================================

    # Agent timeout and retry settings
    agent_timeout_seconds: conint(ge=1) = Field(
        default=30, description="Agent timeout in seconds"
    )
    agent_max_retries: conint(ge=0) = Field(default=3, description="Agent max retries")
    agent_backoff_factor: confloat(ge=1.0) = Field(
        default=2.0, description="Agent backoff factor"
    )

    # Query processing
    query_cache_ttl_seconds: conint(ge=0) = Field(
        default=3600, description="Query cache TTL"
    )
    query_max_length: conint(ge=1) = Field(default=2000, description="Query max length")
    query_min_confidence: confloat(ge=0.0, le=1.0) = Field(
        default=0.7, description="Query min confidence"
    )

    # Agent settings
    enable_reviewer_agent: bool = Field(
        default=True, description="Enable expert reviewer agent"
    )
    reviewer_model: str = Field(
        default="",
        description="Specific model for reviewer agent (empty = use default)",
    )
    reviewer_temperature: float = Field(
        default=0.2, description="Temperature for reviewer agent"
    )
    reviewer_max_tokens: int = Field(
        default=800, description="Max tokens for reviewer agent"
    )
    reviewer_timeout_seconds: int = Field(
        default=45, description="Timeout for reviewer agent"
    )

    # =============================================================================
    # 12. PERFORMANCE & SCALING
    # =============================================================================

    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_per_minute: conint(ge=1) = Field(
        default=60, description="Rate limit per minute"
    )
    rate_limit_burst: conint(ge=1) = Field(default=10, description="Burst allowance")

    # Request limits
    max_request_size_mb: conint(ge=1) = Field(
        default=10, description="Max request size in MB"
    )
    request_timeout: conint(ge=1) = Field(default=30, description="Request timeout")

    # Worker configuration
    worker_processes: conint(ge=1) = Field(default=2, description="Worker processes")
    worker_threads: conint(ge=1) = Field(default=2, description="Worker threads")
    max_memory_usage_mb: conint(ge=1) = Field(
        default=1024, description="Max memory usage in MB"
    )

    # =============================================================================
    # 13. FEATURE FLAGS
    # =============================================================================

    # Development features
    mock_ai_responses: bool = Field(default=False, description="Mock AI responses")
    skip_authentication: bool = Field(default=False, description="Skip authentication")
    enable_debug_endpoints: bool = Field(
        default=False, description="Enable debug endpoints"
    )
    auto_reload: bool = Field(default=False, description="Auto reload")
    test_mode: bool = Field(default=False, description="Test mode")
    mock_providers: bool = Field(default=False, description="Mock providers")

    # Production features
    backup_enabled: bool = Field(default=True, description="Enable backups")
    audit_log_enabled: bool = Field(default=True, description="Enable audit logging")

    # Feature flags
    features: Dict[str, bool] = Field(
        default_factory=lambda: {
            "streaming": True,
            "batch_processing": True,
            "websockets": True,
            "graphql": False,
            "admin_panel": True,
            "expert_review": True,
            "real_time_collaboration": True,
            "advanced_analytics": True,
            "multi_tenant": True,
            "sso": True,
        },
        description="Feature flags",
    )

    # =============================================================================
    # 14. EXTERNAL INTEGRATIONS
    # =============================================================================

    # Web Search APIs
    brave_search_api_key: Optional[SecretStr] = Field(
        default=None, description="Brave Search API key"
    )
    serpapi_key: Optional[SecretStr] = Field(default=None, description="SerpAPI key")
    searchapi_key: Optional[SecretStr] = Field(
        default=None, description="SearchAPI key"
    )

    # Email service
    smtp_host: str = Field(default="smtp.gmail.com", description="SMTP host")
    smtp_port: Port = Field(default=587, description="SMTP port")
    smtp_username: Optional[str] = Field(default=None, description="SMTP username")
    smtp_password: Optional[SecretStr] = Field(
        default=None, description="SMTP password"
    )
    smtp_use_tls: bool = Field(default=True, description="SMTP use TLS")

    # AWS S3
    aws_access_key_id: Optional[SecretStr] = Field(
        default=None, description="AWS access key ID"
    )
    aws_secret_access_key: Optional[SecretStr] = Field(
        default=None, description="AWS secret access key"
    )
    aws_region: str = Field(default="us-west-1", description="AWS region")

    # =============================================================================
    # VALIDATION METHODS
    # =============================================================================

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("features", mode="before")
    @classmethod
    def parse_features(cls, v: Union[str, Dict[str, bool]]) -> Dict[str, bool]:
        """Parse features from string or dict."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                logger.warning(f"Invalid features JSON: {v}")
                return {}
        return v

    @field_validator("vector_db_provider")
    @classmethod
    def validate_vector_provider(cls, v: str) -> str:
        """Validate vector database provider."""
        valid_providers = ["qdrant", "pinecone", "weaviate", "milvus"]
        if v not in valid_providers:
            logger.warning(f"Invalid vector provider '{v}', using qdrant")
            return "qdrant"
        return v

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate environment-specific configuration."""
        env = values.get("environment", Environment.DEVELOPMENT)

        # Development environment overrides
        if env == Environment.DEVELOPMENT:
            if "debug" not in values:
                values["debug"] = True
            if "log_level" not in values:
                values["log_level"] = LogLevel.DEBUG
            if "mock_ai_responses" not in values:
                values["mock_ai_responses"] = True
            if "skip_authentication" not in values:
                values["skip_authentication"] = True

        # Production environment validation
        elif env == Environment.PRODUCTION:
            if not values.get("jwt_secret_key"):
                raise ValueError("JWT_SECRET_KEY is required in production")
            if not values.get("database_url"):
                raise ValueError("DATABASE_URL is required in production")
            if not values.get("redis_url"):
                raise ValueError("REDIS_URL is required in production")

        return values

    # =============================================================================
    # UTILITY METHODS
    # =============================================================================

    def get_feature(self, feature: str) -> bool:
        """Get feature flag value."""
        return self.features.get(feature, False)

    def to_dict(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Convert to dictionary with optional secret masking."""
        return self.dict(include_secrets=include_secrets)

    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []

        # Check required production settings
        if self.environment == Environment.PRODUCTION:
            if not self.jwt_secret_key:
                issues.append("JWT_SECRET_KEY is required in production")
            if not self.database_url:
                issues.append("DATABASE_URL is required in production")
            if not self.redis_url:
                issues.append("REDIS_URL is required in production")

        # Check AI provider configuration
        if not any(
            [
                self.openai_api_key,
                self.anthropic_api_key,
                self.azure_openai_api_key,
                self.google_api_key,
                self.huggingface_api_key,
                self.ollama_enabled,
            ]
        ):
            issues.append("At least one AI provider must be configured")

        # Check vector database configuration
        if not self.vector_db_url and not self.qdrant_url:
            issues.append("Vector database URL is required")

        return issues

    def get_missing_critical_config(self) -> List[str]:
        """Get list of missing critical configuration items."""
        return self.validate_config()

    def print_startup_config(self) -> None:
        """Print startup configuration summary."""
        logger.info("=== Configuration Summary ===")
        logger.info(f"Environment: {self.environment}")
        logger.info(f"Debug Mode: {self.debug}")
        logger.info(f"Log Level: {self.log_level}")
        logger.info(
            f"Database URL: {'Configured' if self.database_url else 'Not configured'}"
        )
        logger.info(
            f"Redis URL: {'Configured' if self.redis_url else 'Not configured'}"
        )
        logger.info(f"AI Providers: {self._get_configured_ai_providers()}")
        logger.info(f"Vector DB: {self.vector_db_provider}")
        logger.info(
            f"MeiliSearch: {'Configured' if self.meilisearch_url else 'Not configured'}"
        )
        logger.info(
            f"ArangoDB: {'Configured' if self.arango_url else 'Not configured'}"
        )

        # Check for issues
        issues = self.validate_config()
        if issues:
            logger.warning("Configuration issues found:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        else:
            logger.info("Configuration validation passed")

    def _get_configured_ai_providers(self) -> List[str]:
        """Get list of configured AI providers."""
        providers = []
        if self.openai_api_key:
            providers.append("OpenAI")
        if self.anthropic_api_key:
            providers.append("Anthropic")
        if self.azure_openai_api_key:
            providers.append("Azure OpenAI")
        if self.google_api_key:
            providers.append("Google AI")
        if self.huggingface_api_key or self.huggingface_read_token:
            providers.append("Hugging Face")
        if self.ollama_enabled:
            providers.append("Ollama")

        return providers if providers else ["None"]
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration with secret management."""
        return {
            "openai_api_key": self.openai_api_key.get_secret_value() if self.openai_api_key else None,
            "anthropic_api_key": self.anthropic_api_key.get_secret_value() if self.anthropic_api_key else None,
            "huggingface_api_key": self.huggingface_api_key.get_secret_value() if self.huggingface_api_key else None,
            "ollama_base_url": str(self.ollama_base_url),
            "prioritize_free_models": self.prioritize_free_models,
            "use_dynamic_selection": self.use_dynamic_selection,
            "llm_timeout_seconds": self.agent_timeout_seconds,
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return {
            "max_requests_per_minute": self.max_requests_per_minute,
            "max_tokens_per_minute": self.max_tokens_per_minute,
            "enable_rate_limiting": self.enable_rate_limiting,
            "enable_security_scanning": self.enable_security_scanning,
            "blocked_keywords": self.blocked_keywords,
            "jwt_secret_key": self.jwt_secret_key.get_secret_value() if self.jwt_secret_key else None,
        }
    
    def get_analytics_config(self) -> Dict[str, Any]:
        """Get analytics configuration."""
        return {
            "anonymize_queries": True,  # Default for privacy
            "retention_hours": 24,  # Default retention
            "enable_performance_monitoring": self.metrics_enabled,
            "log_query_content": False,  # Default for privacy
        }
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration and return status."""
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "missing_critical": []
        }
        
        # Check critical secrets
        critical_secrets = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
        for secret in critical_secrets:
            if not getattr(self, secret.lower(), None):
                validation_results["warnings"].append(f"Missing optional secret: {secret}")
        
        # Check security configuration
        if not self.jwt_secret_key and self.environment == Environment.PRODUCTION:
            validation_results["errors"].append("JWT_SECRET_KEY required in production")
            validation_results["valid"] = False
        
        # Check rate limiting configuration
        if self.max_requests_per_minute > 1000 and self.environment == Environment.PRODUCTION:
            validation_results["warnings"].append("Very high rate limit detected")
        
        return validation_results
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get comprehensive environment information."""
        return {
            "environment": self.environment.value,
            "configuration_valid": self.validate_configuration()["valid"],
            "secret_vault_type": self.secret_vault_type.value,
            "audit_enabled": self.audit_enabled,
            "timestamp": datetime.now().isoformat()
        }

    model_config = ConfigDict(
        # Environment variable prefix
        env_prefix="UKP_",
        # Allow extra fields for forward compatibility
        extra="ignore",
        # Validate on assignment
        validate_assignment=True,
    )


# =============================================================================
# GLOBAL CONFIGURATION INSTANCE
# =============================================================================


@lru_cache(maxsize=1)
def get_central_config() -> CentralConfig:
    """Get cached central configuration instance."""
    return CentralConfig()


# REMOVED: reload_central_config function - unused


# =============================================================================
# CONFIGURATION HELPERS
# =============================================================================


# REMOVED: get_config_value function - unused


def get_database_url() -> str:
    """Get database URL with fallback construction."""
    config = get_central_config()

    if config.database_url:
        return config.database_url

    # Construct from individual components
    user = config.postgres_user
    password = (
        config.postgres_password.get_secret_value() if config.postgres_password else ""
    )
    host = config.postgres_host
    port = config.postgres_port
    name = config.postgres_db

    if password:
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"
    else:
        return f"postgresql://{user}@{host}:{port}/{name}"


def get_redis_url() -> str:
    """Get Redis URL with fallback."""
    config = get_central_config()
    return str(config.redis_url) if config.redis_url else "redis://localhost:6379/0"


def get_ollama_url() -> str:
    """Get Ollama URL with fallback."""
    config = get_central_config()
    return (
        str(config.ollama_base_url)
        if config.ollama_base_url
        else "http://localhost:11434"
    )


def get_vector_db_url() -> str:
    """Get vector database URL with fallback."""
    config = get_central_config()
    return str(config.vector_db_url) if config.vector_db_url else str(config.qdrant_url)


def get_meilisearch_url() -> str:
    """Get MeiliSearch URL with fallback."""
    config = get_central_config()
    return (
        str(config.meilisearch_url)
        if config.meilisearch_url
        else "http://localhost:7700"
    )


def get_arangodb_url() -> str:
    """Get ArangoDB URL with fallback."""
    config = get_central_config()
    return str(config.arango_url) if config.arango_url else "http://localhost:8529"


# =============================================================================
# INITIALIZATION
# =============================================================================


def initialize_config() -> CentralConfig:
    """Initialize and validate configuration."""
    config = get_central_config()

    # Print startup configuration
    config.print_startup_config()

    # Validate configuration
    issues = config.validate_config()
    if issues:
        logger.warning(f"Configuration validation found {len(issues)} issues")
        for issue in issues:
            logger.warning(f"  - {issue}")

    return config
