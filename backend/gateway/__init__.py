"""
Gateway Service
API Gateway for routing requests to backend services.

This service provides:
- Request routing and orchestration
- Service discovery and load balancing
- Authentication and authorization middleware
- Rate limiting and security
"""

from .gateway_service import app

__all__ = [
    "app"
] 