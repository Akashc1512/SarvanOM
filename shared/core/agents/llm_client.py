"""
Simple LLM Client for Agents
Provides a unified interface for LLM operations in the agents module.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from services.gateway.real_llm_integration import LLMRequest, RealLLMProcessor


@dataclass
class LLMResponse:
    """Simple LLM response structure."""
    text: str
    model: str
    tokens_used: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMError(Exception):
    """LLM operation error."""
    pass


class LLMClient:
    """LLM client for agents using the existing RealLLMProcessor."""
    
    def __init__(self):
        self.processor = RealLLMProcessor()
    
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """
        Generate text using an LLMRequest object.
        
        Args:
            request: LLMRequest object containing all parameters
            
        Returns:
            LLMResponse with generated text
        """
        try:
            # Use the existing processor to generate text
            result = await self.processor._call_llm_with_provider(
                request, 
                self.processor.select_optimal_provider(request.complexity, request.prefer_free)
            )
            
            return LLMResponse(
                text=result,
                model="selected_model",  # The processor doesn't return model info
                tokens_used=None,
                metadata={"provider": "real_llm_processor"}
            )
        except Exception as e:
            raise LLMError(f"LLM generation failed: {str(e)}")
