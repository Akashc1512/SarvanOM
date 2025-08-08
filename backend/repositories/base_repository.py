"""
Base Repository Interface

This module defines the base repository interface and common functionality
for all repository implementations following the Repository pattern.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Generic, TypeVar, Union
from datetime import datetime
import asyncio

from ..models.domain.enums import ServiceStatus

logger = logging.getLogger(__name__)

# Generic type for entity models
T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Base repository interface defining common operations for all repositories.
    
    This abstract base class provides the interface that all repositories
    must implement, ensuring consistency across different data persistence layers.
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        """Initialize the repository with optional connection parameters."""
        self.connection_string = connection_string
        self.status = ServiceStatus.HEALTHY
        self.connection_pool = None
        self.metrics = {
            "operations_count": 0,
            "error_count": 0,
            "last_operation": None
        }
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity in the repository."""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """Retrieve an entity by its ID."""
        pass
    
    @abstractmethod
    async def update(self, entity_id: str, updates: Dict[str, Any]) -> Optional[T]:
        """Update an entity with the given updates."""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete an entity by its ID."""
        pass
    
    @abstractmethod
    async def list(
        self, 
        filters: Optional[Dict[str, Any]] = None, 
        offset: int = 0, 
        limit: int = 100
    ) -> List[T]:
        """List entities with optional filtering and pagination."""
        pass
    
    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities matching the given filters."""
        pass
    
    @abstractmethod
    async def exists(self, entity_id: str) -> bool:
        """Check if an entity exists by its ID."""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the repository."""
        try:
            # Basic connectivity check
            await self._check_connection()
            
            return {
                "status": "healthy",
                "metrics": self.metrics,
                "connection_status": "connected",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Repository health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "metrics": self.metrics,
                "connection_status": "disconnected",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_connection(self):
        """Check if the repository connection is healthy."""
        # Default implementation - to be overridden by specific repositories
        pass
    
    def _track_operation(self, operation: str, success: bool = True):
        """Track repository operation metrics."""
        self.metrics["operations_count"] += 1
        self.metrics["last_operation"] = {
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "success": success
        }
        
        if not success:
            self.metrics["error_count"] += 1
    
    async def batch_create(self, entities: List[T]) -> List[T]:
        """Create multiple entities in batch."""
        results = []
        for entity in entities:
            try:
                result = await self.create(entity)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to create entity in batch: {e}")
                continue
        return results
    
    async def batch_update(self, updates: List[Dict[str, Any]]) -> List[Optional[T]]:
        """Update multiple entities in batch."""
        results = []
        for update_data in updates:
            entity_id = update_data.pop("id", None)
            if not entity_id:
                results.append(None)
                continue
                
            try:
                result = await self.update(entity_id, update_data)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to update entity {entity_id} in batch: {e}")
                results.append(None)
        return results
    
    async def batch_delete(self, entity_ids: List[str]) -> List[bool]:
        """Delete multiple entities in batch."""
        results = []
        for entity_id in entity_ids:
            try:
                result = await self.delete(entity_id)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to delete entity {entity_id} in batch: {e}")
                results.append(False)
        return results
    
    async def search(
        self,
        query: str,
        fields: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[T]:
        """Search entities by text query."""
        # Default implementation using list with text filtering
        # Should be overridden by repositories that support full-text search
        all_entities = await self.list(filters, offset, limit)
        
        if not query:
            return all_entities
        
        # Simple text matching - should be improved in specific implementations
        filtered_entities = []
        for entity in all_entities:
            entity_dict = entity.__dict__ if hasattr(entity, '__dict__') else {}
            entity_str = str(entity_dict).lower()
            if query.lower() in entity_str:
                filtered_entities.append(entity)
        
        return filtered_entities
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics."""
        try:
            total_count = await self.count()
            return {
                "total_entities": total_count,
                "operations_performed": self.metrics["operations_count"],
                "error_rate": (
                    self.metrics["error_count"] / max(self.metrics["operations_count"], 1)
                ),
                "last_operation": self.metrics["last_operation"],
                "status": self.status.value,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get repository statistics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


class InMemoryRepository(BaseRepository[T]):
    """
    In-memory implementation of the repository pattern.
    
    Useful for testing and development. Data is stored in memory
    and will be lost when the application shuts down.
    """
    
    def __init__(self):
        super().__init__()
        self._data: Dict[str, T] = {}
        self._id_counter = 0
    
    async def create(self, entity: T) -> T:
        """Create a new entity in memory."""
        try:
            # Generate ID if not present
            if hasattr(entity, 'id') and not getattr(entity, 'id'):
                self._id_counter += 1
                setattr(entity, 'id', str(self._id_counter))
            
            entity_id = getattr(entity, 'id', str(self._id_counter))
            self._data[entity_id] = entity
            
            self._track_operation("create", success=True)
            return entity
            
        except Exception as e:
            self._track_operation("create", success=False)
            raise e
    
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """Retrieve an entity by its ID from memory."""
        try:
            result = self._data.get(entity_id)
            self._track_operation("get_by_id", success=True)
            return result
        except Exception as e:
            self._track_operation("get_by_id", success=False)
            raise e
    
    async def update(self, entity_id: str, updates: Dict[str, Any]) -> Optional[T]:
        """Update an entity in memory."""
        try:
            if entity_id not in self._data:
                return None
            
            entity = self._data[entity_id]
            
            # Update entity attributes
            for key, value in updates.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            
            # Update timestamp if available
            if hasattr(entity, 'updated_at'):
                setattr(entity, 'updated_at', datetime.now())
            
            self._track_operation("update", success=True)
            return entity
            
        except Exception as e:
            self._track_operation("update", success=False)
            raise e
    
    async def delete(self, entity_id: str) -> bool:
        """Delete an entity from memory."""
        try:
            if entity_id in self._data:
                del self._data[entity_id]
                self._track_operation("delete", success=True)
                return True
            
            self._track_operation("delete", success=True)
            return False
            
        except Exception as e:
            self._track_operation("delete", success=False)
            raise e
    
    async def list(
        self, 
        filters: Optional[Dict[str, Any]] = None, 
        offset: int = 0, 
        limit: int = 100
    ) -> List[T]:
        """List entities from memory with filtering and pagination."""
        try:
            entities = list(self._data.values())
            
            # Apply filters
            if filters:
                filtered_entities = []
                for entity in entities:
                    match = True
                    for key, value in filters.items():
                        if not hasattr(entity, key) or getattr(entity, key) != value:
                            match = False
                            break
                    if match:
                        filtered_entities.append(entity)
                entities = filtered_entities
            
            # Apply pagination
            end_index = offset + limit
            result = entities[offset:end_index]
            
            self._track_operation("list", success=True)
            return result
            
        except Exception as e:
            self._track_operation("list", success=False)
            raise e
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities in memory."""
        try:
            if not filters:
                result = len(self._data)
            else:
                entities = await self.list(filters)
                result = len(entities)
            
            self._track_operation("count", success=True)
            return result
            
        except Exception as e:
            self._track_operation("count", success=False)
            raise e
    
    async def exists(self, entity_id: str) -> bool:
        """Check if an entity exists in memory."""
        try:
            result = entity_id in self._data
            self._track_operation("exists", success=True)
            return result
        except Exception as e:
            self._track_operation("exists", success=False)
            raise e
    
    async def _check_connection(self):
        """Check connection - always healthy for in-memory."""
        pass
    
    def clear(self):
        """Clear all data (useful for testing)."""
        self._data.clear()
        self._id_counter = 0
