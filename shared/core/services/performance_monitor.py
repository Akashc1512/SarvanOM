"""
Advanced Performance Monitor - Production-Grade Observability
============================================================

Provides comprehensive performance monitoring for production deployment:
- Real-time metrics collection and aggregation
- Performance anomaly detection  
- SLA monitoring and alerting
- Cost tracking and optimization recommendations
- User experience metrics (P50, P95, P99)

Maps to Phase E1 requirements for production observability.
"""

import os
import time
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import structlog
import json

logger = structlog.get_logger(__name__)


@dataclass
class MetricPoint:
    """Individual metric data point."""
    timestamp: float
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'timestamp': self.timestamp,
            'value': self.value,
            'labels': self.labels,
            'datetime': datetime.fromtimestamp(self.timestamp).isoformat()
        }


@dataclass
class PerformanceAlert:
    """Performance alert configuration and state."""
    metric_name: str
    threshold: float
    comparison: str  # 'gt', 'lt', 'eq'
    duration_seconds: int
    alert_active: bool = False
    last_triggered: Optional[float] = None
    trigger_count: int = 0
    
    def should_trigger(self, current_value: float, current_time: float) -> bool:
        """Check if alert should be triggered."""
        threshold_met = False
        
        if self.comparison == 'gt':
            threshold_met = current_value > self.threshold
        elif self.comparison == 'lt':
            threshold_met = current_value < self.threshold
        elif self.comparison == 'eq':
            threshold_met = abs(current_value - self.threshold) < 0.01
        
        # Check if threshold has been met for duration
        if threshold_met:
            if not self.alert_active:
                if self.last_triggered is None:
                    self.last_triggered = current_time
                elif current_time - self.last_triggered >= self.duration_seconds:
                    self.alert_active = True
                    self.trigger_count += 1
                    return True
        else:
            # Reset if threshold no longer met
            self.last_triggered = None
            self.alert_active = False
        
        return False


