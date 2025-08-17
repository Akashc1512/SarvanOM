"""
Unit tests for health, readiness, and version endpoints

This module tests the standardized health/readiness endpoints:
- /health (liveness probe)
- /ready (readiness probe with dependency checks)
- /version (version information with git SHA and build time)
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timezone
import json
import os

# Import the app
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.gateway.main import app, startup_time

# Test client
client = TestClient(app)


class TestHealthEndpoint:
    """Test cases for /health endpoint (liveness probe)"""
    
    def test_health_endpoint_returns_200(self):
        """Test that /health returns 200 status code"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_response_structure(self):
        """Test that /health returns correct response structure"""
        response = client.get("/health")
        data = response.json()
        
        # Check required fields
        assert "status" in data
        assert "timestamp" in data
        assert "uptime_s" in data
        assert "version" in data
        assert "git_sha" in data
        assert "build_time" in data
        
        # Check data types
        assert isinstance(data["status"], str)
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["uptime_s"], (int, float))
        assert isinstance(data["version"], str)
        assert data["git_sha"] is None or isinstance(data["git_sha"], str)
        assert data["build_time"] is None or isinstance(data["build_time"], str)
    
    def test_health_status_is_healthy(self):
        """Test that health status is 'healthy'"""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_health_uptime_is_positive(self):
        """Test that uptime is a positive number"""
        response = client.get("/health")
        data = response.json()
        assert data["uptime_s"] > 0
    
    def test_health_version_is_correct(self):
        """Test that version is correct"""
        response = client.get("/health")
        data = response.json()
        assert data["version"] == "1.0.0"
    
    def test_health_has_trace_id_header(self):
        """Test that response includes X-Trace-ID header"""
        response = client.get("/health")
        assert "X-Trace-ID" in response.headers
        assert response.headers["X-Trace-ID"] is not None
    
    def test_health_trace_id_is_uuid(self):
        """Test that trace ID is a valid UUID format"""
        response = client.get("/health")
        trace_id = response.headers["X-Trace-ID"]
        # UUID format: 8-4-4-4-12 characters
        assert len(trace_id) == 36
        assert trace_id.count("-") == 4


