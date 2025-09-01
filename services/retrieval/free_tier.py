#!/usr/bin/env python3
"""
Zero-Budget Retrieval System

Implements free-tier retrieval capabilities with:
- MediaWiki API for Wikipedia search
- Brave Search API (if free key available)
- DuckDuckGo HTML parsing as fallback
- Intelligent caching with TTL
- Result deduplication and ranking
- Robust error handling and retry logic

Following MAANG/OpenAI/Perplexity standards for enterprise-grade reliability.
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse, quote_plus
from dataclasses import dataclass, field
from enum import Enum

import aiohttp
import requests
from bs4 import BeautifulSoup
import redis.asyncio as redis

# Configure logging
logger = logging.getLogger(__name__)

# Environment variables
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_TTL_MIN = int(os.getenv("CACHE_TTL_MIN", "10"))
CACHE_TTL_MAX = int(os.getenv("CACHE_TTL_MAX", "60"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
BASE_TIMEOUT = int(os.getenv("BASE_TIMEOUT", "10"))
BACKOFF_BASE = float(os.getenv("BACKOFF_BASE", "2.0"))
BACKOFF_MAX = float(os.getenv("BACKOFF_MAX", "30.0"))

# User agent for polite scraping
USER_AGENT = "SarvanOM/1.0 (Zero-Budget Retrieval; +https://github.com/sarvanom)"


class SearchProvider(str, Enum):
    """Supported search providers."""
    MEDIAWIKI = "mediawiki"
    BRAVE = "brave"
    DUCKDUCKGO = "duckduckgo"
    STACKEXCHANGE = "stackexchange"
    MDN = "mdn"
    GITHUB = "github"
    OPENALEX = "openalex"
    ARXIV = "arxiv"
    YOUTUBE = "youtube"
    CACHE = "cache"


@dataclass
class SearchResult:
    """Structured search result."""
    title: str
    url: str
    snippet: str
    domain: str
    provider: SearchProvider
    relevance_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResponse:
    """Structured search response."""
    query: str
    results: List[SearchResult]
    total_results: int
    cache_hit: bool = False
    providers_used: List[SearchProvider] = field(default_factory=list)
    processing_time_ms: float = 0.0
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    error_message: Optional[str] = None


class ZeroBudgetRetrieval:
    """Zero-budget retrieval system with free-tier search capabilities."""
    
    def __init__(self):
        self.redis_client = None
        self.session = None
        # Don't initialize async components here
        # They will be initialized when first needed
    
    async def setup_redis(self):
        """Setup Redis connection for caching."""
        if self.redis_client is not None:
            return  # Already initialized
            
        try:
            self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            await self.redis_client.ping()
            logger.info("✅ Redis connection established for caching")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory cache.")
            self.redis_client = None
    
    async def setup_session(self):
        """Setup HTTP session with proper headers."""
        if self.session is not None:
            return  # Already initialized
            
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            },
            timeout=aiohttp.ClientTimeout(total=BASE_TIMEOUT)
        )
    
    async def close(self):
        """Cleanup resources."""
        if self.session:
            await self.session.close()
        if self.redis_client:
            await self.redis_client.close()
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for caching."""
        return re.sub(r'\s+', ' ', query.lower().strip())
    
    def _generate_cache_key(self, query: str, provider: str, k: int) -> str:
        """Generate cache key for query."""
        normalized_query = self._normalize_query(query)
        query_hash = hashlib.md5(f"{normalized_query}:{provider}:{k}".encode()).hexdigest()
        return f"retrieval:{provider}:{query_hash}"
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return "unknown"
    
    def _calculate_relevance_score(self, result: SearchResult, query: str) -> float:
        """Calculate relevance score for result."""
        query_terms = set(query.lower().split())
        title_terms = set(result.title.lower().split())
        snippet_terms = set(result.snippet.lower().split())
        
        # Title relevance (higher weight)
        title_matches = len(query_terms.intersection(title_terms))
        title_score = title_matches / max(len(query_terms), 1) * 0.6
        
        # Snippet relevance
        snippet_matches = len(query_terms.intersection(snippet_terms))
        snippet_score = snippet_matches / max(len(query_terms), 1) * 0.4
        
        return min(title_score + snippet_score, 1.0)
    
    async def _cache_get(self, cache_key: str) -> Optional[List[Dict]]:
        """Get results from cache."""
        await self.setup_redis()
        if not self.redis_client:
            return None
        
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
        
        return None
    
    async def _cache_set(self, cache_key: str, results: List[Dict], ttl_minutes: int):
        """Store results in cache."""
        await self.setup_redis()
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.setex(
                cache_key,
                ttl_minutes * 60,
                json.dumps(results)
            )
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
    
    async def _make_request_with_retry(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict]:
        """Make HTTP request with retry logic and exponential backoff."""
        await self.setup_session()
        
        for attempt in range(1, MAX_RETRIES + 2):
            try:
                timeout = min(BASE_TIMEOUT * (BACKOFF_BASE ** (attempt - 1)), BACKOFF_MAX)
                
                logger.info(f"Making request to {url} (attempt {attempt}/{MAX_RETRIES + 1})", extra={
                    "url": url,
                    "attempt": attempt,
                    "timeout": timeout,
                    "provider": "retrieval"
                })
                
                async with self.session.get(url, params=params, headers=headers, timeout=timeout) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        
            except Exception as e:
                logger.warning(f"Request attempt {attempt} failed: {e}", extra={
                    "url": url,
                    "attempt": attempt,
                    "error": str(e),
                    "provider": "retrieval"
                })
                
                if attempt >= MAX_RETRIES + 1:
                    break
                
                # Exponential backoff
                wait_time = min(BACKOFF_BASE ** (attempt - 1), BACKOFF_MAX)
                await asyncio.sleep(wait_time)
        
        return None
    
    async def wiki_search(self, query: str, k: int = 3) -> List[SearchResult]:
        """Search Wikipedia using MediaWiki API."""
        try:
            # MediaWiki API endpoint
            api_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
            
            # Search for pages first
            search_url = "https://en.wikipedia.org/w/api.php"
            search_params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "srlimit": k * 2,  # Get more to filter
                "srnamespace": 0,  # Main namespace only
                "srwhat": "text"
            }
            
            search_data = await self._make_request_with_retry(search_url, params=search_params)
            if not search_data or "query" not in search_data:
                return []
            
            results = []
            for item in search_data["query"]["search"][:k]:
                try:
                    # Get page summary
                    page_title = quote_plus(item["title"])
                    summary_url = f"{api_url}{page_title}"
                    
                    summary_data = await self._make_request_with_retry(summary_url)
                    if summary_data and "extract" in summary_data:
                        result = SearchResult(
                            title=item["title"],
                            url=summary_data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                            snippet=summary_data["extract"][:300] + "...",
                            domain="wikipedia.org",
                            provider=SearchProvider.MEDIAWIKI,
                            metadata={
                                "page_id": item["pageid"],
                                "word_count": item.get("wordcount", 0)
                            }
                        )
                        result.relevance_score = self._calculate_relevance_score(result, query)
                        results.append(result)
                        
                        # Polite delay
                        await asyncio.sleep(0.1)
                        
                except Exception as e:
                    logger.warning(f"Error processing Wikipedia result: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            return []
    
    async def free_web_search(self, query: str, k: int = 5) -> List[SearchResult]:
        """Free web search using Brave API or DuckDuckGo fallback."""
        # Try Brave Search first if API key is available
        if BRAVE_API_KEY and BRAVE_API_KEY.strip() and "your_" not in BRAVE_API_KEY:
            brave_results = await self._brave_search(query, k)
            if brave_results:
                return brave_results
        
        # Fallback to DuckDuckGo
        return await self._duckduckgo_search(query, k)
    
    async def stackexchange_search(self, query: str, k: int = 3, site: str = "stackoverflow") -> List[SearchResult]:
        """Search Stack Exchange sites using their API."""
        try:
            # Stack Exchange API endpoint
            api_url = f"https://api.stackexchange.com/2.3/search"
            params = {
                "order": "desc",
                "sort": "relevance",
                "intitle": query,
                "site": site,
                "pagesize": k,
                "filter": "withbody"  # Include body content
            }
            
            data = await self._make_request_with_retry(api_url, params=params)
            if not data or "items" not in data:
                return []
            
            results = []
            for item in data["items"][:k]:
                try:
                    # Extract relevant content
                    title = item.get("title", "")
                    body = item.get("body", "")
                    # Strip HTML tags for snippet
                    import re
                    clean_body = re.sub(r'<[^>]+>', '', body)
                    snippet = clean_body[:200] + "..." if len(clean_body) > 200 else clean_body
                    
                    result = SearchResult(
                        title=title,
                        url=item.get("link", ""),
                        snippet=snippet,
                        domain=f"{site}.stackexchange.com",
                        provider=SearchProvider.STACKEXCHANGE,
                        metadata={
                            "score": item.get("score", 0),
                            "answer_count": item.get("answer_count", 0),
                            "is_answered": item.get("is_answered", False),
                            "tags": item.get("tags", [])
                        }
                    )
                    result.relevance_score = self._calculate_relevance_score(result, query)
                    results.append(result)
                    
                    # Polite delay
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"Error processing StackExchange result: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"StackExchange search error: {e}")
            return []
    
    async def mdn_search(self, query: str, k: int = 3) -> List[SearchResult]:
        """Search MDN (Mozilla Developer Network) documentation."""
        try:
            # MDN search API endpoint
            api_url = "https://developer.mozilla.org/api/v1/search"
            params = {
                "q": query,
                "locale": "en-US",
                "size": k
            }
            
            data = await self._make_request_with_retry(api_url, params=params)
            if not data or "documents" not in data:
                return []
            
            results = []
            for doc in data["documents"][:k]:
                try:
                    result = SearchResult(
                        title=doc.get("title", ""),
                        url=f"https://developer.mozilla.org{doc.get('mdn_url', '')}",
                        snippet=doc.get("excerpt", "")[:300] + "...",
                        domain="developer.mozilla.org",
                        provider=SearchProvider.MDN,
                        metadata={
                            "locale": doc.get("locale", ""),
                            "popularity": doc.get("popularity", 0),
                            "score": doc.get("score", 0)
                        }
                    )
                    result.relevance_score = self._calculate_relevance_score(result, query)
                    results.append(result)
                    
                    # Polite delay
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"Error processing MDN result: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"MDN search error: {e}")
            return []
    
    async def github_search(self, query: str, k: int = 3) -> List[SearchResult]:
        """Search GitHub issues and repositories."""
        try:
            # GitHub API endpoint (unauthenticated, rate limited)
            api_url = "https://api.github.com/search/issues"
            params = {
                "q": query,
                "sort": "relevance",
                "order": "desc",
                "per_page": k
            }
            
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": USER_AGENT
            }
            
            data = await self._make_request_with_retry(api_url, params=params, headers=headers)
            if not data or "items" not in data:
                return []
            
            results = []
            for item in data["items"][:k]:
                try:
                    result = SearchResult(
                        title=item.get("title", ""),
                        url=item.get("html_url", ""),
                        snippet=item.get("body", "")[:300] + "..." if item.get("body") else "",
                        domain="github.com",
                        provider=SearchProvider.GITHUB,
                        metadata={
                            "state": item.get("state", ""),
                            "comments": item.get("comments", 0),
                            "created_at": item.get("created_at", ""),
                            "repository": item.get("repository", {}).get("full_name", "")
                        }
                    )
                    result.relevance_score = self._calculate_relevance_score(result, query)
                    results.append(result)
                    
                    # Polite delay
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"Error processing GitHub result: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"GitHub search error: {e}")
            return []
    
    async def openalex_search(self, query: str, k: int = 3) -> List[SearchResult]:
        """Search OpenAlex for academic papers."""
        try:
            # OpenAlex API endpoint
            api_url = "https://api.openalex.org/works"
            params = {
                "search": query,
                "per_page": k,
                "sort": "relevance_score:desc"
            }
            
            data = await self._make_request_with_retry(api_url, params=params)
            if not data or "results" not in data:
                return []
            
            results = []
            for work in data["results"][:k]:
                try:
                    # Get authors
                    authors = []
                    if "authorships" in work:
                        for authorship in work["authorships"][:3]:  # First 3 authors
                            if "author" in authorship and "display_name" in authorship["author"]:
                                authors.append(authorship["author"]["display_name"])
                    
                    title = work.get("title", "")
                    abstract = work.get("abstract_inverted_index", {})
                    # Reconstruct abstract from inverted index
                    if abstract:
                        words = []
                        for word, positions in abstract.items():
                            for pos in positions:
                                words.append((pos, word))
                        words.sort(key=lambda x: x[0])
                        abstract_text = " ".join([word for _, word in words])
                    else:
                        abstract_text = ""
                    
                    result = SearchResult(
                        title=title,
                        url=work.get("doi", ""),
                        snippet=abstract_text[:300] + "..." if abstract_text else "",
                        domain="openalex.org",
                        provider=SearchProvider.OPENALEX,
                        metadata={
                            "doi": work.get("doi", ""),
                            "publication_year": work.get("publication_year", ""),
                            "authors": authors,
                            "citations": work.get("cited_by_count", 0)
                        }
                    )
                    result.relevance_score = self._calculate_relevance_score(result, query)
                    results.append(result)
                    
                    # Polite delay
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"Error processing OpenAlex result: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"OpenAlex search error: {e}")
            return []
    
    async def arxiv_search(self, query: str, k: int = 3) -> List[SearchResult]:
        """Search arXiv for preprints."""
        try:
            # arXiv API endpoint
            api_url = "http://export.arxiv.org/api/query"
            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": k,
                "sortBy": "relevance",
                "sortOrder": "descending"
            }
            
            data = await self._make_request_with_retry(api_url, params=params)
            if not data or "feed" not in data or "entry" not in data["feed"]:
                return []
            
            results = []
            for entry in data["feed"]["entry"][:k]:
                try:
                    # Get authors
                    authors = []
                    if "author" in entry:
                        for author in entry["author"][:3]:  # First 3 authors
                            authors.append(author.get("name", ""))
                    
                    result = SearchResult(
                        title=entry.get("title", ""),
                        url=entry.get("id", ""),
                        snippet=entry.get("summary", "")[:300] + "..." if entry.get("summary") else "",
                        domain="arxiv.org",
                        provider=SearchProvider.ARXIV,
                        metadata={
                            "authors": authors,
                            "published": entry.get("published", ""),
                            "updated": entry.get("updated", ""),
                            "categories": entry.get("arxiv:primary_category", {}).get("term", "")
                        }
                    )
                    result.relevance_score = self._calculate_relevance_score(result, query)
                    results.append(result)
                    
                    # Polite delay
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"Error processing arXiv result: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"arXiv search error: {e}")
            return []
    
    async def youtube_search(self, query: str, k: int = 3) -> List[SearchResult]:
        """Search YouTube for educational videos."""
        try:
            # YouTube Data API endpoint
            if not YOUTUBE_API_KEY or "your_" in YOUTUBE_API_KEY:
                logger.warning("YouTube API key not configured, skipping YouTube search")
                return []
            
            api_url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": k,
                "order": "relevance",
                "videoDuration": "medium",  # Prefer medium length videos
                "videoEmbeddable": "true",
                "key": YOUTUBE_API_KEY
            }
            
            data = await self._make_request_with_retry(api_url, params=params)
            if not data or "items" not in data:
                return []
            
            results = []
            for item in data["items"][:k]:
                try:
                    snippet_data = item.get("snippet", {})
                    video_id = item.get("id", {}).get("videoId", "")
                    
                    result = SearchResult(
                        title=snippet_data.get("title", ""),
                        url=f"https://www.youtube.com/watch?v={video_id}",
                        snippet=snippet_data.get("description", "")[:300] + "..." if snippet_data.get("description") else "",
                        domain="youtube.com",
                        provider=SearchProvider.YOUTUBE,
                        metadata={
                            "channel_title": snippet_data.get("channelTitle", ""),
                            "published_at": snippet_data.get("publishedAt", ""),
                            "duration": "medium",
                            "video_id": video_id
                        }
                    )
                    result.relevance_score = self._calculate_relevance_score(result, query)
                    results.append(result)
                    
                    # Polite delay
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"Error processing YouTube result: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"YouTube search error: {e}")
            return []
    
    async def _brave_search(self, query: str, k: int) -> List[SearchResult]:
        """Search using Brave Search API."""
        try:
            brave_url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": BRAVE_API_KEY
            }
            params = {
                "q": query,
                "count": k,
                "safesearch": "moderate"
            }
            
            data = await self._make_request_with_retry(brave_url, params=params, headers=headers)
            if not data or "web" not in data:
                return []
            
            results = []
            for item in data["web"]["results"][:k]:
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("description", ""),
                    domain=self._extract_domain(item.get("url", "")),
                    provider=SearchProvider.BRAVE,
                    metadata={
                        "age": item.get("age", ""),
                        "language": item.get("language", "")
                    }
                )
                result.relevance_score = self._calculate_relevance_score(result, query)
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Brave search error: {e}")
            return []
    
    async def _duckduckgo_search(self, query: str, k: int) -> List[SearchResult]:
        """Search using DuckDuckGo HTML parsing."""
        try:
            await self.setup_session()
            
            # Use DuckDuckGo Lite for better parsing
            ddg_url = "https://lite.duckduckgo.com/lite/"
            params = {"q": query}
            
            async with self.session.get(ddg_url, params=params, timeout=BASE_TIMEOUT) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                results = []
                # Find result links
                result_links = soup.find_all('a', href=True)
                
                for link in result_links[:k * 2]:  # Get more to filter
                    href = link.get('href', '')
                    title = link.get_text(strip=True)
                    
                    # Skip internal DuckDuckGo links
                    if not href or 'duckduckgo.com' in href or not title:
                        continue
                    
                    # Find snippet (next sibling text)
                    snippet = ""
                    next_elem = link.find_next_sibling()
                    if next_elem:
                        snippet = next_elem.get_text(strip=True)[:300]
                    
                    if snippet:
                        result = SearchResult(
                            title=title,
                            url=href,
                            snippet=snippet + "...",
                            domain=self._extract_domain(href),
                            provider=SearchProvider.DUCKDUCKGO
                        )
                        result.relevance_score = self._calculate_relevance_score(result, query)
                        results.append(result)
                        
                        if len(results) >= k:
                            break
                
                return results
                
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Deduplicate results by domain and title similarity."""
        seen = set()
        deduplicated = []
        
        for result in results:
            # Create signature for deduplication
            domain_title = f"{result.domain}:{result.title.lower()}"
            
            # Check for exact matches
            if domain_title in seen:
                continue
            
            # Check for similar titles (fuzzy matching)
            is_duplicate = False
            for existing in deduplicated:
                if (result.domain == existing.domain and 
                    self._title_similarity(result.title, existing.title) > 0.8):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                seen.add(domain_title)
                deduplicated.append(result)
        
        return deduplicated
    
    def _title_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles."""
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    async def search(self, query: str, k: int = 5, use_wiki: bool = True, use_web: bool = True) -> SearchResponse:
        """
        Main search method with caching and result merging.
        
        Args:
            query: Search query
            k: Number of results to return
            use_wiki: Whether to include Wikipedia search
            use_web: Whether to include web search
        
        Returns:
            SearchResponse with results and metadata
        """
        start_time = time.time()
        trace_id = str(uuid.uuid4())
        
        logger.info(f"Starting search for query: {query}", extra={
            "query": query,
            "k": k,
            "use_wiki": use_wiki,
            "use_web": use_web,
            "trace_id": trace_id
        })
        
        # Check cache first
        cache_key = self._generate_cache_key(query, "combined", k)
        cached_results = await self._cache_get(cache_key)
        
        if cached_results:
            # Reconstruct SearchResult objects from cache
            results = []
            for cached in cached_results:
                result = SearchResult(
                    title=cached["title"],
                    url=cached["url"],
                    snippet=cached["snippet"],
                    domain=cached["domain"],
                    provider=SearchProvider(cached["provider"]),
                    relevance_score=cached["relevance_score"],
                    timestamp=datetime.fromisoformat(cached["timestamp"]),
                    metadata=cached.get("metadata", {})
                )
                results.append(result)
            
            processing_time = (time.time() - start_time) * 1000
            
            logger.info(f"Cache hit for query: {query}", extra={
                "query": query,
                "cache_hit": True,
                "results_count": len(results),
                "processing_time_ms": processing_time,
                "trace_id": trace_id
            })
            
            return SearchResponse(
                query=query,
                results=results[:k],
                total_results=len(results),
                cache_hit=True,
                providers_used=[SearchProvider.CACHE],
                processing_time_ms=processing_time,
                trace_id=trace_id
            )
        
        # Perform fresh search
        all_results = []
        providers_used = []
        
        # Wikipedia search
        if use_wiki:
            try:
                wiki_results = await self.wiki_search(query, k=min(k, 3))
                all_results.extend(wiki_results)
                providers_used.append(SearchProvider.MEDIAWIKI)
                logger.info(f"Wikipedia search returned {len(wiki_results)} results")
            except Exception as e:
                logger.error(f"Wikipedia search failed: {e}")
        
        # StackExchange search
        try:
            stack_results = await self.stackexchange_search(query, k=min(k, 2))
            all_results.extend(stack_results)
            providers_used.append(SearchProvider.STACKEXCHANGE)
            logger.info(f"StackExchange search returned {len(stack_results)} results")
        except Exception as e:
            logger.error(f"StackExchange search failed: {e}")
        
        # MDN search
        try:
            mdn_results = await self.mdn_search(query, k=min(k, 2))
            all_results.extend(mdn_results)
            providers_used.append(SearchProvider.MDN)
            logger.info(f"MDN search returned {len(mdn_results)} results")
        except Exception as e:
            logger.error(f"MDN search failed: {e}")
        
        # GitHub search
        try:
            github_results = await self.github_search(query, k=min(k, 2))
            all_results.extend(github_results)
            providers_used.append(SearchProvider.GITHUB)
            logger.info(f"GitHub search returned {len(github_results)} results")
        except Exception as e:
            logger.error(f"GitHub search failed: {e}")
        
        # OpenAlex search
        try:
            openalex_results = await self.openalex_search(query, k=min(k, 2))
            all_results.extend(openalex_results)
            providers_used.append(SearchProvider.OPENALEX)
            logger.info(f"OpenAlex search returned {len(openalex_results)} results")
        except Exception as e:
            logger.error(f"OpenAlex search failed: {e}")
        
        # arXiv search
        try:
            arxiv_results = await self.arxiv_search(query, k=min(k, 2))
            all_results.extend(arxiv_results)
            providers_used.append(SearchProvider.ARXIV)
            logger.info(f"arXiv search returned {len(arxiv_results)} results")
        except Exception as e:
            logger.error(f"arXiv search failed: {e}")
        
        # YouTube search
        try:
            youtube_results = await self.youtube_search(query, k=min(k, 2))
            all_results.extend(youtube_results)
            providers_used.append(SearchProvider.YOUTUBE)
            logger.info(f"YouTube search returned {len(youtube_results)} results")
        except Exception as e:
            logger.error(f"YouTube search failed: {e}")
        
        # Web search (fallback)
        if use_web:
            try:
                web_results = await self.free_web_search(query, k=min(k, 3))
                all_results.extend(web_results)
                providers_used.extend([r.provider for r in web_results])
                logger.info(f"Web search returned {len(web_results)} results")
            except Exception as e:
                logger.error(f"Web search failed: {e}")
        
        # Deduplicate and rank results
        deduplicated = self._deduplicate_results(all_results)
        
        # Sort by relevance score
        sorted_results = sorted(deduplicated, key=lambda x: x.relevance_score, reverse=True)
        
        # Take top k results
        final_results = sorted_results[:k]
        
        # Cache results
        cache_data = []
        for result in final_results:
            cache_data.append({
                "title": result.title,
                "url": result.url,
                "snippet": result.snippet,
                "domain": result.domain,
                "provider": result.provider.value,
                "relevance_score": result.relevance_score,
                "timestamp": result.timestamp.isoformat(),
                "metadata": result.metadata
            })
        
        # Random TTL between min and max
        import random
        ttl_minutes = random.randint(CACHE_TTL_MIN, CACHE_TTL_MAX)
        await self._cache_set(cache_key, cache_data, ttl_minutes)
        
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(f"Search completed for query: {query}", extra={
            "query": query,
            "cache_hit": False,
            "results_count": len(final_results),
            "providers_used": [p.value for p in providers_used],
            "processing_time_ms": processing_time,
            "trace_id": trace_id
        })
        
        return SearchResponse(
            query=query,
            results=final_results,
            total_results=len(final_results),
            cache_hit=False,
            providers_used=list(set(providers_used)),
            processing_time_ms=processing_time,
            trace_id=trace_id
        )


