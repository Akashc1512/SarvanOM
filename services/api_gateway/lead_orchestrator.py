"""
LeadOrchestrator Implementation for Multi-Agent Knowledge Platform
This module implements the central orchestrator that coordinates all agents.
"""

import asyncio
import logging
import time
import os
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from shared.core.agents.base_agent import AgentResult, QueryContext, AgentType
from shared.core.agents.retrieval_agent import RetrievalAgent
from shared.core.agents.factcheck_agent import FactCheckAgent
from shared.core.agents.synthesis_agent import SynthesisAgent
from shared.core.agents.citation_agent import CitationAgent
from shared.core.agents.reviewer_agent import ReviewerAgent
from services.api_gateway.lead_orchestrator_fixes import (
    create_safe_agent_result,
    safe_prepare_synthesis_input,
    handle_agent_failure,
    validate_agent_result,
    create_pipeline_error_response,
)
from services.api_gateway.orchestrator_workflow_fixes import (
    merge_retrieval_results_improved,
    execute_pipeline_improved,
)

# Data models imported as needed

# Import unified logging
from shared.core.unified_logging import get_logger, log_agent_lifecycle, log_execution_time, log_query_event

# Configure unified logging
logger = get_logger(__name__)

# Global cache instance for observability endpoints
GLOBAL_SEMANTIC_CACHE = None


