"""
Metrics Router for SarvanOM Gateway

This module provides a centralized metrics endpoint that exposes Prometheus-compatible
metrics for monitoring and observability. It integrates with the existing metrics
collection system and provides a single source of truth for system metrics.

Following MAANG/OpenAI/Perplexity standards for observability and monitoring.
"""

import time
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import logging

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import PlainTextResponse

from shared.core.logging import get_logger
from services.gateway.model_router import get_model_router

logger = get_logger(__name__)

# Create metrics router
metrics_router = APIRouter(prefix="/metrics", tags=["metrics"])


@dataclass
class MetricValue:
    """Individual metric value with metadata."""
    name: str
    value: float
    labels: Dict[str, str]
    timestamp: float
    help_text: str
    metric_type: str  # counter, gauge, histogram, summary


class MetricsCollector:
    """
    Centralized metrics collector that aggregates metrics from various sources
    and formats them for Prometheus consumption.
    """
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.start_time = time.time()
        self.metrics: Dict[str, MetricValue] = {}
        self.model_router = get_model_router()
        
    def collect_system_metrics(self) -> List[MetricValue]:
        """Collect system-level metrics."""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        metrics = [
            MetricValue(
                name="sarvanom_gateway_uptime_seconds",
                value=uptime,
                labels={},
                timestamp=current_time,
                help_text="Total uptime of the SarvanOM gateway service in seconds",
                metric_type="gauge"
            ),
            MetricValue(
                name="sarvanom_gateway_start_time_seconds",
                value=self.start_time,
                labels={},
                timestamp=current_time,
                help_text="Start time of the SarvanOM gateway service as Unix timestamp",
                metric_type="gauge"
            )
        ]
        
        return metrics
    
    def collect_model_metrics(self) -> List[MetricValue]:
        """Collect model selection and usage metrics."""
        current_time = time.time()
        stats = self.model_router.get_selection_stats()
        available_models = self.model_router.get_available_models()
        
        metrics = []
        
        # Total model selections
        metrics.append(MetricValue(
            name="sarvanom_model_selections_total",
            value=stats.get("total_selections", 0),
            labels={},
            timestamp=current_time,
            help_text="Total number of model selections made",
            metric_type="counter"
        ))
        
        # Total estimated cost
        metrics.append(MetricValue(
            name="sarvanom_model_cost_total",
            value=stats.get("total_estimated_cost", 0.0),
            labels={},
            timestamp=current_time,
            help_text="Total estimated cost of model selections in USD",
            metric_type="counter"
        ))
        
        # Average cost per selection
        metrics.append(MetricValue(
            name="sarvanom_model_cost_average",
            value=stats.get("average_cost_per_selection", 0.0),
            labels={},
            timestamp=current_time,
            help_text="Average cost per model selection in USD",
            metric_type="gauge"
        ))
        
        # Model distribution
        model_dist = stats.get("model_distribution", {})
        for model_name, count in model_dist.items():
            metrics.append(MetricValue(
                name="sarvanom_model_selections_by_model",
                value=count,
                labels={"model": model_name},
                timestamp=current_time,
                help_text="Number of selections by model name",
                metric_type="counter"
            ))
        
        # Provider distribution
        provider_dist = stats.get("provider_distribution", {})
        for provider, count in provider_dist.items():
            metrics.append(MetricValue(
                name="sarvanom_model_selections_by_provider",
                value=count,
                labels={"provider": provider},
                timestamp=current_time,
                help_text="Number of selections by provider",
                metric_type="counter"
            ))
        
        # Tier distribution
        tier_dist = stats.get("tier_distribution", {})
        for tier, count in tier_dist.items():
            metrics.append(MetricValue(
                name="sarvanom_model_selections_by_tier",
                value=count,
                labels={"tier": tier},
                timestamp=current_time,
                help_text="Number of selections by performance tier",
                metric_type="counter"
            ))
        
        # Available models count
        metrics.append(MetricValue(
            name="sarvanom_models_available",
            value=len(available_models),
            labels={},
            timestamp=current_time,
            help_text="Number of available models",
            metric_type="gauge"
        ))
        
        return metrics
    
    def collect_health_metrics(self) -> List[MetricValue]:
        """Collect health and status metrics."""
        current_time = time.time()
        
        # TODO: Integrate with actual health check results
        # For now, return basic health metrics
        metrics = [
            MetricValue(
                name="sarvanom_gateway_health_status",
                value=1.0,  # 1 = healthy, 0 = unhealthy
                labels={"service": "gateway"},
                timestamp=current_time,
                help_text="Health status of the gateway service (1=healthy, 0=unhealthy)",
                metric_type="gauge"
            ),
            MetricValue(
                name="sarvanom_gateway_ready_status",
                value=1.0,  # 1 = ready, 0 = not ready
                labels={"service": "gateway"},
                timestamp=current_time,
                help_text="Readiness status of the gateway service (1=ready, 0=not ready)",
                metric_type="gauge"
            )
        ]
        
        return metrics
    
    def collect_configuration_metrics(self) -> List[MetricValue]:
        """Collect configuration and feature flag metrics."""
        current_time = time.time()
        
        # TODO: Integrate with actual configuration values
        # For now, return basic configuration metrics
        metrics = [
            MetricValue(
                name="sarvanom_config_model_selection_enabled",
                value=1.0,  # 1 = enabled, 0 = disabled
                labels={},
                timestamp=current_time,
                help_text="Whether model selection is enabled (1=enabled, 0=disabled)",
                metric_type="gauge"
            ),
            MetricValue(
                name="sarvanom_config_cost_optimization_enabled",
                value=1.0,  # 1 = enabled, 0 = disabled
                labels={},
                timestamp=current_time,
                help_text="Whether cost optimization is enabled (1=enabled, 0=disabled)",
                metric_type="gauge"
            )
        ]
        
        return metrics
    
    def collect_all_metrics(self) -> List[MetricValue]:
        """Collect all available metrics."""
        all_metrics = []
        
        try:
            all_metrics.extend(self.collect_system_metrics())
            all_metrics.extend(self.collect_model_metrics())
            all_metrics.extend(self.collect_health_metrics())
            all_metrics.extend(self.collect_configuration_metrics())
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
        
        return all_metrics
    
    def format_prometheus_metrics(self, metrics: List[MetricValue]) -> str:
        """Format metrics in Prometheus exposition format."""
        lines = []
        
        # Group metrics by name
        metric_groups = {}
        for metric in metrics:
            if metric.name not in metric_groups:
                metric_groups[metric.name] = []
            metric_groups[metric.name].append(metric)
        
        # Format each metric group
        for metric_name, metric_list in metric_groups.items():
            # Add help text (use the first metric's help text)
            if metric_list:
                lines.append(f"# HELP {metric_name} {metric_list[0].help_text}")
                lines.append(f"# TYPE {metric_name} {metric_list[0].metric_type}")
            
            # Add metric values
            for metric in metric_list:
                if metric.labels:
                    # Format labels
                    label_pairs = [f'{k}="{v}"' for k, v in metric.labels.items()]
                    labels_str = "{" + ",".join(label_pairs) + "}"
                    lines.append(f"{metric_name}{labels_str} {metric.value}")
                else:
                    lines.append(f"{metric_name} {metric.value}")
            
            lines.append("")  # Empty line between metric groups
        
        return "\n".join(lines)


