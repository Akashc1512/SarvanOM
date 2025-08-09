from shared.core.api.config import get_settings

settings = get_settings()
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
from typing import Optional

# Import the new v3 client
from .llm_client_v3 import (
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
        self._model = settings.openai_model or "gpt-3.5-turbo"

        # Set up the model based on provider
        if self._provider == "anthropic":
            self._model = settings.anthropic_model or "claude-3-5-sonnet-20241022"

        logger.info(
            f"✅ LLM Client configured - Provider: {self._provider}, Model: {self._model}"
        )

        # SANITY CHECK: Validate API keys with detailed error surface
        logger.info("🔍 DEEP DEBUG: Validating API keys")
        if self._provider == "openai":
            api_key = settings.openai_api_key
            if not api_key:
                logger.error("❌ OPENAI_API_KEY not found in environment")
                raise Exception("OPENAI_API_KEY is required but not set")
            elif len(api_key) < 20:  # Basic validation
                logger.error("❌ OPENAI_API_KEY appears to be invalid (too short)")
                raise Exception("OPENAI_API_KEY appears to be invalid")
            logger.info("✅ OPENAI_API_KEY found and validated")
        elif self._provider == "anthropic":
            api_key = settings.anthropic_api_key
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
        return await self.synthesize(prompt, max_tokens, temperature)

    async def synthesize(
        self, prompt: str, max_tokens: int = 500, temperature: float = 0.2
    ) -> str:
        """
        Synthesize text using the configured LLM provider.
        """
        try:
            # Create LLMRequest object for the v3 client
            request = LLMRequest(
                prompt=prompt, max_tokens=max_tokens, temperature=temperature
            )
            response = await self._client.generate_text(request)
            return response.content
        except Exception as e:
            logger.error(f"❌ LLM synthesis failed: {e}")
            raise Exception(f"LLM API call failed: {str(e)}")

    async def create_embedding(self, text: str):
        """
        Create embeddings using the configured provider.
        """
        try:
            return await self._client.create_embedding(text)
        except Exception as e:
            logger.error(f"❌ LLM embedding creation failed: {e}")
            raise Exception(f"LLM API call failed: {str(e)}")

    def get_embedding(self, text: str):
        """
        Alias for create_embedding for backward compatibility.
        """
        return self.create_embedding(text)

    # Synchronous wrappers for backward compatibility
    def generate_text_sync(
        self, prompt: str, max_tokens: int = 500, temperature: float = 0.2
    ) -> str:
        """
        Synchronous wrapper for generate_text - use only when async is not available.
        """
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context, use asyncio.create_task
            task = asyncio.create_task(
                self.generate_text(prompt, max_tokens, temperature)
            )
            # This won't work in async context, so we need a different approach
            raise RuntimeError(
                "Cannot use sync method in async context. Use generate_text() instead."
            )
        except RuntimeError:
            # No running loop, we can create one
            return asyncio.run(self.generate_text(prompt, max_tokens, temperature))

    def synthesize_sync(
        self, prompt: str, max_tokens: int = 500, temperature: float = 0.2
    ) -> str:
        """
        Synchronous wrapper for synthesize - use only when async is not available.
        """
        try:
            loop = asyncio.get_running_loop()
            raise RuntimeError(
                "Cannot use sync method in async context. Use synthesize() instead."
            )
        except RuntimeError:
            # No running loop, we can create one
            return asyncio.run(self.synthesize(prompt, max_tokens, temperature))

    def create_embedding_sync(self, text: str):
        """
        Synchronous wrapper for create_embedding - use only when async is not available.
        """
        try:
            loop = asyncio.get_running_loop()
            raise RuntimeError(
                "Cannot use sync method in async context. Use create_embedding() instead."
            )
        except RuntimeError:
            # No running loop, we can create one
            return asyncio.run(self.create_embedding(text))


# Global instance for backward compatibility
_legacy_client: Optional[LLMClient] = None


def get_legacy_llm_client() -> LLMClient:
    """Get a legacy LLM client instance."""
    return LLMClient()


def get_llm_client() -> LLMClient:
    """Get an LLM client instance (alias for get_legacy_llm_client for compatibility)."""
    return get_legacy_llm_client()
