"""
Repository Layer Tests

Tests for the repository pattern implementation including
Query, User, and Agent repositories.
"""

import pytest
from datetime import datetime, timedelta
from typing import List

from ..models.domain.query import Query, QueryStatus, QueryType
from ..models.domain.user import User, UserRole, UserStatus
from ..models.domain.agent import Agent, AgentType, AgentStatus
from ..repositories.query_repository import QueryRepositoryImpl
from ..repositories.user_repository import UserRepositoryImpl
from ..repositories.agent_repository import AgentRepositoryImpl


@pytest.mark.repository
class TestQueryRepository:
    """Test Query Repository functionality."""

    @pytest.mark.asyncio
    async def test_create_query(self, test_query_repository, sample_query):
        """Test creating a new query."""
        # Create query
        created_query = await test_query_repository.create_query(sample_query)

        # Assertions
        assert created_query.id == sample_query.id
        assert created_query.text == sample_query.text
        assert created_query.status == QueryStatus.PENDING

        # Verify it can be retrieved
        retrieved_query = await test_query_repository.get_query_by_id(sample_query.id)
        assert retrieved_query is not None
        assert retrieved_query.id == sample_query.id

    @pytest.mark.asyncio
    async def test_update_query_status(self, test_query_repository, sample_query):
        """Test updating query status."""
        # Create query
        await test_query_repository.create_query(sample_query)

        # Update status to processing
        updated_query = await test_query_repository.update_query_status(
            sample_query.id, QueryStatus.PROCESSING
        )

        assert updated_query.status == QueryStatus.PROCESSING

        # Update status to completed with result
        result_data = {"answer": "Paris", "confidence": 0.95}
        completed_query = await test_query_repository.update_query_status(
            sample_query.id, QueryStatus.COMPLETED, result_data
        )

        assert completed_query.status == QueryStatus.COMPLETED
        assert completed_query.result == result_data

    @pytest.mark.asyncio
    async def test_get_queries_by_user(self, test_query_repository, sample_query):
        """Test retrieving queries by user."""
        user_id = "test-user-123"

        # Create multiple queries for the same user
        for i in range(3):
            query = Query(
                id=f"query-{i}",
                text=f"Test query {i}",
                context=sample_query.context,
                query_type=QueryType.BASIC,
            )
            await test_query_repository.create_query(query)

        # Get queries by user
        user_queries = await test_query_repository.get_queries_by_user(user_id)

        assert len(user_queries) == 3
        assert all(q.context.user_id == user_id for q in user_queries)

    @pytest.mark.asyncio
    async def test_search_queries(self, test_query_repository, sample_query):
        """Test searching queries by text."""
        # Create queries with different content
        queries = [
            Query(
                id="q1",
                text="What is Python?",
                context=sample_query.context,
                query_type=QueryType.BASIC,
            ),
            Query(
                id="q2",
                text="How to use FastAPI?",
                context=sample_query.context,
                query_type=QueryType.BASIC,
            ),
            Query(
                id="q3",
                text="Python programming tips",
                context=sample_query.context,
                query_type=QueryType.BASIC,
            ),
        ]

        for query in queries:
            await test_query_repository.create_query(query)

        # Search for Python-related queries
        results = await test_query_repository.search_queries("Python")

        assert len(results) == 2  # q1 and q3 contain "Python"
        assert all("python" in r.text.lower() for r in results)

    @pytest.mark.asyncio
    async def test_get_query_statistics(self, test_query_repository, sample_query):
        """Test getting query statistics."""
        # Create queries with different statuses
        queries = [
            Query(
                id="q1",
                text="Query 1",
                context=sample_query.context,
                query_type=QueryType.BASIC,
            ),
            Query(
                id="q2",
                text="Query 2",
                context=sample_query.context,
                query_type=QueryType.COMPREHENSIVE,
            ),
        ]

        for query in queries:
            await test_query_repository.create_query(query)
            await test_query_repository.update_query_status(
                query.id, QueryStatus.COMPLETED
            )

        # Get statistics
        stats = await test_query_repository.get_query_statistics()

        assert stats["total_queries"] == 2
        assert stats["status_breakdown"][QueryStatus.COMPLETED.value] == 2
        assert stats["type_breakdown"][QueryType.BASIC.value] == 1
        assert stats["type_breakdown"][QueryType.COMPREHENSIVE.value] == 1


