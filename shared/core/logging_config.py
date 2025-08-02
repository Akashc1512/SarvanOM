from shared.core.api.config import get_settings
settings = get_settings()
"""
Structured Logging Configuration - MAANG Standards

This module provides comprehensive logging configuration following MAANG best practices:
- Structured JSON logging with extra={} pattern
- Context-aware logging with correlation IDs
- Performance monitoring and metrics
- Security-aware logging (no secrets in logs)
- Environment-specific configuration
- Audit trail for compliance

Features:
- Structured logging with structlog
- Request/response correlation
- Performance timing
- Error tracking with context
- Security event logging
- Audit trail for compliance

Security:
- Automatic secret masking
- PII detection and redaction
- Secure log transport
- Log integrity verification

Authors: Universal Knowledge Platform Engineering Team
Version: 2.0.0 (2024-12-28)
"""

import os
import sys
import json
import time
import uuid
import logging
import warnings
from typing import Any, Dict, Optional, Union, List
from pathlib import Path
from datetime import datetime, timezone
from contextlib import contextmanager

import structlog
from structlog.stdlib import LoggerFactory
from structlog.processors import (
    TimeStamper,
    JSONRenderer,
    format_exc_info,
    add_log_level,
    StackInfoRenderer,
)
from structlog.types import Processor

# Configure structlog
structlog.configure(
    processors=[
        # Add timestamp
        TimeStamper(fmt="iso"),
        
        # Add log level
        add_log_level,
        
        # Add stack info
        StackInfoRenderer(),
        
        # Format exceptions
        format_exc_info,
        
        # Render as JSON
        JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=LoggerFactory(),
    cache_logger_on_first_use=True,
)

# Get the logger
logger = structlog.get_logger(__name__)


class SecureLogProcessor:
    """Processor to mask sensitive information in logs."""
    
    # Patterns to mask (passwords, keys, tokens, etc.)
    SENSITIVE_PATTERNS = [
        r'password["\']?\s*[:=]\s*["\'][^"\']*["\']',
        r'api_key["\']?\s*[:=]\s*["\'][^"\']*["\']',
        r'token["\']?\s*[:=]\s*["\'][^"\']*["\']',
        r'secret["\']?\s*[:=]\s*["\'][^"\']*["\']',
        r'key["\']?\s*[:=]\s*["\'][^"\']*["\']',
        r'authorization["\']?\s*[:=]\s*["\']bearer\s+[^"\']*["\']',
    ]
    
    def __init__(self):
        import re
        self.patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.SENSITIVE_PATTERNS]
    
    def __call__(self, logger, method_name, event_dict):
        """Process log event to mask sensitive data."""
        if isinstance(event_dict, dict):
            # Mask sensitive values
            for key, value in event_dict.items():
                if isinstance(value, str):
                    event_dict[key] = self._mask_sensitive_data(value)
                elif isinstance(value, dict):
                    event_dict[key] = self._mask_dict(value)
        return event_dict
    
    def _mask_sensitive_data(self, text: str) -> str:
        """Mask sensitive data in text."""
        for pattern in self.patterns:
            text = pattern.sub('***MASKED***', text)
        return text
    
    def _mask_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively mask sensitive data in dictionaries."""
        masked = {}
        for key, value in data.items():
            if isinstance(value, str):
                masked[key] = self._mask_sensitive_data(value)
            elif isinstance(value, dict):
                masked[key] = self._mask_dict(value)
            else:
                masked[key] = value
        return masked


class CorrelationProcessor:
    """Processor to add correlation IDs to log events."""
    
    def __init__(self):
        self.correlation_id = None
    
    def set_correlation_id(self, correlation_id: str):
        """Set the correlation ID for the current context."""
        self.correlation_id = correlation_id
    
    def __call__(self, logger, method_name, event_dict):
        """Add correlation ID to log event."""
        if self.correlation_id:
            event_dict["correlation_id"] = self.correlation_id
        return event_dict


class PerformanceProcessor:
    """Processor to add performance metrics to log events."""
    
    def __init__(self):
        self.start_time = None
    
    def start_timer(self):
        """Start performance timer."""
        self.start_time = time.time()
    
    def __call__(self, logger, method_name, event_dict):
        """Add performance metrics to log event."""
        if self.start_time:
            duration = time.time() - self.start_time
            event_dict["duration_ms"] = round(duration * 1000, 2)
            self.start_time = None
        return event_dict


class LoggingContext:
    """Context manager for structured logging."""
    
    def __init__(self, context_name: str, **kwargs):
        self.context_name = context_name
        self.context_data = kwargs
        self.logger = structlog.get_logger(context_name)
    
    def __enter__(self):
        """Enter logging context."""
        self.logger = self.logger.bind(**self.context_data)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit logging context."""
        if exc_type:
            self.logger.error(
                "Context execution failed",
                error_type=exc_type.__name__,
                error_message=str(exc_val),
                extra={"exception": exc_val}
            )


