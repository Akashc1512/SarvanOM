from shared.core.api.config import get_settings

settings = get_settings()
"""
Dynamic LLM Client - Universal Knowledge Platform
Enhanced LLM client with intelligent model selection based on query classification.

This module provides dynamic LLM provider selection based on query complexity and type,
optimizing for cost, performance, and quality based on the specific query requirements.

Key Features:
- **Dynamic Model Selection**: Automatically selects the best provider based on query classification
- **Query Classification Integration**: Uses QueryClassifier to determine optimal provider
- **Multi-Provider Support**: Ollama (local), HuggingFace (free API), OpenAI (fallback)
- **Intelligent Fallback**: Automatic retry with different providers on failure
- **Cost Optimization**: Prioritizes free/local providers for simple queries
- **Performance Monitoring**: Tracks response times and success rates
- **Comprehensive Logging**: Detailed logging for transparency and debugging

Provider Selection Logic:
- "simple_factual" → Ollama local models (llama2, mistral)
- "research_synthesis" → HuggingFace Inference API (free tier)
- "complex_reasoning" or fallback → OpenAI GPT-3.5 (free tier)

Environment Variables:
- OLLAMA_BASE_URL: Ollama server URL (default: http://localhost:11434)
- HUGGINGFACE_API_KEY: HuggingFace API key for free tier
- OPENAI_API_KEY: OpenAI API key for fallback
- MEILI_MASTER_KEY: Meilisearch master key (for context retrieval)

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
License: MIT
"""

import asyncio
import logging
import time
import os
import json
import aiohttp
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = structlog.get_logger(__name__)


class QueryType(str, Enum):
    """Query types for dynamic model selection."""

    SIMPLE_FACTUAL = "simple_factual"
    RESEARCH_SYNTHESIS = "research_synthesis"
    COMPLEX_REASONING = "complex_reasoning"
    UNKNOWN = "unknown"


class LLMProvider(str, Enum):
    """Supported LLM providers for dynamic selection."""

    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    OPENAI = "openai"


