#!/usr/bin/env python3
"""
Integration Tests for Resilience System

Tests the comprehensive resilience features:
- Circuit breaker functionality and state transitions
- Graceful degradation with fallback responses
- Error boundary handling and trace IDs
- System health monitoring and recovery
- Chaos testing with provider failures

Following enterprise testing standards for resilience and fault tolerance.
"""

import asyncio
import time
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import pytest
from unittest.mock import Mock, patch, AsyncMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import resilience components
from services.gateway.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerManager,
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitBreakerOpenError,
    CircuitBreakerTimeoutError,
    CircuitBreakerFailureError,
    CircuitState
)

from services.gateway.resilience.graceful_degradation import (
    GracefulDegradationManager,
    ErrorBoundary,
    FallbackResponse,
    DegradationLevel,
    get_fallback_response,
    check_fallback_needed,
    get_degradation_status
)


class TestCircuitBreaker:
    """Test circuit breaker functionality."""
    
    @pytest.fixture
    def config(self):
        """Create circuit breaker configuration for testing."""
        return CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=5,  # Short timeout for testing
            success_threshold=2,
            timeout_threshold=2.0,
            window_size=10,
            max_failures_per_window=5
        )
    
    @pytest.fixture
    def circuit_breaker(self, config):
        """Create circuit breaker instance."""
        return CircuitBreaker("test-provider", config)
    
    async def test_circuit_breaker_initial_state(self, circuit_breaker):
        """Test initial circuit breaker state."""
        assert circuit_breaker.state == CircuitState.CLOSED
        assert circuit_breaker.stats.total_requests == 0
        assert circuit_breaker.stats.failed_requests == 0
    
    async def test_circuit_breaker_success(self, circuit_breaker):
        """Test successful request handling."""
        async def success_func():
            await asyncio.sleep(0.1)
            return "success"
        
        result = await circuit_breaker.call(success_func)
        
        assert result == "success"
        assert circuit_breaker.state == CircuitState.CLOSED
        assert circuit_breaker.stats.total_requests == 1
        assert circuit_breaker.stats.successful_requests == 1
        assert circuit_breaker.stats.failed_requests == 0
    
    async def test_circuit_breaker_failure(self, circuit_breaker):
        """Test failure handling."""
        async def failure_func():
            raise ValueError("Test failure")
        
        with pytest.raises(CircuitBreakerFailureError):
            await circuit_breaker.call(failure_func)
        
        assert circuit_breaker.state == CircuitState.CLOSED  # Not enough failures yet
        assert circuit_breaker.stats.total_requests == 1
        assert circuit_breaker.stats.failed_requests == 1
        assert circuit_breaker.stats.current_failure_count == 1
    
    async def test_circuit_breaker_opening(self, circuit_breaker):
        """Test circuit breaker opening after threshold failures."""
        async def failure_func():
            raise ValueError("Test failure")
        
        # Trigger failures up to threshold
        for i in range(3):
            with pytest.raises(CircuitBreakerFailureError):
                await circuit_breaker.call(failure_func)
        
        # Circuit should now be open
        assert circuit_breaker.state == CircuitState.OPEN
        assert circuit_breaker.stats.circuit_opens == 1
    
    async def test_circuit_breaker_timeout(self, circuit_breaker):
        """Test timeout handling."""
        async def timeout_func():
            await asyncio.sleep(3.0)  # Longer than timeout threshold
            return "should not reach here"
        
        with pytest.raises(CircuitBreakerTimeoutError):
            await circuit_breaker.call(timeout_func)
        
        assert circuit_breaker.stats.timeout_requests == 1
        assert circuit_breaker.stats.current_failure_count == 1
    
    async def test_circuit_breaker_recovery(self, circuit_breaker):
        """Test circuit breaker recovery."""
        # First, open the circuit
        async def failure_func():
            raise ValueError("Test failure")
        
        for i in range(3):
            with pytest.raises(CircuitBreakerFailureError):
                await circuit_breaker.call(failure_func)
        
        assert circuit_breaker.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        await asyncio.sleep(6)  # Longer than recovery_timeout
        
        # Try a successful request
        async def success_func():
            return "success"
        
        result = await circuit_breaker.call(success_func)
        
        assert result == "success"
        assert circuit_breaker.state == CircuitState.HALF_OPEN
    
    async def test_circuit_breaker_half_open_success(self, circuit_breaker):
        """Test successful recovery in half-open state."""
        # Open circuit first
        async def failure_func():
            raise ValueError("Test failure")
        
        for i in range(3):
            with pytest.raises(CircuitBreakerFailureError):
                await circuit_breaker.call(failure_func)
        
        assert circuit_breaker.state == CircuitState.OPEN
        
        # Wait for recovery
        await asyncio.sleep(6)
        
        # Success in half-open should close circuit
        async def success_func():
            return "success"
        
        for i in range(2):  # success_threshold
            result = await circuit_breaker.call(success_func)
            assert result == "success"
        
        assert circuit_breaker.state == CircuitState.CLOSED
        assert circuit_breaker.stats.circuit_closes == 1
    
    async def test_circuit_breaker_half_open_failure(self, circuit_breaker):
        """Test failure in half-open state."""
        # Open circuit first
        async def failure_func():
            raise ValueError("Test failure")
        
        for i in range(3):
            with pytest.raises(CircuitBreakerFailureError):
                await circuit_breaker.call(failure_func)
        
        assert circuit_breaker.state == CircuitState.OPEN
        
        # Wait for recovery
        await asyncio.sleep(6)
        
        # Failure in half-open should reopen circuit
        with pytest.raises(CircuitBreakerOpenError):
            await circuit_breaker.call(failure_func)
        
        assert circuit_breaker.state == CircuitState.OPEN


