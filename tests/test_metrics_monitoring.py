"""
Test suite for metrics and monitoring system.

Tests:
- Metrics accuracy after simulated pipeline flow
- Health check reports accurate component statuses
- Endpoints handle component failures gracefully
- Prometheus metrics format
- Cache hit/miss ratio tracking
- LLM provider selection tracking
- Response time breakdown accuracy

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from shared.core.metrics_collector import (
    MetricsCollector, ResponseTimeBreakdown, LLMProvider,
    ComponentStatus, HealthCheckResult, record_query_metrics,
    record_error_metrics, record_health_check, get_metrics_summary,
    get_prometheus_metrics, reset_all_metrics
)
from shared.core.health_checker import HealthChecker


class TestMetricsCollector:
    """Test the MetricsCollector singleton and its functionality."""
    
    def setup_method(self):
        """Reset metrics before each test."""
        reset_all_metrics()
    
    def test_singleton_pattern(self):
        """Test that MetricsCollector is a singleton."""
        collector1 = MetricsCollector()
        collector2 = MetricsCollector()
        assert collector1 is collector2
    
    @pytest.mark.asyncio
    async def test_query_counter_increment(self):
        """Test query counter increment."""
        collector = MetricsCollector()
        initial_count = collector._query_counter
        
        await collector.increment_query_counter()
        assert collector._query_counter == initial_count + 1
        
        await collector.increment_query_counter()
        assert collector._query_counter == initial_count + 2
    
    @pytest.mark.asyncio
    async def test_error_counter_increment(self):
        """Test error counter increment."""
        collector = MetricsCollector()
        initial_count = collector._error_counter
        
        await collector.increment_error_counter("test_error")
        assert collector._error_counter == initial_count + 1
    
    @pytest.mark.asyncio
    async def test_provider_usage_tracking(self):
        """Test LLM provider usage tracking."""
        collector = MetricsCollector()
        
        # Test initial state
        assert collector._provider_counters[LLMProvider.OLLAMA] == 0
        assert collector._provider_counters[LLMProvider.OPENAI] == 0
        
        # Record usage
        await collector.record_provider_usage(LLMProvider.OLLAMA)
        await collector.record_provider_usage(LLMProvider.OLLAMA)
        await collector.record_provider_usage(LLMProvider.OPENAI)
        
        assert collector._provider_counters[LLMProvider.OLLAMA] == 2
        assert collector._provider_counters[LLMProvider.OPENAI] == 1
    
    @pytest.mark.asyncio
    async def test_response_time_tracking(self):
        """Test response time tracking with rolling averages."""
        collector = MetricsCollector()
        
        # Record response times
        breakdown1 = ResponseTimeBreakdown(
            retrieval_time_ms=100.0,
            llm_time_ms=200.0,
            synthesis_time_ms=50.0,
            total_time_ms=350.0
        )
        
        breakdown2 = ResponseTimeBreakdown(
            retrieval_time_ms=150.0,
            llm_time_ms=250.0,
            synthesis_time_ms=75.0,
            total_time_ms=475.0
        )
        
        await collector.record_response_time(breakdown1)
        await collector.record_response_time(breakdown2)
        
        # Check that times are recorded
        assert len(collector._response_times) == 2
        assert len(collector._retrieval_times) == 2
        assert len(collector._llm_times) == 2
        assert len(collector._synthesis_times) == 2
    
    @pytest.mark.asyncio
    async def test_cache_metrics_tracking(self):
        """Test cache hit/miss ratio tracking."""
        collector = MetricsCollector()
        
        # Record cache hits and misses
        await collector.record_cache_hit("query_cache")
        await collector.record_cache_hit("query_cache")
        await collector.record_cache_miss("query_cache")
        
        await collector.record_cache_hit("retrieval_cache")
        await collector.record_cache_miss("retrieval_cache")
        await collector.record_cache_miss("retrieval_cache")
        
        # Check metrics
        query_cache = collector._cache_metrics["query_cache"]
        retrieval_cache = collector._cache_metrics["retrieval_cache"]
        
        assert query_cache.hits == 2
        assert query_cache.misses == 1
        assert query_cache.total_requests == 3
        assert query_cache.hit_ratio == 2/3
        
        assert retrieval_cache.hits == 1
        assert retrieval_cache.misses == 2
        assert retrieval_cache.total_requests == 3
        assert retrieval_cache.hit_ratio == 1/3
    
    def test_metrics_dict_generation(self):
        """Test comprehensive metrics dictionary generation."""
        metrics_dict = get_metrics_summary()
        
        # Check required fields
        assert "timestamp" in metrics_dict
        assert "uptime_seconds" in metrics_dict
        assert "queries" in metrics_dict
        assert "response_times" in metrics_dict
        assert "cache_performance" in metrics_dict
        assert "llm_providers" in metrics_dict
        assert "health_status" in metrics_dict
        
        # Check query metrics
        queries = metrics_dict["queries"]
        assert "total_processed" in queries
        assert "errors" in queries
        assert "success_rate" in queries
        
        # Check response time metrics
        response_times = metrics_dict["response_times"]
        assert "average_total_ms" in response_times
        assert "average_retrieval_ms" in response_times
        assert "average_llm_ms" in response_times
        assert "average_synthesis_ms" in response_times
        assert "breakdown" in response_times
    
    def test_prometheus_metrics_generation(self):
        """Test Prometheus metrics format generation."""
        prometheus_metrics = get_prometheus_metrics()
        
        # Check that it's a string
        assert isinstance(prometheus_metrics, str)
        
        # Check for required Prometheus format elements
        assert "# HELP" in prometheus_metrics
        assert "# TYPE" in prometheus_metrics
        
        # Check for specific metrics
        assert "queries_total" in prometheus_metrics
        assert "errors_total" in prometheus_metrics
        assert "llm_provider_usage_total" in prometheus_metrics
    
    def test_metrics_reset(self):
        """Test metrics reset functionality."""
        collector = MetricsCollector()
        
        # Set some initial values
        collector._query_counter = 10
        collector._error_counter = 5
        collector._provider_counters[LLMProvider.OLLAMA] = 3
        
        # Reset metrics
        reset_all_metrics()
        
        # Check that all metrics are reset
        assert collector._query_counter == 0
        assert collector._error_counter == 0
        assert collector._provider_counters[LLMProvider.OLLAMA] == 0
        assert len(collector._response_times) == 0
        assert collector._cache_metrics["query_cache"].hits == 0


class TestHealthChecker:
    """Test the HealthChecker functionality."""
    
    @pytest.mark.asyncio
    async def test_database_connection_check(self):
        """Test database connection health check."""
        with patch('asyncpg.connect') as mock_connect:
            mock_conn = AsyncMock()
            mock_connect.return_value = mock_conn
            
            async with HealthChecker() as health_checker:
                result = await health_checker.check_database_connection()
                
                assert isinstance(result, HealthCheckResult)
                assert result.component == "postgresql"
                assert result.status in [ComponentStatus.HEALTHY, ComponentStatus.DEGRADED]
            assert result.response_time_ms >= 0
    
    @pytest.mark.asyncio
    async def test_meilisearch_health_check(self):
        """Test Meilisearch health check."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"status": "available"})
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_get.return_value = mock_context
            
            async with HealthChecker() as health_checker:
                result = await health_checker.check_meilisearch_health()
                
                assert isinstance(result, HealthCheckResult)
                assert result.component == "meilisearch"
                assert result.status in [ComponentStatus.HEALTHY, ComponentStatus.DEGRADED]
    
    @pytest.mark.asyncio
    async def test_llm_api_health_checks(self):
        """Test LLM API health checks."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"models": ["gpt2"]}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with HealthChecker() as health_checker:
                # Test Ollama health check
                result = await health_checker.check_llm_api_health(LLMProvider.OLLAMA)
                assert result.component == "llm_ollama"
                
                # Test OpenAI health check
                result = await health_checker.check_llm_api_health(LLMProvider.OPENAI)
                assert result.component == "llm_openai"
    
    @pytest.mark.asyncio
    async def test_factchecker_health_check(self):
        """Test FactChecker validation logic health check."""
        async with HealthChecker() as health_checker:
            result = await health_checker.check_factchecker_health()
            
            assert isinstance(result, HealthCheckResult)
            assert result.component == "factchecker"
            assert result.status in [ComponentStatus.HEALTHY, ComponentStatus.DEGRADED]
            assert "validation_logic" in result.details
    
    @pytest.mark.asyncio
    async def test_comprehensive_health_check(self):
        """Test comprehensive health check for all components."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"status": "available"}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            with patch('asyncpg.connect') as mock_connect:
                mock_conn = AsyncMock()
                mock_connect.return_value = mock_conn
                
                async with HealthChecker() as health_checker:
                    health_status = await health_checker.run_comprehensive_health_check()
                    
                    # Check structure
                    assert "timestamp" in health_status
                    assert "overall_status" in health_status
                    assert "components" in health_status
                    assert "summary" in health_status
                    
                    # Check summary
                    summary = health_status["summary"]
                    assert "total_components" in summary
                    assert "healthy_components" in summary
                    assert "degraded_components" in summary
                    assert "unhealthy_components" in summary
                    assert "unknown_components" in summary
    
    @pytest.mark.asyncio
    async def test_health_check_failure_handling(self):
        """Test graceful handling of health check failures."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock the context manager to raise an exception
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(side_effect=Exception("Connection failed"))
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_get.return_value = mock_context
            
            async with HealthChecker() as health_checker:
                result = await health_checker.check_meilisearch_health()
                
                assert result.status == ComponentStatus.UNHEALTHY
                assert "Connection failed" in result.error_message


class TestMetricsIntegration:
    """Test integration of metrics with the pipeline."""
    
    def setup_method(self):
        """Reset metrics before each test."""
        reset_all_metrics()
    
    @pytest.mark.asyncio
    async def test_query_metrics_recording(self):
        """Test recording metrics for a complete query pipeline."""
        # Simulate a query pipeline
        response_breakdown = ResponseTimeBreakdown(
            retrieval_time_ms=150.0,
            llm_time_ms=300.0,
            synthesis_time_ms=100.0,
            total_time_ms=550.0
        )
        
        cache_hits = {
            "query_cache": False,
            "retrieval_cache": True,
            "llm_cache": False
        }
        
        # Record metrics
        await record_query_metrics(
            response_time_breakdown=response_breakdown,
            provider=LLMProvider.OLLAMA,
            cache_hits=cache_hits
        )
        
        # Verify metrics were recorded
        metrics_dict = get_metrics_summary()
        
        assert metrics_dict["queries"]["total_processed"] == 1
        assert metrics_dict["queries"]["errors"] == 0
        assert metrics_dict["llm_providers"]["usage_counts"]["ollama"] == 1
        
        # Check cache metrics
        cache_performance = metrics_dict["cache_performance"]
        assert cache_performance["query_cache"]["hits"] == 0
        assert cache_performance["query_cache"]["misses"] == 1
        assert cache_performance["retrieval_cache"]["hits"] == 1
        assert cache_performance["retrieval_cache"]["misses"] == 0
    
    @pytest.mark.asyncio
    async def test_error_metrics_recording(self):
        """Test recording error metrics."""
        await record_error_metrics("test_error")
        
        metrics_dict = get_metrics_summary()
        assert metrics_dict["queries"]["errors"] == 1
    
    @pytest.mark.asyncio
    async def test_health_check_metrics_recording(self):
        """Test recording health check metrics."""
        await record_health_check(
            component="test_component",
            status=ComponentStatus.HEALTHY,
            response_time_ms=50.0,
            details={"test": "data"}
        )
        
        metrics_dict = get_metrics_summary()
        health_status = metrics_dict["health_status"]
        
        assert "test_component" in health_status
        assert health_status["test_component"]["status"] == "healthy"
        assert health_status["test_component"]["response_time_ms"] == 50.0


class TestAPIEndpoints:
    """Test API endpoints for metrics and health checks."""
    
    @pytest.mark.asyncio
    async def test_metrics_endpoint_json(self):
        """Test /metrics endpoint with JSON format."""
        from services.api_gateway.main import get_metrics
        
        with patch('shared.core.metrics_collector.get_metrics_summary') as mock_get_metrics:
            mock_get_metrics.return_value = {
                "timestamp": "2024-12-28T10:00:00",
                "queries": {"total_processed": 100},
                "response_times": {"average_total_ms": 250.0}
            }
            
            response = await get_metrics(admin=False, format="json")
            
            assert response.status_code == 200
            content = response.body.decode()
            assert "queries" in content
            assert "response_times" in content
    
    @pytest.mark.asyncio
    async def test_metrics_endpoint_prometheus(self):
        """Test /metrics endpoint with Prometheus format."""
        from services.api_gateway.main import get_metrics
        
        with patch('shared.core.metrics_collector.get_prometheus_metrics') as mock_get_prometheus:
            mock_get_prometheus.return_value = "# HELP queries_total\n# TYPE queries_total counter\nqueries_total 100"
            
            response = await get_metrics(admin=False, format="prometheus")
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test /health endpoint."""
        from services.api_gateway.main import health_check
        
        with patch('shared.core.health_checker.get_health_checker') as mock_get_checker:
            mock_checker = AsyncMock()
            mock_checker.run_comprehensive_health_check.return_value = {
                "timestamp": "2024-12-28T10:00:00",
                "overall_status": "healthy",
                "components": {"test": {"status": "healthy"}},
                "summary": {"total_components": 1, "healthy_components": 1}
            }
            mock_get_checker.return_value = mock_checker
            
            response = await health_check()
            
            assert "timestamp" in response
            assert "overall_status" in response
            assert "components" in response
            assert "summary" in response
    
    @pytest.mark.asyncio
    async def test_health_endpoint_failure_handling(self):
        """Test /health endpoint handles failures gracefully."""
        from services.api_gateway.main import health_check
        
        with patch('shared.core.health_checker.get_health_checker') as mock_get_checker:
            mock_get_checker.side_effect = Exception("Health checker failed")
            
            response = await health_check()
            
            assert response["overall_status"] == "degraded"
            assert "health_checker" in response
            assert response["health_checker"]["status"] == "unhealthy"


