# External Feeds Providers - SarvanOM v2

**Date**: September 9, 2025  
**Status**: ✅ **UPDATED FOR PR-7**  
**Purpose**: List free news and markets providers with normalized ingest contract - exact runtime behavior

---

## 🎯 **External Feeds Overview**

SarvanOM v2 integrates with free news and markets providers to provide real-time information and financial data. All providers follow a normalized ingest contract with consistent field mapping, rate limits, and error handling.

### **Core Principles**
1. **Free Tier Priority**: Use free tiers and open APIs whenever possible
2. **Normalized Schema**: Consistent data format across all providers
3. **Rate Limit Compliance**: Respect provider rate limits and quotas
4. **Error Resilience**: Graceful handling of provider failures
5. **Data Quality**: Validate and clean incoming data

---

## 🔄 **Runtime Behavior (PR-7 Updated)**

### **Provider Order & Execution**
- **News Lane**: Guardian → NewsAPI → Keyless (GDELT, HN Algolia, RSS)
- **Markets Lane**: Alpha Vantage → Finnhub/FMP → Keyless (Stooq, SEC EDGAR)
- **Parallel Fan-Out**: Providers execute in parallel within each lane
- **First-N Strategy**: Lane completes when sufficient results obtained

### **Budget Enforcement**
- **Per-Provider Timeout**: ≤800ms per individual provider
- **Lane Budget**: 2s (Simple), 3s (Technical), 4s (Research)
- **End-to-End Budget**: 5s (Simple), 7s (Technical), 10s (Research)
- **Graceful Degradation**: Lane continues with available providers

### **Fallback Logic**
- **Keyed Providers**: Primary providers with API keys (Guardian, NewsAPI, Alpha Vantage, Finnhub, FMP)
- **Keyless Providers**: Always available (GDELT, HN Algolia, RSS, Stooq, SEC EDGAR)
- **Fallback Activation**: Automatic when keyed providers fail or unavailable
- **Budget Compliance**: Keyless-only lanes must still meet end-to-end budgets

### **Data Normalization**
- **Common Schema**: All providers normalize to standard article/market schemas
- **Field Mapping**: Consistent field mapping across all providers
- **Data Validation**: Input validation and data cleaning
- **Error Handling**: Graceful handling of provider failures

### **Caching Strategy**
- **Cache TTL**: Per-provider cache time-to-live
- **Cache Keys**: Provider-specific cache keys
- **Cache Invalidation**: Automatic cache invalidation on errors
- **Cache Warming**: Proactive cache warming for popular queries

---

## 📰 **News Providers**

### **Provider 1: NewsAPI**
| Property | Value | Description |
|----------|-------|-------------|
| **Name** | NewsAPI | Free news aggregation API |
| **URL** | https://newsapi.org | API endpoint |
| **Free Tier** | 1000 requests/day | Rate limit |
| **Authentication** | API Key | Required |
| **Data Format** | JSON | Response format |
| **Update Frequency** | Real-time | Data freshness |
| **Coverage** | Global | Geographic coverage |
| **Languages** | Multiple | Language support |

**API Endpoints:**
- `GET /v2/everything` - Search all articles
- `GET /v2/top-headlines` - Get top headlines
- `GET /v2/sources` - Get available sources

**Rate Limits:**
- Free tier: 1000 requests/day
- Request frequency: 1 request/second
- Burst limit: 10 requests/minute

### **Provider 2: RSS Feeds**
| Property | Value | Description |
|----------|-------|-------------|
| **Name** | RSS Feeds | Syndicated content feeds |
| **URL** | Various | Multiple RSS endpoints |
| **Free Tier** | Unlimited | No rate limits |
| **Authentication** | None | Public feeds |
| **Data Format** | XML/RSS | Feed format |
| **Update Frequency** | Variable | Depends on publisher |
| **Coverage** | Global | Wide coverage |
| **Languages** | Multiple | Language support |

**Supported Feeds:**
- BBC News RSS
- Reuters RSS
- Associated Press RSS
- TechCrunch RSS
- Wired RSS

**Rate Limits:**
- No formal limits
- Recommended: 1 request per feed per 5 minutes
- Respect robots.txt and feed update frequency

