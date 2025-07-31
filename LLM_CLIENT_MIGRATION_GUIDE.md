# LLM Client Migration Guide

## Overview

This guide helps you migrate from the old LLM client implementations to the new **LLM Client v3** with the latest SDKs, comprehensive error handling, and production-ready features.

## What's New in v3

### 🚀 Latest SDK Versions
- **OpenAI**: Updated to `openai>=1.50.0` (latest API patterns)
- **Anthropic**: Updated to `anthropic>=0.25.0` (latest Claude models)
- **Async-first**: All operations are now async for better performance
- **Type Safety**: Full type hints and validation

### 🛡️ Robust Error Handling
- **Automatic retry logic** with exponential backoff
- **Fallback mechanisms** between providers
- **Rate limiting** with configurable limits
- **Comprehensive error types** with detailed information

### 📊 Monitoring & Metrics
- **Performance metrics** (response times, token usage, costs)
- **Health checks** for all providers
- **Real-time monitoring** capabilities
- **Cost estimation** for all requests

### 🔄 Advanced Features
- **Streaming support** with proper error handling
- **Embedding generation** with fallback options
- **System message support** for better control
- **Concurrent request handling**

## Migration Steps

### 1. Update Dependencies

Update your `pyproject.toml` or `requirements.txt`:

```toml
# Latest LLM SDKs
openai>=1.50.0
anthropic>=0.25.0

# Additional dependencies for v3
tenacity>=8.2.0
structlog>=24.1.0
aiohttp>=3.10.0
```

### 2. Import the New Client

**Old way:**
```python
from shared.core.llm_client import LLMClient

client = LLMClient()
response = client.generate_text("Hello world")
```

**New way:**
```python
from shared.core.llm_client_v3 import get_llm_client_v3, LLMRequest

client = get_llm_client_v3()
request = LLMRequest(prompt="Hello world")
response = await client.generate_text(request)
print(response.content)
```

### 3. Update Environment Variables

**Old environment variables:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key
OPENAI_LLM_MODEL=gpt-3.5-turbo
ANTHROPIC_API_KEY=your-key
ANTHROPIC_MODEL=claude-3-opus-20240229
```

**New environment variables:**
```bash
# OpenAI
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4
OPENAI_BASE_URL=https://api.openai.com/v1  # Optional
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Anthropic
ANTHROPIC_API_KEY=your-key
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Advanced settings
LLM_REQUESTS_PER_MINUTE=60
LLM_TOKENS_PER_MINUTE=10000
LLM_ENABLE_FALLBACK=true
LLM_ENABLE_METRICS=true
```

### 4. Update Code Patterns

#### Text Generation

**Old way:**
```python
from shared.core.llm_client import LLMClient

client = LLMClient()
response = client.generate_text(
    prompt="Explain quantum computing",
    max_tokens=500,
    temperature=0.2
)
print(response)
```

**New way:**
```python
from shared.core.llm_client_v3 import get_llm_client_v3, LLMRequest

client = get_llm_client_v3()
request = LLMRequest(
    prompt="Explain quantum computing",
    max_tokens=500,
    temperature=0.2,
    system_message="You are a helpful AI assistant."
)
response = await client.generate_text(request)
print(response.content)
print(f"Tokens used: {response.token_usage['total_tokens']}")
print(f"Response time: {response.response_time_ms}ms")
```

#### Streaming

**Old way:**
```python
# Not supported in old client
```

**New way:**
```python
from shared.core.llm_client_v3 import get_llm_client_v3, LLMRequest

client = get_llm_client_v3()
request = LLMRequest(
    prompt="Write a story about a robot",
    max_tokens=200,
    stream=True
)

async for chunk in client.generate_stream(request):
    print(chunk, end="", flush=True)
```

#### Embeddings

**Old way:**
```python
from shared.core.llm_client import LLMClient

client = LLMClient()
embedding = client.create_embedding("Hello world")
```

**New way:**
```python
from shared.core.llm_client_v3 import get_llm_client_v3

client = get_llm_client_v3()
embedding = await client.create_embedding("Hello world")
print(f"Embedding dimension: {len(embedding)}")
```

### 5. Advanced Configuration

#### Multiple Providers with Fallback

```python
from shared.core.llm_client_v3 import (
    EnhancedLLMClientV3, 
    LLMConfig, 
    LLMProvider
)

configs = [
    LLMConfig(
        provider=LLMProvider.OPENAI,
        model="gpt-4",
        api_key="your-openai-key",
        requests_per_minute=60
    ),
    LLMConfig(
        provider=LLMProvider.ANTHROPIC,
        model="claude-3-5-sonnet-20241022",
        api_key="your-anthropic-key",
        requests_per_minute=60
    )
]

client = EnhancedLLMClientV3(configs)
```

#### Custom Rate Limiting

```python
config = LLMConfig(
    provider=LLMProvider.OPENAI,
    model="gpt-4",
    api_key="your-key",
    requests_per_minute=30,  # Custom rate limit
    tokens_per_minute=5000,  # Token rate limit
    enable_rate_limiting=True
)
```

### 6. Error Handling

**Old way:**
```python
try:
    response = client.generate_text(prompt)
except Exception as e:
    print(f"Error: {e}")
```

**New way:**
```python
from shared.core.llm_client_v3 import LLMError

try:
    response = await client.generate_text(request)
