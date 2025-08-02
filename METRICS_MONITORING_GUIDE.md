# Universal Knowledge Platform - Metrics & Monitoring Guide

## Overview

The Universal Knowledge Platform includes a comprehensive metrics and monitoring system that provides real-time insights into platform health, performance, and usage patterns. This system enables proactive monitoring, performance optimization, and operational excellence.

## Features

### 📊 Metrics Collection
- **Query Processing Metrics**: Total queries, success rates, response times
- **Response Time Breakdown**: Retrieval, LLM, and synthesis time tracking
- **Cache Performance**: Hit/miss ratios for all cache layers
- **LLM Provider Usage**: Tracking of Ollama, HuggingFace, OpenAI, and Anthropic usage
- **Error Tracking**: Comprehensive error categorization and counting
- **Health Status**: Real-time component health monitoring

### 🏥 Health Checks
- **Database Connections**: PostgreSQL connection health
- **Search Engine**: Meilisearch availability and performance
- **Vector Database**: Vector retrieval system health
- **LLM APIs**: Provider-specific health checks (Ollama, HF, OpenAI)
- **FactChecker**: Validation logic health verification
- **Comprehensive Reports**: Structured health status with component details

### 📈 Monitoring Endpoints
- **`/metrics`**: JSON and Prometheus-formatted metrics
- **`/health`**: Comprehensive system health status
- **Prometheus Integration**: Ready for monitoring stack integration

## API Endpoints

### GET `/metrics`

Returns comprehensive platform metrics in JSON or Prometheus format.

**Parameters:**
- `format` (optional): `json` (default) or `prometheus`
- `admin` (optional): `false` (default) - admin metrics not enabled

**JSON Response Example:**
```json
{
  "timestamp": "2024-12-28T10:00:00Z",
  "uptime_seconds": 3600.0,
  "queries": {
    "total_processed": 1250,
    "errors": 12,
    "success_rate": 99.04
  },
  "response_times": {
    "average_total_ms": 450.5,
    "average_retrieval_ms": 135.2,
    "average_llm_ms": 225.3,
    "average_synthesis_ms": 90.0,
    "breakdown": {
      "retrieval_percent": 30.0,
      "llm_percent": 50.0,
      "synthesis_percent": 20.0
    }
  },
  "cache_performance": {
    "query_cache": {
      "hits": 850,
      "misses": 400,
      "total_requests": 1250,
      "hit_ratio": 0.68
    },
    "retrieval_cache": {
      "hits": 600,
      "misses": 650,
      "total_requests": 1250,
      "hit_ratio": 0.48
    },
    "llm_cache": {
      "hits": 200,
      "misses": 1050,
      "total_requests": 1250,
      "hit_ratio": 0.16
    }
  },
  "llm_providers": {
    "usage_counts": {
      "ollama": 500,
      "huggingface": 300,
      "openai": 400,
      "anthropic": 50
    },
    "usage_percentages": {
      "ollama": 40.0,
      "huggingface": 24.0,
      "openai": 32.0,
      "anthropic": 4.0
    }
  },
  "health_status": {
    "postgresql": {
      "status": "healthy",
      "response_time_ms": 15.2,
      "error": null,
      "details": {}
    },
    "meilisearch": {
      "status": "healthy",
      "response_time_ms": 25.8,
      "error": null,
      "details": {}
    }
  },
  "system_metrics": {
    "system": {
      "cpu_percent": 45.2,
      "memory_percent": 68.5,
      "disk_percent": 23.1
    }
  }
}
```

**Prometheus Response Example:**
```
# HELP queries_total Total number of queries processed
# TYPE queries_total counter
queries_total 1250

# HELP errors_total Total number of errors
# TYPE errors_total counter
errors_total 12

# HELP response_time_seconds Average response time
# TYPE response_time_seconds gauge
response_time_seconds 0.4505

# HELP query_cache_hits_total Total cache hits
# TYPE query_cache_hits_total counter
query_cache_hits_total 850

# HELP query_cache_misses_total Total cache misses
# TYPE query_cache_misses_total counter
query_cache_misses_total 400

# HELP query_cache_hit_ratio Cache hit ratio
# TYPE query_cache_hit_ratio gauge
query_cache_hit_ratio 0.68

# HELP llm_provider_usage_total Usage count by provider
# TYPE llm_provider_usage_total counter
llm_provider_usage_total{provider="ollama"} 500
llm_provider_usage_total{provider="huggingface"} 300
llm_provider_usage_total{provider="openai"} 400
llm_provider_usage_total{provider="anthropic"} 50

# HELP component_health Component health status
# TYPE component_health gauge
component_health{component="postgresql"} 1
component_health{component="meilisearch"} 1

# HELP component_response_time_ms Component response time
# TYPE component_response_time_ms gauge
component_response_time_ms{component="postgresql"} 15.2
component_response_time_ms{component="meilisearch"} 25.8
```

### GET `/health`

Returns comprehensive system health status for all components.