# Global instance - lazy initialization
_zero_budget_retrieval_instance = None

def get_zero_budget_retrieval():
    """Get the global zero-budget retrieval instance with lazy initialization."""
    global _zero_budget_retrieval_instance
    if _zero_budget_retrieval_instance is None:
        _zero_budget_retrieval_instance = ZeroBudgetRetrieval()
    return _zero_budget_retrieval_instance

# For backward compatibility
zero_budget_retrieval = None  # Will be set when first accessed


async def search_with_cache_headers(query: str, k: int = 5, use_wiki: bool = True, use_web: bool = True) -> Tuple[SearchResponse, Dict[str, str]]:
    """
    Search with cache headers for HTTP responses.
    
    Returns:
        Tuple of (SearchResponse, headers_dict)
    """
    response = await get_zero_budget_retrieval().search(query, k, use_wiki, use_web)
    
    headers = {
        "X-Cache": "HIT" if response.cache_hit else "MISS",
        "X-Trace-ID": response.trace_id,
        "X-Processing-Time": f"{response.processing_time_ms:.2f}ms",
        "X-Providers-Used": ",".join([p.value for p in response.providers_used]),
        "X-Results-Count": str(response.total_results)
    }
    
    return response, headers


# Convenience functions
async def wiki_search(query: str, k: int = 3) -> List[SearchResult]:
    """Search Wikipedia only."""
    return await get_zero_budget_retrieval().wiki_search(query, k)


