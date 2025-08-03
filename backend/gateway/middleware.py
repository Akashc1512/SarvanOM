"""
Gateway Middleware
Middleware components for the API gateway.

This module provides:
- Authentication middleware
- Rate limiting middleware
- Logging middleware
- CORS middleware
- Error handling middleware
"""

import time
import logging
from typing import Callable, Optional
from fastapi import Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for handling authentication."""
    
    def __init__(self, app, auth_service):
        super().__init__(app)
        self.auth_service = auth_service
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip authentication for public endpoints
        public_paths = ["/health", "/docs", "/openapi.json", "/auth/login", "/auth/register"]
        
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)
        
        # Extract token from headers
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        token = auth_header.split(" ")[1]
        
        try:
            # Validate token
            user = await self.auth_service.validate_token(token)
            request.state.user = user
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return await call_next(request)

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""
    
    def __init__(self, app, rate_limiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Get client identifier (IP or user ID)
        client_id = request.client.host
        if hasattr(request.state, 'user'):
            client_id = request.state.user.get('user_id', client_id)
        
        # Check rate limit
        try:
            allowed = await self.rate_limiter.check_rate_limit(client_id)
            if not allowed:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"}
                )
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Continue without rate limiting if there's an error
        
        return await call_next(request)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
        
        # Add processing time to response headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling errors."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Unexpected error: {e}")
            
            # Return generic error response
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for additional security headers."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

def setup_middleware(app, auth_service=None, rate_limiter=None):
    """Setup all middleware for the application."""
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:8000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add security middleware
    app.add_middleware(SecurityMiddleware)
    
    # Add error handling middleware
    app.add_middleware(ErrorHandlingMiddleware)
    
    # Add logging middleware
    app.add_middleware(LoggingMiddleware)
    
    # Add rate limiting middleware if rate limiter is provided
    if rate_limiter:
        app.add_middleware(RateLimitingMiddleware, rate_limiter=rate_limiter)
    
    # Add authentication middleware if auth service is provided
    if auth_service:
        app.add_middleware(AuthenticationMiddleware, auth_service=auth_service) 