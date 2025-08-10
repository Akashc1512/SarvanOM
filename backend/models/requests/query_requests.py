"""
Query Request Models

This module contains Pydantic models for query-related API requests.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional, List
from datetime import datetime


class QueryRequest(BaseModel):
    """Basic query request model."""

    query: str = Field(
        ..., min_length=1, max_length=10000, description="The query text"
    )
    session_id: Optional[str] = Field(None, description="Session identifier")
    max_tokens: int = Field(
        1000, ge=1, le=10000, description="Maximum tokens for response"
    )
    confidence_threshold: float = Field(
        0.8, ge=0.0, le=1.0, description="Confidence threshold"
    )
    cache_enabled: bool = Field(True, description="Enable response caching")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v):
        """Validate query text."""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class ComprehensiveQueryRequest(BaseModel):
    """Comprehensive query request model."""

    query: str = Field(
        ..., min_length=1, max_length=10000, description="The query text"
    )
    session_id: Optional[str] = Field(None, description="Session identifier")
    options: Dict[str, Any] = Field(
        default_factory=dict, description="Processing options"
    )
    include_sources: bool = Field(True, description="Include source information")
    include_confidence: bool = Field(True, description="Include confidence scores")
    include_alternatives: bool = Field(False, description="Include alternative answers")
    max_tokens: int = Field(
        2000, ge=1, le=20000, description="Maximum tokens for response"
    )
    confidence_threshold: float = Field(
        0.8, ge=0.0, le=1.0, description="Confidence threshold"
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v):
        """Validate query text."""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class QueryUpdateRequest(BaseModel):
    """Query update request model."""

    query: Optional[str] = Field(
        None, min_length=1, max_length=10000, description="Updated query text"
    )
    max_tokens: Optional[int] = Field(
        None, ge=1, le=10000, description="Updated max tokens"
    )
    confidence_threshold: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Updated confidence threshold"
    )
    cache_enabled: Optional[bool] = Field(None, description="Updated cache setting")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v):
        """Validate query text if provided."""
        if v is not None and not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip() if v else v


class QueryListRequest(BaseModel):
    """Query list request model."""

    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Page size")
    user_filter: Optional[str] = Field(None, description="Filter by user ID")
    status_filter: Optional[str] = Field(None, description="Filter by status")
    date_from: Optional[datetime] = Field(None, description="Filter from date")
    date_to: Optional[datetime] = Field(None, description="Filter to date")


class QueryReprocessRequest(BaseModel):
    """Query reprocess request model."""

    force_reprocess: bool = Field(
        False, description="Force reprocessing even if cached"
    )
    use_different_agents: bool = Field(
        False, description="Use different agent combination"
    )
    agent_preferences: Optional[List[str]] = Field(
        None, description="Preferred agent IDs"
    )
