#!/usr/bin/env python3
"""
Update Environment Variable Usage Script.

This script updates all files that use environment variables to use the new
centralized configuration system from shared/core/api/config.py.

It replaces direct os.getenv() calls with the Settings class from the config module.
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Dict, Set, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the mapping of environment variables to Settings attributes
ENV_TO_SETTINGS_MAPPING = {
    # LLM Configuration
    "OLLAMA_ENABLED": "ollama_enabled",
    "OLLAMA_MODEL": "ollama_model", 
    "OLLAMA_BASE_URL": "ollama_base_url",
    "HUGGINGFACE_WRITE_TOKEN": "huggingface_write_token",
    "HUGGINGFACE_READ_TOKEN": "huggingface_read_token",
    "HUGGINGFACE_API_KEY": "huggingface_api_key",
    "HUGGINGFACE_MODEL": "huggingface_model",
    "USE_DYNAMIC_SELECTION": "use_dynamic_selection",
    "PRIORITIZE_FREE_MODELS": "prioritize_free_models",
    "OPENAI_API_KEY": "openai_api_key",
    "OPENAI_LLM_MODEL": "openai_model",
    "OPENAI_EMBEDDING_MODEL": "openai_embedding_model",
    "ANTHROPIC_API_KEY": "anthropic_api_key",
    "ANTHROPIC_MODEL": "anthropic_model",
    "AZURE_OPENAI_API_KEY": "azure_openai_api_key",
    "AZURE_OPENAI_ENDPOINT": "azure_openai_endpoint",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "azure_openai_deployment_name",
    "GOOGLE_API_KEY": "google_api_key",
    "GOOGLE_MODEL": "google_model",
    
    # System Configuration
    "ENVIRONMENT": "environment",
    "LOG_LEVEL": "log_level",
    
    # Database Configuration
    "POSTGRES_HOST": "postgres_host",
    "POSTGRES_PORT": "postgres_port",
    "POSTGRES_DB": "postgres_db",
    "POSTGRES_USER": "postgres_user",
    "POSTGRES_PASSWORD": "postgres_password",
    "DATABASE_URL": "database_url",
    
    # Vector Database Configuration
    "QDRANT_PORT": "qdrant_port",
    "QDRANT_CLOUD_URL": "qdrant_cloud_url",
    "QDRANT_API_KEY": "qdrant_api_key",
    "QDRANT_URL": "qdrant_url",
    "QDRANT_COLLECTION": "qdrant_collection",
    "PINECONE_API_KEY": "pinecone_api_key",
    "PINECONE_ENVIRONMENT": "pinecone_environment",
    "PINECONE_INDEX_NAME": "pinecone_index_name",
    
    # Knowledge Graph Configuration
    "SPARQL_ENDPOINT": "sparql_endpoint",
    "GRAPH_UPDATE_ENABLED": "graph_update_enabled",
    "GRAPH_AUTO_EXTRACT_ENTITIES": "graph_auto_extract_entities",
    "GRAPH_CONFIDENCE_THRESHOLD": "graph_confidence_threshold",
    "GRAPH_MAX_ENTITIES_PER_DOC": "graph_max_entities_per_doc",
    "GRAPH_RELATIONSHIP_TYPES": "graph_relationship_types",
    "ARANGO_DATABASE": "arango_database",
    "ARANGO_HOST": "arango_host",
    "ARANGO_PORT": "arango_port",
    "ARANGO_URL": "arango_url",
    "ARANGO_USERNAME": "arango_username",
    "ARANGO_PASSWORD": "arango_password",
    "ARANGO_USER": "arango_username",
    "ARANGO_PASS": "arango_password",
    "ARANGO_DB": "arango_database",
    
    # MeiliSearch Configuration
    "MEILISEARCH_URL": "meilisearch_url",
    "MEILISEARCH_MASTER_KEY": "meilisearch_master_key",
    "MEILISEARCH_API_KEY": "meilisearch_api_key",
    "MEILISEARCH_INDEX": "meilisearch_index",
    "MEILI_MASTER_KEY": "meilisearch_master_key",
    
    # API Gateway Configuration
    "API_GATEWAY_HOST": "host",
    "API_GATEWAY_PORT": "port",
    "API_GATEWAY_WORKERS": "workers",
    "CORS_ORIGINS": "cors_origins",
    "CORS_ALLOW_CREDENTIALS": "cors_credentials",
    "RATE_LIMIT_REQUESTS_PER_MINUTE": "rate_limit_per_minute",
    "RATE_LIMIT_TOKENS_PER_MINUTE": "rate_limit_per_minute",
    "RATE_LIMIT_BURST_SIZE": "rate_limit_burst",
    
    # Security Configuration
    "SECRET_KEY": "jwt_secret_key",
    "JWT_SECRET_KEY": "jwt_secret_key",
    "JWT_ALGORITHM": "jwt_algorithm",
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "jwt_access_token_expire_minutes",
    "JWT_REFRESH_TOKEN_EXPIRE_DAYS": "jwt_refresh_token_expire_days",
    
    # Redis Configuration
    "REDIS_URL": "redis_url",
    "REDIS_ENABLED": "cache_enabled",
    "REDIS_DB": "redis_url",  # Will be handled in URL
    
    # Monitoring Configuration
    "PROMETHEUS_ENABLED": "metrics_enabled",
    "PROMETHEUS_PORT": "metrics_port",
    "HEALTH_CHECK_INTERVAL": "health_check_interval",
    "HEALTH_CHECK_TIMEOUT": "health_check_interval",
    
    # Analytics Configuration
    "ANALYTICS_ENABLED": "features.advanced_analytics",
    "ANALYTICS_BATCH_SIZE": "cache_max_size",
    "ANALYTICS_FLUSH_INTERVAL": "cache_ttl_seconds",
    
    # Development Configuration
    "DEBUG": "debug",
    "RELOAD": "reload",
    "TESTING": "testing",
    "MOCK_AI_RESPONSES": "mock_ai_responses",
    "SKIP_AUTHENTICATION": "skip_authentication",
    "ENABLE_DEBUG_ENDPOINTS": "enable_debug_endpoints",
    "AUTO_RELOAD": "auto_reload",
    "TEST_MODE": "test_mode",
    "MOCK_PROVIDERS": "mock_providers",
    
    # Service URLs
    "AUTH_SERVICE_URL": "auth_service_url",
    "AUTH_SERVICE_SECRET": "auth_service_secret",
    "SEARCH_SERVICE_URL": "search_service_url",
    "SEARCH_SERVICE_SECRET": "search_service_secret",
    "SYNTHESIS_SERVICE_URL": "synthesis_service_url",
    "SYNTHESIS_SERVICE_SECRET": "synthesis_service_secret",
    "FACTCHECK_SERVICE_URL": "factcheck_service_url",
    "FACTCHECK_SERVICE_SECRET": "factcheck_service_secret",
    "ANALYTICS_SERVICE_URL": "analytics_service_url",
    "ANALYTICS_SERVICE_SECRET": "analytics_service_secret",
    
    # Agent Configuration
    "AGENT_TIMEOUT_SECONDS": "agent_timeout_seconds",
    "AGENT_MAX_RETRIES": "agent_max_retries",
    "AGENT_BACKOFF_FACTOR": "agent_backoff_factor",
    "QUERY_CACHE_TTL_SECONDS": "query_cache_ttl_seconds",
    "QUERY_MAX_LENGTH": "query_max_length",
    "QUERY_MIN_CONFIDENCE": "query_min_confidence",
    
    # Knowledge Graph Agent
    "KG_AGENT_ENABLED": "kg_agent_enabled",
    "KG_AGENT_TIMEOUT": "kg_agent_timeout",
    "KG_MAX_RELATIONSHIP_DEPTH": "kg_max_relationship_depth",
    
    # Docker Configuration
    "DOCKER_ENABLED": "docker_enabled",
    "DOCKER_NETWORK": "docker_network",
    "BACKEND_URL": "backend_url",
    "POSTGRES_URL": "postgres_url",
    "MEILISEARCH_URL": "meilisearch_url",
    "ARANGODB_URL": "arangodb_url",
    "QDRANT_URL": "qdrant_url",
    "OLLAMA_URL": "ollama_url",
    
    # External Integrations
    "SMTP_HOST": "smtp_host",
    "SMTP_PORT": "smtp_port",
    "SMTP_USERNAME": "smtp_username",
    "SMTP_PASSWORD": "smtp_password",
    "SMTP_USE_TLS": "smtp_use_tls",
    "STORAGE_TYPE": "storage_type",
    "STORAGE_BUCKET": "storage_bucket",
    "STORAGE_REGION": "storage_region",
    "AWS_ACCESS_KEY_ID": "aws_access_key_id",
    "AWS_SECRET_ACCESS_KEY": "aws_secret_access_key",
    "AWS_REGION": "aws_region",
    "SLACK_WEBHOOK_URL": "slack_webhook_url",
    "SLACK_CHANNEL": "slack_channel",
    "DISCORD_WEBHOOK_URL": "discord_webhook_url",
    
    # Advanced Configuration
    "CACHE_TTL_SECONDS": "cache_ttl_seconds",
    "CACHE_MAX_SIZE": "cache_max_size",
    "SESSION_SECRET": "session_secret",
    "SESSION_TTL_SECONDS": "session_ttl_seconds",
    "API_VERSION": "api_version",
    "API_DEPRECATION_WARNING_DAYS": "api_deprecation_warning_days",
    
    # Performance Tuning
    "DB_POOL_SIZE": "db_pool_size",
    "DB_MAX_OVERFLOW": "db_max_overflow",
    "DB_POOL_TIMEOUT": "db_pool_timeout",
    "WORKER_PROCESSES": "worker_processes",
    "WORKER_THREADS": "worker_threads",
    "MAX_MEMORY_USAGE_MB": "max_memory_usage_mb",
    "GARBAGE_COLLECTION_INTERVAL": "garbage_collection_interval",
    
    # Backup & Recovery
    "BACKUP_ENABLED": "backup_enabled",
    "BACKUP_INTERVAL_HOURS": "backup_interval_hours",
    "BACKUP_RETENTION_DAYS": "backup_retention_days",
    "RECOVERY_MODE": "recovery_mode",
    "RECOVERY_POINT_RETENTION_DAYS": "recovery_point_retention_days",
    
    # Compliance & Audit
    "AUDIT_LOG_ENABLED": "audit_log_enabled",
    "AUDIT_LOG_LEVEL": "audit_log_level",
    "AUDIT_LOG_RETENTION_DAYS": "audit_log_retention_days",
    "DATA_RETENTION_DAYS": "data_retention_days",
    "ANONYMIZE_OLD_DATA": "anonymize_old_data",
    
    # Security Headers
    "SECURITY_HEADERS_ENABLED": "security_headers_enabled",
    "CONTENT_SECURITY_POLICY": "content_security_policy",
    
    # Input Validation
    "MAX_REQUEST_SIZE": "max_request_size",
    "MAX_QUERY_LENGTH": "max_query_length",
    
    # Rate Limiting per User
    "USER_RATE_LIMIT_REQUESTS_PER_MINUTE": "user_rate_limit_requests_per_minute",
    "USER_RATE_LIMIT_TOKENS_PER_MINUTE": "user_rate_limit_tokens_per_minute",
    
    # Test Configuration
    "TEST_DATABASE_URL": "test_database_url",
    "TEST_REDIS_URL": "test_redis_url",
    
    # Service Identification
    "SERVICE_NAME": "service_name",
    "VERSION": "version",
    
    # Feature Flags
    "FEATURE_EXPERT_REVIEW": "features.expert_review",
    "FEATURE_REAL_TIME_COLLABORATION": "features.real_time_collaboration",
    "FEATURE_ADVANCED_ANALYTICS": "features.advanced_analytics",
    "FEATURE_MULTI_TENANT": "features.multi_tenant",
    "FEATURE_SSO": "features.sso",
}


def find_python_files(directory: Path) -> List[Path]:
    """Find all Python files in the directory."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'env', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    return python_files


