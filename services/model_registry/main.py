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
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import redis
import httpx
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Import central configuration
from shared.core.config.central_config import get_central_config

# Import routers and models
from .router import router as api_router
from .routing_router import router as routing_router
from .scan_promote_router import router as scan_promote_router
from .refine_router import router as refine_router
from .search_router import router as search_router
from .feeds_router import router as feeds_router
from .models import ModelResponse, ProviderResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get configuration
config = get_central_config()

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
        self._load_registry_from_source()
    
    def _load_registry_from_source(self):
        """Load registry from documented source (JSON file or in-memory fallback)"""
        try:
            # Try to load from JSON file first
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            models_file = os.path.join(current_dir, "models.json")
            
            if os.path.exists(models_file):
                with open(models_file, 'r') as f:
                    registry_data = json.load(f)
                self._load_models_from_data(registry_data.get("models", []))
                self._load_providers_from_data(registry_data.get("providers", []))
                logger.info(f"Loaded registry from {models_file}")
            else:
                # Fallback to in-memory default models
                logger.warning(f"Models file not found at {models_file}, using in-memory defaults")
                self._initialize_default_models()
                self._initialize_default_providers()
        except Exception as e:
            logger.error(f"Failed to load registry from source: {e}")
            # Fallback to in-memory default models
            logger.info("Falling back to in-memory default models")
            self._initialize_default_models()
            self._initialize_default_providers()
    
    def _load_models_from_data(self, models_data: List[Dict]):
        """Load models from JSON data"""
        for model_data in models_data:
            try:
                model = Model(
                    model_id=model_data["model_id"],
                    provider=model_data["provider"],
                    model_family=model_data["model_family"],
                    version=model_data["version"],
                    status=ModelStatus(model_data["status"]),
                    capabilities=ModelCapabilities(**model_data["capabilities"]),
                    performance=ModelPerformance(**model_data["performance"]),
                    costs=ModelCosts(**model_data["costs"]),
                    limits=ModelLimits(**model_data["limits"]),
                    health=ModelHealth(**model_data["health"]),
                    metadata=ModelMetadata(**model_data["metadata"])
                )
                self.models[model.model_id] = model
                self._update_model_metrics(model)
            except Exception as e:
                logger.error(f"Failed to load model {model_data.get('model_id', 'unknown')}: {e}")
    
    def _load_providers_from_data(self, providers_data: List[Dict]):
        """Load providers from JSON data"""
        for provider_data in providers_data:
            try:
                provider = Provider(
                    provider_id=provider_data["provider_id"],
                    name=provider_data["name"],
                    status=ProviderStatus(provider_data["status"]),
                    api_base_url=provider_data["api_base_url"],
                    authentication=provider_data["authentication"],
                    health=ModelHealth(**provider_data["health"]),
                    quotas=provider_data["quotas"],
                    models=provider_data["models"]
                )
                self.providers[provider.provider_id] = provider
            except Exception as e:
                logger.error(f"Failed to load provider {provider_data.get('provider_id', 'unknown')}: {e}")
    
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

# Create FastAPI app
app = FastAPI(
    title="Model Registry Service",
    version="2.0.0",
    description="Central catalog of all available LLM models, their capabilities, performance characteristics, and cost information"
)

# Set CORS
cors_origins = config.cors_origins
if isinstance(cors_origins, str):
    cors_origins = cors_origins.split(",")
