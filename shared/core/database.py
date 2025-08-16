"""
Database Management Module

This module provides database connection management, session handling, and repository patterns
for the Universal Knowledge Platform. It supports async operations and connection pooling.
"""

import logging
import asyncio
import uuid
from typing import Dict, Any, List, Optional, Type, TypeVar, Union, Generator
from contextlib import asynccontextmanager
from functools import wraps
from datetime import datetime

# SQLAlchemy imports
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from sqlalchemy import text, func
from sqlalchemy import select, update, delete
from sqlalchemy.sql import Select
from sqlalchemy.exc import OperationalError, DisconnectionError

# Retry mechanism
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


class DatabaseConfig:
    """Database configuration class."""

    def __init__(
        self,
        url: str,
        pool_size: int = 20,
        max_overflow: int = 30,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        pool_pre_ping: bool = True,
        echo: bool = False,
        echo_pool: bool = False,
        isolation_level: str = "READ_COMMITTED",
    ):
        self.url = url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.pool_pre_ping = pool_pre_ping
        self.echo = echo
        self.echo_pool = echo_pool
        self.isolation_level = isolation_level


class DatabaseManager:
    """Async database manager with connection pooling."""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        self._scoped_session_factory: Optional[async_sessionmaker] = None

    async def initialize(self) -> None:
        """Initialize database engine and session factories asynchronously."""
        if self._engine is not None:
            return

        # Create async engine with connection pooling
        self._engine = create_async_engine(
            self.config.url,
            poolclass=QueuePool,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            pool_recycle=self.config.pool_recycle,
            pool_pre_ping=self.config.pool_pre_ping,
            echo=self.config.echo,
            echo_pool=self.config.echo_pool,
            isolation_level=self.config.isolation_level,
            connect_args={
                "application_name": "universal_knowledge_platform",
                "options": "-c timezone=utc",
            },
        )

        # Create async session factories
        self._session_factory = async_sessionmaker(
            bind=self._engine, expire_on_commit=False, autoflush=False, autocommit=False
        )

        self._scoped_session_factory = async_sessionmaker(
            bind=self._engine, expire_on_commit=False, autoflush=False, autocommit=False
        )

        logger.info(
            "Database manager initialized",
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
        )

    @property
    async def engine(self) -> AsyncEngine:
        """Get database engine asynchronously."""
        if self._engine is None:
            await self.initialize()
        return self._engine

    @property
    async def session_factory(self) -> async_sessionmaker:
        """Get session factory asynchronously."""
        if self._session_factory is None:
            await self.initialize()
        return self._session_factory

    async def get_session(self) -> AsyncSession:
        """Get a new async database session."""
        factory = await self.session_factory
        return factory()

    async def get_scoped_session(self) -> AsyncSession:
        """Get a scoped async database session."""
        factory = await self._scoped_session_factory
        return factory()

    async def dispose(self) -> None:
        """Dispose of database engine and connections asynchronously."""
        if self._engine:
            await self._engine.dispose()
            logger.info("Database engine disposed")


class DatabaseSession:
    """Async database session wrapper with security and error handling."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self._transaction_depth = 0
        self._audit_log = []

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with proper cleanup."""
        try:
            if exc_type is None:
                await self.session.commit()
            else:
                await self.session.rollback()
                logger.error("Database transaction rolled back", error=str(exc_val))
        finally:
            await self.session.close()

    async def begin_transaction(self) -> None:
        """Begin a database transaction asynchronously."""
        self._transaction_depth += 1
        if self._transaction_depth == 1:
            # Start transaction only at first level
            pass

    async def commit_transaction(self) -> None:
        """Commit database transaction asynchronously."""
        self._transaction_depth -= 1
        if self._transaction_depth == 0:
            await self.session.commit()

    async def rollback_transaction(self) -> None:
        """Rollback database transaction asynchronously."""
        self._transaction_depth -= 1
        if self._transaction_depth == 0:
            await self.session.rollback()


