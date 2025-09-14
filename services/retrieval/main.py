"""
Retrieval Service - SarvanOM v2

Multi-lane retrieval system with Qdrant + Meili + Arango + news + markets.
Pre-flight lane for Guided Prompt that runs in parallel with warmups.
Constraint chips (time, sources, citations-required, cost ceiling, depth) binding.
RRF fusion + diversity + dedupe + conflict detection → send to synthesis with citations_contract.
Budgets: 5s (simple), 7s (technical), 10s (research/multimedia) with orchestrator reserve.
"""

import asyncio
import json
import logging
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
import redis
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Import central configuration
from shared.core.config.central_config import get_central_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get configuration
config = get_central_config()

# Prometheus metrics
retrieval_requests_total = Counter('sarvanom_retrieval_requests_total', 'Total retrieval requests', ['complexity', 'lane'])
retrieval_latency = Histogram('sarvanom_retrieval_latency_seconds', 'Retrieval latency', ['lane', 'complexity'])
retrieval_results_count = Counter('sarvanom_retrieval_results_total', 'Retrieval results count', ['lane', 'status'])
fusion_time = Histogram('sarvanom_fusion_time_seconds', 'Result fusion time')
cache_hit_rate = Gauge('sarvanom_cache_hit_rate', 'Cache hit rate', ['cache_type'])

class QueryComplexity(str, Enum):
    SIMPLE = "simple"  # 5s budget
    TECHNICAL = "technical"  # 7s budget
    RESEARCH = "research"  # 10s budget
    MULTIMEDIA = "multimedia"  # 10s budget

class LaneStatus(str, Enum):
    SUCCESS = "success"
    TIMEOUT = "timeout"
    ERROR = "error"
    PARTIAL = "partial"

@dataclass
class RetrievalResult:
    lane: str
    status: LaneStatus
    results: List[Dict[str, Any]]
    latency_ms: float
    error: Optional[str] = None
    partial_results: List[Dict[str, Any]] = None

@dataclass
class ConstraintChip:
    id: str
    label: str
    type: str
    options: List[str]
    selected: Optional[str] = None

@dataclass
class RetrievalRequest:
    query: str
    complexity: QueryComplexity
    constraints: List[ConstraintChip]
    user_id: str
    session_id: str
    trace_id: str
    budget_remaining: float = 1.0

@dataclass
class FusedResult:
    results: List[Dict[str, Any]]
    fusion_metadata: Dict[str, Any]
    citations: List[Dict[str, Any]]
    disagreements: List[Dict[str, Any]]
    total_results: int
    unique_domains: int
    fusion_time_ms: float

class ConstraintBinder:
    """Binds user constraints to retrieval requests"""
    
    def __init__(self):
        self.constraint_mappings = {
            'time_range': self._map_time_range,
            'sources': self._map_sources,
            'citations_required': self._map_citations,
            'cost_ceiling': self._map_cost_ceiling,
            'depth': self._map_depth
        }
    
    def bind_constraints(self, query: str, constraints: List[ConstraintChip]) -> Dict[str, Any]:
        """Bind user constraints to retrieval request"""
        bound_constraints = {}
        
        for constraint in constraints:
            if constraint.selected and constraint.id in self.constraint_mappings:
                mapper = self.constraint_mappings[constraint.id]
                bound_constraints[constraint.id] = mapper(constraint.selected)
        
        return {
            'original_query': query,
            'constraints': bound_constraints,
            'modified_query': self._apply_query_modifications(query, bound_constraints)
        }
    
    def _map_time_range(self, value: str) -> Dict[str, Any]:
        """Map time range constraint"""
        time_mappings = {
            'Recent (1 year)': {'start_date': datetime.now() - timedelta(days=365)},
            'Last 5 years': {'start_date': datetime.now() - timedelta(days=1825)},
            'All time': {}
        }
        return time_mappings.get(value, {})
    
    def _map_sources(self, value: str) -> Dict[str, Any]:
        """Map sources constraint"""
        source_mappings = {
            'Academic': {'domains': ['scholar.google.com', 'arxiv.org', 'pubmed.ncbi.nlm.nih.gov']},
            'News': {'domains': ['reuters.com', 'bbc.com', 'cnn.com', 'nytimes.com']},
            'Both': {}
        }
        return source_mappings.get(value, {})
    
    def _map_citations(self, value: str) -> Dict[str, Any]:
        """Map citations constraint"""
        return {'required': value == 'Yes'}
    
    def _map_cost_ceiling(self, value: str) -> Dict[str, Any]:
        """Map cost ceiling constraint"""
        cost_mappings = {
            'Low': {'max_cost': 0.01},
            'Medium': {'max_cost': 0.05},
            'High': {'max_cost': 0.10}
        }
        return cost_mappings.get(value, {})
    
    def _map_depth(self, value: str) -> Dict[str, Any]:
        """Map depth constraint"""
        depth_mappings = {
            'Simple': {'max_results': 10, 'max_word_count': 500},
            'Technical': {'max_results': 20, 'max_word_count': 1000},
            'Research': {'max_results': 50, 'max_word_count': 2000}
        }
        return depth_mappings.get(value, {})
    
    def _apply_query_modifications(self, query: str, constraints: Dict[str, Any]) -> str:
        """Apply constraint-based query modifications"""
        modified_query = query
        
        # Add time range to query
        if 'time_range' in constraints and 'start_date' in constraints['time_range']:
            start_date = constraints['time_range']['start_date']
            modified_query += f" (since {start_date.strftime('%Y-%m-%d')})"
        
        # Add source preferences
        if 'sources' in constraints and 'domains' in constraints['sources']:
            domains = constraints['sources']['domains']
            modified_query += f" (from {', '.join(domains[:3])})"
        
        return modified_query

