"""
Monitoring Middleware

This module contains middleware for application monitoring, metrics collection,
and performance tracking.
"""

import logging
import time
import psutil
import gc
from typing import Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ...services.core.metrics_service import MetricsService

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Performance monitoring middleware.

    Tracks request performance, system resources, and application metrics.
    """

    def __init__(self, app, metrics_service: Optional[MetricsService] = None):
        super().__init__(app)
        self.metrics_service = metrics_service
        self.request_counts = defaultdict(int)
        self.response_times = defaultdict(list)
        self.error_rates = defaultdict(int)
        self.last_gc_time = time.time()
        self.gc_interval = 300  # 5 minutes

    async def dispatch(self, request: Request, call_next):
        """Monitor request performance."""
        start_time = time.time()
        start_memory = self._get_memory_usage()

        # Track request start
        request_key = f"{request.method}:{request.url.path}"
        self.request_counts[request_key] += 1

        try:
            # Process request
            response = await call_next(request)

            # Calculate metrics
            processing_time = time.time() - start_time
            end_memory = self._get_memory_usage()
            memory_delta = end_memory - start_memory

            # Track response time
            self.response_times[request_key].append(processing_time)

            # Keep only last 100 response times per endpoint
            if len(self.response_times[request_key]) > 100:
                self.response_times[request_key] = self.response_times[request_key][
                    -100:
                ]

            # Add performance headers
            response.headers["X-Processing-Time"] = str(round(processing_time, 3))
            response.headers["X-Memory-Delta"] = str(round(memory_delta, 2))

            # Track metrics
            if self.metrics_service:
                await self.metrics_service.track_performance_metrics(
                    {
                        "endpoint": request_key,
                        "processing_time": processing_time,
                        "memory_usage": end_memory,
                        "memory_delta": memory_delta,
                        "status_code": response.status_code,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            # Periodic garbage collection
            await self._maybe_run_gc()

            return response

        except Exception as e:
            # Track error
            processing_time = time.time() - start_time
            self.error_rates[request_key] += 1

            # Track error metrics
            if self.metrics_service:
                await self.metrics_service.track_error_metrics(
                    {
                        "endpoint": request_key,
                        "error_type": type(e).__name__,
                        "processing_time": processing_time,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            raise

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0

    async def _maybe_run_gc(self):
        """Run garbage collection if needed."""
        current_time = time.time()
        if current_time - self.last_gc_time > self.gc_interval:
            collected = gc.collect()
            self.last_gc_time = current_time

            if collected > 0:
                logger.debug(f"Garbage collection freed {collected} objects")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics summary."""

        endpoint_stats = {}
        for endpoint, times in self.response_times.items():
            if times:
                endpoint_stats[endpoint] = {
                    "request_count": self.request_counts[endpoint],
                    "error_count": self.error_rates[endpoint],
                    "avg_response_time": sum(times) / len(times),
                    "min_response_time": min(times),
                    "max_response_time": max(times),
                    "error_rate": self.error_rates[endpoint]
                    / max(self.request_counts[endpoint], 1),
                }

        return {
            "endpoint_stats": endpoint_stats,
            "total_requests": sum(self.request_counts.values()),
            "total_errors": sum(self.error_rates.values()),
            "overall_error_rate": sum(self.error_rates.values())
            / max(sum(self.request_counts.values()), 1),
            "memory_usage_mb": self._get_memory_usage(),
            "timestamp": datetime.now().isoformat(),
        }


