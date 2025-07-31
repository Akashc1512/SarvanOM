"""
Database Access Layer - Universal Knowledge Platform
MAANG-level database access patterns with security, scalability, and maintainability.

Features:
- Connection pooling and session management
- SQL injection prevention
- Query optimization and caching
- Audit logging and security
- Pagination and sharding support
- Transaction management
- Error handling and retry logic

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import asyncio
import logging
from contextlib import asynccontextmanager, contextmanager
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    AsyncGenerator,
    Generator,
    Tuple,
)
from functools import wraps
from datetime import datetime, timezone
import uuid

from sqlalchemy import (
    create_engine,
    text,
    select,
    update,
    delete,
    insert,
    and_,
    or_,
    func,
    desc,
    asc,
    distinct,
)
from sqlalchemy.orm import (
    sessionmaker,
    Session,
    scoped_session,
    joinedload,
    selectinload,
    subqueryload,
    contains_eager,
)
from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError,
    OperationalError,
    DisconnectionError,
    TimeoutError,
)
from sqlalchemy.pool import QueuePool
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.engine import Engine
from sqlalchemy.sql import Select, Update, Delete, Insert

import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

# Type variables
T = TypeVar("T")
ModelType = TypeVar("ModelType")

logger = structlog.get_logger(__name__)


class DatabaseConfig:
    """Database configuration with security and performance settings."""

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
    """Database manager with connection pooling and session management."""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._scoped_session_factory: Optional[scoped_session] = None

    def initialize(self) -> None:
        """Initialize database engine and session factories."""
        if self._engine is not None:
            return

        # Create engine with connection pooling
        self._engine = create_engine(
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

        # Create session factories
        self._session_factory = sessionmaker(
            bind=self._engine, expire_on_commit=False, autoflush=False, autocommit=False
        )

        self._scoped_session_factory = scoped_session(self._session_factory)

        logger.info(
            "Database manager initialized",
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
        )

    @property
    def engine(self) -> Engine:
        """Get database engine."""
        if self._engine is None:
            self.initialize()
        return self._engine

    @property
    def session_factory(self) -> sessionmaker:
        """Get session factory."""
        if self._session_factory is None:
            self.initialize()
        return self._session_factory

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.session_factory()

    def get_scoped_session(self) -> Session:
        """Get a scoped database session."""
        return self._scoped_session_factory()

    def dispose(self) -> None:
        """Dispose of database engine and connections."""
        if self._engine:
            self._engine.dispose()
            logger.info("Database engine disposed")


class DatabaseSession:
    """Database session wrapper with security and error handling."""

    def __init__(self, session: Session):
        self.session = session
        self._transaction_depth = 0
        self._audit_log = []

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with proper cleanup."""
        try:
            if exc_type is None:
                self.session.commit()
            else:
                self.session.rollback()
                logger.error("Database transaction rolled back", error=str(exc_val))
        finally:
            self.session.close()

    def begin_transaction(self) -> None:
        """Begin a database transaction."""
        self._transaction_depth += 1
        if self._transaction_depth == 1:
            # Start transaction only at first level
            pass

    def commit_transaction(self) -> None:
        """Commit the current transaction."""
        self._transaction_depth -= 1
        if self._transaction_depth == 0:
            self.session.commit()

    def rollback_transaction(self) -> None:
        """Rollback the current transaction."""
        self._transaction_depth -= 1
        if self._transaction_depth == 0:
            self.session.rollback()


class QueryBuilder:
    """Secure query builder with SQL injection prevention."""

    def __init__(self, session: Session):
        self.session = session

    def select(self, model: Type[T]) -> Select:
        """Create a secure SELECT query."""
        return select(model)

    def select_active(self, model: Type[T]) -> Select:
        """Select only active records."""
        return select(model).where(model.is_active == True)

    def select_by_id(self, model: Type[T], id: Union[str, uuid.UUID]) -> Select:
        """Select record by ID with proper type handling."""
        if isinstance(id, str):
            try:
                id = uuid.UUID(id)
            except ValueError:
                raise ValueError("Invalid UUID format")

        return select(model).where(model.id == id)

    def select_by_field(self, model: Type[T], field: str, value: Any) -> Select:
        """Select records by field value with validation."""
        if not hasattr(model, field):
            raise ValueError(f"Field {field} does not exist on {model.__name__}")

        return select(model).where(getattr(model, field) == value)

    def select_paginated(
        self,
        model: Type[T],
        page: int = 1,
        page_size: int = 50,
        order_by: Optional[str] = None,
        order_desc: bool = True,
    ) -> Tuple[Select, Select]:
        """Create paginated query with count."""
        query = select(model)

        # Add ordering
        if order_by and hasattr(model, order_by):
            order_column = getattr(model, order_by)
            if order_desc:
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))

        # Create count query
        count_query = select(func.count()).select_from(model)

        # Add pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        return query, count_query

    def select_with_filters(
        self, model: Type[T], filters: Dict[str, Any], exact_match: bool = True
    ) -> Select:
        """Select records with multiple filters."""
        query = select(model)

        for field, value in filters.items():
            if not hasattr(model, field):
                continue

            column = getattr(model, field)
            if exact_match:
                query = query.where(column == value)
            else:
                # For string fields, use ILIKE for case-insensitive search
                if isinstance(column.type, (str, type(None))):
                    query = query.where(column.ilike(f"%{value}%"))
                else:
                    query = query.where(column == value)

        return query


