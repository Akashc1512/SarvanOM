"""
Pytest Configuration and Fixtures

This module contains shared fixtures and configuration for the test suite.
"""

import pytest
import asyncio
from typing import Dict, Any, AsyncGenerator
from unittest.mock import Mock, AsyncMock

from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import application components
from ..main import app
from ..api.dependencies import (
    get_cache_service,
    get_metrics_service,
    get_query_orchestrator,
    get_query_repository,
    get_user_repository,
    get_agent_repository,
)
from ..repositories.query_repository import QueryRepositoryImpl
from ..repositories.user_repository import UserRepositoryImpl
from ..repositories.agent_repository import AgentRepositoryImpl
from ..services.core.cache_service import CacheService
from ..services.core.metrics_service import MetricsService
from ..services.query.query_orchestrator import QueryOrchestrator
from ..models.domain.query import Query, QueryContext, QueryType, QueryStatus
from ..models.domain.user import User, UserRole, UserStatus
from ..models.domain.agent import Agent, AgentType, AgentStatus


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_cache_service():
    """Create a test cache service."""
    cache_service = CacheService()
    await cache_service.initialize()
    yield cache_service
    await cache_service.clear()


@pytest.fixture
async def test_metrics_service():
    """Create a test metrics service."""
    metrics_service = MetricsService()
    yield metrics_service


@pytest.fixture
async def test_query_repository():
    """Create a test query repository."""
    repository = QueryRepositoryImpl(storage_type="memory")
    yield repository
    # Cleanup
    if hasattr(repository, "_memory_store") and hasattr(
        repository._memory_store, "clear"
    ):
        repository._memory_store.clear()


@pytest.fixture
async def test_user_repository():
    """Create a test user repository."""
    repository = UserRepositoryImpl(storage_type="memory")
    yield repository
    # Cleanup
    if hasattr(repository, "_memory_store") and hasattr(
        repository._memory_store, "clear"
    ):
        repository._memory_store.clear()


@pytest.fixture
async def test_agent_repository():
    """Create a test agent repository."""
    repository = AgentRepositoryImpl(storage_type="memory")
    yield repository
    # Cleanup
    if hasattr(repository, "_memory_store") and hasattr(
        repository._memory_store, "clear"
    ):
        repository._memory_store.clear()


@pytest.fixture
async def test_query_orchestrator(
    test_query_repository, test_cache_service, test_metrics_service
):
    """Create a test query orchestrator with mocked dependencies."""

    # Mock query processor and validator
    mock_processor = AsyncMock()
    mock_validator = AsyncMock()

    # Mock successful processing
    mock_processor.process_basic_query.return_value = {
        "answer": "Test answer",
        "confidence": 0.95,
        "processing_time": 0.1,
        "metadata": {},
    }

    mock_processor.process_comprehensive_query.return_value = {
        "answer": "Comprehensive test answer",
        "confidence": 0.98,
        "processing_time": 0.2,
        "sources": ["source1", "source2"],
        "alternatives": [],
        "quality_metrics": {},
        "metadata": {},
    }

    orchestrator = QueryOrchestrator(
        query_processor=mock_processor,
        query_validator=mock_validator,
        cache_service=test_cache_service,
        metrics_service=test_metrics_service,
        query_repository=test_query_repository,
    )

    yield orchestrator


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI application."""
    # Override dependencies with test instances
    app.dependency_overrides = {}

    # Use test client
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def async_test_client():
    """Create an async test client for the FastAPI application."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_query():
    """Create a sample query for testing."""
    return Query(
        id="test-query-123",
        text="What is the capital of France?",
        context=QueryContext(
            user_id="test-user",
            session_id="test-session",
            max_tokens=100,
            confidence_threshold=0.8,
            metadata={"test": True},
        ),
        query_type=QueryType.BASIC,
        status=QueryStatus.PENDING,
    )


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(
        id="test-user-123",
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        display_name="Test User",
        metadata={"test": True},
    )