class LeadOrchestrator:
    """
    Refactored LeadOrchestrator that uses proper agent implementations
    and provides clean coordination patterns.
    """

    def __init__(self):
        """Initialize orchestrator with proper agent instances."""
        logger.info(
            "🚀 Initializing LeadOrchestrator with proper agent implementations"
        )

        # Initialize agents using proper implementations
        self.agents = {
            AgentType.RETRIEVAL: RetrievalAgent(),
            AgentType.FACT_CHECK: FactCheckAgent(),
            AgentType.SYNTHESIS: SynthesisAgent(),
            AgentType.CITATION: CitationAgent(),
            # Reviewer is implemented as a synthesis-type agent for simplicity
            # and is invoked after synthesis to validate/improve the answer.
            # It is not part of the standard AgentType set used in pipeline stages.
            # We'll call it explicitly in the pipeline.
            "REVIEWER": ReviewerAgent(),
        }

        # Initialize supporting components
        self.token_budget = TokenBudgetController()
        try:
            from shared.core.api.config import get_settings
            ttl_seconds = int(get_settings().query_cache_ttl_seconds)
        except Exception:
            ttl_seconds = 3600
        # Create namespace from core model settings to avoid cross-model contamination
        try:
            from shared.core.config.central_config import get_central_config
            cfg = get_central_config()
            namespace = "|".join(
                [
                    f"openai={getattr(cfg, 'openai_model', '')}",
                    f"anthropic={getattr(cfg, 'anthropic_model', '')}",
                    f"ollama={getattr(cfg, 'ollama_model', '')}",
                    f"dyn={getattr(cfg, 'use_dynamic_selection', True)}",
                    f"free={getattr(cfg, 'prioritize_free_models', True)}",
                ]
            )
        except Exception:
            namespace = "default"

        self.semantic_cache = SemanticCacheManager(ttl_seconds=ttl_seconds, namespace=namespace)
        # Expose global reference for observability
        global GLOBAL_SEMANTIC_CACHE
        GLOBAL_SEMANTIC_CACHE = self.semantic_cache
        self.response_aggregator = ResponseAggregator()

        logger.info("✅ LeadOrchestrator initialized successfully")

    async def process_query(
        self, query: str, user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for processing queries through the multi-agent pipeline.

        Args:
            query: The user's question
            user_context: Optional user context and preferences

        Returns:
            Dict containing the answer, confidence, citations, and metadata
        """
        start_time = time.time()

        try:
            # Create query context
            context = QueryContext(
                query=query, user_context=user_context or {}, trace_id=str(uuid.uuid4())
            )
            
            # Log query received
            log_query_event(logger, query, "received", 
                          query_id=context.trace_id, 
                          user_context=user_context)
            
            # Check cache first
            cached_response = await self.semantic_cache.get_cached_response(query)
            if cached_response:
                logger.info("Cache hit for query", query_id=context.trace_id)
                return {
                    "success": True,
                    "answer": cached_response["answer"],
                    "sources": cached_response.get("sources", []),
                    "verification": cached_response.get("verification", {}),
                    "metadata": {
                        **cached_response.get("metadata", {}),
                        "cache_status": "Hit",
                        "llm_provider": "cached"
                    },
                    "execution_time_ms": int((time.time() - start_time) * 1000)
                }

            # Continue with full processing if not cached
            logger.info("Cache miss, processing query", query_id=context.trace_id)

            # Allocate token budget with error handling
            try:
                query_budget = await self.token_budget.allocate_budget_for_query(query)
                logger.info(f"Allocated {query_budget} tokens for query", query_id=context.trace_id)
            except Exception as budget_error:
                logger.error(f"Token budget allocation failed: {budget_error}", exc_info=True)
                query_budget = 1000  # Fallback budget
                logger.warning(f"Using fallback budget of {query_budget} tokens", query_id=context.trace_id)

            # Analyze and plan execution with error handling
            try:
                plan = await self.analyze_and_plan(context)
            except Exception as plan_error:
                logger.error(f"Query analysis and planning failed: {plan_error}", exc_info=True)
                # Use default pipeline plan
                plan = {
                    "execution_pattern": "pipeline",
                    "agent_sequence": [AgentType.RETRIEVAL, AgentType.SYNTHESIS],
                    "timeout": 30.0
                }
                logger.warning("Using default pipeline plan", query_id=context.trace_id)

            # Execute based on plan with comprehensive error handling
            try:
                if plan["execution_pattern"] == "pipeline":
                    result = await self.execute_pipeline(context, plan, query_budget)
                elif plan["execution_pattern"] == "fork_join":
                    result = await self.execute_fork_join(context, plan, query_budget)
                elif plan["execution_pattern"] == "scatter_gather":
                    result = await self.execute_scatter_gather(context, plan, query_budget)
                else:
                    result = await self.execute_pipeline(
                        context, plan, query_budget
                    )  # Default to pipeline
            except asyncio.TimeoutError as timeout_error:
                logger.error(f"Query execution timed out: {timeout_error}", exc_info=True)
                return {
                    "success": False,
                    "error": "Query processing timed out. Please try again with a simpler query.",
                    "answer": "",
                    "confidence": 0.0,
                    "citations": [],
                    "metadata": {
                        "trace_id": context.trace_id,
                        "execution_time_ms": int((time.time() - start_time) * 1000),
                        "error_type": "timeout_error"
                    }
                }
            except ConnectionError as conn_error:
                logger.error(f"Connection error during query execution: {conn_error}", exc_info=True)
                return {
                    "success": False,
                    "error": "External service connection failed. Please try again later.",
                    "answer": "",
                    "confidence": 0.0,
                    "citations": [],
                    "metadata": {
                        "trace_id": context.trace_id,
                        "execution_time_ms": int((time.time() - start_time) * 1000),
                        "error_type": "connection_error"
                    }
                }
            except Exception as exec_error:
                logger.error(f"Query execution failed: {exec_error}", exc_info=True)
                return {
                    "success": False,
                    "error": "Query processing failed. Please try again later.",
                    "answer": "",
                    "confidence": 0.0,
                    "citations": [],
                    "metadata": {
                        "trace_id": context.trace_id,
                        "execution_time_ms": int((time.time() - start_time) * 1000),
                        "error_type": "execution_error"
                    }
                }

            # Aggregate results with enhanced aggregator
            try:
                final_response = self.response_aggregator.aggregate_pipeline_results(
                    result, context
                )
            except Exception as agg_error:
                logger.error(f"Response aggregation failed: {agg_error}", exc_info=True)
                return {
                    "success": False,
                    "error": "Response processing failed. Please try again later.",
                    "answer": "",
                    "confidence": 0.0,
                    "citations": [],
                    "metadata": {
                        "trace_id": context.trace_id,
                        "execution_time_ms": int((time.time() - start_time) * 1000),
                        "error_type": "aggregation_error"
                    }
                }

            # Track token usage with error handling
            try:
                total_tokens = (
                    final_response.get("metadata", {})
                    .get("token_usage", {})
                    .get("total", 0)
                )
                await self.token_budget.track_usage(AgentType.ORCHESTRATOR, total_tokens)
            except Exception as track_error:
                logger.warning(f"Token usage tracking failed: {track_error}", query_id=context.trace_id)

            # Cache successful response with error handling
            if final_response.get("success", False):
                try:
                    await self.semantic_cache.cache_response(query, final_response)
                except Exception as cache_error:
                    logger.warning(f"Response caching failed: {cache_error}", query_id=context.trace_id)

            return final_response

        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            return {
                "success": False,
                "error": f"Query processing failed: {str(e)}",
                "answer": "",
                "confidence": 0.0,
                "citations": [],
                "metadata": {
                    "trace_id": (
                        context.trace_id if "context" in locals() else str(uuid.uuid4())
                    ),
                    "execution_time_ms": int((time.time() - start_time) * 1000),
                },
            }

    async def analyze_and_plan(self, context: QueryContext) -> Dict[str, Any]:
        """
        Analyze query and create execution plan.

        Args:
            context: Query context

        Returns:
            Execution plan
        """
        # Simple planning based on query characteristics
        query_lower = context.query.lower()

        # Determine execution pattern
        if any(
            word in query_lower for word in ["compare", "versus", "vs", "difference"]
        ):
            execution_pattern = "fork_join"
        elif any(word in query_lower for word in ["research", "study", "analysis"]):
            execution_pattern = "scatter_gather"
        else:
            execution_pattern = "pipeline"

        # Define agent sequence
        agents_sequence = [
            AgentType.RETRIEVAL,
            AgentType.FACT_CHECK,
            AgentType.SYNTHESIS,
            AgentType.CITATION,
        ]

        return {
            "execution_pattern": execution_pattern,
            "agents_sequence": agents_sequence,
            "estimated_tokens": len(context.query.split()) * 10,
        }

    async def execute_pipeline(
        self, context: QueryContext, plan: Dict[str, Any], query_budget: int
    ) -> Dict[AgentType, AgentResult]:
        """
        Execute the agent pipeline with proper error handling and timeouts.

        Args:
            context: Query context with user information
            plan: Execution plan from planning phase
            query_budget: Token budget for the query

        Returns:
            Results from all agents in the pipeline
        """
        results = {}
        pipeline_start_time = time.time()

        try:
            # Phase 1: Parallel retrieval and entity extraction
            results = await self._execute_retrieval_phase_parallel(context, results)

            # Phase 2: Fact checking (depends on retrieval)
            results = await self._execute_fact_checking_phase(context, results)

            # Phase 3: Synthesis (depends on fact checking)
            results = await self._execute_synthesis_phase(context, results)

            # Phase 4: Citation (depends on synthesis and retrieval)
            results = await self._execute_citation_phase(context, results)

            # Phase 5: Expert review (depends on synthesis)
            results = await self._execute_reviewer_phase(context, results)

            # Log pipeline completion
            total_time = time.time() - pipeline_start_time
            logger.info(
                f"Pipeline completed in {total_time:.2f}s",
                extra={"context": context.query, "total_agents": len(results)},
            )

            return results

        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            # Return partial results with error information
            return self._handle_pipeline_failure(results, str(e))

    async def _execute_retrieval_phase_parallel(
        self, context: QueryContext, results: Dict[AgentType, AgentResult]
    ) -> Dict[AgentType, AgentResult]:
        """Execute the retrieval phase with parallel entity extraction and retrieval."""
        logger.info("Phase 1: Parallel retrieval and entity extraction")

        try:
            # Execute entity extraction and retrieval in parallel
            entity_task = asyncio.create_task(
                asyncio.wait_for(
                    self._extract_entities_parallel(context.query), 
                    timeout=10
                )
            )
            
            # Prepare retrieval task
            retrieval_task_data = {
                "query": context.query,
                "max_tokens": context.user_context.get("max_tokens", 4000),
            }
            
            retrieval_task = asyncio.create_task(
                asyncio.wait_for(
                    self.agents[AgentType.RETRIEVAL].process_task(retrieval_task_data, context),
                    timeout=15,
                )
            )

            # Execute both tasks in parallel
            entities, retrieval_result = await asyncio.gather(
                entity_task, 
                retrieval_task,
                return_exceptions=True
            )

            # Handle entity extraction result
            if isinstance(entities, Exception):
                logger.error(f"Entity extraction failed: {entities}")
                entities = []
            else:
                logger.info(f"Extracted {len(entities)} entities")

            # Handle retrieval result
            if isinstance(retrieval_result, Exception):
                logger.error(f"Retrieval failed: {retrieval_result}")
                results[AgentType.RETRIEVAL] = self._create_error_result(
                    f"Retrieval failed: {str(retrieval_result)}"
                )
            else:
                results[AgentType.RETRIEVAL] = retrieval_result
                
                # Update retrieval result with entities if successful
                if retrieval_result.success and hasattr(retrieval_result, 'data'):
                    retrieval_result.data['entities'] = entities

        except asyncio.TimeoutError:
            logger.error("Retrieval phase timed out")
            results[AgentType.RETRIEVAL] = self._create_timeout_result(
                "Retrieval timed out", 15000
            )
        except Exception as e:
            logger.error(f"Retrieval phase failed: {e}")
            results[AgentType.RETRIEVAL] = self._create_error_result(
                f"Retrieval failed: {str(e)}"
            )

        return results

    async def _execute_reviewer_phase(
        self, context: QueryContext, results: Dict[AgentType, AgentResult]
    ) -> Dict[AgentType, AgentResult]:
        """Execute expert reviewer to validate and improve the answer."""
        logger.info("Phase 5: Expert Review")

        # Check if reviewer is enabled
        try:
            from shared.core.config.central_config import get_central_config
            config = get_central_config()
            if not config.enable_reviewer_agent:
                logger.info("Reviewer agent disabled in config")
                return results
        except Exception:
            logger.warning("Could not check reviewer config, proceeding with reviewer")

        # Skip if synthesis failed
        if (
            AgentType.SYNTHESIS not in results
            or not results[AgentType.SYNTHESIS].success
        ):
            logger.warning("Skipping review due to synthesis failure")
            return results

        try:
            draft_answer = (
                results[AgentType.SYNTHESIS].data.get("answer")
                or results[AgentType.SYNTHESIS].data.get("response", "")
            )
            sources = []
            if AgentType.RETRIEVAL in results and results[AgentType.RETRIEVAL].success:
                sources = results[AgentType.RETRIEVAL].data.get("documents", [])

            review_task = {
                "question": context.query,
                "draft_answer": draft_answer,
                "sources": sources,
            }

            reviewer = self.agents.get("REVIEWER")
            review_result = await asyncio.wait_for(
                reviewer.process_task(review_task, context), timeout=20
            )

            # If reviewer approves with small tweaks, or suggests improved final answer
            if review_result.get("success"):
                improved = review_result.get("data", {})
                approved = improved.get("approved", False)
                final_answer = improved.get("final_answer") or draft_answer
                feedback = improved.get("feedback", "")

                # Merge into synthesis result for downstream usage
                synth = results[AgentType.SYNTHESIS]
                synth.data["answer"] = final_answer
                synth.data["review_feedback"] = feedback
                synth.confidence = max(synth.confidence, float(improved.get("confidence", 0.6)))
                results[AgentType.SYNTHESIS] = synth

        except asyncio.TimeoutError:
            logger.warning("Reviewer phase timed out; using draft answer")
        except Exception as e:
            logger.warning(f"Reviewer phase failed; using draft answer: {e}")

        return results

    async def _execute_fact_checking_phase(
        self, context: QueryContext, results: Dict[AgentType, AgentResult]
    ) -> Dict[AgentType, AgentResult]:
        """Execute the fact checking phase."""
        logger.info("Phase 2: Fact checking")

        # Skip if retrieval failed
        if (
            AgentType.RETRIEVAL not in results
            or not results[AgentType.RETRIEVAL].success
        ):
            logger.warning("Skipping fact checking due to retrieval failure")
            results[AgentType.FACT_CHECK] = self._create_error_result(
                "Skipped due to retrieval failure"
            )
            return results

        try:
            # Prepare fact checking task
            fact_check_task = self._prepare_task_for_agent(
                AgentType.FACT_CHECK, results[AgentType.RETRIEVAL], context
            )

            # Execute fact checking with timeout
            fact_check_result = await asyncio.wait_for(
                self.agents[AgentType.FACT_CHECK].process_task(fact_check_task, context),
                timeout=20,
            )
            results[AgentType.FACT_CHECK] = fact_check_result

            if not fact_check_result.success:
                logger.warning(f"Fact checking failed: {fact_check_result.error}")

        except asyncio.TimeoutError:
            logger.error("Fact checking phase timed out")
            results[AgentType.FACT_CHECK] = self._create_timeout_result(
                "Fact checking timed out", 20000
            )
        except Exception as e:
            logger.error(f"Fact checking failed: {e}")
            results[AgentType.FACT_CHECK] = self._create_error_result(
                f"Fact checking failed: {str(e)}"
            )

        return results

    async def _execute_synthesis_phase(
        self, context: QueryContext, results: Dict[AgentType, AgentResult]
    ) -> Dict[AgentType, AgentResult]:
        """Execute the synthesis phase."""
        logger.info("Phase 3: Synthesis")

        # Skip if previous phases failed
        if (
            AgentType.RETRIEVAL not in results
            or not results[AgentType.RETRIEVAL].success
        ):
            logger.warning("Skipping synthesis due to retrieval failure")
            results[AgentType.SYNTHESIS] = self._create_error_result(
                "Skipped due to retrieval failure"
            )
            return results

        try:
            # Prepare synthesis task
            synthesis_task = self._prepare_task_for_agent(
                AgentType.SYNTHESIS, results[AgentType.RETRIEVAL], context
            )

            # Add fact checking results if available
            if (
                AgentType.FACT_CHECK in results
                and results[AgentType.FACT_CHECK].success
            ):
                synthesis_task["fact_check_results"] = results[AgentType.FACT_CHECK].data

            # Execute synthesis with timeout
            synthesis_result = await asyncio.wait_for(
                self.agents[AgentType.SYNTHESIS].process_task(synthesis_task, context),
                timeout=30,
            )
            results[AgentType.SYNTHESIS] = synthesis_result

            if not synthesis_result.success:
                logger.warning(f"Synthesis failed: {synthesis_result.error}")

        except asyncio.TimeoutError:
            logger.error("Synthesis phase timed out")
            results[AgentType.SYNTHESIS] = self._create_timeout_result(
                "Synthesis timed out", 30000
            )
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            results[AgentType.SYNTHESIS] = self._create_error_result(
                f"Synthesis failed: {str(e)}"
            )

        return results

    async def _execute_citation_phase(
        self, context: QueryContext, results: Dict[AgentType, AgentResult]
    ) -> Dict[AgentType, AgentResult]:
        """Execute the citation phase."""
        logger.info("Phase 4: Citation")

        # Skip if synthesis failed
        if (
            AgentType.SYNTHESIS not in results
            or not results[AgentType.SYNTHESIS].success
        ):
            logger.warning("Skipping citation due to synthesis failure")
            results[AgentType.CITATION] = self._create_error_result(
                "Skipped due to synthesis failure"
            )
            return results

        try:
            # Prepare citation task
            citation_task = self._prepare_task_for_agent(
                AgentType.CITATION, results[AgentType.SYNTHESIS], context
            )

            # Add retrieval results for source information
            if (
                AgentType.RETRIEVAL in results
                and results[AgentType.RETRIEVAL].success
            ):
                citation_task["retrieval_results"] = results[AgentType.RETRIEVAL].data

            # Execute citation with timeout
            citation_result = await asyncio.wait_for(
                self.agents[AgentType.CITATION].process_task(citation_task, context),
                timeout=15,
            )
            results[AgentType.CITATION] = citation_result

            if not citation_result.success:
                logger.warning(f"Citation failed: {citation_result.error}")

        except asyncio.TimeoutError:
            logger.error("Citation phase timed out")
            results[AgentType.CITATION] = self._create_timeout_result(
                "Citation timed out", 15000
            )
        except Exception as e:
            logger.error(f"Citation failed: {e}")
            results[AgentType.CITATION] = self._create_error_result(
                f"Citation failed: {str(e)}"
            )

        return results

    def _create_timeout_result(
        self, message: str, execution_time_ms: int
    ) -> AgentResult:
        """Create a standardized timeout result."""
        return AgentResult(
            success=False,
            data={},
            error=message,
            confidence=0.0,
            execution_time_ms=execution_time_ms,
        )

    def _create_error_result(self, message: str) -> AgentResult:
        """Create a standardized error result."""
        return AgentResult(
            success=False, data={}, error=message, confidence=0.0, execution_time_ms=0
        )

    def _handle_pipeline_failure(
        self, partial_results: Dict[AgentType, AgentResult], error_message: str
    ) -> Dict[AgentType, AgentResult]:
        """Handle pipeline failure by returning partial results with error information."""
        # Ensure all agent types have results (even if failed)
        for agent_type in [
            AgentType.RETRIEVAL,
            AgentType.FACT_CHECK,
            AgentType.SYNTHESIS,
            AgentType.CITATION,
        ]:
            if agent_type not in partial_results:
                partial_results[agent_type] = self._create_error_result(
                    f"Pipeline failed: {error_message}"
                )

        return partial_results

    async def _extract_entities_parallel(self, query: str) -> List[Dict[str, Any]]:
        """Extract entities in parallel (if not already done by retrieval agent)."""
        # This is a lightweight operation that can run in parallel
        await asyncio.sleep(0.01)  # Simulate processing
        return [{"text": "parallel_entity", "type": "PROPER_NOUN", "confidence": 0.8}]

    async def _prepare_synthesis_data(
        self, documents: List[Dict[str, Any]], query: str
    ) -> Dict[str, Any]:
        """Prepare synthesis data in parallel."""
        # This could include document summarization, relevance scoring, etc.
        await asyncio.sleep(0.05)  # Simulate processing

        return {
            "prepared_documents": documents[:10],  # Top 10 most relevant
            "summary": f"Prepared {len(documents)} documents for synthesis",
            "relevance_scores": [doc.get("score", 0.5) for doc in documents[:10]],
        }

    def _prepare_synthesis_input(
        self, results: Dict[AgentType, AgentResult], context: QueryContext
    ) -> Dict[str, Any]:
        """Prepare input for synthesis agent."""
        verified_facts = []
        if AgentType.FACT_CHECK in results and results[AgentType.FACT_CHECK].success:
            verified_facts = results[AgentType.FACT_CHECK].data.get(
                "verified_facts", []
            )

        # Get source documents from retrieval phase for fact checking
        source_docs = []
        if AgentType.RETRIEVAL in results and results[AgentType.RETRIEVAL].success:
            source_docs = results[AgentType.RETRIEVAL].data.get("documents", [])

        # Use prepared synthesis data if available
        synthesis_prep = None
        for key, result in results.items():
            if key == "synthesis_prep" and result.success:
                synthesis_prep = result.data
                break

        return {
            "verified_facts": verified_facts,
            "query": context.query,
            "source_docs": source_docs,  # Add source documents for fact checking
            "synthesis_params": {
                "style": "concise",
                "max_length": 1000,
                "prepared_data": synthesis_prep,
            },
        }

    async def execute_fork_join(
        self, context: QueryContext, plan: Dict[str, Any], query_budget: int
    ) -> Dict[AgentType, AgentResult]:
        """
        Execute agents in fork-join pattern for independent operations.
        
        This pattern is useful when agents can work independently and their
        results can be combined later.
        """
        logger.info("Executing fork-join pattern")
        
        # Define independent agent groups
        independent_groups = [
            [AgentType.RETRIEVAL],  # Retrieval can work independently
            [AgentType.FACT_CHECK],  # Fact checking can work independently
        ]
        
        # Execute independent groups in parallel
        group_tasks = []
        for group in independent_groups:
            group_task = asyncio.create_task(
                self._execute_agent_group_parallel(group, context, plan, query_budget)
            )
            group_tasks.append(group_task)
        
        # Wait for all groups to complete
        group_results = await asyncio.gather(*group_tasks, return_exceptions=True)
        
        # Combine results
        results = {}
        for i, group_result in enumerate(group_results):
            if isinstance(group_result, Exception):
                logger.error(f"Agent group {i} failed: {group_result}")
                # Create error results for the group
                for agent_type in independent_groups[i]:
                    results[agent_type] = self._create_error_result(
                        f"Agent group failed: {str(group_result)}"
                    )
            else:
                results.update(group_result)
        
        # Execute dependent phases
        if AgentType.RETRIEVAL in results and results[AgentType.RETRIEVAL].success:
            # Synthesis depends on retrieval
            synthesis_result = await self._execute_synthesis_phase(context, results)
            results.update(synthesis_result)
            
            # Citation depends on synthesis
            if AgentType.SYNTHESIS in results and results[AgentType.SYNTHESIS].success:
                citation_result = await self._execute_citation_phase(context, results)
                results.update(citation_result)
        
        return results

    async def _execute_agent_group_parallel(
        self, 
        agent_types: List[AgentType], 
        context: QueryContext, 
        plan: Dict[str, Any], 
        query_budget: int
    ) -> Dict[AgentType, AgentResult]:
        """Execute a group of agents in parallel."""
        results = {}
        
        # Create tasks for each agent in the group
        agent_tasks = []
        for agent_type in agent_types:
            task = asyncio.create_task(
                self._execute_single_agent(agent_type, context, plan, query_budget)
            )
            agent_tasks.append((agent_type, task))
        
        # Execute all agents in parallel
        for agent_type, task in agent_tasks:
            try:
                result = await asyncio.wait_for(task, timeout=20)
                results[agent_type] = result
            except asyncio.TimeoutError:
                logger.error(f"Agent {agent_type} timed out")
                results[agent_type] = self._create_timeout_result(
                    f"{agent_type} timed out", 20000
                )
            except Exception as e:
                logger.error(f"Agent {agent_type} failed: {e}")
                results[agent_type] = self._create_error_result(
                    f"{agent_type} failed: {str(e)}"
                )
        
        return results

    async def _execute_single_agent(
        self, 
        agent_type: AgentType, 
        context: QueryContext, 
        plan: Dict[str, Any], 
        query_budget: int
    ) -> AgentResult:
        """Execute a single agent with proper error handling."""
        try:
            # Prepare task for the agent
            task = self._prepare_task_for_agent(agent_type, None, context)
            
            # Execute agent
            result = await self.agents[agent_type].process_task(task, context)
            return result
            
        except Exception as e:
            logger.error(f"Agent {agent_type} execution failed: {e}")
            return self._create_error_result(f"Agent {agent_type} failed: {str(e)}")

    async def execute_scatter_gather(
        self, context: QueryContext, plan: Dict[str, Any], query_budget: int
    ) -> Dict[AgentType, AgentResult]:
        """
        Execute scatter-gather pattern for distributed processing.
        
        This pattern is useful when the same operation needs to be performed
        on multiple data sources or with different parameters.
        """
        logger.info("Executing scatter-gather pattern")
        
        # Detect query domains for parallel processing
        domains = await self._detect_query_domains(context.query)
        
        if not domains:
            # Fall back to standard pipeline
            return await self.execute_pipeline(context, plan, query_budget)
        
        # Generate domain-specific queries
        domain_queries = await self._generate_domain_queries(context.query, domains)
        
        # Execute queries for each domain in parallel
        domain_tasks = []
        for domain, query in domain_queries.items():
            # Create context for this domain
            domain_context = QueryContext(
                query=query,
                user_context=context.user_context,
                trace_id=f"{context.trace_id}-{domain}"
            )
            
            # Create task for this domain
            task = asyncio.create_task(
                self._execute_domain_query(domain, domain_context, plan, query_budget)
            )
            domain_tasks.append((domain, task))
        
        # Wait for all domain queries to complete
        domain_results = {}
        for domain, task in domain_tasks:
            try:
                result = await asyncio.wait_for(task, timeout=30)
                domain_results[domain] = result
            except asyncio.TimeoutError:
                logger.error(f"Domain {domain} query timed out")
                domain_results[domain] = self._create_timeout_result(
                    f"Domain {domain} timed out", 30000
                )
            except Exception as e:
                logger.error(f"Domain {domain} query failed: {e}")
                domain_results[domain] = self._create_error_result(
                    f"Domain {domain} failed: {str(e)}"
                )
        
        # Gather and synthesize results
        return await self._synthesize_domain_results(domain_results, context)

    async def _execute_domain_query(
        self, 
        domain: str, 
        context: QueryContext, 
        plan: Dict[str, Any], 
        query_budget: int
    ) -> AgentResult:
        """Execute a query for a specific domain."""
        try:
            # Execute retrieval for this domain
            retrieval_task = {
                "query": context.query,
                "domain": domain,
                "max_tokens": context.user_context.get("max_tokens", 2000),
            }
            
            retrieval_result = await asyncio.wait_for(
                self.agents[AgentType.RETRIEVAL].process_task(retrieval_task, context),
                timeout=15,
            )
            
            if not retrieval_result.success:
                return retrieval_result
            
            # Execute synthesis for this domain
            synthesis_task = self._prepare_task_for_agent(
                AgentType.SYNTHESIS, retrieval_result, context
            )
            synthesis_task["domain"] = domain
            
            synthesis_result = await asyncio.wait_for(
                self.agents[AgentType.SYNTHESIS].process_task(synthesis_task, context),
                timeout=20,
            )
            
            return synthesis_result
            
        except Exception as e:
            logger.error(f"Domain {domain} query execution failed: {e}")
            return self._create_error_result(f"Domain {domain} failed: {str(e)}")

    async def _synthesize_domain_results(
        self, 
        domain_results: Dict[str, AgentResult], 
        context: QueryContext
    ) -> Dict[AgentType, AgentResult]:
        """Synthesize results from multiple domains."""
        # Filter successful results
        successful_results = {
            domain: result for domain, result in domain_results.items()
            if result.success
        }
        
        if not successful_results:
            return {
                AgentType.RETRIEVAL: self._create_error_result("All domains failed"),
                AgentType.SYNTHESIS: self._create_error_result("All domains failed"),
            }
        
        # Combine domain results
        combined_data = {
            "domains": list(successful_results.keys()),
            "results": successful_results,
            "total_domains": len(domain_results),
            "successful_domains": len(successful_results),
        }
        
        # Create combined result
        combined_result = AgentResult(
            success=True,
            data=combined_data,
            confidence=sum(r.confidence for r in successful_results.values()) / len(successful_results),
            execution_time_ms=sum(r.execution_time_ms for r in successful_results.values()),
            tokens_used=sum(r.tokens_used for r in successful_results.values()),
        )
        
        return {
            AgentType.RETRIEVAL: combined_result,
            AgentType.SYNTHESIS: combined_result,
        }

    def _prepare_task_for_agent(
        self,
        agent_type: AgentType,
        previous_result: Optional[AgentResult],
        context: QueryContext,
    ) -> Dict[str, Any]:
        """
        Prepare task data for a specific agent.

        Args:
            agent_type: Type of agent to prepare task for
            previous_result: Result from previous agent (if any)
            context: Query context

        Returns:
            Task data for the agent
        """
        if agent_type == AgentType.RETRIEVAL:
            return {"query": context.query, "search_type": "hybrid", "top_k": 20}
        elif agent_type == AgentType.FACT_CHECK:
            documents = (
                previous_result.data.get("documents", []) if previous_result else []
            )
            return {"documents": documents, "query": context.query}
        elif agent_type == AgentType.SYNTHESIS:
            verified_facts = (
                previous_result.data.get("verified_facts", [])
                if previous_result
                else []
            )
            return {
                "verified_facts": verified_facts,
                "query": context.query,
                "synthesis_params": {"style": "concise", "max_length": 1000},
            }
        elif agent_type == AgentType.CITATION:
            answer = (
                previous_result.data.get(
                    "response", previous_result.data.get("answer", "")
                )
                if previous_result
                else ""
            )
            sources = (
                previous_result.data.get("documents", []) if previous_result else []
            )
            return {"content": answer, "sources": sources, "style": "APA"}
        else:
            return {"query": context.query}

    def _merge_retrieval_results(self, results: List[AgentResult]) -> AgentResult:
        """
        Merge multiple retrieval results with deduplication and ranking.

        Args:
            results: List of retrieval results

        Returns:
            Merged result with deduplicated documents
        """
        all_documents = []

        for result in results:
            if result.success:
                all_documents.extend(result.data.get("documents", []))

        # Deduplicate by content
        seen_contents = set()
        unique_documents = []

        for doc in all_documents:
            content_hash = hash(doc.get("content", ""))
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                unique_documents.append(doc)

        # Sort by relevance score
        unique_documents.sort(key=lambda x: x.get("score", 0), reverse=True)

        # Take top documents
        final_documents = unique_documents[:20]

        return AgentResult(
            success=True,
            data={"documents": final_documents},
            confidence=min(0.9, len(final_documents) / 20.0),
        )

    async def _detect_query_domains(self, query: str) -> List[str]:
        """
        Detect relevant domains for a query.

        Args:
            query: User query

        Returns:
            List of relevant domains
        """
        # Simple domain detection based on keywords
        query_lower = query.lower()
        domains = []

        if any(
            word in query_lower
            for word in ["science", "research", "study", "experiment"]
        ):
            domains.append("scientific")

        if any(word in query_lower for word in ["news", "current", "recent", "latest"]):
            domains.append("news")

        if any(
            word in query_lower
            for word in ["business", "market", "company", "industry"]
        ):
            domains.append("business")

        if any(
            word in query_lower
            for word in ["academic", "scholarly", "paper", "journal"]
        ):
            domains.append("academic")

        if any(
            word in query_lower
            for word in ["technology", "tech", "software", "digital"]
        ):
            domains.append("technology")

        return domains

    async def _generate_domain_queries(
        self, query: str, domains: List[str]
    ) -> Dict[str, str]:
        """
        Generate domain-specific queries.

        Args:
            query: Original query
            domains: Detected domains

        Returns:
            Domain-specific queries
        """
        domain_queries = {}

        for domain in domains:
            if domain == "scientific":
                domain_queries[domain] = f"scientific research {query}"
            elif domain == "news":
                domain_queries[domain] = f"recent news {query}"
            elif domain == "technology":
                domain_queries[domain] = f"technology {query}"
            elif domain == "academic":
                domain_queries[domain] = f"academic sources {query}"
            elif domain == "business":
                domain_queries[domain] = f"business information {query}"
            else:
                domain_queries[domain] = query

        return domain_queries


# ============================================================================
# Supporting Classes (Simplified)
# ============================================================================


class TokenBudgetController:
    """Enhanced token budget controller with real usage tracking."""

    def __init__(self, daily_budget: int = None):
        self.daily_budget = daily_budget or int(
            os.getenv("DAILY_TOKEN_BUDGET", "100000")
        )
        self.used_today = 0
        self.last_reset = datetime.now().date()
        self.agent_allocations = {
            AgentType.RETRIEVAL: 0.15,  # 15% for retrieval
            AgentType.FACT_CHECK: 0.20,  # 20% for fact-checking
            AgentType.SYNTHESIS: 0.50,  # 50% for synthesis
            AgentType.CITATION: 0.15,  # 15% for citation
        }
        self._lock = asyncio.Lock()

    async def allocate_budget_for_query(self, query: str) -> int:
        """
        Allocate token budget for a query based on length and remaining daily budget.

        Args:
            query: Query string

        Returns:
            Allocated token budget
        """
        async with self._lock:
            # Reset daily usage if it's a new day
            today = datetime.now().date()
            if today > self.last_reset:
                self.used_today = 0
                self.last_reset = today

            # Calculate remaining budget
            remaining_budget = self.daily_budget - self.used_today

            # Allocate based on query length (max 10% of remaining daily budget)
            query_length = len(query.split())
            base_allocation = min(1000, query_length * 10)  # Base allocation
            max_allocation = remaining_budget * 0.1  # Max 10% of remaining

            allocated = min(base_allocation, max_allocation)

            return int(allocated)

    async def track_usage(self, agent_type: AgentType, tokens_used: int):
        """
        Track token usage for an agent.

        Args:
            agent_type: Type of agent that used tokens
            tokens_used: Number of tokens used
        """
        async with self._lock:
            self.used_today += tokens_used

            # Log if usage is high
            if tokens_used > 1000:
                logger.warning(
                    f"High token usage by {agent_type.value}: {tokens_used} tokens"
                )

    async def get_budget_status(self) -> Dict[str, Any]:
        """Get current budget status."""
        async with self._lock:
            return {
                "daily_budget": self.daily_budget,
                "used_today": self.used_today,
                "remaining_today": self.daily_budget - self.used_today,
                "usage_percentage": (self.used_today / self.daily_budget) * 100,
                "last_reset": self.last_reset.isoformat(),
            }

    async def allocate_for_agent(self, agent_type: AgentType, query_budget: int) -> int:
        """
        Allocate portion of query budget for specific agent.

        Args:
            agent_type: Type of agent
            query_budget: Total budget for the query

        Returns:
            Budget allocated for this agent
        """
        allocation_ratio = self.agent_allocations.get(agent_type, 0.1)
        return int(query_budget * allocation_ratio)


class SemanticCacheManager:
    """Enhanced semantic cache manager with embedding-based similarity, TTL and namespacing."""

    def __init__(
        self,
        similarity_threshold: float = 0.85,
        max_cache_size: int = 10000,
        ttl_seconds: int = 3600,
        namespace: str = "default",
    ):
        # cache maps cache_key -> {"response": dict, "created_at": float, "embedding": Optional[List[float]], "query": str}
        self.cache: dict[str, dict] = {}
        self.similarity_threshold = similarity_threshold
        self.max_cache_size = max_cache_size
        self.ttl_seconds = ttl_seconds
        self.namespace = namespace
        self._lock = asyncio.Lock()
        self.access_times: dict[str, float] = {}  # LRU timestamps by cache key
        self.hit_counts: dict[str, int] = {}  # Hit counters by cache key

    async def get_cached_response(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get cached response for query using semantic similarity.

        Args:
            query: Query to search for

        Returns:
            Cached response if similar query found, None otherwise
        """
        async with self._lock:
            # Prune expired entries
            now = time.time()
            expired = [q for q, rec in self.cache.items() if now - rec.get("created_at", now) > self.ttl_seconds]
            for q in expired:
                self.cache.pop(q, None)
                self.access_times.pop(q, None)
                self.hit_counts.pop(q, None)

            # Check exact match first
            key = self._make_key(query)
            if key in self.cache:
                self.access_times[key] = now
                self.hit_counts[key] = self.hit_counts.get(key, 0) + 1
                return self.cache[key]["response"]

            # Check for similar queries using embedding-based similarity
            try:
                from shared.core.agents.llm_client import LLMClient

                llm_client = LLMClient()
                query_embedding = await llm_client.create_embedding(query)

                best_match = None
                best_similarity = 0.0

                for cached_key, record in list(self.cache.items()):
                    # Skip expired just in case
                    if now - record.get("created_at", now) > self.ttl_seconds:
                        continue
                    cached_embedding = record.get("embedding")
                    if cached_embedding is None:
                        # Compute once and store
                        rec_query = record.get("query") or cached_key
                        # strip namespace if included in key
                        if isinstance(rec_query, str) and "::" in rec_query and not record.get("query"):
                            rec_query = rec_query.split("::", 1)[1]
                        cached_embedding = await llm_client.create_embedding(rec_query)
                        record["embedding"] = cached_embedding
                    similarity = self._calculate_cosine_similarity(query_embedding, cached_embedding)

                    if (
                        similarity > self.similarity_threshold
                        and similarity > best_similarity
                    ):
                        best_similarity = similarity
                        best_match = cached_key

                if best_match:
                    self.access_times[best_match] = time.time()
                    self.hit_counts[best_match] = self.hit_counts.get(best_match, 0) + 1
                    logger.info(
                        f"Semantic cache hit: '{query}' matched '{best_match}' (similarity: {best_similarity:.3f})"
                    )
                    return self.cache[best_match]["response"]

            except Exception as e:
                logger.warning(
                    f"Embedding-based similarity failed, falling back to word overlap: {e}"
                )
                # Fallback to word overlap method
                query_words = set(query.lower().split())
                for cached_key in self.cache.keys():
                    cached_words = set(str(cached_key).lower().split())
                    overlap = len(query_words & cached_words) / len(
                        query_words | cached_words
                    )
                    if overlap > 0.7:  # 70% word overlap threshold
                        self.access_times[cached_key] = time.time()
                        self.hit_counts[cached_key] = (
                            self.hit_counts.get(cached_key, 0) + 1
                        )
                        return self.cache[cached_key]["response"]

            return None

    def _calculate_cosine_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        try:
            import numpy as np

            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            return float(similarity)

        except Exception as e:
            logger.error(f"Cosine similarity calculation failed: {e}")
            return 0.0

    async def cache_response(self, query: str, response: Dict[str, Any]):
        """
        Cache response with LRU eviction.

        Args:
            query: Query string
            response: Response to cache
        """
        async with self._lock:
            # Evict least recently used if cache is full
            if len(self.cache) >= self.max_cache_size:
                oldest_query = min(
                    self.access_times.keys(), key=lambda k: self.access_times[k]
                )
                del self.cache[oldest_query]
                del self.access_times[oldest_query]
                if oldest_query in self.hit_counts:
                    del self.hit_counts[oldest_query]

            key = self._make_key(query)
            self.cache[key] = {
                "response": response,
                "created_at": time.time(),
                "embedding": None,
                "query": query,
            }
            self.access_times[key] = time.time()
            self.hit_counts[key] = 0  # Initialize hit count

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics with hit rate tracking."""
        async with self._lock:
            total_hits = sum(self.hit_counts.values())
            total_requests = len(self.access_times) + total_hits  # Rough estimate
            hit_rate = total_hits / max(total_requests, 1)

            return {
                "namespace": self.namespace,
                "size": len(self.cache),
                "max_size": self.max_cache_size,
                "hit_rate": hit_rate,
                "total_hits": total_hits,
                "total_requests": total_requests,
                "oldest_entry": (
                    min(self.access_times.values()) if self.access_times else None
                ),
                "newest_entry": (
                    max(self.access_times.values()) if self.access_times else None
                ),
                "most_hit_key": (
                    max(self.hit_counts.items(), key=lambda x: x[1])
                    if self.hit_counts
                    else None
                ),
            }

    def _make_key(self, query: str) -> str:
        return f"{self.namespace}::{query}"

    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self.cache.clear()
            self.access_times.clear()
            self.hit_counts.clear()

    async def prune(self) -> int:
        """Prune expired entries. Returns number of removed entries."""
        async with self._lock:
            now = time.time()
            to_remove = [k for k, rec in self.cache.items() if now - rec.get("created_at", now) > self.ttl_seconds]
            for k in to_remove:
                self.cache.pop(k, None)
                self.access_times.pop(k, None)
                self.hit_counts.pop(k, None)
            return len(to_remove)


async def get_global_cache_stats() -> Dict[str, Any]:
    try:
        if GLOBAL_SEMANTIC_CACHE is not None:
            return await GLOBAL_SEMANTIC_CACHE.get_cache_stats()
    except Exception:
        pass
    return {"namespace": "none", "size": 0, "max_size": 0, "hit_rate": 0.0, "total_hits": 0, "total_requests": 0}


class ResponseAggregator:
    """Enhanced response aggregator with proper citation integration."""

    def __init__(self):
        # Weighted confidence calculation based on agent importance
        self.agent_weights = {
            AgentType.RETRIEVAL: 0.25,  # Retrieval quality affects overall confidence
            AgentType.FACT_CHECK: 0.30,  # Fact-checking is critical for accuracy
            AgentType.SYNTHESIS: 0.35,  # Synthesis quality is most important
            AgentType.CITATION: 0.10,  # Citations add credibility but less weight
        }

    def aggregate_pipeline_results(
        self, results: Dict[AgentType, AgentResult], context: QueryContext
    ) -> Dict[str, Any]:
        """
        Aggregate results from all agents with enhanced citation handling.

        Args:
            results: Results from each agent
            context: Query context

        Returns:
            Aggregated response with proper citations
        """
        # Check if synthesis succeeded
        synthesis_result = results.get(AgentType.SYNTHESIS)
        if not synthesis_result or not synthesis_result.success:
            return self._create_partial_response(results, context)

        # Convert to standardized data models
        try:
            synthesis_data = synthesis_result.data
            answer = synthesis_data.answer
        except Exception as e:
            logger.warning(f"Failed to convert synthesis data: {e}")
            answer = synthesis_result.data.get(
                "answer", synthesis_result.data.get("response", "")
            )

        # Integrate citations if available
        citation_result = results.get(AgentType.CITATION)
        bibliography = []
        citations = []
        cited_content = None
        if citation_result and citation_result.success:
            try:
                citation_data = citation_result.data
                # Handle both old and new field names
                cited_content = citation_data.get("cited_content", "")
                citations = citation_data.get("citations", [])
                bibliography = citation_data.get("bibliography", citations)
                # Use cited content if available, otherwise use original answer
                if cited_content:
                    answer = cited_content
            except Exception as e:
                logger.warning(f"Failed to extract citation data: {e}")
                # Fallback to direct dictionary access
                cited_content = citation_result.data.get("cited_content", "")
                citations = citation_result.data.get("citations", [])
                bibliography = citation_result.data.get("bibliography", citations)
                if cited_content:
                    answer = cited_content

        # Calculate weighted confidence
        confidence = self._calculate_weighted_confidence(results)

        # Compile token usage
        total_tokens = self._compile_token_usage(results)

        return {
            "success": True,
            "answer": answer,
            "cited_content": cited_content if cited_content else answer,
            "confidence": confidence,
            "citations": citations,  # Include raw citations
            "bibliography": bibliography,  # Formatted bibliography
            "metadata": {
                "agent_results": {
                    agent.value: result.success for agent, result in results.items()
                },
                "token_usage": total_tokens,
                "processing_time_ms": sum(
                    result.execution_time_ms for result in results.values()
                ),
                "trace_id": context.trace_id,
            },
        }

    def _create_partial_response(
        self, results: Dict[AgentType, AgentResult], context: QueryContext
    ) -> Dict[str, Any]:
        """Create response when synthesis fails."""
        # Use the improved error response creator
        error_response = create_pipeline_error_response(
            context,
            "Unable to generate a complete answer due to processing errors.",
            results,
        )

        # Add trace ID and additional metadata
        error_response["metadata"] = {
            "partial_results": True,
            "agent_results": {
                agent.value: result.success for agent, result in results.items()
            },
            "errors": [result.error for result in results.values() if result.error],
            "trace_id": context.trace_id,
        }

        return error_response

    def _calculate_weighted_confidence(
        self, results: Dict[AgentType, AgentResult]
    ) -> float:
        """
        Calculate weighted confidence based on agent importance.

        Args:
            results: Results from each agent

        Returns:
            Weighted confidence score
        """
        total_weight = 0
        weighted_sum = 0

        for agent_type, result in results.items():
            if result.success:
                weight = self.agent_weights.get(agent_type, 0.1)
                weighted_sum += result.confidence * weight
                total_weight += weight

        if total_weight == 0:
            return 0.0

        return weighted_sum / total_weight

    def _compile_token_usage(
        self, results: Dict[AgentType, AgentResult]
    ) -> Dict[str, int]:
        """
        Compile total token usage across all agents.

        Args:
            results: Results from each agent

        Returns:
            Total token usage by type
        """
        total_prompt = 0
        total_completion = 0

        for result in results.values():
            if result.token_usage:
                total_prompt += result.token_usage.get("prompt", 0)
                total_completion += result.token_usage.get("completion", 0)

        return {
            "prompt": total_prompt,
            "completion": total_completion,
            "total": total_prompt + total_completion,
        }
