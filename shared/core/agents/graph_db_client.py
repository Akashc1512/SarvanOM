"""
Graph Database Client for ArangoDB
Handles low-level database connections and basic graph operations.
"""

import asyncio
import logging
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logging.warning("python-dotenv not available. Install with: pip install python-dotenv")

try:
    from arango import ArangoClient
    ARANGO_AVAILABLE = True
except ImportError:
    ARANGO_AVAILABLE = False
    logging.warning("ArangoDB driver not available. Install with: pip install python-arango")

logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """Represents a node in the graph database."""
    id: str
    name: str
    type: str
    properties: Dict[str, Any]
    confidence: float = 1.0


@dataclass
class GraphEdge:
    """Represents an edge in the graph database."""
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any]
    confidence: float = 1.0


class GraphDBClient:
    """
    Low-level client for ArangoDB graph operations.
    Handles connections, basic CRUD operations, and query execution.
    """
    
    def __init__(self):
        """Initialize the GraphDBClient."""
        # ArangoDB connection configuration
        self.arango_url = os.getenv("ARANGO_URL", "http://localhost:8529")
        self.arango_username = os.getenv("ARANGO_USERNAME", "root")
        self.arango_password = os.getenv("ARANGO_PASSWORD", "")
        self.arango_database = os.getenv("ARANGO_DATABASE", "knowledge_graph")
        
        # ArangoDB client
        self.client: Optional[ArangoClient] = None
        self.db = None
        self.connected = False
        
        # Initialize connection if ArangoDB is available
        if ARANGO_AVAILABLE:
            asyncio.create_task(self._initialize_connection())
        else:
            logger.warning("Using mock graph data - ArangoDB driver not available")
        
        logger.info("✅ GraphDBClient initialized successfully")
    
    async def _initialize_connection(self) -> None:
        """Initialize ArangoDB connection."""
        try:
            # Create ArangoDB client
            self.client = ArangoClient(hosts=self.arango_url)
            
            # Test connection
            await self._test_connection()
            self.connected = True
            logger.info(f"✅ Connected to ArangoDB at {self.arango_url}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to ArangoDB: {e}")
            self.connected = False
    
    async def _test_connection(self) -> None:
        """Test ArangoDB connection."""
        try:
            # Test connection by getting server info
            self.db = self.client.db(
                name=self.arango_database,
                username=self.arango_username,
                password=self.arango_password
            )
            
            # Test with a simple query
            result = self.db.aql.execute("RETURN 1")
            if not result:
                raise ConnectionError("ArangoDB connection test failed")
                
        except Exception as e:
            raise ConnectionError(f"ArangoDB connection test failed: {e}")
    
    async def create_constraints(self) -> bool:
        """Create database constraints for data integrity."""
        try:
            if not self.connected or not self.db:
                return False
            
            # Create collections if they don't exist
            if not self.db.has_collection("entities"):
                self.db.create_collection("entities")
            
            if not self.db.has_collection("relationships"):
                self.db.create_collection("relationships", edge=True)
            
            # Create indexes
            entities_collection = self.db.collection("entities")
            relationships_collection = self.db.collection("relationships")
            
            # Create indexes for better performance
            entities_collection.add_index("name", "persistent")
            entities_collection.add_index("type", "persistent")
            relationships_collection.add_index("type", "persistent")
            
            logger.info("✅ Created ArangoDB constraints and indexes")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create ArangoDB constraints: {e}")
            return False
    
    async def create_node(self, node_id: str, node_type: str, properties: Dict[str, Any]) -> bool:
        """Create a node in the graph database."""
        try:
            if not self.connected or not self.db:
                return False
            
            entities_collection = self.db.collection("entities")
            
            # Create node document
            node_doc = {
                "_key": node_id,
                "id": node_id,
                "type": node_type,
                **properties
            }
            
            entities_collection.insert(node_doc, overwrite=True)
            
            logger.debug(f"✅ Created graph node: {node_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create graph node {node_id}: {e}")
            return False
    
    async def create_edge(self, from_node_id: str, to_node_id: str, 
                         relationship_type: str, properties: Optional[Dict[str, Any]] = None) -> bool:
        """Create an edge between nodes in the graph database."""
        try:
            if not self.connected or not self.db:
                return False
            
            relationships_collection = self.db.collection("relationships")
            
            # Create edge document
            edge_doc = {
                "_from": f"entities/{from_node_id}",
                "_to": f"entities/{to_node_id}",
                "type": relationship_type,
                **(properties or {})
            }
            
            relationships_collection.insert(edge_doc)
            
            logger.debug(f"✅ Created graph edge: {from_node_id} --[{relationship_type}]--> {to_node_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create graph edge: {e}")
            return False
    
    async def execute_query(self, aql_query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute an AQL query on the graph database."""
        try:
            if not self.connected or not self.db:
                logger.warning("Cannot execute query - ArangoDB not connected")
                return []
            
            result = self.db.aql.execute(aql_query, parameters or {})
            return list(result)
            
        except Exception as e:
            logger.error(f"❌ Failed to execute AQL query: {e}")
            return []
    
    async def find_nodes_by_name(self, name: str, limit: int = 20) -> List[GraphNode]:
        """Find nodes by name using fuzzy matching."""
        try:
            aql_query = """
            FOR doc IN entities
            FILTER CONTAINS(LOWER(doc.name), LOWER(@name)) OR CONTAINS(LOWER(doc.id), LOWER(@name))
            RETURN doc
            LIMIT @limit
            """
            
            parameters = {"name": name, "limit": limit}
            result = await self.execute_query(aql_query, parameters)
            
            nodes = []
            for record in result:
                nodes.append(GraphNode(
                    id=record.get('id', ''),
                    name=record.get('name', ''),
                    type=record.get('type', 'Node'),
                    properties=record
                ))
            
            return nodes
            
        except Exception as e:
            logger.error(f"Failed to find nodes by name: {e}")
            return []
    
    async def find_relationships_between_nodes(self, node1_name: str, node2_name: str) -> List[GraphEdge]:
        """Find relationships between two nodes."""
        try:
            aql_query = """
            FOR rel IN relationships
            FOR entity1 IN entities
            FOR entity2 IN entities
            FILTER rel._from == entity1._id AND rel._to == entity2._id
            FILTER (CONTAINS(LOWER(entity1.name), LOWER(@entity1)) OR CONTAINS(LOWER(entity1.id), LOWER(@entity1)))
            AND (CONTAINS(LOWER(entity2.name), LOWER(@entity2)) OR CONTAINS(LOWER(entity2.id), LOWER(@entity2)))
            RETURN {entity1, rel, entity2}
            LIMIT 20
            """
            
            parameters = {"entity1": node1_name, "entity2": node2_name}
            result = await self.execute_query(aql_query, parameters)
            
            edges = []
            for record in result:
                if 'rel' in record:
                    rel = record['rel']
                    edges.append(GraphEdge(
                        source_id=rel.get('_from', ''),
                        target_id=rel.get('_to', ''),
                        relationship_type=rel.get('type', ''),
                        properties=rel
                    ))
            
            return edges
            
        except Exception as e:
            logger.error(f"Failed to find relationships between nodes: {e}")
            return []
    
    async def find_paths_between_nodes(self, start_node: str, end_node: str, max_depth: int = 3) -> List[List[GraphNode]]:
        """Find paths between two nodes."""
        try:
            aql_query = """
            FOR start IN entities
            FOR end IN entities
            FILTER (CONTAINS(LOWER(start.name), LOWER(@start)) OR CONTAINS(LOWER(start.id), LOWER(@start)))
            AND (CONTAINS(LOWER(end.name), LOWER(@end)) OR CONTAINS(LOWER(end.id), LOWER(@end)))
            FOR v, e, p IN 1..@max_depth OUTBOUND start relationships
            FILTER v._id == end._id
            SORT LENGTH(p.edges)
            LIMIT 5
            RETURN {path: p, start: start, end: end}
            """
            
            parameters = {
                "start": start_node,
                "end": end_node,
                "max_depth": max_depth
            }
            
            result = await self.execute_query(aql_query, parameters)
            
            paths = []
            for record in result:
                path = record['path']
                path_nodes = []
                
                # Extract nodes from path
                for vertex in path['vertices']:
                    node = GraphNode(
                        id=vertex.get('id', ''),
                        name=vertex.get('name', ''),
                        type=vertex.get('type', 'Node'),
                        properties=vertex
                    )
                    path_nodes.append(node)
                
                if path_nodes:
                    paths.append(path_nodes)
            
            return paths
            
        except Exception as e:
            logger.error(f"Failed to find paths between nodes: {e}")
            return []
    
    async def get_graph_statistics(self) -> Dict[str, Any]:
        """Get statistics about the graph database."""
        try:
            if not self.connected or not self.db:
                return {
                    "total_entities": 0,
                    "total_relationships": 0,
                    "connected": False
                }
            
            # Get entity count
            entity_count = self.db.aql.execute("RETURN LENGTH(FOR doc IN entities RETURN doc)")[0]
            
            # Get relationship count
            relationship_count = self.db.aql.execute("RETURN LENGTH(FOR doc IN relationships RETURN doc)")[0]
            
            # Get entity types distribution
            entity_types = self.db.aql.execute("""
                FOR doc IN entities
                COLLECT type = doc.type WITH COUNT INTO count
                RETURN {type: type, count: count}
            """)
            
            # Get relationship types distribution
            relationship_types = self.db.aql.execute("""
                FOR doc IN relationships
                COLLECT type = doc.type WITH COUNT INTO count
                RETURN {type: type, count: count}
            """)
            
            return {
                "total_entities": entity_count,
                "total_relationships": relationship_count,
                "entity_types": entity_types,
                "relationship_types": relationship_types,
                "connected": True,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get graph statistics: {e}")
            return {
                "error": str(e),
                "connected": self.connected
            }
    
    async def maintain_consistency(self) -> bool:
        """Maintain consistency of the graph database."""
        try:
            if not self.connected or not self.db:
                logger.warning("Cannot maintain consistency - ArangoDB not connected")
                return False
            
            # Remove orphaned relationships
            aql_query = """
            FOR rel IN relationships
            LET source_exists = DOCUMENT(rel._from) != null
            LET target_exists = DOCUMENT(rel._to) != null
            FILTER !source_exists OR !target_exists
            REMOVE rel IN relationships
            """
            
            result = self.db.aql.execute(aql_query)
            logger.info(f"Cleaned up {len(result)} orphaned relationships")
            
            # Remove duplicate relationships
            aql_query = """
            FOR rel IN relationships
            COLLECT from_id = rel._from, to_id = rel._to, rel_type = rel.type
            LET duplicates = (FOR r IN relationships
                           FILTER r._from == from_id AND r._to == to_id AND r.type == rel_type
                           RETURN r)
            FILTER LENGTH(duplicates) > 1
            FOR dup IN duplicates
            LIMIT LENGTH(duplicates) - 1
            REMOVE dup IN relationships
            """
            
            result = self.db.aql.execute(aql_query)
            logger.info(f"Cleaned up {len(result)} duplicate relationships")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to maintain consistency: {e}")
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the graph database client."""
        return {
            "status": "healthy" if self.connected else "disconnected",
            "client_type": "arangodb_graph_client",
            "arangodb_connected": self.connected,
            "arangodb_url": self.arango_url,
            "last_updated": datetime.now().isoformat()
        } 