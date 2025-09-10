#!/usr/bin/env python3
"""
Prometheus-Compatible Metrics Endpoint

Provides /metrics endpoint with comprehensive metrics in Prometheus format:
- Request latency histograms
- Request counters
- SSE duration histograms
- Provider latency counters
- Cache hit counters
- Token cost counters
- Error rates
- Performance percentiles

Following MAANG/OpenAI/Perplexity standards for enterprise monitoring.
"""

import time
from typing import Dict, Any, List
from datetime import datetime, timezone
from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse

from services.gateway.middleware.observability import get_metrics_collector

# Create metrics router
metrics_router = APIRouter(prefix="/metrics", tags=["metrics"])

def format_prometheus_metric(name: str, value: float, labels: Dict[str, str] = None, help_text: str = None) -> str:
    """Format a metric in Prometheus format."""
    lines = []
    
    # Add help text if provided
    if help_text:
        lines.append(f"# HELP {name} {help_text}")
    
    # Add type (default to gauge)
    lines.append(f"# TYPE {name} gauge")
    
    # Format labels
    if labels:
        label_str = ",".join([f'{k}="{v}"' for k, v in labels.items()])
        lines.append(f"{name}{{{label_str}}} {value}")
    else:
        lines.append(f"{name} {value}")
    
    return "\n".join(lines)

def format_prometheus_counter(name: str, value: float, labels: Dict[str, str] = None, help_text: str = None) -> str:
    """Format a counter metric in Prometheus format."""
    lines = []
    
    # Add help text if provided
    if help_text:
        lines.append(f"# HELP {name} {help_text}")
    
    # Add type
    lines.append(f"# TYPE {name} counter")
    
    # Format labels
    if labels:
        label_str = ",".join([f'{k}="{v}"' for k, v in labels.items()])
        lines.append(f"{name}{{{label_str}}} {value}")
    else:
        lines.append(f"{name} {value}")
    
    return "\n".join(lines)

def format_prometheus_histogram(name: str, values: List[float], labels: Dict[str, str] = None, help_text: str = None) -> str:
    """Format a histogram metric in Prometheus format."""
    if not values:
        return ""
    
    lines = []
    
    # Add help text if provided
    if help_text:
        lines.append(f"# HELP {name} {help_text}")
    
    # Add type
    lines.append(f"# TYPE {name} histogram")
    
    # Calculate percentiles
    sorted_values = sorted(values)
    percentiles = [50, 95, 99]
    
    for p in percentiles:
        index = int((p / 100) * (len(sorted_values) - 1))
        value = sorted_values[index]
        
        if labels:
            label_str = ",".join([f'{k}="{v}"' for k, v in labels.items()])
            lines.append(f"{name}_p{p}{{{label_str}}} {value}")
        else:
            lines.append(f"{name}_p{p} {value}")
    
    # Add count and sum
    count = len(values)
    total = sum(values)
    
    if labels:
        label_str = ",".join([f'{k}="{v}"' for k, v in labels.items()])
        lines.append(f"{name}_count{{{label_str}}} {count}")
        lines.append(f"{name}_sum{{{label_str}}} {total}")
    else:
        lines.append(f"{name}_count {count}")
        lines.append(f"{name}_sum {total}")
    
    return "\n".join(lines)

