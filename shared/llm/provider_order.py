#!/usr/bin/env python3
"""
Centralized LLM Provider Order System

This module provides a single source of truth for LLM provider ordering
across the entire SarvanOM system. It implements the free-first fallback
strategy and ensures consistent provider selection behavior.

Key Features:
- Centralized provider order configuration
- Environment-driven provider availability
- Free-first fallback strategy
- Provider health monitoring
- Dynamic provider selection based on query complexity
- Role-based provider selection (FAST, QUALITY, LONG, REASONING, TOOL)
- Provider-specific model selection for each role
- Dynamic model selection based on query complexity
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from functools import lru_cache

logger = logging.getLogger(__name__)

class LLMProvider(str, Enum):
    """Enumeration of available LLM providers."""
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL_STUB = "local_stub"

class QueryComplexity(str, Enum):
    """Query complexity levels for provider selection."""
    SIMPLE = "simple"      # Fast, basic queries
    STANDARD = "standard"  # Normal queries
    COMPLEX = "complex"    # Reasoning, analysis
    EXPERT = "expert"      # Tool use, long context

class LLMRole(str, Enum):
    """LLM roles for capability-based provider selection."""
    FAST = "fast"          # Quick responses, simple tasks
    QUALITY = "quality"    # High-quality outputs, complex reasoning
    LONG = "long"          # Long context, document processing
    REASONING = "reasoning" # Advanced reasoning, analysis
    TOOL = "tool"          # Tool use, function calling

@dataclass
class ModelConfig:
    """Configuration for a specific model within a provider."""
    name: str
    provider: LLMProvider
    role: LLMRole
    max_tokens: int
    avg_latency_ms: int
    cost_per_1k_tokens: float
    supports_streaming: bool
    supports_tools: bool
    is_free: bool
    context_window: int
    reasoning_capability: float  # 0.0 to 1.0
    tool_capability: float      # 0.0 to 1.0
    
    # Phase I3 enhancements
    supports_vision: bool = False          # Vision/image processing capability
    supports_json_mode: bool = False       # Structured JSON output mode
    supports_function_calling: bool = False  # Function/tool calling
    max_rpm: Optional[int] = None          # Requests per minute limit
    max_tpm: Optional[int] = None          # Tokens per minute limit
    cost_tier: str = "standard"           # "free", "standard", "premium"
    
    # Circuit breaker settings
    failure_threshold: int = 5             # Failures before circuit opens
    circuit_timeout: int = 60              # Seconds before trying again

@dataclass
class ProviderConfig:
    """Configuration for a specific LLM provider."""
    name: LLMProvider
    priority: int
    is_free: bool
    max_tokens: int
    supports_streaming: bool
    supports_tools: bool
    avg_latency_ms: int
    cost_per_1k_tokens: float
    capabilities: List[LLMRole]  # What roles this provider can handle
    models: Dict[LLMRole, List[ModelConfig]]  # Models available for each role

class ProviderModelRegistry:
    """Registry for provider-specific models organized by role."""
    
    def __init__(self):
        self._initialize_provider_models()
    
    def _initialize_provider_models(self) -> Dict[LLMProvider, Dict[LLMRole, List[ModelConfig]]]:
        """Initialize provider-specific model configurations."""
        models = {}
        
        # Ollama Models
        models[LLMProvider.OLLAMA] = {
            LLMRole.FAST: [
                ModelConfig(
                    name="llama3:8b",
                    provider=LLMProvider.OLLAMA,
                    role=LLMRole.FAST,
                    max_tokens=8192,
                    avg_latency_ms=1500,
                    cost_per_1k_tokens=0.0,
                    supports_streaming=True,
                    supports_tools=False,
                    is_free=True,
                    context_window=8192,
                    reasoning_capability=0.6,
                    tool_capability=0.0,
                    supports_vision=False,
                    supports_json_mode=True,
                    supports_function_calling=False,
                    max_rpm=1000,
                    max_tpm=10000,
                    cost_tier="free",
                    failure_threshold=5,
                    circuit_timeout=60
                ),
                ModelConfig(
                    name="llama3:3b",
                    provider=LLMProvider.OLLAMA,
                    role=LLMRole.FAST,
                    max_tokens=4096,
                    avg_latency_ms=800,
                    cost_per_1k_tokens=0.0,
                    supports_streaming=True,
                    supports_tools=False,
                    is_free=True,
                    context_window=4096,
                    reasoning_capability=0.4,
                    tool_capability=0.0,
                    supports_vision=False,
                    supports_json_mode=True,
                    supports_function_calling=False,
                    max_rpm=1000,
                    max_tpm=10000,
                    cost_tier="free",
                    failure_threshold=5,
                    circuit_timeout=60
                )
            ],
            LLMRole.QUALITY: [
                ModelConfig(
                    name="llama3:70b",
                    provider=LLMProvider.OLLAMA,
                    role=LLMRole.QUALITY,
                    max_tokens=8192,
                    avg_latency_ms=4000,
                    cost_per_1k_tokens=0.0,
                    supports_streaming=True,
                    supports_tools=False,
                    is_free=True,
                    context_window=8192,
                    reasoning_capability=0.8,
                    tool_capability=0.0,
                    supports_vision=False,
                    supports_json_mode=True,
                    supports_function_calling=False,
                    max_rpm=1000,
                    max_tpm=10000,
                    cost_tier="free",
                    failure_threshold=5,
                    circuit_timeout=60
                )
            ]
        }
        
        # HuggingFace Models
        models[LLMProvider.HUGGINGFACE] = {
            LLMRole.FAST: [
                ModelConfig(
                    name="microsoft/DialoGPT-medium",
                    provider=LLMProvider.HUGGINGFACE,
                    role=LLMRole.FAST,
                    max_tokens=2048,
                    avg_latency_ms=2000,
                    cost_per_1k_tokens=0.0,
                    supports_streaming=True,
                    supports_tools=False,
                    is_free=True,
                    context_window=2048,
                    reasoning_capability=0.5,
                    tool_capability=0.0,
                    supports_vision=False,
                    supports_json_mode=True,
                    supports_function_calling=False,
                    max_rpm=100,
                    max_tpm=5000,
                    cost_tier="free",
                    failure_threshold=5,
                    circuit_timeout=60
                )
            ],
            LLMRole.QUALITY: [
                ModelConfig(
                    name="meta-llama/Llama-2-7b-chat-hf",
                    provider=LLMProvider.HUGGINGFACE,
                    role=LLMRole.QUALITY,
                    max_tokens=4096,
                    avg_latency_ms=3000,
                    cost_per_1k_tokens=0.0,
                    supports_streaming=True,
                    supports_tools=False,
                    is_free=True,
                    context_window=4096,
                    reasoning_capability=0.7,
                    tool_capability=0.0,
                    supports_vision=False,
                    supports_json_mode=True,
                    supports_function_calling=False,
                    max_rpm=100,
                    max_tpm=5000,
                    cost_tier="free",
                    failure_threshold=5,
                    circuit_timeout=60
                )
            ]
        }
        
        # OpenAI Models
        models[LLMProvider.OPENAI] = {
            LLMRole.FAST: [
                ModelConfig(
                    name="gpt-4o-mini",
                    provider=LLMProvider.OPENAI,
                    role=LLMRole.FAST,
                    max_tokens=128000,
                    avg_latency_ms=600,
                    cost_per_1k_tokens=0.00015,
                    supports_streaming=True,
                    supports_tools=True,
                    is_free=False,
                    context_window=128000,
                    reasoning_capability=0.8,
                    tool_capability=0.9,
                    supports_vision=True,
                    supports_json_mode=True,
                    supports_function_calling=True,
                    max_rpm=500,
                    max_tpm=10000,
                    cost_tier="standard",
                    failure_threshold=5,
                    circuit_timeout=60
                )
            ],
            LLMRole.QUALITY: [
                ModelConfig(
                    name="gpt-4o",
                    provider=LLMProvider.OPENAI,
                    role=LLMRole.QUALITY,
                    max_tokens=128000,
                    avg_latency_ms=800,
                    cost_per_1k_tokens=0.005,
                    supports_streaming=True,
                    supports_tools=True,
                    is_free=False,
                    context_window=128000,
                    reasoning_capability=0.95,
                    tool_capability=0.95,
                    supports_vision=True,
                    supports_json_mode=True,
                    supports_function_calling=True,
                    max_rpm=500,
                    max_tpm=10000,
                    cost_tier="standard",
                    failure_threshold=5,
                    circuit_timeout=60
                )
            ],
            LLMRole.LONG: [
                ModelConfig(
                    name="gpt-4o",
                    provider=LLMProvider.OPENAI,
                    role=LLMRole.LONG,
                    max_tokens=128000,
                    avg_latency_ms=800,
                    cost_per_1k_tokens=0.005,
                    supports_streaming=True,
                    supports_tools=True,
                    is_free=False,
                    context_window=128000,
                    reasoning_capability=0.95,
                    tool_capability=0.95,
                    supports_vision=True,
                    supports_json_mode=True,
                    supports_function_calling=True,
                    max_rpm=500,
                    max_tpm=10000,
                    cost_tier="standard",
                    failure_threshold=5,
                    circuit_timeout=60
                )
            ],
            LLMRole.REASONING: [
                ModelConfig(
                    name="o1-preview",
                    provider=LLMProvider.OPENAI,
                    role=LLMRole.REASONING,
                    max_tokens=128000,
                    avg_latency_ms=1200,
                    cost_per_1k_tokens=0.015,
                    supports_streaming=True,
                    supports_tools=True,
                    is_free=False,
                    context_window=128000,
                    reasoning_capability=0.98,
                    tool_capability=0.9,
                    supports_vision=False,
                    supports_json_mode=True,
                    supports_function_calling=True,
                    max_rpm=200,
                    max_tpm=5000,
                    cost_tier="premium",
                    failure_threshold=5,
                    circuit_timeout=60
                )
            ],
            LLMRole.TOOL: [
                ModelConfig(
                    name="gpt-4o",
                    provider=LLMProvider.OPENAI,
                    role=LLMRole.TOOL,
                    max_tokens=128000,
                    avg_latency_ms=800,
                    cost_per_1k_tokens=0.005,
                    supports_streaming=True,
                    supports_tools=True,
                    is_free=False,
                    context_window=128000,
                    reasoning_capability=0.95,
                    tool_capability=0.95,
                    supports_vision=True,
                    supports_json_mode=True,
                    supports_function_calling=True,
                    max_rpm=500,
                    max_tpm=10000,
                    cost_tier="standard",
                    failure_threshold=5,
                    circuit_timeout=60
                )
            ]
        }
        
        # Anthropic Models
        models[LLMProvider.ANTHROPIC] = {
            LLMRole.QUALITY: [
                ModelConfig(
                    name="claude-3-5-sonnet-20241022",
                    provider=LLMProvider.ANTHROPIC,
                    role=LLMRole.QUALITY,
                    max_tokens=200000,
                    avg_latency_ms=1000,
                    cost_per_1k_tokens=0.003,
                    supports_streaming=True,
                    supports_tools=True,
                    is_free=False,
                    context_window=200000,
                    reasoning_capability=0.9,
                    tool_capability=0.9,
                    supports_vision=True,
                    supports_json_mode=True,
                    supports_function_calling=True,
                    max_rpm=200,
                    max_tpm=8000,
                    cost_tier="standard",
                    failure_threshold=5,
                    circuit_timeout=60
                )
            ],
            LLMRole.LONG: [
                ModelConfig(
                    name="claude-3-opus-20240229",
                    provider=LLMProvider.ANTHROPIC,
                    role=LLMRole.LONG,
                    max_tokens=200000,
                    avg_latency_ms=1500,
                    cost_per_1k_tokens=0.015,
                    supports_streaming=True,
                    supports_tools=True,
                    is_free=False,
                    context_window=200000,
                    reasoning_capability=0.95,
                    tool_capability=0.95,
                    supports_vision=True,
                    supports_json_mode=True,
                    supports_function_calling=True,
                    max_rpm=100,
                    max_tpm=4000,
                    cost_tier="premium",
                    failure_threshold=5,
                    circuit_timeout=60
                )
            ],
            LLMRole.REASONING: [
                ModelConfig(
                    name="claude-3-opus-20240229",
                    provider=LLMProvider.ANTHROPIC,
                    role=LLMRole.REASONING,
                    max_tokens=200000,
                    avg_latency_ms=1500,
                    cost_per_1k_tokens=0.015,
                    supports_streaming=True,
                    supports_tools=True,
                    is_free=False,
                    context_window=200000,
                    reasoning_capability=0.95,
                    tool_capability=0.95,
                    supports_vision=True,
                    supports_json_mode=True,
                    supports_function_calling=True,
                    max_rpm=100,
                    max_tpm=4000,
                    cost_tier="premium",
                    failure_threshold=5,
                    circuit_timeout=60
                )
            ],
            LLMRole.TOOL: [
                ModelConfig(
                    name="claude-3-5-sonnet-20241022",
                    provider=LLMProvider.ANTHROPIC,
                    role=LLMRole.TOOL,
                    max_tokens=200000,
                    avg_latency_ms=1000,
                    cost_per_1k_tokens=0.003,
                    supports_streaming=True,
                    supports_tools=True,
                    is_free=False,
                    context_window=200000,
                    reasoning_capability=0.9,
                    tool_capability=0.9,
                    supports_vision=True,
                    supports_json_mode=True,
                    supports_function_calling=True,
                    max_rpm=200,
                    max_tpm=8000,
                    cost_tier="standard",
                    failure_threshold=5,
                    circuit_timeout=60
                )
            ]
        }
        
        # Local Stub (Fallback)
        models[LLMProvider.LOCAL_STUB] = {
            LLMRole.FAST: [
                ModelConfig(
                    name="local_stub",
                    provider=LLMProvider.LOCAL_STUB,
                    role=LLMRole.FAST,
                    max_tokens=4096,
                    avg_latency_ms=100,
                    cost_per_1k_tokens=0.0,
                    supports_streaming=False,
                    supports_tools=False,
                    is_free=True,
                    context_window=4096,
                    reasoning_capability=0.1,
                    tool_capability=0.0,
                    supports_vision=False,
                    supports_json_mode=True,
                    supports_function_calling=False,
                    max_rpm=1000,
                    max_tpm=10000,
                    cost_tier="free",
                    failure_threshold=5,
                    circuit_timeout=60
                )
            ],
            LLMRole.QUALITY: [
                ModelConfig(
                    name="local_stub",
                    provider=LLMProvider.LOCAL_STUB,
                    role=LLMRole.QUALITY,
                    max_tokens=4096,
                    avg_latency_ms=100,
                    cost_per_1k_tokens=0.0,
                    supports_streaming=False,
                    supports_tools=False,
                    is_free=True,
                    context_window=4096,
                    reasoning_capability=0.1,
                    tool_capability=0.0,
                    supports_vision=False,
                    supports_json_mode=True,
                    supports_function_calling=False,
                    max_rpm=1000,
                    max_tpm=10000,
                    cost_tier="free",
                    failure_threshold=5,
                    circuit_timeout=60
                )
            ]
        }
        
        return models
    
    def get_models_for_provider_role(self, provider: LLMProvider, role: LLMRole) -> List[ModelConfig]:
        """Get available models for a specific provider and role."""
        provider_models = self._initialize_provider_models().get(provider, {})
        return provider_models.get(role, [])
    
    def get_best_model_for_complexity(self, provider: LLMProvider, complexity: QueryComplexity, prefer_free: bool = True) -> Optional[ModelConfig]:
        """Get the best model for a provider based on query complexity."""
        # Map complexity to roles
        complexity_role_mapping = {
            QueryComplexity.SIMPLE: LLMRole.FAST,
            QueryComplexity.STANDARD: LLMRole.QUALITY,
            QueryComplexity.COMPLEX: LLMRole.REASONING,
            QueryComplexity.EXPERT: LLMRole.TOOL
        }
        
        target_role = complexity_role_mapping.get(complexity, LLMRole.QUALITY)
        available_models = self.get_models_for_provider_role(provider, target_role)
        
        if not available_models:
            # Fallback to FAST role if target role not available
            available_models = self.get_models_for_provider_role(provider, LLMRole.FAST)
        
        if not available_models:
            return None
        
        # Filter by preferences
        if prefer_free:
            free_models = [m for m in available_models if m.is_free]
            if free_models:
                available_models = free_models
        
        # Select best model based on capability scores
        if complexity == QueryComplexity.EXPERT:
            # For expert queries, prioritize tool capability
            return max(available_models, key=lambda m: m.tool_capability)
        elif complexity == QueryComplexity.COMPLEX:
            # For complex queries, prioritize reasoning capability
            return max(available_models, key=lambda m: m.reasoning_capability)
        else:
            # For simple/standard queries, prioritize speed (lower latency)
            return min(available_models, key=lambda m: m.avg_latency_ms)
    
    def get_all_provider_models(self) -> Dict[LLMProvider, Dict[LLMRole, List[ModelConfig]]]:
        """Get all provider model configurations."""
        return self._initialize_provider_models()

class RoleMapping:
    """Maps LLM roles to specific provider:model combinations."""
    
    def __init__(self):
        self._role_mappings = self._load_role_mappings()
        self.model_registry = ProviderModelRegistry()
    
    def _load_role_mappings(self) -> Dict[LLMRole, List[str]]:
        """Load role mappings from environment variables."""
        mappings = {}
        
        # FAST role - prioritize speed
        fast_config = os.getenv("LLM_FAST", "ollama:llama3:8b,openai:gpt-4o-mini")
        mappings[LLMRole.FAST] = [p.strip() for p in fast_config.split(",")]
        
        # QUALITY role - prioritize output quality
        quality_config = os.getenv("LLM_QUALITY", "anthropic:claude-3-5-sonnet,openai:gpt-4o")
        mappings[LLMRole.QUALITY] = [p.strip() for p in quality_config.split(",")]
        
        # LONG role - prioritize context length
        long_config = os.getenv("LLM_LONG", "anthropic:claude-3-opus,openai:gpt-4o")
        mappings[LLMRole.LONG] = [p.strip() for p in long_config.split(",")]
        
        # REASONING role - prioritize reasoning capabilities
        reasoning_config = os.getenv("LLM_REASONING", "anthropic:claude-3-opus,openai:o1-preview")
        mappings[LLMRole.REASONING] = [p.strip() for p in reasoning_config.split(",")]
        
        # TOOL role - prioritize tool/function calling
        tool_config = os.getenv("LLM_TOOL", "openai:gpt-4o,anthropic:claude-3-5-sonnet")
        mappings[LLMRole.TOOL] = [p.strip() for p in tool_config.split(",")]
        
        return mappings
    
    def get_providers_for_role(self, role: LLMRole) -> List[str]:
        """Get provider:model combinations for a specific role."""
        return self._role_mappings.get(role, [])
    
    def get_role_for_provider(self, provider: str) -> Optional[LLMRole]:
        """Get the primary role for a specific provider."""
        for role, providers in self._role_mappings.items():
            if any(provider in p for p in providers):
                return role
        return None
    
    def get_all_mappings(self) -> Dict[LLMRole, List[str]]:
        """Get all role mappings."""
        return self._role_mappings.copy()

# All duplicate content removed
    
    def get_models_for_provider_role(self, provider: LLMProvider, role: LLMRole) -> List[ModelConfig]:
        """Get available models for a specific provider and role."""
        provider_models = self._initialize_provider_models().get(provider, {})
        return provider_models.get(role, [])
    
    def get_best_model_for_complexity(self, provider: LLMProvider, complexity: QueryComplexity, prefer_free: bool = True) -> Optional[ModelConfig]:
        """Get the best model for a provider based on query complexity."""
        # Map complexity to roles
        complexity_role_mapping = {
            QueryComplexity.SIMPLE: LLMRole.FAST,
            QueryComplexity.STANDARD: LLMRole.QUALITY,
            QueryComplexity.COMPLEX: LLMRole.REASONING,
            QueryComplexity.EXPERT: LLMRole.TOOL
        }
        
        target_role = complexity_role_mapping.get(complexity, LLMRole.QUALITY)
        available_models = self.get_models_for_provider_role(provider, target_role)
        
        if not available_models:
            # Fallback to FAST role if target role not available
            available_models = self.get_models_for_provider_role(provider, LLMRole.FAST)
        
        if not available_models:
            return None
        
        # Filter by preferences
        if prefer_free:
            free_models = [m for m in available_models if m.is_free]
            if free_models:
                available_models = free_models
        
        # Select best model based on capability scores
        if complexity == QueryComplexity.EXPERT:
            # For expert queries, prioritize tool capability
            return max(available_models, key=lambda m: m.tool_capability)
        elif complexity == QueryComplexity.COMPLEX:
            # For complex queries, prioritize reasoning capability
            return max(available_models, key=lambda m: m.reasoning_capability)
        else:
            # For simple/standard queries, prioritize speed (lower latency)
            return min(available_models, key=lambda m: m.avg_latency_ms)
    
    def get_all_provider_models(self) -> Dict[LLMProvider, Dict[LLMRole, List[ModelConfig]]]:
        """Get all provider model configurations."""
        return self._initialize_provider_models()

class ProviderRegistry:
    """Centralized registry for LLM providers with ordering and fallback logic."""
    
    def __init__(self):
        self.providers: Dict[LLMProvider, ProviderConfig] = self._initialize_providers()
        self._base_order: List[LLMProvider] = self._get_base_order()
        self._free_first_order: List[LLMProvider] = self._get_free_first_order()
        self.role_mapping = RoleMapping()
        self.model_registry = ProviderModelRegistry()
        
        # Populate provider models
        self._populate_provider_models()
    
    def _populate_provider_models(self):
        """Populate provider configurations with their available models."""
        all_models = self.model_registry.get_all_provider_models()
        
        for provider, provider_models in all_models.items():
            if provider in self.providers:
                self.providers[provider].models = provider_models
    
    def _initialize_providers(self) -> Dict[LLMProvider, ProviderConfig]:
        """Initialize provider configurations."""
        return {
            LLMProvider.OLLAMA: ProviderConfig(
                name=LLMProvider.OLLAMA,
                priority=1,
                is_free=True,
                max_tokens=8192,
                supports_streaming=True,
                supports_tools=False,
                avg_latency_ms=2000,
                cost_per_1k_tokens=0.0,
                capabilities=[LLMRole.FAST, LLMRole.QUALITY],
                models={}  # Will be populated by model registry
            ),
            LLMProvider.HUGGINGFACE: ProviderConfig(
                name=LLMProvider.HUGGINGFACE,
                priority=2,
                is_free=True,
                max_tokens=4096,
                supports_streaming=True,
                supports_tools=False,
                avg_latency_ms=3000,
                cost_per_1k_tokens=0.0,
                capabilities=[LLMRole.FAST, LLMRole.QUALITY],
                models={}  # Will be populated by model registry
            ),
            LLMProvider.OPENAI: ProviderConfig(
                name=LLMProvider.OPENAI,
                priority=3,
                is_free=False,
                max_tokens=128000,
                supports_streaming=True,
                supports_tools=True,
                avg_latency_ms=800,
                cost_per_1k_tokens=0.01,
                capabilities=[LLMRole.FAST, LLMRole.QUALITY, LLMRole.LONG, LLMRole.REASONING, LLMRole.TOOL],
                models={}  # Will be populated by model registry
            ),
            LLMProvider.ANTHROPIC: ProviderConfig(
                name=LLMProvider.ANTHROPIC,
                priority=4,
                is_free=False,
                max_tokens=200000,
                supports_streaming=True,
                supports_tools=True,
                avg_latency_ms=1200,
                cost_per_1k_tokens=0.015,
                capabilities=[LLMRole.QUALITY, LLMRole.LONG, LLMRole.REASONING, LLMRole.TOOL],
                models={}  # Will be populated by model registry
            ),
            LLMProvider.LOCAL_STUB: ProviderConfig(
                name=LLMProvider.LOCAL_STUB,
                priority=5,
                is_free=True,
                max_tokens=4096,
                supports_streaming=False,
                supports_tools=False,
                avg_latency_ms=100,
                cost_per_1k_tokens=0.0,
                capabilities=[LLMRole.FAST, LLMRole.QUALITY],
                models={}  # Will be populated by model registry
            )
        }
    
    def _get_base_order(self) -> List[LLMProvider]:
        """Get the base provider order from environment or use defaults."""
        env_order = os.getenv("LLM_PROVIDER_ORDER")
        if env_order:
            try:
                # Parse comma-separated provider names
                provider_names = [name.strip().lower() for name in env_order.split(",")]
                providers = []
                for name in provider_names:
                    try:
                        provider = LLMProvider(name)
                        providers.append(provider)
                    except ValueError:
                        logger.warning(f"Unknown provider in LLM_PROVIDER_ORDER: {name}")
                
                if providers:
                    logger.info(f"Using custom provider order: {[p.value for p in providers]}")
                    return providers
            except Exception as e:
                logger.error(f"Failed to parse LLM_PROVIDER_ORDER: {e}")
        
        # Default order: free-first, then paid
        default_order = [
            LLMProvider.OLLAMA,
            LLMProvider.HUGGINGFACE,
            LLMProvider.OPENAI,
            LLMProvider.ANTHROPIC,
            LLMProvider.LOCAL_STUB
        ]
        logger.info(f"Using default provider order: {[p.value for p in default_order]}")
        return default_order
    
    def _get_free_first_order(self) -> List[LLMProvider]:
        """Get provider order optimized for free-first strategy."""
        free_providers = [p for p in self._base_order if self.providers[p].is_free]
        paid_providers = [p for p in self._base_order if not self.providers[p].is_free]
        
        # Free providers first, then paid providers
        return free_providers + paid_providers
    
    def get_provider_order(self, prefer_free: bool = True) -> List[LLMProvider]:
        """
        Get the ordered list of providers.
        
        Args:
            prefer_free: If True, prioritize free providers
            
        Returns:
            List of providers in priority order
        """
        if prefer_free:
            return self._free_first_order.copy()
        return self._base_order.copy()
    
    def get_available_providers(self, prefer_free: bool = True) -> List[LLMProvider]:
        """
        Get list of available providers based on environment configuration.
        
        Args:
            prefer_free: If True, prioritize free providers
            
        Returns:
            List of available providers in priority order
        """
        order = self.get_provider_order(prefer_free)
        available = []
        
        for provider in order:
            if self._is_provider_available(provider):
                available.append(provider)
        
        return available
    
    def select_provider_and_model_for_complexity(
        self, 
        complexity: QueryComplexity, 
        prefer_free: bool = True
    ) -> Tuple[Optional[LLMProvider], Optional[ModelConfig]]:
        """
        Select the best provider and model for a given query complexity.
        
        Args:
            complexity: The complexity level of the query
            prefer_free: If True, prioritize free providers
            
        Returns:
            Tuple of (provider, model) or (None, None) if none available
        """
        available_providers = self.get_available_providers(prefer_free)
        
        if not available_providers:
            logger.warning("No providers available")
            return None, None
        
        best_provider = None
        best_model = None
        best_score = -1
        
        for provider in available_providers:
            model = self.model_registry.get_best_model_for_complexity(
                provider, complexity, prefer_free
            )
            
            if model:
                # Calculate score based on complexity requirements
                score = self._calculate_model_score(model, complexity, prefer_free)
                
                if score > best_score:
                    best_score = score
                    best_provider = provider
                    best_model = model
        
        return best_provider, best_model
    
    def _calculate_model_score(self, model: ModelConfig, complexity: QueryComplexity, prefer_free: bool) -> float:
        """Calculate a score for a model based on complexity requirements."""
        score = 0.0
        
        # Base score from reasoning capability
        score += model.reasoning_capability * 0.4
        
        # Tool capability for expert queries
        if complexity == QueryComplexity.EXPERT:
            score += model.tool_capability * 0.4
        
        # Speed bonus for simple queries
        if complexity == QueryComplexity.SIMPLE:
            speed_score = max(0, 1.0 - (model.avg_latency_ms / 5000.0))
            score += speed_score * 0.3
        
        # Cost penalty for paid models when prefer_free is True
        if prefer_free and not model.is_free:
            score -= 0.5
        
        # Context window bonus for long queries
        if complexity == QueryComplexity.COMPLEX:
            context_score = min(1.0, model.context_window / 100000.0)
            score += context_score * 0.2
        
        return score
    
    def select_provider_for_role(self, role: LLMRole, prefer_free: bool = True) -> Optional[LLMProvider]:
        """
        Select the best provider for a specific role.
        
        Args:
            role: The role to select a provider for
            prefer_free: If True, prioritize free providers
            
        Returns:
            The selected provider or None if none available
        """
        # Get role-specific provider:model mappings
        role_providers = self.role_mapping.get_providers_for_role(role)
        
        # Extract provider names from provider:model strings
        provider_names = []
        for provider_model in role_providers:
            provider_name = provider_model.split(":")[0].lower()
            try:
                provider_enum = LLMProvider(provider_name)
                provider_names.append(provider_enum)
            except ValueError:
                logger.warning(f"Unknown provider in role mapping: {provider_name}")
        
        # Filter by availability and preferences
        available_providers = self.get_available_providers(prefer_free)
        
        # Find providers that can handle this role and are available
        suitable_providers = []
        for provider in available_providers:
            if provider in provider_names and role in self.providers[provider].capabilities:
                suitable_providers.append(provider)
        
        if not suitable_providers:
            logger.warning(f"No suitable providers available for role: {role}")
            return None
        
        # Select based on preferences
        if prefer_free:
            # Prefer free providers for the role
            free_providers = [p for p in suitable_providers if self.providers[p].is_free]
            if free_providers:
                return free_providers[0]
        
        # Return first suitable provider
        return suitable_providers[0]
    
    def get_provider_metrics(self) -> Dict[str, any]:
        """Get comprehensive provider metrics including role-based selection."""
        base_stats = self.get_provider_stats()
        
        # Add role-based metrics
        role_metrics = {}
        for role in LLMRole:
            role_metrics[f"role_{role.value}_providers"] = len(self.role_mapping.get_providers_for_role(role))
            role_metrics[f"role_{role.value}_available"] = self.select_provider_for_role(role) is not None
        
        base_stats.update(role_metrics)
        return base_stats
    
    def _is_provider_available(self, provider: LLMProvider) -> bool:
        """
        Check if a provider is available based on environment configuration.
        
        Args:
            provider: The provider to check
            
        Returns:
            True if provider is available, False otherwise
        """
        if provider == LLMProvider.LOCAL_STUB:
            return True  # Always available as fallback
        
        if provider == LLMProvider.OLLAMA:
            return self._check_ollama_availability()
        
        if provider == LLMProvider.HUGGINGFACE:
            return self._check_huggingface_availability()
        
        if provider == LLMProvider.OPENAI:
            return self._check_openai_availability()
        
        if provider == LLMProvider.ANTHROPIC:
            return self._check_anthropic_availability()
        
        return False
    
    def _check_ollama_availability(self) -> bool:
        """Check if Ollama is available."""
        # Check if Ollama is enabled and base URL is set
        ollama_enabled = os.getenv("OLLAMA_ENABLED", "true").lower() == "true"
        ollama_base_url = os.getenv("OLLAMA_BASE_URL")
        
        if not ollama_enabled:
            return False
        
        if not ollama_base_url:
            logger.warning("Ollama enabled but OLLAMA_BASE_URL not set")
            return False
        
        return True
    
    def _check_huggingface_availability(self) -> bool:
        """Check if HuggingFace is available."""
        # Check if HuggingFace API token is set
        hf_token = os.getenv("HUGGINGFACE_WRITE_TOKEN")
        
        if not hf_token:
            logger.debug("HuggingFace not available: HUGGINGFACE_WRITE_TOKEN not set")
            return False
        
        return True
    
    def _check_openai_availability(self) -> bool:
        """Check if OpenAI is available."""
        # Check if OpenAI API key is set
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if not openai_key:
            logger.debug("OpenAI not available: OPENAI_API_KEY not set")
            return False
        
        return True
    
    def _check_anthropic_availability(self) -> bool:
        """Check if Anthropic is available."""
        # Check if Anthropic API key is set
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not anthropic_key:
            logger.debug("Anthropic not available: ANTHROPIC_API_KEY not set")
            return False
        
        return True
    
    def select_provider_for_complexity(
        self, 
        complexity: QueryComplexity, 
        prefer_free: bool = True
    ) -> Optional[LLMProvider]:
        """
        Select the best provider for a given query complexity.
        
        Args:
            complexity: The complexity level of the query
            prefer_free: If True, prioritize free providers
            
        Returns:
            The selected provider or None if none available
        """
        available_providers = self.get_available_providers(prefer_free)
        
        if not available_providers:
            logger.warning("No providers available")
            return None
        
        # Simple selection strategy based on complexity
        if complexity == QueryComplexity.SIMPLE:
            # For simple queries, prefer fast providers
            fast_providers = [p for p in available_providers 
                            if self.providers[p].avg_latency_ms <= 1000]
            if fast_providers:
                return fast_providers[0]
        
        elif complexity == QueryComplexity.EXPERT:
            # For expert queries, prefer providers with tool support
            tool_providers = [p for p in available_providers 
                            if self.providers[p].supports_tools]
            if tool_providers:
                return tool_providers[0]
        
        # Default: return first available provider
        return available_providers[0]
    
    def select_provider_and_model_for_complexity(
        self, 
        complexity: QueryComplexity, 
        prefer_free: bool = True
    ) -> Tuple[Optional[LLMProvider], Optional[ModelConfig]]:
        """
        Select the best provider and model for a given query complexity.
        
        Args:
            complexity: The complexity level of the query
            prefer_free: If True, prioritize free providers
        
        Returns:
            Tuple of (provider, model) or (None, None) if none available
        """
        available_providers = self.get_available_providers(prefer_free)
        
        if not available_providers:
            logger.warning("No providers available")
            return None, None
        
        best_provider = None
        best_model = None
        best_score = -1
        
        for provider in available_providers:
            model = self.model_registry.get_best_model_for_complexity(
                provider, complexity, prefer_free
            )
            
            if model:
                # Calculate score based on complexity requirements
                score = self._calculate_model_score(model, complexity, prefer_free)
                
                if score > best_score:
                    best_score = score
                    best_provider = provider
                    best_model = model
        
        return best_provider, best_model
    
    def _calculate_model_score(self, model: ModelConfig, complexity: QueryComplexity, prefer_free: bool) -> float:
        """Calculate a score for a model based on complexity requirements."""
        score = 0.0
        
        # Base score from reasoning capability
        score += model.reasoning_capability * 0.4
        
        # Tool capability for expert queries
        if complexity == QueryComplexity.EXPERT:
            score += model.tool_capability * 0.4
        
        # Speed bonus for simple queries
        if complexity == QueryComplexity.SIMPLE:
            speed_score = max(0, 1.0 - (model.avg_latency_ms / 5000.0))
            score += speed_score * 0.3
        
        # Cost penalty for paid models when prefer_free is True
        if prefer_free and not model.is_free:
            score -= 0.5
        
        # Context window bonus for long queries
        if complexity == QueryComplexity.COMPLEX:
            context_score = min(1.0, model.context_window / 100000.0)
            score += context_score * 0.2
        
        return score
    
    def get_provider_info(self, provider: LLMProvider) -> Optional[ProviderConfig]:
        """Get configuration information for a specific provider."""
        return self.providers.get(provider)
    
    def get_provider_stats(self) -> Dict[str, any]:
        """Get statistics about all providers."""
        stats = {
            "total_providers": len(self.providers),
            "free_providers": len([p for p in self.providers.values() if p.is_free]),
            "paid_providers": len([p for p in self.providers.values() if not p.is_free]),
            "available_providers": len(self.get_available_providers()),
            "base_order": [p.value for p in self._base_order],
            "free_first_order": [p.value for p in self._free_first_order]
        }
        
        # Add per-provider availability
        for provider in self.providers:
            stats[f"{provider.value}_available"] = self._is_provider_available(provider)
        
        return stats

# Global registry instance
_provider_registry: Optional[ProviderRegistry] = None

def get_provider_registry() -> ProviderRegistry:
    """Get the global provider registry instance."""
    global _provider_registry
    if _provider_registry is None:
        _provider_registry = ProviderRegistry()
    return _provider_registry

@lru_cache(maxsize=1)
def get_provider_order(prefer_free: bool = True) -> List[str]:
    """
    Get the ordered list of provider names.
    
    This is the main function that other modules should use.
    
    Args:
        prefer_free: If True, prioritize free providers
        
    Returns:
        List of provider names in priority order
    """
    registry = get_provider_registry()
    providers = registry.get_provider_order(prefer_free)
    return [p.value for p in providers]

@lru_cache(maxsize=1)
def get_available_providers(prefer_free: bool = True) -> List[str]:
    """
    Get list of available provider names.
    
    Args:
        prefer_free: If True, prioritize free providers
        
    Returns:
        List of available provider names in priority order
    """
    registry = get_provider_registry()
    providers = registry.get_available_providers(prefer_free)
    return [p.value for p in providers]

def select_provider_for_complexity(
    complexity: QueryComplexity, 
    prefer_free: bool = True
) -> Optional[str]:
    """
    Select the best provider for a given query complexity.
    
    Args:
        complexity: The complexity level of the query
        prefer_free: If True, prioritize free providers
        
    Returns:
        The selected provider name or None if none available
    """
    registry = get_provider_registry()
    provider = registry.select_provider_for_complexity(complexity, prefer_free)
    return provider.value if provider else None

def select_provider_for_role(role: LLMRole, prefer_free: bool = True) -> Optional[str]:
    """
    Select the best provider for a specific role.
    
    Args:
        role: The role to select a provider for
        prefer_free: If True, prioritize free providers
        
    Returns:
        The selected provider name or None if none available
    """
    registry = get_provider_registry()
    provider = registry.select_provider_for_role(role, prefer_free)
    return provider.value if provider else None

def select_provider_and_model_for_complexity(
    complexity: QueryComplexity, 
    prefer_free: bool = True
) -> Tuple[Optional[str], Optional[str]]:
    """
    Select the best provider and model for a given query complexity.
    
    Args:
        complexity: The complexity level of the query
        prefer_free: If True, prioritize free providers
        
    Returns:
        Tuple of (provider_name, model_name) or (None, None) if none available
    """
    registry = get_provider_registry()
    provider, model = registry.select_provider_and_model_for_complexity(complexity, prefer_free)
    return (provider.value if provider else None, model.name if model else None)

def get_provider_stats() -> Dict[str, any]:
    """Get statistics about all providers."""
    registry = get_provider_registry()
    return registry.get_provider_stats()

def get_provider_metrics() -> Dict[str, any]:
    """Get comprehensive provider metrics including role-based selection."""
    registry = get_provider_registry()
    return registry.get_provider_metrics()

def get_role_mappings() -> Dict[LLMRole, List[str]]:
    """Get all role-to-provider mappings."""
    registry = get_provider_registry()
    return registry.role_mapping.get_all_mappings()

def get_provider_models() -> Dict[LLMProvider, Dict[LLMRole, List[ModelConfig]]]:
    """Get all provider model configurations."""
    registry = get_provider_registry()
    return registry.model_registry.get_all_provider_models()

# Export main functions
__all__ = [
    "LLMProvider",
    "QueryComplexity",
    "LLMRole",
    "ProviderConfig",
    "ModelConfig",
    "RoleMapping",
    "ProviderModelRegistry",
    "ProviderRegistry",
    "get_provider_registry",
    "get_provider_order",
    "get_available_providers",
    "select_provider_for_complexity",
    "select_provider_and_model_for_complexity",
    "select_provider_for_role",
    "get_provider_stats",
    "get_provider_metrics",
    "get_role_mappings",
    "get_provider_models"
]
