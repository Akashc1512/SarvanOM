#!/usr/bin/env python3
"""
Cache Manager Integration Example

This module provides examples of cache manager integration.

# DEAD CODE - Candidate for deletion: This example file is not referenced anywhere in the codebase
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from shared.core.cache_manager_postgres import CacheManagerPostgres
from shared.core.database import get_database_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HybridRetrievalEngineWithCache:
    """
    Example hybrid retrieval engine with PostgreSQL caching.
    
    This demonstrates how to use cache manager in retrieval
    to avoid redundant API calls and optimize performance.
    """
    
    def __init__(self):
        """Initialize retrieval engine with cache manager."""
        self.cache_manager = CacheManagerPostgres()
        logger.info("HybridRetrievalEngineWithCache initialized with PostgreSQL cache")
    
    async def retrieve(
        self, 
        query: str, 
        max_results: int = 5,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Retrieve information with caching.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            use_cache: Whether to use caching
            
        Returns:
            Dictionary containing retrieval results
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # Generate cache key for retrieval
            cache_key = self.cache_manager.generate_cache_key(
                "retrieval", query, max_results
            )
            
            # Check cache first if enabled
            if use_cache:
                cached_results = await self.cache_manager.get_cache(cache_key)
                if cached_results:
                    logger.info(f"Cache HIT for retrieval query: {query[:50]}...")
                    cached_results["metadata"] = {
                        "cached": True,
                        "cache_key": cache_key,
                        "processing_time_ms": (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                    }
                    return cached_results
            
            logger.info(f"Cache MISS for retrieval query: {query[:50]}...")
            
            # Perform actual retrieval (simulated)
            results = await self._perform_retrieval(query, max_results)
            
            # Cache results for future use
            if use_cache:
                cache_data = {
                    "query": query,
                    "max_results": max_results,
                    "results": results["results"],
                    "total_found": results["total_found"],
                    "search_time_ms": results["search_time_ms"],
                    "retrieval_method": results["retrieval_method"]
                }
                
                # Cache for 30 minutes
                await self.cache_manager.set_cache(cache_key, cache_data, ttl_minutes=30)
                logger.info(f"Cached retrieval results for key: {cache_key}")
            
            # Add metadata
            results["metadata"] = {
                "cached": False,
                "cache_key": cache_key,
                "processing_time_ms": (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error in retrieval for query '{query}': {e}")
            return {
                "query": query,
                "results": [],
                "total_found": 0,
                "search_time_ms": 0,
                "retrieval_method": "error",
                "error": str(e),
                "metadata": {
                    "cached": False,
                    "error": True,
                    "processing_time_ms": (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                }
            }
    
    async def _perform_retrieval(self, query: str, max_results: int) -> Dict[str, Any]:
        """
        Perform actual retrieval (simulated).
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            Retrieval results
        """
        # Simulate retrieval from multiple sources
        # In a real implementation, this would call Meilisearch and Vector search
        
        # Simulate different retrieval methods
        retrieval_methods = ["hybrid", "vector", "keyword"]
        current_method = retrieval_methods[hash(query) % len(retrieval_methods)]
        
        # Simulate results based on query
        if "python" in query.lower():
            results = [
                {"title": "Python Programming Guide", "content": "Python is a versatile language...", "score": 0.95, "source": "docs.python.org"},
                {"title": "Python Installation", "content": "Download Python from python.org...", "score": 0.87, "source": "python.org"},
                {"title": "Python Tutorial", "content": "Learn Python step by step...", "score": 0.82, "source": "tutorialspoint.com"}
            ]
        elif "machine learning" in query.lower():
            results = [
                {"title": "ML Basics", "content": "Machine learning fundamentals...", "score": 0.94, "source": "ml.org"},
                {"title": "AI Guide", "content": "Artificial intelligence overview...", "score": 0.89, "source": "ai-guide.com"},
                {"title": "Data Science", "content": "Data science principles...", "score": 0.85, "source": "datascience.com"}
            ]
        else:
            results = [
                {"title": "General Information", "content": "Here is some general information...", "score": 0.75, "source": "general.com"},
                {"title": "Helpful Resource", "content": "This might be helpful...", "score": 0.70, "source": "helpful.com"}
            ]
        
        return {
            "query": query,
            "results": results[:max_results],
            "total_found": len(results),
            "search_time_ms": 150 + (hash(query) % 100),  # Simulate variable search time
            "retrieval_method": current_method
        }


class OrchestratorWithCache:
    """
    Example orchestrator with PostgreSQL caching.
    
    This demonstrates how to use cache manager in orchestrator
    to cache final LLM answers and avoid redundant processing.
    """
    
    def __init__(self):
        """Initialize orchestrator with cache manager."""
        self.cache_manager = CacheManagerPostgres()
        self.retrieval_engine = HybridRetrievalEngineWithCache()
        logger.info("OrchestratorWithCache initialized with PostgreSQL cache")
    
    async def process_query(
        self, 
        query: str, 
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process query with caching.
        
        Args:
            query: User's query
            user_context: Optional user context
            
        Returns:
            Dictionary containing answer and metadata
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # Generate cache key for answer
            cache_key = self.cache_manager.generate_cache_key(
                "answer", query, user_context or {}
            )
            
            # Check cache first
            cached_answer = await self.cache_manager.get_cache(cache_key)
            if cached_answer:
                logger.info(f"Cache HIT for answer query: {query[:50]}...")
                cached_answer["metadata"] = {
                    "cached": True,
                    "cache_key": cache_key,
                    "processing_time_ms": (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                }
                return cached_answer
            
            logger.info(f"Cache MISS for answer query: {query[:50]}...")
            
            # Perform retrieval
            retrieval_results = await self.retrieval_engine.retrieve(query, max_results=5)
            
            # Generate answer (simulated LLM processing)
            answer = await self._generate_answer(query, retrieval_results, user_context)
            
            # Cache answer for future use
            cache_data = {
                "query": query,
                "answer": answer["answer"],
                "confidence": answer["confidence"],
                "sources": answer["sources"],
                "model_used": answer["model_used"],
                "tokens_used": answer["tokens_used"],
                "processing_time_ms": answer["processing_time_ms"],
                "retrieval_results": retrieval_results
            }
            
            # Cache for 2 hours
            await self.cache_manager.set_cache(cache_key, cache_data, ttl_minutes=120)
            logger.info(f"Cached answer for key: {cache_key}")
            
            # Add metadata
            answer["metadata"] = {
                "cached": False,
                "cache_key": cache_key,
                "processing_time_ms": (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            }
            
            return answer
            
        except Exception as e:
            logger.error(f"Error processing query '{query}': {e}")
            return {
                "query": query,
                "answer": f"Sorry, I encountered an error: {str(e)}",
                "confidence": 0.0,
                "sources": [],
                "model_used": "error",
                "tokens_used": 0,
                "processing_time_ms": 0,
                "error": str(e),
                "metadata": {
                    "cached": False,
                    "error": True,
                    "processing_time_ms": (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                }
            }
    
    async def _generate_answer(
        self, 
        query: str, 
        retrieval_results: Dict[str, Any], 
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate answer from retrieval results (simulated LLM).
        
        Args:
            query: User's query
            retrieval_results: Results from retrieval engine
            user_context: Optional user context
            
        Returns:
            Generated answer
        """
        # Simulate LLM processing
        # In a real implementation, this would call the LLM service
        
        # Extract sources from retrieval results
        sources = []
        for result in retrieval_results.get("results", []):
            sources.append({
                "title": result.get("title", "Unknown"),
                "url": result.get("source", ""),
                "relevance": result.get("score", 0.0)
            })
        
        # Generate answer based on query and sources
        if "python" in query.lower():
            answer = "Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used in web development, data science, AI, and automation."
            confidence = 0.95
        elif "machine learning" in query.lower():
            answer = "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed."
            confidence = 0.92
        else:
            answer = f"Based on the available information, here's what I found about '{query}'. The sources provide relevant context for your question."
            confidence = 0.85
        
        return {
            "query": query,
            "answer": answer,
            "confidence": confidence,
            "sources": sources,
            "model_used": "gpt-4-simulated",
            "tokens_used": len(answer.split()) * 1.3,  # Rough token estimation
            "processing_time_ms": 2500 + (hash(query) % 1000)  # Simulate variable processing time
        }
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return await self.cache_manager.get_cache_stats()
    
    async def clear_expired_cache(self) -> int:
        """Clear expired cache entries."""
        return await self.cache_manager.clear_expired_cache()


