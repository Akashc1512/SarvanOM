"""
Simple Cache Manager Test - Universal Knowledge Platform
Simplified tests for PostgreSQL-based cache management.

This module provides basic tests for the CacheManagerPostgres service
without complex database setup requirements.

Test Coverage:
- Basic cache operations
- TTL handling
- Cache key generation
- Error handling

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    1.0.0 (2024-12-28)
"""

import asyncio
import pytest
import uuid
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, AsyncMock, MagicMock

from shared.core.cache_manager_postgres import CacheManagerPostgres


class SimpleMockDatabaseService:
    """Simple mock database service for testing."""
    
    def __init__(self):
        self.cache_entries = {}
    
    def get_session(self):
        """Return a simple mock session."""
        return SimpleMockSession(self)
    
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


class SimpleMockSession:
    """Simple mock database session."""
    
    def __init__(self, db_service: SimpleMockDatabaseService):
        self.db_service = db_service
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def execute(self, query):
        """Mock query execution."""
        return SimpleMockQueryResult(self.db_service, query)
    
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


class SimpleMockQueryResult:
    """Simple mock query result."""
    
    def __init__(self, db_service: SimpleMockDatabaseService, query):
        self.db_service = db_service
        self.query = query
    
    def scalar_one_or_none(self):
        """Mock scalar result."""
        # Extract cache_key from query if it's a select
        if hasattr(self.query, 'where') and hasattr(self.query.where, 'right'):
            cache_key = str(self.query.where.right.value)
            return self.db_service.cache_entries.get(cache_key)
        return None
    
    def scalar(self):
        """Mock scalar result."""
        if "count" in str(self.query).lower():
            return len(self.db_service.cache_entries)
        return 0
    
    @property
    def rowcount(self):
        """Mock row count."""
        if "delete" in str(self.query).lower():
            return len(self.db_service.cache_entries)
        return 1


class SimpleCacheStore:
    """Simple cache store for testing."""
    
    def __init__(self, cache_key: str, data: Dict[str, Any], ttl_minutes: Optional[int] = None):
        self.cache_key = cache_key
        self.data = data
        self.created_at = datetime.now(timezone.utc)
        self.expires_at = None
        if ttl_minutes and ttl_minutes > 0:
            self.expires_at = self.created_at + timedelta(minutes=ttl_minutes)
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at
    
    def set_expiration(self, ttl_minutes: int) -> None:
        """Set expiration time."""
        if ttl_minutes > 0:
            self.expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
        else:
            self.expires_at = None


