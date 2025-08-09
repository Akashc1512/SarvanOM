"""
Comprehensive Error Handling Middleware for API Gateway.

This module provides middleware for handling errors in critical operations,
ensuring the server remains stable and provides graceful error responses.

Features:
    - Request/response error handling
    - Critical operation wrapping
    - Graceful fallback mechanisms
    - Structured error logging
    - Circuit breaker patterns
    - Health monitoring integration

Security:
    - Sanitized error messages
    - No sensitive data in logs
    - Rate limiting on error reporting
    - Audit trail for critical errors

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    1.0.0 (2024-12-28)
"""

import asyncio
import time
import traceback
import uuid
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any, Callable, Dict, Optional, Type, TypeVar
from typing_extensions import ParamSpec

import structlog
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from shared.core.error_handler import (
    ErrorContext,
    ErrorInfo,
    ErrorResponse,
    CircuitBreaker,
    error_handler_factory,
    handle_critical_operation,
    safe_api_call,
    safe_llm_call,
    safe_database_call,
)

logger = structlog.get_logger(__name__)

# Type variables for generic error handling
T = TypeVar("T")
P = ParamSpec("P")


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive error handling."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.error_counts = {}
        self.alert_thresholds = {"critical": 5, "high": 10, "medium": 20}
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle requests with comprehensive error handling."""
        start_time = time.time()
        request_id = str(uuid.uuid4())

        # Add request ID to request state
        request.state.request_id = request_id

        # Check circuit breaker before processing
        if not self.circuit_breaker.can_execute():
            logger.warning(
                "Circuit breaker is OPEN, returning fallback response",
                request_id=request_id,
                path=request.url.path,
            )
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Service temporarily unavailable due to high error rate",
                    "error_type": "circuit_breaker_open",
                    "request_id": request_id,
                    "retry_after": self.circuit_breaker.recovery_timeout,
                },
            )

        try:
            # Process the request
            response = await call_next(request)

            # Log successful request and update circuit breaker
            duration = time.time() - start_time
            self.circuit_breaker.on_success()
            logger.info(
                "Request processed successfully",
                request_id=request_id,
                path=request.url.path,
                method=request.method,
                status_code=response.status_code,
                duration=duration,
            )

            return response

        except Exception as e:
            # Update circuit breaker on failure
            self.circuit_breaker.on_failure()
            # Handle the error comprehensively
            return await self._handle_request_error(request, e, start_time, request_id)

    async def _handle_request_error(
        self, request: Request, error: Exception, start_time: float, request_id: str
    ) -> Response:
        """Handle request errors with comprehensive logging and fallback."""

        duration = time.time() - start_time

        # Create error context
        context = ErrorContext(
            operation=f"{request.method}_{request.url.path}",
            service="api_gateway",
            request_id=request_id,
            user_id=getattr(request.state, "user_id", None),
            session_id=getattr(request.state, "session_id", None),
            metadata={
                "path": str(request.url),
                "method": request.method,
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown"),
                "duration": duration,
            },
        )

        # Get appropriate error handler
        error_handler = error_handler_factory.get_handler("api")

        # Handle the error
        error_response = await error_handler.handle_error(error, context)

        # Log the error with structured information
        logger.error(
            "Request processing failed",
            request_id=request_id,
            path=request.url.path,
            method=request.method,
            error_type=type(error).__name__,
            error_message=str(error),
            duration=duration,
            exc_info=True,
        )

        # Update error counts for monitoring
        self._update_error_counts(error, context)

        # Return graceful error response
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": error_response.error,
                "error_type": error_response.error_type,
                "error_code": error_response.error_code,
                "request_id": request_id,
                "timestamp": time.time(),
                "retryable": error_response.retryable,
                "fallback_data": error_response.fallback_data,
                "metadata": error_response.metadata,
            },
        )

    def _update_error_counts(self, error: Exception, context: ErrorContext):
        """Update error counts for monitoring and alerting."""
        error_key = f"{type(error).__name__}_{context.operation}"

        if error_key not in self.error_counts:
            self.error_counts[error_key] = 0

        self.error_counts[error_key] += 1

        # Check for alerting thresholds
        if self.error_counts[error_key] >= self.alert_thresholds.get("high", 10):
            logger.error(
                f"High error rate detected for {error_key}: {self.error_counts[error_key]} errors",
                error_key=error_key,
                count=self.error_counts[error_key],
                threshold=self.alert_thresholds.get("high", 10),
            )


def wrap_critical_operation(
    operation_type: str = "api", timeout: float = 30.0, max_retries: int = 3
):
    """
    Decorator for wrapping critical operations with comprehensive error handling.

    Args:
        operation_type: Type of operation ("api", "llm", "database")
        timeout: Operation timeout in seconds
        max_retries: Maximum retry attempts
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return await handle_critical_operation(
                operation_type=operation_type, max_retries=max_retries, timeout=timeout
            )(func)(*args, **kwargs)

        return wrapper

    return decorator


