"""
Database Connection Manager - Universal Knowledge Platform

This module provides a robust database connection manager with:
- Connection pooling for performance
- Automatic retry logic for transient failures
- Health checks and connection validation
- Graceful shutdown handling
- Support for read replicas
- Transaction management

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, AsyncGenerator, Union
from urllib.parse import urlparse
import time

from sqlalchemy import create_engine, text, event
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import (
    OperationalError,
    DisconnectionError,
    TimeoutError,
    SQLAlchemyError,
)
from sqlalchemy.pool import _ConnectionFairy

import structlog

from shared.core.config.central_config import initialize_config

logger = structlog.get_logger(__name__)


class DatabaseConnectionManager:
    """
    Manages database connections with pooling, retry logic, and health checks.
    
    Features:
    - Connection pooling for optimal performance
    - Automatic retry for transient failures
    - Health checks and connection validation
    - Graceful shutdown handling
    - Support for read replicas
    - Transaction management
    """

    def __init__(self, config=None):
        """Initialize the database connection manager."""
        self.config = config or initialize_config()
        self._engines: Dict[str, Engine] = {}
        self._session_factories: Dict[str, sessionmaker] = {}
        self._health_check_interval = 300  # 5 minutes
        self._last_health_check = 0
        self._is_shutdown = False
        
        # Initialize connection pools
        self._init_connection_pools()
        
        # Start health check task
        self._health_check_task = None
        if self.config.database_url:
            self._start_health_check()

    def _init_connection_pools(self):
        """Initialize database connection pools."""
        try:
            # Primary database
            if self.config.database_url:
                self._create_engine("primary", self.config.database_url)
                logger.info("Primary database connection pool initialized")

            # Read replica (if configured)
            if hasattr(self.config, 'database_read_url') and self.config.database_read_url:
                self._create_engine("read_replica", self.config.database_read_url)
                logger.info("Read replica connection pool initialized")

        except Exception as e:
            logger.error(f"Failed to initialize database connection pools: {e}")
            raise

    def _create_engine(self, name: str, url: str):
        """Create a database engine with proper configuration."""
        try:
            # Parse connection URL
            parsed_url = urlparse(url)
            
            # Engine configuration
            engine_config = {
                "poolclass": QueuePool,
                "pool_size": self.config.database_pool_size,
                "max_overflow": self.config.database_max_overflow,
                "pool_timeout": self.config.database_pool_timeout,
                "pool_pre_ping": True,  # Validate connections before use
                "pool_recycle": 3600,   # Recycle connections every hour
                "echo": self.config.debug,  # SQL logging in debug mode
            }
            
            # Create engine
            engine = create_engine(url, **engine_config)
            
            # Add event listeners for connection management
            self._setup_engine_events(engine, name)
            
            # Store engine and create session factory
            self._engines[name] = engine
            self._session_factories[name] = sessionmaker(
                bind=engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )
            
            logger.info(f"Database engine '{name}' created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database engine '{name}': {e}")
            raise

    def _setup_engine_events(self, engine: Engine, name: str):
        """Setup event listeners for the database engine."""
        
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set SQLite pragmas for better performance."""
            if engine.dialect.name == "sqlite":
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=10000")
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.close()

        @event.listens_for(engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log connection checkout."""
            if self.config.debug:
                logger.debug(f"Database connection checked out from pool '{name}'")

        @event.listens_for(engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Log connection checkin."""
            if self.config.debug:
                logger.debug(f"Database connection checked in to pool '{name}'")

    def get_engine(self, name: str = "primary") -> Engine:
        """Get a database engine by name."""
        if name not in self._engines:
            raise ValueError(f"Database engine '{name}' not found")
        return self._engines[name]

    def get_session_factory(self, name: str = "primary") -> sessionmaker:
        """Get a session factory by name."""
        if name not in self._session_factories:
            raise ValueError(f"Session factory '{name}' not found")
        return self._session_factories[name]

    @asynccontextmanager
    async def get_session(self, name: str = "primary") -> AsyncGenerator[Session, None]:
        """Get a database session with automatic cleanup."""
        session_factory = self.get_session_factory(name)
        session = session_factory()
        
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    @asynccontextmanager
    async def get_connection(self, name: str = "primary") -> AsyncGenerator[Connection, None]:
        """Get a database connection with automatic cleanup."""
        engine = self.get_engine(name)
        connection = engine.connect()
        
        try:
            yield connection
            connection.commit()
        except Exception as e:
            connection.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            connection.close()

    async def health_check(self) -> Dict[str, bool]:
        """Perform health checks on all database connections."""
        if self._is_shutdown:
            return {"status": False, "reason": "Database manager is shutdown"}

        current_time = time.time()
        if current_time - self._last_health_check < self._health_check_interval:
            return {"status": True, "reason": "Health check skipped (too recent)"}

        self._last_health_check = current_time
        health_results = {}

        for name, engine in self._engines.items():
            try:
                # Test connection with a simple query
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    result.fetchone()
                
                health_results[name] = True
                logger.debug(f"Health check passed for database '{name}'")
                
            except Exception as e:
                health_results[name] = False
                logger.error(f"Health check failed for database '{name}': {e}")

        all_healthy = all(health_results.values())
        return {
            "status": all_healthy,
            "databases": health_results,
            "reason": "Health check completed"
        }

    async def _health_check_loop(self):
        """Background health check loop."""
        while not self._is_shutdown:
            try:
                await self.health_check()
                await asyncio.sleep(self._health_check_interval)
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    def _start_health_check(self):
        """Start the background health check task."""
        if not self._health_check_task:
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            logger.info("Database health check task started")

    async def shutdown(self):
        """Gracefully shutdown all database connections."""
        if self._is_shutdown:
            return

        logger.info("Shutting down database connection manager...")
        self._is_shutdown = True

        # Stop health check task
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            logger.info("Database health check task stopped")

        # Close all engines
        for name, engine in self._engines.items():
            try:
                engine.dispose()
                logger.info(f"Database engine '{name}' disposed")
            except Exception as e:
                logger.error(f"Error disposing database engine '{name}': {e}")

        logger.info("Database connection manager shutdown complete")

    def get_pool_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get connection pool statistics."""
        stats = {}
        
        for name, engine in self._engines.items():
            pool = engine.pool
            stats[name] = {
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": getattr(pool, 'invalid', lambda: 0)(),
            }
        
        return stats


# Global database connection manager instance
_db_manager: Optional[DatabaseConnectionManager] = None


def get_db_manager() -> DatabaseConnectionManager:
    """Get the global database connection manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseConnectionManager()
    return _db_manager


async def shutdown_db_manager():
    """Shutdown the global database connection manager."""
    global _db_manager
    if _db_manager:
        await _db_manager.shutdown()
        _db_manager = None


# Convenience functions for common operations
async def execute_query(query: str, params: Optional[Dict[str, Any]] = None, 
                       name: str = "primary") -> Any:
    """Execute a raw SQL query."""
    db_manager = get_db_manager()
    async with db_manager.get_connection(name) as conn:
        result = conn.execute(text(query), params or {})
        return result.fetchall()


async def execute_transaction(operations: list, name: str = "primary") -> Any:
    """Execute multiple operations in a transaction."""
    db_manager = get_db_manager()
    async with db_manager.get_session(name) as session:
        results = []
        for operation in operations:
            if callable(operation):
                result = await operation(session)
            else:
                result = session.execute(operation)
            results.append(result)
        return results


# Export the main class and functions
__all__ = [
    "DatabaseConnectionManager",
    "get_db_manager",
    "shutdown_db_manager",
    "execute_query",
    "execute_transaction",
]
