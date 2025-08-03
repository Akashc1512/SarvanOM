"""
Retrieval Microservice - Search Service
Core search functionality for the retrieval microservice.

This service provides:
- Document search and retrieval
- Query processing
- Result ranking and filtering
- Hybrid search (vector + keyword)
- Knowledge graph integration
"""

import asyncio
import logging
import time
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field

# Import core components
from .hybrid_retrieval import HybridRetrievalEngine
from .meilisearch_engine import MeilisearchEngine
from .query_processor import QueryProcessor

logger = logging.getLogger(__name__)

@dataclass
class Document:
    """Represents a retrieved document/chunk"""
    content: str
    score: float
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    doc_id: str = ""
    chunk_id: Optional[str] = None
    timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "score": self.score,
            "source": self.source,
            "metadata": self.metadata,
            "doc_id": self.doc_id,
            "chunk_id": self.chunk_id,
            "timestamp": self.timestamp,
        }

@dataclass
class SearchResult:
    """Unified search result format"""
    documents: List[Document]
    search_type: str
    query_time_ms: int
    total_hits: int
    metadata: Dict[str, Any] = field(default_factory=dict)

class SearchService:
    """Search service for the retrieval microservice."""
    
    def __init__(self):
        """Initialize the search service."""
        self.hybrid_engine = None
        self.meilisearch_engine = None
        self.query_processor = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all search components."""
        try:
            # Initialize Meilisearch engine
            meili_config = {
                "url": os.getenv("MEILISEARCH_URL", "http://localhost:7700"),
                "master_key": os.getenv("MEILI_MASTER_KEY", "sarvanom-master-key-2024"),
                "index_name": "documents"
            }
            self.meilisearch_engine = MeilisearchEngine(meili_config)
            
            # Initialize hybrid retrieval engine
            self.hybrid_engine = HybridRetrievalEngine()
            
            # Initialize query processor
            self.query_processor = QueryProcessor()
            
            logger.info("All retrieval components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize retrieval components: {e}")
    
    async def search(self, query: str, filters: Optional[Dict[str, Any]] = None, limit: int = 10) -> Dict[str, Any]:
        """Search for documents using the retrieval service."""
        start_time = time.time()
        
        try:
            # Process the query
            processed_query = await self.query_processor.process_query(query)
            
            # Perform hybrid search
            if self.hybrid_engine:
                result = await self.hybrid_engine.search(
                    query=processed_query,
                    filters=filters,
                    limit=limit
                )
            else:
                # Fallback to Meilisearch only
                result = await self.meilisearch_engine.search(
                    query=processed_query,
                    filters=filters,
                    limit=limit
                )
            
            query_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                "results": result.get("documents", []),
                "total": result.get("total_hits", 0),
                "query_time_ms": query_time_ms,
                "query_id": f"search_{int(time.time())}",
                "status": "success",
                "search_type": result.get("search_type", "hybrid")
            }
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                "results": [],
                "total": 0,
                "query_time_ms": int((time.time() - start_time) * 1000),
                "error": str(e),
                "status": "error"
            }
    
    async def get_result(self, query_id: str) -> Dict[str, Any]:
        """Get a specific search result by ID."""
        try:
            # This would typically query a cache or database
            # For now, return a mock result
            return {
                "query_id": query_id,
                "status": "completed",
                "results": [],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get search result {query_id}: {e}")
            return {
                "query_id": query_id,
                "status": "error",
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the retrieval service."""
        try:
            health_status = {
                "service": "retrieval",
                "status": "healthy",
                "components": {
                    "hybrid_engine": "healthy" if self.hybrid_engine else "unavailable",
                    "meilisearch_engine": "healthy" if self.meilisearch_engine else "unavailable",
                    "query_processor": "healthy" if self.query_processor else "unavailable"
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Test Meilisearch connection
            if self.meilisearch_engine:
                try:
                    await self.meilisearch_engine.health_check()
                    health_status["components"]["meilisearch_engine"] = "healthy"
                except Exception as e:
                    health_status["components"]["meilisearch_engine"] = f"unhealthy: {str(e)}"
                    health_status["status"] = "degraded"
            
            return health_status
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "service": "retrieval",
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            if self.hybrid_engine:
                await self.hybrid_engine.cleanup()
            if self.meilisearch_engine:
                await self.meilisearch_engine.cleanup()
            logger.info("Retrieval service cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}") 