class HealthCheckMiddleware(BaseHTTPMiddleware):
    """
    Health check middleware.

    Monitors application health and provides health status endpoints.
    """

    def __init__(self, app):
        super().__init__(app)
        self.start_time = time.time()
        self.health_checks = {}
        self.last_health_check = None

    async def dispatch(self, request: Request, call_next):
        """Monitor application health."""

        # Skip health monitoring for health check endpoints
        if request.url.path.startswith("/health"):
            response = await call_next(request)

            # Add health headers
            uptime = time.time() - self.start_time
            response.headers["X-Uptime-Seconds"] = str(int(uptime))
            response.headers["X-Health-Status"] = await self._get_health_status()

            return response

        # Normal request processing
        try:
            response = await call_next(request)

            # Update health status based on response
            self._update_health_status(
                "api", "healthy" if response.status_code < 500 else "unhealthy"
            )

            return response

        except Exception as e:
            # Update health status on error
            self._update_health_status("api", "unhealthy")
            raise

    def _update_health_status(self, component: str, status: str):
        """Update health status for a component."""
        self.health_checks[component] = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
        }
        self.last_health_check = datetime.now()

    async def _get_health_status(self) -> str:
        """Get overall health status."""
        if not self.health_checks:
            return "unknown"

        unhealthy_components = [
            comp
            for comp, data in self.health_checks.items()
            if data["status"] != "healthy"
        ]

        if unhealthy_components:
            return "unhealthy"

        return "healthy"

    def get_health_report(self) -> Dict[str, Any]:
        """Get detailed health report."""
        uptime = time.time() - self.start_time

        return {
            "status": self._get_health_status(),
            "uptime_seconds": int(uptime),
            "uptime_human": self._format_uptime(uptime),
            "components": dict(self.health_checks),
            "last_check": (
                self.last_health_check.isoformat() if self.last_health_check else None
            ),
            "memory_usage_mb": self._get_memory_usage(),
            "cpu_usage_percent": self._get_cpu_usage(),
            "timestamp": datetime.now().isoformat(),
        }

    def _format_uptime(self, uptime_seconds: float) -> str:
        """Format uptime in human readable format."""
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)

        if days > 0:
            return f"{days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0

    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            return psutil.cpu_percent(interval=None)
        except Exception:
            return 0.0


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware.

    Implements basic rate limiting to prevent abuse.
    """

    def __init__(
        self,
        app,
        max_requests: int = 100,
        time_window: int = 60,
        exclude_paths: list = None,
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.time_window = time_window
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/docs", "/redoc"]
        self.request_history = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        """Apply rate limiting."""

        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Get client identifier
        client_id = self._get_client_identifier(request)
        current_time = time.time()

        # Clean old requests
        self._clean_old_requests(client_id, current_time)

        # Check rate limit
        request_count = len(self.request_history[client_id])

        if request_count >= self.max_requests:
            # Rate limit exceeded
            logger.warning(
                f"Rate limit exceeded for client {client_id}: {request_count} requests in {self.time_window}s"
            )

            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.max_requests} requests per {self.time_window} seconds",
                    "retry_after": self.time_window,
                    "timestamp": datetime.now().isoformat(),
                },
                headers={
                    "Retry-After": str(self.time_window),
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(current_time + self.time_window)),
                },
            )

        # Add request to history
        self.request_history[client_id].append(current_time)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = max(0, self.max_requests - len(self.request_history[client_id]))
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            int(current_time + self.time_window)
        )

        return response

    def _get_client_identifier(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Try to get user ID from request state
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"

        # Fall back to IP address
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"

        if request.client:
            return f"ip:{request.client.host}"

        return "unknown"

    def _clean_old_requests(self, client_id: str, current_time: float):
        """Remove old requests outside the time window."""
        cutoff_time = current_time - self.time_window
        self.request_history[client_id] = [
            req_time
            for req_time in self.request_history[client_id]
            if req_time > cutoff_time
        ]

    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics."""
        current_time = time.time()

        active_clients = {}
        for client_id, requests in self.request_history.items():
            # Clean old requests
            cutoff_time = current_time - self.time_window
            active_requests = [req for req in requests if req > cutoff_time]

            if active_requests:
                active_clients[client_id] = {
                    "request_count": len(active_requests),
                    "remaining": max(0, self.max_requests - len(active_requests)),
                    "oldest_request": min(active_requests),
                    "newest_request": max(active_requests),
                }

        return {
            "max_requests": self.max_requests,
            "time_window": self.time_window,
            "active_clients": len(active_clients),
            "clients": active_clients,
            "timestamp": datetime.now().isoformat(),
        }
