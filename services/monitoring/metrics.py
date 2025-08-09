"""
Metrics collection service for production monitoring.

This module provides comprehensive metrics collection, aggregation, and reporting
capabilities for production deployment monitoring.
"""

import time
import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
import json

from config.production.monitoring import get_metrics_config


class MetricType(Enum):
    """Metric type enumeration."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Metric:
    """Metric data structure."""

    name: str
    type: MetricType
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    description: Optional[str] = None


class MetricsCollector:
    """Metrics collection and aggregation service."""

    def __init__(self):
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.lock = threading.Lock()
        self.config = get_metrics_config()

    def increment_counter(
        self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None
    ):
        """Increment a counter metric."""
        with self.lock:
            key = self._get_metric_key(name, labels)
            self.counters[key] += value
            self._add_metric(
                name, MetricType.COUNTER, float(self.counters[key]), labels
            )

    def set_gauge(
        self, name: str, value: float, labels: Optional[Dict[str, str]] = None
    ):
        """Set a gauge metric."""
        with self.lock:
            key = self._get_metric_key(name, labels)
            self.gauges[key] = value
            self._add_metric(name, MetricType.GAUGE, value, labels)

    def record_histogram(
        self, name: str, value: float, labels: Optional[Dict[str, str]] = None
    ):
        """Record a histogram metric."""
        with self.lock:
            key = self._get_metric_key(name, labels)
            self.histograms[key].append(value)
            self._add_metric(name, MetricType.HISTOGRAM, value, labels)

    def _get_metric_key(
        self, name: str, labels: Optional[Dict[str, str]] = None
    ) -> str:
        """Get metric key with labels."""
        if labels:
            label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            return f"{name}:{label_str}"
        return name

    def _add_metric(
        self,
        name: str,
        metric_type: MetricType,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ):
        """Add metric to collection."""
        metric = Metric(
            name=name,
            type=metric_type,
            value=value,
            timestamp=datetime.utcnow(),
            labels=labels or {},
        )
        self.metrics[name].append(metric)

        # Keep only recent metrics based on config
        max_metrics = self.config.get("max_metrics_per_name", 1000)
        if len(self.metrics[name]) > max_metrics:
            self.metrics[name] = self.metrics[name][-max_metrics:]

    def get_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> int:
        """Get current counter value."""
        key = self._get_metric_key(name, labels)
        return self.counters.get(key, 0)

    def get_gauge(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get current gauge value."""
        key = self._get_metric_key(name, labels)
        return self.gauges.get(key, 0.0)

    def get_histogram_stats(
        self, name: str, labels: Optional[Dict[str, str]] = None
    ) -> Dict[str, float]:
        """Get histogram statistics."""
        key = self._get_metric_key(name, labels)
        values = list(self.histograms.get(key, []))

        if not values:
            return {"count": 0, "sum": 0, "min": 0, "max": 0, "avg": 0}

        return {
            "count": len(values),
            "sum": sum(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
        }

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        with self.lock:
            summary = {
                "timestamp": datetime.utcnow().isoformat(),
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histograms": {
                    name: self.get_histogram_stats(name)
                    for name in self.histograms.keys()
                },
                "total_metrics": sum(len(metrics) for metrics in self.metrics.values()),
            }
            return summary

    def clear_old_metrics(self, max_age_hours: int = 24):
        """Clear metrics older than specified age."""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)

        with self.lock:
            for name in list(self.metrics.keys()):
                self.metrics[name] = [
                    metric
                    for metric in self.metrics[name]
                    if metric.timestamp > cutoff_time
                ]

                # Remove empty metric lists
                if not self.metrics[name]:
                    del self.metrics[name]


class PerformanceMonitor:
    """Performance monitoring with automatic metrics collection."""

    def __init__(self, collector: MetricsCollector):
        self.collector = collector

    def monitor_function(self, metric_name: str):
        """Decorator to monitor function performance."""

        def decorator(func):
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.collector.record_histogram(f"{metric_name}_duration", duration)
                    self.collector.increment_counter(f"{metric_name}_calls")
                    self.collector.increment_counter(f"{metric_name}_success")
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self.collector.record_histogram(f"{metric_name}_duration", duration)
                    self.collector.increment_counter(f"{metric_name}_calls")
                    self.collector.increment_counter(f"{metric_name}_errors")
                    raise

            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.collector.record_histogram(f"{metric_name}_duration", duration)
                    self.collector.increment_counter(f"{metric_name}_calls")
                    self.collector.increment_counter(f"{metric_name}_success")
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self.collector.record_histogram(f"{metric_name}_duration", duration)
                    self.collector.increment_counter(f"{metric_name}_calls")
                    self.collector.increment_counter(f"{metric_name}_errors")
                    raise

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    def monitor_api_endpoint(self, endpoint: str):
        """Decorator to monitor API endpoint performance."""
        return self.monitor_function(f"api_{endpoint}")

    def monitor_service_call(self, service_name: str):
        """Decorator to monitor service call performance."""
        return self.monitor_function(f"service_{service_name}")

    def monitor_database_query(self, query_type: str):
        """Decorator to monitor database query performance."""
        return self.monitor_function(f"db_{query_type}")


