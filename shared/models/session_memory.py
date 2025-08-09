"""
Session Memory Model - Universal Knowledge Platform
PostgreSQL-based session memory storage using JSONB fields.

This module defines the database model for storing session memory
using PostgreSQL JSONB fields for efficient querying and storage.

Features:
- JSONB storage for flexible session data
- Automatic timestamp management
- Indexed queries for performance
- TTL-like behavior with manual cleanup

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    1.0.0 (2024-12-28)
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

from sqlalchemy import Column, String, DateTime, Index, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base

from shared.models.models import Base

import logging

logger = logging.getLogger(__name__)


class SessionMemory(Base):
    """
    Session memory storage using PostgreSQL JSONB.

    Stores conversation history and context for each session
    with automatic timestamp management and TTL-like behavior.
    """

    __tablename__ = "session_memory"
    __table_args__ = (
        Index("idx_session_memory_session_id", "session_id"),
        Index("idx_session_memory_updated_at", "updated_at"),
        Index("idx_session_memory_history_gin", "history", postgresql_using="gin"),
        {"comment": "Session memory storage with JSONB history"},
    )

    # Primary key
    session_id = Column(
        String(255),
        primary_key=True,
        nullable=False,
        comment="Unique session identifier",
    )

    # JSONB field for storing conversation history
    history = Column(
        JSONB,
        nullable=False,
        default=list,
        comment="Conversation history as JSONB array",
    )

    # Timestamp for TTL management
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="Last update timestamp for TTL management",
    )

    def __repr__(self) -> str:
        """String representation of the session memory."""
        return f"<SessionMemory(session_id='{self.session_id}', history_length={len(self.history)})>"

    def add_interaction(
        self, query: str, answer: str, timestamp: Optional[datetime] = None
    ) -> None:
        """
        Add a new interaction to the session history.

        Args:
            query: The user's query
            answer: The system's response
            timestamp: Optional timestamp (defaults to current time)
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        interaction = {
            "query": query,
            "answer": answer,
            "timestamp": timestamp.isoformat(),
        }

        if not self.history:
            self.history = []

        self.history.append(interaction)
        self.updated_at = datetime.now(timezone.utc)

    def get_recent_interactions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent interactions from the session history.

        Args:
            limit: Maximum number of interactions to return

        Returns:
            List of recent interactions sorted by timestamp (newest first)
        """
        if not self.history:
            return []

        # Sort by timestamp (newest first) and return limited results
        sorted_history = sorted(
            self.history, key=lambda x: x.get("timestamp", ""), reverse=True
        )

        return sorted_history[:limit]

    def clear_history(self) -> None:
        """Clear all interaction history for this session."""
        self.history = []
        self.updated_at = datetime.now(timezone.utc)

    def remove_expired_interactions(self, max_age_hours: int = 24) -> int:
        """
        Remove interactions older than the specified age.

        Args:
            max_age_hours: Maximum age in hours for interactions

        Returns:
            Number of interactions removed
        """
        if not self.history:
            return 0

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        original_count = len(self.history)

        # Filter out expired interactions
        self.history = [
            interaction
            for interaction in self.history
            if self._parse_timestamp(interaction.get("timestamp", "")) > cutoff_time
        ]

        removed_count = original_count - len(self.history)
        if removed_count > 0:
            self.updated_at = datetime.now(timezone.utc)

        return removed_count

    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """
        Parse timestamp string to datetime object.

        Args:
            timestamp_str: ISO format timestamp string

        Returns:
            Parsed datetime object
        """
        try:
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            # Return a very old date if parsing fails
            return datetime(1970, 1, 1, tzinfo=timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert session memory to dictionary representation."""
        return {
            "session_id": self.session_id,
            "history": self.history,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "history_length": len(self.history),
        }
