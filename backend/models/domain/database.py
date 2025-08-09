"""
Database Domain Models

This module contains the core database domain models and business logic.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from enum import Enum


class DatabaseType(Enum):
    """Database types."""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    ORACLE = "oracle"
    SQLSERVER = "sqlserver"


@dataclass
class DatabaseConfig:
    """Database configuration."""

    name: str
    type: DatabaseType
    host: str
    port: int
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    ssl_mode: Optional[str] = None
    connection_timeout: int = 30
    pool_size: int = 10
    max_overflow: int = 0
    echo: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class QueryResult:
    """Database query result."""

    success: bool
    data: List[Dict[str, Any]] = field(default_factory=list)
    row_count: int = 0
    columns: List[str] = field(default_factory=list)
    query: str = ""
    database_name: str = ""
    processing_time: float = 0.0
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate query result after initialization."""
        if not self.success and not self.error:
            raise ValueError("Error must be provided when success is False")


@dataclass
class SchemaInfo:
    """Database schema information."""

    database_name: str
    tables: List[Dict[str, Any]] = field(default_factory=list)
    views: List[Dict[str, Any]] = field(default_factory=list)
    indexes: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DataAnalysis:
    """Data analysis result."""

    database_name: str
    table_name: str
    row_count: int = 0
    column_stats: Dict[str, Any] = field(default_factory=dict)
    data_types: Dict[str, str] = field(default_factory=dict)
    missing_values: Dict[str, int] = field(default_factory=dict)
    unique_values: Dict[str, int] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DatabaseConnection:
    """Database connection information."""

    name: str
    type: DatabaseType
    host: str
    port: int
    database: str
    status: str = "disconnected"
    response_time: float = 0.0
    error: Optional[str] = None
    last_connected: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class QueryOptimization:
    """Query optimization result."""

    original_query: str
    optimized_query: str
    suggestions: List[str] = field(default_factory=list)
    performance_improvement: float = 0.0
    database_name: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DatabaseMetrics:
    """Database service metrics."""

    active_connections: int = 0
    max_connections: int = 10
    query_count: int = 0
    error_count: int = 0
    avg_response_time: float = 0.0
    total_databases: int = 0
    connected_databases: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
