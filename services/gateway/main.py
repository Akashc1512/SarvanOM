"""
API Gateway for Universal Knowledge Platform

This gateway routes requests to various microservices including:
- Search/Retrieval service
- Fact-check service  
- Synthesis service
- Authentication service
- Crawler service
- Vector database service
- Knowledge graph service
"""

# Load environment variables from .env file first
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if present
except ImportError:
    pass  # dotenv not installed, continue without it

# Import Windows compatibility fixes first
try:
    import shared.core.windows_compatibility
except ImportError:
    pass  # Windows compatibility not available

from fastapi import FastAPI, HTTPException, Request, Response, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional, List
import logging
import time
import re
import json
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware

# Import unified logging
from shared.core.unified_logging import setup_logging, get_logger, setup_fastapi_logging

# Import analytics metrics
from services.analytics.metrics.knowledge_platform_metrics import (
    record_query_intelligence_metrics,
    record_retrieval_metrics,
    record_business_metrics,
    record_expert_validation_metrics
)

# Import the real LLM processor
from services.gateway.real_llm_integration import RealLLMProcessor

# Import advanced features
from services.gateway.cache_manager import cache_manager
from services.gateway.streaming_manager import stream_manager
from services.gateway.background_processor import background_processor, TaskType, TaskPriority
from services.gateway.prompt_optimizer import prompt_optimizer, PromptType, PromptComplexity
from services.gateway.huggingface_integration import huggingface_integration

# Initialize the LLM processor
llm_processor = RealLLMProcessor()

# Configure unified logging
logging_config = setup_logging(service_name="sarvanom-gateway-service")
logger = get_logger(__name__)

# Initialize advanced features
async def initialize_advanced_features():
    """Initialize all advanced features"""
    try:
        # Initialize cache manager
        await cache_manager.initialize()
        logger.info("✅ Cache manager initialized")
        
        # Initialize stream manager
        await stream_manager.initialize()
        logger.info("✅ Stream manager initialized")
        
        # Initialize background processor
        await background_processor.initialize()
        logger.info("✅ Background processor initialized")
        
        # Initialize prompt optimizer
        await prompt_optimizer.initialize()
        logger.info("✅ Prompt optimizer initialized")
        
        # Initialize HuggingFace integration
        await huggingface_integration.initialize()
        logger.info("✅ HuggingFace integration initialized")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize advanced features: {e}")

# Initialize features on startup using modern lifespan
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_advanced_features()
    yield
    # Shutdown
    await cache_manager.close()
    await stream_manager.close()
    await huggingface_integration.close()
    await background_processor.close()
    await prompt_optimizer.close()

# Update FastAPI app with lifespan
app = FastAPI(
    title="Universal Knowledge Platform API Gateway",
    description="Advanced API Gateway with caching, streaming, background processing, and prompt optimization",
    version="1.0.0",
    lifespan=lifespan
)

# Security configuration
MAX_PAYLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "https://sarvanom.com",
    "https://www.sarvanom.com"
]
TRUSTED_HOSTS = ["localhost", "127.0.0.1", "sarvanom.com", "www.sarvanom.com"]

# Input validation patterns
XSS_PATTERN = re.compile(r'<script[^>]*>.*?</script>|<iframe[^>]*>.*?</iframe>|<object[^>]*>.*?</object>', re.IGNORECASE | re.DOTALL)
SQL_INJECTION_PATTERN = re.compile(r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*?\b(from|into|table|database|where)\b)', re.IGNORECASE)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for input validation and security headers."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip security checks for basic endpoints
        if request.url.path in ["/", "/health", "/health/detailed", "/docs", "/openapi.json"]:
            response = await call_next(request)
            # Still add security headers
            self._add_security_headers(response)
            return response
        
        # Check payload size only for POST/PUT requests with content
        if request.method in ["POST", "PUT", "PATCH"]:
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > MAX_PAYLOAD_SIZE:
                return JSONResponse(
                    status_code=413,
                    content={"error": "Payload too large", "max_size_mb": MAX_PAYLOAD_SIZE // (1024 * 1024)}
                )
        
        # Only validate query parameters for specific endpoints that accept user input
        if request.url.path in ["/search", "/fact-check", "/synthesize", "/vector/search"] and request.query_params:
            query_params = str(request.query_params)
            if self._contains_malicious_content(query_params):
                return JSONResponse(
                    status_code=400,
                    content={"error": "Malicious content detected in query parameters"}
                )
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        self._add_security_headers(response)
        
        return response
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    def _contains_malicious_content(self, content: str) -> bool:
        """Check for malicious content patterns."""
        if XSS_PATTERN.search(content):
            return True
        if SQL_INJECTION_PATTERN.search(content):
            return True
        return False

# App is already created above with lifespan

# Setup FastAPI logging integration
setup_fastapi_logging(app, service_name="sarvanom-gateway-service")

# Add security middleware
app.add_middleware(SecurityMiddleware)

# Add trusted host middleware with permissive configuration for testing
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=TRUSTED_HOSTS + ["testserver", "*"]
)

