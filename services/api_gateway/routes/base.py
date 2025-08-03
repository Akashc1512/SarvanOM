"""
Base utilities for agent routes.
Provides common functionality for all agent endpoints.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import HTTPException, Depends

from ..models.responses import AgentResponse
from ..middleware import get_current_user

logger = logging.getLogger(__name__)


class AgentResponseFormatter:
    """Handles consistent response formatting for all agents."""
    
    @staticmethod
    def format_success(
        agent_id: str,
        result: Dict[str, Any],
        processing_time: float,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous"
    ) -> AgentResponse:
        """Format a successful agent response."""
        if metadata is None:
            metadata = {}
        
        metadata["user_id"] = user_id
        
        return AgentResponse(
            agent_id=agent_id,
            status="completed",
            result=result,
            processing_time=processing_time,
            metadata=metadata
        )
    
    @staticmethod
    def format_error(
        agent_id: str,
        error_message: str,
        processing_time: float,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous"
    ) -> AgentResponse:
        """Format an error response."""
        if metadata is None:
            metadata = {}
        
        metadata["user_id"] = user_id
        metadata["error"] = error_message
        
        return AgentResponse(
            agent_id=agent_id,
            status="failed",
            result={"error": error_message},
            processing_time=processing_time,
            metadata=metadata
        )


class AgentErrorHandler:
    """Handles error processing for agent operations."""
    
    @staticmethod
    def handle_agent_error(
        agent_id: str,
        error: Exception,
        operation: str,
        user_id: str = "anonymous"
    ) -> AgentResponse:
        """Handle and format agent errors."""
        error_message = f"{operation} failed: {str(error)}"
        logger.error(f"Agent {agent_id} error: {error_message}")
        
        return AgentResponseFormatter.format_error(
            agent_id=agent_id,
            error_message=error_message,
            processing_time=0.0,
            user_id=user_id
        )
    
    @staticmethod
    def validate_request(request: Dict[str, Any], required_fields: list) -> None:
        """Validate request has required fields."""
        missing_fields = [field for field in required_fields if not request.get(field)]
        
        if missing_fields:
            raise HTTPException(
                status_code=422,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )


class AgentPerformanceTracker:
    """Tracks performance metrics for agent operations."""
    
    def __init__(self):
        self.start_time: Optional[datetime] = None
    
    def start_tracking(self) -> None:
        """Start performance tracking."""
        self.start_time = datetime.now()
    
    def get_processing_time(self) -> float:
        """Get elapsed processing time."""
        if self.start_time is None:
            return 0.0
        
        return (datetime.now() - self.start_time).total_seconds()


def get_user_id(current_user) -> str:
    """Extract user ID from current user context."""
    return current_user.get("user_id", "anonymous") if current_user else "anonymous"


def create_agent_metadata(
    user_id: str,
    **additional_metadata
) -> Dict[str, Any]:
    """Create standardized metadata for agent responses."""
    metadata = {
        "user_id": user_id,
        "timestamp": datetime.now().isoformat()
    }
    metadata.update(additional_metadata)
    return metadata 