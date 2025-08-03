"""
Database Service

This service handles database queries, schema exploration, and data analysis functionality for the database agent.
It provides database connection management, query execution, and schema analysis capabilities.
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime
import sqlite3
import psycopg2
import pymongo
from sqlalchemy import create_engine, text, inspect, MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import numpy as np

from .base_service import BaseAgentService, ServiceType, ServiceStatus

logger = logging.getLogger(__name__)


class DatabaseService(BaseAgentService):
    """
    Database service for database queries and analysis.
    
    This service provides database connection management, query execution,
    and schema analysis capabilities for the database agent.
    """
    
    def __init__(self, service_type: ServiceType, config: Optional[Dict[str, Any]] = None):
        """Initialize the database service."""
        super().__init__(service_type, config)
        self.connection_pool: Dict[str, Engine] = {}
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
                "schema_exploration": True,
                "data_analysis": True,
                "connection_management": True,
                "multi_database_support": True
            },
            "configuration": {
                "supported_databases": self.supported_databases,
                "max_connections": self.max_connections,
                "query_timeout": self.query_timeout,
                "max_results": self.max_results,
                "connection_retries": self.connection_retries
            }
        }
    
    async def validate_config(self) -> bool:
        """
        Validate database service configuration.
        
        Returns:
            True if configuration is valid
        """
        try:
            # Check required configuration
            if self.max_connections <= 0:
                logger.error("Database service: Invalid max_connections value")
                return False
            
            if self.query_timeout <= 0:
                logger.error("Database service: Invalid query_timeout value")
                return False
            
            if self.max_results <= 0:
                logger.error("Database service: Invalid max_results value")
                return False
            
            if not self.supported_databases:
                logger.error("Database service: No supported databases configured")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Database service config validation failed: {e}")
            return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get database service performance metrics.
        
        Returns:
            Performance metrics
        """
        base_metrics = self.get_service_info()
        
        # Add database-specific metrics
        database_metrics = {
            "queries_executed": 0,  # TODO: Track actual queries
            "connections_active": len(self.connection_pool),
            "average_query_time": 0.0,  # TODO: Track query times
            "success_rate": 1.0 if self.error_count == 0 else 0.0
        }
        
        return {**base_metrics, **database_metrics}
    
    async def execute_query(self, database_name: str, query: str,
                          params: Optional[Dict[str, Any]] = None,
                          timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute a database query.
        
        Args:
            database_name: Name of the database
            query: SQL query to execute
            params: Query parameters
            timeout: Query timeout
            
        Returns:
            Query results
        """
        await self.pre_request()
        
        try:
            # Get database connection
            engine = await self._get_connection(database_name)
            if not engine:
                raise ValueError(f"Database '{database_name}' not configured")
            
            # Execute query
            result = await self._execute_sql_query(engine, query, params, timeout)
            await self.post_request(success=True)
            return result
            
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Query execution failed: {e}")
            raise
    
    async def get_schema(self, database_name: str) -> Dict[str, Any]:
        """
        Get database schema information.
        
        Args:
            database_name: Name of the database
            
        Returns:
            Schema information
        """
        await self.pre_request()
        
        try:
            # Get database connection
            engine = await self._get_connection(database_name)
            if not engine:
                raise ValueError(f"Database '{database_name}' not configured")
            
            # Get schema
            schema = await self._get_database_schema(engine)
            await self.post_request(success=True)
            return schema
            
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Schema retrieval failed: {e}")
            raise
    
    async def analyze_data(self, database_name: str, table_name: str,
                          columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze data in a table.
        
        Args:
            database_name: Name of the database
            table_name: Name of the table
            columns: Specific columns to analyze
            
        Returns:
            Data analysis results
        """
        await self.pre_request()
        
        try:
            # Get database connection
            engine = await self._get_connection(database_name)
            if not engine:
                raise ValueError(f"Database '{database_name}' not configured")
            
            # Analyze data
            analysis = await self._analyze_table_data(engine, table_name, columns)
            await self.post_request(success=True)
            return analysis
            
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Data analysis failed: {e}")
            raise
    
    async def optimize_query(self, database_name: str, query: str) -> Dict[str, Any]:
        """
        Optimize a database query.
        
        Args:
            database_name: Name of the database
            query: SQL query to optimize
            
        Returns:
            Query optimization results
        """
        await self.pre_request()
        
        try:
            # Get database connection
            engine = await self._get_connection(database_name)
            if not engine:
                raise ValueError(f"Database '{database_name}' not configured")
            
            # Optimize query
            optimization = await self._optimize_sql_query(engine, query)
            await self.post_request(success=True)
            return optimization
            
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Query optimization failed: {e}")
            raise
    
    async def list_databases(self) -> Dict[str, Any]:
        """
        List available databases.
        
        Returns:
            List of available databases
        """
        await self.pre_request()
        
        try:
            databases = []
            for name, config in self.database_configs.items():
                databases.append({
                    "name": name,
                    "type": config.get("type", "unknown"),
                    "host": config.get("host", ""),
                    "port": config.get("port", ""),
                    "database": config.get("database", ""),
                    "connected": name in self.connection_pool
                })
            
            await self.post_request(success=True)
            return {
                "databases": databases,
                "total": len(databases),
                "connected": len(self.connection_pool)
            }
            
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Database listing failed: {e}")
            raise
    
    async def test_connection(self, database_name: str) -> Dict[str, Any]:
        """
        Test database connection.
        
        Args:
            database_name: Name of the database
            
        Returns:
            Connection test results
        """
        await self.pre_request()
        
        try:
            # Test connection
            result = await self._test_database_connection(database_name)
            await self.post_request(success=True)
            return result
            
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Connection test failed: {e}")
            raise
    
    async def _get_connection(self, database_name: str) -> Optional[Engine]:
        """
        Get database connection.
        
        Args:
            database_name: Name of the database
            
        Returns:
            Database engine or None
        """
        if database_name in self.connection_pool:
            return self.connection_pool[database_name]
        
        # Create new connection
        config = self.database_configs.get(database_name)
        if not config:
            logger.error(f"Database '{database_name}' not configured")
            return None
        
        try:
            engine = await self._create_connection(config)
            if engine:
                self.connection_pool[database_name] = engine
                logger.info(f"Created connection to database: {database_name}")
            return engine
            
        except Exception as e:
            logger.error(f"Failed to create connection to database '{database_name}': {e}")
            return None
    
    async def _create_connection(self, config: Dict[str, Any]) -> Optional[Engine]:
        """
        Create database connection.
        
        Args:
            config: Database configuration
            
        Returns:
            Database engine or None
        """
        try:
            db_type = config.get("type", "sqlite")
            
            if db_type == "sqlite":
                return create_engine(f"sqlite:///{config.get('database', ':memory:')}")
            
            elif db_type == "postgresql":
                host = config.get("host", "localhost")
                port = config.get("port", 5432)
                database = config.get("database", "")
                username = config.get("username", "")
                password = config.get("password", "")
                
                connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
                return create_engine(connection_string)
            
            elif db_type == "mysql":
                host = config.get("host", "localhost")
                port = config.get("port", 3306)
                database = config.get("database", "")
                username = config.get("username", "")
                password = config.get("password", "")
                
                connection_string = f"mysql://{username}:{password}@{host}:{port}/{database}"
                return create_engine(connection_string)
            
            else:
                logger.error(f"Unsupported database type: {db_type}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            return None
    
    async def _execute_sql_query(self, engine: Engine, query: str,
                                params: Optional[Dict[str, Any]] = None,
                                timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute SQL query.
        
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
            with engine.connect() as connection:
                # Set timeout if specified
                if timeout:
                    connection.execute(text("SET statement_timeout = :timeout"), {"timeout": timeout * 1000})
                
                # Execute query
                if params:
                    result = connection.execute(text(query), params)
                else:
                    result = connection.execute(text(query))
                
                # Fetch results
                if result.returns_rows:
                    rows = result.fetchall()
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
    
    async def _get_database_schema(self, engine: Engine) -> Dict[str, Any]:
        """
        Get database schema information.
        
        Args:
            engine: Database engine
            
        Returns:
            Schema information
        """
        try:
            inspector = inspect(engine)
            
            # Get all tables
            tables = inspector.get_table_names()
            
            schema_info = {
                "tables": [],
                "total_tables": len(tables)
            }
            
            for table_name in tables:
                table_info = {
                    "name": table_name,
                    "columns": [],
                    "primary_keys": [],
                    "foreign_keys": [],
                    "indexes": []
                }
                
                # Get column information
                columns = inspector.get_columns(table_name)
                for column in columns:
                    table_info["columns"].append({
                        "name": column["name"],
                        "type": str(column["type"]),
                        "nullable": column.get("nullable", True),
                        "default": column.get("default"),
                        "primary_key": column.get("primary_key", False)
                    })
                
                # Get primary keys
                primary_keys = inspector.get_pk_constraint(table_name)
                if primary_keys and primary_keys.get("constrained_columns"):
                    table_info["primary_keys"] = primary_keys["constrained_columns"]
                
                # Get foreign keys
                foreign_keys = inspector.get_foreign_keys(table_name)
                table_info["foreign_keys"] = foreign_keys
                
                # Get indexes
                indexes = inspector.get_indexes(table_name)
                table_info["indexes"] = indexes
                
                schema_info["tables"].append(table_info)
            
            return schema_info
            
        except Exception as e:
            return {
                "error": f"Failed to get schema: {str(e)}",
                "tables": [],
                "total_tables": 0
            }
    
    async def _analyze_table_data(self, engine: Engine, table_name: str,
                                 columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze data in a table.
        
        Args:
            engine: Database engine
            table_name: Name of the table
            columns: Specific columns to analyze
            
        Returns:
            Data analysis results
        """
        try:
            # Read table data
            if columns:
                query = f"SELECT {', '.join(columns)} FROM {table_name}"
            else:
                query = f"SELECT * FROM {table_name}"
            
            df = pd.read_sql(query, engine)
            
            if df.empty:
                return {
                    "table_name": table_name,
                    "total_rows": 0,
                    "total_columns": 0,
                    "analysis": "No data to analyze"
                }
            
            analysis = {
                "table_name": table_name,
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "columns": {}
            }
            
            # Analyze each column
            for column in df.columns:
                col_data = df[column]
                col_analysis = {
                    "data_type": str(col_data.dtype),
                    "null_count": col_data.isnull().sum(),
                    "null_percentage": (col_data.isnull().sum() / len(col_data)) * 100
                }
                
                # Numeric analysis
                if pd.api.types.is_numeric_dtype(col_data):
                    col_analysis.update({
                        "min": float(col_data.min()) if not col_data.isnull().all() else None,
                        "max": float(col_data.max()) if not col_data.isnull().all() else None,
                        "mean": float(col_data.mean()) if not col_data.isnull().all() else None,
                        "median": float(col_data.median()) if not col_data.isnull().all() else None,
                        "std": float(col_data.std()) if not col_data.isnull().all() else None
                    })
                
                # Categorical analysis
                elif pd.api.types.is_object_dtype(col_data):
                    unique_values = col_data.nunique()
                    col_analysis.update({
                        "unique_values": int(unique_values),
                        "most_common": col_data.value_counts().head(5).to_dict() if unique_values > 0 else {}
                    })
                
                analysis["columns"][column] = col_analysis
            
            return analysis
            
        except Exception as e:
            return {
                "error": f"Failed to analyze table data: {str(e)}",
                "table_name": table_name
            }
    
    async def _optimize_sql_query(self, engine: Engine, query: str) -> Dict[str, Any]:
        """
        Optimize SQL query.
        
        Args:
            engine: Database engine
            query: SQL query to optimize
            
        Returns:
            Query optimization results
        """
        try:
            # Basic query analysis
            analysis = {
                "original_query": query,
                "suggestions": [],
                "estimated_impact": "low"
            }
            
            # Check for common optimization opportunities
            query_lower = query.lower()
            
            if "select *" in query_lower:
                analysis["suggestions"].append("Consider selecting only needed columns instead of SELECT *")
                analysis["estimated_impact"] = "medium"
            
            if "order by" in query_lower and "limit" not in query_lower:
                analysis["suggestions"].append("Consider adding LIMIT clause when using ORDER BY")
                analysis["estimated_impact"] = "medium"
            
            if "where" not in query_lower and "select" in query_lower:
                analysis["suggestions"].append("Consider adding WHERE clause to filter data")
                analysis["estimated_impact"] = "high"
            
            if "join" in query_lower and "on" not in query_lower:
                analysis["suggestions"].append("Ensure proper JOIN conditions are specified")
                analysis["estimated_impact"] = "high"
            
            # Check for potential index usage
            if "where" in query_lower:
                analysis["suggestions"].append("Ensure appropriate indexes exist for WHERE conditions")
            
            return analysis
            
        except Exception as e:
            return {
                "error": f"Failed to optimize query: {str(e)}",
                "original_query": query
            }
    
    async def _test_database_connection(self, database_name: str) -> Dict[str, Any]:
        """
        Test database connection.
        
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
                    "error": f"Database '{database_name}' not configured"
                }
            
            # Test connection with simple query
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
            
            return {
                "success": True,
                "database_name": database_name,
                "message": "Connection test successful"
            }
            
        except Exception as e:
            return {
                "success": False,
                "database_name": database_name,
                "error": str(e)
            }
    
    async def _test_database_connections(self) -> Dict[str, Any]:
        """
        Test all database connections.
        
        Returns:
            Connection test results
        """
        try:
            results = {}
            all_successful = True
            
            for database_name in self.database_configs.keys():
                result = await self._test_database_connection(database_name)
                results[database_name] = result
                
                if not result["success"]:
                    all_successful = False
            
            return {
                "success": all_successful,
                "results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def shutdown(self) -> None:
        """Shutdown the database service."""
        await super().shutdown()
        
        # Close all database connections
        for name, engine in self.connection_pool.items():
            try:
                engine.dispose()
                logger.info(f"Closed connection to database: {name}")
            except Exception as e:
                logger.error(f"Error closing connection to database '{name}': {e}")
        
        self.connection_pool.clear()
        logger.info("Database service shutdown complete") 