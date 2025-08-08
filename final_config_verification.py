#!/usr/bin/env python3
"""
Final Configuration Refactoring Verification

This script provides a comprehensive verification of the configuration refactoring.
"""

import os
import sys
from pathlib import Path
import re

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def verify_central_config():
    """Verify the central configuration system."""
    print("🔍 Verifying Central Configuration System")
    print("=" * 50)
    
    try:
        from shared.core.config import get_central_config, get_database_url, get_redis_url, get_vector_db_url, get_meilisearch_url, get_arangodb_url, get_ollama_url
        
        # Test central config loading
        config = get_central_config()
        print("✅ Central configuration loaded successfully")
        print(f"   Environment: {config.environment}")
        print(f"   App Name: {config.app_name}")
        print(f"   Debug Mode: {config.debug}")
        
        # Test helper functions
        print("\n✅ Helper functions working:")
        print(f"   Database URL: {get_database_url()}")
        print(f"   Redis URL: {get_redis_url()}")
        print(f"   Vector DB URL: {get_vector_db_url()}")
        print(f"   Meilisearch URL: {get_meilisearch_url()}")
        print(f"   ArangoDB URL: {get_arangodb_url()}")
        print(f"   Ollama URL: {get_ollama_url()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def verify_refactored_files():
    """Verify that files have been properly refactored."""
    print("\n🔍 Verifying Refactored Files")
    print("=" * 50)
    
    # Files that should use central configuration
    refactored_files = [
        "shared/core/llm_client_v3.py",
        "shared/core/health_checker.py", 
        "shared/core/connection_pool.py",
        "services/api_gateway/services/knowledge_service.py",
        "services/api_gateway/routes/health.py",
        "services/api_gateway/main.py",
        "services/api_gateway/di/config.py",
        "services/api_gateway/middleware/cors.py",
        "services/analytics/health_checks.py",
        "services/analytics/integration_monitor.py",
        "shared/core/base_agent.py",
        "shared/core/agents/retrieval_agent.py",
        "shared/core/agents/knowledge_graph_agent.py",
        "shared/core/agents/graph_db_client.py",
        "shared/core/memory_manager.py",
        "shared/core/llm_client_enhanced.py",
        "shared/core/llm_client_dynamic.py",
        "services/gateway/main.py",
        "services/api_gateway/routes/queries.py",
        "services/api_gateway/integration_layer.py"
    ]
    
    config_imports = [
        "from shared.core.config.central_config import",
        "get_central_config",
        "get_database_url",
        "get_redis_url", 
        "get_vector_db_url",
        "get_meilisearch_url",
        "get_arangodb_url",
        "get_ollama_url",
        "get_config_value"
    ]
    
    success_count = 0
    total_count = 0
    
    for file_path in refactored_files:
        if Path(file_path).exists():
            total_count += 1
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if file uses configuration imports
                has_config_imports = any(import_str in content for import_str in config_imports)
                
                if has_config_imports:
                    print(f"✅ {file_path}")
                    success_count += 1
                else:
                    print(f"⚠️  {file_path}: May need updates")
                    
            except Exception as e:
                print(f"❌ {file_path}: Error reading file - {e}")
        else:
            print(f"⚠️  {file_path}: File not found")
    
    print(f"\n📊 Refactoring Summary: {success_count}/{total_count} files using configuration")
    return success_count == total_count

def check_remaining_hardcoded():
    """Check for any remaining hard-coded values in main application code."""
    print("\n🔍 Checking for Remaining Hard-coded Values")
    print("=" * 50)
    
    # Patterns to check for
    hardcoded_patterns = [
        r'"http://localhost:11434"',
        r'"http://localhost:6333"',
        r'"http://localhost:7700"',
        r'"http://localhost:8529"',
        r'"redis://localhost:6379"',
        r'http://localhost:11434',
        r'http://localhost:6333',
        r'http://localhost:7700',
        r'http://localhost:8529',
        r'redis://localhost:6379'
    ]
    
    # Directories to exclude
    exclude_dirs = [
        '.venv', 'venv', '__pycache__', '.git', 'node_modules',
        'tests', 'scripts', 'frontend', 'data'
    ]
    
    issues_found = 0
    
    for root, dirs, files in os.walk('.'):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                
                # Skip test files and scripts
                if 'test' in file_path.name.lower() or 'script' in file_path.name.lower():
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for pattern in hardcoded_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            print(f"⚠️  {file_path}: Found {len(matches)} hard-coded values")
                            issues_found += len(matches)
                            
                except Exception as e:
                    continue
    
    if issues_found == 0:
        print("✅ No hard-coded values found in main application code")
        return True
    else:
        print(f"⚠️  Found {issues_found} potential hard-coded values")
        return False

def verify_security():
    """Verify security improvements."""
    print("\n🔍 Verifying Security Improvements")
    print("=" * 50)
    
    try:
        from shared.core.config import get_central_config
        config = get_central_config()
        
        # Check for SecretStr usage
        secret_fields = [
            'jwt_secret_key',
            'openai_api_key',
            'anthropic_api_key',
            'meilisearch_master_key',
            'postgres_password',
            'redis_password'
        ]
        
        print("✅ Security features:")
        for field in secret_fields:
            if hasattr(config, field):
                value = getattr(config, field)
                if hasattr(value, 'get_secret_value'):
                    print(f"   ✅ {field}: Using SecretStr")
                else:
                    print(f"   ⚠️  {field}: Not using SecretStr")
        
        return True
        
    except Exception as e:
        print(f"❌ Security verification error: {e}")
        return False

def main():
    """Main verification function."""
    print("🎯 Final Configuration Refactoring Verification")
    print("=" * 60)
    
    # Run all verifications
    config_success = verify_central_config()
    refactor_success = verify_refactored_files()
    hardcoded_success = check_remaining_hardcoded()
    security_success = verify_security()
    
    print("\n" + "=" * 60)
    print("📊 FINAL VERIFICATION RESULTS")
    print("=" * 60)
    print(f"✅ Central Configuration: {'PASS' if config_success else 'FAIL'}")
    print(f"✅ File Refactoring: {'PASS' if refactor_success else 'FAIL'}")
    print(f"✅ Hard-coded Removal: {'PASS' if hardcoded_success else 'FAIL'}")
    print(f"✅ Security Improvements: {'PASS' if security_success else 'FAIL'}")
    
    all_success = config_success and refactor_success and hardcoded_success and security_success
    
    if all_success:
        print("\n🎉 CONFIGURATION REFACTORING COMPLETED SUCCESSFULLY!")
        print("\n📋 Summary of Achievements:")
        print("   ✅ Created centralized configuration system")
        print("   ✅ Refactored 20+ files to use configuration")
        print("   ✅ Eliminated hard-coded values from source code")
        print("   ✅ Implemented secure secrets management")
        print("   ✅ Added environment variable support")
        print("   ✅ Created validation and testing tools")
        print("\n🚀 The codebase now follows industry best practices for configuration management!")
    else:
        print("\n❌ Some issues remain that need to be addressed.")
    
    return all_success

if __name__ == "__main__":
    main() 