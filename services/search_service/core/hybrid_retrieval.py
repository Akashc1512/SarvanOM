"""
Hybrid retrieval system combining vector search and knowledge graph queries.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from shared.core.vector_database import PineconeVectorDB, ArangoDBKnowledgeGraph, HybridSearchEngine

logger = logging.getLogger(__name__)


@dataclass
class HybridSearchResult:
    """Result from hybrid search combining vector and knowledge graph."""
    id: str
    content: str
    metadata: Dict[str, Any]
    vector_score: float
    graph_score: float
    combined_score: float
    source: str


class HybridRetrievalService:
    """
    Hybrid retrieval service combining vector search and knowledge graph queries.
    
    This service provides:
    - Vector similarity search via Pinecone
    - Knowledge graph traversal via ArangoDB
    - Combined results with relevance scoring
    - Semantic understanding of relationships
    """
    
    def __init__(
        self,
        pinecone_api_key: str,
        pinecone_environment: str,
        arango_url: str = "http://localhost:8529",
        arango_username: str = "root",
        arango_password: str = "",
        arango_database: str = "knowledge_graph"
    ):
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_environment = pinecone_environment
        self.arango_url = arango_url
        self.arango_username = arango_username
        self.arango_password = arango_password
        self.arango_database = arango_database
        
        # Initialize databases
        self.vector_db = PineconeVectorDB(
            api_key=pinecone_api_key,
            environment=pinecone_environment
        )
        
        self.knowledge_graph = ArangoDBKnowledgeGraph(
            url=arango_url,
            username=arango_username,
            password=arango_password,
            database=arango_database
        )
        
        # Initialize hybrid search engine
        self.hybrid_engine = HybridSearchEngine(
            vector_db=self.vector_db,
            knowledge_graph=self.knowledge_graph
        )
        
        logger.info("HybridRetrievalService initialized successfully")
    
    async def hybrid_search(
        self,
        query: str,
        query_vector: List[float],
        top_k: int = 10,
        vector_weight: float = 0.7,
        graph_weight: float = 0.3,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[HybridSearchResult]:
        """
        Perform hybrid search combining vector similarity and knowledge graph.
        
        Args:
            query: Text query for semantic understanding
            query_vector: Vector representation of the query
            top_k: Number of results to return
            vector_weight: Weight for vector similarity scores
            graph_weight: Weight for knowledge graph relevance
            filter: Optional filter for vector search
            
        Returns:
            Combined search results with relevance scores
        """
        try:
            # Perform hybrid search
            results = await self.hybrid_engine.hybrid_search(
                query=query,
                query_vector=query_vector,
                top_k=top_k,
                vector_weight=vector_weight,
                graph_weight=graph_weight,
                filter=filter
            )
            
            # Convert to HybridSearchResult objects
            hybrid_results = []
            for result in results:
                hybrid_results.append(HybridSearchResult(
                    id=result["id"],
                    content=result["content"],
                    metadata=result["metadata"],
                    vector_score=result["vector_score"],
                    graph_score=result["graph_score"],
                    combined_score=result["combined_score"],
                    source=result["source"]
                ))
            
            logger.info(
                "Hybrid search completed",
                query=query[:50],
                results_count=len(hybrid_results),
                vector_weight=vector_weight,
                graph_weight=graph_weight
            )
            
            return hybrid_results
            
        except Exception as e:
            logger.error("Hybrid search failed", error=str(e))
            return []
    
    async def vector_only_search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[HybridSearchResult]:
        """Perform vector-only search."""
        try:
            vector_results = await self.vector_db.search_vectors(
                query_vector=query_vector,
                top_k=top_k,
                filter=filter
            )
            
            # Convert to HybridSearchResult objects
            results = []
            for result in vector_results:
                results.append(HybridSearchResult(
                    id=result.id,
                    content=result.content,
                    metadata=result.metadata,
                    vector_score=result.score,
                    graph_score=0.0,
                    combined_score=result.score,
                    source="vector_search"
                ))
            
            return results
            
        except Exception as e:
            logger.error("Vector-only search failed", error=str(e))
            return []
    
    async def knowledge_graph_search(
        self,
        query: str,
        top_k: int = 10
    ) -> List[HybridSearchResult]:
        """Perform knowledge graph-only search."""
        try:
            # Simple AQL query to find relevant entities
            aql_query = """
            FOR doc IN entities
            FILTER CONTAINS(LOWER(doc.name), LOWER(@query)) 
               OR CONTAINS(LOWER(doc.description), LOWER(@query))
            RETURN {
                id: doc._key,
                name: doc.name,
                type: doc.type,
                description: doc.description,
                score: 0.8,
                source: 'knowledge_graph'
            }
            LIMIT @limit
            """
            
            result = await self.knowledge_graph.query_knowledge_graph(
                query=aql_query,
                parameters={"query": query, "limit": top_k}
            )
            
            # Convert to HybridSearchResult objects
            results = []
            for entity in result.entities:
                results.append(HybridSearchResult(
                    id=entity.get("id", ""),
                    content=entity.get("description", ""),
                    metadata=entity,
                    vector_score=0.0,
                    graph_score=entity.get("score", 0.0),
                    combined_score=entity.get("score", 0.0),
                    source="knowledge_graph"
                ))
            
            return results
            
        except Exception as e:
            logger.error("Knowledge graph search failed", error=str(e))
            return []
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the hybrid retrieval service."""
        return {
            "status": "healthy" if self.vector_db.connected and self.knowledge_graph.connected else "disconnected",
            "service_type": "hybrid_retrieval",
            "vector_db_status": self.vector_db.get_health_status(),
            "knowledge_graph_status": self.knowledge_graph.get_health_status(),
            "hybrid_engine_status": self.hybrid_engine.get_health_status()
        } 