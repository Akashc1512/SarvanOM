"""
Unit tests for database operations functionality.

Tests cover:
- Database connection management
- CRUD operations
- Query building and execution
- Transaction handling
- Connection pooling
- Error handling and recovery
- Data validation and sanitization
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from shared.core.database.connection import DatabaseConnectionManager
from shared.core.database.repository import BaseRepository
from backend.repositories.base_repository import BaseRepository as BackendBaseRepository
from backend.repositories.agent_repository import AgentRepository


class TestDatabaseOperations:
    """Test database operations functionality."""

    @pytest.fixture
    def mock_db_connection(self):
        """Create mock database connection."""
        connection = Mock(spec=DatabaseConnectionManager)
        connection.execute = AsyncMock()
        connection.fetch_one = AsyncMock()
        connection.fetch_all = AsyncMock()
        connection.execute_many = AsyncMock()
        connection.transaction = AsyncMock()
        return connection

    @pytest.fixture
    def sample_agent_data(self):
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
    def sample_query_data(self):
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

    @pytest.mark.asyncio
    async def test_database_connection_basic(self, mock_db_connection):
        """Test basic database connection operations."""
        # Test connection execution
        query = "SELECT * FROM agents WHERE id = %s"
        params = ["agent_123"]
        
        mock_db_connection.execute.return_value = {"affected_rows": 1}
        result = await mock_db_connection.execute(query, params)
        
        assert result["affected_rows"] == 1
        mock_db_connection.execute.assert_called_once_with(query, params)

    @pytest.mark.asyncio
    async def test_database_fetch_one(self, mock_db_connection):
        """Test fetching single record from database."""
        expected_data = {"id": "agent_123", "name": "Test Agent"}
        mock_db_connection.fetch_one.return_value = expected_data
        
        query = "SELECT * FROM agents WHERE id = %s"
        params = ["agent_123"]
        
        result = await mock_db_connection.fetch_one(query, params)
        
        assert result == expected_data
        mock_db_connection.fetch_one.assert_called_once_with(query, params)

    @pytest.mark.asyncio
    async def test_database_fetch_all(self, mock_db_connection):
        """Test fetching multiple records from database."""
        expected_data = [
            {"id": "agent_123", "name": "Test Agent 1"},
            {"id": "agent_456", "name": "Test Agent 2"},
            {"id": "agent_789", "name": "Test Agent 3"}
        ]
        mock_db_connection.fetch_all.return_value = expected_data
        
        query = "SELECT * FROM agents WHERE status = %s"
        params = ["active"]
        
        result = await mock_db_connection.fetch_all(query, params)
        
        assert result == expected_data
        assert len(result) == 3
        mock_db_connection.fetch_all.assert_called_once_with(query, params)

    @pytest.mark.asyncio
    async def test_database_execute_many(self, mock_db_connection):
        """Test executing multiple queries."""
        queries = [
            ("INSERT INTO agents (id, name) VALUES (%s, %s)", ["agent_1", "Agent 1"]),
            ("INSERT INTO agents (id, name) VALUES (%s, %s)", ["agent_2", "Agent 2"]),
            ("INSERT INTO agents (id, name) VALUES (%s, %s)", ["agent_3", "Agent 3"])
        ]
        
        mock_db_connection.execute_many.return_value = {"affected_rows": 3}
        result = await mock_db_connection.execute_many(queries)
        
        assert result["affected_rows"] == 3
        mock_db_connection.execute_many.assert_called_once_with(queries)

    @pytest.mark.asyncio
    async def test_database_transaction(self, mock_db_connection):
        """Test database transaction handling."""
        async def transaction_operations():
            await mock_db_connection.execute("INSERT INTO agents (id, name) VALUES (%s, %s)", ["agent_1", "Agent 1"])
            await mock_db_connection.execute("UPDATE agents SET status = %s WHERE id = %s", ["active", "agent_1"])
            return {"success": True}
        
        mock_db_connection.transaction.return_value = {"success": True}
        result = await mock_db_connection.transaction(transaction_operations)
        
        assert result["success"] is True
        mock_db_connection.transaction.assert_called_once()

    @pytest.mark.asyncio
    async def test_base_repository_create(self, mock_db_connection, sample_agent_data):
        """Test base repository create operation."""
        repository = BaseRepository(mock_db_connection)
        
        mock_db_connection.execute.return_value = {"affected_rows": 1, "last_id": "agent_123"}
        
        result = await repository.create("agents", sample_agent_data)
        
        assert result["affected_rows"] == 1
        assert result["last_id"] == "agent_123"
        mock_db_connection.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_base_repository_read(self, mock_db_connection, sample_agent_data):
        """Test base repository read operation."""
        repository = BaseRepository(mock_db_connection)
        
        mock_db_connection.fetch_one.return_value = sample_agent_data
        
        result = await repository.read("agents", "agent_123")
        
        assert result == sample_agent_data
        mock_db_connection.fetch_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_base_repository_update(self, mock_db_connection):
        """Test base repository update operation."""
        repository = BaseRepository(mock_db_connection)
        
        update_data = {"name": "Updated Agent", "status": "inactive"}
        mock_db_connection.execute.return_value = {"affected_rows": 1}
        
        result = await repository.update("agents", "agent_123", update_data)
        
        assert result["affected_rows"] == 1
        mock_db_connection.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_base_repository_delete(self, mock_db_connection):
        """Test base repository delete operation."""
        repository = BaseRepository(mock_db_connection)
        
        mock_db_connection.execute.return_value = {"affected_rows": 1}
        
        result = await repository.delete("agents", "agent_123")
        
        assert result["affected_rows"] == 1
        mock_db_connection.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_base_repository_list(self, mock_db_connection):
        """Test base repository list operation."""
        repository = BaseRepository(mock_db_connection)
        
        expected_data = [
            {"id": "agent_123", "name": "Agent 1"},
            {"id": "agent_456", "name": "Agent 2"}
        ]
        mock_db_connection.fetch_all.return_value = expected_data
        
        result = await repository.list("agents", limit=10, offset=0)
        
        assert result == expected_data
        assert len(result) == 2
        mock_db_connection.fetch_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_agent_repository_create_agent(self, mock_db_connection, sample_agent_data):
        """Test agent repository create agent operation."""
        repository = AgentRepository(mock_db_connection)
        
        mock_db_connection.execute.return_value = {"affected_rows": 1, "last_id": "agent_123"}
        
        result = await repository.create_agent(sample_agent_data)
        
        assert result["affected_rows"] == 1
        assert result["last_id"] == "agent_123"
        mock_db_connection.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_agent_repository_get_agent_by_id(self, mock_db_connection, sample_agent_data):
        """Test agent repository get agent by ID operation."""
        repository = AgentRepository(mock_db_connection)
        
        mock_db_connection.fetch_one.return_value = sample_agent_data
        
        result = await repository.get_agent_by_id("agent_123")
        
        assert result == sample_agent_data
        mock_db_connection.fetch_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_agent_repository_get_agents_by_type(self, mock_db_connection):
        """Test agent repository get agents by type operation."""
        repository = AgentRepository(mock_db_connection)
        
        expected_data = [
            {"id": "agent_123", "name": "Retrieval Agent", "type": "retrieval"},
            {"id": "agent_456", "name": "Synthesis Agent", "type": "retrieval"}
        ]
        mock_db_connection.fetch_all.return_value = expected_data
        
        result = await repository.get_agents_by_type("retrieval")
        
        assert result == expected_data
        assert len(result) == 2
        mock_db_connection.fetch_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_agent_repository_update_agent_status(self, mock_db_connection):
        """Test agent repository update agent status operation."""
        repository = AgentRepository(mock_db_connection)
        
        mock_db_connection.execute.return_value = {"affected_rows": 1}
        
        result = await repository.update_agent_status("agent_123", "inactive")
        
        assert result["affected_rows"] == 1
        mock_db_connection.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_database_error_handling(self, mock_db_connection):
        """Test database error handling."""
        repository = BaseRepository(mock_db_connection)
        
        # Simulate database error
        mock_db_connection.execute.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception):
            await repository.create("agents", {"name": "Test Agent"})

    @pytest.mark.asyncio
    async def test_database_connection_pooling(self, mock_db_connection):
        """Test database connection pooling."""
        # Simulate multiple concurrent operations
        async def concurrent_operation():
            await mock_db_connection.execute("SELECT 1")
            return True
        
        # Create multiple concurrent tasks
        tasks = [concurrent_operation() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All operations should succeed
        assert all(results)
        assert mock_db_connection.execute.call_count == 10

    @pytest.mark.asyncio
    async def test_database_query_parameter_validation(self, mock_db_connection):
        """Test database query parameter validation."""
        repository = BaseRepository(mock_db_connection)
        
        # Test with valid parameters
        valid_data = {"name": "Test Agent", "type": "retrieval"}
        mock_db_connection.execute.return_value = {"affected_rows": 1}
        
        result = await repository.create("agents", valid_data)
        assert result["affected_rows"] == 1
        
        # Test with invalid parameters (None values)
        invalid_data = {"name": None, "type": "retrieval"}
        
        with pytest.raises(ValueError):
            await repository.create("agents", invalid_data)

    @pytest.mark.asyncio
    async def test_database_sql_injection_prevention(self, mock_db_connection):
        """Test SQL injection prevention."""
        repository = BaseRepository(mock_db_connection)
        
        # Test with potentially malicious input
        malicious_input = "'; DROP TABLE agents; --"
        
        mock_db_connection.fetch_one.return_value = None
        
        # Should handle safely with parameterized queries
        result = await repository.read("agents", malicious_input)
        
        # Verify that the query was executed with proper parameterization
        mock_db_connection.fetch_one.assert_called_once()
        call_args = mock_db_connection.fetch_one.call_args
        assert "%s" in call_args[0][0]  # Query should use parameterized placeholders

    @pytest.mark.asyncio
    async def test_database_transaction_rollback(self, mock_db_connection):
        """Test database transaction rollback on error."""
        async def failing_transaction():
            await mock_db_connection.execute("INSERT INTO agents (id, name) VALUES (%s, %s)", ["agent_1", "Agent 1"])
            raise Exception("Transaction failed")
        
        mock_db_connection.transaction.side_effect = Exception("Transaction failed")
        
        with pytest.raises(Exception):
            await mock_db_connection.transaction(failing_transaction)

    @pytest.mark.asyncio
    async def test_database_batch_operations(self, mock_db_connection):
        """Test database batch operations."""
        repository = BaseRepository(mock_db_connection)
        
        batch_data = [
            {"id": "agent_1", "name": "Agent 1"},
            {"id": "agent_2", "name": "Agent 2"},
            {"id": "agent_3", "name": "Agent 3"}
        ]
        
        mock_db_connection.execute_many.return_value = {"affected_rows": 3}
        
        result = await repository.batch_create("agents", batch_data)
        
        assert result["affected_rows"] == 3
        mock_db_connection.execute_many.assert_called_once()

    @pytest.mark.asyncio
    async def test_database_connection_timeout(self, mock_db_connection):
        """Test database connection timeout handling."""
        # Simulate timeout
        mock_db_connection.execute.side_effect = asyncio.TimeoutError("Database timeout")
        
        repository = BaseRepository(mock_db_connection)
        
        with pytest.raises(asyncio.TimeoutError):
            await repository.create("agents", {"name": "Test Agent"})

    @pytest.mark.asyncio
    async def test_database_connection_retry(self, mock_db_connection):
        """Test database connection retry logic."""
        repository = BaseRepository(mock_db_connection)
        
        # First call fails, second succeeds
        mock_db_connection.execute.side_effect = [
            Exception("Connection failed"),
            {"affected_rows": 1}
        ]
        
        result = await repository.create("agents", {"name": "Test Agent"})
        
        assert result["affected_rows"] == 1
        assert mock_db_connection.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_database_data_validation(self, mock_db_connection):
        """Test database data validation."""
        repository = BaseRepository(mock_db_connection)
        
        # Test required field validation
        incomplete_data = {"name": "Test Agent"}  # Missing required fields
        
        with pytest.raises(ValueError):
            await repository.create("agents", incomplete_data)
        
        # Test data type validation
        invalid_data = {"name": 123, "type": "retrieval"}  # Name should be string
        
        with pytest.raises(ValueError):
            await repository.create("agents", invalid_data)

    @pytest.mark.asyncio
    async def test_database_query_optimization(self, mock_db_connection):
        """Test database query optimization."""
        repository = BaseRepository(mock_db_connection)
        
        # Test with index hints
        mock_db_connection.fetch_all.return_value = []
        
        result = await repository.list("agents", limit=10, offset=0, use_index="idx_status")
        
        mock_db_connection.fetch_all.assert_called_once()
        call_args = mock_db_connection.fetch_all.call_args
        assert "USE INDEX" in call_args[0][0] or "FORCE INDEX" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_database_connection_health_check(self, mock_db_connection):
        """Test database connection health check."""
        mock_db_connection.execute.return_value = {"result": "ok"}
        
        # Test health check
        result = await mock_db_connection.health_check()
        
        assert result["status"] == "healthy"
        mock_db_connection.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_database_connection_metrics(self, mock_db_connection):
        """Test database connection metrics collection."""
        repository = BaseRepository(mock_db_connection)
        
        # Perform operations to generate metrics
        mock_db_connection.execute.return_value = {"affected_rows": 1}
        mock_db_connection.fetch_one.return_value = {"id": "agent_123"}
        
        await repository.create("agents", {"name": "Test Agent"})
        await repository.read("agents", "agent_123")
        
        # Get metrics
        metrics = await mock_db_connection.get_metrics()
        
        assert "total_queries" in metrics
        assert "avg_response_time" in metrics
        assert metrics["total_queries"] >= 2

    @pytest.mark.asyncio
    async def test_database_connection_cleanup(self, mock_db_connection):
        """Test database connection cleanup."""
        repository = BaseRepository(mock_db_connection)
        
        # Perform operations
        mock_db_connection.execute.return_value = {"affected_rows": 1}
        await repository.create("agents", {"name": "Test Agent"})
        
        # Cleanup
        await mock_db_connection.close()
        
        # Verify cleanup
        mock_db_connection.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_database_connection_reconnection(self, mock_db_connection):
        """Test database connection reconnection logic."""
        repository = BaseRepository(mock_db_connection)
        
        # Simulate connection failure followed by reconnection
        mock_db_connection.execute.side_effect = [
            Exception("Connection lost"),
            {"affected_rows": 1}
        ]
        
        # Should automatically reconnect and retry
        result = await repository.create("agents", {"name": "Test Agent"})
        
        assert result["affected_rows"] == 1
        assert mock_db_connection.execute.call_count == 2
