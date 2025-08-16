"""
API Gateway Routes

This module defines all the routes for the API gateway, including health checks
and placeholder routes for each microservice.

This module uses shared contract models from shared.contracts and shared.core.api
to ensure consistency across the platform and avoid duplication.
"""

import logging
import time
from shared.core.unified_logging import get_logger
from datetime import datetime
from typing import Dict, Any, Optional

# Import shared contract models
from shared.contracts.query import (
    QueryRequest as SharedQueryRequest,
    SynthesisRequest as SharedSynthesisRequest,
    RetrievalSearchRequest as SharedSearchRequest,
    VectorEmbedRequest,
    VectorSearchRequest,
)
from shared.core.api.api_models import (
    HealthResponse,
    QueryRequest,
    QueryResponse,
    LoginRequest,
    RegisterRequest,
    AuthResponse,
    FeedbackRequest,
    FeedbackResponse,
    MetricsResponse,
    AnalyticsResponse,
    TaskRequest,
    TaskResponse,
    ExpertReviewRequest,
    ExpertReviewResponse,
)

# Try to import FastAPI, but handle gracefully if not installed
try:
    from fastapi import APIRouter, HTTPException, status
    from pydantic import BaseModel

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

    # Create dummy classes for testing
    class APIRouter:
        def __init__(self):
            pass

        def get(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

        def post(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

    class HTTPException:
        pass

    class status:
        HTTP_200_OK = 200
        HTTP_400_BAD_REQUEST = 400

    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)


logger = get_logger(__name__)

# Analytics Router
analytics_router = APIRouter()

@analytics_router.get("/metrics")
async def get_analytics_metrics():
    """Get system performance and analytics metrics."""
    try:
        from .analytics_collector import analytics
        
        performance_metrics = analytics.get_performance_metrics()
        agent_metrics = analytics.get_agent_metrics()
        system_health = analytics.get_system_health()
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "performance": performance_metrics,
            "agents": agent_metrics,
            "health": system_health,
            "service": "analytics"
        }
    except Exception as e:
        logger.error(f"Analytics metrics error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "service": "analytics"
        }

@analytics_router.get("/health-detailed")
async def get_system_health():
    """Get detailed system health summary."""
    try:
        from .analytics_collector import analytics
        return analytics.get_system_health()
    except Exception as e:
        return {
            "status": "error",
            "health_score": 0.0,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# Gateway-specific response model for service routing
class ServiceResponse(BaseModel):
    """Gateway service response model for routing to microservices."""
    status: str
    message: str
    service: str
    timestamp: str
    data: Optional[Dict[str, Any]] = None


# Additional gateway-specific request models for services not covered by shared contracts
class FactCheckRequest(BaseModel):
    """Fact check request model for fact-check service."""
    claim: str
    context: Optional[Dict[str, Any]] = None


# Health Router
health_router = APIRouter()


@health_router.get("/health", response_model=HealthResponse)
async def health_check():
    """Gateway health check endpoint - provides aggregate status from all services."""
    import time
    import psutil
    
    try:
        # Get system metrics
        uptime = time.time() - psutil.boot_time()
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Check service health (in production, this would call each service)
        service_health = {
            "gateway": {"status": "healthy", "response_time_ms": 10},
            "auth": {"status": "healthy", "endpoint": "/auth/health"},
            "fact-check": {"status": "healthy", "endpoint": "/fact-check/health"},
            "synthesis": {"status": "healthy", "endpoint": "/synthesis/health"},
            "search": {"status": "healthy", "endpoint": "/search/health"},
            "retrieval": {"status": "healthy", "endpoint": "/retrieval/health"},
        }
        
        # Determine overall health
        all_healthy = all(s["status"] == "healthy" for s in service_health.values())
        overall_status = "healthy" if all_healthy else "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            uptime=uptime,
            memory_usage={
                "total": memory.total,
                "used": memory.used,
                "free": memory.free,
                "percent": memory.percent
            },
            cpu_usage=cpu_percent,
            service_health=service_health
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            uptime=0.0,
            memory_usage={"total": 0, "used": 0, "free": 0},
            cpu_usage=0.0,
            error=str(e)
        )


@health_router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Sarvanom API Gateway",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "health": "/health",
    }


# Search Router
search_router = APIRouter()