@pytest.mark.repository
class TestUserRepository:
    """Test User Repository functionality."""

    @pytest.mark.asyncio
    async def test_create_user(self, test_user_repository, sample_user):
        """Test creating a new user."""
        # Create user
        created_user = await test_user_repository.create_user(sample_user)

        # Assertions
        assert created_user.id == sample_user.id
        assert created_user.username == sample_user.username
        assert created_user.email == sample_user.email
        assert created_user.status == UserStatus.ACTIVE

        # Verify it can be retrieved
        retrieved_user = await test_user_repository.get_user_by_id(sample_user.id)
        assert retrieved_user is not None
        assert retrieved_user.username == sample_user.username

    @pytest.mark.asyncio
    async def test_duplicate_username_rejection(
        self, test_user_repository, sample_user
    ):
        """Test that duplicate usernames are rejected."""
        # Create first user
        await test_user_repository.create_user(sample_user)

        # Try to create user with same username
        duplicate_user = User(
            id="different-id",
            username=sample_user.username,  # Same username
            email="different@example.com",
            password_hash="different_hash",
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
        )

        with pytest.raises(ValueError, match="Username .* already exists"):
            await test_user_repository.create_user(duplicate_user)

    @pytest.mark.asyncio
    async def test_get_user_by_username(self, test_user_repository, sample_user):
        """Test retrieving user by username."""
        # Create user
        await test_user_repository.create_user(sample_user)

        # Retrieve by username
        retrieved_user = await test_user_repository.get_user_by_username(
            sample_user.username
        )

        assert retrieved_user is not None
        assert retrieved_user.id == sample_user.id
        assert retrieved_user.email == sample_user.email

    @pytest.mark.asyncio
    async def test_update_user_profile(self, test_user_repository, sample_user):
        """Test updating user profile."""
        # Create user
        await test_user_repository.create_user(sample_user)

        # Update profile
        updates = {"display_name": "Updated Name", "email": "updated@example.com"}

        updated_user = await test_user_repository.update_user_profile(
            sample_user.id, updates
        )

        assert updated_user.display_name == "Updated Name"
        assert updated_user.email == "updated@example.com"

    @pytest.mark.asyncio
    async def test_authenticate_user(self, test_user_repository, sample_user):
        """Test user authentication."""
        # Create user
        await test_user_repository.create_user(sample_user)

        # Test successful authentication
        authenticated_user = await test_user_repository.authenticate_user(
            sample_user.username, sample_user.password_hash
        )

        assert authenticated_user is not None
        assert authenticated_user.id == sample_user.id

        # Test failed authentication
        failed_auth = await test_user_repository.authenticate_user(
            sample_user.username, "wrong_password"
        )

        assert failed_auth is None

    @pytest.mark.asyncio
    async def test_get_users_by_role(self, test_user_repository):
        """Test retrieving users by role."""
        # Create users with different roles
        admin_user = User(
            id="admin-1",
            username="admin",
            email="admin@example.com",
            password_hash="hash",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
        )

        regular_user = User(
            id="user-1",
            username="user",
            email="user@example.com",
            password_hash="hash",
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
        )

        await test_user_repository.create_user(admin_user)
        await test_user_repository.create_user(regular_user)

        # Get admin users
        admin_users = await test_user_repository.get_users_by_role(UserRole.ADMIN)
        assert len(admin_users) == 1
        assert admin_users[0].role == UserRole.ADMIN

        # Get regular users
        regular_users = await test_user_repository.get_users_by_role(UserRole.USER)
        assert len(regular_users) == 1
        assert regular_users[0].role == UserRole.USER


