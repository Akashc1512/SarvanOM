"""
API Gateway for Universal Knowledge Platform

This gateway routes requests to various microservices including:
- Search/Retrieval service
- Fact-check service  
- Synthesis service
- Authentication service
- Crawler service
- Vector database service
- Knowledge graph service
"""

# Load environment variables from .env file first
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if present
except ImportError:
    pass  # dotenv not installed, continue without it

# Import Windows compatibility fixes first
try:
    import shared.core.windows_compatibility
except ImportError:
    pass  # Windows compatibility not available

from fastapi import FastAPI, HTTPException, Request, Response, WebSocket, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional, List
import logging
import time
import re
import json
import httpx
import asyncio
from datetime import datetime, timezone
from starlette.middleware.base import BaseHTTPMiddleware

# Security patterns for input validation
XSS_PATTERN = re.compile(r'<script[^>]*>.*?</script>|<iframe[^>]*>.*?</iframe>|javascript:|on\w+\s*=', re.IGNORECASE | re.DOTALL)
SQL_INJECTION_PATTERN = re.compile(r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)|(\b(OR|AND)\s+\d+\s*=\s*\d+)|(\b(OR|AND)\s+\w+\s*=\s*\w+)|(\b(OR|AND)\s+\'\s*=\s*\')', re.IGNORECASE)

# Import unified logging
from shared.core.unified_logging import setup_logging, get_logger, setup_fastapi_logging

# Import observability middleware
from services.gateway.middleware.observability import (
    ObservabilityMiddleware, 
    MetricsMiddleware,
    log_llm_call,
    log_cache_event,
    log_stream_event,
    log_error,
    monitor_performance
)

# Import security middleware
from services.gateway.middleware.security import (
    SecurityMiddleware,
    InputValidationMiddleware,
    SecurityConfig,
    RateLimitConfig
)

# Import resilience components
from services.gateway.resilience.circuit_breaker import (
    circuit_breaker_manager,
    CircuitBreakerConfig,
    CircuitBreakerError
)

from services.gateway.resilience.graceful_degradation import (
    degradation_manager,
    error_boundary,
    get_fallback_response,
    check_fallback_needed,
    get_degradation_status
)

# Import analytics metrics
from services.analytics.metrics.knowledge_platform_metrics import (
    record_query_intelligence_metrics,
    record_retrieval_metrics,
    record_business_metrics,
    record_expert_validation_metrics
)

# Import the real LLM processor
from services.gateway.real_llm_integration import RealLLMProcessor

# Import zero-budget retrieval
from services.retrieval.free_tier import get_zero_budget_retrieval, combined_search
from services.retrieval.routers.free_tier_router import router as free_tier_router

# Import gateway routers
from services.gateway.routes import (
    analytics_router,
    health_router,
    search_router,
    fact_check_router,
    synthesis_router,
    auth_router,
    vector_router
)

# Import advanced features router
try:
    from services.gateway.routers.advanced_features_router import router as advanced_features_router
except Exception as e:
    print(f"Warning: Could not import advanced features router: {e}")
    advanced_features_router = None

# Import additional service routers (with error handling)
try:
    from services.auth.routes import router as auth_service_router
except Exception as e:
    print(f"Warning: Could not import auth service router: {e}")
    auth_service_router = None

try:
    from services.fact_check.routes import router as fact_check_service_router
except Exception as e:
    print(f"Warning: Could not import fact check service router: {e}")
    fact_check_service_router = None

# Import backend API routers (with error handling)
try:
    from backend.api.routers.admin_router import router as admin_router
except Exception as e:
    print(f"Warning: Could not import admin router: {e}")
    admin_router = None

try:
    from backend.api.routers.agent_router import router as agent_router
except Exception as e:
    print(f"Warning: Could not import agent router: {e}")
    agent_router = None

try:
    from backend.api.routers.auth_router import router as backend_auth_router
except Exception as e:
    print(f"Warning: Could not import backend auth router: {e}")
    backend_auth_router = None

try:
    from backend.api.routers.database_router import router as database_router
except Exception as e:
    print(f"Warning: Could not import database router: {e}")
    database_router = None

try:
    from backend.api.routers.health_router import router as backend_health_router
except Exception as e:
    print(f"Warning: Could not import backend health router: {e}")
    backend_health_router = None

try:
    from backend.api.routers.query_router import router as query_router
except Exception as e:
    print(f"Warning: Could not import query router: {e}")
    query_router = None

# Import streaming manager
from services.gateway.streaming_manager import streaming_manager, create_sse_response

# Import advanced features
from services.gateway.cache_manager import cache_manager
from services.gateway.background_processor import background_processor, TaskType, TaskPriority
from services.gateway.prompt_optimizer import prompt_optimizer, PromptType, PromptComplexity
from services.gateway.huggingface_integration import huggingface_integration

# Import shared components for microservice architecture
from shared.models.crud_models import (
    CacheEntry, UserProfile, ModelConfiguration, Dataset, SystemSetting,
    CRUDResponse, PaginationParams, FilterParams, ResourceType
)
from shared.contracts.service_contracts import (
    ServiceType, ServiceStatus, ServiceHealth
)
from shared.clients.service_client import ServiceClientFactory, CRUDServiceClient

# Initialize the LLM processor
llm_processor = RealLLMProcessor()

# Configure unified logging
logging_config = setup_logging(service_name="sarvanom-gateway-service")
logger = get_logger(__name__)

# Health and readiness tracking
startup_time = time.time()
import uuid
import os
import subprocess
from contextlib import asynccontextmanager

# Initialize advanced features
async def initialize_advanced_features():
    """Initialize all advanced features"""
    try:
        # Initialize cache manager
        await cache_manager.initialize()
        logger.info("✅ Cache manager initialized")
        
        # Initialize stream manager
        await stream_manager.initialize()
        logger.info("✅ Stream manager initialized")
        
        # Initialize background processor
        await background_processor.initialize()
        logger.info("✅ Background processor initialized")
        
        # Initialize prompt optimizer
        await prompt_optimizer.initialize()
        logger.info("✅ Prompt optimizer initialized")
        
        # Initialize HuggingFace integration
        await huggingface_integration.initialize()
        logger.info("✅ HuggingFace integration initialized")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize advanced features: {e}")

# Initialize features on startup using modern lifespan
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_advanced_features()
    yield
    # Shutdown
    await cache_manager.close()
    await stream_manager.close()
    await huggingface_integration.close()
    await background_processor.close()
    await prompt_optimizer.close()



# Update FastAPI app with lifespan
app = FastAPI(
    title="Universal Knowledge Platform API Gateway",
    description="Advanced API Gateway with caching, streaming, background processing, and prompt optimization",
    version="1.0.0",
    lifespan=lifespan
)

# Security and observability configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "https://sarvanom.com",
    "https://www.sarvanom.com"
]

# Security configuration
security_config = SecurityConfig(
    rate_limit=RateLimitConfig(
        requests_per_minute=60,
        burst_limit=10,
        window_size=60,
        block_duration=300
    ),
    trusted_hosts={
        "localhost",
        "127.0.0.1",
        "::1",
        "sarvanom.local",
        "*.sarvanom.com",
        "*.sarvanom.org"
    },
    max_request_size=10 * 1024 * 1024,  # 10MB
    max_query_length=1000,
    max_headers_size=8192,
    enable_csp=True,
    enable_hsts=True,
    enable_x_frame_options=True,
    enable_x_content_type_options=True,
    enable_referrer_policy=True
)

# App is already created above with lifespan

# Setup FastAPI logging integration
setup_fastapi_logging(app, service_name="sarvanom-gateway-service")

# Add observability middleware (first - to capture all requests)
app.add_middleware(ObservabilityMiddleware, service_name="sarvanom-gateway")

# Add metrics middleware for Prometheus metrics
app.add_middleware(MetricsMiddleware)

# Add security middleware
app.add_middleware(SecurityMiddleware, config=security_config)

# Add input validation middleware
app.add_middleware(InputValidationMiddleware)

# Add trusted host middleware with permissive configuration for testing
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=list(security_config.trusted_hosts) + ["testserver", "*"]
)

# Add CORS middleware with secure configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(free_tier_router, prefix="/retrieval")
app.include_router(analytics_router, prefix="/analytics")

