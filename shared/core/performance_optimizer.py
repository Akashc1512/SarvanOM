"""
Performance Optimization Service for SarvanOM

This module provides comprehensive performance monitoring, optimization,
and bottleneck resolution following MAANG/OpenAI/Perplexity standards.
"""

import asyncio
import functools
import time
import psutil
import gc
from typing import Any, Callable, Dict, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from collections import deque, defaultdict
import structlog
import threading
from concurrent.futures import ThreadPoolExecutor
import weakref

logger = structlog.get_logger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring."""
    function_name: str
    execution_time_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    success: bool = True
    error_message: Optional[str] = None
    cache_hit: bool = False
    retry_count: int = 0

@dataclass
class SystemMetrics:
    """System-wide performance metrics."""
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_usage_percent: float
    network_io_bytes: int
    active_connections: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class PerformanceAlert:
    """Performance alert configuration."""
    metric_name: str
    threshold: float
    operator: str  # 'gt', 'lt', 'eq'
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    enabled: bool = True

class PerformanceMonitor:
    """Comprehensive performance monitoring system."""
    
    def __init__(self, max_history_size: int = 10000):
        self.max_history_size = max_history_size
        self.metrics_history: deque = deque(maxlen=max_history_size)
        self.system_metrics_history: deque = deque(maxlen=1000)
        self.alerts: List[PerformanceAlert] = []
        self.alert_history: deque = deque(maxlen=1000)
        self._lock = threading.Lock()
        self._monitoring_active = False
        self._monitor_task: Optional[asyncio.Task] = None
        
        # Performance thresholds
        self.thresholds = {
            "response_time_ms": 3000,  # 3 seconds
            "memory_usage_mb": 1000,   # 1GB
            "cpu_usage_percent": 80,   # 80%
            "error_rate_percent": 5,   # 5%
            "cache_hit_rate_percent": 30  # 30%
        }
        
        # Initialize default alerts
        self._setup_default_alerts()
    
    def _setup_default_alerts(self):
        """Setup default performance alerts."""
        self.alerts = [
            PerformanceAlert(
                metric_name="response_time_ms",
                threshold=5000,
                operator="gt",
                severity="high",
                message="Response time exceeded 5 seconds"
            ),
            PerformanceAlert(
                metric_name="memory_usage_mb",
                threshold=2000,
                operator="gt",
                severity="critical",
                message="Memory usage exceeded 2GB"
            ),
            PerformanceAlert(
                metric_name="cpu_usage_percent",
                threshold=90,
                operator="gt",
                severity="high",
                message="CPU usage exceeded 90%"
            ),
            PerformanceAlert(
                metric_name="error_rate_percent",
                threshold=10,
                operator="gt",
                severity="critical",
                message="Error rate exceeded 10%"
            )
        ]
    
    async def start_monitoring(self, interval_seconds: float = 30.0):
        """Start continuous system monitoring."""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitor_task = asyncio.create_task(
            self._monitor_system_metrics(interval_seconds)
        )
        logger.info("Performance monitoring started", interval_seconds=interval_seconds)
    
    async def stop_monitoring(self):
        """Stop continuous system monitoring."""
        self._monitoring_active = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Performance monitoring stopped")
    
    async def _monitor_system_metrics(self, interval_seconds: float):
        """Monitor system metrics continuously."""
        while self._monitoring_active:
            try:
                metrics = self._collect_system_metrics()
                with self._lock:
                    self.system_metrics_history.append(metrics)
                
                # Check alerts
                await self._check_system_alerts(metrics)
                
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error("Error in system monitoring", error=str(e))
                await asyncio.sleep(interval_seconds)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available_mb=memory.available / (1024 * 1024),
                disk_usage_percent=disk.percent,
                network_io_bytes=network.bytes_sent + network.bytes_recv,
                active_connections=len(psutil.net_connections())
            )
        except Exception as e:
            logger.error("Error collecting system metrics", error=str(e))
            return SystemMetrics(
                cpu_percent=0,
                memory_percent=0,
                memory_available_mb=0,
                disk_usage_percent=0,
                network_io_bytes=0,
                active_connections=0
            )
    
    async def _check_system_alerts(self, metrics: SystemMetrics):
        """Check system metrics against alerts."""
        for alert in self.alerts:
            if not alert.enabled:
                continue
            
            value = getattr(metrics, alert.metric_name, None)
            if value is None:
                continue
            
            triggered = False
            if alert.operator == "gt" and value > alert.threshold:
                triggered = True
            elif alert.operator == "lt" and value < alert.threshold:
                triggered = True
            elif alert.operator == "eq" and value == alert.threshold:
                triggered = True
            
            if triggered:
                await self._trigger_alert(alert, value, metrics)
    
    async def _trigger_alert(self, alert: PerformanceAlert, value: float, metrics: SystemMetrics):
        """Trigger a performance alert."""
        alert_data = {
            "alert": alert,
            "value": value,
            "threshold": alert.threshold,
            "metrics": metrics,
            "timestamp": datetime.now(timezone.utc)
        }
        
        with self._lock:
            self.alert_history.append(alert_data)
        
        if alert.severity == "critical":
            logger.critical("Critical performance alert", **alert_data)
        elif alert.severity == "high":
            logger.error("High severity performance alert", **alert_data)
        elif alert.severity == "medium":
            logger.warning("Medium severity performance alert", **alert_data)
        else:
            logger.info("Low severity performance alert", **alert_data)
    
    def record_metrics(self, metrics: PerformanceMetrics):
        """Record performance metrics."""
        with self._lock:
            self.metrics_history.append(metrics)
    
    def get_performance_summary(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get performance summary for the specified time window."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)
        
        with self._lock:
            recent_metrics = [
                m for m in self.metrics_history
                if m.timestamp >= cutoff_time
            ]
            
            recent_system_metrics = [
                m for m in self.system_metrics_history
                if m.timestamp >= cutoff_time
            ]
        
        if not recent_metrics:
            return {"error": "No metrics available for the specified time window"}
        
        # Calculate performance statistics
        execution_times = [m.execution_time_ms for m in recent_metrics]
        memory_usage = [m.memory_usage_mb for m in recent_metrics]
        success_count = sum(1 for m in recent_metrics if m.success)
        cache_hits = sum(1 for m in recent_metrics if m.cache_hit)
        
        return {
            "time_window_minutes": time_window_minutes,
            "total_requests": len(recent_metrics),
            "success_rate": (success_count / len(recent_metrics)) * 100,
            "cache_hit_rate": (cache_hits / len(recent_metrics)) * 100,
            "response_time": {
                "avg_ms": sum(execution_times) / len(execution_times),
                "min_ms": min(execution_times),
                "max_ms": max(execution_times),
                "p95_ms": self._calculate_percentile(execution_times, 95),
                "p99_ms": self._calculate_percentile(execution_times, 99)
            },
            "memory_usage": {
                "avg_mb": sum(memory_usage) / len(memory_usage),
                "max_mb": max(memory_usage)
            },
            "system_metrics": self._get_system_summary(recent_system_metrics),
            "alerts": self._get_recent_alerts(time_window_minutes),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def _get_system_summary(self, system_metrics: List[SystemMetrics]) -> Dict[str, Any]:
        """Get system metrics summary."""
        if not system_metrics:
            return {}
        
        return {
            "avg_cpu_percent": sum(m.cpu_percent for m in system_metrics) / len(system_metrics),
            "max_cpu_percent": max(m.cpu_percent for m in system_metrics),
            "avg_memory_percent": sum(m.memory_percent for m in system_metrics) / len(system_metrics),
            "min_memory_available_mb": min(m.memory_available_mb for m in system_metrics),
            "avg_disk_usage_percent": sum(m.disk_usage_percent for m in system_metrics) / len(system_metrics)
        }
    
    def _get_recent_alerts(self, time_window_minutes: int) -> List[Dict[str, Any]]:
        """Get recent alerts within time window."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)
        
        with self._lock:
            recent_alerts = [
                {
                    "metric_name": alert["alert"].metric_name,
                    "severity": alert["alert"].severity,
                    "message": alert["alert"].message,
                    "value": alert["value"],
                    "threshold": alert["threshold"],
                    "timestamp": alert["timestamp"].isoformat()
                }
                for alert in self.alert_history
                if alert["timestamp"] >= cutoff_time
            ]
        
        return recent_alerts

