"""
Enhanced Error Handling for SarvanOM

This module provides comprehensive error handling, logging, and monitoring
capabilities following MAANG/OpenAI/Perplexity standards.
"""

import asyncio
import functools
import logging
import time
import traceback
from typing import Any, Callable, Dict, Optional, Type, Union
from datetime import datetime, timezone
from enum import Enum
import structlog
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse

logger = structlog.get_logger(__name__)

class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(str, Enum):
    """Error categories for better classification."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    DATABASE = "database"
    NETWORK = "network"
    EXTERNAL_API = "external_api"
    INTERNAL = "internal"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"

class SarvanOMError(Exception):
    """Base exception class for SarvanOM with enhanced metadata."""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.INTERNAL,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        retryable: bool = False,
        user_message: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.error_code = error_code or f"{category.value}_{severity.value}"
        self.details = details or {}
        self.retryable = retryable
        self.user_message = user_message or message
        self.timestamp = datetime.now(timezone.utc)
        self.traceback = traceback.format_exc()

class AuthenticationError(SarvanOMError):
    """Authentication related errors."""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )

class ValidationError(SarvanOMError):
    """Input validation errors."""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )

class DatabaseError(SarvanOMError):
    """Database related errors."""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            retryable=True,
            **kwargs
        )

class ExternalAPIError(SarvanOMError):
    """External API related errors."""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.EXTERNAL_API,
            severity=ErrorSeverity.MEDIUM,
            retryable=True,
            **kwargs
        )

class TimeoutError(SarvanOMError):
    """Timeout related errors."""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.TIMEOUT,
            severity=ErrorSeverity.MEDIUM,
            retryable=True,
            **kwargs
        )

class RateLimitError(SarvanOMError):
    """Rate limiting errors."""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.RATE_LIMIT,
            severity=ErrorSeverity.MEDIUM,
            retryable=True,
            **kwargs
        )

class ErrorHandler:
    """Enhanced error handler with monitoring and alerting capabilities."""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.error_history: list = []
        self.alert_thresholds = {
            ErrorSeverity.CRITICAL: 1,
            ErrorSeverity.HIGH: 5,
            ErrorSeverity.MEDIUM: 20,
            ErrorSeverity.LOW: 100
        }
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ) -> Dict[str, Any]:
        """
        Handle an error with comprehensive logging and monitoring.
        
        Args:
            error: The exception that occurred
            context: Additional context information
            request: The FastAPI request object
            
        Returns:
            Dict containing error information for response
        """
        # Determine error type and severity
        if isinstance(error, SarvanOMError):
            error_info = self._handle_sarvanom_error(error, context, request)
        else:
            error_info = self._handle_generic_error(error, context, request)
        
        # Log the error
        self._log_error(error_info)
        
        # Update monitoring
        self._update_error_counts(error_info)
        
        # Check for alerts
        self._check_alerts(error_info)
        
        return error_info
    
    def _handle_sarvanom_error(
        self,
        error: SarvanOMError,
        context: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ) -> Dict[str, Any]:
        """Handle SarvanOM specific errors."""
        error_info = {
            "error_type": "SarvanOMError",
            "error_code": error.error_code,
            "message": error.message,
            "user_message": error.user_message,
            "category": error.category.value,
            "severity": error.severity.value,
            "retryable": error.retryable,
            "timestamp": error.timestamp.isoformat(),
            "details": error.details,
            "context": context or {},
            "request_info": self._extract_request_info(request) if request else None
        }
        
        return error_info
    
    def _handle_generic_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ) -> Dict[str, Any]:
        """Handle generic exceptions."""
        error_info = {
            "error_type": type(error).__name__,
            "error_code": f"generic_{type(error).__name__.lower()}",
            "message": str(error),
            "user_message": "An internal error occurred. Please try again later.",
            "category": ErrorCategory.INTERNAL.value,
            "severity": ErrorSeverity.HIGH.value,
            "retryable": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {"exception_type": type(error).__name__},
            "context": context or {},
            "request_info": self._extract_request_info(request) if request else None,
            "traceback": traceback.format_exc()
        }
        
        return error_info
    
    def _extract_request_info(self, request: Request) -> Dict[str, Any]:
        """Extract relevant information from the request."""
        return {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "request_id": getattr(request.state, "request_id", None)
        }
    
    def _log_error(self, error_info: Dict[str, Any]):
        """Log the error with appropriate level."""
        log_data = {
            "error_code": error_info["error_code"],
            "message": error_info["message"],
            "category": error_info["category"],
            "severity": error_info["severity"],
            "retryable": error_info["retryable"],
            "context": error_info.get("context", {}),
            "request_info": error_info.get("request_info")
        }
        
        if error_info["severity"] == ErrorSeverity.CRITICAL.value:
            logger.critical("Critical error occurred", **log_data)
        elif error_info["severity"] == ErrorSeverity.HIGH.value:
            logger.error("High severity error occurred", **log_data)
        elif error_info["severity"] == ErrorSeverity.MEDIUM.value:
            logger.warning("Medium severity error occurred", **log_data)
        else:
            logger.info("Low severity error occurred", **log_data)
    
    def _update_error_counts(self, error_info: Dict[str, Any]):
        """Update error counts for monitoring."""
        error_code = error_info["error_code"]
        self.error_counts[error_code] = self.error_counts.get(error_code, 0) + 1
        
        # Add to history (keep last 1000 errors)
        self.error_history.append(error_info)
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-1000:]
    
    def _check_alerts(self, error_info: Dict[str, Any]):
        """Check if error thresholds are exceeded and trigger alerts."""
        severity = ErrorSeverity(error_info["severity"])
        threshold = self.alert_thresholds.get(severity, float('inf'))
        
        if self.error_counts.get(error_info["error_code"], 0) >= threshold:
            logger.critical(
                "Error threshold exceeded",
                error_code=error_info["error_code"],
                count=self.error_counts[error_info["error_code"]],
                threshold=threshold,
                severity=severity.value
            )
    
    def get_error_metrics(self) -> Dict[str, Any]:
        """Get error metrics for monitoring."""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_counts": self.error_counts,
            "recent_errors": self.error_history[-100:] if self.error_history else [],
            "error_categories": self._get_error_categories(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _get_error_categories(self) -> Dict[str, int]:
        """Get error counts by category."""
        categories = {}
        for error in self.error_history:
            category = error.get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1
        return categories

# Global error handler instance
_error_handler = ErrorHandler()

def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    return _error_handler

def error_handler(
    default_message: str = "An error occurred",
    default_status_code: int = 500,
    log_error: bool = True,
    include_traceback: bool = False
):
    """
    Decorator for handling errors in async functions.
    
    Args:
        default_message: Default error message
        default_status_code: Default HTTP status code
        log_error: Whether to log the error
        include_traceback: Whether to include traceback in response
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_info = _error_handler.handle_error(e)
                
                if log_error:
                    logger.error(
                        f"Error in {func.__name__}",
                        error=error_info,
                        function=func.__name__
                    )
                
                response_data = {
                    "error": error_info["user_message"],
                    "error_code": error_info["error_code"],
                    "timestamp": error_info["timestamp"]
                }
                
                if include_traceback and error_info.get("traceback"):
                    response_data["traceback"] = error_info["traceback"]
                
                return JSONResponse(
                    content=response_data,
                    status_code=default_status_code
                )
        
        return wrapper
    return decorator

