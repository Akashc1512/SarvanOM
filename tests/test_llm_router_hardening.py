#!/usr/bin/env python3
"""
Unit tests for LLM Router Hardening

Tests the enhanced LLM processor with:
- Provider order gating with PRIORITIZE_FREE_MODELS=true by default
- Timeout, max_retries, exponential backoff per provider
- Automatic fallback to stub response if no API keys available
- Structured logging with {provider, attempt, latency_ms, ok} and trace_id
"""

import pytest
import asyncio
import time
import os
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Import the LLM processor
from services.gateway.real_llm_integration import (
    RealLLMProcessor, LLMProvider, LLMRequest, LLMResponse, 
    ProviderConfig, QueryComplexity
)


class TestLLMRouterHardening:
    """Test LLM router hardening features."""
    
    @pytest.fixture
    def llm_processor(self):
        """Create a test LLM processor instance."""
        return RealLLMProcessor()
    
    def test_provider_configs_setup(self, llm_processor):
        """Test that provider configurations are properly set up."""
        assert hasattr(llm_processor, 'provider_configs')
        assert LLMProvider.HUGGINGFACE in llm_processor.provider_configs
        assert LLMProvider.OLLAMA in llm_processor.provider_configs
        assert LLMProvider.LOCAL_STUB in llm_processor.provider_configs
        
        # Check priority order (free-first)
        hf_config = llm_processor.provider_configs[LLMProvider.HUGGINGFACE]
        assert hf_config.priority == 1  # Highest priority for free models
        
        stub_config = llm_processor.provider_configs[LLMProvider.LOCAL_STUB]
        assert stub_config.priority == 999  # Lowest priority
    
    def test_get_provider_order_free_first(self, llm_processor):
        """Test provider order with PRIORITIZE_FREE_MODELS=true."""
        with patch.object(llm_processor, '_is_provider_available', return_value=True):
            order = llm_processor.get_provider_order(prefer_free=True)
            
            # Should be free-first order
            expected_order = [
                LLMProvider.HUGGINGFACE,
                LLMProvider.OLLAMA,
                LLMProvider.ANTHROPIC,
                LLMProvider.OPENAI,
                LLMProvider.LOCAL_STUB
            ]
            
            assert order == expected_order
    
    @pytest.mark.asyncio
    async def test_call_llm_with_provider_gating_no_providers(self, llm_processor):
        """Test provider gating when no providers are available."""
        with patch.object(llm_processor, 'get_provider_order', return_value=[]):
            response = await llm_processor.call_llm_with_provider_gating(
                prompt="Test prompt",
                max_tokens=100,
                temperature=0.2
            )
            
            assert response.success == True
            assert response.provider == LLMProvider.LOCAL_STUB
            assert "stub response" in response.content.lower()
            assert response.latency_ms == 0
            assert response.attempt == 1
            assert response.retries == 0
    
    @pytest.mark.asyncio
    async def test_call_llm_with_provider_gating_first_provider_succeeds(self, llm_processor):
        """Test provider gating when first provider succeeds."""
        mock_response = "Test response from HuggingFace"
        
        with patch.object(llm_processor, 'get_provider_order', return_value=[LLMProvider.HUGGINGFACE, LLMProvider.OLLAMA]):
            with patch.object(llm_processor, '_call_llm_with_retry') as mock_call:
                mock_call.return_value = LLMResponse(
                    content=mock_response,
                    provider=LLMProvider.HUGGINGFACE,
                    model="distilgpt2",
                    latency_ms=150.0,
                    success=True,
                    trace_id="test-trace-123",
                    attempt=1,
                    retries=0
                )
                
                response = await llm_processor.call_llm_with_provider_gating(
                    prompt="Test prompt",
                    max_tokens=100,
                    temperature=0.2
                )
                
                assert response.success == True
                assert response.content == mock_response
                assert response.provider == LLMProvider.HUGGINGFACE
                assert mock_call.call_count == 1  # Only called once
    
    @pytest.mark.asyncio
    async def test_call_llm_with_provider_gating_all_providers_fail(self, llm_processor):
        """Test provider gating when all providers fail, fallback to stub."""
        with patch.object(llm_processor, 'get_provider_order', return_value=[LLMProvider.HUGGINGFACE, LLMProvider.OLLAMA]):
            with patch.object(llm_processor, '_call_llm_with_retry') as mock_call:
                # All calls fail
                mock_call.return_value = LLMResponse(
                    content="",
                    provider=LLMProvider.HUGGINGFACE,
                    model="distilgpt2",
                    latency_ms=100.0,
                    success=False,
                    error_message="Provider failed",
                    trace_id="test-trace-123",
                    attempt=3,
                    retries=2
                )
                
                start_time = time.time()
                response = await llm_processor.call_llm_with_provider_gating(
                    prompt="Test prompt",
                    max_tokens=100,
                    temperature=0.2
                )
                end_time = time.time()
                
                assert response.success == True
                assert response.provider == LLMProvider.LOCAL_STUB
                assert "stub response" in response.content.lower()
                assert response.attempt == 3  # 2 providers + 1 stub
                assert response.retries == 2  # 2 failed providers
                assert (end_time - start_time) < 2.0  # Should return within 2s
    
    def test_generate_stub_response(self, llm_processor):
        """Test stub response generation."""
        prompt = "What is the meaning of life?"
        stub_response = llm_processor._generate_stub_response(prompt)
        
        assert "stub response" in stub_response.lower()
        assert "provider=local_stub" in stub_response
        assert prompt[:100] in stub_response
        assert "API keys" in stub_response
        assert "try again" in stub_response


class TestLLMRouterHardeningIntegration:
    """Integration tests for LLM router hardening."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_provider_gating(self):
        """Test end-to-end provider gating with real processor."""
        processor = RealLLMProcessor()
        
        # Test with a simple prompt
        response = await processor.call_llm_with_provider_gating(
            prompt="Hello, how are you?",
            max_tokens=50,
            temperature=0.2
        )
        
        # Should always return a response (success or stub)
        assert response is not None
        assert hasattr(response, 'content')
        assert hasattr(response, 'provider')
        assert hasattr(response, 'trace_id')
        assert hasattr(response, 'latency_ms')
        assert hasattr(response, 'success')
        
        # Should have a trace ID
        assert response.trace_id is not None
        assert len(response.trace_id) > 0
    
    @pytest.mark.asyncio
    async def test_missing_api_keys_handling(self):
        """Test handling when API keys are missing."""
        # Create processor with no API keys and mock all providers to be unavailable
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': '',
            'ANTHROPIC_API_KEY': '',
            'HUGGINGFACE_API_KEY': '',
            'PRIORITIZE_FREE_MODELS': 'true'
        }):
            processor = RealLLMProcessor()
            
            # Mock all providers to be unavailable except LOCAL_STUB
            with patch.object(processor, '_is_provider_available', side_effect=lambda provider: provider == LLMProvider.LOCAL_STUB):
                response = await processor.call_llm_with_provider_gating(
                    prompt="Test prompt",
                    max_tokens=100,
                    temperature=0.2
                )
                
                # Should return stub response
                assert response.success == True
                assert response.provider == LLMProvider.LOCAL_STUB
                assert "stub response" in response.content.lower()
                assert response.latency_ms >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
