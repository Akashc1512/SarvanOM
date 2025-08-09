"""
Domain Enums

This module contains all domain-specific enums used across the application.
"""

from enum import Enum


class ServiceStatus(Enum):
    """Service status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class DatabaseType(Enum):
    """Database types."""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    ORACLE = "oracle"
    SQLSERVER = "sqlserver"


class QueryType(Enum):
    """Query types."""

    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CREATE = "create"
    DROP = "drop"
    ALTER = "alter"
    ANALYZE = "analyze"


class ConnectionStatus(Enum):
    """Database connection status."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"
    TIMEOUT = "timeout"


class DataType(Enum):
    """Data types for analysis."""

    NUMERIC = "numeric"
    TEXT = "text"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    BLOB = "blob"
    JSON = "json"
