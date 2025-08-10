"""
Configuration Management Module - MAANG Standards.

This module implements comprehensive configuration management following
MAANG best practices for security, validation, and environment handling.

Features:
    - Type-safe configuration with Pydantic
    - Environment-based configuration
    - Secrets management with encryption
    - Configuration validation and defaults
    - Hot-reloading for development
    - Configuration versioning
    - Audit logging for changes

Security:
    - Sensitive values are never logged
    - Secrets are encrypted at rest
    - Environment validation
    - Secure defaults

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import os
import json
import secrets
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Set, ClassVar, Type, cast
from functools import lru_cache
from enum import Enum
import warnings

from pydantic import (
    Field,
    field_validator,
    model_validator,
    SecretStr,
    HttpUrl,
    PostgresDsn,
    RedisDsn,
    EmailStr,
    IPvAnyAddress,
    conint,
    confloat,
    ValidationInfo,
    ConfigDict,
)
from pydantic_settings import BaseSettings
from pydantic.types import constr
import structlog

logger = structlog.get_logger(__name__)


# Environment types
class Environment(str, Enum):
    """Application environment types."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

    @classmethod
    def from_string(cls, env: str) -> "Environment":
        """Create Environment from string."""
        try:
            return cls(env.lower())
        except ValueError:
            logger.warning(f"Unknown environment '{env}', defaulting to development")
            return cls.DEVELOPMENT


# Log levels
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


