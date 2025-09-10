"""
Pre-flight Lane - SarvanOM v2 Retrieval Service

Pre-flight lane for Guided Prompt Confirmation.
Budget: 500ms (all modes).
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

@dataclass
class RetrievalResult:
    lane: str
    status: str
    results: List[Dict[str, Any]]
    latency_ms: float
    error: Optional[str] = None

class PreflightLane:
    """Pre-flight lane for Guided Prompt Confirmation"""
    
    def __init__(self, guided_prompt_url: str = "http://localhost:8003"):
        self.guided_prompt_url = guided_prompt_url
        self.budget_ms = 500  # Fixed 500ms budget for all modes
        self.http_client = httpx.AsyncClient()
    
    async def retrieve(self, query: str, complexity: str, constraints: List[Dict[str, Any]] = None, 
                      user_id: str = "anonymous", session_id: str = "default", 
                      trace_id: str = "default", budget_remaining: float = 1.0) -> RetrievalResult:
        """Process pre-flight refinement"""
        start_time = time.time()
        
        try:
            # Call Guided Prompt service
            response = await self.http_client.post(
                f"{self.guided_prompt_url}/refine",
                json={
                    "query": query,
                    "context": {
                        "user_id": user_id,
                        "session_id": session_id,
                        "trace_id": trace_id,
                        "budget_remaining": budget_remaining
                    }
                },
                timeout=0.5  # 500ms timeout
            )
            
            if response.status_code == 200:
                refinement_data = response.json()
                
                # Convert to retrieval result format
                results = []
                if refinement_data.get("should_trigger"):
                    for suggestion in refinement_data.get("suggestions", []):
                        results.append({
                            "id": f"preflight_{suggestion['id']}",
                            "title": suggestion["title"],
                            "content": suggestion["description"],
                            "refined_query": suggestion["refined_query"],
                            "type": suggestion["type"],
                            "confidence": suggestion["confidence"],
                            "reasoning": suggestion["reasoning"],
                            "lane": "preflight"
                        })
                
                return RetrievalResult(
                    lane="preflight",
                    status="success",
                    results=results,
                    latency_ms=(time.time() - start_time) * 1000
                )
            else:
                return RetrievalResult(
                    lane="preflight",
                    status="error",
                    results=[],
                    latency_ms=(time.time() - start_time) * 1000,
                    error=f"Guided prompt service error: {response.status_code}"
                )
                
        except asyncio.TimeoutError:
            return RetrievalResult(
                lane="preflight",
                status="timeout",
                results=[],
                latency_ms=(time.time() - start_time) * 1000,
                error="Pre-flight lane exceeded 500ms budget"
            )
        except Exception as e:
            return RetrievalResult(
                lane="preflight",
                status="error",
                results=[],
                latency_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