# Resilience endpoints
@app.get("/health/resilience")
async def get_resilience_health():
    """Get resilience system health status."""
    try:
        circuit_breaker_status = circuit_breaker_manager.get_all_status()
        degradation_status = get_degradation_status()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "circuit_breakers": circuit_breaker_status,
            "degradation": degradation_status,
            "request_id": get_request_id()
        }
    except Exception as e:
        log_error("resilience_health_check_failed", str(e))
        raise HTTPException(status_code=500, detail="Resilience health check failed")

@app.post("/resilience/reset-circuit-breakers")
async def reset_circuit_breakers():
    """Reset all circuit breakers."""
    try:
        await circuit_breaker_manager.reset_all_circuit_breakers()
        return {
            "status": "success",
            "message": "All circuit breakers reset",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": get_request_id()
        }
    except Exception as e:
        log_error("circuit_breaker_reset_failed", str(e))
        raise HTTPException(status_code=500, detail="Failed to reset circuit breakers")

@app.get("/resilience/circuit-breakers/{provider}")
async def get_circuit_breaker_status(provider: str):
    """Get circuit breaker status for specific provider."""
    try:
        circuit_breaker = circuit_breaker_manager.get_circuit_breaker(provider)
        return circuit_breaker.get_status()
    except Exception as e:
        log_error("circuit_breaker_status_failed", str(e))
        raise HTTPException(status_code=404, detail=f"Circuit breaker not found for provider: {provider}")

@app.post("/resilience/circuit-breakers/{provider}/reset")
async def reset_circuit_breaker(provider: str):
    """Reset circuit breaker for specific provider."""
    try:
        await circuit_breaker_manager.reset_circuit_breaker(provider)
        return {
            "status": "success",
            "message": f"Circuit breaker reset for {provider}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": get_request_id()
        }
    except Exception as e:
        log_error("circuit_breaker_reset_failed", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to reset circuit breaker for {provider}")
app.include_router(health_router, prefix="/health")
app.include_router(search_router, prefix="/search")
app.include_router(fact_check_router, prefix="/factcheck")
app.include_router(synthesis_router, prefix="/synthesis")
app.include_router(auth_router, prefix="/auth")
app.include_router(vector_router, prefix="/vector")

# Include additional service routers (only if successfully imported)
if auth_service_router:
    app.include_router(auth_service_router, prefix="/auth-service")

if fact_check_service_router:
    app.include_router(fact_check_service_router, prefix="/fact-check-service")

# Include backend API routers (only if successfully imported)
if admin_router:
    app.include_router(admin_router, prefix="/admin")

if agent_router:
    app.include_router(agent_router, prefix="/agents")

if backend_auth_router:
    app.include_router(backend_auth_router, prefix="/backend-auth")

if database_router:
    app.include_router(database_router, prefix="/database")

if backend_health_router:
    app.include_router(backend_health_router, prefix="/backend-health")

if query_router:
    app.include_router(query_router, prefix="/query")

# Include advanced features router
if advanced_features_router:
    app.include_router(advanced_features_router)

# Request/Response models with enhanced validation
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    user_id: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    
    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and sanitize query input."""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        
        # Check for malicious content
        if XSS_PATTERN.search(v):
            raise ValueError("Query contains potentially malicious content")
        if SQL_INJECTION_PATTERN.search(v):
            raise ValueError("Query contains potentially malicious content")
        
        return v.strip()

class FactCheckRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=50000)
    user_id: Optional[str] = None
    context: Optional[str] = None
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate and sanitize content input."""
        if not v.strip():
            raise ValueError("Content cannot be empty")
        
        # Check for malicious content
        if XSS_PATTERN.search(v):
            raise ValueError("Content contains potentially malicious content")
        
        return v.strip()

class SynthesisRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    sources: Optional[List[str]] = None
    user_id: Optional[str] = None
    
    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and sanitize query input."""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        
        # Check for malicious content
        if XSS_PATTERN.search(v):
            raise ValueError("Query contains potentially malicious content")
        
        return v.strip()

class AuthRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        return v.strip()

class CrawlRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=2048)
    depth: Optional[int] = Field(default=1, ge=1, le=5)
    user_id: Optional[str] = None
    
    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v.strip()

class VectorSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    limit: Optional[int] = Field(default=10, ge=1, le=100)
    filters: Optional[Dict[str, Any]] = None
    
    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and sanitize query input."""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        
        # Check for malicious content
        if XSS_PATTERN.search(v):
            raise ValueError("Query contains potentially malicious content")
        
        return v.strip()

# CRUD Operation Models for Full RESTful API Implementation
class CacheEntry(BaseModel):
    key: str = Field(..., description="Cache key", min_length=1, max_length=255)
    value: Any = Field(..., description="Cache value")
    ttl: int = Field(default=3600, description="Time to live in seconds", ge=1, le=86400)
    tags: Optional[List[str]] = Field(default=None, description="Cache tags for organization")
    service: str = Field(..., description="Service that owns this cache entry")
    
    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str) -> str:
        """Validate cache key format."""
        if not v.strip():
            raise ValueError("Cache key cannot be empty")
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Cache key can only contain letters, numbers, underscores, and hyphens")
        return v.strip()
    
    @field_validator("service")
    @classmethod
    def validate_service(cls, v: str) -> str:
        """Validate service name format."""
        if not v.strip():
            raise ValueError("Service name cannot be empty")
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Service name can only contain letters, numbers, underscores, and hyphens")
        return v.strip()

class UserProfile(BaseModel):
    user_id: str = Field(..., description="User identifier", min_length=1, max_length=100)
    username: str = Field(..., description="Username", min_length=3, max_length=50)
    email: str = Field(..., description="Email address")
    preferences: Optional[Dict[str, Any]] = Field(default=None, description="User preferences")
    settings: Optional[Dict[str, Any]] = Field(default=None, description="User settings")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        import re
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(v):
            raise ValueError("Invalid email format")
        return v.lower()
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        return v.strip()

class ModelConfiguration(BaseModel):
    model_name: str = Field(..., description="Model name", min_length=1, max_length=100)
    provider: str = Field(..., description="Model provider", min_length=1, max_length=50)
    parameters: Dict[str, Any] = Field(..., description="Model parameters")
    enabled: bool = Field(default=True, description="Whether model is enabled")
    priority: int = Field(default=1, description="Model priority", ge=1, le=10)
    service: str = Field(..., description="Service that owns this model")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    
    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        """Validate model name format."""
        if not v.strip():
            raise ValueError("Model name cannot be empty")
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Model name can only contain letters, numbers, underscores, and hyphens")
        return v.strip()
    
    @field_validator("service")
    @classmethod
    def validate_service(cls, v: str) -> str:
        """Validate service name format."""
        if not v.strip():
            raise ValueError("Service name cannot be empty")
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Service name can only contain letters, numbers, underscores, and hyphens")
        return v.strip()

class Dataset(BaseModel):
    dataset_id: str = Field(..., description="Dataset identifier", min_length=1, max_length=100)
    name: str = Field(..., description="Dataset name", min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, description="Dataset description")
    source: str = Field(..., description="Data source", min_length=1, max_length=255)
    format: str = Field(..., description="Data format", min_length=1, max_length=50)
    size: Optional[int] = Field(default=None, description="Dataset size in bytes")
    service: str = Field(..., description="Service that owns this dataset")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    
    @field_validator("dataset_id")
    @classmethod
    def validate_dataset_id(cls, v: str) -> str:
        """Validate dataset ID format."""
        if not v.strip():
            raise ValueError("Dataset ID cannot be empty")
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Dataset ID can only contain letters, numbers, underscores, and hyphens")
        return v.strip()
    
    @field_validator("service")
    @classmethod
    def validate_service(cls, v: str) -> str:
        """Validate service name format."""
        if not v.strip():
            raise ValueError("Service name cannot be empty")
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Service name can only contain letters, numbers, underscores, and hyphens")
        return v.strip()

