#!/usr/bin/env python3
"""
Guardian Open Platform Provider - SarvanOM v2

Implements Guardian Open Platform API integration for news feeds
with normalized data schema and proper error handling.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
import structlog

logger = structlog.get_logger(__name__)

class GuardianProvider:
    """Guardian Open Platform API provider"""
    
    def __init__(self, api_key: str, redis_client=None):
        self.api_key = api_key
        self.redis = redis_client
        self.base_url = "https://content.guardianapis.com"
        self.timeout = 800  # 800ms timeout as per requirements
        
    async def fetch_news(self, query: str, constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fetch news from Guardian Open Platform"""
        start_time = time.time()
        
        try:
            # Build query parameters
            params = {
                "api-key": self.api_key,
                "q": query,
                "show-fields": "headline,trailText,body,thumbnail,byline,publication",
                "show-tags": "all",
                "page-size": 10,
                "order-by": "relevance"
            }
            
            # Apply constraints
            if constraints:
                if constraints.get("date_range"):
                    date_range = constraints["date_range"]
                    if isinstance(date_range, dict):
                        if date_range.get("from"):
                            params["from-date"] = date_range["from"]
                        if date_range.get("to"):
                            params["to-date"] = date_range["to"]
                
                if constraints.get("category"):
                    params["section"] = constraints["category"]
                
                if constraints.get("language"):
                    params["lang"] = constraints["language"]
            
            # Make API request
            async with httpx.AsyncClient(timeout=self.timeout / 1000) as client:
                response = await client.get(f"{self.base_url}/search", params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Normalize results
                normalized_items = []
                for item in data.get("response", {}).get("results", []):
                    normalized_item = self._normalize_article(item)
                    if normalized_item:
                        normalized_items.append(normalized_item)
                
                latency_ms = (time.time() - start_time) * 1000
                
                return {
                    "provider": "guardian",
                    "status": "healthy",
                    "items": normalized_items,
                    "latency_ms": latency_ms,
                    "total_results": len(normalized_items),
                    "rate_limit_remaining": None,  # Guardian doesn't provide this
                    "cache_hit": False
                }
                
        except httpx.TimeoutException:
            latency_ms = (time.time() - start_time) * 1000
            logger.warning(f"Guardian API timeout after {latency_ms}ms")
            return {
                "provider": "guardian",
                "status": "timeout",
                "items": [],
                "latency_ms": latency_ms,
                "error": "API timeout"
            }
            
        except httpx.HTTPStatusError as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Guardian API error: {e.response.status_code}")
            return {
                "provider": "guardian",
                "status": "error",
                "items": [],
                "latency_ms": latency_ms,
                "error": f"HTTP {e.response.status_code}"
            }
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Guardian API failed: {e}")
            return {
                "provider": "guardian",
                "status": "error",
                "items": [],
                "latency_ms": latency_ms,
                "error": str(e)
            }
    
    def _normalize_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize Guardian article to common schema"""
        try:
            fields = article.get("fields", {})
            
            # Extract basic information
            title = fields.get("headline", article.get("webTitle", ""))
            content = fields.get("body", "")
            excerpt = fields.get("trailText", "")
            url = article.get("webUrl", "")
            author = fields.get("byline", "")
            
            # Extract publication date
            published_at = article.get("webPublicationDate")
            if published_at:
                try:
                    published_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                except:
                    published_at = None
            
            # Extract tags
            tags = []
            for tag in article.get("tags", []):
                if tag.get("type") == "keyword":
                    tags.append(tag.get("webTitle", ""))
            
            # Extract category
            category = article.get("sectionName", "")
            
            # Extract source information
            source = {
                "name": "The Guardian",
                "domain": "theguardian.com",
                "authority_score": 0.9
            }
            
            # Generate unique ID
            article_id = f"guardian_{article.get('id', hash(url))}"
            
            return {
                "id": article_id,
                "title": title,
                "content": content,
                "excerpt": excerpt,
                "url": url,
                "source": source,
                "author": author,
                "published_at": published_at.isoformat() if published_at else None,
                "language": "en",
                "category": category,
                "tags": tags,
                "sentiment": {
                    "score": 0.5,  # Default neutral sentiment
                    "label": "neutral"
                },
                "metadata": {
                    "provider": "guardian",
                    "provider_id": article.get("id", ""),
                    "ingested_at": datetime.utcnow().isoformat(),
                    "confidence": 0.95
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to normalize Guardian article: {e}")
            return None
