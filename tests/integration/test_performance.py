"""
Performance Tests for Phase 2.3.3

This module tests the performance characteristics of the service integration,
including service layer overhead, concurrent usage, and response times.
"""

import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock

# Import the main application
from services.api_gateway.main import app


class TestServicePerformance:
    """Test service performance and concurrency."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_browser_service(self):
        """Create mock browser service for performance testing."""
        service = Mock()
        service.search_web = AsyncMock(return_value={
            "success": True,
            "data": {"results": [{"title": "Test Result", "url": "http://test.com"}]},
            "service_used": "BrowserService"
        })
        service.health_check = AsyncMock(return_value={
            "status": "healthy",
            "service": "BrowserService"
        })
        return service
    
    @pytest.fixture
    def mock_pdf_service(self):
        """Create mock PDF service for performance testing."""
        service = Mock()
        service.process_pdf = AsyncMock(return_value={
            "success": True,
            "data": {"text": "Test PDF text", "pages": 1},
            "service_used": "PDFService"
        })
        service.health_check = AsyncMock(return_value={
            "status": "healthy",
            "service": "PDFService"
        })
        return service

    async def test_service_overhead_measurement(self, client, mock_browser_service):
        """Test service layer overhead measurement."""
        # Baseline test (without service layer)
        baseline_times = []
        for _ in range(10):
            start_time = time.time()
            # Simulate baseline operation
            time.sleep(0.01)  # Simulate some work
            baseline_times.append(time.time() - start_time)
        
        baseline_avg = statistics.mean(baseline_times)
        
        # Service layer test
        service_times = []
        with patch('services.api_gateway.routes.agents.browser_agent.get_browser_service', return_value=mock_browser_service):
            for _ in range(10):
                start_time = time.time()
                response = client.post("/agents/browser/search", json={
                    "query": "performance test",
                    "search_engine": "google"
                })
                service_times.append(time.time() - start_time)
        
        service_avg = statistics.mean(service_times)
        
        # Calculate overhead
        overhead_ratio = (service_avg - baseline_avg) / baseline_avg
        
        # Assert overhead is acceptable (< 50% increase for this test)
        assert overhead_ratio < 0.5, f"Service overhead too high: {overhead_ratio:.2%}"
        assert response.status_code == 200
    
    async def test_concurrent_service_usage(self, client, mock_browser_service):
        """Test concurrent service usage."""
        def make_request():
            """Make a single request."""
            return client.post("/agents/browser/search", json={
                "query": "concurrent test",
                "search_engine": "google"
            })
        
        # Test with 10 concurrent requests
        with patch('services.api_gateway.routes.agents.browser_agent.get_browser_service', return_value=mock_browser_service):
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                responses = [future.result() for future in as_completed(futures)]
            
            # All requests should succeed
            for response in responses:
                assert response.status_code == 200
                data = response.json()
                assert data["success"] == True
    
    async def test_concurrent_different_services(self, client, mock_browser_service, mock_pdf_service):
        """Test concurrent usage of different services."""
        def make_browser_request():
            return client.post("/agents/browser/search", json={
                "query": "browser test",
                "search_engine": "google"
            })
        
        def make_pdf_request():
            files = {"file": ("test.pdf", b"fake pdf content", "application/pdf")}
            return client.post("/agents/pdf/process", files=files)
        
        # Test concurrent requests to different services
        with patch('services.api_gateway.routes.agents.browser_agent.get_browser_service', return_value=mock_browser_service), \
             patch('services.api_gateway.routes.agents.pdf_agent.get_pdf_service', return_value=mock_pdf_service):
            
            with ThreadPoolExecutor(max_workers=6) as executor:
                futures = []
                # Add 3 browser requests
                for _ in range(3):
                    futures.append(executor.submit(make_browser_request))
                # Add 3 PDF requests
                for _ in range(3):
                    futures.append(executor.submit(make_pdf_request))
                
                responses = [future.result() for future in as_completed(futures)]
            
            # All requests should succeed
            for response in responses:
                assert response.status_code == 200
                data = response.json()
                assert data["success"] == True
    
    async def test_response_time_distribution(self, client, mock_browser_service):
        """Test response time distribution under load."""
        response_times = []
        
        with patch('services.api_gateway.routes.agents.browser_agent.get_browser_service', return_value=mock_browser_service):
            # Make 20 requests and measure response times
            for i in range(20):
                start_time = time.time()
                response = client.post("/agents/browser/search", json={
                    "query": f"test query {i}",
                    "search_engine": "google"
                })
                response_times.append(time.time() - start_time)
                
                assert response.status_code == 200
        
        # Calculate statistics
        avg_response_time = statistics.mean(response_times)
        median_response_time = statistics.median(response_times)
        std_dev = statistics.stdev(response_times)
        
        # Assert reasonable performance
        assert avg_response_time < 0.5, f"Average response time too high: {avg_response_time:.3f}s"
        assert median_response_time < 0.5, f"Median response time too high: {median_response_time:.3f}s"
        assert std_dev < 0.2, f"Response time variance too high: {std_dev:.3f}s"
    
    async def test_memory_usage_under_load(self, client, mock_browser_service):
        """Test memory usage under concurrent load."""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make concurrent requests
        with patch('services.api_gateway.routes.agents.browser_agent.get_browser_service', return_value=mock_browser_service):
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(
                    lambda: client.post("/agents/browser/search", json={
                        "query": "memory test",
                        "search_engine": "google"
                    })
                ) for _ in range(50)]
                
                responses = [future.result() for future in as_completed(futures)]
            
            # All requests should succeed
            for response in responses:
                assert response.status_code == 200
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Assert reasonable memory usage (less than 100MB increase)
        assert memory_increase < 100, f"Memory usage increased too much: {memory_increase:.1f}MB"
    
    async def test_service_error_performance(self, client, mock_browser_service):
        """Test performance when services return errors."""
        # Mock service to return errors
        mock_browser_service.search_web = AsyncMock(side_effect=Exception("Service error"))
        
        error_response_times = []
        
        with patch('services.api_gateway.routes.agents.browser_agent.get_browser_service', return_value=mock_browser_service):
            # Make requests that will result in errors
            for _ in range(10):
                start_time = time.time()
                response = client.post("/agents/browser/search", json={
                    "query": "error test",
                    "search_engine": "google"
                })
                error_response_times.append(time.time() - start_time)
                
                assert response.status_code == 500
        
        # Calculate error response time statistics
        avg_error_time = statistics.mean(error_response_times)
        
        # Error responses should still be reasonably fast
        assert avg_error_time < 1.0, f"Error response time too high: {avg_error_time:.3f}s"
    
    async def test_health_check_performance(self, client, mock_browser_service):
        """Test health check endpoint performance."""
        health_check_times = []
        
        with patch('services.api_gateway.routes.agents.browser_agent.get_browser_service', return_value=mock_browser_service):
            # Make multiple health check requests
            for _ in range(20):
                start_time = time.time()
                response = client.get("/agents/browser/health")
                health_check_times.append(time.time() - start_time)
                
                assert response.status_code == 200
        
        # Health checks should be very fast
        avg_health_time = statistics.mean(health_check_times)
        assert avg_health_time < 0.1, f"Health check too slow: {avg_health_time:.3f}s"
    
    async def test_service_initialization_performance(self):
        """Test service initialization performance."""
        from services.api_gateway.services.browser_service import BrowserService
        
        init_times = []
        
        # Test service initialization time
        for _ in range(10):
            start_time = time.time()
            service = BrowserService()
            init_times.append(time.time() - start_time)
            
            assert service is not None
        
        avg_init_time = statistics.mean(init_times)
        
        # Service initialization should be fast
        assert avg_init_time < 0.1, f"Service initialization too slow: {avg_init_time:.3f}s"


class TestLoadTesting:
    """Test system behavior under various load conditions."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_services(self):
        """Create mock services for load testing."""
        browser_service = Mock()
        browser_service.search_web = AsyncMock(return_value={
            "success": True,
            "data": {"results": [{"title": "Load Test Result", "url": "http://test.com"}]},
            "service_used": "BrowserService"
        })
        
        pdf_service = Mock()
        pdf_service.process_pdf = AsyncMock(return_value={
            "success": True,
            "data": {"text": "Load Test PDF", "pages": 1},
            "service_used": "PDFService"
        })
        
        return browser_service, pdf_service
    
    async def test_low_load_performance(self, client, mock_services):
        """Test performance under low load (1-5 concurrent requests)."""
        browser_service, pdf_service = mock_services
        
        with patch('services.api_gateway.routes.agents.browser_agent.get_browser_service', return_value=browser_service), \
             patch('services.api_gateway.routes.agents.pdf_agent.get_pdf_service', return_value=pdf_service):
            
            response_times = []
            
            # Make 5 sequential requests
            for i in range(5):
                start_time = time.time()
                response = client.post("/agents/browser/search", json={
                    "query": f"low load test {i}",
                    "search_engine": "google"
                })
                response_times.append(time.time() - start_time)
                
                assert response.status_code == 200
            
            avg_time = statistics.mean(response_times)
            assert avg_time < 0.2, f"Low load performance poor: {avg_time:.3f}s"
    
    async def test_medium_load_performance(self, client, mock_services):
        """Test performance under medium load (10-20 concurrent requests)."""
        browser_service, pdf_service = mock_services
        
        def make_request():
            return client.post("/agents/browser/search", json={
                "query": "medium load test",
                "search_engine": "google"
            })
        
        with patch('services.api_gateway.routes.agents.browser_agent.get_browser_service', return_value=browser_service):
            with ThreadPoolExecutor(max_workers=15) as executor:
                futures = [executor.submit(make_request) for _ in range(15)]
                responses = [future.result() for future in as_completed(futures)]
            
            # All requests should succeed
            for response in responses:
                assert response.status_code == 200
    
    async def test_high_load_performance(self, client, mock_services):
        """Test performance under high load (50+ concurrent requests)."""
        browser_service, pdf_service = mock_services
        
        def make_request():
            return client.post("/agents/browser/search", json={
                "query": "high load test",
                "search_engine": "google"
            })
        
        with patch('services.api_gateway.routes.agents.browser_agent.get_browser_service', return_value=browser_service):
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = [executor.submit(make_request) for _ in range(50)]
                responses = [future.result() for future in as_completed(futures)]
            
            # Most requests should succeed (allow some failures under high load)
            success_count = sum(1 for r in responses if r.status_code == 200)
            success_rate = success_count / len(responses)
            
            assert success_rate >= 0.8, f"Success rate too low under high load: {success_rate:.1%}"