class SystemSetting(BaseModel):
    setting_key: str = Field(..., description="Setting key", min_length=1, max_length=100)
    setting_value: Any = Field(..., description="Setting value")
    category: str = Field(..., description="Setting category", min_length=1, max_length=50)
    description: Optional[str] = Field(default=None, description="Setting description")
    encrypted: bool = Field(default=False, description="Whether setting is encrypted")
    service: str = Field(..., description="Service that owns this setting")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    
    @field_validator("setting_key")
    @classmethod
    def validate_setting_key(cls, v: str) -> str:
        """Validate setting key format."""
        if not v.strip():
            raise ValueError("Setting key cannot be empty")
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Setting key can only contain letters, numbers, underscores, and hyphens")
        return v.strip()
    
    @field_validator("service")
    @classmethod
    def validate_service(cls, v: str) -> str:
        """Validate service name format."""
        if not v.strip():
            raise ValueError("Service name cannot be empty")
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Service name can only contain letters, numbers, underscores, and hyphens")
        return v.strip()

class GraphContextRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    depth: Optional[int] = Field(default=2, ge=1, le=5)
    user_id: Optional[str] = None

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str) -> str:
        """Validate and sanitize topic input."""
        if not v.strip():
            raise ValueError("Topic cannot be empty")
        
        # Check for malicious content
        if XSS_PATTERN.search(v):
            raise ValueError("Topic contains potentially malicious content")
        
        return v.strip()

# Health and Readiness Models
class DependencyStatus(BaseModel):
    """Individual dependency status"""
    name: str = Field(..., description="Dependency name")
    status: str = Field(..., description="Status: healthy, degraded, or unhealthy")
    response_time_ms: Optional[int] = Field(default=None, description="Response time in milliseconds")
    error_message: Optional[str] = Field(default=None, description="Error message if unhealthy")
    last_check: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Last check timestamp")

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Overall status: healthy, degraded, or unhealthy")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Health check timestamp")
    uptime_s: float = Field(..., description="Service uptime in seconds")
    version: str = Field(..., description="Service version")
    git_sha: Optional[str] = Field(default=None, description="Git commit SHA")
    build_time: Optional[str] = Field(default=None, description="Build timestamp")

class ReadinessResponse(BaseModel):
    """Readiness check response model"""
    status: str = Field(..., description="Overall status: ready or not_ready")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Readiness check timestamp")
    uptime_s: float = Field(..., description="Service uptime in seconds")
    dependencies: List[DependencyStatus] = Field(..., description="List of dependency statuses")
    error_count: int = Field(..., description="Number of unhealthy dependencies")

class VersionResponse(BaseModel):
    """Version information response model"""
    version: str = Field(..., description="Service version")
    git_sha: Optional[str] = Field(default=None, description="Git commit SHA")
    build_time: Optional[str] = Field(default=None, description="Build timestamp")
    environment: str = Field(..., description="Environment (development, staging, production)")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Version check timestamp")

# REMOVED: Duplicate health endpoint - using health_router.get("/health") instead

# Health and Readiness Functions
def get_git_sha() -> Optional[str]:
    """Get the current git SHA"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass
    return None

def get_build_time() -> Optional[str]:
    """Get build time from environment or file"""
    # Try to get from environment variable first
    build_time = os.getenv("BUILD_TIME")
    if build_time:
        return build_time
    
    # Try to get from git commit date
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cd", "--date=iso"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass
    return None

async def check_crud_service() -> DependencyStatus:
    """Check CRUD service health"""
    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8001/health")
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                return DependencyStatus(
                    name="crud_service",
                    status="healthy",
                    response_time_ms=response_time_ms
                )
            else:
                return DependencyStatus(
                    name="crud_service",
                    status="unhealthy",
                    response_time_ms=response_time_ms,
                    error_message=f"HTTP {response.status_code}"
                )
    except Exception as e:
        response_time_ms = int((time.time() - start_time) * 1000)
        return DependencyStatus(
            name="crud_service",
            status="unhealthy",
            response_time_ms=response_time_ms,
            error_message=str(e)
        )

async def check_retrieval_service() -> DependencyStatus:
    """Check retrieval service health"""
    start_time = time.time()
    try:
        # For now, check if the service is configured
        # In production, this would check the actual retrieval service endpoint
        retrieval_url = os.getenv("RETRIEVAL_SERVICE_URL", "http://localhost:8002")
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{retrieval_url}/health")
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                return DependencyStatus(
                    name="retrieval_service",
                    status="healthy",
                    response_time_ms=response_time_ms
                )
            else:
                return DependencyStatus(
                    name="retrieval_service",
                    status="unhealthy",
                    response_time_ms=response_time_ms,
                    error_message=f"HTTP {response.status_code}"
                )
    except Exception as e:
        response_time_ms = int((time.time() - start_time) * 1000)
        return DependencyStatus(
            name="retrieval_service",
            status="unhealthy",
            response_time_ms=response_time_ms,
            error_message=str(e)
        )

async def check_synthesis_service() -> DependencyStatus:
    """Check synthesis/LLM service health"""
    start_time = time.time()
    try:
        # Check if LLM processor is available
        if llm_processor and hasattr(llm_processor, 'health_check'):
            await llm_processor.health_check()
            response_time_ms = int((time.time() - start_time) * 1000)
            return DependencyStatus(
                name="synthesis_service",
                status="healthy",
                response_time_ms=response_time_ms
            )
        else:
            # Basic check - if we can import the processor, consider it healthy
            response_time_ms = int((time.time() - start_time) * 1000)
            return DependencyStatus(
                name="synthesis_service",
                status="healthy",
                response_time_ms=response_time_ms
            )
    except Exception as e:
        response_time_ms = int((time.time() - start_time) * 1000)
        return DependencyStatus(
            name="synthesis_service",
            status="unhealthy",
            response_time_ms=response_time_ms,
            error_message=str(e)
        )

async def check_vector_store() -> DependencyStatus:
    """Check vector store health (optional)"""
    start_time = time.time()
    try:
        # Check if vector store is configured
        vector_store_url = os.getenv("VECTOR_STORE_URL")
        if not vector_store_url:
            return DependencyStatus(
                name="vector_store",
                status="healthy",
                response_time_ms=0,
                error_message="Not configured (optional)"
            )
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{vector_store_url}/health")
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                return DependencyStatus(
                    name="vector_store",
                    status="healthy",
                    response_time_ms=response_time_ms
                )
            else:
                return DependencyStatus(
                    name="vector_store",
                    status="unhealthy",
                    response_time_ms=response_time_ms,
                    error_message=f"HTTP {response.status_code}"
                )
    except Exception as e:
        response_time_ms = int((time.time() - start_time) * 1000)
        return DependencyStatus(
            name="vector_store",
            status="unhealthy",
            response_time_ms=response_time_ms,
            error_message=str(e)
        )

async def check_cache_redis() -> DependencyStatus:
    """Check cache/Redis health (optional)"""
    start_time = time.time()
    try:
        # Check if Redis is configured
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            return DependencyStatus(
                name="cache_redis",
                status="healthy",
                response_time_ms=0,
                error_message="Not configured (optional)"
            )
        
        # For now, return healthy if configured
        # In production, this would check Redis connectivity
        response_time_ms = int((time.time() - start_time) * 1000)
        return DependencyStatus(
            name="cache_redis",
            status="healthy",
            response_time_ms=response_time_ms
        )
    except Exception as e:
        response_time_ms = int((time.time() - start_time) * 1000)
        return DependencyStatus(
            name="cache_redis",
            status="unhealthy",
            response_time_ms=response_time_ms,
            error_message=str(e)
        )

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check endpoint for frontend dashboard."""
    import time
    
    start_time = time.time()
    
    try:
        # Basic detailed health check
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Mock metrics for now - in production these would come from actual metrics collection
        mock_metrics = {
            "query_intelligence": {"total_requests": 0},
            "orchestration": {"avg_duration": 0.0},
            "system": {"error_rate": 0.0}
        }
        
        # Compile detailed health report
        health_report = {
            "status": "ok",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "response_time_ms": response_time_ms,
            "overall_healthy": True,
            "service": "sarvanom-gateway",
            "version": "1.0.0",
            "services": {
                "gateway": {"status": "healthy", "response_time_ms": response_time_ms}
            },
            "metrics": {
                "uptime": "operational",
                "last_check": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "performance": {
                "uptime_seconds": time.time() - start_time,
                "total_requests": mock_metrics.get("query_intelligence", {}).get("total_requests", 0),
                "avg_response_time": mock_metrics.get("orchestration", {}).get("avg_duration", 0),
                "error_rate": mock_metrics.get("system", {}).get("error_rate", 0.0)
            },
            "recommendations": []
        }
        
        # Add recommendations based on health status
        all_services_healthy = True  # Mock for now
        
        if not all_services_healthy:
            health_report["recommendations"].append("Some services are experiencing issues. Check service logs for details.")
        
        if mock_metrics.get("system", {}).get("error_rate", 0.0) > 0.05:
            health_report["recommendations"].append("Error rate is elevated. Consider investigating recent changes.")
        
        if mock_metrics.get("orchestration", {}).get("avg_duration", 0) > 5.0:
            health_report["recommendations"].append("Average response time is high. Consider optimizing query processing.")
        
        return health_report
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
            "status": "error",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "overall_healthy": False,
            "recommendations": ["Health check system is experiencing issues. Contact system administrator."]
        }
        )