@pytest.mark.repository
class TestAgentRepository:
    """Test Agent Repository functionality."""

    @pytest.mark.asyncio
    async def test_create_agent(self, test_agent_repository, sample_agent):
        """Test creating a new agent."""
        # Create agent
        created_agent = await test_agent_repository.create_agent(sample_agent)

        # Assertions
        assert created_agent.id == sample_agent.id
        assert created_agent.name == sample_agent.name
        assert created_agent.agent_type == sample_agent.agent_type
        assert created_agent.status == AgentStatus.ACTIVE

        # Verify it can be retrieved
        retrieved_agent = await test_agent_repository.get_agent_by_id(sample_agent.id)
        assert retrieved_agent is not None
        assert retrieved_agent.name == sample_agent.name

    @pytest.mark.asyncio
    async def test_duplicate_agent_name_rejection(
        self, test_agent_repository, sample_agent
    ):
        """Test that duplicate agent names are rejected."""
        # Create first agent
        await test_agent_repository.create_agent(sample_agent)

        # Try to create agent with same name
        duplicate_agent = Agent(
            id="different-id",
            name=sample_agent.name,  # Same name
            agent_type=AgentType.SYNTHESIS,
            status=AgentStatus.ACTIVE,
            config={"different": "config"},
        )

        with pytest.raises(ValueError, match="Agent name .* already exists"):
            await test_agent_repository.create_agent(duplicate_agent)

    @pytest.mark.asyncio
    async def test_update_agent_config(self, test_agent_repository, sample_agent):
        """Test updating agent configuration."""
        # Create agent
        await test_agent_repository.create_agent(sample_agent)

        # Update config
        new_config = {"temperature": 0.9, "max_tokens": 200, "new_setting": "value"}

        updated_agent = await test_agent_repository.update_agent_config(
            sample_agent.id, new_config
        )

        # Check that config is merged
        assert updated_agent.config["temperature"] == 0.9
        assert updated_agent.config["max_tokens"] == 200
        assert updated_agent.config["new_setting"] == "value"
        assert updated_agent.config["model"] == "test-model"  # Original value preserved

    @pytest.mark.asyncio
    async def test_get_agents_by_type(self, test_agent_repository):
        """Test retrieving agents by type."""
        # Create agents of different types
        retrieval_agent = Agent(
            id="ret-1",
            name="retrieval-agent",
            agent_type=AgentType.RETRIEVAL,
            status=AgentStatus.ACTIVE,
            config={},
        )

        synthesis_agent = Agent(
            id="syn-1",
            name="synthesis-agent",
            agent_type=AgentType.SYNTHESIS,
            status=AgentStatus.ACTIVE,
            config={},
        )

        await test_agent_repository.create_agent(retrieval_agent)
        await test_agent_repository.create_agent(synthesis_agent)

        # Get retrieval agents
        retrieval_agents = await test_agent_repository.get_agents_by_type(
            AgentType.RETRIEVAL
        )
        assert len(retrieval_agents) == 1
        assert retrieval_agents[0].agent_type == AgentType.RETRIEVAL

        # Get synthesis agents
        synthesis_agents = await test_agent_repository.get_agents_by_type(
            AgentType.SYNTHESIS
        )
        assert len(synthesis_agents) == 1
        assert synthesis_agents[0].agent_type == AgentType.SYNTHESIS

    @pytest.mark.asyncio
    async def test_update_agent_performance(self, test_agent_repository, sample_agent):
        """Test updating agent performance metrics."""
        # Create agent
        await test_agent_repository.create_agent(sample_agent)

        # Update performance data
        performance_data = {"accuracy": 0.95, "response_time": 0.2, "tokens_used": 150}

        updated_agent = await test_agent_repository.update_agent_performance(
            sample_agent.id, performance_data
        )

        # Check performance history
        performance_history = getattr(updated_agent, "performance_history", [])
        assert len(performance_history) == 1
        assert performance_history[0]["accuracy"] == 0.95
        assert "timestamp" in performance_history[0]

    @pytest.mark.asyncio
    async def test_get_active_agents(self, test_agent_repository):
        """Test retrieving only active agents."""
        # Create agents with different statuses
        active_agent = Agent(
            id="active-1",
            name="active-agent",
            agent_type=AgentType.RETRIEVAL,
            status=AgentStatus.ACTIVE,
            config={},
        )

        inactive_agent = Agent(
            id="inactive-1",
            name="inactive-agent",
            agent_type=AgentType.SYNTHESIS,
            status=AgentStatus.INACTIVE,
            config={},
        )

        await test_agent_repository.create_agent(active_agent)
        await test_agent_repository.create_agent(inactive_agent)

        # Get only active agents
        active_agents = await test_agent_repository.get_active_agents()

        assert len(active_agents) == 1
        assert active_agents[0].status == AgentStatus.ACTIVE
        assert active_agents[0].id == "active-1"


@pytest.mark.repository
@pytest.mark.integration
class TestRepositoryIntegration:
    """Test integration between different repositories."""

    @pytest.mark.asyncio
    async def test_cross_repository_operations(self, clean_repositories):
        """Test operations that span multiple repositories."""
        query_repo, user_repo, agent_repo = clean_repositories

        # Create a user
        user = User(
            id="integration-user",
            username="integration_user",
            email="integration@example.com",
            password_hash="hash",
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
        )
        created_user = await user_repo.create_user(user)

        # Create an agent
        agent = Agent(
            id="integration-agent",
            name="integration-agent",
            agent_type=AgentType.RETRIEVAL,
            status=AgentStatus.ACTIVE,
            config={"user_id": created_user.id},
        )
        created_agent = await agent_repo.create_agent(agent)

        # Create a query associated with the user
        query = Query(
            id="integration-query",
            text="Integration test query",
            context=QueryContext(
                user_id=created_user.id,
                session_id="integration-session",
                max_tokens=100,
                confidence_threshold=0.8,
                metadata={"agent_id": created_agent.id},
            ),
            query_type=QueryType.BASIC,
        )
        created_query = await query_repo.create_query(query)

        # Verify cross-references
        assert created_query.context.user_id == created_user.id
        assert created_query.context.metadata["agent_id"] == created_agent.id

        # Test cascading operations
        user_queries = await query_repo.get_queries_by_user(created_user.id)
        assert len(user_queries) == 1
        assert user_queries[0].id == created_query.id
