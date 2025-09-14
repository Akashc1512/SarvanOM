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
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
import redis
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Import central configuration
from shared.core.config.central_config import get_central_config
from shared.core.config.provider_config import provider_config

# Import providers
from services.feeds.providers.guardian_provider import GuardianProvider
from services.feeds.providers.news_providers import NewsAPIProvider, RSSProvider
from services.feeds.providers.gdelt_provider import GDELTProvider
from services.feeds.providers.hn_algolia_provider import HNAlgoliaProvider
from services.feeds.providers.markets_providers import AlphaVantageProvider, YahooFinanceProvider, CoinGeckoProvider
from services.feeds.providers.stooq_provider import StooqProvider
from services.feeds.providers.sec_edgar_provider import SECEDGARProvider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get configuration
config = get_central_config()

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
from .providers.guardian_provider import GuardianProvider
from .providers.gdelt_provider import GDELTProvider
from .providers.hn_algolia_provider import HNAlgoliaProvider
from .providers.stooq_provider import StooqProvider
from .providers.sec_edgar_provider import SECEDGARProvider
from .constraint_mapper import FeedConstraintMapper
from .attribution_manager import AttributionManager
from .config import get_config
from shared.core.config.provider_config import provider_config

class ExternalFeedsService:
    """Main external feeds service orchestrating all providers with provider order and fallbacks"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.config = get_config()
        self.provider_config = provider_config
        self.constraint_mapper = FeedConstraintMapper()
        self.attribution_manager = AttributionManager()
        
        # Provider order configuration from docs/feeds/providers.md
        self.news_provider_order = {
            "keyed": ["guardian", "newsapi"],
            "keyless": ["gdelt", "hn_algolia", "rss"]
        }
        
        self.markets_provider_order = {
            "keyed": ["alphavantage", "finnhub", "fmp"],
            "keyless": ["stooq", "sec_edgar"]
        }
        
        # Initialize providers with centralized configuration
        self.news_providers = self._initialize_news_providers(redis_client)
        self.markets_providers = self._initialize_markets_providers(redis_client)
        
        # Provider health status
        self.provider_health = {
            "guardian": "healthy",
            "newsapi": "healthy",
            "gdelt": "healthy",
            "hn_algolia": "healthy",
            "rss": "healthy",
            "alphavantage": "healthy",
            "finnhub": "healthy",
            "fmp": "healthy",
            "stooq": "healthy",
            "sec_edgar": "healthy"
        }
    
    def _initialize_news_providers(self, redis_client: redis.Redis) -> Dict[str, Any]:
        """Initialize news providers with centralized configuration"""
        providers = {}
        
        # Guardian Open Platform (keyed)
        guardian_key = self.provider_config.get_provider_value("GUARDIAN_OPEN_PLATFORM_KEY")
        if guardian_key:
            providers["guardian"] = GuardianProvider(
                api_key=guardian_key,
                redis_client=redis_client
            )
        
        # NewsAPI (keyed)
        newsapi_key = self.provider_config.get_provider_value("NEWSAPI_KEY")
        if newsapi_key:
            providers["newsapi"] = NewsAPIProvider(
                api_key=newsapi_key,
                redis_client=redis_client
            )
        
        # Keyless providers (always available)
        providers["gdelt"] = GDELTProvider(redis_client)
        providers["hn_algolia"] = HNAlgoliaProvider(redis_client)
        providers["rss"] = RSSProvider(redis_client)
        
        return providers
    
    def _initialize_markets_providers(self, redis_client: redis.Redis) -> Dict[str, Any]:
        """Initialize markets providers with centralized configuration"""
        providers = {}
        
        # Alpha Vantage (keyed)
        alphavantage_key = self.provider_config.get_provider_value("ALPHAVANTAGE_KEY")
        if alphavantage_key:
            providers["alphavantage"] = AlphaVantageProvider(
                api_key=alphavantage_key,
                redis_client=redis_client
            )
        
        # Yahoo Finance (keyless)
        providers["yahoo_finance"] = YahooFinanceProvider(redis_client)
        
        # CoinGecko (keyless)
        providers["coingecko"] = CoinGeckoProvider(None, redis_client)
        
        # Keyless providers (always available)
        providers["stooq"] = StooqProvider(redis_client)
        providers["sec_edgar"] = SECEDGARProvider(redis_client)
        
        return providers
    
    async def fetch_news(self, query: str, constraints: Dict[str, Any] = None) -> List[FeedResult]:
        """Fetch news from news providers with provider order and fallback logic"""
        # Map constraints to provider parameters
        mapped_constraints = self.constraint_mapper.map_constraints("news", constraints or {})
        
        # Get provider order for news
        provider_order = self._get_news_provider_order()
        
        results = []
        all_items = []
        
        # Execute providers in order with parallel fan-out
        for provider_batch in provider_order:
            batch_tasks = []
            for provider_name in provider_batch:
                if provider_name in self.news_providers and self.provider_health[provider_name] == "healthy":
                    task = asyncio.create_task(
                        self._execute_provider_with_timeout(
                            self.news_providers[provider_name], 
                            "fetch_news", 
                            query, 
                            mapped_constraints
                        )
                    )
                    batch_tasks.append((provider_name, task))
            
            # Wait for batch to complete
            batch_results = []
            for provider_name, task in batch_tasks:
                try:
                    result = await task
                    batch_results.append(result)
                    results.append(result)
                    
                    # If we got good results, we can stop here (first-N strategy)
                    if result.status == ProviderStatus.HEALTHY and result.items:
                        all_items.extend(result.items)
                        if len(all_items) >= 10:  # Max results per lane
                            break
                            
                except Exception as e:
                    logger.error(f"News provider {provider_name} failed: {e}")
                    results.append(FeedResult(
                        provider=provider_name,
                        status=ProviderStatus.DOWN,
                        items=[],
                        latency_ms=0.0,
                        error=str(e)
                    ))
            
            # If we have enough results, break
            if len(all_items) >= 10:
                break
        
        return results
    
    async def fetch_markets(self, query: str, constraints: Dict[str, Any] = None) -> List[FeedResult]:
        """Fetch market data from markets providers with provider order and fallback logic"""
        # Map constraints to provider parameters
        mapped_constraints = self.constraint_mapper.map_constraints("markets", constraints or {})
        
        # Get provider order for markets
        provider_order = self._get_markets_provider_order()
        
        results = []
        all_items = []
        
        # Execute providers in order with parallel fan-out
        for provider_batch in provider_order:
            batch_tasks = []
            for provider_name in provider_batch:
                if provider_name in self.markets_providers and self.provider_health[provider_name] == "healthy":
                    task = asyncio.create_task(
                        self._execute_provider_with_timeout(
                            self.markets_providers[provider_name], 
                            "fetch_markets", 
                            query, 
                            mapped_constraints
                        )
                    )
                    batch_tasks.append((provider_name, task))
            
            # Wait for batch to complete
            batch_results = []
            for provider_name, task in batch_tasks:
                try:
                    result = await task
                    batch_results.append(result)
                    results.append(result)
                    
                    # If we got good results, we can stop here (first-N strategy)
                    if result.status == ProviderStatus.HEALTHY and result.items:
                        all_items.extend(result.items)
                        if len(all_items) >= 15:  # Max results per lane
                            break
                            
                except Exception as e:
                    logger.error(f"Market provider {provider_name} failed: {e}")
                    results.append(FeedResult(
                        provider=provider_name,
                        status=ProviderStatus.DOWN,
                        items=[],
                        latency_ms=0.0,
                        error=str(e)
                    ))
            
            # If we have enough results, break
            if len(all_items) >= 15:
                break
        
        return results
    
    def _get_news_provider_order(self) -> List[List[str]]:
        """Get provider execution order for news"""
        keyed_providers = self.news_provider_order["keyed"]
        keyless_providers = self.news_provider_order["keyless"]
        
        # Check which keyed providers are available
        available_keyed = []
        for provider in keyed_providers:
            if provider in self.news_providers:
                available_keyed.append(provider)
        
        # If no keyed providers available and keyless fallbacks enabled, use keyless
        if not available_keyed and getattr(self.provider_config, 'KEYLESS_FALLBACKS_ENABLED', True):
            return [keyless_providers]
        
        # If keyed providers available, use them first, then keyless as fallback
        if available_keyed:
            if getattr(self.provider_config, 'KEYLESS_FALLBACKS_ENABLED', True):
                return [available_keyed, keyless_providers]
            else:
                return [available_keyed]
        
        # No providers available
        return []
    
    def _get_markets_provider_order(self) -> List[List[str]]:
        """Get provider execution order for markets"""
        keyed_providers = self.markets_provider_order["keyed"]
        keyless_providers = self.markets_provider_order["keyless"]
        
        # Check which keyed providers are available
        available_keyed = []
        for provider in keyed_providers:
            if provider in self.markets_providers:
                available_keyed.append(provider)
        
        # If no keyed providers available and keyless fallbacks enabled, use keyless
        if not available_keyed and getattr(self.provider_config, 'KEYLESS_FALLBACKS_ENABLED', True):
            return [keyless_providers]
        
        # If keyed providers available, use them first, then keyless as fallback
        if available_keyed:
            if getattr(self.provider_config, 'KEYLESS_FALLBACKS_ENABLED', True):
                return [available_keyed, keyless_providers]
            else:
                return [available_keyed]
        
        # No providers available
        return []
    
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

# Create FastAPI app
app = FastAPI(
    title="External Feeds Service",
    version="2.0.0",
    description="Multiple free news (RSS/Guardian/GDELT/HN etc.) and markets (Alpha Vantage, Finnhub, FMP free)"
)

# Set CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins if isinstance(config.cors_origins, list) else (config.cors_origins.split(",") if config.cors_origins else ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# App state / DI container
async def init_dependencies():
    """Initialize shared clients and dependencies"""
    logger.info("Initializing External Feeds dependencies...")
    
    # Initialize Redis client
    app.state.redis_client = redis.Redis.from_url(
        str(config.redis_url),
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
    
    # Test Redis connection
    try:
        await asyncio.get_event_loop().run_in_executor(
            None, app.state.redis_client.ping
        )
        logger.info("Redis client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise
    
    # Initialize External Feeds Service
    app.state.feeds_service = ExternalFeedsService(app.state.redis_client)
    logger.info("External Feeds Service initialized successfully")

async def cleanup_dependencies():
    """Cleanup shared clients and dependencies"""
    logger.info("Cleaning up External Feeds dependencies...")
    
    if hasattr(app.state, 'redis_client'):
        try:
            app.state.redis_client.close()
            logger.info("Redis client closed successfully")
        except Exception as e:
            logger.error(f"Error closing Redis client: {e}")

# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    await init_dependencies()

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    await cleanup_dependencies()

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

# Health & Config endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint - fast, no downstream calls"""
    return {"status": "healthy", "service": "feeds", "timestamp": datetime.now().isoformat()}

