"""
Retrieval Microservice
Handles search and document retrieval functionality.

This microservice provides:
- Document search and retrieval
- Query processing and classification
- Hybrid retrieval (vector + keyword)
- Search result ranking and filtering
- RESTful API endpoints
"""

from .search_service import SearchService
from .api import router as retrieval_router

__all__ = [
    "SearchService",
    "retrieval_router"
] 