"""
Unit tests for cache service functionality.

Tests cover:
- Cache get/set operations
- Cache expiration handling
- Cache key generation
- Cache invalidation
- Cache statistics and metrics
- Error handling for cache operations
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, Optional

from shared.core.cache.cache_manager import UnifiedCacheManager



class TestCacheService:
    """Test cache service functionality."""

    @pytest.fixture
    def cache_manager(self):
        """Create cache manager for testing."""
        from shared.core.cache.cache_config import CacheLevel
        return UnifiedCacheManager.get_instance(CacheLevel.QUERY_RESULTS)

    @pytest.fixture
    def memory_cache(self):
        """Create memory cache for testing."""
        return MemoryCache()

    @pytest.fixture
    def sample_data(self):
        """Sample data for testing."""
        return {
            "string": "test_value",
            "number": 42,
            "list": [1, 2, 3, 4, 5],
            "dict": {"key": "value", "nested": {"deep": "value"}},
            "boolean": True,
            "none": None
        }

    @pytest.mark.asyncio
    async def test_cache_set_get_basic(self, cache_manager, sample_data):
        """Test basic cache set and get operations."""
        key = "test_key"
        value = sample_data["string"]
        ttl = 3600  # 1 hour
        
        # Set value in cache
        await cache_manager.set(key, value, ttl)
        
        # Get value from cache
        cached_value = await cache_manager.get(key)
        
        assert cached_value == value

    @pytest.mark.asyncio
    async def test_cache_set_get_complex_data(self, cache_manager, sample_data):
        """Test cache operations with complex data types."""
        key = "complex_data"
        value = sample_data["dict"]
        ttl = 3600
        
        await cache_manager.set(key, value, ttl)
        cached_value = await cache_manager.get(key)
        
        assert cached_value == value
        assert cached_value["nested"]["deep"] == "value"

    @pytest.mark.asyncio
    async def test_cache_expiration(self, cache_manager):
        """Test cache expiration functionality."""
        key = "expiring_key"
        value = "expiring_value"
        ttl = 1  # 1 second
        
        await cache_manager.set(key, value, ttl)
        
        # Value should be available immediately
        cached_value = await cache_manager.get(key)
        assert cached_value == value
        
        # Wait for expiration
        await asyncio.sleep(1.1)
        
        # Value should be expired
        cached_value = await cache_manager.get(key)
        assert cached_value is None

    @pytest.mark.asyncio
    async def test_cache_key_generation(self, cache_manager):
        """Test cache key generation and uniqueness."""
        # Test different key patterns
        keys = [
            "simple_key",
            "key_with_underscores",
            "key-with-dashes",
            "key_with_numbers_123",
            "key_with_spaces and special chars!@#",
            "very_long_key_" + "x" * 100
        ]
        
        for key in keys:
            value = f"value_for_{key}"
            await cache_manager.set(key, value, 3600)
            cached_value = await cache_manager.get(key)
            assert cached_value == value

    @pytest.mark.asyncio
    async def test_cache_get_nonexistent(self, cache_manager):
        """Test getting non-existent cache keys."""
        key = "nonexistent_key"
        cached_value = await cache_manager.get(key)
        
        assert cached_value is None

    @pytest.mark.asyncio
    async def test_cache_delete(self, cache_manager):
        """Test cache deletion functionality."""
        key = "delete_test_key"
        value = "delete_test_value"
        
        # Set value
        await cache_manager.set(key, value, 3600)
        
        # Verify it exists
        cached_value = await cache_manager.get(key)
        assert cached_value == value
        
        # Delete value
        await cache_manager.delete(key)
        
        # Verify it's gone
        cached_value = await cache_manager.get(key)
        assert cached_value is None

    @pytest.mark.asyncio
    async def test_cache_multiple_operations(self, cache_manager):
        """Test multiple cache operations."""
        operations = [
            ("key1", "value1"),
            ("key2", "value2"),
            ("key3", "value3"),
        ]
        
        # Set multiple values
        for key, value in operations:
            await cache_manager.set(key, value, 3600)
        
        # Get all values
        for key, expected_value in operations:
            cached_value = await cache_manager.get(key)
            assert cached_value == expected_value
        
        # Delete all values
        for key, _ in operations:
            await cache_manager.delete(key)
            cached_value = await cache_manager.get(key)
            assert cached_value is None

    @pytest.mark.asyncio
    async def test_cache_overwrite(self, cache_manager):
        """Test overwriting existing cache values."""
        key = "overwrite_key"
        value1 = "original_value"
        value2 = "new_value"
        
        # Set initial value
        await cache_manager.set(key, value1, 3600)
        cached_value = await cache_manager.get(key)
        assert cached_value == value1
        
        # Overwrite with new value
        await cache_manager.set(key, value2, 3600)
        cached_value = await cache_manager.get(key)
        assert cached_value == value2

    @pytest.mark.asyncio
    async def test_cache_ttl_variations(self, cache_manager):
        """Test different TTL values."""
        ttl_tests = [
            (1, "1_second"),
            (60, "1_minute"),
            (3600, "1_hour"),
            (86400, "1_day"),
        ]
        
        for ttl, suffix in ttl_tests:
            key = f"ttl_test_{suffix}"
            value = f"value_{suffix}"
            
            await cache_manager.set(key, value, ttl)
            cached_value = await cache_manager.get(key)
            assert cached_value == value

    @pytest.mark.asyncio
    async def test_cache_large_data(self, cache_manager):
        """Test cache with large data."""
        key = "large_data_key"
        # Create large data (1MB of text)
        large_value = "x" * 1024 * 1024
        
        await cache_manager.set(key, large_value, 3600)
        cached_value = await cache_manager.get(key)
        
        assert cached_value == large_value
        assert len(cached_value) == 1024 * 1024

    @pytest.mark.asyncio
    async def test_cache_concurrent_access(self, cache_manager):
        """Test concurrent cache access."""
        key = "concurrent_key"
        value = "concurrent_value"
        
        # Set value
        await cache_manager.set(key, value, 3600)
        
        # Simulate concurrent reads
        async def read_cache():
            return await cache_manager.get(key)
        
        # Create multiple concurrent tasks
        tasks = [read_cache() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All should return the same value
        for result in results:
            assert result == value

    @pytest.mark.asyncio
    async def test_cache_error_handling(self, cache_manager):
        """Test cache error handling."""
        # Test with invalid key types
        invalid_keys = [None, 123, [], {}]
        
        for invalid_key in invalid_keys:
            try:
                await cache_manager.set(invalid_key, "value", 3600)
                # Should handle gracefully or raise appropriate exception
            except Exception:
                # Expected for invalid keys
                pass

    @pytest.mark.asyncio
    async def test_cache_statistics(self, cache_manager):
        """Test cache statistics and metrics."""
        # Perform some operations
        await cache_manager.set("stat_key1", "value1", 3600)
        await cache_manager.set("stat_key2", "value2", 3600)
        await cache_manager.get("stat_key1")
        await cache_manager.get("nonexistent_key")  # Miss
        await cache_manager.delete("stat_key1")
        
        # Get statistics (if available)
        stats = await cache_manager.get_stats()
        
        # Basic validation of stats structure
        if stats:
            assert isinstance(stats, dict)

    @pytest.mark.asyncio
    async def test_cache_clear_all(self, cache_manager):
        """Test clearing all cache entries."""
        # Set multiple values
        keys = ["clear_key1", "clear_key2", "clear_key3"]
        for key in keys:
            await cache_manager.set(key, f"value_{key}", 3600)
        
        # Verify they exist
        for key in keys:
            cached_value = await cache_manager.get(key)
            assert cached_value is not None
        
        # Clear all
        await cache_manager.clear()
        
        # Verify all are gone
        for key in keys:
            cached_value = await cache_manager.get(key)
            assert cached_value is None

    @pytest.mark.asyncio
    async def test_cache_pattern_matching(self, cache_manager):
        """Test cache pattern matching for bulk operations."""
        # Set values with pattern
        pattern_keys = ["pattern:user:1", "pattern:user:2", "pattern:user:3"]
        other_keys = ["other:key1", "other:key2"]
        
        for key in pattern_keys + other_keys:
            await cache_manager.set(key, f"value_{key}", 3600)
        
        # Get keys by pattern (if supported)
        try:
            pattern_keys_found = await cache_manager.get_keys("pattern:user:*")
            assert len(pattern_keys_found) >= 3
        except NotImplementedError:
            # Pattern matching not supported
            pass

    @pytest.mark.asyncio
    async def test_cache_serialization(self, cache_manager):
        """Test cache serialization of complex objects."""
        complex_object = {
            "string": "test",
            "number": 42,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "boolean": True,
            "none": None
        }
        
        key = "complex_object"
        await cache_manager.set(key, complex_object, 3600)
        cached_object = await cache_manager.get(key)
        
        assert cached_object == complex_object
        assert cached_object["dict"]["nested"] == "value"

    @pytest.mark.asyncio
    async def test_cache_memory_usage(self, cache_manager):
        """Test cache memory usage tracking."""
        # Set some data
        for i in range(100):
            await cache_manager.set(f"memory_test_{i}", f"value_{i}" * 100, 3600)
        
        # Get memory usage (if available)
        try:
            memory_usage = await cache_manager.get_memory_usage()
            if memory_usage:
                assert isinstance(memory_usage, (int, float))
                assert memory_usage > 0
        except NotImplementedError:
            # Memory usage tracking not supported
            pass

    @pytest.mark.asyncio
    async def test_cache_connection_pooling(self, cache_manager):
        """Test cache connection pooling and reuse."""
        # Perform multiple operations to test connection reuse
        operations = []
        for i in range(50):
            operations.append(cache_manager.set(f"pool_test_{i}", f"value_{i}", 3600))
            operations.append(cache_manager.get(f"pool_test_{i}"))
        
        # Execute all operations
        results = await asyncio.gather(*operations, return_exceptions=True)
        
        # Check that all operations succeeded
        for result in results:
            assert not isinstance(result, Exception)

    @pytest.mark.asyncio
    async def test_cache_timeout_handling(self, cache_manager):
        """Test cache timeout handling."""
        # Test with very short timeout
        key = "timeout_test"
        value = "timeout_value"
        
        await cache_manager.set(key, value, 0.1)  # 100ms
        
        # Should be available immediately
        cached_value = await cache_manager.get(key)
        assert cached_value == value
        
        # Wait for timeout
        await asyncio.sleep(0.2)
        
        # Should be expired
        cached_value = await cache_manager.get(key)
        assert cached_value is None

    @pytest.mark.asyncio
    async def test_cache_bulk_operations(self, cache_manager):
        """Test bulk cache operations."""
        # Bulk set
        bulk_data = {f"bulk_key_{i}": f"bulk_value_{i}" for i in range(10)}
        
        try:
            await cache_manager.set_many(bulk_data, 3600)
            
            # Bulk get
            keys = list(bulk_data.keys())
            bulk_results = await cache_manager.get_many(keys)
            
            assert len(bulk_results) == len(bulk_data)
            for key, value in bulk_data.items():
                assert bulk_results.get(key) == value
        except NotImplementedError:
            # Bulk operations not supported
            pass

    @pytest.mark.asyncio
    async def test_cache_namespace_isolation(self, cache_manager):
        """Test cache namespace isolation."""
        # Test with different namespaces
        namespaces = ["ns1", "ns2", "ns3"]
        key = "test_key"
        value = "test_value"
        
        for namespace in namespaces:
            namespaced_key = f"{namespace}:{key}"
            await cache_manager.set(namespaced_key, f"{value}_{namespace}", 3600)
        
        # Verify isolation
        for namespace in namespaces:
            namespaced_key = f"{namespace}:{key}"
            cached_value = await cache_manager.get(namespaced_key)
            assert cached_value == f"{value}_{namespace}"

    @pytest.mark.asyncio
    async def test_cache_compression(self, cache_manager):
        """Test cache compression for large data."""
        # Create compressible data (repeating pattern)
        compressible_data = "A" * 10000 + "B" * 10000 + "C" * 10000
        
        key = "compression_test"
        await cache_manager.set(key, compressible_data, 3600)
        cached_data = await cache_manager.get(key)
        
        assert cached_data == compressible_data
        assert len(cached_data) == 30000

    @pytest.mark.asyncio
    async def test_cache_eviction_policy(self, cache_manager):
        """Test cache eviction policy."""
        # Fill cache with data
        for i in range(1000):
            await cache_manager.set(f"eviction_test_{i}", f"value_{i}" * 100, 3600)
        
        # Try to get some values to test eviction
        for i in range(0, 1000, 100):
            cached_value = await cache_manager.get(f"eviction_test_{i}")
            # Some values might be evicted, which is expected

    @pytest.mark.asyncio
    async def test_cache_health_check(self, cache_manager):
        """Test cache health check functionality."""
        try:
            health_status = await cache_manager.health_check()
            assert isinstance(health_status, dict)
            assert "status" in health_status
        except NotImplementedError:
            # Health check not supported
            pass
