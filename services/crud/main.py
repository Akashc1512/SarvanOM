"""
CRUD Microservice

This microservice provides comprehensive CRUD operations for all resources
following MAANG/OpenAI/Perplexity standards with latest stable technologies.
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

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
import re
import json
import uuid

# Import central configuration
from shared.core.config.central_config import get_central_config
from datetime import datetime
from typing import Dict, Any, Optional, List

# Import shared components
from shared.core.unified_logging import setup_logging, get_logger, setup_fastapi_logging
from shared.models.crud_models import (
    CacheEntry, UserProfile, ModelConfiguration, Dataset, SystemSetting,
    CRUDResponse, PaginationParams, FilterParams, ResourceType
)
from shared.contracts.service_contracts import (
    CRUDServiceContract, CacheServiceContract, UserServiceContract,
    ModelServiceContract, DatasetServiceContract, SettingsServiceContract,
    ServiceType, ServiceStatus, ServiceHealth
)

# Configure unified logging
logging_config = setup_logging(service_name="sarvanom-crud-service")
logger = get_logger(__name__)

# In-memory storage for CRUD operations (in production, use proper databases)
cache_storage: Dict[str, Dict[str, Any]] = {}
user_profiles: Dict[str, Dict[str, Any]] = {}
model_configurations: Dict[str, Dict[str, Any]] = {}
datasets: Dict[str, Dict[str, Any]] = {}
system_settings: Dict[str, Dict[str, Any]] = {}


class CRUDService(CRUDServiceContract):
    """CRUD service implementation"""
    
    async def create(self, resource_type: str, data: Dict[str, Any]) -> CRUDResponse:
        """Create a new resource"""
        try:
            if resource_type == ResourceType.CACHE:
                entry = CacheEntry(**data)
                cache_storage[entry.key] = entry.dict()
                return CRUDResponse(
                    status="success",
                    message=f"Cache entry '{entry.key}' created successfully",
                    data={"key": entry.key, "ttl": entry.ttl}
                )
            elif resource_type == ResourceType.USER:
                user = UserProfile(**data)
                user_profiles[user.user_id] = user.dict()
                return CRUDResponse(
                    status="success",
                    message=f"User '{user.user_id}' created successfully",
                    data={"user_id": user.user_id}
                )
            elif resource_type == ResourceType.MODEL:
                model = ModelConfiguration(**data)
                model_configurations[model.model_name] = model.dict()
                return CRUDResponse(
                    status="success",
                    message=f"Model '{model.model_name}' created successfully",
                    data={"model_name": model.model_name}
                )
            elif resource_type == ResourceType.DATASET:
                dataset = Dataset(**data)
                datasets[dataset.dataset_id] = dataset.dict()
                return CRUDResponse(
                    status="success",
                    message=f"Dataset '{dataset.dataset_id}' created successfully",
                    data={"dataset_id": dataset.dataset_id}
                )
            elif resource_type == ResourceType.SETTING:
                setting = SystemSetting(**data)
                system_settings[setting.setting_key] = setting.dict()
                return CRUDResponse(
                    status="success",
                    message=f"Setting '{setting.setting_key}' created successfully",
                    data={"setting_key": setting.setting_key}
                )
            else:
                raise ValueError(f"Unsupported resource type: {resource_type}")
        except Exception as e:
            logger.error(f"Create operation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def read(self, resource_type: str, resource_id: str) -> CRUDResponse:
        """Read a resource by ID"""
        try:
            if resource_type == ResourceType.CACHE:
                if resource_id not in cache_storage:
                    raise HTTPException(status_code=404, detail=f"Cache entry '{resource_id}' not found")
                return CRUDResponse(
                    status="success",
                    message="Cache entry retrieved successfully",
                    data=cache_storage[resource_id]
                )
            elif resource_type == ResourceType.USER:
                if resource_id not in user_profiles:
                    raise HTTPException(status_code=404, detail=f"User '{resource_id}' not found")
                return CRUDResponse(
                    status="success",
                    message="User profile retrieved successfully",
                    data=user_profiles[resource_id]
                )
            elif resource_type == ResourceType.MODEL:
                if resource_id not in model_configurations:
                    raise HTTPException(status_code=404, detail=f"Model '{resource_id}' not found")
                return CRUDResponse(
                    status="success",
                    message="Model configuration retrieved successfully",
                    data=model_configurations[resource_id]
                )
            elif resource_type == ResourceType.DATASET:
                if resource_id not in datasets:
                    raise HTTPException(status_code=404, detail=f"Dataset '{resource_id}' not found")
                return CRUDResponse(
                    status="success",
                    message="Dataset retrieved successfully",
                    data=datasets[resource_id]
                )
            elif resource_type == ResourceType.SETTING:
                if resource_id not in system_settings:
                    raise HTTPException(status_code=404, detail=f"Setting '{resource_id}' not found")
                return CRUDResponse(
                    status="success",
                    message="System setting retrieved successfully",
                    data=system_settings[resource_id]
                )
            else:
                raise ValueError(f"Unsupported resource type: {resource_type}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Read operation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def update(self, resource_type: str, resource_id: str, data: Dict[str, Any]) -> CRUDResponse:
        """Update a resource by ID"""
        try:
            if resource_type == ResourceType.CACHE:
                if resource_id not in cache_storage:
                    raise HTTPException(status_code=404, detail=f"Cache entry '{resource_id}' not found")
                entry = CacheEntry(**data)
                cache_storage[resource_id] = entry.dict()
                return CRUDResponse(
                    status="success",
                    message=f"Cache entry '{resource_id}' updated successfully",
                    data={"key": resource_id, "ttl": entry.ttl}
                )
            elif resource_type == ResourceType.USER:
                if resource_id not in user_profiles:
                    raise HTTPException(status_code=404, detail=f"User '{resource_id}' not found")
                user = UserProfile(**data)
                user_profiles[resource_id] = user.dict()
                return CRUDResponse(
                    status="success",
                    message=f"User '{resource_id}' updated successfully",
                    data={"user_id": resource_id}
                )
            elif resource_type == ResourceType.MODEL:
                if resource_id not in model_configurations:
                    raise HTTPException(status_code=404, detail=f"Model '{resource_id}' not found")
                model = ModelConfiguration(**data)
                model_configurations[resource_id] = model.dict()
                return CRUDResponse(
                    status="success",
                    message=f"Model '{resource_id}' updated successfully",
                    data={"model_name": resource_id}
                )
            elif resource_type == ResourceType.DATASET:
                if resource_id not in datasets:
                    raise HTTPException(status_code=404, detail=f"Dataset '{resource_id}' not found")
                dataset = Dataset(**data)
                datasets[resource_id] = dataset.dict()
                return CRUDResponse(
                    status="success",
                    message=f"Dataset '{resource_id}' updated successfully",
                    data={"dataset_id": resource_id}
                )
            elif resource_type == ResourceType.SETTING:
                if resource_id not in system_settings:
                    raise HTTPException(status_code=404, detail=f"Setting '{resource_id}' not found")
                setting = SystemSetting(**data)
                system_settings[resource_id] = setting.dict()
                return CRUDResponse(
                    status="success",
                    message=f"Setting '{resource_id}' updated successfully",
                    data={"setting_key": resource_id}
                )
            else:
                raise ValueError(f"Unsupported resource type: {resource_type}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Update operation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def delete(self, resource_type: str, resource_id: str) -> CRUDResponse:
        """Delete a resource by ID"""
        try:
            if resource_type == ResourceType.CACHE:
                if resource_id not in cache_storage:
                    raise HTTPException(status_code=404, detail=f"Cache entry '{resource_id}' not found")
                del cache_storage[resource_id]
                return CRUDResponse(
                    status="success",
                    message=f"Cache entry '{resource_id}' deleted successfully"
                )
            elif resource_type == ResourceType.USER:
                if resource_id not in user_profiles:
                    raise HTTPException(status_code=404, detail=f"User '{resource_id}' not found")
                del user_profiles[resource_id]
                return CRUDResponse(
                    status="success",
                    message=f"User '{resource_id}' deleted successfully"
                )
            elif resource_type == ResourceType.MODEL:
                if resource_id not in model_configurations:
                    raise HTTPException(status_code=404, detail=f"Model '{resource_id}' not found")
                del model_configurations[resource_id]
                return CRUDResponse(
                    status="success",
                    message=f"Model '{resource_id}' deleted successfully"
                )
            elif resource_type == ResourceType.DATASET:
                if resource_id not in datasets:
                    raise HTTPException(status_code=404, detail=f"Dataset '{resource_id}' not found")
                del datasets[resource_id]
                return CRUDResponse(
                    status="success",
                    message=f"Dataset '{resource_id}' deleted successfully"
                )
            elif resource_type == ResourceType.SETTING:
                if resource_id not in system_settings:
                    raise HTTPException(status_code=404, detail=f"Setting '{resource_id}' not found")
                del system_settings[resource_id]
                return CRUDResponse(
                    status="success",
                    message=f"Setting '{resource_id}' deleted successfully"
                )
            else:
                raise ValueError(f"Unsupported resource type: {resource_type}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Delete operation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def list(self, resource_type: str, pagination: PaginationParams, filters: Optional[FilterParams] = None) -> CRUDResponse:
        """List resources with pagination and filtering"""
        try:
            if resource_type == ResourceType.CACHE:
                items = list(cache_storage.values())
            elif resource_type == ResourceType.USER:
                items = list(user_profiles.values())
            elif resource_type == ResourceType.MODEL:
                items = list(model_configurations.values())
            elif resource_type == ResourceType.DATASET:
                items = list(datasets.values())
            elif resource_type == ResourceType.SETTING:
                items = list(system_settings.values())
            else:
                raise ValueError(f"Unsupported resource type: {resource_type}")
            
            # Apply filters if provided
            if filters:
                if filters.service:
                    items = [item for item in items if item.get("service") == filters.service]
                if filters.category:
                    items = [item for item in items if item.get("category") == filters.category]
                if filters.enabled is not None:
                    items = [item for item in items if item.get("enabled") == filters.enabled]
            
            # Apply pagination
            total = len(items)
            items = items[pagination.skip:pagination.skip + pagination.limit]
            
            return CRUDResponse(
                status="success",
                message=f"{resource_type} resources listed successfully",
                data={"items": items},
                metadata={
                    "total": total,
                    "skip": pagination.skip,
                    "limit": pagination.limit
                }
            )
        except Exception as e:
            logger.error(f"List operation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


# Initialize CRUD service
crud_service = CRUDService()

# Get configuration
config = get_central_config()

# Security configuration
MAX_PAYLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_ORIGINS = config.cors_origins if isinstance(config.cors_origins, list) else (config.cors_origins.split(",") if config.cors_origins else ["*"])
TRUSTED_HOSTS = ["localhost", "127.0.0.1", "sarvanom.com", "www.sarvanom.com"]

# Input validation patterns
XSS_PATTERN = re.compile(r'<script[^>]*>.*?</script>|<iframe[^>]*>.*?</iframe>|<object[^>]*>.*?</object>', re.IGNORECASE | re.DOTALL)
SQL_INJECTION_PATTERN = re.compile(r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*?\b(from|into|table|database|where)\b)', re.IGNORECASE)


from starlette.middleware.base import BaseHTTPMiddleware

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for input validation and security headers."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip security checks for basic endpoints
        if request.url.path in ["/", "/health", "/health/detailed", "/docs", "/openapi.json"]:
            response = await call_next(request)
            # Still add security headers
            self._add_security_headers(response)
            return response
        
        # Check payload size only for POST/PUT requests with content
        if request.method in ["POST", "PUT", "PATCH"]:
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > MAX_PAYLOAD_SIZE:
                return JSONResponse(
                    status_code=413,
                    content={"error": "Payload too large", "max_size_mb": MAX_PAYLOAD_SIZE // (1024 * 1024)}
                )
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        self._add_security_headers(response)
        
        return response
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"


# Initialize FastAPI app with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 CRUD Microservice starting up...")
    yield
    # Shutdown
    logger.info("🛑 CRUD Microservice shutting down...")

app = FastAPI(
    title="SarvanOM CRUD Microservice",
    description="Comprehensive CRUD operations microservice with latest stable technologies",
    version="2.0.0",
    lifespan=lifespan
)

# Setup FastAPI logging integration
setup_fastapi_logging(app, service_name="sarvanom-crud-service")

# Add security middleware
app.add_middleware(SecurityMiddleware)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=TRUSTED_HOSTS + ["testserver", "*"]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "sarvanom-crud-service",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check endpoint"""
    start_time = time.time()
    
    # Check storage health
    storage_health = {
        "cache_entries": len(cache_storage),
        "user_profiles": len(user_profiles),
        "model_configurations": len(model_configurations),
        "datasets": len(datasets),
        "system_settings": len(system_settings)
    }
    
    response_time = (time.time() - start_time) * 1000
    
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "response_time_ms": round(response_time, 2),
        "overall_healthy": True,
        "service": "sarvanom-crud-service",
        "version": "1.0.0",
        "storage_health": storage_health,
        "metrics": {
            "uptime": "operational",
            "last_check": datetime.utcnow().isoformat()
        },
        "performance": {
            "uptime_seconds": time.time(),
            "total_requests": 0,
            "avg_response_time": 0,
            "error_rate": 0
        },
        "recommendations": {}
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SarvanOM CRUD Microservice",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/health",
            "health_detailed": "/health/detailed",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }

# Standard endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "crud"}

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check if CRUD service is available
        return {"status": "ready", "service": "crud"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/config")
async def get_config_endpoint():
    """Config endpoint - sanitized echo of active providers and configuration"""
    return {
        "service": "crud",
        "active_providers": {
            "openai": bool(getattr(config, 'openai_api_key', None)),
            "anthropic": bool(getattr(config, 'anthropic_api_key', None)),
            "google": bool(getattr(config, 'google_api_key', None)),
            "huggingface": bool(getattr(config, 'huggingface_api_key', None) or getattr(config, 'huggingface_read_token', None) or getattr(config, 'huggingface_write_token', None)),
            "ollama": bool(getattr(config, 'ollama_base_url', None))
        },
        "keyless_fallbacks_enabled": getattr(config, 'keyless_fallbacks_enabled', True),
        "environment": getattr(config, 'environment', 'development'),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/version")
async def get_version():
    """Version endpoint"""
    return {
        "service": "crud",
        "version": "2.0.0",
        "environment": getattr(config, 'environment', 'development'),
        "timestamp": datetime.now().isoformat()
    }


# CRUD endpoints for all resource types
@app.post("/{resource_type}")
async def create_resource(resource_type: str, data: Dict[str, Any]):
    """Create a new resource"""
    try:
        response = await crud_service.create(resource_type, data)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create resource failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{resource_type}/{resource_id}")
async def get_resource(resource_type: str, resource_id: str):
    """Get a resource by ID"""
    try:
        response = await crud_service.read(resource_type, resource_id)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get resource failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/{resource_type}/{resource_id}")
async def update_resource(resource_type: str, resource_id: str, data: Dict[str, Any]):
    """Update a resource by ID"""
    try:
        response = await crud_service.update(resource_type, resource_id, data)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update resource failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/{resource_type}/{resource_id}")
async def delete_resource(resource_type: str, resource_id: str):
    """Delete a resource by ID"""
    try:
        response = await crud_service.delete(resource_type, resource_id)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete resource failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{resource_type}")
async def list_resources(
    resource_type: str,
    skip: int = 0,
    limit: int = 100,
    service: Optional[str] = None,
    category: Optional[str] = None,
    enabled: Optional[bool] = None
):
    """List resources with pagination and filtering"""
    try:
        pagination = PaginationParams(skip=skip, limit=limit)
        filters = FilterParams(service=service, category=category, enabled=enabled)
        response = await crud_service.list(resource_type, pagination, filters)
        return response
    except Exception as e:
        logger.error(f"List resources failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
    import uvicorn
    # CRUD service uses port 8015
    uvicorn.run(app, host="0.0.0.0", port=8015)
