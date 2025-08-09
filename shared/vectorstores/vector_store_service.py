"""
Shared Vector Store Service Abstraction

Provides an interface and simple implementations for vector search to support
retrieval components. Includes in-memory, ChromaDB (local), and Qdrant adapters.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import math
from abc import ABC, abstractmethod
import time

from shared.core.logging import get_logger, log_execution_time_decorator
from shared.core.metrics import get_metrics_service

logger = get_logger(__name__)
metrics_service = get_metrics_service()


@dataclass
class VectorDocument:
    """Represents a document stored in the vector index."""

    id: str
    text: str
    embedding: List[float]
    metadata: Dict[str, Any]


class VectorStoreService(ABC):
    """Abstract base class for vector store operations with logging."""

    def __init__(self, store_type: str):
        self.store_type = store_type
        logger.info("Vector store service initialized", store_type=store_type)

    @abstractmethod
    async def add_documents(
        self, documents: List[Dict[str, Any]], embeddings: List[List[float]]
    ) -> bool:
        """Add documents to vector store with logging."""
        pass

    @abstractmethod
    async def search(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search vector store with logging."""
        pass

    def _log_operation(self, operation: str, **kwargs):
        """Log vector store operation."""
        logger.info(f"Vector store {operation}", store_type=self.store_type, **kwargs)


