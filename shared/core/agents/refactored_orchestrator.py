"""
Refactored Orchestrator with Single Responsibility Functions

This module refactors the main backend orchestration code into smaller, focused functions
that each handle a single responsibility. This improves readability and maintainability
while preserving all functionality.

Key improvements:
1. Input parsing separated into dedicated functions
2. Agent execution logic broken into focused methods
3. Result aggregation and formatting in separate functions
4. Clear separation of concerns
5. Improved error handling and logging
6. Better testability of individual components
"""

import asyncio
import time
import uuid
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

from .base_agent import BaseAgent, AgentResult, QueryContext, AgentType
from .standardized_agents import (
    ExtendedAgentType, 
    STANDARDIZED_AGENTS,
    create_agent,
    get_agent_capabilities,
    AgentCapabilities
)
from ..unified_logging import get_logger, log_agent_lifecycle, log_execution_time, log_query_event

logger = get_logger(__name__)


class PipelineStage(Enum):
    """Pipeline execution stages."""
    
    INITIALIZATION = "initialization"
    PARALLEL_RETRIEVAL = "parallel_retrieval"
    ENRICHMENT = "enrichment"
    FACT_CHECK = "fact_check"
    SYNTHESIS = "synthesis"
    CITATION = "citation"
    FINALIZATION = "finalization"


@dataclass
class PipelineConfig:
    """Configuration for pipeline execution."""
    
    max_parallel_agents: int = 5
    agent_timeout_seconds: int = 30
    enable_parallel_retrieval: bool = True
    enable_enrichment_stage: bool = True
    fail_fast: bool = False
    require_minimum_results: bool = True
    minimum_confidence_threshold: float = 0.5
    max_total_execution_time: int = 120
    cache_results: bool = True
    enabled_agents: Set[ExtendedAgentType] = field(default_factory=lambda: {
        ExtendedAgentType.RETRIEVAL,
        ExtendedAgentType.KNOWLEDGE_GRAPH,
        ExtendedAgentType.FACT_CHECK,
        ExtendedAgentType.SYNTHESIS,
        ExtendedAgentType.CITATION
    })
    enable_dynamic_agent_selection: bool = True


@dataclass
class PipelineResult:
    """Result from pipeline execution."""
    
    success: bool
    final_answer: Optional[str] = None
    confidence: float = 0.0
    sources: List[Dict[str, Any]] = field(default_factory=list)
    citations: List[Dict[str, Any]] = field(default_factory=list)
    total_execution_time_ms: int = 0
    stage_results: Dict[str, Any] = field(default_factory=dict)
    agent_results: Dict[str, AgentResult] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    failed_agents: List[str] = field(default_factory=list)
    parallel_execution_time_ms: int = 0
    sequential_execution_time_ms: int = 0
    cache_hits: int = 0


