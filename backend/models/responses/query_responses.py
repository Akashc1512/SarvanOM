"""
Query Response Models

This module contains Pydantic models for query-related API responses.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class QueryResponse(BaseModel):
    """Basic query response model."""

    query_id: str = Field(..., description="Unique query identifier")
    answer: str = Field(..., description="Generated answer")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    processing_time: float = Field(
        ..., ge=0.0, description="Processing time in seconds"
    )
    cache_hit: bool = Field(False, description="Whether response was from cache")
    created_at: datetime = Field(..., description="Query creation timestamp")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class ComprehensiveQueryResponse(BaseModel):
    """Comprehensive query response model."""

    query_id: str = Field(..., description="Unique query identifier")
    answer: str = Field(..., description="Generated answer")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    processing_time: float = Field(
        ..., ge=0.0, description="Processing time in seconds"
    )
    cache_hit: bool = Field(False, description="Whether response was from cache")
    sources: List[Dict[str, Any]] = Field(
        default_factory=list, description="Source information"
    )
    alternatives: List[Dict[str, Any]] = Field(
        default_factory=list, description="Alternative answers"
    )
    quality_metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Quality assessment"
    )
    created_at: datetime = Field(..., description="Query creation timestamp")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class QueryListResponse(BaseModel):
    """Query list response model."""

    queries: List[Dict[str, Any]] = Field(..., description="List of queries")
    total_count: int = Field(..., ge=0, description="Total number of queries")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Page size")
    total_pages: int = Field(..., ge=0, description="Total number of pages")


class QueryDetailResponse(BaseModel):
    """Query detail response model."""

    query_id: str = Field(..., description="Unique query identifier")
    query: str = Field(..., description="Original query text")
    answer: str = Field(..., description="Generated answer")
    status: str = Field(..., description="Query status")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    processing_time: float = Field(
        ..., ge=0.0, description="Processing time in seconds"
    )
    cache_hit: bool = Field(False, description="Whether response was from cache")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    created_at: datetime = Field(..., description="Query creation timestamp")
    updated_at: datetime = Field(..., description="Query update timestamp")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class QueryStatusResponse(BaseModel):
    """Query status response model."""

    query_id: str = Field(..., description="Unique query identifier")
    status: str = Field(..., description="Query status")
    progress: float = Field(..., ge=0.0, le=1.0, description="Processing progress")
    estimated_completion: Optional[datetime] = Field(
        None, description="Estimated completion time"
    )
    current_step: Optional[str] = Field(None, description="Current processing step")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Query creation timestamp")
    updated_at: datetime = Field(..., description="Query update timestamp")


class QueryReprocessResponse(BaseModel):
    """Query reprocess response model."""

    query_id: str = Field(..., description="Unique query identifier")
    reprocessed: bool = Field(..., description="Whether query was reprocessed")
    new_answer: Optional[str] = Field(None, description="New answer if reprocessed")
    processing_time: float = Field(
        ..., ge=0.0, description="Processing time in seconds"
    )
    cache_hit: bool = Field(False, description="Whether response was from cache")
    reprocessed_at: datetime = Field(..., description="Reprocessing timestamp")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Error type")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Error timestamp"
    )
    request_id: Optional[str] = Field(None, description="Request identifier")
