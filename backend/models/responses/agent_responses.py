"""
Agent Response Models

This module contains Pydantic models for agent-related API responses.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class AgentResponse(BaseModel):
    """Basic agent response model."""
    agent_id: str = Field(..., description="Agent identifier")
    status: str = Field(..., description="Response status")
    result: Dict[str, Any] = Field(..., description="Response result")
    processing_time: float = Field(..., ge=0.0, description="Processing time in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")


class AgentDetailResponse(BaseModel):
    """Detailed agent response model."""
    agent_id: str = Field(..., description="Agent identifier")
    agent_type: str = Field(..., description="Agent type")
    name: str = Field(..., description="Agent name")
    status: str = Field(..., description="Agent status")
    current_task: Optional[str] = Field(None, description="Current task ID")
    capabilities: List[Dict[str, Any]] = Field(default_factory=list, description="Agent capabilities")
    config: Dict[str, Any] = Field(default_factory=dict, description="Agent configuration")
    stats: Dict[str, Any] = Field(default_factory=dict, description="Agent statistics")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class AgentListResponse(BaseModel):
    """Agent list response model."""
    agents: List[AgentResponse] = Field(..., description="List of agents")
    total_count: int = Field(..., ge=0, description="Total number of agents")
    available_agents: int = Field(..., ge=0, description="Number of available agents")
    busy_agents: int = Field(..., ge=0, description="Number of busy agents")
    error_agents: int = Field(..., ge=0, description="Number of agents in error state")


class AgentPoolResponse(BaseModel):
    """Agent pool response model."""
    pool_stats: Dict[str, Any] = Field(..., description="Pool statistics")
    agents_by_type: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Agents grouped by type")
    total_agents: int = Field(..., ge=0, description="Total number of agents")
    available_agents: int = Field(..., ge=0, description="Number of available agents")
    busy_agents: int = Field(..., ge=0, description="Number of busy agents")
    error_agents: int = Field(..., ge=0, description="Number of agents in error state")


class AgentTaskResponse(BaseModel):
    """Agent task response model."""
    task_id: str = Field(..., description="Task identifier")
    agent_id: str = Field(..., description="Agent identifier")
    task_type: str = Field(..., description="Task type")
    status: str = Field(..., description="Task status")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result")
    processing_time: float = Field(..., ge=0.0, description="Processing time in seconds")
    created_at: datetime = Field(..., description="Task creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Task completion timestamp")


class AgentCleanupResponse(BaseModel):
    """Agent cleanup response model."""
    cleaned_count: int = Field(..., ge=0, description="Number of agents cleaned up")
    message: str = Field(..., description="Cleanup message")
    timestamp: datetime = Field(..., description="Cleanup timestamp")


class AgentErrorResponse(BaseModel):
    """Agent error response model."""
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Error type")
    agent_id: Optional[str] = Field(None, description="Agent identifier")
    timestamp: datetime = Field(..., description="Error timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details") 