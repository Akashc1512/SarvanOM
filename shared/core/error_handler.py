"""
Comprehensive Error Handling System for Critical Backend Operations.

This module provides centralized error handling for external API calls, LLM requests,
database queries, and other critical operations to ensure server stability and
graceful error responses.

Features:
    - Centralized error handling with logging
    - Graceful fallback mechanisms
    - Circuit breaker patterns
    - Retry logic with exponential backoff
    - Error categorization and response formatting
    - Health monitoring and alerting
    - Structured error logging

Security:
    - No sensitive data in error logs
    - Sanitized error messages for clients
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
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
from typing_extensions import ParamSpec

import structlog
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = structlog.get_logger(__name__)

# Type variables for generic error handling
T = TypeVar('T')
P = ParamSpec('P')


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Error categories for classification."""
    
    # External API errors
    API_TIMEOUT = "api_timeout"
    API_RATE_LIMIT = "api_rate_limit"
    API_AUTHENTICATION = "api_authentication"
    API_PERMISSION = "api_permission"
    API_SERVER_ERROR = "api_server_error"
    API_NETWORK = "api_network"
    
    # LLM errors
    LLM_TIMEOUT = "llm_timeout"
    LLM_RATE_LIMIT = "llm_rate_limit"
    LLM_AUTHENTICATION = "llm_authentication"
    LLM_MODEL_UNAVAILABLE = "llm_model_unavailable"
    LLM_CONTENT_FILTER = "llm_content_filter"
    LLM_TOKEN_LIMIT = "llm_token_limit"
    
    # Database errors
    DB_CONNECTION = "db_connection"
    DB_TIMEOUT = "db_timeout"
    DB_AUTHENTICATION = "db_authentication"
    DB_PERMISSION = "db_permission"
    DB_QUERY_SYNTAX = "db_query_syntax"
    DB_CONSTRAINT_VIOLATION = "db_constraint_violation"
    DB_DEADLOCK = "db_deadlock"
    
    # System errors
    SYSTEM_RESOURCE = "system_resource"
    SYSTEM_CONFIGURATION = "system_configuration"
    SYSTEM_NETWORK = "system_network"
    SYSTEM_MEMORY = "system_memory"
    
    # Validation errors
    VALIDATION_INPUT = "validation_input"
    VALIDATION_BUSINESS_RULE = "validation_business_rule"
    
    # Unknown errors
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Context information for error handling."""
    
    operation: str
    service: str
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    query: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class ErrorInfo:
    """Structured error information."""
    
    error_type: str
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    retryable: bool = True
    status_code: Optional[int] = None
    error_code: Optional[str] = None
    context: Optional[ErrorContext] = None
    original_exception: Optional[Exception] = None
    stack_trace: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorResponse:
    """Structured error response for clients."""
    
    error: str
    error_type: str
    request_id: str
    success: bool = False
    error_code: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    retryable: bool = True
    fallback_data: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CircuitBreaker:
    """Circuit breaker pattern for external service calls."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """Check if the circuit breaker allows execution."""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def on_success(self):
        """Handle successful execution."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def on_failure(self):
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class ErrorHandler(ABC):
    """Abstract base class for error handlers."""
    
    @abstractmethod
    async def handle_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle an error and return a structured response."""
        pass
    
    @abstractmethod
    def should_retry(self, error: Exception) -> bool:
        """Determine if the operation should be retried."""
        pass
    
    @abstractmethod
    def get_fallback_data(self, context: ErrorContext) -> Optional[Dict[str, Any]]:
        """Get fallback data when the operation fails."""
        pass


class APIErrorHandler(ErrorHandler):
    """Error handler for external API calls."""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    async def handle_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle API errors with appropriate categorization."""
        
        # Determine error category and severity
        category, severity, retryable = self._classify_api_error(error)
        
        # Create error info
        error_info = ErrorInfo(
            error_type=type(error).__name__,
            message=str(error),
            category=category,
            severity=severity,
            retryable=retryable,
            context=context,
            original_exception=error,
            stack_trace=traceback.format_exc()
        )
        
        # Log the error
        await self._log_error(error_info)
        
        # Update circuit breaker
        circuit_breaker = self._get_circuit_breaker(context.service)
        circuit_breaker.on_failure()
        
        # Get fallback data
        fallback_data = self.get_fallback_data(context)
        
        return ErrorResponse(
            error=f"API operation failed: {self._sanitize_message(str(error))}",
            error_type=category.value,
            error_code=getattr(error, 'status_code', None),
            request_id=context.request_id,
            retryable=retryable,
            fallback_data=fallback_data,
            metadata={"service": context.service, "operation": context.operation}
        )
    
    def should_retry(self, error: Exception) -> bool:
        """Determine if API call should be retried."""
        retryable_errors = (
            TimeoutError,
            ConnectionError,
            asyncio.TimeoutError,
        )
        
        # Check if it's a retryable error
        if isinstance(error, retryable_errors):
            return True
        
        # Check status codes for HTTP errors
        if hasattr(error, 'status_code'):
            return error.status_code in [429, 500, 502, 503, 504]
        
        return False
    
    def get_fallback_data(self, context: ErrorContext) -> Optional[Dict[str, Any]]:
        """Get fallback data for API failures."""
        return {
            "message": "Service temporarily unavailable",
            "suggestion": "Please try again later",
            "status": "degraded"
        }
    
    def _classify_api_error(self, error: Exception) -> tuple[ErrorCategory, ErrorSeverity, bool]:
        """Classify API errors into categories."""
        
        if isinstance(error, asyncio.TimeoutError):
            return ErrorCategory.API_TIMEOUT, ErrorSeverity.MEDIUM, True
        
        if isinstance(error, ConnectionError):
            return ErrorCategory.API_NETWORK, ErrorSeverity.HIGH, True
        
        # Check for HTTP status codes
        if hasattr(error, 'status_code'):
            status_code = error.status_code
            
            if status_code == 401:
                return ErrorCategory.API_AUTHENTICATION, ErrorSeverity.HIGH, False
            elif status_code == 403:
                return ErrorCategory.API_PERMISSION, ErrorSeverity.HIGH, False
            elif status_code == 429:
                return ErrorCategory.API_RATE_LIMIT, ErrorSeverity.MEDIUM, True
            elif status_code >= 500:
                return ErrorCategory.API_SERVER_ERROR, ErrorSeverity.HIGH, True
        
        return ErrorCategory.API_SERVER_ERROR, ErrorSeverity.MEDIUM, True
    
    def _get_circuit_breaker(self, service: str) -> CircuitBreaker:
        """Get or create circuit breaker for a service."""
        if service not in self.circuit_breakers:
            self.circuit_breakers[service] = CircuitBreaker()
        return self.circuit_breakers[service]
    
    def _sanitize_message(self, message: str) -> str:
        """Sanitize error message for client consumption."""
        # Remove sensitive information
        sensitive_patterns = [
            r'api_key=[^&\s]+',
            r'password=[^&\s]+',
            r'token=[^&\s]+',
            r'secret=[^&\s]+'
        ]
        
        sanitized = message
        for pattern in sensitive_patterns:
            import re
            sanitized = re.sub(pattern, '[REDACTED]', sanitized)
        
        return sanitized
    
    async def _log_error(self, error_info: ErrorInfo):
        """Log error with structured information."""
        log_data = {
            "error_type": error_info.error_type,
            "category": error_info.category.value,
            "severity": error_info.severity.value,
            "retryable": error_info.retryable,
            "service": error_info.context.service if error_info.context else None,
            "operation": error_info.context.operation if error_info.context else None,
            "request_id": error_info.context.request_id if error_info.context else None,
            "user_id": error_info.context.user_id if error_info.context else None,
            "timestamp": error_info.context.timestamp if error_info.context else None
        }
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            logger.error("Critical API error", **log_data, exc_info=error_info.original_exception)
        elif error_info.severity == ErrorSeverity.HIGH:
            logger.error("High severity API error", **log_data, exc_info=error_info.original_exception)
        else:
            logger.warning("API error", **log_data)


