"""
Knowledge Graph Service
High-level service for handling knowledge graph queries and data transformation.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from shared.core.agents.base_agent import (
    BaseAgent,
    AgentType,
    QueryContext,
    AgentResult,
)
from shared.core.agents.graph_db_client import GraphDBClient, GraphNode, GraphEdge
from shared.core.agents.llm_client import LLMClient

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


class KnowledgeGraphService:
    """
    High-level service for knowledge graph operations.
    Handles query logic, entity extraction, and data transformation.
    """

    def __init__(self):
        """Initialize the KnowledgeGraphService."""
        self.graph_client = GraphDBClient()
        self.llm_client = LLMClient()

        # Initialize mock data as fallback
        self.mock_knowledge_graph = self._initialize_mock_knowledge_graph()

        logger.info("✅ KnowledgeGraphService initialized successfully")

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
                        "applications": ["prediction", "classification", "clustering"],
                    },
                },
                "ai": {
                    "id": "ai",
                    "name": "Artificial Intelligence",
                    "type": "technology",
                    "properties": {
                        "description": "The simulation of human intelligence by machines",
                        "category": "AI/ML",
                        "applications": [
                            "automation",
                            "decision_making",
                            "problem_solving",
                        ],
                    },
                },
                "deep_learning": {
                    "id": "deep_learning",
                    "name": "Deep Learning",
                    "type": "technology",
                    "properties": {
                        "description": "A subset of machine learning using neural networks with multiple layers",
                        "category": "AI/ML",
                        "applications": [
                            "image_recognition",
                            "nlp",
                            "speech_recognition",
                        ],
                    },
                },
                "neural_networks": {
                    "id": "neural_networks",
                    "name": "Neural Networks",
                    "type": "technology",
                    "properties": {
                        "description": "Computing systems inspired by biological neural networks",
                        "category": "AI/ML",
                        "applications": [
                            "pattern_recognition",
                            "classification",
                            "regression",
                        ],
                    },
                },
                "python": {
                    "id": "python",
                    "name": "Python",
                    "type": "programming_language",
                    "properties": {
                        "description": "A high-level programming language known for simplicity",
                        "category": "Programming",
                        "applications": [
                            "web_development",
                            "data_science",
                            "automation",
                        ],
                    },
                },
                "javascript": {
                    "id": "javascript",
                    "name": "JavaScript",
                    "type": "programming_language",
                    "properties": {
                        "description": "A programming language for web development",
                        "category": "Programming",
                        "applications": ["web_development", "frontend", "backend"],
                    },
                },
                "react": {
                    "id": "react",
                    "name": "React",
                    "type": "framework",
                    "properties": {
                        "description": "A JavaScript library for building user interfaces",
                        "category": "Frontend",
                        "applications": [
                            "web_applications",
                            "mobile_apps",
                            "ui_development",
                        ],
                    },
                },
                "docker": {
                    "id": "docker",
                    "name": "Docker",
                    "type": "tool",
                    "properties": {
                        "description": "A platform for containerizing applications",
                        "category": "DevOps",
                        "applications": [
                            "containerization",
                            "deployment",
                            "microservices",
                        ],
                    },
                },
                "kubernetes": {
                    "id": "kubernetes",
                    "name": "Kubernetes",
                    "type": "tool",
                    "properties": {
                        "description": "An open-source container orchestration platform",
                        "category": "DevOps",
                        "applications": [
                            "container_orchestration",
                            "scaling",
                            "deployment",
                        ],
                    },
                },
            },
            "relationships": [
                {
                    "source": "ml",
                    "target": "ai",
                    "type": "is_subset_of",
                    "properties": {
                        "description": "Machine Learning is a subset of Artificial Intelligence",
                        "confidence": 0.95,
                    },
                },
                {
                    "source": "deep_learning",
                    "target": "ml",
                    "type": "is_subset_of",
                    "properties": {
                        "description": "Deep Learning is a subset of Machine Learning",
                        "confidence": 0.95,
                    },
                },
                {
                    "source": "neural_networks",
                    "target": "deep_learning",
                    "type": "enables",
                    "properties": {
                        "description": "Neural Networks enable Deep Learning",
                        "confidence": 0.90,
                    },
                },
                {
                    "source": "python",
                    "target": "ml",
                    "type": "used_for",
                    "properties": {
                        "description": "Python is commonly used for Machine Learning",
                        "confidence": 0.85,
                    },
                },
                {
                    "source": "javascript",
                    "target": "react",
                    "type": "used_for",
                    "properties": {
                        "description": "JavaScript is used to build React applications",
                        "confidence": 0.90,
                    },
                },
                {
                    "source": "docker",
                    "target": "kubernetes",
                    "type": "works_with",
                    "properties": {
                        "description": "Docker containers can be orchestrated with Kubernetes",
                        "confidence": 0.85,
                    },
                },
            ],
        }

    async def extract_entities(self, query: str) -> List[str]:
        """Extract entities from the query using LLM."""
        try:
            # Use LLM to extract entities
            prompt = f"""
            Extract the main entities (concepts, technologies, tools, people, organizations) from this query:
            "{query}"
            
            Return only the entity names, one per line, without explanations.
            """

            response = await self.llm_client.generate_text(prompt, max_tokens=50)
            entities = [
                line.strip() for line in response.strip().split("\n") if line.strip()
            ]

            logger.info(f"Extracted entities: {entities}")
            return entities

        except Exception as e:
            logger.warning(f"Entity extraction failed: {e}")
            # Fallback: simple keyword extraction
            keywords = [
                "machine learning",
                "artificial intelligence",
                "deep learning",
                "neural networks",
                "python",
                "javascript",
                "react",
                "docker",
                "kubernetes",
                "blockchain",
                "cloud computing",
            ]

            found_entities = []
            query_lower = query.lower()
            for keyword in keywords:
                if keyword in query_lower:
                    found_entities.append(keyword)

            return found_entities

    async def extract_entities_enhanced(self, content: str) -> List[Dict[str, Any]]:
        """
        Enhanced entity extraction using LLM and multiple strategies.

        Args:
            content: Document content

        Returns:
            List of extracted entities with enhanced metadata
        """
        try:
            # Use LLM for advanced entity extraction
            llm_prompt = f"""
            Extract named entities from this content:
            "{content[:1000]}..."
            
            Return a JSON array with entities in this format:
            [
                {{
                    "text": "entity name",
                    "type": "PERSON|ORGANIZATION|LOCATION|TECHNOLOGY|CONCEPT|OTHER",
                    "confidence": 0.0-1.0,
                    "relevance": "high|medium|low",
                    "description": "brief description"
                }}
            ]
            
            Focus on entities that are important for knowledge graph construction.
            Limit to the most relevant entities.
            """

            try:
                response = await self.llm_client.generate_text(
                    prompt=llm_prompt, max_tokens=500, use_dynamic_selection=True
                )

                if response:
                    import json

                    try:
                        entities = json.loads(response)
                        if isinstance(entities, list):
                            # Filter by confidence threshold
                            entities = [
                                e for e in entities if e.get("confidence", 0) >= 0.7
                            ]
                            # Limit number of entities
                            entities = entities[:10]
                            return entities
                    except json.JSONDecodeError:
                        pass
            except Exception as e:
                logger.warning(f"LLM entity extraction failed: {e}")

            # Fallback to basic entity extraction
            basic_entities = await self.extract_entities(content)
            return [
                {"text": entity, "type": "CONCEPT", "confidence": 0.8}
                for entity in basic_entities
            ]

        except Exception as e:
            logger.error(f"Enhanced entity extraction failed: {e}")
            return []

    async def query_entity_relationships(
        self, query: str, entities: List[str]
    ) -> KnowledgeGraphResult:
        """Query for entity relationships."""
        if self.graph_client.connected:
            return await self._query_arangodb_entity_relationships(query, entities)
        else:
            return await self._query_mock_entity_relationships(query, entities)

    async def query_path_finding(
        self, query: str, entities: List[str]
    ) -> KnowledgeGraphResult:
        """Query for paths between entities."""
        if self.graph_client.connected:
            return await self._query_arangodb_path_finding(query, entities)
        else:
            return await self._query_mock_path_finding(query, entities)

    async def query_entity_search(
        self, query: str, entities: List[str]
    ) -> KnowledgeGraphResult:
        """Query for entity search."""
        if self.graph_client.connected:
            return await self._query_arangodb_entity_search(query, entities)
        else:
            return await self._query_mock_entity_search(query, entities)

    async def query_general(
        self, query: str, entities: List[str]
    ) -> KnowledgeGraphResult:
        """Query for general knowledge graph information."""
        if self.graph_client.connected:
            return await self._query_arangodb_general(query, entities)
        else:
            return await self._query_mock_general(query, entities)

    # ArangoDB Query Methods
    async def _query_arangodb_entity_relationships(
        self, query: str, entities: List[str]
    ) -> KnowledgeGraphResult:
        """Query ArangoDB for entity relationships."""
        try:
            if len(entities) < 2:
                # Single entity query
                nodes = await self.graph_client.find_nodes_by_name(
                    entities[0] if entities else ""
                )
                found_entities = [
                    self._convert_graph_node_to_entity(node) for node in nodes
                ]
                found_relationships = []
            else:
                # Multiple entities - find relationships between them
                edges = await self.graph_client.find_relationships_between_nodes(
                    entities[0], entities[1]
                )
                found_entities = []
                found_relationships = [
                    self._convert_graph_edge_to_relationship(edge) for edge in edges
                ]

                # Get unique entities from relationships
                entity_ids = set()
                for rel in found_relationships:
                    entity_ids.add(rel.source_id)
                    entity_ids.add(rel.target_id)

                # Fetch entity details
                for entity_id in entity_ids:
                    nodes = await self.graph_client.find_nodes_by_name(entity_id)
                    if nodes:
                        found_entities.append(
                            self._convert_graph_node_to_entity(nodes[0])
                        )

            # Remove duplicates
            unique_entities = list(
                {entity.id: entity for entity in found_entities}.values()
            )
            unique_relationships = list(
                {
                    f"{rel.source_id}-{rel.target_id}-{rel.relationship_type}": rel
                    for rel in found_relationships
                }.values()
            )

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
                    "arangodb_connected": self.graph_client.connected,
                },
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
                metadata={"error": str(e)},
            )

    async def _query_arangodb_path_finding(
        self, query: str, entities: List[str]
    ) -> KnowledgeGraphResult:
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
                    metadata={"error": "Need at least 2 entities for path finding"},
                )

            # Find paths between entities
            paths = await self.graph_client.find_paths_between_nodes(
                entities[0], entities[1]
            )

            # Convert paths to entity format
            converted_paths = []
            all_entities = []
            all_relationships = []

            for path in paths:
                path_entities = [
                    self._convert_graph_node_to_entity(node) for node in path
                ]
                converted_paths.append(path_entities)
                all_entities.extend(path_entities)

            # Remove duplicates
            unique_entities = list(
                {entity.id: entity for entity in all_entities}.values()
            )

            return KnowledgeGraphResult(
                entities=unique_entities,
                relationships=all_relationships,
                paths=converted_paths,
                query_entities=entities,
                confidence=0.85 if paths else 0.3,
                processing_time_ms=0,
                metadata={
                    "query_type": "path_finding",
                    "paths_found": len(paths),
                    "arangodb_connected": self.graph_client.connected,
                },
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
                metadata={"error": str(e)},
            )

    async def _query_arangodb_entity_search(
        self, query: str, entities: List[str]
    ) -> KnowledgeGraphResult:
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
                    metadata={"error": "No entities found in query"},
                )

            # Search for entities by name
            nodes = await self.graph_client.find_nodes_by_name(entities[0])
            found_entities = [
                self._convert_graph_node_to_entity(node) for node in nodes
            ]

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
                    "arangodb_connected": self.graph_client.connected,
                },
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
                metadata={"error": str(e)},
            )

    async def _query_arangodb_general(
        self, query: str, entities: List[str]
    ) -> KnowledgeGraphResult:
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
            result = await self.graph_client.execute_query(aql_query, parameters)

            found_entities = []
            found_relationships = []

            for record in result:
                # Extract nodes
                if "entity1" in record:
                    entity = record["entity1"]
                    found_entities.append(
                        EntityNode(
                            id=entity.get("id", ""),
                            name=entity.get("name", ""),
                            type=entity.get("type", "Node"),
                            properties=entity,
                        )
                    )
                if "entity2" in record:
                    entity = record["entity2"]
                    found_entities.append(
                        EntityNode(
                            id=entity.get("id", ""),
                            name=entity.get("name", ""),
                            type=entity.get("type", "Node"),
                            properties=entity,
                        )
                    )

                # Extract relationships
                if "rel" in record:
                    rel = record["rel"]
                    found_relationships.append(
                        Relationship(
                            source_id=rel.get("_from", ""),
                            target_id=rel.get("_to", ""),
                            relationship_type=rel.get("type", ""),
                            properties=rel,
                        )
                    )

            # Remove duplicates
            unique_entities = list(
                {entity.id: entity for entity in found_entities}.values()
            )
            unique_relationships = list(
                {
                    f"{rel.source_id}-{rel.target_id}-{rel.relationship_type}": rel
                    for rel in found_relationships
                }.values()
            )

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
                    "arangodb_connected": self.graph_client.connected,
                },
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
                metadata={"error": str(e)},
            )

    # Mock Query Methods (fallback)
    async def _query_mock_entity_relationships(
        self, query: str, entities: List[str]
    ) -> KnowledgeGraphResult:
        """Process entity-relationship queries using mock data."""
        found_entities = []
        found_relationships = []

        # Find entities in knowledge graph
        for entity_name in entities:
            for entity_id, entity_data in self.mock_knowledge_graph["entities"].items():
                if (
                    entity_name.lower() in entity_data["name"].lower()
                    or entity_name.lower() in entity_id
                ):
                    found_entities.append(
                        EntityNode(
                            id=entity_id,
                            name=entity_data["name"],
                            type=entity_data["type"],
                            properties=entity_data["properties"],
                        )
                    )

        # Find relationships involving these entities
        for rel in self.mock_knowledge_graph["relationships"]:
            source_entity = next(
                (e for e in found_entities if e.id == rel["source"]), None
            )
            target_entity = next(
                (e for e in found_entities if e.id == rel["target"]), None
            )

            if source_entity and target_entity:
                found_relationships.append(
                    Relationship(
                        source_id=rel["source"],
                        target_id=rel["target"],
                        relationship_type=rel["type"],
                        properties=rel["properties"],
                    )
                )

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
                "mock_data": True,
            },
        )

    async def _query_mock_path_finding(
        self, query: str, entities: List[str]
    ) -> KnowledgeGraphResult:
        """Process path-finding queries using mock data."""
        return await self._query_mock_entity_relationships(query, entities)

    async def _query_mock_entity_search(
        self, query: str, entities: List[str]
    ) -> KnowledgeGraphResult:
        """Process entity search queries using mock data."""
        return await self._query_mock_entity_relationships(query, entities)

    async def _query_mock_general(
        self, query: str, entities: List[str]
    ) -> KnowledgeGraphResult:
        """Process general knowledge graph queries using mock data."""
        return await self._query_mock_entity_relationships(query, entities)

    async def _find_paths_between_entities(
        self, entities: List[EntityNode]
    ) -> List[List[EntityNode]]:
        """Find paths between entities in the knowledge graph."""
        if len(entities) < 2:
            return []

        paths = []

        # Simple path finding: find direct relationships
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i + 1 :]:
                # Check if there's a direct relationship
                for rel in self.mock_knowledge_graph["relationships"]:
                    if (
                        rel["source"] == entity1.id and rel["target"] == entity2.id
                    ) or (rel["source"] == entity2.id and rel["target"] == entity1.id):
                        paths.append([entity1, entity2])

        return paths

    def _convert_graph_node_to_entity(self, graph_node: GraphNode) -> EntityNode:
        """Convert GraphNode to EntityNode."""
        return EntityNode(
            id=graph_node.id,
            name=graph_node.name,
            type=graph_node.type,
            properties=graph_node.properties,
            confidence=graph_node.confidence,
        )

    def _convert_graph_edge_to_relationship(
        self, graph_edge: GraphEdge
    ) -> Relationship:
        """Convert GraphEdge to Relationship."""
        return Relationship(
            source_id=graph_edge.source_id,
            target_id=graph_edge.target_id,
            relationship_type=graph_edge.relationship_type,
            properties=graph_edge.properties,
            confidence=graph_edge.confidence,
        )

    async def query(
        self, query: str, query_type: str = "entity_relationship"
    ) -> KnowledgeGraphResult:
        """
        Query the knowledge graph.

        Args:
            query: The query string
            query_type: Type of query (entity_relationship, path_finding, entity_search)

        Returns:
            KnowledgeGraphResult with entities, relationships, and paths
        """
        # Extract entities from query
        entities = await self.extract_entities(query)

        # Process based on query type
        if query_type == "entity_relationship":
            result = await self.query_entity_relationships(query, entities)
        elif query_type == "path_finding":
            result = await self.query_path_finding(query, entities)
        elif query_type == "entity_search":
            result = await self.query_entity_search(query, entities)
        else:
            result = await self.query_general(query, entities)

        return result

    async def upsert_document_entities(
        self, document_id: str, content: str, metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Upsert entities extracted from a document into the knowledge graph.

        Args:
            document_id: Unique identifier for the document
            content: Document content to extract entities from
            metadata: Additional metadata for the document

        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract entities from content
            entities = await self.extract_entities_enhanced(content)

            if not entities:
                logger.debug(f"No entities found in document: {document_id}")
                return True

            # Create entity nodes
            created_entities = []
            for entity in entities:
                node_id = f"entity_{entity['text'].lower().replace(' ', '_')}"

                # Create or update entity node
                success = await self.graph_client.create_node(
                    node_id,
                    entity["type"],
                    {
                        "name": entity["text"],
                        "description": f"Entity extracted from document: {document_id}",
                        "confidence": entity["confidence"],
                        "source_document": document_id,
                        "source_type": (
                            metadata.get("source_type", "unknown")
                            if metadata
                            else "unknown"
                        ),
                        "extraction_timestamp": datetime.now().isoformat(),
                    },
                )

                if success:
                    created_entities.append(
                        {
                            "id": node_id,
                            "name": entity["text"],
                            "type": entity["type"],
                            "confidence": entity["confidence"],
                        }
                    )

            # Create relationships between entities in the same document
            if len(created_entities) > 1:
                await self._create_document_relationships(
                    created_entities, document_id, metadata
                )

            logger.info(
                f"Upserted {len(created_entities)} entities from document: {document_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to upsert document entities: {e}")
            return False

    async def _create_document_relationships(
        self, entities: List[Dict], document_id: str, metadata: Dict[str, Any] = None
    ) -> None:
        """Create relationships between entities from the same document."""
        try:
            # Create relationships between all pairs of entities
            for i, entity1 in enumerate(entities):
                for j, entity2 in enumerate(entities[i + 1 :], i + 1):
                    # Determine relationship type
                    relationship_type = self._determine_entity_relationship_type(
                        entity1, entity2
                    )

                    # Create relationship
                    await self.graph_client.create_edge(
                        entity1["id"],
                        entity2["id"],
                        relationship_type,
                        {
                            "description": f"Relationship from document: {document_id}",
                            "confidence": min(
                                entity1["confidence"], entity2["confidence"]
                            ),
                            "source_document": document_id,
                            "source_type": (
                                metadata.get("source_type", "unknown")
                                if metadata
                                else "unknown"
                            ),
                            "created_timestamp": datetime.now().isoformat(),
                        },
                    )

        except Exception as e:
            logger.error(f"Failed to create document relationships: {e}")

    def _determine_entity_relationship_type(self, entity1: Dict, entity2: Dict) -> str:
        """Determine relationship type between two entities."""
        type1 = entity1["type"].lower()
        type2 = entity2["type"].lower()

        # Technology relationships
        if any(
            tech in type1 or tech in type2
            for tech in ["technology", "framework", "tool"]
        ):
            return "is_related_to"

        # Language relationships
        if any(lang in type1 or lang in type2 for lang in ["language", "programming"]):
            return "works_with"

        # Organization relationships
        if any(org in type1 or org in type2 for org in ["organization", "company"]):
            return "collaborates_with"

        # Person relationships
        if any(
            person in type1 or person in type2 for person in ["person", "individual"]
        ):
            return "works_with"

        # Similar entities
        if type1 == type2:
            return "is_similar_to"

        # Default relationship
        return "is_related_to"

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the knowledge graph service."""
        return {
            "status": "healthy",
            "service_type": "knowledge_graph_service",
            "graph_client_connected": self.graph_client.connected,
            "entities_count": (
                len(self.mock_knowledge_graph["entities"])
                if hasattr(self, "mock_knowledge_graph")
                else 0
            ),
            "relationships_count": (
                len(self.mock_knowledge_graph["relationships"])
                if hasattr(self, "mock_knowledge_graph")
                else 0
            ),
            "last_updated": datetime.now().isoformat(),
        }
