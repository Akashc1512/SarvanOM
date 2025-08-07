#!/usr/bin/env python3
"""
Simple Error Handling Verification Script

This script tests the basic error handling functionality without complex imports.
"""

import sys
import os
import asyncio
import time
from typing import Dict, Any, Optional

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_error_handler_import():
    """Test if error handler can be imported."""
    try:
        from shared.core.error_handler import (
            ErrorSeverity,
            ErrorCategory,
            ErrorContext,
            ErrorInfo,
            ErrorResponse,
            CircuitBreaker,
            APIErrorHandler,
            LLMErrorHandler,
            DatabaseErrorHandler,
            handle_critical_operation,
            safe_api_call,
            safe_llm_call,
            safe_database_call,
            ErrorMonitor
        )
        print("✅ Error handler imports successful")
        return True
    except Exception as e:
        print(f"❌ Error handler import failed: {e}")
        return False

def test_circuit_breaker():
    """Test circuit breaker functionality."""
    try:
        from shared.core.error_handler import CircuitBreaker
        
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=5)
        
        # Test initial state
        assert cb.state == "CLOSED"
        assert cb.can_execute() == True
        
        # Test failure handling
        for i in range(3):
            cb.on_failure()
        
        # Should be open after 3 failures
        assert cb.state == "OPEN"
        assert cb.can_execute() == False
        
        # Test recovery
        cb.last_failure_time = time.time() - 10  # Simulate time passing
        assert cb.can_execute() == True
        assert cb.state == "HALF_OPEN"
        
        # Test success
        cb.on_success()
        assert cb.state == "CLOSED"
        assert cb.can_execute() == True
        
        print("✅ Circuit breaker tests passed")
        return True
    except Exception as e:
        print(f"❌ Circuit breaker test failed: {e}")
        return False

def test_error_categories():
    """Test error category and severity enums."""
    try:
        from shared.core.error_handler import ErrorSeverity, ErrorCategory
        
        # Test severity levels
        assert ErrorSeverity.LOW.value == "low"
        assert ErrorSeverity.CRITICAL.value == "critical"
        
        # Test error categories
        assert ErrorCategory.API_TIMEOUT.value == "api_timeout"
        assert ErrorCategory.LLM_RATE_LIMIT.value == "llm_rate_limit"
        assert ErrorCategory.DB_CONNECTION.value == "db_connection"
        
        print("✅ Error categories and severities tests passed")
        return True
    except Exception as e:
        print(f"❌ Error categories test failed: {e}")
        return False

def test_error_context():
    """Test error context creation."""
    try:
        from shared.core.error_handler import ErrorContext
        
        context = ErrorContext(
            operation="test_operation",
            service="test_service",
            user_id="user123",
            query="test query"
        )
        
        assert context.operation == "test_operation"
        assert context.service == "test_service"
        assert context.user_id == "user123"
        assert context.query == "test query"
        assert context.request_id is not None
        
        print("✅ Error context tests passed")
        return True
    except Exception as e:
        print(f"❌ Error context test failed: {e}")
        return False

def test_api_error_handler():
    """Test API error handler."""
    try:
        from shared.core.error_handler import APIErrorHandler, ErrorContext
        import asyncio
        
        handler = APIErrorHandler()
        context = ErrorContext(operation="test_api", service="test_service")
        
        # Test timeout error
        timeout_error = asyncio.TimeoutError("Request timed out")
        response = asyncio.run(handler.handle_error(timeout_error, context))
        
        assert response.success == False
        assert "timeout" in response.error.lower()
        assert response.retryable == True
        
        print("✅ API error handler tests passed")
        return True
    except Exception as e:
        print(f"❌ API error handler test failed: {e}")
        return False

def test_decorator_import():
    """Test if the decorator can be imported and used."""
    try:
        from shared.core.error_handler import handle_critical_operation
        
        @handle_critical_operation(operation_type="test", max_retries=2, timeout=10.0)
        async def test_function():
            return "success"
        
        # Test the function can be called
        result = asyncio.run(test_function())
        assert result == "success"
        
        print("✅ Decorator import and basic usage test passed")
        return True
    except Exception as e:
        print(f"❌ Decorator test failed: {e}")
        return False

def test_utility_functions():
    """Test utility function imports."""
    try:
        from shared.core.error_handler import (
            safe_api_call,
            safe_llm_call,
            safe_database_call
        )
        
        print("✅ Utility function imports successful")
        return True
    except Exception as e:
        print(f"❌ Utility function import failed: {e}")
        return False

def main():
    """Run all error handling tests."""
    print("🧪 Testing Error Handling System")
    print("=" * 50)
    
    tests = [
        test_error_handler_import,
        test_error_categories,
        test_error_context,
        test_circuit_breaker,
        test_api_error_handler,
        test_decorator_import,
        test_utility_functions
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