#!/usr/bin/env python3
"""
Simple Configuration Test Script

This script tests the basic configuration management functionality
without complex dependencies.
"""

import os
import sys
from pathlib import Path

def test_environment_variables():
    """Test environment variable loading."""
    print("\n🌍 Testing Environment Variables...")
    
    # Test APP_ENV
    app_env = os.getenv("APP_ENV", "development")
    print(f"✅ APP_ENV: {app_env}")
    
    # Test database configuration
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        print(f"✅ DATABASE_URL: {database_url[:30]}...")
    else:
        print("⚠️  DATABASE_URL not set")
    
    # Test Redis configuration
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        print(f"✅ REDIS_URL: {redis_url[:30]}...")
    else:
        print("⚠️  REDIS_URL not set")
    
    # Test AI provider configuration
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if openai_key or anthropic_key:
        print("✅ AI provider API key is set")
    else:
        print("⚠️  No AI provider API keys set")
    
    return True

def test_configuration_files():
    """Test configuration file existence."""
    print("\n📁 Testing Configuration Files...")
    
    config_dir = Path("config")
    if not config_dir.exists():
        print("❌ Configuration directory not found")
        return False
    
    # Check for environment-specific config files
    environments = ["development", "testing", "staging", "production"]
    app_env = os.getenv("APP_ENV", "development")
    
    config_files = []
    for env in environments:
        for ext in [".yaml", ".yml", ".json"]:
            config_file = config_dir / f"{env}{ext}"
            if config_file.exists():
                config_files.append(config_file)
                print(f"✅ Found config file: {config_file.name}")
    
    if not config_files:
        print("⚠️  No configuration files found")
    else:
        print(f"✅ Found {len(config_files)} configuration files")
    
    return True

def test_environment_template():
    """Test environment template file."""
    print("\n📋 Testing Environment Template...")
    
    template_files = ["env.example", ".env.example"]
    found_template = False
    
    for template_file in template_files:
        if Path(template_file).exists():
            print(f"✅ Environment template found: {template_file}")
            found_template = True
            break
    
    if not found_template:
        print("❌ No environment template file found")
        return False
    
    return True

def test_environment_validation():
    """Test environment-specific validation."""
    print("\n✅ Testing Environment Validation...")
    
    app_env = os.getenv("APP_ENV", "development")
    print(f"📋 Current environment: {app_env}")
    
    # Environment-specific checks
    if app_env in ["production", "staging"]:
        print("🔒 Production/Staging environment detected")
        
        # Check for required variables
        required_vars = ["DATABASE_URL", "REDIS_URL", "JWT_SECRET_KEY"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing required variables for {app_env}: {', '.join(missing_vars)}")
            return False
        else:
            print("✅ All required variables are set")
    
    elif app_env == "testing":
        print("🧪 Testing environment detected")
        # Testing environment has minimal requirements
        print("✅ Testing environment validation passed")
    
    else:  # development
        print("🔧 Development environment detected")
        # Development environment has no strict requirements
        print("✅ Development environment validation passed")
    
    return True

def main():
    """Main function to run configuration tests."""
    print("=" * 60)
    print("🔍 SIMPLE CONFIGURATION VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Configuration Files", test_configuration_files),
        ("Environment Template", test_environment_template),
        ("Environment Validation", test_environment_validation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("Configuration management system is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed.")
        print("Please review the configuration setup.")
    
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 