"""
News Providers - SarvanOM v2 External Feeds

Multiple free news providers: NewsAPI, RSS feeds, Reddit API.
Normalize data to common schema with attribution.
"""

import asyncio
import json
import logging
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import xml.etree.ElementTree as ET

import httpx
import redis

logger = logging.getLogger(__name__)

@dataclass
class NormalizedFeedItem:
    id: str
    title: str
    content: str
    url: str
    source: str
    author: Optional[str] = None
    published_at: datetime = None
    category: Optional[str] = None
    tags: List[str] = None
    language: str = "en"
    provider: str = ""
    attribution: Dict[str, Any] = None
    metadata: Dict[str, Any] = None

@dataclass
class FeedResult:
    provider: str
    status: str
    items: List[NormalizedFeedItem]
    latency_ms: float
    error: Optional[str] = None
    rate_limit_remaining: Optional[int] = None
    cache_hit: bool = False

class NewsAPIProvider:
    """NewsAPI provider for news articles"""
    
    def __init__(self, api_key: str, redis_client: redis.Redis):
        self.api_key = api_key
        self.redis = redis_client
        self.base_url = "https://newsapi.org/v2"
        self.rate_limit = 1000  # requests per day
        self.requests_per_minute = 1
        self.http_client = httpx.AsyncClient()
    
    async def fetch_news(self, query: str, constraints: Dict[str, Any] = None) -> FeedResult:
        """Fetch news from NewsAPI"""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = f"newsapi:{hashlib.md5(query.encode()).hexdigest()}"
            cached_result = await self._get_from_cache(cache_key)
            if cached_result:
                return FeedResult(
                    provider="newsapi",
                    status="healthy",
                    items=cached_result,
                    latency_ms=(time.time() - start_time) * 1000,
                    cache_hit=True
                )
            
            # Build query parameters
            params = {
                "apiKey": self.api_key,
                "q": query,
                "pageSize": 20,
                "sortBy": "publishedAt"
            }
            
            # Apply constraints
            if constraints:
                if constraints.get("language"):
                    params["language"] = constraints["language"]
                if constraints.get("sources"):
                    params["sources"] = ",".join(constraints["sources"])
                if constraints.get("date_range"):
                    start_date, end_date = constraints["date_range"]
                    params["from"] = start_date.strftime("%Y-%m-%d")
                    params["to"] = end_date.strftime("%Y-%m-%d")
            
            # Make API request
            response = await self.http_client.get(
                f"{self.base_url}/everything",
                params=params,
                timeout=0.8  # 800ms timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])
                
                # Normalize articles
                normalized_items = []
                for article in articles:
                    normalized_item = self._normalize_article(article)
                    if normalized_item:
                        normalized_items.append(normalized_item)
                
                # Cache results
                await self._set_cache(cache_key, normalized_items, ttl=300)
                
                return FeedResult(
                    provider="newsapi",
                    status="healthy",
                    items=normalized_items,
                    latency_ms=(time.time() - start_time) * 1000,
                    rate_limit_remaining=data.get("totalResults", 0)
                )
            else:
                return FeedResult(
                    provider="newsapi",
                    status="error",
                    items=[],
                    latency_ms=(time.time() - start_time) * 1000,
                    error=f"API error: {response.status_code}"
                )
                
        except asyncio.TimeoutError:
            return FeedResult(
                provider="newsapi",
                status="timeout",
                items=[],
                latency_ms=(time.time() - start_time) * 1000,
                error="Request timeout"
            )
        except Exception as e:
            return FeedResult(
                provider="newsapi",
                status="error",
                items=[],
                latency_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
    
    def _normalize_article(self, article: Dict[str, Any]) -> Optional[NormalizedFeedItem]:
        """Normalize NewsAPI article to common format"""
        try:
            # Parse published date
            published_at = None
            if article.get("publishedAt"):
                published_at = datetime.fromisoformat(article["publishedAt"].replace("Z", "+00:00"))
            
            return NormalizedFeedItem(
                id=hashlib.md5(article.get("url", "").encode()).hexdigest(),
                title=article.get("title", ""),
                content=article.get("description", ""),
                url=article.get("url", ""),
                source=article.get("source", {}).get("name", "Unknown"),
                author=article.get("author"),
                published_at=published_at,
                category=article.get("category"),
                tags=[],
                language="en",
                provider="newsapi",
                attribution={
                    "source": {
                        "name": article.get("source", {}).get("name", "Unknown"),
                        "url": article.get("url", "")
                    },
                    "article": {
                        "title": article.get("title", ""),
                        "url": article.get("url", ""),
                        "author": article.get("author"),
                        "published_at": article.get("publishedAt")
                    },
                    "license": {
                        "type": "fair_use",
                        "terms": "Used under fair use for news aggregation"
                    }
                },
                metadata={
                    "provider": "newsapi",
                    "raw_data": article
                }
            )
        except Exception as e:
            logger.error(f"Failed to normalize NewsAPI article: {e}")
            return None
    
    async def _get_from_cache(self, key: str) -> Optional[List[NormalizedFeedItem]]:
        """Get result from cache"""
        try:
            cached = self.redis.get(key)
            if cached:
                data = json.loads(cached)
                # Convert back to NormalizedFeedItem objects
                return [NormalizedFeedItem(**item) for item in data]
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    async def _set_cache(self, key: str, value: List[NormalizedFeedItem], ttl: int = 300):
        """Set result in cache"""
        try:
            # Convert to serializable format
            data = [asdict(item) for item in value]
            self.redis.setex(key, ttl, json.dumps(data, default=str))
        except Exception as e:
            logger.error(f"Cache set error: {e}")

class RSSProvider:
    """RSS feeds provider for news articles"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.http_client = httpx.AsyncClient()
        self.feeds = {
            "bbc": "http://feeds.bbci.co.uk/news/rss.xml",
            "reuters": "https://feeds.reuters.com/reuters/topNews",
            "ap": "https://feeds.apnews.com/rss/ap/topnews",
            "techcrunch": "https://techcrunch.com/feed/",
            "wired": "https://www.wired.com/feed/rss"
        }
    
    async def fetch_news(self, query: str, constraints: Dict[str, Any] = None) -> FeedResult:
        """Fetch news from RSS feeds"""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = f"rss:{hashlib.md5(query.encode()).hexdigest()}"
            cached_result = await self._get_from_cache(cache_key)
            if cached_result:
                return FeedResult(
                    provider="rss",
                    status="healthy",
                    items=cached_result,
                    latency_ms=(time.time() - start_time) * 1000,
                    cache_hit=True
                )
            
            # Fetch from multiple RSS feeds in parallel
            tasks = []
            for feed_name, feed_url in self.feeds.items():
                task = asyncio.create_task(self._fetch_rss_feed(feed_name, feed_url))
                tasks.append(task)
            
            # Wait for all feeds to complete
            feed_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            all_items = []
            for result in feed_results:
                if isinstance(result, list):
                    all_items.extend(result)
            
            # Filter by query if provided
            if query:
                filtered_items = []
                query_lower = query.lower()
                for item in all_items:
                    if (query_lower in item.title.lower() or 
                        query_lower in item.content.lower()):
                        filtered_items.append(item)
                all_items = filtered_items
            
            # Cache results
            await self._set_cache(cache_key, all_items, ttl=600)  # 10 minutes cache
            
            return FeedResult(
                provider="rss",
                status="healthy",
                items=all_items,
                latency_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            return FeedResult(
                provider="rss",
                status="error",
                items=[],
                latency_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
    
    async def _fetch_rss_feed(self, feed_name: str, feed_url: str) -> List[NormalizedFeedItem]:
        """Fetch individual RSS feed"""
        try:
            response = await self.http_client.get(feed_url, timeout=0.8)
            if response.status_code == 200:
                return self._parse_rss_feed(response.text, feed_name)
            else:
                logger.error(f"Failed to fetch RSS feed {feed_name}: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_name}: {e}")
            return []
    
    def _parse_rss_feed(self, xml_content: str, feed_name: str) -> List[NormalizedFeedItem]:
        """Parse RSS XML content"""
        try:
            root = ET.fromstring(xml_content)
            items = []
            
            # Handle different RSS formats
            for item in root.findall(".//item"):
                try:
                    title = item.find("title")
                    title_text = title.text if title is not None else ""
                    
                    description = item.find("description")
                    description_text = description.text if description is not None else ""
                    
                    link = item.find("link")
                    link_text = link.text if link is not None else ""
                    
                    pub_date = item.find("pubDate")
                    published_at = None
                    if pub_date is not None and pub_date.text:
                        try:
                            published_at = datetime.strptime(pub_date.text, "%a, %d %b %Y %H:%M:%S %Z")
                        except:
                            try:
                                published_at = datetime.strptime(pub_date.text, "%a, %d %b %Y %H:%M:%S %z")
                            except:
                                pass
                    
                    author = item.find("author")
                    author_text = author.text if author is not None else None
                    
                    if title_text and link_text:
                        normalized_item = NormalizedFeedItem(
                            id=hashlib.md5(link_text.encode()).hexdigest(),
                            title=title_text,
                            content=description_text,
                            url=link_text,
                            source=feed_name.upper(),
                            author=author_text,
                            published_at=published_at,
                            category=None,
                            tags=[],
                            language="en",
                            provider="rss",
                            attribution={
                                "source": {
                                    "name": feed_name.upper(),
                                    "url": link_text
                                },
                                "article": {
                                    "title": title_text,
                                    "url": link_text,
                                    "author": author_text,
                                    "published_at": pub_date.text if pub_date is not None else None
                                },
                                "license": {
                                    "type": "fair_use",
                                    "terms": "Used under fair use for news aggregation"
                                }
                            },
                            metadata={
                                "provider": "rss",
                                "feed_name": feed_name
                            }
                        )
                        items.append(normalized_item)
                except Exception as e:
                    logger.error(f"Error parsing RSS item: {e}")
                    continue
            
            return items
        except Exception as e:
            logger.error(f"Error parsing RSS feed: {e}")
            return []
    
    async def _get_from_cache(self, key: str) -> Optional[List[NormalizedFeedItem]]:
        """Get result from cache"""
        try:
            cached = self.redis.get(key)
            if cached:
                data = json.loads(cached)
                return [NormalizedFeedItem(**item) for item in data]
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    async def _set_cache(self, key: str, value: List[NormalizedFeedItem], ttl: int = 600):
        """Set result in cache"""
        try:
            data = [asdict(item) for item in value]
            self.redis.setex(key, ttl, json.dumps(data, default=str))
        except Exception as e:
            logger.error(f"Cache set error: {e}")

class RedditProvider:
    """Reddit API provider for social news"""
    
    def __init__(self, client_id: str, client_secret: str, redis_client: redis.Redis):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redis = redis_client
        self.base_url = "https://oauth.reddit.com"
        self.auth_url = "https://www.reddit.com/api/v1/access_token"
        self.http_client = httpx.AsyncClient()
        self.access_token = None
        self.token_expires = None
    
    async def fetch_news(self, query: str, constraints: Dict[str, Any] = None) -> FeedResult:
        """Fetch news from Reddit"""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = f"reddit:{hashlib.md5(query.encode()).hexdigest()}"
            cached_result = await self._get_from_cache(cache_key)
            if cached_result:
                return FeedResult(
                    provider="reddit",
                    status="healthy",
                    items=cached_result,
                    latency_ms=(time.time() - start_time) * 1000,
                    cache_hit=True
                )
            
            # Ensure we have a valid access token
            await self._ensure_access_token()
            
            if not self.access_token:
                return FeedResult(
                    provider="reddit",
                    status="error",
                    items=[],
                    latency_ms=(time.time() - start_time) * 1000,
                    error="Failed to authenticate with Reddit"
                )
            
            # Search Reddit posts
            headers = {"Authorization": f"bearer {self.access_token}"}
            
            # Determine subreddits to search
            subreddits = ["news", "worldnews", "technology", "business"]
            if constraints and constraints.get("category"):
                category = constraints["category"].lower()
                if category == "tech":
                    subreddits = ["technology", "programming", "gadgets"]
                elif category == "business":
                    subreddits = ["business", "investing", "economics"]
            
            all_posts = []
            for subreddit in subreddits:
                try:
                    response = await self.http_client.get(
                        f"{self.base_url}/r/{subreddit}/hot",
                        headers=headers,
                        params={"limit": 10, "q": query} if query else {"limit": 10},
                        timeout=0.8
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get("data", {}).get("children", [])
                        all_posts.extend(posts)
                except Exception as e:
                    logger.error(f"Error fetching from r/{subreddit}: {e}")
                    continue
            
            # Normalize posts
            normalized_items = []
            for post in all_posts:
                normalized_item = self._normalize_post(post)
                if normalized_item:
                    normalized_items.append(normalized_item)
            
            # Cache results
            await self._set_cache(cache_key, normalized_items, ttl=300)
            
            return FeedResult(
                provider="reddit",
                status="healthy",
                items=normalized_items,
                latency_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            return FeedResult(
                provider="reddit",
                status="error",
                items=[],
                latency_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
    
    async def _ensure_access_token(self):
        """Ensure we have a valid Reddit access token"""
        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            return
        
        try:
            auth = httpx.BasicAuth(self.client_id, self.client_secret)
            data = {"grant_type": "client_credentials"}
            
            response = await self.http_client.post(
                self.auth_url,
                auth=auth,
                data=data,
                headers={"User-Agent": "SarvanOM/1.0"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires = datetime.now() + timedelta(seconds=expires_in - 60)
            else:
                logger.error(f"Failed to get Reddit access token: {response.status_code}")
                self.access_token = None
        except Exception as e:
            logger.error(f"Error getting Reddit access token: {e}")
            self.access_token = None
    
    def _normalize_post(self, post: Dict[str, Any]) -> Optional[NormalizedFeedItem]:
        """Normalize Reddit post to common format"""
        try:
            post_data = post.get("data", {})
            
            # Parse created date
            created_utc = post_data.get("created_utc")
            published_at = None
            if created_utc:
                published_at = datetime.fromtimestamp(created_utc)
            
            return NormalizedFeedItem(
                id=post_data.get("id", ""),
                title=post_data.get("title", ""),
                content=post_data.get("selftext", ""),
                url=f"https://reddit.com{post_data.get('permalink', '')}",
                source=f"r/{post_data.get('subreddit', '')}",
                author=post_data.get("author"),
                published_at=published_at,
                category=post_data.get("subreddit"),
                tags=[],
                language="en",
                provider="reddit",
                attribution={
                    "source": {
                        "name": f"r/{post_data.get('subreddit', '')}",
                        "url": f"https://reddit.com/r/{post_data.get('subreddit', '')}"
                    },
                    "article": {
                        "title": post_data.get("title", ""),
                        "url": f"https://reddit.com{post_data.get('permalink', '')}",
                        "author": post_data.get("author"),
                        "published_at": published_at.isoformat() if published_at else None
                    },
                    "license": {
                        "type": "fair_use",
                        "terms": "Used under fair use for news aggregation"
                    }
                },
                metadata={
                    "provider": "reddit",
                    "subreddit": post_data.get("subreddit"),
                    "score": post_data.get("score"),
                    "num_comments": post_data.get("num_comments")
                }
            )
        except Exception as e:
            logger.error(f"Failed to normalize Reddit post: {e}")
            return None
    
    async def _get_from_cache(self, key: str) -> Optional[List[NormalizedFeedItem]]:
        """Get result from cache"""
        try:
            cached = self.redis.get(key)
            if cached:
                data = json.loads(cached)
                return [NormalizedFeedItem(**item) for item in data]
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    async def _set_cache(self, key: str, value: List[NormalizedFeedItem], ttl: int = 300):
        """Set result in cache"""
        try:
            data = [asdict(item) for item in value]
            self.redis.setex(key, ttl, json.dumps(data, default=str))
        except Exception as e:
            logger.error(f"Cache set error: {e}")
