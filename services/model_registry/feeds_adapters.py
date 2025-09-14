"""
Feeds Adapters - SarvanOM v2 Model Registry

News and markets adapters with normalized schemas and parallel fan-out.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import httpx
import redis

from .feeds_models import (
    NormalizedNewsItem, NormalizedMarketsItem, ProviderResult, 
    SourceInfo, SentimentInfo, NewsMetadata, PriceInfo, ChangeInfo, MarketsMetadata
)

logger = logging.getLogger(__name__)

class NewsAdapter:
    """News adapter with multiple providers and normalized schema"""
    
    def __init__(self, config, redis_client: Optional[redis.Redis] = None):
        self.config = config
        self.redis_client = redis_client
        self.providers = self._initialize_providers()
    
    def _initialize_providers(self) -> Dict[str, Dict[str, Any]]:
        """Initialize available news providers based on config"""
        providers = {}
        
        # NewsAPI provider
        if hasattr(self.config, 'newsapi_key') and self.config.newsapi_key:
            providers['newsapi'] = {
                'enabled': True,
                'key': self.config.newsapi_key,
                'base_url': 'https://newsapi.org/v2',
                'keyless': False
            }
        else:
            providers['newsapi'] = {
                'enabled': True,
                'key': None,
                'base_url': 'https://newsapi.org/v2',
                'keyless': True  # Free tier available
            }
        
        # RSS provider (always available)
        providers['rss'] = {
            'enabled': True,
            'key': None,
            'base_url': None,
            'keyless': True
        }
        
        # Reddit provider
        if hasattr(self.config, 'reddit_client_id') and self.config.reddit_client_id:
            providers['reddit'] = {
                'enabled': True,
                'client_id': self.config.reddit_client_id,
                'client_secret': getattr(self.config, 'reddit_client_secret', ''),
                'base_url': 'https://oauth.reddit.com',
                'keyless': False
            }
        else:
            providers['reddit'] = {
                'enabled': True,
                'key': None,
                'base_url': 'https://www.reddit.com',
                'keyless': True  # Public API available
            }
        
        return providers
    
    async def fetch_news(self, query: str, max_items: int = 50, timeout_ms: int = 800) -> List[ProviderResult]:
        """Fetch news from all enabled providers in parallel"""
        tasks = []
        
        for provider_name, provider_config in self.providers.items():
            if provider_config['enabled']:
                task = self._fetch_from_provider(provider_name, provider_config, query, max_items, timeout_ms)
                tasks.append(task)
        
        # Execute all providers in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                provider_name = list(self.providers.keys())[i]
                processed_results.append(ProviderResult(
                    provider=provider_name,
                    status="error",
                    items=[],
                    latency_ms=timeout_ms,
                    error=str(result),
                    keyless=True
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _fetch_from_provider(self, provider_name: str, provider_config: Dict[str, Any], 
                                 query: str, max_items: int, timeout_ms: int) -> ProviderResult:
        """Fetch news from a specific provider"""
        start_time = time.time()
        
        try:
            if provider_name == 'newsapi':
                return await self._fetch_newsapi(provider_config, query, max_items, timeout_ms)
            elif provider_name == 'rss':
                return await self._fetch_rss(provider_config, query, max_items, timeout_ms)
            elif provider_name == 'reddit':
                return await self._fetch_reddit(provider_config, query, max_items, timeout_ms)
            else:
                raise ValueError(f"Unknown provider: {provider_name}")
                
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return ProviderResult(
                provider=provider_name,
                status="error",
                items=[],
                latency_ms=latency,
                error=str(e),
                keyless=provider_config.get('keyless', True)
            )
    
    async def _fetch_newsapi(self, config: Dict[str, Any], query: str, max_items: int, timeout_ms: int) -> ProviderResult:
        """Fetch from NewsAPI"""
        start_time = time.time()
        
        # Check cache first
        cache_key = f"newsapi:{query}:{max_items}"
        if self.redis_client:
            try:
                cached = self.redis_client.get(cache_key)
                if cached:
                    data = json.loads(cached)
                    return ProviderResult(
                        provider="newsapi",
                        status="success",
                        items=[NormalizedNewsItem(**item) for item in data['items']],
                        latency_ms=(time.time() - start_time) * 1000,
                        cache_hit=True,
                        keyless=config.get('keyless', False)
                    )
            except Exception:
                pass
        
        # Make API request
        async with httpx.AsyncClient(timeout=timeout_ms/1000.0) as client:
            params = {
                'q': query,
                'pageSize': min(max_items, 100),
                'sortBy': 'publishedAt',
                'language': 'en'
            }
            
            if config['key']:
                params['apiKey'] = config['key']
                headers = {}
            else:
                # Use free tier
                headers = {'X-API-Key': 'demo'}  # Demo key for testing
            
            response = await client.get(f"{config['base_url']}/everything", params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                # Normalize articles
                normalized_items = []
                for article in articles[:max_items]:
                    try:
                        normalized_item = NormalizedNewsItem(
                            id=f"newsapi_{hash(article.get('url', ''))}",
                            title=article.get('title', ''),
                            content=article.get('content', ''),
                            excerpt=article.get('description', ''),
                            url=article.get('url', ''),
                            source=SourceInfo(
                                name=article.get('source', {}).get('name', 'Unknown'),
                                domain=article.get('url', '').split('/')[2] if article.get('url') else 'unknown.com',
                                authority_score=0.8
                            ),
                            author=article.get('author'),
                            published_at=datetime.fromisoformat(article.get('publishedAt', '').replace('Z', '+00:00')),
                            category="general",
                            tags=[],
                            sentiment=SentimentInfo(score=0.0, label="neutral"),
                            metadata=NewsMetadata(
                                provider="newsapi",
                                provider_id=article.get('url', ''),
                                ingested_at=datetime.now(),
                                confidence=0.9
                            )
                        )
                        normalized_items.append(normalized_item)
                    except Exception as e:
                        logger.warning(f"Failed to normalize NewsAPI article: {e}")
                        continue
                
                # Cache result
                if self.redis_client and normalized_items:
                    try:
                        cache_data = {
                            'items': [item.dict() for item in normalized_items],
                            'timestamp': datetime.now().isoformat()
                        }
                        self.redis_client.setex(cache_key, 300, json.dumps(cache_data, default=str))  # 5 min cache
                    except Exception:
                        pass
                
                return ProviderResult(
                    provider="newsapi",
                    status="success",
                    items=normalized_items,
                    latency_ms=(time.time() - start_time) * 1000,
                    rate_limit_remaining=data.get('totalResults', 0),
                    keyless=config.get('keyless', False)
                )
            else:
                raise Exception(f"NewsAPI error: {response.status_code} - {response.text}")
    
    async def _fetch_rss(self, config: Dict[str, Any], query: str, max_items: int, timeout_ms: int) -> ProviderResult:
        """Fetch from RSS feeds (mock implementation)"""
        start_time = time.time()
        
        # Mock RSS data
        normalized_items = []
        for i in range(min(max_items, 10)):
            normalized_item = NormalizedNewsItem(
                id=f"rss_{i}",
                title=f"RSS Article {i+1} about {query}",
                content=f"This is RSS content about {query}. Article {i+1} provides insights and analysis.",
                excerpt=f"RSS excerpt about {query} - Article {i+1}",
                url=f"https://rss-feed.com/article/{i+1}",
                source=SourceInfo(
                    name="RSS Feed",
                    domain="rss-feed.com",
                    authority_score=0.7
                ),
                author=f"RSS Author {i+1}",
                published_at=datetime.now() - timedelta(hours=i),
                category="general",
                tags=[query, "rss"],
                sentiment=SentimentInfo(score=0.1, label="positive"),
                metadata=NewsMetadata(
                    provider="rss",
                    provider_id=f"rss_{i}",
                    ingested_at=datetime.now(),
                    confidence=0.8
                )
            )
            normalized_items.append(normalized_item)
        
        return ProviderResult(
            provider="rss",
            status="success",
            items=normalized_items,
            latency_ms=(time.time() - start_time) * 1000,
            keyless=True
        )
    
    async def _fetch_reddit(self, config: Dict[str, Any], query: str, max_items: int, timeout_ms: int) -> ProviderResult:
        """Fetch from Reddit (mock implementation)"""
        start_time = time.time()
        
        # Mock Reddit data
        normalized_items = []
        for i in range(min(max_items, 15)):
            normalized_item = NormalizedNewsItem(
                id=f"reddit_{i}",
                title=f"Reddit Post {i+1}: {query}",
                content=f"Reddit discussion about {query}. Post {i+1} contains user insights and community discussion.",
                excerpt=f"Reddit post about {query} - {i+1}",
                url=f"https://reddit.com/r/news/comments/{i+1}",
                source=SourceInfo(
                    name="Reddit",
                    domain="reddit.com",
                    authority_score=0.6
                ),
                author=f"reddit_user_{i+1}",
                published_at=datetime.now() - timedelta(hours=i*2),
                category="discussion",
                tags=[query, "reddit", "community"],
                sentiment=SentimentInfo(score=-0.1, label="neutral"),
                metadata=NewsMetadata(
                    provider="reddit",
                    provider_id=f"reddit_{i}",
                    ingested_at=datetime.now(),
                    confidence=0.7
                )
            )
            normalized_items.append(normalized_item)
        
        return ProviderResult(
            provider="reddit",
            status="success",
            items=normalized_items,
            latency_ms=(time.time() - start_time) * 1000,
            keyless=config.get('keyless', True)
        )

class MarketsAdapter:
    """Markets adapter with multiple providers and normalized schema"""
    
    def __init__(self, config, redis_client: Optional[redis.Redis] = None):
        self.config = config
        self.redis_client = redis_client
        self.providers = self._initialize_providers()
    
    def _initialize_providers(self) -> Dict[str, Dict[str, Any]]:
        """Initialize available markets providers based on config"""
        providers = {}
        
        # Alpha Vantage provider
        if hasattr(self.config, 'alpha_vantage_key') and self.config.alpha_vantage_key:
            providers['alphavantage'] = {
                'enabled': True,
                'key': self.config.alpha_vantage_key,
                'base_url': 'https://www.alphavantage.co/query',
                'keyless': False
            }
        else:
            providers['alphavantage'] = {
                'enabled': True,
                'key': None,
                'base_url': 'https://www.alphavantage.co/query',
                'keyless': True  # Free tier available
            }
        
        # Yahoo Finance provider (always available)
        providers['yahoo'] = {
            'enabled': True,
            'key': None,
            'base_url': 'https://query1.finance.yahoo.com',
            'keyless': True
        }
        
        # CoinGecko provider (always available)
        providers['coingecko'] = {
            'enabled': True,
            'key': None,
            'base_url': 'https://api.coingecko.com/api/v3',
            'keyless': True
        }
        
        return providers
    
    async def fetch_markets(self, query: str, max_items: int = 50, timeout_ms: int = 800) -> List[ProviderResult]:
        """Fetch markets data from all enabled providers in parallel"""
        tasks = []
        
        for provider_name, provider_config in self.providers.items():
            if provider_config['enabled']:
                task = self._fetch_from_provider(provider_name, provider_config, query, max_items, timeout_ms)
                tasks.append(task)
        
        # Execute all providers in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                provider_name = list(self.providers.keys())[i]
                processed_results.append(ProviderResult(
                    provider=provider_name,
                    status="error",
                    items=[],
                    latency_ms=timeout_ms,
                    error=str(result),
                    keyless=True
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _fetch_from_provider(self, provider_name: str, provider_config: Dict[str, Any], 
                                 query: str, max_items: int, timeout_ms: int) -> ProviderResult:
        """Fetch markets data from a specific provider"""
        start_time = time.time()
        
        try:
            if provider_name == 'alphavantage':
                return await self._fetch_alphavantage(provider_config, query, max_items, timeout_ms)
            elif provider_name == 'yahoo':
                return await self._fetch_yahoo(provider_config, query, max_items, timeout_ms)
            elif provider_name == 'coingecko':
                return await self._fetch_coingecko(provider_config, query, max_items, timeout_ms)
            else:
                raise ValueError(f"Unknown provider: {provider_name}")
                
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return ProviderResult(
                provider=provider_name,
                status="error",
                items=[],
                latency_ms=latency,
                error=str(e),
                keyless=provider_config.get('keyless', True)
            )
    
    async def _fetch_alphavantage(self, config: Dict[str, Any], query: str, max_items: int, timeout_ms: int) -> ProviderResult:
        """Fetch from Alpha Vantage"""
        start_time = time.time()
        
        # Check cache first
        cache_key = f"alphavantage:{query}:{max_items}"
        if self.redis_client:
            try:
                cached = self.redis_client.get(cache_key)
                if cached:
                    data = json.loads(cached)
                    return ProviderResult(
                        provider="alphavantage",
                        status="success",
                        items=[NormalizedMarketsItem(**item) for item in data['items']],
                        latency_ms=(time.time() - start_time) * 1000,
                        cache_hit=True,
                        keyless=config.get('keyless', False)
                    )
            except Exception:
                pass
        
        # Mock Alpha Vantage data
        normalized_items = []
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
        
        for i, symbol in enumerate(symbols[:max_items]):
            if query.lower() in symbol.lower() or query.lower() in ['stock', 'equity', 'market']:
                normalized_item = NormalizedMarketsItem(
                    id=f"alphavantage_{symbol}",
                    symbol=symbol,
                    name=f"{symbol} Company",
                    type="stock",
                    price=PriceInfo(
                        current=150.0 + i * 10,
                        open=149.0 + i * 10,
                        high=152.0 + i * 10,
                        low=148.0 + i * 10,
                        previous_close=149.5 + i * 10
                    ),
                    change=ChangeInfo(
                        absolute=0.5 + i * 0.1,
                        percentage=0.33 + i * 0.05
                    ),
                    volume=50000000 + i * 1000000,
                    market_cap=2500000000000 + i * 100000000000,
                    currency="USD",
                    exchange="NASDAQ",
                    sector="Technology",
                    industry="Software",
                    timestamp=datetime.now(),
                    metadata=MarketsMetadata(
                        provider="alphavantage",
                        provider_id=symbol,
                        ingested_at=datetime.now(),
                        confidence=0.95
                    )
                )
                normalized_items.append(normalized_item)
        
        # Cache result
        if self.redis_client and normalized_items:
            try:
                cache_data = {
                    'items': [item.dict() for item in normalized_items],
                    'timestamp': datetime.now().isoformat()
                }
                self.redis_client.setex(cache_key, 60, json.dumps(cache_data, default=str))  # 1 min cache
            except Exception:
                pass
        
        return ProviderResult(
            provider="alphavantage",
            status="success",
            items=normalized_items,
            latency_ms=(time.time() - start_time) * 1000,
            keyless=config.get('keyless', False)
        )
    
    async def _fetch_yahoo(self, config: Dict[str, Any], query: str, max_items: int, timeout_ms: int) -> ProviderResult:
        """Fetch from Yahoo Finance (mock implementation)"""
        start_time = time.time()
        
        # Mock Yahoo Finance data
        normalized_items = []
        symbols = ['SPY', 'QQQ', 'IWM', 'VTI', 'VEA']
        
        for i, symbol in enumerate(symbols[:max_items]):
            if query.lower() in symbol.lower() or query.lower() in ['etf', 'fund', 'index']:
                normalized_item = NormalizedMarketsItem(
                    id=f"yahoo_{symbol}",
                    symbol=symbol,
                    name=f"{symbol} ETF",
                    type="etf",
                    price=PriceInfo(
                        current=400.0 + i * 20,
                        open=399.0 + i * 20,
                        high=402.0 + i * 20,
                        low=398.0 + i * 20,
                        previous_close=399.5 + i * 20
                    ),
                    change=ChangeInfo(
                        absolute=0.5 + i * 0.2,
                        percentage=0.12 + i * 0.03
                    ),
                    volume=100000000 + i * 5000000,
                    market_cap=None,
                    currency="USD",
                    exchange="NYSE",
                    sector="Financial",
                    industry="ETF",
                    timestamp=datetime.now(),
                    metadata=MarketsMetadata(
                        provider="yahoo",
                        provider_id=symbol,
                        ingested_at=datetime.now(),
                        confidence=0.9
                    )
                )
                normalized_items.append(normalized_item)
        
        return ProviderResult(
            provider="yahoo",
            status="success",
            items=normalized_items,
            latency_ms=(time.time() - start_time) * 1000,
            keyless=True
        )
    
    async def _fetch_coingecko(self, config: Dict[str, Any], query: str, max_items: int, timeout_ms: int) -> ProviderResult:
        """Fetch from CoinGecko (mock implementation)"""
        start_time = time.time()
        
        # Mock CoinGecko data
        normalized_items = []
        cryptos = ['bitcoin', 'ethereum', 'cardano', 'solana', 'polkadot']
        
        for i, crypto in enumerate(cryptos[:max_items]):
            if query.lower() in crypto.lower() or query.lower() in ['crypto', 'bitcoin', 'ethereum']:
                normalized_item = NormalizedMarketsItem(
                    id=f"coingecko_{crypto}",
                    symbol=crypto.upper()[:4],
                    name=crypto.title(),
                    type="crypto",
                    price=PriceInfo(
                        current=50000.0 + i * 1000,
                        open=49900.0 + i * 1000,
                        high=51000.0 + i * 1000,
                        low=49000.0 + i * 1000,
                        previous_close=49950.0 + i * 1000
                    ),
                    change=ChangeInfo(
                        absolute=50.0 + i * 10,
                        percentage=0.1 + i * 0.02
                    ),
                    volume=1000000000 + i * 100000000,
                    market_cap=1000000000000 + i * 10000000000,
                    currency="USD",
                    exchange="CoinGecko",
                    sector="Cryptocurrency",
                    industry="Digital Assets",
                    timestamp=datetime.now(),
                    metadata=MarketsMetadata(
                        provider="coingecko",
                        provider_id=crypto,
                        ingested_at=datetime.now(),
                        confidence=0.92
                    )
                )
                normalized_items.append(normalized_item)
        
        return ProviderResult(
            provider="coingecko",
            status="success",
            items=normalized_items,
            latency_ms=(time.time() - start_time) * 1000,
            keyless=True
        )
