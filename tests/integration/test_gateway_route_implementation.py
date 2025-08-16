"""
Integration tests for Gateway Route Implementation

This module tests that the API Gateway routes are properly implemented
with actual calls to microservices instead of placeholder responses.
"""

import pytest
import asyncio
from typing import Dict, Any
from unittest.mock import patch, AsyncMock

from services.gateway.routes import (
    fact_check_router,
    synthesis_router,
    auth_router,
    vector_router,
    FactCheckRequest,
    ServiceResponse,
)


class TestGatewayRouteImplementation:
    """Test that gateway routes are properly implemented."""

    @pytest.mark.asyncio
    async def test_fact_check_routes_implemented(self):
        """Test that fact-check routes call the actual service."""
        # Test POST /fact-check/
        request = FactCheckRequest(claim="Test claim", context={"test": "data"})
        
        with patch('shared.clients.microservices.call_factcheck_verify') as mock_call:
            mock_call.return_value = {
                "verification_status": "unverified",
                "confidence_score": 0.5,
                "sources": [],
                "reasoning": "Test response"
            }
            
            # Get the route handler
            route_handler = None
            for route in fact_check_router.routes:
                if route.path == "/" and "POST" in route.methods:
                    route_handler = route.endpoint
                    break
            
            assert route_handler is not None, "Fact-check POST route not found"
            
            # Call the handler
            response = await route_handler(request)
            
            # Verify it's a ServiceResponse
            assert isinstance(response, ServiceResponse)
            assert response.status == "success"
            assert response.service == "fact-check"
            
            # Verify the service was called
            mock_call.assert_called_once()

    @pytest.mark.asyncio
    async def test_synthesis_routes_implemented(self):
        """Test that synthesis routes call the actual service."""
        from shared.contracts.query import SynthesisRequest
        
        request = SynthesisRequest(
            query="Test query",
            sources=[{"content": "Test source"}],
            verification={"enabled": True},
            max_tokens=1000,
            context={"test": "data"}
        )
        
        with patch('shared.clients.microservices.call_synthesis_synthesize') as mock_call:
            mock_call.return_value = {
                "content": "Test synthesis result",
                "citations": [],
                "confidence": 0.8
            }
            
            # Get the route handler
            route_handler = None
            for route in synthesis_router.routes:
                if route.path == "/" and "POST" in route.methods:
                    route_handler = route.endpoint
                    break
            
            assert route_handler is not None, "Synthesis POST route not found"
            
            # Call the handler
            response = await route_handler(request)
            
            # Verify it's a ServiceResponse
            assert isinstance(response, ServiceResponse)
            assert response.status == "success"
            assert response.service == "synthesis"
            
            # Verify the service was called
            mock_call.assert_called_once()

    @pytest.mark.asyncio
    async def test_auth_routes_implemented(self):
        """Test that auth routes call the actual service."""
        from shared.core.api.api_models import LoginRequest
        
        request = LoginRequest(
            username="testuser",
            password="testpass123!"
        )
        
        with patch('shared.clients.microservices.call_auth_login') as mock_call:
            mock_call.return_value = {
                "access_token": "test_token",
                "refresh_token": "test_refresh",
                "user": {"username": "testuser"}
            }
            
            # Get the route handler
            route_handler = None
            for route in auth_router.routes:
                if route.path == "/login" and "POST" in route.methods:
                    route_handler = route.endpoint
                    break
            
            assert route_handler is not None, "Auth login route not found"
            
            # Call the handler
            response = await route_handler(request)
            
            # Verify it's a ServiceResponse
            assert isinstance(response, ServiceResponse)
            assert response.status == "success"
            assert response.service == "auth"
            
            # Verify the service was called
            mock_call.assert_called_once()

    @pytest.mark.asyncio
    async def test_vector_routes_implemented(self):
        """Test that vector routes call the actual service."""
        from shared.contracts.query import VectorEmbedRequest
        
        request = VectorEmbedRequest(
            text="Test text for embedding",
            metadata={"test": "data"}
        )
        
        with patch('shared.clients.microservices.call_retrieval_embed') as mock_call:
            mock_call.return_value = {
                "embedding": [0.1, 0.2, 0.3],
                "text": "Test text for embedding",
                "metadata": {"test": "data"}
            }
            
            # Get the route handler
            route_handler = None
            for route in vector_router.routes:
                if route.path == "/embed" and "POST" in route.methods:
                    route_handler = route.endpoint
                    break
            
            assert route_handler is not None, "Vector embed route not found"
            
            # Call the handler
            response = await route_handler(request)
            
            # Verify it's a ServiceResponse
            assert isinstance(response, ServiceResponse)
            assert response.status == "success"
            assert response.service == "vector"
            
            # Verify the service was called
            mock_call.assert_called_once()

    def test_crawler_routes_removed(self):
        """Test that crawler routes have been removed."""
        # Check that crawler_router is not imported in routes.py
        import services.gateway.routes as routes_module
        
        # Verify crawler_router is not defined
        assert not hasattr(routes_module, 'crawler_router'), "crawler_router should be removed"
        
        # Verify CrawlerRequest is not defined
        assert not hasattr(routes_module, 'CrawlerRequest'), "CrawlerRequest should be removed"

    def test_graph_routes_removed(self):
        """Test that graph routes have been removed."""
        # Check that graph_router is not imported in routes.py
        import services.gateway.routes as routes_module
        
        # Verify graph_router is not defined
        assert not hasattr(routes_module, 'graph_router'), "graph_router should be removed"
        
        # Verify GraphRequest is not defined
        assert not hasattr(routes_module, 'GraphRequest'), "GraphRequest should be removed"

    def test_gateway_app_updated(self):
        """Test that gateway app no longer includes removed routers."""
        import services.gateway.gateway_app as gateway_app_module
        
        # Check that the imports don't include removed routers
        assert 'crawler_router' not in gateway_app_module.__dict__, "crawler_router should not be imported"
        assert 'graph_router' not in gateway_app_module.__dict__, "graph_router should not be imported"

    def test_services_init_updated(self):
        """Test that services __init__.py no longer exports removed routers."""
        import services as services_module
        
        # Check that the exports don't include removed routers
        assert 'crawler_router' not in services_module.__all__, "crawler_router should not be exported"
        assert 'graph_router' not in services_module.__all__, "graph_router should not be exported"
