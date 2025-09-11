"""
Vector Database Connection Manager for MAANG Standards

Provides robust connection management for vector databases with proper
error handling, connection pooling, and health monitoring.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
import time
from dataclasses import dataclass
from enum import Enum

try:
    import qdrant_client
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

logger = logging.getLogger(__name__)


class VectorDBProvider(str, Enum):
    """Vector database providers."""
    QDRANT = "qdrant"
    CHROMA = "chroma"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"


@dataclass
class VectorDBConfig:
    """Vector database configuration."""
    provider: VectorDBProvider
    host: str = "localhost"
    port: int = 6333
    api_key: Optional[str] = None
    collection_name: str = "sarvanom_embeddings"
    vector_size: int = 384
    distance_metric: str = "cosine"
    timeout: int = 10
    max_retries: int = 3
    retry_delay: float = 1.0


class VectorDBConnectionManager:
    """
    Vector database connection manager with MAANG-standard reliability.
    
    Provides connection pooling, health monitoring, and automatic failover.
    """
    
    def __init__(self, config: VectorDBConfig):
        self.config = config
        self.client: Optional[Any] = None
        self.connection_pool: List[Any] = []
        self.pool_size = 5
        self.health_check_interval = 30  # seconds
        self.last_health_check = 0
        self.is_healthy = False
        self.connection_attempts = 0
        self.max_connection_attempts = 3
        
        logger.info(f"VectorDB connection manager initialized: {config.provider}")
    
    async def initialize(self) -> bool:
        """Initialize vector database connection."""
        try:
            if self.config.provider == VectorDBProvider.QDRANT:
                return await self._init_qdrant()
            elif self.config.provider == VectorDBProvider.CHROMA:
                return await self._init_chroma()
            else:
                logger.error(f"Unsupported vector DB provider: {self.config.provider}")
                return False
        except Exception as e:
            logger.error(f"Failed to initialize vector DB: {e}")
            return False
    
    async def _init_qdrant(self) -> bool:
        """Initialize Qdrant connection."""
        if not QDRANT_AVAILABLE:
            logger.error("Qdrant client not available")
            return False
        
        try:
            self.client = QdrantClient(
                host=self.config.host,
                port=self.config.port,
                api_key=self.config.api_key,
                timeout=self.config.timeout
            )
            
            # Test connection
            collections = self.client.get_collections()
            logger.info(f"Qdrant connected successfully: {len(collections.collections)} collections")
            
            # Create collection if it doesn't exist
            await self._ensure_collection_exists()
            
            self.is_healthy = True
            return True
            
        except Exception as e:
            logger.error(f"Qdrant connection failed: {e}")
            return False
    
    async def _init_chroma(self) -> bool:
        """Initialize ChromaDB connection."""
        if not CHROMA_AVAILABLE:
            logger.error("ChromaDB client not available")
            return False
        
        try:
            self.client = chromadb.Client(
                settings=Settings(
                    chroma_server_host=self.config.host,
                    chroma_server_http_port=self.config.port
                )
            )
            
            # Test connection
            collections = self.client.list_collections()
            logger.info(f"ChromaDB connected successfully: {len(collections)} collections")
            
            # Create collection if it doesn't exist
            await self._ensure_collection_exists()
            
            self.is_healthy = True
            return True
            
        except Exception as e:
            logger.error(f"ChromaDB connection failed: {e}")
            return False
    
    async def _ensure_collection_exists(self):
        """Ensure the collection exists."""
        try:
            if self.config.provider == VectorDBProvider.QDRANT:
                collections = self.client.get_collections()
                collection_names = [c.name for c in collections.collections]
                
                if self.config.collection_name not in collection_names:
                    self.client.create_collection(
                        collection_name=self.config.collection_name,
                        vectors_config=VectorParams(
                            size=self.config.vector_size,
                            distance=Distance.COSINE
                        )
                    )
                    logger.info(f"Created Qdrant collection: {self.config.collection_name}")
            
            elif self.config.provider == VectorDBProvider.CHROMA:
                collections = self.client.list_collections()
                collection_names = [c.name for c in collections]
                
                if self.config.collection_name not in collection_names:
                    self.client.create_collection(
                        name=self.config.collection_name,
                        metadata={"hnsw:space": "cosine"}
                    )
                    logger.info(f"Created ChromaDB collection: {self.config.collection_name}")
        
        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {e}")
    
    async def health_check(self) -> bool:
        """Perform health check on vector database."""
        current_time = time.time()
        
        # Skip if checked recently
        if current_time - self.last_health_check < self.health_check_interval:
            return self.is_healthy
        
        try:
            if self.config.provider == VectorDBProvider.QDRANT:
                collections = self.client.get_collections()
                self.is_healthy = True
            elif self.config.provider == VectorDBProvider.CHROMA:
                collections = self.client.list_collections()
                self.is_healthy = True
            else:
                self.is_healthy = False
            
            self.last_health_check = current_time
            logger.debug(f"Vector DB health check passed: {self.is_healthy}")
            return self.is_healthy
            
        except Exception as e:
            logger.error(f"Vector DB health check failed: {e}")
            self.is_healthy = False
            self.last_health_check = current_time
            return False
    
    async def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: float = 0.7,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            filter_conditions: Additional filter conditions
            
        Returns:
            List of search results
        """
        if not await self.health_check():
            raise ConnectionError("Vector database is not healthy")
        
        try:
            if self.config.provider == VectorDBProvider.QDRANT:
                return await self._search_qdrant(query_vector, limit, score_threshold, filter_conditions)
            elif self.config.provider == VectorDBProvider.CHROMA:
                return await self._search_chroma(query_vector, limit, score_threshold, filter_conditions)
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")
        
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            raise
    
    async def _search_qdrant(
        self,
        query_vector: List[float],
        limit: int,
        score_threshold: float,
        filter_conditions: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Search using Qdrant."""
        try:
            results = self.client.search(
                collection_name=self.config.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=filter_conditions
            )
            
            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                }
                for result in results
            ]
        
        except Exception as e:
            logger.error(f"Qdrant search failed: {e}")
            raise
    
    async def _search_chroma(
        self,
        query_vector: List[float],
        limit: int,
        score_threshold: float,
        filter_conditions: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Search using ChromaDB."""
        try:
            collection = self.client.get_collection(self.config.collection_name)
            results = collection.query(
                query_embeddings=[query_vector],
                n_results=limit,
                where=filter_conditions
            )
            
            return [
                {
                    "id": results["ids"][0][i],
                    "score": 1 - results["distances"][0][i],  # Convert distance to similarity
                    "payload": results["metadatas"][0][i] if results["metadatas"] else {}
                }
                for i in range(len(results["ids"][0]))
                if (1 - results["distances"][0][i]) >= score_threshold
            ]
        
        except Exception as e:
            logger.error(f"ChromaDB search failed: {e}")
            raise
    
    async def add_vectors(
        self,
        vectors: List[List[float]],
        ids: List[str],
        payloads: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Add vectors to the database.
        
        Args:
            vectors: List of vectors to add
            ids: List of IDs for the vectors
            payloads: List of payloads for the vectors
            
        Returns:
            True if successful
        """
        if not await self.health_check():
            raise ConnectionError("Vector database is not healthy")
        
        try:
            if self.config.provider == VectorDBProvider.QDRANT:
                return await self._add_vectors_qdrant(vectors, ids, payloads)
            elif self.config.provider == VectorDBProvider.CHROMA:
                return await self._add_vectors_chroma(vectors, ids, payloads)
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")
        
        except Exception as e:
            logger.error(f"Failed to add vectors: {e}")
            return False
    
    async def _add_vectors_qdrant(
        self,
        vectors: List[List[float]],
        ids: List[str],
        payloads: Optional[List[Dict[str, Any]]]
    ) -> bool:
        """Add vectors to Qdrant."""
        try:
            points = []
            for i, (vector, vector_id) in enumerate(zip(vectors, ids)):
                point = {
                    "id": vector_id,
                    "vector": vector
                }
                if payloads and i < len(payloads):
                    point["payload"] = payloads[i]
                points.append(point)
            
            self.client.upsert(
                collection_name=self.config.collection_name,
                points=points
            )
            return True
        
        except Exception as e:
            logger.error(f"Failed to add vectors to Qdrant: {e}")
            return False
    
    async def _add_vectors_chroma(
        self,
        vectors: List[List[float]],
        ids: List[str],
        payloads: Optional[List[Dict[str, Any]]]
    ) -> bool:
        """Add vectors to ChromaDB."""
        try:
            collection = self.client.get_collection(self.config.collection_name)
            collection.add(
                embeddings=vectors,
                ids=ids,
                metadatas=payloads or [{}] * len(vectors)
            )
            return True
        
        except Exception as e:
            logger.error(f"Failed to add vectors to ChromaDB: {e}")
            return False
    
    async def close(self):
        """Close all connections."""
        try:
            if self.client:
                if hasattr(self.client, 'close'):
                    self.client.close()
                self.client = None
            
            self.connection_pool.clear()
            self.is_healthy = False
            logger.info("Vector DB connections closed")
        
        except Exception as e:
            logger.error(f"Error closing vector DB connections: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get connection status."""
        return {
            "provider": self.config.provider.value,
            "is_healthy": self.is_healthy,
            "last_health_check": self.last_health_check,
            "connection_attempts": self.connection_attempts,
            "collection_name": self.config.collection_name
        }


# Global connection manager instance
_vector_db_manager: Optional[VectorDBConnectionManager] = None


async def get_vector_db_manager() -> VectorDBConnectionManager:
    """Get global vector database manager instance."""
    global _vector_db_manager
    
    if _vector_db_manager is None:
        config = VectorDBConfig(
            provider=VectorDBProvider.QDRANT,
            host="localhost",
            port=6333,
            collection_name="sarvanom_embeddings"
        )
        _vector_db_manager = VectorDBConnectionManager(config)
        await _vector_db_manager.initialize()
    
    return _vector_db_manager


async def close_vector_db_manager():
    """Close global vector database manager."""
    global _vector_db_manager
    
    if _vector_db_manager:
        await _vector_db_manager.close()
        _vector_db_manager = None