class TestReadyEndpoint:
    """Test cases for /ready endpoint (readiness probe)"""
    
    @patch('services.gateway.main.check_crud_service')
    @patch('services.gateway.main.check_retrieval_service')
    @patch('services.gateway.main.check_synthesis_service')
    @patch('services.gateway.main.check_vector_store')
    @patch('services.gateway.main.check_cache_redis')
    def test_ready_endpoint_returns_200_when_all_healthy(
        self, mock_cache, mock_vector, mock_synthesis, mock_retrieval, mock_crud
    ):
        """Test that /ready returns 200 when all dependencies are healthy"""
        # Mock all dependencies as healthy
        from services.gateway.main import DependencyStatus
        
        mock_crud.return_value = DependencyStatus(
            name="crud_service",
            status="healthy",
            response_time_ms=50,
            error_message=None,
            last_check=datetime.now(timezone.utc).isoformat()
        )
        mock_retrieval.return_value = DependencyStatus(
            name="retrieval_service",
            status="healthy",
            response_time_ms=100,
            error_message=None,
            last_check=datetime.now(timezone.utc).isoformat()
        )
        mock_synthesis.return_value = DependencyStatus(
            name="synthesis_service",
            status="healthy",
            response_time_ms=75,
            error_message=None,
            last_check=datetime.now(timezone.utc).isoformat()
        )
        mock_vector.return_value = DependencyStatus(
            name="vector_store",
            status="healthy",
            response_time_ms=25,
            error_message=None,
            last_check=datetime.now(timezone.utc).isoformat()
        )
        mock_cache.return_value = DependencyStatus(
            name="cache_redis",
            status="healthy",
            response_time_ms=10,
            error_message=None,
            last_check=datetime.now(timezone.utc).isoformat()
        )
        
        response = client.get("/ready")
        assert response.status_code == 200
    
    @patch('services.gateway.main.check_crud_service')
    @patch('services.gateway.main.check_retrieval_service')
    @patch('services.gateway.main.check_synthesis_service')
    @patch('services.gateway.main.check_vector_store')
    @patch('services.gateway.main.check_cache_redis')
    def test_ready_response_structure_when_healthy(
        self, mock_cache, mock_vector, mock_synthesis, mock_retrieval, mock_crud
    ):
        """Test that /ready returns correct response structure when healthy"""
        # Mock all dependencies as healthy
        from services.gateway.main import DependencyStatus
        
        for mock_func in [mock_crud, mock_retrieval, mock_synthesis, mock_vector, mock_cache]:
            mock_func.return_value = DependencyStatus(
                name="test_service",
                status="healthy",
                response_time_ms=50,
                error_message=None,
                last_check=datetime.now(timezone.utc).isoformat()
            )
        
        response = client.get("/ready")
        data = response.json()
        
        # Check required fields
        assert "status" in data
        assert "timestamp" in data
        assert "uptime_s" in data
        assert "dependencies" in data
        assert "error_count" in data
        
        # Check data types
        assert isinstance(data["status"], str)
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["uptime_s"], (int, float))
        assert isinstance(data["dependencies"], list)
        assert isinstance(data["error_count"], int)
        
        # Check status when all healthy
        assert data["status"] == "ready"
        assert data["error_count"] == 0
        assert len(data["dependencies"]) == 5  # 5 dependencies
    
    @patch('services.gateway.main.check_crud_service')
    @patch('services.gateway.main.check_retrieval_service')
    @patch('services.gateway.main.check_synthesis_service')
    @patch('services.gateway.main.check_vector_store')
    @patch('services.gateway.main.check_cache_redis')
    def test_ready_status_not_ready_when_dependency_unhealthy(
        self, mock_cache, mock_vector, mock_synthesis, mock_retrieval, mock_crud
    ):
        """Test that /ready returns 'not_ready' when a dependency is unhealthy"""
        # Mock CRUD service as unhealthy
        from services.gateway.main import DependencyStatus
        
        mock_crud.return_value = DependencyStatus(
            name="crud_service",
            status="unhealthy",
            response_time_ms=5000,
            error_message="Connection timeout",
            last_check=datetime.now(timezone.utc).isoformat()
        )
        
        # Mock other dependencies as healthy
        for mock_func in [mock_retrieval, mock_synthesis, mock_vector, mock_cache]:
            mock_func.return_value = DependencyStatus(
                name="test_service",
                status="healthy",
                response_time_ms=50,
                error_message=None,
                last_check=datetime.now(timezone.utc).isoformat()
            )
        
        response = client.get("/ready")
        data = response.json()
        
        assert data["status"] == "not_ready"
        assert data["error_count"] == 1
    
    @patch('services.gateway.main.check_crud_service')
    def test_ready_handles_dependency_exception(self, mock_crud):
        """Test that /ready handles exceptions in dependency checks"""
        # Mock dependency to raise an exception
        mock_crud.side_effect = Exception("Connection failed")
        
        response = client.get("/ready")
        data = response.json()
        
        assert data["status"] == "not_ready"
        assert data["error_count"] >= 1
    
    def test_ready_has_trace_id_header(self):
        """Test that /ready response includes X-Trace-ID header"""
        response = client.get("/ready")
        assert "X-Trace-ID" in response.headers
        assert response.headers["X-Trace-ID"] is not None


class TestVersionEndpoint:
    """Test cases for /version endpoint"""
    
    def test_version_endpoint_returns_200(self):
        """Test that /version returns 200 status code"""
        response = client.get("/version")
        assert response.status_code == 200
    
    def test_version_response_structure(self):
        """Test that /version returns correct response structure"""
        response = client.get("/version")
        data = response.json()
        
        # Check required fields
        assert "version" in data
        assert "git_sha" in data
        assert "build_time" in data
        assert "environment" in data
        assert "timestamp" in data
        
        # Check data types
        assert isinstance(data["version"], str)
        assert data["git_sha"] is None or isinstance(data["git_sha"], str)
        assert data["build_time"] is None or isinstance(data["build_time"], str)
        assert isinstance(data["environment"], str)
        assert isinstance(data["timestamp"], str)
    
    def test_version_is_correct(self):
        """Test that version is correct"""
        response = client.get("/version")
        data = response.json()
        assert data["version"] == "1.0.0"
    
    def test_environment_defaults_to_development(self):
        """Test that environment defaults to 'development'"""
        response = client.get("/version")
        data = response.json()
        assert data["environment"] == "development"
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'production'})
    def test_environment_from_env_variable(self):
        """Test that environment is read from ENVIRONMENT env var"""
        response = client.get("/version")
        data = response.json()
        assert data["environment"] == "production"
    
    def test_version_has_trace_id_header(self):
        """Test that /version response includes X-Trace-ID header"""
        response = client.get("/version")
        assert "X-Trace-ID" in response.headers
        assert response.headers["X-Trace-ID"] is not None


