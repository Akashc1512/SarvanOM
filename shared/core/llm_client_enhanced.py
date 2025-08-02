"""
Enhanced LLM Client - Universal Knowledge Platform
Modular LLM provider selection with intelligent routing and fallback chains.

This module provides enhanced LLM provider selection based on:
- Query classification (simple factual, complex synthesis, large context)
- Token limits and context size constraints
- Provider availability and health status
- Cost optimization (prioritizes free/local providers)

Key Features:
- **Modular Provider Selection**: select_llm_provider() method for transparent routing
- **Token Limit Awareness**: Checks context + query size against provider limits
- **Intelligent Fallback Chain**: Ollama → HuggingFace → OpenAI with automatic fallback
- **Query Classification Integration**: Uses QueryClassifier for optimal provider selection
- **Comprehensive Logging**: Tracks which model handled each query
- **Provider Health Monitoring**: Checks provider health before selection

Provider Selection Logic:
- Simple factual → Ollama local model first (free, fast)
- Complex synthesis → HuggingFace Inference API (free, good for research)
- Large context or fallback → OpenAI GPT-3.5 (paid, high capacity)

Token Limits:
- Ollama: ~4K tokens (varies by model)
- HuggingFace: ~2K tokens (free tier limits)
- OpenAI: ~16K tokens (GPT-3.5-turbo)

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
License: MIT
"""

import asyncio
import logging
import time
import os
import json
import hashlib
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
    """Query types for enhanced model selection."""
    SIMPLE_FACTUAL = "simple_factual"
    COMPLEX_SYNTHESIS = "complex_synthesis"
    LARGE_CONTEXT = "large_context"
    UNKNOWN = "unknown"


class LLMProvider(str, Enum):
    """Supported LLM providers with token limits."""
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    OPENAI = "openai"


@dataclass
class ProviderTokenLimits:
    """Token limits for each provider."""
    max_context_tokens: int
    max_total_tokens: int
    cost_per_1k_tokens: float = 0.0
    is_free: bool = True


@dataclass
class LLMRequest:
    """Enhanced LLM request structure."""
    query: str
    context: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.2
    system_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    query_id: Optional[str] = None


@dataclass
class LLMResponse:
    """Enhanced LLM response structure."""
    content: str
    provider: LLMProvider
    model: str
    response_time_ms: float
    token_usage: Optional[Dict[str, int]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    query_id: Optional[str] = None


@dataclass
class ProviderConfig:
    """Enhanced configuration for each LLM provider."""
    name: LLMProvider
    base_url: str
    api_key: Optional[str] = None
    models: List[str] = field(default_factory=list)
    timeout: int = 30
    max_retries: int = 3
    is_available: bool = True
    token_limits: ProviderTokenLimits = field(default_factory=lambda: ProviderTokenLimits(4000, 4000))


class LLMProviderInterface(ABC):
    """Enhanced LLM provider interface with token limit awareness."""
    
    @abstractmethod
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text with token limit awareness."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check provider health."""
        pass
    
    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information including token limits."""
        pass
    
    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        pass
    
    @abstractmethod
    def can_handle_request(self, request: LLMRequest) -> bool:
        """Check if provider can handle the request within token limits."""
        pass


class OllamaProvider(LLMProviderInterface):
    """Enhanced Ollama local LLM provider."""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.session = None
        self.default_model = "llama3.2:3b"
        # Ollama token limits (varies by model)
        self.token_limits = ProviderTokenLimits(
            max_context_tokens=4000,
            max_total_tokens=4000,
            cost_per_1k_tokens=0.0,
            is_free=True
        )
    
    async def _get_session(self):
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            import aiohttp
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for Ollama (rough approximation)."""
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def can_handle_request(self, request: LLMRequest) -> bool:
        """Check if Ollama can handle the request within token limits."""
        total_text = request.query
        if request.context:
            total_text = f"{request.context}\n\n{request.query}"
        if request.system_message:
            total_text = f"{request.system_message}\n\n{total_text}"
        
        estimated_tokens = self.estimate_tokens(total_text) + request.max_tokens
        return estimated_tokens <= self.token_limits.max_total_tokens
    
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text using Ollama."""
        start_time = time.time()
        session = await self._get_session()
        
        # Check token limits
        if not self.can_handle_request(request):
            raise ValueError(f"Request exceeds Ollama token limits: {self.token_limits.max_total_tokens}")
        
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
                "num_predict": request.max_tokens
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
                    response_time_ms=response_time,
                    token_usage={
                        "prompt_tokens": self.estimate_tokens(prompt),
                        "completion_tokens": self.estimate_tokens(content),
                        "total_tokens": self.estimate_tokens(prompt + content)
                    },
                    metadata={"ollama_response": result},
                    query_id=request.query_id
                )
                
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check Ollama health."""
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
            "name": "Ollama",
            "provider": LLMProvider.OLLAMA,
            "model": self.default_model,
            "base_url": self.config.base_url,
            "token_limits": self.token_limits,
            "is_free": True,
            "cost_per_token": 0.0
        }


