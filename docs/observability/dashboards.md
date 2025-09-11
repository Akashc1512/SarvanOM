# Dashboards - SarvanOM v2

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE CONTRACT**  
**Purpose**: Document dashboards for what tiles, thresholds, and alerts

---

## 🎯 **Dashboard Overview**

SarvanOM v2 implements comprehensive dashboards to monitor system health, performance, and user experience. Dashboards provide real-time visibility into system metrics, alerts, and trends.

### **Core Principles**
1. **Real-Time Monitoring**: Provide immediate visibility into system state
2. **Proactive Alerting**: Alert on issues before they impact users
3. **Performance Tracking**: Monitor SLA compliance and performance trends
4. **Business Metrics**: Track user satisfaction and business outcomes
5. **Operational Efficiency**: Enable quick incident response and resolution

---

## 📊 **Dashboard Categories**

### **1. System Health Dashboard**
**Purpose**: Monitor overall system health and availability  
**Refresh Rate**: 30 seconds  
**Alert Thresholds**: Critical alerts for system failures

### **2. Performance Dashboard**
**Purpose**: Track SLA compliance and performance metrics  
**Refresh Rate**: 1 minute  
**Alert Thresholds**: SLA violations and performance degradation

### **3. User Experience Dashboard**
**Purpose**: Monitor user satisfaction and experience metrics  
**Refresh Rate**: 5 minutes  
**Alert Thresholds**: User satisfaction drops and query failures

### **4. Business Metrics Dashboard**
**Purpose**: Track business outcomes and user engagement  
**Refresh Rate**: 15 minutes  
**Alert Thresholds**: Business metric anomalies

### **5. Infrastructure Dashboard**
**Purpose**: Monitor infrastructure resources and capacity  
**Refresh Rate**: 1 minute  
**Alert Thresholds**: Resource utilization and capacity limits

---

## 🏥 **System Health Dashboard**

### **Dashboard Layout**
```
┌─────────────────────────────────────────────────────────────────┐
│                    SarvanOM v2 - System Health                  │
├─────────────────────────────────────────────────────────────────┤
│  Status: 🟢 HEALTHY  |  Uptime: 99.9%  |  Last Updated: 12:00  │
├─────────────────────────────────────────────────────────────────┤
│  Service Status Grid (6x2)                                     │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐     │
│  │ API Gateway │ Auth Service│Search Service│Synthesis Svc│     │
│  │    🟢 OK    │    🟢 OK    │    🟢 OK    │    🟢 OK    │     │
│  ├─────────────┼─────────────┼─────────────┼─────────────┤     │
│  │Fact Check   │Analytics    │PostgreSQL   │Redis        │     │
│  │    🟢 OK    │    🟢 OK    │    🟢 OK    │    🟢 OK    │     │
│  ├─────────────┼─────────────┼─────────────┼─────────────┤     │
│  │Qdrant       │Meilisearch  │ArangoDB     │Ollama       │     │
│  │    🟢 OK    │    🟢 OK    │    🟢 OK    │    🟢 OK    │     │
│  └─────────────┴─────────────┴─────────────┴─────────────┘     │
├─────────────────────────────────────────────────────────────────┤
│  Recent Alerts (Last 24h)                                      │
│  • 12:30 - High CPU usage on API Gateway (85%)                 │
│  • 11:45 - Slow response time on Vector Search (2.1s)          │
│  • 10:20 - Cache miss rate increased (25%)                     │
└─────────────────────────────────────────────────────────────────┘
```

### **Tiles & Metrics**
| Tile | Metric | Threshold | Alert Level | Description |
|------|--------|-----------|-------------|-------------|
| **Service Status** | Service health | 100% healthy | Critical | All services operational |
| **Uptime** | System uptime | > 99.9% | Warning | System availability |
| **Response Time** | Global response time | < 5s/7s/10s | Warning | End-to-end response time |
| **Error Rate** | Global error rate | < 1% | Critical | System-wide error rate |
| **Active Users** | Concurrent users | < 1000 | Info | Current active users |
| **Queue Depth** | Request queue depth | < 100 | Warning | Pending requests |

