"""
Vector Store Service Abstraction

Provides an interface and simple in-memory implementation for vector search
to support retrieval components. Can be swapped for real backends like
Qdrant, FAISS, or Pinecone.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import math

logger = logging.getLogger(__name__)


@dataclass
class VectorDocument:
    """Represents a document stored in the vector index."""
    id: str
    text: str
    embedding: List[float]
    metadata: Dict[str, Any]


class VectorStoreService:
    """Abstract vector store interface."""

    async def upsert(self, docs: List[VectorDocument]) -> int:
        raise NotImplementedError

    async def delete(self, doc_ids: List[str]) -> int:
        raise NotImplementedError

    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[VectorDocument, float]]:
        raise NotImplementedError

    async def count(self) -> int:
        raise NotImplementedError


class InMemoryVectorStore(VectorStoreService):
    """Simple in-memory vector store for development and testing."""

    def __init__(self) -> None:
        self._docs: Dict[str, VectorDocument] = {}

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

    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[VectorDocument, float]]:
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


try:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance, VectorParams, PointStruct
except Exception:  # pragma: no cover
    QdrantClient = None  # type: ignore


class QdrantVectorStore(VectorStoreService):
    """Qdrant-backed vector store adapter."""

    def __init__(self, url: str, api_key: Optional[str], collection: str, vector_size: int = 1536):
        if QdrantClient is None:
            raise RuntimeError("qdrant-client not available")
        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection = collection
        self.vector_size = vector_size
        # Ensure collection exists
        try:
            self.client.get_collection(collection_name=self.collection)
        except Exception:
            self.client.recreate_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )

    async def upsert(self, docs: List[VectorDocument]) -> int:
        points = [
            PointStruct(id=d.id, vector=d.embedding, payload={"text": d.text, **d.metadata})
            for d in docs
        ]
        # qdrant client is sync; run in threadpool
        import anyio

        def _upsert():
            self.client.upsert(collection_name=self.collection, points=points)

        await anyio.to_thread.run_sync(_upsert)
        return len(points)

    async def delete(self, doc_ids: List[str]) -> int:
        import anyio
        from qdrant_client.http import models as qm

        def _delete():
            self.client.delete(
                collection_name=self.collection,
                points_selector=qm.PointIdsList(points=doc_ids),
            )

        await anyio.to_thread.run_sync(_delete)
        return len(doc_ids)

    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[VectorDocument, float]]:
        import anyio

        def _search():
            return self.client.search(
                collection_name=self.collection,
                query_vector=query_embedding,
                limit=top_k,
                with_payload=True,
            )

        res = await anyio.to_thread.run_sync(_search)
        out: List[Tuple[VectorDocument, float]] = []
        for r in res:
            payload = r.payload or {}
            out.append(
                (
                    VectorDocument(
                        id=str(r.id),
                        text=str(payload.get("text", "")),
                        embedding=[],
                        metadata=payload,
                    ),
                    float(r.score),
                )
            )
        return out

    async def count(self) -> int:
        import anyio

        def _count():
            info = self.client.get_collection(self.collection)
            return info.vectors_count

        return await anyio.to_thread.run_sync(_count)


