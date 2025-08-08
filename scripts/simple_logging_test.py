#!/usr/bin/env python3
"""
Simple Unified Logging Test

This script tests the core logging functionality without external dependencies.
"""

import os
import sys
import logging
import json
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the logging module directly
try:
    import sys
    sys.path.append(str(Path(__file__).parent.parent / "shared" / "core"))
    from unified_logging import setup_logging, get_logger
    print("✅ Successfully imported unified logging")
except ImportError as e:
    print(f"❌ Could not import unified logging: {e}")
    sys.exit(1)

def test_basic_configuration():
    """Test basic logging configuration."""
    print("\n🧪 Testing Basic Configuration")
    print("=" * 40)
    
    # Test development configuration
    print("📝 Setting up development logging...")
    config = setup_logging(
        service_name="test-service",
        version="1.0.0",
        log_level="DEBUG",
        log_format="text"
    )
    
    logger = get_logger("test_module")
    
    print("✅ Testing log levels:")
    logger.debug("Debug message", test=True)
    logger.info("Info message", test=True)
    logger.warning("Warning message", test=True)
    logger.error("Error message", test=True)
    
    return True


def test_json_configuration():
    """Test JSON logging configuration."""
    print("\n🧪 Testing JSON Configuration")
    print("=" * 40)
    
    # Test production-like configuration
    print("📝 Setting up JSON logging...")
    config = setup_logging(
        service_name="json-test-service",
        version="2.0.0",
        log_level="INFO",
        log_format="json"
    )
    
    logger = get_logger("json_test")
    
    print("✅ Testing JSON formatted logs:")
    logger.info("JSON test message", 
               component="test",
               data={"key": "value", "number": 42})
    
    return True


def test_environment_variables():
    """Test environment variable configuration."""
    print("\n🧪 Testing Environment Variables")
    print("=" * 40)
    
    # Set environment variables
    os.environ["LOG_LEVEL"] = "WARNING"
    os.environ["LOG_FORMAT"] = "json"
    os.environ["SERVICE_NAME"] = "env-test-service"
    
    print("📝 Setting up environment-based logging...")
    config = setup_logging()
    logger = get_logger("env_test")
    
    print("✅ Testing environment configuration:")
    logger.warning("Warning message from environment config", env_test=True)
    logger.error("Error message from environment config", env_test=True)
    
    # Clean up
    del os.environ["LOG_LEVEL"]
    del os.environ["LOG_FORMAT"]
    del os.environ["SERVICE_NAME"]
    
    return True


def test_context_logging():
    """Test context-aware logging."""
    print("\n🧪 Testing Context Logging")
    print("=" * 40)
    
    logger = get_logger("context_test")
    
    print("✅ Testing context setting:")
    logger.set_context(request_id="req-123", user_id="user-456")
    logger.info("Message with context", operation="test")
    
    logger.set_context(request_id="req-456")
    logger.info("Message with different context", operation="test2")
    
    return True


def test_exception_logging():
    """Test exception logging."""
    print("\n🧪 Testing Exception Logging")
    print("=" * 40)
    
    logger = get_logger("exception_test")
    
    print("✅ Testing exception handling:")
    try:
        raise ValueError("Test exception for logging")
    except Exception:
        logger.exception("Exception occurred during test", test_component="exception_handler")
    
    return True


def main():
    """Run all tests."""
    print("🚀 Starting Simple Logging Tests")
    print("=" * 60)
    
    tests = [
        test_basic_configuration,
        test_json_configuration,
        test_environment_variables,
        test_context_logging,
        test_exception_logging
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✅ {test.__name__} PASSED")
            else:
                failed += 1
                print(f"❌ {test.__name__} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Unified logging is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())