"""
Synthesis Microservice
Handles content synthesis and generation functionality.

This microservice provides:
- Content synthesis from multiple sources
- Citation management
- Content generation
- RESTful API endpoints
"""

from .synthesis_service import SynthesisService
from .api import router as synthesis_router

__all__ = [
    "SynthesisService",
    "synthesis_router"
] 