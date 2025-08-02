#!/usr/bin/env python3
"""
Script to add missing critical environment variables to .env file.
"""

import os
import re
from typing import List, Dict

def read_env_file() -> List[str]:
    """Read the current .env file."""
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            return f.readlines()
    except FileNotFoundError:
        return []

def write_env_file(lines: List[str]):
    """Write lines to .env file."""
    with open('.env', 'w', encoding='utf-8') as f:
        f.writelines(lines)

def get_missing_critical_keys() -> Dict[str, str]:
    """Get critical missing keys that should be added to .env."""
    return {
        # Core System - High Priority
        "ARANGO_USERNAME": "root",
        "ARANGO_PASSWORD": "your_arangodb_password_here",
        "MEILISEARCH_API_KEY": "your_meilisearch_api_key_here",
        "MEILISEARCH_MASTER_KEY": "your_meilisearch_master_key_here",
        "MEILISEARCH_INDEX": "knowledge_base",
        "VECTOR_DB_URL": "http://localhost:6333",
        
        # Authentication - High Priority
        "ADMIN_API_KEY": "your_admin_api_key_here",
        "USER_API_KEY": "your_user_api_key_here",
        "READONLY_API_KEY": "your_readonly_api_key_here",
        "ADMIN_RATE_LIMIT": "1000",
        "USER_RATE_LIMIT": "100",
        "READONLY_RATE_LIMIT": "50",
        
        # LLM Providers - High Priority
        "HUGGINGFACE_API_KEY": "your_huggingface_api_key_here",
        "HUGGINGFACE_READ_TOKEN": "your_hf_read_token_here",
        "HUGGINGFACE_WRITE_TOKEN": "your_hf_write_token_here",
        "HUGGINGFACE_MODEL": "microsoft/DialoGPT-medium",
        "LLM_PROVIDER": "openai",
        "OPENAI_BASE_URL": "https://api.openai.com/v1",
        "OPENAI_MODEL": "gpt-4",
        "USE_MOCK_LLM": "false",
        "GROQ_API_KEY": "your_groq_api_key_here",
        
        # Database Configuration - Medium Priority
        "DATABASE_ENCRYPTION_KEY": "your_encryption_key_here",
        "DATABASE_NAME": "knowledge_base",
        "DB_HOST": "localhost",
        "DB_NAME": "universal_knowledge",
        "DB_PASSWORD": "your_db_password_here",
        "DB_PORT": "5432",
        "DB_USER": "your_db_user_here",
        
        # Agent Configuration - Medium Priority
        "AGENT_TIMEOUT_MS": "5000",
        "DEFAULT_TOKEN_BUDGET": "1000",
        "DAILY_TOKEN_BUDGET": "100000",
        "CONFIDENCE_THRESHOLD": "0.7",
        
        # Connection Pool - Medium Priority
        "CONNECTION_POOL_SIZE": "10",
        "CONNECTION_POOL_TIMEOUT": "30.0",
        "CIRCUIT_BREAKER_FAILURE_THRESHOLD": "5",
        "CIRCUIT_BREAKER_TIMEOUT": "60",
        "MAX_KEEPALIVE_TIME": "300",
        
        # Search & Vector Database - Medium Priority
        "MEILISEARCH_HOST": "localhost",
        "MEILISEARCH_PORT": "7700",
        "QDRANT_API_KEY": "your_qdrant_api_key_here",
        "QDRANT_HOST": "localhost",
        "QDRANT_PASSWORD": "your_qdrant_password_here",
        "QDRANT_PORT": "6333",
        "QDRANT_USERNAME": "your_qdrant_username_here",
        "VECTOR_DB_HOST": "localhost",
        
        # OAuth & External Services - Low Priority
        "GITHUB_CLIENT_ID": "your_github_client_id_here",
        "GITHUB_CLIENT_SECRET": "your_github_client_secret_here",
        "GITHUB_REDIRECT_URI": "http://localhost:3000/auth/github/callback",
        "GOOGLE_CLIENT_ID": "your_google_client_id_here",
        "GOOGLE_CLIENT_SECRET": "your_google_client_secret_here",
        "GOOGLE_CUSTOM_SEARCH_CX": "your_google_cse_id_here",
        "GOOGLE_REDIRECT_URI": "http://localhost:3000/auth/google/callback",
        
        # Monitoring & Logging - Low Priority
        "LOG_QUERY_CONTENT": "true",
        "MESSAGE_TTL_MS": "30000",
        "PROMETHEUS_MULTIPROC_DIR": "/tmp",
        "PYTHON_VERSION": "3.9",
        "UKP_ACCESS_LOG": "true",
        "UKP_HOST": "0.0.0.0",
        "UKP_LOG_LEVEL": "info",
        "UKP_PORT": "8000",
        "UKP_RELOAD": "false",
        "UKP_WORKERS": "1",
        
        # Testing - Low Priority
        "LOCUST_MAX_WAIT": "1000",
        "LOCUST_MIN_WAIT": "1000",
        "LOCUST_USERS": "10",
        "MAX_PAYLOAD_SIZE": "10485760",
        "MAX_SOURCE_AGE_DAYS": "365",
        "MIN_SOURCE_CONFIDENCE": "0.6",
        "TEST_API_BASE_URL": "http://localhost:8000",
        "TEST_CONCURRENT_REQUESTS": "10",
        "TEST_CONCURRENT_USERS": "5",
        "TEST_CPU_THRESHOLD_PERCENT": "80",
        "TEST_DURATION_SECONDS": "60",
        "TEST_ERROR_RATE_THRESHOLD": "5",
        "TEST_MAX_RESPONSE_TIME_MS": "5000",
        "TEST_MEMORY_THRESHOLD_MB": "1024",
        "TEST_RAMP_UP_SECONDS": "10",
        "TEST_RATE_LIMIT_ATTEMPTS": "100",
        "TEST_RESPONSE_TIME_LIMIT": "5000",
        "TEST_SQL_INJECTION_ATTEMPTS": "10",
        "TEST_TARGET_RPS": "100",
        "TEST_THROUGHPUT_RPS": "50",
        "TEST_TIMEOUT": "30",
        "TEST_XSS_ATTEMPTS": "10",
        
        # Email & External Services - Low Priority
        "SMTP_HOST": "smtp.gmail.com",
        "SMTP_PASSWORD": "your_smtp_password_here",
        "SMTP_PORT": "587",
        "SMTP_USERNAME": "your_smtp_username_here",
    }

