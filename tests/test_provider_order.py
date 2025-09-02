#!/usr/bin/env python3
"""
Tests for Centralized LLM Provider Order System

This test suite verifies the provider ordering, fallback chains, and
dynamic provider selection functionality including role-based selection.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from shared.llm.provider_order import (
    LLMProvider,
    QueryComplexity,
    LLMRole,
    ProviderConfig,
    RoleMapping,
    ProviderRegistry,
    get_provider_registry,
    get_provider_order,
    get_available_providers,
    select_provider_for_complexity,
    select_provider_for_role,
    get_provider_stats,
    get_provider_metrics,
    get_role_mappings
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

    def test_provider_capabilities(self):
        """Test that providers have correct capability assignments."""
        registry = ProviderRegistry()
        
        # Check Ollama capabilities
        ollama_config = registry.providers[LLMProvider.OLLAMA]
        assert LLMRole.FAST in ollama_config.capabilities
        assert LLMRole.STANDARD in ollama_config.capabilities
        assert LLMRole.TOOL not in ollama_config.capabilities
        
        # Check OpenAI capabilities (should have all roles)
        openai_config = registry.providers[LLMProvider.OPENAI]
        assert LLMRole.FAST in openai_config.capabilities
        assert LLMRole.QUALITY in openai_config.capabilities
        assert LLMRole.LONG in openai_config.capabilities
        assert LLMRole.REASONING in openai_config.capabilities
        assert LLMRole.TOOL in openai_config.capabilities
        
        # Check Anthropic capabilities
        anthropic_config = registry.providers[LLMProvider.ANTHROPIC]
        assert LLMRole.QUALITY in anthropic_config.capabilities
        assert LLMRole.LONG in anthropic_config.capabilities
        assert LLMRole.REASONING in anthropic_config.capabilities
        assert LLMRole.TOOL in anthropic_config.capabilities

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


class TestRoleMapping:
    """Test the RoleMapping class for role-based provider selection."""

    def setup_method(self):
        """Set up test environment."""
        import shared.llm.provider_order
        shared.llm.provider_order._provider_registry = None

    def test_default_role_mappings(self):
        """Test default role mappings are loaded correctly."""
        role_mapping = RoleMapping()
        
        # Check that all roles have mappings
        for role in LLMRole:
            mappings = role_mapping.get_providers_for_role(role)
            assert len(mappings) > 0, f"Role {role} should have provider mappings"
        
        # Check specific role mappings
        fast_providers = role_mapping.get_providers_for_role(LLMRole.FAST)
        assert "ollama:llama3" in fast_providers
        assert "openai:gpt-4o-mini" in fast_providers
        
        quality_providers = role_mapping.get_providers_for_role(LLMRole.QUALITY)
        assert "anthropic:claude-3-5-sonnet" in quality_providers
        assert "openai:gpt-4o" in quality_providers

    @patch.dict(os.environ, {
        "LLM_FAST": "ollama:llama3",
        "LLM_QUALITY": "openai:gpt-4o"
    })
    def test_custom_role_mappings_from_env(self):
        """Test custom role mappings from environment variables."""
        role_mapping = RoleMapping()
        
        fast_providers = role_mapping.get_providers_for_role(LLMRole.FAST)
        assert fast_providers == ["ollama:llama3"]
        
        quality_providers = role_mapping.get_providers_for_role(LLMRole.QUALITY)
        assert quality_providers == ["openai:gpt-4o"]

    def test_get_role_for_provider(self):
        """Test getting the primary role for a provider."""
        role_mapping = RoleMapping()
        
        # Test that providers are mapped to appropriate roles
        ollama_role = role_mapping.get_role_for_provider("ollama")
        assert ollama_role == LLMRole.FAST
        
        openai_role = role_mapping.get_role_for_provider("openai")
        assert openai_role in [LLMRole.FAST, LLMRole.QUALITY, LLMRole.LONG, LLMRole.REASONING, LLMRole.TOOL]

    def test_get_all_mappings(self):
        """Test getting all role mappings."""
        role_mapping = RoleMapping()
        all_mappings = role_mapping.get_all_mappings()
        
        # Check that all roles are present
        for role in LLMRole:
            assert role in all_mappings
            assert len(all_mappings[role]) > 0


class TestRoleBasedProviderSelection:
    """Test role-based provider selection functionality."""

    def setup_method(self):
        """Set up test environment."""
        import shared.llm.provider_order
        shared.llm.provider_order._provider_registry = None

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_select_provider_for_fast_role(self):
        """Test provider selection for FAST role."""
        registry = ProviderRegistry()
        
        provider = registry.select_provider_for_role(LLMRole.FAST, prefer_free=True)
        
        # Should prefer free providers for FAST role
        if provider:
            config = registry.providers[provider]
            assert LLMRole.FAST in config.capabilities
            # Should prefer free providers when available
            if provider in [LLMProvider.OLLAMA, LLMProvider.HUGGINGFACE, LLMProvider.LOCAL_STUB]:
                assert config.is_free

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_select_provider_for_quality_role(self):
        """Test provider selection for QUALITY role."""
        registry = ProviderRegistry()
        
        provider = registry.select_provider_for_role(LLMRole.QUALITY, prefer_free=False)
        
        # Should select a provider capable of QUALITY role
        if provider:
            config = registry.providers[provider]
            assert LLMRole.QUALITY in config.capabilities

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_select_provider_for_tool_role(self):
        """Test provider selection for TOOL role."""
        registry = ProviderRegistry()
        
        provider = registry.select_provider_for_role(LLMRole.TOOL, prefer_free=False)
        
        # Should select a provider capable of TOOL role
        if provider:
            config = registry.providers[provider]
            assert LLMRole.TOOL in config.capabilities
            assert config.supports_tools

    def test_select_provider_for_role_no_available_providers(self):
        """Test role-based selection when no providers are available."""
        with patch.dict(os.environ, {}, clear=True):
            registry = ProviderRegistry()
            
            # Mock all availability checks to return False except local_stub
            with patch.object(ProviderRegistry, '_check_ollama_availability', return_value=False):
                provider = registry.select_provider_for_role(LLMRole.QUALITY, prefer_free=True)
                
                # Should return None since no suitable providers available
                assert provider is None

    def test_role_based_selection_with_mixed_availability(self):
        """Test role-based selection with mixed provider availability."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            registry = ProviderRegistry()
            
            # Test FAST role - should prefer free providers
            fast_provider = registry.select_provider_for_role(LLMRole.FAST, prefer_free=True)
            if fast_provider:
                config = registry.providers[fast_provider]
                assert LLMRole.FAST in config.capabilities
            
            # Test TOOL role - should use OpenAI since it's available and supports tools
            tool_provider = registry.select_provider_for_role(LLMRole.TOOL, prefer_free=False)
            if tool_provider:
                config = registry.providers[tool_provider]
                assert LLMRole.TOOL in config.capabilities
                assert config.supports_tools


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
            config = registry.providers[provider]
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

    def test_select_provider_for_role_function(self):
        """Test select_provider_for_role function."""
        provider = select_provider_for_role(
            LLMRole.FAST, 
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

    def test_get_provider_metrics_function(self):
        """Test get_provider_metrics function."""
        metrics = get_provider_metrics()
        
        assert isinstance(metrics, dict)
        # Should include base stats
        assert "total_providers" in metrics
        
        # Should include role-based metrics
        for role in LLMRole:
            assert f"role_{role.value}_providers" in metrics
            assert f"role_{role.value}_available" in metrics

    def test_get_role_mappings_function(self):
        """Test get_role_mappings function."""
        mappings = get_role_mappings()
        
        assert isinstance(mappings, dict)
        # Should include all roles
        for role in LLMRole:
            assert role in mappings
            assert isinstance(mappings[role], list)


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
