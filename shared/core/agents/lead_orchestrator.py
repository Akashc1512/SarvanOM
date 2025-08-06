"""
LeadOrchestrator Implementation for Multi-Agent Knowledge Platform
Refactored to use standardized multi-agent pipeline with common interface.

This module provides a clean wrapper around the RefinedLeadOrchestrator which implements:
- Common BaseAgent.execute(context) interface for all agents
- Parallel execution using asyncio.gather() for I/O operations  
- Shared QueryContext for agent communication
- Simplified orchestration logic with easy agent registration
"""

import asyncio
import time
import uuid
from typing import Dict, List, Any, Optional

from .refined_lead_orchestrator import (
    RefinedLeadOrchestrator,
    PipelineConfig,
    PipelineResult,
    PipelineStage
)
from .standardized_agents import ExtendedAgentType
from .base_agent import QueryContext
from ..unified_logging import get_logger, log_query_event

logger = get_logger(__name__)


class LeadOrchestrator:
    """
    Main LeadOrchestrator class that coordinates all specialized agents.
    
    This is a clean wrapper around RefinedLeadOrchestrator that provides:
    - Backward compatibility with existing interfaces
    - Simplified configuration and usage
    - Standard query processing pipeline
    
    Key improvements:
    1. All agents use common BaseAgent.execute(context) interface
    2. Parallel execution for retrieval operations using asyncio.gather()
    3. Shared QueryContext maintains state between agents
    4. Easy agent registration/removal via configuration
    5. Clear pipeline stages with optimized execution order
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LeadOrchestrator.
        
        Args:
            config: Optional configuration dictionary
        """
        logger.info("🚀 Initializing LeadOrchestrator with refined pipeline",
                   component="orchestrator")
        
        # Create pipeline configuration
        pipeline_config = PipelineConfig()
        
        if config:
            # Apply custom configuration
            if "max_parallel_agents" in config:
                pipeline_config.max_parallel_agents = config["max_parallel_agents"]
            if "agent_timeout_seconds" in config:
                pipeline_config.agent_timeout_seconds = config["agent_timeout_seconds"]
            if "enabled_agents" in config:
                pipeline_config.enabled_agents = set(config["enabled_agents"])
            if "enable_parallel_retrieval" in config:
                pipeline_config.enable_parallel_retrieval = config["enable_parallel_retrieval"]
            if "enable_enrichment_stage" in config:
                pipeline_config.enable_enrichment_stage = config["enable_enrichment_stage"]
        
        # Initialize the refined orchestrator
        self.orchestrator = RefinedLeadOrchestrator(pipeline_config)
        
        logger.info("✅ LeadOrchestrator initialized successfully",
                   enabled_agents=len(pipeline_config.enabled_agents),
                   parallel_retrieval=pipeline_config.enable_parallel_retrieval,
                   component="orchestrator")
    
    async def process_query(self, query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a query through the standardized multi-agent pipeline.
        
        This method orchestrates the execution of specialized agents in an optimized sequence:
        1. Parallel Retrieval: RetrievalAgent and KnowledgeAgent run concurrently
        2. Enrichment: Browser, Database agents run in parallel (optional)
        3. Fact Check: FactCheckAgent processes retrieved information
        4. Synthesis: SynthesisAgent generates the answer
        5. Citation: CitationAgent adds proper citations
        
        Args:
            query: The user query to process
            user_context: Additional context information
        
        Returns:
            Dictionary containing the final answer, sources, and execution metadata
        """
        log_query_event(logger, query, "received",
                       query_id=str(uuid.uuid4()),
                       user_context=user_context,
                       component="orchestrator")
        
        try:
            # Execute the pipeline using the refined orchestrator
            result: PipelineResult = await self.orchestrator.process_query(query, user_context)
            
            # Convert PipelineResult to the expected format
            response = {
                "success": result.success,
                "answer": result.final_answer,
                "confidence": result.confidence,
                "sources": result.sources,
                "citations": result.citations,
                "execution_time_ms": result.total_execution_time_ms,
                "metadata": {
                    "pipeline_stages": list(result.stage_results.keys()),
                    "parallel_execution_time_ms": result.parallel_execution_time_ms,
                    "sequential_execution_time_ms": result.sequential_execution_time_ms,
                    "cache_hits": result.cache_hits,
                    "failed_agents": result.failed_agents
                }
            }
            
            # Add error information if there were failures
            if result.errors:
                response["errors"] = result.errors
                response["warnings"] = f"Some agents failed: {', '.join(result.failed_agents)}"
            
            logger.info("Query processing completed",
                       success=result.success,
                       execution_time_ms=result.total_execution_time_ms,
                       confidence=result.confidence,
                       component="orchestrator")
            
            return response
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}",
                        query=query,
                        error=str(e),
                        component="orchestrator")
            
            return {
                "success": False,
                "error": str(e),
                "answer": None,
                "confidence": 0.0,
                "sources": [],
                "citations": [],
                "execution_time_ms": 0,
                "metadata": {"error_type": type(e).__name__}
            }
    
    def register_agent(self, agent_type: str, agent):
        """
        Register a new agent with the orchestrator.
        
        Args:
            agent_type: String identifier for the agent type
            agent: Agent instance implementing BaseAgent interface
        """
        try:
            extended_agent_type = ExtendedAgentType(agent_type)
            self.orchestrator.register_agent(extended_agent_type, agent)
            logger.info(f"Registered new agent: {agent_type}",
                       agent_type=agent_type,
                       component="orchestrator")
        except ValueError:
            logger.warning(f"Unknown agent type: {agent_type}",
                          agent_type=agent_type,
                          component="orchestrator")
    
    def unregister_agent(self, agent_type: str):
        """
        Remove an agent from the orchestrator.
        
        Args:
            agent_type: String identifier for the agent type to remove
        """
        try:
            extended_agent_type = ExtendedAgentType(agent_type)
            self.orchestrator.unregister_agent(extended_agent_type)
            logger.info(f"Unregistered agent: {agent_type}",
                       agent_type=agent_type,
                       component="orchestrator")
        except ValueError:
            logger.warning(f"Unknown agent type: {agent_type}",
                          agent_type=agent_type,
                          component="orchestrator")
    
    def get_available_agents(self) -> List[str]:
        """
        Get list of available agent types.
        
        Returns:
            List of agent type strings
        """
        return [agent_type.value for agent_type in self.orchestrator.agent_registry.keys()]
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get current pipeline status and configuration.
        
        Returns:
            Dictionary with pipeline status information
        """
        config = self.orchestrator.config
        return {
            "enabled_agents": [agent.value for agent in config.enabled_agents],
            "max_parallel_agents": config.max_parallel_agents,
            "agent_timeout_seconds": config.agent_timeout_seconds,
            "parallel_retrieval_enabled": config.enable_parallel_retrieval,
            "enrichment_stage_enabled": config.enable_enrichment_stage,
            "registered_agents": len(self.orchestrator.agent_registry),
            "pipeline_stages": [stage.value for stage in self.orchestrator.pipeline_stages.keys()]
        }


# Backward compatibility aliases
StandardizedLeadOrchestrator = LeadOrchestrator

# Export main classes
__all__ = [
    'LeadOrchestrator',
    'StandardizedLeadOrchestrator',
    'PipelineConfig',
    'PipelineResult',
    'PipelineStage',
    'ExtendedAgentType'
]