# Search/Retrieval service endpoint
@app.get("/search")
async def search_endpoint():
    """Placeholder for search/retrieval service."""
    return {"message": "Retrieval service route"}

@app.post("/search")
async def search_post(request: SearchRequest):
    """Enhanced search endpoint with zero-budget retrieval and LLM integration."""
    
    start_time = time.time()
    
    try:
        # Record query intelligence metrics
        record_query_intelligence_metrics(
            intent_type="search",
            complexity_level="medium",  # Could be enhanced with query analysis
            domain_type="general",
            duration_seconds=0.0,  # Will be updated after processing
            cache_hit=False,  # Could be enhanced with cache checking
            cache_type="redis"
        )
        
        # First, use zero-budget retrieval to get free search results
        logger.info(f"Starting zero-budget retrieval for query: {request.query}")
        retrieval_response = await combined_search(
            query=request.query,
            k=min(request.max_results or 10, 10)
        )
        
        # Convert retrieval results to the format expected by LLM processor
        retrieval_results = []
        for result in retrieval_response.results:
            retrieval_results.append({
                "id": f"retrieval_{result.provider.value}_{len(retrieval_results)}",
                "title": result.title,
                "url": result.url,
                "snippet": result.snippet,
                "relevance_score": result.relevance_score,
                "source_type": result.provider.value,
                "publication_date": result.timestamp.isoformat(),
                "author": "Zero-Budget Retrieval",
                "citations": 0
            })
        
        # Use real LLM to enhance the search results
        llm_result = await llm_processor.search_with_ai(
            query=request.query,
            user_id=request.user_id,
            max_results=10
        )
        
        # Merge zero-budget retrieval results with LLM results
        if retrieval_results:
            # Add zero-budget results to the LLM response
            llm_result["zero_budget_results"] = retrieval_results
            llm_result["zero_budget_cache_hit"] = retrieval_response.cache_hit
            llm_result["zero_budget_providers_used"] = [p.value for p in retrieval_response.providers_used]
            llm_result["zero_budget_processing_time_ms"] = retrieval_response.processing_time_ms
            llm_result["zero_budget_trace_id"] = retrieval_response.trace_id
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Record retrieval metrics
        record_retrieval_metrics(
            source_type="zero_budget_hybrid",
            fusion_strategy="zero_budget_first",
            duration_seconds=processing_time,
            result_count=len(retrieval_results) + len(llm_result.get("results", [])),
            confidence_score=llm_result.get("confidence_score", 0.8)
        )
        
        # Record business metrics
        record_business_metrics(
            user_id=request.user_id or "anonymous",
            query_type="search",
            complexity="medium",
            response_time_seconds=processing_time,
            satisfaction_score=None  # Could be collected from user feedback
        )
        
        # Add timing information to response
        llm_result["processing_time_ms"] = int(processing_time * 1000)
        llm_result["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        llm_result["zero_budget_enabled"] = True
        
        return llm_result
        
    except Exception as e:
        logger.error(f"Search request failed: {e}")
        
        # Record error metrics
        record_business_metrics(
            user_id=request.user_id or "anonymous",
            query_type="search",
            complexity="medium",
            response_time_seconds=time.time() - start_time,
            error_type="search_failure"
        )
        
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# ============================================================================
# FILE UPLOAD ENDPOINTS - Vector DB Integration
# Following MAANG/OpenAI/Perplexity standards for document processing
# ============================================================================

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: Optional[str] = None
):
    """Upload document for vector indexing."""
    try:
        # Check if vector DB is enabled
        config = get_central_config()
        if not getattr(config, "use_vector_db", False):
            raise HTTPException(
                status_code=400, 
                detail="Vector database is disabled. Enable USE_VECTOR_DB=true to upload documents."
            )
        
        # Validate file type
        allowed_types = ["application/pdf", "text/plain", "text/markdown"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
            )
        
        # Read file content
        content = await file.read()
        
        # Process based on file type
        if file.content_type == "application/pdf":
            # Extract text from PDF
            try:
                import PyPDF2
                import io
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
            except ImportError:
                raise HTTPException(
                    status_code=500,
                    detail="PDF processing requires PyPDF2. Install with: pip install PyPDF2"
                )
        else:
            # Text or markdown file
            text_content = content.decode('utf-8')
        
        # Chunk the text
        chunks = _chunk_text(text_content, chunk_size=1000, overlap=200)
        
        # Generate embeddings and store in vector DB
        from shared.embeddings.local_embedder import embed_texts
        from shared.vectorstores.vector_store_service import ChromaVectorStore
        
        embeddings = await embed_texts(chunks)
        
        # Create vector store instance
        vector_store = ChromaVectorStore(collection_name=f"user_{user_id or 'anonymous'}")
        
        # Store documents
        from shared.vectorstores.vector_store_service import VectorDocument
        documents = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            doc = VectorDocument(
                id=f"{file.filename}_{i}",
                text=chunk,
                embedding=embedding,
                metadata={
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "user_id": user_id or "anonymous",
                    "chunk_index": i,
                    "upload_time": datetime.now().isoformat()
                }
            )
            documents.append(doc)
        
        # Upsert documents
        upserted_count = await vector_store.upsert(documents)
        
        logger.info(f"Document uploaded successfully", extra={
            "filename": file.filename,
            "user_id": user_id,
            "chunks": len(chunks),
            "upserted": upserted_count
        })
        
        return {
            "message": "Document uploaded successfully",
            "filename": file.filename,
            "chunks_processed": len(chunks),
            "chunks_stored": upserted_count,
            "collection": f"user_{user_id or 'anonymous'}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/status/vector")
async def get_vector_status():
    """Get vector database status and collection sizes."""
    try:
        config = get_central_config()
        use_vector_db = getattr(config, "use_vector_db", False)
        
        if not use_vector_db:
            return {
                "vector_db_enabled": False,
                "message": "Vector database is disabled"
            }
        
        # Get collection information
        from shared.vectorstores.vector_store_service import ChromaVectorStore
        
        collections = {}
        # This would need to be implemented based on the specific vector store
        # For now, return basic status
        
        return {
            "vector_db_enabled": True,
            "provider": config.vector_db_provider,
            "collections": collections,
            "message": "Vector database is enabled"
        }
        
    except Exception as e:
        logger.error(f"Vector status check failed: {e}")
        return {
            "vector_db_enabled": False,
            "error": str(e)
        }


def _chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings
            for i in range(end, max(start + chunk_size - 100, start), -1):
                if text[i] in '.!?':
                    end = i + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks


# ============================================================================
# SSE STREAMING ENDPOINTS - Server-Sent Events Implementation
# Following MAANG/OpenAI/Perplexity standards for real-time streaming
# ============================================================================

