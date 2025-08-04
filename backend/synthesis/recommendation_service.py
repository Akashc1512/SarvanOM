"""
Recommendation Service

This module provides recommendation functionality for the backend synthesis service.

# DEAD CODE - Candidate for deletion: This backend directory is not used by the main application
"""

import asyncio
import logging
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from shared.core.vector_database import ArangoDBKnowledgeGraph

logger = logging.getLogger(__name__)


@dataclass
class Recommendation:
    """Knowledge recommendation with metadata."""
    id: str
    title: str
    content: str
    confidence: float
    source: str
    metadata: Dict[str, Any]


class RecommendationService:
    """Service for generating knowledge recommendations."""
    
    def __init__(
        self,
        uri: str = None,
        username: str = None,
        password: str = None,
        database: str = None
    ):
        """Initialize recommendation service with ArangoDB connection."""
        self.uri = uri or settings.arango_url or "http://localhost:8529"
        self.username = username or settings.arango_username or "root"
        self.password = password or settings.arango_password or ""
        self.database = database or settings.arango_database or "knowledge_graph"
        
        # Initialize ArangoDB knowledge graph
        self.knowledge_graph = ArangoDBKnowledgeGraph(
            url=self.uri,
            username=self.username,
            password=self.password,
            database=self.database
        )
        
        logger.info("RecommendationService initialized with ArangoDB")
    
    async def get_recommendations(
        self,
        query: str,
        user_id: Optional[str] = None,
        max_recommendations: int = 5
    ) -> List[Recommendation]:
        """
        Get knowledge recommendations based on query and user context.
        
        Args:
            query: User query for context
            user_id: Optional user ID for personalized recommendations
            max_recommendations: Maximum number of recommendations to return
            
        Returns:
            List of recommendations
        """
        try:
            # Query ArangoDB for relevant entities
            aql_query = """
            FOR doc IN entities
            FILTER CONTAINS(LOWER(doc.name), LOWER(@query)) 
               OR CONTAINS(LOWER(doc.description), LOWER(@query))
            RETURN {
                id: doc._key,
                title: doc.name,
                content: doc.description,
                confidence: 0.8,
                source: 'knowledge_graph',
                metadata: doc
            }
            LIMIT @limit
            """
            
            result = await self.knowledge_graph.query_knowledge_graph(
                query=aql_query,
                parameters={"query": query, "limit": max_recommendations}
            )
            
            # Convert to Recommendation objects
            recommendations = []
            for entity in result.entities:
                recommendations.append(Recommendation(
                    id=entity.get("id", ""),
                    title=entity.get("title", ""),
                    content=entity.get("content", ""),
                    confidence=entity.get("confidence", 0.8),
                    source=entity.get("source", "knowledge_graph"),
                    metadata=entity.get("metadata", {})
                ))
            
            logger.info(f"Generated {len(recommendations)} recommendations for query: {query[:50]}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return []
    
    async def get_related_concepts(
        self,
        concept_id: str,
        max_related: int = 3
    ) -> List[Recommendation]:
        """
        Get related concepts from knowledge graph.
        
        Args:
            concept_id: ID of the concept to find related concepts for
            max_related: Maximum number of related concepts to return
            
        Returns:
            List of related concept recommendations
        """
        try:
            # Query ArangoDB for related entities
            aql_query = """
            FOR rel IN relationships
            FOR entity1 IN entities
            FOR entity2 IN entities
            FILTER rel._from == entity1._id AND rel._to == entity2._id
            FILTER entity1._key == @concept_id OR entity2._key == @concept_id
            RETURN {
                id: entity2._key,
                title: entity2.name,
                content: entity2.description,
                confidence: 0.7,
                source: 'knowledge_graph',
                metadata: {
                    relationship_type: rel.type,
                    source_entity: entity1.name,
                    target_entity: entity2.name
                }
            }
            LIMIT @limit
            """
            
            result = await self.knowledge_graph.query_knowledge_graph(
                query=aql_query,
                parameters={"concept_id": concept_id, "limit": max_related}
            )
            
            # Convert to Recommendation objects
            recommendations = []
            for entity in result.entities:
                recommendations.append(Recommendation(
                    id=entity.get("id", ""),
                    title=entity.get("title", ""),
                    content=entity.get("content", ""),
                    confidence=entity.get("confidence", 0.7),
                    source=entity.get("source", "knowledge_graph"),
                    metadata=entity.get("metadata", {})
                ))
            
            logger.info(f"Found {len(recommendations)} related concepts for concept: {concept_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get related concepts: {e}")
            return []
    
    async def get_trending_topics(self, max_topics: int = 5) -> List[Recommendation]:
        """
        Get trending topics from knowledge graph.
        
        Args:
            max_topics: Maximum number of trending topics to return
            
        Returns:
            List of trending topic recommendations
        """
        try:
            # Query ArangoDB for popular entities
            aql_query = """
            FOR doc IN entities
            SORT doc.popularity DESC
            RETURN {
                id: doc._key,
                title: doc.name,
                content: doc.description,
                confidence: 0.9,
                source: 'knowledge_graph',
                metadata: {
                    popularity: doc.popularity,
                    type: doc.type
                }
            }
            LIMIT @limit
            """
            
            result = await self.knowledge_graph.query_knowledge_graph(
                query=aql_query,
                parameters={"limit": max_topics}
            )
            
            # Convert to Recommendation objects
            recommendations = []
            for entity in result.entities:
                recommendations.append(Recommendation(
                    id=entity.get("id", ""),
                    title=entity.get("title", ""),
                    content=entity.get("content", ""),
                    confidence=entity.get("confidence", 0.9),
                    source=entity.get("source", "knowledge_graph"),
                    metadata=entity.get("metadata", {})
                ))
            
            logger.info(f"Retrieved {len(recommendations)} trending topics")
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get trending topics: {e}")
            return []
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the recommendation service."""
        return {
            "status": "healthy" if self.knowledge_graph.connected else "disconnected",
            "service_type": "recommendation",
            "knowledge_graph_status": self.knowledge_graph.get_health_status(),
            "uri": self.uri,
            "database": self.database
        }
