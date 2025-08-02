"""
Test Orchestrator LLM Selection - Universal Knowledge Platform
Comprehensive tests for enhanced LLM provider selection and routing.

This module tests the enhanced orchestrator's LLM selection functionality
including query classification, provider selection, fallback chains,
and token limit handling.

Test Coverage:
- Correct provider selection based on query classification
- Provider failure simulation and fallback triggering
- Token overflow detection and correct fallback routing
- Query classification accuracy
- Provider health monitoring
- Comprehensive logging and transparency

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    1.0.0 (2024-12-28)
"""

import asyncio
import pytest
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, AsyncMock, MagicMock, patch

from shared.core.llm_client_enhanced import (
    EnhancedLLMClient,
    LLMProvider,
    QueryType,
    LLMRequest,
    LLMResponse,
    ProviderTokenLimits,
    ProviderConfig
)


class MockOllamaProvider:
    """Mock Ollama provider for testing."""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.token_limits = ProviderTokenLimits(
            max_context_tokens=4000,
            max_total_tokens=4000,
            cost_per_1k_tokens=0.0,
            is_free=True
        )
    
    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4
    
    def can_handle_request(self, request: LLMRequest) -> bool:
        total_text = request.query
        if request.context:
            total_text = f"{request.context}\n\n{request.query}"
        if request.system_message:
            total_text = f"{request.system_message}\n\n{total_text}"
        
        estimated_tokens = self.estimate_tokens(total_text) + request.max_tokens
        return estimated_tokens <= self.token_limits.max_total_tokens
    
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            content="Mock Ollama response",
            provider=LLMProvider.OLLAMA,
            model="llama3.2:3b",
            response_time_ms=100.0,
            token_usage={"prompt_tokens": 50, "completion_tokens": 20, "total_tokens": 70},
            metadata={"mock": True},
            query_id=request.query_id
        )
    
    async def health_check(self) -> bool:
        return True
    
    def get_provider_info(self) -> Dict[str, Any]:
        return {
            "name": "Ollama",
            "provider": LLMProvider.OLLAMA,
            "model": "llama3.2:3b",
            "token_limits": self.token_limits,
            "is_free": True
        }


class MockHuggingFaceProvider:
    """Mock HuggingFace provider for testing."""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.token_limits = ProviderTokenLimits(
            max_context_tokens=2000,
            max_total_tokens=2000,
            cost_per_1k_tokens=0.0,
            is_free=True
        )
    
    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4
    
    def can_handle_request(self, request: LLMRequest) -> bool:
        total_text = request.query
        if request.context:
            total_text = f"{request.context}\n\n{request.query}"
        if request.system_message:
            total_text = f"{request.system_message}\n\n{total_text}"
        
        estimated_tokens = self.estimate_tokens(total_text) + request.max_tokens
        return estimated_tokens <= self.token_limits.max_total_tokens
    
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            content="Mock HuggingFace response",
            provider=LLMProvider.HUGGINGFACE,
            model="microsoft/DialoGPT-medium",
            response_time_ms=150.0,
            token_usage={"prompt_tokens": 40, "completion_tokens": 15, "total_tokens": 55},
            metadata={"mock": True},
            query_id=request.query_id
        )
    
    async def health_check(self) -> bool:
        return True
    
    def get_provider_info(self) -> Dict[str, Any]:
        return {
            "name": "HuggingFace",
            "provider": LLMProvider.HUGGINGFACE,
            "model": "microsoft/DialoGPT-medium",
            "token_limits": self.token_limits,
            "is_free": True
        }


class MockOpenAIProvider:
    """Mock OpenAI provider for testing."""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.token_limits = ProviderTokenLimits(
            max_context_tokens=16000,
            max_total_tokens=16000,
            cost_per_1k_tokens=0.002,
            is_free=False
        )
    
    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4
    
    def can_handle_request(self, request: LLMRequest) -> bool:
        total_text = request.query
        if request.context:
            total_text = f"{request.context}\n\n{request.query}"
        if request.system_message:
            total_text = f"{request.system_message}\n\n{total_text}"
        
        estimated_tokens = self.estimate_tokens(total_text) + request.max_tokens
        return estimated_tokens <= self.token_limits.max_total_tokens
    
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            content="Mock OpenAI response",
            provider=LLMProvider.OPENAI,
            model="gpt-3.5-turbo",
            response_time_ms=200.0,
            token_usage={"prompt_tokens": 60, "completion_tokens": 25, "total_tokens": 85},
            metadata={"mock": True},
            query_id=request.query_id
        )
    
    async def health_check(self) -> bool:
        return True
    
    def get_provider_info(self) -> Dict[str, Any]:
        return {
            "name": "OpenAI",
            "provider": LLMProvider.OPENAI,
            "model": "gpt-3.5-turbo",
            "token_limits": self.token_limits,
            "is_free": False
        }


