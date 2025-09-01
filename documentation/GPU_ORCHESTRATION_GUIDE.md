# SarvanOM GPU Orchestration Guide

## Overview

SarvanOM's GPU orchestration system provides **free GPU access** with zero-budget optimization, following MAANG-style industry standards. The system intelligently routes LLM requests through multiple providers, prioritizing free options while maintaining high availability.

## 🎯 Key Features

- **Free GPU Prioritization**: Always uses free providers first
- **Circuit Breaker Pattern**: 3 failures → skip provider for 5 minutes
- **Health Monitoring**: Real-time provider status and latency tracking
- **Automatic Fallback**: Never fails - always returns a response
- **Timeout Protection**: 15-second timeout per request
- **Zero Budget First**: Prioritizes free providers over paid APIs

## 🏗️ Architecture

### Provider Hierarchy

1. **ollama_local** - Local CPU quantized models (free)
2. **remote_gpu** - Remote GPU via Colab/Kaggle/HF Space (free)
3. **huggingface** - HuggingFace free tier API
4. **openai** - Paid API (only if ENABLE_PAID_API=true)
5. **anthropic** - Paid API (only if ENABLE_PAID_API=true)
6. **local_stub** - Fallback stub response (always available)

### Core Components

```
services/gateway/providers/gpu_providers.py
├── BaseGPUProvider (abstract base class)
├── LocalOllamaProvider (CPU quantized)
├── RemoteGPUProvider (Colab/Kaggle/HF Space)
├── HuggingFaceProvider (free tier)
├── OpenAIProvider (paid)
├── AnthropicProvider (paid)
├── LocalStubProvider (fallback)
└── GPUProviderOrchestrator (main orchestrator)
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Required for local Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Optional: Remote GPU via ngrok
GPU_REMOTE_URL=https://your-ngrok-url.ngrok.io

# Optional: HuggingFace free tier
HUGGINGFACE_API_KEY=hf_...

# Optional: Paid APIs (only if ENABLE_PAID_API=true)
ENABLE_PAID_API=false
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Timeout configuration
LLM_TIMEOUT_SECONDS=15
```

### 2. Basic Usage

```python
from services.gateway.providers.gpu_providers import (
    gpu_orchestrator,
    LLMRequest
)

# Simple request
request = LLMRequest(
    prompt="What is the capital of France?",
    max_tokens=100,
    temperature=0.2
)

response = await gpu_orchestrator.complete_request(request)

if response.success:
    print(f"Provider: {response.provider.value}")
    print(f"Response: {response.content}")
else:
    print(f"Error: {response.error_message}")
```

### 3. Health Monitoring

```python
# Check provider health
health_status = await gpu_orchestrator.get_provider_health()

for provider_name, health in health_status.items():
    print(f"{provider_name}: {health.status.value}")
    print(f"  Latency: {health.latency_ms}ms")
    print(f"  Errors: {health.error_count}")
```

## 🔧 Configuration Scenarios

### Zero Budget Mode (Recommended)

```bash
# Only free providers
ENABLE_PAID_API=false
GPU_REMOTE_URL=https://your-colab-ngrok.ngrok.io
HUGGINGFACE_API_KEY=hf_...
```

**Provider Order**: `ollama_local` → `remote_gpu` → `huggingface` → `local_stub`

### Local Only (No Internet)

```bash
# Only local Ollama
OLLAMA_BASE_URL=http://localhost:11434
ENABLE_PAID_API=false
```

**Provider Order**: `ollama_local` → `local_stub`

### Remote GPU Only

```bash
# Use Colab/Kaggle GPU
GPU_REMOTE_URL=https://your-ngrok-url.ngrok.io
ENABLE_PAID_API=false
```

**Provider Order**: `remote_gpu` → `local_stub`

### Full Stack (All Providers)

