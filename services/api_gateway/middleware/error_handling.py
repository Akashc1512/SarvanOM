"""
Error Handling Middleware for Universal Knowledge Platform

This module provides comprehensive error handling middleware that:
- Catches and logs all exceptions with context
- Converts exceptions to appropriate HTTP responses
- Provides standardized error response format
- Includes request tracking and debugging information
- Handles different types of errors appropriately

Features:
- Global exception handling
- Request context preservation
- Structured error logging
- Security-conscious error messages
- Performance monitoring integration
"""

import logging
from shared.core.unified_logging import get_logger
import time
import traceback
from typing import Dict, Any, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from pydantic import ValidationError

from shared.core.api.exceptions import (
    UKPHTTPException, AuthenticationError, AuthorizationError,
    ResourceNotFoundError, DatabaseError, ExternalServiceError,
    QueryProcessingError, ValidationError as UKPValidationError
)

logger = get_logger(__name__)


class ErrorHandlingMiddleware:
    """Middleware for comprehensive error handling."""
    
    def __init__(self):
        self.error_counts = {}
        self.error_types = {}
    
    async def __call__(self, request: Request, call_next):
        """Process request with comprehensive error handling."""
        start_time = time.time()
        request_id = getattr(request.state, "request_id", f"req_{int(time.time() * 1000)}")
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Log successful requests (optional)
            processing_time = time.time() - start_time
            if processing_time > 1.0:  # Log slow requests
                logger.warning(
                    f"Slow request: {request.method} {request.url} - {processing_time:.2f}s",
                    extra={"request_id": request_id, "processing_time": processing_time}
                )
            
            return response
            
        except HTTPException as exc:
            # HTTP exceptions are already properly formatted
            return await self._handle_http_exception(request, exc, start_time, request_id)
            
        except ValidationError as exc:
            # Pydantic validation errors
            return await self._handle_validation_error(request, exc, start_time, request_id)
            
        except UKPHTTPException as exc:
            # Custom HTTP exceptions
            return await self._handle_ukp_http_exception(request, exc, start_time, request_id)
            
        except (ConnectionError, TimeoutError) as exc:
            # Connection and timeout errors
            return await self._handle_connection_error(request, exc, start_time, request_id)
            
        except (ValueError, TypeError) as exc:
            # Validation errors
            return await self._handle_validation_error(request, exc, start_time, request_id)
            
        except (PermissionError, OSError) as exc:
            # Permission and system errors
            return await self._handle_permission_error(request, exc, start_time, request_id)
            
        except Exception as exc:
            # Generic exceptions
            return await self._handle_generic_exception(request, exc, start_time, request_id)
    
    async def _handle_http_exception(
        self, request: Request, exc: HTTPException, start_time: float, request_id: str
    ) -> JSONResponse:
        """Handle HTTP exceptions."""
        processing_time = time.time() - start_time
        
        logger.warning(
            f"HTTP {exc.status_code}: {exc.detail}",
            extra={
                "request_id": request_id,
                "path": str(request.url),
                "method": request.method,
                "status_code": exc.status_code,
                "processing_time": processing_time
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "status_code": exc.status_code,
                "timestamp": time.time(),
                "path": str(request.url),
                "request_id": request_id,
                "error_type": "http_exception",
                "processing_time": processing_time
            }
        )
    
    async def _handle_validation_error(
        self, request: Request, exc: ValidationError, start_time: float, request_id: str
    ) -> JSONResponse:
        """Handle validation errors."""
        processing_time = time.time() - start_time
        
        logger.warning(
            f"Validation error: {exc.errors()}",
            extra={
                "request_id": request_id,
                "path": str(request.url),
                "method": request.method,
                "processing_time": processing_time,
                "validation_errors": exc.errors()
            }
        )
        
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "status_code": 422,
                "timestamp": time.time(),
                "path": str(request.url),
                "request_id": request_id,
                "error_type": "validation_error",
                "processing_time": processing_time,
                "details": exc.errors()
            }
        )
    
    async def _handle_ukp_http_exception(
        self, request: Request, exc: UKPHTTPException, start_time: float, request_id: str
    ) -> JSONResponse:
        """Handle custom HTTP exceptions."""
        processing_time = time.time() - start_time
        
        logger.error(
            f"UKP HTTP {exc.status_code}: {exc.internal_message}",
            extra={
                "request_id": request_id,
                "path": str(request.url),
                "method": request.method,
                "status_code": exc.status_code,
                "processing_time": processing_time,
                "internal_message": exc.internal_message
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "status_code": exc.status_code,
                "timestamp": time.time(),
                "path": str(request.url),
                "request_id": request_id,
                "error_type": "ukp_http_exception",
                "processing_time": processing_time
            },
            headers=exc.headers
        )
    
    async def _handle_connection_error(
        self, request: Request, exc: Exception, start_time: float, request_id: str
    ) -> JSONResponse:
        """Handle connection and timeout errors."""
        processing_time = time.time() - start_time
        
        logger.error(
            f"Connection error: {str(exc)}",
            extra={
                "request_id": request_id,
                "path": str(request.url),
                "method": request.method,
                "processing_time": processing_time,
                "error_type": type(exc).__name__
            },
            exc_info=True
        )
        
        return JSONResponse(
            status_code=503,
            content={
                "error": "Service temporarily unavailable",
                "status_code": 503,
                "timestamp": time.time(),
                "path": str(request.url),
                "request_id": request_id,
                "error_type": "service_unavailable",
                "processing_time": processing_time
            }
        )
    
    async def _handle_permission_error(
        self, request: Request, exc: Exception, start_time: float, request_id: str
    ) -> JSONResponse:
        """Handle permission and system errors."""
        processing_time = time.time() - start_time
        
        logger.error(
            f"Permission error: {str(exc)}",
            extra={
                "request_id": request_id,
                "path": str(request.url),
                "method": request.method,
                "processing_time": processing_time,
                "error_type": type(exc).__name__
            },
            exc_info=True
        )
        
        return JSONResponse(
            status_code=403,
            content={
                "error": "Access denied",
                "status_code": 403,
                "timestamp": time.time(),
                "path": str(request.url),
                "request_id": request_id,
                "error_type": "permission_error",
                "processing_time": processing_time
            }
        )
    
    async def _handle_generic_exception(
        self, request: Request, exc: Exception, start_time: float, request_id: str
    ) -> JSONResponse:
        """Handle generic exceptions with comprehensive logging."""
        processing_time = time.time() - start_time
        
        # Log the full exception with context
        logger.error(
            f"Unhandled exception in {request.url}: {str(exc)}",
            extra={
                "request_id": request_id,
                "path": str(request.url),
                "method": request.method,
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown"),
                "processing_time": processing_time,
                "error_type": type(exc).__name__,
                "traceback": traceback.format_exc()
            },
            exc_info=True
        )
        
        # Update error statistics
        error_type = type(exc).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "status_code": 500,
                "timestamp": time.time(),
                "path": str(request.url),
                "request_id": request_id,
                "error_type": "internal_server_error",
                "processing_time": processing_time
            }
        )


