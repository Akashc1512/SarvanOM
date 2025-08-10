#!/usr/bin/env python3
"""
SarvanOM Agent Orchestrator - Consolidated Multi-Agent System

Extracted from services/api_gateway/lead_orchestrator.py and enhanced with best practices.
Implements the multi-agent AI orchestration described in Sarvanom_blueprint.md.

Features extracted and consolidated:
- Token budget management
- Semantic caching
- Agent lifecycle management  
- Execution planning and routing
- Error handling and fallbacks
- Performance monitoring
"""

import asyncio
import time
import uuid
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json

# Import our unified LLM processor
from .real_llm_integration import real_llm_processor, QueryComplexity, LLMProvider


class AgentType(str, Enum):
    """Agent types for the multi-agent system."""
    RETRIEVAL = "retrieval"
    SYNTHESIS = "synthesis"
    FACT_CHECK = "fact_check"
    CITATION = "citation"
    REVIEWER = "reviewer"


class ExecutionPattern(str, Enum):
    """Execution patterns for agent orchestration."""
    PIPELINE = "pipeline"        # Sequential: Retrieval → Synthesis → Fact-check
    PARALLEL = "parallel"        # Parallel: All agents run simultaneously
    ADAPTIVE = "adaptive"        # Dynamic based on query complexity


@dataclass
class QueryContext:
    """Query context for agent orchestration."""
    trace_id: str
    query: str
    user_id: Optional[str] = None
    complexity: QueryComplexity = QueryComplexity.RESEARCH_SYNTHESIS
    timeout: float = 30.0
    enable_cache: bool = True
    enable_reviewer: bool = False


@dataclass
class AgentResult:
    """Standardized agent result structure."""
    agent_type: AgentType
    success: bool
    content: Any
    sources: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    execution_time_ms: int = 0
    error: Optional[str] = None


class TokenBudgetController:
    """Token budget management for cost optimization."""
    
    def __init__(self):
        self.default_budget = 10000
        self.budget_per_complexity = {
            QueryComplexity.SIMPLE_FACTUAL: 2000,
            QueryComplexity.RESEARCH_SYNTHESIS: 5000,
            QueryComplexity.COMPLEX_REASONING: 10000
        }
    
    async def allocate_budget_for_query(self, query: str, complexity: QueryComplexity = None) -> int:
        """Allocate token budget based on query complexity."""
        if complexity is None:
            complexity = real_llm_processor.classify_query_complexity(query)
        
        base_budget = self.budget_per_complexity.get(complexity, self.default_budget)
        
        # Adjust based on query length
        query_length_factor = min(2.0, len(query.split()) / 50)
        allocated_budget = int(base_budget * query_length_factor)
        
        return max(1000, min(allocated_budget, 15000))  # Clamp between 1K and 15K


