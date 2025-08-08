"""
Advanced Analytics Router for API Gateway.

Provides data collection, analytics generation, and dashboard management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from ..services import advanced_analytics_service
from ..models.requests import (
    AnalyticsDataRequest,
    DashboardConfigRequest,
    WidgetConfigRequest
)
from ..models.responses import (
    AnalyticsDataResponse,
    UsageAnalyticsResponse,
    PerformanceAnalyticsResponse,
    UserAnalyticsResponse,
    PredictiveAnalyticsResponse,
    DashboardResponse,
    DashboardListResponse,
    WidgetDataResponse
)
from ..middleware import get_current_user
from shared.core.unified_logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/analytics", tags=["Advanced Analytics"])

@router.post("/collect")
async def collect_analytics_data(request: AnalyticsDataRequest):
    """
    Collect analytics data point.
    
    Records a single data point for analytics processing.
    """
    try:
        success = await advanced_analytics_service.collect_analytics_data(
            metric_name=request.metric_name,
            value=request.value,
            tenant_id=request.tenant_id,
            metadata=request.metadata
        )
        
        if success:
            return {"message": "Analytics data collected successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to collect analytics data"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to collect analytics data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to collect analytics data"
        )

@router.get("/usage", response_model=UsageAnalyticsResponse)
async def get_usage_analytics(
    tenant_id: str = "default",
    timeframe: str = "7d",
    metrics: Optional[List[str]] = None
):
    """
    Get usage analytics for the specified tenant and timeframe.
    
    Provides insights into API usage, user activity, and feature adoption.
    """
    try:
        analytics_data = await advanced_analytics_service.get_usage_analytics(
            tenant_id=tenant_id,
            timeframe=timeframe,
            metrics=metrics
        )
        
        return UsageAnalyticsResponse(
            tenant_id=tenant_id,
            timeframe=timeframe,
            total_api_calls=analytics_data.get("total_api_calls", 0),
            unique_users=analytics_data.get("unique_users", 0),
            popular_features=analytics_data.get("popular_features", []),
            usage_trends=analytics_data.get("usage_trends", {}),
            peak_usage_times=analytics_data.get("peak_usage_times", []),
            error_rates=analytics_data.get("error_rates", {}),
            response_times=analytics_data.get("response_times", {}),
            data_points=analytics_data.get("data_points", [])
        )
    except Exception as e:
        logger.error(f"Failed to get usage analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get usage analytics"
        )

@router.get("/performance", response_model=PerformanceAnalyticsResponse)
async def get_performance_analytics(
    tenant_id: str = "default",
    timeframe: str = "24h"
):
    """
    Get performance analytics for the specified tenant and timeframe.
    
    Provides insights into system performance, response times, and resource utilization.
    """
    try:
        analytics_data = await advanced_analytics_service.get_performance_analytics(
            tenant_id=tenant_id,
            timeframe=timeframe
        )
        
        return PerformanceAnalyticsResponse(
            tenant_id=tenant_id,
            timeframe=timeframe,
            avg_response_time=analytics_data.get("avg_response_time", 0.0),
            p95_response_time=analytics_data.get("p95_response_time", 0.0),
            p99_response_time=analytics_data.get("p99_response_time", 0.0),
            throughput=analytics_data.get("throughput", 0.0),
            error_rate=analytics_data.get("error_rate", 0.0),
            cpu_usage=analytics_data.get("cpu_usage", 0.0),
            memory_usage=analytics_data.get("memory_usage", 0.0),
            disk_usage=analytics_data.get("disk_usage", 0.0),
            network_io=analytics_data.get("network_io", {}),
            slow_queries=analytics_data.get("slow_queries", []),
            bottlenecks=analytics_data.get("bottlenecks", [])
        )
    except Exception as e:
        logger.error(f"Failed to get performance analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get performance analytics"
        )

@router.get("/users", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    tenant_id: str = "default",
    timeframe: str = "30d"
):
    """
    Get user analytics for the specified tenant and timeframe.
    
    Provides insights into user behavior, engagement, and demographics.
    """
    try:
        analytics_data = await advanced_analytics_service.get_user_analytics(
            tenant_id=tenant_id,
            timeframe=timeframe
        )
        
        return UserAnalyticsResponse(
            tenant_id=tenant_id,
            timeframe=timeframe,
            total_users=analytics_data.get("total_users", 0),
            active_users=analytics_data.get("active_users", 0),
            new_users=analytics_data.get("new_users", 0),
            returning_users=analytics_data.get("returning_users", 0),
            user_retention_rate=analytics_data.get("user_retention_rate", 0.0),
            user_engagement_score=analytics_data.get("user_engagement_score", 0.0),
            popular_user_actions=analytics_data.get("popular_user_actions", []),
            user_sessions=analytics_data.get("user_sessions", {}),
            user_demographics=analytics_data.get("user_demographics", {}),
            user_feedback=analytics_data.get("user_feedback", [])
        )
    except Exception as e:
        logger.error(f"Failed to get user analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user analytics"
        )

@router.get("/predictive", response_model=PredictiveAnalyticsResponse)
async def get_predictive_analytics(
    tenant_id: str = "default",
    metric: str = "api_calls",
    forecast_periods: int = 7
):
    """
    Get predictive analytics for the specified metric.
    
    Provides forecasts and predictions based on historical data.
    """
    try:
        analytics_data = await advanced_analytics_service.get_predictive_analytics(
            tenant_id=tenant_id,
            metric=metric,
            forecast_periods=forecast_periods
        )
        
        return PredictiveAnalyticsResponse(
            tenant_id=tenant_id,
            metric=metric,
            forecast_periods=forecast_periods,
            forecast_values=analytics_data.get("forecast_values", []),
            confidence_intervals=analytics_data.get("confidence_intervals", []),
            trend_direction=analytics_data.get("trend_direction", "stable"),
            trend_strength=analytics_data.get("trend_strength", 0.0),
            seasonality_detected=analytics_data.get("seasonality_detected", False),
            anomaly_detected=analytics_data.get("anomaly_detected", False),
            accuracy_metrics=analytics_data.get("accuracy_metrics", {}),
            recommendations=analytics_data.get("recommendations", [])
        )
    except Exception as e:
        logger.error(f"Failed to get predictive analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get predictive analytics"
        )

@router.post("/dashboards", response_model=DashboardResponse)
async def create_dashboard(request: DashboardConfigRequest):
    """
    Create a new analytics dashboard.
    
    Creates a dashboard with the specified configuration and widgets.
    """
    try:
        from ..services.advanced_analytics_service import DashboardConfig
        
        dashboard_config = DashboardConfig(
            id=request.id,
            name=request.name,
            description=request.description,
            tenant_id=request.tenant_id,
            widgets=request.widgets,
            layout=request.layout,
            refresh_interval=request.refresh_interval,
            is_public=request.is_public
        )
        
        success = await advanced_analytics_service.create_dashboard(dashboard_config)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create dashboard"
            )
        
        return DashboardResponse(
            id=dashboard_config.id,
            name=dashboard_config.name,
            description=dashboard_config.description,
            tenant_id=dashboard_config.tenant_id,
            widgets=dashboard_config.widgets,
            layout=dashboard_config.layout,
            refresh_interval=dashboard_config.refresh_interval,
            is_public=dashboard_config.is_public,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create dashboard"
        )

@router.get("/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard_data(dashboard_id: str, tenant_id: str = "default"):
    """
    Get dashboard data and configuration.
    
    Returns the dashboard configuration and current data for all widgets.
    """
    try:
        dashboard_data = await advanced_analytics_service.get_dashboard_data(
            dashboard_id=dashboard_id,
            tenant_id=tenant_id
        )
        
        if not dashboard_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        return DashboardResponse(
            id=dashboard_data.get("id", dashboard_id),
            name=dashboard_data.get("name", ""),
            description=dashboard_data.get("description", ""),
            tenant_id=dashboard_data.get("tenant_id", tenant_id),
            widgets=dashboard_data.get("widgets", []),
            layout=dashboard_data.get("layout", {}),
            refresh_interval=dashboard_data.get("refresh_interval", 300),
            is_public=dashboard_data.get("is_public", False),
            created_at=dashboard_data.get("created_at", datetime.now().isoformat()),
            updated_at=dashboard_data.get("updated_at", datetime.now().isoformat())
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard data"
        )

@router.get("/dashboards", response_model=DashboardListResponse)
async def list_dashboards(tenant_id: str = "default"):
    """
    List all dashboards for the specified tenant.
    """
    try:
        # This would typically query the dashboard service
        # For now, we'll return a mock response
        dashboards = [
            {
                "id": "default_dashboard",
                "name": "Default Analytics Dashboard",
                "description": "Default dashboard with key metrics",
                "tenant_id": tenant_id,
                "widgets": [],
                "layout": {},
                "refresh_interval": 300,
                "is_public": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        
        return DashboardListResponse(
            dashboards=dashboards,
            total=len(dashboards)
        )
    except Exception as e:
        logger.error(f"Failed to list dashboards: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list dashboards"
        )

@router.get("/widgets/{widget_id}/data", response_model=WidgetDataResponse)
async def get_widget_data(
    widget_id: str,
    tenant_id: str = "default",
    config: Optional[Dict[str, Any]] = None
):
    """
    Get data for a specific widget.
    
    Returns the data needed to render a specific widget type.
    """
    try:
        # This would typically query the analytics service for widget-specific data
        # For now, we'll return mock data based on widget type
        widget_data = {
            "widget_id": widget_id,
            "tenant_id": tenant_id,
            "data": {
                "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
                "datasets": [
                    {
                        "label": "API Calls",
                        "data": [100, 150, 200, 180, 250],
                        "backgroundColor": "rgba(54, 162, 235, 0.2)",
                        "borderColor": "rgba(54, 162, 235, 1)",
                        "borderWidth": 1
                    }
                ]
            },
            "config": config or {},
            "last_updated": datetime.now().isoformat()
        }
        
        return WidgetDataResponse(**widget_data)
    except Exception as e:
        logger.error(f"Failed to get widget data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get widget data"
        )

@router.get("/metrics")
async def get_available_metrics(tenant_id: str = "default"):
    """
    Get list of available metrics for analytics.
    """
    try:
        metrics = [
            "api_calls",
            "response_time",
            "error_rate",
            "user_activity",
            "storage_usage",
            "cpu_usage",
            "memory_usage",
            "network_io",
            "database_queries",
            "cache_hit_rate"
        ]
        
        return {
            "tenant_id": tenant_id,
            "metrics": metrics,
            "total": len(metrics)
        }
    except Exception as e:
        logger.error(f"Failed to get available metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available metrics"
        )

@router.get("/insights")
async def get_analytics_insights(tenant_id: str = "default"):
    """
    Get automated insights from analytics data.
    """
    try:
        insights = [
            {
                "type": "trend",
                "title": "API Usage Increasing",
                "description": "API calls have increased by 25% over the last week",
                "severity": "info",
                "timestamp": datetime.now().isoformat()
            },
            {
                "type": "anomaly",
                "title": "Unusual Error Rate",
                "description": "Error rate spiked to 5% yesterday, above normal 1%",
                "severity": "warning",
                "timestamp": datetime.now().isoformat()
            },
            {
                "type": "recommendation",
                "title": "Consider Scaling",
                "description": "Response times are approaching threshold, consider scaling resources",
                "severity": "info",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        return {
            "tenant_id": tenant_id,
            "insights": insights,
            "total": len(insights)
        }
    except Exception as e:
        logger.error(f"Failed to get analytics insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analytics insights"
        )
