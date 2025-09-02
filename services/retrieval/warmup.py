"""
Retrieval Service Warmup Module

This module provides warmup functionality to initialize services and reduce
first-query latency by pre-loading models, establishing connections, and
running dummy queries.
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional

from shared.core.logging import get_logger
from shared.contracts.query import RetrievalSearchRequest
from services.retrieval.orchestrator import get_orchestrator

logger = get_logger(__name__)


class RetrievalWarmup:
    """Handles warmup operations for retrieval services."""
    
    def __init__(self):
        self.warmup_completed = False
        self.warmup_start_time: Optional[float] = None
        self.warmup_duration: Optional[float] = None
    
    async def warmup_services(self) -> Dict[str, Any]:
        """
        Perform comprehensive warmup of all retrieval services.
        
        This includes:
        - Pre-loading embedding models
        - Initializing vector stores
        - Establishing KG connections
        - Running dummy queries to warm caches
        """
        if self.warmup_completed:
            logger.info("Warmup already completed, skipping")
            return {"status": "already_warmed", "duration_ms": 0}
        
        self.warmup_start_time = time.time()
        logger.info("Starting retrieval services warmup...")
        
        warmup_results = {
            "embedding_warmup": await self._warmup_embeddings(),
            "vector_store_warmup": await self._warmup_vector_store(),
            "knowledge_graph_warmup": await self._warmup_knowledge_graph(),
            "web_search_warmup": await self._warmup_web_search(),
            "orchestrator_warmup": await self._warmup_orchestrator(),
        }
        
        self.warmup_duration = (time.time() - self.warmup_start_time) * 1000
        self.warmup_completed = True
        
        logger.info(
            f"Retrieval services warmup completed in {self.warmup_duration:.2f}ms",
            extra={
                "warmup_duration_ms": self.warmup_duration,
                "warmup_results": warmup_results
            }
        )
        
        return {
            "status": "completed",
            "duration_ms": self.warmup_duration,
            "results": warmup_results
        }
    
    async def _warmup_embeddings(self) -> Dict[str, Any]:
        """Warmup embedding models."""
        try:
            from shared.embeddings.local_embedder import embed_texts
            
            # Run a few dummy embeddings to initialize the model
            dummy_texts = [
                "warmup query for embedding model",
                "artificial intelligence and machine learning",
                "knowledge graph and vector search"
            ]
            
            start_time = time.time()
            embeddings = embed_texts(dummy_texts)
            duration_ms = (time.time() - start_time) * 1000
            
            logger.info(f"Embedding warmup completed in {duration_ms:.2f}ms")
            
            return {
                "status": "success",
                "duration_ms": duration_ms,
                "embeddings_generated": len(embeddings)
            }
            
        except Exception as e:
            logger.warning(f"Embedding warmup failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _warmup_vector_store(self) -> Dict[str, Any]:
        """Warmup vector store connections."""
        try:
            from services.retrieval.main import VECTOR_STORE
            from shared.embeddings.local_embedder import embed_texts
            
            # Generate a dummy embedding and perform a search
            dummy_query = "warmup vector search"
            start_time = time.time()
            
            query_embedding = embed_texts([dummy_query])[0]
            search_results = await VECTOR_STORE.search(
                query_embedding=query_embedding,
                top_k=1
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            logger.info(f"Vector store warmup completed in {duration_ms:.2f}ms")
            
            return {
                "status": "success",
                "duration_ms": duration_ms,
                "results_found": len(search_results)
            }
            
        except Exception as e:
            logger.warning(f"Vector store warmup failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _warmup_knowledge_graph(self) -> Dict[str, Any]:
        """Warmup knowledge graph connections."""
        try:
            from shared.core.agents.knowledge_graph_service import KnowledgeGraphService
            
            # Initialize KG service and run a dummy query
            kg_service = KnowledgeGraphService()
            start_time = time.time()
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            kg_result = await loop.run_in_executor(
                None,
                lambda: kg_service.query("warmup knowledge graph query", "entity_relationship")
            )
            
            # Ensure we have a proper result object
            if hasattr(kg_result, 'entities') and hasattr(kg_result, 'relationships'):
                entities_count = len(kg_result.entities)
                relationships_count = len(kg_result.relationships)
            else:
                # Handle case where KG service returns different format
                entities_count = 0
                relationships_count = 0
            
            duration_ms = (time.time() - start_time) * 1000
            
            logger.info(f"Knowledge graph warmup completed in {duration_ms:.2f}ms")
            
            return {
                "status": "success",
                "duration_ms": duration_ms,
                "entities_found": entities_count,
                "relationships_found": relationships_count
            }
            
        except Exception as e:
            logger.warning(f"Knowledge graph warmup failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _warmup_web_search(self) -> Dict[str, Any]:
        """Warmup web search APIs."""
        try:
            import os
            import requests
            
            # Check API availability without making actual searches
            brave_key = os.getenv("BRAVE_SEARCH_API_KEY")
            serpapi_key = os.getenv("SERPAPI_KEY")
            
            start_time = time.time()
            
            if brave_key:
                # Test Brave API connectivity
                headers = {"X-Subscription-Token": brave_key}
                params = {"q": "test", "count": 1}
                response = requests.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    headers=headers,
                    params=params,
                    timeout=5
                )
                api_status = "brave_available" if response.ok else "brave_unavailable"
            elif serpapi_key:
                # Test SerpAPI connectivity
                params = {
                    "engine": "google",
                    "q": "test",
                    "api_key": serpapi_key,
                    "num": 1
                }
                response = requests.get(
                    "https://serpapi.com/search.json",
                    params=params,
                    timeout=5
                )
                api_status = "serpapi_available" if response.ok else "serpapi_unavailable"
            else:
                api_status = "no_api_keys"
            
            duration_ms = (time.time() - start_time) * 1000
            
            logger.info(f"Web search warmup completed in {duration_ms:.2f}ms")
            
            return {
                "status": "success",
                "duration_ms": duration_ms,
                "api_status": api_status
            }
            
        except Exception as e:
            logger.warning(f"Web search warmup failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _warmup_orchestrator(self) -> Dict[str, Any]:
        """Warmup the retrieval orchestrator with a dummy query."""
        try:
            orchestrator = get_orchestrator()
            
            # Run a simple orchestrated query to warm up all components
            dummy_request = RetrievalSearchRequest(
                query="warmup orchestrated retrieval",
                max_results=3
            )
            
            start_time = time.time()
            response = await orchestrator.orchestrate_retrieval(dummy_request)
            duration_ms = (time.time() - start_time) * 1000
            
            logger.info(f"Orchestrator warmup completed in {duration_ms:.2f}ms")
            
            return {
                "status": "success",
                "duration_ms": duration_ms,
                "sources_found": len(response.sources),
                "method": response.method
            }
            
        except Exception as e:
            logger.warning(f"Orchestrator warmup failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def get_warmup_status(self) -> Dict[str, Any]:
        """Get current warmup status."""
        return {
            "warmup_completed": self.warmup_completed,
            "warmup_duration_ms": self.warmup_duration,
            "warmup_start_time": self.warmup_start_time
        }


# Global warmup instance
_warmup_instance: Optional[RetrievalWarmup] = None


def get_warmup() -> RetrievalWarmup:
    """Get the global warmup instance."""
    global _warmup_instance
    if _warmup_instance is None:
        _warmup_instance = RetrievalWarmup()
    return _warmup_instance


async def warmup_retrieval_services() -> Dict[str, Any]:
    """Convenience function to warmup all retrieval services."""
    warmup = get_warmup()
    return await warmup.warmup_services()
