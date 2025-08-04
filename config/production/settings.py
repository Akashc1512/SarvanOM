"""
Production settings configuration for the Universal Knowledge Platform.

This module provides environment-based configuration management for production
deployment with proper validation, defaults, and security considerations.
"""

import os
from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field, validator
from pathlib import Path


class ProductionSettings(BaseSettings):
    """Production configuration settings with validation."""
    
    # Application Settings
    APP_NAME: str = Field(default="Universal Knowledge Platform", description="Application name")
    APP_VERSION: str = Field(default="2.4.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Debug mode (disabled in production)")
    ENVIRONMENT: str = Field(default="production", description="Environment name")
    
    # Server Settings
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    WORKERS: int = Field(default=4, description="Number of worker processes")
    WORKER_CLASS: str = Field(default="uvicorn.workers.UvicornWorker", description="Worker class")
    
    # Database Settings
    DATABASE_URL: str = Field(..., description="Database connection URL")
    DATABASE_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=30, description="Database max overflow")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, description="Database pool timeout")
    
    # Redis Settings
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    REDIS_POOL_SIZE: int = Field(default=10, description="Redis connection pool size")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    
    # Security Settings
    SECRET_KEY: str = Field(..., description="Application secret key")
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiry")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiry")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Rate limit per minute")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, description="Rate limit per hour")
    RATE_LIMIT_PER_DAY: int = Field(default=10000, description="Rate limit per day")
    
    # CORS Settings
    CORS_ORIGINS: list = Field(default=["*"], description="CORS allowed origins")
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="CORS allow credentials")
    CORS_ALLOW_METHODS: list = Field(default=["*"], description="CORS allowed methods")
    CORS_ALLOW_HEADERS: list = Field(default=["*"], description="CORS allowed headers")
    
    # Logging Settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format (json or text)")
    LOG_FILE: Optional[str] = Field(default=None, description="Log file path")
    LOG_MAX_SIZE: int = Field(default=100, description="Log max size in MB")
    LOG_BACKUP_COUNT: int = Field(default=5, description="Log backup count")
    
    # Monitoring Settings
    METRICS_ENABLED: bool = Field(default=True, description="Enable metrics collection")
    METRICS_PORT: int = Field(default=9090, description="Metrics server port")
    HEALTH_CHECK_INTERVAL: int = Field(default=30, description="Health check interval in seconds")
    
    # AI Service Settings
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-4", description="OpenAI model name")
    OPENAI_MAX_TOKENS: int = Field(default=4000, description="OpenAI max tokens")
    OPENAI_TEMPERATURE: float = Field(default=0.7, description="OpenAI temperature")
    
    # Vector Database Settings
    PINECONE_API_KEY: str = Field(..., description="Pinecone API key")
    PINECONE_ENVIRONMENT: str = Field(..., description="Pinecone environment")
    PINECONE_INDEX_NAME: str = Field(..., description="Pinecone index name")
    
    # File Storage Settings
    UPLOAD_DIR: str = Field(default="/app/uploads", description="Upload directory")
    MAX_FILE_SIZE: int = Field(default=100, description="Max file size in MB")
    ALLOWED_EXTENSIONS: list = Field(default=[".pdf", ".txt", ".doc", ".docx"], description="Allowed file extensions")
    
    # Cache Settings
    CACHE_TTL: int = Field(default=3600, description="Cache TTL in seconds")
    CACHE_MAX_SIZE: int = Field(default=1000, description="Cache max size")
    
    # Service Timeouts
    SERVICE_TIMEOUT: int = Field(default=30, description="Service timeout in seconds")
    REQUEST_TIMEOUT: int = Field(default=60, description="Request timeout in seconds")
    
    # Backup Settings
    BACKUP_ENABLED: bool = Field(default=True, description="Enable automated backups")
    BACKUP_INTERVAL: int = Field(default=24, description="Backup interval in hours")
    BACKUP_RETENTION_DAYS: int = Field(default=30, description="Backup retention in days")
    
    @validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        """Validate secret key length."""
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')
        return v
    
    @validator('DATABASE_URL')
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v.startswith(('postgresql://', 'mysql://', 'sqlite://')):
            raise ValueError('DATABASE_URL must be a valid database URL')
        return v
    
    @validator('REDIS_URL')
    def validate_redis_url(cls, v):
        """Validate Redis URL format."""
        if not v.startswith('redis://'):
            raise ValueError('REDIS_URL must be a valid Redis URL')
        return v
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'LOG_LEVEL must be one of {valid_levels}')
        return v.upper()
    
    @validator('CORS_ORIGINS')
    def validate_cors_origins(cls, v):
        """Validate CORS origins."""
        if not isinstance(v, list):
            raise ValueError('CORS_ORIGINS must be a list')
        return v
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def get_settings() -> ProductionSettings:
    """Get production settings instance."""
    return ProductionSettings()


