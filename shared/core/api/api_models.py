"""
API Models for Universal Knowledge Platform API Gateway.

This module defines Pydantic models for API request/response validation
and serialization following MAANG-level standards.

Architecture:
    - Request/Response models for all endpoints
    - Proper validation and error handling
    - Type safety with Pydantic
    - Consistent response formats
    - API versioning support

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    1.0.0 (2024-12-28)
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class HealthStatus(str, Enum):
    """Health status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthResponse(BaseModel):
    """Health check response model."""

    status: HealthStatus
    timestamp: str
    version: str
    uptime: float
    memory_usage: Dict[str, Any]
    cpu_usage: float


class QueryRequest(BaseModel):
    """Query request model."""

    query: str = Field(..., min_length=1, max_length=10000, description="Query text")
    context: Optional[str] = Field(None, max_length=5000, description="Query context")
    user_id: Optional[str] = Field(None, description="User ID")
    session_id: Optional[str] = Field(None, description="Session ID")
    source: Optional[str] = Field(None, description="Query source")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class QueryResponse(BaseModel):
    """Query response model."""

    query_id: str
    status: str
    answer: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    sources: List[str]
    processing_time: float
    timestamp: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class QueryUpdateRequest(BaseModel):
    """Query update request model."""

    answer: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    sources: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class QueryListResponse(BaseModel):
    """Query list response model."""

    queries: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool


class QueryDetailResponse(BaseModel):
    """Query detail response model."""

    query_id: str
    query_text: str
    response_text: str
    confidence: float
    sources: List[str]
    processing_time: float
    created_at: str
    updated_at: str
    user_id: Optional[str] = None
    feedback_rating: Optional[int] = None
    feedback_text: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class QueryStatusResponse(BaseModel):
    """Query status response model."""

    query_id: str
    status: str
    progress: float = Field(..., ge=0.0, le=1.0)
    estimated_completion: Optional[str] = None
    current_step: Optional[str] = None
    error_message: Optional[str] = None


class MetricsResponse(BaseModel):
    """Metrics response model."""

    total_queries: int
    average_response_time: float
    success_rate: float
    active_users: int
    system_health: HealthStatus
    timestamp: str
    period: str


class AnalyticsResponse(BaseModel):
    """Analytics response model."""

    user_activity: Dict[str, Any]
    query_trends: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    system_usage: Dict[str, Any]
    timestamp: str


class FeedbackRequest(BaseModel):
    """Feedback request model."""

    query_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(
        None, max_length=1000, description="Feedback comment"
    )
    category: Optional[str] = Field(None, description="Feedback category")
    metadata: Optional[Dict[str, Any]] = None


class FeedbackResponse(BaseModel):
    """Feedback response model."""

    feedback_id: str
    query_id: str
    rating: int
    comment: Optional[str] = None
    category: Optional[str] = None
    created_at: str
    user_id: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request model."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    remember_me: Optional[bool] = False
    device_info: Optional[Dict[str, Any]] = None


class RegisterRequest(BaseModel):
    """Registration request model."""

    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=100)
    role: str = Field(default="user", description="User role")


class AuthResponse(BaseModel):
    """Authentication response model."""

    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    role: str
    permissions: List[str]
    expires_in: int
    refresh_token: Optional[str] = None


class APIKeyResponse(BaseModel):
    """API key response model."""

    api_key: str
    user_id: str
    role: str
    permissions: List[str]
    description: str
    created_at: str
    expires_at: Optional[str] = None
    last_used_at: Optional[str] = None


class ExpertReviewRequest(BaseModel):
    """Expert review request model."""

    review_id: str
    expert_id: str
    verdict: str = Field(..., description="Review verdict")
    notes: str = Field(..., max_length=5000, description="Review notes")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level")


class ExpertReviewResponse(BaseModel):
    """Expert review response model."""

    review_id: str
    status: str
    expert_id: str
    verdict: str
    notes: str
    confidence: float
    completed_at: str
    metadata: Optional[Dict[str, Any]] = None


class TaskRequest(BaseModel):
    """Task generation request model."""

    task_type: str = Field(..., description="Type of task to generate")
    description: str = Field(..., max_length=1000, description="Task description")
    priority: Optional[str] = Field("medium", description="Task priority")
    assignee: Optional[str] = Field(None, description="Task assignee")
    due_date: Optional[str] = Field(None, description="Task due date")
    metadata: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    """Task generation response model."""

    task_id: str
    status: str
    tasks: List[Dict[str, Any]]
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


class IntegrationStatus(BaseModel):
    """Integration status model."""

    name: str
    status: str
    version: str
    last_check: str
    response_time: Optional[float] = None
    error_message: Optional[str] = None


class IntegrationsResponse(BaseModel):
    """Integrations response model."""

    status: str
    integrations: Dict[str, IntegrationStatus]
    timestamp: str
    overall_health: HealthStatus


# Validator models
class QueryRequestValidator(BaseModel):
    """Query request validator with enhanced validation."""

    query: str = Field(..., min_length=1, max_length=10000)
    context: Optional[str] = Field(None, max_length=5000)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @field_validator("query")
    @classmethod
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class FeedbackRequestValidator(BaseModel):
    """Feedback request validator."""

    query_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class SearchRequestValidator(BaseModel):
    """Search request validator."""

    query: str = Field(..., min_length=1, max_length=1000)
    filters: Optional[Dict[str, Any]] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: Optional[str] = Field(None, pattern="^(asc|desc)$")


class AnalyticsRequestValidator(BaseModel):
    """Analytics request validator."""

    start_date: Optional[str] = None
    end_date: Optional[str] = None
    metrics: List[str] = Field(default_factory=list)
    group_by: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None


class ConfigUpdateValidator(BaseModel):
    """Configuration update validator."""

    key: str = Field(..., min_length=1)
    value: Any
    description: Optional[str] = None
    category: Optional[str] = None