### **Provider 3: Reddit API**
| Property | Value | Description |
|----------|-------|-------------|
| **Name** | Reddit API | Social media content |
| **URL** | https://www.reddit.com/api | API endpoint |
| **Free Tier** | 60 requests/minute | Rate limit |
| **Authentication** | OAuth2 | Required |
| **Data Format** | JSON | Response format |
| **Update Frequency** | Real-time | Data freshness |
| **Coverage** | Global | User-generated content |
| **Languages** | Multiple | Language support |

**API Endpoints:**
- `GET /r/{subreddit}/hot` - Hot posts from subreddit
- `GET /r/{subreddit}/new` - New posts from subreddit
- `GET /r/{subreddit}/top` - Top posts from subreddit

**Rate Limits:**
- Free tier: 60 requests/minute
- Request frequency: 1 request/second
- Burst limit: 10 requests/minute

---

## 📈 **Markets Providers**

### **Provider 1: Alpha Vantage**
| Property | Value | Description |
|----------|-------|-------------|
| **Name** | Alpha Vantage | Financial data API |
| **URL** | https://www.alphavantage.co | API endpoint |
| **Free Tier** | 5 requests/minute | Rate limit |
| **Authentication** | API Key | Required |
| **Data Format** | JSON/CSV | Response format |
| **Update Frequency** | Real-time | Data freshness |
| **Coverage** | Global | Stock markets worldwide |
| **Languages** | English | Language support |

**API Endpoints:**
- `GET /query?function=TIME_SERIES_INTRADAY` - Intraday data
- `GET /query?function=TIME_SERIES_DAILY` - Daily data
- `GET /query?function=NEWS_SENTIMENT` - News sentiment

**Rate Limits:**
- Free tier: 5 requests/minute
- Request frequency: 1 request per 12 seconds
- Daily limit: 500 requests/day

### **Provider 2: Yahoo Finance**
| Property | Value | Description |
|----------|-------|-------------|
| **Name** | Yahoo Finance | Financial data API |
| **URL** | https://query1.finance.yahoo.com | API endpoint |
| **Free Tier** | Unlimited | No formal limits |
| **Authentication** | None | Public API |
| **Data Format** | JSON | Response format |
| **Update Frequency** | Real-time | Data freshness |
| **Coverage** | Global | Stock markets worldwide |
| **Languages** | English | Language support |

**API Endpoints:**
- `GET /v8/finance/chart/{symbol}` - Stock chart data
- `GET /v1/finance/search` - Search stocks
- `GET /v1/finance/quote` - Get quotes

**Rate Limits:**
- No formal limits
- Recommended: 1 request per 2 seconds
- Respect server load

### **Provider 3: CoinGecko**
| Property | Value | Description |
|----------|-------|-------------|
| **Name** | CoinGecko | Cryptocurrency data API |
| **URL** | https://api.coingecko.com | API endpoint |
| **Free Tier** | 50 requests/minute | Rate limit |
| **Authentication** | API Key | Optional |
| **Data Format** | JSON | Response format |
| **Update Frequency** | Real-time | Data freshness |
| **Coverage** | Global | Cryptocurrency markets |
| **Languages** | English | Language support |

**API Endpoints:**
- `GET /api/v3/coins/markets` - Market data
- `GET /api/v3/coins/{id}` - Coin details
- `GET /api/v3/coins/{id}/market_chart` - Price charts

**Rate Limits:**
- Free tier: 50 requests/minute
- Request frequency: 1 request per 1.2 seconds
- Daily limit: 10,000 requests/day

---

## 📋 **Normalized Ingest Contract**

### **News Data Schema**
```json
{
  "id": "news_12345",
  "title": "Article Title",
  "content": "Article content...",
  "excerpt": "Article excerpt...",
  "url": "https://example.com/article",
  "source": {
    "name": "Source Name",
    "domain": "example.com",
    "authority_score": 0.8
  },
  "author": "Author Name",
  "published_at": "2025-09-09T10:00:00Z",
  "language": "en",
  "category": "technology",
  "tags": ["AI", "machine learning"],
  "sentiment": {
    "score": 0.7,
    "label": "positive"
  },
  "metadata": {
    "provider": "newsapi",
    "provider_id": "provider_123",
    "ingested_at": "2025-09-09T10:05:00Z",
    "confidence": 0.95
  }
}
```

