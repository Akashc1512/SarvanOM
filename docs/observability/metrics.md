# Metrics Catalog - SarvanOM v2

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE CONTRACT**  
**Purpose**: Document metrics catalog for SLA, TTFT, lane timeouts, cache hit rate, and provider health

---

## 🎯 **Metrics Overview**

SarvanOM v2 implements comprehensive observability through structured metrics that track system performance, user experience, and business outcomes. All metrics are designed to support SLO monitoring, alerting, and capacity planning.

### **Core Principles**
1. **SLO-Driven**: Metrics directly support SLO monitoring and alerting
2. **User-Centric**: Focus on metrics that impact user experience
3. **Business-Aligned**: Track metrics that drive business value
4. **Actionable**: Metrics must enable operational decisions
5. **Comprehensive**: Cover all system components and interactions

---

## 📊 **SLA Metrics**

### **Response Time Metrics**
| Metric | Description | Target | Alert Threshold | Measurement |
|--------|-------------|--------|-----------------|-------------|
| **sla_global_ms** | Global response time | < 5s/7s/10s | > 6s/8s/12s | End-to-end request time |
| **sla_ttft_ms** | Time to first token | < 1.5s | > 2s | First token delivery time |
| **sla_orchestrator_reserve_ms** | Orchestrator reserve time | < 500ms/700ms/900ms | > 600ms/800ms/1000ms | Orchestrator overhead |
| **sla_llm_ms** | LLM processing time | < 1s/1.5s/2s | > 1.5s/2s/2.5s | LLM response time |
| **sla_web_ms** | Web retrieval time | < 1s/1.5s/2s | > 1.5s/2s/2.5s | Web search time |
| **sla_vector_ms** | Vector search time | < 1s/1.5s/2s | > 1.5s/2s/2.5s | Vector search time |
| **sla_kg_ms** | Knowledge graph time | < 1s/1.5s/2s | > 1.5s/2s/2.5s | Graph query time |
| **sla_yt_ms** | YouTube processing time | < 1s/1.5s/2s | > 1.5s/2s/2.5s | Video processing time |

### **SLA Implementation**
```python
# Example SLA metrics implementation
class SLAMetrics:
    def __init__(self):
        self.sla_targets = {
            "simple": {
                "global_ms": 5000,
                "ttft_ms": 1500,
                "orchestrator_reserve_ms": 500,
                "llm_ms": 1000,
                "web_ms": 1000,
                "vector_ms": 1000,
                "kg_ms": 1000,
                "yt_ms": 1000
            },
            "technical": {
                "global_ms": 7000,
                "ttft_ms": 1500,
                "orchestrator_reserve_ms": 700,
                "llm_ms": 1500,
                "web_ms": 1500,
                "vector_ms": 1500,
                "kg_ms": 1500,
                "yt_ms": 1500
            },
            "research": {
                "global_ms": 10000,
                "ttft_ms": 1500,
                "orchestrator_reserve_ms": 900,
                "llm_ms": 2000,
                "web_ms": 2000,
                "vector_ms": 2000,
                "kg_ms": 2000,
                "yt_ms": 2000
            },
            "multimedia": {
                "global_ms": 10000,
                "ttft_ms": 1500,
                "orchestrator_reserve_ms": 900,
                "llm_ms": 2000,
                "web_ms": 2000,
                "vector_ms": 2000,
                "kg_ms": 2000,
                "yt_ms": 2000
            }
        }
    
    def record_sla_metric(self, metric_name: str, value: float, query_mode: str):
        """Record SLA metric"""
        target = self.sla_targets.get(query_mode, {}).get(metric_name, 0)
        
        # Record metric with target
        self.metrics.record_histogram(
            f"sla_{metric_name}",
            value,
            labels={"mode": query_mode, "target": target}
        )
        
        # Check if SLA is violated
        if value > target:
            self.record_sla_violation(metric_name, value, target, query_mode)
    
    def record_sla_violation(self, metric_name: str, value: float, target: float, query_mode: str):
        """Record SLA violation"""
        self.metrics.record_counter(
            "sla_violations_total",
            labels={
                "metric": metric_name,
                "mode": query_mode,
                "severity": "warning" if value <= target * 1.2 else "critical"
            }
        )
```

---

## ⚡ **Performance Metrics**

### **Lane Performance Metrics**
| Metric | Description | Target | Alert Threshold | Measurement |
|--------|-------------|--------|-----------------|-------------|
| **lane_success_rate** | Lane success rate | > 95% | < 90% | Successful lane completions |
| **lane_timeout_rate** | Lane timeout rate | < 5% | > 10% | Lane timeouts |
| **lane_error_rate** | Lane error rate | < 2% | > 5% | Lane errors |
| **lane_avg_time** | Average lane time | < 80% of budget | > 90% of budget | Average lane execution time |
| **lane_p95_time** | 95th percentile lane time | < 95% of budget | > 100% of budget | 95th percentile execution time |
| **lane_p99_time** | 99th percentile lane time | < 100% of budget | > 110% of budget | 99th percentile execution time |

### **Lane Metrics Implementation**
```python
# Example lane metrics implementation
class LaneMetrics:
    def __init__(self):
        self.lanes = [
            "web_retrieval", "vector_search", "knowledge_graph",
            "keyword_search", "news_feeds", "markets_feeds",
            "llm_synthesis", "fact_check"
        ]
    
    def record_lane_metric(self, lane_name: str, metric_name: str, value: float, labels: dict = None):
        """Record lane metric"""
        if labels is None:
            labels = {}
        
        labels["lane"] = lane_name
        
        self.metrics.record_histogram(
            f"lane_{metric_name}",
            value,
            labels=labels
        )
    
    def record_lane_success(self, lane_name: str, execution_time: float, budget_ms: int):
        """Record successful lane execution"""
        self.record_lane_metric(lane_name, "execution_time_ms", execution_time)
        self.record_lane_metric(lane_name, "budget_utilization", (execution_time / budget_ms) * 100)
        
        self.metrics.record_counter(
            "lane_success_total",
            labels={"lane": lane_name}
        )
    
    def record_lane_timeout(self, lane_name: str, budget_ms: int):
        """Record lane timeout"""
        self.metrics.record_counter(
            "lane_timeout_total",
            labels={"lane": lane_name, "budget_ms": budget_ms}
        )
    
    def record_lane_error(self, lane_name: str, error_type: str):
        """Record lane error"""
        self.metrics.record_counter(
            "lane_error_total",
            labels={"lane": lane_name, "error_type": error_type}
        )
```

---

## 🗄️ **Cache Metrics**

### **Cache Performance Metrics**
| Metric | Description | Target | Alert Threshold | Measurement |
|--------|-------------|--------|-----------------|-------------|
| **cache_hit_rate** | Cache hit rate | > 80% | < 70% | Cache hits / total requests |
| **cache_miss_rate** | Cache miss rate | < 20% | > 30% | Cache misses / total requests |
| **cache_eviction_rate** | Cache eviction rate | < 10% | > 20% | Evictions / total requests |
| **cache_size_bytes** | Cache size in bytes | < 8GB | > 12GB | Current cache size |
| **cache_ttl_utilization** | TTL utilization | > 80% | < 60% | TTL usage efficiency |
| **cache_latency_ms** | Cache access latency | < 10ms | > 50ms | Cache access time |

### **Cache Metrics Implementation**
```python
# Example cache metrics implementation
class CacheMetrics:
    def __init__(self):
        self.cache_types = [
            "query_results", "model_responses", "vector_embeddings",
            "web_content", "news_feeds", "markets_data"
        ]
    
    def record_cache_hit(self, cache_type: str, key: str, latency_ms: float):
        """Record cache hit"""
        self.metrics.record_counter(
            "cache_hits_total",
            labels={"cache_type": cache_type}
        )
        
        self.metrics.record_histogram(
            "cache_latency_ms",
            latency_ms,
            labels={"cache_type": cache_type, "result": "hit"}
        )
    
    def record_cache_miss(self, cache_type: str, key: str, latency_ms: float):
        """Record cache miss"""
        self.metrics.record_counter(
            "cache_misses_total",
            labels={"cache_type": cache_type}
        )
        
        self.metrics.record_histogram(
            "cache_latency_ms",
            latency_ms,
            labels={"cache_type": cache_type, "result": "miss"}
        )
    
    def record_cache_eviction(self, cache_type: str, reason: str):
        """Record cache eviction"""
        self.metrics.record_counter(
            "cache_evictions_total",
            labels={"cache_type": cache_type, "reason": reason}
        )
    
    def record_cache_size(self, cache_type: str, size_bytes: int):
        """Record cache size"""
        self.metrics.record_gauge(
            "cache_size_bytes",
            size_bytes,
            labels={"cache_type": cache_type}
        )
```

---

## 🔌 **Provider Health Metrics**

### **Provider Performance Metrics**
| Metric | Description | Target | Alert Threshold | Measurement |
|--------|-------------|--------|-----------------|-------------|
| **provider_uptime** | Provider uptime | > 99.9% | < 99.5% | Provider availability |
| **provider_response_time** | Provider response time | < 2s | > 5s | Provider response time |
| **provider_error_rate** | Provider error rate | < 1% | > 5% | Provider errors |
| **provider_rate_limit_hits** | Rate limit hits | < 5% | > 20% | Rate limit violations |
| **provider_quota_usage** | Quota usage | < 80% | > 95% | API quota utilization |
| **provider_data_quality** | Data quality score | > 95% | < 90% | Data quality assessment |

### **Provider Metrics Implementation**
```python
# Example provider metrics implementation
class ProviderMetrics:
    def __init__(self):
        self.providers = [
            "openai", "anthropic", "huggingface", "ollama",
            "newsapi", "reddit", "alphavantage", "yahoo_finance",
            "coingecko", "qdrant", "meilisearch", "arangodb"
        ]
    
    def record_provider_request(self, provider: str, success: bool, response_time: float, data_quality: float = 1.0):
        """Record provider request"""
        self.metrics.record_counter(
            "provider_requests_total",
            labels={"provider": provider, "success": success}
        )
        
        self.metrics.record_histogram(
            "provider_response_time_ms",
            response_time,
            labels={"provider": provider, "success": success}
        )
        
        self.metrics.record_histogram(
            "provider_data_quality",
            data_quality,
            labels={"provider": provider}
        )
    
    def record_provider_error(self, provider: str, error_type: str, error_message: str):
        """Record provider error"""
        self.metrics.record_counter(
            "provider_errors_total",
            labels={"provider": provider, "error_type": error_type}
        )
    
    def record_provider_rate_limit(self, provider: str, limit_type: str):
        """Record provider rate limit hit"""
        self.metrics.record_counter(
            "provider_rate_limits_total",
            labels={"provider": provider, "limit_type": limit_type}
        )
    
    def record_provider_quota_usage(self, provider: str, quota_type: str, usage_percent: float):
        """Record provider quota usage"""
        self.metrics.record_gauge(
            "provider_quota_usage_percent",
            usage_percent,
            labels={"provider": provider, "quota_type": quota_type}
        )
```

---

## 📈 **Business Metrics**

### **User Experience Metrics**
| Metric | Description | Target | Alert Threshold | Measurement |
|--------|-------------|--------|-----------------|-------------|
| **user_satisfaction** | User satisfaction score | > 4.5/5 | < 4.0/5 | User rating |
| **query_success_rate** | Query success rate | > 95% | < 90% | Successful queries |
| **citation_accuracy** | Citation accuracy | > 90% | < 80% | Accurate citations |
| **response_quality** | Response quality score | > 0.8 | < 0.7 | Quality assessment |
| **user_retention** | User retention rate | > 80% | < 70% | Returning users |
| **query_completion_rate** | Query completion rate | > 95% | < 90% | Completed queries |

### **Business Metrics Implementation**
```python
# Example business metrics implementation
class BusinessMetrics:
    def __init__(self):
        self.quality_thresholds = {
            "user_satisfaction": 4.0,
            "query_success_rate": 0.90,
            "citation_accuracy": 0.80,
            "response_quality": 0.70,
            "user_retention": 0.70,
            "query_completion_rate": 0.90
        }
    
    def record_user_satisfaction(self, user_id: str, rating: float, feedback: str = None):
        """Record user satisfaction"""
        self.metrics.record_histogram(
            "user_satisfaction_rating",
            rating,
            labels={"user_id": user_id}
        )
        
        if feedback:
            self.metrics.record_counter(
                "user_feedback_total",
                labels={"user_id": user_id, "rating": str(rating)}
            )
    
    def record_query_success(self, query_id: str, success: bool, quality_score: float):
        """Record query success"""
        self.metrics.record_counter(
            "query_success_total",
            labels={"query_id": query_id, "success": success}
        )
        
        self.metrics.record_histogram(
            "query_quality_score",
            quality_score,
            labels={"query_id": query_id, "success": success}
        )
    
    def record_citation_accuracy(self, query_id: str, accuracy: float, citation_count: int):
        """Record citation accuracy"""
        self.metrics.record_histogram(
            "citation_accuracy",
            accuracy,
            labels={"query_id": query_id, "citation_count": citation_count}
        )
    
    def record_user_retention(self, user_id: str, is_returning: bool, days_since_last: int):
        """Record user retention"""
        self.metrics.record_counter(
            "user_retention_total",
            labels={"user_id": user_id, "is_returning": is_returning}
        )
        
        self.metrics.record_histogram(
            "user_retention_days",
            days_since_last,
            labels={"user_id": user_id, "is_returning": is_returning}
        )
```

---

## 🔍 **System Metrics**

### **Infrastructure Metrics**
| Metric | Description | Target | Alert Threshold | Measurement |
|--------|-------------|--------|-----------------|-------------|
| **cpu_usage** | CPU utilization | < 80% | > 90% | CPU usage percentage |
| **memory_usage** | Memory utilization | < 80% | > 90% | Memory usage percentage |
| **disk_usage** | Disk utilization | < 80% | > 90% | Disk usage percentage |
| **network_usage** | Network utilization | < 80% | > 90% | Network usage percentage |
| **connection_pool_usage** | Connection pool usage | < 80% | > 90% | Connection pool utilization |
| **queue_depth** | Queue depth | < 100 | > 500 | Pending requests |

### **System Metrics Implementation**
```python
# Example system metrics implementation
class SystemMetrics:
    def __init__(self):
        self.system_components = [
            "api_gateway", "auth_service", "search_service",
            "synthesis_service", "fact_check_service", "analytics_service",
            "postgresql", "redis", "qdrant", "meilisearch", "arangodb"
        ]
    
    def record_cpu_usage(self, component: str, cpu_percent: float):
        """Record CPU usage"""
        self.metrics.record_gauge(
            "cpu_usage_percent",
            cpu_percent,
            labels={"component": component}
        )
    
    def record_memory_usage(self, component: str, memory_bytes: int):
        """Record memory usage"""
        self.metrics.record_gauge(
            "memory_usage_bytes",
            memory_bytes,
            labels={"component": component}
        )
    
    def record_disk_usage(self, component: str, disk_bytes: int):
        """Record disk usage"""
        self.metrics.record_gauge(
            "disk_usage_bytes",
            disk_bytes,
            labels={"component": component}
        )
    
    def record_network_usage(self, component: str, bytes_sent: int, bytes_received: int):
        """Record network usage"""
        self.metrics.record_gauge(
            "network_bytes_sent",
            bytes_sent,
            labels={"component": component}
        )
        
        self.metrics.record_gauge(
            "network_bytes_received",
            bytes_received,
            labels={"component": component}
        )
    
    def record_connection_pool_usage(self, component: str, active_connections: int, max_connections: int):
        """Record connection pool usage"""
        usage_percent = (active_connections / max_connections) * 100
        
        self.metrics.record_gauge(
            "connection_pool_usage_percent",
            usage_percent,
            labels={"component": component}
        )
    
    def record_queue_depth(self, queue_name: str, depth: int):
        """Record queue depth"""
        self.metrics.record_gauge(
            "queue_depth",
            depth,
            labels={"queue": queue_name}
        )
```

---

## 📊 **Metrics Collection & Storage**

### **Metrics Collection Strategy**
| Collection Method | Description | Use Case | Frequency |
|-------------------|-------------|----------|-----------|
| **Prometheus** | Pull-based metrics | System metrics | 15s |
| **StatsD** | Push-based metrics | Application metrics | Real-time |
| **Custom Collectors** | Application-specific | Business metrics | Real-time |
| **Log-based Metrics** | Log parsing | Error rates | 1m |
| **Health Checks** | Endpoint monitoring | Service health | 30s |

### **Metrics Storage**
| Storage Type | Description | Retention | Use Case |
|--------------|-------------|-----------|----------|
| **Prometheus** | Time series database | 15 days | Real-time monitoring |
| **InfluxDB** | Time series database | 90 days | Historical analysis |
| **Elasticsearch** | Search engine | 365 days | Log analysis |
| **S3** | Object storage | 7 years | Long-term storage |

### **Metrics Collection Implementation**
```python
# Example metrics collection implementation
class MetricsCollector:
    def __init__(self):
        self.prometheus_client = PrometheusClient()
        self.statsd_client = StatsDClient()
        self.custom_collectors = {}
    
    def collect_system_metrics(self):
        """Collect system metrics"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.prometheus_client.record_gauge("cpu_usage_percent", cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.prometheus_client.record_gauge("memory_usage_percent", memory.percent)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        self.prometheus_client.record_gauge("disk_usage_percent", (disk.used / disk.total) * 100)
        
        # Network usage
        network = psutil.net_io_counters()
        self.prometheus_client.record_gauge("network_bytes_sent", network.bytes_sent)
        self.prometheus_client.record_gauge("network_bytes_received", network.bytes_recv)
    
    def collect_application_metrics(self):
        """Collect application metrics"""
        # Request metrics
        request_count = self.get_request_count()
        self.statsd_client.record_counter("requests_total", request_count)
        
        # Response time metrics
        response_time = self.get_avg_response_time()
        self.statsd_client.record_histogram("response_time_ms", response_time)
        
        # Error metrics
        error_count = self.get_error_count()
        self.statsd_client.record_counter("errors_total", error_count)
    
    def collect_business_metrics(self):
        """Collect business metrics"""
        # User satisfaction
        satisfaction = self.get_user_satisfaction()
        self.custom_collectors["user_satisfaction"].record(satisfaction)
        
        # Query success rate
        success_rate = self.get_query_success_rate()
        self.custom_collectors["query_success_rate"].record(success_rate)
        
        # Citation accuracy
        citation_accuracy = self.get_citation_accuracy()
        self.custom_collectors["citation_accuracy"].record(citation_accuracy)
```

---

## 📚 **References**

- Observability & Budgets: `09_observability_and_budgets.md`
- System Context: `docs/architecture/system_context.md`
- Service Catalog: `docs/architecture/service_catalog.md`
- Budgets: `docs/architecture/budgets.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This metrics catalog provides comprehensive observability for SarvanOM v2 system performance and user experience.*
