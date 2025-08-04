"""
Gateway Service

This service orchestrates all backend services and provides a unified API interface.
It handles request routing, service discovery, load balancing, and inter-service communication.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

# FastAPI imports
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import services
from ..retrieval import SearchService
from ..fact_check import FactCheckService
from ..synthesis import SynthesisService
from ..auth import AuthService
from ..crawler import CrawlerService
from ..vector import VectorService
from ..graph import GraphService

# Import router
from .router import router

logger = logging.getLogger(__name__)


class GatewayService:
    """
    Gateway Service that orchestrates all backend services.
    Provides unified API interface and handles inter-service communication.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize all services
        self.search_service = SearchService()
        self.fact_check_service = FactCheckService()
        self.synthesis_service = SynthesisService()
        self.auth_service = AuthService()
        self.crawler_service = CrawlerService()
        self.vector_service = VectorService()
        self.graph_service = GraphService()
        
        # Service registry for discovery
        self.services = {
            "search": self.search_service,
            "fact_check": self.fact_check_service,
            "synthesis": self.synthesis_service,
            "auth": self.auth_service,
            "crawler": self.crawler_service,
            "vector": self.vector_service,
            "graph": self.graph_service
        }
        
        # Initialize FastAPI app
        self.app = self._create_app()
    
    def _create_app(self) -> FastAPI:
        """Create and configure FastAPI application."""
        app = FastAPI(
            title="Knowledge Platform API Gateway",
            description="Unified API gateway for all backend services",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add request logging middleware
        @app.middleware("http")
        async def log_requests(request: Request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            
            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            return response
        
        # Add exception handler
        @app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            logger.error(f"Unhandled exception: {exc}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "detail": str(exc),
                    "timestamp": time.time()
                }
            )
        
        # Include router
        app.include_router(router)
        
        # Add root endpoint
        @app.get("/")
        async def root():
            return {
                "message": "Knowledge Platform API Gateway",
                "version": "1.0.0",
                "status": "healthy",
                "services": list(self.services.keys())
            }
        
        # Add health check endpoint
        @app.get("/health")
        async def health_check():
            return await self.get_services_health()
        
        return app
    
    async def get_services_health(self) -> Dict[str, Any]:
        """Get health status of all services."""
        health_status = {
            "gateway": "healthy",
            "timestamp": time.time(),
            "services": {}
        }
        
        for service_name, service in self.services.items():
            try:
                status = service.get_status()
                health_status["services"][service_name] = status
            except Exception as e:
                logger.error(f"Failed to get status for {service_name}: {e}")
                health_status["services"][service_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        return health_status
    
    async def route_request(self, service_name: str, method: str, **kwargs) -> Any:
        """Route request to appropriate service."""
        if service_name not in self.services:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
        
        service = self.services[service_name]
        
        try:
            if hasattr(service, method):
                method_func = getattr(service, method)
                if asyncio.iscoroutinefunction(method_func):
                    return await method_func(**kwargs)
                else:
                    return method_func(**kwargs)
            else:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Method {method} not found in service {service_name}"
                )
        except Exception as e:
            logger.error(f"Service {service_name} method {method} failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Service {service_name} error: {str(e)}"
            )
    
    async def orchestrate_search(self, query: str, user_id: str = None, **kwargs) -> Dict[str, Any]:
        """Orchestrate a comprehensive search across multiple services."""
        try:
            # Start with vector search
            vector_results = await self.vector_service.search_similar(query)
            
            # Get graph entities
            entities = await self.graph_service.find_entities(query)
            
            # Combine results
            combined_results = {
                "vector_results": [result.__dict__ for result in vector_results],
                "entities": [entity.__dict__ for entity in entities],
                "query": query,
                "timestamp": time.time()
            }
            
            return combined_results
        except Exception as e:
            logger.error(f"Orchestrated search failed: {e}")
            raise HTTPException(status_code=500, detail=f"Search orchestration failed: {str(e)}")
    
    async def orchestrate_fact_check(self, claim: str, sources: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Orchestrate fact checking with multiple services."""
        try:
            # Perform fact check
            fact_check_result = await self.fact_check_service.fact_check(claim, sources)
            
            # Get related entities from graph
            entities = await self.graph_service.find_entities(claim)
            
            # Search for supporting evidence
            evidence_results = await self.vector_service.search_similar(claim, top_k=5)
            
            return {
                "fact_check": fact_check_result,
                "related_entities": [entity.__dict__ for entity in entities],
                "supporting_evidence": [result.__dict__ for result in evidence_results],
                "claim": claim,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Orchestrated fact check failed: {e}")
            raise HTTPException(status_code=500, detail=f"Fact check orchestration failed: {str(e)}")
    
    async def orchestrate_synthesis(self, content: List[Dict[str, Any]], query: str, **kwargs) -> Dict[str, Any]:
        """Orchestrate content synthesis with multiple services."""
        try:
            # Synthesize content
            synthesis_result = await self.synthesis_service.synthesize(content, query)
            
            # Generate citations
            citations = await self.synthesis_service.generate_citations(content)
            
            # Find related entities
            entities = await self.graph_service.find_entities(query)
            
            return {
                "synthesis": synthesis_result,
                "citations": citations,
                "related_entities": [entity.__dict__ for entity in entities],
                "query": query,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Orchestrated synthesis failed: {e}")
            raise HTTPException(status_code=500, detail=f"Synthesis orchestration failed: {str(e)}")
    
    def get_service(self, service_name: str):
        """Get a specific service by name."""
        if service_name not in self.services:
            raise ValueError(f"Service {service_name} not found")
        return self.services[service_name]
    
    def list_services(self) -> List[str]:
        """List all available services."""
        return list(self.services.keys())
    
    async def shutdown(self):
        """Shutdown all services gracefully."""
        logger.info("Shutting down gateway service...")
        
        # Shutdown all services
        for service_name, service in self.services.items():
            try:
                if hasattr(service, 'shutdown'):
                    if asyncio.iscoroutinefunction(service.shutdown):
                        await service.shutdown()
                    else:
                        service.shutdown()
                logger.info(f"Shutdown {service_name} service")
            except Exception as e:
                logger.error(f"Failed to shutdown {service_name} service: {e}")
        
        logger.info("Gateway service shutdown complete")


# Create global gateway instance
gateway = GatewayService()


def get_gateway() -> GatewayService:
    """Get the global gateway instance."""
    return gateway 