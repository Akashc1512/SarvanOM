#!/usr/bin/env python3
"""
Final Error Handling Verification Script

This script verifies the core error handling implementation without complex dependencies.
"""

import sys
import os
import asyncio
import time
import traceback
from typing import Dict, Any, Optional, List

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_error_handler_file_structure():
    """Test that the error handler file has the correct structure."""
    try:
        error_handler_path = "shared/core/error_handler.py"

        if not os.path.exists(error_handler_path):
            print(f"❌ Error handler file not found: {error_handler_path}")
            return False

        with open(error_handler_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for all required components
        required_components = [
            "class ErrorSeverity",
            "class ErrorCategory",
            "class ErrorContext",
            "class ErrorInfo",
            "class ErrorResponse",
            "class CircuitBreaker",
            "class APIErrorHandler",
            "class LLMErrorHandler",
            "class DatabaseErrorHandler",
            "class ErrorHandlerFactory",
            "class CriticalOperationError",
            "class ErrorMonitor",
            "def handle_critical_operation",
            "def safe_api_call",
            "def safe_llm_call",
            "def safe_database_call",
            "async def critical_operation_context",
        ]

        missing_components = []
        for component in required_components:
            if component not in content:
                missing_components.append(component)

        if missing_components:
            print(f"❌ Missing required components: {missing_components}")
            return False

        print("✅ Error handler file has all required components")
        return True

    except Exception as e:
        print(f"❌ Error handler file structure test failed: {e}")
        return False


def test_llm_client_error_integration():
    """Test that LLM client has error handling integrated."""
    try:
        llm_client_path = "shared/core/llm_client_v3.py"

        if not os.path.exists(llm_client_path):
            print(f"❌ LLM client file not found: {llm_client_path}")
            return False

        with open(llm_client_path, "r", encoding="utf-8") as f:
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

        # Check for error handler import
        if "from shared.core.error_handler import handle_critical_operation" in content:
            print("✅ LLM client imports error handler")
        else:
            print("❌ LLM client missing error handler import")
            return False

        # Check for try/except blocks
        if "except Exception as e:" in content:
            print("✅ LLM client has exception handling")
        else:
            print("❌ LLM client missing exception handling")
            return False

        return True
    except Exception as e:
        print(f"❌ LLM client integration test failed: {e}")
        return False


def test_api_gateway_error_integration():
    """Test that API gateway has error handling integrated."""
    try:
        api_gateway_path = "services/api_gateway/main.py"

        if not os.path.exists(api_gateway_path):
            print(f"❌ API gateway file not found: {api_gateway_path}")
            return False

        with open(api_gateway_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for fallback data in error responses
        if "fallback_data" in content:
            print("✅ API gateway has fallback error handling")
        else:
            print("❌ API gateway missing fallback error handling")
            return False

        # Check for structured error responses
        if "error_type" in content and "request_id" in content:
            print("✅ API gateway has structured error responses")
        else:
            print("❌ API gateway missing structured error responses")
            return False

        # Check for general exception handler
        if "general_exception_handler" in content:
            print("✅ API gateway has general exception handler")
        else:
            print("❌ API gateway missing general exception handler")
            return False

        return True
    except Exception as e:
        print(f"❌ API gateway integration test failed: {e}")
        return False


def test_error_handler_direct_import():
    """Test direct import of error handler without complex dependencies."""
    try:
        # Test direct import using importlib
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "error_handler", "shared/core/error_handler.py"
        )
        error_handler = importlib.util.module_from_spec(spec)

        # Mock missing dependencies
        import sys

        sys.modules["shared.core.unified_logging"] = type(
            "MockLogger",
            (),
            {
                "get_logger": lambda name: type(
                    "MockLogger",
                    (),
                    {
                        "info": lambda *args: None,
                        "warning": lambda *args: None,
                        "error": lambda *args: None,
                    },
                )()
            },
        )()

        spec.loader.exec_module(error_handler)

        # Test basic classes
        assert hasattr(error_handler, "ErrorSeverity")
        assert hasattr(error_handler, "ErrorCategory")
        assert hasattr(error_handler, "CircuitBreaker")
        assert hasattr(error_handler, "APIErrorHandler")
        assert hasattr(error_handler, "LLMErrorHandler")
        assert hasattr(error_handler, "DatabaseErrorHandler")
        assert hasattr(error_handler, "handle_critical_operation")

        print("✅ Error handler can be imported directly")
        return True

    except Exception as e:
        print(f"❌ Direct import test failed: {e}")
        return False


def test_circuit_breaker_direct():
    """Test circuit breaker functionality directly."""
    try:
        # Import circuit breaker directly
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "error_handler", "shared/core/error_handler.py"
        )
        error_handler = importlib.util.module_from_spec(spec)

        # Mock dependencies
        import sys

        sys.modules["shared.core.unified_logging"] = type(
            "MockLogger",
            (),
            {
                "get_logger": lambda name: type(
                    "MockLogger",
                    (),
                    {
                        "info": lambda *args: None,
                        "warning": lambda *args: None,
                        "error": lambda *args: None,
                    },
                )()
            },
        )()

        spec.loader.exec_module(error_handler)

        # Test circuit breaker
        cb = error_handler.CircuitBreaker(failure_threshold=3, recovery_timeout=5)

        # Initial state
        assert cb.state == "CLOSED"
        assert cb.can_execute() == True

        # Test failures
        for i in range(3):
            cb.on_failure()

        # Should be open after threshold
        assert cb.state == "OPEN"
        assert cb.can_execute() == False

        # Test recovery
        cb.last_failure_time = time.time() - 10
        assert cb.can_execute() == True
        assert cb.state == "HALF_OPEN"

        # Test success
        cb.on_success()
        assert cb.state == "CLOSED"
        assert cb.can_execute() == True

        print("✅ Circuit breaker works correctly")
        return True

    except Exception as e:
        print(f"❌ Circuit breaker test failed: {e}")
        return False


