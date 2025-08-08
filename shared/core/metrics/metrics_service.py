"""
Metrics Service for SarvanOM

Provides comprehensive metrics collection and monitoring capabilities
for the Universal Knowledge Platform.
"""

import time
from typing import Dict, Optional, Any
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
import threading

from shared.core.logging import get_logger


logger = get_logger(__name__)

# Global registry to prevent duplicate registrations
_metrics_service_instance = None
_metrics_service_lock = threading.Lock()

class MetricsService:
    """Service for collecting and exposing application metrics."""
    
    def __init__(self):
        # Use a custom registry to avoid conflicts
        self.registry = CollectorRegistry()
        
        # HTTP request metrics
        try:
            self.http_requests_total = Counter(
                'http_requests_total',
                'Total number of HTTP requests',
                ['method', 'path', 'status'],
                registry=self.registry
            )
        except ValueError:
            # Handle duplicate registration
            self.http_requests_total = None
        
        try:
            self.http_request_duration_seconds = Histogram(
                'http_request_duration_seconds',
                'HTTP request duration in seconds',
                ['method', 'path'],
                registry=self.registry
            )
        except ValueError:
            self.http_request_duration_seconds = None
        
        try:
            self.http_errors_total = Counter(
                'http_errors_total',
                'Total number of HTTP errors',
                ['method', 'path', 'error_type'],
                registry=self.registry
            )
        except ValueError:
            self.http_errors_total = None
        
        # LLM metrics
        try:
            self.llm_requests_total = Counter(
                'llm_requests_total',
                'Total number of LLM requests',
                ['provider', 'model', 'status'],
                registry=self.registry
            )
        except ValueError:
            self.llm_requests_total = None
        
        try:
            self.llm_request_duration_seconds = Histogram(
                'llm_request_duration_seconds',
                'LLM request duration in seconds',
                ['provider', 'model'],
                registry=self.registry
            )
        except ValueError:
            self.llm_request_duration_seconds = None
        
        try:
            self.llm_tokens_total = Counter(
                'llm_tokens_total',
                'Total number of LLM tokens used',
                ['provider', 'model', 'token_type'],
                registry=self.registry
            )
        except ValueError:
            self.llm_tokens_total = None
        
        # Vector store metrics
        try:
            self.vector_store_queries_total = Counter(
                'vector_store_queries_total',
                'Total number of vector store queries',
                ['store_type', 'operation', 'status'],
                registry=self.registry
            )
        except ValueError:
            self.vector_store_queries_total = None
        
        try:
            self.vector_store_query_duration_seconds = Histogram(
                'vector_store_query_duration_seconds',
                'Vector store query duration in seconds',
                ['store_type', 'operation'],
                registry=self.registry
            )
        except ValueError:
            self.vector_store_query_duration_seconds = None
        
        # Cache metrics
        try:
            self.cache_hits_total = Counter(
                'cache_hits_total',
                'Total number of cache hits',
                ['cache_type'],
                registry=self.registry
            )
        except ValueError:
            self.cache_hits_total = None
        
        try:
            self.cache_misses_total = Counter(
                'cache_misses_total',
                'Total number of cache misses',
                ['cache_type'],
                registry=self.registry
            )
        except ValueError:
            self.cache_misses_total = None
        
        try:
            self.cache_size = Gauge(
                'cache_size',
                'Current cache size',
                ['cache_type'],
                registry=self.registry
            )
        except ValueError:
            self.cache_size = None
        
        # Agent metrics
        try:
            self.agent_executions_total = Counter(
                'agent_executions_total',
                'Total number of agent executions',
                ['agent_type', 'status'],
                registry=self.registry
            )
        except ValueError:
            self.agent_executions_total = None
        
        try:
            self.agent_execution_duration_seconds = Histogram(
                'agent_execution_duration_seconds',
                'Agent execution duration in seconds',
                ['agent_type'],
                registry=self.registry
            )
        except ValueError:
            self.agent_execution_duration_seconds = None
        
        # System metrics
        try:
            self.active_queries = Gauge(
                'active_queries',
                'Number of currently active queries',
                registry=self.registry
            )
        except ValueError:
            self.active_queries = None
        
        try:
            self.memory_usage_bytes = Gauge(
                'memory_usage_bytes',
                'Current memory usage in bytes',
                registry=self.registry
            )
        except ValueError:
            self.memory_usage_bytes = None
        
        # Custom metrics storage
        self._custom_counters = {}
        self._custom_histograms = {}
    
    def increment_counter(self, name: str, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        if name == "http_requests_total":
            if self.http_requests_total:
                self.http_requests_total.labels(**labels).inc()
        elif name == "http_errors_total":
            if self.http_errors_total:
                self.http_errors_total.labels(**labels).inc()
        elif name == "llm_requests_total":
            if self.llm_requests_total:
                self.llm_requests_total.labels(**labels).inc()
        elif name == "llm_tokens_total":
            if self.llm_tokens_total:
                self.llm_tokens_total.labels(**labels).inc()
        elif name == "vector_store_queries_total":
            if self.vector_store_queries_total:
                self.vector_store_queries_total.labels(**labels).inc()
        elif name == "cache_hits_total":
            if self.cache_hits_total:
                self.cache_hits_total.labels(**labels).inc()
        elif name == "cache_misses_total":
            if self.cache_misses_total:
                self.cache_misses_total.labels(**labels).inc()
        elif name == "agent_executions_total":
            if self.agent_executions_total:
                self.agent_executions_total.labels(**labels).inc()
        else:
            # Handle custom counters
            if name not in self._custom_counters:
                self._custom_counters[name] = Counter(
                    name,
                    f'Custom counter: {name}',
                    list(labels.keys()) if labels else [],
                    registry=self.registry
                )
            self._custom_counters[name].labels(**labels).inc()
    
    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a histogram metric."""
        if name == "http_request_duration_seconds":
            if self.http_request_duration_seconds:
                self.http_request_duration_seconds.labels(**labels).observe(value)
        elif name == "llm_request_duration_seconds":
            if self.llm_request_duration_seconds:
                self.llm_request_duration_seconds.labels(**labels).observe(value)
        elif name == "vector_store_query_duration_seconds":
            if self.vector_store_query_duration_seconds:
                self.vector_store_query_duration_seconds.labels(**labels).observe(value)
        elif name == "agent_execution_duration_seconds":
            if self.agent_execution_duration_seconds:
                self.agent_execution_duration_seconds.labels(**labels).observe(value)
        else:
            # Handle custom histograms
            if name not in self._custom_histograms:
                self._custom_histograms[name] = Histogram(
                    name,
                    f'Custom histogram: {name}',
                    list(labels.keys()) if labels else [],
                    registry=self.registry
                )
            self._custom_histograms[name].labels(**labels).observe(value)
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric."""
        if name == "cache_size":
            if self.cache_size:
                self.cache_size.labels(**labels).set(value)
        elif name == "active_queries":
            if self.active_queries:
                self.active_queries.set(value)
        elif name == "memory_usage_bytes":
            if self.memory_usage_bytes:
                self.memory_usage_bytes.set(value)
        else:
            # Handle custom gauges
            if name not in self._custom_gauges:
                self._custom_gauges[name] = Gauge(
                    name,
                    f'Custom gauge: {name}',
                    list(labels.keys()) if labels else [],
                    registry=self.registry
                )
            self._custom_gauges[name].labels(**labels).set(value)
    
    def record_llm_request(self, provider: str, model: str, duration: float, 
                          tokens_used: int, status: str = "success"):
        """Record LLM request metrics."""
        if self.llm_requests_total:
            self.increment_counter("llm_requests_total", {
                "provider": provider,
                "model": model,
                "status": status
            })
        
        if self.llm_request_duration_seconds:
            self.record_histogram("llm_request_duration_seconds", duration, {
                "provider": provider,
                "model": model
            })
        
        if tokens_used > 0 and self.llm_tokens_total:
            self.increment_counter("llm_tokens_total", {
                "provider": provider,
                "model": model,
                "token_type": "total"
            })
    
    def record_vector_store_query(self, store_type: str, operation: str, 
                                duration: float, status: str = "success"):
        """Record vector store query metrics."""
        if self.vector_store_queries_total:
            self.increment_counter("vector_store_queries_total", {
                "store_type": store_type,
                "operation": operation,
                "status": status
            })
        
        if self.vector_store_query_duration_seconds:
            self.record_histogram("vector_store_query_duration_seconds", duration, {
                "store_type": store_type,
                "operation": operation
            })
    
    def record_cache_operation(self, cache_type: str, hit: bool):
        """Record cache operation metrics."""
        if hit:
            if self.cache_hits_total:
                self.increment_counter("cache_hits_total", {"cache_type": cache_type})
        else:
            if self.cache_misses_total:
                self.increment_counter("cache_misses_total", {"cache_type": cache_type})
    
    def record_agent_execution(self, agent_type: str, duration: float, status: str = "success"):
        """Record agent execution metrics."""
        if self.agent_executions_total:
            self.increment_counter("agent_executions_total", {
                "agent_type": agent_type,
                "status": status
            })
        
        if self.agent_execution_duration_seconds:
            self.record_histogram("agent_execution_duration_seconds", duration, {
                "agent_type": agent_type
            })
    
    def get_metrics(self) -> str:
        """Get Prometheus metrics as string."""
        return generate_latest(self.registry)
    
    def get_metrics_content_type(self) -> str:
        """Get content type for metrics endpoint."""
        return CONTENT_TYPE_LATEST


def get_metrics_service() -> MetricsService:
    """Get the global metrics service instance."""
    global _metrics_service_instance
    with _metrics_service_lock:
        if _metrics_service_instance is None:
            _metrics_service_instance = MetricsService()
            logger.info("Initialized metrics service")
        return _metrics_service_instance
