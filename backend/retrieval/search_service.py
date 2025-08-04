"""
Search Service

This service provides search and retrieval functionality by wrapping the existing
retrieval agent and providing a clean interface for the API gateway.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import the existing retrieval agent
from .retrieval_agent import RetrievalAgent

logger = logging.getLogger(__name__)


class SearchService:
    """
    Search Service that provides search and retrieval functionality.
    Wraps the existing RetrievalAgent to provide a clean API interface.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.retrieval_agent = RetrievalAgent(config)
        logger.info("SearchService initialized")
    
    async def search(self, query: str, user_id: str = None, context: Dict[str, Any] = None, max_results: int = 10) -> Dict[str, Any]:
        """Search for information using the retrieval agent."""
        try:
            # Prepare search context
            search_context = {
                "user_id": user_id,
                "max_results": max_results,
                "timestamp": datetime.now().isoformat(),
                **(context or {})
            }
            
            # Perform search using retrieval agent
            results = await self.retrieval_agent.search(
                query=query,
                context=search_context
            )
            
            return {
                "status": "success",
                "results": results,
                "query": query,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
    
    async def hybrid_search(self, query: str, user_id: str = None, **kwargs) -> Dict[str, Any]:
        """Perform hybrid search combining multiple search methods."""
        try:
            results = await self.retrieval_agent.hybrid_search(
                query=query,
                user_id=user_id,
                **kwargs
            )
            
            return {
                "status": "success",
                "results": results,
                "query": query,
                "search_type": "hybrid",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
    
    async def vector_search(self, query: str, top_k: int = 10, **kwargs) -> Dict[str, Any]:
        """Perform vector-based search."""
        try:
            results = await self.retrieval_agent.vector_search(
                query=query,
                top_k=top_k,
                **kwargs
            )
            
            return {
                "status": "success",
                "results": results,
                "query": query,
                "search_type": "vector",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
    
    async def keyword_search(self, query: str, max_results: int = 10, **kwargs) -> Dict[str, Any]:
        """Perform keyword-based search."""
        try:
            results = await self.retrieval_agent.keyword_search(
                query=query,
                max_results=max_results,
                **kwargs
            )
            
            return {
                "status": "success",
                "results": results,
                "query": query,
                "search_type": "keyword",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
    
    async def graph_search(self, query: str, max_depth: int = 2, **kwargs) -> Dict[str, Any]:
        """Perform knowledge graph search."""
        try:
            results = await self.retrieval_agent.graph_search(
                query=query,
                max_depth=max_depth,
                **kwargs
            )
            
            return {
                "status": "success",
                "results": results,
                "query": query,
                "search_type": "graph",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Graph search failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status and configuration."""
        return {
            "service": "search",
            "status": "healthy",
            "agent_available": hasattr(self, 'retrieval_agent'),
            "config": self.config,
            "timestamp": datetime.now().isoformat()
        }
    
    async def shutdown(self):
        """Shutdown the search service."""
        logger.info("Shutting down SearchService")
        # Cleanup if needed
        pass 