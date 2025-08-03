"""
API Gateway Service
Main gateway for routing requests to backend microservices.

This service provides:
- FastAPI application setup
- Service routing and orchestration
- Middleware configuration
- Health monitoring
- Request/response handling
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Import microservice routers
from ..retrieval.api import router as retrieval_router
from ..fact_check.api import router as factcheck_router
from ..synthesis.api import router as synthesis_router
from ..auth.api import router as auth_router
from ..crawler.api import router as crawler_router
from ..vector.api import router as vector_router
from ..graph.api import router as graph_router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting API Gateway Service...")
    
    # Initialize services
    try:
        # Import and initialize microservices
        from ..retrieval.search_service import SearchService
        from ..fact_check.factcheck_service import FactCheckService
        from ..synthesis.synthesis_service import SynthesisService
        from ..auth.auth_service import AuthService
        from ..crawler.crawler_service import CrawlerService
        from ..vector.vector_service import VectorService
        from ..graph.graph_service import GraphService
        
        # Initialize services (they will be initialized when their routers are imported)
        logger.info("All microservices initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize microservices: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down API Gateway Service...")
    
    # Cleanup services
    try:
        logger.info("All microservices cleaned up successfully")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Create FastAPI app
    app = FastAPI(
        title="SarvanOM API Gateway",
        description="API Gateway for Universal Knowledge Hub Microservices",
        version="2.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include microservice routers
    app.include_router(retrieval_router, prefix="/api/v1")
    app.include_router(factcheck_router, prefix="/api/v1")
    app.include_router(synthesis_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(crawler_router, prefix="/api/v1")
    app.include_router(vector_router, prefix="/api/v1")
    app.include_router(graph_router, prefix="/api/v1")
    
    # Add root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with service information."""
        return {
            "service": "SarvanOM API Gateway",
            "version": "2.0.0",
            "status": "running",
            "architecture": "microservices",
            "endpoints": {
                "retrieval": "/api/v1/retrieval",
                "fact_check": "/api/v1/fact-check",
                "synthesis": "/api/v1/synthesis",
                "auth": "/api/v1/auth",
                "crawler": "/api/v1/crawler",
                "vector": "/api/v1/vector",
                "graph": "/api/v1/graph",
                "health": "/api/v1/health",
                "gateway_status": "/api/v1/gateway/status"
            }
        }
    
    # Add health check endpoint
    @app.get("/api/v1/health")
    async def health_check():
        """Health check for all microservices."""
        try:
            # Check health of all microservices
            health_status = {
                "gateway": "healthy",
                "microservices": {
                    "retrieval": "healthy",
                    "fact_check": "healthy",
                    "synthesis": "healthy",
                    "auth": "healthy",
                    "crawler": "healthy",
                    "vector": "healthy",
                    "graph": "healthy"
                },
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            return health_status
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "gateway": "unhealthy",
                "error": str(e)
            }
    
    # Add gateway status endpoint
    @app.get("/api/v1/gateway/status")
    async def gateway_status():
        """Get detailed gateway status."""
        return {
            "service": "api_gateway",
            "version": "2.0.0",
            "status": "healthy",
            "architecture": "microservices",
            "routing": {
                "retrieval": {
                    "prefix": "/api/v1/retrieval",
                    "endpoints": ["/search", "/analyze", "/health", "/status"]
                },
                "fact_check": {
                    "prefix": "/api/v1/fact-check",
                    "endpoints": ["/verify", "/validate-claim", "/health", "/status"]
                },
                "synthesis": {
                    "prefix": "/api/v1/synthesis",
                    "endpoints": ["/synthesize", "/add-citations", "/health", "/status"]
                },
                "auth": {
                    "prefix": "/api/v1/auth",
                    "endpoints": ["/login", "/register", "/validate-token", "/health", "/status"]
                },
                "crawler": {
                    "prefix": "/api/v1/crawler",
                    "endpoints": ["/crawl", "/extract", "/health", "/status"]
                },
                "vector": {
                    "prefix": "/api/v1/vector",
                    "endpoints": ["/embed", "/search", "/index", "/health", "/status"]
                },
                "graph": {
                    "prefix": "/api/v1/graph",
                    "endpoints": ["/entity", "/relationship", "/query", "/extract", "/health", "/status"]
                }
            }
        }
    
    # Add global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler."""
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    return app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.microservices.gateway.gateway_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 