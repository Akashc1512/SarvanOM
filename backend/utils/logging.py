"""
Logging utilities for the clean architecture backend.

This module provides centralized logging functionality for all backend components.
"""

import logging
import sys
from typing import Optional
from datetime import datetime


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a logger instance with consistent configuration.

    Args:
        name: The logger name (usually __name__)
        level: Optional logging level override

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Set level if provided or use default
    if level is not None:
        logger.setLevel(level)
    elif not logger.handlers:  # Only set default level if no handlers exist
        logger.setLevel(logging.INFO)

    # Add handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    log_file: Optional[str] = None,
) -> None:
    """
    Set up global logging configuration.

    Args:
        level: Logging level
        format_string: Custom format string
        log_file: Optional log file path
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure root logger
    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout),
            *([logging.FileHandler(log_file)] if log_file else []),
        ],
    )


class StructuredLogger:
    """Structured logger for JSON-formatted logs."""

    def __init__(self, name: str):
        self.logger = get_logger(name)
        self.name = name

    def info(self, message: str, **kwargs):
        """Log info message with structured data."""
        extra_data = {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "logger": self.name,
            **kwargs,
        }
        self.logger.info(f"{message} | {extra_data}")

    def error(self, message: str, **kwargs):
        """Log error message with structured data."""
        extra_data = {
            "timestamp": datetime.now().isoformat(),
            "level": "ERROR",
            "logger": self.name,
            **kwargs,
        }
        self.logger.error(f"{message} | {extra_data}")

    def warning(self, message: str, **kwargs):
        """Log warning message with structured data."""
        extra_data = {
            "timestamp": datetime.now().isoformat(),
            "level": "WARNING",
            "logger": self.name,
            **kwargs,
        }
        self.logger.warning(f"{message} | {extra_data}")

    def debug(self, message: str, **kwargs):
        """Log debug message with structured data."""
        extra_data = {
            "timestamp": datetime.now().isoformat(),
            "level": "DEBUG",
            "logger": self.name,
            **kwargs,
        }
        self.logger.debug(f"{message} | {extra_data}")


def get_structured_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)