@app.get("/stream/search")
async def stream_search_endpoint(
    query: str,
    max_tokens: int = 1000,
    temperature: float = 0.2,
    user_id: Optional[str] = None
):
    """
    SSE streaming search endpoint with comprehensive lifecycle management.
    
    Args:
        query: Search query
        max_tokens: Maximum tokens to generate
        temperature: Generation temperature
        user_id: Optional user ID for tracking
        
    Returns:
        StreamingResponse with SSE events
    """
    try:
        # Validate query
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Sanitize query
        query = query.strip()
        if len(query) > 1000:
            raise HTTPException(status_code=400, detail="Query too long (max 1000 characters)")
        
        # Log stream start
        logger.info(f"SSE stream started for query: {query[:50]}...", extra={
            "query": query,
            "user_id": user_id,
            "max_tokens": max_tokens,
            "temperature": temperature
        })
        
        # Create SSE response
        response = await create_sse_response(
            query=query,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Add trace ID to headers
        trace_id = str(uuid.uuid4())
        response.headers["X-Trace-ID"] = trace_id
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SSE stream error: {e}")
        raise HTTPException(status_code=500, detail=f"Streaming failed: {str(e)}")

@app.get("/stream/stats")
async def get_stream_stats():
    """Get streaming statistics."""
    try:
        stats = streaming_manager.get_stream_stats()
        return {
            "status": "success",
            "data": stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get stream stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Fact-check service endpoint
@app.post("/fact-check")
async def fact_check_endpoint(request: FactCheckRequest):
    """Enhanced fact-check endpoint with real LLM integration."""
    
    start_time = time.time()
    
    try:
        # Record query intelligence metrics
        record_query_intelligence_metrics(
            intent_type="fact_check",
            complexity_level="high",  # Fact-checking is typically complex
            domain_type="validation",
            duration_seconds=0.0,  # Will be updated after processing
            cache_hit=False,
            cache_type="redis"
        )
        
        # Use real LLM to perform fact checking
        llm_result = await llm_processor.fact_check_with_ai(
            claim=request.content,
            context=request.context,
            sources=[]
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Record expert validation metrics
        record_expert_validation_metrics(
            network_type="academic,industry,ai_model",
            validation_status=llm_result.get("status", "unclear"),
            duration_seconds=processing_time,
            consensus_score=llm_result.get("consensus_score", 0.8),
            consensus_level="high" if llm_result.get("consensus_score", 0) > 0.8 else "medium",
            agreement_ratio=llm_result.get("agreeing_experts", 0) / llm_result.get("total_experts", 1)
        )
        
        # Record business metrics
        record_business_metrics(
            user_id=request.user_id or "anonymous",
            query_type="fact_check",
            complexity="high",
            response_time_seconds=processing_time,
            satisfaction_score=None
        )
        
        # Add timing information to response
        llm_result["processing_time_ms"] = int(processing_time * 1000)
        llm_result["validation_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        return llm_result
        
    except Exception as e:
        logger.error(f"Fact-check request failed: {e}")
        
        # Record error metrics
        record_business_metrics(
            user_id=request.user_id or "anonymous",
            query_type="fact_check",
            complexity="high",
            response_time_seconds=time.time() - start_time,
            error_type="fact_check_failure"
        )
        
        raise HTTPException(status_code=500, detail=f"Fact-check failed: {str(e)}")

# Synthesis service endpoint
@app.post("/synthesize")
async def synthesize_endpoint(request: SynthesisRequest):
    """Enhanced synthesis endpoint with real LLM integration."""
    import time
    from services.analytics.metrics.knowledge_platform_metrics import (
        record_query_intelligence_metrics,
        record_orchestration_metrics,
        record_business_metrics
    )
    
    start_time = time.time()
    
    try:
        # Record query intelligence metrics
        record_query_intelligence_metrics(
            intent_type="synthesis",
            complexity_level="high",  # Synthesis is typically complex
            domain_type="multi_source",
            duration_seconds=0.0,  # Will be updated after processing
            cache_hit=False,
            cache_type="redis"
        )
        
        # Use real LLM to perform synthesis
        llm_result = await llm_processor.synthesize_with_ai(
            content=request.query,
            query=request.query,
            sources=request.sources or []
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Record orchestration metrics
        from shared.core.config import get_central_config
        config = get_central_config()
        record_orchestration_metrics(
            model_type=config.openai_model,  # Use configured model
            strategy="multi_agent",
            duration_seconds=processing_time,
            fallback_used=False,
            circuit_breaker_state="closed"
        )
        
        # Record business metrics
        record_business_metrics(
            user_id=request.user_id or "anonymous",
            query_type="synthesis",
            complexity="high",
            response_time_seconds=processing_time,
            satisfaction_score=None
        )
        
        # Add timing information to response
        llm_result["processing_time_ms"] = int(processing_time * 1000)
        llm_result["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        return llm_result
        
    except Exception as e:
        logger.error(f"Synthesis request failed: {e}")
        
        # Record error metrics
        record_business_metrics(
            user_id=request.user_id or "anonymous",
            query_type="synthesis",
            complexity="high",
            response_time_seconds=time.time() - start_time,
            error_type="synthesis_failure"
        )
        
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")

# Authentication service endpoints
@app.post("/auth/login")
async def auth_login_endpoint(request: AuthRequest):
    """Placeholder for authentication service login."""
    return {
        "message": "Auth service route",
        "username": request.username
    }

@app.post("/auth/register")
async def auth_register_endpoint(request: AuthRequest):
    """Placeholder for authentication service registration."""
    return {
        "message": "Auth service registration route",
        "username": request.username
    }

# Crawler service endpoint
@app.post("/crawl")
async def crawl_endpoint(request: CrawlRequest):
    """Placeholder for crawler service."""
    return {
        "message": "Crawler service route",
        "url": request.url,
        "depth": request.depth,
        "user_id": request.user_id
    }

# Vector database service endpoint
@app.post("/vector/search")
async def vector_search_endpoint(request: VectorSearchRequest):
    """Placeholder for vector database service."""
    return {
        "message": "Vector DB service route",
        "query": request.query,
        "limit": request.limit,
        "filters": request.filters
    }

# Knowledge graph service endpoint
@app.get("/graph/context")
async def graph_context_endpoint(topic: str = "", depth: int = 2, user_id: Optional[str] = None):
    """Placeholder for knowledge graph service."""
    import random
    
    # Generate sample graph data based on topic
    main_topic = topic[:30] if topic else "Query Topic"
    
    # Create nodes
    nodes = [
        {
            "id": "main",
            "name": main_topic,
            "label": main_topic,
            "description": f"Main topic: {main_topic}",
            "type": "main",
            "weight": 1.0
        }
    ]
    
    # Add related concepts
    related_concepts = [
        f"Related Concept {i+1}" for i in range(min(depth, 3))
    ]
    
    for i, concept in enumerate(related_concepts):
        nodes.append({
            "id": f"related_{i}",
            "name": concept,
            "label": concept,
            "description": f"Related to {main_topic}",
            "type": "related",
            "weight": 0.8 - (i * 0.1)
        })
    
    # Add sub-concepts
    sub_concepts = [
        f"Sub-concept {i+1}" for i in range(min(depth * 2, 4))
    ]
    
    for i, concept in enumerate(sub_concepts):
        nodes.append({
            "id": f"sub_{i}",
            "name": concept,
            "label": concept,
            "description": f"Sub-concept of related concept",
            "type": "sub",
            "weight": 0.6 - (i * 0.1)
        })
    
    # Create edges
    edges = []
    
    # Connect main topic to related concepts
    for i in range(len(related_concepts)):
        edges.append({
            "from": "main",
            "to": f"related_{i}",
            "label": "relates to",
            "relationship": "relates to",
            "type": "strong",
            "weight": 0.9
        })
    
    # Connect related concepts to sub-concepts
    for i in range(len(sub_concepts)):
        parent_idx = i % len(related_concepts)
        edges.append({
            "from": f"related_{parent_idx}",
            "to": f"sub_{i}",
            "label": "contains",
            "relationship": "contains",
            "type": "medium",
            "weight": 0.7
        })
    
    return {
        "message": "Knowledge graph service route",
        "topic": topic,
        "depth": depth,
        "user_id": user_id,
        "nodes": nodes,
        "edges": edges,
        "total_nodes": len(nodes),
        "total_edges": len(edges)
    }

@app.post("/graph/context")
async def graph_context_post_endpoint(request: GraphContextRequest):
    """Placeholder for knowledge graph service with POST."""
    return {
        "message": "Knowledge graph service route",
        "topic": request.topic,
        "depth": request.depth,
        "user_id": request.user_id
    }

# Analytics endpoint
@app.get("/analytics")
async def analytics_endpoint():
    """Enhanced analytics endpoint with comprehensive metrics."""
    import time
    from services.analytics.metrics.knowledge_platform_metrics import get_metrics_json
    
    try:
        # Get comprehensive metrics
        metrics = get_metrics_json()
        
        # Add additional analytics data
        analytics_data = {
            "metrics": metrics,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
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
        
        return analytics_data
        
    except Exception as e:
        logger.error(f"Analytics endpoint failed: {e}")
        return {
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "error"
        }

@app.get("/analytics/summary")
async def analytics_summary_endpoint(time_range: str = "30d"):
    """Enhanced analytics summary endpoint with time-based filtering."""
    import time
    from services.analytics.metrics.knowledge_platform_metrics import get_metrics_json
    
    try:
        # Get metrics with time filtering (placeholder implementation)
        metrics = get_metrics_json()
        
        # Calculate summary statistics
        summary = {
            "time_range": time_range,
            "total_queries": metrics.get("query_intelligence", {}).get("total_requests", 0),
            "average_response_time": metrics.get("orchestration", {}).get("avg_duration", 0),
            "success_rate": 0.95,  # Placeholder - could be calculated from metrics
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
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Analytics summary failed: {e}")
        return {
            "error": str(e),
            "time_range": time_range,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "error"
        }

@app.post("/analytics/track")
async def analytics_track_endpoint():
    """Enhanced analytics tracking endpoint for custom events."""
    from pydantic import BaseModel
    from typing import Dict, Any, Optional
    
    class TrackingEvent(BaseModel):
        event_type: str
        user_id: Optional[str] = None
        session_id: Optional[str] = None
        properties: Optional[Dict[str, Any]] = None
        timestamp: Optional[str] = None
    
    async def track_event(event: TrackingEvent):
        """Track a custom analytics event."""
        import time
        from services.analytics.metrics.knowledge_platform_metrics import record_business_metrics
        
        try:
            # Record business metrics for the event
            record_business_metrics(
                user_id=event.user_id or "anonymous",
                query_type=event.event_type,
                complexity="medium",
                response_time_seconds=0.0,
                satisfaction_score=None
            )
            
            # Log the event
            logger.info(f"Tracked event: {event.event_type} for user: {event.user_id}")
            
            return {
                "status": "success",
                "event_id": f"event_{int(time.time())}",
                "timestamp": event.timestamp or time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Event tracking failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    return {
        "message": "Analytics tracking endpoint",
        "supported_events": [
            "page_view",
            "button_click", 
            "form_submit",
            "search_query",
            "result_view",
            "feedback_submit",
            "error_occurred"
        ],
        "usage": "POST with TrackingEvent model to track custom events"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "message": "Universal Knowledge Platform API Gateway",
        "version": "1.0.0",
        "services": [
            "search",
            "fact-check", 
            "synthesize",
            "auth",
            "crawl",
            "vector",
            "graph",
            "analytics"
        ],
        "health": "/health",
        "ready": "/ready",
        "version_info": "/version"
    }

# Health and Readiness Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Liveness probe - basic health check"""
    trace_id = str(uuid.uuid4())
    
    response = HealthResponse(
        status="healthy",
        uptime_s=time.time() - startup_time,
        version="1.0.0",
        git_sha=get_git_sha(),
        build_time=get_build_time()
    )
    
    # Add trace_id to response headers
    from fastapi.responses import JSONResponse
    return JSONResponse(
        content=response.model_dump(),
        headers={"X-Trace-ID": trace_id}
    )

@app.get("/ready", response_model=ReadinessResponse)
async def readiness_check():
    """Readiness probe - check downstream dependencies"""
    trace_id = str(uuid.uuid4())
    
    # Check all dependencies
    dependencies = await asyncio.gather(
        check_crud_service(),
        check_retrieval_service(),
        check_synthesis_service(),
        check_vector_store(),
        check_cache_redis(),
        return_exceptions=True
    )
    
    # Handle any exceptions in dependency checks
    processed_dependencies = []
    error_count = 0
    
    for dep in dependencies:
        if isinstance(dep, Exception):
            processed_dependencies.append(DependencyStatus(
                name="unknown",
                status="unhealthy",
                error_message=str(dep)
            ))
            error_count += 1
        else:
            processed_dependencies.append(dep)
            if dep.status != "healthy":
                error_count += 1
    
    # Determine overall status
    overall_status = "ready" if error_count == 0 else "not_ready"
    
    response = ReadinessResponse(
        status=overall_status,
        uptime_s=time.time() - startup_time,
        dependencies=processed_dependencies,
        error_count=error_count
    )
    
    # Add trace_id to response headers
    from fastapi.responses import JSONResponse
    return JSONResponse(
        content=response.model_dump(),
        headers={"X-Trace-ID": trace_id}
    )

@app.get("/version", response_model=VersionResponse)
async def version_info():
    """Get version information including git SHA and build time"""
    trace_id = str(uuid.uuid4())
    
    response = VersionResponse(
        version="1.0.0",
        git_sha=get_git_sha(),
        build_time=get_build_time(),
        environment=os.getenv("ENVIRONMENT", "development")
    )
    
    # Add trace_id to response headers
    from fastapi.responses import JSONResponse
    return JSONResponse(
        content=response.dict(),
        headers={"X-Trace-ID": trace_id}
    )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found", 
            "message": "The requested endpoint does not exist",
            "path": str(request.url.path),
            "method": request.method
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error", 
            "message": "An unexpected error occurred",
            "path": str(request.url.path),
            "method": request.method
        }
    )

# Advanced Features Endpoints

# Cache Management Endpoints
@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    try:
        stats = await cache_manager.get_stats()
        return {
            "status": "success",
            "cache_stats": stats
        }
    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cache/clear")
async def clear_cache():
    """Clear all cache entries"""
    try:
        await cache_manager.clear_all()
        return {
            "status": "success",
            "message": "Cache cleared successfully"
        }
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Streaming Endpoints
@app.get("/stream/search")
async def stream_search_endpoint(query: str, user_id: str = "anonymous"):
    """Stream search results using Server-Sent Events"""
    try:
        return await stream_manager.create_sse_stream(
            query=query,
            user_id=user_id,
            endpoint="search",
            llm_processor=llm_processor
        )
    except Exception as e:
        logger.error(f"Stream search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/search")
async def websocket_search_endpoint(websocket: WebSocket):
    """WebSocket endpoint for streaming search results"""
    try:
        await stream_manager.create_websocket_stream(
            websocket=websocket,
            query="",  # Will be received via WebSocket
            user_id="anonymous",
            endpoint="search",
            llm_processor=llm_processor
        )
    except Exception as e:
        logger.error(f"WebSocket search error: {e}")

@app.get("/stream/fact-check")
async def stream_fact_check_endpoint(claim: str, user_id: str = "anonymous"):
    """Stream fact-check results using Server-Sent Events"""
    try:
        return await stream_manager.create_sse_stream(
            query=claim,
            user_id=user_id,
            endpoint="fact_check",
            llm_processor=llm_processor
        )
    except Exception as e:
        logger.error(f"Stream fact-check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background Processing Endpoints
@app.post("/background/task")
async def submit_background_task(
    task_type: str,
    query: str,
    user_id: str = "anonymous",
    priority: str = "normal"
):
    """Submit a background task for processing"""
    try:
        # Map string to enum
        task_type_enum = TaskType(task_type.lower())
        
        # Map priority string to enum value
        priority_map = {
            "critical": TaskPriority.CRITICAL,
            "high": TaskPriority.HIGH,
            "normal": TaskPriority.NORMAL,
            "low": TaskPriority.LOW,
            "bulk": TaskPriority.BULK
        }
        priority_enum = priority_map.get(priority.lower(), TaskPriority.NORMAL)
        
        task_id = await background_processor.submit_task(
            task_type=task_type_enum,
            query=query,
            user_id=user_id,
            endpoint=task_type.lower(),
            priority=priority_enum
        )
        
        return {
            "status": "success",
            "task_id": task_id,
            "message": f"Background task submitted: {task_id}"
        }
    except Exception as e:
        logger.error(f"Background task submission error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/background/task/{task_id}")
async def get_background_task_status(task_id: str):
    """Get background task status and result"""
    try:
        task_info = await background_processor.get_task_status(task_id)
        if not task_info:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "status": "success",
            "task_info": task_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Background task status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/background/task/{task_id}")
async def cancel_background_task(task_id: str):
    """Cancel a background task"""
    try:
        cancelled = await background_processor.cancel_task(task_id)
        if not cancelled:
            raise HTTPException(status_code=404, detail="Task not found or cannot be cancelled")
        
        return {
            "status": "success",
            "message": f"Task {task_id} cancelled successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Background task cancellation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/background/stats")
async def background_stats():
    """Get background processing statistics"""
    try:
        stats = await background_processor.get_queue_stats()
        return {
            "status": "success",
            "background_stats": stats
        }
    except Exception as e:
        logger.error(f"Background stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Prompt Optimization Endpoints
@app.post("/optimize/prompt")
async def optimize_prompt_endpoint(
    prompt: str,
    prompt_type: str = "search",
    complexity: str = "medium"
):
    """Optimize a prompt for better performance"""
    try:
        # Map strings to enums
        prompt_type_enum = PromptType(prompt_type.lower())
        complexity_enum = PromptComplexity(complexity.lower())
        
        optimized = await prompt_optimizer.optimize_prompt(
            prompt=prompt,
            prompt_type=prompt_type_enum,
            complexity=complexity_enum
        )
        
        return {
            "status": "success",
            "optimized_prompt": optimized.to_dict()
        }
    except Exception as e:
        logger.error(f"Prompt optimization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/optimize/stats")
async def prompt_optimization_stats():
    """Get prompt optimization statistics"""
    try:
        stats = await prompt_optimizer.get_optimization_stats()
        return {
            "status": "success",
            "optimization_stats": stats
        }
    except Exception as e:
        logger.error(f"Prompt optimization stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize/clear-cache")
async def clear_prompt_cache():
    """Clear prompt optimization cache"""
    try:
        await prompt_optimizer.clear_cache()
        return {
            "status": "success",
            "message": "Prompt optimization cache cleared"
        }
    except Exception as e:
        logger.error(f"Prompt cache clear error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System Status Endpoint
@app.get("/system/status")
async def system_status():
    """Get comprehensive system status including all advanced features"""
    try:
        # Get stats from all systems
        cache_stats = await cache_manager.get_stats()
        stream_stats = await stream_manager.get_metrics()
        background_stats = await background_processor.get_queue_stats()
        optimization_stats = await prompt_optimizer.get_optimization_stats()
        
        return {
            "status": "success",
            "system_status": {
                "cache": cache_stats,
                "streaming": stream_stats,
                "background_processing": background_stats,
                "prompt_optimization": optimization_stats,
                "huggingface": {
                    "device": huggingface_integration.device,
                    "loaded_models": len(huggingface_integration.models),
                    "loaded_pipelines": len(huggingface_integration.pipelines),
                    "embedding_model_loaded": huggingface_integration.embedding_model is not None,
                    "auth_status": await huggingface_integration.get_auth_status()
                },
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"System status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# HuggingFace Integration Endpoints
@app.post("/huggingface/generate")
async def huggingface_text_generation(
    prompt: str,
    model_name: str = "distilgpt2",
    max_length: int = 100,
    temperature: float = 0.7
):
    """Generate text using HuggingFace models"""
    try:
        result = await huggingface_integration.generate_text(
            prompt=prompt,
            model_name=model_name,
            max_length=max_length,
            temperature=temperature
        )
        
        return {
            "status": "success",
            "generated_text": result.result,
            "metadata": result.metadata,
            "processing_time": result.processing_time
        }
    except Exception as e:
        logger.error(f"HuggingFace text generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/huggingface/embeddings")
async def huggingface_embeddings(
    texts: List[str],
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
):
    """Get embeddings for texts using HuggingFace models"""
    try:
        result = await huggingface_integration.get_embeddings(
            texts=texts,
            model_name=model_name
        )
        
        return {
            "status": "success",
            "embeddings": result.result,
            "metadata": result.metadata,
            "processing_time": result.processing_time
        }
    except Exception as e:
        logger.error(f"HuggingFace embeddings error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/huggingface/sentiment")
async def huggingface_sentiment_analysis(
    text: str,
    model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"
):
    """Analyze sentiment using HuggingFace models"""
    try:
        result = await huggingface_integration.analyze_sentiment(
            text=text,
            model_name=model_name
        )
        
        return {
            "status": "success",
            "sentiment": result.result,
            "metadata": result.metadata,
            "processing_time": result.processing_time
        }
    except Exception as e:
        logger.error(f"HuggingFace sentiment analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/huggingface/summarize")
async def huggingface_summarization(
    text: str,
    model_name: str = "facebook/bart-large-cnn",
    max_length: int = 130
):
    """Summarize text using HuggingFace models"""
    try:
        result = await huggingface_integration.summarize_text(
            text=text,
            model_name=model_name,
            max_length=max_length
        )
        
        return {
            "status": "success",
            "summary": result.result,
            "metadata": result.metadata,
            "processing_time": result.processing_time
        }
    except Exception as e:
        logger.error(f"HuggingFace summarization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/huggingface/translate")
async def huggingface_translation(
    text: str,
    target_language: str = "es",
    model_name: str = "Helsinki-NLP/opus-mt-en-es"
):
    """Translate text using HuggingFace models"""
    try:
        result = await huggingface_integration.translate_text(
            text=text,
            target_language=target_language,
            model_name=model_name
        )
        return {
            "status": "success",
            "translation": result.result,
            "metadata": result.metadata,
            "processing_time": result.processing_time
        }
    except Exception as e:
        logger.error(f"HuggingFace translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/huggingface/entities")
async def huggingface_entity_extraction(
    text: str,
    model_name: str = "dbmdz/bert-large-cased-finetuned-conll03-english"
):
    """Extract named entities using HuggingFace models"""
    try:
        result = await huggingface_integration.extract_entities(
            text=text,
            model_name=model_name
        )
        
        return {
            "status": "success",
            "entities": result.result,
            "metadata": result.metadata,
            "processing_time": result.processing_time
        }
    except Exception as e:
        logger.error(f"HuggingFace entity extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/huggingface/qa")
async def huggingface_question_answering(
    question: str,
    context: str,
    model_name: str = "distilbert-base-cased-distilled-squad"
):
    """Answer questions using HuggingFace models"""
    try:
        result = await huggingface_integration.answer_question(
            question=question,
            context=context,
            model_name=model_name
        )
        
        return {
            "status": "success",
            "answer": result.result,
            "metadata": result.metadata,
            "processing_time": result.processing_time
        }
    except Exception as e:
        logger.error(f"HuggingFace question answering error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/huggingface/similarity")
async def huggingface_text_similarity(
    text1: str,
    text2: str,
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
):
    """Calculate text similarity using HuggingFace models"""
    try:
        result = await huggingface_integration.calculate_similarity(
            text1=text1,
            text2=text2,
            model_name=model_name
        )
        
        return {
            "status": "success",
            "similarity": result.result,
            "metadata": result.metadata,
            "processing_time": result.processing_time
        }
    except Exception as e:
        logger.error(f"HuggingFace similarity calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/huggingface/zero-shot")
async def huggingface_zero_shot_classification(
    text: str,
    candidate_labels: List[str],
    model_name: str = "facebook/bart-large-mnli"
):
    """Perform zero-shot classification using HuggingFace models"""
    try:
        result = await huggingface_integration.zero_shot_classification(
            text=text,
            candidate_labels=candidate_labels,
            model_name=model_name
        )
        
        return {
            "status": "success",
            "classification": result.result,
            "metadata": result.metadata,
            "processing_time": result.processing_time
        }
    except Exception as e:
        logger.error(f"HuggingFace zero-shot classification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/huggingface/models")
async def huggingface_available_models():
    """Get available HuggingFace models"""
    try:
        models = await huggingface_integration.get_available_models()
        
        return {
            "status": "success",
            "models": models,
            "device": huggingface_integration.device,
            "loaded_models": len(huggingface_integration.models),
            "loaded_pipelines": len(huggingface_integration.pipelines)
        }
    except Exception as e:
        logger.error(f"HuggingFace models error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/huggingface/model/{model_name}")
async def huggingface_model_info(model_name: str):
    """Get information about a specific HuggingFace model"""
    try:
        model_info = await huggingface_integration.get_model_info(model_name)
        
        return {
            "status": "success",
            "model_info": model_info
        }
    except Exception as e:
        logger.error(f"HuggingFace model info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CRUD SERVICE CLIENT - Microservice Architecture Implementation
# MAANG/OpenAI/Perplexity Standards with Latest Stable Technologies
# ============================================================================

# Initialize CRUD service client
crud_client = ServiceClientFactory.create_crud_client()

# Initialize streaming manager
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    await streaming_manager.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup services on shutdown."""
    await streaming_manager.close()

# ============================================================================
# CACHE CRUD OPERATIONS - Microservice Architecture
# ============================================================================

@app.get("/cache/{key}")
async def get_cache_entry(key: str):
    """GET - Retrieve a cache entry via CRUD microservice"""
    try:
        response = await crud_client.get_resource("cache", key)
        return response
    except Exception as e:
        logger.error(f"Cache GET error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cache")
async def create_cache_entry(entry: CacheEntry):
    """POST - Create a new cache entry via CRUD microservice"""
    try:
        response = await crud_client.create_resource("cache", entry.dict())
        return response
    except Exception as e:
        logger.error(f"Cache POST error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/cache/{key}")
async def update_cache_entry(key: str, entry: CacheEntry):
    """PUT - Update an existing cache entry via CRUD microservice"""
    try:
        response = await crud_client.update_resource("cache", key, entry.dict())
        return response
    except Exception as e:
        logger.error(f"Cache PUT error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/cache/{key}")
async def delete_cache_entry(key: str):
    """DELETE - Remove a cache entry via CRUD microservice"""
    try:
        response = await crud_client.delete_resource("cache", key)
        return response
    except Exception as e:
        logger.error(f"Cache DELETE error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cache")
async def list_cache_entries(skip: int = 0, limit: int = 100):
    """GET - List all cache entries with pagination via CRUD microservice"""
    try:
        pagination = PaginationParams(skip=skip, limit=limit)
        response = await crud_client.list_resources("cache", pagination)
        return response
    except Exception as e:
        logger.error(f"Cache list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# USER PROFILE CRUD OPERATIONS - Microservice Architecture
# ============================================================================

@app.get("/users/{user_id}")
async def get_user_profile(user_id: str):
    """GET - Retrieve a user profile via CRUD microservice"""
    try:
        response = await crud_client.get_resource("user", user_id)
        return response
    except Exception as e:
        logger.error(f"User GET error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users")
async def create_user_profile(user: UserProfile):
    """POST - Create a new user profile via CRUD microservice"""
    try:
        response = await crud_client.create_resource("user", user.dict())
        return response
    except Exception as e:
        logger.error(f"User POST error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/users/{user_id}")
async def update_user_profile(user_id: str, user: UserProfile):
    """PUT - Update an existing user profile via CRUD microservice"""
    try:
        response = await crud_client.update_resource("user", user_id, user.dict())
        return response
    except Exception as e:
        logger.error(f"User PUT error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/users/{user_id}")
async def delete_user_profile(user_id: str):
    """DELETE - Remove a user profile via CRUD microservice"""
    try:
        response = await crud_client.delete_resource("user", user_id)
        return response
    except Exception as e:
        logger.error(f"User DELETE error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users")
async def list_user_profiles(skip: int = 0, limit: int = 100):
    """GET - List all user profiles with pagination via CRUD microservice"""
    try:
        pagination = PaginationParams(skip=skip, limit=limit)
        response = await crud_client.list_resources("user", pagination)
        return response
    except Exception as e:
        logger.error(f"User list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MODEL CONFIGURATION CRUD OPERATIONS - Microservice Architecture
# ============================================================================

@app.get("/models/{model_name}")
async def get_model_configuration(model_name: str):
    """GET - Retrieve a model configuration via CRUD microservice"""
    try:
        response = await crud_client.get_resource("model", model_name)
        return response
    except Exception as e:
        logger.error(f"Model GET error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/models")
async def create_model_configuration(model: ModelConfiguration):
    """POST - Create a new model configuration via CRUD microservice"""
    try:
        response = await crud_client.create_resource("model", model.dict())
        return response
    except Exception as e:
        logger.error(f"Model POST error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/models/{model_name}")
async def update_model_configuration(model_name: str, model: ModelConfiguration):
    """PUT - Update an existing model configuration via CRUD microservice"""
    try:
        response = await crud_client.update_resource("model", model_name, model.dict())
        return response
    except Exception as e:
        logger.error(f"Model PUT error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/models/{model_name}")
async def delete_model_configuration(model_name: str):
    """DELETE - Remove a model configuration via CRUD microservice"""
    try:
        response = await crud_client.delete_resource("model", model_name)
        return response
    except Exception as e:
        logger.error(f"Model DELETE error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_model_configurations(skip: int = 0, limit: int = 100):
    """GET - List all model configurations with pagination via CRUD microservice"""
    try:
        pagination = PaginationParams(skip=skip, limit=limit)
        response = await crud_client.list_resources("model", pagination)
        return response
    except Exception as e:
        logger.error(f"Model list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DATASET CRUD OPERATIONS - Microservice Architecture
# ============================================================================

@app.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str):
    """GET - Retrieve a dataset via CRUD microservice"""
    try:
        response = await crud_client.get_resource("dataset", dataset_id)
        return response
    except Exception as e:
        logger.error(f"Dataset GET error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/datasets")
async def create_dataset(dataset: Dataset):
    """POST - Create a new dataset via CRUD microservice"""
    try:
        response = await crud_client.create_resource("dataset", dataset.dict())
        return response
    except Exception as e:
        logger.error(f"Dataset POST error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/datasets/{dataset_id}")
async def update_dataset(dataset_id: str, dataset: Dataset):
    """PUT - Update an existing dataset via CRUD microservice"""
    try:
        response = await crud_client.update_resource("dataset", dataset_id, dataset.dict())
        return response
    except Exception as e:
        logger.error(f"Dataset PUT error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/datasets/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """DELETE - Remove a dataset via CRUD microservice"""
    try:
        response = await crud_client.delete_resource("dataset", dataset_id)
        return response
    except Exception as e:
        logger.error(f"Dataset DELETE error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/datasets")
async def list_datasets(skip: int = 0, limit: int = 100):
    """GET - List all datasets with pagination via CRUD microservice"""
    try:
        pagination = PaginationParams(skip=skip, limit=limit)
        response = await crud_client.list_resources("dataset", pagination)
        return response
    except Exception as e:
        logger.error(f"Dataset list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SYSTEM SETTINGS CRUD OPERATIONS - Microservice Architecture
# ============================================================================

@app.get("/settings/{setting_key}")
async def get_system_setting(setting_key: str):
    """GET - Retrieve a system setting via CRUD microservice"""
    try:
        response = await crud_client.get_resource("setting", setting_key)
        return response
    except Exception as e:
        logger.error(f"Setting GET error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/settings")
async def create_system_setting(setting: SystemSetting):
    """POST - Create a new system setting via CRUD microservice"""
    try:
        response = await crud_client.create_resource("setting", setting.dict())
        return response
    except Exception as e:
        logger.error(f"Setting POST error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/settings/{setting_key}")
async def update_system_setting(setting_key: str, setting: SystemSetting):
    """PUT - Update an existing system setting via CRUD microservice"""
    try:
        response = await crud_client.update_resource("setting", setting_key, setting.dict())
        return response
    except Exception as e:
        logger.error(f"Setting PUT error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/settings/{setting_key}")
async def delete_system_setting(setting_key: str):
    """DELETE - Remove a system setting via CRUD microservice"""
    try:
        response = await crud_client.delete_resource("setting", setting_key)
        return response
    except Exception as e:
        logger.error(f"Setting DELETE error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/settings")
async def list_system_settings(skip: int = 0, limit: int = 100, category: Optional[str] = None):
    """GET - List all system settings with pagination and optional category filter via CRUD microservice"""
    try:
        pagination = PaginationParams(skip=skip, limit=limit)
        filters = FilterParams(category=category) if category else None
        response = await crud_client.list_resources("setting", pagination, filters)
        return response
    except Exception as e:
        logger.error(f"Setting list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 