#!/usr/bin/env python3
"""
MAANG-Grade Observability Middleware

Provides comprehensive metrics collection, tracing, and monitoring for:
- Request latency histograms
- Request counters
- SSE duration histograms
- Provider latency counters
- Cache hit counters
- Token cost counters
- Trace ID propagation
- Structured logging

Following MAANG/OpenAI/Perplexity standards for enterprise observability.
"""

import time
import uuid
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
from collections import defaultdict, Counter
import asyncio
import json

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

# Configure logging
logger = logging.getLogger(__name__)

# Metrics storage
class MetricsCollector:
    """In-memory metrics collector for Prometheus-style metrics."""
    
    def __init__(self):
        # Request metrics
        self.request_counter = Counter()
        self.request_latency_histogram = defaultdict(list)
        self.request_errors = Counter()
        
        # SSE metrics
        self.sse_duration_histogram = defaultdict(list)
        self.sse_connections = Counter()
        self.sse_heartbeats = Counter()
        
        # Provider metrics
        self.provider_latency = defaultdict(list)
        self.provider_usage = Counter()
        self.provider_errors = Counter()
        
        # Cache metrics
        self.cache_hits = Counter()
        self.cache_misses = Counter()
        
        # Cost metrics
        self.token_costs = defaultdict(float)
        self.api_costs = defaultdict(float)
        
        # Trace metrics
        self.trace_requests = Counter()
        self.trace_duration = defaultdict(list)
        
        logger.info("✅ MetricsCollector initialized")
    
    def increment_request_counter(self, method: str, endpoint: str, status_code: int):
        """Increment request counter."""
        key = f"{method}_{endpoint}_{status_code}"
        self.request_counter[key] += 1
    
    def record_request_latency(self, method: str, endpoint: str, latency_ms: float):
        """Record request latency."""
        key = f"{method}_{endpoint}"
        self.request_latency_histogram[key].append(latency_ms)
    
    def increment_request_errors(self, method: str, endpoint: str, error_type: str):
        """Increment request error counter."""
        key = f"{method}_{endpoint}_{error_type}"
        self.request_errors[key] += 1
    
    def record_sse_duration(self, endpoint: str, duration_ms: float):
        """Record SSE stream duration."""
        self.sse_duration_histogram[endpoint].append(duration_ms)
    
    def increment_sse_connections(self, endpoint: str):
        """Increment SSE connection counter."""
        self.sse_connections[endpoint] += 1
    
    def increment_sse_heartbeats(self, endpoint: str):
        """Increment SSE heartbeat counter."""
        self.sse_heartbeats[endpoint] += 1
    
    def record_provider_latency(self, provider: str, latency_ms: float):
        """Record provider latency."""
        self.provider_latency[provider].append(latency_ms)
    
    def increment_provider_usage(self, provider: str):
        """Increment provider usage counter."""
        self.provider_usage[provider] += 1
    
    def increment_provider_errors(self, provider: str, error_type: str):
        """Increment provider error counter."""
        key = f"{provider}_{error_type}"
        self.provider_errors[key] += 1
    
    def increment_cache_hits(self, cache_type: str):
        """Increment cache hit counter."""
        self.cache_hits[cache_type] += 1
    
    def increment_cache_misses(self, cache_type: str):
        """Increment cache miss counter."""
        self.cache_misses[cache_type] += 1
    
    def record_token_cost(self, provider: str, tokens: int, cost: float):
        """Record token cost."""
        self.token_costs[provider] += cost
    
    def record_api_cost(self, provider: str, cost: float):
        """Record API cost."""
        self.api_costs[provider] += cost
    
    def increment_trace_requests(self, trace_id: str):
        """Increment trace request counter."""
        self.trace_requests[trace_id] += 1
    
    def record_trace_duration(self, trace_id: str, duration_ms: float):
        """Record trace duration."""
        self.trace_duration[trace_id].append(duration_ms)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary for /metrics endpoint."""
        def calculate_percentiles(values: List[float], percentiles: List[float] = [50, 95, 99]) -> Dict[str, float]:
            if not values:
                return {f"p{p}": 0.0 for p in percentiles}
            
            sorted_values = sorted(values)
            result = {}
            for p in percentiles:
                index = int((p / 100) * (len(sorted_values) - 1))
                result[f"p{p}"] = sorted_values[index]
            return result
        
        # Calculate latency percentiles
        request_latency_p50 = {}
        request_latency_p95 = {}
        for key, values in self.request_latency_histogram.items():
            percentiles = calculate_percentiles(values)
            request_latency_p50[key] = percentiles["p50"]
            request_latency_p95[key] = percentiles["p95"]
        
        # Calculate provider latency percentiles
        provider_latency_p50 = {}
        provider_latency_p95 = {}
        for provider, values in self.provider_latency.items():
            percentiles = calculate_percentiles(values)
            provider_latency_p50[provider] = percentiles["p50"]
            provider_latency_p95[provider] = percentiles["p95"]
        
        # Calculate SSE duration percentiles
        sse_duration_p50 = {}
        sse_duration_p95 = {}
        for endpoint, values in self.sse_duration_histogram.items():
            percentiles = calculate_percentiles(values)
            sse_duration_p50[endpoint] = percentiles["p50"]
            sse_duration_p95[endpoint] = percentiles["p95"]
        
        return {
            "request_counter": dict(self.request_counter),
            "request_errors": dict(self.request_errors),
            "request_latency_p50": request_latency_p50,
            "request_latency_p95": request_latency_p95,
            "sse_connections": dict(self.sse_connections),
            "sse_heartbeats": dict(self.sse_heartbeats),
            "sse_duration_p50": sse_duration_p50,
            "sse_duration_p95": sse_duration_p95,
            "provider_usage": dict(self.provider_usage),
            "provider_errors": dict(self.provider_errors),
            "provider_latency_p50": provider_latency_p50,
            "provider_latency_p95": provider_latency_p95,
            "cache_hits": dict(self.cache_hits),
            "cache_misses": dict(self.cache_misses),
            "token_costs": dict(self.token_costs),
            "api_costs": dict(self.api_costs),
            "trace_requests": len(self.trace_requests),
            "total_requests": sum(self.request_counter.values()),
            "total_errors": sum(self.request_errors.values()),
            "error_rate": sum(self.request_errors.values()) / max(1, sum(self.request_counter.values())),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Global metrics collector
metrics_collector = MetricsCollector()

@dataclass
class TraceContext:
    """Trace context for request tracking."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: Dict[str, str] = field(default_factory=dict)
    baggage: Dict[str, str] = field(default_factory=dict)

