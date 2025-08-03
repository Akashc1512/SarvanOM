"""
Fact-Check Microservice
Handles fact-checking and validation functionality.

This microservice provides:
- Content fact-checking
- Source validation
- Confidence scoring
- RESTful API endpoints
"""

from .factcheck_service import FactCheckService
from .api import router as factcheck_router

__all__ = [
    "FactCheckService",
    "factcheck_router"
] 