class RefactoredOrchestrator:
    """
    Refactored orchestrator with single responsibility functions.
    
    This orchestrator breaks down the main orchestration logic into smaller,
    focused functions that each handle a single responsibility:
    
    1. Input parsing and validation
    2. Context creation and initialization
    3. Agent execution coordination
    4. Result aggregation and processing
    5. Response formatting and finalization
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """Initialize the refactored orchestrator."""
        self.config = config or PipelineConfig()
        self.agent_registry: Dict[ExtendedAgentType, BaseAgent] = {}
        self._initialize_agents()
        
        logger.info("🚀 Refactored Orchestrator initialized",
                   enabled_agents=len(self.config.enabled_agents),
                   component="orchestrator")
    
    def _initialize_agents(self):
        """Initialize all enabled agents."""
        logger.info("🔧 Initializing agents", component="orchestrator")
        
        for agent_type in self.config.enabled_agents:
            try:
                agent = create_agent(agent_type)
                self.agent_registry[agent_type] = agent
                logger.info(f"✅ Initialized agent: {agent_type.value}",
                           agent_type=agent_type.value,
                           component="orchestrator")
            except Exception as e:
                logger.error(f"❌ Failed to initialize agent {agent_type.value}: {e}",
                           agent_type=agent_type.value,
                           component="orchestrator")
    
    async def process_query(self, query: str, user_context: Dict[str, Any] = None) -> PipelineResult:
        """
        Main entry point for processing queries.
        
        This function orchestrates the complete pipeline by calling focused helper functions
        in sequence, each handling a single responsibility.
        """
        start_time = time.time()
        
        # Step 1: Parse and validate input
        parsed_input = await self._parse_and_validate_input(query, user_context)
        if not parsed_input["valid"]:
            return self._create_error_result(parsed_input["errors"], start_time)
        
        # Step 2: Create and initialize context
        context = await self._create_query_context(parsed_input, start_time)
        
        # Step 3: Execute pipeline stages
        stage_results = await self._execute_pipeline_stages(context)
        
        # Step 4: Aggregate and process results
        aggregated_results = await self._aggregate_pipeline_results(stage_results, context)
        
        # Step 5: Format final response
        final_result = await self._format_final_response(aggregated_results, context, start_time)
        
        return final_result
    
    async def _parse_and_validate_input(self, query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Parse and validate input parameters.
        
        Single responsibility: Input validation and parsing
        """
        errors = []
        
        # Validate query
        if not query or not isinstance(query, str):
            errors.append("Query must be a non-empty string")
        elif len(query.strip()) == 0:
            errors.append("Query cannot be empty")
        elif len(query) > 10000:  # Reasonable limit
            errors.append("Query too long (max 10000 characters)")
        
        # Validate user context
        if user_context is not None and not isinstance(user_context, dict):
            errors.append("User context must be a dictionary or None")
        
        # Sanitize query
        sanitized_query = query.strip() if query else ""
        
        return {
            "valid": len(errors) == 0,
            "query": sanitized_query,
            "user_context": user_context or {},
            "errors": errors
        }
    
    async def _create_query_context(self, parsed_input: Dict[str, Any], start_time: float) -> QueryContext:
        """
        Create and initialize query context.
        
        Single responsibility: Context creation and initialization
        """
        trace_id = str(uuid.uuid4())
        
        context = QueryContext(
            query=parsed_input["query"],
            user_context=parsed_input["user_context"],
            trace_id=trace_id,
            metadata={
                "start_time": start_time,
                "orchestrator": "refactored_orchestrator",
                "input_validation": "passed"
            }
        )
        
        log_query_event(logger, parsed_input["query"], "context_created",
                       query_id=trace_id,
                       user_context=parsed_input["user_context"],
                       component="orchestrator")
        
        return context
    
    async def _execute_pipeline_stages(self, context: QueryContext) -> Dict[PipelineStage, Any]:
        """
        Execute all pipeline stages in sequence.
        
        Single responsibility: Pipeline stage coordination
        """
        stage_results = {}
        
        try:
            # Stage 1: Parallel Retrieval
            if self.config.enable_parallel_retrieval:
                retrieval_results = await self._execute_parallel_retrieval_stage(context)
                stage_results[PipelineStage.PARALLEL_RETRIEVAL] = retrieval_results
                await self._update_context_with_results(context, retrieval_results)
            
            # Stage 2: Enrichment
            if self.config.enable_enrichment_stage:
                enrichment_results = await self._execute_enrichment_stage(context)
                stage_results[PipelineStage.ENRICHMENT] = enrichment_results
                await self._update_context_with_results(context, enrichment_results)
            
            # Stage 3: Fact Check
            fact_check_result = await self._execute_single_agent_stage(
                ExtendedAgentType.FACT_CHECK, context
            )
            stage_results[PipelineStage.FACT_CHECK] = fact_check_result
            await self._update_context_with_results(context, [fact_check_result])
            
            # Stage 4: Synthesis
            synthesis_result = await self._execute_single_agent_stage(
                ExtendedAgentType.SYNTHESIS, context
            )
            stage_results[PipelineStage.SYNTHESIS] = synthesis_result
            await self._update_context_with_results(context, [synthesis_result])
            
            # Stage 5: Citation
            citation_result = await self._execute_single_agent_stage(
                ExtendedAgentType.CITATION, context
            )
            stage_results[PipelineStage.CITATION] = citation_result
            
        except Exception as e:
            logger.error(f"Pipeline stage execution failed: {e}",
                        query_id=context.trace_id,
                        component="orchestrator")
            stage_results["error"] = str(e)
        
        return stage_results
    
    async def _execute_parallel_retrieval_stage(self, context: QueryContext) -> List[AgentResult]:
        """
        Execute retrieval and knowledge graph agents in parallel.
        
        Single responsibility: Parallel agent execution for retrieval
        """
        parallel_agents = []
        
        # Add retrieval agent
        if ExtendedAgentType.RETRIEVAL in self.agent_registry:
            parallel_agents.append((ExtendedAgentType.RETRIEVAL, self.agent_registry[ExtendedAgentType.RETRIEVAL]))
        
        # Add knowledge graph agent
        if ExtendedAgentType.KNOWLEDGE_GRAPH in self.agent_registry:
            parallel_agents.append((ExtendedAgentType.KNOWLEDGE_GRAPH, self.agent_registry[ExtendedAgentType.KNOWLEDGE_GRAPH]))
        
        if not parallel_agents:
            logger.warning("No retrieval agents available",
                          query_id=context.trace_id,
                          component="orchestrator")
            return []
        
        return await self._execute_agents_in_parallel(
            parallel_agents, context, "parallel_retrieval"
        )
    
    async def _execute_enrichment_stage(self, context: QueryContext) -> List[AgentResult]:
        """
        Execute enrichment agents in parallel.
        
        Single responsibility: Parallel agent execution for enrichment
        """
        enrichment_agents = []
        
        # Add browser agent
        if ExtendedAgentType.BROWSER in self.agent_registry:
            enrichment_agents.append((ExtendedAgentType.BROWSER, self.agent_registry[ExtendedAgentType.BROWSER]))
        
        # Add database agent
        if ExtendedAgentType.DATABASE in self.agent_registry:
            enrichment_agents.append((ExtendedAgentType.DATABASE, self.agent_registry[ExtendedAgentType.DATABASE]))
        
        # Add PDF agent
        if ExtendedAgentType.PDF in self.agent_registry:
            enrichment_agents.append((ExtendedAgentType.PDF, self.agent_registry[ExtendedAgentType.PDF]))
        
        if not enrichment_agents:
            logger.warning("No enrichment agents available",
                          query_id=context.trace_id,
                          component="orchestrator")
            return []
        
        return await self._execute_agents_in_parallel(
            enrichment_agents, context, "enrichment"
        )
    
    async def _execute_single_agent_stage(self, agent_type: ExtendedAgentType, context: QueryContext) -> AgentResult:
        """
        Execute a single agent stage.
        
        Single responsibility: Single agent execution
        """
        if agent_type not in self.agent_registry:
            logger.error(f"Agent {agent_type.value} not found in registry",
                        agent_type=agent_type.value,
                        query_id=context.trace_id,
                        component="orchestrator")
            return AgentResult(
                success=False,
                agent_type=agent_type,
                error=f"Agent {agent_type.value} not available"
            )
        
        agent = self.agent_registry[agent_type]
        return await self._execute_agent_with_timeout(agent, context, agent_type)
    
    async def _execute_agents_in_parallel(
        self, 
        agents: List[Tuple[ExtendedAgentType, BaseAgent]], 
        context: QueryContext,
        stage_name: str
    ) -> List[AgentResult]:
        """
        Execute multiple agents in parallel.
        
        Single responsibility: Parallel execution coordination
        """
        if not agents:
            return []
        
        logger.info(f"Executing {len(agents)} agents in parallel for stage: {stage_name}",
                   query_id=context.trace_id,
                   stage=stage_name,
                   agent_count=len(agents),
                   component="orchestrator")
        
        # Create tasks for parallel execution
        tasks = []
        for agent_type, agent in agents:
            task = self._execute_agent_with_timeout(agent, context, agent_type)
            tasks.append(task)
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            agent_type = agents[i][0]
            
            if isinstance(result, Exception):
                logger.error(f"Agent {agent_type.value} failed: {result}",
                           agent_type=agent_type.value,
                           query_id=context.trace_id,
                           component="orchestrator")
                processed_results.append(AgentResult(
                    success=False,
                    agent_type=agent_type,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_agent_with_timeout(
        self, 
        agent: BaseAgent, 
        context: QueryContext, 
        agent_type: ExtendedAgentType
    ) -> AgentResult:
        """
        Execute a single agent with timeout and error handling.
        
        Single responsibility: Individual agent execution with safety
        """
        try:
            log_agent_lifecycle(logger, agent_type.value, "started",
                              query_id=context.trace_id,
                              component="orchestrator")
            
            # Execute with timeout
            result = await asyncio.wait_for(
                agent.execute(context),
                timeout=self.config.agent_timeout_seconds
            )
            
            log_agent_lifecycle(logger, agent_type.value, "completed",
                              query_id=context.trace_id,
                              success=result.success,
                              component="orchestrator")
            
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"Agent {agent_type.value} timed out",
                        agent_type=agent_type.value,
                        query_id=context.trace_id,
                        timeout=self.config.agent_timeout_seconds,
                        component="orchestrator")
            return AgentResult(
                success=False,
                agent_type=agent_type,
                error=f"Agent {agent_type.value} timed out after {self.config.agent_timeout_seconds}s"
            )
        except Exception as e:
            logger.error(f"Agent {agent_type.value} failed: {e}",
                        agent_type=agent_type.value,
                        query_id=context.trace_id,
                        component="orchestrator")
            return AgentResult(
                success=False,
                agent_type=agent_type,
                error=str(e)
            )
    
    async def _update_context_with_results(self, context: QueryContext, results: List[AgentResult]):
        """
        Update context with agent results.
        
        Single responsibility: Context state management
        """
        if not results:
            return
        
        # Collect successful results
        successful_results = [r for r in results if r.success]
        
        if successful_results:
            # Update context metadata with results summary
            context.metadata["last_stage_results"] = {
                "total_agents": len(results),
                "successful_agents": len(successful_results),
                "failed_agents": len(results) - len(successful_results),
                "agent_types": [r.agent_type.value for r in results]
            }
            
            # Add individual results to context
            for result in successful_results:
                context.metadata[f"{result.agent_type.value}_result"] = {
                    "success": result.success,
                    "confidence": getattr(result, 'confidence', 0.0),
                    "content": getattr(result, 'content', ''),
                    "sources": getattr(result, 'sources', [])
                }
    
    async def _aggregate_pipeline_results(self, stage_results: Dict[PipelineStage, Any], context: QueryContext) -> Dict[str, Any]:
        """
        Aggregate results from all pipeline stages.
        
        Single responsibility: Result aggregation and processing
        """
        aggregated = {
            "stages": {},
            "total_agents": 0,
            "successful_agents": 0,
            "failed_agents": 0,
            "final_answer": None,
            "confidence": 0.0,
            "sources": [],
            "citations": []
        }
        
        for stage, results in stage_results.items():
            if isinstance(results, list):
                # Handle list of agent results
                stage_summary = {
                    "agent_count": len(results),
                    "successful_count": len([r for r in results if r.success]),
                    "failed_count": len([r for r in results if not r.success]),
                    "results": results
                }
                aggregated["stages"][stage.value] = stage_summary
                aggregated["total_agents"] += len(results)
                aggregated["successful_agents"] += stage_summary["successful_count"]
                aggregated["failed_agents"] += stage_summary["failed_count"]
                
                # Extract final answer from synthesis stage
                if stage == PipelineStage.SYNTHESIS and results:
                    synthesis_result = results[0]
                    if synthesis_result.success:
                        aggregated["final_answer"] = getattr(synthesis_result, 'content', '')
                        aggregated["confidence"] = getattr(synthesis_result, 'confidence', 0.0)
                
                # Collect sources and citations
                for result in results:
                    if result.success:
                        if hasattr(result, 'sources'):
                            aggregated["sources"].extend(result.sources)
                        if hasattr(result, 'citations'):
                            aggregated["citations"].extend(result.citations)
            else:
                # Handle single result or error
                aggregated["stages"][stage.value] = results
        
        return aggregated
    
    async def _format_final_response(self, aggregated_results: Dict[str, Any], context: QueryContext, start_time: float) -> PipelineResult:
        """
        Format the final response from aggregated results.
        
        Single responsibility: Response formatting and finalization
        """
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        # Determine success based on results
        success = (
            aggregated_results["successful_agents"] > 0 and
            aggregated_results["final_answer"] is not None and
            aggregated_results["confidence"] >= self.config.minimum_confidence_threshold
        )
        
        # Create pipeline result
        result = PipelineResult(
            success=success,
            final_answer=aggregated_results["final_answer"],
            confidence=aggregated_results["confidence"],
            sources=aggregated_results["sources"],
            citations=aggregated_results["citations"],
            total_execution_time_ms=execution_time_ms,
            stage_results=aggregated_results["stages"]
        )
        
        # Log completion
        log_query_event(logger, context.query, "completed",
                       query_id=context.trace_id,
                       success=success,
                       execution_time_ms=execution_time_ms,
                       component="orchestrator")
        
        return result
    
    def _create_error_result(self, errors: List[str], start_time: float) -> PipelineResult:
        """
        Create error result for invalid input.
        
        Single responsibility: Error response creation
        """
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        return PipelineResult(
            success=False,
            errors=errors,
            total_execution_time_ms=execution_time_ms
        )
    
    def register_agent(self, agent_type: ExtendedAgentType, agent: BaseAgent):
        """Register an agent with the orchestrator."""
        self.agent_registry[agent_type] = agent
        self.config.enabled_agents.add(agent_type)
        logger.info(f"Registered agent: {agent_type.value}",
                   agent_type=agent_type.value,
                   component="orchestrator")
    
    def unregister_agent(self, agent_type: ExtendedAgentType):
        """Unregister an agent from the orchestrator."""
        if agent_type in self.agent_registry:
            del self.agent_registry[agent_type]
            self.config.enabled_agents.discard(agent_type)
            logger.info(f"Unregistered agent: {agent_type.value}",
                       agent_type=agent_type.value,
                       component="orchestrator") 