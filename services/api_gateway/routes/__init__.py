"""
Routes package for API Gateway.

This package contains all route handlers for the API gateway endpoints.
"""

from .queries import router as queries_router
from .health import router as health_router
from .agents import router as agents_router
from .sso import router as sso_router
from .multi_tenant import router as multi_tenant_router
from .analytics import router as analytics_router

# List of all routers for easy registration
routers = [
    queries_router,
    health_router,
    agents_router,
    sso_router,
    multi_tenant_router,
    analytics_router
]

__all__ = [
    "queries_router",
    "health_router", 
    "agents_router",
    "sso_router",
    "multi_tenant_router",
    "analytics_router",
    "routers"
] 