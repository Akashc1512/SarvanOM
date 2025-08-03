"""
Retrieval Service
Handles search and document retrieval functionality.

This service provides:
- Document search and retrieval
- Query processing and classification
- Hybrid retrieval (vector + keyword)
- Search result ranking and filtering
"""

from .search_service import SearchService

__all__ = [
    "SearchService"
] 