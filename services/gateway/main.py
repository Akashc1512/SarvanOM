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

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Universal Knowledge Platform API Gateway",
    description="API Gateway for routing requests to microservices",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class SearchRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None

class FactCheckRequest(BaseModel):
    content: str
    user_id: Optional[str] = None
    context: Optional[str] = None

class SynthesisRequest(BaseModel):
    query: str
    sources: Optional[list] = None
    user_id: Optional[str] = None

class AuthRequest(BaseModel):
    username: str
    password: str

class CrawlRequest(BaseModel):
    url: str
    depth: Optional[int] = 1
    user_id: Optional[str] = None

class VectorSearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10
    filters: Optional[Dict[str, Any]] = None

class GraphContextRequest(BaseModel):
    topic: str
    depth: Optional[int] = 2
    user_id: Optional[str] = None

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for the API gateway."""
    return {"status": "ok"}

# Search/Retrieval service endpoint
@app.get("/search")
async def search_endpoint():
    """Placeholder for search/retrieval service."""
    return {"message": "Retrieval service route"}

@app.post("/search")
async def search_post(request: SearchRequest):
    """Placeholder for search/retrieval service with POST."""
    return {
        "message": "Retrieval service route",
        "query": request.query,
        "user_id": request.user_id
    }

# Fact-check service endpoint
@app.post("/fact-check")
async def fact_check_endpoint(request: FactCheckRequest):
    """Placeholder for fact-check service."""
    return {
        "message": "Fact-check service route",
        "content": request.content,
        "user_id": request.user_id
    }

# Synthesis service endpoint
@app.post("/synthesize")
async def synthesize_endpoint(request: SynthesisRequest):
    """Placeholder for synthesis service."""
    return {
        "message": "Synthesis service route",
        "query": request.query,
        "user_id": request.user_id
    }

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
    return {
        "message": "Knowledge graph service route",
        "topic": topic,
        "depth": depth,
        "user_id": user_id
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
    """Placeholder for analytics service."""
    return {"message": "Analytics service route"}

@app.post("/analytics/track")
async def analytics_track_endpoint():
    """Placeholder for analytics tracking."""
    return {"message": "Analytics tracking route"}

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
        "health": "/health"
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "message": "The requested endpoint does not exist"}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "message": "An unexpected error occurred"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 