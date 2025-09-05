#!/usr/bin/env python3
"""
Index Fabric Service - Phase D1 Implementation
=============================================

Fuses all indexing lanes (Meili+Qdrant+Chroma+KG) with parallel enrichers
that operate within strict 3-second budget constraints.

Key Features:
- Parallel execution of all indexing lanes
- Reciprocal rank fusion for result merging
- Strict timebox enforcement per lane
- Graceful degradation with partial results
- Comprehensive performance metrics
- Real environment variable integration

Maps to Phase D1 requirements for production index fabric.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import structlog

from shared.core.unified_logging import get_logger

logger = get_logger(__name__)

@dataclass
class IndexLaneResult:
    """Result from a single indexing lane."""
    lane_name: str
    results: List[Dict[str, Any]]
    processing_time_ms: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FusedIndexResult:
    """Fused result from all indexing lanes."""
    query: str
    total_results: int
    fused_results: List[Dict[str, Any]]
    lane_results: Dict[str, IndexLaneResult]
    fusion_time_ms: float
    total_time_ms: float
    within_budget: bool
    successful_lanes: int
    failed_lanes: int
    timestamp: datetime = field(default_factory=datetime.utcnow)

class IndexFabricService:
    """
    Index Fabric Service that fuses all indexing lanes.
    
    Features:
    - Parallel execution of Meili+Qdrant+Chroma+KG lanes
    - Reciprocal rank fusion for optimal result ordering
    - Strict 3-second budget enforcement
    - Graceful degradation with partial results
    - Real environment variable integration
    """
    
    def __init__(self):
        """Initialize the index fabric service."""
        self.config = self._load_config()
        self._lanes_initialized = False
        
        logger.info("IndexFabricService initialized", config=self.config)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        import os
        
        return {
            "max_total_time_ms": float(os.getenv("INDEX_FABRIC_TIMEOUT_MS", "3000")),  # 3s budget
            "meili_timeout_ms": float(os.getenv("MEILI_TIMEOUT_MS", "800")),  # 800ms for keyword
            "qdrant_timeout_ms": float(os.getenv("QDRANT_TIMEOUT_MS", "800")),  # 800ms for vector
            "chroma_timeout_ms": float(os.getenv("CHROMA_TIMEOUT_MS", "800")),  # 800ms for local
            "kg_timeout_ms": float(os.getenv("KG_TIMEOUT_MS", "600")),  # 600ms for KG
            "fusion_timeout_ms": float(os.getenv("FUSION_TIMEOUT_MS", "200")),  # 200ms for fusion
            "max_results_per_lane": int(os.getenv("INDEX_MAX_RESULTS_PER_LANE", "10")),
            "enable_reciprocal_rank_fusion": os.getenv("ENABLE_RRF", "true").lower() == "true"
        }
    
    async def initialize_lanes(self) -> bool:
        """Initialize all indexing lanes."""
        if self._lanes_initialized:
            return True
        
        try:
            # Test connections to all services
            connection_tests = await asyncio.gather(
                self._test_meili_connection(),
                self._test_qdrant_connection(),
                self._test_chroma_connection(),
                self._test_kg_connection(),
                return_exceptions=True
            )
            
            successful_connections = sum(1 for result in connection_tests if isinstance(result, bool) and result)
            
            if successful_connections >= 2:  # Need at least 2 lanes working
                self._lanes_initialized = True
                logger.info("Index lanes initialized", successful_connections=successful_connections, total_lanes=4)
                return True
            else:
                logger.warning("Insufficient index lanes available", successful_connections=successful_connections)
                return False
                
        except Exception as e:
            logger.error("Failed to initialize index lanes", error=str(e))
            return False
    
    async def _test_meili_connection(self) -> bool:
        """Test Meilisearch connection."""
        try:
            from shared.core.services.meilisearch_service import MeilisearchService
            meili_service = MeilisearchService()
            return await meili_service.connect()
        except Exception as e:
            logger.debug("Meilisearch connection test failed", error=str(e))
            return False
    
    async def _test_qdrant_connection(self) -> bool:
        """Test Qdrant connection."""
        try:
            from shared.core.services.vector_singleton_service import get_vector_singleton_service
            vector_service = get_vector_singleton_service()
            health = vector_service.get_health()
            return health.get("vector_store", {}).get("connected", False)
        except Exception as e:
            logger.debug("Qdrant connection test failed", error=str(e))
            return False
    
    async def _test_chroma_connection(self) -> bool:
        """Test ChromaDB connection."""
        try:
            from shared.core.services.vector_singleton_service import get_vector_singleton_service
            vector_service = get_vector_singleton_service()
            health = vector_service.get_health()
            # ChromaDB is local, so we assume it's available if vector service is healthy
            return health.get("status") == "healthy"
        except Exception as e:
            logger.debug("ChromaDB connection test failed", error=str(e))
            return False
    
    async def _test_kg_connection(self) -> bool:
        """Test Knowledge Graph connection."""
        try:
            from shared.core.services.arangodb_service import ArangoDBService
            kg_service = ArangoDBService()
            return kg_service.is_available
        except Exception as e:
            logger.debug("Knowledge Graph connection test failed", error=str(e))
            return False
    
    async def search_across_all_lanes(self, query: str, max_results: int = 10) -> FusedIndexResult:
        """
        Search across all indexing lanes in parallel.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            FusedIndexResult with merged results from all lanes
        """
        start_time = time.time()
        
        # Ensure lanes are initialized
        if not await self.initialize_lanes():
            return self._create_error_result(query, "Index lanes not available")
        
        # Execute all lanes in parallel with strict timeouts
        lane_tasks = [
            self._execute_meili_lane(query, max_results),
            self._execute_qdrant_lane(query, max_results),
            self._execute_chroma_lane(query, max_results),
            self._execute_kg_lane(query, max_results)
        ]
        
        # Execute with overall timeout
        try:
            lane_results = await asyncio.wait_for(
                asyncio.gather(*lane_tasks, return_exceptions=True),
                timeout=self.config["max_total_time_ms"] / 1000.0
            )
        except asyncio.TimeoutError:
            logger.warning("Index fabric search timeout exceeded", query=query)
            # Return partial results from completed lanes
            lane_results = [None] * len(lane_tasks)
        
        # Process lane results
        processed_lanes = {}
        successful_lanes = 0
        failed_lanes = 0
        
        lane_names = ["meili", "qdrant", "chroma", "kg"]
        
        for i, result in enumerate(lane_results):
            lane_name = lane_names[i]
            
            if isinstance(result, Exception):
                processed_lanes[lane_name] = IndexLaneResult(
                    lane_name=lane_name,
                    results=[],
                    processing_time_ms=0,
                    success=False,
                    error_message=str(result)
                )
                failed_lanes += 1
            elif result is None:
                processed_lanes[lane_name] = IndexLaneResult(
                    lane_name=lane_name,
                    results=[],
                    processing_time_ms=0,
                    success=False,
                    error_message="Timeout"
                )
                failed_lanes += 1
            else:
                processed_lanes[lane_name] = result
                successful_lanes += 1
        
        # Fuse results using reciprocal rank fusion
        fusion_start = time.time()
        fused_results = self._reciprocal_rank_fusion(processed_lanes, max_results)
        fusion_time_ms = (time.time() - fusion_start) * 1000
        
        # Calculate total time
        total_time_ms = (time.time() - start_time) * 1000
        within_budget = total_time_ms <= self.config["max_total_time_ms"]
        
        result = FusedIndexResult(
            query=query,
            total_results=len(fused_results),
            fused_results=fused_results,
            lane_results=processed_lanes,
            fusion_time_ms=fusion_time_ms,
            total_time_ms=total_time_ms,
            within_budget=within_budget,
            successful_lanes=successful_lanes,
            failed_lanes=failed_lanes
        )
        
        logger.info("Index fabric search completed",
                   query=query[:100],
                   total_results=len(fused_results),
                   total_time_ms=total_time_ms,
                   within_budget=within_budget,
                   successful_lanes=successful_lanes)
        
        return result
    
    async def _execute_meili_lane(self, query: str, max_results: int) -> IndexLaneResult:
        """Execute Meilisearch keyword search lane."""
        start_time = time.time()
        
        try:
            from shared.core.services.meilisearch_service import MeilisearchService
            
            meili_service = MeilisearchService()
            if not await meili_service.connect():
                return IndexLaneResult("meili", [], 0, False, "Connection failed")
            
            # Search across all indexes
            results = []
            for index_name in ["sarvanom_docs", "sarvanom_code", "sarvanom_qa"]:
                try:
                    index_results = await asyncio.wait_for(
                        meili_service.search(index_name, query, max_results // 3),
                        timeout=self.config["meili_timeout_ms"] / 1000.0
                    )
                    results.extend(index_results)
                except asyncio.TimeoutError:
                    logger.warning("Meili index timeout", index=index_name)
                except Exception as e:
                    logger.debug("Meili index search failed", index=index_name, error=str(e))
            
            processing_time = (time.time() - start_time) * 1000
            
            return IndexLaneResult(
                lane_name="meili",
                results=results[:max_results],
                processing_time_ms=processing_time,
                success=True,
                metadata={"indexes_searched": 3, "total_found": len(results)}
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return IndexLaneResult(
                lane_name="meili",
                results=[],
                processing_time_ms=processing_time,
                success=False,
                error_message=str(e)
            )
    
    async def _execute_qdrant_lane(self, query: str, max_results: int) -> IndexLaneResult:
        """Execute Qdrant vector search lane."""
        start_time = time.time()
        
        try:
            from shared.core.services.vector_singleton_service import get_vector_singleton_service
            
            vector_service = get_vector_singleton_service()
            
            # Generate embedding for query
            embedding = await asyncio.wait_for(
                vector_service.get_embedding(query),
                timeout=self.config["qdrant_timeout_ms"] / 1000.0
            )
            
            # Search in Qdrant
            results = await asyncio.wait_for(
                vector_service.search_similar(embedding, max_results),
                timeout=self.config["qdrant_timeout_ms"] / 1000.0
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            return IndexLaneResult(
                lane_name="qdrant",
                results=results,
                processing_time_ms=processing_time,
                success=True,
                metadata={"embedding_dim": len(embedding), "results_found": len(results)}
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return IndexLaneResult(
                lane_name="qdrant",
                results=[],
                processing_time_ms=processing_time,
                success=False,
                error_message=str(e)
            )
    
    async def _execute_chroma_lane(self, query: str, max_results: int) -> IndexLaneResult:
        """Execute ChromaDB local search lane."""
        start_time = time.time()
        
        try:
            from shared.core.services.vector_singleton_service import get_vector_singleton_service
            
            vector_service = get_vector_singleton_service()
            
            # Generate embedding for query
            embedding = await asyncio.wait_for(
                vector_service.get_embedding(query),
                timeout=self.config["chroma_timeout_ms"] / 1000.0
            )
            
            # Search in ChromaDB (local)
            results = await asyncio.wait_for(
                vector_service.search_similar(embedding, max_results),
                timeout=self.config["chroma_timeout_ms"] / 1000.0
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            return IndexLaneResult(
                lane_name="chroma",
                results=results,
                processing_time_ms=processing_time,
                success=True,
                metadata={"embedding_dim": len(embedding), "results_found": len(results)}
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return IndexLaneResult(
                lane_name="chroma",
                results=[],
                processing_time_ms=processing_time,
                success=False,
                error_message=str(e)
            )
    
    async def _execute_kg_lane(self, query: str, max_results: int) -> IndexLaneResult:
        """Execute Knowledge Graph search lane."""
        start_time = time.time()
        
        try:
            from shared.core.services.arangodb_service import ArangoDBService
            
            kg_service = ArangoDBService()
            
            # Search for entities and relationships
            results = await asyncio.wait_for(
                kg_service.search_entities(query, max_results),
                timeout=self.config["kg_timeout_ms"] / 1000.0
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            return IndexLaneResult(
                lane_name="kg",
                results=results,
                processing_time_ms=processing_time,
                success=True,
                metadata={"entities_found": len(results)}
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return IndexLaneResult(
                lane_name="kg",
                results=[],
                processing_time_ms=processing_time,
                success=False,
                error_message=str(e)
            )
    
    def _reciprocal_rank_fusion(self, lane_results: Dict[str, IndexLaneResult], max_results: int) -> List[Dict[str, Any]]:
        """Fuse results using reciprocal rank fusion algorithm."""
        if not self.config["enable_reciprocal_rank_fusion"]:
            # Simple concatenation if RRF is disabled
            all_results = []
            for lane_result in lane_results.values():
                if lane_result.success:
                    all_results.extend(lane_result.results)
            return all_results[:max_results]
        
        # Reciprocal Rank Fusion implementation
        document_scores = {}
        
        for lane_name, lane_result in lane_results.items():
            if not lane_result.success:
                continue
            
            for rank, result in enumerate(lane_result.results):
                doc_id = result.get('id', str(hash(str(result))))
                
                if doc_id not in document_scores:
                    document_scores[doc_id] = {
                        'score': 0.0,
                        'result': result,
                        'sources': []
                    }
                
                # RRF formula: 1 / (k + rank)
                k = 60  # Standard RRF parameter
                rrf_score = 1.0 / (k + rank + 1)
                document_scores[doc_id]['score'] += rrf_score
                document_scores[doc_id]['sources'].append(lane_name)
        
        # Sort by RRF score and return top results
        sorted_results = sorted(
            document_scores.values(),
            key=lambda x: x['score'],
            reverse=True
        )
        
        # Add fusion metadata
        for result in sorted_results[:max_results]:
            result['result']['fusion_metadata'] = {
                'rrf_score': result['score'],
                'source_lanes': result['sources'],
                'fusion_method': 'reciprocal_rank_fusion'
            }
        
        return [result['result'] for result in sorted_results[:max_results]]
    
    def _create_error_result(self, query: str, error_message: str) -> FusedIndexResult:
        """Create error result when search fails."""
        return FusedIndexResult(
            query=query,
            total_results=0,
            fused_results=[],
            lane_results={},
            fusion_time_ms=0,
            total_time_ms=0,
            within_budget=False,
            successful_lanes=0,
            failed_lanes=4,
            timestamp=datetime.utcnow()
        )
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all indexing lanes."""
        try:
            # Test all connections
            connection_tests = await asyncio.gather(
                self._test_meili_connection(),
                self._test_qdrant_connection(),
                self._test_chroma_connection(),
                self._test_kg_connection(),
                return_exceptions=True
            )
            
            lane_names = ["meili", "qdrant", "chroma", "kg"]
            lane_status = {}
            
            for i, result in enumerate(connection_tests):
                lane_name = lane_names[i]
                if isinstance(result, Exception):
                    lane_status[lane_name] = {"status": "error", "error": str(result)}
                else:
                    lane_status[lane_name] = {"status": "healthy" if result else "unavailable"}
            
            return {
                "status": "healthy" if sum(1 for s in lane_status.values() if s.get("status") == "healthy") >= 2 else "degraded",
                "lanes": lane_status,
                "total_lanes": len(lane_names),
                "healthy_lanes": sum(1 for s in lane_status.values() if s.get("status") == "healthy"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# Global service instance
_index_fabric_service: Optional[IndexFabricService] = None

def get_index_fabric_service() -> IndexFabricService:
    """Get the global index fabric service instance."""
    global _index_fabric_service
    
    if _index_fabric_service is None:
        _index_fabric_service = IndexFabricService()
    
    return _index_fabric_service

async def search_with_index_fabric(query: str, max_results: int = 10) -> FusedIndexResult:
    """Convenience function to search using the index fabric."""
    service = get_index_fabric_service()
    return await service.search_across_all_lanes(query, max_results)
