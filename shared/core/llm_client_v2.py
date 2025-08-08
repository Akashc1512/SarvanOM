from shared.core.api.config import get_settings
settings = get_settings()
"""
Enhanced LLM Client - MAANG Standards
Robust LLM integration with fallback mechanisms and comprehensive logging.

Features:
- Multiple provider support (OpenAI, Anthropic, Azure, Google)
- Automatic fallback between providers
- Comprehensive error handling and retry logic
- Token usage tracking
- Performance monitoring
- Rate limiting integration
- Prompt template management
- Streaming support

Authors:
- Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import asyncio
import logging
import time
import os
import json
from typing import Dict, Any, List, Optional, Union, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = structlog.get_logger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    GOOGLE = "google"
    OLLAMA = "ollama"  # Local models
    MOCK = "mock"  # For testing


class LLMModel(str, Enum):
    """Supported LLM models."""

    # OpenAI models
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_3_5_TURBO = "gpt-3.5-turbo"

    # Anthropic models
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"

    # Azure models
    AZURE_GPT_4 = "gpt-4"
    AZURE_GPT_35 = "gpt-35-turbo"

    # Google models
    GEMINI_PRO = "gemini-pro"
    GEMINI_PRO_VISION = "gemini-pro-vision"


@dataclass
class LLMConfig:
    """LLM configuration."""

    provider: LLMProvider
    model: str
    api_key: str
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    temperature: float = 0.2
    max_tokens: int = 1000

    # Advanced settings
    enable_streaming: bool = False
    enable_fallback: bool = True
    enable_logging: bool = True
    enable_metrics: bool = True


@dataclass
class LLMRequest:
    """LLM request structure."""

    prompt: str
    system_message: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """LLM response structure."""

    content: str
    provider: LLMProvider
    model: str
    token_usage: Dict[str, int]
    finish_reason: str
    response_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMError:
    """LLM error structure."""

    error_type: str
    message: str
    provider: LLMProvider
    model: str
    retryable: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class LLMProviderInterface(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text using the provider."""
        pass

    @abstractmethod
    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Generate streaming text using the provider."""
        pass

    @abstractmethod
    async def create_embedding(self, text: str) -> List[float]:
        """Create embeddings using the provider."""
        pass

    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information."""
        pass


class OpenAIProvider(LLMProviderInterface):
    """OpenAI provider implementation."""

    def __init__(self, config: LLMConfig):
        self.config = config
        import openai

        self.client = openai.AsyncOpenAI(
            api_key=config.api_key, base_url=config.base_url, timeout=config.timeout
        )

    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text using OpenAI."""
        start_time = time.time()

        try:
            messages = []
            if request.system_message:
                messages.append({"role": "system", "content": request.system_message})
            messages.append({"role": "user", "content": request.prompt})

            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=request.temperature or self.config.temperature,
                max_tokens=request.max_tokens or self.config.max_tokens,
                stream=request.stream,
            )

            response_time = (time.time() - start_time) * 1000

            return LLMResponse(
                content=response.choices[0].message.content,
                provider=LLMProvider.OPENAI,
                model=self.config.model,
                token_usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                finish_reason=response.choices[0].finish_reason,
                response_time_ms=response_time,
                metadata={"request_id": response.id},
            )

        except Exception as e:
            raise LLMError(
                error_type="openai_error",
                message=str(e),
                provider=LLMProvider.OPENAI,
                model=self.config.model,
                retryable=True,
            )

    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Generate streaming text using OpenAI."""
        try:
            messages = []
            if request.system_message:
                messages.append({"role": "system", "content": request.system_message})
            messages.append({"role": "user", "content": request.prompt})

            stream = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=request.temperature or self.config.temperature,
                max_tokens=request.max_tokens or self.config.max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise LLMError(
                error_type="openai_stream_error",
                message=str(e),
                provider=LLMProvider.OPENAI,
                model=self.config.model,
                retryable=True,
            )

    async def create_embedding(self, text: str) -> List[float]:
        """Create embeddings using OpenAI."""
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-small", input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise LLMError(
                error_type="openai_embedding_error",
                message=str(e),
                provider=LLMProvider.OPENAI,
                model="text-embedding-3-small",
                retryable=True,
            )

    def get_provider_info(self) -> Dict[str, Any]:
        """Get OpenAI provider information."""
        return {
            "provider": LLMProvider.OPENAI.value,
            "model": self.config.model,
            "base_url": self.config.base_url,
        }


