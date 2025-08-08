"""
Query Orchestrator Service

This module contains the main orchestration logic for query processing.
It coordinates between different services and manages the query pipeline.
"""

import asyncio
import time
import uuid
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ...models.domain.query import Query, QueryContext, QueryResult, QueryStatus, QueryType
from ...models.requests.query_requests import QueryRequest, ComprehensiveQueryRequest
from ...models.responses.query_responses import QueryResponse, ComprehensiveQueryResponse
from .query_processor import QueryProcessor
from .query_validator import QueryValidator
from ..core.cache_service import CacheService
from ..core.metrics_service import MetricsService

logger = logging.getLogger(__name__)


class QueryOrchestrator:
    """Orchestrates query processing and coordinates between services."""
    
    def __init__(
        self,
        query_processor: QueryProcessor,
        query_validator: QueryValidator,
        cache_service: CacheService,
        metrics_service: MetricsService
    ):
        self.query_processor = query_processor
        self.query_validator = query_validator
        self.cache_service = cache_service
        self.metrics_service = metrics_service
        self.active_queries: Dict[str, Query] = {}
    
    async def process_basic_query(
        self, 
        request: QueryRequest,
        user_context: Dict[str, Any]
    ) -> QueryResponse:
        """Process a basic query with caching and validation."""
        start_time = time.time()
        query_id = str(uuid.uuid4())
        
        try:
            # Create query domain model
            query_context = QueryContext(
                user_id=user_context.get("user_id", "anonymous"),
                session_id=request.session_id or str(uuid.uuid4()),
                max_tokens=request.max_tokens,
                confidence_threshold=request.confidence_threshold,
                metadata=user_context
            )
            
            query = Query(
                id=query_id,
                text=request.query,
                context=query_context,
                query_type=QueryType.BASIC
            )
            
            # Validate query
            await self.query_validator.validate_query(query)
            
            # Check cache first
            if request.cache_enabled:
                cached_result = await self._get_cached_result(query)
                if cached_result:
                    logger.info(f"Cache hit for query {query_id}")
                    return self._create_basic_response(query, cached_result, cache_hit=True)
            
            # Process query
            self.active_queries[query_id] = query
            query.mark_processing()
            
            result = await self.query_processor.process_basic_query(query)
            
            # Cache result
            if request.cache_enabled:
                await self._cache_result(query, result)
            
            # Track metrics
            processing_time = time.time() - start_time
            await self.metrics_service.track_query_processing(
                query_id=query_id,
                query_type="basic",
                processing_time=processing_time,
                cache_hit=False
            )
            
            return self._create_basic_response(query, result, cache_hit=False)
            
        except Exception as e:
            logger.error(f"Error processing basic query {query_id}: {e}", exc_info=True)
            if query_id in self.active_queries:
                self.active_queries[query_id].mark_failed(str(e))
            
            # Track error metrics
            processing_time = time.time() - start_time
            await self.metrics_service.track_query_error(
                query_id=query_id,
                error_type=type(e).__name__,
                processing_time=processing_time
            )
            
            raise
    
    async def process_comprehensive_query(
        self,
        request: ComprehensiveQueryRequest,
        user_context: Dict[str, Any]
    ) -> ComprehensiveQueryResponse:
        """Process a comprehensive query with full pipeline."""
        start_time = time.time()
        query_id = str(uuid.uuid4())
        
        try:
            # Create query domain model
            query_context = QueryContext(
                user_id=user_context.get("user_id", "anonymous"),
                session_id=request.session_id or str(uuid.uuid4()),
                max_tokens=request.max_tokens,
                confidence_threshold=request.confidence_threshold,
                metadata=user_context
            )
            
            query = Query(
                id=query_id,
                text=request.query,
                context=query_context,
                query_type=QueryType.COMPREHENSIVE
            )
            
            # Validate query
            await self.query_validator.validate_query(query)
            
            # Check cache first
            cached_result = await self._get_cached_result(query)
            if cached_result:
                logger.info(f"Cache hit for comprehensive query {query_id}")
                return self._create_comprehensive_response(query, cached_result, cache_hit=True)
            
            # Process query
            self.active_queries[query_id] = query
            query.mark_processing()
            
            result = await self.query_processor.process_comprehensive_query(query, request.options)
            
            # Cache result
            await self._cache_result(query, result)
            
            # Track metrics
            processing_time = time.time() - start_time
            await self.metrics_service.track_query_processing(
                query_id=query_id,
                query_type="comprehensive",
                processing_time=processing_time,
                cache_hit=False
            )
            
            return self._create_comprehensive_response(query, result, cache_hit=False)
            
        except Exception as e:
            logger.error(f"Error processing comprehensive query {query_id}: {e}", exc_info=True)
            if query_id in self.active_queries:
                self.active_queries[query_id].mark_failed(str(e))
            
            # Track error metrics
            processing_time = time.time() - start_time
            await self.metrics_service.track_query_error(
                query_id=query_id,
                error_type=type(e).__name__,
                processing_time=processing_time
            )
            
            raise
    
    async def get_query_status(self, query_id: str) -> Dict[str, Any]:
        """Get the status of a query."""
        if query_id in self.active_queries:
            query = self.active_queries[query_id]
            return {
                "query_id": query_id,
                "status": query.status.value,
                "created_at": query.created_at,
                "updated_at": query.updated_at
            }
        
        # Check if query exists in storage
        stored_query = await self._get_stored_query(query_id)
        if stored_query:
            return {
                "query_id": query_id,
                "status": stored_query.status.value,
                "created_at": stored_query.created_at,
                "updated_at": stored_query.updated_at
            }
        
        raise ValueError(f"Query {query_id} not found")
    
    async def _get_cached_result(self, query: Query) -> Optional[Dict[str, Any]]:
        """Get cached result for query."""
        cache_key = self._generate_cache_key(query)
        return await self.cache_service.get(cache_key)
    
    async def _cache_result(self, query: Query, result: Dict[str, Any]):
        """Cache query result."""
        cache_key = self._generate_cache_key(query)
        await self.cache_service.set(cache_key, result, ttl=3600)  # 1 hour TTL
    
    def _generate_cache_key(self, query: Query) -> str:
        """Generate cache key for query."""
        return f"query:{query.text}:{query.context.user_id}:{query.query_type.value}"
    
    def _create_basic_response(self, query: Query, result: Dict[str, Any], cache_hit: bool) -> QueryResponse:
        """Create basic query response."""
        return QueryResponse(
            query_id=query.id,
            answer=result.get("answer", ""),
            confidence=result.get("confidence", 0.0),
            processing_time=result.get("processing_time", 0.0),
            cache_hit=cache_hit,
            created_at=query.created_at,
            metadata=result.get("metadata", {})
        )
    
    def _create_comprehensive_response(self, query: Query, result: Dict[str, Any], cache_hit: bool) -> ComprehensiveQueryResponse:
        """Create comprehensive query response."""
        return ComprehensiveQueryResponse(
            query_id=query.id,
            answer=result.get("answer", ""),
            confidence=result.get("confidence", 0.0),
            processing_time=result.get("processing_time", 0.0),
            cache_hit=cache_hit,
            sources=result.get("sources", []),
            alternatives=result.get("alternatives", []),
            quality_metrics=result.get("quality_metrics", {}),
            created_at=query.created_at,
            metadata=result.get("metadata", {})
        )
    
    async def _get_stored_query(self, query_id: str) -> Optional[Query]:
        """Get stored query from repository (to be implemented)."""
        # TODO: Implement query repository
        return None 