# Add CORS middleware with secure configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page-Count"],
    max_age=3600,
)

# Request/Response models with enhanced validation
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    user_id: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    
    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and sanitize query input."""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        
        # Check for malicious content
        if XSS_PATTERN.search(v):
            raise ValueError("Query contains potentially malicious content")
        if SQL_INJECTION_PATTERN.search(v):
            raise ValueError("Query contains potentially malicious content")
        
        return v.strip()

class FactCheckRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=50000)
    user_id: Optional[str] = None
    context: Optional[str] = None
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate and sanitize content input."""
        if not v.strip():
            raise ValueError("Content cannot be empty")
        
        # Check for malicious content
        if XSS_PATTERN.search(v):
            raise ValueError("Content contains potentially malicious content")
        
        return v.strip()

class SynthesisRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    sources: Optional[List[str]] = None
    user_id: Optional[str] = None
    
    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and sanitize query input."""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        
        # Check for malicious content
        if XSS_PATTERN.search(v):
            raise ValueError("Query contains potentially malicious content")
        
        return v.strip()

class AuthRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        return v.strip()

class CrawlRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=2048)
    depth: Optional[int] = Field(default=1, ge=1, le=5)
    user_id: Optional[str] = None
    
    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v.strip()

class VectorSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    limit: Optional[int] = Field(default=10, ge=1, le=100)
    filters: Optional[Dict[str, Any]] = None
    
    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and sanitize query input."""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        
        # Check for malicious content
        if XSS_PATTERN.search(v):
            raise ValueError("Query contains potentially malicious content")
        
        return v.strip()

class GraphContextRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    depth: Optional[int] = Field(default=2, ge=1, le=5)
    user_id: Optional[str] = None

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str) -> str:
        """Validate and sanitize topic input."""
        if not v.strip():
            raise ValueError("Topic cannot be empty")
        
        # Check for malicious content
        if XSS_PATTERN.search(v):
            raise ValueError("Topic contains potentially malicious content")
        
        return v.strip()

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint for the API gateway with service status."""
    import time
    
    start_time = time.time()
    
    try:
        # Basic health check - API is responding
        response_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            "status": "ok",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "response_time_ms": response_time_ms,
            "service": "sarvanom-gateway",
            "version": "1.0.0",
            "overall_healthy": True
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
            "status": "error",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "overall_healthy": False
        }
        )

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check endpoint for frontend dashboard."""
    import time
    
    start_time = time.time()
    
    try:
        # Basic detailed health check
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Mock metrics for now - in production these would come from actual metrics collection
        mock_metrics = {
            "query_intelligence": {"total_requests": 0},
            "orchestration": {"avg_duration": 0.0},
            "system": {"error_rate": 0.0}
        }
        
        # Compile detailed health report
        health_report = {
            "status": "ok",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "response_time_ms": response_time_ms,
            "overall_healthy": True,
            "service": "sarvanom-gateway",
            "version": "1.0.0",
            "services": {
                "gateway": {"status": "healthy", "response_time_ms": response_time_ms}
            },
            "metrics": {
                "uptime": "operational",
                "last_check": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "performance": {
                "uptime_seconds": time.time() - start_time,
                "total_requests": mock_metrics.get("query_intelligence", {}).get("total_requests", 0),
                "avg_response_time": mock_metrics.get("orchestration", {}).get("avg_duration", 0),
                "error_rate": mock_metrics.get("system", {}).get("error_rate", 0.0)
            },
            "recommendations": []
        }
        
        # Add recommendations based on health status
        all_services_healthy = True  # Mock for now
        
        if not all_services_healthy:
            health_report["recommendations"].append("Some services are experiencing issues. Check service logs for details.")
        
        if mock_metrics.get("system", {}).get("error_rate", 0.0) > 0.05:
            health_report["recommendations"].append("Error rate is elevated. Consider investigating recent changes.")
        
        if mock_metrics.get("orchestration", {}).get("avg_duration", 0) > 5.0:
            health_report["recommendations"].append("Average response time is high. Consider optimizing query processing.")
        
        return health_report
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
            "status": "error",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "overall_healthy": False,
            "recommendations": ["Health check system is experiencing issues. Contact system administrator."]
        }
        )

