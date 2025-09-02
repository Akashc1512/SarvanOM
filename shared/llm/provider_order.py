#!/usr/bin/env python3
"""
Centralized LLM Provider Order System

This module provides a single source of truth for LLM provider ordering
across the entire SarvanOM system. It implements the free-first fallback
strategy and ensures consistent provider selection behavior.

Key Features:
- Centralized provider order configuration
- Environment-driven provider availability
- Free-first fallback strategy
- Provider health monitoring
- Dynamic provider selection based on query complexity
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from functools import lru_cache

logger = logging.getLogger(__name__)

class LLMProvider(str, Enum):
    """Enumeration of available LLM providers."""
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL_STUB = "local_stub"

class QueryComplexity(str, Enum):
    """Query complexity levels for provider selection."""
    SIMPLE = "simple"      # Fast, basic queries
    STANDARD = "standard"  # Normal queries
    COMPLEX = "complex"    # Reasoning, analysis
    EXPERT = "expert"      # Tool use, long context

@dataclass
class ProviderConfig:
    """Configuration for a specific LLM provider."""
    name: LLMProvider
    priority: int
    is_free: bool
    max_tokens: int
    supports_streaming: bool
    supports_tools: bool
    avg_latency_ms: int
    cost_per_1k_tokens: float

class ProviderRegistry:
    """Centralized registry for LLM providers with ordering and fallback logic."""
    
    def __init__(self):
        self.providers: Dict[LLMProvider, ProviderConfig] = self._initialize_providers()
        self._base_order: List[LLMProvider] = self._get_base_order()
        self._free_first_order: List[LLMProvider] = self._get_free_first_order()
    
    def _initialize_providers(self) -> Dict[LLMProvider, ProviderConfig]:
        """Initialize provider configurations."""
        return {
            LLMProvider.OLLAMA: ProviderConfig(
                name=LLMProvider.OLLAMA,
                priority=1,
                is_free=True,
                max_tokens=8192,
                supports_streaming=True,
                supports_tools=False,
                avg_latency_ms=2000,
                cost_per_1k_tokens=0.0
            ),
            LLMProvider.HUGGINGFACE: ProviderConfig(
                name=LLMProvider.HUGGINGFACE,
                priority=2,
                is_free=True,
                max_tokens=4096,
                supports_streaming=True,
                supports_tools=False,
                avg_latency_ms=3000,
                cost_per_1k_tokens=0.0
            ),
            LLMProvider.OPENAI: ProviderConfig(
                name=LLMProvider.OPENAI,
                priority=3,
                is_free=False,
                max_tokens=128000,
                supports_streaming=True,
                supports_tools=True,
                avg_latency_ms=800,
                cost_per_1k_tokens=0.01
            ),
            LLMProvider.ANTHROPIC: ProviderConfig(
                name=LLMProvider.ANTHROPIC,
                priority=4,
                is_free=False,
                max_tokens=200000,
                supports_streaming=True,
                supports_tools=True,
                avg_latency_ms=1200,
                cost_per_1k_tokens=0.015
            ),
            LLMProvider.LOCAL_STUB: ProviderConfig(
                name=LLMProvider.LOCAL_STUB,
                priority=5,
                is_free=True,
                max_tokens=4096,
                supports_streaming=False,
                supports_tools=False,
                avg_latency_ms=100,
                cost_per_1k_tokens=0.0
            )
        }
    
    def _get_base_order(self) -> List[LLMProvider]:
        """Get the base provider order from environment or use defaults."""
        env_order = os.getenv("LLM_PROVIDER_ORDER")
        if env_order:
            try:
                # Parse comma-separated provider names
                provider_names = [name.strip().lower() for name in env_order.split(",")]
                providers = []
                for name in provider_names:
                    try:
                        provider = LLMProvider(name)
                        providers.append(provider)
                    except ValueError:
                        logger.warning(f"Unknown provider in LLM_PROVIDER_ORDER: {name}")
                
                if providers:
                    logger.info(f"Using custom provider order: {[p.value for p in providers]}")
                    return providers
            except Exception as e:
                logger.error(f"Failed to parse LLM_PROVIDER_ORDER: {e}")
        
        # Default order: free-first, then paid
        default_order = [
            LLMProvider.OLLAMA,
            LLMProvider.HUGGINGFACE,
            LLMProvider.OPENAI,
            LLMProvider.ANTHROPIC,
            LLMProvider.LOCAL_STUB
        ]
        logger.info(f"Using default provider order: {[p.value for p in default_order]}")
        return default_order
    
    def _get_free_first_order(self) -> List[LLMProvider]:
        """Get provider order optimized for free-first strategy."""
        free_providers = [p for p in self._base_order if self.providers[p].is_free]
        paid_providers = [p for p in self._base_order if not self.providers[p].is_free]
        
        # Free providers first, then paid providers
        return free_providers + paid_providers
    
    def get_provider_order(self, prefer_free: bool = True) -> List[LLMProvider]:
        """
        Get the ordered list of providers.
        
        Args:
            prefer_free: If True, prioritize free providers
            
        Returns:
            List of providers in priority order
        """
        if prefer_free:
            return self._free_first_order.copy()
        return self._base_order.copy()
    
    def get_available_providers(self, prefer_free: bool = True) -> List[LLMProvider]:
        """
        Get list of available providers based on environment configuration.
        
        Args:
            prefer_free: If True, prioritize free providers
            
        Returns:
            List of available providers in priority order
        """
        order = self.get_provider_order(prefer_free)
        available = []
        
        for provider in order:
            if self._is_provider_available(provider):
                available.append(provider)
        
        return available
    
    def _is_provider_available(self, provider: LLMProvider) -> bool:
        """
        Check if a provider is available based on environment configuration.
        
        Args:
            provider: The provider to check
            
        Returns:
            True if provider is available, False otherwise
        """
        if provider == LLMProvider.LOCAL_STUB:
            return True  # Always available as fallback
        
        if provider == LLMProvider.OLLAMA:
            return self._check_ollama_availability()
        
        if provider == LLMProvider.HUGGINGFACE:
            return self._check_huggingface_availability()
        
        if provider == LLMProvider.OPENAI:
            return self._check_openai_availability()
        
        if provider == LLMProvider.ANTHROPIC:
            return self._check_anthropic_availability()
        
        return False
    
    def _check_ollama_availability(self) -> bool:
        """Check if Ollama is available."""
        # Check if Ollama is enabled and base URL is set
        ollama_enabled = os.getenv("OLLAMA_ENABLED", "true").lower() == "true"
        ollama_base_url = os.getenv("OLLAMA_BASE_URL")
        
        if not ollama_enabled:
            return False
        
        if not ollama_base_url:
            logger.warning("Ollama enabled but OLLAMA_BASE_URL not set")
            return False
        
        return True
    
    def _check_huggingface_availability(self) -> bool:
        """Check if HuggingFace is available."""
        # Check if HuggingFace API token is set
        hf_token = os.getenv("HUGGINGFACE_WRITE_TOKEN")
        
        if not hf_token:
            logger.debug("HuggingFace not available: HUGGINGFACE_WRITE_TOKEN not set")
            return False
        
        return True
    
    def _check_openai_availability(self) -> bool:
        """Check if OpenAI is available."""
        # Check if OpenAI API key is set
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if not openai_key:
            logger.debug("OpenAI not available: OPENAI_API_KEY not set")
            return False
        
        return True
    
    def _check_anthropic_availability(self) -> bool:
        """Check if Anthropic is available."""
        # Check if Anthropic API key is set
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not anthropic_key:
            logger.debug("Anthropic not available: ANTHROPIC_API_KEY not set")
            return False
        
        return True
    
    def select_provider_for_complexity(
        self, 
        complexity: QueryComplexity, 
        prefer_free: bool = True
    ) -> Optional[LLMProvider]:
        """
        Select the best provider for a given query complexity.
        
        Args:
            complexity: The complexity level of the query
            prefer_free: If True, prioritize free providers
            
        Returns:
            The selected provider or None if none available
        """
        available_providers = self.get_available_providers(prefer_free)
        
        if not available_providers:
            logger.warning("No providers available")
            return None
        
        # Simple selection strategy based on complexity
        if complexity == QueryComplexity.SIMPLE:
            # For simple queries, prefer fast providers
            fast_providers = [p for p in available_providers 
                            if self.providers[p].avg_latency_ms <= 1000]
            if fast_providers:
                return fast_providers[0]
        
        elif complexity == QueryComplexity.EXPERT:
            # For expert queries, prefer providers with tool support
            tool_providers = [p for p in available_providers 
                            if self.providers[p].supports_tools]
            if tool_providers:
                return tool_providers[0]
        
        # Default: return first available provider
        return available_providers[0]
    
    def get_provider_info(self, provider: LLMProvider) -> Optional[ProviderConfig]:
        """Get configuration information for a specific provider."""
        return self.providers.get(provider)
    
    def get_provider_stats(self) -> Dict[str, any]:
        """Get statistics about all providers."""
        stats = {
            "total_providers": len(self.providers),
            "free_providers": len([p for p in self.providers.values() if p.is_free]),
            "paid_providers": len([p for p in self.providers.values() if not p.is_free]),
            "available_providers": len(self.get_available_providers()),
            "base_order": [p.value for p in self._base_order],
            "free_first_order": [p.value for p in self._free_first_order]
        }
        
        # Add per-provider availability
        for provider in self.providers:
            stats[f"{provider.value}_available"] = self._is_provider_available(provider)
        
        return stats

# Global registry instance
_provider_registry: Optional[ProviderRegistry] = None

def get_provider_registry() -> ProviderRegistry:
    """Get the global provider registry instance."""
    global _provider_registry
    if _provider_registry is None:
        _provider_registry = ProviderRegistry()
    return _provider_registry

@lru_cache(maxsize=1)
def get_provider_order(prefer_free: bool = True) -> List[str]:
    """
    Get the ordered list of provider names.
    
    This is the main function that other modules should use.
    
    Args:
        prefer_free: If True, prioritize free providers
        
    Returns:
        List of provider names in priority order
    """
    registry = get_provider_registry()
    providers = registry.get_provider_order(prefer_free)
    return [p.value for p in providers]

@lru_cache(maxsize=1)
def get_available_providers(prefer_free: bool = True) -> List[str]:
    """
    Get list of available provider names.
    
    Args:
        prefer_free: If True, prioritize free providers
        
    Returns:
        List of available provider names in priority order
    """
    registry = get_provider_registry()
    providers = registry.get_available_providers(prefer_free)
    return [p.value for p in providers]

def select_provider_for_complexity(
    complexity: QueryComplexity, 
    prefer_free: bool = True
) -> Optional[str]:
    """
    Select the best provider for a given query complexity.
    
    Args:
        complexity: The complexity level of the query
        prefer_free: If True, prioritize free providers
        
    Returns:
        The selected provider name or None if none available
    """
    registry = get_provider_registry()
    provider = registry.select_provider_for_complexity(complexity, prefer_free)
    return provider.value if provider else None

def get_provider_stats() -> Dict[str, any]:
    """Get statistics about all providers."""
    registry = get_provider_registry()
    return registry.get_provider_stats()

# Export main functions
__all__ = [
    "LLMProvider",
    "QueryComplexity",
    "ProviderConfig",
    "ProviderRegistry",
    "get_provider_registry",
    "get_provider_order",
    "get_available_providers",
    "select_provider_for_complexity",
    "get_provider_stats"
]
