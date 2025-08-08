#!/usr/bin/env python3
"""
Simple Configuration Test

Tests basic configuration loading and environment switching without
heavy dependencies.
"""

import os
import sys
from pathlib import Path

def test_config_files():
    """Test that configuration files exist."""
    print("🔍 Testing Configuration Files")
    print("-" * 40)
    
    required_files = [
        "config/development.yaml",
        "config/testing.yaml", 
        "config/staging.yaml",
        "config/production.yaml",
        "env.example"
    ]
    
    all_found = True
    for config_file in required_files:
        if Path(config_file).exists():
            print(f"✅ {config_file}")
        else:
            print(f"❌ {config_file}")
            all_found = False
    
    return all_found

def test_environment_variables():
    """Test environment variable handling."""
    print("\n🌍 Testing Environment Variables")
    print("-" * 40)
    
    # Test APP_ENV
    app_env = os.getenv("APP_ENV", "development")
    print(f"📋 APP_ENV: {app_env}")
    
    # Test some common variables
    test_vars = [
        "LOG_LEVEL",
        "DEBUG", 
        "SERVICE_NAME",
        "JWT_SECRET_KEY",
        "DATABASE_URL"
    ]
    
    set_vars = []
    unset_vars = []
    
    for var in test_vars:
        value = os.getenv(var)
        if value:
            set_vars.append(var)
            print(f"✅ {var}: {'***' if 'secret' in var.lower() or 'key' in var.lower() else value}")
        else:
            unset_vars.append(var)
            print(f"⚪ {var}: not set")
    
    print(f"\n📊 Summary: {len(set_vars)} set, {len(unset_vars)} unset")
    return True

def test_environment_switching():
    """Test switching between environments."""
    print("\n🔄 Testing Environment Switching")
    print("-" * 40)
    
    original_env = os.getenv("APP_ENV")
    environments = ["development", "testing", "staging", "production"]
    
    results = {}
    
    for env in environments:
        print(f"\n🧪 Testing {env} environment...")
        os.environ["APP_ENV"] = env
        
        # Test that we can read the environment
        current_env = os.getenv("APP_ENV")
        if current_env == env:
            print(f"   ✅ Environment variable set correctly")
            results[env] = True
        else:
            print(f"   ❌ Environment variable not set correctly")
            results[env] = False
        
        # Check if config file exists
        config_file = f"config/{env}.yaml"
        if Path(config_file).exists():
            print(f"   ✅ Configuration file exists")
        else:
            print(f"   ❌ Configuration file missing")
            results[env] = False
    
    # Restore original environment
    if original_env:
        os.environ["APP_ENV"] = original_env
    
    return all(results.values())

def test_security_checks():
    """Test security-related configuration."""
    print("\n🔒 Testing Security Configuration")
    print("-" * 40)
    
    # Check for common security mistakes
    issues = []
    
    # Check if secrets are in environment (without printing them)
    if os.getenv("JWT_SECRET_KEY") == "your_jwt_secret_key_here":
        issues.append("JWT_SECRET_KEY still has placeholder value")
    
    if os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
        issues.append("OPENAI_API_KEY still has placeholder value")
    
    # Check environment-specific settings
    app_env = os.getenv("APP_ENV", "development")
    
    if app_env == "production":
        if os.getenv("DEBUG", "false").lower() == "true":
            issues.append("DEBUG should be false in production")
        
        if os.getenv("MOCK_AI_RESPONSES", "false").lower() == "true":
            issues.append("MOCK_AI_RESPONSES should be false in production")
    
    if issues:
        print("⚠️  Security issues found:")
        for issue in issues:
            print(f"   ❌ {issue}")
        return False
    else:
        print("✅ No obvious security issues detected")
        return True

def main():
    """Run all configuration tests."""
    print("🔧 Simple Configuration Test")
    print("=" * 60)
    
    print(f"📍 Working directory: {os.getcwd()}")
    print(f"🐍 Python version: {sys.version}")
    print(f"🌍 Current APP_ENV: {os.getenv('APP_ENV', 'not set')}")
    
    all_passed = True
    
    # Run tests
    tests = [
        ("Configuration Files", test_config_files),
        ("Environment Variables", test_environment_variables),
        ("Environment Switching", test_environment_switching),
        ("Security Configuration", test_security_checks)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All configuration tests passed!")
        print("✅ Your configuration setup looks good")
    else:
        print("⚠️  Some configuration tests failed")
        print("📋 Please review the issues above")
    
    print("\n💡 Next steps:")
    print("1. Copy env.example to .env")
    print("2. Fill in your actual secrets")
    print("3. Test with: python scripts/verify_env_config.py")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())