# Import lanes
from .lanes.web_lane import WebLane
from .lanes.vector_lane import VectorLane
from .lanes.keyword_lane import KeywordLane
from .lanes.kg_lane import KnowledgeGraphLane
from .lanes.news_lane import NewsLane
from .lanes.markets_lane import MarketsLane
from .lanes.preflight_lane import PreflightLane
from .fusion import ReciprocalRankFusion

class RetrievalService:
    """Main retrieval service orchestrating all lanes"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.constraint_binder = ConstraintBinder()
        self.fusion = ReciprocalRankFusion()
        
        # Initialize lanes
        self.lanes = {
            "web": WebLane(redis_client),
            "vector": VectorLane(),
            "keyword": KeywordLane(),
            "knowledge_graph": KnowledgeGraphLane(),
            "news": NewsLane(),
            "markets": MarketsLane(),
            "preflight": PreflightLane()
        }
        
        # Budget allocations
        self.budget_allocations = {
            QueryComplexity.SIMPLE: 5000,  # 5s total
            QueryComplexity.TECHNICAL: 7000,  # 7s total
            QueryComplexity.RESEARCH: 10000,  # 10s total
            QueryComplexity.MULTIMEDIA: 10000  # 10s total
        }
    
    async def retrieve(self, request: RetrievalRequest) -> FusedResult:
        """Execute multi-lane retrieval with fusion"""
        start_time = time.time()
        
        # Bind constraints
        bound_request = self.constraint_binder.bind_constraints(request.query, request.constraints)
        
        # Execute all lanes in parallel
        lane_tasks = []
        for lane_name, lane in self.lanes.items():
            task = asyncio.create_task(
                self._execute_lane_with_timeout(lane, request)
            )
            lane_tasks.append(task)
        
        # Wait for all lanes to complete
        lane_results = await asyncio.gather(*lane_tasks, return_exceptions=True)
        
        # Process results
        valid_results = []
        for i, result in enumerate(lane_results):
            if isinstance(result, Exception):
                logger.error(f"Lane {list(self.lanes.keys())[i]} failed: {result}")
                valid_results.append(RetrievalResult(
                    lane=list(self.lanes.keys())[i],
                    status=LaneStatus.ERROR,
                    results=[],
                    latency_ms=0.0,
                    error=str(result)
                ))
            else:
                valid_results.append(result)
        
        # Fuse results
        fused_result = self.fusion.fuse_results(valid_results)
        
        # Record metrics
        total_latency = (time.time() - start_time) * 1000
        self._record_metrics(valid_results, fused_result, total_latency)
        
        return fused_result
    
    async def _execute_lane_with_timeout(self, lane, request: RetrievalRequest) -> RetrievalResult:
        """Execute lane with timeout"""
        try:
            return await asyncio.wait_for(
                lane.retrieve(
                    request.query, 
                    request.complexity.value,
                    [constraint.__dict__ for constraint in request.constraints],
                    request.user_id,
                    request.session_id,
                    request.trace_id,
                    request.budget_remaining
                ),
                timeout=request.budget_remaining
            )
        except asyncio.TimeoutError:
            return RetrievalResult(
                lane=lane.__class__.__name__.lower().replace('lane', ''),
                status=LaneStatus.TIMEOUT,
                results=[],
                latency_ms=0.0,
                error="Lane exceeded timeout"
            )
    
    def _record_metrics(self, lane_results: List[RetrievalResult], fused_result: FusedResult, total_latency: float):
        """Record metrics for monitoring"""
        for result in lane_results:
            retrieval_requests_total.labels(
                complexity="unknown",  # Would be from request
                lane=result.lane
            ).inc()
            
            retrieval_latency.labels(
                lane=result.lane,
                complexity="unknown"
            ).observe(result.latency_ms / 1000.0)
            
            retrieval_results_count.labels(
                lane=result.lane,
                status=result.status.value
            ).inc(len(result.results))
        
        fusion_time.observe(fused_result.fusion_time_ms / 1000.0)

# Create FastAPI app
app = FastAPI(
    title="Retrieval Service",
    version="2.0.0",
    description="Multi-lane retrieval system with Qdrant + Meili + Arango + news + markets"
)

# Set CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins if isinstance(config.cors_origins, list) else (config.cors_origins.split(",") if config.cors_origins else ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# App state / DI container
async def init_dependencies():
    """Initialize shared clients and dependencies"""
    logger.info("Initializing Retrieval dependencies...")
    
    # Initialize Redis client
    app.state.redis_client = redis.Redis.from_url(
        str(config.redis_url),
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
    
    # Test Redis connection
    try:
        await asyncio.get_event_loop().run_in_executor(
            None, app.state.redis_client.ping
        )
        logger.info("Redis client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise
    
    # Initialize Retrieval Service
    app.state.retrieval_service = RetrievalService(app.state.redis_client)
    logger.info("Retrieval Service initialized successfully")

async def cleanup_dependencies():
    """Cleanup shared clients and dependencies"""
    logger.info("Cleaning up Retrieval dependencies...")
    
    if hasattr(app.state, 'redis_client'):
        try:
            app.state.redis_client.close()
            logger.info("Redis client closed successfully")
        except Exception as e:
            logger.error(f"Error closing Redis client: {e}")

# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    await init_dependencies()

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    await cleanup_dependencies()

# Pydantic models for API
class ConstraintChipRequest(BaseModel):
    id: str
    label: str
    type: str
    options: List[str]
    selected: Optional[str] = None

class RetrievalRequestModel(BaseModel):
    query: str
    complexity: str
    constraints: List[ConstraintChipRequest] = []
    user_id: str
    session_id: str
    trace_id: str
    budget_remaining: float = 1.0

class RetrievalResultResponse(BaseModel):
    results: List[Dict[str, Any]]
    fusion_metadata: Dict[str, Any]
    citations: List[Dict[str, Any]]
    disagreements: List[Dict[str, Any]]
    total_results: int
    unique_domains: int
    fusion_time_ms: float

# Health & Config endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint - fast, no downstream calls"""
    return {"status": "healthy", "service": "retrieval", "timestamp": datetime.now().isoformat()}

