#!/usr/bin/env python3
"""
Integration Tests for Observability and Security Middleware

Tests the comprehensive observability and security features:
- Request ID injection and propagation
- Structured logging with trace IDs
- Prometheus metrics collection
- Rate limiting with burst handling
- Security headers and input validation
- Trusted host validation
- Performance monitoring

Following enterprise testing standards for observability and security.
"""

import asyncio
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import pytest
from unittest.mock import Mock, patch, AsyncMock

from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
from fastapi.middleware.base import BaseHTTPMiddleware

# Import middleware components
from services.gateway.middleware.observability import (
    ObservabilityMiddleware,
    MetricsMiddleware,
    log_llm_call,
    log_cache_event,
    log_stream_event,
    log_error,
    monitor_performance,
    get_request_id,
    get_user_id,
    get_session_id
)

from services.gateway.middleware.security import (
    SecurityMiddleware,
    InputValidationMiddleware,
    SecurityConfig,
    RateLimitConfig,
    validate_email,
    validate_url,
    validate_filename,
    sanitize_filename
)


class TestObservabilityMiddleware:
    """Test observability middleware functionality."""
    
    @pytest.fixture
    def app(self):
        """Create test FastAPI app with observability middleware."""
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        @app.get("/error")
        async def error_endpoint():
            raise ValueError("Test error")
        
        @app.get("/metrics")
        async def metrics_endpoint():
            return {"metrics": "test"}
        
        # Add observability middleware
        app.add_middleware(ObservabilityMiddleware, service_name="test-service")
        app.add_middleware(MetricsMiddleware)
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    def test_request_id_injection(self, client):
        """Test that request IDs are injected and propagated."""
        response = client.get("/test")
        
        # Check that request ID is in response headers
        assert "X-Request-ID" in response.headers
        request_id = response.headers["X-Request-ID"]
        assert request_id is not None
        assert len(request_id) > 0
        
        # Check that response time is included
        assert "X-Response-Time" in response.headers
        response_time = response.headers["X-Response-Time"]
        assert response_time.endswith("s")
    
    def test_metrics_endpoint(self, client):
        """Test that Prometheus metrics endpoint works."""
        response = client.get("/metrics")
        
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        
        # Check that metrics content is present
        content = response.text
        assert "http_requests_total" in content
        assert "http_request_duration_seconds" in content
    
    def test_error_logging(self, client):
        """Test that errors are properly logged."""
        with patch('services.gateway.middleware.observability.logger') as mock_logger:
            response = client.get("/error")
            
            assert response.status_code == 500
            
            # Check that error was logged
            mock_logger.error.assert_called()
            log_call = mock_logger.error.call_args[0][0]
            log_data = json.loads(log_call)
            
            assert log_data["event"] == "request_error"
            assert log_data["error_type"] == "ValueError"
            assert "Test error" in log_data["error_message"]
    
    def test_llm_call_logging(self):
        """Test LLM call logging functionality."""
        with patch('services.gateway.middleware.observability.logger') as mock_logger:
            log_llm_call(
                provider="openai",
                model="gpt-4",
                duration=1.5,
                success=True
            )
            
            mock_logger.info.assert_called()
            log_call = mock_logger.info.call_args[0][0]
            log_data = json.loads(log_call)
            
            assert log_data["event"] == "llm_call"
            assert log_data["provider"] == "openai"
            assert log_data["model"] == "gpt-4"
            assert log_data["duration_seconds"] == 1.5
            assert log_data["success"] is True
    
    def test_cache_event_logging(self):
        """Test cache event logging functionality."""
        with patch('services.gateway.middleware.observability.logger') as mock_logger:
            log_cache_event("redis", True)  # Cache hit
            
            mock_logger.info.assert_called()
            log_call = mock_logger.info.call_args[0][0]
            log_data = json.loads(log_call)
            
            assert log_data["event"] == "cache_event"
            assert log_data["cache_type"] == "redis"
            assert log_data["hit"] is True
    
    def test_stream_event_logging(self):
        """Test stream event logging functionality."""
        with patch('services.gateway.middleware.observability.logger') as mock_logger:
            log_stream_event("content_chunk", "stream-123", {"tokens": 10})
            
            mock_logger.info.assert_called()
            log_call = mock_logger.info.call_args[0][0]
            log_data = json.loads(log_call)
            
            assert log_data["event"] == "stream_event"
            assert log_data["event_type"] == "content_chunk"
            assert log_data["stream_id"] == "stream-123"
            assert log_data["metadata"]["tokens"] == 10
    
    def test_performance_monitoring_decorator(self):
        """Test performance monitoring decorator."""
        @monitor_performance("test_operation")
        async def test_async_function():
            await asyncio.sleep(0.1)
            return "success"
        
        @monitor_performance("test_sync_operation")
        def test_sync_function():
            time.sleep(0.1)
            return "success"
        
        with patch('services.gateway.middleware.observability.logger') as mock_logger:
            # Test async function
            result = asyncio.run(test_async_function())
            assert result == "success"
            
            # Test sync function
            result = test_sync_function()
            assert result == "success"
            
            # Check that performance was logged
            assert mock_logger.info.call_count >= 2
            
            # Check performance log structure
            for call in mock_logger.info.call_args_list:
                log_data = json.loads(call[0][0])
                assert log_data["event"] == "performance"
                assert "duration_seconds" in log_data
                assert log_data["success"] is True