class PerformanceMonitor:
    """
    Advanced performance monitoring system for production deployment.
    
    Features:
    - Real-time metrics collection and time-series storage
    - Percentile calculations (P50, P95, P99)
    - SLA monitoring with configurable thresholds
    - Performance anomaly detection
    - Cost tracking and optimization recommendations
    - Comprehensive alerting system
    """
    
    def __init__(self, retention_hours: int = 24):
        """Initialize performance monitor."""
        self.retention_hours = retention_hours
        self.retention_seconds = retention_hours * 3600
        
        # Time-series storage (metric_name -> deque of MetricPoint)
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        
        # Performance targets and SLAs
        self.sla_targets = {
            'query_response_time_ms': 3000.0,  # 3s SLA
            'vector_search_time_ms': 2000.0,   # 2s SLA
            'retrieval_time_ms': 3000.0,       # 3s SLA
            'citations_time_ms': 2000.0,       # 2s SLA
            'success_rate': 0.95,              # 95% success rate
            'cache_hit_rate': 0.30,            # 30% cache hit rate
            'error_rate': 0.05                 # 5% error rate maximum
        }
        
        # Performance alerts
        self.alerts = [
            PerformanceAlert('query_response_time_ms', 5000.0, 'gt', 60),  # Alert if >5s for 1min
            PerformanceAlert('error_rate', 0.10, 'gt', 30),               # Alert if >10% errors for 30s
            PerformanceAlert('success_rate', 0.90, 'lt', 120),            # Alert if <90% success for 2min
            PerformanceAlert('vector_search_time_ms', 4000.0, 'gt', 60),  # Alert if >4s vector for 1min
        ]
        
        # Cost tracking
        self.cost_metrics = {
            'api_calls_total': 0,
            'api_calls_openai': 0,
            'api_calls_anthropic': 0,
            'api_calls_huggingface': 0,
            'estimated_cost_usd': 0.0,
            'tokens_consumed': 0
        }
        
        logger.info("PerformanceMonitor initialized", 
                   retention_hours=retention_hours,
                   sla_targets=len(self.sla_targets),
                   alerts_configured=len(self.alerts))
    
    def record_metric(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record a metric value with timestamp and labels."""
        current_time = time.time()
        labels = labels or {}
        
        point = MetricPoint(
            timestamp=current_time,
            value=value,
            labels=labels
        )
        
        self.metrics[metric_name].append(point)
        
        # Clean up old data
        self._cleanup_old_metrics(metric_name)
        
        # Check alerts
        self._check_alerts(metric_name, value, current_time)
        
        logger.debug("Metric recorded",
                    metric=metric_name,
                    value=value,
                    labels=labels)
    
    def _cleanup_old_metrics(self, metric_name: str) -> None:
        """Remove metrics older than retention period."""
        current_time = time.time()
        cutoff_time = current_time - self.retention_seconds
        
        metrics_deque = self.metrics[metric_name]
        while metrics_deque and metrics_deque[0].timestamp < cutoff_time:
            metrics_deque.popleft()
    
    def _check_alerts(self, metric_name: str, value: float, current_time: float) -> None:
        """Check if any alerts should be triggered."""
        for alert in self.alerts:
            if alert.metric_name == metric_name:
                if alert.should_trigger(value, current_time):
                    self._trigger_alert(alert, value, current_time)
    
    def _trigger_alert(self, alert: PerformanceAlert, value: float, current_time: float) -> None:
        """Trigger a performance alert."""
        alert_data = {
            'alert_name': f"{alert.metric_name}_{alert.comparison}_{alert.threshold}",
            'metric_name': alert.metric_name,
            'current_value': value,
            'threshold': alert.threshold,
            'comparison': alert.comparison,
            'trigger_count': alert.trigger_count,
            'timestamp': current_time,
            'datetime': datetime.fromtimestamp(current_time).isoformat()
        }
        
        logger.warning("Performance alert triggered", **alert_data)
        
        # In production, this would send alerts to monitoring systems
        # (Slack, PagerDuty, email, etc.)
    
    def get_percentiles(self, metric_name: str, percentiles: List[float] = [50, 95, 99]) -> Dict[str, float]:
        """Calculate percentiles for a metric over the retention period."""
        if metric_name not in self.metrics:
            return {f"p{int(p)}": 0.0 for p in percentiles}
        
        values = [point.value for point in self.metrics[metric_name]]
        if not values:
            return {f"p{int(p)}": 0.0 for p in percentiles}
        
        values.sort()
        result = {}
        
        for percentile in percentiles:
            index = int((percentile / 100.0) * len(values))
            if index >= len(values):
                index = len(values) - 1
            result[f"p{int(percentile)}"] = values[index]
        
        return result
    
    def get_sla_compliance(self) -> Dict[str, Any]:
        """Calculate SLA compliance for all monitored metrics."""
        compliance = {}
        
        for metric_name, target in self.sla_targets.items():
            if metric_name not in self.metrics:
                compliance[metric_name] = {
                    'target': target,
                    'compliance_rate': 0.0,
                    'total_measurements': 0,
                    'compliant_measurements': 0,
                    'status': 'no_data'
                }
                continue
            
            values = [point.value for point in self.metrics[metric_name]]
            if not values:
                continue
            
            total_count = len(values)
            
            # Determine compliance based on metric type
            if 'rate' in metric_name:
                # For rates, check if above target (higher is better)
                compliant_count = sum(1 for v in values if v >= target)
            else:
                # For times, check if below target (lower is better)
                compliant_count = sum(1 for v in values if v <= target)
            
            compliance_rate = compliant_count / total_count if total_count > 0 else 0.0
            
            status = 'compliant' if compliance_rate >= 0.95 else 'degraded' if compliance_rate >= 0.90 else 'failing'
            
            compliance[metric_name] = {
                'target': target,
                'compliance_rate': compliance_rate,
                'total_measurements': total_count,
                'compliant_measurements': compliant_count,
                'status': status,
                'percentiles': self.get_percentiles(metric_name)
            }
        
        return compliance
    
    def record_api_cost(self, provider: str, tokens: int, estimated_cost: float) -> None:
        """Record API usage and cost."""
        self.cost_metrics['api_calls_total'] += 1
        self.cost_metrics[f'api_calls_{provider.lower()}'] += 1
        self.cost_metrics['tokens_consumed'] += tokens
        self.cost_metrics['estimated_cost_usd'] += estimated_cost
        
        # Record as time series
        self.record_metric('api_cost_usd', estimated_cost, {'provider': provider})
        self.record_metric('tokens_used', tokens, {'provider': provider})
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost summary and optimization recommendations."""
        hourly_cost = 0.0
        if self.metrics.get('api_cost_usd'):
            recent_costs = [
                point.value for point in self.metrics['api_cost_usd']
                if point.timestamp > time.time() - 3600  # Last hour
            ]
            hourly_cost = sum(recent_costs)
        
        daily_projection = hourly_cost * 24
        monthly_projection = daily_projection * 30
        
        # Cost optimization recommendations
        recommendations = []
        
        if self.cost_metrics.get('api_calls_openai', 0) > self.cost_metrics.get('api_calls_huggingface', 0):
            recommendations.append("Consider routing more queries to HuggingFace for cost optimization")
        
        if hourly_cost > 1.0:  # $1/hour threshold
            recommendations.append("High API costs detected - review query complexity and caching")
        
        cache_hit_rate = self.get_latest_metric('cache_hit_rate')
        if cache_hit_rate and cache_hit_rate < 0.30:
            recommendations.append("Low cache hit rate - consider cache warming or TTL optimization")
        
        return {
            'current_metrics': self.cost_metrics,
            'hourly_cost_usd': round(hourly_cost, 4),
            'daily_projection_usd': round(daily_projection, 2),
            'monthly_projection_usd': round(monthly_projection, 2),
            'optimization_recommendations': recommendations,
            'cost_efficiency_score': min(1.0, (1.0 / max(hourly_cost, 0.01)))  # Higher is better
        }
    
    def get_latest_metric(self, metric_name: str) -> Optional[float]:
        """Get the most recent value for a metric."""
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return None
        return self.metrics[metric_name][-1].value
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary for monitoring dashboard."""
        current_time = time.time()
        
        # System health score (0-100)
        sla_compliance = self.get_sla_compliance()
        compliance_scores = [
            data['compliance_rate'] for data in sla_compliance.values()
            if data['total_measurements'] > 0
        ]
        health_score = (sum(compliance_scores) / len(compliance_scores) * 100) if compliance_scores else 0
        
        # Active alerts
        active_alerts = [
            {
                'metric': alert.metric_name,
                'threshold': alert.threshold,
                'trigger_count': alert.trigger_count
            }
            for alert in self.alerts if alert.alert_active
        ]
        
        # Performance overview
        key_metrics = {}
        for metric in ['query_response_time_ms', 'success_rate', 'error_rate', 'cache_hit_rate']:
            latest = self.get_latest_metric(metric)
            percentiles = self.get_percentiles(metric)
            key_metrics[metric] = {
                'latest': latest,
                'percentiles': percentiles,
                'sla_target': self.sla_targets.get(metric)
            }
        
        return {
            'timestamp': current_time,
            'health_score': round(health_score, 1),
            'sla_compliance': sla_compliance,
            'active_alerts': active_alerts,
            'key_metrics': key_metrics,
            'cost_summary': self.get_cost_summary(),
            'data_points_collected': sum(len(deque) for deque in self.metrics.values()),
            'metrics_tracked': len(self.metrics)
        }
    
    async def start_background_monitoring(self) -> None:
        """Start background monitoring tasks."""
        logger.info("Starting background performance monitoring")
        
        # This would typically include:
        # - Periodic metric aggregation
        # - Alert evaluation
        # - Data cleanup
        # - Export to external monitoring systems
        
        while True:
            try:
                # Cleanup old metrics every 5 minutes
                await asyncio.sleep(300)
                
                for metric_name in list(self.metrics.keys()):
                    self._cleanup_old_metrics(metric_name)
                
                logger.debug("Background cleanup completed",
                           metrics_tracked=len(self.metrics),
                           total_points=sum(len(deque) for deque in self.metrics.values()))
                
            except Exception as e:
                logger.error("Background monitoring error", error=str(e))
                await asyncio.sleep(60)  # Wait before retrying


# Global performance monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get or create global performance monitor."""
    global _performance_monitor
    
    if _performance_monitor is None:
        retention_hours = int(os.getenv('PERFORMANCE_MONITOR_RETENTION_HOURS', '24'))
        _performance_monitor = PerformanceMonitor(retention_hours=retention_hours)
    
    return _performance_monitor

def record_performance_metric(metric_name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
    """Convenience function to record a performance metric."""
    monitor = get_performance_monitor()
    monitor.record_metric(metric_name, value, labels)

def record_api_cost(provider: str, tokens: int, estimated_cost: float) -> None:
    """Convenience function to record API cost."""
    monitor = get_performance_monitor()
    monitor.record_api_cost(provider, tokens, estimated_cost)

def get_performance_summary() -> Dict[str, Any]:
    """Convenience function to get performance summary."""
    monitor = get_performance_monitor()
    return monitor.get_performance_summary()

# Export public interface
__all__ = [
    'PerformanceMonitor',
    'MetricPoint',
    'PerformanceAlert',
    'get_performance_monitor',
    'record_performance_metric',
    'record_api_cost',
    'get_performance_summary'
]
