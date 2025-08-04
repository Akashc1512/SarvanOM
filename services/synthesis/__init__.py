"""
Synthesis Service for Universal Knowledge Hub.

This service handles AI-powered content synthesis and recommendations.
"""

__version__ = "1.0.0"

from .synthesis_service import SynthesisService
from .synthesis_agent import SynthesisAgent
from .citation_agent import CitationAgent

__all__ = ["SynthesisService", "SynthesisAgent", "CitationAgent"]
