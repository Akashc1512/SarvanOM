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
        self._client = get_llm_client_v3()
        self._provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self._model = os.getenv("OPENAI_LLM_MODEL", "gpt-3.5-turbo")

        # Set up the model based on provider
        if self._provider == "anthropic":
            self._model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

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

    def generate_text(
        self, prompt: str, max_tokens: int = 500, temperature: float = 0.2
    ) -> str:
        """
        Generate text using the configured LLM provider.
        This is the main method agents should use.
        """
        return self.synthesize(prompt, max_tokens, temperature)

    def synthesize(
        self, prompt: str, max_tokens: int = 500, temperature: float = 0.2
    ) -> str:
        """
        Synthesize text using the configured LLM provider.
        """
        # Create async event loop if not exists
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Run the async operation
        request = LLMRequest(
            prompt=prompt, max_tokens=max_tokens, temperature=temperature
        )

        async def _synthesize():
            response = await self._client.generate_text(request)
            return response.content

        return loop.run_until_complete(_synthesize())

    def create_embedding(self, text: str):
        """
        Create embeddings using the configured provider.
        """
        # Create async event loop if not exists
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Run the async operation
        async def _create_embedding():
            return await self._client.create_embedding(text)

        return loop.run_until_complete(_create_embedding())

    def get_embedding(self, text: str):
        """
        Alias for create_embedding for backward compatibility.
        """
        return self.create_embedding(text)


# Global instance for backward compatibility
_legacy_client: Optional[LLMClient] = None


def get_legacy_llm_client() -> LLMClient:
    """Get global legacy LLM client instance."""
    global _legacy_client

    if _legacy_client is None:
        _legacy_client = LLMClient()

    return _legacy_client
