"""
Universal Knowledge Platform - Metrics Collector
Comprehensive real-time metrics collection for platform health and usage tracking.

Features:
- In-memory counters for basic metrics
- Rolling averages for response times
- LLM provider selection tracking
- Cache hit/miss ratio monitoring
- Health check integration
- Prometheus-compatible metrics

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from collections import deque
import statistics
from enum import Enum

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """LLM provider types."""
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"


class ComponentStatus(str, Enum):
    """Component health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ResponseTimeBreakdown:
    """Breakdown of response times by component."""
    retrieval_time_ms: float = 0.0
    llm_time_ms: float = 0.0
    synthesis_time_ms: float = 0.0
    total_time_ms: float = 0.0


@dataclass
class CacheMetrics:
    """Cache performance metrics."""
    hits: int = 0
    misses: int = 0
    total_requests: int = 0
    
    @property
    def hit_ratio(self) -> float:
        """Calculate cache hit ratio."""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests


@dataclass
class HealthCheckResult:
    """Health check result for a component."""
    component: str
    status: ComponentStatus
    response_time_ms: float
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """
    Singleton metrics collector for real-time platform monitoring.
    
    Features:
    - In-memory counters for queries, errors, and provider usage
    - Rolling averages for response times
    - Cache hit/miss tracking
    - Health check integration
    - Prometheus-compatible metrics
    """
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        
        # Initialize counters
        self._query_counter = 0
        self._error_counter = 0
        self._provider_counters = {provider: 0 for provider in LLMProvider}
        
        # Initialize response time tracking with rolling windows
        self._response_times = deque(maxlen=1000)  # Last 1000 requests
        self._retrieval_times = deque(maxlen=1000)
        self._llm_times = deque(maxlen=1000)
        self._synthesis_times = deque(maxlen=1000)
        
        # Initialize cache metrics
        self._cache_metrics = {
            "query_cache": CacheMetrics(),
            "retrieval_cache": CacheMetrics(),
            "llm_cache": CacheMetrics()
        }
        
        # Initialize health check results
        self._health_results = {}
        
        # Initialize startup time
        self._startup_time = time.time()
        
        logger.info("✅ MetricsCollector initialized successfully")
    
    async def increment_query_counter(self) -> None:
        """Increment total query counter."""
        async with self._lock:
            self._query_counter += 1
    
    async def increment_error_counter(self, error_type: str = "unknown") -> None:
        """Increment error counter."""
        async with self._lock:
            self._error_counter += 1
    
    async def record_provider_usage(self, provider: LLMProvider) -> None:
        """Record LLM provider usage."""
        async with self._lock:
            if provider in self._provider_counters:
                self._provider_counters[provider] += 1
    
    async def record_response_time(self, breakdown: ResponseTimeBreakdown) -> None:
        """Record response time breakdown."""
        async with self._lock:
            self._response_times.append(breakdown.total_time_ms)
            self._retrieval_times.append(breakdown.retrieval_time_ms)
            self._llm_times.append(breakdown.llm_time_ms)
            self._synthesis_times.append(breakdown.synthesis_time_ms)
    
    async def record_cache_hit(self, cache_name: str) -> None:
        """Record cache hit."""
        async with self._lock:
            if cache_name in self._cache_metrics:
                self._cache_metrics[cache_name].hits += 1
                self._cache_metrics[cache_name].total_requests += 1
    
    async def record_cache_miss(self, cache_name: str) -> None:
        """Record cache miss."""
        async with self._lock:
            if cache_name in self._cache_metrics:
                self._cache_metrics[cache_name].misses += 1
                self._cache_metrics[cache_name].total_requests += 1
    
    async def update_health_result(self, result: HealthCheckResult) -> None:
        """Update health check result."""
        async with self._lock:
            self._health_results[result.component] = result
    
    def get_metrics_dict(self) -> Dict[str, Any]:
        """Get comprehensive metrics as dictionary."""
        try:
            # Calculate rolling averages
            avg_response_time = statistics.mean(self._response_times) if self._response_times else 0.0
            avg_retrieval_time = statistics.mean(self._retrieval_times) if self._retrieval_times else 0.0
            avg_llm_time = statistics.mean(self._llm_times) if self._llm_times else 0.0
            avg_synthesis_time = statistics.mean(self._synthesis_times) if self._synthesis_times else 0.0
            
            # Calculate cache metrics
            cache_metrics = {}
            for cache_name, metrics in self._cache_metrics.items():
                cache_metrics[cache_name] = {
                    "hits": metrics.hits,
                    "misses": metrics.misses,
                    "total_requests": metrics.total_requests,
                    "hit_ratio": metrics.hit_ratio
                }
            
            # Calculate provider usage percentages
            total_provider_usage = sum(self._provider_counters.values())
            provider_percentages = {}
            if total_provider_usage > 0:
                for provider, count in self._provider_counters.items():
                    provider_percentages[provider.value] = (count / total_provider_usage) * 100
            else:
                provider_percentages = {provider.value: 0.0 for provider in LLMProvider}
            
            return {
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": time.time() - self._startup_time,
                "queries": {
                    "total_processed": self._query_counter,
                    "errors": self._error_counter,
                    "success_rate": ((self._query_counter - self._error_counter) / max(self._query_counter, 1)) * 100
                },
                "response_times": {
                    "average_total_ms": avg_response_time,
                    "average_retrieval_ms": avg_retrieval_time,
                    "average_llm_ms": avg_llm_time,
                    "average_synthesis_ms": avg_synthesis_time,
                    "breakdown": {
                        "retrieval_percent": (avg_retrieval_time / max(avg_response_time, 1)) * 100,
                        "llm_percent": (avg_llm_time / max(avg_response_time, 1)) * 100,
                        "synthesis_percent": (avg_synthesis_time / max(avg_response_time, 1)) * 100
                    }
                },
                "cache_performance": cache_metrics,
                "llm_providers": {
                    "usage_counts": {provider.value: count for provider, count in self._provider_counters.items()},
                    "usage_percentages": provider_percentages
                },
                "health_status": {
                    component: {
                        "status": result.status.value,
                        "response_time_ms": result.response_time_ms,
                        "error": result.error_message,
                        "details": result.details
                    }
                    for component, result in self._health_results.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate metrics: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "degraded"
            }
    
    def get_prometheus_metrics(self) -> str:
        """Get metrics in Prometheus format."""
        try:
            metrics_lines = []
            
            # Basic counters
            metrics_lines.append(f"# HELP queries_total Total number of queries processed")
            metrics_lines.append(f"# TYPE queries_total counter")
            metrics_lines.append(f"queries_total {self._query_counter}")
            
            metrics_lines.append(f"# HELP errors_total Total number of errors")
            metrics_lines.append(f"# TYPE errors_total counter")
            metrics_lines.append(f"errors_total {self._error_counter}")
            
            # Response time histograms
            if self._response_times:
                avg_response = statistics.mean(self._response_times)
                metrics_lines.append(f"# HELP response_time_seconds Average response time")
                metrics_lines.append(f"# TYPE response_time_seconds gauge")
                metrics_lines.append(f"response_time_seconds {avg_response / 1000.0}")
            
            # Cache metrics
            for cache_name, metrics in self._cache_metrics.items():
                metrics_lines.append(f"# HELP {cache_name}_hits_total Total cache hits")
                metrics_lines.append(f"# TYPE {cache_name}_hits_total counter")
                metrics_lines.append(f"{cache_name}_hits_total {metrics.hits}")
                
                metrics_lines.append(f"# HELP {cache_name}_misses_total Total cache misses")
                metrics_lines.append(f"# TYPE {cache_name}_misses_total counter")
                metrics_lines.append(f"{cache_name}_misses_total {metrics.misses}")
                
                metrics_lines.append(f"# HELP {cache_name}_hit_ratio Cache hit ratio")
                metrics_lines.append(f"# TYPE {cache_name}_hit_ratio gauge")
                metrics_lines.append(f"{cache_name}_hit_ratio {metrics.hit_ratio}")
            
            # Provider usage metrics
            for provider, count in self._provider_counters.items():
                metrics_lines.append(f"# HELP llm_provider_usage_total Usage count by provider")
                metrics_lines.append(f"# TYPE llm_provider_usage_total counter")
                metrics_lines.append(f'llm_provider_usage_total{{provider="{provider.value}"}} {count}')
            
            # Health status
            for component, result in self._health_results.items():
                status_value = {"healthy": 1, "degraded": 0.5, "unhealthy": 0, "unknown": -1}.get(result.status.value, -1)
                metrics_lines.append(f"# HELP component_health Component health status")
                metrics_lines.append(f"# TYPE component_health gauge")
                metrics_lines.append(f'component_health{{component="{component}"}} {status_value}')
                
                metrics_lines.append(f"# HELP component_response_time_ms Component response time")
                metrics_lines.append(f"# TYPE component_response_time_ms gauge")
                metrics_lines.append(f'component_response_time_ms{{component="{component}"}} {result.response_time_ms}')
            
            return "\n".join(metrics_lines)
            
        except Exception as e:
            logger.error(f"Failed to generate Prometheus metrics: {e}")
            return f"# Error generating metrics: {e}"
    
    def reset_metrics(self) -> None:
        """Reset all metrics (useful for testing)."""
        try:
            self._query_counter = 0
            self._error_counter = 0
            self._provider_counters = {provider: 0 for provider in LLMProvider}
            self._response_times.clear()
            self._retrieval_times.clear()
            self._llm_times.clear()
            self._synthesis_times.clear()
            self._cache_metrics = {
                "query_cache": CacheMetrics(),
                "retrieval_cache": CacheMetrics(),
                "llm_cache": CacheMetrics()
            }
            self._health_results.clear()
            logger.info("✅ Metrics reset successfully")
            
        except Exception as e:
            logger.error(f"Failed to reset metrics: {e}")


# Global metrics collector instance
metrics_collector = MetricsCollector()


async def record_query_metrics(
    response_time_breakdown: ResponseTimeBreakdown,
    provider: LLMProvider,
    cache_hits: Dict[str, bool] = None
) -> None:
    """Record comprehensive query metrics."""
    try:
        await metrics_collector.increment_query_counter()
        await metrics_collector.record_provider_usage(provider)
        await metrics_collector.record_response_time(response_time_breakdown)
        
        # Record cache metrics if provided
        if cache_hits:
            for cache_name, hit in cache_hits.items():
                if hit:
                    await metrics_collector.record_cache_hit(cache_name)
                else:
                    await metrics_collector.record_cache_miss(cache_name)
        
        logger.debug(f"📊 Recorded query metrics: provider={provider.value}, total_time={response_time_breakdown.total_time_ms:.2f}ms")
        
    except Exception as e:
        logger.error(f"Failed to record query metrics: {e}")


async def record_error_metrics(error_type: str = "unknown") -> None:
    """Record error metrics."""
    try:
        await metrics_collector.increment_error_counter(error_type)
        logger.debug(f"📊 Recorded error metrics: type={error_type}")
        
    except Exception as e:
        logger.error(f"Failed to record error metrics: {e}")


async def record_health_check(
    component: str,
    status: ComponentStatus,
    response_time_ms: float,
    error_message: Optional[str] = None,
    details: Dict[str, Any] = None
) -> None:
    """Record health check result."""
    try:
        result = HealthCheckResult(
            component=component,
            status=status,
            response_time_ms=response_time_ms,
            error_message=error_message,
            details=details or {}
        )
        await metrics_collector.update_health_result(result)
        logger.debug(f"📊 Recorded health check: {component}={status.value}, {response_time_ms:.2f}ms")
        
    except Exception as e:
        logger.error(f"Failed to record health check: {e}")


def get_metrics_summary() -> Dict[str, Any]:
    """Get metrics summary for API endpoints."""
    return metrics_collector.get_metrics_dict()


def get_prometheus_metrics() -> str:
    """Get Prometheus-formatted metrics."""
    return metrics_collector.get_prometheus_metrics()


def reset_all_metrics() -> None:
    """Reset all metrics (for testing)."""
    metrics_collector.reset_metrics() 