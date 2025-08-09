"""
Vector database integration for hybrid search.
Supports Pinecone, Qdrant, and other vector databases.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    logging.warning(
        "python-dotenv not available. Install with: pip install python-dotenv"
    )

import pinecone
from pinecone import Pinecone, ServerlessSpec

try:
    from arango import ArangoClient

    ARANGO_AVAILABLE = True
except ImportError:
    ARANGO_AVAILABLE = False
    logging.warning(
        "ArangoDB driver not available. Install with: pip install python-arango"
    )

logger = logging.getLogger(__name__)


@dataclass
class VectorSearchResult:
    """Result from vector search operation."""

    id: str
    score: float
    metadata: Dict[str, Any]
    content: str


@dataclass
class KnowledgeGraphResult:
    """Result from knowledge graph query."""

    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    paths: List[List[Dict[str, Any]]]
    query_entities: List[str]
    confidence: float
    processing_time_ms: float
    metadata: Dict[str, Any]


class PineconeVectorDB:
    """Pinecone vector database integration with best practices."""

    def __init__(
        self,
        api_key: str,
        environment: str,
        index_name: str = "knowledge-base",
        dimension: int = 1536,
        metric: str = "cosine",
        max_connection_lifetime: int = 3600,
        max_connection_pool_size: int = 50,
    ):
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric
        self.max_connection_lifetime = max_connection_lifetime
        self.max_connection_pool_size = max_connection_pool_size
        self.pc: Optional[Pinecone] = None
        self.index = None
        self.connected = False

        # Initialize connection
        asyncio.create_task(self._initialize_connection())

    async def _initialize_connection(self) -> None:
        """Initialize Pinecone connection with connection pooling."""
        try:
            # Initialize Pinecone
            import pinecone

            pinecone.init(api_key=self.api_key, environment=self.environment)
            self.pc = pinecone

            # Test connection
            await self._test_connection()
            self.connected = True
            logger.info(f"Connected to Pinecone (environment: {self.environment})")

        except Exception as e:
            logger.error(f"Failed to connect to Pinecone: {e}")
            self.connected = False

    async def _test_connection(self) -> None:
        """Test Pinecone connection."""
        try:
            # List indexes to test connection
            indexes = self.pc.list_indexes()
            if not indexes:
                raise ConnectionError("Pinecone connection test failed")

        except Exception as e:
            raise ConnectionError(f"Pinecone connection test failed: {e}")

    async def create_index(self) -> bool:
        """Create Pinecone index if it doesn't exist."""
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()

            if self.index_name not in [idx.name for idx in existing_indexes]:
                # Create index
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric,
                    spec=ServerlessSpec(cloud="aws", region="us-west-2"),
                )
                logger.info(f"Created Pinecone index: {self.index_name}")
            else:
                logger.info(f"Pinecone index already exists: {self.index_name}")

            # Get index
            self.index = self.pc.Index(self.index_name)
            return True

        except Exception as e:
            logger.error(f"Failed to create Pinecone index: {e}")
            return False

    async def upsert_vectors(
        self, vectors: List[Tuple[str, List[float], Dict[str, Any]]]
    ) -> bool:
        """Upsert vectors to Pinecone index."""
        try:
            if not self.index:
                await self.create_index()

            # Prepare vectors for upsert
            upsert_data = []
            for vector_id, vector, metadata in vectors:
                upsert_data.append(
                    {"id": vector_id, "values": vector, "metadata": metadata}
                )

            # Upsert in batches
            batch_size = 100
            for i in range(0, len(upsert_data), batch_size):
                batch = upsert_data[i : i + batch_size]
                self.index.upsert(vectors=batch)

            logger.info(f"Upserted vectors to Pinecone: {len(vectors)} vectors")
            return True

        except Exception as e:
            logger.error(f"Failed to upsert vectors to Pinecone: {e}")
            return False

    async def search_vectors(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True,
    ) -> List[VectorSearchResult]:
        """Search vectors in Pinecone index."""
        try:
            if not self.index:
                await self.create_index()

            # Perform search
            search_kwargs = {
                "vector": query_vector,
                "top_k": top_k,
                "include_metadata": include_metadata,
            }

            if filter:
                search_kwargs["filter"] = filter

            results = self.index.query(**search_kwargs)

            # Parse results
            search_results = []
            for match in results.matches:
                search_results.append(
                    VectorSearchResult(
                        id=match.id,
                        score=match.score,
                        metadata=match.metadata or {},
                        content=(
                            match.metadata.get("content", "") if match.metadata else ""
                        ),
                    )
                )

            logger.info(
                "Searched vectors in Pinecone", results_count=len(search_results)
            )
            return search_results

        except Exception as e:
            logger.error(f"Failed to search vectors in Pinecone: {e}")
            return []

    async def delete_vectors(self, vector_ids: List[str]) -> bool:
        """Delete vectors from Pinecone index."""
        try:
            if not self.index:
                await self.create_index()

            # Delete vectors
            self.index.delete(ids=vector_ids)

            logger.info("Deleted vectors from Pinecone", count=len(vector_ids))
            return True

        except Exception as e:
            logger.error(f"Failed to delete vectors from Pinecone: {e}")
            return False

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of Pinecone vector database."""
        return {
            "status": "healthy" if self.connected else "disconnected",
            "database_type": "pinecone",
            "index_name": self.index_name,
            "environment": self.environment,
            "dimension": self.dimension,
            "metric": self.metric,
            "last_updated": datetime.now().isoformat(),
        }


class ArangoDBKnowledgeGraph:
    """ArangoDB knowledge graph integration with best practices."""

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        database: str = "knowledge_graph",
        max_connection_lifetime: int = 3600,
        max_connection_pool_size: int = 50,
    ):
        self.url = url
        self.username = username
        self.password = password
        self.database = database
        self.max_connection_lifetime = max_connection_lifetime
        self.max_connection_pool_size = max_connection_pool_size
        self.client: Optional[ArangoClient] = None
        self.db = None
        self.connected = False

        # Initialize connection
        asyncio.create_task(self._initialize_connection())

    async def _initialize_connection(self) -> None:
        """Initialize ArangoDB connection with connection pooling."""
        try:
            # Create ArangoDB client
            self.client = ArangoClient(hosts=self.url)

            # Test connection
            await self._test_connection()
            self.connected = True
            logger.info("Connected to ArangoDB", url=self.url)

        except Exception as e:
            logger.error(f"Failed to connect to ArangoDB: {e}")
            self.connected = False

    async def _test_connection(self) -> None:
        """Test ArangoDB connection."""
        try:
            # Test connection by getting server info
            self.db = self.client.db(
                name=self.database, username=self.username, password=self.password
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

            logger.info("Created ArangoDB constraints and indexes")
            return True
        except Exception as e:
            logger.error(f"Failed to create ArangoDB constraints: {e}")
            return False

    async def create_knowledge_node(
        self, node_id: str, node_type: str, properties: Dict[str, Any]
    ) -> bool:
        """Create knowledge graph node in ArangoDB."""
        try:
            entities_collection = self.db.collection("entities")

            # Create node document
            node_doc = {"_key": node_id, "id": node_id, "type": node_type, **properties}

            entities_collection.insert(node_doc, overwrite=True)

            logger.debug("Created knowledge node", node_id=node_id)
            return True
        except Exception as e:
            logger.error(f"Failed to create knowledge node {node_id}: {e}")
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
                **(properties or {}),
            }

            relationships_collection.insert(edge_doc)

            logger.debug(
                "Created relationship",
                from_node=from_node_id,
                to_node=to_node_id,
                type=relationship_type,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to create relationship: {e}")
            return False

    async def query_knowledge_graph(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> KnowledgeGraphResult:
        """Execute AQL query and return structured results."""
        try:
            if not self.db:
                raise ConnectionError("ArangoDB not connected")

            # Execute query
            result = self.db.aql.execute(query, parameters or {})

            # Parse results
            entities = []
            relationships = []
            paths = []

            for record in result:
                # Extract entities and relationships from record
                if "entity" in record:
                    entities.append(record["entity"])
                if "relationship" in record:
                    relationships.append(record["relationship"])
                if "path" in record:
                    paths.append(record["path"])

            return KnowledgeGraphResult(
                entities=entities,
                relationships=relationships,
                paths=paths,
                query_entities=[],
                confidence=0.9 if entities or relationships else 0.3,
                processing_time_ms=0,
                metadata={
                    "query": query,
                    "parameters": parameters,
                    "entities_found": len(entities),
                    "relationships_found": len(relationships),
                    "paths_found": len(paths),
                },
            )

        except Exception as e:
            logger.error(f"ArangoDB query failed: {e}")
            return []

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of ArangoDB knowledge graph."""
        return {
            "status": "healthy" if self.connected else "disconnected",
            "database_type": "arangodb",
            "url": self.url,
            "database": self.database,
            "last_updated": datetime.now().isoformat(),
        }