def create_error_handling_middleware() -> ErrorHandlingMiddleware:
    """Create and return error handling middleware instance."""
    return ErrorHandlingMiddleware()


# Utility functions for service error handling
def handle_service_error(
    service_name: str,
    operation: str,
    error: Exception,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Handle service errors and convert them to appropriate HTTP exceptions.
    
    Args:
        service_name: Name of the service that encountered the error
        operation: Operation that failed
        error: The exception that occurred
        request_id: Optional request ID for tracking
    
    Returns:
        Dictionary with error information for logging
    """
    error_info = {
        "service": service_name,
        "operation": operation,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "request_id": request_id,
        "timestamp": time.time()
    }
    
    # Log the error
    logger.error(f"Service error in {service_name}.{operation}: {str(error)}", extra=error_info)
    
    # Convert to appropriate HTTP exception
    if isinstance(error, (ConnectionError, TimeoutError)):
        raise ExternalServiceError(
            service=service_name,
            operation=operation,
            error=str(error),
            retryable=True
        )
    elif isinstance(error, (ValueError, TypeError)):
        raise UKPValidationError(
            field="input",
            message=f"Invalid input for {operation}",
            value=str(error)
        )
    elif isinstance(error, PermissionError):
        raise AuthorizationError(f"Permission denied for {operation}")
    elif isinstance(error, FileNotFoundError):
        raise ResourceNotFoundError("file", str(error))
    else:
        # Generic service error
        raise QueryProcessingError(
            query_id=request_id or "unknown",
            internal_error=f"{service_name}.{operation} failed: {str(error)}",
            recoverable=True
        )
    
    return error_info


def validate_service_response(
    response: Any,
    service_name: str,
    operation: str,
    expected_type: type = dict
) -> None:
    """
    Validate service response and raise appropriate errors if invalid.
    
    Args:
        response: The response to validate
        service_name: Name of the service
        operation: Operation that produced the response
        expected_type: Expected type of the response
    
    Raises:
        ExternalServiceError: If response is invalid
    """
    if response is None:
        raise ExternalServiceError(
            service=service_name,
            operation=operation,
            error="Service returned None response",
            retryable=True
        )
    
    if not isinstance(response, expected_type):
        raise ExternalServiceError(
            service=service_name,
            operation=operation,
            error=f"Expected {expected_type.__name__}, got {type(response).__name__}",
            retryable=False
        )


def log_service_operation(
    service_name: str,
    operation: str,
    success: bool,
    duration: float,
    request_id: Optional[str] = None,
    additional_info: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log service operation with performance metrics.
    
    Args:
        service_name: Name of the service
        operation: Operation performed
        success: Whether the operation was successful
        duration: Duration of the operation in seconds
        request_id: Optional request ID for tracking
        additional_info: Additional information to log
    """
    log_data = {
        "service": service_name,
        "operation": operation,
        "success": success,
        "duration": duration,
        "request_id": request_id,
        "timestamp": time.time()
    }
    
    if additional_info:
        log_data.update(additional_info)
    
    if success:
        if duration > 1.0:  # Log slow operations
            logger.warning(f"Slow {service_name}.{operation}: {duration:.2f}s", extra=log_data)
        else:
            logger.info(f"{service_name}.{operation} completed in {duration:.3f}s", extra=log_data)
    else:
        logger.error(f"{service_name}.{operation} failed after {duration:.3f}s", extra=log_data) 