async def demo_cache_integration():
    """Demonstrate cache manager integration with retrieval and orchestrator."""
    logger.info("Starting Cache Manager PostgreSQL Integration Demo")
    
    # Initialize orchestrator with cache
    orchestrator = OrchestratorWithCache()
    
    # Sample queries
    queries = [
        "What is Python?",
        "How does machine learning work?",
        "What is Python?",  # Duplicate to test caching
        "Explain artificial intelligence",
        "How do I install Python?"
    ]
    
    logger.info(f"Processing {len(queries)} queries with caching...")
    
    for i, query in enumerate(queries, 1):
        logger.info(f"\n--- Query {i} ---")
        logger.info(f"User: {query}")
        
        # Process query
        response = await orchestrator.process_query(query)
        
        logger.info(f"Answer: {response['answer'][:100]}...")
        logger.info(f"Confidence: {response['confidence']:.2f}")
        logger.info(f"Cached: {response['metadata']['cached']}")
        logger.info(f"Processing time: {response['metadata']['processing_time_ms']:.2f}ms")
        
        # Small delay to simulate processing time
        await asyncio.sleep(0.5)
    
    # Get cache statistics
    logger.info("\n--- Cache Statistics ---")
    stats = await orchestrator.get_cache_stats()
    logger.info(f"Total entries: {stats['total_entries']}")
    logger.info(f"Active entries: {stats['active_entries']}")
    logger.info(f"Expired entries: {stats['expired_entries']}")
    
    # Demonstrate cache key generation
    logger.info("\n--- Cache Key Generation Demo ---")
    cache_manager = CacheManagerPostgres()
    
    # Generate different cache keys
    key1 = cache_manager.generate_cache_key("retrieval", "What is Python?", 5)
    key2 = cache_manager.generate_cache_key("answer", "What is Python?")
    key3 = cache_manager.generate_cache_key("retrieval", "What is Python?", 10)
    
    logger.info(f"Retrieval key (max_results=5): {key1}")
    logger.info(f"Answer key: {key2}")
    logger.info(f"Retrieval key (max_results=10): {key3}")
    
    # Clear expired cache
    logger.info("\n--- Cache Cleanup ---")
    cleared_count = await orchestrator.clear_expired_cache()
    logger.info(f"Cleared {cleared_count} expired cache entries")
    
    logger.info("\nDemo completed successfully!")


