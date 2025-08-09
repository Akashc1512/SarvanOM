"""
Cache Store Model - Universal Knowledge Platform
PostgreSQL-based cache storage using JSONB fields.

This module defines the database model for storing cache data
using PostgreSQL JSONB fields for efficient caching operations.

Features:
- JSONB storage for flexible cache data
- Automatic expiration management
- Indexed queries for performance
- TTL-based cache invalidation
- Zero-budget alternative to Redis

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    1.0.0 (2024-12-28)
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

from sqlalchemy import Column, String, DateTime, Index, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base

from shared.models.models import Base

import logging

logger = logging.getLogger(__name__)


class CacheStore(Base):
    """
    Cache storage using PostgreSQL JSONB.

    Stores cache data with automatic expiration management
    and efficient querying for zero-budget caching.
    """

    __tablename__ = "cache_store"
    __table_args__ = (
        Index("idx_cache_store_cache_key", "cache_key"),
        Index("idx_cache_store_expires_at", "expires_at"),
        Index("idx_cache_store_data_gin", "data", postgresql_using="gin"),
        {"comment": "Cache storage with JSONB data and TTL"},
    )

    # Primary key
    cache_key = Column(
        String(500),
        primary_key=True,
        nullable=False,
        comment="Unique cache key identifier",
    )

    # JSONB field for storing cache data
    data = Column(JSONB, nullable=False, comment="Cache data as JSONB")

    # Timestamp for cache creation
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="Cache creation timestamp",
    )

    # Timestamp for cache expiration
    expires_at = Column(
        DateTime(timezone=True), nullable=True, comment="Cache expiration timestamp"
    )

    def __repr__(self) -> str:
        """String representation of the cache store."""
        return (
            f"<CacheStore(cache_key='{self.cache_key}', expires_at={self.expires_at})>"
        )

    def is_expired(self) -> bool:
        """
        Check if cache entry is expired.

        Returns:
            True if expired, False otherwise
        """
        if not self.expires_at:
            return False

        return datetime.now(timezone.utc) > self.expires_at

    def set_expiration(self, ttl_minutes: int) -> None:
        """
        Set expiration time based on TTL.

        Args:
            ttl_minutes: Time to live in minutes
        """
        if ttl_minutes > 0:
            self.expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=ttl_minutes
            )
        else:
            self.expires_at = None

    def get_remaining_ttl_minutes(self) -> Optional[int]:
        """
        Get remaining TTL in minutes.

        Returns:
            Remaining minutes or None if no expiration
        """
        if not self.expires_at:
            return None

        remaining = self.expires_at - datetime.now(timezone.utc)
        if remaining.total_seconds() <= 0:
            return 0

        return int(remaining.total_seconds() / 60)

    def to_dict(self) -> Dict[str, Any]:
        """Convert cache store to dictionary representation."""
        return {
            "cache_key": self.cache_key,
            "data": self.data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_expired": self.is_expired(),
            "remaining_ttl_minutes": self.get_remaining_ttl_minutes(),
        }