### **Markets Data Schema**
```json
{
  "id": "market_12345",
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "type": "stock",
  "price": {
    "current": 150.25,
    "open": 149.50,
    "high": 151.00,
    "low": 149.00,
    "previous_close": 149.75
  },
  "change": {
    "absolute": 0.50,
    "percentage": 0.33
  },
  "volume": 50000000,
  "market_cap": 2500000000000,
  "currency": "USD",
  "exchange": "NASDAQ",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "timestamp": "2025-09-09T10:00:00Z",
  "metadata": {
    "provider": "alphavantage",
    "provider_id": "provider_123",
    "ingested_at": "2025-09-09T10:05:00Z",
    "confidence": 0.98
  }
}
```

### **Field Mapping**
| Standard Field | NewsAPI | RSS | Reddit | Alpha Vantage | Yahoo Finance | CoinGecko |
|----------------|---------|-----|--------|---------------|---------------|-----------|
| **id** | url | guid | id | symbol | symbol | id |
| **title** | title | title | title | - | longName | name |
| **content** | content | description | selftext | - | - | - |
| **url** | url | link | url | - | - | - |
| **published_at** | publishedAt | pubDate | created_utc | - | - | - |
| **author** | author | author | author | - | - | - |
| **source** | source.name | source | subreddit | - | - | - |
| **category** | category | category | subreddit | - | sector | categories |
| **tags** | - | tags | - | - | - | - |
| **price** | - | - | - | price | regularMarketPrice | current_price |
| **change** | - | - | - | change | regularMarketChange | price_change_24h |
| **volume** | - | - | - | volume | regularMarketVolume | total_volume |

---

## ⏱️ **Time Budgets & Cache TTLs**

### **Time Budgets**
| Provider | Timeout | Retry Count | Backoff Strategy |
|----------|---------|-------------|------------------|
| **NewsAPI** | 800ms | 2 | Exponential (1s, 2s) |
| **RSS Feeds** | 800ms | 1 | Linear (5s) |
| **Reddit API** | 800ms | 2 | Exponential (1s, 2s) |
| **Alpha Vantage** | 800ms | 1 | Linear (12s) |
| **Yahoo Finance** | 800ms | 2 | Exponential (2s, 4s) |
| **CoinGecko** | 800ms | 2 | Exponential (1.2s, 2.4s) |

### **Cache TTLs**
| Data Type | TTL | Reason |
|-----------|-----|--------|
| **News Articles** | 300s (5 min) | News becomes stale quickly |
| **Stock Prices** | 60s (1 min) | Prices change frequently |
| **Crypto Prices** | 30s (30 sec) | Crypto is very volatile |
| **Market Data** | 300s (5 min) | Market data updates regularly |
| **Sentiment Data** | 600s (10 min) | Sentiment changes slowly |
| **Source Metadata** | 3600s (1 hour) | Source info is stable |

### **Cache Strategy**
```python
# Example cache strategy
class FeedCacheManager:
    def __init__(self):
        self.cache_ttls = {
            "news": 300,      # 5 minutes
            "stocks": 60,     # 1 minute
            "crypto": 30,     # 30 seconds
            "markets": 300,   # 5 minutes
            "sentiment": 600, # 10 minutes
            "metadata": 3600  # 1 hour
        }
    
    def get_cache_key(self, provider: str, data_type: str, params: dict) -> str:
        """Generate cache key for data"""
        param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        return f"feed:{provider}:{data_type}:{hash(param_str)}"
    
    def should_cache(self, data_type: str, response_time: float) -> bool:
        """Determine if data should be cached"""
        # Don't cache if response was slow (likely error)
        if response_time > 1000:  # 1 second
            return False
        
        # Don't cache if data type is not cacheable
        if data_type not in self.cache_ttls:
            return False
        
        return True
```

---

## 🔄 **Error Mapping & Handling**

