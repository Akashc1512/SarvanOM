#!/usr/bin/env python3
"""
ArangoDB Service - Environment-Driven Knowledge Graph Connection

This service provides environment-driven configuration for ArangoDB connections
with health checks, warmup, and structured logging.

Key Features:
- Environment-driven configuration (no hardcoded values)
- Lightweight connection probe (≤300ms)
- Background warmup task with cache priming
- Structured logging with secret redaction
- Health endpoint integration
"""

import os
import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from contextlib import asynccontextmanager

try:
    from arango import ArangoClient
    from arango.database import StandardDatabase
    from arango.collection import StandardCollection
    ARANGO_AVAILABLE = True
except ImportError:
    ARANGO_AVAILABLE = False
    ArangoClient = None
    StandardDatabase = None
    StandardCollection = None

from shared.core.unified_logging import get_logger

logger = get_logger(__name__)

@dataclass
class ArangoDBConfig:
    """ArangoDB configuration from environment variables."""
    
    url: str
    username: str  
    password: str
    database: str
    connection_timeout: int
    query_timeout: int
    max_connection_pool_size: int
    
    @classmethod
    def from_environment(cls) -> 'ArangoDBConfig':
        """Load configuration from environment variables."""
        return cls(
            url=os.getenv("ARANGODB_URL", "http://localhost:8529"),
            username=os.getenv("ARANGODB_USERNAME", "root"),
            password=os.getenv("ARANGODB_PASSWORD", ""),
            database=os.getenv("ARANGODB_DATABASE", "sarvanom_kg"),
            connection_timeout=int(os.getenv("ARANGODB_CONNECTION_TIMEOUT", "10")),
            query_timeout=int(os.getenv("ARANGODB_QUERY_TIMEOUT", "30")), 
            max_connection_pool_size=int(os.getenv("ARANGODB_MAX_CONNECTIONS", "10"))
        )
    
    def get_redacted_config(self) -> Dict[str, Any]:
        """Get configuration with password redacted for logging."""
        return {
            "url": self.url,
            "username": self.username,
            "password": "***REDACTED***" if self.password else "***EMPTY***",
            "database": self.database,
            "connection_timeout": self.connection_timeout,
            "query_timeout": self.query_timeout,
            "max_connection_pool_size": self.max_connection_pool_size
        }


