from shared.core.api.config import get_settings

settings = get_settings()
"""
Integration tests for LLM Client v3.

Tests cover:
- Real API calls to OpenAI and Anthropic
- Fallback mechanisms between providers
- Error handling and retry logic
- Rate limiting behavior
- Streaming functionality
- Embedding generation
- Health checks
- Performance under load

Authors:
- Universal Knowledge Platform Engineering Team
    
Version:
    1.0.0 (2024-12-28)
"""

import pytest
import asyncio
import time
import os
from typing import List, Dict, Any

# Add the project root to the path
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.core.llm_client_v3 import (
    EnhancedLLMClientV3,
    LLMConfig,
    LLMRequest,
    LLMProvider,
    LLMModel,
    get_llm_client_v3,
)


class TestLLMClientV3Integration:
    """Integration tests for LLM Client v3."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        # Ensure we have API keys for testing
        self.openai_key = settings.openai_api_key
        self.anthropic_key = settings.anthropic_api_key

        # Skip tests if no API keys are available
        if not self.openai_key and not self.anthropic_key:
            pytest.skip("No API keys available for integration tests")

    @pytest.mark.asyncio
    async def test_openai_integration(self):
        """Test OpenAI integration with real API calls."""
        if not self.openai_key:
            pytest.skip("OpenAI API key not available")

        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-3.5-turbo",
            api_key=self.openai_key,
            max_retries=2,
        )

        client = EnhancedLLMClientV3([config])

        # Test text generation
        request = LLMRequest(prompt="What is 2+2?", max_tokens=50, temperature=0.1)

        response = await client.generate_text(request)

        assert isinstance(response.content, str)
        assert len(response.content) > 0
        assert response.provider == LLMProvider.OPENAI
        assert response.token_usage["total_tokens"] > 0
        assert response.response_time_ms > 0

    @pytest.mark.asyncio
    async def test_anthropic_integration(self):
        """Test Anthropic integration with real API calls."""
        if not self.anthropic_key:
            pytest.skip("Anthropic API key not available")

        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-5-haiku-20241022",
            api_key=self.anthropic_key,
            max_retries=2,
        )

        client = EnhancedLLMClientV3([config])

        # Test text generation
        request = LLMRequest(prompt="What is 2+2?", max_tokens=50, temperature=0.1)

        response = await client.generate_text(request)

        assert isinstance(response.content, str)
        assert len(response.content) > 0
        assert response.provider == LLMProvider.ANTHROPIC
        assert response.token_usage["total_tokens"] > 0
        assert response.response_time_ms > 0

    @pytest.mark.asyncio
    async def test_fallback_mechanism(self):
        """Test fallback mechanism between providers."""
        if not self.openai_key or not self.anthropic_key:
            pytest.skip("Both OpenAI and Anthropic API keys required for fallback test")

        configs = [
            LLMConfig(
                provider=LLMProvider.OPENAI,
                model="gpt-3.5-turbo",
                api_key=self.openai_key,
                max_retries=1,
            ),
            LLMConfig(
                provider=LLMProvider.ANTHROPIC,
                model="claude-3-5-haiku-20241022",
                api_key=self.anthropic_key,
                max_retries=1,
            ),
        ]

        client = EnhancedLLMClientV3(configs)

        # Test that fallback works
        request = LLMRequest(prompt="What is 2+2?", max_tokens=50, temperature=0.1)

        response = await client.generate_text(request)

        assert isinstance(response.content, str)
        assert len(response.content) > 0
        assert response.provider in [LLMProvider.OPENAI, LLMProvider.ANTHROPIC]
        assert client.metrics["total_requests"] == 1
        assert client.metrics["successful_requests"] == 1

    @pytest.mark.asyncio
    async def test_streaming_integration(self):
        """Test streaming functionality."""
        if not self.openai_key:
            pytest.skip("OpenAI API key not available")

        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-3.5-turbo",
            api_key=self.openai_key,
            max_retries=2,
        )

        client = EnhancedLLMClientV3([config])

        # Test streaming
        request = LLMRequest(
            prompt="Count from 1 to 5:", max_tokens=50, temperature=0.1, stream=True
        )

        chunks = []
        async for chunk in client.generate_stream(request):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
        assert len("".join(chunks)) > 0

    @pytest.mark.asyncio
    async def test_embedding_integration(self):
        """Test embedding generation."""
        if not self.openai_key:
            pytest.skip("OpenAI API key not available")

        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-3.5-turbo",
            api_key=self.openai_key,
            embedding_model="text-embedding-3-small",
        )

        client = EnhancedLLMClientV3([config])

        # Test embedding generation
        text = "This is a test sentence for embedding generation."
        embedding = await client.create_embedding(text)

        assert isinstance(embedding, list)
        assert len(embedding) == 1536  # text-embedding-3-small dimension
        assert all(isinstance(x, float) for x in embedding)
        assert all(-1 <= x <= 1 for x in embedding)

    @pytest.mark.asyncio
    async def test_health_check_integration(self):
        """Test health check functionality."""
        if not self.openai_key:
            pytest.skip("OpenAI API key not available")

        config = LLMConfig(
            provider=LLMProvider.OPENAI, model="gpt-3.5-turbo", api_key=self.openai_key
        )

        client = EnhancedLLMClientV3([config])

        # Test health check
        health_status = await client.health_check()

        assert isinstance(health_status, dict)
        assert "provider_0" in health_status
        assert health_status["provider_0"]["healthy"] is True
        assert "info" in health_status["provider_0"]

    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test error handling with invalid API key."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-3.5-turbo",
            api_key="invalid-key",
            max_retries=1,
        )

        client = EnhancedLLMClientV3([config])

        request = LLMRequest(prompt="Test prompt", max_tokens=50)

        with pytest.raises(Exception):
            await client.generate_text(request)

    @pytest.mark.asyncio
    async def test_rate_limiting_integration(self):
        """Test rate limiting behavior."""
        if not self.openai_key:
            pytest.skip("OpenAI API key not available")

        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-3.5-turbo",
            api_key=self.openai_key,
            requests_per_minute=10,
            tokens_per_minute=1000,
        )

        client = EnhancedLLMClientV3([config])

        # Make multiple requests to test rate limiting
        requests = []
        for i in range(3):
            request = LLMRequest(
                prompt=f"Test request {i}", max_tokens=10, temperature=0.1
            )
            requests.append(request)

        # Execute requests concurrently
        start_time = time.time()
        responses = await asyncio.gather(
            *[client.generate_text(req) for req in requests]
        )
        end_time = time.time()

        assert len(responses) == 3
        assert all(isinstance(r, type(responses[0])) for r in responses)
        assert end_time - start_time > 0  # Should take some time due to rate limiting

    @pytest.mark.asyncio
    async def test_performance_metrics(self):
        """Test performance metrics collection."""
        if not self.openai_key:
            pytest.skip("OpenAI API key not available")

        config = LLMConfig(
            provider=LLMProvider.OPENAI, model="gpt-3.5-turbo", api_key=self.openai_key
        )

        client = EnhancedLLMClientV3([config])

        # Make a request
        request = LLMRequest(prompt="Test prompt for metrics", max_tokens=50)

        await client.generate_text(request)

        # Check metrics
        metrics = client.get_metrics()

        assert metrics["total_requests"] == 1
        assert metrics["successful_requests"] == 1
        assert metrics["failed_requests"] == 0
        assert metrics["total_tokens"] > 0
        assert metrics["total_response_time"] > 0
        assert "avg_response_time_ms" in metrics
        assert "providers" in metrics

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        if not self.openai_key:
            pytest.skip("OpenAI API key not available")

        config = LLMConfig(
            provider=LLMProvider.OPENAI, model="gpt-3.5-turbo", api_key=self.openai_key
        )

        client = EnhancedLLMClientV3([config])

        # Create multiple concurrent requests
        async def make_request(i: int):
            request = LLMRequest(
                prompt=f"Concurrent test request {i}", max_tokens=20, temperature=0.1
            )
            return await client.generate_text(request)

        # Execute 5 concurrent requests
        start_time = time.time()
        responses = await asyncio.gather(*[make_request(i) for i in range(5)])
        end_time = time.time()

        assert len(responses) == 5
        assert all(isinstance(r, type(responses[0])) for r in responses)
        assert client.metrics["total_requests"] == 5
        assert client.metrics["successful_requests"] == 5

    @pytest.mark.asyncio
    async def test_large_prompt_handling(self):
        """Test handling of large prompts."""
        if not self.openai_key:
            pytest.skip("OpenAI API key not available")

        config = LLMConfig(
            provider=LLMProvider.OPENAI, model="gpt-3.5-turbo", api_key=self.openai_key
        )

        client = EnhancedLLMClientV3([config])

        # Create a large prompt
        large_prompt = "This is a test. " * 1000  # ~6000 words

        request = LLMRequest(prompt=large_prompt, max_tokens=50, temperature=0.1)

        response = await client.generate_text(request)

        assert isinstance(response.content, str)
        assert len(response.content) > 0
        assert response.token_usage["total_tokens"] > 0

    @pytest.mark.asyncio
    async def test_system_message_integration(self):
        """Test system message functionality."""
        if not self.openai_key:
            pytest.skip("OpenAI API key not available")

        config = LLMConfig(
            provider=LLMProvider.OPENAI, model="gpt-3.5-turbo", api_key=self.openai_key
        )

        client = EnhancedLLMClientV3([config])

        request = LLMRequest(
            prompt="What is your role?",
            system_message="You are a helpful math tutor. Always provide step-by-step explanations.",
            max_tokens=100,
            temperature=0.1,
        )

        response = await client.generate_text(request)

        assert isinstance(response.content, str)
        assert len(response.content) > 0
        # Should mention being a math tutor or providing explanations
        assert any(
            keyword in response.content.lower()
            for keyword in ["math", "tutor", "explain", "step"]
        )

    @pytest.mark.asyncio
    async def test_global_client_integration(self):
        """Test global client instance."""
        if not self.openai_key:
            pytest.skip("OpenAI API key not available")

        client = get_llm_client_v3()

        # Test that global client works
        request = LLMRequest(
            prompt="Test global client", max_tokens=50, temperature=0.1
        )

        response = await client.generate_text(request)

        assert isinstance(response.content, str)
        assert len(response.content) > 0


class TestLLMClientV3EdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_empty_prompt(self):
        """Test handling of empty prompt."""
        # Use mock provider for this test
        config = LLMConfig(
            provider=LLMProvider.MOCK, model="mock-model", api_key="mock-key"
        )

        client = EnhancedLLMClientV3([config])

        request = LLMRequest(prompt="")
        response = await client.generate_text(request)

        assert isinstance(response.content, str)
        assert len(response.content) > 0

    @pytest.mark.asyncio
    async def test_no_providers(self):
        """Test behavior when no providers are configured."""
        client = EnhancedLLMClientV3([])

        request = LLMRequest(prompt="Test prompt")

        with pytest.raises(Exception) as exc_info:
            await client.generate_text(request)

        assert "no_providers" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_model(self):
        """Test behavior with invalid model."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI, model="invalid-model", api_key="test-key"
        )

        client = EnhancedLLMClientV3([config])

        request = LLMRequest(prompt="Test prompt")

        with pytest.raises(Exception):
            await client.generate_text(request)

    @pytest.mark.asyncio
    async def test_very_long_prompt(self):
        """Test handling of very long prompts."""
        # Use mock provider for this test
        config = LLMConfig(
            provider=LLMProvider.MOCK, model="mock-model", api_key="mock-key"
        )

        client = EnhancedLLMClientV3([config])

        # Create a very long prompt
        very_long_prompt = "Test. " * 10000  # ~60,000 words

        request = LLMRequest(prompt=very_long_prompt, max_tokens=50)

        response = await client.generate_text(request)

        assert isinstance(response.content, str)
        assert len(response.content) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
