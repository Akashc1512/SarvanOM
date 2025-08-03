"""
Gateway Service
Main API Gateway for routing requests to backend services.

This service provides:
- FastAPI application setup
- Service routing and orchestration
- Middleware configuration
- Health monitoring
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Import routers and middleware
from .router import router
from .middleware import setup_middleware

# Import backend services for initialization
from ..auth import AuthService
from ..retrieval import SearchService
from ..fact_check import FactCheckService
from ..synthesis import SynthesisService
from ..crawler import WebCrawler
from ..vector import VectorService
from ..graph import GraphService

logger = logging.getLogger(__name__)

# Global service instances
auth_service = None
search_service = None
fact_check_service = None
synthesis_service = None
crawler_service = None
vector_service = None
graph_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Gateway Service...")
    
    # Initialize services
    global auth_service, search_service, fact_check_service, synthesis_service
    global crawler_service, vector_service, graph_service
    
    try:
        auth_service = AuthService()
        search_service = SearchService()
        fact_check_service = FactCheckService()
        synthesis_service = SynthesisService()
        crawler_service = WebCrawler()
        vector_service = VectorService()
        graph_service = GraphService()
        
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Gateway Service...")
    
    # Cleanup services
    try:
        if auth_service:
            await auth_service.cleanup()
        if search_service:
            await search_service.cleanup()
        if fact_check_service:
            await fact_check_service.cleanup()
        if synthesis_service:
            await synthesis_service.cleanup()
        if crawler_service:
            await crawler_service.cleanup()
        if vector_service:
            await vector_service.cleanup()
        if graph_service:
            await graph_service.cleanup()
        
        logger.info("All services cleaned up successfully")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Create FastAPI app
    app = FastAPI(
        title="SarvanOM API Gateway",
        description="API Gateway for Universal Knowledge Hub Backend Services",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Setup middleware
    setup_middleware(app, auth_service=auth_service)
    
    # Include routers
    app.include_router(router)
    
    # Add root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with service information."""
        return {
            "service": "SarvanOM API Gateway",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "search": "/api/v1/search",
                "fact_check": "/api/v1/fact-check",
                "synthesis": "/api/v1/synthesis",
                "auth": "/api/v1/auth",
                "crawler": "/api/v1/crawler",
                "vector": "/api/v1/vector",
                "graph": "/api/v1/graph",
                "health": "/api/v1/health"
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
        "backend.gateway.gateway_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