elif not cors_origins:
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# App state / DI container
async def init_dependencies():
    """Initialize shared clients and dependencies"""
    logger.info("Initializing Model Registry dependencies...")
    
    # Initialize Redis client
    redis_url = str(config.redis_url) if hasattr(config, 'redis_url') else "redis://localhost:6379/0"
    app.state.redis_client = redis.Redis.from_url(
        redis_url,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
    
    # Test Redis connection
    try:
        await asyncio.get_event_loop().run_in_executor(
            None, app.state.redis_client.ping
        )
        logger.info("Redis client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise
    
    # Initialize Model Registry
    app.state.model_registry = ModelRegistry(app.state.redis_client)
    logger.info(f"Model Registry initialized successfully with {len(app.state.model_registry.models)} models and {len(app.state.model_registry.providers)} providers")
    
    # Store config in app.state for feature flag access
    app.state.config = config
    
    # Initialize Registry Client for routing
    registry_url = getattr(config, 'registry_url', 'http://localhost:8000')
    app.state.registry_client = httpx.AsyncClient(
        base_url=registry_url,
        timeout=httpx.Timeout(10.0),
        limits=httpx.Limits(max_keepalive_connections=10, max_connections=50)
    )
    logger.info(f"Registry client initialized with URL: {registry_url}")
    
    # Initialize Router Client for query routing
    router_url = getattr(config, 'router_url', 'http://localhost:8001')
    app.state.router_client = httpx.AsyncClient(
        base_url=router_url,
        timeout=httpx.Timeout(5.0),  # Budget constraint: ≤500ms median
        limits=httpx.Limits(max_keepalive_connections=5, max_connections=20)
    )
    logger.info(f"Router client initialized with URL: {router_url}")
    
    # Initialize Cache Client for refinement caching
    cache_redis_url = getattr(config, 'cache_redis_url', str(config.redis_url) if hasattr(config, 'redis_url') else "redis://localhost:6379/1")
    app.state.cache_client = redis.Redis.from_url(
        cache_redis_url, 
        decode_responses=True, 
        socket_connect_timeout=2,  # Budget constraint: fast cache access
        socket_timeout=2,
        retry_on_timeout=True
    )
    try:
        await asyncio.get_event_loop().run_in_executor(None, app.state.cache_client.ping)
        logger.info("Cache client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to connect to cache Redis: {e}")
        # Don't raise - cache is optional for refinement
    
    # Initialize Qdrant Client for vector search
    try:
        from qdrant_client import QdrantClient
        qdrant_url = getattr(config, 'qdrant_url', 'http://localhost:6333')
        # Convert to string if it's a Pydantic HttpUrl object
        qdrant_url = str(qdrant_url) if qdrant_url else 'http://localhost:6333'
        app.state.qdrant_client = QdrantClient(url=qdrant_url, timeout=2.0)
        # Test connection
        app.state.qdrant_client.get_collections()
        logger.info(f"Qdrant client initialized successfully with URL: {qdrant_url}")
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        app.state.qdrant_client = None
    
    # Initialize MeiliSearch Client
    try:
        import meilisearch
        meili_url = getattr(config, 'meili_url', 'http://localhost:7700')
        # Convert to string if it's a Pydantic HttpUrl object
        meili_url = str(meili_url) if meili_url else 'http://localhost:7700'
        meili_key = getattr(config, 'meili_master_key', None)
        app.state.meili_client = meilisearch.Client(meili_url, meili_key)
        # Test connection
        app.state.meili_client.health()
        logger.info(f"MeiliSearch client initialized successfully with URL: {meili_url}")
    except Exception as e:
        logger.error(f"Failed to connect to MeiliSearch: {e}")
        app.state.meili_client = None
    
    # Initialize ArangoDB Client
    try:
        from arango import ArangoClient
        arango_url = getattr(config, 'arango_url', 'http://localhost:8529')
        # Convert to string if it's a Pydantic HttpUrl object
        arango_url = str(arango_url) if arango_url else 'http://localhost:8529'
        arango_username = getattr(config, 'arango_username', 'root')
        arango_password = getattr(config, 'arango_password', '')
        app.state.arango_client = ArangoClient(hosts=[arango_url])
        app.state.arango_db = app.state.arango_client.db('_system', username=arango_username, password=arango_password)
        # Test connection
        app.state.arango_db.version()
        logger.info(f"ArangoDB client initialized successfully with URL: {arango_url}")
    except Exception as e:
        logger.error(f"Failed to connect to ArangoDB: {e}")
        app.state.arango_client = None
        app.state.arango_db = None
    
    # Initialize Web/News/Markets Provider Clients
    web_provider_url = getattr(config, 'web_provider_url', 'http://localhost:8002')
    app.state.web_provider_client = httpx.AsyncClient(
        base_url=web_provider_url,
        timeout=httpx.Timeout(3.0),
        limits=httpx.Limits(max_keepalive_connections=3, max_connections=10)
    )
    logger.info(f"Web provider client initialized with URL: {web_provider_url}")
    
    news_provider_url = getattr(config, 'news_provider_url', 'http://localhost:8003')
    app.state.news_provider_client = httpx.AsyncClient(
        base_url=news_provider_url,
        timeout=httpx.Timeout(3.0),
        limits=httpx.Limits(max_keepalive_connections=3, max_connections=10)
    )
    logger.info(f"News provider client initialized with URL: {news_provider_url}")
    
    markets_provider_url = getattr(config, 'markets_provider_url', 'http://localhost:8004')
    app.state.markets_provider_client = httpx.AsyncClient(
        base_url=markets_provider_url,
        timeout=httpx.Timeout(3.0),
        limits=httpx.Limits(max_keepalive_connections=3, max_connections=10)
    )
    logger.info(f"Markets provider client initialized with URL: {markets_provider_url}")
    
    # Initialize Guided Prompt Pre-flight Client
    guided_prompt_url = getattr(config, 'guided_prompt_url', 'http://localhost:8005')
    app.state.guided_prompt_client = httpx.AsyncClient(
        base_url=guided_prompt_url,
        timeout=httpx.Timeout(1.0),  # Pre-flight budget constraint
        limits=httpx.Limits(max_keepalive_connections=2, max_connections=5)
    )
    logger.info(f"Guided prompt client initialized with URL: {guided_prompt_url}")
    
    # Initialize News and Markets Adapters
    from .feeds_adapters import NewsAdapter, MarketsAdapter
    
    app.state.news_adapter = NewsAdapter(config, app.state.redis_client)
    logger.info(f"News adapter initialized with {len(app.state.news_adapter.providers)} providers")
    
    app.state.markets_adapter = MarketsAdapter(config, app.state.redis_client)
    logger.info(f"Markets adapter initialized with {len(app.state.markets_adapter.providers)} providers")

async def cleanup_dependencies():
    """Cleanup shared clients and dependencies"""
    logger.info("Cleaning up Model Registry dependencies...")
    
    if hasattr(app.state, 'redis_client'):
        try:
            app.state.redis_client.close()
            logger.info("Redis client closed successfully")
        except Exception as e:
            logger.error(f"Error closing Redis client: {e}")
    
    if hasattr(app.state, 'registry_client'):
        try:
            await app.state.registry_client.aclose()
            logger.info("Registry client closed successfully")
        except Exception as e:
            logger.error(f"Error closing registry client: {e}")
    
    if hasattr(app.state, 'router_client'):
        try:
            await app.state.router_client.aclose()
            logger.info("Router client closed successfully")
        except Exception as e:
            logger.error(f"Error closing router client: {e}")
    
    if hasattr(app.state, 'cache_client'):
        try:
            app.state.cache_client.close()
            logger.info("Cache client closed successfully")
        except Exception as e:
            logger.error(f"Error closing cache client: {e}")
    
    # Close provider clients
    provider_clients = [
        ('web_provider_client', 'Web provider'),
        ('news_provider_client', 'News provider'),
        ('markets_provider_client', 'Markets provider'),
        ('guided_prompt_client', 'Guided prompt')
    ]
    
    for client_attr, client_name in provider_clients:
        if hasattr(app.state, client_attr):
            try:
                await getattr(app.state, client_attr).aclose()
                logger.info(f"{client_name} client closed successfully")
            except Exception as e:
                logger.error(f"Error closing {client_name} client: {e}")
    
    # Close database clients
    if hasattr(app.state, 'qdrant_client') and app.state.qdrant_client:
        try:
            app.state.qdrant_client.close()
            logger.info("Qdrant client closed successfully")
        except Exception as e:
            logger.error(f"Error closing Qdrant client: {e}")
    
    if hasattr(app.state, 'meili_client') and app.state.meili_client:
        try:
            # MeiliSearch client doesn't have explicit close method
            app.state.meili_client = None
            logger.info("MeiliSearch client closed successfully")
        except Exception as e:
            logger.error(f"Error closing MeiliSearch client: {e}")
    
    if hasattr(app.state, 'arango_client') and app.state.arango_client:
        try:
            app.state.arango_client.close()
            logger.info("ArangoDB client closed successfully")
        except Exception as e:
            logger.error(f"Error closing ArangoDB client: {e}")

# Include routers
app.include_router(api_router)
app.include_router(routing_router)
app.include_router(scan_promote_router)
app.include_router(refine_router)
app.include_router(search_router)
app.include_router(feeds_router)

# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    await init_dependencies()

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    await cleanup_dependencies()

# Pydantic models are now imported from models.py

# Health & Config endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint - fast, no downstream calls"""
    return {"service": "model-registry", "status": "ok"}

@app.get("/models")
async def get_models():
    """Get all available models from the registry"""
    try:
        if not hasattr(app.state, 'model_registry'):
            raise HTTPException(status_code=503, detail="Model registry not initialized")
        
        models = list(app.state.model_registry.models.values())
        return {
            "models": [
                {
                    "model_id": model.model_id,
                    "model_family": getattr(model, 'model_family', model.model_id),
                    "provider": model.provider,
                    "status": model.status.value,
                    "capabilities": {
                        "text_generation": getattr(model.capabilities, 'text_generation', False),
                        "code_generation": getattr(model.capabilities, 'code_generation', False),
                        "fast_inference": getattr(model.capabilities, 'fast_inference', False),
                        "reasoning": getattr(model.capabilities, 'reasoning', False),
                        "vision": getattr(model.capabilities, 'vision', False),
                        "multimodal": getattr(model.capabilities, 'multimodal', False),
                        "tool_use": getattr(model.capabilities, 'tool_use', False),
                        "long_context": getattr(model.capabilities, 'long_context', False),
                        "streaming": getattr(model.capabilities, 'streaming', False),
                        "function_calling": getattr(model.capabilities, 'function_calling', False)
                    },
                    "performance": {
                        "quality_score": getattr(model.performance, 'quality_score', 0.0),
                        "avg_completion_ms": getattr(model.performance, 'avg_completion_ms', 0),
                        "success_rate": getattr(model.performance, 'success_rate', 0.0)
                    },
                    "health": {
                        "status": getattr(model.health, 'status', 'unknown'),
                        "last_check": model.health.last_check if hasattr(model.health, 'last_check') and model.health.last_check else None
                    }
                }
                for model in models
            ],
            "total_count": len(models)
        }
    except Exception as e:
        logger.error(f"Error retrieving models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve models: {str(e)}")

@app.get("/ready")
async def ready_check():
    """Ready check endpoint - performs 1-shot registry ping under small timeout"""
    try:
        # Check if model registry is loaded and has models
        if not hasattr(app.state, 'model_registry'):
            raise HTTPException(status_code=503, detail="Model registry not initialized")
        
        # Check if registry has models loaded
        if not app.state.model_registry.models:
            raise HTTPException(status_code=503, detail="No models loaded in registry")
        
        # Quick Redis ping to ensure connectivity
        await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None, app.state.redis_client.ping
            ),
            timeout=2.0
        )
        
        # Perform 1-shot registry ping
        registry_status = "reachable"
        try:
            if hasattr(app.state, 'registry_client'):
                await asyncio.wait_for(
                    app.state.registry_client.get("/health"),
                    timeout=1.0
                )
            else:
                registry_status = "degraded"
        except Exception as e:
            logger.warning(f"Registry ping failed: {e}")
            registry_status = "degraded"
        
        # Probe Qdrant/Meili/Arango with tiny timeouts
        database_status = {}
        
        # Qdrant probe
        try:
            if hasattr(app.state, 'qdrant_client') and app.state.qdrant_client:
                await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None, app.state.qdrant_client.get_collections
                    ),
                    timeout=0.5
                )
                database_status["qdrant"] = "healthy"
            else:
                database_status["qdrant"] = "degraded"
        except Exception as e:
            logger.warning(f"Qdrant probe failed: {e}")
            database_status["qdrant"] = "degraded"
        
        # MeiliSearch probe
        try:
            if hasattr(app.state, 'meili_client') and app.state.meili_client:
                await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None, app.state.meili_client.health
                    ),
                    timeout=0.5
                )
                database_status["meili"] = "healthy"
            else:
                database_status["meili"] = "degraded"
        except Exception as e:
            logger.warning(f"MeiliSearch probe failed: {e}")
            database_status["meili"] = "degraded"
        
        # ArangoDB probe
        try:
            if hasattr(app.state, 'arango_db') and app.state.arango_db:
                await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None, app.state.arango_db.version
                    ),
                    timeout=0.5
                )
                database_status["arango"] = "healthy"
            else:
                database_status["arango"] = "degraded"
        except Exception as e:
            logger.warning(f"ArangoDB probe failed: {e}")
            database_status["arango"] = "degraded"
        
        # Determine overall status
        healthy_dbs = sum(1 for status in database_status.values() if status == "healthy")
        total_dbs = len(database_status)
        
        if healthy_dbs == total_dbs:
            overall_status = "ready"
        elif healthy_dbs > 0:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"
        
        return {
            "status": overall_status, 
            "service": "model-registry", 
            "models_loaded": len(app.state.model_registry.models),
            "registry_status": registry_status,
            "database_status": database_status,
            "healthy_databases": f"{healthy_dbs}/{total_dbs}"
        }
    except Exception as e:
        logger.error(f"Ready check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/config")