```bash
# All providers including paid
ENABLE_PAID_API=true
GPU_REMOTE_URL=https://your-ngrok-url.ngrok.io
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

**Provider Order**: `ollama_local` → `remote_gpu` → `huggingface` → `openai` → `anthropic` → `local_stub`

## 🏥 Health Endpoints

### GPU Providers Health

```bash
curl http://localhost:8000/health/gpu-providers
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "gpu_providers": {
    "providers": {
      "ollama_local": {
        "status": "healthy",
        "last_check": "2024-01-15T10:29:55Z",
        "latency_ms": 45.2,
        "error_count": 0,
        "success_count": 15,
        "circuit_open_until": null,
        "last_error": null
      },
      "remote_gpu": {
        "status": "circuit_open",
        "last_check": "2024-01-15T10:25:00Z",
        "latency_ms": 0,
        "error_count": 3,
        "success_count": 5,
        "circuit_open_until": "2024-01-15T10:30:00Z",
        "last_error": "Connection timeout"
      }
    },
    "available_providers": ["ollama_local", "huggingface", "local_stub"]
  }
}
```

## 🔌 Circuit Breaker

The circuit breaker pattern protects against failing providers:

- **Threshold**: 3 consecutive failures
- **Timeout**: 5 minutes
- **Recovery**: Automatic after timeout
- **Monitoring**: Real-time status via health endpoints

### Circuit Breaker States

1. **CLOSED**: Provider is healthy and accepting requests
2. **OPEN**: Provider is failing, requests are rejected
3. **HALF_OPEN**: Testing if provider has recovered

## 🧪 Testing

### Run Test Suite

```bash
# Test the GPU orchestration system
python scripts/test_gpu_orchestration.py
```

### Run Demo

```bash
# See the system in action
python scripts/demo_gpu_orchestration.py
```

### Manual Testing

```bash
# Test health endpoint
curl http://localhost:8000/health/gpu-providers

# Test with different configurations
export ENABLE_PAID_API=false
export GPU_REMOTE_URL=https://your-ngrok-url.ngrok.io
python scripts/test_gpu_orchestration.py
```

## 🎯 Provider Details

### LocalOllamaProvider

- **Type**: Local CPU quantized models
- **Cost**: Free
- **Requirements**: Ollama running locally
- **Models**: deepseek-r1:8b (default)
- **Health Check**: `GET /api/tags`

### RemoteGPUProvider

- **Type**: Remote GPU via ngrok tunnel
- **Cost**: Free (Colab/Kaggle/HF Space)
- **Requirements**: GPU_REMOTE_URL environment variable
- **Health Check**: `GET /health`
- **Setup**: See [Remote GPU Setup Guide](#remote-gpu-setup)

### HuggingFaceProvider

- **Type**: HuggingFace free tier API
- **Cost**: Free (with rate limits)
- **Requirements**: HUGGINGFACE_API_KEY
- **Models**: distilgpt2 (default)
- **Health Check**: API endpoint availability

### OpenAIProvider

- **Type**: OpenAI paid API
- **Cost**: Per token
- **Requirements**: ENABLE_PAID_API=true, OPENAI_API_KEY
- **Models**: gpt-4o-mini (cost-efficient)
- **Health Check**: Models list API

### AnthropicProvider

- **Type**: Anthropic paid API
- **Cost**: Per token
- **Requirements**: ENABLE_PAID_API=true, ANTHROPIC_API_KEY
- **Models**: claude-3-5-haiku-20241022 (cost-efficient)
- **Health Check**: API availability

### LocalStubProvider

- **Type**: Fallback stub response
- **Cost**: Free
- **Requirements**: None
- **Always Available**: Yes
- **Use Case**: When all other providers fail

## 🌐 Remote GPU Setup

### Google Colab Setup

1. **Create Colab Notebook**:
```python
!pip install fastapi uvicorn
!pip install transformers torch

from fastapi import FastAPI
import uvicorn
from transformers import pipeline

app = FastAPI()

# Load model
generator = pipeline('text-generation', model='gpt2')

@app.get("/health")
async def health():
    return {"status": "healthy", "model": "gpt2"}

@app.post("/generate")
async def generate(request: dict):
    prompt = request["prompt"]
    result = generator(prompt, max_length=100, num_return_sequences=1)
    return {"content": result[0]["generated_text"]}

# Run with ngrok
!pip install pyngrok
from pyngrok import ngrok

public_url = ngrok.connect(8000)
print(f"Public URL: {public_url}")

