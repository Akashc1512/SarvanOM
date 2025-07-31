"""
Pinecone and Neo4j integration with best practices for knowledge graphs and vector search.

This module provides:
- Pinecone vector database integration
- Neo4j knowledge graph integration
- Hybrid search capabilities
- Optimized performance and reliability
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple, Union, AsyncGenerator, Generator
from dataclasses import dataclass
from datetime import datetime, timezone
import uuid
import json

import numpy as np
# Pinecone imports only
from neo4j import AsyncGraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class VectorSearchResult:
    """Vector search result with metadata."""

    id: str
    score: float
    payload: Dict[str, Any]
    vector: Optional[List[float]] = None


@dataclass
class KnowledgeGraphResult:
    """Knowledge graph query result."""

    nodes: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    paths: List[List[Dict[str, Any]]]
    metadata: Dict[str, Any]


# PineconeVectorDB class only

    def __init__(
        self,
        url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        prefer_grpc: bool = True,
    ):
        self.url = url
        self.api_key = api_key
        self.timeout = timeout
        self.prefer_grpc = prefer_grpc
        self.client: Optional[PineconeClient] = None
        self._connection_pool = {}

    async def connect(self) -> bool:
        """Connect to Pinecone with connection pooling."""
        try:
            self.client = PineconeClient(api_key=self.api_key)
            # Test connection
            await self._test_connection()
            logger.info("Connected to Pinecone")
            return True
        except Exception as e:
            logger.error("Failed to connect to Pinecone", error=str(e))
            return False

    async def _test_connection(self) -> None:
        """Test Pinecone connection."""
        try:
            # Test Pinecone connection by listing indexes
            indexes = self.client.list_indexes()
            logger.debug(
                "Pinecone connection test successful",
                indexes_count=len(indexes),
            )
        except Exception as e:
            raise ConnectionError(f"Pinecone connection test failed: {e}")

    async def create_collection(
        self,
        collection_name: str,
        vector_size: int = 1536,
        distance: str = "Cosine",
        on_disk: bool = True,
        hnsw_config: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Create Pinecone index with optimized settings."""
        try:
            # Create Pinecone index with optimized settings
            self.client.create_index(
                name=collection_name,
                dimension=vector_size,
                metric="cosine",
            )

            logger.info(
                "Created Pinecone index",
                collection_name=collection_name,
                vector_size=vector_size,
            )
            return True
        except Exception as e:
            logger.error(
                "Failed to create Pinecone index",
                collection_name=collection_name,
                error=str(e),
            )
            return False

    async def upsert_vectors(
        self,
        collection_name: str,
        vectors: List[Tuple[str, List[float], Dict[str, Any]]],
        batch_size: int = 100,
    ) -> bool:
        """Upsert vectors in batches for optimal performance."""
        try:
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i : i + batch_size]

                points = []
                for vector_id, vector, payload in batch:
                    points.append(
                        models.PointStruct(id=vector_id, vector=vector, payload=payload)
                    )

                self.client.upsert(collection_name=collection_name, points=points)

                logger.debug(
                    "Upserted vector batch",
                    collection_name=collection_name,
                    batch_size=len(batch),
                    batch_number=i // batch_size + 1,
                )

            return True
        except Exception as e:
            logger.error(
                "Failed to upsert vectors",
                collection_name=collection_name,
                error=str(e),
            )
            return False

    async def search_vectors(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: float = 0.7,
        with_payload: bool = True,
        with_vectors: bool = False,
        filter_conditions: Optional[Dict[str, Any]] = None,
    ) -> List[VectorSearchResult]:
        """Search vectors with filtering and scoring."""
        try:
            # Build search filter
            search_filter = None
            if filter_conditions:
                search_filter = self._build_search_filter(filter_conditions)

            # Perform search
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=with_payload,
                with_vectors=with_vectors,
                query_filter=search_filter,
            )

            # Convert to standardized results
            results = []
            for point in search_result:
                results.append(
                    VectorSearchResult(
                        id=point.id,
                        score=point.score,
                        payload=point.payload,
                        vector=point.vector if with_vectors else None,
                    )
                )

            logger.debug(
                "Vector search completed",
                collection_name=collection_name,
                results_count=len(results),
                query_vector_size=len(query_vector),
            )
            return results
        except Exception as e:
            logger.error(
                "Vector search failed", collection_name=collection_name, error=str(e)
            )
            return []

    def _build_search_filter(self, conditions: Dict[str, Any]) -> models.Filter:
        """Build Pinecone search filter from conditions."""
        must_conditions = []
        should_conditions = []
        must_not_conditions = []

        for field, condition in conditions.items():
            if isinstance(condition, dict):
                # Handle range conditions
                if "gte" in condition or "lte" in condition:
                    range_filter = {}
                    if "gte" in condition:
                        range_filter["gte"] = condition["gte"]
                    if "lte" in condition:
                        range_filter["lte"] = condition["lte"]
                    must_conditions.append(
                        models.FieldCondition(
                            key=field, range=models.DatetimeRange(**range_filter)
                        )
                    )
                # Handle match conditions
                elif "match" in condition:
                    must_conditions.append(
                        models.FieldCondition(
                            key=field, match=models.MatchValue(value=condition["match"])
                        )
                    )
            else:
                # Simple equality
                must_conditions.append(
                    models.FieldCondition(
                        key=field, match=models.MatchValue(value=condition)
                    )
                )

        return models.Filter(
            must=must_conditions, should=should_conditions, must_not=must_not_conditions
        )

    async def delete_vectors(self, collection_name: str, vector_ids: List[str]) -> bool:
        """Delete vectors by IDs."""
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(points=vector_ids),
            )

            logger.info(
                "Deleted vectors",
                collection_name=collection_name,
                count=len(vector_ids),
            )
            return True
        except Exception as e:
            logger.error(
                "Failed to delete vectors",
                collection_name=collection_name,
                error=str(e),
            )
            return False

    async def get_collection_info(
        self, collection_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get collection information and statistics."""
        try:
            info = self.client.get_collection(collection_name)
            stats = self.client.get_collection(collection_name)

            return {
                "name": collection_name,
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance,
                "points_count": stats.points_count,
                "segments_count": stats.segments_count,
                "config": {
                    "on_disk": info.config.params.vectors.on_disk,
                    "hnsw_config": info.config.params.vectors.hnsw_config,
                },
            }
        except Exception as e:
            logger.error(
                "Failed to get collection info",
                collection_name=collection_name,
                error=str(e),
            )
            return None


class Neo4jKnowledgeGraph:
    """Neo4j knowledge graph integration with best practices."""

    def __init__(
        self,
        uri: str,
        username: str,
        password: str,
        database: str = "neo4j",
        max_connection_lifetime: int = 3600,
        max_connection_pool_size: int = 50,
    ):
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self.max_connection_lifetime = max_connection_lifetime
        self.max_connection_pool_size = max_connection_pool_size
        self.driver: Optional[AsyncGraphDatabase] = None

    async def connect(self) -> bool:
        """Connect to Neo4j with connection pooling."""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                max_connection_lifetime=self.max_connection_lifetime,
                max_connection_pool_size=self.max_connection_pool_size,
            )

            # Test connection
            await self._test_connection()
            logger.info("Connected to Neo4j", uri=self.uri)
            return True
        except Exception as e:
            logger.error("Failed to connect to Neo4j", error=str(e))
            return False

    async def _test_connection(self) -> None:
        """Test Neo4j connection."""
        try:
            async with self.driver.session(database=self.database) as session:
                result = await session.run("RETURN 1 as test")
                record = await result.single()
                if record["test"] != 1:
                    raise ConnectionError("Neo4j connection test failed")
        except Exception as e:
            raise ConnectionError(f"Neo4j connection test failed: {e}")

    async def create_constraints(self) -> bool:
        """Create database constraints for data integrity."""
        try:
            constraints = [
                "CREATE CONSTRAINT unique_user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE",
                "CREATE CONSTRAINT unique_knowledge_item_id IF NOT EXISTS FOR (k:KnowledgeItem) REQUIRE k.id IS UNIQUE",
                "CREATE CONSTRAINT unique_concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE",
                "CREATE INDEX user_email_index IF NOT EXISTS FOR (u:User) ON (u.email)",
                "CREATE INDEX knowledge_item_type_index IF NOT EXISTS FOR (k:KnowledgeItem) ON (k.type)",
                "CREATE INDEX concept_name_index IF NOT EXISTS FOR (c:Concept) ON (c.name)",
            ]

            async with self.driver.session(database=self.database) as session:
                for constraint in constraints:
                    await session.run(constraint)

            logger.info("Created Neo4j constraints and indexes")
            return True
        except Exception as e:
            logger.error("Failed to create Neo4j constraints", error=str(e))
            return False

    async def create_knowledge_node(
        self, node_id: str, node_type: str, properties: Dict[str, Any]
    ) -> bool:
        """Create knowledge graph node."""
        try:
            query = f"""
            MERGE (n:{node_type} {{id: $node_id}})
            SET n += $properties
            RETURN n
            """

            async with self.driver.session(database=self.database) as session:
                await session.run(query, node_id=node_id, properties=properties)

            logger.debug("Created knowledge node", node_id=node_id, node_type=node_type)
            return True
        except Exception as e:
            logger.error(
                "Failed to create knowledge node", node_id=node_id, error=str(e)
            )
            return False

    async def create_relationship(
        self,
        from_node_id: str,
        to_node_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Create relationship between nodes."""
        try:
            query = f"""
            MATCH (a {{id: $from_id}})
            MATCH (b {{id: $to_id}})
            MERGE (a)-[r:{relationship_type}]->(b)
            SET r += $properties
            RETURN r
            """

            async with self.driver.session(database=self.database) as session:
                await session.run(
                    query,
                    from_id=from_node_id,
                    to_id=to_node_id,
                    properties=properties or {},
                )

            logger.debug(
                "Created relationship",
                from_id=from_node_id,
                to_id=to_node_id,
                relationship_type=relationship_type,
            )
            return True
        except Exception as e:
            logger.error("Failed to create relationship", error=str(e))
            return False

    async def query_knowledge_graph(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> KnowledgeGraphResult:
        """Execute Cypher query and return structured results."""
        try:
            async with self.driver.session(database=self.database) as session:
                result = await session.run(query, parameters or {})
                records = await result.data()

            # Parse results into structured format
            nodes = []
            relationships = []
            paths = []

            for record in records:
                # Extract nodes
                for key, value in record.items():
                    if hasattr(value, "labels"):  # Node
                        nodes.append(
                            {
                                "id": value.get("id"),
                                "labels": list(value.labels),
                                "properties": dict(value),
                            }
                        )
                    elif hasattr(value, "type"):  # Relationship
                        relationships.append(
                            {
                                "id": value.get("id"),
                                "type": value.type,
                                "start_node": value.start_node.get("id"),
                                "end_node": value.end_node.get("id"),
                                "properties": dict(value),
                            }
                        )
                    elif isinstance(value, list):  # Path
                        path_nodes = []
                        path_rels = []
                        for item in value:
                            if hasattr(item, "labels"):
                                path_nodes.append(
                                    {
                                        "id": item.get("id"),
                                        "labels": list(item.labels),
                                        "properties": dict(item),
                                    }
                                )
                            elif hasattr(item, "type"):
                                path_rels.append(
                                    {
                                        "id": item.get("id"),
                                        "type": item.type,
                                        "start_node": item.start_node.get("id"),
                                        "end_node": item.end_node.get("id"),
                                        "properties": dict(item),
                                    }
                                )
                        if path_nodes or path_rels:
                            paths.append(
                                {"nodes": path_nodes, "relationships": path_rels}
                            )

            return KnowledgeGraphResult(
                nodes=nodes,
                relationships=relationships,
                paths=paths,
                metadata={"query": query, "parameters": parameters},
            )
        except Exception as e:
            logger.error("Knowledge graph query failed", error=str(e))
            return KnowledgeGraphResult([], [], [], {"error": str(e)})

    async def find_similar_concepts(
        self, concept_id: str, relationship_type: str = "SIMILAR_TO", limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find similar concepts in knowledge graph."""
        query = f"""
        MATCH (c1 {{id: $concept_id}})-[r:{relationship_type}]-(c2)
        RETURN c2, r.similarity as similarity
        ORDER BY r.similarity DESC
        LIMIT $limit
        """

        result = await self.query_knowledge_graph(
            query, {"concept_id": concept_id, "limit": limit}
        )

        return [
            {
                "concept": node["properties"],
                "similarity": rel["properties"].get("similarity", 0.0),
            }
            for node, rel in zip(result.nodes, result.relationships)
        ]

    async def get_knowledge_path(
        self, start_node_id: str, end_node_id: str, max_depth: int = 3
    ) -> List[List[Dict[str, Any]]]:
        """Find paths between two nodes in knowledge graph."""
        query = f"""
        MATCH path = (start {{id: $start_id}})-[*1..{max_depth}]-(end {{id: $end_id}})
        RETURN path
        ORDER BY length(path)
        LIMIT 10
        """

        result = await self.query_knowledge_graph(
            query, {"start_id": start_node_id, "end_id": end_node_id}
        )

        return result.paths


class HybridSearchEngine:
    """Hybrid search combining vector and knowledge graph search."""

    def __init__(self, vector_db: PineconeVectorDB, knowledge_graph: Neo4jKnowledgeGraph):
        self.vector_db = vector_db
        self.knowledge_graph = knowledge_graph

    async def hybrid_search(
        self,
        query: str,
        query_vector: List[float],
        collection_name: str = "knowledge_base",
        vector_weight: float = 0.7,
        graph_weight: float = 0.3,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search combining vector and graph results."""
        try:
            # Vector search
            vector_results = await self.vector_db.search_vectors(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit * 2,  # Get more for re-ranking
                score_threshold=0.5,
            )

            # Knowledge graph search
            graph_results = await self._search_knowledge_graph(query, limit * 2)

            # Combine and re-rank results
            combined_results = self._combine_results(
                vector_results, graph_results, vector_weight, graph_weight
            )

            # Return top results
            return combined_results[:limit]
        except Exception as e:
            logger.error("Hybrid search failed", error=str(e))
            return []

    async def _search_knowledge_graph(
        self, query: str, limit: int
    ) -> List[Dict[str, Any]]:
        """Search knowledge graph for relevant concepts."""
        # This is a simplified implementation
        # In production, you'd use more sophisticated graph queries
        cypher_query = """
        MATCH (c:Concept)
        WHERE c.name CONTAINS $query OR c.description CONTAINS $query
        RETURN c, 0.8 as score
        LIMIT $limit
        """

        result = await self.knowledge_graph.query_knowledge_graph(
            cypher_query, {"query": query, "limit": limit}
        )

        return [
            {
                "id": node["properties"].get("id"),
                "score": 0.8,  # Simplified scoring
                "source": "knowledge_graph",
                "content": node["properties"].get("description", ""),
                "metadata": node["properties"],
            }
            for node in result.nodes
        ]

    def _combine_results(
        self,
        vector_results: List[VectorSearchResult],
        graph_results: List[Dict[str, Any]],
        vector_weight: float,
        graph_weight: float,
    ) -> List[Dict[str, Any]]:
        """Combine and re-rank search results."""
        combined = {}

        # Process vector results
        for result in vector_results:
            combined[result.id] = {
                "id": result.id,
                "vector_score": result.score,
                "graph_score": 0.0,
                "combined_score": result.score * vector_weight,
                "content": result.payload.get("content", ""),
                "metadata": result.payload,
                "sources": ["vector"],
            }

        # Process graph results
        for result in graph_results:
            if result["id"] in combined:
                # Update existing result
                combined[result["id"]]["graph_score"] = result["score"]
                combined[result["id"]]["combined_score"] += (
                    result["score"] * graph_weight
                )
                combined[result["id"]]["sources"].append("graph")
            else:
                # Add new result
                combined[result["id"]] = {
                    "id": result["id"],
                    "vector_score": 0.0,
                    "graph_score": result["score"],
                    "combined_score": result["score"] * graph_weight,
                    "content": result["content"],
                    "metadata": result["metadata"],
                    "sources": ["graph"],
                }

        # Sort by combined score
        sorted_results = sorted(
            combined.values(), key=lambda x: x["combined_score"], reverse=True
        )

        return sorted_results


# Export main classes
__all__ = [
    "PineconeVectorDB",
    "Neo4jKnowledgeGraph",
    "HybridSearchEngine",
    "VectorSearchResult",
    "KnowledgeGraphResult",
]