class TestCircuitBreakerManager:
    """Test circuit breaker manager functionality."""
    
    @pytest.fixture
    def manager(self):
        """Create circuit breaker manager."""
        return CircuitBreakerManager()
    
    async def test_get_circuit_breaker(self, manager):
        """Test getting circuit breaker for provider."""
        circuit_breaker = manager.get_circuit_breaker("test-provider")
        
        assert isinstance(circuit_breaker, CircuitBreaker)
        assert circuit_breaker.provider_name == "test-provider"
        assert circuit_breaker.state == CircuitState.CLOSED
    
    async def test_call_with_fallback(self, manager):
        """Test calling with fallback logic."""
        providers = ["provider1", "provider2", "provider3"]
        
        async def provider_func(provider: str):
            if provider == "provider1":
                raise ValueError("Provider 1 failed")
            elif provider == "provider2":
                raise ValueError("Provider 2 failed")
            else:
                return f"Success from {provider}"
        
        result, used_provider = await manager.call_with_fallback(providers, provider_func)
        
        assert result == "Success from provider3"
        assert used_provider == "provider3"
    
    async def test_call_with_fallback_all_fail(self, manager):
        """Test fallback when all providers fail."""
        providers = ["provider1", "provider2"]
        
        async def failure_func(provider: str):
            raise ValueError(f"{provider} failed")
        
        with pytest.raises(CircuitBreakerError):
            await manager.call_with_fallback(providers, failure_func)
    
    async def test_get_all_status(self, manager):
        """Test getting status of all circuit breakers."""
        # Create some circuit breakers
        manager.get_circuit_breaker("provider1")
        manager.get_circuit_breaker("provider2")
        
        status = manager.get_all_status()
        
        assert "provider1" in status
        assert "provider2" in status
        assert status["provider1"]["provider"] == "provider1"
        assert status["provider2"]["provider"] == "provider2"


