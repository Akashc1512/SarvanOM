"""
Model Router Service Configuration - SarvanOM v2

Configuration module for the Model Router service that reads only canonical
environment variable names and implements safe fallbacks.

Features:
    - Canonical environment variable names only
    - Fail-fast for required providers
    - Safe fallbacks for optional providers
    - Text LLM and Vision/LMM provider configurations
    - Integration with centralized provider config
"""

import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import structlog

# Import the centralized provider configuration
from sarvanom.shared.core.config.provider_config import (
    provider_config,
    get_provider_key,
    is_provider_available,
    get_provider_summary,
    log_provider_status
)

logger = structlog.get_logger(__name__)

@dataclass
class ModelProviderConfig:
    """Configuration for a model provider"""
    name: str
    env_key: Optional[str]
    is_configured: bool
    is_required: bool
    models: List[str]
    capabilities: List[str]

@dataclass
class ModelRouterConfig:
    """Configuration for Model Router service"""
    
    # Service settings
    service_name: str = "model-router"
    port: int = 8001
    metrics_port: int = 8002
    
    # Model Registry settings
    model_registry_url: str = "http://localhost:8000"
    
    # Provider configurations
    text_providers: Dict[str, ModelProviderConfig] = None
    vision_providers: Dict[str, ModelProviderConfig] = None
    
    # Budget settings (from docs)
    refinement_budget_ms: int = 500
    refinement_p95_budget_ms: int = 800
    
    # Feature flags
    keyless_fallbacks_enabled: bool = True
    
    def __post_init__(self):
        """Initialize provider configurations after dataclass creation"""
        if self.text_providers is None:
            self.text_providers = {}
        if self.vision_providers is None:
            self.vision_providers = {}
        self._load_provider_configurations()
        self._log_configuration_status()
    
    def _load_provider_configurations(self):
        """Load provider configurations using canonical env keys only"""
        
        # Text LLM Providers (OpenAI, Anthropic)
        self.text_providers = {
            "openai": ModelProviderConfig(
                name="OpenAI",
                env_key="OPENAI_API_KEY",
                is_configured=is_provider_available("OPENAI_API_KEY"),
                is_required=True,  # Required for text LLMs
                models=["gpt-4o-2024-08-06", "gpt-4o-mini-2024-07-18", "gpt-3.5-turbo-0125"],
                capabilities=["text_generation", "function_calling", "streaming", "fast_inference"]
            ),
            "anthropic": ModelProviderConfig(
                name="Anthropic",
                env_key="ANTHROPIC_API_KEY",
                is_configured=is_provider_available("ANTHROPIC_API_KEY"),
                is_required=True,  # Required for text LLMs
                models=["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
                capabilities=["text_generation", "function_calling", "streaming", "long_context"]
            )
        }
        
        # Vision/LMM Providers (Gemini, OpenAI Vision)
        self.vision_providers = {
            "gemini": ModelProviderConfig(
                name="Google Gemini",
                env_key="GEMINI_API_KEY",
                is_configured=is_provider_available("GEMINI_API_KEY"),
                is_required=False,  # Optional for vision
                models=["gemini-1.5-pro"],
                capabilities=["multimodal", "vision", "text_generation", "long_context"]
            ),
            "openai_vision": ModelProviderConfig(
                name="OpenAI Vision",
                env_key="OPENAI_API_KEY",
                is_configured=is_provider_available("OPENAI_API_KEY"),
                is_required=False,  # Fallback for vision
                models=["gpt-4o-2024-08-06"],
                capabilities=["multimodal", "vision", "text_generation"]
            )
        }
        
        # Get keyless fallbacks setting
        self.keyless_fallbacks_enabled = provider_config.keyless_fallbacks_enabled
    
    def _log_configuration_status(self):
        """Log the configuration status"""
        logger.info(f"Model Router Service Configuration:")
        logger.info(f"  Keyless Fallbacks: {self.keyless_fallbacks_enabled}")
        logger.info(f"  Refinement Budget: {self.refinement_budget_ms}ms (p95: {self.refinement_p95_budget_ms}ms)")
        
        logger.info("  Text LLM Providers:")
        for provider_name, provider_config in self.text_providers.items():
            status = "✅" if provider_config.is_configured else "❌"
            logger.info(f"    {status} {provider_config.name}: {'Configured' if provider_config.is_configured else 'Not configured'}")
            if provider_config.is_configured:
                logger.info(f"      Models: {', '.join(provider_config.models)}")
        
        logger.info("  Vision/LMM Providers:")
        for provider_name, provider_config in self.vision_providers.items():
            status = "✅" if provider_config.is_configured else "⚠️"
            logger.info(f"    {status} {provider_config.name}: {'Configured' if provider_config.is_configured else 'Not configured'}")
            if provider_config.is_configured:
                logger.info(f"      Models: {', '.join(provider_config.models)}")
        
        # Log provider status
        log_provider_status()
    
    def get_text_providers(self) -> Dict[str, ModelProviderConfig]:
        """Get text LLM provider configurations"""
        return self.text_providers
    
    def get_vision_providers(self) -> Dict[str, ModelProviderConfig]:
        """Get vision/LMM provider configurations"""
        return self.vision_providers
    
    def get_configured_text_providers(self) -> List[str]:
        """Get list of configured text LLM providers"""
        return [name for name, config in self.text_providers.items() if config.is_configured]
    
    def get_configured_vision_providers(self) -> List[str]:
        """Get list of configured vision/LMM providers"""
        return [name for name, config in self.vision_providers.items() if config.is_configured]
    
    def get_text_model_selection(self) -> Dict[str, Any]:
        """Get text model selection policy"""
        configured_providers = self.get_configured_text_providers()
        
        if not configured_providers:
            return {
                "available": False,
                "error": "No text LLM providers configured",
                "models": []
            }
        
        # Build model selection based on available providers
        models = []
        for provider_name in configured_providers:
            provider_config = self.text_providers[provider_name]
            models.extend(provider_config.models)
        
        return {
            "available": True,
            "providers": configured_providers,
            "models": models,
            "primary_models": [
                "gpt-4o-2024-08-06" if "openai" in configured_providers else None,
                "claude-3-5-sonnet-20241022" if "anthropic" in configured_providers else None
            ],
            "fallback_models": [
                "gpt-4o-mini-2024-07-18" if "openai" in configured_providers else None,
                "gpt-3.5-turbo-0125" if "openai" in configured_providers else None,
                "claude-3-5-haiku-20241022" if "anthropic" in configured_providers else None
            ]
        }
    
    def get_vision_model_selection(self) -> Dict[str, Any]:
        """Get vision/LMM model selection policy"""
        configured_providers = self.get_configured_vision_providers()
        
        if not configured_providers:
            return {
                "available": False,
                "error": "No vision/LMM providers configured",
                "models": [],
                "graceful_degradation": True
            }
        
        # Build model selection based on available providers
        models = []
        for provider_name in configured_providers:
            provider_config = self.vision_providers[provider_name]
            models.extend(provider_config.models)
        
        return {
            "available": True,
            "providers": configured_providers,
            "models": models,
            "primary_models": [
                "gemini-1.5-pro" if "gemini" in configured_providers else None,
                "gpt-4o-2024-08-06" if "openai_vision" in configured_providers else None
            ],
            "fallback_models": [
                "gpt-4o-2024-08-06" if "openai_vision" in configured_providers and "gemini" not in configured_providers else None
            ],
            "graceful_degradation": True
        }
    
    def get_refinement_model_selection(self) -> Dict[str, Any]:
        """Get refinement model selection policy (for Guided Prompt)"""
        configured_providers = self.get_configured_text_providers()
        
        if not configured_providers:
            return {
                "available": False,
                "error": "No refinement models available",
                "models": []
            }
        
        # Fast refinement models (≤500ms median)
        fast_models = []
        if "openai" in configured_providers:
            fast_models.append("gpt-3.5-turbo-0125")
        if "anthropic" in configured_providers:
            fast_models.append("claude-3-5-haiku-20241022")
        
        # Quality refinement models (≤800ms p95)
        quality_models = []
        if "openai" in configured_providers:
            quality_models.append("gpt-4o-mini-2024-07-18")
        if "anthropic" in configured_providers:
            quality_models.append("claude-3-5-sonnet-20241022")
        
        return {
            "available": len(fast_models + quality_models) > 0,
            "fast_models": fast_models,
            "quality_models": quality_models,
            "budget_limits": {
                "median_ms": self.refinement_budget_ms,
                "p95_ms": self.refinement_p95_budget_ms
            }
        }
    
    def is_text_llm_available(self) -> bool:
        """Check if text LLM is available"""
        return len(self.get_configured_text_providers()) > 0
    
    def is_vision_available(self) -> bool:
        """Check if vision/LMM is available"""
        return len(self.get_configured_vision_providers()) > 0
    
    def get_provider_api_key(self, provider_name: str) -> Optional[str]:
        """Get API key for a specific provider"""
        # Check text providers
        if provider_name in self.text_providers:
            provider_config = self.text_providers[provider_name]
            if provider_config.env_key:
                return get_provider_key(provider_config.env_key)
        
        # Check vision providers
        if provider_name in self.vision_providers:
            provider_config = self.vision_providers[provider_name]
            if provider_config.env_key:
                return get_provider_key(provider_config.env_key)
        
        return None
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get service health status"""
        text_selection = self.get_text_model_selection()
        vision_selection = self.get_vision_model_selection()
        refinement_selection = self.get_refinement_model_selection()
        
        return {
            "service": self.service_name,
            "status": "healthy" if text_selection["available"] else "degraded",
            "text_llm": {
                "available": text_selection["available"],
                "providers": text_selection.get("providers", []),
                "models": text_selection.get("models", []),
                "error": text_selection.get("error")
            },
            "vision_lmm": {
                "available": vision_selection["available"],
                "providers": vision_selection.get("providers", []),
                "models": vision_selection.get("models", []),
                "graceful_degradation": vision_selection.get("graceful_degradation", False),
                "error": vision_selection.get("error")
            },
            "refinement": {
                "available": refinement_selection["available"],
                "fast_models": refinement_selection.get("fast_models", []),
                "quality_models": refinement_selection.get("quality_models", []),
                "budget_limits": refinement_selection.get("budget_limits", {}),
                "error": refinement_selection.get("error")
            },
            "keyless_fallbacks_enabled": self.keyless_fallbacks_enabled
        }

# Global configuration instance
config = ModelRouterConfig()

# Convenience functions
def get_config() -> ModelRouterConfig:
    """Get the global configuration instance"""
    return config

def get_text_providers() -> Dict[str, ModelProviderConfig]:
    """Get text LLM provider configurations"""
    return config.get_text_providers()

def get_vision_providers() -> Dict[str, ModelProviderConfig]:
    """Get vision/LMM provider configurations"""
    return config.get_vision_providers()

def get_configured_text_providers() -> List[str]:
    """Get list of configured text LLM providers"""
    return config.get_configured_text_providers()

def get_configured_vision_providers() -> List[str]:
    """Get list of configured vision/LMM providers"""
    return config.get_configured_vision_providers()

def get_text_model_selection() -> Dict[str, Any]:
    """Get text model selection policy"""
    return config.get_text_model_selection()

def get_vision_model_selection() -> Dict[str, Any]:
    """Get vision/LMM model selection policy"""
    return config.get_vision_model_selection()

def get_refinement_model_selection() -> Dict[str, Any]:
    """Get refinement model selection policy"""
    return config.get_refinement_model_selection()

def is_text_llm_available() -> bool:
    """Check if text LLM is available"""
    return config.is_text_llm_available()

def is_vision_available() -> bool:
    """Check if vision/LMM is available"""
    return config.is_vision_available()

def get_provider_api_key(provider_name: str) -> Optional[str]:
    """Get API key for a specific provider"""
    return config.get_provider_api_key(provider_name)
