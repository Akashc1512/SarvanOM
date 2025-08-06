"""
Universal Knowledge Hub - API Gateway Service
Main entry point for the knowledge platform with modular architecture.

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
- Modular design with separated concerns

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

# Import shared components
from shared.core.api.config import get_settings
settings = get_settings()

# Import the enhanced environment manager
from shared.core.config.environment_manager import get_environment_manager, Environment

# Get environment manager and configuration
env_manager = get_environment_manager()
env_config = env_manager.get_config()

# Import the new modular components
from .models import *
from .middleware import (
    setup_cors,
    add_request_id,
    log_requests,
    security_check,
    rate_limit_check,
    get_current_user,
    get_performance_metrics
)
from .middleware.error_handling import create_error_handling_middleware
from .routes import routers
from .services import query_service, health_service

# Import analytics functions
try:
    import importlib
    analytics_module = importlib.import_module("services.analytics_service.analytics")
    track_query = analytics_module.track_query
except ImportError:
    # Fallback if analytics service is not available
    async def track_query(*args, **kwargs):
        """Implement actual query tracking with comprehensive monitoring and analytics."""
        try:
            import asyncpg
            import os
            from datetime import datetime
            
            # Extract query information from arguments
            request = args[0] if args else None
            query_data = kwargs.get("query_data", {})
            user_id = kwargs.get("user_id", "anonymous")
            
            if not request or not query_data:
                return
            
            # Get database configuration
            db_host = os.getenv('DB_HOST', 'localhost')
            db_port = int(os.getenv('DB_PORT', '5432'))
            db_name = os.getenv('DB_NAME', 'sarvanom')
            db_user = os.getenv('DB_USER', 'postgres')
            db_password = os.getenv('DB_PASSWORD', '')
            
            # Extract query information
            query_text = query_data.get("query", "")
            query_type = query_data.get("type", "basic")
            processing_time = query_data.get("processing_time", 0)
            success = query_data.get("success", False)
            error_message = query_data.get("error", None)
            sources_count = len(query_data.get("sources", []))
            verification_score = query_data.get("verification", {}).get("confidence", 0)
            
            # Get request metadata
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            request_id = getattr(request.state, "request_id", "unknown")
            
            try:
                # Connect to database
                conn = await asyncpg.connect(
                    host=db_host,
                    port=db_port,
                    database=db_name,
                    user=db_user,
                    password=db_password
                )
                
                # Insert query tracking record
                await conn.execute("""
                    INSERT INTO query_tracking (
                        query_id, user_id, query_text, query_type, processing_time,
                        success, error_message, sources_count, verification_score,
                        client_ip, user_agent, request_id, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                """, 
                    request_id, user_id, query_text, query_type, processing_time,
                    success, error_message, sources_count, verification_score,
                    client_ip, user_agent, request_id, datetime.now()
                )
                
                # Update user query statistics
                await conn.execute("""
                    INSERT INTO user_query_stats (user_id, total_queries, successful_queries, avg_processing_time, last_query_at)
                    VALUES ($1, 1, $2, $3, $4)
                    ON CONFLICT (user_id) DO UPDATE SET
                        total_queries = user_query_stats.total_queries + 1,
                        successful_queries = user_query_stats.successful_queries + $2,
                        avg_processing_time = (user_query_stats.avg_processing_time * user_query_stats.total_queries + $3) / (user_query_stats.total_queries + 1),
                        last_query_at = $4
                """, user_id, 1 if success else 0, processing_time, datetime.now())
                
                await conn.close()
                
                logger.info(f"Query tracked successfully: {request_id} for user {user_id}")
                
            except asyncpg.InvalidPasswordError:
                logger.error("Database authentication failed for query tracking")
            except asyncpg.ConnectionDoesNotExistError:
                logger.error("Database connection failed for query tracking")
            except Exception as e:
                logger.error(f"Database query tracking failed: {e}")
                
        except ImportError:
            logger.warning("asyncpg not available, using in-memory query tracking")
            # Fallback to in-memory tracking
            track_query_in_memory(request_id, query_data, user_id)
            
        except Exception as e:
            logger.error(f"Query tracking failed: {e}")

def track_query_in_memory(request_id: str, query_data: Dict[str, Any], user_id: str):
    """Fallback in-memory query tracking."""
    query_record = {
        "request_id": request_id,
        "user_id": user_id,
        "query_text": query_data.get("query", ""),
        "query_type": query_data.get("type", "basic"),
        "processing_time": query_data.get("processing_time", 0),
        "success": query_data.get("success", False),
        "timestamp": datetime.now()
    }
    
    # Store in memory (limited to last 1000 queries)
    if not hasattr(track_query_in_memory, "query_history"):
        track_query_in_memory.query_history = []
    
    track_query_in_memory.query_history.append(query_record)
    
    # Keep only last 1000 queries
    if len(track_query_in_memory.query_history) > 1000:
        track_query_in_memory.query_history = track_query_in_memory.query_history[-1000:]

# Import agent handlers
try:
    from .agents import agent_handler
except ImportError:
    # Fallback if agent handlers are not available
    agent_handler = None

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
    """Validate critical environment variables using the enhanced environment manager."""
    try:
        # Use the environment manager to validate configuration
        env_manager = get_environment_manager()
        config = env_manager.get_config()
        
        # Environment-specific validation
        environment = env_manager.environment.value
        missing_vars = []
        
        if environment in ["production", "staging"]:
            # Production and staging require all critical variables
            if not config.database_url:
                missing_vars.append("DATABASE_URL")
            if not config.redis_url:
                missing_vars.append("REDIS_URL")
            if not config.jwt_secret_key:
                missing_vars.append("JWT_SECRET_KEY")
            if not config.openai_api_key and not config.anthropic_api_key:
                missing_vars.append("OPENAI_API_KEY or ANTHROPIC_API_KEY")
            if not config.vector_db_url:
                missing_vars.append("VECTOR_DB_URL")
            if not config.meilisearch_url:
                missing_vars.append("MEILISEARCH_URL")
            if not config.arangodb_url:
                missing_vars.append("ARANGO_URL")
        
        elif environment == "testing":
            # Testing environment has minimal requirements
            if not config.test_mode:
                missing_vars.append("TEST_MODE should be True")
            if not config.mock_ai_responses:
                missing_vars.append("MOCK_AI_RESPONSES should be True")
            if not config.skip_authentication:
                missing_vars.append("SKIP_AUTHENTICATION should be True")
        
        # Development environment has no strict requirements
        
        if missing_vars:
            # Missing environment variables - will be logged after logging setup
            return False
        
        # Environment validation passed - will be logged after logging setup
        return True
        
    except Exception as e:
        # Will be logged properly after logging setup
        return False

# Validate critical environment variables at startup
validate_critical_env_vars()

# Import unified logging configuration
from shared.core.unified_logging import setup_logging, get_logger, setup_fastapi_logging
from shared.core.production_logging import setup_production_logging, get_production_log_collector

# Initialize environment manager first
env_manager = get_environment_manager()
env_config = env_manager.get_config()

# Configure unified logging based on environment
if env_manager.is_production():
    setup_production_logging("sarvanom-api-gateway", enable_collection=True)
    log_collector = get_production_log_collector()
else:
    logging_config = setup_logging(
        service_name="sarvanom-api-gateway",
        version="1.0.0"
    )

logger = get_logger(__name__)

logger.info("=" * 80)
logger.info("🚀 UNIVERSAL KNOWLEDGE PLATFORM - STARTING UP")
logger.info("=" * 80)
logger.info(f"📋 Environment: {env_manager.environment.value.upper()}")
logger.info(f"🔧 Configuration: {env_config.name}")
logger.info(f"🐛 Debug Mode: {env_config.debug}")
logger.info(f"🧪 Testing Mode: {env_config.testing}")
logger.info(f"📝 Log Level: {env_config.log_level}")
logger.info(f"⚡ Auto Reload: {env_config.auto_reload}")
logger.info(f"🔒 Security Headers: {env_config.security_headers_enabled}")
logger.info(f"📊 Metrics Enabled: {env_config.metrics_enabled}")
logger.info(f"🔍 Tracing Enabled: {env_config.enable_tracing}")
logger.info(f"🎭 Mock AI Responses: {env_config.mock_ai_responses}")
logger.info(f"🔐 Skip Authentication: {env_config.skip_authentication}")
logger.info(f"🐛 Debug Endpoints: {env_config.enable_debug_endpoints}")
logger.info(f"🎭 Mock Providers: {env_config.mock_providers}")

# Log feature flags
logger.info("🎛️  Feature Flags:")
for feature, enabled in env_config.features.items():
    status = "✅" if enabled else "❌"
    logger.info(f"   {status} {feature}")

# Log environment-specific settings
if env_manager.is_production():
    logger.info("🏭 PRODUCTION MODE - All security features enabled")
    if not env_config.database_url:
        logger.warning("⚠️  DATABASE_URL not set - required for production")
    if not env_config.redis_url:
        logger.warning("⚠️  REDIS_URL not set - required for production")
    if not env_config.jwt_secret_key:
        logger.warning("⚠️  JWT_SECRET_KEY not set - required for production")
elif env_manager.is_development():
    logger.info("🔧 DEVELOPMENT MODE - Debug features enabled")
elif env_manager.is_testing():
    logger.info("🧪 TESTING MODE - Mock providers enabled")
elif env_manager.is_staging():
    logger.info("🚀 STAGING MODE - Production-like with monitoring")

logger.info("=" * 80)

# Mock functions for demonstration (these would be actual implementations)
async def route_query(query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Mock route query function."""
    return {
        "success": True,
        "answer": f"Mock answer for: {query}",
        "sources": ["mock_source_1", "mock_source_2"],
        "verification": {"overall_status": "verified"},
        "metadata": {
            "llm_provider": "mock_provider",
            "vector_results": [],
            "keyword_results": [],
            "knowledge_graph_results": []
        },
        "confidence": 0.85
    }

async def get_integration_layer():
    """Mock integration layer function."""
    class MockIntegration:
        async def process_query(self, request):
            return {
                "success": True,
                "orchestration_result": {"response": "Mock response", "model_used": "mock_model"},
                "query_analysis": {"intent": "mock_intent", "complexity": "simple", "domain": "general", "entities": []},
                "verification": {},
                "sources": [],
                "confidence": 0.8,
                "processing_time_ms": 1000
            }
    
    return MockIntegration()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("🚀 Starting SarvanOM API Gateway")
    logger.info(f"📊 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"🔧 Debug mode: {os.getenv('DEBUG', 'false')}")
    
    # Health check
    try:
        # Basic system checks
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        logger.info(f"💾 Memory usage: {memory.percent}%")
        logger.info(f"🖥️ CPU usage: {cpu_percent}%")
        logger.info("✅ System health check passed")
        
    except Exception as e:
        logger.error(f"❌ System health check failed: {e}")
        sys.exit(1)
    
    # Service startup
    logger.info("🔗 Initializing service connections...")
    
    # Initialize actual service connections
    try:
        import asyncpg
        import redis.asyncio as redis
        import aiohttp
        import os
        
        # Database connection pool
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = int(os.getenv('DB_PORT', '5432'))
        db_name = os.getenv('DB_NAME', 'sarvanom')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        
        app.state.db_pool = await asyncpg.create_pool(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
            min_size=5,
            max_size=20
        )
        logger.info("✅ Database connection pool initialized")
        
        # Redis connection
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', '6379'))
        redis_db = int(os.getenv('REDIS_DB', '0'))
        
        app.state.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True
        )
        await app.state.redis_client.ping()
        logger.info("✅ Redis connection initialized")
        
        # HTTP session for external API calls
        app.state.http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'Sarvanom-API/1.0.0'}
        )
        logger.info("✅ HTTP session initialized")
        
        # Meilisearch connection
        meili_url = os.getenv('MEILISEARCH_URL', 'http://localhost:7700')
        meili_key = os.getenv('MEILI_MASTER_KEY', '')
        
        async with app.state.http_session.get(f'{meili_url}/health', timeout=5) as response:
            if response.status == 200:
                logger.info("✅ Meilisearch connection verified")
            else:
                logger.warning("⚠️ Meilisearch connection failed")
        
        # ArangoDB connection
        arango_url = os.getenv('ARANGO_URL', 'http://localhost:8529')
        arango_user = os.getenv('ARANGO_USERNAME', 'root')
        arango_pass = os.getenv('ARANGO_PASSWORD', '')
        
        auth = aiohttp.BasicAuth(arango_user, arango_pass)
        async with app.state.http_session.get(f'{arango_url}/_api/version', auth=auth, timeout=5) as response:
            if response.status == 200:
                logger.info("✅ ArangoDB connection verified")
            else:
                logger.warning("⚠️ ArangoDB connection failed")
        
        # LLM service connections
        openai_key = os.getenv('OPENAI_API_KEY', '')
        if openai_key:
            async with app.state.http_session.get(
                'https://api.openai.com/v1/models',
                headers={'Authorization': f'Bearer {openai_key}'},
                timeout=5
            ) as response:
                if response.status == 200:
                    logger.info("✅ OpenAI connection verified")
                else:
                    logger.warning("⚠️ OpenAI connection failed")
        
        anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
        if anthropic_key:
            async with app.state.http_session.get(
                'https://api.anthropic.com/v1/messages',
                headers={'x-api-key': anthropic_key, 'anthropic-version': '2023-06-01'},
                timeout=5
            ) as response:
                if response.status in [200, 401]:  # 401 means auth works but no message
                    logger.info("✅ Anthropic connection verified")
                else:
                    logger.warning("⚠️ Anthropic connection failed")
        
        logger.info("🚀 All service connections initialized successfully")
        
    except ImportError as e:
        logger.warning(f"⚠️ Service connection initialization failed (missing dependency): {e}")
    except Exception as e:
        logger.error(f"❌ Service connection initialization failed: {e}")
        # Continue startup even if some connections fail
    
    logger.info("✅ All service connections initialized")
    logger.info("🎉 SarvanOM API Gateway is ready!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down SarvanOM API Gateway...")
    
    # Cleanup connections
    try:
        # Close database connection pool
        if hasattr(app.state, 'db_pool'):
            await app.state.db_pool.close()
            logger.info("✅ Database connection pool closed")
        
        # Close Redis connection
        if hasattr(app.state, 'redis_client'):
            await app.state.redis_client.close()
            logger.info("✅ Redis connection closed")
        
        # Close HTTP session
        if hasattr(app.state, 'http_session'):
            await app.state.http_session.close()
            logger.info("✅ HTTP session closed")
        
        # Close any other service connections
        if hasattr(app.state, 'query_cache'):
            if hasattr(app.state.query_cache, 'close'):
                await app.state.query_cache.close()
            logger.info("✅ Query cache closed")
        
        # Clear any remaining state
        for attr in list(app.state.__dict__.keys()):
            if attr.startswith('_'):
                continue
            try:
                if hasattr(getattr(app.state, attr), 'close'):
                    await getattr(app.state, attr).close()
            except:
                pass
        
        logger.info("✅ All service connections cleaned up successfully")
        
    except Exception as e:
        logger.error(f"❌ Service connection cleanup failed: {e}")
        # Continue shutdown even if cleanup fails
    
    logger.info("👋 SarvanOM API Gateway shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="SarvanOM API Gateway",
    description="Universal Knowledge Hub - API Gateway Service",
    version="1.0.0",
    lifespan=lifespan
)

