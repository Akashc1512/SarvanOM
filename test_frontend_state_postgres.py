"""
Frontend State PostgreSQL Integration Tests - Universal Knowledge Platform

This module provides comprehensive integration tests for frontend session
persistence using PostgreSQL, ensuring the complete workflow from database
creation to API endpoints works correctly.

Test Coverage:
- Database table creation and structure
- State saving, fetching, and clearing operations
- Session-specific state isolation
- Graceful handling of missing states
- API endpoint functionality
- Error handling and edge cases

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import os
import sys
import pytest
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the components to test
from shared.models.frontend_state import FrontendState, Base
from services.frontend_state_service import FrontendStateService
from services.api_gateway.main import app

# Test client for API endpoints
client = TestClient(app)

# Mock orchestrator for API tests
class MockOrchestrator:
    """Mock orchestrator for API endpoint tests."""
    
    async def process_query(self, query: str, user_context: dict = None):
        """Mock process_query method."""
        return {
            "status": "success",
            "result": "Mock query result",
            "session_id": "mock_session_123"
        }

# Patch the orchestrator in the main app
import services.api_gateway.main
services.api_gateway.main.orchestrator = MockOrchestrator()


class TestFrontendStatePostgres:
    """Integration tests for frontend state persistence using PostgreSQL."""
    
    @pytest.fixture(scope="class")
    def db_engine(self):
        """Create database engine for testing."""
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            pytest.skip("DATABASE_URL not configured")
        
        engine = create_engine(db_url)
        
        # Create tables
        Base.metadata.create_all(engine)
        
        yield engine
        
        # Cleanup - drop tables
        Base.metadata.drop_all(engine)
    
    @pytest.fixture
    def db_session(self, db_engine):
        """Create database session for testing."""
        SessionLocal = sessionmaker(bind=db_engine)
        session = SessionLocal()
        
        yield session
        
        # Cleanup - rollback any uncommitted changes
        session.rollback()
        session.close()
    
    @pytest.fixture
    def frontend_state_service(self, db_session):
        """Create FrontendStateService instance."""
        return FrontendStateService(db_session)
    
    @pytest.fixture
    def sample_ui_state(self):
        """Sample UI state data for testing."""
        return {
            "sidebar": {
                "collapsed": False,
                "active_tab": "dashboard",
                "width": 250
            },
            "query_history": [
                {
                    "query": "What is artificial intelligence?",
                    "timestamp": "2024-12-28T10:00:00Z",
                    "results_count": 15
                },
                {
                    "query": "Machine learning algorithms",
                    "timestamp": "2024-12-28T10:05:00Z",
                    "results_count": 23
                }
            ],
            "current_view": {
                "page": "dashboard",
                "filters": {
                    "category": "technology",
                    "date_range": "last_week",
                    "sort_by": "relevance"
                },
                "pagination": {
                    "page": 1,
                    "per_page": 20,
                    "total": 150
                }
            },
            "user_preferences": {
                "theme": "dark",
                "language": "en",
                "notifications": True,
                "auto_save": True
            },
            "form_data": {
                "search_query": "",
                "selected_filters": [],
                "sort_preference": "relevance"
            }
        }
    
    def test_database_table_structure(self, db_engine):
        """Test that the frontend_states table has correct structure."""
        with db_engine.connect() as conn:
            # Check table exists - use database-agnostic approach
            try:
                # Try PostgreSQL approach first
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'frontend_states'
                    )
                """))
                table_exists = result.fetchone()[0]
            except Exception:
                # Fallback to SQLite approach
                result = conn.execute(text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='frontend_states'
                """))
                table_exists = result.fetchone() is not None
            
            assert table_exists, "frontend_states table should exist"
            
            # Check columns - use database-agnostic approach
            try:
                # PostgreSQL approach
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'frontend_states'
                    ORDER BY ordinal_position
                """))
                columns = {row[0]: {'type': row[1], 'nullable': row[2]} for row in result.fetchall()}
            except Exception:
                # SQLite approach - just verify table exists and has expected structure
                # For SQLite, we'll just verify the table exists and can be queried
                result = conn.execute(text("PRAGMA table_info(frontend_states)"))
                columns_info = result.fetchall()
                columns = {row[1]: {'type': row[2], 'nullable': 'YES' if row[3] == 0 else 'NO'} for row in columns_info}
            
            # Verify required columns exist
            assert 'session_id' in columns, "session_id column should exist"
            assert 'user_id' in columns, "user_id column should exist"
            assert 'current_view_state' in columns, "current_view_state column should exist"
            assert 'last_updated' in columns, "last_updated column should exist"
            
            # Verify data types (more flexible for different database types)
            session_id_type = columns['session_id']['type'].lower()
            user_id_type = columns['user_id']['type'].lower()
            current_view_state_type = columns['current_view_state']['type'].lower()
            last_updated_type = columns['last_updated']['type'].lower()
            
            assert 'varchar' in session_id_type or 'text' in session_id_type, "session_id should be varchar/text"
            assert 'varchar' in user_id_type or 'text' in user_id_type, "user_id should be varchar/text"
            assert 'json' in current_view_state_type or 'text' in current_view_state_type, "current_view_state should be json/text"
            assert 'timestamp' in last_updated_type or 'datetime' in last_updated_type, "last_updated should be timestamp/datetime"
            
            # Verify constraints
            assert columns['session_id']['nullable'] == 'NO', "session_id should be NOT NULL"
            assert columns['user_id']['nullable'] == 'YES', "user_id should be nullable"
            assert columns['current_view_state']['nullable'] == 'NO', "current_view_state should be NOT NULL"
            assert columns['last_updated']['nullable'] == 'NO', "last_updated should be NOT NULL"
    
    def test_save_ui_state_new_session(self, frontend_state_service, sample_ui_state):
        """Test saving UI state for a new session."""
        session_id = "test_session_new_123"
        user_id = "user_456"
        
        # Save state
        result = frontend_state_service.update_state(session_id, sample_ui_state, user_id)
        
        # Verify result
        assert result is not None
        assert result["session_id"] == session_id
        assert result["user_id"] == user_id
        assert result["current_view_state"] == sample_ui_state
        assert "last_updated" in result
        
        # Verify database record
        saved_state = frontend_state_service.get_state(session_id)
        assert saved_state is not None
        assert saved_state["session_id"] == session_id
        assert saved_state["user_id"] == user_id
        assert saved_state["current_view_state"] == sample_ui_state
    
    def test_save_ui_state_existing_session(self, frontend_state_service, sample_ui_state):
        """Test updating UI state for an existing session."""
        session_id = "test_session_existing_123"
        user_id = "user_789"
        
        # Initial state
        initial_state = {
            "sidebar": {"collapsed": True},
            "current_view": {"page": "search"}
        }
        
        # Save initial state
        frontend_state_service.update_state(session_id, initial_state, user_id)
        
        # Update with new state - this does shallow merge (replaces nested objects)
        updated_state = {
            "sidebar": {"collapsed": False, "active_tab": "dashboard"},
            "current_view": {"page": "dashboard", "filters": {"category": "technology"}},
            "user_preferences": {"theme": "dark"}
        }
        
        result = frontend_state_service.update_state(session_id, updated_state, user_id)
        
        # Verify result
        assert result is not None
        assert result["session_id"] == session_id
        assert result["user_id"] == user_id
        
        # Verify merged state - shallow merge behavior
        saved_state = frontend_state_service.get_state(session_id)
        assert saved_state is not None
        
        # Check that the new values are present (shallow merge replaces nested objects)
        assert saved_state["current_view_state"]["sidebar"]["collapsed"] == False
        assert saved_state["current_view_state"]["sidebar"]["active_tab"] == "dashboard"
        assert saved_state["current_view_state"]["current_view"]["page"] == "dashboard"
        assert saved_state["current_view_state"]["user_preferences"]["theme"] == "dark"
        
        # Check that the new nested objects are present
        assert "filters" in saved_state["current_view_state"]["current_view"]
        assert saved_state["current_view_state"]["current_view"]["filters"]["category"] == "technology"
    
    def test_get_ui_state_existing(self, frontend_state_service, sample_ui_state):
        """Test retrieving UI state for an existing session."""
        session_id = "test_session_get_123"
        user_id = "user_get_456"
        
        # Save state first
        frontend_state_service.update_state(session_id, sample_ui_state, user_id)
        
        # Retrieve state
        result = frontend_state_service.get_state(session_id)
        
        # Verify result
        assert result is not None
        assert result["session_id"] == session_id
        assert result["user_id"] == user_id
        assert result["current_view_state"] == sample_ui_state
        assert "last_updated" in result
        
        # Verify specific state values
        state = result["current_view_state"]
        assert state["sidebar"]["collapsed"] == False
        assert state["sidebar"]["active_tab"] == "dashboard"
        assert len(state["query_history"]) == 2
        assert state["user_preferences"]["theme"] == "dark"
    
    def test_get_ui_state_missing(self, frontend_state_service):
        """Test retrieving UI state for a non-existent session."""
        session_id = "nonexistent_session_123"
        
        # Try to get state
        result = frontend_state_service.get_state(session_id)
        
        # Should return None for missing session
        assert result is None
    
    def test_clear_ui_state_existing(self, frontend_state_service, sample_ui_state):
        """Test clearing UI state for an existing session."""
        session_id = "test_session_clear_123"
        user_id = "user_clear_456"
        
        # Save state first
        frontend_state_service.update_state(session_id, sample_ui_state, user_id)
        
        # Verify state exists
        saved_state = frontend_state_service.get_state(session_id)
        assert saved_state is not None
        
        # Clear state
        result = frontend_state_service.clear_state(session_id)
        
        # Verify clear operation
        assert result is True
        
        # Verify state is cleared
        cleared_state = frontend_state_service.get_state(session_id)
        assert cleared_state is not None
        assert cleared_state["current_view_state"] == {}
    
    def test_clear_ui_state_missing(self, frontend_state_service):
        """Test clearing UI state for a non-existent session."""
        session_id = "nonexistent_session_clear_123"
        
        # Try to clear state
        result = frontend_state_service.clear_state(session_id)
        
        # Should return False for missing session
        assert result is False
    
    def test_session_isolation(self, frontend_state_service, sample_ui_state):
        """Test that sessions are properly isolated from each other."""
        session_1 = "test_session_1"
        session_2 = "test_session_2"
        user_id = "user_isolation_123"
        
        # State for session 1
        state_1 = {
            "sidebar": {"collapsed": False, "active_tab": "dashboard"},
            "current_view": {"page": "dashboard"},
            "user_preferences": {"theme": "dark"}
        }
        
        # State for session 2
        state_2 = {
            "sidebar": {"collapsed": True, "active_tab": "search"},
            "current_view": {"page": "search"},
            "user_preferences": {"theme": "light"}
        }
        
        # Save states
        frontend_state_service.update_state(session_1, state_1, user_id)
        frontend_state_service.update_state(session_2, state_2, user_id)
        
        # Retrieve states
        retrieved_1 = frontend_state_service.get_state(session_1)
        retrieved_2 = frontend_state_service.get_state(session_2)
        
        # Verify isolation
        assert retrieved_1 is not None
        assert retrieved_2 is not None
        assert retrieved_1["session_id"] == session_1
        assert retrieved_2["session_id"] == session_2
        
        # Verify different states
        assert retrieved_1["current_view_state"]["sidebar"]["collapsed"] == False
        assert retrieved_2["current_view_state"]["sidebar"]["collapsed"] == True
        assert retrieved_1["current_view_state"]["user_preferences"]["theme"] == "dark"
        assert retrieved_2["current_view_state"]["user_preferences"]["theme"] == "light"
    
    def test_graceful_missing_state_handling(self, frontend_state_service):
        """Test graceful handling of missing state scenarios."""
        session_id = "missing_session_graceful_123"
        
        # Test get_state with missing session
        result = frontend_state_service.get_state(session_id)
        assert result is None
        
        # Test get_state_value with missing session
        result = frontend_state_service.get_state_value(session_id, "sidebar", "default_value")
        assert result == "default_value"
        
        # Test get_session_info with missing session
        result = frontend_state_service.get_session_info(session_id)
        assert result is None
        
        # Test clear_state with missing session
        result = frontend_state_service.clear_state(session_id)
        assert result is False
        
        # Test delete_state with missing session
        result = frontend_state_service.delete_state(session_id)
        assert result is False
    
    def test_api_endpoint_get_state(self, frontend_state_service, sample_ui_state):
        """Test API endpoint for getting state."""
        session_id = "test_api_get_123"
        user_id = "user_api_456"
        
        # Save state first
        frontend_state_service.update_state(session_id, sample_ui_state, user_id)
        
        # Test API endpoint
        response = client.get(f"/api/v1/state/{session_id}")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["session_id"] == session_id
        assert data["data"]["user_id"] == user_id
        assert data["data"]["current_view_state"] == sample_ui_state
    
    def test_api_endpoint_get_state_missing(self):
        """Test API endpoint for getting non-existent state."""
        session_id = "nonexistent_api_session_123"
        
        # Test API endpoint
        response = client.get(f"/api/v1/state/{session_id}")
        
        # Verify response
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_api_endpoint_update_state(self, sample_ui_state):
        """Test API endpoint for updating state."""
        session_id = "test_api_update_123"
        
        # Test API endpoint
        response = client.put(f"/api/v1/state/{session_id}", json=sample_ui_state)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["session_id"] == session_id
        assert data["data"]["current_view_state"] == sample_ui_state
    
    def test_api_endpoint_clear_state(self, frontend_state_service, sample_ui_state):
        """Test API endpoint for clearing state."""
        session_id = "test_api_clear_123"
        user_id = "user_api_clear_456"
        
        # Save state first
        frontend_state_service.update_state(session_id, sample_ui_state, user_id)
        
        # Test API endpoint
        response = client.delete(f"/api/v1/state/{session_id}")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "cleared" in data["message"].lower()
    
    def test_api_endpoint_get_session_info(self, frontend_state_service, sample_ui_state):
        """Test API endpoint for getting session info."""
        session_id = "test_api_info_123"
        user_id = "user_api_info_456"
        
        # Save state first
        frontend_state_service.update_state(session_id, sample_ui_state, user_id)
        
        # Test API endpoint
        response = client.get(f"/api/v1/state/{session_id}/info")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["session_id"] == session_id
        assert data["data"]["user_id"] == user_id
        assert "state_keys_count" in data["data"]
    
    def test_comprehensive_workflow(self, frontend_state_service, sample_ui_state):
        """Test a comprehensive workflow from creation to deletion."""
        session_id = "comprehensive_workflow_123"
        user_id = "user_comprehensive_456"
        
        # Step 1: Create initial state
        result = frontend_state_service.update_state(session_id, sample_ui_state, user_id)
        assert result is not None
        assert result["session_id"] == session_id
        
        # Step 2: Retrieve and verify state
        retrieved_state = frontend_state_service.get_state(session_id)
        assert retrieved_state is not None
        assert retrieved_state["current_view_state"] == sample_ui_state
        
        # Step 3: Update specific values - set_state_value adds to current_view_state directly
        updated_state = frontend_state_service.set_state_value(
            session_id, "new_preference", "dark_mode"
        )
        assert updated_state is not None
        
        # Debug: Check what was returned by set_state_value
        print(f"DEBUG: set_state_value returned: {updated_state}")
        
        # Step 4: Merge additional state
        additional_state = {
            "additional_key": "additional_value",
            "sidebar": {"collapsed": True}  # Override existing
        }
        merged_state = frontend_state_service.merge_state(session_id, additional_state)
        assert merged_state is not None
        
        # Debug: Check what was returned by merge_state
        print(f"DEBUG: merge_state returned: {merged_state}")
        
        # Step 5: Verify merged state - check that new_preference is at the top level of current_view_state
        final_state = frontend_state_service.get_state(session_id)
        assert final_state is not None
        
        # Debug: Check the final state
        print(f"DEBUG: final_state: {final_state}")
        print(f"DEBUG: current_view_state keys: {final_state['current_view_state'].keys()}")
        
        # Check that the new_preference was set correctly
        assert "new_preference" in final_state["current_view_state"], f"new_preference not found in state: {final_state['current_view_state'].keys()}"
        assert final_state["current_view_state"]["new_preference"] == "dark_mode"
        assert final_state["current_view_state"]["additional_key"] == "additional_value"
        
        # Verify that the sidebar was overridden (shallow merge behavior)
        assert final_state["current_view_state"]["sidebar"]["collapsed"] == True
        # The original sidebar properties should be preserved
        assert "active_tab" in final_state["current_view_state"]["sidebar"]
        
        # Step 6: Get session info
        session_info = frontend_state_service.get_session_info(session_id)
        assert session_info is not None
        assert session_info["session_id"] == session_id
        assert session_info["user_id"] == user_id
        
        # Step 7: Clear state
        clear_result = frontend_state_service.clear_state(session_id)
        assert clear_result is True
        
        # Step 8: Verify cleared state
        cleared_state = frontend_state_service.get_state(session_id)
        assert cleared_state is not None
        assert cleared_state["current_view_state"] == {}
        
        # Step 9: Delete state completely
        delete_result = frontend_state_service.delete_state(session_id)
        assert delete_result is True
        
        # Step 10: Verify deletion
        deleted_state = frontend_state_service.get_state(session_id)
        assert deleted_state is None
    
    def test_error_handling_database_errors(self, frontend_state_service):
        """Test error handling for database errors."""
        session_id = "error_test_session_123"
        
        # Mock database error
        with patch.object(frontend_state_service.db_session, 'commit') as mock_commit:
            mock_commit.side_effect = SQLAlchemyError("Database connection failed")
            
            # Test that database errors are properly handled
            with pytest.raises(SQLAlchemyError):
                frontend_state_service.update_state(session_id, {"test": "data"})
    
    def test_data_validation(self, frontend_state_service):
        """Test data validation for state updates."""
        session_id = "validation_test_session_123"
        
        # Test with invalid data type
        with pytest.raises(ValueError, match="State data must be a dictionary"):
            frontend_state_service.update_state(session_id, "invalid_data")
        
        # Test with None data
        with pytest.raises(ValueError, match="State data must be a dictionary"):
            frontend_state_service.update_state(session_id, None)
    
    def test_performance_with_large_state(self, frontend_state_service):
        """Test performance with large state objects."""
        session_id = "performance_test_session_123"
        user_id = "user_performance_456"
        
        # Create large state object
        large_state = {
            "large_array": [{"id": i, "data": f"item_{i}"} for i in range(1000)],
            "nested_object": {
                "level1": {
                    "level2": {
                        "level3": {
                            "level4": {
                                "level5": {"deep_value": "test"}
                            }
                        }
                    }
                }
            },
            "query_history": [
                {
                    "query": f"Test query {i}",
                    "timestamp": "2024-12-28T10:00:00Z",
                    "results": [{"id": j, "title": f"Result {j}"} for j in range(50)]
                }
                for i in range(100)
            ]
        }
        
        # Test save performance
        start_time = datetime.now()
        result = frontend_state_service.update_state(session_id, large_state, user_id)
        save_time = (datetime.now() - start_time).total_seconds()
        
        assert result is not None
        assert save_time < 1.0  # Should complete within 1 second
        
        # Test retrieve performance
        start_time = datetime.now()
        retrieved_state = frontend_state_service.get_state(session_id)
        retrieve_time = (datetime.now() - start_time).total_seconds()
        
        assert retrieved_state is not None
        assert retrieve_time < 1.0  # Should complete within 1 second
        
        # Verify data integrity
        assert len(retrieved_state["current_view_state"]["large_array"]) == 1000
        assert len(retrieved_state["current_view_state"]["query_history"]) == 100
        assert retrieved_state["current_view_state"]["nested_object"]["level1"]["level2"]["level3"]["level4"]["level5"]["deep_value"] == "test"


def run_integration_tests():
    """Run all integration tests."""
    print("🚀 Running Frontend State PostgreSQL Integration Tests")
    print("=" * 60)
    
    # Run tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short"
    ])


if __name__ == "__main__":
    run_integration_tests() 