@dataclass
class LLMRequest:
    """LLM request structure."""

    query: str
    context: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.2
    system_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """LLM response structure."""

    content: str
    provider: LLMProvider
    model: str
    response_time_ms: float
    token_usage: Optional[Dict[str, int]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderConfig:
    """Configuration for each LLM provider."""

    name: LLMProvider
    base_url: str
    api_key: Optional[str] = None
    models: List[str] = field(default_factory=list)
    timeout: int = 30
    max_retries: int = 3
    is_available: bool = True


class LLMProviderInterface(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text using the provider."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is available."""
        pass

    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information."""
        pass


class OllamaProvider(LLMProviderInterface):
    """Ollama local LLM provider."""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.session = None
        self.default_model = "llama2:7b"

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session

    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text using Ollama."""
        start_time = time.time()
        session = await self._get_session()

        # Prepare the prompt
        prompt = request.query
        if request.context:
            prompt = f"Context: {request.context}\n\nQuery: {request.query}"
        if request.system_message:
            prompt = f"System: {request.system_message}\n\n{prompt}"

        # Prepare request payload
        payload = {
            "model": self.default_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            },
        }

        try:
            async with session.post(
                f"{self.config.base_url}/api/generate",
                json=payload,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result.get("response", "")

                    return LLMResponse(
                        content=content,
                        provider=LLMProvider.OLLAMA,
                        model=self.default_model,
                        response_time_ms=(time.time() - start_time) * 1000,
                        metadata={
                            "ollama_response": result,
                            "prompt_tokens": len(prompt.split()),
                            "response_tokens": len(content.split()),
                        },
                    )
                else:
                    error_text = await response.text()
                    raise Exception(
                        f"Ollama API error: {response.status} - {error_text}"
                    )

        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if Ollama is available."""
        try:
            session = await self._get_session()
            async with session.get(f"{self.config.base_url}/api/tags") as response:
                return response.status == 200
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False

    def get_provider_info(self) -> Dict[str, Any]:
        """Get Ollama provider information."""
        return {
            "provider": "ollama",
            "base_url": self.config.base_url,
            "default_model": self.default_model,
            "is_local": True,
            "cost_per_token": 0.0,
        }


class HuggingFaceProvider(LLMProviderInterface):
    """HuggingFace Inference API provider."""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.session = None
        self.default_model = "microsoft/DialoGPT-medium"

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session

    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text using HuggingFace Inference API."""
        start_time = time.time()
        session = await self._get_session()

        # Prepare the prompt
        prompt = request.query
        if request.context:
            prompt = f"Context: {request.context}\n\nQuery: {request.query}"

        # Prepare request payload
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": request.max_tokens,
                "temperature": request.temperature,
                "do_sample": True,
                "return_full_text": False,
            },
        }

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with session.post(
                f"https://api-inference.huggingface.co/models/{self.default_model}",
                json=payload,
                headers=headers,
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = (
                        result[0].get("generated_text", "")
                        if isinstance(result, list)
                        else result.get("generated_text", "")
                    )

                    return LLMResponse(
                        content=content,
                        provider=LLMProvider.HUGGINGFACE,
                        model=self.default_model,
                        response_time_ms=(time.time() - start_time) * 1000,
                        metadata={
                            "huggingface_response": result,
                            "prompt_tokens": len(prompt.split()),
                            "response_tokens": len(content.split()),
                        },
                    )
                else:
                    error_text = await response.text()
                    raise Exception(
                        f"HuggingFace API error: {response.status} - {error_text}"
                    )

        except Exception as e:
            logger.error(f"HuggingFace generation failed: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if HuggingFace is available."""
        try:
            session = await self._get_session()
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            async with session.get(
                "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
            ) as response:
                return response.status in [
                    200,
                    404,
                ]  # 404 means model not loaded but API is working
        except Exception as e:
            logger.warning(f"HuggingFace health check failed: {e}")
            return False

    def get_provider_info(self) -> Dict[str, Any]:
        """Get HuggingFace provider information."""
        return {
            "provider": "huggingface",
            "base_url": "https://api-inference.huggingface.co",
            "default_model": self.default_model,
            "is_local": False,
            "cost_per_token": 0.0,  # Free tier
        }


class OpenAIProvider(LLMProviderInterface):
    """OpenAI API provider."""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.session = None
        self.default_model = "gpt-3.5-turbo"

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session

    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text using OpenAI API."""
        start_time = time.time()
        session = await self._get_session()

        # Prepare messages
        messages = []
        if request.system_message:
            messages.append({"role": "system", "content": request.system_message})
        messages.append({"role": "user", "content": request.query})

        # Prepare request payload
        payload = {
            "model": self.default_model,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
        }

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers,
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    usage = result.get("usage", {})

                    return LLMResponse(
                        content=content,
                        provider=LLMProvider.OPENAI,
                        model=self.default_model,
                        response_time_ms=(time.time() - start_time) * 1000,
                        token_usage=usage,
                        metadata={
                            "openai_response": result,
                            "finish_reason": result["choices"][0].get(
                                "finish_reason", "unknown"
                            ),
                        },
                    )
                else:
                    error_text = await response.text()
                    raise Exception(
                        f"OpenAI API error: {response.status} - {error_text}"
                    )

        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if OpenAI is available."""
        try:
            session = await self._get_session()
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "test"}],
            }
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers,
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {e}")
            return False

    def get_provider_info(self) -> Dict[str, Any]:
        """Get OpenAI provider information."""
        return {
            "provider": "openai",
            "base_url": "https://api.openai.com/v1",
            "default_model": self.default_model,
            "is_local": False,
            "cost_per_token": 0.002,  # Approximate cost per 1K tokens
        }