class QueryBuilder:
    """Async query builder for database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def select(self, model: Type[T]) -> Select:
        """Create a select query."""
        return select(model)

    def select_active(self, model: Type[T]) -> Select:
        """Create a select query for active records."""
        return select(model).where(model.is_active == True)

    def select_by_id(self, model: Type[T], id: Union[str, uuid.UUID]) -> Select:
        """Create a select query by ID."""
        return select(model).where(model.id == id)

    def select_by_field(self, model: Type[T], field: str, value: Any) -> Select:
        """Create a select query by field."""
        return select(model).where(getattr(model, field) == value)

    def select_paginated(
        self,
        model: Type[T],
        page: int = 1,
        page_size: int = 50,
        order_by: Optional[str] = None,
        order_desc: bool = True,
    ) -> tuple[Select, Select]:
        """Create paginated select queries."""
        query = select(model)

        if order_by:
            order_column = getattr(model, order_by)
            if order_desc:
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())

        # Count query
        count_query = select(func.count()).select_from(model)

        # Paginated query
        offset = (page - 1) * page_size
        paginated_query = query.offset(offset).limit(page_size)

        return paginated_query, count_query

    def select_with_filters(
        self, model: Type[T], filters: Dict[str, Any], exact_match: bool = True
    ) -> Select:
        """Create a select query with filters."""
        query = select(model)

        for field, value in filters.items():
            if hasattr(model, field):
                column = getattr(model, field)
                if exact_match:
                    query = query.where(column == value)
                else:
                    query = query.where(column.ilike(f"%{value}%"))

        return query


class Repository:
    """Async repository pattern for database operations."""

    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model
        self.query_builder = QueryBuilder(session)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    )
    async def get_by_id(self, id: Union[str, uuid.UUID]) -> Optional[T]:
        """Get entity by ID asynchronously."""
        query = self.query_builder.select_by_id(self.model, id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    )
    async def get_all(self, limit: Optional[int] = None) -> List[T]:
        """Get all entities asynchronously."""
        query = self.query_builder.select(self.model)
        if limit:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    )
    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 50,
        order_by: Optional[str] = None,
        order_desc: bool = True,
    ) -> tuple[List[T], int]:
        """Get paginated entities asynchronously."""
        query, count_query = self.query_builder.select_paginated(
            self.model, page, page_size, order_by, order_desc
        )

        # Execute both queries
        result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)

        entities = result.scalars().all()
        total_count = count_result.scalar()

        return entities, total_count

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    )
    async def find_by_filters(
        self,
        filters: Dict[str, Any],
        exact_match: bool = True,
        limit: Optional[int] = None,
    ) -> List[T]:
        """Find entities by filters asynchronously."""
        query = self.query_builder.select_with_filters(self.model, filters, exact_match)
        if limit:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    )
    async def create(self, data: Dict[str, Any]) -> T:
        """Create entity asynchronously."""
        entity = self.model(**data)
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    )
    async def update(
        self, id: Union[str, uuid.UUID], data: Dict[str, Any]
    ) -> Optional[T]:
        """Update entity asynchronously."""
        entity = await self.get_by_id(id)
        if not entity:
            return None

        for field, value in data.items():
            if hasattr(entity, field):
                setattr(entity, field, value)

        entity.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    )
    async def delete(self, id: Union[str, uuid.UUID], soft_delete: bool = True) -> bool:
        """Delete entity asynchronously."""
        entity = await self.get_by_id(id)
        if not entity:
            return False

        if soft_delete and hasattr(entity, "is_active"):
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            await self.session.flush()
        else:
            await self.session.delete(entity)
            await self.session.flush()

        return True

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    )
    async def bulk_create(self, data_list: List[Dict[str, Any]]) -> List[T]:
        """Bulk create entities asynchronously."""
        entities = [self.model(**data) for data in data_list]
        self.session.add_all(entities)
        await self.session.flush()

        # Refresh all entities
        for entity in entities:
            await self.session.refresh(entity)

        return entities

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    )
    async def bulk_update(
        self, updates: List[tuple[Union[str, uuid.UUID], Dict[str, Any]]]
    ) -> int:
        """Bulk update entities asynchronously."""
        updated_count = 0

        for id, data in updates:
            entity = await self.update(id, data)
            if entity:
                updated_count += 1

        return updated_count


class DatabaseService:
    """Async database service with session management."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    @asynccontextmanager
    async def get_session(self) -> Generator[DatabaseSession, None, None]:
        """Get database session asynchronously."""
        session = await self.db_manager.get_session()
        db_session = DatabaseSession(session)
        try:
            yield db_session
        finally:
            await db_session.session.close()

    def get_repository(self, model: Type[T]) -> Repository:
        """Get repository for a model."""
        # Note: This will need to be called within a session context
        session = self.db_manager._session_factory()
        return Repository(session, model)

    async def execute_raw_sql(
        self, sql: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute raw SQL asynchronously."""
        async with self.get_session() as session:
            result = await session.session.execute(text(sql), params or {})
            return [dict(row._mapping) for row in result]

    async def health_check(self) -> Dict[str, Any]:
        """Check database health asynchronously."""
        try:
            async with self.get_session() as session:
                # Test connection with simple query
                result = await session.session.execute(text("SELECT 1"))
                await result.fetchone()

                return {
                    "healthy": True,
                    "status": "connected",
                    "timestamp": datetime.utcnow().isoformat(),
                    "pool_size": self.db_manager.config.pool_size,
                    "max_overflow": self.db_manager.config.max_overflow,
                }

        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "healthy": False,
                "status": "disconnected",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def get_metrics(self) -> Dict[str, Any]:
        """Get database metrics asynchronously."""
        try:
            # Get connection pool info
            engine = await self.db_manager.engine
            pool = engine.pool

            return {
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid(),
            }

        except Exception as e:
            logger.error(f"Failed to get database metrics: {e}")
            return {"error": str(e)}


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


async def get_database_manager() -> DatabaseManager:
    """Get global database manager instance."""
    global _db_manager
    if _db_manager is None:
        raise RuntimeError("Database manager not initialized")
    return _db_manager


async def initialize_database(config: DatabaseConfig) -> DatabaseManager:
    """Initialize database asynchronously."""
    global _db_manager
    _db_manager = DatabaseManager(config)
    await _db_manager.initialize()
    return _db_manager


async def get_database_service() -> DatabaseService:
    """Get database service instance."""
    db_manager = await get_database_manager()
    return DatabaseService(db_manager)


def with_transaction(func):
    """Decorator for database transactions."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        db_service = await get_database_service()
        async with db_service.get_session() as session:
            return await func(*args, **kwargs, session=session)

    return wrapper


def with_retry(max_attempts: int = 3):
    """Decorator for retrying database operations."""

    def decorator(func):
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=4, max=10),
            retry=retry_if_exception_type((OperationalError, DisconnectionError)),
        )
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator
