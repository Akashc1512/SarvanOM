"""
Anthropic LLM Provider Client
Implements Anthropic API integration with proper error handling and retry logic.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic library not available")

class AnthropicClient:
    """Anthropic API client with comprehensive error handling."""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        self.setup_client()
    
    def setup_client(self):
        """Initialize Anthropic client."""
        if not ANTHROPIC_AVAILABLE:
            logger.error("Anthropic library not available")
            return
        
        if not self.api_key:
            logger.error("Anthropic API key not configured")
            return
        
        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            logger.info("✅ Anthropic client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            self.client = None
    
    async def generate_text(
        self, 
        prompt: str, 
        max_tokens: int = 1000, 
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate text using Anthropic API."""
        if not self.client:
            return {
                "success": False,
                "error": "Anthropic client not available",
                "content": None
            }
        
        try:
            # Select optimal model based on task complexity
            if not model:
                if len(prompt) > 1000 or max_tokens > 1000:
                    model = "claude-3-5-sonnet-20241022"  # Latest Claude 3.5 Sonnet for complex tasks
                else:
                    model = "claude-3-5-haiku-20241022"   # Latest Claude 3.5 Haiku for efficient tasks
            
            # Make API call with timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.messages.create,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}]
                ),
                timeout=15.0
            )
            
            return {
                "success": True,
                "content": response.content[0].text,
                "model": model,
                "provider": "anthropic"
            }
            
        except asyncio.TimeoutError:
            logger.error("Anthropic API call timed out")
            return {
                "success": False,
                "error": "API call timed out",
                "content": None
            }
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    def is_available(self) -> bool:
        """Check if Anthropic client is available and configured."""
        return self.client is not None and self.api_key is not None
