"""
Windows-Compatible Metrics Collector
Provides metrics collection functionality that works reliably on Windows systems.

This module provides:
- Windows-compatible metrics collection
- Performance monitoring
- Error tracking
- System resource monitoring
- JSON-based metrics export

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import time
import psutil
import platform
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import json
import logging
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Metric types supported by the collector."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


@dataclass
class MetricValue:
    """Represents a metric value with labels."""

    value: float
    labels: Dict[str, str]
    timestamp: float


class WindowsMetricsCollector:
    """Windows-compatible metrics collector."""

    def __init__(self):
        self.metrics: Dict[str, Dict] = defaultdict(dict)
        self.lock = threading.Lock()
        self.start_time = time.time()

        # Initialize system metrics
        self._init_system_metrics()

    def _init_system_metrics(self):
        """Initialize system resource metrics."""
        self._create_metric(
            "memory_usage_bytes", "Memory usage in bytes", MetricType.GAUGE, ["type"]
        )
        self._create_metric(
            "cpu_usage_percent", "CPU usage percentage", MetricType.GAUGE, ["core"]
        )
        self._create_metric(
            "disk_usage_percent", "Disk usage percentage", MetricType.GAUGE, ["device"]
        )

    def _create_metric(
        self,
        name: str,
        description: str,
        metric_type: MetricType,
        label_names: List[str] = None,
    ):
        """Create a new metric."""
        with self.lock:
            self.metrics[name] = {
                "description": description,
                "type": metric_type.value,
                "label_names": label_names or [],
                "values": defaultdict(list),
                "created_at": time.time(),
            }

    def inc(self, metric_name: str, amount: float = 1.0, labels: Dict[str, str] = None):
        """Increment a counter metric."""
        with self.lock:
            if metric_name not in self.metrics:
                self._create_metric(
                    metric_name, f"Counter for {metric_name}", MetricType.COUNTER
                )

            label_key = self._get_label_key(labels or {})
            current_value = self._get_current_value(metric_name, label_key)
            new_value = current_value + amount

            self._set_value(metric_name, label_key, new_value)

    def set(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric value."""
        with self.lock:
            if metric_name not in self.metrics:
                self._create_metric(
                    metric_name, f"Gauge for {metric_name}", MetricType.GAUGE
                )

            label_key = self._get_label_key(labels or {})
            self._set_value(metric_name, label_key, value)

    def observe(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Record a histogram observation."""
        with self.lock:
            if metric_name not in self.metrics:
                self._create_metric(
                    metric_name, f"Histogram for {metric_name}", MetricType.HISTOGRAM
                )

            label_key = self._get_label_key(labels or {})
            self._add_observation(metric_name, label_key, value)

    def _get_label_key(self, labels: Dict[str, str]) -> str:
        """Convert labels to a string key."""
        return json.dumps(sorted(labels.items()))

    def _get_current_value(self, metric_name: str, label_key: str) -> float:
        """Get current value for a metric and label combination."""
        values = self.metrics[metric_name]["values"]
        if label_key in values and values[label_key]:
            return values[label_key][-1].value
        return 0.0

    def _set_value(self, metric_name: str, label_key: str, value: float):
        """Set a value for a metric and label combination."""
        metric_value = MetricValue(
            value=value,
            labels=json.loads(label_key) if label_key != "{}" else {},
            timestamp=time.time(),
        )
        self.metrics[metric_name]["values"][label_key].append(metric_value)

        # Keep only last 1000 values to prevent memory issues
        if len(self.metrics[metric_name]["values"][label_key]) > 1000:
            self.metrics[metric_name]["values"][label_key] = self.metrics[metric_name][
                "values"
            ][label_key][-1000:]

    def _add_observation(self, metric_name: str, label_key: str, value: float):
        """Add an observation to a histogram."""
        self._set_value(metric_name, label_key, value)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        with self.lock:
            summary = {
                "collector_type": "windows_metrics",
                "platform": platform.system(),
                "uptime_seconds": time.time() - self.start_time,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metrics_count": len(self.metrics),
                "system_info": self._get_system_info(),
                "metrics": {},
            }

            for metric_name, metric_data in self.metrics.items():
                summary["metrics"][metric_name] = {
                    "description": metric_data["description"],
                    "type": metric_data["type"],
                    "label_names": metric_data["label_names"],
                    "values_count": sum(
                        len(values) for values in metric_data["values"].values()
                    ),
                    "current_values": self._get_current_values(metric_name),
                }

            return summary

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            return {
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_total": memory.total,
                "memory_available": memory.available,
                "memory_percent": memory.percent,
                "disk_total": disk.total,
                "disk_free": disk.free,
                "disk_percent": (disk.used / disk.total) * 100,
            }
        except Exception as e:
            logger.warning(f"Failed to get system info: {e}")
            return {"error": str(e)}

    def _get_current_values(self, metric_name: str) -> Dict[str, float]:
        """Get current values for all label combinations of a metric."""
        current_values = {}
        metric_data = self.metrics[metric_name]

        for label_key, values in metric_data["values"].items():
            if values:
                labels = json.loads(label_key) if label_key != "{}" else {}
                label_str = (
                    ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
                    if labels
                    else "default"
                )
                current_values[label_str] = values[-1].value

        return current_values

    def export_prometheus_format(self) -> str:
        """Export metrics in Prometheus format."""
        with self.lock:
            lines = []

            for metric_name, metric_data in self.metrics.items():
                # Add help and type lines
                lines.append(f"# HELP {metric_name} {metric_data['description']}")
                lines.append(f"# TYPE {metric_name} {metric_data['type']}")

                # Add metric values
                for label_key, values in metric_data["values"].items():
                    if values:
                        labels = json.loads(label_key) if label_key != "{}" else {}
                        label_str = (
                            ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
                            if labels
                            else ""
                        )

                        if label_str:
                            lines.append(
                                f"{metric_name}{{{label_str}}} {values[-1].value}"
                            )
                        else:
                            lines.append(f"{metric_name} {values[-1].value}")

            return "\n".join(lines)

    def export_json_format(self) -> str:
        """Export metrics in JSON format."""
        return json.dumps(self.get_metrics_summary(), indent=2)

    def reset_metrics(self):
        """Reset all metrics."""
        with self.lock:
            self.metrics.clear()
            self._init_system_metrics()

    def update_system_metrics(self):
        """Update system resource metrics."""
        try:
            # Memory metrics
            memory = psutil.virtual_memory()
            self.set("memory_usage_bytes", memory.used, {"type": "used"})
            self.set("memory_usage_bytes", memory.available, {"type": "available"})
            self.set("memory_usage_bytes", memory.total, {"type": "total"})

            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            for i, percent in enumerate(cpu_percent):
                self.set("cpu_usage_percent", percent, {"core": f"cpu_{i}"})

            # Disk metrics
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            self.set("disk_usage_percent", disk_percent, {"device": "root"})

        except Exception as e:
            logger.warning(f"Failed to update system metrics: {e}")


# Global metrics collector instance
_metrics_collector = None


def get_metrics_collector() -> WindowsMetricsCollector:
    """Get the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = WindowsMetricsCollector()
    return _metrics_collector


# Convenience functions for common metrics
def record_request(method: str, endpoint: str, status: int, duration: float):
    """Record HTTP request metrics."""
    collector = get_metrics_collector()
    collector.inc(
        "http_requests_total",
        labels={"method": method, "endpoint": endpoint, "status": str(status)},
    )
    collector.observe(
        "http_request_duration_seconds",
        duration,
        labels={"method": method, "endpoint": endpoint},
    )


def record_error(method: str, endpoint: str, error_type: str):
    """Record error metrics."""
    collector = get_metrics_collector()
    collector.inc(
        "http_errors_total",
        labels={"method": method, "endpoint": endpoint, "error_type": error_type},
    )


def record_cache_hit(cache_name: str):
    """Record cache hit."""
    collector = get_metrics_collector()
    collector.inc("cache_hits_total", labels={"cache_name": cache_name})


def record_cache_miss(cache_name: str):
    """Record cache miss."""
    collector = get_metrics_collector()
    collector.inc("cache_misses_total", labels={"cache_name": cache_name})


def update_system_metrics():
    """Update system resource metrics."""
    collector = get_metrics_collector()
    collector.update_system_metrics()


def get_metrics_summary() -> Dict[str, Any]:
    """Get metrics summary."""
    collector = get_metrics_collector()
    return collector.get_metrics_summary()


def get_prometheus_metrics() -> str:
    """Get metrics in Prometheus format."""
    collector = get_metrics_collector()
    return collector.export_prometheus_format()


def check_monitoring_health() -> Dict[str, Any]:
    """Check monitoring system health."""
    return {
        "status": "healthy",
        "collector_type": "windows_metrics",
        "platform": platform.system(),
        "message": "Windows-compatible metrics collector operational",
    }
