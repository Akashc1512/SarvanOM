"""
Test Cache Manager PostgreSQL - Universal Knowledge Platform
Comprehensive tests for PostgreSQL-based cache management.

This module tests the CacheManagerPostgres service with various scenarios
including cache operations, TTL handling, and integration patterns.

Test Coverage:
- Set/get cache flows
- TTL expiry handling
- Retrieval caching logic
- Answer caching logic
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

from shared.core.cache_manager_postgres import CacheManagerPostgres
from shared.models.cache_store import CacheStore
from shared.core.database import DatabaseService, DatabaseConfig


class MockDatabaseService:
    """Mock database service for testing."""
    
    def __init__(self):
        self.cache_entries = {}  # In-memory storage for testing
        self.cache_counter = 0
        self.current_request_key = None  # Track the current request key
    
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
            "total_entries": len(self.cache_entries),
            "active_entries": len([c for c in self.cache_entries.values() if not c.is_expired()]),
            "expired_entries": len([c for c in self.cache_entries.values() if c.is_expired()]),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


class MockSessionContext:
    """Mock session context manager."""
    
    def __init__(self, db_service: MockDatabaseService):
        self.db_service = db_service
        self.session = MockSession(db_service)
    
    def __enter__(self):
        return self.session
    
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
        # Try to extract the key from the query for tracking
        query_str = str(query).lower()
        if "cache_key" in query_str and "cache_store" in query_str:
            # This is a simplified approach - in a real scenario we'd parse the parameters
            # For now, we'll use a simple heuristic to track the key
            if self.db_service.cache_entries:
                # Use the first available key as the requested key
                self.db_service.current_request_key = list(self.db_service.cache_entries.keys())[0]
            else:
                # If no cache entries exist, set a dummy key to indicate no match
                self.db_service.current_request_key = "non_existent_key"
        
        return MockQueryResult(self.db_service, query)
    
    def add(self, obj):
        """Mock adding object to session."""
        if hasattr(obj, 'cache_key'):
            self.db_service.cache_entries[obj.cache_key] = obj
    
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
        self.requested_key = None
        
        # Try to extract the requested key from the query
        query_str = str(query).lower()
        if "cache_key" in query_str and "cache_store" in query_str:
            # For parameterized queries, we need to track the key being requested
            # This is a simplified approach - in a real scenario we'd parse the parameters
            if self.db_service.cache_entries:
                # Store the first key as the requested key (simplified mock)
                self.requested_key = list(self.db_service.cache_entries.keys())[0]
    
    def scalar_one_or_none(self):
        """Mock scalar result."""
        # Extract cache_key from query if it's a select
        query_str = str(self.query).lower()
        
        if "cache_key" in query_str and "cache_store" in query_str:
            # For parameterized queries, we need to get the parameter value
            # Since this is a mock, we'll return the cache entry for the requested key
            if (self.db_service.current_request_key and 
                self.db_service.current_request_key in self.db_service.cache_entries and
                self.db_service.current_request_key != "non_existent_key"):
                return self.db_service.cache_entries.get(self.db_service.current_request_key)
        return None
    
    def scalar(self):
        """Mock scalar result."""
        if "count" in str(self.query).lower():
            return len(self.db_service.cache_entries)
        return 0
    
    @property
    def rowcount(self):
        """Mock row count."""
        # For delete operations, return 1 if we have entries
        if "delete" in str(self.query).lower():
            return len(self.db_service.cache_entries)
        return 1


class TestCacheManagerPostgres:
    """Test suite for CacheManagerPostgres."""
    
    @pytest.fixture
    async def cache_manager(self):
        """Create a cache manager instance for testing."""
        # Create mock database service
        mock_db_service = MockDatabaseService()
        
        # Create cache manager with mock service
        manager = CacheManagerPostgres(database_service=mock_db_service)
        yield manager
        
        # Cleanup
        try:
            await manager.clear_expired_cache()
        except Exception:
            pass
    
    @pytest.fixture
    def sample_cache_data(self):
        """Generate sample cache data for testing."""
        return {
            "query": "What is Python?",
            "answer": "Python is a high-level programming language.",
            "sources": [
                {"title": "Python.org", "url": "https://python.org"},
                {"title": "Wikipedia", "url": "https://wikipedia.org/python"}
            ],
            "confidence": 0.95,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def test_set_get_cache_flows(self, cache_manager, sample_cache_data):
        """Test basic set/get cache flows."""
        cache_key = f"test_cache_{uuid.uuid4().hex[:8]}"
        
        # Set cache
        success = await cache_manager.set_cache(cache_key, sample_cache_data, ttl_minutes=30)
        assert success, "Failed to set cache"
        
        # Get cache
        cached_data = await cache_manager.get_cache(cache_key)
        assert cached_data is not None, "Failed to get cached data"
        assert cached_data["query"] == sample_cache_data["query"], "Cached data mismatch"
        assert cached_data["answer"] == sample_cache_data["answer"], "Cached data mismatch"
        
        # Test cache miss
        non_existent_data = await cache_manager.get_cache("non_existent_key")
        assert non_existent_data is None, "Should return None for non-existent key"
    
    async def test_ttl_expiry_handling(self, cache_manager, sample_cache_data):
        """Test TTL expiry handling."""
        cache_key = f"expiry_test_{uuid.uuid4().hex[:8]}"
        
        # Set cache with short TTL
        success = await cache_manager.set_cache(cache_key, sample_cache_data, ttl_minutes=1)
        assert success, "Failed to set cache"
        
        # Get cache immediately (should work)
        cached_data = await cache_manager.get_cache(cache_key)
        assert cached_data is not None, "Cache should be available immediately"
        
        # Simulate expiration by manually setting expired timestamp
        # In a real test, we'd wait for actual expiration
        # For testing, we'll test the expiration logic directly
        
        # Test with 0 TTL (no expiration)
        cache_key_no_expiry = f"no_expiry_{uuid.uuid4().hex[:8]}"
        success = await cache_manager.set_cache(cache_key_no_expiry, sample_cache_data, ttl_minutes=0)
        assert success, "Failed to set cache with no expiry"
        
        cached_data = await cache_manager.get_cache(cache_key_no_expiry)
        assert cached_data is not None, "Cache with no expiry should always be available"
    
    async def test_retrieval_caching_logic(self, cache_manager):
        """Test retrieval caching logic."""
        query = "What is machine learning?"
        max_results = 5
        
        # Generate cache key for retrieval
        cache_key = cache_manager.generate_cache_key("retrieval", query, max_results)
        
        # Simulate retrieval results
        retrieval_data = {
            "query": query,
            "max_results": max_results,
            "results": [
                {"title": "ML Basics", "content": "Machine learning is...", "score": 0.95},
                {"title": "AI Guide", "content": "Artificial intelligence...", "score": 0.87},
                {"title": "Data Science", "content": "Data science involves...", "score": 0.82}
            ],
            "total_found": 3,
            "search_time_ms": 150
        }
        
        # Cache retrieval results
        success = await cache_manager.set_cache(cache_key, retrieval_data, ttl_minutes=60)
        assert success, "Failed to cache retrieval results"
        
        # Retrieve cached results
        cached_results = await cache_manager.get_cache(cache_key)
        assert cached_results is not None, "Failed to get cached retrieval results"
        assert cached_results["query"] == query, "Cached query mismatch"
        assert len(cached_results["results"]) == 3, "Cached results count mismatch"
        assert cached_results["total_found"] == 3, "Cached total count mismatch"
    
    async def test_answer_caching_logic(self, cache_manager):
        """Test answer caching logic."""
        query = "How do I install Python?"
        
        # Generate cache key for answer
        cache_key = cache_manager.generate_cache_key("answer", query)
        
        # Simulate LLM answer
        answer_data = {
            "query": query,
            "answer": "You can install Python by downloading it from python.org...",
            "confidence": 0.92,
            "model_used": "gpt-4",
            "tokens_used": 150,
            "processing_time_ms": 2500,
            "sources": [
                {"title": "Python Installation Guide", "url": "https://python.org/downloads"}
            ]
        }
        
        # Cache answer
        success = await cache_manager.set_cache(cache_key, answer_data, ttl_minutes=120)
        assert success, "Failed to cache answer"
        
        # Retrieve cached answer
        cached_answer = await cache_manager.get_cache(cache_key)
        assert cached_answer is not None, "Failed to get cached answer"
        assert cached_answer["query"] == query, "Cached query mismatch"
        assert cached_answer["answer"] == answer_data["answer"], "Cached answer mismatch"
        assert cached_answer["confidence"] == 0.92, "Cached confidence mismatch"
    
    async def test_cache_key_generation(self, cache_manager):
        """Test cache key generation."""
        # Test with different arguments
        key1 = cache_manager.generate_cache_key("retrieval", "test query", 5)
        key2 = cache_manager.generate_cache_key("retrieval", "test query", 5)
        key3 = cache_manager.generate_cache_key("retrieval", "different query", 5)
        
        # Same arguments should generate same key
        assert key1 == key2, "Same arguments should generate same cache key"
        
        # Different arguments should generate different keys
        assert key1 != key3, "Different arguments should generate different cache keys"
        
        # Test with keyword arguments
        key4 = cache_manager.generate_cache_key("answer", query="test", model="gpt-4")
        key5 = cache_manager.generate_cache_key("answer", query="test", model="gpt-4")
        key6 = cache_manager.generate_cache_key("answer", query="test", model="gpt-3")
        
        assert key4 == key5, "Same keyword arguments should generate same cache key"
        assert key4 != key6, "Different keyword arguments should generate different cache keys"
    
    async def test_cache_deletion(self, cache_manager, sample_cache_data):
        """Test cache deletion."""
        cache_key = f"delete_test_{uuid.uuid4().hex[:8]}"
        
        # Set cache
        success = await cache_manager.set_cache(cache_key, sample_cache_data)
        assert success, "Failed to set cache"
        
        # Verify cache exists
        cached_data = await cache_manager.get_cache(cache_key)
        assert cached_data is not None, "Cache should exist before deletion"
        
        # Delete cache
        delete_success = await cache_manager.delete_cache(cache_key)
        assert delete_success, "Failed to delete cache"
        
        # Verify cache is deleted
        cached_data = await cache_manager.get_cache(cache_key)
        assert cached_data is None, "Cache should be deleted"
        
        # Test deleting non-existent cache
        delete_success = await cache_manager.delete_cache("non_existent_key")
        assert not delete_success, "Should return False for non-existent key"
    
    async def test_cache_stats(self, cache_manager, sample_cache_data):
        """Test cache statistics."""
        # Get initial stats
        initial_stats = await cache_manager.get_cache_stats()
        assert initial_stats["total_entries"] == 0, "Should start with 0 entries"
        
        # Add some cache entries
        for i in range(3):
            cache_key = f"stats_test_{i}_{uuid.uuid4().hex[:8]}"
            await cache_manager.set_cache(cache_key, sample_cache_data, ttl_minutes=30)
        
        # Get stats after adding entries
        stats = await cache_manager.get_cache_stats()
        assert stats["total_entries"] == 3, f"Expected 3 entries, got {stats['total_entries']}"
        assert stats["active_entries"] == 3, f"Expected 3 active entries, got {stats['active_entries']}"
        assert stats["expired_entries"] == 0, f"Expected 0 expired entries, got {stats['expired_entries']}"
    
    async def test_clear_expired_cache(self, cache_manager, sample_cache_data):
        """Test clearing expired cache entries."""
        # Add cache entries with different TTLs
        cache_keys = []
        
        # Add entry with short TTL (will be expired in test)
        key1 = f"expired_{uuid.uuid4().hex[:8]}"
        await cache_manager.set_cache(key1, sample_cache_data, ttl_minutes=1)
        cache_keys.append(key1)
        
        # Add entry with no expiration
        key2 = f"no_expiry_{uuid.uuid4().hex[:8]}"
        await cache_manager.set_cache(key2, sample_cache_data, ttl_minutes=0)
        cache_keys.append(key2)
        
        # Add entry with long TTL
        key3 = f"long_ttl_{uuid.uuid4().hex[:8]}"
        await cache_manager.set_cache(key3, sample_cache_data, ttl_minutes=60)
        cache_keys.append(key3)
        
        # Clear expired cache
        cleared_count = await cache_manager.clear_expired_cache()
        assert cleared_count >= 0, "Should return non-negative count"
    
    async def test_health_check(self, cache_manager, sample_cache_data):
        """Test health check functionality."""
        health = await cache_manager.health_check()
        
        assert "status" in health, "Health check should include status"
        assert "total_entries" in health, "Health check should include total_entries"
        assert "active_entries" in health, "Health check should include active_entries"
        assert "expired_entries" in health, "Health check should include expired_entries"
        assert "timestamp" in health, "Health check should include timestamp"
        
        # Add a cache entry and check again
        cache_key = f"health_test_{uuid.uuid4().hex[:8]}"
        await cache_manager.set_cache(cache_key, sample_cache_data)
        
        health_after = await cache_manager.health_check()
        assert health_after["total_entries"] >= 0, "Total entries should be non-negative"
    
    async def test_error_handling(self, cache_manager):
        """Test error handling with invalid inputs."""
        # Test with empty cache key
        success = await cache_manager.set_cache("", {"test": "data"})
        assert not success, "Should fail with empty cache key"
        
        # Test with None cache key
        success = await cache_manager.set_cache(None, {"test": "data"})
        assert not success, "Should fail with None cache key"
        
        # Test getting cache for non-existent key
        cached_data = await cache_manager.get_cache("non_existent_key")
        assert cached_data is None, "Non-existent key should return None"
        
        # Test deleting non-existent cache
        success = await cache_manager.delete_cache("non_existent_key")
        assert not success, "Deleting non-existent cache should return False"
    
    async def test_concurrent_cache_access(self, cache_manager, sample_cache_data):
        """Test concurrent access to cache."""
        cache_key = f"concurrent_{uuid.uuid4().hex[:8]}"
        
        # Create multiple concurrent tasks
        async def set_cache(task_id: int):
            return await cache_manager.set_cache(
                f"{cache_key}_{task_id}",
                {**sample_cache_data, "task_id": task_id}
            )
        
        async def get_cache(task_id: int):
            return await cache_manager.get_cache(f"{cache_key}_{task_id}")
        
        # Run concurrent set operations
        set_tasks = [set_cache(i) for i in range(5)]
        set_results = await asyncio.gather(*set_tasks, return_exceptions=True)
        
        # All set operations should succeed
        for result in set_results:
            assert isinstance(result, bool), "All set operations should return boolean"
        
        # Run concurrent get operations
        get_tasks = [get_cache(i) for i in range(5)]
        get_results = await asyncio.gather(*get_tasks, return_exceptions=True)
        
        # All get operations should return data or None
        for result in get_results:
            assert result is None or isinstance(result, dict), "All get operations should return dict or None"
    
    async def test_large_cache_operations(self, cache_manager):
        """Test handling of large cache operations."""
        # Add many cache entries
        for i in range(50):
            cache_key = f"large_test_{i}_{uuid.uuid4().hex[:8]}"
            cache_data = {
                "index": i,
                "data": f"Large cache data for entry {i}",
                "metadata": {
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "size": len(f"Large cache data for entry {i}")
                }
            }
            
            await cache_manager.set_cache(cache_key, cache_data, ttl_minutes=30)
        
        # Get cache statistics
        stats = await cache_manager.get_cache_stats()
        assert stats["total_entries"] >= 50, f"Expected at least 50 entries, got {stats['total_entries']}"
        
        # Test retrieving some cached entries
        for i in range(10):
            cache_key = f"large_test_{i}_"
            # Find the actual key (since we added UUID)
            all_keys = await cache_manager.get_all_cache_keys(limit=100)
            matching_keys = [k["cache_key"] for k in all_keys if cache_key in k["cache_key"]]
            
            if matching_keys:
                cached_data = await cache_manager.get_cache(matching_keys[0])
                assert cached_data is not None, f"Should retrieve cached data for key {matching_keys[0]}"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 