def extract_env_vars_from_file(file_path: Path) -> Set[str]:
    """Extract environment variable names used in a file."""
    env_vars = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find os.getenv calls
        getenv_pattern = r'os\.getenv\([\'"]([^\'"]+)[\'"]'
        matches = re.findall(getenv_pattern, content)
        env_vars.update(matches)
        
        # Find os.environ access
        environ_pattern = r'os\.environ\[[\'"]([^\'"]+)[\'"]'
        matches = re.findall(environ_pattern, content)
        env_vars.update(matches)
        
        # Find os.environ.get calls
        environ_get_pattern = r'os\.environ\.get\([\'"]([^\'"]+)[\'"]'
        matches = re.findall(environ_get_pattern, content)
        env_vars.update(matches)
        
    except Exception as e:
        logger.warning(f"Error reading {file_path}: {e}")
    
    return env_vars


def generate_settings_import(file_path: Path) -> str:
    """Generate the appropriate import statement for the settings."""
    # Calculate relative path to shared/core/api/config.py
    current_dir = file_path.parent
    config_path = Path("shared/core/api/config.py")
    
    # Calculate relative path
    try:
        relative_path = os.path.relpath(config_path, current_dir)
        if relative_path.startswith('.'):
            return f"from {relative_path.replace('/', '.').replace('.py', '')} import get_settings"
        else:
            return "from shared.core.api.config import get_settings"
    except ValueError:
        return "from shared.core.api.config import get_settings"