### **Alerts Configuration**
```yaml
# System Health Alerts
system_health_alerts:
  - name: "Service Down"
    condition: "service_status != 'healthy'"
    severity: "critical"
    notification: ["slack", "email", "pagerduty"]
    threshold: "immediate"
  
  - name: "High Error Rate"
    condition: "error_rate > 5%"
    severity: "critical"
    notification: ["slack", "email"]
    threshold: "5 minutes"
  
  - name: "Slow Response Time"
    condition: "response_time > 10s"
    severity: "warning"
    notification: ["slack"]
    threshold: "2 minutes"
  
  - name: "High Queue Depth"
    condition: "queue_depth > 500"
    severity: "warning"
    notification: ["slack"]
    threshold: "1 minute"
```

---

## ⚡ **Performance Dashboard**

### **Dashboard Layout**
```
┌─────────────────────────────────────────────────────────────────┐
│                  SarvanOM v2 - Performance                      │
├─────────────────────────────────────────────────────────────────┤
│  SLA Compliance: 🟢 98.5%  |  TTFT: 1.2s  |  Budget: 4.8s/6.9s │
├─────────────────────────────────────────────────────────────────┤
│  Response Time Trends (Last 24h)                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Simple: ████████████████████████████████████████████   │   │
│  │  Technical: ████████████████████████████████████████    │   │
│  │  Research: ██████████████████████████████████████████   │   │
│  └─────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  Lane Performance Grid (4x2)                                   │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐     │
│  │ Web Retrieval│Vector Search│Knowledge Graph│Keyword Search│   │
│  │   1.2s ✅   │   0.8s ✅   │   1.1s ✅   │   0.9s ✅   │     │
│  ├─────────────┼─────────────┼─────────────┼─────────────┤     │
│  │ News Feeds  │Markets Feeds│LLM Synthesis│Fact Check   │     │
│  │   0.7s ✅   │   0.6s ✅   │   1.5s ✅   │   0.8s ✅   │     │
│  └─────────────┴─────────────┴─────────────┴─────────────┘     │
├─────────────────────────────────────────────────────────────────┤
│  SLA Violations (Last 24h)                                     │
│  • 14:30 - Research query exceeded 10s budget (12.3s)          │
│  │  • Web retrieval: 3.2s (budget: 2s)                        │
│  │  • LLM synthesis: 2.8s (budget: 2s)                        │
│  • 13:15 - Technical query exceeded 7s budget (8.1s)           │
│  │  • Vector search: 2.1s (budget: 1.5s)                      │
└─────────────────────────────────────────────────────────────────┘
```

### **Tiles & Metrics**
| Tile | Metric | Threshold | Alert Level | Description |
|------|--------|-----------|-------------|-------------|
| **SLA Compliance** | SLA compliance rate | > 95% | Warning | Overall SLA compliance |
| **TTFT** | Time to first token | < 1.5s | Warning | First token delivery time |
| **Budget Utilization** | Budget usage | < 90% | Warning | Time budget utilization |
| **Lane Performance** | Lane response times | < 80% of budget | Warning | Individual lane performance |
| **Cache Hit Rate** | Cache efficiency | > 80% | Info | Cache hit rate |
| **External API Latency** | External API times | < 2s | Warning | External service latency |

### **Performance Alerts**
```yaml
# Performance Alerts
performance_alerts:
  - name: "SLA Violation"
    condition: "sla_compliance < 95%"
    severity: "critical"
    notification: ["slack", "email"]
    threshold: "5 minutes"
  
  - name: "Slow TTFT"
    condition: "ttft > 2s"
    severity: "warning"
    notification: ["slack"]
    threshold: "2 minutes"
  
  - name: "High Budget Utilization"
    condition: "budget_utilization > 90%"
    severity: "warning"
    notification: ["slack"]
    threshold: "3 minutes"
  
  - name: "Lane Timeout"
    condition: "lane_timeout_rate > 10%"
    severity: "critical"
    notification: ["slack", "email", "pagerduty"]
    threshold: "1 minute"
```

