"""
Memory Manager PostgreSQL - Universal Knowledge Platform
PostgreSQL-based session memory management using JSONB fields.

This module implements a memory manager that uses PostgreSQL JSONB
fields to store session memory, replacing Redis for zero-budget persistence.

Features:
- PostgreSQL JSONB storage for session memory
- Automatic TTL-like behavior with manual cleanup
- Efficient querying with GIN indexes
- Session context management for orchestrator integration
- Zero-budget alternative to Redis

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    1.0.0 (2024-12-28)
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from contextlib import asynccontextmanager

from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from shared.core.database import DatabaseService, get_database_service
from shared.models.session_memory import SessionMemory

logger = logging.getLogger(__name__)


class MemoryManagerPostgres:
    """
    PostgreSQL-based memory manager for session memory.
    
    Manages session memory using PostgreSQL JSONB fields with
    automatic TTL-like behavior and efficient querying.
    """
    
    def __init__(self, database_service: Optional[DatabaseService] = None):
        """
        Initialize the PostgreSQL memory manager.
        
        Args:
            database_service: Database service instance (auto-initialized if None)
        """
        self.db_service = database_service or get_database_service()
        self.default_ttl_hours = 24  # 1 day default TTL
        logger.info("MemoryManagerPostgres initialized")
    
    async def add_to_memory(
        self, 
        session_id: str, 
        query: str, 
        answer: str,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Add a query-answer interaction to session memory.
        
        Args:
            session_id: Unique session identifier
            query: User's query
            answer: System's response
            timestamp: Optional timestamp (defaults to current time)
            
        Returns:
            True if successfully added, False otherwise
        """
        try:
            with self.db_service.get_session() as session:
                # Get or create session memory
                session_memory = await self._get_or_create_session_memory(
                    session, session_id
                )
                
                # Add the interaction
                session_memory.add_interaction(query, answer, timestamp)
                
                # Save to database
                session.commit()
                
                logger.debug(f"Added interaction to session {session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to add interaction to session {session_id}: {e}")
            return False
    
    async def get_context(self, session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve the last N interactions for a session.
        
        Args:
            session_id: Unique session identifier
            limit: Maximum number of interactions to return
            
        Returns:
            List of recent interactions sorted by timestamp (newest first)
        """
        try:
            with self.db_service.get_session() as session:
                # Get session memory
                session_memory = await self._get_session_memory(session, session_id)
                
                if not session_memory:
                    return []
                
                # Remove expired interactions (TTL-like behavior)
                expired_count = session_memory.remove_expired_interactions(
                    self.default_ttl_hours
                )
                
                if expired_count > 0:
                    session.commit()
                    logger.debug(f"Removed {expired_count} expired interactions from session {session_id}")
                
                # Get recent interactions
                recent_interactions = session_memory.get_recent_interactions(limit)
                
                logger.debug(f"Retrieved {len(recent_interactions)} interactions for session {session_id}")
                return recent_interactions
                
        except Exception as e:
            logger.error(f"Failed to get context for session {session_id}: {e}")
            return []
    
    async def clear_memory(self, session_id: str) -> bool:
        """
        Delete the session record from the table.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            True if successfully deleted, False otherwise
        """
        try:
            with self.db_service.get_session() as session:
                # Delete session memory
                result = session.execute(
                    delete(SessionMemory).where(SessionMemory.session_id == session_id)
                )
                session.commit()
                
                deleted_count = result.rowcount
                if deleted_count > 0:
                    logger.info(f"Cleared memory for session {session_id}")
                    return True
                else:
                    logger.debug(f"No session memory found for {session_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to clear memory for session {session_id}: {e}")
            return False
    
    async def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Dictionary with session statistics
        """
        try:
            with self.db_service.get_session() as session:
                session_memory = await self._get_session_memory(session, session_id)
                
                if not session_memory:
                    return {
                        "session_id": session_id,
                        "exists": False,
                        "history_length": 0,
                        "last_updated": None
                    }
                
                return {
                    "session_id": session_id,
                    "exists": True,
                    "history_length": len(session_memory.history),
                    "last_updated": session_memory.updated_at.isoformat() if session_memory.updated_at else None
                }
                
        except Exception as e:
            logger.error(f"Failed to get stats for session {session_id}: {e}")
            return {
                "session_id": session_id,
                "exists": False,
                "history_length": 0,
                "last_updated": None,
                "error": str(e)
            }
    
    async def cleanup_expired_sessions(self, max_age_hours: Optional[int] = None) -> int:
        """
        Clean up sessions that haven't been updated for the specified time.
        
        Args:
            max_age_hours: Maximum age in hours (defaults to default_ttl_hours)
            
        Returns:
            Number of sessions cleaned up
        """
        if max_age_hours is None:
            max_age_hours = self.default_ttl_hours
        
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
            
            with self.db_service.get_session() as session:
                # Delete sessions older than cutoff time
                result = session.execute(
                    delete(SessionMemory).where(
                        SessionMemory.updated_at < cutoff_time
                    )
                )
                session.commit()
                
                deleted_count = result.rowcount
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired sessions")
                
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            return 0
    
    async def get_all_sessions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all active sessions with their statistics.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of session statistics
        """
        try:
            with self.db_service.get_session() as session:
                # Query all sessions with basic stats
                query = select(
                    SessionMemory.session_id,
                    SessionMemory.updated_at,
                    func.jsonb_array_length(SessionMemory.history).label("history_length")
                ).order_by(SessionMemory.updated_at.desc()).limit(limit)
                
                result = session.execute(query)
                sessions = []
                
                for row in result:
                    sessions.append({
                        "session_id": row.session_id,
                        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                        "history_length": row.history_length or 0
                    })
                
                return sessions
                
        except Exception as e:
            logger.error(f"Failed to get all sessions: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check of the memory manager.
        
        Returns:
            Dictionary with health status and statistics
        """
        try:
            with self.db_service.get_session() as session:
                # Check if we can query the table
                result = session.execute(select(func.count(SessionMemory.session_id)))
                total_sessions = result.scalar() or 0
                
                # Get recent sessions count
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
                result = session.execute(
                    select(func.count(SessionMemory.session_id)).where(
                        SessionMemory.updated_at >= cutoff_time
                    )
                )
                recent_sessions = result.scalar() or 0
                
                return {
                    "status": "healthy",
                    "total_sessions": total_sessions,
                    "recent_sessions": recent_sessions,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _get_or_create_session_memory(
        self, 
        session: Session, 
        session_id: str
    ) -> SessionMemory:
        """
        Get existing session memory or create a new one.
        
        Args:
            session: Database session
            session_id: Unique session identifier
            
        Returns:
            SessionMemory instance
        """
        # Try to get existing session memory
        session_memory = await self._get_session_memory(session, session_id)
        
        if not session_memory:
            # Create new session memory
            session_memory = SessionMemory(session_id=session_id)
            session.add(session_memory)
            logger.debug(f"Created new session memory for {session_id}")
        
        return session_memory
    
    async def _get_session_memory(
        self, 
        session: Session, 
        session_id: str
    ) -> Optional[SessionMemory]:
        """
        Get session memory by session ID.
        
        Args:
            session: Database session
            session_id: Unique session identifier
            
        Returns:
            SessionMemory instance or None if not found
        """
        result = session.execute(
            select(SessionMemory).where(SessionMemory.session_id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # No cleanup needed for database connections
        pass 