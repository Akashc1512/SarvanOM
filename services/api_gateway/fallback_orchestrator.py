"""
Fallback Orchestrator for when main orchestrator fails.

# DEAD CODE - Candidate for deletion: This class is not imported or used anywhere in the codebase
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from shared.core.agents.base_agent import AgentResult, QueryContext

logger = logging.getLogger(__name__)

class FallbackOrchestrator:
    """Fallback orchestrator that uses direct service calls."""
    
    def __init__(self):
        self.search_agent = None
        self.factcheck_agent = None
        self.synthesis_agent = None
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize individual agents."""
        try:
            from services.search_service.retrieval_agent import RetrievalAgent
            self.search_agent = RetrievalAgent()
            logger.info("✅ Search agent initialized")
        except Exception as e:
            logger.warning(f"⚠️ Search agent initialization failed: {e}")
        
        try:
            from services.factcheck_service.factcheck_agent import FactCheckAgent
            self.factcheck_agent = FactCheckAgent()
            logger.info("✅ Factcheck agent initialized")
        except Exception as e:
            logger.warning(f"⚠️ Factcheck agent initialization failed: {e}")
        
        try:
            from services.synthesis_service.synthesis_agent import SynthesisAgent
            self.synthesis_agent = SynthesisAgent()
            logger.info("✅ Synthesis agent initialized")
        except Exception as e:
            logger.warning(f"⚠️ Synthesis agent initialization failed: {e}")
    
    async def process_query(self, query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process query using fallback pipeline."""
        logger.info(f"🔄 Using fallback orchestrator for query: {query[:50]}...")
        
        try:
            # Step 1: Search
            search_results = {}
            if self.search_agent:
                try:
                    search_context = QueryContext(
                        query=query,
                        user_id=user_context.get("user_id", "anonymous"),
                        session_id=user_context.get("session_id", "fallback-session"),
                        max_tokens=user_context.get("max_tokens", 1000),
                        confidence_threshold=user_context.get("confidence_threshold", 0.8)
                    )
                    
                    search_task = {"query": query, "context": search_context}
                    search_result = await self.search_agent.process_task(search_task, search_context)
                    
                    if search_result.success:
                        search_results = search_result.data
                        logger.info(f"✅ Search completed: {len(search_results.get('documents', []))} documents")
                    else:
                        logger.warning(f"⚠️ Search failed: {search_result.error}")
                except Exception as e:
                    logger.error(f"❌ Search error: {e}")
            
            # Step 2: Fact-checking
            factcheck_results = {}
            if self.factcheck_agent and search_results:
                try:
                    factcheck_context = QueryContext(
                        query=query,
                        user_id=user_context.get("user_id", "anonymous"),
                        session_id=user_context.get("session_id", "fallback-session")
                    )
                    
                    factcheck_task = {
                        "query": query,
                        "documents": search_results.get("documents", []),
                        "context": factcheck_context
                    }
                    factcheck_result = await self.factcheck_agent.process_task(factcheck_task, factcheck_context)
                    
                    if factcheck_result.success:
                        factcheck_results = factcheck_result.data
                        logger.info("✅ Fact-checking completed")
                    else:
                        logger.warning(f"⚠️ Fact-checking failed: {factcheck_result.error}")
                except Exception as e:
                    logger.error(f"❌ Fact-checking error: {e}")
            
            # Step 3: Synthesis
            synthesis_results = {}
            if self.synthesis_agent:
                try:
                    synthesis_context = QueryContext(
                        query=query,
                        user_id=user_context.get("user_id", "anonymous"),
                        session_id=user_context.get("session_id", "fallback-session")
                    )
                    
                    synthesis_task = {
                        "query": query,
                        "search_results": search_results,
                        "factcheck_results": factcheck_results,
                        "context": synthesis_context
                    }
                    synthesis_result = await self.synthesis_agent.process_task(synthesis_task, synthesis_context)
                    
                    if synthesis_result.success:
                        synthesis_results = synthesis_result.data
                        logger.info("✅ Synthesis completed")
                    else:
                        logger.warning(f"⚠️ Synthesis failed: {synthesis_result.error}")
                except Exception as e:
                    logger.error(f"❌ Synthesis error: {e}")
            
            # Compile results
            result = {
                "success": True,
                "answer": synthesis_results.get("answer", "Unable to generate answer"),
                "citations": synthesis_results.get("citations", []),
                "confidence": synthesis_results.get("confidence", 0.5),
                "metadata": {
                    "orchestrator_type": "fallback",
                    "search_success": bool(search_results),
                    "factcheck_success": bool(factcheck_results),
                    "synthesis_success": bool(synthesis_results),
                    "agent_results": {
                        "search": search_results,
                        "factcheck": factcheck_results,
                        "synthesis": synthesis_results
                    }
                }
            }
            
            logger.info("✅ Fallback orchestrator completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Fallback orchestrator failed: {e}")
            return {
                "success": False,
                "error": f"Fallback processing failed: {str(e)}",
                "answer": "Sorry, I encountered an error while processing your query.",
                "citations": [],
                "confidence": 0.0,
                "metadata": {
                    "orchestrator_type": "fallback",
                    "error": str(e)
                }
            }
