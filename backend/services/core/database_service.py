"""
Database Service for Clean Architecture Backend

This service handles database queries, schema exploration, and data analysis functionality.
It provides database connection management, query execution, and schema analysis capabilities.
Migrated from the original services/api_gateway/services/database_service.py.
"""

import logging
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

from ...utils.logging import get_logger
from ...models.domain.database import DatabaseConfig, QueryResult, SchemaInfo, DataAnalysis
from ...models.domain.enums import ServiceStatus, DatabaseType

logger = get_logger(__name__)


class DatabaseService:
    """
    Database service for database queries and analysis.
    
    This service provides database connection management, query execution,
    and schema analysis capabilities.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the database service."""
        self.config = config or {}
        self.connection_pool: Dict[str, AsyncEngine] = {}
        self.session_factories: Dict[str, async_sessionmaker] = {}
        self.max_connections = self.config.get("max_connections", 10)
        self.query_timeout = self.config.get("query_timeout", 60)
        self.max_results = self.config.get("max_results", 1000)
        self.supported_databases = self.config.get("supported_databases", [
            "sqlite", "postgresql", "mysql", "mongodb"
        ])
        self.connection_retries = self.config.get("connection_retries", 3)
        self.database_configs = self.config.get("database_configs", {})
        self.status = ServiceStatus.HEALTHY
        
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
                self.status = ServiceStatus.HEALTHY
                return {
                    "healthy": True,
                    "database_connections": "OK",
                    "supported_databases": self.supported_databases,
                    "active_connections": len(self.connection_pool),
                    "max_connections": self.max_connections,
                    "query_timeout": self.query_timeout,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                self.status = ServiceStatus.DEGRADED
                return {
                    "healthy": False,
                    "database_connections": "FAILED",
                    "error": test_result.get("error", "Unknown error"),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.status = ServiceStatus.UNHEALTHY
            logger.error(f"Database service health check failed: {e}")
            return {
                "healthy": False,
                "database_connections": "FAILED",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
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
            
            # Validate each database configuration
            for db_name, config in self.database_configs.items():
                if not self._validate_database_config(config):
                    logger.error(f"Invalid configuration for database: {db_name}")
                    return False
            
            logger.info("Database service configuration validated successfully")
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
                "status": self.status.value,
                "active_connections": len(self.connection_pool),
                "max_connections": self.max_connections,
                "supported_databases": len(self.supported_databases),
                "configured_databases": len(self.database_configs),
                "query_timeout": self.query_timeout,
                "max_results": self.max_results,
                "connection_retries": self.connection_retries,
                "timestamp": datetime.now().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting database service metrics: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def execute_query(
        self, 
        database_name: str, 
        query: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> QueryResult:
        """
        Execute a database query.
        
        Args:
            database_name: Name of the database
            query: SQL query to execute
            params: Query parameters
            timeout: Query timeout in seconds
            
        Returns:
            Query result with data and metadata
        """
        try:
            start_time = time.time()
            
            # Get database connection
            engine = await self._get_connection(database_name)
            if not engine:
                raise Exception(f"Could not connect to database: {database_name}")
            
            # Execute query
            result = await self._execute_sql_query(engine, query, params, timeout)
            
            processing_time = time.time() - start_time
            
            return QueryResult(
                success=True,
                data=result.get("data", []),
                row_count=result.get("row_count", 0),
                columns=result.get("columns", []),
                query=query,
                database_name=database_name,
                processing_time=processing_time,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error executing query on {database_name}: {e}")
            return QueryResult(
                success=False,
                error=str(e),
                query=query,
                database_name=database_name,
                timestamp=datetime.now()
            )
    
    async def get_schema(self, database_name: str) -> SchemaInfo:
        """
        Get database schema information.
        
        Args:
            database_name: Name of the database
            
        Returns:
            Schema information
        """
        try:
            engine = await self._get_connection(database_name)
            if not engine:
                raise Exception(f"Could not connect to database: {database_name}")
            
            schema_data = await self._get_database_schema(engine)
            
            return SchemaInfo(
                database_name=database_name,
                tables=schema_data.get("tables", []),
                views=schema_data.get("views", []),
                indexes=schema_data.get("indexes", []),
                constraints=schema_data.get("constraints", []),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error getting schema for {database_name}: {e}")
            return SchemaInfo(
                database_name=database_name,
                error=str(e),
                timestamp=datetime.now()
            )
    
    async def analyze_data(
        self, 
        database_name: str, 
        table_name: str,
        columns: Optional[List[str]] = None
    ) -> DataAnalysis:
        """
        Analyze table data.
        
        Args:
            database_name: Name of the database
            table_name: Name of the table
            columns: Specific columns to analyze
            
        Returns:
            Data analysis results
        """
        try:
            engine = await self._get_connection(database_name)
            if not engine:
                raise Exception(f"Could not connect to database: {database_name}")
            
            analysis_data = await self._analyze_table_data(engine, table_name, columns)
            
            return DataAnalysis(
                database_name=database_name,
                table_name=table_name,
                row_count=analysis_data.get("row_count", 0),
                column_stats=analysis_data.get("column_stats", {}),
                data_types=analysis_data.get("data_types", {}),
                missing_values=analysis_data.get("missing_values", {}),
                unique_values=analysis_data.get("unique_values", {}),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error analyzing data for {database_name}.{table_name}: {e}")
            return DataAnalysis(
                database_name=database_name,
                table_name=table_name,
                error=str(e),
                timestamp=datetime.now()
            )
    
    async def optimize_query(self, database_name: str, query: str) -> Dict[str, Any]:
        """
        Optimize a database query.
        
        Args:
            database_name: Name of the database
            query: SQL query to optimize
            
        Returns:
            Query optimization suggestions
        """
        try:
            engine = await self._get_connection(database_name)
            if not engine:
                raise Exception(f"Could not connect to database: {database_name}")
            
            optimization_data = await self._optimize_sql_query(engine, query)
            
            return {
                "original_query": query,
                "optimized_query": optimization_data.get("optimized_query", query),
                "suggestions": optimization_data.get("suggestions", []),
                "performance_improvement": optimization_data.get("performance_improvement", 0.0),
                "database_name": database_name,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error optimizing query for {database_name}: {e}")
            return {
                "original_query": query,
                "error": str(e),
                "database_name": database_name,
                "timestamp": datetime.now().isoformat()
            }
    
    async def list_databases(self) -> Dict[str, Any]:
        """
        List available databases.
        
        Returns:
            List of available databases
        """
        try:
            databases = []
            
            for db_name, config in self.database_configs.items():
                try:
                    # Test connection
                    test_result = await self._test_database_connection(db_name)
                    
                    databases.append({
                        "name": db_name,
                        "type": config.get("type", "unknown"),
                        "host": config.get("host", "localhost"),
                        "port": config.get("port", 5432),
                        "database": config.get("database", ""),
                        "status": "connected" if test_result["success"] else "disconnected",
                        "error": test_result.get("error")
                    })
                    
                except Exception as e:
                    databases.append({
                        "name": db_name,
                        "type": config.get("type", "unknown"),
                        "status": "error",
                        "error": str(e)
                    })
            
            return {
                "databases": databases,
                "total_count": len(databases),
                "connected_count": len([db for db in databases if db["status"] == "connected"]),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error listing databases: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def test_connection(self, database_name: str) -> Dict[str, Any]:
        """
        Test database connection.
        
        Args:
            database_name: Name of the database
            
        Returns:
            Connection test result
        """
        try:
            test_result = await self._test_database_connection(database_name)
            
            return {
                "database_name": database_name,
                "success": test_result["success"],
                "response_time": test_result.get("response_time", 0.0),
                "error": test_result.get("error"),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error testing connection for {database_name}: {e}")
            return {
                "database_name": database_name,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # Private helper methods
    
    def _validate_database_config(self, config: Dict[str, Any]) -> bool:
        """Validate database configuration."""
        required_fields = ["type", "host", "database"]
        
        for field in required_fields:
            if field not in config:
                return False
        
        return True
    
    async def _get_connection(self, database_name: str) -> Optional[AsyncEngine]:
        """Get database connection."""
        try:
            if database_name in self.connection_pool:
                return self.connection_pool[database_name]
            
            config = self.database_configs.get(database_name)
            if not config:
                raise Exception(f"Database configuration not found: {database_name}")
            
            engine = await self._create_connection(config)
            if engine:
                self.connection_pool[database_name] = engine
            
            return engine
            
        except Exception as e:
            logger.error(f"Error getting connection for {database_name}: {e}")
            return None
    
    async def _create_connection(self, config: Dict[str, Any]) -> Optional[AsyncEngine]:
        """Create database connection."""
        try:
            db_type = config.get("type", "postgresql")
            host = config.get("host", "localhost")
            port = config.get("port", 5432)
            database = config.get("database", "")
            username = config.get("username", "")
            password = config.get("password", "")
            
            if db_type == "postgresql":
                connection_string = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
            elif db_type == "mysql":
                connection_string = f"mysql+aiomysql://{username}:{password}@{host}:{port}/{database}"
            elif db_type == "sqlite":
                connection_string = f"sqlite+aiosqlite:///{database}"
            else:
                raise Exception(f"Unsupported database type: {db_type}")
            
            engine = create_async_engine(
                connection_string,
                echo=False,
                pool_size=self.max_connections,
                max_overflow=0,
                pool_pre_ping=True
            )
            
            # Test connection
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            logger.info(f"Successfully created connection for {database}")
            return engine
            
        except Exception as e:
            logger.error(f"Error creating database connection: {e}")
            return None
    
    async def _execute_sql_query(
        self, 
        engine: AsyncEngine, 
        query: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute SQL query."""
        try:
            timeout = timeout or self.query_timeout
            
            async with engine.begin() as conn:
                # Execute query with timeout
                result = await asyncio.wait_for(
                    conn.execute(text(query), params or {}),
                    timeout=timeout
                )
                
                # Fetch results
                if result.returns_rows:
                    rows = await asyncio.wait_for(result.fetchall(), timeout=timeout)
                    columns = result.keys()
                    
                    # Convert to list of dicts
                    data = []
                    for row in rows[:self.max_results]:
                        data.append(dict(zip(columns, row)))
                    
                    return {
                        "data": data,
                        "row_count": len(data),
                        "columns": list(columns),
                        "success": True
                    }
                else:
                    return {
                        "data": [],
                        "row_count": result.rowcount,
                        "columns": [],
                        "success": True
                    }
                    
        except Exception as e:
            logger.error(f"Error executing SQL query: {e}")
            return {
                "data": [],
                "row_count": 0,
                "columns": [],
                "success": False,
                "error": str(e)
            }
    
    async def _get_database_schema(self, engine: AsyncEngine) -> Dict[str, Any]:
        """Get database schema information."""
        try:
            inspector = inspect(engine)
            
            tables = []
            for table_name in await inspector.get_table_names():
                columns = await inspector.get_columns(table_name)
                indexes = await inspector.get_indexes(table_name)
                foreign_keys = await inspector.get_foreign_keys(table_name)
                
                tables.append({
                    "name": table_name,
                    "columns": [{"name": col["name"], "type": str(col["type"])} for col in columns],
                    "indexes": [{"name": idx["name"], "columns": idx["column_names"]} for idx in indexes],
                    "foreign_keys": [{"name": fk["name"], "referred_table": fk["referred_table"]} for fk in foreign_keys]
                })
            
            views = []
            for view_name in await inspector.get_view_names():
                view_columns = await inspector.get_columns(view_name)
                views.append({
                    "name": view_name,
                    "columns": [{"name": col["name"], "type": str(col["type"])} for col in view_columns]
                })
            
            return {
                "tables": tables,
                "views": views,
                "indexes": [],
                "constraints": []
            }
            
        except Exception as e:
            logger.error(f"Error getting database schema: {e}")
            return {
                "tables": [],
                "views": [],
                "indexes": [],
                "constraints": [],
                "error": str(e)
            }
    
    async def _analyze_table_data(
        self, 
        engine: AsyncEngine, 
        table_name: str,
        columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Analyze table data."""
        try:
            # Get table data
            query = f"SELECT * FROM {table_name} LIMIT 1000"
            result = await self._execute_sql_query(engine, query)
            
            if not result["success"]:
                return {"error": result.get("error", "Failed to fetch data")}
            
            data = result["data"]
            if not data:
                return {"row_count": 0, "column_stats": {}, "data_types": {}}
            
            # Analyze columns
            column_stats = {}
            data_types = {}
            missing_values = {}
            unique_values = {}
            
            for column in result["columns"]:
                if columns and column not in columns:
                    continue
                
                values = [row[column] for row in data if column in row]
                
                # Basic statistics
                non_null_values = [v for v in values if v is not None]
                column_stats[column] = {
                    "count": len(values),
                    "non_null_count": len(non_null_values),
                    "null_count": len(values) - len(non_null_values)
                }
                
                # Data type detection
                if non_null_values:
                    sample_value = non_null_values[0]
                    if isinstance(sample_value, (int, float)):
                        data_types[column] = "numeric"
                        if non_null_values:
                            column_stats[column].update({
                                "min": min(non_null_values),
                                "max": max(non_null_values),
                                "avg": sum(non_null_values) / len(non_null_values)
                            })
                    else:
                        data_types[column] = "text"
                        column_stats[column]["unique_count"] = len(set(non_null_values))
                
                # Missing values
                missing_values[column] = len(values) - len(non_null_values)
                
                # Unique values (for text columns)
                if data_types.get(column) == "text":
                    unique_values[column] = len(set(non_null_values))
            
            return {
                "row_count": len(data),
                "column_stats": column_stats,
                "data_types": data_types,
                "missing_values": missing_values,
                "unique_values": unique_values
            }
            
        except Exception as e:
            logger.error(f"Error analyzing table data: {e}")
            return {"error": str(e)}
    
    async def _optimize_sql_query(self, engine: AsyncEngine, query: str) -> Dict[str, Any]:
        """Optimize SQL query."""
        try:
            # Basic query optimization suggestions
            suggestions = []
            optimized_query = query
            
            # Check for SELECT *
            if "SELECT *" in query.upper():
                suggestions.append("Consider selecting specific columns instead of using SELECT *")
            
            # Check for missing WHERE clause
            if "SELECT" in query.upper() and "WHERE" not in query.upper():
                suggestions.append("Consider adding a WHERE clause to limit results")
            
            # Check for ORDER BY without LIMIT
            if "ORDER BY" in query.upper() and "LIMIT" not in query.upper():
                suggestions.append("Consider adding LIMIT when using ORDER BY")
            
            # Check for potential index usage
            if "WHERE" in query.upper():
                suggestions.append("Ensure appropriate indexes exist for WHERE clause columns")
            
            return {
                "optimized_query": optimized_query,
                "suggestions": suggestions,
                "performance_improvement": 0.1 if suggestions else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error optimizing SQL query: {e}")
            return {
                "optimized_query": query,
                "suggestions": [f"Error during optimization: {str(e)}"],
                "performance_improvement": 0.0
            }
    
    async def _test_database_connection(self, database_name: str) -> Dict[str, Any]:
        """Test database connection."""
        try:
            start_time = time.time()
            
            engine = await self._get_connection(database_name)
            if not engine:
                return {"success": False, "error": "Could not create connection"}
            
            # Test with simple query
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            response_time = time.time() - start_time
            
            return {
                "success": True,
                "response_time": response_time
            }
            
        except Exception as e:
            logger.error(f"Error testing database connection for {database_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_database_connections(self) -> Dict[str, Any]:
        """Test all database connections."""
        try:
            results = {}
            all_success = True
            
            for db_name in self.database_configs.keys():
                test_result = await self._test_database_connection(db_name)
                results[db_name] = test_result
                
                if not test_result["success"]:
                    all_success = False
            
            return {
                "success": all_success,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error testing database connections: {e}")
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
            
            logger.info("Database service shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during database service shutdown: {e}") 