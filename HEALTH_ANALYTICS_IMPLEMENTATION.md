# Health Endpoints and Analytics Tracking Implementation

## Overview

This document describes the implementation of comprehensive health endpoints and analytics tracking in the Universal Knowledge Platform backend. The implementation provides real-time service health monitoring and detailed analytics for query processing, user interactions, and system performance.

## Health Endpoints

### 1. Basic Health Check (`/health`)

**Endpoint:** `GET /health`

**Purpose:** Quick health status check for load balancers and basic monitoring.

**Response:**
```json
{
  "status": "ok|degraded|error",
  "timestamp": "2024-01-15 10:30:45",
  "response_time_ms": 150,
  "external_services": {
    "overall_healthy": true,
    "vector_db": {"healthy": true, "latency_ms": 25},
    "elasticsearch": {"healthy": true, "status": "green"},
    "redis": {"healthy": true, "latency_ms": 5},
    "knowledge_graph": {"healthy": true, "latency_ms": 45}
  },
  "agent_services": {
    "overall_healthy": true,
    "browser": {"healthy": true},
    "pdf": {"healthy": true},
    "knowledge": {"healthy": true},
    "code": {"healthy": true},
    "database": {"healthy": true},
    "crawler": {"healthy": true}
  },
  "overall_healthy": true
}
```

### 2. Detailed Health Check (`/health/detailed`)

**Endpoint:** `GET /health/detailed`

**Purpose:** Comprehensive health status for frontend dashboards and detailed monitoring.

**Response:**
```json
{
  "status": "ok|degraded|error",
  "timestamp": "2024-01-15 10:30:45",
  "response_time_ms": 250,
  "overall_healthy": true,
  "services": {
    "external": { /* external service health */ },
    "agents": { /* agent service health */ }
  },
  "metrics": {
    "query_intelligence": { /* query intelligence metrics */ },
    "orchestration": { /* orchestration metrics */ },
    "retrieval": { /* retrieval metrics */ },
    "memory": { /* memory metrics */ },
    "expert_validation": { /* expert validation metrics */ },
    "business": { /* business metrics */ }
  },
  "performance": {
    "uptime_seconds": 86400,
    "total_requests": 1250,
    "avg_response_time": 1.2,
    "error_rate": 0.02
  },
  "recommendations": [
    "System is performing optimally",
    "Consider scaling if request volume increases"
  ]
}
```

## Analytics Endpoints

### 1. Analytics Overview (`/analytics`)

**Endpoint:** `GET /analytics`

**Purpose:** Comprehensive analytics data for all platform components.

**Response:**
```json
{
  "metrics": {
    "query_intelligence": { /* detailed metrics */ },
    "orchestration": { /* detailed metrics */ },
    "retrieval": { /* detailed metrics */ },
    "memory": { /* detailed metrics */ },
    "expert_validation": { /* detailed metrics */ },
    "business": { /* detailed metrics */ }
  },
  "timestamp": "2024-01-15 10:30:45",
  "platform_status": "operational",
  "data_sources": {
    "query_intelligence": "active",
    "orchestration": "active",
    "retrieval": "active",
    "memory": "active",
    "expert_validation": "active",
    "business_metrics": "active"
  }
}
```

### 2. Analytics Summary (`/analytics/summary`)

**Endpoint:** `GET /analytics/summary?time_range=30d`

**Purpose:** Time-based analytics summary for dashboards.

**Response:**
```json
{
  "time_range": "30d",
  "total_queries": 1250,
  "average_response_time": 1.2,
  "success_rate": 0.95,
  "top_query_types": [
    {"type": "search", "count": 150},
    {"type": "fact_check", "count": 75},
    {"type": "synthesis", "count": 50}
  ],
  "service_health": {
    "retrieval": "healthy",
    "synthesis": "healthy",
    "fact_check": "healthy",
    "knowledge_graph": "healthy"
  },
  "performance_metrics": {
    "avg_processing_time_ms": 1200,
    "cache_hit_rate": 0.65,
    "error_rate": 0.02
  },
  "timestamp": "2024-01-15 10:30:45"
}
```

### 3. Analytics Tracking (`/analytics/track`)

**Endpoint:** `POST /analytics/track`

**Purpose:** Track custom analytics events from frontend.

**Request Body:**
```json
{
  "event_type": "page_view|button_click|form_submit|search_query|result_view|feedback_submit|error_occurred",
  "user_id": "user_123",
  "session_id": "session_456",
  "properties": {
    "page": "/search",
    "query": "machine learning",
    "result_count": 15
  },
  "timestamp": "2024-01-15T10:30:45Z"
}
```

## Service Endpoints with Analytics

### 1. Search Endpoint (`/search`)

**Enhanced with:**
- Query intelligence metrics
- Retrieval metrics
- Business metrics
- Processing time tracking
- Error tracking

### 2. Fact-Check Endpoint (`/fact-check`)

**Enhanced with:**
- Query intelligence metrics
- Expert validation metrics
- Business metrics
- Processing time tracking
- Error tracking

### 3. Synthesis Endpoint (`/synthesize`)

**Enhanced with:**
- Query intelligence metrics
- Orchestration metrics
- Business metrics
- Processing time tracking
- Error tracking

## LeadOrchestrator Analytics Integration

The `LeadOrchestrator.process_query()` method has been enhanced with comprehensive analytics tracking:

### Metrics Recorded:

1. **Query Intelligence Metrics:**
   - Intent type classification
   - Complexity level assessment
   - Domain type identification
   - Cache hit/miss tracking

2. **Orchestration Metrics:**
   - Model type selection
   - Strategy execution
   - Processing duration
   - Fallback usage
   - Circuit breaker state