---

## 👥 **User Experience Dashboard**

### **Dashboard Layout**
```
┌─────────────────────────────────────────────────────────────────┐
│                SarvanOM v2 - User Experience                    │
├─────────────────────────────────────────────────────────────────┤
│  Satisfaction: 4.6/5  |  Success Rate: 96.2%  |  Users: 1,247  │
├─────────────────────────────────────────────────────────────────┤
│  User Satisfaction Trends (Last 7 days)                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Rating: ████████████████████████████████████████████   │   │
│  │  Trend: ↗️ +0.2 (4.4 → 4.6)                            │   │
│  └─────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  Query Success Metrics (4x2)                                   │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐     │
│  │ Simple      │ Technical   │ Research    │ Multimedia  │     │
│  │ 98.5% ✅    │ 95.8% ✅    │ 94.2% ✅    │ 96.1% ✅    │     │
│  ├─────────────┼─────────────┼─────────────┼─────────────┤     │
│  │ Citation    │ Response    │ User        │ Query       │     │
│  │ Accuracy    │ Quality     │ Retention   │ Completion  │     │
│  │ 92.3% ✅    │ 0.87 ✅     │ 84.7% ✅    │ 97.1% ✅    │     │
│  └─────────────┴─────────────┴─────────────┴─────────────┘     │
├─────────────────────────────────────────────────────────────────┤
│  Recent User Feedback (Last 24h)                               │
│  • "Great response time and accurate information" - 5⭐        │
│  • "Sometimes citations are outdated" - 4⭐                    │
│  • "Love the multimedia support!" - 5⭐                        │
│  • "Technical queries could be more detailed" - 3⭐            │
└─────────────────────────────────────────────────────────────────┘
```

### **Tiles & Metrics**
| Tile | Metric | Threshold | Alert Level | Description |
|------|--------|-----------|-------------|-------------|
| **User Satisfaction** | Average rating | > 4.0/5 | Warning | User satisfaction score |
| **Query Success Rate** | Success rate | > 95% | Critical | Successful query rate |
| **Citation Accuracy** | Citation accuracy | > 90% | Warning | Accurate citation rate |
| **Response Quality** | Quality score | > 0.8 | Warning | Response quality assessment |
| **User Retention** | Retention rate | > 80% | Info | User retention rate |
| **Query Completion** | Completion rate | > 95% | Warning | Query completion rate |

### **User Experience Alerts**
```yaml
# User Experience Alerts
user_experience_alerts:
  - name: "Low User Satisfaction"
    condition: "user_satisfaction < 4.0"
    severity: "critical"
    notification: ["slack", "email"]
    threshold: "1 hour"
  
  - name: "High Query Failure Rate"
    condition: "query_success_rate < 90%"
    severity: "critical"
    notification: ["slack", "email", "pagerduty"]
    threshold: "15 minutes"
  
  - name: "Poor Citation Accuracy"
    condition: "citation_accuracy < 80%"
    severity: "warning"
    notification: ["slack"]
    threshold: "30 minutes"
  
  - name: "Low Response Quality"
    condition: "response_quality < 0.7"
    severity: "warning"
    notification: ["slack"]
    threshold: "1 hour"
```

---

## 💼 **Business Metrics Dashboard**