### **Error Types**
| Error Type | Description | Action | Retry |
|------------|-------------|--------|-------|
| **Rate Limit** | Too many requests | Wait and retry | Yes |
| **Authentication** | Invalid API key | Log and skip | No |
| **Network** | Connection timeout | Retry with backoff | Yes |
| **Data Format** | Invalid response | Log and skip | No |
| **Server Error** | 5xx status codes | Retry with backoff | Yes |
| **Client Error** | 4xx status codes | Log and skip | No |

### **Error Handling Implementation**
```python
# Example error handling
class FeedErrorHandler:
    def __init__(self):
        self.retryable_errors = {
            "rate_limit": True,
            "network": True,
            "server_error": True,
            "authentication": False,
            "data_format": False,
            "client_error": False
        }
    
    def handle_error(self, error: Exception, provider: str, retry_count: int) -> dict:
        """Handle feed errors"""
        error_type = self.classify_error(error)
        
        if error_type == "rate_limit":
            return self.handle_rate_limit(error, provider)
        elif error_type == "network":
            return self.handle_network_error(error, retry_count)
        elif error_type == "server_error":
            return self.handle_server_error(error, retry_count)
        else:
            return self.handle_non_retryable_error(error, provider)
    
    def classify_error(self, error: Exception) -> str:
        """Classify error type"""
        if "rate limit" in str(error).lower():
            return "rate_limit"
        elif "timeout" in str(error).lower():
            return "network"
        elif "5" in str(error) and "status" in str(error).lower():
            return "server_error"
        elif "4" in str(error) and "status" in str(error).lower():
            return "client_error"
        elif "unauthorized" in str(error).lower():
            return "authentication"
        else:
            return "data_format"
    
    def handle_rate_limit(self, error: Exception, provider: str) -> dict:
        """Handle rate limit errors"""
        # Extract retry-after header if available
        retry_after = self.extract_retry_after(error)
        
        return {
            "action": "retry",
            "retry_after": retry_after,
            "message": f"Rate limit exceeded for {provider}",
            "retryable": True
        }
    
    def handle_network_error(self, error: Exception, retry_count: int) -> dict:
        """Handle network errors"""
        if retry_count < 2:
            return {
                "action": "retry",
                "retry_after": 2 ** retry_count,  # Exponential backoff
                "message": f"Network error: {error}",
                "retryable": True
            }
        else:
            return {
                "action": "skip",
                "message": f"Network error after {retry_count} retries: {error}",
                "retryable": False
            }
```

---

## 🎯 **Guided Chips for Feed-Specific Constraints**

### **Constraint Chips Mapping**
The Guided Prompt Confirmation feature provides constraint chips that map to specific provider query parameters:

