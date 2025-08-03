"""
Retrieval Microservice API
RESTful API endpoints for the retrieval service.

This module provides:
- Search endpoints
- Query processing endpoints
- Health check endpoints
- Error handling
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from .search_service import SearchService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/retrieval", tags=["retrieval"])

# Initialize service
search_service = SearchService()

# Request/Response Models
class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 10
    search_type: Optional[str] = "hybrid"  # "vector", "keyword", "hybrid"

class SearchResponse(BaseModel):
    results: list
    total: int
    query: str
    search_type: str
    query_time_ms: int
    status: str
    query_id: str

class QueryAnalysisRequest(BaseModel):
    query: str

class QueryAnalysisResponse(BaseModel):
    intent: str
    complexity: str
    entities: list
    language: str
    confidence: float

class HealthCheckResponse(BaseModel):
    service: str
    status: str
    components: Dict[str, str]
    timestamp: str

@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Search for documents using the retrieval service."""
    try:
        logger.info(f"Processing search request: {request.query}")
        
        result = await search_service.search(
            query=request.query,
            filters=request.filters,
            limit=request.limit
        )
        
        return SearchResponse(
            results=result.get("results", []),
            total=result.get("total", 0),
            query=request.query,
            search_type=result.get("search_type", "hybrid"),
            query_time_ms=result.get("query_time_ms", 0),
            status=result.get("status", "success"),
            query_id=result.get("query_id", "")
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/{query_id}")
async def get_search_result(query_id: str):
    """Get a specific search result by ID."""
    try:
        result = await search_service.get_result(query_id)
        return result
    except Exception as e:
        logger.error(f"Failed to get search result {query_id}: {e}")
        raise HTTPException(status_code=404, detail="Search result not found")

@router.post("/analyze", response_model=QueryAnalysisResponse)
async def analyze_query(request: QueryAnalysisRequest):
    """Analyze a query for intent, complexity, and entities."""
    try:
        logger.info(f"Analyzing query: {request.query}")
        
        # This would use the QueryProcessor from the service
        # For now, return a basic analysis
        analysis = {
            "intent": "information_retrieval",
            "complexity": "medium",
            "entities": [],
            "language": "en",
            "confidence": 0.8
        }
        
        return QueryAnalysisResponse(**analysis)
        
    except Exception as e:
        logger.error(f"Query analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint for the retrieval service."""
    try:
        health = await search_service.health_check()
        return HealthCheckResponse(**health)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@router.get("/status")
async def service_status():
    """Get detailed service status."""
    try:
        health = await search_service.health_check()
        return {
            "service": "retrieval",
            "version": "2.0.0",
            "status": health.get("status", "unknown"),
            "components": health.get("components", {}),
            "endpoints": {
                "search": "/api/v1/retrieval/search",
                "analyze": "/api/v1/retrieval/analyze",
                "health": "/api/v1/retrieval/health"
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 