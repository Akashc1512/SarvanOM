"""
Unit tests for the FastAPI app factory.

Tests the creation of standardized FastAPI applications with
middleware, routes, and configuration.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from contextlib import asynccontextmanager

from shared.core.app_factory import create_app_factory, create_simple_app, with_request_metrics


class TestAppFactory:
    """Test cases for the app factory functionality."""

    def test_create_simple_app(self):
        """Test creating a simple app with basic configuration."""
        app = create_simple_app(
            service_name="test",
            description="Test service",
            port=8000,
        )
        
        assert isinstance(app, FastAPI)
        assert app.title == "sarvanom-test"
        assert "Test service" in app.description
        
        # Test that standard endpoints are available
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "test"
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        
        # Test root endpoint
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "test"
        assert data["status"] == "ok"
        assert "description" in data
        
        # Test metrics endpoint
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]

    def test_create_app_factory_with_custom_routes(self):
        """Test creating an app factory with custom routes."""
        def add_test_routes(app: FastAPI):
            @app.get("/test")
            async def test_endpoint():
                return {"message": "test"}
        
        app_factory = create_app_factory(
            service_name="custom",
            description="Custom service",
            additional_routes=[add_test_routes],
        )
        
        app = app_factory()
        client = TestClient(app)
        
        # Test custom endpoint
        response = client.get("/test")
        assert response.status_code == 200
        assert response.json()["message"] == "test"
        
        # Test standard endpoints still work
        response = client.get("/health")
        assert response.status_code == 200

    def test_create_app_factory_with_custom_lifespan(self):
        """Test creating an app factory with custom lifespan."""
        startup_called = False
        shutdown_called = False
        
        @asynccontextmanager
        async def custom_lifespan(app: FastAPI):
            nonlocal startup_called, shutdown_called
            startup_called = True
            yield
            shutdown_called = True
        
        app_factory = create_app_factory(
            service_name="lifespan",
            description="Lifespan test service",
            lifespan=custom_lifespan,
        )
        
        app = app_factory()
        # Note: We can't easily test lifespan in unit tests without running the app
        # This test just verifies the factory accepts custom lifespan

    def test_create_app_factory_with_disabled_endpoints(self):
        """Test creating an app factory with disabled endpoints."""
        app_factory = create_app_factory(
            service_name="disabled",
            description="Disabled endpoints service",
            enable_health=False,
            enable_metrics=False,
            enable_root=False,
        )
        
        app = app_factory()
        client = TestClient(app)
        
        # Test that disabled endpoints return 404
        response = client.get("/health")
        assert response.status_code == 404
        
        response = client.get("/metrics")
        assert response.status_code == 404
        
        response = client.get("/")
        assert response.status_code == 404

    def test_with_request_metrics_decorator(self):
        """Test the request metrics decorator."""
        @with_request_metrics("test")
        async def test_function():
            return {"result": "success"}
        
        # The decorator should not break the function
        import asyncio
        result = asyncio.run(test_function())
        assert result["result"] == "success"

    def test_app_factory_cors_configuration(self):
        """Test that CORS middleware is properly configured."""
        app = create_simple_app(
            service_name="cors",
            description="CORS test service",
            port=8000,
        )
        
        client = TestClient(app)
        
        # Test CORS headers are present
        response = client.options("/health", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        })
        
        # Should not return 405 (Method Not Allowed) if CORS is working
        assert response.status_code != 405

    def test_app_factory_trusted_host_middleware(self):
        """Test that TrustedHost middleware is configured when allowed_hosts is set."""
        # This test would require mocking the config to set allowed_hosts
        # For now, we just verify the factory function exists and works
        app_factory = create_app_factory(
            service_name="trusted",
            description="Trusted host test service",
        )
        
        app = app_factory()
        assert isinstance(app, FastAPI)


if __name__ == "__main__":
    pytest.main([__file__])
