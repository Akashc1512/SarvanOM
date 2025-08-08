"""
Unified Logging Configuration for Backend Services

This module provides a centralized logging configuration system that:
- Configures Python logging at the application entry point
- Uses environment variables to control log levels
- Provides structured JSON logging for production
- Includes comprehensive event logging for monitoring
- Integrates with FastAPI and Uvicorn
- Supports different environments (development, testing, production)

Features:
- Environment-based configuration (LOG_LEVEL, LOG_FORMAT, LOG_FILE)
- Structured JSON logging with timestamps and metadata
- Request/response correlation tracking
- Performance monitoring with timing information
- Error logging with stack traces at debug level
- FastAPI integration with startup event logging
- Uvicorn log redirection and formatting
- Agent lifecycle event logging

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import os
import sys
import json
import logging
import logging.config
import logging.handlers
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union, List
from pathlib import Path
from contextlib import contextmanager

try:
    from fastapi import FastAPI, Request
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    FastAPI = None
    Request = None

# Import configuration manager if available
try:
    from shared.core.config.environment_manager import get_environment_manager
    ENVIRONMENT_MANAGER_AVAILABLE = True
except ImportError:
    ENVIRONMENT_MANAGER_AVAILABLE = False


class StructuredJSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    Provides consistent JSON output with timestamps, levels, and metadata.
    Masks sensitive information and handles exceptions gracefully.
    """
    
    def __init__(self, service_name: str = "sarvanom", version: str = "1.0.0"):
        super().__init__()
        self.service_name = service_name
        self.version = version
        self.sensitive_keys = {
            'password', 'token', 'key', 'secret', 'auth', 'credential', 
            'api_key', 'jwt', 'bearer', 'authorization'
        }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        
        # Base log entry
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service_name,
            "version": self.version,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add process and thread info
        log_entry.update({
            "process_id": record.process,
            "thread_id": record.thread,
            "thread_name": record.threadName,
        })
        
        # Add request ID if available
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        
        # Add user ID if available
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        # Add extra fields while masking sensitive information
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'getMessage', 'exc_info',
                          'exc_text', 'stack_info']:
                
                # Mask sensitive information
                if any(sensitive in key.lower() for sensitive in self.sensitive_keys):
                    log_entry[key] = "***MASKED***"
                else:
                    log_entry[key] = value
        
        # Add exception information
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
            }
            
            # Add full stack trace only in debug mode
            if record.levelno == logging.DEBUG:
                log_entry['exception']['traceback'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)