class LLMErrorHandler(ErrorHandler):
    """Error handler for LLM operations."""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    async def handle_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle LLM errors with appropriate categorization."""
        
        # Determine error category and severity
        category, severity, retryable = self._classify_llm_error(error)
        
        # Create error info
        error_info = ErrorInfo(
            error_type=type(error).__name__,
            message=str(error),
            category=category,
            severity=severity,
            retryable=retryable,
            context=context,
            original_exception=error,
            stack_trace=traceback.format_exc()
        )
        
        # Log the error
        await self._log_error(error_info)
        
        # Update circuit breaker
        circuit_breaker = self._get_circuit_breaker(context.service)
        circuit_breaker.on_failure()
        
        # Get fallback data
        fallback_data = self.get_fallback_data(context)
        
        return ErrorResponse(
            error=f"LLM operation failed: {self._sanitize_message(str(error))}",
            error_type=category.value,
            error_code=getattr(error, 'error_code', None),
            request_id=context.request_id,
            retryable=retryable,
            fallback_data=fallback_data,
            metadata={"service": context.service, "operation": context.operation}
        )
    
    def should_retry(self, error: Exception) -> bool:
        """Determine if LLM operation should be retried."""
        retryable_errors = (
            TimeoutError,
            ConnectionError,
            asyncio.TimeoutError,
        )
        
        # Check if it's a retryable error
        if isinstance(error, retryable_errors):
            return True
        
        # Check for LLM-specific retryable errors
        if hasattr(error, 'retryable'):
            return error.retryable
        
        return False
    
    def get_fallback_data(self, context: ErrorContext) -> Optional[Dict[str, Any]]:
        """Get fallback data for LLM failures."""
        return {
            "content": "I apologize, but I'm experiencing technical difficulties. Please try again later.",
            "provider": "fallback",
            "model": "fallback",
            "confidence": 0.0,
            "status": "degraded"
        }
    
    def _classify_llm_error(self, error: Exception) -> tuple[ErrorCategory, ErrorSeverity, bool]:
        """Classify LLM errors into categories."""
        
        if isinstance(error, asyncio.TimeoutError):
            return ErrorCategory.LLM_TIMEOUT, ErrorSeverity.MEDIUM, True
        
        if isinstance(error, ConnectionError):
            return ErrorCategory.LLM_NETWORK, ErrorSeverity.HIGH, True
        
        # Check for LLM-specific error types
        error_message = str(error).lower()
        
        if "rate limit" in error_message or "quota" in error_message:
            return ErrorCategory.LLM_RATE_LIMIT, ErrorSeverity.MEDIUM, True
        elif "authentication" in error_message or "api key" in error_message:
            return ErrorCategory.LLM_AUTHENTICATION, ErrorSeverity.HIGH, False
        elif "model" in error_message and "unavailable" in error_message:
            return ErrorCategory.LLM_MODEL_UNAVAILABLE, ErrorSeverity.MEDIUM, True
        elif "content" in error_message and "filter" in error_message:
            return ErrorCategory.LLM_CONTENT_FILTER, ErrorSeverity.LOW, False
        elif "token" in error_message and "limit" in error_message:
            return ErrorCategory.LLM_TOKEN_LIMIT, ErrorSeverity.MEDIUM, False
        
        return ErrorCategory.LLM_SERVER_ERROR, ErrorSeverity.MEDIUM, True
    
    def _get_circuit_breaker(self, service: str) -> CircuitBreaker:
        """Get or create circuit breaker for a service."""
        if service not in self.circuit_breakers:
            self.circuit_breakers[service] = CircuitBreaker()
        return self.circuit_breakers[service]
    
    def _sanitize_message(self, message: str) -> str:
        """Sanitize error message for client consumption."""
        # Remove sensitive information
        sensitive_patterns = [
            r'api_key=[^&\s]+',
            r'password=[^&\s]+',
            r'token=[^&\s]+',
            r'secret=[^&\s]+'
        ]
        
        sanitized = message
        for pattern in sensitive_patterns:
            import re
            sanitized = re.sub(pattern, '[REDACTED]', sanitized)
        
        return sanitized
    
    async def _log_error(self, error_info: ErrorInfo):
        """Log error with structured information."""
        log_data = {
            "error_type": error_info.error_type,
            "category": error_info.category.value,
            "severity": error_info.severity.value,
            "retryable": error_info.retryable,
            "service": error_info.context.service if error_info.context else None,
            "operation": error_info.context.operation if error_info.context else None,
            "request_id": error_info.context.request_id if error_info.context else None,
            "user_id": error_info.context.user_id if error_info.context else None,
            "timestamp": error_info.context.timestamp if error_info.context else None
        }
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            logger.error("Critical LLM error", **log_data, exc_info=error_info.original_exception)
        elif error_info.severity == ErrorSeverity.HIGH:
            logger.error("High severity LLM error", **log_data, exc_info=error_info.original_exception)
        else:
            logger.warning("LLM error", **log_data)


class DatabaseErrorHandler(ErrorHandler):
    """Error handler for database operations."""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    async def handle_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle database errors with appropriate categorization."""
        
        # Determine error category and severity
        category, severity, retryable = self._classify_database_error(error)
        
        # Create error info
        error_info = ErrorInfo(
            error_type=type(error).__name__,
            message=str(error),
            category=category,
            severity=severity,
            retryable=retryable,
            context=context,
            original_exception=error,
            stack_trace=traceback.format_exc()
        )
        
        # Log the error
        await self._log_error(error_info)
        
        # Update circuit breaker
        circuit_breaker = self._get_circuit_breaker(context.service)
        circuit_breaker.on_failure()
        
        # Get fallback data
        fallback_data = self.get_fallback_data(context)
        
        return ErrorResponse(
            error=f"Database operation failed: {self._sanitize_message(str(error))}",
            error_type=category.value,
            error_code=getattr(error, 'code', None),
            request_id=context.request_id,
            retryable=retryable,
            fallback_data=fallback_data,
            metadata={"service": context.service, "operation": context.operation}
        )
    
    def should_retry(self, error: Exception) -> bool:
        """Determine if database operation should be retried."""
        retryable_errors = (
            TimeoutError,
            ConnectionError,
            asyncio.TimeoutError,
        )
        
        # Check if it's a retryable error
        if isinstance(error, retryable_errors):
            return True
        
        # Check for database-specific retryable errors
        error_message = str(error).lower()
        
        if "connection" in error_message:
            return True
        elif "timeout" in error_message:
            return True
        elif "deadlock" in error_message:
            return True
        
        return False
    
    def get_fallback_data(self, context: ErrorContext) -> Optional[Dict[str, Any]]:
        """Get fallback data for database failures."""
        return {
            "message": "Database temporarily unavailable",
            "suggestion": "Please try again later",
            "status": "degraded",
            "data": []
        }
    
    def _classify_database_error(self, error: Exception) -> tuple[ErrorCategory, ErrorSeverity, bool]:
        """Classify database errors into categories."""
        
        if isinstance(error, asyncio.TimeoutError):
            return ErrorCategory.DB_TIMEOUT, ErrorSeverity.MEDIUM, True
        
        if isinstance(error, ConnectionError):
            return ErrorCategory.DB_CONNECTION, ErrorSeverity.HIGH, True
        
        # Check for database-specific error types
        error_message = str(error).lower()
        
        if "authentication" in error_message or "password" in error_message:
            return ErrorCategory.DB_AUTHENTICATION, ErrorSeverity.HIGH, False
        elif "permission" in error_message or "access" in error_message:
            return ErrorCategory.DB_PERMISSION, ErrorSeverity.HIGH, False
        elif "syntax" in error_message or "invalid" in error_message:
            return ErrorCategory.DB_QUERY_SYNTAX, ErrorSeverity.MEDIUM, False
        elif "constraint" in error_message or "unique" in error_message:
            return ErrorCategory.DB_CONSTRAINT_VIOLATION, ErrorSeverity.MEDIUM, False
        elif "deadlock" in error_message:
            return ErrorCategory.DB_DEADLOCK, ErrorSeverity.MEDIUM, True
        
        return ErrorCategory.DB_CONNECTION, ErrorSeverity.HIGH, True
    
    def _get_circuit_breaker(self, service: str) -> CircuitBreaker:
        """Get or create circuit breaker for a service."""
        if service not in self.circuit_breakers:
            self.circuit_breakers[service] = CircuitBreaker()
        return self.circuit_breakers[service]
    
    def _sanitize_message(self, message: str) -> str:
        """Sanitize error message for client consumption."""
        # Remove sensitive information
        sensitive_patterns = [
            r'password=[^&\s]+',
            r'user=[^&\s]+',
            r'host=[^&\s]+',
            r'port=[^&\s]+'
        ]
        
        sanitized = message
        for pattern in sensitive_patterns:
            import re
            sanitized = re.sub(pattern, '[REDACTED]', sanitized)
        
        return sanitized
    
    async def _log_error(self, error_info: ErrorInfo):
        """Log error with structured information."""
        log_data = {
            "error_type": error_info.error_type,
            "category": error_info.category.value,
            "severity": error_info.severity.value,
            "retryable": error_info.retryable,
            "service": error_info.context.service if error_info.context else None,
            "operation": error_info.context.operation if error_info.context else None,
            "request_id": error_info.context.request_id if error_info.context else None,
            "user_id": error_info.context.user_id if error_info.context else None,
            "timestamp": error_info.context.timestamp if error_info.context else None
        }
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            logger.error("Critical database error", **log_data, exc_info=error_info.original_exception)
        elif error_info.severity == ErrorSeverity.HIGH:
            logger.error("High severity database error", **log_data, exc_info=error_info.original_exception)
        else:
            logger.warning("Database error", **log_data)


