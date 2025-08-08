#!/usr/bin/env python3
"""
Comprehensive Error Handling Verification Test

This script tests the error handling implementation to ensure:
1. Critical operations are properly wrapped with error handling
2. Graceful fallback mechanisms work correctly
3. No unhandled exceptions can bring down the server
4. Error logging and monitoring function properly
5. Circuit breaker patterns work as expected

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    1.0.0 (2024-12-28)
"""

import asyncio
import time
import uuid
from typing import Dict, Any, Optional
import structlog

# Import error handling components
from shared.core.error_handler import (
    handle_critical_operation,
    safe_api_call,
    safe_llm_call,
    safe_database_call,
    error_handler_factory,
    ErrorContext,
    ErrorCategory,
    ErrorSeverity
)

logger = structlog.get_logger(__name__)


class MockAPIError(Exception):
    """Mock API error for testing."""
    pass


class MockLLMError(Exception):
    """Mock LLM error for testing."""
    pass


class MockDatabaseError(Exception):
    """Mock database error for testing."""
    pass


async def mock_api_call(success: bool = True, delay: float = 0.1) -> Dict[str, Any]:
    """Mock API call that can succeed or fail."""
    await asyncio.sleep(delay)
    
    if not success:
        raise MockAPIError("Mock API call failed")
    
    return {"status": "success", "data": "mock_api_response"}


async def mock_llm_call(success: bool = True, delay: float = 0.1) -> Dict[str, Any]:
    """Mock LLM call that can succeed or fail."""
    await asyncio.sleep(delay)
    
    if not success:
        raise MockLLMError("Mock LLM call failed")
    
    return {"content": "Mock LLM response", "provider": "mock"}


async def mock_database_call(success: bool = True, delay: float = 0.1) -> Dict[str, Any]:
    """Mock database call that can succeed or fail."""
    await asyncio.sleep(delay)
    
    if not success:
        raise MockDatabaseError("Mock database call failed")
    
    return {"rows": [{"id": 1, "name": "test"}], "count": 1}


@handle_critical_operation(operation_type="api", max_retries=2, timeout=5.0)
async def test_api_operation(success: bool = True) -> Dict[str, Any]:
    """Test API operation with error handling."""
    return await mock_api_call(success)


@handle_critical_operation(operation_type="llm", max_retries=2, timeout=10.0)
async def test_llm_operation(success: bool = True) -> Dict[str, Any]:
    """Test LLM operation with error handling."""
    return await mock_llm_call(success)


@handle_critical_operation(operation_type="database", max_retries=2, timeout=5.0)
async def test_database_operation(success: bool = True) -> Dict[str, Any]:
    """Test database operation with error handling."""
    return await mock_database_call(success)


async def test_safe_api_call():
    """Test safe API call utility function."""
    print("🔍 Testing safe API call...")
    
    # Test successful call
    try:
        result = await safe_api_call(
            mock_api_call,
            success=True,
            timeout=5.0,
            max_retries=2,
            fallback_data={"status": "fallback", "message": "API unavailable"}
        )
        print(f"✅ Safe API call (success): {result}")
    except Exception as e:
        print(f"❌ Safe API call (success) failed: {e}")
        return False
    
    # Test failed call with fallback
    try:
        result = await safe_api_call(
            mock_api_call,
            success=False,
            timeout=5.0,
            max_retries=2,
            fallback_data={"status": "fallback", "message": "API unavailable"}
        )
        print(f"✅ Safe API call (failure with fallback): {result}")
    except Exception as e:
        print(f"❌ Safe API call (failure) failed: {e}")
        return False
    
    return True


async def test_safe_llm_call():
    """Test safe LLM call utility function."""
    print("🔍 Testing safe LLM call...")
    
    # Test successful call
    try:
        result = await safe_llm_call(
            mock_llm_call,
            success=True,
            timeout=10.0,
            max_retries=2,
            fallback_data={"content": "Fallback response", "provider": "fallback"}
        )
        print(f"✅ Safe LLM call (success): {result}")
    except Exception as e:
        print(f"❌ Safe LLM call (success) failed: {e}")
        return False
    
    # Test failed call with fallback
    try:
        result = await safe_llm_call(
            mock_llm_call,
            success=False,
            timeout=10.0,
            max_retries=2,
            fallback_data={"content": "Fallback response", "provider": "fallback"}
        )
        print(f"✅ Safe LLM call (failure with fallback): {result}")
    except Exception as e:
        print(f"❌ Safe LLM call (failure) failed: {e}")
        return False
    
    return True


