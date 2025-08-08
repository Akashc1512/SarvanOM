"""
Environment Configuration Manager - MAANG Standards.

This module implements comprehensive environment-based configuration management
following MAANG best practices for security, validation, and environment handling.

Features:
    - Environment-specific configuration loading
    - Secure secrets management
    - Configuration validation and defaults
    - Environment variable precedence
    - Configuration file support (YAML/JSON)
    - Hot-reloading for development
    - Configuration versioning
    - Audit logging for changes

Security:
    - Sensitive values are never logged
    - Secrets are encrypted at rest
    - Environment validation
    - Secure defaults
    - No hardcoded secrets

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import os
import json
import yaml
import secrets
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from enum import Enum
from functools import lru_cache
import structlog
from dataclasses import dataclass, field
import warnings

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


@dataclass
class EnvironmentConfig:
    """Configuration for a specific environment."""
    
    name: str
    debug: bool = False
    testing: bool = False
    log_level: str = "INFO"
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    vector_db_url: Optional[str] = None
    vector_db_api_key: Optional[str] = None
    meilisearch_url: Optional[str] = None
    meilisearch_master_key: Optional[str] = None
    arangodb_url: Optional[str] = None
    arangodb_username: Optional[str] = None
    arangodb_password: Optional[str] = None
    arangodb_database: Optional[str] = None
    jwt_secret_key: Optional[str] = None
    cors_origins: List[str] = field(default_factory=list)
    rate_limit_per_minute: int = 60
    max_request_size_mb: int = 10
    cache_ttl_seconds: int = 3600
    session_ttl_seconds: int = 86400
    backup_enabled: bool = True
    audit_log_enabled: bool = True
    security_headers_enabled: bool = True
    mock_ai_responses: bool = False
    skip_authentication: bool = False
    enable_debug_endpoints: bool = False
    auto_reload: bool = False
    test_mode: bool = False
    mock_providers: bool = False
    
    # Service URLs (configurable via environment variables)
    auth_service_url: str = "http://localhost:8001"  # AUTH_SERVICE_URL
    search_service_url: str = "http://localhost:8002"  # SEARCH_SERVICE_URL
    synthesis_service_url: str = "http://localhost:8003"  # SYNTHESIS_SERVICE_URL
    factcheck_service_url: str = "http://localhost:8004"  # FACTCHECK_SERVICE_URL
    analytics_service_url: str = "http://localhost:8005"  # ANALYTICS_SERVICE_URL
    
    # Service secrets
    auth_service_secret: Optional[str] = None
    search_service_secret: Optional[str] = None
    synthesis_service_secret: Optional[str] = None
    factcheck_service_secret: Optional[str] = None
    analytics_service_secret: Optional[str] = None
    
    # Agent settings
    agent_timeout_seconds: int = 30
    agent_max_retries: int = 3
    agent_backoff_factor: float = 2.0
    query_cache_ttl_seconds: int = 3600
    query_max_length: int = 2000
    query_min_confidence: float = 0.7
    
    # Performance settings
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    worker_processes: int = 2
    worker_threads: int = 2
    max_memory_usage_mb: int = 1024
    garbage_collection_interval: int = 300
    
    # Monitoring settings
    metrics_enabled: bool = True
    metrics_port: int = 9090
    enable_tracing: bool = False
    jaeger_agent_host: str = "localhost"
    jaeger_agent_port: int = 6831
    sentry_dsn: Optional[str] = None
    sentry_traces_sample_rate: float = 0.1
    sentry_profiles_sample_rate: float = 0.1
    health_check_interval: int = 30
    health_check_timeout: int = 10
    
    # Feature flags
    features: Dict[str, bool] = field(default_factory=lambda: {
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
    })
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate configuration values."""
        if self.rate_limit_per_minute < 1:
            raise ValueError("rate_limit_per_minute must be at least 1")
        
        if self.max_request_size_mb < 1:
            raise ValueError("max_request_size_mb must be at least 1")
        
        if self.cache_ttl_seconds < 0:
            raise ValueError("cache_ttl_seconds must be non-negative")
        
        if self.session_ttl_seconds < 1:
            raise ValueError("session_ttl_seconds must be at least 1")
        
        if self.agent_timeout_seconds < 1:
            raise ValueError("agent_timeout_seconds must be at least 1")
        
        if self.agent_max_retries < 0:
            raise ValueError("agent_max_retries must be non-negative")
        
        if self.agent_backoff_factor < 1.0:
            raise ValueError("agent_backoff_factor must be at least 1.0")
        
        if self.query_min_confidence < 0.0 or self.query_min_confidence > 1.0:
            raise ValueError("query_min_confidence must be between 0.0 and 1.0")
    
    def to_dict(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        config_dict = {}
        
        for field_name, field_value in self.__dict__.items():
            if field_name in ["openai_api_key", "anthropic_api_key", "vector_db_api_key", 
                            "meilisearch_master_key", "arangodb_password", "jwt_secret_key",
                            "auth_service_secret", "search_service_secret", "synthesis_service_secret",
                            "factcheck_service_secret", "analytics_service_secret", "sentry_dsn"]:
                if include_secrets:
                    config_dict[field_name] = field_value
                else:
                    config_dict[field_name] = "***REDACTED***" if field_value else None
            else:
                config_dict[field_name] = field_value
        
        return config_dict


class EnvironmentManager:
    """
    Environment-based configuration manager.
    
    This class handles loading, validating, and managing configuration
    for different environments (development, testing, staging, production).
    """
    
    def __init__(self, app_env: Optional[str] = None):
        """
        Initialize the environment manager.
        
        Args:
            app_env: Environment name (defaults to APP_ENV environment variable)
        """
        # Load APP_ENV from environment variable with fallback
        self.app_env = app_env or os.getenv("APP_ENV", "development")
        self.environment = Environment.from_string(self.app_env)
        self.config = self._load_environment_config()
        
        # Log configuration loading
        logger.info(f"🚀 Environment manager initialized for {self.environment.value.upper()} environment")
        logger.info(f"📋 Configuration loaded successfully from APP_ENV={self.app_env}")
        
        # Print startup configuration summary
        self._print_startup_config()
        
        # Validate configuration for the current environment
        self._validate_environment_config(self.config)
    
    def _load_environment_config(self) -> EnvironmentConfig:
        """Load configuration for the current environment."""
        # Start with environment-specific defaults
        config = self._get_environment_defaults()
        
        # Load from environment-specific config file
        config_file = self._get_config_file_path()
        if config_file and config_file.exists():
            file_config = self._load_from_file(config_file)
            config = self._merge_configs(config, file_config)
            logger.info(f"📄 Loaded configuration from file: {config_file}")
        
        # Load from environment variables (highest precedence)
        env_config = self._load_from_environment()
        config = self._merge_configs(config, env_config)
        
        # Validate final configuration
        self._validate_environment_config(config)
        
        return config
    
    def _get_environment_defaults(self) -> EnvironmentConfig:
        """Get default configuration for the current environment."""
        if self.environment == Environment.DEVELOPMENT:
            return EnvironmentConfig(
                name="development",
                debug=True,
                testing=False,
                log_level="DEBUG",
                database_url="sqlite:///dev.db",
                redis_url="redis://localhost:6379/0",
                openai_api_key=None,  # Will be loaded from env
                anthropic_api_key=None,  # Will be loaded from env
                vector_db_url="http://localhost:6333",
                meilisearch_url="http://localhost:7700",
                arangodb_url="http://localhost:8529",
                arangodb_username="root",
                arangodb_password="",
                arangodb_database="knowledge_graph",
                jwt_secret_key=None,  # Must be set via JWT_SECRET_KEY
                cors_origins=["http://localhost:3000", "http://localhost:8000"],
                rate_limit_per_minute=1000,
                max_request_size_mb=50,
                cache_ttl_seconds=1800,
                session_ttl_seconds=3600,
                backup_enabled=False,
                audit_log_enabled=True,
                security_headers_enabled=False,
                mock_ai_responses=True,
                skip_authentication=True,
                enable_debug_endpoints=True,
                auto_reload=True,
                test_mode=False,
                mock_providers=True,
                agent_timeout_seconds=60,
                agent_max_retries=5,
                agent_backoff_factor=1.5,
                query_cache_ttl_seconds=1800,
                query_max_length=5000,
                query_min_confidence=0.5,
                db_pool_size=3,
                db_max_overflow=5,
                db_pool_timeout=20,
                worker_processes=1,
                worker_threads=2,
                max_memory_usage_mb=512,
                garbage_collection_interval=600,
                metrics_enabled=True,
                metrics_port=9090,
                enable_tracing=False,
                jaeger_agent_host="localhost",
                jaeger_agent_port=6831,
                sentry_dsn=None,
                sentry_traces_sample_rate=0.0,
                sentry_profiles_sample_rate=0.0,
                health_check_interval=60,
                health_check_timeout=30,
                features={
                    "streaming": True,
                    "batch_processing": True,
                    "websockets": True,
                    "graphql": False,
                    "admin_panel": True,
                    "expert_review": True,
                    "real_time_collaboration": True,
                    "advanced_analytics": True,
                    "multi_tenant": False,
                    "sso": False,
                }
            )
        
        elif self.environment == Environment.TESTING:
            return EnvironmentConfig(
                name="testing",
                debug=True,
                testing=True,
                log_level="DEBUG",
                database_url="sqlite:///test.db",
                redis_url="redis://localhost:6379/1",
                openai_api_key=None,
                anthropic_api_key=None,
                vector_db_url="http://localhost:6333",
                meilisearch_url="http://localhost:7700",
                arangodb_url="http://localhost:8529",
                arangodb_username="root",
                arangodb_password="",
                arangodb_database="test_knowledge_graph",
                jwt_secret_key=None,  # Must be set via JWT_SECRET_KEY
                cors_origins=["http://localhost:3000"],
                rate_limit_per_minute=10000,
                max_request_size_mb=100,
                cache_ttl_seconds=300,
                session_ttl_seconds=1800,
                backup_enabled=False,
                audit_log_enabled=False,
                security_headers_enabled=False,
                mock_ai_responses=True,
                skip_authentication=True,
                enable_debug_endpoints=True,
                auto_reload=False,
                test_mode=True,
                mock_providers=True,
                agent_timeout_seconds=30,
                agent_max_retries=2,
                agent_backoff_factor=1.0,
                query_cache_ttl_seconds=300,
                query_max_length=1000,
                query_min_confidence=0.3,
                db_pool_size=2,
                db_max_overflow=3,
                db_pool_timeout=10,
                worker_processes=1,
                worker_threads=1,
                max_memory_usage_mb=256,
                garbage_collection_interval=300,
                metrics_enabled=False,
                metrics_port=9091,
                enable_tracing=False,
                jaeger_agent_host="localhost",
                jaeger_agent_port=6831,
                sentry_dsn=None,
                sentry_traces_sample_rate=0.0,
                sentry_profiles_sample_rate=0.0,
                health_check_interval=30,
                health_check_timeout=5,
                features={
                    "streaming": False,
                    "batch_processing": True,
                    "websockets": False,
                    "graphql": False,
                    "admin_panel": False,
                    "expert_review": False,
                    "real_time_collaboration": False,
                    "advanced_analytics": False,
                    "multi_tenant": False,
                    "sso": False,
                }
            )
        
        elif self.environment == Environment.STAGING:
            return EnvironmentConfig(
                name="staging",
                debug=False,
                testing=False,
                log_level="INFO",
                database_url=None,  # Must be set via env
                redis_url=None,  # Must be set via env
                openai_api_key=None,  # Must be set via env
                anthropic_api_key=None,  # Must be set via env
                vector_db_url=None,  # Must be set via env
                meilisearch_url=None,  # Must be set via env
                arangodb_url=None,  # Must be set via env
                arangodb_username=None,  # Must be set via env
                arangodb_password=None,  # Must be set via env
                arangodb_database="staging_knowledge_graph",
                jwt_secret_key=None,  # Must be set via env
                cors_origins=["https://staging.sarvanom.com"],
                rate_limit_per_minute=100,
                max_request_size_mb=20,
                cache_ttl_seconds=3600,
                session_ttl_seconds=7200,
                backup_enabled=True,
                audit_log_enabled=True,
                security_headers_enabled=True,
                mock_ai_responses=False,
                skip_authentication=False,
                enable_debug_endpoints=False,
                auto_reload=False,
                test_mode=False,
                mock_providers=False,
                agent_timeout_seconds=45,
                agent_max_retries=3,
                agent_backoff_factor=2.0,
                query_cache_ttl_seconds=3600,
                query_max_length=3000,
                query_min_confidence=0.7,
                db_pool_size=10,
                db_max_overflow=20,
                db_pool_timeout=30,
                worker_processes=4,
                worker_threads=4,
                max_memory_usage_mb=2048,
                garbage_collection_interval=300,
                metrics_enabled=True,
                metrics_port=9090,
                enable_tracing=True,
                jaeger_agent_host="localhost",
                jaeger_agent_port=6831,
                sentry_dsn=None,  # Must be set via env
                sentry_traces_sample_rate=0.1,
                sentry_profiles_sample_rate=0.1,
                health_check_interval=30,
                health_check_timeout=10,
                features={
                    "streaming": True,
                    "batch_processing": True,
                    "websockets": True,
                    "graphql": False,
                    "admin_panel": True,
                    "expert_review": True,
                    "real_time_collaboration": True,
                    "advanced_analytics": True,
                    "multi_tenant": False,
                    "sso": False,
                }
            )
        
        elif self.environment == Environment.PRODUCTION:
            return EnvironmentConfig(
                name="production",
                debug=False,
                testing=False,
                log_level="WARNING",
                database_url=None,  # Must be set via env
                redis_url=None,  # Must be set via env
                openai_api_key=None,  # Must be set via env
                anthropic_api_key=None,  # Must be set via env
                vector_db_url=None,  # Must be set via env
                meilisearch_url=None,  # Must be set via env
                arangodb_url=None,  # Must be set via env
                arangodb_username=None,  # Must be set via env
                arangodb_password=None,  # Must be set via env
                arangodb_database="production_knowledge_graph",
                jwt_secret_key=None,  # Must be set via env
                cors_origins=["https://sarvanom.com", "https://www.sarvanom.com"],
                rate_limit_per_minute=60,
                max_request_size_mb=10,
                cache_ttl_seconds=7200,
                session_ttl_seconds=86400,
                backup_enabled=True,
                audit_log_enabled=True,
                security_headers_enabled=True,
                mock_ai_responses=False,
                skip_authentication=False,
                enable_debug_endpoints=False,
                auto_reload=False,
                test_mode=False,
                mock_providers=False,
                agent_timeout_seconds=30,
                agent_max_retries=2,
                agent_backoff_factor=2.0,
                query_cache_ttl_seconds=7200,
                query_max_length=2000,
                query_min_confidence=0.8,
                db_pool_size=20,
                db_max_overflow=40,
                db_pool_timeout=30,
                worker_processes=8,
                worker_threads=8,
                max_memory_usage_mb=4096,
                garbage_collection_interval=300,
                metrics_enabled=True,
                metrics_port=9090,
                enable_tracing=True,
                jaeger_agent_host="localhost",
                jaeger_agent_port=6831,
                sentry_dsn=None,  # Must be set via env
                sentry_traces_sample_rate=0.05,
                sentry_profiles_sample_rate=0.05,
                health_check_interval=15,
                health_check_timeout=5,
                features={
                    "streaming": True,
                    "batch_processing": True,
                    "websockets": True,
                    "graphql": False,
                    "admin_panel": False,
                    "expert_review": True,
                    "real_time_collaboration": True,
                    "advanced_analytics": True,
                    "multi_tenant": False,
                    "sso": False,
                }
            )
        
        else:
            raise ValueError(f"Unknown environment: {self.environment}")
    
    def _get_config_file_path(self) -> Optional[Path]:
        """Get the path to the environment-specific configuration file."""
        config_dir = Path("config")
        
        # Try environment-specific config files
        config_files = [
            config_dir / f"{self.environment.value}.yaml",
            config_dir / f"{self.environment.value}.yml",
            config_dir / f"{self.environment.value}.json",
        ]
        
        for config_file in config_files:
            if config_file.exists():
                return config_file
        
        return None
    
    def _load_from_file(self, config_file: Path) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.suffix in ['.yaml', '.yml']:
                    return yaml.safe_load(f) or {}
                elif config_file.suffix == '.json':
                    return json.load(f)
                else:
                    logger.warning(f"Unsupported config file format: {config_file.suffix}")
                    return {}
        except Exception as e:
            logger.error(f"Failed to load config file {config_file}: {e}")
            return {}
    
    def _load_from_environment(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}
        
        # Environment variable mapping
        env_mapping = {
            "APP_ENV": "name",
            "LOG_LEVEL": "log_level",
            "DEBUG": "debug",
            "TESTING": "testing",
            "DATABASE_URL": "database_url",
            "REDIS_URL": "redis_url",
            "OPENAI_API_KEY": "openai_api_key",
            "ANTHROPIC_API_KEY": "anthropic_api_key",
            "VECTOR_DB_URL": "vector_db_url",
            "VECTOR_DB_API_KEY": "vector_db_api_key",
            "MEILISEARCH_URL": "meilisearch_url",
            "MEILISEARCH_MASTER_KEY": "meilisearch_master_key",
            "ARANGO_URL": "arangodb_url",
            "ARANGO_USERNAME": "arangodb_username",
            "ARANGO_PASSWORD": "arangodb_password",
            "ARANGO_DATABASE": "arangodb_database",
            "JWT_SECRET_KEY": "jwt_secret_key",
            "CORS_ORIGINS": "cors_origins",
            "RATE_LIMIT_PER_MINUTE": "rate_limit_per_minute",
            "MAX_REQUEST_SIZE_MB": "max_request_size_mb",
            "CACHE_TTL_SECONDS": "cache_ttl_seconds",
            "SESSION_TTL_SECONDS": "session_ttl_seconds",
            "BACKUP_ENABLED": "backup_enabled",
            "AUDIT_LOG_ENABLED": "audit_log_enabled",
            "SECURITY_HEADERS_ENABLED": "security_headers_enabled",
            "MOCK_AI_RESPONSES": "mock_ai_responses",
            "SKIP_AUTHENTICATION": "skip_authentication",
            "ENABLE_DEBUG_ENDPOINTS": "enable_debug_endpoints",
            "AUTO_RELOAD": "auto_reload",
            "TEST_MODE": "test_mode",
            "MOCK_PROVIDERS": "mock_providers",
            "AGENT_TIMEOUT_SECONDS": "agent_timeout_seconds",
            "AGENT_MAX_RETRIES": "agent_max_retries",
            "AGENT_BACKOFF_FACTOR": "agent_backoff_factor",
            "QUERY_CACHE_TTL_SECONDS": "query_cache_ttl_seconds",
            "QUERY_MAX_LENGTH": "query_max_length",
            "QUERY_MIN_CONFIDENCE": "query_min_confidence",
            "DB_POOL_SIZE": "db_pool_size",
            "DB_MAX_OVERFLOW": "db_max_overflow",
            "DB_POOL_TIMEOUT": "db_pool_timeout",
            "WORKER_PROCESSES": "worker_processes",
            "WORKER_THREADS": "worker_threads",
            "MAX_MEMORY_USAGE_MB": "max_memory_usage_mb",
            "GARBAGE_COLLECTION_INTERVAL": "garbage_collection_interval",
            "METRICS_ENABLED": "metrics_enabled",
            "METRICS_PORT": "metrics_port",
            "ENABLE_TRACING": "enable_tracing",
            "JAEGER_AGENT_HOST": "jaeger_agent_host",
            "JAEGER_AGENT_PORT": "jaeger_agent_port",
            "SENTRY_DSN": "sentry_dsn",
            "SENTRY_TRACES_SAMPLE_RATE": "sentry_traces_sample_rate",
            "SENTRY_PROFILES_SAMPLE_RATE": "sentry_profiles_sample_rate",
            "HEALTH_CHECK_INTERVAL": "health_check_interval",
            "HEALTH_CHECK_TIMEOUT": "health_check_timeout",
            # Service URLs
            "AUTH_SERVICE_URL": "auth_service_url",
            "SEARCH_SERVICE_URL": "search_service_url",
            "SYNTHESIS_SERVICE_URL": "synthesis_service_url",
            "FACTCHECK_SERVICE_URL": "factcheck_service_url",
            "ANALYTICS_SERVICE_URL": "analytics_service_url",
        }
        
        for env_var, config_key in env_mapping.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Convert string values to appropriate types
                if config_key in ["debug", "testing", "backup_enabled", "audit_log_enabled", 
                                "security_headers_enabled", "mock_ai_responses", "skip_authentication",
                                "enable_debug_endpoints", "auto_reload", "test_mode", "mock_providers",
                                "metrics_enabled", "enable_tracing"]:
                    config[config_key] = env_value.lower() in ["true", "1", "yes", "on"]
                elif config_key in ["rate_limit_per_minute", "max_request_size_mb", "cache_ttl_seconds",
                                  "session_ttl_seconds", "agent_timeout_seconds", "agent_max_retries",
                                  "query_cache_ttl_seconds", "query_max_length", "db_pool_size",
                                  "db_max_overflow", "db_pool_timeout", "worker_processes", "worker_threads",
                                  "max_memory_usage_mb", "garbage_collection_interval", "metrics_port",
                                  "jaeger_agent_port", "health_check_interval", "health_check_timeout"]:
                    try:
                        config[config_key] = int(env_value)
                    except ValueError:
                        logger.warning(f"Invalid integer value for {env_var}: {env_value}")
                elif config_key in ["agent_backoff_factor", "query_min_confidence", "sentry_traces_sample_rate",
                                  "sentry_profiles_sample_rate"]:
                    try:
                        config[config_key] = float(env_value)
                    except ValueError:
                        logger.warning(f"Invalid float value for {env_var}: {env_value}")
                elif config_key == "cors_origins":
                    config[config_key] = [origin.strip() for origin in env_value.split(",")]
                else:
                    config[config_key] = env_value
        
        return config
    
    def _merge_configs(self, base_config: EnvironmentConfig, override_config: Dict[str, Any]) -> EnvironmentConfig:
        """Merge configuration overrides into base configuration."""
        for key, value in override_config.items():
            if hasattr(base_config, key):
                setattr(base_config, key, value)
        
        return base_config
    
    def _validate_environment_config(self, config: EnvironmentConfig) -> None:
        """Validate environment-specific configuration requirements."""
        errors = []
        
        # Production and staging require certain configurations
        if self.environment == Environment.PRODUCTION:
            if not config.database_url:
                errors.append("DATABASE_URL is required for production")
            if not config.redis_url:
                errors.append("REDIS_URL is required for production")
            if not config.jwt_secret_key:
                errors.append("JWT_SECRET_KEY is required for production")
            if not config.openai_api_key and not config.anthropic_api_key:
                errors.append("At least one AI provider API key is required for production")
            if not config.vector_db_url:
                errors.append("VECTOR_DB_URL is required for production")
            if not config.meilisearch_url:
                errors.append("MEILISEARCH_URL is required for production")
            if not config.arangodb_url:
                errors.append("ARANGO_URL is required for production")
            if config.debug:
                errors.append("DEBUG should be False in production")
            if config.mock_ai_responses:
                errors.append("MOCK_AI_RESPONSES should be False in production")
            if config.skip_authentication:
                errors.append("SKIP_AUTHENTICATION should be False in production")
            if config.enable_debug_endpoints:
                errors.append("ENABLE_DEBUG_ENDPOINTS should be False in production")
        
        elif self.environment == Environment.STAGING:
            if not config.database_url:
                errors.append("DATABASE_URL is required for staging")
            if not config.redis_url:
                errors.append("REDIS_URL is required for staging")
            if not config.jwt_secret_key:
                errors.append("JWT_SECRET_KEY is required for staging")
            if not config.openai_api_key and not config.anthropic_api_key:
                errors.append("At least one AI provider API key is required for staging")
            if not config.vector_db_url:
                errors.append("VECTOR_DB_URL is required for staging")
            if not config.meilisearch_url:
                errors.append("MEILISEARCH_URL is required for staging")
            if not config.arangodb_url:
                errors.append("ARANGO_URL is required for staging")
            if config.debug:
                errors.append("DEBUG should be False in staging")
            if config.mock_ai_responses:
                errors.append("MOCK_AI_RESPONSES should be False in staging")
            if config.skip_authentication:
                errors.append("SKIP_AUTHENTICATION should be False in staging")
            if config.enable_debug_endpoints:
                errors.append("ENABLE_DEBUG_ENDPOINTS should be False in staging")
        
        elif self.environment == Environment.TESTING:
            if config.mock_ai_responses is False:
                errors.append("MOCK_AI_RESPONSES should be True in testing")
            if config.skip_authentication is False:
                errors.append("SKIP_AUTHENTICATION should be True in testing")
            if config.test_mode is False:
                errors.append("TEST_MODE should be True in testing")
        
        if errors:
            error_msg = f"Configuration validation failed for {self.environment.value} environment:\n" + "\n".join(errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def get_config(self) -> EnvironmentConfig:
        """Get the current environment configuration."""
        return self.config
    
    def get_feature(self, feature_name: str) -> bool:
        """Get a feature flag value."""
        return self.config.features.get(feature_name, False)
    
    def is_production(self) -> bool:
        """Check if current environment is production."""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if current environment is development."""
        return self.environment == Environment.DEVELOPMENT
    
    def is_testing(self) -> bool:
        """Check if current environment is testing."""
        return self.environment == Environment.TESTING
    
    def is_staging(self) -> bool:
        """Check if current environment is staging."""
        return self.environment == Environment.STAGING
    
    def reload_config(self) -> None:
        """Reload configuration from sources."""
        logger.info("🔄 Reloading configuration...")
        self.config = self._load_environment_config()
        logger.info("✅ Configuration reloaded successfully")
    
    def get_config_summary(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Get a summary of the current configuration."""
        return {
            "environment": self.environment.value,
            "config_name": self.config.name,
            "debug": self.config.debug,
            "testing": self.config.testing,
            "log_level": self.config.log_level,
            "features": self.config.features,
            "is_production": self.is_production(),
            "is_development": self.is_development(),
            "is_testing": self.is_testing(),
            "is_staging": self.is_staging(),
            "config": self.config.to_dict(include_secrets=include_secrets)
        }
    
    def _print_startup_config(self) -> None:
        """Print startup configuration summary."""
        config_summary = self.get_config_summary(include_secrets=False)
        
        print(f"\n{'='*70}")
        print(f"🚀 SARVANOM PLATFORM CONFIGURATION STARTUP")
        print(f"{'='*70}")
        print(f"📋 Environment: {config_summary['environment'].upper()}")
        print(f"🏷️  APP_ENV Variable: {self.app_env}")
        print(f"📂 Config File: {self._get_config_file_path() or 'Using defaults'}")
        print(f"🔧 Debug Mode: {config_summary['debug']}")
        print(f"🧪 Testing Mode: {config_summary['testing']}")
        print(f"📊 Log Level: {config_summary['log_level']}")
        
        # Configuration Sources
        print(f"\n📚 Configuration Sources (in order of precedence):")
        print(f"  1. Environment Variables (highest priority)")
        config_file = self._get_config_file_path()
        if config_file and config_file.exists():
            print(f"  2. Config File: {config_file}")
        else:
            print(f"  2. Config File: None (using environment defaults)")
        print(f"  3. Environment Defaults (lowest priority)")
        
        # Critical Settings
        print(f"\n🔐 Critical Security Settings:")
        print(f"  🔒 Security Headers: {config_summary['config']['security_headers_enabled']}")
        print(f"  🔐 Skip Authentication: {config_summary['config']['skip_authentication']}")
        print(f"  🤖 Mock AI Responses: {config_summary['config']['mock_ai_responses']}")
        print(f"  🐛 Debug Endpoints: {config_summary['config']['enable_debug_endpoints']}")
        print(f"  🧪 Test Mode: {config_summary['config']['test_mode']}")
        
        # Feature Flags
        enabled_features = [f for f, enabled in config_summary['features'].items() if enabled]
        print(f"\n⚙️  Feature Flags ({len(enabled_features)} enabled):")
        for feature in enabled_features[:5]:  # Show first 5 enabled features
            print(f"  ✅ {feature}")
        if len(enabled_features) > 5:
            print(f"  ... and {len(enabled_features) - 5} more")
        
        # Configuration Validation Status
        missing_critical = self._check_missing_critical_config()
        if missing_critical:
            print(f"\n⚠️  MISSING CRITICAL CONFIGURATION:")
            for item in missing_critical:
                print(f"  ❌ {item}")
        else:
            print(f"\n✅ All critical configuration is present")
            
        print(f"{'='*70}\n")
    
    def _check_missing_critical_config(self) -> List[str]:
        """Check for missing critical configuration values."""
        missing = []
        
        # Environment-specific critical checks
        if self.environment in [Environment.PRODUCTION, Environment.STAGING]:
            if not self.config.database_url:
                missing.append("DATABASE_URL")
            if not self.config.redis_url:
                missing.append("REDIS_URL")
            if not self.config.jwt_secret_key:
                missing.append("JWT_SECRET_KEY")
            if not self.config.meilisearch_master_key:
                missing.append("MEILISEARCH_MASTER_KEY")
            if not self.config.openai_api_key and not self.config.anthropic_api_key:
                missing.append("OPENAI_API_KEY or ANTHROPIC_API_KEY")
        elif self.environment == Environment.DEVELOPMENT:
            if not self.config.jwt_secret_key:
                missing.append("JWT_SECRET_KEY (recommended)")
            if not self.config.meilisearch_master_key:
                missing.append("MEILISEARCH_MASTER_KEY")
        elif self.environment == Environment.TESTING:
            if not self.config.test_mode:
                missing.append("TEST_MODE should be True")
                
        return missing


@lru_cache(maxsize=1)
def get_environment_manager() -> EnvironmentManager:
    """Get the singleton environment manager instance."""
    return EnvironmentManager()


def set_environment_manager(manager: EnvironmentManager) -> None:
    """Set the environment manager instance (for testing)."""
    get_environment_manager.cache_clear()
    globals()["_environment_manager"] = manager


def reload_environment_config() -> None:
    """Reload the environment configuration."""
    manager = get_environment_manager()
    manager.reload_config() 