class TestOrchestratorLLMSelection:
    """Test suite for enhanced orchestrator LLM selection."""
    
    @pytest.fixture
    async def enhanced_llm_client(self):
        """Create enhanced LLM client with mock providers."""
        client = EnhancedLLMClient()
        
        # Replace providers with mocks
        ollama_config = ProviderConfig(
            name=LLMProvider.OLLAMA,
            base_url="http://localhost:11434",
            api_key=None,
            models=["llama3.2:3b"],
            timeout=60
        )
        client.providers[LLMProvider.OLLAMA] = MockOllamaProvider(ollama_config)
        
        hf_config = ProviderConfig(
            name=LLMProvider.HUGGINGFACE,
            base_url="https://api-inference.huggingface.co",
            api_key="mock_key",
            models=["microsoft/DialoGPT-medium"],
            timeout=30
        )
        client.providers[LLMProvider.HUGGINGFACE] = MockHuggingFaceProvider(hf_config)
        
        openai_config = ProviderConfig(
            name=LLMProvider.OPENAI,
            base_url="https://api.openai.com",
            api_key="mock_key",
            models=["gpt-3.5-turbo"],
            timeout=30
        )
        client.providers[LLMProvider.OPENAI] = MockOpenAIProvider(openai_config)
        
        # Initialize statistics
        for provider in client.providers:
            client.provider_stats[provider] = {
                "calls": 0,
                "success": 0,
                "failures": 0,
                "avg_time": 0.0,
                "last_used": None
            }
        
        yield client
    
    async def test_query_classification_simple_factual(self, enhanced_llm_client):
        """Test correct provider selection for simple factual queries."""
        # Simple factual queries should prefer Ollama
        simple_queries = [
            "What is Python?",
            "Who is Albert Einstein?",
            "When was the first computer invented?",
            "Where is the capital of France?",
            "How many planets are in our solar system?",
            "Define machine learning"
        ]
        
        for query in simple_queries:
            selected_provider = await enhanced_llm_client.select_llm_provider(query)
            assert selected_provider == LLMProvider.OLLAMA, f"Expected Ollama for query: {query}"
    
    async def test_query_classification_complex_synthesis(self, enhanced_llm_client):
        """Test correct provider selection for complex synthesis queries."""
        # Complex synthesis queries should prefer HuggingFace
        synthesis_queries = [
            "Analyze the impact of climate change on agriculture",
            "Compare different machine learning algorithms",
            "Research the history of artificial intelligence",
            "Study the effects of social media on society",
            "Investigate the relationship between diet and health",
            "Synthesize information about renewable energy"
        ]
        
        for query in synthesis_queries:
            selected_provider = await enhanced_llm_client.select_llm_provider(query)
            assert selected_provider == LLMProvider.HUGGINGFACE, f"Expected HuggingFace for query: {query}"
    
    async def test_query_classification_large_context(self, enhanced_llm_client):
        """Test correct provider selection for large context queries."""
        # Large context queries should prefer OpenAI
        large_context_query = "This is a very long query that contains a lot of context and information " * 50
        
        selected_provider = await enhanced_llm_client.select_llm_provider(large_context_query)
        assert selected_provider == LLMProvider.OPENAI, "Expected OpenAI for large context query"
    
    async def test_provider_failure_fallback(self, enhanced_llm_client):
        """Test provider failure and fallback chain."""
        # Mock Ollama to fail
        class FailingOllamaProvider(MockOllamaProvider):
            async def health_check(self) -> bool:
                return False
            
            async def generate_text(self, request: LLMRequest) -> LLMResponse:
                raise Exception("Ollama provider failed")
        
        # Replace Ollama provider with failing one
        ollama_config = ProviderConfig(
            name=LLMProvider.OLLAMA,
            base_url="http://localhost:11434",
            api_key=None,
            models=["llama3.2:3b"],
            timeout=60
        )
        enhanced_llm_client.providers[LLMProvider.OLLAMA] = FailingOllamaProvider(ollama_config)
        
        # Test simple factual query - should fallback to HuggingFace
        query = "What is Python?"
        response = await enhanced_llm_client.dispatch(query, query_id="test_fallback")
        
        # Should use HuggingFace as fallback
        assert response.provider == LLMProvider.HUGGINGFACE, "Expected fallback to HuggingFace"
        assert "Mock HuggingFace response" in response.content
    
    async def test_token_overflow_detection(self, enhanced_llm_client):
        """Test token overflow detection and correct fallback routing."""
        # Create a request that exceeds Ollama's token limits
        large_context = "This is a very large context " * 1000  # ~25K characters
        large_query = "This is a very large query " * 500  # ~12K characters
        
        # Mock Ollama to return False for can_handle_request
        class LimitedOllamaProvider(MockOllamaProvider):
            def can_handle_request(self, request: LLMRequest) -> bool:
                return False  # Simulate token limit exceeded
        
        # Replace Ollama provider
        ollama_config = ProviderConfig(
            name=LLMProvider.OLLAMA,
            base_url="http://localhost:11434",
            api_key=None,
            models=["llama3.2:3b"],
            timeout=60
        )
        enhanced_llm_client.providers[LLMProvider.OLLAMA] = LimitedOllamaProvider(ollama_config)
        
        # Test query with large context - should skip Ollama and use HuggingFace
        # Use a simple factual query to ensure Ollama is selected first
        simple_query = "What is Python?"
        selected_provider = await enhanced_llm_client.select_llm_provider(simple_query, context_size=5000)
        assert selected_provider == LLMProvider.HUGGINGFACE, "Expected HuggingFace for token overflow"
    
    async def test_provider_health_monitoring(self, enhanced_llm_client):
        """Test provider health monitoring."""
        # Test health check for all providers
        health_status = await enhanced_llm_client.health_check()
        
        assert LLMProvider.OLLAMA.value in health_status
        assert LLMProvider.HUGGINGFACE.value in health_status
        assert LLMProvider.OPENAI.value in health_status
        
        for provider_name, status in health_status.items():
            assert status["status"] == "healthy", f"Provider {provider_name} should be healthy"
    
    async def test_comprehensive_logging(self, enhanced_llm_client):
        """Test comprehensive logging and transparency."""
        query = "What is machine learning?"
        query_id = "test_logging_123"
        
        # Capture logs (this would require more sophisticated logging capture)
        response = await enhanced_llm_client.dispatch(query, query_id=query_id)
        
        # Verify response contains expected metadata
        assert response.query_id == query_id
        assert response.provider in [LLMProvider.OLLAMA, LLMProvider.HUGGINGFACE, LLMProvider.OPENAI]
        assert response.content is not None
        assert response.response_time_ms > 0
    
    async def test_provider_statistics_tracking(self, enhanced_llm_client):
        """Test provider statistics tracking."""
        # Make several requests
        queries = [
            "What is Python?",
            "Analyze machine learning trends",
            "This is a very long query " * 100
        ]
        
        for query in queries:
            await enhanced_llm_client.dispatch(query, query_id=f"stats_test_{hash(query) % 1000}")
        
        # Check statistics
        stats = enhanced_llm_client.get_provider_stats()
        
        for provider_name, provider_stats in stats.items():
            assert provider_stats["calls"] >= 0
            assert provider_stats["success"] >= 0
            assert provider_stats["failures"] >= 0
            assert provider_stats["success_rate"] >= 0.0
            assert provider_stats["avg_time_ms"] >= 0.0
    
    async def test_fallback_chain_complete_failure(self, enhanced_llm_client):
        """Test complete fallback chain failure."""
        # Mock all providers to fail
        class FailingProvider:
            async def health_check(self) -> bool:
                return False
            
            async def generate_text(self, request: LLMRequest) -> LLMResponse:
                raise Exception("Provider failed")
            
            def can_handle_request(self, request: LLMRequest) -> bool:
                return True
        
        # Replace all providers with failing ones
        for provider_name in [LLMProvider.OLLAMA, LLMProvider.HUGGINGFACE, LLMProvider.OPENAI]:
            config = ProviderConfig(
                name=provider_name,
                base_url="http://mock.com",
                api_key="mock_key",
                models=["mock_model"],
                timeout=30
            )
            enhanced_llm_client.providers[provider_name] = FailingProvider()
        
        # Test that all providers failing raises an exception
        # The retry mechanism wraps the exception, so we need to catch the retry error
        with pytest.raises(Exception):
            await enhanced_llm_client.dispatch("Test query", query_id="complete_failure_test")
    
    async def test_token_limit_awareness(self, enhanced_llm_client):
        """Test token limit awareness for different providers."""
        # Test Ollama token limits
        ollama_provider = enhanced_llm_client.providers[LLMProvider.OLLAMA]
        
        # Small request should be handled
        small_request = LLMRequest(query="What is Python?", max_tokens=100)
        assert ollama_provider.can_handle_request(small_request)
        
        # Large request should not be handled
        large_request = LLMRequest(
            query="This is a very large query " * 1000,  # ~25K characters
            max_tokens=1000
        )
        assert not ollama_provider.can_handle_request(large_request)
        
        # Test HuggingFace token limits
        hf_provider = enhanced_llm_client.providers[LLMProvider.HUGGINGFACE]
        
        # Medium request should be handled
        medium_request = LLMRequest(query="Analyze this data", max_tokens=500)
        assert hf_provider.can_handle_request(medium_request)
        
        # Very large request should not be handled
        very_large_request = LLMRequest(
            query="This is a very large query " * 800,  # ~20K characters
            max_tokens=1000
        )
        assert not hf_provider.can_handle_request(very_large_request)
        
        # Test OpenAI token limits (should handle larger requests)
        openai_provider = enhanced_llm_client.providers[LLMProvider.OPENAI]
        
        # Large request should be handled by OpenAI
        large_openai_request = LLMRequest(
            query="This is a large query " * 2000,  # ~50K characters
            max_tokens=1000
        )
        assert openai_provider.can_handle_request(large_openai_request)
    
    async def test_query_id_tracking(self, enhanced_llm_client):
        """Test query ID tracking throughout the process."""
        query = "What is artificial intelligence?"
        query_id = "test_query_456"
        
        response = await enhanced_llm_client.dispatch(query, query_id=query_id)
        
        # Verify query ID is preserved
        assert response.query_id == query_id
        
        # Verify provider stats are updated
        stats = enhanced_llm_client.get_provider_stats()
        provider_stats = stats[response.provider.value]
        assert provider_stats["calls"] > 0
        assert provider_stats["success"] > 0
    
    async def test_concurrent_requests(self, enhanced_llm_client):
        """Test concurrent request handling."""
        queries = [
            "What is Python?",
            "Analyze machine learning",
            "This is a long query " * 50
        ]
        
        # Make concurrent requests
        tasks = [
            enhanced_llm_client.dispatch(query, query_id=f"concurrent_{i}")
            for i, query in enumerate(queries)
        ]
        
        responses = await asyncio.gather(*tasks)
        
        # Verify all responses are valid
        for response in responses:
            assert response.content is not None
            assert response.provider in [LLMProvider.OLLAMA, LLMProvider.HUGGINGFACE, LLMProvider.OPENAI]
            assert response.response_time_ms > 0
    
    async def test_provider_selection_edge_cases(self, enhanced_llm_client):
        """Test edge cases in provider selection."""
        # Test very short query
        selected_provider = await enhanced_llm_client.select_llm_provider("Hi")
        assert selected_provider in [LLMProvider.OLLAMA, LLMProvider.HUGGINGFACE, LLMProvider.OPENAI]
        
        # Test query with special characters
        special_query = "What is AI? 🤖 #machinelearning @tech"
        selected_provider = await enhanced_llm_client.select_llm_provider(special_query)
        assert selected_provider in [LLMProvider.OLLAMA, LLMProvider.HUGGINGFACE, LLMProvider.OPENAI]
        
        # Test empty query - should handle gracefully
        try:
            await enhanced_llm_client.select_llm_provider("")
        except Exception:
            # Expected behavior for empty query
            pass


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 