"""
Graph Service

This service handles knowledge graph operations including:
- Knowledge graph construction and maintenance
- Relationship extraction and modeling
- Graph traversal and querying
- Entity linking and disambiguation
- Graph analytics and insights
"""

import asyncio
import logging
import os
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logging.warning("python-dotenv not available")

# ArangoDB imports
try:
    from arango import ArangoClient
    ARANGO_AVAILABLE = True
except ImportError:
    ARANGO_AVAILABLE = False
    logging.warning("ArangoDB driver not available. Install with: pip install python-arango")

# SPARQL imports
try:
    import aiohttp
    SPARQL_AVAILABLE = True
except ImportError:
    SPARQL_AVAILABLE = False
    aiohttp = None

logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """Represents a node in the knowledge graph."""
    id: str
    label: str
    properties: Dict[str, Any]
    node_type: str


@dataclass
class GraphEdge:
    """Represents an edge in the knowledge graph."""
    id: str
    source: str
    target: str
    label: str
    properties: Dict[str, Any]
    edge_type: str


@dataclass
class GraphQueryResult:
    """Result from graph query operation."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    metadata: Dict[str, Any]


class GraphService:
    """
    Graph Service for handling knowledge graph operations.
    Supports ArangoDB and SPARQL endpoints.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # ArangoDB configuration
        self.arango_url = os.getenv("ARANGO_URL", "http://localhost:8529")
        self.arango_db = os.getenv("ARANGO_DB", "knowledge_graph")
        self.arango_username = os.getenv("ARANGO_USERNAME", "root")
        self.arango_password = os.getenv("ARANGO_PASSWORD", "")
        
        # SPARQL configuration
        self.sparql_endpoint = os.getenv("SPARQL_ENDPOINT_URL")
        
        # Initialize graph database
        self.arango_client = None
        self.arango_db_instance = None
        self._initialize_graph_db()
    
    def _initialize_graph_db(self):
        """Initialize graph database connection."""
        # Try ArangoDB first
        if ARANGO_AVAILABLE:
            try:
                self.arango_client = ArangoClient(hosts=self.arango_url)
                # Connect to database
                self.arango_db_instance = self.arango_client.db(
                    self.arango_db,
                    username=self.arango_username,
                    password=self.arango_password
                )
                logger.info("✅ ArangoDB initialized successfully")
                return
            except Exception as e:
                logger.warning(f"⚠️ ArangoDB initialization failed: {e}")
        
        # SPARQL endpoint check
        if SPARQL_AVAILABLE and self.sparql_endpoint:
            logger.info("✅ SPARQL endpoint available")
            return
        
        logger.info("⚠️ No graph database available")
    
    async def create_node(self, node_data: Dict[str, Any]) -> Optional[str]:
        """Create a new node in the knowledge graph."""
        if not self.arango_db_instance:
            logger.warning("ArangoDB not available")
            return None
        
        try:
            # Create node in ArangoDB
            collection_name = node_data.get("collection", "nodes")
            collection = self.arango_db_instance.collection(collection_name)
            
            # Ensure collection exists
            if not collection.exists():
                self.arango_db_instance.create_collection(collection_name)
            
            # Insert node
            result = collection.insert(node_data)
            logger.info(f"Created node {result['_key']} in collection {collection_name}")
            return result['_key']
        except Exception as e:
            logger.error(f"Failed to create node: {e}")
            return None
    
    async def create_edge(self, edge_data: Dict[str, Any]) -> Optional[str]:
        """Create a new edge in the knowledge graph."""
        if not self.arango_db_instance:
            logger.warning("ArangoDB not available")
            return None
        
        try:
            # Create edge in ArangoDB
            collection_name = edge_data.get("collection", "edges")
            collection = self.arango_db_instance.collection(collection_name)
            
            # Ensure collection exists
            if not collection.exists():
                self.arango_db_instance.create_collection(collection_name, edge=True)
            
            # Insert edge
            result = collection.insert(edge_data)
            logger.info(f"Created edge {result['_key']} in collection {collection_name}")
            return result['_key']
        except Exception as e:
            logger.error(f"Failed to create edge: {e}")
            return None
    
    async def query_graph(self, query: str, params: Dict[str, Any] = None) -> GraphQueryResult:
        """Query the knowledge graph using AQL or SPARQL."""
        params = params or {}
        
        # Try ArangoDB AQL query
        if self.arango_db_instance:
            try:
                cursor = self.arango_db_instance.aql.execute(query, bind_vars=params)
                results = cursor.batch()
                
                nodes = []
                edges = []
                
                for result in results:
                    if '_from' in result and '_to' in result:
                        # This is an edge
                        edges.append(GraphEdge(
                            id=result.get('_key', ''),
                            source=result['_from'],
                            target=result['_to'],
                            label=result.get('label', ''),
                            properties=result,
                            edge_type=result.get('type', 'edge')
                        ))
                    else:
                        # This is a node
                        nodes.append(GraphNode(
                            id=result.get('_key', ''),
                            label=result.get('label', ''),
                            properties=result,
                            node_type=result.get('type', 'node')
                        ))
                
                return GraphQueryResult(
                    nodes=nodes,
                    edges=edges,
                    metadata={"source": "arango", "query": query}
                )
            except Exception as e:
                logger.error(f"ArangoDB query failed: {e}")
        
        # Try SPARQL query
        if SPARQL_AVAILABLE and self.sparql_endpoint:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.sparql_endpoint,
                        data={'query': query},
                        headers={'Content-Type': 'application/x-www-form-urlencoded'}
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            # Parse SPARQL results
                            nodes = []
                            edges = []
                            
                            # This is a simplified SPARQL result parser
                            # In a real implementation, you'd want more sophisticated parsing
                            for binding in data.get('results', {}).get('bindings', []):
                                # Extract node/edge information from SPARQL results
                                # This is a placeholder implementation
                                pass
                            
                            return GraphQueryResult(
                                nodes=nodes,
                                edges=edges,
                                metadata={"source": "sparql", "query": query}
                            )
            except Exception as e:
                logger.error(f"SPARQL query failed: {e}")
        
        return GraphQueryResult(nodes=[], edges=[], metadata={"error": "No graph database available"})
    
    async def find_entities(self, text: str) -> List[GraphNode]:
        """Find entities in text and link them to knowledge graph."""
        # This is a placeholder implementation
        # In a real implementation, you'd use NER and entity linking
        entities = []
        
        # Simple keyword-based entity extraction
        keywords = text.lower().split()
        for keyword in keywords:
            if len(keyword) > 3:  # Filter out short words
                # Query for entities matching the keyword
                query = """
                FOR node IN nodes
                FILTER CONTAINS(LOWER(node.label), @keyword)
                RETURN node
                """
                result = await self.query_graph(query, {"keyword": keyword})
                entities.extend(result.nodes)
        
        return entities
    
    async def get_relationships(self, entity_id: str, max_depth: int = 2) -> GraphQueryResult:
        """Get relationships for an entity up to a certain depth."""
        if not self.arango_db_instance:
            return GraphQueryResult(nodes=[], edges=[], metadata={"error": "ArangoDB not available"})
        
        try:
            # Query for relationships
            query = """
            FOR v, e, p IN @max_depth..@max_depth OUTBOUND @entity_id
            GRAPH 'knowledge_graph'
            RETURN {
                'nodes': p.vertices,
                'edges': p.edges
            }
            """
            
            result = await self.query_graph(query, {
                "entity_id": entity_id,
                "max_depth": max_depth
            })
            
            return result
        except Exception as e:
            logger.error(f"Failed to get relationships: {e}")
            return GraphQueryResult(nodes=[], edges=[], metadata={"error": str(e)})
    
    async def add_knowledge_triple(self, subject: str, predicate: str, object_value: str) -> bool:
        """Add a knowledge triple (subject, predicate, object) to the graph."""
        try:
            # Create subject node if it doesn't exist
            subject_id = await self.create_node({
                "label": subject,
                "type": "entity",
                "collection": "entities"
            })
            
            # Create object node if it doesn't exist
            object_id = await self.create_node({
                "label": object_value,
                "type": "entity",
                "collection": "entities"
            })
            
            # Create relationship edge
            if subject_id and object_id:
                await self.create_edge({
                    "_from": subject_id,
                    "_to": object_id,
                    "label": predicate,
                    "type": "relationship",
                    "collection": "relationships"
                })
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to add knowledge triple: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status and configuration."""
        return {
            "service": "graph",
            "status": "healthy" if (self.arango_db_instance or self.sparql_endpoint) else "unavailable",
            "arango_available": bool(self.arango_db_instance),
            "sparql_available": SPARQL_AVAILABLE and bool(self.sparql_endpoint),
            "arango_url": self.arango_url,
            "arango_db": self.arango_db
        } 