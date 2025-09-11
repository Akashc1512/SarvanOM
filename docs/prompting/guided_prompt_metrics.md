# Guided Prompt Metrics

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE METRICS**  
**Purpose**: KPIs, event schema, dashboard tiles, and thresholds for Guided Prompt Confirmation

---

## 📊 **Key Performance Indicators (KPIs)**

### **Primary KPIs**
| KPI | Description | Target | Alert Threshold | Measurement |
|-----|-------------|--------|-----------------|-------------|
| **refinement_shown_rate** | % of queries showing refinement | 60-80% | < 50% | Queries with refinement / Total queries |
| **accept_rate** | % of suggestions accepted | ≥ 45% | < 30% | Accepted suggestions / Shown suggestions |
| **edit_rate** | % of suggestions edited | 20-30% | < 15% | Edited suggestions / Shown suggestions |
| **skip_rate** | % of suggestions skipped | ≤ 35% | > 50% | Skipped suggestions / Shown suggestions |
| **ttfr_refine_ms** | Time to first refinement (p95) | ≤ 800ms | > 1000ms | 95th percentile latency |
| **downstream_quality_lift** | Quality improvement from refinement | ≥ 15% | < 10% | Quality score improvement |
| **complaint_rate** | % of users complaining | ≤ 5% | > 10% | Complaints / Total users |

### **Secondary KPIs**
| KPI | Description | Target | Alert Threshold | Measurement |
|-----|-------------|--------|-----------------|-------------|
| **user_satisfaction** | User satisfaction score | ≥ 4.0/5.0 | < 3.5/5.0 | User feedback average |
| **learning_rate** | % of users improving over time | ≥ 20% | < 15% | Users with improving quality |
| **retention_rate** | % of users keeping feature enabled | ≥ 70% | < 60% | Users with feature enabled |
| **cost_per_refinement** | Cost per refinement suggestion | ≤ $0.005 | > $0.010 | Total cost / Refinements |

---

## 📋 **Event Schema & Properties**

### **Core Event Schema**
```json
{
  "event_type": "guided_prompt_event",
  "timestamp": "2025-09-09T10:00:00Z",
  "user_id": "user_12345",
  "session_id": "session_abc123",
  "trace_id": "trace_xyz789",
  "event_data": {
    "event_name": "refinement_shown",
    "query_hash": "hash_abc123",
    "original_query": "show me apple",
    "refinement_type": "disambiguate",
    "suggestions_count": 3,
    "latency_ms": 450,
    "model_used": "gpt-3.5-turbo",
    "cost_usd": 0.001,
    "user_agent": "Mozilla/5.0...",
    "device_type": "desktop",
    "language": "en"
  }
}
```

### **Event Types**
| Event Type | Description | Properties | Frequency |
|------------|-------------|------------|-----------|
| **refinement_shown** | Refinement suggestions displayed | query_hash, suggestions_count, latency_ms | Per refinement |
| **suggestion_accepted** | User accepted a suggestion | suggestion_id, acceptance_time_ms | Per acceptance |
| **suggestion_edited** | User edited a suggestion | suggestion_id, edit_type, edit_time_ms | Per edit |
| **suggestion_skipped** | User skipped refinement | skip_reason, skip_time_ms | Per skip |
| **refinement_timeout** | Refinement timed out | timeout_reason, elapsed_ms | Per timeout |
| **user_feedback** | User provided feedback | feedback_type, rating, comment | Per feedback |
| **feature_toggle** | User toggled feature | toggle_action, new_state | Per toggle |

### **Event Properties Schema**
```python
# Example event properties schema
class GuidedPromptEvent:
    def __init__(self, event_type: str, user_id: str, session_id: str, trace_id: str):
        self.event_type = event_type
        self.timestamp = time.time()
        self.user_id = user_id
        self.session_id = session_id
        self.trace_id = trace_id
        self.event_data = {}
    
    def add_property(self, key: str, value: Any):
        """Add property to event data"""
        self.event_data[key] = value
    
    def to_dict(self) -> Dict:
        """Convert event to dictionary"""
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "trace_id": self.trace_id,
            "event_data": self.event_data
        }
    
    def validate(self) -> bool:
        """Validate event schema"""
        required_fields = ["event_type", "timestamp", "user_id", "session_id", "trace_id"]
        return all(hasattr(self, field) for field in required_fields)
```