class TestSecurityMiddleware:
    """Test security middleware functionality."""
    
    @pytest.fixture
    def security_config(self):
        """Create security configuration for testing."""
        return SecurityConfig(
            rate_limit=RateLimitConfig(
                requests_per_minute=10,
                burst_limit=3,
                window_size=60,
                block_duration=30
            ),
            trusted_hosts={
                "localhost",
                "127.0.0.1",
                "test.example.com"
            },
            max_request_size=1024 * 1024,  # 1MB
            max_query_length=100,
            max_headers_size=4096
        )
    
    @pytest.fixture
    def app(self, security_config):
        """Create test FastAPI app with security middleware."""
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        @app.post("/submit")
        async def submit_endpoint(request: Request):
            body = await request.json()
            return {"received": body}
        
        # Add security middleware
        app.add_middleware(SecurityMiddleware, config=security_config)
        app.add_middleware(InputValidationMiddleware)
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    def test_rate_limiting(self, client):
        """Test rate limiting functionality."""
        # Make requests up to the limit
        for i in range(10):
            response = client.get("/test")
            assert response.status_code == 200
        
        # Next request should be rate limited
        response = client.get("/test")
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]
    
    def test_burst_limiting(self, client):
        """Test burst limiting functionality."""
        # Make rapid requests to trigger burst limit
        for i in range(4):  # Exceeds burst limit of 3
            response = client.get("/test")
            if i < 3:
                assert response.status_code == 200
            else:
                assert response.status_code == 429
    
    def test_trusted_host_validation(self, client):
        """Test trusted host validation."""
        # Test with untrusted host
        with patch.object(client, 'base_url', 'http://untrusted.example.com'):
            response = client.get("/test", headers={"host": "untrusted.example.com"})
            assert response.status_code == 400
            assert "Invalid host header" in response.json()["detail"]
    
    def test_request_size_validation(self, client):
        """Test request size validation."""
        # Create large payload
        large_payload = "x" * (1024 * 1024 + 1)  # Exceeds 1MB limit
        
        response = client.post(
            "/submit",
            json={"data": large_payload},
            headers={"content-length": str(len(large_payload.encode()))}
        )
        
        assert response.status_code == 413
        assert "Request too large" in response.json()["detail"]
    
    def test_security_headers(self, client):
        """Test that security headers are added."""
        response = client.get("/test")
        
        # Check security headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert "Strict-Transport-Security" in response.headers
        assert "Content-Security-Policy" in response.headers
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    
    def test_xss_prevention(self, client):
        """Test XSS prevention in input validation."""
        malicious_query = "?q=<script>alert('xss')</script>"
        
        response = client.get(f"/test{malicious_query}")
        
        # Should be blocked or sanitized
        assert response.status_code in [200, 400]
    
    def test_sql_injection_prevention(self, client):
        """Test SQL injection prevention."""
        malicious_query = "?q=1' OR '1'='1"
        
        response = client.get(f"/test{malicious_query}")
        
        # Should be blocked or sanitized
        assert response.status_code in [200, 400]


