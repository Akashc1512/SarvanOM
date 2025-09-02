"""
Comprehensive Test Configuration for SarvanOM Backend

This module provides fixtures and utilities for testing the backend with real LLM providers.
All tests use actual LLM services (Ollama, OpenAI, Anthropic) instead of mocks for
end-to-end validation.
"""

import pytest
import asyncio
import os
import sys
from typing import Any, Optional, Dict
from unittest.mock import patch
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the main application
from services.gateway.main import app

# Test-specific configuration to bypass security middleware for testing
import os
os.environ["TESTING"] = "true"

# Test configuration
PERFORMANCE_THRESHOLD = 30.0  # seconds for real LLM calls
TEST_TIMEOUT = 60.0  # seconds for real LLM calls


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> TestClient:
    """Get synchronous test client for API testing with proper security headers."""
    return TestClient(app, headers={"host": "localhost"})


@pytest.fixture
def test_data():
    """Provide test data for unit tests."""
    return {
        "valid_query": {
            "query": "What is Python 3.13.5?",
            "max_tokens": 1000,
            "confidence_threshold": 0.8,
        },
        "valid_auth": {"username": "admin", "password": "password"},
        "invalid_auth": {"username": "wrong", "password": "wrong"},
        "empty_query": {"query": "", "max_tokens": 1000},
        "long_query": {"query": "x" * 10001, "max_tokens": 1000},
        "complex_query": {
            "query": "Analyze the impact of artificial intelligence on modern society",
            "max_tokens": 2000,
            "confidence_threshold": 0.9,
        },
        "synthesis_query": {
            "query": "Synthesize information about machine learning",
            "sources": ["source1.com", "source2.org"],
            "user_id": "test_user"
        },
        "fact_check_query": {
            "content": "The Earth is flat",
            "user_id": "test_user",
            "context": "Scientific claim verification"
        }
    }


@pytest.fixture
def llm_test_queries():
    """Provide test queries specifically for LLM testing."""
    return {
        "simple": "What is Python programming?",
        "medium": "Explain the key principles of machine learning",
        "complex": "Analyze the philosophical implications of quantum mechanics in the context of deterministic chaos theory",
        "technical": "Compare and contrast different approaches to natural language processing",
        "creative": "Write a short story about a robot learning to paint",
        "analytical": "Analyze the economic impact of renewable energy adoption",
        "factual": "What are the main causes of climate change?",
        "synthesis": "Synthesize information about blockchain technology and its applications"
    }


@pytest.fixture
def environment_config():
    """Provide environment configuration for testing."""
    return {
        "ollama_enabled": os.getenv("OLLAMA_ENABLED", "true").lower() == "true",
        "openai_enabled": bool(os.getenv("OPENAI_API_KEY")),
        "anthropic_enabled": bool(os.getenv("ANTHROPIC_API_KEY")),
        "vector_db_enabled": os.getenv("USE_VECTOR_DB", "true").lower() == "true",
        "model_policy": os.getenv("MODEL_POLICY", "cheap_first"),
        "test_timeout": TEST_TIMEOUT,
        "performance_threshold": PERFORMANCE_THRESHOLD
    }


@pytest.fixture
def mock_external_services():
    """Mock external services that are not LLM-related."""
    with patch("services.gateway.main.time.sleep") as mock_sleep:
        mock_sleep.return_value = None
        yield {"sleep": mock_sleep}


@pytest.fixture
def performance_monitor():
    """Monitor performance during tests."""
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.durations = []
        
        def start(self):
            self.start_time = asyncio.get_event_loop().time()
        
        def stop(self):
            if self.start_time:
                duration = asyncio.get_event_loop().time() - self.start_time
                self.durations.append(duration)
                return duration
            return 0.0
        
        def get_average_duration(self):
            return sum(self.durations) / len(self.durations) if self.durations else 0.0
        
        def get_max_duration(self):
            return max(self.durations) if self.durations else 0.0
    
    return PerformanceMonitor()


# Test utilities
def assert_response_structure(response, expected_fields: list[str]):
    """Assert response has expected structure."""
    assert response.status_code == 200
    data = response.json()

    for field in expected_fields:
        assert field in data, f"Missing field: {field}"


def assert_error_response(response, status_code: int):
    """Assert error response structure."""
    assert response.status_code == status_code


def assert_performance(actual_time: float, expected_max: float):
    """Assert performance meets expectations."""
    assert (
        actual_time <= expected_max
    ), f"Performance test failed: {actual_time:.3f}s > {expected_max:.3f}s"


