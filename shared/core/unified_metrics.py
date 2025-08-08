"""
Unified Metrics Interface
Automatically chooses between Prometheus and Windows-compatible metrics.

This module provides:
- Automatic platform detection
- Fallback to Windows-compatible metrics on Windows
- Unified API for both implementations
- Graceful error handling

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import platform
import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Platform detection
IS_WINDOWS = platform.system().lower() == "windows"

# Import metrics implementations
try:
    from .api.monitoring import (
        record_request as prometheus_record_request,
        record_error as prometheus_record_error,
        record_cache_hit as prometheus_record_cache_hit,
        record_cache_miss as prometheus_record_cache_miss,
        update_system_metrics as prometheus_update_system_metrics,
        get_metrics_summary as prometheus_get_metrics_summary,
        get_prometheus_metrics as prometheus_get_prometheus_metrics,
        check_monitoring_health as prometheus_check_monitoring_health,
        PROMETHEUS_AVAILABLE
    )
    PROMETHEUS_IMPORT_SUCCESS = True
except Exception as e:
    logger.warning(f"Failed to import Prometheus monitoring: {e}")
    PROMETHEUS_IMPORT_SUCCESS = False
    PROMETHEUS_AVAILABLE = False

try:
    from .windows_metrics import (
        record_request as windows_record_request,
        record_error as windows_record_error,
        record_cache_hit as windows_record_cache_hit,
        record_cache_miss as windows_record_cache_miss,
        update_system_metrics as windows_update_system_metrics,
        get_metrics_summary as windows_get_metrics_summary,
        get_prometheus_metrics as windows_get_prometheus_metrics,
        check_monitoring_health as windows_check_monitoring_health
    )
    WINDOWS_METRICS_IMPORT_SUCCESS = True
except Exception as e:
    logger.warning(f"Failed to import Windows metrics: {e}")
    WINDOWS_METRICS_IMPORT_SUCCESS = False

def _get_metrics_implementation():
    """Determine which metrics implementation to use."""
    if IS_WINDOWS:
        if WINDOWS_METRICS_IMPORT_SUCCESS:
            logger.info("Using Windows-compatible metrics implementation")
            return "windows"
        else:
            logger.warning("Windows metrics not available, using fallback")
            return "fallback"
    else:
        if PROMETHEUS_IMPORT_SUCCESS and PROMETHEUS_AVAILABLE:
            logger.info("Using Prometheus metrics implementation")
            return "prometheus"
        elif WINDOWS_METRICS_IMPORT_SUCCESS:
            logger.info("Prometheus not available, using Windows metrics")
            return "windows"
        else:
            logger.warning("No metrics implementation available, using fallback")
            return "fallback"

# Determine implementation at module load time
CURRENT_IMPLEMENTATION = _get_metrics_implementation()

class FallbackMetrics:
    """Fallback metrics implementation when no other implementation is available."""
    
    @staticmethod
    def record_request(method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics (no-op fallback)."""
        logger.debug(f"Fallback: Record request {method} {endpoint} {status} {duration}s")
    
    @staticmethod
    def record_error(method: str, endpoint: str, error_type: str):
        """Record error metrics (no-op fallback)."""
        logger.debug(f"Fallback: Record error {method} {endpoint} {error_type}")
    
    @staticmethod
    def record_cache_hit(cache_name: str):
        """Record cache hit (no-op fallback)."""
        logger.debug(f"Fallback: Record cache hit {cache_name}")
    
    @staticmethod
    def record_cache_miss(cache_name: str):
        """Record cache miss (no-op fallback)."""
        logger.debug(f"Fallback: Record cache miss {cache_name}")
    
    @staticmethod
    def update_system_metrics():
        """Update system metrics (no-op fallback)."""
        logger.debug("Fallback: Update system metrics")
    
    @staticmethod
    def get_metrics_summary() -> Dict[str, Any]:
        """Get metrics summary (fallback)."""
        return {
            "implementation": "fallback",
            "status": "degraded",
            "message": "No metrics implementation available",
            "platform": platform.system(),
            "windows_detected": IS_WINDOWS
        }
    
    @staticmethod
    def get_prometheus_metrics() -> str:
        """Get Prometheus metrics (fallback)."""
        return "# No metrics available\n"
    
    @staticmethod
    def check_monitoring_health() -> Dict[str, Any]:
        """Check monitoring health (fallback)."""
        return {
            "status": "degraded",
            "implementation": "fallback",
            "platform": platform.system(),
            "message": "No metrics implementation available"
        }

