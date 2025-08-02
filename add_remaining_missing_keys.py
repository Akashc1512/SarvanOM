#!/usr/bin/env python3
"""
Script to add the remaining missing critical environment variables to .env file.
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

def get_remaining_missing_keys() -> Dict[str, str]:
    """Get the remaining missing critical keys."""
    return {
        # Graph Update Configuration - Critical for multi-source retrieval
        "GRAPH_UPDATE_ENABLED": "true",
        "GRAPH_AUTO_EXTRACT_ENTITIES": "true",
        "GRAPH_CONFIDENCE_THRESHOLD": "0.7",
        "GRAPH_MAX_ENTITIES_PER_DOC": "10",
        "GRAPH_RELATIONSHIP_TYPES": "is_related_to,is_part_of,is_similar_to,enables,requires",
        
        # ArangoDB Configuration - Critical for graph search
        "ARANGO_DATABASE": "knowledge_graph",
        "ARANGO_HOST": "localhost",
        "ARANGO_PORT": "8529",
        "ARANGO_USERNAME": "root",
        "ARANGO_PASSWORD": "your_arangodb_password_here",
        
        # Meilisearch Configuration - Critical for keyword search
        "MEILISEARCH_API_KEY": "your_meilisearch_api_key_here",
        "MEILISEARCH_INDEX": "knowledge_base",
        "MEILISEARCH_MASTER_KEY": "your_meilisearch_master_key_here",
        
        # Vector Database Configuration - Critical for vector search
        "VECTOR_DB_URL": "http://localhost:6333",
        "QDRANT_HOST": "localhost",
        "QDRANT_PASSWORD": "your_qdrant_password_here",
        "QDRANT_USERNAME": "your_qdrant_username_here",
        
        # Database Configuration - Critical for data persistence
        "DATABASE_ENCRYPTION_KEY": "your_encryption_key_here",
        "DATABASE_NAME": "knowledge_base",
        "DB_HOST": "localhost",
        "DB_NAME": "universal_knowledge",
        "DB_PASSWORD": "your_db_password_here",
        "DB_PORT": "5432",
        "DB_USER": "your_db_user_here",
        
        # External Services - Important for web search
        "GOOGLE_API_KEY": "your_google_api_key_here",
        "SERP_API_KEY": "your_serp_api_key_here",
        
        # System Configuration - Important for functionality
        "REDIS_ENABLED": "true",
        "ENABLE_SECURITY_ENDPOINT": "false",
        "ANONYMIZE_QUERIES": "false",
        "DATA_RETENTION_DAYS": "365",
        
        # Azure OpenAI (Optional - for fallback)
        "AZURE_OPENAI_API_KEY": "your_azure_openai_api_key_here",
        
        # Elasticsearch (Legacy - can be removed since we use Meilisearch)
        "ELASTICSEARCH_HOST": "localhost",
        "ELASTICSEARCH_INDEX": "knowledge_base",
        "ELASTICSEARCH_PASSWORD": "your_elasticsearch_password_here",
        "ELASTICSEARCH_URL": "http://localhost:9200",
        "ELASTICSEARCH_USERNAME": "your_elasticsearch_username_here",
        "ELASTICSEARCH_CLOUD_URL": "your_elasticsearch_cloud_url_here",
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

def add_remaining_missing_keys():
    """Add the remaining missing critical keys to .env file."""
    print("🔧 Adding remaining missing critical environment variables to .env file...")
    
    # Read current .env file
    env_lines = read_env_file()
    existing_keys = get_existing_keys(env_lines)
    
    # Get remaining missing critical keys
    missing_keys = get_remaining_missing_keys()
    
    # Filter out keys that already exist
    keys_to_add = {k: v for k, v in missing_keys.items() if k not in existing_keys}
    
    if not keys_to_add:
        print("✅ No remaining missing critical keys found!")
        return
    
    print(f"📝 Adding {len(keys_to_add)} remaining missing critical keys...")
    
    # Add to existing file
    new_lines = []
    new_lines.extend(env_lines)
    
    # Add missing keys with proper organization
    if keys_to_add:
        new_lines.append("\n# ============================================================================\n")
        new_lines.append("# REMAINING MISSING CRITICAL ENVIRONMENT VARIABLES (AUTO-ADDED)\n")
        new_lines.append("# ============================================================================\n")
        
        # Group keys by priority
        high_priority = {
            "Graph Update Configuration": ["GRAPH_UPDATE_ENABLED", "GRAPH_AUTO_EXTRACT_ENTITIES", "GRAPH_CONFIDENCE_THRESHOLD", "GRAPH_MAX_ENTITIES_PER_DOC", "GRAPH_RELATIONSHIP_TYPES"],
            "ArangoDB Configuration": ["ARANGO_DATABASE", "ARANGO_HOST", "ARANGO_PORT", "ARANGO_USERNAME", "ARANGO_PASSWORD"],
            "Meilisearch Configuration": ["MEILISEARCH_API_KEY", "MEILISEARCH_INDEX", "MEILISEARCH_MASTER_KEY"],
            "Vector Database Configuration": ["VECTOR_DB_URL", "QDRANT_HOST", "QDRANT_PASSWORD", "QDRANT_USERNAME"],
            "Database Configuration": ["DATABASE_ENCRYPTION_KEY", "DATABASE_NAME", "DB_HOST", "DB_NAME", "DB_PASSWORD", "DB_PORT", "DB_USER"],
            "External Services": ["GOOGLE_API_KEY", "SERP_API_KEY"],
            "System Configuration": ["REDIS_ENABLED", "ENABLE_SECURITY_ENDPOINT", "ANONYMIZE_QUERIES", "DATA_RETENTION_DAYS"],
            "Azure OpenAI": ["AZURE_OPENAI_API_KEY"],
            "Elasticsearch (Legacy)": ["ELASTICSEARCH_HOST", "ELASTICSEARCH_INDEX", "ELASTICSEARCH_PASSWORD", "ELASTICSEARCH_URL", "ELASTICSEARCH_USERNAME", "ELASTICSEARCH_CLOUD_URL"]
        }
        
        for category, category_keys in high_priority.items():
            # Filter keys that are actually missing
            missing_category_keys = {k: keys_to_add[k] for k in category_keys if k in keys_to_add}
            
            if missing_category_keys:
                new_lines.append(f"\n# {category}\n")
                for key, value in missing_category_keys.items():
                    new_lines.append(f"{key}={value}\n")
    
    # Write updated .env file
    write_env_file(new_lines)
    
    print(f"✅ Successfully added {len(keys_to_add)} remaining missing critical keys to .env file")
    print("\n📋 Added keys by category:")
    for category, category_keys in high_priority.items():
        missing_category_keys = {k: keys_to_add[k] for k in category_keys if k in keys_to_add}
        if missing_category_keys:
            print(f"   {category}: {len(missing_category_keys)} keys")
    
    print("\n⚠️ Remember to:")
    print("   1. Replace placeholder values with actual credentials")
    print("   2. Test the configuration after updating")
    print("   3. Keep sensitive keys secure")
    print("   4. Consider removing Elasticsearch keys if not using Elasticsearch")

def main():
    """Main function."""
    print("🚀 Remaining Environment Variable Fix Script")
    print("=" * 60)
    
    add_remaining_missing_keys()
    
    print("\n🎉 Remaining environment variable fix completed!")

if __name__ == "__main__":
    main() 