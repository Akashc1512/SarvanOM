#!/usr/bin/env python3
"""
Advanced Caching System for SarvanOM
Implements MAANG/OpenAI/Perplexity level caching with Redis + in-memory fallback
"""

import asyncio
import hashlib
import json
import logging
import time
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as aioredis
from fastapi import HTTPException
import pickle
import gzip
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Cache strategy types following industry standards"""
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    HYBRID = "hybrid"

class CacheLevel(Enum):
    """Cache levels for different data types"""
    HOT = "hot"      # Frequently accessed, short TTL
    WARM = "warm"    # Moderately accessed, medium TTL
    COLD = "cold"    # Rarely accessed, long TTL

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    ttl: int = 3600  # Default 1 hour
    level: CacheLevel = CacheLevel.WARM
    compressed: bool = False
    size_bytes: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "access_count": self.access_count,
            "ttl": self.ttl,
            "level": self.level.value,
            "compressed": self.compressed,
            "size_bytes": self.size_bytes
        }

class AdvancedCacheManager:
    """
    Advanced caching system with Redis + in-memory fallback
    Following MAANG/OpenAI/Perplexity industry standards
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        max_memory_size: int = 100 * 1024 * 1024,  # 100MB
        compression_threshold: int = 1024,  # 1KB
        enable_compression: bool = True,
        cache_strategy: CacheStrategy = CacheStrategy.HYBRID,
        enable_metrics: bool = True
    ):
        self.redis_url = redis_url
        self.redis_client: Optional[aioredis.Redis] = None
        self.max_memory_size = max_memory_size
        self.compression_threshold = compression_threshold
        self.enable_compression = enable_compression
        self.cache_strategy = cache_strategy
        self.enable_metrics = enable_metrics
        
        # In-memory cache as fallback
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.current_memory_size = 0
        
        # Metrics
        self.metrics = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "compressions": 0,
            "redis_errors": 0
        }
        
        # Cache patterns for different query types
        self.cache_patterns = {
            "search": {"ttl": 1800, "level": CacheLevel.HOT},  # 30 min
            "fact_check": {"ttl": 3600, "level": CacheLevel.WARM},  # 1 hour
            "synthesis": {"ttl": 7200, "level": CacheLevel.COLD},  # 2 hours
            "vector_search": {"ttl": 900, "level": CacheLevel.HOT},  # 15 min
            "analytics": {"ttl": 300, "level": CacheLevel.HOT},  # 5 min
        }
    
    async def initialize(self) -> None:
        """Initialize Redis connection and cache"""
        try:
            if self.redis_url:
                self.redis_client = aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=False,  # Keep as bytes for compression
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                # Test connection
                await self.redis_client.ping()
                logger.info("✅ Redis cache initialized successfully")
            else:
                logger.warning("⚠️ Redis URL not provided, using in-memory cache only")
        except Exception as e:
            logger.error(f"❌ Redis initialization failed: {e}")
            self.redis_client = None
    
    def _generate_cache_key(self, query: str, user_id: str, endpoint: str) -> str:
        """Generate consistent cache key"""
        # Normalize query for better cache hits
        normalized_query = query.lower().strip()
        key_data = f"{endpoint}:{user_id}:{normalized_query}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def _compress_data(self, data: Any) -> bytes:
        """Compress data using gzip"""
        try:
            serialized = pickle.dumps(data)
            if len(serialized) > self.compression_threshold and self.enable_compression:
                compressed = gzip.compress(serialized)
                self.metrics["compressions"] += 1
                return compressed
            return serialized
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            return pickle.dumps(data)
    
    def _decompress_data(self, data: bytes, compressed: bool) -> Any:
        """Decompress data"""
        try:
            if compressed:
                decompressed = gzip.decompress(data)
                return pickle.loads(decompressed)
            return pickle.loads(data)
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            return None
    
    async def get(self, query: str, user_id: str, endpoint: str) -> Optional[Any]:
        """Get cached response"""
        cache_key = self._generate_cache_key(query, user_id, endpoint)
        
        # Try Redis first
        if self.redis_client:
            try:
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    # Parse metadata
                    metadata_key = f"{cache_key}:metadata"
                    metadata = await self.redis_client.get(metadata_key)
                    
                    if metadata:
                        metadata_dict = json.loads(metadata.decode())
                        entry = CacheEntry(
                            key=cache_key,
                            value=self._decompress_data(cached_data, metadata_dict.get("compressed", False)),
                            created_at=datetime.fromisoformat(metadata_dict["created_at"]),
                            accessed_at=datetime.now(),
                            access_count=metadata_dict["access_count"] + 1,
                            ttl=metadata_dict["ttl"],
                            level=CacheLevel(metadata_dict["level"]),
                            compressed=metadata_dict.get("compressed", False),
                            size_bytes=len(cached_data)
                        )
                        
                        # Update access metadata
                        await self.redis_client.setex(
                            metadata_key,
                            entry.ttl,
                            json.dumps(entry.to_dict())
                        )
                        
                        self.metrics["hits"] += 1
                        logger.debug(f"Cache HIT: {cache_key}")
                        return entry.value
            except Exception as e:
                logger.error(f"Redis get error: {e}")
                self.metrics["redis_errors"] += 1
        
        # Fallback to in-memory cache
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if datetime.now() - entry.created_at < timedelta(seconds=entry.ttl):
                entry.accessed_at = datetime.now()
                entry.access_count += 1
                self.metrics["hits"] += 1
                logger.debug(f"Memory cache HIT: {cache_key}")
                return entry.value
            else:
                # Expired, remove from memory
                del self.memory_cache[cache_key]
                self.current_memory_size -= entry.size_bytes
        
        self.metrics["misses"] += 1
        logger.debug(f"Cache MISS: {cache_key}")
        return None
    
    async def set(
        self,
        query: str,
        user_id: str,
        endpoint: str,
        value: Any,
        ttl: Optional[int] = None,
        level: Optional[CacheLevel] = None
    ) -> bool:
        """Set cached response"""
        cache_key = self._generate_cache_key(query, user_id, endpoint)
        
        # Get cache configuration
        pattern_config = self.cache_patterns.get(endpoint, {"ttl": 3600, "level": CacheLevel.WARM})
        ttl = ttl or pattern_config["ttl"]
        level = level or CacheLevel(pattern_config["level"])
        
        # Compress if needed
        compressed_data = self._compress_data(value)
        compressed = len(compressed_data) < len(pickle.dumps(value))
        
        entry = CacheEntry(
            key=cache_key,
            value=value,
            created_at=datetime.now(),
            accessed_at=datetime.now(),
            access_count=1,
            ttl=ttl,
            level=level,
            compressed=compressed,
            size_bytes=len(compressed_data)
        )
        
        # Store in Redis
        if self.redis_client:
            try:
                # Store data
                await self.redis_client.setex(cache_key, ttl, compressed_data)
                
                # Store metadata
                metadata_key = f"{cache_key}:metadata"
                await self.redis_client.setex(
                    metadata_key,
                    ttl,
                    json.dumps(entry.to_dict())
                )
                
                logger.debug(f"Redis cache SET: {cache_key}")
                return True
            except Exception as e:
                logger.error(f"Redis set error: {e}")
                self.metrics["redis_errors"] += 1
        
        # Fallback to in-memory cache
        try:
            # Check memory limit
            if self.current_memory_size + entry.size_bytes > self.max_memory_size:
                await self._evict_entries()
            
            self.memory_cache[cache_key] = entry
            self.current_memory_size += entry.size_bytes
            logger.debug(f"Memory cache SET: {cache_key}")
            return True
        except Exception as e:
            logger.error(f"Memory cache set error: {e}")
            return False
    
    async def _evict_entries(self) -> None:
        """Evict entries based on cache strategy"""
        if not self.memory_cache:
            return
        
        if self.cache_strategy == CacheStrategy.LRU:
            # Remove least recently used
            oldest_key = min(
                self.memory_cache.keys(),
                key=lambda k: self.memory_cache[k].accessed_at
            )
        elif self.cache_strategy == CacheStrategy.LFU:
            # Remove least frequently used
            oldest_key = min(
                self.memory_cache.keys(),
                key=lambda k: self.memory_cache[k].access_count
            )
        else:  # TTL or HYBRID
            # Remove expired entries first, then oldest
            now = datetime.now()
            expired_keys = [
                k for k, v in self.memory_cache.items()
                if now - v.created_at > timedelta(seconds=v.ttl)
            ]
            
            if expired_keys:
                oldest_key = expired_keys[0]
            else:
                oldest_key = min(
                    self.memory_cache.keys(),
                    key=lambda k: self.memory_cache[k].created_at
                )
        
        # Remove entry
        entry = self.memory_cache.pop(oldest_key)
        self.current_memory_size -= entry.size_bytes
        self.metrics["evictions"] += 1
        logger.debug(f"Evicted cache entry: {oldest_key}")
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern"""
        invalidated = 0
        
        # Invalidate Redis entries
        if self.redis_client:
            try:
                keys = await self.redis_client.keys(f"*{pattern}*")
                if keys:
                    await self.redis_client.delete(*keys)
                    invalidated += len(keys)
            except Exception as e:
                logger.error(f"Redis invalidation error: {e}")
        
        # Invalidate memory entries
        memory_keys = [k for k in self.memory_cache.keys() if pattern in k]
        for key in memory_keys:
            entry = self.memory_cache.pop(key)
            self.current_memory_size -= entry.size_bytes
            invalidated += 1
        
        logger.info(f"Invalidated {invalidated} cache entries for pattern: {pattern}")
        return invalidated
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.metrics["hits"] + self.metrics["misses"]
        hit_rate = (self.metrics["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hits": self.metrics["hits"],
            "misses": self.metrics["misses"],
            "hit_rate": round(hit_rate, 2),
            "evictions": self.metrics["evictions"],
            "compressions": self.metrics["compressions"],
            "redis_errors": self.metrics["redis_errors"],
            "memory_entries": len(self.memory_cache),
            "memory_size_mb": round(self.current_memory_size / (1024 * 1024), 2),
            "max_memory_mb": round(self.max_memory_size / (1024 * 1024), 2),
            "cache_strategy": self.cache_strategy.value,
            "redis_connected": self.redis_client is not None
        }
    
    async def clear_all(self) -> None:
        """Clear all cache entries"""
        # Clear Redis
        if self.redis_client:
            try:
                await self.redis_client.flushdb()
            except Exception as e:
                logger.error(f"Redis clear error: {e}")
        
        # Clear memory
        self.memory_cache.clear()
        self.current_memory_size = 0
        logger.info("All cache entries cleared")
    
    async def close(self) -> None:
        """Close cache connections"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Cache manager closed")

# Global cache instance
import os

# Get Redis URL from environment or use None for in-memory only
redis_url = os.getenv("REDIS_URL", None)
if redis_url == "redis://localhost:6379" and not os.getenv("REDIS_ENABLED", "false").lower() == "true":
    # If Redis URL is default but Redis is not explicitly enabled, use in-memory
    redis_url = None

cache_manager = AdvancedCacheManager(
    redis_url=redis_url,
    max_memory_size=int(os.getenv("MAX_CACHE_SIZE", "100")) * 1024 * 1024,  # Convert MB to bytes
    compression_threshold=int(os.getenv("COMPRESSION_THRESHOLD", "1024")),
    enable_compression=os.getenv("ENABLE_COMPRESSION", "true").lower() == "true",
    cache_strategy=CacheStrategy.HYBRID,
    enable_metrics=True
)
