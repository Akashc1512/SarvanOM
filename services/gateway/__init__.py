"""
API Gateway Service Module

This module provides the main API gateway that routes requests to various microservices
including search, fact-check, synthesis, auth, crawler, vector, and graph services.
"""

from .gateway_app import GatewayApp
from .routes import health_router, search_router, fact_check_router, synthesis_router
from .routes import auth_router, crawler_router, vector_router, graph_router

__all__ = [
    "GatewayApp",
    "health_router",
    "search_router",
    "fact_check_router",
    "synthesis_router",
    "auth_router",
    "crawler_router",
    "vector_router",
    "graph_router",
]
