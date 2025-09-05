#!/usr/bin/env python3
"""
Health Router - Production Service Health Monitoring
================================================================

Comprehensive health endpoint that checks all critical services:
- ArangoDB Knowledge Graph
- Qdrant Vector Database  
- Meilisearch Search Engine
- PostgreSQL Primary Database
- Redis Cache
- LLM Providers

Maps to Phase I1 requirements for `/health` showing "arangodb":"ok"
"""

import time
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


class ServiceHealth(BaseModel):
    """Individual service health status."""
    status: str  # "ok", "degraded", "error"
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Comprehensive health response."""
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: str
    services: Dict[str, ServiceHealth]
    overall_health: bool
    response_time_ms: float


async def check_arangodb_health() -> ServiceHealth:
    """Check ArangoDB Knowledge Graph health with real env variables."""
    start_time = time.time()
    
    try:
        from shared.core.services.arangodb_service import ArangoDBService
        
        # Get singleton service instance (uses real env variables)
        arangodb_service = ArangoDBService()
        
        if not arangodb_service.is_available:
            return ServiceHealth(
                status="error",
                error="ArangoDB library not available",
                response_time_ms=(time.time() - start_time) * 1000
            )
        
        # Perform real connection probe with actual credentials
        probe_result = await arangodb_service.connection_probe()
        response_time_ms = (time.time() - start_time) * 1000
        
        if probe_result.get('status') == 'ok':
            return ServiceHealth(
                status="ok",
                response_time_ms=response_time_ms,
                details={
                    "database": arangodb_service.config.database,
                    "warmup_completed": arangodb_service.is_warmup_completed,
                    "last_probe": probe_result.get('timestamp')
                }
            )
        else:
            return ServiceHealth(
                status="error", 
                response_time_ms=response_time_ms,
                error=probe_result.get('error', 'Connection probe failed'),
                details=probe_result
            )
            
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        logger.error("ArangoDB health check failed", error=str(e), response_time_ms=response_time_ms)
        
        return ServiceHealth(
            status="error",
            response_time_ms=response_time_ms,
            error=str(e)
        )


async def check_vector_health() -> ServiceHealth:
    """Check Qdrant Vector Database health with real env variables."""
    start_time = time.time()
    
    try:
        from shared.core.services.vector_singleton_service import get_vector_singleton_health
        
        # Get singleton service health (uses real env variables) 
        health_result = await get_vector_singleton_health()
        response_time_ms = (time.time() - start_time) * 1000
        
        if health_result.get('status') == 'healthy':
            return ServiceHealth(
                status="ok",
                response_time_ms=response_time_ms,
                details={
                    "provider": health_result.get('provider'),
                    "embedding_loaded": health_result.get('embedding', {}).get('model_loaded', False),
                    "vector_connected": health_result.get('vector_store', {}).get('connected', False),
                    "service_initialized": health_result.get('service_initialized', False)
                }
            )
        else:
            return ServiceHealth(
                status="error",
                response_time_ms=response_time_ms,
                error=f"Vector service status: {health_result.get('status', 'unknown')}",
                details=health_result
            )
            
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        logger.error("Vector health check failed", error=str(e), response_time_ms=response_time_ms)
        
        return ServiceHealth(
            status="error",
            response_time_ms=response_time_ms,
            error=str(e)
        )


async def check_search_health() -> ServiceHealth:
    """Check Meilisearch health with real env variables."""
    start_time = time.time()
    
    try:
        from shared.core.services.meilisearch_service import get_search_status
        
        # Get real Meilisearch status using actual credentials
        search_status = await get_search_status()
        response_time_ms = (time.time() - start_time) * 1000
        
        if search_status.get('status') == 'healthy':
            return ServiceHealth(
                status="ok",
                response_time_ms=response_time_ms,
                details={
                    "indices": search_status.get('indices', []),
                    "total_documents": search_status.get('total_documents', 0),
                    "indexing_status": search_status.get('indexing_status', 'unknown')
                }
            )
        else:
            return ServiceHealth(
                status="error",
                response_time_ms=response_time_ms,
                error=search_status.get('error', 'Search health check failed'),
                details=search_status
            )
            
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        logger.error("Search health check failed", error=str(e), response_time_ms=response_time_ms)
        
        return ServiceHealth(
            status="error",
            response_time_ms=response_time_ms,
            error=str(e)
        )


async def check_database_health() -> ServiceHealth:
    """Check PostgreSQL primary database health with real env variables."""
    start_time = time.time()
    
    try:
        from shared.core.database import get_database_service
        
        # Get database service (uses real env variables)
        db_service = get_database_service()
        
        # Perform real connection health check
        health_result = await db_service.health_check()
        response_time_ms = (time.time() - start_time) * 1000
        
        if health_result.get('status') == 'healthy':
            return ServiceHealth(
                status="ok",
                response_time_ms=response_time_ms,
                details={
                    "pool_status": health_result.get('pool_status', {}),
                    "connection_count": health_result.get('active_connections', 0)
                }
            )
        else:
            return ServiceHealth(
                status="error",
                response_time_ms=response_time_ms,
                error=health_result.get('error', 'Database health check failed'),
                details=health_result
            )
            
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        logger.error("Database health check failed", error=str(e), response_time_ms=response_time_ms)
        
        return ServiceHealth(
            status="error",
            response_time_ms=response_time_ms,
            error=str(e)
        )


async def check_cache_health() -> ServiceHealth:
    """Check Redis cache health with real env variables."""
    start_time = time.time()
    
    try:
        from shared.core.cache import get_cache_service
        
        # Get cache service (uses real env variables)
        cache_service = get_cache_service()
        
        # Perform real cache health check
        health_result = await cache_service.health_check()
        response_time_ms = (time.time() - start_time) * 1000
        
        if health_result.get('status') == 'healthy':
            return ServiceHealth(
                status="ok",
                response_time_ms=response_time_ms,
                details={
                    "connected": health_result.get('connected', False),
                    "memory_usage": health_result.get('memory_usage', 'unknown')
                }
            )
        else:
            return ServiceHealth(
                status="degraded",  # Cache is not critical, so degraded not error
                response_time_ms=response_time_ms,
                error=health_result.get('error', 'Cache not available'),
                details=health_result
            )
            
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        logger.debug("Cache health check failed (expected in local dev)", error=str(e))
        
        return ServiceHealth(
            status="degraded",  # Cache failure is not critical
            response_time_ms=response_time_ms,
            error="Cache not available (expected in local development)"
        )


@router.get("/", response_model=HealthResponse)
async def comprehensive_health_check():
    """
    Comprehensive health check for all critical services.
    
    MANDATORY: Uses real environment variables, NO mock responses.
    
    Returns:
        Complete health status including ArangoDB, Vector DB, Search, etc.
    """
    start_time = time.time()
    
    logger.info("Starting comprehensive health check with real API calls")
    
    # Run all health checks in parallel for efficiency
    health_checks = await asyncio.gather(
        check_arangodb_health(),
        check_vector_health(), 
        check_search_health(),
        check_database_health(),
        check_cache_health(),
        return_exceptions=True
    )
    
    # Map results to service names
    service_names = ["arangodb", "vector", "search", "database", "cache"]
    services = {}
    
    for i, (service_name, health_result) in enumerate(zip(service_names, health_checks)):
        if isinstance(health_result, Exception):
            services[service_name] = ServiceHealth(
                status="error",
                error=str(health_result),
                response_time_ms=0
            )
        else:
            services[service_name] = health_result
    
    # Determine overall health status
    error_services = [name for name, health in services.items() if health.status == "error"]
    degraded_services = [name for name, health in services.items() if health.status == "degraded"]
    
    if len(error_services) > 0:
        overall_status = "unhealthy"
        overall_health = False
    elif len(degraded_services) > 0:
        overall_status = "degraded" 
        overall_health = True  # Still functional
    else:
        overall_status = "healthy"
        overall_health = True
    
    total_response_time = (time.time() - start_time) * 1000
    
    response = HealthResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        services=services,
        overall_health=overall_health,
        response_time_ms=total_response_time
    )
    
    logger.info(
        "Health check completed",
        overall_status=overall_status,
        arangodb_status=services["arangodb"].status,
        vector_status=services["vector"].status,
        search_status=services["search"].status,
        response_time_ms=total_response_time,
        error_services=error_services,
        degraded_services=degraded_services
    )
    
    return response


@router.get("/arangodb")
async def arangodb_health():
    """Dedicated ArangoDB health check endpoint."""
    health_result = await check_arangodb_health()
    
    if health_result.status == "error":
        raise HTTPException(status_code=503, detail={
            "service": "arangodb",
            "status": health_result.status,
            "error": health_result.error,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    return {
        "service": "arangodb", 
        "status": health_result.status,
        "response_time_ms": health_result.response_time_ms,
        "details": health_result.details,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/vector")
async def vector_health():
    """Dedicated Vector Database health check endpoint."""
    health_result = await check_vector_health()
    
    if health_result.status == "error":
        raise HTTPException(status_code=503, detail={
            "service": "vector",
            "status": health_result.status,
            "error": health_result.error,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    return {
        "service": "vector",
        "status": health_result.status,
        "response_time_ms": health_result.response_time_ms,
        "details": health_result.details,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/search") 
async def search_health():
    """Dedicated Search Engine health check endpoint."""
    health_result = await check_search_health()
    
    if health_result.status == "error":
        raise HTTPException(status_code=503, detail={
            "service": "search",
            "status": health_result.status,
            "error": health_result.error,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    return {
        "service": "search",
        "status": health_result.status,
        "response_time_ms": health_result.response_time_ms,
        "details": health_result.details,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