class TestMetricsAccuracy:
    """Test metrics accuracy and consistency."""
    
    def setup_method(self):
        """Reset metrics before each test."""
        reset_all_metrics()
    
    @pytest.mark.asyncio
    async def test_response_time_accuracy(self):
        """Test that response times are accurately tracked."""
        collector = MetricsCollector()
        
        # Record multiple response times
        times = [100.0, 200.0, 300.0, 150.0, 250.0]
        
        for time_ms in times:
            breakdown = ResponseTimeBreakdown(
                retrieval_time_ms=time_ms * 0.3,
                llm_time_ms=time_ms * 0.5,
                synthesis_time_ms=time_ms * 0.2,
                total_time_ms=time_ms
            )
            await collector.record_response_time(breakdown)
        
        # Check accuracy
        metrics_dict = get_metrics_summary()
        avg_total = metrics_dict["response_times"]["average_total_ms"]
        
        # Should be close to the mean of our test times
        expected_avg = sum(times) / len(times)
        assert abs(avg_total - expected_avg) < 1.0  # Allow small floating point differences
    
    @pytest.mark.asyncio
    async def test_provider_usage_percentages(self):
        """Test LLM provider usage percentage calculations."""
        collector = MetricsCollector()
        
        # Record usage for different providers
        await collector.record_provider_usage(LLMProvider.OLLAMA)
        await collector.record_provider_usage(LLMProvider.OLLAMA)
        await collector.record_provider_usage(LLMProvider.OPENAI)
        await collector.record_provider_usage(LLMProvider.HUGGINGFACE)
        
        metrics_dict = get_metrics_summary()
        percentages = metrics_dict["llm_providers"]["usage_percentages"]
        
        # Check percentages
        assert percentages["ollama"] == 50.0  # 2 out of 4 = 50%
        assert percentages["openai"] == 25.0  # 1 out of 4 = 25%
        assert percentages["huggingface"] == 25.0  # 1 out of 4 = 25%
    
    @pytest.mark.asyncio
    async def test_cache_hit_ratio_accuracy(self):
        """Test cache hit ratio accuracy."""
        collector = MetricsCollector()
        
        # Record cache hits and misses
        for _ in range(8):
            await collector.record_cache_hit("query_cache")
        
        for _ in range(2):
            await collector.record_cache_miss("query_cache")
        
        metrics_dict = get_metrics_summary()
        cache_metrics = metrics_dict["cache_performance"]["query_cache"]
        
        # Should be 80% hit ratio (8 hits out of 10 total)
        assert cache_metrics["hit_ratio"] == 0.8
        assert cache_metrics["hits"] == 8
        assert cache_metrics["misses"] == 2
        assert cache_metrics["total_requests"] == 10


if __name__ == "__main__":
    pytest.main([__file__]) 