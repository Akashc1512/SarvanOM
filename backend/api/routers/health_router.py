"""
Health Router

This module contains health check and monitoring endpoints.
Migrated from the original health routes with enhanced functionality.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from ...services.core.cache_service import CacheService
from ...services.core.metrics_service import MetricsService
from ...services.health.health_service import HealthService
from ..dependencies import get_cache_service, get_metrics_service, get_health_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check(health_service: HealthService = Depends(get_health_service)):
    """Comprehensive health check endpoint."""
    try:
        health_data = await health_service.get_system_health()
        return health_data
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Service unhealthy")


@router.get("/basic")
async def basic_health_check(
    health_service: HealthService = Depends(get_health_service),
):
    """Basic health check for load balancers."""
    try:
        health_data = await health_service.get_basic_health()
        return health_data
    except Exception as e:
        logger.error(f"Basic health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "service": "sarvanom-backend",
        }


@router.get("/detailed")
async def detailed_health_check(
    health_service: HealthService = Depends(get_health_service),
):
    """Detailed health check with comprehensive metrics."""
    try:
        health_data = await health_service.get_detailed_metrics()
        return health_data
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Service unhealthy")


@router.get("/diagnostics")
async def system_diagnostics(
    health_service: HealthService = Depends(get_health_service),
):
    """Get comprehensive system diagnostics."""
    try:
        diagnostics = await health_service.get_system_diagnostics()
        return diagnostics
    except Exception as e:
        logger.error(f"System diagnostics failed: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Diagnostics unavailable")


@router.get("/cache")
async def cache_health_check(cache_service: CacheService = Depends(get_cache_service)):
    """Cache-specific health check."""
    try:
        stats = await cache_service.get_stats()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "cache_stats": stats,
        }

    except Exception as e:
        logger.error(f"Cache health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Cache service unhealthy")


@router.get("/metrics")
async def metrics_health_check(
    metrics_service: MetricsService = Depends(get_metrics_service),
):
    """Metrics-specific health check."""
    try:
        summary = metrics_service.get_metrics_summary()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "metrics_summary": summary,
        }

    except Exception as e:
        logger.error(f"Metrics health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Metrics service unhealthy")
