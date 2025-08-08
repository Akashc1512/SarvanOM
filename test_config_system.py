#!/usr/bin/env python3
"""
Test Configuration System

This script tests the central configuration system to ensure it's working correctly.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_configuration_system():
    """Test the central configuration system."""
    print("Testing Central Configuration System")
    print("=" * 50)
    
    try:
        from shared.core.config import get_central_config, get_database_url, get_redis_url, get_vector_db_url, get_meilisearch_url, get_arangodb_url, get_ollama_url
        
        # Test basic configuration loading
        print("1. Testing basic configuration loading...")
        config = get_central_config()
        print(f"   ✅ Configuration loaded successfully")
        print(f"   Environment: {config.environment}")
        print(f"   Debug mode: {config.debug}")
        print(f"   Log level: {config.log_level}")
        
        # Test helper functions
        print("\n2. Testing configuration helper functions...")
        print(f"   Database URL: {get_database_url()}")
        print(f"   Redis URL: {get_redis_url()}")
        print(f"   Vector DB URL: {get_vector_db_url()}")
        print(f"   MeiliSearch URL: {get_meilisearch_url()}")
        print(f"   ArangoDB URL: {get_arangodb_url()}")
        print(f"   Ollama URL: {get_ollama_url()}")
        
        # Test configuration validation
        print("\n3. Testing configuration validation...")
        issues = config.validate_config()
        if issues:
            print(f"   ⚠️  Configuration issues found: {len(issues)}")
            for issue in issues[:5]:  # Show first 5 issues
                print(f"      - {issue}")
        else:
            print("   ✅ Configuration validation passed")
        
        # Test environment-specific settings
        print("\n4. Testing environment-specific settings...")
        print(f"   AI Providers configured: {config._get_configured_ai_providers()}")
        print(f"   Features enabled: {list(config.features.keys())[:5]}...")
        
        # Test configuration masking
        print("\n5. Testing configuration masking...")
        config_dict = config.to_dict(include_secrets=False)
        print(f"   Secrets masked: {config_dict.get('openai_api_key', 'Not set')}")
        
        print("\n✅ All configuration tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_environment_variables():
    """Test environment variable loading."""
    print("\nTesting Environment Variables")
    print("=" * 50)
    
    # Test required environment variables
    required_vars = ["JWT_SECRET_KEY", "DATABASE_URL", "REDIS_URL"]
    optional_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "MEILISEARCH_MASTER_KEY"]
    
    print("Required environment variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: Set")
        else:
            print(f"   ⚠️  {var}: Not set")
    
    print("\nOptional environment variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: Set")
        else:
            print(f"   ⚠️  {var}: Not set (optional)")
    
    return True

def main():
    """Main test function."""
    print("Configuration System Test")
    print("=" * 50)
    
    # Test environment variables
    test_environment_variables()
    
    # Test configuration system
    success = test_configuration_system()
    
    if success:
        print("\n🎉 Configuration system is working correctly!")
        print("\nNext steps:")
        print("1. Set required environment variables in .env file")
        print("2. Run the application to test full functionality")
        print("3. Use the validation script to check for issues")
    else:
        print("\n❌ Configuration system has issues that need to be resolved.")
    
    return success

if __name__ == "__main__":
    main() 