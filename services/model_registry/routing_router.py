"""
Model Registry Routing Router - SarvanOM v2

Router for model routing endpoints including /route and /refine.
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
import asyncio
import time

# Create router
router = APIRouter(prefix="/api/v1", tags=["model-routing"])

# Prometheus metrics for observability
from prometheus_client import Counter, Histogram, Gauge

# Metrics with model_family, task, fallback tags
routing_requests_total = Counter(
    'sarvanom_routing_requests_total', 
    'Total routing requests', 
    ['model_family', 'task', 'fallback']
)

routing_duration_seconds = Histogram(
    'sarvanom_routing_duration_seconds',
    'Routing request duration',
    ['model_family', 'task', 'fallback']
)

routing_fallback_count = Counter(
    'sarvanom_routing_fallback_total',
    'Routing fallback count',
    ['from_model_family', 'to_model_family', 'task']
)

# Pydantic models
class RouteRequest(BaseModel):
    query: str
    task: str = "general"  # general, refinement, analysis, etc.
    context: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None

class RouteResponse(BaseModel):
    model_id: str
    model_family: str
    provider: str
    confidence: float
    reasoning: str
    fallback_models: List[str]
    estimated_cost: float
    estimated_latency: float

class RefineRequest(BaseModel):
    query: str
    original_response: str
    refinement_type: str = "improve"  # improve, clarify, expand, etc.
    context: Optional[Dict[str, Any]] = None

class RefineResponse(BaseModel):
    refined_query: str
    model_id: str
    model_family: str
    provider: str
    confidence: float
    reasoning: str

@router.post("/route", response_model=RouteResponse)
async def route_query(request: RouteRequest, http_request: Request):
    """Route query to appropriate model based on task and context"""
    start_time = time.time()
    
    try:
        # Get available models from registry
        registry = http_request.app.state.model_registry
        available_models = list(registry.models.values())
        
        if not available_models:
            raise HTTPException(status_code=503, detail="No models available")
        
        # Simple routing logic based on task
        selected_model = None
        fallback_models = []
        model_family = "unknown"
        fallback_used = False
        
        if request.task == "refinement":
            # Prefer fast, cheap models for refinement
            for model in available_models:
                if model.model_family in ["gpt-3.5-turbo", "claude-3-haiku"]:
                    selected_model = model
                    model_family = model.model_family
                    break
        elif request.task == "analysis":
            # Prefer more capable models for analysis
            for model in available_models:
                if model.model_family in ["gpt-4o", "claude-3-5-sonnet"]:
                    selected_model = model
                    model_family = model.model_family
                    break
        else:
            # General task - use first available model
            selected_model = available_models[0]
            model_family = selected_model.model_family
        
        # If no specific model found, use fallback
        if not selected_model:
            selected_model = available_models[0]
            model_family = selected_model.model_family
            fallback_used = True
        
        # Create fallback list (exclude selected model)
        fallback_models = [
            model.model_id for model in available_models 
            if model.model_id != selected_model.model_id
        ][:3]  # Limit to 3 fallbacks
        
        # Calculate confidence based on model performance
        confidence = selected_model.performance.quality_score if selected_model.performance else 0.8
        
        # Estimate cost and latency
        estimated_cost = 0.001  # Simplified calculation
        estimated_latency = selected_model.performance.avg_completion_ms / 1000.0 if selected_model.performance else 1.0
        
        # Record metrics
        routing_requests_total.labels(
            model_family=model_family,
            task=request.task,
            fallback="true" if fallback_used else "false"
        ).inc()
        
        duration = time.time() - start_time
        routing_duration_seconds.labels(
            model_family=model_family,
            task=request.task,
            fallback="true" if fallback_used else "false"
        ).observe(duration)
        
        if fallback_used:
            routing_fallback_count.labels(
                from_model_family="none",
                to_model_family=model_family,
                task=request.task
            ).inc()
        
        return RouteResponse(
            model_id=selected_model.model_id,
            model_family=model_family,
            provider=selected_model.provider,
            confidence=confidence,
            reasoning=f"Selected {model_family} for {request.task} task",
            fallback_models=fallback_models,
            estimated_cost=estimated_cost,
            estimated_latency=estimated_latency
        )
        
    except Exception as e:
        # Record error metrics
        routing_requests_total.labels(
            model_family="error",
            task=request.task,
            fallback="true"
        ).inc()
        
        raise HTTPException(status_code=500, detail=f"Routing failed: {str(e)}")

@router.post("/refine", response_model=RefineResponse)
async def refine_query(request: RefineRequest, http_request: Request):
    """Refine query for better results (refiner path wired)"""
    start_time = time.time()
    
    try:
        # Get available models from registry
        registry = http_request.app.state.model_registry
        available_models = list(registry.models.values())
        
        if not available_models:
            raise HTTPException(status_code=503, detail="No models available")
        
        # Select refiner model (prefer fast, cheap models)
        refiner_model = None
        model_family = "unknown"
        
        for model in available_models:
            if model.model_family in ["gpt-3.5-turbo", "claude-3-haiku"]:
                refiner_model = model
                model_family = model.model_family
                break
        
        # Fallback to first available model
        if not refiner_model:
            refiner_model = available_models[0]
            model_family = refiner_model.model_family
        
        # Simple refinement logic
        refined_query = request.query
        if request.refinement_type == "improve":
            refined_query = f"Please improve this query for better results: {request.query}"
        elif request.refinement_type == "clarify":
            refined_query = f"Please clarify this query: {request.query}"
        elif request.refinement_type == "expand":
            refined_query = f"Please expand this query with more context: {request.query}"
        
        # Calculate confidence
        confidence = refiner_model.performance.quality_score if refiner_model.performance else 0.8
        
        # Record metrics
        routing_requests_total.labels(
            model_family=model_family,
            task="refinement",
            fallback="false"
        ).inc()
        
        duration = time.time() - start_time
        routing_duration_seconds.labels(
            model_family=model_family,
            task="refinement",
            fallback="false"
        ).observe(duration)
        
        return RefineResponse(
            refined_query=refined_query,
            model_id=refiner_model.model_id,
            model_family=model_family,
            provider=refiner_model.provider,
            confidence=confidence,
            reasoning=f"Refined query using {model_family} for {request.refinement_type}"
        )
        
    except Exception as e:
        # Record error metrics
        routing_requests_total.labels(
            model_family="error",
            task="refinement",
            fallback="true"
        ).inc()
        
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")
