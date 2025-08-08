"""
Agent Request Models

This module contains Pydantic models for agent-related API requests.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class AgentCreateRequest(BaseModel):
    """Request to create a new agent."""
    agent_type: str = Field(..., description="Type of agent to create")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Agent configuration")


class AgentUpdateRequest(BaseModel):
    """Request to update an agent."""
    config: Optional[Dict[str, Any]] = Field(None, description="Updated agent configuration")
    status: Optional[str] = Field(None, description="Updated agent status")


class AgentTaskRequest(BaseModel):
    """Request to assign a task to an agent."""
    task_type: str = Field(..., description="Type of task to assign")
    task_data: Dict[str, Any] = Field(..., description="Task data")
    priority: Optional[int] = Field(1, ge=1, le=10, description="Task priority (1-10)")
    timeout: Optional[int] = Field(300, ge=1, le=3600, description="Task timeout in seconds")


class AgentPoolRequest(BaseModel):
    """Request to manage agent pool."""
    action: str = Field(..., description="Action to perform (create, cleanup, resize)")
    agent_type: Optional[str] = Field(None, description="Agent type for the action")
    count: Optional[int] = Field(None, ge=1, le=100, description="Number of agents for resize action")


class AgentRequest(BaseModel):
    """Generic agent request model."""
    query: Optional[str] = Field(None, description="Query for agent operations")
    url: Optional[str] = Field(None, description="URL for agent operations")
    code: Optional[str] = Field(None, description="Code for agent operations")
    file_data: Optional[Any] = Field(None, description="File data for agent operations")
    search_type: Optional[str] = Field("web", description="Search type for browser operations")
    max_results: Optional[int] = Field(10, description="Maximum results to return")
    extraction_type: Optional[str] = Field("full", description="Extraction type for content operations")
    language: Optional[str] = Field("python", description="Programming language for code operations")
    database_type: Optional[str] = Field("postgres", description="Database type for database operations")
    crawl_type: Optional[str] = Field("full", description="Crawl type for crawler operations")
    query_type: Optional[str] = Field("entities", description="Query type for knowledge graph operations")
    processing_options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Processing options")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional parameters") 