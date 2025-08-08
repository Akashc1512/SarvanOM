"""
Request Models for API Gateway

This module contains all request models used by the API gateway endpoints.
Models are organized by functionality and follow Pydantic validation patterns.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


# Authentication Models
class LoginRequest(BaseModel):
    """Request model for user login."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    remember_me: Optional[bool] = False
    device_info: Optional[Dict[str, Any]] = None


class RegisterRequest(BaseModel):
    """Request model for user registration."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=100)
    role: str = Field(default="user", description="User role")


# Query Models
class QueryRequest(BaseModel):
    """Base request model for query processing."""
    query: str = Field(..., min_length=1, max_length=10000)
    context: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None


class ComprehensiveQueryRequest(BaseModel):
    """Request model for comprehensive query processing."""
    query: str = Field(..., min_length=1, max_length=10000)
    include_fact_checking: bool = Field(default=True)
    include_synthesis: bool = Field(default=True)
    include_citations: bool = Field(default=True)
    max_results: int = Field(default=10, ge=1, le=100)
    context: Optional[Dict[str, Any]] = None


# Feedback Models
class FeedbackRequest(BaseModel):
    """Request model for user feedback."""
    query_id: str = Field(..., description="ID of the query being rated")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    feedback_type: str = Field(..., description="Type of feedback")
    comment: Optional[str] = Field(None, max_length=1000)
    metadata: Optional[Dict[str, Any]] = None


# Expert Review Models
class ExpertReviewRequest(BaseModel):
    """Request model for expert review submission."""
    review_id: str = Field(..., description="Unique review identifier")
    expert_id: str = Field(..., description="Expert identifier")
    verdict: str = Field(..., description="Review verdict: supported, contradicted, or unclear")
    notes: str = Field(..., max_length=5000)
    confidence: float = Field(..., ge=0.0, le=1.0)


# Task Generation Models
class TaskGenerationRequest(BaseModel):
    """Request model for task generation."""
    query: str = Field(..., min_length=1, max_length=10000)
    task_type: str = Field(..., description="Type of tasks to generate")
    max_tasks: int = Field(default=5, ge=1, le=20)
    context: Optional[Dict[str, Any]] = None


# Agent Models
class AgentRequest(BaseModel):
    """Base request model for agent operations."""
    query: str = Field(..., min_length=1, max_length=10000)
    parameters: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None


class BrowserSearchRequest(AgentRequest):
    """Request model for browser search agent."""
    search_type: str = Field(default="web", description="Type of search")
    max_results: int = Field(default=10, ge=1, le=50)


class PDFProcessRequest(AgentRequest):
    """Request model for PDF processing agent."""
    file_url: str = Field(..., description="URL of the PDF file")
    extraction_mode: str = Field(default="text", description="Extraction mode")


class CodeExecutorRequest(AgentRequest):
    """Request model for code execution agent."""
    code: str = Field(..., description="Code to execute")
    language: str = Field(default="python", description="Programming language")
    timeout: int = Field(default=30, ge=1, le=300)


class KnowledgeGraphRequest(AgentRequest):
    """Request model for knowledge graph queries."""
    query_type: str = Field(default="entity_relationship", description="Type of graph query")
    depth: int = Field(default=2, ge=1, le=5)


class DatabaseQueryRequest(AgentRequest):
    """Request model for database queries."""
    database_type: str = Field(..., description="Type of database")
    query: str = Field(..., description="Database query")
    parameters: Optional[Dict[str, Any]] = None


class WebCrawlerRequest(AgentRequest):
    """Request model for web crawler agent."""
    url: str = Field(..., description="URL to crawl")
    depth: int = Field(default=1, ge=1, le=3)
    max_pages: int = Field(default=10, ge=1, le=100)


# Query Management Models
class QueryUpdateRequest(BaseModel):
    """Request model for updating queries."""
    status: Optional[str] = Field(None, description="New status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
    notes: Optional[str] = Field(None, max_length=5000)


# Generic Request Models
class GenericRequest(BaseModel):
    """Generic request model for flexible endpoints."""
    data: Dict[str, Any] = Field(..., description="Request data")
    options: Optional[Dict[str, Any]] = Field(None, description="Request options")


# SSO Models
class OAuthLoginRequest(BaseModel):
    """Request model for OAuth login."""
    code: str = Field(..., description="OAuth authorization code")
    redirect_uri: Optional[str] = Field(None, description="OAuth redirect URI")


class PasswordChangeRequest(BaseModel):
    """Request model for password change."""
    current_password: str = Field(..., min_length=6, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)


class UserUpdateRequest(BaseModel):
    """Request model for user profile update."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, description="Valid email address")
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)


# Multi-Tenant Models
class CreateTenantRequest(BaseModel):
    """Request model for creating a new tenant."""
    name: str = Field(..., min_length=2, max_length=100)
    domain: str = Field(..., description="Tenant domain")
    owner_id: str = Field(..., description="Owner user ID")
    tier: str = Field(default="free", description="Tenant tier")
    admin_emails: Optional[List[str]] = Field(None, description="Admin email addresses")


class UpdateTenantRequest(BaseModel):
    """Request model for updating tenant information."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    domain: Optional[str] = Field(None, description="Tenant domain")
    owner_id: Optional[str] = Field(None, description="Owner user ID")
    admin_emails: Optional[List[str]] = Field(None, description="Admin email addresses")


class TenantConfigRequest(BaseModel):
    """Request model for tenant configuration."""
    features_enabled: List[str] = Field(default_factory=list, description="Enabled features")
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Custom settings")
    api_rate_limit: int = Field(default=1000, ge=1, description="API rate limit")
    storage_limit_gb: float = Field(default=1.0, ge=0.1, description="Storage limit in GB")


class UsageTrackingRequest(BaseModel):
    """Request model for usage tracking."""
    storage_gb: float = Field(..., ge=0.0, description="Storage usage in GB")
    api_calls: int = Field(default=1, ge=0, description="Number of API calls")
    user_id: Optional[str] = Field(None, description="User ID for activity tracking")


# Analytics Models
class AnalyticsDataRequest(BaseModel):
    """Request model for analytics data collection."""
    metric_name: str = Field(..., description="Name of the metric")
    value: float = Field(..., description="Metric value")
    tenant_id: str = Field(default="default", description="Tenant ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class DashboardConfigRequest(BaseModel):
    """Request model for dashboard configuration."""
    id: str = Field(..., description="Dashboard ID")
    name: str = Field(..., min_length=1, max_length=100, description="Dashboard name")
    description: Optional[str] = Field(None, max_length=500, description="Dashboard description")
    tenant_id: str = Field(default="default", description="Tenant ID")
    widgets: List[Dict[str, Any]] = Field(default_factory=list, description="Dashboard widgets")
    layout: Dict[str, Any] = Field(default_factory=dict, description="Widget layout")
    refresh_interval: int = Field(default=300, ge=30, description="Refresh interval in seconds")
    is_public: bool = Field(default=False, description="Whether dashboard is public")


class WidgetConfigRequest(BaseModel):
    """Request model for widget configuration."""
    widget_type: str = Field(..., description="Type of widget")
    title: str = Field(..., min_length=1, max_length=100, description="Widget title")
    config: Dict[str, Any] = Field(default_factory=dict, description="Widget configuration")
    position: Dict[str, int] = Field(default_factory=dict, description="Widget position")
    size: Dict[str, int] = Field(default_factory=dict, description="Widget size") 