"""
Dependencies for API endpoints.

This module contains all dependency injection functions for FastAPI endpoints.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..services.query.query_orchestrator import QueryOrchestrator
from ..services.query.query_processor import QueryProcessor
from ..services.query.query_validator import QueryValidator
from ..services.core.cache_service import CacheService
from ..services.core.metrics_service import MetricsService
from ..services.agents.agent_coordinator import AgentCoordinator
from ..services.health.health_service import HealthService
from ..services.agents.agent_service import AgentService
from ..services.core.database_service import DatabaseService

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer(auto_error=False)


# Service instances (singletons)
_cache_service: Optional[CacheService] = None
_metrics_service: Optional[MetricsService] = None
_agent_coordinator: Optional[AgentCoordinator] = None
_agent_service: Optional[AgentService] = None
_query_processor: Optional[QueryProcessor] = None
_query_validator: Optional[QueryValidator] = None
_query_orchestrator: Optional[QueryOrchestrator] = None
_health_service: Optional[HealthService] = None
_database_service: Optional[DatabaseService] = None


def get_cache_service() -> CacheService:
    """Get cache service instance."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
        logger.info("Initialized CacheService")
    return _cache_service


def get_metrics_service() -> MetricsService:
    """Get metrics service instance."""
    global _metrics_service
    if _metrics_service is None:
        _metrics_service = MetricsService()
        logger.info("Initialized MetricsService")
    return _metrics_service


def get_agent_coordinator() -> AgentCoordinator:
    """Get agent coordinator instance."""
    global _agent_coordinator
    if _agent_coordinator is None:
        _agent_coordinator = AgentCoordinator()
        logger.info("Initialized AgentCoordinator")
    return _agent_coordinator


def get_agent_service() -> AgentService:
    """Get agent service instance."""
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
        logger.info("Initialized AgentService")
    return _agent_service


def get_query_processor() -> QueryProcessor:
    """Get query processor instance."""
    global _query_processor
    if _query_processor is None:
        cache_service = get_cache_service()
        agent_coordinator = get_agent_coordinator()
        _query_processor = QueryProcessor(agent_coordinator, cache_service)
        logger.info("Initialized QueryProcessor")
    return _query_processor


def get_query_validator() -> QueryValidator:
    """Get query validator instance."""
    global _query_validator
    if _query_validator is None:
        _query_validator = QueryValidator()
        logger.info("Initialized QueryValidator")
    return _query_validator


def get_query_orchestrator() -> QueryOrchestrator:
    """Get query orchestrator instance."""
    global _query_orchestrator
    if _query_orchestrator is None:
        query_processor = get_query_processor()
        query_validator = get_query_validator()
        cache_service = get_cache_service()
        metrics_service = get_metrics_service()
        _query_orchestrator = QueryOrchestrator(
            query_processor, 
            query_validator, 
            cache_service, 
            metrics_service
        )
        logger.info("Initialized QueryOrchestrator")
    return _query_orchestrator


def get_health_service() -> HealthService:
    """Get health service instance."""
    global _health_service
    if _health_service is None:
        _health_service = HealthService()
        logger.info("Initialized HealthService")
    return _health_service


def get_database_service() -> DatabaseService:
    """Get database service instance."""
    global _database_service
    if _database_service is None:
        _database_service = DatabaseService()
        logger.info("Initialized DatabaseService")
    return _database_service


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """Get current user from request."""
    # TODO: Implement proper authentication
    # For now, return anonymous user
    return {
        "user_id": "anonymous",
        "username": "anonymous",
        "role": "anonymous",
        "is_authenticated": False
    }


async def require_authentication(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Require authentication for protected endpoints."""
    if not current_user.get("is_authenticated", False):
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    return current_user


async def require_admin(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Require admin role for admin endpoints."""
    if not current_user.get("is_authenticated", False):
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    return current_user


def get_request_id(request: Request) -> str:
    """Get request ID from request state."""
    return getattr(request.state, "request_id", "unknown")


def get_user_context(
    current_user: Dict[str, Any] = Depends(get_current_user),
    request: Request = None
) -> Dict[str, Any]:
    """Get user context for request processing."""
    return {
        "user_id": current_user.get("user_id", "anonymous"),
        "username": current_user.get("username", "anonymous"),
        "role": current_user.get("role", "anonymous"),
        "is_authenticated": current_user.get("is_authenticated", False),
        "request_id": get_request_id(request) if request else "unknown"
    } 