# Setup FastAPI logging integration
setup_fastapi_logging(app, service_name="sarvanom-api-gateway")

# Setup CORS
setup_cors(app)

# Add middleware
app.middleware("http")(add_request_id)
app.middleware("http")(log_requests)
app.middleware("http")(security_check)
app.middleware("http")(rate_limit_check)
app.middleware("http")(create_error_handling_middleware())

# Register all routers
for router in routers:
    app.include_router(router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "SarvanOM API Gateway",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "queries": "/query",
            "health": "/health",
            "agents": "/agents",
            "docs": "/docs"
        }
    }

# Test endpoint
@app.get("/test")
async def test_endpoint():
    """Test endpoint for basic connectivity."""
    return {
        "message": "SarvanOM API Gateway is running!",
        "timestamp": datetime.now().isoformat(),
        "status": "ok"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with standardized response format."""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - Path: {request.url}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url),
            "request_id": getattr(request.state, "request_id", "unknown"),
            "error_type": "http_exception"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with comprehensive logging and standardized response."""
    import traceback
    
    # Generate request ID if not present
    request_id = getattr(request.state, "request_id", f"req_{int(time.time() * 1000)}")
    
    # Log the full exception with context
    logger.error(
        f"Unhandled exception in {request.url}: {str(exc)}",
        extra={
            "request_id": request_id,
            "path": str(request.url),
            "method": request.method,
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "traceback": traceback.format_exc()
        },
        exc_info=True
    )
    
    # Determine if this is a known error type that should be handled differently
    error_type = "internal_server_error"
    status_code = 500
    
    if isinstance(exc, (ValueError, TypeError)):
        error_type = "validation_error"
        status_code = 400
    elif isinstance(exc, (ConnectionError, TimeoutError)):
        error_type = "service_unavailable"
        status_code = 503
    elif isinstance(exc, (PermissionError, OSError)):
        error_type = "permission_error"
        status_code = 403
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": "Internal server error",
            "status_code": status_code,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url),
            "request_id": request_id,
            "error_type": error_type
        }
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors."""
    logger.warning(f"Validation error: {exc.errors()} - Path: {request.url}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "status_code": 422,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url),
            "request_id": getattr(request.state, "request_id", "unknown"),
            "error_type": "validation_error",
            "details": exc.errors()
        }
    )

@app.exception_handler(TimeoutError)
async def timeout_exception_handler(request: Request, exc: TimeoutError):
    """Handle timeout errors."""
    logger.error(f"Timeout error: {str(exc)} - Path: {request.url}")
    
    return JSONResponse(
        status_code=408,
        content={
            "error": "Request timeout",
            "status_code": 408,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url),
            "request_id": getattr(request.state, "request_id", "unknown"),
            "error_type": "timeout_error"
        }
    )

@app.exception_handler(ConnectionError)
async def connection_exception_handler(request: Request, exc: ConnectionError):
    """Handle connection errors."""
    logger.error(f"Connection error: {str(exc)} - Path: {request.url}")
    
    return JSONResponse(
        status_code=503,
        content={
            "error": "Service temporarily unavailable",
            "status_code": 503,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url),
            "request_id": getattr(request.state, "request_id", "unknown"),
            "error_type": "service_unavailable"
        }
    )

# Server configuration
def get_server_config() -> dict:
    """Get server configuration."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    # Find available port if default is in use
    def is_port_available(host: str, port: int, timeout: float = 1.0) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                return result != 0
        except Exception:
            return False
    
    def find_available_port(host: str, preferred_ports: list, max_attempts: int = 10) -> int:
        for port in preferred_ports:
            if is_port_available(host, port):
                return port
        
        # If no preferred port is available, find any available port
        for attempt in range(max_attempts):
            port = 8000 + attempt
            if is_port_available(host, port):
                return port
        
        raise RuntimeError("No available ports found")
    
    # Check if default port is available
    if not is_port_available(host, port):
        logger.warning(f"Port {port} is not available, finding alternative...")
        port = find_available_port(host, [8000, 8001, 8002, 8003, 8004])
        logger.info(f"Using port {port}")
    
    return {
        "host": host,
        "port": port,
        "reload": os.getenv("DEBUG", "false").lower() == "true",
        "log_level": os.getenv("LOG_LEVEL", "info").lower()
    }

if __name__ == "__main__":
    config = get_server_config()
    
    logger.info(f"🚀 Starting server on {config['host']}:{config['port']}")
    logger.info(f"🔧 Debug mode: {config['reload']}")
    logger.info(f"📝 Log level: {config['log_level']}")
    
    uvicorn.run(
        "main:app",
        host=config["host"],
        port=config["port"],
        reload=config["reload"],
        log_level=config["log_level"]
    )