uvicorn.run(app, host="0.0.0.0", port=8000)
```

2. **Set Environment Variable**:
```bash
export GPU_REMOTE_URL=https://your-ngrok-url.ngrok.io
```

### Kaggle Setup

Similar to Colab but with Kaggle's free GPU tier.

### HuggingFace Spaces Setup

1. **Create Space** with FastAPI
2. **Deploy** with GPU runtime
3. **Set GPU_REMOTE_URL** to space URL

## 📊 Monitoring and Metrics

### Health Metrics

- **Provider Status**: healthy/unhealthy/circuit_open
- **Latency**: Response time in milliseconds
- **Error Count**: Consecutive failures
- **Success Count**: Successful requests
- **Circuit Breaker**: Open/closed status

### Logging

Structured logging with trace IDs:

```python
logger.info("Request completed", extra={
    "provider": "ollama_local",
    "latency_ms": 45.2,
    "trace_id": "uuid-here"
})
```

### Performance Monitoring

- **Response Time**: Per provider
- **Success Rate**: Per provider
- **Circuit Breaker Events**: When providers fail
- **Fallback Usage**: When stub provider is used

## 🔒 Security Considerations

### API Key Management

- Store API keys in environment variables
- Never commit keys to version control
- Use `.env` files for local development
- Rotate keys regularly

### Network Security

- Use HTTPS for remote GPU connections
- Validate ngrok URLs
- Monitor for suspicious activity
- Rate limit requests

### Data Privacy

- No data is stored permanently
- Requests are processed in memory
- Consider data residency requirements
- Audit provider data handling

## 🚨 Troubleshooting

### Common Issues

1. **Ollama Not Running**
   ```
   Error: Connection refused
   Solution: Start Ollama with `ollama serve`
   ```

2. **Remote GPU Unavailable**
   ```
   Error: GPU_REMOTE_URL not set
   Solution: Set environment variable or use local providers
   ```

3. **Circuit Breaker Open**
   ```
   Status: circuit_open
   Solution: Wait 5 minutes or check provider health
   ```

4. **API Key Issues**
   ```
   Error: Invalid API key
   Solution: Check environment variables and key validity
   ```

### Debug Commands

```bash
# Check provider health
curl http://localhost:8000/health/gpu-providers

# Test specific provider
python -c "
import asyncio
from services.gateway.providers.gpu_providers import gpu_orchestrator
health = asyncio.run(gpu_orchestrator.get_provider_health())
print(health)
"

# Check environment
env | grep -E "(GPU|OLLAMA|ENABLE_PAID|API_KEY)"
```

## 📈 Performance Optimization

### Provider Selection

- **Simple Queries**: Use local Ollama
- **Complex Queries**: Use remote GPU
- **High Volume**: Use HuggingFace free tier
- **Critical Tasks**: Use paid APIs

### Caching

- Cache responses for repeated queries
- Use Redis for distributed caching
- Implement TTL for cache entries

### Load Balancing

- Distribute requests across providers
- Monitor provider load
- Implement request queuing

## 🔄 Integration with Existing Code

### Legacy Integration

The system integrates seamlessly with existing `real_llm_integration.py`:

```python
# Old way
response = await real_llm_processor.call_llm_with_provider_gating(prompt)

# New way (same interface, better orchestration)
response = await real_llm_processor.call_llm_with_provider_gating(prompt)
```

### API Integration

```python
# Health endpoint
GET /health/gpu-providers

# LLM endpoint (existing)
POST /api/query
{
  "prompt": "Your question here",
  "max_tokens": 100
}
```

## 🎯 Best Practices

1. **Start with Zero Budget**: Use free providers first
2. **Monitor Health**: Check provider status regularly
3. **Handle Failures**: Implement proper error handling
4. **Optimize Costs**: Use appropriate providers for tasks
5. **Test Thoroughly**: Validate all provider configurations
6. **Document Changes**: Keep configuration documentation updated

## 📚 Additional Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [HuggingFace API](https://huggingface.co/docs/api-inference)
- [Google Colab](https://colab.research.google.com/)
- [ngrok Documentation](https://ngrok.com/docs)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)

---

**Last Updated**: January 2025  
**Version**: 1.0.0  
**Maintainer**: SarvanOM Team