class ObservabilityMiddleware(BaseHTTPMiddleware):
    """MAANG-grade observability middleware."""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger(__name__)
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request with observability."""
        # Generate or extract trace ID
        trace_id = self._get_or_generate_trace_id(request)
        
        # Create trace context
        trace_context = TraceContext(
            trace_id=trace_id,
            span_id=str(uuid.uuid4()),
            tags={
                "method": request.method,
                "path": request.url.path,
                "user_agent": request.headers.get("user-agent", "unknown"),
                "remote_addr": request.client.host if request.client else "unknown"
            }
        )
        
        # Add trace context to request state
        request.state.trace_context = trace_context
        
        # Record request start
        start_time = time.time()
        self.logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "trace_id": trace_id,
                "span_id": trace_context.span_id,
                "method": request.method,
                "path": request.url.path,
                "user_agent": request.headers.get("user-agent", "unknown"),
                "remote_addr": request.client.host if request.client else "unknown"
            }
        )
        
        # Increment request counter
        metrics_collector.increment_trace_requests(trace_id)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Record metrics
            metrics_collector.increment_request_counter(
                request.method, 
                request.url.path, 
                response.status_code
            )
            metrics_collector.record_request_latency(
                request.method, 
                request.url.path, 
                latency_ms
            )
            metrics_collector.record_trace_duration(trace_id, latency_ms)
            
            # Add trace ID to response headers
            response.headers["X-Trace-ID"] = trace_id
            
            # Log request completion
            self.logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    "trace_id": trace_id,
                    "span_id": trace_context.span_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "latency_ms": latency_ms,
                    "response_size": response.headers.get("content-length", 0)
                }
            )
            
            return response
            
        except Exception as e:
            # Calculate latency for failed requests
            latency_ms = (time.time() - start_time) * 1000
            
            # Record error metrics
            metrics_collector.increment_request_errors(
                request.method, 
                request.url.path, 
                type(e).__name__
            )
            metrics_collector.record_trace_duration(trace_id, latency_ms)
            
            # Log error
            self.logger.error(
                f"Request failed: {request.method} {request.url.path} - {type(e).__name__}",
                extra={
                    "trace_id": trace_id,
                    "span_id": trace_context.span_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "latency_ms": latency_ms
                }
            )
            
            raise
            
    def _get_or_generate_trace_id(self, request: Request) -> str:
        """Get trace ID from headers or generate new one."""
        # Check for existing trace ID in headers
        trace_id = request.headers.get("X-Trace-ID")
        if trace_id:
            return trace_id
        
        # Check for trace ID in query parameters
        trace_id = request.query_params.get("trace_id")
        if trace_id:
            return trace_id
        
        # Generate new trace ID
        return f"trace_{uuid.uuid4().hex[:16]}"

def log_request_metrics(
    trace_id: str,
    method: str,
    endpoint: str,
    status_code: int,
    latency_ms: float,
    **kwargs
):
    """Log request metrics with trace ID."""
    logger.info(
        f"Request metrics: {method} {endpoint} - {status_code}",
        extra={
            "trace_id": trace_id,
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "latency_ms": latency_ms,
            **kwargs
        }
    )

def log_sse_metrics(
    trace_id: str,
    endpoint: str,
    duration_ms: float,
    heartbeats: int,
    chunks: int,
    **kwargs
):
    """Log SSE metrics with trace ID."""
    logger.info(
        f"SSE metrics: {endpoint} - {duration_ms}ms",
        extra={
            "trace_id": trace_id,
            "endpoint": endpoint,
            "duration_ms": duration_ms,
            "heartbeats": heartbeats,
            "chunks": chunks,
            **kwargs
        }
    )

def log_provider_metrics(
    trace_id: str,
    provider: str,
    latency_ms: float,
    success: bool,
    tokens: Optional[int] = None,
    cost: Optional[float] = None,
    **kwargs
):
    """Log provider metrics with trace ID."""
    # Record metrics
    metrics_collector.record_provider_latency(provider, latency_ms)
    metrics_collector.increment_provider_usage(provider)
    
    if not success:
        metrics_collector.increment_provider_errors(provider, "api_error")
    
    if tokens and cost:
        metrics_collector.record_token_cost(provider, tokens, cost)
    
    logger.info(
        f"Provider metrics: {provider} - {latency_ms}ms - {'success' if success else 'error'}",
        extra={
            "trace_id": trace_id,
        "provider": provider,
            "latency_ms": latency_ms,
        "success": success,
            "tokens": tokens,
            "cost": cost,
            **kwargs
        }
    )

def log_cache_metrics(
    trace_id: str,
    cache_type: str,
    hit: bool,
    latency_ms: float,
    **kwargs
):
    """Log cache metrics with trace ID."""
    if hit:
        metrics_collector.increment_cache_hits(cache_type)
    else:
        metrics_collector.increment_cache_misses(cache_type)
    
    logger.info(
        f"Cache metrics: {cache_type} - {'hit' if hit else 'miss'} - {latency_ms}ms",
        extra={
            "trace_id": trace_id,
        "cache_type": cache_type,
        "hit": hit,
            "latency_ms": latency_ms,
            **kwargs
        }
    )

def log_stream_event(
    event_type: str,
    stream_id: str,
    data: Dict[str, Any],
    trace_id: Optional[str] = None
):
    """Log stream event with trace ID."""
    logger.info(
        f"Stream event: {event_type} - {stream_id}",
        extra={
            "trace_id": trace_id or "unknown",
        "event_type": event_type,
        "stream_id": stream_id,
            "data": data
        }
    )

def log_error(
    error_type: str,
    message: str,
    trace_id: Optional[str] = None,
    **kwargs
):
    """Log error with trace ID."""
    logger.error(
        f"Error: {error_type} - {message}",
        extra={
            "trace_id": trace_id or "unknown",
        "error_type": error_type,
            "error_message": message,
            **kwargs
        }
    )

def monitor_performance(
    operation: str,
    trace_id: str,
    start_time: float,
    **kwargs
):
    """Monitor operation performance with trace ID."""
    duration_ms = (time.time() - start_time) * 1000
    
    logger.info(
        f"Performance: {operation} - {duration_ms}ms",
        extra={
            "trace_id": trace_id,
            "operation": operation,
            "duration_ms": duration_ms,
            **kwargs
        }
    )
    
    return duration_ms

def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector."""
    return metrics_collector

def get_request_id() -> str:
    """Generate a unique request ID."""
    return f"req_{uuid.uuid4().hex[:16]}"

def get_user_id() -> str:
    """Generate a unique user ID."""
    return f"user_{uuid.uuid4().hex[:16]}"

def log_llm_call(trace_id: str, provider: str, model: str, tokens: int, latency_ms: float, success: bool, **kwargs):
    """Log LLM call metrics with trace ID."""
    logger.info(
        f"LLM call: {provider}/{model} - {tokens} tokens, {latency_ms:.2f}ms, success={success}",
        extra={
            "trace_id": trace_id,
            "provider": provider,
            "model": model,
            "tokens": tokens,
            "latency_ms": latency_ms,
            "success": success,
            **kwargs
        }
    )

def log_security_event(event_type: str, message: str, context: Dict[str, Any]):
    """Log security events with enhanced context."""
    logger.warning(
        f"Security event: {event_type} - {message}",
        extra={
            "event_type": f"security_{event_type}",
            "security_message": message,
            **context
        }
    )