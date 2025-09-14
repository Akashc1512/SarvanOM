#!/usr/bin/env python3
"""
Knowledge Graph Service - Environment-Driven ArangoDB Integration

This service provides knowledge graph operations using the environment-driven
ArangoDB service with proper error handling and performance optimization.

Key Features:
- Uses environment-driven ArangoDB configuration
- Timeboxed queries (≤1.5s as per requirements)
- Proper error handling and logging
- Context fusion for synthesis
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from shared.core.services.arangodb_service import arangodb_service, ArangoDBService
from shared.core.unified_logging import get_logger

logger = get_logger(__name__)

@dataclass
class KnowledgeEntity:
    """Represents a knowledge graph entity."""
    
    id: str
    name: str
    type: str
    properties: Dict[str, Any]
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "properties": self.properties,
            "confidence": self.confidence
        }

@dataclass 
class KnowledgeRelationship:
    """Represents a knowledge graph relationship."""
    
    from_entity: str
    to_entity: str
    relationship_type: str
    properties: Dict[str, Any]
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "from_entity": self.from_entity,
            "to_entity": self.to_entity,
            "relationship_type": self.relationship_type,
            "properties": self.properties,
            "confidence": self.confidence
        }

@dataclass
class KnowledgeGraphResult:
    """Result from knowledge graph query."""
    
    entities: List[KnowledgeEntity]
    relationships: List[KnowledgeRelationship]
    query_time_ms: float
    total_results: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "entities": [e.to_dict() for e in self.entities],
            "relationships": [r.to_dict() for r in self.relationships],
            "query_time_ms": self.query_time_ms,
            "total_results": self.total_results
        }


class KnowledgeGraphService:
    """Production-ready knowledge graph service using ArangoDB."""
    
    def __init__(self):
        """Initialize knowledge graph service."""
        self.arangodb_service: Optional[ArangoDBService] = None
        self.default_timeout = 1.5  # 1.5s max as per requirements
        logger.info("KnowledgeGraphService initialized")
    
    async def _get_service(self) -> ArangoDBService:
        """Get or initialize ArangoDB service."""
        if self.arangodb_service is None:
            self.arangodb_service = arangodb_service
        return self.arangodb_service
    
    async def find_entities(self, query: str, entity_types: Optional[List[str]] = None,
                           limit: int = 20, timeout: Optional[float] = None) -> KnowledgeGraphResult:
        """
        Find entities matching query with timeboxed execution.
        
        Args:
            query: Search query for entities
            entity_types: Optional filter by entity types
            limit: Maximum number of results
            timeout: Query timeout (default 1.5s)
            
        Returns:
            KnowledgeGraphResult with found entities
        """
        query_timeout = timeout or self.default_timeout
        query_start = time.time()
        
        try:
            service = await self._get_service()
            
            # Build AQL query for entity search
            aql_query = """
            FOR e IN entities
                FILTER CONTAINS(LOWER(e.name), LOWER(@query))
            """
            
            bind_vars = {"query": query, "limit": limit}
            
            # Add entity type filter if specified
            if entity_types:
                aql_query += " FILTER e.type IN @entity_types"
                bind_vars["entity_types"] = entity_types
            
            aql_query += " LIMIT @limit RETURN e"
            
            # Execute with timeout
            results = await service.execute_aql(aql_query, bind_vars, timeout=query_timeout)
            
            # Convert results to entities
            entities = []
            for result in results:
                entity = KnowledgeEntity(
                    id=result.get("_key", result.get("id", "")),
                    name=result.get("name", ""),
                    type=result.get("type", "unknown"),
                    properties={k: v for k, v in result.items() 
                              if k not in ["_key", "_id", "_rev", "id", "name", "type"]}
                )
                entities.append(entity)
            
            query_time_ms = (time.time() - query_start) * 1000
            
            logger.debug(
                "Entity search completed",
                query=query,
                entity_count=len(entities),
                query_time_ms=round(query_time_ms, 2)
            )
            
            return KnowledgeGraphResult(
                entities=entities,
                relationships=[],
                query_time_ms=query_time_ms,
                total_results=len(entities)
            )
            
        except asyncio.TimeoutError:
            logger.warning("Entity search timed out", query=query, timeout=query_timeout)
            return KnowledgeGraphResult(entities=[], relationships=[], 
                                      query_time_ms=query_timeout * 1000, total_results=0)
        except Exception as e:
            logger.error("Entity search failed", query=query, error=str(e))
            return KnowledgeGraphResult(entities=[], relationships=[], 
                                      query_time_ms=(time.time() - query_start) * 1000, total_results=0)
    
    async def find_relationships(self, entity_id: str, relationship_types: Optional[List[str]] = None,
                                depth: int = 2, limit: int = 10, 
                                timeout: Optional[float] = None) -> KnowledgeGraphResult:
        """
        Find relationships for an entity with depth limit.
        
        Args:
            entity_id: ID of the entity
            relationship_types: Optional filter by relationship types
            depth: Maximum traversal depth
            limit: Maximum number of results
            timeout: Query timeout (default 1.5s)
            
        Returns:
            KnowledgeGraphResult with relationships and connected entities
        """
        query_timeout = timeout or self.default_timeout
        query_start = time.time()
        
        try:
            service = await self._get_service()
            
            # Build AQL query for relationship traversal
            aql_query = f"""
            FOR v, e, p IN 1..{depth} ANY 'entities/{entity_id}' relationships
            """
            
            bind_vars = {"limit": limit}
            
            # Add relationship type filter if specified
            if relationship_types:
                aql_query += " FILTER e.type IN @relationship_types"
                bind_vars["relationship_types"] = relationship_types
            
            aql_query += " LIMIT @limit RETURN {vertex: v, edge: e, path: p}"
            
            # Execute with timeout
            results = await service.execute_aql(aql_query, bind_vars, timeout=query_timeout)
            
            # Process results
            entities = []
            relationships = []
            seen_entities = set()
            
            for result in results:
                vertex = result.get("vertex", {})
                edge = result.get("edge", {})
                
                # Add entity if not seen
                entity_id = vertex.get("_key", vertex.get("id", ""))
                if entity_id and entity_id not in seen_entities:
                    entity = KnowledgeEntity(
                        id=entity_id,
                        name=vertex.get("name", ""),
                        type=vertex.get("type", "unknown"),
                        properties={k: v for k, v in vertex.items() 
                                  if k not in ["_key", "_id", "_rev", "id", "name", "type"]}
                    )
                    entities.append(entity)
                    seen_entities.add(entity_id)
                
                # Add relationship
                if edge:
                    relationship = KnowledgeRelationship(
                        from_entity=edge.get("_from", "").split("/")[-1],
                        to_entity=edge.get("_to", "").split("/")[-1],
                        relationship_type=edge.get("type", "unknown"),
                        properties={k: v for k, v in edge.items() 
                                  if k not in ["_key", "_id", "_rev", "_from", "_to", "type"]}
                    )
                    relationships.append(relationship)
            
            query_time_ms = (time.time() - query_start) * 1000
            
            logger.debug(
                "Relationship search completed",
                entity_id=entity_id,
                entity_count=len(entities),
                relationship_count=len(relationships),
                query_time_ms=round(query_time_ms, 2)
            )
            
            return KnowledgeGraphResult(
                entities=entities,
                relationships=relationships,
                query_time_ms=query_time_ms,
                total_results=len(entities) + len(relationships)
            )
            
        except asyncio.TimeoutError:
            logger.warning("Relationship search timed out", entity_id=entity_id, timeout=query_timeout)
            return KnowledgeGraphResult(entities=[], relationships=[], 
                                      query_time_ms=query_timeout * 1000, total_results=0)
        except Exception as e:
            logger.error("Relationship search failed", entity_id=entity_id, error=str(e))
            return KnowledgeGraphResult(entities=[], relationships=[], 
                                      query_time_ms=(time.time() - query_start) * 1000, total_results=0)
    
    async def query_context_for_synthesis(self, query: str, max_results: int = 10,
                                         timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Get knowledge graph context for query synthesis.
        
        Args:
            query: User query
            max_results: Maximum number of context items
            timeout: Query timeout (default 1.5s)
            
        Returns:
            Dictionary with context for synthesis
        """
        query_timeout = timeout or self.default_timeout
        context_start = time.time()
        
        try:
            # Find relevant entities
            entity_result = await self.find_entities(
                query, limit=max_results // 2, timeout=query_timeout / 2
            )
            
            context_items = []
            
            # Process entities into context
            for entity in entity_result.entities:
                context_items.append({
                    "type": "entity",
                    "content": f"{entity.name} ({entity.type})",
                    "metadata": entity.properties,
                    "confidence": entity.confidence
                })
            
            # If we have entities, get their relationships
            if entity_result.entities and len(context_items) < max_results:
                remaining_timeout = query_timeout - ((time.time() - context_start))
                if remaining_timeout > 0.1:  # At least 100ms left
                    
                    # Get relationships for first few entities
                    for entity in entity_result.entities[:3]:
                        try:
                            rel_result = await self.find_relationships(
                                entity.id, limit=3, timeout=remaining_timeout / 3
                            )
                            
                            for rel in rel_result.relationships:
                                if len(context_items) < max_results:
                                    context_items.append({
                                        "type": "relationship",
                                        "content": f"{rel.from_entity} --{rel.relationship_type}--> {rel.to_entity}",
                                        "metadata": rel.properties,
                                        "confidence": rel.confidence
                                    })
                                    
                        except Exception as e:
                            logger.debug("Failed to get relationships", entity_id=entity.id, error=str(e))
                            continue
            
            context_time_ms = (time.time() - context_start) * 1000
            
            logger.debug(
                "Knowledge graph context generated",
                query=query,
                context_items=len(context_items),
                context_time_ms=round(context_time_ms, 2)
            )
            
            return {
                "context_items": context_items,
                "total_items": len(context_items),
                "query_time_ms": context_time_ms,
                "source": "knowledge_graph"
            }
            
        except Exception as e:
            logger.error("Failed to generate KG context", query=query, error=str(e))
            return {
                "context_items": [],
                "total_items": 0,
                "query_time_ms": (time.time() - context_start) * 1000,
                "source": "knowledge_graph",
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Get knowledge graph service health status."""
        try:
            service = await self._get_service()
            arangodb_health = await service.health_check()
            
            return {
                "service": "knowledge_graph",
                "status": "ok" if arangodb_health.get("available") else "error",
                "arangodb": arangodb_health,
                "timeout_setting": self.default_timeout
            }
            
        except Exception as e:
            logger.error("KG service health check failed", error=str(e))
            return {
                "service": "knowledge_graph",
                "status": "error",
                "error": str(e),
                "timeout_setting": self.default_timeout
            }
