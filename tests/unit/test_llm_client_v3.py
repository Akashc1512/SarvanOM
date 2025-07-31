"""
Comprehensive unit tests for LLM Client v3.

Tests cover:
- All provider implementations (OpenAI, Anthropic, Mock)
- Error handling and retry logic
- Fallback mechanisms
- Rate limiting
- Streaming support
- Embedding functionality
- Health checks
- Metrics and monitoring
- Edge cases and error conditions

Authors:
- Universal Knowledge Platform Engineering Team
    
Version:
    1.0.0 (2024-12-28)
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any

# Add the project root to the path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.core.llm_client_v3 import (
    EnhancedLLMClientV3,
    LLMConfig,
    LLMRequest,
    LLMResponse,
    LLMError,
    LLMProvider,
    LLMModel,
    RateLimiter,
    OpenAIProvider,
    AnthropicProvider,
    MockProvider,
    get_llm_client_v3,
    generate_text,
    create_embedding
)

class TestRateLimiter:
    """Test rate limiter functionality."""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_basic(self):
        """Test basic rate limiting functionality."""
        limiter = RateLimiter(requests_per_minute=2, tokens_per_minute=100)
        
        # First two requests should succeed
        assert await limiter.acquire(10)
        assert await limiter.acquire(10)
        
        # Third request should fail
        assert not await limiter.acquire(10)
    
    @pytest.mark.asyncio
    async def test_rate_limiter_token_limit(self):
        """Test token-based rate limiting."""
        limiter = RateLimiter(requests_per_minute=10, tokens_per_minute=50)
        
        # Should fail due to token limit
        assert not await limiter.acquire(60)
        
        # Should succeed with smaller token count
        assert await limiter.acquire(30)
    
    @pytest.mark.asyncio
    async def test_rate_limiter_wait_if_needed(self):
        """Test wait_if_needed functionality."""
        limiter = RateLimiter(requests_per_minute=1, tokens_per_minute=100)
        
        # First request should succeed immediately
        start_time = time.time()
        await limiter.wait_if_needed(10)
        assert time.time() - start_time < 0.1
        
        # Second request should wait
        start_time = time.time()
        await limiter.wait_if_needed(10)
        assert time.time() - start_time >= 0.5  # Should wait at least 0.5 seconds

class TestMockProvider:
    """Test mock provider functionality."""
    
    @pytest.mark.asyncio
    async def test_mock_provider_generate_text(self):
        """Test mock provider text generation."""
        config = LLMConfig(
            provider=LLMProvider.MOCK,
            model="mock-model",
            api_key="mock-key"
        )
        provider = MockProvider(config)
        
        request = LLMRequest(prompt="Test prompt")
        response = await provider.generate_text(request)
        
        assert isinstance(response, LLMResponse)
        assert response.provider == LLMProvider.MOCK
        assert response.model == "mock-model"
        assert "Test prompt" in response.content
        assert response.token_usage["total_tokens"] == 30
    
    @pytest.mark.asyncio
    async def test_mock_provider_streaming(self):
        """Test mock provider streaming."""
        config = LLMConfig(
            provider=LLMProvider.MOCK,
            model="mock-model",
            api_key="mock-key"
        )
        provider = MockProvider(config)
        
        request = LLMRequest(prompt="Test prompt", stream=True)
        chunks = []
        
        async for chunk in provider.generate_stream(request):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
    
    @pytest.mark.asyncio
    async def test_mock_provider_embedding(self):
        """Test mock provider embedding."""
        config = LLMConfig(
            provider=LLMProvider.MOCK,
            model="mock-model",
            api_key="mock-key"
        )
        provider = MockProvider(config)
        
        embedding = await provider.create_embedding("test text")
        
        assert isinstance(embedding, list)
        assert len(embedding) == 8
        assert all(isinstance(x, float) for x in embedding)
        assert all(0 <= x <= 1 for x in embedding)
    
    @pytest.mark.asyncio
    async def test_mock_provider_health_check(self):
        """Test mock provider health check."""
        config = LLMConfig(
            provider=LLMProvider.MOCK,
            model="mock-model",
            api_key="mock-key"
        )
        provider = MockProvider(config)
        
        assert await provider.health_check() is True

class TestOpenAIProvider:
    """Test OpenAI provider functionality."""
    
    @pytest.mark.asyncio
    async def test_openai_provider_initialization(self):
        """Test OpenAI provider initialization."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key="test-key"
        )
        
        with patch('shared.core.llm_client_v3.openai') as mock_openai:
            mock_openai.AsyncOpenAI.return_value = AsyncMock()
            provider = OpenAIProvider(config)
            
            assert provider.config == config
            assert provider.rate_limiter is not None
    
    @pytest.mark.asyncio
    async def test_openai_provider_generate_text_success(self):
        """Test successful OpenAI text generation."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key="test-key"
        )
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 30
        mock_response.id = "test-id"
        
        with patch('shared.core.llm_client_v3.openai') as mock_openai:
            mock_client = AsyncMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.AsyncOpenAI.return_value = mock_client
            
            provider = OpenAIProvider(config)
            request = LLMRequest(prompt="Test prompt")
            response = await provider.generate_text(request)
            
            assert isinstance(response, LLMResponse)
            assert response.content == "Test response"
            assert response.provider == LLMProvider.OPENAI
            assert response.model == "gpt-4"
            assert response.token_usage["total_tokens"] == 30
            assert response.request_id == "test-id"
    
    @pytest.mark.asyncio
    async def test_openai_provider_generate_text_error(self):
        """Test OpenAI text generation error handling."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key="test-key"
        )
        
        with patch('shared.core.llm_client_v3.openai') as mock_openai:
            mock_client = AsyncMock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai.AsyncOpenAI.return_value = mock_client
            
            provider = OpenAIProvider(config)
            request = LLMRequest(prompt="Test prompt")
            
            with pytest.raises(LLMError) as exc_info:
                await provider.generate_text(request)
            
            assert exc_info.value.provider == LLMProvider.OPENAI
            assert "API Error" in str(exc_info.value.message)
    
    @pytest.mark.asyncio
    async def test_openai_provider_embedding(self):
        """Test OpenAI embedding generation."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key="test-key"
        )
        
        mock_embedding_response = MagicMock()
        mock_embedding_response.data = [MagicMock()]
        mock_embedding_response.data[0].embedding = [0.1, 0.2, 0.3]
        
        with patch('shared.core.llm_client_v3.openai') as mock_openai:
            mock_client = AsyncMock()
            mock_client.embeddings.create.return_value = mock_embedding_response
            mock_openai.AsyncOpenAI.return_value = mock_client
            
            provider = OpenAIProvider(config)
            embedding = await provider.create_embedding("test text")
            
            assert isinstance(embedding, list)
            assert len(embedding) == 3
            assert embedding == [0.1, 0.2, 0.3]

class TestAnthropicProvider:
    """Test Anthropic provider functionality."""
    
    @pytest.mark.asyncio
    async def test_anthropic_provider_initialization(self):
        """Test Anthropic provider initialization."""
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-5-sonnet-20241022",
            api_key="test-key"
        )
        
        with patch('shared.core.llm_client_v3.anthropic') as mock_anthropic:
            mock_anthropic.AsyncAnthropic.return_value = AsyncMock()
            provider = AnthropicProvider(config)
            
            assert provider.config == config
            assert provider.rate_limiter is not None
    
    @pytest.mark.asyncio
    async def test_anthropic_provider_generate_text_success(self):
        """Test successful Anthropic text generation."""
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-5-sonnet-20241022",
            api_key="test-key"
        )
        
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "Test response"
        mock_response.stop_reason = "end_turn"
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 20
        mock_response.id = "test-id"
        
        with patch('shared.core.llm_client_v3.anthropic') as mock_anthropic:
            mock_client = AsyncMock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.AsyncAnthropic.return_value = mock_client
            
            provider = AnthropicProvider(config)
            request = LLMRequest(prompt="Test prompt")
            response = await provider.generate_text(request)
            
            assert isinstance(response, LLMResponse)
            assert response.content == "Test response"
            assert response.provider == LLMProvider.ANTHROPIC
            assert response.model == "claude-3-5-sonnet-20241022"
            assert response.token_usage["total_tokens"] == 30
            assert response.request_id == "test-id"

class TestEnhancedLLMClientV3:
    """Test enhanced LLM client v3 functionality."""
    
    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initialization."""
        client = EnhancedLLMClientV3()
        assert isinstance(client, EnhancedLLMClientV3)
        assert hasattr(client, 'providers')
        assert hasattr(client, 'metrics')
    
    @pytest.mark.asyncio
    async def test_client_with_mock_provider(self):
        """Test client with mock provider."""
        config = LLMConfig(
            provider=LLMProvider.MOCK,
            model="mock-model",
            api_key="mock-key"
        )
        
        client = EnhancedLLMClientV3([config])
        assert len(client.providers) == 1
        assert isinstance(client.providers[0], MockProvider)
    
    @pytest.mark.asyncio
    async def test_client_generate_text_success(self):
        """Test successful text generation."""
        config = LLMConfig(
            provider=LLMProvider.MOCK,
            model="mock-model",
            api_key="mock-key"
        )
        
        client = EnhancedLLMClientV3([config])
        request = LLMRequest(prompt="Test prompt")
        response = await client.generate_text(request)
        
        assert isinstance(response, LLMResponse)
        assert response.content is not None
        assert client.metrics["successful_requests"] == 1
        assert client.metrics["total_requests"] == 1
    
    @pytest.mark.asyncio
    async def test_client_generate_text_fallback(self):
        """Test text generation with fallback."""
        config1 = LLMConfig(
            provider=LLMProvider.MOCK,
            model="mock-model-1",
            api_key="mock-key-1"
        )
        config2 = LLMConfig(
            provider=LLMProvider.MOCK,
            model="mock-model-2",
            api_key="mock-key-2"
        )
        
        # Create client with two providers
        client = EnhancedLLMClientV3([config1, config2])
        
        # Mock the first provider to fail
        client.providers[0].generate_text = AsyncMock(side_effect=LLMError(
            error_type="test_error",
            message="Test error",
            provider=LLMProvider.MOCK,
            model="mock-model-1"
        ))
        
        request = LLMRequest(prompt="Test prompt")
        response = await client.generate_text(request)
        
        assert isinstance(response, LLMResponse)
        assert client.metrics["fallback_requests"] == 1
    
    @pytest.mark.asyncio
    async def test_client_generate_text_all_fail(self):
        """Test text generation when all providers fail."""
        config = LLMConfig(
            provider=LLMProvider.MOCK,
            model="mock-model",
            api_key="mock-key"
        )
        
        client = EnhancedLLMClientV3([config])
        
        # Mock provider to fail
        client.providers[0].generate_text = AsyncMock(side_effect=LLMError(
            error_type="test_error",
            message="Test error",
            provider=LLMProvider.MOCK,
            model="mock-model"
        ))
        
        request = LLMRequest(prompt="Test prompt")
        
        with pytest.raises(LLMError) as exc_info:
            await client.generate_text(request)
        
        assert "all_providers_failed" in exc_info.value.error_type
    
    @pytest.mark.asyncio
    async def test_client_streaming(self):
        """Test streaming text generation."""
        config = LLMConfig(
            provider=LLMProvider.MOCK,
            model="mock-model",
            api_key="mock-key"
        )
        
        client = EnhancedLLMClientV3([config])
        request = LLMRequest(prompt="Test prompt", stream=True)
        
        chunks = []
        async for chunk in client.generate_stream(request):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
    
    @pytest.mark.asyncio
    async def test_client_embedding(self):
        """Test embedding generation."""
        config = LLMConfig(
            provider=LLMProvider.MOCK,
            model="mock-model",
            api_key="mock-key"
        )
        
        client = EnhancedLLMClientV3([config])
        embedding = await client.create_embedding("test text")
        
        assert isinstance(embedding, list)
        assert len(embedding) == 8
        assert all(isinstance(x, float) for x in embedding)
    
    @pytest.mark.asyncio
    async def test_client_health_check(self):
        """Test client health check."""
        config = LLMConfig(
            provider=LLMProvider.MOCK,
            model="mock-model",
            api_key="mock-key"
        )
        
        client = EnhancedLLMClientV3([config])
        health_status = await client.health_check()
        
        assert isinstance(health_status, dict)
        assert "provider_0" in health_status
        assert health_status["provider_0"]["healthy"] is True
    
    @pytest.mark.asyncio
    async def test_client_metrics(self):
        """Test client metrics."""
        config = LLMConfig(
            provider=LLMProvider.MOCK,
            model="mock-model",
            api_key="mock-key"
        )
        
        client = EnhancedLLMClientV3([config])
        
        # Make a request to generate metrics
        request = LLMRequest(prompt="Test prompt")
        await client.generate_text(request)
        
        metrics = client.get_metrics()
        
        assert "total_requests" in metrics
        assert "successful_requests" in metrics
        assert "failed_requests" in metrics
        assert "total_tokens" in metrics
        assert "total_response_time" in metrics
        assert "providers" in metrics
        assert metrics["total_requests"] == 1
        assert metrics["successful_requests"] == 1

