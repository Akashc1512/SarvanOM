"""
Production logging configuration for the Universal Knowledge Platform.

This module provides structured logging configuration for production deployment
with proper rotation, retention, and formatting.
"""

import logging
import logging.handlers
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from config.production.settings import get_logging_config


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)


class TextFormatter(logging.Formatter):
    """Text formatter for human-readable logs."""
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


class StructuredLogger:
    """Structured logger with additional context support."""
    
    def __init__(self, name: str, logger: logging.Logger):
        self.name = name
        self.logger = logger
    
    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log with additional context."""
        extra_fields = {
            "service": self.name,
            "context": kwargs
        }
        
        # Create a new record with extra fields
        record = self.logger.makeRecord(
            self.name, level, "", 0, message, (), None
        )
        record.extra_fields = extra_fields
        
        self.logger.handle(record)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message with context."""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with context."""
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with context."""
        self._log_with_context(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with context."""
        self._log_with_context(logging.ERROR, message, **kwargs)


def setup_logging(
    name: str = "universal_knowledge_platform",
    level: str = "INFO",
    format_type: str = "json",
    log_file: Optional[str] = None,
    max_size: int = 100,
    backup_count: int = 5
) -> StructuredLogger:
    """Setup logging configuration."""
    
    # Get logging configuration
    config = get_logging_config()
    level = config.get("level", level)
    format_type = config.get("format", format_type)
    log_file = config.get("file", log_file)
    max_size = config.get("max_size", max_size) * 1024 * 1024  # Convert to bytes
    backup_count = config.get("backup_count", backup_count)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    if format_type.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Create structured logger
    return StructuredLogger(name, logger)


def get_logger(name: str = "universal_knowledge_platform") -> StructuredLogger:
    """Get structured logger instance."""
    return setup_logging(name)


def log_request(request_id: str, method: str, path: str, status_code: int, duration: float):
    """Log HTTP request details."""
    logger = get_logger("api")
    logger.info(
        "HTTP Request",
        request_id=request_id,
        method=method,
        path=path,
        status_code=status_code,
        duration=duration
    )


def log_service_call(service_name: str, method: str, duration: float, success: bool, error: Optional[str] = None):
    """Log service call details."""
    logger = get_logger("services")
    logger.info(
        "Service Call",
        service=service_name,
        method=method,
        duration=duration,
        success=success,
        error=error
    )


def log_database_query(query: str, duration: float, success: bool, error: Optional[str] = None):
    """Log database query details."""
    logger = get_logger("database")
    logger.info(
        "Database Query",
        query=query,
        duration=duration,
        success=success,
        error=error
    )


def log_security_event(event_type: str, user_id: Optional[str] = None, ip_address: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
    """Log security events."""
    logger = get_logger("security")
    logger.warning(
        "Security Event",
        event_type=event_type,
        user_id=user_id,
        ip_address=ip_address,
        details=details or {}
    )


def log_performance_metric(metric_name: str, value: float, unit: str, tags: Optional[Dict[str, Any]] = None):
    """Log performance metrics."""
    logger = get_logger("performance")
    logger.info(
        "Performance Metric",
        metric=metric_name,
        value=value,
        unit=unit,
        tags=tags or {}
    )


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    """Log error with context."""
    logger = get_logger("errors")
    logger.error(
        "Application Error",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {}
    )


def log_startup(version: str, environment: str):
    """Log application startup."""
    logger = get_logger("startup")
    logger.info(
        "Application Startup",
        version=version,
        environment=environment,
        timestamp=datetime.utcnow().isoformat()
    )


def log_shutdown():
    """Log application shutdown."""
    logger = get_logger("shutdown")
    logger.info(
        "Application Shutdown",
        timestamp=datetime.utcnow().isoformat()
    )


# Default logger instance
default_logger = get_logger() 