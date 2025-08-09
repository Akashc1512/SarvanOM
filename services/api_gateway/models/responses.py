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
    fact_check_results: Optional[Dict[str, Any]] = Field(
        None, description="Fact checking results"
    )
    synthesis_results: Optional[Dict[str, Any]] = Field(
        None, description="Synthesis results"
    )
    citations: Optional[List[Dict[str, Any]]] = Field(
        None, description="Source citations"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Overall confidence"
    )
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
    estimated_completion: Optional[datetime] = Field(
        None, description="Estimated completion time"
    )
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
    errors: List[Dict[str, Any]] = Field(
        default_factory=list, description="Recent errors"
    )
    warnings: List[Dict[str, Any]] = Field(
        default_factory=list, description="Recent warnings"
    )


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
    vulnerabilities: List[Dict[str, Any]] = Field(
        default_factory=list, description="Security vulnerabilities"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Security recommendations"
    )


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


# SSO Response Models
class UserResponse(BaseModel):
    """Response model for user information."""

    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="Whether user is active")
    created_at: str = Field(..., description="Account creation timestamp")
    last_login: Optional[str] = Field(None, description="Last login timestamp")


class UserStatsResponse(BaseModel):
    """Response model for user statistics."""

    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    new_users_today: int = Field(..., description="New users today")
    new_users_week: int = Field(..., description="New users this week")
    new_users_month: int = Field(..., description="New users this month")
    top_roles: List[Dict[str, Any]] = Field(
        default_factory=list, description="Most common user roles"
    )
    login_stats: Dict[str, Any] = Field(
        default_factory=dict, description="Login statistics"
    )


class OAuthUrlResponse(BaseModel):
    """Response model for OAuth URL generation."""

    provider: str = Field(..., description="OAuth provider")
    authorization_url: str = Field(..., description="Authorization URL")
    redirect_uri: str = Field(..., description="Redirect URI")


# Multi-Tenant Response Models
class TenantResponse(BaseModel):
    """Response model for tenant information."""

    id: str = Field(..., description="Tenant ID")
    name: str = Field(..., description="Tenant name")
    domain: str = Field(..., description="Tenant domain")
    owner_id: str = Field(..., description="Owner user ID")
    tier: str = Field(..., description="Tenant tier")
    status: str = Field(..., description="Tenant status")
    config: "TenantConfigResponse" = Field(..., description="Tenant configuration")
    usage: "TenantUsageResponse" = Field(..., description="Tenant usage")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


class TenantConfigResponse(BaseModel):
    """Response model for tenant configuration."""

    features_enabled: List[str] = Field(
        default_factory=list, description="Enabled features"
    )
    custom_settings: Dict[str, Any] = Field(
        default_factory=dict, description="Custom settings"
    )
    api_rate_limit: int = Field(..., description="API rate limit")
    storage_limit_gb: float = Field(..., description="Storage limit in GB")


class TenantUsageResponse(BaseModel):
    """Response model for tenant usage statistics."""

    api_calls_this_month: int = Field(..., description="API calls this month")
    storage_used_gb: float = Field(..., description="Storage used in GB")
    active_users: int = Field(..., description="Number of active users")
    last_activity: Optional[str] = Field(None, description="Last activity timestamp")


class TenantListResponse(BaseModel):
    """Response model for tenant listing."""

    tenants: List[TenantResponse] = Field(..., description="List of tenants")
    total: int = Field(..., description="Total number of tenants")


class TenantStatsResponse(BaseModel):
    """Response model for tenant statistics."""

    total_tenants: int = Field(..., description="Total number of tenants")
    active_tenants: int = Field(..., description="Number of active tenants")
    suspended_tenants: int = Field(..., description="Number of suspended tenants")
    tier_distribution: Dict[str, int] = Field(
        default_factory=dict, description="Tenants by tier"
    )
    total_api_calls: int = Field(..., description="Total API calls across all tenants")
    total_storage_used: float = Field(
        ..., description="Total storage used across all tenants"
    )


