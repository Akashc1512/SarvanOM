# Resilience System Documentation

## Overview

The SarvanOM Resilience System provides comprehensive fault tolerance and error handling capabilities to ensure the platform remains operational even under adverse conditions. This system implements enterprise-grade patterns for high availability and graceful degradation.

## Architecture

The resilience system consists of three main components:

1. **Circuit Breaker Pattern** - Prevents cascading failures
2. **Graceful Degradation** - Provides fallback responses when services fail
3. **Error Boundaries** - Catches and handles errors at different levels

## Components

### 1. Circuit Breaker System

The circuit breaker pattern prevents cascading failures by monitoring service health and temporarily disabling failing services.

#### Key Features

- **Per-provider monitoring** - Each LLM provider has its own circuit breaker
- **Configurable thresholds** - Failure count, recovery timeout, success threshold
- **Automatic recovery** - Services are automatically re-enabled after recovery
- **State management** - Closed (normal), Open (failing), Half-Open (testing)

#### Configuration

```python
from services.gateway.resilience.circuit_breaker import CircuitBreakerConfig

config = CircuitBreakerConfig(
    failure_threshold=5,        # Failures before opening circuit
    recovery_timeout=60,        # Seconds to wait before half-open
    success_threshold=3,        # Successes needed to close circuit
    timeout_threshold=30.0,     # Request timeout in seconds
    window_size=60,             # Time window for failure counting
    max_failures_per_window=10  # Max failures in window
)
```

#### Usage

```python
from services.gateway.resilience.circuit_breaker import CircuitBreakerManager

manager = CircuitBreakerManager()

# Get circuit breaker for a provider
circuit_breaker = manager.get_circuit_breaker("openai")

# Call with fallback through multiple providers
result, used_provider = await manager.call_with_fallback(
    providers=["openai", "anthropic", "ollama"],
    func=your_llm_function
)
```

#### States

- **CLOSED**: Normal operation, requests pass through
- **OPEN**: Circuit is open, requests are rejected immediately
- **HALF_OPEN**: Testing recovery, limited requests allowed

### 2. Graceful Degradation

The graceful degradation system provides intelligent fallback responses when LLM services are unavailable.

#### Key Features

- **Intelligent fallback generation** - Creates meaningful responses from available sources
- **Template-based responses** - Different templates for different query types
- **Source summarization** - Extracts key information from available sources
- **Trace ID inclusion** - Includes trace IDs for debugging

#### Degradation Levels

- **FULL**: All services operational
- **LLM_DEGRADED**: LLM services down, using fallback generation
- **RETRIEVAL_DEGRADED**: Retrieval services down, limited sources
- **EMERGENCY**: Critical failure, minimal response

#### Usage

```python
from services.gateway.resilience.graceful_degradation import GracefulDegradationManager

manager = GracefulDegradationManager()

# Generate fallback response
response = await manager.generate_fallback_response(
    query="How to fix React hydration error?",
    sources=available_sources,
    error_message="LLM service unavailable"
)

print(response.answer)  # Generated fallback answer
print(response.provider)  # "fallback_free_tier"
print(response.degradation_level)  # DegradationLevel.LLM_DEGRADED
```

#### Response Templates

The system uses different templates based on query type:

- **Technical queries**: Focus on code examples and technical details
- **General queries**: Provide overview and key points
- **Error scenarios**: Include troubleshooting steps

### 3. Error Boundaries

Error boundaries catch and handle errors at different levels of the application.

#### Key Features

- **LLM error handling** - Handles LLM service failures
- **Retrieval error handling** - Handles retrieval service failures
- **Trace ID propagation** - Includes trace IDs in error responses
- **Graceful error messages** - User-friendly error messages

#### Usage

```python
from services.gateway.resilience.graceful_degradation import ErrorBoundary

error_boundary = ErrorBoundary(degradation_manager)

# Handle LLM errors
response = await error_boundary.handle_llm_error(
    query="Test query",
    sources=available_sources,
    error=llm_error
)

# Handle retrieval errors
response = await error_boundary.handle_retrieval_error(
    query="Test query",
    error=retrieval_error
)
```

## Integration with Middleware

### Observability Integration

The resilience system integrates with the observability middleware to provide comprehensive monitoring:

```python
from services.gateway.middleware.observability import log_error, log_llm_call

# Circuit breaker logs failures
log_error("circuit_breaker_failure", f"Circuit breaker opened for {provider}")

# LLM calls are logged with success/failure status
log_llm_call(provider="openai", model="gpt-4", duration=1.5, success=True)
```

### Security Integration

The resilience system works with security middleware to ensure secure error handling:

- **Input validation** - All inputs are validated before processing
- **Rate limiting** - Prevents abuse during degraded states
- **Security headers** - Maintained even during errors

## API Endpoints

### Circuit Breaker Management

```http
GET /health/resilience
POST /resilience/reset-circuit-breakers
GET /resilience/circuit-breakers/{provider}
POST /resilience/circuit-breakers/{provider}/reset
```

### Health Check Response

```json
{
  "status": "healthy",
  "circuit_breakers": {
    "openai": {
      "state": "closed",
      "total_requests": 100,
      "failed_requests": 2,
      "success_rate": 0.98
    },
    "anthropic": {
      "state": "open",
      "total_requests": 50,
      "failed_requests": 10,
      "success_rate": 0.8
    }
  },
  "degradation_level": "full",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Configuration

### Environment Variables

```bash
# Circuit breaker configuration
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60
CIRCUIT_BREAKER_SUCCESS_THRESHOLD=3
CIRCUIT_BREAKER_TIMEOUT_THRESHOLD=30.0

