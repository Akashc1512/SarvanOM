from shared.core.api.config import get_settings
settings = get_settings()
"""
Hybrid retrieval system combining vector search and knowledge graph queries.
"""

import asyncio
import logging
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logging.warning("python-dotenv not available. Install with: pip install python-dotenv")

from shared.core.vector_database import PineconeVectorDB, ArangoDBKnowledgeGraph, HybridSearchEngine

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Simple retrieval result for internal use."""
    content: str
    source: str
    score: float
    metadata: Dict[str, Any]


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


class RetrievalSource(Enum):
    """Enumeration of retrieval sources."""
    MEILISEARCH = "meilisearch"
    VECTOR_DB = "vector_db"
    KNOWLEDGE_GRAPH = "knowledge_graph"


class FusionStrategy(Enum):
    """Enumeration of fusion strategies."""
    WEIGHTED_SUM = "weighted_sum"
    AVERAGE = "average"
    MAX = "max"


@dataclass
class EnhancedRetrievalResult:
    """Enhanced retrieval result with metadata."""
    document_id: str
    title: str
    content: str
    snippet: str
    combined_score: float
    source_scores: Dict[str, float]
    source_types: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime


@dataclass
class HybridRetrievalResultV2:
    """Enhanced hybrid retrieval result."""
    query: str
    fused_content: str
    enhanced_results: List[EnhancedRetrievalResult]
    fusion_strategy: FusionStrategy
    confidence_score: float
    processing_time_ms: float
    metadata: Dict[str, Any]
    timestamp: datetime


class HybridRetrievalEngine:
    """
    Enhanced hybrid retrieval engine combining Meilisearch and vector search.
    
    This engine provides:
    - Keyword search via Meilisearch
    - Vector similarity search via Pinecone/Qdrant
    - Score normalization and fusion
    - Enhanced metadata and result structure
    """
    
    def __init__(
        self,
        meilisearch_url: str = None,
        meilisearch_api_key: str = None,
        pinecone_api_key: str = None,
        pinecone_environment: str = None,
        vector_weight: float = 0.5,
        meilisearch_weight: float = 0.5
    ):
        # Initialize Meilisearch
        if meilisearch_url is None:
            meilisearch_url = settings.meilisearch_url or "http://localhost:7700"
        if meilisearch_api_key is None:
            # Try master key first, then API key
            meilisearch_api_key = settings.meilisearch_master_key or settings.meilisearch_api_key
        
        self.meilisearch_engine = None
        try:
            # Import here to avoid circular imports
            from services.search_service.core.meilisearch_engine import MeilisearchEngine
            self.meilisearch_engine = MeilisearchEngine(meilisearch_url, meilisearch_api_key)
            logger.info("Meilisearch engine initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Meilisearch engine: {e}")
            self.meilisearch_engine = None
        
        # Initialize vector database (lazy initialization)
        self.vector_db = None
        self.vector_db_initialized = False
        
        # Store configuration
        self.vector_weight = vector_weight
        self.meilisearch_weight = meilisearch_weight
        
        # Store API keys for lazy initialization
        self.pinecone_api_key = pinecone_api_key or settings.pinecone_api_key
        self.pinecone_environment = pinecone_environment or settings.pinecone_environment or "us-west1-gcp"
        
        logger.info("HybridRetrievalEngine initialized successfully")
    
    async def _initialize_vector_db(self):
        """Initialize vector database when needed."""
        if self.vector_db_initialized or not (self.pinecone_api_key and self.pinecone_environment):
            return
        
        try:
            from shared.core.vector_database import PineconeVectorDB
            self.vector_db = PineconeVectorDB(
                api_key=self.pinecone_api_key,
                environment=self.pinecone_environment
            )
            self.vector_db_initialized = True
            logger.info("Vector database initialized successfully")
        except Exception as e:
            logger.warning(f"Vector database initialization failed: {e}")
            self.vector_db = None
    
    async def retrieve(
        self,
        query: str,
        max_results: int = 10,
        fusion_strategy: FusionStrategy = FusionStrategy.WEIGHTED_SUM,
        sources: List[RetrievalSource] = None
    ) -> HybridRetrievalResultV2:
        """
        Perform hybrid retrieval using Meilisearch and vector search.
        
        Args:
            query: User query
            max_results: Maximum number of results to return
            fusion_strategy: Strategy for combining scores
            sources: List of sources to use (default: all available)
            
        Returns:
            Enhanced hybrid retrieval result with normalized scores and metadata
        """
        start_time = datetime.now()
        
        # Initialize vector database if needed
        await self._initialize_vector_db()
        
        # Default to all available sources
        if sources is None:
            sources = [RetrievalSource.MEILISEARCH]
            if self.vector_db:
                sources.append(RetrievalSource.VECTOR_DB)
        
        try:
            # Execute parallel searches
            search_tasks = []
            
            if RetrievalSource.MEILISEARCH in sources:
                search_tasks.append(self._meilisearch_search(query, max_results))
            
            if RetrievalSource.VECTOR_DB in sources and self.vector_db:
                search_tasks.append(self._vector_search(query, max_results))
            
            # Execute all searches in parallel
            if search_tasks:
                results = await asyncio.gather(*search_tasks, return_exceptions=True)
                
                # Process results and handle exceptions
                meilisearch_results = []
                vector_results = []
                
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.warning(f"Search {i} failed: {result}")
                        continue
                    
                    if i == 0 and RetrievalSource.MEILISEARCH in sources:
                        meilisearch_results = result
                    elif i == 1 and RetrievalSource.VECTOR_DB in sources:
                        vector_results = result
                
                # Perform score normalization and fusion
                enhanced_results = await self._perform_score_fusion(
                    meilisearch_results, vector_results, fusion_strategy
                )
                
                # Create fused content from top results
                fused_content = self._create_fused_content(enhanced_results)
                
                processing_time = (datetime.now() - start_time).total_seconds() * 1000
                
                return HybridRetrievalResultV2(
                    query=query,
                    fused_content=fused_content,
                    enhanced_results=enhanced_results,
                    fusion_strategy=fusion_strategy,
                    confidence_score=self._calculate_confidence_score(enhanced_results),
                    processing_time_ms=processing_time,
                    metadata={
                        "sources_used": [source.value for source in sources],
                        "total_results": len(enhanced_results),
                        "fusion_strategy": fusion_strategy.value
                    },
                    timestamp=datetime.now()
                )
            
            # Fallback if no searches were executed
            logger.warning("No search sources available")
            return self._create_empty_result(query, start_time)
            
        except Exception as e:
            logger.error(f"Hybrid retrieval failed: {e}")
            return self._create_empty_result(query, start_time)
    
    async def _meilisearch_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform Meilisearch search."""
        try:
            if not self.meilisearch_engine:
                logger.warning("Meilisearch engine not available")
                return []
            
            results = await self.meilisearch_engine.search(query, top_k=max_results)
            
            # Convert to standardized format
            formatted_results = []
            for result in results:
                # Debug: Print the raw score
                logger.info(f"Meilisearch raw score for '{result.metadata.get('title', 'Unknown')}': {result.score}")
                
                formatted_results.append({
                    "id": result.metadata.get("meilisearch_id", result.metadata.get("title", "unknown")),
                    "title": result.metadata.get("title", "Unknown"),
                    "content": result.content,
                    "snippet": result.content[:200] + "..." if len(result.content) > 200 else result.content,
                    "score": result.score,
                    "source_type": RetrievalSource.MEILISEARCH.value,
                    "metadata": {
                        **result.metadata,
                        "source": "meilisearch"
                    }
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Meilisearch search failed: {e}")
            return []
    
    async def _vector_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform vector search."""
        try:
            # For now, we'll use a simple approach - in a real implementation,
            # you'd want to generate embeddings for the query
            # This is a placeholder that would need to be implemented with actual embedding generation
            results = await self.vector_db.search_vectors(
                query_vector=[0.0] * 1536,  # Placeholder vector
                top_k=max_results
            )
            
            # Convert to standardized format
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "title": result.metadata.get("title", "Unknown"),
                    "content": result.content,
                    "snippet": result.content[:200] + "..." if len(result.content) > 200 else result.content,
                    "score": result.score,
                    "source_type": RetrievalSource.VECTOR_DB.value,
                    "metadata": {
                        **result.metadata,
                        "source": "vector_db"
                    }
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    async def _perform_score_fusion(
        self,
        meilisearch_results: List[Dict[str, Any]],
        vector_results: List[Dict[str, Any]],
        fusion_strategy: FusionStrategy
    ) -> List[EnhancedRetrievalResult]:
        """Perform score normalization and fusion."""
        # Group results by document ID for deduplication
        document_groups = {}
        
        # Process Meilisearch results
        for result in meilisearch_results:
            doc_id = result["id"]
            if doc_id not in document_groups:
                document_groups[doc_id] = {
                    "id": doc_id,
                    "title": result["title"],
                    "content": result["content"],
                    "snippet": result["snippet"],
                    "source_scores": {},
                    "source_types": set(),
                    "metadata": result["metadata"]
                }
            
            group = document_groups[doc_id]
            group["source_types"].add(RetrievalSource.MEILISEARCH.value)
            normalized_score = self._normalize_score(result["score"], RetrievalSource.MEILISEARCH)
            group["source_scores"][RetrievalSource.MEILISEARCH.value] = normalized_score
        
        # Process vector results
        for result in vector_results:
            doc_id = result["id"]
            if doc_id not in document_groups:
                document_groups[doc_id] = {
                    "id": doc_id,
                    "title": result["title"],
                    "content": result["content"],
                    "snippet": result["snippet"],
                    "source_scores": {},
                    "source_types": set(),
                    "metadata": result["metadata"]
                }
            
            group = document_groups[doc_id]
            group["source_types"].add(RetrievalSource.VECTOR_DB.value)
            normalized_score = self._normalize_score(result["score"], RetrievalSource.VECTOR_DB)
            group["source_scores"][RetrievalSource.VECTOR_DB.value] = normalized_score
        
        # Calculate combined scores
        enhanced_results = []
        for doc_id, group in document_groups.items():
            combined_score = self._calculate_combined_score(
                group["source_scores"], fusion_strategy
            )
            
            enhanced_results.append(EnhancedRetrievalResult(
                document_id=doc_id,
                title=group["title"],
                content=group["content"],
                snippet=group["snippet"],
                combined_score=combined_score,
                source_scores=group["source_scores"],
                source_types=list(group["source_types"]),
                metadata=group["metadata"],
                timestamp=datetime.now()
            ))
        
        # Sort by combined score (descending)
        enhanced_results.sort(key=lambda x: x.combined_score, reverse=True)
        
        return enhanced_results
    
    def _normalize_score(self, score: float, source: RetrievalSource) -> float:
        """Normalize scores to 0-1 scale."""
        if source == RetrievalSource.VECTOR_DB:
            # Vector similarity scores are typically 0-1
            return max(0.0, min(1.0, score))
        elif source == RetrievalSource.MEILISEARCH:
            # Meilisearch scores can vary, normalize to 0-1
            # Meilisearch scores are typically very small (0.001-0.1), so we scale them up
            # If score is already 0-1, use as is, otherwise scale appropriately
            if score <= 1.0:
                return score  # Already normalized
            else:
                # Scale down if score is larger than 1
                return max(0.0, min(1.0, score / 100.0))
        else:
            return max(0.0, min(1.0, score))
    
    def _calculate_combined_score(
        self,
        source_scores: Dict[str, float],
        fusion_strategy: FusionStrategy
    ) -> float:
        """Calculate combined score using specified fusion strategy."""
        if not source_scores:
            return 0.0
        
        if fusion_strategy == FusionStrategy.AVERAGE:
            return sum(source_scores.values()) / len(source_scores)
        elif fusion_strategy == FusionStrategy.MAX:
            return max(source_scores.values())
        else:  # WEIGHTED_SUM
            weights = {
                RetrievalSource.MEILISEARCH.value: self.meilisearch_weight,
                RetrievalSource.VECTOR_DB.value: self.vector_weight
            }
            
            # Calculate weighted sum
            weighted_sum = sum(
                score * weights.get(source, 0.1)
                for source, score in source_scores.items()
            )
            total_weight = sum(
                weights.get(source, 0.1)
                for source in source_scores.keys()
            )
            
            # Boost score for documents found in multiple sources
            source_count_boost = min(1.0, len(source_scores) * 0.2)
            
            base_score = weighted_sum / total_weight if total_weight > 0 else 0.0
            boosted_score = base_score * (1.0 + source_count_boost)
            
            return min(1.0, boosted_score)
    
    def _create_fused_content(self, enhanced_results: List[EnhancedRetrievalResult]) -> str:
        """Create fused content from top results."""
        if not enhanced_results:
            return "No relevant results found."
        
        # Take top 3 results and combine their snippets
        top_results = enhanced_results[:3]
        snippets = [result.snippet for result in top_results]
        
        return " ".join(snippets)
    
    def _calculate_confidence_score(self, enhanced_results: List[EnhancedRetrievalResult]) -> float:
        """Calculate overall confidence score."""
        if not enhanced_results:
            return 0.0
        
        # Average of top 3 combined scores
        top_scores = [result.combined_score for result in enhanced_results[:3]]
        return sum(top_scores) / len(top_scores)
    
    def _create_empty_result(self, query: str, start_time: datetime) -> HybridRetrievalResultV2:
        """Create empty result when no searches are available."""
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return HybridRetrievalResultV2(
            query=query,
            fused_content="No search sources available.",
            enhanced_results=[],
            fusion_strategy=FusionStrategy.WEIGHTED_SUM,
            confidence_score=0.0,
            processing_time_ms=processing_time,
            metadata={
                "sources_used": [],
                "total_results": 0,
                "fusion_strategy": FusionStrategy.WEIGHTED_SUM.value,
                "error": "No search sources available"
            },
            timestamp=datetime.now()
        )


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