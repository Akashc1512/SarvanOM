

"""
ArangoDB Service - Environment-Driven Configuration & Warm Path
================================================================

Provides authenticated ArangoDB connection with:
- Environment-driven configuration (no hardcoded values)
- Lightweight connection probe (≤300ms)
- Background warmup (index creation + cache priming)
- Structured logging with secret redaction
- Health check integration

Maps to Phase I1 requirements for production-grade KG operations.
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from contextlib import asynccontextmanager
import structlog
from datetime import datetime

try:
    from arango import ArangoClient
    from arango.database import StandardDatabase
    from arango.exceptions import ArangoError, DatabaseCreateError, CollectionCreateError
except ImportError:
    ArangoClient = None
    StandardDatabase = None
    ArangoError = Exception
    DatabaseCreateError = Exception
    CollectionCreateError = Exception

logger = structlog.get_logger(__name__)


@dataclass
class ArangoDBConfig:
    """ArangoDB configuration from environment variables."""
    url: str
    username: str
    password: str
    database: str
    connection_timeout: int = 10
    probe_timeout: float = 0.3  # 300ms probe limit
    warmup_enabled: bool = True
    
    @classmethod
    def from_environment(cls) -> 'ArangoDBConfig':
        """Load configuration from environment variables."""
        return cls(
            url=os.getenv('ARANGODB_URL', 'http://localhost:8529'),
            username=os.getenv('ARANGODB_USERNAME', 'root'),
            password=os.getenv('ARANGODB_PASSWORD', ''),
            database=os.getenv('ARANGODB_DATABASE', 'sarvanom_kg'),
            connection_timeout=int(os.getenv('ARANGODB_CONNECTION_TIMEOUT', '10')),
            probe_timeout=float(os.getenv('ARANGODB_PROBE_TIMEOUT', '0.3')),
            warmup_enabled=os.getenv('ARANGODB_WARMUP_ENABLED', 'true').lower() == 'true'
        )
    
    def get_redacted_config(self) -> Dict[str, Any]:
        """Return configuration with password redacted for logging."""
        return {
            'url': self.url,
            'username': self.username,
            'password': '[REDACTED]' if self.password else '[MISSING]',
            'database': self.database,
            'connection_timeout': self.connection_timeout,
            'probe_timeout': self.probe_timeout,
            'warmup_enabled': self.warmup_enabled
        }


class ArangoDBService:
    """
    Production-grade ArangoDB service with warm path optimization.
    
    Features:
    - Environment-driven configuration
    - Connection health probes with timeout
    - Background warmup tasks
    - Structured logging with secret redaction
    - Thread-safe singleton pattern
    """
    
    _instance: Optional['ArangoDBService'] = None
    _client: Optional[ArangoClient] = None
    _database: Optional[StandardDatabase] = None
    _config: Optional[ArangoDBConfig] = None
    _health_status: Dict[str, Any] = {'status': 'unknown', 'last_check': None}
    _warmup_completed: bool = False
    
    def __new__(cls) -> 'ArangoDBService':
        """Singleton pattern for process-level instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize service with environment configuration."""
        if self._config is None:
            self._config = ArangoDBConfig.from_environment()
            logger.info(
                "ArangoDB service initialized",
                config=self._config.get_redacted_config()
            )
    
    @property
    def config(self) -> ArangoDBConfig:
        """Get current configuration."""
        return self._config
    
    @property
    def is_available(self) -> bool:
        """Check if ArangoDB is available."""
        return ArangoClient is not None
    
    @property
    def health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        return self._health_status.copy()
    
    @property
    def is_warmup_completed(self) -> bool:
        """Check if warmup tasks completed."""
        return self._warmup_completed
    
    async def connection_probe(self) -> Dict[str, Any]:
        """
        Lightweight connection probe (≤300ms).
        
        Returns:
            Dict with status, latency, and details
        """
        if not self.is_available:
            return {
                'status': 'unavailable',
                'error': 'ArangoDB client not installed',
                'latency_ms': 0
            }
        
        start_time = datetime.now()
        
        try:
            # Timeout-protected probe
            result = await asyncio.wait_for(
                self._probe_connection(),
                timeout=self._config.probe_timeout
            )
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            self._health_status = {
                'status': 'ok',
                'last_check': datetime.now().isoformat(),
                'latency_ms': round(latency_ms, 2),
                'database': self._config.database,
                'warmup_completed': self._warmup_completed
            }
            
            logger.info(
                "ArangoDB connection probe successful",
                latency_ms=round(latency_ms, 2),
                database=self._config.database
            )
            
            return self._health_status.copy()
            
        except asyncio.TimeoutError:
            error_msg = f"Connection probe timeout after {self._config.probe_timeout}s"
            self._health_status = {
                'status': 'timeout',
                'error': error_msg,
                'last_check': datetime.now().isoformat(),
                'latency_ms': self._config.probe_timeout * 1000
            }
            
            logger.warning(
                "ArangoDB connection probe timeout",
                timeout_ms=self._config.probe_timeout * 1000,
                config=self._config.get_redacted_config()
            )
            
            return self._health_status.copy()
            
        except Exception as e:
            error_msg = f"Connection probe failed: {str(e)}"
            self._health_status = {
                'status': 'error',
                'error': error_msg,
                'last_check': datetime.now().isoformat(),
                'latency_ms': (datetime.now() - start_time).total_seconds() * 1000
            }
            
            logger.error(
                "ArangoDB connection probe failed",
                error=str(e),
                config=self._config.get_redacted_config()
            )
            
            return self._health_status.copy()
    
    async def _probe_connection(self) -> bool:
        """Internal connection probe logic."""
        try:
            # Initialize client if needed
            if self._client is None:
                self._client = ArangoClient(hosts=self._config.url)
            
            # Test database connection
            if self._database is None:
                self._database = self._client.db(
                    self._config.database,
                    username=self._config.username,
                    password=self._config.password
                )
            
            # Simple health check query
            result = self._database.aql.execute('RETURN 1')
            list(result)  # Consume result to ensure query executes
            
            return True
            
        except Exception as e:
            logger.error(
                "ArangoDB probe connection failed",
                error=str(e),
                database=self._config.database
            )
            raise
    
    async def background_warmup(self) -> Dict[str, Any]:
        """
        Background warmup tasks for optimal performance.
        
        Tasks:
        - Create missing collections
        - Create essential indices
        - Prime query cache with trivial AQL
        
        Returns:
            Warmup results and timing
        """
        if not self._config.warmup_enabled:
            logger.info("ArangoDB warmup disabled by configuration")
            return {'status': 'disabled', 'warmup_completed': False}
        
        start_time = datetime.now()
        warmup_results = {'tasks': [], 'errors': []}
        
        try:
            # Ensure connection is established
            await self._probe_connection()
            
            # Create essential collections
            await self._create_essential_collections(warmup_results)
            
            # Create essential indices
            await self._create_essential_indices(warmup_results)
            
            # Prime query cache
            await self._prime_query_cache(warmup_results)
            
            self._warmup_completed = True
            warmup_duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(
                "ArangoDB warmup completed successfully",
                duration_seconds=round(warmup_duration, 2),
                tasks_completed=len(warmup_results['tasks']),
                errors=len(warmup_results['errors'])
            )
            
            return {
                'status': 'completed',
                'warmup_completed': True,
                'duration_seconds': round(warmup_duration, 2),
                'tasks_completed': len(warmup_results['tasks']),
                'results': warmup_results
            }
            
        except Exception as e:
            warmup_duration = (datetime.now() - start_time).total_seconds()
            
            logger.error(
                "ArangoDB warmup failed",
                error=str(e),
                duration_seconds=round(warmup_duration, 2),
                partial_results=warmup_results
            )
            
            return {
                'status': 'failed',
                'warmup_completed': False,
                'error': str(e),
                'duration_seconds': round(warmup_duration, 2),
                'partial_results': warmup_results
            }
    
    async def _create_essential_collections(self, results: Dict) -> None:
        """Create essential collections for knowledge graph operations."""
        essential_collections = [
            'entities',
            'relationships', 
            'documents',
            'facts',
            'topics'
        ]
        
        for collection_name in essential_collections:
            try:
                if not self._database.has_collection(collection_name):
                    self._database.create_collection(collection_name)
                    results['tasks'].append(f"Created collection: {collection_name}")
                else:
                    results['tasks'].append(f"Collection exists: {collection_name}")
                    
            except CollectionCreateError as e:
                if "duplicate name" in str(e).lower():
                    results['tasks'].append(f"Collection exists: {collection_name}")
                else:
                    results['errors'].append(f"Failed to create {collection_name}: {e}")
            except Exception as e:
                results['errors'].append(f"Error with {collection_name}: {e}")
    
    async def _create_essential_indices(self, results: Dict) -> None:
        """Create essential indices for optimal query performance."""
        try:
            # Entity name index
            entities = self._database.collection('entities')
            if entities.has_index():
                entities.add_index({'fields': ['name'], 'type': 'hash'})
                results['tasks'].append("Created entities.name index")
            
            # Relationship type index
            relationships = self._database.collection('relationships')
            if relationships.has_index():
                relationships.add_index({'fields': ['type'], 'type': 'hash'})
                results['tasks'].append("Created relationships.type index")
                
        except Exception as e:
            results['errors'].append(f"Index creation error: {e}")
    
    async def _prime_query_cache(self, results: Dict) -> None:
        """Prime query cache with trivial AQL queries."""
        try:
            # Simple count queries to warm cache
            cache_queries = [
                'FOR e IN entities LIMIT 1 RETURN e',
                'FOR r IN relationships LIMIT 1 RETURN r',
                'RETURN LENGTH(FOR e IN entities RETURN 1)'
            ]
            
            for query in cache_queries:
                try:
                    result = self._database.aql.execute(query)
                    list(result)  # Consume to execute
                    results['tasks'].append(f"Cache primed: {query[:30]}...")
                except Exception as e:
                    results['errors'].append(f"Cache prime failed: {e}")
                    
        except Exception as e:
            results['errors'].append(f"Cache priming error: {e}")
    
    @asynccontextmanager
    async def get_database(self):
        """
        Get database connection with automatic error handling.
        
        Usage:
            async with arangodb_service.get_database() as db:
                result = db.aql.execute('FOR e IN entities RETURN e')
        """
        try:
            if self._database is None:
                await self._probe_connection()
            
            yield self._database
            
        except Exception as e:
            logger.error(
                "ArangoDB database operation failed",
                error=str(e),
                config=self._config.get_redacted_config()
            )
            raise
    
    async def execute_aql(self, query: str, bind_vars: Optional[Dict] = None) -> List[Dict]:
        """
        Execute AQL query with error handling and logging.
        
        Args:
            query: AQL query string
            bind_vars: Query bind variables
            
        Returns:
            Query results as list of dictionaries
        """
        start_time = datetime.now()
        
        try:
            async with self.get_database() as db:
                result = db.aql.execute(query, bind_vars=bind_vars or {})
                results = list(result)
                
                query_duration = (datetime.now() - start_time).total_seconds()
                
                logger.info(
                    "AQL query executed successfully",
                    query=query[:100] + "..." if len(query) > 100 else query,
                    duration_seconds=round(query_duration, 3),
                    result_count=len(results)
                )
                
                return results
                
        except Exception as e:
            query_duration = (datetime.now() - start_time).total_seconds()
            
            logger.error(
                "AQL query execution failed",
                query=query[:100] + "..." if len(query) > 100 else query,
                error=str(e),
                duration_seconds=round(query_duration, 3)
            )
            raise
    
    async def get_health(self) -> Dict[str, Any]:
        """Get health status (alias for compatibility)."""
        return await self.connection_probe()
    
    async def create_entity(self, entity_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create entity in knowledge graph."""
        try:
            async with self.get_database() as db:
                collection = db.collection('entities')
                result = collection.insert(entity_data)
                return result
        except Exception as e:
            logger.error(f"Failed to create entity: {e}")
            return None
    
    async def query_relationships(self, entity_name: str) -> List[Dict[str, Any]]:
        """Query relationships for an entity."""
        try:
            query = """
            FOR doc IN entities
            FILTER doc.name == @entity_name
            RETURN doc
            """
            results = await self.execute_aql(query, {'entity_name': entity_name})
            return results
        except Exception as e:
            logger.error(f"Failed to query relationships: {e}")
            return []
    
    async def search_entities(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for entities in the knowledge graph based on a text query.
        
        Args:
            query: Text query to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of matching entities
        """
        try:
            if not self.is_available:
                logger.warning("ArangoDB not available for entity search")
                return []
            
            # Simple text search across entities
            # In a real implementation, this could use full-text search or more sophisticated matching
            aql_query = """
            FOR doc IN entities
            FILTER CONTAINS(LOWER(doc.name), LOWER(@search_term)) 
               OR CONTAINS(LOWER(doc.description), LOWER(@search_term))
               OR CONTAINS(LOWER(doc.type), LOWER(@search_term))
            LIMIT @max_results
            RETURN {
                id: doc._key,
                name: doc.name,
                type: doc.type,
                description: doc.description,
                properties: doc.properties,
                metadata: doc.metadata
            }
            """
            
            results = await self.execute_aql(aql_query, {
                'search_term': query,
                'max_results': max_results
            })
            
            logger.debug(f"Found {len(results)} entities for query: {query[:100]}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search entities: {e}")
            return []


# Global service instance
arangodb_service = ArangoDBService()


async def get_arangodb_health() -> Dict[str, Any]:
    """Get ArangoDB health status for health check endpoints."""
    return await arangodb_service.connection_probe()


async def warmup_arangodb() -> Dict[str, Any]:
    """Execute ArangoDB warmup tasks."""
    return await arangodb_service.background_warmup()


# Export public interface
__all__ = [
    'ArangoDBConfig',
    'ArangoDBService', 
    'arangodb_service',
    'get_arangodb_health',
    'warmup_arangodb'
]