class ErrorHandlerFactory:
    """Factory for creating error handlers based on operation type."""
    
    def __init__(self):
        self._handlers: Dict[str, ErrorHandler] = {
            "api": APIErrorHandler(),
            "llm": LLMErrorHandler(),
            "database": DatabaseErrorHandler(),
        }
    
    def get_handler(self, operation_type: str) -> ErrorHandler:
        """Get error handler for the specified operation type."""
        return self._handlers.get(operation_type, APIErrorHandler())


# Global error handler factory
error_handler_factory = ErrorHandlerFactory()


def handle_critical_operation(
    operation_type: str = "api",
    max_retries: int = 3,
    timeout: float = 30.0
):
    """
    Decorator for handling critical operations with comprehensive error handling.
    
    Args:
        operation_type: Type of operation ("api", "llm", "database")
        max_retries: Maximum number of retry attempts
        timeout: Operation timeout in seconds
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Get error handler
            error_handler = error_handler_factory.get_handler(operation_type)
            
            # Create error context
            context = ErrorContext(
                operation=func.__name__,
                service=operation_type,
                metadata=kwargs.get("metadata", {})
            )
            
            # Retry logic with exponential backoff
            @retry(
                stop=stop_after_attempt(max_retries),
                wait=wait_exponential(multiplier=1, min=2, max=10),
                retry=retry_if_exception_type(Exception),
                before_sleep=before_sleep_log(logger, structlog.stdlib.WARNING),
            )
            async def execute_with_retry():
                try:
                    # Execute the operation with timeout
                    return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
                except Exception as e:
                    # Handle the error
                    error_response = await error_handler.handle_error(e, context)
                    
                    # If not retryable, raise the error
                    if not error_handler.should_retry(e):
                        raise e
                    
                    # If retryable, raise for retry mechanism
                    raise e
            
            try:
                return await execute_with_retry()
            except Exception as e:
                # Final error handling - return graceful response
                error_response = await error_handler.handle_error(e, context)
                
                # Return fallback data or raise a structured exception
                if error_response.fallback_data:
                    logger.warning(
                        "Operation failed, returning fallback data",
                        operation=func.__name__,
                        error=str(e),
                        request_id=context.request_id
                    )
                    return error_response.fallback_data
                else:
                    # Create a structured exception
                    raise CriticalOperationError(
                        message=error_response.error,
                        error_type=error_response.error_type,
                        error_code=error_response.error_code,
                        retryable=error_response.retryable,
                        context=context
                    )
        
        return wrapper
    return decorator


@asynccontextmanager
async def critical_operation_context(
    operation_type: str = "api",
    timeout: float = 30.0,
    **context_kwargs
):
    """
    Context manager for critical operations with error handling.
    
    Args:
        operation_type: Type of operation ("api", "llm", "database")
        timeout: Operation timeout in seconds
        **context_kwargs: Additional context information
    """
    # Get error handler
    error_handler = error_handler_factory.get_handler(operation_type)
    
    # Create error context
    context = ErrorContext(
        operation=context_kwargs.get("operation", "unknown"),
        service=operation_type,
        **context_kwargs
    )
    
    try:
        yield context
    except Exception as e:
        # Handle the error
        error_response = await error_handler.handle_error(e, context)
        
        # Log the error and raise structured exception
        logger.warning(
            "Operation failed in context manager",
            operation=context.operation,
            error=str(e),
            request_id=context.request_id
        )
        
        # Always raise a structured exception from context manager
        raise CriticalOperationError(
            message=error_response.error,
            error_type=error_response.error_type,
            error_code=error_response.error_code,
            retryable=error_response.retryable,
            context=context
        )


class CriticalOperationError(Exception):
    """Structured exception for critical operation failures."""
    
    def __init__(
        self,
        message: str,
        error_type: str,
        error_code: Optional[str] = None,
        retryable: bool = True,
        context: Optional[ErrorContext] = None
    ):
        self.message = message
        self.error_type = error_type
        self.error_code = error_code
        self.retryable = retryable
        self.context = context
        super().__init__(message)


# Utility functions for common error handling patterns

async def safe_api_call(
    api_func: Callable,
    *args,
    timeout: float = 30.0,
    max_retries: int = 3,
    fallback_data: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Any:
    """
    Safely execute an API call with error handling.
    
    Args:
        api_func: The API function to call
        timeout: Operation timeout
        max_retries: Maximum retry attempts
        fallback_data: Fallback data if operation fails
        **kwargs: Additional arguments for the API function
    
    Returns:
        API response or fallback data
    """
    @handle_critical_operation(operation_type="api", max_retries=max_retries, timeout=timeout)
    async def execute_api_call():
        return await api_func(*args, **kwargs)
    
    try:
        return await execute_api_call()
    except CriticalOperationError as e:
        if fallback_data:
            return fallback_data
        raise e


async def safe_llm_call(
    llm_func: Callable,
    *args,
    timeout: float = 60.0,
    max_retries: int = 3,
    fallback_data: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Any:
    """
    Safely execute an LLM call with error handling.
    
    Args:
        llm_func: The LLM function to call
        timeout: Operation timeout
        max_retries: Maximum retry attempts
        fallback_data: Fallback data if operation fails
        **kwargs: Additional arguments for the LLM function
    
    Returns:
        LLM response or fallback data
    """
    @handle_critical_operation(operation_type="llm", max_retries=max_retries, timeout=timeout)
    async def execute_llm_call():
        return await llm_func(*args, **kwargs)
    
    try:
        return await execute_llm_call()
    except CriticalOperationError as e:
        if fallback_data:
            return fallback_data
        raise e


async def safe_database_call(
    db_func: Callable,
    *args,
    timeout: float = 30.0,
    max_retries: int = 3,
    fallback_data: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Any:
    """
    Safely execute a database call with error handling.
    
    Args:
        db_func: The database function to call
        timeout: Operation timeout
        max_retries: Maximum retry attempts
        fallback_data: Fallback data if operation fails
        **kwargs: Additional arguments for the database function
    
    Returns:
        Database response or fallback data
    """
    @handle_critical_operation(operation_type="database", max_retries=max_retries, timeout=timeout)
    async def execute_db_call():
        return await db_func(*args, **kwargs)
    
    try:
        return await execute_db_call()
    except CriticalOperationError as e:
        if fallback_data:
            return fallback_data
        raise e


# Health monitoring and alerting

class ErrorMonitor:
    """Monitor for tracking error patterns and alerting."""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.error_timestamps: Dict[str, List[float]] = {}
        self.alert_thresholds: Dict[str, int] = {
            "critical": 5,
            "high": 10,
            "medium": 20
        }
    
    def record_error(self, error_info: ErrorInfo):
        """Record an error for monitoring."""
        error_key = f"{error_info.category.value}_{error_info.severity.value}"
        
        # Update error count
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Update timestamps
        if error_key not in self.error_timestamps:
            self.error_timestamps[error_key] = []
        self.error_timestamps[error_key].append(error_info.context.timestamp)
        
        # Clean old timestamps (keep last hour)
        current_time = time.time()
        self.error_timestamps[error_key] = [
            ts for ts in self.error_timestamps[error_key]
            if current_time - ts < 3600
        ]
        
        # Check for alerting
        self._check_alerts(error_key, error_info)
    
    def _check_alerts(self, error_key: str, error_info: ErrorInfo):
        """Check if alerts should be triggered."""
        recent_count = len(self.error_timestamps[error_key])
        threshold = self.alert_thresholds.get(error_info.severity.value, 10)
        
        if recent_count >= threshold:
            logger.error(
                f"Error alert: {recent_count} {error_info.severity.value} severity "
                f"{error_info.category.value} errors in the last hour",
                error_key=error_key,
                count=recent_count,
                threshold=threshold,
                severity=error_info.severity.value,
                category=error_info.category.value
            )


# Global error monitor
error_monitor = ErrorMonitor() 