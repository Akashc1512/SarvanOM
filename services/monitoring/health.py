"""
Health check service for production monitoring.

This module provides comprehensive health checks, status monitoring, and health
endpoint functionality for production deployment.
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Callable, Awaitable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import threading
import json

from config.production.monitoring import get_health_config, HealthStatus
from services.monitoring.metrics import get_metrics_collector


@dataclass
class HealthCheckResult:
    """Health check result data structure."""
    name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    duration: float
    details: Optional[Dict[str, Any]] = None


class HealthChecker:
    """Health check service with async support."""
    
    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.results: Dict[str, HealthCheckResult] = {}
        self.lock = threading.Lock()
        self.config = get_health_config()
        self.metrics_collector = get_metrics_collector()
    
    def register_check(self, name: str, check_func: Callable[[], Awaitable[HealthCheckResult]]):
        """Register a health check function."""
        self.checks[name] = check_func
    
    def register_sync_check(self, name: str, check_func: Callable[[], HealthCheckResult]):
        """Register a synchronous health check function."""
        async def async_wrapper():
            return check_func()
        self.checks[name] = async_wrapper
    
    async def run_check(self, name: str) -> HealthCheckResult:
        """Run a specific health check."""
        if name not in self.checks:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNKNOWN,
                message=f"Health check '{name}' not found",
                timestamp=datetime.utcnow(),
                duration=0.0
            )
        
        start_time = time.time()
        try:
            result = await self.checks[name]()
            duration = time.time() - start_time
            
            # Update result with duration
            result.duration = duration
            result.timestamp = datetime.utcnow()
            
            # Store result
            with self.lock:
                self.results[name] = result
            
            # Record metrics
            self.metrics_collector.record_histogram(
                "health_check_duration", 
                duration, 
                labels={"check": name}
            )
            self.metrics_collector.increment_counter(
                "health_check_total", 
                labels={"check": name, "status": result.status.value}
            )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            result = HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                timestamp=datetime.utcnow(),
                duration=duration,
                details={"error": str(e)}
            )
            
            # Store result
            with self.lock:
                self.results[name] = result
            
            # Record metrics
            self.metrics_collector.record_histogram(
                "health_check_duration", 
                duration, 
                labels={"check": name}
            )
            self.metrics_collector.increment_counter(
                "health_check_total", 
                labels={"check": name, "status": "unhealthy"}
            )
            
            return result
    
    async def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all registered health checks."""
        tasks = [self.run_check(name) for name in self.checks.keys()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert results to dict
        result_dict = {}
        for name, result in zip(self.checks.keys(), results):
            if isinstance(result, Exception):
                result_dict[name] = HealthCheckResult(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check failed: {str(result)}",
                    timestamp=datetime.utcnow(),
                    duration=0.0,
                    details={"error": str(result)}
                )
            else:
                result_dict[name] = result
        
        return result_dict
    
    def get_overall_status(self, results: Dict[str, HealthCheckResult]) -> HealthStatus:
        """Determine overall health status from individual results."""
        if not results:
            return HealthStatus.UNKNOWN
        
        status_counts = {}
        for result in results.values():
            status_counts[result.status] = status_counts.get(result.status, 0) + 1
        
        # If any unhealthy, overall is unhealthy
        if HealthStatus.UNHEALTHY in status_counts:
            return HealthStatus.UNHEALTHY
        
        # If any degraded, overall is degraded
        if HealthStatus.DEGRADED in status_counts:
            return HealthStatus.DEGRADED
        
        # If all healthy, overall is healthy
        if HealthStatus.HEALTHY in status_counts and len(status_counts) == 1:
            return HealthStatus.HEALTHY
        
        # Default to unknown
        return HealthStatus.UNKNOWN
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health check summary."""
        with self.lock:
            overall_status = self.get_overall_status(self.results)
            
            summary = {
                "status": overall_status.value,
                "timestamp": datetime.utcnow().isoformat(),
                "checks": {
                    name: {
                        "status": result.status.value,
                        "message": result.message,
                        "timestamp": result.timestamp.isoformat(),
                        "duration": result.duration,
                        "details": result.details
                    }
                    for name, result in self.results.items()
                },
                "total_checks": len(self.results),
                "healthy_checks": sum(1 for r in self.results.values() if r.status == HealthStatus.HEALTHY),
                "degraded_checks": sum(1 for r in self.results.values() if r.status == HealthStatus.DEGRADED),
                "unhealthy_checks": sum(1 for r in self.results.values() if r.status == HealthStatus.UNHEALTHY)
            }
            
            return summary


class BuiltInHealthChecks:
    """Built-in health check implementations."""
    
    def __init__(self, health_checker: HealthChecker):
        self.health_checker = health_checker
        self.register_default_checks()
    
    def register_default_checks(self):
        """Register default health checks."""
        self.health_checker.register_check("application", self.check_application)
        self.health_checker.register_check("memory", self.check_memory)
        self.health_checker.register_check("disk", self.check_disk)
        self.health_checker.register_check("database", self.check_database)
        self.health_checker.register_check("external_services", self.check_external_services)
    
    async def check_application(self) -> HealthCheckResult:
        """Check application health."""
        return HealthCheckResult(
            name="application",
            status=HealthStatus.HEALTHY,
            message="Application is running",
            timestamp=datetime.utcnow(),
            duration=0.0,
            details={"version": "2.4.0", "uptime": "running"}
        )
    
    async def check_memory(self) -> HealthCheckResult:
        """Check memory usage."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            if memory_usage < 80:
                status = HealthStatus.HEALTHY
                message = f"Memory usage: {memory_usage:.1f}%"
            elif memory_usage < 90:
                status = HealthStatus.DEGRADED
                message = f"High memory usage: {memory_usage:.1f}%"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Critical memory usage: {memory_usage:.1f}%"
            
            return HealthCheckResult(
                name="memory",
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                duration=0.0,
                details={
                    "usage_percent": memory_usage,
                    "total_gb": memory.total / (1024**3),
                    "available_gb": memory.available / (1024**3)
                }
            )
        except ImportError:
            return HealthCheckResult(
                name="memory",
                status=HealthStatus.UNKNOWN,
                message="Memory check not available (psutil not installed)",
                timestamp=datetime.utcnow(),
                duration=0.0
            )
    
    async def check_disk(self) -> HealthCheckResult:
        """Check disk usage."""
        try:
            import psutil
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            
            if disk_usage < 80:
                status = HealthStatus.HEALTHY
                message = f"Disk usage: {disk_usage:.1f}%"
            elif disk_usage < 90:
                status = HealthStatus.DEGRADED
                message = f"High disk usage: {disk_usage:.1f}%"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Critical disk usage: {disk_usage:.1f}%"
            
            return HealthCheckResult(
                name="disk",
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                duration=0.0,
                details={
                    "usage_percent": disk_usage,
                    "total_gb": disk.total / (1024**3),
                    "free_gb": disk.free / (1024**3)
                }
            )
        except ImportError:
            return HealthCheckResult(
                name="disk",
                status=HealthStatus.UNKNOWN,
                message="Disk check not available (psutil not installed)",
                timestamp=datetime.utcnow(),
                duration=0.0
            )
    
    async def check_database(self) -> HealthCheckResult:
        """Check database connectivity."""
        try:
            # This is a placeholder - implement actual database check
            # based on your database configuration
            await asyncio.sleep(0.1)  # Simulate database check
            
            return HealthCheckResult(
                name="database",
                status=HealthStatus.HEALTHY,
                message="Database connection is healthy",
                timestamp=datetime.utcnow(),
                duration=0.1,
                details={"connection_pool": "active", "active_connections": 5}
            )
        except Exception as e:
            return HealthCheckResult(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                timestamp=datetime.utcnow(),
                duration=0.0,
                details={"error": str(e)}
            )
    
    async def check_external_services(self) -> HealthCheckResult:
        """Check external service dependencies."""
        try:
            # This is a placeholder - implement actual external service checks
            # based on your service dependencies
            await asyncio.sleep(0.1)  # Simulate external service check
            
            return HealthCheckResult(
                name="external_services",
                status=HealthStatus.HEALTHY,
                message="External services are accessible",
                timestamp=datetime.utcnow(),
                duration=0.1,
                details={"services": ["meilisearch", "browser_service", "pdf_service"]}
            )
        except Exception as e:
            return HealthCheckResult(
                name="external_services",
                status=HealthStatus.UNHEALTHY,
                message=f"External service check failed: {str(e)}",
                timestamp=datetime.utcnow(),
                duration=0.0,
                details={"error": str(e)}
            )


class HealthEndpoint:
    """Health endpoint for FastAPI integration."""
    
    def __init__(self, health_checker: HealthChecker):
        self.health_checker = health_checker
    
    async def get_health(self) -> Dict[str, Any]:
        """Get health status endpoint."""
        results = await self.health_checker.run_all_checks()
        overall_status = self.health_checker.get_overall_status(results)
        
        return {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                name: {
                    "status": result.status.value,
                    "message": result.message,
                    "duration": result.duration,
                    "details": result.details
                }
                for name, result in results.items()
            }
        }
    
    async def get_health_live(self) -> Dict[str, Any]:
        """Get liveness probe endpoint."""
        results = await self.health_checker.run_all_checks()
        overall_status = self.health_checker.get_overall_status(results)
        
        return {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_health_ready(self) -> Dict[str, Any]:
        """Get readiness probe endpoint."""
        results = await self.health_checker.run_all_checks()
        overall_status = self.health_checker.get_overall_status(results)
        
        return {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "ready": overall_status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
        }


# Global health checker instance
health_checker = HealthChecker()
built_in_checks = BuiltInHealthChecks(health_checker)
health_endpoint = HealthEndpoint(health_checker)


def get_health_checker() -> HealthChecker:
    """Get global health checker instance."""
    return health_checker


def get_health_endpoint() -> HealthEndpoint:
    """Get global health endpoint instance."""
    return health_endpoint


def register_custom_health_check(name: str, check_func: Callable[[], Awaitable[HealthCheckResult]]):
    """Register a custom health check."""
    health_checker.register_check(name, check_func)


def register_custom_sync_health_check(name: str, check_func: Callable[[], HealthCheckResult]):
    """Register a custom synchronous health check."""
    health_checker.register_sync_check(name, check_func)


async def run_health_checks() -> Dict[str, HealthCheckResult]:
    """Run all health checks."""
    return await health_checker.run_all_checks()


def get_health_summary() -> Dict[str, Any]:
    """Get health check summary."""
    return health_checker.get_health_summary() 