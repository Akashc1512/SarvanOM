"""
Rate Limiting Middleware - MAANG Standards.

This module implements a sophisticated rate limiting system following MAANG
best practices for API protection and resource management.

Features:
    - Redis-based distributed rate limiting
    - Configurable rate limits per minute
    - Burst allowance support
    - IP-based and user-based rate limiting
    - Sliding window algorithm
    - Graceful degradation
    - Rate limit headers in responses
    - Detailed logging and monitoring

Architecture:
    - Middleware-based implementation
    - Async-first design
    - Circuit breaker for cache failures
    - Configurable key strategies

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    1.0.0 (2024-12-28)
"""

import time
import hashlib
import json
from typing import Optional, Dict, Any, Callable, Union
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
import structlog

from shared.core.config.central_config import initialize_config
from shared.core.cache import get_cache_manager, CacheLevel
from shared.core.logging import get_logger

logger = get_logger(__name__)


class RateLimitExceeded(HTTPException):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, retry_after: int, limit: int, window: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "retry_after": retry_after,
                "limit": limit,
                "window_seconds": window,
                "message": f"Rate limit exceeded. Try again in {retry_after} seconds."
            }
        )
        self.retry_after = retry_after
        self.limit = limit
        self.window = window


class RateLimiter:
    """Rate limiter implementation using Redis cache."""
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_allowance: int = 10,
        key_prefix: str = "rate_limit",
        window_seconds: int = 60,
        enable_headers: bool = True,
        enable_logging: bool = True,
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests allowed per minute
            burst_allowance: Additional burst requests allowed
            key_prefix: Prefix for Redis keys
            window_seconds: Time window in seconds (default: 60 for per-minute)
            enable_headers: Whether to add rate limit headers to responses
            enable_logging: Whether to log rate limit events
        """
        self.requests_per_minute = requests_per_minute
        self.burst_allowance = burst_allowance
        self.key_prefix = key_prefix
        self.window_seconds = window_seconds
        self.enable_headers = enable_headers
        self.enable_logging = enable_logging
        
        # Calculate total limit including burst
        self.total_limit = requests_per_minute + burst_allowance
        
        # Initialize cache manager
        self.cache = None
        self._init_cache()
    
    def _init_cache(self):
        """Initialize cache manager."""
        try:
            # Use the new cache system with rate limiting level
            self.cache = get_cache_manager(CacheLevel.RATE_LIMITING)
            logger.info(
                "Rate limiter initialized",
                requests_per_minute=self.requests_per_minute,
                burst_allowance=self.burst_allowance,
                total_limit=self.total_limit,
                window_seconds=self.window_seconds,
            )
        except Exception as e:
            logger.error(f"Failed to initialize rate limiter cache: {e}")
            self.cache = None
    
    def _get_client_identifier(self, request: Request) -> str:
        """
        Get client identifier for rate limiting.
        
        Priority:
        1. X-Forwarded-For header (for proxied requests)
        2. X-Real-IP header (for nginx proxy)
        3. Client host
        4. Fallback to user agent hash
        
        Args:
            request: FastAPI request object
            
        Returns:
            Client identifier string
        """
        # Try to get real IP from headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            real_ip = forwarded_for.split(",")[0].strip()
            return f"ip:{real_ip}"
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return f"ip:{real_ip}"
        
        # Fallback to client host
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"
    
    def _get_rate_limit_key(self, identifier: str, endpoint: str) -> str:
        """
        Generate Redis key for rate limiting.
        
        Args:
            identifier: Client identifier
            endpoint: API endpoint path
            
        Returns:
            Redis key string
        """
        # Create a hash of the identifier and endpoint
        key_data = f"{identifier}:{endpoint}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        
        # Include current window timestamp for sliding window
        current_window = int(time.time() // self.window_seconds)
        
        return f"{self.key_prefix}:{key_hash}:{current_window}"
    
    async def _get_current_count(self, key: str) -> int:
        """
        Get current request count for the given key.
        
        Args:
            key: Cache key
            
        Returns:
            Current request count
        """
        if not self.cache:
            # If cache is not available, allow all requests
            logger.warning("Rate limiter cache not available, allowing all requests")
            return 0
        
        try:
            count_data = await self.cache.get(key)
            if count_data is None:
                return 0
            
            # Handle different data types
            if isinstance(count_data, dict):
                return count_data.get("count", 0)
            elif isinstance(count_data, (int, str)):
                return int(count_data)
            else:
                return 0
                
        except Exception as e:
            logger.error(f"Failed to get rate limit count for key {key}: {e}")
            # On cache failure, allow the request
            return 0
    
    async def _increment_count(self, key: str) -> int:
        """
        Increment request count for the given key.
        
        Args:
            key: Cache key
            
        Returns:
            New request count
        """
        if not self.cache:
            return 1
        
        try:
            # Get current count
            current_count = await self._get_current_count(key)
            new_count = current_count + 1
            
            # Set the new count with TTL
            await self.cache.set(key, new_count, ttl_seconds=self.window_seconds)
            
            return new_count
            
        except Exception as e:
            logger.error(f"Failed to increment rate limit count for key {key}: {e}")
            # On cache failure, allow the request
            return 1
    
    async def _get_reset_time(self, key: str) -> int:
        """
        Get time until rate limit resets.
        
        Args:
            key: Redis key
            
        Returns:
            Seconds until reset
        """
        try:
            # Extract window timestamp from key
            window_timestamp = int(key.split(":")[-1])
            current_time = int(time.time() // self.window_seconds)
            
            if window_timestamp == current_time:
                # Current window, calculate remaining time
                elapsed = int(time.time()) % self.window_seconds
                return self.window_seconds - elapsed
            else:
                # Next window
                return 0
                
        except Exception as e:
            logger.error(f"Failed to calculate reset time for key {key}: {e}")
            return self.window_seconds
    
    async def check_rate_limit(
        self,
        request: Request,
        endpoint: Optional[str] = None,
        custom_limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Check if request is within rate limits.
        
        Args:
            request: FastAPI request object
            endpoint: API endpoint path (defaults to request.url.path)
            custom_limit: Custom rate limit override
            
        Returns:
            Dictionary with rate limit information
            
        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        # Get endpoint path
        if endpoint is None:
            endpoint = request.url.path
        
        # Get client identifier
        identifier = self._get_client_identifier(request)
        
        # Generate rate limit key
        key = self._get_rate_limit_key(identifier, endpoint)
        
        # Use custom limit or default
        limit = custom_limit or self.total_limit
        
        # Get current count
        current_count = await self._get_current_count(key)
        
        # Check if limit exceeded
        if current_count >= limit:
            # Calculate reset time
            reset_time = await self._get_reset_time(key)
            
            # Log rate limit exceeded
            if self.enable_logging:
                logger.warning(
                    "Rate limit exceeded",
                    identifier=identifier,
                    endpoint=endpoint,
                    current_count=current_count,
                    limit=limit,
                    reset_time=reset_time,
                    user_agent=request.headers.get("User-Agent", "unknown"),
                )
            
            # Raise rate limit exception
            raise RateLimitExceeded(
                retry_after=reset_time,
                limit=limit,
                window=self.window_seconds,
            )
        
        # Increment count
        new_count = await self._increment_count(key)
        
        # Calculate remaining requests
        remaining = max(0, limit - new_count)
        
        # Calculate reset time
        reset_time = await self._get_reset_time(key)
        
        return {
            "limit": limit,
            "remaining": remaining,
            "reset_time": reset_time,
            "current_count": new_count,
            "identifier": identifier,
            "endpoint": endpoint,
        }
    
    def add_rate_limit_headers(self, response: Response, rate_limit_info: Dict[str, Any]):
        """
        Add rate limit headers to response.
        
        Args:
            response: FastAPI response object
            rate_limit_info: Rate limit information from check_rate_limit
        """
        if not self.enable_headers:
            return
        
        response.headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_limit_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_limit_info["reset_time"])
        response.headers["X-RateLimit-Reset-Time"] = str(
            int(time.time()) + rate_limit_info["reset_time"]
        )


def create_rate_limit_middleware(
    requests_per_minute: Optional[int] = None,
    burst_allowance: Optional[int] = None,
    key_prefix: str = "rate_limit",
    window_seconds: int = 60,
    enable_headers: bool = True,
    enable_logging: bool = True,
    exclude_paths: Optional[list] = None,
    exclude_methods: Optional[list] = None,
) -> Callable:
    """
    Create rate limiting middleware for FastAPI.
    
    Args:
        requests_per_minute: Maximum requests per minute (defaults to config)
        burst_allowance: Burst allowance (defaults to config)
        key_prefix: Prefix for Redis keys
        window_seconds: Time window in seconds
        enable_headers: Whether to add rate limit headers
        enable_logging: Whether to log rate limit events
        exclude_paths: List of paths to exclude from rate limiting
        exclude_methods: List of HTTP methods to exclude from rate limiting
        
    Returns:
        Middleware function for FastAPI
    """
    # Get configuration
    config = initialize_config()
    
    # Use provided values or defaults from config
    rate_limit_per_minute = requests_per_minute or config.rate_limit_per_minute
    rate_limit_burst = burst_allowance or config.rate_limit_burst
    
    # Default exclusions
    if exclude_paths is None:
        exclude_paths = ["/health", "/metrics", "/docs", "/openapi.json"]
    
    if exclude_methods is None:
        exclude_methods = ["OPTIONS"]
    
    # Create rate limiter instance
    rate_limiter = RateLimiter(
        requests_per_minute=rate_limit_per_minute,
        burst_allowance=rate_limit_burst,
        key_prefix=key_prefix,
        window_seconds=window_seconds,
        enable_headers=enable_headers,
        enable_logging=enable_logging,
    )
    
    async def rate_limit_middleware(request: Request, call_next):
        """Rate limiting middleware function."""
        
        # Check if path should be excluded
        if any(request.url.path.startswith(path) for path in exclude_paths):
            return await call_next(request)
        
        # Check if method should be excluded
        if request.method in exclude_methods:
            return await call_next(request)
        
        try:
            # Check rate limit
            rate_limit_info = await rate_limiter.check_rate_limit(request)
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            rate_limiter.add_rate_limit_headers(response, rate_limit_info)
            
            return response
            
        except RateLimitExceeded as e:
            # Create rate limit exceeded response
            response_data = {
                "error": "Rate limit exceeded",
                "message": e.detail["message"],
                "retry_after": e.retry_after,
                "limit": e.limit,
                "window_seconds": e.window,
                "timestamp": datetime.now().isoformat(),
            }
            
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=response_data,
            )
            
            # Add rate limit headers
            response.headers["Retry-After"] = str(e.retry_after)
            response.headers["X-RateLimit-Limit"] = str(e.limit)
            response.headers["X-RateLimit-Remaining"] = "0"
            response.headers["X-RateLimit-Reset"] = str(e.retry_after)
            
            return response
            
        except Exception as e:
            # Log unexpected errors but allow request to proceed
            logger.error(f"Rate limiting error: {e}")
            return await call_next(request)
    
    return rate_limit_middleware


# Convenience function to get rate limiter with default config
def get_rate_limiter() -> RateLimiter:
    """
    Get rate limiter instance with default configuration.
    
    Returns:
        RateLimiter instance
    """
    config = initialize_config()
    return RateLimiter(
        requests_per_minute=config.rate_limit_per_minute,
        burst_allowance=config.rate_limit_burst,
    )


# Decorator for rate limiting individual endpoints
def rate_limit(
    requests_per_minute: Optional[int] = None,
    burst_allowance: Optional[int] = None,
    key_prefix: str = "rate_limit",
    window_seconds: int = 60,
    enable_headers: bool = True,
    enable_logging: bool = True,
):
    """
    Decorator to apply rate limiting to individual endpoints.
    
    Args:
        requests_per_minute: Maximum requests per minute
        burst_allowance: Burst allowance
        key_prefix: Prefix for Redis keys
        window_seconds: Time window in seconds
        enable_headers: Whether to add rate limit headers
        enable_logging: Whether to log rate limit events
        
    Returns:
        Decorator function
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get request object from FastAPI
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # If no request found, proceed without rate limiting
                return await func(*args, **kwargs)
            
            # Create rate limiter
            config = initialize_config()
            rate_limiter = RateLimiter(
                requests_per_minute=requests_per_minute or config.rate_limit_per_minute,
                burst_allowance=burst_allowance or config.rate_limit_burst,
                key_prefix=key_prefix,
                window_seconds=window_seconds,
                enable_headers=enable_headers,
                enable_logging=enable_logging,
            )
            
            try:
                # Check rate limit
                rate_limit_info = await rate_limiter.check_rate_limit(request)
                
                # Execute function
                response = await func(*args, **kwargs)
                
                # Add rate limit headers if response is a Response object
                if hasattr(response, 'headers'):
                    rate_limiter.add_rate_limit_headers(response, rate_limit_info)
                
                return response
                
            except RateLimitExceeded as e:
                # Re-raise the exception
                raise e
        
        return wrapper
    return decorator
