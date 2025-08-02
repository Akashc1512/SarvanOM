"""
Frontend State Model - Universal Knowledge Platform

This module defines the SQLAlchemy model for storing frontend UI states
in PostgreSQL, enabling seamless state synchronization between backend
AI flows and frontend UI components.

Features:
- Session-based state management
- JSON storage for flexible UI state
- User association for multi-user support
- Automatic timestamp tracking
- Zero-cost DB sync between backend and frontend

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

from sqlalchemy import Column, String, JSON, DateTime, Index, Text
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Dict, Any, Optional
import json

Base = declarative_base()


class FrontendState(Base):
    """
    SQLAlchemy model for storing frontend UI states in PostgreSQL.
    
    This table enables seamless state synchronization between backend
    AI flows and frontend UI components, providing a single source
    of truth for UI state management.
    """
    
    __tablename__ = 'frontend_states'
    
    # Primary key - session identifier
    session_id = Column(String(255), primary_key=True, nullable=False, 
                       comment='Unique session identifier')
    
    # User association
    user_id = Column(String(255), nullable=True, 
                    comment='Associated user ID (optional for anonymous sessions)')
    
    # UI state storage as JSON
    current_view_state = Column(JSON, nullable=False, default={},
                              comment='Current UI state as JSON object')
    
    # Timestamp tracking
    last_updated = Column(DateTime(timezone=True), server_default=func.now(),
                         onupdate=func.now(), nullable=False,
                         comment='Last update timestamp')
    
    # Index for performance
    __table_args__ = (
        Index('idx_frontend_states_user_id', 'user_id'),
        Index('idx_frontend_states_last_updated', 'last_updated'),
    )
    
    def __init__(self, session_id: str, current_view_state: Dict[str, Any] = None, 
                 user_id: Optional[str] = None):
        """
        Initialize a new frontend state record.
        
        Args:
            session_id: Unique session identifier
            current_view_state: UI state as dictionary
            user_id: Associated user ID (optional)
        """
        self.session_id = session_id
        self.user_id = user_id
        self.current_view_state = current_view_state or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'current_view_state': self.current_view_state,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
    
    def update_state(self, new_state: Dict[str, Any]) -> None:
        """
        Update the current view state.
        
        Args:
            new_state: New UI state to merge with existing state
        """
        if not isinstance(new_state, dict):
            raise ValueError("State must be a dictionary")
        
        # Merge with existing state
        if self.current_view_state:
            self.current_view_state.update(new_state)
        else:
            self.current_view_state = new_state
        
        # Update timestamp
        self.last_updated = datetime.utcnow()
    
    def clear_state(self) -> None:
        """Clear the current view state."""
        self.current_view_state = {}
        self.last_updated = datetime.utcnow()
    
    def get_state_value(self, key: str, default: Any = None) -> Any:
        """
        Get a specific value from the current view state.
        
        Args:
            key: State key to retrieve
            default: Default value if key doesn't exist
            
        Returns:
            Value associated with the key
        """
        return self.current_view_state.get(key, default)
    
    def set_state_value(self, key: str, value: Any) -> None:
        """
        Set a specific value in the current view state.
        
        Args:
            key: State key to set
            value: Value to store
        """
        if not self.current_view_state:
            self.current_view_state = {}
        
        self.current_view_state[key] = value
        self.last_updated = datetime.utcnow()
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<FrontendState(session_id='{self.session_id}', user_id='{self.user_id}', last_updated='{self.last_updated}')>" 