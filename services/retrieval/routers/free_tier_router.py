#!/usr/bin/env python3
"""
FastAPI Router for Zero-Budget Retrieval

Provides REST API endpoints for free-tier search capabilities:
- Wikipedia search via MediaWiki API
- Web search via Brave/DuckDuckGo
- Combined search with caching
- Proper error handling and cache headers

Following MAANG/OpenAI/Perplexity standards for enterprise-grade APIs.
"""

from fastapi import APIRouter, HTTPException, Query, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
import logging
import time

from services.retrieval.free_tier import (
    get_zero_budget_retrieval, 
    search_with_cache_headers,
    wiki_search,
    free_web_search,
    combined_search,
    SearchResult,
    SearchResponse,
    SearchProvider
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/retrieval/free", tags=["Zero-Budget Retrieval"])


class SearchRequest(BaseModel):
    """Search request model."""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    k: int = Field(default=5, ge=1, le=20, description="Number of results to return")
    use_wiki: bool = Field(default=True, description="Include Wikipedia search")
    use_web: bool = Field(default=True, description="Include web search")
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        """Validate search query."""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class SearchResultResponse(BaseModel):
    """Search result response model."""
    title: str
    url: str
    snippet: str
    domain: str
    provider: str
    relevance_score: float
    timestamp: str
    metadata: Dict[str, Any] = {}


class SearchResponseModel(BaseModel):
    """Search response model."""
    query: str
    results: List[SearchResultResponse]
    total_results: int
    cache_hit: bool
    providers_used: List[str]
    processing_time_ms: float
    trace_id: str
    error_message: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    providers: Dict[str, bool]
    cache_available: bool
    timestamp: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for zero-budget retrieval."""
    try:
        # Check provider availability
        retrieval_system = get_zero_budget_retrieval()
        providers = {
            "mediawiki": True,  # MediaWiki is always available
            "brave": bool(retrieval_system.redis_client is not None),
            "duckduckgo": True,  # DuckDuckGo is always available
            "cache": retrieval_system.redis_client is not None
        }
        
        return HealthResponse(
            status="healthy",
            providers=providers,
            cache_available=retrieval_system.redis_client is not None,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.post("/search", response_model=SearchResponseModel)
async def search_endpoint(request: SearchRequest):
    """Combined search endpoint with caching."""
    try:
        start_time = time.time()
        
        logger.info(f"Search request: {request.query}", extra={
            "query": request.query,
            "k": request.k,
            "use_wiki": request.use_wiki,
            "use_web": request.use_web
        })
        
        # Perform search
        response, headers = await search_with_cache_headers(
            query=request.query,
            k=request.k,
            use_wiki=request.use_wiki,
            use_web=request.use_web
        )
        
        # Convert results to response model
        result_responses = []
        for result in response.results:
            result_responses.append(SearchResultResponse(
                title=result.title,
                url=result.url,
                snippet=result.snippet,
                domain=result.domain,
                provider=result.provider.value,
                relevance_score=result.relevance_score,
                timestamp=result.timestamp.isoformat(),
                metadata=result.metadata
            ))
        
        # Create response
        search_response = SearchResponseModel(
            query=response.query,
            results=result_responses,
            total_results=response.total_results,
            cache_hit=response.cache_hit,
            providers_used=[p.value for p in response.providers_used],
            processing_time_ms=response.processing_time_ms,
            trace_id=response.trace_id,
            error_message=response.error_message
        )
        
        # Return with cache headers
        return JSONResponse(
            content=search_response.model_dump(),
            headers=headers
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}", extra={"query": request.query})
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/wiki", response_model=SearchResponseModel)
async def wiki_search_endpoint(
    query: str = Query(..., min_length=1, max_length=500),
    k: int = Query(default=3, ge=1, le=10)
):
    """Wikipedia search endpoint."""
    try:
        start_time = time.time()
        
        logger.info(f"Wikipedia search request: {query}", extra={
            "query": query,
            "k": k
        })
        
        # Perform Wikipedia search
        results = await wiki_search(query, k)
        
        # Convert to response format
        result_responses = []
        for result in results:
            result_responses.append(SearchResultResponse(
                title=result.title,
                url=result.url,
                snippet=result.snippet,
                domain=result.domain,
                provider=result.provider.value,
                relevance_score=result.relevance_score,
                timestamp=result.timestamp.isoformat(),
                metadata=result.metadata
            ))
        
        processing_time = (time.time() - start_time) * 1000
        
        return SearchResponseModel(
            query=query,
            results=result_responses,
            total_results=len(results),
            cache_hit=False,  # Wikipedia search doesn't use cache
            providers_used=["mediawiki"],
            processing_time_ms=processing_time,
            trace_id=str(time.time())
        )
        
    except Exception as e:
        logger.error(f"Wikipedia search failed: {e}", extra={"query": query})
        raise HTTPException(status_code=500, detail=f"Wikipedia search failed: {str(e)}")


@router.get("/web", response_model=SearchResponseModel)
async def web_search_endpoint(
    query: str = Query(..., min_length=1, max_length=500),
    k: int = Query(default=5, ge=1, le=10)
):
    """Web search endpoint."""
    try:
        start_time = time.time()
        
        logger.info(f"Web search request: {query}", extra={
            "query": query,
            "k": k
        })
        
        # Perform web search
        results = await free_web_search(query, k)
        
        # Convert to response format
        result_responses = []
        providers_used = []
        for result in results:
            result_responses.append(SearchResultResponse(
                title=result.title,
                url=result.url,
                snippet=result.snippet,
                domain=result.domain,
                provider=result.provider.value,
                relevance_score=result.relevance_score,
                timestamp=result.timestamp.isoformat(),
                metadata=result.metadata
            ))
            providers_used.append(result.provider.value)
        
        processing_time = (time.time() - start_time) * 1000
        
        return SearchResponseModel(
            query=query,
            results=result_responses,
            total_results=len(results),
            cache_hit=False,  # Web search doesn't use cache
            providers_used=list(set(providers_used)),
            processing_time_ms=processing_time,
            trace_id=str(time.time())
        )
        
    except Exception as e:
        logger.error(f"Web search failed: {e}", extra={"query": query})
        raise HTTPException(status_code=500, detail=f"Web search failed: {str(e)}")


@router.get("/combined", response_model=SearchResponseModel)
async def combined_search_endpoint(
    query: str = Query(..., min_length=1, max_length=500),
    k: int = Query(default=5, ge=1, le=20)
):
    """Combined search endpoint with caching."""
    try:
        start_time = time.time()
        
        logger.info(f"Combined search request: {query}", extra={
            "query": query,
            "k": k
        })
        
        # Perform combined search
        response, headers = await search_with_cache_headers(query, k)
        
        # Convert to response format
        result_responses = []
        for result in response.results:
            result_responses.append(SearchResultResponse(
                title=result.title,
                url=result.url,
                snippet=result.snippet,
                domain=result.domain,
                provider=result.provider.value,
                relevance_score=result.relevance_score,
                timestamp=result.timestamp.isoformat(),
                metadata=result.metadata
            ))
        
        # Return with cache headers
        return JSONResponse(
            content=SearchResponseModel(
                query=response.query,
                results=result_responses,
                total_results=response.total_results,
                cache_hit=response.cache_hit,
                providers_used=[p.value for p in response.providers_used],
                processing_time_ms=response.processing_time_ms,
                trace_id=response.trace_id,
                error_message=response.error_message
            ).model_dump(),
            headers=headers
        )
        
    except Exception as e:
        logger.error(f"Combined search failed: {e}", extra={"query": query})
        raise HTTPException(status_code=500, detail=f"Combined search failed: {str(e)}")


@router.delete("/cache")
async def clear_cache():
    """Clear all cached search results."""
    try:
        retrieval_system = get_zero_budget_retrieval()
        if retrieval_system.redis_client:
            # Clear all retrieval cache keys
            keys = await retrieval_system.redis_client.keys("retrieval:*")
            if keys:
                await retrieval_system.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} cache entries")
                return {"message": f"Cleared {len(keys)} cache entries"}
            else:
                return {"message": "No cache entries to clear"}
        else:
            return {"message": "Cache not available"}
            
    except Exception as e:
        logger.error(f"Cache clear failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cache clear failed: {str(e)}")


@router.get("/cache/stats")
async def cache_stats():
    """Get cache statistics."""
    try:
        retrieval_system = get_zero_budget_retrieval()
        if retrieval_system.redis_client:
            # Get cache statistics
            keys = await retrieval_system.redis_client.keys("retrieval:*")
            total_keys = len(keys)
            
            # Get memory usage
            info = await retrieval_system.redis_client.info("memory")
            memory_usage = info.get("used_memory_human", "unknown")
            
            return {
                "cache_available": True,
                "total_keys": total_keys,
                "memory_usage": memory_usage,
                "cache_prefix": "retrieval:"
            }
        else:
            return {
                "cache_available": False,
                "total_keys": 0,
                "memory_usage": "N/A",
                "cache_prefix": "N/A"
            }
            
    except Exception as e:
        logger.error(f"Cache stats failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cache stats failed: {str(e)}")


# Startup and shutdown events
@router.on_event("startup")
async def startup_event():
    """Initialize zero-budget retrieval on startup."""
    logger.info("Initializing zero-budget retrieval system")
    # The global instance is already initialized when imported


@router.on_event("shutdown")
async def shutdown_event():
    """Cleanup zero-budget retrieval on shutdown."""
    logger.info("Shutting down zero-budget retrieval system")
    retrieval_system = get_zero_budget_retrieval()
    await retrieval_system.close()