class PerformanceOptimizer:
    """Performance optimization utilities and decorators."""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
        self.cache = {}
        self.cache_ttl = {}
        self._cache_lock = threading.Lock()
    
    def monitor_performance(
        self,
        cache_ttl_seconds: Optional[int] = None,
        max_retries: int = 3,
        timeout_seconds: Optional[float] = None
    ):
        """
        Decorator for monitoring function performance.
        
        Args:
            cache_ttl_seconds: Cache TTL in seconds
            max_retries: Maximum number of retries
            timeout_seconds: Function timeout in seconds
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                function_name = f"{func.__module__}.{func.__name__}"
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / (1024 * 1024)
                
                # Check cache first
                cache_key = self._generate_cache_key(func, args, kwargs)
                if cache_ttl_seconds and self._is_cache_valid(cache_key, cache_ttl_seconds):
                    metrics = PerformanceMetrics(
                        function_name=function_name,
                        execution_time_ms=(time.time() - start_time) * 1000,
                        memory_usage_mb=psutil.Process().memory_info().rss / (1024 * 1024) - start_memory,
                        cpu_usage_percent=psutil.cpu_percent(),
                        cache_hit=True
                    )
                    self.monitor.record_metrics(metrics)
                    return self.cache[cache_key]
                
                # Execute function with retries and timeout
                last_exception = None
                retry_count = 0
                
                for attempt in range(max_retries + 1):
                    try:
                        if timeout_seconds:
                            result = await asyncio.wait_for(
                                func(*args, **kwargs),
                                timeout=timeout_seconds
                            )
                        else:
                            result = await func(*args, **kwargs)
                        
                        # Cache result if TTL specified
                        if cache_ttl_seconds:
                            with self._cache_lock:
                                self.cache[cache_key] = result
                                self.cache_ttl[cache_key] = time.time() + cache_ttl_seconds
                        
                        # Record successful metrics
                        metrics = PerformanceMetrics(
                            function_name=function_name,
                            execution_time_ms=(time.time() - start_time) * 1000,
                            memory_usage_mb=psutil.Process().memory_info().rss / (1024 * 1024) - start_memory,
                            cpu_usage_percent=psutil.cpu_percent(),
                            retry_count=retry_count
                        )
                        self.monitor.record_metrics(metrics)
                        
                        return result
                        
                    except Exception as e:
                        last_exception = e
                        retry_count += 1
                        
                        if attempt < max_retries:
                            await asyncio.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                        else:
                            # Record failed metrics
                            metrics = PerformanceMetrics(
                                function_name=function_name,
                                execution_time_ms=(time.time() - start_time) * 1000,
                                memory_usage_mb=psutil.Process().memory_info().rss / (1024 * 1024) - start_memory,
                                cpu_usage_percent=psutil.cpu_percent(),
                                success=False,
                                error_message=str(e),
                                retry_count=retry_count
                            )
                            self.monitor.record_metrics(metrics)
                            raise e
                
                raise last_exception
            
            return wrapper
        return decorator
    
    def _generate_cache_key(self, func: Callable, args: tuple, kwargs: dict) -> str:
        """Generate cache key for function call."""
        key_parts = [
            func.__name__,
            str(hash(str(args))),
            str(hash(str(sorted(kwargs.items()))))
        ]
        return ":".join(key_parts)
    
    def _is_cache_valid(self, cache_key: str, ttl_seconds: int) -> bool:
        """Check if cache entry is valid."""
        with self._cache_lock:
            if cache_key not in self.cache:
                return False
            return time.time() < self.cache_ttl.get(cache_key, 0)
    
    def clear_cache(self):
        """Clear all cached results."""
        with self._cache_lock:
            self.cache.clear()
            self.cache_ttl.clear()
        logger.info("Performance cache cleared")
    
    def optimize_memory(self):
        """Perform memory optimization."""
        # Force garbage collection
        collected = gc.collect()
        
        # Clear cache if memory usage is high
        memory_percent = psutil.virtual_memory().percent
        if memory_percent > 80:
            self.clear_cache()
            logger.warning("Memory usage high, cleared performance cache", memory_percent=memory_percent)
        
        logger.info("Memory optimization completed", collected_objects=collected, memory_percent=memory_percent)
        return collected

class ConnectionPool:
    """Optimized connection pool for database and external services."""
    
    def __init__(self, max_connections: int = 10, max_idle_time: float = 300.0):
        self.max_connections = max_connections
        self.max_idle_time = max_idle_time
        self.connections: deque = deque()
        self.idle_since: Dict[Any, float] = {}
        self._lock = threading.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def get_connection(self, connection_factory: Callable) -> Any:
        """Get a connection from the pool or create a new one."""
        with self._lock:
            # Try to get an existing connection
            while self.connections:
                connection = self.connections.popleft()
                if connection in self.idle_since:
                    idle_time = time.time() - self.idle_since[connection]
                    if idle_time < self.max_idle_time:
                        del self.idle_since[connection]
                        return connection
                    else:
                        # Connection is too old, close it
                        try:
                            await self._close_connection(connection)
                        except Exception:
                            pass
                        del self.idle_since[connection]
            
            # Create new connection if pool is not full
            if len(self.connections) < self.max_connections:
                return await connection_factory()
            
            # Pool is full, wait for a connection to become available
            # This is a simple implementation - in production, you'd want proper waiting
            return await connection_factory()
    
    async def return_connection(self, connection: Any):
        """Return a connection to the pool."""
        with self._lock:
            if len(self.connections) < self.max_connections:
                self.connections.append(connection)
                self.idle_since[connection] = time.time()
            else:
                # Pool is full, close the connection
                await self._close_connection(connection)
    
    async def _close_connection(self, connection: Any):
        """Close a connection."""
        if hasattr(connection, 'close'):
            if asyncio.iscoroutinefunction(connection.close):
                await connection.close()
            else:
                connection.close()
    
    async def cleanup_idle_connections(self):
        """Clean up idle connections."""
        current_time = time.time()
        with self._lock:
            connections_to_close = []
            for connection, idle_since in list(self.idle_since.items()):
                if current_time - idle_since > self.max_idle_time:
                    connections_to_close.append(connection)
            
            for connection in connections_to_close:
                try:
                    await self._close_connection(connection)
                    self.connections.remove(connection)
                    del self.idle_since[connection]
                except Exception as e:
                    logger.warning("Error closing idle connection", error=str(e))
    
    async def start_cleanup_task(self, interval_seconds: float = 60.0):
        """Start periodic cleanup of idle connections."""
        if self._cleanup_task:
            return
        
        async def cleanup_loop():
            while True:
                try:
                    await self.cleanup_idle_connections()
                    await asyncio.sleep(interval_seconds)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error("Error in connection cleanup", error=str(e))
                    await asyncio.sleep(interval_seconds)
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())
    
    async def stop_cleanup_task(self):
        """Stop the cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

# Global instances
_performance_monitor = PerformanceMonitor()
_performance_optimizer = PerformanceOptimizer(_performance_monitor)

def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    return _performance_monitor

def get_performance_optimizer() -> PerformanceOptimizer:
    """Get the global performance optimizer instance."""
    return _performance_optimizer

# Convenience decorators
def monitor_performance(**kwargs):
    """Convenience decorator for performance monitoring."""
    return _performance_optimizer.monitor_performance(**kwargs)

# Export main components
__all__ = [
    "PerformanceMonitor",
    "PerformanceOptimizer", 
    "ConnectionPool",
    "PerformanceMetrics",
    "SystemMetrics",
    "PerformanceAlert",
    "get_performance_monitor",
    "get_performance_optimizer",
    "monitor_performance"
]
