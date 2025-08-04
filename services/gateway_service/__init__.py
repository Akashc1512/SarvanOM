"""
API Gateway Service

This service handles API routing and orchestration including:
- Request routing to appropriate services
- Service discovery and load balancing
- Authentication and authorization middleware
- Rate limiting and security
- Request/response transformation
- Error handling and logging
"""

from .gateway_service import GatewayService
from .router import APIRouter

__all__ = ["GatewayService", "APIRouter"] 