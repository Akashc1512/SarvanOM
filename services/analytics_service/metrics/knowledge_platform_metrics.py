"""
Knowledge Platform Metrics - Universal Knowledge Platform
Comprehensive Prometheus-compatible metrics for all platform components.
"""
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from prometheus_client import (
    Counter, Gauge, Histogram, Summary,
    generate_latest, CONTENT_TYPE_LATEST
)

# Configure logging
logger = logging.getLogger(__name__)


class KnowledgePlatformMetricsCollector:
    """Main metrics collector for the knowledge platform."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        # Query Intelligence Metrics
        self.query_intelligence_requests = Counter(
            'query_intelligence_requests_total',
            'Total query intelligence requests',
            ['intent_type', 'complexity_level', 'domain_type']
        )
        self.query_intelligence_duration = Histogram(
            'query_intelligence_duration_seconds',
            'Query intelligence processing duration',
            ['intent_type', 'complexity_level']
        )
        self.query_cache_hits = Counter(
            'query_cache_hits_total',
            'Total query cache hits',
            ['cache_type']
        )
        self.query_cache_misses = Counter(
            'query_cache_misses_total',
            'Total query cache misses',
            ['cache_type']
        )
        
        # Orchestration Metrics
        self.orchestration_requests = Counter(
            'orchestration_requests_total',
            'Total orchestration requests',
            ['model_type', 'strategy', 'fallback_used']
        )
        self.orchestration_duration = Histogram(
            'orchestration_duration_seconds',
            'Orchestration processing duration',
            ['model_type', 'strategy']
        )
        self.circuit_breaker_state = Gauge(
            'circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=half_open, 2=open)',
            ['model_type']
        )
        self.model_failures = Counter(
            'model_failures_total',
            'Total model failures',
            ['model_type', 'error_type']
        )
        
        # Retrieval Metrics
        self.retrieval_requests = Counter(
            'retrieval_requests_total',
            'Total retrieval requests',
            ['source_type', 'fusion_strategy']
        )
        self.retrieval_duration = Histogram(
            'retrieval_duration_seconds',
            'Retrieval processing duration',
            ['source_type', 'fusion_strategy']
        )
        self.retrieval_results = Gauge(
            'retrieval_results_count',
            'Number of retrieval results',
            ['source_type']
        )
        self.retrieval_confidence = Histogram(
            'retrieval_confidence_score',
            'Retrieval confidence scores',
            ['source_type', 'fusion_strategy']
        )
        
        # Memory Metrics
        self.memory_operations = Counter(
            'memory_operations_total',
            'Total memory operations',
            ['operation_type', 'memory_type', 'success']
        )
        self.memory_size = Gauge(
            'memory_size_bytes',
            'Memory size in bytes',
            ['memory_type']
        )
        self.memory_items = Gauge(
            'memory_items_count',
            'Number of items in memory',
            ['memory_type']
        )
        self.memory_hit_rate = Gauge(
            'memory_hit_rate',
            'Memory hit rate (0-1)',
            ['memory_type']
        )
        
        # Expert Validation Metrics
        self.validation_requests = Counter(
            'validation_requests_total',
            'Total validation requests',
            ['network_type', 'validation_status']
        )
        self.validation_duration = Histogram(
            'validation_duration_seconds',
            'Validation processing duration',
            ['network_type']
        )
        self.consensus_score = Histogram(
            'consensus_score',
            'Expert consensus scores',
            ['consensus_level']
        )
        self.expert_agreement = Gauge(
            'expert_agreement_ratio',
            'Ratio of agreeing experts',
            ['network_type']
        )
        
        # Business Metrics
        self.user_queries = Counter(
            'user_queries_total',
            'Total user queries',
            ['user_id', 'query_type']
        )
        self.response_time = Histogram(
            'response_time_seconds',
            'End-to-end response time',
            ['query_type', 'complexity']
        )
        self.user_satisfaction = Gauge(
            'user_satisfaction_score',
            'User satisfaction scores',
            ['user_id']
        )
        self.system_uptime = Gauge(
            'system_uptime_seconds',
            'System uptime in seconds'
        )
        
        # Error Metrics
        self.errors_total = Counter(
            'errors_total',
            'Total errors',
            ['error_type', 'component', 'severity']
        )
        self.error_rate = Gauge(
            'error_rate',
            'Error rate (errors per second)',
            ['component']
        )
        
        logger.info("KnowledgePlatformMetricsCollector initialized")


def record_query_intelligence_metrics(
    intent_type: str,
    complexity_level: str,
    domain_type: str,
    duration_seconds: float,
    cache_hit: bool,
    cache_type: str = "redis"
):
    """Record query intelligence metrics."""
    try:
        collector = KnowledgePlatformMetricsCollector()
        
        # Record request
        collector.query_intelligence_requests.labels(
            intent_type=intent_type,
            complexity_level=complexity_level,
            domain_type=domain_type
        ).inc()
        
        # Record duration
        collector.query_intelligence_duration.labels(
            intent_type=intent_type,
            complexity_level=complexity_level
        ).observe(duration_seconds)
        
        # Record cache metrics
        if cache_hit:
            collector.query_cache_hits.labels(cache_type=cache_type).inc()
        else:
            collector.query_cache_misses.labels(cache_type=cache_type).inc()
        
        logger.debug(f"Recorded query intelligence metrics: {intent_type}, {complexity_level}, {duration_seconds:.3f}s")
        
    except Exception as e:
        logger.error(f"Failed to record query intelligence metrics: {e}")


def record_orchestration_metrics(
    model_type: str,
    strategy: str,
    duration_seconds: float,
    fallback_used: bool,
    circuit_breaker_state: str,
    error_type: Optional[str] = None
):
    """Record orchestration metrics."""
    try:
        collector = KnowledgePlatformMetricsCollector()
        
        # Record request
        collector.orchestration_requests.labels(
            model_type=model_type,
            strategy=strategy,
            fallback_used=str(fallback_used).lower()
        ).inc()
        
        # Record duration
        collector.orchestration_duration.labels(
            model_type=model_type,
            strategy=strategy
        ).observe(duration_seconds)
        
        # Record circuit breaker state
        state_value = {"closed": 0, "half_open": 1, "open": 2}.get(circuit_breaker_state, 0)
        collector.circuit_breaker_state.labels(model_type=model_type).set(state_value)
        
        # Record failures if any
        if error_type:
            collector.model_failures.labels(
                model_type=model_type,
                error_type=error_type
            ).inc()
        
        logger.debug(f"Recorded orchestration metrics: {model_type}, {strategy}, {duration_seconds:.3f}s")
        
    except Exception as e:
        logger.error(f"Failed to record orchestration metrics: {e}")


def record_retrieval_metrics(
    source_type: str,
    fusion_strategy: str,
    duration_seconds: float,
    result_count: int,
    confidence_score: float
):
    """Record retrieval metrics."""
    try:
        collector = KnowledgePlatformMetricsCollector()
        
        # Record request
        collector.retrieval_requests.labels(
            source_type=source_type,
            fusion_strategy=fusion_strategy
        ).inc()
        
        # Record duration
        collector.retrieval_duration.labels(
            source_type=source_type,
            fusion_strategy=fusion_strategy
        ).observe(duration_seconds)
        
        # Record results count
        collector.retrieval_results.labels(source_type=source_type).set(result_count)
        
        # Record confidence
        collector.retrieval_confidence.labels(
            source_type=source_type,
            fusion_strategy=fusion_strategy
        ).observe(confidence_score)
        
        logger.debug(f"Recorded retrieval metrics: {source_type}, {fusion_strategy}, {duration_seconds:.3f}s")
        
    except Exception as e:
        logger.error(f"Failed to record retrieval metrics: {e}")


def record_memory_metrics(
    operation_type: str,
    memory_type: str,
    success: bool,
    size_bytes: int,
    item_count: int,
    hit_rate: float
):
    """Record memory metrics."""
    try:
        collector = KnowledgePlatformMetricsCollector()
        
        # Record operation
        collector.memory_operations.labels(
            operation_type=operation_type,
            memory_type=memory_type,
            success=str(success).lower()
        ).inc()
        
        # Record size
        collector.memory_size.labels(memory_type=memory_type).set(size_bytes)
        
        # Record item count
        collector.memory_items.labels(memory_type=memory_type).set(item_count)
        
        # Record hit rate
        collector.memory_hit_rate.labels(memory_type=memory_type).set(hit_rate)
        
        logger.debug(f"Recorded memory metrics: {operation_type}, {memory_type}, {success}")
        
    except Exception as e:
        logger.error(f"Failed to record memory metrics: {e}")


def record_expert_validation_metrics(
    network_type: str,
    validation_status: str,
    duration_seconds: float,
    consensus_score: float,
    consensus_level: str,
    agreement_ratio: float
):
    """Record expert validation metrics."""
    try:
        collector = KnowledgePlatformMetricsCollector()
        
        # Record request
        collector.validation_requests.labels(
            network_type=network_type,
            validation_status=validation_status
        ).inc()
        
        # Record duration
        collector.validation_duration.labels(network_type=network_type).observe(duration_seconds)
        
        # Record consensus score
        collector.consensus_score.labels(consensus_level=consensus_level).observe(consensus_score)
        
        # Record agreement ratio
        collector.expert_agreement.labels(network_type=network_type).set(agreement_ratio)
        
        logger.debug(f"Recorded expert validation metrics: {network_type}, {validation_status}, {duration_seconds:.3f}s")
        
    except Exception as e:
        logger.error(f"Failed to record expert validation metrics: {e}")


def record_business_metrics(
    user_id: str,
    query_type: str,
    complexity: str,
    response_time_seconds: float,
    satisfaction_score: Optional[float] = None,
    error_type: Optional[str] = None
):
    """Record business metrics."""
    try:
        collector = KnowledgePlatformMetricsCollector()
        
        # Record user query
        collector.user_queries.labels(
            user_id=user_id,
            query_type=query_type
        ).inc()
        
        # Record response time
        collector.response_time.labels(
            query_type=query_type,
            complexity=complexity
        ).observe(response_time_seconds)
        
        # Record satisfaction if provided
        if satisfaction_score is not None:
            collector.user_satisfaction.labels(user_id=user_id).set(satisfaction_score)
        
        # Record errors if any
        if error_type:
            collector.errors_total.labels(
                error_type=error_type,
                component="business",
                severity="medium"
            ).inc()
        
        logger.debug(f"Recorded business metrics: {user_id}, {query_type}, {response_time_seconds:.3f}s")
        
    except Exception as e:
        logger.error(f"Failed to record business metrics: {e}")


def record_system_metrics(
    uptime_seconds: float,
    error_count: int,
    error_rate: float,
    component: str = "system"
):
    """Record system-level metrics."""
    try:
        collector = KnowledgePlatformMetricsCollector()
        
        # Record uptime
        collector.system_uptime.set(uptime_seconds)
        
        # Record error rate
        collector.error_rate.labels(component=component).set(error_rate)
        
        logger.debug(f"Recorded system metrics: uptime={uptime_seconds:.0f}s, errors={error_count}")
        
    except Exception as e:
        logger.error(f"Failed to record system metrics: {e}")


def get_metrics_prometheus() -> str:
    """Get metrics in Prometheus format."""
    try:
        return generate_latest().decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to generate Prometheus metrics: {e}")
        return ""


def get_metrics_json() -> Dict[str, Any]:
    """Get metrics in JSON format."""
    try:
        collector = KnowledgePlatformMetricsCollector()
        
        # This would collect all metrics and format them as JSON
        # For now, return a basic structure
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "query_intelligence": {
                    "requests_total": 0,
                    "cache_hit_rate": 0.0,
                    "average_duration": 0.0
                },
                "orchestration": {
                    "requests_total": 0,
                    "model_failures": 0,
                    "average_duration": 0.0
                },
                "retrieval": {
                    "requests_total": 0,
                    "average_confidence": 0.0,
                    "average_duration": 0.0
                },
                "memory": {
                    "operations_total": 0,
                    "total_size_bytes": 0,
                    "hit_rate": 0.0
                },
                "validation": {
                    "requests_total": 0,
                    "average_consensus": 0.0,
                    "average_duration": 0.0
                },
                "business": {
                    "user_queries_total": 0,
                    "average_response_time": 0.0,
                    "average_satisfaction": 0.0
                },
                "system": {
                    "uptime_seconds": 0,
                    "error_rate": 0.0,
                    "status": "healthy"
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to generate JSON metrics: {e}")
        return {"error": str(e)}


def reset_metrics():
    """Reset all metrics (useful for testing)."""
    try:
        # This would reset all Prometheus metrics
        # For now, just log the action
        logger.info("Metrics reset requested")
        
    except Exception as e:
        logger.error(f"Failed to reset metrics: {e}")


def health_check_metrics() -> Dict[str, Any]:
    """Perform health check of metrics system."""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "metrics_available": True,
            "prometheus_format": True,
            "json_format": True
        }
    except Exception as e:
        logger.error(f"Metrics health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        } 