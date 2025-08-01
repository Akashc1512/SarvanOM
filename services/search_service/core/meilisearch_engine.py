"""
Meilisearch Engine - Zero-budget Elasticsearch alternative
Lightning-fast search engine written in Rust with simple REST API.
"""
import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import aiohttp
import json

from .hybrid_retrieval import RetrievalResult, RetrievalSource

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class MeilisearchDocument:
    """Document structure for Meilisearch."""
    id: str
    title: str
    content: str
    url: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class MeilisearchEngine:
    """Meilisearch search engine - zero-budget Elasticsearch alternative."""
    
    def __init__(self, meilisearch_url: str = "http://localhost:7700", 
                 master_key: Optional[str] = None):
        self.meilisearch_url = meilisearch_url.rstrip('/')
        self.master_key = master_key
        self.session = None
        self.index_name = "knowledge_base"
        self.headers = {
            "Content-Type": "application/json"
        }
        if self.master_key:
            self.headers["Authorization"] = f"Bearer {self.master_key}"
        
        logger.info("MeilisearchEngine initialized")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session
    
    async def health_check(self) -> bool:
        """Check if Meilisearch is running."""
        try:
            session = await self._get_session()
            async with session.get(f"{self.meilisearch_url}/health") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Meilisearch health check failed: {e}")
            return False
    
    async def create_index(self) -> bool:
        """Create the search index if it doesn't exist."""
        try:
            session = await self._get_session()
            
            # Check if index exists
            async with session.get(f"{self.meilisearch_url}/indexes/{self.index_name}") as response:
                if response.status == 200:
                    logger.info(f"Index {self.index_name} already exists")
                    return True
            
            # Create index
            index_config = {
                "uid": self.index_name,
                "primaryKey": "id"
            }
            
            async with session.post(
                f"{self.meilisearch_url}/indexes",
                json=index_config
            ) as response:
                if response.status == 201:
                    logger.info(f"Created index {self.index_name}")
                    
                    # Configure searchable attributes
                    await self._configure_index()
                    return True
                else:
                    logger.error(f"Failed to create index: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            return False
    
    async def _configure_index(self):
        """Configure index settings for optimal search."""
        try:
            session = await self._get_session()
            
            # Configure searchable attributes
            searchable_attributes = ["title", "content", "tags"]
            async with session.put(
                f"{self.meilisearch_url}/indexes/{self.index_name}/settings/searchable-attributes",
                json=searchable_attributes
            ) as response:
                if response.status == 200:
                    logger.info("Configured searchable attributes")
            
            # Configure filterable attributes
            filterable_attributes = ["tags", "created_at"]
            async with session.put(
                f"{self.meilisearch_url}/indexes/{self.index_name}/settings/filterable-attributes",
                json=filterable_attributes
            ) as response:
                if response.status == 200:
                    logger.info("Configured filterable attributes")
            
            # Configure sortable attributes
            sortable_attributes = ["created_at", "updated_at"]
            async with session.put(
                f"{self.meilisearch_url}/indexes/{self.index_name}/settings/sortable-attributes",
                json=sortable_attributes
            ) as response:
                if response.status == 200:
                    logger.info("Configured sortable attributes")
                    
        except Exception as e:
            logger.error(f"Failed to configure index: {e}")
    
    async def add_documents(self, documents: List[MeilisearchDocument]) -> bool:
        """Add documents to the search index."""
        try:
            session = await self._get_session()
            
            # Convert documents to Meilisearch format
            docs_data = []
            for doc in documents:
                doc_dict = {
                    "id": doc.id,
                    "title": doc.title,
                    "content": doc.content,
                    "tags": doc.tags
                }
                if doc.url:
                    doc_dict["url"] = doc.url
                if doc.created_at:
                    doc_dict["created_at"] = doc.created_at
                if doc.updated_at:
                    doc_dict["updated_at"] = doc.updated_at
                
                docs_data.append(doc_dict)
            
            # Add documents
            async with session.post(
                f"{self.meilisearch_url}/indexes/{self.index_name}/documents",
                json=docs_data
            ) as response:
                if response.status == 202:
                    logger.info(f"Added {len(documents)} documents to Meilisearch")
                    return True
                else:
                    logger.error(f"Failed to add documents: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False
        finally:
            # Ensure session is properly closed
            if self.session:
                await self.session.close()
                self.session = None
    
    async def search(self, query: str, top_k: int = 10, 
                    filters: Optional[str] = None) -> List[RetrievalResult]:
        """Search Meilisearch for keyword matches."""
        start_time = time.time()
        
        try:
            session = await self._get_session()
            
            # Prepare search parameters
            search_params = {
                "q": query,
                "limit": top_k,
                "attributesToRetrieve": ["id", "title", "content", "url", "tags", "_score"]
            }
            
            if filters:
                search_params["filter"] = filters
            
            # Perform search
            async with session.post(
                f"{self.meilisearch_url}/indexes/{self.index_name}/search",
                json=search_params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    hits = data.get("hits", [])
                    
                    results = []
                    for hit in hits:
                        # Meilisearch returns _score as a string, convert to float
                        score = float(hit.get("_score", 0.0))
                        
                        # Normalize score to 0-1 range (Meilisearch scores are typically 0-1)
                        normalized_score = min(score, 1.0)
                        
                        results.append(RetrievalResult(
                            content=hit.get("content", ""),
                            source=RetrievalSource.MEILISEARCH,
                            score=normalized_score,
                            metadata={
                                "meilisearch_id": hit.get("id"),
                                "title": hit.get("title", ""),
                                "url": hit.get("url"),
                                "tags": hit.get("tags", []),
                                "raw_score": score,
                                "search_engine": "meilisearch"
                            }
                        ))
                    
                    processing_time = (time.time() - start_time) * 1000
                    logger.info(f"Meilisearch search completed in {processing_time:.2f}ms")
                    return results
                else:
                    logger.error(f"Meilisearch search failed: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Meilisearch search failed: {e}")
            return []
        finally:
            # Ensure session is properly closed
            if self.session:
                await self.session.close()
                self.session = None
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from the index."""
        try:
            session = await self._get_session()
            
            async with session.delete(
                f"{self.meilisearch_url}/indexes/{self.index_name}/documents/{document_id}"
            ) as response:
                if response.status == 202:
                    logger.info(f"Deleted document {document_id}")
                    return True
                else:
                    logger.error(f"Failed to delete document: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    async def clear_index(self) -> bool:
        """Clear all documents from the index."""
        try:
            session = await self._get_session()
            
            async with session.delete(
                f"{self.meilisearch_url}/indexes/{self.index_name}/documents"
            ) as response:
                if response.status == 202:
                    logger.info("Cleared all documents from index")
                    return True
                else:
                    logger.error(f"Failed to clear index: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to clear index: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        try:
            session = await self._get_session()
            
            async with session.get(
                f"{self.meilisearch_url}/indexes/{self.index_name}/stats"
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Failed to get stats: {response.status}"}
                    
        except Exception as e:
            return {"error": f"Failed to get stats: {e}"}
    
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()


# Factory function for easy integration
async def create_meilisearch_engine(
    meilisearch_url: str = "http://localhost:7700",
    master_key: Optional[str] = None
) -> MeilisearchEngine:
    """Create and initialize a Meilisearch engine."""
    engine = MeilisearchEngine(meilisearch_url, master_key)
    
    # Check if Meilisearch is running
    if not await engine.health_check():
        logger.warning("Meilisearch is not running. Please start it first.")
        logger.info("To start Meilisearch: docker run -p 7700:7700 getmeili/meilisearch:latest")
        return engine
    
    # Create index if it doesn't exist
    await engine.create_index()
    
    return engine 