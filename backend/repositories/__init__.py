"""
Repository Layer for SarvanOM Backend

This package contains the repository pattern implementation for data persistence.
Repositories handle data access and abstract the underlying storage mechanisms.

Architecture:
- Base Repository: Common interface and functionality
- Domain Repositories: Specific to domain entities (Query, User, Agent)
- Database Repositories: Database-specific implementations
"""

from .base_repository import BaseRepository
from .query_repository import QueryRepository, QueryRepositoryImpl
from .user_repository import UserRepository, UserRepositoryImpl
from .agent_repository import AgentRepository, AgentRepositoryImpl

__all__ = [
    "BaseRepository",
    "QueryRepository",
    "QueryRepositoryImpl", 
    "UserRepository",
    "UserRepositoryImpl",
    "AgentRepository",
    "AgentRepositoryImpl"
]
