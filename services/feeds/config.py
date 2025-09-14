"""
Feeds Service Configuration - SarvanOM v2

Configuration module for the Feeds service that reads only canonical
environment variable names and implements safe fallbacks.

Features:
    - Canonical environment variable names only
    - Fail-fast for required providers
    - Safe fallbacks for optional providers
    - News and markets provider configurations
    - Integration with centralized provider config
"""

import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import structlog

# Import the centralized provider configuration
from shared.core.config.provider_config import (
    provider_config,
    get_provider_key,
    is_provider_available,
    get_lane_providers,
    get_lane_keyless_fallbacks,
    get_provider_summary,
    log_provider_status
)

logger = structlog.get_logger(__name__)

@dataclass
class FeedProviderConfig:
    """Configuration for a feed provider"""
    name: str
    env_key: Optional[str]
    is_configured: bool
    is_required: bool
    timeout_ms: int = 800
    cache_ttl_seconds: int = 300

@dataclass
class FeedsConfig:
    """Configuration for Feeds service"""
    
    # Service settings
    service_name: str = "feeds"
    port: int = 8005
    metrics_port: int = 8008
    
    # Provider timeout budget
    provider_timeout_ms: int = 800
    
    # Cache TTLs (from docs/feeds/providers.md)
    news_cache_ttl_seconds: int = 300  # 5 minutes
    markets_cache_ttl_seconds: int = 60  # 1 minute
    crypto_cache_ttl_seconds: int = 30  # 30 seconds
    
    # Provider configurations
    news_providers: Dict[str, FeedProviderConfig] = None
    markets_providers: Dict[str, FeedProviderConfig] = None
    
    # Feature flags
    keyless_fallbacks_enabled: bool = True
    
    def __post_init__(self):
        """Initialize provider configurations after dataclass creation"""
        if self.news_providers is None:
            self.news_providers = {}
        if self.markets_providers is None:
            self.markets_providers = {}
        self._load_provider_configurations()
        self._log_configuration_status()
    
    def _load_provider_configurations(self):
        """Load provider configurations using canonical env keys only"""
        
        # News Providers
        self.news_providers = {
            "guardian": FeedProviderConfig(
                name="Guardian Open Platform",
                env_key="GUARDIAN_OPEN_PLATFORM_KEY",
                is_configured=is_provider_available("GUARDIAN_OPEN_PLATFORM_KEY"),
                is_required=True,  # Required for news lane
                timeout_ms=self.provider_timeout_ms,
                cache_ttl_seconds=self.news_cache_ttl_seconds
            ),
            "newsapi": FeedProviderConfig(
                name="NewsAPI",
                env_key="NEWSAPI_KEY",
                is_configured=is_provider_available("NEWSAPI_KEY"),
                is_required=True,  # Required for news lane
                timeout_ms=self.provider_timeout_ms,
                cache_ttl_seconds=self.news_cache_ttl_seconds
            ),
            "gdelt": FeedProviderConfig(
                name="GDELT 2.1 API",
                env_key=None,  # Keyless
                is_configured=True,  # Always available
                is_required=False,
                timeout_ms=self.provider_timeout_ms,
                cache_ttl_seconds=self.news_cache_ttl_seconds
            ),
            "hn_algolia": FeedProviderConfig(
                name="Hacker News Algolia",
                env_key=None,  # Keyless
                is_configured=True,  # Always available
                is_required=False,
                timeout_ms=self.provider_timeout_ms,
                cache_ttl_seconds=self.news_cache_ttl_seconds
            ),
            "rss": FeedProviderConfig(
                name="RSS Feeds",
                env_key=None,  # Keyless
                is_configured=True,  # Always available
                is_required=False,
                timeout_ms=self.provider_timeout_ms,
                cache_ttl_seconds=self.news_cache_ttl_seconds
            )
        }
        
        # Markets Providers
        self.markets_providers = {
            "alphavantage": FeedProviderConfig(
                name="Alpha Vantage",
                env_key="ALPHAVANTAGE_KEY",
                is_configured=is_provider_available("ALPHAVANTAGE_KEY"),
                is_required=True,  # Required for markets lane
                timeout_ms=self.provider_timeout_ms,
                cache_ttl_seconds=self.markets_cache_ttl_seconds
            ),
            "finnhub": FeedProviderConfig(
                name="Finnhub",
                env_key="FINNHUB_KEY",
                is_configured=is_provider_available("FINNHUB_KEY"),
                is_required=True,  # Required for markets lane
                timeout_ms=self.provider_timeout_ms,
                cache_ttl_seconds=self.markets_cache_ttl_seconds
            ),
            "fmp": FeedProviderConfig(
                name="Financial Modeling Prep",
                env_key="FMP_API_KEY",
                is_configured=is_provider_available("FMP_API_KEY"),
                is_required=True,  # Required for markets lane
                timeout_ms=self.provider_timeout_ms,
                cache_ttl_seconds=self.markets_cache_ttl_seconds
            ),
            "stooq": FeedProviderConfig(
                name="Stooq CSV",
                env_key=None,  # Keyless
                is_configured=True,  # Always available
                is_required=False,
                timeout_ms=self.provider_timeout_ms,
                cache_ttl_seconds=self.markets_cache_ttl_seconds
            ),
            "sec_edgar": FeedProviderConfig(
                name="SEC EDGAR",
                env_key=None,  # Keyless
                is_configured=True,  # Always available
                is_required=False,
                timeout_ms=self.provider_timeout_ms,
                cache_ttl_seconds=self.markets_cache_ttl_seconds
            )
        }
        
        # Get keyless fallbacks setting
        self.keyless_fallbacks_enabled = provider_config.keyless_fallbacks_enabled
    
    def _log_configuration_status(self):
        """Log the configuration status"""
        logger.info(f"Feeds Service Configuration:")
        logger.info(f"  Keyless Fallbacks: {self.keyless_fallbacks_enabled}")
        logger.info(f"  Provider Timeout: {self.provider_timeout_ms}ms")
        
        logger.info("  News Providers:")
        for provider_name, provider_config in self.news_providers.items():
            status = "✅" if provider_config.is_configured else "❌" if provider_config.is_required else "⚠️"
            logger.info(f"    {status} {provider_config.name}: {'Configured' if provider_config.is_configured else 'Not configured'}")
        
        logger.info("  Markets Providers:")
        for provider_name, provider_config in self.markets_providers.items():
            status = "✅" if provider_config.is_configured else "❌" if provider_config.is_required else "⚠️"
            logger.info(f"    {status} {provider_config.name}: {'Configured' if provider_config.is_configured else 'Not configured'}")
        
        # Log provider status
        log_provider_status()
    
    def get_news_providers(self) -> Dict[str, FeedProviderConfig]:
        """Get news provider configurations"""
        return self.news_providers
    
    def get_markets_providers(self) -> Dict[str, FeedProviderConfig]:
        """Get markets provider configurations"""
        return self.markets_providers
    
    def get_configured_news_providers(self) -> List[str]:
        """Get list of configured news providers"""
        return [name for name, config in self.news_providers.items() if config.is_configured]
    
    def get_configured_markets_providers(self) -> List[str]:
        """Get list of configured markets providers"""
        return [name for name, config in self.markets_providers.items() if config.is_configured]
    
    def get_news_provider_order(self) -> List[str]:
        """Get news provider order (primary → fallback → keyless)"""
        provider_order = []
        
        # Add configured providers first
        for provider_name, provider_config in self.news_providers.items():
            if provider_config.is_configured and provider_config.env_key:
                provider_order.append(provider_name)
        
        # Add keyless providers if enabled
        if self.keyless_fallbacks_enabled:
            for provider_name, provider_config in self.news_providers.items():
                if not provider_config.env_key and provider_name not in provider_order:
                    provider_order.append(provider_name)
        
        return provider_order
    
    def get_markets_provider_order(self) -> List[str]:
        """Get markets provider order (primary → fallback → keyless)"""
        provider_order = []
        
        # Add configured providers first
        for provider_name, provider_config in self.markets_providers.items():
            if provider_config.is_configured and provider_config.env_key:
                provider_order.append(provider_name)
        
        # Add keyless providers if enabled
        if self.keyless_fallbacks_enabled:
            for provider_name, provider_config in self.markets_providers.items():
                if not provider_config.env_key and provider_name not in provider_order:
                    provider_order.append(provider_name)
        
        return provider_order
    
    def is_news_available(self) -> bool:
        """Check if news feeds are available"""
        return len(self.get_configured_news_providers()) > 0 or self.keyless_fallbacks_enabled
    
    def is_markets_available(self) -> bool:
        """Check if markets feeds are available"""
        return len(self.get_configured_markets_providers()) > 0 or self.keyless_fallbacks_enabled
    
    def get_provider_api_key(self, provider_name: str, feed_type: str) -> Optional[str]:
        """Get API key for a specific provider"""
        if feed_type == "news":
            provider_config = self.news_providers.get(provider_name)
        elif feed_type == "markets":
            provider_config = self.markets_providers.get(provider_name)
        else:
            return None
        
        if provider_config and provider_config.env_key:
            return get_provider_key(provider_config.env_key)
        return None
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get service health status"""
        configured_news = self.get_configured_news_providers()
        configured_markets = self.get_configured_markets_providers()
        
        return {
            "service": self.service_name,
            "status": "healthy" if (configured_news or configured_markets) else "degraded",
            "news": {
                "available": self.is_news_available(),
                "configured_providers": configured_news,
                "provider_order": self.get_news_provider_order(),
                "keyless_fallbacks": self.keyless_fallbacks_enabled
            },
            "markets": {
                "available": self.is_markets_available(),
                "configured_providers": configured_markets,
                "provider_order": self.get_markets_provider_order(),
                "keyless_fallbacks": self.keyless_fallbacks_enabled
            },
            "cache_ttls": {
                "news_seconds": self.news_cache_ttl_seconds,
                "markets_seconds": self.markets_cache_ttl_seconds,
                "crypto_seconds": self.crypto_cache_ttl_seconds
            },
            "provider_timeout_ms": self.provider_timeout_ms
        }

# Global configuration instance
config = FeedsConfig()

# Convenience functions
def get_config() -> FeedsConfig:
    """Get the global configuration instance"""
    return config

def get_news_providers() -> Dict[str, FeedProviderConfig]:
    """Get news provider configurations"""
    return config.get_news_providers()

def get_markets_providers() -> Dict[str, FeedProviderConfig]:
    """Get markets provider configurations"""
    return config.get_markets_providers()

def get_configured_news_providers() -> List[str]:
    """Get list of configured news providers"""
    return config.get_configured_news_providers()

def get_configured_markets_providers() -> List[str]:
    """Get list of configured markets providers"""
    return config.get_configured_markets_providers()

def get_news_provider_order() -> List[str]:
    """Get news provider order"""
    return config.get_news_provider_order()

def get_markets_provider_order() -> List[str]:
    """Get markets provider order"""
    return config.get_markets_provider_order()

def is_news_available() -> bool:
    """Check if news feeds are available"""
    return config.is_news_available()

def is_markets_available() -> bool:
    """Check if markets feeds are available"""
    return config.is_markets_available()

def get_provider_api_key(provider_name: str, feed_type: str) -> Optional[str]:
    """Get API key for a specific provider"""
    return config.get_provider_api_key(provider_name, feed_type)
