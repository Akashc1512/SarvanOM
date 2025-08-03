"""
Fact Check Microservice API
RESTful API endpoints for the fact check service.

This module provides:
- Fact verification endpoints
- Expert validation endpoints
- Health check endpoints
- Error handling
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from .factcheck_service import FactCheckService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/fact-check", tags=["fact-check"])

# Initialize service
factcheck_service = FactCheckService()

# Request/Response Models
class FactCheckRequest(BaseModel):
    content: str
    sources: Optional[List[str]] = None
    context: Optional[str] = None

class FactCheckResponse(BaseModel):
    verdict: str
    confidence: float
    sources: List[str]
    reasoning: str
    verification_time_ms: int
    check_id: str
    status: str

class ClaimValidationRequest(BaseModel):
    claim: str
    sources: List[str]

class ClaimValidationResponse(BaseModel):
    is_valid: bool
    confidence: float
    supporting_sources: List[str]
    contradicting_sources: List[str]
    reasoning: str

class HealthCheckResponse(BaseModel):
    service: str
    status: str
    components: Dict[str, str]
    timestamp: str

@router.post("/verify", response_model=FactCheckResponse)
async def verify_facts(request: FactCheckRequest):
    """Verify facts in the provided content."""
    try:
        logger.info(f"Processing fact check request for content: {request.content[:100]}...")
        
        result = await factcheck_service.verify(
            content=request.content,
            sources=request.sources
        )
        
        return FactCheckResponse(**result)
        
    except Exception as e:
        logger.error(f"Fact check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/result/{check_id}")
async def get_fact_check_result(check_id: str):
    """Get a specific fact check result by ID."""
    try:
        result = await factcheck_service.get_result(check_id)
        return result
    except Exception as e:
        logger.error(f"Failed to get fact check result {check_id}: {e}")
        raise HTTPException(status_code=404, detail="Fact check result not found")

@router.post("/validate-claim", response_model=ClaimValidationResponse)
async def validate_claim(request: ClaimValidationRequest):
    """Validate a specific claim against sources."""
    try:
        logger.info(f"Validating claim: {request.claim}")
        
        # For now, return a mock validation result
        # In a real implementation, this would use the actual validation logic
        result = {
            "is_valid": True,
            "confidence": 0.7,
            "supporting_sources": request.sources[:2] if len(request.sources) > 1 else request.sources,
            "contradicting_sources": [],
            "reasoning": f"Claim validated against {len(request.sources)} sources"
        }
        
        return ClaimValidationResponse(**result)
        
    except Exception as e:
        logger.error(f"Claim validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint for the fact check service."""
    try:
        health = await factcheck_service.health_check()
        return HealthCheckResponse(**health)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@router.get("/status")
async def service_status():
    """Get detailed service status."""
    try:
        health = await factcheck_service.health_check()
        return {
            "service": "fact_check",
            "version": "2.0.0",
            "status": health.get("status", "unknown"),
            "components": health.get("components", {}),
            "endpoints": {
                "verify": "/api/v1/fact-check/verify",
                "validate_claim": "/api/v1/fact-check/validate-claim",
                "health": "/api/v1/fact-check/health"
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 