def update_file_with_settings(file_path: Path) -> bool:
    """Update a file to use the Settings class instead of direct environment access."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Add import if not present
        if "from shared.core.api.config import get_settings" not in content:
            import_line = generate_settings_import(file_path)
            # Find the best place to add the import
            lines = content.split('\n')
            import_section_end = 0
            
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    import_section_end = i + 1
                elif line.strip() and not line.strip().startswith('#'):
                    break
            
            lines.insert(import_section_end, import_line)
            content = '\n'.join(lines)
        
        # Add settings initialization if not present
        if "get_settings()" not in content:
            # Find a good place to add settings initialization (after imports)
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip() and not line.strip().startswith(('import ', 'from ', '#')):
                    # Add settings initialization before the first non-import line
                    lines.insert(i, "settings = get_settings()")
                    break
            content = '\n'.join(lines)
        
        # Replace os.getenv calls
        for env_var, setting_path in ENV_TO_SETTINGS_MAPPING.items():
            # Handle nested settings (e.g., features.expert_review)
            if '.' in setting_path:
                setting_parts = setting_path.split('.')
                setting_access = f"settings.{'.'.join(setting_parts)}"
            else:
                setting_access = f"settings.{setting_path}"
            
            # Replace os.getenv("ENV_VAR", default) with settings.setting_path
            pattern = rf'os\.getenv\([\'"]({re.escape(env_var)})[\'"](?:,\s*([^)]+))?\)'
            
            def replace_getenv(match):
                env_name = match.group(1)
                default = match.group(2)
                
                if default:
                    # If there's a default, we need to handle it carefully
                    if setting_path in ['ollama_enabled', 'use_dynamic_selection', 'prioritize_free_models', 
                                      'cache_enabled', 'metrics_enabled', 'debug', 'reload', 'testing',
                                      'mock_ai_responses', 'skip_authentication', 'enable_debug_endpoints',
                                      'auto_reload', 'test_mode', 'mock_providers', 'backup_enabled',
                                      'recovery_mode', 'audit_log_enabled', 'anonymize_old_data',
                                      'security_headers_enabled', 'smtp_use_tls']:
                        # Boolean settings
                        return f"getattr({setting_access}, 'value', {default}) if hasattr({setting_access}, 'value') else {setting_access}"
                    else:
                        return f"{setting_access} or {default}"
                else:
                    return setting_access
            
            content = re.sub(pattern, replace_getenv, content)
            
            # Replace os.environ["ENV_VAR"] with settings.setting_path
            pattern = rf'os\.environ\[[\'"]({re.escape(env_var)})[\'"]\]'
            content = re.sub(pattern, setting_access, content)
            
            # Replace os.environ.get("ENV_VAR") with settings.setting_path
            pattern = rf'os\.environ\.get\([\'"]({re.escape(env_var)})[\'"]\)'
            content = re.sub(pattern, setting_access, content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error updating {file_path}: {e}")
        return False


def main():
    """Main function to update all files."""
    project_root = Path(".")
    
    # Find all Python files
    python_files = find_python_files(project_root)
    
    # Skip certain files
    skip_files = {
        "shared/core/api/config.py",  # The config file itself
        "update_env_usage.py",  # This script
        "test_env_key_value_pairs.py",  # Test file that should keep direct env access
    }
    
    python_files = [f for f in python_files if str(f) not in skip_files]
    
    logger.info(f"Found {len(python_files)} Python files to process")
    
    updated_files = []
    
    for file_path in python_files:
        logger.info(f"Processing {file_path}")
        
        # Extract environment variables used in the file
        env_vars = extract_env_vars_from_file(file_path)
        
        if env_vars:
            logger.info(f"  Found environment variables: {env_vars}")
            
            # Check if any of the env vars are in our mapping
            mapped_vars = env_vars.intersection(set(ENV_TO_SETTINGS_MAPPING.keys()))
            
            if mapped_vars:
                logger.info(f"  Updating {len(mapped_vars)} mapped variables: {mapped_vars}")
                
                if update_file_with_settings(file_path):
                    updated_files.append(file_path)
                    logger.info(f"  ✅ Updated {file_path}")
                else:
                    logger.info(f"  ⚠️ No changes needed for {file_path}")
            else:
                logger.info(f"  ⚠️ No mapped environment variables found in {file_path}")
        else:
            logger.info(f"  ⚠️ No environment variables found in {file_path}")
    
    logger.info(f"\nSummary:")
    logger.info(f"  Total files processed: {len(python_files)}")
    logger.info(f"  Files updated: {len(updated_files)}")
    
    if updated_files:
        logger.info(f"\nUpdated files:")
        for file_path in updated_files:
            logger.info(f"  - {file_path}")
    
    logger.info(f"\nEnvironment variable mapping:")
    for env_var, setting_path in ENV_TO_SETTINGS_MAPPING.items():
        logger.info(f"  {env_var} -> settings.{setting_path}")


if __name__ == "__main__":
    main() 