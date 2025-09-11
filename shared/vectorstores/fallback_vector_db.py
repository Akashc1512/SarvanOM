"""
Fallback Vector Database Implementation

Provides a simple in-memory vector database when Qdrant/ChromaDB
are not available, ensuring the system remains functional.
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
import time
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class VectorDocument:
    """Vector document with metadata."""
    id: str
    vector: List[float]
    text: str
    metadata: Dict[str, Any]
    created_at: float


class FallbackVectorDB:
    """
    Simple in-memory vector database for fallback scenarios.
    
    Provides basic vector similarity search when external
    vector databases are not available.
    """
    
    def __init__(self, collection_name: str = "sarvanom_embeddings"):
        self.collection_name = collection_name
        self.documents: Dict[str, VectorDocument] = {}
        self.vectors: List[List[float]] = []
        self.doc_ids: List[str] = []
        
        logger.info(f"Fallback vector DB initialized: {collection_name}")
    
    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        vectors: List[List[float]],
        ids: Optional[List[str]] = None
    ) -> bool:
        """
        Add documents to the vector database.
        
        Args:
            documents: List of documents with text and metadata
            vectors: List of corresponding vectors
            ids: Optional list of document IDs
            
        Returns:
            True if successful
        """
        try:
            if ids is None:
                ids = [f"doc_{len(self.documents) + i}" for i in range(len(documents))]
            
            for i, (doc, vector, doc_id) in enumerate(zip(documents, vectors, ids)):
                if doc_id in self.documents:
                    logger.warning(f"Document {doc_id} already exists, updating")
                
                vector_doc = VectorDocument(
                    id=doc_id,
                    vector=vector,
                    text=doc.get("text", ""),
                    metadata=doc.get("metadata", {}),
                    created_at=time.time()
                )
                
                self.documents[doc_id] = vector_doc
                self.vectors.append(vector)
                self.doc_ids.append(doc_id)
            
            logger.info(f"Added {len(documents)} documents to fallback vector DB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to fallback vector DB: {e}")
            return False
    
    def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        score_threshold: float = 0.7,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query vector
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            filter_conditions: Optional filter conditions
            
        Returns:
            List of search results
        """
        try:
            if not self.vectors:
                logger.warning("No vectors in fallback vector DB")
                return []
            
            # Convert to numpy arrays for efficient computation
            query_array = np.array(query_vector)
            vectors_array = np.array(self.vectors)
            
            # Calculate cosine similarity
            similarities = self._cosine_similarity(query_array, vectors_array)
            
            # Get top-k results
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                similarity = similarities[idx]
                if similarity < score_threshold:
                    continue
                
                doc_id = self.doc_ids[idx]
                doc = self.documents[doc_id]
                
                # Apply filters if provided
                if filter_conditions and not self._matches_filters(doc.metadata, filter_conditions):
                    continue
                
                results.append({
                    "id": doc_id,
                    "score": float(similarity),
                    "text": doc.text,
                    "metadata": doc.metadata
                })
            
            logger.info(f"Fallback vector search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Fallback vector search failed: {e}")
            return []
    
    def _cosine_similarity(self, query: np.ndarray, vectors: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity between query and vectors."""
        # Normalize vectors
        query_norm = query / np.linalg.norm(query)
        vectors_norm = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
        
        # Calculate cosine similarity
        similarities = np.dot(vectors_norm, query_norm)
        return similarities
    
    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if document metadata matches filter conditions."""
        for key, value in filters.items():
            if key not in metadata:
                return False
            if metadata[key] != value:
                return False
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        return {
            "collection_name": self.collection_name,
            "total_documents": len(self.documents),
            "total_vectors": len(self.vectors),
            "vector_dimension": len(self.vectors[0]) if self.vectors else 0,
            "memory_usage_mb": self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB."""
        try:
            # Rough estimate: 4 bytes per float + metadata overhead
            vector_memory = len(self.vectors) * len(self.vectors[0]) * 4 if self.vectors else 0
            metadata_memory = len(self.documents) * 1000  # Rough estimate for metadata
            total_bytes = vector_memory + metadata_memory
            return total_bytes / (1024 * 1024)
        except Exception:
            return 0.0
    
    def clear(self):
        """Clear all documents from the database."""
        self.documents.clear()
        self.vectors.clear()
        self.doc_ids.clear()
        logger.info("Fallback vector DB cleared")
    
    def save_to_disk(self, file_path: str):
        """Save database to disk for persistence."""
        try:
            data = {
                "collection_name": self.collection_name,
                "documents": {
                    doc_id: {
                        "id": doc.id,
                        "vector": doc.vector,
                        "text": doc.text,
                        "metadata": doc.metadata,
                        "created_at": doc.created_at
                    }
                    for doc_id, doc in self.documents.items()
                }
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Fallback vector DB saved to: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save fallback vector DB: {e}")
    
    def load_from_disk(self, file_path: str):
        """Load database from disk."""
        try:
            if not Path(file_path).exists():
                logger.warning(f"Fallback vector DB file not found: {file_path}")
                return
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self.collection_name = data.get("collection_name", "sarvanom_embeddings")
            self.documents.clear()
            self.vectors.clear()
            self.doc_ids.clear()
            
            for doc_id, doc_data in data.get("documents", {}).items():
                vector_doc = VectorDocument(
                    id=doc_data["id"],
                    vector=doc_data["vector"],
                    text=doc_data["text"],
                    metadata=doc_data["metadata"],
                    created_at=doc_data["created_at"]
                )
                
                self.documents[doc_id] = vector_doc
                self.vectors.append(doc_data["vector"])
                self.doc_ids.append(doc_id)
            
            logger.info(f"Fallback vector DB loaded from: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load fallback vector DB: {e}")


# Global fallback vector DB instance
_fallback_vector_db: Optional[FallbackVectorDB] = None


def get_fallback_vector_db() -> FallbackVectorDB:
    """Get global fallback vector DB instance."""
    global _fallback_vector_db
    
    if _fallback_vector_db is None:
        _fallback_vector_db = FallbackVectorDB()
    
    return _fallback_vector_db
