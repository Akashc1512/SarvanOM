"""
API Routers for SarvanOM Backend

This module contains all FastAPI router definitions for the API endpoints.
Each router is focused on a specific domain or functionality.
"""

from .query_router import router as query_router
from .health_router import router as health_router
from .agent_router import router as agent_router
from .admin_router import router as admin_router
from .auth_router import router as auth_router

# List of all routers for easy registration
routers = [query_router, health_router, agent_router, admin_router, auth_router]

__all__ = [
    "query_router",
    "health_router",
    "agent_router",
    "admin_router",
    "auth_router",
    "routers",
]
