# Model Services - SarvanOM v2

This directory contains the core model management services for SarvanOM v2:

- **Model Registry**: Central catalog of all available LLM models
- **Model Router**: Routes queries to appropriate models based on intent and complexity
- **Auto-Upgrade**: Automatically discovers, evaluates, and deploys new stable models

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Model Router  │    │  Model Registry │    │  Auto-Upgrade   │
│   (Port 8001)   │◄──►│   (Port 8000)   │◄──►│   (Port 8002)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Query Router  │    │   Model Catalog │    │  Model Discovery│
│   Classification│    │   Health Monitor│    │   Evaluation    │
│   Fallback Chain│    │   Cost Tracking │    │   Deployment    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 **Quick Start**

### **Prerequisites**
- Docker and Docker Compose
- Python 3.11+
- Redis (included in docker-compose)

### **Start Services**
```bash
# Start all services
docker-compose up -d

# Check service health
curl http://localhost:8000/health  # Registry
curl http://localhost:8001/health  # Router
curl http://localhost:8002/health  # Auto-Upgrade
```

### **Run Tests**
```bash
# Install test dependencies
pip install -r requirements.txt

# Run comprehensive tests
python test_model_services.py
```

## 📋 **Service Details**

### **Model Registry Service (Port 8000)**

**Purpose**: Central catalog of all available LLM models, their capabilities, performance characteristics, and cost information.

**Key Features**:
- Model discovery and registration
- Capability mapping (text, multimodal, tool use, long context)
- Performance tracking (latency, quality, success rate)
- Cost management and optimization
- Provider health monitoring
- Prometheus metrics export

**API Endpoints**:
- `GET /models` - Get all models
- `GET /models/{model_id}` - Get specific model
- `GET /models/stable` - Get stable models only
- `GET /models/refiners` - Get refinement models (fast & cheap)
- `GET /models/capability/{capability}` - Get models by capability
- `GET /models/provider/{provider}` - Get models by provider
- `POST /models/{model_id}/usage` - Record model usage

### **Model Router Service (Port 8001)**

**Purpose**: Routes queries to appropriate models based on intent, capabilities, and performance requirements.

**Key Features**:
- Query classification (simple, technical, research, multimedia)
- Automatic model selection with fallback chains
- Cost-aware routing
- Refinement path for Guided Prompt Confirmation
- LMM auto-trigger for image/video content
- Budget enforcement (5/7/10s per complexity)

**API Endpoints**:
- `POST /route` - Route query to appropriate model
- `POST /route/refinement` - Route refinement query (≤500ms budget)
- `GET /classify` - Classify query type and complexity

**Model Selection Policy**:
- **Simple Queries**: GPT-3.5 Turbo → Claude 3.5 Sonnet → GPT-4o
- **Technical Queries**: Claude 3.5 Sonnet → GPT-4o → GPT-3.5 Turbo
- **Research Queries**: GPT-4o → Claude 3.5 Sonnet → GPT-3.5 Turbo
- **Multimedia Queries**: GPT-4o (only multimodal model)

### **Auto-Upgrade Service (Port 8002)**

**Purpose**: Automatically discovers, evaluates, and deploys new stable models while maintaining system reliability.

**Key Features**:
- Weekly model discovery from all providers
- Shadow evaluation with 1-5% traffic
- Canary deployment with 10-20% traffic
- Full rollout with 100% traffic
- Automatic rollback on performance regression
- Refiner model sweep for Guided Prompt optimization

**API Endpoints**:
- `GET /candidates` - Get discovered model candidates
- `GET /evaluations` - Get evaluation results
- `POST /start` - Start auto-upgrade service
- `POST /stop` - Stop auto-upgrade service
- `POST /discover` - Trigger manual discovery

**Upgrade Workflow**:
1. **Discovery**: Scan provider APIs for new stable models
2. **Shadow Eval**: Test with 1-5% traffic for 24-48 hours
3. **Canary**: Deploy to 10-20% traffic for 3-7 days
4. **Full Rollout**: Deploy to 100% traffic
5. **Rollback**: Automatic rollback on failure detection

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Registry Service
REDIS_HOST=redis
REDIS_PORT=6379

# Router Service
REGISTRY_URL=http://model-registry:8000

# Auto-Upgrade Service
REGISTRY_URL=http://model-registry:8000
```

### **Model Configuration**
Models are configured in the registry with the following schema:
```json
{
  "model_id": "gpt-4o-2024-08-06",
  "provider": "openai",
  "capabilities": {
    "text_generation": true,
    "multimodal": true,
    "tool_use": true,
    "long_context": true,
    "streaming": true,
    "function_calling": true,
    "fast_inference": false
  },
  "performance": {
    "avg_ttft_ms": 150,
    "avg_completion_ms": 2500,
    "success_rate": 0.98,
    "quality_score": 0.92
  },
  "costs": {
    "input_tokens_per_1k": 0.005,
    "output_tokens_per_1k": 0.015,
    "currency": "USD"
  }
}
```

## 📊 **Monitoring**

### **Prometheus Metrics**
- **Registry**: Port 8001 - Model usage, performance, health
- **Router**: Port 8002 - Routing decisions, selection time, fallbacks
- **Auto-Upgrade**: Port 8003 - Discovery runs, evaluations, deployments

### **Health Checks**
All services include health check endpoints:
- `GET /health` - Service health status
- Docker health checks configured
- Automatic restart on failure

## 🧪 **Testing**

### **Test Coverage**
- Unit tests for each service
- Integration tests between services
- End-to-end workflow testing
- Performance and latency testing
- Error handling and fallback testing

### **Test Scenarios**
- Model discovery and registration
- Query classification and routing
- Fallback chain execution
- Refinement query routing (≤500ms budget)
- Auto-upgrade workflow phases
- Performance regression detection

## 🔒 **Security**

### **Security Features**
- Input validation and sanitization
- Rate limiting and abuse protection
- Secure API key handling
- Provider authentication
- Audit logging for all operations

### **Privacy**
- No user data storage
- Model usage anonymization
- Cost tracking without PII
- Secure provider communication

## 🚀 **Deployment**

### **Production Deployment**
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale model-router=3

# Monitor logs
docker-compose logs -f model-registry
```

### **Kubernetes Deployment**
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -l app=model-services
```

## 📚 **API Documentation**

### **OpenAPI/Swagger**
- Registry: http://localhost:8000/docs
- Router: http://localhost:8001/docs
- Auto-Upgrade: http://localhost:8002/docs

### **API Examples**
```bash
# Route a simple query
curl -X POST http://localhost:8001/route \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the capital of France?"}'

# Route a refinement query
curl -X POST http://localhost:8001/route/refinement \
  -H "Content-Type: application/json" \
  -d '{"query": "show me apple", "refinement_type": "fast"}'

# Get stable models
curl http://localhost:8000/models/stable

# Trigger model discovery
curl -X POST http://localhost:8002/discover
```

## 🔄 **Integration**

### **With Other Services**
- **Gateway**: Uses router for model selection
- **Retrieval**: Uses registry for model capabilities
- **Synthesis**: Uses router for query routing
- **Guided Prompt**: Uses router refinement path

### **External Providers**
- OpenAI API integration
- Anthropic API integration
- Hugging Face API integration
- Ollama local models

---

**Status**: ✅ **IMPLEMENTED**  
**Version**: 2.0.0  
**Last Updated**: September 9, 2025