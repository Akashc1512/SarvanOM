"""
Fact Check Service

This service provides fact checking functionality by wrapping the existing
fact check agent and providing a clean interface for the API gateway.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import the existing fact check agent
from .factcheck_agent import FactCheckAgent

logger = logging.getLogger(__name__)


class FactCheckService:
    """
    Fact Check Service that provides fact checking and validation functionality.
    Wraps the existing FactCheckAgent to provide a clean API interface.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.fact_check_agent = FactCheckAgent(config)
        logger.info("FactCheckService initialized")
    
    async def fact_check(self, claim: str, sources: List[str] = None, user_id: str = None) -> Dict[str, Any]:
        """Fact check a claim using the fact check agent."""
        try:
            # Prepare fact check context
            fact_check_context = {
                "user_id": user_id,
                "sources": sources or [],
                "timestamp": datetime.now().isoformat()
            }
            
            # Perform fact check using agent
            result = await self.fact_check_agent.fact_check(
                claim=claim,
                context=fact_check_context
            )
            
            return {
                "status": "success",
                "result": result,
                "claim": claim,
                "sources": sources,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Fact check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "claim": claim,
                "timestamp": datetime.now().isoformat()
            }
    
    async def verify_claim(self, claim: str, evidence: List[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Verify a claim against provided evidence."""
        try:
            result = await self.fact_check_agent.verify_claim(
                claim=claim,
                evidence=evidence,
                **kwargs
            )
            
            return {
                "status": "success",
                "result": result,
                "claim": claim,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Claim verification failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "claim": claim,
                "timestamp": datetime.now().isoformat()
            }
    
    async def batch_fact_check(self, claims: List[str], user_id: str = None) -> Dict[str, Any]:
        """Fact check multiple claims."""
        try:
            results = []
            for claim in claims:
                result = await self.fact_check(claim, user_id=user_id)
                results.append(result)
            
            return {
                "status": "success",
                "results": results,
                "claims_count": len(claims),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Batch fact check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "claims_count": len(claims),
                "timestamp": datetime.now().isoformat()
            }
    
    async def assess_source_credibility(self, source_url: str, **kwargs) -> Dict[str, Any]:
        """Assess the credibility of a source."""
        try:
            credibility_score = await self.fact_check_agent.assess_source_credibility(
                source_url=source_url,
                **kwargs
            )
            
            return {
                "status": "success",
                "credibility_score": credibility_score,
                "source_url": source_url,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Source credibility assessment failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "source_url": source_url,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_fact_check_history(self, user_id: str = None, limit: int = 50) -> Dict[str, Any]:
        """Get fact check history for a user."""
        try:
            history = await self.fact_check_agent.get_history(
                user_id=user_id,
                limit=limit
            )
            
            return {
                "status": "success",
                "history": history,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get fact check history: {e}")
            return {
                "status": "error",
                "error": str(e),
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status and configuration."""
        return {
            "service": "fact_check",
            "status": "healthy",
            "agent_available": hasattr(self, 'fact_check_agent'),
            "config": self.config,
            "timestamp": datetime.now().isoformat()
        }
    
    async def shutdown(self):
        """Shutdown the fact check service."""
        logger.info("Shutting down FactCheckService")
        # Cleanup if needed
        pass 