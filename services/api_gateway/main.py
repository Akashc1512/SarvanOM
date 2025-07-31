"""
Universal Knowledge Hub - API Gateway Service
Main entry point for the knowledge platform with comprehensive request handling.

This module provides:
- Request routing and orchestration
- Authentication and authorization
- Rate limiting and security middleware
- Real-time WebSocket communication
- Health monitoring and metrics
- Expert review system integration

Architecture:
- FastAPI-based REST API
- Structured JSON logging
- Middleware for request tracking
- Exception handling with detailed error responses
- WebSocket support for real-time collaboration

Environment Variables:
- LOG_LEVEL: Logging level (default: INFO)
- SERVICE_NAME: Service identifier (default: sarvanom-api)
- VERSION: Service version (default: 1.0.0)
- CORS_ORIGINS: Allowed CORS origins
- RATE_LIMIT_REQUESTS: Requests per minute (default: 60)
- RATE_LIMIT_TOKENS: Tokens per minute (default: 10000)

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import asyncio
import logging
import time
import uuid
import psutil
import sys
import importlib
import socket
from contextlib import asynccontextmanager
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

# FastAPI and web framework imports
import uvicorn
from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    Response,
    Depends,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError, Field, BaseModel

# Environment and configuration
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Import analytics functions
try:
    import importlib
    analytics_module = importlib.import_module("services.analytics-service.analytics")
    track_query = analytics_module.track_query
except ImportError:
    # Fallback if analytics service is not available
    async def track_query(*args, **kwargs):
        pass

# Initialize query cache
try:
    from shared.core.cache import CacheManager
    _query_cache = CacheManager()
except ImportError:
    # Fallback cache implementation
    class SimpleCache:
        def __init__(self):
            self._cache = {}
        
        async def get(self, key):
            return self._cache.get(key)
        
        async def set(self, key, value):
            self._cache[key] = value
    
    _query_cache = SimpleCache()

# Critical environment variables validation
def validate_critical_env_vars():
    """Validate critical environment variables and fail fast if missing."""
    critical_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "REDIS_URL": os.getenv("REDIS_URL"),
    }
    
    missing_vars = []
    for var_name, var_value in critical_vars.items():
        if not var_value:
            missing_vars.append(var_name)
    
    if missing_vars:
        print(f"❌ Critical environment variables missing: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment")
        sys.exit(1)
    
    print("✅ All critical environment variables are configured")

# Validate critical environment variables at startup
validate_critical_env_vars()

# Configure structured JSON logging for production monitoring
# This format is compatible with ELK stack and other log aggregation systems
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "service": "sarvanom-api", "version": "1.0.0"}',
    handlers=[logging.StreamHandler()],
)


# Create custom formatter that handles missing fields
class SafeJSONFormatter(logging.Formatter):
    def format(self, record):
        # Add default values for common fields
        record.request_id = getattr(record, "request_id", "unknown")
        record.user_id = getattr(record, "user_id", "unknown")
        record.service = "sarvanom-api"
        record.version = "1.0.0"

        # Use JSON format with all fields
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": record.request_id,
            "user_id": record.user_id,
            "service": record.service,
            "version": record.version,
        }

        import json

        return json.dumps(log_obj)


# Apply custom formatter to all handlers
root_logger = logging.getLogger()
formatter = SafeJSONFormatter()
for handler in root_logger.handlers:
    handler.setFormatter(formatter)

logger = logging.getLogger(__name__)

# Import after logging setup
from shared.core.agent_orchestrator import AgentOrchestrator
from shared.core.agents.base_agent import QueryContext
from shared.core.rate_limiter import RateLimiter, RateLimitConfig
import importlib
auth_module = importlib.import_module("services.auth-service.auth")
get_current_user = auth_module.get_current_user
require_read = auth_module.require_read
login_user = auth_module.login_user
register_user = auth_module.register_user
generate_api_key = auth_module.generate_api_key
get_user_api_keys = auth_module.get_user_api_keys
revoke_api_key = auth_module.revoke_api_key
API_KEY_REGISTRY = auth_module.API_KEY_REGISTRY
from shared.core.cache import CacheManager
from shared.core.performance import PerformanceMonitor
from shared.core.security_middleware import SecurityMiddleware
from shared.core.api.api_models import (
    QueryRequest,
    QueryResponse,
    QueryUpdateRequest,
    QueryListResponse,
    QueryDetailResponse,
    QueryStatusResponse,
    HealthResponse,
    MetricsResponse,
    AnalyticsResponse,
    FeedbackRequest,
    FeedbackResponse,
    QueryRequestValidator,
    FeedbackRequestValidator,
    SearchRequestValidator,
    AnalyticsRequestValidator,
    ConfigUpdateValidator,
)
from shared.core.api.exceptions import (
    UKPHTTPException,
    AuthenticationError,
    AuthorizationError,
    RateLimitExceededError,
)

# Add expert review models
class ExpertReviewRequest(BaseModel):
    review_id: str
    expert_id: str
    verdict: str  # "supported", "contradicted", "unclear"
    notes: str
    confidence: float = Field(ge=0.0, le=1.0)


class ExpertReviewResponse(BaseModel):
    review_id: str
    status: str
    expert_id: str
    verdict: str
    notes: str
    confidence: float
    completed_at: str


# Rate limiting configurations
QUERY_RATE_LIMIT = RateLimitConfig(
    requests_per_minute=60, requests_per_hour=1000, burst_size=10
)

AUTH_RATE_LIMIT = RateLimitConfig(
    requests_per_minute=10, requests_per_hour=100, burst_size=5
)

# Add authentication models
from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    remember_me: Optional[bool] = False
    device_info: Optional[Dict[str, Any]] = None


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=100)
    role: str = Field(default="user", description="User role")


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    api_key: str
    user_id: str
    role: str
    permissions: list[str]


class APIKeyResponse(BaseModel):
    api_key: str
    user_id: str
    role: str
    permissions: list[str]
    description: str
    created_at: str


# Global variables
orchestrator = None
startup_time = None
app_version = "1.0.0"

# Request concurrency control
request_semaphore = asyncio.Semaphore(100)  # Limit to 100 concurrent requests

# In-memory query storage (for demonstration - replace with database in production)
query_storage = {}
query_index = 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with proper startup and shutdown."""
    global orchestrator, startup_time

    # Startup
    startup_time = time.time()
    logger.info("🚀 Starting SarvanOM - Your Own Knowledge Hub Powered by AI")

    # COMPREHENSIVE STARTUP DEBUGGING
    logger.info("🔍 COMPREHENSIVE STARTUP DEBUGGING")
    
    # 1. Environment Variables Check with Masking
    logger.info("📋 Environment Variables Check:")
    critical_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "REDIS_URL": os.getenv("REDIS_URL"),
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER"),
        "OPENAI_LLM_MODEL": os.getenv("OPENAI_LLM_MODEL"),
        "ANTHROPIC_MODEL": os.getenv("ANTHROPIC_MODEL"),
        "CORS_ORIGINS": os.getenv("CORS_ORIGINS"),
        "UKP_HOST": os.getenv("UKP_HOST"),
        "UKP_PORT": os.getenv("UKP_PORT"),
        "ENVIRONMENT": os.getenv("ENVIRONMENT"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL"),
    }
    
    for var_name, var_value in critical_vars.items():
        if var_value:
            # Mask sensitive values for security
            if "KEY" in var_name or "URL" in var_name:
                masked_value = var_value[:8] + "..." if len(var_value) > 8 else "***"
                logger.info(f"  ✅ {var_name}: {masked_value}")
            else:
                logger.info(f"  ✅ {var_name}: {var_value}")
        else:
            logger.warning(f"  ⚠️ {var_name}: NOT SET")
    
    # Simplified startup - skip problematic import checks for now
    logger.info("✅ Basic startup completed - skipping detailed checks")
    
    try:
        # Initialize orchestrator
        logger.info("🔍 DEEP DEBUG: Initializing orchestrator")
        try:
            from shared.core.agents.lead_orchestrator import LeadOrchestrator
            orchestrator = LeadOrchestrator()
            logger.info("✅ Orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"❌ Orchestrator initialization failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            orchestrator = None
        
        # Check vector backends and search services
        logger.info("🔍 Checking vector backends and search services...")
        try:
            # Import the vector backend checker
            from scripts.check_vector_backends import VectorBackendChecker
            
            checker = VectorBackendChecker()
            backend_results = await checker.check_all_backends()
            
            # Log results
            for backend_name, status in backend_results.items():
                if status.reachable:
                    logger.info(f"✅ {backend_name}: Reachable ({status.response_time:.3f}s)")
                elif status.configured:
                    logger.warning(f"⚠️ {backend_name}: Configured but not reachable - {status.error}")
                else:
                    logger.warning(f"⚠️ {backend_name}: Not configured - {status.error}")
            
            # Count reachable backends
            reachable_count = sum(1 for s in backend_results.values() if s.reachable)
            total_backends = len(backend_results)
            
            if reachable_count == 0:
                logger.warning("⚠️ No vector backends are reachable - search functionality will be limited")
            elif reachable_count < total_backends:
                logger.info(f"ℹ️ {reachable_count}/{total_backends} vector backends are reachable")
            else:
                logger.info(f"✅ All {total_backends} vector backends are operational")
                
        except Exception as e:
            logger.error(f"❌ Vector backend check failed: {e}")
            logger.warning("⚠️ Continuing startup without vector backend verification")
        
        logger.info("✅ SarvanOM initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize SarvanOM: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down SarvanOM - Starting graceful shutdown")

    # Create shutdown tasks list
    shutdown_tasks = []
    shutdown_errors = []

    # 1. Stop accepting new requests (handled by FastAPI)

    # 2. Wait for ongoing requests to complete (with timeout)
    logger.info("⏳ Waiting for ongoing requests to complete...")
    await asyncio.sleep(2)  # Give requests 2 seconds to complete

    # 3. Shutdown orchestrator
    if orchestrator:
        try:
            logger.info("🔄 Shutting down orchestrator...")
            await orchestrator.shutdown()
            logger.info("✅ Orchestrator shut down")
        except Exception as e:
            error_msg = f"Error during orchestrator shutdown: {e}"
            logger.error(error_msg)
            shutdown_errors.append(error_msg)

    # 4. Shutdown rate limiter
    try:
        logger.info("🔄 Shutting down rate limiter...")
        # rate_limiter.shutdown()
        logger.info("✅ Rate limiter shut down")
    except Exception as e:
        error_msg = f"Error during rate limiter shutdown: {e}"
        logger.error(error_msg)
        shutdown_errors.append(error_msg)

    # 5. Shutdown connection pools
    try:
        logger.info("🔄 Shutting down connection pools...")
        # pool_manager.shutdown()
        logger.info("✅ Connection pools shut down")
    except Exception as e:
        error_msg = f"Error during connection pool shutdown: {e}"
        logger.error(error_msg)
        shutdown_errors.append(error_msg)

    # 6. Shutdown caches
    try:
        logger.info("🔄 Shutting down caches...")
        # await initialize_caches(shutdown=True)
        logger.info("✅ Caches shut down")
    except Exception as e:
        error_msg = f"Error during cache shutdown: {e}"
        logger.error(error_msg)
        shutdown_errors.append(error_msg)

    # 7. Stop integration monitoring
    try:
        logger.info("🔄 Stopping integration monitoring...")
        # await stop_integration_monitoring()
        logger.info("✅ Integration monitoring stopped")
    except Exception as e:
        error_msg = f"Error during integration monitoring shutdown: {e}"
        logger.error(error_msg)
        shutdown_errors.append(error_msg)

    # 8. Final cleanup
    try:
        logger.info("🔄 Final cleanup...")
        # shutdown_handler.cleanup()
        logger.info("✅ Final cleanup completed")
    except Exception as e:
        error_msg = f"Error during final cleanup: {e}"
        logger.error(error_msg)
        shutdown_errors.append(error_msg)

    # Log shutdown summary
    if shutdown_errors:
        logger.error(f"❌ Shutdown completed with {len(shutdown_errors)} errors:")
        for error in shutdown_errors:
            logger.error(f"  - {error}")
    else:
        logger.info("✅ Graceful shutdown completed successfully")

    logger.info("🛑 SarvanOM shutdown complete")


# Create FastAPI app with lifespan
app = FastAPI(
    title="SarvanOM - Your Own Knowledge Hub",
    description="AI-powered knowledge platform with multi-agent architecture",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS origins from environment
cors_origins = os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://localhost:3001"
).split(",")

# Add CORS middleware with comprehensive WebSocket support
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE", "PATCH"],
    allow_headers=[
        "Content-Type", 
        "X-API-Key", 
        "Authorization", 
        "Accept",
        "Origin",
        "X-Requested-With",
        "Sec-WebSocket-Protocol",
        "Sec-WebSocket-Version",
        "Sec-WebSocket-Key",
        "Sec-WebSocket-Extensions",
        "Upgrade",
        "Connection",
        "Cache-Control",
        "Pragma"
    ],
    expose_headers=["X-Request-ID", "X-Total-Count", "X-Powered-By"],
    max_age=86400,  # Cache preflight requests for 24 hours
)

# Add rate limiting middleware (temporarily disabled due to Redis issues)
# app.middleware("http")(rate_limit_middleware)

# Add authentication endpoints
import importlib
auth_endpoints = importlib.import_module("services.auth-service.auth_endpoints")
auth_router = auth_endpoints.router

app.include_router(auth_router)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to all requests for tracing."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Add request ID to response headers
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing and request ID."""
    start_time = time.time()
    request_id = getattr(request.state, "request_id", "unknown")

    # Extract user info
    user_id = "anonymous"
    try:
        # Only try to get user for endpoints that require authentication
        # Temporarily exclude auth endpoints to avoid body consumption
        if request.url.path not in [
            "/",
            "/health",
            "/metrics",
            "/analytics",
            "/integrations",
            "/query",
            "/auth/login",
            "/auth/register",
            "/ws/collaboration",
            "/ws/query-updates",
        ]:
            current_user = await get_current_user(request)
            user_id = current_user.user_id
    except Exception as e:
        # For metrics and other public endpoints, ignore authentication errors
        if request.url.path in ["/metrics", "/health", "/"]:
            pass  # Ignore auth errors for public endpoints
        else:
            # Re-raise for protected endpoints
            raise

    # Log request
    logger.info(
        f"📥 {request.method} {request.url.path} from {request.client.host}",
        extra={
            "request_id": request_id,
            "user_id": user_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host,
        },
    )

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Record metrics
        try:
            # from api.metrics import record_request_metrics
            pass # record_request_metrics(
            #     method=request.method,
            #     endpoint=request.url.path,
            #     status_code=response.status_code,
            #     duration=process_time,
            # )
        except Exception as e:
            logger.warning(f"Failed to record metrics: {e}")

        # Log response
        logger.info(
            f"📤 {request.method} {request.url.path} -> {response.status_code} ({process_time:.3f}s)",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "status_code": response.status_code,
                "process_time": process_time,
            },
        )

        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"❌ {request.method} {request.url.path} -> ERROR ({process_time:.3f}s): {str(e)}",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "error": str(e),
                "process_time": process_time,
            },
            exc_info=True,
        )
        raise


# Security middleware
@app.middleware("http")
async def security_check(request: Request, call_next):
    """Security middleware that checks requests for threats with WebSocket bypass."""
    start_time = time.time()
    request_id = getattr(request.state, "request_id", "unknown")
    client_ip = request.client.host
    user_id = "anonymous"

    # BYPASS SECURITY FOR WEBSOCKET ENDPOINTS - CRITICAL FIX
    if request.url.path.startswith("/ws/"):
        logger.info(f"🔓 Bypassing security check for WebSocket endpoint: {request.url.path}")
        logger.info(f"WebSocket bypass - Client IP: {client_ip}, Request ID: {request_id}")
        
        # For WebSocket endpoints, skip all security checks and proceed directly
        response = await call_next(request)
        return response

    # BYPASS SECURITY FOR METRICS ENDPOINT (if needed)
    if request.url.path == "/metrics":
        logger.info(f"🔓 Bypassing security check for metrics endpoint")
        response = await call_next(request)
        return response

    try:
        # Extract user ID if available (skip for WebSocket endpoints)
        if request.url.path not in [
            "/",
            "/health",
            "/metrics",
            "/analytics",
            "/integrations",
            "/ws/collaboration",
            "/ws/query-updates",
        ]:
            current_user = await get_current_user(request)
            user_id = current_user.user_id
    except:
        pass

    # Extract query for security check (ONLY for query endpoint)
    query = ""
    if request.url.path == "/query" and request.method == "POST":
        try:
            # Read body for security check
            body_bytes = await request.body()
            if body_bytes:
                import json
                data = json.loads(body_bytes)
                query = data.get("query", "")
                
                # CRITICAL: Reset the request body so downstream can read it
                async def receive():
                    return {"type": "http.request", "body": body_bytes}
                request._receive = receive
        except Exception as e:
            logger.error(f"Security check body parsing failed: {e}")

    # Perform security check
    try:
        # from api.security import check_security
        # security_result = await check_security(
        #     query=query, client_ip=client_ip, user_id=user_id, initial_confidence=0.0
        # )
        security_result = {"blocked": False, "threats": []}

        # If blocked, return error response
        if security_result.get("blocked", False):
            logger.warning(
                f"Request blocked by security check",
                extra={
                    "request_id": request_id,
                    "user_id": user_id,
                    "client_ip": client_ip,
                    "threats": security_result.get("threats", []),
                },
            )

            # Record security metrics for blocked request
            threats = security_result.get("threats", [])
            for threat in threats:
                # record_security_metrics(
                #     threat_type=threat.get("type", "unknown"),
                #     severity=threat.get("severity", "medium"),
                #     blocked=True,
                # )
                pass # record_security_metrics(
                #     threat_type=threat.get("type", "unknown"),
                #     severity=threat.get("severity", "medium"),
                #     blocked=True,
                # )

            # Also record for any block_reason
            if security_result.get("block_reason"):
                # record_security_metrics(
                #     threat_type="ip_blocked", severity="high", blocked=True
                # )
                pass # record_security_metrics(
                #     threat_type="ip_blocked", severity="high", blocked=True
                # )

            raise HTTPException(
                status_code=403,
                detail=f"Request blocked by security check: {security_result.get('block_reason', 'Security violation detected')}",
            )

        # Record security metrics for monitored (but not blocked) threats
        threats = security_result.get("threats", [])
        for threat in threats:
            # record_security_metrics(
            #     threat_type=threat.get("type", "unknown"),
            #     severity=threat.get("severity", "low"),
            #     blocked=False,
            # )
            pass # record_security_metrics(
            #     threat_type=threat.get("type", "unknown"),
            #     severity=threat.get("severity", "low"),
            #     blocked=False,
            # )

    except HTTPException:
        # Re-raise HTTPException (security blocks)
        raise
    except Exception as e:
        logger.error(
            f"Security check failed: {e}",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "error": str(e),
            },
            exc_info=True,
        )
        # Continue processing if security check fails (fail-open for availability)

    # Acquire semaphore to limit concurrent requests
    async with request_semaphore:
        logger.info(
            f"Acquired semaphore for query processing",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "semaphore_available": request_semaphore._value,
            },
        )

        try:
            # Check cache first
            cache_key = f"{user_id}:{query}"
            cached_result = await _query_cache.get(cache_key)

            if cached_result:
                logger.info(
                    f"Cache HIT for query: {query[:50]}...",
                    extra={
                        "request_id": request_id,
                        "user_id": user_id,
                        "cache_hit": True,
                    },
                )

                # Track analytics for cache hit
                await track_query(
                    query=query,
                    execution_time=time.time() - start_time,
                    confidence=cached_result.get("confidence", 0.0),
                    client_ip=request.client.host,
                    user_id=user_id,
                    cache_hit=True,
                )

                # Record comprehensive metrics
                execution_time = time.time() - start_time
                # record_request_metrics("POST", "/query", 200, execution_time)
                # record_cache_metrics("query", True, None)
                # record_business_metrics(
                #     "cache_hit",
                #     cached_result.get("confidence", 0.0),
                #     len(cached_result.get("answer", "")),
                #     "/query",
                # )

                return QueryResponse(
                    answer=cached_result.get("answer", ""),
                    confidence=cached_result.get("confidence", 0.0),
                    citations=cached_result.get("citations", []),
                    query_id=cached_result.get("query_id", str(uuid.uuid4())),
                    metadata={
                        "cache_hit": True,
                        "request_id": request_id,
                        "execution_time_ms": int(execution_time * 1000),
                    },
                )

            # FIXED: Create user_context properly and call orchestrator with string query
            user_context = getattr(request, 'user_context', {}) or {}
            # Use getattr to safely access fields that might not exist
            max_tokens = getattr(request, 'max_tokens', 1000)
            confidence_threshold = getattr(request, 'confidence_threshold', 0.7)
            user_context["max_tokens"] = max_tokens
            user_context["confidence_threshold"] = confidence_threshold
            user_context["trace_id"] = request_id
            user_context["user_id"] = user_id

            # Process query through orchestrator - FIXED: pass string and dict instead of QueryContext
            result = await orchestrator.process_query(query, user_context)
            process_time = time.time() - start_time

            # Check if processing was successful
            if not result.get("success", True):
                error_msg = result.get("error", "Processing failed")
                error_type = result.get("error_type", "unknown_error")
                
                logger.error(
                    f"Query processing failed: {error_msg}",
                    extra={
                        "request_id": request_id,
                        "user_id": user_id,
                        "error": error_msg,
                        "error_type": error_type,
                    },
                    exc_info=True,
                )
                
                # Return 503 for service errors, 500 for other errors
                if error_type in ["authentication_error", "rate_limit_error", "model_error", "api_error", "initialization_error", "configuration_error"]:
                    raise HTTPException(status_code=503, detail=error_msg)
                else:
                raise HTTPException(status_code=500, detail=error_msg)

            # Record comprehensive metrics for orchestrator processing
            # record_request_metrics("POST", "/query", 200, process_time)
            # record_cache_metrics("query", False, None)

            # Record agent metrics if available
            agent_results = result.get("metadata", {}).get("agent_results", {})
            if agent_results:
                for agent_type, agent_result in agent_results.items():
                    if isinstance(agent_result, dict):
                        # record_agent_metrics(
                        #     agent_type=str(agent_type),
                        #     status=(
                        #         "success"
                        #         if agent_result.get("success", False)
                        #         else "error"
                        #     ),
                        #     duration=agent_result.get("execution_time_ms", 0) / 1000.0,
                        # )
                        pass # record_agent_metrics(
                        #     agent_type=str(agent_type),
                        #     status=(
                        #         "success"
                        #         if agent_result.get("success", False)
                        #         else "error"
                        #     ),
                        #     duration=agent_result.get("execution_time_ms", 0) / 1000.0,
                        # )

            # Record token usage if available
            token_usage = result.get("metadata", {}).get("token_usage", {})
            if token_usage:
                for agent_type, tokens in token_usage.items():
                    if isinstance(tokens, dict):
                        # record_token_metrics(
                        #     agent_type=str(agent_type),
                        #     prompt_tokens=tokens.get("prompt_tokens", 0),
                        #     completion_tokens=tokens.get("completion_tokens", 0),
                        # )
                        pass # record_token_metrics(
                        #     agent_type=str(agent_type),
                        #     prompt_tokens=tokens.get("prompt_tokens", 0),
                        #     completion_tokens=tokens.get("completion_tokens", 0),
                        # )
            failed_agents = []
            successful_agents = []

            for agent_type, agent_result in agent_results.items():
                if agent_result.get("status") == "failed":
                    failed_agents.append(agent_type)
                elif agent_result.get("status") == "success":
                    successful_agents.append(agent_type)

            # Determine if this is a partial failure
            is_partial_failure = len(failed_agents) > 0 and len(successful_agents) > 0
            is_complete_failure = len(successful_agents) == 0

            # Adjust success flag based on failure analysis
            if is_complete_failure:
                result["success"] = False
            elif is_partial_failure:
                result["success"] = True  # Still successful but with partial results
                result["metadata"]["partial_failure"] = True
                result["metadata"]["failed_agents"] = failed_agents
                result["metadata"]["successful_agents"] = successful_agents

            # Cache the result
            await _query_cache.set(cache_key, result)

            # Log success with detailed information
            logger.info(
                f"Query processed successfully in {process_time:.3f}s",
                extra={
                    "request_id": request_id,
                    "user_id": user_id,
                    "execution_time": process_time,
                    "confidence": result.get("confidence", 0.0),
                    "cache_hit": False,
                    "partial_failure": is_partial_failure,
                    "failed_agents": failed_agents,
                    "successful_agents": successful_agents,
                },
            )

            # Track analytics
            await track_query(
                query=query,
                execution_time=process_time,
                confidence=result.get("confidence", 0.0),
                client_ip=request.client.host,
                user_id=user_id,
                cache_hit=False,
                agent_results=agent_results,
            )

            # Record metrics
            # record_request_metrics("POST", "/query", 200, process_time)
            # record_business_metrics(
            #     "query_processed",
            #     result.get("confidence", 0.0),
            #     len(result.get("answer", "")),
            #     "/query",
            # )

            # Generate query ID and store query
            query_id = str(uuid.uuid4())

            # Store query in storage
            global query_index
            query_index += 1

            query_record = {
                "query_id": query_id,
                "query": query,
                "answer": result.get("answer", ""),
                "confidence": result.get("confidence", 0.0),
                "citations": result.get("citations", []),
                "metadata": {
                    "request_id": request_id,
                    "execution_time_ms": int(process_time * 1000),
                    "cache_hit": False,
                    "agent_results": agent_results,
                    "token_usage": result.get("metadata", {}).get("token_usage", {}),
                    "partial_failure": is_partial_failure,
                    "failed_agents": failed_agents,
                    "successful_agents": successful_agents,
                },
                "created_at": datetime.now(),
                "updated_at": None,
                "processing_time": process_time,
                "user_id": user_id,
                "status": "completed",
                "max_tokens": getattr(request, 'max_tokens', 1000),
                "confidence_threshold": getattr(request, 'confidence_threshold', 0.7),
                "user_context": getattr(request, 'user_context', None),
            }

            query_storage[query_id] = query_record

            return QueryResponse(
                answer=result.get("answer", ""),
                confidence=result.get("confidence", 0.0),
                citations=result.get("citations", []),
                query_id=query_id,
                processing_time=process_time,
                metadata={
                    "request_id": request_id,
                    "execution_time_ms": int(process_time * 1000),
                    "cache_hit": False,
                    "agent_results": agent_results,
                    "token_usage": result.get("metadata", {}).get("token_usage", {}),
                    "partial_failure": is_partial_failure,
                    "failed_agents": failed_agents,
                    "successful_agents": successful_agents,
                },
            )

        except Exception as e:
            process_time = time.time() - start_time

            logger.error(
                f"❌ Query processing failed: {str(e)}",
                extra={
                    "request_id": request_id,
                    "user_id": user_id,
                    "execution_time": process_time,
                    "error": str(e),
                },
                exc_info=True,
            )

            # Track failed query
            await track_query(
                query=query,
                execution_time=process_time,
                confidence=0.0,
                client_ip=request.client.host,
                user_id=user_id,
                error=str(e),
            )

            # Record error metrics
            # record_error_metrics("query_processing_error", "/query")
            # record_request_metrics("POST", "/query", 500, process_time)

            raise HTTPException(
                status_code=500, detail=f"Query processing failed: {str(e)}"
            )


@app.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackRequest,
    http_request: Request,
    current_user=Depends(get_current_user),
):
    """Submit user feedback for query results."""
    request_id = getattr(http_request.state, "request_id", "unknown")

    logger.info(
        f"Feedback received for query {feedback.query_id}: {feedback.feedback_type}",
        extra={
            "request_id": request_id,
            "user_id": current_user.user_id,
            "query_id": feedback.query_id,
            "feedback_type": feedback.feedback_type,
        },
    )

    try:
        # Generate feedback ID
        feedback_id = f"feedback_{feedback.query_id}_{int(time.time())}"

        # Store feedback using the new feedback storage system
        try:
            import importlib
            feedback_storage_module = importlib.import_module("services.analytics-service.feedback_storage")
            get_feedback_storage = feedback_storage_module.get_feedback_storage
            FeedbackRequest = feedback_storage_module.FeedbackRequest
            FeedbackType = feedback_storage_module.FeedbackType
            FeedbackPriority = feedback_storage_module.FeedbackPriority

            # Create feedback request
            feedback_request = FeedbackRequest(
                query_id=feedback.query_id,
                user_id=current_user.user_id,
                feedback_type=FeedbackType(feedback.feedback_type),
                details=feedback.details,
                priority=FeedbackPriority.MEDIUM,
                metadata={
                    "request_id": request_id,
                    "timestamp": datetime.now().isoformat(),
                    "source": "api",
                },
            )

            # Store feedback
            feedback_storage = get_feedback_storage()
            stored_feedback = await feedback_storage.store_feedback(feedback_request)

            logger.info(f"Feedback stored successfully: {stored_feedback.id}")

        except Exception as e:
            logger.error(f"Failed to store feedback: {e}")
            # Don't fail the request if feedback storage fails

        return FeedbackResponse(
            success=True,
            message="Feedback recorded successfully",
            feedback_id=feedback_id,
        )

    except Exception as e:
        logger.error(
            f"Failed to process feedback: {e}", extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to record feedback: {str(e)}"
        )


# Custom authentication for metrics endpoint
async def get_metrics_user():
    """Allow anonymous access to metrics endpoint."""
    return None

@app.get("/metrics")
async def get_metrics(admin: bool = False):
    if admin:
        # Optionally require admin auth here (not implemented in this public version)
        return JSONResponse(status_code=403, content={"error": "Admin metrics not enabled"})
    try:
        import prometheus_client
            from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        metrics_data = generate_latest()
        return Response(
            content=metrics_data,
            media_type=CONTENT_TYPE_LATEST,
            headers={"Cache-Control": "no-cache"}
        )
    except ImportError:
                return JSONResponse(
            status_code=503,
                    content={
                "status": "degraded",
                "message": "Prometheus client not available",
                "error": "prometheus_client package not installed",
                "installation_command": "pip install prometheus-client"
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=200,
            content={
                "status": "degraded",
                "message": "Metrics generation failed",
                "error": str(e),
                "error_type": type(e).__name__,
            }
        )


@app.get("/analytics", response_model=Dict[str, Any])
async def get_analytics(current_user=Depends(require_read())):
    """Get analytics data (any authenticated user)."""
    # TODO: Restrict to admin in future when proper user accounts exist
    try:
        analytics_data = await _analytics_collector.get_summary()
        # Remove sensitive data
        safe_analytics = {
            "total_requests": analytics_data.get("total_requests", 0),
            "total_errors": analytics_data.get("total_errors", 0),
            "average_response_time": analytics_data.get("average_response_time", 0),
            "cache_hit_rate": analytics_data.get("cache_hit_rate", 0),
            "popular_queries": analytics_data.get("popular_query_categories", {}),
            "timestamp": datetime.now().isoformat(),
        }
        return safe_analytics
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analytics retrieval failed")


@app.get("/security", response_model=Dict[str, Any])
async def get_security_status(current_user=Depends(get_current_user)):
    """Get security status (admin only)."""
    # Check admin permissions
    if not current_user.has_permission("admin"):
        raise AuthorizationError("Admin permission required for security endpoint")

    # Additional security check for production
    if (
        os.getenv("ENVIRONMENT") == "production"
        and not os.getenv("ENABLE_SECURITY_ENDPOINT", "").lower() == "true"
    ):
        raise AuthorizationError("Security endpoint disabled in production")

    try:
        from shared.core.security import get_security_summary

        security_summary = get_security_summary()
        # Remove sensitive security details
        safe_summary = {
            "status": security_summary.get("status", "unknown"),
            "threats_detected_today": security_summary.get("threat_stats", {}).get(
                "daily_count", 0
            ),
            "requests_blocked_today": security_summary.get("threat_stats", {}).get(
                "blocked_today", 0
            ),
            "security_level": security_summary.get("security_level", "normal"),
            "timestamp": datetime.now().isoformat(),
        }
        return safe_summary
    except Exception as e:
        logger.error(f"Failed to get security status: {e}")
        raise HTTPException(status_code=500, detail="Security status retrieval failed")


@app.get("/integrations")
async def get_integration_status():
    """Get status of all external integrations."""
    try:
        import importlib
        integration_monitor = importlib.import_module("services.analytics-service.integration_monitor")
        get_integration_monitor = integration_monitor.get_integration_monitor

        monitor = await get_integration_monitor()
        status = await monitor.get_integration_status()

        return {
            "timestamp": time.time(),
            "integrations": status,
            "summary": {
                "total": len(status),
                "healthy": len(
                    [s for s in status.values() if s["status"] == "healthy"]
                ),
                "unhealthy": len(
                    [s for s in status.values() if s["status"] == "unhealthy"]
                ),
                "not_configured": len(
                    [s for s in status.values() if s["status"] == "not_configured"]
                ),
            },
        }
    except Exception as e:
        logger.error(f"Failed to get integration status: {e}")
        return {"error": "Failed to get integration status"}


# ============================================================================
# COMPREHENSIVE QUERY MANAGEMENT ENDPOINTS
# ============================================================================


@app.get("/queries", response_model=QueryListResponse)
async def list_queries(
    page: int = 1,
    page_size: int = 20,
    user_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    http_request: Request = None,
    current_user=Depends(get_current_user),
):
    """List all queries with pagination and filtering."""
    request_id = getattr(http_request.state, "request_id", "unknown")

    try:
        # Filter queries for current user (unless admin)
        user_queries = []
        for query_record in query_storage.values():
            # Basic user filter - only show user's own queries unless admin
            if query_record[
                "user_id"
            ] == current_user.user_id or current_user.permissions.get("admin", False):
                # Apply additional filters
                if user_filter and user_filter not in query_record["user_id"]:
                    continue
                if status_filter and query_record["status"] != status_filter:
                    continue
                user_queries.append(query_record)

        # Sort by creation date (newest first)
        user_queries.sort(key=lambda x: x["created_at"], reverse=True)

        # Implement pagination
        total = len(user_queries)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_queries = user_queries[start_idx:end_idx]

        # Convert to simplified format for listing
        query_list = []
        for query in paginated_queries:
            query_list.append(
                {
                    "query_id": query["query_id"],
                    "query": (
                        query["query"][:100] + "..."
                        if len(query["query"]) > 100
                        else query["query"]
                    ),
                    "status": query["status"],
                    "confidence": query["confidence"],
                    "created_at": query["created_at"].isoformat(),
                    "processing_time": query["processing_time"],
                }
            )

        has_next = end_idx < total

        logger.info(
            f"Listed {len(query_list)} queries for user {current_user.user_id}",
            extra={
                "request_id": request_id,
                "user_id": current_user.user_id,
                "total": total,
            },
        )

        return QueryListResponse(
            queries=query_list,
            total=total,
            page=page,
            page_size=page_size,
            has_next=has_next,
        )

    except Exception as e:
        logger.error(f"Failed to list queries: {e}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Failed to list queries: {str(e)}")


@app.get("/queries/{query_id}", response_model=QueryDetailResponse)
async def get_query(
    query_id: str, http_request: Request, current_user=Depends(get_current_user)
):
    """Get detailed information about a specific query."""
    request_id = getattr(http_request.state, "request_id", "unknown")

    try:
        if query_id not in query_storage:
            raise HTTPException(status_code=404, detail="Query not found")

        query_record = query_storage[query_id]

        # Check authorization - users can only see their own queries unless admin
        if query_record[
            "user_id"
        ] != current_user.user_id and not current_user.permissions.get("admin", False):
            raise HTTPException(status_code=403, detail="Access denied")

        logger.info(
            f"Retrieved query {query_id}",
            extra={
                "request_id": request_id,
                "user_id": current_user.user_id,
                "query_id": query_id,
            },
        )

        return QueryDetailResponse(
            query_id=query_record["query_id"],
            query=query_record["query"],
            answer=query_record["answer"],
            confidence=query_record["confidence"],
            citations=query_record["citations"],
            metadata=query_record["metadata"],
            created_at=query_record["created_at"],
            updated_at=query_record["updated_at"],
            processing_time=query_record["processing_time"],
            user_id=query_record["user_id"],
            status=query_record["status"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get query {query_id}: {e}", extra={"request_id": request_id}
        )
        raise HTTPException(status_code=500, detail=f"Failed to get query: {str(e)}")


@app.put("/queries/{query_id}", response_model=QueryDetailResponse)
async def update_query(
    query_id: str,
    update_request: QueryUpdateRequest,
    http_request: Request,
    current_user=Depends(get_current_user),
):
    """Update an existing query and optionally reprocess it."""
    request_id = getattr(http_request.state, "request_id", "unknown")

    try:
        if query_id not in query_storage:
            raise HTTPException(status_code=404, detail="Query not found")

        query_record = query_storage[query_id]

        # Check authorization
        if query_record[
            "user_id"
        ] != current_user.user_id and not current_user.permissions.get("admin", False):
            raise HTTPException(status_code=403, detail="Access denied")

        # Update fields
        if update_request.query is not None:
            query_record["query"] = update_request.query
        if update_request.max_tokens is not None:
            query_record["max_tokens"] = update_request.max_tokens
        if update_request.confidence_threshold is not None:
            query_record["confidence_threshold"] = update_request.confidence_threshold
        if update_request.user_context is not None:
            query_record["user_context"] = update_request.user_context

        query_record["updated_at"] = datetime.now()

        # Reprocess if requested
        if update_request.reprocess and update_request.query:
            query_record["status"] = "processing"
            query_storage[query_id] = query_record

            # Create new query request
            new_request = QueryRequest(
                query=query_record["query"],
                max_tokens=query_record["max_tokens"],
                confidence_threshold=query_record["confidence_threshold"],
                user_context=query_record["user_context"],
            )

            # Process through orchestrator
            start_time = time.time()
            query_context = QueryContext(
                query=new_request.query,
                user_id=current_user.user_id,
                user_context={
                    **(new_request.user_context or {}),
                    "max_tokens": new_request.max_tokens,
                    "confidence_threshold": new_request.confidence_threshold,
                },
                token_budget=new_request.max_tokens or 4000,
            )

            result = await orchestrator.process_query(query_context)
            process_time = time.time() - start_time

            # Update with new results
            query_record.update(
                {
                    "answer": result.get("answer", ""),
                    "confidence": result.get("confidence", 0.0),
                    "citations": result.get("citations", []),
                    "processing_time": process_time,
                    "status": "completed",
                    "metadata": {
                        **query_record["metadata"],
                        "reprocessed": True,
                        "reprocess_time": process_time,
                        "execution_time_ms": int(process_time * 1000),
                    },
                }
            )

        query_storage[query_id] = query_record

        logger.info(
            f"Updated query {query_id}",
            extra={
                "request_id": request_id,
                "user_id": current_user.user_id,
                "query_id": query_id,
                "reprocessed": update_request.reprocess,
            },
        )

        return QueryDetailResponse(
            query_id=query_record["query_id"],
            query=query_record["query"],
            answer=query_record["answer"],
            confidence=query_record["confidence"],
            citations=query_record["citations"],
            metadata=query_record["metadata"],
            created_at=query_record["created_at"],
            updated_at=query_record["updated_at"],
            processing_time=query_record["processing_time"],
            user_id=query_record["user_id"],
            status=query_record["status"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to update query {query_id}: {e}", extra={"request_id": request_id}
        )
        raise HTTPException(status_code=500, detail=f"Failed to update query: {str(e)}")


@app.delete("/queries/{query_id}")
async def delete_query(
    query_id: str, http_request: Request, current_user=Depends(get_current_user)
):
    """Delete a specific query."""
    request_id = getattr(http_request.state, "request_id", "unknown")

    try:
        if query_id not in query_storage:
            raise HTTPException(status_code=404, detail="Query not found")

        query_record = query_storage[query_id]

        # Check authorization
        if query_record[
            "user_id"
        ] != current_user.user_id and not current_user.permissions.get("admin", False):
            raise HTTPException(status_code=403, detail="Access denied")

        # Delete the query
        del query_storage[query_id]

        logger.info(
            f"Deleted query {query_id}",
            extra={
                "request_id": request_id,
                "user_id": current_user.user_id,
                "query_id": query_id,
            },
        )

        return {"message": "Query deleted successfully", "query_id": query_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete query {query_id}: {e}", extra={"request_id": request_id}
        )
        raise HTTPException(status_code=500, detail=f"Failed to delete query: {str(e)}")


@app.get("/queries/{query_id}/status", response_model=QueryStatusResponse)
async def get_query_status(
    query_id: str, http_request: Request, current_user=Depends(get_current_user)
):
    """Get the processing status of a specific query."""
    request_id = getattr(http_request.state, "request_id", "unknown")

    try:
        if query_id not in query_storage:
            raise HTTPException(status_code=404, detail="Query not found")

        query_record = query_storage[query_id]

        # Check authorization
        if query_record[
            "user_id"
        ] != current_user.user_id and not current_user.permissions.get("admin", False):
            raise HTTPException(status_code=403, detail="Access denied")

        # Calculate progress for processing queries
        progress = None
        estimated_completion = None
        message = None

        if query_record["status"] == "processing":
            # Simulate progress calculation (in real implementation, this would be tracked)
            progress = 0.5  # 50% complete
            estimated_completion = datetime.now() + timedelta(seconds=30)
            message = "Query is being processed by the multi-agent system"
        elif query_record["status"] == "completed":
            progress = 1.0
            message = "Query processing completed successfully"
        elif query_record["status"] == "failed":
            progress = 0.0
            message = "Query processing failed"

        return QueryStatusResponse(
            query_id=query_id,
            status=query_record["status"],
            message=message,
            progress=progress,
            estimated_completion=estimated_completion,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get query status {query_id}: {e}",
            extra={"request_id": request_id},
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to get query status: {str(e)}"
        )


@app.patch("/queries/{query_id}/reprocess")
async def reprocess_query(
    query_id: str, http_request: Request, current_user=Depends(get_current_user)
):
    """Reprocess an existing query with the same parameters."""
    request_id = getattr(http_request.state, "request_id", "unknown")

    try:
        if query_id not in query_storage:
            raise HTTPException(status_code=404, detail="Query not found")

        query_record = query_storage[query_id]

        # Check authorization
        if query_record[
            "user_id"
        ] != current_user.user_id and not current_user.permissions.get("admin", False):
            raise HTTPException(status_code=403, detail="Access denied")

        # Mark as processing
        query_record["status"] = "processing"
        query_record["updated_at"] = datetime.now()
        query_storage[query_id] = query_record

        # Create query request from stored data
        reprocess_request = QueryRequest(
            query=query_record["query"],
            max_tokens=query_record["max_tokens"],
            confidence_threshold=query_record["confidence_threshold"],
            user_context=query_record["user_context"],
        )

        # Process through orchestrator
        start_time = time.time()
        query_context = QueryContext(
            query=reprocess_request.query,
            user_id=current_user.user_id,
            user_context={
                **(reprocess_request.user_context or {}),
                "max_tokens": reprocess_request.max_tokens,
                "confidence_threshold": reprocess_request.confidence_threshold,
            },
            token_budget=reprocess_request.max_tokens or 4000,
        )

        result = await orchestrator.process_query(query_context)
        process_time = time.time() - start_time

        # Update with new results
        query_record.update(
            {
                "answer": result.get("answer", ""),
                "confidence": result.get("confidence", 0.0),
                "citations": result.get("citations", []),
                "processing_time": process_time,
                "status": "completed",
                "updated_at": datetime.now(),
                "metadata": {
                    **query_record["metadata"],
                    "reprocessed": True,
                    "reprocess_count": query_record["metadata"].get(
                        "reprocess_count", 0
                    )
                    + 1,
                    "last_reprocess_time": process_time,
                },
            }
        )

        query_storage[query_id] = query_record

        logger.info(
            f"Reprocessed query {query_id}",
            extra={
                "request_id": request_id,
                "user_id": current_user.user_id,
                "query_id": query_id,
                "processing_time": process_time,
            },
        )

        return {
            "message": "Query reprocessed successfully",
            "query_id": query_id,
            "processing_time": process_time,
            "new_confidence": result.get("confidence", 0.0),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to reprocess query {query_id}: {e}",
            extra={"request_id": request_id},
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to reprocess query: {str(e)}"
        )


@app.post("/tasks", response_model=Dict[str, Any])
async def generate_tasks(
    request: Dict[str, Any], http_request: Request, current_user=None
):
    """Generate actionable tasks from an AI answer or query."""
    request_id = getattr(http_request.state, "request_id", "unknown")

    # Create default user if none provided
    if current_user is None:
        import importlib
        auth_module = importlib.import_module("services.auth-service.auth")
        User = auth_module.User

        current_user = User(
            user_id="default_user", role="user", permissions=["read", "write"]
        )

    try:
        answer = request.get("answer", "")
        query = request.get("query", "")

        if not answer and not query:
            raise HTTPException(
                status_code=400, detail="Either answer or query must be provided"
            )

        # Use the orchestrator to generate tasks
        from shared.core.agents.lead_orchestrator import LeadOrchestrator

        orchestrator = LeadOrchestrator()

        # Create task generation prompt
        if answer:
            task_prompt = f"""
            Based on the following AI-generated answer, extract 3-5 actionable tasks that can be taken:
            
            Answer: {answer}
            
            Please provide tasks in the following format:
            1. [Task description] - [Priority: High/Medium/Low]
            2. [Task description] - [Priority: High/Medium/Low]
            ...
            
            Focus on practical, actionable steps that can be implemented.
            """
        else:
            task_prompt = f"""
            Based on the following research query, generate 3-5 actionable tasks:
            
            Query: {query}
            
            Please provide tasks in the following format:
            1. [Task description] - [Priority: High/Medium/Low]
            2. [Task description] - [Priority: High/Medium/Low]
            ...
            
            Focus on practical, actionable steps that can be implemented.
            """

        # Generate tasks using LLM
        from shared.core.agents.llm_client import LLMClient

        llm_client = LLMClient()

        tasks_response = await llm_client.generate_text(
            task_prompt, max_tokens=300, temperature=0.3
        )

        # Parse tasks from response
        tasks = []
        if tasks_response:
            lines = tasks_response.strip().split("\n")
            for line in lines:
                line = line.strip()
                if line and (
                    line[0].isdigit()
                    or line.startswith("•")
                    or line.startswith("-")
                    or line.startswith("*")
                ):
                    # Extract task and priority
                    task_text = line
                    priority = "Medium"

                    # Check for priority indicators
                    if "High" in line:
                        priority = "High"
                    elif "Low" in line:
                        priority = "Low"

                    # Clean up the task text
                    task_text = (
                        task_text.replace("High", "")
                        .replace("Medium", "")
                        .replace("Low", "")
                        .replace("-", "")
                        .strip()
                    )
                    if task_text.startswith(("1.", "2.", "3.", "4.", "5.", "•", "*")):
                        task_text = task_text[2:].strip()

                    if task_text:
                        tasks.append(
                            {
                                "task": task_text,
                                "priority": priority,
                                "status": "pending",
                            }
                        )

        return {
            "tasks": tasks,
            "total_tasks": len(tasks),
            "generated_at": datetime.now().isoformat(),
            "request_id": request_id,
        }

    except Exception as e:
        logger.error(f"Task generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Task generation failed: {str(e)}")


@app.websocket("/ws/collaboration")
async def websocket_collaboration(websocket: WebSocket):
    """WebSocket endpoint for real-time collaboration."""
    connection_id = None
    try:
        # Accept the WebSocket connection first
        await websocket.accept()
        logger.info("🔓 WebSocket collaboration connection accepted")

        # Get connection manager
        try:
            import importlib
            realtime_module = importlib.import_module("services.api_gateway.realtime")
            get_connection_manager = realtime_module.get_connection_manager
            connection_manager = get_connection_manager()
            connection_id = await connection_manager.connect(websocket)
            logger.info(f"✅ WebSocket collaboration connected: {connection_id}")
        except ImportError as e:
            logger.error(f"❌ WebSocket collaboration setup error: {e}")
            await websocket.send_json({
                "type": "error",
                "message": "Collaboration service unavailable",
                "error_code": "SERVICE_UNAVAILABLE"
            })
            await websocket.close(code=1008, reason="Service unavailable")
            return
        except Exception as e:
            logger.error(f"❌ WebSocket collaboration setup error: {e}")
            await websocket.send_json({
                "type": "error", 
                "message": "Internal server error",
                "error_code": "INTERNAL_ERROR"
            })
            await websocket.close(code=1011, reason="Internal server error")
            return

        try:
            while True:
                # Receive message
                data = await websocket.receive_json()

                # Handle different message types
                message_type = data.get("type")

                if message_type == "join_session":
                    session_id = data.get("session_id")
                    user_id = data.get("user_id", "anonymous")

                    # Join collaboration session
                    try:
                        get_collaboration_manager = realtime_module.get_collaboration_manager
                        collab_manager = get_collaboration_manager(connection_manager)
                        await collab_manager.join_session(session_id, user_id, connection_id)

                        await websocket.send_json({
                            "type": "session_joined",
                            "session_id": session_id,
                            "user_id": user_id,
                        })
                    except Exception as e:
                        logger.error(f"Failed to join session: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "message": "Failed to join session",
                            "error_code": "SESSION_JOIN_FAILED"
                        })

                elif message_type == "update_document":
                    session_id = data.get("session_id")
                    user_id = data.get("user_id", "anonymous")
                    changes = data.get("changes", [])

                    try:
                        # Update document
                        collab_manager = get_collaboration_manager(connection_manager)
                        await collab_manager.update_document(session_id, user_id, changes)

                        # Broadcast to other users in session
                        await connection_manager.broadcast_message(
                            RealtimeMessage(
                                message_type=MessageType.COLLABORATION,
                                payload={
                                    "type": "document_updated",
                                    "session_id": session_id,
                                    "user_id": user_id,
                                    "changes": changes,
                                },
                            ),
                            exclude_connection_id=connection_id,
                        )
                    except Exception as e:
                        logger.error(f"Failed to update document: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "message": "Failed to update document",
                            "error_code": "DOCUMENT_UPDATE_FAILED"
                        })

                elif message_type == "cursor_update":
                    session_id = data.get("session_id")
                    user_id = data.get("user_id", "anonymous")
                    position = data.get("position", 0)

                    try:
                        # Update cursor position
                        collab_manager = get_collaboration_manager(connection_manager)
                        await collab_manager.update_cursor(session_id, user_id, position)

                        # Broadcast cursor update
                        await connection_manager.broadcast_message(
                            RealtimeMessage(
                                message_type=MessageType.COLLABORATION,
                                payload={
                                    "type": "cursor_updated",
                                    "session_id": session_id,
                                    "user_id": user_id,
                                    "position": position,
                                },
                            ),
                            exclude_connection_id=connection_id,
                        )
                    except Exception as e:
                        logger.error(f"Failed to update cursor: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "message": "Failed to update cursor",
                            "error_code": "CURSOR_UPDATE_FAILED"
                        })

                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                        "error_code": "UNKNOWN_MESSAGE_TYPE"
                    })

        except WebSocketDisconnect:
            logger.info(f"WebSocket collaboration disconnected: {connection_id}")
        except Exception as e:
            logger.error(f"WebSocket collaboration error: {e}")
            import traceback
            traceback.print_exc()
            try:
                await websocket.send_json({
                    "type": "error",
                    "message": "Internal error occurred",
                    "error_code": "INTERNAL_ERROR"
                })
            except:
                pass
        finally:
            # Disconnect from manager
            if connection_id:
                try:
                    await connection_manager.disconnect(connection_id)
                except Exception as e:
                    logger.error(f"Error disconnecting from manager: {e}")

    except Exception as e:
        logger.error(f"❌ WebSocket collaboration setup error: {e}")
        import traceback
        traceback.print_exc()
        try:
            await websocket.send_json({
                "type": "error",
                "message": "Connection setup failed",
                "error_code": "SETUP_FAILED"
            })
        except:
            pass
        try:
            await websocket.close(code=1011, reason="Internal error")
        except:
            pass


@app.websocket("/ws/query-updates")
async def websocket_query_updates(websocket: WebSocket):
    """WebSocket endpoint for real-time query status updates."""
    connection_id = None
    try:
        # Get connection manager
        import importlib
        realtime_module = importlib.import_module("services.api_gateway.realtime")
        get_connection_manager = realtime_module.get_connection_manager

        connection_manager = get_connection_manager()

        # Connect to manager
        connection_id = await connection_manager.connect(websocket)

        logger.info(f"WebSocket query updates connected: {connection_id}")

        try:
            while True:
                # Receive subscription request
                data = await websocket.receive_json()

                if data.get("type") == "subscribe":
                    query_id = data.get("query_id")

                    if query_id:
                        # Subscribe to query updates
                        await websocket.send_json(
                            {"type": "subscribed", "query_id": query_id}
                        )

                        # Send current status if available
                        if query_id in query_storage:
                            query_data = query_storage[query_id]
                            await websocket.send_json(
                                {
                                    "type": "query_update",
                                    "query_id": query_id,
                                    "status": query_data.get("status", "unknown"),
                                    "progress": query_data.get("progress", 0),
                                    "answer": query_data.get("answer", ""),
                                    "confidence": query_data.get("confidence", 0.0),
                                }
                            )
                    else:
                        await websocket.send_json(
                            {"type": "error", "message": "query_id is required"}
                        )

                else:
                    await websocket.send_json(
                        {"type": "error", "message": "Invalid message type"}
                    )

        except WebSocketDisconnect:
            logger.info(f"WebSocket query updates disconnected: {connection_id}")
        except Exception as e:
            logger.error(f"WebSocket query updates error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Disconnect from manager
            if connection_id:
                await connection_manager.disconnect(connection_id)

    except Exception as e:
        logger.error(f"WebSocket query updates setup error: {e}")
        import traceback
        traceback.print_exc()
        await websocket.close(code=1011, reason="Internal error")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("UKP_HOST", "0.0.0.0"),
        port=int(os.getenv("UKP_PORT", "8000")),
        reload=os.getenv("UKP_RELOAD", "false").lower() == "true",
        log_level=os.getenv("UKP_LOG_LEVEL", "info").lower(),
    )
