"""
Database Repository Base - Universal Knowledge Platform

This module provides a base repository pattern implementation with:
- Common CRUD operations
- Query building and filtering
- Pagination support
- Transaction management
- Error handling and retry logic
- Performance optimization
- Audit trail integration

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import (
    TypeVar, Generic, Optional, List, Dict, Any, Union, Type,
    AsyncGenerator, Tuple, Callable
)
from enum import Enum

from sqlalchemy import (
    select, update, delete, and_, or_, func, desc, asc,
    text, case, distinct, exists
)
from sqlalchemy.orm import Session, joinedload, selectinload, lazyload
from sqlalchemy.exc import (
    SQLAlchemyError, IntegrityError, OperationalError,
    DisconnectionError, TimeoutError
)
from sqlalchemy.sql import Select, Update, Delete

import structlog

from shared.core.database.connection import get_db_manager
from shared.models.models import Base, RecordStatus

logger = structlog.get_logger(__name__)

# Type variables
T = TypeVar('T', bound=Base)
TEntity = TypeVar('TEntity', bound=Base)


class SortOrder(Enum):
    """Sort order enumeration."""
    ASC = "asc"
    DESC = "desc"


class FilterOperator(Enum):
    """Filter operator enumeration."""
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_EQUAL = "lte"
    LIKE = "like"
    ILIKE = "ilike"
    IN = "in"
    NOT_IN = "nin"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    BETWEEN = "between"


class FilterCondition:
    """Represents a filter condition for queries."""
    
    def __init__(
        self,
        field: str,
        operator: FilterOperator,
        value: Any,
        case_sensitive: bool = True
    ):
        self.field = field
        self.operator = operator
        self.value = value
        self.case_sensitive = case_sensitive

    def to_sqlalchemy(self, model_class: Type[TEntity]) -> Any:
        """Convert filter condition to SQLAlchemy expression."""
        if not hasattr(model_class, self.field):
            raise ValueError(f"Field '{self.field}' not found in model {model_class.__name__}")
        
        column = getattr(model_class, self.field)
        
        if self.operator == FilterOperator.EQUALS:
            return column == self.value
        elif self.operator == FilterOperator.NOT_EQUALS:
            return column != self.value
        elif self.operator == FilterOperator.GREATER_THAN:
            return column > self.value
        elif self.operator == FilterOperator.GREATER_EQUAL:
            return column >= self.value
        elif self.operator == FilterOperator.LESS_THAN:
            return column < self.value
        elif self.operator == FilterOperator.LESS_EQUAL:
            return column <= self.value
        elif self.operator == FilterOperator.LIKE:
            return column.like(f"%{self.value}%")
        elif self.operator == FilterOperator.ILIKE:
            return column.ilike(f"%{self.value}%")
        elif self.operator == FilterOperator.IN:
            return column.in_(self.value if isinstance(self.value, list) else [self.value])
        elif self.operator == FilterOperator.NOT_IN:
            return ~column.in_(self.value if isinstance(self.value, list) else [self.value])
        elif self.operator == FilterOperator.IS_NULL:
            return column.is_(None)
        elif self.operator == FilterOperator.IS_NOT_NULL:
            return column.is_not(None)
        elif self.operator == FilterOperator.BETWEEN:
            if not isinstance(self.value, (list, tuple)) or len(self.value) != 2:
                raise ValueError("BETWEEN operator requires a list or tuple with exactly 2 values")
            return column.between(self.value[0], self.value[1])
        else:
            raise ValueError(f"Unsupported operator: {self.operator}")


class SortCondition:
    """Represents a sort condition for queries."""
    
    def __init__(self, field: str, order: SortOrder = SortOrder.ASC):
        self.field = field
        self.order = order

    def to_sqlalchemy(self, model_class: Type[TEntity]) -> Any:
        """Convert sort condition to SQLAlchemy expression."""
        if not hasattr(model_class, self.field):
            raise ValueError(f"Field '{self.field}' not found in model {model_class.__name__}")
        
        column = getattr(model_class, self.field)
        
        if self.order == SortOrder.ASC:
            return asc(column)
        elif self.order == SortOrder.DESC:
            return desc(column)
        else:
            raise ValueError(f"Unsupported sort order: {self.order}")


class QueryOptions:
    """Query options for filtering, sorting, and pagination."""
    
    def __init__(
        self,
        filters: Optional[List[FilterCondition]] = None,
        sort_conditions: Optional[List[SortCondition]] = None,
        page: int = 1,
        page_size: int = 50,
        include_deleted: bool = False,
        eager_load: Optional[List[str]] = None,
        select_fields: Optional[List[str]] = None
    ):
        self.filters = filters or []
        self.sort_conditions = sort_conditions or []
        self.page = max(1, page)
        self.page_size = max(1, min(page_size, 1000))  # Limit page size
        self.include_deleted = include_deleted
        self.eager_load = eager_load or []
        self.select_fields = select_fields or []


class PaginatedResult:
    """Represents a paginated query result."""
    
    def __init__(
        self,
        items: List[TEntity],
        total_count: int,
        page: int,
        page_size: int,
        total_pages: int
    ):
        self.items = items
        self.total_count = total_count
        self.page = page
        self.page_size = page_size
        self.total_pages = total_pages
        self.has_next = page < total_pages
        self.has_previous = page > 1


class BaseRepository(ABC, Generic[TEntity]):
    """
    Base repository class providing common CRUD operations.
    
    This class implements the repository pattern with:
    - Standard CRUD operations
    - Query building and filtering
    - Pagination support
    - Transaction management
    - Error handling and retry logic
    - Performance optimization
    """

    def __init__(self, model_class: Type[TEntity], db_name: str = "primary"):
        """
        Initialize the repository.
        
        Args:
            model_class: The SQLAlchemy model class
            db_name: Database connection name (primary, read_replica, etc.)
        """
        self.model_class = model_class
        self.db_name = db_name
        self.db_manager = get_db_manager()
        self._retry_attempts = 3
        self._retry_delay = 1.0

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[Session, None]:
        """Get a database session."""
        async with self.db_manager.get_session(self.db_name) as session:
            yield session

    async def _execute_with_retry(
        self, 
        operation: Callable[[Session], Any],
        session: Optional[Session] = None
    ) -> Any:
        """Execute an operation with retry logic."""
        last_exception = None
        
        for attempt in range(self._retry_attempts):
            try:
                if session:
                    return operation(session)
                else:
                    async with self.get_session() as sess:
                        return operation(sess)
                        
            except (OperationalError, DisconnectionError, TimeoutError) as e:
                last_exception = e
                if attempt < self._retry_attempts - 1:
                    await asyncio.sleep(self._retry_delay * (2 ** attempt))
                    logger.warning(f"Database operation failed, retrying... (attempt {attempt + 1})")
                else:
                    logger.error(f"Database operation failed after {self._retry_attempts} attempts")
                    raise
            except SQLAlchemyError as e:
                logger.error(f"Database error: {e}")
                raise
        
        if last_exception:
            raise last_exception

    async def create(self, entity: TEntity) -> TEntity:
        """Create a new entity."""
        async def _create(session: Session) -> TEntity:
            # Set timestamps
            if hasattr(entity, 'created_at') and not entity.created_at:
                entity.created_at = datetime.now(timezone.utc)
            if hasattr(entity, 'updated_at'):
                entity.updated_at = datetime.now(timezone.utc)
            
            # Set status if not set
            if hasattr(entity, 'status') and not entity.status:
                entity.status = RecordStatus.ACTIVE
            
            session.add(entity)
            session.flush()  # Flush to get the ID
            session.refresh(entity)
            return entity

        return await self._execute_with_retry(_create)

    async def get_by_id(self, entity_id: str, include_deleted: bool = False) -> Optional[TEntity]:
        """Get an entity by ID."""
        async def _get_by_id(session: Session) -> Optional[TEntity]:
            query = select(self.model_class).where(self.model_class.id == entity_id)
            
            if not include_deleted and hasattr(self.model_class, 'deleted_at'):
                query = query.where(self.model_class.deleted_at.is_(None))
            
            result = session.execute(query)
            return result.scalar_one_or_none()

        return await self._execute_with_retry(_get_by_id)

    async def get_by_ids(self, entity_ids: List[str], include_deleted: bool = False) -> List[TEntity]:
        """Get multiple entities by IDs."""
        if not entity_ids:
            return []

        async def _get_by_ids(session: Session) -> List[TEntity]:
            query = select(self.model_class).where(self.model_class.id.in_(entity_ids))
            
            if not include_deleted and hasattr(self.model_class, 'deleted_at'):
                query = query.where(self.model_class.deleted_at.is_(None))
            
            result = session.execute(query)
            return result.scalars().all()

        return await self._execute_with_retry(_get_by_ids)

    async def update(self, entity: TEntity) -> TEntity:
        """Update an existing entity."""
        async def _update(session: Session) -> TEntity:
            # Update timestamp
            if hasattr(entity, 'updated_at'):
                entity.updated_at = datetime.now(timezone.utc)
            
            # Increment version for optimistic locking
            if hasattr(entity, 'version'):
                entity.version += 1
            
            session.merge(entity)
            session.flush()
            session.refresh(entity)
            return entity

        return await self._execute_with_retry(_update)

    async def delete(self, entity_id: str, hard_delete: bool = False) -> bool:
        """Delete an entity (soft delete by default)."""
        async def _delete(session: Session) -> bool:
            entity = await self.get_by_id(entity_id, include_deleted=True)
            if not entity:
                return False
            
            if hard_delete:
                session.delete(entity)
            else:
                # Soft delete
                if hasattr(entity, 'deleted_at'):
                    entity.deleted_at = datetime.now(timezone.utc)
                if hasattr(entity, 'status'):
                    entity.status = RecordStatus.DELETED
                if hasattr(entity, 'updated_at'):
                    entity.updated_at = datetime.now(timezone.utc)
            
            session.flush()
            return True

        return await self._execute_with_retry(_delete)

    async def list(
        self,
        options: Optional[QueryOptions] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[TEntity]:
        """List entities with optional filtering and pagination."""
        if options is None:
            options = QueryOptions()
        
        if limit is not None:
            options.page_size = limit
        if offset is not None:
            options.page = (offset // options.page_size) + 1

        async def _list(session: Session) -> List[TEntity]:
            query = self._build_query(options)
            result = session.execute(query)
            return result.scalars().all()

        return await self._execute_with_retry(_list)

    async def paginate(self, options: Optional[QueryOptions] = None) -> PaginatedResult:
        """Get paginated results."""
        if options is None:
            options = QueryOptions()

        async def _paginate(session: Session) -> PaginatedResult:
            # Get total count
            count_query = select(func.count()).select_from(self.model_class)
            count_query = self._apply_filters(count_query, options.filters)
            if not options.include_deleted and hasattr(self.model_class, 'deleted_at'):
                count_query = count_query.where(self.model_class.deleted_at.is_(None))
            
            total_count = session.execute(count_query).scalar()
            
            # Get paginated results
            query = self._build_query(options)
            result = session.execute(query)
            items = result.scalars().all()
            
            total_pages = (total_count + options.page_size - 1) // options.page_size
            
            return PaginatedResult(
                items=items,
                total_count=total_count,
                page=options.page,
                page_size=options.page_size,
                total_pages=total_pages
            )

        return await self._execute_with_retry(_paginate)

    async def count(self, filters: Optional[List[FilterCondition]] = None, include_deleted: bool = False) -> int:
        """Count entities with optional filtering."""
        async def _count(session: Session) -> int:
            query = select(func.count()).select_from(self.model_class)
            query = self._apply_filters(query, filters or [])
            
            if not include_deleted and hasattr(self.model_class, 'deleted_at'):
                query = query.where(self.model_class.deleted_at.is_(None))
            
            result = session.execute(query)
            return result.scalar()

        return await self._execute_with_retry(_count)

    async def exists(self, entity_id: str, include_deleted: bool = False) -> bool:
        """Check if an entity exists."""
        async def _exists(session: Session) -> bool:
            query = select(exists().where(self.model_class.id == entity_id))
            
            if not include_deleted and hasattr(self.model_class, 'deleted_at'):
                query = query.where(self.model_class.deleted_at.is_(None))
            
            result = session.execute(query)
            return result.scalar()

        return await self._execute_with_retry(_exists)

    def _build_query(self, options: QueryOptions) -> Select:
        """Build a query with filters, sorting, and pagination."""
        query = select(self.model_class)
        
        # Apply filters
        query = self._apply_filters(query, options.filters)
        
        # Apply soft delete filter
        if not options.include_deleted and hasattr(self.model_class, 'deleted_at'):
            query = query.where(self.model_class.deleted_at.is_(None))
        
        # Apply eager loading
        for relation in options.eager_load:
            if hasattr(self.model_class, relation):
                query = query.options(joinedload(getattr(self.model_class, relation)))
        
        # Apply sorting
        if options.sort_conditions:
            sort_expressions = [
                condition.to_sqlalchemy(self.model_class)
                for condition in options.sort_conditions
            ]
            query = query.order_by(*sort_expressions)
        
        # Apply pagination
        offset = (options.page - 1) * options.page_size
        query = query.offset(offset).limit(options.page_size)
        
        return query

    def _apply_filters(self, query: Select, filters: List[FilterCondition]) -> Select:
        """Apply filters to a query."""
        if not filters:
            return query
        
        conditions = []
        for filter_condition in filters:
            try:
                condition = filter_condition.to_sqlalchemy(self.model_class)
                conditions.append(condition)
            except ValueError as e:
                logger.warning(f"Invalid filter condition: {e}")
                continue
        
        if conditions:
            query = query.where(and_(*conditions))
        
        return query

    async def bulk_create(self, entities: List[TEntity]) -> List[TEntity]:
        """Create multiple entities in a single transaction."""
        async def _bulk_create(session: Session) -> List[TEntity]:
            current_time = datetime.now(timezone.utc)
            
            for entity in entities:
                # Set timestamps
                if hasattr(entity, 'created_at') and not entity.created_at:
                    entity.created_at = current_time
                if hasattr(entity, 'updated_at'):
                    entity.updated_at = current_time
                
                # Set status if not set
                if hasattr(entity, 'status') and not entity.status:
                    entity.status = RecordStatus.ACTIVE
                
                session.add(entity)
            
            session.flush()
            
            # Refresh all entities to get their IDs
            for entity in entities:
                session.refresh(entity)
            
            return entities

        return await self._execute_with_retry(_bulk_create)

    async def bulk_update(self, entities: List[TEntity]) -> List[TEntity]:
        """Update multiple entities in a single transaction."""
        async def _bulk_update(session: Session) -> List[TEntity]:
            current_time = datetime.now(timezone.utc)
            
            for entity in entities:
                # Update timestamp
                if hasattr(entity, 'updated_at'):
                    entity.updated_at = current_time
                
                # Increment version for optimistic locking
                if hasattr(entity, 'version'):
                    entity.version += 1
                
                session.merge(entity)
            
            session.flush()
            
            # Refresh all entities
            for entity in entities:
                session.refresh(entity)
            
            return entities

        return await self._execute_with_retry(_bulk_update)

    async def transaction(self, operations: List[Callable[[Session], Any]]) -> List[Any]:
        """Execute multiple operations in a single transaction."""
        async def _transaction(session: Session) -> List[Any]:
            results = []
            for operation in operations:
                result = operation(session)
                if asyncio.iscoroutine(result):
                    result = await result
                results.append(result)
            return results

        return await self._execute_with_retry(_transaction)


# Export classes and functions
__all__ = [
    "BaseRepository",
    "QueryOptions",
    "PaginatedResult",
    "FilterCondition",
    "SortCondition",
    "FilterOperator",
    "SortOrder",
]
