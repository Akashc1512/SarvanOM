"""
Knowledge Graph Agent Route Handler
Handles knowledge graph queries and operations using KnowledgeService.
"""

import logging
from shared.core.unified_logging import get_logger
from typing import Dict, Any, List
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, Depends

from .base import (
    AgentResponseFormatter,
    AgentErrorHandler,
    AgentPerformanceTracker,
    get_user_id,
    create_agent_metadata,
)
from ...models.requests import KnowledgeGraphRequest
from ...models.responses import AgentResponse
from ...middleware import get_current_user
from ...di import get_knowledge_service
from ...services.knowledge_service import KnowledgeService

logger = get_logger(__name__)

router = APIRouter()


@router.post("/knowledge-graph/query")
async def knowledge_graph_query(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> AgentResponse:
    """Query the knowledge graph for entities and relationships using knowledge service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()

    try:
        # Validate request
        AgentErrorHandler.validate_request(request, ["query"])

        kg_request = KnowledgeGraphRequest(
            query=request.get("query", ""),
            query_type=request.get("query_type", "entity_relationship"),
            parameters=request.get("parameters", {}),
            context=request.get("context", {}),
        )

        # Execute knowledge graph query using service
        kg_results = await knowledge_service.query_entities(
            entity_type=kg_request.parameters.get("entity_type"),
            properties=kg_request.parameters.get("properties"),
            limit=kg_request.parameters.get("limit", 10),
        )

        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)

        return AgentResponseFormatter.format_success(
            agent_id="knowledge_graph",
            result=kg_results,
            processing_time=processing_time,
            metadata=create_agent_metadata(
                user_id=user_id,
                query_type=kg_request.query_type,
                query=kg_request.query,
            ),
            user_id=user_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="knowledge_graph",
            error=e,
            operation="Knowledge graph query",
            user_id=get_user_id(current_user),
        )


@router.post("/knowledge-graph/entities")
async def get_entities(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> AgentResponse:
    """Get entities from the knowledge graph using knowledge service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()

    try:
        # Validate request
        AgentErrorHandler.validate_request(request, ["entity_type"])

        entity_type = request.get("entity_type", "")
        properties = request.get("properties", {})
        limit = request.get("limit", 10)

        # Get entities using service
        entities = await knowledge_service.query_entities(
            entity_type=entity_type, properties=properties, limit=limit
        )

        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)

        return AgentResponseFormatter.format_success(
            agent_id="knowledge_graph_entities",
            result=entities,
            processing_time=processing_time,
            metadata=create_agent_metadata(
                user_id=user_id, entity_type=entity_type, limit=limit
            ),
            user_id=user_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="knowledge_graph_entities",
            error=e,
            operation="Entity retrieval",
            user_id=get_user_id(current_user),
        )


@router.post("/knowledge-graph/relationships")
async def get_relationships(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> AgentResponse:
    """Get relationships from the knowledge graph using knowledge service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()

    try:
        # Validate request
        AgentErrorHandler.validate_request(request, ["source_entity", "target_entity"])

        source_entity = request.get("source_entity", "")
        target_entity = request.get("target_entity", "")
        relationship_type = request.get("relationship_type", "")
        limit = request.get("limit", 10)

        # Get relationships using service
        relationships = await knowledge_service.query_relationships(
            source_entity=source_entity,
            target_entity=target_entity,
            relationship_type=relationship_type,
            limit=limit,
        )

        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)

        return AgentResponseFormatter.format_success(
            agent_id="knowledge_graph_relationships",
            result=relationships,
            processing_time=processing_time,
            metadata=create_agent_metadata(
                user_id=user_id,
                source_entity=source_entity,
                target_entity=target_entity,
                relationship_type=relationship_type,
            ),
            user_id=user_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="knowledge_graph_relationships",
            error=e,
            operation="Relationship retrieval",
            user_id=get_user_id(current_user),
        )


@router.post("/knowledge-graph/paths")
async def find_paths(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> AgentResponse:
    """Find paths between entities using knowledge service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()

    try:
        # Validate request
        AgentErrorHandler.validate_request(request, ["source_entity", "target_entity"])

        source_entity = request.get("source_entity", "")
        target_entity = request.get("target_entity", "")
        max_paths = request.get("max_paths", 5)
        max_length = request.get("max_length", 5)

        # Find paths using service
        paths = await knowledge_service.find_paths(
            source_entity=source_entity,
            target_entity=target_entity,
            max_paths=max_paths,
            max_length=max_length,
        )

        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)

        return AgentResponseFormatter.format_success(
            agent_id="knowledge_graph_paths",
            result=paths,
            processing_time=processing_time,
            metadata=create_agent_metadata(
                user_id=user_id,
                source_entity=source_entity,
                target_entity=target_entity,
                max_paths=max_paths,
            ),
            user_id=user_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="knowledge_graph_paths",
            error=e,
            operation="Path finding",
            user_id=get_user_id(current_user),
        )


@router.post("/knowledge-graph/search")
async def search_entities(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> AgentResponse:
    """Search for entities using knowledge service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()

    try:
        # Validate request
        AgentErrorHandler.validate_request(request, ["search_term"])

        search_term = request.get("search_term", "")
        entity_types = request.get("entity_types", [])
        limit = request.get("limit", 10)

        # Search entities using service
        search_results = await knowledge_service.search_entities(
            search_term=search_term, entity_types=entity_types, limit=limit
        )

        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)

        return AgentResponseFormatter.format_success(
            agent_id="knowledge_graph_search",
            result=search_results,
            processing_time=processing_time,
            metadata=create_agent_metadata(
                user_id=user_id, search_term=search_term, entity_types=entity_types
            ),
            user_id=user_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="knowledge_graph_search",
            error=e,
            operation="Entity search",
            user_id=get_user_id(current_user),
        )


@router.get("/knowledge-graph/health")
async def knowledge_health(
    current_user=Depends(get_current_user),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> AgentResponse:
    """Get knowledge service health status."""
    try:
        health_status = await knowledge_service.health_check()

        return AgentResponseFormatter.format_success(
            agent_id="knowledge_health",
            result=health_status,
            processing_time=0.0,
            metadata=create_agent_metadata(
                user_id=get_user_id(current_user), health_check=True
            ),
            user_id=get_user_id(current_user),
        )

    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="knowledge_health",
            error=e,
            operation="Health check",
            user_id=get_user_id(current_user),
        )


@router.get("/knowledge-graph/status")
async def knowledge_status(
    current_user=Depends(get_current_user),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> AgentResponse:
    """Get knowledge service detailed status."""
    try:
        status_info = await knowledge_service.get_status()

        return AgentResponseFormatter.format_success(
            agent_id="knowledge_status",
            result=status_info,
            processing_time=0.0,
            metadata=create_agent_metadata(
                user_id=get_user_id(current_user), status_check=True
            ),
            user_id=get_user_id(current_user),
        )

    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="knowledge_status",
            error=e,
            operation="Status check",
            user_id=get_user_id(current_user),
        )
