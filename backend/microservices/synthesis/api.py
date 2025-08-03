"""
Synthesis Microservice API
RESTful API endpoints for the synthesis service.

This module provides:
- Content synthesis endpoints
- Citation management endpoints
- Health check endpoints
- Error handling
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from .synthesis_service import SynthesisService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/synthesis", tags=["synthesis"])

# Initialize service
synthesis_service = SynthesisService()

# Request/Response Models
class SynthesisRequest(BaseModel):
    query: str
    search_results: List[Dict[str, Any]]
    fact_check_results: Optional[Dict[str, Any]] = None
    style: Optional[str] = "academic"

class SynthesisResponse(BaseModel):
    content: str
    citations: List[Dict[str, Any]]
    confidence: float
    synthesis_time_ms: int
    synthesis_id: str
    status: str

class CitationRequest(BaseModel):
    content: str
    sources: List[Dict[str, Any]]

class CitationResponse(BaseModel):
    content: str
    citations: List[Dict[str, Any]]
    citation_count: int

class HealthCheckResponse(BaseModel):
    service: str
    status: str
    components: Dict[str, str]
    timestamp: str

@router.post("/synthesize", response_model=SynthesisResponse)
async def synthesize_content(request: SynthesisRequest):
    """Synthesize content from search results."""
    try:
        logger.info(f"Processing synthesis request for query: {request.query}")
        
        result = await synthesis_service.synthesize(
            query=request.query,
            search_results=request.search_results,
            fact_check_results=request.fact_check_results
        )
        
        return SynthesisResponse(**result)
        
    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/result/{synthesis_id}")
async def get_synthesis_result(synthesis_id: str):
    """Get a specific synthesis result by ID."""
    try:
        result = await synthesis_service.get_result(synthesis_id)
        return result
    except Exception as e:
        logger.error(f"Failed to get synthesis result {synthesis_id}: {e}")
        raise HTTPException(status_code=404, detail="Synthesis result not found")

@router.post("/add-citations", response_model=CitationResponse)
async def add_citations(request: CitationRequest):
    """Add citations to content."""
    try:
        logger.info(f"Adding citations to content of length: {len(request.content)}")
        
        # For now, return a mock citation result
        # In a real implementation, this would use the actual citation logic
        citations = []
        for i, source in enumerate(request.sources):
            citations.append({
                "id": f"citation_{i}",
                "source": source.get("source", f"source_{i}"),
                "text": source.get("text", "")[:100],
                "position": i
            })
        
        result = {
            "content": request.content,
            "citations": citations,
            "citation_count": len(citations)
        }
        
        return CitationResponse(**result)
        
    except Exception as e:
        logger.error(f"Citation addition failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint for the synthesis service."""
    try:
        health = await synthesis_service.health_check()
        return HealthCheckResponse(**health)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@router.get("/status")
async def service_status():
    """Get detailed service status."""
    try:
        health = await synthesis_service.health_check()
        return {
            "service": "synthesis",
            "version": "2.0.0",
            "status": health.get("status", "unknown"),
            "components": health.get("components", {}),
            "endpoints": {
                "synthesize": "/api/v1/synthesis/synthesize",
                "add_citations": "/api/v1/synthesis/add-citations",
                "health": "/api/v1/synthesis/health"
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 