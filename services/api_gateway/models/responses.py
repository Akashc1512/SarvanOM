"""
Response Models for API Gateway

This module contains all response models used by the API gateway endpoints.
Models are organized by functionality and follow Pydantic validation patterns.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# Authentication Responses
class AuthResponse(BaseModel):
    """Response model for authentication operations."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    api_key: str = Field(..., description="API key for service access")
    user_id: str = Field(..., description="User identifier")
    role: str = Field(..., description="User role")
    permissions: List[str] = Field(default_factory=list, description="User permissions")
    expires_at: Optional[datetime] = Field(None, description="Token expiration time")


class APIKeyResponse(BaseModel):
    """Response model for API key operations."""
    api_key: str = Field(..., description="Generated API key")
    user_id: str = Field(..., description="User identifier")
    role: str = Field(..., description="User role")
    permissions: List[str] = Field(default_factory=list, description="Key permissions")
    description: str = Field(..., description="Key description")
    created_at: str = Field(..., description="Creation timestamp")


# Query Responses
class QueryResponse(BaseModel):
    """Base response model for query processing."""
    query_id: str = Field(..., description="Unique query identifier")
    status: str = Field(..., description="Query processing status")
    result: Optional[Dict[str, Any]] = Field(None, description="Query result")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Query metadata")
    processing_time: float = Field(..., description="Processing time in seconds")
    created_at: datetime = Field(..., description="Creation timestamp")


class ComprehensiveQueryResponse(BaseModel):
    """Response model for comprehensive query processing."""
    query_id: str = Field(..., description="Unique query identifier")
    status: str = Field(..., description="Query processing status")
    search_results: Optional[Dict[str, Any]] = Field(None, description="Search results")
    fact_check_results: Optional[Dict[str, Any]] = Field(None, description="Fact checking results")
    synthesis_results: Optional[Dict[str, Any]] = Field(None, description="Synthesis results")
    citations: Optional[List[Dict[str, Any]]] = Field(None, description="Source citations")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")
    processing_time: float = Field(..., description="Processing time in seconds")
    created_at: datetime = Field(..., description="Creation timestamp")


# Feedback Responses
class FeedbackResponse(BaseModel):
    """Response model for feedback operations."""
    feedback_id: str = Field(..., description="Unique feedback identifier")
    query_id: str = Field(..., description="Related query identifier")
    status: str = Field(..., description="Feedback processing status")
    message: str = Field(..., description="Feedback confirmation message")
    created_at: datetime = Field(..., description="Creation timestamp")


# Expert Review Responses
class ExpertReviewResponse(BaseModel):
    """Response model for expert review operations."""
    review_id: str = Field(..., description="Unique review identifier")
    status: str = Field(..., description="Review status")
    expert_id: str = Field(..., description="Expert identifier")
    verdict: str = Field(..., description="Review verdict")
    notes: str = Field(..., description="Expert notes")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Expert confidence")
    completed_at: str = Field(..., description="Completion timestamp")


# Query Management Responses
class QueryListResponse(BaseModel):
    """Response model for query listing."""
    queries: List[Dict[str, Any]] = Field(..., description="List of queries")
    total_count: int = Field(..., description="Total number of queries")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")


class QueryDetailResponse(BaseModel):
    """Response model for query details."""
    query_id: str = Field(..., description="Unique query identifier")
    query_text: str = Field(..., description="Original query text")
    status: str = Field(..., description="Query status")
    result: Optional[Dict[str, Any]] = Field(None, description="Query result")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Query metadata")
    processing_time: float = Field(..., description="Processing time in seconds")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    user_id: Optional[str] = Field(None, description="User identifier")
    tags: List[str] = Field(default_factory=list, description="Query tags")
    notes: Optional[str] = Field(None, description="User notes")


class QueryStatusResponse(BaseModel):
    """Response model for query status."""
    query_id: str = Field(..., description="Unique query identifier")
    status: str = Field(..., description="Current status")
    progress: float = Field(..., ge=0.0, le=1.0, description="Processing progress")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    current_step: Optional[str] = Field(None, description="Current processing step")
    error_message: Optional[str] = Field(None, description="Error message if failed")


# Health and System Responses
class HealthResponse(BaseModel):
    """Response model for health checks."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(..., description="Health check timestamp")
    uptime: float = Field(..., description="Service uptime in seconds")
    memory_usage: Dict[str, Any] = Field(..., description="Memory usage statistics")
    cpu_usage: float = Field(..., description="CPU usage percentage")
    active_connections: int = Field(..., description="Active connections count")


class MetricsResponse(BaseModel):
    """Response model for system metrics."""
    service_name: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(..., description="Metrics timestamp")
    metrics: Dict[str, Any] = Field(..., description="System metrics")
    performance: Dict[str, Any] = Field(..., description="Performance metrics")
    resources: Dict[str, Any] = Field(..., description="Resource usage")


class SystemDiagnosticsResponse(BaseModel):
    """Response model for system diagnostics."""
    system_info: Dict[str, Any] = Field(..., description="System information")
    service_status: Dict[str, Any] = Field(..., description="Service status")
    dependencies: Dict[str, Any] = Field(..., description="Dependency status")
    performance: Dict[str, Any] = Field(..., description="Performance metrics")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Recent errors")
    warnings: List[Dict[str, Any]] = Field(default_factory=list, description="Recent warnings")


# Analytics Responses
class AnalyticsResponse(BaseModel):
    """Response model for analytics data."""
    period: str = Field(..., description="Analytics period")
    metrics: Dict[str, Any] = Field(..., description="Analytics metrics")
    trends: Dict[str, Any] = Field(..., description="Trend data")
    top_queries: List[Dict[str, Any]] = Field(..., description="Top queries")
    user_activity: Dict[str, Any] = Field(..., description="User activity data")


# Security Responses
class SecurityStatusResponse(BaseModel):
    """Response model for security status."""
    security_level: str = Field(..., description="Current security level")
    threats_detected: int = Field(..., description="Number of threats detected")
    last_scan: datetime = Field(..., description="Last security scan")
    vulnerabilities: List[Dict[str, Any]] = Field(default_factory=list, description="Security vulnerabilities")
    recommendations: List[str] = Field(default_factory=list, description="Security recommendations")


# Integration Responses
class IntegrationStatusResponse(BaseModel):
    """Response model for integration status."""
    integrations: Dict[str, Any] = Field(..., description="Integration status")
    health_checks: Dict[str, Any] = Field(..., description="Health check results")
    last_updated: datetime = Field(..., description="Last update timestamp")


# Agent Responses
class AgentResponse(BaseModel):
    """Base response model for agent operations."""
    agent_id: str = Field(..., description="Agent identifier")
    status: str = Field(..., description="Operation status")
    result: Optional[Dict[str, Any]] = Field(None, description="Operation result")
    processing_time: float = Field(..., description="Processing time in seconds")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Operation metadata")


# WebSocket Responses
class WebSocketMessage(BaseModel):
    """Response model for WebSocket messages."""
    message_type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(..., description="Message data")
    timestamp: datetime = Field(..., description="Message timestamp")
    user_id: Optional[str] = Field(None, description="User identifier")


# Error Responses
class ErrorResponse(BaseModel):
    """Response model for error conditions."""
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(..., description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier")


# Generic Responses
class GenericResponse(BaseModel):
    """Generic response model for flexible endpoints."""
    status: str = Field(..., description="Operation status")
    data: Dict[str, Any] = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Response message")
    timestamp: datetime = Field(..., description="Response timestamp") 