"""
Routes package for API Gateway.

This package contains all route handlers for the API gateway endpoints.
"""

from .queries import router as queries_router
from .health import router as health_router
from .agents import router as agents_router

# List of all routers for easy registration
routers = [
    queries_router,
    health_router,
    agents_router
]

__all__ = [
    "queries_router",
    "health_router", 
    "agents_router",
    "routers"
] 