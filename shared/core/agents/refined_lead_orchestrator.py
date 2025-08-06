"""
Refined LeadOrchestrator with Standardized Multi-Agent Pipeline

This module implements a clean, maintainable orchestrator that uses:
- Common interface (BaseAgent.execute(context)) for all agents
- Parallel execution using asyncio.gather() for I/O bound operations
- Shared QueryContext for agent communication
- Simplified orchestration logic with easy agent registration/removal
- Pipeline stages with defined dependencies and execution order

Features:
- Fork-join pattern for parallel agent execution
- Scatter-gather pattern for collecting results
- Error handling and graceful degradation
- Performance monitoring and metrics
- Dynamic agent registration via ServiceProvider
"""

import asyncio
import time
import uuid
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque

from .base_agent import BaseAgent, AgentResult, QueryContext, AgentType
from .standardized_agents import (
    ExtendedAgentType, 
    STANDARDIZED_AGENTS,
    create_agent,
    get_agent_capabilities,
    AgentCapabilities
)
from .retrieval_agent import RetrievalAgent
from .factcheck_agent import FactCheckAgent
from .synthesis_agent import SynthesisAgent
from .citation_agent import CitationAgent
from ..unified_logging import get_logger, log_agent_lifecycle, log_execution_time, log_query_event

logger = get_logger(__name__)


class PipelineStage(Enum):
    """Pipeline execution stages."""
    
    INITIALIZATION = "initialization"
    PARALLEL_RETRIEVAL = "parallel_retrieval"  # Retrieval + Knowledge Graph in parallel
    ENRICHMENT = "enrichment"  # Browser, PDF, Code, Database in parallel
    FACT_CHECK = "fact_check"
    SYNTHESIS = "synthesis"
    CITATION = "citation"
    FINALIZATION = "finalization"


@dataclass
class PipelineConfig:
    """Configuration for pipeline execution."""
    
    # Agent execution configuration
    max_parallel_agents: int = 5
    agent_timeout_seconds: int = 30
    enable_parallel_retrieval: bool = True
    enable_enrichment_stage: bool = True
    
    # Pipeline behavior
    fail_fast: bool = False  # Stop on first agent failure
    require_minimum_results: bool = True
    minimum_confidence_threshold: float = 0.5
    
    # Performance settings
    max_total_execution_time: int = 120  # seconds
    cache_results: bool = True
    
    # Agent selection
    enabled_agents: Set[ExtendedAgentType] = field(default_factory=lambda: {
        ExtendedAgentType.RETRIEVAL,
        ExtendedAgentType.KNOWLEDGE_GRAPH,
        ExtendedAgentType.FACT_CHECK,
        ExtendedAgentType.SYNTHESIS,
        ExtendedAgentType.CITATION
    })
    
    # Dynamic agent selection based on query
    enable_dynamic_agent_selection: bool = True


@dataclass
class PipelineResult:
    """Result from pipeline execution."""
    
    success: bool
    final_answer: Optional[str] = None
    confidence: float = 0.0
    sources: List[Dict[str, Any]] = field(default_factory=list)
    citations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Execution metadata
    total_execution_time_ms: int = 0
    stage_results: Dict[str, Any] = field(default_factory=dict)
    agent_results: Dict[str, AgentResult] = field(default_factory=dict)
    
    # Error information
    errors: List[str] = field(default_factory=list)
    failed_agents: List[str] = field(default_factory=list)
    
    # Performance metrics
    parallel_execution_time_ms: int = 0
    sequential_execution_time_ms: int = 0
    cache_hits: int = 0