class TestGitIntegration:
    """Test cases for git SHA and build time functionality"""
    
    @patch('subprocess.run')
    def test_get_git_sha_success(self, mock_run):
        """Test successful git SHA retrieval"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="abc123def456\n"
        )
        
        from services.gateway.main import get_git_sha
        result = get_git_sha()
        assert result == "abc123def456"
    
    @patch('subprocess.run')
    def test_get_git_sha_failure(self, mock_run):
        """Test git SHA retrieval failure"""
        mock_run.side_effect = FileNotFoundError()
        
        from services.gateway.main import get_git_sha
        result = get_git_sha()
        assert result is None
    
    @patch('subprocess.run')
    def test_get_build_time_from_env(self, mock_run):
        """Test build time retrieval from environment variable"""
        with patch.dict(os.environ, {'BUILD_TIME': '2025-08-17T10:00:00Z'}):
            from services.gateway.main import get_build_time
            result = get_build_time()
            assert result == "2025-08-17T10:00:00Z"
    
    @patch('subprocess.run')
    def test_get_build_time_from_git(self, mock_run):
        """Test build time retrieval from git"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="2025-08-17 10:00:00 +0000\n"
        )
        
        with patch.dict(os.environ, {}, clear=True):
            from services.gateway.main import get_build_time
            result = get_build_time()
            assert result == "2025-08-17 10:00:00 +0000"


class TestDependencyChecks:
    """Test cases for individual dependency check functions"""
    
    @patch('httpx.AsyncClient')
    async def test_check_crud_service_healthy(self, mock_client):
        """Test CRUD service health check when healthy"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        from services.gateway.main import check_crud_service
        result = await check_crud_service()
        
        assert result.name == "crud_service"
        assert result.status == "healthy"
        assert result.response_time_ms >= 0  # Can be 0 for very fast responses
        assert result.error_message is None
    
    @patch('httpx.AsyncClient')
    async def test_check_crud_service_unhealthy(self, mock_client):
        """Test CRUD service health check when unhealthy"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        from services.gateway.main import check_crud_service
        result = await check_crud_service()
        
        assert result.name == "crud_service"
        assert result.status == "unhealthy"
        assert result.error_message == "HTTP 500"
    
    @patch('httpx.AsyncClient')
    async def test_check_crud_service_connection_error(self, mock_client):
        """Test CRUD service health check with connection error"""
        mock_client.side_effect = Exception("Connection failed")
        
        from services.gateway.main import check_crud_service
        result = await check_crud_service()
        
        assert result.name == "crud_service"
        assert result.status == "unhealthy"
        assert "Connection failed" in result.error_message


class TestIntegration:
    """Integration tests for health endpoints"""
    
    def test_all_health_endpoints_accessible(self):
        """Test that all health endpoints are accessible"""
        endpoints = ["/health", "/ready", "/version"]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Endpoint {endpoint} returned {response.status_code}"
    
    def test_health_endpoints_have_consistent_structure(self):
        """Test that all health endpoints have consistent response structure"""
        endpoints = ["/health", "/ready", "/version"]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            data = response.json()
            
            # All should have timestamp
            assert "timestamp" in data
            
            # All should have trace ID header
            assert "X-Trace-ID" in response.headers
    
    def test_health_endpoints_are_fast(self):
        """Test that health endpoints respond quickly"""
        import time
        
        endpoints = ["/health", "/ready", "/version"]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response_time < 5.0, f"Endpoint {endpoint} took {response_time:.2f}s"


if __name__ == "__main__":
    pytest.main([__file__])
