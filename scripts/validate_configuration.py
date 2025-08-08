#!/usr/bin/env python3
"""
Configuration Validation Script for SarvanOM.

This script validates that all required environment variables are set
and that the configuration system is working properly.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import structlog

logger = structlog.get_logger(__name__)

# Required environment variables for different environments
REQUIRED_VARS = {
    "development": [
        "APP_ENV",
        "DATABASE_URL",
        "REDIS_URL",
        "MEILISEARCH_URL",
        "ARANGODB_URL",
    ],
    "testing": [
        "APP_ENV",
        "DATABASE_URL",
        "REDIS_URL",
        "MEILISEARCH_URL",
        "ARANGODB_URL",
    ],
    "staging": [
        "APP_ENV",
        "DATABASE_URL",
        "REDIS_URL",
        "MEILISEARCH_URL",
        "ARANGODB_URL",
        "JWT_SECRET_KEY",
    ],
    "production": [
        "APP_ENV",
        "DATABASE_URL",
        "REDIS_URL",
        "MEILISEARCH_URL",
        "ARANGODB_URL",
        "JWT_SECRET_KEY",
        "MEILISEARCH_MASTER_KEY",
    ]
}

# Recommended variables for production
RECOMMENDED_VARS = {
    "production": [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "SENTRY_DSN",
        "VECTOR_DB_API_KEY",
        "ARANGODB_PASSWORD",
        "REDIS_PASSWORD",
    ]
}

# Security-sensitive variables that should be masked in logs
SENSITIVE_VARS = [
    "JWT_SECRET_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "MEILISEARCH_MASTER_KEY",
    "VECTOR_DB_API_KEY",
    "ARANGODB_PASSWORD",
    "REDIS_PASSWORD",
    "DATABASE_URL",
    "REDIS_URL",
    "SENTRY_DSN",
]

def check_environment_variables() -> Tuple[bool, List[str], List[str]]:
    """
    Check if all required environment variables are set.
    
    Returns:
        Tuple of (is_valid, missing_vars, warnings)
    """
    app_env = os.getenv("APP_ENV", "development").lower()
    
    if app_env not in REQUIRED_VARS:
        logger.warning(f"Unknown environment '{app_env}', using development requirements")
        app_env = "development"
    
    required_vars = REQUIRED_VARS[app_env]
    recommended_vars = RECOMMENDED_VARS.get(app_env, [])
    
    missing_vars = []
    warnings = []
    
    # Check required variables
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    # Check recommended variables
    for var in recommended_vars:
        if not os.getenv(var):
            warnings.append(f"Recommended variable '{var}' is not set for {app_env} environment")
    
    is_valid = len(missing_vars) == 0
    
    return is_valid, missing_vars, warnings

def validate_configuration_loading() -> Tuple[bool, List[str]]:
    """
    Test if the configuration system loads properly.
    
    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []
    
    try:
        # Test environment manager
        from shared.core.config.environment_manager import get_environment_manager
        env_manager = get_environment_manager()
        config = env_manager.get_config()
        
        logger.info("✅ Environment manager loaded successfully")
        logger.info(f"📋 Environment: {config.name}")
        logger.info(f"🔧 Debug mode: {config.debug}")
        
    except Exception as e:
        errors.append(f"Failed to load environment manager: {str(e)}")
    
    try:
        # Test central config
        from shared.core.config.central_config import get_config
        central_config = get_config()
        
        logger.info("✅ Central configuration loaded successfully")
        
    except Exception as e:
        errors.append(f"Failed to load central configuration: {str(e)}")
    
    return len(errors) == 0, errors

def check_security_configuration() -> Tuple[bool, List[str]]:
    """
    Check security-related configuration.
    
    Returns:
        Tuple of (is_secure, warnings)
    """
    warnings = []
    app_env = os.getenv("APP_ENV", "development").lower()
    
    # Check JWT secret
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    if not jwt_secret:
        warnings.append("JWT_SECRET_KEY is not set - authentication will not work")
    elif len(jwt_secret) < 32:
        warnings.append("JWT_SECRET_KEY should be at least 32 characters long")
    
    # Check for default passwords
    arango_pass = os.getenv("ARANGODB_PASSWORD", "")
    if app_env == "production" and not arango_pass:
        warnings.append("ARANGODB_PASSWORD is not set for production")
    
    # Check for debug mode in production
    debug_mode = os.getenv("DEBUG", "false").lower() in ["true", "1", "yes"]
    if app_env == "production" and debug_mode:
        warnings.append("DEBUG mode is enabled in production - this is not recommended")
    
    # Check CORS configuration
    cors_origins = os.getenv("CORS_ORIGINS", "")
    if app_env == "production" and "*" in cors_origins:
        warnings.append("CORS_ORIGINS contains wildcard (*) in production - security risk")
    
    return len(warnings) == 0, warnings

