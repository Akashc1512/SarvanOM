"""
Rate Limiting Middleware for API Gateway

This module handles rate limiting for the API gateway to prevent abuse and ensure fair usage.
It provides configurable rate limiting based on IP address, user ID, and API keys.
"""

import time
import logging
from shared.core.unified_logging import get_logger
from typing import Dict, Any, Optional, Tuple
from fastapi import Request, HTTPException
from collections import defaultdict, deque

logger = get_logger(__name__)


class RateLimiter:
    """Rate limiter implementation using sliding window algorithm."""
    
    def __init__(self, window_size: int = 60, max_requests: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            window_size: Time window in seconds
            max_requests: Maximum requests per window
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests = defaultdict(deque)
    
    def is_allowed(self, key: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed.
        
        Args:
            key: Rate limiting key (IP, user ID, etc.)
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        current_time = time.time()
        window_start = current_time - self.window_size
        
        # Clean old requests
        if key in self.requests:
            while self.requests[key] and self.requests[key][0] < window_start:
                self.requests[key].popleft()
        
        # Check if limit exceeded
        request_count = len(self.requests[key])
        is_allowed = request_count < self.max_requests
        
        if is_allowed:
            self.requests[key].append(current_time)
        
        # Calculate remaining requests and reset time
        remaining_requests = max(0, self.max_requests - request_count)
        reset_time = current_time + self.window_size
        
        return is_allowed, {
            "limit": self.max_requests,
            "remaining": remaining_requests,
            "reset_time": reset_time,
            "window_size": self.window_size
        }


class RateLimitConfig:
    """Configuration for rate limiting."""
    
    def __init__(self):
        # Default limits
        self.default_limit = 60  # requests per minute
        self.default_window = 60  # seconds
        
        # Per-endpoint limits
        self.endpoint_limits = {
            "/query": 30,  # 30 requests per minute for queries
            "/query/comprehensive": 10,  # 10 comprehensive queries per minute
            "/agents/": 20,  # 20 agent requests per minute
            "/health": 120,  # 120 health checks per minute
            "/metrics": 60,  # 60 metrics requests per minute
        }
        
        # Per-user limits (for authenticated users)
        self.user_limits = {
            "free": 100,  # 100 requests per hour
            "premium": 1000,  # 1000 requests per hour
            "enterprise": 10000,  # 10000 requests per hour
        }
        
        # IP-based limits
        self.ip_limit = 200  # 200 requests per minute per IP
        
        # Exempt paths (no rate limiting)
        self.exempt_paths = [
            "/health/basic",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]


class RateLimitingMiddleware:
    """Rate limiting middleware for API gateway."""
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        """
        Initialize rate limiting middleware.
        
        Args:
            config: Rate limiting configuration
        """
        self.config = config or RateLimitConfig()
        
        # Create rate limiters
        self.ip_limiter = RateLimiter(
            window_size=60,
            max_requests=self.config.ip_limit
        )
        
        self.user_limiters = {}
        for user_type, limit in self.config.user_limits.items():
            self.user_limiters[user_type] = RateLimiter(
                window_size=3600,  # 1 hour
                max_requests=limit
            )
        
        self.endpoint_limiters = {}
        for endpoint, limit in self.config.endpoint_limits.items():
            self.endpoint_limiters[endpoint] = RateLimiter(
                window_size=60,
                max_requests=limit
            )
    
    def _get_rate_limit_key(self, request: Request, user_id: Optional[str] = None) -> str:
        """Generate rate limiting key based on request."""
        # Use IP address as base key
        key = f"ip:{request.client.host}"
        
        # Add user ID if available
        if user_id:
            key += f":user:{user_id}"
        
        return key
    
    def _get_endpoint_limit(self, path: str) -> Optional[int]:
        """Get rate limit for specific endpoint."""
        for endpoint, limit in self.config.endpoint_limits.items():
            if path.startswith(endpoint):
                return limit
        return None
    
    def _is_exempt(self, path: str) -> bool:
        """Check if path is exempt from rate limiting."""
        return any(path.startswith(exempt) for exempt in self.config.exempt_paths)
    
    async def check_rate_limit(
        self, 
        request: Request, 
        user_id: Optional[str] = None,
        user_type: str = "free"
    ) -> Dict[str, Any]:
        """
        Check rate limits for request.
        
        Args:
            request: FastAPI request object
            user_id: User identifier (optional)
            user_type: User type for rate limiting
            
        Returns:
            Rate limit information
        """
        path = request.url.path
        
        # Check if path is exempt
        if self._is_exempt(path):
            return {
                "allowed": True,
                "exempt": True,
                "limit": None,
                "remaining": None,
                "reset_time": None
            }
        
        # Check IP-based rate limit
        ip_key = f"ip:{request.client.host}"
        ip_allowed, ip_info = self.ip_limiter.is_allowed(ip_key)
        
        if not ip_allowed:
            logger.warning(
                f"IP rate limit exceeded: {request.client.host}",
                extra={
                    "ip": request.client.host,
                    "path": path,
                    "user_id": user_id
                }
            )
            raise HTTPException(
                status_code=429,
                detail="Too many requests from this IP address",
                headers={
                    "X-RateLimit-Limit": str(ip_info["limit"]),
                    "X-RateLimit-Remaining": str(ip_info["remaining"]),
                    "X-RateLimit-Reset": str(int(ip_info["reset_time"]))
                }
            )
        
        # Check user-based rate limit (if authenticated)
        user_allowed = True
        user_info = {}
        if user_id and user_type in self.user_limiters:
            user_key = f"user:{user_id}:{user_type}"
            user_allowed, user_info = self.user_limiters[user_type].is_allowed(user_key)
            
            if not user_allowed:
                logger.warning(
                    f"User rate limit exceeded: {user_id}",
                    extra={
                        "user_id": user_id,
                        "user_type": user_type,
                        "path": path
                    }
                )
                raise HTTPException(
                    status_code=429,
                    detail="User rate limit exceeded",
                    headers={
                        "X-RateLimit-Limit": str(user_info["limit"]),
                        "X-RateLimit-Remaining": str(user_info["remaining"]),
                        "X-RateLimit-Reset": str(int(user_info["reset_time"]))
                    }
                )
        
        # Check endpoint-specific rate limit
        endpoint_allowed = True
        endpoint_info = {}
        endpoint_limit = self._get_endpoint_limit(path)
        if endpoint_limit:
            endpoint_key = f"endpoint:{path}"
            if endpoint_key not in self.endpoint_limiters:
                self.endpoint_limiters[endpoint_key] = RateLimiter(
                    window_size=60,
                    max_requests=endpoint_limit
                )
            
            endpoint_allowed, endpoint_info = self.endpoint_limiters[endpoint_key].is_allowed(endpoint_key)
            
            if not endpoint_allowed:
                logger.warning(
                    f"Endpoint rate limit exceeded: {path}",
                    extra={
                        "path": path,
                        "user_id": user_id,
                        "ip": request.client.host
                    }
                )
                raise HTTPException(
                    status_code=429,
                    detail="Endpoint rate limit exceeded",
                    headers={
                        "X-RateLimit-Limit": str(endpoint_info["limit"]),
                        "X-RateLimit-Remaining": str(endpoint_info["remaining"]),
                        "X-RateLimit-Reset": str(int(endpoint_info["reset_time"]))
                    }
                )
        
        # Return rate limit information
        return {
            "allowed": True,
            "exempt": False,
            "ip_limit": ip_info,
            "user_limit": user_info if user_id else None,
            "endpoint_limit": endpoint_info if endpoint_limit else None
        }


# Global rate limiting middleware instance
rate_limiting_middleware = RateLimitingMiddleware()


async def rate_limit_check(request: Request, call_next):
    """Rate limiting middleware function."""
    try:
        # Extract user information (simplified)
        user_id = None
        user_type = "free"
        
        # Check rate limits
        rate_limit_info = await rate_limiting_middleware.check_rate_limit(
            request=request,
            user_id=user_id,
            user_type=user_type
        )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        if not rate_limit_info["exempt"]:
            ip_info = rate_limit_info["ip_limit"]
            response.headers["X-RateLimit-Limit"] = str(ip_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(ip_info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(int(ip_info["reset_time"]))
            
            if rate_limit_info["user_limit"]:
                user_info = rate_limit_info["user_limit"]
                response.headers["X-UserRateLimit-Limit"] = str(user_info["limit"])
                response.headers["X-UserRateLimit-Remaining"] = str(user_info["remaining"])
                response.headers["X-UserRateLimit-Reset"] = str(int(user_info["reset_time"]))
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions (rate limit exceeded)
        raise
    except Exception as e:
        logger.error(f"Rate limiting error: {e}")
        # Continue with request if rate limiting fails
        return await call_next(request) 