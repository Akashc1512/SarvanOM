#!/usr/bin/env python3
"""
Demo script for unified logging system functionality.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import unified logging
sys.path.append(str(Path(__file__).parent.parent / "shared" / "core"))
from unified_logging import setup_logging, get_logger


def demo_text_logging():
    """Demo text logging for development."""
    print("\n=== DEVELOPMENT MODE (Text Logging) ===")

    config = setup_logging(
        service_name="demo-service",
        version="1.0.0",
        log_level="DEBUG",
        log_format="text",
    )

    logger = get_logger("demo")

    # Demo different log levels
    logger.debug("🔍 Debug: Processing user request", user_id="user123")
    logger.info(
        "📥 Query received", query="What is machine learning?", request_id="req-001"
    )
    logger.info("🤖 Agent started", agent_name="retrieval_agent", task_id="task-001")
    logger.info("✅ Agent finished", agent_name="retrieval_agent", duration_ms=150)
    logger.warning("⚠️ Rate limit approaching", current_usage=85, limit=100)
    logger.error("❌ External service timeout", service="search_api", timeout_ms=5000)


def demo_json_logging():
    """Demo JSON logging for production."""
    print("\n=== PRODUCTION MODE (JSON Logging) ===")

    config = setup_logging(
        service_name="sarvanom-api",
        version="1.0.0",
        log_level="INFO",
        log_format="json",
    )

    logger = get_logger("sarvanom.api")

    # Demo structured logging
    logger.info(
        "FastAPI application startup",
        component="fastapi_startup",
        environment="production",
    )

    logger.info(
        "Query processing started",
        query="Climate change impact on agriculture",
        query_id="q123",
        user_id="user456",
        agents=["retrieval", "synthesis", "fact_check"],
    )

    logger.info(
        "Agent execution completed",
        agent_name="synthesis_agent",
        duration_ms=2340,
        tokens_used=1250,
        confidence=0.89,
        component="agent_execution",
    )


def demo_error_logging():
    """Demo error logging with stack traces."""
    print("\n=== ERROR HANDLING DEMO ===")

    logger = get_logger("error_demo")

    try:
        # Simulate an error
        data = {"key": "value"}
        missing = data["missing_key"]
    except KeyError:
        logger.exception(
            "Data processing error",
            operation="data_access",
            expected_key="missing_key",
            component="data_processor",
        )


def main():
    """Run logging demos."""
    print("🚀 Unified Logging System Demo")
    print("=" * 50)

    demo_text_logging()
    demo_json_logging()
    demo_error_logging()

    print("\n" + "=" * 50)
    print("✅ Demo completed! Logging system is working.")
    print("\nKey Features Demonstrated:")
    print("- Environment-based configuration (text vs JSON)")
    print("- Structured logging with metadata")
    print("- Different log levels")
    print("- Error handling with stack traces")
    print("- Request/agent lifecycle tracking")


if __name__ == "__main__":
    main()
