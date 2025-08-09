"""
Production Logging Configuration - Advanced Features

This module extends the unified logging system with production-specific features:
- Log aggregation and shipping
- Performance metrics collection  
- Automated log analysis
- Integration with monitoring systems
- Health check logging
- Security event logging

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import os
import json
import time
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from collections import deque, defaultdict
import threading

from .unified_logging import get_logger, setup_logging


@dataclass
class LogMetrics:
    """Metrics collected from logs for monitoring."""

    total_requests: int = 0
    error_rate: float = 0.0
    avg_response_time: float = 0.0
    peak_response_time: float = 0.0
    queries_processed: int = 0
    agents_executed: int = 0
    cache_hit_rate: float = 0.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ProductionLogCollector:
    """
    Advanced log collector for production environments.

    Collects metrics, analyzes patterns, and provides aggregated insights
    for monitoring and alerting systems.
    """

    def __init__(self, buffer_size: int = 10000):
        self.buffer_size = buffer_size
        self.log_buffer = deque(maxlen=buffer_size)
        self.metrics = LogMetrics()
        self.error_patterns = defaultdict(int)
        self.performance_data = deque(maxlen=1000)
        self.lock = threading.Lock()
        self.logger = get_logger(__name__)

        # Start background processing
        self._start_background_processing()

    def collect_log_entry(self, level: str, message: str, **context):
        """Collect a log entry for analysis."""
        timestamp = datetime.now(timezone.utc)

        entry = {
            "timestamp": timestamp.isoformat(),
            "level": level,
            "message": message,
            "context": context,
        }

        with self.lock:
            self.log_buffer.append(entry)
            self._update_metrics(entry)

    def _update_metrics(self, entry: Dict[str, Any]):
        """Update metrics based on log entry."""
        level = entry.get("level", "")
        context = entry.get("context", {})

        # Count requests
        if "request_id" in context:
            self.metrics.total_requests += 1

        # Track query processing
        if "query_id" in context:
            self.metrics.queries_processed += 1

        # Track agent execution
        if "agent_name" in context:
            self.metrics.agents_executed += 1

        # Track response times
        if "duration_ms" in context:
            duration = float(context["duration_ms"])
            self.performance_data.append(duration)

            if len(self.performance_data) > 0:
                self.metrics.avg_response_time = sum(self.performance_data) / len(
                    self.performance_data
                )
                self.metrics.peak_response_time = max(self.performance_data)

        # Track errors
        if level in ["ERROR", "CRITICAL"]:
            error_type = context.get("error_type", "unknown")
            self.error_patterns[error_type] += 1

            # Calculate error rate
            total_logs = len(self.log_buffer)
            error_logs = sum(
                1
                for log in self.log_buffer
                if log.get("level") in ["ERROR", "CRITICAL"]
            )
            self.metrics.error_rate = (
                (error_logs / total_logs) * 100 if total_logs > 0 else 0.0
            )

        # Track cache performance
        if "cache_hit" in context:
            cache_entries = [
                log for log in self.log_buffer if "cache_hit" in log.get("context", {})
            ]
            if cache_entries:
                hits = sum(1 for log in cache_entries if log["context"]["cache_hit"])
                self.metrics.cache_hit_rate = (hits / len(cache_entries)) * 100

        self.metrics.last_updated = datetime.now(timezone.utc)

    def get_metrics(self) -> LogMetrics:
        """Get current metrics."""
        with self.lock:
            return self.metrics

    def get_error_patterns(self) -> Dict[str, int]:
        """Get error patterns for analysis."""
        with self.lock:
            return dict(self.error_patterns)

    def get_recent_logs(self, minutes: int = 5) -> List[Dict[str, Any]]:
        """Get recent logs within specified time window."""
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)

        with self.lock:
            recent = []
            for entry in reversed(self.log_buffer):
                entry_time = datetime.fromisoformat(
                    entry["timestamp"].replace("Z", "+00:00")
                )
                if entry_time >= cutoff:
                    recent.append(entry)
                else:
                    break
            return recent

    def _start_background_processing(self):
        """Start background processing for log analysis."""

        def process_logs():
            while True:
                try:
                    self._analyze_patterns()
                    self._generate_alerts()
                    time.sleep(60)  # Process every minute
                except Exception as e:
                    self.logger.error(
                        "Background log processing error",
                        error=str(e),
                        component="log_collector",
                    )

        thread = threading.Thread(target=process_logs, daemon=True)
        thread.start()

    def _analyze_patterns(self):
        """Analyze log patterns for insights."""
        recent_logs = self.get_recent_logs(minutes=5)

        if len(recent_logs) < 10:
            return

        # Analyze error clustering
        error_logs = [
            log for log in recent_logs if log.get("level") in ["ERROR", "CRITICAL"]
        ]
        if len(error_logs) > len(recent_logs) * 0.1:  # More than 10% errors
            self.logger.warning(
                "High error rate detected",
                error_count=len(error_logs),
                total_logs=len(recent_logs),
                error_rate=f"{(len(error_logs)/len(recent_logs))*100:.1f}%",
                component="log_analysis",
            )

        # Analyze performance degradation
        if len(self.performance_data) > 50:
            recent_avg = sum(list(self.performance_data)[-20:]) / 20
            overall_avg = sum(self.performance_data) / len(self.performance_data)

            if recent_avg > overall_avg * 1.5:  # 50% slower than average
                self.logger.warning(
                    "Performance degradation detected",
                    recent_avg_ms=round(recent_avg, 2),
                    overall_avg_ms=round(overall_avg, 2),
                    degradation_factor=round(recent_avg / overall_avg, 2),
                    component="performance_analysis",
                )

    def _generate_alerts(self):
        """Generate alerts based on log analysis."""
        metrics = self.get_metrics()

        # Error rate alert
        if metrics.error_rate > 5.0:  # More than 5% error rate
            self.logger.critical(
                "High error rate alert",
                error_rate=f"{metrics.error_rate:.1f}%",
                threshold="5.0%",
                alert_type="error_rate",
                component="alerting",
            )

        # Response time alert
        if metrics.avg_response_time > 5000:  # More than 5 seconds
            self.logger.critical(
                "High response time alert",
                avg_response_time_ms=round(metrics.avg_response_time, 2),
                threshold_ms=5000,
                alert_type="response_time",
                component="alerting",
            )

        # Cache performance alert
        if metrics.cache_hit_rate < 70.0:  # Less than 70% cache hit rate
            self.logger.warning(
                "Low cache hit rate",
                cache_hit_rate=f"{metrics.cache_hit_rate:.1f}%",
                threshold="70.0%",
                alert_type="cache_performance",
                component="alerting",
            )


class HealthCheckLogger:
    """Specialized logger for health check events."""

    def __init__(self):
        self.logger = get_logger("health_check")
        self.last_health_status = {}

    def log_health_check(
        self, service: str, status: str, details: Dict[str, Any] = None
    ):
        """Log health check result."""
        self.logger.info(
            "Health check completed",
            service=service,
            status=status,
            details=details or {},
            component="health_check",
        )

        # Alert on status changes
        if service in self.last_health_status:
            if self.last_health_status[service] != status:
                if status == "unhealthy":
                    self.logger.critical(
                        "Service health degraded",
                        service=service,
                        previous_status=self.last_health_status[service],
                        current_status=status,
                        alert_type="health_degradation",
                        component="health_alerting",
                    )
                elif status == "healthy":
                    self.logger.info(
                        "Service health recovered",
                        service=service,
                        previous_status=self.last_health_status[service],
                        current_status=status,
                        component="health_recovery",
                    )

        self.last_health_status[service] = status

    def log_dependency_check(
        self, dependency: str, available: bool, response_time_ms: float = None
    ):
        """Log dependency availability check."""
        self.logger.info(
            "Dependency check",
            dependency=dependency,
            available=available,
            response_time_ms=response_time_ms,
            component="dependency_check",
        )


class SecurityEventLogger:
    """Specialized logger for security events."""

    def __init__(self):
        self.logger = get_logger("security")
        self.failed_attempts = defaultdict(int)

    def log_authentication_attempt(
        self, user_id: str, success: bool, ip_address: str = None
    ):
        """Log authentication attempt."""
        if success:
            self.logger.info(
                "Authentication successful",
                user_id=user_id,
                ip_address=ip_address,
                component="authentication",
            )
            # Reset failed attempts on success
            if user_id in self.failed_attempts:
                del self.failed_attempts[user_id]
        else:
            self.failed_attempts[user_id] += 1
            self.logger.warning(
                "Authentication failed",
                user_id=user_id,
                ip_address=ip_address,
                attempt_count=self.failed_attempts[user_id],
                component="authentication",
            )

            # Alert on multiple failed attempts
            if self.failed_attempts[user_id] >= 5:
                self.logger.critical(
                    "Multiple authentication failures",
                    user_id=user_id,
                    ip_address=ip_address,
                    attempt_count=self.failed_attempts[user_id],
                    alert_type="brute_force",
                    component="security_alerting",
                )

    def log_authorization_failure(self, user_id: str, resource: str, action: str):
        """Log authorization failure."""
        self.logger.warning(
            "Authorization denied",
            user_id=user_id,
            resource=resource,
            action=action,
            component="authorization",
        )

    def log_suspicious_activity(self, activity_type: str, details: Dict[str, Any]):
        """Log suspicious activity."""
        self.logger.critical(
            "Suspicious activity detected",
            activity_type=activity_type,
            details=details,
            alert_type="suspicious_activity",
            component="security_monitoring",
        )


# Global instances
_log_collector = None
_health_logger = None
_security_logger = None


def get_production_log_collector() -> ProductionLogCollector:
    """Get global production log collector instance."""
    global _log_collector
    if _log_collector is None:
        _log_collector = ProductionLogCollector()
    return _log_collector


def get_health_check_logger() -> HealthCheckLogger:
    """Get global health check logger instance."""
    global _health_logger
    if _health_logger is None:
        _health_logger = HealthCheckLogger()
    return _health_logger


def get_security_event_logger() -> SecurityEventLogger:
    """Get global security event logger instance."""
    global _security_logger
    if _security_logger is None:
        _security_logger = SecurityEventLogger()
    return _security_logger


def setup_production_logging(service_name: str, enable_collection: bool = True):
    """
    Set up production logging with all advanced features.

    Args:
        service_name: Name of the service
        enable_collection: Whether to enable log collection and analysis
    """
    # Set up unified logging for production
    setup_logging(
        service_name=service_name,
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_format="json",
    )

    logger = get_logger(__name__)
    logger.info(
        "Production logging initialized",
        service_name=service_name,
        collection_enabled=enable_collection,
        component="production_logging",
    )

    if enable_collection:
        # Initialize collectors
        get_production_log_collector()
        get_health_check_logger()
        get_security_event_logger()

        logger.info(
            "Production log collectors initialized",
            collectors=["metrics", "health", "security"],
            component="production_logging",
        )


# Export main functions
__all__ = [
    "ProductionLogCollector",
    "HealthCheckLogger",
    "SecurityEventLogger",
    "LogMetrics",
    "get_production_log_collector",
    "get_health_check_logger",
    "get_security_event_logger",
    "setup_production_logging",
]
