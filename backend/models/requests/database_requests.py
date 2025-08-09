"""
Database Request Models

This module contains Pydantic models for database-related API requests.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class DatabaseQueryRequest(BaseModel):
    """Request to execute a database query."""

    database_name: str = Field(..., description="Name of the database")
    query: str = Field(..., description="SQL query to execute")
    params: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Query parameters"
    )
    timeout: Optional[int] = Field(
        60, ge=1, le=3600, description="Query timeout in seconds"
    )


class DatabaseAnalysisRequest(BaseModel):
    """Request to analyze database table data."""

    table_name: str = Field(..., description="Name of the table to analyze")
    columns: Optional[List[str]] = Field(
        default_factory=list, description="Specific columns to analyze"
    )


class DatabaseConfigRequest(BaseModel):
    """Request to configure a database connection."""

    name: str = Field(..., description="Database name")
    type: str = Field(
        ..., description="Database type (postgresql, mysql, sqlite, etc.)"
    )
    host: str = Field(..., description="Database host")
    port: int = Field(5432, ge=1, le=65535, description="Database port")
    database: str = Field(..., description="Database name")
    username: Optional[str] = Field(None, description="Database username")
    password: Optional[str] = Field(None, description="Database password")
    ssl_mode: Optional[str] = Field(None, description="SSL mode")
    connection_timeout: int = Field(
        30, ge=1, le=300, description="Connection timeout in seconds"
    )
    pool_size: int = Field(10, ge=1, le=100, description="Connection pool size")
    max_overflow: int = Field(
        0, ge=0, le=100, description="Maximum overflow connections"
    )


class DatabaseTestRequest(BaseModel):
    """Request to test database connection."""

    database_name: str = Field(..., description="Name of the database to test")


class DatabaseOptimizationRequest(BaseModel):
    """Request to optimize a database query."""

    database_name: str = Field(..., description="Name of the database")
    query: str = Field(..., description="SQL query to optimize")
    analyze_plan: bool = Field(
        True, description="Whether to analyze query execution plan"
    )
