"""
Agent Coordinator Service

This module coordinates between different agents and manages agent lifecycle.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from ...models.domain.agent import Agent, AgentType, AgentStatus
from .agent_factory import AgentFactory

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """Coordinates between different agents and manages agent lifecycle."""
    
    def __init__(self):
        self.agent_factory = AgentFactory()
        self.active_agents: Dict[str, Agent] = {}
        self.agent_pool: Dict[AgentType, List[Agent]] = {}
        self.agent_stats: Dict[str, Dict[str, Any]] = {}
    
    async def get_agent(self, agent_type: AgentType) -> Agent:
        """Get an available agent of the specified type."""
        try:
            # Check if we have available agents in the pool
            if agent_type in self.agent_pool and self.agent_pool[agent_type]:
                for agent in self.agent_pool[agent_type]:
                    if agent.is_available():
                        return agent
            
            # Create new agent if none available
            agent = await self._create_agent(agent_type)
            return agent
            
        except Exception as e:
            logger.error(f"Error getting agent {agent_type}: {e}", exc_info=True)
            raise
    
    async def _create_agent(self, agent_type: AgentType) -> Agent:
        """Create a new agent of the specified type."""
        try:
            agent = await self.agent_factory.create_agent(agent_type)
            
            # Add to active agents
            self.active_agents[agent.id] = agent
            
            # Add to pool
            if agent_type not in self.agent_pool:
                self.agent_pool[agent_type] = []
            self.agent_pool[agent_type].append(agent)
            
            # Initialize stats
            self.agent_stats[agent.id] = {
                "created_at": datetime.now(),
                "total_tasks": 0,
                "successful_tasks": 0,
                "failed_tasks": 0,
                "total_processing_time": 0.0
            }
            
            logger.info(f"Created agent {agent.id} of type {agent_type}")
            return agent
            
        except Exception as e:
            logger.error(f"Error creating agent {agent_type}: {e}", exc_info=True)
            raise
    
    async def release_agent(self, agent_id: str):
        """Release an agent back to the pool."""
        try:
            if agent_id in self.active_agents:
                agent = self.active_agents[agent_id]
                agent.complete_task()
                
                logger.debug(f"Released agent {agent_id}")
                
        except Exception as e:
            logger.error(f"Error releasing agent {agent_id}: {e}", exc_info=True)
    
    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent."""
        try:
            if agent_id not in self.active_agents:
                return None
            
            agent = self.active_agents[agent_id]
            stats = self.agent_stats.get(agent_id, {})
            
            return {
                "agent_id": agent_id,
                "agent_type": agent.agent_type.value,
                "status": agent.status.value,
                "current_task": agent.current_task,
                "created_at": stats.get("created_at"),
                "total_tasks": stats.get("total_tasks", 0),
                "successful_tasks": stats.get("successful_tasks", 0),
                "failed_tasks": stats.get("failed_tasks", 0),
                "avg_processing_time": (
                    stats.get("total_processing_time", 0.0) / max(stats.get("total_tasks", 1), 1)
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting agent status {agent_id}: {e}", exc_info=True)
            return None
    
    async def get_all_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        try:
            status = {}
            for agent_id in self.active_agents:
                agent_status = await self.get_agent_status(agent_id)
                if agent_status:
                    status[agent_id] = agent_status
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting all agent status: {e}", exc_info=True)
            return {}
    
    async def track_agent_task(
        self, 
        agent_id: str, 
        task_id: str, 
        processing_time: float, 
        success: bool
    ):
        """Track agent task completion."""
        try:
            if agent_id in self.agent_stats:
                stats = self.agent_stats[agent_id]
                stats["total_tasks"] += 1
                stats["total_processing_time"] += processing_time
                
                if success:
                    stats["successful_tasks"] += 1
                else:
                    stats["failed_tasks"] += 1
                
                logger.debug(f"Tracked task for agent {agent_id}: success={success}, time={processing_time}s")
                
        except Exception as e:
            logger.error(f"Error tracking agent task: {e}", exc_info=True)
    
    async def cleanup_inactive_agents(self) -> int:
        """Clean up inactive agents."""
        try:
            cleaned_count = 0
            agents_to_remove = []
            
            for agent_id, agent in self.active_agents.items():
                # Remove agents that have been inactive for too long
                if agent.status == AgentStatus.ERROR:
                    agents_to_remove.append(agent_id)
                    cleaned_count += 1
                
                # Remove agents that haven't been used for a long time
                stats = self.agent_stats.get(agent_id, {})
                created_at = stats.get("created_at")
                if created_at:
                    age = (datetime.now() - created_at).total_seconds()
                    if age > 3600:  # 1 hour
                        agents_to_remove.append(agent_id)
                        cleaned_count += 1
            
            # Remove agents
            for agent_id in agents_to_remove:
                await self._remove_agent(agent_id)
            
            logger.info(f"Cleaned up {cleaned_count} inactive agents")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up inactive agents: {e}", exc_info=True)
            return 0
    
    async def _remove_agent(self, agent_id: str):
        """Remove an agent from the system."""
        try:
            if agent_id in self.active_agents:
                agent = self.active_agents[agent_id]
                
                # Remove from active agents
                del self.active_agents[agent_id]
                
                # Remove from pool
                if agent.agent_type in self.agent_pool:
                    self.agent_pool[agent.agent_type] = [
                        a for a in self.agent_pool[agent.agent_type] 
                        if a.id != agent_id
                    ]
                
                # Remove stats
                if agent_id in self.agent_stats:
                    del self.agent_stats[agent_id]
                
                logger.info(f"Removed agent {agent_id}")
                
        except Exception as e:
            logger.error(f"Error removing agent {agent_id}: {e}", exc_info=True)
    
    def get_agent_pool_stats(self) -> Dict[str, Any]:
        """Get statistics about the agent pool."""
        try:
            stats = {
                "total_agents": len(self.active_agents),
                "agents_by_type": {},
                "available_agents": 0,
                "busy_agents": 0,
                "error_agents": 0
            }
            
            # Count by type and status
            for agent in self.active_agents.values():
                agent_type = agent.agent_type.value
                if agent_type not in stats["agents_by_type"]:
                    stats["agents_by_type"][agent_type] = {
                        "total": 0,
                        "available": 0,
                        "busy": 0,
                        "error": 0
                    }
                
                stats["agents_by_type"][agent_type]["total"] += 1
                
                if agent.status == AgentStatus.IDLE:
                    stats["agents_by_type"][agent_type]["available"] += 1
                    stats["available_agents"] += 1
                elif agent.status == AgentStatus.BUSY:
                    stats["agents_by_type"][agent_type]["busy"] += 1
                    stats["busy_agents"] += 1
                elif agent.status == AgentStatus.ERROR:
                    stats["agents_by_type"][agent_type]["error"] += 1
                    stats["error_agents"] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting agent pool stats: {e}", exc_info=True)
            return {} 