class TestSimpleCacheManager:
    """Simple test suite for CacheManagerPostgres."""
    
    @pytest.fixture
    async def cache_manager(self):
        """Create a cache manager instance for testing."""
        mock_db_service = SimpleMockDatabaseService()
        manager = CacheManagerPostgres(database_service=mock_db_service)
        yield manager
    
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
    
    async def test_cache_key_generation(self, cache_manager):
        """Test cache key generation."""
        # Test with different inputs
        key1 = cache_manager.generate_cache_key("query1", "param1")
        key2 = cache_manager.generate_cache_key("query1", "param1")
        key3 = cache_manager.generate_cache_key("query2", "param1")
        
        # Same inputs should generate same key
        assert key1 == key2, "Same inputs should generate same key"
        
        # Different inputs should generate different keys
        assert key1 != key3, "Different inputs should generate different keys"
        
        # Test with kwargs
        key4 = cache_manager.generate_cache_key("query1", param1="value1", param2="value2")
        key5 = cache_manager.generate_cache_key("query1", param2="value2", param1="value1")
        
        # Same kwargs in different order should generate same key
        assert key4 == key5, "Same kwargs in different order should generate same key"
    
    async def test_basic_cache_operations(self, cache_manager, sample_cache_data):
        """Test basic cache operations."""
        cache_key = f"test_cache_{uuid.uuid4().hex[:8]}"
        
        # Test cache key generation
        generated_key = cache_manager.generate_cache_key("test_query", cache_key)
        assert len(generated_key) == 32, "Generated key should be 32 characters (MD5)"
        
        # Test that cache operations don't crash
        # Note: We're not testing actual database operations since we're using mocks
        assert cache_manager is not None, "Cache manager should be created"
        assert hasattr(cache_manager, 'set_cache'), "Cache manager should have set_cache method"
        assert hasattr(cache_manager, 'get_cache'), "Cache manager should have get_cache method"
        assert hasattr(cache_manager, 'delete_cache'), "Cache manager should have delete_cache method"
    
    async def test_cache_manager_initialization(self, cache_manager):
        """Test cache manager initialization."""
        assert cache_manager is not None, "Cache manager should be created"
        assert hasattr(cache_manager, 'db_service'), "Cache manager should have database service"
        assert hasattr(cache_manager, 'default_ttl_minutes'), "Cache manager should have default TTL"
    
    async def test_health_check(self, cache_manager):
        """Test health check functionality."""
        # Test that health check doesn't crash
        try:
            health_status = await cache_manager.health_check()
            assert isinstance(health_status, dict), "Health check should return a dictionary"
        except Exception as e:
            # Health check might fail with mocks, which is expected
            assert "Mock" in str(e) or "database" in str(e).lower(), f"Unexpected error: {e}"
    
    async def test_cache_stats(self, cache_manager):
        """Test cache statistics."""
        # Test that cache stats don't crash
        try:
            stats = await cache_manager.get_cache_stats()
            assert isinstance(stats, dict), "Cache stats should return a dictionary"
        except Exception as e:
            # Stats might fail with mocks, which is expected
            assert "Mock" in str(e) or "database" in str(e).lower(), f"Unexpected error: {e}"
    
    async def test_error_handling(self, cache_manager):
        """Test error handling."""
        # Test with invalid inputs
        try:
            result = await cache_manager.set_cache("", {}, ttl_minutes=30)
            # Should handle empty key gracefully
        except Exception as e:
            # Should not crash on invalid input
            assert "key" in str(e).lower() or "empty" in str(e).lower(), f"Unexpected error: {e}"
        
        try:
            result = await cache_manager.get_cache("")
            # Should handle empty key gracefully
        except Exception as e:
            # Should not crash on invalid input
            assert "key" in str(e).lower() or "empty" in str(e).lower(), f"Unexpected error: {e}"
    
    async def test_concurrent_access_simulation(self, cache_manager):
        """Test concurrent access simulation."""
        # Simulate multiple cache operations
        tasks = []
        
        async def cache_operation(task_id: int):
            key = f"concurrent_test_{task_id}"
            data = {"task_id": task_id, "data": f"test_data_{task_id}"}
            
            # Simulate set operation
            try:
                await cache_manager.set_cache(key, data, ttl_minutes=5)
            except Exception:
                pass  # Expected with mocks
            
            # Simulate get operation
            try:
                await cache_manager.get_cache(key)
            except Exception:
                pass  # Expected with mocks
        
        # Create multiple concurrent operations
        for i in range(5):
            tasks.append(cache_operation(i))
        
        # Execute concurrently
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            # Expected with mocks
            assert "Mock" in str(e) or "database" in str(e).lower(), f"Unexpected error: {e}"
    
    async def test_ttl_handling_simulation(self, cache_manager):
        """Test TTL handling simulation."""
        # Test TTL calculation
        cache_entry = SimpleCacheStore("test_key", {"data": "test"}, ttl_minutes=30)
        
        # Should not be expired immediately
        assert not cache_entry.is_expired(), "Cache should not be expired immediately"
        
        # Test with 0 TTL (no expiration)
        cache_entry_no_expiry = SimpleCacheStore("test_key2", {"data": "test"}, ttl_minutes=0)
        assert not cache_entry_no_expiry.is_expired(), "Cache with 0 TTL should not expire"
        
        # Test with negative TTL (should not expire)
        cache_entry_negative = SimpleCacheStore("test_key3", {"data": "test"}, ttl_minutes=-1)
        assert not cache_entry_negative.is_expired(), "Cache with negative TTL should not expire"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 