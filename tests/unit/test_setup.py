#!/usr/bin/env python3
"""
Test Setup Script for Universal Knowledge Hub
This script tests each component step by step to identify issues.
"""

import sys
import os
import asyncio
import requests
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        import pydantic
        print("✅ Pydantic imported")
    except ImportError as e:
        print(f"❌ Pydantic import failed: {e}")
        return False
    
    try:
    from shared.core.database import get_database_service
    print("✅ Database service imported")
except ImportError as e:
    print(f"❌ Database service import failed: {e}")
        return False
    
    try:
        import aiocache
        print("✅ Aiocache imported")
    except ImportError as e:
        print(f"❌ Aiocache import failed: {e}")
        return False
    
    try:
        import openai
        print("✅ OpenAI imported")
    except ImportError as e:
        print(f"❌ OpenAI import failed: {e}")
        return False
    
    try:
        import anthropic
        print("✅ Anthropic imported")
    except ImportError as e:
        print(f"❌ Anthropic import failed: {e}")
        return False
    
    try:
        from shared.core.llm_client_v3 import EnhancedLLMClientV3
        print("✅ LLM Client v3 imported")
    except ImportError as e:
        print(f"❌ LLM Client v3 import failed: {e}")
        return False
    
    return True

def test_api_imports():
    """Test if API modules can be imported."""
    print("\n🔍 Testing API imports...")
    
    # Add current directory to Python path
    sys.path.insert(0, str(Path.cwd()))
    
    try:
        import api.config
        print("✅ api.config imported")
    except ImportError as e:
        print(f"❌ api.config import failed: {e}")
        return False
    
    try:
        import api.cache
        print("✅ api.cache imported")
    except ImportError as e:
        print(f"❌ api.cache import failed: {e}")
        return False
    
    try:
        import agents.base_agent
        print("✅ agents.base_agent imported")
    except ImportError as e:
        print(f"❌ agents.base_agent import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment variables."""
    print("\n🔍 Testing environment variables...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file exists")
    else:
        print("⚠️  .env file not found - please create it")
        return False
    
    # Check required environment variables
    required_vars = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "SECRET_KEY",
        "API_KEY_SECRET"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    else:
        print("✅ All required environment variables are set")
    
    return True

def test_backend_startup():
    """Test if the backend can start."""
    print("\n🔍 Testing backend startup...")
    
    try:
        # Import the main module
        import api.main
        print("✅ Backend modules imported successfully")
        
        # Check if the app is defined
        if hasattr(api.main, 'app'):
            print("✅ FastAPI app is defined")
        else:
            print("❌ FastAPI app not found")
            return False
            
    except Exception as e:
        print(f"❌ Backend startup failed: {e}")
        return False
    
    return True

def test_frontend():
    """Test frontend setup."""
    print("\n🔍 Testing frontend setup...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        print("❌ package.json not found")
        return False
    
    print("✅ Frontend directory structure is correct")
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        print("✅ Node modules are installed")
    else:
        print("⚠️  Node modules not found - run 'npm install' in frontend directory")
        return False
    
    return True

def test_network():
    """Test network connectivity."""
    print("\n🔍 Testing network connectivity...")
    
    try:
        response = requests.get("https://api.openai.com/v1/models", timeout=5)
        print("✅ OpenAI API connectivity")
    except Exception as e:
        print(f"⚠️  OpenAI API connectivity issue: {e}")
    
    try:
        response = requests.get("https://api.anthropic.com/v1/messages", timeout=5)
        print("✅ Anthropic API connectivity")
    except Exception as e:
        print(f"⚠️  Anthropic API connectivity issue: {e}")
    
    # Test LLM Client v3
    try:
        from shared.core.llm_client_v3 import get_llm_client_v3
        client = get_llm_client_v3()
        if client.providers:
            print("✅ LLM Client v3 configured")
        else:
            print("⚠️  LLM Client v3 has no providers configured")
    except Exception as e:
        print(f"❌ LLM Client v3 configuration failed: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 Universal Knowledge Hub - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("API Import Tests", test_api_imports),
        ("Environment Tests", test_environment),
        ("Backend Startup Tests", test_backend_startup),
        ("Frontend Tests", test_frontend),
        ("Network Tests", test_network),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The setup is complete.")
        print("\nNext steps:")
        print("1. Start the backend: python api/main.py")
        print("2. Start the frontend: cd frontend && npm run dev")
        print("3. Test the application: python test_ai_improvements.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 