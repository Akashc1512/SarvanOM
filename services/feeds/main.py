"""
External Feeds Service - SarvanOM v2

Multiple free news (RSS/Guardian/GDELT/HN etc.) and markets (Alpha Vantage, Finnhub, FMP free).
Normalize data → common schema; provider ≤800ms time budget, parallel fetch, graceful degradation, cache per TTL.
Map guided chips (region/category/tickers/date range) to provider params.
Attribute sources per policy.
"""

import asyncio
import json
import logging
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import httpx
import redis
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
feed_requests_total = Counter('sarvanom_feed_requests_total', 'Total feed requests', ['provider', 'type', 'status'])
feed_latency = Histogram('sarvanom_feed_latency_seconds', 'Feed latency', ['provider', 'type'])
feed_cache_hit_rate = Gauge('sarvanom_feed_cache_hit_rate', 'Feed cache hit rate', ['provider'])
feed_rate_limit_hits = Counter('sarvanom_feed_rate_limit_hits_total', 'Rate limit hits', ['provider'])

class FeedType(str, Enum):
    NEWS = "news"
    MARKETS = "markets"
    SOCIAL = "social"

class ProviderStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    RATE_LIMITED = "rate_limited"

@dataclass
class FeedConstraint:
    region: Optional[str] = None
    category: Optional[str] = None
    tickers: Optional[List[str]] = None
    date_range: Optional[Tuple[datetime, datetime]] = None
    language: Optional[str] = None
    sources: Optional[List[str]] = None

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
    status: ProviderStatus
    items: List[NormalizedFeedItem]
    latency_ms: float
    error: Optional[str] = None
    rate_limit_remaining: Optional[int] = None
    cache_hit: bool = False

# Import providers and managers
from .providers.news_providers import NewsAPIProvider, RSSProvider, RedditProvider
from .providers.markets_providers import AlphaVantageProvider, YahooFinanceProvider, CoinGeckoProvider
from .constraint_mapper import FeedConstraintMapper
from .attribution_manager import AttributionManager

