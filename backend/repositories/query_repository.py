"""
Query Repository Implementation

This module contains the repository implementation for Query domain entities.
Handles persistence, retrieval, and management of query data.
"""

import logging
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta

from .base_repository import BaseRepository, InMemoryRepository
from ..models.domain.query import Query, QueryStatus, QueryType
from ..models.domain.enums import ServiceStatus

logger = logging.getLogger(__name__)


class QueryRepository(ABC):
    """Abstract interface for Query repository operations."""
    
    @abstractmethod
    async def create_query(self, query: Query) -> Query:
        """Create a new query."""
        pass
    
    @abstractmethod
    async def get_query_by_id(self, query_id: str) -> Optional[Query]:
        """Get a query by its ID."""
        pass
    
    @abstractmethod
    async def update_query_status(self, query_id: str, status: QueryStatus, result: Optional[Dict[str, Any]] = None) -> Optional[Query]:
        """Update query status and optionally store result."""
        pass
    
    @abstractmethod
    async def get_queries_by_user(self, user_id: str, limit: int = 50) -> List[Query]:
        """Get queries for a specific user."""
        pass
    
    @abstractmethod
    async def get_queries_by_session(self, session_id: str) -> List[Query]:
        """Get queries for a specific session."""
        pass
    
    @abstractmethod
    async def search_queries(self, search_term: str, filters: Optional[Dict[str, Any]] = None) -> List[Query]:
        """Search queries by text content."""
        pass
    
    @abstractmethod
    async def get_recent_queries(self, hours: int = 24, limit: int = 100) -> List[Query]:
        """Get recent queries within specified time period."""
        pass
    
    @abstractmethod
    async def get_query_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get query statistics."""
        pass
    
    @abstractmethod
    async def delete_old_queries(self, days: int = 30) -> int:
        """Delete old queries beyond specified days."""
        pass


class QueryRepositoryImpl(QueryRepository, BaseRepository[Query]):
    """
    Implementation of Query repository using the base repository.
    
    This implementation can be extended to use different storage backends
    like PostgreSQL, MongoDB, etc.
    """
    
    def __init__(self, connection_string: Optional[str] = None, storage_type: str = "memory"):
        """Initialize the query repository."""
        super().__init__(connection_string)
        self.storage_type = storage_type
        
        # For now, use in-memory storage
        # TODO: Implement database-backed storage
        if storage_type == "memory":
            self._memory_store = InMemoryRepository[Query]()
        
        # Query-specific indices for faster lookups
        self._user_index: Dict[str, List[str]] = {}  # user_id -> [query_ids]
        self._session_index: Dict[str, List[str]] = {}  # session_id -> [query_ids]
        self._status_index: Dict[QueryStatus, List[str]] = {}  # status -> [query_ids]
        self._date_index: Dict[str, List[str]] = {}  # date -> [query_ids]
        
        logger.info(f"Query repository initialized with {storage_type} storage")
    
    async def create(self, entity: Query) -> Query:
        """Create a new query (BaseRepository interface)."""
        return await self.create_query(entity)
    
    async def get_by_id(self, entity_id: str) -> Optional[Query]:
        """Get query by ID (BaseRepository interface)."""
        return await self.get_query_by_id(entity_id)
    
    async def update(self, entity_id: str, updates: Dict[str, Any]) -> Optional[Query]:
        """Update query (BaseRepository interface)."""
        # Convert generic updates to query-specific updates
        status = updates.get('status')
        result = updates.get('result')
        
        if status:
            if isinstance(status, str):
                status = QueryStatus(status)
            return await self.update_query_status(entity_id, status, result)
        
        # For other updates, use the memory store directly
        if self.storage_type == "memory":
            return await self._memory_store.update(entity_id, updates)
        
        return None
    
    async def delete(self, entity_id: str) -> bool:
        """Delete query (BaseRepository interface)."""
        if self.storage_type == "memory":
            # Also remove from indices
            query = await self.get_query_by_id(entity_id)
            if query:
                await self._remove_from_indices(query)
            return await self._memory_store.delete(entity_id)
        return False
    
    async def list(self, filters: Optional[Dict[str, Any]] = None, offset: int = 0, limit: int = 100) -> List[Query]:
        """List queries (BaseRepository interface)."""
        if self.storage_type == "memory":
            return await self._memory_store.list(filters, offset, limit)
        return []
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count queries (BaseRepository interface)."""
        if self.storage_type == "memory":
            return await self._memory_store.count(filters)
        return 0
    
    async def exists(self, entity_id: str) -> bool:
        """Check if query exists (BaseRepository interface)."""
        if self.storage_type == "memory":
            return await self._memory_store.exists(entity_id)
        return False
    
    # Query-specific methods
    
    async def create_query(self, query: Query) -> Query:
        """Create a new query with indexing."""
        try:
            # Store the query
            if self.storage_type == "memory":
                created_query = await self._memory_store.create(query)
            else:
                # TODO: Implement database storage
                created_query = query
            
            # Update indices
            await self._add_to_indices(created_query)
            
            self._track_operation("create_query", success=True)
            logger.info(f"Created query {created_query.id} for user {created_query.context.user_id}")
            
            return created_query
            
        except Exception as e:
            self._track_operation("create_query", success=False)
            logger.error(f"Failed to create query: {e}")
            raise
    
    async def get_query_by_id(self, query_id: str) -> Optional[Query]:
        """Get a query by its ID."""
        try:
            if self.storage_type == "memory":
                query = await self._memory_store.get_by_id(query_id)
            else:
                # TODO: Implement database retrieval
                query = None
            
            self._track_operation("get_query_by_id", success=True)
            return query
            
        except Exception as e:
            self._track_operation("get_query_by_id", success=False)
            logger.error(f"Failed to get query {query_id}: {e}")
            raise
    
    async def update_query_status(self, query_id: str, status: QueryStatus, result: Optional[Dict[str, Any]] = None) -> Optional[Query]:
        """Update query status and result."""
        try:
            query = await self.get_query_by_id(query_id)
            if not query:
                return None
            
            # Update status
            old_status = query.status
            if status == QueryStatus.PROCESSING:
                query.mark_processing()
            elif status == QueryStatus.COMPLETED:
                query.mark_completed()
                if result:
                    query.result = result
            elif status == QueryStatus.FAILED:
                error_message = result.get('error', 'Unknown error') if result else 'Unknown error'
                query.mark_failed(error_message)
            
            # Update in storage
            if self.storage_type == "memory":
                await self._memory_store.update(query_id, {
                    'status': status,
                    'result': result,
                    'updated_at': query.updated_at
                })
            
            # Update status index
            if old_status != status:
                if old_status in self._status_index:
                    if query_id in self._status_index[old_status]:
                        self._status_index[old_status].remove(query_id)
                
                if status not in self._status_index:
                    self._status_index[status] = []
                self._status_index[status].append(query_id)
            
            self._track_operation("update_query_status", success=True)
            logger.info(f"Updated query {query_id} status from {old_status} to {status}")
            
            return query
            
        except Exception as e:
            self._track_operation("update_query_status", success=False)
            logger.error(f"Failed to update query status for {query_id}: {e}")
            raise
    
    async def get_queries_by_user(self, user_id: str, limit: int = 50) -> List[Query]:
        """Get queries for a specific user."""
        try:
            query_ids = self._user_index.get(user_id, [])
            queries = []
            
            for query_id in query_ids[-limit:]:  # Get most recent
                query = await self.get_query_by_id(query_id)
                if query:
                    queries.append(query)
            
            # Sort by creation time (most recent first)
            queries.sort(key=lambda q: q.created_at, reverse=True)
            
            self._track_operation("get_queries_by_user", success=True)
            return queries
            
        except Exception as e:
            self._track_operation("get_queries_by_user", success=False)
            logger.error(f"Failed to get queries for user {user_id}: {e}")
            raise
    
    async def get_queries_by_session(self, session_id: str) -> List[Query]:
        """Get queries for a specific session."""
        try:
            query_ids = self._session_index.get(session_id, [])
            queries = []
            
            for query_id in query_ids:
                query = await self.get_query_by_id(query_id)
                if query:
                    queries.append(query)
            
            # Sort by creation time
            queries.sort(key=lambda q: q.created_at)
            
            self._track_operation("get_queries_by_session", success=True)
            return queries
            
        except Exception as e:
            self._track_operation("get_queries_by_session", success=False)
            logger.error(f"Failed to get queries for session {session_id}: {e}")
            raise
    
    async def search_queries(self, search_term: str, filters: Optional[Dict[str, Any]] = None) -> List[Query]:
        """Search queries by text content."""
        try:
            if self.storage_type == "memory":
                all_queries = await self._memory_store.list()
            else:
                # TODO: Implement database search
                all_queries = []
            
            # Simple text search in query text and result
            matching_queries = []
            search_lower = search_term.lower()
            
            for query in all_queries:
                # Check query text
                if search_lower in query.text.lower():
                    matching_queries.append(query)
                    continue
                
                # Check result content if available
                if query.result:
                    result_text = str(query.result).lower()
                    if search_lower in result_text:
                        matching_queries.append(query)
            
            # Apply additional filters
            if filters:
                filtered_queries = []
                for query in matching_queries:
                    match = True
                    for key, value in filters.items():
                        if key == 'user_id' and query.context.user_id != value:
                            match = False
                            break
                        elif key == 'status' and query.status != value:
                            match = False
                            break
                        elif key == 'query_type' and query.query_type != value:
                            match = False
                            break
                    
                    if match:
                        filtered_queries.append(query)
                
                matching_queries = filtered_queries
            
            self._track_operation("search_queries", success=True)
            return matching_queries
            
        except Exception as e:
            self._track_operation("search_queries", success=False)
            logger.error(f"Failed to search queries with term '{search_term}': {e}")
            raise
    
    async def get_recent_queries(self, hours: int = 24, limit: int = 100) -> List[Query]:
        """Get recent queries within specified time period."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            if self.storage_type == "memory":
                all_queries = await self._memory_store.list()
            else:
                # TODO: Implement database query with time filter
                all_queries = []
            
            # Filter by time
            recent_queries = [
                query for query in all_queries 
                if query.created_at >= cutoff_time
            ]
            
            # Sort by creation time (most recent first)
            recent_queries.sort(key=lambda q: q.created_at, reverse=True)
            
            # Apply limit
            result = recent_queries[:limit]
            
            self._track_operation("get_recent_queries", success=True)
            return result
            
        except Exception as e:
            self._track_operation("get_recent_queries", success=False)
            logger.error(f"Failed to get recent queries: {e}")
            raise
    
    async def get_query_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get query statistics."""
        try:
            if user_id:
                queries = await self.get_queries_by_user(user_id, limit=1000)
            else:
                if self.storage_type == "memory":
                    queries = await self._memory_store.list()
                else:
                    queries = []
            
            # Calculate statistics
            total_queries = len(queries)
            
            if total_queries == 0:
                return {
                    "total_queries": 0,
                    "status_breakdown": {},
                    "type_breakdown": {},
                    "average_processing_time": 0,
                    "success_rate": 0,
                    "queries_today": 0,
                    "queries_this_week": 0
                }
            
            # Status breakdown
            status_breakdown = {}
            for query in queries:
                status = query.status.value
                status_breakdown[status] = status_breakdown.get(status, 0) + 1
            
            # Type breakdown
            type_breakdown = {}
            for query in queries:
                query_type = query.query_type.value
                type_breakdown[query_type] = type_breakdown.get(query_type, 0) + 1
            
            # Processing time statistics
            completed_queries = [q for q in queries if q.status == QueryStatus.COMPLETED and hasattr(q, 'processing_time')]
            avg_processing_time = 0
            if completed_queries:
                total_time = sum(getattr(q, 'processing_time', 0) for q in completed_queries)
                avg_processing_time = total_time / len(completed_queries)
            
            # Success rate
            completed_count = status_breakdown.get(QueryStatus.COMPLETED.value, 0)
            success_rate = completed_count / total_queries if total_queries > 0 else 0
            
            # Time-based counts
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=now.weekday())
            
            queries_today = len([q for q in queries if q.created_at >= today_start])
            queries_this_week = len([q for q in queries if q.created_at >= week_start])
            
            self._track_operation("get_query_statistics", success=True)
            
            return {
                "total_queries": total_queries,
                "status_breakdown": status_breakdown,
                "type_breakdown": type_breakdown,
                "average_processing_time": avg_processing_time,
                "success_rate": success_rate,
                "queries_today": queries_today,
                "queries_this_week": queries_this_week,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self._track_operation("get_query_statistics", success=False)
            logger.error(f"Failed to get query statistics: {e}")
            raise
    
    async def delete_old_queries(self, days: int = 30) -> int:
        """Delete old queries beyond specified days."""
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            
            if self.storage_type == "memory":
                all_queries = await self._memory_store.list()
            else:
                # TODO: Implement database query
                all_queries = []
            
            # Find old queries
            old_queries = [
                query for query in all_queries 
                if query.created_at < cutoff_time
            ]
            
            # Delete old queries
            deleted_count = 0
            for query in old_queries:
                success = await self.delete(query.id)
                if success:
                    deleted_count += 1
            
            self._track_operation("delete_old_queries", success=True)
            logger.info(f"Deleted {deleted_count} old queries (older than {days} days)")
            
            return deleted_count
            
        except Exception as e:
            self._track_operation("delete_old_queries", success=False)
            logger.error(f"Failed to delete old queries: {e}")
            raise
    
    async def _add_to_indices(self, query: Query):
        """Add query to various indices for faster lookups."""
        query_id = query.id
        
        # User index
        user_id = query.context.user_id
        if user_id not in self._user_index:
            self._user_index[user_id] = []
        self._user_index[user_id].append(query_id)
        
        # Session index
        session_id = query.context.session_id
        if session_id not in self._session_index:
            self._session_index[session_id] = []
        self._session_index[session_id].append(query_id)
        
        # Status index
        status = query.status
        if status not in self._status_index:
            self._status_index[status] = []
        self._status_index[status].append(query_id)
        
        # Date index
        date_key = query.created_at.strftime('%Y-%m-%d')
        if date_key not in self._date_index:
            self._date_index[date_key] = []
        self._date_index[date_key].append(query_id)
    
    async def _remove_from_indices(self, query: Query):
        """Remove query from all indices."""
        query_id = query.id
        
        # Remove from user index
        user_id = query.context.user_id
        if user_id in self._user_index and query_id in self._user_index[user_id]:
            self._user_index[user_id].remove(query_id)
        
        # Remove from session index
        session_id = query.context.session_id
        if session_id in self._session_index and query_id in self._session_index[session_id]:
            self._session_index[session_id].remove(query_id)
        
        # Remove from status index
        status = query.status
        if status in self._status_index and query_id in self._status_index[status]:
            self._status_index[status].remove(query_id)
        
        # Remove from date index
        date_key = query.created_at.strftime('%Y-%m-%d')
        if date_key in self._date_index and query_id in self._date_index[date_key]:
            self._date_index[date_key].remove(query_id)