```python
# Example constraint chips mapping
class FeedConstraintMapper:
    def __init__(self):
        self.constraint_mappings = {
            'news': {
                'region': self.map_news_region,
                'category': self.map_news_category,
                'language': self.map_news_language,
                'date_range': self.map_news_date_range,
                'sources': self.map_news_sources
            },
            'markets': {
                'tickers': self.map_market_tickers,
                'date_range': self.map_market_date_range,
                'interval': self.map_market_interval,
                'indicators': self.map_market_indicators,
                'region': self.map_market_region
            }
        }
    
    def map_constraints_to_provider_params(self, feed_type: str, constraints: dict) -> dict:
        """Map constraint chips to provider-specific parameters"""
        if feed_type not in self.constraint_mappings:
            return {}
        
        provider_params = {}
        constraint_mappings = self.constraint_mappings[feed_type]
        
        for constraint_type, constraint_value in constraints.items():
            if constraint_type in constraint_mappings:
                mapped_params = constraint_mappings[constraint_type](constraint_value)
                provider_params.update(mapped_params)
        
        return provider_params
    
    def map_news_region(self, region: str) -> dict:
        """Map region constraint to news provider parameters"""
        region_mappings = {
            'global': {'country': None, 'language': 'en'},
            'us': {'country': 'us', 'language': 'en'},
            'uk': {'country': 'gb', 'language': 'en'},
            'europe': {'country': None, 'language': 'en', 'region': 'europe'},
            'asia': {'country': None, 'language': 'en', 'region': 'asia'},
            'africa': {'country': None, 'language': 'en', 'region': 'africa'},
            'americas': {'country': None, 'language': 'en', 'region': 'americas'}
        }
        return region_mappings.get(region, region_mappings['global'])
    
    def map_news_category(self, category: str) -> dict:
        """Map category constraint to news provider parameters"""
        category_mappings = {
            'business': {'category': 'business'},
            'technology': {'category': 'technology'},
            'science': {'category': 'science'},
            'health': {'category': 'health'},
            'sports': {'category': 'sports'},
            'entertainment': {'category': 'entertainment'},
            'politics': {'category': 'politics'},
            'general': {'category': 'general'}
        }
        return category_mappings.get(category, category_mappings['general'])
    
    def map_news_language(self, language: str) -> dict:
        """Map language constraint to news provider parameters"""
        language_mappings = {
            'en': {'language': 'en'},
            'es': {'language': 'es'},
            'fr': {'language': 'fr'},
            'de': {'language': 'de'},
            'it': {'language': 'it'},
            'pt': {'language': 'pt'},
            'ru': {'language': 'ru'},
            'zh': {'language': 'zh'},
            'ja': {'language': 'ja'},
            'ko': {'language': 'ko'}
        }
        return language_mappings.get(language, language_mappings['en'])
    
    def map_news_date_range(self, date_range: str) -> dict:
        """Map date range constraint to news provider parameters"""
        now = datetime.now()
        date_mappings = {
            'today': {'from': now.strftime('%Y-%m-%d'), 'to': now.strftime('%Y-%m-%d')},
            'yesterday': {
                'from': (now - timedelta(days=1)).strftime('%Y-%m-%d'),
                'to': (now - timedelta(days=1)).strftime('%Y-%m-%d')
            },
            'last_week': {
                'from': (now - timedelta(days=7)).strftime('%Y-%m-%d'),
                'to': now.strftime('%Y-%m-%d')
            },
            'last_month': {
                'from': (now - timedelta(days=30)).strftime('%Y-%m-%d'),
                'to': now.strftime('%Y-%m-%d')
            },
            'last_year': {
                'from': (now - timedelta(days=365)).strftime('%Y-%m-%d'),
                'to': now.strftime('%Y-%m-%d')
            }
        }
        return date_mappings.get(date_range, date_mappings['last_week'])
    
    def map_news_sources(self, sources: str) -> dict:
        """Map sources constraint to news provider parameters"""
        source_mappings = {
            'all': {'sources': None},
            'reuters': {'sources': 'reuters'},
            'bbc': {'sources': 'bbc-news'},
            'cnn': {'sources': 'cnn'},
            'nytimes': {'sources': 'the-new-york-times'},
            'guardian': {'sources': 'the-guardian-uk'},
            'techcrunch': {'sources': 'techcrunch'},
            'wired': {'sources': 'wired'},
            'academic': {'sources': 'arxiv,scholar'}
        }
        return source_mappings.get(sources, source_mappings['all'])
    
    def map_market_tickers(self, tickers: str) -> dict:
        """Map ticker constraint to market provider parameters"""
        # Parse comma-separated tickers
        ticker_list = [ticker.strip().upper() for ticker in tickers.split(',')]
        
        return {
            'symbols': ticker_list,
            'symbol_count': len(ticker_list)
        }
    
    def map_market_date_range(self, date_range: str) -> dict:
        """Map date range constraint to market provider parameters"""
        now = datetime.now()
        date_mappings = {
            'today': {'from': now.strftime('%Y-%m-%d'), 'to': now.strftime('%Y-%m-%d')},
            'last_week': {
                'from': (now - timedelta(days=7)).strftime('%Y-%m-%d'),
                'to': now.strftime('%Y-%m-%d')
            },
            'last_month': {
                'from': (now - timedelta(days=30)).strftime('%Y-%m-%d'),
                'to': now.strftime('%Y-%m-%d')
            },
            'last_quarter': {
                'from': (now - timedelta(days=90)).strftime('%Y-%m-%d'),
                'to': now.strftime('%Y-%m-%d')
            },
            'last_year': {
                'from': (now - timedelta(days=365)).strftime('%Y-%m-%d'),
                'to': now.strftime('%Y-%m-%d')
            },
            '5_years': {
                'from': (now - timedelta(days=365*5)).strftime('%Y-%m-%d'),
                'to': now.strftime('%Y-%m-%d')
            }
        }
        return date_mappings.get(date_range, date_mappings['last_month'])
    
    def map_market_interval(self, interval: str) -> dict:
        """Map interval constraint to market provider parameters"""
        interval_mappings = {
            '1min': {'interval': '1min'},
            '5min': {'interval': '5min'},
            '15min': {'interval': '15min'},
            '30min': {'interval': '30min'},
            '1hour': {'interval': '1h'},
            '1day': {'interval': '1d'},
            '1week': {'interval': '1wk'},
            '1month': {'interval': '1mo'}
        }
        return interval_mappings.get(interval, interval_mappings['1day'])
    
    def map_market_indicators(self, indicators: str) -> dict:
        """Map indicators constraint to market provider parameters"""
        indicator_list = [indicator.strip().lower() for indicator in indicators.split(',')]
        
        # Map common indicators to provider-specific names
        indicator_mappings = {
            'sma': 'SMA',
            'ema': 'EMA',
            'rsi': 'RSI',
            'macd': 'MACD',
            'bollinger': 'BBANDS',
            'volume': 'VOLUME',
            'price': 'PRICE'
        }
        
        mapped_indicators = []
        for indicator in indicator_list:
            if indicator in indicator_mappings:
                mapped_indicators.append(indicator_mappings[indicator])
            else:
                mapped_indicators.append(indicator.upper())
        
        return {
            'indicators': mapped_indicators,
            'indicator_count': len(mapped_indicators)
        }
    
    def map_market_region(self, region: str) -> dict:
        """Map region constraint to market provider parameters"""
        region_mappings = {
            'global': {'region': 'global'},
            'us': {'region': 'us', 'exchange': 'NASDAQ,NYSE'},
            'uk': {'region': 'uk', 'exchange': 'LSE'},
            'europe': {'region': 'europe', 'exchange': 'EURONEXT'},
            'asia': {'region': 'asia', 'exchange': 'NSE,BSE'},
            'japan': {'region': 'japan', 'exchange': 'TSE'},
            'china': {'region': 'china', 'exchange': 'SSE,SZSE'},
            'australia': {'region': 'australia', 'exchange': 'ASX'}
        }
        return region_mappings.get(region, region_mappings['global'])
```

