"""
Metrics Utilities - SarvanOM v2

Utility functions for collecting and recording metrics across services.
"""

import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger()

class QueryMode(str, Enum):
    SIMPLE = "simple"
    TECHNICAL = "technical"
    RESEARCH = "research"
    MULTIMEDIA = "multimedia"

class LaneName(str, Enum):
    WEB_RETRIEVAL = "web_retrieval"
    VECTOR_SEARCH = "vector_search"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    KEYWORD_SEARCH = "keyword_search"
    NEWS_FEEDS = "news_feeds"
    MARKETS_FEEDS = "markets_feeds"
    LLM_SYNTHESIS = "llm_synthesis"
    FACT_CHECK = "fact_check"
    GUIDED_PROMPT = "guided_prompt"

@dataclass
class SLAMetrics:
    global_ms: float
    ttft_ms: float
    orchestrator_reserve_ms: float
    llm_ms: float
    web_ms: float
    vector_ms: float
    kg_ms: float
    yt_ms: float
    mode: QueryMode
    complexity: str

@dataclass
class LaneMetrics:
    lane_name: LaneName
    success_rate: float
    timeout_rate: float
    error_rate: float
    avg_time: float
    p95_time: float
    p99_time: float
    mode: QueryMode

@dataclass
class GuidedPromptMetrics:
    accept_rate: float
    edit_rate: float
    skip_rate: float
    ttfr_ms: float
    complaint_rate: float
    mode: QueryMode