def get_database_config() -> Dict[str, Any]:
    """Get database configuration."""
    settings = get_settings()
    return {
        "url": settings.DATABASE_URL,
        "pool_size": settings.DATABASE_POOL_SIZE,
        "max_overflow": settings.DATABASE_MAX_OVERFLOW,
        "pool_timeout": settings.DATABASE_POOL_TIMEOUT,
    }


def get_redis_config() -> Dict[str, Any]:
    """Get Redis configuration."""
    settings = get_settings()
    return {
        "url": settings.REDIS_URL,
        "pool_size": settings.REDIS_POOL_SIZE,
        "password": settings.REDIS_PASSWORD,
    }


def get_security_config() -> Dict[str, Any]:
    """Get security configuration."""
    settings = get_settings()
    return {
        "secret_key": settings.SECRET_KEY,
        "algorithm": settings.ALGORITHM,
        "access_token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        "refresh_token_expire_days": settings.REFRESH_TOKEN_EXPIRE_DAYS,
    }


def get_rate_limit_config() -> Dict[str, Any]:
    """Get rate limiting configuration."""
    settings = get_settings()
    return {
        "per_minute": settings.RATE_LIMIT_PER_MINUTE,
        "per_hour": settings.RATE_LIMIT_PER_HOUR,
        "per_day": settings.RATE_LIMIT_PER_DAY,
    }


def get_cors_config() -> Dict[str, Any]:
    """Get CORS configuration."""
    settings = get_settings()
    return {
        "origins": settings.CORS_ORIGINS,
        "allow_credentials": settings.CORS_ALLOW_CREDENTIALS,
        "allow_methods": settings.CORS_ALLOW_METHODS,
        "allow_headers": settings.CORS_ALLOW_HEADERS,
    }


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration."""
    settings = get_settings()
    return {
        "level": settings.LOG_LEVEL,
        "format": settings.LOG_FORMAT,
        "file": settings.LOG_FILE,
        "max_size": settings.LOG_MAX_SIZE,
        "backup_count": settings.LOG_BACKUP_COUNT,
    }


def get_monitoring_config() -> Dict[str, Any]:
    """Get monitoring configuration."""
    settings = get_settings()
    return {
        "metrics_enabled": settings.METRICS_ENABLED,
        "metrics_port": settings.METRICS_PORT,
        "health_check_interval": settings.HEALTH_CHECK_INTERVAL,
    }


def get_ai_config() -> Dict[str, Any]:
    """Get AI service configuration."""
    settings = get_settings()
    return {
        "openai_api_key": settings.OPENAI_API_KEY,
        "openai_model": settings.OPENAI_MODEL,
        "openai_max_tokens": settings.OPENAI_MAX_TOKENS,
        "openai_temperature": settings.OPENAI_TEMPERATURE,
    }


def get_vector_db_config() -> Dict[str, Any]:
    """Get vector database configuration."""
    settings = get_settings()
    return {
        "pinecone_api_key": settings.PINECONE_API_KEY,
        "pinecone_environment": settings.PINECONE_ENVIRONMENT,
        "pinecone_index_name": settings.PINECONE_INDEX_NAME,
    }


def get_file_storage_config() -> Dict[str, Any]:
    """Get file storage configuration."""
    settings = get_settings()
    return {
        "upload_dir": settings.UPLOAD_DIR,
        "max_file_size": settings.MAX_FILE_SIZE,
        "allowed_extensions": settings.ALLOWED_EXTENSIONS,
    }


def get_cache_config() -> Dict[str, Any]:
    """Get cache configuration."""
    settings = get_settings()
    return {
        "ttl": settings.CACHE_TTL,
        "max_size": settings.CACHE_MAX_SIZE,
    }


def get_timeout_config() -> Dict[str, Any]:
    """Get timeout configuration."""
    settings = get_settings()
    return {
        "service_timeout": settings.SERVICE_TIMEOUT,
        "request_timeout": settings.REQUEST_TIMEOUT,
    }


def get_backup_config() -> Dict[str, Any]:
    """Get backup configuration."""
    settings = get_settings()
    return {
        "enabled": settings.BACKUP_ENABLED,
        "interval": settings.BACKUP_INTERVAL,
        "retention_days": settings.BACKUP_RETENTION_DAYS,
    }


# Global settings instance
settings = get_settings() 