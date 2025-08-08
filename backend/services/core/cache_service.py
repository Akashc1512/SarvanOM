"""
Cache Service

This module provides caching functionality for the application.
"""

import asyncio
import json
import logging
import time
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheService:
    """Provides caching functionality for the application."""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = 3600  # 1 hour default TTL
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            if key not in self._cache:
                return None
            
            cache_entry = self._cache[key]
            
            # Check if entry has expired
            if self._is_expired(cache_entry):
                await self.delete(key)
                return None
            
            logger.debug(f"Cache hit for key: {key}")
            return cache_entry["value"]
            
        except Exception as e:
            logger.error(f"Error getting from cache: {e}", exc_info=True)
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        try:
            ttl = ttl or self._default_ttl
            expiry_time = datetime.now() + timedelta(seconds=ttl)
            
            self._cache[key] = {
                "value": value,
                "expiry": expiry_time,
                "created_at": datetime.now()
            }
            
            logger.debug(f"Cache set for key: {key} with TTL: {ttl}s")
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache: {e}", exc_info=True)
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Cache deleted for key: {key}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}", exc_info=True)
            return False
    
    async def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            self._cache.clear()
            logger.info("Cache cleared")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}", exc_info=True)
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            total_entries = len(self._cache)
            expired_entries = 0
            total_size = 0
            
            for key, entry in self._cache.items():
                if self._is_expired(entry):
                    expired_entries += 1
                else:
                    # Estimate size (rough calculation)
                    total_size += len(str(entry["value"]))
            
            return {
                "total_entries": total_entries,
                "expired_entries": expired_entries,
                "active_entries": total_entries - expired_entries,
                "total_size_bytes": total_size,
                "default_ttl": self._default_ttl
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}", exc_info=True)
            return {}
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry has expired."""
        expiry_time = cache_entry.get("expiry")
        if not expiry_time:
            return True
        
        return datetime.now() > expiry_time
    
    async def cleanup_expired(self) -> int:
        """Remove expired entries from cache."""
        try:
            expired_keys = []
            
            for key, entry in self._cache.items():
                if self._is_expired(entry):
                    expired_keys.append(key)
            
            for key in expired_keys:
                await self.delete(key)
            
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            return len(expired_keys)
            
        except Exception as e:
            logger.error(f"Error cleaning up expired cache entries: {e}", exc_info=True)
            return 0
    
    async def get_with_fallback(
        self, 
        key: str, 
        fallback_func, 
        ttl: Optional[int] = None,
        *args, 
        **kwargs
    ) -> Any:
        """Get from cache or execute fallback function."""
        # Try to get from cache first
        cached_value = await self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Execute fallback function
        try:
            if asyncio.iscoroutinefunction(fallback_func):
                value = await fallback_func(*args, **kwargs)
            else:
                value = fallback_func(*args, **kwargs)
            
            # Cache the result
            await self.set(key, value, ttl)
            
            return value
            
        except Exception as e:
            logger.error(f"Error in cache fallback function: {e}", exc_info=True)
            raise
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern."""
        try:
            import re
            pattern_re = re.compile(pattern)
            invalidated_count = 0
            
            keys_to_delete = []
            for key in self._cache.keys():
                if pattern_re.match(key):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                await self.delete(key)
                invalidated_count += 1
            
            logger.info(f"Invalidated {invalidated_count} cache entries matching pattern: {pattern}")
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Error invalidating cache pattern: {e}", exc_info=True)
            return 0 