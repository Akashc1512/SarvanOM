"""
Graph Microservice API
RESTful API endpoints for the graph service.

This module provides:
- Graph query endpoints
- Entity management endpoints
- Relationship management endpoints
- Health check endpoints
- Error handling
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from .graph_service import GraphService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/graph", tags=["graph"])

# Initialize service
graph_service = GraphService()

# Request/Response Models
class EntityRequest(BaseModel):
    entity_data: Dict[str, Any]

class EntityResponse(BaseModel):
    entity_id: Optional[str]
    entity: Dict[str, Any]
    add_time_ms: int
    status: str

class RelationshipRequest(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str

class RelationshipResponse(BaseModel):
    relationship_id: Optional[str]
    source_id: str
    target_id: str
    relationship_type: str
    status: str

class QueryRequest(BaseModel):
    query: str
    query_type: str = "entity"

class QueryResponse(BaseModel):
    query: str
    query_type: str
    results: List[Dict[str, Any]]
    query_time_ms: int
    query_id: str
    status: str

class ExtractRequest(BaseModel):
    text: str

class ExtractResponse(BaseModel):
    text: str
    entities: List[Dict[str, Any]]
    extraction_id: str
    status: str

class HealthCheckResponse(BaseModel):
    service: str
    status: str
    components: Dict[str, str]
    timestamp: str

@router.post("/entity", response_model=EntityResponse)
async def add_entity(request: EntityRequest):
    """Add an entity to the knowledge graph."""
    try:
        logger.info(f"Processing entity addition request")
        
        result = await graph_service.add_entity(request.entity_data)
        
        return EntityResponse(**result)
        
    except Exception as e:
        logger.error(f"Entity addition failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/relationship", response_model=RelationshipResponse)
async def add_relationship(request: RelationshipRequest):
    """Add a relationship between entities."""
    try:
        logger.info(f"Processing relationship addition request")
        
        result = await graph_service.add_relationship(
            source_id=request.source_id,
            target_id=request.target_id,
            relationship_type=request.relationship_type
        )
        
        return RelationshipResponse(**result)
        
    except Exception as e:
        logger.error(f"Relationship addition failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryResponse)
async def query_graph(request: QueryRequest):
    """Query the knowledge graph."""
    try:
        logger.info(f"Processing graph query: {request.query}")
        
        result = await graph_service.query_graph(
            query=request.query,
            query_type=request.query_type
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Graph query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract", response_model=ExtractResponse)
async def extract_entities(request: ExtractRequest):
    """Extract entities from text."""
    try:
        logger.info(f"Processing entity extraction for text: {request.text[:100]}...")
        
        result = await graph_service.extract_entities(request.text)
        
        return ExtractResponse(**result)
        
    except Exception as e:
        logger.error(f"Entity extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/entity/{entity_id}")
async def get_entity(entity_id: str):
    """Get a specific entity by ID."""
    try:
        result = await graph_service.get_entity(entity_id)
        return result
    except Exception as e:
        logger.error(f"Failed to get entity {entity_id}: {e}")
        raise HTTPException(status_code=404, detail="Entity not found")

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint for the graph service."""
    try:
        health = await graph_service.health_check()
        return HealthCheckResponse(**health)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@router.get("/status")
async def service_status():
    """Get detailed service status."""
    try:
        health = await graph_service.health_check()
        return {
            "service": "graph",
            "version": "2.0.0",
            "status": health.get("status", "unknown"),
            "components": health.get("components", {}),
            "endpoints": {
                "add_entity": "/api/v1/graph/entity",
                "add_relationship": "/api/v1/graph/relationship",
                "query": "/api/v1/graph/query",
                "extract": "/api/v1/graph/extract",
                "health": "/api/v1/graph/health"
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 