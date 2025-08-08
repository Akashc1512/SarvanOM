"""
Service Integration Tests for Phase 2.3.3

This module tests the integration of all 6 agent services with their respective
route handlers, ensuring proper dependency injection, error handling, and
backward compatibility.
"""

import pytest
import asyncio
import time
from typing import Dict, Any
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock

# Import the main application
from services.api_gateway.main import app
from services.api_gateway.services.browser_service import BrowserService
from services.api_gateway.services.pdf_service import PDFService
from services.api_gateway.services.knowledge_service import KnowledgeService
from services.api_gateway.services.code_service import CodeService
from services.api_gateway.services.database_service import DatabaseService
from services.api_gateway.services.crawler_service import CrawlerService


class TestServiceIntegration:
    """Test service integration in route handlers."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_browser_service(self):
        """Create mock browser service."""
        service = Mock(spec=BrowserService)
        service.search_web = AsyncMock(return_value={
            "success": True,
            "data": {"results": [{"title": "Test Result", "url": "http://test.com"}]},
            "service_used": "BrowserService"
        })
        service.extract_content = AsyncMock(return_value={
            "success": True,
            "data": {"content": "Test content extracted"},
            "service_used": "BrowserService"
        })
        service.browse_page = AsyncMock(return_value={
            "success": True,
            "data": {"page_content": "Test page content"},
            "service_used": "BrowserService"
        })
        service.health_check = AsyncMock(return_value={
            "status": "healthy",
            "service": "BrowserService"
        })
        return service
    
    @pytest.fixture
    def mock_pdf_service(self):
        """Create mock PDF service."""
        service = Mock(spec=PDFService)
        service.process_pdf = AsyncMock(return_value={
            "success": True,
            "data": {"text": "Test PDF text", "pages": 1},
            "service_used": "PDFService"
        })
        service.extract_text = AsyncMock(return_value={
            "success": True,
            "data": {"text": "Extracted text"},
            "service_used": "PDFService"
        })
        service.extract_images = AsyncMock(return_value={
            "success": True,
            "data": {"images": ["image1.png", "image2.png"]},
            "service_used": "PDFService"
        })
        service.analyze_pdf = AsyncMock(return_value={
            "success": True,
            "data": {"analysis": "PDF analysis result"},
            "service_used": "PDFService"
        })
        service.health_check = AsyncMock(return_value={
            "status": "healthy",
            "service": "PDFService"
        })
        return service
    
    @pytest.fixture
    def mock_knowledge_service(self):
        """Create mock knowledge service."""
        service = Mock(spec=KnowledgeService)
        service.query_entities = AsyncMock(return_value={
            "success": True,
            "data": {"entities": [{"id": "1", "name": "Test Entity"}]},
            "service_used": "KnowledgeService"
        })
        service.query_relationships = AsyncMock(return_value={
            "success": True,
            "data": {"relationships": [{"from": "1", "to": "2", "type": "RELATES_TO"}]},
            "service_used": "KnowledgeService"
        })
        service.find_paths = AsyncMock(return_value={
            "success": True,
            "data": {"paths": [["1", "2", "3"]]},
            "service_used": "KnowledgeService"
        })
        service.search_entities = AsyncMock(return_value={
            "success": True,
            "data": {"entities": [{"id": "1", "name": "Search Result"}]},
            "service_used": "KnowledgeService"
        })
        service.health_check = AsyncMock(return_value={
            "status": "healthy",
            "service": "KnowledgeService"
        })
        return service
    
    @pytest.fixture
    def mock_code_service(self):
        """Create mock code service."""
        service = Mock(spec=CodeService)
        service.execute_code = AsyncMock(return_value={
            "success": True,
            "data": {"output": "Hello World", "execution_time": 0.1},
            "service_used": "CodeService"
        })
        service.validate_syntax = AsyncMock(return_value={
            "success": True,
            "data": {"valid": True, "errors": []},
            "service_used": "CodeService"
        })
        service.analyze_code = AsyncMock(return_value={
            "success": True,
            "data": {"complexity": "low", "lines": 10},
            "service_used": "CodeService"
        })
        service.upload_and_execute = AsyncMock(return_value={
            "success": True,
            "data": {"result": "Code executed successfully"},
            "service_used": "CodeService"
        })
        service.health_check = AsyncMock(return_value={
            "status": "healthy",
            "service": "CodeService"
        })
        return service
    
    @pytest.fixture
    def mock_database_service(self):
        """Create mock database service."""
        service = Mock(spec=DatabaseService)
        service.execute_query = AsyncMock(return_value={
            "success": True,
            "data": {"results": [{"id": 1, "name": "Test"}]},
            "service_used": "DatabaseService"
        })
        service.get_schema = AsyncMock(return_value={
            "success": True,
            "data": {"tables": ["users", "posts"]},
            "service_used": "DatabaseService"
        })
        service.analyze_data = AsyncMock(return_value={
            "success": True,
            "data": {"analysis": "Data analysis result"},
            "service_used": "DatabaseService"
        })
        service.optimize_query = AsyncMock(return_value={
            "success": True,
            "data": {"optimized_query": "SELECT * FROM users"},
            "service_used": "DatabaseService"
        })
        service.list_databases = AsyncMock(return_value={
            "success": True,
            "data": {"databases": ["test_db", "prod_db"]},
            "service_used": "DatabaseService"
        })
        service.test_connection = AsyncMock(return_value={
            "success": True,
            "data": {"connected": True},
            "service_used": "DatabaseService"
        })
        service.health_check = AsyncMock(return_value={
            "status": "healthy",
            "service": "DatabaseService"
        })
        return service
    
    @pytest.fixture
    def mock_crawler_service(self):
        """Create mock crawler service."""
        service = Mock(spec=CrawlerService)
        service.crawl_website = AsyncMock(return_value={
            "success": True,
            "data": {"pages_crawled": 10, "links_found": 50},
            "service_used": "CrawlerService"
        })
        service.extract_content = AsyncMock(return_value={
            "success": True,
            "data": {"content": "Extracted content"},
            "service_used": "CrawlerService"
        })
        service.discover_links = AsyncMock(return_value={
            "success": True,
            "data": {"links": ["http://link1.com", "http://link2.com"]},
            "service_used": "CrawlerService"
        })
        service.generate_sitemap = AsyncMock(return_value={
            "success": True,
            "data": {"sitemap": "Generated sitemap"},
            "service_used": "CrawlerService"
        })
        service.crawl_with_filters = AsyncMock(return_value={
            "success": True,
            "data": {"filtered_results": "Filtered crawl results"},
            "service_used": "CrawlerService"
        })
        service.health_check = AsyncMock(return_value={
            "status": "healthy",
            "service": "CrawlerService"
        })
        return service

    # Browser Service Tests
    async def test_browser_service_injection(self, client, mock_browser_service):
        """Test browser service injection in route handler."""
        with patch('services.api_gateway.routes.agents.browser_agent.get_browser_service', return_value=mock_browser_service):
            response = client.post("/agents/browser/search", json={
                "query": "test query",
                "search_engine": "google",
                "max_results": 5
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert data["success"] == True
            assert "service_used" in data
            assert data["service_used"] == "BrowserService"
    
    async def test_browser_extract_content(self, client, mock_browser_service):
        """Test browser content extraction endpoint."""
        with patch('services.api_gateway.routes.agents.browser_agent.get_browser_service', return_value=mock_browser_service):
            response = client.post("/agents/browser/extract", json={
                "url": "http://test.com",
                "extract_type": "content"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert data["success"] == True
            assert "service_used" in data
            assert data["service_used"] == "BrowserService"
    
    async def test_browser_health_check(self, client, mock_browser_service):
        """Test browser service health check."""
        with patch('services.api_gateway.routes.agents.browser_agent.get_browser_service', return_value=mock_browser_service):
            response = client.get("/agents/browser/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"
            assert "service" in data
            assert data["service"] == "BrowserService"

    # PDF Service Tests
    async def test_pdf_service_injection(self, client, mock_pdf_service):
        """Test PDF service injection in route handler."""
        with patch('services.api_gateway.routes.agents.pdf_agent.get_pdf_service', return_value=mock_pdf_service):
            files = {"file": ("test.pdf", b"fake pdf content", "application/pdf")}
            response = client.post("/agents/pdf/process", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert data["success"] == True
            assert "service_used" in data
            assert data["service_used"] == "PDFService"
    
    async def test_pdf_extract_text(self, client, mock_pdf_service):
        """Test PDF text extraction endpoint."""
        with patch('services.api_gateway.routes.agents.pdf_agent.get_pdf_service', return_value=mock_pdf_service):
            files = {"file": ("test.pdf", b"fake pdf content", "application/pdf")}
            response = client.post("/agents/pdf/extract-text", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert data["success"] == True
            assert "service_used" in data
            assert data["service_used"] == "PDFService"
    
    async def test_pdf_health_check(self, client, mock_pdf_service):
        """Test PDF service health check."""
        with patch('services.api_gateway.routes.agents.pdf_agent.get_pdf_service', return_value=mock_pdf_service):
            response = client.get("/agents/pdf/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"
            assert "service" in data
            assert data["service"] == "PDFService"

    # Knowledge Service Tests
    async def test_knowledge_service_injection(self, client, mock_knowledge_service):
        """Test knowledge service injection in route handler."""
        with patch('services.api_gateway.routes.agents.knowledge_agent.get_knowledge_service', return_value=mock_knowledge_service):
            response = client.post("/agents/knowledge/query", json={
                "query": "test knowledge query",
                "query_type": "entity_relationship"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert data["success"] == True
            assert "service_used" in data
            assert data["service_used"] == "KnowledgeService"
    
    async def test_knowledge_find_paths(self, client, mock_knowledge_service):
        """Test knowledge path finding endpoint."""
        with patch('services.api_gateway.routes.agents.knowledge_agent.get_knowledge_service', return_value=mock_knowledge_service):
            response = client.post("/agents/knowledge/paths", json={
                "from_entity": "entity1",
                "to_entity": "entity2"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert data["success"] == True
            assert "service_used" in data
            assert data["service_used"] == "KnowledgeService"
    
    async def test_knowledge_health_check(self, client, mock_knowledge_service):
        """Test knowledge service health check."""
        with patch('services.api_gateway.routes.agents.knowledge_agent.get_knowledge_service', return_value=mock_knowledge_service):
            response = client.get("/agents/knowledge/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"
            assert "service" in data
            assert data["service"] == "KnowledgeService"

    # Code Service Tests
    async def test_code_service_injection(self, client, mock_code_service):
        """Test code service injection in route handler."""
        with patch('services.api_gateway.routes.agents.code_agent.get_code_service', return_value=mock_code_service):
            response = client.post("/agents/code/execute", json={
                "code": "print('Hello World')",
                "language": "python"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert data["success"] == True
            assert "service_used" in data
            assert data["service_used"] == "CodeService"
    
    async def test_code_validate_syntax(self, client, mock_code_service):
        """Test code syntax validation endpoint."""
        with patch('services.api_gateway.routes.agents.code_agent.get_code_service', return_value=mock_code_service):
            response = client.post("/agents/code/validate", json={
                "code": "print('Hello World')",
                "language": "python"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert data["success"] == True
            assert "service_used" in data
            assert data["service_used"] == "CodeService"
    
    async def test_code_health_check(self, client, mock_code_service):
        """Test code service health check."""
        with patch('services.api_gateway.routes.agents.code_agent.get_code_service', return_value=mock_code_service):
            response = client.get("/agents/code/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"
            assert "service" in data
            assert data["service"] == "CodeService"

    # Database Service Tests
    async def test_database_service_injection(self, client, mock_database_service):
        """Test database service injection in route handler."""
        with patch('services.api_gateway.routes.agents.database_agent.get_database_service', return_value=mock_database_service):
            response = client.post("/agents/database/query", json={
                "query": "SELECT * FROM users",
                "database": "test_db"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert data["success"] == True
            assert "service_used" in data
            assert data["service_used"] == "DatabaseService"
    
    async def test_database_get_schema(self, client, mock_database_service):
        """Test database schema endpoint."""
        with patch('services.api_gateway.routes.agents.database_agent.get_database_service', return_value=mock_database_service):
            response = client.get("/agents/database/schema?database=test_db")
            
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert data["success"] == True
            assert "service_used" in data
            assert data["service_used"] == "DatabaseService"
    
    async def test_database_health_check(self, client, mock_database_service):
        """Test database service health check."""
        with patch('services.api_gateway.routes.agents.database_agent.get_database_service', return_value=mock_database_service):
            response = client.get("/agents/database/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"
            assert "service" in data
            assert data["service"] == "DatabaseService"

    # Crawler Service Tests
    async def test_crawler_service_injection(self, client, mock_crawler_service):
        """Test crawler service injection in route handler."""
        with patch('services.api_gateway.routes.agents.crawler_agent.get_crawler_service', return_value=mock_crawler_service):
            response = client.post("/agents/crawler/crawl", json={
                "url": "http://test.com",
                "max_pages": 10
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert data["success"] == True
            assert "service_used" in data
            assert data["service_used"] == "CrawlerService"
    
    async def test_crawler_extract_content(self, client, mock_crawler_service):
        """Test crawler content extraction endpoint."""
        with patch('services.api_gateway.routes.agents.crawler_agent.get_crawler_service', return_value=mock_crawler_service):
            response = client.post("/agents/crawler/extract", json={
                "url": "http://test.com",
                "extract_type": "content"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert data["success"] == True
            assert "service_used" in data
            assert data["service_used"] == "CrawlerService"
    
    async def test_crawler_health_check(self, client, mock_crawler_service):
        """Test crawler service health check."""
        with patch('services.api_gateway.routes.agents.crawler_agent.get_crawler_service', return_value=mock_crawler_service):
            response = client.get("/agents/crawler/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"
            assert "service" in data
            assert data["service"] == "CrawlerService"

    # Error Handling Tests
    async def test_service_error_handling(self, client, mock_browser_service):
        """Test service error handling and propagation."""
        # Mock service to raise an exception
        mock_browser_service.search_web = AsyncMock(side_effect=Exception("Service error"))
        
        with patch('services.api_gateway.routes.agents.browser_agent.get_browser_service', return_value=mock_browser_service):
            response = client.post("/agents/browser/search", json={
                "query": "test query",
                "search_engine": "google"
            })
            
            assert response.status_code == 500
            data = response.json()
            assert "success" in data
            assert data["success"] == False
            assert "error" in data
            assert "Service error" in data["error"]

    # Performance Tests
    async def test_service_response_time(self, client, mock_browser_service):
        """Test service response time performance."""
        with patch('services.api_gateway.routes.agents.browser_agent.get_browser_service', return_value=mock_browser_service):
            start_time = time.time()
            response = client.post("/agents/browser/search", json={
                "query": "performance test",
                "search_engine": "google"
            })
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 1.0  # Should respond within 1 second
            assert response_time > 0.0  # Should take some time

    # Backward Compatibility Tests
    async def test_backward_compatibility_response_format(self, client, mock_browser_service):
        """Test that response format maintains backward compatibility."""
        with patch('services.api_gateway.routes.agents.browser_agent.get_browser_service', return_value=mock_browser_service):
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

    async def test_error_response_format(self, client):
        """Test error response format consistency."""
        # Test with invalid request
        response = client.post("/agents/browser/search", json={
            "invalid": "request"
        })
        
        assert response.status_code == 400
        data = response.json()
        
        # Check error response format
        assert "success" in data
        assert data["success"] == False
        assert "error" in data
        assert "data" in data


class TestServiceLifecycle:
    """Test service lifecycle management."""
    
    async def test_service_initialization(self):
        """Test service initialization and setup."""
        # This would test service initialization
        # For now, we'll test that services can be created
        browser_service = BrowserService()
        assert browser_service is not None
        assert hasattr(browser_service, 'search_web')
    
    async def test_service_cleanup(self):
        """Test service cleanup and resource management."""
        # This would test service cleanup
        # For now, we'll test that services can be properly disposed
        browser_service = BrowserService()
        # In a real implementation, we would test cleanup methods
        assert browser_service is not None


class TestServiceHealthMonitoring:
    """Test service health monitoring."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    async def test_all_service_health_checks(self, client):
        """Test health checks for all services."""
        services = [
            ("browser", "/agents/browser/health"),
            ("pdf", "/agents/pdf/health"),
            ("knowledge", "/agents/knowledge/health"),
            ("code", "/agents/code/health"),
            ("database", "/agents/database/health"),
            ("crawler", "/agents/crawler/health")
        ]
        
        for service_name, health_endpoint in services:
            response = client.get(health_endpoint)
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] in ["healthy", "unhealthy"]


if __name__ == "__main__":
    pytest.main([__file__]) 