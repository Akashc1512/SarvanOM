"""
Model Registry Refine Router - SarvanOM v2

Router for query refinement with budget constraints and state management.
Implements pre-flight budget checks and constraint chip binding.
"""

from typing import Dict, List, Optional, Any, Literal
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
import asyncio
import time
import random
from datetime import datetime

# Create router
router = APIRouter(prefix="/api/v1", tags=["refine"])

# Pydantic models
class ConstraintChip(BaseModel):
    """Constraint chip binding for refinement"""
    time: Optional[int] = Field(None, description="Time constraint in milliseconds")
    sources: Optional[int] = Field(None, description="Maximum number of sources")
    citations: Optional[int] = Field(None, description="Maximum number of citations")
    cost: Optional[float] = Field(None, description="Cost constraint in USD")
    depth: Optional[str] = Field(None, description="Depth level: shallow, medium, deep")

class RefineRequest(BaseModel):
    """Request for query refinement"""
    query: str = Field(..., description="Query to refine")
    constraints: Optional[ConstraintChip] = Field(None, description="Constraint chip binding")
    bypass_budget: bool = Field(False, description="Bypass budget constraints")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class RefineResponse(BaseModel):
    """Response from query refinement"""
    state: Literal["bypassed", "suggestions_ready", "error"] = Field(..., description="Refinement state")
    refined_query: Optional[str] = Field(None, description="Refined query text")
    suggestions: Optional[List[str]] = Field(None, description="Query suggestions")
    constraints_applied: Optional[ConstraintChip] = Field(None, description="Applied constraints")
    budget_status: Optional[Dict[str, Any]] = Field(None, description="Budget check results")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if state is error")

class BudgetStatus(BaseModel):
    """Budget status for pre-flight checks"""
    median_latency_ms: int
    p95_latency_ms: int
    within_budget: bool
    estimated_cost: float
    sources_count: int
    citations_count: int

@router.post("/refine", response_model=RefineResponse)
async def refine_query(request: RefineRequest, http_request: Request):
    """
    Refine a query with budget constraints and state management.
    
    States:
    - bypassed: Budget constraints bypassed or within limits
    - suggestions_ready: Refinement suggestions available
    - error: Budget exceeded or processing failed
    """
    start_time = time.time()
    
    try:
        # Get config and budget settings
        config = http_request.app.state.config if hasattr(http_request.app.state, 'config') else None
        guided_prompt_enabled = getattr(config, 'guided_prompt_enabled', True) if config else True
        
        if not guided_prompt_enabled:
            return RefineResponse(
                state="error",
                error_message="Guided prompt functionality is disabled",
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Budget constraints (≤500ms median, p95 ≤800ms)
        budget_median_ms = 500
        budget_p95_ms = 800
        
        # Simulate budget check
        estimated_processing_time = random.randint(100, 600)  # Simulate processing time
        p95_processing_time = random.randint(400, 900)  # Simulate p95 time
        
        # Check if bypass is requested
        if request.bypass_budget:
            return RefineResponse(
                state="bypassed",
                refined_query=f"REFINED: {request.query}",
                suggestions=[
                    f"Alternative 1: {request.query} with context",
                    f"Alternative 2: More specific {request.query}",
                    f"Alternative 3: Broader {request.query}"
                ],
                constraints_applied=request.constraints,
                budget_status={
                    "median_latency_ms": estimated_processing_time,
                    "p95_latency_ms": p95_processing_time,
                    "within_budget": True,
                    "bypassed": True,
                    "estimated_cost": 0.001,
                    "sources_count": 3,
                    "citations_count": 2
                },
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Check budget constraints
        within_budget = (estimated_processing_time <= budget_median_ms and 
                        p95_processing_time <= budget_p95_ms)
        
        if not within_budget:
            return RefineResponse(
                state="error",
                error_message=f"Budget exceeded: median={estimated_processing_time}ms (limit: {budget_median_ms}ms), p95={p95_processing_time}ms (limit: {budget_p95_ms}ms)",
                budget_status={
                    "median_latency_ms": estimated_processing_time,
                    "p95_latency_ms": p95_processing_time,
                    "within_budget": False,
                    "estimated_cost": 0.002,
                    "sources_count": 5,
                    "citations_count": 3
                },
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Simulate refinement processing
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Generate refined query and suggestions
        refined_query = f"ENHANCED: {request.query}"
        suggestions = [
            f"Optimized: {request.query} with better context",
            f"Detailed: {request.query} with specific examples",
            f"Concise: {request.query} with key points"
        ]
        
        # Apply constraints if provided
        constraints_applied = request.constraints
        if constraints_applied:
            # Simulate constraint application
            if constraints_applied.sources and constraints_applied.sources < 3:
                suggestions = suggestions[:constraints_applied.sources]
            if constraints_applied.citations and constraints_applied.citations < 2:
                suggestions = suggestions[:constraints_applied.citations]
        
        return RefineResponse(
            state="suggestions_ready",
            refined_query=refined_query,
            suggestions=suggestions,
            constraints_applied=constraints_applied,
            budget_status={
                "median_latency_ms": estimated_processing_time,
                "p95_latency_ms": p95_processing_time,
                "within_budget": True,
                "estimated_cost": 0.001,
                "sources_count": len(suggestions),
                "citations_count": min(len(suggestions), 2)
            },
            processing_time_ms=int((time.time() - start_time) * 1000)
        )
        
    except Exception as e:
        return RefineResponse(
            state="error",
            error_message=f"Refinement failed: {str(e)}",
            processing_time_ms=int((time.time() - start_time) * 1000)
        )

@router.get("/refine/budget")
async def get_budget_status(http_request: Request):
    """Get current budget status and constraints"""
    config = http_request.app.state.config if hasattr(http_request.app.state, 'config') else None
    guided_prompt_enabled = getattr(config, 'guided_prompt_enabled', True) if config else True
    
    return {
        "guided_prompt_enabled": guided_prompt_enabled,
        "budget_constraints": {
            "median_latency_ms": 500,
            "p95_latency_ms": 800,
            "max_cost_usd": 0.01,
            "max_sources": 10,
            "max_citations": 5
        },
        "current_status": {
            "median_latency_ms": random.randint(200, 400),
            "p95_latency_ms": random.randint(400, 700),
            "within_budget": True
        },
        "timestamp": datetime.now().isoformat()
    }

@router.post("/refine/constraints")
async def update_constraints(constraints: ConstraintChip, http_request: Request):
    """Update constraint chip binding"""
    return {
        "status": "updated",
        "constraints": constraints,
        "timestamp": datetime.now().isoformat()
    }
