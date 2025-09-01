#!/usr/bin/env python3
"""
Observability Middleware System

Provides comprehensive monitoring, logging, and tracing capabilities:
- Request ID injection and propagation
- Structured JSON logging with trace IDs
- Prometheus metrics collection
- Performance monitoring and alerting
- Distributed tracing support

Following enterprise standards for observability and monitoring.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from contextvars import ContextVar
import os

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Configure structured logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
session_id_var: ContextVar[Optional[str]] = ContextVar('session_id', default=None)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code', 'service']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint', 'service']
)

ACTIVE_REQUESTS = Gauge(
    'http_active_requests',
    'Number of active HTTP requests',
    ['service']
)

LLM_CALLS = Counter(
    'llm_calls_total',
    'Total LLM API calls',
    ['provider', 'model', 'status', 'service']
)

LLM_DURATION = Histogram(
    'llm_call_duration_seconds',
    'LLM API call duration in seconds',
    ['provider', 'model', 'service']
)

CACHE_HITS = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type', 'service']
)

CACHE_MISSES = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type', 'service']
)

STREAM_EVENTS = Counter(
    'stream_events_total',
    'Total streaming events',
    ['event_type', 'service']
)

ERROR_COUNT = Counter(
    'errors_total',
    'Total errors',
    ['error_type', 'service']
)


@dataclass
class RequestContext:
    """Request context for tracking and observability."""
    request_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive observability and monitoring."""
    
    def __init__(self, app: ASGIApp, service_name: str = "sarvanom-gateway"):
        super().__init__(app)
        self.service_name = service_name
        self.logger = logging.getLogger(f"{service_name}.middleware")
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
        
        # Extract user and session info
        user_id = self._extract_user_id(request)
        session_id = self._extract_session_id(request)
        
        user_id_var.set(user_id)
        session_id_var.set(session_id)
        
        # Create request context
        context = RequestContext(
            request_id=request_id,
            user_id=user_id,
            session_id=session_id,
            metadata={
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", ""),
            }
        )
        
        # Start timing
        start_time = time.time()
        ACTIVE_REQUESTS.labels(service=self.service_name).inc()
        
        try:
            # Log request start
            self._log_request_start(context)
            
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Record metrics
            self._record_request_metrics(request, response, duration)
            
            # Log request completion
            self._log_request_complete(context, response, duration)
            
            # Add trace headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Record error metrics
            ERROR_COUNT.labels(error_type=type(e).__name__, service=self.service_name).inc()
            
            # Log error
            self._log_request_error(context, e, duration)
            
            # Re-raise exception
            raise
            
        finally:
            # Decrement active requests
            ACTIVE_REQUESTS.labels(service=self.service_name).dec()
    
    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request headers or query params."""
        # Check Authorization header
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # In a real implementation, you would decode the JWT here
            # For now, we'll extract from query params
            pass
        
        # Check query parameters
        return request.query_params.get("user_id")
    
    def _extract_session_id(self, request: Request) -> Optional[str]:
        """Extract session ID from request."""
        return request.query_params.get("session_id") or request.headers.get("X-Session-ID")
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _log_request_start(self, context: RequestContext):
        """Log request start with structured data."""
        log_data = {
            "timestamp": context.start_time.isoformat(),
            "level": "INFO",
            "request_id": context.request_id,
            "user_id": context.user_id,
            "session_id": context.session_id,
            "event": "request_start",
            "method": context.metadata["method"],
            "url": context.metadata["url"],
            "client_ip": context.metadata["client_ip"],
            "user_agent": context.metadata["user_agent"],
            "service": self.service_name,
        }
        
        self.logger.info(json.dumps(log_data))
    
    def _log_request_complete(self, context: RequestContext, response: Response, duration: float):
        """Log request completion with structured data."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "INFO",
            "request_id": context.request_id,
            "user_id": context.user_id,
            "session_id": context.session_id,
            "event": "request_complete",
            "method": context.metadata["method"],
            "url": context.metadata["url"],
            "status_code": response.status_code,
            "duration_seconds": duration,
            "service": self.service_name,
        }
        
        self.logger.info(json.dumps(log_data))
    
    def _log_request_error(self, context: RequestContext, error: Exception, duration: float):
        """Log request error with structured data."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "ERROR",
            "request_id": context.request_id,
            "user_id": context.user_id,
            "session_id": context.session_id,
            "event": "request_error",
            "method": context.metadata["method"],
            "url": context.metadata["url"],
            "error_type": type(error).__name__,
            "error_message": str(error),
            "duration_seconds": duration,
            "service": self.service_name,
        }
        
        self.logger.error(json.dumps(log_data))
    
    def _record_request_metrics(self, request: Request, response: Response, duration: float):
        """Record Prometheus metrics for the request."""
        endpoint = request.url.path
        if len(endpoint) > 50:  # Truncate long endpoints
            endpoint = endpoint[:47] + "..."
        
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status_code=response.status_code,
            service=self.service_name
        ).inc()
        
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=endpoint,
            service=self.service_name
        ).observe(duration)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for exposing Prometheus metrics endpoint."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path == "/metrics":
            return Response(
                content=generate_latest(),
                media_type=CONTENT_TYPE_LATEST,
                headers={"Cache-Control": "no-cache"}
            )
        
        return await call_next(request)


# Utility functions for observability
def get_request_id() -> Optional[str]:
    """Get current request ID from context."""
    return request_id_var.get()


def get_user_id() -> Optional[str]:
    """Get current user ID from context."""
    return user_id_var.get()


def get_session_id() -> Optional[str]:
    """Get current session ID from context."""
    return session_id_var.get()


def log_llm_call(provider: str, model: str, duration: float, success: bool, error_message: Optional[str] = None):
    """Log LLM API call metrics."""
    status = "success" if success else "error"
    
    LLM_CALLS.labels(
        provider=provider,
        model=model,
        status=status,
        service="sarvanom-gateway"
    ).inc()
    
    LLM_DURATION.labels(
        provider=provider,
        model=model,
        service="sarvanom-gateway"
    ).observe(duration)
    
    # Structured logging
    log_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": "INFO" if success else "ERROR",
        "request_id": get_request_id(),
        "user_id": get_user_id(),
        "event": "llm_call",
        "provider": provider,
        "model": model,
        "duration_seconds": duration,
        "success": success,
        "error_message": error_message,
        "service": "sarvanom-gateway",
    }
    
    logger.info(json.dumps(log_data))


def log_cache_event(cache_type: str, hit: bool):
    """Log cache hit/miss metrics."""
    if hit:
        CACHE_HITS.labels(cache_type=cache_type, service="sarvanom-gateway").inc()
    else:
        CACHE_MISSES.labels(cache_type=cache_type, service="sarvanom-gateway").inc()
    
    # Structured logging
    log_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": "INFO",
        "request_id": get_request_id(),
        "user_id": get_user_id(),
        "event": "cache_event",
        "cache_type": cache_type,
        "hit": hit,
        "service": "sarvanom-gateway",
    }
    
    logger.info(json.dumps(log_data))


def log_stream_event(event_type: str, stream_id: str, metadata: Optional[Dict[str, Any]] = None):
    """Log streaming event metrics."""
    STREAM_EVENTS.labels(event_type=event_type, service="sarvanom-gateway").inc()
    
    # Structured logging
    log_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": "INFO",
        "request_id": get_request_id(),
        "user_id": get_user_id(),
        "event": "stream_event",
        "event_type": event_type,
        "stream_id": stream_id,
        "metadata": metadata or {},
        "service": "sarvanom-gateway",
    }
    
    logger.info(json.dumps(log_data))


def log_error(error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None):
    """Log error with structured data."""
    ERROR_COUNT.labels(error_type=error_type, service="sarvanom-gateway").inc()
    
    # Structured logging
    log_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": "ERROR",
        "request_id": get_request_id(),
        "user_id": get_user_id(),
        "event": "error",
        "error_type": error_type,
        "error_message": error_message,
        "context": context or {},
        "service": "sarvanom-gateway",
    }
    
    logger.error(json.dumps(log_data))


# Performance monitoring decorator
def monitor_performance(operation_name: str):
    """Decorator for monitoring function performance."""
    def decorator(func: Callable):
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log performance
                log_data = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": "INFO",
                    "request_id": get_request_id(),
                    "user_id": get_user_id(),
                    "event": "performance",
                    "operation": operation_name,
                    "duration_seconds": duration,
                    "success": True,
                    "service": "sarvanom-gateway",
                }
                logger.info(json.dumps(log_data))
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                # Log error
                log_data = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": "ERROR",
                    "request_id": get_request_id(),
                    "user_id": get_user_id(),
                    "event": "performance",
                    "operation": operation_name,
                    "duration_seconds": duration,
                    "success": False,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "service": "sarvanom-gateway",
                }
                logger.error(json.dumps(log_data))
                
                raise
        
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log performance
                log_data = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": "INFO",
                    "request_id": get_request_id(),
                    "user_id": get_user_id(),
                    "event": "performance",
                    "operation": operation_name,
                    "duration_seconds": duration,
                    "success": True,
                    "service": "sarvanom-gateway",
                }
                logger.info(json.dumps(log_data))
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                # Log error
                log_data = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": "ERROR",
                    "request_id": get_request_id(),
                    "user_id": get_user_id(),
                    "event": "performance",
                    "operation": operation_name,
                    "duration_seconds": duration,
                    "success": False,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "service": "sarvanom-gateway",
                }
                logger.error(json.dumps(log_data))
                
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
