#!/usr/bin/env python3
"""
SarvanOM Universal Knowledge Platform - Real LLM Integration
Consolidated from all LLM client implementations with best features.

This is the UNIFIED LLM processor implementing:
- Multi-provider support (OpenAI, Anthropic, Ollama, HuggingFace)
- Intelligent fallback chains (local → free → paid)
- Query classification and dynamic routing
- Zero-budget optimization with free-tier APIs
- Real-time performance monitoring
- Comprehensive error handling and retry logic
- LLM Router Hardening with provider order gating, timeouts, retries, and exponential backoff

Based on Sarvanom_blueprint.md specifications for multi-agent AI orchestration.
"""

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if present
except ImportError:
    pass  # dotenv not installed, continue without it

import asyncio
import json
import time
import hashlib
import re
import uuid
import logging
from typing import Dict, Any, List, Optional, Union
import os
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

# Import observability functions
try:
    from services.gateway.middleware.observability import (
        log_provider_metrics,
        get_metrics_collector
    )
    OBSERVABILITY_AVAILABLE = True
except ImportError:
    OBSERVABILITY_AVAILABLE = False

# LLM Integration with fallback imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

import requests

# Central registry import
from services.gateway.providers import register, get_ordered_providers

# GPU Provider Orchestration
from services.gateway.providers.gpu_providers import (
    gpu_orchestrator, 
    LLMRequest as GPURequest, 
    LLMResponse as GPUResponse,
    ProviderType
)

"""
At startup, ensure provider singletons are constructed and registered.
If your code already creates them elsewhere, import and register them there instead.
Example (pseudocode):
    from .clients.openai_client import OpenAIClient
    register("openai", OpenAIClient)
"""

# Configuration from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "30"))
OLLAMA_DEFAULT_MODEL = os.getenv("OLLAMA_DEFAULT_MODEL", "llama3")

# Zero-budget optimization flags
PRIORITIZE_FREE_MODELS = os.getenv("PRIORITIZE_FREE_MODELS", "true").lower() == "true"
USE_DYNAMIC_SELECTION = os.getenv("USE_DYNAMIC_SELECTION", "true").lower() == "true"
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "15"))

# LLM Router Hardening Configuration
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))
LLM_BASE_TIMEOUT = int(os.getenv("LLM_BASE_TIMEOUT", "10"))
LLM_EXPONENTIAL_BACKOFF_BASE = float(os.getenv("LLM_EXPONENTIAL_BACKOFF_BASE", "2.0"))
LLM_EXPONENTIAL_BACKOFF_MAX = float(os.getenv("LLM_EXPONENTIAL_BACKOFF_MAX", "30.0"))

# Setup structured logging
logger = logging.getLogger(__name__)

# LLM Router Hardening Configuration
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))
LLM_BASE_TIMEOUT = int(os.getenv("LLM_BASE_TIMEOUT", "10"))
LLM_EXPONENTIAL_BACKOFF_BASE = float(os.getenv("LLM_EXPONENTIAL_BACKOFF_BASE", "2.0"))
LLM_EXPONENTIAL_BACKOFF_MAX = float(os.getenv("LLM_EXPONENTIAL_BACKOFF_MAX", "30.0"))

