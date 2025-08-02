from shared.core.api.config import get_settings
settings = get_settings()
"""
Frontend State API Endpoints - Universal Knowledge Platform

This module provides REST API endpoints for managing frontend UI states
in PostgreSQL, enabling seamless synchronization between backend AI flows
and frontend UI components.

API Endpoints:
- GET /api/state/{session_id} - Get current state
- PUT /api/state/{session_id} - Update state
- DELETE /api/state/{session_id} - Clear state
- GET /api/state/{session_id}/info - Get session info
- GET /api/state/user/{user_id} - Get all states for user

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
import logging

from services.frontend_state_service import FrontendStateService
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_db_session() -> Session:
    """Get database session for dependency injection."""
    db_url = settings.database_url
    if not db_url:
        raise Exception("DATABASE_URL not configured")
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()

logger = logging.getLogger(__name__)

# Create router for frontend state endpoints
router = APIRouter(prefix="/api/v1/state", tags=["frontend-state"])


def get_frontend_state_service(db_session: Session = Depends(get_db_session)) -> FrontendStateService:
    """
    Dependency to get FrontendStateService instance.
    
    Args:
        db_session: Database session from dependency injection
        
    Returns:
        FrontendStateService instance
    """
    return FrontendStateService(db_session)


@router.get("/{session_id}")
async def get_state(
    session_id: str,
    service: FrontendStateService = Depends(get_frontend_state_service)
) -> Dict[str, Any]:
    """
    Get the current UI state for a session.
    
    Args:
        session_id: Unique session identifier
        service: FrontendStateService instance
        
    Returns:
        Current UI state as dictionary
        
    Raises:
        HTTPException: If session not found or database error
    """
    try:
        logger.info(f"API: Getting state for session: {session_id}")
        
        state_data = service.get_state(session_id)
        
        if state_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"State not found for session: {session_id}"
            )
        
        logger.info(f"API: Successfully retrieved state for session: {session_id}")
        return {
            "success": True,
            "data": state_data,
            "message": "State retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Error getting state for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/{session_id}")
async def update_state(
    session_id: str,
    state_data: Dict[str, Any],
    user_id: Optional[str] = None,
    service: FrontendStateService = Depends(get_frontend_state_service)
) -> Dict[str, Any]:
    """
    Update UI state for a session.
    
    Args:
        session_id: Unique session identifier
        state_data: New UI state data
        user_id: Associated user ID (optional)
        service: FrontendStateService instance
        
    Returns:
        Updated state data
        
    Raises:
        HTTPException: If invalid data or database error
    """
    try:
        logger.info(f"API: Updating state for session: {session_id}")
        
        if not isinstance(state_data, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State data must be a dictionary"
            )
        
        updated_state = service.update_state(session_id, state_data, user_id)
        
        logger.info(f"API: Successfully updated state for session: {session_id}")
        return {
            "success": True,
            "data": updated_state,
            "message": "State updated successfully"
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"API: Invalid data for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"API: Error updating state for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{session_id}")
async def clear_state(
    session_id: str,
    service: FrontendStateService = Depends(get_frontend_state_service)
) -> Dict[str, Any]:
    """
    Clear frontend session state on logout.
    
    Args:
        session_id: Unique session identifier
        service: FrontendStateService instance
        
    Returns:
        Success status
        
    Raises:
        HTTPException: If database error
    """
    try:
        logger.info(f"API: Clearing state for session: {session_id}")
        
        success = service.clear_state(session_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"State not found for session: {session_id}"
            )
        
        logger.info(f"API: Successfully cleared state for session: {session_id}")
        return {
            "success": True,
            "message": "State cleared successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Error clearing state for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{session_id}/delete")
async def delete_state(
    session_id: str,
    service: FrontendStateService = Depends(get_frontend_state_service)
) -> Dict[str, Any]:
    """
    Delete the entire state record for a session.
    
    Args:
        session_id: Unique session identifier
        service: FrontendStateService instance
        
    Returns:
        Success status
        
    Raises:
        HTTPException: If database error
    """
    try:
        logger.info(f"API: Deleting state for session: {session_id}")
        
        success = service.delete_state(session_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"State not found for session: {session_id}"
            )
        
        logger.info(f"API: Successfully deleted state for session: {session_id}")
        return {
            "success": True,
            "message": "State deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Error deleting state for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{session_id}/info")
async def get_session_info(
    session_id: str,
    service: FrontendStateService = Depends(get_frontend_state_service)
) -> Dict[str, Any]:
    """
    Get session information without the full state data.
    
    Args:
        session_id: Unique session identifier
        service: FrontendStateService instance
        
    Returns:
        Session information
        
    Raises:
        HTTPException: If session not found or database error
    """
    try:
        logger.info(f"API: Getting session info for session: {session_id}")
        
        session_info = service.get_session_info(session_id)
        
        if session_info is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {session_id}"
            )
        
        logger.info(f"API: Successfully retrieved session info for session: {session_id}")
        return {
            "success": True,
            "data": session_info,
            "message": "Session info retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Error getting session info for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/user/{user_id}")
async def get_states_by_user(
    user_id: str,
    service: FrontendStateService = Depends(get_frontend_state_service)
) -> Dict[str, Any]:
    """
    Get all states for a specific user.
    
    Args:
        user_id: User identifier
        service: FrontendStateService instance
        
    Returns:
        List of state dictionaries for the user
        
    Raises:
        HTTPException: If database error
    """
    try:
        logger.info(f"API: Getting states for user: {user_id}")
        
        states = service.get_states_by_user(user_id)
        
        logger.info(f"API: Successfully retrieved {len(states)} states for user: {user_id}")
        return {
            "success": True,
            "data": states,
            "count": len(states),
            "message": f"Retrieved {len(states)} states for user"
        }
        
    except Exception as e:
        logger.error(f"API: Error getting states for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{session_id}/value/{key}")
async def get_state_value(
    session_id: str,
    key: str,
    default: Optional[str] = None,
    service: FrontendStateService = Depends(get_frontend_state_service)
) -> Dict[str, Any]:
    """
    Get a specific value from the current view state.
    
    Args:
        session_id: Unique session identifier
        key: State key to retrieve
        default: Default value if key doesn't exist
        service: FrontendStateService instance
        
    Returns:
        Value associated with the key
        
    Raises:
        HTTPException: If database error
    """
    try:
        logger.info(f"API: Getting state value for session {session_id}, key {key}")
        
        value = service.get_state_value(session_id, key, default)
        
        logger.info(f"API: Successfully retrieved state value for session {session_id}, key {key}")
        return {
            "success": True,
            "data": {
                "session_id": session_id,
                "key": key,
                "value": value
            },
            "message": "State value retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"API: Error getting state value for session {session_id}, key {key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/{session_id}/value/{key}")
async def set_state_value(
    session_id: str,
    key: str,
    value: Any,
    user_id: Optional[str] = None,
    service: FrontendStateService = Depends(get_frontend_state_service)
) -> Dict[str, Any]:
    """
    Set a specific value in the current view state.
    
    Args:
        session_id: Unique session identifier
        key: State key to set
        value: Value to store
        user_id: Associated user ID (optional)
        service: FrontendStateService instance
        
    Returns:
        Updated state data
        
    Raises:
        HTTPException: If database error
    """
    try:
        logger.info(f"API: Setting state value for session {session_id}, key {key}")
        
        updated_state = service.set_state_value(session_id, key, value, user_id)
        
        logger.info(f"API: Successfully set state value for session {session_id}, key {key}")
        return {
            "success": True,
            "data": updated_state,
            "message": "State value set successfully"
        }
        
    except Exception as e:
        logger.error(f"API: Error setting state value for session {session_id}, key {key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/{session_id}/merge")
async def merge_state(
    session_id: str,
    new_state: Dict[str, Any],
    user_id: Optional[str] = None,
    service: FrontendStateService = Depends(get_frontend_state_service)
) -> Dict[str, Any]:
    """
    Merge new state data with existing state.
    
    Args:
        session_id: Unique session identifier
        new_state: New state data to merge
        user_id: Associated user ID (optional)
        service: FrontendStateService instance
        
    Returns:
        Merged state data
        
    Raises:
        HTTPException: If database error
    """
    try:
        logger.info(f"API: Merging state for session: {session_id}")
        
        if not isinstance(new_state, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New state data must be a dictionary"
            )
        
        merged_state = service.merge_state(session_id, new_state, user_id)
        
        logger.info(f"API: Successfully merged state for session: {session_id}")
        return {
            "success": True,
            "data": merged_state,
            "message": "State merged successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Error merging state for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        ) 