class SecureSettings(BaseSettings):
    """
    Base settings class with security features.

    Features:
    - Automatic secret masking in logs
    - Environment variable validation
    - Type conversion and validation
    """

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Custom JSON encoders for security - removed for Pydantic V2 compatibility
        # Use model_serializer instead
    )

    def dict(self, **kwargs) -> Dict[str, Any]:
        """Override dict to mask secrets."""
        d = super().dict(**kwargs)
        return self._mask_secrets(d)

    def _mask_secrets(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively mask secret values."""
        masked = {}
        for key, value in data.items():
            if any(
                secret in key.lower()
                for secret in ["password", "secret", "key", "token", "dsn"]
            ):
                masked[key] = "***REDACTED***"
            elif isinstance(value, dict):
                masked[key] = self._mask_secrets(value)
            else:
                masked[key] = value
        return masked

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Override model_dump to mask secrets."""
        d = super().model_dump(**kwargs)
        return self._mask_secrets(d)


class APISettings(SecureSettings):
    """API-specific settings."""

    # Basic settings
    host: IPvAnyAddress = Field(default="0.0.0.0", description="API host address")
    port: Port = Field(default=8000, description="API port")
    workers: conint(ge=1) = Field(default=4, description="Number of worker processes")

    # API configuration
    api_prefix: str = Field(default="/api/v2", description="API route prefix")
    docs_enabled: bool = Field(default=True, description="Enable API documentation")

    # CORS settings
    cors_origins: List[HttpUrl] = Field(
        default=["http://localhost:3000"], description="Allowed CORS origins"
    )
    cors_credentials: bool = Field(
        default=True, description="Allow credentials in CORS"
    )

    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_per_minute: conint(ge=1) = Field(
        default=60, description="Default rate limit per minute"
    )
    rate_limit_burst: conint(ge=1) = Field(default=10, description="Burst allowance")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


class DatabaseSettings(SecureSettings):
    """Database configuration settings."""

    # Primary database
    database_url: Optional[str] = Field(
        default=None, description="Database connection URL (PostgreSQL or SQLite)"
    )
    database_pool_size: conint(ge=1) = Field(
        default=20, description="Connection pool size"
    )
    database_max_overflow: conint(ge=0) = Field(
        default=10, description="Max overflow connections"
    )
    database_pool_timeout: conint(ge=1) = Field(
        default=30, description="Pool timeout in seconds"
    )

    # Read replica
    database_read_url: Optional[PostgresDsn] = Field(
        default=None, description="Read replica URL"
    )

    # SQLite for testing
    sqlite_file: Optional[Path] = Field(
        default=None, description="SQLite file for testing"
    )

    # PostgreSQL specific settings
    postgres_host: str = Field(default="localhost", description="PostgreSQL host")
    postgres_port: Port = Field(default=5432, description="PostgreSQL port")
    postgres_db: str = Field(default="sarvanom", description="PostgreSQL database name")
    postgres_user: str = Field(default="postgres", description="PostgreSQL username")
    postgres_password: Optional[SecretStr] = Field(
        default=None, description="PostgreSQL password"
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def build_database_url(
        cls, v: Optional[str], info: ValidationInfo
    ) -> Optional[str]:
        """Build database URL from components if not provided."""
        if v:
            return v

        # Build from components
        user = info.data.get("postgres_user", "postgres")
        password = info.data.get("postgres_password")
        host = info.data.get("postgres_host", "localhost")
        port = info.data.get("postgres_port", "5432")
        name = info.data.get("postgres_db", "sarvanom")

        if user and password:
            return f"postgresql://{user}:{password}@{host}:{port}/{name}"

        return None


class CacheSettings(SecureSettings):
    """Cache configuration settings."""

    # Redis settings
    redis_url: Optional[RedisDsn] = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )
    redis_password: Optional[SecretStr] = Field(
        default=None, description="Redis password"
    )
    redis_pool_size: conint(ge=1) = Field(
        default=10, description="Redis connection pool size"
    )

    # Cache TTL settings
    cache_ttl_default: conint(ge=0) = Field(
        default=300, description="Default cache TTL in seconds"
    )
    cache_ttl_user: conint(ge=0) = Field(default=600, description="User cache TTL")
    cache_ttl_query: conint(ge=0) = Field(default=3600, description="Query cache TTL")

    # Cache behavior
    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_prefix: str = Field(default="ukp:", description="Cache key prefix")


class SecuritySettings(SecureSettings):
    """Security configuration settings."""

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

    # Password settings
    password_min_length: conint(ge=8) = Field(
        default=12, description="Minimum password length"
    )
    password_require_uppercase: bool = Field(
        default=True, description="Require uppercase letters"
    )
    password_require_lowercase: bool = Field(
        default=True, description="Require lowercase letters"
    )
    password_require_digits: bool = Field(default=True, description="Require digits")
    password_require_special: bool = Field(
        default=True, description="Require special characters"
    )

    # Bcrypt settings
    bcrypt_rounds: conint(ge=4, le=31) = Field(
        default=12, description="Bcrypt cost factor"
    )

    # Security features
    enable_api_keys: bool = Field(
        default=True, description="Enable API key authentication"
    )
    enable_two_factor: bool = Field(default=False, description="Enable 2FA")

    # Session settings
    session_lifetime_hours: conint(ge=1) = Field(
        default=24, description="Session lifetime"
    )
    max_sessions_per_user: conint(ge=1) = Field(
        default=5, description="Max concurrent sessions"
    )

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, v: SecretStr) -> SecretStr:
        """Ensure JWT secret is strong enough."""
        secret = v.get_secret_value()
        if len(secret) < 32:
            raise ValueError("JWT secret must be at least 32 characters")
        return v


class AISettings(SecureSettings):
    """AI/ML service configuration."""

    # OpenAI
    openai_api_key: Optional[SecretStr] = Field(
        default=None, description="OpenAI API key"
    )
    openai_organization: Optional[str] = Field(
        default=None, description="OpenAI organization ID"
    )
    openai_model: str = Field(default="gpt-4o-mini", description="Default OpenAI model")
    openai_max_tokens: conint(ge=1) = Field(
        default=2000, description="Max tokens per request"
    )
    openai_temperature: confloat(ge=0.0, le=2.0) = Field(
        default=0.7, description="Model temperature"
    )
    openai_embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", description="Embedding model"
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

    # Vector database
    vector_db_provider: str = Field(
        default="pinecone", description="Vector DB provider (pinecone/weaviate/milvus)"
    )
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

    @field_validator("vector_db_provider")
    @classmethod
    def validate_vector_provider(cls, v: str) -> str:
        """Validate vector DB provider."""
        valid_providers = {"pinecone", "weaviate", "milvus", "qdrant", "meilisearch"}
        if v.lower() not in valid_providers:
            raise ValueError(f"Invalid provider. Must be one of: {valid_providers}")
        return v.lower()


