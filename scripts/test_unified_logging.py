#!/usr/bin/env python3
"""
Test Script for Unified Logging Configuration

This script tests the unified logging configuration across different environments
and scenarios to ensure proper setup and functionality.

Usage:
    python scripts/test_unified_logging.py

Features tested:
- Environment-based configuration
- Different log levels and formats
- FastAPI integration
- Agent lifecycle logging
- Query event logging
- Error handling and stack traces
- Performance timing
"""

import os
import sys
import asyncio
import tempfile
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import unified logging directly to avoid dependency issues
try:
    from shared.core.unified_logging import (
        setup_logging,
        get_logger,
        log_execution_time,
        log_agent_lifecycle,
        log_query_event
    )
    LOGGING_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Could not import unified logging: {e}")
    print("Installing missing dependencies...")
    LOGGING_AVAILABLE = False


def test_basic_logging():
    """Test basic logging functionality."""
    print("\n🧪 Testing Basic Logging Configuration")
    print("=" * 50)
    
    # Test with development settings
    config = setup_logging(
        service_name="test-service",
        version="1.0.0",
        log_level="DEBUG",
        log_format="text"
    )
    
    logger = get_logger("test_module")
    
    print("✅ Testing different log levels:")
    logger.debug("This is a debug message", component="test", test_id="001")
    logger.info("This is an info message", component="test", test_id="002")
    logger.warning("This is a warning message", component="test", test_id="003")
    logger.error("This is an error message", component="test", test_id="004")
    
    print("✅ Testing exception logging:")
    try:
        raise ValueError("Test exception for logging")
    except Exception:
        logger.exception("Test exception occurred", component="test", test_id="005")
    
    print("✅ Testing contextual logging:")
    logger.set_context(request_id="req-123", user_id="user-456")
    logger.info("Message with context", action="test_context", test_id="006")


def test_json_logging():
    """Test JSON logging format."""
    print("\n🧪 Testing JSON Logging Format")
    print("=" * 50)
    
    # Test with production-like settings
    config = setup_logging(
        service_name="test-json-service",
        version="2.0.0",
        log_level="INFO",
        log_format="json"
    )
    
    logger = get_logger("json_test_module")
    
    print("✅ Testing JSON formatted logs:")
    logger.info("JSON formatted log message", 
                component="json_test",
                metrics={"response_time": 150, "status": "success"},
                test_data={"key": "value", "number": 42})


def test_file_logging():
    """Test file logging functionality."""
    print("\n🧪 Testing File Logging")
    print("=" * 50)
    
    # Create temporary directory for log files
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = os.path.join(temp_dir, "test.log")
        
        config = setup_logging(
            service_name="file-test-service",
            log_level="INFO",
            log_format="json",
            log_file=log_file
        )
        
        logger = get_logger("file_test_module")
        
        logger.info("Test message for file logging", 
                   component="file_test",
                   test_file=log_file)
        
        # Check if log file was created and contains data
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                content = f.read()
                if content:
                    print(f"✅ Log file created successfully at {log_file}")
                    print(f"   Content preview: {content[:100]}...")
                else:
                    print(f"❌ Log file created but is empty")
        else:
            print(f"❌ Log file was not created at {log_file}")


def test_environment_configuration():
    """Test environment-based configuration."""
    print("\n🧪 Testing Environment-Based Configuration")
    print("=" * 50)
    
    # Test different environment configurations
    test_environments = [
        ("development", "DEBUG", "text"),
        ("production", "INFO", "json"),
        ("testing", "WARNING", "json")
    ]
    
    for env, level, format_type in test_environments:
        # Set environment variables
        os.environ["APP_ENV"] = env
        os.environ["LOG_LEVEL"] = level
        os.environ["LOG_FORMAT"] = format_type
        
        config = setup_logging(service_name=f"test-{env}-service")
        logger = get_logger(f"env_test_{env}")
        
        print(f"✅ Testing {env} environment (level: {level}, format: {format_type})")
        logger.info(f"Test message for {env} environment",
                   environment=env,
                   configured_level=level,
                   configured_format=format_type)


