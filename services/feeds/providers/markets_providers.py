"""
Markets Providers - SarvanOM v2 External Feeds

Multiple free markets providers: Alpha Vantage, Yahoo Finance, CoinGecko.
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

class AlphaVantageProvider:
    """Alpha Vantage provider for financial data"""
    
    def __init__(self, api_key: str, redis_client: redis.Redis):
        self.api_key = api_key
        self.redis = redis_client
        self.base_url = "https://www.alphavantage.co/query"
        self.rate_limit = 5  # requests per minute
        self.http_client = httpx.AsyncClient()
    
    async def fetch_markets(self, query: str, constraints: Dict[str, Any] = None) -> FeedResult:
        """Fetch market data from Alpha Vantage"""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = f"alphavantage:{hashlib.md5(query.encode()).hexdigest()}"
            cached_result = await self._get_from_cache(cache_key)
            if cached_result:
                return FeedResult(
                    provider="alphavantage",
                    status="healthy",
                    items=cached_result,
                    latency_ms=(time.time() - start_time) * 1000,
                    cache_hit=True
                )
            
            # Extract ticker symbols from query or constraints
            tickers = self._extract_tickers(query, constraints)
            if not tickers:
                return FeedResult(
                    provider="alphavantage",
                    status="error",
                    items=[],
                    latency_ms=(time.time() - start_time) * 1000,
                    error="No ticker symbols found"
                )
            
            # Fetch data for each ticker
            all_items = []
            for ticker in tickers[:3]:  # Limit to 3 tickers to respect rate limits
                try:
                    # Get quote data
                    quote_data = await self._get_quote(ticker)
                    if quote_data:
                        all_items.append(quote_data)
                    
                    # Get news sentiment
                    news_data = await self._get_news_sentiment(ticker)
                    if news_data:
                        all_items.extend(news_data)
                        
                except Exception as e:
                    logger.error(f"Error fetching data for {ticker}: {e}")
                    continue
            
            # Cache results
            await self._set_cache(cache_key, all_items, ttl=300)
            
            return FeedResult(
                provider="alphavantage",
                status="healthy",
                items=all_items,
                latency_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            return FeedResult(
                provider="alphavantage",
                status="error",
                items=[],
                latency_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
    
    def _extract_tickers(self, query: str, constraints: Dict[str, Any] = None) -> List[str]:
        """Extract ticker symbols from query or constraints"""
        tickers = []
        
        # Check constraints first
        if constraints and constraints.get("tickers"):
            tickers.extend(constraints["tickers"])
        
        # Extract from query (simple pattern matching)
        query_upper = query.upper()
        common_tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX", "AMD", "INTC"]
        
        for ticker in common_tickers:
            if ticker in query_upper:
                tickers.append(ticker)
        
        # Remove duplicates and return
        return list(set(tickers))
    
    async def _get_quote(self, symbol: str) -> Optional[NormalizedFeedItem]:
        """Get quote data for a symbol"""
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            response = await self.http_client.get(self.base_url, params=params, timeout=0.8)
            
            if response.status_code == 200:
                data = response.json()
                quote = data.get("Global Quote", {})
                
                if quote:
                    price = quote.get("05. price", "N/A")
                    change = quote.get("09. change", "N/A")
                    change_percent = quote.get("10. change percent", "N/A")
                    
                    return NormalizedFeedItem(
                        id=f"quote_{symbol}_{int(time.time())}",
                        title=f"{symbol} Stock Quote",
                        content=f"Price: ${price}, Change: {change} ({change_percent})",
                        url=f"https://www.alphavantage.co/quote/{symbol}",
                        source="Alpha Vantage",
                        author=None,
                        published_at=datetime.now(),
                        category="markets",
                        tags=["stock", "quote", symbol.lower()],
                        language="en",
                        provider="alphavantage",
                        attribution={
                            "source": {
                                "name": "Alpha Vantage",
                                "url": "https://www.alphavantage.co"
                            },
                            "data": {
                                "symbol": symbol,
                                "price": price,
                                "change": change,
                                "change_percent": change_percent
                            },
                            "license": {
                                "type": "api_terms",
                                "terms": "Data provided by Alpha Vantage API"
                            }
                        },
                        metadata={
                            "provider": "alphavantage",
                            "symbol": symbol,
                            "data_type": "quote",
                            "raw_data": quote
                        }
                    )
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
        
        return None
    
    async def _get_news_sentiment(self, symbol: str) -> List[NormalizedFeedItem]:
        """Get news sentiment for a symbol"""
        try:
            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": symbol,
                "apikey": self.api_key,
                "limit": 5
            }
            
            response = await self.http_client.get(self.base_url, params=params, timeout=0.8)
            
            if response.status_code == 200:
                data = response.json()
                news_items = data.get("feed", [])
                
                normalized_items = []
                for item in news_items:
                    try:
                        published_at = None
                        if item.get("time_published"):
                            published_at = datetime.strptime(item["time_published"], "%Y%m%dT%H%M%S")
                        
                        sentiment = item.get("overall_sentiment_score", 0)
                        sentiment_label = item.get("overall_sentiment_label", "Neutral")
                        
                        normalized_item = NormalizedFeedItem(
                            id=hashlib.md5(item.get("url", "").encode()).hexdigest(),
                            title=item.get("title", ""),
                            content=item.get("summary", ""),
                            url=item.get("url", ""),
                            source=item.get("source", "Unknown"),
                            author=None,
                            published_at=published_at,
                            category="markets",
                            tags=["news", "sentiment", symbol.lower()],
                            language="en",
                            provider="alphavantage",
                            attribution={
                                "source": {
                                    "name": item.get("source", "Unknown"),
                                    "url": item.get("url", "")
                                },
                                "article": {
                                    "title": item.get("title", ""),
                                    "url": item.get("url", ""),
                                    "published_at": item.get("time_published")
                                },
                                "license": {
                                    "type": "api_terms",
                                    "terms": "Data provided by Alpha Vantage API"
                                }
                            },
                            metadata={
                                "provider": "alphavantage",
                                "symbol": symbol,
                                "data_type": "news_sentiment",
                                "sentiment_score": sentiment,
                                "sentiment_label": sentiment_label,
                                "raw_data": item
                            }
                        )
                        normalized_items.append(normalized_item)
                    except Exception as e:
                        logger.error(f"Error normalizing news item: {e}")
                        continue
                
                return normalized_items
        except Exception as e:
            logger.error(f"Error getting news sentiment for {symbol}: {e}")
        
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
    
    async def _set_cache(self, key: str, value: List[NormalizedFeedItem], ttl: int = 300):
        """Set result in cache"""
        try:
            data = [asdict(item) for item in value]
            self.redis.setex(key, ttl, json.dumps(data, default=str))
        except Exception as e:
            logger.error(f"Cache set error: {e}")

class YahooFinanceProvider:
    """Yahoo Finance provider for financial data"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.base_url = "https://query1.finance.yahoo.com"
        self.http_client = httpx.AsyncClient()
    
    async def fetch_markets(self, query: str, constraints: Dict[str, Any] = None) -> FeedResult:
        """Fetch market data from Yahoo Finance"""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = f"yahoo:{hashlib.md5(query.encode()).hexdigest()}"
            cached_result = await self._get_from_cache(cache_key)
            if cached_result:
                return FeedResult(
                    provider="yahoo",
                    status="healthy",
                    items=cached_result,
                    latency_ms=(time.time() - start_time) * 1000,
                    cache_hit=True
                )
            
            # Extract ticker symbols
            tickers = self._extract_tickers(query, constraints)
            if not tickers:
                return FeedResult(
                    provider="yahoo",
                    status="error",
                    items=[],
                    latency_ms=(time.time() - start_time) * 1000,
                    error="No ticker symbols found"
                )
            
            # Fetch data for each ticker
            all_items = []
            for ticker in tickers[:5]:  # Limit to 5 tickers
                try:
                    quote_data = await self._get_quote(ticker)
                    if quote_data:
                        all_items.append(quote_data)
                except Exception as e:
                    logger.error(f"Error fetching data for {ticker}: {e}")
                    continue
            
            # Cache results
            await self._set_cache(cache_key, all_items, ttl=300)
            
            return FeedResult(
                provider="yahoo",
                status="healthy",
                items=all_items,
                latency_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            return FeedResult(
                provider="yahoo",
                status="error",
                items=[],
                latency_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
    
    def _extract_tickers(self, query: str, constraints: Dict[str, Any] = None) -> List[str]:
        """Extract ticker symbols from query or constraints"""
        tickers = []
        
        # Check constraints first
        if constraints and constraints.get("tickers"):
            tickers.extend(constraints["tickers"])
        
        # Extract from query
        query_upper = query.upper()
        common_tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX", "AMD", "INTC"]
        
        for ticker in common_tickers:
            if ticker in query_upper:
                tickers.append(ticker)
        
        return list(set(tickers))
    
    async def _get_quote(self, symbol: str) -> Optional[NormalizedFeedItem]:
        """Get quote data for a symbol"""
        try:
            params = {
                "symbols": symbol,
                "fields": "regularMarketPrice,regularMarketChange,regularMarketChangePercent,regularMarketTime"
            }
            
            response = await self.http_client.get(
                f"{self.base_url}/v1/finance/quote",
                params=params,
                timeout=0.8
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("result", [])
                
                if result:
                    quote = result[0]
                    price = quote.get("regularMarketPrice", "N/A")
                    change = quote.get("regularMarketChange", "N/A")
                    change_percent = quote.get("regularMarketChangePercent", "N/A")
                    
                    return NormalizedFeedItem(
                        id=f"yahoo_quote_{symbol}_{int(time.time())}",
                        title=f"{symbol} Stock Quote (Yahoo Finance)",
                        content=f"Price: ${price}, Change: {change} ({change_percent}%)",
                        url=f"https://finance.yahoo.com/quote/{symbol}",
                        source="Yahoo Finance",
                        author=None,
                        published_at=datetime.now(),
                        category="markets",
                        tags=["stock", "quote", symbol.lower()],
                        language="en",
                        provider="yahoo",
                        attribution={
                            "source": {
                                "name": "Yahoo Finance",
                                "url": "https://finance.yahoo.com"
                            },
                            "data": {
                                "symbol": symbol,
                                "price": price,
                                "change": change,
                                "change_percent": change_percent
                            },
                            "license": {
                                "type": "public_api",
                                "terms": "Data provided by Yahoo Finance public API"
                            }
                        },
                        metadata={
                            "provider": "yahoo",
                            "symbol": symbol,
                            "data_type": "quote",
                            "raw_data": quote
                        }
                    )
        except Exception as e:
            logger.error(f"Error getting Yahoo quote for {symbol}: {e}")
        
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

class CoinGeckoProvider:
    """CoinGecko provider for cryptocurrency data"""
    
    def __init__(self, api_key: Optional[str], redis_client: redis.Redis):
        self.api_key = api_key
        self.redis = redis_client
        self.base_url = "https://api.coingecko.com/api/v3"
        self.rate_limit = 50  # requests per minute
        self.http_client = httpx.AsyncClient()
    
    async def fetch_markets(self, query: str, constraints: Dict[str, Any] = None) -> FeedResult:
        """Fetch cryptocurrency data from CoinGecko"""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = f"coingecko:{hashlib.md5(query.encode()).hexdigest()}"
            cached_result = await self._get_from_cache(cache_key)
            if cached_result:
                return FeedResult(
                    provider="coingecko",
                    status="healthy",
                    items=cached_result,
                    latency_ms=(time.time() - start_time) * 1000,
                    cache_hit=True
                )
            
            # Extract cryptocurrency symbols
            crypto_symbols = self._extract_crypto_symbols(query, constraints)
            if not crypto_symbols:
                return FeedResult(
                    provider="coingecko",
                    status="error",
                    items=[],
                    latency_ms=(time.time() - start_time) * 1000,
                    error="No cryptocurrency symbols found"
                )
            
            # Fetch data for each cryptocurrency
            all_items = []
            for symbol in crypto_symbols[:3]:  # Limit to 3 symbols
                try:
                    crypto_data = await self._get_crypto_data(symbol)
                    if crypto_data:
                        all_items.append(crypto_data)
                except Exception as e:
                    logger.error(f"Error fetching data for {symbol}: {e}")
                    continue
            
            # Cache results
            await self._set_cache(cache_key, all_items, ttl=300)
            
            return FeedResult(
                provider="coingecko",
                status="healthy",
                items=all_items,
                latency_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            return FeedResult(
                provider="coingecko",
                status="error",
                items=[],
                latency_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
    
    def _extract_crypto_symbols(self, query: str, constraints: Dict[str, Any] = None) -> List[str]:
        """Extract cryptocurrency symbols from query or constraints"""
        symbols = []
        
        # Check constraints first
        if constraints and constraints.get("tickers"):
            symbols.extend(constraints["tickers"])
        
        # Extract from query
        query_lower = query.lower()
        common_cryptos = ["bitcoin", "btc", "ethereum", "eth", "cardano", "ada", "solana", "sol", "polkadot", "dot"]
        
        for crypto in common_cryptos:
            if crypto in query_lower:
                symbols.append(crypto)
        
        return list(set(symbols))
    
    async def _get_crypto_data(self, symbol: str) -> Optional[NormalizedFeedItem]:
        """Get cryptocurrency data"""
        try:
            params = {
                "ids": symbol,
                "vs_currencies": "usd",
                "include_24hr_change": "true"
            }
            
            if self.api_key:
                params["x_cg_demo_api_key"] = self.api_key
            
            response = await self.http_client.get(
                f"{self.base_url}/simple/price",
                params=params,
                timeout=0.8
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if symbol in data:
                    crypto_data = data[symbol]
                    price = crypto_data.get("usd", "N/A")
                    change_24h = crypto_data.get("usd_24h_change", "N/A")
                    
                    return NormalizedFeedItem(
                        id=f"coingecko_{symbol}_{int(time.time())}",
                        title=f"{symbol.upper()} Cryptocurrency Price",
                        content=f"Price: ${price}, 24h Change: {change_24h}%",
                        url=f"https://www.coingecko.com/en/coins/{symbol}",
                        source="CoinGecko",
                        author=None,
                        published_at=datetime.now(),
                        category="cryptocurrency",
                        tags=["crypto", "price", symbol.lower()],
                        language="en",
                        provider="coingecko",
                        attribution={
                            "source": {
                                "name": "CoinGecko",
                                "url": "https://www.coingecko.com"
                            },
                            "data": {
                                "symbol": symbol,
                                "price": price,
                                "change_24h": change_24h
                            },
                            "license": {
                                "type": "api_terms",
                                "terms": "Data provided by CoinGecko API"
                            }
                        },
                        metadata={
                            "provider": "coingecko",
                            "symbol": symbol,
                            "data_type": "crypto_price",
                            "raw_data": crypto_data
                        }
                    )
        except Exception as e:
            logger.error(f"Error getting CoinGecko data for {symbol}: {e}")
        
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