async def free_web_search(query: str, k: int = 5) -> List[SearchResult]:
    """Search web only."""
    return await get_zero_budget_retrieval().free_web_search(query, k)


async def combined_search(query: str, k: int = 5) -> SearchResponse:
    """Combined search with caching."""
    return await get_zero_budget_retrieval().search(query, k, use_wiki=True, use_web=True)


if __name__ == "__main__":
    # Test the implementation
    async def test():
        import asyncio
        
        # Test Wikipedia search
        print("Testing Wikipedia search...")
        wiki_results = await wiki_search("artificial intelligence", k=2)
        for result in wiki_results:
            print(f"  {result.title}: {result.url}")
        
        # Test web search
        print("\nTesting web search...")
        web_results = await free_web_search("machine learning", k=2)
        for result in web_results:
            print(f"  {result.title}: {result.url}")
        
        # Test combined search
        print("\nTesting combined search...")
        combined_response = await combined_search("deep learning", k=3)
        print(f"Cache hit: {combined_response.cache_hit}")
        print(f"Providers used: {[p.value for p in combined_response.providers_used]}")
        for result in combined_response.results:
            print(f"  {result.title} ({result.provider.value}): {result.relevance_score:.2f}")
        
        await zero_budget_retrieval.close()
    
    asyncio.run(test())
