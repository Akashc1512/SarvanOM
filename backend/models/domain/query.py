"""
Query Domain Models

This module contains the core query domain models and business logic.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum


class QueryStatus(Enum):
    """Query processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QueryType(Enum):
    """Types of queries."""

    BASIC = "basic"
    COMPREHENSIVE = "comprehensive"
    FACT_CHECK = "fact_check"
    SYNTHESIS = "synthesis"


@dataclass
class QueryContext:
    """Context information for query processing."""

    user_id: str
    session_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    max_tokens: int = 1000
    confidence_threshold: float = 0.8


@dataclass
class QueryResult:
    """Result of query processing."""

    query_id: str
    answer: str
    sources: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    processing_time: float = 0.0
    cache_hit: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Query:
    """Core query domain model."""

    id: str
    text: str
    context: QueryContext
    query_type: QueryType = QueryType.BASIC
    status: QueryStatus = QueryStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    result: Optional[QueryResult] = None

    def __post_init__(self):
        """Validate query after initialization."""
        if not self.text.strip():
            raise ValueError("Query text cannot be empty")

        if len(self.text) > 10000:
            raise ValueError("Query text too long (max 10000 characters)")

    def mark_processing(self):
        """Mark query as processing."""
        self.status = QueryStatus.PROCESSING
        self.updated_at = datetime.now()

    def mark_completed(self, result: QueryResult):
        """Mark query as completed with result."""
        self.status = QueryStatus.COMPLETED
        self.result = result
        self.updated_at = datetime.now()

    def mark_failed(self, error: str):
        """Mark query as failed."""
        self.status = QueryStatus.FAILED
        self.updated_at = datetime.now()
        if self.result is None:
            self.result = QueryResult(
                query_id=self.id, answer=f"Error: {error}", confidence=0.0
            )

    def is_completed(self) -> bool:
        """Check if query is completed."""
        return self.status == QueryStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if query failed."""
        return self.status == QueryStatus.FAILED

    def can_be_processed(self) -> bool:
        """Check if query can be processed."""
        return self.status in [QueryStatus.PENDING, QueryStatus.PROCESSING]
