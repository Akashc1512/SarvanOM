"""
Advanced Analytics Service for API Gateway

This module provides advanced analytics functionality with:
- Data analysis and insights
- Real-time analytics
- Predictive analytics
- Custom dashboards
- Data visualization
- Performance metrics
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Optional heavy visualization libs are not required for core analytics logic
try:
    import matplotlib.pyplot as plt  # type: ignore
    import seaborn as sns  # type: ignore
    import plotly.graph_objects as go  # type: ignore
    import plotly.express as px  # type: ignore
    from plotly.subplots import make_subplots  # type: ignore
except Exception:  # pragma: no cover - optional in testing
    plt = None  # type: ignore
    sns = None  # type: ignore
    go = None  # type: ignore
    px = None  # type: ignore
    make_subplots = None  # type: ignore
from shared.core.unified_logging import get_logger

logger = get_logger(__name__)


class AnalyticsType(Enum):
    """Types of analytics available."""

    USAGE_ANALYTICS = "usage_analytics"
    PERFORMANCE_ANALYTICS = "performance_analytics"
    USER_ANALYTICS = "user_analytics"
    PREDICTIVE_ANALYTICS = "predictive_analytics"
    BUSINESS_ANALYTICS = "business_analytics"


@dataclass
class AnalyticsData:
    """Analytics data structure."""

    timestamp: datetime
    metric_name: str
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsInsight:
    """Analytics insight structure."""

    insight_type: str
    title: str
    description: str
    confidence: float
    data: Dict[str, Any]
    recommendations: List[str] = field(default_factory=list)


@dataclass
class DashboardConfig:
    """Dashboard configuration."""

    dashboard_id: str
    name: str
    description: str
    widgets: List[Dict[str, Any]]
    refresh_interval: int = 300  # seconds
    is_public: bool = False


class AdvancedAnalyticsService:
    """Service for handling advanced analytics and insights."""

    def __init__(self):
        self.analytics_data = {}  # In-memory analytics store
        self.dashboards = {}  # Dashboard configurations
        self.insights_cache = {}  # Cached insights
        self._initialize_default_dashboards()

    def _initialize_default_dashboards(self):
        """Initialize default dashboard configurations."""
        default_dashboard = DashboardConfig(
            dashboard_id="default",
            name="SarvanOM Analytics Dashboard",
            description="Default analytics dashboard with key metrics",
            widgets=[
                {
                    "id": "api_usage_chart",
                    "type": "line_chart",
                    "title": "API Usage Over Time",
                    "config": {"metric": "api_calls", "timeframe": "7d"},
                },
                {
                    "id": "user_activity_chart",
                    "type": "bar_chart",
                    "title": "User Activity",
                    "config": {"metric": "active_users", "timeframe": "30d"},
                },
                {
                    "id": "performance_metrics",
                    "type": "gauge_chart",
                    "title": "System Performance",
                    "config": {
                        "metrics": ["cpu_usage", "memory_usage", "response_time"]
                    },
                },
            ],
        )

        self.dashboards[default_dashboard.dashboard_id] = default_dashboard

    async def collect_analytics_data(
        self,
        metric_name: str,
        value: float,
        tenant_id: str = "default",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Collect analytics data point."""
        try:
            data_point = AnalyticsData(
                timestamp=datetime.now(),
                metric_name=metric_name,
                value=value,
                metadata=metadata or {},
            )

            if tenant_id not in self.analytics_data:
                self.analytics_data[tenant_id] = []

            self.analytics_data[tenant_id].append(data_point)

            # Keep only last 1000 data points per tenant
            if len(self.analytics_data[tenant_id]) > 1000:
                self.analytics_data[tenant_id] = self.analytics_data[tenant_id][-1000:]

            logger.debug(
                f"Collected analytics data: {metric_name}={value} for tenant {tenant_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to collect analytics data: {e}")
            return False

    async def get_usage_analytics(
        self,
        tenant_id: str = "default",
        timeframe: str = "7d",
        metrics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get usage analytics for a tenant."""
        try:
            if tenant_id not in self.analytics_data:
                return {"error": "No data available for tenant"}

            # Filter data by timeframe
            cutoff_time = datetime.now() - self._parse_timeframe(timeframe)
            filtered_data = [
                d for d in self.analytics_data[tenant_id] if d.timestamp >= cutoff_time
            ]

            if not filtered_data:
                return {"error": "No data available for specified timeframe"}

            # Group by metric
            metric_data = {}
            for data_point in filtered_data:
                metric = data_point.metric_name
                if metrics and metric not in metrics:
                    continue

                if metric not in metric_data:
                    metric_data[metric] = []
                metric_data[metric].append(data_point)

            # Calculate statistics for each metric
            analytics_results = {}
            for metric, data_points in metric_data.items():
                values = [dp.value for dp in data_points]
                analytics_results[metric] = {
                    "count": len(values),
                    "mean": np.mean(values),
                    "median": np.median(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values),
                    "trend": self._calculate_trend(values),
                    "data_points": [
                        {
                            "timestamp": dp.timestamp.isoformat(),
                            "value": dp.value,
                            "metadata": dp.metadata,
                        }
                        for dp in data_points
                    ],
                }

            return {
                "tenant_id": tenant_id,
                "timeframe": timeframe,
                "metrics": analytics_results,
                "summary": {
                    "total_data_points": len(filtered_data),
                    "metrics_analyzed": list(analytics_results.keys()),
                    "analysis_timestamp": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Failed to get usage analytics: {e}")
            return {"error": str(e)}

    async def get_performance_analytics(
        self, tenant_id: str = "default", timeframe: str = "24h"
    ) -> Dict[str, Any]:
        """Get performance analytics."""
        try:
            # Get performance-related metrics
            performance_metrics = [
                "response_time",
                "cpu_usage",
                "memory_usage",
                "error_rate",
            ]

            analytics_data = await self.get_usage_analytics(
                tenant_id=tenant_id, timeframe=timeframe, metrics=performance_metrics
            )

            if "error" in analytics_data:
                return analytics_data

            # Calculate performance insights
            insights = []

            # Response time analysis
            if "response_time" in analytics_data["metrics"]:
                rt_data = analytics_data["metrics"]["response_time"]
                if rt_data["mean"] > 1000:  # ms
                    insights.append(
                        {
                            "type": "performance_warning",
                            "title": "High Response Time",
                            "description": f"Average response time is {rt_data['mean']:.2f}ms",
                            "severity": "warning",
                        }
                    )

            # Error rate analysis
            if "error_rate" in analytics_data["metrics"]:
                error_data = analytics_data["metrics"]["error_rate"]
                if error_data["mean"] > 0.05:  # 5%
                    insights.append(
                        {
                            "type": "performance_critical",
                            "title": "High Error Rate",
                            "description": f"Error rate is {error_data['mean']*100:.2f}%",
                            "severity": "critical",
                        }
                    )

            return {
                "tenant_id": tenant_id,
                "timeframe": timeframe,
                "performance_metrics": analytics_data["metrics"],
                "insights": insights,
                "summary": analytics_data["summary"],
            }

        except Exception as e:
            logger.error(f"Failed to get performance analytics: {e}")
            return {"error": str(e)}

    async def get_user_analytics(
        self, tenant_id: str = "default", timeframe: str = "30d"
    ) -> Dict[str, Any]:
        """Get user behavior analytics."""
        try:
            # Get user-related metrics
            user_metrics = ["active_users", "user_sessions", "user_engagement"]

            analytics_data = await self.get_usage_analytics(
                tenant_id=tenant_id, timeframe=timeframe, metrics=user_metrics
            )

            if "error" in analytics_data:
                return analytics_data

            # Calculate user insights
            insights = []

            # User growth analysis
            if "active_users" in analytics_data["metrics"]:
                users_data = analytics_data["metrics"]["active_users"]
                if users_data["trend"] > 0.1:  # 10% growth
                    insights.append(
                        {
                            "type": "user_growth",
                            "title": "Strong User Growth",
                            "description": f"User growth trend: {users_data['trend']*100:.1f}%",
                            "severity": "positive",
                        }
                    )

            # Engagement analysis
            if "user_engagement" in analytics_data["metrics"]:
                engagement_data = analytics_data["metrics"]["user_engagement"]
                if engagement_data["mean"] < 0.3:  # 30% engagement
                    insights.append(
                        {
                            "type": "engagement_warning",
                            "title": "Low User Engagement",
                            "description": f"Average engagement: {engagement_data['mean']*100:.1f}%",
                            "severity": "warning",
                        }
                    )

            return {
                "tenant_id": tenant_id,
                "timeframe": timeframe,
                "user_metrics": analytics_data["metrics"],
                "insights": insights,
                "summary": analytics_data["summary"],
            }

        except Exception as e:
            logger.error(f"Failed to get user analytics: {e}")
            return {"error": str(e)}

    async def get_predictive_analytics(
        self,
        tenant_id: str = "default",
        metric: str = "api_calls",
        forecast_periods: int = 7,
    ) -> Dict[str, Any]:
        """Get predictive analytics using time series forecasting."""
        try:
            if tenant_id not in self.analytics_data:
                return {"error": "No data available for tenant"}

            # Get historical data for the metric
            metric_data = [
                dp for dp in self.analytics_data[tenant_id] if dp.metric_name == metric
            ]

            if len(metric_data) < 10:
                return {"error": "Insufficient data for prediction"}

            # Prepare time series data
            df = pd.DataFrame(
                [{"timestamp": dp.timestamp, "value": dp.value} for dp in metric_data]
            )

            df = df.sort_values("timestamp")
            df["date"] = pd.to_datetime(df["timestamp"]).dt.date
            daily_data = df.groupby("date")["value"].sum().reset_index()

            # Simple moving average prediction
            window_size = min(7, len(daily_data))
            if window_size < 3:
                return {"error": "Insufficient data for prediction"}

            moving_avg = daily_data["value"].rolling(window=window_size).mean()
            trend = daily_data["value"].diff().mean()

            # Generate forecast
            last_value = daily_data["value"].iloc[-1]
            forecast_values = []

            for i in range(forecast_periods):
                predicted_value = last_value + (trend * (i + 1))
                forecast_values.append(max(0, predicted_value))  # Ensure non-negative

            # Calculate confidence intervals (simplified)
            std_dev = daily_data["value"].std()
            confidence_intervals = {
                "lower": [max(0, v - std_dev) for v in forecast_values],
                "upper": [v + std_dev for v in forecast_values],
            }

            return {
                "tenant_id": tenant_id,
                "metric": metric,
                "forecast_periods": forecast_periods,
                "historical_data": {
                    "dates": daily_data["date"].astype(str).tolist(),
                    "values": daily_data["value"].tolist(),
                },
                "forecast": {
                    "values": forecast_values,
                    "confidence_intervals": confidence_intervals,
                    "trend": trend,
                    "accuracy_metrics": {
                        "mae": self._calculate_mae(daily_data["value"], moving_avg),
                        "rmse": self._calculate_rmse(daily_data["value"], moving_avg),
                    },
                },
                "insights": [
                    {
                        "type": "trend_analysis",
                        "title": f"{metric.replace('_', ' ').title()} Trend",
                        "description": f"Trend: {trend:.2f} per day",
                        "confidence": 0.8,
                    }
                ],
            }

        except Exception as e:
            logger.error(f"Failed to get predictive analytics: {e}")
            return {"error": str(e)}

    async def create_dashboard(self, dashboard_config: DashboardConfig) -> bool:
        """Create a new analytics dashboard."""
        try:
            self.dashboards[dashboard_config.dashboard_id] = dashboard_config
            logger.info(f"Created dashboard: {dashboard_config.dashboard_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create dashboard: {e}")
            return False

    async def get_dashboard_data(
        self, dashboard_id: str, tenant_id: str = "default"
    ) -> Dict[str, Any]:
        """Get data for a specific dashboard."""
        try:
            if dashboard_id not in self.dashboards:
                return {"error": "Dashboard not found"}

            dashboard = self.dashboards[dashboard_id]
            dashboard_data = {
                "dashboard_id": dashboard_id,
                "name": dashboard.name,
                "description": dashboard.description,
                "widgets": [],
            }

            # Generate data for each widget
            for widget in dashboard.widgets:
                widget_data = await self._generate_widget_data(widget, tenant_id)
                dashboard_data["widgets"].append(widget_data)

            return dashboard_data

        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {"error": str(e)}

    async def _generate_widget_data(
        self, widget: Dict[str, Any], tenant_id: str
    ) -> Dict[str, Any]:
        """Generate data for a specific widget."""
        widget_type = widget.get("type", "chart")
        config = widget.get("config", {})

        if widget_type == "line_chart":
            return await self._generate_line_chart_data(widget, config, tenant_id)
        elif widget_type == "bar_chart":
            return await self._generate_bar_chart_data(widget, config, tenant_id)
        elif widget_type == "gauge_chart":
            return await self._generate_gauge_chart_data(widget, config, tenant_id)
        else:
            return {"error": f"Unsupported widget type: {widget_type}"}

    async def _generate_line_chart_data(
        self, widget: Dict[str, Any], config: Dict[str, Any], tenant_id: str
    ) -> Dict[str, Any]:
        """Generate line chart data."""
        metric = config.get("metric", "api_calls")
        timeframe = config.get("timeframe", "7d")

        analytics_data = await self.get_usage_analytics(
            tenant_id=tenant_id, timeframe=timeframe, metrics=[metric]
        )

        if "error" in analytics_data:
            return {"error": analytics_data["error"]}

        if metric not in analytics_data["metrics"]:
            return {"error": f"No data available for metric: {metric}"}

        metric_data = analytics_data["metrics"][metric]
        data_points = metric_data["data_points"]

        return {
            "widget_id": widget.get("id"),
            "type": "line_chart",
            "title": widget.get("title", "Line Chart"),
            "data": {
                "x": [dp["timestamp"] for dp in data_points],
                "y": [dp["value"] for dp in data_points],
                "metric": metric,
            },
            "config": {
                "xaxis_title": "Time",
                "yaxis_title": metric.replace("_", " ").title(),
                "show_legend": True,
            },
        }

    async def _generate_bar_chart_data(
        self, widget: Dict[str, Any], config: Dict[str, Any], tenant_id: str
    ) -> Dict[str, Any]:
        """Generate bar chart data."""
        metric = config.get("metric", "active_users")
        timeframe = config.get("timeframe", "30d")

        analytics_data = await self.get_usage_analytics(
            tenant_id=tenant_id, timeframe=timeframe, metrics=[metric]
        )

        if "error" in analytics_data:
            return {"error": analytics_data["error"]}

        if metric not in analytics_data["metrics"]:
            return {"error": f"No data available for metric: {metric}"}

        metric_data = analytics_data["metrics"][metric]

        return {
            "widget_id": widget.get("id"),
            "type": "bar_chart",
            "title": widget.get("title", "Bar Chart"),
            "data": {
                "x": ["Current", "Average", "Max"],
                "y": [
                    (
                        metric_data["data_points"][-1]["value"]
                        if metric_data["data_points"]
                        else 0
                    ),
                    metric_data["mean"],
                    metric_data["max"],
                ],
                "metric": metric,
            },
            "config": {
                "xaxis_title": "Metric",
                "yaxis_title": metric.replace("_", " ").title(),
                "show_legend": True,
            },
        }

    async def _generate_gauge_chart_data(
        self, widget: Dict[str, Any], config: Dict[str, Any], tenant_id: str
    ) -> Dict[str, Any]:
        """Generate gauge chart data."""
        metrics = config.get("metrics", ["cpu_usage", "memory_usage"])

        gauge_data = []
        for metric in metrics:
            analytics_data = await self.get_usage_analytics(
                tenant_id=tenant_id, timeframe="24h", metrics=[metric]
            )

            if "error" not in analytics_data and metric in analytics_data["metrics"]:
                current_value = (
                    analytics_data["metrics"][metric]["data_points"][-1]["value"]
                    if analytics_data["metrics"][metric]["data_points"]
                    else 0
                )
                gauge_data.append(
                    {
                        "metric": metric,
                        "value": current_value,
                        "max_value": analytics_data["metrics"][metric]["max"],
                    }
                )

        return {
            "widget_id": widget.get("id"),
            "type": "gauge_chart",
            "title": widget.get("title", "Performance Metrics"),
            "data": gauge_data,
            "config": {"show_legend": True, "gauge_type": "percentage"},
        }

    def _parse_timeframe(self, timeframe: str) -> timedelta:
        """Parse timeframe string into timedelta."""
        timeframe_map = {
            "1h": timedelta(hours=1),
            "24h": timedelta(days=1),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90),
        }
        return timeframe_map.get(timeframe, timedelta(days=7))

    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend of values."""
        if len(values) < 2:
            return 0.0

        # Simple linear trend calculation
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        return slope

    def _calculate_mae(self, actual: pd.Series, predicted: pd.Series) -> float:
        """Calculate Mean Absolute Error."""
        return np.mean(np.abs(actual - predicted))

    def _calculate_rmse(self, actual: pd.Series, predicted: pd.Series) -> float:
        """Calculate Root Mean Square Error."""
        return np.sqrt(np.mean((actual - predicted) ** 2))


# Create global advanced analytics service instance
advanced_analytics_service = AdvancedAnalyticsService()
