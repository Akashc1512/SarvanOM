"""
Retrieval Service Configuration - SarvanOM v2

Configuration module for the Retrieval service that reads only canonical
environment variable names and implements safe fallbacks.

Features:
    - Canonical environment variable names only
    - Fail-fast for required providers
    - Safe fallbacks for optional providers
    - Lane-specific provider configurations
    - Integration with centralized provider config
"""

import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import structlog

# Import the centralized provider configuration
from sarvanom.shared.core.config.provider_config import (
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
class LaneProviderConfig:
    """Configuration for a lane's providers"""
    name: str
    primary_providers: List[str]
    fallback_providers: List[str]
    keyless_fallbacks: List[str]
    is_required: bool
    budget_ms: int
    provider_timeout_ms: int = 800

@dataclass
class RetrievalConfig:
    """Configuration for Retrieval service"""
    
    # Service settings
    service_name: str = "retrieval"
    port: int = 8004
    metrics_port: int = 8005
    
    # Budget allocations (from docs/retrieval/lanes.md)
    simple_budget_ms: int = 5000
    technical_budget_ms: int = 7000
    research_budget_ms: int = 10000
    multimedia_budget_ms: int = 10000
    
    # Provider timeout budget
    provider_timeout_ms: int = 800
    
    # Lane configurations
    lanes: Dict[str, LaneProviderConfig] = None
    
    # Feature flags
    keyless_fallbacks_enabled: bool = True
    
    def __post_init__(self):
        """Initialize lane configurations after dataclass creation"""
        if self.lanes is None:
            self.lanes = {}
        self._load_lane_configurations()
        self._log_configuration_status()
    
    def _load_lane_configurations(self):
        """Load lane configurations using canonical env keys only"""
        
        # Web Search Lane (Brave → SerpAPI → Keyless)
        web_providers = get_lane_providers("web_search")
        web_keyless = get_lane_keyless_fallbacks("web_search")
        self.lanes["web"] = LaneProviderConfig(
            name="Web Search",
            primary_providers=web_providers,
            fallback_providers=web_providers,  # Same as primary for now
            keyless_fallbacks=web_keyless,
            is_required=True,
            budget_ms=2000,  # 2s for web search
            provider_timeout_ms=self.provider_timeout_ms
        )
        
        # News Lane (Guardian → NewsAPI → Keyless)
        news_providers = get_lane_providers("news")
        news_keyless = get_lane_keyless_fallbacks("news")
        self.lanes["news"] = LaneProviderConfig(
            name="News",
            primary_providers=news_providers,
            fallback_providers=news_providers,
            keyless_fallbacks=news_keyless,
            is_required=True,
            budget_ms=1500,  # 1.5s for news
            provider_timeout_ms=self.provider_timeout_ms
        )
        
        # Markets Lane (Alpha Vantage → Finnhub/FMP → Keyless)
        markets_providers = get_lane_providers("markets")
        markets_keyless = get_lane_keyless_fallbacks("markets")
        self.lanes["markets"] = LaneProviderConfig(
            name="Markets",
            primary_providers=markets_providers,
            fallback_providers=markets_providers,
            keyless_fallbacks=markets_keyless,
            is_required=True,
            budget_ms=1000,  # 1s for markets
            provider_timeout_ms=self.provider_timeout_ms
        )
        
        # Vector Lane (Qdrant)
        vector_providers = get_lane_providers("vector")
        vector_keyless = get_lane_keyless_fallbacks("vector")
        self.lanes["vector"] = LaneProviderConfig(
            name="Vector Search",
            primary_providers=vector_providers,
            fallback_providers=vector_providers,
            keyless_fallbacks=vector_keyless,
            is_required=False,  # Can work without API key
            budget_ms=1500,  # 1.5s for vector
            provider_timeout_ms=self.provider_timeout_ms
        )
        
        # Keyword Lane (Meilisearch)
        keyword_providers = get_lane_providers("keyword")
        keyword_keyless = get_lane_keyless_fallbacks("keyword")
        self.lanes["keyword"] = LaneProviderConfig(
            name="Keyword Search",
            primary_providers=keyword_providers,
            fallback_providers=keyword_providers,
            keyless_fallbacks=keyword_keyless,
            is_required=False,  # Can work without API key
            budget_ms=1000,  # 1s for keyword
            provider_timeout_ms=self.provider_timeout_ms
        )
        
        # Knowledge Graph Lane (ArangoDB)
        kg_providers = get_lane_providers("knowledge_graph")
        kg_keyless = get_lane_keyless_fallbacks("knowledge_graph")
        self.lanes["knowledge_graph"] = LaneProviderConfig(
            name="Knowledge Graph",
            primary_providers=kg_providers,
            fallback_providers=kg_providers,
            keyless_fallbacks=kg_keyless,
            is_required=True,  # Requires database credentials
            budget_ms=2000,  # 2s for KG
            provider_timeout_ms=self.provider_timeout_ms
        )
        
        # Get keyless fallbacks setting
        self.keyless_fallbacks_enabled = provider_config.keyless_fallbacks_enabled
    
    def _log_configuration_status(self):
        """Log the configuration status"""
        logger.info(f"Retrieval Service Configuration:")
        logger.info(f"  Keyless Fallbacks: {self.keyless_fallbacks_enabled}")
        logger.info(f"  Provider Timeout: {self.provider_timeout_ms}ms")
        
        for lane_name, lane_config in self.lanes.items():
            logger.info(f"  {lane_config.name}:")
            logger.info(f"    Primary Providers: {lane_config.primary_providers}")
            logger.info(f"    Keyless Fallbacks: {lane_config.keyless_fallbacks}")
            logger.info(f"    Budget: {lane_config.budget_ms}ms")
            logger.info(f"    Required: {lane_config.is_required}")
        
        # Log provider status
        log_provider_status()
    
    def get_lane_config(self, lane_name: str) -> Optional[LaneProviderConfig]:
        """Get configuration for a specific lane"""
        return self.lanes.get(lane_name)
    
    def get_available_lanes(self) -> List[str]:
        """Get list of available lanes (with configured providers or keyless fallbacks)"""
        available_lanes = []
        
        for lane_name, lane_config in self.lanes.items():
            has_providers = len(lane_config.primary_providers) > 0
            has_keyless = len(lane_config.keyless_fallbacks) > 0 and self.keyless_fallbacks_enabled
            
            if has_providers or has_keyless:
                available_lanes.append(lane_name)
        
        return available_lanes
    
    def get_lane_provider_order(self, lane_name: str) -> List[str]:
        """Get provider order for a lane (primary → fallback → keyless)"""
        lane_config = self.lanes.get(lane_name)
        if not lane_config:
            return []
        
        provider_order = []
        
        # Add primary providers
        provider_order.extend(lane_config.primary_providers)
        
        # Add fallback providers (excluding already added)
        for provider in lane_config.fallback_providers:
            if provider not in provider_order:
                provider_order.append(provider)
        
        # Add keyless fallbacks if enabled
        if self.keyless_fallbacks_enabled:
            provider_order.extend(lane_config.keyless_fallbacks)
        
        return provider_order
    
    def get_budget_for_complexity(self, complexity: str) -> int:
        """Get budget for query complexity"""
        budget_map = {
            "simple": self.simple_budget_ms,
            "technical": self.technical_budget_ms,
            "research": self.research_budget_ms,
            "multimedia": self.multimedia_budget_ms
        }
        return budget_map.get(complexity, self.simple_budget_ms)
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get service health status"""
        available_lanes = self.get_available_lanes()
        
        lane_health = {}
        for lane_name, lane_config in self.lanes.items():
            has_providers = len(lane_config.primary_providers) > 0
            has_keyless = len(lane_config.keyless_fallbacks) > 0 and self.keyless_fallbacks_enabled
            
            lane_health[lane_name] = {
                "available": has_providers or has_keyless,
                "has_providers": has_providers,
                "has_keyless": has_keyless,
                "required": lane_config.is_required,
                "providers": lane_config.primary_providers,
                "keyless_fallbacks": lane_config.keyless_fallbacks
            }
        
        return {
            "service": self.service_name,
            "status": "healthy" if len(available_lanes) > 0 else "degraded",
            "available_lanes": available_lanes,
            "lane_health": lane_health,
            "keyless_fallbacks_enabled": self.keyless_fallbacks_enabled,
            "budget_allocations": {
                "simple_ms": self.simple_budget_ms,
                "technical_ms": self.technical_budget_ms,
                "research_ms": self.research_budget_ms,
                "multimedia_ms": self.multimedia_budget_ms
            },
            "provider_timeout_ms": self.provider_timeout_ms
        }

# Global configuration instance
config = RetrievalConfig()

# Convenience functions
def get_config() -> RetrievalConfig:
    """Get the global configuration instance"""
    return config

def get_lane_config(lane_name: str) -> Optional[LaneProviderConfig]:
    """Get configuration for a specific lane"""
    return config.get_lane_config(lane_name)

def get_available_lanes() -> List[str]:
    """Get list of available lanes"""
    return config.get_available_lanes()

def get_lane_provider_order(lane_name: str) -> List[str]:
    """Get provider order for a lane"""
    return config.get_lane_provider_order(lane_name)

def get_budget_for_complexity(complexity: str) -> int:
    """Get budget for query complexity"""
    return config.get_budget_for_complexity(complexity)

def is_lane_available(lane_name: str) -> bool:
    """Check if a lane is available"""
    return lane_name in config.get_available_lanes()