async def demo_ttl_behavior():
    """Demonstrate TTL behavior of the cache manager."""
    logger.info("Starting TTL Behavior Demo")
    
    cache_manager = CacheManagerPostgres()
    
    # Test different TTL scenarios
    test_data = {
        "short_ttl": {"data": "Short TTL data", "ttl": 1},  # 1 minute
        "long_ttl": {"data": "Long TTL data", "ttl": 60},   # 1 hour
        "no_ttl": {"data": "No TTL data", "ttl": 0}        # No expiration
    }
    
    for name, config in test_data.items():
        cache_key = f"ttl_test_{name}"
        
        # Set cache with specific TTL
        success = await cache_manager.set_cache(
            cache_key, 
            config["data"], 
            ttl_minutes=config["ttl"]
        )
        
        if success:
            logger.info(f"Set cache for {name} with TTL: {config['ttl']} minutes")
            
            # Get cache immediately
            cached_data = await cache_manager.get_cache(cache_key)
            if cached_data:
                logger.info(f"  ✓ Retrieved {name} immediately")
            else:
                logger.info(f"  ✗ Failed to retrieve {name}")
    
    # Get cache statistics
    stats = await cache_manager.get_cache_stats()
    logger.info(f"Cache stats: {stats}")
    
    logger.info("TTL behavior demo completed!")


if __name__ == "__main__":
    # Run demos
    asyncio.run(demo_cache_integration())
    asyncio.run(demo_ttl_behavior()) 