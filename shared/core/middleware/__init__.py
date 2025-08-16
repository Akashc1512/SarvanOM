"""
Middleware Package - Shared Middleware Components.

This package contains shared middleware components that can be used
across all FastAPI services in the platform.

Components:
    - Rate limiting middleware
    - Authentication middleware (future)
    - Logging middleware (future)
    - CORS middleware (future)
    - Security middleware (future)

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    1.0.0 (2024-12-28)
"""

from .rate_limiter import (
    RateLimiter,
    RateLimitExceeded,
    create_rate_limit_middleware,
    get_rate_limiter,
    rate_limit,
)

__all__ = [
    "RateLimiter",
    "RateLimitExceeded", 
    "create_rate_limit_middleware",
    "get_rate_limiter",
    "rate_limit",
]