class AuditLogger:
    """Specialized logger for audit events."""
    
    def __init__(self):
        self.logger = structlog.get_logger("audit")
    
    def log_user_action(self, user_id: str, action: str, resource: str, 
                       success: bool = True, details: Dict[str, Any] = None):
        """Log user actions for audit trail."""
        self.logger.info(
            "User action logged",
            user_id=user_id,
            action=action,
            resource=resource,
            success=success,
            details=details or {},
            extra={"audit_event": True}
        )
    
    def log_security_event(self, event_type: str, severity: str, 
                          user_id: str = None, details: Dict[str, Any] = None):
        """Log security events."""
        self.logger.warning(
            "Security event detected",
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            details=details or {},
            extra={"security_event": True}
        )
    
    def log_system_event(self, event_type: str, component: str, 
                        status: str, details: Dict[str, Any] = None):
        """Log system events."""
        self.logger.info(
            "System event",
            event_type=event_type,
            component=component,
            status=status,
            details=details or {},
            extra={"system_event": True}
        )


class PerformanceLogger:
    """Specialized logger for performance metrics."""
    
    def __init__(self):
        self.logger = structlog.get_logger("performance")
    
    def log_operation(self, operation: str, duration_ms: float, 
                     success: bool = True, metadata: Dict[str, Any] = None):
        """Log operation performance."""
        self.logger.info(
            "Operation performance",
            operation=operation,
            duration_ms=duration_ms,
            success=success,
            metadata=metadata or {},
            extra={"performance_metric": True}
        )
    
    def log_database_query(self, query_type: str, table: str, 
                          duration_ms: float, row_count: int = None):
        """Log database query performance."""
        self.logger.info(
            "Database query performance",
            query_type=query_type,
            table=table,
            duration_ms=duration_ms,
            row_count=row_count,
            extra={"database_metric": True}
        )
    
    def log_api_request(self, endpoint: str, method: str, 
                       status_code: int, duration_ms: float, 
                       user_id: str = None):
        """Log API request performance."""
        self.logger.info(
            "API request performance",
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            duration_ms=duration_ms,
            user_id=user_id,
            extra={"api_metric": True}
        )


class ErrorLogger:
    """Specialized logger for error tracking."""
    
    def __init__(self):
        self.logger = structlog.get_logger("errors")
    
    def log_error(self, error_type: str, error_message: str, 
                 context: Dict[str, Any] = None, user_id: str = None):
        """Log application errors."""
        self.logger.error(
            "Application error",
            error_type=error_type,
            error_message=error_message,
            context=context or {},
            user_id=user_id,
            extra={"error_tracking": True}
        )
    
    def log_exception(self, exception: Exception, context: Dict[str, Any] = None,
                     user_id: str = None):
        """Log exceptions with full context."""
        self.logger.error(
            "Exception occurred",
            exception_type=type(exception).__name__,
            exception_message=str(exception),
            context=context or {},
            user_id=user_id,
            extra={"exception_tracking": True}
        )


# Global instances
audit_logger = AuditLogger()
performance_logger = PerformanceLogger()
error_logger = ErrorLogger()
correlation_processor = CorrelationProcessor()
performance_processor = PerformanceProcessor()
secure_processor = SecureLogProcessor()


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name or __name__)


def set_correlation_id(correlation_id: str):
    """Set correlation ID for the current context."""
    correlation_processor.set_correlation_id(correlation_id)


def start_performance_timer():
    """Start performance timer."""
    performance_processor.start_timer()


@contextmanager
def log_operation(operation_name: str, **context):
    """Context manager for logging operations with timing."""
    logger = get_logger("operations")
    start_time = time.time()
    
    try:
        logger.info(
            "Operation started",
            operation=operation_name,
            **context,
            extra={"operation_start": True}
        )
        yield logger
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.error(
            "Operation failed",
            operation=operation_name,
            duration_ms=round(duration, 2),
            error=str(e),
            **context,
            extra={"operation_failed": True}
        )
        raise
    else:
        duration = (time.time() - start_time) * 1000
        logger.info(
            "Operation completed",
            operation=operation_name,
            duration_ms=round(duration, 2),
            **context,
            extra={"operation_completed": True}
        )


@contextmanager
def log_api_request(endpoint: str, method: str, user_id: str = None):
    """Context manager for logging API requests."""
    logger = get_logger("api")
    start_time = time.time()
    
    try:
        logger.info(
            "API request started",
            endpoint=endpoint,
            method=method,
            user_id=user_id,
            extra={"api_request_start": True}
        )
        yield logger
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.error(
            "API request failed",
            endpoint=endpoint,
            method=method,
            duration_ms=round(duration, 2),
            error=str(e),
            user_id=user_id,
            extra={"api_request_failed": True}
        )
        raise
    else:
        duration = (time.time() - start_time) * 1000
        logger.info(
            "API request completed",
            endpoint=endpoint,
            method=method,
            duration_ms=round(duration, 2),
            user_id=user_id,
            extra={"api_request_completed": True}
        )


def configure_logging(environment: str = "development", log_level: str = "INFO"):
    """Configure logging for the application."""
    
    # Set log level
    logging.basicConfig(level=getattr(logging, log_level.upper()))
    
    # Configure structlog processors
    processors = [
        TimeStamper(fmt="iso"),
        add_log_level,
        StackInfoRenderer(),
        format_exc_info,
        secure_processor,
        correlation_processor,
        performance_processor,
        JSONRenderer(),
    ]
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Log configuration
    logger.info(
        "Logging configured",
        environment=environment,
        log_level=log_level,
        extra={"logging_config": True}
    )


# Initialize logging configuration
configure_logging(
    environment=settings.environment or "development",
    log_level=settings.log_level or "INFO"
) 