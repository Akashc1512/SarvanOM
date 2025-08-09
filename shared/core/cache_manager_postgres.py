"""
Cache Manager PostgreSQL - Universal Knowledge Platform
PostgreSQL-based cache management using JSONB fields.

This module implements a cache manager that uses PostgreSQL JSONB
fields to store cache data, replacing Redis for zero-budget caching.

Features:
- PostgreSQL JSONB storage for cache data
- Automatic TTL management with expiration
- Efficient querying with GIN indexes
- Cache invalidation and cleanup
- Zero-budget alternative to Redis

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    1.0.0 (2024-12-28)
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from shared.core.database import DatabaseService, get_database_service
from shared.models.cache_store import CacheStore

logger = logging.getLogger(__name__)


class CacheManagerPostgres:
    """
    PostgreSQL-based cache manager.

    Manages cache data using PostgreSQL JSONB fields with
    automatic TTL management and efficient querying.
    """

    def __init__(self, database_service: Optional[DatabaseService] = None):
        """
        Initialize the PostgreSQL cache manager.

        Args:
            database_service: Database service instance (auto-initialized if None)
        """
        self.db_service = database_service or get_database_service()
        self.default_ttl_minutes = 60  # 1 hour default TTL
        logger.info("CacheManagerPostgres initialized")

    async def set_cache(
        self, key: str, data: Dict[str, Any], ttl_minutes: Optional[int] = None
    ) -> bool:
        """
        Set cache data with expiration.

        Args:
            key: Cache key
            data: Data to cache
            ttl_minutes: Time to live in minutes (defaults to default_ttl_minutes)

        Returns:
            True if successfully cached, False otherwise
        """
        if ttl_minutes is None:
            ttl_minutes = self.default_ttl_minutes

        try:
            with self.db_service.get_session() as session:
                # Create or update cache entry
                cache_entry = await self._get_or_create_cache_entry(session, key)

                # Set data and expiration
                cache_entry.data = data
                cache_entry.set_expiration(ttl_minutes)

                # Save to database
                session.commit()

                logger.debug(f"Cached data for key: {key} (TTL: {ttl_minutes} minutes)")
                return True

        except Exception as e:
            logger.error(f"Failed to set cache for key {key}: {e}")
            return False

    async def get_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached data if not expired.

        Args:
            key: Cache key

        Returns:
            Cached data or None if not found/expired
        """
        try:
            with self.db_service.get_session() as session:
                # Get cache entry
                cache_entry = await self._get_cache_entry(session, key)

                if not cache_entry:
                    return None

                # Check if expired
                if cache_entry.is_expired():
                    logger.debug(f"Cache expired for key: {key}")
                    await self.delete_cache(key)
                    return None

                logger.debug(f"Cache hit for key: {key}")
                return cache_entry.data

        except Exception as e:
            logger.error(f"Failed to get cache for key {key}: {e}")
            return None

    async def delete_cache(self, key: str) -> bool:
        """
        Delete specific cache entry.

        Args:
            key: Cache key to delete

        Returns:
            True if successfully deleted, False otherwise
        """
        try:
            with self.db_service.get_session() as session:
                # Delete cache entry
                result = session.execute(
                    delete(CacheStore).where(CacheStore.cache_key == key)
                )
                session.commit()

                deleted_count = result.rowcount
                if deleted_count > 0:
                    logger.debug(f"Deleted cache for key: {key}")
                    return True
                else:
                    logger.debug(f"No cache found for key: {key}")
                    return False

        except Exception as e:
            logger.error(f"Failed to delete cache for key {key}: {e}")
            return False

    async def clear_expired_cache(self) -> int:
        """
        Clear all expired cache entries.

        Returns:
            Number of expired entries cleared
        """
        try:
            with self.db_service.get_session() as session:
                # Delete expired cache entries
                result = session.execute(
                    delete(CacheStore).where(
                        and_(
                            CacheStore.expires_at.isnot(None),
                            CacheStore.expires_at < datetime.now(timezone.utc),
                        )
                    )
                )
                session.commit()

                cleared_count = result.rowcount
                if cleared_count > 0:
                    logger.info(f"Cleared {cleared_count} expired cache entries")

                return cleared_count

        except Exception as e:
            logger.error(f"Failed to clear expired cache: {e}")
            return 0

    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        try:
            with self.db_service.get_session() as session:
                # Get total cache entries
                total_result = session.execute(select(func.count(CacheStore.cache_key)))
                total_entries = total_result.scalar() or 0

                # Get expired cache entries
                expired_result = session.execute(
                    select(func.count(CacheStore.cache_key)).where(
                        and_(
                            CacheStore.expires_at.isnot(None),
                            CacheStore.expires_at < datetime.now(timezone.utc),
                        )
                    )
                )
                expired_entries = expired_result.scalar() or 0

                # Get active cache entries
                active_entries = total_entries - expired_entries

                return {
                    "total_entries": total_entries,
                    "active_entries": active_entries,
                    "expired_entries": expired_entries,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {
                "total_entries": 0,
                "active_entries": 0,
                "expired_entries": 0,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def get_all_cache_keys(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all cache keys with their metadata.

        Args:
            limit: Maximum number of keys to return

        Returns:
            List of cache key metadata
        """
        try:
            with self.db_service.get_session() as session:
                # Query all cache entries with metadata
                query = (
                    select(
                        CacheStore.cache_key,
                        CacheStore.created_at,
                        CacheStore.expires_at,
                    )
                    .order_by(CacheStore.created_at.desc())
                    .limit(limit)
                )

                result = session.execute(query)
                cache_keys = []

                for row in result:
                    cache_keys.append(
                        {
                            "cache_key": row.cache_key,
                            "created_at": (
                                row.created_at.isoformat() if row.created_at else None
                            ),
                            "expires_at": (
                                row.expires_at.isoformat() if row.expires_at else None
                            ),
                            "is_expired": row.expires_at
                            and row.expires_at < datetime.now(timezone.utc),
                        }
                    )

                return cache_keys

        except Exception as e:
            logger.error(f"Failed to get cache keys: {e}")
            return []

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check of the cache manager.

        Returns:
            Dictionary with health status and statistics
        """
        try:
            stats = await self.get_cache_stats()

            return {
                "status": "healthy",
                "total_entries": stats["total_entries"],
                "active_entries": stats["active_entries"],
                "expired_entries": stats["expired_entries"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def generate_cache_key(self, *args, **kwargs) -> str:
        """
        Generate a cache key from arguments.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Generated cache key
        """
        # Create a string representation of arguments
        key_parts = []

        # Add positional arguments
        for arg in args:
            key_parts.append(str(arg))

        # Add keyword arguments (sorted for consistency)
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")

        # Create hash of the combined string
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    async def _get_or_create_cache_entry(
        self, session: Session, key: str
    ) -> CacheStore:
        """
        Get existing cache entry or create a new one.

        Args:
            session: Database session
            key: Cache key

        Returns:
            CacheStore instance
        """
        # Try to get existing cache entry
        cache_entry = await self._get_cache_entry(session, key)

        if not cache_entry:
            # Create new cache entry
            cache_entry = CacheStore(cache_key=key)
            session.add(cache_entry)
            logger.debug(f"Created new cache entry for key: {key}")

        return cache_entry

    async def _get_cache_entry(
        self, session: Session, key: str
    ) -> Optional[CacheStore]:
        """
        Get cache entry by key.

        Args:
            session: Database session
            key: Cache key

        Returns:
            CacheStore instance or None if not found
        """
        result = session.execute(select(CacheStore).where(CacheStore.cache_key == key))
        return result.scalar_one_or_none()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # No cleanup needed for database connections
        pass