3. **Retrieval Metrics:**
   - Source type identification
   - Fusion strategy performance
   - Result count tracking
   - Confidence score recording

4. **Business Metrics:**
   - User identification
   - Query type classification
   - Response time measurement
   - Satisfaction score tracking
   - Error type classification

## Metrics Categories

### 1. Query Intelligence Metrics
- Total requests by intent type
- Processing duration by complexity
- Cache hit/miss rates
- Domain type distribution

### 2. Orchestration Metrics
- Model type usage distribution
- Strategy effectiveness
- Processing duration
- Fallback usage rates
- Circuit breaker states

### 3. Retrieval Metrics
- Source type performance
- Fusion strategy effectiveness
- Result count distribution
- Confidence score distribution

### 4. Memory Metrics
- Operation type tracking
- Memory type usage
- Success rates
- Size and item count tracking
- Hit rate monitoring

### 5. Expert Validation Metrics
- Network type performance
- Validation status distribution
- Processing duration
- Consensus score tracking
- Agreement ratio monitoring

### 6. Business Metrics
- User activity tracking
- Query type distribution
- Complexity assessment
- Response time monitoring
- Satisfaction score tracking
- Error type classification

### 7. System Metrics
- Uptime monitoring
- Error count tracking
- Error rate calculation
- Component-specific metrics

## Testing

### Test Script: `test_health_analytics.py`

The test script provides comprehensive testing of:

1. **Health Endpoints:**
   - Basic health check
   - Detailed health check
   - Response time validation
   - Service status verification

2. **Analytics Endpoints:**
   - Analytics overview
   - Analytics summary
   - Time range filtering
   - Data source verification

3. **Service Endpoints:**
   - Search with analytics
   - Fact-check with analytics
   - Synthesis with analytics
   - Processing time validation

### Running Tests:

```bash
python test_health_analytics.py
```

## Implementation Details

### Health Check Implementation

1. **External Services:** Uses `services.analytics.health_checks.check_all_services()`
2. **Agent Services:** Uses `ServiceProvider.health_check_all_services()`
3. **Metrics Integration:** Uses `KnowledgePlatformMetricsCollector`
4. **Error Handling:** Comprehensive exception handling with detailed error reporting

### Analytics Implementation

1. **Metrics Collection:** Uses Prometheus-compatible metrics
2. **Real-time Tracking:** Immediate metric recording on each request
3. **Performance Monitoring:** Response time and error rate tracking
4. **Business Intelligence:** User behavior and query pattern analysis

### Service Provider Integration

1. **Health Checks:** Integrated with existing ServiceProvider pattern
2. **Service Discovery:** Automatic detection of all registered services
3. **Status Aggregation:** Comprehensive health status compilation
4. **Recommendation Engine:** Intelligent recommendations based on metrics

## Monitoring and Alerting

### Health Status Levels:

1. **OK:** All services healthy, performance within normal ranges
2. **Degraded:** Some services experiencing issues, performance impacted
3. **Error:** Critical services down, immediate attention required

### Key Metrics for Alerting:

1. **Error Rate:** > 5% triggers warning
2. **Response Time:** > 5 seconds triggers warning
3. **Service Health:** Any service unhealthy triggers alert
4. **Cache Hit Rate:** < 50% triggers optimization recommendation

## Future Enhancements

1. **Real-time Dashboard:** WebSocket-based real-time metrics
2. **Predictive Analytics:** ML-based performance prediction
3. **Auto-scaling:** Metrics-driven auto-scaling decisions
4. **Advanced Alerting:** Intelligent alerting based on patterns
5. **Custom Metrics:** User-defined custom metrics
6. **Historical Analysis:** Long-term trend analysis
7. **Performance Optimization:** Automated performance recommendations

## Configuration

### Environment Variables:

```bash
# Health check timeouts
HEALTH_CHECK_TIMEOUT=5.0

# Analytics configuration
ANALYTICS_ENABLED=true
METRICS_RETENTION_DAYS=30

# Service URLs
VECTOR_DB_URL=http://localhost:6333
ELASTICSEARCH_URL=http://localhost:9200
REDIS_URL=redis://localhost:6379
```

### Metrics Configuration:

```python
# In knowledge_platform_metrics.py
class KnowledgePlatformMetricsCollector:
    def __init__(self):
        # Configure metrics collection intervals
        self.collection_interval = 60  # seconds
        self.retention_period = 30     # days
        self.max_metrics_count = 10000
```

## Troubleshooting

### Common Issues:

1. **Health Check Timeouts:**
   - Increase `HEALTH_CHECK_TIMEOUT`
   - Check network connectivity
   - Verify service URLs

2. **Metrics Collection Errors:**
   - Check Prometheus client configuration
   - Verify metric registration
   - Check memory usage

3. **Service Provider Issues:**
   - Verify service registration
   - Check DI container configuration
   - Review service dependencies

### Debug Commands:

```bash
# Test health endpoints
curl http://localhost:8000/health
curl http://localhost:8000/health/detailed

# Test analytics endpoints
curl http://localhost:8000/analytics
curl http://localhost:8000/analytics/summary

# Test service endpoints
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "user_id": "test_user"}'
```

## Conclusion

This implementation provides comprehensive health monitoring and analytics tracking for the Universal Knowledge Platform. The system is designed to be:

- **Scalable:** Handles high request volumes
- **Reliable:** Comprehensive error handling
- **Observable:** Detailed metrics and logging
- **Maintainable:** Clean separation of concerns
- **Extensible:** Easy to add new metrics and endpoints

The health endpoints and analytics tracking are now fully integrated and ready for production use. 