except LLMError as e:
    print(f"LLM Error: {e.error_type}")
    print(f"Message: {e.message}")
    print(f"Provider: {e.provider}")
    print(f"Retryable: {e.retryable}")
```

### 7. Monitoring and Metrics

```python
# Get client metrics
metrics = client.get_metrics()
print(f"Total requests: {metrics['total_requests']}")
print(f"Success rate: {metrics['successful_requests'] / metrics['total_requests']}")
print(f"Average response time: {metrics['avg_response_time_ms']}ms")
print(f"Total cost: ${metrics['total_cost']:.4f}")

# Health check
health_status = await client.health_check()
for provider_name, status in health_status.items():
    print(f"{provider_name}: {'✅' if status['healthy'] else '❌'}")
```

## Backward Compatibility

The old `LLMClient` class is still available for backward compatibility:

```python
from shared.core.llm_client import LLMClient

# This still works but uses the new v3 client under the hood
client = LLMClient()
response = client.generate_text("Hello world")
```

## Testing

### Unit Tests

```python
# Run unit tests
pytest tests/unit/test_llm_client_v3.py -v
```

### Integration Tests

```python
# Run integration tests (requires API keys)
pytest tests/integration/test_llm_client_v3_integration.py -v
```

### Performance Tests

```python
# Test with load
python -m pytest tests/integration/test_llm_client_v3_integration.py::TestLLMClientV3Integration::test_concurrent_requests -v
```

## Best Practices

### 1. Use Async/Await

```python
# ✅ Good
async def process_query(query: str):
    client = get_llm_client_v3()
    request = LLMRequest(prompt=query)
    response = await client.generate_text(request)
    return response.content

# ❌ Avoid
def process_query_sync(query: str):
    client = get_llm_client_v3()
    request = LLMRequest(prompt=query)
    # This blocks the event loop
    response = asyncio.run(client.generate_text(request))
    return response.content
```

### 2. Handle Errors Gracefully

```python
async def safe_generate_text(prompt: str) -> str:
    try:
        client = get_llm_client_v3()
        request = LLMRequest(prompt=prompt)
        response = await client.generate_text(request)
        return response.content
    except LLMError as e:
        if e.retryable:
            # Implement custom retry logic
            return await retry_with_backoff(prompt)
        else:
            # Log and return fallback
            logger.error(f"Non-retryable error: {e}")
            return "I'm sorry, I'm having trouble processing your request."
```

### 3. Monitor Performance

```python
async def monitored_generate_text(prompt: str):
    start_time = time.time()
    client = get_llm_client_v3()
    
    try:
        request = LLMRequest(prompt=prompt)
        response = await client.generate_text(request)
        
        # Log performance metrics
        logger.info(f"Request completed in {response.response_time_ms}ms")
        logger.info(f"Tokens used: {response.token_usage['total_tokens']}")
        
        return response.content
    except Exception as e:
        logger.error(f"Request failed after {time.time() - start_time:.2f}s")
        raise
```

### 4. Use System Messages

```python
request = LLMRequest(
    prompt="What is the capital of France?",
    system_message="You are a helpful geography tutor. Always provide accurate information.",
    max_tokens=100
)
```

### 5. Configure Rate Limiting

```python
config = LLMConfig(
    provider=LLMProvider.OPENAI,
    model="gpt-4",
    api_key="your-key",
    requests_per_minute=30,  # Conservative rate limit
    tokens_per_minute=5000,
    enable_rate_limiting=True
)
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:** `ModuleNotFoundError: No module named 'shared.core.llm_client_v3'`

**Solution:** Ensure the project root is in your Python path:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

#### 2. API Key Issues

**Problem:** `AuthenticationError` or `InvalidAPIKey`

**Solution:** Check your environment variables:
```bash
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
```

#### 3. Rate Limiting

**Problem:** Requests are taking too long or failing

**Solution:** Adjust rate limits:
```python
config = LLMConfig(
    provider=LLMProvider.OPENAI,
    model="gpt-4",
    api_key="your-key",
    requests_per_minute=10,  # Reduce rate limit
    tokens_per_minute=1000
)
```

#### 4. Async/Await Issues

**Problem:** `RuntimeError: no running event loop`

**Solution:** Ensure you're in an async context:
```python
async def main():
    client = get_llm_client_v3()
    response = await client.generate_text(request)

# Run with asyncio
asyncio.run(main())
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use structlog
import structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

## Migration Checklist

- [ ] Update dependencies in `pyproject.toml`
- [ ] Update imports to use `llm_client_v3`
- [ ] Convert synchronous calls to async/await
- [ ] Update environment variables
- [ ] Test with your existing code
- [ ] Update error handling
- [ ] Configure rate limiting
- [ ] Set up monitoring
- [ ] Run unit and integration tests
- [ ] Update documentation

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the test files for examples
3. Check the source code in `shared/core/llm_client_v3.py`
4. Run the test suite to verify your setup

## Version History

- **v3.0.0** (2024-12-28): Complete rewrite with latest SDKs, async support, comprehensive error handling, and monitoring
- **v2.0.0** (2024-12-28): Enhanced version with fallback mechanisms
- **v1.0.0**: Original implementation

---

**Note:** The old `LLMClient` class will continue to work but is deprecated. We recommend migrating to the new v3 client for better performance, reliability, and features. 