"""
Unit test configuration and fixtures for SarvanOM backend.

This module provides fixtures and utilities specifically for unit testing,
with mocks for external dependencies to ensure isolated testing.
"""

import pytest
import asyncio
import os
import sys
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import test dependencies
from datetime import datetime, timezone, timedelta
import jwt
import secrets


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing."""
    client = Mock()
    client.generate = AsyncMock()
    client.generate_text = AsyncMock()
    client.generate.return_value = Mock(
        content="This is a test response from the LLM.",
        usage=Mock(total_tokens=150)
    )
    client.generate_text.return_value = "This is a test response from the LLM."
    return client


@pytest.fixture
def mock_cache_manager():
    """Mock cache manager for testing."""
    cache = Mock()
    cache.get = AsyncMock()
    cache.set = AsyncMock()
    cache.delete = AsyncMock()
    cache.clear = AsyncMock()
    cache.get_stats = AsyncMock(return_value={"hits": 10, "misses": 5})
    return cache


@pytest.fixture
def mock_database_connection():
    """Mock database connection for testing."""
    connection = Mock()
    connection.execute = AsyncMock()
    connection.fetch_one = AsyncMock()
    connection.fetch_all = AsyncMock()
    connection.execute_many = AsyncMock()
    connection.transaction = AsyncMock()
    connection.close = AsyncMock()
    connection.health_check = AsyncMock(return_value={"status": "healthy"})
    connection.get_metrics = AsyncMock(return_value={"total_queries": 100, "avg_response_time": 0.05})
    return connection


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing."""
    store = Mock()
    store.search = AsyncMock()
    store.add_documents = AsyncMock()
    store.delete_documents = AsyncMock()
    store.get_collection_stats = AsyncMock(return_value={"total_documents": 1000})
    return store


@pytest.fixture
def mock_auth_manager():
    """Mock authentication manager for testing."""
    auth_manager = Mock()
    auth_manager.authenticate_user = AsyncMock()
    auth_manager.validate_token = AsyncMock()
    auth_manager.create_session = AsyncMock()
    auth_manager.invalidate_session = AsyncMock()
    return auth_manager


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": "user_123",
        "username": "testuser",
        "email": "test@example.com",
        "role": "user",
        "permissions": ["read", "write"],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }


@pytest.fixture
def sample_agent_data():
    """Sample agent data for testing."""
    return {
        "id": "agent_123",
        "name": "Test Agent",
        "type": "retrieval",
        "status": "active",
        "config": {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 1000
        },
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }


@pytest.fixture
def sample_query_data():
    """Sample query data for testing."""
    return {
        "id": "query_456",
        "user_id": "user_123",
        "query_text": "What is Python programming?",
        "status": "completed",
        "result": "Python is a high-level programming language...",
        "created_at": datetime.now(timezone.utc),
        "completed_at": datetime.now(timezone.utc)
    }


@pytest.fixture
def sample_search_results():
    """Sample search results for testing."""
    return [
        {
            "id": "doc1",
            "content": "This is the first document about Python programming.",
            "metadata": {"source": "python_guide.pdf", "page": 1},
            "score": 0.95,
            "distance": 0.05
        },
        {
            "id": "doc2",
            "content": "Machine learning algorithms and their applications.",
            "metadata": {"source": "ml_tutorial.pdf", "page": 5},
            "score": 0.87,
            "distance": 0.13
        },
        {
            "id": "doc3",
            "content": "Data structures and algorithms in Python.",
            "metadata": {"source": "ds_algo.pdf", "page": 3},
            "score": 0.76,
            "distance": 0.24
        }
    ]


@pytest.fixture
def sample_llm_response():
    """Sample LLM response for testing."""
    return """
    Python is a high-level programming language that emphasizes code readability.
    
    According to the Python documentation【python.org†L1-L5】, Python was created by Guido van Rossum and first released in 1991.
    
    The language features include:
    - Dynamic typing【python_guide.pdf†L10-L15】
    - Automatic memory management
    - Comprehensive standard library【stdlib_reference.pdf†L20-L25】
    
    Machine learning applications【ml_tutorial.pdf†L30-L35】 have become increasingly popular in Python.
    """


@pytest.fixture
def mock_jwt_manager():
    """Mock JWT manager for testing."""
    jwt_manager = Mock()
    jwt_manager.create_access_token = Mock(return_value="mock_access_token")
    jwt_manager.create_refresh_token = Mock(return_value="mock_refresh_token")
    jwt_manager.validate_token = Mock(return_value={"sub": "user_123", "role": "user"})
    jwt_manager.blacklisted_tokens = set()
    return jwt_manager


@pytest.fixture
def mock_metrics_service():
    """Mock metrics service for testing."""
    metrics = Mock()
    metrics.record_request = Mock()
    metrics.record_latency = Mock()
    metrics.record_error = Mock()
    metrics.record_vector_store_query = Mock()
    metrics.record_llm_call = Mock()
    metrics.get_stats = Mock(return_value={"total_requests": 1000, "avg_latency": 0.5})
    return metrics


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    logger = Mock()
    logger.info = Mock()
    logger.error = Mock()
    logger.warning = Mock()
    logger.debug = Mock()
    return logger


