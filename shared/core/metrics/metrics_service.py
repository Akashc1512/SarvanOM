"""
Metrics service for collecting and exposing Prometheus metrics.

Provides counters, histograms, and gauges for monitoring system performance
and behavior across all services.
"""

import time
from typing import Dict, Any, Optional
from collections import defaultdict
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

from shared.core.logging.structured_logger import get_logger


logger = get_logger(__name__)


class MetricsService:
    """Service for collecting and exposing application metrics."""
    
    def __init__(self):
        # HTTP request metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total number of HTTP requests',
            ['method', 'path', 'status']
        )
        
        self.http_request_duration_seconds = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'path']
        )
        
        self.http_errors_total = Counter(
            'http_errors_total',
            'Total number of HTTP errors',
            ['method', 'path', 'error_type']
        )
        
        # LLM metrics
        self.llm_requests_total = Counter(
            'llm_requests_total',
            'Total number of LLM requests',
            ['provider', 'model', 'status']
        )
        
        self.llm_request_duration_seconds = Histogram(
            'llm_request_duration_seconds',
            'LLM request duration in seconds',
            ['provider', 'model']
        )
        
        self.llm_tokens_total = Counter(
            'llm_tokens_total',
            'Total number of LLM tokens used',
            ['provider', 'model', 'token_type']
        )
        
        # Vector store metrics
        self.vector_store_queries_total = Counter(
            'vector_store_queries_total',
            'Total number of vector store queries',
            ['store_type', 'operation', 'status']
        )
        
        self.vector_store_query_duration_seconds = Histogram(
            'vector_store_query_duration_seconds',
            'Vector store query duration in seconds',
            ['store_type', 'operation']
        )
        
        # Cache metrics
        self.cache_hits_total = Counter(
            'cache_hits_total',
            'Total number of cache hits',
            ['cache_type']
        )
        
        self.cache_misses_total = Counter(
            'cache_misses_total',
            'Total number of cache misses',
            ['cache_type']
        )
        
        self.cache_size = Gauge(
            'cache_size',
            'Current cache size',
            ['cache_type']
        )
        
        # Agent metrics
        self.agent_executions_total = Counter(
            'agent_executions_total',
            'Total number of agent executions',
            ['agent_type', 'status']
        )
        
        self.agent_execution_duration_seconds = Histogram(
            'agent_execution_duration_seconds',
            'Agent execution duration in seconds',
            ['agent_type']
        )
        
        # System metrics
        self.active_queries = Gauge(
            'active_queries',
            'Number of currently active queries'
        )
        
        self.memory_usage_bytes = Gauge(
            'memory_usage_bytes',
            'Current memory usage in bytes'
        )
        
        # Custom metrics storage
        self._custom_counters = {}
        self._custom_histograms = {}
        self._custom_gauges = {}
    
    def increment_counter(self, name: str, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        if name == "http_requests_total":
            self.http_requests_total.labels(**labels).inc()
        elif name == "http_errors_total":
            self.http_errors_total.labels(**labels).inc()
        elif name == "llm_requests_total":
            self.llm_requests_total.labels(**labels).inc()
        elif name == "llm_tokens_total":
            self.llm_tokens_total.labels(**labels).inc()
        elif name == "vector_store_queries_total":
            self.vector_store_queries_total.labels(**labels).inc()
        elif name == "cache_hits_total":
            self.cache_hits_total.labels(**labels).inc()
        elif name == "cache_misses_total":
            self.cache_misses_total.labels(**labels).inc()
        elif name == "agent_executions_total":
            self.agent_executions_total.labels(**labels).inc()
        else:
            # Handle custom counters
            if name not in self._custom_counters:
                self._custom_counters[name] = Counter(
                    name,
                    f'Custom counter: {name}',
                    list(labels.keys()) if labels else []
                )
            self._custom_counters[name].labels(**labels).inc()
    
    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a histogram metric."""
        if name == "http_request_duration_seconds":
            self.http_request_duration_seconds.labels(**labels).observe(value)
        elif name == "llm_request_duration_seconds":
            self.llm_request_duration_seconds.labels(**labels).observe(value)
        elif name == "vector_store_query_duration_seconds":
            self.vector_store_query_duration_seconds.labels(**labels).observe(value)
        elif name == "agent_execution_duration_seconds":
            self.agent_execution_duration_seconds.labels(**labels).observe(value)
        else:
            # Handle custom histograms
            if name not in self._custom_histograms:
                self._custom_histograms[name] = Histogram(
                    name,
                    f'Custom histogram: {name}',
                    list(labels.keys()) if labels else []
                )
            self._custom_histograms[name].labels(**labels).observe(value)
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric."""
        if name == "cache_size":
            self.cache_size.labels(**labels).set(value)
        elif name == "active_queries":
            self.active_queries.set(value)
        elif name == "memory_usage_bytes":
            self.memory_usage_bytes.set(value)
        else:
            # Handle custom gauges
            if name not in self._custom_gauges:
                self._custom_gauges[name] = Gauge(
                    name,
                    f'Custom gauge: {name}',
                    list(labels.keys()) if labels else []
                )
            self._custom_gauges[name].labels(**labels).set(value)
    
    def record_llm_request(self, provider: str, model: str, duration: float, 
                          tokens_used: int, status: str = "success"):
        """Record LLM request metrics."""
        self.increment_counter("llm_requests_total", {
            "provider": provider,
            "model": model,
            "status": status
        })
        
        self.record_histogram("llm_request_duration_seconds", duration, {
            "provider": provider,
            "model": model
        })
        
        if tokens_used > 0:
            self.increment_counter("llm_tokens_total", {
                "provider": provider,
                "model": model,
                "token_type": "total"
            })
    
    def record_vector_store_query(self, store_type: str, operation: str, 
                                duration: float, status: str = "success"):
        """Record vector store query metrics."""
        self.increment_counter("vector_store_queries_total", {
            "store_type": store_type,
            "operation": operation,
            "status": status
        })
        
        self.record_histogram("vector_store_query_duration_seconds", duration, {
            "store_type": store_type,
            "operation": operation
        })
    
    def record_cache_operation(self, cache_type: str, hit: bool):
        """Record cache operation metrics."""
        if hit:
            self.increment_counter("cache_hits_total", {"cache_type": cache_type})
        else:
            self.increment_counter("cache_misses_total", {"cache_type": cache_type})
    
    def record_agent_execution(self, agent_type: str, duration: float, status: str = "success"):
        """Record agent execution metrics."""
        self.increment_counter("agent_executions_total", {
            "agent_type": agent_type,
            "status": status
        })
        
        self.record_histogram("agent_execution_duration_seconds", duration, {
            "agent_type": agent_type
        })
    
    def get_metrics(self) -> str:
        """Get Prometheus metrics as string."""
        return generate_latest()
    
    def get_metrics_content_type(self) -> str:
        """Get content type for metrics endpoint."""
        return CONTENT_TYPE_LATEST


# Global metrics service instance
_metrics_service: Optional[MetricsService] = None


def get_metrics_service() -> MetricsService:
    """Get the global metrics service instance."""
    global _metrics_service
    if _metrics_service is None:
        _metrics_service = MetricsService()
        logger.info("Initialized metrics service")
    return _metrics_service