# Degradation configuration
DEGRADATION_ENABLE_FALLBACK=true
DEGRADATION_INCLUDE_TRACE_IDS=true
DEGRADATION_LOG_LEVEL=INFO
```

### Configuration Files

```yaml
# config/development.yaml
resilience:
  circuit_breaker:
    failure_threshold: 5
    recovery_timeout: 60
    success_threshold: 3
    timeout_threshold: 30.0
    window_size: 60
    max_failures_per_window: 10
  
  degradation:
    enable_fallback: true
    include_trace_ids: true
    log_level: INFO
    templates:
      technical: "templates/technical_fallback.md"
      general: "templates/general_fallback.md"
      error: "templates/error_fallback.md"
```

## Testing

### Unit Tests

```bash
# Run resilience unit tests
pytest tests/integration/test_resilience.py -v

# Run observability and security tests
pytest tests/integration/test_observability_security.py -v
```

### Integration Tests

```bash
# Run comprehensive resilience test suite
python scripts/test_resilience.py
```

### Chaos Testing

The system includes chaos testing scenarios:

- **Provider failure** - All LLM providers fail
- **Network partition** - Network connectivity issues
- **High load** - Concurrent request handling
- **Memory pressure** - Resource constraints
- **Recovery test** - System recovery after failures

## Monitoring and Alerting

### Metrics

The resilience system exposes Prometheus metrics:

- `circuit_breaker_state` - Current state of each circuit breaker
- `circuit_breaker_requests_total` - Total requests per provider
- `circuit_breaker_failures_total` - Total failures per provider
- `degradation_level` - Current degradation level
- `fallback_responses_total` - Total fallback responses generated

### Alerts

Configure alerts for:

- Circuit breaker opening
- High failure rates
- Degradation level changes
- Recovery timeouts

### Dashboards

Create dashboards showing:

- Circuit breaker states
- Provider health
- Degradation levels
- Error rates
- Recovery times

## Best Practices

### Circuit Breaker Configuration

1. **Set appropriate thresholds** - Balance between responsiveness and stability
2. **Monitor recovery times** - Ensure services recover within expected timeframes
3. **Use different configs per provider** - Tailor to provider characteristics
4. **Test failure scenarios** - Regularly test circuit breaker behavior

### Degradation Strategy

1. **Maintain user experience** - Provide meaningful responses even during failures
2. **Include trace IDs** - Enable debugging and support
3. **Use appropriate templates** - Match response style to query type
4. **Monitor degradation levels** - Track system health over time

### Error Handling

1. **Catch specific exceptions** - Handle different error types appropriately
2. **Provide context** - Include relevant information in error messages
3. **Log comprehensively** - Ensure all errors are logged with context
4. **Test error scenarios** - Regularly test error handling paths

## Troubleshooting

### Common Issues

1. **Circuit breaker stuck open**
   - Check provider health
   - Verify recovery timeout configuration
   - Review failure patterns

2. **Degradation not working**
   - Verify fallback templates exist
   - Check source availability
   - Review error boundary configuration

3. **High error rates**
   - Monitor provider health
   - Review circuit breaker thresholds
   - Check network connectivity

### Debugging

1. **Enable debug logging**
   ```python
   import logging
   logging.getLogger('services.gateway.resilience').setLevel(logging.DEBUG)
   ```

2. **Check circuit breaker status**
   ```python
   status = manager.get_all_status()
   print(json.dumps(status, indent=2))
   ```

3. **Monitor degradation level**
   ```python
   level = await degradation_manager.check_system_health()
   print(f"Current degradation level: {level}")
   ```

## Performance Considerations

### Circuit Breaker Overhead

- Minimal overhead in normal operation
- Fast failure detection in degraded states
- Configurable timeouts to balance responsiveness

### Degradation Performance

- Template-based responses are fast
- Source summarization has minimal overhead
- Caching can improve response times

### Memory Usage

- Circuit breakers use minimal memory
- Degradation templates are loaded once
- Error boundaries have no persistent state

## Security Considerations

### Error Information Disclosure

- Avoid exposing sensitive information in error messages
- Use generic error messages for external users
- Include detailed information only in logs

### Rate Limiting

- Maintain rate limiting even during degraded states
- Prevent abuse of fallback responses
- Monitor for unusual patterns

### Input Validation

- Validate all inputs before processing
- Sanitize error messages
- Prevent injection attacks

## Future Enhancements

### Planned Features

1. **Adaptive thresholds** - Dynamic circuit breaker configuration
2. **Predictive degradation** - Proactive service health monitoring
3. **Advanced templates** - AI-generated fallback responses
4. **Distributed tracing** - Enhanced trace ID propagation

### Integration Opportunities

1. **Service mesh integration** - Istio/Linkerd circuit breakers
2. **Cloud provider integration** - AWS/Azure health checks
3. **Monitoring integration** - Grafana/Prometheus dashboards
4. **Alerting integration** - PagerDuty/Slack notifications

## Conclusion

The SarvanOM Resilience System provides enterprise-grade fault tolerance and error handling capabilities. By implementing circuit breakers, graceful degradation, and error boundaries, the system ensures high availability and excellent user experience even under adverse conditions.

The system is designed to be:

- **Reliable** - Handles failures gracefully
- **Observable** - Comprehensive monitoring and logging
- **Configurable** - Flexible configuration options
- **Testable** - Comprehensive test coverage
- **Maintainable** - Clear separation of concerns

This resilience system enables SarvanOM to provide a robust, trustworthy AI meta-search platform that users can depend on for their technical learning and development needs.