class AnthropicProvider(LLMProviderInterface):
    """Anthropic provider implementation."""

    def __init__(self, config: LLMConfig):
        self.config = config
        import anthropic

        self.client = anthropic.AsyncAnthropic(api_key=config.api_key)

    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text using Anthropic."""
        start_time = time.time()

        try:
            messages = []
            if request.system_message:
                messages.append({"role": "system", "content": request.system_message})
            messages.append({"role": "user", "content": request.prompt})

            response = await self.client.messages.create(
                model=self.config.model,
                max_tokens=request.max_tokens or self.config.max_tokens,
                temperature=request.temperature or self.config.temperature,
                messages=messages,
            )

            response_time = (time.time() - start_time) * 1000

            return LLMResponse(
                content=response.content[0].text if response.content else "",
                provider=LLMProvider.ANTHROPIC,
                model=self.config.model,
                token_usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                finish_reason=response.stop_reason,
                response_time_ms=response_time,
                metadata={"request_id": response.id},
            )

        except Exception as e:
            raise LLMError(
                error_type="anthropic_error",
                message=str(e),
                provider=LLMProvider.ANTHROPIC,
                model=self.config.model,
                retryable=True,
            )

    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Generate streaming text using Anthropic."""
        try:
            messages = []
            if request.system_message:
                messages.append({"role": "system", "content": request.system_message})
            messages.append({"role": "user", "content": request.prompt})

            stream = await self.client.messages.create(
                model=self.config.model,
                max_tokens=request.max_tokens or self.config.max_tokens,
                temperature=request.temperature or self.config.temperature,
                messages=messages,
                stream=True,
            )

            async for chunk in stream:
                if chunk.type == "content_block_delta":
                    yield chunk.delta.text

        except Exception as e:
            raise LLMError(
                error_type="anthropic_stream_error",
                message=str(e),
                provider=LLMProvider.ANTHROPIC,
                model=self.config.model,
                retryable=True,
            )

    async def create_embedding(self, text: str) -> List[float]:
        """Create embeddings using Anthropic."""
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3", input=text
            )
            return response.embedding
        except Exception as e:
            raise LLMError(
                error_type="anthropic_embedding_error",
                message=str(e),
                provider=LLMProvider.ANTHROPIC,
                model="text-embedding-3",
                retryable=True,
            )

    def get_provider_info(self) -> Dict[str, Any]:
        """Get Anthropic provider information."""
        return {"provider": LLMProvider.ANTHROPIC.value, "model": self.config.model}