### **Dashboard Layout**
```
┌─────────────────────────────────────────────────────────────────┐
│                SarvanOM v2 - Business Metrics                   │
├─────────────────────────────────────────────────────────────────┤
│  DAU: 2,847  |  MAU: 45,623  |  Growth: +12.3%  |  Revenue: $0  │
├─────────────────────────────────────────────────────────────────┤
│  User Growth Trends (Last 30 days)                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  DAU: ████████████████████████████████████████████████  │   │
│  │  MAU: ████████████████████████████████████████████████  │   │
│  │  Growth: ↗️ +12.3% (40,623 → 45,623)                   │   │
│  └─────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  Engagement Metrics (4x2)                                      │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐     │
│  │ Queries/Day │Session Time │Pages/Visit  │Bounce Rate  │     │
│  │   3.2 ✅    │   8.5m ✅   │   4.1 ✅    │   23% ✅    │     │
│  ├─────────────┼─────────────┼─────────────┼─────────────┤     │
│  │Return Users │New Users    │Feature Usage│Support Tickets│   │
│  │   78% ✅    │   22% ✅    │   65% ✅    │   12 ✅     │     │
│  └─────────────┴─────────────┴─────────────┴─────────────┘     │
├─────────────────────────────────────────────────────────────────┤
│  Feature Usage Breakdown (Last 7 days)                         │
│  • Simple Queries: 45.2% (12,847 queries)                      │
│  • Technical Queries: 28.7% (8,156 queries)                    │
│  • Research Queries: 18.3% (5,201 queries)                     │
│  • Multimedia Queries: 7.8% (2,216 queries)                    │
└─────────────────────────────────────────────────────────────────┘
```

### **Tiles & Metrics**
| Tile | Metric | Threshold | Alert Level | Description |
|------|--------|-----------|-------------|-------------|
| **Daily Active Users** | DAU count | > 1000 | Info | Daily active users |
| **Monthly Active Users** | MAU count | > 10000 | Info | Monthly active users |
| **User Growth Rate** | Growth percentage | > 5% | Info | User growth rate |
| **Queries per Day** | Query volume | > 1000 | Info | Daily query volume |
| **Session Duration** | Average session time | > 5 minutes | Info | User engagement |
| **Feature Usage** | Feature adoption | > 50% | Info | Feature utilization |

### **Business Metrics Alerts**
```yaml
# Business Metrics Alerts
business_metrics_alerts:
  - name: "User Growth Drop"
    condition: "user_growth_rate < -10%"
    severity: "warning"
    notification: ["slack", "email"]
    threshold: "1 day"
  
  - name: "Low Query Volume"
    condition: "queries_per_day < 500"
    severity: "warning"
    notification: ["slack"]
    threshold: "1 day"
  
  - name: "High Bounce Rate"
    condition: "bounce_rate > 50%"
    severity: "warning"
    notification: ["slack"]
    threshold: "2 hours"
  
  - name: "Low Feature Usage"
    condition: "feature_usage < 30%"
    severity: "info"
    notification: ["slack"]
    threshold: "1 week"
```

---

## 🏗️ **Infrastructure Dashboard**

### **Dashboard Layout**
```
┌─────────────────────────────────────────────────────────────────┐
│              SarvanOM v2 - Infrastructure                       │
├─────────────────────────────────────────────────────────────────┤
│  CPU: 65%  |  Memory: 72%  |  Disk: 45%  |  Network: 23%       │
├─────────────────────────────────────────────────────────────────┤
│  Resource Utilization Trends (Last 24h)                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  CPU: ████████████████████████████████████████████████  │   │
│  │  Memory: ████████████████████████████████████████████   │   │
│  │  Disk: ████████████████████████████████████████████████ │   │
│  │  Network: ████████████████████████████████████████████  │   │
│  └─────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  Service Resource Usage (4x2)                                  │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐     │
│  │ API Gateway │ Auth Service│Search Service│Synthesis Svc│     │
│  │ CPU: 45%    │ CPU: 23%    │ CPU: 67%    │ CPU: 89%    │     │
│  │ Mem: 512MB  │ Mem: 256MB  │ Mem: 1.2GB  │ Mem: 2.1GB  │     │
│  ├─────────────┼─────────────┼─────────────┼─────────────┤     │
│  │PostgreSQL   │Redis        │Qdrant       │Meilisearch  │     │
│  │ CPU: 34%    │ CPU: 12%    │ CPU: 56%    │ CPU: 41%    │     │
│  │ Mem: 2.8GB  │ Mem: 128MB  │ Mem: 1.8GB  │ Mem: 512MB  │     │
│  └─────────────┴─────────────┴─────────────┴─────────────┘     │
├─────────────────────────────────────────────────────────────────┤
│  Capacity Alerts (Last 24h)                                    │
│  • 15:30 - High CPU usage on Synthesis Service (89%)           │
│  • 14:15 - Memory usage approaching limit on PostgreSQL (85%)  │
│  • 13:45 - Disk space warning on Qdrant (78%)                  │
└─────────────────────────────────────────────────────────────────┘
```