---

## 📈 **Dashboard Tiles & Thresholds**

### **Primary Dashboard Tiles**
| Tile | Metric | Green | Yellow | Red | Update Frequency |
|------|--------|-------|--------|-----|------------------|
| **Refinement Rate** | refinement_shown_rate | 60-80% | 50-60% | < 50% | Real-time |
| **Acceptance Rate** | accept_rate | ≥ 45% | 30-45% | < 30% | Real-time |
| **Edit Rate** | edit_rate | 20-30% | 15-20% | < 15% | Real-time |
| **Skip Rate** | skip_rate | ≤ 35% | 35-50% | > 50% | Real-time |
| **Latency (p95)** | ttfr_refine_ms | ≤ 800ms | 800-1000ms | > 1000ms | Real-time |
| **Quality Lift** | downstream_quality_lift | ≥ 15% | 10-15% | < 10% | Hourly |
| **Complaint Rate** | complaint_rate | ≤ 5% | 5-10% | > 10% | Daily |

### **Secondary Dashboard Tiles**
| Tile | Metric | Green | Yellow | Red | Update Frequency |
|------|--------|-------|--------|-----|------------------|
| **User Satisfaction** | user_satisfaction | ≥ 4.0/5.0 | 3.5-4.0/5.0 | < 3.5/5.0 | Daily |
| **Learning Rate** | learning_rate | ≥ 20% | 15-20% | < 15% | Weekly |
| **Retention Rate** | retention_rate | ≥ 70% | 60-70% | < 60% | Weekly |
| **Cost per Refinement** | cost_per_refinement | ≤ $0.005 | $0.005-0.010 | > $0.010 | Real-time |

### **Dashboard Implementation**
```python
# Example dashboard implementation
class GuidedPromptDashboard:
    def __init__(self):
        self.tiles = {
            'refinement_rate': {
                'metric': 'refinement_shown_rate',
                'thresholds': {'green': (0.6, 0.8), 'yellow': (0.5, 0.6), 'red': (0, 0.5)},
                'update_frequency': 'real_time'
            },
            'acceptance_rate': {
                'metric': 'accept_rate',
                'thresholds': {'green': (0.45, 1.0), 'yellow': (0.3, 0.45), 'red': (0, 0.3)},
                'update_frequency': 'real_time'
            },
            'latency': {
                'metric': 'ttfr_refine_ms',
                'thresholds': {'green': (0, 800), 'yellow': (800, 1000), 'red': (1000, float('inf'))},
                'update_frequency': 'real_time'
            }
        }
    
    def get_tile_status(self, tile_name: str, current_value: float) -> str:
        """Get tile status based on current value"""
        tile_config = self.tiles.get(tile_name)
        if not tile_config:
            return 'unknown'
        
        thresholds = tile_config['thresholds']
        
        if self.is_in_range(current_value, thresholds['green']):
            return 'green'
        elif self.is_in_range(current_value, thresholds['yellow']):
            return 'yellow'
        else:
            return 'red'
    
    def is_in_range(self, value: float, range_tuple: tuple) -> bool:
        """Check if value is in range"""
        min_val, max_val = range_tuple
        return min_val <= value <= max_val
    
    def get_dashboard_data(self) -> Dict:
        """Get complete dashboard data"""
        dashboard_data = {}
        
        for tile_name, tile_config in self.tiles.items():
            current_value = self.get_current_metric_value(tile_config['metric'])
            status = self.get_tile_status(tile_name, current_value)
            
            dashboard_data[tile_name] = {
                'value': current_value,
                'status': status,
                'thresholds': tile_config['thresholds'],
                'last_updated': time.time()
            }
        
        return dashboard_data
```

---

## 🔍 **Trace ID Integration**

### **Trace ID Propagation**
The Guided Prompt Confirmation feature integrates with the main system's trace ID to provide end-to-end observability:

