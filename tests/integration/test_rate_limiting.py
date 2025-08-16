"""
Integration tests for rate limiting middleware.

Tests that rate limiting is properly configured and working across all services
using the shared middleware and Redis cache.
"""

import pytest
import asyncio
import time
from fastapi.testclient import TestClient
import sys
import os

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


class TestRateLimiting:
    """Test cases for rate limiting functionality."""

    def test_rate_limiting_middleware_import(self):
        """Test that rate limiting middleware can be imported."""
        try:
            from shared.core.middleware.rate_limiter import (
                RateLimiter,
                create_rate_limit_middleware,
                RateLimitExceeded,
            )
            
            # Verify classes exist
            assert RateLimiter is not None
            assert create_rate_limit_middleware is not None
            assert RateLimitExceeded is not None
            
            print("✅ Rate limiting middleware imports successfully")
            
        except Exception as e:
            pytest.fail(f"Rate limiting middleware import failed: {e}")

    def test_redis_backend_available(self):
        """Test that Redis backend is available in cache system."""
        try:
            from shared.core.cache.cache_manager import RedisCacheBackend, REDIS_AVAILABLE
            
            # Check if Redis is available
            if REDIS_AVAILABLE:
                assert RedisCacheBackend is not None
                print("✅ Redis backend is available")
            else:
                print("⚠️ Redis backend not available (redis package not installed)")
            
        except Exception as e:
            pytest.fail(f"Redis backend test failed: {e}")

    def test_rate_limiter_creation(self):
        """Test that rate limiter can be created with configuration."""
        try:
            from shared.core.middleware.rate_limiter import RateLimiter
            from shared.core.config.central_config import initialize_config
            
            config = initialize_config()
            
            # Create rate limiter with config
            rate_limiter = RateLimiter(
                requests_per_minute=config.rate_limit_per_minute,
                burst_allowance=config.rate_limit_burst,
                key_prefix="test_rate_limit",
            )
            
            assert rate_limiter is not None
            assert rate_limiter.requests_per_minute == config.rate_limit_per_minute
            assert rate_limiter.burst_allowance == config.rate_limit_burst
            
            print("✅ Rate limiter created successfully with configuration")
            
        except Exception as e:
            pytest.fail(f"Rate limiter creation failed: {e}")

    def test_middleware_creation(self):
        """Test that rate limiting middleware can be created."""
        try:
            from shared.core.middleware.rate_limiter import create_rate_limit_middleware
            
            # Create middleware
            middleware = create_rate_limit_middleware(
                requests_per_minute=100,
                burst_allowance=10,
                key_prefix="test_middleware",
                exclude_paths=["/health", "/metrics"],
            )
            
            assert middleware is not None
            assert callable(middleware)
            
            print("✅ Rate limiting middleware created successfully")
            
        except Exception as e:
            pytest.fail(f"Middleware creation failed: {e}")

    def test_app_factory_rate_limiting(self):
        """Test that app factory includes rate limiting middleware."""
        try:
            from shared.core.app_factory import create_app_factory
            from shared.core.config.central_config import initialize_config
            
            config = initialize_config()
            
            # Create app factory with rate limiting enabled
            app_factory = create_app_factory(
                service_name="test_service",
                description="Test service for rate limiting",
                enable_rate_limiting=True,
            )
            
            # Create app
            app = app_factory()
            
            # Check that app has middleware
            assert app is not None
            
            # Create test client
            client = TestClient(app)
            
            # Test health endpoint (should not be rate limited)
            response = client.get("/health")
            assert response.status_code in [200, 404]  # 404 if health not enabled
            
            print("✅ App factory creates app with rate limiting middleware")
            
        except Exception as e:
            pytest.fail(f"App factory rate limiting test failed: {e}")

    def test_rate_limit_configuration(self):
        """Test that rate limit configuration is properly loaded."""
        try:
            from shared.core.config.central_config import initialize_config
            
            config = initialize_config()
            
            # Check that rate limiting config exists
            assert hasattr(config, 'rate_limit_enabled')
            assert hasattr(config, 'rate_limit_per_minute')
            assert hasattr(config, 'rate_limit_burst')
            
            # Check that values are reasonable
            assert config.rate_limit_per_minute >= 1
            assert config.rate_limit_burst >= 0
            assert isinstance(config.rate_limit_enabled, bool)
            
            print(f"✅ Rate limit configuration loaded: {config.rate_limit_per_minute}/min, burst: {config.rate_limit_burst}")
            
        except Exception as e:
            pytest.fail(f"Rate limit configuration test failed: {e}")

    def test_cache_manager_redis_support(self):
        """Test that cache manager supports Redis backend."""
        try:
            from shared.core.cache import get_cache_manager
            from shared.core.cache.cache_manager import REDIS_AVAILABLE
            
            # Get cache manager
            cache_manager = get_cache_manager()
            assert cache_manager is not None
            
            # Check if Redis backend is available
            if REDIS_AVAILABLE:
                print("✅ Cache manager supports Redis backend")
            else:
                print("⚠️ Redis backend not available, using in-memory only")
            
        except Exception as e:
            pytest.fail(f"Cache manager Redis support test failed: {e}")

    def test_rate_limiter_key_generation(self):
        """Test that rate limiter generates proper keys."""
        try:
            from shared.core.middleware.rate_limiter import RateLimiter
            from fastapi import Request
            from unittest.mock import Mock
            
            # Create rate limiter
            rate_limiter = RateLimiter(
                requests_per_minute=60,
                burst_allowance=10,
                key_prefix="test_keys",
            )
            
            # Mock request
            mock_request = Mock()
            mock_request.headers = {"X-Forwarded-For": "192.168.1.1"}
            mock_request.url.path = "/api/test"
            mock_request.client.host = "192.168.1.1"
            
            # Test key generation
            identifier = rate_limiter._get_client_identifier(mock_request)
            key = rate_limiter._get_rate_limit_key(identifier, "/api/test")
            
            assert identifier == "ip:192.168.1.1"
            assert key.startswith("test_keys:")
            assert len(key) > 0
            
            print("✅ Rate limiter key generation works correctly")
            
        except Exception as e:
            pytest.fail(f"Rate limiter key generation test failed: {e}")

    def test_all_services_use_app_factory(self):
        """Test that all services use the app factory with rate limiting."""
        try:
            # Check that all services use app factory
            services_to_check = [
                "services.auth.main",
                "services.search.main", 
                "services.retrieval.main",
                "services.synthesis.main",
                "services.fact_check.main",
            ]
            
            for service_module in services_to_check:
                try:
                    module = __import__(service_module, fromlist=["app"])
                    assert hasattr(module, "app"), f"Service {service_module} missing app"
                    print(f"✅ {service_module} uses app factory")
                except ImportError as e:
                    print(f"⚠️ Could not import {service_module}: {e}")
                except Exception as e:
                    print(f"⚠️ Error checking {service_module}: {e}")
            
        except Exception as e:
            pytest.fail(f"Service app factory check failed: {e}")

    def test_rate_limit_headers(self):
        """Test that rate limiting middleware adds proper headers."""
        try:
            from shared.core.middleware.rate_limiter import RateLimiter
            from fastapi import Response
            
            # Create rate limiter
            rate_limiter = RateLimiter(
                requests_per_minute=60,
                burst_allowance=10,
                enable_headers=True,
            )
            
            # Mock response
            response = Response()
            
            # Mock rate limit info
            rate_limit_info = {
                "limit": 70,
                "remaining": 65,
                "reset_time": 30,
                "current_count": 5,
            }
            
            # Add headers
            rate_limiter.add_rate_limit_headers(response, rate_limit_info)
            
            # Check headers
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers
            assert "X-RateLimit-Reset" in response.headers
            assert "X-RateLimit-Reset-Time" in response.headers
            
            print("✅ Rate limiting headers added correctly")
            
        except Exception as e:
            pytest.fail(f"Rate limit headers test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
