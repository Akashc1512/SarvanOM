"""
End-to-End User Journey Tests - MAANG Standards

This module provides comprehensive E2E tests for complete user journeys,
ensuring the entire application works correctly from user perspective.

Test Coverage:
    - User registration and authentication flows
    - Query processing end-to-end
    - Admin dashboard functionality
    - API key management flows
    - Real-time collaboration features
    - Error recovery scenarios
    - Cross-browser compatibility
    - Mobile responsiveness
    - Performance under load

Authors:
    - Universal Knowledge Platform Engineering Team
    
Version:
    2.0.0 (2024-12-28)
"""

import pytest
import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, AsyncMock

# Import test dependencies
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Import application components
from services.api_gateway.main import app
from shared.models.models import User, Role, APIKey, Query

class TestUserRegistrationJourney:
    """Test complete user registration journey."""
    
    @pytest.fixture
    def client(self):
        """Get test client."""
        return TestClient(app)
    
    @pytest.fixture
    def browser(self):
        """Get browser instance for UI testing."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()
    
    def test_user_registration_flow(self, client):
        """Test complete user registration flow."""
        # Step 1: Register new user
        registration_data = {
            "username": "testuser_e2e",
            "email": "testuser_e2e@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test User E2E"
        }
        
        response = client.post("/auth/register", json=registration_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "user_id" in data
        assert data["role"] == "user"
        
        # Step 2: Login with new user
        login_data = {
            "username": "testuser_e2e",
            "password": "SecurePassword123!"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "api_key" in data
        
        # Step 3: Verify user can access protected endpoints
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        
        # Test health check
        response = client.get("/health", headers=headers)
        assert response.status_code == 200
        
        # Test user profile
        response = client.get("/queries", headers=headers)
        assert response.status_code == 200
    
    def test_user_registration_validation(self, client):
        """Test user registration validation."""
        # Test invalid email
        invalid_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "SecurePassword123!"
        }
        
        response = client.post("/auth/register", json=invalid_data)
        assert response.status_code == 422  # Validation error
        
        # Test weak password
        weak_password_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123"
        }
        
        response = client.post("/auth/register", json=weak_password_data)
        assert response.status_code == 422  # Validation error
    
    def test_user_registration_duplicate(self, client):
        """Test duplicate user registration."""
        # Register first user
        user_data = {
            "username": "duplicate_user",
            "email": "duplicate@example.com",
            "password": "SecurePassword123!"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        
        # Try to register duplicate
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 409  # Conflict
    
    def test_user_registration_ui_flow(self, browser):
        """Test user registration UI flow."""
        # Navigate to registration page
        browser.get("http://localhost:3000/register")
        
        # Fill registration form
        username_input = browser.find_element(By.ID, "username")
        email_input = browser.find_element(By.ID, "email")
        password_input = browser.find_element(By.ID, "password")
        submit_button = browser.find_element(By.ID, "register-submit")
        
        username_input.send_keys("ui_test_user")
        email_input.send_keys("ui_test@example.com")
        password_input.send_keys("SecurePassword123!")
        
        # Submit form
        submit_button.click()
        
        # Wait for success message
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        
        # Verify redirect to dashboard
        assert "dashboard" in browser.current_url

class TestQueryProcessingJourney:
    """Test complete query processing journey."""
    
    @pytest.fixture
    def authenticated_client(self, client):
        """Get authenticated client."""
        # Register and login user
        user_data = {
            "username": "query_test_user",
            "email": "query_test@example.com",
            "password": "SecurePassword123!"
        }
        
        # Register
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        
        # Login
        login_data = {
            "username": "query_test_user",
            "password": "SecurePassword123!"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        
        return client, headers
    
    def test_query_processing_flow(self, authenticated_client):
        """Test complete query processing flow."""
        client, headers = authenticated_client
        
        # Step 1: Submit query
        query_data = {
            "query": "What is Python programming language?",
            "max_tokens": 1000,
            "confidence_threshold": 0.8,
            "include_sources": True
        }
        
        response = client.post("/query", json=query_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "query_id" in data
        assert "status" in data
        assert data["status"] in ["processing", "completed"]
        
        query_id = data["query_id"]
        
        # Step 2: Check query status
        response = client.get(f"/queries/{query_id}/status", headers=headers)
        assert response.status_code == 200
        
        status_data = response.json()
        assert "status" in status_data
        assert "progress" in status_data
        
        # Step 3: Get final result
        response = client.get(f"/queries/{query_id}", headers=headers)
        assert response.status_code == 200
        
        result_data = response.json()
        assert "query" in result_data
        assert "answer" in result_data
        assert "sources" in result_data
    
    def test_query_processing_with_feedback(self, authenticated_client):
        """Test query processing with user feedback."""
        client, headers = authenticated_client
        
        # Submit query
        query_data = {
            "query": "What are the benefits of Python?",
            "max_tokens": 1000,
            "include_sources": True
        }
        
        response = client.post("/query", json=query_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        query_id = data["query_id"]
        
        # Wait for completion
        max_attempts = 10
        for attempt in range(max_attempts):
            response = client.get(f"/queries/{query_id}/status", headers=headers)
            status_data = response.json()
            
            if status_data["status"] == "completed":
                break
            
            time.sleep(1)
        
        # Submit feedback
        feedback_data = {
            "query_id": query_id,
            "rating": 5,
            "feedback_text": "Excellent response, very helpful!",
            "category": "positive"
        }
        
        response = client.post("/feedback", json=feedback_data, headers=headers)
        assert response.status_code == 200
        
        feedback_data = response.json()
        assert "feedback_id" in feedback_data
        assert feedback_data["rating"] == 5
    
    def test_query_processing_error_recovery(self, authenticated_client):
        """Test query processing error recovery."""
        client, headers = authenticated_client
        
        # Submit invalid query
        invalid_query_data = {
            "query": "",  # Empty query
            "max_tokens": 1000
        }
        
        response = client.post("/query", json=invalid_query_data, headers=headers)
        assert response.status_code == 400  # Bad request
        
        # Submit valid query after error
        valid_query_data = {
            "query": "What is Python?",
            "max_tokens": 1000
        }
        
        response = client.post("/query", json=valid_query_data, headers=headers)
        assert response.status_code == 200  # Should work after error
    
    def test_query_processing_ui_flow(self, browser):
        """Test query processing UI flow."""
        # Login to application
        browser.get("http://localhost:3000/login")
        
        username_input = browser.find_element(By.ID, "username")
        password_input = browser.find_element(By.ID, "password")
        login_button = browser.find_element(By.ID, "login-submit")
        
        username_input.send_keys("ui_test_user")
        password_input.send_keys("SecurePassword123!")
        login_button.click()
        
        # Wait for dashboard
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "query-input"))
        )
        
        # Submit query
        query_input = browser.find_element(By.ID, "query-input")
        submit_button = browser.find_element(By.ID, "submit-query")
        
        query_input.send_keys("What is Python programming?")
        submit_button.click()
        
        # Wait for response
        WebDriverWait(browser, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "query-response"))
        )
        
        # Verify response content
        response_element = browser.find_element(By.CLASS_NAME, "query-response")
        assert "Python" in response_element.text

class TestAdminDashboardJourney:
    """Test admin dashboard functionality."""
    
    @pytest.fixture
    def admin_client(self, client):
        """Get admin client."""
        # Create admin user
        admin_data = {
            "username": "admin_test_user",
            "email": "admin_test@example.com",
            "password": "SecurePassword123!",
            "role": "admin"
        }
        
        # Register admin
        response = client.post("/auth/register", json=admin_data)
        assert response.status_code == 200
        
        # Login as admin
        login_data = {
            "username": "admin_test_user",
            "password": "SecurePassword123!"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        
        return client, headers
    
    def test_admin_dashboard_access(self, admin_client):
        """Test admin dashboard access."""
        client, headers = admin_client
        
        # Access admin analytics
        response = client.get("/analytics", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "total_queries" in data
        assert "user_engagement" in data
        
        # Access admin metrics
        response = client.get("/metrics", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "system_metrics" in data
        assert "application_metrics" in data
        
        # Access security status
        response = client.get("/security", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "authentication_status" in data
        assert "encryption_status" in data
    
    def test_admin_user_management(self, admin_client):
        """Test admin user management."""
        client, headers = admin_client
        
        # List all users (admin functionality)
        response = client.get("/admin/users", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Get user details
        if data:
            user_id = data[0]["user_id"]
            response = client.get(f"/admin/users/{user_id}", headers=headers)
            assert response.status_code == 200
    
    def test_admin_system_monitoring(self, admin_client):
        """Test admin system monitoring."""
        client, headers = admin_client
        
        # Check system health
        response = client.get("/health", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        
        # Check integration status
        response = client.get("/integrations", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "llm_providers" in data
        assert "database" in data

class TestAPIKeyManagementJourney:
    """Test API key management flows."""
    
    @pytest.fixture
    def api_client(self, client):
        """Get API client."""
        # Register and login user
        user_data = {
            "username": "api_test_user",
            "email": "api_test@example.com",
            "password": "SecurePassword123!"
        }
        
        # Register
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        
        # Login
        login_data = {
            "username": "api_test_user",
            "password": "SecurePassword123!"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        
        return client, headers, data["api_key"]
    
    def test_api_key_creation_flow(self, api_client):
        """Test API key creation flow."""
        client, headers, existing_key = api_client
        
        # Create new API key
        response = client.post("/auth/api-key", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "api_key" in data
        assert "user_id" in data
        assert "permissions" in data
        
        new_api_key = data["api_key"]
        
        # Verify API key works
        api_headers = {"X-API-Key": new_api_key}
        response = client.get("/health", headers=api_headers)
        assert response.status_code == 200
    
    def test_api_key_listing_flow(self, api_client):
        """Test API key listing flow."""
        client, headers, existing_key = api_client
        
        # List API keys
        response = client.get("/auth/api-keys", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify existing key is listed
        api_keys = [key["api_key"] for key in data]
        assert existing_key in api_keys
    
    def test_api_key_revocation_flow(self, api_client):
        """Test API key revocation flow."""
        client, headers, existing_key = api_client
        
        # Create new API key
        response = client.post("/auth/api-key", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        new_api_key = data["api_key"]
        
        # Revoke API key
        response = client.delete(f"/auth/api-key/{new_api_key}", headers=headers)
        assert response.status_code == 200
        
        # Verify revoked key doesn't work
        api_headers = {"X-API-Key": new_api_key}
        response = client.get("/health", headers=api_headers)
        assert response.status_code == 401  # Unauthorized
    
    def test_api_key_permissions_flow(self, api_client):
        """Test API key permissions flow."""
        client, headers, existing_key = api_client
        
        # Create API key with specific permissions
        key_data = {
            "name": "Test API Key",
            "permissions": ["read", "write"],
            "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        response = client.post("/auth/api-key", json=key_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "permissions" in data
        assert "read" in data["permissions"]
        assert "write" in data["permissions"]

class TestRealTimeCollaborationJourney:
    """Test real-time collaboration features."""
    
    @pytest.fixture
    def collaboration_client(self, client):
        """Get collaboration client."""
        # Register and login user
        user_data = {
            "username": "collab_test_user",
            "email": "collab_test@example.com",
            "password": "SecurePassword123!"
        }
        
        # Register
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        
        # Login
        login_data = {
            "username": "collab_test_user",
            "password": "SecurePassword123!"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        
        return client, headers
    
    def test_websocket_connection_flow(self, collaboration_client):
        """Test WebSocket connection flow."""
        client, headers = collaboration_client
        
        # Test WebSocket connection
        with client.websocket_connect("/ws/collaboration") as websocket:
            # Send join message
            join_message = {
                "type": "join",
                "room": "test_room",
                "user_id": "test_user"
            }
            websocket.send_text(json.dumps(join_message))
            
            # Receive confirmation
            response = websocket.receive_text()
            data = json.loads(response)
            assert data["type"] == "joined"
            assert data["room"] == "test_room"
    
    def test_real_time_messaging_flow(self, collaboration_client):
        """Test real-time messaging flow."""
        client, headers = collaboration_client
        
        with client.websocket_connect("/ws/collaboration") as websocket:
            # Join room
            join_message = {
                "type": "join",
                "room": "test_room",
                "user_id": "test_user"
            }
            websocket.send_text(json.dumps(join_message))
            
            # Send message
            message = {
                "type": "message",
                "room": "test_room",
                "content": "Hello, world!",
                "user_id": "test_user"
            }
            websocket.send_text(json.dumps(message))
            
            # Receive message
            response = websocket.receive_text()
            data = json.loads(response)
            assert data["type"] == "message"
            assert data["content"] == "Hello, world!"
    
    def test_query_updates_websocket_flow(self, collaboration_client):
        """Test query updates WebSocket flow."""
        client, headers = collaboration_client
        
        with client.websocket_connect("/ws/query-updates") as websocket:
            # Subscribe to query updates
            subscribe_message = {
                "type": "subscribe",
                "query_id": "test_query_123"
            }
            websocket.send_text(json.dumps(subscribe_message))
            
            # Receive subscription confirmation
            response = websocket.receive_text()
            data = json.loads(response)
            assert data["type"] == "subscribed"

class TestErrorRecoveryJourney:
    """Test error recovery scenarios."""
    
    @pytest.fixture
    def recovery_client(self, client):
        """Get recovery client."""
        # Register and login user
        user_data = {
            "username": "recovery_test_user",
            "email": "recovery_test@example.com",
            "password": "SecurePassword123!"
        }
        
        # Register
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        
        # Login
        login_data = {
            "username": "recovery_test_user",
            "password": "SecurePassword123!"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        
        return client, headers
    
    def test_network_error_recovery(self, recovery_client):
        """Test network error recovery."""
        client, headers = recovery_client
        
        # Simulate network error by using invalid endpoint
        response = client.get("/nonexistent-endpoint", headers=headers)
        assert response.status_code == 404
        
        # Verify system still works after error
        response = client.get("/health", headers=headers)
        assert response.status_code == 200
    
    def test_authentication_error_recovery(self, recovery_client):
        """Test authentication error recovery."""
        client, headers = recovery_client
        
        # Use invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/queries", headers=invalid_headers)
        assert response.status_code == 401
        
        # Verify valid token still works
        response = client.get("/queries", headers=headers)
        assert response.status_code == 200
    
    def test_rate_limit_recovery(self, recovery_client):
        """Test rate limit recovery."""
        client, headers = recovery_client
        
        # Make many requests to trigger rate limit
        for i in range(20):
            response = client.post("/query", json={
                "query": f"Test query {i}",
                "max_tokens": 100
            }, headers=headers)
            
            if response.status_code == 429:  # Rate limited
                break
        
        # Wait and verify system recovers
        time.sleep(2)
        response = client.get("/health", headers=headers)
        assert response.status_code == 200

class TestCrossBrowserCompatibility:
    """Test cross-browser compatibility."""
    
    @pytest.fixture
    def browsers(self):
        """Get multiple browser instances."""
        browsers = []
        
        # Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        browsers.append(webdriver.Chrome(options=chrome_options))
        
        # Firefox (if available)
        try:
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            firefox_options = FirefoxOptions()
            firefox_options.add_argument("--headless")
            browsers.append(webdriver.Firefox(options=firefox_options))
        except:
            pass
        
        yield browsers
        
        for browser in browsers:
            browser.quit()
    
    def test_login_flow_chrome(self, browsers):
        """Test login flow in Chrome."""
        if not browsers:
            pytest.skip("No browsers available")
        
        browser = browsers[0]  # Chrome
        
        # Navigate to login page
        browser.get("http://localhost:3000/login")
        
        # Fill login form
        username_input = browser.find_element(By.ID, "username")
        password_input = browser.find_element(By.ID, "password")
        login_button = browser.find_element(By.ID, "login-submit")
        
        username_input.send_keys("test_user")
        password_input.send_keys("SecurePassword123!")
        login_button.click()
        
        # Wait for dashboard
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "dashboard"))
        )
        
        # Verify successful login
        assert "dashboard" in browser.current_url
    
    def test_query_processing_chrome(self, browsers):
        """Test query processing in Chrome."""
        if not browsers:
            pytest.skip("No browsers available")
        
        browser = browsers[0]  # Chrome
        
        # Login first
        browser.get("http://localhost:3000/login")
        
        username_input = browser.find_element(By.ID, "username")
        password_input = browser.find_element(By.ID, "password")
        login_button = browser.find_element(By.ID, "login-submit")
        
        username_input.send_keys("test_user")
        password_input.send_keys("SecurePassword123!")
        login_button.click()
        
        # Wait for dashboard
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "query-input"))
        )
        
        # Submit query
        query_input = browser.find_element(By.ID, "query-input")
        submit_button = browser.find_element(By.ID, "submit-query")
        
        query_input.send_keys("What is Python?")
        submit_button.click()
        
        # Wait for response
        WebDriverWait(browser, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "query-response"))
        )
        
        # Verify response
        response_element = browser.find_element(By.CLASS_NAME, "query-response")
        assert len(response_element.text) > 0

class TestMobileResponsiveness:
    """Test mobile responsiveness."""
    
    @pytest.fixture
    def mobile_browser(self):
        """Get mobile browser instance."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=375,667")  # iPhone 6/7/8 size
        
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()
    
    def test_mobile_login_flow(self, mobile_browser):
        """Test mobile login flow."""
        # Navigate to login page
        mobile_browser.get("http://localhost:3000/login")
        
        # Check mobile layout
        username_input = mobile_browser.find_element(By.ID, "username")
        password_input = mobile_browser.find_element(By.ID, "password")
        login_button = mobile_browser.find_element(By.ID, "login-submit")
        
        # Verify elements are visible and accessible
        assert username_input.is_displayed()
        assert password_input.is_displayed()
        assert login_button.is_displayed()
        
        # Test mobile interaction
        username_input.send_keys("mobile_test_user")
        password_input.send_keys("SecurePassword123!")
        login_button.click()
        
        # Wait for dashboard
        WebDriverWait(mobile_browser, 10).until(
            EC.presence_of_element_located((By.ID, "dashboard"))
        )
    
    def test_mobile_query_processing(self, mobile_browser):
        """Test mobile query processing."""
        # Login first
        mobile_browser.get("http://localhost:3000/login")
        
        username_input = mobile_browser.find_element(By.ID, "username")
        password_input = mobile_browser.find_element(By.ID, "password")
        login_button = mobile_browser.find_element(By.ID, "login-submit")
        
        username_input.send_keys("mobile_test_user")
        password_input.send_keys("SecurePassword123!")
        login_button.click()
        
        # Wait for dashboard
        WebDriverWait(mobile_browser, 10).until(
            EC.presence_of_element_located((By.ID, "query-input"))
        )
        
        # Test mobile query input
        query_input = mobile_browser.find_element(By.ID, "query-input")
        submit_button = mobile_browser.find_element(By.ID, "submit-query")
        
        query_input.send_keys("What is Python?")
        submit_button.click()
        
        # Wait for response
        WebDriverWait(mobile_browser, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "query-response"))
        )
        
        # Verify mobile-friendly response
        response_element = mobile_browser.find_element(By.CLASS_NAME, "query-response")
        assert len(response_element.text) > 0

