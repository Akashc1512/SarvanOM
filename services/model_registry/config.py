"""
Model Registry Service Configuration - SarvanOM v2

Configuration module for the Model Registry service that reads only canonical
environment variable names and implements safe fallbacks.

Features:
    - Canonical environment variable names only
    - Fail-fast for required providers
    - Safe fallbacks for optional providers
    - Provider health status tracking
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
class RegistryProviderConfig:
    """Configuration for a registry provider"""
    name: str
    env_key: Optional[str]
    is_configured: bool
    is_required: bool
    models: List[str]
    status: str = "inactive"

@dataclass
class ModelRegistryConfig:
    """Configuration for Model Registry service"""
    
    # Service settings
    service_name: str = "model-registry"
    port: int = 8000
    metrics_port: int = 8001
    
    # Provider configurations
    providers: Dict[str, RegistryProviderConfig] = None
    
    # Feature flags
    keyless_fallbacks_enabled: bool = True
    
    def __post_init__(self):
        """Initialize provider configurations after dataclass creation"""
        if self.providers is None:
            self.providers = {}
        self._load_provider_configurations()
        self._log_configuration_status()
    
    def _load_provider_configurations(self):
        """Load provider configurations using canonical env keys only"""
        
        # AI Providers
        self.providers = {
            "openai": RegistryProviderConfig(
                name="OpenAI",
                env_key="OPENAI_API_KEY",
                is_configured=is_provider_available("OPENAI_API_KEY"),
                is_required=True,  # Required for text LLMs
                models=["gpt-4o-2024-08-06", "gpt-4o-mini-2024-07-18", "gpt-3.5-turbo-0125"],
                status="active" if is_provider_available("OPENAI_API_KEY") else "inactive"
            ),
            "anthropic": RegistryProviderConfig(
                name="Anthropic",
                env_key="ANTHROPIC_API_KEY",
                is_configured=is_provider_available("ANTHROPIC_API_KEY"),
                is_required=True,  # Required for text LLMs
                models=["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
                status="active" if is_provider_available("ANTHROPIC_API_KEY") else "inactive"
            ),
            "gemini": RegistryProviderConfig(
                name="Google Gemini",
                env_key="GEMINI_API_KEY",
                is_configured=is_provider_available("GEMINI_API_KEY"),
                is_required=False,  # Optional for vision
                models=["gemini-1.5-pro"],
                status="active" if is_provider_available("GEMINI_API_KEY") else "inactive"
            ),
            "huggingface": RegistryProviderConfig(
                name="HuggingFace",
                env_key="HUGGINGFACE_API_KEY",
                is_configured=is_provider_available("HUGGINGFACE_API_KEY"),
                is_required=False,  # Optional
                models=[],  # Would be populated from HF Hub
                status="active" if is_provider_available("HUGGINGFACE_API_KEY") else "inactive"
            )
        }
        
        # Get keyless fallbacks setting
        self.keyless_fallbacks_enabled = provider_config.keyless_fallbacks_enabled
    
    def _log_configuration_status(self):
        """Log the configuration status"""
        logger.info(f"Model Registry Service Configuration:")
        logger.info(f"  Keyless Fallbacks: {self.keyless_fallbacks_enabled}")
        
        logger.info("  Providers:")
        for provider_name, provider_config in self.providers.items():
            status_icon = "✅" if provider_config.is_configured else "❌" if provider_config.is_required else "⚠️"
            logger.info(f"    {status_icon} {provider_config.name}: {provider_config.status}")
            if provider_config.is_configured and provider_config.models:
                logger.info(f"      Models: {', '.join(provider_config.models)}")
        
        # Log provider status
        log_provider_status()
    
    def get_providers(self) -> Dict[str, RegistryProviderConfig]:
        """Get provider configurations"""
        return self.providers
    
    def get_configured_providers(self) -> List[str]:
        """Get list of configured providers"""
        return [name for name, config in self.providers.items() if config.is_configured]
    
    def get_active_providers(self) -> List[str]:
        """Get list of active providers"""
        return [name for name, config in self.providers.items() if config.status == "active"]
    
    def get_inactive_providers(self) -> List[str]:
        """Get list of inactive providers"""
        return [name for name, config in self.providers.items() if config.status == "inactive"]
    
    def get_available_models(self) -> List[str]:
        """Get list of all available models from configured providers"""
        models = []
        for provider_name, provider_config in self.providers.items():
            if provider_config.is_configured:
                models.extend(provider_config.models)
        return models
    
    def get_models_by_provider(self, provider_name: str) -> List[str]:
        """Get models for a specific provider"""
        provider_config = self.providers.get(provider_name)
        if provider_config and provider_config.is_configured:
            return provider_config.models
        return []
    
    def get_stable_models(self) -> List[str]:
        """Get stable models (all configured models are considered stable)"""
        return self.get_available_models()
    
    def get_refiner_models(self) -> List[str]:
        """Get models suitable for refinement (fast & cheap)"""
        refiner_models = []
        for provider_name, provider_config in self.providers.items():
            if provider_config.is_configured:
                # Filter for fast/cheap models
                if provider_name == "openai":
                    refiner_models.extend(["gpt-3.5-turbo-0125", "gpt-4o-mini-2024-07-18"])
                elif provider_name == "anthropic":
                    refiner_models.append("claude-3-5-haiku-20241022")
        return refiner_models
    
    def get_vision_models(self) -> List[str]:
        """Get vision/multimodal models"""
        vision_models = []
        for provider_name, provider_config in self.providers.items():
            if provider_config.is_configured:
                if provider_name == "gemini":
                    vision_models.extend(["gemini-1.5-pro"])
                elif provider_name == "openai":
                    vision_models.extend(["gpt-4o-2024-08-06"])
        return vision_models
    
    def get_provider_api_key(self, provider_name: str) -> Optional[str]:
        """Get API key for a specific provider"""
        provider_config = self.providers.get(provider_name)
        if provider_config and provider_config.env_key:
            return get_provider_key(provider_config.env_key)
        return None
    
    def update_provider_status(self, provider_name: str, status: str):
        """Update provider status"""
        if provider_name in self.providers:
            self.providers[provider_name].status = status
            logger.info(f"Updated {provider_name} status to {status}")
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get service health status"""
        configured_providers = self.get_configured_providers()
        active_providers = self.get_active_providers()
        available_models = self.get_available_models()
        
        return {
            "service": self.service_name,
            "status": "healthy" if len(configured_providers) > 0 else "degraded",
            "providers": {
                "total": len(self.providers),
                "configured": len(configured_providers),
                "active": len(active_providers),
                "inactive": len(self.get_inactive_providers())
            },
            "models": {
                "total": len(available_models),
                "stable": len(self.get_stable_models()),
                "refiners": len(self.get_refiner_models()),
                "vision": len(self.get_vision_models())
            },
            "provider_details": {
                name: {
                    "status": config.status,
                    "configured": config.is_configured,
                    "required": config.is_required,
                    "models": config.models
                }
                for name, config in self.providers.items()
            },
            "keyless_fallbacks_enabled": self.keyless_fallbacks_enabled
        }

