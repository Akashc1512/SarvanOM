"""
Model Registry Service - SarvanOM v2

Central catalog of all available LLM models, their capabilities, performance characteristics, and cost information.
Enables automatic model selection, provider fallback, and cost-aware routing.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import redis
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
model_usage_counter = Counter('sarvanom_model_usage_total', 'Total model usage', ['model_id', 'provider', 'query_type'])
model_response_time = Histogram('sarvanom_model_response_time_seconds', 'Model response time', ['model_id', 'provider'])
model_quality_score = Gauge('sarvanom_model_quality_score', 'Model quality score', ['model_id', 'provider'])
model_cost_usd = Counter('sarvanom_model_cost_usd', 'Model cost in USD', ['model_id', 'provider'])
model_health_status = Gauge('sarvanom_model_health_status', 'Model health status', ['model_id', 'provider'])

class ModelStatus(str, Enum):
    STABLE = "stable"
    BETA = "beta"
    DEPRECATED = "deprecated"
    UNSTABLE = "unstable"

class ProviderStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"

@dataclass
class ModelCapabilities:
    text_generation: bool = False
    multimodal: bool = False
    tool_use: bool = False
    long_context: bool = False
    streaming: bool = False
    function_calling: bool = False
    fast_inference: bool = False

@dataclass
class ModelPerformance:
    avg_ttft_ms: float = 0.0
    avg_completion_ms: float = 0.0
    success_rate: float = 0.0
    quality_score: float = 0.0

@dataclass
class ModelCosts:
    input_tokens_per_1k: float = 0.0
    output_tokens_per_1k: float = 0.0
    currency: str = "USD"

@dataclass
class ModelLimits:
    max_context_tokens: int = 0
    max_output_tokens: int = 0
    rate_limit_rpm: int = 0
    rate_limit_tpm: int = 0

@dataclass
class ModelHealth:
    status: str = "healthy"
    last_check: str = ""
    uptime_percentage: float = 0.0
    error_rate: float = 0.0

@dataclass
class ModelMetadata:
    release_date: str = ""
    deprecation_date: Optional[str] = None
    recommended_for: List[str] = None
    not_recommended_for: List[str] = None

    def __post_init__(self):
        if self.recommended_for is None:
            self.recommended_for = []
        if self.not_recommended_for is None:
            self.not_recommended_for = []

@dataclass
class Model:
    model_id: str
    provider: str
    model_family: str
    version: str
    status: ModelStatus
    capabilities: ModelCapabilities
    performance: ModelPerformance
    costs: ModelCosts
    limits: ModelLimits
    health: ModelHealth
    metadata: ModelMetadata

@dataclass
class Provider:
    provider_id: str
    name: str
    status: ProviderStatus
    api_base_url: str
    authentication: Dict[str, Any]
    health: ModelHealth
    quotas: Dict[str, int]
    models: List[str]

class ModelRegistry:
    """Central model registry for tracking all available models"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.models: Dict[str, Model] = {}
        self.providers: Dict[str, Provider] = {}
        self._initialize_default_models()
        self._initialize_default_providers()
    
    def _initialize_default_models(self):
        """Initialize with default stable models"""
        default_models = [
            # OpenAI Models
            Model(
                model_id="gpt-4o-2024-08-06",
                provider="openai",
                model_family="gpt-4o",
                version="2024-08-06",
                status=ModelStatus.STABLE,
                capabilities=ModelCapabilities(
                    text_generation=True,
                    multimodal=True,
                    tool_use=True,
                    long_context=True,
                    streaming=True,
                    function_calling=True
                ),
                performance=ModelPerformance(
                    avg_ttft_ms=150,
                    avg_completion_ms=2500,
                    success_rate=0.98,
                    quality_score=0.92
                ),
                costs=ModelCosts(
                    input_tokens_per_1k=0.005,
                    output_tokens_per_1k=0.015,
                    currency="USD"
                ),
                limits=ModelLimits(
                    max_context_tokens=128000,
                    max_output_tokens=4096,
                    rate_limit_rpm=10000,
                    rate_limit_tpm=200000
                ),
                health=ModelHealth(
                    status="healthy",
                    last_check=datetime.now().isoformat(),
                    uptime_percentage=99.9,
                    error_rate=0.02
                ),
                metadata=ModelMetadata(
                    release_date="2024-08-06",
                    recommended_for=["general", "multimodal", "long_context"],
                    not_recommended_for=["simple_queries"]
                )
            ),
            # Refinement Models (Fast & Cheap)
            Model(
                model_id="gpt-3.5-turbo-0125",
                provider="openai",
                model_family="gpt-3.5-turbo",
                version="0125",
                status=ModelStatus.STABLE,
                capabilities=ModelCapabilities(
                    text_generation=True,
                    streaming=True,
                    fast_inference=True
                ),
                performance=ModelPerformance(
                    avg_ttft_ms=100,
                    avg_completion_ms=800,
                    success_rate=0.99,
                    quality_score=0.85
                ),
                costs=ModelCosts(
                    input_tokens_per_1k=0.0005,
                    output_tokens_per_1k=0.0015,
                    currency="USD"
                ),
                limits=ModelLimits(
                    max_context_tokens=16385,
                    max_output_tokens=4096,
                    rate_limit_rpm=15000,
                    rate_limit_tpm=300000
                ),
                health=ModelHealth(
                    status="healthy",
                    last_check=datetime.now().isoformat(),
                    uptime_percentage=99.95,
                    error_rate=0.01
                ),
                metadata=ModelMetadata(
                    release_date="2024-01-25",
                    recommended_for=["refinement", "simple_queries", "fast_inference"],
                    not_recommended_for=["complex_reasoning", "multimodal"]
                )
            ),
            # Anthropic Models
            Model(
                model_id="claude-3-5-sonnet-20241022",
                provider="anthropic",
                model_family="claude-3-5-sonnet",
                version="20241022",
                status=ModelStatus.STABLE,
                capabilities=ModelCapabilities(
                    text_generation=True,
                    tool_use=True,
                    long_context=True,
                    streaming=True,
                    function_calling=True
                ),
                performance=ModelPerformance(
                    avg_ttft_ms=200,
                    avg_completion_ms=3000,
                    success_rate=0.97,
                    quality_score=0.94
                ),
                costs=ModelCosts(
                    input_tokens_per_1k=0.003,
                    output_tokens_per_1k=0.015,
                    currency="USD"
                ),
                limits=ModelLimits(
                    max_context_tokens=200000,
                    max_output_tokens=8192,
                    rate_limit_rpm=5000,
                    rate_limit_tpm=100000
                ),
                health=ModelHealth(
                    status="healthy",
                    last_check=datetime.now().isoformat(),
                    uptime_percentage=99.8,
                    error_rate=0.03
                ),
                metadata=ModelMetadata(
                    release_date="2024-10-22",
                    recommended_for=["general", "reasoning", "long_context"],
                    not_recommended_for=["multimodal"]
                )
            )
        ]
        
        for model in default_models:
            self.models[model.model_id] = model
            self._update_model_metrics(model)
    
    def _initialize_default_providers(self):
        """Initialize with default providers"""
        default_providers = [
            Provider(
                provider_id="openai",
                name="OpenAI",
                status=ProviderStatus.ACTIVE,
                api_base_url="https://api.openai.com/v1",
                authentication={
                    "type": "api_key",
                    "header": "Authorization",
                    "format": "Bearer {api_key}"
                },
                health=ModelHealth(
                    status="healthy",
                    last_check=datetime.now().isoformat(),
                    uptime_percentage=99.8,
                    error_rate=0.02
                ),
                quotas={
                    "requests_per_minute": 10000,
                    "tokens_per_minute": 200000,
                    "requests_per_day": 1000000,
                    "tokens_per_day": 10000000
                },
                models=["gpt-4o-2024-08-06", "gpt-3.5-turbo-0125"]
            ),
            Provider(
                provider_id="anthropic",
                name="Anthropic",
                status=ProviderStatus.ACTIVE,
                api_base_url="https://api.anthropic.com/v1",
                authentication={
                    "type": "api_key",
                    "header": "x-api-key",
                    "format": "{api_key}"
                },
                health=ModelHealth(
                    status="healthy",
                    last_check=datetime.now().isoformat(),
                    uptime_percentage=99.7,
                    error_rate=0.03
                ),
                quotas={
                    "requests_per_minute": 5000,
                    "tokens_per_minute": 100000,
                    "requests_per_day": 500000,
                    "tokens_per_day": 5000000
                },
                models=["claude-3-5-sonnet-20241022"]
            )
        ]
        
        for provider in default_providers:
            self.providers[provider.provider_id] = provider
    
    def _update_model_metrics(self, model: Model):
        """Update Prometheus metrics for a model"""
        model_quality_score.labels(
            model_id=model.model_id,
            provider=model.provider
        ).set(model.performance.quality_score)
        
        model_health_status.labels(
            model_id=model.model_id,
            provider=model.provider
        ).set(1.0 if model.health.status == "healthy" else 0.0)
    
    def get_model(self, model_id: str) -> Optional[Model]:
        """Get model by ID"""
        return self.models.get(model_id)
    
    def get_models_by_capability(self, capability: str) -> List[Model]:
        """Get models that have a specific capability"""
        matching_models = []
        for model in self.models.values():
            if hasattr(model.capabilities, capability) and getattr(model.capabilities, capability):
                matching_models.append(model)
        return matching_models
    
    def get_models_by_provider(self, provider: str) -> List[Model]:
        """Get all models from a specific provider"""
        return [model for model in self.models.values() if model.provider == provider]
    
    def get_stable_models(self) -> List[Model]:
        """Get all stable models"""
        return [model for model in self.models.values() if model.status == ModelStatus.STABLE]
    
    def get_refiner_models(self) -> List[Model]:
        """Get models suitable for refinement (fast & cheap)"""
        refiners = []
        for model in self.models.values():
            if (model.capabilities.fast_inference and 
                model.performance.avg_completion_ms <= 500 and
                model.costs.input_tokens_per_1k <= 0.005):
                refiners.append(model)
        return refiners
    
    def update_model_performance(self, model_id: str, performance: ModelPerformance):
        """Update model performance metrics"""
        if model_id in self.models:
            self.models[model_id].performance = performance
            self._update_model_metrics(self.models[model_id])
    
    def update_model_health(self, model_id: str, health: ModelHealth):
        """Update model health status"""
        if model_id in self.models:
            self.models[model_id].health = health
            self._update_model_metrics(self.models[model_id])
    
    def record_model_usage(self, model_id: str, query_type: str, response_time: float, cost_usd: float):
        """Record model usage for metrics"""
        if model_id in self.models:
            model = self.models[model_id]
            model_usage_counter.labels(
                model_id=model_id,
                provider=model.provider,
                query_type=query_type
            ).inc()
            
            model_response_time.labels(
                model_id=model_id,
                provider=model.provider
            ).observe(response_time)
            
            model_cost_usd.labels(
                model_id=model_id,
                provider=model.provider
            ).inc(cost_usd)

