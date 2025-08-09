"""
Query Processor Service

This module contains the core query processing logic.
It handles the actual processing pipeline and coordinates with agents.
Migrated from the original QueryService with enhanced functionality.
"""

import asyncio
import time
import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

from ...models.domain.query import Query, QueryResult, QueryType
from ...models.domain.agent import Agent, AgentType
from ..agents.agent_coordinator import AgentCoordinator
from ..core.cache_service import CacheService
from shared.clients.microservices import call_retrieval_search, call_synthesis_generate

logger = logging.getLogger(__name__)


@dataclass
class QueryContext:
    """Context for query processing."""

    user_id: str
    session_id: str
    query_id: str
    timestamp: datetime
    metadata: Dict[str, Any]


class QueryProcessor:
    """Processes queries using the appropriate pipeline.

    Migrated from the original QueryService with enhanced functionality
    and clean architecture principles.
    """

    def __init__(
        self, agent_coordinator: AgentCoordinator, cache_service: CacheService
    ):
        self.agent_coordinator = agent_coordinator
        self.cache_service = cache_service
        self.active_queries = {}
        self.query_history = []

    async def process_basic_query(self, query: Query) -> Dict[str, Any]:
        """Process a basic query using simplified pipeline."""
        start_time = time.time()

        # Create query context
        context = QueryContext(
            user_id=query.context.user_id,
            session_id=query.context.session_id,
            query_id=query.id,
            timestamp=datetime.now(),
            metadata=query.context.metadata,
        )

        # Check cache first
        cached_result = await self._get_cached_result(query, context)
        if cached_result:
            # Cache hit
            await self._track_query(query, context, cached_result, cache_hit=True)
            return cached_result

        # Cache miss - process query
        result = await self._execute_query_pipeline(query, context)

        # Cache the result
        await self._cache_result(query, context, result)

        # Track query with cache miss
        await self._track_query(query, context, result, cache_hit=False)

        return result

    async def process_comprehensive_query(
        self, query: Query, options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process a comprehensive query using full pipeline."""
        start_time = time.time()
        query_id = str(uuid.uuid4())

        try:
            # Create query context
            context = QueryContext(
                user_id=query.context.user_id,
                session_id=query.context.session_id,
                query_id=query_id,
                timestamp=datetime.now(),
                metadata={**query.context.metadata, "options": options or {}},
            )

            # Execute comprehensive pipeline
            result = await self._execute_comprehensive_pipeline(query, context, options)

            # Add timing information
            result["processing_time"] = time.time() - start_time
            result["query_id"] = query_id

            # Track query
            await self._track_query(query, context, result)

            return result

        except Exception as e:
            logger.error(
                f"Comprehensive query processing failed: {e}",
                extra={"query_id": query_id},
            )
            return {
                "success": False,
                "error": str(e),
                "query_id": query_id,
                "processing_time": time.time() - start_time,
            }

    async def _classify_query(self, query: Query) -> Dict[str, Any]:
        """Classify the type and intent of the query."""
        # Use classification agent
        classification_agent = await self.agent_coordinator.get_agent(
            AgentType.RETRIEVAL
        )

        classification_result = await classification_agent.process(
            {
                "task": "classify_query",
                "query": query.text,
                "context": query.context.metadata,
            }
        )

        return {
            "intent": classification_result.get("intent", "general"),
            "domain": classification_result.get("domain", "general"),
            "complexity": classification_result.get("complexity", "medium"),
            "requires_fact_checking": classification_result.get(
                "requires_fact_checking", False
            ),
            "requires_synthesis": classification_result.get("requires_synthesis", True),
        }

    async def _retrieve_information(
        self, query: Query, classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Retrieve relevant information for the query."""
        retrieval_agent = await self.agent_coordinator.get_agent(AgentType.RETRIEVAL)

        retrieval_result = await retrieval_agent.process(
            {
                "task": "retrieve_information",
                "query": query.text,
                "classification": classification,
                "max_results": 10,
                "context": query.context.metadata,
            }
        )

        return {
            "sources": retrieval_result.get("sources", []),
            "method": retrieval_result.get("method", "vector_search"),
            "total_results": len(retrieval_result.get("sources", [])),
            "relevance_scores": retrieval_result.get("relevance_scores", []),
        }

    async def _generate_answer(
        self, query: Query, retrieval_results: Dict[str, Any]
    ) -> str:
        """Generate answer from retrieved information."""
        synthesis_agent = await self.agent_coordinator.get_agent(AgentType.SYNTHESIS)

        synthesis_result = await synthesis_agent.process(
            {
                "task": "generate_answer",
                "query": query.text,
                "sources": retrieval_results.get("sources", []),
                "max_tokens": query.context.max_tokens,
                "context": query.context.metadata,
            }
        )

        return synthesis_result.get("answer", "")

    async def _calculate_confidence(
        self, query: Query, answer: str, retrieval_results: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for the answer."""
        # Simple confidence calculation based on source quality and answer length
        source_count = len(retrieval_results.get("sources", []))
        answer_length = len(answer)

        # Base confidence on source count and answer quality
        source_confidence = min(source_count / 5.0, 1.0)  # Max 1.0 for 5+ sources
        length_confidence = min(answer_length / 100.0, 1.0)  # Max 1.0 for 100+ chars

        return (source_confidence + length_confidence) / 2.0

    async def _analyze_query(self, query: Query) -> Dict[str, Any]:
        """Analyze query for comprehensive processing."""
        # Use retrieval agent for analysis
        retrieval_agent = await self.agent_coordinator.get_agent(AgentType.RETRIEVAL)

        analysis_result = await retrieval_agent.process(
            {
                "task": "analyze_query",
                "query": query.text,
                "context": query.context.metadata,
            }
        )

        return {
            "intent": analysis_result.get("intent", "general"),
            "domain": analysis_result.get("domain", "general"),
            "complexity": analysis_result.get("complexity", "medium"),
            "required_sources": analysis_result.get(
                "required_sources", ["web", "database"]
            ),
            "verification_needed": analysis_result.get("verification_needed", True),
            "synthesis_approach": analysis_result.get(
                "synthesis_approach", "comprehensive"
            ),
        }

    async def _multi_source_retrieval(
        self, query: Query, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Retrieve information from multiple sources."""
        retrieval_agent = await self.agent_coordinator.get_agent(AgentType.RETRIEVAL)

        retrieval_result = await retrieval_agent.process(
            {
                "task": "multi_source_retrieval",
                "query": query.text,
                "analysis": analysis,
                "sources": analysis.get("required_sources", ["web", "database"]),
                "max_results_per_source": 5,
                "context": query.context.metadata,
            }
        )

        return {
            "sources": retrieval_result.get("sources", []),
            "source_breakdown": retrieval_result.get("source_breakdown", {}),
            "total_results": len(retrieval_result.get("sources", [])),
            "relevance_scores": retrieval_result.get("relevance_scores", []),
        }

    async def _verify_information(
        self, query: Query, retrieval_results: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify and fact-check retrieved information."""
        if not analysis.get("verification_needed", True):
            return {"verified": True, "verification_score": 1.0}

        fact_check_agent = await self.agent_coordinator.get_agent(AgentType.FACT_CHECK)

        verification_result = await fact_check_agent.process(
            {
                "task": "verify_information",
                "query": query.text,
                "sources": retrieval_results.get("sources", []),
                "analysis": analysis,
                "context": query.context.metadata,
            }
        )

        return {
            "verified": verification_result.get("verified", True),
            "verification_score": verification_result.get("verification_score", 1.0),
            "verification_details": verification_result.get("details", {}),
            "contradictions": verification_result.get("contradictions", []),
        }

    async def _synthesize_answer(
        self,
        query: Query,
        retrieval_results: Dict[str, Any],
        verification_results: Dict[str, Any],
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Synthesize comprehensive answer."""
        synthesis_agent = await self.agent_coordinator.get_agent(AgentType.SYNTHESIS)

        synthesis_result = await synthesis_agent.process(
            {
                "task": "synthesize_answer",
                "query": query.text,
                "sources": retrieval_results.get("sources", []),
                "verification": verification_results,
                "analysis": analysis,
                "max_tokens": query.context.max_tokens,
                "context": query.context.metadata,
            }
        )

        return {
            "answer": synthesis_result.get("answer", ""),
            "synthesis_method": synthesis_result.get("method", "comprehensive"),
            "source_usage": synthesis_result.get("source_usage", {}),
            "key_points": synthesis_result.get("key_points", []),
        }

    async def _assess_quality(
        self,
        query: Query,
        synthesis_results: Dict[str, Any],
        verification_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Assess the quality of the synthesized answer."""
        # Use synthesis agent for quality assessment
        synthesis_agent = await self.agent_coordinator.get_agent(AgentType.SYNTHESIS)

        quality_result = await synthesis_agent.process(
            {
                "task": "assess_quality",
                "query": query.text,
                "answer": synthesis_results.get("answer", ""),
                "verification": verification_results,
                "context": query.context.metadata,
            }
        )

        return {
            "confidence": quality_result.get("confidence", 0.8),
            "completeness": quality_result.get("completeness", 0.8),
            "accuracy": quality_result.get("accuracy", 0.8),
            "relevance": quality_result.get("relevance", 0.8),
            "overall_score": quality_result.get("overall_score", 0.8),
        }

    async def _generate_alternatives(
        self, query: Query, synthesis_results: Dict[str, Any], analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate alternative answers."""
        synthesis_agent = await self.agent_coordinator.get_agent(AgentType.SYNTHESIS)

        alternatives_result = await synthesis_agent.process(
            {
                "task": "generate_alternatives",
                "query": query.text,
                "primary_answer": synthesis_results.get("answer", ""),
                "analysis": analysis,
                "max_alternatives": 3,
                "context": query.context.metadata,
            }
        )

        return alternatives_result.get("alternatives", [])

    async def _execute_query_pipeline(
        self, query: Query, context: QueryContext
    ) -> Dict[str, Any]:
        """Execute the basic query pipeline."""
        try:
            # Step 1: Query classification
            classification = await self._classify_query(query)

            # Step 2: Search and retrieval
            search_results = await self._execute_search(query, classification)

            # Step 3: Fact checking
            verification_results = await self._execute_fact_checking(
                query, search_results
            )

            # Step 4: Synthesis
            synthesis_results = await self._execute_synthesis(
                query, search_results, verification_results
            )

            # Format response
            return await self._format_response(
                query, search_results, verification_results, synthesis_results, context
            )

        except Exception as e:
            logger.error(f"Query pipeline execution failed: {e}", exc_info=True)
            raise

    async def _execute_search(
        self, query: Query, classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute search and retrieval."""
        # Prefer microservice if available; fall back to agent
        try:
            search_result = await call_retrieval_search(
                {
                    "query": query.text,
                    "classification": classification,
                    "max_results": 10,
                    "context": query.context.metadata,
                }
            )
        except Exception:
            retrieval_agent = await self.agent_coordinator.get_agent(
                AgentType.RETRIEVAL
            )
            search_result = await retrieval_agent.process(
                {
                    "task": "search",
                    "query": query.text,
                    "classification": classification,
                    "max_results": 10,
                    "context": query.context.metadata,
                }
            )

        return {
            "sources": search_result.get("sources", []),
            "method": search_result.get("method", "vector_search"),
            "total_results": len(search_result.get("sources", [])),
            "relevance_scores": search_result.get("relevance_scores", []),
        }

    async def _execute_fact_checking(
        self, query: Query, search_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute fact checking."""
        fact_check_agent = await self.agent_coordinator.get_agent(AgentType.FACT_CHECK)

        fact_check_result = await fact_check_agent.process(
            {
                "task": "fact_check",
                "query": query.text,
                "sources": search_results.get("sources", []),
                "context": query.context.metadata,
            }
        )

        return {
            "verified": fact_check_result.get("verified", True),
            "verification_score": fact_check_result.get("verification_score", 1.0),
            "verification_details": fact_check_result.get("details", {}),
            "contradictions": fact_check_result.get("contradictions", []),
        }

    async def _execute_synthesis(
        self,
        query: Query,
        search_results: Dict[str, Any],
        verification_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute synthesis."""
        try:
            synthesis_result = await call_synthesis_generate(
                {
                    "query": query.text,
                    "sources": search_results.get("sources", []),
                    "verification": verification_results,
                    "max_tokens": query.context.max_tokens,
                    "context": query.context.metadata,
                }
            )
        except Exception:
            synthesis_agent = await self.agent_coordinator.get_agent(
                AgentType.SYNTHESIS
            )
            synthesis_result = await synthesis_agent.process(
                {
                    "task": "synthesize",
                    "query": query.text,
                    "sources": search_results.get("sources", []),
                    "verification": verification_results,
                    "max_tokens": query.context.max_tokens,
                    "context": query.context.metadata,
                }
            )

        return {
            "answer": synthesis_result.get("answer", ""),
            "synthesis_method": synthesis_result.get("method", "basic"),
            "source_usage": synthesis_result.get("source_usage", {}),
            "key_points": synthesis_result.get("key_points", []),
        }

    async def _format_response(
        self,
        query: Query,
        search_results: Dict[str, Any],
        verification_results: Dict[str, Any],
        synthesis_results: Dict[str, Any],
        context: QueryContext,
    ) -> Dict[str, Any]:
        """Format the basic response."""
        return {
            "success": True,
            "answer": synthesis_results.get("answer", ""),
            "confidence": verification_results.get("verification_score", 0.8),
            "sources": search_results.get("sources", []),
            "verification": verification_results,
            "synthesis_method": synthesis_results.get("synthesis_method", "basic"),
            "key_points": synthesis_results.get("key_points", []),
            "source_usage": synthesis_results.get("source_usage", {}),
            "metadata": {
                "query_id": context.query_id,
                "user_id": context.user_id,
                "session_id": context.session_id,
                "timestamp": context.timestamp.isoformat(),
                "verification_details": verification_results.get(
                    "verification_details", {}
                ),
            },
        }

    async def _get_cached_result(
        self, query: Query, context: QueryContext
    ) -> Optional[Dict[str, Any]]:
        """Get cached result for query."""
        cache_key = f"query:{hash(query.text)}:{context.user_id}"
        return await self.cache_service.get(cache_key)

    async def _cache_result(
        self, query: Query, context: QueryContext, result: Dict[str, Any]
    ):
        """Cache query result."""
        cache_key = f"query:{hash(query.text)}:{context.user_id}"
        await self.cache_service.set(cache_key, result, ttl=3600)  # 1 hour TTL

    async def _execute_comprehensive_pipeline(
        self, query: Query, context: QueryContext, options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute the comprehensive query pipeline."""
        try:
            # Step 1: Query analysis
            analysis = await self._analyze_query(query)

            # Step 2: Multi-source retrieval
            retrieval_results = await self._execute_multi_source_retrieval(
                query, analysis
            )

            # Step 3: Advanced verification
            verification_results = await self._execute_advanced_verification(
                query, retrieval_results, analysis
            )

            # Step 4: Advanced synthesis
            synthesis_results = await self._execute_advanced_synthesis(
                query, retrieval_results, verification_results, analysis
            )

            # Step 5: Quality assessment
            quality_results = await self._assess_synthesis_quality(
                synthesis_results.get("answer", ""),
                verification_results.get("verified_content", []),
                verification_results,
            )

            # Step 6: Generate alternatives
            alternatives = await self._generate_alternatives(
                query, synthesis_results.get("verified_content", []), analysis
            )

            # Format comprehensive response
            return await self._format_comprehensive_response(
                query,
                retrieval_results,
                verification_results,
                synthesis_results,
                quality_results,
                context,
            )

        except Exception as e:
            logger.error(f"Comprehensive pipeline execution failed: {e}", exc_info=True)
            raise

    async def _execute_multi_source_retrieval(
        self, query: Query, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute multi-source retrieval."""
        retrieval_agent = await self.agent_coordinator.get_agent(AgentType.RETRIEVAL)

        retrieval_result = await retrieval_agent.process(
            {
                "task": "multi_source_retrieval",
                "query": query.text,
                "analysis": analysis,
                "sources": analysis.get(
                    "required_sources", ["web", "database", "knowledge_graph"]
                ),
                "max_results_per_source": 5,
                "context": query.context.metadata,
            }
        )

        return {
            "sources": retrieval_result.get("sources", []),
            "source_breakdown": retrieval_result.get("source_breakdown", {}),
            "total_results": len(retrieval_result.get("sources", [])),
            "relevance_scores": retrieval_result.get("relevance_scores", []),
        }

    async def _execute_advanced_verification(
        self, query: Query, retrieval_results: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute advanced verification and fact-checking."""
        fact_check_agent = await self.agent_coordinator.get_agent(AgentType.FACT_CHECK)

        verification_result = await fact_check_agent.process(
            {
                "task": "advanced_verification",
                "query": query.text,
                "sources": retrieval_results.get("sources", []),
                "analysis": analysis,
                "context": query.context.metadata,
            }
        )

        return {
            "verified": verification_result.get("verified", True),
            "verification_score": verification_result.get("verification_score", 1.0),
            "verification_details": verification_result.get("details", {}),
            "verified_content": verification_result.get("verified_content", []),
            "contradictions": verification_result.get("contradictions", []),
        }

    async def _execute_advanced_synthesis(
        self,
        query: Query,
        retrieval_results: Dict[str, Any],
        verification_results: Dict[str, Any],
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute advanced synthesis."""
        synthesis_agent = await self.agent_coordinator.get_agent(AgentType.SYNTHESIS)

        synthesis_result = await synthesis_agent.process(
            {
                "task": "advanced_synthesis",
                "query": query.text,
                "sources": retrieval_results.get("sources", []),
                "verification": verification_results,
                "analysis": analysis,
                "max_tokens": query.context.max_tokens,
                "context": query.context.metadata,
            }
        )

        return {
            "answer": synthesis_result.get("answer", ""),
            "synthesis_method": synthesis_result.get("method", "comprehensive"),
            "source_usage": synthesis_result.get("source_usage", {}),
            "key_points": synthesis_result.get("key_points", []),
            "verified_content": verification_results.get("verified_content", []),
        }

    async def _assess_synthesis_quality(
        self,
        answer: str,
        verified_content: List[Dict[str, Any]],
        verification_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Assess the quality of the synthesized answer."""
        synthesis_agent = await self.agent_coordinator.get_agent(AgentType.SYNTHESIS)

        quality_result = await synthesis_agent.process(
            {
                "task": "assess_synthesis_quality",
                "answer": answer,
                "verified_content": verified_content,
                "verification_results": verification_results,
            }
        )

        return {
            "confidence": quality_result.get("confidence", 0.8),
            "completeness": quality_result.get("completeness", 0.8),
            "accuracy": quality_result.get("accuracy", 0.8),
            "relevance": quality_result.get("relevance", 0.8),
            "overall_score": quality_result.get("overall_score", 0.8),
        }

    async def _format_comprehensive_response(
        self,
        query: Query,
        retrieval_results: Dict[str, Any],
        verification_results: Dict[str, Any],
        synthesis_results: Dict[str, Any],
        quality_results: Dict[str, Any],
        context: QueryContext,
    ) -> Dict[str, Any]:
        """Format the comprehensive response."""
        return {
            "success": True,
            "answer": synthesis_results.get("answer", ""),
            "confidence": quality_results.get("confidence", 0.8),
            "sources": retrieval_results.get("sources", []),
            "verification": verification_results,
            "quality_metrics": quality_results,
            "synthesis_method": synthesis_results.get(
                "synthesis_method", "comprehensive"
            ),
            "key_points": synthesis_results.get("key_points", []),
            "source_usage": synthesis_results.get("source_usage", {}),
            "metadata": {
                "query_id": context.query_id,
                "user_id": context.user_id,
                "session_id": context.session_id,
                "timestamp": context.timestamp.isoformat(),
                "analysis": synthesis_results.get("analysis", {}),
                "verification_details": verification_results.get(
                    "verification_details", {}
                ),
                "quality_assessment": quality_results,
            },
        }

    async def _track_query(
        self,
        query: Query,
        context: QueryContext,
        result: Dict[str, Any],
        cache_hit: bool = False,
    ):
        """Track query processing for analytics."""
        tracking_data = {
            "query_id": context.query_id,
            "user_id": context.user_id,
            "session_id": context.session_id,
            "timestamp": context.timestamp,
            "query_text": query.text,
            "processing_time": result.get("processing_time", 0),
            "cache_hit": cache_hit,
            "success": result.get("success", True),
            "confidence": result.get("confidence", 0.0),
            "source_count": len(result.get("sources", [])),
            "metadata": context.metadata,
        }

        self.query_history.append(tracking_data)

        # Keep only last 1000 queries in memory
        if len(self.query_history) > 1000:
            self.query_history = self.query_history[-1000:]

        logger.info(f"Query tracked: {context.query_id}", extra=tracking_data)

    async def get_query_history(
        self, user_id: str = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get query history."""
        if user_id:
            return [q for q in self.query_history if q["user_id"] == user_id][-limit:]
        return self.query_history[-limit:]

    async def get_query_stats(self) -> Dict[str, Any]:
        """Get query processing statistics."""
        if not self.query_history:
            return {"total_queries": 0, "avg_processing_time": 0, "success_rate": 0}

        total_queries = len(self.query_history)
        successful_queries = len(
            [q for q in self.query_history if q.get("success", True)]
        )
        avg_processing_time = (
            sum(q.get("processing_time", 0) for q in self.query_history) / total_queries
        )

        return {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "failed_queries": total_queries - successful_queries,
            "success_rate": (
                successful_queries / total_queries if total_queries > 0 else 0
            ),
            "avg_processing_time": avg_processing_time,
            "cache_hit_rate": (
                len([q for q in self.query_history if q.get("cache_hit", False)])
                / total_queries
                if total_queries > 0
                else 0
            ),
        }
