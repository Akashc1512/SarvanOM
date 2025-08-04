#!/usr/bin/env python3
"""
Memory Manager Integration Example

This module provides examples of memory manager integration.

# DEAD CODE - Candidate for deletion: This example file is not referenced anywhere in the codebase
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

from shared.core.memory_manager_postgres import MemoryManagerPostgres
from shared.core.database import get_database_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrchestratorWithMemory:
    """
    Example orchestrator that integrates with MemoryManagerPostgres.
    
    This demonstrates how to use session memory in the orchestrator
    for maintaining conversation context across multiple queries.
    """
    
    def __init__(self):
        """Initialize orchestrator with memory manager."""
        self.memory_manager = MemoryManagerPostgres()
        logger.info("OrchestratorWithMemory initialized with PostgreSQL memory manager")
    
    async def process_query(
        self, 
        query: str, 
        session_id: str, 
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a query with session memory integration.
        
        Args:
            query: User's query
            session_id: Unique session identifier
            user_context: Optional user context
            
        Returns:
            Dictionary containing response and metadata
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            logger.info(f"Processing query for session {session_id}: {query[:50]}...")
            
            # Step 1: Preload session context
            session_context = await self._preload_session_context(session_id)
            
            # Step 2: Process query with context
            response = await self._process_with_context(query, session_context, user_context)
            
            # Step 3: Update session memory
            await self._update_session_memory(session_id, query, response["answer"])
            
            # Step 4: Add metadata
            response["metadata"] = {
                "session_id": session_id,
                "context_length": len(session_context),
                "processing_time_ms": (datetime.now(timezone.utc) - start_time).total_seconds() * 1000,
                "memory_updated": True
            }
            
            logger.info(f"Query processed successfully for session {session_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query for session {session_id}: {e}")
            return {
                "answer": f"Sorry, I encountered an error: {str(e)}",
                "confidence": 0.0,
                "metadata": {
                    "session_id": session_id,
                    "error": str(e),
                    "processing_time_ms": (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                }
            }
    
    async def _preload_session_context(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Preload session context before processing query.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            List of recent interactions for context
        """
        try:
            # Get last 5 interactions for context
            context = await self.memory_manager.get_context(session_id, limit=5)
            
            logger.debug(f"Loaded {len(context)} interactions for session {session_id}")
            return context
            
        except Exception as e:
            logger.warning(f"Failed to load context for session {session_id}: {e}")
            return []
    
    async def _process_with_context(
        self, 
        query: str, 
        context: List[Dict[str, Any]], 
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process query with session context.
        
        Args:
            query: User's query
            context: Session context (recent interactions)
            user_context: Optional user context
            
        Returns:
            Dictionary containing answer and confidence
        """
        # Simulate LLM processing with context
        # In a real implementation, this would call your LLM service
        
        # Build context string
        context_str = ""
        if context:
            context_str = "\n".join([
                f"Previous Q: {interaction['query']}\nPrevious A: {interaction['answer']}"
                for interaction in context[-3:]  # Last 3 interactions
            ])
        
        # Simulate response based on context
        if "python" in query.lower():
            if context_str and "python" in context_str.lower():
                answer = "I see you're continuing our Python discussion. Python is indeed a versatile language with many applications in data science, web development, and automation."
                confidence = 0.9
            else:
                answer = "Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used in web development, data science, AI, and automation."
                confidence = 0.8
        elif "memory" in query.lower():
            answer = "Session memory allows me to remember our conversation context. I can recall previous questions and answers to provide more relevant responses."
            confidence = 0.85
        else:
            answer = f"I understand your question: '{query}'. I'm here to help with any information you need."
            confidence = 0.7
        
        return {
            "answer": answer,
            "confidence": confidence,
            "context_used": len(context)
        }
    
    async def _update_session_memory(
        self, 
        session_id: str, 
        query: str, 
        answer: str
    ) -> None:
        """
        Update session memory with new interaction.
        
        Args:
            session_id: Unique session identifier
            query: User's query
            answer: System's response
        """
        try:
            success = await self.memory_manager.add_to_memory(session_id, query, answer)
            
            if success:
                logger.debug(f"Updated session memory for {session_id}")
            else:
                logger.warning(f"Failed to update session memory for {session_id}")
                
        except Exception as e:
            logger.error(f"Error updating session memory for {session_id}: {e}")
    
    async def clear_session_memory(self, session_id: str) -> bool:
        """
        Clear memory for a specific session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            True if successfully cleared, False otherwise
        """
        try:
            success = await self.memory_manager.clear_memory(session_id)
            
            if success:
                logger.info(f"Cleared memory for session {session_id}")
            else:
                logger.warning(f"No memory found to clear for session {session_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error clearing memory for session {session_id}: {e}")
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
            stats = await self.memory_manager.get_session_stats(session_id)
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats for session {session_id}: {e}")
            return {
                "session_id": session_id,
                "exists": False,
                "error": str(e)
            }


async def demo_memory_integration():
    """Demonstrate memory manager integration with orchestrator."""
    logger.info("Starting Memory Manager PostgreSQL Integration Demo")
    
    # Initialize orchestrator
    orchestrator = OrchestratorWithMemory()
    
    # Sample session ID
    session_id = "demo_session_123"
    
    # Simulate a conversation
    queries = [
        "What is Python?",
        "How does Python compare to other languages?",
        "Can you tell me about Python packages?",
        "What are the best practices for Python development?",
        "How does session memory work in this system?"
    ]
    
    logger.info(f"Starting conversation for session: {session_id}")
    
    for i, query in enumerate(queries, 1):
        logger.info(f"\n--- Query {i} ---")
        logger.info(f"User: {query}")
        
        # Process query
        response = await orchestrator.process_query(query, session_id)
        
        logger.info(f"System: {response['answer']}")
        logger.info(f"Confidence: {response['confidence']:.2f}")
        logger.info(f"Context used: {response['metadata']['context_length']} interactions")
        
        # Small delay to simulate processing time
        await asyncio.sleep(0.5)
    
    # Get session statistics
    logger.info("\n--- Session Statistics ---")
    stats = await orchestrator.get_session_stats(session_id)
    logger.info(f"Session exists: {stats['exists']}")
    logger.info(f"History length: {stats['history_length']}")
    logger.info(f"Last updated: {stats['last_updated']}")
    
    # Demonstrate context retrieval
    logger.info("\n--- Context Retrieval Demo ---")
    memory_manager = MemoryManagerPostgres()
    context = await memory_manager.get_context(session_id, limit=3)
    
    logger.info(f"Retrieved {len(context)} recent interactions:")
    for i, interaction in enumerate(context, 1):
        logger.info(f"  {i}. Q: {interaction['query'][:50]}...")
        logger.info(f"     A: {interaction['answer'][:50]}...")
    
    # Cleanup demo session
    logger.info("\n--- Cleanup ---")
    await orchestrator.clear_session_memory(session_id)
    logger.info("Demo session memory cleared")
    
    logger.info("\nDemo completed successfully!")


async def demo_ttl_behavior():
    """Demonstrate TTL-like behavior of the memory manager."""
    logger.info("Starting TTL Behavior Demo")
    
    memory_manager = MemoryManagerPostgres()
    
    # Create sessions with different timestamps
    old_session = "old_session_demo"
    recent_session = "recent_session_demo"
    
    # Add old interaction (simulated)
    old_timestamp = datetime.now(timezone.utc) - timedelta(hours=25)
    await memory_manager.add_to_memory(
        old_session,
        "Old query",
        "Old answer",
        old_timestamp
    )
    
    # Add recent interaction
    recent_timestamp = datetime.now(timezone.utc) - timedelta(minutes=30)
    await memory_manager.add_to_memory(
        recent_session,
        "Recent query",
        "Recent answer",
        recent_timestamp
    )
    
    # Get context (should trigger pruning)
    logger.info("Getting context for old session (should trigger pruning)...")
    old_context = await memory_manager.get_context(old_session)
    logger.info(f"Old session context length: {len(old_context)}")
    
    logger.info("Getting context for recent session...")
    recent_context = await memory_manager.get_context(recent_session)
    logger.info(f"Recent session context length: {len(recent_context)}")
    
    # Cleanup
    await memory_manager.clear_memory(old_session)
    await memory_manager.clear_memory(recent_session)
    
    logger.info("TTL behavior demo completed!")


if __name__ == "__main__":
    # Run demos
    asyncio.run(demo_memory_integration())
    asyncio.run(demo_ttl_behavior()) 