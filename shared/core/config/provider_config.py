"""
Provider Configuration Module - SarvanOM v2

Centralized configuration for all provider API keys and settings.
Implements fail-fast for required providers and safe fallbacks for optional ones.
Reads only the canonical environment variable names as specified in the contract.

Features:
    - Canonical environment variable names only
    - Fail-fast for required providers
    - Safe fallbacks for optional providers
    - KEYLESS_FALLBACKS_ENABLED feature flag
    - Clear logging for unconfigured providers
    - Provider health status tracking

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import os
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)

class ProviderStatus(str, Enum):
    """Provider configuration status"""
    CONFIGURED = "configured"
    NOT_CONFIGURED = "not_configured"
    REQUIRED_MISSING = "required_missing"
    FALLBACK_AVAILABLE = "fallback_available"

@dataclass
class ProviderConfig:
    """Configuration for a single provider"""
    name: str
    env_key: str
    value: Optional[str]
    status: ProviderStatus
    is_required: bool
    fallback_providers: List[str]
    description: str

@dataclass
class LaneConfig:
    """Configuration for a retrieval lane"""
    name: str
    required_providers: List[str]
    fallback_providers: List[str]
    keyless_fallbacks: List[str]
    is_required: bool

class ProviderConfigurationManager:
    """Manages provider configuration across all services"""
    
    # Canonical environment variable names (no synonyms, no renames)
    CANONICAL_ENV_KEYS = {
        # News & Search Providers
        "GUARDIAN_OPEN_PLATFORM_KEY": "Guardian Open Platform API key",
        "FINNHUB_KEY": "Finnhub API key", 
        "ALPHAVANTAGE_KEY": "Alpha Vantage API key",
        "NEWSAPI_KEY": "NewsAPI key",
        "FMP_API_KEY": "Financial Modeling Prep API key",
        
        # AI Provider Keys
        "OPENAI_API_KEY": "OpenAI API key",
        "ANTHROPIC_API_KEY": "Anthropic API key", 
        "HUGGINGFACE_WRITE_TOKEN": "HuggingFace write token",
        "HUGGINGFACE_READ_TOKEN": "HuggingFace read token",
        "HUGGINGFACE_API_KEY": "HuggingFace API key",
        
        # Search & Database Keys
        "QDRANT_API_KEY": "Qdrant API key",
        "BRAVE_SEARCH_API_KEY": "Brave Search API key",
        "SERPAPI_KEY": "SerpAPI key",
        "GEMINI_API_KEY": "Google Gemini API key",
        "YOUTUBE_API_KEY": "YouTube Data API key",
        "MEILI_MASTER_KEY": "Meilisearch master key",
        
        # Database Credentials
        "ARANGO_USERNAME": "ArangoDB username",
        "ARANGO_PASSWORD": "ArangoDB password", 
        "ARANGO_DATABASE": "ArangoDB database name"
    }
    
    # Lane configurations based on docs/retrieval/lanes.md
    LANE_CONFIGS = {
        "web_search": LaneConfig(
            name="Web Search",
            required_providers=["BRAVE_SEARCH_API_KEY", "SERPAPI_KEY"],  # At least one required
            fallback_providers=["BRAVE_SEARCH_API_KEY", "SERPAPI_KEY"],
            keyless_fallbacks=["DuckDuckGo IA", "Wikipedia API", "StackExchange API", "MDN"],
            is_required=True
        ),
        "news": LaneConfig(
            name="News",
            required_providers=["GUARDIAN_OPEN_PLATFORM_KEY", "NEWSAPI_KEY"],  # At least one required
            fallback_providers=["GUARDIAN_OPEN_PLATFORM_KEY", "NEWSAPI_KEY"],
            keyless_fallbacks=["GDELT 2.1 API", "Hacker News Algolia", "curated RSS"],
            is_required=True
        ),
        "markets": LaneConfig(
            name="Markets",
            required_providers=["ALPHAVANTAGE_KEY", "FINNHUB_KEY", "FMP_API_KEY"],  # At least one required
            fallback_providers=["ALPHAVANTAGE_KEY", "FINNHUB_KEY", "FMP_API_KEY"],
            keyless_fallbacks=["Stooq CSV endpoints", "SEC EDGAR basics"],
            is_required=True
        ),
        "vector": LaneConfig(
            name="Vector Search",
            required_providers=["QDRANT_API_KEY"],
            fallback_providers=["QDRANT_API_KEY"],
            keyless_fallbacks=[],
            is_required=False  # Can work without API key if Qdrant is unprotected
        ),
        "keyword": LaneConfig(
            name="Keyword Search", 
            required_providers=["MEILI_MASTER_KEY"],
            fallback_providers=["MEILI_MASTER_KEY"],
            keyless_fallbacks=[],
            is_required=False  # Can work without API key if Meilisearch is unprotected
        ),
        "knowledge_graph": LaneConfig(
            name="Knowledge Graph",
            required_providers=["ARANGO_USERNAME", "ARANGO_PASSWORD", "ARANGO_DATABASE"],
            fallback_providers=["ARANGO_USERNAME", "ARANGO_PASSWORD", "ARANGO_DATABASE"],
            keyless_fallbacks=[],
            is_required=True
        )
    }
    
    def __init__(self):
        self.providers: Dict[str, ProviderConfig] = {}
        self.keyless_fallbacks_enabled = self._get_keyless_fallbacks_setting()
        self._load_provider_configurations()
        self._validate_required_providers()
    
    def _get_keyless_fallbacks_setting(self) -> bool:
        """Get KEYLESS_FALLBACKS_ENABLED setting from existing settings mechanism"""
        # This would integrate with the existing settings system
        # For now, default to True as specified
        return os.getenv("KEYLESS_FALLBACKS_ENABLED", "true").lower() == "true"
    
    def _load_provider_configurations(self):
        """Load all provider configurations from environment variables"""
        for env_key, description in self.CANONICAL_ENV_KEYS.items():
            value = os.getenv(env_key)
            
            # Determine if this provider is required for any lane
            is_required = self._is_provider_required(env_key)
            
            # Determine status
            if value:
                status = ProviderStatus.CONFIGURED
            elif is_required:
                status = ProviderStatus.REQUIRED_MISSING
            else:
                status = ProviderStatus.NOT_CONFIGURED
            
            # Get fallback providers for this provider
            fallback_providers = self._get_fallback_providers(env_key)
            
            self.providers[env_key] = ProviderConfig(
                name=env_key.replace("_", " ").title(),
                env_key=env_key,
                value=value,
                status=status,
                is_required=is_required,
                fallback_providers=fallback_providers,
                description=description
            )
    
    def _is_provider_required(self, env_key: str) -> bool:
        """Check if a provider is required for any lane"""
        for lane_config in self.LANE_CONFIGS.values():
            if env_key in lane_config.required_providers:
                return True
        return False
    
    def _get_fallback_providers(self, env_key: str) -> List[str]:
        """Get fallback providers for a given provider"""
        fallbacks = []
        for lane_config in self.LANE_CONFIGS.values():
            if env_key in lane_config.fallback_providers:
                fallbacks.extend([p for p in lane_config.fallback_providers if p != env_key])
        return list(set(fallbacks))  # Remove duplicates
    
    def _validate_required_providers(self):
        """Validate that all required providers are configured"""
        missing_required = []
        
        for lane_name, lane_config in self.LANE_CONFIGS.items():
            if not lane_config.is_required:
                continue
                
            # Check if at least one required provider is configured
            has_configured_provider = False
            for provider_key in lane_config.required_providers:
                if provider_key in self.providers and self.providers[provider_key].value:
                    has_configured_provider = True
                    break
            
            if not has_configured_provider:
                missing_required.append(lane_name)
        
        if missing_required:
            error_msg = f"Required providers missing for lanes: {', '.join(missing_required)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def get_provider_config(self, env_key: str) -> Optional[ProviderConfig]:
        """Get configuration for a specific provider"""
        return self.providers.get(env_key)
    
    def get_provider_value(self, env_key: str) -> Optional[str]:
        """Get the value for a specific provider"""
        config = self.providers.get(env_key)
        return config.value if config else None
    
    def is_provider_configured(self, env_key: str) -> bool:
        """Check if a provider is configured"""
        config = self.providers.get(env_key)
        return config is not None and config.value is not None
    
    def get_lane_config(self, lane_name: str) -> Optional[LaneConfig]:
        """Get configuration for a specific lane"""
        return self.LANE_CONFIGS.get(lane_name)
    
    def get_configured_providers_for_lane(self, lane_name: str) -> List[str]:
        """Get list of configured providers for a lane"""
        lane_config = self.LANE_CONFIGS.get(lane_name)
        if not lane_config:
            return []
        
        configured_providers = []
        for provider_key in lane_config.required_providers + lane_config.fallback_providers:
            if self.is_provider_configured(provider_key):
                configured_providers.append(provider_key)
        
        return configured_providers
    
    def get_keyless_fallbacks_for_lane(self, lane_name: str) -> List[str]:
        """Get keyless fallbacks for a lane"""
        lane_config = self.LANE_CONFIGS.get(lane_name)
        if not lane_config or not self.keyless_fallbacks_enabled:
            return []
        return lane_config.keyless_fallbacks
    
    def log_provider_status(self):
        """Log the status of all providers and fail-fast for required missing providers"""
        logger.info("Provider Configuration Status:")
        
        required_missing = []
        
        for env_key, config in self.providers.items():
            if config.status == ProviderStatus.CONFIGURED:
                logger.info(f"✅ {config.name}: Configured")
            elif config.status == ProviderStatus.REQUIRED_MISSING:
                logger.error(f"❌ {config.name}: REQUIRED - Missing")
                required_missing.append(config.name)
            else:
                if self.keyless_fallbacks_enabled:
                    logger.info(f"⚠️  {config.name}: Not configured → will use keyless fallbacks")
                else:
                    logger.warning(f"⚠️  {config.name}: Not configured")
        
        # Fail-fast for required missing providers
        if required_missing:
            error_msg = f"Required providers not configured: {', '.join(required_missing)}. Service cannot start without these providers."
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def get_provider_summary(self) -> Dict[str, Any]:
        """Get a summary of all provider configurations"""
        summary = {
            "keyless_fallbacks_enabled": self.keyless_fallbacks_enabled,
            "total_providers": len(self.providers),
            "configured_providers": len([p for p in self.providers.values() if p.value]),
            "required_missing": len([p for p in self.providers.values() if p.status == ProviderStatus.REQUIRED_MISSING]),
            "lanes": {}
        }
        
        for lane_name, lane_config in self.LANE_CONFIGS.items():
            configured_providers = self.get_configured_providers_for_lane(lane_name)
            keyless_fallbacks = self.get_keyless_fallbacks_for_lane(lane_name)
            
            summary["lanes"][lane_name] = {
                "is_required": lane_config.is_required,
                "configured_providers": configured_providers,
                "keyless_fallbacks": keyless_fallbacks,
                "has_configured_provider": len(configured_providers) > 0,
                "can_use_keyless": len(keyless_fallbacks) > 0 and self.keyless_fallbacks_enabled
            }
        
        return summary
    
    def get_active_providers(self) -> Dict[str, List[str]]:
        """Get active providers by lane for frontend display"""
        active_providers = {}
        
        for lane_name in self.LANE_CONFIGS.keys():
            configured_providers = self.get_configured_providers_for_lane(lane_name)
            keyless_fallbacks = self.get_keyless_fallbacks_for_lane(lane_name)
            
            active_providers[lane_name] = {
                "keyed": configured_providers,
                "keyless": keyless_fallbacks,
                "status": "active" if configured_providers or keyless_fallbacks else "inactive"
            }
        
        return active_providers

# Global instance
provider_config = ProviderConfigurationManager()

# Convenience functions for services
def get_provider_key(env_key: str) -> Optional[str]:
    """Get provider API key value"""
    return provider_config.get_provider_value(env_key)

def is_provider_available(env_key: str) -> bool:
    """Check if provider is available"""
    return provider_config.is_provider_configured(env_key)

def get_lane_providers(lane_name: str) -> List[str]:
    """Get configured providers for a lane"""
    return provider_config.get_configured_providers_for_lane(lane_name)

def get_lane_keyless_fallbacks(lane_name: str) -> List[str]:
    """Get keyless fallbacks for a lane"""
    return provider_config.get_keyless_fallbacks_for_lane(lane_name)

def log_provider_status():
    """Log provider status"""
    provider_config.log_provider_status()

def get_provider_summary() -> Dict[str, Any]:
    """Get provider configuration summary"""
    return provider_config.get_provider_summary()

def get_active_providers() -> Dict[str, List[str]]:
    """Get active providers for frontend"""
    return provider_config.get_active_providers()
