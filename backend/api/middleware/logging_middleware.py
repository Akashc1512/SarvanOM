"""
FastAPI middleware for request/response logging and observability.

Provides structured logging for all HTTP requests with correlation IDs,
performance metrics, and error tracking.
"""

import time
import json
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from shared.core.logging import get_logger, set_request_id, get_request_id


logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive request/response logging."""

    def __init__(self, app, include_headers: bool = False, include_body: bool = False):
        super().__init__(app)
        self.include_headers = include_headers
        self.include_body = include_body

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = set_request_id()
        else:
            set_request_id(request_id)

        # Log request start
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
            client_ip=client_ip,
            user_agent=user_agent,
            request_id=request_id,
        )

        # Log headers if enabled (excluding sensitive ones)
        if self.include_headers:
            safe_headers = {
                k: v
                for k, v in request.headers.items()
                if k.lower() not in {"authorization", "cookie", "x-api-key"}
            }
            logger.debug("Request headers", headers=safe_headers, request_id=request_id)

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log successful response
            logger.info(
                "Request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=int(duration * 1000),
                request_id=request_id,
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration:.3f}s"

            return response

        except Exception as e:
            # Calculate duration for error case
            duration = time.time() - start_time

            # Log error
            logger.error(
                "Request failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=int(duration * 1000),
                request_id=request_id,
            )

            # Return error response
            error_response = JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "request_id": request_id,
                    "timestamp": time.time(),
                },
            )
            error_response.headers["X-Request-ID"] = request_id
            error_response.headers["X-Response-Time"] = f"{duration:.3f}s"

            return error_response


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring and metrics."""

    def __init__(self, app, metrics_service=None):
        super().__init__(app)
        self.metrics_service = metrics_service

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Record request start
        if self.metrics_service:
            self.metrics_service.increment_counter(
                "http_requests_total",
                {
                    "method": request.method,
                    "path": request.url.path,
                    "status": "started",
                },
            )

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Record successful request
            if self.metrics_service:
                self.metrics_service.increment_counter(
                    "http_requests_total",
                    {
                        "method": request.method,
                        "path": request.url.path,
                        "status": "success",
                    },
                )
                self.metrics_service.record_histogram(
                    "http_request_duration_seconds",
                    duration,
                    {"method": request.method, "path": request.url.path},
                )

            return response

        except Exception as e:
            duration = time.time() - start_time

            # Record failed request
            if self.metrics_service:
                self.metrics_service.increment_counter(
                    "http_requests_total",
                    {
                        "method": request.method,
                        "path": request.url.path,
                        "status": "error",
                    },
                )
                self.metrics_service.increment_counter(
                    "http_errors_total",
                    {
                        "method": request.method,
                        "path": request.url.path,
                        "error_type": type(e).__name__,
                    },
                )

            raise


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive error logging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            # Log detailed error information
            logger.error(
                "Unhandled exception in request",
                method=request.method,
                path=request.url.path,
                error=str(e),
                error_type=type(e).__name__,
                request_id=get_request_id(),
                client_ip=request.client.host if request.client else "unknown",
                user_agent=request.headers.get("user-agent", "unknown"),
            )

            # Re-raise to let other middleware handle it
            raise