```python
# Example trace ID integration
class TraceIntegration:
    def __init__(self):
        self.trace_id = None
        self.span_id = None
    
    def start_trace(self, trace_id: str = None):
        """Start new trace or continue existing one"""
        if trace_id:
            self.trace_id = trace_id
        else:
            self.trace_id = self.generate_trace_id()
        
        self.span_id = self.generate_span_id()
        return self.trace_id
    
    def create_span(self, operation_name: str) -> str:
        """Create new span for operation"""
        span_id = self.generate_span_id()
        
        # Log span start
        self.log_span_start(operation_name, span_id)
        
        return span_id
    
    def end_span(self, span_id: str, success: bool, metadata: Dict = None):
        """End span with results"""
        self.log_span_end(span_id, success, metadata)
    
    def log_span_start(self, operation_name: str, span_id: str):
        """Log span start event"""
        log_data = {
            'trace_id': self.trace_id,
            'span_id': span_id,
            'operation': operation_name,
            'start_time': time.time(),
            'event_type': 'span_start'
        }
        self.send_log(log_data)
    
    def log_span_end(self, span_id: str, success: bool, metadata: Dict = None):
        """Log span end event"""
        log_data = {
            'trace_id': self.trace_id,
            'span_id': span_id,
            'success': success,
            'end_time': time.time(),
            'event_type': 'span_end',
            'metadata': metadata or {}
        }
        self.send_log(log_data)
```

### **Trace Events**
| Event | Description | Trace Level | Properties |
|-------|-------------|-------------|------------|
| **refinement_start** | Refinement process started | Span | query_hash, user_id |
| **intent_analysis** | Intent analysis completed | Span | confidence, complexity |
| **model_selection** | Model selected for refinement | Span | model_name, latency |
| **refinement_generation** | Refinement suggestions generated | Span | suggestions_count, quality |
| **user_interaction** | User interacted with suggestions | Span | interaction_type, time_ms |
| **refinement_complete** | Refinement process completed | Span | final_action, total_time |

---

## 📊 **Metrics Collection**

### **Real-time Metrics**
```python
# Example real-time metrics collection
class RealTimeMetrics:
    def __init__(self):
        self.metrics = {
            'refinement_shown_rate': 0.0,
            'accept_rate': 0.0,
            'edit_rate': 0.0,
            'skip_rate': 0.0,
            'ttfr_refine_ms': 0.0,
            'cost_per_refinement': 0.0
        }
        self.counters = {
            'total_queries': 0,
            'refinements_shown': 0,
            'suggestions_accepted': 0,
            'suggestions_edited': 0,
            'suggestions_skipped': 0,
            'refinements_timed_out': 0
        }
        self.latency_samples = []
        self.cost_samples = []
    
    def record_query(self, query_hash: str):
        """Record new query"""
        self.counters['total_queries'] += 1
        self.update_refinement_rate()
    
    def record_refinement_shown(self, suggestions_count: int, latency_ms: float):
        """Record refinement shown"""
        self.counters['refinements_shown'] += 1
        self.latency_samples.append(latency_ms)
        self.update_refinement_rate()
        self.update_latency_metrics()
    
    def record_suggestion_accepted(self, acceptance_time_ms: float):
        """Record suggestion accepted"""
        self.counters['suggestions_accepted'] += 1
        self.update_accept_rate()
    
    def record_suggestion_edited(self, edit_time_ms: float):
        """Record suggestion edited"""
        self.counters['suggestions_edited'] += 1
        self.update_edit_rate()
    
    def record_suggestion_skipped(self, skip_time_ms: float):
        """Record suggestion skipped"""
        self.counters['suggestions_skipped'] += 1
        self.update_skip_rate()
    
    def record_cost(self, cost_usd: float):
        """Record refinement cost"""
        self.cost_samples.append(cost_usd)
        self.update_cost_metrics()
    
    def update_refinement_rate(self):
        """Update refinement shown rate"""
        if self.counters['total_queries'] > 0:
            self.metrics['refinement_shown_rate'] = (
                self.counters['refinements_shown'] / self.counters['total_queries']
            )
    
    def update_accept_rate(self):
        """Update acceptance rate"""
        if self.counters['refinements_shown'] > 0:
            self.metrics['accept_rate'] = (
                self.counters['suggestions_accepted'] / self.counters['refinements_shown']
            )
    
    def update_edit_rate(self):
        """Update edit rate"""
        if self.counters['refinements_shown'] > 0:
            self.metrics['edit_rate'] = (
                self.counters['suggestions_edited'] / self.counters['refinements_shown']
            )
    
    def update_skip_rate(self):
        """Update skip rate"""
        if self.counters['refinements_shown'] > 0:
            self.metrics['skip_rate'] = (
                self.counters['suggestions_skipped'] / self.counters['refinements_shown']
            )
    
    def update_latency_metrics(self):
        """Update latency metrics"""
        if self.latency_samples:
            # Calculate p95 latency
            sorted_samples = sorted(self.latency_samples)
            p95_index = int(len(sorted_samples) * 0.95)
            self.metrics['ttfr_refine_ms'] = sorted_samples[p95_index]
    
    def update_cost_metrics(self):
        """Update cost metrics"""
        if self.cost_samples:
            self.metrics['cost_per_refinement'] = sum(self.cost_samples) / len(self.cost_samples)
    
    def get_metrics(self) -> Dict:
        """Get current metrics"""
        return self.metrics.copy()
    
    def get_counters(self) -> Dict:
        """Get current counters"""
        return self.counters.copy()
```

