"""
ArangoDB Knowledge Graph Agent Implementation
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from shared.core.agents.base_agent import (
    BaseAgent,
    AgentType,
    AgentResult,
    QueryContext,
)
from shared.core.agents.data_models import KnowledgeGraphResult
from shared.core.agents.agent_utilities import (
    AgentTaskProcessor,
    ResponseFormatter,
    time_agent_function,
)
from shared.core.agents.validation_utilities import CommonValidators

# Configure logging
from shared.core.unified_logging import get_logger

logger = get_logger(__name__)


class ArangoDBKnowledgeGraphAgent(BaseAgent):
    """
    ArangoDB Knowledge Graph Agent for querying and managing knowledge graphs.
    """

    def __init__(self):
        """Initialize the ArangoDB knowledge graph agent."""
        super().__init__(
            agent_id="arangodb_knowledge_graph_agent",
            agent_type=AgentType.KNOWLEDGE_GRAPH,
        )

        # Initialize shared utilities
        self.task_processor = AgentTaskProcessor(self.agent_id)
        self.logger = get_logger(f"{__name__}.{self.agent_id}")

        # Initialize knowledge service and graph client
        from shared.core.services.knowledge_service import KnowledgeService
        from shared.core.services.graph_client import ArangoDBGraphClient

        self.knowledge_service = KnowledgeService()
        self.graph_client = ArangoDBGraphClient()

        logger.info("✅ ArangoDB KnowledgeGraphAgent initialized successfully")

    @time_agent_function("arangodb_knowledge_graph_agent")
    async def process_task(
        self, task: Dict[str, Any], context: QueryContext
    ) -> Dict[str, Any]:
        """
        Process knowledge graph query task using shared utilities.

        This method now uses the standardized workflow from AgentTaskProcessor
        to eliminate duplicate logic and ensure consistent behavior.
        """
        # Use shared task processor with validation
        result = await self.task_processor.process_task_with_workflow(
            task=task,
            context=context,
            processing_func=self._process_knowledge_graph_task,
            validation_func=CommonValidators.validate_query_input,
            timeout_seconds=60,
        )

        # Convert TaskResult to standard response format
        return ResponseFormatter.format_agent_response(
            success=result.success,
            data=result.data,
            error=result.error,
            confidence=result.confidence,
            execution_time_ms=result.execution_time_ms,
            metadata=result.metadata,
        )

    async def _process_knowledge_graph_task(
        self, task: Dict[str, Any], context: QueryContext
    ) -> Dict[str, Any]:
        """
        Process knowledge graph query task.

        Args:
            task: Task containing query and parameters
            context: Query context

        Returns:
            Knowledge graph query results
        """
        query = task.get("query", context.query)
        query_type = task.get("query_type", "entity_relationship")

        logger.info(f"🔍 Processing ArangoDB knowledge graph query: {query[:50]}...")

        # Use the knowledge service to process the query
        result = await self.knowledge_service.query(query, query_type)

        # Create agent result
        return {
            "data": result,
            "confidence": result.confidence,
            "metadata": {
                "query_type": query_type,
                "entities_found": len(result.entities),
                "relationships_found": len(result.relationships),
                "paths_found": len(result.paths),
                "arangodb_connected": self.graph_client.connected,
            },
        }

    async def query(
        self, query: str, query_type: str = "entity_relationship"
    ) -> KnowledgeGraphResult:
        """
        Query the knowledge graph using ArangoDB.

        Args:
            query: The query string
            query_type: Type of query (entity_relationship, path_finding, entity_search)

        Returns:
            KnowledgeGraphResult with entities, relationships, and paths
        """
        return await self.knowledge_service.query(query, query_type)

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
        return await self.knowledge_service.upsert_document_entities(
            document_id, content, metadata
        )

    async def upsert_document_entities_enhanced(
        self, document_id: str, content: str, metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Enhanced upsert of entities extracted from a document into the knowledge graph.

        Args:
            document_id: Unique identifier for the document
            content: Document content to extract entities from
            metadata: Additional metadata for the document

        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract entities from content using enhanced extraction
            entities = await self.knowledge_service.extract_entities_enhanced(content)

            if not entities:
                logger.debug(f"No entities found in document: {document_id}")
                return True

            # Create entity nodes with enhanced metadata
            created_entities = []
            for entity in entities:
                node_id = f"entity_{entity['text'].lower().replace(' ', '_').replace('-', '_')}"

                # Enhanced properties
                properties = {
                    "name": entity["text"],
                    "description": entity.get(
                        "description", f"Entity extracted from document: {document_id}"
                    ),
                    "confidence": entity["confidence"],
                    "relevance": entity.get("relevance", "medium"),
                    "source_document": document_id,
                    "source_type": (
                        metadata.get("source_type", "unknown")
                        if metadata
                        else "unknown"
                    ),
                    "extraction_timestamp": datetime.now().isoformat(),
                    "content_preview": (
                        content[:200] + "..." if len(content) > 200 else content
                    ),
                }

                # Create or update entity node
                success = await self.graph_client.create_node(
                    node_id, entity["type"], properties
                )

                if success:
                    created_entities.append(
                        {
                            "id": node_id,
                            "name": entity["text"],
                            "type": entity["type"],
                            "confidence": entity["confidence"],
                            "properties": properties,
                        }
                    )

            # Create enhanced relationships between entities
            if len(created_entities) > 1:
                await self._create_enhanced_document_relationships(
                    created_entities, document_id, metadata, content
                )

            # Link to existing entities in the graph
            await self._link_to_existing_entities(
                created_entities, document_id, metadata
            )

            logger.info(
                f"Enhanced upsert of {len(created_entities)} entities from document: {document_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to enhanced upsert document entities: {e}")
            return False

    async def _create_enhanced_document_relationships(
        self,
        entities: List[Dict],
        document_id: str,
        metadata: Dict[str, Any] = None,
        content: str = "",
    ) -> None:
        """
        Create enhanced relationships between entities from the same document.

        Args:
            entities: List of entity dictionaries
            document_id: Source document ID
            metadata: Document metadata
            content: Document content for context
        """
        try:
            # Create relationships between all pairs of entities
            for i, entity1 in enumerate(entities):
                for j, entity2 in enumerate(entities[i + 1 :], i + 1):
                    # Determine enhanced relationship type
                    relationship_type = (
                        self._determine_enhanced_entity_relationship_type(
                            entity1, entity2, content
                        )
                    )

                    # Calculate relationship strength
                    relationship_strength = self._calculate_relationship_strength(
                        entity1, entity2, content
                    )

                    # Create relationship with enhanced properties
                    await self.graph_client.create_edge(
                        entity1["id"],
                        entity2["id"],
                        relationship_type,
                        {
                            "description": f"Enhanced relationship from document: {document_id}",
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
                            "relationship_strength": relationship_strength,
                            "content_context": (
                                content[:100] + "..." if len(content) > 100 else content
                            ),
                        },
                    )

        except Exception as e:
            logger.error(f"Failed to create enhanced document relationships: {e}")

    async def _link_to_existing_entities(
        self,
        new_entities: List[Dict],
        document_id: str,
        metadata: Dict[str, Any] = None,
    ) -> None:
        """
        Link new entities to existing entities in the knowledge graph.

        Args:
            new_entities: List of new entity dictionaries
            document_id: Source document ID
            metadata: Document metadata
        """
        try:
            for new_entity in new_entities:
                # Query for similar existing entities
                similar_entities = await self.query_related_entities(
                    [new_entity["name"]], max_depth=1
                )

                for existing_entity in similar_entities.entities:
                    if existing_entity.name != new_entity["name"]:
                        # Create relationship to existing entity
                        relationship_type = (
                            self._determine_enhanced_entity_relationship_type(
                                new_entity,
                                {
                                    "name": existing_entity.name,
                                    "type": existing_entity.type,
                                },
                                "",
                            )
                        )

                        await self.graph_client.create_edge(
                            new_entity["id"],
                            existing_entity.id,
                            relationship_type,
                            {
                                "description": f"Link from document: {document_id}",
                                "confidence": new_entity["confidence"],
                                "source_document": document_id,
                                "source_type": (
                                    metadata.get("source_type", "unknown")
                                    if metadata
                                    else "unknown"
                                ),
                                "created_timestamp": datetime.now().isoformat(),
                                "link_type": "document_to_existing",
                            },
                        )

        except Exception as e:
            logger.error(f"Failed to link to existing entities: {e}")

    def _determine_enhanced_entity_relationship_type(
        self, entity1: Dict, entity2: Dict, content: str = ""
    ) -> str:
        """
        Determine enhanced relationship type between two entities.

        Args:
            entity1: First entity
            entity2: Second entity
            content: Document content for context

        Returns:
            Relationship type
        """
        # Enhanced relationship type determination
        type1 = entity1["type"].lower()
        type2 = entity2["type"].lower()
        name1 = entity1["name"].lower()
        name2 = entity2["name"].lower()

        # Check content for relationship indicators
        content_lower = content.lower()

        # Technology relationships
        if any(
            tech in type1 or tech in type2
            for tech in ["technology", "framework", "tool"]
        ):
            if any(word in content_lower for word in ["enables", "supports", "powers"]):
                return "enables"
            elif any(
                word in content_lower for word in ["requires", "needs", "depends"]
            ):
                return "requires"
            else:
                return "is_related_to"

        # Language relationships
        if any(lang in type1 or lang in type2 for lang in ["language", "programming"]):
            if any(
                word in content_lower
                for word in ["used with", "compatible", "works with"]
            ):
                return "works_with"
            else:
                return "is_related_to"

        # Organization relationships
        if any(org in type1 or org in type2 for org in ["organization", "company"]):
            if any(
                word in content_lower
                for word in ["partners", "collaborates", "works with"]
            ):
                return "collaborates_with"
            else:
                return "is_related_to"

        # Person relationships
        if any(
            person in type1 or person in type2 for person in ["person", "individual"]
        ):
            if any(
                word in content_lower
                for word in ["works with", "collaborates", "teams"]
            ):
                return "works_with"
            else:
                return "is_related_to"

        # Similar entities
        if type1 == type2:
            return "is_similar_to"

        # Default relationship
        return "is_related_to"

    def _calculate_relationship_strength(
        self, entity1: Dict, entity2: Dict, content: str
    ) -> float:
        """
        Calculate the strength of relationship between two entities.

        Args:
            entity1: First entity
            entity2: Second entity
            content: Document content

        Returns:
            Relationship strength (0.0 to 1.0)
        """
        # Base strength on entity confidence
        base_strength = min(entity1["confidence"], entity2["confidence"])

        # Boost strength if entities appear close together in content
        if content:
            content_lower = content.lower()
            name1 = entity1["name"].lower()
            name2 = entity2["name"].lower()

            if name1 in content_lower and name2 in content_lower:
                # Find positions of both entities
                pos1 = content_lower.find(name1)
                pos2 = content_lower.find(name2)

                # Calculate distance
                distance = abs(pos1 - pos2)

                # Closer entities get higher strength
                if distance < 50:
                    base_strength += 0.2
                elif distance < 100:
                    base_strength += 0.1
                elif distance < 200:
                    base_strength += 0.05

        return min(1.0, base_strength)

    async def maintain_graph_consistency(self) -> bool:
        """
        Maintain consistency of the knowledge graph by cleaning up orphaned nodes and relationships.

        Returns:
            True if successful, False otherwise
        """
        return await self.graph_client.maintain_consistency()

    async def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge graph.

        Returns:
            Dictionary with graph statistics
        """
        return await self.graph_client.get_graph_statistics()

    async def query_related_entities(
        self, query_entities: List[str], max_depth: int = 2
    ) -> KnowledgeGraphResult:
        """
        Query for entities related to the given query entities.

        Args:
            query_entities: List of entity names to search for
            max_depth: Maximum depth for relationship traversal

        Returns:
            KnowledgeGraphResult with related entities and relationships
        """
        try:
            if not self.graph_client.connected:
                return await self._query_mock_related_entities(query_entities)

            # Build AQL query for related entities
            aql_query = """
            FOR entity IN entities
            FOR rel IN relationships
            LET related_entity = DOCUMENT(rel._to)
            FILTER entity.name IN @query_entities OR related_entity.name IN @query_entities
            RETURN {
                entity: entity,
                relationship: rel,
                related_entity: related_entity
            }
            LIMIT 50
            """

            parameters = {"query_entities": query_entities}
            result = await self.graph_client.execute_query(aql_query, parameters)

            # Parse results
            found_entities = []
            found_relationships = []
            entity_ids = set()

            for record in result:
                if "entity" in record and record["entity"]:
                    entity = record["entity"]
                    if entity["_id"] not in entity_ids:
                        found_entities.append(
                            self.knowledge_service._convert_graph_node_to_entity(
                                self.graph_client.GraphNode(
                                    id=entity.get("id", ""),
                                    name=entity.get("name", ""),
                                    type=entity.get("type", "Node"),
                                    properties=entity,
                                )
                            )
                        )
                        entity_ids.add(entity["_id"])

                if "related_entity" in record and record["related_entity"]:
                    related_entity = record["related_entity"]
                    if related_entity["_id"] not in entity_ids:
                        found_entities.append(
                            self.knowledge_service._convert_graph_node_to_entity(
                                self.graph_client.GraphNode(
                                    id=related_entity.get("id", ""),
                                    name=related_entity.get("name", ""),
                                    type=related_entity.get("type", "Node"),
                                    properties=related_entity,
                                )
                            )
                        )
                        entity_ids.add(related_entity["_id"])

                if "relationship" in record and record["relationship"]:
                    rel = record["relationship"]
                    found_relationships.append(
                        self.knowledge_service._convert_graph_edge_to_relationship(
                            self.graph_client.GraphEdge(
                                source_id=rel.get("_from", ""),
                                target_id=rel.get("_to", ""),
                                relationship_type=rel.get("type", ""),
                                properties=rel,
                            )
                        )
                    )

            return KnowledgeGraphResult(
                entities=found_entities,
                relationships=found_relationships,
                paths=[],
                query_entities=query_entities,
                confidence=0.9 if found_entities else 0.3,
                processing_time_ms=0,
                metadata={
                    "query_type": "related_entities",
                    "entities_found": len(found_entities),
                    "relationships_found": len(found_relationships),
                    "max_depth": max_depth,
                },
            )

        except Exception as e:
            logger.error(f"Failed to query related entities: {e}")
            return await self._query_mock_related_entities(query_entities)

    async def _query_mock_related_entities(
        self, query_entities: List[str]
    ) -> KnowledgeGraphResult:
        """Mock implementation for related entities query."""
        found_entities = []
        found_relationships = []

        # Find entities in mock knowledge graph
        for entity_name in query_entities:
            for entity_id, entity_data in self.knowledge_service.mock_knowledge_graph[
                "entities"
            ].items():
                if entity_name.lower() in entity_data["name"].lower():
                    found_entities.append(
                        self.knowledge_service.EntityNode(
                            id=entity_id,
                            name=entity_data["name"],
                            type=entity_data["type"],
                            properties=entity_data["properties"],
                        )
                    )

        # Find relationships involving these entities
        for rel in self.knowledge_service.mock_knowledge_graph["relationships"]:
            source_entity = next(
                (e for e in found_entities if e.id == rel["source"]), None
            )
            target_entity = next(
                (e for e in found_entities if e.id == rel["target"]), None
            )

            if source_entity and target_entity:
                found_relationships.append(
                    self.knowledge_service.Relationship(
                        source_id=rel["source"],
                        target_id=rel["target"],
                        relationship_type=rel["type"],
                        properties=rel["properties"],
                    )
                )

        return KnowledgeGraphResult(
            entities=found_entities,
            relationships=found_relationships,
            paths=[],
            query_entities=query_entities,
            confidence=0.85 if found_entities else 0.3,
            processing_time_ms=0,
            metadata={
                "query_type": "related_entities",
                "entities_found": len(found_entities),
                "relationships_found": len(found_relationships),
                "mock_data": True,
            },
        )

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the ArangoDB knowledge graph agent."""
        return {
            "status": "healthy" if self.graph_client.connected else "disconnected",
            "agent_type": "arangodb_knowledge_graph",
            "arangodb_connected": self.graph_client.connected,
            "arangodb_url": self.graph_client.arango_url,
            "entities_count": (
                len(self.knowledge_service.mock_knowledge_graph["entities"])
                if hasattr(self.knowledge_service, "mock_knowledge_graph")
                else 0
            ),
            "relationships_count": (
                len(self.knowledge_service.mock_knowledge_graph["relationships"])
                if hasattr(self.knowledge_service, "mock_knowledge_graph")
                else 0
            ),
            "last_updated": datetime.now().isoformat(),
        }
