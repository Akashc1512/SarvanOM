# Unified Logging Configuration Guide

## Overview

The unified logging system provides centralized, structured logging for all backend services in the SarvanOM platform. It supports environment-based configuration, structured JSON logging, and comprehensive event tracking.

## Key Features

### ✅ Environment-Based Configuration
- **Development**: Text format, DEBUG level for easy reading
- **Production**: JSON format, INFO level for monitoring systems
- **Testing**: Configurable levels for test environments

### ✅ Structured Logging
- JSON format with timestamps, service metadata, and context
- Automatic sensitive data masking (passwords, tokens, keys)
- Request correlation with request IDs and user IDs

### ✅ FastAPI Integration
- Automatic request/response logging
- Startup and shutdown event logging
- Middleware integration for request tracking

### ✅ Agent Lifecycle Tracking
- Agent start/finish events
- Performance timing information
- Error handling with stack traces

## Environment Variables

Configure logging behavior through environment variables:

```bash
# Basic Configuration
LOG_LEVEL=INFO           # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json          # json or text
SERVICE_NAME=sarvanom    # Service identifier

# Advanced Configuration
LOG_FILE=/var/log/sarvanom/app.log  # Optional: Enable file logging
LOG_MAX_FILE_SIZE_MB=100            # Log file rotation size
LOG_BACKUP_COUNT=5                  # Number of backup files to keep
APP_ENV=production                  # Environment: development, production, testing
```

## Usage Examples

### Basic Service Setup

```python
from shared.core.unified_logging import setup_logging, get_logger

# Configure logging at application startup
logging_config = setup_logging(
    service_name="my-service",
    version="1.0.0"
)

# Get logger for your module
logger = get_logger(__name__)

# Log events
logger.info("Service started", component="startup")
logger.debug("Processing request", request_id="req-123", user_id="user-456")
```

### FastAPI Integration

```python
from fastapi import FastAPI
from shared.core.unified_logging import setup_fastapi_logging

app = FastAPI(title="My Service")

# Setup logging integration (automatic request logging)
setup_fastapi_logging(app, service_name="my-service")
```

### Agent Lifecycle Logging

```python
from shared.core.unified_logging import log_agent_lifecycle, log_execution_time

logger = get_logger(__name__)

# Log agent events
log_agent_lifecycle(logger, "retrieval_agent", "start", task_id="task-001")

# Time operations
with log_execution_time(logger, "data_processing", batch_id="batch-001"):
    # Your processing code here
    process_data()
```

### Query Event Logging

```python
from shared.core.unified_logging import log_query_event

# Log query processing events
log_query_event(logger, query_text, "received", query_id="q123", user_id="user456")
log_query_event(logger, query_text, "processing", agents=["retrieval", "synthesis"])
log_query_event(logger, query_text, "completed", response_length=1250, confidence=0.85)
```

## Log Formats

### Development (Text Format)
```
2025-08-06 10:04:47 - my-service - INFO - Query received
2025-08-06 10:04:47 - my-service - DEBUG - Processing user request
```

### Production (JSON Format)
```json
{
  "timestamp": "2025-08-06T04:34:47.169657+00:00",
  "level": "INFO",
  "logger": "my-service",
  "message": "Query received",
  "service": "sarvanom-api",
  "version": "1.0.0",
  "request_id": "req-123",
  "user_id": "user456",
  "query_id": "q123",
  "component": "query_processor"
}
```

## Integration with Existing Services

### API Gateway
- ✅ Configured in `services/api_gateway/main.py`
- ✅ FastAPI integration enabled
- ✅ Request/response logging

### Gateway Service
- ✅ Configured in `services/gateway/gateway_app.py`
- ✅ Service startup/shutdown logging

### Agent Orchestrator
- ✅ Updated in `shared/core/agent_orchestrator.py`
- ✅ Agent lifecycle events

## Security Features

### Automatic Data Masking
Sensitive fields are automatically masked in logs:
- `password`, `token`, `key`, `secret`, `auth`
- `api_key`, `jwt`, `bearer`, `authorization`
- `credential`

Example:
```python
logger.info("User login", user_id="123", password="secret123", email="user@example.com")
# Output: password will be "***MASKED***"
```

## Monitoring Integration

### Key Events Logged
- ✅ Service startup/shutdown
- ✅ HTTP requests/responses with timing
- ✅ Agent lifecycle (start/finish/error)
- ✅ Query processing flow
- ✅ Error conditions with stack traces
- ✅ Performance metrics

### Log Levels by Environment
- **Development**: DEBUG and above
- **Production**: INFO and above  
- **Testing**: WARNING and above (configurable)

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure `structlog` is installed
   ```bash
   pip install structlog
   ```

2. **Configuration Not Applied**: Verify environment variables are set
   ```bash
   echo $LOG_LEVEL
   echo $LOG_FORMAT
   ```

3. **Log File Not Created**: Check directory permissions
   ```bash
   mkdir -p /var/log/sarvanom
   chmod 755 /var/log/sarvanom
   ```

### Testing Configuration

Run the demo script to verify logging works:
```bash
python scripts/demo_logging.py
```

## Best Practices

### Do's
- ✅ Use structured logging with context
- ✅ Include request IDs for tracing
- ✅ Log key business events (queries, agent actions)
- ✅ Use appropriate log levels
- ✅ Include timing information for performance monitoring

### Don'ts
- ❌ Don't use `print()` statements in production code
- ❌ Don't log sensitive data without masking
- ❌ Don't log excessively in production (avoid DEBUG in production)
- ❌ Don't include user passwords or API keys in logs

## Performance Considerations

- JSON logging adds ~1-2ms per log entry
- File logging may impact performance in high-throughput scenarios
- Use INFO level or higher in production
- Consider log aggregation systems for high-volume applications

## Migration from Existing Logging

Replace existing logging calls:

```python
# Old way
import logging
logger = logging.getLogger(__name__)
logger.info("Query received")

# New way  
from shared.core.unified_logging import get_logger
logger = get_logger(__name__)
logger.info("Query received", component="query_processor", query_id="q123")
```

## Future Enhancements

- [ ] Integration with external monitoring systems (Datadog, New Relic)
- [ ] Log aggregation and search capabilities
- [ ] Automated log analysis and alerting
- [ ] Performance metrics collection
- [ ] Distributed tracing integration