@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        "database": {
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "username": "test_user",
            "password": "test_password"
        },
        "cache": {
            "type": "memory",
            "ttl": 3600
        },
        "llm": {
            "default_model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 1000
        },
        "auth": {
            "jwt_secret": "test_secret_key",
            "jwt_algorithm": "HS256",
            "access_token_expire_minutes": 30,
            "refresh_token_expire_days": 7
        }
    }


@pytest.fixture
def mock_environment():
    """Mock environment variables for testing."""
    env_vars = {
        "DATABASE_URL": "postgresql://test:test@localhost:5432/test_db",
        "REDIS_URL": "redis://localhost:6379/0",
        "OPENAI_API_KEY": "test_openai_key",
        "ANTHROPIC_API_KEY": "test_anthropic_key",
        "JWT_SECRET_KEY": "test_jwt_secret",
        "MEILI_MASTER_KEY": "test_meili_key"
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def mock_external_apis():
    """Mock external API calls."""
    with patch("httpx.AsyncClient.get") as mock_get, \
         patch("httpx.AsyncClient.post") as mock_post:
        
        # Mock web search results
        mock_get.return_value = Mock(
            status_code=200,
            json=AsyncMock(return_value={
                "results": [
                    {"title": "Test Result 1", "url": "https://example1.com", "snippet": "Test snippet 1"},
                    {"title": "Test Result 2", "url": "https://example2.com", "snippet": "Test snippet 2"}
                ]
            })
        )
        
        # Mock API responses
        mock_post.return_value = Mock(
            status_code=200,
            json=AsyncMock(return_value={"success": True, "data": "test_response"})
        )
        
        yield {"get": mock_get, "post": mock_post}


@pytest.fixture
def mock_file_operations():
    """Mock file operations for testing."""
    with patch("builtins.open", create=True) as mock_open, \
         patch("os.path.exists") as mock_exists, \
         patch("os.makedirs") as mock_makedirs:
        
        mock_open.return_value.__enter__.return_value.read.return_value = "test file content"
        mock_open.return_value.__enter__.return_value.write = Mock()
        mock_exists.return_value = True
        mock_makedirs.return_value = None
        
        yield {
            "open": mock_open,
            "exists": mock_exists,
            "makedirs": mock_makedirs
        }


@pytest.fixture
def mock_time_operations():
    """Mock time operations for testing."""
    with patch("time.time") as mock_time, \
         patch("datetime.datetime") as mock_datetime:
        
        mock_time.return_value = 1640995200.0  # Fixed timestamp
        mock_datetime.now.return_value = datetime(2022, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.fromtimestamp.return_value = datetime(2022, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        yield {
            "time": mock_time,
            "datetime": mock_datetime
        }


@pytest.fixture
def mock_async_operations():
    """Mock async operations for testing."""
    with patch("asyncio.sleep") as mock_sleep, \
         patch("asyncio.gather") as mock_gather:
        
        mock_sleep.return_value = None
        mock_gather.return_value = ["result1", "result2", "result3"]
        
        yield {
            "sleep": mock_sleep,
            "gather": mock_gather
        }


@pytest.fixture
def sample_test_data():
    """Comprehensive test data for various scenarios."""
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
def mock_error_scenarios():
    """Mock various error scenarios for testing."""
    return {
        "network_error": ConnectionError("Network connection failed"),
        "timeout_error": asyncio.TimeoutError("Operation timed out"),
        "validation_error": ValueError("Invalid input data"),
        "authentication_error": jwt.InvalidTokenError("Invalid token"),
        "database_error": Exception("Database connection failed"),
        "llm_error": Exception("LLM service unavailable"),
        "cache_error": Exception("Cache service error"),
        "vector_store_error": Exception("Vector store error")
    }


# Utility functions for testing
def create_mock_response(status_code: int = 200, data: Any = None, headers: Dict = None):
    """Create a mock HTTP response."""
    response = Mock()
    response.status_code = status_code
    response.headers = headers or {}
    response.json = AsyncMock(return_value=data or {})
    response.text = str(data or "")
    return response


def create_mock_request(method: str = "GET", url: str = "/test", headers: Dict = None, data: Any = None):
    """Create a mock HTTP request."""
    request = Mock()
    request.method = method
    request.url = url
    request.headers = headers or {}
    request.json = AsyncMock(return_value=data or {})
    return request


def assert_dict_contains(actual: Dict, expected: Dict):
    """Assert that actual dict contains all expected key-value pairs."""
    for key, value in expected.items():
        assert key in actual, f"Key '{key}' not found in actual dict"
        assert actual[key] == value, f"Value for key '{key}' does not match"


def assert_list_contains(actual: List, expected_items: List):
    """Assert that actual list contains all expected items."""
    for item in expected_items:
        assert item in actual, f"Item '{item}' not found in actual list"


def create_test_token(user_id: str = "user_123", role: str = "user", expires_in: int = 3600):
    """Create a test JWT token."""
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc).timestamp() + expires_in,
        "iat": datetime.now(timezone.utc).timestamp()
    }
    return jwt.encode(payload, "test_secret", algorithm="HS256")
