# DEAD CODE - Candidate for deletion: This backend directory is not used by the main application
"""
Search Service for Universal Knowledge Hub.

This service handles knowledge retrieval, vector search, and document indexing.
"""

__version__ = "1.0.0"

from .search_service import SearchService
from .retrieval_agent import RetrievalAgent

__all__ = ["SearchService", "RetrievalAgent"]
