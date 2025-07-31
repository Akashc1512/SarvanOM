"""
Comprehensive LLM Call Tests - MAANG Standards

This module provides comprehensive unit tests for all LLM calls,
ensuring proper functionality, error handling, and performance compliance.

Test Coverage:
    - OpenAI provider calls
    - Anthropic provider calls
    - Azure provider calls
    - Google provider calls
    - Fallback mechanisms
    - Rate limiting
    - Error handling
    - Performance monitoring
    - Token management
    - Streaming responses

Authors:
    - Universal Knowledge Platform Engineering Team
    
Version:
    2.0.0 (2024-12-28)
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta

# Import LLM client
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.core.llm_client_v3 import EnhancedLLMClient, LLMRequest, LLMResponse, LLMConfig
from shared.core.llm_client_v2 import LLMProviderInterface

class TestOpenAIProvider:
    """Test OpenAI provider functionality."""
    
    @pytest.fixture
    def openai_config(self):
        """OpenAI configuration."""
        return LLMConfig(
            provider="openai",
            api_key="test_openai_key",
            model="gpt-4",
            base_url="https://api.openai.com/v1",
            max_tokens=1000,
            temperature=0.7
        )
    
    @pytest.fixture
    def llm_client(self, openai_config):
        """Create LLM client with OpenAI provider."""
        return EnhancedLLMClient([openai_config])
    
    @pytest.fixture
    def sample_request(self):
        """Sample LLM request."""
        return LLMRequest(
            prompt="What is Python programming?",
            max_tokens=1000,
            temperature=0.7,
            model="gpt-4"
        )
    
    @pytest.mark.asyncio
    async def test_openai_generate_text_success(self, llm_client, sample_request):
        """Test successful OpenAI text generation."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Python is a high-level programming language..."
            mock_response.usage.total_tokens = 150
            mock_client.chat.completions.create.return_value = mock_response
            
            response = await llm_client.generate_text(sample_request)
            
            assert response.success is True
            assert "Python is a high-level programming language" in response.content
            assert response.tokens_used == 150
    
    @pytest.mark.asyncio
    async def test_openai_generate_text_error(self, llm_client, sample_request):
        """Test OpenAI text generation with error."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            mock_client.chat.completions.create.side_effect = Exception("OpenAI API error")
            
            response = await llm_client.generate_text(sample_request)
            
            assert response.success is False
            assert "OpenAI API error" in response.error
    
    @pytest.mark.asyncio
    async def test_openai_rate_limit_handling(self, llm_client, sample_request):
        """Test OpenAI rate limit handling."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            # Simulate rate limit error
            from openai import RateLimitError
            mock_client.chat.completions.create.side_effect = RateLimitError("Rate limit exceeded", response=Mock(), body={})
            
            response = await llm_client.generate_text(sample_request)
            
            assert response.success is False
            assert "rate limit" in response.error.lower()
    
    @pytest.mark.asyncio
    async def test_openai_token_limit_handling(self, llm_client, sample_request):
        """Test OpenAI token limit handling."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            # Simulate token limit error
            from openai import BadRequestError
            mock_client.chat.completions.create.side_effect = BadRequestError("Token limit exceeded", response=Mock(), body={})
            
            response = await llm_client.generate_text(sample_request)
            
            assert response.success is False
            assert "token" in response.error.lower()

class TestAnthropicProvider:
    """Test Anthropic provider functionality."""
    
    @pytest.fixture
    def anthropic_config(self):
        """Anthropic configuration."""
        return LLMConfig(
            provider="anthropic",
            api_key="test_anthropic_key",
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0.7
        )
    
    @pytest.fixture
    def llm_client(self, anthropic_config):
        """Create LLM client with Anthropic provider."""
        return EnhancedLLMClient([anthropic_config])
    
    @pytest.fixture
    def sample_request(self):
        """Sample LLM request."""
        return LLMRequest(
            prompt="What is Python programming?",
            max_tokens=1000,
            temperature=0.7,
            model="claude-3-sonnet-20240229"
        )
    
    @pytest.mark.asyncio
    async def test_anthropic_generate_text_success(self, llm_client, sample_request):
        """Test successful Anthropic text generation."""
        with patch('anthropic.AsyncAnthropic') as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            
            mock_response = Mock()
            mock_response.content = [Mock()]
            mock_response.content[0].text = "Python is a high-level programming language..."
            mock_response.usage.input_tokens = 50
            mock_response.usage.output_tokens = 100
            mock_client.messages.create.return_value = mock_response
            
            response = await llm_client.generate_text(sample_request)
            
            assert response.success is True
            assert "Python is a high-level programming language" in response.content
            assert response.tokens_used == 150
    
    @pytest.mark.asyncio
    async def test_anthropic_generate_text_error(self, llm_client, sample_request):
        """Test Anthropic text generation with error."""
        with patch('anthropic.AsyncAnthropic') as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            
            mock_client.messages.create.side_effect = Exception("Anthropic API error")
            
            response = await llm_client.generate_text(sample_request)
            
            assert response.success is False
            assert "Anthropic API error" in response.error

class TestAzureProvider:
    """Test Azure provider functionality."""
    
    @pytest.fixture
    def azure_config(self):
        """Azure configuration."""
        return LLMConfig(
            provider="azure",
            api_key="test_azure_key",
            model="gpt-4",
            base_url="https://test-resource.openai.azure.com/",
            api_version="2024-02-15-preview"
        )
    
    @pytest.fixture
    def llm_client(self, azure_config):
        """Create LLM client with Azure provider."""
        return EnhancedLLMClient([azure_config])
    
    @pytest.fixture
    def sample_request(self):
        """Sample LLM request."""
        return LLMRequest(
            prompt="What is Python programming?",
            max_tokens=1000,
            temperature=0.7,
            model="gpt-4"
        )
    
    @pytest.mark.asyncio
    async def test_azure_generate_text_success(self, llm_client, sample_request):
        """Test successful Azure text generation."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Python is a high-level programming language..."
            mock_response.usage.total_tokens = 150
            mock_client.chat.completions.create.return_value = mock_response
            
            response = await llm_client.generate_text(sample_request)
            
            assert response.success is True
            assert "Python is a high-level programming language" in response.content
            assert response.tokens_used == 150
    
    @pytest.mark.asyncio
    async def test_azure_generate_text_error(self, llm_client, sample_request):
        """Test Azure text generation with error."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            mock_client.chat.completions.create.side_effect = Exception("Azure API error")
            
            response = await llm_client.generate_text(sample_request)
            
            assert response.success is False
            assert "Azure API error" in response.error

class TestGoogleProvider:
    """Test Google provider functionality."""
    
    @pytest.fixture
    def google_config(self):
        """Google configuration."""
        return LLMConfig(
            provider="google",
            api_key="test_google_key",
            model="gemini-pro",
            max_tokens=1000,
            temperature=0.7
        )
    
    @pytest.fixture
    def llm_client(self, google_config):
        """Create LLM client with Google provider."""
        return EnhancedLLMClient([google_config])
    
    @pytest.fixture
    def sample_request(self):
        """Sample LLM request."""
        return LLMRequest(
            prompt="What is Python programming?",
            max_tokens=1000,
            temperature=0.7,
            model="gemini-pro"
        )
    
    @pytest.mark.asyncio
    async def test_google_generate_text_success(self, llm_client, sample_request):
        """Test successful Google text generation."""
        with patch('google.generativeai') as mock_google:
            mock_model = AsyncMock()
            mock_google.GenerativeModel.return_value = mock_model
            
            mock_response = Mock()
            mock_response.text = "Python is a high-level programming language..."
            mock_model.generate_content.return_value = mock_response
            
            response = await llm_client.generate_text(sample_request)
            
            assert response.success is True
            assert "Python is a high-level programming language" in response.content
    
    @pytest.mark.asyncio
    async def test_google_generate_text_error(self, llm_client, sample_request):
        """Test Google text generation with error."""
        with patch('google.generativeai') as mock_google:
            mock_model = AsyncMock()
            mock_google.GenerativeModel.return_value = mock_model
            
            mock_model.generate_content.side_effect = Exception("Google API error")
            
            response = await llm_client.generate_text(sample_request)
            
            assert response.success is False
            assert "Google API error" in response.error

class TestFallbackMechanisms:
    """Test LLM fallback mechanisms."""
    
    @pytest.fixture
    def multi_provider_client(self):
        """Create LLM client with multiple providers."""
        configs = [
            LLMConfig(provider="openai", api_key="test_openai", model="gpt-4"),
            LLMConfig(provider="anthropic", api_key="test_anthropic", model="claude-3-sonnet-20240229"),
            LLMConfig(provider="azure", api_key="test_azure", model="gpt-4")
        ]
        return EnhancedLLMClient(configs)
    
    @pytest.fixture
    def sample_request(self):
        """Sample LLM request."""
        return LLMRequest(
            prompt="What is Python programming?",
            max_tokens=1000,
            temperature=0.7
        )
    
    @pytest.mark.asyncio
    async def test_fallback_on_primary_failure(self, multi_provider_client, sample_request):
        """Test fallback when primary provider fails."""
        with patch.object(multi_provider_client.providers[0], 'generate_text') as mock_primary, \
             patch.object(multi_provider_client.providers[1], 'generate_text') as mock_fallback:
            
            # Primary provider fails
            mock_primary.side_effect = Exception("Primary provider failed")
            
            # Fallback provider succeeds
            mock_fallback.return_value = LLMResponse(
                success=True,
                content="Python is a programming language...",
                tokens_used=150
            )
            
            response = await multi_provider_client.generate_text(sample_request)
            
            assert response.success is True
            assert "Python is a programming language" in response.content
    
    @pytest.mark.asyncio
    async def test_all_providers_fail(self, multi_provider_client, sample_request):
        """Test when all providers fail."""
        with patch.object(multi_provider_client.providers[0], 'generate_text') as mock_primary, \
             patch.object(multi_provider_client.providers[1], 'generate_text') as mock_fallback, \
             patch.object(multi_provider_client.providers[2], 'generate_text') as mock_third:
            
            # All providers fail
            mock_primary.side_effect = Exception("Primary failed")
            mock_fallback.side_effect = Exception("Fallback failed")
            mock_third.side_effect = Exception("Third failed")
            
            response = await multi_provider_client.generate_text(sample_request)
            
            assert response.success is False
            assert "All providers failed" in response.error
    
    @pytest.mark.asyncio
    async def test_fallback_performance(self, multi_provider_client, sample_request):
        """Test fallback performance characteristics."""
        import time
        
        with patch.object(multi_provider_client.providers[0], 'generate_text') as mock_primary, \
             patch.object(multi_provider_client.providers[1], 'generate_text') as mock_fallback:
            
            # Primary fails after delay
            async def delayed_failure(*args, **kwargs):
                await asyncio.sleep(0.1)
                raise Exception("Primary failed")
            
            mock_primary.side_effect = delayed_failure
            
            # Fallback succeeds
            mock_fallback.return_value = LLMResponse(
                success=True,
                content="Fallback response",
                tokens_used=100
            )
            
            start_time = time.time()
            response = await multi_provider_client.generate_text(sample_request)
            end_time = time.time()
            
            assert response.success is True
            assert (end_time - start_time) < 2.0  # Should complete within 2 seconds

class TestRateLimiting:
    """Test rate limiting functionality."""
    
    @pytest.fixture
    def rate_limited_client(self):
        """Create rate-limited LLM client."""
        config = LLMConfig(
            provider="openai",
            api_key="test_key",
            model="gpt-4",
            rate_limit=10,  # 10 requests per minute
            rate_limit_window=60
        )
        return EnhancedLLMClient([config])
    
    @pytest.fixture
    def sample_request(self):
        """Sample LLM request."""
        return LLMRequest(
            prompt="Test request",
            max_tokens=100
        )
    
    @pytest.mark.asyncio
    async def test_rate_limit_enforcement(self, rate_limited_client, sample_request):
        """Test rate limit enforcement."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Response"
            mock_response.usage.total_tokens = 50
            mock_client.chat.completions.create.return_value = mock_response
            
            # Make multiple requests rapidly
            responses = []
            for i in range(15):  # Exceed rate limit
                response = await rate_limited_client.generate_text(sample_request)
                responses.append(response)
            
            # Some requests should be rate limited
            rate_limited_count = sum(1 for r in responses if not r.success and "rate limit" in r.error.lower())
            assert rate_limited_count > 0
    
    @pytest.mark.asyncio
    async def test_rate_limit_recovery(self, rate_limited_client, sample_request):
        """Test rate limit recovery after window."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Response"
            mock_response.usage.total_tokens = 50
            mock_client.chat.completions.create.return_value = mock_response
            
            # Make requests to hit rate limit
            for i in range(10):
                await rate_limited_client.generate_text(sample_request)
            
            # Wait for rate limit window to pass (simulated)
            with patch.object(rate_limited_client, '_rate_limiter') as mock_limiter:
                mock_limiter.is_allowed.return_value = True
                
                # Should succeed after rate limit window
                response = await rate_limited_client.generate_text(sample_request)
                assert response.success is True

class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.fixture
    def llm_client(self):
        """Create LLM client."""
        config = LLMConfig(
            provider="openai",
            api_key="test_key",
            model="gpt-4"
        )
        return EnhancedLLMClient([config])
    
    @pytest.fixture
    def sample_request(self):
        """Sample LLM request."""
        return LLMRequest(
            prompt="Test request",
            max_tokens=100
        )
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self, llm_client, sample_request):
        """Test network error handling."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            mock_client.chat.completions.create.side_effect = Exception("Network error")
            
            response = await llm_client.generate_text(sample_request)
            
            assert response.success is False
            assert "Network error" in response.error
    
    @pytest.mark.asyncio
    async def test_authentication_error_handling(self, llm_client, sample_request):
        """Test authentication error handling."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            from openai import AuthenticationError
            mock_client.chat.completions.create.side_effect = AuthenticationError("Invalid API key", response=Mock(), body={})
            
            response = await llm_client.generate_text(sample_request)
            
            assert response.success is False
            assert "authentication" in response.error.lower()
    
    @pytest.mark.asyncio
    async def test_timeout_error_handling(self, llm_client, sample_request):
        """Test timeout error handling."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            import asyncio
            mock_client.chat.completions.create.side_effect = asyncio.TimeoutError("Request timeout")
            
            response = await llm_client.generate_text(sample_request)
            
            assert response.success is False
            assert "timeout" in response.error.lower()

