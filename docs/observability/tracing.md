# Tracing Spans - SarvanOM v2

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE CONTRACT**  
**Purpose**: Document tracing spans for trace-ID propagation, lane spans, and external calls

---

## 🎯 **Tracing Overview**

SarvanOM v2 implements distributed tracing to track requests across all services and external dependencies. Tracing provides visibility into request flow, performance bottlenecks, and error propagation.

### **Core Principles**
1. **End-to-End Visibility**: Track requests from frontend to backend to external services
2. **Performance Analysis**: Identify bottlenecks and optimization opportunities
3. **Error Propagation**: Understand how errors flow through the system
4. **Dependency Mapping**: Map service dependencies and interactions
5. **Root Cause Analysis**: Enable quick identification of failure points

---

## 🔍 **Trace Structure**

### **Trace Hierarchy**
```
Request Trace
├── Frontend Span
│   ├── API Gateway Span
│   │   ├── Auth Service Span
│   │   ├── Search Service Span
│   │   │   ├── Web Retrieval Lane Span
│   │   │   │   ├── External Web API Span
│   │   │   │   └── Content Processing Span
│   │   │   ├── Vector Search Lane Span
│   │   │   │   ├── Qdrant Query Span
│   │   │   │   └── Embedding Generation Span
│   │   │   ├── Knowledge Graph Lane Span
│   │   │   │   ├── ArangoDB Query Span
│   │   │   │   └── Graph Processing Span
│   │   │   ├── Keyword Search Lane Span
│   │   │   │   ├── Meilisearch Query Span
│   │   │   │   └── Result Processing Span
│   │   │   ├── News Feeds Lane Span
│   │   │   │   ├── News API Span
│   │   │   │   └── Content Aggregation Span
│   │   │   └── Markets Feeds Lane Span
│   │   │       ├── Financial API Span
│   │   │       └── Data Processing Span
│   │   ├── Synthesis Service Span
│   │   │   ├── LLM Selection Span
│   │   │   ├── Model Orchestration Span
│   │   │   │   ├── OpenAI API Span
│   │   │   │   ├── Anthropic API Span
│   │   │   │   ├── HuggingFace API Span
│   │   │   │   └── Ollama API Span
│   │   │   ├── Response Generation Span
│   │   │   └── Quality Assessment Span
│   │   ├── Fact Check Service Span
│   │   │   ├── Claim Extraction Span
│   │   │   ├── Source Verification Span
│   │   │   └── Accuracy Scoring Span
│   │   └── Analytics Service Span
│   │       ├── Metrics Collection Span
│   │       ├── User Behavior Span
│   │       └── Performance Analysis Span
│   └── Response Processing Span
└── Cache Operations Span
    ├── Cache Hit Span
    ├── Cache Miss Span
    └── Cache Update Span
```

---

## 🏷️ **Span Types & Attributes**

### **Frontend Spans**
| Span Name | Description | Attributes | Duration Target |
|-----------|-------------|------------|-----------------|
| **frontend_request** | Frontend request handling | `user_id`, `session_id`, `query_type` | < 100ms |
| **api_call** | API call to backend | `endpoint`, `method`, `status_code` | < 200ms |
| **ui_rendering** | UI component rendering | `component`, `props`, `state` | < 50ms |
| **user_interaction** | User interaction handling | `action`, `element`, `context` | < 100ms |

### **API Gateway Spans**
| Span Name | Description | Attributes | Duration Target |
|-----------|-------------|------------|-----------------|
| **gateway_request** | Gateway request processing | `request_id`, `user_id`, `endpoint` | < 50ms |
| **auth_validation** | Authentication validation | `user_id`, `token_type`, `permissions` | < 100ms |
| **rate_limiting** | Rate limiting check | `user_id`, `endpoint`, `limit_type` | < 10ms |
| **request_routing** | Request routing to services | `service`, `endpoint`, `method` | < 20ms |

### **Service Spans**
| Span Name | Description | Attributes | Duration Target |
|-----------|-------------|------------|-----------------|
| **service_request** | Service request processing | `service`, `endpoint`, `user_id` | < 100ms |
| **database_query** | Database query execution | `database`, `query_type`, `table` | < 200ms |
| **cache_operation** | Cache operation | `cache_type`, `operation`, `key` | < 10ms |
| **external_api_call** | External API call | `provider`, `endpoint`, `status_code` | < 2s |

### **Lane Spans**
| Span Name | Description | Attributes | Duration Target |
|-----------|-------------|------------|-----------------|
| **lane_execution** | Lane execution | `lane_name`, `query_mode`, `budget_ms` | < 5s/7s/10s |
| **lane_parallel_execution** | Parallel lane execution | `lane_count`, `query_mode`, `budget_ms` | < 5s/7s/10s |
| **lane_fusion** | Lane result fusion | `lane_count`, `fusion_method`, `result_count` | < 100ms |
| **lane_timeout** | Lane timeout handling | `lane_name`, `timeout_ms`, `reason` | < 50ms |

---

## 🔗 **Trace-ID Propagation**

### **Trace-ID Format**
```
Format: {service}-{timestamp}-{random}
Example: frontend-20250909120000-abc123def456
```

### **Propagation Headers**
| Header | Description | Format | Example |
|--------|-------------|--------|---------|
| **X-Trace-ID** | Main trace identifier | `{service}-{timestamp}-{random}` | `frontend-20250909120000-abc123def456` |
| **X-Span-ID** | Current span identifier | `{random}` | `def456ghi789` |
| **X-Parent-Span-ID** | Parent span identifier | `{random}` | `abc123def456` |
| **X-Service-Name** | Service name | `{service}` | `api-gateway` |
| **X-Request-ID** | Request identifier | `{uuid}` | `550e8400-e29b-41d4-a716-446655440000` |

### **Trace-ID Propagation Implementation**
```python
# Example trace-ID propagation implementation
class TracePropagation:
    def __init__(self):
        self.trace_id = None
        self.span_id = None
        self.parent_span_id = None
        self.service_name = None
        self.request_id = None
    
    def start_trace(self, service_name: str, request_id: str = None):
        """Start new trace"""
        if request_id is None:
            request_id = str(uuid.uuid4())
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        
        self.trace_id = f"{service_name}-{timestamp}-{random_suffix}"
        self.span_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        self.parent_span_id = None
        self.service_name = service_name
        self.request_id = request_id
        
        return {
            "X-Trace-ID": self.trace_id,
            "X-Span-ID": self.span_id,
            "X-Service-Name": self.service_name,
            "X-Request-ID": self.request_id
        }
    
    def create_child_span(self, service_name: str):
        """Create child span"""
        child_span_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        
        return {
            "X-Trace-ID": self.trace_id,
            "X-Span-ID": child_span_id,
            "X-Parent-Span-ID": self.span_id,
            "X-Service-Name": service_name,
            "X-Request-ID": self.request_id
        }
    
    def propagate_trace(self, headers: dict):
        """Propagate trace to external service"""
        return {
            "X-Trace-ID": self.trace_id,
            "X-Span-ID": self.span_id,
            "X-Parent-Span-ID": self.parent_span_id,
            "X-Service-Name": self.service_name,
            "X-Request-ID": self.request_id,
            **headers
        }
```

---

## 🚀 **Lane Spans**

### **Web Retrieval Lane Spans**
| Span Name | Description | Attributes | Duration Target |
|-----------|-------------|------------|-----------------|
| **web_retrieval_start** | Web retrieval initiation | `query`, `search_engines`, `max_results` | < 50ms |
| **search_engine_query** | Search engine query | `engine`, `query`, `results_count` | < 1s |
| **content_extraction** | Content extraction | `url`, `content_type`, `size_bytes` | < 500ms |
| **content_processing** | Content processing | `processing_type`, `quality_score` | < 200ms |
| **web_retrieval_fusion** | Web result fusion | `result_count`, `fusion_method` | < 100ms |

### **Vector Search Lane Spans**
| Span Name | Description | Attributes | Duration Target |
|-----------|-------------|------------|-----------------|
| **vector_search_start** | Vector search initiation | `query`, `collection`, `top_k` | < 50ms |
| **embedding_generation** | Embedding generation | `model`, `text_length`, `dimensions` | < 200ms |
| **qdrant_query** | Qdrant query execution | `collection`, `vector_dim`, `top_k` | < 500ms |
| **result_ranking** | Result ranking | `result_count`, `ranking_method` | < 100ms |
| **vector_search_fusion** | Vector result fusion | `result_count`, `fusion_method` | < 100ms |

### **Knowledge Graph Lane Spans**
| Span Name | Description | Attributes | Duration Target |
|-----------|-------------|------------|-----------------|
| **kg_search_start** | Knowledge graph search initiation | `query`, `graph_type`, `max_depth` | < 50ms |
| **arango_query** | ArangoDB query execution | `query_type`, `collection`, `result_count` | < 500ms |
| **graph_traversal** | Graph traversal | `start_node`, `max_depth`, `path_count` | < 300ms |
| **entity_extraction** | Entity extraction | `entity_count`, `entity_types` | < 200ms |
| **kg_search_fusion** | Knowledge graph result fusion | `result_count`, `fusion_method` | < 100ms |

### **Keyword Search Lane Spans**
| Span Name | Description | Attributes | Duration Target |
|-----------|-------------|------------|-----------------|
| **keyword_search_start** | Keyword search initiation | `query`, `indexes`, `filters` | < 50ms |
| **meili_query** | Meilisearch query execution | `index`, `query_type`, `result_count` | < 300ms |
| **result_filtering** | Result filtering | `filter_count`, `filtered_count` | < 100ms |
| **result_ranking** | Result ranking | `result_count`, `ranking_method` | < 100ms |
| **keyword_search_fusion** | Keyword result fusion | `result_count`, `fusion_method` | < 100ms |

### **News Feeds Lane Spans**
| Span Name | Description | Attributes | Duration Target |
|-----------|-------------|------------|-----------------|
| **news_feeds_start** | News feeds initiation | `query`, `sources`, `time_range` | < 50ms |
| **news_api_call** | News API call | `provider`, `endpoint`, `article_count` | < 800ms |
| **content_aggregation** | Content aggregation | `source_count`, `article_count` | < 200ms |
| **content_filtering** | Content filtering | `filter_count`, `filtered_count` | < 100ms |
| **news_feeds_fusion** | News result fusion | `result_count`, `fusion_method` | < 100ms |

### **Markets Feeds Lane Spans**
| Span Name | Description | Attributes | Duration Target |
|-----------|-------------|------------|-----------------|
| **markets_feeds_start** | Markets feeds initiation | `query`, `data_types`, `time_range` | < 50ms |
| **financial_api_call** | Financial API call | `provider`, `endpoint`, `data_count` | < 800ms |
| **data_processing** | Data processing | `data_type`, `processing_method` | < 200ms |
| **data_validation** | Data validation | `validation_rules`, `valid_count` | < 100ms |
| **markets_feeds_fusion** | Markets result fusion | `result_count`, `fusion_method` | < 100ms |

---

## 🔌 **External Call Spans**

### **LLM Provider Spans**
| Span Name | Description | Attributes | Duration Target |
|-----------|-------------|------------|-----------------|
| **llm_selection** | LLM model selection | `query_type`, `model_class`, `selected_model` | < 50ms |
| **llm_api_call** | LLM API call | `provider`, `model`, `tokens_in`, `tokens_out` | < 2s |
| **response_processing** | Response processing | `processing_type`, `quality_score` | < 100ms |
| **cost_calculation** | Cost calculation | `provider`, `model`, `cost_usd` | < 10ms |

### **Database Spans**
| Span Name | Description | Attributes | Duration Target |
|-----------|-------------|------------|-----------------|
| **db_connection** | Database connection | `database`, `connection_type`, `pool_size` | < 100ms |
| **db_query** | Database query | `database`, `query_type`, `table`, `rows` | < 200ms |
| **db_transaction** | Database transaction | `database`, `transaction_type`, `duration` | < 500ms |
| **db_connection_pool** | Connection pool operation | `database`, `operation`, `pool_size` | < 10ms |

### **Cache Spans**
| Span Name | Description | Attributes | Duration Target |
|-----------|-------------|------------|-----------------|
| **cache_lookup** | Cache lookup | `cache_type`, `key`, `hit` | < 10ms |
| **cache_store** | Cache store | `cache_type`, `key`, `size_bytes` | < 20ms |
| **cache_eviction** | Cache eviction | `cache_type`, `reason`, `evicted_count` | < 10ms |
| **cache_invalidation** | Cache invalidation | `cache_type`, `pattern`, `invalidated_count` | < 50ms |

---

## 📊 **Span Attributes & Tags**

### **Common Attributes**
| Attribute | Description | Type | Example |
|-----------|-------------|------|---------|
| **trace_id** | Trace identifier | String | `frontend-20250909120000-abc123def456` |
| **span_id** | Span identifier | String | `def456ghi789` |
| **parent_span_id** | Parent span identifier | String | `abc123def456` |
| **service_name** | Service name | String | `api-gateway` |
| **operation_name** | Operation name | String | `process_query` |
| **start_time** | Span start time | Timestamp | `2025-09-09T12:00:00Z` |
| **end_time** | Span end time | Timestamp | `2025-09-09T12:00:01Z` |
| **duration_ms** | Span duration | Number | `1000` |
| **status** | Span status | String | `success`, `error`, `timeout` |
| **error_message** | Error message | String | `Connection timeout` |

### **Query-Specific Attributes**
| Attribute | Description | Type | Example |
|-----------|-------------|------|---------|
| **query_id** | Query identifier | String | `q_550e8400-e29b-41d4-a716-446655440000` |
| **query_type** | Query type | String | `simple`, `technical`, `research`, `multimedia` |
| **query_mode** | Query mode | String | `simple`, `technical`, `research`, `multimedia` |
| **user_id** | User identifier | String | `user_12345` |
| **session_id** | Session identifier | String | `session_67890` |
| **intent** | Query intent | String | `information`, `analysis`, `comparison` |
| **complexity** | Query complexity | String | `low`, `medium`, `high` |

### **Performance Attributes**
| Attribute | Description | Type | Example |
|-----------|-------------|------|---------|
| **budget_ms** | Time budget | Number | `5000` |
| **actual_ms** | Actual duration | Number | `4500` |
| **budget_utilization** | Budget utilization | Number | `0.9` |
| **sla_violation** | SLA violation | Boolean | `false` |
| **timeout_ms** | Timeout threshold | Number | `6000` |
| **retry_count** | Retry count | Number | `0` |
| **circuit_breaker** | Circuit breaker state | String | `closed`, `open`, `half-open` |

### **External Service Attributes**
| Attribute | Description | Type | Example |
|-----------|-------------|------|---------|
| **provider** | External provider | String | `openai`, `anthropic`, `huggingface` |
| **endpoint** | API endpoint | String | `/v1/chat/completions` |
| **status_code** | HTTP status code | Number | `200` |
| **response_size** | Response size | Number | `1024` |
| **rate_limit_remaining** | Rate limit remaining | Number | `100` |
| **quota_usage** | Quota usage | Number | `0.75` |
| **cost_usd** | Cost in USD | Number | `0.001` |

---

## 🔧 **Tracing Implementation**

### **Tracing Setup**
```python
# Example tracing setup implementation
class TracingSetup:
    def __init__(self):
        self.tracer = None
        self.trace_propagation = TracePropagation()
        self.span_processors = []
    
    def setup_tracing(self, service_name: str):
        """Setup tracing for service"""
        # Configure trace exporter
        trace_exporter = OTLPSpanExporter(
            endpoint="http://jaeger:14268/api/traces",
            insecure=True
        )
        
        # Configure span processor
        span_processor = BatchSpanProcessor(trace_exporter)
        self.span_processors.append(span_processor)
        
        # Configure tracer provider
        tracer_provider = TracerProvider(
            resource=Resource.create({
                "service.name": service_name,
                "service.version": "2.0.0"
            })
        )
        
        for processor in self.span_processors:
            tracer_provider.add_span_processor(processor)
        
        # Set global tracer provider
        trace.set_tracer_provider(tracer_provider)
        
        # Get tracer
        self.tracer = trace.get_tracer(__name__)
        
        return self.tracer
    
    def create_span(self, name: str, parent_span=None, attributes: dict = None):
        """Create span"""
        if attributes is None:
            attributes = {}
        
        span = self.tracer.start_span(
            name=name,
            parent=parent_span,
            attributes=attributes
        )
        
        return span
    
    def end_span(self, span, status: str = "success", error: Exception = None):
        """End span"""
        if error:
            span.set_status(Status(StatusCode.ERROR, str(error)))
            span.record_exception(error)
        else:
            span.set_status(Status(StatusCode.OK))
        
        span.end()
```

### **Span Decorators**
```python
# Example span decorators implementation
def trace_span(name: str, attributes: dict = None):
    """Decorator for tracing spans"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            
            with tracer.start_span(name=name, attributes=attributes) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        
        return wrapper
    return decorator

def trace_external_call(provider: str, endpoint: str):
    """Decorator for tracing external calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            
            with tracer.start_span(
                name=f"external_call_{provider}",
                attributes={
                    "provider": provider,
                    "endpoint": endpoint,
                    "call_type": "external"
                }
            ) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        
        return wrapper
    return decorator
```

---

## 📈 **Tracing Analytics**

