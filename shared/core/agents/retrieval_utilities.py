"""
Retrieval Utilities - Shared Functions for Retrieval Workflows

This module provides reusable utility functions to eliminate duplicate logic
in retrieval workflows across different agents and services. It includes:

1. Common search patterns and strategies
2. Result processing and fusion
3. Document formatting and optimization
4. Query expansion and refinement
5. Cache management
6. Fallback mechanisms

This reduces code duplication and ensures consistent retrieval behavior.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import re

from shared.core.unified_logging import get_logger

logger = get_logger(__name__)


class SearchStrategy(Enum):
    """Search strategy types."""
    VECTOR = "vector"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    GRAPH = "graph"
    WEB = "web"
    SEMANTIC = "semantic"


@dataclass
class SearchResult:
    """Standardized search result format."""
    
    documents: List[Dict[str, Any]]
    search_type: str
    query_time_ms: int
    total_hits: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0


@dataclass
class Document:
    """Standardized document format."""
    
    content: str
    score: float
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    doc_id: str = ""
    chunk_id: Optional[str] = None
    timestamp: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "score": self.score,
            "source": self.source,
            "metadata": self.metadata,
            "doc_id": self.doc_id,
            "chunk_id": self.chunk_id,
            "timestamp": self.timestamp,
        }


class QueryProcessor:
    """Common query processing utilities."""
    
    @staticmethod
    def extract_keywords(query: str) -> List[str]:
        """Extract keywords from query."""
        # Remove common stop words and extract meaningful terms
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Clean and tokenize
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    @staticmethod
    def expand_query(query: str) -> List[str]:
        """Expand query with related terms."""
        # Simple query expansion - in practice, this could use LLM or thesaurus
        expansions = []
        
        # Add original query
        expansions.append(query)
        
        # Add keyword-based expansion
        keywords = QueryProcessor.extract_keywords(query)
        if keywords:
            expansions.append(" ".join(keywords))
        
        # Add common variations
        if "what is" in query.lower():
            expansions.append(query.replace("what is", "definition of"))
        if "how to" in query.lower():
            expansions.append(query.replace("how to", "steps for"))
        
        return list(set(expansions))  # Remove duplicates
    
    @staticmethod
    def classify_query_intent(query: str) -> Dict[str, Any]:
        """Classify query intent for search strategy selection."""
        query_lower = query.lower()
        
        intent = {
            "type": "general",
            "complexity": "simple",
            "entities": [],
            "requires_facts": False,
            "requires_procedures": False,
            "requires_definitions": False
        }
        
        # Intent classification
        if any(word in query_lower for word in ["what is", "define", "definition"]):
            intent["type"] = "definition"
            intent["requires_definitions"] = True
        elif any(word in query_lower for word in ["how to", "steps", "procedure"]):
            intent["type"] = "procedural"
            intent["requires_procedures"] = True
        elif any(word in query_lower for word in ["why", "cause", "reason"]):
            intent["type"] = "explanatory"
            intent["requires_facts"] = True
        elif any(word in query_lower for word in ["compare", "difference", "vs"]):
            intent["type"] = "comparative"
            intent["requires_facts"] = True
        
        # Complexity assessment
        word_count = len(query.split())
        if word_count > 10:
            intent["complexity"] = "complex"
        elif word_count > 5:
            intent["complexity"] = "moderate"
        
        return intent


class ResultProcessor:
    """Common result processing utilities."""
    
    @staticmethod
    def deduplicate_documents(documents: List[Document], similarity_threshold: float = 0.8) -> List[Document]:
        """Remove duplicate or very similar documents."""
        if not documents:
            return documents
        
        unique_docs = []
        seen_contents = set()
        
        for doc in documents:
            # Create a simplified content signature
            content_signature = ResultProcessor._create_content_signature(doc.content)
            
            if content_signature not in seen_contents:
                seen_contents.add(content_signature)
                unique_docs.append(doc)
        
        return unique_docs
    
    @staticmethod
    def _create_content_signature(content: str) -> str:
        """Create a signature for content similarity checking."""
        # Normalize content for comparison
        normalized = re.sub(r'\s+', ' ', content.lower().strip())
        # Take first 100 characters as signature
        return normalized[:100]
    
    @staticmethod
    def rank_documents(documents: List[Document], query: str) -> List[Document]:
        """Rank documents by relevance to query."""
        if not documents:
            return documents
        
        # Simple ranking based on score and content relevance
        for doc in documents:
            relevance_score = ResultProcessor._calculate_relevance(doc.content, query)
            doc.score = (doc.score + relevance_score) / 2
        
        # Sort by score (highest first)
        return sorted(documents, key=lambda x: x.score, reverse=True)
    
    @staticmethod
    def _calculate_relevance(content: str, query: str) -> float:
        """Calculate content relevance to query."""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        if not query_words:
            return 0.0
        
        # Calculate word overlap
        overlap = len(query_words.intersection(content_words))
        return min(overlap / len(query_words), 1.0)
    
    @staticmethod
    def format_documents_for_llm(documents: List[Document], max_tokens: int = 4000) -> str:
        """Format documents for LLM consumption."""
        if not documents:
            return ""
        
        formatted_docs = []
        current_tokens = 0
        token_per_char_estimate = 0.25  # Rough estimate
        
        for i, doc in enumerate(documents):
            doc_text = f"[{i+1}] {doc.content}\nSource: {doc.source}\n"
            estimated_tokens = len(doc_text) * token_per_char_estimate
            
            if current_tokens + estimated_tokens > max_tokens:
                break
            
            formatted_docs.append(doc_text)
            current_tokens += estimated_tokens
        
        return "\n".join(formatted_docs)


class SearchFusion:
    """Result fusion strategies for multiple search sources."""
    
    @staticmethod
    async def fuse_results(
        results: List[SearchResult],
        fusion_strategy: str = "weighted"
    ) -> SearchResult:
        """Fuse multiple search results into a single result."""
        if not results:
            return SearchResult(
                documents=[],
                search_type="fused",
                query_time_ms=0,
                total_hits=0
            )
        
        if fusion_strategy == "weighted":
            return SearchFusion._weighted_fusion(results)
        elif fusion_strategy == "reciprocal_rank":
            return SearchFusion._reciprocal_rank_fusion(results)
        else:
            return SearchFusion._simple_fusion(results)
    
    @staticmethod
    def _weighted_fusion(results: List[SearchResult]) -> SearchResult:
        """Weighted fusion based on search type confidence."""
        all_documents = []
        total_time = 0
        
        # Define weights for different search types
        weights = {
            "vector": 0.4,
            "keyword": 0.3,
            "hybrid": 0.5,
            "graph": 0.3,
            "web": 0.2,
            "semantic": 0.4
        }
        
        for result in results:
            weight = weights.get(result.search_type, 0.3)
            
            for doc in result.documents:
                if isinstance(doc, dict):
                    doc_obj = Document(**doc)
                else:
                    doc_obj = doc
                
                # Apply weight to score
                doc_obj.score *= weight
                all_documents.append(doc_obj)
            
            total_time += result.query_time_ms
        
        # Deduplicate and rank
        unique_docs = ResultProcessor.deduplicate_documents(all_documents)
        ranked_docs = ResultProcessor.rank_documents(unique_docs, "")
        
        return SearchResult(
            documents=[doc.to_dict() for doc in ranked_docs],
            search_type="fused_weighted",
            query_time_ms=total_time,
            total_hits=len(ranked_docs),
            metadata={"fusion_strategy": "weighted", "source_results": len(results)}
        )
    
    @staticmethod
    def _reciprocal_rank_fusion(results: List[SearchResult]) -> SearchResult:
        """Reciprocal rank fusion for result combination."""
        doc_scores = {}
        total_time = 0
        
        for result in results:
            for i, doc in enumerate(result.documents):
                if isinstance(doc, dict):
                    doc_id = doc.get("doc_id", f"doc_{i}")
                    content = doc.get("content", "")
                else:
                    doc_id = getattr(doc, "doc_id", f"doc_{i}")
                    content = getattr(doc, "content", "")
                
                # Reciprocal rank scoring
                rank_score = 1.0 / (i + 1)
                
                if doc_id in doc_scores:
                    doc_scores[doc_id]["score"] += rank_score
                    doc_scores[doc_id]["count"] += 1
                else:
                    doc_scores[doc_id] = {
                        "doc": doc,
                        "score": rank_score,
                        "count": 1,
                        "content": content
                    }
            
            total_time += result.query_time_ms
        
        # Create fused documents
        fused_docs = []
        for doc_id, score_info in doc_scores.items():
            # Normalize score by number of appearances
            normalized_score = score_info["score"] / score_info["count"]
            
            if isinstance(score_info["doc"], dict):
                doc_dict = score_info["doc"].copy()
                doc_dict["score"] = normalized_score
            else:
                doc_dict = score_info["doc"].to_dict()
                doc_dict["score"] = normalized_score
            
            fused_docs.append(doc_dict)
        
        # Sort by score
        fused_docs.sort(key=lambda x: x["score"], reverse=True)
        
        return SearchResult(
            documents=fused_docs,
            search_type="fused_reciprocal_rank",
            query_time_ms=total_time,
            total_hits=len(fused_docs),
            metadata={"fusion_strategy": "reciprocal_rank", "source_results": len(results)}
        )
    
    @staticmethod
    def _simple_fusion(results: List[SearchResult]) -> SearchResult:
        """Simple concatenation fusion."""
        all_documents = []
        total_time = 0
        
        for result in results:
            all_documents.extend(result.documents)
            total_time += result.query_time_ms
        
        # Deduplicate
        if all_documents and isinstance(all_documents[0], dict):
            doc_objects = [Document(**doc) for doc in all_documents]
        else:
            doc_objects = all_documents
        
        unique_docs = ResultProcessor.deduplicate_documents(doc_objects)
        
        return SearchResult(
            documents=[doc.to_dict() if hasattr(doc, 'to_dict') else doc for doc in unique_docs],
            search_type="fused_simple",
            query_time_ms=total_time,
            total_hits=len(unique_docs),
            metadata={"fusion_strategy": "simple", "source_results": len(results)}
        )


class CacheManager:
    """Simple cache management for search results."""
    
    def __init__(self, max_size: int = 1000):
        """Initialize cache manager."""
        self.cache = {}
        self.max_size = max_size
        self.access_times = {}
    
    def get(self, key: str) -> Optional[SearchResult]:
        """Get cached result."""
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
    
    def set(self, key: str, result: SearchResult):
        """Set cached result."""
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[key] = result
        self.access_times[key] = time.time()
    
    def _evict_oldest(self):
        """Evict oldest cache entry."""
        if not self.access_times:
            return
        
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        del self.cache[oldest_key]
        del self.access_times[oldest_key]
    
    def clear(self):
        """Clear all cached results."""
        self.cache.clear()
        self.access_times.clear()


class FallbackManager:
    """Fallback mechanisms for search failures."""
    
    @staticmethod
    async def execute_with_fallback(
        primary_func: callable,
        fallback_func: callable,
        *args,
        **kwargs
    ) -> SearchResult:
        """Execute primary function with fallback."""
        try:
            return await primary_func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Primary search failed, using fallback: {str(e)}")
            try:
                return await fallback_func(*args, **kwargs)
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {str(fallback_error)}")
                return SearchResult(
                    documents=[],
                    search_type="fallback_failed",
                    query_time_ms=0,
                    total_hits=0,
                    metadata={"error": str(fallback_error)}
                )
    
    @staticmethod
    def create_mock_result(query: str) -> SearchResult:
        """Create a mock result for emergency fallback."""
        mock_doc = Document(
            content=f"Unable to retrieve information for: {query}. Please try again later.",
            score=0.0,
            source="fallback",
            metadata={"fallback": True, "error": "Search service unavailable"}
        )
        
        return SearchResult(
            documents=[mock_doc.to_dict()],
            search_type="mock_fallback",
            query_time_ms=0,
            total_hits=1,
            metadata={"fallback": True, "mock": True}
        )


# Convenience functions for easy integration
def create_search_result(
    documents: List[Dict[str, Any]],
    search_type: str,
    query_time_ms: int,
    total_hits: int,
    metadata: Dict[str, Any] = None
) -> SearchResult:
    """Create a standardized search result."""
    return SearchResult(
        documents=documents,
        search_type=search_type,
        query_time_ms=query_time_ms,
        total_hits=total_hits,
        metadata=metadata or {}
    )


def create_document(
    content: str,
    score: float,
    source: str,
    metadata: Dict[str, Any] = None,
    doc_id: str = "",
    chunk_id: Optional[str] = None
) -> Document:
    """Create a standardized document."""
    return Document(
        content=content,
        score=score,
        source=source,
        metadata=metadata or {},
        doc_id=doc_id,
        chunk_id=chunk_id
    )


async def execute_search_with_fallback(
    primary_search: callable,
    fallback_search: callable,
    query: str,
    **kwargs
) -> SearchResult:
    """Execute search with automatic fallback."""
    return await FallbackManager.execute_with_fallback(
        primary_search,
        fallback_search,
        query,
        **kwargs
    ) 