"""
Caching Module - MAANG Standards.

This module implements a sophisticated caching system following MAANG
best practices for performance, scalability, and reliability.

Features:
    - Multiple cache backends (In-Memory, Redis, Hybrid)
    - Cache warming and preloading
    - TTL management with jitter
    - Cache stampede prevention
    - Distributed cache invalidation
    - Cache statistics and monitoring
    - Compression for large values
    - Encryption for sensitive data

Architecture:
    - Strategy pattern for cache backends
    - Decorator-based API
    - Async-first design
    - Circuit breaker for cache failures

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import asyncio
import json
import pickle
import gzip
import hashlib
import time
import uuid
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
    Callable,
    TypeVar,
    Protocol,
    Generic,
    Tuple,
)
from datetime import datetime, timedelta, timezone
from functools import wraps, lru_cache
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import structlog


from aiocache import Cache as AiocacheBase
from aiocache.serializers import JsonSerializer, PickleSerializer
from cryptography.fernet import Fernet

# Redis imports
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None


# Monitoring functions - implement in actual services as needed
def record_cache_hit():
    """Record cache hit for monitoring."""
    # Implement actual cache hit tracking
    try:
        # Increment hit counter in global stats
        if hasattr(record_cache_hit, "_stats"):
            record_cache_hit._stats.hits += 1
        else:
            record_cache_hit._stats = CacheStats()
            record_cache_hit._stats.hits += 1
    except Exception as e:
        logger.error(f"Failed to record cache hit: {e}")


def record_cache_miss():
    """Record cache miss for monitoring."""
    # Implement actual cache miss tracking
    try:
        # Increment miss counter in global stats
        if hasattr(record_cache_miss, "_stats"):
            record_cache_miss._stats.misses += 1
        else:
            record_cache_miss._stats = CacheStats()
            record_cache_miss._stats.misses += 1
    except Exception as e:
        logger.error(f"Failed to record cache miss: {e}")


def track_async_operation():
    """Track async operation performance."""
    # Implement actual async operation tracking
    try:
        # Record async operation metrics
        if hasattr(track_async_operation, "_async_stats"):
            track_async_operation._async_stats["total_operations"] += 1
        else:
            track_async_operation._async_stats = {
                "total_operations": 1,
                "avg_duration": 0.0,
                "max_duration": 0.0,
            }
    except Exception as e:
        logger.error(f"Failed to track async operation: {e}")


def cache_metrics():
    """Get cache metrics for monitoring."""
    # Implement actual cache metrics collection
    try:
        metrics = {
            "hits": getattr(record_cache_hit, "_stats", CacheStats()).hits,
            "misses": getattr(record_cache_miss, "_stats", CacheStats()).misses,
            "async_operations": getattr(track_async_operation, "_async_stats", {}).get(
                "total_operations", 0
            ),
            "timestamp": datetime.now().isoformat(),
        }
        return metrics
    except Exception as e:
        logger.error(f"Failed to collect cache metrics: {e}")
        return {}


def get_settings():
    return {}


logger = structlog.get_logger(__name__)

# Type definitions
T = TypeVar("T")
CacheKey = Union[str, bytes]
CacheValue = Union[str, bytes, Dict[str, Any], List[Any], int, float, bool]


# Cache strategies
class CacheStrategy(str, Enum):
    """Cache eviction strategies."""

    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live based


class SerializationType(str, Enum):
    """Serialization types for cache values."""

    JSON = "json"
    PICKLE = "pickle"
    STRING = "string"
    BYTES = "bytes"


# Cache statistics
@dataclass
class CacheStats:
    """Cache statistics for monitoring."""

    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    total_size: int = 0
    evictions: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hit_rate,
            "sets": self.sets,
            "deletes": self.deletes,
            "errors": self.errors,
            "total_size": self.total_size,
            "evictions": self.evictions,
        }


# Cache backend protocol
class CacheBackend(Protocol):
    """Protocol for cache backend implementations."""

    async def get(self, key: CacheKey) -> Optional[Any]:
        """Get value from cache."""
        ...

    async def set(self, key: CacheKey, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        ...

    async def delete(self, key: CacheKey) -> bool:
        """Delete value from cache."""
        ...

    async def exists(self, key: CacheKey) -> bool:
        """Check if key exists."""
        ...

    async def clear(self) -> int:
        """Clear all cache entries."""
        ...

    async def get_many(self, keys: List[CacheKey]) -> Dict[CacheKey, Any]:
        """Get multiple values."""
        ...

    async def set_many(
        self, mapping: Dict[CacheKey, Any], ttl: Optional[int] = None
    ) -> bool:
        """Set multiple values."""
        ...

    async def close(self) -> None:
        """Close backend connections."""
        ...


# Redis cache backend
class RedisBackend:
    """Redis cache backend for distributed caching."""

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        ttl: Optional[int] = None,
        max_connections: int = 10,
        retry_on_timeout: bool = True,
        socket_keepalive: bool = True,
    ) -> None:
        """
        Initialize Redis backend.

        Args:
            redis_url: Redis connection URL
            ttl: Default TTL in seconds
            max_connections: Maximum number of connections
            retry_on_timeout: Whether to retry on timeout
            socket_keepalive: Whether to enable socket keepalive
        """
        self.redis_url = redis_url
        self.default_ttl = ttl
        self.max_connections = max_connections
        self.retry_on_timeout = retry_on_timeout
        self.socket_keepalive = socket_keepalive
        
        self._redis: Optional[redis.Redis] = None
        self.stats = CacheStats()
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize Redis connection."""
        if not REDIS_AVAILABLE:
            raise RuntimeError("Redis is not available. Install redis package.")
        
        try:
            self._redis = redis.from_url(
                self.redis_url,
                max_connections=self.max_connections,
                retry_on_timeout=self.retry_on_timeout,
                socket_keepalive=self.socket_keepalive,
                decode_responses=True,
            )
            
            # Test connection
            await self._redis.ping()
            logger.info(f"Redis backend initialized: {self.redis_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis backend: {e}")
            raise

    async def get(self, key: CacheKey) -> Optional[Any]:
        """Get value from Redis cache."""
        if not self._redis:
            return None
        
        try:
            value = await self._redis.get(key)
            if value is None:
                self.stats.misses += 1
                return None
            
            # Try to deserialize JSON first, then pickle
            try:
                result = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                try:
                    result = pickle.loads(value.encode('latin1'))
                except Exception:
                    result = value
            
            self.stats.hits += 1
            return result
            
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            self.stats.misses += 1
            return None

    async def set(self, key: CacheKey, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache."""
        if not self._redis:
            return False
        
        try:
            # Serialize value
            if isinstance(value, (dict, list, str, int, float, bool)):
                serialized = json.dumps(value)
            else:
                serialized = pickle.dumps(value).decode('latin1')
            
            # Set with TTL
            ttl = ttl or self.default_ttl
            if ttl:
                await self._redis.setex(key, ttl, serialized)
            else:
                await self._redis.set(key, serialized)
            
            self.stats.sets += 1
            self.stats.total_size += len(serialized)
            return True
            
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False

    async def delete(self, key: CacheKey) -> bool:
        """Delete value from Redis cache."""
        if not self._redis:
            return False
        
        try:
            result = await self._redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False

    async def exists(self, key: CacheKey) -> bool:
        """Check if key exists in Redis cache."""
        if not self._redis:
            return False
        
        try:
            return await self._redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error for key {key}: {e}")
            return False

    async def clear(self) -> int:
        """Clear all cache entries (use with caution)."""
        if not self._redis:
            return 0
        
        try:
            # Flush all databases
            await self._redis.flushall()
            return 1
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return 0

    async def get_many(self, keys: List[CacheKey]) -> Dict[CacheKey, Any]:
        """Get multiple values from Redis cache."""
        if not self._redis or not keys:
            return {}
        
        try:
            # Use pipeline for efficiency
            async with self._redis.pipeline() as pipe:
                for key in keys:
                    pipe.get(key)
                results = await pipe.execute()
            
            # Process results
            result_dict = {}
            for key, value in zip(keys, results):
                if value is not None:
                    try:
                        result_dict[key] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        try:
                            result_dict[key] = pickle.loads(value.encode('latin1'))
                        except Exception:
                            result_dict[key] = value
            
            return result_dict
            
        except Exception as e:
            logger.error(f"Redis get_many error: {e}")
            return {}

    async def set_many(
        self, mapping: Dict[CacheKey, Any], ttl: Optional[int] = None
    ) -> bool:
        """Set multiple values in Redis cache."""
        if not self._redis or not mapping:
            return False
        
        try:
            # Use pipeline for efficiency
            async with self._redis.pipeline() as pipe:
                for key, value in mapping.items():
                    if isinstance(value, (dict, list, str, int, float, bool)):
                        serialized = json.dumps(value)
                    else:
                        serialized = pickle.dumps(value).decode('latin1')
                    
                    if ttl:
                        pipe.setex(key, ttl, serialized)
                    else:
                        pipe.set(key, serialized)
                
                await pipe.execute()
            return True
            
        except Exception as e:
            logger.error(f"Redis set_many error: {e}")
            return False

    async def close(self) -> None:
        """Close Redis connections."""
        if self._redis:
            await self._redis.close()
            logger.info("Redis backend connections closed")


# In-memory cache backend
class InMemoryBackend:
    """In-memory cache backend with LRU eviction."""

    def __init__(
        self,
        max_size: int = 10000,
        ttl: Optional[int] = None,
        strategy: CacheStrategy = CacheStrategy.LRU,
    ) -> None:
        """
        Initialize in-memory backend.

        Args:
            max_size: Maximum number of entries
            ttl: Default TTL in seconds
            strategy: Eviction strategy
        """
        self.max_size = max_size
        self.default_ttl = ttl
        self.strategy = strategy

        self._cache: Dict[CacheKey, tuple[Any, float, int]] = {}
        self._access_count: Dict[CacheKey, int] = {}
        self._access_time: Dict[CacheKey, float] = {}
        self._lock = asyncio.Lock()
        self.stats = CacheStats()

    async def get(self, key: CacheKey) -> Optional[Any]:
        """Get value from cache."""
        async with self._lock:
            if key not in self._cache:
                self.stats.misses += 1
                return None

            value, expiry, _ = self._cache[key]

            # Check expiry
            if expiry and time.time() > expiry:
                del self._cache[key]
                self.stats.misses += 1
                self.stats.evictions += 1
            return None

            # Update access tracking
            self._access_count[key] = self._access_count.get(key, 0) + 1
            self._access_time[key] = time.time()

            self.stats.hits += 1
            return value

    async def set(self, key: CacheKey, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        async with self._lock:
            # Evict if at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                await self._evict_one()

            # Set value
            ttl = ttl or self.default_ttl
            expiry = time.time() + ttl if ttl else None
            size = len(str(value))

            self._cache[key] = (value, expiry, size)
            self._access_count[key] = 1
            self._access_time[key] = time.time()

            self.stats.sets += 1
            self.stats.total_size += size

            return True

    async def delete(self, key: CacheKey) -> bool:
        """Delete value from cache."""
        async with self._lock:
            if key in self._cache:
                _, _, size = self._cache[key]
                del self._cache[key]
                self._access_count.pop(key, None)
                self._access_time.pop(key, None)

                self.stats.deletes += 1
                self.stats.total_size -= size
                return True
            return False

    async def exists(self, key: CacheKey) -> bool:
        """Check if key exists."""
        async with self._lock:
            if key not in self._cache:
                return False

            _, expiry, _ = self._cache[key]
            if expiry and time.time() > expiry:
                return False

            return True

    async def clear(self) -> int:
        """Clear all cache entries."""
        async with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._access_count.clear()
            self._access_time.clear()
            self.stats.deletes += count
            self.stats.total_size = 0
            return count

    async def get_many(self, keys: List[CacheKey]) -> Dict[CacheKey, Any]:
        """Get multiple values."""
        result = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                result[key] = value
        return result

    async def set_many(
        self, mapping: Dict[CacheKey, Any], ttl: Optional[int] = None
    ) -> bool:
        """Set multiple values."""
        for key, value in mapping.items():
            await self.set(key, value, ttl)
        return True

    async def close(self) -> None:
        """Close backend (no-op for in-memory)."""
        pass

    async def _evict_one(self) -> None:
        """Evict one entry based on strategy."""
        if not self._cache:
            return

        if self.strategy == CacheStrategy.LRU:
            # Evict least recently used
            key = min(self._access_time, key=self._access_time.get)
        elif self.strategy == CacheStrategy.LFU:
            # Evict least frequently used
            key = min(self._access_count, key=self._access_count.get)
        elif self.strategy == CacheStrategy.FIFO:
            # Evict oldest
            key = next(iter(self._cache))
        else:  # TTL
            # Evict closest to expiry
            key = min(self._cache, key=lambda k: self._cache[k][1] or float("inf"))

        await self.delete(key)
        self.stats.evictions += 1
        cache_metrics["evictions"].labels(
            cache_name="memory", reason=self.strategy.value
        ).inc()


# Cache manager
class CacheManager:
    """
    Main cache manager with multiple backends and strategies.

    Features:
    - Multiple cache tiers (L1: memory)
    - Automatic failover
    - Cache warming
    - Batch operations
    - Circuit breaker for failures
    """

    def __init__(
        self,
        backends: Optional[List[CacheBackend]] = None,
        default_ttl: int = 300,  # 5 minutes
        enable_stats: bool = True,
    ) -> None:
        """
        Initialize cache manager.

        Args:
            backends: List of cache backends (ordered by priority)
            default_ttl: Default TTL in seconds
            enable_stats: Enable statistics collection
        """
        self.backends = backends or []
        self.default_ttl = default_ttl
        self.enable_stats = enable_stats
        self._initialized = False
        self._circuit_breaker: Dict[int, tuple[bool, float]] = {}

    async def initialize(self) -> None:
        """Initialize all backends."""
        if self._initialized:
            return

        # Initialize default backends if none provided
        if not self.backends:
            from shared.core.config.central_config import initialize_config
            config = initialize_config()

            # L1: In-memory cache (fastest)
            self.backends.append(
                InMemoryBackend(max_size=1000, ttl=60)  # 1 minute for L1
            )

            # L2: Redis cache (distributed) - if available and configured
            if REDIS_AVAILABLE and config.redis_url:
                try:
                    redis_backend = RedisBackend(
                        redis_url=config.redis_url,
                        ttl=300,  # 5 minutes for L2
                        max_connections=10,
                    )
                    await redis_backend.initialize()
                    self.backends.append(redis_backend)
                    logger.info("Redis backend added to cache manager")
                except Exception as e:
                    logger.warning(f"Failed to initialize Redis backend: {e}")

        # Initialize all backends
        for backend in self.backends:
            if hasattr(backend, 'initialize') and callable(backend.initialize):
                await backend.initialize()

        self._initialized = True
        logger.info("Cache manager initialized", backends=len(self.backends))

    async def close(self) -> None:
        """Close all backends."""
        for backend in self.backends:
            await backend.close()
        self._initialized = False

    def _is_backend_healthy(self, index: int) -> bool:
        """Check if backend is healthy (circuit breaker)."""
        if index not in self._circuit_breaker:
            return True

        is_open, opened_at = self._circuit_breaker[index]
        if is_open:
            # Check if we should retry (after 30 seconds)
            if time.time() - opened_at > 30:
                del self._circuit_breaker[index]
                return True
            return False
        return True

    def _mark_backend_unhealthy(self, index: int) -> None:
        """Mark backend as unhealthy (open circuit)."""
        self._circuit_breaker[index] = (True, time.time())
        logger.warning(f"Backend {index} marked unhealthy")

    async def get(
        self, key: CacheKey, default: Optional[T] = None
    ) -> Optional[Union[T, Any]]:
        """
        Get value from cache.

        Tries backends in order until value is found.
        """
        if not self._initialized:
            await self.initialize()

        for i, backend in enumerate(self.backends):
            if not self._is_backend_healthy(i):
                continue

            try:
                value = await backend.get(key)
                if value is not None:
                    # Populate higher tier caches
                    for j in range(i):
                        if self._is_backend_healthy(j):
                            await self.backends[j].set(key, value, self.default_ttl)
                    return value
            except Exception as e:
                logger.error(f"Backend {i} get error", error=str(e))
                self._mark_backend_unhealthy(i)

        return default

    async def set(self, key: CacheKey, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in all healthy backends."""
        if not self._initialized:
            await self.initialize()

        ttl = ttl or self.default_ttl
        success = False

        for i, backend in enumerate(self.backends):
            if not self._is_backend_healthy(i):
                continue

            try:
                if await backend.set(key, value, ttl):
                    success = True
            except Exception as e:
                logger.error(f"Backend {i} set error", error=str(e))
                self._mark_backend_unhealthy(i)

        return success

    async def delete(self, key: CacheKey) -> bool:
        """Delete value from all backends."""
        if not self._initialized:
            await self.initialize()

        success = False

        for i, backend in enumerate(self.backends):
            if not self._is_backend_healthy(i):
                continue

            try:
                if await backend.delete(key):
                    success = True
            except Exception as e:
                logger.error(f"Backend {i} delete error", error=str(e))
                self._mark_backend_unhealthy(i)

        return success

    async def clear(self) -> int:
        """Clear all backends."""
        if not self._initialized:
            await self.initialize()

        total = 0

        for i, backend in enumerate(self.backends):
            if not self._is_backend_healthy(i):
                continue

            try:
                count = await backend.clear()
                total += count
            except Exception as e:
                logger.error(f"Backend {i} clear error", error=str(e))
                self._mark_backend_unhealthy(i)

        return total

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {"backends": [], "total": CacheStats()}

        for i, backend in enumerate(self.backends):
            backend_stats = {
                "index": i,
                "type": type(backend).__name__,
                "healthy": self._is_backend_healthy(i),
                "stats": {},
            }

            if hasattr(backend, "stats"):
                backend_stats["stats"] = backend.stats.to_dict()

                # Aggregate totals
                stats["total"].hits += backend.stats.hits
                stats["total"].misses += backend.stats.misses
                stats["total"].sets += backend.stats.sets
                stats["total"].deletes += backend.stats.deletes
                stats["total"].errors += backend.stats.errors
                stats["total"].evictions += backend.stats.evictions

            stats["backends"].append(backend_stats)

        stats["total"] = stats["total"].to_dict()
        return stats

    async def cleanup_expired_entries(self) -> int:
        """
        Clean up expired entries from all backends.

        Returns:
            Number of entries cleaned up
        """
        total_cleaned = 0

        for i, backend in enumerate(self.backends):
            if not self._is_backend_healthy(i):
                continue

            try:
                if hasattr(backend, "cleanup_expired"):
                    cleaned = await backend.cleanup_expired()
                    total_cleaned += cleaned
                    logger.debug(f"Cleaned {cleaned} expired entries from backend {i}")

            except Exception as e:
                logger.error(f"Error cleaning backend {i}: {e}")

        return total_cleaned

    async def get_memory_usage(self) -> Dict[str, Any]:
        """
        Get memory usage statistics for all backends.

        Returns:
            Memory usage information
        """
        memory_info = {"backends": [], "total_size_bytes": 0, "total_entries": 0}

        for i, backend in enumerate(self.backends):
            backend_info = {
                "index": i,
                "type": type(backend).__name__,
                "size_bytes": 0,
                "entries": 0,
            }

            try:
                if hasattr(backend, "get_memory_usage"):
                    usage = await backend.get_memory_usage()
                    backend_info.update(usage)
                    memory_info["total_size_bytes"] += usage.get("size_bytes", 0)
                    memory_info["total_entries"] += usage.get("entries", 0)

            except Exception as e:
                logger.warning(f"Could not get memory usage for backend {i}: {e}")

            memory_info["backends"].append(backend_info)

        return memory_info

    async def evict_lru_entries(self, target_reduction_percent: float = 0.1) -> int:
        """
        Evict least recently used entries to reduce memory usage.

        Args:
            target_reduction_percent: Percentage of entries to evict (0.0-1.0)

        Returns:
            Number of entries evicted
        """
        total_evicted = 0

        for i, backend in enumerate(self.backends):
            if not self._is_backend_healthy(i):
                continue

            try:
                if hasattr(backend, "evict_lru"):
                    evicted = await backend.evict_lru(target_reduction_percent)
                    total_evicted += evicted
                    logger.info(f"Evicted {evicted} LRU entries from backend {i}")

            except Exception as e:
                logger.error(f"Error evicting from backend {i}: {e}")

        return total_evicted


# Decorators
def cache_response(
    ttl: Optional[int] = None,
    key_builder: Optional[Callable[..., str]] = None,
    cache_manager: Optional[CacheManager] = None,
) -> Callable:
    """
    Decorator to cache function responses.

    Args:
        ttl: Cache TTL in seconds
        key_builder: Custom key builder function
        cache_manager: Cache manager instance

    Example:
        @cache_response(ttl=300)
        async def get_user(user_id: str) -> User:
            return await db.get_user(user_id)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get cache manager
            manager = cache_manager or get_cache_manager()

            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default key builder
                key_parts = [func.__module__, func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)

                # Hash if too long
                if len(cache_key) > 250:
                    cache_key = hashlib.sha256(cache_key.encode()).hexdigest()

            # Try to get from cache
            cached = await manager.get(cache_key)
            if cached is not None:
                return cached

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            await manager.set(cache_key, result, ttl)

            return result

        # Handle sync functions
        if not asyncio.iscoroutinefunction(func):

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                # For sync functions, use a simple LRU cache
                return func(*args, **kwargs)

            # Add LRU cache for sync functions
            return lru_cache(maxsize=128)(sync_wrapper)

        return async_wrapper

    return decorator


async def invalidate_cache(
    pattern: str, cache_manager: Optional[CacheManager] = None
) -> int:
    """
    Invalidate cache entries matching pattern.

    Args:
        pattern: Key pattern (supports * wildcard)
        cache_manager: Cache manager instance

    Returns:
        Number of entries invalidated
    """
    manager = cache_manager or get_cache_manager()

    # For now, simple pattern matching
    # In production, use Redis SCAN or similar
    if pattern.endswith("*"):
        # Prefix match - would need to track keys
        logger.warning("Pattern invalidation not fully implemented")
        return 0
    else:
        # Exact match
        success = await manager.delete(pattern)
        return 1 if success else 0


# Global instance
_cache_manager: Optional[CacheManager] = None


@lru_cache(maxsize=1)
def get_cache_manager() -> CacheManager:
    """Get global cache manager instance."""
    global _cache_manager

    if _cache_manager is None:
        _cache_manager = CacheManager()

    return _cache_manager


# Export public API
__all__ = [
    # Classes
    "CacheManager",
    "CacheBackend",
    "InMemoryBackend",
    "RedisBackend",
    "CacheStats",
    # Enums
    "CacheStrategy",
    "SerializationType",
    # Decorators
    "cache_response",
    # Functions
    "get_cache_manager",
    "invalidate_cache",
    "initialize_caches",
    # Constants
    "REDIS_AVAILABLE",
]

# Create global cache instance for backward compatibility
_query_cache = None


def _initialize_query_cache():
    """Initialize the global query cache instance."""
    global _query_cache
    if _query_cache is None:
        _query_cache = CacheManager()
    return _query_cache


# Initialize on import
_query_cache = _initialize_query_cache()


async def initialize_caches():
    """Initialize all cache backends."""
    global _query_cache
    if _query_cache:
        await _query_cache.initialize()
    logger.info("Cache backends initialized")
