"""
ArangoDB Knowledge Graph Agent
Complete replacement of Neo4j with ArangoDB implementation.
"""

import asyncio
import logging
import time
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    from arango import ArangoClient
    ARANGO_AVAILABLE = True
except ImportError:
    ARANGO_AVAILABLE = False
    logging.warning("ArangoDB driver not available. Install with: pip install python-arango")

from shared.core.agents.base_agent import BaseAgent, AgentType, QueryContext, AgentResult
from shared.core.llm_client_v3 import EnhancedLLMClientV3

logger = logging.getLogger(__name__)


@dataclass
class EntityNode:
    """Represents an entity in the knowledge graph."""
    id: str
    name: str
    type: str
    properties: Dict[str, Any]
    confidence: float = 1.0


@dataclass
class Relationship:
    """Represents a relationship between entities."""
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any]
    confidence: float = 1.0


@dataclass
class KnowledgeGraphResult:
    """Result from knowledge graph query."""
    entities: List[EntityNode]
    relationships: List[Relationship]
    paths: List[List[EntityNode]]
    query_entities: List[str]
    confidence: float
    processing_time_ms: float
    metadata: Dict[str, Any]


class KnowledgeGraphAgent(BaseAgent):
    """
    Agent for handling knowledge graph queries using ArangoDB.
    Complete replacement of Neo4j implementation.
    """
    
    def __init__(self):
        """Initialize the ArangoDB KnowledgeGraphAgent."""
        super().__init__("knowledge_graph_agent", AgentType.RETRIEVAL)
        self.llm_client = EnhancedLLMClientV3()
        
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
            asyncio.create_task(self._initialize_arangodb_connection())
        else:
            logger.warning("Using mock knowledge graph data - ArangoDB driver not available")
        
        # Initialize mock data as fallback
        self.mock_knowledge_graph = self._initialize_mock_knowledge_graph()
        
        logger.info("✅ ArangoDB KnowledgeGraphAgent initialized successfully")
    
    async def _initialize_arangodb_connection(self) -> None:
        """Initialize ArangoDB connection."""
        try:
            # Create ArangoDB client
            self.client = ArangoClient(hosts=self.arango_url)
            
            # Test connection
            await self._test_arangodb_connection()
            self.connected = True
            logger.info(f"✅ Connected to ArangoDB at {self.arango_url}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to ArangoDB: {e}")
            self.connected = False
    
    async def _test_arangodb_connection(self) -> None:
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
    
    async def create_knowledge_node(
        self, node_id: str, node_type: str, properties: Dict[str, Any]
    ) -> bool:
        """Create knowledge graph node in ArangoDB."""
        try:
            entities_collection = self.db.collection("entities")
            
            # Create node document
            node_doc = {
                "_key": node_id,
                "id": node_id,
                "type": node_type,
                **properties
            }
            
            entities_collection.insert(node_doc, overwrite=True)
            
            logger.debug(f"✅ Created knowledge node: {node_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create knowledge node {node_id}: {e}")
            return False
    
    async def create_relationship(
        self,
        from_node_id: str,
        to_node_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Create relationship between nodes in ArangoDB."""
        try:
            relationships_collection = self.db.collection("relationships")
            
            # Create edge document
            edge_doc = {
                "_from": f"entities/{from_node_id}",
                "_to": f"entities/{to_node_id}",
                "type": relationship_type,
                **(properties or {})
            }
            
            relationships_collection.insert(edge_doc)
            
            logger.debug(f"✅ Created relationship: {from_node_id} --[{relationship_type}]--> {to_node_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create relationship: {e}")
            return False
    
    def _initialize_mock_knowledge_graph(self) -> Dict[str, Any]:
        """Initialize mock knowledge graph data for demonstration."""
        return {
            "entities": {
                "ml": {
                    "id": "ml",
                    "name": "Machine Learning",
                    "type": "technology",
                    "properties": {
                        "description": "A subset of artificial intelligence that enables systems to learn from data",
                        "category": "AI/ML",
                        "applications": ["prediction", "classification", "clustering"]
                    }
                },
                "ai": {
                    "id": "ai",
                    "name": "Artificial Intelligence",
                    "type": "technology",
                    "properties": {
                        "description": "The simulation of human intelligence by machines",
                        "category": "AI/ML",
                        "applications": ["automation", "decision_making", "problem_solving"]
                    }
                },
                "deep_learning": {
                    "id": "deep_learning",
                    "name": "Deep Learning",
                    "type": "technology",
                    "properties": {
                        "description": "A subset of machine learning using neural networks with multiple layers",
                        "category": "AI/ML",
                        "applications": ["image_recognition", "nlp", "speech_recognition"]
                    }
                },
                "neural_networks": {
                    "id": "neural_networks",
                    "name": "Neural Networks",
                    "type": "technology",
                    "properties": {
                        "description": "Computing systems inspired by biological neural networks",
                        "category": "AI/ML",
                        "applications": ["pattern_recognition", "classification", "regression"]
                    }
                },
                "python": {
                    "id": "python",
                    "name": "Python",
                    "type": "programming_language",
                    "properties": {
                        "description": "A high-level programming language known for simplicity",
                        "category": "Programming",
                        "applications": ["web_development", "data_science", "automation"]
                    }
                },
                "javascript": {
                    "id": "javascript",
                    "name": "JavaScript",
                    "type": "programming_language",
                    "properties": {
                        "description": "A programming language for web development",
                        "category": "Programming",
                        "applications": ["web_development", "frontend", "backend"]
                    }
                },
                "react": {
                    "id": "react",
                    "name": "React",
                    "type": "framework",
                    "properties": {
                        "description": "A JavaScript library for building user interfaces",
                        "category": "Frontend",
                        "applications": ["web_applications", "mobile_apps", "ui_development"]
                    }
                },
                "docker": {
                    "id": "docker",
                    "name": "Docker",
                    "type": "tool",
                    "properties": {
                        "description": "A platform for containerizing applications",
                        "category": "DevOps",
                        "applications": ["containerization", "deployment", "microservices"]
                    }
                },
                "kubernetes": {
                    "id": "kubernetes",
                    "name": "Kubernetes",
                    "type": "tool",
                    "properties": {
                        "description": "An open-source container orchestration platform",
                        "category": "DevOps",
                        "applications": ["container_orchestration", "scaling", "deployment"]
                    }
                }
            },
            "relationships": [
                {
                    "source": "ml",
                    "target": "ai",
                    "type": "is_subset_of",
                    "properties": {
                        "description": "Machine Learning is a subset of Artificial Intelligence",
                        "confidence": 0.95
                    }
                },
                {
                    "source": "deep_learning",
                    "target": "ml",
                    "type": "is_subset_of",
                    "properties": {
                        "description": "Deep Learning is a subset of Machine Learning",
                        "confidence": 0.95
                    }
                },
                {
                    "source": "neural_networks",
                    "target": "deep_learning",
                    "type": "enables",
                    "properties": {
                        "description": "Neural Networks enable Deep Learning",
                        "confidence": 0.90
                    }
                },
                {
                    "source": "python",
                    "target": "ml",
                    "type": "used_for",
                    "properties": {
                        "description": "Python is commonly used for Machine Learning",
                        "confidence": 0.85
                    }
                },
                {
                    "source": "javascript",
                    "target": "react",
                    "type": "used_for",
                    "properties": {
                        "description": "JavaScript is used to build React applications",
                        "confidence": 0.90
                    }
                },
                {
                    "source": "docker",
                    "target": "kubernetes",
                    "type": "works_with",
                    "properties": {
                        "description": "Docker containers can be orchestrated with Kubernetes",
                        "confidence": 0.85
                    }
                }
            ]
        }
    
    async def process_task(
        self, task: Dict[str, Any], context: QueryContext
    ) -> Dict[str, Any]:
        """
        Process a knowledge graph query task.
        
        Args:
            task: Task containing query and parameters
            context: Query context
            
        Returns:
            Knowledge graph query results
        """
        start_time = time.time()
        
        try:
            query = task.get("query", context.query)
            query_type = task.get("query_type", "entity_relationship")
            
            logger.info(f"🔍 Processing ArangoDB knowledge graph query: {query[:50]}...")
            
            # Extract entities from query
            entities = await self._extract_entities(query)
            
            # Process based on query type
            if query_type == "entity_relationship":
                result = await self._process_entity_relationship_query(query, entities)
            elif query_type == "path_finding":
                result = await self._process_path_finding_query(query, entities)
            elif query_type == "entity_search":
                result = await self._process_entity_search_query(query, entities)
            else:
                result = await self._process_general_query(query, entities)
            
            processing_time = (time.time() - start_time) * 1000
            
            # Create agent result
            agent_result = AgentResult(
                success=True,
                data=result,
                confidence=result.confidence,
                execution_time_ms=int(processing_time),
                metadata={
                    "query_type": query_type,
                    "entities_found": len(entities),
                    "relationships_found": len(result.relationships),
                    "paths_found": len(result.paths),
                    "arangodb_connected": self.connected
                }
            )
            
            logger.info(f"✅ ArangoDB knowledge graph query completed in {processing_time:.2f}ms")
            return agent_result.to_dict()
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error(f"❌ ArangoDB knowledge graph query failed: {e}")
            
            return AgentResult(
                success=False,
                error=str(e),
                execution_time_ms=int(processing_time)
            ).to_dict()
    
    async def _extract_entities(self, query: str) -> List[str]:
        """Extract entities from the query using LLM."""
        try:
            # Use LLM to extract entities
            prompt = f"""
            Extract the main entities (concepts, technologies, tools, people, organizations) from this query:
            "{query}"
            
            Return only the entity names, one per line, without explanations.
            """
            
            response = await self.llm_client.generate_text(prompt, max_tokens=50)
            entities = [line.strip() for line in response.strip().split('\n') if line.strip()]
            
            logger.info(f"Extracted entities: {entities}")
            return entities
            
        except Exception as e:
            logger.warning(f"Entity extraction failed: {e}")
            # Fallback: simple keyword extraction
            keywords = ["machine learning", "artificial intelligence", "deep learning", 
                       "neural networks", "python", "javascript", "react", "docker", 
                       "kubernetes", "blockchain", "cloud computing"]
            
            found_entities = []
            query_lower = query.lower()
            for keyword in keywords:
                if keyword in query_lower:
                    found_entities.append(keyword)
            
            return found_entities
    
    async def _process_entity_relationship_query(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Process entity-relationship queries using ArangoDB."""
        if self.connected and self.db:
            return await self._query_arangodb_entity_relationships(query, entities)
        else:
            return await self._query_mock_entity_relationships(query, entities)
    
    async def _process_path_finding_query(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Process path-finding queries using ArangoDB."""
        if self.connected and self.db:
            return await self._query_arangodb_path_finding(query, entities)
        else:
            return await self._query_mock_path_finding(query, entities)
    
    async def _process_entity_search_query(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Process entity search queries using ArangoDB."""
        if self.connected and self.db:
            return await self._query_arangodb_entity_search(query, entities)
        else:
            return await self._query_mock_entity_search(query, entities)
    
    async def _process_general_query(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Process general knowledge graph queries using ArangoDB."""
        if self.connected and self.db:
            return await self._query_arangodb_general(query, entities)
        else:
            return await self._query_mock_general(query, entities)
    
    # ArangoDB Query Methods
    async def _query_arangodb_entity_relationships(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Query ArangoDB for entity relationships."""
        try:
            if len(entities) < 2:
                # Single entity query
                aql_query = """
                FOR doc IN entities
                FILTER CONTAINS(LOWER(doc.name), LOWER(@entity)) OR CONTAINS(LOWER(doc.id), LOWER(@entity))
                RETURN doc
                LIMIT 20
                """
                parameters = {"entity": entities[0] if entities else ""}
            else:
                # Multiple entities - find relationships between them
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
                parameters = {
                    "entity1": entities[0],
                    "entity2": entities[1]
                }
            
            result = self.db.aql.execute(aql_query, parameters)
            
            # Parse results
            found_entities = []
            found_relationships = []
            
            for record in result:
                if 'entity1' in record:
                    entity = record['entity1']
                    found_entities.append(EntityNode(
                        id=entity.get('id', ''),
                        name=entity.get('name', ''),
                        type=entity.get('type', 'Node'),
                        properties=entity
                    ))
                if 'entity2' in record:
                    entity = record['entity2']
                    found_entities.append(EntityNode(
                        id=entity.get('id', ''),
                        name=entity.get('name', ''),
                        type=entity.get('type', 'Node'),
                        properties=entity
                    ))
                
                if 'rel' in record:
                    rel = record['rel']
                    found_relationships.append(Relationship(
                        source_id=rel.get('_from', ''),
                        target_id=rel.get('_to', ''),
                        relationship_type=rel.get('type', ''),
                        properties=rel
                    ))
            
            # Remove duplicates
            unique_entities = list({entity.id: entity for entity in found_entities}.values())
            unique_relationships = list({f"{rel.source_id}-{rel.target_id}-{rel.relationship_type}": rel 
                                      for rel in found_relationships}.values())
            
            return KnowledgeGraphResult(
                entities=unique_entities,
                relationships=unique_relationships,
                paths=[],
                query_entities=entities,
                confidence=0.9 if unique_entities else 0.3,
                processing_time_ms=0,
                metadata={
                    "query_type": "entity_relationship",
                    "entities_found": len(unique_entities),
                    "relationships_found": len(unique_relationships),
                    "arangodb_query": aql_query
                }
            )
            
        except Exception as e:
            logger.error(f"ArangoDB entity relationship query failed: {e}")
            return KnowledgeGraphResult(
                entities=[],
                relationships=[],
                paths=[],
                query_entities=entities,
                confidence=0.0,
                processing_time_ms=0,
                metadata={"error": str(e)}
            )
    
    async def _query_arangodb_path_finding(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Query ArangoDB for path finding between entities."""
        try:
            if len(entities) < 2:
                return KnowledgeGraphResult(
                    entities=[],
                    relationships=[],
                    paths=[],
                    query_entities=entities,
                    confidence=0.0,
                    processing_time_ms=0,
                    metadata={"error": "Need at least 2 entities for path finding"}
                )
            
            # Find shortest path between entities using ArangoDB's SHORTEST_PATH
            aql_query = """
            FOR start IN entities
            FOR end IN entities
            FILTER (CONTAINS(LOWER(start.name), LOWER(@entity1)) OR CONTAINS(LOWER(start.id), LOWER(@entity1)))
            AND (CONTAINS(LOWER(end.name), LOWER(@entity2)) OR CONTAINS(LOWER(end.id), LOWER(@entity2)))
            FOR v, e, p IN 1..3 OUTBOUND start relationships
            FILTER v._id == end._id
            SORT LENGTH(p.edges)
            LIMIT 5
            RETURN {path: p, start: start, end: end}
            """
            
            parameters = {
                "entity1": entities[0],
                "entity2": entities[1]
            }
            
            result = self.db.aql.execute(aql_query, parameters)
            
            # Parse path results
            paths = []
            all_entities = []
            all_relationships = []
            
            for record in result:
                path = record['path']
                path_nodes = []
                path_rels = []
                
                # Extract nodes from path
                for vertex in path['vertices']:
                    entity = EntityNode(
                        id=vertex.get('id', ''),
                        name=vertex.get('name', ''),
                        type=vertex.get('type', 'Node'),
                        properties=vertex
                    )
                    path_nodes.append(entity)
                    all_entities.append(entity)
                
                # Extract edges from path
                for edge in path['edges']:
                    relationship = Relationship(
                        source_id=edge.get('_from', ''),
                        target_id=edge.get('_to', ''),
                        relationship_type=edge.get('type', ''),
                        properties=edge
                    )
                    path_rels.append(relationship)
                    all_relationships.append(relationship)
                
                if path_nodes:
                    paths.append(path_nodes)
            
            return KnowledgeGraphResult(
                entities=list({entity.id: entity for entity in all_entities}.values()),
                relationships=list({f"{rel.source_id}-{rel.target_id}-{rel.relationship_type}": rel 
                                 for rel in all_relationships}.values()),
                paths=paths,
                query_entities=entities,
                confidence=0.85 if paths else 0.3,
                processing_time_ms=0,
                metadata={
                    "query_type": "path_finding",
                    "paths_found": len(paths),
                    "arangodb_query": aql_query
                }
            )
            
        except Exception as e:
            logger.error(f"ArangoDB path finding query failed: {e}")
            return KnowledgeGraphResult(
                entities=[],
                relationships=[],
                paths=[],
                query_entities=entities,
                confidence=0.0,
                processing_time_ms=0,
                metadata={"error": str(e)}
            )
    
    async def _query_arangodb_entity_search(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Query ArangoDB for entity search."""
        try:
            if not entities:
                return KnowledgeGraphResult(
                    entities=[],
                    relationships=[],
                    paths=[],
                    query_entities=entities,
                    confidence=0.0,
                    processing_time_ms=0,
                    metadata={"error": "No entities found in query"}
                )
            
            # Search for entities by name or properties
            aql_query = """
            FOR doc IN entities
            FILTER CONTAINS(LOWER(doc.name), LOWER(@entity)) 
               OR CONTAINS(LOWER(doc.id), LOWER(@entity))
               OR CONTAINS(LOWER(doc.description), LOWER(@entity))
            RETURN doc
            LIMIT 20
            """
            
            parameters = {"entity": entities[0]}
            
            result = self.db.aql.execute(aql_query, parameters)
            
            found_entities = []
            for record in result:
                found_entities.append(EntityNode(
                    id=record.get('id', ''),
                    name=record.get('name', ''),
                    type=record.get('type', 'Node'),
                    properties=record
                ))
            
            return KnowledgeGraphResult(
                entities=found_entities,
                relationships=[],
                paths=[],
                query_entities=entities,
                confidence=0.9 if found_entities else 0.3,
                processing_time_ms=0,
                metadata={
                    "query_type": "entity_search",
                    "entities_found": len(found_entities),
                    "arangodb_query": aql_query
                }
            )
            
        except Exception as e:
            logger.error(f"ArangoDB entity search query failed: {e}")
            return KnowledgeGraphResult(
                entities=[],
                relationships=[],
                paths=[],
                query_entities=entities,
                confidence=0.0,
                processing_time_ms=0,
                metadata={"error": str(e)}
            )
    
    async def _query_arangodb_general(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Query ArangoDB for general knowledge graph queries."""
        try:
            # General query - try to find relevant nodes and relationships
            aql_query = """
            FOR rel IN relationships
            FOR entity1 IN entities
            FOR entity2 IN entities
            FILTER rel._from == entity1._id AND rel._to == entity2._id
            FILTER ANY(entity IN @entities SATISFIES 
                CONTAINS(LOWER(entity1.name), LOWER(entity)) 
                OR CONTAINS(LOWER(entity1.id), LOWER(entity))
                OR CONTAINS(LOWER(entity2.name), LOWER(entity))
                OR CONTAINS(LOWER(entity2.id), LOWER(entity))
            )
            RETURN {entity1, rel, entity2}
            LIMIT 30
            """
            
            parameters = {"entities": entities}
            
            result = self.db.aql.execute(aql_query, parameters)
            
            found_entities = []
            found_relationships = []
            
            for record in result:
                # Extract nodes
                if 'entity1' in record:
                    entity = record['entity1']
                    found_entities.append(EntityNode(
                        id=entity.get('id', ''),
                        name=entity.get('name', ''),
                        type=entity.get('type', 'Node'),
                        properties=entity
                    ))
                if 'entity2' in record:
                    entity = record['entity2']
                    found_entities.append(EntityNode(
                        id=entity.get('id', ''),
                        name=entity.get('name', ''),
                        type=entity.get('type', 'Node'),
                        properties=entity
                    ))
                
                # Extract relationships
                if 'rel' in record:
                    rel = record['rel']
                    found_relationships.append(Relationship(
                        source_id=rel.get('_from', ''),
                        target_id=rel.get('_to', ''),
                        relationship_type=rel.get('type', ''),
                        properties=rel
                    ))
            
            # Remove duplicates
            unique_entities = list({entity.id: entity for entity in found_entities}.values())
            unique_relationships = list({f"{rel.source_id}-{rel.target_id}-{rel.relationship_type}": rel 
                                      for rel in found_relationships}.values())
            
            return KnowledgeGraphResult(
                entities=unique_entities,
                relationships=unique_relationships,
                paths=[],
                query_entities=entities,
                confidence=0.8 if unique_entities else 0.3,
                processing_time_ms=0,
                metadata={
                    "query_type": "general",
                    "entities_found": len(unique_entities),
                    "relationships_found": len(unique_relationships),
                    "arangodb_query": aql_query
                }
            )
            
        except Exception as e:
            logger.error(f"ArangoDB general query failed: {e}")
            return KnowledgeGraphResult(
                entities=[],
                relationships=[],
                paths=[],
                query_entities=entities,
                confidence=0.0,
                processing_time_ms=0,
                metadata={"error": str(e)}
            )
    
    # Mock Query Methods (fallback)
    async def _query_mock_entity_relationships(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Process entity-relationship queries using mock data."""
        found_entities = []
        found_relationships = []
        
        # Find entities in knowledge graph
        for entity_name in entities:
            for entity_id, entity_data in self.mock_knowledge_graph["entities"].items():
                if entity_name.lower() in entity_data["name"].lower() or entity_name.lower() in entity_id:
                    found_entities.append(EntityNode(
                        id=entity_id,
                        name=entity_data["name"],
                        type=entity_data["type"],
                        properties=entity_data["properties"]
                    ))
        
        # Find relationships involving these entities
        for rel in self.mock_knowledge_graph["relationships"]:
            source_entity = next((e for e in found_entities if e.id == rel["source"]), None)
            target_entity = next((e for e in found_entities if e.id == rel["target"]), None)
            
            if source_entity and target_entity:
                found_relationships.append(Relationship(
                    source_id=rel["source"],
                    target_id=rel["target"],
                    relationship_type=rel["type"],
                    properties=rel["properties"]
                ))
        
        # Find paths between entities
        paths = await self._find_paths_between_entities(found_entities)
        
        return KnowledgeGraphResult(
            entities=found_entities,
            relationships=found_relationships,
            paths=paths,
            query_entities=entities,
            confidence=0.85 if found_entities else 0.3,
            processing_time_ms=0,
            metadata={
                "query_type": "entity_relationship",
                "entities_found": len(found_entities),
                "relationships_found": len(found_relationships),
                "mock_data": True
            }
        )
    
    async def _query_mock_path_finding(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Process path-finding queries using mock data."""
        return await self._query_mock_entity_relationships(query, entities)
    
    async def _query_mock_entity_search(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Process entity search queries using mock data."""
        return await self._query_mock_entity_relationships(query, entities)
    
    async def _query_mock_general(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Process general knowledge graph queries using mock data."""
        return await self._query_mock_entity_relationships(query, entities)
    
    async def _find_paths_between_entities(self, entities: List[EntityNode]) -> List[List[EntityNode]]:
        """Find paths between entities in the knowledge graph."""
        if len(entities) < 2:
            return []
        
        paths = []
        
        # Simple path finding: find direct relationships
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                # Check if there's a direct relationship
                for rel in self.mock_knowledge_graph["relationships"]:
                    if (rel["source"] == entity1.id and rel["target"] == entity2.id) or \
                       (rel["source"] == entity2.id and rel["target"] == entity1.id):
                        paths.append([entity1, entity2])
        
        return paths
    
    async def query(self, query: str, query_type: str = "entity_relationship") -> KnowledgeGraphResult:
        """
        Query the knowledge graph using ArangoDB.
        
        Args:
            query: The query string
            query_type: Type of query (entity_relationship, path_finding, entity_search)
            
        Returns:
            KnowledgeGraphResult with entities, relationships, and paths
        """
        # Extract entities from query
        entities = await self._extract_entities(query)
        
        # Process based on query type
        if query_type == "entity_relationship":
            result = await self._process_entity_relationship_query(query, entities)
        elif query_type == "path_finding":
            result = await self._process_path_finding_query(query, entities)
        elif query_type == "entity_search":
            result = await self._process_entity_search_query(query, entities)
        else:
            result = await self._process_general_query(query, entities)
        
        return result
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the ArangoDB knowledge graph agent."""
        return {
            "status": "healthy" if self.connected else "disconnected",
            "agent_type": "knowledge_graph",
            "arangodb_connected": self.connected,
            "arangodb_url": self.arango_url,
            "entities_count": len(self.mock_knowledge_graph["entities"]) if hasattr(self, 'mock_knowledge_graph') else 0,
            "relationships_count": len(self.mock_knowledge_graph["relationships"]) if hasattr(self, 'mock_knowledge_graph') else 0,
            "last_updated": datetime.now().isoformat()
        } 