### **Constraint Chips UI Integration**
```python
# Example constraint chips UI integration
class ConstraintChipsUI:
    def __init__(self):
        self.feed_constraints = {
            'news': {
                'region': ['global', 'us', 'uk', 'europe', 'asia', 'africa', 'americas'],
                'category': ['business', 'technology', 'science', 'health', 'sports', 'entertainment', 'politics', 'general'],
                'language': ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko'],
                'date_range': ['today', 'yesterday', 'last_week', 'last_month', 'last_year'],
                'sources': ['all', 'reuters', 'bbc', 'cnn', 'nytimes', 'guardian', 'techcrunch', 'wired', 'academic']
            },
            'markets': {
                'tickers': 'text_input',  # Free text input for ticker symbols
                'date_range': ['today', 'last_week', 'last_month', 'last_quarter', 'last_year', '5_years'],
                'interval': ['1min', '5min', '15min', '30min', '1hour', '1day', '1week', '1month'],
                'indicators': ['sma', 'ema', 'rsi', 'macd', 'bollinger', 'volume', 'price'],
                'region': ['global', 'us', 'uk', 'europe', 'asia', 'japan', 'china', 'australia']
            }
        }
    
    def get_constraint_chips_for_feed(self, feed_type: str) -> dict:
        """Get available constraint chips for a specific feed type"""
        return self.feed_constraints.get(feed_type, {})
    
    def render_constraint_chips(self, feed_type: str, selected_constraints: dict = None) -> str:
        """Render constraint chips HTML for a specific feed type"""
        if selected_constraints is None:
            selected_constraints = {}
        
        available_constraints = self.get_constraint_chips_for_feed(feed_type)
        
        html_chips = []
        for constraint_type, constraint_options in available_constraints.items():
            if constraint_type == 'tickers':  # Special case for text input
                html_chips.append(f'''
                <div class="constraint-chip-group">
                    <label>Ticker Symbols:</label>
                    <input type="text" 
                           name="tickers" 
                           placeholder="AAPL, GOOGL, MSFT" 
                           value="{selected_constraints.get('tickers', '')}"
                           class="constraint-input">
                </div>
                ''')
            else:
                chip_html = f'''
                <div class="constraint-chip-group">
                    <label>{constraint_type.replace('_', ' ').title()}:</label>
                    <div class="constraint-chips">
                '''
                
                for option in constraint_options:
                    is_selected = selected_constraints.get(constraint_type) == option
                    selected_class = 'selected' if is_selected else ''
                    
                    chip_html += f'''
                    <button type="button" 
                            class="constraint-chip {selected_class}"
                            data-constraint-type="{constraint_type}"
                            data-constraint-value="{option}">
                        {option.replace('_', ' ').title()}
                    </button>
                    '''
                
                chip_html += '''
                    </div>
                </div>
                '''
                html_chips.append(chip_html)
        
        return ''.join(html_chips)
```