class ExternalFeedsService:
    """Main external feeds service orchestrating all providers"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.constraint_mapper = FeedConstraintMapper()
        self.attribution_manager = AttributionManager()
        
        # Initialize providers
        self.news_providers = {
            "newsapi": NewsAPIProvider(
                api_key="your_newsapi_key",  # Would come from env
                redis_client=redis_client
            ),
            "rss": RSSProvider(redis_client),
            "reddit": RedditProvider(
                client_id="your_reddit_client_id",  # Would come from env
                client_secret="your_reddit_client_secret",  # Would come from env
                redis_client=redis_client
            )
        }
        
        self.markets_providers = {
            "alphavantage": AlphaVantageProvider(
                api_key="your_alphavantage_key",  # Would come from env
                redis_client=redis_client
            ),
            "yahoo": YahooFinanceProvider(redis_client),
            "coingecko": CoinGeckoProvider(
                api_key="your_coingecko_key",  # Would come from env
                redis_client=redis_client
            )
        }
        
        # Provider health status
        self.provider_health = {
            "newsapi": "healthy",
            "rss": "healthy",
            "reddit": "healthy",
            "alphavantage": "healthy",
            "yahoo": "healthy",
            "coingecko": "healthy"
        }
    
    async def fetch_news(self, query: str, constraints: Dict[str, Any] = None) -> List[FeedResult]:
        """Fetch news from all news providers"""
        # Map constraints to provider parameters
        mapped_constraints = self.constraint_mapper.map_constraints("news", constraints or {})
        
        # Execute all news providers in parallel
        tasks = []
        for provider_name, provider in self.news_providers.items():
            if self.provider_health[provider_name] == "healthy":
                task = asyncio.create_task(
                    self._execute_provider_with_timeout(provider, "fetch_news", query, mapped_constraints)
                )
                tasks.append((provider_name, task))
        
        # Wait for all providers to complete
        results = []
        for provider_name, task in tasks:
            try:
                result = await task
                results.append(result)
            except Exception as e:
                logger.error(f"News provider {provider_name} failed: {e}")
                results.append(FeedResult(
                    provider=provider_name,
                    status="error",
                    items=[],
                    latency_ms=0.0,
                    error=str(e)
                ))
        
        return results
    
    async def fetch_markets(self, query: str, constraints: Dict[str, Any] = None) -> List[FeedResult]:
        """Fetch market data from all market providers"""
        # Map constraints to provider parameters
        mapped_constraints = self.constraint_mapper.map_constraints("markets", constraints or {})
        
        # Execute all market providers in parallel
        tasks = []
        for provider_name, provider in self.markets_providers.items():
            if self.provider_health[provider_name] == "healthy":
                task = asyncio.create_task(
                    self._execute_provider_with_timeout(provider, "fetch_markets", query, mapped_constraints)
                )
                tasks.append((provider_name, task))
        
        # Wait for all providers to complete
        results = []
        for provider_name, task in tasks:
            try:
                result = await task
                results.append(result)
            except Exception as e:
                logger.error(f"Market provider {provider_name} failed: {e}")
                results.append(FeedResult(
                    provider=provider_name,
                    status="error",
                    items=[],
                    latency_ms=0.0,
                    error=str(e)
                ))
        
        return results
    
    async def _execute_provider_with_timeout(self, provider, method_name: str, query: str, constraints: Dict[str, Any]) -> FeedResult:
        """Execute provider method with timeout"""
        try:
            method = getattr(provider, method_name)
            return await asyncio.wait_for(
                method(query, constraints),
                timeout=0.8  # 800ms timeout
            )
        except asyncio.TimeoutError:
            return FeedResult(
                provider=provider.__class__.__name__.lower().replace('provider', ''),
                status="timeout",
                items=[],
                latency_ms=0.0,
                error="Provider exceeded 800ms timeout"
            )
    
    def _record_metrics(self, results: List[FeedResult]):
        """Record metrics for monitoring"""
        for result in results:
            feed_requests_total.labels(
                provider=result.provider,
                type="news" if "news" in result.provider else "markets",
                status=result.status
            ).inc()
            
            feed_latency.labels(
                provider=result.provider,
                type="news" if "news" in result.provider else "markets"
            ).observe(result.latency_ms / 1000.0)
            
            if result.cache_hit:
                feed_cache_hit_rate.labels(provider=result.provider).set(1.0)
            else:
                feed_cache_hit_rate.labels(provider=result.provider).set(0.0)

# FastAPI app
app = FastAPI(title="External Feeds Service", version="2.0.0")

# Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# External feeds service instance
feeds_service = ExternalFeedsService(redis_client)

# Pydantic models for API
class FeedConstraintRequest(BaseModel):
    region: Optional[str] = None
    category: Optional[str] = None
    tickers: Optional[List[str]] = None
    date_range: Optional[Tuple[datetime, datetime]] = None
    language: Optional[str] = None
    sources: Optional[List[str]] = None

class FeedRequestModel(BaseModel):
    query: str
    feed_type: str  # "news" or "markets"
    constraints: Optional[FeedConstraintRequest] = None
    user_id: str
    session_id: str
    trace_id: str

class FeedResultResponse(BaseModel):
    provider: str
    status: str
    items: List[Dict[str, Any]]
    latency_ms: float
    error: Optional[str] = None
    rate_limit_remaining: Optional[int] = None
    cache_hit: bool = False

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "feeds"}

@app.post("/fetch", response_model=List[FeedResultResponse])
async def fetch_feeds(request: FeedRequestModel):
    """Fetch feeds from external providers"""
    try:
        # Convert constraints to dict
        constraints = request.constraints.dict() if request.constraints else {}
        
        # Fetch based on feed type
        if request.feed_type == "news":
            results = await feeds_service.fetch_news(request.query, constraints)
        elif request.feed_type == "markets":
            results = await feeds_service.fetch_markets(request.query, constraints)
        else:
            raise HTTPException(status_code=400, detail="Invalid feed_type. Must be 'news' or 'markets'")
        
        # Record metrics
        feeds_service._record_metrics(results)
        
        # Convert to response format
        response_results = []
        for result in results:
            response_results.append(FeedResultResponse(
                provider=result.provider,
                status=result.status,
                items=[asdict(item) for item in result.items],
                latency_ms=result.latency_ms,
                error=result.error,
                rate_limit_remaining=result.rate_limit_remaining,
                cache_hit=result.cache_hit
            ))
        
        return response_results
        
    except Exception as e:
        logger.error(f"Feed fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/providers")
async def get_provider_status():
    """Get status of all feed providers"""
    return {
        "news_providers": list(feeds_service.news_providers.keys()),
        "markets_providers": list(feeds_service.markets_providers.keys()),
        "provider_health": feeds_service.provider_health,
        "status": "healthy"
    }

@app.get("/constraints")
async def get_supported_constraints():
    """Get supported constraint types"""
    return {
        "news": {
            "region": ["US", "UK", "Europe", "Asia", "Global"],
            "category": ["Technology", "Business", "Science", "Health", "Sports", "Politics"],
            "language": ["English", "Spanish", "French", "German", "Chinese", "Japanese"],
            "date_range": ["Last 24 hours", "Last 7 days", "Last 30 days", "Last 3 months"],
            "sources": ["Custom source list"]
        },
        "markets": {
            "tickers": ["Custom ticker list"],
            "date_range": ["1 day", "1 week", "1 month", "3 months", "1 year"],
            "interval": ["1 minute", "5 minutes", "15 minutes", "1 hour", "1 day", "1 week", "1 month"],
            "indicators": ["SMA", "EMA", "RSI", "MACD", "Bollinger Bands", "Volume"],
            "region": ["US Markets", "European Markets", "Asian Markets", "Global Markets"]
        }
    }

if __name__ == "__main__":
    # Start Prometheus metrics server
    start_http_server(8006)
    
    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8005)
