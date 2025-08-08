"""
Error Handling Middleware

This module contains comprehensive error handling middleware for the FastAPI application.
Provides structured error responses, logging, and monitoring integration.
"""

import logging
import traceback
import time
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError

from ...services.core.metrics_service import MetricsService

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive error handling middleware.
    
    Catches and handles all exceptions, providing consistent error responses
    and detailed logging for debugging and monitoring.
    """
    
    def __init__(self, app, metrics_service: Optional[MetricsService] = None):
        super().__init__(app)
        self.metrics_service = metrics_service
        self.error_counts = {}
    
    async def dispatch(self, request: Request, call_next):
        """Process request and handle any errors."""
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Track successful requests
            if self.metrics_service:
                processing_time = time.time() - start_time
                await self.metrics_service.track_request_success(
                    method=request.method,
                    path=str(request.url.path),
                    status_code=response.status_code,
                    processing_time=processing_time
                )
            
            return response
            
        except HTTPException as e:
            # Handle known HTTP exceptions
            processing_time = time.time() - start_time
            
            error_response = await self._handle_http_exception(
                request, e, processing_time
            )
            
            if self.metrics_service:
                await self.metrics_service.track_request_error(
                    method=request.method,
                    path=str(request.url.path),
                    status_code=e.status_code,
                    error_type="HTTPException",
                    processing_time=processing_time
                )
            
            return error_response
            
        except ValidationError as e:
            # Handle Pydantic validation errors
            processing_time = time.time() - start_time
            
            error_response = await self._handle_validation_error(
                request, e, processing_time
            )
            
            if self.metrics_service:
                await self.metrics_service.track_request_error(
                    method=request.method,
                    path=str(request.url.path),
                    status_code=422,
                    error_type="ValidationError",
                    processing_time=processing_time
                )
            
            return error_response
            
        except Exception as e:
            # Handle unexpected exceptions
            processing_time = time.time() - start_time
            
            error_response = await self._handle_unexpected_error(
                request, e, processing_time
            )
            
            if self.metrics_service:
                await self.metrics_service.track_request_error(
                    method=request.method,
                    path=str(request.url.path),
                    status_code=500,
                    error_type=type(e).__name__,
                    processing_time=processing_time
                )
            
            return error_response
    
    async def _handle_http_exception(
        self, 
        request: Request, 
        exc: HTTPException, 
        processing_time: float
    ) -> JSONResponse:
        """Handle HTTP exceptions with structured response."""
        
        request_id = getattr(request.state, "request_id", "unknown")
        
        error_data = {
            "error": {
                "type": "HTTPException",
                "message": exc.detail,
                "status_code": exc.status_code
            },
            "request": {
                "method": request.method,
                "path": str(request.url.path),
                "request_id": request_id
            },
            "timestamp": datetime.now().isoformat(),
            "processing_time": round(processing_time, 3)
        }
        
        # Log error
        logger.warning(
            f"HTTP {exc.status_code} error on {request.method} {request.url.path}: {exc.detail}",
            extra={
                "request_id": request_id,
                "status_code": exc.status_code,
                "processing_time": processing_time
            }
        )
        
        # Track error frequency
        error_key = f"{exc.status_code}:{str(request.url.path)}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_data
        )
    
    async def _handle_validation_error(
        self, 
        request: Request, 
        exc: ValidationError, 
        processing_time: float
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Extract validation error details
        validation_errors = []
        for error in exc.errors():
            validation_errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
                "input": error.get("input")
            })
        
        error_data = {
            "error": {
                "type": "ValidationError",
                "message": "Request validation failed",
                "details": validation_errors
            },
            "request": {
                "method": request.method,
                "path": str(request.url.path),
                "request_id": request_id
            },
            "timestamp": datetime.now().isoformat(),
            "processing_time": round(processing_time, 3)
        }
        
        # Log validation error
        logger.warning(
            f"Validation error on {request.method} {request.url.path}: {len(validation_errors)} errors",
            extra={
                "request_id": request_id,
                "validation_errors": validation_errors,
                "processing_time": processing_time
            }
        )
        
        return JSONResponse(
            status_code=422,
            content=error_data
        )
    
    async def _handle_unexpected_error(
        self, 
        request: Request, 
        exc: Exception, 
        processing_time: float
    ) -> JSONResponse:
        """Handle unexpected exceptions."""
        
        request_id = getattr(request.state, "request_id", "unknown")
        error_id = f"err_{int(time.time())}_{hash(str(exc)) % 10000:04d}"
        
        # Get stack trace
        stack_trace = traceback.format_exc()
        
        error_data = {
            "error": {
                "type": "InternalServerError",
                "message": "An unexpected error occurred",
                "error_id": error_id,
                "details": str(exc) if logger.level <= logging.DEBUG else None
            },
            "request": {
                "method": request.method,
                "path": str(request.url.path),
                "request_id": request_id
            },
            "timestamp": datetime.now().isoformat(),
            "processing_time": round(processing_time, 3)
        }
        
        # Log error with full details
        logger.error(
            f"Unexpected error {error_id} on {request.method} {request.url.path}: {type(exc).__name__}: {exc}",
            extra={
                "request_id": request_id,
                "error_id": error_id,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "stack_trace": stack_trace,
                "processing_time": processing_time
            },
            exc_info=True
        )
        
        # Track critical error
        error_key = f"500:{type(exc).__name__}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        return JSONResponse(
            status_code=500,
            content=error_data
        )
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        return {
            "error_counts": dict(self.error_counts),
            "total_errors": sum(self.error_counts.values()),
            "unique_error_types": len(self.error_counts),
            "timestamp": datetime.now().isoformat()
        }


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Security headers middleware.
    
    Adds security headers to all responses for better security posture.
    """
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers to response."""
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # Remove server header
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Request logging middleware.
    
    Logs all incoming requests with detailed information for monitoring and debugging.
    """
    
    def __init__(self, app, metrics_service: Optional[MetricsService] = None):
        super().__init__(app)
        self.metrics_service = metrics_service
    
    async def dispatch(self, request: Request, call_next):
        """Log request details."""
        start_time = time.time()
        
        # Generate request ID if not exists
        if not hasattr(request.state, "request_id"):
            import uuid
            request.state.request_id = str(uuid.uuid4())
        
        request_id = request.state.request_id
        
        # Log incoming request
        logger.info(
            f"📥 {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
                "query_params": str(request.query_params),
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"📤 {response.status_code} - {processing_time:.3f}s",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "processing_time": processing_time
            }
        )
        
        # Add processing time to response headers
        response.headers["X-Process-Time"] = str(round(processing_time, 3))
        response.headers["X-Request-ID"] = request_id
        
        return response


class CORSMiddleware(BaseHTTPMiddleware):
    """
    Custom CORS middleware with enhanced configuration.
    """
    
    def __init__(
        self, 
        app,
        allowed_origins: list = None,
        allowed_methods: list = None,
        allowed_headers: list = None,
        allow_credentials: bool = True
    ):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["*"]
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allowed_headers = allowed_headers or ["*"]
        self.allow_credentials = allow_credentials
    
    async def dispatch(self, request: Request, call_next):
        """Handle CORS."""
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
            return self._add_cors_headers(response, request)
        
        # Process request
        response = await call_next(request)
        
        # Add CORS headers
        return self._add_cors_headers(response, request)
    
    def _add_cors_headers(self, response: Response, request: Request) -> Response:
        """Add CORS headers to response."""
        
        origin = request.headers.get("origin")
        
        # Check if origin is allowed
        if self.allowed_origins == ["*"] or origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin or "*"
        
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)
        
        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        response.headers["Access-Control-Max-Age"] = "86400"  # 24 hours
        
        return response
