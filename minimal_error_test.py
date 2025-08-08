#!/usr/bin/env python3
"""
Minimal Error Handling Test

This script tests the error handling system with minimal dependencies.
"""

import sys
import os
import asyncio
import time
from typing import Dict, Any, Optional

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_direct_error_handler():
    """Test error handler directly without complex imports."""
    try:
        # Test the error handler file directly
        import importlib.util
        
        # Load the error handler module directly
        spec = importlib.util.spec_from_file_location(
            "error_handler", 
            "shared/core/error_handler.py"
        )
        error_handler = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(error_handler)
        
        print("✅ Error handler module loaded successfully")
        
        # Test basic classes
        from enum import Enum
        
        # Test ErrorSeverity
        severity = error_handler.ErrorSeverity.LOW
        assert severity.value == "low"
        
        # Test ErrorCategory
        category = error_handler.ErrorCategory.API_TIMEOUT
        assert category.value == "api_timeout"
        
        # Test CircuitBreaker
        cb = error_handler.CircuitBreaker(failure_threshold=3, recovery_timeout=5)
        assert cb.state == "CLOSED"
        assert cb.can_execute() == True
        
        print("✅ Basic error handler classes work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Direct error handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handler_file_content():
    """Test that the error handler file exists and has expected content."""
    try:
        error_handler_path = "shared/core/error_handler.py"
        
        if not os.path.exists(error_handler_path):
            print(f"❌ Error handler file not found: {error_handler_path}")
            return False
        
        with open(error_handler_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key classes
        required_classes = [
            "class ErrorSeverity",
            "class ErrorCategory", 
            "class ErrorContext",
            "class ErrorInfo",
            "class ErrorResponse",
            "class CircuitBreaker",
            "class APIErrorHandler",
            "class LLMErrorHandler",
            "class DatabaseErrorHandler",
            "def handle_critical_operation",
            "def safe_api_call",
            "def safe_llm_call",
            "def safe_database_call"
        ]
        
        missing_classes = []
        for class_name in required_classes:
            if class_name not in content:
                missing_classes.append(class_name)
        
        if missing_classes:
            print(f"❌ Missing required classes in error handler: {missing_classes}")
            return False
        
        print("✅ Error handler file contains all required classes")
        return True
        
    except Exception as e:
        print(f"❌ Error handler file content test failed: {e}")
        return False

def test_llm_client_error_handling():
    """Test that LLM client has error handling applied."""
    try:
        llm_client_path = "shared/core/llm_client_v3.py"
        
        if not os.path.exists(llm_client_path):
            print(f"❌ LLM client file not found: {llm_client_path}")
            return False
        
        with open(llm_client_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for error handling decorator
        if "@handle_critical_operation" not in content:
            print("❌ LLM client missing error handling decorator")
            return False
        
        # Check for graceful error handling
        if "return LLMResponse" in content and "fallback" in content:
            print("✅ LLM client has graceful error handling")
        else:
            print("❌ LLM client missing graceful error handling")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ LLM client error handling test failed: {e}")
        return False

def test_api_gateway_error_handling():
    """Test that API gateway has error handling applied."""
    try:
        api_gateway_path = "services/api_gateway/main.py"
        
        if not os.path.exists(api_gateway_path):
            print(f"❌ API gateway file not found: {api_gateway_path}")
            return False
        
        with open(api_gateway_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for fallback data in error responses
        if "fallback_data" in content:
            print("✅ API gateway has fallback error handling")
        else:
            print("❌ API gateway missing fallback error handling")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ API gateway error handling test failed: {e}")
        return False

def main():
    """Run minimal error handling tests."""
    print("🧪 Testing Error Handling System (Minimal)")
    print("=" * 50)
    
    tests = [
        test_error_handler_file_content,
        test_direct_error_handler,
        test_llm_client_error_handling,
        test_api_gateway_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All error handling tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 