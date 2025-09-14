#!/usr/bin/env python3
"""
GDELT Provider - SarvanOM v2

Implements GDELT 2.1 API integration for news feeds (keyless)
with normalized data schema and proper error handling.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
import structlog

logger = structlog.get_logger(__name__)

class GDELTProvider:
    """GDELT 2.1 API provider (keyless)"""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.base_url = "https://api.gdeltproject.org/api/v2"
        self.timeout = 800  # 800ms timeout as per requirements
        
    async def fetch_news(self, query: str, constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fetch news from GDELT 2.1 API"""
        start_time = time.time()
        
        try:
            # Build query parameters
            params = {
                "query": query,
                "mode": "artlist",
                "maxrecords": 10,
                "format": "json"
            }
            
            # Apply constraints
            if constraints:
                if constraints.get("date_range"):
                    date_range = constraints["date_range"]
                    if isinstance(date_range, dict):
                        if date_range.get("from"):
                            params["startdatetime"] = date_range["from"]
                        if date_range.get("to"):
                            params["enddatetime"] = date_range["to"]
                
                if constraints.get("language"):
                    params["lang"] = constraints["language"]
            
            # Make API request
            async with httpx.AsyncClient(timeout=self.timeout / 1000) as client:
                response = await client.get(f"{self.base_url}/doc/doc", params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Normalize results
                normalized_items = []
                for item in data.get("articles", []):
                    normalized_item = self._normalize_article(item)
                    if normalized_item:
                        normalized_items.append(normalized_item)
                
                latency_ms = (time.time() - start_time) * 1000
                
                return {
                    "provider": "gdelt",
                    "status": "healthy",
                    "items": normalized_items,
                    "latency_ms": latency_ms,
                    "total_results": len(normalized_items),
                    "rate_limit_remaining": None,  # GDELT doesn't provide this
                    "cache_hit": False
                }
                
        except httpx.TimeoutException:
            latency_ms = (time.time() - start_time) * 1000
            logger.warning(f"GDELT API timeout after {latency_ms}ms")
            return {
                "provider": "gdelt",
                "status": "timeout",
                "items": [],
                "latency_ms": latency_ms,
                "error": "API timeout"
            }
            
        except httpx.HTTPStatusError as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"GDELT API error: {e.response.status_code}")
            return {
                "provider": "gdelt",
                "status": "error",
                "items": [],
                "latency_ms": latency_ms,
                "error": f"HTTP {e.response.status_code}"
            }
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"GDELT API failed: {e}")
            return {
                "provider": "gdelt",
                "status": "error",
                "items": [],
                "latency_ms": latency_ms,
                "error": str(e)
            }
    
    def _normalize_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize GDELT article to common schema"""
        try:
            # Extract basic information
            title = article.get("title", "")
            content = article.get("seendate", "")  # GDELT doesn't provide full content
            url = article.get("url", "")
            
            # Extract publication date
            published_at = article.get("seendate")
            if published_at:
                try:
                    published_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                except:
                    published_at = None
            
            # Extract source information
            source_domain = article.get("domain", "")
            source = {
                "name": source_domain,
                "domain": source_domain,
                "authority_score": 0.7  # Default score for GDELT sources
            }
            
            # Extract language
            language = article.get("lang", "en")
            
            # Extract country
            country = article.get("country", "")
            
            # Generate unique ID
            article_id = f"gdelt_{hash(url)}"
            
            return {
                "id": article_id,
                "title": title,
                "content": content,
                "excerpt": content[:200] + "..." if len(content) > 200 else content,
                "url": url,
                "source": source,
                "author": None,
                "published_at": published_at.isoformat() if published_at else None,
                "language": language,
                "category": "general",
                "tags": [country] if country else [],
                "sentiment": {
                    "score": 0.5,  # Default neutral sentiment
                    "label": "neutral"
                },
                "metadata": {
                    "provider": "gdelt",
                    "provider_id": article_id,
                    "ingested_at": datetime.utcnow().isoformat(),
                    "confidence": 0.8
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to normalize GDELT article: {e}")
            return None
