"""
Ollama LLM Provider Client
Implements Ollama API integration with proper error handling and retry logic.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
import os
import requests

logger = logging.getLogger(__name__)

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    logger.warning("aiohttp not available, using requests fallback")

class OllamaClient:
    """Ollama API client with comprehensive error handling."""
    
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT", "30"))
        self.default_model = os.getenv("OLLAMA_DEFAULT_MODEL", "llama3")
        self.setup_client()
    
    def setup_client(self):
        """Initialize Ollama client."""
        try:
            # Test connection to Ollama
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("[OK] Ollama client initialized successfully")
            else:
                logger.warning(f"Ollama connection test failed: {response.status_code}")
        except Exception as e:
            logger.warning(f"Ollama connection test failed: {e}")
    
    def _select_model(self, prompt: str, max_tokens: int) -> str:
        """Select optimal Ollama model based on query characteristics."""
        prompt_lower = prompt.lower()
        
        # Use available DeepSeek R1 model for all tasks (it's currently the only available model)
        # DeepSeek R1 is a powerful reasoning model that can handle various tasks well
        return "deepseek-r1:8b"
    
    async def generate_text(
        self, 
        prompt: str, 
        max_tokens: int = 1000, 
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate text using Ollama API."""
        try:
            # Select optimal model based on query characteristics
            if not model:
                model = self._select_model(prompt, max_tokens)
            
            if not AIOHTTP_AVAILABLE:
                # Fallback to requests with enhanced error handling
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "options": {
                            "temperature": temperature, 
                            "num_predict": max_tokens,
                            "top_p": 0.9,
                            "top_k": 40
                        }
                    },
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "content": result.get("response", ""),
                        "model": model,
                        "provider": "ollama"
                    }
                else:
                    # Try fallback model if primary fails
                    if model != "llama3":
                        response = requests.post(
                            f"{self.base_url}/api/generate",
                            json={
                                "model": "llama3",
                                "prompt": prompt,
                                "options": {"temperature": temperature, "num_predict": max_tokens}
                            },
                            timeout=self.timeout
                        )
                        if response.status_code == 200:
                            response_text = response.json().get("response", "")
                            return {
                                "success": True,
                                "content": self._sanitize_response(response_text),
                                "model": "llama3",
                                "provider": "ollama"
                            }
            else:
                async with aiohttp.ClientSession() as session:
                    # Simple, fast payload for quick responses
                    payload = {
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": min(max_tokens, 150),  # Limit tokens for faster response
                            "stop": ["\n\n", "Human:", "Assistant:"],  # Stop tokens for cleaner responses
                            "num_ctx": 1024  # Smaller context for faster processing
                        }
                    }
                    
                    # Fast timeout for quick responses
                    timeout = aiohttp.ClientTimeout(total=15)
                    
                    async with session.post(
                        f"{self.base_url}/api/generate",
                        json=payload,
                        timeout=timeout
                    ) as response:
                        if response.status == 200:
                            try:
                                result = await response.json()
                                response_text = result.get("response", "")
                                if response_text:
                                    # Sanitize response to remove problematic characters
                                    sanitized = self._sanitize_response(response_text)
                                    return {
                                        "success": True,
                                        "content": sanitized,
                                        "model": model,
                                        "provider": "ollama"
                                    }
                                else:
                                    logger.warning(f"Ollama empty response: {result}")
                                    return {
                                        "success": False,
                                        "error": "Ollama returned empty response",
                                        "content": None
                                    }
                            except Exception as parse_error:
                                logger.error(f"Ollama JSON parse error: {parse_error}")
                                return {
                                    "success": False,
                                    "error": "Ollama JSON parse error",
                                    "content": None
                                }
                        else:
                            error_text = await response.text()
                            logger.error(f"Ollama API error {response.status}: {error_text}")
                            return {
                                "success": False,
                                "error": f"Ollama API error {response.status}: {error_text}",
                                "content": None
                            }
            
            return {
                "success": False,
                "error": "Ollama call failed",
                "content": None
            }
            
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    def _sanitize_response(self, text: str) -> str:
        """Sanitize response text to remove problematic characters."""
        if not text:
            return ""
        
        # Remove common problematic patterns
        text = text.replace("\x00", "")  # Remove null bytes
        text = text.replace("\r", "\n")  # Normalize line endings
        text = " ".join(text.split())  # Normalize whitespace
        
        return text.strip()
    
    def is_available(self) -> bool:
        """Check if Ollama client is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
