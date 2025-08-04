"""
Services Module

This module provides access to all microservices including:
- API Gateway for request routing
- Authentication service
- Search and retrieval services
- Fact checking service
- Synthesis service
- Crawler service
- Vector database service
- Graph service
"""

from .gateway import GatewayApp
from .gateway.routes import (
    health_router,
    search_router,
    fact_check_router,
    synthesis_router,
    auth_router,
    crawler_router,
    vector_router,
    graph_router,
)

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