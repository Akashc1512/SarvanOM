"""
Frontend State Service Tests - Universal Knowledge Platform

This module contains comprehensive unit tests for the FrontendStateService,
ensuring proper CRUD operations, error handling, and data consistency.

Test Coverage:
- State creation and retrieval
- State updates and merging
- State clearing and deletion
- Error handling for missing sessions
- Database session mocking
- Data consistency validation

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from typing import Dict, Any, Optional

from services.frontend_state_service import FrontendStateService
from shared.models.frontend_state import FrontendState


class TestFrontendStateService:
    """Test suite for FrontendStateService."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mocked database session."""
        session = Mock(spec=Session)
        
        # Create a mock query object
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_query.all.return_value = []
        
        # Set up the session to return the mock query
        session.query.return_value = mock_query
        session.add = Mock()
        session.commit = Mock()
        session.rollback = Mock()
        session.delete = Mock()
        
        return session
    
    @pytest.fixture
    def service(self, mock_db_session):
        """Create FrontendStateService instance with mocked database."""
        return FrontendStateService(mock_db_session)
    
    @pytest.fixture
    def sample_state_data(self):
        """Sample UI state data for testing."""
        return {
            "sidebar": {
                "collapsed": False,
                "active_tab": "dashboard"
            },
            "query_history": [
                {"query": "What is AI?", "timestamp": "2024-12-28T10:00:00Z"},
                {"query": "Machine learning basics", "timestamp": "2024-12-28T10:05:00Z"}
            ],
            "current_view": {
                "page": "dashboard",
                "filters": {"category": "technology"},
                "sort_by": "relevance"
            },
            "user_preferences": {
                "theme": "dark",
                "language": "en",
                "notifications": True
            }
        }
    
    @pytest.fixture
    def mock_frontend_state(self, sample_state_data):
        """Create a mocked FrontendState instance."""
        state = Mock(spec=FrontendState)
        state.session_id = "test_session_123"
        state.user_id = "user_456"
        state.current_view_state = sample_state_data
        state.last_updated = datetime(2024, 12, 28, 10, 0, 0)
        state.to_dict.return_value = {
            "session_id": "test_session_123",
            "user_id": "user_456",
            "current_view_state": sample_state_data,
            "last_updated": "2024-12-28T10:00:00"
        }
        state.update_state = Mock()
        state.clear_state = Mock()
        return state

    def test_service_initialization(self, mock_db_session):
        """Test FrontendStateService initialization."""
        service = FrontendStateService(mock_db_session)
        assert service.db_session == mock_db_session

    def test_get_state_success(self, service, mock_frontend_state, mock_db_session):
        """Test successful state retrieval."""
        # Setup mock
        mock_query = mock_db_session.query.return_value
        mock_query.first.return_value = mock_frontend_state
        
        # Execute
        result = service.get_state("test_session_123")
        
        # Assert
        assert result is not None
        assert result["session_id"] == "test_session_123"
        assert result["user_id"] == "user_456"
        assert "current_view_state" in result
        assert "last_updated" in result
        
        # Verify database calls
        mock_db_session.query.assert_called_once_with(FrontendState)
        mock_query.filter.assert_called_once()

    def test_get_state_not_found(self, service, mock_db_session):
        """Test state retrieval when session doesn't exist."""
        # Setup mock
        mock_query = mock_db_session.query.return_value
        mock_query.first.return_value = None
        
        # Execute
        result = service.get_state("nonexistent_session")
        
        # Assert
        assert result is None
        
        # Verify database calls
        mock_db_session.query.assert_called_once_with(FrontendState)
        mock_query.filter.assert_called_once()

    def test_get_state_database_error(self, service, mock_db_session):
        """Test state retrieval with database error."""
        # Setup mock to raise exception
        mock_db_session.query.side_effect = SQLAlchemyError("Database connection failed")
        
        # Execute and assert
        with pytest.raises(SQLAlchemyError):
            service.get_state("test_session_123")

    def test_update_state_new_session(self, service, mock_db_session, sample_state_data):
        """Test updating state for a new session."""
        # Setup mock
        mock_query = mock_db_session.query.return_value
        mock_query.first.return_value = None
        mock_state = Mock(spec=FrontendState)
        mock_state.to_dict.return_value = {
            "session_id": "new_session_123",
            "user_id": "user_456",
            "current_view_state": sample_state_data,
            "last_updated": "2024-12-28T10:00:00"
        }
        
        # Execute
        result = service.update_state("new_session_123", sample_state_data, "user_456")
        
        # Assert
        assert result is not None
        assert result["session_id"] == "new_session_123"
        assert result["user_id"] == "user_456"
        
        # Verify database calls
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    def test_update_state_existing_session(self, service, mock_db_session, sample_state_data):
        """Test updating state for an existing session."""
        # Setup mock
        mock_state = Mock(spec=FrontendState)
        mock_state.to_dict.return_value = {
            "session_id": "existing_session_123",
            "user_id": "user_456",
            "current_view_state": sample_state_data,
            "last_updated": "2024-12-28T10:00:00"
        }
        mock_query = mock_db_session.query.return_value
        mock_query.first.return_value = mock_state
        
        # Execute
        result = service.update_state("existing_session_123", sample_state_data, "user_456")
        
        # Assert
        assert result is not None
        assert result["session_id"] == "existing_session_123"
        
        # Verify database calls
        mock_state.update_state.assert_called_once_with(sample_state_data)
        mock_db_session.commit.assert_called_once()

    def test_update_state_invalid_data(self, service):
        """Test updating state with invalid data."""
        # Execute and assert
        with pytest.raises(ValueError, match="State data must be a dictionary"):
            service.update_state("test_session_123", "invalid_data")

    def test_update_state_database_error(self, service, mock_db_session, sample_state_data):
        """Test updating state with database error."""
        # Setup mock to raise exception
        mock_db_session.commit.side_effect = SQLAlchemyError("Database error")
        
        # Execute and assert
        with pytest.raises(SQLAlchemyError):
            service.update_state("test_session_123", sample_state_data)
        
        # Verify rollback was called
        mock_db_session.rollback.assert_called_once()

    def test_clear_state_success(self, service, mock_db_session):
        """Test successful state clearing."""
        # Setup mock
        mock_state = Mock(spec=FrontendState)
        mock_query = mock_db_session.query.return_value
        mock_query.first.return_value = mock_state
        
        # Execute
        result = service.clear_state("test_session_123")
        
        # Assert
        assert result is True
        mock_state.clear_state.assert_called_once()
        mock_db_session.commit.assert_called_once()

    def test_clear_state_not_found(self, service, mock_db_session):
        """Test clearing state when session doesn't exist."""
        # Setup mock
        mock_query = mock_db_session.query.return_value
        mock_query.first.return_value = None
        
        # Execute
        result = service.clear_state("nonexistent_session")
        
        # Assert
        assert result is False
        mock_db_session.commit.assert_not_called()

    def test_clear_state_database_error(self, service, mock_db_session):
        """Test clearing state with database error."""
        # Setup mock to raise exception
        mock_db_session.commit.side_effect = SQLAlchemyError("Database error")
        mock_state = Mock(spec=FrontendState)
        mock_query = mock_db_session.query.return_value
        mock_query.first.return_value = mock_state
        
        # Execute and assert
        with pytest.raises(SQLAlchemyError):
            service.clear_state("test_session_123")
        
        # Verify rollback was called
        mock_db_session.rollback.assert_called_once()

    def test_delete_state_success(self, service, mock_db_session):
        """Test successful state deletion."""
        # Setup mock
        mock_state = Mock(spec=FrontendState)
        mock_query = mock_db_session.query.return_value
        mock_query.first.return_value = mock_state
        
        # Execute
        result = service.delete_state("test_session_123")
        
        # Assert
        assert result is True
        mock_db_session.delete.assert_called_once_with(mock_state)
        mock_db_session.commit.assert_called_once()

    def test_delete_state_not_found(self, service, mock_db_session):
        """Test deleting state when session doesn't exist."""
        # Setup mock
        mock_query = mock_db_session.query.return_value
        mock_query.first.return_value = None
        
        # Execute
        result = service.delete_state("nonexistent_session")
        
        # Assert
        assert result is False
        mock_db_session.delete.assert_not_called()

    def test_get_states_by_user(self, service, mock_db_session):
        """Test getting all states for a user."""
        # Setup mock
        mock_states = [
            Mock(spec=FrontendState),
            Mock(spec=FrontendState)
        ]
        mock_states[0].to_dict.return_value = {"session_id": "session_1", "user_id": "user_123"}
        mock_states[1].to_dict.return_value = {"session_id": "session_2", "user_id": "user_123"}
        mock_query = mock_db_session.query.return_value
        mock_query.all.return_value = mock_states
        
        # Execute
        result = service.get_states_by_user("user_123")
        
        # Assert
        assert len(result) == 2
        assert result[0]["session_id"] == "session_1"
        assert result[1]["session_id"] == "session_2"

    def test_get_state_value_success(self, service, mock_db_session, sample_state_data):
        """Test getting a specific state value."""
        # Setup mock
        mock_state = Mock(spec=FrontendState)
        mock_state.to_dict.return_value = {
            "session_id": "test_session_123",
            "current_view_state": sample_state_data
        }
        mock_query = mock_db_session.query.return_value
        mock_query.first.return_value = mock_state
        
        # Execute
        result = service.get_state_value("test_session_123", "sidebar")
        
        # Assert
        assert result == sample_state_data["sidebar"]

    def test_get_state_value_not_found(self, service, mock_db_session):
        """Test getting state value when session doesn't exist."""
        # Setup mock
        mock_query = mock_db_session.query.return_value
        mock_query.first.return_value = None
        
        # Execute
        result = service.get_state_value("nonexistent_session", "sidebar", "default_value")
        
        # Assert
        assert result == "default_value"

    def test_set_state_value(self, service, mock_db_session, sample_state_data):
        """Test setting a specific state value."""
        # Setup mock
        mock_state = Mock(spec=FrontendState)
        mock_state.to_dict.return_value = {
            "session_id": "test_session_123",
            "current_view_state": {**sample_state_data, "new_key": "new_value"}
        }
        mock_query = mock_db_session.query.return_value
        mock_query.first.return_value = mock_state
        
        # Execute
        result = service.set_state_value("test_session_123", "new_key", "new_value")
        
        # Assert
        assert result is not None
        assert result["session_id"] == "test_session_123"

    def test_merge_state(self, service, mock_db_session, sample_state_data):
        """Test merging state data."""
        # Setup mock
        mock_state = Mock(spec=FrontendState)
        mock_state.to_dict.return_value = {
            "session_id": "test_session_123",
            "current_view_state": {**sample_state_data, "merged_key": "merged_value"}
        }
        mock_query = mock_db_session.query.return_value
        mock_query.first.return_value = mock_state
        
        # Execute
        new_state = {"merged_key": "merged_value", "another_key": "another_value"}
        result = service.merge_state("test_session_123", new_state)
        
        # Assert
        assert result is not None
        assert result["session_id"] == "test_session_123"

    def test_get_session_info_success(self, service, mock_db_session):
        """Test getting session information."""
        # Setup mock
        mock_state = Mock(spec=FrontendState)
        mock_state.session_id = "test_session_123"
        mock_state.user_id = "user_456"
        mock_state.last_updated = datetime(2024, 12, 28, 10, 0, 0)
        mock_state.current_view_state = {"key1": "value1", "key2": "value2"}
        mock_query = mock_db_session.query.return_value
        mock_query.first.return_value = mock_state
        
        # Execute
        result = service.get_session_info("test_session_123")
        
        # Assert
        assert result is not None
        assert result["session_id"] == "test_session_123"
        assert result["user_id"] == "user_456"
        assert result["state_keys_count"] == 2

    def test_get_session_info_not_found(self, service, mock_db_session):
        """Test getting session info when session doesn't exist."""
        # Setup mock
        mock_query = mock_db_session.query.return_value
        mock_query.first.return_value = None
        
        # Execute
        result = service.get_session_info("nonexistent_session")
        
        # Assert
        assert result is None

    def test_comprehensive_state_workflow(self, service, mock_db_session, sample_state_data):
        """Test a complete state management workflow."""
        # 1. Create new state
        mock_query = mock_db_session.query.return_value
        mock_query.first.return_value = None
        mock_state = Mock(spec=FrontendState)
        mock_state.to_dict.return_value = {
            "session_id": "workflow_session",
            "user_id": "user_789",
            "current_view_state": sample_state_data,
            "last_updated": "2024-12-28T10:00:00"
        }
        
        # Create state
        result = service.update_state("workflow_session", sample_state_data, "user_789")
        assert result["session_id"] == "workflow_session"
        
        # 2. Retrieve state
        mock_query.first.return_value = mock_state
        retrieved_state = service.get_state("workflow_session")
        assert retrieved_state is not None
        assert retrieved_state["session_id"] == "workflow_session"
        
        # 3. Update specific value
        updated_state = service.set_state_value("workflow_session", "new_preference", "dark_mode")
        assert updated_state is not None
        
        # 4. Merge additional state
        additional_state = {"additional_key": "additional_value"}
        merged_state = service.merge_state("workflow_session", additional_state)
        assert merged_state is not None
        
        # 5. Get session info - need to mock the current_view_state properly
        mock_state.current_view_state = sample_state_data  # Set actual data instead of Mock
        mock_state.session_id = "workflow_session"  # Set actual session_id
        mock_state.user_id = "user_789"  # Set actual user_id
        session_info = service.get_session_info("workflow_session")
        assert session_info is not None
        assert session_info["session_id"] == "workflow_session"
        
        # 6. Clear state
        mock_query.first.return_value = mock_state
        clear_result = service.clear_state("workflow_session")
        assert clear_result is True

    def test_error_handling_edge_cases(self, service, mock_db_session):
        """Test error handling for edge cases."""
        # Test with invalid state data
        with pytest.raises(ValueError):
            service.update_state("test_session", "invalid_data")
        
        # Test database connection failure
        mock_db_session.query.side_effect = SQLAlchemyError("Connection failed")
        with pytest.raises(SQLAlchemyError):
            service.get_state("test_session")

    def test_data_consistency_validation(self, service, mock_db_session, sample_state_data):
        """Test data consistency across operations."""
        # Setup mock
        mock_state = Mock(spec=FrontendState)
        mock_state.to_dict.return_value = {
            "session_id": "consistency_test",
            "user_id": "user_123",
            "current_view_state": sample_state_data,
            "last_updated": "2024-12-28T10:00:00"
        }
        mock_query = mock_db_session.query.return_value
        mock_query.first.return_value = mock_state
        
        # Test that retrieved data matches stored data
        retrieved_state = service.get_state("consistency_test")
        assert retrieved_state["session_id"] == "consistency_test"
        assert retrieved_state["user_id"] == "user_123"
        assert "current_view_state" in retrieved_state
        assert "last_updated" in retrieved_state
        
        # Test that state structure is consistent
        assert isinstance(retrieved_state["current_view_state"], dict)
        assert "sidebar" in retrieved_state["current_view_state"]
        assert "query_history" in retrieved_state["current_view_state"]

    def test_missing_session_handling(self, service, mock_db_session):
        """Test handling of missing session cases."""
        # Setup mock to return None (session not found)
        mock_query = mock_db_session.query.return_value
        mock_query.first.return_value = None
        
        # Test get_state with missing session
        result = service.get_state("missing_session")
        assert result is None
        
        # Test get_state_value with missing session
        result = service.get_state_value("missing_session", "key", "default")
        assert result == "default"
        
        # Test get_session_info with missing session
        result = service.get_session_info("missing_session")
        assert result is None
        
        # Test clear_state with missing session
        result = service.clear_state("missing_session")
        assert result is False
        
        # Test delete_state with missing session
        result = service.delete_state("missing_session")
        assert result is False

    def test_database_session_mocking_verification(self, mock_db_session):
        """Verify that database session mocking works correctly."""
        # Test that mock session has required methods
        assert hasattr(mock_db_session, 'query')
        assert hasattr(mock_db_session, 'add')
        assert hasattr(mock_db_session, 'commit')
        assert hasattr(mock_db_session, 'rollback')
        assert hasattr(mock_db_session, 'delete')
        
        # Test that mock session methods are callable
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        # Verify method calls
        mock_db_session.query(FrontendState)
        mock_query.filter()
        mock_query.first()
        
        # Verify calls were made
        assert mock_db_session.query.called
        assert mock_query.filter.called
        assert mock_query.first.called

    def test_service_methods_return_types(self, service, mock_db_session, sample_state_data):
        """Test that service methods return correct types."""
        # Setup mock
        mock_state = Mock(spec=FrontendState)
        mock_state.to_dict.return_value = {
            "session_id": "type_test",
            "user_id": "user_123",
            "current_view_state": sample_state_data,
            "last_updated": "2024-12-28T10:00:00"
        }
        mock_query = mock_db_session.query.return_value
        mock_query.first.return_value = mock_state
        
        # Test get_state returns dict or None
        result = service.get_state("type_test")
        assert isinstance(result, dict)
        
        # Test update_state returns dict
        result = service.update_state("type_test", sample_state_data)
        assert isinstance(result, dict)
        
        # Test get_states_by_user returns list
        mock_query.all.return_value = [mock_state]
        result = service.get_states_by_user("user_123")
        assert isinstance(result, list)
        
        # Test clear_state returns bool
        result = service.clear_state("type_test")
        assert isinstance(result, bool)
        
        # Test delete_state returns bool
        result = service.delete_state("type_test")
        assert isinstance(result, bool) 