"""
Admin Router

This module contains administrative endpoints.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from ...services.core.cache_service import CacheService
from ...services.core.metrics_service import MetricsService
from ...services.agents.agent_coordinator import AgentCoordinator
from ..dependencies import get_cache_service, get_metrics_service, get_agent_coordinator, require_admin

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/")
async def admin_dashboard(
    current_user=Depends(require_admin),
    cache_service: CacheService = Depends(get_cache_service),
    metrics_service: MetricsService = Depends(get_metrics_service),
    agent_coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """Admin dashboard with system overview."""
    try:
        # Get system statistics
        cache_stats = await cache_service.get_stats()
        metrics_summary = metrics_service.get_metrics_summary()
        agent_pool_stats = agent_coordinator.get_agent_pool_stats()
        
        return {
            "dashboard": {
                "cache": cache_stats,
                "metrics": metrics_summary,
                "agents": agent_pool_stats
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting admin dashboard: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error retrieving dashboard")


@router.post("/cache/clear")
async def clear_cache(
    current_user=Depends(require_admin),
    cache_service: CacheService = Depends(get_cache_service)
):
    """Clear all cache entries."""
    try:
        success = await cache_service.clear()
        if success:
            return {
                "message": "Cache cleared successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear cache")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing cache: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error clearing cache")


@router.post("/metrics/reset")
async def reset_metrics(
    current_user=Depends(require_admin),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Reset all metrics."""
    try:
        metrics_service.reset_metrics()
        return {
            "message": "Metrics reset successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error resetting metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error resetting metrics")


@router.post("/agents/cleanup")
async def cleanup_agents(
    current_user=Depends(require_admin),
    agent_coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """Clean up inactive agents."""
    try:
        cleaned_count = await agent_coordinator.cleanup_inactive_agents()
        return {
            "cleaned_count": cleaned_count,
            "message": f"Cleaned up {cleaned_count} inactive agents",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up agents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error cleaning up agents")


@router.get("/system/status")
async def system_status(
    current_user=Depends(require_admin),
    cache_service: CacheService = Depends(get_cache_service),
    metrics_service: MetricsService = Depends(get_metrics_service),
    agent_coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """Get comprehensive system status."""
    try:
        # Get all system components status
        cache_stats = await cache_service.get_stats()
        metrics_summary = metrics_service.get_metrics_summary()
        agent_pool_stats = agent_coordinator.get_agent_pool_stats()
        
        # Determine overall system health
        overall_status = "healthy"
        issues = []
        
        # Check cache health
        if cache_stats.get("total_entries", 0) > 10000:
            issues.append("Cache has too many entries")
        
        # Check metrics health
        if metrics_summary.get("error_rate", 0) > 0.1:
            issues.append("High error rate detected")
        
        # Check agent health
        if agent_pool_stats.get("error_agents", 0) > 0:
            issues.append("Some agents are in error state")
        
        if issues:
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "issues": issues,
            "components": {
                "cache": {
                    "status": "healthy" if cache_stats.get("total_entries", 0) < 10000 else "warning",
                    "stats": cache_stats
                },
                "metrics": {
                    "status": "healthy" if metrics_summary.get("error_rate", 0) < 0.1 else "warning",
                    "summary": metrics_summary
                },
                "agents": {
                    "status": "healthy" if agent_pool_stats.get("error_agents", 0) == 0 else "warning",
                    "stats": agent_pool_stats
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error retrieving system status") 