def _get_implementation_functions():
    """Get the appropriate implementation functions."""
    if CURRENT_IMPLEMENTATION == "prometheus":
        return {
            "record_request": prometheus_record_request,
            "record_error": prometheus_record_error,
            "record_cache_hit": prometheus_record_cache_hit,
            "record_cache_miss": prometheus_record_cache_miss,
            "update_system_metrics": prometheus_update_system_metrics,
            "get_metrics_summary": prometheus_get_metrics_summary,
            "get_prometheus_metrics": prometheus_get_prometheus_metrics,
            "check_monitoring_health": prometheus_check_monitoring_health
        }
    elif CURRENT_IMPLEMENTATION == "windows":
        return {
            "record_request": windows_record_request,
            "record_error": windows_record_error,
            "record_cache_hit": windows_record_cache_hit,
            "record_cache_miss": windows_record_cache_miss,
            "update_system_metrics": windows_update_system_metrics,
            "get_metrics_summary": windows_get_metrics_summary,
            "get_prometheus_metrics": windows_get_prometheus_metrics,
            "check_monitoring_health": windows_check_monitoring_health
        }
    else:
        return {
            "record_request": FallbackMetrics.record_request,
            "record_error": FallbackMetrics.record_error,
            "record_cache_hit": FallbackMetrics.record_cache_hit,
            "record_cache_miss": FallbackMetrics.record_cache_miss,
            "update_system_metrics": FallbackMetrics.update_system_metrics,
            "get_metrics_summary": FallbackMetrics.get_metrics_summary,
            "get_prometheus_metrics": FallbackMetrics.get_prometheus_metrics,
            "check_monitoring_health": FallbackMetrics.check_monitoring_health
        }

# Get the implementation functions
_impl = _get_implementation_functions()

# Export unified API
def record_request(method: str, endpoint: str, status: int, duration: float):
    """Record HTTP request metrics."""
    try:
        _impl["record_request"](method, endpoint, status, duration)
    except Exception as e:
        logger.warning(f"Failed to record request metrics: {e}")

def record_error(method: str, endpoint: str, error_type: str):
    """Record error metrics."""
    try:
        _impl["record_error"](method, endpoint, error_type)
    except Exception as e:
        logger.warning(f"Failed to record error metrics: {e}")

def record_cache_hit(cache_name: str):
    """Record cache hit."""
    try:
        _impl["record_cache_hit"](cache_name)
    except Exception as e:
        logger.warning(f"Failed to record cache hit: {e}")

def record_cache_miss(cache_name: str):
    """Record cache miss."""
    try:
        _impl["record_cache_miss"](cache_name)
    except Exception as e:
        logger.warning(f"Failed to record cache miss: {e}")

def update_system_metrics():
    """Update system resource metrics."""
    try:
        _impl["update_system_metrics"]()
    except Exception as e:
        logger.warning(f"Failed to update system metrics: {e}")

def get_metrics_summary() -> Dict[str, Any]:
    """Get metrics summary."""
    try:
        summary = _impl["get_metrics_summary"]()
        summary["implementation"] = CURRENT_IMPLEMENTATION
        summary["platform"] = platform.system()
        summary["windows_detected"] = IS_WINDOWS
        return summary
    except Exception as e:
        logger.error(f"Failed to get metrics summary: {e}")
        return {
            "error": str(e),
            "implementation": CURRENT_IMPLEMENTATION,
            "platform": platform.system(),
            "windows_detected": IS_WINDOWS
        }

def get_prometheus_metrics() -> str:
    """Get metrics in Prometheus format."""
    try:
        return _impl["get_prometheus_metrics"]()
    except Exception as e:
        logger.error(f"Failed to get Prometheus metrics: {e}")
        return f"# Error generating metrics: {e}\n"

def check_monitoring_health() -> Dict[str, Any]:
    """Check monitoring system health."""
    try:
        health = _impl["check_monitoring_health"]()
        health["implementation"] = CURRENT_IMPLEMENTATION
        health["platform"] = platform.system()
        health["windows_detected"] = IS_WINDOWS
        return health
    except Exception as e:
        logger.error(f"Failed to check monitoring health: {e}")
        return {
            "status": "error",
            "error": str(e),
            "implementation": CURRENT_IMPLEMENTATION,
            "platform": platform.system(),
            "windows_detected": IS_WINDOWS
        }

def get_implementation_info() -> Dict[str, Any]:
    """Get information about the current metrics implementation."""
    return {
        "current_implementation": CURRENT_IMPLEMENTATION,
        "platform": platform.system(),
        "windows_detected": IS_WINDOWS,
        "prometheus_import_success": PROMETHEUS_IMPORT_SUCCESS,
        "windows_metrics_import_success": WINDOWS_METRICS_IMPORT_SUCCESS,
        "prometheus_available": PROMETHEUS_AVAILABLE if 'PROMETHEUS_AVAILABLE' in globals() else False
    }

# Log the implementation choice at module load
logger.info(f"Unified metrics initialized with implementation: {CURRENT_IMPLEMENTATION}")
logger.info(f"Platform: {platform.system()}, Windows detected: {IS_WINDOWS}") 