def assert_llm_response_quality(data: Dict[str, Any]):
    """Assert LLM response has good quality indicators."""
    # Check basic structure
    assert "message" in data, "Response missing message field"
    assert "query" in data, "Response missing query field"
    assert "processing_time_ms" in data, "Response missing processing time"
    
    # Check response quality
    if "results" in data:
        assert isinstance(data["results"], list), "Results should be a list"
    
    if "total_results" in data:
        assert isinstance(data["total_results"], int), "Total results should be an integer"
    
    # Check timing is reasonable
    processing_time = data.get("processing_time_ms", 0)
    assert processing_time > 0, "Processing time should be positive"
    assert processing_time < PERFORMANCE_THRESHOLD * 1000, f"Processing time too high: {processing_time}ms"


def assert_health_response(data: Dict[str, Any]):
    """Assert health response has correct structure."""
    assert "status" in data, "Health response missing status"
    assert data["status"] in ["ok", "degraded", "error"], f"Invalid status: {data['status']}"
    assert "timestamp" in data, "Health response missing timestamp"
    assert "overall_healthy" in data, "Health response missing overall_healthy"


def assert_cors_headers(response):
    """Assert CORS headers are present."""
    assert "Access-Control-Allow-Origin" in response.headers, "Missing CORS origin header"
    assert "Access-Control-Allow-Methods" in response.headers, "Missing CORS methods header"
    assert "Access-Control-Allow-Headers" in response.headers, "Missing CORS headers"


def assert_vector_db_response(data: Dict[str, Any]):
    """Assert vector DB response has correct structure."""
    assert "message" in data, "Vector DB response missing message"
    assert "query" in data, "Vector DB response missing query"
    if "limit" in data:
        assert isinstance(data["limit"], int), "Limit should be an integer"
    if "filters" in data:
        assert isinstance(data["filters"], dict), "Filters should be a dictionary"


def assert_analytics_response(data: Dict[str, Any]):
    """Assert analytics response has correct structure."""
    required_fields = ["metrics", "timestamp", "platform_status", "data_sources"]
    for field in required_fields:
        assert field in data, f"Analytics response missing field: {field}"
    
    assert isinstance(data["metrics"], dict), "Metrics should be a dictionary"
    assert isinstance(data["data_sources"], dict), "Data sources should be a dictionary"


def assert_graph_response(data: Dict[str, Any]):
    """Assert knowledge graph response has correct structure."""
    required_fields = ["topic", "depth", "nodes", "edges", "total_nodes", "total_edges"]
    for field in required_fields:
        assert field in data, f"Graph response missing field: {field}"
    
    assert isinstance(data["nodes"], list), "Nodes should be a list"
    assert isinstance(data["edges"], list), "Edges should be a list"
    assert data["total_nodes"] == len(data["nodes"]), "Total nodes count mismatch"
    assert data["total_edges"] == len(data["edges"]), "Total edges count mismatch"


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "api: mark test as an API test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "llm: mark test as LLM integration test")
    config.addinivalue_line("markers", "performance: mark test as performance test")
    config.addinivalue_line("markers", "health: mark test as health check test")
    config.addinivalue_line("markers", "cors: mark test as CORS test")
    config.addinivalue_line("markers", "vector: mark test as vector DB test")
    config.addinivalue_line("markers", "analytics: mark test as analytics test")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add markers based on test class names
        if "TestHealthEndpoints" in str(item.cls):
            item.add_marker(pytest.mark.health)
        elif "TestPerformance" in str(item.cls):
            item.add_marker(pytest.mark.performance)
        elif "TestLLMRouting" in str(item.cls) or "TestRealLLMIntegration" in str(item.cls):
            item.add_marker(pytest.mark.llm)
        elif "TestCORS" in str(item.cls):
            item.add_marker(pytest.mark.cors)
        elif "TestVectorDBIntegration" in str(item.cls):
            item.add_marker(pytest.mark.vector)
        elif "TestAnalyticsEndpoints" in str(item.cls):
            item.add_marker(pytest.mark.analytics)
        
        # Add slow marker for performance tests
        if "performance" in item.name.lower() or "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)


# Export test utilities and fixtures
__all__ = [
    "client",
    "async_client", 
    "event_loop",
    "test_data",
    "llm_test_queries",
    "environment_config",
    "mock_external_services",
    "performance_monitor",
    "assert_response_structure",
    "assert_error_response",
    "assert_performance",
    "assert_llm_response_quality",
    "assert_health_response",
    "assert_cors_headers",
    "assert_vector_db_response",
    "assert_analytics_response",
    "assert_graph_response",
    "PERFORMANCE_THRESHOLD",
    "TEST_TIMEOUT"
]
