"""
Web crawler agent routes.
Handles web crawling, content extraction, and link discovery using CrawlerService.
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from ..base import (
    AgentResponseFormatter,
    AgentErrorHandler,
    AgentPerformanceTracker,
    get_user_id,
    create_agent_metadata
)
from ..models.responses import AgentResponse
from ...middleware import get_current_user
from ...di import get_crawler_service
from ...services.crawler_service import CrawlerService

logger = logging.getLogger(__name__)

crawler_router = APIRouter(prefix="/crawler", tags=["web-crawler"])


@crawler_router.post("/crawl")
async def crawl_website(
    request: Dict[str, Any],
    current_user = Depends(get_current_user),
    crawler_service: CrawlerService = Depends(get_crawler_service)
) -> AgentResponse:
    """
    Crawl a website and extract content using crawler service.
    
    Expected request format:
    {
        "url": "https://example.com",
        "max_depth": 2,
        "max_pages": 10,
        "follow_links": true,
        "extract_content": true
    }
    """
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        user_id = get_user_id(current_user)
        
        # Validate request
        AgentErrorHandler.validate_request(request, ["url"])
        
        url = request.get("url", "")
        max_depth = request.get("max_depth", 2)
        max_pages = request.get("max_pages", 10)
        
        # Crawl the website using service
        result = await crawler_service.crawl_website(
            start_url=url,
            max_depth=max_depth,
            max_pages=max_pages
        )
        
        processing_time = tracker.get_processing_time()
        metadata = create_agent_metadata(
            user_id, 
            url=url,
            max_depth=max_depth,
            max_pages=max_pages,
            pages_crawled=len(result.get("pages_crawled", []))
        )
        
        return AgentResponseFormatter.format_success(
            agent_id="web-crawler",
            result=result,
            processing_time=processing_time,
            metadata=metadata,
            user_id=user_id
        )
        
    except Exception as e:
        processing_time = tracker.get_processing_time()
        return AgentErrorHandler.handle_agent_error(
            agent_id="web-crawler",
            error=e,
            operation="website crawling",
            user_id=get_user_id(current_user)
        )


@crawler_router.post("/extract")
async def extract_content(
    request: Dict[str, Any],
    current_user = Depends(get_current_user),
    crawler_service: CrawlerService = Depends(get_crawler_service)
) -> AgentResponse:
    """
    Extract content from a single webpage using crawler service.
    
    Expected request format:
    {
        "url": "https://example.com",
        "extract_images": true,
        "extract_links": true
    }
    """
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        user_id = get_user_id(current_user)
        
        # Validate request
        AgentErrorHandler.validate_request(request, ["url"])
        
        url = request.get("url", "")
        extract_images = request.get("extract_images", True)
        extract_links = request.get("extract_links", True)
        
        # Extract content using service
        result = await crawler_service.extract_content(
            url=url,
            extract_images=extract_images,
            extract_links=extract_links
        )
        
        processing_time = tracker.get_processing_time()
        metadata = create_agent_metadata(
            user_id, 
            url=url,
            extract_images=extract_images,
            extract_links=extract_links
        )
        
        return AgentResponseFormatter.format_success(
            agent_id="content-extractor",
            result=result,
            processing_time=processing_time,
            metadata=metadata,
            user_id=user_id
        )
        
    except Exception as e:
        processing_time = tracker.get_processing_time()
        return AgentErrorHandler.handle_agent_error(
            agent_id="content-extractor",
            error=e,
            operation="content extraction",
            user_id=get_user_id(current_user)
        )


@crawler_router.post("/discover")
async def discover_links(
    request: Dict[str, Any],
    current_user = Depends(get_current_user),
    crawler_service: CrawlerService = Depends(get_crawler_service)
) -> AgentResponse:
    """
    Discover links from a webpage using crawler service.
    
    Expected request format:
    {
        "url": "https://example.com",
        "max_links": 50,
        "filter_domains": ["example.com"]
    }
    """
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        user_id = get_user_id(current_user)
        
        # Validate request
        AgentErrorHandler.validate_request(request, ["url"])
        
        url = request.get("url", "")
        max_links = request.get("max_links", 50)
        
        # Discover links using service
        result = await crawler_service.discover_links(
            url=url,
            max_links=max_links
        )
        
        processing_time = tracker.get_processing_time()
        metadata = create_agent_metadata(
            user_id, 
            url=url,
            max_links=max_links
        )
        
        return AgentResponseFormatter.format_success(
            agent_id="link-discoverer",
            result=result,
            processing_time=processing_time,
            metadata=metadata,
            user_id=user_id
        )
        
    except Exception as e:
        processing_time = tracker.get_processing_time()
        return AgentErrorHandler.handle_agent_error(
            agent_id="link-discoverer",
            error=e,
            operation="link discovery",
            user_id=get_user_id(current_user)
        )


@crawler_router.post("/sitemap")
async def generate_sitemap(
    request: Dict[str, Any],
    current_user = Depends(get_current_user),
    crawler_service: CrawlerService = Depends(get_crawler_service)
) -> AgentResponse:
    """
    Generate a sitemap for a website using crawler service.
    
    Expected request format:
    {
        "url": "https://example.com",
        "max_pages": 100,
        "include_priority": true
    }
    """
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        user_id = get_user_id(current_user)
        
        # Validate request
        AgentErrorHandler.validate_request(request, ["url"])
        
        url = request.get("url", "")
        max_pages = request.get("max_pages", 100)
        
        # Generate sitemap using service
        result = await crawler_service.generate_sitemap(
            start_url=url,
            max_pages=max_pages
        )
        
        processing_time = tracker.get_processing_time()
        metadata = create_agent_metadata(
            user_id, 
            url=url,
            max_pages=max_pages
        )
        
        return AgentResponseFormatter.format_success(
            agent_id="sitemap-generator",
            result=result,
            processing_time=processing_time,
            metadata=metadata,
            user_id=user_id
        )
        
    except Exception as e:
        processing_time = tracker.get_processing_time()
        return AgentErrorHandler.handle_agent_error(
            agent_id="sitemap-generator",
            error=e,
            operation="sitemap generation",
            user_id=get_user_id(current_user)
        )


@crawler_router.post("/crawl-filtered")
async def crawl_with_filters(
    request: Dict[str, Any],
    current_user = Depends(get_current_user),
    crawler_service: CrawlerService = Depends(get_crawler_service)
) -> AgentResponse:
    """
    Crawl website with URL filters using crawler service.
    
    Expected request format:
    {
        "url": "https://example.com",
        "include_patterns": ["*.html", "*.php"],
        "exclude_patterns": ["*.pdf", "*.zip"],
        "max_depth": 3
    }
    """
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        user_id = get_user_id(current_user)
        
        # Validate request
        AgentErrorHandler.validate_request(request, ["url"])
        
        url = request.get("url", "")
        include_patterns = request.get("include_patterns", [])
        exclude_patterns = request.get("exclude_patterns", [])
        max_depth = request.get("max_depth", 3)
        
        # Crawl with filters using service
        result = await crawler_service.crawl_with_filters(
            start_url=url,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            max_depth=max_depth
        )
        
        processing_time = tracker.get_processing_time()
        metadata = create_agent_metadata(
            user_id, 
            url=url,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            max_depth=max_depth
        )
        
        return AgentResponseFormatter.format_success(
            agent_id="filtered-crawler",
            result=result,
            processing_time=processing_time,
            metadata=metadata,
            user_id=user_id
        )
        
    except Exception as e:
        processing_time = tracker.get_processing_time()
        return AgentErrorHandler.handle_agent_error(
            agent_id="filtered-crawler",
            error=e,
            operation="filtered crawling",
            user_id=get_user_id(current_user)
        )


@crawler_router.get("/health")
async def crawler_health(
    current_user = Depends(get_current_user),
    crawler_service: CrawlerService = Depends(get_crawler_service)
) -> AgentResponse:
    """Get crawler service health status."""
    try:
        health_status = await crawler_service.health_check()
        
        return AgentResponseFormatter.format_success(
            agent_id="crawler-health",
            result=health_status,
            processing_time=0.0,
            metadata=create_agent_metadata(
                get_user_id(current_user),
                health_check=True
            ),
            user_id=get_user_id(current_user)
        )
        
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="crawler-health",
            error=e,
            operation="health check",
            user_id=get_user_id(current_user)
        )


@crawler_router.get("/status")
async def crawler_status(
    current_user = Depends(get_current_user),
    crawler_service: CrawlerService = Depends(get_crawler_service)
) -> AgentResponse:
    """Get crawler service detailed status."""
    try:
        status_info = await crawler_service.get_status()
        
        return AgentResponseFormatter.format_success(
            agent_id="crawler-status",
            result=status_info,
            processing_time=0.0,
            metadata=create_agent_metadata(
                get_user_id(current_user),
                status_check=True
            ),
            user_id=get_user_id(current_user)
        )
        
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="crawler-status",
            error=e,
            operation="status check",
            user_id=get_user_id(current_user)
        ) 