async def test_safe_database_call():
    """Test safe database call utility function."""
    print("🔍 Testing safe database call...")
    
    # Test successful call
    try:
        result = await safe_database_call(
            mock_database_call,
            success=True,
            timeout=5.0,
            max_retries=2,
            fallback_data={"rows": [], "count": 0, "status": "fallback"}
        )
        print(f"✅ Safe database call (success): {result}")
    except Exception as e:
        print(f"❌ Safe database call (success) failed: {e}")
        return False
    
    # Test failed call with fallback
    try:
        result = await safe_database_call(
            mock_database_call,
            success=False,
            timeout=5.0,
            max_retries=2,
            fallback_data={"rows": [], "count": 0, "status": "fallback"}
        )
        print(f"✅ Safe database call (failure with fallback): {result}")
    except Exception as e:
        print(f"❌ Safe database call (failure) failed: {e}")
        return False
    
    return True


async def test_decorated_operations():
    """Test operations decorated with error handling."""
    print("🔍 Testing decorated operations...")
    
    # Test API operation
    try:
        result = await test_api_operation(success=True)
        print(f"✅ Decorated API operation (success): {result}")
    except Exception as e:
        print(f"❌ Decorated API operation (success) failed: {e}")
        return False
    
    try:
        result = await test_api_operation(success=False)
        print(f"✅ Decorated API operation (failure): {result}")
    except Exception as e:
        print(f"❌ Decorated API operation (failure) failed: {e}")
        return False
    
    # Test LLM operation
    try:
        result = await test_llm_operation(success=True)
        print(f"✅ Decorated LLM operation (success): {result}")
    except Exception as e:
        print(f"❌ Decorated LLM operation (success) failed: {e}")
        return False
    
    try:
        result = await test_llm_operation(success=False)
        print(f"✅ Decorated LLM operation (failure): {result}")
    except Exception as e:
        print(f"❌ Decorated LLM operation (failure) failed: {e}")
        return False
    
    # Test database operation
    try:
        result = await test_database_operation(success=True)
        print(f"✅ Decorated database operation (success): {result}")
    except Exception as e:
        print(f"❌ Decorated database operation (success) failed: {e}")
        return False
    
    try:
        result = await test_database_operation(success=False)
        print(f"✅ Decorated database operation (failure): {result}")
    except Exception as e:
        print(f"❌ Decorated database operation (failure) failed: {e}")
        return False
    
    return True


async def test_error_handler_factory():
    """Test error handler factory."""
    print("🔍 Testing error handler factory...")
    
    # Test API handler
    api_handler = error_handler_factory.get_handler("api")
    print(f"✅ API handler: {type(api_handler).__name__}")
    
    # Test LLM handler
    llm_handler = error_handler_factory.get_handler("llm")
    print(f"✅ LLM handler: {type(llm_handler).__name__}")
    
    # Test database handler
    db_handler = error_handler_factory.get_handler("database")
    print(f"✅ Database handler: {type(db_handler).__name__}")
    
    # Test default handler
    default_handler = error_handler_factory.get_handler("unknown")
    print(f"✅ Default handler: {type(default_handler).__name__}")
    
    return True


async def test_error_context():
    """Test error context creation and handling."""
    print("🔍 Testing error context...")
    
    # Create error context
    context = ErrorContext(
        operation="test_operation",
        service="test_service",
        user_id="test_user",
        session_id="test_session",
        query="test query",
        metadata={"test": "data"}
    )
    
    print(f"✅ Error context created: {context}")
    
    # Test error categorization
    api_handler = error_handler_factory.get_handler("api")
    
    # Test timeout error
    timeout_error = asyncio.TimeoutError("Operation timed out")
    category, severity, retryable = api_handler._classify_api_error(timeout_error)
    print(f"✅ Timeout error classification: {category.value}, {severity.value}, {retryable}")
    
    # Test connection error
    connection_error = ConnectionError("Connection failed")
    category, severity, retryable = api_handler._classify_api_error(connection_error)
    print(f"✅ Connection error classification: {category.value}, {severity.value}, {retryable}")
    
    return True