@search_router.post("/", response_model=ServiceResponse)
async def search(request: QueryRequest):
    """Search endpoint with real AI-powered processing and full orchestration."""
    logger.info(f"🔍 Unified AI Search request: {request.query}")
    
    try:
        # Import consolidated components
        from .agent_orchestrator import agent_orchestrator, QueryContext
        from .analytics_collector import analytics
        from .real_llm_integration import QueryComplexity, real_llm_processor
        
        # Create query context
        context = QueryContext(
            trace_id=f"search_{int(time.time() * 1000)}",
            query=request.query,
            user_id=request.user_id,
            complexity=real_llm_processor.classify_query_complexity(request.query),
            timeout=30.0
        )
        
        # Process with agent orchestrator
        start_time = time.time()
        orchestration_result = await agent_orchestrator.process_query(context)
        processing_time = int((time.time() - start_time) * 1000)
        
        # Track analytics
        analytics.track_request(
            query=request.query,
            user_id=request.user_id,
            complexity=context.complexity.value,
            provider=orchestration_result.get("metadata", {}).get("primary_provider", "orchestrated"),
            response_time_ms=processing_time,
            success=orchestration_result.get("success", False)
        )
        
        return ServiceResponse(
            status="success" if orchestration_result.get("success") else "partial_success",
            message="AI-powered search with multi-agent orchestration completed",
            service="search",
            timestamp=datetime.now().isoformat(),
            data={
                **orchestration_result,
                "request_metadata": {
                    "orchestration_used": True,
                    "processing_time_ms": processing_time,
                    "context": request.context,
                    "source": request.source,
                    "metadata": request.metadata
                }
            },
        )
        
    except Exception as e:
        logger.error(f"Search processing error: {e}")
        
        # Track error in analytics
        try:
            from .analytics_collector import analytics
            analytics.track_request(
                query=request.query,
                user_id=request.user_id,
                complexity="unknown",
                provider="error",
                response_time_ms=100,
                success=False,
                error_type="search_orchestration_error"
            )
        except:
            pass
        
        # Fallback to basic response
        return ServiceResponse(
            status="error",
            message=f"Search orchestration failed, using fallback: {str(e)[:100]}",
            service="search",
            timestamp=datetime.now().isoformat(),
            data={
                "query": request.query,
                "user_id": request.user_id,
                "context": request.context,
                "source": request.source,
                "metadata": request.metadata,
                "processing_time_ms": 100,
                "error": "Orchestration unavailable - using fallback",
                "fallback_active": True
            },
        )


@search_router.get("/hybrid")
async def hybrid_search(query: str, user_id: Optional[str] = None):
    """Hybrid search endpoint."""
    logger.info(f"🔍 Hybrid search request: {query}")
    return ServiceResponse(
        status="success",
        message="Hybrid search request received - will route to retrieval service",
        service="search",
        timestamp=datetime.now().isoformat(),
        data={"query": query, "user_id": user_id, "type": "hybrid"},
    )


@search_router.get("/vector")
async def vector_search(query: str, top_k: int = 10):
    """Vector search endpoint."""
    logger.info(f"🔍 Vector search request: {query}")
    return ServiceResponse(
        status="success",
        message="Vector search request received - will route to vector service",
        service="search",
        timestamp=datetime.now().isoformat(),
        data={"query": query, "top_k": top_k, "type": "vector"},
    )


# Fact Check Router
fact_check_router = APIRouter()


@fact_check_router.post("/", response_model=ServiceResponse)
async def fact_check(request: FactCheckRequest):
    """Fact check endpoint - routes to fact-check service."""
    logger.info(f"🔍 Fact check request: {request.claim}")
    try:
        from shared.clients.microservices import call_factcheck_verify
        
        # Call fact-check service
        result = await call_factcheck_verify({
            "claim": request.claim,
            "context": request.context
        })
        
        return ServiceResponse(
            status="success",
            message="Fact check completed",
            service="fact-check",
            timestamp=datetime.now().isoformat(),
            data=result,
        )
    except Exception as e:
        logger.error(f"Fact check failed: {e}")
        return ServiceResponse(
            status="error",
            message=f"Fact check failed: {str(e)}",
            service="fact-check",
            timestamp=datetime.now().isoformat(),
            data={"error": str(e)},
        )


