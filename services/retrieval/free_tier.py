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

# Add circuit breaker imports and configuration
import asyncio
import hashlib
import json
import logging
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

import aiohttp
import feedparser
from bs4 import BeautifulSoup

# Configure logging
logger = logging.getLogger(__name__)

# Environment variables with defaults
CACHE_TTL_MAX = int(os.getenv("CACHE_TTL_MAX", "60"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
BASE_TIMEOUT = int(os.getenv("BASE_TIMEOUT", "2"))
BACKOFF_BASE = float(os.getenv("BACKOFF_BASE", "2.0"))
BACKOFF_MAX = float(os.getenv("BACKOFF_MAX", "30.0"))

# Circuit breaker configuration
CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "3"))
CIRCUIT_BREAKER_TIMEOUT_SECONDS = int(os.getenv("CIRCUIT_BREAKER_TIMEOUT_SECONDS", "60"))
PROVIDER_TIMEOUT_MS = int(os.getenv("PROVIDER_TIMEOUT_MS", "1500"))  # 1.5s per provider

# Provider-specific timeouts (balanced for 3s SLA)
WIKIPEDIA_TIMEOUT_MS = int(os.getenv("WIKIPEDIA_TIMEOUT_MS", "800"))
STACKEXCHANGE_TIMEOUT_MS = int(os.getenv("STACKEXCHANGE_TIMEOUT_MS", "800"))
MDN_TIMEOUT_MS = int(os.getenv("MDN_TIMEOUT_MS", "800"))
GITHUB_TIMEOUT_MS = int(os.getenv("GITHUB_TIMEOUT_MS", "800"))
OPENALEX_TIMEOUT_MS = int(os.getenv("OPENALEX_TIMEOUT_MS", "800"))
ARXIV_TIMEOUT_MS = int(os.getenv("ARXIV_TIMEOUT_MS", "800"))
YOUTUBE_TIMEOUT_MS = int(os.getenv("YOUTUBE_TIMEOUT_MS", "800"))
DUCKDUCKGO_TIMEOUT_MS = int(os.getenv("DUCKDUCKGO_TIMEOUT_MS", "800"))


