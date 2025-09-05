"""
Database Package - Universal Knowledge Platform

This package provides database functionality including:
- Connection management
- Repository patterns
- Query building
- Transaction handling
- Migration support

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

from .connection import (
    DatabaseConnectionManager,
    get_db_manager,
    shutdown_db_manager,
    execute_query,
    execute_transaction,
)

def get_database_service():
    """Get database service (alias for connection manager)."""
    return get_db_manager()

from .repository import (
    BaseRepository,
    QueryOptions,
    PaginatedResult,
    FilterCondition,
    SortCondition,
    FilterOperator,
    SortOrder,
)

__all__ = [
    # Connection management
    "DatabaseConnectionManager",
    "get_db_manager",
    "get_database_service",
    "shutdown_db_manager",
    "execute_query",
    "execute_transaction",
    
    # Repository patterns
    "BaseRepository",
    "QueryOptions",
    "PaginatedResult",
    "FilterCondition",
    "SortCondition",
    "FilterOperator",
    "SortOrder",
]
