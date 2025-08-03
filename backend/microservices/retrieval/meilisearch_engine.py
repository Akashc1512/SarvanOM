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

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logging.warning("python-dotenv not available. Install with: pip install python-dotenv")

# Define local RetrievalResult to avoid circular import
@dataclass
class RetrievalResult:
    """Simple retrieval result for internal use."""
    content: str
    source: str
    score: float
    metadata: Dict[str, Any]


class RetrievalSource:
    """Enumeration of retrieval sources."""
    MEILISEARCH = "meilisearch"
    VECTOR_DB = "vector_db"
    KNOWLEDGE_GRAPH = "knowledge_graph"

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
                    # Configure the existing index
                    await self._configure_index()
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
                    # Configure the new index
                    await self._configure_index()
                    return True
                else:
                    logger.error(f"Failed to create index: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            return False
    
    async def _configure_index(self):
        """Configure searchable attributes and ranking rules."""
        try:
            session = await self._get_session()
            
            # Configure searchable attributes
            searchable_attributes = ["title", "content", "tags"]
            async with session.put(
                f"{self.meilisearch_url}/indexes/{self.index_name}/settings/searchable-attributes",
                json=searchable_attributes
            ) as response:
                if response.status != 202:
                    logger.warning(f"Failed to configure searchable attributes: {response.status}")
            
            # Configure ranking rules
            ranking_rules = [
                "words",
                "typo",
                "proximity",
                "attribute",
                "sort",
                "exactness"
            ]
            async with session.put(
                f"{self.meilisearch_url}/indexes/{self.index_name}/settings/ranking-rules",
                json=ranking_rules
            ) as response:
                if response.status != 202:
                    logger.warning(f"Failed to configure ranking rules: {response.status}")
            
            # Configure filterable attributes
            filterable_attributes = ["tags", "created_at"]
            async with session.put(
                f"{self.meilisearch_url}/indexes/{self.index_name}/settings/filterable-attributes",
                json=filterable_attributes
            ) as response:
                if response.status != 202:
                    logger.warning(f"Failed to configure filterable attributes: {response.status}")
            
            logger.info("Index configuration completed")
            
        except Exception as e:
            logger.error(f"Failed to configure index: {e}")
    
    async def add_documents(self, documents: List[MeilisearchDocument]) -> bool:
        """Add documents to the search index."""
        try:
            session = await self._get_session()
            
            # Convert documents to Meilisearch format
            meilisearch_docs = []
            for doc in documents:
                meilisearch_docs.append({
                    "id": doc.id,
                    "title": doc.title,
                    "content": doc.content,
                    "url": doc.url,
                    "tags": doc.tags,
                    "created_at": doc.created_at,
                    "updated_at": doc.updated_at
                })
            
            # Add documents
            async with session.post(
                f"{self.meilisearch_url}/indexes/{self.index_name}/documents",
                json=meilisearch_docs
            ) as response:
                if response.status == 202:
                    logger.info(f"Added {len(documents)} documents to index")
                    return True
                else:
                    logger.error(f"Failed to add documents: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False
    
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
                        
                        # Debug: Print raw score
                        logger.info(f"Meilisearch raw score for '{hit.get('title', 'Unknown')}': {score}")
                        
                        # Calculate a more meaningful score based on content relevance
                        # If Meilisearch returns 0.0, calculate a score based on query match
                        if score == 0.0:
                            # Calculate a simple relevance score based on query terms in content
                            query_terms = query.lower().split()
                            title = hit.get("title", "").lower()
                            content = hit.get("content", "").lower()
                            
                            # Count matching terms in title (weighted higher)
                            title_matches = sum(1 for term in query_terms if term in title)
                            content_matches = sum(1 for term in query_terms if term in content)
                            
                            # Calculate relevance score (0.1 to 0.9)
                            total_terms = len(query_terms)
                            if total_terms > 0:
                                title_score = (title_matches / total_terms) * 0.6
                                content_score = (content_matches / total_terms) * 0.4
                                calculated_score = title_score + content_score
                                normalized_score = max(0.1, min(0.9, calculated_score))
                            else:
                                normalized_score = 0.1
                        else:
                            # Use Meilisearch score if it's not 0.0
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
                                "calculated_score": normalized_score,
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
            
            async with session.get(f"{self.meilisearch_url}/indexes/{self.index_name}/stats") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get stats: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None


async def create_meilisearch_engine(
    meilisearch_url: str = "http://localhost:7700",
    master_key: Optional[str] = None
) -> MeilisearchEngine:
    """Create and configure a Meilisearch engine instance."""
    engine = MeilisearchEngine(meilisearch_url, master_key)
    
    # Check health
    if not await engine.health_check():
        logger.error("Meilisearch is not running")
        return None
    
    # Create index if it doesn't exist
    if not await engine.create_index():
        logger.error("Failed to create Meilisearch index")
        return None
    
    return engine 