**Response Example:**
```json
{
  "timestamp": "2024-12-28T10:00:00Z",
  "overall_status": "healthy",
  "api_gateway": {
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2024-12-28T10:00:00Z"
  },
  "environment": "development",
  "uptime_seconds": 3600.0,
  "components": {
    "postgresql": {
      "status": "healthy",
      "response_time_ms": 15.2,
      "error": null,
      "details": {
        "connection_string": "localhost:5432"
      }
    },
    "meilisearch": {
      "status": "healthy",
      "response_time_ms": 25.8,
      "error": null,
      "details": {
        "status": "available"
      }
    },
    "vector_retrieval": {
      "status": "healthy",
      "response_time_ms": 45.3,
      "error": null,
      "details": {
        "vector_db_url": "http://localhost:6333"
      }
    },
    "llm_ollama": {
      "status": "healthy",
      "response_time_ms": 120.5,
      "error": null,
      "details": {
        "models_available": 3
      }
    },
    "llm_huggingface": {
      "status": "healthy",
      "response_time_ms": 85.2,
      "error": null,
      "details": {
        "model_status": "available"
      }
    },
    "llm_openai": {
      "status": "healthy",
      "response_time_ms": 95.8,
      "error": null,
      "details": {
        "models_available": 15
      }
    },
    "factchecker": {
      "status": "healthy",
      "response_time_ms": 35.1,
      "error": null,
      "details": {
        "validation_logic": "operational",
        "test_claim": "The Earth is round",
        "test_sources": ["NASA", "Scientific American"]
      }
    }
  },
  "summary": {
    "total_components": 7,
    "healthy_components": 7,
    "degraded_components": 0,
    "unhealthy_components": 0,
    "unknown_components": 0
  }
}
```

## Metrics Collection

### Recording Query Metrics

```python
from shared.core.metrics_collector import (
    record_query_metrics, ResponseTimeBreakdown, LLMProvider
)

# Create response time breakdown
response_breakdown = ResponseTimeBreakdown(
    retrieval_time_ms=150.0,
    llm_time_ms=300.0,
    synthesis_time_ms=100.0,
    total_time_ms=550.0
)

# Record cache hits/misses
cache_hits = {
    "query_cache": False,
    "retrieval_cache": True,
    "llm_cache": False
}

# Record metrics
await record_query_metrics(
    response_time_breakdown=response_breakdown,
    provider=LLMProvider.OLLAMA,
    cache_hits=cache_hits
)
```

### Recording Error Metrics

```python
from shared.core.metrics_collector import record_error_metrics

# Record different types of errors
await record_error_metrics("timeout_error")
await record_error_metrics("rate_limit_exceeded")
await record_error_metrics("database_connection_failed")
```

### Recording Health Check Metrics

```python
from shared.core.metrics_collector import record_health_check, ComponentStatus

await record_health_check(
    component="postgresql",
    status=ComponentStatus.HEALTHY,
    response_time_ms=15.2,
    details={"connection_string": "localhost:5432"}
)
```

## Health Checks

### Running Comprehensive Health Checks

```python
from shared.core.health_checker import HealthChecker

async def check_system_health():
    health_checker = HealthChecker()
    health_status = await health_checker.run_comprehensive_health_check()
    
    print(f"Overall Status: {health_status['overall_status']}")
    print(f"Healthy Components: {health_status['summary']['healthy_components']}")
    print(f"Unhealthy Components: {health_status['summary']['unhealthy_components']}")
    
    return health_status
```

### Individual Component Health Checks

```python
from shared.core.health_checker import HealthChecker

async def check_specific_components():
    health_checker = HealthChecker()
    
    # Check database
    db_health = await health_checker.check_database_connection()
    print(f"Database: {db_health.status.value}")
    
    # Check Meilisearch
    search_health = await health_checker.check_meilisearch_health()
    print(f"Meilisearch: {search_health.status.value}")
    
    # Check LLM APIs
    ollama_health = await health_checker.check_llm_api_health(LLMProvider.OLLAMA)
    print(f"Ollama: {ollama_health.status.value}")
```

## Deployment with Monitoring

### Prometheus Configuration

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'universal-knowledge-platform'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    params:
      format: ['prometheus']
    scrape_interval: 15s
    scrape_timeout: 10s