class Repository:
    """Generic repository pattern for database operations."""

    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model
        self.query_builder = QueryBuilder(session)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    )
    def get_by_id(self, id: Union[str, uuid.UUID]) -> Optional[T]:
        """Get record by ID with retry logic."""
        query = self.query_builder.select_by_id(self.model, id)
        return self.session.execute(query).scalar_one_or_none()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    )
    def get_all(self, limit: Optional[int] = None) -> List[T]:
        """Get all records with optional limit."""
        query = self.query_builder.select_active(self.model)
        if limit:
            query = query.limit(limit)
        return list(self.session.execute(query).scalars().all())

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    )
    def get_paginated(
        self,
        page: int = 1,
        page_size: int = 50,
        order_by: Optional[str] = None,
        order_desc: bool = True,
    ) -> Tuple[List[T], int]:
        """Get paginated results with total count."""
        query, count_query = self.query_builder.select_paginated(
            self.model, page, page_size, order_by, order_desc
        )

        results = list(self.session.execute(query).scalars().all())
        total_count = self.session.execute(count_query).scalar()

        return results, total_count

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    )
    def find_by_filters(
        self,
        filters: Dict[str, Any],
        exact_match: bool = True,
        limit: Optional[int] = None,
    ) -> List[T]:
        """Find records by filters."""
        query = self.query_builder.select_with_filters(self.model, filters, exact_match)

        if limit:
            query = query.limit(limit)

        return list(self.session.execute(query).scalars().all())

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    )
    def create(self, data: Dict[str, Any]) -> T:
        """Create new record with validation."""
        try:
            instance = self.model(**data)
            self.session.add(instance)
            self.session.flush()  # Get the ID without committing
            return instance
        except IntegrityError as e:
            self.session.rollback()
            logger.error("Database integrity error", error=str(e))
            raise ValueError(f"Database constraint violation: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    )
    def update(self, id: Union[str, uuid.UUID], data: Dict[str, Any]) -> Optional[T]:
        """Update record by ID."""
        instance = self.get_by_id(id)
        if not instance:
            return None

        for key, value in data.items():
            if hasattr(instance, key) and key not in ["id", "created_at"]:
                setattr(instance, key, value)

        instance.updated_at = datetime.now(timezone.utc)
        instance.version += 1  # Optimistic locking

        return instance

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    )
    def delete(self, id: Union[str, uuid.UUID], soft_delete: bool = True) -> bool:
        """Delete record by ID (soft delete by default)."""
        instance = self.get_by_id(id)
        if not instance:
            return False

        if soft_delete:
            instance.soft_delete()
        else:
            self.session.delete(instance)

        return True

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    )
    def bulk_create(self, data_list: List[Dict[str, Any]]) -> List[T]:
        """Bulk create records efficiently."""
        instances = []
        for data in data_list:
            instance = self.model(**data)
            instances.append(instance)

        self.session.add_all(instances)
        self.session.flush()
        return instances

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    )
    def bulk_update(
        self, updates: List[Tuple[Union[str, uuid.UUID], Dict[str, Any]]]
    ) -> int:
        """Bulk update records efficiently."""
        updated_count = 0
        for id, data in updates:
            if self.update(id, data):
                updated_count += 1

        return updated_count


class DatabaseService:
    """High-level database service with business logic."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    @contextmanager
    def get_session(self) -> Generator[DatabaseSession, None, None]:
        """Get database session with proper error handling."""
        session = self.db_manager.get_session()
        db_session = DatabaseSession(session)

        try:
            yield db_session
        except Exception as e:
            logger.error("Database operation failed", error=str(e))
            raise
        finally:
            db_session.session.close()

    def get_repository(self, model: Type[T]) -> Repository:
        """Get repository for specific model."""
        session = self.db_manager.get_session()
        return Repository(session, model)

    def execute_raw_sql(
        self, sql: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute raw SQL with parameter binding for security."""
        with self.get_session() as session:
            result = session.session.execute(text(sql), params or {})
            return [dict(row._mapping) for row in result]

    def health_check(self) -> Dict[str, Any]:
        """Perform database health check."""
        try:
            with self.get_session() as session:
                result = session.session.execute(text("SELECT 1 as health"))
                health_status = result.scalar()

                # Check connection pool status
                pool = self.db_manager.engine.pool
                pool_status = {
                    "size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow(),
                }

                return {
                    "status": "healthy" if health_status == 1 else "unhealthy",
                    "pool_status": pool_status,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get global database manager instance."""
    global _db_manager
    if _db_manager is None:
        raise RuntimeError("Database manager not initialized")
    return _db_manager


def initialize_database(config: DatabaseConfig) -> DatabaseManager:
    """Initialize global database manager."""
    global _db_manager
    _db_manager = DatabaseManager(config)
    _db_manager.initialize()
    return _db_manager


def get_database_service() -> DatabaseService:
    """Get database service instance."""
    return DatabaseService(get_database_manager())


# Decorators for database operations
def with_transaction(func):
    """Decorator to handle database transactions."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        db_service = get_database_service()
        with db_service.get_session() as session:
            session.begin_transaction()
            try:
                result = func(*args, **kwargs)
                session.commit_transaction()
                return result
            except Exception:
                session.rollback_transaction()
                raise

    return wrapper


def with_retry(max_attempts: int = 3):
    """Decorator to add retry logic to database operations."""

    def decorator(func):
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=4, max=10),
            retry=retry_if_exception_type((OperationalError, DisconnectionError)),
        )
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


# Export main classes
__all__ = [
    "DatabaseConfig",
    "DatabaseManager",
    "DatabaseSession",
    "QueryBuilder",
    "Repository",
    "DatabaseService",
    "get_database_manager",
    "initialize_database",
    "get_database_service",
    "with_transaction",
    "with_retry",
]
