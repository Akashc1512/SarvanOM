"""
End-to-End Service Workflow Tests for Phase 2.3.3

This module tests complete service workflows and service interactions,
ensuring that the service integration works correctly in real-world scenarios.
"""

import pytest
import asyncio
import time
from typing import Dict, Any, List
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock

# Import the main application
from services.api_gateway.main import app


class TestServiceWorkflows:
    """Test complete service workflows and interactions."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_services(self):
        """Create comprehensive mock services for workflow testing."""
        # Browser Service
        browser_service = Mock()
        browser_service.search_web = AsyncMock(
            return_value={
                "success": True,
                "data": {
                    "results": [
                        {
                            "title": "Test Result 1",
                            "url": "http://test1.com",
                            "snippet": "Test snippet 1",
                        },
                        {
                            "title": "Test Result 2",
                            "url": "http://test2.com",
                            "snippet": "Test snippet 2",
                        },
                    ],
                    "total_results": 2,
                },
                "service_used": "BrowserService",
            }
        )
        browser_service.extract_content = AsyncMock(
            return_value={
                "success": True,
                "data": {"content": "Extracted content from webpage"},
                "service_used": "BrowserService",
            }
        )
        browser_service.browse_page = AsyncMock(
            return_value={
                "success": True,
                "data": {"page_content": "Full page content", "title": "Test Page"},
                "service_used": "BrowserService",
            }
        )
        browser_service.health_check = AsyncMock(
            return_value={"status": "healthy", "service": "BrowserService"}
        )

        # PDF Service
        pdf_service = Mock()
        pdf_service.process_pdf = AsyncMock(
            return_value={
                "success": True,
                "data": {
                    "text": "Extracted PDF text content",
                    "pages": 3,
                    "metadata": {"title": "Test PDF", "author": "Test Author"},
                },
                "service_used": "PDFService",
            }
        )
        pdf_service.extract_text = AsyncMock(
            return_value={
                "success": True,
                "data": {"text": "Extracted text from PDF"},
                "service_used": "PDFService",
            }
        )
        pdf_service.extract_images = AsyncMock(
            return_value={
                "success": True,
                "data": {"images": ["image1.png", "image2.png"]},
                "service_used": "PDFService",
            }
        )
        pdf_service.analyze_pdf = AsyncMock(
            return_value={
                "success": True,
                "data": {"analysis": "PDF analysis result", "complexity": "medium"},
                "service_used": "PDFService",
            }
        )
        pdf_service.health_check = AsyncMock(
            return_value={"status": "healthy", "service": "PDFService"}
        )

        # Knowledge Service
        knowledge_service = Mock()
        knowledge_service.query_entities = AsyncMock(
            return_value={
                "success": True,
                "data": {
                    "entities": [
                        {"id": "1", "name": "Entity 1", "type": "person"},
                        {"id": "2", "name": "Entity 2", "type": "organization"},
                    ]
                },
                "service_used": "KnowledgeService",
            }
        )
        knowledge_service.query_relationships = AsyncMock(
            return_value={
                "success": True,
                "data": {
                    "relationships": [
                        {"from": "1", "to": "2", "type": "WORKS_FOR"},
                        {"from": "2", "to": "3", "type": "LOCATED_IN"},
                    ]
                },
                "service_used": "KnowledgeService",
            }
        )
        knowledge_service.find_paths = AsyncMock(
            return_value={
                "success": True,
                "data": {"paths": [["1", "2", "3"], ["1", "4", "3"]]},
                "service_used": "KnowledgeService",
            }
        )
        knowledge_service.search_entities = AsyncMock(
            return_value={
                "success": True,
                "data": {"entities": [{"id": "1", "name": "Search Result"}]},
                "service_used": "KnowledgeService",
            }
        )
        knowledge_service.health_check = AsyncMock(
            return_value={"status": "healthy", "service": "KnowledgeService"}
        )

        # Code Service
        code_service = Mock()
        code_service.execute_code = AsyncMock(
            return_value={
                "success": True,
                "data": {
                    "output": "Hello World\n",
                    "execution_time": 0.05,
                    "memory_used": "2MB",
                },
                "service_used": "CodeService",
            }
        )
        code_service.validate_syntax = AsyncMock(
            return_value={
                "success": True,
                "data": {"valid": True, "errors": []},
                "service_used": "CodeService",
            }
        )
        code_service.analyze_code = AsyncMock(
            return_value={
                "success": True,
                "data": {"complexity": "low", "lines": 5, "functions": 1},
                "service_used": "CodeService",
            }
        )
        code_service.upload_and_execute = AsyncMock(
            return_value={
                "success": True,
                "data": {"result": "Code executed successfully"},
                "service_used": "CodeService",
            }
        )
        code_service.health_check = AsyncMock(
            return_value={"status": "healthy", "service": "CodeService"}
        )

        # Database Service
        database_service = Mock()
        database_service.execute_query = AsyncMock(
            return_value={
                "success": True,
                "data": {
                    "results": [
                        {"id": 1, "name": "User 1", "email": "user1@test.com"},
                        {"id": 2, "name": "User 2", "email": "user2@test.com"},
                    ],
                    "row_count": 2,
                },
                "service_used": "DatabaseService",
            }
        )
        database_service.get_schema = AsyncMock(
            return_value={
                "success": True,
                "data": {
                    "tables": ["users", "posts", "comments"],
                    "columns": {"users": ["id", "name", "email"]},
                },
                "service_used": "DatabaseService",
            }
        )
        database_service.analyze_data = AsyncMock(
            return_value={
                "success": True,
                "data": {
                    "analysis": "Data analysis result",
                    "insights": ["insight1", "insight2"],
                },
                "service_used": "DatabaseService",
            }
        )
        database_service.optimize_query = AsyncMock(
            return_value={
                "success": True,
                "data": {"optimized_query": "SELECT * FROM users WHERE id = 1"},
                "service_used": "DatabaseService",
            }
        )
        database_service.list_databases = AsyncMock(
            return_value={
                "success": True,
                "data": {"databases": ["test_db", "prod_db", "dev_db"]},
                "service_used": "DatabaseService",
            }
        )
        database_service.test_connection = AsyncMock(
            return_value={
                "success": True,
                "data": {"connected": True, "response_time": "0.1s"},
                "service_used": "DatabaseService",
            }
        )
        database_service.health_check = AsyncMock(
            return_value={"status": "healthy", "service": "DatabaseService"}
        )

        # Crawler Service
        crawler_service = Mock()
        crawler_service.crawl_website = AsyncMock(
            return_value={
                "success": True,
                "data": {"pages_crawled": 15, "links_found": 75, "crawl_time": "2.5s"},
                "service_used": "CrawlerService",
            }
        )
        crawler_service.extract_content = AsyncMock(
            return_value={
                "success": True,
                "data": {"content": "Extracted content from crawled page"},
                "service_used": "CrawlerService",
            }
        )
        crawler_service.discover_links = AsyncMock(
            return_value={
                "success": True,
                "data": {
                    "links": [
                        "http://link1.com",
                        "http://link2.com",
                        "http://link3.com",
                    ]
                },
                "service_used": "CrawlerService",
            }
        )
        crawler_service.generate_sitemap = AsyncMock(
            return_value={
                "success": True,
                "data": {"sitemap": "Generated sitemap XML"},
                "service_used": "CrawlerService",
            }
        )
        crawler_service.crawl_with_filters = AsyncMock(
            return_value={
                "success": True,
                "data": {"filtered_results": "Filtered crawl results"},
                "service_used": "CrawlerService",
            }
        )
        crawler_service.health_check = AsyncMock(
            return_value={"status": "healthy", "service": "CrawlerService"}
        )

        return {
            "browser": browser_service,
            "pdf": pdf_service,
            "knowledge": knowledge_service,
            "code": code_service,
            "database": database_service,
            "crawler": crawler_service,
        }

    async def test_complete_browser_workflow(self, client, mock_services):
        """Test complete browser service workflow."""
        services = mock_services

        with patch(
            "services.api_gateway.routes.agents.browser_agent.get_browser_service",
            return_value=services["browser"],
        ):
            # Step 1: Search for content
            search_response = client.post(
                "/agents/browser/search",
                json={
                    "query": "test search query",
                    "search_engine": "google",
                    "max_results": 5,
                },
            )

            assert search_response.status_code == 200
            search_data = search_response.json()
            assert search_data["success"] == True
            assert "results" in search_data["data"]

            # Step 2: Extract content from search results
            extract_response = client.post(
                "/agents/browser/extract",
                json={"url": "http://test1.com", "extract_type": "content"},
            )

            assert extract_response.status_code == 200
            extract_data = extract_response.json()
            assert extract_data["success"] == True
            assert "content" in extract_data["data"]

            # Step 3: Browse specific page
            browse_response = client.post(
                "/agents/browser/browse", json={"url": "http://test2.com"}
            )

            assert browse_response.status_code == 200
            browse_data = browse_response.json()
            assert browse_data["success"] == True
            assert "page_content" in browse_data["data"]

            # Step 4: Check service health
            health_response = client.get("/agents/browser/health")

            assert health_response.status_code == 200
            health_data = health_response.json()
            assert health_data["status"] == "healthy"

    async def test_complete_pdf_workflow(self, client, mock_services):
        """Test complete PDF service workflow."""
        services = mock_services

        with patch(
            "services.api_gateway.routes.agents.pdf_agent.get_pdf_service",
            return_value=services["pdf"],
        ):
            # Step 1: Process PDF file
            files = {"file": ("test.pdf", b"fake pdf content", "application/pdf")}
            process_response = client.post("/agents/pdf/process", files=files)

            assert process_response.status_code == 200
            process_data = process_response.json()
            assert process_data["success"] == True
            assert "text" in process_data["data"]

            # Step 2: Extract text from PDF
            extract_text_response = client.post("/agents/pdf/extract-text", files=files)

            assert extract_text_response.status_code == 200
            extract_text_data = extract_text_response.json()
            assert extract_text_data["success"] == True
            assert "text" in extract_text_data["data"]

            # Step 3: Extract images from PDF
            extract_images_response = client.post(
                "/agents/pdf/extract-images", files=files
            )

            assert extract_images_response.status_code == 200
            extract_images_data = extract_images_response.json()
            assert extract_images_data["success"] == True
            assert "images" in extract_images_data["data"]

            # Step 4: Analyze PDF
            analyze_response = client.post("/agents/pdf/analyze", files=files)

            assert analyze_response.status_code == 200
            analyze_data = analyze_response.json()
            assert analyze_data["success"] == True
            assert "analysis" in analyze_data["data"]

            # Step 5: Check service health
            health_response = client.get("/agents/pdf/health")

            assert health_response.status_code == 200
            health_data = health_response.json()
            assert health_data["status"] == "healthy"

    async def test_complete_knowledge_workflow(self, client, mock_services):
        """Test complete knowledge service workflow."""
        services = mock_services

        with patch(
            "services.api_gateway.routes.agents.knowledge_agent.get_knowledge_service",
            return_value=services["knowledge"],
        ):
            # Step 1: Query entities
            query_response = client.post(
                "/agents/knowledge/query",
                json={
                    "query": "test knowledge query",
                    "query_type": "entity_relationship",
                },
            )

            assert query_response.status_code == 200
            query_data = query_response.json()
            assert query_data["success"] == True
            assert "entities" in query_data["data"]

            # Step 2: Get relationships
            relationships_response = client.post(
                "/agents/knowledge/relationships", json={"entity_id": "1"}
            )

            assert relationships_response.status_code == 200
            relationships_data = relationships_response.json()
            assert relationships_data["success"] == True
            assert "relationships" in relationships_data["data"]

            # Step 3: Find paths between entities
            paths_response = client.post(
                "/agents/knowledge/paths", json={"from_entity": "1", "to_entity": "3"}
            )

            assert paths_response.status_code == 200
            paths_data = paths_response.json()
            assert paths_data["success"] == True
            assert "paths" in paths_data["data"]

            # Step 4: Search entities
            search_response = client.post(
                "/agents/knowledge/search", json={"search_term": "test entity"}
            )

            assert search_response.status_code == 200
            search_data = search_response.json()
            assert search_data["success"] == True
            assert "entities" in search_data["data"]

            # Step 5: Check service health
            health_response = client.get("/agents/knowledge/health")

            assert health_response.status_code == 200
            health_data = health_response.json()
            assert health_data["status"] == "healthy"

    async def test_complete_code_workflow(self, client, mock_services):
        """Test complete code service workflow."""
        services = mock_services

        with patch(
            "services.api_gateway.routes.agents.code_agent.get_code_service",
            return_value=services["code"],
        ):
            # Step 1: Execute code
            execute_response = client.post(
                "/agents/code/execute",
                json={"code": "print('Hello World')", "language": "python"},
            )

            assert execute_response.status_code == 200
            execute_data = execute_response.json()
            assert execute_data["success"] == True
            assert "output" in execute_data["data"]

            # Step 2: Validate syntax
            validate_response = client.post(
                "/agents/code/validate",
                json={"code": "print('Hello World')", "language": "python"},
            )

            assert validate_response.status_code == 200
            validate_data = validate_response.json()
            assert validate_data["success"] == True
            assert "valid" in validate_data["data"]

            # Step 3: Analyze code
            analyze_response = client.post(
                "/agents/code/analyze",
                json={"code": "print('Hello World')", "language": "python"},
            )

            assert analyze_response.status_code == 200
            analyze_data = analyze_response.json()
            assert analyze_data["success"] == True
            assert "complexity" in analyze_data["data"]

            # Step 4: Upload and execute
            upload_response = client.post(
                "/agents/code/upload-execute",
                json={"code": "print('Uploaded code')", "language": "python"},
            )

            assert upload_response.status_code == 200
            upload_data = upload_response.json()
            assert upload_data["success"] == True
            assert "result" in upload_data["data"]

            # Step 5: Check service health
            health_response = client.get("/agents/code/health")

            assert health_response.status_code == 200
            health_data = health_response.json()
            assert health_data["status"] == "healthy"

    async def test_complete_database_workflow(self, client, mock_services):
        """Test complete database service workflow."""
        services = mock_services

        with patch(
            "services.api_gateway.routes.agents.database_agent.get_database_service",
            return_value=services["database"],
        ):
            # Step 1: Test connection
            test_connection_response = client.post(
                "/agents/database/test-connection", json={"database": "test_db"}
            )

            assert test_connection_response.status_code == 200
            test_connection_data = test_connection_response.json()
            assert test_connection_data["success"] == True
            assert "connected" in test_connection_data["data"]

            # Step 2: Get schema
            schema_response = client.get("/agents/database/schema?database=test_db")

            assert schema_response.status_code == 200
            schema_data = schema_response.json()
            assert schema_data["success"] == True
            assert "tables" in schema_data["data"]

            # Step 3: Execute query
            query_response = client.post(
                "/agents/database/query",
                json={"query": "SELECT * FROM users", "database": "test_db"},
            )

            assert query_response.status_code == 200
            query_data = query_response.json()
            assert query_data["success"] == True
            assert "results" in query_data["data"]

            # Step 4: Analyze data
            analyze_response = client.post(
                "/agents/database/analyze",
                json={"database": "test_db", "table": "users"},
            )

            assert analyze_response.status_code == 200
            analyze_data = analyze_response.json()
            assert analyze_data["success"] == True
            assert "analysis" in analyze_data["data"]

            # Step 5: Optimize query
            optimize_response = client.post(
                "/agents/database/optimize",
                json={
                    "query": "SELECT * FROM users WHERE id = 1",
                    "database": "test_db",
                },
            )

            assert optimize_response.status_code == 200
            optimize_data = optimize_response.json()
            assert optimize_data["success"] == True
            assert "optimized_query" in optimize_data["data"]

            # Step 6: List databases
            list_response = client.get("/agents/database/list")

            assert list_response.status_code == 200
            list_data = list_response.json()
            assert list_data["success"] == True
            assert "databases" in list_data["data"]

            # Step 7: Check service health
            health_response = client.get("/agents/database/health")

            assert health_response.status_code == 200
            health_data = health_response.json()
            assert health_data["status"] == "healthy"

    async def test_complete_crawler_workflow(self, client, mock_services):
        """Test complete crawler service workflow."""
        services = mock_services

        with patch(
            "services.api_gateway.routes.agents.crawler_agent.get_crawler_service",
            return_value=services["crawler"],
        ):
            # Step 1: Crawl website
            crawl_response = client.post(
                "/agents/crawler/crawl",
                json={"url": "http://test.com", "max_pages": 10},
            )

            assert crawl_response.status_code == 200
            crawl_data = crawl_response.json()
            assert crawl_data["success"] == True
            assert "pages_crawled" in crawl_data["data"]

            # Step 2: Extract content
            extract_response = client.post(
                "/agents/crawler/extract",
                json={"url": "http://test.com", "extract_type": "content"},
            )

            assert extract_response.status_code == 200
            extract_data = extract_response.json()
            assert extract_data["success"] == True
            assert "content" in extract_data["data"]

            # Step 3: Discover links
            discover_response = client.post(
                "/agents/crawler/discover", json={"url": "http://test.com"}
            )

            assert discover_response.status_code == 200
            discover_data = discover_response.json()
            assert discover_data["success"] == True
            assert "links" in discover_data["data"]

            # Step 4: Generate sitemap
            sitemap_response = client.post(
                "/agents/crawler/sitemap", json={"url": "http://test.com"}
            )

            assert sitemap_response.status_code == 200
            sitemap_data = sitemap_response.json()
            assert sitemap_data["success"] == True
            assert "sitemap" in sitemap_data["data"]

            # Step 5: Crawl with filters
            filtered_response = client.post(
                "/agents/crawler/crawl-filtered",
                json={
                    "url": "http://test.com",
                    "filters": {"content_type": "text/html"},
                },
            )

            assert filtered_response.status_code == 200
            filtered_data = filtered_response.json()
            assert filtered_data["success"] == True
            assert "filtered_results" in filtered_data["data"]

            # Step 6: Check service health
            health_response = client.get("/agents/crawler/health")

            assert health_response.status_code == 200
            health_data = health_response.json()
            assert health_data["status"] == "healthy"

    async def test_cross_service_interaction(self, client, mock_services):
        """Test interaction between different services."""
        services = mock_services

        # Test workflow that involves multiple services
        with (
            patch(
                "services.api_gateway.routes.agents.browser_agent.get_browser_service",
                return_value=services["browser"],
            ),
            patch(
                "services.api_gateway.routes.agents.pdf_agent.get_pdf_service",
                return_value=services["pdf"],
            ),
            patch(
                "services.api_gateway.routes.agents.knowledge_agent.get_knowledge_service",
                return_value=services["knowledge"],
            ),
        ):

            # Step 1: Search for PDF documents
            search_response = client.post(
                "/agents/browser/search",
                json={"query": "PDF documents", "search_engine": "google"},
            )

            assert search_response.status_code == 200
            search_data = search_response.json()
            assert search_data["success"] == True

            # Step 2: Process a PDF from search results
            files = {"file": ("document.pdf", b"fake pdf content", "application/pdf")}
            pdf_response = client.post("/agents/pdf/process", files=files)

            assert pdf_response.status_code == 200
            pdf_data = pdf_response.json()
            assert pdf_data["success"] == True

            # Step 3: Query knowledge graph about extracted content
            knowledge_response = client.post(
                "/agents/knowledge/query",
                json={
                    "query": "extracted content analysis",
                    "query_type": "entity_relationship",
                },
            )

            assert knowledge_response.status_code == 200
            knowledge_data = knowledge_response.json()
            assert knowledge_data["success"] == True

    async def test_error_propagation_across_services(self, client, mock_services):
        """Test error propagation across service interactions."""
        services = mock_services

        # Mock service to return errors
        services["browser"].search_web = AsyncMock(
            side_effect=Exception("Browser service error")
        )
        services["pdf"].process_pdf = AsyncMock(
            side_effect=Exception("PDF service error")
        )

        with (
            patch(
                "services.api_gateway.routes.agents.browser_agent.get_browser_service",
                return_value=services["browser"],
            ),
            patch(
                "services.api_gateway.routes.agents.pdf_agent.get_pdf_service",
                return_value=services["pdf"],
            ),
        ):

            # Test browser service error
            browser_response = client.post(
                "/agents/browser/search",
                json={"query": "test query", "search_engine": "google"},
            )

            assert browser_response.status_code == 500
            browser_data = browser_response.json()
            assert browser_data["success"] == False
            assert "error" in browser_data

            # Test PDF service error
            files = {"file": ("test.pdf", b"fake content", "application/pdf")}
            pdf_response = client.post("/agents/pdf/process", files=files)

            assert pdf_response.status_code == 500
            pdf_data = pdf_response.json()
            assert pdf_data["success"] == False
            assert "error" in pdf_data

    async def test_service_health_monitoring_workflow(self, client, mock_services):
        """Test comprehensive health monitoring workflow."""
        services = mock_services

        # Test health checks for all services
        health_endpoints = [
            "/agents/browser/health",
            "/agents/pdf/health",
            "/agents/knowledge/health",
            "/agents/code/health",
            "/agents/database/health",
            "/agents/crawler/health",
        ]

        health_results = {}

        for endpoint in health_endpoints:
            service_name = endpoint.split("/")[2]
            with patch(
                f"services.api_gateway.routes.agents.{service_name}_agent.get_{service_name}_service",
                return_value=services[service_name],
            ):
                response = client.get(endpoint)

                assert response.status_code == 200
                data = response.json()
                health_results[service_name] = data["status"]

        # All services should be healthy
        for service_name, status in health_results.items():
            assert (
                status == "healthy"
            ), f"Service {service_name} is not healthy: {status}"


if __name__ == "__main__":
    pytest.main([__file__])
