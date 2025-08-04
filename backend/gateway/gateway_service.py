"""
Gateway Service

This module provides gateway operations for the backend gateway service.

# DEAD CODE - Candidate for deletion: This backend directory is not used by the main application
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import asyncio

# Import services using absolute imports
from backend.retrieval import SearchService
from backend.fact_check import FactCheckService
from backend.synthesis import SynthesisService
from backend.auth import AuthService
from backend.crawler import CrawlerService
from backend.vector import VectorService
from backend.graph import GraphService

from .router import router # Import router

logger = logging.getLogger(__name__)

class GatewayService:
    def __init__(self):
        self.app = None
        self.services = {}
        self.service_registry = {}
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all service instances."""
        try:
            # Initialize all services
            self.services["search"] = SearchService()
            self.services["fact_check"] = FactCheckService()
            self.services["synthesis"] = SynthesisService()
            self.services["auth"] = AuthService()
            self.services["crawler"] = CrawlerService()
            self.services["vector"] = VectorService()
            self.services["graph"] = GraphService()
            
            # Register services
            for name, service in self.services.items():
                self.service_registry[name] = service
                logger.info(f"Initialized {name} service")
            
            logger.info("All services initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing services: {e}")
            raise
    
    def create_app(self) -> FastAPI:
        """Create and configure the FastAPI application."""
        app = FastAPI(
            title="Universal Knowledge Hub API",
            description="API Gateway for the Universal Knowledge Platform",
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
        
        # Add global exception handler
        @app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            logger.error(f"Global exception handler: {exc}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
        
        # Include the router
        app.include_router(router, prefix="/api/v1")
        
        self.app = app
        return app
    
    async def get_services_health(self) -> Dict[str, Any]:
        """Get health status of all services."""
        health_status = {}
        
        for name, service in self.services.items():
            try:
                status = await service.get_status()
                health_status[name] = status
            except Exception as e:
                logger.error(f"Error getting {name} service status: {e}")
                health_status[name] = {"status": "error", "error": str(e)}
        
        return health_status
    
    async def route_request(self, service_name: str, method: str, **kwargs) -> Any:
        """Route request to appropriate service."""
        if service_name not in self.services:
            raise ValueError(f"Service {service_name} not found")
        
        service = self.services[service_name]
        
        if not hasattr(service, method):
            raise ValueError(f"Method {method} not found in {service_name} service")
        
        method_func = getattr(service, method)
        return await method_func(**kwargs)
    
    async def orchestrate_search(self, query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Orchestrate search across multiple services."""
        try:
            # Perform search
            search_results = await self.services["search"].search(query, filters)
            
            # Get vector search results
            vector_results = await self.services["vector"].search_similar(query)
            
            # Get graph results
            graph_results = await self.services["graph"].query_graph(f"FOR doc IN entities FILTER doc.name CONTAINS '{query}' RETURN doc")
            
            return {
                "search_results": search_results,
                "vector_results": vector_results,
                "graph_results": graph_results,
                "query": query
            }
        except Exception as e:
            logger.error(f"Error orchestrating search: {e}")
            raise
    
    async def orchestrate_fact_check(self, claim: str, sources: List[str] = None) -> Dict[str, Any]:
        """Orchestrate fact-checking process."""
        try:
            # Perform fact-checking
            fact_check_result = await self.services["fact_check"].fact_check(claim, sources)
            
            # Get related information from search
            search_results = await self.services["search"].search(claim)
            
            # Get vector similarity for claim
            vector_results = await self.services["vector"].search_similar(claim)
            
            return {
                "fact_check_result": fact_check_result,
                "search_results": search_results,
                "vector_results": vector_results,
                "claim": claim
            }
        except Exception as e:
            logger.error(f"Error orchestrating fact-check: {e}")
            raise
    
    async def orchestrate_synthesis(self, content: str, style: str = "academic") -> Dict[str, Any]:
        """Orchestrate content synthesis."""
        try:
            # Perform synthesis
            synthesis_result = await self.services["synthesis"].synthesize(content, style)
            
            # Generate citations
            citations = await self.services["synthesis"].generate_citations(content)
            
            # Get related content from search
            search_results = await self.services["search"].search(content[:100])  # Use first 100 chars
            
            return {
                "synthesis_result": synthesis_result,
                "citations": citations,
                "search_results": search_results,
                "content": content
            }
        except Exception as e:
            logger.error(f"Error orchestrating synthesis: {e}")
            raise
    
    async def startup(self):
        """Startup the gateway service."""
        logger.info("Starting Gateway Service...")
        
        # Create the FastAPI app
        self.create_app()
        
        # Initialize all services
        for name, service in self.services.items():
            if hasattr(service, 'startup'):
                await service.startup()
        
        logger.info("Gateway Service started successfully")
    
    async def shutdown(self):
        """Shutdown the gateway service."""
        logger.info("Shutting down Gateway Service...")
        
        # Shutdown all services
        for name, service in self.services.items():
            if hasattr(service, 'shutdown'):
                await service.shutdown()
        
        logger.info("Gateway Service shut down successfully")
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application."""
        if not self.app:
            self.create_app()
        return self.app 