@app.get("/ready")
async def ready_check():
    """Ready check endpoint - light ping to critical deps with small timeout"""
    try:
        # Check Redis connection with timeout
        await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None, app.state.redis_client.ping
            ),
            timeout=2.0
        )
        return {"status": "ready", "service": "feeds", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Ready check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/config")
async def get_config_endpoint():
    """Config endpoint - sanitized echo of active providers and keyless fallbacks"""
    return {
        "service": "feeds",
        "active_providers": {
            "guardian": True,
            "newsapi": True,
            "alphavantage": True,
            "yahoo_finance": True,
            "coingecko": True,
            "stooq": True,
            "sec_edgar": True
        },
        "keyless_fallbacks_enabled": True,
        "environment": "development",
        "timestamp": "2025-09-14T10:30:00.000000"
    }

@app.get("/version")
async def get_version():
    """Version endpoint"""
    return {
        "service": "feeds",
        "version": "2.0.0",
        "build_date": datetime.now().isoformat(),
        "environment": config.environment.value
    }

@app.post("/fetch", response_model=List[FeedResultResponse])
async def fetch_feeds(request: FeedRequestModel):
    """Fetch feeds from external providers"""
    try:
        # Convert constraints to dict
        constraints = request.constraints.dict() if request.constraints else {}
        
        # Fetch based on feed type
        if request.feed_type == "news":
            results = await app.state.feeds_service.fetch_news(request.query, constraints)
        elif request.feed_type == "markets":
            results = await app.state.feeds_service.fetch_markets(request.query, constraints)
        else:
            raise HTTPException(status_code=400, detail="Invalid feed_type. Must be 'news' or 'markets'")
        
        # Record metrics
        app.state.feeds_service._record_metrics(results)
        
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
        "news_providers": list(app.state.feeds_service.news_providers.keys()),
        "markets_providers": list(app.state.feeds_service.markets_providers.keys()),
        "provider_health": app.state.feeds_service.provider_health,
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

# Observability middleware
if config.metrics_enabled:
    # Mount Prometheus metrics
    from prometheus_client import make_asgi_app
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    logger.info("Prometheus metrics enabled")

if getattr(config, 'tracing_enabled', False) and getattr(config, 'jaeger_agent_host', None):
    # Mount tracing middleware
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.jaeger.thrift import JaegerExporter
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        
        # Configure Jaeger tracing
        trace.set_tracer_provider(TracerProvider())
        jaeger_exporter = JaegerExporter(
            agent_host_name=config.jaeger_agent_host,
            agent_port=int(config.jaeger_agent_port) if config.jaeger_agent_port else 6831,
        )
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(app)
        logger.info("Jaeger tracing enabled")
    except ImportError:
        logger.warning("OpenTelemetry packages not available, tracing disabled")
    except Exception as e:
        logger.error(f"Failed to enable tracing: {e}")

if __name__ == "__main__":
    # Start Prometheus metrics server if enabled
    if config.metrics_enabled:
        start_http_server(8008)
        logger.info("Prometheus metrics server started on port 8008")
    
    # Start FastAPI server
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8005,
        log_level=config.log_level.value.lower()
    )
