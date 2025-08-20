"""
Local Stub LLM Provider Client
Provides stub responses when no other providers are available.
"""

import asyncio
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class LocalStubClient:
    """Local stub client for fallback responses."""
    
    def __init__(self):
        logger.info("✅ Local Stub client initialized")
    
    async def generate_text(
        self, 
        prompt: str, 
        max_tokens: int = 100, 
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate stub response when no providers are available."""
        try:
            # Generate a helpful stub response
            stub_response = self._generate_stub_response(prompt)
            
            return {
                "success": True,
                "content": stub_response,
                "model": "local_stub",
                "provider": "local_stub"
            }
            
        except Exception as e:
            logger.error(f"Local stub error: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    def _generate_stub_response(self, prompt: str) -> str:
        """Generate a helpful stub response based on the prompt."""
        prompt_lower = prompt.lower()
        
        if "hello" in prompt_lower or "hi" in prompt_lower:
            return "Hello! I'm a stub response while the LLM providers are being configured. Please check your API keys and try again."
        elif "help" in prompt_lower:
            return "I'm currently in stub mode. To get real responses, please ensure your LLM providers (OpenAI, Anthropic, Ollama, or HuggingFace) are properly configured with valid API keys."
        elif "error" in prompt_lower or "problem" in prompt_lower:
            return "This is a stub response indicating that no LLM providers are currently available. Please check your configuration and API keys."
        else:
            return f"This is a stub response (provider=local_stub) because no LLM providers are currently available. Please check your API keys and try again later.\n\nYour query was: {prompt[:100]}{'...' if len(prompt) > 100 else ''}"
    
    def is_available(self) -> bool:
        """Local stub is always available as a fallback."""
        return True
