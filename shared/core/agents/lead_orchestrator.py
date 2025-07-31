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
import importlib
# Import fixes module
lead_orchestrator_fixes = importlib.import_module("services.api_gateway.lead_orchestrator_fixes")
create_safe_agent_result = lead_orchestrator_fixes.create_safe_agent_result
safe_prepare_synthesis_input = lead_orchestrator_fixes.safe_prepare_synthesis_input
handle_agent_failure = lead_orchestrator_fixes.handle_agent_failure
validate_agent_result = lead_orchestrator_fixes.validate_agent_result
create_pipeline_error_response = lead_orchestrator_fixes.create_pipeline_error_response
# orchestrator_workflow_fixes import removed - not needed

# Data models imported as needed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        }

        # Initialize supporting components
        self.token_budget = TokenBudgetController()
        self.semantic_cache = SemanticCacheManager()
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
        trace_id = str(uuid.uuid4())
        logger.info(f"🚀 Starting query processing - Trace ID: {trace_id}")

        try:
            # DEEP DEBUG: Log environment configuration with masking
            logger.info("🔍 DEEP DEBUG: Environment Configuration Check")
            env_vars = {
                "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
                "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
                "DATABASE_URL": os.getenv("DATABASE_URL"),
                "REDIS_URL": os.getenv("REDIS_URL"),
                "LLM_PROVIDER": os.getenv("LLM_PROVIDER", "Not set"),
                "OPENAI_LLM_MODEL": os.getenv("OPENAI_LLM_MODEL", "Not set"),
                "ANTHROPIC_MODEL": os.getenv("ANTHROPIC_MODEL", "Not set"),
            }
            
            for var_name, var_value in env_vars.items():
                if var_value:
                    # Mask sensitive values for security
                    if "KEY" in var_name or "URL" in var_name:
                        masked_value = var_value[:8] + "..." if len(var_value) > 8 else "***"
                        logger.info(f"  ✅ {var_name}: {masked_value}")
                    else:
                        logger.info(f"  ✅ {var_name}: {var_value}")
                else:
                    logger.warning(f"  ⚠️ {var_name}: NOT SET")

            # SANITY CHECK: Validate critical environment variables
            missing_critical = []
            for var_name in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DATABASE_URL", "REDIS_URL"]:
                if not os.getenv(var_name):
                    missing_critical.append(var_name)
            
            if missing_critical:
                error_msg = f"Critical environment variables missing: {', '.join(missing_critical)}"
                logger.error(f"❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "error_type": "configuration_error",
                    "missing_vars": missing_critical,
                    "suggestion": "Please check your environment configuration",
                    "trace_id": trace_id
                }

            # DEEP DEBUG: Test LLM client initialization with detailed error surface
            logger.info("🔍 DEEP DEBUG: Testing LLM Client Initialization")
            try:
                from shared.core.agents.llm_client import LLMClient
                llm_client = LLMClient()
                logger.info(f"✅ LLM Client initialized successfully")
                logger.info(f"Provider: {llm_client.get_provider()}")
                logger.info(f"Model: {llm_client.get_model()}")
                logger.info(f"LLM Name: {llm_client.get_llm_name()}")
                
                # Test basic LLM call with detailed error surface
                logger.info("🔍 DEEP DEBUG: Testing basic LLM call")
                try:
                    test_response = await llm_client.generate_text("Test", max_tokens=10, temperature=0.1)
                    logger.info(f"✅ LLM test call successful: {test_response[:50]}...")
                except Exception as api_error:
                    logger.error(f"❌ LLM API call failed: {api_error}")
                    logger.error(f"API Error type: {type(api_error).__name__}")
                    logger.error(f"API Error details: {str(api_error)}")
                    
                    # Surface specific API errors
                    if "authentication" in str(api_error).lower() or "unauthorized" in str(api_error).lower():
                        return {
                            "success": False,
                            "error": f"LLM API authentication failed. Check your API keys: {str(api_error)}",
                            "error_type": "authentication_error",
                            "suggestion": "Please verify your API keys are correct and have sufficient credits",
                            "trace_id": trace_id
                        }
                    elif "quota" in str(api_error).lower() or "rate limit" in str(api_error).lower():
                        return {
                            "success": False,
                            "error": f"LLM API quota exceeded or rate limited: {str(api_error)}",
                            "error_type": "rate_limit_error",
                            "suggestion": "Please try again later or upgrade your API plan",
                            "trace_id": trace_id
                        }
                    elif "model" in str(api_error).lower():
                        return {
                            "success": False,
                            "error": f"LLM model not found or invalid: {str(api_error)}",
                            "error_type": "model_error",
                            "suggestion": "Please check your model configuration",
                            "trace_id": trace_id
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"LLM API call failed: {str(api_error)}",
                            "error_type": "api_error",
                            "suggestion": "Please check your network connection and try again",
                            "trace_id": trace_id
                        }
                
            except Exception as e:
                logger.error(f"❌ LLM Client initialization failed: {e}")
                logger.error(f"Error type: {type(e).__name__}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return {
                    "success": False,
                    "error": f"LLM Client initialization failed: {str(e)}",
                    "error_type": "initialization_error",
                    "suggestion": "Please check your environment configuration",
                    "trace_id": trace_id
                }

            # Create query context
            context = QueryContext(
                query=query, user_context=user_context or {}, trace_id=trace_id
            )

            # Check cache first
            logger.info("🔍 Checking semantic cache...")
            cached_result = await self.semantic_cache.get_cached_response(query)
            if cached_result:
                logger.info(f"✅ Cache HIT for query: {query[:50]}...")
                return cached_result

            # Allocate token budget
            logger.info("🔍 Allocating token budget...")
            query_budget = await self.token_budget.allocate_budget_for_query(query)
            logger.info(f"✅ Allocated {query_budget} tokens for query")

            # Analyze and plan
            logger.info("🔍 Starting query analysis and planning...")
            try:
            plan = await self.analyze_and_plan(context)
                logger.info(f"✅ Query analysis completed: {plan}")
            except Exception as e:
                logger.error(f"❌ Query analysis failed: {e}")
                return {
                    "success": False,
                    "error": f"Query analysis failed: {str(e)}",
                    "error_type": "analysis_error",
                    "suggestion": "Please try rephrasing your query",
                    "trace_id": trace_id
                }

            # Execute pipeline
            logger.info("🔍 Starting pipeline execution...")
            try:
                results = await self.execute_pipeline(context, plan, query_budget)
                logger.info(f"✅ Pipeline execution completed with {len(results)} agent results")
            except Exception as e:
                logger.error(f"❌ Pipeline execution failed: {e}")
                return {
                    "success": False,
                    "error": f"Pipeline execution failed: {str(e)}",
                    "error_type": "pipeline_error",
                    "suggestion": "Please try again or contact support",
                    "trace_id": trace_id
                }

            # Aggregate results
            logger.info("🔍 Starting result aggregation...")
            try:
                final_result = self.response_aggregator.aggregate_pipeline_results(results, context)
                logger.info(f"✅ Result aggregation completed")
            except Exception as e:
                logger.error(f"❌ Result aggregation failed: {e}")
                return {
                    "success": False,
                    "error": f"Result aggregation failed: {str(e)}",
                    "error_type": "aggregation_error",
                    "suggestion": "Please try again or contact support",
                    "trace_id": trace_id
                }

            # Cache the result
            logger.info("🔍 Caching result...")
            try:
                await self.semantic_cache.cache_response(query, final_result)
                logger.info("✅ Result cached successfully")
            except Exception as e:
                logger.warning(f"⚠️ Failed to cache result: {e}")

            process_time = time.time() - start_time
            logger.info(f"✅ Query processing completed in {process_time:.3f}s")

            return final_result

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"❌ Query processing failed after {process_time:.3f}s: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Trace ID: {trace_id}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            # Return graceful error response with detailed information
            return {
                "success": False,
                "error": f"Unable to generate a complete answer due to processing errors: {str(e)}",
                "error_type": "processing_error",
                "answer": "I apologize, but I encountered an error while processing your query. Please try again or contact support if the issue persists.",
                "confidence": 0.0,
                "citations": [],
                "metadata": {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "processing_time": process_time,
                    "trace_id": trace_id,
                    "debug_info": {
                        "env_vars_checked": bool(env_vars.get("OPENAI_API_KEY")),
                        "llm_client_initialized": "llm_client" in locals(),
                        "pipeline_stage": "unknown"
                    }
                }
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
    ) -> Dict[AgentType, Dict[str, Any]]:
        """
        Execute the multi-agent pipeline with the given plan.

        Args:
            context: Query context
            plan: Execution plan
            query_budget: Token budget for the query

        Returns:
            Dictionary mapping agent types to their results
        """
        results: Dict[AgentType, Dict[str, Any]] = {}

        try:
            # Execute retrieval phase
            results = await self._execute_retrieval_phase(context, results)

            # Execute fact checking phase
            results = await self._execute_fact_checking_phase(context, results)

            # Execute synthesis phase
            results = await self._execute_synthesis_phase(context, results)

            # Execute citation phase
            results = await self._execute_citation_phase(context, results)

            return results

        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            # Return partial results if available
            return results

    async def _execute_retrieval_phase(
        self, context: QueryContext, results: Dict[AgentType, Dict[str, Any]]
    ) -> Dict[AgentType, Dict[str, Any]]:
        """Execute the retrieval phase."""
        phase_start = time.time()
        logger.info("🚀 Phase 1: Starting Retrieval")
        logger.info(f"  Query: {context.query[:100]}...")
        logger.info(f"  Trace ID: {context.trace_id}")

        try:
            # Extract entities for retrieval
            logger.info("  🔍 Extracting entities...")
            entities = await self._extract_entities_parallel(context.query)
            logger.info(f"  ✅ Extracted {len(entities)} entities")

            # Prepare retrieval task
            retrieval_task = {
                "query": context.query,
                "entities": entities,
                "search_type": "hybrid",
                "top_k": 20,
            }
            logger.info("  🔍 Preparing retrieval task...")

            logger.info("  🔍 Executing retrieval agent...")
            retrieval_result = await asyncio.wait_for(
                self.agents[AgentType.RETRIEVAL].process_task(
                    retrieval_task, context
                ),
                timeout=30,
            )
            
            # Ensure result is a dictionary
            retrieval_result = self._ensure_dict_result(retrieval_result, "RETRIEVAL")
            results[AgentType.RETRIEVAL] = retrieval_result

            phase_time = time.time() - phase_start
            if retrieval_result.get("success", False):
                docs_count = len(retrieval_result.get("data", {}).get("documents", []))
                logger.info(f"  ✅ Retrieval completed successfully in {phase_time:.2f}s")
                logger.info(f"  📄 Retrieved {docs_count} documents")
            else:
                logger.error(f"  ❌ Retrieval failed in {phase_time:.2f}s: {retrieval_result.get('error', 'Unknown error')}")

        except asyncio.TimeoutError:
            phase_time = time.time() - phase_start
            logger.error(f"  ❌ Retrieval timed out after {phase_time:.2f}s")
            results[AgentType.RETRIEVAL] = self._create_timeout_result(
                "Retrieval timed out", 30000
            )
        except Exception as e:
            phase_time = time.time() - phase_start
            logger.error(f"  ❌ Retrieval failed after {phase_time:.2f}s: {e}")
            logger.error(f"  Error type: {type(e).__name__}")
            import traceback
            logger.error(f"  Traceback: {traceback.format_exc()}")
            results[AgentType.RETRIEVAL] = self._create_error_result(
                f"Retrieval failed: {str(e)}"
            )

        return results

    async def _execute_fact_checking_phase(
        self, context: QueryContext, results: Dict[AgentType, Dict[str, Any]]
    ) -> Dict[AgentType, Dict[str, Any]]:
        """Execute the fact checking phase."""
        phase_start = time.time()
        logger.info("🚀 Phase 2: Starting Fact checking")
        logger.info(f"  Query: {context.query[:100]}...")
        logger.info(f"  Trace ID: {context.trace_id}")

        # Skip if retrieval failed
        if (
            AgentType.RETRIEVAL not in results
            or not results[AgentType.RETRIEVAL].get("success", False)
        ):
            logger.warning("  ⚠️ Skipping fact checking due to retrieval failure")
            results[AgentType.FACT_CHECK] = self._create_error_result(
                "Skipped due to retrieval failure"
            )
            return results

        try:
            fact_check_task = {
                "documents": results[AgentType.RETRIEVAL].get("data", {}).get("documents", []),
                "query": context.query,
            }
            logger.info(f"  🔍 Preparing fact check task with {len(fact_check_task['documents'])} documents...")

            logger.info("  🔍 Executing fact check agent...")
            fact_check_result = await asyncio.wait_for(
                self.agents[AgentType.FACT_CHECK].process_task(
                    fact_check_task, context
                ),
                timeout=20,
            )
            
            # Ensure result is a dictionary
            fact_check_result = self._ensure_dict_result(fact_check_result, "FACT_CHECK")
            results[AgentType.FACT_CHECK] = fact_check_result

            phase_time = time.time() - phase_start
            if fact_check_result.get("success", False):
                facts_count = len(fact_check_result.get("data", {}).get("verified_facts", []))
                logger.info(f"  ✅ Fact checking completed successfully in {phase_time:.2f}s")
                logger.info(f"  ✅ Verified {facts_count} facts")
            else:
                logger.error(f"  ❌ Fact checking failed in {phase_time:.2f}s: {fact_check_result.get('error', 'Unknown error')}")

        except asyncio.TimeoutError:
            phase_time = time.time() - phase_start
            logger.error(f"  ❌ Fact checking timed out after {phase_time:.2f}s")
            results[AgentType.FACT_CHECK] = self._create_timeout_result(
                "Fact checking timed out", 20000
            )
        except Exception as e:
            phase_time = time.time() - phase_start
            logger.error(f"  ❌ Fact checking failed after {phase_time:.2f}s: {e}")
            logger.error(f"  Error type: {type(e).__name__}")
            import traceback
            logger.error(f"  Traceback: {traceback.format_exc()}")
            results[AgentType.FACT_CHECK] = self._create_error_result(
                f"Fact checking failed: {str(e)}"
            )

        return results

    async def _execute_synthesis_phase(
        self, context: QueryContext, results: Dict[AgentType, Dict[str, Any]]
    ) -> Dict[AgentType, Dict[str, Any]]:
        """Execute the synthesis phase."""
        phase_start = time.time()
        logger.info("🚀 Phase 3: Starting Synthesis")
        logger.info(f"  Query: {context.query[:100]}...")
        logger.info(f"  Trace ID: {context.trace_id}")

        try:
            synthesis_input = self._prepare_synthesis_input(results, context)
            logger.info("  🔍 Preparing synthesis input...")

            logger.info("  🔍 Executing synthesis agent...")
            synthesis_result = await asyncio.wait_for(
                self.agents[AgentType.SYNTHESIS].process_task(synthesis_input, context),
                timeout=15,
            )
            
            # Ensure result is a dictionary
            synthesis_result = self._ensure_dict_result(synthesis_result, "SYNTHESIS")
            results[AgentType.SYNTHESIS] = synthesis_result

            phase_time = time.time() - phase_start
            if synthesis_result.get("success", False):
                answer_length = len(synthesis_result.get("data", {}).get("answer", ""))
                logger.info(f"  ✅ Synthesis completed successfully in {phase_time:.2f}s")
                logger.info(f"  📝 Generated answer with {answer_length} characters")
            else:
                logger.error(f"  ❌ Synthesis failed in {phase_time:.2f}s: {synthesis_result.get('error', 'Unknown error')}")

        except asyncio.TimeoutError:
            phase_time = time.time() - phase_start
            logger.error(f"  ❌ Synthesis timed out after {phase_time:.2f}s")
            results[AgentType.SYNTHESIS] = self._create_timeout_result(
                "Synthesis timed out", 15000
            )
        except Exception as e:
            phase_time = time.time() - phase_start
            logger.error(f"  ❌ Synthesis failed after {phase_time:.2f}s: {e}")
            logger.error(f"  Error type: {type(e).__name__}")
            import traceback
            logger.error(f"  Traceback: {traceback.format_exc()}")
            results[AgentType.SYNTHESIS] = self._create_error_result(
                f"Synthesis failed: {str(e)}"
            )

        return results

    async def _execute_citation_phase(
        self, context: QueryContext, results: Dict[AgentType, Dict[str, Any]]
    ) -> Dict[AgentType, Dict[str, Any]]:
        """Execute the citation phase."""
        phase_start = time.time()
        logger.info("🚀 Phase 4: Starting Citation")
        logger.info(f"  Query: {context.query[:100]}...")
        logger.info(f"  Trace ID: {context.trace_id}")

        # Skip if synthesis failed
        if (
            AgentType.SYNTHESIS not in results
            or not results[AgentType.SYNTHESIS].get("success", False)
        ):
            logger.warning("  ⚠️ Skipping citation due to synthesis failure")
            results[AgentType.CITATION] = self._create_error_result(
                "Skipped due to synthesis failure"
            )
            return results

        try:
            # Prepare citation task with synthesis result and retrieval documents
            synthesis_data = results[AgentType.SYNTHESIS].get("data", {})
            retrieval_data = results[AgentType.RETRIEVAL].get("data", {})
            
            citation_task = {
                "content": synthesis_data.get("answer", ""),
                "sources": retrieval_data.get("documents", []),
                "format": "academic",
            }
            logger.info("  🔍 Preparing citation task...")

            logger.info("  🔍 Executing citation agent...")
            citation_result = await asyncio.wait_for(
                self.agents[AgentType.CITATION].process_task(citation_task, context),
                timeout=10,
            )
            
            # Ensure result is a dictionary
            citation_result = self._ensure_dict_result(citation_result, "CITATION")
            results[AgentType.CITATION] = citation_result

            phase_time = time.time() - phase_start
            if citation_result.get("success", False):
                citations_count = len(citation_result.get("data", {}).get("citations", []))
                logger.info(f"  ✅ Citation completed successfully in {phase_time:.2f}s")
                logger.info(f"  📚 Generated {citations_count} citations")
            else:
                logger.error(f"  ❌ Citation failed in {phase_time:.2f}s: {citation_result.get('error', 'Unknown error')}")

        except asyncio.TimeoutError:
            phase_time = time.time() - phase_start
            logger.error(f"  ❌ Citation timed out after {phase_time:.2f}s")
            results[AgentType.CITATION] = self._create_timeout_result(
                "Citation timed out", 10000
            )
        except Exception as e:
            phase_time = time.time() - phase_start
            logger.error(f"  ❌ Citation failed after {phase_time:.2f}s: {e}")
            logger.error(f"  Error type: {type(e).__name__}")
            import traceback
            logger.error(f"  Traceback: {traceback.format_exc()}")
            results[AgentType.CITATION] = self._create_error_result(
                f"Citation failed: {str(e)}"
            )

        return results

    def _create_timeout_result(
        self, message: str, execution_time_ms: int
    ) -> Dict[str, Any]:
        """Create a timeout result dictionary."""
        return {
            "success": False,
            "data": {},
            "error": f"Timeout: {message}",
            "confidence": 0.0,
            "execution_time_ms": execution_time_ms,
        }

    def _create_error_result(self, message: str) -> Dict[str, Any]:
        """Create an error result dictionary."""
        return {
            "success": False,
            "data": {},
            "error": message,
            "confidence": 0.0,
            "execution_time_ms": 0,
        }

    def _handle_pipeline_failure(
        self, partial_results: Dict[AgentType, Dict[str, Any]], error_message: str
    ) -> Dict[AgentType, Dict[str, Any]]:
        """Handle pipeline failure with partial results."""
        # Create error results for missing agents
        for agent_type in [AgentType.RETRIEVAL, AgentType.FACT_CHECK, AgentType.SYNTHESIS, AgentType.CITATION]:
            if agent_type not in partial_results:
                partial_results[agent_type] = self._create_error_result(
                    f"Agent {agent_type.value} failed to execute"
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
        self, results: Dict[AgentType, Dict[str, Any]], context: QueryContext
    ) -> Dict[str, Any]:
        """Prepare input for synthesis agent."""
        synthesis_input = {
            "query": context.query,
            "verified_facts": [],
            "synthesis_params": {
                "style": "academic",
                "include_sources": True,
                "max_length": 1000,
            },
        }

        # Add verified facts from fact checking
        fact_check_result = results.get(AgentType.FACT_CHECK, {})
        if fact_check_result.get("success", False):
            verified_facts = fact_check_result.get("data", {}).get("verified_facts", [])
            synthesis_input["verified_facts"] = verified_facts

        # Add retrieval documents for context
        retrieval_result = results.get(AgentType.RETRIEVAL, {})
        if retrieval_result.get("success", False):
            documents = retrieval_result.get("data", {}).get("documents", [])
            synthesis_input["documents"] = documents

        return synthesis_input

    async def execute_fork_join(
        self, context: QueryContext, plan: Dict[str, Any], query_budget: int
    ) -> Dict[AgentType, Dict[str, Any]]:
        """Execute agents in parallel and join results."""
        results: Dict[AgentType, Dict[str, Any]] = {}

        # Execute all agents in parallel
        tasks = []
        for agent_type in [AgentType.RETRIEVAL, AgentType.FACT_CHECK]:
            task = self.agents[agent_type].process_task(
                self._prepare_task_for_agent(agent_type, None, context), context
            )
            tasks.append((agent_type, task))

        # Wait for all tasks to complete
        for agent_type, task in tasks:
            try:
                result = await asyncio.wait_for(task, timeout=30)
                results[agent_type] = self._ensure_dict_result(result, agent_type.value)
            except Exception as e:
                logger.error(f"Agent {agent_type.value} failed: {e}")
                results[agent_type] = self._create_error_result(f"Agent {agent_type.value} failed: {str(e)}")

        return results

    async def execute_scatter_gather(
        self, context: QueryContext, plan: Dict[str, Any], query_budget: int
    ) -> Dict[AgentType, Dict[str, Any]]:
        """Execute agents with scatter-gather pattern."""
        results: Dict[AgentType, Dict[str, Any]] = {}

        # Scatter: Execute retrieval agents in parallel
        retrieval_tasks = []
        for search_type in ["vector", "keyword", "graph"]:
            task = self.agents[AgentType.RETRIEVAL].process_task(
                {
                    "query": context.query,
                    "search_type": search_type,
                    "top_k": 10,
                },
                context
            )
            retrieval_tasks.append(task)

        # Gather retrieval results
        retrieval_results = []
        for task in retrieval_tasks:
            try:
                result = await asyncio.wait_for(task, timeout=30)
                retrieval_results.append(self._ensure_dict_result(result, "RETRIEVAL"))
            except Exception as e:
                logger.error(f"Retrieval task failed: {e}")
                retrieval_results.append(self._create_error_result(f"Retrieval failed: {str(e)}"))

        # Merge retrieval results
        merged_retrieval = self._merge_retrieval_results(retrieval_results)
        results[AgentType.RETRIEVAL] = merged_retrieval

        # Execute downstream agents
        if merged_retrieval.get("success", False):
            # Fact checking
            fact_check_result = await self.agents[AgentType.FACT_CHECK].process_task(
                {
                    "documents": merged_retrieval.get("data", {}).get("documents", []),
                "query": context.query,
                },
                context
            )
            results[AgentType.FACT_CHECK] = self._ensure_dict_result(fact_check_result, "FACT_CHECK")

            # Synthesis
            synthesis_result = await self.agents[AgentType.SYNTHESIS].process_task(
                self._prepare_synthesis_input(results, context),
                context
            )
            results[AgentType.SYNTHESIS] = self._ensure_dict_result(synthesis_result, "SYNTHESIS")

        return results

    def _prepare_task_for_agent(
        self,
        agent_type: AgentType,
        previous_result: Optional[Dict[str, Any]],
        context: QueryContext,
    ) -> Dict[str, Any]:
        """Prepare task for a specific agent."""
        base_task = {
                "query": context.query,
            "user_context": context.user_context,
            "trace_id": context.trace_id,
        }

        if previous_result and isinstance(previous_result, dict):
            # Add relevant data from previous result
            if agent_type == AgentType.FACT_CHECK:
                documents = previous_result.get("data", {}).get("documents", [])
                base_task["documents"] = documents
            elif agent_type == AgentType.SYNTHESIS:
                verified_facts = previous_result.get("data", {}).get("verified_facts", [])
                base_task["verified_facts"] = verified_facts
        elif agent_type == AgentType.CITATION:
                answer = previous_result.get("data", {}).get("answer", "")
                base_task["content"] = answer

        return base_task

    def _merge_retrieval_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple retrieval results into a single result."""
        if not results:
            return self._create_error_result("No retrieval results to merge")

        # Merge documents from all results
        all_documents = []
        total_hits = 0
        total_time = 0

        for result in results:
            if isinstance(result, dict) and result.get("success", False):
                documents = result.get("data", {}).get("documents", [])
                all_documents.extend(documents)
                total_hits += result.get("data", {}).get("total_hits", 0)
                total_time += result.get("execution_time_ms", 0)

        # Remove duplicates based on document ID
        seen_ids = set()
        unique_documents = []
        for doc in all_documents:
            doc_id = doc.get("id", doc.get("doc_id", ""))
            if doc_id not in seen_ids:
                unique_documents.append(doc)
                seen_ids.add(doc_id)

        return {
            "success": True,
            "data": {
                "documents": unique_documents,
                "total_hits": total_hits,
                "query_time_ms": total_time,
            },
            "confidence": 0.8 if unique_documents else 0.0,
            "execution_time_ms": total_time,
        }

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

    def _ensure_dict_result(self, result, agent_type: str) -> Dict[str, Any]:
        """Ensure agent result is always a dictionary."""
        if isinstance(result, dict):
            return result
        elif hasattr(result, 'to_dict') and callable(getattr(result, 'to_dict')):
            # Handle AgentResult objects
            logger.info(f"Converting AgentResult to dict for {agent_type}")
            return result.to_dict()
        elif result is None:
            logger.warning(f"Agent {agent_type} returned None")
            return {
                "success": False,
                "error": f"Agent {agent_type} returned None",
                "data": {},
                "confidence": 0.0,
                "execution_time_ms": 0
            }
        elif isinstance(result, bool):
            logger.warning(f"Agent {agent_type} returned boolean: {result}")
            return {
                "success": result,
                "error": f"Agent {agent_type} returned boolean instead of dict",
                "data": {},
                "confidence": 0.0 if not result else 0.5,
                "execution_time_ms": 0
            }
        else:
            logger.warning(f"Agent {agent_type} returned {type(result)}: {result}")
            return {
                "success": False,
                "error": f"Agent {agent_type} returned {type(result)} instead of dict",
                "data": {"raw_result": str(result)},
                "confidence": 0.0,
                "execution_time_ms": 0
            }


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
    """Enhanced semantic cache manager with embedding-based similarity."""

    def __init__(self, similarity_threshold: float = 0.85, max_cache_size: int = 10000):
        self.cache = {}
        self.similarity_threshold = similarity_threshold
        self.max_cache_size = max_cache_size
        self._lock = asyncio.Lock()
        self.access_times = {}  # Track access times for LRU eviction
        self.hit_counts = {}  # Track hit counts for hit rate calculation

    async def get_cached_response(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get cached response for query using semantic similarity.

        Args:
            query: Query to search for

        Returns:
            Cached response if similar query found, None otherwise
        """
        async with self._lock:
            # Check exact match first
            if query in self.cache:
                self.access_times[query] = time.time()
                self.hit_counts[query] = self.hit_counts.get(query, 0) + 1
                return self.cache[query]

            # Check for similar queries using embedding-based similarity
            try:
                from shared.core.agents.llm_client import LLMClient

                llm_client = LLMClient()
                query_embedding = await llm_client.create_embedding(query)

                best_match = None
                best_similarity = 0.0

                for cached_query in self.cache.keys():
                    cached_embedding = await llm_client.create_embedding(cached_query)
                    similarity = self._calculate_cosine_similarity(
                        query_embedding, cached_embedding
                    )

                    if (
                        similarity > self.similarity_threshold
                        and similarity > best_similarity
                    ):
                        best_similarity = similarity
                        best_match = cached_query

                if best_match:
                    self.access_times[best_match] = time.time()
                    self.hit_counts[best_match] = self.hit_counts.get(best_match, 0) + 1
                    logger.info(
                        f"Semantic cache hit: '{query}' matched '{best_match}' (similarity: {best_similarity:.3f})"
                    )
                    return self.cache[best_match]

            except Exception as e:
                logger.warning(
                    f"Embedding-based similarity failed, falling back to word overlap: {e}"
                )
                # Fallback to word overlap method
                query_words = set(query.lower().split())
                for cached_query in self.cache.keys():
                    cached_words = set(cached_query.lower().split())
                    overlap = len(query_words & cached_words) / len(
                        query_words | cached_words
                    )
                    if overlap > 0.7:  # 70% word overlap threshold
                        self.access_times[cached_query] = time.time()
                        self.hit_counts[cached_query] = (
                            self.hit_counts.get(cached_query, 0) + 1
                        )
                        return self.cache[cached_query]

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

            self.cache[query] = response
            self.access_times[query] = time.time()
            self.hit_counts[query] = 0  # Initialize hit count

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics with hit rate tracking."""
        async with self._lock:
            total_hits = sum(self.hit_counts.values())
            total_requests = len(self.access_times) + total_hits  # Rough estimate
            hit_rate = total_hits / max(total_requests, 1)

            return {
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
                "most_hit_query": (
                    max(self.hit_counts.items(), key=lambda x: x[1])
                    if self.hit_counts
                    else None
                ),
            }


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
        self, results: Dict[AgentType, Dict[str, Any]], context: QueryContext
    ) -> Dict[str, Any]:
        """
        Aggregate results from all agents with enhanced citation handling.

        Args:
            results: Results from each agent
            context: Query context

        Returns:
            Aggregated response with proper citations
        """
        # Defensive check: ensure all results are valid
        for agent_type, result in results.items():
            if not isinstance(result, dict):
                logger.warning(f"Non-dict result from {agent_type}: {type(result)}")
                # Wrap non-dict results as safe dict
                results[agent_type] = {
                    "success": False,
                    "result": result,
                    "error": f"Non-dict result from {agent_type}",
                    "data": {}
                }
            elif not isinstance(result.get("data"), dict):
                logger.warning(f"Non-dict data from {agent_type}: {type(result.get('data'))}")
                # Ensure data is a dict
                if result.get("data") is None:
                    result["data"] = {}
                else:
                    result["data"] = {"raw_data": result.get("data")}

        # Check if synthesis succeeded
        synthesis_result = results.get(AgentType.SYNTHESIS)
        if not synthesis_result or not synthesis_result.get("success", False):
            return self._create_partial_response(results, context)

        # Convert to standardized data models
        try:
            synthesis_data = synthesis_result.get("data", {})
            answer = synthesis_data.get("answer", synthesis_data.get("response", ""))
        except Exception as e:
            logger.warning(f"Failed to convert synthesis data: {e}")
            answer = synthesis_result.get("data", {}).get(
                "answer", synthesis_result.get("data", {}).get("response", "")
            )

        # Integrate citations if available
        citation_result = results.get(AgentType.CITATION)
        bibliography = []
        citations = []
        cited_content = None
        if citation_result and citation_result.get("success", False):
            try:
                citation_data = citation_result.get("data", {})
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
                citation_data = citation_result.get("data", {})
                cited_content = citation_data.get("cited_content", "")
                citations = citation_data.get("citations", [])
                bibliography = citation_data.get("bibliography", citations)
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
                    agent.value: result.get("success", False) for agent, result in results.items()
                },
                "token_usage": total_tokens,
                "processing_time_ms": sum(
                    result.get("execution_time_ms", 0) for result in results.values()
                ),
                "trace_id": context.trace_id,
            },
        }

    def _create_partial_response(
        self, results: Dict[AgentType, Dict[str, Any]], context: QueryContext
    ) -> Dict[str, Any]:
        """Create response when synthesis fails."""
        # Use the improved error response creator
        error_response = create_pipeline_error_response(
            context, "Synthesis failed", results
        )
        return error_response

    def _calculate_weighted_confidence(
        self, results: Dict[AgentType, Dict[str, Any]]
    ) -> float:
        """Calculate weighted confidence based on agent results."""
        weights = {
            AgentType.RETRIEVAL: 0.2,
            AgentType.FACT_CHECK: 0.3,
            AgentType.SYNTHESIS: 0.4,
            AgentType.CITATION: 0.1,
        }

        total_confidence = 0.0
        total_weight = 0.0

        for agent_type, result in results.items():
            if agent_type in weights and result.get("success", False):
                confidence = result.get("confidence", 0.0)
                weight = weights[agent_type]
                total_confidence += confidence * weight
                total_weight += weight

        return total_confidence / max(total_weight, 0.1)

    def _compile_token_usage(
        self, results: Dict[AgentType, Dict[str, Any]]
    ) -> Dict[str, int]:
        """Compile token usage from all agents."""
        total_usage = {"prompt": 0, "completion": 0}

        for result in results.values():
            if isinstance(result, dict):
                token_usage = result.get("token_usage", {})
                if isinstance(token_usage, dict):
                    total_usage["prompt"] += token_usage.get("prompt", 0)
                    total_usage["completion"] += token_usage.get("completion", 0)

        return total_usage
