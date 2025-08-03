"""
Crawler Microservice API
RESTful API endpoints for the crawler service.

This module provides:
- Web crawling endpoints
- Content extraction endpoints
- Health check endpoints
- Error handling
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from .crawler_service import CrawlerService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/crawler", tags=["crawler"])

# Initialize service
crawler_service = CrawlerService()

# Request/Response Models
class CrawlRequest(BaseModel):
    url: str
    depth: int = 1
    max_pages: int = 10

class CrawlResponse(BaseModel):
    content: str
    links: List[str]
    metadata: Dict[str, Any]
    crawl_time_ms: int
    crawl_id: str
    status: str

class ExtractRequest(BaseModel):
    url: str

class ExtractResponse(BaseModel):
    url: str
    content: str
    metadata: Dict[str, Any]
    status: str

class HealthCheckResponse(BaseModel):
    service: str
    status: str
    components: Dict[str, str]
    timestamp: str

@router.post("/crawl", response_model=CrawlResponse)
async def crawl_website(request: CrawlRequest):
    """Crawl a website and extract content."""
    try:
        logger.info(f"Processing crawl request for URL: {request.url}")
        
        result = await crawler_service.crawl_url(
            url=request.url,
            depth=request.depth,
            max_pages=request.max_pages
        )
        
        return CrawlResponse(**result)
        
    except Exception as e:
        logger.error(f"Crawl failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/crawl/{crawl_id}")
async def get_crawl_result(crawl_id: str):
    """Get a specific crawl result by ID."""
    try:
        result = await crawler_service.get_crawl_result(crawl_id)
        return result
    except Exception as e:
        logger.error(f"Failed to get crawl result {crawl_id}: {e}")
        raise HTTPException(status_code=404, detail="Crawl result not found")

@router.post("/extract", response_model=ExtractResponse)
async def extract_content(request: ExtractRequest):
    """Extract content from a single URL."""
    try:
        logger.info(f"Processing content extraction for URL: {request.url}")
        
        result = await crawler_service.extract_content(request.url)
        
        return ExtractResponse(**result)
        
    except Exception as e:
        logger.error(f"Content extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint for the crawler service."""
    try:
        health = await crawler_service.health_check()
        return HealthCheckResponse(**health)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@router.get("/status")
async def service_status():
    """Get detailed service status."""
    try:
        health = await crawler_service.health_check()
        return {
            "service": "crawler",
            "version": "2.0.0",
            "status": health.get("status", "unknown"),
            "components": health.get("components", {}),
            "endpoints": {
                "crawl": "/api/v1/crawler/crawl",
                "extract": "/api/v1/crawler/extract",
                "health": "/api/v1/crawler/health"
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 