class UnifiedLogger:
    """
    Unified logger wrapper that provides consistent logging interface.
    
    Provides methods for different log levels and automatically adds
    contextual information like request IDs and timing data.
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._request_id = None
        self._user_id = None
    
    def set_context(self, request_id: str = None, user_id: str = None):
        """Set context information for logging."""
        self._request_id = request_id
        self._user_id = user_id
    
    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log message with context information."""
        extra = kwargs.copy()
        
        # Handle exc_info separately as it's a special logging parameter
        exc_info = extra.pop('exc_info', None)
        
        if self._request_id:
            extra['request_id'] = self._request_id
        
        if self._user_id:
            extra['user_id'] = self._user_id
        
        self.logger.log(level, message, extra=extra, exc_info=exc_info)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log_with_context(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with stack trace."""
        # Don't override exc_info if already set
        if 'exc_info' not in kwargs:
            kwargs['exc_info'] = True
        self._log_with_context(logging.ERROR, message, **kwargs)


class LoggingConfig:
    """
    Unified logging configuration manager.
    
    Handles configuration from environment variables and provides
    methods to set up logging for different components.
    """
    
    def __init__(self):
        self.service_name = os.getenv('SERVICE_NAME', 'sarvanom')
        self.version = os.getenv('APP_VERSION', '1.0.0')
        
        # Get configuration from environment or configuration manager
        if ENVIRONMENT_MANAGER_AVAILABLE:
            try:
                env_manager = get_environment_manager()
                config = env_manager.get_config()
                self.log_level = config.log_level
                self.environment = env_manager.environment.value
            except Exception:
                self.log_level = os.getenv('LOG_LEVEL', 'INFO')
                self.environment = os.getenv('APP_ENV', 'development')
        else:
            self.log_level = os.getenv('LOG_LEVEL', 'INFO')
            self.environment = os.getenv('APP_ENV', 'development')
        
        self.log_format = os.getenv('LOG_FORMAT', 'json' if self.environment == 'production' else 'text')
        self.log_file = os.getenv('LOG_FILE', None)
        self.max_file_size = int(os.getenv('LOG_MAX_FILE_SIZE_MB', '100')) * 1024 * 1024
        self.backup_count = int(os.getenv('LOG_BACKUP_COUNT', '5'))
        
        # Configure root logger level
        self.log_level_int = getattr(logging, self.log_level.upper(), logging.INFO)
    
    def configure_root_logging(self):
        """Configure root logging with appropriate handlers and formatters."""
        
        # Clear any existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
        # Set root log level
        root_logger.setLevel(self.log_level_int)
        
        # Create formatter
        if self.log_format.lower() == 'json':
            formatter = StructuredJSONFormatter(self.service_name, self.version)
        else:
            # Simple text formatter for development
            formatter = logging.Formatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(self.log_level_int)
        root_logger.addHandler(console_handler)
        
        # File handler (if specified)
        if self.log_file:
            self._setup_file_handler(root_logger, formatter)
        
        # Configure third-party loggers
        self._configure_third_party_loggers()
    
    def _setup_file_handler(self, logger: logging.Logger, formatter: logging.Formatter):
        """Set up rotating file handler."""
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(self.log_level_int)
        logger.addHandler(file_handler)
    
    def _configure_third_party_loggers(self):
        """Configure third-party library loggers."""
        
        # Uvicorn loggers
        uvicorn_loggers = [
            'uvicorn',
            'uvicorn.access',
            'uvicorn.error'
        ]
        
        for logger_name in uvicorn_loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(self.log_level_int)
            # Clear handlers to use root logger handlers
            logger.handlers.clear()
            logger.propagate = True
        
        # FastAPI logger
        fastapi_logger = logging.getLogger('fastapi')
        fastapi_logger.setLevel(self.log_level_int)
        fastapi_logger.propagate = True
        
        # Database loggers (reduce verbosity in production)
        db_loggers = ['sqlalchemy.engine', 'aiopg', 'asyncpg']
        for logger_name in db_loggers:
            logger = logging.getLogger(logger_name)
            if self.environment == 'production':
                logger.setLevel(logging.WARNING)
            else:
                logger.setLevel(logging.INFO)
            logger.propagate = True
    
    def get_logger(self, name: str) -> UnifiedLogger:
        """Get a unified logger instance."""
        return UnifiedLogger(name)


# Global logging configuration instance
_logging_config = None


def setup_logging(
    service_name: str = None,
    version: str = None,
    log_level: str = None,
    log_format: str = None,
    log_file: str = None
) -> LoggingConfig:
    """
    Set up unified logging configuration.
    
    This should be called once at application startup, preferably in the
    FastAPI startup event or main module initialization.
    
    Args:
        service_name: Name of the service (defaults to environment variable)
        version: Version of the service (defaults to environment variable)
        log_level: Log level (defaults to environment variable)
        log_format: Log format - 'json' or 'text' (defaults to environment variable)
        log_file: Log file path (optional, defaults to environment variable)
    
    Returns:
        LoggingConfig instance
    """
    global _logging_config
    
    # Override environment variables if provided
    if service_name:
        os.environ['SERVICE_NAME'] = service_name
    if version:
        os.environ['APP_VERSION'] = version
    if log_level:
        os.environ['LOG_LEVEL'] = log_level
    if log_format:
        os.environ['LOG_FORMAT'] = log_format
    if log_file:
        os.environ['LOG_FILE'] = log_file
    
    # Create and configure logging
    _logging_config = LoggingConfig()
    _logging_config.configure_root_logging()
    
    # Log configuration startup
    logger = _logging_config.get_logger(__name__)
    logger.info(
        "Unified logging configured",
        service_name=_logging_config.service_name,
        version=_logging_config.version,
        log_level=_logging_config.log_level,
        log_format=_logging_config.log_format,
        environment=_logging_config.environment,
        log_file=_logging_config.log_file,
        component="logging_setup"
    )
    
    return _logging_config


def get_logger(name: str) -> UnifiedLogger:
    """
    Get a unified logger instance.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        UnifiedLogger instance
    """
    global _logging_config
    
    if _logging_config is None:
        # Auto-configure if not already done
        _logging_config = setup_logging()
    
    return _logging_config.get_logger(name)


@contextmanager
def log_execution_time(logger: UnifiedLogger, operation: str, **context):
    """
    Context manager to log execution time of operations.
    
    Args:
        logger: Logger instance
        operation: Description of the operation
        **context: Additional context to include in logs
    """
    start_time = time.time()
    operation_id = str(uuid.uuid4())[:8]
    
    logger.info(
        f"Starting {operation}",
        operation=operation,
        operation_id=operation_id,
        **context
    )
    
    try:
        yield operation_id
        duration = time.time() - start_time
        logger.info(
            f"Completed {operation}",
            operation=operation,
            operation_id=operation_id,
            duration_seconds=round(duration, 3),
            duration_ms=round(duration * 1000, 1),
            status="success",
            **context
        )
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"Failed {operation}",
            operation=operation,
            operation_id=operation_id,
            duration_seconds=round(duration, 3),
            duration_ms=round(duration * 1000, 1),
            status="error",
            error_type=type(e).__name__,
            error_message=str(e),
            **context
        )
        raise


def log_execution_time_decorator(operation: str):
    """
    Decorator version of log_execution_time for async functions.
    
    Args:
        operation: Description of the operation
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            start_time = time.time()
            operation_id = str(uuid.uuid4())[:8]
            
            logger.info(
                f"Starting {operation}",
                operation=operation,
                operation_id=operation_id,
                function=func.__name__
            )
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(
                    f"Completed {operation}",
                    operation=operation,
                    operation_id=operation_id,
                    duration_seconds=round(duration, 3),
                    duration_ms=round(duration * 1000, 1),
                    status="success",
                    function=func.__name__
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Failed {operation}",
                    operation=operation,
                    operation_id=operation_id,
                    duration_seconds=round(duration, 3),
                    duration_ms=round(duration * 1000, 1),
                    status="error",
                    error_type=type(e).__name__,
                    error_message=str(e),
                    function=func.__name__
                )
                raise
        return wrapper
    return decorator


def log_agent_lifecycle(logger: UnifiedLogger, agent_name: str, action: str, **context):
    """
    Log agent lifecycle events (start, finish, error).
    
    Args:
        logger: Logger instance
        agent_name: Name of the agent
        action: Action type ('start', 'finish', 'error')
        **context: Additional context
    """
    logger.info(
        f"Agent {action}",
        agent_name=agent_name,
        action=action,
        component="agent_lifecycle",
        **context
    )


def log_query_event(logger: UnifiedLogger, query: str, event: str, **context):
    """
    Log query processing events.
    
    Args:
        logger: Logger instance
        query: The query being processed
        event: Event type ('received', 'processing', 'completed', 'failed')
        **context: Additional context
    """
    # Truncate long queries for logging
    display_query = query[:200] + "..." if len(query) > 200 else query
    
    logger.info(
        f"Query {event}",
        query=display_query,
        query_length=len(query),
        event=event,
        component="query_processing",
        **context
    )


if FASTAPI_AVAILABLE:
    def setup_fastapi_logging(app: FastAPI, service_name: str = None):
        """
        Set up logging integration with FastAPI.
        
        Args:
            app: FastAPI application instance
            service_name: Service name for logging
        """
        
        @app.on_event("startup")
        async def startup_event():
            """FastAPI startup event - configure logging."""
            config = setup_logging(service_name=service_name or "fastapi-service")
            logger = config.get_logger(__name__)
            
            logger.info(
                "FastAPI application starting up",
                app_title=app.title,
                app_version=app.version,
                component="fastapi_startup"
            )
        
        @app.on_event("shutdown")
        async def shutdown_event():
            """FastAPI shutdown event."""
            logger = get_logger(__name__)
            logger.info(
                "FastAPI application shutting down",
                app_title=app.title,
                component="fastapi_shutdown"
            )
        
        @app.middleware("http")
        async def request_logging_middleware(request: Request, call_next):
            """Middleware to log HTTP requests."""
            logger = get_logger(__name__)
            request_id = str(uuid.uuid4())
            start_time = time.time()
            
            # Set context for this request
            logger.set_context(request_id=request_id)
            
            # Log request start
            logger.info(
                "HTTP request received",
                method=request.method,
                url=str(request.url),
                client_ip=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                request_id=request_id,
                component="http_request"
            )
            
            try:
                response = await call_next(request)
                duration = time.time() - start_time
                
                # Log successful response
                logger.info(
                    "HTTP request completed",
                    method=request.method,
                    url=str(request.url),
                    status_code=response.status_code,
                    duration_seconds=round(duration, 3),
                    duration_ms=round(duration * 1000, 1),
                    request_id=request_id,
                    component="http_response"
                )
                
                return response
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Log error response
                logger.error(
                    "HTTP request failed",
                    method=request.method,
                    url=str(request.url),
                    error_type=type(e).__name__,
                    error_message=str(e),
                    duration_seconds=round(duration, 3),
                    duration_ms=round(duration * 1000, 1),
                    request_id=request_id,
                    component="http_error"
                )
                raise


# Export main functions
__all__ = [
    'setup_logging',
    'get_logger',
    'log_execution_time',
    'log_execution_time_decorator',
    'log_agent_lifecycle',
    'log_query_event',
    'setup_fastapi_logging',
    'UnifiedLogger',
    'LoggingConfig'
]