class RefinedLeadOrchestrator:
    """
    Refined LeadOrchestrator implementing standardized multi-agent pipeline.
    
    Key improvements:
    1. All agents implement common BaseAgent.execute(context) interface
    2. Parallel execution for I/O bound operations (retrieval, web search, etc.)
    3. Shared QueryContext maintains state between agents
    4. Simple agent registration/removal via configuration
    5. Clear pipeline stages with defined dependencies
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """Initialize the refined orchestrator."""
        self.config = config or PipelineConfig()
        self.agent_registry: Dict[ExtendedAgentType, BaseAgent] = {}
        self.pipeline_cache = {}
        
        logger.info("🚀 Initializing Refined LeadOrchestrator",
                   max_parallel_agents=self.config.max_parallel_agents,
                   enabled_agents=len(self.config.enabled_agents),
                   component="orchestrator")
        
        # Initialize agents
        self._initialize_agents()
        
        # Pipeline stage definitions with dependencies
        self.pipeline_stages = {
            PipelineStage.PARALLEL_RETRIEVAL: {
                "agents": [ExtendedAgentType.RETRIEVAL, ExtendedAgentType.KNOWLEDGE_GRAPH],
                "parallel": True,
                "required": True,
                "timeout": 20
            },
            PipelineStage.ENRICHMENT: {
                "agents": [ExtendedAgentType.BROWSER, ExtendedAgentType.DATABASE],
                "parallel": True,
                "required": False,
                "timeout": 15
            },
            PipelineStage.FACT_CHECK: {
                "agents": [ExtendedAgentType.FACT_CHECK],
                "parallel": False,
                "required": True,
                "timeout": 10,
                "depends_on": [PipelineStage.PARALLEL_RETRIEVAL]
            },
            PipelineStage.SYNTHESIS: {
                "agents": [ExtendedAgentType.SYNTHESIS],
                "parallel": False,
                "required": True,
                "timeout": 15,
                "depends_on": [PipelineStage.FACT_CHECK]
            },
            PipelineStage.CITATION: {
                "agents": [ExtendedAgentType.CITATION],
                "parallel": False,
                "required": True,
                "timeout": 10,
                "depends_on": [PipelineStage.SYNTHESIS]
            }
        }
        
        logger.info("✅ Refined LeadOrchestrator initialized successfully",
                   registered_agents=len(self.agent_registry),
                   pipeline_stages=len(self.pipeline_stages),
                   component="orchestrator")
    
    def _initialize_agents(self):
        """Initialize all configured agents."""
        # Initialize core agents - these use the original AgentType
        try:
            # Map ExtendedAgentType to original agents that use AgentType
            self.agent_registry[ExtendedAgentType.RETRIEVAL] = RetrievalAgent()
            self.agent_registry[ExtendedAgentType.FACT_CHECK] = FactCheckAgent()
            self.agent_registry[ExtendedAgentType.SYNTHESIS] = SynthesisAgent()
            self.agent_registry[ExtendedAgentType.CITATION] = CitationAgent()
            logger.info("✅ Core agents initialized successfully", component="orchestrator")
        except Exception as e:
            logger.warning(f"Failed to initialize core agents: {e}", 
                          error=str(e), component="orchestrator")
        
        # Initialize specialized agents from standardized implementations
        for agent_type in self.config.enabled_agents:
            if agent_type not in self.agent_registry:
                try:
                    agent = create_agent(agent_type)
                    self.agent_registry[agent_type] = agent
                    logger.info(f"Registered agent: {agent_type.value}", 
                               agent_type=agent_type.value,
                               component="orchestrator")
                except Exception as e:
                    logger.warning(f"Failed to initialize {agent_type.value} agent: {e}",
                                 agent_type=agent_type.value,
                                 component="orchestrator")
    
    def register_agent(self, agent_type: ExtendedAgentType, agent: BaseAgent):
        """Register a new agent in the orchestrator."""
        self.agent_registry[agent_type] = agent
        self.config.enabled_agents.add(agent_type)
        logger.info(f"Registered new agent: {agent_type.value}",
                   agent_type=agent_type.value,
                   component="orchestrator")
    
    def unregister_agent(self, agent_type: ExtendedAgentType):
        """Remove an agent from the orchestrator."""
        if agent_type in self.agent_registry:
            del self.agent_registry[agent_type]
            self.config.enabled_agents.discard(agent_type)
            logger.info(f"Unregistered agent: {agent_type.value}",
                       agent_type=agent_type.value,
                       component="orchestrator")
    
    async def process_query(self, query: str, user_context: Dict[str, Any] = None) -> PipelineResult:
        """
        Process a query through the standardized multi-agent pipeline.
        
        Args:
            query: The user query to process
            user_context: Additional context information
        
        Returns:
            PipelineResult with the final answer and execution metadata
        """
        start_time = time.time()
        trace_id = str(uuid.uuid4())
        
        log_query_event(logger, query, "started",
                       query_id=trace_id,
                       user_context=user_context,
                       component="orchestrator")
        
        # Create shared context for all agents
        context = QueryContext(
            query=query,
            user_context=user_context or {},
            trace_id=trace_id,
            metadata={
                "start_time": start_time,
                "orchestrator": "refined_lead_orchestrator"
            }
        )
        
        result = PipelineResult(success=False)
        
        try:
            # Execute pipeline stages
            stage_results = {}
            
            # Stage 1: Parallel Retrieval (Retrieval + Knowledge Graph)
            if self.config.enable_parallel_retrieval:
                retrieval_results = await self._execute_parallel_retrieval_stage(context)
                stage_results[PipelineStage.PARALLEL_RETRIEVAL] = retrieval_results
                self._update_context_with_results(context, retrieval_results)
            
            # Stage 2: Enrichment (Browser, Database, etc. in parallel)
            if self.config.enable_enrichment_stage:
                enrichment_results = await self._execute_enrichment_stage(context)
                stage_results[PipelineStage.ENRICHMENT] = enrichment_results
                self._update_context_with_results(context, enrichment_results)
            
            # Stage 3: Fact Check (sequential)
            fact_check_result = await self._execute_single_agent_stage(
                ExtendedAgentType.FACT_CHECK, context
            )
            stage_results[PipelineStage.FACT_CHECK] = fact_check_result
            self._update_context_with_results(context, [fact_check_result])
            
            # Stage 4: Synthesis (sequential)
            synthesis_result = await self._execute_single_agent_stage(
                ExtendedAgentType.SYNTHESIS, context
            )
            stage_results[PipelineStage.SYNTHESIS] = synthesis_result
            self._update_context_with_results(context, [synthesis_result])
            
            # Stage 5: Citation (sequential)
            citation_result = await self._execute_single_agent_stage(
                ExtendedAgentType.CITATION, context
            )
            stage_results[PipelineStage.CITATION] = citation_result
            
            # Build final result
            result = self._build_pipeline_result(stage_results, context, start_time)
            
            log_query_event(logger, query, "completed",
                           query_id=trace_id,
                           success=result.success,
                           execution_time_ms=result.total_execution_time_ms,
                           component="orchestrator")
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Pipeline execution failed: {e}",
                        query_id=trace_id,
                        execution_time_ms=execution_time_ms,
                        component="orchestrator")
            
            result.errors.append(str(e))
            result.total_execution_time_ms = execution_time_ms
        
        return result
    
    async def _execute_parallel_retrieval_stage(self, context: QueryContext) -> List[AgentResult]:
        """Execute retrieval and knowledge graph agents in parallel."""
        parallel_agents = []
        
        # Add retrieval agent
        if ExtendedAgentType.RETRIEVAL in self.agent_registry:
            parallel_agents.append((ExtendedAgentType.RETRIEVAL, self.agent_registry[ExtendedAgentType.RETRIEVAL]))
        
        # Add knowledge graph agent
        if ExtendedAgentType.KNOWLEDGE_GRAPH in self.agent_registry:
            parallel_agents.append((ExtendedAgentType.KNOWLEDGE_GRAPH, self.agent_registry[ExtendedAgentType.KNOWLEDGE_GRAPH]))
        
        return await self._execute_agents_in_parallel(parallel_agents, context, "parallel_retrieval")
    
    async def _execute_enrichment_stage(self, context: QueryContext) -> List[AgentResult]:
        """Execute enrichment agents (browser, database, etc.) in parallel."""
        parallel_agents = []
        
        # Dynamically select enrichment agents based on query analysis
        enrichment_agent_types = [
            ExtendedAgentType.BROWSER,
            ExtendedAgentType.DATABASE,
        ]
        
        # Add available enrichment agents
        for agent_type in enrichment_agent_types:
            if agent_type in self.agent_registry:
                parallel_agents.append((agent_type, self.agent_registry[agent_type]))
        
        return await self._execute_agents_in_parallel(parallel_agents, context, "enrichment")
    
    async def _execute_single_agent_stage(self, agent_type: ExtendedAgentType, context: QueryContext) -> AgentResult:
        """Execute a single agent stage."""
        if agent_type not in self.agent_registry:
            return AgentResult(
                success=False,
                error=f"Agent {agent_type.value} not available",
                metadata={"agent_type": agent_type.value}
            )
        
        agent = self.agent_registry[agent_type]
        
        log_agent_lifecycle(logger, agent_type.value, "started",
                           stage="single_agent",
                           query=context.query)
        
        try:
            with log_execution_time(logger, f"{agent_type.value}_execution"):
                result = await asyncio.wait_for(
                    agent.execute(context),
                    timeout=self.config.agent_timeout_seconds
                )
            
            log_agent_lifecycle(logger, agent_type.value, "completed",
                               success=result.success,
                               execution_time_ms=result.execution_time_ms)
            
            return result
            
        except asyncio.TimeoutError:
            logger.warning(f"Agent {agent_type.value} timed out",
                          agent_type=agent_type.value,
                          timeout=self.config.agent_timeout_seconds)
            return AgentResult(
                success=False,
                error=f"Agent {agent_type.value} timed out",
                metadata={"agent_type": agent_type.value, "timeout": True}
            )
        except Exception as e:
            logger.error(f"Agent {agent_type.value} execution failed: {e}",
                        agent_type=agent_type.value,
                        error=str(e))
            return AgentResult(
                success=False,
                error=str(e),
                metadata={"agent_type": agent_type.value, "error_type": type(e).__name__}
            )
    
    async def _execute_agents_in_parallel(
        self, 
        agents: List[Tuple[ExtendedAgentType, BaseAgent]], 
        context: QueryContext,
        stage_name: str
    ) -> List[AgentResult]:
        """Execute multiple agents in parallel using asyncio.gather()."""
        
        if not agents:
            return []
        
        logger.info(f"Executing {len(agents)} agents in parallel",
                   stage=stage_name,
                   agents=[agent_type.value for agent_type, _ in agents],
                   component="orchestrator")
        
        # Create coroutines for parallel execution
        tasks = []
        for agent_type, agent in agents:
            log_agent_lifecycle(logger, agent_type.value, "started",
                               stage=stage_name,
                               query=context.query)
            
            # Wrap each agent execution with timeout and error handling
            task = asyncio.create_task(
                self._execute_agent_with_timeout(agent, context, agent_type),
                name=f"{agent_type.value}_task"
            )
            tasks.append(task)
        
        # Execute all agents in parallel
        try:
            with log_execution_time(logger, f"{stage_name}_parallel_execution"):
                results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and convert exceptions to error results
            processed_results = []
            for i, (result, (agent_type, _)) in enumerate(zip(results, agents)):
                if isinstance(result, Exception):
                    logger.error(f"Parallel agent {agent_type.value} failed: {result}",
                                agent_type=agent_type.value,
                                stage=stage_name,
                                error=str(result))
                    processed_results.append(AgentResult(
                        success=False,
                        error=str(result),
                        metadata={"agent_type": agent_type.value, "stage": stage_name}
                    ))
                else:
                    log_agent_lifecycle(logger, agent_type.value, "completed",
                                       success=result.success,
                                       execution_time_ms=result.execution_time_ms,
                                       stage=stage_name)
                    processed_results.append(result)
            
            logger.info(f"Parallel execution completed",
                       stage=stage_name,
                       successful_agents=sum(1 for r in processed_results if r.success),
                       total_agents=len(processed_results),
                       component="orchestrator")
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Parallel execution failed: {e}",
                        stage=stage_name,
                        component="orchestrator")
            return []
    
    async def _execute_agent_with_timeout(
        self, 
        agent: BaseAgent, 
        context: QueryContext, 
        agent_type: ExtendedAgentType
    ) -> AgentResult:
        """Execute a single agent with timeout handling."""
        try:
            result = await asyncio.wait_for(
                agent.execute(context),
                timeout=self.config.agent_timeout_seconds
            )
            return result
        except asyncio.TimeoutError:
            return AgentResult(
                success=False,
                error=f"Agent {agent_type.value} timed out",
                metadata={"agent_type": agent_type.value, "timeout": True}
            )
        except Exception as e:
            return AgentResult(
                success=False,
                error=str(e),
                metadata={"agent_type": agent_type.value, "error_type": type(e).__name__}
            )
    
    def _update_context_with_results(self, context: QueryContext, results: List[AgentResult]):
        """Update the shared context with results from agent execution."""
        for result in results:
            if result.success and result.data:
                agent_type = result.metadata.get("agent_type", "unknown")
                
                # Store agent results in context metadata
                if "agent_results" not in context.metadata:
                    context.metadata["agent_results"] = {}
                
                context.metadata["agent_results"][agent_type] = result.data
                
                # Extract and aggregate common data types
                if isinstance(result.data, dict):
                    # Documents/sources
                    if "documents" in result.data:
                        if "all_documents" not in context.metadata:
                            context.metadata["all_documents"] = []
                        context.metadata["all_documents"].extend(result.data["documents"])
                    
                    # Search results
                    if "results" in result.data:
                        if "all_results" not in context.metadata:
                            context.metadata["all_results"] = []
                        context.metadata["all_results"].extend(result.data["results"])
                    
                    # Knowledge graph data
                    if "nodes" in result.data or "relationships" in result.data:
                        context.metadata["knowledge_graph"] = result.data
    
    def _build_pipeline_result(
        self, 
        stage_results: Dict[PipelineStage, Any], 
        context: QueryContext, 
        start_time: float
    ) -> PipelineResult:
        """Build the final pipeline result from all stage results."""
        total_execution_time_ms = int((time.time() - start_time) * 1000)
        
        # Extract final answer from synthesis stage
        final_answer = None
        confidence = 0.0
        
        synthesis_results = stage_results.get(PipelineStage.SYNTHESIS)
        if synthesis_results and synthesis_results.success:
            synthesis_data = synthesis_results.data
            if isinstance(synthesis_data, dict):
                final_answer = synthesis_data.get("answer") or synthesis_data.get("response")
                confidence = synthesis_data.get("confidence", 0.0)
        
        # Extract citations
        citations = []
        citation_results = stage_results.get(PipelineStage.CITATION)
        if citation_results and citation_results.success:
            citation_data = citation_results.data
            if isinstance(citation_data, dict):
                citations = citation_data.get("citations", [])
        
        # Extract sources from all retrieval stages
        sources = []
        all_documents = context.metadata.get("all_documents", [])
        all_results = context.metadata.get("all_results", [])
        sources.extend(all_documents)
        sources.extend(all_results)
        
        # Determine overall success
        success = (
            final_answer is not None and 
            confidence >= self.config.minimum_confidence_threshold
        )
        
        # Collect errors
        errors = []
        failed_agents = []
        for stage, result in stage_results.items():
            if isinstance(result, list):
                for r in result:
                    if not r.success:
                        errors.append(r.error)
                        failed_agents.append(r.metadata.get("agent_type", "unknown"))
            elif hasattr(result, 'success') and not result.success:
                errors.append(result.error)
                failed_agents.append(result.metadata.get("agent_type", "unknown"))
        
        return PipelineResult(
            success=success,
            final_answer=final_answer,
            confidence=confidence,
            sources=sources,
            citations=citations,
            total_execution_time_ms=total_execution_time_ms,
            stage_results={stage.value: result for stage, result in stage_results.items()},
            agent_results={},  # Could be populated if needed
            errors=errors,
            failed_agents=failed_agents
        )


# Export main classes
__all__ = [
    'RefinedLeadOrchestrator',
    'PipelineConfig',
    'PipelineResult',
    'PipelineStage'
]