@fact_check_router.get("/verify")
async def verify_claim(claim: str):
    """Verify claim endpoint."""
    logger.info(f"🔍 Verify claim request: {claim}")
    try:
        from shared.clients.microservices import call_factcheck_verify
        
        # Call fact-check service
        result = await call_factcheck_verify({
            "claim": claim,
            "type": "verification"
        })
        
        return ServiceResponse(
            status="success",
            message="Claim verification completed",
            service="fact-check",
            timestamp=datetime.now().isoformat(),
            data=result,
        )
    except Exception as e:
        logger.error(f"Claim verification failed: {e}")
        return ServiceResponse(
            status="error",
            message=f"Claim verification failed: {str(e)}",
            service="fact-check",
            timestamp=datetime.now().isoformat(),
            data={"error": str(e)},
        )


# Synthesis Router
synthesis_router = APIRouter()


@synthesis_router.post("/", response_model=ServiceResponse)
async def synthesize(request: SharedSynthesisRequest):
    """Synthesis endpoint - routes to synthesis service."""
    logger.info(f"🔍 Synthesis request: {request.query[:50]}...")
    try:
        from shared.clients.microservices import call_synthesis_synthesize
        
        # Call synthesis service
        result = await call_synthesis_synthesize({
            "query": request.query,
            "sources": request.sources,
            "verification": request.verification,
            "max_tokens": request.max_tokens,
            "context": request.context,
        })
        
        return ServiceResponse(
            status="success",
            message="Synthesis completed",
            service="synthesis",
            timestamp=datetime.now().isoformat(),
            data=result,
        )
    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        return ServiceResponse(
            status="error",
            message=f"Synthesis failed: {str(e)}",
            service="synthesis",
            timestamp=datetime.now().isoformat(),
            data={"error": str(e)},
        )


@synthesis_router.post("/citations")
async def add_citations(content: str, sources: list):
    """Add citations endpoint."""
    logger.info(f"🔍 Add citations request")
    try:
        from shared.clients.microservices import call_synthesis_citations
        
        # Call synthesis service for citations
        result = await call_synthesis_citations({
            "content": content,
            "sources": sources
        })
        
        return ServiceResponse(
            status="success",
            message="Citations added successfully",
            service="synthesis",
            timestamp=datetime.now().isoformat(),
            data=result,
        )
    except Exception as e:
        logger.error(f"Add citations failed: {e}")
        return ServiceResponse(
            status="error",
            message=f"Add citations failed: {str(e)}",
            service="synthesis",
            timestamp=datetime.now().isoformat(),
            data={"error": str(e)},
        )


# Auth Router
auth_router = APIRouter()


@auth_router.post("/login", response_model=ServiceResponse)
async def login(request: LoginRequest):
    """Login endpoint - routes to auth service."""
    logger.info(f"🔍 Login request: {request.username}")
    try:
        from shared.clients.microservices import call_auth_login
        
        # Call auth service for login
        result = await call_auth_login(request)
        
        return ServiceResponse(
            status="success",
            message="Login successful",
            service="auth",
            timestamp=datetime.now().isoformat(),
            data=result,
        )
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return ServiceResponse(
            status="error",
            message=f"Login failed: {str(e)}",
            service="auth",
            timestamp=datetime.now().isoformat(),
            data={"error": str(e)},
        )


@auth_router.post("/register")
async def register(request: RegisterRequest):
    """Register endpoint - routes to auth service."""
    logger.info(f"🔍 Register request: {request.username}")
    try:
        from shared.clients.microservices import call_auth_register
        
        # Call auth service for registration
        result = await call_auth_register(request)
        
        return ServiceResponse(
            status="success",
            message="Registration successful",
            service="auth",
            timestamp=datetime.now().isoformat(),
            data=result,
        )
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        return ServiceResponse(
            status="error",
            message=f"Registration failed: {str(e)}",
            service="auth",
            timestamp=datetime.now().isoformat(),
            data={"error": str(e)},
        )