class MetricsExporter:
    """Metrics export functionality."""

    def __init__(self, collector: MetricsCollector):
        self.collector = collector

    def export_prometheus_format(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []

        # Export counters
        for key, value in self.collector.counters.items():
            if ":" in key:
                name, labels = key.split(":", 1)
                lines.append(f"{name}{{{labels}}} {value}")
            else:
                lines.append(f"{key} {value}")

        # Export gauges
        for key, value in self.collector.gauges.items():
            if ":" in key:
                name, labels = key.split(":", 1)
                lines.append(f"{name}{{{labels}}} {value}")
            else:
                lines.append(f"{key} {value}")

        # Export histogram summaries
        for key, stats in self.collector.get_metrics_summary()["histograms"].items():
            if ":" in key:
                name, labels = key.split(":", 1)
                for stat_name, stat_value in stats.items():
                    lines.append(f"{name}_{stat_name}{{{labels}}} {stat_value}")
            else:
                for stat_name, stat_value in stats.items():
                    lines.append(f"{key}_{stat_name} {stat_value}")

        return "\n".join(lines)

    def export_json_format(self) -> str:
        """Export metrics in JSON format."""
        return json.dumps(self.collector.get_metrics_summary(), indent=2)

    def export_health_check_format(self) -> Dict[str, Any]:
        """Export metrics for health check format."""
        summary = self.collector.get_metrics_summary()

        # Calculate health indicators
        error_rates = {}
        for key in self.collector.counters.keys():
            if key.endswith("_errors"):
                base_key = key[:-7]  # Remove "_errors"
                total_calls = self.collector.counters.get(f"{base_key}_calls", 0)
                errors = self.collector.counters.get(key, 0)
                if total_calls > 0:
                    error_rates[base_key] = errors / total_calls

        return {
            "status": (
                "healthy"
                if not any(rate > 0.1 for rate in error_rates.values())
                else "degraded"
            ),
            "timestamp": summary["timestamp"],
            "metrics": summary,
            "error_rates": error_rates,
        }


# Global metrics collector instance
metrics_collector = MetricsCollector()
performance_monitor = PerformanceMonitor(metrics_collector)
metrics_exporter = MetricsExporter(metrics_collector)


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance."""
    return metrics_collector


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    return performance_monitor


def get_metrics_exporter() -> MetricsExporter:
    """Get global metrics exporter instance."""
    return metrics_exporter


# Convenience functions for common metrics
def record_api_request(endpoint: str, method: str, status_code: int, duration: float):
    """Record API request metrics."""
    collector = get_metrics_collector()
    collector.increment_counter(
        "api_requests_total",
        labels={"endpoint": endpoint, "method": method, "status": str(status_code)},
    )
    collector.record_histogram(
        "api_request_duration",
        duration,
        labels={"endpoint": endpoint, "method": method},
    )


def record_service_call(service_name: str, method: str, duration: float, success: bool):
    """Record service call metrics."""
    collector = get_metrics_collector()
    collector.increment_counter(
        "service_calls_total",
        labels={"service": service_name, "method": method, "success": str(success)},
    )
    collector.record_histogram(
        "service_call_duration",
        duration,
        labels={"service": service_name, "method": method},
    )


def record_database_query(query_type: str, duration: float, success: bool):
    """Record database query metrics."""
    collector = get_metrics_collector()
    collector.increment_counter(
        "database_queries_total", labels={"type": query_type, "success": str(success)}
    )
    collector.record_histogram(
        "database_query_duration", duration, labels={"type": query_type}
    )


def record_error(error_type: str, error_message: str):
    """Record error metrics."""
    collector = get_metrics_collector()
    collector.increment_counter("errors_total", labels={"type": error_type})
    collector.increment_counter(
        "errors_by_message", labels={"message": error_message[:100]}
    )  # Truncate long messages


def record_memory_usage(usage_mb: float):
    """Record memory usage metrics."""
    collector = get_metrics_collector()
    collector.set_gauge("memory_usage_mb", usage_mb)


def record_cpu_usage(usage_percent: float):
    """Record CPU usage metrics."""
    collector = get_metrics_collector()
    collector.set_gauge("cpu_usage_percent", usage_percent)


def record_active_connections(count: int):
    """Record active connections metric."""
    collector = get_metrics_collector()
    collector.set_gauge("active_connections", count)


def record_queue_size(queue_name: str, size: int):
    """Record queue size metrics."""
    collector = get_metrics_collector()
    collector.set_gauge("queue_size", size, labels={"queue": queue_name})


def record_cache_hit_rate(cache_name: str, hit_rate: float):
    """Record cache hit rate metrics."""
    collector = get_metrics_collector()
    collector.set_gauge("cache_hit_rate", hit_rate, labels={"cache": cache_name})
