"""
Gateway Router

This module provides routing logic for the backend gateway service.

# DEAD CODE - Candidate for deletion: This backend directory is not used by the main application
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from datetime import datetime

# Import services
from backend.retrieval import SearchService
from backend.fact_check import FactCheckService
from backend.synthesis import SynthesisService
from backend.auth import AuthService
from backend.crawler import CrawlerService
from backend.vector import VectorService
from backend.graph import GraphService

logger = logging.getLogger(__name__)

# Initialize service instances
search_service = SearchService()
fact_check_service = FactCheckService()
synthesis_service = SynthesisService()
auth_service = AuthService()
crawler_service = CrawlerService()
vector_service = VectorService()
graph_service = GraphService()

# Create router
router = APIRouter()

# Pydantic models for requests
class QueryRequest(BaseModel):
    query: str = Field(..., description="Search query")
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
    limit: int = Field(10, description="Number of results to return")

class FactCheckRequest(BaseModel):
    claim: str = Field(..., description="Claim to fact-check")
    sources: Optional[List[str]] = Field(None, description="Sources to check against")

class SynthesisRequest(BaseModel):
    content: str = Field(..., description="Content to synthesize")
    style: Optional[str] = Field("academic", description="Synthesis style")
    include_citations: bool = Field(True, description="Include citations")

class CrawlRequest(BaseModel):
    url: str = Field(..., description="URL to crawl")
    depth: int = Field(1, description="Crawl depth")
    max_pages: int = Field(10, description="Maximum pages to crawl")

class VectorSearchRequest(BaseModel):
    query: str = Field(..., description="Vector search query")
    top_k: int = Field(5, description="Number of similar vectors to return")

class GraphQueryRequest(BaseModel):
    query: str = Field(..., description="Graph query")
    limit: int = Field(10, description="Query result limit")

class AuthRequest(BaseModel):
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

class UserCreateRequest(BaseModel):
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email")
    password: str = Field(..., description="Password")

# Authentication dependency
async def get_current_user(token: str = Depends()):
    """Get current user from token."""
    try:
        user = await auth_service.verify_token(token)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

# Search endpoints
@router.post("/search")
async def search(request: QueryRequest):
    """Search for information."""
    try:
        results = await search_service.search(
            query=request.query,
            filters=request.filters,
            limit=request.limit
        )
        return {"results": results, "query": request.query}
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/hybrid")
async def hybrid_search(request: QueryRequest):
    """Perform hybrid search combining multiple search methods."""
    try:
        results = await search_service.hybrid_search(
            query=request.query,
            filters=request.filters,
            limit=request.limit
        )
        return {"results": results, "query": request.query}
    except Exception as e:
        logger.error(f"Hybrid search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Fact-checking endpoints
@router.post("/fact-check")
async def fact_check(request: FactCheckRequest):
    """Fact-check a claim."""
    try:
        result = await fact_check_service.fact_check(
            claim=request.claim,
            sources=request.sources
        )
        return {"result": result, "claim": request.claim}
    except Exception as e:
        logger.error(f"Fact-check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fact-check/batch")
async def batch_fact_check(claims: List[str]):
    """Fact-check multiple claims."""
    try:
        results = await fact_check_service.batch_fact_check(claims)
        return {"results": results}
    except Exception as e:
        logger.error(f"Batch fact-check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Synthesis endpoints
@router.post("/synthesize")
async def synthesize(request: SynthesisRequest):
    """Synthesize content."""
    try:
        result = await synthesis_service.synthesize(
            content=request.content,
            style=request.style,
            include_citations=request.include_citations
        )
        return {"result": result, "content": request.content}
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/synthesize/citations")
async def generate_citations(content: str):
    """Generate citations for content."""
    try:
        citations = await synthesis_service.generate_citations(content)
        return {"citations": citations}
    except Exception as e:
        logger.error(f"Citation generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Crawler endpoints
@router.post("/crawl")
async def crawl(request: CrawlRequest):
    """Crawl a website."""
    try:
        result = await crawler_service.crawl(
            url=request.url,
            depth=request.depth,
            max_pages=request.max_pages
        )
        return {"result": result, "url": request.url}
    except Exception as e:
        logger.error(f"Crawl error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/crawl/status/{job_id}")
async def get_crawl_status(job_id: str):
    """Get crawl job status."""
    try:
        status = await crawler_service.get_status()
        return {"job_id": job_id, "status": status}
    except Exception as e:
        logger.error(f"Get crawl status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Vector search endpoints
@router.post("/vector/search")
async def vector_search(request: VectorSearchRequest):
    """Search for similar vectors."""
    try:
        results = await vector_service.search_similar(
            query=request.query,
            top_k=request.top_k
        )
        return {"results": results, "query": request.query}
    except Exception as e:
        logger.error(f"Vector search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vector/embed")
async def get_embedding(text: str):
    """Get embedding for text."""
    try:
        embedding = await vector_service.get_embedding(text)
        return {"embedding": embedding, "text": text}
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Graph endpoints
@router.post("/graph/query")
async def graph_query(request: GraphQueryRequest):
    """Query the knowledge graph."""
    try:
        results = await graph_service.query_graph(
            query=request.query,
            limit=request.limit
        )
        return {"results": results, "query": request.query}
    except Exception as e:
        logger.error(f"Graph query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/graph/entities")
async def find_entities(entity_type: Optional[str] = None, properties: Optional[Dict[str, Any]] = None):
    """Find entities in the knowledge graph."""
    try:
        results = await graph_service.find_entities(
            entity_type=entity_type,
            properties=properties
        )
        return {"results": results}
    except Exception as e:
        logger.error(f"Find entities error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Authentication endpoints
@router.post("/auth/login")
async def login(request: AuthRequest):
    """User login."""
    try:
        result = await auth_service.login(
            username=request.username,
            password=request.password
        )
        return {"result": result}
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/auth/register")
async def register(request: UserCreateRequest):
    """User registration."""
    try:
        result = await auth_service.register(
            username=request.username,
            email=request.email,
            password=request.password
        )
        return {"result": result}
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/verify")
async def verify_token(token: str):
    """Verify authentication token."""
    try:
        user = await auth_service.verify_token(token)
        return {"user": user}
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

# Health and status endpoints
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/services/status")
async def get_services_status():
    """Get status of all services."""
    try:
        statuses = {}
        
        # Get status from each service
        statuses["search"] = await search_service.get_status()
        statuses["fact_check"] = await fact_check_service.get_status()
        statuses["synthesis"] = await synthesis_service.get_status()
        statuses["auth"] = await auth_service.get_status()
        statuses["crawler"] = await crawler_service.get_status()
        statuses["vector"] = await vector_service.get_status()
        statuses["graph"] = await graph_service.get_status()
        
        return {"services": statuses}
    except Exception as e:
        logger.error(f"Get services status error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 