class InMemoryVectorStore(VectorStoreService):
    """Simple in-memory vector store for development and testing."""

    def __init__(self) -> None:
        self._docs: Dict[str, VectorDocument] = {}
        super().__init__("in_memory")

    async def upsert(self, docs: List[VectorDocument]) -> int:
        for d in docs:
            self._docs[d.id] = d
        logger.info(f"Upserted {len(docs)} documents into vector store")
        return len(docs)

    async def delete(self, doc_ids: List[str]) -> int:
        deleted = 0
        for doc_id in doc_ids:
            if doc_id in self._docs:
                del self._docs[doc_id]
                deleted += 1
        logger.info(f"Deleted {deleted} documents from vector store")
        return deleted

    async def search(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[Tuple[VectorDocument, float]]:
        # Cosine similarity search
        def cosine(a: List[float], b: List[float]) -> float:
            if not a or not b or len(a) != len(b):
                return 0.0
            dot = sum(x * y for x, y in zip(a, b))
            na = math.sqrt(sum(x * x for x in a))
            nb = math.sqrt(sum(y * y for y in b))
            if na == 0 or nb == 0:
                return 0.0
            return dot / (na * nb)

        scores: List[Tuple[VectorDocument, float]] = []
        for doc in self._docs.values():
            scores.append((doc, cosine(query_embedding, doc.embedding)))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    async def count(self) -> int:
        return len(self._docs)

    @log_execution_time_decorator("in_memory_upsert")
    async def add_documents(
        self, documents: List[Dict[str, Any]], embeddings: List[List[float]]
    ) -> bool:
        start_time = time.time()
        logger.info(
            "Adding documents to InMemoryVectorStore", document_count=len(documents)
        )
        try:
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                self._docs[doc.get("id", str(i))] = VectorDocument(
                    id=doc.get("id", str(i)),
                    text=doc.get("content", ""),
                    embedding=embedding,
                    metadata=doc.get("metadata", {}),
                )
            duration = time.time() - start_time
            metrics_service.record_vector_store_query(
                store_type="in_memory",
                operation="add_documents",
                duration=duration,
                status="success",
            )
            logger.info(
                "Documents added to InMemoryVectorStore successfully",
                document_count=len(documents),
                duration_ms=int(duration * 1000),
            )
            return True
        except Exception as e:
            duration = time.time() - start_time
            metrics_service.record_vector_store_query(
                store_type="in_memory",
                operation="add_documents",
                duration=duration,
                status="error",
            )
            logger.error(
                "Failed to add documents to InMemoryVectorStore",
                error=str(e),
                error_type=type(e).__name__,
                document_count=len(documents),
                duration_ms=int(duration * 1000),
            )
            raise

    @log_execution_time_decorator("in_memory_search")
    async def search(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        start_time = time.time()
        logger.info("Searching InMemoryVectorStore", top_k=top_k)
        try:
            scores: List[Tuple[VectorDocument, float]] = []
            for doc in self._docs.values():
                scores.append((doc, cosine(query_embedding, doc.embedding)))

            scores.sort(key=lambda x: x[1], reverse=True)
            documents = [
                {
                    "id": doc.id,
                    "text": doc.text,
                    "embedding": doc.embedding,
                    "metadata": doc.metadata,
                }
                for doc, _ in scores[:top_k]
            ]
            duration = time.time() - start_time
            metrics_service.record_vector_store_query(
                store_type="in_memory",
                operation="search",
                duration=duration,
                status="success",
            )
            logger.info(
                "InMemoryVectorStore search completed",
                results_found=len(documents),
                top_k=top_k,
                duration_ms=int(duration * 1000),
            )
            return documents
        except Exception as e:
            duration = time.time() - start_time
            metrics_service.record_vector_store_query(
                store_type="in_memory",
                operation="search",
                duration=duration,
                status="error",
            )
            logger.error(
                "InMemoryVectorStore search failed",
                error=str(e),
                error_type=type(e).__name__,
                top_k=top_k,
                duration_ms=int(duration * 1000),
            )
            raise


class ChromaVectorStore(VectorStoreService):
    """ChromaDB vector store implementation with comprehensive logging."""

    def __init__(self, collection_name: str = "documents"):
        super().__init__("chromadb")
        self.collection_name = collection_name

        try:
            import chromadb

            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection(collection_name)
            logger.info(
                "ChromaDB initialized successfully", collection_name=collection_name
            )
        except Exception as e:
            logger.error("Failed to initialize ChromaDB", error=str(e))
            raise

    @log_execution_time_decorator("chroma_add_documents")
    async def add_documents(
        self, documents: List[Dict[str, Any]], embeddings: List[List[float]]
    ) -> bool:
        """Add documents to ChromaDB with logging and metrics."""
        start_time = time.time()

        logger.info(
            "Adding documents to ChromaDB",
            document_count=len(documents),
            collection_name=self.collection_name,
        )

        try:
            # Prepare data for ChromaDB
            ids = [doc.get("id", str(i)) for i, doc in enumerate(documents)]
            texts = [doc.get("content", "") for doc in documents]
            metadatas = [doc.get("metadata", {}) for doc in documents]

            # Add to collection
            self.collection.add(
                ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas
            )

            duration = time.time() - start_time
            metrics_service.record_vector_store_query(
                store_type="chromadb",
                operation="add_documents",
                duration=duration,
                status="success",
            )

            logger.info(
                "Documents added to ChromaDB successfully",
                document_count=len(documents),
                duration_ms=int(duration * 1000),
            )

            return True

        except Exception as e:
            duration = time.time() - start_time
            metrics_service.record_vector_store_query(
                store_type="chromadb",
                operation="add_documents",
                duration=duration,
                status="error",
            )

            logger.error(
                "Failed to add documents to ChromaDB",
                error=str(e),
                error_type=type(e).__name__,
                document_count=len(documents),
                duration_ms=int(duration * 1000),
            )
            raise

    @log_execution_time_decorator("chroma_search")
    async def search(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search ChromaDB with logging and metrics."""
        start_time = time.time()

        logger.info(
            "Searching ChromaDB", top_k=top_k, collection_name=self.collection_name
        )

        try:
            # Perform search
            results = self.collection.query(
                query_embeddings=[query_embedding], n_results=top_k
            )

            # Format results
            documents = []
            if results["documents"]:
                for i in range(len(results["documents"][0])):
                    doc = {
                        "content": results["documents"][0][i],
                        "metadata": (
                            results["metadatas"][0][i] if results["metadatas"] else {}
                        ),
                        "id": results["ids"][0][i],
                        "distance": (
                            results["distances"][0][i] if results["distances"] else 0.0
                        ),
                    }
                    documents.append(doc)

            duration = time.time() - start_time
            metrics_service.record_vector_store_query(
                store_type="chromadb",
                operation="search",
                duration=duration,
                status="success",
            )

            logger.info(
                "ChromaDB search completed",
                results_found=len(documents),
                top_k=top_k,
                duration_ms=int(duration * 1000),
            )

            return documents

        except Exception as e:
            duration = time.time() - start_time
            metrics_service.record_vector_store_query(
                store_type="chromadb",
                operation="search",
                duration=duration,
                status="error",
            )

            logger.error(
                "ChromaDB search failed",
                error=str(e),
                error_type=type(e).__name__,
                top_k=top_k,
                duration_ms=int(duration * 1000),
            )
            raise


try:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance, VectorParams, PointStruct
except Exception:  # pragma: no cover
    QdrantClient = None  # type: ignore


class QdrantVectorStore(VectorStoreService):
    """Qdrant vector store implementation with comprehensive logging."""

    def __init__(
        self,
        url: str,
        api_key: str = None,
        collection: str = "documents",
        vector_size: int = 384,
    ):
        super().__init__("qdrant")
        self.url = url
        self.collection = collection
        self.vector_size = vector_size

        try:
            from qdrant_client import QdrantClient

            self.client = QdrantClient(url=url, api_key=api_key)

            # Ensure collection exists
            self.client.get_collection(collection)
            logger.info(
                "Qdrant initialized successfully",
                url=url,
                collection=collection,
                vector_size=vector_size,
            )
        except Exception as e:
            logger.error("Failed to initialize Qdrant", error=str(e))
            raise

    @log_execution_time_decorator("qdrant_add_documents")
    async def add_documents(
        self, documents: List[Dict[str, Any]], embeddings: List[List[float]]
    ) -> bool:
        """Add documents to Qdrant with logging and metrics."""
        start_time = time.time()

        logger.info(
            "Adding documents to Qdrant",
            document_count=len(documents),
            collection=self.collection,
        )

        try:
            # Prepare points for Qdrant
            points = []
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                point = {
                    "id": doc.get("id", str(i)),
                    "vector": embedding,
                    "payload": {
                        "content": doc.get("content", ""),
                        "metadata": doc.get("metadata", {}),
                    },
                }
                points.append(point)

            # Add points to collection
            self.client.upsert(collection_name=self.collection, points=points)

            duration = time.time() - start_time
            metrics_service.record_vector_store_query(
                store_type="qdrant",
                operation="add_documents",
                duration=duration,
                status="success",
            )

            logger.info(
                "Documents added to Qdrant successfully",
                document_count=len(documents),
                duration_ms=int(duration * 1000),
            )

            return True

        except Exception as e:
            duration = time.time() - start_time
            metrics_service.record_vector_store_query(
                store_type="qdrant",
                operation="add_documents",
                duration=duration,
                status="error",
            )

            logger.error(
                "Failed to add documents to Qdrant",
                error=str(e),
                error_type=type(e).__name__,
                document_count=len(documents),
                duration_ms=int(duration * 1000),
            )
            raise

    @log_execution_time_decorator("qdrant_search")
    async def search(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search Qdrant with logging and metrics."""
        start_time = time.time()

        logger.info("Searching Qdrant", top_k=top_k, collection=self.collection)

        try:
            # Perform search
            results = self.client.search(
                collection_name=self.collection,
                query_vector=query_embedding,
                limit=top_k,
            )

            # Format results
            documents = []
            for result in results:
                doc = {
                    "content": result.payload.get("content", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "id": result.id,
                    "distance": result.score,
                }
                documents.append(doc)

            duration = time.time() - start_time
            metrics_service.record_vector_store_query(
                store_type="qdrant",
                operation="search",
                duration=duration,
                status="success",
            )

            logger.info(
                "Qdrant search completed",
                results_found=len(documents),
                top_k=top_k,
                duration_ms=int(duration * 1000),
            )

            return documents

        except Exception as e:
            duration = time.time() - start_time
            metrics_service.record_vector_store_query(
                store_type="qdrant",
                operation="search",
                duration=duration,
                status="error",
            )

            logger.error(
                "Qdrant search failed",
                error=str(e),
                error_type=type(e).__name__,
                top_k=top_k,
                duration_ms=int(duration * 1000),
            )
            raise