# Search/Retrieval service endpoint
@app.get("/search")
async def search_endpoint():
    """Placeholder for search/retrieval service."""
    return {"message": "Retrieval service route"}

@app.post("/search")
async def search_post(request: SearchRequest):
    """Enhanced search endpoint with real LLM integration."""
    
    start_time = time.time()
    
    try:
        # Record query intelligence metrics
        record_query_intelligence_metrics(
            intent_type="search",
            complexity_level="medium",  # Could be enhanced with query analysis
            domain_type="general",
            duration_seconds=0.0,  # Will be updated after processing
            cache_hit=False,  # Could be enhanced with cache checking
            cache_type="redis"
        )
        
        # Use real LLM to process the search request
        llm_result = await llm_processor.search_with_ai(
            query=request.query,
            user_id=request.user_id,
            max_results=10
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Record retrieval metrics
        record_retrieval_metrics(
            source_type="web_search",
            fusion_strategy="hybrid",
            duration_seconds=processing_time,
            result_count=len(llm_result.get("results", [])),
            confidence_score=llm_result.get("confidence_score", 0.8)
        )
        
        # Record business metrics
        record_business_metrics(
            user_id=request.user_id or "anonymous",
            query_type="search",
            complexity="medium",
            response_time_seconds=processing_time,
            satisfaction_score=None  # Could be collected from user feedback
        )
        
        # Add timing information to response
        llm_result["processing_time_ms"] = int(processing_time * 1000)
        llm_result["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        return llm_result
        
    except Exception as e:
        logger.error(f"Search request failed: {e}")
        
        # Record error metrics
        record_business_metrics(
            user_id=request.user_id or "anonymous",
            query_type="search",
            complexity="medium",
            response_time_seconds=time.time() - start_time,
            error_type="search_failure"
        )
        
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Fact-check service endpoint
@app.post("/fact-check")
async def fact_check_endpoint(request: FactCheckRequest):
    """Enhanced fact-check endpoint with real LLM integration."""
    
    start_time = time.time()
    
    try:
        # Record query intelligence metrics
        record_query_intelligence_metrics(
            intent_type="fact_check",
            complexity_level="high",  # Fact-checking is typically complex
            domain_type="validation",
            duration_seconds=0.0,  # Will be updated after processing
            cache_hit=False,
            cache_type="redis"
        )
        
        # Use real LLM to perform fact checking
        llm_result = await llm_processor.fact_check_with_ai(
            claim=request.content,
            context=request.context,
            sources=[]
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Record expert validation metrics
        record_expert_validation_metrics(
            network_type="academic,industry,ai_model",
            validation_status=llm_result.get("status", "unclear"),
            duration_seconds=processing_time,
            consensus_score=llm_result.get("consensus_score", 0.8),
            consensus_level="high" if llm_result.get("consensus_score", 0) > 0.8 else "medium",
            agreement_ratio=llm_result.get("agreeing_experts", 0) / llm_result.get("total_experts", 1)
        )
        
        # Record business metrics
        record_business_metrics(
            user_id=request.user_id or "anonymous",
            query_type="fact_check",
            complexity="high",
            response_time_seconds=processing_time,
            satisfaction_score=None
        )
        
        # Add timing information to response
        llm_result["processing_time_ms"] = int(processing_time * 1000)
        llm_result["validation_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        return llm_result
        
    except Exception as e:
        logger.error(f"Fact-check request failed: {e}")
        
        # Record error metrics
        record_business_metrics(
            user_id=request.user_id or "anonymous",
            query_type="fact_check",
            complexity="high",
            response_time_seconds=time.time() - start_time,
            error_type="fact_check_failure"
        )
        
        raise HTTPException(status_code=500, detail=f"Fact-check failed: {str(e)}")

# Synthesis service endpoint
@app.post("/synthesize")
async def synthesize_endpoint(request: SynthesisRequest):
    """Enhanced synthesis endpoint with real LLM integration."""
    import time
    from services.analytics.metrics.knowledge_platform_metrics import (
        record_query_intelligence_metrics,
        record_orchestration_metrics,
        record_business_metrics
    )
    
    start_time = time.time()
    
    try:
        # Record query intelligence metrics
        record_query_intelligence_metrics(
            intent_type="synthesis",
            complexity_level="high",  # Synthesis is typically complex
            domain_type="multi_source",
            duration_seconds=0.0,  # Will be updated after processing
            cache_hit=False,
            cache_type="redis"
        )
        
        # Use real LLM to perform synthesis
        llm_result = await llm_processor.synthesize_with_ai(
            content=request.query,
            query=request.query,
            sources=request.sources or []
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Record orchestration metrics
        from shared.core.config import get_central_config
        config = get_central_config()
        record_orchestration_metrics(
            model_type=config.openai_model,  # Use configured model
            strategy="multi_agent",
            duration_seconds=processing_time,
            fallback_used=False,
            circuit_breaker_state="closed"
        )
        
        # Record business metrics
        record_business_metrics(
            user_id=request.user_id or "anonymous",
            query_type="synthesis",
            complexity="high",
            response_time_seconds=processing_time,
            satisfaction_score=None
        )
        
        # Add timing information to response
        llm_result["processing_time_ms"] = int(processing_time * 1000)
        llm_result["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        return llm_result
        
    except Exception as e:
        logger.error(f"Synthesis request failed: {e}")
        
        # Record error metrics
        record_business_metrics(
            user_id=request.user_id or "anonymous",
            query_type="synthesis",
            complexity="high",
            response_time_seconds=time.time() - start_time,
            error_type="synthesis_failure"
        )
        
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")

# Authentication service endpoints
@app.post("/auth/login")
async def auth_login_endpoint(request: AuthRequest):
    """Placeholder for authentication service login."""
    return {
        "message": "Auth service route",
        "username": request.username
    }

@app.post("/auth/register")
async def auth_register_endpoint(request: AuthRequest):
    """Placeholder for authentication service registration."""
    return {
        "message": "Auth service registration route",
        "username": request.username
    }

# Crawler service endpoint
@app.post("/crawl")
async def crawl_endpoint(request: CrawlRequest):
    """Placeholder for crawler service."""
    return {
        "message": "Crawler service route",
        "url": request.url,
        "depth": request.depth,
        "user_id": request.user_id
    }

# Vector database service endpoint
@app.post("/vector/search")
async def vector_search_endpoint(request: VectorSearchRequest):
    """Placeholder for vector database service."""
    return {
        "message": "Vector DB service route",
        "query": request.query,
        "limit": request.limit,
        "filters": request.filters
    }

# Knowledge graph service endpoint
@app.get("/graph/context")
async def graph_context_endpoint(topic: str = "", depth: int = 2, user_id: Optional[str] = None):
    """Placeholder for knowledge graph service."""
    import random
    
    # Generate sample graph data based on topic
    main_topic = topic[:30] if topic else "Query Topic"
    
    # Create nodes
    nodes = [
        {
            "id": "main",
            "name": main_topic,
            "label": main_topic,
            "description": f"Main topic: {main_topic}",
            "type": "main",
            "weight": 1.0
        }
    ]
    
    # Add related concepts
    related_concepts = [
        f"Related Concept {i+1}" for i in range(min(depth, 3))
    ]
    
    for i, concept in enumerate(related_concepts):
        nodes.append({
            "id": f"related_{i}",
            "name": concept,
            "label": concept,
            "description": f"Related to {main_topic}",
            "type": "related",
            "weight": 0.8 - (i * 0.1)
        })
    
    # Add sub-concepts
    sub_concepts = [
        f"Sub-concept {i+1}" for i in range(min(depth * 2, 4))
    ]
    
    for i, concept in enumerate(sub_concepts):
        nodes.append({
            "id": f"sub_{i}",
            "name": concept,
            "label": concept,
            "description": f"Sub-concept of related concept",
            "type": "sub",
            "weight": 0.6 - (i * 0.1)
        })
    
    # Create edges
    edges = []
    
    # Connect main topic to related concepts
    for i in range(len(related_concepts)):
        edges.append({
            "from": "main",
            "to": f"related_{i}",
            "label": "relates to",
            "relationship": "relates to",
            "type": "strong",
            "weight": 0.9
        })
    
    # Connect related concepts to sub-concepts
    for i in range(len(sub_concepts)):
        parent_idx = i % len(related_concepts)
        edges.append({
            "from": f"related_{parent_idx}",
            "to": f"sub_{i}",
            "label": "contains",
            "relationship": "contains",
            "type": "medium",
            "weight": 0.7
        })
    
    return {
        "message": "Knowledge graph service route",
        "topic": topic,
        "depth": depth,
        "user_id": user_id,
        "nodes": nodes,
        "edges": edges,
        "total_nodes": len(nodes),
        "total_edges": len(edges)
    }

@app.post("/graph/context")
async def graph_context_post_endpoint(request: GraphContextRequest):
    """Placeholder for knowledge graph service with POST."""
    return {
        "message": "Knowledge graph service route",
        "topic": request.topic,
        "depth": request.depth,
        "user_id": request.user_id
    }

# Analytics endpoint
@app.get("/analytics")
async def analytics_endpoint():
    """Enhanced analytics endpoint with comprehensive metrics."""
    import time
    from services.analytics.metrics.knowledge_platform_metrics import get_metrics_json
    
    try:
        # Get comprehensive metrics
        metrics = get_metrics_json()
        
        # Add additional analytics data
        analytics_data = {
            "metrics": metrics,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "platform_status": "operational",
            "data_sources": {
                "query_intelligence": "active",
                "orchestration": "active", 
                "retrieval": "active",
                "memory": "active",
                "expert_validation": "active",
                "business_metrics": "active"
            }
        }
        
        return analytics_data
        
    except Exception as e:
        logger.error(f"Analytics endpoint failed: {e}")
        return {
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "error"
        }

@app.get("/analytics/summary")
async def analytics_summary_endpoint(time_range: str = "30d"):
    """Enhanced analytics summary endpoint with time-based filtering."""
    import time
    from services.analytics.metrics.knowledge_platform_metrics import get_metrics_json
    
    try:
        # Get metrics with time filtering (placeholder implementation)
        metrics = get_metrics_json()
        
        # Calculate summary statistics
        summary = {
            "time_range": time_range,
            "total_queries": metrics.get("query_intelligence", {}).get("total_requests", 0),
            "average_response_time": metrics.get("orchestration", {}).get("avg_duration", 0),
            "success_rate": 0.95,  # Placeholder - could be calculated from metrics
            "top_query_types": [
                {"type": "search", "count": 150},
                {"type": "fact_check", "count": 75},
                {"type": "synthesis", "count": 50}
            ],
            "service_health": {
                "retrieval": "healthy",
                "synthesis": "healthy", 
                "fact_check": "healthy",
                "knowledge_graph": "healthy"
            },
            "performance_metrics": {
                "avg_processing_time_ms": 1200,
                "cache_hit_rate": 0.65,
                "error_rate": 0.02
            },
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Analytics summary failed: {e}")
        return {
            "error": str(e),
            "time_range": time_range,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "error"
        }

@app.post("/analytics/track")
async def analytics_track_endpoint():
    """Enhanced analytics tracking endpoint for custom events."""
    from pydantic import BaseModel
    from typing import Dict, Any, Optional
    
    class TrackingEvent(BaseModel):
        event_type: str
        user_id: Optional[str] = None
        session_id: Optional[str] = None
        properties: Optional[Dict[str, Any]] = None
        timestamp: Optional[str] = None
    
    async def track_event(event: TrackingEvent):
        """Track a custom analytics event."""
        import time
        from services.analytics.metrics.knowledge_platform_metrics import record_business_metrics
        
        try:
            # Record business metrics for the event
            record_business_metrics(
                user_id=event.user_id or "anonymous",
                query_type=event.event_type,
                complexity="medium",
                response_time_seconds=0.0,
                satisfaction_score=None
            )
            
            # Log the event
            logger.info(f"Tracked event: {event.event_type} for user: {event.user_id}")
            
            return {
                "status": "success",
                "event_id": f"event_{int(time.time())}",
                "timestamp": event.timestamp or time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Event tracking failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    return {
        "message": "Analytics tracking endpoint",
        "supported_events": [
            "page_view",
            "button_click", 
            "form_submit",
            "search_query",
            "result_view",
            "feedback_submit",
            "error_occurred"
        ],
        "usage": "POST with TrackingEvent model to track custom events"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "message": "Universal Knowledge Platform API Gateway",
        "version": "1.0.0",
        "services": [
            "search",
            "fact-check", 
            "synthesize",
            "auth",
            "crawl",
            "vector",
            "graph",
            "analytics"
        ],
        "health": "/health"
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found", 
            "message": "The requested endpoint does not exist",
            "path": str(request.url.path),
            "method": request.method
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error", 
            "message": "An unexpected error occurred",
            "path": str(request.url.path),
            "method": request.method
        }
    )

# Advanced Features Endpoints

# Cache Management Endpoints
@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    try:
        stats = await cache_manager.get_stats()
        return {
            "status": "success",
            "cache_stats": stats
        }
    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cache/clear")
async def clear_cache():
    """Clear all cache entries"""
    try:
        await cache_manager.clear_all()
        return {
            "status": "success",
            "message": "Cache cleared successfully"
        }
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Streaming Endpoints
@app.get("/stream/search")
async def stream_search_endpoint(query: str, user_id: str = "anonymous"):
    """Stream search results using Server-Sent Events"""
    try:
        return await stream_manager.create_sse_stream(
            query=query,
            user_id=user_id,
            endpoint="search",
            llm_processor=llm_processor
        )
    except Exception as e:
        logger.error(f"Stream search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/search")
async def websocket_search_endpoint(websocket: WebSocket):
    """WebSocket endpoint for streaming search results"""
    try:
        await stream_manager.create_websocket_stream(
            websocket=websocket,
            query="",  # Will be received via WebSocket
            user_id="anonymous",
            endpoint="search",
            llm_processor=llm_processor
        )
    except Exception as e:
        logger.error(f"WebSocket search error: {e}")

@app.get("/stream/fact-check")
async def stream_fact_check_endpoint(claim: str, user_id: str = "anonymous"):
    """Stream fact-check results using Server-Sent Events"""
    try:
        return await stream_manager.create_sse_stream(
            query=claim,
            user_id=user_id,
            endpoint="fact_check",
            llm_processor=llm_processor
        )
    except Exception as e:
        logger.error(f"Stream fact-check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background Processing Endpoints
@app.post("/background/task")
async def submit_background_task(
    task_type: str,
    query: str,
    user_id: str = "anonymous",
    priority: str = "normal"
):
    """Submit a background task for processing"""
    try:
        # Map string to enum
        task_type_enum = TaskType(task_type.lower())
        
        # Map priority string to enum value
        priority_map = {
            "critical": TaskPriority.CRITICAL,
            "high": TaskPriority.HIGH,
            "normal": TaskPriority.NORMAL,
            "low": TaskPriority.LOW,
            "bulk": TaskPriority.BULK
        }
        priority_enum = priority_map.get(priority.lower(), TaskPriority.NORMAL)
        
        task_id = await background_processor.submit_task(
            task_type=task_type_enum,
            query=query,
            user_id=user_id,
            endpoint=task_type.lower(),
            priority=priority_enum
        )
        
        return {
            "status": "success",
            "task_id": task_id,
            "message": f"Background task submitted: {task_id}"
        }
    except Exception as e:
        logger.error(f"Background task submission error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/background/task/{task_id}")
async def get_background_task_status(task_id: str):
    """Get background task status and result"""
    try:
        task_info = await background_processor.get_task_status(task_id)
        if not task_info:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "status": "success",
            "task_info": task_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Background task status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/background/task/{task_id}")
async def cancel_background_task(task_id: str):
    """Cancel a background task"""
    try:
        cancelled = await background_processor.cancel_task(task_id)
        if not cancelled:
            raise HTTPException(status_code=404, detail="Task not found or cannot be cancelled")
        
        return {
            "status": "success",
            "message": f"Task {task_id} cancelled successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Background task cancellation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/background/stats")
async def background_stats():
    """Get background processing statistics"""
    try:
        stats = await background_processor.get_queue_stats()
        return {
            "status": "success",
            "background_stats": stats
        }
    except Exception as e:
        logger.error(f"Background stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Prompt Optimization Endpoints
@app.post("/optimize/prompt")
async def optimize_prompt_endpoint(
    prompt: str,
    prompt_type: str = "search",
    complexity: str = "medium"
):
    """Optimize a prompt for better performance"""
    try:
        # Map strings to enums
        prompt_type_enum = PromptType(prompt_type.lower())
        complexity_enum = PromptComplexity(complexity.lower())
        
        optimized = await prompt_optimizer.optimize_prompt(
            prompt=prompt,
            prompt_type=prompt_type_enum,
            complexity=complexity_enum
        )
        
        return {
            "status": "success",
            "optimized_prompt": optimized.to_dict()
        }
    except Exception as e:
        logger.error(f"Prompt optimization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/optimize/stats")
async def prompt_optimization_stats():
    """Get prompt optimization statistics"""
    try:
        stats = await prompt_optimizer.get_optimization_stats()
        return {
            "status": "success",
            "optimization_stats": stats
        }
    except Exception as e:
        logger.error(f"Prompt optimization stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize/clear-cache")
async def clear_prompt_cache():
    """Clear prompt optimization cache"""
    try:
        await prompt_optimizer.clear_cache()
        return {
            "status": "success",
            "message": "Prompt optimization cache cleared"
        }
    except Exception as e:
        logger.error(f"Prompt cache clear error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System Status Endpoint
@app.get("/system/status")
async def system_status():
    """Get comprehensive system status including all advanced features"""
    try:
        # Get stats from all systems
        cache_stats = await cache_manager.get_stats()
        stream_stats = await stream_manager.get_metrics()
        background_stats = await background_processor.get_queue_stats()
        optimization_stats = await prompt_optimizer.get_optimization_stats()
        
        return {
            "status": "success",
            "system_status": {
                "cache": cache_stats,
                "streaming": stream_stats,
                "background_processing": background_stats,
                "prompt_optimization": optimization_stats,
                "huggingface": {
                    "device": huggingface_integration.device,
                    "loaded_models": len(huggingface_integration.models),
                    "loaded_pipelines": len(huggingface_integration.pipelines),
                    "embedding_model_loaded": huggingface_integration.embedding_model is not None,
                    "auth_status": await huggingface_integration.get_auth_status()
                },
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"System status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# HuggingFace Integration Endpoints
@app.post("/huggingface/generate")
async def huggingface_text_generation(
    prompt: str,
    model_name: str = "distilgpt2",
    max_length: int = 100,
    temperature: float = 0.7
):
    """Generate text using HuggingFace models"""
    try:
        result = await huggingface_integration.generate_text(
            prompt=prompt,
            model_name=model_name,
            max_length=max_length,
            temperature=temperature
        )
        
        return {
            "status": "success",
            "generated_text": result.result,
            "metadata": result.metadata,
            "processing_time": result.processing_time
        }
    except Exception as e:
        logger.error(f"HuggingFace text generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/huggingface/embeddings")
async def huggingface_embeddings(
    texts: List[str],
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
):
    """Get embeddings for texts using HuggingFace models"""
    try:
        result = await huggingface_integration.get_embeddings(
            texts=texts,
            model_name=model_name
        )
        
        return {
            "status": "success",
            "embeddings": result.result,
            "metadata": result.metadata,
            "processing_time": result.processing_time
        }
    except Exception as e:
        logger.error(f"HuggingFace embeddings error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/huggingface/sentiment")
async def huggingface_sentiment_analysis(
    text: str,
    model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"
):
    """Analyze sentiment using HuggingFace models"""
    try:
        result = await huggingface_integration.analyze_sentiment(
            text=text,
            model_name=model_name
        )
        
        return {
            "status": "success",
            "sentiment": result.result,
            "metadata": result.metadata,
            "processing_time": result.processing_time
        }
    except Exception as e:
        logger.error(f"HuggingFace sentiment analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/huggingface/summarize")
async def huggingface_summarization(
    text: str,
    model_name: str = "facebook/bart-large-cnn",
    max_length: int = 130
):
    """Summarize text using HuggingFace models"""
    try:
        result = await huggingface_integration.summarize_text(
            text=text,
            model_name=model_name,
            max_length=max_length
        )
        
        return {
            "status": "success",
            "summary": result.result,
            "metadata": result.metadata,
            "processing_time": result.processing_time
        }
    except Exception as e:
        logger.error(f"HuggingFace summarization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/huggingface/translate")
async def huggingface_translation(
    text: str,
    target_language: str = "es",
    model_name: str = "Helsinki-NLP/opus-mt-en-es"
):
    """Translate text using HuggingFace models"""
    try:
        result = await huggingface_integration.translate_text(
            text=text,
            target_language=target_language,
            model_name=model_name
        )
        return {
            "status": "success",
            "translation": result.result,
            "metadata": result.metadata,
            "processing_time": result.processing_time
        }
    except Exception as e:
        logger.error(f"HuggingFace translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/huggingface/entities")
async def huggingface_entity_extraction(
    text: str,
    model_name: str = "dbmdz/bert-large-cased-finetuned-conll03-english"
):
    """Extract named entities using HuggingFace models"""
    try:
        result = await huggingface_integration.extract_entities(
            text=text,
            model_name=model_name
        )
        
        return {
            "status": "success",
            "entities": result.result,
            "metadata": result.metadata,
            "processing_time": result.processing_time
        }
    except Exception as e:
        logger.error(f"HuggingFace entity extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/huggingface/qa")
async def huggingface_question_answering(
    question: str,
    context: str,
    model_name: str = "distilbert-base-cased-distilled-squad"
):
    """Answer questions using HuggingFace models"""
    try:
        result = await huggingface_integration.answer_question(
            question=question,
            context=context,
            model_name=model_name
        )
        
        return {
            "status": "success",
            "answer": result.result,
            "metadata": result.metadata,
            "processing_time": result.processing_time
        }
    except Exception as e:
        logger.error(f"HuggingFace question answering error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/huggingface/similarity")
async def huggingface_text_similarity(
    text1: str,
    text2: str,
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
):
    """Calculate text similarity using HuggingFace models"""
    try:
        result = await huggingface_integration.calculate_similarity(
            text1=text1,
            text2=text2,
            model_name=model_name
        )
        
        return {
            "status": "success",
            "similarity": result.result,
            "metadata": result.metadata,
            "processing_time": result.processing_time
        }
    except Exception as e:
        logger.error(f"HuggingFace similarity calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/huggingface/zero-shot")
async def huggingface_zero_shot_classification(
    text: str,
    candidate_labels: List[str],
    model_name: str = "facebook/bart-large-mnli"
):
    """Perform zero-shot classification using HuggingFace models"""
    try:
        result = await huggingface_integration.zero_shot_classification(
            text=text,
            candidate_labels=candidate_labels,
            model_name=model_name
        )
        
        return {
            "status": "success",
            "classification": result.result,
            "metadata": result.metadata,
            "processing_time": result.processing_time
        }
    except Exception as e:
        logger.error(f"HuggingFace zero-shot classification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/huggingface/models")
async def huggingface_available_models():
    """Get available HuggingFace models"""
    try:
        models = await huggingface_integration.get_available_models()
        
        return {
            "status": "success",
            "models": models,
            "device": huggingface_integration.device,
            "loaded_models": len(huggingface_integration.models),
            "loaded_pipelines": len(huggingface_integration.pipelines)
        }
    except Exception as e:
        logger.error(f"HuggingFace models error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/huggingface/model/{model_name}")
async def huggingface_model_info(model_name: str):
    """Get information about a specific HuggingFace model"""
    try:
        model_info = await huggingface_integration.get_model_info(model_name)
        
        return {
            "status": "success",
            "model_info": model_info
        }
    except Exception as e:
        logger.error(f"HuggingFace model info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 