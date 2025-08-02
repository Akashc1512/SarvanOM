#!/usr/bin/env python3
"""
SarvanOM Setup Test Script

This script performs basic validation of the SarvanOM platform setup.
"""

import os
import sys
from pathlib import Path

def test_environment_setup():
    """Test environment configuration."""
    print("🔍 Testing environment setup...")
    
    # Check if .env template exists
    env_template = Path("env.template")
    if not env_template.exists():
        print("❌ env.template not found")
        return False
    
    # Check if .env exists (optional for testing)
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found (create from env.template)")
    else:
        print("✅ .env file exists")
    
    # Check critical environment variables
    critical_vars = ["ENVIRONMENT", "SERVICE_NAME", "LOG_LEVEL"]
    missing_vars = []
    
    for var in critical_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
    else:
        print("✅ Environment variables configured")
    
    return True

def test_imports():
    """Test that all required modules can be imported."""
    print("\n🔍 Testing imports...")
    
    try:
        # Test core imports
        from shared.core.logging_config import get_logger
        print("✅ Logging configuration imported")
        
        from shared.core.api.config import get_settings
        print("✅ Configuration management imported")
        
        from shared.core.agent_pattern import AgentFactory
        print("✅ Agent patterns imported")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_file_structure():
    """Test that required files and directories exist."""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        "README.md",
        "env.template",
        "shared/core/logging_config.py",
        "shared/core/api/config.py",
        "shared/core/agent_pattern.py",
        "services/api_gateway/main.py",
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_logging():
    """Test logging configuration."""
    print("\n🔍 Testing logging configuration...")
    
    try:
        from shared.core.logging_config import get_logger
        
        logger = get_logger("test")
        logger.info("Test log message", extra={"test": True})
        print("✅ Logging configuration working")
        return True
    except Exception as e:
        print(f"❌ Logging test failed: {e}")
        return False

def test_configuration():
    """Test configuration management."""
    print("\n🔍 Testing configuration management...")
    
    try:
        from shared.core.api.config import get_settings
        
        settings = get_settings()
        print(f"✅ Configuration loaded: {settings.environment}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 SarvanOM Setup Test")
    print("=" * 50)
    
    tests = [
        test_environment_setup,
        test_imports,
        test_file_structure,
        test_logging,
        test_configuration,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! SarvanOM setup is ready.")
        print("\n📋 Next steps:")
        print("1. Configure your .env file with actual credentials")
        print("2. Start the development server: python run_server.py")
        print("3. Access the platform at http://localhost:8000")
    else:
        print("⚠️  Some tests failed. Please address the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 