class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @pytest.mark.asyncio
    async def test_generate_text_function(self):
        """Test generate_text convenience function."""
        with patch('shared.core.llm_client_v3.get_llm_client_v3') as mock_get_client:
            mock_client = AsyncMock()
            mock_response = LLMResponse(
                content="Test response",
                provider=LLMProvider.MOCK,
                model="mock-model",
                token_usage={"total_tokens": 30},
                finish_reason="stop",
                response_time_ms=100
            )
            mock_client.generate_text.return_value = mock_response
            mock_get_client.return_value = mock_client
            
            result = await generate_text("Test prompt")
            
            assert result == "Test response"
            mock_client.generate_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_embedding_function(self):
        """Test create_embedding convenience function."""
        with patch('shared.core.llm_client_v3.get_llm_client_v3') as mock_get_client:
            mock_client = AsyncMock()
            mock_embedding = [0.1, 0.2, 0.3]
            mock_client.create_embedding.return_value = mock_embedding
            mock_get_client.return_value = mock_client
            
            result = await create_embedding("test text")
            
            assert result == [0.1, 0.2, 0.3]
            mock_client.create_embedding.assert_called_once_with("test text")

class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_retry_logic(self):
        """Test retry logic with exponential backoff."""
        config = LLMConfig(
            provider=LLMProvider.MOCK,
            model="mock-model",
            api_key="mock-key"
        )
        
        client = EnhancedLLMClientV3([config])
        
        # Mock provider to fail twice then succeed
        call_count = 0
        async def mock_generate_text(request):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise LLMError(
                    error_type="retryable_error",
                    message="Retryable error",
                    provider=LLMProvider.MOCK,
                    model="mock-model",
                    retryable=True
                )
            return LLMResponse(
                content="Success after retries",
                provider=LLMProvider.MOCK,
                model="mock-model",
                token_usage={"total_tokens": 30},
                finish_reason="stop",
                response_time_ms=100
            )
        
        client.providers[0].generate_text = mock_generate_text
        
        request = LLMRequest(prompt="Test prompt")
        response = await client.generate_text(request)
        
        assert response.content == "Success after retries"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_non_retryable_error(self):
        """Test non-retryable error handling."""
        config = LLMConfig(
            provider=LLMProvider.MOCK,
            model="mock-model",
            api_key="mock-key"
        )
        
        client = EnhancedLLMClientV3([config])
        
        # Mock provider to fail with non-retryable error
        client.providers[0].generate_text = AsyncMock(side_effect=LLMError(
            error_type="non_retryable_error",
            message="Non-retryable error",
            provider=LLMProvider.MOCK,
            model="mock-model",
            retryable=False
        ))
        
        request = LLMRequest(prompt="Test prompt")
        
        with pytest.raises(LLMError) as exc_info:
            await client.generate_text(request)
        
        assert exc_info.value.retryable is False

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.mark.asyncio
    async def test_empty_prompt(self):
        """Test handling of empty prompt."""
        config = LLMConfig(
            provider=LLMProvider.MOCK,
            model="mock-model",
            api_key="mock-key"
        )
        
        client = EnhancedLLMClientV3([config])
        request = LLMRequest(prompt="")
        response = await client.generate_text(request)
        
        assert isinstance(response, LLMResponse)
        assert response.content is not None
    
    @pytest.mark.asyncio
    async def test_very_long_prompt(self):
        """Test handling of very long prompt."""
        config = LLMConfig(
            provider=LLMProvider.MOCK,
            model="mock-model",
            api_key="mock-key"
        )
        
        client = EnhancedLLMClientV3([config])
        long_prompt = "Test " * 1000  # Very long prompt
        request = LLMRequest(prompt=long_prompt)
        response = await client.generate_text(request)
        
        assert isinstance(response, LLMResponse)
        assert response.content is not None
    
    @pytest.mark.asyncio
    async def test_no_providers(self):
        """Test behavior when no providers are configured."""
        client = EnhancedLLMClientV3([])
        request = LLMRequest(prompt="Test prompt")
        
        with pytest.raises(LLMError) as exc_info:
            await client.generate_text(request)
        
        assert "no_providers" in exc_info.value.error_type
    
    @pytest.mark.asyncio
    async def test_system_message(self):
        """Test handling of system message."""
        config = LLMConfig(
            provider=LLMProvider.MOCK,
            model="mock-model",
            api_key="mock-key"
        )
        
        client = EnhancedLLMClientV3([config])
        request = LLMRequest(
            prompt="Test prompt",
            system_message="You are a helpful assistant."
        )
        response = await client.generate_text(request)
        
        assert isinstance(response, LLMResponse)
        assert response.content is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 