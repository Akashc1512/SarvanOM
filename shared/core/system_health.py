"""
System Health and Monitoring Service for SarvanOM

This module provides comprehensive system health monitoring, diagnostics,
and automated recovery following MAANG/OpenAI/Perplexity standards.
"""

import asyncio
import time
import psutil
import os
import sys
from typing import Any, Dict, List, Optional, Callable, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import structlog
import threading
from concurrent.futures import ThreadPoolExecutor
import subprocess
import json

logger = structlog.get_logger(__name__)

class HealthStatus(str, Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class ComponentType(str, Enum):
    """System component types."""
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_API = "external_api"
    FILE_SYSTEM = "file_system"
    NETWORK = "network"
    MEMORY = "memory"
    CPU = "cpu"
    DISK = "disk"
    SERVICE = "service"

@dataclass
class HealthCheck:
    """Individual health check configuration."""
    name: str
    component_type: ComponentType
    check_function: Callable
    timeout_seconds: float = 30.0
    retry_count: int = 3
    retry_delay: float = 1.0
    critical: bool = False
    enabled: bool = True
    last_check: Optional[datetime] = None
    last_status: HealthStatus = HealthStatus.UNKNOWN
    last_error: Optional[str] = None
    consecutive_failures: int = 0

@dataclass
class HealthResult:
    """Result of a health check."""
    name: str
    component_type: ComponentType
    status: HealthStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    response_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error: Optional[str] = None

@dataclass
class SystemHealth:
    """Overall system health status."""
    overall_status: HealthStatus
    components: List[HealthResult]
    system_metrics: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    uptime_seconds: float = 0.0
    version: str = "1.0.0"

class SystemHealthMonitor:
    """Comprehensive system health monitoring."""
    
    def __init__(self):
        self.health_checks: Dict[str, HealthCheck] = {}
        self.health_history: List[SystemHealth] = []
        self.max_history_size = 1000
        self._lock = threading.Lock()
        self._monitoring_active = False
        self._monitor_task: Optional[asyncio.Task] = None
        self.start_time = time.time()
        
        # Health thresholds
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0,
            "response_time_ms": 5000.0,
            "error_rate_percent": 10.0
        }
        
        # Initialize default health checks
        self._setup_default_health_checks()
    
    def _setup_default_health_checks(self):
        """Setup default system health checks."""
        self.add_health_check(
            name="system_cpu",
            component_type=ComponentType.CPU,
            check_function=self._check_cpu_health,
            timeout_seconds=10.0
        )
        
        self.add_health_check(
            name="system_memory",
            component_type=ComponentType.MEMORY,
            check_function=self._check_memory_health,
            timeout_seconds=10.0
        )
        
        self.add_health_check(
            name="system_disk",
            component_type=ComponentType.DISK,
            check_function=self._check_disk_health,
            timeout_seconds=10.0
        )
        
        self.add_health_check(
            name="system_network",
            component_type=ComponentType.NETWORK,
            check_function=self._check_network_health,
            timeout_seconds=15.0
        )
        
        self.add_health_check(
            name="file_system",
            component_type=ComponentType.FILE_SYSTEM,
            check_function=self._check_file_system_health,
            timeout_seconds=10.0
        )
    
    def add_health_check(
        self,
        name: str,
        component_type: ComponentType,
        check_function: Callable,
        timeout_seconds: float = 30.0,
        retry_count: int = 3,
        retry_delay: float = 1.0,
        critical: bool = False,
        enabled: bool = True
    ):
        """Add a health check to the monitor."""
        health_check = HealthCheck(
            name=name,
            component_type=component_type,
            check_function=check_function,
            timeout_seconds=timeout_seconds,
            retry_count=retry_count,
            retry_delay=retry_delay,
            critical=critical,
            enabled=enabled
        )
        
        self.health_checks[name] = health_check
        logger.info("Health check added", name=name, component_type=component_type.value)
    
    def remove_health_check(self, name: str):
        """Remove a health check from the monitor."""
        if name in self.health_checks:
            del self.health_checks[name]
            logger.info("Health check removed", name=name)
    
    async def start_monitoring(self, interval_seconds: float = 60.0):
        """Start continuous health monitoring."""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitor_task = asyncio.create_task(
            self._monitor_health(interval_seconds)
        )
        logger.info("System health monitoring started", interval_seconds=interval_seconds)
    
    async def stop_monitoring(self):
        """Stop continuous health monitoring."""
        self._monitoring_active = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("System health monitoring stopped")
    
    async def _monitor_health(self, interval_seconds: float):
        """Monitor system health continuously."""
        while self._monitoring_active:
            try:
                health = await self.check_system_health()
                with self._lock:
                    self.health_history.append(health)
                    if len(self.health_history) > self.max_history_size:
                        self.health_history = self.health_history[-self.max_history_size:]
                
                # Log health status
                if health.overall_status == HealthStatus.CRITICAL:
                    logger.critical("System health critical", health=health)
                elif health.overall_status == HealthStatus.UNHEALTHY:
                    logger.error("System health unhealthy", health=health)
                elif health.overall_status == HealthStatus.DEGRADED:
                    logger.warning("System health degraded", health=health)
                else:
                    logger.info("System health check completed", status=health.overall_status.value)
                
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error("Error in health monitoring", error=str(e))
                await asyncio.sleep(interval_seconds)
    
    async def check_system_health(self) -> SystemHealth:
        """Perform comprehensive system health check."""
        start_time = time.time()
        components = []
        
        # Run all health checks in parallel
        tasks = []
        for name, health_check in self.health_checks.items():
            if health_check.enabled:
                task = asyncio.create_task(self._run_health_check(health_check))
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, HealthResult):
                    components.append(result)
                elif isinstance(result, Exception):
                    logger.error("Health check failed with exception", error=str(result))
        
        # Collect system metrics
        system_metrics = await self._collect_system_metrics()
        
        # Determine overall status
        overall_status = self._determine_overall_status(components)
        
        health = SystemHealth(
            overall_status=overall_status,
            components=components,
            system_metrics=system_metrics,
            uptime_seconds=time.time() - self.start_time,
            version=os.getenv("APP_VERSION", "1.0.0")
        )
        
        return health
    
    async def _run_health_check(self, health_check: HealthCheck) -> HealthResult:
        """Run a single health check with retries."""
        start_time = time.time()
        last_exception = None
        
        for attempt in range(health_check.retry_count + 1):
            try:
                # Run the health check with timeout
                result = await asyncio.wait_for(
                    health_check.check_function(),
                    timeout=health_check.timeout_seconds
                )
                
                # Update health check status
                health_check.last_check = datetime.now(timezone.utc)
                health_check.last_status = result.status
                health_check.last_error = None
                health_check.consecutive_failures = 0
                
                result.response_time_ms = (time.time() - start_time) * 1000
                return result
                
            except Exception as e:
                last_exception = e
                health_check.consecutive_failures += 1
                
                if attempt < health_check.retry_count:
                    await asyncio.sleep(health_check.retry_delay)
                else:
                    # All retries failed
                    health_check.last_check = datetime.now(timezone.utc)
                    health_check.last_status = HealthStatus.UNHEALTHY
                    health_check.last_error = str(e)
                    
                    return HealthResult(
                        name=health_check.name,
                        component_type=health_check.component_type,
                        status=HealthStatus.UNHEALTHY,
                        message=f"Health check failed after {health_check.retry_count + 1} attempts",
                        error=str(e),
                        response_time_ms=(time.time() - start_time) * 1000
                    )
        
        # This should never be reached, but just in case
        return HealthResult(
            name=health_check.name,
            component_type=health_check.component_type,
            status=HealthStatus.UNKNOWN,
            message="Health check failed unexpectedly",
            error=str(last_exception) if last_exception else "Unknown error"
        )
    
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network = psutil.net_io_counters()
            network_connections = len(psutil.net_connections())
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "frequency_mhz": cpu_freq.current if cpu_freq else None,
                    "process_percent": process_cpu
                },
                "memory": {
                    "total_gb": memory.total / (1024**3),
                    "available_gb": memory.available / (1024**3),
                    "used_gb": memory.used / (1024**3),
                    "percent": memory.percent,
                    "process_mb": process_memory.rss / (1024**2),
                    "swap_total_gb": swap.total / (1024**3),
                    "swap_used_gb": swap.used / (1024**3)
                },
                "disk": {
                    "total_gb": disk.total / (1024**3),
                    "used_gb": disk.used / (1024**3),
                    "free_gb": disk.free / (1024**3),
                    "percent": disk.percent,
                    "read_bytes": disk_io.read_bytes if disk_io else 0,
                    "write_bytes": disk_io.write_bytes if disk_io else 0
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv,
                    "connections": network_connections
                },
                "system": {
                    "uptime_seconds": time.time() - self.start_time,
                    "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None,
                    "python_version": sys.version,
                    "platform": sys.platform
                }
            }
        except Exception as e:
            logger.error("Error collecting system metrics", error=str(e))
            return {"error": str(e)}
    
    def _determine_overall_status(self, components: List[HealthResult]) -> HealthStatus:
        """Determine overall system health status."""
        if not components:
            return HealthStatus.UNKNOWN
        
        # Check for critical failures
        critical_failures = [
            c for c in components
            if c.status == HealthStatus.CRITICAL
        ]
        if critical_failures:
            return HealthStatus.CRITICAL
        
        # Check for unhealthy components
        unhealthy_components = [
            c for c in components
            if c.status == HealthStatus.UNHEALTHY
        ]
        if unhealthy_components:
            return HealthStatus.UNHEALTHY
        
        # Check for degraded components
        degraded_components = [
            c for c in components
            if c.status == HealthStatus.DEGRADED
        ]
        if degraded_components:
            return HealthStatus.DEGRADED
        
        # All components are healthy
        return HealthStatus.HEALTHY
    
    # Default health check implementations
    async def _check_cpu_health(self) -> HealthResult:
        """Check CPU health."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            
            if cpu_percent > 90:
                status = HealthStatus.CRITICAL
                message = f"CPU usage critically high: {cpu_percent:.1f}%"
            elif cpu_percent > 80:
                status = HealthStatus.UNHEALTHY
                message = f"CPU usage high: {cpu_percent:.1f}%"
            elif cpu_percent > 60:
                status = HealthStatus.DEGRADED
                message = f"CPU usage elevated: {cpu_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU usage normal: {cpu_percent:.1f}%"
            
            return HealthResult(
                name="system_cpu",
                component_type=ComponentType.CPU,
                status=status,
                message=message,
                details={"cpu_percent": cpu_percent}
            )
        except Exception as e:
            return HealthResult(
                name="system_cpu",
                component_type=ComponentType.CPU,
                status=HealthStatus.UNHEALTHY,
                message="CPU health check failed",
                error=str(e)
            )
    
    async def _check_memory_health(self) -> HealthResult:
        """Check memory health."""
        try:
            memory = psutil.virtual_memory()
            
            if memory.percent > 95:
                status = HealthStatus.CRITICAL
                message = f"Memory usage critically high: {memory.percent:.1f}%"
            elif memory.percent > 85:
                status = HealthStatus.UNHEALTHY
                message = f"Memory usage high: {memory.percent:.1f}%"
            elif memory.percent > 70:
                status = HealthStatus.DEGRADED
                message = f"Memory usage elevated: {memory.percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {memory.percent:.1f}%"
            
            return HealthResult(
                name="system_memory",
                component_type=ComponentType.MEMORY,
                status=status,
                message=message,
                details={
                    "memory_percent": memory.percent,
                    "available_gb": memory.available / (1024**3)
                }
            )
        except Exception as e:
            return HealthResult(
                name="system_memory",
                component_type=ComponentType.MEMORY,
                status=HealthStatus.UNHEALTHY,
                message="Memory health check failed",
                error=str(e)
            )
    
    async def _check_disk_health(self) -> HealthResult:
        """Check disk health."""
        try:
            disk = psutil.disk_usage('/')
            
            if disk.percent > 95:
                status = HealthStatus.CRITICAL
                message = f"Disk usage critically high: {disk.percent:.1f}%"
            elif disk.percent > 90:
                status = HealthStatus.UNHEALTHY
                message = f"Disk usage high: {disk.percent:.1f}%"
            elif disk.percent > 80:
                status = HealthStatus.DEGRADED
                message = f"Disk usage elevated: {disk.percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk usage normal: {disk.percent:.1f}%"
            
            return HealthResult(
                name="system_disk",
                component_type=ComponentType.DISK,
                status=status,
                message=message,
                details={
                    "disk_percent": disk.percent,
                    "free_gb": disk.free / (1024**3)
                }
            )
        except Exception as e:
            return HealthResult(
                name="system_disk",
                component_type=ComponentType.DISK,
                status=HealthStatus.UNHEALTHY,
                message="Disk health check failed",
                error=str(e)
            )
    
    async def _check_network_health(self) -> HealthResult:
        """Check network health."""
        try:
            # Test network connectivity
            network = psutil.net_io_counters()
            connections = len(psutil.net_connections())
            
            # Simple connectivity test (you might want to ping external services)
            if network.bytes_sent == 0 and network.bytes_recv == 0:
                status = HealthStatus.UNHEALTHY
                message = "No network activity detected"
            elif connections > 1000:
                status = HealthStatus.DEGRADED
                message = f"High number of network connections: {connections}"
            else:
                status = HealthStatus.HEALTHY
                message = f"Network connectivity normal, {connections} connections"
            
            return HealthResult(
                name="system_network",
                component_type=ComponentType.NETWORK,
                status=status,
                message=message,
                details={
                    "connections": connections,
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv
                }
            )
        except Exception as e:
            return HealthResult(
                name="system_network",
                component_type=ComponentType.NETWORK,
                status=HealthStatus.UNHEALTHY,
                message="Network health check failed",
                error=str(e)
            )
    
    async def _check_file_system_health(self) -> HealthResult:
        """Check file system health."""
        try:
            # Test write access to temp directory
            import tempfile
            with tempfile.NamedTemporaryFile(delete=True) as tmp:
                tmp.write(b"health_check")
                tmp.flush()
            
            # Check if we can read from current directory
            os.listdir('.')
            
            status = HealthStatus.HEALTHY
            message = "File system access normal"
            
            return HealthResult(
                name="file_system",
                component_type=ComponentType.FILE_SYSTEM,
                status=status,
                message=message,
                details={"write_test": "passed", "read_test": "passed"}
            )
        except Exception as e:
            return HealthResult(
                name="file_system",
                component_type=ComponentType.FILE_SYSTEM,
                status=HealthStatus.UNHEALTHY,
                message="File system health check failed",
                error=str(e)
            )
    
    def get_health_summary(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get health summary for the specified time window."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)
        
        with self._lock:
            recent_health = [
                h for h in self.health_history
                if h.timestamp >= cutoff_time
            ]
        
        if not recent_health:
            return {"error": "No health data available for the specified time window"}
        
        # Calculate health statistics
        status_counts = {}
        for health in recent_health:
            status = health.overall_status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Get latest health status
        latest_health = recent_health[-1] if recent_health else None
        
        return {
            "time_window_minutes": time_window_minutes,
            "total_checks": len(recent_health),
            "status_distribution": status_counts,
            "latest_status": latest_health.overall_status.value if latest_health else "unknown",
            "latest_components": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "response_time_ms": c.response_time_ms
                }
                for c in latest_health.components
            ] if latest_health else [],
            "system_metrics": latest_health.system_metrics if latest_health else {},
            "uptime_seconds": latest_health.uptime_seconds if latest_health else 0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Global instance
_system_health_monitor = SystemHealthMonitor()

def get_system_health_monitor() -> SystemHealthMonitor:
    """Get the global system health monitor instance."""
    return _system_health_monitor

# Export main components
__all__ = [
    "SystemHealthMonitor",
    "HealthStatus",
    "ComponentType",
    "HealthCheck",
    "HealthResult",
    "SystemHealth",
    "get_system_health_monitor"
]
