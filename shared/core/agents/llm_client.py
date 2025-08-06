
"""
LLMClient: Legacy wrapper for backward compatibility.
This module provides backward compatibility with the old LLM client interface.
For new code, use shared.core.llm_client_v3 instead.

Authors:
- Universal Knowledge Platform Engineering Team

Version:
    1.0.0 (2024-12-28)
"""

import os
import logging
import asyncio
import concurrent.futures
from typing import Optional

# Import the v3 client
from shared.core.llm_client_v3 import (
    EnhancedLLMClientV3,
    LLMConfig,
    LLMRequest,
    LLMProvider,
    get_llm_client_v3,
)

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Legacy LLM client wrapper for backward compatibility.

    This class provides the same interface as the old LLMClient but uses
    the new EnhancedLLMClientV3 under the hood.
    """

    def __init__(self):
        """Initialize the legacy LLM client."""
        logger.info("🔍 DEEP DEBUG: Initializing LLM Client")
        
        try:
            self._client = get_llm_client_v3()
            logger.info("✅ LLM Client v3 initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM Client v3: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise Exception(f"LLM Client v3 initialization failed: {str(e)}")
        
        self._provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self._model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

        # Set up the model based on provider
        if self._provider == "anthropic":
            self._model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

        logger.info(f"✅ LLM Client configured - Provider: {self._provider}, Model: {self._model}")
        
        # SANITY CHECK: Validate API keys with detailed error surface
        logger.info("🔍 DEEP DEBUG: Validating API keys")
        if self._provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error("❌ OPENAI_API_KEY not found in environment")
                raise Exception("OPENAI_API_KEY is required but not set")
            elif len(api_key) < 20:  # Basic validation
                logger.error("❌ OPENAI_API_KEY appears to be invalid (too short)")
                raise Exception("OPENAI_API_KEY appears to be invalid")
            logger.info("✅ OPENAI_API_KEY found and validated")
        elif self._provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                logger.error("❌ ANTHROPIC_API_KEY not found in environment")
                raise Exception("ANTHROPIC_API_KEY is required but not set")
            elif len(api_key) < 20:  # Basic validation
                logger.error("❌ ANTHROPIC_API_KEY appears to be invalid (too short)")
                raise Exception("ANTHROPIC_API_KEY appears to be invalid")
            logger.info("✅ ANTHROPIC_API_KEY found and validated")
        
        logger.info("✅ LLM Client initialization completed successfully")

    def get_provider(self):
        """Get the current provider."""
        return self._provider

    def get_model(self):
        """Get the current model."""
        return self._model

    def get_llm_name(self):
        """Get the LLM name."""
        if self._provider == "openai":
            return f"openai:{self._model}"
        elif self._provider == "anthropic":
            return f"anthropic:{self._model}"
        return "unknown"

    async def generate_text(
        self, prompt: str, max_tokens: int = 500, temperature: float = 0.2
    ) -> str:
        """
        Generate text using the configured LLM provider.
        This is the main method agents should use.
        """
        logger.info(f"🔍 DEEP DEBUG: Generating text with {self._provider}")
        logger.info(f"Prompt length: {len(prompt)} characters")
        logger.info(f"Max tokens: {max_tokens}, Temperature: {temperature}")
        
        try:
            result = await self.synthesize(prompt, max_tokens, temperature)
            logger.info(f"✅ Text generation successful, response length: {len(result)}")
            return result
        except Exception as e:
            logger.error(f"❌ Text generation failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Provider: {self._provider}, Model: {self._model}")
            
            # Surface specific API errors with actionable messages
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ["authentication", "unauthorized", "invalid api key"]):
                raise Exception(f"LLM API authentication failed. Please check your {self._provider.upper()}_API_KEY: {str(e)}")
            elif any(keyword in error_str for keyword in ["quota", "rate limit", "too many requests"]):
                raise Exception(f"LLM API quota exceeded or rate limited. Please try again later: {str(e)}")
            elif any(keyword in error_str for keyword in ["model", "not found", "invalid model"]):
                raise Exception(f"LLM model '{self._model}' not found or invalid. Please check your model configuration: {str(e)}")
            elif any(keyword in error_str for keyword in ["timeout", "connection", "network"]):
                raise Exception(f"LLM API network error. Please check your internet connection: {str(e)}")
            elif any(keyword in error_str for keyword in ["billing", "payment", "account"]):
                raise Exception(f"LLM API billing issue. Please check your account status: {str(e)}")
            else:
                raise Exception(f"LLM API call failed: {str(e)}")

    async def synthesize(self, prompt: str, max_tokens: int = 500, temperature: float = 0.2) -> str:
        """Synthesize text using the LLM client."""
        try:
            return await self._client.generate_text(prompt, max_tokens, temperature)
        except Exception as e:
            logger.error(f"LLM synthesis failed: {e}")
            raise Exception(f"LLM API call failed: {str(e)}")

    async def create_embedding(self, text: str):
        """
        Create embeddings using the configured provider.
        """
        try:
            return await self._client.create_embedding(text)
        except Exception as e:
            logger.error(f"LLM embedding creation failed: {e}")
            raise Exception(f"LLM embedding API call failed: {str(e)}")

    async def get_embedding(self, text: str):
        """
        Alias for create_embedding for backward compatibility.
        """
        return await self.create_embedding(text)


# Global instance for backward compatibility
_legacy_client: Optional[LLMClient] = None


def get_legacy_llm_client() -> LLMClient:
    """Get global legacy LLM client instance."""
    global _legacy_client

    if _legacy_client is None:
        _legacy_client = LLMClient()

    return _legacy_client
