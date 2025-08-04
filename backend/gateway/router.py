"""
API Gateway Router

This module provides the main routing logic for the API gateway,
handling requests to all backend services.
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel

# Import services
from ..retrieval import SearchService
from ..fact_check import FactCheckService
from ..synthesis import SynthesisService
from ..auth import AuthService
from ..crawler import CrawlerService
from ..vector import VectorService
from ..graph import GraphService

logger = logging.getLogger(__name__)


class QueryRequest(BaseModel):
    """Request model for search queries."""
    query: str
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    max_results: Optional[int] = 10


class FactCheckRequest(BaseModel):
    """Request model for fact checking."""
    claim: str
    sources: List[str] = []
    user_id: Optional[str] = None


class SynthesisRequest(BaseModel):
    """Request model for content synthesis."""
    content: List[Dict[str, Any]]
    query: str
    user_id: Optional[str] = None
    style: Optional[str] = "academic"


class CrawlRequest(BaseModel):
    """Request model for web crawling."""
    url: str
    depth: Optional[int] = 1
    max_pages: Optional[int] = 10


class VectorSearchRequest(BaseModel):
    """Request model for vector search."""
    query: str
    top_k: Optional[int] = 10
    filters: Optional[Dict[str, Any]] = None


class GraphQueryRequest(BaseModel):
    """Request model for graph queries."""
    query: str
    params: Optional[Dict[str, Any]] = None


class AuthRequest(BaseModel):
    """Request model for authentication."""
    username: str
    password: str


class UserCreateRequest(BaseModel):
    """Request model for user creation."""
    username: str
    email: str
    password: str
    role: Optional[str] = "user"


# Initialize services
search_service = SearchService()
fact_check_service = FactCheckService()
synthesis_service = SynthesisService()
auth_service = AuthService()
crawler_service = CrawlerService()
vector_service = VectorService()
graph_service = GraphService()


# Create router
router = APIRouter(prefix="/api/v1")


# Authentication middleware
async def get_current_user(request: Request):
    """Get current user from request."""
    # This is a simplified implementation
    # In a real implementation, you'd verify JWT tokens
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Extract token and verify
    token = auth_header.replace("Bearer ", "")
    user = await auth_service.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return user


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "services": {
            "search": search_service.get_status(),
            "fact_check": fact_check_service.get_status(),
            "synthesis": synthesis_service.get_status(),
            "auth": auth_service.get_status(),
            "crawler": crawler_service.get_status(),
            "vector": vector_service.get_status(),
            "graph": graph_service.get_status()
        }
    }


# Search endpoints
@router.post("/search")
async def search(request: QueryRequest, user: Dict = Depends(get_current_user)):
    """Search for information using the retrieval service."""
    try:
        results = await search_service.search(
            query=request.query,
            user_id=request.user_id or user.get("id"),
            context=request.context,
            max_results=request.max_results
        )
        return {
            "status": "success",
            "results": results,
            "query": request.query
        }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/search/{query}")
async def search_get(query: str, user: Dict = Depends(get_current_user)):
    """GET endpoint for search."""
    try:
        results = await search_service.search(
            query=query,
            user_id=user.get("id"),
            max_results=10
        )
        return {
            "status": "success",
            "results": results,
            "query": query
        }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# Fact check endpoints
@router.post("/fact-check")
async def fact_check(request: FactCheckRequest, user: Dict = Depends(get_current_user)):
    """Fact check a claim using the fact check service."""
    try:
        result = await fact_check_service.fact_check(
            claim=request.claim,
            sources=request.sources,
            user_id=request.user_id or user.get("id")
        )
        return {
            "status": "success",
            "result": result,
            "claim": request.claim
        }
    except Exception as e:
        logger.error(f"Fact check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Fact check failed: {str(e)}")


@router.post("/fact-check/batch")
async def fact_check_batch(claims: List[str], user: Dict = Depends(get_current_user)):
    """Fact check multiple claims."""
    try:
        results = []
        for claim in claims:
            result = await fact_check_service.fact_check(
                claim=claim,
                user_id=user.get("id")
            )
            results.append(result)
        
        return {
            "status": "success",
            "results": results,
            "count": len(claims)
        }
    except Exception as e:
        logger.error(f"Batch fact check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch fact check failed: {str(e)}")


# Synthesis endpoints
@router.post("/synthesize")
async def synthesize(request: SynthesisRequest, user: Dict = Depends(get_current_user)):
    """Synthesize content using the synthesis service."""
    try:
        result = await synthesis_service.synthesize(
            content=request.content,
            query=request.query,
            user_id=request.user_id or user.get("id"),
            style=request.style
        )
        return {
            "status": "success",
            "result": result,
            "query": request.query
        }
    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")


@router.post("/synthesize/citations")
async def generate_citations(content: List[Dict[str, Any]], user: Dict = Depends(get_current_user)):
    """Generate citations for content."""
    try:
        citations = await synthesis_service.generate_citations(
            content=content,
            user_id=user.get("id")
        )
        return {
            "status": "success",
            "citations": citations
        }
    except Exception as e:
        logger.error(f"Citation generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Citation generation failed: {str(e)}")


# Crawler endpoints
@router.post("/crawl")
async def crawl(request: CrawlRequest, user: Dict = Depends(get_current_user)):
    """Crawl a website using the crawler service."""
    try:
        result = await crawler_service.crawl(
            url=request.url,
            depth=request.depth,
            max_pages=request.max_pages,
            user_id=user.get("id")
        )
        return {
            "status": "success",
            "result": result,
            "url": request.url
        }
    except Exception as e:
        logger.error(f"Crawling failed: {e}")
        raise HTTPException(status_code=500, detail=f"Crawling failed: {str(e)}")


@router.get("/crawl/status/{job_id}")
async def crawl_status(job_id: str, user: Dict = Depends(get_current_user)):
    """Get crawling job status."""
    try:
        status = await crawler_service.get_status(job_id)
        return {
            "status": "success",
            "job_status": status
        }
    except Exception as e:
        logger.error(f"Failed to get crawl status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get crawl status: {str(e)}")


# Vector search endpoints
@router.post("/vector/search")
async def vector_search(request: VectorSearchRequest, user: Dict = Depends(get_current_user)):
    """Search using vector embeddings."""
    try:
        results = await vector_service.search_similar(
            query=request.query,
            top_k=request.top_k
        )
        return {
            "status": "success",
            "results": [result.__dict__ for result in results],
            "query": request.query
        }
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Vector search failed: {str(e)}")


@router.post("/vector/upsert")
async def vector_upsert(documents: List[Dict[str, Any]], user: Dict = Depends(get_current_user)):
    """Upsert documents to vector database."""
    try:
        success = await vector_service.upsert_documents(documents)
        return {
            "status": "success" if success else "failed",
            "documents_count": len(documents)
        }
    except Exception as e:
        logger.error(f"Vector upsert failed: {e}")
        raise HTTPException(status_code=500, detail=f"Vector upsert failed: {str(e)}")


# Graph endpoints
@router.post("/graph/query")
async def graph_query(request: GraphQueryRequest, user: Dict = Depends(get_current_user)):
    """Query the knowledge graph."""
    try:
        result = await graph_service.query_graph(
            query=request.query,
            params=request.params
        )
        return {
            "status": "success",
            "result": {
                "nodes": [node.__dict__ for node in result.nodes],
                "edges": [edge.__dict__ for edge in result.edges],
                "metadata": result.metadata
            }
        }
    except Exception as e:
        logger.error(f"Graph query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Graph query failed: {str(e)}")


@router.post("/graph/entities")
async def find_entities(text: str, user: Dict = Depends(get_current_user)):
    """Find entities in text."""
    try:
        entities = await graph_service.find_entities(text)
        return {
            "status": "success",
            "entities": [entity.__dict__ for entity in entities],
            "text": text
        }
    except Exception as e:
        logger.error(f"Entity finding failed: {e}")
        raise HTTPException(status_code=500, detail=f"Entity finding failed: {str(e)}")


@router.post("/graph/triple")
async def add_triple(subject: str, predicate: str, object_value: str, user: Dict = Depends(get_current_user)):
    """Add a knowledge triple to the graph."""
    try:
        success = await graph_service.add_knowledge_triple(subject, predicate, object_value)
        return {
            "status": "success" if success else "failed",
            "triple": {"subject": subject, "predicate": predicate, "object": object_value}
        }
    except Exception as e:
        logger.error(f"Failed to add triple: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add triple: {str(e)}")


# Authentication endpoints
@router.post("/auth/login")
async def login(request: AuthRequest):
    """User login."""
    try:
        token = await auth_service.login(
            username=request.username,
            password=request.password
        )
        return {
            "status": "success",
            "token": token
        }
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=401, detail=f"Login failed: {str(e)}")


@router.post("/auth/register")
async def register(request: UserCreateRequest):
    """User registration."""
    try:
        user = await auth_service.create_user(
            username=request.username,
            email=request.email,
            password=request.password,
            role=request.role
        )
        return {
            "status": "success",
            "user": user
        }
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")


@router.get("/auth/profile")
async def get_profile(user: Dict = Depends(get_current_user)):
    """Get user profile."""
    try:
        profile = await auth_service.get_user_profile(user.get("id"))
        return {
            "status": "success",
            "profile": profile
        }
    except Exception as e:
        logger.error(f"Failed to get profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")


@router.post("/auth/logout")
async def logout(user: Dict = Depends(get_current_user)):
    """User logout."""
    try:
        await auth_service.logout(user.get("id"))
        return {
            "status": "success",
            "message": "Logged out successfully"
        }
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")


# Service status endpoints
@router.get("/services/status")
async def get_services_status():
    """Get status of all services."""
    return {
        "status": "success",
        "services": {
            "search": search_service.get_status(),
            "fact_check": fact_check_service.get_status(),
            "synthesis": synthesis_service.get_status(),
            "auth": auth_service.get_status(),
            "crawler": crawler_service.get_status(),
            "vector": vector_service.get_status(),
            "graph": graph_service.get_status()
        }
    } 