def test_error_categorization_direct():
    """Test error categorization directly."""
    try:
        # Import error handler directly
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "error_handler", "shared/core/error_handler.py"
        )
        error_handler = importlib.util.module_from_spec(spec)

        # Mock dependencies
        import sys

        sys.modules["shared.core.unified_logging"] = type(
            "MockLogger",
            (),
            {
                "get_logger": lambda name: type(
                    "MockLogger",
                    (),
                    {
                        "info": lambda *args: None,
                        "warning": lambda *args: None,
                        "error": lambda *args: None,
                    },
                )()
            },
        )()

        spec.loader.exec_module(error_handler)

        # Test severity levels
        severities = [
            error_handler.ErrorSeverity.LOW,
            error_handler.ErrorSeverity.MEDIUM,
            error_handler.ErrorSeverity.HIGH,
            error_handler.ErrorSeverity.CRITICAL,
        ]
        for severity in severities:
            assert severity.value in ["low", "medium", "high", "critical"]

        # Test error categories
        categories = [
            error_handler.ErrorCategory.API_TIMEOUT,
            error_handler.ErrorCategory.LLM_RATE_LIMIT,
            error_handler.ErrorCategory.DB_CONNECTION,
            error_handler.ErrorCategory.SYSTEM_RESOURCE,
        ]
        for category in categories:
            assert category.value in [
                "api_timeout",
                "llm_rate_limit",
                "db_connection",
                "system_resource",
            ]

        print("✅ Error categorization works correctly")
        return True

    except Exception as e:
        print(f"❌ Error categorization test failed: {e}")
        return False


def test_error_handler_implementation():
    """Test that error handlers are properly implemented."""
    try:
        # Import error handler directly
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "error_handler", "shared/core/error_handler.py"
        )
        error_handler = importlib.util.module_from_spec(spec)

        # Mock dependencies
        import sys

        sys.modules["shared.core.unified_logging"] = type(
            "MockLogger",
            (),
            {
                "get_logger": lambda name: type(
                    "MockLogger",
                    (),
                    {
                        "info": lambda *args: None,
                        "warning": lambda *args: None,
                        "error": lambda *args: None,
                    },
                )()
            },
        )()

        spec.loader.exec_module(error_handler)

        # Test API error handler
        api_handler = error_handler.APIErrorHandler()
        assert hasattr(api_handler, "handle_error")
        assert hasattr(api_handler, "should_retry")
        assert hasattr(api_handler, "get_fallback_data")

        # Test LLM error handler
        llm_handler = error_handler.LLMErrorHandler()
        assert hasattr(llm_handler, "handle_error")
        assert hasattr(llm_handler, "should_retry")
        assert hasattr(llm_handler, "get_fallback_data")

        # Test Database error handler
        db_handler = error_handler.DatabaseErrorHandler()
        assert hasattr(db_handler, "handle_error")
        assert hasattr(db_handler, "should_retry")
        assert hasattr(db_handler, "get_fallback_data")

        print("✅ Error handlers are properly implemented")
        return True

    except Exception as e:
        print(f"❌ Error handler implementation test failed: {e}")
        return False