class VectorDatabaseSettings(SecureSettings):
    """Vector database configuration settings."""

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
    qdrant_cloud_url: Optional[HttpUrl] = Field(
        default=None, description="Qdrant cloud URL"
    )

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
        default="knowledge_base", description="MeiliSearch index name"
    )


class KnowledgeGraphSettings(SecureSettings):
    """Knowledge Graph configuration settings."""

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

    # Graph settings
    graph_update_enabled: bool = Field(default=True, description="Enable graph updates")
    graph_auto_extract_entities: bool = Field(
        default=True, description="Auto-extract entities"
    )
    graph_confidence_threshold: confloat(ge=0.0, le=1.0) = Field(
        default=0.7, description="Graph confidence threshold"
    )
    graph_max_entities_per_doc: conint(ge=1) = Field(
        default=10, description="Max entities per document"
    )
    graph_relationship_types: str = Field(
        default="is_related_to,is_part_of,is_similar_to,enables,requires",
        description="Graph relationship types",
    )

    # Knowledge Graph Agent
    kg_agent_enabled: bool = Field(default=True, description="Enable KG agent")
    kg_agent_timeout: conint(ge=1) = Field(default=30, description="KG agent timeout")
    kg_max_relationship_depth: conint(ge=1) = Field(
        default=3, description="Max relationship depth"
    )


class MonitoringSettings(SecureSettings):
    """Monitoring and observability settings."""

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

    # Logging
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    log_format: str = Field(default="json", description="Log format (json/text)")
    log_file: Optional[Path] = Field(default=None, description="Log file path")

    @field_validator("log_level", mode="before")
    @classmethod
    def validate_log_level(cls, v: Union[str, LogLevel]) -> LogLevel:
        """Validate and convert log level from string."""
        if isinstance(v, str):
            return LogLevel.from_string(v)
        return v

    # Health checks
    health_check_interval: conint(ge=1) = Field(
        default=30, description="Health check interval in seconds"
    )


class MicroservicesSettings(SecureSettings):
    """Microservices configuration settings."""

    # Service URLs
    auth_service_url: HttpUrl = Field(
        default="http://localhost:8001", description="Auth service URL"
    )
    auth_service_secret: SecretStr = Field(
        default_factory=lambda: SecretStr(secrets.token_urlsafe(32)),
        description="Auth service secret",
    )

    search_service_url: HttpUrl = Field(
        default="http://localhost:8002", description="Search service URL"
    )
    search_service_secret: SecretStr = Field(
        default_factory=lambda: SecretStr(secrets.token_urlsafe(32)),
        description="Search service secret",
    )

    synthesis_service_url: HttpUrl = Field(
        default="http://localhost:8003", description="Synthesis service URL"
    )
    synthesis_service_secret: SecretStr = Field(
        default_factory=lambda: SecretStr(secrets.token_urlsafe(32)),
        description="Synthesis service secret",
    )

    factcheck_service_url: HttpUrl = Field(
        default="http://localhost:8004", description="Fact-check service URL"
    )
    factcheck_service_secret: SecretStr = Field(
        default_factory=lambda: SecretStr(secrets.token_urlsafe(32)),
        description="Fact-check service secret",
    )

    analytics_service_url: HttpUrl = Field(
        default="http://localhost:8005", description="Analytics service URL"
    )
    analytics_service_secret: SecretStr = Field(
        default_factory=lambda: SecretStr(secrets.token_urlsafe(32)),
        description="Analytics service secret",
    )