# FastAPI app
app = FastAPI(title="Model Registry Service", version="2.0.0")

# Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Model registry instance
model_registry = ModelRegistry(redis_client)

# Pydantic models for API
class ModelResponse(BaseModel):
    model_id: str
    provider: str
    model_family: str
    version: str
    status: str
    capabilities: Dict[str, bool]
    performance: Dict[str, float]
    costs: Dict[str, Any]
    limits: Dict[str, int]
    health: Dict[str, Any]
    metadata: Dict[str, Any]

class ProviderResponse(BaseModel):
    provider_id: str
    name: str
    status: str
    api_base_url: str
    authentication: Dict[str, Any]
    health: Dict[str, Any]
    quotas: Dict[str, int]
    models: List[str]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "model-registry"}

@app.get("/models", response_model=List[ModelResponse])
async def get_models():
    """Get all models"""
    return [ModelResponse(**asdict(model)) for model in model_registry.models.values()]

@app.get("/models/{model_id}", response_model=ModelResponse)
async def get_model(model_id: str):
    """Get specific model"""
    model = model_registry.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return ModelResponse(**asdict(model))

@app.get("/models/capability/{capability}", response_model=List[ModelResponse])
async def get_models_by_capability(capability: str):
    """Get models by capability"""
    models = model_registry.get_models_by_capability(capability)
    return [ModelResponse(**asdict(model)) for model in models]