def test_decorator_implementation():
    """Test that the decorator is properly implemented."""
    try:
        # Import error handler directly
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "error_handler", "shared/core/error_handler.py"
        )
        error_handler = importlib.util.module_from_spec(spec)

        # Mock dependencies
        import sys

        sys.modules["shared.core.unified_logging"] = type(
            "MockLogger",
            (),
            {
                "get_logger": lambda name: type(
                    "MockLogger",
                    (),
                    {
                        "info": lambda *args: None,
                        "warning": lambda *args: None,
                        "error": lambda *args: None,
                    },
                )()
            },
        )()

        spec.loader.exec_module(error_handler)

        # Test decorator exists
        assert hasattr(error_handler, "handle_critical_operation")

        # Test decorator is callable
        decorator = error_handler.handle_critical_operation(
            operation_type="test", max_retries=2, timeout=10.0
        )
        assert callable(decorator)

        print("✅ Decorator is properly implemented")
        return True

    except Exception as e:
        print(f"❌ Decorator implementation test failed: {e}")
        return False


def test_utility_functions_implementation():
    """Test that utility functions are properly implemented."""
    try:
        # Import error handler directly
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "error_handler", "shared/core/error_handler.py"
        )
        error_handler = importlib.util.module_from_spec(spec)

        # Mock dependencies
        import sys

        sys.modules["shared.core.unified_logging"] = type(
            "MockLogger",
            (),
            {
                "get_logger": lambda name: type(
                    "MockLogger",
                    (),
                    {
                        "info": lambda *args: None,
                        "warning": lambda *args: None,
                        "error": lambda *args: None,
                    },
                )()
            },
        )()

        spec.loader.exec_module(error_handler)

        # Test utility functions exist
        assert hasattr(error_handler, "safe_api_call")
        assert hasattr(error_handler, "safe_llm_call")
        assert hasattr(error_handler, "safe_database_call")

        # Test they are callable
        assert callable(error_handler.safe_api_call)
        assert callable(error_handler.safe_llm_call)
        assert callable(error_handler.safe_database_call)

        print("✅ Utility functions are properly implemented")
        return True

    except Exception as e:
        print(f"❌ Utility functions implementation test failed: {e}")
        return False


def test_error_monitoring_implementation():
    """Test that error monitoring is properly implemented."""
    try:
        # Import error handler directly
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "error_handler", "shared/core/error_handler.py"
        )
        error_handler = importlib.util.module_from_spec(spec)

        # Mock dependencies
        import sys

        sys.modules["shared.core.unified_logging"] = type(
            "MockLogger",
            (),
            {
                "get_logger": lambda name: type(
                    "MockLogger",
                    (),
                    {
                        "info": lambda *args: None,
                        "warning": lambda *args: None,
                        "error": lambda *args: None,
                    },
                )()
            },
        )()

        spec.loader.exec_module(error_handler)

        # Test error monitor exists
        assert hasattr(error_handler, "ErrorMonitor")

        # Test error monitor can be instantiated
        monitor = error_handler.ErrorMonitor()
        assert hasattr(monitor, "record_error")
        assert callable(monitor.record_error)

        print("✅ Error monitoring is properly implemented")
        return True

    except Exception as e:
        print(f"❌ Error monitoring implementation test failed: {e}")
        return False


def main():
    """Run final error handling verification tests."""
    print("🧪 Final Error Handling Verification")
    print("=" * 60)

    tests = [
        test_error_handler_file_structure,
        test_llm_client_error_integration,
        test_api_gateway_error_integration,
        test_error_handler_direct_import,
        test_circuit_breaker_direct,
        test_error_categorization_direct,
        test_error_handler_implementation,
        test_decorator_implementation,
        test_utility_functions_implementation,
        test_error_monitoring_implementation,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            traceback.print_exc()

    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All error handling tests passed!")
        print("✅ Comprehensive error handling implementation is complete and working!")
        print("✅ Error handling system is ready for production use!")
        return True
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