class TestPerformanceMonitoring:
    """Test performance monitoring functionality."""
    
    @pytest.fixture
    def monitored_client(self):
        """Create monitored LLM client."""
        config = LLMConfig(
            provider="openai",
            api_key="test_key",
            model="gpt-4"
        )
        return EnhancedLLMClient([config])
    
    @pytest.fixture
    def sample_request(self):
        """Sample LLM request."""
        return LLMRequest(
            prompt="Test request",
            max_tokens=100
        )
    
    @pytest.mark.asyncio
    async def test_response_time_monitoring(self, monitored_client, sample_request):
        """Test response time monitoring."""
        import time
        
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Response"
            mock_response.usage.total_tokens = 50
            mock_client.chat.completions.create.return_value = mock_response
            
            start_time = time.time()
            response = await monitored_client.generate_text(sample_request)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.success is True
            assert response_time < 5.0  # Should complete within 5 seconds
    
    @pytest.mark.asyncio
    async def test_token_usage_monitoring(self, monitored_client, sample_request):
        """Test token usage monitoring."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Response"
            mock_response.usage.total_tokens = 150
            mock_response.usage.prompt_tokens = 50
            mock_response.usage.completion_tokens = 100
            mock_client.chat.completions.create.return_value = mock_response
            
            response = await monitored_client.generate_text(sample_request)
            
            assert response.success is True
            assert response.tokens_used == 150
    
    @pytest.mark.asyncio
    async def test_cost_monitoring(self, monitored_client, sample_request):
        """Test cost monitoring."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Response"
            mock_response.usage.total_tokens = 100
            mock_client.chat.completions.create.return_value = mock_response
            
            response = await monitored_client.generate_text(sample_request)
            
            assert response.success is True
            # Cost should be calculated based on token usage
            assert hasattr(response, 'cost') or response.tokens_used > 0

