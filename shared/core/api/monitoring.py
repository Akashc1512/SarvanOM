"""
Universal Knowledge Hub - Monitoring Module
Centralized monitoring and metrics for the knowledge platform.

This module provides:
- Prometheus metrics integration
- Performance monitoring
- Error tracking
- Cache monitoring
- System resource monitoring

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import time
import psutil
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import os
# Set multiprocess mode to disabled to avoid file creation issues on Windows
os.environ.setdefault('PROMETHEUS_MULTIPROC_DIR', '')

from prometheus_client import Counter, Histogram, Gauge

# Prometheus metrics
request_counter = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"]
)

error_counter = Counter(
    "http_errors_total",
    "Total HTTP errors",
    ["method", "endpoint", "error_type"]
)

active_connections = Gauge(
    "active_connections",
    "Number of active connections"
)

cache_hits = Counter(
    "cache_hits_total",
    "Total cache hits",
    ["cache_name"]
)

cache_misses = Counter(
    "cache_misses_total", 
    "Total cache misses",
    ["cache_name"]
)

memory_usage = Gauge(
    "memory_usage_bytes",
    "Memory usage in bytes",
    ["type"]
)

cpu_usage = Gauge(
    "cpu_usage_percent",
    "CPU usage percentage",
    ["core"]
)

def record_request(method: str, endpoint: str, status: int, duration: float):
    """Record HTTP request metrics."""
    request_counter.labels(method=method, endpoint=endpoint, status=status).inc()
    request_duration.labels(method=method, endpoint=endpoint).observe(duration)

def record_error(method: str, endpoint: str, error_type: str):
    """Record error metrics."""
    error_counter.labels(method=method, endpoint=endpoint, error_type=error_type).inc()

def record_cache_hit(cache_name: str):
    """Record cache hit."""
    cache_hits.labels(cache_name=cache_name).inc()

def record_cache_miss(cache_name: str):
    """Record cache miss."""
    cache_misses.labels(cache_name=cache_name).inc()

def update_system_metrics():
    """Update system resource metrics."""
    # Memory metrics
    memory = psutil.virtual_memory()
    memory_usage.labels(type="used").set(memory.used)
    memory_usage.labels(type="available").set(memory.available)
    memory_usage.labels(type="total").set(memory.total)
    
    # CPU metrics
    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    for i, percent in enumerate(cpu_percent):
        cpu_usage.labels(core=str(i)).set(percent)

def get_metrics_summary() -> Dict[str, Any]:
    """Get comprehensive metrics summary."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system": {
            "memory": dict(psutil.virtual_memory()._asdict()),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_count": psutil.cpu_count(),
        },
        "prometheus": {
            "request_counter": request_counter._value.sum(),
            "error_counter": error_counter._value.sum(),
            "active_connections": active_connections._value.get(),
        }
    } 