class OllamaProvider(LLMProviderInterface):
    """Ollama local LLM provider."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.session = None
        self.default_model = "llama3.2:3b"

    async def _get_session(self):
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            import aiohttp
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session

    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text using Ollama."""
        start_time = time.time()
        session = await self._get_session()

        # Prepare the prompt
        prompt = request.prompt
        if request.system_message:
            prompt = f"System: {request.system_message}\n\n{prompt}"

        # Prepare request payload
        payload = {
            "model": self.default_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": request.temperature or self.config.temperature,
                "num_predict": request.max_tokens or self.config.max_tokens
            }
        }

        try:
            async with session.post(
                f"{self.config.base_url}/api/generate",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    raise Exception(f"Ollama API error: {response.status}")

                result = await response.json()
                content = result.get("response", "")

                response_time = (time.time() - start_time) * 1000

                return LLMResponse(
                    content=content,
                    provider=LLMProvider.OLLAMA,
                    model=self.default_model,
                    token_usage={
                        "prompt_tokens": len(prompt.split()),
                        "completion_tokens": len(content.split()),
                        "total_tokens": len(prompt.split()) + len(content.split()),
                    },
                    finish_reason="stop",
                    response_time_ms=response_time,
                    metadata={"ollama_response": result},
                )

        except Exception as e:
            # Ensure the exception is properly derived from BaseException
            error_message = str(e) if e else "Unknown Ollama error"
            raise LLMError(
                error_type="ollama_error",
                message=error_message,
                provider=LLMProvider.OLLAMA,
                model=self.default_model,
                retryable=True,
            )

    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Generate streaming text using Ollama."""
        session = await self._get_session()

        # Prepare the prompt
        prompt = request.prompt
        if request.system_message:
            prompt = f"System: {request.system_message}\n\n{prompt}"

        # Prepare request payload
        payload = {
            "model": self.default_model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": request.temperature or self.config.temperature,
                "num_predict": request.max_tokens or self.config.max_tokens
            }
        }

        try:
            async with session.post(
                f"{self.config.base_url}/api/generate",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    raise Exception(f"Ollama API error: {response.status}")

                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line.decode())
                            if "response" in data:
                                yield data["response"]
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            # Ensure the exception is properly derived from BaseException
            error_message = str(e) if e else "Unknown Ollama streaming error"
            raise LLMError(
                error_type="ollama_stream_error",
                message=error_message,
                provider=LLMProvider.OLLAMA,
                model=self.default_model,
                retryable=True,
            )

    async def create_embedding(self, text: str) -> List[float]:
        """Create embeddings using Ollama."""
        session = await self._get_session()

        try:
            payload = {
                "model": "llama3.2:3b",
                "prompt": text
            }

            async with session.post(
                f"{self.config.base_url}/api/embeddings",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    raise Exception(f"Ollama embeddings API error: {response.status}")

                result = await response.json()
                return result.get("embedding", [])

        except Exception as e:
            # Ensure the exception is properly derived from BaseException
            error_message = str(e) if e else "Unknown Ollama embedding error"
            raise LLMError(
                error_type="ollama_embedding_error",
                message=error_message,
                provider=LLMProvider.OLLAMA,
                model="llama3.2:3b",
                retryable=True,
            )

    def get_provider_info(self) -> Dict[str, Any]:
        """Get Ollama provider information."""
        return {
            "provider": LLMProvider.OLLAMA.value,
            "model": self.default_model,
            "base_url": self.config.base_url,
        }


class MockProvider(LLMProviderInterface):
    """Mock provider for testing."""

    def __init__(self, config: LLMConfig):
        self.config = config

    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate mock text."""
        await asyncio.sleep(0.1)  # Simulate network delay

        return LLMResponse(
            content=f"Mock response to: {request.prompt[:50]}...",
            provider=LLMProvider.MOCK,
            model=self.config.model,
            token_usage={
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30,
            },
            finish_reason="stop",
            response_time_ms=100,
            metadata={"mock": True},
        )

    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Generate mock streaming text."""
        words = f"Mock streaming response to: {request.prompt[:30]}...".split()
        for word in words:
            await asyncio.sleep(0.05)
            yield word + " "

    async def create_embedding(self, text: str) -> List[float]:
        """Create mock embeddings."""
        import hashlib

        hash_obj = hashlib.md5(text.encode())
        return [float(x) / 255.0 for x in hash_obj.digest()[:8]]

    def get_provider_info(self) -> Dict[str, Any]:
        """Get mock provider information."""
        return {
            "provider": LLMProvider.MOCK.value,
            "model": self.config.model,
            "mock": True,
        }


class EnhancedLLMClient:
    """Enhanced LLM client with fallback and comprehensive features."""

    def __init__(self, configs: List[LLMConfig] = None):
        """Initialize the enhanced LLM client."""
        self.providers: List[LLMProviderInterface] = []
        self.current_provider_index = 0
        self.fallback_providers: List[int] = []
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "fallback_requests": 0,
            "total_tokens": 0,
            "total_response_time": 0,
        }

        # Initialize providers
        if configs:
            for config in configs:
                self._add_provider(config)
        else:
            # Use default configuration
            self._setup_default_providers()

    def _setup_default_providers(self):
        """Setup default providers from environment variables."""
        providers = []

        # Ollama provider (free, local) - prioritize if enabled
        if settings.ollama_enabled:
            providers.append(
                LLMConfig(
                    provider=LLMProvider.OLLAMA,
                    model=settings.ollama_model or "llama3.2:3b",
                    api_key=None,  # No API key needed for local Ollama
                    base_url=str(settings.ollama_base_url),
                )
            )

        # OpenAI provider
        if settings.openai_api_key:
            providers.append(
                LLMConfig(
                    provider=LLMProvider.OPENAI,
                    model=os.getenv("OPENAI_MODEL", "gpt-4"),
                    api_key=settings.openai_api_key,
                    base_url=os.getenv("OPENAI_BASE_URL"),
                )
            )

        # Anthropic provider
        if settings.anthropic_api_key:
            providers.append(
                LLMConfig(
                    provider=LLMProvider.ANTHROPIC,
                    model=settings.anthropic_model or "claude-3-sonnet-20240229",
                    api_key=settings.anthropic_api_key,
                )
            )

        # Mock provider for testing
        if os.getenv("USE_MOCK_LLM", "false").lower() == "true":
            providers.append(
                LLMConfig(
                    provider=LLMProvider.MOCK, model="mock-model", api_key="mock-key"
                )
            )

        for config in providers:
            self._add_provider(config)

    def _add_provider(self, config: LLMConfig):
        """Add a provider to the client."""
        provider_map = {
            LLMProvider.OPENAI: OpenAIProvider,
            LLMProvider.ANTHROPIC: AnthropicProvider,
            LLMProvider.OLLAMA: OllamaProvider,
            LLMProvider.MOCK: MockProvider,
        }

        provider_class = provider_map.get(config.provider)
        if provider_class:
            provider = provider_class(config)
            self.providers.append(provider)
            logger.info(
                f"Added {config.provider.value} provider with model {config.model}"
            )
        else:
            logger.warning(f"Unsupported provider: {config.provider}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((LLMError, Exception)),
    )
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text with automatic fallback."""
        if not self.providers:
            raise LLMError(
                error_type="no_providers",
                message="No LLM providers configured",
                provider=LLMProvider.MOCK,
                model="none",
                retryable=False,
            )

        self.metrics["total_requests"] += 1
        start_time = time.time()

        # Try primary provider
        for i, provider in enumerate(self.providers):
            try:
                logger.info(
                    f"Attempting request with provider {i}: {provider.get_provider_info()}"
                )

                response = await provider.generate_text(request)

                # Update metrics
                self.metrics["successful_requests"] += 1
                self.metrics["total_tokens"] += response.token_usage.get(
                    "total_tokens", 0
                )
                self.metrics["total_response_time"] += response.response_time_ms

                if i > 0:
                    self.metrics["fallback_requests"] += 1

                logger.info(
                    f"Request successful with provider {i}: {response.response_time_ms:.2f}ms"
                )
                return response

            except Exception as e:
                logger.warning(f"Provider {i} failed: {str(e)}")
                self.metrics["failed_requests"] += 1

                if i == len(self.providers) - 1:
                    # All providers failed
                    raise LLMError(
                        error_type="all_providers_failed",
                        message=f"All providers failed: {str(e)}",
                        provider=LLMProvider.MOCK,
                        model="none",
                        retryable=True,
                    )

        raise LLMError(
            error_type="no_response",
            message="No response from any provider",
            provider=LLMProvider.MOCK,
            model="none",
            retryable=True,
        )

    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Generate streaming text with fallback."""
        if not self.providers:
            raise LLMError(
                error_type="no_providers",
                message="No LLM providers configured",
                provider=LLMProvider.MOCK,
                model="none",
                retryable=False,
            )

        # Try primary provider
        for i, provider in enumerate(self.providers):
            try:
                logger.info(f"Attempting streaming request with provider {i}")

                async for chunk in provider.generate_stream(request):
                    yield chunk

                return  # Success

            except Exception as e:
                logger.warning(f"Streaming provider {i} failed: {str(e)}")

                if i == len(self.providers) - 1:
                    # All providers failed
                    raise LLMError(
                        error_type="all_providers_failed",
                        message=f"All streaming providers failed: {str(e)}",
                        provider=LLMProvider.MOCK,
                        model="none",
                        retryable=True,
                    )

    async def create_embedding(self, text: str) -> List[float]:
        """Create embeddings with local-first strategy (free) and fallback."""
        # Prefer free/local embeddings when configured
        try:
            from shared.core.config.central_config import get_central_config
            cfg = get_central_config()
            if getattr(cfg, "prioritize_free_models", True):
                import anyio

                def _local_embed() -> List[float]:
                    from shared.embeddings.local_embedder import embed_texts
                    return embed_texts([text])[0]

                return await anyio.to_thread.run_sync(_local_embed)
        except Exception as e:
            logger.warning(f"Local embedding attempt failed, falling back to providers: {e}")

        if not self.providers:
            raise LLMError(
                error_type="no_providers",
                message="No LLM providers configured",
                provider=LLMProvider.MOCK,
                model="none",
                retryable=False,
            )

        # Try primary provider
        for i, provider in enumerate(self.providers):
            try:
                return await provider.create_embedding(text)
            except Exception as e:
                logger.warning(f"Embedding provider {i} failed: {str(e)}")

                if i == len(self.providers) - 1:
                    raise LLMError(
                        error_type="all_providers_failed",
                        message=f"All embedding providers failed: {str(e)}",
                        provider=LLMProvider.MOCK,
                        model="none",
                        retryable=True,
                    )

    def get_metrics(self) -> Dict[str, Any]:
        """Get client metrics."""
        return {
            **self.metrics,
            "providers": [p.get_provider_info() for p in self.providers],
            "current_provider": self.current_provider_index,
        }

    def get_health_status(self) -> Dict[str, Any]:
        """Get client health status."""
        return {
            "status": "healthy" if self.providers else "unhealthy",
            "providers_count": len(self.providers),
            "metrics": self.get_metrics(),
        }


# Global client instance
_llm_client: Optional[EnhancedLLMClient] = None


def get_llm_client() -> EnhancedLLMClient:
    """Get global LLM client instance."""
    global _llm_client

    if _llm_client is None:
        _llm_client = EnhancedLLMClient()

    return _llm_client