class TestStreamingResponses:
    """Test streaming response functionality."""
    
    @pytest.fixture
    def streaming_client(self):
        """Create streaming LLM client."""
        config = LLMConfig(
            provider="openai",
            api_key="test_key",
            model="gpt-4"
        )
        return EnhancedLLMClient([config])
    
    @pytest.fixture
    def streaming_request(self):
        """Sample streaming request."""
        return LLMRequest(
            prompt="Generate a long response",
            max_tokens=1000,
            stream=True
        )
    
    @pytest.mark.asyncio
    async def test_streaming_response(self, streaming_client, streaming_request):
        """Test streaming response handling."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            # Mock streaming response
            async def mock_stream():
                chunks = [
                    Mock(choices=[Mock(delta=Mock(content="Hello"))]),
                    Mock(choices=[Mock(delta=Mock(content=" "))]),
                    Mock(choices=[Mock(delta=Mock(content="world"))])
                ]
                for chunk in chunks:
                    yield chunk
            
            mock_client.chat.completions.create.return_value = mock_stream()
            
            response = await streaming_client.generate_text(streaming_request)
            
            assert response.success is True
            assert "Hello world" in response.content

class TestTokenManagement:
    """Test token management functionality."""
    
    @pytest.fixture
    def token_client(self):
        """Create token-managed LLM client."""
        config = LLMConfig(
            provider="openai",
            api_key="test_key",
            model="gpt-4",
            max_tokens=1000
        )
        return EnhancedLLMClient([config])
    
    @pytest.fixture
    def sample_request(self):
        """Sample LLM request."""
        return LLMRequest(
            prompt="Test request",
            max_tokens=100
        )
    
    @pytest.mark.asyncio
    async def test_token_limit_enforcement(self, token_client, sample_request):
        """Test token limit enforcement."""
        # Create request that exceeds token limit
        large_request = LLMRequest(
            prompt="x" * 10000,  # Very long prompt
            max_tokens=100
        )
        
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            from openai import BadRequestError
            mock_client.chat.completions.create.side_effect = BadRequestError("Token limit exceeded", response=Mock(), body={})
            
            response = await token_client.generate_text(large_request)
            
            assert response.success is False
            assert "token" in response.error.lower()
    
    @pytest.mark.asyncio
    async def test_token_optimization(self, token_client, sample_request):
        """Test token optimization."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Optimized response"
            mock_response.usage.total_tokens = 50
            mock_client.chat.completions.create.return_value = mock_response
            
            response = await token_client.generate_text(sample_request)
            
            assert response.success is True
            assert response.tokens_used <= 100  # Within limit

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 