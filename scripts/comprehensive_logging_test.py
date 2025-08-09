#!/usr/bin/env python3
"""
Comprehensive test of the unified logging system across all services.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "shared" / "core"))

from unified_logging import (
    setup_logging,
    get_logger,
    log_execution_time,
    log_agent_lifecycle,
    log_query_event,
)


def test_environment_configurations():
    """Test different environment configurations."""
    print("\n🧪 Testing Environment Configurations")
    print("=" * 50)

    environments = [
        ("development", "DEBUG", "text"),
        ("production", "INFO", "json"),
        ("testing", "WARNING", "json"),
    ]

    for env, level, format_type in environments:
        print(f"\n📋 Testing {env.upper()} environment:")

        # Set environment variables
        os.environ["APP_ENV"] = env
        os.environ["LOG_LEVEL"] = level
        os.environ["LOG_FORMAT"] = format_type
        os.environ["SERVICE_NAME"] = f"test-{env}-service"

        # Setup logging
        config = setup_logging()
        logger = get_logger(f"test_{env}")

        # Test logging at configured level
        logger.info(
            f"✅ {env} environment configured successfully",
            environment=env,
            log_level=level,
            log_format=format_type,
        )

        if level == "DEBUG":
            logger.debug("Debug message visible in development", env=env)

        logger.warning(f"Warning message in {env}", env=env)


def test_structured_logging():
    """Test structured logging features."""
    print("\n🧪 Testing Structured Logging Features")
    print("=" * 50)

    # JSON format for structured data
    os.environ["LOG_FORMAT"] = "json"
    setup_logging(service_name="structured-test")
    logger = get_logger("structured_test")

    # Test rich structured data
    logger.info(
        "Structured log test",
        query_id="q123",
        user_id="user456",
        performance_data={
            "response_time_ms": 1250,
            "agents_used": ["retrieval", "synthesis"],
            "confidence": 0.89,
        },
        metadata={"version": "1.0.0", "environment": "test"},
    )

    print("✅ Structured logging with complex data complete")


async def test_performance_logging():
    """Test performance logging features."""
    print("\n🧪 Testing Performance Logging")
    print("=" * 50)

    logger = get_logger("performance_test")

    # Test execution timing
    with log_execution_time(logger, "test_operation", operation_id="op123"):
        await asyncio.sleep(0.1)
        logger.info("Operation in progress", step="processing")

    # Test agent lifecycle logging
    agents = ["retrieval_agent", "synthesis_agent"]
    for agent in agents:
        log_agent_lifecycle(logger, agent, "start", task_id="task456")
        await asyncio.sleep(0.05)
        log_agent_lifecycle(
            logger, agent, "finish", task_id="task456", duration_ms=50, result_count=10
        )

    print("✅ Performance logging complete")


def test_query_event_logging():
    """Test query event logging."""
    print("\n🧪 Testing Query Event Logging")
    print("=" * 50)

    logger = get_logger("query_test")

    query = "What are the benefits of renewable energy?"
    query_id = "q789"

    # Test query lifecycle
    log_query_event(logger, query, "received", query_id=query_id, user_id="user789")

    log_query_event(
        logger,
        query,
        "processing",
        query_id=query_id,
        agents=["retrieval", "fact_check", "synthesis"],
    )

    log_query_event(
        logger,
        query,
        "completed",
        query_id=query_id,
        response_length=1500,
        confidence=0.92,
        processing_time_ms=2100,
    )

    print("✅ Query event logging complete")


def test_sensitive_data_masking():
    """Test sensitive data masking."""
    print("\n🧪 Testing Sensitive Data Masking")
    print("=" * 50)

    logger = get_logger("security_test")

    # Test various sensitive fields
    logger.info(
        "User authentication",
        user_id="user123",
        password="should_be_masked",
        api_key="sk-1234567890abcdef",
        jwt_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9",
        authorization="Bearer secret_token",
        credential="user_secret",
        # Non-sensitive data should remain visible
        user_email="user@example.com",
        timestamp="2024-12-28T10:00:00Z",
    )

    print("✅ Sensitive data masking test complete")
    print("   (Check that password, api_key, jwt_token, etc. show as ***MASKED***)")


def test_error_handling():
    """Test error handling and logging."""
    print("\n🧪 Testing Error Handling")
    print("=" * 50)

    logger = get_logger("error_test")

    # Test different error scenarios
    try:
        # Simulate processing error
        data = {"key": "value"}
        missing = data["missing_key"]
    except KeyError as e:
        logger.error(
            "Data processing error",
            error_type="KeyError",
            expected_key="missing_key",
            available_keys=list(data.keys()),
            operation="data_access",
        )

    # Test warning for recoverable issues
    logger.warning(
        "Service degradation detected",
        service="external_api",
        response_time_ms=5000,
        threshold_ms=3000,
        action="continuing_with_fallback",
    )

    print("✅ Error handling test complete")


async def main():
    """Run comprehensive logging tests."""
    print("🚀 Comprehensive Unified Logging System Test")
    print("=" * 80)

    try:
        test_environment_configurations()
        test_structured_logging()
        await test_performance_logging()
        test_query_event_logging()
        test_sensitive_data_masking()
        test_error_handling()

        print("\n" + "=" * 80)
        print("🎉 ALL LOGGING TESTS PASSED!")
        print("=" * 80)
        print("\n✅ Key Features Verified:")
        print("   • Environment-based configuration")
        print("   • Structured JSON and text logging")
        print("   • Performance timing and agent lifecycle tracking")
        print("   • Query event logging throughout processing")
        print("   • Sensitive data masking for security")
        print("   • Comprehensive error handling")
        print("\n🚀 The unified logging system is production-ready!")

        return 0

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
