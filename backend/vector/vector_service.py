"""
Vector Service

This service handles vector database operations including:
- Vector embeddings generation
- Vector database operations (Pinecone, Qdrant)
- Similarity search and matching
- Embedding model management
- Vector indexing and storage
"""

import asyncio
import logging
import os
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logging.warning("python-dotenv not available")

# Vector database imports
try:
    import pinecone
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    pinecone = None

try:
    import qdrant_client
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantClient = None

# OpenAI for embeddings
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

logger = logging.getLogger(__name__)


@dataclass
class VectorSearchResult:
    """Result from vector search operation."""
    id: str
    score: float
    metadata: Dict[str, Any]
    content: str


class VectorService:
    """
    Vector Service for handling vector database operations.
    Supports Pinecone and Qdrant with OpenAI embeddings.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.embedding_model = config.get("embedding_model", "text-embedding-ada-002")
        
        # Pinecone configuration
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_env = os.getenv("PINECONE_ENVIRONMENT")
        self.pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")
        
        # Qdrant configuration
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_collection = config.get("collection_name", "knowledge_base")
        
        # OpenAI configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize vector database
        self.pinecone_index = None
        self.qdrant_client = None
        self._initialize_vector_db()
    
    def _initialize_vector_db(self):
        """Initialize vector database connection."""
        # Try Pinecone first
        if PINECONE_AVAILABLE and self.pinecone_api_key:
            try:
                pc = Pinecone(api_key=self.pinecone_api_key)
                self.pinecone_index = pc.Index(self.pinecone_index_name)
                logger.info("✅ Pinecone v3 initialized successfully")
                return
            except Exception as e:
                logger.warning(f"⚠️ Pinecone v3 initialization failed: {e}")
        
        # Try Qdrant as fallback
        if QDRANT_AVAILABLE and self.qdrant_url:
            try:
                self.qdrant_client = QdrantClient(url=self.qdrant_url)
                # Create collection if it doesn't exist
                try:
                    self.qdrant_client.get_collection(self.qdrant_collection)
                except:
                    self.qdrant_client.create_collection(
                        collection_name=self.qdrant_collection,
                        vectors_config=VectorParams(
                            size=1536, distance=Distance.COSINE
                        ),
                    )
                logger.info("✅ Qdrant initialized successfully")
                return
            except Exception as e:
                logger.warning(f"⚠️ Qdrant initialization failed: {e}")
        
        logger.info("⚠️ No vector database available, using fallback storage")
    
    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI."""
        if not OPENAI_AVAILABLE or not self.openai_api_key:
            logger.warning("OpenAI not available for embeddings")
            return []
        
        try:
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []
    
    async def search_similar(self, query: str, top_k: int = 10) -> List[VectorSearchResult]:
        """Search for similar vectors using the query embedding."""
        embedding = await self.get_embedding(query)
        if not embedding:
            return []
        
        results = []
        
        # Try Pinecone search
        if self.pinecone_index:
            try:
                search_response = self.pinecone_index.query(
                    vector=embedding,
                    top_k=top_k,
                    include_metadata=True
                )
                
                for match in search_response.matches:
                    results.append(VectorSearchResult(
                        id=match.id,
                        score=match.score,
                        metadata=match.metadata or {},
                        content=match.metadata.get("content", "") if match.metadata else ""
                    ))
                
                return results
            except Exception as e:
                logger.error(f"Pinecone search failed: {e}")
        
        # Try Qdrant search
        if self.qdrant_client:
            try:
                search_response = self.qdrant_client.search(
                    collection_name=self.qdrant_collection,
                    query_vector=embedding,
                    limit=top_k,
                    with_payload=True
                )
                
                for result in search_response:
                    results.append(VectorSearchResult(
                        id=result.id,
                        score=result.score,
                        metadata=result.payload or {},
                        content=result.payload.get("content", "") if result.payload else ""
                    ))
                
                return results
            except Exception as e:
                logger.error(f"Qdrant search failed: {e}")
        
        return results
    
    async def upsert_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Upsert documents to vector database."""
        if not documents:
            return False
        
        # Generate embeddings for all documents
        embeddings = []
        for doc in documents:
            embedding = await self.get_embedding(doc.get("content", ""))
            embeddings.append(embedding)
        
        # Remove documents without embeddings
        valid_docs = []
        valid_embeddings = []
        for doc, embedding in zip(documents, embeddings):
            if embedding:
                valid_docs.append(doc)
                valid_embeddings.append(embedding)
        
        if not valid_docs:
            logger.warning("No valid embeddings generated")
            return False
        
        # Try Pinecone upsert
        if self.pinecone_index:
            try:
                vectors = []
                for i, (doc, embedding) in enumerate(zip(valid_docs, valid_embeddings)):
                    vectors.append({
                        "id": doc.get("id", f"doc_{i}"),
                        "values": embedding,
                        "metadata": {
                            "content": doc["content"],
                            "source": doc.get("source", "unknown"),
                            "timestamp": doc.get("timestamp", ""),
                            **doc.get("metadata", {})
                        }
                    })
                
                self.pinecone_index.upsert(vectors=vectors)
                logger.info(f"Upserted {len(valid_docs)} documents to Pinecone")
                return True
            except Exception as e:
                logger.error(f"Pinecone upsert failed: {e}")
        
        # Try Qdrant upsert
        if self.qdrant_client:
            try:
                points = []
                for i, (doc, embedding) in enumerate(zip(valid_docs, valid_embeddings)):
                    points.append(
                        PointStruct(
                            id=doc.get("id", f"doc_{i}"),
                            vector=embedding,
                            payload={
                                "content": doc["content"],
                                "source": doc.get("source", "unknown"),
                                "timestamp": doc.get("timestamp", ""),
                                **doc.get("metadata", {})
                            }
                        )
                    )
                
                self.qdrant_client.upsert(
                    collection_name=self.qdrant_collection,
                    points=points
                )
                logger.info(f"Upserted {len(valid_docs)} documents to Qdrant")
                return True
            except Exception as e:
                logger.error(f"Qdrant upsert failed: {e}")
        
        return False
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document from vector database."""
        # Try Pinecone delete
        if self.pinecone_index:
            try:
                self.pinecone_index.delete(ids=[doc_id])
                logger.info(f"Deleted document {doc_id} from Pinecone")
                return True
            except Exception as e:
                logger.error(f"Pinecone delete failed: {e}")
        
        # Try Qdrant delete
        if self.qdrant_client:
            try:
                self.qdrant_client.delete(
                    collection_name=self.qdrant_collection,
                    points_selector=[doc_id]
                )
                logger.info(f"Deleted document {doc_id} from Qdrant")
                return True
            except Exception as e:
                logger.error(f"Qdrant delete failed: {e}")
        
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status and configuration."""
        return {
            "service": "vector",
            "status": "healthy" if (self.pinecone_index or self.qdrant_client) else "unavailable",
            "pinecone_available": bool(self.pinecone_index),
            "qdrant_available": bool(self.qdrant_client),
            "openai_available": OPENAI_AVAILABLE and bool(self.openai_api_key),
            "embedding_model": self.embedding_model
        } 