class TestGracefulDegradation:
    """Test graceful degradation functionality."""
    
    @pytest.fixture
    def degradation_manager(self):
        """Create degradation manager."""
        return GracefulDegradationManager()
    
    @pytest.fixture
    def sample_sources(self):
        """Create sample sources for testing."""
        return [
            {
                "title": "Test Source 1",
                "url": "https://example.com/1",
                "snippet": "This is a test snippet about programming.",
                "domain": "example.com"
            },
            {
                "title": "Test Source 2",
                "url": "https://docs.example.com/2",
                "snippet": "Another test snippet with technical details.",
                "domain": "docs.example.com"
            }
        ]
    
    async def test_generate_fallback_response(self, degradation_manager, sample_sources):
        """Test fallback response generation."""
        query = "How to fix React hydration error?"
        
        with patch('services.gateway.resilience.graceful_degradation.get_request_id') as mock_get_id:
            mock_get_id.return_value = "test-trace-id"
            
            response = await degradation_manager.generate_fallback_response(
                query=query,
                sources=sample_sources
            )
        
        assert isinstance(response, FallbackResponse)
        assert response.provider == "fallback_free_tier"
        assert response.degradation_level == DegradationLevel.LLM_DEGRADED
        assert response.trace_id == "test-trace-id"
        assert "Test Source 1" in response.answer
        assert "example.com" in response.answer
        assert "Trace ID" in response.answer
    
    async def test_generate_fallback_response_no_sources(self, degradation_manager):
        """Test fallback response with no sources."""
        query = "Test query"
        
        response = await degradation_manager.generate_fallback_response(
            query=query,
            sources=[]
        )
        
        assert response.provider == "fallback_free_tier"
        assert "No relevant sources were found" in response.answer
    
    async def test_generate_fallback_response_with_error(self, degradation_manager, sample_sources):
        """Test fallback response with error message."""
        query = "Test query"
        error_message = "LLM service unavailable"
        
        response = await degradation_manager.generate_fallback_response(
            query=query,
            sources=sample_sources,
            error_message=error_message
        )
        
        assert error_message in response.answer
        assert response.error_message == error_message
    
    async def test_source_summary_generation(self, degradation_manager, sample_sources):
        """Test source summary generation."""
        summary = await degradation_manager._generate_source_summary(sample_sources)
        
        assert "Key findings:" in summary
        assert "Test Source 1" in summary
        assert "Test Source 2" in summary
        assert "2 different domains" in summary
    
    def test_template_selection(self, degradation_manager):
        """Test template selection based on query type."""
        # Technical query
        technical_query = "How to fix JavaScript error?"
        template_key = degradation_manager._determine_template_key(technical_query)
        assert template_key == "technical"
        
        # General query
        general_query = "What is the weather like?"
        template_key = degradation_manager._determine_template_key(general_query)
        assert template_key == "general"
    
    def test_technical_points_extraction(self, degradation_manager, sample_sources):
        """Test technical points extraction."""
        # Add technical content to sources
        technical_sources = [
            {
                "title": "Error Fix Guide",
                "url": "https://example.com/error",
                "snippet": "To fix this error, you need to update your code. The solution involves changing the function call.",
                "domain": "example.com"
            }
        ]
        
        technical_points = degradation_manager._extract_technical_points(technical_sources)
        
        assert "To fix this error" in technical_points
        assert "function call" in technical_points


class TestErrorBoundary:
    """Test error boundary functionality."""
    
    @pytest.fixture
    def error_boundary(self):
        """Create error boundary."""
        degradation_manager = GracefulDegradationManager()
        return ErrorBoundary(degradation_manager)
    
    async def test_handle_llm_error(self, error_boundary, sample_sources):
        """Test LLM error handling."""
        query = "Test query"
        error = ValueError("LLM service failed")
        
        with patch('services.gateway.resilience.graceful_degradation.get_request_id') as mock_get_id:
            mock_get_id.return_value = "test-trace-id"
            
            response = await error_boundary.handle_llm_error(query, sample_sources, error)
        
        assert isinstance(response, FallbackResponse)
        assert response.provider == "fallback_free_tier"
        assert "AI synthesis failed" in response.answer
        assert response.trace_id == "test-trace-id"
    
    async def test_handle_retrieval_error(self, error_boundary):
        """Test retrieval error handling."""
        query = "Test query"
        error = ValueError("Retrieval service failed")
        
        with patch('services.gateway.resilience.graceful_degradation.get_request_id') as mock_get_id:
            mock_get_id.return_value = "test-trace-id"
            
            response = await error_boundary.handle_retrieval_error(query, error)
        
        assert isinstance(response, FallbackResponse)
        assert response.provider == "fallback_free_tier"
        assert response.degradation_level == DegradationLevel.EMERGENCY
        assert "Retrieval service failed" in response.answer
        assert response.trace_id == "test-trace-id"


