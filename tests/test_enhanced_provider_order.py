#!/usr/bin/env python3
"""
Tests for Enhanced LLM Provider Order System (Phase B2)

This test suite verifies the enhanced provider ordering system including:
- Role-based model selection for each provider
- Dynamic model selection based on query complexity
- Provider-specific model configurations
- Model scoring and selection algorithms
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from shared.llm.provider_order import (
    LLMProvider,
    QueryComplexity,
    LLMRole,
    ProviderConfig,
    ModelConfig,
    RoleMapping,
    ProviderModelRegistry,
    ProviderRegistry,
    get_provider_registry,
    get_provider_order,
    get_available_providers,
    select_provider_for_complexity,
    select_provider_and_model_for_complexity,
    select_provider_for_role,
    get_provider_stats,
    get_provider_metrics,
    get_role_mappings,
    get_provider_models
)


class TestModelConfig:
    """Test the ModelConfig dataclass."""
    
    def test_model_config_creation(self):
        """Test ModelConfig can be created with all required fields."""
        model = ModelConfig(
            name="test-model",
            provider=LLMProvider.OPENAI,
            role=LLMRole.FAST,
            max_tokens=1000,
            avg_latency_ms=500,
            cost_per_1k_tokens=0.001,
            supports_streaming=True,
            supports_tools=False,
            is_free=False,
            context_window=1000,
            reasoning_capability=0.8,
            tool_capability=0.0
        )
        
        assert model.name == "test-model"
        assert model.provider == LLMProvider.OPENAI
        assert model.role == LLMRole.FAST
        assert model.max_tokens == 1000
        assert model.avg_latency_ms == 500
        assert model.cost_per_1k_tokens == 0.001
        assert model.supports_streaming is True
        assert model.supports_tools is False
        assert model.is_free is False
        assert model.context_window == 1000
        assert model.reasoning_capability == 0.8
        assert model.tool_capability == 0.0


class TestProviderModelRegistry:
    """Test the ProviderModelRegistry class."""
    
    def setup_method(self):
        """Set up test environment."""
        import shared.llm.provider_order
        shared.llm.provider_order._provider_registry = None

    def test_registry_initialization(self):
        """Test registry initializes with correct model configurations."""
        registry = ProviderModelRegistry()
        all_models = registry.get_all_provider_models()
        
        # Check that all providers have models
        assert LLMProvider.OLLAMA in all_models
        assert LLMProvider.HUGGINGFACE in all_models
        assert LLMProvider.OPENAI in all_models
        assert LLMProvider.ANTHROPIC in all_models
        assert LLMProvider.LOCAL_STUB in all_models
        
        # Check specific provider models
        ollama_models = all_models[LLMProvider.OLLAMA]
        assert LLMRole.FAST in ollama_models
        assert LLMRole.STANDARD in ollama_models
        
        # Check that Ollama has specific models
        fast_models = ollama_models[LLMRole.FAST]
        model_names = [m.name for m in fast_models]
        assert "llama3:8b" in model_names
        assert "llama3:3b" in model_names

    def test_get_models_for_provider_role(self):
        """Test getting models for specific provider and role."""
        registry = ProviderModelRegistry()
        
        # Test Ollama FAST role
        ollama_fast_models = registry.get_models_for_provider_role(LLMProvider.OLLAMA, LLMRole.FAST)
        assert len(ollama_fast_models) == 2
        assert any(m.name == "llama3:8b" for m in ollama_fast_models)
        assert any(m.name == "llama3:3b" for m in ollama_fast_models)
        
        # Test OpenAI TOOL role
        openai_tool_models = registry.get_models_for_provider_role(LLMProvider.OPENAI, LLMRole.TOOL)
        assert len(openai_tool_models) == 1
        assert openai_tool_models[0].name == "gpt-4o"
        assert openai_tool_models[0].tool_capability > 0.9

    def test_get_best_model_for_complexity_simple(self):
        """Test model selection for simple queries."""
        registry = ProviderModelRegistry()
        
        # For simple queries, should prioritize speed
        model = registry.get_best_model_for_complexity(
            LLMProvider.OLLAMA, 
            QueryComplexity.SIMPLE, 
            prefer_free=True
        )
        
        assert model is not None
        # Should select the fastest model (llama3:3b with 800ms latency)
        assert model.name == "llama3:3b"
        assert model.avg_latency_ms == 800

    def test_get_best_model_for_complexity_expert(self):
        """Test model selection for expert queries."""
        registry = ProviderModelRegistry()
        
        # For expert queries, should prioritize tool capability
        model = registry.get_best_model_for_complexity(
            LLMProvider.OPENAI, 
            QueryComplexity.EXPERT, 
            prefer_free=False
        )
        
        assert model is not None
        # Should select the model with highest tool capability
        assert model.tool_capability > 0.9

    def test_get_best_model_for_complexity_complex(self):
        """Test model selection for complex queries."""
        registry = ProviderModelRegistry()
        
        # For complex queries, should prioritize reasoning capability
        model = registry.get_best_model_for_complexity(
            LLMProvider.OPENAI, 
            QueryComplexity.COMPLEX, 
            prefer_free=False
        )
        
        assert model is not None
        # Should select the model with highest reasoning capability
        assert model.reasoning_capability > 0.9

    def test_get_best_model_for_complexity_fallback(self):
        """Test model selection fallback when target role not available."""
        registry = ProviderModelRegistry()
        
        # Test with a provider that doesn't have TOOL role
        model = registry.get_best_model_for_complexity(
            LLMProvider.OLLAMA, 
            QueryComplexity.EXPERT, 
            prefer_free=True
        )
        
        # Should fallback to FAST role since Ollama doesn't support TOOL
        assert model is not None
        assert model.role == LLMRole.FAST

    def test_get_best_model_for_complexity_prefer_free(self):
        """Test model selection respects free preference."""
        registry = ProviderModelRegistry()
        
        # Test with free preference
        model = registry.get_best_model_for_complexity(
            LLMProvider.OPENAI, 
            QueryComplexity.SIMPLE, 
            prefer_free=True
        )
        
        # Should still return a model even though OpenAI is paid
        # (since no free alternative available for this provider)
        assert model is not None


class TestEnhancedProviderRegistry:
    """Test the enhanced ProviderRegistry with model selection."""
    
    def setup_method(self):
        """Set up test environment."""
        import shared.llm.provider_order
        shared.llm.provider_order._provider_registry = None

    def test_provider_models_population(self):
        """Test that provider models are populated correctly."""
        registry = ProviderRegistry()
        
        # Check that providers have their models populated
        ollama_config = registry.providers[LLMProvider.OLLAMA]
        assert ollama_config.models is not None
        assert len(ollama_config.models) > 0
        
        # Check specific models
        ollama_fast_models = ollama_config.models[LLMRole.FAST]
        assert len(ollama_fast_models) == 2
        assert any(m.name == "llama3:8b" for m in ollama_fast_models)

    def test_select_provider_and_model_for_complexity_simple(self):
        """Test provider and model selection for simple queries."""
        registry = ProviderRegistry()
        
        provider, model = registry.select_provider_and_model_for_complexity(
            QueryComplexity.SIMPLE, 
            prefer_free=True
        )
        
        assert provider is not None
        assert model is not None
        
        # Should prefer free providers for simple queries
        assert registry.providers[provider].is_free
        
        # Should select a fast model
        assert model.role == LLMRole.FAST or model.avg_latency_ms <= 1000

    def test_select_provider_and_model_for_complexity_expert(self):
        """Test provider and model selection for expert queries."""
        registry = ProviderRegistry()
        
        provider, model = registry.select_provider_and_model_for_complexity(
            QueryComplexity.EXPERT, 
            prefer_free=False
        )
        
        assert provider is not None
        assert model is not None
        
        # Should select a provider with tool support
        assert registry.providers[provider].supports_tools
        
        # Should select a model with high tool capability
        assert model.tool_capability > 0.8

    def test_select_provider_and_model_for_complexity_complex(self):
        """Test provider and model selection for complex queries."""
        registry = ProviderRegistry()
        
        provider, model = registry.select_provider_and_model_for_complexity(
            QueryComplexity.COMPLEX, 
            prefer_free=False
        )
        
        assert provider is not None
        assert model is not None
        
        # Should select a model with high reasoning capability
        assert model.reasoning_capability > 0.8

    def test_model_scoring_algorithm(self):
        """Test the model scoring algorithm."""
        registry = ProviderRegistry()
        
        # Create a test model
        test_model = ModelConfig(
            name="test-model",
            provider=LLMProvider.OPENAI,
            role=LLMRole.FAST,
            max_tokens=1000,
            avg_latency_ms=500,
            cost_per_1k_tokens=0.001,
            supports_streaming=True,
            supports_tools=True,
            is_free=False,
            context_window=1000,
            reasoning_capability=0.9,
            tool_capability=0.8
        )
        
        # Test scoring for different complexities
        simple_score = registry._calculate_model_score(
            test_model, QueryComplexity.SIMPLE, prefer_free=False
        )
        expert_score = registry._calculate_model_score(
            test_model, QueryComplexity.EXPERT, prefer_free=False
        )
        
        # Expert queries should score higher due to tool capability
        assert expert_score > simple_score
        
        # Test free preference penalty
        paid_score = registry._calculate_model_score(
            test_model, QueryComplexity.SIMPLE, prefer_free=True
        )
        free_score = registry._calculate_model_score(
            test_model, QueryComplexity.SIMPLE, prefer_free=False
        )
        
        # Paid models should score lower when prefer_free is True
        assert paid_score < free_score


class TestEnhancedModuleFunctions:
    """Test the enhanced module-level functions."""
    
    def setup_method(self):
        """Set up test environment."""
        import shared.llm.provider_order
        shared.llm.provider_order._provider_registry = None
        # Clear LRU cache
        get_provider_order.cache_clear()
        get_available_providers.cache_clear()

    def test_select_provider_and_model_for_complexity_function(self):
        """Test the module-level function for provider and model selection."""
        provider_name, model_name = select_provider_and_model_for_complexity(
            QueryComplexity.SIMPLE, 
            prefer_free=True
        )
        
        # Should return provider and model names
        assert provider_name is None or isinstance(provider_name, str)
        assert model_name is None or isinstance(model_name, str)

    def test_get_provider_models_function(self):
        """Test the get_provider_models function."""
        provider_models = get_provider_models()
        
        assert isinstance(provider_models, dict)
        assert LLMProvider.OLLAMA in provider_models
        assert LLMProvider.OPENAI in provider_models
        
        # Check that each provider has role-based models
        ollama_models = provider_models[LLMProvider.OLLAMA]
        assert LLMRole.FAST in ollama_models
        assert LLMRole.STANDARD in ollama_models

    def test_comprehensive_provider_selection(self):
        """Test comprehensive provider selection across all complexities."""
        complexities = [
            QueryComplexity.SIMPLE,
            QueryComplexity.STANDARD,
            QueryComplexity.COMPLEX,
            QueryComplexity.EXPERT
        ]
        
        for complexity in complexities:
            provider_name, model_name = select_provider_and_model_for_complexity(
                complexity, 
                prefer_free=True
            )
            
            # Should return valid provider and model names
            if provider_name:
                assert isinstance(provider_name, str)
                assert provider_name in ["ollama", "huggingface", "openai", "anthropic", "local_stub"]
            
            if model_name:
                assert isinstance(model_name, str)
                assert len(model_name) > 0

    def test_role_based_provider_selection(self):
        """Test role-based provider selection."""
        roles = [
            LLMRole.FAST,
            LLMRole.QUALITY,
            LLMRole.LONG,
            LLMRole.REASONING,
            LLMRole.TOOL
        ]
        
        for role in roles:
            provider_name = select_provider_for_role(role, prefer_free=True)
            
            # Should return valid provider name or None
            if provider_name:
                assert isinstance(provider_name, str)
                assert provider_name in ["ollama", "huggingface", "openai", "anthropic", "local_stub"]


class TestEnvironmentConfiguration:
    """Test environment-based configuration for role mappings."""
    
    def setup_method(self):
        """Set up test environment."""
        import shared.llm.provider_order
        shared.llm.provider_order._provider_registry = None

    @patch.dict(os.environ, {
        "LLM_FAST": "ollama:llama3:8b",
        "LLM_QUALITY": "openai:gpt-4o",
        "LLM_TOOL": "anthropic:claude-3-5-sonnet"
    })
    def test_custom_role_mappings_from_env(self):
        """Test custom role mappings from environment variables."""
        role_mapping = RoleMapping()
        
        # Check custom FAST mapping
        fast_providers = role_mapping.get_providers_for_role(LLMRole.FAST)
        assert fast_providers == ["ollama:llama3:8b"]
        
        # Check custom QUALITY mapping
        quality_providers = role_mapping.get_providers_for_role(LLMRole.QUALITY)
        assert quality_providers == ["openai:gpt-4o"]
        
        # Check custom TOOL mapping
        tool_providers = role_mapping.get_providers_for_role(LLMRole.TOOL)
        assert tool_providers == ["anthropic:claude-3-5-sonnet"]

    def test_default_role_mappings(self):
        """Test default role mappings when environment variables not set."""
        with patch.dict(os.environ, {}, clear=True):
            role_mapping = RoleMapping()
            
            # Check that all roles have default mappings
            for role in LLMRole:
                mappings = role_mapping.get_providers_for_role(role)
                assert len(mappings) > 0
                assert all(":" in mapping for mapping in mappings)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