### **Trace Analysis Metrics**
| Metric | Description | Calculation | Use Case |
|--------|-------------|-------------|----------|
| **Trace Duration** | Total trace duration | `end_time - start_time` | Performance analysis |
| **Span Count** | Number of spans per trace | `count(spans)` | Complexity analysis |
| **Error Rate** | Error rate per trace | `error_spans / total_spans` | Reliability analysis |
| **External Call Count** | External calls per trace | `count(external_spans)` | Dependency analysis |
| **Cache Hit Rate** | Cache hit rate per trace | `cache_hits / cache_requests` | Cache efficiency |
| **SLA Violation Rate** | SLA violations per trace | `sla_violations / total_spans` | SLA monitoring |

### **Trace Analytics Implementation**
```python
# Example trace analytics implementation
class TraceAnalytics:
    def __init__(self):
        self.trace_metrics = {}
        self.span_metrics = {}
    
    def analyze_trace(self, trace_id: str, spans: list):
        """Analyze trace"""
        trace_analysis = {
            "trace_id": trace_id,
            "total_spans": len(spans),
            "total_duration_ms": 0,
            "error_count": 0,
            "external_call_count": 0,
            "cache_hit_count": 0,
            "sla_violation_count": 0,
            "span_breakdown": {}
        }
        
        for span in spans:
            # Calculate total duration
            if span.end_time and span.start_time:
                duration = (span.end_time - span.start_time).total_seconds() * 1000
                trace_analysis["total_duration_ms"] += duration
            
            # Count errors
            if span.status == "error":
                trace_analysis["error_count"] += 1
            
            # Count external calls
            if span.attributes.get("call_type") == "external":
                trace_analysis["external_call_count"] += 1
            
            # Count cache hits
            if span.attributes.get("cache_hit"):
                trace_analysis["cache_hit_count"] += 1
            
            # Count SLA violations
            if span.attributes.get("sla_violation"):
                trace_analysis["sla_violation_count"] += 1
            
            # Span breakdown
            span_type = span.attributes.get("span_type", "unknown")
            if span_type not in trace_analysis["span_breakdown"]:
                trace_analysis["span_breakdown"][span_type] = 0
            trace_analysis["span_breakdown"][span_type] += 1
        
        return trace_analysis
    
    def generate_trace_report(self, trace_analysis: dict):
        """Generate trace report"""
        report = {
            "summary": {
                "total_spans": trace_analysis["total_spans"],
                "total_duration_ms": trace_analysis["total_duration_ms"],
                "error_rate": trace_analysis["error_count"] / trace_analysis["total_spans"],
                "external_call_rate": trace_analysis["external_call_count"] / trace_analysis["total_spans"],
                "cache_hit_rate": trace_analysis["cache_hit_count"] / trace_analysis["total_spans"],
                "sla_violation_rate": trace_analysis["sla_violation_count"] / trace_analysis["total_spans"]
            },
            "span_breakdown": trace_analysis["span_breakdown"],
            "recommendations": self._generate_recommendations(trace_analysis)
        }
        
        return report
    
    def _generate_recommendations(self, trace_analysis: dict):
        """Generate recommendations based on trace analysis"""
        recommendations = []
        
        # Error rate recommendations
        if trace_analysis["error_count"] > 0:
            recommendations.append({
                "type": "error_rate",
                "message": f"High error rate: {trace_analysis['error_count']} errors in {trace_analysis['total_spans']} spans",
                "action": "Investigate error patterns and implement error handling"
            })
        
        # External call recommendations
        if trace_analysis["external_call_count"] > 5:
            recommendations.append({
                "type": "external_calls",
                "message": f"High external call count: {trace_analysis['external_call_count']} calls",
                "action": "Consider caching or batching external calls"
            })
        
        # Cache efficiency recommendations
        if trace_analysis["cache_hit_count"] < trace_analysis["total_spans"] * 0.5:
            recommendations.append({
                "type": "cache_efficiency",
                "message": f"Low cache hit rate: {trace_analysis['cache_hit_count']} hits",
                "action": "Review cache strategy and TTL settings"
            })
        
        # SLA violation recommendations
        if trace_analysis["sla_violation_count"] > 0:
            recommendations.append({
                "type": "sla_violations",
                "message": f"SLA violations detected: {trace_analysis['sla_violation_count']} violations",
                "action": "Review performance bottlenecks and optimize critical paths"
            })
        
        return recommendations
```

---

## 📚 **References**

- Observability & Budgets: `09_observability_and_budgets.md`
- Metrics Catalog: `docs/observability/metrics.md`
- System Context: `docs/architecture/system_context.md`
- Service Catalog: `docs/architecture/service_catalog.md`
- Budgets: `docs/architecture/budgets.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This tracing specification provides comprehensive distributed tracing for SarvanOM v2 system observability and performance analysis.*
