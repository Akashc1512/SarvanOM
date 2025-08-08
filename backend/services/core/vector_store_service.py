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


