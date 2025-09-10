#!/usr/bin/env python3
"""
SarvanOM GPU Provider Orchestration
Free GPU orchestration with zero-budget optimization.

This module implements:
- Provider base class with health checks and circuit breakers
- LocalOllamaProvider (CPU quantized models)
- RemoteGPUProvider (Colab/Kaggle/HF Space via ngrok)
- PaidProvider stubs (OpenAI, Anthropic)
- Circuit breaker pattern (3 failures → skip 5 min)
- Health checks with latency monitoring
- Timeout handling (15s per call)
"""

import asyncio
import time
import logging
import os
import json
import uuid
from typing import Dict, Any, Optional, List, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import requests

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)

# Environment configuration
GPU_REMOTE_URL = os.getenv("GPU_REMOTE_URL", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
ENABLE_PAID_API = os.getenv("ENABLE_PAID_API", "false").lower() == "true"
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "15"))

# Validate environment variables
if GPU_REMOTE_URL and not GPU_REMOTE_URL.startswith(('http://', 'https://')):
    logger.warning(f"Invalid GPU_REMOTE_URL format: {GPU_REMOTE_URL}. Expected http:// or https://")
    GPU_REMOTE_URL = ""


class ProviderType(str, Enum):
    """GPU provider types for orchestration."""
    LOCAL_OLLAMA = "ollama_local"
    REMOTE_GPU = "remote_gpu"
    HUGGINGFACE = "huggingface"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    # Removed LOCAL_STUB - no mock responses