### **Tiles & Metrics**
| Tile | Metric | Threshold | Alert Level | Description |
|------|--------|-----------|-------------|-------------|
| **CPU Usage** | CPU utilization | < 80% | Warning | CPU usage percentage |
| **Memory Usage** | Memory utilization | < 80% | Warning | Memory usage percentage |
| **Disk Usage** | Disk utilization | < 80% | Warning | Disk usage percentage |
| **Network Usage** | Network utilization | < 80% | Info | Network usage percentage |
| **Connection Pool** | Connection usage | < 80% | Warning | Connection pool utilization |
| **Queue Depth** | Queue depth | < 100 | Warning | Pending requests |

### **Infrastructure Alerts**
```yaml
# Infrastructure Alerts
infrastructure_alerts:
  - name: "High CPU Usage"
    condition: "cpu_usage > 90%"
    severity: "critical"
    notification: ["slack", "email", "pagerduty"]
    threshold: "5 minutes"
  
  - name: "High Memory Usage"
    condition: "memory_usage > 90%"
    severity: "critical"
    notification: ["slack", "email", "pagerduty"]
    threshold: "5 minutes"
  
  - name: "High Disk Usage"
    condition: "disk_usage > 85%"
    severity: "warning"
    notification: ["slack", "email"]
    threshold: "10 minutes"
  
  - name: "Connection Pool Exhaustion"
    condition: "connection_pool_usage > 95%"
    severity: "critical"
    notification: ["slack", "email", "pagerduty"]
    threshold: "2 minutes"
```

---

## 🔔 **Alert Configuration**

### **Alert Severity Levels**
| Level | Color | Notification | Response Time | Description |
|-------|-------|--------------|---------------|-------------|
| **Critical** | 🔴 Red | Slack + Email + PagerDuty | < 5 minutes | System down, SLA violations |
| **Warning** | 🟡 Yellow | Slack + Email | < 15 minutes | Performance degradation |
| **Info** | 🔵 Blue | Slack | < 1 hour | Informational alerts |

### **Notification Channels**
| Channel | Use Case | Response Time | Escalation |
|---------|----------|---------------|------------|
| **Slack** | All alerts | Immediate | Auto-escalate after 30 minutes |
| **Email** | Warning+ alerts | < 5 minutes | Auto-escalate after 1 hour |
| **PagerDuty** | Critical alerts | < 2 minutes | Auto-escalate after 15 minutes |

### **Alert Escalation Policy**
```yaml
# Alert Escalation Policy
escalation_policy:
  critical:
    - level_1: "on_call_engineer"
      timeout: "5 minutes"
    - level_2: "senior_engineer"
      timeout: "15 minutes"
    - level_3: "engineering_manager"
      timeout: "30 minutes"
  
  warning:
    - level_1: "on_call_engineer"
      timeout: "15 minutes"
    - level_2: "senior_engineer"
      timeout: "1 hour"
  
  info:
    - level_1: "on_call_engineer"
      timeout: "1 hour"
```

---

## 📊 **Dashboard Implementation**

