from shared.core.api.config import get_settings

settings = get_settings()
"""
Standalone LLM Client v3 - No Dependencies
Modern, production-ready LLM integration with latest SDKs.

This is a standalone version that doesn't depend on other modules
to avoid import issues during testing and development.

Features:
- Latest SDK versions (OpenAI 1.50+, Anthropic 0.25+)
- Async-first design with proper error handling
- Automatic fallback between providers
- Comprehensive retry logic with exponential backoff
- Rate limiting and token usage tracking
- Performance monitoring and metrics
- Streaming support with proper error handling
- Embedding support with fallback options

Authors:
- Universal Knowledge Platform Engineering Team

Version:
    3.0.0 (2024-12-28)
"""

import asyncio
import logging
import time
import os
import json
import hashlib
from typing import Dict, Any, List, Optional, Union, AsyncGenerator, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
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

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    GOOGLE = "google"
    MOCK = "mock"  # For testing


class LLMModel(str, Enum):
    """Supported LLM models with latest versions."""

    # OpenAI models (Latest as of 2024-2025)
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4 = "gpt-4"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"

    # Anthropic models (Latest as of 2024-2025)
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_3_5_HAIKU = "claude-3-5-haiku-20241022"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"

    # Azure models
    AZURE_GPT_4 = "gpt-4"
    AZURE_GPT_35 = "gpt-35-turbo"

    # Google models
    GEMINI_PRO = "gemini-pro"
    GEMINI_PRO_VISION = "gemini-pro-vision"


class EmbeddingModel(str, Enum):
    """Supported embedding models."""

    # OpenAI embeddings
    OPENAI_TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    OPENAI_TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"

    # Anthropic embeddings
    ANTHROPIC_TEXT_EMBEDDING_3 = "text-embedding-3"

    # Local fallback
    SENTENCE_TRANSFORMERS = "all-MiniLM-L6-v2"


@dataclass
class LLMConfig:
    """LLM configuration with latest settings."""

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
    enable_rate_limiting: bool = True

    # Rate limiting
    requests_per_minute: int = 60
    tokens_per_minute: int = 10000

    # Embedding settings
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536


@dataclass
class LLMRequest:
    """LLM request structure with comprehensive options."""

    prompt: str
    system_message: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Advanced options
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop_sequences: Optional[List[str]] = None


@dataclass
class LLMResponse:
    """LLM response structure with comprehensive data."""

    content: str
    provider: LLMProvider
    model: str
    token_usage: Dict[str, int]
    finish_reason: str
    response_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Additional fields
    request_id: Optional[str] = None
    model_version: Optional[str] = None
    cost_estimate: Optional[float] = None


@dataclass
class LLMError:
    """LLM error structure with detailed information."""

    error_type: str
    message: str
    provider: LLMProvider
    model: str
    retryable: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Additional error info
    status_code: Optional[int] = None
    error_code: Optional[str] = None
    rate_limit_info: Optional[Dict[str, Any]] = None


@dataclass
class RateLimitInfo:
    """Rate limiting information."""

    requests_remaining: int
    tokens_remaining: int
    reset_time: float
    window_size: int = 60


