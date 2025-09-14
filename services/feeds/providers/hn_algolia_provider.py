#!/usr/bin/env python3
"""
Hacker News Algolia Provider - SarvanOM v2

Implements Hacker News Algolia API integration for news feeds (keyless)
with normalized data schema and proper error handling.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
import structlog

logger = structlog.get_logger(__name__)

class HNAlgoliaProvider:
    """Hacker News Algolia API provider (keyless)"""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.base_url = "https://hn.algolia.com/api/v1"
        self.timeout = 800  # 800ms timeout as per requirements
        
    async def fetch_news(self, query: str, constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fetch news from Hacker News Algolia API"""
        start_time = time.time()
        
        try:
            # Build query parameters
            params = {
                "query": query,
                "hitsPerPage": 10,
                "tags": "story",
                "numericFilters": "points>0"  # Only stories with points
            }
            
            # Apply constraints
            if constraints:
                if constraints.get("date_range"):
                    date_range = constraints["date_range"]
                    if isinstance(date_range, dict):
                        if date_range.get("from"):
                            # Convert to timestamp
                            from_date = datetime.fromisoformat(date_range["from"])
                            params["numericFilters"] += f",created_at_i>{int(from_date.timestamp())}"
                        if date_range.get("to"):
                            to_date = datetime.fromisoformat(date_range["to"])
                            params["numericFilters"] += f",created_at_i<{int(to_date.timestamp())}"
            
            # Make API request
            async with httpx.AsyncClient(timeout=self.timeout / 1000) as client:
                response = await client.get(f"{self.base_url}/search", params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Normalize results
                normalized_items = []
                for item in data.get("hits", []):
                    normalized_item = self._normalize_article(item)
                    if normalized_item:
                        normalized_items.append(normalized_item)
                
                latency_ms = (time.time() - start_time) * 1000
                
                return {
                    "provider": "hn_algolia",
                    "status": "healthy",
                    "items": normalized_items,
                    "latency_ms": latency_ms,
                    "total_results": len(normalized_items),
                    "rate_limit_remaining": None,  # HN Algolia doesn't provide this
                    "cache_hit": False
                }
                
        except httpx.TimeoutException:
            latency_ms = (time.time() - start_time) * 1000
            logger.warning(f"HN Algolia API timeout after {latency_ms}ms")
            return {
                "provider": "hn_algolia",
                "status": "timeout",
                "items": [],
                "latency_ms": latency_ms,
                "error": "API timeout"
            }
            
        except httpx.HTTPStatusError as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"HN Algolia API error: {e.response.status_code}")
            return {
                "provider": "hn_algolia",
                "status": "error",
                "items": [],
                "latency_ms": latency_ms,
                "error": f"HTTP {e.response.status_code}"
            }
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"HN Algolia API failed: {e}")
            return {
                "provider": "hn_algolia",
                "status": "error",
                "items": [],
                "latency_ms": latency_ms,
                "error": str(e)
            }
    
    def _normalize_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize HN article to common schema"""
        try:
            # Extract basic information
            title = article.get("title", "")
            content = article.get("comment_text", "") or article.get("story_text", "")
            url = article.get("url", f"https://news.ycombinator.com/item?id={article.get('objectID', '')}")
            
            # Extract publication date
            created_at = article.get("created_at_i")
            if created_at:
                published_at = datetime.fromtimestamp(created_at)
            else:
                published_at = None
            
            # Extract author
            author = article.get("author", "")
            
            # Extract source information
            source = {
                "name": "Hacker News",
                "domain": "news.ycombinator.com",
                "authority_score": 0.8
            }
            
            # Extract tags
            tags = []
            for tag in article.get("_tags", []):
                if tag not in ["story", "comment", "poll", "pollopt"]:
                    tags.append(tag)
            
            # Extract points and comments count
            points = article.get("points", 0)
            num_comments = article.get("num_comments", 0)
            
            # Generate unique ID
            article_id = f"hn_{article.get('objectID', hash(url))}"
            
            return {
                "id": article_id,
                "title": title,
                "content": content,
                "excerpt": content[:200] + "..." if len(content) > 200 else content,
                "url": url,
                "source": source,
                "author": author,
                "published_at": published_at.isoformat() if published_at else None,
                "language": "en",
                "category": "technology",
                "tags": tags,
                "sentiment": {
                    "score": 0.5,  # Default neutral sentiment
                    "label": "neutral"
                },
                "metadata": {
                    "provider": "hn_algolia",
                    "provider_id": article.get("objectID", ""),
                    "ingested_at": datetime.utcnow().isoformat(),
                    "confidence": 0.85,
                    "points": points,
                    "num_comments": num_comments
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to normalize HN article: {e}")
            return None
