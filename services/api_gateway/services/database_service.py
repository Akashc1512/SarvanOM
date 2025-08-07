"""
Database Service

This service handles database queries, schema exploration, and data analysis functionality for the database agent.
It provides database connection management, query execution, and schema analysis capabilities.
"""

import logging
from shared.core.unified_logging import get_logger
import asyncio
import json
import time
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime
import aiosqlite
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import text, inspect, MetaData
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import numpy as np

from .base_service import BaseAgentService, ServiceType, ServiceStatus
from shared.core.api.exceptions import (
    DatabaseError, ExternalServiceError, ResourceNotFoundError,
    ValidationError, QueryProcessingError
)
from services.api_gateway.middleware.error_handling import (
    handle_service_error, validate_service_response, log_service_operation
)
from shared.core.error_handler import handle_critical_operation

logger = get_logger(__name__)


class DatabaseService(BaseAgentService):
    """
    Database service for database queries and analysis.
    
    This service provides database connection management, query execution,
    and schema analysis capabilities for the database agent.
    """
    
    def __init__(self, service_type: ServiceType, config: Optional[Dict[str, Any]] = None):
        """Initialize the database service."""
        super().__init__(service_type, config)
        self.connection_pool: Dict[str, AsyncEngine] = {}
        self.session_factories: Dict[str, async_sessionmaker] = {}
        self.max_connections = self.get_config("max_connections", 10)
        self.query_timeout = self.get_config("query_timeout", 60)
        self.max_results = self.get_config("max_results", 1000)
        self.supported_databases = self.get_config("supported_databases", [
            "sqlite", "postgresql", "mysql", "mongodb"
        ])
        self.connection_retries = self.get_config("connection_retries", 3)
        
        # Database configurations
        self.database_configs = self.get_config("database_configs", {})
        
        logger.info("Database service initialized")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check database service health.
        
        Returns:
            Health status and metrics
        """
        try:
            # Test database connectivity
            test_result = await self._test_database_connections()
            
            if test_result["success"]:
                self.update_status(ServiceStatus.HEALTHY)
                return {
                    "healthy": True,
                    "database_connections": "OK",
                    "supported_databases": self.supported_databases,
                    "active_connections": len(self.connection_pool),
                    "max_connections": self.max_connections,
                    "query_timeout": self.query_timeout
                }
            else:
                self.update_status(ServiceStatus.DEGRADED)
                return {
                    "healthy": False,
                    "database_connections": "FAILED",
                    "error": test_result.get("error", "Unknown error")
                }
                
        except Exception as e:
            self.update_status(ServiceStatus.UNHEALTHY)
            logger.error(f"Database service health check failed: {e}")
            return {
                "healthy": False,
                "database_connections": "FAILED",
                "error": str(e)
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get detailed database service status.
        
        Returns:
            Service status information
        """
        health_info = await self.health_check()
        service_info = self.get_service_info()
        
        return {
            **service_info,
            **health_info,
            "capabilities": {
                "query_execution": True,
                "schema_analysis": True,
                "data_analysis": True,
                "query_optimization": True,
                "connection_pooling": True
            }
        }
    
    async def validate_config(self) -> bool:
        """
        Validate database service configuration.
        
        Returns:
            True if configuration is valid
        """
        try:
            # Check required configurations
            if not self.database_configs:
                logger.warning("No database configurations provided")
                return False
            
            # Test connections
            for db_name, config in self.database_configs.items():
                if not await self._test_database_connection(db_name):
                    logger.error(f"Database connection test failed for {db_name}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Database service configuration validation failed: {e}")
            return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get database service metrics.
        
        Returns:
            Service metrics
        """
        try:
            metrics = {
                "active_connections": len(self.connection_pool),
                "total_queries_executed": 0,  # TODO: Implement query counter
                "average_query_time": 0.0,  # TODO: Implement timing metrics
                "cache_hit_rate": 0.0,  # TODO: Implement cache metrics
                "error_rate": 0.0,  # TODO: Implement error tracking
                "supported_databases": len(self.supported_databases),
                "connection_pool_size": self.max_connections
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get database service metrics: {e}")
            return {"error": str(e)}
    
    @handle_critical_operation(operation_type="database", max_retries=3, timeout=30.0)
    async def execute_query(self, database_name: str, query: str,
                          params: Optional[Dict[str, Any]] = None,
                          timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute a database query with proper error handling.
        
        Args:
            database_name: Name of the database
            query: SQL query to execute
            params: Query parameters
            timeout: Query timeout in seconds
            
        Returns:
            Query execution results
            
        Raises:
            DatabaseError: If database operation fails
            ResourceNotFoundError: If database not found
            ValidationError: If query is invalid
        """
        start_time = time.time()
        request_id = f"db_query_{int(start_time * 1000)}"
        
        try:
            # Validate inputs
            if not query or not query.strip():
                raise ValidationError(
                    field="query",
                    message="Query cannot be empty",
                    value=query
                )
            
            if not database_name:
                raise ValidationError(
                    field="database_name",
                    message="Database name is required",
                    value=database_name
                )
            
            # Get database connection
            engine = await self._get_connection(database_name)
            if not engine:
                raise ResourceNotFoundError("database", database_name)
            
            # Execute query with timeout
            query_timeout = timeout or self.query_timeout
            result = await asyncio.wait_for(
                self._execute_sql_query(engine, query, params, query_timeout),
                timeout=query_timeout
            )
            
            # Validate response
            validate_service_response(result, "DatabaseService", "execute_query", dict)
            
            # Log successful operation
            duration = time.time() - start_time
            log_service_operation(
                "DatabaseService",
                "execute_query",
                True,
                duration,
                request_id,
                {"database": database_name, "query_length": len(query)}
            )
            
            return {
                "success": True,
                "data": result,
                "database": database_name,
                "query": query,
                "execution_time": duration,
                "request_id": request_id
            }
            
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            log_service_operation(
                "DatabaseService",
                "execute_query",
                False,
                duration,
                request_id,
                {"database": database_name, "timeout": query_timeout}
            )
            raise DatabaseError(
                operation="execute_query",
                error=f"Query timeout after {query_timeout} seconds",
                database=database_name
            )
            
        except SQLAlchemyError as e:
            duration = time.time() - start_time
            log_service_operation(
                "DatabaseService",
                "execute_query",
                False,
                duration,
                request_id,
                {"database": database_name, "sql_error": str(e)}
            )
            raise DatabaseError(
                operation="execute_query",
                error=str(e),
                database=database_name
            )
            
        except Exception as e:
            duration = time.time() - start_time
            log_service_operation(
                "DatabaseService",
                "execute_query",
                False,
                duration,
                request_id,
                {"database": database_name, "error": str(e)}
            )
            # Use the error handling utility
            handle_service_error("DatabaseService", "execute_query", e, request_id)
            raise  # Re-raise the converted exception
    
    async def get_schema(self, database_name: str) -> Dict[str, Any]:
        """
        Get database schema asynchronously.
        
        Args:
            database_name: Name of the database
            
        Returns:
            Schema information
        """
        try:
            engine = await self._get_connection(database_name)
            if not engine:
                return {
                    "success": False,
                    "error": f"Database connection not available for {database_name}"
                }
            
            return await self._get_database_schema(engine)
            
        except Exception as e:
            logger.error(f"Schema retrieval failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_data(self, database_name: str, table_name: str,
                          columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze table data asynchronously.
        
        Args:
            database_name: Name of the database
            table_name: Name of the table
            columns: Specific columns to analyze
            
        Returns:
            Analysis results
        """
        try:
            engine = await self._get_connection(database_name)
            if not engine:
                return {
                    "success": False,
                    "error": f"Database connection not available for {database_name}"
                }
            
            return await self._analyze_table_data(engine, table_name, columns)
            
        except Exception as e:
            logger.error(f"Data analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def optimize_query(self, database_name: str, query: str) -> Dict[str, Any]:
        """
        Optimize SQL query asynchronously.
        
        Args:
            database_name: Name of the database
            query: SQL query to optimize
            
        Returns:
            Optimization suggestions
        """
        try:
            engine = await self._get_connection(database_name)
            if not engine:
                return {
                    "success": False,
                    "error": f"Database connection not available for {database_name}"
                }
            
            return await self._optimize_sql_query(engine, query)
            
        except Exception as e:
            logger.error(f"Query optimization failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_databases(self) -> Dict[str, Any]:
        """
        List available databases asynchronously.
        
        Returns:
            List of databases
        """
        try:
            databases = []
            
            for db_name, config in self.database_configs.items():
                status = await self._test_database_connection(db_name)
                databases.append({
                    "name": db_name,
                    "type": config.get("type", "unknown"),
                    "host": config.get("host", ""),
                    "port": config.get("port", ""),
                    "database": config.get("database", ""),
                    "status": "connected" if status else "disconnected"
                })
            
            return {
                "success": True,
                "databases": databases,
                "total": len(databases)
            }
            
        except Exception as e:
            logger.error(f"Database listing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_connection(self, database_name: str) -> Dict[str, Any]:
        """
        Test database connection asynchronously.
        
        Args:
            database_name: Name of the database
            
        Returns:
            Connection test results
        """
        try:
            return await self._test_database_connection(database_name)
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_connection(self, database_name: str) -> Optional[AsyncEngine]:
        """
        Get database connection asynchronously.
        
        Args:
            database_name: Name of the database
            
        Returns:
            Database engine
        """
        if database_name not in self.connection_pool:
            config = self.database_configs.get(database_name)
            if not config:
                logger.error(f"No configuration found for database: {database_name}")
                return None
            
            engine = await self._create_connection(config)
            if engine:
                self.connection_pool[database_name] = engine
        
        return self.connection_pool.get(database_name)
    
    async def _create_connection(self, config: Dict[str, Any]) -> Optional[AsyncEngine]:
        """
        Create database connection asynchronously.
        
        Args:
            config: Database configuration
            
        Returns:
            Database engine
        """
        try:
            db_type = config.get("type", "sqlite")
            
            if db_type == "sqlite":
                db_path = config.get("database", ":memory:")
                connection_string = f"sqlite+aiosqlite:///{db_path}"
                
            elif db_type == "postgresql":
                host = config.get("host", "localhost")
                port = config.get("port", 5432)
                database = config.get("database", "")
                username = config.get("username", "")
                password = config.get("password", "")
                
                connection_string = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
                
            elif db_type == "mysql":
                host = config.get("host", "localhost")
                port = config.get("port", 3306)
                database = config.get("database", "")
                username = config.get("username", "")
                password = config.get("password", "")
                
                connection_string = f"mysql+aiomysql://{username}:{password}@{host}:{port}/{database}"
                
            else:
                logger.error(f"Unsupported database type: {db_type}")
                return None
            
            # Create async engine
            engine = create_async_engine(
                connection_string,
                pool_size=self.max_connections,
                max_overflow=self.max_connections * 2,
                pool_timeout=self.query_timeout,
                pool_recycle=3600,
                echo=False
            )
            
            # Create session factory
            session_factory = async_sessionmaker(
                bind=engine,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False
            )
            
            # Store session factory
            db_name = config.get("name", "default")
            self.session_factories[db_name] = session_factory
            
            logger.info(f"Created async connection for {db_type} database")
            return engine
            
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            return None
    
    async def _execute_sql_query(self, engine: AsyncEngine, query: str,
                                params: Optional[Dict[str, Any]] = None,
                                timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute SQL query asynchronously.
        
        Args:
            engine: Database engine
            query: SQL query
            params: Query parameters
            timeout: Query timeout
            
        Returns:
            Query results
        """
        start_time = datetime.now()
        
        try:
            async with engine.begin() as connection:
                # Set timeout if specified
                if timeout:
                    await connection.execute(text("SET statement_timeout = :timeout"), {"timeout": timeout * 1000})
                
                # Execute query
                if params:
                    result = await connection.execute(text(query), params)
                else:
                    result = await connection.execute(text(query))
                
                # Fetch results
                if result.returns_rows:
                    rows = await result.fetchall()
                    columns = result.keys()
                    
                    # Convert to list of dictionaries
                    data = []
                    for row in rows[:self.max_results]:
                        data.append(dict(zip(columns, row)))
                    
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    return {
                        "success": True,
                        "data": data,
                        "total_rows": len(rows),
                        "returned_rows": len(data),
                        "columns": list(columns),
                        "execution_time": execution_time,
                        "query": query
                    }
                else:
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    return {
                        "success": True,
                        "data": [],
                        "total_rows": 0,
                        "returned_rows": 0,
                        "columns": [],
                        "execution_time": execution_time,
                        "query": query,
                        "message": "Query executed successfully (no results)"
                    }
                    
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "query": query
            }
    
    async def _get_database_schema(self, engine: AsyncEngine) -> Dict[str, Any]:
        """
        Get database schema asynchronously.
        
        Args:
            engine: Database engine
            
        Returns:
            Schema information
        """
        try:
            async with engine.begin() as connection:
                # Get table names
                result = await connection.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                tables = await result.fetchall()
                
                schema_info = {
                    "tables": [],
                    "total_tables": len(tables)
                }
                
                for table_row in tables:
                    table_name = table_row[0]
                    
                    # Get columns for this table
                    result = await connection.execute(text("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns 
                        WHERE table_name = :table_name
                        ORDER BY ordinal_position
                    """), {"table_name": table_name})
                    
                    columns = await result.fetchall()
                    
                    table_info = {
                        "name": table_name,
                        "columns": [
                            {
                                "name": col[0],
                                "type": col[1],
                                "nullable": col[2] == "YES",
                                "default": col[3]
                            }
                            for col in columns
                        ]
                    }
                    
                    schema_info["tables"].append(table_info)
                
                return {
                    "success": True,
                    "schema": schema_info
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _analyze_table_data(self, engine: AsyncEngine, table_name: str,
                                 columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze table data asynchronously.
        
        Args:
            engine: Database engine
            table_name: Name of the table
            columns: Specific columns to analyze
            
        Returns:
            Analysis results
        """
        try:
            async with engine.begin() as connection:
                # Get row count
                result = await connection.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                row_count = await result.scalar()
                
                # Get column statistics
                if not columns:
                    result = await connection.execute(text(f"SELECT * FROM {table_name} LIMIT 1"))
                    columns = [desc[0] for desc in result.cursor.description]
                
                analysis = {
                    "table_name": table_name,
                    "row_count": row_count,
                    "columns": {}
                }
                
                for column in columns:
                    # Get column statistics
                    result = await connection.execute(text(f"""
                        SELECT 
                            COUNT(*) as count,
                            COUNT(DISTINCT {column}) as distinct_count,
                            MIN({column}) as min_value,
                            MAX({column}) as max_value,
                            AVG({column}) as avg_value
                        FROM {table_name}
                    """))
                    
                    stats = await result.fetchone()
                    if stats:
                        analysis["columns"][column] = {
                            "count": stats[0],
                            "distinct_count": stats[1],
                            "min_value": stats[2],
                            "max_value": stats[3],
                            "avg_value": float(stats[4]) if stats[4] else None
                        }
                
                return {
                    "success": True,
                    "analysis": analysis
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _optimize_sql_query(self, engine: AsyncEngine, query: str) -> Dict[str, Any]:
        """
        Optimize SQL query asynchronously.
        
        Args:
            engine: Database engine
            query: SQL query to optimize
            
        Returns:
            Optimization suggestions
        """
        try:
            # Basic query analysis
            query_lower = query.lower()
            
            suggestions = []
            
            # Check for SELECT *
            if "select *" in query_lower:
                suggestions.append({
                    "type": "warning",
                    "message": "Consider selecting specific columns instead of using SELECT *",
                    "impact": "medium"
                })
            
            # Check for missing WHERE clause
            if "select" in query_lower and "where" not in query_lower:
                suggestions.append({
                    "type": "warning",
                    "message": "Consider adding a WHERE clause to limit results",
                    "impact": "high"
                })
            
            # Check for ORDER BY without LIMIT
            if "order by" in query_lower and "limit" not in query_lower:
                suggestions.append({
                    "type": "warning",
                    "message": "Consider adding LIMIT when using ORDER BY",
                    "impact": "medium"
                })
            
            return {
                "success": True,
                "query": query,
                "suggestions": suggestions,
                "total_suggestions": len(suggestions)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_database_connection(self, database_name: str) -> Dict[str, Any]:
        """
        Test database connection asynchronously.
        
        Args:
            database_name: Name of the database
            
        Returns:
            Connection test results
        """
        try:
            engine = await self._get_connection(database_name)
            if not engine:
                return {
                    "success": False,
                    "error": f"Failed to create connection for {database_name}"
                }
            
            # Test connection with simple query
            async with engine.begin() as connection:
                result = await connection.execute(text("SELECT 1"))
                await result.fetchone()
            
            return {
                "success": True,
                "database": database_name,
                "status": "connected"
            }
            
        except Exception as e:
            return {
                "success": False,
                "database": database_name,
                "error": str(e)
            }
    
    async def _test_database_connections(self) -> Dict[str, Any]:
        """
        Test all database connections asynchronously.
        
        Returns:
            Test results
        """
        try:
            results = []
            all_successful = True
            
            for db_name in self.database_configs.keys():
                result = await self._test_database_connection(db_name)
                results.append(result)
                
                if not result["success"]:
                    all_successful = False
            
            return {
                "success": all_successful,
                "results": results,
                "total_databases": len(results),
                "successful_connections": len([r for r in results if r["success"]])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def shutdown(self) -> None:
        """Shutdown database service."""
        try:
            # Close all connections
            for engine in self.connection_pool.values():
                await engine.dispose()
            
            self.connection_pool.clear()
            self.session_factories.clear()
            
            logger.info("Database service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during database service shutdown: {e}") 