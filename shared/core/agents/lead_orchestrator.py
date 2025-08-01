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
from shared.core.agents.knowledge_graph_agent import KnowledgeGraphAgent
from shared.core.query_classifier import QueryClassifier, QueryClassification, QueryCategory
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
    and provides clean coordination patterns with comprehensive error handling.
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
        
        # Initialize specialized agents
        self.knowledge_graph_agent = KnowledgeGraphAgent()

        # Initialize supporting components
        self.token_budget = TokenBudgetController()
        self.semantic_cache = SemanticCacheManager()
        self.response_aggregator = ResponseAggregator()
        
        # Initialize QueryClassifier for intelligent routing
        self.query_classifier = QueryClassifier()

        # Initialize shutdown state tracking
        self._shutdown_initiated = False
        self._shutdown_completed = False
        self._active_tasks = {}

        # Enhanced error handling configuration
        self.retry_config = {
            AgentType.RETRIEVAL: {"max_retries": 2, "timeout": 30, "backoff_factor": 1.5},
            AgentType.FACT_CHECK: {"max_retries": 1, "timeout": 20, "backoff_factor": 1.0},
            AgentType.SYNTHESIS: {"max_retries": 2, "timeout": 15, "backoff_factor": 1.5},
            AgentType.CITATION: {"max_retries": 1, "timeout": 10, "backoff_factor": 1.0},
        }

        # Fallback strategies configuration
        self.fallback_strategies = {
            AgentType.RETRIEVAL: ["broaden_query", "keyword_search", "knowledge_graph"],
            AgentType.FACT_CHECK: ["skip_verification", "basic_validation"],
            AgentType.SYNTHESIS: ["template_response", "concatenation", "error_message"],
            AgentType.CITATION: ["skip_citations", "basic_formatting"],
        }

        logger.info("✅ LeadOrchestrator initialized successfully")

    async def process_query(
        self, query: str, user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for processing queries through the multi-agent pipeline.
        Enhanced with comprehensive error handling and fallback strategies.

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
            }
            for key, value in env_vars.items():
                if value:
                    masked_value = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
                    logger.info(f"  {key}: {masked_value}")
                else:
                    logger.warning(f"  {key}: NOT SET")

            # Create query context
            context = QueryContext(
                query=query, user_context=user_context or {}, trace_id=trace_id
            )

            # Check cache first
            cached_result = await self.semantic_cache.get_cached_response(query)
            if cached_result:
                logger.info(f"Cache HIT for query: {query[:50]}...")
                return cached_result

            # Allocate token budget
            query_budget = await self.token_budget.allocate_budget_for_query(query)
            logger.info(f"Allocated {query_budget} tokens for query")

            # Analyze and plan execution
            plan = await self.analyze_and_plan(context)

            # Execute based on plan with intelligent routing
            result = await self.execute_with_intelligent_routing(context, plan, query_budget)

            # Aggregate results with enhanced aggregator
            final_response = self.response_aggregator.aggregate_pipeline_results(
                result, context
            )

            # Track token usage
            total_tokens = final_response.get("metadata", {}).get("token_usage", {})
            await self.token_budget.track_usage(AgentType.SYNTHESIS, total_tokens.get("total", 0))

            # Cache the result
            await self.semantic_cache.cache_response(query, final_response)

            processing_time = (time.time() - start_time) * 1000
            final_response["processing_time_ms"] = processing_time
            final_response["trace_id"] = trace_id

            logger.info(f"✅ Query processing completed in {processing_time:.2f}ms")
            return final_response

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error(f"❌ Query processing failed after {processing_time:.2f}ms: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Return comprehensive error response
            return {
                "success": False,
                "error": f"Query processing failed: {str(e)}",
                "error_type": "orchestrator_error",
                "suggestion": "Please try rephrasing your query or contact support if the issue persists.",
                "trace_id": trace_id,
                "processing_time_ms": processing_time,
                "metadata": {
                    "error_details": {
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "trace_id": trace_id
                    }
                }
            }

    async def analyze_and_plan(self, context: QueryContext) -> Dict[str, Any]:
        """Analyze query and create execution plan with intelligent classification."""
        try:
            # Use QueryClassifier for intelligent analysis
            classification = await self.query_classifier.classify_query(context.query)
            
            logger.info(f"🔍 Query Classification Results:")
            logger.info(f"  Category: {classification.category.value}")
            logger.info(f"  Confidence: {classification.confidence:.2f}")
            logger.info(f"  Complexity: {classification.complexity.value}")
            logger.info(f"  Suggested Agents: {classification.suggested_agents}")
            
            # Use classification results for planning
            execution_pattern = classification.routing_hints.get("execution_strategy", "pipeline")
            complexity_score = classification.confidence
            estimated_tokens = classification.routing_hints.get("estimated_tokens", 1000)
            
            # Enhanced plan with classification insights
            plan = {
                "execution_pattern": execution_pattern,
                "complexity_score": complexity_score,
                "estimated_tokens": estimated_tokens,
                "classification": classification.to_dict(),
                "primary_category": classification.category.value,
                "suggested_agents": classification.suggested_agents,
                "routing_hints": classification.routing_hints,
                "priority_level": classification.routing_hints.get("priority_level", "normal"),
                "cache_strategy": classification.routing_hints.get("cache_strategy", "conservative")
            }
            
            logger.info(f"📋 Execution Plan Created:")
            logger.info(f"  Pattern: {execution_pattern}")
            logger.info(f"  Priority: {plan['priority_level']}")
            logger.info(f"  Cache Strategy: {plan['cache_strategy']}")
            
            return plan
            
        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            # Return safe default plan with basic classification
            return {
                "execution_pattern": "pipeline",
                "complexity_score": 0.5,
                "estimated_tokens": 1000,
                "classification": {
                    "category": "unknown",
                    "confidence": 0.3,
                    "complexity": "moderate"
                },
                "primary_category": "unknown",
                "suggested_agents": ["retrieval", "synthesis"],
                "routing_hints": {
                    "execution_strategy": "pipeline",
                    "priority_level": "normal",
                    "cache_strategy": "conservative"
                },
                "priority_level": "normal",
                "cache_strategy": "conservative"
            }

    async def execute_with_intelligent_routing(
        self, context: QueryContext, plan: Dict[str, Any], query_budget: int
    ) -> Dict[AgentType, Dict[str, Any]]:
        """
        Execute query with intelligent routing based on classification.
        
        Args:
            context: Query context
            plan: Execution plan with classification
            query_budget: Token budget for the query
            
        Returns:
            Dictionary mapping agent types to their results
        """
        start_time = time.time()
        results: Dict[AgentType, Dict[str, Any]] = {}
        
        try:
            # Get classification from plan
            classification_data = plan.get("classification", {})
            category = classification_data.get("category", "unknown")
            confidence = classification_data.get("confidence", 0.0)
            
            logger.info(f"🎯 Intelligent Routing - Category: {category}, Confidence: {confidence:.2f}")
            
            # Route based on category
            if category == QueryCategory.KNOWLEDGE_GRAPH.value:
                logger.info("🔗 Routing to Knowledge Graph Agent")
                results = await self._execute_knowledge_graph_route(context, plan, query_budget)
                
            elif category == QueryCategory.CODE.value:
                logger.info("💻 Routing to Code-Specific Processing")
                results = await self._execute_code_route(context, plan, query_budget)
                
            elif category == QueryCategory.ANALYTICAL.value:
                logger.info("📊 Routing to Analytical Processing")
                results = await self._execute_analytical_route(context, plan, query_budget)
                
            elif category == QueryCategory.COMPARATIVE.value:
                logger.info("⚖️ Routing to Comparative Processing")
                results = await self._execute_comparative_route(context, plan, query_budget)
                
            else:
                # Default to general factual processing
                logger.info("📚 Routing to General Factual Processing")
                results = await self._execute_general_factual_route(context, plan, query_budget)
            
            # Apply fallback logic for low-confidence results
            if confidence < 0.4:
                logger.info("🔄 Applying fallback logic due to low confidence")
                results = await self._apply_fallback_logic(context, results, plan, query_budget)
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"✅ Intelligent routing completed in {processing_time:.2f}ms")
            
            return results
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error(f"❌ Intelligent routing failed after {processing_time:.2f}ms: {e}")
            return self._handle_routing_failure(context, str(e))
    
    async def _execute_knowledge_graph_route(
        self, context: QueryContext, plan: Dict[str, Any], query_budget: int
    ) -> Dict[AgentType, Dict[str, Any]]:
        """Execute knowledge graph route for entity-relationship queries."""
        results: Dict[AgentType, Dict[str, Any]] = {}
        
        try:
            # Query knowledge graph agent
            kg_result = await self.knowledge_graph_agent.query(context.query)
            
            # Convert knowledge graph results to document format for synthesis
            documents = []
            if kg_result.entities:
                for entity in kg_result.entities:
                    doc = {
                        "content": f"{entity.name}: {entity.properties.get('description', '')}",
                        "source": "knowledge_graph",
                        "metadata": {
                            "entity_id": entity.id,
                            "entity_type": entity.type,
                            "properties": entity.properties
                        }
                    }
                    documents.append(doc)
            
            if kg_result.relationships:
                for rel in kg_result.relationships:
                    source_entity = next((e for e in kg_result.entities if e.id == rel.source_id), None)
                    target_entity = next((e for e in kg_result.entities if e.id == rel.target_id), None)
                    
                    if source_entity and target_entity:
                        doc = {
                            "content": f"{source_entity.name} {rel.relationship_type} {target_entity.name}: {rel.properties.get('description', '')}",
                            "source": "knowledge_graph",
                            "metadata": {
                                "relationship_type": rel.relationship_type,
                                "source_entity": source_entity.name,
                                "target_entity": target_entity.name,
                                "properties": rel.properties
                            }
                        }
                        documents.append(doc)
            
            # Store knowledge graph results
            results[AgentType.RETRIEVAL] = {
                "success": True,
                "documents": documents,
                "source": "knowledge_graph",
                "confidence": kg_result.confidence,
                "metadata": {
                    "entities_found": len(kg_result.entities),
                    "relationships_found": len(kg_result.relationships),
                    "paths_found": len(kg_result.paths),
                    "query_entities": kg_result.query_entities
                }
            }
            
            # Proceed with synthesis
            results = await self._execute_synthesis_phase_with_retries(context, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Knowledge graph route failed: {e}")
            # Fallback to general retrieval
            return await self._execute_general_factual_route(context, plan, query_budget)
    
    async def _execute_code_route(
        self, context: QueryContext, plan: Dict[str, Any], query_budget: int
    ) -> Dict[AgentType, Dict[str, Any]]:
        """Execute code-specific route for programming queries."""
        results: Dict[AgentType, Dict[str, Any]] = {}
        
        try:
            # For code queries, we can use specialized processing
            # For now, use standard retrieval but with code-specific hints
            retrieval_task = {
                "query": context.query,
                "search_type": "code_specific",
                "top_k": 15,
                "code_focus": True
            }
            
            # Execute retrieval with code focus
            retrieval_result = await self.agents[AgentType.RETRIEVAL].process_task(
                retrieval_task, context
            )
            
            results[AgentType.RETRIEVAL] = retrieval_result
            
            # Proceed with synthesis
            results = await self._execute_synthesis_phase_with_retries(context, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Code route failed: {e}")
            # Fallback to general retrieval
            return await self._execute_general_factual_route(context, plan, query_budget)
    
    async def _execute_analytical_route(
        self, context: QueryContext, plan: Dict[str, Any], query_budget: int
    ) -> Dict[AgentType, Dict[str, Any]]:
        """Execute analytical route for analysis queries."""
        results: Dict[AgentType, Dict[str, Any]] = {}
        
        try:
            # For analytical queries, use enhanced retrieval with fact checking
            retrieval_task = {
                "query": context.query,
                "search_type": "analytical",
                "top_k": 20,
                "analytical_focus": True
            }
            
            # Execute retrieval
            retrieval_result = await self.agents[AgentType.RETRIEVAL].process_task(
                retrieval_task, context
            )
            
            results[AgentType.RETRIEVAL] = retrieval_result
            
            # Add fact checking for analytical queries
            results = await self._execute_fact_checking_phase_with_fallbacks(context, results)
            
            # Proceed with synthesis
            results = await self._execute_synthesis_phase_with_retries(context, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Analytical route failed: {e}")
            # Fallback to general retrieval
            return await self._execute_general_factual_route(context, plan, query_budget)
    
    async def _execute_comparative_route(
        self, context: QueryContext, plan: Dict[str, Any], query_budget: int
    ) -> Dict[AgentType, Dict[str, Any]]:
        """Execute comparative route for comparison queries."""
        results: Dict[AgentType, Dict[str, Any]] = {}
        
        try:
            # For comparative queries, use enhanced retrieval
            retrieval_task = {
                "query": context.query,
                "search_type": "comparative",
                "top_k": 25,
                "comparative_focus": True
            }
            
            # Execute retrieval
            retrieval_result = await self.agents[AgentType.RETRIEVAL].process_task(
                retrieval_task, context
            )
            
            results[AgentType.RETRIEVAL] = retrieval_result
            
            # Proceed with synthesis
            results = await self._execute_synthesis_phase_with_retries(context, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Comparative route failed: {e}")
            # Fallback to general retrieval
            return await self._execute_general_factual_route(context, plan, query_budget)
    
    async def _execute_general_factual_route(
        self, context: QueryContext, plan: Dict[str, Any], query_budget: int
    ) -> Dict[AgentType, Dict[str, Any]]:
        """Execute general factual route for standard queries."""
        # Use the standard pipeline execution
        if plan["execution_pattern"] == "pipeline":
            return await self.execute_pipeline(context, plan, query_budget)
        elif plan["execution_pattern"] == "fork_join":
            return await self.execute_fork_join(context, plan, query_budget)
        elif plan["execution_pattern"] == "scatter_gather":
            return await self.execute_scatter_gather(context, plan, query_budget)
        else:
            return await self.execute_pipeline(context, plan, query_budget)
    
    async def _apply_fallback_logic(
        self, context: QueryContext, results: Dict[AgentType, Dict[str, Any]], 
        plan: Dict[str, Any], query_budget: int
    ) -> Dict[AgentType, Dict[str, Any]]:
        """Apply fallback logic for low-confidence classifications."""
        
        # Check if retrieval yielded no results
        retrieval_result = results.get(AgentType.RETRIEVAL, {})
        documents = retrieval_result.get("documents", [])
        
        if not documents or len(documents) == 0:
            logger.info("🔄 No retrieval results, trying knowledge graph as fallback")
            
            # Try knowledge graph as fallback
            try:
                kg_result = await self.knowledge_graph_agent.query(context.query)
                
                if kg_result.entities:
                    logger.info(f"✅ Knowledge graph fallback found {len(kg_result.entities)} entities")
                    
                    # Convert to document format
                    documents = []
                    for entity in kg_result.entities:
                        doc = {
                            "content": f"{entity.name}: {entity.properties.get('description', '')}",
                            "source": "knowledge_graph_fallback",
                            "metadata": {
                                "entity_id": entity.id,
                                "entity_type": entity.type,
                                "properties": entity.properties
                            }
                        }
                        documents.append(doc)
                    
                    # Update retrieval results
                    results[AgentType.RETRIEVAL] = {
                        "success": True,
                        "documents": documents,
                        "source": "knowledge_graph_fallback",
                        "confidence": kg_result.confidence,
                        "metadata": {
                            "entities_found": len(kg_result.entities),
                            "relationships_found": len(kg_result.relationships),
                            "fallback_used": True
                        }
                    }
                    
                    # Re-run synthesis with new documents
                    results = await self._execute_synthesis_phase_with_retries(context, results)
                    
            except Exception as e:
                logger.error(f"Knowledge graph fallback failed: {e}")
        
        return results
    
    def _handle_routing_failure(
        self, context: QueryContext, error_message: str
    ) -> Dict[AgentType, Dict[str, Any]]:
        """Handle routing failures with fallback to general processing."""
        logger.error(f"Routing failure: {error_message}")
        
        return {
            AgentType.RETRIEVAL: {
                "success": False,
                "error": error_message,
                "documents": [],
                "source": "fallback"
            },
            AgentType.SYNTHESIS: {
                "success": False,
                "error": "Routing failed, no synthesis possible",
                "answer": "I apologize, but I encountered an error while processing your query. Please try rephrasing your question.",
                "source": "fallback"
            }
        }

    async def execute_pipeline(
        self, context: QueryContext, plan: Dict[str, Any], query_budget: int
    ) -> Dict[AgentType, Dict[str, Any]]:
        """
        Execute the multi-agent pipeline with comprehensive error handling and fallback strategies.

        Args:
            context: Query context
            plan: Execution plan
            query_budget: Token budget for the query

        Returns:
            Dictionary mapping agent types to their results
        """
        results: Dict[AgentType, Dict[str, Any]] = {}
        pipeline_start_time = time.time()

        try:
            # Phase 1: Retrieval with enhanced error handling
            results = await self._execute_retrieval_phase_with_fallbacks(context, results)

            # Phase 2: Fact checking with graceful degradation
            results = await self._execute_fact_checking_phase_with_fallbacks(context, results)

            # Phase 3: Synthesis with retry logic
            results = await self._execute_synthesis_phase_with_retries(context, results)

            # Phase 4: Citation with fallback options
            results = await self._execute_citation_phase_with_fallbacks(context, results)

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

    async def _execute_retrieval_phase_with_fallbacks(
        self, context: QueryContext, results: Dict[AgentType, Dict[str, Any]]
    ) -> Dict[AgentType, Dict[str, Any]]:
        """Execute retrieval phase with comprehensive fallback strategies."""
        phase_start = time.time()
        logger.info("🚀 Phase 1: Starting Retrieval with Fallbacks")
        logger.info(f"  Query: {context.query[:100]}...")
        logger.info(f"  Trace ID: {context.trace_id}")

        retrieval_config = self.retry_config[AgentType.RETRIEVAL]
        max_retries = retrieval_config["max_retries"]
        timeout = retrieval_config["timeout"]
        backoff_factor = retrieval_config["backoff_factor"]

        for attempt in range(max_retries + 1):
            try:
                # Extract entities for retrieval
                logger.info(f"  🔍 Retrieval attempt {attempt + 1}/{max_retries + 1}")
                entities = await self._extract_entities_parallel(context.query)
                logger.info(f"  ✅ Extracted {len(entities)} entities")

                # Prepare retrieval task
                retrieval_task = {
                    "query": context.query,
                    "entities": entities,
                    "search_type": "hybrid",
                    "top_k": 20,
                }

                # Execute retrieval with timeout
                retrieval_result = await asyncio.wait_for(
                    self.agents[AgentType.RETRIEVAL].process_task(retrieval_task, context),
                    timeout=timeout,
                )
                
                # Validate and ensure result is a dictionary
                retrieval_result = self._ensure_dict_result(retrieval_result, "RETRIEVAL")
                
                # Check for empty retrieval results
                documents = retrieval_result.get("data", {}).get("documents", [])
                if not documents:
                    logger.warning("  ⚠️ Retrieval returned no documents - trying fallback strategies")
                    
                    # Try fallback strategies
                    fallback_result = await self._try_retrieval_fallbacks(context, entities)
                    if fallback_result:
                        retrieval_result = fallback_result
                        documents = retrieval_result.get("data", {}).get("documents", [])
                
                results[AgentType.RETRIEVAL] = retrieval_result

                phase_time = time.time() - phase_start
                if retrieval_result.get("success", False):
                    docs_count = len(documents)
                    logger.info(f"  ✅ Retrieval completed successfully in {phase_time:.2f}s")
                    logger.info(f"  📄 Retrieved {docs_count} documents")
                    
                    # Store retrieval context for downstream use
                    results["retrieval_context"] = {
                        "documents_count": docs_count,
                        "entities_found": len(entities),
                        "search_strategy": "hybrid",
                        "has_results": docs_count > 0,
                        "attempts_used": attempt + 1
                    }
                    return results
                else:
                    logger.warning(f"  ⚠️ Retrieval attempt {attempt + 1} failed: {retrieval_result.get('error', 'Unknown error')}")
                    if attempt < max_retries:
                        wait_time = timeout * (backoff_factor ** attempt)
                        logger.info(f"  ⏳ Waiting {wait_time:.1f}s before retry...")
                        await asyncio.sleep(wait_time)

            except asyncio.TimeoutError:
                phase_time = time.time() - phase_start
                logger.error(f"  ❌ Retrieval attempt {attempt + 1} timed out after {phase_time:.2f}s")
                if attempt < max_retries:
                    wait_time = timeout * (backoff_factor ** attempt)
                    logger.info(f"  ⏳ Waiting {wait_time:.1f}s before retry...")
                    await asyncio.sleep(wait_time)
            except Exception as e:
                phase_time = time.time() - phase_start
                logger.error(f"  ❌ Retrieval attempt {attempt + 1} failed after {phase_time:.2f}s: {e}")
                if attempt < max_retries:
                    wait_time = timeout * (backoff_factor ** attempt)
                    logger.info(f"  ⏳ Waiting {wait_time:.1f}s before retry...")
                    await asyncio.sleep(wait_time)

        # All attempts failed - create fallback response
        logger.error("  ❌ All retrieval attempts failed - using fallback response")
        results[AgentType.RETRIEVAL] = self._create_retrieval_fallback_result(context)
        return results

    async def _try_retrieval_fallbacks(
        self, context: QueryContext, entities: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Try alternative retrieval strategies when primary retrieval fails."""
        fallback_strategies = self.fallback_strategies[AgentType.RETRIEVAL]
        
        for strategy in fallback_strategies:
            try:
                logger.info(f"  🔄 Trying fallback strategy: {strategy}")
                
                if strategy == "broaden_query":
                    # Try with broader search terms
                    broadened_query = self._broaden_query(context.query)
                    fallback_task = {
                        "query": broadened_query,
                        "entities": entities,
                        "search_type": "keyword",
                        "top_k": 30,
                    }
                elif strategy == "keyword_search":
                    # Fall back to keyword search
                    fallback_task = {
                        "query": context.query,
                        "entities": entities,
                        "search_type": "keyword",
                        "top_k": 15,
                    }
                elif strategy == "knowledge_graph":
                    # Try knowledge graph search
                    fallback_task = {
                        "query": context.query,
                        "entities": entities,
                        "search_type": "graph",
                        "top_k": 10,
                    }
                else:
                    continue

                fallback_result = await asyncio.wait_for(
                    self.agents[AgentType.RETRIEVAL].process_task(fallback_task, context),
                    timeout=15,
                )
                
                fallback_result = self._ensure_dict_result(fallback_result, "RETRIEVAL")
                documents = fallback_result.get("data", {}).get("documents", [])
                
                if documents:
                    logger.info(f"  ✅ Fallback strategy '{strategy}' succeeded with {len(documents)} documents")
                    fallback_result["fallback_strategy_used"] = strategy
                    return fallback_result
                else:
                    logger.warning(f"  ⚠️ Fallback strategy '{strategy}' returned no documents")
                    
            except Exception as e:
                logger.warning(f"  ⚠️ Fallback strategy '{strategy}' failed: {e}")
                continue
        
        return None

    def _broaden_query(self, query: str) -> str:
        """Broaden the query by removing specific terms and keeping core concepts."""
        # Simple broadening - remove specific terms and keep core concepts
        words = query.split()
        if len(words) > 3:
            # Keep first 3 words as core concepts
            return " ".join(words[:3])
        return query

    def _create_retrieval_fallback_result(self, context: QueryContext) -> Dict[str, Any]:
        """Create a fallback result when all retrieval attempts fail."""
        return {
            "success": False,
            "data": {
                "documents": [],
                "search_performed": True,
                "fallback": True,
                "error": "No relevant documents found"
            },
            "error": "Retrieval failed after all attempts and fallback strategies",
            "confidence": 0.0,
            "execution_time_ms": 0,
            "fallback_message": "I couldn't find specific information about your query. Please try rephrasing or asking a different question."
        }

    async def _execute_fact_checking_phase_with_fallbacks(
        self, context: QueryContext, results: Dict[AgentType, Dict[str, Any]]
    ) -> Dict[AgentType, Dict[str, Any]]:
        """Execute fact checking phase with graceful degradation."""
        phase_start = time.time()
        logger.info("🚀 Phase 2: Starting Fact Checking with Fallbacks")
        logger.info(f"  Query: {context.query[:100]}...")
        logger.info(f"  Trace ID: {context.trace_id}")

        # Check if retrieval failed or returned no results
        retrieval_result = results.get(AgentType.RETRIEVAL, {})
        if not retrieval_result.get("success", False):
            logger.warning("  ⚠️ Skipping fact checking due to retrieval failure")
            results[AgentType.FACT_CHECK] = self._create_fact_check_skip_result("Retrieval failure")
            return results

        # Handle empty retrieval results
        documents = retrieval_result.get("data", {}).get("documents", [])
        if not documents:
            logger.warning("  ⚠️ No documents to fact-check - creating fallback result")
            results[AgentType.FACT_CHECK] = self._create_fact_check_skip_result("No documents available")
            return results

        fact_check_config = self.retry_config[AgentType.FACT_CHECK]
        max_retries = fact_check_config["max_retries"]
        timeout = fact_check_config["timeout"]

        for attempt in range(max_retries + 1):
            try:
                logger.info(f"  🔍 Fact checking attempt {attempt + 1}/{max_retries + 1}")
                
                fact_check_task = {
                    "documents": documents,
                    "query": context.query,
                    "verification_level": "standard",
                }

                fact_check_result = await asyncio.wait_for(
                    self.agents[AgentType.FACT_CHECK].process_task(fact_check_task, context),
                    timeout=timeout,
                )
                
                fact_check_result = self._ensure_dict_result(fact_check_result, "FACT_CHECK")
                results[AgentType.FACT_CHECK] = fact_check_result

                phase_time = time.time() - phase_start
                if fact_check_result.get("success", False):
                    verified_facts = fact_check_result.get("data", {}).get("verified_facts", [])
                    logger.info(f"  ✅ Fact checking completed successfully in {phase_time:.2f}s")
                    logger.info(f"  ✅ Verified {len(verified_facts)} facts")
                    
                    # Store fact check context
                    results["fact_check_context"] = {
                        "verified_facts_count": len(verified_facts),
                        "verification_level": "standard",
                        "attempts_used": attempt + 1
                    }
                    return results
                else:
                    logger.warning(f"  ⚠️ Fact checking attempt {attempt + 1} failed: {fact_check_result.get('error', 'Unknown error')}")
                    if attempt < max_retries:
                        logger.info("  ⏳ Waiting before retry...")
                        await asyncio.sleep(2)

            except asyncio.TimeoutError:
                phase_time = time.time() - phase_start
                logger.error(f"  ❌ Fact checking attempt {attempt + 1} timed out after {phase_time:.2f}s")
                if attempt < max_retries:
                    await asyncio.sleep(2)
            except Exception as e:
                phase_time = time.time() - phase_start
                logger.error(f"  ❌ Fact checking attempt {attempt + 1} failed after {phase_time:.2f}s: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(2)

        # All attempts failed - create fallback result
        logger.error("  ❌ All fact checking attempts failed - using fallback")
        results[AgentType.FACT_CHECK] = self._create_fact_check_fallback_result(documents)
        return results

    def _create_fact_check_skip_result(self, reason: str) -> Dict[str, Any]:
        """Create a result when fact checking is skipped."""
        return {
            "success": False,
            "data": {
                "verified_facts": [],
                "contested_claims": [],
                "verification_method": "skipped",
                "total_claims": 0,
                "skip_reason": reason,
                "metadata": {
                    "agent_id": "factcheck_agent",
                    "processing_time_ms": 0,
                    "skip_reason": reason
                },
            },
            "confidence": 0.0,
            "execution_time_ms": 0,
            "skip_reason": reason
        }

    def _create_fact_check_fallback_result(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a fallback result when fact checking fails."""
        # Convert documents to basic facts without verification
        basic_facts = [
            {
                "content": doc.get("content", "")[:200],
                "source": doc.get("source", "Unknown"),
                "confidence": 0.5,  # Lower confidence since not verified
                "verified": False,
                "fallback": True
            }
            for doc in documents[:5]  # Limit to top 5
        ]
        
        return {
            "success": False,
            "data": {
                "verified_facts": basic_facts,
                "contested_claims": [],
                "verification_method": "fallback",
                "total_claims": len(basic_facts),
                "fallback": True,
                "metadata": {
                    "agent_id": "factcheck_agent",
                    "processing_time_ms": 0,
                    "fallback_used": True
                },
            },
            "confidence": 0.3,
            "execution_time_ms": 0,
            "fallback_message": "Fact verification was incomplete, but I've provided available information."
        }

    async def _execute_synthesis_phase_with_retries(
        self, context: QueryContext, results: Dict[AgentType, Dict[str, Any]]
    ) -> Dict[AgentType, Dict[str, Any]]:
        """Execute synthesis phase with retry logic and fallback strategies."""
        phase_start = time.time()
        logger.info("🚀 Phase 3: Starting Synthesis with Retries")
        logger.info(f"  Query: {context.query[:100]}...")
        logger.info(f"  Trace ID: {context.trace_id}")

        synthesis_config = self.retry_config[AgentType.SYNTHESIS]
        max_retries = synthesis_config["max_retries"]
        timeout = synthesis_config["timeout"]
        backoff_factor = synthesis_config["backoff_factor"]

        # Prepare synthesis input with fallback handling
        synthesis_input = await self._prepare_synthesis_input_with_fallbacks(results, context)

        for attempt in range(max_retries + 1):
            try:
                logger.info(f"  🔍 Synthesis attempt {attempt + 1}/{max_retries + 1}")
                
                synthesis_result = await asyncio.wait_for(
                    self.agents[AgentType.SYNTHESIS].process_task(synthesis_input, context),
                    timeout=timeout,
                )
                
                synthesis_result = self._ensure_dict_result(synthesis_result, "SYNTHESIS")
                results[AgentType.SYNTHESIS] = synthesis_result

                phase_time = time.time() - phase_start
                if synthesis_result.get("success", False):
                    answer = synthesis_result.get("data", {}).get("answer", "")
                    answer_length = len(answer)
                    logger.info(f"  ✅ Synthesis completed successfully in {phase_time:.2f}s")
                    logger.info(f"  📝 Generated answer with {answer_length} characters")
                    
                    # Store synthesis context for citation
                    results["synthesis_context"] = {
                        "answer_length": answer_length,
                        "synthesis_style": synthesis_input.get("synthesis_params", {}).get("style", "comprehensive"),
                        "fallback_mode": synthesis_input.get("synthesis_params", {}).get("fallback_mode", False),
                        "attempts_used": attempt + 1
                    }
                    return results
                else:
                    logger.warning(f"  ⚠️ Synthesis attempt {attempt + 1} failed: {synthesis_result.get('error', 'Unknown error')}")
                    if attempt < max_retries:
                        wait_time = timeout * (backoff_factor ** attempt)
                        logger.info(f"  ⏳ Waiting {wait_time:.1f}s before retry...")
                        await asyncio.sleep(wait_time)

            except asyncio.TimeoutError:
                phase_time = time.time() - phase_start
                logger.error(f"  ❌ Synthesis attempt {attempt + 1} timed out after {phase_time:.2f}s")
                if attempt < max_retries:
                    wait_time = timeout * (backoff_factor ** attempt)
                    logger.info(f"  ⏳ Waiting {wait_time:.1f}s before retry...")
                    await asyncio.sleep(wait_time)
            except Exception as e:
                phase_time = time.time() - phase_start
                logger.error(f"  ❌ Synthesis attempt {attempt + 1} failed after {phase_time:.2f}s: {e}")
                if attempt < max_retries:
                    wait_time = timeout * (backoff_factor ** attempt)
                    logger.info(f"  ⏳ Waiting {wait_time:.1f}s before retry...")
                    await asyncio.sleep(wait_time)

        # All attempts failed - create fallback response
        logger.error("  ❌ All synthesis attempts failed - using fallback response")
        results[AgentType.SYNTHESIS] = self._create_synthesis_fallback_result(context, results)
        return results

    async def _prepare_synthesis_input_with_fallbacks(
        self, results: Dict[AgentType, Dict[str, Any]], context: QueryContext
    ) -> Dict[str, Any]:
        """Prepare synthesis input with comprehensive fallback handling."""
        # Check if fact-checking failed or returned no verified facts
        fact_check_result = results.get(AgentType.FACT_CHECK, {})
        verified_facts = fact_check_result.get("data", {}).get("verified_facts", [])
        
        if not fact_check_result.get("success", False):
            logger.warning("  ⚠️ Fact-checking failed - proceeding with limited synthesis")
            synthesis_input = {
                "verified_facts": [],
                "query": context.query,
                "synthesis_params": {
                    "style": "limited",
                    "confidence_threshold": 0.0,
                    "fallback_mode": True
                },
                "context": {
                    "fact_check_failed": True,
                    "retrieval_context": results.get("retrieval_context", {}),
                    "available_documents": results.get(AgentType.RETRIEVAL, {}).get("data", {}).get("documents", [])
                }
            }
        elif not verified_facts:
            logger.warning("  ⚠️ No verified facts available - proceeding with limited synthesis")
            synthesis_input = {
                "verified_facts": [],
                "query": context.query,
                "synthesis_params": {
                    "style": "limited",
                    "confidence_threshold": 0.0,
                    "fallback_mode": True
                },
                "context": {
                    "no_verified_facts": True,
                    "retrieval_context": results.get("retrieval_context", {}),
                    "fact_check_context": results.get("fact_check_context", {})
                }
            }
        else:
            # Normal synthesis with verified facts
            synthesis_input = self._prepare_synthesis_input(results, context)
            # Add context from previous phases
            synthesis_input["context"] = {
                "retrieval_context": results.get("retrieval_context", {}),
                "fact_check_context": results.get("fact_check_context", {}),
                "verified_facts_count": len(verified_facts)
            }

        return synthesis_input

    def _create_synthesis_fallback_result(
        self, context: QueryContext, results: Dict[AgentType, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a fallback synthesis result when all attempts fail."""
        # Try to salvage information from previous phases
        facts = []
        documents = []
        
        # Get facts from fact checker
        fact_check_result = results.get(AgentType.FACT_CHECK, {})
        if fact_check_result.get("success", False):
            facts = fact_check_result.get("data", {}).get("verified_facts", [])
        
        # Get documents from retrieval
        retrieval_result = results.get(AgentType.RETRIEVAL, {})
        if retrieval_result.get("success", False):
            documents = retrieval_result.get("data", {}).get("documents", [])
        
        # Create a basic response
        if facts:
            answer = "Based on available information:\n\n"
            for i, fact in enumerate(facts[:3], 1):
                content = fact.get("content", "")[:200]
                answer += f"{i}. {content}...\n"
        elif documents:
            answer = "I found some relevant information:\n\n"
            for i, doc in enumerate(documents[:3], 1):
                content = doc.get("content", "")[:200]
                answer += f"{i}. {content}...\n"
        else:
            answer = f"I apologize, but I couldn't process your query about '{context.query}'. Please try rephrasing your question or breaking it into smaller parts."
        
        return {
            "success": False,
            "data": {
                "answer": answer,
                "response": answer,
                "fallback": True,
                "synthesis_method": "fallback_concatenation"
            },
            "error": "Synthesis failed after all retry attempts",
            "confidence": 0.2,
            "execution_time_ms": 0,
            "fallback_message": "I've provided available information, but the response may be incomplete."
        }

    async def _execute_citation_phase_with_fallbacks(
        self, context: QueryContext, results: Dict[AgentType, Dict[str, Any]]
    ) -> Dict[AgentType, Dict[str, Any]]:
        """Execute citation phase with fallback options."""
        phase_start = time.time()
        logger.info("🚀 Phase 4: Starting Citation with Fallbacks")
        logger.info(f"  Query: {context.query[:100]}...")
        logger.info(f"  Trace ID: {context.trace_id}")

        # Skip if synthesis failed
        if (
            AgentType.SYNTHESIS not in results
            or not results[AgentType.SYNTHESIS].get("success", False)
        ):
            logger.warning("  ⚠️ Skipping citation due to synthesis failure")
            results[AgentType.CITATION] = self._create_citation_skip_result("Synthesis failure")
            return results

        citation_config = self.retry_config[AgentType.CITATION]
        max_retries = citation_config["max_retries"]
        timeout = citation_config["timeout"]

        for attempt in range(max_retries + 1):
            try:
                logger.info(f"  🔍 Citation attempt {attempt + 1}/{max_retries + 1}")
                
                # Prepare citation task with synthesis result and retrieval documents
                synthesis_data = results[AgentType.SYNTHESIS].get("data", {})
                retrieval_data = results[AgentType.RETRIEVAL].get("data", {})
                
                citation_task = {
                    "content": synthesis_data.get("answer", ""),
                    "sources": retrieval_data.get("documents", []),
                    "format": "academic",
                }

                citation_result = await asyncio.wait_for(
                    self.agents[AgentType.CITATION].process_task(citation_task, context),
                    timeout=timeout,
                )
                
                citation_result = self._ensure_dict_result(citation_result, "CITATION")
                results[AgentType.CITATION] = citation_result

                phase_time = time.time() - phase_start
                if citation_result.get("success", False):
                    citations_count = len(citation_result.get("data", {}).get("citations", []))
                    logger.info(f"  ✅ Citation completed successfully in {phase_time:.2f}s")
                    logger.info(f"  📚 Generated {citations_count} citations")
                    return results
                else:
                    logger.warning(f"  ⚠️ Citation attempt {attempt + 1} failed: {citation_result.get('error', 'Unknown error')}")
                    if attempt < max_retries:
                        logger.info("  ⏳ Waiting before retry...")
                        await asyncio.sleep(1)

            except asyncio.TimeoutError:
                phase_time = time.time() - phase_start
                logger.error(f"  ❌ Citation attempt {attempt + 1} timed out after {phase_time:.2f}s")
                if attempt < max_retries:
                    await asyncio.sleep(1)
            except Exception as e:
                phase_time = time.time() - phase_start
                logger.error(f"  ❌ Citation attempt {attempt + 1} failed after {phase_time:.2f}s: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(1)

        # All attempts failed - create fallback result
        logger.error("  ❌ All citation attempts failed - using fallback")
        results[AgentType.CITATION] = self._create_citation_fallback_result(results)
        return results

    def _create_citation_skip_result(self, reason: str) -> Dict[str, Any]:
        """Create a result when citation is skipped."""
        return {
            "success": False,
            "data": {
                "citations": [],
                "bibliography": [],
                "citation_method": "skipped",
                "skip_reason": reason,
                "metadata": {
                    "agent_id": "citation_agent",
                    "processing_time_ms": 0,
                    "skip_reason": reason
                },
            },
            "confidence": 0.0,
            "execution_time_ms": 0,
            "skip_reason": reason
        }

    def _create_citation_fallback_result(self, results: Dict[AgentType, Dict[str, Any]]) -> Dict[str, Any]:
        """Create a fallback citation result when all attempts fail."""
        # Extract basic citation information from available sources
        synthesis_data = results.get(AgentType.SYNTHESIS, {}).get("data", {})
        retrieval_data = results.get(AgentType.RETRIEVAL, {}).get("data", {})
        
        answer = synthesis_data.get("answer", "")
        documents = retrieval_data.get("documents", [])
        
        # Create basic citations from documents
        basic_citations = []
        for i, doc in enumerate(documents[:5], 1):
            basic_citations.append({
                "id": f"source_{i}",
                "content": doc.get("content", "")[:100],
                "source": doc.get("source", "Unknown"),
                "format": "basic"
            })
        
        return {
            "success": False,
            "data": {
                "citations": basic_citations,
                "bibliography": [doc.get("source", "Unknown") for doc in documents[:5]],
                "citation_method": "fallback",
                "fallback": True,
                "metadata": {
                    "agent_id": "citation_agent",
                    "processing_time_ms": 0,
                    "fallback_used": True
                },
            },
            "confidence": 0.3,
            "execution_time_ms": 0,
            "fallback_message": "Citations were generated using available sources, but may be incomplete."
        }

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

    async def shutdown(self) -> None:
        """
        Gracefully shutdown the LeadOrchestrator following MAANG standards.
        
        This method ensures:
        1. All active agents are stopped gracefully
        2. Pending tasks are canceled
        3. All connections (Redis, database, etc.) are closed
        4. Cleanup is completed before returning
        5. Comprehensive logging of the shutdown process
        6. Exception handling for robust shutdown
        
        Follows MAANG standards for graceful shutdown patterns.
        """
        logger.info("🔄 Starting LeadOrchestrator graceful shutdown")
        shutdown_start_time = time.time()
        shutdown_errors = []
        
        try:
            # Phase 1: Stop accepting new tasks
            logger.info("📋 Phase 1: Stopping new task acceptance")
            self._shutdown_initiated = True
            
            # Phase 2: Cancel any pending tasks
            logger.info("📋 Phase 2: Canceling pending tasks")
            try:
                # Cancel any running tasks
                if hasattr(self, '_active_tasks'):
                    for task_id, task in list(self._active_tasks.items()):
                        if not task.done():
                            task.cancel()
                            logger.info(f"✅ Canceled task: {task_id}")
                
                # Wait for tasks to complete cancellation
                if hasattr(self, '_active_tasks') and self._active_tasks:
                    await asyncio.sleep(0.5)  # Give tasks time to cancel
                    logger.info(f"✅ Canceled {len(self._active_tasks)} pending tasks")
            except Exception as e:
                error_msg = f"Error canceling pending tasks: {e}"
                logger.warning(f"⚠️ {error_msg}")
                shutdown_errors.append(error_msg)
            
            # Phase 3: Shutdown all agents gracefully
            logger.info("📋 Phase 3: Shutting down agents")
            agent_shutdown_tasks = []
            
            for agent_type, agent in self.agents.items():
                try:
                    # Check if agent has shutdown method
                    if hasattr(agent, 'shutdown'):
                        logger.info(f"🔄 Shutting down {agent_type.value} agent")
                        shutdown_task = asyncio.create_task(agent.shutdown())
                        agent_shutdown_tasks.append((agent_type, shutdown_task))
                    else:
                        logger.info(f"ℹ️ {agent_type.value} agent has no shutdown method")
                except Exception as e:
                    error_msg = f"Error initiating shutdown for {agent_type.value} agent: {e}"
                    logger.warning(f"⚠️ {error_msg}")
                    shutdown_errors.append(error_msg)
            
            # Wait for all agents to shutdown with timeout
            if agent_shutdown_tasks:
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*[task for _, task in agent_shutdown_tasks], return_exceptions=True),
                        timeout=10.0  # 10 second timeout for agent shutdown
                    )
                    logger.info(f"✅ All agents shutdown completed")
                except asyncio.TimeoutError:
                    logger.warning("⚠️ Agent shutdown timeout - some agents may not have shut down gracefully")
                    shutdown_errors.append("Agent shutdown timeout")
                except Exception as e:
                    error_msg = f"Error during agent shutdown: {e}"
                    logger.error(f"❌ {error_msg}")
                    shutdown_errors.append(error_msg)
            
            # Phase 4: Close all connections
            logger.info("📋 Phase 4: Closing connections")
            
            # Close Redis connections
            try:
                if hasattr(self, 'semantic_cache') and hasattr(self.semantic_cache, '_redis_client'):
                    if self.semantic_cache._redis_client:
                        await self.semantic_cache._redis_client.close()
                        logger.info("✅ Redis cache connection closed")
            except Exception as e:
                error_msg = f"Error closing Redis connection: {e}"
                logger.warning(f"⚠️ {error_msg}")
                shutdown_errors.append(error_msg)
            
            # Close database connections
            try:
                if hasattr(self, '_db_pool'):
                    await self._db_pool.close()
                    logger.info("✅ Database connection pool closed")
            except Exception as e:
                error_msg = f"Error closing database connections: {e}"
                logger.warning(f"⚠️ {error_msg}")
                shutdown_errors.append(error_msg)
            
            # Close HTTP connections
            try:
                if hasattr(self, '_http_session') and self._http_session:
                    await self._http_session.close()
                    logger.info("✅ HTTP session closed")
            except Exception as e:
                error_msg = f"Error closing HTTP session: {e}"
                logger.warning(f"⚠️ {error_msg}")
                shutdown_errors.append(error_msg)
            
            # Phase 5: Cleanup supporting components
            logger.info("📋 Phase 5: Cleaning up supporting components")
            
            # Shutdown token budget controller
            try:
                if hasattr(self, 'token_budget') and hasattr(self.token_budget, 'shutdown'):
                    await self.token_budget.shutdown()
                    logger.info("✅ Token budget controller shutdown")
            except Exception as e:
                error_msg = f"Error shutting down token budget controller: {e}"
                logger.warning(f"⚠️ {error_msg}")
                shutdown_errors.append(error_msg)
            
            # Shutdown semantic cache
            try:
                if hasattr(self, 'semantic_cache') and hasattr(self.semantic_cache, 'shutdown'):
                    await self.semantic_cache.shutdown()
                    logger.info("✅ Semantic cache shutdown")
            except Exception as e:
                error_msg = f"Error shutting down semantic cache: {e}"
                logger.warning(f"⚠️ {error_msg}")
                shutdown_errors.append(error_msg)
            
            # Phase 6: Final cleanup
            logger.info("📋 Phase 6: Final cleanup")
            
            # Clear any remaining references
            try:
                self.agents.clear()
                logger.info("✅ Agent references cleared")
            except Exception as e:
                error_msg = f"Error clearing agent references: {e}"
                logger.warning(f"⚠️ {error_msg}")
                shutdown_errors.append(error_msg)
            
            # Wait for any remaining async operations
            await asyncio.sleep(0.1)
            
        except Exception as e:
            error_msg = f"Critical error during shutdown: {e}"
            logger.error(f"❌ {error_msg}")
            shutdown_errors.append(error_msg)
        
        finally:
            # Phase 7: Log shutdown completion
            shutdown_duration = time.time() - shutdown_start_time
            logger.info(f"📊 Shutdown completed in {shutdown_duration:.2f} seconds")
            
            if shutdown_errors:
                logger.error(f"❌ Shutdown completed with {len(shutdown_errors)} errors:")
                for i, error in enumerate(shutdown_errors, 1):
                    logger.error(f"  {i}. {error}")
            else:
                logger.info("✅ LeadOrchestrator shutdown completed successfully")
            
            # Set shutdown flag
            self._shutdown_completed = True


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
    """Enhanced response aggregator with comprehensive error handling and fallback support."""

    def __init__(self):
        # Weighted confidence calculation based on agent importance
        self.agent_weights = {
            AgentType.RETRIEVAL: 0.25,  # Retrieval quality affects overall confidence
            AgentType.FACT_CHECK: 0.30,  # Fact-checking is critical for accuracy
            AgentType.SYNTHESIS: 0.35,  # Synthesis quality is most important
            AgentType.CITATION: 0.10,  # Citations add credibility but less weight
        }

        # Fallback message templates
        self.fallback_messages = {
            "retrieval_failure": "I couldn't find specific information about your query. Please try rephrasing or asking a different question.",
            "fact_check_failure": "I found some information but couldn't fully verify all claims. Please use this information with caution.",
            "synthesis_failure": "I encountered some issues while processing your query. Here's what I could determine based on the available information.",
            "citation_failure": "I've provided an answer but couldn't generate complete citations. The information may still be useful.",
            "partial_failure": "Some parts of the processing encountered issues, but I've provided the best available information.",
            "complete_failure": "I apologize, but I encountered significant issues while processing your query. Please try again or contact support."
        }

    def aggregate_pipeline_results(
        self, results: Dict[AgentType, Dict[str, Any]], context: QueryContext
    ) -> Dict[str, Any]:
        """
        Aggregate results from all pipeline stages into a final response.
        Enhanced with comprehensive error handling and fallback strategies.

        Args:
            results: Dictionary mapping agent types to their results
            context: Query context

        Returns:
            Final response with answer, confidence, citations, and metadata
        """
        try:
            # Analyze pipeline health and determine response strategy
            pipeline_health = self._analyze_pipeline_health(results)
            
            # Check for complete pipeline failure
            if pipeline_health["status"] == "complete_failure":
                logger.error("❌ Complete pipeline failure - no agents succeeded")
                return self._create_complete_failure_response(context, results)
            
            # Extract synthesis result (most important)
            synthesis_result = results.get(AgentType.SYNTHESIS, {})
            synthesis_data = synthesis_result.get("data", {})
            
            # Extract answer with fallback handling
            answer = self._extract_answer_with_fallbacks(synthesis_result, results, context)
            
            # Calculate weighted confidence with degradation for failures
            confidence = self._calculate_weighted_confidence_with_degradation(results, pipeline_health)
            
            # Extract citations from citation agent if available
            citations = self._extract_citations_with_fallbacks(results)
            
            # Compile comprehensive metadata with error details
            metadata = self._compile_enhanced_metadata(results, context, pipeline_health)
            
            # Determine response type and warnings
            response_type = self._determine_response_type(pipeline_health)
            warnings = self._generate_warnings(pipeline_health, results)
            
            # Add fallback messages if needed
            fallback_messages = self._generate_fallback_messages(pipeline_health, results)
            
            return {
                "success": True,
                "answer": answer,
                "confidence": confidence,
                "citations": citations,
                "metadata": metadata,
                "response_type": response_type,
                "warnings": warnings,
                "fallback_messages": fallback_messages,
                "pipeline_health": pipeline_health["status"]
            }
            
        except Exception as e:
            logger.error(f"Response aggregation failed: {e}")
            return self._create_aggregation_error_response(context, str(e))

    def _analyze_pipeline_health(self, results: Dict[AgentType, Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the overall health of the pipeline and identify issues."""
        successful_agents = []
        failed_agents = []
        partial_failures = []
        fallback_used = []
        
        for agent_type, result in results.items():
            if isinstance(agent_type, AgentType):
                if result.get("success", False):
                    successful_agents.append(agent_type.value)
                    if result.get("fallback", False):
                        fallback_used.append(agent_type.value)
                else:
                    failed_agents.append(agent_type.value)
                    if result.get("fallback", False):
                        partial_failures.append(agent_type.value)
        
        # Determine overall status
        if not successful_agents:
            status = "complete_failure"
        elif failed_agents and successful_agents:
            status = "partial_failure"
        elif fallback_used:
            status = "fallback_used"
        else:
            status = "success"
        
        return {
            "status": status,
            "successful_agents": successful_agents,
            "failed_agents": failed_agents,
            "partial_failures": partial_failures,
            "fallback_used": fallback_used,
            "total_agents": len([k for k in results.keys() if isinstance(k, AgentType)])
        }

    def _extract_answer_with_fallbacks(
        self, synthesis_result: Dict[str, Any], results: Dict[AgentType, Dict[str, Any]], context: QueryContext
    ) -> str:
        """Extract answer with comprehensive fallback handling."""
        # Try to get answer from synthesis
        answer = synthesis_result.get("data", {}).get("answer", "")
        
        if not answer:
            # Check if synthesis failed but has fallback
            if synthesis_result.get("fallback", False):
                answer = synthesis_result.get("data", {}).get("response", "")
            
            # If still no answer, try to construct from other sources
            if not answer:
                answer = self._construct_answer_from_fallbacks(results, context)
        
        return answer

    def _construct_answer_from_fallbacks(
        self, results: Dict[AgentType, Dict[str, Any]], context: QueryContext
    ) -> str:
        """Construct an answer from available fallback sources."""
        # Try to get facts from fact checker
        facts = []
        fact_check_result = results.get(AgentType.FACT_CHECK, {})
        if fact_check_result.get("success", False) or fact_check_result.get("fallback", False):
            facts = fact_check_result.get("data", {}).get("verified_facts", [])
        
        # Try to get documents from retrieval
        documents = []
        retrieval_result = results.get(AgentType.RETRIEVAL, {})
        if retrieval_result.get("success", False) or retrieval_result.get("fallback", False):
            documents = retrieval_result.get("data", {}).get("documents", [])
        
        # Construct answer from available sources
        if facts:
            answer = "Based on available information:\n\n"
            for i, fact in enumerate(facts[:3], 1):
                content = fact.get("content", "")[:200]
                answer += f"{i}. {content}...\n"
        elif documents:
            answer = "I found some relevant information:\n\n"
            for i, doc in enumerate(documents[:3], 1):
                content = doc.get("content", "")[:200]
                answer += f"{i}. {content}...\n"
        else:
            answer = f"I apologize, but I couldn't process your query about '{context.query}'. Please try rephrasing your question or breaking it into smaller parts."
        
        return answer

    def _calculate_weighted_confidence_with_degradation(
        self, results: Dict[AgentType, Dict[str, Any]], pipeline_health: Dict[str, Any]
    ) -> float:
        """Calculate weighted confidence with degradation for failures."""
        weights = {
            AgentType.RETRIEVAL: 0.2,
            AgentType.FACT_CHECK: 0.3,
            AgentType.SYNTHESIS: 0.4,
            AgentType.CITATION: 0.1,
        }

        total_confidence = 0.0
        total_weight = 0.0
        degradation_factor = 1.0

        # Apply degradation based on pipeline health
        if pipeline_health["status"] == "partial_failure":
            degradation_factor = 0.7
        elif pipeline_health["status"] == "fallback_used":
            degradation_factor = 0.8
        elif pipeline_health["status"] == "complete_failure":
            degradation_factor = 0.3

        for agent_type, result in results.items():
            if agent_type in weights:
                if result.get("success", False):
                    confidence = result.get("confidence", 0.0)
                    weight = weights[agent_type]
                    total_confidence += confidence * weight
                    total_weight += weight
                elif result.get("fallback", False):
                    # Apply reduced confidence for fallback results
                    confidence = result.get("confidence", 0.0) * 0.6
                    weight = weights[agent_type]
                    total_confidence += confidence * weight
                    total_weight += weight

        base_confidence = total_confidence / max(total_weight, 0.1)
        return min(base_confidence * degradation_factor, 1.0)

    def _extract_citations_with_fallbacks(self, results: Dict[AgentType, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract citations with fallback handling."""
        citations = []
        citation_result = results.get(AgentType.CITATION, {})
        
        if citation_result.get("success", False):
            citations = citation_result.get("data", {}).get("citations", [])
        elif citation_result.get("fallback", False):
            # Use fallback citations if available
            citations = citation_result.get("data", {}).get("citations", [])
        
        return citations

    def _compile_enhanced_metadata(
        self, results: Dict[AgentType, Dict[str, Any]], context: QueryContext, pipeline_health: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compile comprehensive metadata with error details."""
        metadata = {
            "pipeline_status": pipeline_health["status"],
            "successful_agents": pipeline_health["successful_agents"],
            "failed_agents": pipeline_health["failed_agents"],
            "fallback_used": pipeline_health["fallback_used"],
            "agent_results": {
                agent_type.value: {
                    "success": result.get("success", False),
                    "confidence": result.get("confidence", 0.0),
                    "execution_time_ms": result.get("execution_time_ms", 0),
                    "fallback_used": result.get("fallback", False),
                    "error": result.get("error", None),
                    "attempts_used": result.get("attempts_used", 1)
                }
                for agent_type, result in results.items()
                if isinstance(agent_type, AgentType)
            },
            "token_usage": self._compile_token_usage(results),
            "retrieval_context": results.get("retrieval_context", {}),
            "fact_check_context": results.get("fact_check_context", {}),
            "synthesis_context": results.get("synthesis_context", {}),
            "trace_id": context.trace_id,
            "query_complexity": len(context.query.split()),
            "user_context_keys": list(context.user_context.keys()) if context.user_context else []
        }
        
        # Add error details for failed agents
        error_details = {}
        for agent_type, result in results.items():
            if isinstance(agent_type, AgentType) and not result.get("success", False):
                error_details[agent_type.value] = {
                    "error": result.get("error", "Unknown error"),
                    "fallback_message": result.get("fallback_message", None),
                    "skip_reason": result.get("skip_reason", None)
                }
        
        if error_details:
            metadata["error_details"] = error_details
        
        return metadata

    def _determine_response_type(self, pipeline_health: Dict[str, Any]) -> str:
        """Determine the type of response based on pipeline health."""
        if pipeline_health["status"] == "success":
            return "complete"
        elif pipeline_health["status"] == "fallback_used":
            return "fallback"
        elif pipeline_health["status"] == "partial_failure":
            return "partial"
        else:
            return "error"

    def _generate_warnings(self, pipeline_health: Dict[str, Any], results: Dict[AgentType, Dict[str, Any]]) -> List[str]:
        """Generate warnings based on pipeline health and results."""
        warnings = []
        
        # Add warnings for failed agents
        for agent in pipeline_health["failed_agents"]:
            warnings.append(f"Agent {agent} failed during processing")
        
        # Add specific warnings for critical failures
        if AgentType.RETRIEVAL.value in pipeline_health["failed_agents"]:
            warnings.append("Limited information available due to retrieval issues")
        if AgentType.FACT_CHECK.value in pipeline_health["failed_agents"]:
            warnings.append("Fact verification was incomplete")
        if AgentType.SYNTHESIS.value in pipeline_health["failed_agents"]:
            warnings.append("Answer synthesis may be incomplete")
        
        # Add warnings for fallback usage
        for agent in pipeline_health["fallback_used"]:
            warnings.append(f"Agent {agent} used fallback processing")
        
        # Add warnings for empty retrieval
        retrieval_result = results.get(AgentType.RETRIEVAL, {})
        if retrieval_result.get("empty_retrieval", False):
            warnings.append("No relevant documents found for this query")
        
        return warnings

    def _generate_fallback_messages(
        self, pipeline_health: Dict[str, Any], results: Dict[AgentType, Dict[str, Any]]
    ) -> List[str]:
        """Generate fallback messages for user communication."""
        messages = []
        
        # Add agent-specific fallback messages
        for agent_type, result in results.items():
            if isinstance(agent_type, AgentType) and result.get("fallback", False):
                fallback_msg = result.get("fallback_message")
                if fallback_msg:
                    messages.append(f"{agent_type.value}: {fallback_msg}")
        
        # Add general fallback messages based on pipeline health
        if pipeline_health["status"] == "partial_failure":
            messages.append(self.fallback_messages["partial_failure"])
        elif pipeline_health["status"] == "complete_failure":
            messages.append(self.fallback_messages["complete_failure"])
        
        return messages

    def _create_complete_failure_response(
        self, context: QueryContext, results: Dict[AgentType, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create response for complete pipeline failure."""
        return {
            "success": False,
            "answer": self.fallback_messages["complete_failure"],
            "confidence": 0.0,
            "citations": [],
            "metadata": {
                "pipeline_status": "complete_failure",
                "failed_agents": [agent_type.value for agent_type in results.keys() if isinstance(agent_type, AgentType)],
                "error": "All pipeline agents failed",
                "trace_id": context.trace_id
            },
            "response_type": "error",
            "warnings": ["All processing agents failed"],
            "fallback_messages": [self.fallback_messages["complete_failure"]]
        }

    def _create_aggregation_error_response(self, context: QueryContext, error: str) -> Dict[str, Any]:
        """Create response when aggregation itself fails."""
        return {
            "success": False,
            "answer": "I apologize, but I encountered an error while processing your query. Please try again.",
            "confidence": 0.0,
            "citations": [],
            "metadata": {
                "error": error,
                "error_type": "aggregation_error",
                "trace_id": context.trace_id
            },
            "response_type": "error",
            "warnings": ["Response aggregation failed"],
            "fallback_messages": ["Please try again or contact support"]
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