def check_database_connections() -> Tuple[bool, List[str]]:
    """
    Test database connections if possible.
    
    Returns:
        Tuple of (all_connected, connection_errors)
    """
    connection_errors = []
    
    # Test Redis connection
    try:
        import redis.asyncio as redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        r = redis.from_url(redis_url)
        r.ping()
        logger.info("✅ Redis connection test passed")
    except Exception as e:
        connection_errors.append(f"Redis connection failed: {str(e)}")
    
    # Test database connection
    try:
        import asyncpg
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            # Extract connection info for testing
            if database_url.startswith("postgresql://"):
                # Parse PostgreSQL URL
                import urllib.parse
                parsed = urllib.parse.urlparse(database_url)
                host = parsed.hostname or "localhost"
                port = parsed.port or 5432
                user = parsed.username or "postgres"
                password = parsed.password or ""
                database = parsed.path.lstrip("/") or "sarvanom"
                
                # Test connection
                conn = await asyncpg.connect(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=database
                )
                await conn.close()
                logger.info("✅ Database connection test passed")
            else:
                logger.info("⚠️ Database connection test skipped (not PostgreSQL)")
    except Exception as e:
        connection_errors.append(f"Database connection failed: {str(e)}")
    
    return len(connection_errors) == 0, connection_errors

def print_configuration_summary():
    """Print a summary of the current configuration."""
    print("\n" + "="*60)
    print("🔧 CONFIGURATION SUMMARY")
    print("="*60)
    
    # Environment info
    app_env = os.getenv("APP_ENV", "development")
    debug_mode = os.getenv("DEBUG", "false").lower() in ["true", "1", "yes"]
    
    print(f"🌍 Environment: {app_env}")
    print(f"🐛 Debug mode: {debug_mode}")
    print(f"📝 Log level: {os.getenv('LOG_LEVEL', 'INFO')}")
    
    # Service URLs
    print("\n🔗 Service URLs:")
    services = [
        ("Database", "DATABASE_URL"),
        ("Redis", "REDIS_URL"),
        ("MeiliSearch", "MEILISEARCH_URL"),
        ("ArangoDB", "ARANGODB_URL"),
        ("Vector DB", "VECTOR_DB_URL"),
    ]
    
    for service_name, var_name in services:
        value = os.getenv(var_name, "Not set")
        if var_name in SENSITIVE_VARS:
            value = "***REDACTED***" if value != "Not set" else value
        print(f"  {service_name}: {value}")
    
    # AI Providers
    print("\n🤖 AI Providers:")
    providers = [
        ("OpenAI", "OPENAI_API_KEY"),
        ("Anthropic", "ANTHROPIC_API_KEY"),
        ("Ollama", "OLLAMA_BASE_URL"),
    ]
    
    for provider_name, var_name in providers:
        value = os.getenv(var_name, "Not set")
        if var_name in SENSITIVE_VARS:
            value = "***REDACTED***" if value != "Not set" else value
        print(f"  {provider_name}: {value}")
    
    print("="*60)

def main():
    """Main validation function."""
    print("🔍 Validating SarvanOM Configuration...")
    print("="*60)
    
    # Check environment variables
    is_valid, missing_vars, warnings = check_environment_variables()
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print()
    
    if warnings:
        print("⚠️ Configuration warnings:")
        for warning in warnings:
            print(f"  - {warning}")
        print()
    
    # Validate configuration loading
    config_valid, config_errors = validate_configuration_loading()
    
    if config_errors:
        print("❌ Configuration loading errors:")
        for error in config_errors:
            print(f"  - {error}")
        print()
    
    # Check security
    is_secure, security_warnings = check_security_configuration()
    
    if security_warnings:
        print("⚠️ Security warnings:")
        for warning in security_warnings:
            print(f"  - {warning}")
        print()
    
    # Print configuration summary
    print_configuration_summary()
    
    # Final status
    if is_valid and config_valid:
        print("✅ Configuration validation passed!")
        if not security_warnings:
            print("✅ Security configuration looks good!")
        else:
            print("⚠️ Security warnings found - please review")
        return 0
    else:
        print("❌ Configuration validation failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 