class HuggingFaceProvider(LLMProviderInterface):
    """Enhanced HuggingFace Inference API provider."""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.session = None
        self.default_model = "microsoft/DialoGPT-medium"
        # HuggingFace free tier limits
        self.token_limits = ProviderTokenLimits(
            max_context_tokens=2000,
            max_total_tokens=2000,
            cost_per_1k_tokens=0.0,
            is_free=True
        )
    
    async def _get_session(self):
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            import aiohttp
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for HuggingFace."""
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def can_handle_request(self, request: LLMRequest) -> bool:
        """Check if HuggingFace can handle the request within token limits."""
        total_text = request.query
        if request.context:
            total_text = f"{request.context}\n\n{request.query}"
        if request.system_message:
            total_text = f"{request.system_message}\n\n{total_text}"
        
        estimated_tokens = self.estimate_tokens(total_text) + request.max_tokens
        return estimated_tokens <= self.token_limits.max_total_tokens
    
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text using HuggingFace Inference API."""
        start_time = time.time()
        session = await self._get_session()
        
        # Check token limits
        if not self.can_handle_request(request):
            raise ValueError(f"Request exceeds HuggingFace token limits: {self.token_limits.max_total_tokens}")
        
        # Prepare the prompt
        prompt = request.query
        if request.context:
            prompt = f"Context: {request.context}\n\nQuery: {request.query}"
        if request.system_message:
            prompt = f"System: {request.system_message}\n\n{prompt}"
        
        # Prepare request payload
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": request.max_tokens,
                "temperature": request.temperature,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with session.post(
                f"https://api-inference.huggingface.co/models/{self.default_model}",
                json=payload,
                headers=headers
            ) as response:
                if response.status != 200:
                    raise Exception(f"HuggingFace API error: {response.status}")
                
                result = await response.json()
                content = result[0].get("generated_text", "") if isinstance(result, list) else result.get("generated_text", "")
                
                response_time = (time.time() - start_time) * 1000
                
                return LLMResponse(
                    content=content,
                    provider=LLMProvider.HUGGINGFACE,
                    model=self.default_model,
                    response_time_ms=response_time,
                    token_usage={
                        "prompt_tokens": self.estimate_tokens(prompt),
                        "completion_tokens": self.estimate_tokens(content),
                        "total_tokens": self.estimate_tokens(prompt + content)
                    },
                    metadata={"huggingface_response": result},
                    query_id=request.query_id
                )
                
        except Exception as e:
            logger.error(f"HuggingFace generation failed: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check HuggingFace health."""
        try:
            session = await self._get_session()
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            async with session.get(
                f"https://api-inference.huggingface.co/models/{self.default_model}",
                headers=headers
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.warning(f"HuggingFace health check failed: {e}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get HuggingFace provider information."""
        return {
            "name": "HuggingFace",
            "provider": LLMProvider.HUGGINGFACE,
            "model": self.default_model,
            "base_url": "https://api-inference.huggingface.co",
            "token_limits": self.token_limits,
            "is_free": True,
            "cost_per_token": 0.0
        }


class OpenAIProvider(LLMProviderInterface):
    """Enhanced OpenAI provider with token limit awareness."""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.session = None
        self.default_model = "gpt-3.5-turbo"
        # OpenAI GPT-3.5 token limits
        self.token_limits = ProviderTokenLimits(
            max_context_tokens=16000,
            max_total_tokens=16000,
            cost_per_1k_tokens=0.002,  # $0.002 per 1K tokens
            is_free=False
        )
    
    async def _get_session(self):
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            import aiohttp
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for OpenAI."""
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def can_handle_request(self, request: LLMRequest) -> bool:
        """Check if OpenAI can handle the request within token limits."""
        total_text = request.query
        if request.context:
            total_text = f"{request.context}\n\n{request.query}"
        if request.system_message:
            total_text = f"{request.system_message}\n\n{total_text}"
        
        estimated_tokens = self.estimate_tokens(total_text) + request.max_tokens
        return estimated_tokens <= self.token_limits.max_total_tokens
    
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text using OpenAI."""
        start_time = time.time()
        session = await self._get_session()
        
        # Check token limits
        if not self.can_handle_request(request):
            raise ValueError(f"Request exceeds OpenAI token limits: {self.token_limits.max_total_tokens}")
        
        # Prepare messages
        messages = []
        if request.system_message:
            messages.append({"role": "system", "content": request.system_message})
        
        # Add context and query
        if request.context:
            messages.append({"role": "user", "content": f"Context: {request.context}\n\nQuery: {request.query}"})
        else:
            messages.append({"role": "user", "content": request.query})
        
        # Prepare request payload
        payload = {
            "model": self.default_model,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens
        }
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers
            ) as response:
                if response.status != 200:
                    raise Exception(f"OpenAI API error: {response.status}")
                
                result = await response.json()
                content = result["choices"][0]["message"]["content"]
                
                response_time = (time.time() - start_time) * 1000
                
                return LLMResponse(
                    content=content,
                    provider=LLMProvider.OPENAI,
                    model=self.default_model,
                    response_time_ms=response_time,
                    token_usage=result.get("usage", {}),
                    metadata={"openai_response": result},
                    query_id=request.query_id
                )
                
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check OpenAI health."""
        try:
            session = await self._get_session()
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            async with session.get(
                "https://api.openai.com/v1/models",
                headers=headers
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {e}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get OpenAI provider information."""
        return {
            "name": "OpenAI",
            "provider": LLMProvider.OPENAI,
            "model": self.default_model,
            "base_url": "https://api.openai.com",
            "token_limits": self.token_limits,
            "is_free": False,
            "cost_per_token": self.token_limits.cost_per_1k_tokens
        }


class EnhancedLLMClient:
    """
    Enhanced LLM client with modular provider selection.
    
    Features:
    - Intelligent provider selection based on query classification
    - Token limit awareness and automatic fallback
    - Comprehensive logging and transparency
    - Health monitoring and automatic failover
    """
    
    def __init__(self):
        """Initialize enhanced LLM client."""
        self.providers: Dict[LLMProvider, LLMProviderInterface] = {}
        self.provider_stats: Dict[LLMProvider, Dict[str, Any]] = {}
        self.query_classifier = None
        
        # Setup providers
        self._setup_providers()
        
        # Initialize statistics
        for provider in self.providers:
            self.provider_stats[provider] = {
                "calls": 0,
                "success": 0,
                "failures": 0,
                "avg_time": 0.0,
                "last_used": None
            }
        
        logger.info("✅ EnhancedLLMClient initialized successfully")
    
    def _setup_providers(self):
        """Setup available providers based on environment configuration."""
        # Ollama provider (local, free)
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        if os.getenv("OLLAMA_ENABLED", "true").lower() == "true":
            ollama_config = ProviderConfig(
                name=LLMProvider.OLLAMA,
                base_url=ollama_url,
                api_key=None,
                models=["llama3.2:3b", "mistral:7b"],
                timeout=60
            )
            self.providers[LLMProvider.OLLAMA] = OllamaProvider(ollama_config)
            logger.info("✅ Ollama provider configured")
        
        # HuggingFace provider (free API)
        hf_token = os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HUGGINGFACE_WRITE_TOKEN")
        if hf_token:
            hf_config = ProviderConfig(
                name=LLMProvider.HUGGINGFACE,
                base_url="https://api-inference.huggingface.co",
                api_key=hf_token,
                models=["microsoft/DialoGPT-medium", "gpt2"],
                timeout=30
            )
            self.providers[LLMProvider.HUGGINGFACE] = HuggingFaceProvider(hf_config)
            logger.info("✅ HuggingFace provider configured")
        
        # OpenAI provider (paid, fallback)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            openai_config = ProviderConfig(
                name=LLMProvider.OPENAI,
                base_url="https://api.openai.com",
                api_key=openai_key,
                models=["gpt-3.5-turbo", "gpt-4"],
                timeout=30
            )
            self.providers[LLMProvider.OPENAI] = OpenAIProvider(openai_config)
            logger.info("✅ OpenAI provider configured")
        
        if not self.providers:
            logger.warning("⚠️ No LLM providers configured")
    
    async def _classify_query(self, query: str) -> QueryType:
        """Classify the query to determine optimal provider."""
        # Simple heuristic-based classification
        query_lower = query.lower()
        
        # Simple factual queries
        factual_indicators = ["what is", "who is", "when", "where", "how many", "define", "explain"]
        if any(indicator in query_lower for indicator in factual_indicators):
            return QueryType.SIMPLE_FACTUAL
        
        # Complex synthesis queries
        synthesis_indicators = ["analyze", "compare", "research", "study", "investigate", "synthesize"]
        if any(indicator in query_lower for indicator in synthesis_indicators):
            return QueryType.COMPLEX_SYNTHESIS
        
        # Large context queries
        if len(query) > 500:  # Long queries likely need more context
            return QueryType.LARGE_CONTEXT
        
        return QueryType.UNKNOWN
    
    async def select_llm_provider(self, query: str, context_size: int = 0) -> LLMProvider:
        """
        Select the best LLM provider based on query classification and context size.
        
        Args:
            query: The user query
            context_size: Size of context in tokens
            
        Returns:
            Selected LLM provider
        """
        # Classify query
        query_type = await self._classify_query(query)
        
        # Estimate total tokens needed
        estimated_query_tokens = len(query.split()) * 1.3  # Rough estimation
        total_tokens_needed = estimated_query_tokens + context_size + 1000  # Buffer for response
        
        logger.info(f"🔍 Query classified as: {query_type.value}")
        logger.info(f"📊 Estimated tokens needed: {total_tokens_needed}")
        
        # Provider selection logic
        if query_type == QueryType.SIMPLE_FACTUAL:
            # Try Ollama first (local, free, fast)
            if LLMProvider.OLLAMA in self.providers:
                provider = self.providers[LLMProvider.OLLAMA]
                if provider.can_handle_request(LLMRequest(query=query, max_tokens=1000)):
                    logger.info(f"🎯 Selected LLM Provider: Ollama for simple factual query")
                    return LLMProvider.OLLAMA
            
            # Fallback to HuggingFace
            if LLMProvider.HUGGINGFACE in self.providers:
                provider = self.providers[LLMProvider.HUGGINGFACE]
                if provider.can_handle_request(LLMRequest(query=query, max_tokens=1000)):
                    logger.info(f"🎯 Selected LLM Provider: HuggingFace for simple factual query")
                    return LLMProvider.HUGGINGFACE
        
        elif query_type == QueryType.COMPLEX_SYNTHESIS:
            # Try HuggingFace first (good for research, free)
            if LLMProvider.HUGGINGFACE in self.providers:
                provider = self.providers[LLMProvider.HUGGINGFACE]
                if provider.can_handle_request(LLMRequest(query=query, max_tokens=1000)):
                    logger.info(f"🎯 Selected LLM Provider: HuggingFace for complex synthesis")
                    return LLMProvider.HUGGINGFACE
            
            # Fallback to OpenAI
            if LLMProvider.OPENAI in self.providers:
                provider = self.providers[LLMProvider.OPENAI]
                if provider.can_handle_request(LLMRequest(query=query, max_tokens=1000)):
                    logger.info(f"🎯 Selected LLM Provider: OpenAI for complex synthesis")
                    return LLMProvider.OPENAI
        
        # Large context or fallback - use OpenAI
        if LLMProvider.OPENAI in self.providers:
            provider = self.providers[LLMProvider.OPENAI]
            if provider.can_handle_request(LLMRequest(query=query, max_tokens=1000)):
                logger.info(f"🎯 Selected LLM Provider: OpenAI for large context/fallback")
                return LLMProvider.OPENAI
        
        # Final fallback chain
        for provider_name in [LLMProvider.OLLAMA, LLMProvider.HUGGINGFACE, LLMProvider.OPENAI]:
            if provider_name in self.providers:
                logger.info(f"🎯 Selected LLM Provider: {provider_name.value} (fallback)")
                return provider_name
        
        raise Exception("No LLM providers available")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    async def dispatch(self, query: str, context: Optional[str] = None, **kwargs) -> LLMResponse:
        """
        Dispatch a query to the best LLM provider with intelligent fallback.
        
        Args:
            query: The user query
            context: Optional context information
            **kwargs: Additional parameters for the request
        
        Returns:
            LLMResponse: The generated response
        """
        start_time = time.time()
        query_id = kwargs.get("query_id", hashlib.md5(query.encode()).hexdigest()[:8])
        
        # Create request
        request = LLMRequest(
            query=query,
            context=context,
            max_tokens=kwargs.get("max_tokens", 1000),
            temperature=kwargs.get("temperature", 0.2),
            system_message=kwargs.get("system_message"),
            metadata=kwargs.get("metadata", {}),
            query_id=query_id
        )
        
        # Estimate context size
        context_size = 0
        if context:
            context_size = len(context.split()) * 1.3
        
        # Select provider
        selected_provider = await self.select_llm_provider(query, context_size)
        logger.info(f"Selected LLM Provider: {selected_provider.value} for query: {query_id}")
        
        # Try the selected provider
        try:
            provider = self.providers[selected_provider]
            
            # Check if provider is healthy
            if not await provider.health_check():
                logger.warning(f"⚠️ Provider {selected_provider.value} is not healthy, trying fallback")
                raise Exception(f"Provider {selected_provider.value} health check failed")
            
            # Generate response
            response = await provider.generate_text(request)
            
            # Update statistics
            self.provider_stats[selected_provider]["calls"] += 1
            self.provider_stats[selected_provider]["success"] += 1
            self.provider_stats[selected_provider]["avg_time"] = (
                (self.provider_stats[selected_provider]["avg_time"] * 
                 (self.provider_stats[selected_provider]["calls"] - 1) + 
                 response.response_time_ms) / self.provider_stats[selected_provider]["calls"]
            )
            self.provider_stats[selected_provider]["last_used"] = time.time()
            
            # Log success
            logger.info(f"✅ Generated response using {selected_provider.value} in {response.response_time_ms:.2f}ms")
            logger.info(f"Selected LLM Provider: {selected_provider.value} for query: {query_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Provider {selected_provider.value} failed: {e}")
            
            # Update failure statistics
            self.provider_stats[selected_provider]["calls"] += 1
            self.provider_stats[selected_provider]["failures"] += 1
            
            # Try fallback providers
            fallback_providers = [p for p in [LLMProvider.OLLAMA, LLMProvider.HUGGINGFACE, LLMProvider.OPENAI] 
                                if p != selected_provider and p in self.providers]
            
            for fallback_provider in fallback_providers:
                try:
                    logger.info(f"🔄 Trying fallback provider: {fallback_provider.value}")
                    provider = self.providers[fallback_provider]
                    
                    if await provider.health_check():
                        response = await provider.generate_text(request)
                        
                        # Update statistics
                        self.provider_stats[fallback_provider]["calls"] += 1
                        self.provider_stats[fallback_provider]["success"] += 1
                        self.provider_stats[fallback_provider]["avg_time"] = (
                            (self.provider_stats[fallback_provider]["avg_time"] * 
                             (self.provider_stats[fallback_provider]["calls"] - 1) + 
                             response.response_time_ms) / self.provider_stats[fallback_provider]["calls"]
                        )
                        self.provider_stats[fallback_provider]["last_used"] = time.time()
                        
                        logger.info(f"✅ Fallback successful using {fallback_provider.value}")
                        logger.info(f"Selected LLM Provider: {fallback_provider.value} for query: {query_id}")
                        
                        return response
                        
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback provider {fallback_provider.value} also failed: {fallback_error}")
                    self.provider_stats[fallback_provider]["calls"] += 1
                    self.provider_stats[fallback_provider]["failures"] += 1
            
            # All providers failed
            raise Exception(f"All LLM providers failed for query: {query}")
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get comprehensive provider statistics."""
        stats = {}
        for provider, provider_stats in self.provider_stats.items():
            stats[provider.value] = {
                "calls": provider_stats["calls"],
                "success": provider_stats["success"],
                "failures": provider_stats["failures"],
                "success_rate": provider_stats["success"] / max(provider_stats["calls"], 1),
                "avg_time_ms": provider_stats["avg_time"],
                "last_used": provider_stats["last_used"]
            }
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all providers."""
        health_status = {}
        for provider_name, provider in self.providers.items():
            try:
                is_healthy = await provider.health_check()
                health_status[provider_name.value] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "info": provider.get_provider_info()
                }
            except Exception as e:
                health_status[provider_name.value] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return health_status


def get_enhanced_llm_client() -> EnhancedLLMClient:
    """Get enhanced LLM client instance."""
    return EnhancedLLMClient()


async def dispatch_query(query: str, context: Optional[str] = None, **kwargs) -> LLMResponse:
    """Convenience function to dispatch a query."""
    client = get_enhanced_llm_client()
    return await client.dispatch(query, context, **kwargs)


async def generate_text(prompt: str, **kwargs) -> str:
    """Convenience function to generate text."""
    response = await dispatch_query(prompt, **kwargs)
    return response.content 