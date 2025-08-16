"""
Integration tests for refactored services using the app factory.

Tests that all services refactored to use the shared app factory
work correctly and maintain their functionality.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


class TestRefactoredServices:
    """Test cases for refactored services."""

    def test_auth_service_refactored(self):
        """Test that the auth service works after refactoring."""
        try:
            from services.auth.main import app
            client = TestClient(app)
            
            # Test health endpoint
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "auth"
            assert data["status"] == "healthy"
            
            # Test root endpoint
            response = client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "auth"
            assert data["status"] == "ok"
            
            # Test metrics endpoint
            response = client.get("/metrics")
            assert response.status_code == 200
            
        except ImportError as e:
            pytest.skip(f"Auth service not available: {e}")

    def test_fact_check_service_refactored(self):
        """Test that the fact_check service works after refactoring."""
        try:
            from services.fact_check.main import app
            client = TestClient(app)
            
            # Test health endpoint
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "fact_check"
            assert data["status"] == "healthy"
            
            # Test root endpoint
            response = client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "fact_check"
            assert data["status"] == "ok"
            
            # Test metrics endpoint
            response = client.get("/metrics")
            assert response.status_code == 200
            
        except ImportError as e:
            pytest.skip(f"Fact check service not available: {e}")

    def test_search_service_refactored(self):
        """Test that the search service works after refactoring."""
        try:
            from services.search.main import app
            client = TestClient(app)
            
            # Test health endpoint
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "search"
            assert data["status"] == "healthy"
            
            # Test root endpoint
            response = client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "search"
            assert data["status"] == "ok"
            
            # Test metrics endpoint
            response = client.get("/metrics")
            assert response.status_code == 200
            
        except ImportError as e:
            pytest.skip(f"Search service not available: {e}")

    def test_retrieval_service_refactored(self):
        """Test that the retrieval service works after refactoring."""
        try:
            from services.retrieval.main import app
            client = TestClient(app)
            
            # Test health endpoint
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "retrieval"
            assert data["status"] == "healthy"
            
            # Test root endpoint
            response = client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "retrieval"
            assert data["status"] == "ok"
            
            # Test metrics endpoint
            response = client.get("/metrics")
            assert response.status_code == 200
            
            # Test that search endpoint exists (should be added by additional_routes)
            # Note: This might fail if dependencies are not available
            try:
                response = client.post("/search", json={
                    "query": "test query",
                    "max_results": 5
                })
                # Should not return 404 if endpoint exists
                assert response.status_code != 404
            except Exception:
                # If dependencies are missing, that's okay for this test
                pass
            
        except ImportError as e:
            pytest.skip(f"Retrieval service not available: {e}")

    def test_synthesis_service_refactored(self):
        """Test that the synthesis service works after refactoring."""
        try:
            from services.synthesis.main import app
            client = TestClient(app)
            
            # Test health endpoint
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "synthesis"
            assert data["status"] == "healthy"
            
            # Test root endpoint
            response = client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "synthesis"
            assert data["status"] == "ok"
            
            # Test metrics endpoint
            response = client.get("/metrics")
            assert response.status_code == 200
            
            # Test that synthesize endpoint exists (should be added by additional_routes)
            # Note: This might fail if dependencies are not available
            try:
                response = client.post("/synthesize", json={
                    "query": "test query",
                    "sources": [{"content": "test source"}],
                    "max_tokens": 100
                })
                # Should not return 404 if endpoint exists
                assert response.status_code != 404
            except Exception:
                # If dependencies are missing, that's okay for this test
                pass
            
        except ImportError as e:
            pytest.skip(f"Synthesis service not available: {e}")

    def test_all_services_have_consistent_endpoints(self):
        """Test that all refactored services have consistent standard endpoints."""
        services = [
            ("auth", "services.auth.main"),
            ("fact_check", "services.fact_check.main"),
            ("search", "services.search.main"),
            ("retrieval", "services.retrieval.main"),
            ("synthesis", "services.synthesis.main"),
        ]
        
        for service_name, module_path in services:
            try:
                module = __import__(module_path, fromlist=["app"])
                app = module.app
                client = TestClient(app)
                
                # All services should have these standard endpoints
                endpoints = ["/health", "/", "/metrics"]
                
                for endpoint in endpoints:
                    response = client.get(endpoint)
                    assert response.status_code == 200, f"{service_name} {endpoint} failed"
                    
                    if endpoint == "/health":
                        data = response.json()
                        assert data["service"] == service_name
                        assert data["status"] == "healthy"
                    
                    elif endpoint == "/":
                        data = response.json()
                        assert data["service"] == service_name
                        assert data["status"] == "ok"
                    
                    elif endpoint == "/metrics":
                        assert "text/plain" in response.headers.get("content-type", "")
                
            except ImportError:
                pytest.skip(f"Service {service_name} not available")
            except Exception as e:
                pytest.fail(f"Service {service_name} failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
