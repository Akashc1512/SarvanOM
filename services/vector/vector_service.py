"""
Vector Service

This module provides vector operations for the backend vector service.

# DEAD CODE - Candidate for deletion: This backend directory is not used by the main application
"""

import os
import logging
from typing import Dict, List, Any, Optional
import openai
import pinecone
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.embedding_model = self.config.get("embedding_model", "text-embedding-ada-002")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_env = os.getenv("PINECONE_ENVIRONMENT")
        self.pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_collection = self.config.get("collection_name", "knowledge_base")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.pinecone_index = None
        self.qdrant_client = None
        self._initialize_vector_db()
    
    def _initialize_vector_db(self):
        """Initialize vector database connections."""
        try:
            # Initialize OpenAI for embeddings
            if self.openai_api_key:
                openai.api_key = self.openai_api_key
                logger.info("OpenAI initialized for embeddings")
            
            # Initialize Pinecone with new API
            if self.pinecone_api_key:
                from pinecone import Pinecone
                self.pinecone_client = Pinecone(api_key=self.pinecone_api_key)
                if self.pinecone_index_name in self.pinecone_client.list_indexes().names():
                    self.pinecone_index = self.pinecone_client.Index(self.pinecone_index_name)
                    logger.info("Pinecone index initialized")
                else:
                    logger.warning("Pinecone index not found")
            
            # Initialize Qdrant
            if self.qdrant_url:
                self.qdrant_client = QdrantClient(url=self.qdrant_url)
                logger.info("Qdrant client initialized")
            
        except Exception as e:
            logger.error(f"Error initializing vector database: {e}")
    
    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for given text."""
        try:
            if not self.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            
            response = openai.Embedding.create(
                input=text,
                model=self.embedding_model
            )
            return response['data'][0]['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        try:
            embedding = await self.get_embedding(query)
            results = []
            
            # Search in Pinecone
            if self.pinecone_index:
                pinecone_results = self.pinecone_index.query(
                    vector=embedding,
                    top_k=top_k,
                    include_metadata=True
                )
                for match in pinecone_results.matches:
                    results.append({
                        "id": match.id,
                        "score": match.score,
                        "metadata": match.metadata,
                        "source": "pinecone"
                    })
            
            # Search in Qdrant
            if self.qdrant_client:
                qdrant_results = self.qdrant_client.search(
                    collection_name=self.qdrant_collection,
                    query_vector=embedding,
                    limit=top_k
                )
                for result in qdrant_results:
                    results.append({
                        "id": result.id,
                        "score": result.score,
                        "payload": result.payload,
                        "source": "qdrant"
                    })
            
            return results
        except Exception as e:
            logger.error(f"Error searching similar vectors: {e}")
            raise
    
    async def upsert_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Upsert documents to vector database."""
        try:
            for doc in documents:
                embedding = await self.get_embedding(doc["text"])
                
                # Upsert to Pinecone
                if self.pinecone_index:
                    self.pinecone_index.upsert(
                        vectors=[{
                            "id": doc["id"],
                            "values": embedding,
                            "metadata": doc.get("metadata", {})
                        }]
                    )
                
                # Upsert to Qdrant
                if self.qdrant_client:
                    self.qdrant_client.upsert(
                        collection_name=self.qdrant_collection,
                        points=[{
                            "id": doc["id"],
                            "vector": embedding,
                            "payload": doc.get("metadata", {})
                        }]
                    )
            
            logger.info(f"Upserted {len(documents)} documents")
            return True
        except Exception as e:
            logger.error(f"Error upserting documents: {e}")
            return False
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete document from vector database."""
        try:
            # Delete from Pinecone
            if self.pinecone_index:
                self.pinecone_index.delete(ids=[doc_id])
            
            # Delete from Qdrant
            if self.qdrant_client:
                self.qdrant_client.delete(
                    collection_name=self.qdrant_collection,
                    points_selector=[doc_id]
                )
            
            logger.info(f"Deleted document {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get service status."""
        return {
            "status": "healthy",
            "openai_configured": bool(self.openai_api_key),
            "pinecone_configured": bool(self.pinecone_index),
            "qdrant_configured": bool(self.qdrant_client),
            "embedding_model": self.embedding_model
        }
    
    async def shutdown(self):
        """Shutdown the service."""
        logger.info("VectorService shutting down") 