class ArangoDBService:
    """Production-ready ArangoDB service with environment-driven configuration."""
    
    def __init__(self, config: Optional[ArangoDBConfig] = None):
        """Initialize ArangoDB service with environment configuration."""
        self.config = config or ArangoDBConfig.from_environment()
        self.client: Optional[ArangoClient] = None
        self.db: Optional[StandardDatabase] = None
        self.connected = False
        self.warmup_completed = False
        self.last_health_check = 0
        self.connection_start_time = 0
        
        if not ARANGO_AVAILABLE:
            logger.warning("ArangoDB client not available - install python-arango package")
            return
            
        logger.info("ArangoDB service initialized", config=self.config.get_redacted_config())
    
    async def connect(self) -> bool:
        """
        Connect to ArangoDB with lightweight probe (≤300ms timeout).
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not ARANGO_AVAILABLE:
            logger.error("ArangoDB client not available")
            return False
            
        if self.connected:
            return True
            
        self.connection_start_time = time.time()
        
        try:
            # Create client with timeout
            self.client = ArangoClient(
                hosts=self.config.url,
                request_timeout=min(self.config.connection_timeout, 0.3)  # Max 300ms for probe
            )
            
            # Lightweight connection probe
            connection_probe_start = time.time()
            
            # Connect to database
            self.db = self.client.db(
                name=self.config.database,
                username=self.config.username,
                password=self.config.password
            )
            
            # Quick connection test with timeout
            probe_timeout = 0.3  # 300ms max
            try:
                await asyncio.wait_for(
                    self._test_connection_probe(),
                    timeout=probe_timeout
                )
            except asyncio.TimeoutError:
                logger.error("ArangoDB connection probe timed out", timeout_ms=probe_timeout * 1000)
                return False
            
            connection_time_ms = (time.time() - connection_probe_start) * 1000
            
            self.connected = True
            self.last_health_check = time.time()
            
            logger.info(
                "ArangoDB connection established",
                url=self.config.url,
                database=self.config.database,
                connection_time_ms=round(connection_time_ms, 2)
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Failed to connect to ArangoDB",
                error=str(e),
                url=self.config.url,
                database=self.config.database
            )
            self.connected = False
            return False
    
    async def _test_connection_probe(self) -> None:
        """Lightweight connection probe - quick test query."""
        try:
            # Simple query to test connection
            result = self.db.aql.execute("RETURN 1", count=True)
            test_result = list(result)
            
            if not test_result or test_result[0] != 1:
                raise ConnectionError("ArangoDB probe query failed")
                
        except Exception as e:
            raise ConnectionError(f"ArangoDB connection probe failed: {e}")
    
    async def ensure_collections(self) -> bool:
        """
        Ensure required collections exist with proper indexes.
        
        Returns:
            bool: True if collections created/verified, False otherwise
        """
        if not self.connected:
            logger.warning("ArangoDB not connected - cannot ensure collections")
            return False
            
        try:
            # Create entities collection if not exists
            if not self.db.has_collection("entities"):
                entities_col = self.db.create_collection("entities")
                logger.info("Created entities collection")
            else:
                entities_col = self.db.collection("entities")
            
            # Create relationships edge collection if not exists  
            if not self.db.has_collection("relationships"):
                relationships_col = self.db.create_collection("relationships", edge=True)
                logger.info("Created relationships edge collection")
            else:
                relationships_col = self.db.collection("relationships")
            
            return True
            
        except Exception as e:
            logger.error("Failed to ensure ArangoDB collections", error=str(e))
            return False
    
    async def create_indexes(self) -> bool:
        """
        Create performance indexes if missing.
        
        Returns:
            bool: True if indexes created, False otherwise
        """
        if not self.connected:
            return False
            
        try:
            entities_col = self.db.collection("entities")
            relationships_col = self.db.collection("relationships")
            
            # Create indexes for entities
            existing_indexes = {idx['fields'][0] for idx in entities_col.indexes() 
                              if idx['type'] == 'persistent' and len(idx['fields']) == 1}
            
            if 'name' not in existing_indexes:
                entities_col.add_index({'fields': ['name'], 'type': 'persistent'})
                logger.info("Created entities.name index")
                
            if 'type' not in existing_indexes:
                entities_col.add_index({'fields': ['type'], 'type': 'persistent'})
                logger.info("Created entities.type index")
            
            # Create indexes for relationships
            rel_existing_indexes = {idx['fields'][0] for idx in relationships_col.indexes()
                                   if idx['type'] == 'persistent' and len(idx['fields']) == 1}
            
            if 'type' not in rel_existing_indexes:
                relationships_col.add_index({'fields': ['type'], 'type': 'persistent'})
                logger.info("Created relationships.type index")
            
            return True
            
        except Exception as e:
            logger.error("Failed to create ArangoDB indexes", error=str(e))
            return False
    
    async def warmup_cache(self) -> bool:
        """
        Background warmup task - run trivial AQL to prime caches.
        
        Returns:
            bool: True if warmup successful, False otherwise
        """
        if not self.connected:
            return False
            
        try:
            warmup_start = time.time()
            
            # Run a few cache-priming queries
            warmup_queries = [
                "RETURN 1",
                "FOR e IN entities LIMIT 1 RETURN e",
                "FOR r IN relationships LIMIT 1 RETURN r",
                "RETURN LENGTH(entities)",
                "RETURN LENGTH(relationships)"
            ]
            
            for query in warmup_queries:
                try:
                    result = self.db.aql.execute(query, count=True)
                    # Consume the cursor to ensure query executes
                    list(result)
                except Exception as e:
                    logger.debug(f"Warmup query failed (expected): {query}", error=str(e))
                    continue
                    
            warmup_time_ms = (time.time() - warmup_start) * 1000
            self.warmup_completed = True
            
            logger.info(
                "ArangoDB cache warmup completed",
                warmup_time_ms=round(warmup_time_ms, 2)
            )
            
            return True
            
        except Exception as e:
            logger.error("ArangoDB warmup failed", error=str(e))
            return False
    
    async def start_background_warmup(self) -> None:
        """Start background warmup task after connection."""
        if not self.connected:
            return
            
        async def warmup_task():
            # Wait a bit for main connection to stabilize
            await asyncio.sleep(1)
            
            # Ensure collections and indexes
            await self.ensure_collections()
            await self.create_indexes()
            
            # Prime caches
            await self.warmup_cache()
        
        # Start warmup task in background
        asyncio.create_task(warmup_task())
        logger.info("Started ArangoDB background warmup task")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for /health endpoint.
        
        Returns:
            Dict with health status information
        """
        if not ARANGO_AVAILABLE:
            return {
                "status": "error",
                "message": "ArangoDB client not available",
                "available": False
            }
            
        if not self.connected:
            return {
                "status": "error", 
                "message": "Not connected",
                "available": False
            }
        
        try:
            # Quick health probe
            health_start = time.time()
            result = self.db.aql.execute("RETURN 1")
            list(result)  # Consume cursor
            health_time_ms = (time.time() - health_start) * 1000
            
            self.last_health_check = time.time()
            
            # Get collection counts
            entities_count = 0
            relationships_count = 0
            
            try:
                if self.db.has_collection("entities"):
                    entities_count = self.db.collection("entities").count()
                if self.db.has_collection("relationships"):
                    relationships_count = self.db.collection("relationships").count()
            except Exception:
                pass  # Counts are optional for health check
            
            return {
                "status": "ok",
                "available": True,
                "response_time_ms": round(health_time_ms, 2),
                "database": self.config.database,
                "entities_count": entities_count,
                "relationships_count": relationships_count,
                "warmup_completed": self.warmup_completed,
                "last_check": self.last_health_check
            }
            
        except Exception as e:
            logger.error("ArangoDB health check failed", error=str(e))
            return {
                "status": "error",
                "message": str(e),
                "available": False
            }
    
    async def execute_aql(self, query: str, bind_vars: Optional[Dict] = None, 
                         timeout: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Execute AQL query with timeout.
        
        Args:
            query: AQL query string
            bind_vars: Query bind variables
            timeout: Query timeout in seconds
            
        Returns:
            List of query results
        """
        if not self.connected:
            raise ConnectionError("ArangoDB not connected")
            
        query_timeout = timeout or self.config.query_timeout
        
        try:
            query_start = time.time()
            
            # Execute with timeout
            cursor = self.db.aql.execute(
                query, 
                bind_vars=bind_vars or {},
                count=True,
                batch_size=1000
            )
            
            # Convert cursor to list with timeout
            results = []
            async def execute_query():
                nonlocal results
                results = list(cursor)
            
            await asyncio.wait_for(execute_query(), timeout=query_timeout)
            
            query_time_ms = (time.time() - query_start) * 1000
            
            logger.debug(
                "AQL query executed",
                query=query[:100] + "..." if len(query) > 100 else query,
                result_count=len(results),
                query_time_ms=round(query_time_ms, 2)
            )
            
            return results
            
        except asyncio.TimeoutError:
            logger.error("AQL query timed out", query=query[:100], timeout=query_timeout)
            raise TimeoutError(f"AQL query timed out after {query_timeout}s")
        except Exception as e:
            logger.error("AQL query failed", query=query[:100], error=str(e))
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from ArangoDB."""
        if self.client:
            try:
                # ArangoDB client doesn't need explicit disconnect
                self.connected = False
                self.client = None
                self.db = None
                logger.info("Disconnected from ArangoDB")
            except Exception as e:
                logger.error("Error disconnecting from ArangoDB", error=str(e))
    
    @asynccontextmanager
    async def get_connection(self):
        """Context manager for ArangoDB operations."""
        if not self.connected:
            await self.connect()
            
        try:
            yield self.db
        finally:
            # Connection stays open for reuse
            pass


# Global service instance
_arangodb_service: Optional[ArangoDBService] = None

async def get_arangodb_service() -> ArangoDBService:
    """Get or create global ArangoDB service instance."""
    global _arangodb_service
    
    if _arangodb_service is None:
        _arangodb_service = ArangoDBService()
        await _arangodb_service.connect()
        await _arangodb_service.start_background_warmup()
    
    return _arangodb_service

async def get_arangodb_health() -> Dict[str, Any]:
    """Get ArangoDB health status for /health endpoint."""
    try:
        service = await get_arangodb_service()
        return await service.health_check()
    except Exception as e:
        logger.error("Failed to get ArangoDB health", error=str(e))
        return {
            "status": "error",
            "message": str(e),
            "available": False
        }