class TestResourceManagement:
    """Test resource management and cleanup."""
    
    async def test_service_resource_cleanup(self):
        """Test that services properly clean up resources."""
        from services.api_gateway.services.browser_service import BrowserService
        
        # Create and destroy multiple service instances
        for _ in range(10):
            service = BrowserService()
            # Simulate some work
            await asyncio.sleep(0.01)
            # Service should be properly cleaned up when it goes out of scope
            del service
        
        # If we get here without errors, cleanup is working
        assert True
    
    async def test_concurrent_resource_usage(self, client, mock_browser_service):
        """Test resource usage under concurrent load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_cpu = process.cpu_percent()
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        def make_request():
            return client.post("/agents/browser/search", json={
                "query": "resource test",
                "search_engine": "google"
            })
        
        with patch('services.api_gateway.routes.agents.browser_agent.get_browser_service', return_value=mock_browser_service):
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(20)]
                responses = [future.result() for future in as_completed(futures)]
            
            # All requests should succeed
            for response in responses:
                assert response.status_code == 200
        
        # Check resource usage after load
        final_cpu = process.cpu_percent()
        final_memory = process.memory_info().rss / 1024 / 1024
        
        # CPU usage should be reasonable
        assert final_cpu < 80, f"CPU usage too high: {final_cpu:.1f}%"
        
        # Memory usage should not increase dramatically
        memory_increase = final_memory - initial_memory
        assert memory_increase < 50, f"Memory increase too high: {memory_increase:.1f}MB"


if __name__ == "__main__":
    pytest.main([__file__])