def get_existing_keys(env_lines: List[str]) -> set:
    """Extract existing keys from .env file."""
    existing_keys = set()
    for line in env_lines:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key = line.split('=')[0].strip()
            existing_keys.add(key)
    return existing_keys

def add_missing_keys():
    """Add missing critical keys to .env file."""
    print("🔧 Adding missing critical environment variables to .env file...")
    
    # Read current .env file
    env_lines = read_env_file()
    existing_keys = get_existing_keys(env_lines)
    
    # Get missing critical keys
    missing_keys = get_missing_critical_keys()
    
    # Filter out keys that already exist
    keys_to_add = {k: v for k, v in missing_keys.items() if k not in existing_keys}
    
    if not keys_to_add:
        print("✅ No missing critical keys found!")
        return
    
    print(f"📝 Adding {len(keys_to_add)} missing critical keys...")
    
    # Add section headers and keys
    new_lines = []
    
    # Add to existing file
    new_lines.extend(env_lines)
    
    # Add missing keys with proper organization
    if keys_to_add:
        new_lines.append("\n# ============================================================================\n")
        new_lines.append("# MISSING CRITICAL ENVIRONMENT VARIABLES (AUTO-ADDED)\n")
        new_lines.append("# ============================================================================\n")
        
        # Group keys by category
        categories = {
            "Core System": ["ARANGO_USERNAME", "ARANGO_PASSWORD", "MEILISEARCH_API_KEY", "MEILISEARCH_MASTER_KEY", "MEILISEARCH_INDEX", "VECTOR_DB_URL"],
            "Authentication": ["ADMIN_API_KEY", "USER_API_KEY", "READONLY_API_KEY", "ADMIN_RATE_LIMIT", "USER_RATE_LIMIT", "READONLY_RATE_LIMIT"],
            "LLM Providers": ["HUGGINGFACE_API_KEY", "HUGGINGFACE_READ_TOKEN", "HUGGINGFACE_WRITE_TOKEN", "HUGGINGFACE_MODEL", "LLM_PROVIDER", "OPENAI_BASE_URL", "OPENAI_MODEL", "USE_MOCK_LLM", "GROQ_API_KEY"],
            "Database": ["DATABASE_ENCRYPTION_KEY", "DATABASE_NAME", "DB_HOST", "DB_NAME", "DB_PASSWORD", "DB_PORT", "DB_USER"],
            "Agent Config": ["AGENT_TIMEOUT_MS", "DEFAULT_TOKEN_BUDGET", "DAILY_TOKEN_BUDGET", "CONFIDENCE_THRESHOLD"],
            "Connection Pool": ["CONNECTION_POOL_SIZE", "CONNECTION_POOL_TIMEOUT", "CIRCUIT_BREAKER_FAILURE_THRESHOLD", "CIRCUIT_BREAKER_TIMEOUT", "MAX_KEEPALIVE_TIME"],
            "Search & Vector": ["MEILISEARCH_HOST", "MEILISEARCH_PORT", "QDRANT_API_KEY", "QDRANT_HOST", "QDRANT_PASSWORD", "QDRANT_PORT", "QDRANT_USERNAME", "VECTOR_DB_HOST"],
            "OAuth & External": ["GITHUB_CLIENT_ID", "GITHUB_CLIENT_SECRET", "GITHUB_REDIRECT_URI", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_CUSTOM_SEARCH_CX", "GOOGLE_REDIRECT_URI"],
            "Monitoring": ["LOG_QUERY_CONTENT", "MESSAGE_TTL_MS", "PROMETHEUS_MULTIPROC_DIR", "PYTHON_VERSION", "UKP_ACCESS_LOG", "UKP_HOST", "UKP_LOG_LEVEL", "UKP_PORT", "UKP_RELOAD", "UKP_WORKERS"],
            "Testing": ["LOCUST_MAX_WAIT", "LOCUST_MIN_WAIT", "LOCUST_USERS", "MAX_PAYLOAD_SIZE", "MAX_SOURCE_AGE_DAYS", "MIN_SOURCE_CONFIDENCE", "TEST_API_BASE_URL", "TEST_CONCURRENT_REQUESTS", "TEST_CONCURRENT_USERS", "TEST_CPU_THRESHOLD_PERCENT", "TEST_DURATION_SECONDS", "TEST_ERROR_RATE_THRESHOLD", "TEST_MAX_RESPONSE_TIME_MS", "TEST_MEMORY_THRESHOLD_MB", "TEST_RAMP_UP_SECONDS", "TEST_RATE_LIMIT_ATTEMPTS", "TEST_RESPONSE_TIME_LIMIT", "TEST_SQL_INJECTION_ATTEMPTS", "TEST_TARGET_RPS", "TEST_THROUGHPUT_RPS", "TEST_TIMEOUT", "TEST_XSS_ATTEMPTS"],
            "Email": ["SMTP_HOST", "SMTP_PASSWORD", "SMTP_PORT", "SMTP_USERNAME"]
        }
        
        for category, category_keys in categories.items():
            # Filter keys that are actually missing
            missing_category_keys = {k: keys_to_add[k] for k in category_keys if k in keys_to_add}
            
            if missing_category_keys:
                new_lines.append(f"\n# {category}\n")
                for key, value in missing_category_keys.items():
                    new_lines.append(f"{key}={value}\n")
    
    # Write updated .env file
    write_env_file(new_lines)
    
    print(f"✅ Successfully added {len(keys_to_add)} missing critical keys to .env file")
    print("\n📋 Added keys by category:")
    for category, category_keys in categories.items():
        missing_category_keys = {k: keys_to_add[k] for k in category_keys if k in keys_to_add}
        if missing_category_keys:
            print(f"   {category}: {len(missing_category_keys)} keys")
    
    print("\n⚠️ Remember to:")
    print("   1. Replace placeholder values with actual credentials")
    print("   2. Test the configuration after updating")
    print("   3. Keep sensitive keys secure")

def main():
    """Main function."""
    print("🚀 Environment Variable Fix Script")
    print("=" * 50)
    
    add_missing_keys()
    
    print("\n🎉 Environment variable fix completed!")

if __name__ == "__main__":
    main() 