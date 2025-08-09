"""
Production monitoring configuration for the Universal Knowledge Platform.

This module provides monitoring configuration for production deployment
including metrics collection, health checks, and alerting setup.
"""

import time
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from config.production.settings import get_monitoring_config


class HealthStatus(Enum):
    """Health status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Health check configuration."""

    name: str
    check_function: callable
    interval: int = 30
    timeout: int = 10
    critical: bool = False
    last_check: Optional[datetime] = None
    last_status: HealthStatus = HealthStatus.UNKNOWN
    last_error: Optional[str] = None


@dataclass
class Metric:
    """Metric configuration."""

    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, Any] = field(default_factory=dict)


class MonitoringConfig:
    """Monitoring configuration manager."""

    def __init__(self):
        self.config = get_monitoring_config()
        self.metrics_enabled = self.config.get("metrics_enabled", True)
        self.metrics_port = self.config.get("metrics_port", 9090)
        self.health_check_interval = self.config.get("health_check_interval", 30)

        # Health checks registry
        self.health_checks: List[HealthCheck] = []

        # Metrics registry
        self.metrics: Dict[str, Metric] = {}

        # Performance tracking
        self.performance_metrics: Dict[str, List[float]] = {}

    def add_health_check(
        self,
        name: str,
        check_function: callable,
        interval: int = 30,
        timeout: int = 10,
        critical: bool = False,
    ):
        """Add a health check."""
        health_check = HealthCheck(
            name=name,
            check_function=check_function,
            interval=interval,
            timeout=timeout,
            critical=critical,
        )
        self.health_checks.append(health_check)

    def register_metric(
        self, name: str, value: float, unit: str, tags: Optional[Dict[str, Any]] = None
    ):
        """Register a metric."""
        if not self.metrics_enabled:
            return

        metric = Metric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.utcnow(),
            tags=tags or {},
        )
        self.metrics[name] = metric

    def track_performance(self, operation: str, duration: float):
        """Track performance metric."""
        if operation not in self.performance_metrics:
            self.performance_metrics[operation] = []

        self.performance_metrics[operation].append(duration)

        # Keep only last 1000 measurements
        if len(self.performance_metrics[operation]) > 1000:
            self.performance_metrics[operation] = self.performance_metrics[operation][
                -1000:
            ]

        # Register metric
        self.register_metric(
            name=f"{operation}_duration",
            value=duration,
            unit="seconds",
            tags={"operation": operation},
        )

    def get_performance_stats(self, operation: str) -> Dict[str, float]:
        """Get performance statistics for an operation."""
        if operation not in self.performance_metrics:
            return {}

        values = self.performance_metrics[operation]
        if not values:
            return {}

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "p95": sorted(values)[int(len(values) * 0.95)],
            "p99": sorted(values)[int(len(values) * 0.99)],
        }

    async def run_health_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = {}

        for health_check in self.health_checks:
            try:
                # Check if it's time to run this health check
                if (
                    health_check.last_check is None
                    or datetime.utcnow() - health_check.last_check
                    > timedelta(seconds=health_check.interval)
                ):

                    # Run health check with timeout
                    start_time = time.time()
                    result = await asyncio.wait_for(
                        health_check.check_function(), timeout=health_check.timeout
                    )
                    duration = time.time() - start_time

                    health_check.last_check = datetime.utcnow()
                    health_check.last_status = HealthStatus.HEALTHY
                    health_check.last_error = None

                    results[health_check.name] = {
                        "status": "healthy",
                        "duration": duration,
                        "timestamp": health_check.last_check.isoformat(),
                    }

                    # Track performance
                    self.track_performance(
                        f"health_check_{health_check.name}", duration
                    )

            except asyncio.TimeoutError:
                health_check.last_status = HealthStatus.UNHEALTHY
                health_check.last_error = "Timeout"
                results[health_check.name] = {
                    "status": "unhealthy",
                    "error": "Timeout",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                health_check.last_status = HealthStatus.UNHEALTHY
                health_check.last_error = str(e)
                results[health_check.name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

        return results

    def get_overall_health(self) -> HealthStatus:
        """Get overall health status."""
        if not self.health_checks:
            return HealthStatus.UNKNOWN

        critical_checks = [check for check in self.health_checks if check.critical]
        if critical_checks:
            # If any critical check is unhealthy, overall is unhealthy
            for check in critical_checks:
                if check.last_status == HealthStatus.UNHEALTHY:
                    return HealthStatus.UNHEALTHY

        # Check if any checks are degraded
        for check in self.health_checks:
            if check.last_status == HealthStatus.DEGRADED:
                return HealthStatus.DEGRADED

        # If all checks are healthy, overall is healthy
        all_healthy = all(
            check.last_status == HealthStatus.HEALTHY for check in self.health_checks
        )
        return HealthStatus.HEALTHY if all_healthy else HealthStatus.UNKNOWN

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        if not self.metrics_enabled:
            return {"enabled": False}

        return {
            "enabled": True,
            "total_metrics": len(self.metrics),
            "recent_metrics": [
                {
                    "name": metric.name,
                    "value": metric.value,
                    "unit": metric.unit,
                    "timestamp": metric.timestamp.isoformat(),
                    "tags": metric.tags,
                }
                for metric in self.metrics.values()
                if datetime.utcnow() - metric.timestamp < timedelta(hours=1)
            ],
        }

    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return {
            "metrics_enabled": self.metrics_enabled,
            "metrics_port": self.metrics_port,
            "health_check_interval": self.health_check_interval,
            "health_checks_count": len(self.health_checks),
            "overall_health": self.get_overall_health().value,
        }


# Global monitoring instance
monitoring_config = MonitoringConfig()


def get_monitoring() -> MonitoringConfig:
    """Get monitoring configuration instance."""
    return monitoring_config


# Health check functions
async def check_database_health() -> bool:
    """Check database health."""
    # This would be implemented to check database connectivity
    # For now, return True as placeholder
    return True


async def check_redis_health() -> bool:
    """Check Redis health."""
    # This would be implemented to check Redis connectivity
    # For now, return True as placeholder
    return True


async def check_external_apis_health() -> bool:
    """Check external APIs health."""
    # This would be implemented to check external API connectivity
    # For now, return True as placeholder
    return True


async def check_disk_space() -> bool:
    """Check disk space."""
    # This would be implemented to check available disk space
    # For now, return True as placeholder
    return True


async def check_memory_usage() -> bool:
    """Check memory usage."""
    # This would be implemented to check memory usage
    # For now, return True as placeholder
    return True


def setup_monitoring():
    """Setup monitoring configuration."""
    monitoring = get_monitoring()

    # Add default health checks
    monitoring.add_health_check("database", check_database_health, critical=True)
    monitoring.add_health_check("redis", check_redis_health, critical=True)
    monitoring.add_health_check("external_apis", check_external_apis_health)
    monitoring.add_health_check("disk_space", check_disk_space)
    monitoring.add_health_check("memory_usage", check_memory_usage)

    return monitoring


def track_request_metrics(
    request_id: str, method: str, path: str, status_code: int, duration: float
):
    """Track request metrics."""
    monitoring = get_monitoring()

    # Track request duration
    monitoring.track_performance("request", duration)

    # Register request metric
    monitoring.register_metric(
        name="http_requests_total",
        value=1,
        unit="count",
        tags={
            "method": method,
            "path": path,
            "status_code": status_code,
            "request_id": request_id,
        },
    )


def track_service_metrics(
    service_name: str, method: str, duration: float, success: bool
):
    """Track service metrics."""
    monitoring = get_monitoring()

    # Track service call duration
    monitoring.track_performance(f"service_{service_name}_{method}", duration)

    # Register service metric
    monitoring.register_metric(
        name="service_calls_total",
        value=1,
        unit="count",
        tags={"service": service_name, "method": method, "success": success},
    )


def track_error_metrics(error_type: str, error_message: str):
    """Track error metrics."""
    monitoring = get_monitoring()

    # Register error metric
    monitoring.register_metric(
        name="errors_total",
        value=1,
        unit="count",
        tags={"error_type": error_type, "error_message": error_message},
    )


def get_health_status() -> Dict[str, Any]:
    """Get comprehensive health status."""
    monitoring = get_monitoring()

    return {
        "overall_status": monitoring.get_overall_health().value,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.4.0",
        "environment": "production",
        "health_checks": {
            check.name: {
                "status": check.last_status.value,
                "last_check": (
                    check.last_check.isoformat() if check.last_check else None
                ),
                "last_error": check.last_error,
                "critical": check.critical,
            }
            for check in monitoring.health_checks
        },
        "performance": {
            operation: monitoring.get_performance_stats(operation)
            for operation in monitoring.performance_metrics.keys()
        },
    }
