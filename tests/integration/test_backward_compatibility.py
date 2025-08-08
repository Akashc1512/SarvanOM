"""
Backward Compatibility Tests for Phase 2.3.3

This module tests that the service integration maintains backward compatibility
with existing API contracts, response formats, and error handling.
"""

import pytest
import json
from typing import Dict, Any, List
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock

# Import the main application
from services.api_gateway.main import app


class TestBackwardCompatibility:
    """Test backward compatibility of API changes."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_services(self):
        """Create mock services for compatibility testing."""
        browser_service = Mock()
        browser_service.search_web = AsyncMock(return_value={
            "success": True,
            "data": {"results": [{"title": "Test Result", "url": "http://test.com"}]},
            "service_used": "BrowserService"
        })
        
        pdf_service = Mock()
        pdf_service.process_pdf = AsyncMock(return_value={
            "success": True,
            "data": {"text": "Test PDF text", "pages": 1},
            "service_used": "PDFService"
        })
        
        knowledge_service = Mock()
        knowledge_service.query_entities = AsyncMock(return_value={
            "success": True,
            "data": {"entities": [{"id": "1", "name": "Test Entity"}]},
            "service_used": "KnowledgeService"
        })
        
        code_service = Mock()
        code_service.execute_code = AsyncMock(return_value={
            "success": True,
            "data": {"output": "Hello World", "execution_time": 0.1},
            "service_used": "CodeService"
        })
        
        database_service = Mock()
        database_service.execute_query = AsyncMock(return_value={
            "success": True,
            "data": {"results": [{"id": 1, "name": "Test"}]},
            "service_used": "DatabaseService"
        })
        
        crawler_service = Mock()
        crawler_service.crawl_website = AsyncMock(return_value={
            "success": True,
            "data": {"pages_crawled": 10, "links_found": 50},
            "service_used": "CrawlerService"
        })
        
        return {
            "browser": browser_service,
            "pdf": pdf_service,
            "knowledge": knowledge_service,
            "code": code_service,
            "database": database_service,
            "crawler": crawler_service
        }

    async def test_existing_api_contracts_maintained(self, client, mock_services):
        """Test that existing API contracts are maintained."""
        services = mock_services
        
        # Test browser service
        with patch('services.api_gateway.routes.agents.browser_agent.get_browser_service', return_value=services["browser"]):
            response = client.post("/agents/browser/search", json={
                "query": "test query",
                "search_engine": "google"
            })
            
            assert response.status_code == 200
            data = response.json()
            
            # Check for required fields in response format
            assert "success" in data
            assert "data" in data
            assert "error" in data
            assert "service_used" in data
            
            # Validate data structure
            assert isinstance(data["success"], bool)
            assert isinstance(data["data"], dict)
            assert isinstance(data["error"], str)
            assert isinstance(data["service_used"], str)
    
    async def test_response_format_consistency(self, client, mock_services):
        """Test that response format is consistent across all services."""
        services = mock_services
        
        # Test all services to ensure consistent response format
        test_cases = [
            ("browser", "/agents/browser/search", {"query": "test", "search_engine": "google"}),
            ("pdf", "/agents/pdf/process", {"file": ("test.pdf", b"fake content", "application/pdf")}),
            ("knowledge", "/agents/knowledge/query", {"query": "test", "query_type": "entity_relationship"}),
            ("code", "/agents/code/execute", {"code": "print('test')", "language": "python"}),
            ("database", "/agents/database/query", {"query": "SELECT * FROM test", "database": "test_db"}),
            ("crawler", "/agents/crawler/crawl", {"url": "http://test.com", "max_pages": 5})
        ]
        
        for service_name, endpoint, request_data in test_cases:
            with patch(f'services.api_gateway.routes.agents.{service_name}_agent.get_{service_name}_service', return_value=services[service_name]):
                if service_name == "pdf":
                    # Handle file upload for PDF service
                    files = {"file": request_data["file"]}
                    response = client.post(endpoint, files=files)
                else:
                    response = client.post(endpoint, json=request_data)
                
                assert response.status_code == 200
                data = response.json()
                
                # Check consistent response format
                assert "success" in data
                assert "data" in data
                assert "error" in data
                assert "service_used" in data
                
                # Validate data types
                assert isinstance(data["success"], bool)
                assert isinstance(data["data"], dict)
                assert isinstance(data["error"], str)
                assert isinstance(data["service_used"], str)
    
    async def test_error_response_format_consistency(self, client):
        """Test that error response format is consistent."""
        # Test with invalid requests to trigger errors
        invalid_requests = [
            ("/agents/browser/search", {"invalid": "request"}),
            ("/agents/knowledge/query", {"invalid": "request"}),
            ("/agents/code/execute", {"invalid": "request"}),
            ("/agents/database/query", {"invalid": "request"}),
            ("/agents/crawler/crawl", {"invalid": "request"})
        ]
        
        for endpoint, invalid_data in invalid_requests:
            response = client.post(endpoint, json=invalid_data)
            
            # Should return 400 or 422 for invalid requests
            assert response.status_code in [400, 422]
            data = response.json()
            
            # Check error response format
            assert "success" in data
            assert data["success"] == False
            assert "error" in data
            assert "data" in data
    
    async def test_legacy_endpoint_compatibility(self, client, mock_services):
        """Test compatibility with legacy endpoints."""
        services = mock_services
        
        # Test legacy endpoint formats that should still work
        legacy_tests = [
            ("/agents/browser/search", {"query": "legacy test"}),
            ("/agents/knowledge/query", {"query": "legacy test"}),
            ("/agents/code/execute", {"code": "print('legacy')"}),
            ("/agents/database/query", {"query": "SELECT 1"}),
            ("/agents/crawler/crawl", {"url": "http://legacy.com"})
        ]
        
        for endpoint, request_data in legacy_tests:
            service_name = endpoint.split('/')[2]  # Extract service name from endpoint
            with patch(f'services.api_gateway.routes.agents.{service_name}_agent.get_{service_name}_service', return_value=services[service_name]):
                response = client.post(endpoint, json=request_data)
                
                # Legacy endpoints should still work
                assert response.status_code == 200
                data = response.json()
                assert data["success"] == True
    
    async def test_health_endpoint_compatibility(self, client, mock_services):
        """Test health endpoint compatibility."""
        services = mock_services
        
        # Test health endpoints for all services
        health_endpoints = [
            "/agents/browser/health",
            "/agents/pdf/health",
            "/agents/knowledge/health",
            "/agents/code/health",
            "/agents/database/health",
            "/agents/crawler/health"
        ]
        
        for endpoint in health_endpoints:
            service_name = endpoint.split('/')[2]  # Extract service name from endpoint
            services[service_name].health_check = AsyncMock(return_value={
                "status": "healthy",
                "service": f"{service_name.capitalize()}Service"
            })
            
            with patch(f'services.api_gateway.routes.agents.{service_name}_agent.get_{service_name}_service', return_value=services[service_name]):
                response = client.get(endpoint)
                
                assert response.status_code == 200
                data = response.json()
                
                # Health response should have consistent format
                assert "status" in data
                assert data["status"] in ["healthy", "unhealthy"]
    
    async def test_version_compatibility(self, client, mock_services):
        """Test version compatibility of API changes."""
        services = mock_services
        
        # Test that API versioning is maintained
        version_tests = [
            ("/agents/browser/search", "v1"),
            ("/agents/knowledge/query", "v1"),
            ("/agents/code/execute", "v1"),
            ("/agents/database/query", "v1"),
            ("/agents/crawler/crawl", "v1")
        ]
        
        for endpoint, version in version_tests:
            service_name = endpoint.split('/')[2]
            with patch(f'services.api_gateway.routes.agents.{service_name}_agent.get_{service_name}_service', return_value=services[service_name]):
                # Test with version header
                headers = {"X-API-Version": version}
                response = client.post(endpoint, json={"test": "data"}, headers=headers)
                
                # Should handle version headers gracefully
                assert response.status_code in [200, 400, 422]
    
    async def test_data_type_compatibility(self, client, mock_services):
        """Test that data types in requests and responses are compatible."""
        services = mock_services
        
        # Test various data types in requests
        data_type_tests = [
            ("/agents/browser/search", {
                "query": "string test",
                "search_engine": "google",
                "max_results": 10,  # integer
                "include_metadata": True,  # boolean
                "filters": {"domain": "test.com"}  # object
            }),
            ("/agents/knowledge/query", {
                "query": "string test",
                "query_type": "entity_relationship",
                "max_results": 5,  # integer
                "include_metadata": False,  # boolean
                "filters": {"entity_type": "person"}  # object
            }),
            ("/agents/code/execute", {
                "code": "print('test')",  # string
                "language": "python",  # string
                "timeout": 30,  # integer
                "sandbox": True,  # boolean
                "environment": {"variables": {"TEST": "value"}}  # object
            })
        ]
        
        for endpoint, request_data in data_type_tests:
            service_name = endpoint.split('/')[2]
            with patch(f'services.api_gateway.routes.agents.{service_name}_agent.get_{service_name}_service', return_value=services[service_name]):
                response = client.post(endpoint, json=request_data)
                
                # Should handle various data types gracefully
                assert response.status_code in [200, 400, 422]
                
                if response.status_code == 200:
                    data = response.json()
                    # Response should maintain data type consistency
                    assert isinstance(data["success"], bool)
                    assert isinstance(data["data"], dict)
    
    async def test_optional_parameter_compatibility(self, client, mock_services):
        """Test compatibility with optional parameters."""
        services = mock_services
        
        # Test endpoints with optional parameters
        optional_param_tests = [
            ("/agents/browser/search", {"query": "test"}),  # Minimal request
            ("/agents/browser/search", {"query": "test", "search_engine": "google", "max_results": 10}),  # Full request
            ("/agents/knowledge/query", {"query": "test"}),  # Minimal request
            ("/agents/knowledge/query", {"query": "test", "query_type": "entity_relationship", "max_results": 5}),  # Full request
            ("/agents/code/execute", {"code": "print('test')"}),  # Minimal request
            ("/agents/code/execute", {"code": "print('test')", "language": "python", "timeout": 30}),  # Full request
        ]
        
        for endpoint, request_data in optional_param_tests:
            service_name = endpoint.split('/')[2]
            with patch(f'services.api_gateway.routes.agents.{service_name}_agent.get_{service_name}_service', return_value=services[service_name]):
                response = client.post(endpoint, json=request_data)
                
                # Should handle both minimal and full requests
                assert response.status_code in [200, 400, 422]
    
    async def test_error_message_compatibility(self, client):
        """Test that error messages are compatible and helpful."""
        # Test various error scenarios
        error_scenarios = [
            ("/agents/browser/search", {}, "Missing required field"),
            ("/agents/knowledge/query", {}, "Missing required field"),
            ("/agents/code/execute", {}, "Missing required field"),
            ("/agents/database/query", {}, "Missing required field"),
            ("/agents/crawler/crawl", {}, "Missing required field"),
        ]
        
        for endpoint, request_data, expected_error in error_scenarios:
            response = client.post(endpoint, json=request_data)
            
            assert response.status_code in [400, 422]
            data = response.json()
            
            # Error response should be helpful
            assert "error" in data
            assert data["success"] == False
            assert len(data["error"]) > 0  # Error message should not be empty
    
    async def test_content_type_compatibility(self, client, mock_services):
        """Test content type compatibility."""
        services = mock_services
        
        # Test different content types
        content_type_tests = [
            ("application/json", {"query": "test"}),
            ("application/json; charset=utf-8", {"query": "test"}),
        ]
        
        for content_type, request_data in content_type_tests:
            headers = {"Content-Type": content_type}
            with patch('services.api_gateway.routes.agents.browser_agent.get_browser_service', return_value=services["browser"]):
                response = client.post("/agents/browser/search", json=request_data, headers=headers)
                
                # Should handle different content types gracefully
                assert response.status_code in [200, 400, 422]
    
    async def test_encoding_compatibility(self, client, mock_services):
        """Test encoding compatibility."""
        services = mock_services
        
        # Test with different encodings
        encoding_tests = [
            "Hello World",  # ASCII
            "Hello 世界",  # Unicode
            "Special chars: !@#$%^&*()",  # Special characters
        ]
        
        for test_string in encoding_tests:
            with patch('services.api_gateway.routes.agents.browser_agent.get_browser_service', return_value=services["browser"]):
                response = client.post("/agents/browser/search", json={
                    "query": test_string,
                    "search_engine": "google"
                })
                
                # Should handle different encodings gracefully
                assert response.status_code in [200, 400, 422]


class TestMigrationCompatibility:
    """Test compatibility with migration scenarios."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    async def test_old_to_new_api_migration(self, client):
        """Test migration from old API format to new service-based format."""
        # Simulate old API format
        old_format_tests = [
            ("/agents/browser/search", {"search_query": "old format"}),
            ("/agents/knowledge/query", {"knowledge_query": "old format"}),
            ("/agents/code/execute", {"code_block": "print('old')"}),
        ]
        
        for endpoint, old_format_data in old_format_tests:
            response = client.post(endpoint, json=old_format_data)
            
            # Should handle old format gracefully (either work or give clear error)
            assert response.status_code in [200, 400, 422]
    
    async def test_parameter_name_changes(self, client):
        """Test compatibility with parameter name changes."""
        # Test various parameter name variations
        parameter_variations = [
            {"query": "test", "search_engine": "google"},
            {"search_query": "test", "engine": "google"},
            {"q": "test", "search_type": "google"},
        ]
        
        for params in parameter_variations:
            response = client.post("/agents/browser/search", json=params)
            
            # Should handle parameter variations gracefully
            assert response.status_code in [200, 400, 422]


if __name__ == "__main__":
    pytest.main([__file__]) 