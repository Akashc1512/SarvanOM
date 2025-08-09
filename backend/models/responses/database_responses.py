"""
Database Response Models

This module contains Pydantic models for database-related API responses.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class DatabaseResponse(BaseModel):
    """Basic database response model."""

    success: bool = Field(..., description="Operation success status")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if operation failed")
    processing_time: float = Field(
        ..., ge=0.0, description="Processing time in seconds"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Response metadata"
    )
    timestamp: datetime = Field(..., description="Response timestamp")


class DatabaseListResponse(BaseModel):
    """Database list response model."""

    success: bool = Field(..., description="Operation success status")
    databases: List[Dict[str, Any]] = Field(..., description="List of databases")
    total_count: int = Field(..., ge=0, description="Total number of databases")
    connected_count: int = Field(..., ge=0, description="Number of connected databases")
    processing_time: float = Field(
        ..., ge=0.0, description="Processing time in seconds"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Response metadata"
    )
    error: Optional[str] = Field(None, description="Error message if operation failed")
    timestamp: datetime = Field(..., description="Response timestamp")


class DatabaseQueryResponse(BaseModel):
    """Database query response model."""

    success: bool = Field(..., description="Query success status")
    data: List[Dict[str, Any]] = Field(
        default_factory=list, description="Query results"
    )
    row_count: int = Field(..., ge=0, description="Number of rows returned")
    columns: List[str] = Field(default_factory=list, description="Column names")
    query: str = Field(..., description="Executed query")
    database_name: str = Field(..., description="Database name")
    processing_time: float = Field(..., ge=0.0, description="Query processing time")
    error: Optional[str] = Field(None, description="Error message if query failed")
    timestamp: datetime = Field(..., description="Response timestamp")


class DatabaseSchemaResponse(BaseModel):
    """Database schema response model."""

    success: bool = Field(..., description="Operation success status")
    database_name: str = Field(..., description="Database name")
    tables: List[Dict[str, Any]] = Field(
        default_factory=list, description="Database tables"
    )
    views: List[Dict[str, Any]] = Field(
        default_factory=list, description="Database views"
    )
    indexes: List[Dict[str, Any]] = Field(
        default_factory=list, description="Database indexes"
    )
    constraints: List[Dict[str, Any]] = Field(
        default_factory=list, description="Database constraints"
    )
    processing_time: float = Field(
        ..., ge=0.0, description="Processing time in seconds"
    )
    error: Optional[str] = Field(None, description="Error message if operation failed")
    timestamp: datetime = Field(..., description="Response timestamp")


class DatabaseAnalysisResponse(BaseModel):
    """Database analysis response model."""

    success: bool = Field(..., description="Analysis success status")
    database_name: str = Field(..., description="Database name")
    table_name: str = Field(..., description="Table name")
    row_count: int = Field(..., ge=0, description="Number of rows analyzed")
    column_stats: Dict[str, Any] = Field(
        default_factory=dict, description="Column statistics"
    )
    data_types: Dict[str, str] = Field(default_factory=dict, description="Data types")
    missing_values: Dict[str, int] = Field(
        default_factory=dict, description="Missing value counts"
    )
    unique_values: Dict[str, int] = Field(
        default_factory=dict, description="Unique value counts"
    )
    processing_time: float = Field(
        ..., ge=0.0, description="Processing time in seconds"
    )
    error: Optional[str] = Field(None, description="Error message if analysis failed")
    timestamp: datetime = Field(..., description="Response timestamp")


class DatabaseOptimizationResponse(BaseModel):
    """Database query optimization response model."""

    success: bool = Field(..., description="Optimization success status")
    original_query: str = Field(..., description="Original query")
    optimized_query: str = Field(..., description="Optimized query")
    suggestions: List[str] = Field(
        default_factory=list, description="Optimization suggestions"
    )
    performance_improvement: float = Field(
        ..., ge=0.0, le=1.0, description="Expected performance improvement"
    )
    database_name: str = Field(..., description="Database name")
    processing_time: float = Field(
        ..., ge=0.0, description="Processing time in seconds"
    )
    error: Optional[str] = Field(
        None, description="Error message if optimization failed"
    )
    timestamp: datetime = Field(..., description="Response timestamp")


class DatabaseConnectionResponse(BaseModel):
    """Database connection test response model."""

    success: bool = Field(..., description="Connection test success status")
    database_name: str = Field(..., description="Database name")
    status: str = Field(..., description="Connection status")
    response_time: float = Field(..., ge=0.0, description="Connection response time")
    error: Optional[str] = Field(None, description="Error message if connection failed")
    timestamp: datetime = Field(..., description="Response timestamp")