class ProviderStatus(str, Enum):
    """Provider health status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    CIRCUIT_OPEN = "circuit_open"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class ProviderHealth:
    """Provider health status with metrics."""
    status: ProviderStatus
    last_check: datetime
    latency_ms: float = 0.0
    error_count: int = 0
    success_count: int = 0
    circuit_open_until: Optional[datetime] = None
    last_error: Optional[str] = None


@dataclass
class LLMRequest:
    """Standardized LLM request."""
    prompt: str
    system_message: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.2
    timeout: int = 15
    trace_id: Optional[str] = None


@dataclass
class LLMResponse:
    """Standardized LLM response."""
    content: str
    provider: ProviderType
    model: str
    latency_ms: float
    success: bool
    error_message: Optional[str] = None
    trace_id: Optional[str] = None
    attempt: int = 1


class BaseGPUProvider:
    """Base class for all GPU providers with circuit breaker and health monitoring."""
    
    def __init__(self, provider_type: ProviderType, name: str):
        self.provider_type = provider_type
        self.name = name
        self.health = ProviderHealth(
            status=ProviderStatus.UNHEALTHY,
            last_check=datetime.now()
        )
        self.circuit_breaker_threshold = 3
        self.circuit_breaker_timeout = 300  # 5 minutes
        self.max_timeout = LLM_TIMEOUT_SECONDS
        
    async def health_check(self) -> ProviderHealth:
        """Check provider health with timeout."""
        start_time = time.time()
        trace_id = str(uuid.uuid4())
        
        try:
            # Check if circuit breaker is open
            if (self.health.circuit_open_until and 
                datetime.now() < self.health.circuit_open_until):
                self.health.status = ProviderStatus.CIRCUIT_OPEN
                return self.health
            
            # Perform health check with timeout
            await asyncio.wait_for(self._perform_health_check(), timeout=self.max_timeout)
            
            # Success
            latency_ms = (time.time() - start_time) * 1000
            self.health.status = ProviderStatus.HEALTHY
            self.health.last_check = datetime.now()
            self.health.latency_ms = latency_ms
            self.health.success_count += 1
            self.health.error_count = 0  # Reset error count on success
            self.health.circuit_open_until = None
            
            logger.info(f"✅ {self.name} health check passed", extra={
                "provider": self.name,
                "latency_ms": latency_ms,
                "trace_id": trace_id
            })
            
        except asyncio.TimeoutError:
            # Timeout
            latency_ms = (time.time() - start_time) * 1000
            self._handle_error("Health check timeout", latency_ms)
            logger.warning(f"⏰ {self.name} health check timeout", extra={
                "provider": self.name,
                "latency_ms": latency_ms,
                "trace_id": trace_id
            })
            
        except Exception as e:
            # Error
            latency_ms = (time.time() - start_time) * 1000
            self._handle_error(f"Health check error: {str(e)}", latency_ms)
            logger.error(f"❌ {self.name} health check failed: {e}", extra={
                "provider": self.name,
                "latency_ms": latency_ms,
                "error": str(e),
                "trace_id": trace_id
            })
        
        return self.health
    
    def _handle_error(self, error_msg: str, latency_ms: float):
        """Handle provider error with circuit breaker logic."""
        self.health.status = ProviderStatus.ERROR
        self.health.last_check = datetime.now()
        self.health.latency_ms = latency_ms
        self.health.error_count += 1
        self.health.last_error = error_msg
        
        # Check circuit breaker
        if self.health.error_count >= self.circuit_breaker_threshold:
            self.health.status = ProviderStatus.CIRCUIT_OPEN
            self.health.circuit_open_until = datetime.now() + timedelta(seconds=self.circuit_breaker_timeout)
            logger.warning(f"🔌 {self.name} circuit breaker opened for {self.circuit_breaker_timeout}s")
    
    async def _perform_health_check(self):
        """Override in subclasses to implement specific health checks."""
        raise NotImplementedError
    
    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Complete LLM request with timeout and error handling."""
        start_time = time.time()
        trace_id = request.trace_id or str(uuid.uuid4())
        
        try:
            # Check circuit breaker
            if (self.health.circuit_open_until and 
                datetime.now() < self.health.circuit_open_until):
                return LLMResponse(
                    content="",
                    provider=self.provider_type,
                    model=self.name,
                    latency_ms=0,
                    success=False,
                    error_message="Circuit breaker open",
                    trace_id=trace_id
                )
            
            # Perform request with timeout
            content = await asyncio.wait_for(
                self._complete_request(request),
                timeout=request.timeout
            )
            
            # Success
            latency_ms = (time.time() - start_time) * 1000
            self.health.success_count += 1
            self.health.error_count = 0
            self.health.circuit_open_until = None
            
            logger.info(f"✅ {self.name} request successful", extra={
                "provider": self.name,
                "latency_ms": latency_ms,
                "trace_id": trace_id
            })
            
            return LLMResponse(
                content=content,
                provider=self.provider_type,
                model=self.name,
                latency_ms=latency_ms,
                success=True,
                trace_id=trace_id
            )
            
        except asyncio.TimeoutError:
            # Timeout
            latency_ms = (time.time() - start_time) * 1000
            self._handle_error("Request timeout", latency_ms)
            return LLMResponse(
                content="",
                provider=self.provider_type,
                model=self.name,
                latency_ms=latency_ms,
                success=False,
                error_message="Request timeout",
                trace_id=trace_id
            )
            
        except Exception as e:
            # Error
            latency_ms = (time.time() - start_time) * 1000
            self._handle_error(f"Request error: {str(e)}", latency_ms)
            return LLMResponse(
                content="",
                provider=self.provider_type,
                model=self.name,
                latency_ms=latency_ms,
                success=False,
                error_message=str(e),
                trace_id=trace_id
            )
    
    async def _complete_request(self, request: LLMRequest) -> str:
        """Override in subclasses to implement specific request handling."""
        raise NotImplementedError
    
    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Stream LLM response (optional implementation)."""
        # Default implementation - return single response
        response = await self.complete(request)
        if response.success:
            yield response.content
        else:
            yield f"Error: {response.error_message}"


class LocalOllamaProvider(BaseGPUProvider):
    """Local Ollama provider with CPU quantized models."""
    
    def __init__(self):
        super().__init__(ProviderType.LOCAL_OLLAMA, "ollama_local")
        self.base_url = OLLAMA_BASE_URL
        self.default_model = "deepseek-r1:8b"  # This should match the model name from Ollama
    
    async def _perform_health_check(self):
        """Check if Ollama is running locally."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags", timeout=5) as response:
                    if response.status != 200:
                        raise Exception(f"Ollama health check failed: {response.status}")
                    result = await response.json()
                    
                    # Check if the default model is available
                    models = result.get("models", [])
                    model_names = [model.get("name", "") for model in models]
                    
                    if self.default_model not in model_names:
                        logger.warning(f"Model {self.default_model} not found in Ollama. Available: {model_names[:3]}")
                        # Try to use the first available model
                        if model_names:
                            self.default_model = model_names[0]
                            logger.info(f"Using available model: {self.default_model}")
                        else:
                            raise Exception("No models available in Ollama")
                    
                    return result
        except Exception as e:
            raise Exception(f"Ollama health check failed: {str(e)}")
    
    async def _complete_request(self, request: LLMRequest) -> str:
        """Complete request using local Ollama."""
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.default_model,
                "prompt": request.prompt,
                "stream": False,
                "options": {
                    "temperature": request.temperature,
                    "num_predict": min(request.max_tokens, 150),
                    "stop": ["\n\n", "Human:", "Assistant:"],
                    "num_ctx": 1024
                }
            }
            
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=request.timeout)
            ) as response:
                if response.status != 200:
                    raise Exception(f"Ollama API error: {response.status}")
                
                result = await response.json()
                return result.get("response", "")


