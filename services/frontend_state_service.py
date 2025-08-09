"""
Frontend State Service - Universal Knowledge Platform

This service manages frontend UI states in PostgreSQL, providing seamless
synchronization between backend AI flows and frontend UI components.

Features:
- Session-based state management
- CRUD operations for UI states
- Zero-cost DB sync between backend and frontend
- Automatic state persistence
- User association support

API Endpoints:
- GET /api/state/{session_id} - Get current state
- PUT /api/state/{session_id} - Update state
- DELETE /api/state/{session_id} - Clear state

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import json

from shared.models.frontend_state import FrontendState
from shared.core.unified_logging import get_logger

logger = get_logger(__name__)


class FrontendStateService:
    """
    Service for managing frontend UI states in PostgreSQL.

    This service provides CRUD operations for frontend states,
    enabling seamless synchronization between backend AI flows
    and frontend UI components.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the frontend state service.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session
        logger.info("FrontendStateService initialized")

    def get_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the current UI state for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            Current UI state as dictionary, or None if not found

        Raises:
            SQLAlchemyError: Database error
        """
        try:
            logger.debug(f"Fetching state for session: {session_id}")

            # Query the database for the session state
            state_record = (
                self.db_session.query(FrontendState)
                .filter(FrontendState.session_id == session_id)
                .first()
            )

            if not state_record:
                logger.debug(f"No state found for session: {session_id}")
                return None

            # Convert to dictionary format
            state_data = state_record.to_dict()
            logger.debug(
                f"Retrieved state for session {session_id}: {len(state_data.get('current_view_state', {}))} keys"
            )

            return state_data

        except SQLAlchemyError as e:
            logger.error(
                f"Database error while fetching state for session {session_id}: {e}"
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error while fetching state for session {session_id}: {e}"
            )
            raise

    def update_state(
        self, session_id: str, state_data: Dict[str, Any], user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update UI state for a session.

        Args:
            session_id: Unique session identifier
            state_data: New UI state data
            user_id: Associated user ID (optional)

        Returns:
            Updated state data

        Raises:
            ValueError: Invalid state data
            SQLAlchemyError: Database error
        """
        try:
            logger.debug(f"Updating state for session: {session_id}")

            if not isinstance(state_data, dict):
                raise ValueError("State data must be a dictionary")

            # Check if state record exists
            state_record = (
                self.db_session.query(FrontendState)
                .filter(FrontendState.session_id == session_id)
                .first()
            )

            if state_record:
                # Update existing record
                logger.debug(f"Updating existing state for session: {session_id}")
                state_record.update_state(state_data)
                if user_id:
                    state_record.user_id = user_id
            else:
                # Create new record
                logger.debug(f"Creating new state for session: {session_id}")
                state_record = FrontendState(
                    session_id=session_id,
                    current_view_state=state_data,
                    user_id=user_id,
                )
                self.db_session.add(state_record)

            # Commit changes
            self.db_session.commit()

            # Return updated state
            updated_state = state_record.to_dict()
            logger.debug(
                f"Successfully updated state for session {session_id}: {len(updated_state.get('current_view_state', {}))} keys"
            )

            return updated_state

        except SQLAlchemyError as e:
            logger.error(
                f"Database error while updating state for session {session_id}: {e}"
            )
            self.db_session.rollback()
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error while updating state for session {session_id}: {e}"
            )
            self.db_session.rollback()
            raise

    def clear_state(self, session_id: str) -> bool:
        """
        Clear frontend session state on logout.

        Args:
            session_id: Unique session identifier

        Returns:
            True if state was cleared, False if not found

        Raises:
            SQLAlchemyError: Database error
        """
        try:
            logger.debug(f"Clearing state for session: {session_id}")

            # Find the state record
            state_record = (
                self.db_session.query(FrontendState)
                .filter(FrontendState.session_id == session_id)
                .first()
            )

            if not state_record:
                logger.debug(f"No state found to clear for session: {session_id}")
                return False

            # Clear the state
            state_record.clear_state()
            self.db_session.commit()

            logger.debug(f"Successfully cleared state for session: {session_id}")
            return True

        except SQLAlchemyError as e:
            logger.error(
                f"Database error while clearing state for session {session_id}: {e}"
            )
            self.db_session.rollback()
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error while clearing state for session {session_id}: {e}"
            )
            self.db_session.rollback()
            raise

    def delete_state(self, session_id: str) -> bool:
        """
        Delete the entire state record for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            True if state was deleted, False if not found

        Raises:
            SQLAlchemyError: Database error
        """
        try:
            logger.debug(f"Deleting state for session: {session_id}")

            # Find and delete the state record
            state_record = (
                self.db_session.query(FrontendState)
                .filter(FrontendState.session_id == session_id)
                .first()
            )

            if not state_record:
                logger.debug(f"No state found to delete for session: {session_id}")
                return False

            # Delete the record
            self.db_session.delete(state_record)
            self.db_session.commit()

            logger.debug(f"Successfully deleted state for session: {session_id}")
            return True

        except SQLAlchemyError as e:
            logger.error(
                f"Database error while deleting state for session {session_id}: {e}"
            )
            self.db_session.rollback()
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error while deleting state for session {session_id}: {e}"
            )
            self.db_session.rollback()
            raise

    def get_states_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all states for a specific user.

        Args:
            user_id: User identifier

        Returns:
            List of state dictionaries for the user

        Raises:
            SQLAlchemyError: Database error
        """
        try:
            logger.debug(f"Fetching states for user: {user_id}")

            # Query all states for the user
            state_records = (
                self.db_session.query(FrontendState)
                .filter(FrontendState.user_id == user_id)
                .all()
            )

            # Convert to dictionary format
            states = [record.to_dict() for record in state_records]
            logger.debug(f"Retrieved {len(states)} states for user {user_id}")

            return states

        except SQLAlchemyError as e:
            logger.error(
                f"Database error while fetching states for user {user_id}: {e}"
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error while fetching states for user {user_id}: {e}"
            )
            raise

    def get_state_value(self, session_id: str, key: str, default: Any = None) -> Any:
        """
        Get a specific value from the current view state.

        Args:
            session_id: Unique session identifier
            key: State key to retrieve
            default: Default value if key doesn't exist

        Returns:
            Value associated with the key, or default if not found
        """
        try:
            state_data = self.get_state(session_id)
            if not state_data:
                return default

            return state_data.get("current_view_state", {}).get(key, default)

        except Exception as e:
            logger.error(
                f"Error getting state value for session {session_id}, key {key}: {e}"
            )
            return default

    def set_state_value(
        self, session_id: str, key: str, value: Any, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Set a specific value in the current view state.

        Args:
            session_id: Unique session identifier
            key: State key to set
            value: Value to store
            user_id: Associated user ID (optional)

        Returns:
            Updated state data
        """
        try:
            # Get current state record
            state_record = (
                self.db_session.query(FrontendState)
                .filter(FrontendState.session_id == session_id)
                .first()
            )

            if state_record:
                # Debug: Check current state before update
                print(
                    f"DEBUG: Before set_state_value - current_view_state: {state_record.current_view_state}"
                )

                # Use the model's set_state_value method
                state_record.set_state_value(key, value)

                # Debug: Check state after update
                print(
                    f"DEBUG: After set_state_value - current_view_state: {state_record.current_view_state}"
                )

                if user_id:
                    state_record.user_id = user_id
            else:
                # Create new record with the single key-value pair
                state_record = FrontendState(
                    session_id=session_id,
                    current_view_state={key: value},
                    user_id=user_id,
                )
                self.db_session.add(state_record)

            # Commit changes
            self.db_session.commit()

            # Debug: Check state after commit
            print(
                f"DEBUG: After commit - current_view_state: {state_record.current_view_state}"
            )

            # Return updated state
            return state_record.to_dict()

        except Exception as e:
            logger.error(
                f"Error setting state value for session {session_id}, key {key}: {e}"
            )
            raise

    def merge_state(
        self, session_id: str, new_state: Dict[str, Any], user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Merge new state data with existing state.

        Args:
            session_id: Unique session identifier
            new_state: New state data to merge
            user_id: Associated user ID (optional)

        Returns:
            Merged state data
        """
        try:
            # Get current state record
            state_record = (
                self.db_session.query(FrontendState)
                .filter(FrontendState.session_id == session_id)
                .first()
            )

            if state_record:
                # Use the model's update_state method for proper merging
                state_record.update_state(new_state)
                if user_id:
                    state_record.user_id = user_id
            else:
                # Create new record with the merged state
                state_record = FrontendState(
                    session_id=session_id, current_view_state=new_state, user_id=user_id
                )
                self.db_session.add(state_record)

            # Commit changes
            self.db_session.commit()

            # Return updated state
            return state_record.to_dict()

        except Exception as e:
            logger.error(f"Error merging state for session {session_id}: {e}")
            raise

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information without the full state data.

        Args:
            session_id: Unique session identifier

        Returns:
            Session info (session_id, user_id, last_updated) or None
        """
        try:
            state_record = (
                self.db_session.query(FrontendState)
                .filter(FrontendState.session_id == session_id)
                .first()
            )

            if not state_record:
                return None

            return {
                "session_id": state_record.session_id,
                "user_id": state_record.user_id,
                "last_updated": (
                    state_record.last_updated.isoformat()
                    if state_record.last_updated
                    else None
                ),
                "state_keys_count": (
                    len(state_record.current_view_state)
                    if state_record.current_view_state
                    else 0
                ),
            }

        except SQLAlchemyError as e:
            logger.error(
                f"Database error while getting session info for {session_id}: {e}"
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error while getting session info for {session_id}: {e}"
            )
            raise
