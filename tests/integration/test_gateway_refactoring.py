"""
Integration tests for refactored gateway routes using shared contract models.

Tests that the gateway routes properly use shared contract models instead of
duplicate local definitions, ensuring consistency across the platform.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


class TestGatewayRefactoring:
    """Test cases for refactored gateway routes."""

    def test_gateway_imports_shared_models(self):
        """Test that gateway routes import shared models correctly."""
        try:
            from services.gateway.routes import (
                QueryRequest,
                LoginRequest,
                RegisterRequest,
                HealthResponse,
                SharedSynthesisRequest,
                SharedSearchRequest,
            )
            
            # Verify that we're using shared models
            assert QueryRequest.__module__ == "shared.core.api.api_models"
            assert LoginRequest.__module__ == "shared.core.api.api_models"
            assert RegisterRequest.__module__ == "shared.core.api.api_models"
            assert HealthResponse.__module__ == "shared.core.api.api_models"
            assert SharedSynthesisRequest.__module__ == "shared.contracts.query"
            assert SharedSearchRequest.__module__ == "shared.contracts.query"
            
            print("✅ Gateway successfully imports shared models")
            
        except ImportError as e:
            pytest.fail(f"Failed to import shared models: {e}")

    def test_gateway_health_endpoint_uses_shared_model(self):
        """Test that health endpoint uses shared HealthResponse model."""
        try:
            from services.gateway.routes import health_router
            from shared.core.api.api_models import HealthResponse
            
            # Create a test client
            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(health_router)
            client = TestClient(app)
            
            # Test health endpoint
            response = client.get("/health")
            assert response.status_code == 200
            
            data = response.json()
            # Verify the response matches the shared HealthResponse model structure
            assert "status" in data
            assert "timestamp" in data
            assert "version" in data
            assert "uptime" in data
            assert "memory_usage" in data
            assert "cpu_usage" in data
            
            print("✅ Health endpoint uses shared HealthResponse model")
            
        except Exception as e:
            pytest.fail(f"Health endpoint test failed: {e}")

    def test_gateway_search_endpoint_uses_shared_model(self):
        """Test that search endpoint uses shared QueryRequest model."""
        try:
            from services.gateway.routes import search_router
            from shared.core.api.api_models import QueryRequest
            
            # Create a test client
            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(search_router)
            client = TestClient(app)
            
            # Test search endpoint with shared model
            test_request = {
                "query": "test query",
                "context": "test context",
                "user_id": "test_user",
                "session_id": "test_session",
                "source": "test",
                "metadata": {"test": "data"}
            }
            
            response = client.post("/", json=test_request)
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] in ["success", "partial_success", "error"]
            assert data["service"] == "search"
            
            print("✅ Search endpoint uses shared QueryRequest model")
            
        except Exception as e:
            pytest.fail(f"Search endpoint test failed: {e}")

    def test_gateway_synthesis_endpoint_uses_shared_model(self):
        """Test that synthesis endpoint uses shared SynthesisRequest model."""
        try:
            from services.gateway.routes import synthesis_router
            from shared.contracts.query import SynthesisRequest as SharedSynthesisRequest
            
            # Create a test client
            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(synthesis_router)
            client = TestClient(app)
            
            # Test synthesis endpoint with shared model
            test_request = {
                "query": "test synthesis query",
                "sources": [{"title": "Test Source", "url": "http://test.com"}],
                "verification": {"verified": True},
                "max_tokens": 1000,
                "context": {"domain": "test"}
            }
            
            response = client.post("/", json=test_request)
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success"
            assert data["service"] == "synthesis"
            
            print("✅ Synthesis endpoint uses shared SynthesisRequest model")
            
        except Exception as e:
            pytest.fail(f"Synthesis endpoint test failed: {e}")

    def test_gateway_auth_endpoints_use_shared_models(self):
        """Test that auth endpoints use shared models."""
        try:
            from services.gateway.routes import auth_router
            from shared.core.api.api_models import LoginRequest, RegisterRequest
            
            # Create a test client
            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(auth_router)
            client = TestClient(app)
            
            # Test login endpoint
            login_request = {
                "username": "testuser",
                "password": "testpassword123",
                "remember_me": True,
                "device_info": {"browser": "test"}
            }
            
            response = client.post("/login", json=login_request)
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success"
            assert data["service"] == "auth"
            
            # Test register endpoint
            register_request = {
                "username": "newuser",
                "email": "newuser@test.com",
                "password": "newpassword123",
                "full_name": "New User",
                "role": "user"
            }
            
            response = client.post("/register", json=register_request)
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success"
            assert data["service"] == "auth"
            
            print("✅ Auth endpoints use shared models")
            
        except Exception as e:
            pytest.fail(f"Auth endpoints test failed: {e}")

    def test_gateway_no_duplicate_models(self):
        """Test that gateway doesn't have duplicate model definitions."""
        try:
            import services.gateway.routes as gateway_routes
            
            # Check that we don't have duplicate model definitions
            # The gateway should only have ServiceResponse and gateway-specific models
            expected_gateway_models = {
                'ServiceResponse',
                'FactCheckRequest', 
                'CrawlerRequest',
                'VectorRequest',
                'GraphRequest'
            }
            
            # Get all classes defined in the module
            module_classes = {
                name for name, obj in gateway_routes.__dict__.items()
                if isinstance(obj, type) and hasattr(obj, '__module__') 
                and obj.__module__ == gateway_routes.__name__
            }
            
            # Remove expected gateway-specific models
            unexpected_models = module_classes - expected_gateway_models
            
            # Remove any FastAPI or Pydantic base classes
            unexpected_models = {
                name for name in unexpected_models 
                if not name.startswith('_') and name not in ['BaseModel', 'APIRouter', 'HTTPException']
            }
            
            if unexpected_models:
                pytest.fail(f"Found unexpected duplicate models in gateway: {unexpected_models}")
            
            print("✅ Gateway has no duplicate model definitions")
            
        except Exception as e:
            pytest.fail(f"Duplicate models check failed: {e}")

    def test_shared_models_consistency(self):
        """Test that shared models are consistent across the platform."""
        try:
            # Import models from different locations to ensure consistency
            from shared.contracts.query import SynthesisRequest as ContractSynthesisRequest
            from shared.core.api.api_models import QueryRequest as APIQueryRequest
            
            # Verify model structures by checking field names
            synthesis_fields = ContractSynthesisRequest.model_fields.keys()
            assert 'query' in synthesis_fields
            assert 'sources' in synthesis_fields
            assert 'verification' in synthesis_fields
            assert 'max_tokens' in synthesis_fields
            assert 'context' in synthesis_fields
            
            query_fields = APIQueryRequest.model_fields.keys()
            assert 'query' in query_fields
            assert 'context' in query_fields
            assert 'user_id' in query_fields
            assert 'session_id' in query_fields
            assert 'source' in query_fields
            assert 'metadata' in query_fields
            
            print("✅ Shared models are consistent across the platform")
            
        except Exception as e:
            pytest.fail(f"Shared models consistency check failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