---

## 🚨 **Alerting & Thresholds**

### **Alert Configuration**
```python
# Example alert configuration
class AlertManager:
    def __init__(self):
        self.alerts = {
            'refinement_rate_low': {
                'metric': 'refinement_shown_rate',
                'threshold': 0.5,
                'operator': '<',
                'severity': 'warning',
                'message': 'Refinement rate is below 50%'
            },
            'acceptance_rate_low': {
                'metric': 'accept_rate',
                'threshold': 0.3,
                'operator': '<',
                'severity': 'critical',
                'message': 'Acceptance rate is below 30%'
            },
            'latency_high': {
                'metric': 'ttfr_refine_ms',
                'threshold': 1000,
                'operator': '>',
                'severity': 'warning',
                'message': 'Refinement latency is above 1000ms'
            },
            'complaint_rate_high': {
                'metric': 'complaint_rate',
                'threshold': 0.1,
                'operator': '>',
                'severity': 'critical',
                'message': 'Complaint rate is above 10%'
            }
        }
    
    def check_alerts(self, metrics: Dict) -> List[Dict]:
        """Check for alert conditions"""
        triggered_alerts = []
        
        for alert_name, alert_config in self.alerts.items():
            metric_name = alert_config['metric']
            threshold = alert_config['threshold']
            operator = alert_config['operator']
            
            if metric_name in metrics:
                current_value = metrics[metric_name]
                
                if self.evaluate_condition(current_value, operator, threshold):
                    alert = {
                        'name': alert_name,
                        'metric': metric_name,
                        'current_value': current_value,
                        'threshold': threshold,
                        'severity': alert_config['severity'],
                        'message': alert_config['message'],
                        'timestamp': time.time()
                    }
                    triggered_alerts.append(alert)
        
        return triggered_alerts
    
    def evaluate_condition(self, value: float, operator: str, threshold: float) -> bool:
        """Evaluate alert condition"""
        if operator == '<':
            return value < threshold
        elif operator == '>':
            return value > threshold
        elif operator == '<=':
            return value <= threshold
        elif operator == '>=':
            return value >= threshold
        elif operator == '==':
            return value == threshold
        else:
            return False
    
    def send_alert(self, alert: Dict):
        """Send alert notification"""
        # Implementation for sending alerts (email, Slack, PagerDuty, etc.)
        logger.warning(f"Alert triggered: {alert}")
```

---

## 📚 **References**

- Overview: `docs/prompting/guided_prompt_overview.md`
- UX Flow: `docs/prompting/guided_prompt_ux_flow.md`
- Policy: `docs/prompting/guided_prompt_policy.md`
- Toggle Contract: `docs/prompting/guided_prompt_toggle_contract.md`
- LLM Policy: `docs/prompting/guided_prompt_llm_policy.md`
- Experiments: `docs/prompting/guided_prompt_experiments.md`
- Test Cases: `docs/prompting/guided_prompt_test_cases.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This metrics specification ensures comprehensive monitoring and observability for the Guided Prompt Confirmation feature.*
