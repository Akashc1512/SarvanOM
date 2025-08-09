"""
Metrics Module - SarvanOM

This module provides metrics and monitoring functionality for all services.
"""

from .metrics_service import get_metrics_service, MetricsService

__all__ = [
    "get_metrics_service",
    "MetricsService",
]
