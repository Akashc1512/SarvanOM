"""
Agent Repository Implementation

This module contains the repository implementation for Agent domain entities.
Handles agent configuration, state management, and agent-related data persistence.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

from .base_repository import BaseRepository, InMemoryRepository
from ..models.domain.agent import Agent, AgentType, AgentStatus

logger = logging.getLogger(__name__)


class AgentRepository(ABC):
    """Abstract interface for Agent repository operations."""

    @abstractmethod
    async def create_agent(self, agent: Agent) -> Agent:
        """Create a new agent."""
        pass

    @abstractmethod
    async def get_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by its ID."""
        pass

    @abstractmethod
    async def get_agent_by_name(self, name: str) -> Optional[Agent]:
        """Get an agent by its name."""
        pass

    @abstractmethod
    async def update_agent_config(
        self, agent_id: str, config: Dict[str, Any]
    ) -> Optional[Agent]:
        """Update agent configuration."""
        pass

    @abstractmethod
    async def update_agent_status(
        self, agent_id: str, status: AgentStatus
    ) -> Optional[Agent]:
        """Update agent status."""
        pass

    @abstractmethod
    async def get_agents_by_type(self, agent_type: AgentType) -> List[Agent]:
        """Get all agents of a specific type."""
        pass

    @abstractmethod
    async def get_active_agents(self) -> List[Agent]:
        """Get all active agents."""
        pass

    @abstractmethod
    async def update_agent_performance(
        self, agent_id: str, performance_data: Dict[str, Any]
    ) -> Optional[Agent]:
        """Update agent performance metrics."""
        pass

    @abstractmethod
    async def get_agent_statistics(
        self, agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get agent statistics."""
        pass


class AgentRepositoryImpl(AgentRepository, BaseRepository[Agent]):
    """
    Implementation of Agent repository using the base repository.

    This implementation can be extended to use different storage backends
    like PostgreSQL, MongoDB, etc.
    """

    def __init__(
        self, connection_string: Optional[str] = None, storage_type: str = "memory"
    ):
        """Initialize the agent repository."""
        super().__init__(connection_string)
        self.storage_type = storage_type

        # For now, use in-memory storage
        # TODO: Implement database-backed storage
        if storage_type == "memory":
            self._memory_store = InMemoryRepository[Agent]()

        # Agent-specific indices for faster lookups
        self._name_index: Dict[str, str] = {}  # name -> agent_id
        self._type_index: Dict[AgentType, List[str]] = {}  # type -> [agent_ids]
        self._status_index: Dict[AgentStatus, List[str]] = {}  # status -> [agent_ids]

        logger.info(f"Agent repository initialized with {storage_type} storage")

    async def create(self, entity: Agent) -> Agent:
        """Create a new agent (BaseRepository interface)."""
        return await self.create_agent(entity)

    async def get_by_id(self, entity_id: str) -> Optional[Agent]:
        """Get agent by ID (BaseRepository interface)."""
        return await self.get_agent_by_id(entity_id)

    async def update(self, entity_id: str, updates: Dict[str, Any]) -> Optional[Agent]:
        """Update agent (BaseRepository interface)."""
        # Handle specific agent updates
        if "status" in updates:
            status = updates.pop("status")
            if isinstance(status, str):
                status = AgentStatus(status)
            await self.update_agent_status(entity_id, status)

        if "config" in updates:
            config = updates.pop("config")
            await self.update_agent_config(entity_id, config)

        if "performance_data" in updates:
            performance_data = updates.pop("performance_data")
            await self.update_agent_performance(entity_id, performance_data)

        # Handle other updates
        if updates:
            if self.storage_type == "memory":
                return await self._memory_store.update(entity_id, updates)

        return await self.get_agent_by_id(entity_id)

    async def delete(self, entity_id: str) -> bool:
        """Delete agent (BaseRepository interface)."""
        if self.storage_type == "memory":
            # Also remove from indices
            agent = await self.get_agent_by_id(entity_id)
            if agent:
                await self._remove_from_indices(agent)
            return await self._memory_store.delete(entity_id)
        return False

    async def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Agent]:
        """List agents (BaseRepository interface)."""
        if self.storage_type == "memory":
            return await self._memory_store.list(filters, offset, limit)
        return []

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count agents (BaseRepository interface)."""
        if self.storage_type == "memory":
            return await self._memory_store.count(filters)
        return 0

    async def exists(self, entity_id: str) -> bool:
        """Check if agent exists (BaseRepository interface)."""
        if self.storage_type == "memory":
            return await self._memory_store.exists(entity_id)
        return False

    # Agent-specific methods

    async def create_agent(self, agent: Agent) -> Agent:
        """Create a new agent with validation and indexing."""
        try:
            # Check for duplicate name
            existing_agent = await self.get_agent_by_name(agent.name)
            if existing_agent:
                raise ValueError(f"Agent name '{agent.name}' already exists")

            # Store the agent
            if self.storage_type == "memory":
                created_agent = await self._memory_store.create(agent)
            else:
                # TODO: Implement database storage
                created_agent = agent

            # Update indices
            await self._add_to_indices(created_agent)

            self._track_operation("create_agent", success=True)
            logger.info(f"Created agent {created_agent.id} ({created_agent.name})")

            return created_agent

        except Exception as e:
            self._track_operation("create_agent", success=False)
            logger.error(f"Failed to create agent: {e}")
            raise

    async def get_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by its ID."""
        try:
            if self.storage_type == "memory":
                agent = await self._memory_store.get_by_id(agent_id)
            else:
                # TODO: Implement database retrieval
                agent = None

            self._track_operation("get_agent_by_id", success=True)
            return agent

        except Exception as e:
            self._track_operation("get_agent_by_id", success=False)
            logger.error(f"Failed to get agent {agent_id}: {e}")
            raise

    async def get_agent_by_name(self, name: str) -> Optional[Agent]:
        """Get an agent by its name."""
        try:
            agent_id = self._name_index.get(name)
            if agent_id:
                return await self.get_agent_by_id(agent_id)

            self._track_operation("get_agent_by_name", success=True)
            return None

        except Exception as e:
            self._track_operation("get_agent_by_name", success=False)
            logger.error(f"Failed to get agent by name {name}: {e}")
            raise

    async def update_agent_config(
        self, agent_id: str, config: Dict[str, Any]
    ) -> Optional[Agent]:
        """Update agent configuration."""
        try:
            agent = await self.get_agent_by_id(agent_id)
            if not agent:
                return None

            # Merge with existing config
            updated_config = {**agent.config, **config}

            # Update in storage
            if self.storage_type == "memory":
                updated_agent = await self._memory_store.update(
                    agent_id, {"config": updated_config, "updated_at": datetime.now()}
                )
            else:
                # TODO: Implement database update
                agent.config = updated_config
                agent.updated_at = datetime.now()
                updated_agent = agent

            self._track_operation("update_agent_config", success=True)
            logger.info(f"Updated config for agent {agent_id}")

            return updated_agent

        except Exception as e:
            self._track_operation("update_agent_config", success=False)
            logger.error(f"Failed to update agent config for {agent_id}: {e}")
            raise

    async def update_agent_status(
        self, agent_id: str, status: AgentStatus
    ) -> Optional[Agent]:
        """Update agent status."""
        try:
            agent = await self.get_agent_by_id(agent_id)
            if not agent:
                return None

            old_status = agent.status

            # Update in storage
            if self.storage_type == "memory":
                updated_agent = await self._memory_store.update(
                    agent_id, {"status": status, "updated_at": datetime.now()}
                )
            else:
                # TODO: Implement database update
                agent.status = status
                agent.updated_at = datetime.now()
                updated_agent = agent

            # Update status index
            if old_status != status:
                if old_status in self._status_index:
                    if agent_id in self._status_index[old_status]:
                        self._status_index[old_status].remove(agent_id)

                if status not in self._status_index:
                    self._status_index[status] = []
                self._status_index[status].append(agent_id)

            self._track_operation("update_agent_status", success=True)
            logger.info(
                f"Updated agent {agent_id} status from {old_status} to {status}"
            )

            return updated_agent

        except Exception as e:
            self._track_operation("update_agent_status", success=False)
            logger.error(f"Failed to update agent status for {agent_id}: {e}")
            raise

    async def get_agents_by_type(self, agent_type: AgentType) -> List[Agent]:
        """Get all agents of a specific type."""
        try:
            agent_ids = self._type_index.get(agent_type, [])
            agents = []

            for agent_id in agent_ids:
                agent = await self.get_agent_by_id(agent_id)
                if agent:
                    agents.append(agent)

            self._track_operation("get_agents_by_type", success=True)
            return agents

        except Exception as e:
            self._track_operation("get_agents_by_type", success=False)
            logger.error(f"Failed to get agents by type {agent_type}: {e}")
            raise

    async def get_active_agents(self) -> List[Agent]:
        """Get all active agents."""
        try:
            active_agent_ids = self._status_index.get(AgentStatus.ACTIVE, [])
            agents = []

            for agent_id in active_agent_ids:
                agent = await self.get_agent_by_id(agent_id)
                if agent:
                    agents.append(agent)

            self._track_operation("get_active_agents", success=True)
            return agents

        except Exception as e:
            self._track_operation("get_active_agents", success=False)
            logger.error(f"Failed to get active agents: {e}")
            raise

    async def update_agent_performance(
        self, agent_id: str, performance_data: Dict[str, Any]
    ) -> Optional[Agent]:
        """Update agent performance metrics."""
        try:
            agent = await self.get_agent_by_id(agent_id)
            if not agent:
                return None

            # Initialize performance history if not exists
            if not hasattr(agent, "performance_history"):
                agent.performance_history = []

            # Add timestamp to performance data
            performance_entry = {
                **performance_data,
                "timestamp": datetime.now().isoformat(),
            }

            # Add to performance history (keep last 100 entries)
            performance_history = getattr(agent, "performance_history", [])
            performance_history.append(performance_entry)
            if len(performance_history) > 100:
                performance_history = performance_history[-100:]

            # Update in storage
            if self.storage_type == "memory":
                updated_agent = await self._memory_store.update(
                    agent_id,
                    {
                        "performance_history": performance_history,
                        "last_performance_update": datetime.now(),
                        "updated_at": datetime.now(),
                    },
                )
            else:
                # TODO: Implement database update
                agent.performance_history = performance_history
                agent.last_performance_update = datetime.now()
                agent.updated_at = datetime.now()
                updated_agent = agent

            self._track_operation("update_agent_performance", success=True)
            logger.info(f"Updated performance data for agent {agent_id}")

            return updated_agent

        except Exception as e:
            self._track_operation("update_agent_performance", success=False)
            logger.error(f"Failed to update agent performance for {agent_id}: {e}")
            raise

    async def get_agent_statistics(
        self, agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get agent statistics."""
        try:
            if agent_id:
                # Statistics for specific agent
                agent = await self.get_agent_by_id(agent_id)
                if not agent:
                    return {"error": f"Agent {agent_id} not found"}

                performance_history = getattr(agent, "performance_history", [])

                return {
                    "agent_id": agent_id,
                    "agent_name": agent.name,
                    "agent_type": agent.agent_type.value,
                    "status": agent.status.value,
                    "created_at": agent.created_at.isoformat(),
                    "updated_at": agent.updated_at.isoformat(),
                    "performance_entries": len(performance_history),
                    "last_performance_update": getattr(
                        agent, "last_performance_update", None
                    ),
                    "config": agent.config,
                    "timestamp": datetime.now().isoformat(),
                }

            else:
                # Overall agent statistics
                if self.storage_type == "memory":
                    all_agents = await self._memory_store.list()
                else:
                    # TODO: Implement database query
                    all_agents = []

                total_agents = len(all_agents)

                if total_agents == 0:
                    return {
                        "total_agents": 0,
                        "type_breakdown": {},
                        "status_breakdown": {},
                        "active_agents": 0,
                        "performance_summary": {},
                    }

                # Type breakdown
                type_breakdown = {}
                for agent in all_agents:
                    agent_type = agent.agent_type.value
                    type_breakdown[agent_type] = type_breakdown.get(agent_type, 0) + 1

                # Status breakdown
                status_breakdown = {}
                for agent in all_agents:
                    status = agent.status.value
                    status_breakdown[status] = status_breakdown.get(status, 0) + 1

                # Active agents
                active_agents = status_breakdown.get(AgentStatus.ACTIVE.value, 0)

                # Performance summary
                total_performance_entries = 0
                agents_with_performance = 0
                for agent in all_agents:
                    performance_history = getattr(agent, "performance_history", [])
                    if performance_history:
                        total_performance_entries += len(performance_history)
                        agents_with_performance += 1

                performance_summary = {
                    "total_performance_entries": total_performance_entries,
                    "agents_with_performance": agents_with_performance,
                    "avg_performance_entries_per_agent": (
                        total_performance_entries / max(agents_with_performance, 1)
                    ),
                }

                self._track_operation("get_agent_statistics", success=True)

                return {
                    "total_agents": total_agents,
                    "type_breakdown": type_breakdown,
                    "status_breakdown": status_breakdown,
                    "active_agents": active_agents,
                    "performance_summary": performance_summary,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            self._track_operation("get_agent_statistics", success=False)
            logger.error(f"Failed to get agent statistics: {e}")
            raise

    async def _add_to_indices(self, agent: Agent):
        """Add agent to various indices for faster lookups."""
        agent_id = agent.id

        # Name index
        self._name_index[agent.name] = agent_id

        # Type index
        agent_type = agent.agent_type
        if agent_type not in self._type_index:
            self._type_index[agent_type] = []
        self._type_index[agent_type].append(agent_id)

        # Status index
        status = agent.status
        if status not in self._status_index:
            self._status_index[status] = []
        self._status_index[status].append(agent_id)

    async def _remove_from_indices(self, agent: Agent):
        """Remove agent from all indices."""
        agent_id = agent.id

        # Remove from name index
        if agent.name in self._name_index:
            del self._name_index[agent.name]

        # Remove from type index
        agent_type = agent.agent_type
        if agent_type in self._type_index and agent_id in self._type_index[agent_type]:
            self._type_index[agent_type].remove(agent_id)

        # Remove from status index
        status = agent.status
        if status in self._status_index and agent_id in self._status_index[status]:
            self._status_index[status].remove(agent_id)