@pytest.fixture
def sample_agent():
    """Create a sample agent for testing."""
    return Agent(
        id="test-agent-123",
        name="test-agent",
        agent_type=AgentType.RETRIEVAL,
        status=AgentStatus.ACTIVE,
        config={"model": "test-model", "max_tokens": 100, "temperature": 0.7},
        description="Test agent for unit tests",
        version="1.0.0",
        metadata={"test": True},
    )


@pytest.fixture
def sample_query_request():
    """Create a sample query request for testing."""
    return {
        "query": "What is the capital of France?",
        "session_id": "test-session",
        "max_tokens": 100,
        "confidence_threshold": 0.8,
        "cache_enabled": True,
    }


@pytest.fixture
def sample_user_request():
    """Create a sample user request for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "test_password",
        "display_name": "Test User",
    }


@pytest.fixture
def sample_agent_request():
    """Create a sample agent request for testing."""
    return {
        "name": "test-agent",
        "agent_type": "retrieval",
        "config": {"model": "test-model", "max_tokens": 100, "temperature": 0.7},
        "description": "Test agent for API testing",
    }


@pytest.fixture
def mock_dependencies():
    """Mock all application dependencies for isolated testing."""

    # Create mock instances
    mock_cache = AsyncMock(spec=CacheService)
    mock_metrics = AsyncMock(spec=MetricsService)
    mock_query_repo = AsyncMock(spec=QueryRepositoryImpl)
    mock_user_repo = AsyncMock(spec=UserRepositoryImpl)
    mock_agent_repo = AsyncMock(spec=AgentRepositoryImpl)
    mock_orchestrator = AsyncMock(spec=QueryOrchestrator)

    # Setup mock responses
    mock_cache.get.return_value = None
    mock_cache.set.return_value = True
    mock_cache.clear.return_value = True
    mock_cache.get_stats.return_value = {"hits": 0, "misses": 0}

    mock_metrics.track_query_processing.return_value = None
    mock_metrics.track_query_error.return_value = None
    mock_metrics.get_metrics_summary.return_value = {"total_queries": 0}

    # Override dependencies
    app.dependency_overrides[get_cache_service] = lambda: mock_cache
    app.dependency_overrides[get_metrics_service] = lambda: mock_metrics
    app.dependency_overrides[get_query_repository] = lambda: mock_query_repo
    app.dependency_overrides[get_user_repository] = lambda: mock_user_repo
    app.dependency_overrides[get_agent_repository] = lambda: mock_agent_repo
    app.dependency_overrides[get_query_orchestrator] = lambda: mock_orchestrator

    yield {
        "cache": mock_cache,
        "metrics": mock_metrics,
        "query_repo": mock_query_repo,
        "user_repo": mock_user_repo,
        "agent_repo": mock_agent_repo,
        "orchestrator": mock_orchestrator,
    }

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def test_database_config():
    """Create test database configuration."""
    return {
        "host": "localhost",
        "port": 5432,
        "database": "sarvanom_test",
        "username": "test_user",
        "password": "test_password",
        "ssl": False,
        "pool_size": 5,
        "max_overflow": 10,
    }


@pytest.fixture
async def clean_repositories(
    test_query_repository, test_user_repository, test_agent_repository
):
    """Ensure all repositories are clean before and after tests."""

    # Clean before test
    repositories = [test_query_repository, test_user_repository, test_agent_repository]
    for repo in repositories:
        if hasattr(repo, "_memory_store") and hasattr(repo._memory_store, "clear"):
            repo._memory_store.clear()

    yield repositories

    # Clean after test
    for repo in repositories:
        if hasattr(repo, "_memory_store") and hasattr(repo._memory_store, "clear"):
            repo._memory_store.clear()


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "api: mark test as an API test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "repository: mark test as a repository test")
    config.addinivalue_line("markers", "service: mark test as a service test")


# Custom pytest markers for test categorization
pytest_plugins = []
