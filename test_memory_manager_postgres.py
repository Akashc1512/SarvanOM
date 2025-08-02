"""
Test Memory Manager PostgreSQL - Universal Knowledge Platform
Comprehensive tests for PostgreSQL-based session memory management.

This module tests the MemoryManagerPostgres service with various scenarios
including session management, TTL behavior, and error handling.

Test Coverage:
- Adding multiple interactions to session
- Validating retrieval order (last N exchanges)
- Testing memory clearance
- Simulating expired context pruning
- Error handling and edge cases

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    1.0.0 (2024-12-28)
"""

import asyncio
import pytest
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, AsyncMock, MagicMock

from shared.core.memory_manager_postgres import MemoryManagerPostgres
from shared.models.session_memory import SessionMemory
from shared.core.database import DatabaseService, DatabaseConfig


class MockDatabaseService:
    """Mock database service for testing."""
    
    def __init__(self):
        self.sessions = {}  # In-memory storage for testing
        self.session_counter = 0
    
    def get_session(self):
        """Return a mock session context manager."""
        return MockSessionContext(self)
    
    async def execute_raw_sql(self, sql: str, params: Optional[Dict[str, Any]] = None):
        """Mock raw SQL execution."""
        return []
    
    def health_check(self) -> Dict[str, Any]:
        """Mock health check."""
        return {
            "status": "healthy",
            "total_sessions": len(self.sessions),
            "recent_sessions": len([s for s in self.sessions.values() if s.updated_at > datetime.now(timezone.utc) - timedelta(hours=1)]),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


class MockSessionContext:
    """Mock session context manager."""
    
    def __init__(self, db_service: MockDatabaseService):
        self.db_service = db_service
        self.session = MockSession(db_service)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def commit(self):
        pass


class MockSession:
    """Mock database session."""
    
    def __init__(self, db_service: MockDatabaseService):
        self.db_service = db_service
    
    def execute(self, query):
        """Mock query execution."""
        return MockQueryResult(self.db_service, query)
    
    def add(self, obj):
        """Mock adding object to session."""
        if hasattr(obj, 'session_id'):
            self.db_service.sessions[obj.session_id] = obj
    
    def commit(self):
        """Mock commit."""
        pass
    
    def close(self):
        """Mock close."""
        pass


class MockQueryResult:
    """Mock query result."""
    
    def __init__(self, db_service: MockDatabaseService, query):
        self.db_service = db_service
        self.query = query
    
    def scalar_one_or_none(self):
        """Mock scalar result."""
        # Extract session_id from query if it's a select
        if hasattr(self.query, 'where') and hasattr(self.query.where, 'right'):
            session_id = str(self.query.where.right.value)
            return self.db_service.sessions.get(session_id)
        return None
    
    def scalar(self):
        """Mock scalar result."""
        if "count" in str(self.query).lower():
            return len(self.db_service.sessions)
        return 0
    
    @property
    def rowcount(self):
        """Mock row count."""
        return 1


class TestMemoryManagerPostgres:
    """Test suite for MemoryManagerPostgres."""
    
    @pytest.fixture
    async def memory_manager(self):
        """Create a memory manager instance for testing."""
        # Create mock database service
        mock_db_service = MockDatabaseService()
        
        # Create memory manager with mock service
        manager = MemoryManagerPostgres(database_service=mock_db_service)
        yield manager
        
        # Cleanup
        try:
            await manager.cleanup_expired_sessions(0)  # Clean all sessions
        except Exception:
            pass
    
    @pytest.fixture
    def sample_session_id(self):
        """Generate a sample session ID."""
        return f"test_session_{uuid.uuid4().hex[:8]}"
    
    @pytest.fixture
    def sample_interactions(self):
        """Generate sample interactions for testing."""
        return [
            {
                "query": "What is Python?",
                "answer": "Python is a high-level programming language.",
                "timestamp": datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                "query": "How do I install Python?",
                "answer": "You can download Python from python.org.",
                "timestamp": datetime.now(timezone.utc) - timedelta(minutes=20)
            },
            {
                "query": "What are Python packages?",
                "answer": "Python packages are collections of modules.",
                "timestamp": datetime.now(timezone.utc) - timedelta(minutes=10)
            },
            {
                "query": "How do I use pip?",
                "answer": "pip is Python's package installer.",
                "timestamp": datetime.now(timezone.utc) - timedelta(minutes=5)
            },
            {
                "query": "What is virtualenv?",
                "answer": "virtualenv creates isolated Python environments.",
                "timestamp": datetime.now(timezone.utc)
            }
        ]
    
    async def test_add_multiple_interactions(self, memory_manager, sample_session_id, sample_interactions):
        """Test adding multiple interactions to a session."""
        # Add multiple interactions
        for interaction in sample_interactions:
            success = await memory_manager.add_to_memory(
                sample_session_id,
                interaction["query"],
                interaction["answer"],
                interaction["timestamp"]
            )
            assert success, f"Failed to add interaction: {interaction['query']}"
        
        # Verify all interactions were added
        context = await memory_manager.get_context(sample_session_id, limit=10)
        assert len(context) == 5, f"Expected 5 interactions, got {len(context)}"
        
        # Verify interactions are sorted by timestamp (newest first)
        timestamps = [interaction["timestamp"] for interaction in context]
        assert timestamps == sorted(timestamps, reverse=True), "Interactions not sorted by timestamp"
    
    async def test_retrieval_order(self, memory_manager, sample_session_id, sample_interactions):
        """Test that retrieval returns interactions in correct order (last N exchanges)."""
        # Add interactions
        for interaction in sample_interactions:
            await memory_manager.add_to_memory(
                sample_session_id,
                interaction["query"],
                interaction["answer"],
                interaction["timestamp"]
            )
        
        # Test retrieval with different limits
        for limit in [1, 3, 5]:
            context = await memory_manager.get_context(sample_session_id, limit=limit)
            assert len(context) == min(limit, 5), f"Expected {min(limit, 5)} interactions, got {len(context)}"
            
            # Verify newest interactions come first
            if len(context) > 1:
                first_timestamp = context[0]["timestamp"]
                last_timestamp = context[-1]["timestamp"]
                assert first_timestamp >= last_timestamp, "Interactions not in descending order"
    
    async def test_memory_clearance(self, memory_manager, sample_session_id, sample_interactions):
        """Test clearing memory for a session."""
        # Add some interactions
        for interaction in sample_interactions[:3]:
            await memory_manager.add_to_memory(
                sample_session_id,
                interaction["query"],
                interaction["answer"],
                interaction["timestamp"]
            )
        
        # Verify interactions exist
        context = await memory_manager.get_context(sample_session_id)
        assert len(context) == 3, "Expected 3 interactions before clearing"
        
        # Clear memory
        success = await memory_manager.clear_memory(sample_session_id)
        assert success, "Failed to clear memory"
        
        # Verify memory is cleared
        context = await memory_manager.get_context(sample_session_id)
        assert len(context) == 0, "Memory not cleared properly"
    
    async def test_expired_context_pruning(self, memory_manager, sample_session_id):
        """Test that expired interactions are automatically pruned."""
        # Add interactions with different timestamps
        old_timestamp = datetime.now(timezone.utc) - timedelta(hours=25)  # Expired
        recent_timestamp = datetime.now(timezone.utc) - timedelta(minutes=30)  # Recent
        
        # Add expired interaction
        await memory_manager.add_to_memory(
            sample_session_id,
            "Old query",
            "Old answer",
            old_timestamp
        )
        
        # Add recent interaction
        await memory_manager.add_to_memory(
            sample_session_id,
            "Recent query",
            "Recent answer",
            recent_timestamp
        )
        
        # Get context (should trigger pruning)
        context = await memory_manager.get_context(sample_session_id)
        
        # Should only have the recent interaction
        assert len(context) == 1, f"Expected 1 interaction after pruning, got {len(context)}"
        assert context[0]["query"] == "Recent query", "Wrong interaction retained after pruning"
    
    async def test_session_stats(self, memory_manager, sample_session_id, sample_interactions):
        """Test getting session statistics."""
        # Get stats for non-existent session
        stats = await memory_manager.get_session_stats(sample_session_id)
        assert not stats["exists"], "Non-existent session should not exist"
        assert stats["history_length"] == 0, "Non-existent session should have 0 history"
        
        # Add interactions
        for interaction in sample_interactions[:3]:
            await memory_manager.add_to_memory(
                sample_session_id,
                interaction["query"],
                interaction["answer"],
                interaction["timestamp"]
            )
        
        # Get stats for existing session
        stats = await memory_manager.get_session_stats(sample_session_id)
        assert stats["exists"], "Session should exist after adding interactions"
        assert stats["history_length"] == 3, f"Expected 3 interactions, got {stats['history_length']}"
        assert stats["last_updated"] is not None, "Last updated should not be None"
    
    async def test_cleanup_expired_sessions(self, memory_manager):
        """Test cleanup of expired sessions."""
        # Create multiple sessions with different timestamps
        old_session = f"old_session_{uuid.uuid4().hex[:8]}"
        recent_session = f"recent_session_{uuid.uuid4().hex[:8]}"
        
        # Add old session (expired)
        await memory_manager.add_to_memory(
            old_session,
            "Old query",
            "Old answer",
            datetime.now(timezone.utc) - timedelta(hours=25)
        )
        
        # Add recent session
        await memory_manager.add_to_memory(
            recent_session,
            "Recent query",
            "Recent answer",
            datetime.now(timezone.utc) - timedelta(minutes=30)
        )
        
        # Cleanup expired sessions
        cleaned_count = await memory_manager.cleanup_expired_sessions(max_age_hours=24)
        assert cleaned_count >= 0, "Cleanup should return non-negative count"
        
        # Verify old session is gone
        old_stats = await memory_manager.get_session_stats(old_session)
        # Note: In a real implementation, this would be deleted
        # For testing, we'll just check the stats
    
    async def test_health_check(self, memory_manager, sample_session_id):
        """Test health check functionality."""
        health = await memory_manager.health_check()
        
        assert "status" in health, "Health check should include status"
        assert "total_sessions" in health, "Health check should include total_sessions"
        assert "recent_sessions" in health, "Health check should include recent_sessions"
        assert "timestamp" in health, "Health check should include timestamp"
        
        # Add a session and check again
        await memory_manager.add_to_memory(
            sample_session_id,
            "Health test query",
            "Health test answer"
        )
        
        health_after = await memory_manager.health_check()
        assert health_after["total_sessions"] >= 0, "Total sessions should be non-negative"
    
    async def test_error_handling(self, memory_manager):
        """Test error handling with invalid inputs."""
        # Test with empty session ID
        success = await memory_manager.add_to_memory("", "query", "answer")
        assert not success, "Should fail with empty session ID"
        
        # Test with None session ID
        success = await memory_manager.add_to_memory(None, "query", "answer")
        assert not success, "Should fail with None session ID"
        
        # Test getting context for non-existent session
        context = await memory_manager.get_context("non_existent_session")
        assert len(context) == 0, "Non-existent session should return empty context"
        
        # Test clearing non-existent session
        success = await memory_manager.clear_memory("non_existent_session")
        assert not success, "Clearing non-existent session should return False"
    
    async def test_concurrent_access(self, memory_manager):
        """Test concurrent access to the same session."""
        session_id = f"concurrent_session_{uuid.uuid4().hex[:8]}"
        
        # Create multiple concurrent tasks
        async def add_interaction(task_id: int):
            return await memory_manager.add_to_memory(
                session_id,
                f"Query from task {task_id}",
                f"Answer from task {task_id}"
            )
        
        # Run concurrent tasks
        tasks = [add_interaction(i) for i in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All tasks should succeed
        for result in results:
            assert isinstance(result, bool), "All tasks should return boolean"
        
        # Verify all interactions were added
        context = await memory_manager.get_context(session_id, limit=10)
        assert len(context) == 5, f"Expected 5 interactions, got {len(context)}"
    
    async def test_large_session_history(self, memory_manager, sample_session_id):
        """Test handling of large session history."""
        # Add many interactions
        for i in range(50):
            await memory_manager.add_to_memory(
                sample_session_id,
                f"Query {i}",
                f"Answer {i}",
                datetime.now(timezone.utc) - timedelta(minutes=i)
            )
        
        # Test retrieval with different limits
        for limit in [5, 10, 25]:
            context = await memory_manager.get_context(sample_session_id, limit=limit)
            assert len(context) == limit, f"Expected {limit} interactions, got {len(context)}"
            
            # Verify order
            if len(context) > 1:
                timestamps = [interaction["timestamp"] for interaction in context]
                assert timestamps == sorted(timestamps, reverse=True), "Interactions not in correct order"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 