# Setup structured logging
logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers with zero-budget optimization."""
    OLLAMA = "ollama"      # Local models (free)
    HUGGINGFACE = "huggingface"  # Free tier API
    OPENAI = "openai"      # Paid (fallback)
    ANTHROPIC = "anthropic"  # Paid (fallback)
    LOCAL_STUB = "local_stub"  # Stub response when no providers available
    MOCK = "mock"          # Testing fallback


class QueryComplexity(str, Enum):
    """Query complexity levels for dynamic routing."""
    SIMPLE_FACTUAL = "simple_factual"
    RESEARCH_SYNTHESIS = "research_synthesis"
    COMPLEX_REASONING = "complex_reasoning"


class LLMModel(str, Enum):
    """Comprehensive LLM model catalog from all implementations."""
    # OpenAI models (Latest 2025)
    OPENAI_GPT_4O = "gpt-4o"  # Latest multimodal model (Dec 2024+)
    OPENAI_GPT_4O_MINI = "gpt-4o-mini"  # Cost-efficient latest model
    OPENAI_GPT_4_TURBO = "gpt-4-turbo"  # Updated stable version
    OPENAI_GPT_4 = "gpt-4"
    OPENAI_O1_PREVIEW = "o1-preview"  # Latest reasoning model (Sept 2024+)
    OPENAI_O1_MINI = "o1-mini"  # Efficient reasoning model
    
    # Anthropic models (Latest 2025)
    ANTHROPIC_CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"  # Latest Claude 3.5 Sonnet (Oct 2024+)
    ANTHROPIC_CLAUDE_3_5_HAIKU = "claude-3-5-haiku-20241022"    # Latest Claude 3.5 Haiku (Oct 2024+) 
    ANTHROPIC_CLAUDE_3_OPUS = "claude-3-opus-20240229"          # Still latest Opus
    ANTHROPIC_CLAUDE_3_SONNET = "claude-3-sonnet-20240229"      # Legacy Sonnet
    ANTHROPIC_CLAUDE_3_HAIKU = "claude-3-haiku-20240307"        # Legacy Haiku
    
    # Local Ollama models (free)
    OLLAMA_LLAMA2 = "llama2"
    OLLAMA_LLAMA2_7B = "llama2:7b"
    OLLAMA_LLAMA2_13B = "llama2:13b"
    OLLAMA_LLAMA3 = "llama3"
    OLLAMA_LLAMA3_7B = "llama3:7b"
    OLLAMA_LLAMA3_13B = "llama3:13b"
    OLLAMA_MISTRAL = "mistral"
    OLLAMA_CODELLAMA = "codellama"
    
    # HuggingFace free models
    HF_DIALOGPT_MEDIUM = "microsoft/DialoGPT-medium"
    HF_DIALOGPT_LARGE = "microsoft/DialoGPT-large"
    HF_DISTILGPT2 = "distilgpt2"
    HF_GPT_NEO_125M = "EleutherAI/gpt-neo-125M"
    HF_LLAMA_2_7B = "meta-llama/Llama-2-7b-hf"
    HF_FALCON_7B = "tiiuae/falcon-7b"
    
    # Fallback
    MOCK_MODEL = "mock"


class EmbeddingModel(str, Enum):
    """Supported embedding models."""
    OPENAI_TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    OPENAI_TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    SENTENCE_TRANSFORMERS = "all-MiniLM-L6-v2"


@dataclass
class LLMRequest:
    """Unified LLM request structure."""
    prompt: str
    system_message: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.2
    complexity: QueryComplexity = QueryComplexity.RESEARCH_SYNTHESIS
    prefer_free: bool = True
    timeout: int = 15
    trace_id: Optional[str] = None


@dataclass
class LLMResponse:
    """Structured LLM response with metadata."""
    content: str
    provider: LLMProvider
    model: str
    latency_ms: float
    success: bool
    error_message: Optional[str] = None
    trace_id: Optional[str] = None
    attempt: int = 1
    retries: int = 0


@dataclass
class ProviderConfig:
    """Configuration for each LLM provider."""
    provider: LLMProvider
    timeout_s: int
    max_retries: int
    priority: int
    enabled: bool = True
    api_key_required: bool = True
    api_key: Optional[str] = None
    trace_id: Optional[str] = None


@dataclass
class LLMResponse:
    """Structured LLM response with metadata."""
    content: str
    provider: LLMProvider
    model: str
    latency_ms: float
    success: bool
    error_message: Optional[str] = None
    trace_id: Optional[str] = None
    attempt: int = 1
    retries: int = 0


@dataclass
class ProviderConfig:
    """Configuration for each LLM provider."""
    provider: LLMProvider
    timeout_s: int
    max_retries: int
    priority: int
    enabled: bool = True
    api_key_required: bool = True
    api_key: Optional[str] = None


class RealLLMProcessor:
    """Real LLM processing with multiple provider support and router hardening."""
    
    def __init__(self):
        self.setup_provider_registry()
        self.setup_provider_configs()
        self.last_used_provider = None
        self.gpu_orchestrator = gpu_orchestrator
    
    def setup_provider_registry(self):
        """Setup LLM provider registry with zero-budget optimization."""
        try:
            from services.gateway.providers import PROVIDERS, get_available_providers
            
            self.provider_registry = PROVIDERS
            self.available_providers = get_available_providers()
            self.provider_health = {}
            
            # Initialize provider health status
            for provider_name in self.available_providers:
                try:
                    provider_class = self.provider_registry.get(provider_name)
                    if provider_class:
                        provider_instance = provider_class()
                        self.provider_health[provider_name] = provider_instance.is_available()
                        logger.info(f"[OK] {provider_name} provider: {'available' if self.provider_health[provider_name] else 'unavailable'}")
                    else:
                        self.provider_health[provider_name] = False
                        logger.warning(f"[ERROR] {provider_name} provider class not found")
                except Exception as e:
                    logger.error(f"Failed to initialize {provider_name} provider: {e}")
                    self.provider_health[provider_name] = False
            
            # Always available fallback options
            self.provider_health["local_stub"] = True
            self.provider_health["mock"] = True
            
            logger.info(f"[INFO] Provider registry initialized with {len(self.available_providers)} providers")
            
        except Exception as e:
            logger.error(f"Failed to setup provider registry: {e}")
            self.provider_registry = {}
            self.available_providers = []
            self.provider_health = {"local_stub": True, "mock": True}
    
    def setup_provider_configs(self):
        """Setup provider configurations with timeout, retries, and priority."""
        self.provider_configs = {}
        
        # Configure available providers from registry
        if "huggingface" in self.available_providers:
            self.provider_configs["huggingface"] = ProviderConfig(
                provider="huggingface",
                timeout_s=LLM_BASE_TIMEOUT,
                max_retries=LLM_MAX_RETRIES,
                priority=1,  # Highest priority for free models
                enabled=True,
                api_key_required=True,
                api_key=HUGGINGFACE_API_KEY
            )
        
        if "ollama" in self.available_providers:
            self.provider_configs["ollama"] = ProviderConfig(
                provider="ollama",
                timeout_s=LLM_BASE_TIMEOUT + 5,  # Slightly longer for local models
                max_retries=LLM_MAX_RETRIES,
                priority=2,
                enabled=True,
                api_key_required=False
            )
        
        if "anthropic" in self.available_providers:
            self.provider_configs["anthropic"] = ProviderConfig(
                provider="anthropic",
                timeout_s=LLM_BASE_TIMEOUT,
                max_retries=LLM_MAX_RETRIES,
                priority=3,
                enabled=True,
                api_key_required=True,
                api_key=ANTHROPIC_API_KEY
            )
        
        if "openai" in self.available_providers:
            self.provider_configs["openai"] = ProviderConfig(
                provider="openai",
                timeout_s=LLM_BASE_TIMEOUT,
                max_retries=LLM_MAX_RETRIES,
                priority=4,
                enabled=True,
                api_key_required=True,
                api_key=OPENAI_API_KEY
            )
        
        # Always available fallback options
        self.provider_configs["local_stub"] = ProviderConfig(
            provider="local_stub",
            timeout_s=1,  # Very fast stub response
            max_retries=0,
            priority=999,  # Lowest priority - only used when all else fails
            enabled=True,
            api_key_required=False
        )
    

    
    def _is_provider_available(self, provider: LLMProvider) -> bool:
        """Check if a provider is available and properly configured."""
        config = self.provider_configs.get(provider)
        if not config or not config.enabled:
            return False
        
        if provider == LLMProvider.HUGGINGFACE:
            return (config.api_key and 
                   config.api_key.strip() and 
                   "your_" not in config.api_key and
                   config.api_key != "disabled")
        
        elif provider == LLMProvider.OPENAI:
            return (config.api_key and 
                   config.api_key.strip() and 
                   "your_" not in config.api_key and
                   config.api_key != "disabled")
        
        elif provider == LLMProvider.ANTHROPIC:
            return (config.api_key and 
                   config.api_key.strip() and 
                   "your_" not in config.api_key and
                   config.api_key != "disabled")
        
        elif provider == LLMProvider.OLLAMA:
            # Check if Ollama is running locally
            try:
                response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
                return response.status_code == 200
            except:
                return False
        
        elif provider == LLMProvider.LOCAL_STUB:
            return True  # Always available
        
        return False
    
    async def _call_llm_with_retry(self, request: LLMRequest, provider: LLMProvider) -> LLMResponse:
        """Call LLM provider with retry logic, exponential backoff, and structured logging."""
        config = self.provider_configs.get(provider)
        if not config:
            return self._create_error_response(provider, "Provider not configured", request.trace_id)
        
        trace_id = request.trace_id or str(uuid.uuid4())
        start_time = time.time()
        
        for attempt in range(1, config.max_retries + 2):  # +2 because we start from 1 and want to include max_retries
            try:
                # Calculate timeout with exponential backoff
                timeout = min(
                    config.timeout_s * (LLM_EXPONENTIAL_BACKOFF_BASE ** (attempt - 1)),
                    LLM_EXPONENTIAL_BACKOFF_MAX
                )
                
                # Log attempt
                logger.info(f"LLM attempt {attempt}/{config.max_retries + 1} for provider {provider.value}", extra={
                    "provider": provider.value,
                    "attempt": attempt,
                    "timeout_s": timeout,
                    "trace_id": trace_id
                })
                
                # Call the specific provider
                if provider == LLMProvider.OLLAMA:
                    content = await self._call_ollama_with_timeout(request.prompt, request.max_tokens, request.temperature, timeout)
                elif provider == LLMProvider.HUGGINGFACE:
                    content = await self._call_huggingface_with_timeout(request.prompt, request.max_tokens, request.temperature, timeout)
                elif provider == LLMProvider.OPENAI:
                    content = await self._call_openai_with_timeout(request.prompt, request.max_tokens, request.temperature, timeout)
                elif provider == LLMProvider.ANTHROPIC:
                    content = await self._call_anthropic_with_timeout(request.prompt, request.max_tokens, request.temperature, timeout)
                elif provider == LLMProvider.LOCAL_STUB:
                    content = self._generate_stub_response(request.prompt)
                else:
                    content = None
                
                # Calculate latency
                latency_ms = (time.time() - start_time) * 1000
                
                if content is not None:
                    # Success
                    logger.info(f"LLM success for provider {provider.value}", extra={
                        "provider": provider.value,
                        "attempt": attempt,
                        "latency_ms": latency_ms,
                        "ok": True,
                        "trace_id": trace_id
                    })
                    
                    self.last_used_provider = provider
                    return LLMResponse(
                        content=content,
                        provider=provider,
                        model=self._get_model_name(provider),
                        latency_ms=latency_ms,
                        success=True,
                        trace_id=trace_id,
                        attempt=attempt,
                        retries=attempt - 1
                    )
                else:
                    # Provider returned None - treat as error
                    raise Exception(f"Provider {provider.value} returned None")
                    
            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                error_msg = str(e)
                
                # Log error
                logger.warning(f"LLM attempt {attempt} failed for provider {provider.value}: {error_msg}", extra={
                    "provider": provider.value,
                    "attempt": attempt,
                    "latency_ms": latency_ms,
                    "ok": False,
                    "error": error_msg,
                    "trace_id": trace_id
                })
                
                # If this was the last attempt, return error response
                if attempt >= config.max_retries + 1:
                    return LLMResponse(
                        content="",
                        provider=provider,
                        model=self._get_model_name(provider),
                        latency_ms=latency_ms,
                        success=False,
                        error_message=error_msg,
                        trace_id=trace_id,
                        attempt=attempt,
                        retries=attempt - 1
                    )
                
                # Wait before retry (exponential backoff)
                if attempt < config.max_retries + 1:
                    wait_time = min(
                        LLM_EXPONENTIAL_BACKOFF_BASE ** (attempt - 1),
                        LLM_EXPONENTIAL_BACKOFF_MAX
                    )
                    await asyncio.sleep(wait_time)
        
        # Should never reach here, but just in case
        return self._create_error_response(provider, "Max retries exceeded", trace_id)
    
    def _create_error_response(self, provider: LLMProvider, error_msg: str, trace_id: str) -> LLMResponse:
        """Create error response for failed LLM calls."""
        return LLMResponse(
            content="",
            provider=provider,
            model=self._get_model_name(provider),
            latency_ms=0,
            success=False,
            error_message=error_msg,
            trace_id=trace_id,
            attempt=0,
            retries=0
        )
    
    def _get_model_name(self, provider: LLMProvider) -> str:
        """Get model name for provider."""
        model_map = {
            LLMProvider.OPENAI: "gpt-4o-mini",
            LLMProvider.ANTHROPIC: "claude-3-5-haiku-20241022",
            LLMProvider.OLLAMA: "deepseek-r1:8b",
            LLMProvider.HUGGINGFACE: "distilgpt2",
            LLMProvider.LOCAL_STUB: "local_stub",
            LLMProvider.MOCK: "mock"
        }
        return model_map.get(provider, "unknown")
    
    def _generate_stub_response(self, prompt: str) -> str:
        """Generate a stub response when no providers are available."""
        return f"""I'm currently unable to process your request: "{prompt[:100]}{'...' if len(prompt) > 100 else ''}"