@app.get("/ready")
async def ready_check():
    """Ready check endpoint - light ping to critical deps with small timeout"""
    try:
        # Check Redis connection with timeout
        await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None, app.state.redis_client.ping
            ),
            timeout=2.0
        )
        return {"status": "ready", "service": "retrieval", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Ready check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/config")
async def get_config_endpoint():
    """Config endpoint - sanitized echo of active providers and keyless fallbacks"""
    return {
        "service": "retrieval",
        "active_providers": {
            "qdrant": bool(config.vector_db_url),
            "meilisearch": bool(config.meilisearch_url),
            "arangodb": bool(getattr(config, 'arango_url', None)),
            "redis": bool(config.redis_url)
        },
        "keyless_fallbacks_enabled": getattr(config, 'keyless_fallbacks_enabled', True),
        "environment": config.environment.value,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/version")
async def get_version():
    """Version endpoint"""
    return {
        "service": "retrieval",
        "version": "2.0.0",
        "build_date": datetime.now().isoformat(),
        "environment": config.environment.value
    }

@app.post("/retrieve", response_model=RetrievalResultResponse)
async def retrieve_documents(request: RetrievalRequestModel):
    """Retrieve documents using multi-lane retrieval"""
    try:
        # Convert request to internal format
        constraints = [ConstraintChip(**constraint.dict()) for constraint in request.constraints]
        
        retrieval_request = RetrievalRequest(
            query=request.query,
            complexity=QueryComplexity(request.complexity),
            constraints=constraints,
            user_id=request.user_id,
            session_id=request.session_id,
            trace_id=request.trace_id,
            budget_remaining=request.budget_remaining
        )
        
        # Execute retrieval
        fused_result = await app.state.retrieval_service.retrieve(retrieval_request)
        
        return RetrievalResultResponse(**asdict(fused_result))
        
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lanes")
async def get_lane_status():
    """Get status of all retrieval lanes"""
    return {
        "lanes": list(app.state.retrieval_service.lanes.keys()),
        "status": "healthy",
        "budget_allocations": app.state.retrieval_service.budget_allocations
    }

# Observability middleware
if config.metrics_enabled:
    # Mount Prometheus metrics
    from prometheus_client import make_asgi_app
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    logger.info("Prometheus metrics enabled")

if getattr(config, 'tracing_enabled', False) and getattr(config, 'jaeger_agent_host', None):
    # Mount tracing middleware
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.jaeger.thrift import JaegerExporter
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        
        # Configure Jaeger tracing
        trace.set_tracer_provider(TracerProvider())
        jaeger_exporter = JaegerExporter(
            agent_host_name=config.jaeger_agent_host,
            agent_port=int(config.jaeger_agent_port) if config.jaeger_agent_port else 6831,
        )
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(app)
        logger.info("Jaeger tracing enabled")
    except ImportError:
        logger.warning("OpenTelemetry packages not available, tracing disabled")
    except Exception as e:
        logger.error(f"Failed to enable tracing: {e}")

if __name__ == "__main__":
    # Start Prometheus metrics server if enabled
    if config.metrics_enabled:
        start_http_server(8006)
        logger.info("Prometheus metrics server started on port 8006")
    
    # Start FastAPI server
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8004,
        log_level=config.log_level.value.lower()
    )
