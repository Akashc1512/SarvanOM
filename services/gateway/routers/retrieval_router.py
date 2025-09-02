#!/usr/bin/env python3
"""
Retrieval Router - Phase C1 Implementation

This router exposes the retrieval aggregator service endpoints:
- /search: Main search endpoint with query aggregation
- /search/status: Source health and rate limiting status
- /search/sources: Available knowledge sources
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from shared.core.services.retrieval_aggregator import get_retrieval_aggregator, SourceResult, AggregatedResults

router = APIRouter(prefix="/search", tags=["retrieval"])

class SearchRequest(BaseModel):
    """Search request model."""
    query: str
    max_results: int = 10
    use_cache: bool = True

class SearchResponse(BaseModel):
    """Search response model."""
    query: str
    results: List[dict]
    total_sources: int
    successful_sources: int
    failed_sources: int
    query_time_ms: float
    deduplication_ratio: float
    timestamp: datetime

class SourceStatus(BaseModel):
    """Source status model."""
    name: str
    available: bool
    backoff_until: Optional[float]
    consecutive_failures: int
    requests_in_window: int
    max_requests: int

@router.post("/", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search across multiple knowledge sources.
    
    Args:
        request: Search request with query and parameters
        
    Returns:
        Aggregated and deduplicated search results
    """
    try:
        aggregator = get_retrieval_aggregator()
        
        # Perform search
        results = await aggregator.search(
            query=request.query,
            max_results=request.max_results,
            use_cache=request.use_cache
        )
        
        # Convert results to response format
        response_results = []
        for result in results.get_top_k(request.max_results):
            response_results.append({
                "title": result.title,
                "url": result.url,
                "snippet": result.snippet,
                "provider": result.provider,
                "domain": result.domain,
                "timestamp": result.timestamp.isoformat(),
                "scores": {
                    "relevance": result.relevance_score,
                    "credibility": result.credibility_score,
                    "recency": result.recency_score,
                    "diversity": result.diversity_score,
                    "combined": result.relevance_score * result.credibility_score * result.recency_score * result.diversity_score
                }
            })
        
        return SearchResponse(
            query=request.query,
            results=response_results,
            total_sources=results.total_sources,
            successful_sources=results.successful_sources,
            failed_sources=results.failed_sources,
            query_time_ms=results.query_time_ms,
            deduplication_ratio=results.deduplication_ratio,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/status", response_model=List[SourceStatus])
async def get_source_status():
    """
    Get health and rate limiting status of all knowledge sources.
    
    Returns:
        List of source status information
    """
    try:
        aggregator = get_retrieval_aggregator()
        status = aggregator.get_source_status()
        
        source_status_list = []
        for source_name, source_info in status.items():
            source_status_list.append(SourceStatus(
                name=source_name,
                available=source_info['available'],
                backoff_until=source_info['backoff_until'] if source_info['backoff_until'] > 0 else None,
                consecutive_failures=source_info['consecutive_failures'],
                requests_in_window=source_info['requests_in_window'],
                max_requests=source_info['max_requests']
            ))
        
        return source_status_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@router.get("/sources")
async def get_available_sources():
    """
    Get list of available knowledge sources.
    
    Returns:
        Dictionary of available sources with their capabilities
    """
    sources = {
        "wikipedia": {
            "name": "Wikipedia",
            "description": "Free encyclopedia articles",
            "rate_limit": "30 requests/minute",
            "credibility": "High",
            "coverage": "General knowledge"
        },
        "stackexchange": {
            "name": "Stack Overflow",
            "description": "Programming Q&A and technical discussions",
            "rate_limit": "100 requests/minute",
            "credibility": "High",
            "coverage": "Technical/programming"
        },
        "mdn": {
            "name": "MDN Web Docs",
            "description": "Web development documentation",
            "rate_limit": "50 requests/minute",
            "credibility": "High",
            "coverage": "Web development"
        },
        "github": {
            "name": "GitHub",
            "description": "Open source repositories and code",
            "rate_limit": "10 requests/minute (unauthenticated)",
            "credibility": "Medium",
            "coverage": "Code and projects"
        }
    }
    
    return {
        "available_sources": sources,
        "total_sources": len(sources),
        "note": "All sources are free and respect API rate limits"
    }

@router.get("/health")
async def health_check():
    """
    Health check for the retrieval aggregator service.
    
    Returns:
        Health status and basic metrics
    """
    try:
        aggregator = get_retrieval_aggregator()
        status = aggregator.get_source_status()
        
        # Calculate overall health
        available_sources = sum(1 for s in status.values() if s['available'])
        total_sources = len(status)
        health_percentage = (available_sources / total_sources) * 100 if total_sources > 0 else 0
        
        return {
            "status": "healthy" if health_percentage >= 75 else "degraded",
            "available_sources": available_sources,
            "total_sources": total_sources,
            "health_percentage": health_percentage,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