### **Dashboard Framework**
```python
# Example dashboard implementation
class DashboardFramework:
    def __init__(self):
        self.dashboards = {}
        self.alerts = {}
        self.metrics = {}
    
    def create_dashboard(self, name: str, tiles: list, refresh_rate: int = 60):
        """Create dashboard"""
        dashboard = {
            "name": name,
            "tiles": tiles,
            "refresh_rate": refresh_rate,
            "created_at": datetime.now(),
            "last_updated": datetime.now()
        }
        
        self.dashboards[name] = dashboard
        return dashboard
    
    def add_tile(self, dashboard_name: str, tile: dict):
        """Add tile to dashboard"""
        if dashboard_name in self.dashboards:
            self.dashboards[dashboard_name]["tiles"].append(tile)
            self.dashboards[dashboard_name]["last_updated"] = datetime.now()
    
    def create_alert(self, name: str, condition: str, severity: str, notification: list):
        """Create alert"""
        alert = {
            "name": name,
            "condition": condition,
            "severity": severity,
            "notification": notification,
            "created_at": datetime.now(),
            "last_triggered": None,
            "status": "active"
        }
        
        self.alerts[name] = alert
        return alert
    
    def check_alerts(self):
        """Check all alerts"""
        for alert_name, alert in self.alerts.items():
            if self._evaluate_condition(alert["condition"]):
                self._trigger_alert(alert_name, alert)
    
    def _evaluate_condition(self, condition: str) -> bool:
        """Evaluate alert condition"""
        # Implementation for condition evaluation
        pass
    
    def _trigger_alert(self, alert_name: str, alert: dict):
        """Trigger alert"""
        alert["last_triggered"] = datetime.now()
        
        # Send notifications
        for channel in alert["notification"]:
            self._send_notification(channel, alert)
    
    def _send_notification(self, channel: str, alert: dict):
        """Send notification"""
        # Implementation for notification sending
        pass
```

### **Dashboard Tiles**
```python
# Example dashboard tiles implementation
class DashboardTiles:
    def __init__(self):
        self.tile_types = {
            "metric": self._create_metric_tile,
            "chart": self._create_chart_tile,
            "status": self._create_status_tile,
            "alert": self._create_alert_tile
        }
    
    def create_tile(self, tile_type: str, config: dict):
        """Create dashboard tile"""
        if tile_type in self.tile_types:
            return self.tile_types[tile_type](config)
        else:
            raise ValueError(f"Unknown tile type: {tile_type}")
    
    def _create_metric_tile(self, config: dict):
        """Create metric tile"""
        return {
            "type": "metric",
            "title": config["title"],
            "metric": config["metric"],
            "value": config["value"],
            "threshold": config.get("threshold"),
            "alert_level": config.get("alert_level"),
            "format": config.get("format", "number")
        }
    
    def _create_chart_tile(self, config: dict):
        """Create chart tile"""
        return {
            "type": "chart",
            "title": config["title"],
            "chart_type": config["chart_type"],
            "data_source": config["data_source"],
            "time_range": config.get("time_range", "24h"),
            "refresh_rate": config.get("refresh_rate", 60)
        }
    
    def _create_status_tile(self, config: dict):
        """Create status tile"""
        return {
            "type": "status",
            "title": config["title"],
            "status": config["status"],
            "status_text": config["status_text"],
            "last_updated": config.get("last_updated"),
            "details": config.get("details", [])
        }
    
    def _create_alert_tile(self, config: dict):
        """Create alert tile"""
        return {
            "type": "alert",
            "title": config["title"],
            "alerts": config["alerts"],
            "severity": config.get("severity", "info"),
            "count": len(config["alerts"]),
            "last_updated": config.get("last_updated")
        }
```

---

## 📚 **References**

- Observability & Budgets: `09_observability_and_budgets.md`
- Metrics Catalog: `docs/observability/metrics.md`
- Tracing Spans: `docs/observability/tracing.md`
- System Context: `docs/architecture/system_context.md`
- Service Catalog: `docs/architecture/service_catalog.md`
- Budgets: `docs/architecture/budgets.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This dashboard specification provides comprehensive monitoring and alerting for SarvanOM v2 system health, performance, and user experience.*
