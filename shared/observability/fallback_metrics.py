#!/usr/bin/env python3
"""
Fallback Metrics Service - SarvanOM v2

Tracks keyless fallback usage by lane/provider and provider failure/timeout rates.
Implements PR-6 observability requirements for fallback monitoring.
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import structlog
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry

logger = structlog.get_logger(__name__)

@dataclass
class FallbackEvent:
    """Fallback event data structure"""
    timestamp: datetime
    lane: str
    provider: str
    source: str  # 'keyed' or 'keyless'
    fallback_used: bool
    timeout: bool
    error: Optional[str] = None
    latency_ms: float = 0.0
    trace_id: Optional[str] = None

class FallbackMetricsCollector:
    """Collects and tracks fallback metrics for observability"""
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or CollectorRegistry()
        self.events: List[FallbackEvent] = []
        self.auto_demotion_threshold = 0.3  # 30% failure rate triggers auto-demotion
        
        # Prometheus metrics
        self._init_metrics()
    
    def _init_metrics(self):
        """Initialize Prometheus metrics"""
        # Keyless fallback usage counters
        self.keyless_fallback_counter = Counter(
            'sarvanom_keyless_fallback_total',
            'Total keyless fallback usage by lane and provider',
            ['lane', 'provider', 'source'],
            registry=self.registry
        )
        
        # Provider failure/timeout rates
        self.provider_failure_counter = Counter(
            'sarvanom_provider_failures_total',
            'Total provider failures by lane and provider',
            ['lane', 'provider', 'failure_type'],
            registry=self.registry
        )
        
        # Provider timeout rates
        self.provider_timeout_counter = Counter(
            'sarvanom_provider_timeouts_total',
            'Total provider timeouts by lane and provider',
            ['lane', 'provider'],
            registry=self.registry
        )
        
        # Provider latency histograms
        self.provider_latency_histogram = Histogram(
            'sarvanom_provider_latency_seconds',
            'Provider response latency',
            ['lane', 'provider', 'source'],
            registry=self.registry
        )
        
        # Auto-demotion threshold gauge
        self.auto_demotion_threshold_gauge = Gauge(
            'sarvanom_auto_demotion_threshold',
            'Auto-demotion threshold for provider failures',
            registry=self.registry
        )
        
        # Provider health status
        self.provider_health_gauge = Gauge(
            'sarvanom_provider_health_status',
            'Provider health status (1=healthy, 0=unhealthy)',
            ['lane', 'provider'],
            registry=self.registry
        )
        
        # Set initial threshold
        self.auto_demotion_threshold_gauge.set(self.auto_demotion_threshold)
    
    def record_fallback_event(self, event: FallbackEvent):
        """Record a fallback event"""
        try:
            # Store event
            self.events.append(event)
            
            # Emit Prometheus metrics
            if event.fallback_used:
                self.keyless_fallback_counter.labels(
                    lane=event.lane,
                    provider=event.provider,
                    source=event.source
                ).inc()
            
            # Record latency
            self.provider_latency_histogram.labels(
                lane=event.lane,
                provider=event.provider,
                source=event.source
            ).observe(event.latency_ms / 1000.0)
            
            # Record failures
            if event.error:
                failure_type = 'timeout' if event.timeout else 'error'
                self.provider_failure_counter.labels(
                    lane=event.lane,
                    provider=event.provider,
                    failure_type=failure_type
                ).inc()
            
            # Record timeouts
            if event.timeout:
                self.provider_timeout_counter.labels(
                    lane=event.lane,
                    provider=event.provider
                ).inc()
            
            # Update provider health status
            health_status = 0 if event.error else 1
            self.provider_health_gauge.labels(
                lane=event.lane,
                provider=event.provider
            ).set(health_status)
            
            logger.info(
                "Fallback event recorded",
                lane=event.lane,
                provider=event.provider,
                source=event.source,
                fallback_used=event.fallback_used,
                timeout=event.timeout,
                latency_ms=event.latency_ms,
                trace_id=event.trace_id
            )
            
        except Exception as e:
            logger.error(f"Failed to record fallback event: {e}")
    
    def get_fallback_stats(self, lane: Optional[str] = None, provider: Optional[str] = None) -> Dict[str, Any]:
        """Get fallback statistics for a specific lane or provider"""
        try:
            # Filter events
            filtered_events = self.events
            if lane:
                filtered_events = [e for e in filtered_events if e.lane == lane]
            if provider:
                filtered_events = [e for e in filtered_events if e.provider == provider]
            
            if not filtered_events:
                return {
                    "total_events": 0,
                    "fallback_usage_rate": 0.0,
                    "timeout_rate": 0.0,
                    "error_rate": 0.0,
                    "avg_latency_ms": 0.0,
                    "auto_demotion_eligible": False
                }
            
            # Calculate statistics
            total_events = len(filtered_events)
            fallback_events = [e for e in filtered_events if e.fallback_used]
            timeout_events = [e for e in filtered_events if e.timeout]
            error_events = [e for e in filtered_events if e.error]
            
            fallback_usage_rate = len(fallback_events) / total_events
            timeout_rate = len(timeout_events) / total_events
            error_rate = len(error_events) / total_events
            avg_latency_ms = sum(e.latency_ms for e in filtered_events) / total_events
            
            # Check auto-demotion eligibility
            failure_rate = timeout_rate + error_rate
            auto_demotion_eligible = failure_rate >= self.auto_demotion_threshold
            
            return {
                "total_events": total_events,
                "fallback_usage_rate": fallback_usage_rate,
                "timeout_rate": timeout_rate,
                "error_rate": error_rate,
                "avg_latency_ms": avg_latency_ms,
                "auto_demotion_eligible": auto_demotion_eligible,
                "failure_rate": failure_rate,
                "threshold": self.auto_demotion_threshold
            }
            
        except Exception as e:
            logger.error(f"Failed to get fallback stats: {e}")
            return {}
    
    def get_provider_health_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get health summary for all providers"""
        try:
            # Group events by lane and provider
            provider_stats = {}
            
            for event in self.events:
                key = f"{event.lane}:{event.provider}"
                if key not in provider_stats:
                    provider_stats[key] = {
                        "lane": event.lane,
                        "provider": event.provider,
                        "total_requests": 0,
                        "successful_requests": 0,
                        "failed_requests": 0,
                        "timeout_requests": 0,
                        "total_latency_ms": 0.0
                    }
                
                stats = provider_stats[key]
                stats["total_requests"] += 1
                stats["total_latency_ms"] += event.latency_ms
                
                if event.error:
                    stats["failed_requests"] += 1
                    if event.timeout:
                        stats["timeout_requests"] += 1
                else:
                    stats["successful_requests"] += 1
            
            # Calculate health metrics
            health_summary = {}
            for key, stats in provider_stats.items():
                success_rate = stats["successful_requests"] / stats["total_requests"] if stats["total_requests"] > 0 else 0
                avg_latency_ms = stats["total_latency_ms"] / stats["total_requests"] if stats["total_requests"] > 0 else 0
                timeout_rate = stats["timeout_requests"] / stats["total_requests"] if stats["total_requests"] > 0 else 0
                
                health_summary[key] = {
                    "lane": stats["lane"],
                    "provider": stats["provider"],
                    "total_requests": stats["total_requests"],
                    "success_rate": success_rate,
                    "timeout_rate": timeout_rate,
                    "avg_latency_ms": avg_latency_ms,
                    "health_status": "healthy" if success_rate >= 0.95 and timeout_rate <= 0.05 else "unhealthy",
                    "auto_demotion_eligible": (1 - success_rate) >= self.auto_demotion_threshold
                }
            
            return health_summary
            
        except Exception as e:
            logger.error(f"Failed to get provider health summary: {e}")
            return {}
    
    def cleanup_old_events(self, max_age_hours: int = 24):
        """Clean up old events to prevent memory growth"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            original_count = len(self.events)
            self.events = [e for e in self.events if e.timestamp > cutoff_time]
            removed_count = original_count - len(self.events)
            
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} old fallback events")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old events: {e}")

# Global metrics collector instance
_metrics_collector: Optional[FallbackMetricsCollector] = None

def get_fallback_metrics() -> FallbackMetricsCollector:
    """Get the global fallback metrics collector"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = FallbackMetricsCollector()
    return _metrics_collector

def record_fallback_event(
    lane: str,
    provider: str,
    source: str,
    fallback_used: bool,
    timeout: bool = False,
    error: Optional[str] = None,
    latency_ms: float = 0.0,
    trace_id: Optional[str] = None
):
    """Convenience function to record a fallback event"""
    event = FallbackEvent(
        timestamp=datetime.utcnow(),
        lane=lane,
        provider=provider,
        source=source,
        fallback_used=fallback_used,
        timeout=timeout,
        error=error,
        latency_ms=latency_ms,
        trace_id=trace_id
    )
    
    collector = get_fallback_metrics()
    collector.record_fallback_event(event)