class DynamicLLMClient:
    """
    Enhanced LLM client with dynamic model selection based on query classification.

    This client automatically selects the best LLM provider based on query complexity
    and type, optimizing for cost, performance, and quality.
    """

    def __init__(self):
        """Initialize the dynamic LLM client."""
        logger.info("🔍 Initializing Dynamic LLM Client...")

        # Initialize providers
        self.providers = {}
        self._setup_providers()

        # Initialize query classifier
        try:
            from shared.core.query_classifier import QueryClassifier

            self.query_classifier = QueryClassifier()
            logger.info("✅ QueryClassifier initialized successfully")
        except ImportError as e:
            logger.warning(f"⚠️ QueryClassifier not available: {e}")
            self.query_classifier = None

        # Performance tracking
        self.provider_stats = {
            LLMProvider.OLLAMA: {"calls": 0, "success": 0, "avg_time": 0},
            LLMProvider.HUGGINGFACE: {"calls": 0, "success": 0, "avg_time": 0},
            LLMProvider.OPENAI: {"calls": 0, "success": 0, "avg_time": 0},
        }

        logger.info("✅ Dynamic LLM Client initialized successfully")

    def _setup_providers(self):
        """Setup available LLM providers."""
        # Setup Ollama provider
        from shared.core.config.central_config import get_ollama_url

        ollama_url = settings.ollama_base_url or get_ollama_url()
        self.providers[LLMProvider.OLLAMA] = OllamaProvider(
            ProviderConfig(
                name=LLMProvider.OLLAMA,
                base_url=ollama_url,
                models=["llama2:7b", "mistral:7b", "codellama:7b"],
            )
        )
        logger.info(f"✅ Ollama provider configured: {ollama_url}")

        # Setup HuggingFace provider
        hf_api_key = settings.huggingface_api_key
        if hf_api_key:
            self.providers[LLMProvider.HUGGINGFACE] = HuggingFaceProvider(
                ProviderConfig(
                    name=LLMProvider.HUGGINGFACE,
                    base_url="https://api-inference.huggingface.co",
                    api_key=hf_api_key,
                    models=["microsoft/DialoGPT-medium", "distilgpt2"],
                )
            )
            logger.info("✅ HuggingFace provider configured")
        else:
            logger.warning(
                "⚠️ HUGGINGFACE_API_KEY not found, HuggingFace provider disabled"
            )

        # Setup OpenAI provider
        openai_api_key = settings.openai_api_key
        if openai_api_key:
            self.providers[LLMProvider.OPENAI] = OpenAIProvider(
                ProviderConfig(
                    name=LLMProvider.OPENAI,
                    base_url="https://api.openai.com/v1",
                    api_key=openai_api_key,
                    models=["gpt-3.5-turbo", "gpt-4"],
                )
            )
            logger.info("✅ OpenAI provider configured")
        else:
            logger.warning("⚠️ OPENAI_API_KEY not found, OpenAI provider disabled")

    async def _classify_query(self, query: str) -> QueryType:
        """Classify the query to determine the best provider."""
        if not self.query_classifier:
            # Fallback classification based on simple heuristics
            query_lower = query.lower()
            if any(
                word in query_lower
                for word in ["what is", "who is", "when", "where", "how many", "define"]
            ):
                return QueryType.SIMPLE_FACTUAL
            elif any(
                word in query_lower
                for word in ["analyze", "compare", "research", "study", "investigate"]
            ):
                return QueryType.RESEARCH_SYNTHESIS
            else:
                return QueryType.COMPLEX_REASONING

        try:
            classification = await self.query_classifier.classify_query(query)

            # Map classification to query type
            if classification.category.value in ["general_factual", "procedural"]:
                return QueryType.SIMPLE_FACTUAL
            elif classification.category.value in [
                "analytical",
                "comparative",
                "research_synthesis",
            ]:
                return QueryType.RESEARCH_SYNTHESIS
            else:
                return QueryType.COMPLEX_REASONING

        except Exception as e:
            logger.warning(f"Query classification failed: {e}, using fallback")
            return QueryType.COMPLEX_REASONING

    def _select_provider(self, query_type: QueryType) -> LLMProvider:
        """Select the best provider based on query type."""
        if query_type == QueryType.SIMPLE_FACTUAL:
            # Try Ollama first (local, free)
            if LLMProvider.OLLAMA in self.providers:
                return LLMProvider.OLLAMA
            # Fallback to HuggingFace (free API)
            elif LLMProvider.HUGGINGFACE in self.providers:
                return LLMProvider.HUGGINGFACE
            # Final fallback to OpenAI
            elif LLMProvider.OPENAI in self.providers:
                return LLMProvider.OPENAI

        elif query_type == QueryType.RESEARCH_SYNTHESIS:
            # Try HuggingFace first (free API, good for research)
            if LLMProvider.HUGGINGFACE in self.providers:
                return LLMProvider.HUGGINGFACE
            # Fallback to OpenAI
            elif LLMProvider.OPENAI in self.providers:
                return LLMProvider.OPENAI
            # Final fallback to Ollama
            elif LLMProvider.OLLAMA in self.providers:
                return LLMProvider.OLLAMA

        else:  # COMPLEX_REASONING or UNKNOWN
            # Try OpenAI first (best for complex reasoning)
            if LLMProvider.OPENAI in self.providers:
                return LLMProvider.OPENAI
            # Fallback to HuggingFace
            elif LLMProvider.HUGGINGFACE in self.providers:
                return LLMProvider.HUGGINGFACE
            # Final fallback to Ollama
            elif LLMProvider.OLLAMA in self.providers:
                return LLMProvider.OLLAMA

        # If no providers available, raise error
        raise Exception("No LLM providers available")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def dispatch(
        self, query: str, context: Optional[str] = None, **kwargs
    ) -> LLMResponse:
        """
        Dispatch a query to the best LLM provider based on classification.

        Args:
            query: The user query
            context: Optional context information
            **kwargs: Additional parameters for the request

        Returns:
            LLMResponse: The generated response
        """
        start_time = time.time()

        # Classify the query
        query_type = await self._classify_query(query)
        logger.info(f"🔍 Query classified as: {query_type.value}")

        # Select the best provider
        selected_provider = self._select_provider(query_type)
        logger.info(f"🎯 Selected provider: {selected_provider.value}")

        # Create request
        request = LLMRequest(
            query=query,
            context=context,
            max_tokens=kwargs.get("max_tokens", 1000),
            temperature=kwargs.get("temperature", 0.2),
            system_message=kwargs.get("system_message"),
            metadata=kwargs.get("metadata", {}),
        )

        # Try the selected provider
        try:
            provider = self.providers[selected_provider]

            # Check if provider is healthy
            if not await provider.health_check():
                logger.warning(
                    f"⚠️ Provider {selected_provider.value} is not healthy, trying fallback"
                )
                raise Exception(
                    f"Provider {selected_provider.value} health check failed"
                )

            # Generate response
            response = await provider.generate_text(request)

            # Update statistics
            self.provider_stats[selected_provider]["calls"] += 1
            self.provider_stats[selected_provider]["success"] += 1
            self.provider_stats[selected_provider]["avg_time"] = (
                self.provider_stats[selected_provider]["avg_time"]
                * (self.provider_stats[selected_provider]["calls"] - 1)
                + response.response_time_ms
            ) / self.provider_stats[selected_provider]["calls"]

            # Log success
            logger.info(
                f"✅ Generated response using {selected_provider.value} in {response.response_time_ms:.2f}ms"
            )

            return response

        except Exception as e:
            logger.warning(f"❌ Provider {selected_provider.value} failed: {e}")

            # Update statistics
            self.provider_stats[selected_provider]["calls"] += 1

            # Try fallback providers
            fallback_providers = [
                p for p in self.providers.keys() if p != selected_provider
            ]

            for fallback_provider in fallback_providers:
                try:
                    logger.info(
                        f"🔄 Trying fallback provider: {fallback_provider.value}"
                    )

                    provider = self.providers[fallback_provider]

                    # Check if provider is healthy
                    if not await provider.health_check():
                        logger.warning(
                            f"⚠️ Fallback provider {fallback_provider.value} is not healthy"
                        )
                        continue

                    # Generate response
                    response = await provider.generate_text(request)

                    # Update statistics
                    self.provider_stats[fallback_provider]["calls"] += 1
                    self.provider_stats[fallback_provider]["success"] += 1
                    self.provider_stats[fallback_provider]["avg_time"] = (
                        self.provider_stats[fallback_provider]["avg_time"]
                        * (self.provider_stats[fallback_provider]["calls"] - 1)
                        + response.response_time_ms
                    ) / self.provider_stats[fallback_provider]["calls"]

                    # Log success
                    logger.info(
                        f"✅ Generated response using fallback {fallback_provider.value} in {response.response_time_ms:.2f}ms"
                    )

                    return response

                except Exception as fallback_error:
                    logger.warning(
                        f"❌ Fallback provider {fallback_provider.value} failed: {fallback_error}"
                    )
                    self.provider_stats[fallback_provider]["calls"] += 1
                    continue

            # If all providers failed, raise the original error
            raise Exception(f"All LLM providers failed. Original error: {e}")

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using dynamic provider selection."""
        response = await self.dispatch(prompt, **kwargs)
        return response.content

    def get_provider_stats(self) -> Dict[str, Any]:
        """Get provider statistics."""
        return {
            "provider_stats": self.provider_stats,
            "available_providers": list(self.providers.keys()),
            "total_calls": sum(
                stats["calls"] for stats in self.provider_stats.values()
            ),
            "total_success": sum(
                stats["success"] for stats in self.provider_stats.values()
            ),
        }

    async def health_check(self) -> Dict[str, Any]:
        """Check health of all providers."""
        health_status = {}

        for provider_name, provider in self.providers.items():
            try:
                is_healthy = await provider.health_check()
                health_status[provider_name.value] = {
                    "healthy": is_healthy,
                    "info": provider.get_provider_info(),
                }
            except Exception as e:
                health_status[provider_name.value] = {"healthy": False, "error": str(e)}

        return health_status


# Global instance
_dynamic_llm_client = None


def get_dynamic_llm_client() -> DynamicLLMClient:
    """Get the global dynamic LLM client instance."""
    global _dynamic_llm_client
    if _dynamic_llm_client is None:
        _dynamic_llm_client = DynamicLLMClient()
    return _dynamic_llm_client


async def dispatch_query(
    query: str, context: Optional[str] = None, **kwargs
) -> LLMResponse:
    """Convenience function to dispatch a query."""
    client = get_dynamic_llm_client()
    return await client.dispatch(query, context, **kwargs)


async def generate_text(prompt: str, **kwargs) -> str:
    """Convenience function to generate text."""
    client = get_dynamic_llm_client()
    return await client.generate_text(prompt, **kwargs)
