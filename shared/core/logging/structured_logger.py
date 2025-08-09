"""
Structured logging system for SarvanOM backend.

Provides JSON-formatted logs with proper log levels, request correlation,
and sensitive data masking for production observability.
"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Union
from contextvars import ContextVar
from functools import wraps

# Request correlation ID for tracing requests across services
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class StructuredLogger:
    """Structured logger with JSON formatting and correlation IDs."""

    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # Ensure we have a handler
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _format_log(self, level: str, message: str, **kwargs) -> str:
        """Format log entry as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "logger": self.logger.name,
            "message": message,
            "request_id": request_id_var.get(),
        }

        # Add additional fields
        for key, value in kwargs.items():
            if key not in log_entry:
                log_entry[key] = self._mask_sensitive_data(key, value)

        return json.dumps(log_entry)

    def _mask_sensitive_data(self, key: str, value: Any) -> Any:
        """Mask sensitive data in logs."""
        sensitive_keys = {
            "api_key",
            "token",
            "password",
            "secret",
            "authorization",
            "openai_api_key",
            "anthropic_api_key",
            "qdrant_api_key",
        }

        if key.lower() in sensitive_keys:
            if isinstance(value, str) and len(value) > 8:
                return f"{value[:4]}...{value[-4:]}"
            return "***MASKED***"

        return value

    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(self._format_log("INFO", message, **kwargs))

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(self._format_log("WARNING", message, **kwargs))

    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(self._format_log("ERROR", message, **kwargs))

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(self._format_log("DEBUG", message, **kwargs))

    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(self._format_log("CRITICAL", message, **kwargs))

    def log(self, level: int, message: str, **kwargs):
        """Log message with specified level (for compatibility with standard logging)."""
        level_name = logging.getLevelName(level)
        if level_name == "WARNING":
            self.warning(message, **kwargs)
        elif level_name == "ERROR":
            self.error(message, **kwargs)
        elif level_name == "DEBUG":
            self.debug(message, **kwargs)
        elif level_name == "CRITICAL":
            self.critical(message, **kwargs)
        else:
            self.info(message, **kwargs)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)


def set_request_id(request_id: Optional[str] = None) -> str:
    """Set request correlation ID."""
    if request_id is None:
        request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    return request_id


def get_request_id() -> Optional[str]:
    """Get current request correlation ID."""
    return request_id_var.get()


def log_execution_time(func_name: str = None):
    """Decorator to log function execution time."""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            logger = get_logger(func.__module__)
            name = func_name or func.__name__

            try:
                logger.info(f"Starting {name}")
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(
                    f"Completed {name}", execution_time_ms=int(execution_time * 1000)
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"Failed {name}: {str(e)}",
                    execution_time_ms=int(execution_time * 1000),
                    error_type=type(e).__name__,
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            logger = get_logger(func.__module__)
            name = func_name or func.__name__

            try:
                logger.info(f"Starting {name}")
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(
                    f"Completed {name}", execution_time_ms=int(execution_time * 1000)
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"Failed {name}: {str(e)}",
                    execution_time_ms=int(execution_time * 1000),
                    error_type=type(e).__name__,
                )
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# Import asyncio for the decorator
import asyncio