@metrics_router.get("/", response_class=PlainTextResponse, operation_id="get_prometheus_metrics")
async def get_metrics():
    """Get Prometheus-compatible metrics."""
    try:
        collector = get_metrics_collector()
        metrics_summary = collector.get_metrics_summary()
        
        lines = []
        
        # Add timestamp
        lines.append(f"# Generated at {datetime.now(timezone.utc).isoformat()}")
        lines.append("")
        
        # Request metrics
        lines.append("# Request Metrics")
        lines.append(format_prometheus_counter(
            "http_requests_total",
            metrics_summary["total_requests"],
            help_text="Total number of HTTP requests"
        ))
        lines.append("")
        
        lines.append(format_prometheus_counter(
            "http_errors_total",
            metrics_summary["total_errors"],
            help_text="Total number of HTTP errors"
        ))
        lines.append("")
        
        lines.append(format_prometheus_metric(
            "http_error_rate",
            metrics_summary["error_rate"],
            help_text="HTTP error rate (0-1)"
        ))
        lines.append("")
        
        # Request latency histograms
        for endpoint, p50 in metrics_summary["request_latency_p50"].items():
            p95 = metrics_summary["request_latency_p95"].get(endpoint, 0)
            
            lines.append(format_prometheus_metric(
                "http_request_duration_p50_ms",
                p50,
                {"endpoint": endpoint},
                "50th percentile of HTTP request duration in milliseconds"
            ))
            
            lines.append(format_prometheus_metric(
                "http_request_duration_p95_ms",
                p95,
                {"endpoint": endpoint},
                "95th percentile of HTTP request duration in milliseconds"
            ))
        
        lines.append("")
        
        # SSE metrics
        lines.append("# SSE Metrics")
        for endpoint, connections in metrics_summary["sse_connections"].items():
            lines.append(format_prometheus_counter(
                "sse_connections_total",
                connections,
                {"endpoint": endpoint},
                "Total number of SSE connections"
            ))
        
        lines.append("")
        
        for endpoint, heartbeats in metrics_summary["sse_heartbeats"].items():
            lines.append(format_prometheus_counter(
                "sse_heartbeats_total",
                heartbeats,
                {"endpoint": endpoint},
                "Total number of SSE heartbeats"
            ))
        
        lines.append("")
        
        # SSE duration histograms
        for endpoint, p50 in metrics_summary["sse_duration_p50"].items():
            p95 = metrics_summary["sse_duration_p95"].get(endpoint, 0)
            
            lines.append(format_prometheus_metric(
                "sse_duration_p50_ms",
                p50,
                {"endpoint": endpoint},
                "50th percentile of SSE stream duration in milliseconds"
            ))
            
            lines.append(format_prometheus_metric(
                "sse_duration_p95_ms",
                p95,
                {"endpoint": endpoint},
                "95th percentile of SSE stream duration in milliseconds"
            ))
        
        lines.append("")
        
        # Provider metrics
        lines.append("# Provider Metrics")
        for provider, usage in metrics_summary["provider_usage"].items():
            lines.append(format_prometheus_counter(
                "provider_requests_total",
                usage,
                {"provider": provider},
                "Total number of provider requests"
            ))
        
        lines.append("")
        
        for provider, errors in metrics_summary["provider_errors"].items():
            lines.append(format_prometheus_counter(
                "provider_errors_total",
                errors,
                {"provider": provider},
                "Total number of provider errors"
            ))
        
        lines.append("")
        
        # Provider latency histograms
        for provider, p50 in metrics_summary["provider_latency_p50"].items():
            p95 = metrics_summary["provider_latency_p95"].get(provider, 0)
            
            lines.append(format_prometheus_metric(
                "provider_latency_p50_ms",
                p50,
                {"provider": provider},
                "50th percentile of provider latency in milliseconds"
            ))
            
            lines.append(format_prometheus_metric(
                "provider_latency_p95_ms",
                p95,
                {"provider": provider},
                "95th percentile of provider latency in milliseconds"
            ))
        
        lines.append("")
        
        # Cache metrics
        lines.append("# Cache Metrics")
        for cache_type, hits in metrics_summary["cache_hits"].items():
            lines.append(format_prometheus_counter(
                "cache_hits_total",
                hits,
                {"cache_type": cache_type},
                "Total number of cache hits"
            ))
        
        lines.append("")
        
        for cache_type, misses in metrics_summary["cache_misses"].items():
            lines.append(format_prometheus_counter(
                "cache_misses_total",
                misses,
                {"cache_type": cache_type},
                "Total number of cache misses"
            ))
        
        lines.append("")
        
        # Cost metrics
        lines.append("# Cost Metrics")
        for provider, cost in metrics_summary["token_costs"].items():
            lines.append(format_prometheus_metric(
                "token_cost_total",
                cost,
                {"provider": provider},
                "Total token cost by provider"
            ))
        
        lines.append("")
        
        for provider, cost in metrics_summary["api_costs"].items():
            lines.append(format_prometheus_metric(
                "api_cost_total",
                cost,
                {"provider": provider},
                "Total API cost by provider"
            ))
        
        lines.append("")
        
        # Trace metrics
        lines.append("# Trace Metrics")
        lines.append(format_prometheus_counter(
            "trace_requests_total",
            metrics_summary["trace_requests"],
            help_text="Total number of traced requests"
        ))
        lines.append("")
        
        # System metrics
        lines.append("# System Metrics")
        lines.append(format_prometheus_metric(
            "system_uptime_seconds",
            time.time(),
            help_text="System uptime in seconds"
        ))
        lines.append("")
        
        # Join all lines
        metrics_text = "\n".join(lines)
        
        return PlainTextResponse(
            content=metrics_text,
            media_type="text/plain; version=0.0.4; charset=utf-8"
        )
        
    except Exception as e:
        return PlainTextResponse(
            content=f"# Error generating metrics: {str(e)}\n",
            media_type="text/plain; version=0.0.4; charset=utf-8",
            status_code=500
        )

@metrics_router.get("/health")
async def metrics_health():
    """Health check for metrics endpoint."""
    try:
        collector = get_metrics_collector()
        metrics_summary = collector.get_metrics_summary()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics_count": len(metrics_summary),
            "total_requests": metrics_summary["total_requests"],
            "error_rate": metrics_summary["error_rate"]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@metrics_router.get("/summary", operation_id="get_metrics_summary_json")
async def get_metrics_summary():
    """Get metrics summary in JSON format."""
    try:
        collector = get_metrics_collector()
        return collector.get_metrics_summary()
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
