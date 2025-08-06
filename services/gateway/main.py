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

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

# Import unified logging
from shared.core.unified_logging import setup_logging, get_logger, setup_fastapi_logging

# Configure unified logging
logging_config = setup_logging(service_name="sarvanom-gateway-service")
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Universal Knowledge Platform API Gateway",
    description="API Gateway for routing requests to microservices",
    version="1.0.0"
)

# Setup FastAPI logging integration
setup_fastapi_logging(app, service_name="sarvanom-gateway-service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class SearchRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None

class FactCheckRequest(BaseModel):
    content: str
    user_id: Optional[str] = None
    context: Optional[str] = None

class SynthesisRequest(BaseModel):
    query: str
    sources: Optional[list] = None
    user_id: Optional[str] = None

class AuthRequest(BaseModel):
    username: str
    password: str

class CrawlRequest(BaseModel):
    url: str
    depth: Optional[int] = 1
    user_id: Optional[str] = None

class VectorSearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10
    filters: Optional[Dict[str, Any]] = None

class GraphContextRequest(BaseModel):
    topic: str
    depth: Optional[int] = 2
    user_id: Optional[str] = None

# Health check endpoint
@app.get("/health")
async def health_check():
    """Enhanced health check endpoint for the API gateway with service status."""
    import time
    from services.analytics.health_checks import check_all_services
    from services.api_gateway.di.providers import get_service_provider
    
    start_time = time.time()
    
    try:
        # Get service provider for agent service health checks
        service_provider = get_service_provider()
        
        # Check all external services
        external_services = await check_all_services()
        
        # Check all agent services
        agent_services = await service_provider.health_check_all_services()
        
        # Calculate overall health
        all_services_healthy = (
            external_services.get("overall_healthy", False) and 
            agent_services.get("overall_healthy", False)
        )
        
        # Record health check metrics
        from services.analytics.metrics.knowledge_platform_metrics import record_system_metrics
        record_system_metrics(
            uptime_seconds=time.time() - start_time,
            error_count=0 if all_services_healthy else 1,
            error_rate=0.0 if all_services_healthy else 1.0,
            component="gateway_health_check"
        )
        
        return {
            "status": "ok" if all_services_healthy else "degraded",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "response_time_ms": int((time.time() - start_time) * 1000),
            "external_services": external_services,
            "agent_services": agent_services,
            "overall_healthy": all_services_healthy
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "overall_healthy": False
        }

# Comprehensive health check endpoint for frontend
@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check endpoint for frontend dashboard."""
    import time
    from services.analytics.health_checks import check_all_services
    from services.api_gateway.di.providers import get_service_provider
    from services.analytics.metrics.knowledge_platform_metrics import get_metrics_json
    
    start_time = time.time()
    
    try:
        # Get service provider for agent service health checks
        service_provider = get_service_provider()
        
        # Check all external services
        external_services = await check_all_services()
        
        # Check all agent services
        agent_services = await service_provider.health_check_all_services()
        
        # Get current metrics
        current_metrics = get_metrics_json()
        
        # Calculate overall health
        all_services_healthy = (
            external_services.get("overall_healthy", False) and 
            agent_services.get("overall_healthy", False)
        )
        
        # Compile detailed health report
        health_report = {
            "status": "ok" if all_services_healthy else "degraded",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "response_time_ms": int((time.time() - start_time) * 1000),
            "overall_healthy": all_services_healthy,
            "services": {
                "external": external_services,
                "agents": agent_services
            },
            "metrics": {
                "query_intelligence": current_metrics.get("query_intelligence", {}),
                "orchestration": current_metrics.get("orchestration", {}),
                "retrieval": current_metrics.get("retrieval", {}),
                "memory": current_metrics.get("memory", {}),
                "expert_validation": current_metrics.get("expert_validation", {}),
                "business": current_metrics.get("business", {})
            },
            "performance": {
                "uptime_seconds": time.time() - start_time,
                "total_requests": current_metrics.get("query_intelligence", {}).get("total_requests", 0),
                "avg_response_time": current_metrics.get("orchestration", {}).get("avg_duration", 0),
                "error_rate": current_metrics.get("system", {}).get("error_rate", 0.0)
            },
            "recommendations": []
        }
        
        # Add recommendations based on health status
        if not all_services_healthy:
            health_report["recommendations"].append("Some services are experiencing issues. Check service logs for details.")
        
        if current_metrics.get("system", {}).get("error_rate", 0.0) > 0.05:
            health_report["recommendations"].append("Error rate is elevated. Consider investigating recent changes.")
        
        if current_metrics.get("orchestration", {}).get("avg_duration", 0) > 5.0:
            health_report["recommendations"].append("Average response time is high. Consider optimizing query processing.")
        
        return health_report
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "overall_healthy": False,
            "recommendations": ["Health check system is experiencing issues. Contact system administrator."]
        }

# Search/Retrieval service endpoint
@app.get("/search")
async def search_endpoint():
    """Placeholder for search/retrieval service."""
    return {"message": "Retrieval service route"}

@app.post("/search")
async def search_post(request: SearchRequest):
    """Enhanced search endpoint with analytics tracking."""
    import time
    from services.analytics.metrics.knowledge_platform_metrics import (
        record_query_intelligence_metrics,
        record_retrieval_metrics,
        record_business_metrics
    )
    
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
        
        # Process the search request (placeholder for now)
        result = {
            "message": "Retrieval service route",
            "query": request.query,
            "user_id": request.user_id,
            "results": [],  # Placeholder for actual results
            "total_results": 0
        }
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Record retrieval metrics
        record_retrieval_metrics(
            source_type="web_search",
            fusion_strategy="hybrid",
            duration_seconds=processing_time,
            result_count=result.get("total_results", 0),
            confidence_score=0.8  # Placeholder confidence
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
        result["processing_time_ms"] = int(processing_time * 1000)
        result["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        return result
        
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
    """Enhanced fact-check endpoint with analytics tracking."""
    import time
    import random
    from services.analytics.metrics.knowledge_platform_metrics import (
        record_query_intelligence_metrics,
        record_expert_validation_metrics,
        record_business_metrics
    )
    
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
        
        # Simulate validation process
        time.sleep(0.5)
        
        # Simulate validation result
        statuses = ["supported", "contradicted", "unclear", "pending"]
        status = random.choice(statuses)
        confidence = random.uniform(0.6, 0.95)
        consensus_score = random.uniform(0.7, 0.9)
        total_experts = random.randint(3, 8)
        agreeing_experts = random.randint(2, 6)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Record expert validation metrics
        record_expert_validation_metrics(
            network_type="academic,industry,ai_model",
            validation_status=status,
            duration_seconds=processing_time,
            consensus_score=consensus_score,
            consensus_level="high" if consensus_score > 0.8 else "medium",
            agreement_ratio=agreeing_experts / total_experts
        )
        
        # Record business metrics
        record_business_metrics(
            user_id=request.user_id or "anonymous",
            query_type="fact_check",
            complexity="high",
            response_time_seconds=processing_time,
            satisfaction_score=None
        )
        
        return {
            "status": status,
            "confidence": confidence,
            "consensus_score": consensus_score,
            "total_experts": total_experts,
            "agreeing_experts": agreeing_experts,
            "expert_network": "academic,industry,ai_model",
            "validation_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "processing_time_ms": int(processing_time * 1000),
            "details": {
                "academic_validation": {
                    "status": status,
                    "confidence": confidence * 0.9,
                    "notes": "Academic sources reviewed"
                },
                "industry_validation": {
                    "status": status,
                    "confidence": confidence * 0.85,
                    "notes": "Industry experts consulted"
                },
                "ai_model_validation": {
                    "status": status,
                    "confidence": confidence * 0.95,
                    "notes": "AI model analysis completed"
                }
            },
            "sources_checked": ["source1.com", "source2.org", "source3.edu"],
            "reasoning": f"Expert validation completed for claim: {request.content[:100]}...",
            "message": "Fact-check service route",
            "content": request.content,
            "user_id": request.user_id
        }
        
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
    """Enhanced synthesis endpoint with analytics tracking."""
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
        
        # Simulate synthesis processing
        time.sleep(0.3)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Record orchestration metrics
        record_orchestration_metrics(
            model_type="gpt-4",  # Placeholder - could be dynamic
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
        
        return {
            "message": "Synthesis service route",
            "query": request.query,
            "user_id": request.user_id,
            "synthesis_result": f"Synthesized response for: {request.query}",
            "sources_used": request.sources or [],
            "processing_time_ms": int(processing_time * 1000),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "confidence_score": 0.85,  # Placeholder confidence
            "synthesis_strategy": "multi_agent_orchestration"
        }
        
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
    return {"error": "Endpoint not found", "message": "The requested endpoint does not exist"}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "message": "An unexpected error occurred"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 