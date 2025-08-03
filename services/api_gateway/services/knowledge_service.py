"""
Knowledge Service

This service handles knowledge graph queries and operations for the knowledge agent.
It provides entity queries, relationship exploration, and graph analysis capabilities.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime
import json
import networkx as nx
from collections import defaultdict

from .base_service import BaseAgentService, ServiceType, ServiceStatus

logger = logging.getLogger(__name__)


class KnowledgeService(BaseAgentService):
    """
    Knowledge service for graph database queries and operations.
    
    This service provides knowledge graph querying, entity exploration,
    and relationship analysis capabilities for the knowledge agent.
    """
    
    def __init__(self, service_type: ServiceType, config: Optional[Dict[str, Any]] = None):
        """Initialize the knowledge service."""
        super().__init__(service_type, config)
        self.graph_db_url = self.get_config("graph_db_url", "http://localhost:8529")
        self.database_name = self.get_config("database_name", "knowledge_graph")
        self.username = self.get_config("username", "root")
        self.password = self.get_config("password", "")
        self.max_results = self.get_config("max_results", 100)
        self.timeout = self.get_config("timeout", 30)
        self.cache_enabled = self.get_config("cache_enabled", True)
        self.cache_ttl = self.get_config("cache_ttl", 3600)  # 1 hour
        
        # In-memory cache for query results
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        
        logger.info("Knowledge service initialized")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check knowledge service health.
        
        Returns:
            Health status and metrics
        """
        try:
            # Test database connectivity
            test_result = await self._test_database_connection()
            
            if test_result["success"]:
                self.update_status(ServiceStatus.HEALTHY)
                return {
                    "healthy": True,
                    "database_connection": "OK",
                    "graph_db_url": self.graph_db_url,
                    "database_name": self.database_name,
                    "cache_enabled": self.cache_enabled,
                    "max_results": self.max_results
                }
            else:
                self.update_status(ServiceStatus.DEGRADED)
                return {
                    "healthy": False,
                    "database_connection": "FAILED",
                    "error": test_result.get("error", "Unknown error")
                }
                
        except Exception as e:
            self.update_status(ServiceStatus.UNHEALTHY)
            logger.error(f"Knowledge service health check failed: {e}")
            return {
                "healthy": False,
                "database_connection": "FAILED",
                "error": str(e)
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get detailed knowledge service status.
        
        Returns:
            Service status information
        """
        health_info = await self.health_check()
        service_info = self.get_service_info()
        
        return {
            **service_info,
            **health_info,
            "capabilities": {
                "entity_queries": True,
                "relationship_queries": True,
                "graph_analysis": True,
                "path_finding": True,
                "subgraph_extraction": True
            },
            "configuration": {
                "graph_db_url": self.graph_db_url,
                "database_name": self.database_name,
                "max_results": self.max_results,
                "cache_enabled": self.cache_enabled,
                "cache_ttl": self.cache_ttl
            }
        }
    
    async def validate_config(self) -> bool:
        """
        Validate knowledge service configuration.
        
        Returns:
            True if configuration is valid
        """
        try:
            # Check required configuration
            if not self.graph_db_url:
                logger.error("Knowledge service: No graph database URL configured")
                return False
            
            if not self.database_name:
                logger.error("Knowledge service: No database name configured")
                return False
            
            if self.max_results <= 0:
                logger.error("Knowledge service: Invalid max_results value")
                return False
            
            if self.timeout <= 0:
                logger.error("Knowledge service: Invalid timeout value")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Knowledge service config validation failed: {e}")
            return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get knowledge service performance metrics.
        
        Returns:
            Performance metrics
        """
        base_metrics = self.get_service_info()
        
        # Add knowledge-specific metrics
        knowledge_metrics = {
            "queries_executed": 0,  # TODO: Track actual queries
            "entities_retrieved": 0,  # TODO: Track entities retrieved
            "relationships_found": 0,  # TODO: Track relationships found
            "cache_hits": 0,  # TODO: Track cache performance
            "cache_misses": 0,  # TODO: Track cache misses
            "average_query_time": 0.0,  # TODO: Track query times
            "success_rate": 1.0 if self.error_count == 0 else 0.0
        }
        
        return {**base_metrics, **knowledge_metrics}
    
    async def query_entities(self, entity_type: Optional[str] = None, 
                           properties: Optional[Dict[str, Any]] = None,
                           limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Query entities from the knowledge graph.
        
        Args:
            entity_type: Type of entities to query
            properties: Property filters
            limit: Maximum number of results
            
        Returns:
            Query results
        """
        await self.pre_request()
        
        try:
            cache_key = f"entities:{entity_type}:{json.dumps(properties, sort_keys=True)}:{limit}"
            
            # Check cache first
            if self.cache_enabled:
                cached_result = self._get_cached_result(cache_key)
                if cached_result:
                    await self.post_request(success=True)
                    return cached_result
            
            # Execute query
            query = self._build_entity_query(entity_type, properties, limit or self.max_results)
            result = await self._execute_query(query)
            
            # Cache result
            if self.cache_enabled:
                self._cache_result(cache_key, result)
            
            await self.post_request(success=True)
            return result
            
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Entity query failed: {e}")
            raise
    
    async def query_relationships(self, source_entity: Optional[str] = None,
                               target_entity: Optional[str] = None,
                               relationship_type: Optional[str] = None,
                               limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Query relationships from the knowledge graph.
        
        Args:
            source_entity: Source entity identifier
            target_entity: Target entity identifier
            relationship_type: Type of relationship
            limit: Maximum number of results
            
        Returns:
            Query results
        """
        await self.pre_request()
        
        try:
            cache_key = f"relationships:{source_entity}:{target_entity}:{relationship_type}:{limit}"
            
            # Check cache first
            if self.cache_enabled:
                cached_result = self._get_cached_result(cache_key)
                if cached_result:
                    await self.post_request(success=True)
                    return cached_result
            
            # Execute query
            query = self._build_relationship_query(source_entity, target_entity, 
                                                 relationship_type, limit or self.max_results)
            result = await self._execute_query(query)
            
            # Cache result
            if self.cache_enabled:
                self._cache_result(cache_key, result)
            
            await self.post_request(success=True)
            return result
            
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Relationship query failed: {e}")
            raise
    
    async def find_paths(self, source_entity: str, target_entity: str,
                        max_paths: int = 5, max_length: int = 5) -> Dict[str, Any]:
        """
        Find paths between entities in the knowledge graph.
        
        Args:
            source_entity: Source entity identifier
            target_entity: Target entity identifier
            max_paths: Maximum number of paths to find
            max_length: Maximum path length
            
        Returns:
            Path finding results
        """
        await self.pre_request()
        
        try:
            cache_key = f"paths:{source_entity}:{target_entity}:{max_paths}:{max_length}"
            
            # Check cache first
            if self.cache_enabled:
                cached_result = self._get_cached_result(cache_key)
                if cached_result:
                    await self.post_request(success=True)
                    return cached_result
            
            # Execute path finding
            query = self._build_path_query(source_entity, target_entity, max_paths, max_length)
            result = await self._execute_query(query)
            
            # Cache result
            if self.cache_enabled:
                self._cache_result(cache_key, result)
            
            await self.post_request(success=True)
            return result
            
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Path finding failed: {e}")
            raise
    
    async def analyze_subgraph(self, entities: List[str], 
                             include_neighbors: bool = True,
                             max_depth: int = 2) -> Dict[str, Any]:
        """
        Analyze a subgraph around specified entities.
        
        Args:
            entities: List of entity identifiers
            include_neighbors: Whether to include neighboring entities
            max_depth: Maximum depth for neighbor inclusion
            
        Returns:
            Subgraph analysis results
        """
        await self.pre_request()
        
        try:
            cache_key = f"subgraph:{json.dumps(entities, sort_keys=True)}:{include_neighbors}:{max_depth}"
            
            # Check cache first
            if self.cache_enabled:
                cached_result = self._get_cached_result(cache_key)
                if cached_result:
                    await self.post_request(success=True)
                    return cached_result
            
            # Execute subgraph analysis
            query = self._build_subgraph_query(entities, include_neighbors, max_depth)
            result = await self._execute_query(query)
            
            # Cache result
            if self.cache_enabled:
                self._cache_result(cache_key, result)
            
            await self.post_request(success=True)
            return result
            
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Subgraph analysis failed: {e}")
            raise
    
    async def get_entity_details(self, entity_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific entity.
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            Entity details
        """
        await self.pre_request()
        
        try:
            cache_key = f"entity_details:{entity_id}"
            
            # Check cache first
            if self.cache_enabled:
                cached_result = self._get_cached_result(cache_key)
                if cached_result:
                    await self.post_request(success=True)
                    return cached_result
            
            # Execute entity details query
            query = self._build_entity_details_query(entity_id)
            result = await self._execute_query(query)
            
            # Cache result
            if self.cache_enabled:
                self._cache_result(cache_key, result)
            
            await self.post_request(success=True)
            return result
            
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Entity details query failed: {e}")
            raise
    
    async def search_entities(self, search_term: str, 
                            entity_types: Optional[List[str]] = None,
                            limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Search for entities by name or properties.
        
        Args:
            search_term: Search term
            entity_types: Types of entities to search
            limit: Maximum number of results
            
        Returns:
            Search results
        """
        await self.pre_request()
        
        try:
            cache_key = f"search:{search_term}:{json.dumps(entity_types, sort_keys=True)}:{limit}"
            
            # Check cache first
            if self.cache_enabled:
                cached_result = self._get_cached_result(cache_key)
                if cached_result:
                    await self.post_request(success=True)
                    return cached_result
            
            # Execute search query
            query = self._build_search_query(search_term, entity_types, limit or self.max_results)
            result = await self._execute_query(query)
            
            # Cache result
            if self.cache_enabled:
                self._cache_result(cache_key, result)
            
            await self.post_request(success=True)
            return result
            
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Entity search failed: {e}")
            raise
    
    def _build_entity_query(self, entity_type: Optional[str], 
                           properties: Optional[Dict[str, Any]], 
                           limit: int) -> str:
        """Build entity query."""
        query_parts = ["FOR entity IN entities"]
        
        if entity_type:
            query_parts.append(f"FILTER entity.type == '{entity_type}'")
        
        if properties:
            for key, value in properties.items():
                if isinstance(value, str):
                    query_parts.append(f"FILTER entity.{key} == '{value}'")
                else:
                    query_parts.append(f"FILTER entity.{key} == {value}")
        
        query_parts.append(f"LIMIT {limit}")
        query_parts.append("RETURN entity")
        
        return " ".join(query_parts)
    
    def _build_relationship_query(self, source_entity: Optional[str],
                                target_entity: Optional[str],
                                relationship_type: Optional[str],
                                limit: int) -> str:
        """Build relationship query."""
        query_parts = ["FOR rel IN relationships"]
        
        if source_entity:
            query_parts.append(f"FILTER rel.source == '{source_entity}'")
        
        if target_entity:
            query_parts.append(f"FILTER rel.target == '{target_entity}'")
        
        if relationship_type:
            query_parts.append(f"FILTER rel.type == '{relationship_type}'")
        
        query_parts.append(f"LIMIT {limit}")
        query_parts.append("RETURN rel")
        
        return " ".join(query_parts)
    
    def _build_path_query(self, source_entity: str, target_entity: str,
                         max_paths: int, max_length: int) -> str:
        """Build path finding query."""
        return f"""
        FOR path IN OUTBOUND SHORTEST_PATH
        '{source_entity}' TO '{target_entity}'
        GRAPH 'knowledge_graph'
        OPTIONS {{weightAttribute: 'weight', defaultWeight: 1}}
        LIMIT {max_paths}
        RETURN path
        """
    
    def _build_subgraph_query(self, entities: List[str],
                             include_neighbors: bool,
                             max_depth: int) -> str:
        """Build subgraph query."""
        entity_list = ", ".join([f"'{entity}'" for entity in entities])
        
        if include_neighbors:
            return f"""
            FOR entity IN [{entity_list}]
            FOR neighbor IN 1..{max_depth} ANY entity
            GRAPH 'knowledge_graph'
            RETURN DISTINCT neighbor
            """
        else:
            return f"""
            FOR entity IN [{entity_list}]
            RETURN entity
            """
    
    def _build_entity_details_query(self, entity_id: str) -> str:
        """Build entity details query."""
        return f"""
        FOR entity IN entities
        FILTER entity._id == '{entity_id}'
        LET relationships = (
            FOR rel IN relationships
            FILTER rel.source == '{entity_id}' OR rel.target == '{entity_id}'
            RETURN rel
        )
        RETURN {{
            entity: entity,
            relationships: relationships
        }}
        """
    
    def _build_search_query(self, search_term: str,
                           entity_types: Optional[List[str]],
                           limit: int) -> str:
        """Build search query."""
        query_parts = ["FOR entity IN entities"]
        
        # Add search filter
        query_parts.append(f"FILTER CONTAINS(LOWER(entity.name), LOWER('{search_term}'))")
        
        if entity_types:
            type_filter = " OR ".join([f"entity.type == '{t}'" for t in entity_types])
            query_parts.append(f"FILTER ({type_filter})")
        
        query_parts.append(f"LIMIT {limit}")
        query_parts.append("RETURN entity")
        
        return " ".join(query_parts)
    
    async def _execute_query(self, query: str) -> Dict[str, Any]:
        """
        Execute a query against the knowledge graph database.
        
        Args:
            query: Query string
            
        Returns:
            Query results
        """
        # TODO: Implement actual database connection and query execution
        # For now, return mock data
        return {
            "query": query,
            "results": [],
            "count": 0,
            "execution_time": 0.0,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _test_database_connection(self) -> Dict[str, Any]:
        """
        Test database connectivity.
        
        Returns:
            Connection test results
        """
        try:
            # TODO: Implement actual database connection test
            # For now, return mock success
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached result if available and not expired.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached result or None
        """
        if cache_key not in self._cache:
            return None
        
        result, timestamp = self._cache[cache_key]
        age = (datetime.now() - timestamp).total_seconds()
        
        if age > self.cache_ttl:
            del self._cache[cache_key]
            return None
        
        return result
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]) -> None:
        """
        Cache a query result.
        
        Args:
            cache_key: Cache key
            result: Result to cache
        """
        self._cache[cache_key] = (result, datetime.now())
        
        # Clean up old cache entries
        current_time = datetime.now()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if (current_time - timestamp).total_seconds() > self.cache_ttl
        ]
        
        for key in expired_keys:
            del self._cache[key]
    
    async def shutdown(self) -> None:
        """Shutdown the knowledge service."""
        await super().shutdown()
        
        # Clear cache
        self._cache.clear()
        
        logger.info("Knowledge service shutdown complete") 