@app.get("/models/provider/{provider}", response_model=List[ModelResponse])
async def get_models_by_provider(provider: str):
    """Get models by provider"""
    models = model_registry.get_models_by_provider(provider)
    return [ModelResponse(**asdict(model)) for model in models]

@app.get("/models/stable", response_model=List[ModelResponse])
async def get_stable_models():
    """Get all stable models"""
    models = model_registry.get_stable_models()
    return [ModelResponse(**asdict(model)) for model in models]

@app.get("/models/refiners", response_model=List[ModelResponse])
async def get_refiner_models():
    """Get models suitable for refinement"""
    models = model_registry.get_refiner_models()
    return [ModelResponse(**asdict(model)) for model in models]

@app.get("/providers", response_model=List[ProviderResponse])
async def get_providers():
    """Get all providers"""
    return [ProviderResponse(**asdict(provider)) for provider in model_registry.providers.values()]

@app.get("/providers/{provider_id}", response_model=ProviderResponse)
async def get_provider(provider_id: str):
    """Get specific provider"""
    provider = model_registry.providers.get(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return ProviderResponse(**asdict(provider))

@app.post("/models/{model_id}/usage")
async def record_model_usage(
    model_id: str,
    query_type: str,
    response_time: float,
    cost_usd: float
):
    """Record model usage"""
    model_registry.record_model_usage(model_id, query_type, response_time, cost_usd)
    return {"status": "recorded"}

if __name__ == "__main__":
    # Start Prometheus metrics server
    start_http_server(8001)
    
    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
