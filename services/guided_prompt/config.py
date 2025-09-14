"""
Guided Prompt Service Configuration - SarvanOM v2

Configuration module for the Guided Prompt service that reads only canonical
environment variable names and implements safe fallbacks.

Features:
    - Canonical environment variable names only
    - Fail-fast for required providers
    - Safe fallbacks for optional providers
    - Integration with centralized provider config
"""

import os
import logging
from typing import Dict, Any, Optional
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
class GuidedPromptConfig:
    """Configuration for Guided Prompt service"""
    
    # Service settings
    service_name: str = "guided-prompt"
    port: int = 8003
    metrics_port: int = 8004
    
    # Model Router settings
    model_router_url: str = "http://localhost:8001"
    
    # Budget settings (from docs)
    median_budget_ms: int = 500
    p95_budget_ms: int = 800
    
    # Provider configurations
    openai_available: bool = False
    anthropic_available: bool = False
    gemini_available: bool = False
    
    # Feature flags
    keyless_fallbacks_enabled: bool = True
    
    def __post_init__(self):
        """Initialize provider availability after dataclass creation"""
        self._load_provider_configurations()
        self._log_configuration_status()
    
    def _load_provider_configurations(self):
        """Load provider configurations using canonical env keys only"""
        
        # Check AI provider availability (for refinement models)
        self.openai_available = is_provider_available("OPENAI_API_KEY")
        self.anthropic_available = is_provider_available("ANTHROPIC_API_KEY") 
        self.gemini_available = is_provider_available("GEMINI_API_KEY")
        
        # Get keyless fallbacks setting
        self.keyless_fallbacks_enabled = provider_config.keyless_fallbacks_enabled
        
        # Log provider status
        if not self.openai_available and not self.anthropic_available:
            logger.warning("No text LLM providers configured for refinement")
        elif not self.gemini_available:
            logger.info("Gemini not configured - vision refinement will use OpenAI fallback")
    
    def _log_configuration_status(self):
        """Log the configuration status"""
        logger.info(f"Guided Prompt Service Configuration:")
        logger.info(f"  OpenAI Available: {self.openai_available}")
        logger.info(f"  Anthropic Available: {self.anthropic_available}")
        logger.info(f"  Gemini Available: {self.gemini_available}")
        logger.info(f"  Keyless Fallbacks: {self.keyless_fallbacks_enabled}")
        
        # Log provider status
        log_provider_status()
    
    def get_available_refinement_models(self) -> Dict[str, bool]:
        """Get available refinement models"""
        return {
            "gpt-3.5-turbo": self.openai_available,
            "gpt-4o-mini": self.openai_available,
            "claude-3-5-haiku": self.anthropic_available,
            "claude-3-5-sonnet": self.anthropic_available,
            "gemini-1.5-pro": self.gemini_available
        }
    
    def get_refinement_model_selection(self) -> Dict[str, Any]:
        """Get refinement model selection policy"""
        available_models = self.get_available_refinement_models()
        
        # Fast refinement (≤500ms median)
        fast_models = []
        if available_models["gpt-3.5-turbo"]:
            fast_models.append("gpt-3.5-turbo")
        if available_models["claude-3-5-haiku"]:
            fast_models.append("claude-3-5-haiku")
        
        # Quality refinement (≤800ms p95)
        quality_models = []
        if available_models["gpt-4o-mini"]:
            quality_models.append("gpt-4o-mini")
        if available_models["claude-3-5-sonnet"]:
            quality_models.append("claude-3-5-sonnet")
        
        # Vision refinement
        vision_models = []
        if available_models["gemini-1.5-pro"]:
            vision_models.append("gemini-1.5-pro")
        elif available_models["gpt-4o-mini"]:
            vision_models.append("gpt-4o-mini")  # OpenAI vision fallback
        
        return {
            "fast": fast_models,
            "quality": quality_models,
            "vision": vision_models,
            "has_any_model": len(fast_models + quality_models + vision_models) > 0
        }
    
    def should_enable_guided_prompt(self) -> bool:
        """Determine if guided prompt should be enabled"""
        model_selection = self.get_refinement_model_selection()
        return model_selection["has_any_model"]
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get service health status"""
        model_selection = self.get_refinement_model_selection()
        
        return {
            "service": self.service_name,
            "status": "healthy" if model_selection["has_any_model"] else "degraded",
            "providers": {
                "openai": self.openai_available,
                "anthropic": self.anthropic_available,
                "gemini": self.gemini_available
            },
            "refinement_models": model_selection,
            "keyless_fallbacks_enabled": self.keyless_fallbacks_enabled,
            "budget_limits": {
                "median_ms": self.median_budget_ms,
                "p95_ms": self.p95_budget_ms
            }
        }

# Global configuration instance
config = GuidedPromptConfig()

# Convenience functions
def get_config() -> GuidedPromptConfig:
    """Get the global configuration instance"""
    return config

def get_provider_summary() -> Dict[str, Any]:
    """Get provider configuration summary"""
    return get_provider_summary()

def is_guided_prompt_enabled() -> bool:
    """Check if guided prompt is enabled"""
    return config.should_enable_guided_prompt()

def get_available_models() -> Dict[str, bool]:
    """Get available refinement models"""
    return config.get_available_refinement_models()