class MetricsCollector:
    """Collect and aggregate metrics from services"""
    
    def __init__(self):
        self.sla_targets = {
            QueryMode.SIMPLE: {
                "global_ms": 5000,
                "ttft_ms": 1500,
                "orchestrator_reserve_ms": 500,
                "llm_ms": 1000,
                "web_ms": 1000,
                "vector_ms": 1000,
                "kg_ms": 1000,
                "yt_ms": 1000
            },
            QueryMode.TECHNICAL: {
                "global_ms": 7000,
                "ttft_ms": 1500,
                "orchestrator_reserve_ms": 700,
                "llm_ms": 1500,
                "web_ms": 1500,
                "vector_ms": 1500,
                "kg_ms": 1500,
                "yt_ms": 1500
            },
            QueryMode.RESEARCH: {
                "global_ms": 10000,
                "ttft_ms": 1500,
                "orchestrator_reserve_ms": 900,
                "llm_ms": 2000,
                "web_ms": 2000,
                "vector_ms": 2000,
                "kg_ms": 2000,
                "yt_ms": 2000
            },
            QueryMode.MULTIMEDIA: {
                "global_ms": 10000,
                "ttft_ms": 1500,
                "orchestrator_reserve_ms": 900,
                "llm_ms": 2000,
                "web_ms": 2000,
                "vector_ms": 2000,
                "kg_ms": 2000,
                "yt_ms": 2000
            }
        }
        
        # Metrics storage
        self.sla_metrics: List[SLAMetrics] = []
        self.lane_metrics: List[LaneMetrics] = []
        self.guided_prompt_metrics: List[GuidedPromptMetrics] = []
        self.cache_metrics: Dict[str, Dict[str, float]] = {}
        self.provider_health: Dict[str, Dict[str, float]] = {}
    
    def record_sla_metrics(self, metrics: SLAMetrics):
        """Record SLA metrics"""
        self.sla_metrics.append(metrics)
        
        # Check SLA violations
        targets = self.sla_targets.get(metrics.mode, {})
        violations = []
        
        for metric_name, value in metrics.__dict__.items():
            if metric_name in ["mode", "complexity"]:
                continue
            
            target = targets.get(metric_name, 0)
            if value > target:
                violations.append({
                    "metric": metric_name,
                    "value": value,
                    "target": target,
                    "violation_percent": ((value - target) / target) * 100
                })
        
        if violations:
            logger.warning(
                "SLA violations detected",
                mode=metrics.mode.value,
                complexity=metrics.complexity,
                violations=violations
            )
    
    def record_lane_metrics(self, metrics: LaneMetrics):
        """Record lane metrics"""
        self.lane_metrics.append(metrics)
        
        # Check for performance issues
        if metrics.success_rate < 0.95:
            logger.warning(
                "Low lane success rate",
                lane=metrics.lane_name.value,
                mode=metrics.mode.value,
                success_rate=metrics.success_rate
            )
        
        if metrics.timeout_rate > 0.05:
            logger.warning(
                "High lane timeout rate",
                lane=metrics.lane_name.value,
                mode=metrics.mode.value,
                timeout_rate=metrics.timeout_rate
            )
        
        if metrics.error_rate > 0.02:
            logger.warning(
                "High lane error rate",
                lane=metrics.lane_name.value,
                mode=metrics.mode.value,
                error_rate=metrics.error_rate
            )
    
    def record_guided_prompt_metrics(self, metrics: GuidedPromptMetrics):
        """Record Guided Prompt metrics"""
        self.guided_prompt_metrics.append(metrics)
        
        # Check Guided Prompt SLOs
        if metrics.accept_rate < 0.30:
            logger.warning(
                "Low Guided Prompt accept rate",
                mode=metrics.mode.value,
                accept_rate=metrics.accept_rate
            )
        
        if metrics.ttfr_ms > 800:
            logger.warning(
                "High Guided Prompt TTFR",
                mode=metrics.mode.value,
                ttfr_ms=metrics.ttfr_ms
            )
        
        if metrics.complaint_rate > 0.05:
            logger.warning(
                "High Guided Prompt complaint rate",
                mode=metrics.mode.value,
                complaint_rate=metrics.complaint_rate
            )
    
    def record_cache_metrics(self, cache_type: str, service: str, hit_rate: float):
        """Record cache metrics"""
        if cache_type not in self.cache_metrics:
            self.cache_metrics[cache_type] = {}
        
        self.cache_metrics[cache_type][service] = hit_rate
        
        if hit_rate < 0.80:
            logger.warning(
                "Low cache hit rate",
                cache_type=cache_type,
                service=service,
                hit_rate=hit_rate
            )
    
    def record_provider_health(self, provider: str, provider_type: str, health_status: float):
        """Record provider health metrics"""
        if provider not in self.provider_health:
            self.provider_health[provider] = {}
        
        self.provider_health[provider][provider_type] = health_status
        
        if health_status < 0.8:
            logger.warning(
                "Provider health degraded",
                provider=provider,
                provider_type=provider_type,
                health_status=health_status
            )
    
    def get_sla_compliance_rate(self, mode: QueryMode) -> float:
        """Calculate SLA compliance rate for a mode"""
        mode_metrics = [m for m in self.sla_metrics if m.mode == mode]
        if not mode_metrics:
            return 100.0
        
        targets = self.sla_targets.get(mode, {})
        compliant_count = 0
        
        for metrics in mode_metrics:
            is_compliant = True
            for metric_name, value in metrics.__dict__.items():
                if metric_name in ["mode", "complexity"]:
                    continue
                
                target = targets.get(metric_name, 0)
                if value > target:
                    is_compliant = False
                    break
            
            if is_compliant:
                compliant_count += 1
        
        return (compliant_count / len(mode_metrics)) * 100
    
    def get_lane_performance_summary(self, lane: LaneName) -> Dict[str, Any]:
        """Get performance summary for a lane"""
        lane_metrics = [m for m in self.lane_metrics if m.lane_name == lane]
        if not lane_metrics:
            return {}
        
        return {
            "avg_success_rate": sum(m.success_rate for m in lane_metrics) / len(lane_metrics),
            "avg_timeout_rate": sum(m.timeout_rate for m in lane_metrics) / len(lane_metrics),
            "avg_error_rate": sum(m.error_rate for m in lane_metrics) / len(lane_metrics),
            "avg_execution_time": sum(m.avg_time for m in lane_metrics) / len(lane_metrics),
            "p95_execution_time": max(m.p95_time for m in lane_metrics),
            "p99_execution_time": max(m.p99_time for m in lane_metrics),
            "total_requests": len(lane_metrics)
        }
    
    def get_guided_prompt_summary(self, mode: QueryMode) -> Dict[str, Any]:
        """Get Guided Prompt summary for a mode"""
        mode_metrics = [m for m in self.guided_prompt_metrics if m.mode == mode]
        if not mode_metrics:
            return {}
        
        return {
            "avg_accept_rate": sum(m.accept_rate for m in mode_metrics) / len(mode_metrics),
            "avg_edit_rate": sum(m.edit_rate for m in mode_metrics) / len(mode_metrics),
            "avg_skip_rate": sum(m.skip_rate for m in mode_metrics) / len(mode_metrics),
            "avg_ttfr_ms": sum(m.ttfr_ms for m in mode_metrics) / len(mode_metrics),
            "avg_complaint_rate": sum(m.complaint_rate for m in mode_metrics) / len(mode_metrics),
            "total_requests": len(mode_metrics)
        }
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        return {
            "sla_compliance": {
                mode.value: self.get_sla_compliance_rate(mode)
                for mode in QueryMode
            },
            "lane_performance": {
                lane.value: self.get_lane_performance_summary(lane)
                for lane in LaneName
            },
            "guided_prompt_performance": {
                mode.value: self.get_guided_prompt_summary(mode)
                for mode in QueryMode
            },
            "cache_performance": self.cache_metrics,
            "provider_health": self.provider_health
        }

class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, operation_name: str, labels: Dict[str, str] = None):
        self.operation_name = operation_name
        self.labels = labels or {}
        self.start_time = None
        self.duration = None
    
    def __enter__(self):
        """Start timing"""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and record metrics"""
        self.duration = time.time() - self.start_time
        
        logger.info(
            "Operation completed",
            operation=self.operation_name,
            duration=self.duration,
            labels=self.labels,
            success=exc_type is None,
            error=str(exc_val) if exc_val else None
        )
    
    def get_duration(self) -> float:
        """Get operation duration"""
        return self.duration or 0.0

def create_metrics_labels(**kwargs) -> Dict[str, str]:
    """Create standardized metrics labels"""
    return {k: str(v) for k, v in kwargs.items()}

def record_operation_metrics(operation_name: str, duration: float, success: bool, 
                           labels: Dict[str, str] = None, error: str = None):
    """Record operation metrics"""
    logger.info(
        "Operation metrics",
        operation=operation_name,
        duration=duration,
        success=success,
        labels=labels or {},
        error=error
    )