This is a stub response (provider=local_stub) because no LLM providers are currently available. Please check your API keys and try again later.

For immediate assistance, you can:
1. Verify your API keys are properly configured
2. Check your internet connection
3. Try again in a few moments

If the problem persists, please contact support."""
    
    async def _call_ollama_with_timeout(self, prompt: str, max_tokens: int, temperature: float, timeout: float) -> Optional[str]:
        """Call Ollama with timeout."""
        try:
            selected_model = self._select_ollama_model(prompt, max_tokens)
            
            if AIOHTTP_AVAILABLE:
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "model": selected_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": min(max_tokens, 150),
                            "stop": ["\n\n", "Human:", "Assistant:"],
                            "num_ctx": 1024
                        }
                    }
                    
                    timeout_obj = aiohttp.ClientTimeout(total=timeout)
                    
                    async with session.post(
                        f"{OLLAMA_BASE_URL}/api/generate",
                        json=payload,
                        timeout=timeout_obj
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            response_text = result.get("response", "")
                            if response_text:
                                return self._sanitize_response(response_text)
            else:
                # Fallback to requests
                response = requests.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": selected_model,
                        "prompt": prompt,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens
                        }
                    },
                    timeout=timeout
                )
                if response.status_code == 200:
                    result = response.json()
                    return self._sanitize_response(result.get("response", ""))
        except Exception as e:
            logger.error(f"Ollama call failed: {e}")
        
        return None
    
    async def _call_huggingface_with_timeout(self, prompt: str, max_tokens: int, temperature: float, timeout: float) -> Optional[str]:
        """Call HuggingFace with timeout."""
        try:
            from services.gateway.huggingface_integration import huggingface_integration
            
            model_name = self._select_huggingface_model(prompt, max_tokens)
            
            # Use the comprehensive HuggingFace integration
            response = await asyncio.wait_for(
                huggingface_integration.generate_text(
                    prompt=prompt,
                    model_name=model_name,
                    max_length=max_tokens,
                    temperature=temperature
                ),
                timeout=timeout
            )
            
            return response.result
            
        except asyncio.TimeoutError:
            logger.error(f"HuggingFace call timed out after {timeout}s")
        except Exception as e:
            logger.error(f"HuggingFace call failed: {e}")
        
        return None
    
    async def _call_openai_with_timeout(self, prompt: str, max_tokens: int, temperature: float, timeout: float) -> Optional[str]:
        """Call OpenAI with timeout."""
        try:
            if not OPENAI_AVAILABLE or not OPENAI_API_KEY:
                return None
                
            # Select optimal accessible model based on task complexity (2025 models)
            if len(prompt) > 1000 or "reasoning" in prompt.lower() or "complex" in prompt.lower():
                model = "gpt-4o"  # Latest multimodal model for complex tasks
            elif max_tokens > 1000:
                model = "gpt-4o"  # Latest multimodal model for long responses
            else:
                model = "gpt-4o-mini"  # Cost-efficient latest model for standard tasks
            
            # Use the pre-configured OpenAI client with latest models
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                ),
                timeout=timeout
            )
            return response.choices[0].message.content
        except asyncio.TimeoutError:
            logger.error(f"OpenAI call timed out after {timeout}s")
        except Exception as e:
            logger.error(f"OpenAI call failed: {e}")
        
        return None
    
    async def _call_anthropic_with_timeout(self, prompt: str, max_tokens: int, temperature: float, timeout: float) -> Optional[str]:
        """Call Anthropic with timeout."""
        try:
            # Select optimal latest Claude model based on task complexity (2025 models)
            if len(prompt) > 1000 or max_tokens > 1000:
                model = "claude-3-5-sonnet-20241022"  # Latest Claude 3.5 Sonnet for complex tasks
            else:
                model = "claude-3-5-haiku-20241022"   # Latest Claude 3.5 Haiku for efficient tasks
            
            message = await asyncio.wait_for(
                asyncio.to_thread(
                    self.anthropic_client.messages.create,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}]
                ),
                timeout=timeout
            )
            return message.content[0].text
        except asyncio.TimeoutError:
            logger.error(f"Anthropic call timed out after {timeout}s")
        except Exception as e:
            logger.error(f"Anthropic call failed: {e}")
        
        return None
    
    def _select_ollama_model(self, prompt: str, max_tokens: int) -> str:
        """Select optimal Ollama model based on query characteristics."""
        prompt_lower = prompt.lower()
        
        # Use available DeepSeek R1 model for all tasks (it's currently the only available model)
        # DeepSeek R1 is a powerful reasoning model that can handle various tasks well
        return "deepseek-r1:8b"
    
    def classify_query_complexity(self, query: str) -> QueryComplexity:
        """
        Advanced query complexity classification.
        
        Extracted and enhanced from shared/core/query_classifier.py and 
        shared/core/model_selector.py for better accuracy.
        """
        if not query or len(query.strip()) < 3:
            return QueryComplexity.SIMPLE_FACTUAL
        
        query_lower = query.lower()
        complexity_score = 0.0
        
        # Advanced pattern matching (extracted from query_classifier.py)
        
        # Complex reasoning indicators (high weight)
        complex_patterns = [
            r'\b(analyze|synthesize|evaluate|compare)\b.*\b(between|against|versus)\b',
            r'\bmulti[- ]?step\b',
            r'\b(comprehensive|thorough|detailed)\s+(analysis|review|evaluation)\b',
            r'\b(pros\s+and\s+cons|advantages\s+and\s+disadvantages)\b',
            r'\b(framework|methodology|approach|strategy)\b.*\b(develop|create|design)\b'
        ]
        
        for pattern in complex_patterns:
            if re.search(pattern, query_lower):
                complexity_score += 2.0
        
        # Research synthesis indicators (medium weight)
        research_patterns = [
            r'\b(research|study|findings|evidence|literature)\b',
            r'\b(recent|latest|current)\s+(research|developments|trends)\b',
            r'\b(academic|scientific|peer[- ]?reviewed)\b',
            r'\b(correlation|causation|relationship)\s+between\b',
            r'\b(survey|review|meta[- ]?analysis)\b'
        ]
        
        for pattern in research_patterns:
            if re.search(pattern, query_lower):
                complexity_score += 1.5
        
        # Analytical indicators (medium weight)
        analytical_patterns = [
            r'\bhow\s+(does|do|did)\b.*\bwork\b',
            r'\bwhy\s+(is|are|was|were|does|do)\b',
            r'\bexplain\s+the\s+(reason|process|mechanism)\b',
            r'\b(cause|effect|impact|consequence)\b.*\bof\b'
        ]
        
        for pattern in analytical_patterns:
            if re.search(pattern, query_lower):
                complexity_score += 1.0
        
        # Simple factual indicators (low weight)
        simple_patterns = [
            r'^\s*what\s+is\b',
            r'^\s*who\s+is\b', 
            r'^\s*when\s+(is|was|will)\b',
            r'^\s*where\s+(is|was|can)\b',
            r'^\s*(define|list|name)\b',
            r'^\s*how\s+many\b'
        ]
        
        for pattern in simple_patterns:
            if re.search(pattern, query_lower):
                complexity_score -= 0.5
        
        # Query length and structure analysis (from model_selector.py)
        words = query.split()
        word_count = len(words)
        
        if word_count > 50:
            complexity_score += 1.0
        elif word_count > 20:
            complexity_score += 0.5
        elif word_count < 5:
            complexity_score -= 0.5
        
        # Technical indicators
        technical_terms = ['api', 'algorithm', 'database', 'implementation', 'architecture', 'code', 'programming']
        if any(term in query_lower for term in technical_terms):
            complexity_score += 0.5
        
        # Classification based on score
        if complexity_score >= 2.0:
            return QueryComplexity.COMPLEX_REASONING
        elif complexity_score >= 0.5:
            return QueryComplexity.RESEARCH_SYNTHESIS
        else:
            return QueryComplexity.SIMPLE_FACTUAL
    
    def select_optimal_provider(self, complexity: QueryComplexity, prefer_free: bool = True) -> LLMProvider:
        """
        Dynamic provider selection using centralized registry.
        
        Uses environment-driven provider order with proper fallback chain.
        """
        if not USE_DYNAMIC_SELECTION:
            return self._get_fallback_provider()
        
        # Use centralized, env-driven order
        ordered = get_ordered_providers()
        if not ordered:
            logger.warning("❌ No providers in registry - using local_stub")
            return LLMProvider.LOCAL_STUB
        
        # Return first available provider from ordered registry
        for provider_name, provider in ordered.items():
            if self._is_provider_available(LLMProvider(provider_name)):
                logger.info(f"🚀 Selected {provider_name} from registry")
                return LLMProvider(provider_name)
        
        # Fallback to local stub if no providers available
        logger.warning("❌ No providers available - using local_stub")
        return LLMProvider.LOCAL_STUB
    
    def _get_available_providers(self) -> List[LLMProvider]:
        """Get list of available providers in order of preference."""
        available = []
        
        # Check HuggingFace (free tier)
        if self._is_provider_available(LLMProvider.HUGGINGFACE):
            available.append(LLMProvider.HUGGINGFACE)
        
        # Check Ollama (local)
        if self._is_provider_available(LLMProvider.OLLAMA):
            available.append(LLMProvider.OLLAMA)
        
        # Check Anthropic (paid)
        if self._is_provider_available(LLMProvider.ANTHROPIC):
            available.append(LLMProvider.ANTHROPIC)
        
        # Check OpenAI (paid)
        if self._is_provider_available(LLMProvider.OPENAI):
            available.append(LLMProvider.OPENAI)
        
        return available
    
    async def get_gpu_provider_health(self) -> Dict[str, Any]:
        """Get health status of all GPU providers with circuit breaker info."""
        try:
            health_status = await self.gpu_orchestrator.get_provider_health()
            
            # Convert to API-friendly format
            formatted_health = {}
            for provider_name, health in health_status.items():
                formatted_health[provider_name] = {
                    "status": health.status.value,
                    "last_check": health.last_check.isoformat(),
                    "latency_ms": health.latency_ms,
                    "error_count": health.error_count,
                    "success_count": health.success_count,
                    "circuit_open_until": health.circuit_open_until.isoformat() if health.circuit_open_until else None,
                    "last_error": health.last_error
                }
            
            return {
                "providers": formatted_health,
                "available_providers": self.gpu_orchestrator.get_available_providers(),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get GPU provider health: {e}")
            return {
                "providers": {},
                "available_providers": [],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_fallback_provider(self) -> LLMProvider:
        """Get best available fallback provider using dynamic selection."""
        available_providers = self._get_available_providers()
        
        if not available_providers:
            logger.warning("❌ No providers available - using local_stub")
            return LLMProvider.LOCAL_STUB
        
        # Return first available provider
        selected = available_providers[0]
        logger.info(f"🔄 Using {selected.value} as fallback provider")
        return selected
    
    async def call_llm_with_provider_gating(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.2, prefer_free: bool = True) -> LLMResponse:
        """
        Call LLM with GPU provider orchestration and automatic fallback.
        
        This method uses the new GPU orchestrator with:
        - Free GPU prioritization (ollama_local, remote_gpu, huggingface)
        - Circuit breaker pattern (3 failures → skip 5 min)
        - Health checks with latency monitoring
        - Timeout handling (15s per call)
        - Automatic fallback to stub response
        """
        # Use GPU orchestrator for free GPU orchestration
        gpu_request = GPURequest(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=LLM_TIMEOUT_SECONDS
        )
        
        try:
            gpu_response = await self.gpu_orchestrator.complete_request(gpu_request)
            
            # Record provider metrics
            if OBSERVABILITY_AVAILABLE:
                log_provider_metrics(
                    trace_id=gpu_response.trace_id or "unknown",
                    provider=gpu_response.provider.value,
                    latency_ms=gpu_response.latency_ms,
                    success=gpu_response.success,
                    tokens=len(gpu_response.content.split()) if gpu_response.content else 0,
                    cost=0.0  # GPU calls are free
                )
            
            # Convert GPU response to legacy format
            return LLMResponse(
                content=gpu_response.content,
                provider=LLMProvider(gpu_response.provider.value),
                model=gpu_response.model,
                latency_ms=gpu_response.latency_ms,
                success=gpu_response.success,
                error_message=gpu_response.error_message,
                trace_id=gpu_response.trace_id,
                attempt=gpu_response.attempt,
                retries=0
            )
        except Exception as e:
            logger.error(f"GPU orchestrator failed: {e}")
            # Fallback to legacy method
            return await self._call_llm_with_provider_gating_legacy(prompt, max_tokens, temperature, prefer_free)
    
    async def _call_llm_with_provider_gating_legacy(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.2, prefer_free: bool = True) -> LLMResponse:
        """
        Call LLM with provider order gating, automatic fallback to stub responses.
        
        This method implements the LLM router hardening requirements:
        - Provider order gating with PRIORITIZE_FREE_MODELS=true by default
        - Timeout, max_retries, exponential backoff per provider
        - Automatic fallback to stub response if no API keys available
        - Structured logging with {provider, attempt, latency_ms, ok} and trace_id
        - Never hangs - always returns a response within 2s for stub
        """
        trace_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Get provider order based on preferences using centralized utility
        base_order = get_provider_order()
        provider_order = []
        for provider_name in base_order:
            try:
                provider = LLMProvider(provider_name)
                config = self.provider_configs.get(provider)
                if config and config.enabled and self._is_provider_available(provider):
                    provider_order.append(provider)
            except ValueError:
                # Skip unknown providers
                continue
        
        if not provider_order:
            # No providers available - return stub immediately
            logger.warning("No LLM providers available - returning stub response", extra={
                "provider": "local_stub",
                "attempt": 1,
                "latency_ms": 0,
                "ok": True,
                "trace_id": trace_id
            })
            
            return LLMResponse(
                content=self._generate_stub_response(prompt),
                provider=LLMProvider.LOCAL_STUB,
                model="local_stub",
                latency_ms=0,
                success=True,
                trace_id=trace_id,
                attempt=1,
                retries=0
            )
        
        # Try providers in order until one succeeds
        for i, provider in enumerate(provider_order):
            try:
                logger.info(f"Trying provider {provider.value} (attempt {i+1}/{len(provider_order)})", extra={
                    "provider": provider.value,
                    "attempt": i+1,
                    "trace_id": trace_id
                })
                
                request = LLMRequest(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    prefer_free=prefer_free,
                    trace_id=trace_id
                )
                
                response = await self._call_llm_with_retry(request, provider)
                
                if response.success:
                    # Success - log and return
                    logger.info(f"LLM call successful with {provider.value}", extra={
                        "provider": provider.value,
                        "attempt": i+1,
                        "latency_ms": response.latency_ms,
                        "ok": True,
                        "trace_id": trace_id
                    })
                    return response
                else:
                    # Provider failed - log and continue to next
                    logger.warning(f"Provider {provider.value} failed: {response.error_message}", extra={
                        "provider": provider.value,
                        "attempt": i+1,
                        "latency_ms": response.latency_ms,
                        "ok": False,
                        "error": response.error_message,
                        "trace_id": trace_id
                    })
                    
            except Exception as e:
                # Provider threw exception - log and continue to next
                latency_ms = (time.time() - start_time) * 1000
                logger.error(f"Provider {provider.value} exception: {str(e)}", extra={
                    "provider": provider.value,
                    "attempt": i+1,
                    "latency_ms": latency_ms,
                    "ok": False,
                    "error": str(e),
                    "trace_id": trace_id
                })
        
        # All providers failed - return stub response
        total_latency_ms = (time.time() - start_time) * 1000
        logger.warning("All LLM providers failed - returning stub response", extra={
            "provider": "local_stub",
            "attempt": len(provider_order) + 1,
            "latency_ms": total_latency_ms,
            "ok": True,
            "trace_id": trace_id
        })
        
        return LLMResponse(
            content=self._generate_stub_response(prompt),
            provider=LLMProvider.LOCAL_STUB,
            model="local_stub",
            latency_ms=total_latency_ms,
            success=True,
            trace_id=trace_id,
            attempt=len(provider_order) + 1,
            retries=len(provider_order)
        )
    
    async def search_with_ai(self, query: str, user_id: str = None, max_results: int = 10) -> Dict[str, Any]:
        """Process search query with AI enhancement using optimal provider selection."""
        start_time = time.time()
        
        # Classify query complexity for optimal provider selection
        complexity = self.classify_query_complexity(query)
        selected_provider = self.select_optimal_provider(complexity, prefer_free=True)
        
        # Enhanced search processing with AI
        search_prompt = f"""
        You are an expert research assistant for the SarvanOM Universal Knowledge Platform.
        
        User Query: "{query}"
        Query Complexity: {complexity.value}
        
        Provide a comprehensive search analysis that includes:
        1. Query intent classification (factual, research, comparative, etc.)
        2. Key search terms and concepts to explore
        3. Suggested information sources and databases
        4. Potential follow-up questions for deeper research
        5. Complexity assessment (simple, medium, complex)
        
        Respond in JSON format with structured data.
        """
        
        # Create LLM request with optimal settings
        llm_request = LLMRequest(
            prompt=search_prompt,
            complexity=complexity,
            max_tokens=800,
            timeout=LLM_TIMEOUT_SECONDS
        )
        
        ai_analysis = await self._call_llm_with_retry(llm_request, selected_provider)
        
        # Generate search results with AI-enhanced metadata
        results = self._generate_search_results(query, ai_analysis.content)
        
        processing_time = time.time() - start_time
        
        return {
            "query": query,
            "user_id": user_id,
            "max_results": max_results,
            "processing_time_ms": int(processing_time * 1000),
            "results": results,
            "total_results": len(results),
            "ai_analysis": ai_analysis.content,
            "query_classification": self._extract_classification(ai_analysis.content),
            "complexity_score": complexity.value,
            "selected_provider": selected_provider.value,
            "zero_budget_mode": PRIORITIZE_FREE_MODELS,
            "timestamp": datetime.now().isoformat(),
            "search_strategy": "ai_enhanced_hybrid",
            "trace_id": ai_analysis.trace_id
        }
    
    async def fact_check_with_ai(self, claim: str, sources: List[Dict[str, Any]] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform AI-powered fact-checking."""
        if sources is None:
            sources = []
        
        start_time = time.time()
        
        # Create sources text
        sources_text = "\n".join([f"- {source.get('title', 'Source')}: {source.get('content', source.get('snippet', ''))}" for source in sources[:5]])
        
        fact_check_prompt = f"""
        You are an expert fact-checker for the SarvanOM Universal Knowledge Platform.
        
        Claim to verify: "{claim}"
        Context: {json.dumps(context) if context else "General fact-checking"}
        
        Reference Sources:
        {sources_text}
        
        Perform a comprehensive fact-check analysis:
        1. Assess the verifiability of the claim
        2. Identify key factual elements that can be verified
        3. Determine the claim's accuracy based on available information
        4. Provide confidence score (0.0 to 1.0)
        5. Suggest verification sources and methods
        6. Flag any potential biases or limitations
        
        Respond in JSON format with structured verification data.
        """
        
        ai_verification = await self._call_llm_with_retry(LLMRequest(prompt=fact_check_prompt, max_tokens=1000), self.select_optimal_provider(QueryComplexity.COMPLEX_REASONING))
        
        processing_time = time.time() - start_time
        
        # Extract verification details
        verification_result = self._parse_fact_check_result(ai_verification.content)
        
        return {
            "claim": claim,
            "context": context,
            "verification_status": verification_result.get("status", "analyzed"),
            "confidence_score": verification_result.get("confidence", 0.8),
            "consensus_score": verification_result.get("consensus", 0.75),
            "evidence_sources": verification_result.get("sources", []),
            "verification_details": ai_verification.content,
            "processing_time_ms": int(processing_time * 1000),
            "timestamp": datetime.now().isoformat(),
            "expert_analysis": verification_result.get("analysis", "AI-powered verification completed"),
            "limitations": verification_result.get("limitations", []),
            "follow_up_needed": verification_result.get("follow_up", False),
            "trace_id": ai_verification.trace_id
        }
    
    async def synthesize_with_ai(self, content: str = None, query: str = None, style: str = "default", 
                               sources: List[Any] = None, target_audience: str = None) -> Dict[str, Any]:
        """AI-powered content synthesis and analysis."""
        if sources is None:
            sources = []
        
        # Use query as content if content is not provided
        if content is None and query:
            content = query
        elif content is None:
            content = "General synthesis request"
            
        start_time = time.time()
        
        synthesis_prompt = f"""
        You are an expert knowledge synthesizer for the SarvanOM Universal Knowledge Platform.
        
        Content to synthesize: "{content}"
        Query context: {query or "General synthesis"}
        Target audience: {target_audience or "General audience"}
        Style: {style}
        Sources to consider: {sources or ["general knowledge"]}
        
        Create a comprehensive synthesis that includes:
        1. Executive summary of key points
        2. Detailed analysis and insights
        3. Connections between different concepts
        4. Implications and conclusions
        5. Recommendations for further exploration
        6. Source reliability assessment
        
        Adapt the tone and complexity for the target audience.
        Respond in JSON format with structured synthesis data.
        """
        
        ai_synthesis = await self._call_llm_with_retry(LLMRequest(prompt=synthesis_prompt, max_tokens=1500), self.select_optimal_provider(QueryComplexity.RESEARCH_SYNTHESIS))
        
        # Handle case where LLM call returns None - use enhanced fallback
        if ai_synthesis.content is None:
            ai_synthesis.content = await self._generate_fallback_response(synthesis_prompt)
        
        processing_time = time.time() - start_time
        
        # Parse synthesis results
        synthesis_result = self._parse_synthesis_result(ai_synthesis.content)
        
        return {
            "content": content,
            "query": query,
            "style": style,
            "target_audience": target_audience,
            "sources": sources or [],
            "synthesis": synthesis_result.get("synthesis", synthesis_result.get("response", ai_synthesis.content)),
            "executive_summary": synthesis_result.get("summary", synthesis_result.get("analysis", "AI synthesis completed")),
            "key_insights": synthesis_result.get("insights", synthesis_result.get("key_terms", [])),
            "recommendations": synthesis_result.get("recommendations", synthesis_result.get("suggested_sources", [])),
            "confidence_score": synthesis_result.get("confidence", 0.85),
            "processing_time_ms": int(processing_time * 1000),
            "timestamp": datetime.now().isoformat(),
            "synthesis_method": "multi_agent_ai",
            "quality_score": synthesis_result.get("quality", 0.8),
            "trace_id": ai_synthesis.trace_id
        }
    
    async def _call_llm_with_provider(self, request: LLMRequest, provider: LLMProvider) -> LLMResponse:
        """Call specific LLM provider with router hardening, retry logic, and structured logging."""
        # Use the new router hardening method
        return await self._call_llm_with_retry(request, provider)

    async def _call_llm(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.2) -> LLMResponse:
        """Legacy method - call LLM with automatic provider selection."""
        complexity = self.classify_query_complexity(prompt)
        provider = self.select_optimal_provider(complexity)
        request = LLMRequest(prompt=prompt, max_tokens=max_tokens, temperature=temperature)
        return await self._call_llm_with_provider(request, provider)
    
    async def _call_openai(self, prompt: str, max_tokens: int, temperature: float) -> LLMResponse:
        """Call OpenAI API."""
        try:
            if not OPENAI_AVAILABLE or not OPENAI_API_KEY:
                return self._create_error_response(LLMProvider.OPENAI, "OpenAI API key not configured or invalid", None)
                
            # Select optimal accessible model based on task complexity (2025 models)
            if len(prompt) > 1000 or "reasoning" in prompt.lower() or "complex" in prompt.lower():
                model = "gpt-4o"  # Latest multimodal model for complex tasks
            elif max_tokens > 1000:
                model = "gpt-4o"  # Latest multimodal model for long responses
            else:
                model = "gpt-4o-mini"  # Cost-efficient latest model for standard tasks
            
            # Use the pre-configured OpenAI client with latest models
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=LLM_TIMEOUT_SECONDS
            )
            return LLMResponse(
                content=response.choices[0].message.content,
                provider=LLMProvider.OPENAI,
                model=model,
                latency_ms=0, # This will be calculated by _call_llm_with_provider
                success=True,
                trace_id=None, # Trace ID will be added by _call_llm_with_provider
                attempt=1,
                retries=0
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._create_error_response(LLMProvider.OPENAI, str(e), None)
    
    async def _call_anthropic(self, prompt: str, max_tokens: int, temperature: float) -> LLMResponse:
        """Call Anthropic API."""
        try:
            # Select optimal latest Claude model based on task complexity (2025 models)
            if len(prompt) > 1000 or max_tokens > 1000:
                model = "claude-3-5-sonnet-20241022"  # Latest Claude 3.5 Sonnet for complex tasks
            else:
                model = "claude-3-5-haiku-20241022"   # Latest Claude 3.5 Haiku for efficient tasks
            
            message = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return LLMResponse(
                content=message.content[0].text,
                provider=LLMProvider.ANTHROPIC,
                model=model,
                latency_ms=0, # This will be calculated by _call_llm_with_provider
                success=True,
                trace_id=None, # Trace ID will be added by _call_llm_with_provider
                attempt=1,
                retries=0
            )
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return self._create_error_response(LLMProvider.ANTHROPIC, str(e), None)
    
    def _select_ollama_model(self, prompt: str, max_tokens: int) -> str:
        """Select optimal Ollama model based on query characteristics."""
        prompt_lower = prompt.lower()
        
        # Use available DeepSeek R1 model for all tasks (it's currently the only available model)
        # DeepSeek R1 is a powerful reasoning model that can handle various tasks well
        return "deepseek-r1:8b"

    async def _call_ollama(self, prompt: str, max_tokens: int, temperature: float) -> LLMResponse:
        """Enhanced Ollama integration with intelligent model selection."""
        try:
            # Select optimal model based on query characteristics
            selected_model = self._select_ollama_model(prompt, max_tokens)
            
            if not AIOHTTP_AVAILABLE:
                # Fallback to requests with enhanced error handling
                response = requests.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": selected_model,
                        "prompt": prompt,
                        "options": {
                            "temperature": temperature, 
                            "num_predict": max_tokens,
                            "top_p": 0.9,
                            "top_k": 40
                        }
                    },
                    timeout=OLLAMA_TIMEOUT
                )
                if response.status_code == 200:
                    result = response.json()
                    return LLMResponse(
                        content=result.get("response", ""),
                        provider=LLMProvider.OLLAMA,
                        model=selected_model,
                        latency_ms=0, # This will be calculated by _call_llm_with_provider
                        success=True,
                        trace_id=None, # Trace ID will be added by _call_llm_with_provider
                        attempt=1,
                        retries=0
                    )
                else:
                    # Try fallback model if primary fails
                    if selected_model != "llama3":
                        response = requests.post(
                            f"{OLLAMA_BASE_URL}/api/generate",
                            json={
                                "model": "llama3",
                                "prompt": prompt,
                                "options": {"temperature": temperature, "num_predict": max_tokens}
                            },
                            timeout=OLLAMA_TIMEOUT
                        )
                        if response.status_code == 200:
                            response_text = response.json().get("response", "")
                            return LLMResponse(
                                content=self._sanitize_response(response_text),
                                provider=LLMProvider.OLLAMA,
                                model="llama3",
                                latency_ms=0, # This will be calculated by _call_llm_with_provider
                                success=True,
                                trace_id=None, # Trace ID will be added by _call_llm_with_provider
                                attempt=1,
                                retries=0
                            )
            else:
                async with aiohttp.ClientSession() as session:
                    # Simple, fast payload for quick responses (5 seconds target)
                    payload = {
                        "model": selected_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": min(max_tokens, 150),  # Limit tokens for faster response
                            "stop": ["\n\n", "Human:", "Assistant:"],  # Stop tokens for cleaner responses
                            "num_ctx": 1024  # Smaller context for faster processing
                        }
                    }
                    
                    # Fast timeout for quick responses (5-10 seconds max)
                    timeout = aiohttp.ClientTimeout(total=15)
                    
                    async with session.post(
                        f"{OLLAMA_BASE_URL}/api/generate",
                        json=payload,
                        timeout=timeout
                    ) as response:
                        if response.status == 200:
                            # For non-streaming, expect simple JSON response
                            try:
                                result = await response.json()
                                response_text = result.get("response", "")
                                if response_text:
                                    # Sanitize response to remove problematic characters
                                    sanitized = self._sanitize_response(response_text)
                                    return LLMResponse(
                                        content=sanitized,
                                        provider=LLMProvider.OLLAMA,
                                        model=selected_model,
                                        latency_ms=0, # This will be calculated by _call_llm_with_provider
                                        success=True,
                                        trace_id=None, # Trace ID will be added by _call_llm_with_provider
                                        attempt=1,
                                        retries=0
                                    )
                                else:
                                    logger.warning(f"Ollama empty response: {result}")
                                    return self._create_error_response(LLMProvider.OLLAMA, "Ollama returned empty response", None)
                            except Exception as parse_error:
                                logger.error(f"Ollama JSON parse error: {parse_error}")
                                # Try reading as text
                                text_response = await response.text()
                                logger.warning(f"Ollama raw response: {text_response[:200]}...")
                                return self._create_error_response(LLMProvider.OLLAMA, "Ollama JSON parse error", None)
                        else:
                            error_text = await response.text()
                            logger.error(f"Ollama API error {response.status}: {error_text}")
                            return self._create_error_response(LLMProvider.OLLAMA, f"Ollama API error {response.status}: {error_text}", None)
            return self._create_error_response(LLMProvider.OLLAMA, "Ollama call failed", None)
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return self._create_error_response(LLMProvider.OLLAMA, str(e), None)
    
    async def _call_huggingface(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> LLMResponse:
        """
        Use the comprehensive HuggingFace integration for advanced AI capabilities
        Following MAANG/OpenAI/Perplexity standards
        """
        try:
            # Import the HuggingFace integration
            from services.gateway.huggingface_integration import huggingface_integration
            
            # Select appropriate model based on task
            model_name = self._select_huggingface_model(prompt, max_tokens)
            
            # Use the comprehensive HuggingFace integration
            response = await huggingface_integration.generate_text(
                prompt=prompt,
                model_name=model_name,
                max_length=max_tokens,
                temperature=temperature
            )
            
            # Return the generated text
            return LLMResponse(
                content=response.result,
                provider=LLMProvider.HUGGINGFACE,
                model=model_name,
                latency_ms=0, # This will be calculated by _call_llm_with_provider
                success=True,
                trace_id=None, # Trace ID will be added by _call_llm_with_provider
                attempt=1,
                retries=0
            )
            
        except Exception as e:
            logger.error(f"HuggingFace integration error: {e}")
            # Fallback to basic API if integration fails
            return await self._call_huggingface_fallback(prompt, max_tokens, temperature)
    
    def _select_huggingface_model(self, prompt: str, max_tokens: int) -> str:
        """
        Advanced HuggingFace model selection using available models
        """
        prompt_lower = prompt.lower()
        
        # Use models that are available in the HuggingFace integration
        available_models = {
            "text_generation": ["gpt2", "distilgpt2", "microsoft/DialoGPT-medium"],
            "summarization": ["facebook/bart-large-cnn", "t5-small"],
            "sentiment": ["distilbert-base-uncased-finetuned-sst-2-english"],
            "translation": ["Helsinki-NLP/opus-mt-en-es"],
            "qa": ["distilbert-base-cased-distilled-squad"]
        }
        
        # Text Generation/Creative/Conversational
        if any(term in prompt_lower for term in ['generate', 'create', 'write', 'story', 'creative', 'compose', 'explain', 'describe', 'tell me', 'how does', 'what is']):
            return "distilgpt2"  # Fast and reliable
        
        # Question Answering
        if any(term in prompt_lower for term in ['?', 'question', 'answer', 'who', 'what', 'when', 'where', 'why', 'how']):
            return "distilgpt2"  # Use GPT-2 for Q&A
        
        # Summarization tasks
        if any(term in prompt_lower for term in ['summarize', 'summary', 'key points', 'overview', 'brief']):
            return "distilgpt2"  # GPT-2 can handle summarization
        
        # Complex reasoning
        if len(prompt) > 200 or max_tokens > 300:
            return "microsoft/DialoGPT-medium"  # Larger model for complex tasks
        
        # Default: Fast, reliable model
        return "distilgpt2"
    
    async def _call_huggingface_fallback(self, prompt: str, max_tokens: int, temperature: float) -> LLMResponse:
        """Fallback to verified working HuggingFace models when primary fails."""
        fallback_models = ["gpt2", "distilgpt2"]  # Only use verified working free models
        
        for model in fallback_models:
            try:
                headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
                api_url = f"https://api-inference.huggingface.co/models/{model}"
                
                payload = {
                    "inputs": prompt[:500],  # Truncate for faster models
                    "parameters": {
                        "max_new_tokens": min(max_tokens, 256),
                        "temperature": temperature,
                        "return_full_text": False
                    }
                }
                
                if AIOHTTP_AVAILABLE:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            api_url,
                            headers=headers,
                            json=payload,
                            timeout=aiohttp.ClientTimeout(total=10)  # Shorter timeout for fallback
                        ) as response:
                            if response.status == 200:
                                result = await response.json()
                                parsed = self._parse_huggingface_response(result, model)
                                if parsed:
                                    return LLMResponse(
                                        content=parsed,
                                        provider=LLMProvider.HUGGINGFACE,
                                        model=model,
                                        latency_ms=0, # This will be calculated by _call_llm_with_provider
                                        success=True,
                                        trace_id=None, # Trace ID will be added by _call_llm_with_provider
                                        attempt=1,
                                        retries=0
                                    )
                else:
                    response = requests.post(
                        api_url,
                        headers=headers,
                        json=payload,
                        timeout=10
                    )
                    if response.status_code == 200:
                        result = response.json()
                        parsed = self._parse_huggingface_response(result, model)
                        if parsed:
                            return LLMResponse(
                                content=parsed,
                                provider=LLMProvider.HUGGINGFACE,
                                model=model,
                                latency_ms=0, # This will be calculated by _call_llm_with_provider
                                success=True,
                                trace_id=None, # Trace ID will be added by _call_llm_with_provider
                                attempt=1,
                                retries=0
                            )
            except Exception as e:
                logger.error(f"HuggingFace fallback error with {model}: {e}")
                continue
        
        return self._create_error_response(LLMProvider.HUGGINGFACE, "All HuggingFace fallback models failed", None)
    
    async def _generate_fallback_response(self, prompt: str) -> str:
        """
        Enhanced fallback using HuggingFace free models instead of mock responses.
        Tries multiple HuggingFace models as fallback before giving up.
        """
        fallback_models = [
            "distilgpt2",           # Fast and reliable
            "gpt2",                 # Robust text generation
            "microsoft/DialoGPT-small"  # Conversational
        ]
        
        for model in fallback_models:
            try:
                # Try each fallback model
                if HUGGINGFACE_API_KEY:
                    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
                    api_url = f"https://api-inference.huggingface.co/models/{model}"
                    
                    # Simplified payload for fallback
                    payload = {
                        "inputs": prompt[:200],  # Truncate for fallback
                        "parameters": {
                            "max_new_tokens": 100,
                            "temperature": 0.7,
                            "return_full_text": False
                        }
                    }
                    
                    if AIOHTTP_AVAILABLE:
                        async with aiohttp.ClientSession() as session:
                            async with session.post(
                                api_url,
                                headers=headers,
                                json=payload,
                                timeout=aiohttp.ClientTimeout(total=10)
                            ) as response:
                                if response.status == 200:
                                    result = await response.json()
                                    parsed = self._parse_huggingface_response(result, model)
                                    if parsed and parsed != "No response generated":
                                        return parsed
                    else:
                        # Fallback to requests
                        response = requests.post(
                            api_url,
                            headers=headers,
                            json=payload,
                            timeout=10
                        )
                        if response.status_code == 200:
                            result = response.json()
                            parsed = self._parse_huggingface_response(result, model)
                            if parsed and parsed != "No response generated":
                                return parsed
                                
            except Exception as e:
                logger.error(f"Fallback model {model} failed: {e}")
                continue
        
        # Final fallback - return meaningful response without mock data
        return f"Unable to process the query '{prompt[:50]}...' at this time. Please try again later or rephrase your question."
    
    def _generate_search_results(self, query: str, ai_analysis: str) -> List[Dict[str, Any]]:
        """Generate realistic search results based on query and AI analysis."""
        # This would normally query actual databases, but for demo we'll create structured results
        results = []
        
        # Extract key terms for result generation
        key_terms = query.split()[:3]  # Simple extraction
        
        for i in range(min(5, len(key_terms) + 2)):
            result = {
                "id": f"result_{i+1}",
                "title": f"Research on {' '.join(key_terms[:2])} - Source {i+1}",
                "url": f"https://academic-source-{i+1}.com/research",
                "snippet": f"Comprehensive analysis of {query[:50]}... discussing key findings and implications.",
                "relevance_score": 0.9 - (i * 0.1),
                "source_type": ["academic", "industry", "government", "expert"][i % 4],
                "publication_date": "2024-01-15",
                "author": f"Research Team {i+1}",
                "citations": 150 - (i * 20)
            }
            results.append(result)
        
        return results
    
    def _extract_classification(self, ai_analysis: str) -> str:
        """Extract query classification from AI analysis."""
        try:
            if isinstance(ai_analysis, str) and ai_analysis.startswith('{'):
                data = json.loads(ai_analysis)
                return data.get("intent", "research_query")
        except:
            pass
        return "research_query"
    
    def _sanitize_response(self, response: str) -> str:
        """Sanitize LLM response to remove problematic characters."""
        if not response:
            return response
        
        # Remove emoji and other problematic characters
        import re
        # Remove emoji characters
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        
        sanitized = emoji_pattern.sub('', response)
        
        # Remove other problematic characters
        sanitized = sanitized.replace('\x00', '')  # Null bytes
        sanitized = sanitized.replace('\ufffd', '')  # Replacement character
        
        # Ensure it's valid UTF-8
        try:
            sanitized.encode('utf-8')
        except UnicodeEncodeError:
            # If still problematic, force encode/decode
            sanitized = sanitized.encode('utf-8', errors='ignore').decode('utf-8')
        
        return sanitized.strip()
    
    def _calculate_complexity(self, query: str) -> float:
        """Calculate query complexity score."""
        complexity_indicators = ["analyze", "compare", "synthesize", "evaluate", "comprehensive"]
        score = 0.5  # base score
        
        for indicator in complexity_indicators:
            if indicator in query.lower():
                score += 0.1
        
        # Length factor
        if len(query.split()) > 10:
            score += 0.2
        
        return min(score, 1.0)
    
    def _parse_fact_check_result(self, ai_verification: str) -> Dict[str, Any]:
        """Parse AI fact-check result."""
        try:
            if isinstance(ai_verification, str) and ai_verification.startswith('{'):
                return json.loads(ai_verification)
        except:
            pass
        
        return {
            "status": "analyzed",
            "confidence": 0.8,
            "consensus": 0.75,
            "sources": ["ai_analysis"],
            "analysis": ai_verification[:200] + "..." if len(ai_verification) > 200 else ai_verification,
            "limitations": ["ai_generated"],
            "follow_up": False
        }
    
    def _parse_synthesis_result(self, ai_synthesis: str) -> Dict[str, Any]:
        """Parse AI synthesis result."""
        try:
            if isinstance(ai_synthesis, str) and ai_synthesis.startswith('{'):
                return json.loads(ai_synthesis)
        except:
            pass
        
        # Ensure ai_synthesis is not None
        if ai_synthesis is None:
            ai_synthesis = "Synthesis result unavailable"
            
        return {
            "synthesis": ai_synthesis,
            "summary": ai_synthesis[:200] + "..." if len(ai_synthesis) > 200 else ai_synthesis,
            "insights": ["ai_generated_insights"],
            "recommendations": ["further_research"],
            "confidence": 0.85,
            "quality": 0.8
        }

    async def generate_citations(self, content: str, sources: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate proper citations for content based on sources."""
        if sources is None:
            sources = []
            
        try:
            # Create citation prompt
            sources_text = "\n".join([
                f"{i+1}. {source.get('title', 'Unknown Title')} - {source.get('url', 'No URL')} ({source.get('type', 'web')})"
                for i, source in enumerate(sources[:10])
            ])
            
            prompt = f"""
                    Generate proper citations for the following content:

                    Content: {content}

                    Available Sources:
                    {sources_text}

                    Please provide:
                    1. In-text citations in the content where appropriate
                    2. A formatted bibliography/references section
                    3. Citation style: APA format

                    Citations:"""

            llm_response = await self._call_llm_with_retry(LLMRequest(prompt=prompt, max_tokens=500, temperature=0.1), self.select_optimal_provider(QueryComplexity.SIMPLE_FACTUAL))
            
            return {
                "success": True,
                "citations": llm_response.content,
                "provider": self.last_used_provider.value if self.last_used_provider else "unknown",
                "sources_cited": len(sources or []),
                "citation_style": "APA",
                "trace_id": llm_response.trace_id
            }
        except Exception as e:
            logger.error(f"Citation generation error: {e}")
            return {
                "success": False,
                "citations": f"Basic citations: {', '.join([s.get('title', 'Source') for s in (sources or [])[:3]])}",
                "error": str(e),
                "sources_cited": len(sources or []),
                "trace_id": None
            }

    async def review_content(self, content: str, sources: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Review content for quality, accuracy, and completeness."""
        if sources is None:
            sources = []
            
        try:
            # Create review prompt
            sources_text = "\n".join([f"- {source.get('title', 'Source')}: {source.get('content', source.get('snippet', ''))}" for source in sources[:3]])
            
            prompt = f"""
Review the following content for quality, accuracy, and completeness:

Content: {content}

Reference Sources:
{sources_text}

Please provide a review that includes:
1. Overall quality score (0-10)
2. Accuracy assessment
3. Completeness evaluation
4. Specific suggestions for improvement
5. Factual corrections if needed

Review:"""

            llm_response = await self._call_llm_with_retry(LLMRequest(prompt=prompt, max_tokens=600, temperature=0.2), self.select_optimal_provider(QueryComplexity.RESEARCH_SYNTHESIS))
            
            # Extract quality score if possible
            quality_score = 0.8  # Default
            if "score:" in llm_response.content.lower():
                try:
                    score_text = llm_response.content.lower().split("score:")[1].split()[0]
                    quality_score = float(score_text.replace("/10", "")) / 10
                except:
                    pass
            
            return {
                "success": True,
                "review": llm_response.content,
                "quality_score": quality_score,
                "provider": self.last_used_provider.value if self.last_used_provider else "unknown",
                "sources_reviewed": len(sources or []),
                "trace_id": llm_response.trace_id
            }
        except Exception as e:
            logger.error(f"Content review error: {e}")
            return {
                "success": False,
                "review": f"Content appears to be about: {content[:100]}... Review unavailable.",
                "quality_score": 0.5,
                "error": str(e),
                "sources_reviewed": len(sources or []),
                "trace_id": None
            }

# Global processor instance
real_llm_processor = RealLLMProcessor()