# Analytics Response Models
class AnalyticsDataResponse(BaseModel):
    """Response model for analytics data collection."""

    metric_name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    tenant_id: str = Field(..., description="Tenant ID")
    timestamp: str = Field(..., description="Data collection timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class UsageAnalyticsResponse(BaseModel):
    """Response model for usage analytics."""

    tenant_id: str = Field(..., description="Tenant ID")
    timeframe: str = Field(..., description="Analytics timeframe")
    total_api_calls: int = Field(..., description="Total API calls")
    unique_users: int = Field(..., description="Number of unique users")
    popular_features: List[Dict[str, Any]] = Field(
        default_factory=list, description="Popular features"
    )
    usage_trends: Dict[str, Any] = Field(
        default_factory=dict, description="Usage trends"
    )
    peak_usage_times: List[Dict[str, Any]] = Field(
        default_factory=list, description="Peak usage times"
    )
    error_rates: Dict[str, Any] = Field(default_factory=dict, description="Error rates")
    response_times: Dict[str, Any] = Field(
        default_factory=dict, description="Response times"
    )
    data_points: List[Dict[str, Any]] = Field(
        default_factory=list, description="Data points"
    )


class PerformanceAnalyticsResponse(BaseModel):
    """Response model for performance analytics."""

    tenant_id: str = Field(..., description="Tenant ID")
    timeframe: str = Field(..., description="Analytics timeframe")
    avg_response_time: float = Field(..., description="Average response time")
    p95_response_time: float = Field(..., description="95th percentile response time")
    p99_response_time: float = Field(..., description="99th percentile response time")
    throughput: float = Field(..., description="Requests per second")
    error_rate: float = Field(..., description="Error rate percentage")
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    disk_usage: float = Field(..., description="Disk usage percentage")
    network_io: Dict[str, Any] = Field(
        default_factory=dict, description="Network I/O statistics"
    )
    slow_queries: List[Dict[str, Any]] = Field(
        default_factory=list, description="Slow queries"
    )
    bottlenecks: List[Dict[str, Any]] = Field(
        default_factory=list, description="Performance bottlenecks"
    )


class UserAnalyticsResponse(BaseModel):
    """Response model for user analytics."""

    tenant_id: str = Field(..., description="Tenant ID")
    timeframe: str = Field(..., description="Analytics timeframe")
    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    new_users: int = Field(..., description="Number of new users")
    returning_users: int = Field(..., description="Number of returning users")
    user_retention_rate: float = Field(..., description="User retention rate")
    user_engagement_score: float = Field(..., description="User engagement score")
    popular_user_actions: List[Dict[str, Any]] = Field(
        default_factory=list, description="Popular user actions"
    )
    user_sessions: Dict[str, Any] = Field(
        default_factory=dict, description="User session data"
    )
    user_demographics: Dict[str, Any] = Field(
        default_factory=dict, description="User demographics"
    )
    user_feedback: List[Dict[str, Any]] = Field(
        default_factory=list, description="User feedback"
    )


class PredictiveAnalyticsResponse(BaseModel):
    """Response model for predictive analytics."""

    tenant_id: str = Field(..., description="Tenant ID")
    metric: str = Field(..., description="Predicted metric")
    forecast_periods: int = Field(..., description="Number of forecast periods")
    forecast_values: List[float] = Field(
        default_factory=list, description="Forecasted values"
    )
    confidence_intervals: List[Dict[str, float]] = Field(
        default_factory=list, description="Confidence intervals"
    )
    trend_direction: str = Field(..., description="Trend direction")
    trend_strength: float = Field(..., description="Trend strength")
    seasonality_detected: bool = Field(
        ..., description="Whether seasonality was detected"
    )
    anomaly_detected: bool = Field(..., description="Whether anomalies were detected")
    accuracy_metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Model accuracy metrics"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Recommendations"
    )


class DashboardResponse(BaseModel):
    """Response model for dashboard configuration."""

    id: str = Field(..., description="Dashboard ID")
    name: str = Field(..., description="Dashboard name")
    description: Optional[str] = Field(None, description="Dashboard description")
    tenant_id: str = Field(..., description="Tenant ID")
    widgets: List[Dict[str, Any]] = Field(
        default_factory=list, description="Dashboard widgets"
    )
    layout: Dict[str, Any] = Field(default_factory=dict, description="Widget layout")
    refresh_interval: int = Field(..., description="Refresh interval in seconds")
    is_public: bool = Field(..., description="Whether dashboard is public")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


class DashboardListResponse(BaseModel):
    """Response model for dashboard listing."""

    dashboards: List[Dict[str, Any]] = Field(..., description="List of dashboards")
    total: int = Field(..., description="Total number of dashboards")


class WidgetDataResponse(BaseModel):
    """Response model for widget data."""

    widget_id: str = Field(..., description="Widget ID")
    tenant_id: str = Field(..., description="Tenant ID")
    data: Dict[str, Any] = Field(..., description="Widget data")
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Widget configuration"
    )
    last_updated: str = Field(..., description="Last update timestamp")