def retry_on_error(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    retryable_errors: Optional[list] = None
):
    """
    Decorator for retrying functions on retryable errors.
    
    Args:
        max_retries: Maximum number of retries
        delay: Initial delay between retries
        backoff_factor: Factor to multiply delay by after each retry
        retryable_errors: List of error types to retry on
    """
    if retryable_errors is None:
        retryable_errors = [DatabaseError, ExternalAPIError, TimeoutError, RateLimitError]
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if error is retryable
                    is_retryable = (
                        isinstance(e, SarvanOMError) and e.retryable
                    ) or any(isinstance(e, error_type) for error_type in retryable_errors)
                    
                    if not is_retryable or attempt == max_retries:
                        break
                    
                    logger.warning(
                        f"Retrying {func.__name__} after error",
                        attempt=attempt + 1,
                        max_retries=max_retries,
                        delay=current_delay,
                        error=str(e)
                    )
                    
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff_factor
            
            # If we get here, all retries failed
            raise last_exception
        
        return wrapper
    return decorator

def validate_input(
    required_fields: Optional[list] = None,
    field_validators: Optional[Dict[str, Callable]] = None,
    max_length: Optional[int] = None
):
    """
    Decorator for input validation.
    
    Args:
        required_fields: List of required field names
        field_validators: Dict mapping field names to validation functions
        max_length: Maximum length for string inputs
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request data from kwargs
            request_data = kwargs.get('request', {})
            if isinstance(request_data, dict):
                data = request_data
            else:
                data = kwargs
            
            # Validate required fields
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    raise ValidationError(
                        f"Missing required fields: {', '.join(missing_fields)}",
                        details={"missing_fields": missing_fields}
                    )
            
            # Validate field values
            if field_validators:
                for field, validator in field_validators.items():
                    if field in data:
                        try:
                            validator(data[field])
                        except Exception as e:
                            raise ValidationError(
                                f"Validation failed for field '{field}': {str(e)}",
                                details={"field": field, "value": data[field]}
                            )
            
            # Validate string length
            if max_length:
                for key, value in data.items():
                    if isinstance(value, str) and len(value) > max_length:
                        raise ValidationError(
                            f"Field '{key}' exceeds maximum length of {max_length}",
                            details={"field": key, "length": len(value), "max_length": max_length}
                        )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# FastAPI exception handlers
async def sarvanom_exception_handler(request: Request, exc: SarvanOMError) -> JSONResponse:
    """Handle SarvanOM specific exceptions."""
    error_info = _error_handler.handle_error(exc, request=request)
    
    status_code = 500
    if exc.category == ErrorCategory.AUTHENTICATION:
        status_code = 401
    elif exc.category == ErrorCategory.AUTHORIZATION:
        status_code = 403
    elif exc.category == ErrorCategory.VALIDATION:
        status_code = 400
    elif exc.category == ErrorCategory.RATE_LIMIT:
        status_code = 429
    
    return JSONResponse(
        content={
            "error": exc.user_message,
            "error_code": exc.error_code,
            "category": exc.category.value,
            "retryable": exc.retryable,
            "timestamp": exc.timestamp.isoformat()
        },
        status_code=status_code
    )

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle generic exceptions."""
    error_info = _error_handler.handle_error(exc, request=request)
    
    return JSONResponse(
        content={
            "error": "An internal error occurred",
            "error_code": "internal_error",
            "timestamp": error_info["timestamp"]
        },
        status_code=500
    )

# Export main components
__all__ = [
    "SarvanOMError",
    "AuthenticationError",
    "ValidationError", 
    "DatabaseError",
    "ExternalAPIError",
    "TimeoutError",
    "RateLimitError",
    "ErrorHandler",
    "get_error_handler",
    "error_handler",
    "retry_on_error",
    "validate_input",
    "sarvanom_exception_handler",
    "generic_exception_handler"
]