class TestPerformanceUnderLoad:
    """Test performance under load."""
    
    @pytest.fixture
    def load_client(self, client):
        """Get load test client."""
        # Register and login user
        user_data = {
            "username": "load_test_user",
            "email": "load_test@example.com",
            "password": "SecurePassword123!"
        }
        
        # Register
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        
        # Login
        login_data = {
            "username": "load_test_user",
            "password": "SecurePassword123!"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        
        return client, headers
    
    def test_concurrent_query_processing(self, load_client):
        """Test concurrent query processing."""
        client, headers = load_client
        
        import threading
        import time
        
        results = []
        errors = []
        
        def make_query(query_id):
            try:
                response = client.post("/query", json={
                    "query": f"Test query {query_id}",
                    "max_tokens": 100
                }, headers=headers)
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Start multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_query, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(results) == 10
        success_count = sum(1 for status in results if status == 200)
        assert success_count >= 8  # At least 80% success rate
        assert len(errors) == 0
    
    def test_response_time_under_load(self, load_client):
        """Test response time under load."""
        client, headers = load_client
        
        import time
        
        response_times = []
        
        # Make multiple requests and measure response times
        for i in range(20):
            start_time = time.time()
            
            response = client.get("/health", headers=headers)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            response_times.append(response_time)
            
            assert response.status_code == 200
        
        # Calculate average response time
        avg_response_time = sum(response_times) / len(response_times)
        
        # Verify performance requirements
        assert avg_response_time < 1.0  # Average response time < 1 second
        assert max(response_times) < 3.0  # Max response time < 3 seconds

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 