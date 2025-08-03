"""
API Gateway Microservice
Single entry point for all backend microservices.

This gateway provides:
- Request routing to appropriate microservices
- Response aggregation
- Authentication and authorization
- Rate limiting and monitoring
- Unified API interface
"""

from .gateway_service import GatewayService
from .api import router as gateway_router

__all__ = [
    "GatewayService",
    "gateway_router"
] 