class SemanticCache:
    """Semantic caching for query responses."""
    
    def __init__(self):
        self.cache = {}  # In-memory cache (in production, use Redis)
        self.ttl_seconds = 3600
    
    async def get_cached_response(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached response for similar query."""
        # Simple implementation - in production, use semantic similarity
        query_key = self._normalize_query(query)
        
        if query_key in self.cache:
            cached_item = self.cache[query_key]
            if time.time() - cached_item["timestamp"] < self.ttl_seconds:
                return cached_item["response"]
            else:
                del self.cache[query_key]
        
        return None
    
    async def cache_response(self, query: str, response: Dict[str, Any]):
        """Cache response for future queries."""
        query_key = self._normalize_query(query)
        self.cache[query_key] = {
            "response": response,
            "timestamp": time.time()
        }
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for caching."""
        return query.lower().strip()


class AgentOrchestrator:
    """
    Multi-agent orchestrator implementing SarvanOM's AI-first architecture.
    
    Coordinates specialized agents (Retrieval, Synthesis, Fact-check, Citation, Reviewer)
    as described in the Sarvanom blueprint for 70% research time reduction.
    """
    
    def __init__(self):
        self.token_budget = TokenBudgetController()
        self.semantic_cache = SemanticCache()
        self.execution_stats = {
            "total_queries": 0,
            "cache_hits": 0,
            "avg_execution_time": 0
        }
    
    async def process_query(self, context: QueryContext) -> Dict[str, Any]:
        """
        Main orchestration method implementing the multi-agent pipeline.
        
        Based on Sarvanom blueprint:
        1. Query analysis and planning
        2. Agent execution coordination
        3. Result synthesis and validation
        4. Caching and optimization
        """
        start_time = time.time()
        
        try:
            # Update stats
            self.execution_stats["total_queries"] += 1
            
            # Check semantic cache first
            if context.enable_cache:
                cached_response = await self.semantic_cache.get_cached_response(context.query)
                if cached_response:
                    self.execution_stats["cache_hits"] += 1
                    print(f"Cache hit for query {context.trace_id}")
                    return {
                        **cached_response,
                        "cache_status": "hit",
                        "execution_time_ms": int((time.time() - start_time) * 1000)
                    }
            
            # Allocate token budget
            query_budget = await self.token_budget.allocate_budget_for_query(
                context.query, context.complexity
            )
            
            # Analyze and plan execution
            execution_plan = await self.analyze_and_plan(context)
            
            # Execute agent pipeline
            results = await self.execute_pipeline(context, execution_plan)
            
            # Process results into final response
            final_response = await self.synthesize_final_response(results, context)
            
            # Cache successful response
            if context.enable_cache and final_response.get("success"):
                await self.semantic_cache.cache_response(context.query, final_response)
            
            # Update execution stats
            execution_time = time.time() - start_time
            self.execution_stats["avg_execution_time"] = (
                self.execution_stats["avg_execution_time"] * (self.execution_stats["total_queries"] - 1) + 
                execution_time
            ) / self.execution_stats["total_queries"]
            
            final_response["execution_time_ms"] = int(execution_time * 1000)
            final_response["token_budget"] = query_budget
            final_response["cache_status"] = "miss"
            
            return final_response
            
        except Exception as e:
            error_response = {
                "success": False,
                "error": f"Orchestration failed: {str(e)}",
                "execution_time_ms": int((time.time() - start_time) * 1000),
                "cache_status": "error"
            }
            print(f"Orchestration error for {context.trace_id}: {e}")
            return error_response
    
    async def analyze_and_plan(self, context: QueryContext) -> Dict[str, Any]:
        """Analyze query and create execution plan."""
        # Determine execution pattern based on complexity
        if context.complexity == QueryComplexity.SIMPLE_FACTUAL:
            pattern = ExecutionPattern.PIPELINE
            agents = [AgentType.RETRIEVAL, AgentType.SYNTHESIS]
        elif context.complexity == QueryComplexity.RESEARCH_SYNTHESIS:
            pattern = ExecutionPattern.PIPELINE  
            agents = [AgentType.RETRIEVAL, AgentType.SYNTHESIS, AgentType.FACT_CHECK]
        else:  # COMPLEX_REASONING
            pattern = ExecutionPattern.PIPELINE
            agents = [AgentType.RETRIEVAL, AgentType.SYNTHESIS, AgentType.FACT_CHECK, AgentType.CITATION]
            if context.enable_reviewer:
                agents.append(AgentType.REVIEWER)
        
        return {
            "execution_pattern": pattern,
            "agent_sequence": agents,
            "timeout": context.timeout,
            "parallel_capable": len(agents) <= 3
        }
    
    async def execute_pipeline(self, context: QueryContext, plan: Dict[str, Any]) -> List[AgentResult]:
        """Execute the agent pipeline based on the plan."""
        results = []
        agent_sequence = plan["agent_sequence"]
        
        # For pipeline execution, run agents sequentially
        current_content = context.query
        retrieval_sources = []
        
        for agent_type in agent_sequence:
            try:
                agent_start = time.time()
                
                if agent_type == AgentType.RETRIEVAL:
                    # Use our unified LLM processor for search
                    search_result = await real_llm_processor.search_with_ai(
                        query=context.query,
                        user_id=context.user_id,
                        max_results=10
                    )
                    retrieval_sources = search_result.get("results", [])
                    if retrieval_sources is None:
                        retrieval_sources = []
                    
                    result = AgentResult(
                        agent_type=agent_type,
                        success=True,
                        content=search_result,
                        sources=retrieval_sources or [],
                        metadata={"complexity": context.complexity.value},
                        execution_time_ms=search_result.get("processing_time_ms", 0)
                    )
                
                elif agent_type == AgentType.SYNTHESIS:
                    try:
                        # Use unified LLM processor for synthesis
                        synthesis_result = await real_llm_processor.synthesize_with_ai(
                            content=f"Synthesize response for: {context.query}",
                            query=context.query,
                            sources=["retrieval_results"] + [s.get("title", "") for s in (retrieval_sources or [])[:3]]
                        )
                        
                        result = AgentResult(
                            agent_type=agent_type,
                            success=True,
                            content=synthesis_result,
                            sources=retrieval_sources or [],
                            metadata={"synthesis_method": "ai_powered"},
                            execution_time_ms=synthesis_result.get("processing_time_ms", 0) if synthesis_result else 0
                        )
                        current_content = synthesis_result.get("synthesis", current_content) if synthesis_result else current_content
                    except Exception as e:
                        print(f"Agent synthesis failed: {e}")
                        import traceback
                        traceback.print_exc()
                        
                        result = AgentResult(
                            agent_type=agent_type,
                            success=False,
                            content=f"Synthesis failed: {str(e)}",
                            sources=retrieval_sources or [],
                            metadata={"synthesis_method": "error_fallback", "error": str(e)},
                            execution_time_ms=0
                        )
                
                elif agent_type == AgentType.FACT_CHECK:
                    # Use unified LLM processor for fact-checking
                    fact_check_result = await real_llm_processor.fact_check_with_ai(
                        claim=current_content[:500],  # First 500 chars for fact-checking
                        sources=retrieval_sources or [],
                        context={"query": context.query, "domain": "general"}
                    )
                    
                    result = AgentResult(
                        agent_type=agent_type,
                        success=True,
                        content=fact_check_result,
                        sources=retrieval_sources or [],
                        metadata={"verification_method": "ai_powered"},
                        execution_time_ms=fact_check_result.get("processing_time_ms", 0)
                    )
                
                else:
                    # Real processing for other agents using LLM integration
                    if agent_type == AgentType.FACT_CHECK:
                        llm_response = await real_llm_processor.fact_check_with_ai(
                            claim=context.query,
                            sources=retrieval_sources
                        )
                        result = AgentResult(
                            agent_type=agent_type,
                            success=llm_response.get("success", True),
                            content=llm_response.get("verification", f"Fact-checked: {context.query}"),
                            sources=retrieval_sources or [],
                            metadata={
                                "method": "llm_fact_check",
                                "provider": llm_response.get("provider", "unknown"),
                                "confidence": llm_response.get("confidence", 0.8)
                            },
                            execution_time_ms=int((time.time() - agent_start) * 1000)
                        )
                    elif agent_type == AgentType.CITATION:
                        llm_response = await real_llm_processor.generate_citations(
                            content=context.query,
                            sources=retrieval_sources
                        )
                        result = AgentResult(
                            agent_type=agent_type,
                            success=llm_response.get("success", True),
                            content=llm_response.get("citations", f"Citations for: {context.query}"),
                            sources=retrieval_sources or [],
                            metadata={
                                "method": "llm_citation",
                                "provider": llm_response.get("provider", "unknown"),
                                "citation_count": len(retrieval_sources or [])
                            },
                            execution_time_ms=int((time.time() - agent_start) * 1000)
                        )
                    elif agent_type == AgentType.REVIEWER:
                        llm_response = await real_llm_processor.review_content(
                            content=context.query,
                            sources=retrieval_sources
                        )
                        result = AgentResult(
                            agent_type=agent_type,
                            success=llm_response.get("success", True),
                            content=llm_response.get("review", f"Reviewed: {context.query}"),
                            sources=retrieval_sources or [],
                            metadata={
                                "method": "llm_review",
                                "provider": llm_response.get("provider", "unknown"),
                                "quality_score": llm_response.get("quality_score", 0.8)
                            },
                            execution_time_ms=int((time.time() - agent_start) * 1000)
                        )
                    else:
                        # Fallback using general synthesis for unknown agent types
                        llm_response = await real_llm_processor.synthesize_with_ai(
                            query=context.query,
                            sources=retrieval_sources or []
                        )
                        result = AgentResult(
                            agent_type=agent_type,
                            success=llm_response.get("success", True),
                            content=llm_response.get("synthesis", f"{agent_type.value} processing completed"),
                            sources=retrieval_sources or [],
                            metadata={
                                "method": "llm_synthesis",
                                "provider": llm_response.get("provider", "unknown")
                            },
                            execution_time_ms=int((time.time() - agent_start) * 1000)
                        )
                
                results.append(result)
                print(f"Completed {agent_type.value} in {result.execution_time_ms}ms")
                
            except Exception as e:
                error_result = AgentResult(
                    agent_type=agent_type,
                    success=False,
                    content=None,
                    error=str(e),
                    execution_time_ms=int((time.time() - agent_start) * 1000)
                )
                results.append(error_result)
                print(f"Agent {agent_type.value} failed: {e}")
        
        return results
    
    async def synthesize_final_response(self, results: List[AgentResult], context: QueryContext) -> Dict[str, Any]:
        """Synthesize final response from agent results."""
        successful_results = [r for r in results if r.success]
        
        if not successful_results:
            return {
                "success": False,
                "error": "All agents failed",
                "results": [{"agent": r.agent_type.value, "error": r.error} for r in results]
            }
        
        # Find key results
        retrieval_result = next((r for r in successful_results if r.agent_type == AgentType.RETRIEVAL), None)
        synthesis_result = next((r for r in successful_results if r.agent_type == AgentType.SYNTHESIS), None)
        fact_check_result = next((r for r in successful_results if r.agent_type == AgentType.FACT_CHECK), None)
        
        # Build final response with real AI content
        response = {
            "success": True,
            "query": context.query,
            "query_id": context.trace_id,
            "complexity": context.complexity.value,
            "answer": "Real AI response will be populated below",  # Placeholder - updated below
            "sources": [],
            "verification": {},
            "metadata": {
                "agents_used": [r.agent_type.value for r in successful_results],
                "total_agents": len(results),
                "successful_agents": len(successful_results)
            }
        }
        
        # Extract content from results
        if synthesis_result and synthesis_result.content:
            synthesis_content = synthesis_result.content
            if isinstance(synthesis_content, dict):
                response["answer"] = synthesis_content.get("synthesis", synthesis_content.get("summary", "Synthesis completed"))
                response["metadata"].update(synthesis_content.get("metadata", {}))
        
        if retrieval_result and retrieval_result.sources:
            response["sources"] = retrieval_result.sources[:5]  # Top 5 sources
        
        if fact_check_result and fact_check_result.content:
            fact_content = fact_check_result.content
            if isinstance(fact_content, dict):
                response["verification"] = {
                    "status": fact_content.get("verification_status", "completed"),
                    "confidence": fact_content.get("confidence_score", 0.8)
                }
        
        return response


# Global orchestrator instance
agent_orchestrator = AgentOrchestrator()
