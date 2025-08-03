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