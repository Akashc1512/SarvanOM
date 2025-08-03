"""
Vector Microservice API
RESTful API endpoints for the vector service.

This module provides:
- Embedding endpoints
- Vector search endpoints
- Document indexing endpoints
- Health check endpoints
- Error handling
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from .vector_service import VectorService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/vector", tags=["vector"])

# Initialize service
vector_service = VectorService()

# Request/Response Models
class EmbeddingRequest(BaseModel):
    text: str

class EmbeddingResponse(BaseModel):
    embedding: List[float]
    text: str
    embedding_time_ms: int
    embedding_id: str
    status: str

class SearchRequest(BaseModel):
    query: str
    limit: int = 10

class SearchResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    search_time_ms: int
    search_id: str
    status: str

class IndexRequest(BaseModel):
    document: Dict[str, Any]

class IndexResponse(BaseModel):
    index_id: Optional[str]
    document: Dict[str, Any]
    embedding: Dict[str, Any]
    status: str

class HealthCheckResponse(BaseModel):
    service: str
    status: str
    components: Dict[str, str]
    timestamp: str

@router.post("/embed", response_model=EmbeddingResponse)
async def create_embedding(request: EmbeddingRequest):
    """Create an embedding for the given text."""
    try:
        logger.info(f"Processing embedding request for text: {request.text[:100]}...")
        
        result = await vector_service.create_embedding(request.text)
        
        return EmbeddingResponse(**result)
        
    except Exception as e:
        logger.error(f"Embedding creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=SearchResponse)
async def search_similar(request: SearchRequest):
    """Search for similar vectors."""
    try:
        logger.info(f"Processing similarity search for query: {request.query}")
        
        result = await vector_service.search_similar(
            query=request.query,
            limit=request.limit
        )
        
        return SearchResponse(**result)
        
    except Exception as e:
        logger.error(f"Similarity search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/index", response_model=IndexResponse)
async def index_document(request: IndexRequest):
    """Index a document in the vector database."""
    try:
        logger.info(f"Processing document indexing request")
        
        result = await vector_service.index_document(request.document)
        
        return IndexResponse(**result)
        
    except Exception as e:
        logger.error(f"Document indexing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/embedding/{embedding_id}")
async def get_embedding(embedding_id: str):
    """Get a specific embedding by ID."""
    try:
        result = await vector_service.get_embedding(embedding_id)
        return result
    except Exception as e:
        logger.error(f"Failed to get embedding {embedding_id}: {e}")
        raise HTTPException(status_code=404, detail="Embedding not found")

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint for the vector service."""
    try:
        health = await vector_service.health_check()
        return HealthCheckResponse(**health)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@router.get("/status")
async def service_status():
    """Get detailed service status."""
    try:
        health = await vector_service.health_check()
        return {
            "service": "vector",
            "version": "2.0.0",
            "status": health.get("status", "unknown"),
            "components": health.get("components", {}),
            "endpoints": {
                "embed": "/api/v1/vector/embed",
                "search": "/api/v1/vector/search",
                "index": "/api/v1/vector/index",
                "health": "/api/v1/vector/health"
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 