"""
API Endpoint Tests

Tests for FastAPI endpoints including authentication, validation,
error handling, and response formats.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient

from ..models.requests.query_requests import QueryRequest, ComprehensiveQueryRequest
from ..models.responses.query_responses import QueryResponse, ComprehensiveQueryResponse


@pytest.mark.api
class TestQueryEndpoints:
    """Test query-related API endpoints."""
    
    def test_root_endpoint(self, test_client):
        """Test the root endpoint."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "SarvanOM Backend"
        assert data["version"] == "1.0.0"
        assert data["architecture"] == "Clean Architecture"
        assert "endpoints" in data
    
    def test_health_endpoint(self, test_client):
        """Test the health check endpoint."""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
    
    @pytest.mark.asyncio
    async def test_basic_query_endpoint(self, mock_dependencies):
        """Test the basic query processing endpoint."""
        # Setup mock response
        mock_dependencies["orchestrator"].process_basic_query.return_value = QueryResponse(
            query_id="test-query-123",
            answer="Test answer",
            confidence=0.95,
            processing_time=0.1,
            cache_hit=False,
            created_at="2024-01-01T00:00:00",
            metadata={}
        )
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/query/",
                json={
                    "query": "What is the capital of France?",
                    "session_id": "test-session",
                    "max_tokens": 100,
                    "confidence_threshold": 0.8,
                    "cache_enabled": True
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Test answer"
        assert data["confidence"] == 0.95
        assert data["query_id"] == "test-query-123"
    
    @pytest.mark.asyncio
    async def test_comprehensive_query_endpoint(self, mock_dependencies):
        """Test the comprehensive query processing endpoint."""
        # Setup mock response
        mock_dependencies["orchestrator"].process_comprehensive_query.return_value = ComprehensiveQueryResponse(
            query_id="test-comp-query-123",
            answer="Comprehensive test answer",
            confidence=0.98,
            processing_time=0.2,
            cache_hit=False,
            sources=["source1", "source2"],
            alternatives=[],
            quality_metrics={},
            created_at="2024-01-01T00:00:00",
            metadata={}
        )
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/query/comprehensive",
                json={
                    "query": "Explain quantum computing in detail",
                    "session_id": "test-session",
                    "max_tokens": 500,
                    "confidence_threshold": 0.9,
                    "options": {
                        "include_sources": True,
                        "include_alternatives": True
                    }
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Comprehensive test answer"
        assert data["confidence"] == 0.98
        assert len(data["sources"]) == 2
    
    def test_query_validation_error(self, test_client):
        """Test query endpoint with invalid data."""
        response = test_client.post(
            "/query/",
            json={
                "query": "",  # Empty query should fail validation
                "max_tokens": -1  # Negative tokens should fail validation
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["error"]["type"] == "ValidationError"
    
    @pytest.mark.asyncio
    async def test_query_status_endpoint(self, mock_dependencies):
        """Test getting query status."""
        # Setup mock response
        mock_dependencies["orchestrator"].get_query_status.return_value = {
            "status": "completed",
            "progress": 1.0,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:01:00"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/query/test-query-123/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["progress"] == 1.0
    
    def test_query_not_found(self, mock_dependencies):
        """Test query status for non-existent query."""
        mock_dependencies["orchestrator"].get_query_status.side_effect = ValueError("Query not found")
        
        response = test_client.get("/query/non-existent-query/status")
        
        assert response.status_code == 404


@pytest.mark.api
class TestHealthEndpoints:
    """Test health-related API endpoints."""
    
    def test_basic_health_check(self, test_client):
        """Test basic health check endpoint."""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        
        # Check response headers
        assert "X-Request-ID" in response.headers
        assert "X-Process-Time" in response.headers
    
    def test_metrics_endpoint(self, test_client):
        """Test metrics endpoint."""
        response = test_client.get("/metrics")
        
        assert response.status_code == 200
        # Metrics endpoint should return metrics data
        data = response.json()
        assert isinstance(data, (dict, list))  # Metrics can be dict or list format


@pytest.mark.api
class TestMiddlewareIntegration:
    """Test middleware integration with API endpoints."""
    
    def test_cors_headers(self, test_client):
        """Test CORS headers are present."""
        response = test_client.options("/", headers={"Origin": "http://localhost:3000"})
        
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
    
    def test_security_headers(self, test_client):
        """Test security headers are present."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
    
    def test_request_id_header(self, test_client):
        """Test request ID is added to response."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        # Request ID should be a UUID-like string
        request_id = response.headers["X-Request-ID"]
        assert len(request_id) > 10  # Basic check for UUID format
    
    def test_processing_time_header(self, test_client):
        """Test processing time is added to response."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        assert "X-Process-Time" in response.headers
        # Processing time should be a number
        process_time = float(response.headers["X-Process-Time"])
        assert process_time >= 0
    
    def test_rate_limiting_headers(self, test_client):
        """Test rate limiting headers are present."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers


@pytest.mark.api
class TestErrorHandling:
    """Test API error handling."""
    
    def test_404_error_handling(self, test_client):
        """Test 404 error response format."""
        response = test_client.get("/non-existent-endpoint")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["type"] == "HTTPException"
        assert "timestamp" in data
        assert "request" in data
    
    def test_validation_error_handling(self, test_client):
        """Test validation error response format."""
        response = test_client.post(
            "/query/",
            json={
                "invalid_field": "invalid_value"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["error"]["type"] == "ValidationError"
        assert "details" in data["error"]
        assert "timestamp" in data
    
    @pytest.mark.asyncio
    async def test_internal_server_error_handling(self, mock_dependencies):
        """Test internal server error handling."""
        # Make orchestrator raise an exception
        mock_dependencies["orchestrator"].process_basic_query.side_effect = Exception("Test error")
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/query/",
                json={
                    "query": "Test query",
                    "session_id": "test-session"
                }
            )
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert data["error"]["type"] == "InternalServerError"
        assert "error_id" in data["error"]
        assert "timestamp" in data


@pytest.mark.api
class TestAuthenticationEndpoints:
    """Test authentication-related endpoints."""
    
    def test_anonymous_access(self, test_client):
        """Test that endpoints work with anonymous access."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        # Anonymous access should work for public endpoints
    
    def test_admin_endpoint_access(self, test_client):
        """Test admin endpoint access control."""
        response = test_client.get("/admin/dashboard")
        
        # Should fail without proper authentication
        # Exact status code depends on implementation
        assert response.status_code in [401, 403, 404]


@pytest.mark.api
@pytest.mark.slow
class TestPerformanceEndpoints:
    """Test API endpoint performance."""
    
    def test_endpoint_response_time(self, test_client):
        """Test that endpoints respond within reasonable time."""
        import time
        
        start_time = time.time()
        response = test_client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second
        
        # Check performance header
        process_time = float(response.headers.get("X-Process-Time", "0"))
        assert process_time < 0.5  # Processing should be under 500ms
    
    def test_concurrent_requests(self, test_client):
        """Test handling of concurrent requests."""
        import concurrent.futures
        import threading
        
        def make_request():
            return test_client.get("/health")
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in futures]
        
        # All requests should succeed
        assert all(r.status_code == 200 for r in responses)
        
        # All should have unique request IDs
        request_ids = [r.headers.get("X-Request-ID") for r in responses]
        assert len(set(request_ids)) == 10  # All unique


@pytest.mark.api
class TestDataFormats:
    """Test API data format handling."""
    
    def test_json_content_type(self, test_client):
        """Test JSON content type handling."""
        response = test_client.post(
            "/query/",
            json={"query": "test", "session_id": "test"},
            headers={"Content-Type": "application/json"}
        )
        
        # Should handle JSON content type properly
        assert response.status_code in [200, 422]  # Either success or validation error
    
    def test_invalid_json_handling(self, test_client):
        """Test handling of invalid JSON."""
        response = test_client.post(
            "/query/",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
        # Should return proper error for invalid JSON
    
    def test_response_content_type(self, test_client):
        """Test response content type."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")
    
    def test_unicode_handling(self, test_client):
        """Test Unicode character handling."""
        response = test_client.post(
            "/query/",
            json={
                "query": "What is 数学 in English?",  # Unicode characters
                "session_id": "test-session"
            }
        )
        
        # Should handle Unicode properly
        assert response.status_code in [200, 422]
        
        if response.status_code == 200:
            data = response.json()
            # Response should maintain Unicode characters
            assert isinstance(data, dict)
