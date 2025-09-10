"""
Constraint Mapper - SarvanOM v2 External Feeds

Map guided chips (region/category/tickers/date range) to provider params.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

class FeedConstraintMapper:
    """Maps UI constraint chips to provider-specific parameters"""
    
    def __init__(self):
        self.constraint_mappings = {
            'news': {
                'region': self._map_news_region,
                'category': self._map_news_category,
                'language': self._map_news_language,
                'date_range': self._map_news_date_range,
                'sources': self._map_news_sources
            },
            'markets': {
                'tickers': self._map_market_tickers,
                'date_range': self._map_market_date_range,
                'interval': self._map_market_interval,
                'indicators': self._map_market_indicators,
                'region': self._map_market_region
            }
        }
    
    def map_constraints(self, feed_type: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Map constraints to provider-specific parameters"""
        if feed_type not in self.constraint_mappings:
            return {}
        
        mapped_constraints = {}
        mappers = self.constraint_mappings[feed_type]
        
        for constraint_key, constraint_value in constraints.items():
            if constraint_key in mappers:
                mapper = mappers[constraint_key]
                mapped_value = mapper(constraint_value)
                if mapped_value is not None:
                    mapped_constraints[constraint_key] = mapped_value
        
        return mapped_constraints
    
    # News constraint mappers
    def _map_news_region(self, region: str) -> Optional[Dict[str, Any]]:
        """Map region constraint for news providers"""
        region_mappings = {
            'US': {'country': 'us', 'language': 'en'},
            'UK': {'country': 'gb', 'language': 'en'},
            'Europe': {'region': 'europe', 'language': 'en'},
            'Asia': {'region': 'asia', 'language': 'en'},
            'Global': {}
        }
        return region_mappings.get(region, {})
    
    def _map_news_category(self, category: str) -> Optional[Dict[str, Any]]:
        """Map category constraint for news providers"""
        category_mappings = {
            'Technology': {'category': 'technology', 'sources': ['techcrunch', 'wired', 'ars-technica']},
            'Business': {'category': 'business', 'sources': ['bloomberg', 'reuters', 'wsj']},
            'Science': {'category': 'science', 'sources': ['nature', 'science', 'scientific-american']},
            'Health': {'category': 'health', 'sources': ['webmd', 'healthline', 'mayo-clinic']},
            'Sports': {'category': 'sports', 'sources': ['espn', 'bbc-sport', 'sky-sports']},
            'Politics': {'category': 'politics', 'sources': ['politico', 'the-hill', 'bbc-news']}
        }
        return category_mappings.get(category, {})
    
    def _map_news_language(self, language: str) -> Optional[Dict[str, Any]]:
        """Map language constraint for news providers"""
        language_mappings = {
            'English': {'language': 'en'},
            'Spanish': {'language': 'es'},
            'French': {'language': 'fr'},
            'German': {'language': 'de'},
            'Chinese': {'language': 'zh'},
            'Japanese': {'language': 'ja'}
        }
        return language_mappings.get(language, {})
    
    def _map_news_date_range(self, date_range: str) -> Optional[Dict[str, Any]]:
        """Map date range constraint for news providers"""
        now = datetime.now()
        
        date_mappings = {
            'Last 24 hours': {
                'from': now - timedelta(days=1),
                'to': now
            },
            'Last 7 days': {
                'from': now - timedelta(days=7),
                'to': now
            },
            'Last 30 days': {
                'from': now - timedelta(days=30),
                'to': now
            },
            'Last 3 months': {
                'from': now - timedelta(days=90),
                'to': now
            }
        }
        return date_mappings.get(date_range, {})
    
    def _map_news_sources(self, sources: List[str]) -> Optional[Dict[str, Any]]:
        """Map sources constraint for news providers"""
        return {'sources': sources}
    
    # Markets constraint mappers
    def _map_market_tickers(self, tickers: List[str]) -> Optional[Dict[str, Any]]:
        """Map tickers constraint for market providers"""
        return {'tickers': tickers}
    
    def _map_market_date_range(self, date_range: str) -> Optional[Dict[str, Any]]:
        """Map date range constraint for market providers"""
        now = datetime.now()
        
        date_mappings = {
            '1 day': {
                'from': now - timedelta(days=1),
                'to': now,
                'interval': '1m'
            },
            '1 week': {
                'from': now - timedelta(days=7),
                'to': now,
                'interval': '1h'
            },
            '1 month': {
                'from': now - timedelta(days=30),
                'to': now,
                'interval': '1d'
            },
            '3 months': {
                'from': now - timedelta(days=90),
                'to': now,
                'interval': '1d'
            },
            '1 year': {
                'from': now - timedelta(days=365),
                'to': now,
                'interval': '1wk'
            }
        }
        return date_mappings.get(date_range, {})
    
    def _map_market_interval(self, interval: str) -> Optional[Dict[str, Any]]:
        """Map interval constraint for market providers"""
        interval_mappings = {
            '1 minute': {'interval': '1m'},
            '5 minutes': {'interval': '5m'},
            '15 minutes': {'interval': '15m'},
            '1 hour': {'interval': '1h'},
            '1 day': {'interval': '1d'},
            '1 week': {'interval': '1wk'},
            '1 month': {'interval': '1mo'}
        }
        return interval_mappings.get(interval, {})
    
    def _map_market_indicators(self, indicators: List[str]) -> Optional[Dict[str, Any]]:
        """Map indicators constraint for market providers"""
        indicator_mappings = {
            'SMA': 'simple_moving_average',
            'EMA': 'exponential_moving_average',
            'RSI': 'relative_strength_index',
            'MACD': 'macd',
            'Bollinger Bands': 'bollinger_bands',
            'Volume': 'volume'
        }
        
        mapped_indicators = []
        for indicator in indicators:
            if indicator in indicator_mappings:
                mapped_indicators.append(indicator_mappings[indicator])
        
        return {'indicators': mapped_indicators} if mapped_indicators else {}
    
    def _map_market_region(self, region: str) -> Optional[Dict[str, Any]]:
        """Map region constraint for market providers"""
        region_mappings = {
            'US Markets': {'market': 'us', 'exchange': 'NASDAQ,NYSE'},
            'European Markets': {'market': 'europe', 'exchange': 'LSE,EURONEXT'},
            'Asian Markets': {'market': 'asia', 'exchange': 'TSE,HKEX'},
            'Global Markets': {}
        }
        return region_mappings.get(region, {})
    
    def get_provider_specific_params(self, provider: str, feed_type: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Get provider-specific parameters based on constraints"""
        mapped_constraints = self.map_constraints(feed_type, constraints)
        
        # Provider-specific parameter mapping
        provider_mappings = {
            'newsapi': {
                'language': mapped_constraints.get('language', {}).get('language'),
                'sources': mapped_constraints.get('sources', {}).get('sources'),
                'from': mapped_constraints.get('date_range', {}).get('from'),
                'to': mapped_constraints.get('date_range', {}).get('to'),
                'country': mapped_constraints.get('region', {}).get('country')
            },
            'alphavantage': {
                'symbol': mapped_constraints.get('tickers', {}).get('tickers', [None])[0] if mapped_constraints.get('tickers', {}).get('tickers') else None,
                'interval': mapped_constraints.get('interval', {}).get('interval'),
                'outputsize': 'compact' if mapped_constraints.get('date_range', {}).get('from') and (datetime.now() - mapped_constraints.get('date_range', {}).get('from')).days < 100 else 'full'
            },
            'yahoo': {
                'symbols': mapped_constraints.get('tickers', {}).get('tickers'),
                'interval': mapped_constraints.get('interval', {}).get('interval'),
                'range': self._get_yahoo_range(mapped_constraints.get('date_range', {}))
            },
            'coingecko': {
                'ids': mapped_constraints.get('tickers', {}).get('tickers'),
                'vs_currencies': 'usd',
                'include_24hr_change': 'true'
            }
        }
        
        return provider_mappings.get(provider, {})
    
    def _get_yahoo_range(self, date_range: Dict[str, Any]) -> str:
        """Get Yahoo Finance range parameter from date range"""
        if not date_range:
            return '1mo'
        
        from_date = date_range.get('from')
        if not from_date:
            return '1mo'
        
        days_diff = (datetime.now() - from_date).days
        
        if days_diff <= 1:
            return '1d'
        elif days_diff <= 7:
            return '5d'
        elif days_diff <= 30:
            return '1mo'
        elif days_diff <= 90:
            return '3mo'
        elif days_diff <= 365:
            return '1y'
        else:
            return 'max'