class ProviderStatus(Enum):
    """Provider health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    CIRCUIT_OPEN = "circuit_open"


@dataclass
class ProviderHealth:
    """Provider health tracking."""
    provider: str
    status: ProviderStatus = ProviderStatus.HEALTHY
    failure_count: int = 0
    last_failure: float = 0.0
    last_success: float = 0.0
    avg_response_time: float = 0.0
    total_requests: int = 0
    
    def record_failure(self):
        """Record a provider failure."""
        self.failure_count += 1
        self.last_failure = time.time()
        self.status = ProviderStatus.FAILING if self.failure_count >= CIRCUIT_BREAKER_FAILURE_THRESHOLD else ProviderStatus.DEGRADED
    
    def record_success(self, response_time: float):
        """Record a provider success."""
        self.last_success = time.time()
        self.total_requests += 1
        
        # Update average response time
        if self.total_requests == 1:
            self.avg_response_time = response_time
        else:
            self.avg_response_time = (self.avg_response_time * (self.total_requests - 1) + response_time) / self.total_requests
        
        # Reset failure count on success
        if self.failure_count > 0:
            self.failure_count = max(0, self.failure_count - 1)
        
        # Update status
        if self.failure_count == 0:
            self.status = ProviderStatus.HEALTHY
        elif self.failure_count < CIRCUIT_BREAKER_FAILURE_THRESHOLD:
            self.status = ProviderStatus.DEGRADED
    
    def should_attempt_request(self) -> bool:
        """Check if provider should be attempted."""
        if self.status == ProviderStatus.CIRCUIT_OPEN:
            # Check if circuit should be closed
            if time.time() - self.last_failure > CIRCUIT_BREAKER_TIMEOUT_SECONDS:
                self.status = ProviderStatus.DEGRADED
                return True
            return False
        return True
    
    def get_timeout_ms(self) -> int:
        """Get provider-specific timeout."""
        timeout_map = {
            'wiki': WIKIPEDIA_TIMEOUT_MS,
            'stackexchange': STACKEXCHANGE_TIMEOUT_MS,
            'mdn': MDN_TIMEOUT_MS,
            'github': GITHUB_TIMEOUT_MS,
            'openalex': OPENALEX_TIMEOUT_MS,
            'arxiv': ARXIV_TIMEOUT_MS,
            'youtube': YOUTUBE_TIMEOUT_MS,
            'web': PROVIDER_TIMEOUT_MS,  # Web search gets default timeout
            'duckduckgo': DUCKDUCKGO_TIMEOUT_MS
        }
        return timeout_map.get(self.provider, PROVIDER_TIMEOUT_MS)


# Environment variables
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
# Fix Docker hostname issues for local development
if "sarvanom-redis" in REDIS_URL:
    REDIS_URL = "redis://localhost:6379"
CACHE_TTL_MIN = int(os.getenv("CACHE_TTL_MIN", "10"))
CACHE_TTL_MAX = int(os.getenv("CACHE_TTL_MAX", "60"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
BASE_TIMEOUT = int(os.getenv("BASE_TIMEOUT", "2"))
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
        
        # Initialize provider health tracking
        self.provider_health = {
            'wiki': ProviderHealth('wiki'),
            'stackexchange': ProviderHealth('stackexchange'),
            'mdn': ProviderHealth('mdn'),
            'github': ProviderHealth('github'),
            'openalex': ProviderHealth('openalex'),
            'arxiv': ProviderHealth('arxiv'),
            'youtube': ProviderHealth('youtube'),
            'web': ProviderHealth('web'),
            'duckduckgo': ProviderHealth('duckduckgo')
        }
    
    async def setup_redis(self):
        """Setup Redis connection for caching with timeout."""
        if self.redis_client is not None:
            return  # Already initialized
            
        try:
            # Use asyncio.wait_for to prevent blocking on Redis connection
            async def connect_redis():
                client = redis.from_url(REDIS_URL, decode_responses=True)
                await client.ping()
                return client
                
            self.redis_client = await asyncio.wait_for(connect_redis(), timeout=0.5)  # 500ms timeout
            logger.info("✅ Redis connection established for caching")
        except asyncio.TimeoutError:
            logger.warning(f"Redis connection timed out after 500ms. Using in-memory cache.")
            self.redis_client = None
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
    
    def _check_provider_health(self, provider: str) -> bool:
        """Check if provider is healthy enough to attempt request."""
        if provider not in self.provider_health:
            return True  # Unknown provider, allow attempt
        
        health = self.provider_health[provider]
        return health.should_attempt_request()
    
    def _get_provider_timeout(self, provider: str) -> float:
        """Get timeout for specific provider in seconds."""
        if provider not in self.provider_health:
            return PROVIDER_TIMEOUT_MS / 1000
        
        health = self.provider_health[provider]
        return health.get_timeout_ms() / 1000
    
    def _record_provider_success(self, provider: str, response_time: float):
        """Record successful provider request."""
        if provider in self.provider_health:
            self.provider_health[provider].record_success(response_time)
    
    def _record_provider_failure(self, provider: str):
        """Record provider failure."""
        if provider in self.provider_health:
            self.provider_health[provider].record_failure()
    
    def get_provider_health_status(self) -> Dict[str, Dict]:
        """Get current provider health status."""
        return {
            provider: {
                'status': health.status.value,
                'failure_count': health.failure_count,
                'avg_response_time': health.avg_response_time,
                'total_requests': health.total_requests,
                'last_success': health.last_success,
                'last_failure': health.last_failure
            }
            for provider, health in self.provider_health.items()
        }
    
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
    
    async def _make_arxiv_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Make HTTP request to arXiv API and parse XML response."""
        await self.setup_session()
        
        try:
            async with self.session.get(url, params=params, timeout=BASE_TIMEOUT) as response:
                if response.status == 200:
                    xml_text = await response.text()
                    
                    # Parse XML using feedparser (simpler than BeautifulSoup for Atom feeds)
                    try:
                        import feedparser
                        parsed = feedparser.parse(xml_text)
                        
                        # Convert to dict format similar to JSON APIs
                        result = {
                            "feed": {
                                "entry": []
                            }
                        }
                        
                        for entry in parsed.entries:
                            result["feed"]["entry"].append({
                                "title": entry.get("title", ""),
                                "id": entry.get("id", ""),
                                "summary": entry.get("summary", ""),
                                "published": entry.get("published", ""),
                                "updated": entry.get("updated", ""),
                                "author": [{"name": author.get("name", "")} for author in entry.get("authors", [])],
                                "arxiv:primary_category": {"term": entry.get("arxiv_primary_category", {}).get("term", "")}
                            })
                        
                        return result
                        
                    except ImportError:
                        # Fallback: simple XML parsing
                        logger.warning("feedparser not available, skipping arXiv search")
                        return None
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    
        except Exception as e:
            logger.warning(f"arXiv request failed: {e}")
        
        return None
    
    async def wiki_search(self, query: str, k: int = 3) -> List[SearchResult]:
        """Search Wikipedia using MediaWiki API with health checks and timeouts."""
        provider = 'wikipedia'
        
        # Check provider health before attempting
        if not self._check_provider_health(provider):
            logger.warning(f"Wikipedia provider circuit breaker open, skipping request")
            return []
        
        start_time = time.time()
        try:
            # Use OpenSearch API for faster, simpler results
            search_url = "https://en.wikipedia.org/w/api.php"
            search_params = {
                "action": "opensearch",
                "format": "json",
                "search": query,
                "limit": k,
                "namespace": 0,
                "redirects": "resolve"
            }
            
            # Use provider-specific timeout
            timeout = self._get_provider_timeout(provider)
            search_data = await asyncio.wait_for(
                self._make_request_with_retry(search_url, params=search_params),
                timeout=timeout
            )
            
            if not search_data or len(search_data) < 4:
                return []
            
            # OpenSearch returns [query, titles, descriptions, urls]
            titles = search_data[1]
            descriptions = search_data[2] 
            urls = search_data[3]
            
            results = []
            for i, (title, description, url) in enumerate(zip(titles, descriptions, urls)):
                try:
                    result = SearchResult(
                        title=title,
                        url=url,
                        snippet=description[:300] + "..." if description else "Wikipedia article",
                        domain="wikipedia.org",
                        provider=SearchProvider.MEDIAWIKI,
                        metadata={
                            "source": "opensearch_api"
                        }
                    )
                    result.relevance_score = self._calculate_relevance_score(result, query)
                    results.append(result)
                    
                except Exception as e:
                    logger.warning(f"Error processing Wikipedia result: {e}")
                    continue
            
            # Record success
            response_time = time.time() - start_time
            self._record_provider_success(provider, response_time)
            logger.info(f"wiki search returned {len(results)} results")
            
            return results
            
        except asyncio.TimeoutError:
            logger.warning(f"Wikipedia search timeout after {timeout}s")
            self._record_provider_failure(provider)
            return []
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            self._record_provider_failure(provider)
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
                    
                    # Minimal delay for performance
                    await asyncio.sleep(0.01)
                    
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
                    
                    # Minimal delay for performance
                    await asyncio.sleep(0.01)
                    
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
                    
                    # Minimal delay for performance
                    await asyncio.sleep(0.01)
                    
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
                    
                    # Minimal delay for performance
                    await asyncio.sleep(0.01)
                    
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
            
            # arXiv returns XML, not JSON - need special handling
            xml_data = await self._make_arxiv_request(api_url, params=params)
            if not xml_data:
                return []
            
            results = []
            for entry in xml_data.get("feed", {}).get("entry", [])[:k]:
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
                    
                    # Minimal delay for performance
                    await asyncio.sleep(0.01)
                    
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
                    
                    # Minimal delay for performance
                    await asyncio.sleep(0.01)
                    
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
        # Define a global SLA timeout for the entire search method
        GLOBAL_SEARCH_TIMEOUT_MS = int(os.getenv("GLOBAL_SEARCH_TIMEOUT_MS", "2800"))  # 2.8s to leave buffer for orchestrator
        
        start_time = time.time()
        trace_id = str(uuid.uuid4())
        
        logger.info(f"Starting search for query: {query}", extra={
            "query": query,
            "k": k,
            "use_wiki": use_wiki,
            "use_web": use_web,
            "trace_id": trace_id,
            "timeout_ms": GLOBAL_SEARCH_TIMEOUT_MS
        })
        
        # Create a wrapper function for the entire search operation
        async def perform_search():
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
            
            # Perform fresh search with parallel execution
            all_results = []
            providers_used = []
            
            # Create tasks for parallel execution
            tasks = []
            
            # Wikipedia search
            if use_wiki:
                tasks.append(("wiki", self.wiki_search(query, k=min(k, 3))))
            
            # StackExchange search
            tasks.append(("stackexchange", self.stackexchange_search(query, k=min(k, 2))))
            
            # MDN search
            tasks.append(("mdn", self.mdn_search(query, k=min(k, 2))))
            
            # GitHub search
            tasks.append(("github", self.github_search(query, k=min(k, 2))))
            
            # OpenAlex search
            tasks.append(("openalex", self.openalex_search(query, k=min(k, 2))))
            
            # arXiv search
            tasks.append(("arxiv", self.arxiv_search(query, k=min(k, 2))))
            
            # YouTube search
            tasks.append(("youtube", self.youtube_search(query, k=min(k, 2))))
            
            # Web search (fallback) - always include DuckDuckGo for reliability
            if use_web:
                tasks.append(("web", self.free_web_search(query, k=min(k, 3))))
            
            # Always add DuckDuckGo as backup source for reliability
            tasks.append(("duckduckgo", self._duckduckgo_search(query, k=min(k, 2))))
            
            # Filter out unhealthy providers
            healthy_tasks = []
            for task_name, task_func in tasks:
                if self._check_provider_health(task_name):
                    healthy_tasks.append((task_name, task_func))
                else:
                    logger.info(f"Skipping {task_name} due to circuit breaker")
            
            if not healthy_tasks:
                logger.warning("All providers are unhealthy, returning empty results")
                return SearchResponse(
                    results=[],
                    total_results=0,
                    cache_hit=False,
                    processing_time_ms=0,
                    providers_used=[],
                    trace_id=trace_id,
                    error_message="All providers are unhealthy"
                )
            
            # Execute all tasks in parallel with strict timeout
            logger.info(f"Executing {len(healthy_tasks)} healthy search tasks in parallel")
            
            # Execute tasks in parallel with individual timeouts
            async def execute_with_timeout(task_name, task_func):
                try:
                    provider_timeout = self._get_provider_timeout(task_name)
                    logger.info(f"Executing {task_name} with {provider_timeout*1000:.0f}ms timeout")
                    
                    result = await asyncio.wait_for(task_func, timeout=provider_timeout)
                    return result
                    
                except asyncio.TimeoutError:
                    logger.warning(f"{task_name} timed out after {provider_timeout*1000:.0f}ms")
                    self._record_provider_failure(task_name)
                    return []
                except Exception as e:
                    logger.error(f"{task_name} failed: {e}")
                    self._record_provider_failure(task_name)
                    return []
            
            # Execute all tasks in parallel
            tasks_with_timeouts = [
                execute_with_timeout(task_name, task_func) 
                for task_name, task_func in healthy_tasks
            ]
            
            results = await asyncio.gather(*tasks_with_timeouts, return_exceptions=True)
            
            # Handle any exceptions from gather
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Task {healthy_tasks[i][0]} failed with exception: {result}")
                    results[i] = []
            
            # Process results
            process_start = time.time()
            for i, (provider_name, result) in enumerate(zip([task[0] for task in healthy_tasks], results)):
                if isinstance(result, Exception):
                    logger.error(f"{provider_name} search failed: {result}")
                    continue
                
                if result:
                    all_results.extend(result)
                    if provider_name == "wiki":
                        providers_used.append(SearchProvider.MEDIAWIKI)
                    elif provider_name == "stackexchange":
                        providers_used.append(SearchProvider.STACKEXCHANGE)
                    elif provider_name == "mdn":
                        providers_used.append(SearchProvider.MDN)
                    elif provider_name == "github":
                        providers_used.append(SearchProvider.GITHUB)
                    elif provider_name == "openalex":
                        providers_used.append(SearchProvider.OPENALEX)
                    elif provider_name == "arxiv":
                        providers_used.append(SearchProvider.ARXIV)
                    elif provider_name == "youtube":
                        providers_used.append(SearchProvider.YOUTUBE)
                    elif provider_name == "web":
                        providers_used.extend([r.provider for r in result])
                    elif provider_name == "duckduckgo":
                        providers_used.append(SearchProvider.DUCKDUCKGO)
                    
                    logger.info(f"{provider_name} search returned {len(result)} results")
            
            process_time = (time.time() - process_start) * 1000
            logger.info(f"Results processing took {process_time:.2f}ms")
            
            # Deduplicate and rank results
            dedup_start = time.time()
            deduplicated = self._deduplicate_results(all_results)
            dedup_time = (time.time() - dedup_start) * 1000
            logger.info(f"Deduplication took {dedup_time:.2f}ms")
            
            # Sort by relevance score
            sort_start = time.time()
            sorted_results = sorted(deduplicated, key=lambda x: x.relevance_score, reverse=True)
            sort_time = (time.time() - sort_start) * 1000
            logger.info(f"Sorting took {sort_time:.2f}ms")
            
            # Take top k results
            final_results = sorted_results[:k]
            
            # Cache results (non-blocking)
            cache_start = time.time()
            try:
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
                
                # Use asyncio.wait_for to prevent blocking on Redis failures
                await asyncio.wait_for(
                    self._cache_set(cache_key, cache_data, ttl_minutes),
                    timeout=0.5  # 500ms max for caching
                )
                cache_time = (time.time() - cache_start) * 1000
                logger.info(f"Caching took {cache_time:.2f}ms")
                
            except asyncio.TimeoutError:
                cache_time = (time.time() - cache_start) * 1000
                logger.warning(f"Caching timed out after {cache_time:.2f}ms, continuing without cache")
            except Exception as e:
                cache_time = (time.time() - cache_start) * 1000
                logger.warning(f"Caching failed after {cache_time:.2f}ms: {e}, continuing without cache")
            
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
        
        # Execute the search with global timeout
        try:
            # Convert milliseconds to seconds for asyncio.wait_for
            global_timeout = GLOBAL_SEARCH_TIMEOUT_MS / 1000
            logger.info(f"Enforcing global timeout of {global_timeout:.2f}s")
            
            return await asyncio.wait_for(perform_search(), timeout=global_timeout)
            
        except asyncio.TimeoutError:
            # If we hit the global timeout, return partial results
            logger.warning(f"Global search timeout after {GLOBAL_SEARCH_TIMEOUT_MS}ms, returning partial results")
            
            # Return a minimal response with error message
            return SearchResponse(
                query=query,
                results=[],  # Empty results
                total_results=0,
                cache_hit=False,
                providers_used=[],
                processing_time_ms=GLOBAL_SEARCH_TIMEOUT_MS,
                trace_id=trace_id,
                error_message=f"Search timed out after {GLOBAL_SEARCH_TIMEOUT_MS}ms"
            )
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary for monitoring."""
        health_status = self.get_provider_health_status()
        
        # Calculate overall health metrics
        total_providers = len(health_status)
        healthy_providers = sum(1 for h in health_status.values() if h['status'] == 'healthy')
        degraded_providers = sum(1 for h in health_status.values() if h['status'] == 'degraded')
        failing_providers = sum(1 for h in health_status.values() if h['status'] == 'failing')
        circuit_open_providers = sum(1 for h in health_status.values() if h['status'] == 'circuit_open')
        
        # Calculate average response times
        avg_response_times = {}
        for provider, health in health_status.items():
            if health['total_requests'] > 0:
                avg_response_times[provider] = health['avg_response_time']
        
        return {
            'overall_health': {
                'total_providers': total_providers,
                'healthy_providers': healthy_providers,
                'degraded_providers': degraded_providers,
                'failing_providers': failing_providers,
                'circuit_open_providers': circuit_open_providers,
                'health_percentage': (healthy_providers / total_providers * 100) if total_providers > 0 else 0
            },
            'provider_details': health_status,
            'performance_metrics': {
                'avg_response_times': avg_response_times,
                'total_requests': sum(h['total_requests'] for h in health_status.values())
            },
            'timestamp': time.time()
        }


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
