"""
SarvanOM LLM Provider Registry
Centralized registry for all LLM providers with environment-driven configuration.
"""

from typing import Dict, Type, Optional
from enum import Enum
import logging

from .base import LLMProvider
from .registry import register, get_registry, get_ordered_providers

logger = logging.getLogger(__name__)

class LLMProvider(str, Enum):
    """Supported LLM providers with zero-budget optimization."""
    OLLAMA = "ollama"      # Local models (free)
    HUGGINGFACE = "huggingface"  # Free tier API
    OPENAI = "openai"      # Paid (fallback)
    ANTHROPIC = "anthropic"  # Paid (fallback)
    # Removed local_stub and mock - no mock responses allowed

# Import provider client classes
try:
    from .openai_client import OpenAIClient
    OPENAI_AVAILABLE = True
except ImportError:
    OpenAIClient = None
    OPENAI_AVAILABLE = False

try:
    from .anthropic_client import AnthropicClient
    ANTHROPIC_AVAILABLE = True
except ImportError:
    AnthropicClient = None
    ANTHROPIC_AVAILABLE = False

try:
    from .huggingface_client import HuggingFaceClient
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HuggingFaceClient = None
    HUGGINGFACE_AVAILABLE = False

try:
    from .ollama_client import OllamaClient
    OLLAMA_AVAILABLE = True
except ImportError:
    OllamaClient = None
    OLLAMA_AVAILABLE = False

# Removed local_stub_client - no mock responses allowed

# Centralized provider registry
PROVIDERS: Dict[str, Optional[Type]] = {}

# Register available providers
if OPENAI_AVAILABLE and OpenAIClient:
    PROVIDERS["openai"] = OpenAIClient
    logger.info("✅ OpenAI provider registered")

if ANTHROPIC_AVAILABLE and AnthropicClient:
    PROVIDERS["anthropic"] = AnthropicClient
    logger.info("✅ Anthropic provider registered")

if HUGGINGFACE_AVAILABLE and HuggingFaceClient:
    PROVIDERS["huggingface"] = HuggingFaceClient
    logger.info("✅ HuggingFace provider registered")

if OLLAMA_AVAILABLE and OllamaClient:
    PROVIDERS["ollama"] = OllamaClient
    logger.info("✅ Ollama provider registered")

# Removed local_stub provider registration - no mock responses allowed

# Log registry status
logger.info(f"📋 LLM Provider Registry initialized with {len(PROVIDERS)} providers: {list(PROVIDERS.keys())}")

def get_provider(provider_name: str):
    """Get a provider client by name."""
    return PROVIDERS.get(provider_name.lower())

def get_available_providers() -> list:
    """Get list of available provider names."""
    return list(PROVIDERS.keys())

def is_provider_available(provider_name: str) -> bool:
    """Check if a provider is available."""
    return provider_name.lower() in PROVIDERS
