"""
Comprehensive API Endpoint Tests - MAANG Standards

This module provides comprehensive unit tests for all API endpoints,
ensuring proper functionality, error handling, and security compliance.

Test Coverage:
    - Authentication endpoints
    - Query processing endpoints
    - User management endpoints
    - Analytics endpoints
    - WebSocket endpoints
    - Expert review endpoints
    - Task generation endpoints
    - Error handling scenarios
    - Rate limiting validation
    - Security compliance

Authors:
    - Universal Knowledge Platform Engineering Team
    
Version:
    2.0.0 (2024-12-28)
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta

from fastapi.testclient import TestClient
from fastapi import HTTPException, status

# Import the main application
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'services', 'api-gateway'))
from services.api-gateway.main import app
from shared.models.models import User, Role, APIKey, Query, AuditLog

class TestAuthenticationEndpoints:
    """Test authentication-related endpoints."""
    
    @pytest.fixture
    def client(self):
        """Get test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing."""
        return {
            "username": "testuser",
            "password": "securepassword123",
            "email": "test@example.com"
        }
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "uptime" in data
    
    @patch('services.api_gateway.main.login_user')
    def test_login_success(self, mock_login, client, sample_user_data):
        """Test successful login."""
        mock_login.return_value = {
            "access_token": "test_token",
            "token_type": "bearer",
            "api_key": "test_api_key",
            "user_id": "test_user_id",
            "role": "user",
            "permissions": ["read", "write"]
        }
        
        response = client.post("/auth/login", json=sample_user_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "api_key" in data
        assert "user_id" in data
    
    @patch('services.api_gateway.main.login_user')
    def test_login_invalid_credentials(self, mock_login, client):
        """Test login with invalid credentials."""
        mock_login.side_effect = HTTPException(status_code=401, detail="Invalid credentials")
        
        response = client.post("/auth/login", json={
            "username": "wronguser",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    @patch('services.api_gateway.main.register_user')
    def test_register_success(self, mock_register, client, sample_user_data):
        """Test successful user registration."""
        mock_register.return_value = {
            "access_token": "test_token",
            "token_type": "bearer",
            "api_key": "test_api_key",
            "user_id": "test_user_id",
            "role": "user",
            "permissions": ["read"]
        }
        
        response = client.post("/auth/register", json=sample_user_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user_id" in data
    
    @patch('services.api_gateway.main.register_user')
    def test_register_existing_user(self, mock_register, client, sample_user_data):
        """Test registration with existing username."""
        mock_register.side_effect = HTTPException(status_code=409, detail="Username already exists")
        
        response = client.post("/auth/register", json=sample_user_data)
        assert response.status_code == 409
        assert "Username already exists" in response.json()["detail"]
    
    @patch('services.api_gateway.main.generate_api_key')
    def test_create_api_key(self, mock_generate, client):
        """Test API key creation."""
        mock_generate.return_value = {
            "api_key": "test_api_key_123",
            "user_id": "test_user_id",
            "role": "user",
            "permissions": ["read", "write"],
            "description": "Test API Key",
            "created_at": datetime.now().isoformat()
        }
        
        # Mock authentication
        with patch('services.api_gateway.main.get_current_user') as mock_auth:
            mock_auth.return_value = {"user_id": "test_user_id", "role": "user"}
            
            response = client.post("/auth/api-key")
            assert response.status_code == 200
            data = response.json()
            assert "api_key" in data
            assert "user_id" in data
    
    @patch('services.api_gateway.main.revoke_api_key')
    def test_revoke_api_key(self, mock_revoke, client):
        """Test API key revocation."""
        mock_revoke.return_value = {"message": "API key revoked successfully"}
        
        # Mock authentication
        with patch('services.api_gateway.main.get_current_user') as mock_auth:
            mock_auth.return_value = {"user_id": "test_user_id", "role": "user"}
            
            response = client.delete("/auth/api-key/test_key_123")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
    
    @patch('services.api_gateway.main.get_user_api_keys')
    def test_list_api_keys(self, mock_list, client):
        """Test listing user API keys."""
        mock_list.return_value = [
            {
                "api_key": "test_key_1",
                "user_id": "test_user_id",
                "role": "user",
                "permissions": ["read"],
                "description": "Test Key 1",
                "created_at": datetime.now().isoformat()
            }
        ]
        
        # Mock authentication
        with patch('services.api_gateway.main.get_current_user') as mock_auth:
            mock_auth.return_value = {"user_id": "test_user_id", "role": "user"}
            
            response = client.get("/auth/api-keys")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0

class TestQueryProcessingEndpoints:
    """Test query processing endpoints."""
    
    @pytest.fixture
    def client(self):
        """Get test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_query_data(self):
        """Sample query data for testing."""
        return {
            "query": "What is Python programming?",
            "max_tokens": 1000,
            "confidence_threshold": 0.8,
            "include_sources": True,
            "stream_response": False
        }
    
    @patch('services.api_gateway.main.process_query_with_orchestrator')
    def test_process_query_success(self, mock_process, client, sample_query_data):
        """Test successful query processing."""
        mock_process.return_value = {
            "query_id": "test_query_123",
            "status": "completed",
            "answer": "Python is a programming language...",
            "sources": ["source1", "source2"],
            "confidence": 0.95,
            "processing_time": 2.5,
            "tokens_used": 500
        }
        
        response = client.post("/query", json=sample_query_data)
        assert response.status_code == 200
        data = response.json()
        assert "query_id" in data
        assert "answer" in data
        assert "status" in data
    
    @patch('services.api_gateway.main.process_query_with_orchestrator')
    def test_process_query_invalid_input(self, mock_process, client):
        """Test query processing with invalid input."""
        mock_process.side_effect = HTTPException(status_code=400, detail="Invalid query")
        
        response = client.post("/query", json={"query": ""})
        assert response.status_code == 400
        assert "Invalid query" in response.json()["detail"]
    
    @patch('services.api_gateway.main.process_query_with_orchestrator')
    def test_process_query_rate_limit(self, mock_process, client, sample_query_data):
        """Test query processing with rate limiting."""
        mock_process.side_effect = HTTPException(status_code=429, detail="Rate limit exceeded")
        
        response = client.post("/query", json=sample_query_data)
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]
    
    @patch('services.api_gateway.main.get_query_from_cache')
    def test_get_query_success(self, mock_get, client):
        """Test getting query details."""
        mock_get.return_value = {
            "query_id": "test_query_123",
            "query": "What is Python?",
            "answer": "Python is a programming language...",
            "status": "completed",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        response = client.get("/queries/test_query_123")
        assert response.status_code == 200
        data = response.json()
        assert "query_id" in data
        assert "query" in data
        assert "answer" in data
    
    @patch('services.api_gateway.main.get_query_from_cache')
    def test_get_query_not_found(self, mock_get, client):
        """Test getting non-existent query."""
        mock_get.side_effect = HTTPException(status_code=404, detail="Query not found")
        
        response = client.get("/queries/nonexistent_query")
        assert response.status_code == 404
        assert "Query not found" in response.json()["detail"]
    
    @patch('services.api_gateway.main.list_user_queries')
    def test_list_queries_success(self, mock_list, client):
        """Test listing user queries."""
        mock_list.return_value = {
            "queries": [
                {
                    "query_id": "query_1",
                    "query": "What is Python?",
                    "status": "completed",
                    "created_at": datetime.now().isoformat()
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 20
        }
        
        # Mock authentication
        with patch('services.api_gateway.main.get_current_user') as mock_auth:
            mock_auth.return_value = {"user_id": "test_user_id", "role": "user"}
            
            response = client.get("/queries")
            assert response.status_code == 200
            data = response.json()
            assert "queries" in data
            assert "total" in data
    
    @patch('services.api_gateway.main.update_query_in_cache')
    def test_update_query_success(self, mock_update, client):
        """Test updating query."""
        mock_update.return_value = {
            "query_id": "test_query_123",
            "query": "Updated query",
            "status": "updated",
            "updated_at": datetime.now().isoformat()
        }
        
        # Mock authentication
        with patch('services.api_gateway.main.get_current_user') as mock_auth:
            mock_auth.return_value = {"user_id": "test_user_id", "role": "user"}
            
            response = client.put("/queries/test_query_123", json={
                "query": "Updated query",
                "max_tokens": 1500
            })
            assert response.status_code == 200
            data = response.json()
            assert "query_id" in data
            assert data["query"] == "Updated query"
    
    @patch('services.api_gateway.main.delete_query_from_cache')
    def test_delete_query_success(self, mock_delete, client):
        """Test deleting query."""
        mock_delete.return_value = {"message": "Query deleted successfully"}
        
        # Mock authentication
        with patch('services.api_gateway.main.get_current_user') as mock_auth:
            mock_auth.return_value = {"user_id": "test_user_id", "role": "user"}
            
            response = client.delete("/queries/test_query_123")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
    
    @patch('services.api_gateway.main.get_query_status')
    def test_get_query_status(self, mock_status, client):
        """Test getting query status."""
        mock_status.return_value = {
            "query_id": "test_query_123",
            "status": "processing",
            "progress": 75,
            "estimated_completion": datetime.now().isoformat()
        }
        
        response = client.get("/queries/test_query_123/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "progress" in data
    
    @patch('services.api_gateway.main.reprocess_query')
    def test_reprocess_query_success(self, mock_reprocess, client):
        """Test reprocessing query."""
        mock_reprocess.return_value = {
            "query_id": "test_query_123",
            "status": "reprocessing",
            "message": "Query reprocessing started"
        }
        
        # Mock authentication
        with patch('services.api_gateway.main.get_current_user') as mock_auth:
            mock_auth.return_value = {"user_id": "test_user_id", "role": "user"}
            
            response = client.patch("/queries/test_query_123/reprocess")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] == "reprocessing"

class TestExpertReviewEndpoints:
    """Test expert review endpoints."""
    
    @pytest.fixture
    def client(self):
        """Get test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_review_data(self):
        """Sample review data for testing."""
        return {
            "review_id": "review_123",
            "expert_id": "expert_456",
            "verdict": "supported",
            "notes": "This is a comprehensive review",
            "confidence": 0.95
        }
    
    @patch('services.api_gateway.main.get_pending_reviews')
    def test_get_pending_reviews(self, mock_get, client):
        """Test getting pending reviews."""
        mock_get.return_value = [
            {
                "review_id": "review_123",
                "query": "What is Python?",
                "answer": "Python is a programming language...",
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }
        ]
        
        # Mock authentication
        with patch('services.api_gateway.main.get_current_user') as mock_auth:
            mock_auth.return_value = {"user_id": "expert_456", "role": "expert"}
            
            response = client.get("/expert-reviews/pending")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0
    
    @patch('services.api_gateway.main.submit_expert_review')
    def test_submit_expert_review_success(self, mock_submit, client, sample_review_data):
        """Test successful expert review submission."""
        mock_submit.return_value = {
            "review_id": "review_123",
            "expert_id": "expert_456",
            "verdict": "supported",
            "notes": "This is a comprehensive review",
            "confidence": 0.95,
            "completed_at": datetime.now().isoformat()
        }
        
        # Mock authentication
        with patch('services.api_gateway.main.get_current_user') as mock_auth:
            mock_auth.return_value = {"user_id": "expert_456", "role": "expert"}
            
            response = client.post("/expert-reviews/review_123", json=sample_review_data)
            assert response.status_code == 200
            data = response.json()
            assert "review_id" in data
            assert "verdict" in data
            assert "confidence" in data
    
    @patch('services.api_gateway.main.get_review_details')
    def test_get_review_details(self, mock_get, client):
        """Test getting review details."""
        mock_get.return_value = {
            "review_id": "review_123",
            "expert_id": "expert_456",
            "verdict": "supported",
            "notes": "Comprehensive review",
            "confidence": 0.95,
            "completed_at": datetime.now().isoformat(),
            "query": "What is Python?",
            "answer": "Python is a programming language..."
        }
        
        # Mock authentication
        with patch('services.api_gateway.main.get_current_user') as mock_auth:
            mock_auth.return_value = {"user_id": "expert_456", "role": "expert"}
            
            response = client.get("/expert-reviews/review_123")
            assert response.status_code == 200
            data = response.json()
            assert "review_id" in data
            assert "verdict" in data
            assert "query" in data

class TestTaskGenerationEndpoints:
    """Test task generation endpoints."""
    
    @pytest.fixture
    def client(self):
        """Get test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_task_data(self):
        """Sample task generation data."""
        return {
            "query": "What is Python programming?",
            "task_type": "research",
            "complexity": "medium",
            "deadline": datetime.now().isoformat()
        }
    
    @patch('services.api_gateway.main.generate_tasks_from_query')
    def test_generate_tasks_success(self, mock_generate, client, sample_task_data):
        """Test successful task generation."""
        mock_generate.return_value = {
            "tasks": [
                {
                    "task_id": "task_1",
                    "title": "Research Python basics",
                    "description": "Research fundamental Python concepts",
                    "priority": "high",
                    "estimated_duration": "2 hours"
                }
            ],
            "total_tasks": 1,
            "estimated_completion": datetime.now().isoformat()
        }
        
        response = client.post("/tasks", json=sample_task_data)
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total_tasks" in data
    
    @patch('services.api_gateway.main.generate_tasks_from_query')
    def test_generate_tasks_invalid_input(self, mock_generate, client):
        """Test task generation with invalid input."""
        mock_generate.side_effect = HTTPException(status_code=400, detail="Invalid task type")
        
        response = client.post("/tasks", json={"query": "", "task_type": "invalid"})
        assert response.status_code == 400
        assert "Invalid task type" in response.json()["detail"]

class TestAnalyticsEndpoints:
    """Test analytics endpoints."""
    
    @pytest.fixture
    def client(self):
        """Get test client."""
        return TestClient(app)
    
    @patch('services.api_gateway.main.get_analytics_data')
    def test_get_analytics_success(self, mock_analytics, client):
        """Test getting analytics data."""
        mock_analytics.return_value = {
            "total_queries": 1000,
            "successful_queries": 950,
            "average_response_time": 2.5,
            "popular_topics": ["Python", "JavaScript", "AI"],
            "user_engagement": {
                "daily_active_users": 150,
                "weekly_active_users": 500,
                "monthly_active_users": 2000
            }
        }
        
        # Mock authentication
        with patch('services.api_gateway.main.require_read') as mock_auth:
            mock_auth.return_value = {"user_id": "admin_user", "role": "admin"}
            
            response = client.get("/analytics")
            assert response.status_code == 200
            data = response.json()
            assert "total_queries" in data
            assert "user_engagement" in data
    
    @patch('services.api_gateway.main.get_metrics_data')
    def test_get_metrics_success(self, mock_metrics, client):
        """Test getting metrics data."""
        mock_metrics.return_value = {
            "system_metrics": {
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "disk_usage": 23.1
            },
            "application_metrics": {
                "request_count": 15000,
                "error_rate": 0.5,
                "average_response_time": 125
            }
        }
        
        # Mock authentication
        with patch('services.api_gateway.main.get_current_user') as mock_auth:
            mock_auth.return_value = {"user_id": "admin_user", "role": "admin"}
            
            response = client.get("/metrics")
            assert response.status_code == 200
            data = response.json()
            assert "system_metrics" in data
            assert "application_metrics" in data

class TestSecurityEndpoints:
    """Test security-related endpoints."""
    
    @pytest.fixture
    def client(self):
        """Get test client."""
        return TestClient(app)
    
    @patch('services.api_gateway.main.get_security_status')
    def test_get_security_status(self, mock_security, client):
        """Test getting security status."""
        mock_security.return_value = {
            "authentication_status": "secure",
            "encryption_status": "enabled",
            "rate_limiting_status": "active",
            "last_security_scan": datetime.now().isoformat(),
            "vulnerabilities_found": 0
        }
        
        # Mock authentication
        with patch('services.api_gateway.main.get_current_user') as mock_auth:
            mock_auth.return_value = {"user_id": "admin_user", "role": "admin"}
            
            response = client.get("/security")
            assert response.status_code == 200
            data = response.json()
            assert "authentication_status" in data
            assert "encryption_status" in data

class TestIntegrationEndpoints:
    """Test integration endpoints."""
    
    @pytest.fixture
    def client(self):
        """Get test client."""
        return TestClient(app)
    
    @patch('services.api_gateway.main.get_integration_status')
    def test_get_integration_status(self, mock_integration, client):
        """Test getting integration status."""
        mock_integration.return_value = {
            "llm_providers": {
                "openai": "connected",
                "anthropic": "connected",
                "google": "disconnected"
            },
            "database": "connected",
            "cache": "connected",
            "monitoring": "connected"
        }
        
        response = client.get("/integrations")
        assert response.status_code == 200
        data = response.json()
        assert "llm_providers" in data
        assert "database" in data

class TestFeedbackEndpoints:
    """Test feedback endpoints."""
    
    @pytest.fixture
    def client(self):
        """Get test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_feedback_data(self):
        """Sample feedback data."""
        return {
            "query_id": "query_123",
            "rating": 5,
            "feedback_text": "Excellent response, very helpful!",
            "category": "positive"
        }
    
    @patch('services.api_gateway.main.submit_feedback')
    def test_submit_feedback_success(self, mock_submit, client, sample_feedback_data):
        """Test successful feedback submission."""
        mock_submit.return_value = {
            "feedback_id": "feedback_123",
            "query_id": "query_123",
            "rating": 5,
            "status": "submitted",
            "created_at": datetime.now().isoformat()
        }
        
        # Mock authentication
        with patch('services.api_gateway.main.get_current_user') as mock_auth:
            mock_auth.return_value = {"user_id": "test_user", "role": "user"}
            
            response = client.post("/feedback", json=sample_feedback_data)
            assert response.status_code == 200
            data = response.json()
            assert "feedback_id" in data
            assert "rating" in data

class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.fixture
    def client(self):
        """Get test client."""
        return TestClient(app)
    
    def test_validation_error_handling(self, client):
        """Test validation error handling."""
        response = client.post("/query", json={"invalid": "data"})
        assert response.status_code == 422  # Validation error
    
    def test_authentication_error_handling(self, client):
        """Test authentication error handling."""
        response = client.get("/queries")
        assert response.status_code == 401  # Unauthorized
    
    def test_not_found_error_handling(self, client):
        """Test not found error handling."""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404  # Not found
    
    @patch('services.api_gateway.main.process_query_with_orchestrator')
    def test_internal_server_error_handling(self, mock_process, client):
        """Test internal server error handling."""
        mock_process.side_effect = Exception("Internal server error")
        
        response = client.post("/query", json={"query": "test"})
        assert response.status_code == 500  # Internal server error

class TestRateLimiting:
    """Test rate limiting functionality."""
    
    @pytest.fixture
    def client(self):
        """Get test client."""
        return TestClient(app)
    
    def test_rate_limit_exceeded(self, client):
        """Test rate limit exceeded scenario."""
        # This would require mocking the rate limiter
        # For now, we'll test the structure
        with patch('services.api_gateway.main.rate_limit_middleware') as mock_rate_limit:
            mock_rate_limit.side_effect = HTTPException(status_code=429, detail="Rate limit exceeded")
            
            response = client.post("/query", json={"query": "test"})
            assert response.status_code == 429

class TestWebSocketEndpoints:
    """Test WebSocket endpoints."""
    
    @pytest.fixture
    def client(self):
        """Get test client."""
        return TestClient(app)
    
    def test_websocket_collaboration_connection(self, client):
        """Test WebSocket collaboration connection."""
        # WebSocket testing requires special handling
        # This is a skeleton for WebSocket tests
        with client.websocket_connect("/ws/collaboration") as websocket:
            # Test connection establishment
            assert websocket is not None
    
    def test_websocket_query_updates_connection(self, client):
        """Test WebSocket query updates connection."""
        # WebSocket testing requires special handling
        # This is a skeleton for WebSocket tests
        with client.websocket_connect("/ws/query-updates") as websocket:
            # Test connection establishment
            assert websocket is not None

class TestPerformanceEndpoints:
    """Test performance-related endpoints."""
    
    @pytest.fixture
    def client(self):
        """Get test client."""
        return TestClient(app)
    
    def test_endpoint_response_time(self, client):
        """Test endpoint response time."""
        import time
        
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second
    
    def test_concurrent_requests(self, client):
        """Test concurrent request handling."""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get("/health")
            results.append(response.status_code)
        
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 10

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 