async def get_config_endpoint():
    """Config endpoint - sanitized echo of active providers, keyless fallbacks, and budgets"""
    
    # Get news providers info
    news_providers = {}
    if hasattr(app.state, 'news_adapter'):
        for provider_name, provider_config in app.state.news_adapter.providers.items():
            news_providers[provider_name] = {
                "enabled": provider_config.get('enabled', False),
                "keyless": provider_config.get('keyless', True),
                "has_key": bool(provider_config.get('key'))
            }
    
    # Get markets providers info
    markets_providers = {}
    if hasattr(app.state, 'markets_adapter'):
        for provider_name, provider_config in app.state.markets_adapter.providers.items():
            markets_providers[provider_name] = {
                "enabled": provider_config.get('enabled', False),
                "keyless": provider_config.get('keyless', True),
                "has_key": bool(provider_config.get('key'))
            }
    
    return {
        "service": "model-registry",
        "active_providers": {
            "openai": bool(getattr(config, 'openai_api_key', None)),
            "anthropic": bool(getattr(config, 'anthropic_api_key', None)),
            "google": bool(getattr(config, 'google_api_key', None)),
            "huggingface": bool(getattr(config, 'huggingface_api_key', None) or getattr(config, 'huggingface_read_token', None) or getattr(config, 'huggingface_write_token', None)),
            "ollama": bool(getattr(config, 'ollama_base_url', None))
        },
        "feeds_providers": {
            "news": news_providers,
            "markets": markets_providers
        },
        "keyless_fallbacks_enabled": getattr(config, 'keyless_fallbacks_enabled', True),
        "guided_prompt_enabled": True,  # Always enabled for refinement
        "budgets": {
            "pre_flight": {
                "median_latency_ms": 500,
                "p95_latency_ms": 800,
                "max_cost_usd": 0.01,
                "max_sources": 10,
                "max_citations": 5
            },
            "router_timeout_ms": 5000,
            "cache_timeout_ms": 2000,
            "feeds_timeout_ms": 800
        },
        "environment": getattr(config, 'environment', 'development'),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/version")
async def get_version():
    """Version endpoint"""
    return {
        "service": "model-registry",
        "version": "2.0.0",
        "build_date": datetime.now().isoformat(),
        "environment": getattr(config, 'environment', 'development')
    }

# API endpoints are now handled by the included router

# Observability middleware
# Always mount Prometheus metrics endpoint
try:
    from prometheus_client import make_asgi_app
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    logger.info("Prometheus metrics endpoint mounted at /metrics")
except Exception as e:
    logger.error(f"Failed to mount Prometheus metrics: {e}")

# Conditional tracing setup - only if keys exist
tracing_enabled = False
if (hasattr(config, 'tracing_enabled') and config.tracing_enabled and 
    hasattr(config, 'jaeger_agent_host') and config.jaeger_agent_host):
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.jaeger.thrift import JaegerExporter
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        
        # Configure Jaeger tracing
        trace.set_tracer_provider(TracerProvider())
        jaeger_exporter = JaegerExporter(
            agent_host_name=config.jaeger_agent_host,
            agent_port=int(config.jaeger_agent_port) if hasattr(config, 'jaeger_agent_port') and config.jaeger_agent_port else 6831,
        )
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(app)
        tracing_enabled = True
        logger.info("Jaeger tracing enabled")
    except ImportError:
        logger.warning("OpenTelemetry packages not available, tracing disabled")
    except Exception as e:
        logger.error(f"Failed to enable tracing: {e}")
else:
    logger.info("Tracing disabled - no tracing keys configured")

# Add debug trace endpoint if tracing is enabled
if tracing_enabled:
    @app.get("/_debug/trace")
    async def debug_trace():
        """Debug endpoint to echo trace information when tracing is enabled"""
        try:
            from opentelemetry import trace
            tracer = trace.get_tracer(__name__)
            
            # Create a sample span
            with tracer.start_as_current_span("debug_trace_echo") as span:
                span.set_attribute("debug.endpoint", "/_debug/trace")
                span.set_attribute("debug.timestamp", datetime.now().isoformat())
                
                return {
                    "status": "tracing_enabled",
                    "tracer_name": tracer.name,
                    "trace_id": format(span.get_span_context().trace_id, '032x'),
                    "span_id": format(span.get_span_context().span_id, '016x'),
                    "timestamp": datetime.now().isoformat(),
                    "message": "Tracing is active and working"
                }
        except Exception as e:
            logger.error(f"Debug trace endpoint error: {e}")
            return {
                "status": "tracing_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
else:
    @app.get("/_debug/trace")
    async def debug_trace_disabled():
        """Debug endpoint when tracing is disabled"""
        return {
            "status": "tracing_disabled",
            "message": "Tracing is not enabled - no tracing keys configured",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Start FastAPI server with integrated metrics endpoint
    log_level = getattr(config, 'log_level', 'info')
    if hasattr(log_level, 'value'):
        log_level = log_level.value.lower()
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level=log_level
    )
