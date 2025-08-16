"""
Lead Orchestrator for Agent Coordination
Coordinates between different agents in the SarvanOM platform.
"""

import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

from .base_agent import BaseAgent, AgentType, AgentResult, QueryContext

logger = logging.getLogger(__name__)


@dataclass
class OrchestrationRequest:
    """Request for agent orchestration."""
    query: str
    context: str = ""
    agent_types: List[AgentType] = None
    priority: str = "normal"
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.agent_types is None:
            self.agent_types = [AgentType.RETRIEVAL, AgentType.SYNTHESIS]
        if self.metadata is None:
            self.metadata = {}


@dataclass
class OrchestrationResult:
    """Result of agent orchestration."""
    success: bool
    results: Dict[AgentType, AgentResult]
    final_response: str
    processing_time: float
    metadata: Dict[str, Any] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class LeadOrchestrator:
    """Coordinates multiple agents to process complex queries."""
    
    def __init__(self):
        self.agents: Dict[AgentType, BaseAgent] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_agent(self, agent_type: AgentType, agent: BaseAgent):
        """Register an agent for orchestration."""
        self.agents[agent_type] = agent
        self.logger.info(f"Registered agent: {agent_type}")
    
    async def orchestrate(
        self, 
        request: OrchestrationRequest
    ) -> OrchestrationResult:
        """
        Orchestrate multiple agents to process a query.
        
        Args:
            request: OrchestrationRequest containing query and agent types
            
        Returns:
            OrchestrationResult with coordinated results
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            self.logger.info(f"Starting orchestration for query: {request.query[:100]}...")
            
            # Create query context
            context = QueryContext(
                query=request.query,
                context=request.context,
                metadata=request.metadata or {}
            )
            
            # Process with each agent type
            results = {}
            for agent_type in request.agent_types:
                if agent_type in self.agents:
                    try:
                        agent = self.agents[agent_type]
                        result = await agent.process_task(
                            task={"query": request.query, "context": request.context},
                            context=context
                        )
                        results[agent_type] = result
                        self.logger.info(f"Agent {agent_type} completed successfully")
                    except Exception as e:
                        self.logger.error(f"Agent {agent_type} failed: {e}")
                        results[agent_type] = AgentResult(
                            success=False,
                            content=f"Agent {agent_type} failed: {e}",
                            metadata={"error": str(e)}
                        )
                else:
                    self.logger.warning(f"Agent type {agent_type} not registered")
                    results[agent_type] = AgentResult(
                        success=False,
                        content=f"Agent type {agent_type} not available",
                        metadata={"error": "Agent not registered"}
                    )
            
            # Synthesize final response
            final_response = await self._synthesize_response(results, request)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return OrchestrationResult(
                success=True,
                results=results,
                final_response=final_response,
                processing_time=processing_time,
                metadata={
                    "agent_count": len(results),
                    "successful_agents": sum(1 for r in results.values() if r.success)
                }
            )
            
        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            self.logger.error(f"Orchestration failed: {e}")
            
            return OrchestrationResult(
                success=False,
                results={},
                final_response=f"Orchestration failed: {e}",
                processing_time=processing_time,
                error=str(e)
            )
    
    async def _synthesize_response(
        self, 
        results: Dict[AgentType, AgentResult], 
        request: OrchestrationRequest
    ) -> str:
        """
        Synthesize a final response from multiple agent results.
        
        Args:
            results: Results from different agents
            request: Original orchestration request
            
        Returns:
            Synthesized response
        """
        successful_results = [
            result for result in results.values() 
            if result.success and result.content
        ]
        
        if not successful_results:
            return "I apologize, but I was unable to process your request with the available agents."
        
        # Simple synthesis - combine all successful results
        if len(successful_results) == 1:
            return successful_results[0].content
        
        # Multiple results - create a summary
        response_parts = []
        for agent_type, result in results.items():
            if result.success and result.content:
                response_parts.append(f"**{agent_type.value.title()} Analysis:**\n{result.content}")
        
        return "\n\n".join(response_parts)
    
    def get_available_agents(self) -> List[AgentType]:
        """Get list of available agent types."""
        return list(self.agents.keys())
    
    def get_agent_status(self) -> Dict[AgentType, bool]:
        """Get status of all registered agents."""
        return {agent_type: True for agent_type in self.agents.keys()}