class TestIntegration:
    """Integration tests for resilience system."""
    
    @pytest.fixture
    def app(self):
        """Create test FastAPI app."""
        app = FastAPI()
        
        @app.get("/test-circuit-breaker")
        async def test_circuit_breaker():
            # This would be a real endpoint that uses circuit breakers
            return {"status": "success"}
        
        @app.get("/test-degradation")
        async def test_degradation():
            # This would be a real endpoint that uses degradation
            return {"status": "success"}
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    async def test_circuit_breaker_integration(self):
        """Test circuit breaker integration with real scenarios."""
        manager = CircuitBreakerManager()
        
        # Simulate provider failures
        async def failing_provider(provider: str):
            if provider == "openai":
                raise ValueError("OpenAI API error")
            elif provider == "anthropic":
                raise ValueError("Anthropic API error")
            else:
                return f"Success from {provider}"
        
        providers = ["openai", "anthropic", "ollama"]
        
        # First call should fail through openai and anthropic, succeed with ollama
        result, used_provider = await manager.call_with_fallback(providers, failing_provider)
        
        assert result == "Success from ollama"
        assert used_provider == "ollama"
        
        # Check circuit breaker states
        openai_cb = manager.get_circuit_breaker("openai")
        anthropic_cb = manager.get_circuit_breaker("anthropic")
        
        # After multiple failures, circuits should be open
        for i in range(5):
            try:
                await openai_cb.call(lambda: failing_provider("openai"))
            except CircuitBreakerFailureError:
                pass
        
        assert openai_cb.state == CircuitState.OPEN
    
    async def test_degradation_integration(self):
        """Test degradation integration with real scenarios."""
        degradation_manager = GracefulDegradationManager()
        
        # Test system health check
        health_level = await degradation_manager.check_system_health()
        assert health_level in [DegradationLevel.FULL, DegradationLevel.LLM_DEGRADED]
        
        # Test fallback generation
        sources = [
            {
                "title": "React Documentation",
                "url": "https://react.dev/errors",
                "snippet": "React hydration errors occur when the server-rendered HTML doesn't match the client-side rendered HTML.",
                "domain": "react.dev"
            }
        ]
        
        response = await degradation_manager.generate_fallback_response(
            query="React hydration error fix",
            sources=sources
        )
        
        assert response.provider == "fallback_free_tier"
        assert "React hydration errors" in response.answer
        assert "react.dev" in response.answer


class TestChaosTesting:
    """Chaos testing for resilience system."""
    
    async def test_provider_failure_scenario(self):
        """Test scenario where all providers fail."""
        manager = CircuitBreakerManager()
        
        async def all_failing_provider(provider: str):
            raise ValueError(f"{provider} is down")
        
        providers = ["openai", "anthropic", "ollama", "huggingface"]
        
        # All providers should fail
        with pytest.raises(CircuitBreakerError):
            await manager.call_with_fallback(providers, all_failing_provider)
        
        # Check that all circuit breakers are open
        for provider in providers:
            cb = manager.get_circuit_breaker(provider)
            assert cb.state == CircuitState.OPEN
    
    async def test_partial_recovery_scenario(self):
        """Test scenario where some providers recover."""
        manager = CircuitBreakerManager()
        
        # First, make all providers fail
        async def failing_provider(provider: str):
            raise ValueError(f"{provider} failed")
        
        providers = ["openai", "anthropic", "ollama"]
        
        # Open all circuits
        for provider in providers:
            cb = manager.get_circuit_breaker(provider)
            for i in range(5):
                try:
                    await cb.call(lambda: failing_provider(provider))
                except CircuitBreakerFailureError:
                    pass
        
        # Wait for recovery timeout
        await asyncio.sleep(6)
        
        # Now make one provider succeed
        async def partial_recovery_provider(provider: str):
            if provider == "ollama":
                return "Success from ollama"
            else:
                raise ValueError(f"{provider} still failing")
        
        result, used_provider = await manager.call_with_fallback(providers, partial_recovery_provider)
        
        assert result == "Success from ollama"
        assert used_provider == "ollama"
    
    async def test_degradation_under_load(self):
        """Test degradation under high load."""
        degradation_manager = GracefulDegradationManager()
        
        # Simulate high load with many concurrent requests
        async def concurrent_request():
            sources = [{"title": "Test", "url": "https://test.com", "snippet": "Test content", "domain": "test.com"}]
            return await degradation_manager.generate_fallback_response("Test query", sources)
        
        # Run multiple concurrent requests
        tasks = [concurrent_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert len(results) == 10
        for result in results:
            assert isinstance(result, FallbackResponse)
            assert result.provider == "fallback_free_tier"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
