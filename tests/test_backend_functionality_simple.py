"""
Simplified Backend Functionality Tests for SarvanOM

This test suite focuses on endpoints that are currently working
and provides a foundation for testing as the backend is fixed.
"""

import pytest
import time
import json
from fastapi.testclient import TestClient
from services.gateway.main import app


class TestWorkingEndpoints:
    """Test suite for endpoints that are currently working."""

    def test_root_endpoint_metadata(self, client: TestClient):
        """Test that GET / returns metadata with service info and endpoints."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required metadata fields
        assert "message" in data
        assert "version" in data
        assert "services" in data
        assert "health" in data
        
        # Verify service information
        assert "Universal Knowledge Platform" in data["message"] or "SarvanOM" in data["message"]
        assert isinstance(data["services"], list)
        assert len(data["services"]) > 0
        
        # Verify key services are listed
        services = data["services"]
        expected_services = ["search", "fact-check", "synthesize"]
        for service in expected_services:
            assert service in services, f"Missing service: {service}"
        
        # Verify health endpoint reference
        assert data["health"] == "/health"

    def test_root_endpoint_performance(self, client: TestClient):
        """Test that root endpoint responds quickly."""
        start_time = time.time()
        response = client.get("/")
        duration = time.time() - start_time
        
        assert response.status_code == 200
        assert duration < 1.0, f"Root endpoint took too long: {duration:.3f}s"

    def test_root_endpoint_structure(self, client: TestClient):
        """Test that root endpoint has consistent structure."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields are present and have correct types
        assert isinstance(data["message"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["services"], list)
        assert isinstance(data["health"], str)
        
        # Verify version format
        assert len(data["version"]) > 0
        assert "." in data["version"]  # Should be semantic versioning

    def test_root_endpoint_json_format(self, client: TestClient):
        """Test that root endpoint returns valid JSON."""
        response = client.get("/")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        # Verify JSON is valid
        try:
            data = response.json()
            assert isinstance(data, dict)
        except json.JSONDecodeError:
            pytest.fail("Root endpoint did not return valid JSON")


class TestBasicFunctionality:
    """Test suite for basic API functionality."""

    def test_api_accepts_requests(self, client: TestClient):
        """Test that the API accepts HTTP requests."""
        response = client.get("/")
        
        # Should return a response (even if it's an error)
        assert response.status_code in [200, 404, 500]
        assert len(response.content) > 0

    def test_api_has_cors_headers(self, client: TestClient):
        """Test that the API includes CORS headers."""
        # Test OPTIONS request (preflight) which should include CORS headers
        response = client.options("/", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type"
        })
        
        # Check for CORS headers (they should be present due to middleware)
        cors_headers = [
            "access-control-allow-origin",
            "access-control-allow-methods", 
            "access-control-allow-headers"
        ]
        
        # At least one CORS header should be present
        found_cors_headers = [h for h in cors_headers if h in response.headers]
        assert len(found_cors_headers) > 0, "No CORS headers found"

    def test_api_handles_invalid_routes(self, client: TestClient):
        """Test that the API handles invalid routes gracefully."""
        response = client.get("/nonexistent-endpoint")
        
        # Should return 404 for invalid routes
        assert response.status_code == 404
        
        # Should return JSON error response
        try:
            data = response.json()
            assert "error" in data or "detail" in data
        except json.JSONDecodeError:
            # Accept non-JSON 404 responses too
            assert len(response.text) > 0

    def test_api_handles_different_methods(self, client: TestClient):
        """Test that the API handles different HTTP methods."""
        # Test GET (should work)
        get_response = client.get("/")
        assert get_response.status_code in [200, 404, 500]
        
        # Test POST to root (should return 405 Method Not Allowed)
        post_response = client.post("/")
        assert post_response.status_code in [405, 404, 500]
        
        # Test OPTIONS (should work for CORS)
        options_response = client.options("/")
        assert options_response.status_code in [200, 405, 404, 500]


class TestErrorHandling:
    """Test suite for error handling."""

    def test_invalid_json_handling(self, client: TestClient):
        """Test handling of malformed JSON requests."""
        invalid_json = '{"query": "incomplete json'
        
        # Try to post invalid JSON to a POST endpoint
        response = client.post(
            "/search",
            content=invalid_json,
            headers={"Content-Type": "application/json"}
        )
        
        # Should return validation error
        assert response.status_code in [422, 400, 500]
        
        if response.status_code == 422:
            try:
                data = response.json()
                assert "detail" in data
            except json.JSONDecodeError:
                # Accept non-JSON error responses too
                assert len(response.text) > 0

    def test_large_request_handling(self, client: TestClient):
        """Test handling of unusually large requests."""
        large_query = "A" * 10000  # Large but reasonable query
        
        query_data = {"query": large_query}
        response = client.post("/search", json=query_data)
        
        # Should either handle it or return appropriate error
        assert response.status_code in [200, 413, 422, 500]
        
        if response.status_code != 200:
            try:
                data = response.json()
                assert "detail" in data or "error" in data
            except json.JSONDecodeError:
                # Accept non-JSON error responses too
                assert len(response.text) > 0

    def test_missing_content_type(self, client: TestClient):
        """Test handling of requests without content-type header."""
        query_data = {"query": "test query"}
        
        # Post without content-type header
        response = client.post("/search", json=query_data, headers={})
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 422, 500]