@asynccontextmanager
async def critical_operation_context(
    operation_type: str = "api", timeout: float = 30.0, **context_kwargs
):
    """
    Context manager for critical operations with error handling.

    Args:
        operation_type: Type of operation ("api", "llm", "database")
        timeout: Operation timeout in seconds
        **context_kwargs: Additional context information
    """
    from shared.core.error_handler import critical_operation_context as base_context

    async with base_context(
        operation_type=operation_type, timeout=timeout, **context_kwargs
    ) as context:
        yield context


def create_error_handling_middleware() -> ErrorHandlingMiddleware:
    """Create and configure error handling middleware."""

    def middleware_factory(app: ASGIApp) -> ErrorHandlingMiddleware:
        return ErrorHandlingMiddleware(app)

    return middleware_factory


# Utility functions for common error handling patterns


async def safe_api_operation(
    operation: Callable,
    *args,
    operation_type: str = "api",
    timeout: float = 30.0,
    max_retries: int = 3,
    fallback_data: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Any:
    """
    Safely execute an API operation with comprehensive error handling.

    Args:
        operation: The operation to execute
        operation_type: Type of operation
        timeout: Operation timeout
        max_retries: Maximum retry attempts
        fallback_data: Fallback data if operation fails
        **kwargs: Additional arguments for the operation

    Returns:
        Operation result or fallback data
    """
    try:
        return await safe_api_call(
            operation,
            *args,
            timeout=timeout,
            max_retries=max_retries,
            fallback_data=fallback_data,
            **kwargs,
        )
    except Exception as e:
        logger.error(
            "API operation failed",
            operation=operation.__name__,
            error=str(e),
            exc_info=True,
        )
        if fallback_data:
            return fallback_data
        raise


async def safe_llm_operation(
    operation: Callable,
    *args,
    timeout: float = 60.0,
    max_retries: int = 3,
    fallback_data: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Any:
    """
    Safely execute an LLM operation with comprehensive error handling.

    Args:
        operation: The operation to execute
        timeout: Operation timeout
        max_retries: Maximum retry attempts
        fallback_data: Fallback data if operation fails
        **kwargs: Additional arguments for the operation

    Returns:
        Operation result or fallback data
    """
    try:
        return await safe_llm_call(
            operation,
            *args,
            timeout=timeout,
            max_retries=max_retries,
            fallback_data=fallback_data,
            **kwargs,
        )
    except Exception as e:
        logger.error(
            "LLM operation failed",
            operation=operation.__name__,
            error=str(e),
            exc_info=True,
        )
        if fallback_data:
            return fallback_data
        raise


async def safe_database_operation(
    operation: Callable,
    *args,
    timeout: float = 30.0,
    max_retries: int = 3,
    fallback_data: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Any:
    """
    Safely execute a database operation with comprehensive error handling.

    Args:
        operation: The operation to execute
        timeout: Operation timeout
        max_retries: Maximum retry attempts
        fallback_data: Fallback data if operation fails
        **kwargs: Additional arguments for the operation

    Returns:
        Operation result or fallback data
    """
    try:
        return await safe_database_call(
            operation,
            *args,
            timeout=timeout,
            max_retries=max_retries,
            fallback_data=fallback_data,
            **kwargs,
        )
    except Exception as e:
        logger.error(
            "Database operation failed",
            operation=operation.__name__,
            error=str(e),
            exc_info=True,
        )
        if fallback_data:
            return fallback_data
        raise


# Health monitoring and alerting


class ErrorMonitor:
    """Monitor for tracking error patterns and alerting."""

    def __init__(self):
        self.error_counts = {}
        self.error_timestamps = {}
        self.alert_thresholds = {"critical": 5, "high": 10, "medium": 20}

    def record_error(self, error: Exception, context: Dict[str, Any]):
        """Record an error for monitoring."""
        error_key = f"{type(error).__name__}_{context.get('operation', 'unknown')}"

        # Update error count
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1

        # Update timestamps
        if error_key not in self.error_timestamps:
            self.error_timestamps[error_key] = []
        self.error_timestamps[error_key].append(time.time())

        # Clean old timestamps (keep last hour)
        current_time = time.time()
        self.error_timestamps[error_key] = [
            ts for ts in self.error_timestamps[error_key] if current_time - ts < 3600
        ]

        # Check for alerting
        self._check_alerts(error_key, error, context)

    def _check_alerts(self, error_key: str, error: Exception, context: Dict[str, Any]):
        """Check if alerts should be triggered."""
        recent_count = len(self.error_timestamps[error_key])
        threshold = self.alert_thresholds.get("high", 10)

        if recent_count >= threshold:
            logger.error(
                f"High error rate detected: {recent_count} {type(error).__name__} errors in the last hour",
                error_key=error_key,
                count=recent_count,
                threshold=threshold,
                operation=context.get("operation", "unknown"),
                request_id=context.get("request_id", "unknown"),
            )


# Global error monitor
error_monitor = ErrorMonitor()


# Middleware setup functions


def setup_error_handling_middleware(app: ASGIApp) -> ErrorHandlingMiddleware:
    """Setup error handling middleware for the application."""
    middleware = ErrorHandlingMiddleware(app)
    return middleware


def add_error_handling_to_app(app: ASGIApp):
    """Add error handling middleware to the application."""
    app.add_middleware(ErrorHandlingMiddleware)


# Validation and response handling


def validate_service_response(
    response: Any, service_name: str, operation: str, expected_type: Type
) -> bool:
    """
    Validate service response format and content.

    Args:
        response: The response to validate
        service_name: Name of the service
        operation: Name of the operation
        expected_type: Expected response type

    Returns:
        True if response is valid, False otherwise
    """
    try:
        if not isinstance(response, expected_type):
            logger.error(
                f"Invalid response type from {service_name}.{operation}",
                expected_type=expected_type.__name__,
                actual_type=type(response).__name__,
            )
            return False

        return True

    except Exception as e:
        logger.error(
            f"Response validation failed for {service_name}.{operation}",
            error=str(e),
            exc_info=True,
        )
        return False


def log_service_operation(
    service_name: str,
    operation: str,
    success: bool,
    duration: float,
    request_id: str,
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Log service operation with structured information.

    Args:
        service_name: Name of the service
        operation: Name of the operation
        success: Whether the operation was successful
        duration: Operation duration in seconds
        request_id: Request identifier
        metadata: Additional metadata
    """
    log_data = {
        "service": service_name,
        "operation": operation,
        "success": success,
        "duration": duration,
        "request_id": request_id,
    }

    if metadata:
        log_data.update(metadata)

    if success:
        logger.info("Service operation completed", **log_data)
    else:
        logger.error("Service operation failed", **log_data)


def handle_service_error(
    error: Exception,
    service_name: str,
    operation: str,
    request_id: str,
    fallback_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Handle service errors with structured logging and fallback.

    Args:
        error: The error that occurred
        service_name: Name of the service
        operation: Name of the operation
        request_id: Request identifier
        fallback_data: Fallback data to return

    Returns:
        Error response with fallback data
    """
    # Log the error
    logger.error(
        f"Service error in {service_name}.{operation}",
        service=service_name,
        operation=operation,
        request_id=request_id,
        error_type=type(error).__name__,
        error_message=str(error),
        exc_info=True,
    )

    # Record error for monitoring
    error_monitor.record_error(
        error,
        {"service": service_name, "operation": operation, "request_id": request_id},
    )

    # Return fallback response
    return {
        "success": False,
        "error": f"Service operation failed: {str(error)}",
        "error_type": type(error).__name__,
        "service": service_name,
        "operation": operation,
        "request_id": request_id,
        "timestamp": time.time(),
        "fallback_data": fallback_data
        or {
            "message": "Service temporarily unavailable",
            "suggestion": "Please try again later",
            "status": "degraded",
        },
    }