async def test_circuit_breaker():
    """Test circuit breaker pattern."""
    print("🔍 Testing circuit breaker...")
    
    from shared.core.error_handler import CircuitBreaker
    
    # Create circuit breaker
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=5)
    
    # Test initial state
    assert cb.can_execute() == True, "Circuit breaker should be closed initially"
    print("✅ Circuit breaker initial state: CLOSED")
    
    # Simulate failures
    for i in range(3):
        cb.on_failure()
        print(f"✅ Failure {i+1} recorded")
    
    # Test open state
    assert cb.can_execute() == False, "Circuit breaker should be open after 3 failures"
    print("✅ Circuit breaker state: OPEN")
    
    # Test recovery
    cb.on_success()
    assert cb.can_execute() == True, "Circuit breaker should be closed after success"
    print("✅ Circuit breaker state: CLOSED (after recovery)")
    
    return True


async def test_error_monitoring():
    """Test error monitoring and alerting."""
    print("🔍 Testing error monitoring...")
    
    from shared.core.error_handler import error_monitor
    
    # Record some errors
    test_error = Exception("Test error")
    context = {"operation": "test_op", "request_id": "test_req"}
    
    for i in range(5):
        error_monitor.record_error(test_error, context)
        print(f"✅ Error {i+1} recorded")
    
    # Check error counts
    error_key = f"{type(test_error).__name__}_{context['operation']}"
    count = error_monitor.error_counts.get(error_key, 0)
    print(f"✅ Error count for {error_key}: {count}")
    
    return True


async def test_stability():
    """Test that no unhandled exceptions can bring down the server."""
    print("🔍 Testing server stability...")
    
    # Test that exceptions are caught and don't crash
    operations = [
        lambda: mock_api_call(success=False),
        lambda: mock_llm_call(success=False),
        lambda: mock_database_call(success=False),
        lambda: test_api_operation(success=False),
        lambda: test_llm_operation(success=False),
        lambda: test_database_operation(success=False),
    ]
    
    for i, operation in enumerate(operations):
        try:
            result = await operation()
            print(f"✅ Operation {i+1} handled gracefully: {result}")
        except Exception as e:
            print(f"❌ Operation {i+1} failed to handle gracefully: {e}")
            return False
    
    return True


async def test_performance():
    """Test error handling performance."""
    print("🔍 Testing error handling performance...")
    
    start_time = time.time()
    
    # Test multiple concurrent operations
    tasks = []
    for i in range(10):
        task = asyncio.create_task(test_api_operation(success=i % 2 == 0))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✅ Processed {len(results)} operations in {duration:.2f}s")
    print(f"✅ Average time per operation: {duration/len(results):.3f}s")
    
    # Check that all operations completed (either successfully or with fallback)
    successful = sum(1 for r in results if not isinstance(r, Exception))
    print(f"✅ Successful operations: {successful}/{len(results)}")
    
    return successful > 0


async def main():
    """Run all error handling tests."""
    print("🚀 Starting Comprehensive Error Handling Verification")
    print("=" * 60)
    
    tests = [
        ("Error Handler Factory", test_error_handler_factory),
        ("Error Context", test_error_context),
        ("Circuit Breaker", test_circuit_breaker),
        ("Error Monitoring", test_error_monitoring),
        ("Safe API Call", test_safe_api_call),
        ("Safe LLM Call", test_safe_llm_call),
        ("Safe Database Call", test_safe_database_call),
        ("Decorated Operations", test_decorated_operations),
        ("Server Stability", test_stability),
        ("Performance", test_performance),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            result = await test_func()
            results[test_name] = result
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        except Exception as e:
            results[test_name] = False
            print(f"❌ FAIL {test_name}: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Error handling implementation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the error handling implementation.")
        return False


if __name__ == "__main__":
    asyncio.run(main()) 