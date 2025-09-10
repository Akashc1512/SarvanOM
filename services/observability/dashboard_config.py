"""
Dashboard Configuration - SarvanOM v2

Generate dashboard JSON/config per docs (no screenshots needed).
"""

from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class DashboardTile:
    title: str
    type: str
    metric: str
    labels: Dict[str, str] = None
    thresholds: Dict[str, float] = None
    size: str = "medium"
    refresh_rate: int = 30

@dataclass
class DashboardRow:
    title: str
    type: str
    tiles: List[DashboardTile]
    size: str = "large"

@dataclass
class DashboardAlert:
    name: str
    condition: str
    severity: str
    notification: List[str]
    threshold: str = "immediate"

@dataclass
class Dashboard:
    title: str
    refresh_rate: int
    layout: Dict[str, Any]
    alerts: List[DashboardAlert]

class DashboardConfigGenerator:
    """Generate dashboard configurations"""
    
    def __init__(self):
        self.tile_templates = {
            "status": {
                "type": "status",
                "size": "small",
                "refresh_rate": 30
            },
            "gauge": {
                "type": "gauge",
                "size": "medium",
                "refresh_rate": 60
            },
            "histogram": {
                "type": "histogram",
                "size": "large",
                "refresh_rate": 60
            },
            "line_chart": {
                "type": "line_chart",
                "size": "large",
                "refresh_rate": 60
            },
            "grid": {
                "type": "grid",
                "size": "large",
                "refresh_rate": 30
            }
        }
    
    def generate_system_health_dashboard(self) -> Dashboard:
        """Generate system health dashboard configuration"""
        return Dashboard(
            title="SarvanOM v2 - System Health",
            refresh_rate=30,
            layout={
                "rows": [
                    DashboardRow(
                        title="Service Status Grid",
                        type="grid",
                        size="large",
                        tiles=[
                            DashboardTile(
                                title="API Gateway",
                                type="status",
                                metric="sarvanom_service_health",
                                labels={"service": "api-gateway"},
                                thresholds={"healthy": 1, "degraded": 0.5, "down": 0},
                                size="small"
                            ),
                            DashboardTile(
                                title="Auth Service",
                                type="status",
                                metric="sarvanom_service_health",
                                labels={"service": "auth"},
                                thresholds={"healthy": 1, "degraded": 0.5, "down": 0},
                                size="small"
                            ),
                            DashboardTile(
                                title="Search Service",
                                type="status",
                                metric="sarvanom_service_health",
                                labels={"service": "search"},
                                thresholds={"healthy": 1, "degraded": 0.5, "down": 0},
                                size="small"
                            ),
                            DashboardTile(
                                title="Synthesis Service",
                                type="status",
                                metric="sarvanom_service_health",
                                labels={"service": "synthesis"},
                                thresholds={"healthy": 1, "degraded": 0.5, "down": 0},
                                size="small"
                            ),
                            DashboardTile(
                                title="Fact Check Service",
                                type="status",
                                metric="sarvanom_service_health",
                                labels={"service": "fact-check"},
                                thresholds={"healthy": 1, "degraded": 0.5, "down": 0},
                                size="small"
                            ),
                            DashboardTile(
                                title="Analytics Service",
                                type="status",
                                metric="sarvanom_service_health",
                                labels={"service": "analytics"},
                                thresholds={"healthy": 1, "degraded": 0.5, "down": 0},
                                size="small"
                            ),
                            DashboardTile(
                                title="PostgreSQL",
                                type="status",
                                metric="sarvanom_database_health",
                                labels={"database": "postgresql"},
                                thresholds={"healthy": 1, "degraded": 0.5, "down": 0},
                                size="small"
                            ),
                            DashboardTile(
                                title="Redis",
                                type="status",
                                metric="sarvanom_cache_health",
                                labels={"cache": "redis"},
                                thresholds={"healthy": 1, "degraded": 0.5, "down": 0},
                                size="small"
                            ),
                            DashboardTile(
                                title="Qdrant",
                                type="status",
                                metric="sarvanom_vector_db_health",
                                labels={"database": "qdrant"},
                                thresholds={"healthy": 1, "degraded": 0.5, "down": 0},
                                size="small"
                            ),
                            DashboardTile(
                                title="Meilisearch",
                                type="status",
                                metric="sarvanom_search_engine_health",
                                labels={"engine": "meilisearch"},
                                thresholds={"healthy": 1, "degraded": 0.5, "down": 0},
                                size="small"
                            ),
                            DashboardTile(
                                title="ArangoDB",
                                type="status",
                                metric="sarvanom_graph_db_health",
                                labels={"database": "arangodb"},
                                thresholds={"healthy": 1, "degraded": 0.5, "down": 0},
                                size="small"
                            ),
                            DashboardTile(
                                title="Ollama",
                                type="status",
                                metric="sarvanom_llm_health",
                                labels={"provider": "ollama"},
                                thresholds={"healthy": 1, "degraded": 0.5, "down": 0},
                                size="small"
                            )
                        ]
                    ),
                    DashboardRow(
                        title="System Metrics",
                        type="row",
                        tiles=[
                            DashboardTile(
                                title="Uptime",
                                type="gauge",
                                metric="sarvanom_system_uptime",
                                thresholds={"warning": 99.9, "critical": 99.0},
                                size="medium"
                            ),
                            DashboardTile(
                                title="Response Time",
                                type="histogram",
                                metric="sarvanom_sla_global_ms",
                                thresholds={"warning": 5000, "critical": 10000},
                                size="large"
                            ),
                            DashboardTile(
                                title="Error Rate",
                                type="gauge",
                                metric="sarvanom_error_rate",
                                thresholds={"warning": 1.0, "critical": 5.0},
                                size="medium"
                            ),
                            DashboardTile(
                                title="Active Users",
                                type="gauge",
                                metric="sarvanom_active_users",
                                thresholds={"warning": 1000, "critical": 2000},
                                size="medium"
                            ),
                            DashboardTile(
                                title="Queue Depth",
                                type="gauge",
                                metric="sarvanom_queue_depth",
                                thresholds={"warning": 100, "critical": 500},
                                size="medium"
                            )
                        ]
                    )
                ]
            },
            alerts=[
                DashboardAlert(
                    name="Service Down",
                    condition="sarvanom_service_health == 0",
                    severity="critical",
                    notification=["slack", "email", "pagerduty"]
                ),
                DashboardAlert(
                    name="High Error Rate",
                    condition="sarvanom_error_rate > 5%",
                    severity="critical",
                    notification=["slack", "email"]
                ),
                DashboardAlert(
                    name="Slow Response Time",
                    condition="sarvanom_sla_global_ms > 10s",
                    severity="warning",
                    notification=["slack"]
                ),
                DashboardAlert(
                    name="High Queue Depth",
                    condition="sarvanom_queue_depth > 500",
                    severity="warning",
                    notification=["slack"]
                )
            ]
        )
    
    def generate_performance_dashboard(self) -> Dashboard:
        """Generate performance dashboard configuration"""
        return Dashboard(
            title="SarvanOM v2 - Performance",
            refresh_rate=60,
            layout={
                "rows": [
                    DashboardRow(
                        title="SLA Compliance",
                        type="row",
                        tiles=[
                            DashboardTile(
                                title="SLA Compliance Rate",
                                type="gauge",
                                metric="sarvanom_sla_compliance_rate",
                                thresholds={"warning": 95.0, "critical": 90.0},
                                size="medium"
                            ),
                            DashboardTile(
                                title="TTFT",
                                type="histogram",
                                metric="sarvanom_sla_ttft_ms",
                                thresholds={"warning": 1500, "critical": 2000},
                                size="large"
                            ),
                            DashboardTile(
                                title="Budget Usage",
                                type="gauge",
                                metric="sarvanom_budget_usage_percent",
                                thresholds={"warning": 80.0, "critical": 95.0},
                                size="medium"
                            )
                        ]
                    ),
                    DashboardRow(
                        title="Lane Performance",
                        type="grid",
                        size="large",
                        tiles=[
                            DashboardTile(
                                title="Web Retrieval",
                                type="histogram",
                                metric="sarvanom_sla_web_ms",
                                labels={"lane": "web_retrieval"},
                                thresholds={"warning": 1000, "critical": 2000},
                                size="medium"
                            ),
                            DashboardTile(
                                title="Vector Search",
                                type="histogram",
                                metric="sarvanom_sla_vector_ms",
                                labels={"lane": "vector_search"},
                                thresholds={"warning": 1000, "critical": 2000},
                                size="medium"
                            ),
                            DashboardTile(
                                title="Knowledge Graph",
                                type="histogram",
                                metric="sarvanom_sla_kg_ms",
                                labels={"lane": "knowledge_graph"},
                                thresholds={"warning": 1000, "critical": 2000},
                                size="medium"
                            ),
                            DashboardTile(
                                title="Keyword Search",
                                type="histogram",
                                metric="sarvanom_sla_keyword_ms",
                                labels={"lane": "keyword_search"},
                                thresholds={"warning": 500, "critical": 1000},
                                size="medium"
                            ),
                            DashboardTile(
                                title="News Feeds",
                                type="histogram",
                                metric="sarvanom_sla_news_ms",
                                labels={"lane": "news_feeds"},
                                thresholds={"warning": 300, "critical": 800},
                                size="medium"
                            ),
                            DashboardTile(
                                title="Markets Feeds",
                                type="histogram",
                                metric="sarvanom_sla_markets_ms",
                                labels={"lane": "markets_feeds"},
                                thresholds={"warning": 300, "critical": 800},
                                size="medium"
                            ),
                            DashboardTile(
                                title="LLM Synthesis",
                                type="histogram",
                                metric="sarvanom_sla_llm_ms",
                                labels={"lane": "llm_synthesis"},
                                thresholds={"warning": 1000, "critical": 2000},
                                size="medium"
                            ),
                            DashboardTile(
                                title="Fact Check",
                                type="histogram",
                                metric="sarvanom_sla_fact_check_ms",
                                labels={"lane": "fact_check"},
                                thresholds={"warning": 500, "critical": 1000},
                                size="medium"
                            )
                        ]
                    ),
                    DashboardRow(
                        title="Performance Trends",
                        type="row",
                        tiles=[
                            DashboardTile(
                                title="Response Time Trends",
                                type="line_chart",
                                metric="sarvanom_sla_global_ms",
                                size="large"
                            ),
                            DashboardTile(
                                title="Lane Success Rates",
                                type="line_chart",
                                metric="sarvanom_lane_success_rate",
                                size="large"
                            )
                        ]
                    )
                ]
            },
            alerts=[
                DashboardAlert(
                    name="SLA Violation",
                    condition="sarvanom_sla_compliance_rate < 95%",
                    severity="warning",
                    notification=["slack"]
                ),
                DashboardAlert(
                    name="High TTFT",
                    condition="sarvanom_sla_ttft_ms > 2s",
                    severity="critical",
                    notification=["slack", "email"]
                ),
                DashboardAlert(
                    name="Lane Timeout",
                    condition="sarvanom_lane_timeout_rate > 10%",
                    severity="warning",
                    notification=["slack"]
                )
            ]
        )
    
    def generate_guided_prompt_dashboard(self) -> Dashboard:
        """Generate Guided Prompt dashboard configuration"""
        return Dashboard(
            title="SarvanOM v2 - Guided Prompt",
            refresh_rate=60,
            layout={
                "rows": [
                    DashboardRow(
                        title="Guided Prompt KPIs",
                        type="row",
                        tiles=[
                            DashboardTile(
                                title="Accept Rate",
                                type="gauge",
                                metric="sarvanom_guided_prompt_accept_rate",
                                thresholds={"warning": 30.0, "critical": 20.0},
                                size="medium"
                            ),
                            DashboardTile(
                                title="Edit Rate",
                                type="gauge",
                                metric="sarvanom_guided_prompt_edit_rate",
                                thresholds={"warning": 50.0, "critical": 70.0},
                                size="medium"
                            ),
                            DashboardTile(
                                title="Skip Rate",
                                type="gauge",
                                metric="sarvanom_guided_prompt_skip_rate",
                                thresholds={"warning": 20.0, "critical": 30.0},
                                size="medium"
                            ),
                            DashboardTile(
                                title="TTFR",
                                type="histogram",
                                metric="sarvanom_guided_prompt_ttfr_ms",
                                thresholds={"warning": 500, "critical": 800},
                                size="large"
                            )
                        ]
                    ),
                    DashboardRow(
                        title="Guided Prompt SLOs",
                        type="row",
                        tiles=[
                            DashboardTile(
                                title="P95 Latency",
                                type="histogram",
                                metric="sarvanom_guided_prompt_ttfr_ms",
                                labels={"percentile": "95"},
                                thresholds={"warning": 500, "critical": 800},
                                size="large"
                            ),
                            DashboardTile(
                                title="Complaint Rate",
                                type="gauge",
                                metric="sarvanom_guided_prompt_complaint_rate",
                                thresholds={"warning": 5.0, "critical": 10.0},
                                size="medium"
                            ),
                            DashboardTile(
                                title="Quality Score",
                                type="gauge",
                                metric="sarvanom_guided_prompt_quality_score",
                                thresholds={"warning": 0.8, "critical": 0.7},
                                size="medium"
                            )
                        ]
                    ),
                    DashboardRow(
                        title="Guided Prompt Trends",
                        type="row",
                        tiles=[
                            DashboardTile(
                                title="Accept Rate Trends",
                                type="line_chart",
                                metric="sarvanom_guided_prompt_accept_rate",
                                size="large"
                            ),
                            DashboardTile(
                                title="TTFR Trends",
                                type="line_chart",
                                metric="sarvanom_guided_prompt_ttfr_ms",
                                size="large"
                            )
                        ]
                    )
                ]
            },
            alerts=[
                DashboardAlert(
                    name="Low Accept Rate",
                    condition="sarvanom_guided_prompt_accept_rate < 30%",
                    severity="warning",
                    notification=["slack"]
                ),
                DashboardAlert(
                    name="High TTFR",
                    condition="sarvanom_guided_prompt_ttfr_ms > 800ms",
                    severity="critical",
                    notification=["slack", "email"]
                ),
                DashboardAlert(
                    name="High Complaint Rate",
                    condition="sarvanom_guided_prompt_complaint_rate > 10%",
                    severity="critical",
                    notification=["slack", "email"]
                )
            ]
        )
    
    def generate_user_experience_dashboard(self) -> Dashboard:
        """Generate user experience dashboard configuration"""
        return Dashboard(
            title="SarvanOM v2 - User Experience",
            refresh_rate=300,
            layout={
                "rows": [
                    DashboardRow(
                        title="User Satisfaction",
                        type="row",
                        tiles=[
                            DashboardTile(
                                title="Overall Satisfaction",
                                type="gauge",
                                metric="sarvanom_user_satisfaction",
                                thresholds={"warning": 4.0, "critical": 3.5},
                                size="medium"
                            ),
                            DashboardTile(
                                title="Query Success Rate",
                                type="gauge",
                                metric="sarvanom_query_success_rate",
                                thresholds={"warning": 95.0, "critical": 90.0},
                                size="medium"
                            ),
                            DashboardTile(
                                title="User Retention",
                                type="gauge",
                                metric="sarvanom_user_retention",
                                thresholds={"warning": 80.0, "critical": 70.0},
                                size="medium"
                            )
                        ]
                    ),
                    DashboardRow(
                        title="User Behavior",
                        type="row",
                        tiles=[
                            DashboardTile(
                                title="Active Users",
                                type="line_chart",
                                metric="sarvanom_active_users",
                                size="large"
                            ),
                            DashboardTile(
                                title="Query Volume",
                                type="line_chart",
                                metric="sarvanom_query_volume",
                                size="large"
                            ),
                            DashboardTile(
                                title="Session Duration",
                                type="histogram",
                                metric="sarvanom_session_duration",
                                size="large"
                            )
                        ]
                    )
                ]
            },
            alerts=[
                DashboardAlert(
                    name="Low User Satisfaction",
                    condition="sarvanom_user_satisfaction < 3.5",
                    severity="critical",
                    notification=["slack", "email"]
                ),
                DashboardAlert(
                    name="High Query Failure Rate",
                    condition="sarvanom_query_success_rate < 90%",
                    severity="critical",
                    notification=["slack", "email"]
                )
            ]
        )
    
    def generate_business_metrics_dashboard(self) -> Dashboard:
        """Generate business metrics dashboard configuration"""
        return Dashboard(
            title="SarvanOM v2 - Business Metrics",
            refresh_rate=900,
            layout={
                "rows": [
                    DashboardRow(
                        title="Business KPIs",
                        type="row",
                        tiles=[
                            DashboardTile(
                                title="Revenue",
                                type="gauge",
                                metric="sarvanom_revenue",
                                size="medium"
                            ),
                            DashboardTile(
                                title="Cost per Query",
                                type="gauge",
                                metric="sarvanom_cost_per_query",
                                thresholds={"warning": 0.10, "critical": 0.15},
                                size="medium"
                            ),
                            DashboardTile(
                                title="User Growth",
                                type="gauge",
                                metric="sarvanom_user_growth_rate",
                                size="medium"
                            )
                        ]
                    ),
                    DashboardRow(
                        title="Cost Analysis",
                        type="row",
                        tiles=[
                            DashboardTile(
                                title="LLM Costs",
                                type="line_chart",
                                metric="sarvanom_llm_costs",
                                size="large"
                            ),
                            DashboardTile(
                                title="Infrastructure Costs",
                                type="line_chart",
                                metric="sarvanom_infrastructure_costs",
                                size="large"
                            )
                        ]
                    )
                ]
            },
            alerts=[
                DashboardAlert(
                    name="High Cost per Query",
                    condition="sarvanom_cost_per_query > 0.15",
                    severity="warning",
                    notification=["slack"]
                )
            ]
        )
    
    def generate_infrastructure_dashboard(self) -> Dashboard:
        """Generate infrastructure dashboard configuration"""
        return Dashboard(
            title="SarvanOM v2 - Infrastructure",
            refresh_rate=60,
            layout={
                "rows": [
                    DashboardRow(
                        title="Resource Utilization",
                        type="row",
                        tiles=[
                            DashboardTile(
                                title="CPU Usage",
                                type="gauge",
                                metric="sarvanom_cpu_usage",
                                thresholds={"warning": 80.0, "critical": 90.0},
                                size="medium"
                            ),
                            DashboardTile(
                                title="Memory Usage",
                                type="gauge",
                                metric="sarvanom_memory_usage",
                                thresholds={"warning": 80.0, "critical": 90.0},
                                size="medium"
                            ),
                            DashboardTile(
                                title="Disk Usage",
                                type="gauge",
                                metric="sarvanom_disk_usage",
                                thresholds={"warning": 80.0, "critical": 90.0},
                                size="medium"
                            ),
                            DashboardTile(
                                title="Network Usage",
                                type="gauge",
                                metric="sarvanom_network_usage",
                                thresholds={"warning": 80.0, "critical": 90.0},
                                size="medium"
                            )
                        ]
                    ),
                    DashboardRow(
                        title="Capacity Planning",
                        type="row",
                        tiles=[
                            DashboardTile(
                                title="Request Rate",
                                type="line_chart",
                                metric="sarvanom_request_rate",
                                size="large"
                            ),
                            DashboardTile(
                                title="Response Time Distribution",
                                type="histogram",
                                metric="sarvanom_response_time_distribution",
                                size="large"
                            )
                        ]
                    )
                ]
            },
            alerts=[
                DashboardAlert(
                    name="High CPU Usage",
                    condition="sarvanom_cpu_usage > 90%",
                    severity="critical",
                    notification=["slack", "email"]
                ),
                DashboardAlert(
                    name="High Memory Usage",
                    condition="sarvanom_memory_usage > 90%",
                    severity="critical",
                    notification=["slack", "email"]
                )
            ]
        )
    
    def generate_all_dashboards(self) -> Dict[str, Dashboard]:
        """Generate all dashboard configurations"""
        return {
            "system_health": self.generate_system_health_dashboard(),
            "performance": self.generate_performance_dashboard(),
            "guided_prompt": self.generate_guided_prompt_dashboard(),
            "user_experience": self.generate_user_experience_dashboard(),
            "business_metrics": self.generate_business_metrics_dashboard(),
            "infrastructure": self.generate_infrastructure_dashboard()
        }