class HybridSearchEngine:
    """
    Hybrid search engine combining vector search and knowledge graph queries.

    This engine provides:
    - Vector similarity search via Pinecone
    - Knowledge graph traversal via ArangoDB
    - Combined results with relevance scoring
    - Semantic understanding of relationships
    """

    def __init__(
        self, vector_db: PineconeVectorDB, knowledge_graph: ArangoDBKnowledgeGraph
    ):
        self.vector_db = vector_db
        self.knowledge_graph = knowledge_graph
        self.logger = logging.getLogger(__name__)

    async def hybrid_search(
        self,
        query: str,
        query_vector: List[float],
        top_k: int = 10,
        vector_weight: float = 0.7,
        graph_weight: float = 0.3,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining vector similarity and knowledge graph.

        Args:
            query: Text query for semantic understanding
            query_vector: Vector representation of the query
            top_k: Number of results to return
            vector_weight: Weight for vector similarity scores
            graph_weight: Weight for knowledge graph relevance
            filter: Optional filter for vector search

        Returns:
            Combined search results with relevance scores
        """
        start_time = time.time()

        try:
            # Perform vector search
            vector_results = await self.vector_db.search_vectors(
                query_vector=query_vector,
                top_k=top_k * 2,  # Get more results for better combination
                filter=filter,
            )

            # Perform knowledge graph search
            graph_results = await self._search_knowledge_graph(query)

            # Combine results
            combined_results = await self._combine_results(
                vector_results=vector_results,
                graph_results=graph_results,
                vector_weight=vector_weight,
                graph_weight=graph_weight,
            )

            # Sort by combined score and return top_k
            combined_results.sort(key=lambda x: x["combined_score"], reverse=True)
            final_results = combined_results[:top_k]

            processing_time = (time.time() - start_time) * 1000

            self.logger.info(
                "Hybrid search completed",
                query=query[:50],
                vector_results=len(vector_results),
                graph_results=len(graph_results),
                combined_results=len(final_results),
                processing_time_ms=processing_time,
            )

            return final_results

        except Exception as e:
            self.logger.error(f"Hybrid search failed: {e}")
            return []

    async def _search_knowledge_graph(self, query: str) -> List[Dict[str, Any]]:
        """Search knowledge graph for relevant entities and relationships."""
        try:
            # Simple AQL query to find relevant entities
            aql_query = """
            FOR doc IN entities
            FILTER CONTAINS(LOWER(doc.name), LOWER(@query)) 
               OR CONTAINS(LOWER(doc.description), LOWER(@query))
            RETURN {
                id: doc._key,
                name: doc.name,
                type: doc.type,
                description: doc.description,
                score: 0.8,
                source: 'knowledge_graph'
            }
            LIMIT 20
            """

            result = await self.knowledge_graph.query_knowledge_graph(
                query=aql_query, parameters={"query": query}
            )

            return result.entities

        except Exception as e:
            self.logger.error(f"Knowledge graph search failed: {e}")
            return []

    async def _combine_results(
        self,
        vector_results: List[VectorSearchResult],
        graph_results: List[Dict[str, Any]],
        vector_weight: float,
        graph_weight: float,
    ) -> List[Dict[str, Any]]:
        """Combine vector and knowledge graph results with scoring."""
        combined_results = []

        # Process vector results
        for result in vector_results:
            combined_results.append(
                {
                    "id": result.id,
                    "content": result.content,
                    "metadata": result.metadata,
                    "vector_score": result.score,
                    "graph_score": 0.0,
                    "combined_score": result.score * vector_weight,
                    "source": "vector_search",
                }
            )

        # Process graph results
        for result in graph_results:
            # Check if this entity already exists in vector results
            existing_result = next(
                (r for r in combined_results if r["id"] == result.get("id")), None
            )

            if existing_result:
                # Update existing result with graph score
                existing_result["graph_score"] = result.get("score", 0.0)
                existing_result["combined_score"] += (
                    result.get("score", 0.0) * graph_weight
                )
                existing_result["source"] = "hybrid"
            else:
                # Add new result from knowledge graph
                combined_results.append(
                    {
                        "id": result.get("id", ""),
                        "content": result.get("description", ""),
                        "metadata": result,
                        "vector_score": 0.0,
                        "graph_score": result.get("score", 0.0),
                        "combined_score": result.get("score", 0.0) * graph_weight,
                        "source": "knowledge_graph",
                    }
                )

        return combined_results

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of hybrid search engine."""
        return {
            "status": (
                "healthy"
                if self.vector_db.connected and self.knowledge_graph.connected
                else "disconnected"
            ),
            "engine_type": "hybrid_search",
            "vector_db_status": self.vector_db.get_health_status(),
            "knowledge_graph_status": self.knowledge_graph.get_health_status(),
            "last_updated": datetime.now().isoformat(),
        }


# Export main classes
__all__ = [
    "PineconeVectorDB",
    "ArangoDBKnowledgeGraph",
    "HybridSearchEngine",
    "VectorSearchResult",
    "KnowledgeGraphResult",
]