class RateLimiter:
    """Rate limiter for LLM API calls."""

    def __init__(self, requests_per_minute: int, tokens_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.tokens_per_minute = tokens_per_minute
        self.request_times: List[float] = []
        self.token_usage: List[Tuple[float, int]] = []
        self._lock = asyncio.Lock()

    async def acquire(self, estimated_tokens: int = 0) -> bool:
        """Acquire permission to make a request."""
        async with self._lock:
            now = time.time()

            # Clean old entries
            self.request_times = [t for t in self.request_times if now - t < 60]
            self.token_usage = [
                (t, tokens) for t, tokens in self.token_usage if now - t < 60
            ]

            # Check request rate limit
            if len(self.request_times) >= self.requests_per_minute:
                return False

            # Check token rate limit
            current_tokens = sum(tokens for _, tokens in self.token_usage)
            if current_tokens + estimated_tokens > self.tokens_per_minute:
                return False

            # Record usage
            self.request_times.append(now)
            self.token_usage.append((now, estimated_tokens))

            return True

    async def wait_if_needed(self, estimated_tokens: int = 0):
        """Wait if rate limit is exceeded."""
        while not await self.acquire(estimated_tokens):
            await asyncio.sleep(1)


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

    @abstractmethod
    async def health_check(self) -> bool:
        """Check provider health."""
        pass


class OpenAIProvider(LLMProviderInterface):
    """OpenAI provider implementation with latest SDK."""

    def __init__(self, config: LLMConfig):
        self.config = config
        import openai

        self.client = openai.AsyncOpenAI(
            api_key=config.api_key, base_url=config.base_url, timeout=config.timeout
        )
        self.rate_limiter = RateLimiter(
            config.requests_per_minute, config.tokens_per_minute
        )

    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text using OpenAI with latest API."""
        start_time = time.time()

        try:
            # Wait for rate limit
            estimated_tokens = len(request.prompt.split()) * 2
            await self.rate_limiter.wait_if_needed(estimated_tokens)

            messages = []
            if request.system_message:
                messages.append({"role": "system", "content": request.system_message})
            messages.append({"role": "user", "content": request.prompt})

            # Prepare parameters
            params = {
                "model": self.config.model,
                "messages": messages,
                "temperature": request.temperature or self.config.temperature,
                "max_tokens": request.max_tokens or self.config.max_tokens,
                "stream": request.stream,
            }

            # Add optional parameters
            if request.top_p is not None:
                params["top_p"] = request.top_p
            if request.frequency_penalty is not None:
                params["frequency_penalty"] = request.frequency_penalty
            if request.presence_penalty is not None:
                params["presence_penalty"] = request.presence_penalty
            if request.stop_sequences:
                params["stop"] = request.stop_sequences

            response = await self.client.chat.completions.create(**params)

            response_time = (time.time() - start_time) * 1000

            return LLMResponse(
                content=response.choices[0].message.content or "",
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
                request_id=response.id,
                cost_estimate=self._estimate_cost(response.usage),
            )

        except Exception as e:
            raise LLMError(
                error_type="openai_error",
                message=str(e),
                provider=LLMProvider.OPENAI,
                model=self.config.model,
                retryable=self._is_retryable_error(e),
            )

    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Generate streaming text using OpenAI."""
        try:
            # Wait for rate limit
            estimated_tokens = len(request.prompt.split()) * 2
            await self.rate_limiter.wait_if_needed(estimated_tokens)

            messages = []
            if request.system_message:
                messages.append({"role": "system", "content": request.system_message})
            messages.append({"role": "user", "content": request.prompt})

            params = {
                "model": self.config.model,
                "messages": messages,
                "temperature": request.temperature or self.config.temperature,
                "max_tokens": request.max_tokens or self.config.max_tokens,
                "stream": True,
            }

            # Add optional parameters
            if request.top_p is not None:
                params["top_p"] = request.top_p
            if request.frequency_penalty is not None:
                params["frequency_penalty"] = request.frequency_penalty
            if request.presence_penalty is not None:
                params["presence_penalty"] = request.presence_penalty
            if request.stop_sequences:
                params["stop"] = request.stop_sequences

            stream = await self.client.chat.completions.create(**params)

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise LLMError(
                error_type="openai_stream_error",
                message=str(e),
                provider=LLMProvider.OPENAI,
                model=self.config.model,
                retryable=self._is_retryable_error(e),
            )

    async def create_embedding(self, text: str) -> List[float]:
        """Create embeddings using OpenAI."""
        try:
            # Wait for rate limit
            estimated_tokens = len(text.split())
            await self.rate_limiter.wait_if_needed(estimated_tokens)

            response = await self.client.embeddings.create(
                model=self.config.embedding_model, input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise LLMError(
                error_type="openai_embedding_error",
                message=str(e),
                provider=LLMProvider.OPENAI,
                model=self.config.embedding_model,
                retryable=self._is_retryable_error(e),
            )

    def get_provider_info(self) -> Dict[str, Any]:
        """Get OpenAI provider information."""
        return {
            "provider": LLMProvider.OPENAI.value,
            "model": self.config.model,
            "base_url": self.config.base_url,
            "embedding_model": self.config.embedding_model,
        }

    async def health_check(self) -> bool:
        """Check OpenAI health."""
        try:
            response = await self.client.models.list()
            return len(response.data) > 0
        except Exception:
            return False

    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if error is retryable."""
        error_str = str(error).lower()
        retryable_errors = [
            "rate_limit",
            "timeout",
            "connection",
            "server_error",
            "internal_error",
            "service_unavailable",
        ]
        return any(err in error_str for err in retryable_errors)

    def _estimate_cost(self, usage) -> float:
        """Estimate cost based on token usage."""
        # Rough cost estimates (update with current pricing)
        costs = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        }

        model_costs = costs.get(self.config.model, {"input": 0.01, "output": 0.02})
        return (
            usage.prompt_tokens * model_costs["input"] / 1000
            + usage.completion_tokens * model_costs["output"] / 1000
        )


class AnthropicProvider(LLMProviderInterface):
    """Anthropic provider implementation with latest SDK."""

    def __init__(self, config: LLMConfig):
        self.config = config
        import anthropic

        self.client = anthropic.AsyncAnthropic(api_key=config.api_key)
        self.rate_limiter = RateLimiter(
            config.requests_per_minute, config.tokens_per_minute
        )

    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text using Anthropic with latest API."""
        start_time = time.time()

        try:
            # Wait for rate limit
            estimated_tokens = len(request.prompt.split()) * 2
            await self.rate_limiter.wait_if_needed(estimated_tokens)

            messages = []
            if request.system_message:
                messages.append({"role": "system", "content": request.system_message})
            messages.append({"role": "user", "content": request.prompt})

            # Prepare parameters
            params = {
                "model": self.config.model,
                "max_tokens": request.max_tokens or self.config.max_tokens,
                "temperature": request.temperature or self.config.temperature,
                "messages": messages,
            }

            # Add optional parameters
            if request.top_p is not None:
                params["top_p"] = request.top_p
            if request.stop_sequences:
                params["stop_sequences"] = request.stop_sequences

            response = await self.client.messages.create(**params)

            response_time = (time.time() - start_time) * 1000

            return LLMResponse(
                content=response.content[0].text if response.content else "",
                provider=LLMProvider.ANTHROPIC,
                model=self.config.model,
                token_usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens
                    + response.usage.output_tokens,
                },
                finish_reason=response.stop_reason,
                response_time_ms=response_time,
                metadata={"request_id": response.id},
                request_id=response.id,
                cost_estimate=self._estimate_cost(response.usage),
            )

        except Exception as e:
            raise LLMError(
                error_type="anthropic_error",
                message=str(e),
                provider=LLMProvider.ANTHROPIC,
                model=self.config.model,
                retryable=self._is_retryable_error(e),
            )

    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Generate streaming text using Anthropic."""
        try:
            # Wait for rate limit
            estimated_tokens = len(request.prompt.split()) * 2
            await self.rate_limiter.wait_if_needed(estimated_tokens)

            messages = []
            if request.system_message:
                messages.append({"role": "system", "content": request.system_message})
            messages.append({"role": "user", "content": request.prompt})

            params = {
                "model": self.config.model,
                "max_tokens": request.max_tokens or self.config.max_tokens,
                "temperature": request.temperature or self.config.temperature,
                "messages": messages,
                "stream": True,
            }

            # Add optional parameters
            if request.top_p is not None:
                params["top_p"] = request.top_p
            if request.stop_sequences:
                params["stop_sequences"] = request.stop_sequences

            stream = await self.client.messages.create(**params)

            async for chunk in stream:
                if chunk.type == "content_block_delta":
                    yield chunk.delta.text

        except Exception as e:
            raise LLMError(
                error_type="anthropic_stream_error",
                message=str(e),
                provider=LLMProvider.ANTHROPIC,
                model=self.config.model,
                retryable=self._is_retryable_error(e),
            )

    async def create_embedding(self, text: str) -> List[float]:
        """Create embeddings using Anthropic."""
        try:
            # Wait for rate limit
            estimated_tokens = len(text.split())
            await self.rate_limiter.wait_if_needed(estimated_tokens)

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
                retryable=self._is_retryable_error(e),
            )

    def get_provider_info(self) -> Dict[str, Any]:
        """Get Anthropic provider information."""
        return {
            "provider": LLMProvider.ANTHROPIC.value,
            "model": self.config.model,
            "embedding_model": "text-embedding-3",
        }

    async def health_check(self) -> bool:
        """Check Anthropic health."""
        try:
            # Simple health check
            response = await self.client.messages.create(
                model=self.config.model,
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}],
            )
            return True
        except Exception:
            return False

    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if error is retryable."""
        error_str = str(error).lower()
        retryable_errors = [
            "rate_limit",
            "timeout",
            "connection",
            "server_error",
            "internal_error",
            "service_unavailable",
        ]
        return any(err in error_str for err in retryable_errors)

    def _estimate_cost(self, usage) -> float:
        """Estimate cost based on token usage."""
        # Rough cost estimates for Claude (update with current pricing)
        costs = {
            "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
            "claude-3-5-haiku-20241022": {"input": 0.00025, "output": 0.00125},
            "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
            "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
        }

        model_costs = costs.get(self.config.model, {"input": 0.003, "output": 0.015})
        return (
            usage.input_tokens * model_costs["input"] / 1000
            + usage.output_tokens * model_costs["output"] / 1000
        )


class MockProvider(LLMProviderInterface):
    """Mock provider for testing with realistic behavior."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.rate_limiter = RateLimiter(
            config.requests_per_minute, config.tokens_per_minute
        )

    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate mock text with realistic timing."""
        await asyncio.sleep(0.1)  # Simulate network delay

        # Wait for rate limit
        estimated_tokens = len(request.prompt.split()) * 2
        await self.rate_limiter.wait_if_needed(estimated_tokens)

        start_time = time.time()

        # Generate realistic mock response
        mock_content = f"Mock response to: {request.prompt[:50]}... This is a simulated response from the mock LLM provider."

        response_time = (time.time() - start_time) * 1000

        return LLMResponse(
            content=mock_content,
            provider=LLMProvider.MOCK,
            model=self.config.model,
            token_usage={
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30,
            },
            finish_reason="stop",
            response_time_ms=response_time,
            metadata={"mock": True},
            request_id=f"mock_{hashlib.md5(request.prompt.encode()).hexdigest()[:8]}",
            cost_estimate=0.0,
        )

    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Generate mock streaming text."""
        # Wait for rate limit
        estimated_tokens = len(request.prompt.split()) * 2
        await self.rate_limiter.wait_if_needed(estimated_tokens)

        words = f"Mock streaming response to: {request.prompt[:30]}... This is a simulated streaming response.".split()
        for word in words:
            await asyncio.sleep(0.05)  # Simulate streaming delay
            yield word + " "

    async def create_embedding(self, text: str) -> List[float]:
        """Create mock embeddings."""
        # Wait for rate limit
        estimated_tokens = len(text.split())
        await self.rate_limiter.wait_if_needed(estimated_tokens)

        # Generate deterministic mock embeddings
        hash_obj = hashlib.md5(text.encode())
        return [float(x) / 255.0 for x in hash_obj.digest()[:8]]

    def get_provider_info(self) -> Dict[str, Any]:
        """Get mock provider information."""
        return {
            "provider": LLMProvider.MOCK.value,
            "model": self.config.model,
            "mock": True,
        }

    async def health_check(self) -> bool:
        """Mock health check."""
        return True


class EnhancedLLMClientV3:
    """Enhanced LLM client v3 with comprehensive features."""

    def __init__(self, configs: List[LLMConfig] = None):
        """Initialize the enhanced LLM client."""
        self.providers: List[LLMProviderInterface] = []
        self.current_provider_index = 0
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "fallback_requests": 0,
            "total_tokens": 0,
            "total_response_time": 0,
            "total_cost": 0.0,
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

        # OpenAI provider
        if settings.openai_api_key:
            providers.append(
                LLMConfig(
                    provider=LLMProvider.OPENAI,
                    model=os.getenv("OPENAI_MODEL", "gpt-4"),
                    api_key=settings.openai_api_key,
                    base_url=os.getenv("OPENAI_BASE_URL"),
                    embedding_model=os.getenv(
                        "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
                    ),
                )
            )

        # Anthropic provider
        if settings.anthropic_api_key:
            providers.append(
                LLMConfig(
                    provider=LLMProvider.ANTHROPIC,
                    model=settings.anthropic_model or "claude-3-5-sonnet-20241022",
                    api_key=settings.anthropic_api_key,
                    embedding_model="text-embedding-3",
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
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text with automatic fallback and comprehensive error handling."""
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

        # Try providers in order with fallback
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
                if response.cost_estimate:
                    self.metrics["total_cost"] += response.cost_estimate

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

        # Try providers in order with fallback
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
        """Create embeddings with fallback."""
        if not self.providers:
            raise LLMError(
                error_type="no_providers",
                message="No LLM providers configured",
                provider=LLMProvider.MOCK,
                model="none",
                retryable=False,
            )

        # Try providers in order with fallback
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

    async def health_check(self) -> Dict[str, Any]:
        """Check health of all providers."""
        health_status = {}

        for i, provider in enumerate(self.providers):
            try:
                is_healthy = await provider.health_check()
                health_status[f"provider_{i}"] = {
                    "healthy": is_healthy,
                    "info": provider.get_provider_info(),
                }
            except Exception as e:
                health_status[f"provider_{i}"] = {
                    "healthy": False,
                    "error": str(e),
                    "info": provider.get_provider_info(),
                }

        return health_status

    def get_metrics(self) -> Dict[str, Any]:
        """Get client metrics."""
        avg_response_time = (
            self.metrics["total_response_time"] / self.metrics["successful_requests"]
            if self.metrics["successful_requests"] > 0
            else 0
        )

        return {
            **self.metrics,
            "avg_response_time_ms": avg_response_time,
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
_llm_client_v3: Optional[EnhancedLLMClientV3] = None


def get_llm_client_v3() -> EnhancedLLMClientV3:
    """Get global LLM client v3 instance."""
    global _llm_client_v3

    if _llm_client_v3 is None:
        _llm_client_v3 = EnhancedLLMClientV3()

    return _llm_client_v3


# Convenience functions for backward compatibility
async def generate_text(prompt: str, **kwargs) -> str:
    """Generate text using the global LLM client."""
    client = get_llm_client_v3()
    request = LLMRequest(prompt=prompt, **kwargs)
    response = await client.generate_text(request)
    return response.content


async def create_embedding(text: str) -> List[float]:
    """Create embedding using the global LLM client."""
    client = get_llm_client_v3()
    return await client.create_embedding(text)
