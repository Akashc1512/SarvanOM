"""
Middleware package for API Gateway.

This package contains all middleware components for the API gateway.
"""

from .auth import (
    SecurityMiddleware,
    AuthenticationMiddleware,
    security_middleware,
    auth_middleware,
    security_check,
    get_current_user,
    require_admin,
    require_read,
    require_write
)

from .logging import (
    SafeJSONFormatter,
    RequestLogger,
    PerformanceLogger,
    request_logger,
    performance_logger,
    add_request_id,
    log_requests,
    get_request_stats,
    get_performance_metrics
)

from .cors import (
    CORSConfig,
    setup_cors,
    create_cors_config,
    get_development_cors_config,
    get_production_cors_config
)

from .rate_limiting import (
    RateLimiter,
    RateLimitConfig,
    RateLimitingMiddleware,
    rate_limiting_middleware,
    rate_limit_check
)

__all__ = [
    # Authentication middleware
    "SecurityMiddleware",
    "AuthenticationMiddleware", 
    "security_middleware",
    "auth_middleware",
    "security_check",
    "get_current_user",
    "require_admin",
    "require_read",
    "require_write",
    
    # Logging middleware
    "SafeJSONFormatter",
    "RequestLogger",
    "PerformanceLogger",
    "request_logger",
    "performance_logger",
    "add_request_id",
    "log_requests",
    "get_request_stats",
    "get_performance_metrics",
    
    # CORS middleware
    "CORSConfig",
    "setup_cors",
    "create_cors_config",
    "get_development_cors_config",
    "get_production_cors_config",
    
    # Rate limiting middleware
    "RateLimiter",
    "RateLimitConfig",
    "RateLimitingMiddleware",
    "rate_limiting_middleware",
    "rate_limit_check"
] 