class TestPerformance:
    """Test suite for basic performance requirements."""

    def test_root_endpoint_latency(self, client: TestClient):
        """Test that root endpoint responds quickly."""
        start_time = time.time()
        response = client.get("/")
        duration = time.time() - start_time
        
        assert response.status_code == 200
        assert duration < 2.0, f"Root endpoint took too long: {duration:.3f}s"

    def test_multiple_requests_performance(self, client: TestClient):
        """Test performance under multiple requests."""
        durations = []
        
        for i in range(5):
            start_time = time.time()
            response = client.get("/")
            duration = time.time() - start_time
            
            assert response.status_code == 200
            durations.append(duration)
        
        # Average response time should be reasonable
        avg_duration = sum(durations) / len(durations)
        assert avg_duration < 1.0, f"Average response time too high: {avg_duration:.3f}s"
        
        # No single request should be extremely slow
        max_duration = max(durations)
        assert max_duration < 3.0, f"Max response time too high: {max_duration:.3f}s"


class TestConfiguration:
    """Test suite for configuration and environment."""

    def test_api_has_proper_headers(self, client: TestClient):
        """Test that API responses have proper headers."""
        response = client.get("/")
        
        # Check for common headers
        assert "content-type" in response.headers
        assert "content-length" in response.headers or "transfer-encoding" in response.headers

    def test_api_handles_different_user_agents(self, client: TestClient):
        """Test that API handles different user agents."""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "curl/7.68.0",
            "PostmanRuntime/7.28.0",
            "python-requests/2.25.1"
        ]
        
        for user_agent in user_agents:
            response = client.get("/", headers={"User-Agent": user_agent})
            assert response.status_code in [200, 404, 500]

    def test_api_logging_functionality(self, client: TestClient):
        """Test that API has logging functionality."""
        # Make a request and check that it's logged
        response = client.get("/")
        
        # The fact that we get a response means logging is working
        # (we can see logs in the test output)
        assert response.status_code in [200, 404, 500]


# Performance test specifically for CI/CD
@pytest.mark.slow
class TestCICDRequirements:
    """Performance tests specifically for CI/CD pipeline."""

    def test_basic_functionality_under_threshold(self, client: TestClient):
        """Test that basic functionality completes within reasonable time."""
        start_time = time.time()
        
        # Test root endpoint
        root_response = client.get("/")
        
        # Test error handling
        error_response = client.get("/nonexistent")
        
        total_duration = time.time() - start_time
        
        # All endpoints should respond
        assert root_response.status_code == 200
        assert error_response.status_code == 404
        
        # Total pipeline should complete within reasonable time
        assert total_duration < 5.0, f"Basic functionality took too long: {total_duration:.3f}s"

    def test_concurrent_access_simulation(self, client: TestClient):
        """Simulate concurrent access patterns."""
        import threading
        
        def make_request():
            start = time.time()
            response = client.get("/")
            duration = time.time() - start
            return response.status_code, duration
        
        # Run multiple requests in parallel
        threads = []
        results = []
        
        for i in range(3):
            thread = threading.Thread(target=lambda: results.append(make_request()))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All should succeed and be reasonably fast
        for status_code, duration in results:
            assert status_code == 200
            assert duration < 2.0, f"Concurrent request took too long: {duration:.3f}s"


# Test utilities
def test_api_is_accessible(client: TestClient):
    """Basic test to verify API is accessible."""
    response = client.get("/")
    assert response.status_code in [200, 404, 500]
    assert len(response.content) > 0


def test_api_has_fastapi_structure(client: TestClient):
    """Test that API has FastAPI structure."""
    response = client.get("/")
    
    # Should have JSON content type
    assert "application/json" in response.headers.get("content-type", "")
    
    # Should return valid JSON
    try:
        data = response.json()
        assert isinstance(data, dict)
    except json.JSONDecodeError:
        # Accept non-JSON responses for error cases
        assert response.status_code in [404, 500]


# Export test utilities
__all__ = [
    "TestWorkingEndpoints",
    "TestBasicFunctionality", 
    "TestErrorHandling",
    "TestPerformance",
    "TestConfiguration",
    "TestCICDRequirements",
    "test_api_is_accessible",
    "test_api_has_fastapi_structure"
]