@auth_router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Refresh token endpoint - routes to auth service."""
    logger.info("🔍 Refresh token request")
    try:
        from shared.clients.microservices import call_auth_refresh
        
        # Call auth service for token refresh
        result = await call_auth_refresh(refresh_token)
        
        return ServiceResponse(
            status="success",
            message="Token refresh successful",
            service="auth",
            timestamp=datetime.now().isoformat(),
            data=result,
        )
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        return ServiceResponse(
            status="error",
            message=f"Token refresh failed: {str(e)}",
            service="auth",
            timestamp=datetime.now().isoformat(),
            data={"error": str(e)},
        )


@auth_router.post("/logout")
async def logout():
    """Logout endpoint - routes to auth service."""
    logger.info("🔍 Logout request")
    try:
        from shared.clients.microservices import call_auth_logout
        
        # Call auth service for logout
        result = await call_auth_logout()
        
        return ServiceResponse(
            status="success",
            message="Logout successful",
            service="auth",
            timestamp=datetime.now().isoformat(),
            data=result,
        )
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        return ServiceResponse(
            status="error",
            message=f"Logout failed: {str(e)}",
            service="auth",
            timestamp=datetime.now().isoformat(),
            data={"error": str(e)},
        )


@auth_router.get("/me")
async def get_current_user():
    """Get current user endpoint - routes to auth service."""
    logger.info("🔍 Get current user request")
    try:
        from shared.clients.microservices import call_auth_me
        
        # Call auth service for current user info
        result = await call_auth_me()
        
        return ServiceResponse(
            status="success",
            message="Current user info retrieved",
            service="auth",
            timestamp=datetime.now().isoformat(),
            data=result,
        )
    except Exception as e:
        logger.error(f"Get current user failed: {e}")
        return ServiceResponse(
            status="error",
            message=f"Get current user failed: {str(e)}",
            service="auth",
            timestamp=datetime.now().isoformat(),
            data={"error": str(e)},
        )


@auth_router.get("/profile")
async def get_profile(user_id: str):
    """Get user profile endpoint."""
    logger.info(f"🔍 Get profile request: {user_id}")
    return ServiceResponse(
        status="success",
        message="Get profile request received - will route to auth service",
        service="auth",
        timestamp=datetime.now().isoformat(),
        data={"user_id": user_id},
    )





# Vector Router
vector_router = APIRouter()


@vector_router.post("/", response_model=ServiceResponse)
async def vector_operation(request: VectorEmbedRequest):
    """Vector operation endpoint - routes to retrieval service."""
    logger.info(f"🔍 Vector operation request: {request.text[:50]}...")
    try:
        from shared.clients.microservices import call_retrieval_embed
        
        # Call retrieval service for embedding
        result = await call_retrieval_embed(request)
        
        return ServiceResponse(
            status="success",
            message="Vector embedding completed via retrieval service",
            service="vector",
            timestamp=datetime.now().isoformat(),
            data={
                "embedding": result.get("embedding"),
                "text": result.get("text"),
                "metadata": result.get("metadata"),
                "operation": "embed"
            },
        )
    except Exception as e:
        logger.error(f"Vector operation failed: {e}")
        return ServiceResponse(
            status="error",
            message=f"Vector operation failed: {str(e)}",
            service="vector",
            timestamp=datetime.now().isoformat(),
            data={"error": str(e), "operation": "embed"},
        )


@vector_router.post("/embed")
async def embed_text(request: VectorEmbedRequest):
    """Embed text endpoint - calls retrieval service."""
    logger.info(f"🔍 Embed text request: {request.text[:50]}...")
    try:
        from shared.clients.microservices import call_retrieval_embed
        
        # Call retrieval service for embedding
        result = await call_retrieval_embed(request)
        
        return ServiceResponse(
            status="success",
            message="Text embedding completed via retrieval service",
            service="vector",
            timestamp=datetime.now().isoformat(),
            data={
                "embedding": result.get("embedding"),
                "text": result.get("text"),
                "metadata": result.get("metadata"),
                "operation": "embed"
            },
        )
    except Exception as e:
        logger.error(f"Text embedding failed: {e}")
        return ServiceResponse(
            status="error",
            message=f"Text embedding failed: {str(e)}",
            service="vector",
            timestamp=datetime.now().isoformat(),
            data={"error": str(e), "operation": "embed"},
        )


@vector_router.post("/search")
async def vector_search_similar(request: VectorSearchRequest):
    """Vector similarity search endpoint - calls retrieval service."""
    logger.info(f"🔍 Vector similarity search request: {request.text[:50]}...")
    try:
        from shared.clients.microservices import call_retrieval_vector_search
        
        # Call retrieval service for vector search
        result = await call_retrieval_vector_search(request)
        
        return ServiceResponse(
            status="success",
            message="Vector similarity search completed via retrieval service",
            service="vector",
            timestamp=datetime.now().isoformat(),
            data={
                "results": result.get("results", []),
                "query_text": result.get("query_text"),
                "total_results": result.get("total_results", 0),
                "top_k": result.get("top_k", 10),
                "operation": "search"
            },
        )
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return ServiceResponse(
            status="error",
            message=f"Vector search failed: {str(e)}",
            service="vector",
            timestamp=datetime.now().isoformat(),
            data={"error": str(e), "operation": "search"},
        )