---

## 📊 **Provider Health Monitoring**

### **Health Metrics**
| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| **Response Time** | Average response time | < 800ms | > 1000ms |
| **Success Rate** | % of successful requests | > 95% | < 90% |
| **Rate Limit Hits** | % of rate-limited requests | < 5% | > 10% |
| **Data Quality** | % of valid data | > 98% | < 95% |
| **Availability** | % uptime | > 99% | < 95% |

### **Health Monitoring**
```python
# Example health monitoring
class ProviderHealthMonitor:
    def __init__(self):
        self.metrics = {}
        self.health_thresholds = {
            "response_time": 1000,  # ms
            "success_rate": 0.90,   # 90%
            "rate_limit_hits": 0.10, # 10%
            "data_quality": 0.95,   # 95%
            "availability": 0.95    # 95%
        }
    
    def record_request(self, provider: str, success: bool, response_time: float, data_quality: float):
        """Record request metrics"""
        if provider not in self.metrics:
            self.metrics[provider] = {
                "total_requests": 0,
                "successful_requests": 0,
                "total_response_time": 0.0,
                "total_data_quality": 0.0,
                "rate_limit_hits": 0
            }
        
        metrics = self.metrics[provider]
        metrics["total_requests"] += 1
        
        if success:
            metrics["successful_requests"] += 1
            metrics["total_response_time"] += response_time
            metrics["total_data_quality"] += data_quality
        
        if "rate limit" in str(success).lower():
            metrics["rate_limit_hits"] += 1
    
    def get_health_status(self, provider: str) -> dict:
        """Get provider health status"""
        if provider not in self.metrics:
            return {"status": "unknown", "message": "No data available"}
        
        metrics = self.metrics[provider]
        
        # Calculate health metrics
        success_rate = metrics["successful_requests"] / max(metrics["total_requests"], 1)
        avg_response_time = metrics["total_response_time"] / max(metrics["successful_requests"], 1)
        rate_limit_rate = metrics["rate_limit_hits"] / max(metrics["total_requests"], 1)
        avg_data_quality = metrics["total_data_quality"] / max(metrics["successful_requests"], 1)
        
        # Determine health status
        if (success_rate >= self.health_thresholds["success_rate"] and
            avg_response_time <= self.health_thresholds["response_time"] and
            rate_limit_rate <= self.health_thresholds["rate_limit_hits"] and
            avg_data_quality >= self.health_thresholds["data_quality"]):
            status = "healthy"
        else:
            status = "unhealthy"
        
        return {
            "status": status,
            "metrics": {
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "rate_limit_rate": rate_limit_rate,
                "avg_data_quality": avg_data_quality
            },
            "thresholds": self.health_thresholds
        }
```

---

## 📚 **References**

- External Feeds: `14_external_feeds_news_markets.md`
- Retrieval & Index Fabric: `06_retrieval_and_index_fabric.md`
- System Context: `docs/architecture/system_context.md`
- Budgets: `docs/architecture/budgets.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This external feeds providers specification provides the foundation for real-time news and markets data in SarvanOM v2.*