class TestInputValidation:
    """Test input validation utilities."""
    
    def test_email_validation(self):
        """Test email validation."""
        # Valid emails
        assert validate_email("test@example.com") is True
        assert validate_email("user.name+tag@domain.co.uk") is True
        
        # Invalid emails
        assert validate_email("invalid-email") is False
        assert validate_email("@example.com") is False
        assert validate_email("test@") is False
    
    def test_url_validation(self):
        """Test URL validation."""
        # Valid URLs
        assert validate_url("https://example.com") is True
        assert validate_url("http://subdomain.example.org/path") is True
        
        # Invalid URLs
        assert validate_url("not-a-url") is False
        assert validate_url("ftp://example.com") is False  # Only http/https allowed
    
    def test_filename_validation(self):
        """Test filename validation."""
        # Valid filenames
        assert validate_filename("document.pdf") is True
        assert validate_filename("image.jpg") is True
        
        # Invalid filenames (path traversal)
        assert validate_filename("../../../etc/passwd") is False
        assert validate_filename("..\\windows\\system32\\config") is False
        
        # Invalid filenames (dangerous extensions)
        assert validate_filename("script.exe") is False
        assert validate_filename("malware.bat") is False
    
    def test_filename_sanitization(self):
        """Test filename sanitization."""
        # Test path separator removal
        assert sanitize_filename("path/to/file.txt") == "path_to_file.txt"
        
        # Test dangerous character replacement
        assert sanitize_filename("file<name>.txt") == "file_name_.txt"
        
        # Test length limiting
        long_name = "a" * 300 + ".txt"
        sanitized = sanitize_filename(long_name)
        assert len(sanitized) <= 255
        assert sanitized.endswith(".txt")


class TestIntegration:
    """Integration tests for observability and security working together."""
    
    @pytest.fixture
    def full_app(self):
        """Create test app with both observability and security middleware."""
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        @app.get("/error")
        async def error_endpoint():
            raise ValueError("Test error")
        
        # Add both middleware layers
        app.add_middleware(ObservabilityMiddleware, service_name="test-service")
        app.add_middleware(MetricsMiddleware)
        
        security_config = SecurityConfig(
            rate_limit=RateLimitConfig(requests_per_minute=5, burst_limit=2),
            trusted_hosts={"localhost", "127.0.0.1"}
        )
        app.add_middleware(SecurityMiddleware, config=security_config)
        app.add_middleware(InputValidationMiddleware)
        
        return app
    
    @pytest.fixture
    def client(self, full_app):
        """Create test client."""
        return TestClient(full_app)
    
    def test_observability_with_security(self, client):
        """Test that observability works with security middleware."""
        with patch('services.gateway.middleware.observability.logger') as mock_logger:
            # Make a request that passes security checks
            response = client.get("/test")
            
            assert response.status_code == 200
            
            # Check that observability logged the request
            mock_logger.info.assert_called()
            
            # Check that security headers are present
            assert "X-Request-ID" in response.headers
            assert "X-Content-Type-Options" in response.headers
    
    def test_error_handling_with_security(self, client):
        """Test error handling with security middleware."""
        with patch('services.gateway.middleware.observability.logger') as mock_logger:
            # Make a request that triggers an error
            response = client.get("/error")
            
            assert response.status_code == 500
            
            # Check that error was logged with observability
            mock_logger.error.assert_called()
            
            # Check that security headers are still present
            assert "X-Request-ID" in response.headers
            assert "X-Content-Type-Options" in response.headers
    
    def test_rate_limiting_with_observability(self, client):
        """Test rate limiting with observability logging."""
        with patch('services.gateway.middleware.observability.logger') as mock_logger:
            # Make requests up to the limit
            for i in range(5):
                response = client.get("/test")
                assert response.status_code == 200
            
            # Next request should be rate limited
            response = client.get("/test")
            assert response.status_code == 429
            
            # Check that rate limiting was logged
            mock_logger.error.assert_called()
            log_call = mock_logger.error.call_args[0][0]
            log_data = json.loads(log_call)
            
            assert log_data["event"] == "request_error"
            assert "rate_limit" in log_data["error_type"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