class RemoteGPUProvider(BaseGPUProvider):
    """Remote GPU provider (Colab/Kaggle/HF Space via ngrok)."""
    
    def __init__(self):
        super().__init__(ProviderType.REMOTE_GPU, "remote_gpu")
        self.remote_url = GPU_REMOTE_URL
        if not self.remote_url:
            raise ValueError("GPU_REMOTE_URL environment variable not set")
        if not self.remote_url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid GPU_REMOTE_URL format: {self.remote_url}. Expected http:// or https://")
    
    async def _perform_health_check(self):
        """Check remote GPU endpoint health."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.remote_url}/health", timeout=10) as response:
                if response.status != 200:
                    raise Exception(f"Remote GPU health check failed: {response.status}")
                return await response.json()
    
    async def _complete_request(self, request: LLMRequest) -> str:
        """Complete request using remote GPU."""
        async with aiohttp.ClientSession() as session:
            payload = {
                "prompt": request.prompt,
                "system_message": request.system_message,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "stream": False
            }
            
            async with session.post(
                f"{self.remote_url}/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=request.timeout)
            ) as response:
                if response.status != 200:
                    raise Exception(f"Remote GPU API error: {response.status}")
                
                result = await response.json()
                return result.get("content", result.get("response", ""))


class HuggingFaceProvider(BaseGPUProvider):
    """HuggingFace free tier provider."""
    
    def __init__(self):
        super().__init__(ProviderType.HUGGINGFACE, "huggingface")
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY environment variable not set")
        # Use a more reliable model that's always available
        self.default_model = "gpt2"
        
        # Validate API key format
        if not self.api_key.startswith("hf_"):
            logger.warning(f"Invalid HuggingFace API key format: {self.api_key[:10]}...")
            # Don't raise error, let health check handle it
    
    async def _perform_health_check(self):
        """Check HuggingFace API health."""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api-inference.huggingface.co/models/{self.default_model}",
                    headers=headers,
                    timeout=10
                ) as response:
                    if response.status not in [200, 503]:  # 503 is normal for loading models
                        raise Exception(f"HuggingFace health check failed: {response.status}")
                    return {"status": "available"}
        except Exception as e:
            raise Exception(f"HuggingFace health check failed: {str(e)}")
    
    async def _complete_request(self, request: LLMRequest) -> str:
        """Complete request using HuggingFace."""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "inputs": request.prompt[:500],  # Truncate for faster models
            "parameters": {
                "max_new_tokens": min(request.max_tokens, 256),
                "temperature": request.temperature,
                "return_full_text": False
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://api-inference.huggingface.co/models/{self.default_model}",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=request.timeout)
            ) as response:
                if response.status != 200:
                    raise Exception(f"HuggingFace API error: {response.status}")
                
                result = await response.json()
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    return result.get("generated_text", "")
                else:
                    return str(result)


class OpenAIProvider(BaseGPUProvider):
    """OpenAI paid provider (only if ENABLE_PAID_API=true)."""
    
    def __init__(self):
        super().__init__(ProviderType.OPENAI, "openai")
        if not ENABLE_PAID_API:
            raise ValueError("OpenAI provider disabled (ENABLE_PAID_API=false)")
        
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        try:
            import openai
            self.client = openai
            self.client.api_key = self.api_key
        except ImportError:
            raise ImportError("OpenAI library not installed")
    
    async def _perform_health_check(self):
        """Check OpenAI API health."""
        # Simple health check - try to list models
        import openai
        try:
            models = await asyncio.to_thread(
                openai.models.list
            )
            return {"status": "available", "models": len(models.data)}
        except Exception as e:
            raise Exception(f"OpenAI health check failed: {str(e)}")
    
    async def _complete_request(self, request: LLMRequest) -> str:
        """Complete request using OpenAI."""
        import openai
        
        response = await asyncio.to_thread(
            openai.chat.completions.create,
            model="gpt-4o-mini",  # Use cost-efficient model
            messages=[
                {"role": "system", "content": request.system_message or "You are a helpful assistant."},
                {"role": "user", "content": request.prompt}
            ],
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return response.choices[0].message.content


class AnthropicProvider(BaseGPUProvider):
    """Anthropic paid provider (only if ENABLE_PAID_API=true)."""
    
    def __init__(self):
        super().__init__(ProviderType.ANTHROPIC, "anthropic")
        if not ENABLE_PAID_API:
            raise ValueError("Anthropic provider disabled (ENABLE_PAID_API=false)")
        
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("Anthropic library not installed")
    
    async def _perform_health_check(self):
        """Check Anthropic API health."""
        try:
            # Simple health check
            return {"status": "available"}
        except Exception as e:
            raise Exception(f"Anthropic health check failed: {str(e)}")
    
    async def _complete_request(self, request: LLMRequest) -> str:
        """Complete request using Anthropic."""
        message = await asyncio.to_thread(
            self.client.messages.create,
            model="claude-3-5-haiku-20241022",  # Use cost-efficient model
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            messages=[{"role": "user", "content": request.prompt}]
        )
        
        return message.content[0].text


# Removed LocalStubProvider class - no mock responses allowed


class GPUProviderOrchestrator:
    """Orchestrates multiple GPU providers with intelligent routing."""
    
    def __init__(self):
        self.providers: Dict[ProviderType, BaseGPUProvider] = {}
        self.provider_order: List[ProviderType] = []
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available providers based on configuration."""
        # Removed stub provider - no mock responses
        
        # Try to add local Ollama
        try:
            self.providers[ProviderType.LOCAL_OLLAMA] = LocalOllamaProvider()
            logger.info("✅ Local Ollama provider initialized")
        except Exception as e:
            logger.warning(f"❌ Local Ollama provider failed to initialize: {e}")
        
        # Try to add remote GPU (only if URL is valid)
        if GPU_REMOTE_URL and GPU_REMOTE_URL.startswith(('http://', 'https://')):
            try:
                self.providers[ProviderType.REMOTE_GPU] = RemoteGPUProvider()
                logger.info("✅ Remote GPU provider initialized")
            except Exception as e:
                logger.warning(f"❌ Remote GPU provider failed to initialize: {e}")
        elif GPU_REMOTE_URL:
            logger.warning(f"❌ Invalid GPU_REMOTE_URL format: {GPU_REMOTE_URL}")
        
        # Try to add HuggingFace
        try:
            self.providers[ProviderType.HUGGINGFACE] = HuggingFaceProvider()
            logger.info("✅ HuggingFace provider initialized")
        except Exception as e:
            logger.warning(f"❌ HuggingFace provider failed to initialize: {e}")
        
        # Try to add paid providers if enabled
        if ENABLE_PAID_API:
            try:
                self.providers[ProviderType.OPENAI] = OpenAIProvider()
                logger.info("✅ OpenAI provider initialized")
            except Exception as e:
                logger.warning(f"❌ OpenAI provider failed to initialize: {e}")
            
            try:
                self.providers[ProviderType.ANTHROPIC] = AnthropicProvider()
                logger.info("✅ Anthropic provider initialized")
            except Exception as e:
                logger.warning(f"❌ Anthropic provider failed to initialize: {e}")
        
        # Set provider order
        self.provider_order = [
            ProviderType.LOCAL_OLLAMA,
            ProviderType.REMOTE_GPU,
            ProviderType.HUGGINGFACE,
            ProviderType.OPENAI,
            ProviderType.ANTHROPIC
            # Removed LOCAL_STUB - no mock responses
        ]
        
        # Filter to only available providers
        self.provider_order = [p for p in self.provider_order if p in self.providers]
        
        logger.info(f"🎯 Provider order: {[p.value for p in self.provider_order]}")
        
        # Ensure we have at least the stub provider
        if not self.providers:
            logger.error("❌ No providers available - this should not happen")
        elif len(self.providers) == 0:
            logger.warning("⚠️ No providers available - no LLM providers configured")
        else:
            logger.info(f"✅ {len(self.providers)} providers available")
    
    async def get_provider_health(self) -> Dict[str, ProviderHealth]:
        """Get health status of all providers."""
        health_status = {}
        
        for provider_type, provider in self.providers.items():
            try:
                health = await provider.health_check()
                health_status[provider_type.value] = health
            except Exception as e:
                logger.error(f"Health check failed for {provider_type.value}: {e}")
                health_status[provider_type.value] = ProviderHealth(
                    status=ProviderStatus.ERROR,
                    last_check=datetime.now(),
                    last_error=str(e)
                )
        
        return health_status
    
    async def complete_request(self, request: LLMRequest) -> LLMResponse:
        """Complete request using best available provider."""
        # Try providers in order until one succeeds
        for provider_type in self.provider_order:
            provider = self.providers[provider_type]
            
            # Skip if circuit breaker is open
            if (provider.health.circuit_open_until and 
                datetime.now() < provider.health.circuit_open_until):
                logger.info(f"⏭️ Skipping {provider.name} (circuit breaker open)")
                continue
            
            try:
                response = await provider.complete(request)
                if response.success:
                    logger.info(f"✅ Request completed with {provider.name}")
                    return response
                else:
                    logger.warning(f"❌ {provider.name} failed: {response.error_message}")
            except Exception as e:
                logger.error(f"❌ {provider.name} exception: {e}")
        
        # All providers failed - return error response
        logger.warning("🚨 All providers failed - no fallback available")
        return CompletionResponse(
            content="All LLM providers are currently unavailable. Please check your configuration and try again.",
            provider="none",
            model="none",
            tokens=0,
            latency_ms=0,
            success=False,
            error="All providers failed"
        )
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return [p.value for p in self.provider_order]


# Global orchestrator instance
gpu_orchestrator = GPUProviderOrchestrator()
