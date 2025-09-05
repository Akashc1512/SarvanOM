"""
HuggingFace LLM Provider Client
Implements HuggingFace API integration with proper error handling and retry logic.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)

class HuggingFaceClient:
    """HuggingFace API client with comprehensive error handling."""
    
    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.setup_client()
    
    def setup_client(self):
        """Initialize HuggingFace client."""
        if not self.api_key:
            logger.error("HuggingFace API key not configured")
            return
        
        try:
            # Import the HuggingFace integration
            from services.gateway.huggingface_integration import huggingface_integration
            self.integration = huggingface_integration
            logger.info("[OK] HuggingFace client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace client: {e}")
            self.integration = None
    
    async def generate_completion(self, prompt: str, model: str = "microsoft/DialoGPT-medium", 
                                max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        """Generate completion using HuggingFace API (alias for compatibility)."""
        result = await self.generate_text(prompt, max_tokens, temperature, model)
        return result.get("content") if result.get("success") else None
    
    def _select_model(self, prompt: str, max_tokens: int) -> str:
        """Select appropriate HuggingFace model based on task."""
        prompt_lower = prompt.lower()
        
        # Task-specific model selection
        if "code" in prompt_lower or "programming" in prompt_lower:
            return "microsoft/DialoGPT-medium"  # Good for code-related tasks
        elif "question" in prompt_lower or "answer" in prompt_lower:
            return "microsoft/DialoGPT-medium"  # Good for Q&A
        elif "summarize" in prompt_lower or "summary" in prompt_lower:
            return "facebook/bart-large-cnn"  # Good for summarization
        else:
            return "microsoft/DialoGPT-medium"  # Default model
    
    async def generate_text(
        self, 
        prompt: str, 
        max_tokens: int = 100, 
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate text using HuggingFace API."""
        if not self.integration:
            return {
                "success": False,
                "error": "HuggingFace client not available",
                "content": None
            }
        
        try:
            # Select appropriate model based on task
            if not model:
                model = self._select_model(prompt, max_tokens)
            
            # Use the comprehensive HuggingFace integration
            response = await self.integration.generate_text(
                prompt=prompt,
                model_name=model,
                max_length=max_tokens,
                temperature=temperature
            )
            
            return {
                "success": True,
                "content": response.result,
                "model": model,
                "provider": "huggingface"
            }
            
        except asyncio.TimeoutError:
            logger.error("HuggingFace API call timed out")
            return {
                "success": False,
                "error": "API call timed out",
                "content": None
            }
        except Exception as e:
            logger.error(f"HuggingFace API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    def is_available(self) -> bool:
        """Check if HuggingFace client is available and configured."""
        return self.integration is not None and self.api_key is not None