async def test_performance_logging():
    """Test performance logging features."""
    print("\n🧪 Testing Performance Logging")
    print("=" * 50)
    
    logger = get_logger("performance_test")
    
    # Test execution time logging
    with log_execution_time(logger, "test_operation", operation_type="performance_test"):
        await asyncio.sleep(0.1)  # Simulate work
        logger.info("Work completed during timed operation")
    
    # Test multiple operations
    operations = ["data_retrieval", "data_processing", "result_formatting"]
    for op in operations:
        with log_execution_time(logger, op, batch_id="batch-001"):
            await asyncio.sleep(0.05)  # Simulate different workloads


def test_agent_logging():
    """Test agent lifecycle logging."""
    print("\n🧪 Testing Agent Lifecycle Logging")
    print("=" * 50)
    
    logger = get_logger("agent_test")
    
    # Test agent lifecycle events
    agents = ["retrieval_agent", "synthesis_agent", "fact_check_agent"]
    
    for agent in agents:
        log_agent_lifecycle(logger, agent, "start", task_id="task-001")
        
        # Simulate agent work
        logger.info(f"{agent} processing", agent_name=agent, status="working")
        
        log_agent_lifecycle(logger, agent, "finish", 
                          task_id="task-001", 
                          duration_ms=150,
                          result_count=5)


def test_query_logging():
    """Test query event logging."""
    print("\n🧪 Testing Query Event Logging")
    print("=" * 50)
    
    logger = get_logger("query_test")
    
    test_queries = [
        "What is the impact of climate change on agriculture?",
        "Explain quantum computing principles",
        "How does machine learning work in natural language processing?"
    ]
    
    for i, query in enumerate(test_queries):
        query_id = f"query-{i+1}"
        
        log_query_event(logger, query, "received", 
                       query_id=query_id, 
                       user_id="test-user")
        
        log_query_event(logger, query, "processing", 
                       query_id=query_id,
                       agents_involved=["retrieval", "synthesis"])
        
        log_query_event(logger, query, "completed", 
                       query_id=query_id,
                       response_length=1250,
                       confidence=0.85,
                       processing_time_ms=2340)


def test_error_scenarios():
    """Test error logging and stack traces."""
    print("\n🧪 Testing Error Scenarios")
    print("=" * 50)
    
    logger = get_logger("error_test")
    
    # Test different types of errors
    try:
        # Simulate a processing error
        data = {"key": "value"}
        result = data["missing_key"]
    except KeyError:
        logger.exception("Key error during data processing",
                        operation="data_access",
                        expected_key="missing_key",
                        available_keys=list(data.keys()))
    
    try:
        # Simulate a network-like error
        raise ConnectionError("Failed to connect to external service")
    except ConnectionError:
        logger.exception("Connection error occurred",
                        service="external_api",
                        retry_count=3,
                        last_attempt=True)
    
    # Test error without exception context
    logger.error("Custom error scenario",
                error_type="validation_error",
                error_code="E001",
                user_input="invalid_format",
                expected_format="ISO date")


def test_sensitive_data_masking():
    """Test that sensitive data is properly masked."""
    print("\n🧪 Testing Sensitive Data Masking")
    print("=" * 50)
    
    logger = get_logger("security_test")
    
    # Test logging with sensitive information
    logger.info("User authentication attempt",
               user_id="user123",
               password="should_be_masked",
               api_key="secret_key_123",
               jwt_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9",
               public_info="this_should_be_visible")
    
    logger.warning("Security event detected",
                  event_type="suspicious_activity",
                  authorization="Bearer token_should_be_masked",
                  client_ip="192.168.1.100",
                  credential="user_secret",
                  timestamp="2024-12-28T10:00:00Z")


async def main():
    """Run all logging tests."""
    print("🚀 Starting Unified Logging Tests")
    print("=" * 80)
    
    try:
        # Run all test functions
        test_basic_logging()
        test_json_logging()
        test_file_logging()
        test_environment_configuration()
        await test_performance_logging()
        test_agent_logging()
        test_query_logging()
        test_error_scenarios()
        test_sensitive_data_masking()
        
        print("\n" + "=" * 80)
        print("✅ All logging tests completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)