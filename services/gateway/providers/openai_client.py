"""
OpenAI LLM Provider Client
Implements OpenAI API integration with proper error handling and retry logic.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available")

class OpenAIClient:
    """OpenAI API client with comprehensive error handling."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        self.setup_client()
    
    def setup_client(self):
        """Initialize OpenAI client."""
        if not OPENAI_AVAILABLE:
            logger.error("OpenAI library not available")
            return
        
        if not self.api_key:
            logger.error("OpenAI API key not configured")
            return
        
        try:
            self.client = openai.OpenAI(api_key=self.api_key)
            logger.info("[OK] OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None
    
    async def generate_text(
        self, 
        prompt: str, 
        max_tokens: int = 1000, 
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate text using OpenAI API."""
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI client not available",
                "content": None
            }
        
        try:
            # Select optimal model based on task complexity
            if not model:
                if len(prompt) > 1000 or max_tokens > 1000:
                    model = "gpt-4o"  # Latest GPT-4 for complex tasks
                else:
                    model = "gpt-3.5-turbo"  # Efficient for simpler tasks
            
            # Make API call with timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                ),
                timeout=15.0
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": model,
                "provider": "openai"
            }
            
        except asyncio.TimeoutError:
            logger.error("OpenAI API call timed out")
            return {
                "success": False,
                "error": "API call timed out",
                "content": None
            }
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    def is_available(self) -> bool:
        """Check if OpenAI client is available and configured."""
        return self.client is not None and self.api_key is not None