```

### Grafana Dashboard

Create a dashboard with the following panels:

1. **Query Processing**
   - Total queries processed
   - Success rate
   - Average response time

2. **Response Time Breakdown**
   - Retrieval time
   - LLM time
   - Synthesis time

3. **Cache Performance**
   - Hit ratios for each cache
   - Cache hit/miss counts

4. **LLM Provider Usage**
   - Usage counts by provider
   - Usage percentages

5. **System Health**
   - Component health status
   - Component response times

6. **Error Tracking**
   - Error counts by type
   - Error rates over time

### Alerting Rules

```yaml
groups:
  - name: universal-knowledge-platform
    rules:
      - alert: HighErrorRate
        expr: rate(errors_total[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          
      - alert: SlowResponseTime
        expr: response_time_seconds > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow response times detected"
          
      - alert: ComponentUnhealthy
        expr: component_health == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Component is unhealthy"
          
      - alert: LowCacheHitRate
        expr: query_cache_hit_ratio < 0.5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low cache hit rate"
```

## Testing

### Running Tests

```bash
# Run all metrics and monitoring tests
pytest tests/test_metrics_monitoring.py -v

# Run specific test classes
pytest tests/test_metrics_monitoring.py::TestMetricsCollector -v
pytest tests/test_metrics_monitoring.py::TestHealthChecker -v
pytest tests/test_metrics_monitoring.py::TestAPIEndpoints -v
```

### Demo Script

```bash
# Run the demo script
python demo_metrics_monitoring.py
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/sarvanom_db

# Search Engine
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_MASTER_KEY=your-meilisearch-master-key

# Vector Database
VECTOR_DB_URL=http://localhost:6333

# LLM Providers
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
HUGGINGFACE_API_KEY=your-huggingface-api-key
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### Health Check Configuration

```python
from shared.core.health_checker import HealthCheckConfig

config = HealthCheckConfig(
    timeout_seconds=5.0,
    retry_attempts=2,
    critical_threshold_ms=1000.0,
    warning_threshold_ms=500.0
)
```

## Best Practices

### 1. Metrics Collection
- Record metrics at every pipeline stage
- Use consistent naming for cache keys
- Track both successful and failed operations
- Include context in error metrics

### 2. Health Checks
- Run health checks regularly (every 30-60 seconds)
- Set appropriate timeouts for external services
- Implement circuit breakers for failing components
- Log health check results for debugging

### 3. Monitoring
- Set up alerts for critical metrics
- Use dashboards for real-time visibility
- Monitor trends over time
- Set up automated scaling based on metrics

### 4. Performance
- Use rolling averages for response times
- Implement metrics batching for high-volume scenarios
- Consider metrics sampling for very high throughput
- Monitor memory usage of metrics collection

## Troubleshooting

### Common Issues

1. **Metrics Not Updating**
   - Check that metrics collector is properly initialized
   - Verify async/await usage in metrics recording
   - Check for exceptions in metrics recording

2. **Health Checks Failing**
   - Verify service URLs and credentials
   - Check network connectivity
   - Review timeout configurations
   - Check service-specific error messages

3. **High Memory Usage**
   - Monitor metrics collector memory usage
   - Consider reducing rolling window sizes
   - Implement metrics cleanup for long-running processes

4. **Prometheus Integration Issues**
   - Verify endpoint accessibility
   - Check content-type headers
   - Ensure proper metric naming conventions
   - Validate Prometheus configuration

### Debug Commands

```python
# Reset all metrics
from shared.core.metrics_collector import reset_all_metrics
reset_all_metrics()

# Get current metrics
from shared.core.metrics_collector import get_metrics_summary
metrics = get_metrics_summary()
print(json.dumps(metrics, indent=2))

# Test health checker
from shared.core.health_checker import HealthChecker
health_checker = HealthChecker()
health_status = await health_checker.run_comprehensive_health_check()
print(json.dumps(health_status, indent=2))
```

## API Reference

### MetricsCollector

Singleton class for collecting and managing platform metrics.

**Methods:**
- `increment_query_counter()`: Increment total query counter
- `increment_error_counter(error_type)`: Increment error counter
- `record_provider_usage(provider)`: Record LLM provider usage
- `record_response_time(breakdown)`: Record response time breakdown
- `record_cache_hit(cache_name)`: Record cache hit
- `record_cache_miss(cache_name)`: Record cache miss
- `update_health_result(result)`: Update health check result
- `get_metrics_dict()`: Get comprehensive metrics as dictionary
- `get_prometheus_metrics()`: Get Prometheus-formatted metrics
- `reset_metrics()`: Reset all metrics

### HealthChecker

Comprehensive health checker for all platform components.

**Methods:**
- `check_database_connection()`: Check database health
- `check_meilisearch_health()`: Check Meilisearch health
- `check_vector_retrieval_health()`: Check vector retrieval health
- `check_llm_api_health(provider)`: Check LLM API health
- `check_factchecker_health()`: Check FactChecker health
- `run_comprehensive_health_check()`: Run all health checks

### Data Classes

- `ResponseTimeBreakdown`: Response time breakdown by component
- `CacheMetrics`: Cache performance metrics
- `HealthCheckResult`: Health check result for a component
- `LLMProvider`: Enum for LLM providers
- `ComponentStatus`: Enum for component health status

## Contributing

When adding new metrics or health checks:

1. **Metrics**: Add to `MetricsCollector` with appropriate methods
2. **Health Checks**: Add to `HealthChecker` with proper error handling
3. **Tests**: Add comprehensive tests in `test_metrics_monitoring.py`
4. **Documentation**: Update this guide with new features
5. **API**: Update API endpoints if needed

## License

This metrics and monitoring system is part of the Universal Knowledge Platform and follows the same licensing terms. 