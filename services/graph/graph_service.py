"""
Graph Service

This module provides graph operations for the backend graph service.

# DEAD CODE - Candidate for deletion: This backend directory is not used by the main application
"""

import os
import logging
from typing import Dict, List, Any, Optional
from arango import ArangoClient
import requests

logger = logging.getLogger(__name__)

class GraphService:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.arango_url = os.getenv("ARANGO_URL", "http://localhost:8529")
        self.arango_db = os.getenv("ARANGO_DATABASE", "ukp")
        self.arango_username = os.getenv("ARANGO_USERNAME", "root")
        self.arango_password = os.getenv("ARANGO_PASSWORD", "")
        self.arango_client = None
        self.db = None
        self._initialize_graph_db()
    
    def _initialize_graph_db(self):
        """Initialize graph database connections."""
        try:
            # Initialize ArangoDB
            if self.arango_url:
                self.arango_client = ArangoClient(hosts=self.arango_url)
                # Try to connect to the database
                try:
                    self.db = self.arango_client.db(
                        self.arango_db,
                        username=self.arango_username,
                        password=self.arango_password
                    )
                    logger.info("ArangoDB connected successfully")
                except Exception as e:
                    logger.warning(f"Could not connect to ArangoDB: {e}")
            
        except Exception as e:
            logger.error(f"Error initializing graph database: {e}")
    
    async def create_node(self, node_data: Dict[str, Any]) -> Optional[str]:
        """Create a node in the knowledge graph."""
        try:
            if not self.db:
                raise ValueError("Graph database not initialized")
            
            collection_name = node_data.get("collection", "entities")
            collection = self.db.collection(collection_name)
            
            # Create the node
            result = collection.insert(node_data)
            node_id = result["_key"]
            
            logger.info(f"Created node {node_id} in collection {collection_name}")
            return node_id
        except Exception as e:
            logger.error(f"Error creating node: {e}")
            return None
    
    async def create_edge(self, edge_data: Dict[str, Any]) -> Optional[str]:
        """Create an edge in the knowledge graph."""
        try:
            if not self.db:
                raise ValueError("Graph database not initialized")
            
            collection_name = edge_data.get("collection", "relationships")
            collection = self.db.collection(collection_name)
            
            # Create the edge
            result = collection.insert(edge_data)
            edge_id = result["_key"]
            
            logger.info(f"Created edge {edge_id} in collection {collection_name}")
            return edge_id
        except Exception as e:
            logger.error(f"Error creating edge: {e}")
            return None
    
    async def query_graph(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Query the knowledge graph."""
        try:
            if not self.db:
                raise ValueError("Graph database not initialized")
            
            # Execute AQL query
            cursor = self.db.aql.execute(query, limit=limit)
            results = [doc for doc in cursor]
            
            logger.info(f"Graph query returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error querying graph: {e}")
            return []
    
    async def find_entities(self, entity_type: str = None, properties: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Find entities in the knowledge graph."""
        try:
            if not self.db:
                raise ValueError("Graph database not initialized")
            
            collection_name = "entities"
            collection = self.db.collection(collection_name)
            
            # Build filter
            filter_conditions = []
            if entity_type:
                filter_conditions.append(f"doc.type == '{entity_type}'")
            
            if properties:
                for key, value in properties.items():
                    filter_conditions.append(f"doc.{key} == '{value}'")
            
            filter_expr = " AND ".join(filter_conditions) if filter_conditions else "true"
            
            query = f"""
            FOR doc IN {collection_name}
            FILTER {filter_expr}
            RETURN doc
            """
            
            cursor = self.db.aql.execute(query)
            results = [doc for doc in cursor]
            
            logger.info(f"Found {len(results)} entities")
            return results
        except Exception as e:
            logger.error(f"Error finding entities: {e}")
            return []
    
    async def get_relationships(self, entity_id: str, relationship_type: str = None) -> List[Dict[str, Any]]:
        """Get relationships for an entity."""
        try:
            if not self.db:
                raise ValueError("Graph database not initialized")
            
            collection_name = "relationships"
            
            # Build query
            filter_expr = f"doc._from == '{entity_id}' OR doc._to == '{entity_id}'"
            if relationship_type:
                filter_expr += f" AND doc.type == '{relationship_type}'"
            
            query = f"""
            FOR doc IN {collection_name}
            FILTER {filter_expr}
            RETURN doc
            """
            
            cursor = self.db.aql.execute(query)
            results = [doc for doc in cursor]
            
            logger.info(f"Found {len(results)} relationships for entity {entity_id}")
            return results
        except Exception as e:
            logger.error(f"Error getting relationships: {e}")
            return []
    
    async def add_knowledge_triple(self, subject: str, predicate: str, object_value: str) -> bool:
        """Add a knowledge triple to the graph."""
        try:
            if not self.db:
                raise ValueError("Graph database not initialized")
            
            # Create subject node if it doesn't exist
            subject_id = await self.create_node({
                "name": subject,
                "type": "entity"
            })
            
            # Create object node if it doesn't exist
            object_id = await self.create_node({
                "name": object_value,
                "type": "entity"
            })
            
            # Create relationship
            edge_id = await self.create_edge({
                "_from": subject_id,
                "_to": object_id,
                "type": predicate,
                "relationship": predicate
            })
            
            logger.info(f"Added knowledge triple: {subject} {predicate} {object_value}")
            return True
        except Exception as e:
            logger.error(f"Error adding knowledge triple: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get service status."""
        return {
            "status": "healthy" if self.db else "unhealthy",
            "arango_configured": bool(self.arango_client),
            "database_connected": bool(self.db),
            "arango_url": self.arango_url,
            "database_name": self.arango_db
        }
    
    async def shutdown(self):
        """Shutdown the service."""
        logger.info("GraphService shutting down") 