# Global configuration instance
config = ModelRegistryConfig()

# Convenience functions
def get_config() -> ModelRegistryConfig:
    """Get the global configuration instance"""
    return config

def get_providers() -> Dict[str, RegistryProviderConfig]:
    """Get provider configurations"""
    return config.get_providers()

def get_configured_providers() -> List[str]:
    """Get list of configured providers"""
    return config.get_configured_providers()

def get_active_providers() -> List[str]:
    """Get list of active providers"""
    return config.get_active_providers()

def get_available_models() -> List[str]:
    """Get list of all available models"""
    return config.get_available_models()

def get_models_by_provider(provider_name: str) -> List[str]:
    """Get models for a specific provider"""
    return config.get_models_by_provider(provider_name)

def get_stable_models() -> List[str]:
    """Get stable models"""
    return config.get_stable_models()

def get_refiner_models() -> List[str]:
    """Get refiner models"""
    return config.get_refiner_models()

def get_vision_models() -> List[str]:
    """Get vision models"""
    return config.get_vision_models()

def get_provider_api_key(provider_name: str) -> Optional[str]:
    """Get API key for a specific provider"""
    return config.get_provider_api_key(provider_name)

def update_provider_status(provider_name: str, status: str):
    """Update provider status"""
    config.update_provider_status(provider_name, status)
