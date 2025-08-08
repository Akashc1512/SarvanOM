"""
Universal Knowledge Hub - Monitoring Module
Centralized monitoring and metrics for the knowledge platform.

This module provides:
- Prometheus metrics integration (Windows-compatible)
- Performance monitoring
- Error tracking
- Cache monitoring
- System resource monitoring

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import time
import psutil
import platform
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Windows compatibility check
IS_WINDOWS = platform.system().lower() == "windows"

# Set multiprocess mode to disabled to avoid file creation issues on Windows
os.environ.setdefault('PROMETHEUS_MULTIPROC_DIR', '')

# Conditional Prometheus import with fallback
PROMETHEUS_AVAILABLE = False
try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
    logger.info("Prometheus client successfully imported")
except ImportError as e:
    logger.warning(f"Prometheus client not available: {e}")
except Exception as e:
    logger.warning(f"Prometheus client initialization failed: {e}")

# Fallback metrics implementation for Windows or when Prometheus is unavailable
class FallbackMetrics:
    """Fallback metrics implementation when Prometheus is unavailable."""
    
    def __init__(self):
        self.metrics = {}
    
    def _get_metric(self, name: str, metric_type: str = "counter"):
        if name not in self.metrics:
            self.metrics[name] = {"value": 0, "type": metric_type, "labels": {}}
        return self.metrics[name]
    
    def inc(self, amount: float = 1.0):
        """Increment counter."""
        self.metrics["value"] += amount
    
    def observe(self, value: float):
        """Record histogram observation."""
        if "observations" not in self.metrics:
            self.metrics["observations"] = []
        self.metrics["observations"].append(value)
    
    def set(self, value: float):
        """Set gauge value."""
        self.metrics["value"] = value
    
    def labels(self, **kwargs):
        """Set labels (no-op for fallback)."""
        self.metrics["labels"] = kwargs
        return self

class FallbackCounter(FallbackMetrics):
    """Fallback counter implementation."""
    pass

class FallbackHistogram(FallbackMetrics):
    """Fallback histogram implementation."""
    pass

class FallbackGauge(FallbackMetrics):
    """Fallback gauge implementation."""
    pass

# Initialize metrics with fallback support
def create_metric(metric_class, name: str, description: str, labelnames: list = None):
    """Create metric with fallback support."""
    if PROMETHEUS_AVAILABLE and not IS_WINDOWS:
        try:
            return metric_class(name, description, labelnames or [])
        except Exception as e:
            logger.warning(f"Failed to create Prometheus metric {name}: {e}")
    
    # Use fallback implementation
    fallback_class = {
        Counter: FallbackCounter,
        Histogram: FallbackHistogram,
        Gauge: FallbackGauge
    }.get(metric_class, FallbackCounter)
    
    metric = fallback_class()
    metric.metrics["name"] = name
    metric.metrics["description"] = description
    metric.metrics["labelnames"] = labelnames or []
    logger.info(f"Using fallback metric for {name}")
    return metric

# Create metrics with fallback support
request_counter = create_metric(
    Counter, "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)

request_duration = create_metric(
    Histogram, "http_request_duration_seconds", "HTTP request duration", ["method", "endpoint"]
)

error_counter = create_metric(
    Counter, "http_errors_total", "Total HTTP errors", ["method", "endpoint", "error_type"]
)

active_connections = create_metric(
    Gauge, "active_connections", "Number of active connections"
)

cache_hits = create_metric(
    Counter, "cache_hits_total", "Total cache hits", ["cache_name"]
)

cache_misses = create_metric(
    Counter, "cache_misses_total", "Total cache misses", ["cache_name"]
)

memory_usage = create_metric(
    Gauge, "memory_usage_bytes", "Memory usage in bytes", ["type"]
)

cpu_usage = create_metric(
    Gauge, "cpu_usage_percent", "CPU usage percentage", ["core"]
)

def record_request(method: str, endpoint: str, status: int, duration: float):
    """Record HTTP request metrics."""
    try:
        request_counter.labels(method=method, endpoint=endpoint, status=status).inc()
        request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    except Exception as e:
        logger.warning(f"Failed to record request metrics: {e}")

def record_error(method: str, endpoint: str, error_type: str):
    """Record error metrics."""
    try:
        error_counter.labels(method=method, endpoint=endpoint, error_type=error_type).inc()
    except Exception as e:
        logger.warning(f"Failed to record error metrics: {e}")

def record_cache_hit(cache_name: str):
    """Record cache hit."""
    try:
        cache_hits.labels(cache_name=cache_name).inc()
    except Exception as e:
        logger.warning(f"Failed to record cache hit: {e}")

def record_cache_miss(cache_name: str):
    """Record cache miss."""
    try:
        cache_misses.labels(cache_name=cache_name).inc()
    except Exception as e:
        logger.warning(f"Failed to record cache miss: {e}")

def update_system_metrics():
    """Update system resource metrics."""
    try:
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_usage.labels(type="used").set(memory.used)
        memory_usage.labels(type="available").set(memory.available)
        memory_usage.labels(type="total").set(memory.total)
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        for i, percent in enumerate(cpu_percent):
            cpu_usage.labels(core=f"cpu_{i}").set(percent)
    except Exception as e:
        logger.warning(f"Failed to update system metrics: {e}")

def get_metrics_summary() -> Dict[str, Any]:
    """Get metrics summary for health checks."""
    try:
        summary = {
            "prometheus_available": PROMETHEUS_AVAILABLE,
            "platform": platform.system(),
            "windows_compatibility_mode": IS_WINDOWS,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available
            }
        }
        
        # Add fallback metrics if Prometheus is not available
        if not PROMETHEUS_AVAILABLE or IS_WINDOWS:
            summary["fallback_metrics"] = {
                "request_counter": getattr(request_counter, 'metrics', {}),
                "error_counter": getattr(error_counter, 'metrics', {}),
                "memory_usage": getattr(memory_usage, 'metrics', {})
            }
        
        return summary
    except Exception as e:
        logger.error(f"Failed to get metrics summary: {e}")
        return {
            "error": str(e),
            "prometheus_available": PROMETHEUS_AVAILABLE,
            "platform": platform.system()
        }

def get_prometheus_metrics() -> str:
    """Get metrics in Prometheus format."""
    if PROMETHEUS_AVAILABLE and not IS_WINDOWS:
        try:
            from prometheus_client import generate_latest
            return generate_latest().decode('utf-8')
        except Exception as e:
            logger.warning(f"Failed to generate Prometheus metrics: {e}")
    
    # Return fallback metrics format
    fallback_metrics = []
    for metric_name, metric in [
        ("http_requests_total", request_counter),
        ("http_errors_total", error_counter),
        ("memory_usage_bytes", memory_usage),
        ("cpu_usage_percent", cpu_usage)
    ]:
        if hasattr(metric, 'metrics'):
            value = metric.metrics.get('value', 0)
            fallback_metrics.append(f"# HELP {metric_name} Fallback metric")
            fallback_metrics.append(f"# TYPE {metric_name} counter")
            fallback_metrics.append(f"{metric_name} {value}")
    
    return "\n".join(fallback_metrics)

# Health check function
def check_monitoring_health() -> Dict[str, Any]:
    """Check monitoring system health."""
    return {
        "status": "healthy" if PROMETHEUS_AVAILABLE or IS_WINDOWS else "degraded",
        "prometheus_available": PROMETHEUS_AVAILABLE,
        "windows_compatibility_mode": IS_WINDOWS,
        "fallback_active": not PROMETHEUS_AVAILABLE or IS_WINDOWS,
        "message": "Monitoring system operational with fallback support" if IS_WINDOWS else "Monitoring system operational"
    } 