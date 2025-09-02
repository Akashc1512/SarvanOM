#!/usr/bin/env python3
"""
Tests for Centralized LLM Provider Order System

This test suite verifies the provider ordering, fallback chains, and
dynamic provider selection functionality.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from shared.llm.provider_order import (
    LLMProvider,
    QueryComplexity,
    ProviderConfig,
    ProviderRegistry,
    get_provider_registry,
    get_provider_order,
    get_available_providers,
    select_provider_for_complexity,
    get_provider_stats
)


class TestProviderRegistry:
    """Test the ProviderRegistry class."""

    def setup_method(self):
        """Set up test environment."""
        # Clear any cached registry
        import shared.llm.provider_order
        shared.llm.provider_order._provider_registry = None
        
    def test_registry_initialization(self):
        """Test registry initializes with correct provider configs."""
        registry = ProviderRegistry()
        
        # Check all providers are registered
        assert len(registry.providers) == 5
        assert LLMProvider.OLLAMA in registry.providers
        assert LLMProvider.HUGGINGFACE in registry.providers
        assert LLMProvider.OPENAI in registry.providers
        assert LLMProvider.ANTHROPIC in registry.providers
        assert LLMProvider.LOCAL_STUB in registry.providers
        
        # Check free providers
        free_providers = [p for p in registry.providers.values() if p.is_free]
        assert len(free_providers) == 3  # Ollama, HuggingFace, LocalStub
        
        # Check paid providers
        paid_providers = [p for p in registry.providers.values() if not p.is_free]
        assert len(paid_providers) == 2  # OpenAI, Anthropic

    def test_default_provider_order(self):
        """Test default provider order is correct."""
        registry = ProviderRegistry()
        
        # Check base order
        base_order = registry._base_order
        expected_order = [
            LLMProvider.OLLAMA,
            LLMProvider.HUGGINGFACE,
            LLMProvider.OPENAI,
            LLMProvider.ANTHROPIC,
            LLMProvider.LOCAL_STUB
        ]
        assert base_order == expected_order

    def test_free_first_order(self):
        """Test free-first ordering prioritizes free providers."""
        registry = ProviderRegistry()
        
        free_first_order = registry._free_first_order
        
        # Check that free providers come first
        free_providers = [p for p in free_first_order if registry.providers[p].is_free]
        paid_providers = [p for p in free_first_order if not registry.providers[p].is_free]
        
        # All free providers should come before all paid providers
        last_free_index = max([free_first_order.index(p) for p in free_providers])
        first_paid_index = min([free_first_order.index(p) for p in paid_providers])
        
        assert last_free_index < first_paid_index

    @patch.dict(os.environ, {"LLM_PROVIDER_ORDER": "openai,anthropic,ollama"})
    def test_custom_provider_order_from_env(self):
        """Test custom provider order from environment variable."""
        registry = ProviderRegistry()
        
        expected_order = [
            LLMProvider.OPENAI,
            LLMProvider.ANTHROPIC,
            LLMProvider.OLLAMA
        ]
        
        # Only the first 3 should match the custom order
        assert registry._base_order[:3] == expected_order

    def test_provider_availability_checks(self):
        """Test provider availability checks."""
        registry = ProviderRegistry()
        
        # Local stub should always be available
        assert registry._is_provider_available(LLMProvider.LOCAL_STUB)

    @patch.dict(os.environ, {}, clear=True)
    def test_no_keys_scenario(self):
        """Test provider selection when no API keys are available."""
        registry = ProviderRegistry()
        
        available = registry.get_available_providers(prefer_free=True)
        
        # Should only include free providers
        for provider in available:
            assert registry.providers[provider].is_free

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_some_keys_scenario(self):
        """Test provider selection when some API keys are available."""
        registry = ProviderRegistry()
        
        available = registry.get_available_providers(prefer_free=False)
        
        # Should include providers with keys
        provider_names = [p.value for p in available]
        # OpenAI should be available since we set the key
        # Local stub should always be available
        assert "local_stub" in provider_names

    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-openai-key",
        "ANTHROPIC_API_KEY": "test-anthropic-key",
        "HUGGINGFACE_WRITE_TOKEN": "test-hf-token",
        "OLLAMA_BASE_URL": "http://localhost:11434"
    })
    def test_all_keys_scenario(self):
        """Test provider selection when all API keys are available."""
        registry = ProviderRegistry()
        
        available = registry.get_available_providers(prefer_free=True)
        
        # Should include all providers
        provider_names = [p.value for p in available]
        assert "openai" in provider_names
        assert "anthropic" in provider_names
        assert "huggingface" in provider_names
        assert "local_stub" in provider_names
        # Ollama depends on service being available, not just URL


class TestProviderSelection:
    """Test provider selection for different query complexities."""

    def setup_method(self):
        """Set up test environment."""
        import shared.llm.provider_order
        shared.llm.provider_order._provider_registry = None

    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-key",
        "ANTHROPIC_API_KEY": "test-key"
    })
    def test_simple_query_provider_selection(self):
        """Test provider selection for simple queries."""
        registry = ProviderRegistry()
        
        provider = registry.select_provider_for_complexity(
            QueryComplexity.SIMPLE, 
            prefer_free=True
        )
        
        # Should prefer fast providers for simple queries
        # Local stub has fastest latency in our config
        assert provider in [LLMProvider.LOCAL_STUB, LLMProvider.OPENAI]

    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-key",
        "ANTHROPIC_API_KEY": "test-key"
    })
    def test_expert_query_provider_selection(self):
        """Test provider selection for expert queries."""
        registry = ProviderRegistry()
        
        provider = registry.select_provider_for_complexity(
            QueryComplexity.EXPERT, 
            prefer_free=False  # Allow paid providers for expert queries
        )
        
        # Should prefer providers with tool support for expert queries
        if provider:
            config = registry.get_provider_info(provider)
            # For expert queries, should prioritize tool-supporting providers
            assert config.supports_tools or provider == LLMProvider.LOCAL_STUB

    def test_no_providers_available(self):
        """Test behavior when no providers are available."""
        with patch.dict(os.environ, {}, clear=True):
            # Mock all availability checks to return False except local_stub
            with patch.object(ProviderRegistry, '_check_ollama_availability', return_value=False):
                registry = ProviderRegistry()
                
                available = registry.get_available_providers()
                
                # Should only have local_stub available
                assert len(available) == 1
                assert available[0] == LLMProvider.LOCAL_STUB


class TestProviderOrderFunctions:
    """Test the module-level convenience functions."""

    def setup_method(self):
        """Set up test environment."""
        import shared.llm.provider_order
        shared.llm.provider_order._provider_registry = None
        # Clear LRU cache
        get_provider_order.cache_clear()
        get_available_providers.cache_clear()

    def test_get_provider_order_free_first(self):
        """Test get_provider_order with free-first preference."""
        order = get_provider_order(prefer_free=True)
        
        assert isinstance(order, list)
        assert len(order) > 0
        assert "ollama" in order
        assert "huggingface" in order

    def test_get_provider_order_base_order(self):
        """Test get_provider_order with base order."""
        order = get_provider_order(prefer_free=False)
        
        assert isinstance(order, list)
        assert len(order) > 0

    def test_get_available_providers_function(self):
        """Test get_available_providers function."""
        available = get_available_providers(prefer_free=True)
        
        assert isinstance(available, list)
        # Local stub should always be available
        assert "local_stub" in available

    def test_select_provider_for_complexity_function(self):
        """Test select_provider_for_complexity function."""
        provider = select_provider_for_complexity(
            QueryComplexity.SIMPLE, 
            prefer_free=True
        )
        
        # Should return a provider name or None
        assert provider is None or isinstance(provider, str)

    def test_get_provider_stats_function(self):
        """Test get_provider_stats function."""
        stats = get_provider_stats()
        
        assert isinstance(stats, dict)
        assert "total_providers" in stats
        assert "free_providers" in stats
        assert "paid_providers" in stats
        assert "available_providers" in stats
        assert "base_order" in stats
        assert "free_first_order" in stats
        
        # Check provider availability flags
        assert "ollama_available" in stats
        assert "huggingface_available" in stats
        assert "openai_available" in stats
        assert "anthropic_available" in stats
        assert "local_stub_available" in stats


class TestFallbackChain:
    """Test the complete fallback chain functionality."""

    def setup_method(self):
        """Set up test environment."""
        import shared.llm.provider_order
        shared.llm.provider_order._provider_registry = None

    @patch.dict(os.environ, {}, clear=True)
    def test_no_keys_fallback_chain(self):
        """Test fallback chain when no API keys are provided."""
        available = get_available_providers(prefer_free=True)
        
        # Should fall back to free/local providers
        for provider_name in available:
            registry = get_provider_registry()
            provider_enum = LLMProvider(provider_name)
            config = registry.get_provider_info(provider_enum)
            if config:
                # Only free providers should be available
                assert config.is_free, f"Provider {provider_name} should be free but isn't"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_partial_keys_fallback_chain(self):
        """Test fallback chain when some API keys are provided."""
        available = get_available_providers(prefer_free=True)
        
        # Should include both free and available paid providers
        provider_names = set(available)
        assert "local_stub" in provider_names  # Always available
        # OpenAI should be available due to API key

    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-openai-key",
        "ANTHROPIC_API_KEY": "test-anthropic-key",
        "HUGGINGFACE_WRITE_TOKEN": "test-hf-token",
        "OLLAMA_BASE_URL": "http://localhost:11434"
    })
    def test_all_keys_fallback_chain(self):
        """Test fallback chain when all API keys are provided."""
        order = get_provider_order(prefer_free=True)
        
        # Should prioritize free providers first
        assert "ollama" in order
        assert "huggingface" in order
        assert "openai" in order
        assert "anthropic" in order
        assert "local_stub" in order
        
        # Free providers should come before paid ones in free-first mode
        ollama_idx = order.index("ollama")
        openai_idx = order.index("openai")
        assert ollama_idx < openai_idx


class TestEnvironmentConfig:
    """Test environment-based configuration."""

    def setup_method(self):
        """Set up test environment."""
        import shared.llm.provider_order
        shared.llm.provider_order._provider_registry = None

    def test_ollama_availability_check(self):
        """Test Ollama availability checking."""
        registry = ProviderRegistry()
        
        # Test with Ollama disabled
        with patch.dict(os.environ, {"OLLAMA_ENABLED": "false"}):
            assert not registry._check_ollama_availability()
        
        # Test with Ollama enabled but no URL
        with patch.dict(os.environ, {"OLLAMA_ENABLED": "true"}, clear=True):
            assert not registry._check_ollama_availability()
        
        # Test with Ollama enabled and URL set
        with patch.dict(os.environ, {
            "OLLAMA_ENABLED": "true",
            "OLLAMA_BASE_URL": "http://localhost:11434"
        }):
            assert registry._check_ollama_availability()

    def test_api_key_availability_checks(self):
        """Test API key availability checks."""
        registry = ProviderRegistry()
        
        # Test OpenAI
        with patch.dict(os.environ, {}, clear=True):
            assert not registry._check_openai_availability()
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            assert registry._check_openai_availability()
        
        # Test Anthropic
        with patch.dict(os.environ, {}, clear=True):
            assert not registry._check_anthropic_availability()
        
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            assert registry._check_anthropic_availability()
        
        # Test HuggingFace
        with patch.dict(os.environ, {}, clear=True):
            assert not registry._check_huggingface_availability()
        
        with patch.dict(os.environ, {"HUGGINGFACE_WRITE_TOKEN": "test-token"}):
            assert registry._check_huggingface_availability()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
