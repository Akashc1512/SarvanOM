"""
Observability Service - SarvanOM v2

Wire metrics, tracing and dashboards as per docs/observability/*:
Emit all metrics (E2E, TTFT, lane timeouts, cache hit %, RRF time, provider health).
Add Guided Prompt KPIs and SLOs.
Trace-ID propagation end-to-end (frontend → gateway → lanes → providers).
Dashboard JSON/config per docs (no screenshots needed).
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel, Field
import httpx
import redis
from prometheus_client import Counter, Histogram, Gauge, start_http_server, generate_latest
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger()

# Prometheus metrics
sla_global_ms = Histogram('sarvanom_sla_global_ms', 'Global response time', ['mode', 'complexity'])
sla_ttft_ms = Histogram('sarvanom_sla_ttft_ms', 'Time to first token', ['mode', 'complexity'])
sla_orchestrator_reserve_ms = Histogram('sarvanom_sla_orchestrator_reserve_ms', 'Orchestrator reserve time', ['mode', 'complexity'])
sla_llm_ms = Histogram('sarvanom_sla_llm_ms', 'LLM processing time', ['mode', 'complexity'])
sla_web_ms = Histogram('sarvanom_sla_web_ms', 'Web retrieval time', ['mode', 'complexity'])
sla_vector_ms = Histogram('sarvanom_sla_vector_ms', 'Vector search time', ['mode', 'complexity'])
sla_kg_ms = Histogram('sarvanom_sla_kg_ms', 'Knowledge graph time', ['mode', 'complexity'])
sla_yt_ms = Histogram('sarvanom_sla_yt_ms', 'YouTube processing time', ['mode', 'complexity'])

lane_success_rate = Gauge('sarvanom_lane_success_rate', 'Lane success rate', ['lane', 'mode'])
lane_timeout_rate = Gauge('sarvanom_lane_timeout_rate', 'Lane timeout rate', ['lane', 'mode'])
lane_error_rate = Gauge('sarvanom_lane_error_rate', 'Lane error rate', ['lane', 'mode'])
lane_avg_time = Histogram('sarvanom_lane_avg_time', 'Average lane time', ['lane', 'mode'])
lane_p95_time = Histogram('sarvanom_lane_p95_time', '95th percentile lane time', ['lane', 'mode'])
lane_p99_time = Histogram('sarvanom_lane_p99_time', '99th percentile lane time', ['lane', 'mode'])

cache_hit_rate = Gauge('sarvanom_cache_hit_rate', 'Cache hit rate', ['cache_type', 'service'])
rrf_fusion_time = Histogram('sarvanom_rrf_fusion_time_ms', 'RRF fusion time', ['mode'])
provider_health = Gauge('sarvanom_provider_health', 'Provider health status', ['provider', 'type'])

guided_prompt_accept_rate = Gauge('sarvanom_guided_prompt_accept_rate', 'Guided prompt accept rate', ['mode'])
guided_prompt_edit_rate = Gauge('sarvanom_guided_prompt_edit_rate', 'Guided prompt edit rate', ['mode'])
guided_prompt_skip_rate = Gauge('sarvanom_guided_prompt_skip_rate', 'Guided prompt skip rate', ['mode'])
guided_prompt_ttfr_ms = Histogram('sarvanom_guided_prompt_ttfr_ms', 'Guided prompt time to first refinement', ['mode'])
guided_prompt_complaint_rate = Gauge('sarvanom_guided_prompt_complaint_rate', 'Guided prompt complaint rate', ['mode'])

trace_requests_total = Counter('sarvanom_trace_requests_total', 'Total traced requests', ['service', 'endpoint', 'status'])
trace_duration = Histogram('sarvanom_trace_duration_seconds', 'Trace duration', ['service', 'endpoint'])
trace_errors_total = Counter('sarvanom_trace_errors_total', 'Total trace errors', ['service', 'endpoint', 'error_type'])

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
class TraceContext:
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    service_name: str = ""
    request_id: str = ""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    start_time: float = 0.0
    attributes: Dict[str, Any] = None

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

class TracePropagation:
    """Trace-ID propagation and management"""
    
    def __init__(self):
        self.trace_id = None
        self.span_id = None
        self.parent_span_id = None
        self.service_name = None
        self.request_id = None
    
    def start_trace(self, service_name: str, request_id: str = None) -> TraceContext:
        """Start new trace"""
        if request_id is None:
            request_id = str(uuid.uuid4())
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = ''.join([str(uuid.uuid4()).replace('-', '')[:12]])
        
        self.trace_id = f"{service_name}-{timestamp}-{random_suffix}"
        self.span_id = str(uuid.uuid4()).replace('-', '')[:12]
        self.parent_span_id = None
        self.service_name = service_name
        self.request_id = request_id
        
        return TraceContext(
            trace_id=self.trace_id,
            span_id=self.span_id,
            parent_span_id=self.parent_span_id,
            service_name=service_name,
            request_id=request_id,
            start_time=time.time()
        )
    
    def create_span(self, parent_context: TraceContext, span_name: str, attributes: Dict[str, Any] = None) -> TraceContext:
        """Create child span"""
        if attributes is None:
            attributes = {}
        
        new_span_id = str(uuid.uuid4()).replace('-', '')[:12]
        
        return TraceContext(
            trace_id=parent_context.trace_id,
            span_id=new_span_id,
            parent_span_id=parent_context.span_id,
            service_name=parent_context.service_name,
            request_id=parent_context.request_id,
            user_id=parent_context.user_id,
            session_id=parent_context.session_id,
            start_time=time.time(),
            attributes=attributes
        )
    
    def extract_trace_headers(self, request: Request) -> Optional[TraceContext]:
        """Extract trace context from request headers"""
        trace_id = request.headers.get("X-Trace-ID")
        span_id = request.headers.get("X-Span-ID")
        parent_span_id = request.headers.get("X-Parent-Span-ID")
        service_name = request.headers.get("X-Service-Name")
        request_id = request.headers.get("X-Request-ID")
        
        if not trace_id or not span_id:
            return None
        
        return TraceContext(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            service_name=service_name or "unknown",
            request_id=request_id or str(uuid.uuid4()),
            start_time=time.time()
        )
    
    def inject_trace_headers(self, context: TraceContext) -> Dict[str, str]:
        """Inject trace context into headers"""
        return {
            "X-Trace-ID": context.trace_id,
            "X-Span-ID": context.span_id,
            "X-Parent-Span-ID": context.parent_span_id or "",
            "X-Service-Name": context.service_name,
            "X-Request-ID": context.request_id
        }

class MetricsCollector:
    """Collect and record metrics"""
    
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
    
    def record_sla_metrics(self, metrics: SLAMetrics):
        """Record SLA metrics"""
        mode = metrics.mode.value
        complexity = metrics.complexity
        
        # Record global metrics
        sla_global_ms.labels(mode=mode, complexity=complexity).observe(metrics.global_ms)
        sla_ttft_ms.labels(mode=mode, complexity=complexity).observe(metrics.ttft_ms)
        sla_orchestrator_reserve_ms.labels(mode=mode, complexity=complexity).observe(metrics.orchestrator_reserve_ms)
        sla_llm_ms.labels(mode=mode, complexity=complexity).observe(metrics.llm_ms)
        sla_web_ms.labels(mode=mode, complexity=complexity).observe(metrics.web_ms)
        sla_vector_ms.labels(mode=mode, complexity=complexity).observe(metrics.vector_ms)
        sla_kg_ms.labels(mode=mode, complexity=complexity).observe(metrics.kg_ms)
        sla_yt_ms.labels(mode=mode, complexity=complexity).observe(metrics.yt_ms)
        
        # Check SLA violations
        targets = self.sla_targets.get(metrics.mode, {})
        for metric_name, value in asdict(metrics).items():
            if metric_name == "mode" or metric_name == "complexity":
                continue
            
            target = targets.get(metric_name, 0)
            if value > target:
                logger.warning(
                    "SLA violation detected",
                    metric=metric_name,
                    value=value,
                    target=target,
                    mode=mode,
                    complexity=complexity
                )
    
    def record_lane_metrics(self, metrics: LaneMetrics):
        """Record lane metrics"""
        lane = metrics.lane_name.value
        mode = metrics.mode.value
        
        lane_success_rate.labels(lane=lane, mode=mode).set(metrics.success_rate)
        lane_timeout_rate.labels(lane=lane, mode=mode).set(metrics.timeout_rate)
        lane_error_rate.labels(lane=lane, mode=mode).set(metrics.error_rate)
        lane_avg_time.labels(lane=lane, mode=mode).observe(metrics.avg_time)
        lane_p95_time.labels(lane=lane, mode=mode).observe(metrics.p95_time)
        lane_p99_time.labels(lane=lane, mode=mode).observe(metrics.p99_time)
    
    def record_guided_prompt_metrics(self, metrics: GuidedPromptMetrics):
        """Record Guided Prompt metrics"""
        mode = metrics.mode.value
        
        guided_prompt_accept_rate.labels(mode=mode).set(metrics.accept_rate)
        guided_prompt_edit_rate.labels(mode=mode).set(metrics.edit_rate)
        guided_prompt_skip_rate.labels(mode=mode).set(metrics.skip_rate)
        guided_prompt_ttfr_ms.labels(mode=mode).observe(metrics.ttfr_ms)
        guided_prompt_complaint_rate.labels(mode=mode).set(metrics.complaint_rate)
    
    def record_cache_metrics(self, cache_type: str, service: str, hit_rate: float):
        """Record cache metrics"""
        cache_hit_rate.labels(cache_type=cache_type, service=service).set(hit_rate)
    
    def record_rrf_metrics(self, mode: QueryMode, fusion_time_ms: float):
        """Record RRF fusion metrics"""
        rrf_fusion_time.labels(mode=mode.value).observe(fusion_time_ms)
    
    def record_provider_health(self, provider: str, provider_type: str, health_status: float):
        """Record provider health metrics"""
        provider_health.labels(provider=provider, type=provider_type).set(health_status)
    
    def record_trace_metrics(self, service: str, endpoint: str, status: str, duration: float, error_type: str = None):
        """Record trace metrics"""
        trace_requests_total.labels(service=service, endpoint=endpoint, status=status).inc()
        trace_duration.labels(service=service, endpoint=endpoint).observe(duration)
        
        if error_type:
            trace_errors_total.labels(service=service, endpoint=endpoint, error_type=error_type).inc()

class DashboardGenerator:
    """Generate dashboard configurations"""
    
    def __init__(self):
        self.dashboard_configs = {}
    
    def generate_system_health_dashboard(self) -> Dict[str, Any]:
        """Generate system health dashboard configuration"""
        return {
            "title": "SarvanOM v2 - System Health",
            "refresh_rate": 30,
            "layout": {
                "rows": [
                    {
                        "title": "Service Status Grid",
                        "type": "grid",
                        "size": "large",
                        "tiles": [
                            {
                                "title": "API Gateway",
                                "type": "status",
                                "metric": "sarvanom_service_health",
                                "labels": {"service": "api-gateway"},
                                "thresholds": {"healthy": 1, "degraded": 0.5, "down": 0}
                            },
                            {
                                "title": "Auth Service",
                                "type": "status",
                                "metric": "sarvanom_service_health",
                                "labels": {"service": "auth"},
                                "thresholds": {"healthy": 1, "degraded": 0.5, "down": 0}
                            },
                            {
                                "title": "Search Service",
                                "type": "status",
                                "metric": "sarvanom_service_health",
                                "labels": {"service": "search"},
                                "thresholds": {"healthy": 1, "degraded": 0.5, "down": 0}
                            },
                            {
                                "title": "Synthesis Service",
                                "type": "status",
                                "metric": "sarvanom_service_health",
                                "labels": {"service": "synthesis"},
                                "thresholds": {"healthy": 1, "degraded": 0.5, "down": 0}
                            }
                        ]
                    },
                    {
                        "title": "System Metrics",
                        "type": "row",
                        "tiles": [
                            {
                                "title": "Uptime",
                                "type": "gauge",
                                "metric": "sarvanom_system_uptime",
                                "thresholds": {"warning": 99.9, "critical": 99.0}
                            },
                            {
                                "title": "Response Time",
                                "type": "histogram",
                                "metric": "sarvanom_sla_global_ms",
                                "thresholds": {"warning": 5000, "critical": 10000}
                            },
                            {
                                "title": "Error Rate",
                                "type": "gauge",
                                "metric": "sarvanom_error_rate",
                                "thresholds": {"warning": 1.0, "critical": 5.0}
                            },
                            {
                                "title": "Active Users",
                                "type": "gauge",
                                "metric": "sarvanom_active_users",
                                "thresholds": {"warning": 1000, "critical": 2000}
                            }
                        ]
                    }
                ]
            },
            "alerts": [
                {
                    "name": "Service Down",
                    "condition": "sarvanom_service_health == 0",
                    "severity": "critical",
                    "notification": ["slack", "email", "pagerduty"]
                },
                {
                    "name": "High Error Rate",
                    "condition": "sarvanom_error_rate > 5%",
                    "severity": "critical",
                    "notification": ["slack", "email"]
                },
                {
                    "name": "Slow Response Time",
                    "condition": "sarvanom_sla_global_ms > 10s",
                    "severity": "warning",
                    "notification": ["slack"]
                }
            ]
        }
    
    def generate_performance_dashboard(self) -> Dict[str, Any]:
        """Generate performance dashboard configuration"""
        return {
            "title": "SarvanOM v2 - Performance",
            "refresh_rate": 60,
            "layout": {
                "rows": [
                    {
                        "title": "SLA Compliance",
                        "type": "row",
                        "tiles": [
                            {
                                "title": "SLA Compliance Rate",
                                "type": "gauge",
                                "metric": "sarvanom_sla_compliance_rate",
                                "thresholds": {"warning": 95.0, "critical": 90.0}
                            },
                            {
                                "title": "TTFT",
                                "type": "histogram",
                                "metric": "sarvanom_sla_ttft_ms",
                                "thresholds": {"warning": 1500, "critical": 2000}
                            },
                            {
                                "title": "Budget Usage",
                                "type": "gauge",
                                "metric": "sarvanom_budget_usage_percent",
                                "thresholds": {"warning": 80.0, "critical": 95.0}
                            }
                        ]
                    },
                    {
                        "title": "Lane Performance",
                        "type": "grid",
                        "size": "large",
                        "tiles": [
                            {
                                "title": "Web Retrieval",
                                "type": "histogram",
                                "metric": "sarvanom_sla_web_ms",
                                "labels": {"lane": "web_retrieval"},
                                "thresholds": {"warning": 1000, "critical": 2000}
                            },
                            {
                                "title": "Vector Search",
                                "type": "histogram",
                                "metric": "sarvanom_sla_vector_ms",
                                "labels": {"lane": "vector_search"},
                                "thresholds": {"warning": 1000, "critical": 2000}
                            },
                            {
                                "title": "Knowledge Graph",
                                "type": "histogram",
                                "metric": "sarvanom_sla_kg_ms",
                                "labels": {"lane": "knowledge_graph"},
                                "thresholds": {"warning": 1000, "critical": 2000}
                            },
                            {
                                "title": "LLM Synthesis",
                                "type": "histogram",
                                "metric": "sarvanom_sla_llm_ms",
                                "labels": {"lane": "llm_synthesis"},
                                "thresholds": {"warning": 1000, "critical": 2000}
                            }
                        ]
                    }
                ]
            },
            "alerts": [
                {
                    "name": "SLA Violation",
                    "condition": "sarvanom_sla_compliance_rate < 95%",
                    "severity": "warning",
                    "notification": ["slack"]
                },
                {
                    "name": "High TTFT",
                    "condition": "sarvanom_sla_ttft_ms > 2s",
                    "severity": "critical",
                    "notification": ["slack", "email"]
                }
            ]
        }
    
    def generate_guided_prompt_dashboard(self) -> Dict[str, Any]:
        """Generate Guided Prompt dashboard configuration"""
        return {
            "title": "SarvanOM v2 - Guided Prompt",
            "refresh_rate": 60,
            "layout": {
                "rows": [
                    {
                        "title": "Guided Prompt KPIs",
                        "type": "row",
                        "tiles": [
                            {
                                "title": "Accept Rate",
                                "type": "gauge",
                                "metric": "sarvanom_guided_prompt_accept_rate",
                                "thresholds": {"warning": 30.0, "critical": 20.0}
                            },
                            {
                                "title": "Edit Rate",
                                "type": "gauge",
                                "metric": "sarvanom_guided_prompt_edit_rate",
                                "thresholds": {"warning": 50.0, "critical": 70.0}
                            },
                            {
                                "title": "Skip Rate",
                                "type": "gauge",
                                "metric": "sarvanom_guided_prompt_skip_rate",
                                "thresholds": {"warning": 20.0, "critical": 30.0}
                            },
                            {
                                "title": "TTFR",
                                "type": "histogram",
                                "metric": "sarvanom_guided_prompt_ttfr_ms",
                                "thresholds": {"warning": 500, "critical": 800}
                            }
                        ]
                    },
                    {
                        "title": "Guided Prompt SLOs",
                        "type": "row",
                        "tiles": [
                            {
                                "title": "P95 Latency",
                                "type": "histogram",
                                "metric": "sarvanom_guided_prompt_ttfr_ms",
                                "percentile": 95,
                                "thresholds": {"warning": 500, "critical": 800}
                            },
                            {
                                "title": "Complaint Rate",
                                "type": "gauge",
                                "metric": "sarvanom_guided_prompt_complaint_rate",
                                "thresholds": {"warning": 5.0, "critical": 10.0}
                            }
                        ]
                    }
                ]
            },
            "alerts": [
                {
                    "name": "Low Accept Rate",
                    "condition": "sarvanom_guided_prompt_accept_rate < 30%",
                    "severity": "warning",
                    "notification": ["slack"]
                },
                {
                    "name": "High TTFR",
                    "condition": "sarvanom_guided_prompt_ttfr_ms > 800ms",
                    "severity": "critical",
                    "notification": ["slack", "email"]
                }
            ]
        }

# FastAPI app
app = FastAPI(title="Observability Service", version="2.0.0")

# Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Observability components
trace_propagation = TracePropagation()
metrics_collector = MetricsCollector()
dashboard_generator = DashboardGenerator()

# Pydantic models for API
class SLAMetricsRequest(BaseModel):
    global_ms: float
    ttft_ms: float
    orchestrator_reserve_ms: float
    llm_ms: float
    web_ms: float
    vector_ms: float
    kg_ms: float
    yt_ms: float
    mode: str
    complexity: str

class LaneMetricsRequest(BaseModel):
    lane_name: str
    success_rate: float
    timeout_rate: float
    error_rate: float
    avg_time: float
    p95_time: float
    p99_time: float
    mode: str

class GuidedPromptMetricsRequest(BaseModel):
    accept_rate: float
    edit_rate: float
    skip_rate: float
    ttfr_ms: float
    complaint_rate: float
    mode: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "observability"}

@app.post("/metrics/sla")
async def record_sla_metrics(request: SLAMetricsRequest):
    """Record SLA metrics"""
    try:
        metrics = SLAMetrics(
            global_ms=request.global_ms,
            ttft_ms=request.ttft_ms,
            orchestrator_reserve_ms=request.orchestrator_reserve_ms,
            llm_ms=request.llm_ms,
            web_ms=request.web_ms,
            vector_ms=request.vector_ms,
            kg_ms=request.kg_ms,
            yt_ms=request.yt_ms,
            mode=QueryMode(request.mode),
            complexity=request.complexity
        )
        
        metrics_collector.record_sla_metrics(metrics)
        
        return {"status": "success", "message": "SLA metrics recorded"}
        
    except Exception as e:
        logger.error("Failed to record SLA metrics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/metrics/lane")
async def record_lane_metrics(request: LaneMetricsRequest):
    """Record lane metrics"""
    try:
        metrics = LaneMetrics(
            lane_name=LaneName(request.lane_name),
            success_rate=request.success_rate,
            timeout_rate=request.timeout_rate,
            error_rate=request.error_rate,
            avg_time=request.avg_time,
            p95_time=request.p95_time,
            p99_time=request.p99_time,
            mode=QueryMode(request.mode)
        )
        
        metrics_collector.record_lane_metrics(metrics)
        
        return {"status": "success", "message": "Lane metrics recorded"}
        
    except Exception as e:
        logger.error("Failed to record lane metrics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/metrics/guided-prompt")
async def record_guided_prompt_metrics(request: GuidedPromptMetricsRequest):
    """Record Guided Prompt metrics"""
    try:
        metrics = GuidedPromptMetrics(
            accept_rate=request.accept_rate,
            edit_rate=request.edit_rate,
            skip_rate=request.skip_rate,
            ttfr_ms=request.ttfr_ms,
            complaint_rate=request.complaint_rate,
            mode=QueryMode(request.mode)
        )
        
        metrics_collector.record_guided_prompt_metrics(metrics)
        
        return {"status": "success", "message": "Guided Prompt metrics recorded"}
        
    except Exception as e:
        logger.error("Failed to record Guided Prompt metrics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trace/start")
async def start_trace(service_name: str, request_id: str = None):
    """Start new trace"""
    try:
        context = trace_propagation.start_trace(service_name, request_id)
        
        return {
            "status": "success",
            "trace_context": asdict(context)
        }
        
    except Exception as e:
        logger.error("Failed to start trace", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trace/span")
async def create_span(parent_trace_id: str, parent_span_id: str, span_name: str, attributes: Dict[str, Any] = None):
    """Create child span"""
    try:
        # In real implementation, would look up parent context
        parent_context = TraceContext(
            trace_id=parent_trace_id,
            span_id=parent_span_id,
            service_name="unknown",
            request_id="unknown"
        )
        
        child_context = trace_propagation.create_span(parent_context, span_name, attributes)
        
        return {
            "status": "success",
            "trace_context": asdict(child_context)
        }
        
    except Exception as e:
        logger.error("Failed to create span", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboards/system-health")
async def get_system_health_dashboard():
    """Get system health dashboard configuration"""
    try:
        dashboard = dashboard_generator.generate_system_health_dashboard()
        return dashboard
        
    except Exception as e:
        logger.error("Failed to generate system health dashboard", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboards/performance")
async def get_performance_dashboard():
    """Get performance dashboard configuration"""
    try:
        dashboard = dashboard_generator.generate_performance_dashboard()
        return dashboard
        
    except Exception as e:
        logger.error("Failed to generate performance dashboard", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboards/guided-prompt")
async def get_guided_prompt_dashboard():
    """Get Guided Prompt dashboard configuration"""
    try:
        dashboard = dashboard_generator.generate_guided_prompt_dashboard()
        return dashboard
        
    except Exception as e:
        logger.error("Failed to generate Guided Prompt dashboard", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """Get Prometheus metrics"""
    try:
        metrics_data = generate_latest()
        return metrics_data.decode('utf-8')
        
    except Exception as e:
        logger.error("Failed to generate Prometheus metrics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Start Prometheus metrics server
    start_http_server(8007)
    
    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8006)
