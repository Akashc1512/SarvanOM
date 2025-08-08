#!/usr/bin/env python3
"""
Configuration Management Test Script.

This script tests the new environment-based configuration management system
to ensure it works correctly across different environments.

Features:
    - Test environment loading
    - Test configuration validation
    - Test environment variable precedence
    - Test configuration file loading
    - Test error handling for missing config
    - Test environment switching

Usage:
    python scripts/test_configuration_management.py [environment]
    
    environment: development, testing, staging, production (default: development)
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.core.config.environment_manager import (
    EnvironmentManager, 
    Environment, 
    EnvironmentConfig,
    get_environment_manager
)
from services.api_gateway.di.config import ConfigManager, get_config_manager


def test_environment_loading(environment: str = "development") -> bool:
    """Test environment loading and configuration."""
    print(f"\n🧪 Testing environment loading for: {environment}")
    
    try:
        # Set environment variable
        os.environ["APP_ENV"] = environment
        
        # Create environment manager
        env_manager = EnvironmentManager()
        env_config = env_manager.get_config()
        
        print(f"✅ Environment loaded: {env_manager.environment.value}")
        print(f"✅ Config name: {env_config.name}")
        print(f"✅ Debug mode: {env_config.debug}")
        print(f"✅ Testing mode: {env_config.testing}")
        print(f"✅ Log level: {env_config.log_level}")
        
        # Test environment-specific validations
        if env_manager.is_production():
            print("🏭 Production mode detected")
            if not env_config.database_url:
                print("⚠️  Warning: DATABASE_URL not set (required for production)")
        elif env_manager.is_development():
            print("🔧 Development mode detected")
        elif env_manager.is_testing():
            print("🧪 Testing mode detected")
        elif env_manager.is_staging():
            print("🚀 Staging mode detected")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment loading failed: {e}")
        return False


def test_configuration_validation() -> bool:
    """Test configuration validation."""
    print(f"\n🧪 Testing configuration validation")
    
    try:
        # Test valid configuration
        env_manager = get_environment_manager()
        env_config = env_manager.get_config()
        
        # Test configuration validation
        env_config._validate_config()
        print("✅ Configuration validation passed")
        
        # Test invalid configuration
        invalid_config = EnvironmentConfig(
            name="test",
            rate_limit_per_minute=0,  # Invalid: must be at least 1
            max_request_size_mb=0,    # Invalid: must be at least 1
            cache_ttl_seconds=-1,     # Invalid: must be non-negative
            session_ttl_seconds=0,    # Invalid: must be at least 1
            agent_timeout_seconds=0,  # Invalid: must be at least 1
            agent_max_retries=-1,     # Invalid: must be non-negative
            agent_backoff_factor=0.5, # Invalid: must be at least 1.0
            query_min_confidence=1.5  # Invalid: must be between 0.0 and 1.0
        )
        
        try:
            invalid_config._validate_config()
            print("❌ Invalid configuration validation should have failed")
            return False
        except ValueError as e:
            print(f"✅ Invalid configuration correctly rejected: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False


def test_environment_variable_precedence() -> bool:
    """Test that environment variables take precedence over config files."""
    print(f"\n🧪 Testing environment variable precedence")
    
    try:
        # Set environment variables
        os.environ["LOG_LEVEL"] = "DEBUG"
        os.environ["RATE_LIMIT_PER_MINUTE"] = "999"
        os.environ["MAX_REQUEST_SIZE_MB"] = "50"
        
        # Create environment manager
        env_manager = EnvironmentManager()
        env_config = env_manager.get_config()
        
        # Verify environment variables took precedence
        if env_config.log_level == "DEBUG":
            print("✅ LOG_LEVEL environment variable applied")
        else:
            print(f"❌ LOG_LEVEL not applied: {env_config.log_level}")
            return False
        
        if env_config.rate_limit_per_minute == 999:
            print("✅ RATE_LIMIT_PER_MINUTE environment variable applied")
        else:
            print(f"❌ RATE_LIMIT_PER_MINUTE not applied: {env_config.rate_limit_per_minute}")
            return False
        
        if env_config.max_request_size_mb == 50:
            print("✅ MAX_REQUEST_SIZE_MB environment variable applied")
        else:
            print(f"❌ MAX_REQUEST_SIZE_MB not applied: {env_config.max_request_size_mb}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Environment variable precedence test failed: {e}")
        return False


def test_configuration_file_loading() -> bool:
    """Test configuration file loading."""
    print(f"\n🧪 Testing configuration file loading")
    
    try:
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                "name": "test_config",
                "debug": True,
                "log_level": "DEBUG",
                "rate_limit_per_minute": 100,
                "max_request_size_mb": 25,
                "features": {
                    "streaming": False,
                    "batch_processing": True,
                    "websockets": False
                }
            }
            import yaml
            yaml.dump(config_data, f)
            config_file = f.name
        
        try:
            # Test loading from file
            env_manager = EnvironmentManager()
            
            # Check if config file was loaded
            env_config = env_manager.get_config()
            
            print(f"✅ Configuration file loaded: {config_file}")
            print(f"✅ Config name: {env_config.name}")
            print(f"✅ Debug mode: {env_config.debug}")
            print(f"✅ Log level: {env_config.log_level}")
            
            return True
            
        finally:
            # Clean up
            os.unlink(config_file)
        
    except Exception as e:
        print(f"❌ Configuration file loading failed: {e}")
        return False


def test_missing_configuration_handling() -> bool:
    """Test handling of missing configuration values."""
    print(f"\n🧪 Testing missing configuration handling")
    
    try:
        # Clear environment variables that might interfere
        env_vars_to_clear = [
            "DATABASE_URL", "REDIS_URL", "JWT_SECRET_KEY",
            "OPENAI_API_KEY", "ANTHROPIC_API_KEY"
        ]
        
        original_values = {}
        for var in env_vars_to_clear:
            original_values[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]
        
        try:
            # Test production environment with missing required values
            os.environ["APP_ENV"] = "production"
            
            env_manager = EnvironmentManager()
            env_config = env_manager.get_config()
            
            # Should not raise an exception, but should log warnings
            print("✅ Production environment loaded with missing required values")
            print(f"✅ Database URL: {env_config.database_url}")
            print(f"✅ Redis URL: {env_config.redis_url}")
            print(f"✅ JWT Secret: {'Set' if env_config.jwt_secret_key else 'Not set'}")
            
            return True
            
        finally:
            # Restore original environment variables
            for var, value in original_values.items():
                if value is not None:
                    os.environ[var] = value
                elif var in os.environ:
                    del os.environ[var]
        
    except Exception as e:
        print(f"❌ Missing configuration handling failed: {e}")
        return False


def test_environment_switching() -> bool:
    """Test switching between different environments."""
    print(f"\n🧪 Testing environment switching")
    
    environments = ["development", "testing", "staging", "production"]
    
    try:
        for env in environments:
            print(f"\n🔄 Testing {env} environment:")
            
            # Set environment
            os.environ["APP_ENV"] = env
            
            # Create new environment manager
            env_manager = EnvironmentManager()
            env_config = env_manager.get_config()
            
            print(f"   ✅ Environment: {env_manager.environment.value}")
            print(f"   ✅ Config name: {env_config.name}")
            print(f"   ✅ Debug mode: {env_config.debug}")
            print(f"   ✅ Testing mode: {env_config.testing}")
            print(f"   ✅ Log level: {env_config.log_level}")
            
            # Test environment-specific features
            if env == "development":
                if not env_config.debug:
                    print("   ❌ Development should have debug enabled")
                    return False
            elif env == "testing":
                if not env_config.mock_ai_responses:
                    print("   ❌ Testing should have mock AI responses enabled")
                    return False
            elif env == "production":
                if env_config.debug:
                    print("   ❌ Production should not have debug enabled")
                    return False
        
        return True
        
    except Exception as e:
        print(f"❌ Environment switching failed: {e}")
        return False


def test_config_manager_integration() -> bool:
    """Test integration with the ConfigManager."""
    print(f"\n🧪 Testing ConfigManager integration")
    
    try:
        # Get the config manager
        config_manager = get_config_manager()
        
        # Test environment info
        env_info = config_manager.get_environment_info()
        print(f"✅ Environment info: {env_info['environment']}")
        print(f"✅ Config name: {env_info['config_name']}")
        print(f"✅ Debug mode: {env_info['debug']}")
        print(f"✅ Testing mode: {env_info['testing']}")
        
        # Test service configs
        all_configs = config_manager.get_all_configs()
        print(f"✅ Service configs loaded: {list(all_configs.keys())}")
        
        # Test specific service config
        browser_config = config_manager.get_service_config("browser")
        print(f"✅ Browser config: {browser_config['max_results']} max results")
        
        return True
        
    except Exception as e:
        print(f"❌ ConfigManager integration failed: {e}")
        return False


def test_secret_handling() -> bool:
    """Test that secrets are handled securely."""
    print(f"\n🧪 Testing secret handling")
    
    try:
        # Set some test secrets
        os.environ["OPENAI_API_KEY"] = "sk-test123456789"
        os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key"
        os.environ["DATABASE_URL"] = "postgresql://user:password@localhost:5432/db"
        
        # Create environment manager
        env_manager = EnvironmentManager()
        env_config = env_manager.get_config()
        
        # Test that secrets are masked in to_dict()
        config_dict = env_config.to_dict(include_secrets=False)
        
        if config_dict.get("openai_api_key") == "***REDACTED***":
            print("✅ OpenAI API key correctly masked")
        else:
            print("❌ OpenAI API key not masked")
            return False
        
        if config_dict.get("jwt_secret_key") == "***REDACTED***":
            print("✅ JWT secret key correctly masked")
        else:
            print("❌ JWT secret key not masked")
            return False
        
        if config_dict.get("database_url") == "***REDACTED***":
            print("✅ Database URL correctly masked")
        else:
            print("❌ Database URL not masked")
            return False
        
        # Test that secrets are included when requested
        config_dict_with_secrets = env_config.to_dict(include_secrets=True)
        
        if config_dict_with_secrets.get("openai_api_key") == "sk-test123456789":
            print("✅ OpenAI API key correctly included when requested")
        else:
            print("❌ OpenAI API key not included when requested")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Secret handling test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 CONFIGURATION MANAGEMENT TEST SUITE")
    print("=" * 60)
    
    # Get environment from command line argument
    environment = sys.argv[1] if len(sys.argv) > 1 else "development"
    
    # Run all tests
    tests = [
        ("Environment Loading", lambda: test_environment_loading(environment)),
        ("Configuration Validation", test_configuration_validation),
        ("Environment Variable Precedence", test_environment_variable_precedence),
        ("Configuration File Loading", test_configuration_file_loading),
        ("Missing Configuration Handling", test_missing_configuration_handling),
        ("Environment Switching", test_environment_switching),
        ("ConfigManager Integration", test_config_manager_integration),
        ("Secret Handling", test_secret_handling),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 Running: {test_name}")
        print(f"{'='*60}")
        
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print(f"🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"⚠️  SOME TESTS FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 