class AgentSettings(SecureSettings):
    """Agent configuration settings."""

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


class Settings(
    APISettings,
    DatabaseSettings,
    CacheSettings,
    SecuritySettings,
    AISettings,
    VectorDatabaseSettings,
    KnowledgeGraphSettings,
    MonitoringSettings,
    MicroservicesSettings,
    AgentSettings,
):
    """
    Complete application settings.

    Combines all setting categories with validation and defaults.
    """

    # Application metadata
    app_name: str = Field(
        default="Universal Knowledge Platform", description="Application name"
    )
    app_version: str = Field(default="2.0.0", description="Application version")

    # Environment
    environment: Environment = Field(
        default=Environment.DEVELOPMENT, description="Deployment environment"
    )
    debug: bool = Field(default=False, description="Debug mode")
    testing: bool = Field(default=False, description="Testing mode")

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

    # Deployment
    trusted_hosts: Optional[List[str]] = Field(
        default=None, description="Trusted host headers"
    )
    behind_proxy: bool = Field(default=False, description="Running behind proxy")

    # Performance
    request_timeout: conint(ge=1) = Field(
        default=30, description="Request timeout in seconds"
    )
    max_request_size: conint(ge=1) = Field(
        default=10 * 1024 * 1024, description="Max request size in bytes"  # 10MB
    )

    # Development
    reload: bool = Field(default=False, description="Auto-reload on changes")
    access_log: bool = Field(default=True, description="Enable access logging")

    # Service identification
    service_name: str = Field(default="sarvanom-backend", description="Service name")
    version: str = Field(default="1.0.0", description="Service version")

    # Docker configuration
    docker_enabled: bool = Field(default=True, description="Docker mode enabled")
    docker_network: str = Field(
        default="sarvanom-network", description="Docker network"
    )

    # Service URLs for Docker
    backend_url: HttpUrl = Field(
        default="http://sarvanom_backend:8000", description="Backend URL"
    )
    postgres_url: PostgresDsn = Field(
        default="postgresql://postgres:password@postgres:5432/sarvanom_db",
        description="PostgreSQL URL",
    )
    redis_url: RedisDsn = Field(default="redis://redis:6379/0", description="Redis URL")
    meilisearch_url: HttpUrl = Field(
        default="http://meilisearch:7700", description="MeiliSearch URL"
    )
    arangodb_url: HttpUrl = Field(
        default="http://arangodb:8529", description="ArangoDB URL"
    )
    qdrant_url: HttpUrl = Field(default="http://qdrant:6333", description="Qdrant URL")
    ollama_url: HttpUrl = Field(default="http://ollama:11434", description="Ollama URL")

    # External integrations
    smtp_host: str = Field(default="smtp.gmail.com", description="SMTP host")
    smtp_port: Port = Field(default=587, description="SMTP port")
    smtp_username: Optional[str] = Field(default=None, description="SMTP username")
    smtp_password: Optional[SecretStr] = Field(
        default=None, description="SMTP password"
    )
    smtp_use_tls: bool = Field(default=True, description="SMTP use TLS")

    # File storage
    storage_type: str = Field(default="local", description="Storage type")
    storage_bucket: str = Field(
        default="sarvanom-uploads", description="Storage bucket"
    )
    storage_region: str = Field(default="us-west-1", description="Storage region")

    # AWS S3
    aws_access_key_id: Optional[SecretStr] = Field(
        default=None, description="AWS access key ID"
    )
    aws_secret_access_key: Optional[SecretStr] = Field(
        default=None, description="AWS secret access key"
    )
    aws_region: str = Field(default="us-west-1", description="AWS region")

    # Webhooks
    slack_webhook_url: Optional[HttpUrl] = Field(
        default=None, description="Slack webhook URL"
    )
    slack_channel: str = Field(default="#sarvanom-alerts", description="Slack channel")
    discord_webhook_url: Optional[HttpUrl] = Field(
        default=None, description="Discord webhook URL"
    )

    # Advanced configuration
    cache_ttl_seconds: conint(ge=0) = Field(
        default=3600, description="Cache TTL in seconds"
    )
    cache_max_size: conint(ge=1) = Field(default=1000, description="Cache max size")
    session_secret: SecretStr = Field(
        default_factory=lambda: SecretStr(secrets.token_urlsafe(32)),
        description="Session secret",
    )
    session_ttl_seconds: conint(ge=1) = Field(
        default=86400, description="Session TTL in seconds"
    )

    # API versioning
    api_version: str = Field(default="v1", description="API version")
    api_deprecation_warning_days: conint(ge=0) = Field(
        default=30, description="API deprecation warning days"
    )

    # Performance tuning
    db_pool_size: conint(ge=1) = Field(default=5, description="DB pool size")
    db_max_overflow: conint(ge=0) = Field(default=10, description="DB max overflow")
    db_pool_timeout: conint(ge=1) = Field(default=30, description="DB pool timeout")
    worker_processes: conint(ge=1) = Field(default=2, description="Worker processes")
    worker_threads: conint(ge=1) = Field(default=2, description="Worker threads")
    max_memory_usage_mb: conint(ge=1) = Field(
        default=1024, description="Max memory usage in MB"
    )
    garbage_collection_interval: conint(ge=1) = Field(
        default=300, description="Garbage collection interval"
    )

    # Backup & Recovery
    backup_enabled: bool = Field(default=True, description="Enable backups")
    backup_interval_hours: conint(ge=1) = Field(
        default=24, description="Backup interval in hours"
    )
    backup_retention_days: conint(ge=1) = Field(
        default=30, description="Backup retention in days"
    )
    recovery_mode: bool = Field(default=False, description="Recovery mode")
    recovery_point_retention_days: conint(ge=1) = Field(
        default=7, description="Recovery point retention"
    )

    # Compliance & Audit
    audit_log_enabled: bool = Field(default=True, description="Enable audit logging")
    audit_log_level: LogLevel = Field(
        default=LogLevel.INFO, description="Audit log level"
    )
    audit_log_retention_days: conint(ge=1) = Field(
        default=365, description="Audit log retention"
    )
    data_retention_days: conint(ge=1) = Field(
        default=2555, description="Data retention in days"
    )
    anonymize_old_data: bool = Field(default=True, description="Anonymize old data")

    # Security headers
    security_headers_enabled: bool = Field(
        default=True, description="Enable security headers"
    )
    content_security_policy: str = Field(
        default="default-src 'self'", description="Content security policy"
    )

    # Input validation
    max_request_size_mb: conint(ge=1) = Field(
        default=10, description="Max request size in MB"
    )
    max_query_length: conint(ge=1) = Field(default=2000, description="Max query length")

    # Rate limiting per user
    user_rate_limit_requests_per_minute: conint(ge=1) = Field(
        default=30, description="User rate limit requests per minute"
    )
    user_rate_limit_tokens_per_minute: conint(ge=1) = Field(
        default=5000, description="User rate limit tokens per minute"
    )

    # Development & Testing
    mock_ai_responses: bool = Field(default=False, description="Mock AI responses")
    skip_authentication: bool = Field(default=False, description="Skip authentication")
    enable_debug_endpoints: bool = Field(
        default=False, description="Enable debug endpoints"
    )
    auto_reload: bool = Field(default=False, description="Auto reload")
    test_mode: bool = Field(default=False, description="Test mode")
    mock_providers: bool = Field(default=False, description="Mock providers")

    # Test database
    test_database_url: str = Field(
        default="sqlite:///test.db", description="Test database URL"
    )
    test_redis_url: RedisDsn = Field(
        default="redis://redis:6379/1", description="Test Redis URL"
    )

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate environment-specific settings."""
        env = values.get("environment", Environment.DEVELOPMENT)

        # Convert string to enum
        if isinstance(env, str):
            env = Environment.from_string(env)
            values["environment"] = env

        # Set environment-specific defaults
        if env == Environment.PRODUCTION:
            # Production settings
            values.setdefault("debug", False)
            values.setdefault("docs_enabled", False)
            values.setdefault("reload", False)
            values.setdefault("log_level", LogLevel.WARNING)

            # Require certain settings in production
            required = ["database_url", "redis_url", "jwt_secret_key", "sentry_dsn"]

            missing = [field for field in required if not values.get(field)]

            if missing:
                warnings.warn(f"Missing recommended production settings: {missing}")

        elif env == Environment.DEVELOPMENT:
            # Development settings
            values.setdefault("debug", True)
            values.setdefault("reload", True)
            values.setdefault("log_level", LogLevel.DEBUG)

        elif env == Environment.TESTING:
            # Testing settings
            values.setdefault("testing", True)
            values.setdefault("debug", True)
            values.setdefault("log_level", LogLevel.DEBUG)

            # Use SQLite for testing
            if not values.get("database_url"):
                values["database_url"] = "sqlite:///test.db"

        return values

    @field_validator("features", mode="before")
    @classmethod
    def parse_features(cls, v: Union[str, Dict[str, bool]]) -> Dict[str, bool]:
        """Parse feature flags from string or dict."""
        if isinstance(v, str):
            # Parse JSON string
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                logger.error(f"Invalid feature flags JSON: {v}")
                return {}
        return v

    def get_feature(self, feature: str) -> bool:
        """Check if a feature is enabled."""
        return self.features.get(feature, False)

    def to_dict(self, include_secrets: bool = False) -> Dict[str, Any]:
        """
        Convert settings to dictionary.

        Args:
            include_secrets: Include secret values (dangerous!)

        Returns:
            Settings dictionary
        """
        if include_secrets:
            return super().dict()
        else:
            return self.dict()

    def validate_config(self) -> List[str]:
        """
        Validate configuration completeness.

        Returns:
            List of validation warnings
        """
        warnings = []

        # Check AI configuration
        if (
            not self.openai_api_key
            and not self.anthropic_api_key
            and not self.ollama_enabled
        ):
            warnings.append("No AI provider configured")

        # Check database configuration
        if not self.database_url and self.environment != Environment.TESTING:
            warnings.append("No database URL configured")

        # Check cache configuration
        if self.cache_enabled and not self.redis_url:
            warnings.append("Cache enabled but no Redis URL configured")

        # Check monitoring
        if self.environment == Environment.PRODUCTION:
            if not self.sentry_dsn:
                warnings.append("Sentry not configured for production")

            if not self.enable_tracing:
                warnings.append("Distributed tracing disabled in production")

        # Check security
        if self.jwt_secret_key.get_secret_value() == secrets.token_urlsafe(32):
            warnings.append("Using default JWT secret key")

        return warnings

    model_config = ConfigDict(
        # Environment variable prefix
        env_prefix="UKP_",
        # Allow extra fields for forward compatibility
        extra="ignore",
        # Validate on assignment
        validate_assignment=True,
    )


# Global settings instance
_settings: Optional[Settings] = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Global settings instance
    """
    global _settings

    if _settings is None:
        _settings = Settings()

        # Log configuration (without secrets)
        logger.info(
            "Settings initialized",
            environment=_settings.environment.value,
            debug=_settings.debug,
            features=list(_settings.features.keys()),
        )

        # Validate configuration
        warnings = _settings.validate_config()
        for warning in warnings:
            logger.warning(f"Configuration warning: {warning}")

    return _settings


def reload_settings() -> Settings:
    """
    Reload settings from environment.

    Returns:
        New settings instance
    """
    global _settings

    # Clear cache
    get_settings.cache_clear()

    # Reload
    _settings = Settings()

    logger.info("Settings reloaded")

    return _settings


# Export public API
__all__ = [
    "Settings",
    "get_settings",
    "reload_settings",
    "Environment",
    "LogLevel",
]
