"""
API Router for Backend Services
Routes requests to appropriate backend services.

This module provides:
- Service routing and orchestration
- Request/response handling
- Error handling and logging
- Service discovery
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

# Import backend services
from ..retrieval import SearchService
from ..fact_check import FactCheckService
from ..synthesis import SynthesisService
from ..auth import AuthService
from ..crawler import WebCrawler
from ..vector import VectorService
from ..graph import GraphService

logger = logging.getLogger(__name__)

# Initialize services
search_service = SearchService()
fact_check_service = FactCheckService()
synthesis_service = SynthesisService()
auth_service = AuthService()
crawler_service = WebCrawler()
vector_service = VectorService()
graph_service = GraphService()

# Create router
router = APIRouter(prefix="/api/v1")

# Request/Response Models
class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 10

class SearchResponse(BaseModel):
    results: list
    total: int
    query: str

class FactCheckRequest(BaseModel):
    content: str
    sources: Optional[list] = None

class FactCheckResponse(BaseModel):
    verdict: str
    confidence: float
    sources: list
    reasoning: str

class SynthesisRequest(BaseModel):
    query: str
    search_results: list
    fact_check_results: Optional[Dict[str, Any]] = None

class SynthesisResponse(BaseModel):
    content: str
    citations: list
    confidence: float

class AuthRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    token: str
    user_id: str
    role: str

class CrawlerRequest(BaseModel):
    url: str
    depth: int = 1

class CrawlerResponse(BaseModel):
    content: str
    links: list
    metadata: Dict[str, Any]

class VectorRequest(BaseModel):
    text: str
    operation: str  # "search", "store", "update"

class VectorResponse(BaseModel):
    results: list
    operation: str

class GraphRequest(BaseModel):
    query: str
    operation: str  # "search", "add", "update"

class GraphResponse(BaseModel):
    results: list
    operation: str

# Search endpoints
@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Search for documents using the retrieval service."""
    try:
        results = await search_service.search(
            query=request.query,
            filters=request.filters,
            limit=request.limit
        )
        return SearchResponse(
            results=results.get("documents", []),
            total=results.get("total", 0),
            query=request.query
        )
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/{query_id}")
async def get_search_result(query_id: str):
    """Get a specific search result by ID."""
    try:
        result = await search_service.get_result(query_id)
        return result
    except Exception as e:
        logger.error(f"Get search result error: {e}")
        raise HTTPException(status_code=404, detail="Search result not found")

# Fact check endpoints
@router.post("/fact-check", response_model=FactCheckResponse)
async def fact_check_content(request: FactCheckRequest):
    """Fact check content using the fact check service."""
    try:
        result = await fact_check_service.verify(
            content=request.content,
            sources=request.sources
        )
        return FactCheckResponse(
            verdict=result.get("verdict", "unclear"),
            confidence=result.get("confidence", 0.0),
            sources=result.get("sources", []),
            reasoning=result.get("reasoning", "")
        )
    except Exception as e:
        logger.error(f"Fact check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fact-check/{check_id}")
async def get_fact_check_result(check_id: str):
    """Get a specific fact check result by ID."""
    try:
        result = await fact_check_service.get_result(check_id)
        return result
    except Exception as e:
        logger.error(f"Get fact check result error: {e}")
        raise HTTPException(status_code=404, detail="Fact check result not found")

# Synthesis endpoints
@router.post("/synthesis", response_model=SynthesisResponse)
async def synthesize_content(request: SynthesisRequest):
    """Synthesize content using the synthesis service."""
    try:
        result = await synthesis_service.synthesize(
            query=request.query,
            search_results=request.search_results,
            fact_check_results=request.fact_check_results
        )
        return SynthesisResponse(
            content=result.get("content", ""),
            citations=result.get("citations", []),
            confidence=result.get("confidence", 0.0)
        )
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/synthesis/{synthesis_id}")
async def get_synthesis_result(synthesis_id: str):
    """Get a specific synthesis result by ID."""
    try:
        result = await synthesis_service.get_result(synthesis_id)
        return result
    except Exception as e:
        logger.error(f"Get synthesis result error: {e}")
        raise HTTPException(status_code=404, detail="Synthesis result not found")

# Auth endpoints
@router.post("/auth/login", response_model=AuthResponse)
async def login(request: AuthRequest):
    """Authenticate user using the auth service."""
    try:
        result = await auth_service.authenticate(
            username=request.username,
            password=request.password
        )
        return AuthResponse(
            token=result.get("token", ""),
            user_id=result.get("user_id", ""),
            role=result.get("role", "user")
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.post("/auth/register")
async def register(request: AuthRequest):
    """Register new user using the auth service."""
    try:
        result = await auth_service.register(
            username=request.username,
            password=request.password
        )
        return result
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Crawler endpoints
@router.post("/crawler/crawl", response_model=CrawlerResponse)
async def crawl_website(request: CrawlerRequest):
    """Crawl website using the crawler service."""
    try:
        result = await crawler_service.crawl(
            url=request.url,
            depth=request.depth
        )
        return CrawlerResponse(
            content=result.get("content", ""),
            links=result.get("links", []),
            metadata=result.get("metadata", {})
        )
    except Exception as e:
        logger.error(f"Crawler error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Vector endpoints
@router.post("/vector", response_model=VectorResponse)
async def vector_operation(request: VectorRequest):
    """Perform vector operations using the vector service."""
    try:
        if request.operation == "search":
            result = await vector_service.search(request.text)
        elif request.operation == "store":
            result = await vector_service.store(request.text)
        elif request.operation == "update":
            result = await vector_service.update(request.text)
        else:
            raise HTTPException(status_code=400, detail="Invalid operation")
        
        return VectorResponse(
            results=result.get("results", []),
            operation=request.operation
        )
    except Exception as e:
        logger.error(f"Vector operation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Graph endpoints
@router.post("/graph", response_model=GraphResponse)
async def graph_operation(request: GraphRequest):
    """Perform graph operations using the graph service."""
    try:
        if request.operation == "search":
            result = await graph_service.search(request.query)
        elif request.operation == "add":
            result = await graph_service.add(request.query)
        elif request.operation == "update":
            result = await graph_service.update(request.query)
        else:
            raise HTTPException(status_code=400, detail="Invalid operation")
        
        return GraphResponse(
            results=result.get("results", []),
            operation=request.operation
        )
    except Exception as e:
        logger.error(f"Graph operation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for all services."""
    try:
        health_status = {
            "status": "healthy",
            "services": {
                "search": await search_service.health_check(),
                "fact_check": await fact_check_service.health_check(),
                "synthesis": await synthesis_service.health_check(),
                "auth": await auth_service.health_check(),
                "crawler": await crawler_service.health_check(),
                "vector": await vector_service.health_check(),
                "graph": await graph_service.health_check()
            }
        }
        return health_status
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy") 