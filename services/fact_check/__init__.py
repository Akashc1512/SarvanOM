# DEAD CODE - Candidate for deletion: This backend directory is not used by the main application
"""
Fact Check Service for Universal Knowledge Hub.

This service handles fact verification and source validation.
"""

__version__ = "1.0.0"

from .factcheck_service import FactCheckService
from .factcheck_agent import FactCheckAgent

__all__ = ["FactCheckService", "FactCheckAgent"]