# Global metrics collector instance
metrics_collector = MetricsCollector()


@metrics_router.get("/", response_class=PlainTextResponse)
async def get_metrics():
    """
    Get Prometheus-compatible metrics.
    
    This endpoint provides a single source of truth for all system metrics
    in Prometheus exposition format.
    """
    try:
        # Collect all metrics
        all_metrics = metrics_collector.collect_all_metrics()
        
        # Format for Prometheus
        prometheus_format = metrics_collector.format_prometheus_metrics(all_metrics)
        
        logger.debug(f"Exported {len(all_metrics)} metrics")
        
        return prometheus_format
        
    except Exception as e:
        logger.error(f"Failed to collect metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics collection failed: {str(e)}")


@metrics_router.get("/health")
async def get_metrics_health():
    """Get health status of the metrics system."""
    try:
        # Test metrics collection
        test_metrics = metrics_collector.collect_system_metrics()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics_collected": len(test_metrics),
            "uptime_seconds": time.time() - metrics_collector.start_time
        }
        
    except Exception as e:
        logger.error(f"Metrics health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }


@metrics_router.get("/summary")
async def get_metrics_summary():
    """Get a summary of available metrics."""
    try:
        all_metrics = metrics_collector.collect_all_metrics()
        
        # Group by metric type
        by_type = {}
        by_name = {}
        
        for metric in all_metrics:
            metric_type = metric.metric_type
            metric_name = metric.name
            
            if metric_type not in by_type:
                by_type[metric_type] = 0
            by_type[metric_type] += 1
            
            if metric_name not in by_name:
                by_name[metric_name] = {
                    "type": metric_type,
                    "help": metric.help_text,
                    "count": 0
                }
            by_name[metric_name]["count"] += 1
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_metrics": len(all_metrics),
            "unique_metric_names": len(by_name),
            "metrics_by_type": by_type,
            "metric_details": by_name
        }
        
    except Exception as e:
        logger.error(f"Failed to get metrics summary: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics summary failed: {str(e)}")


@metrics_router.get("/model-stats")
async def get_model_metrics():
    """Get detailed model selection metrics."""
    try:
        model_router = get_model_router()
        stats = model_router.get_selection_stats()
        available_models = model_router.get_available_models()
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "selection_stats": stats,
            "available_models": available_models,
            "total_available_models": len(available_models)
        }
        
    except Exception as e:
        logger.error(f"Failed to get model metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Model metrics failed: {str(e)}")


# TODO: Add integration with existing analytics metrics
# TODO: Add custom metric registration API
# TODO: Add metric aggregation and rollup
# TODO: Add alerting rules integration
# TODO: Add metric retention and cleanup
