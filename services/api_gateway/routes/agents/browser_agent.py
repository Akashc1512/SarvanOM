"""
Browser Agent Route Handler
Handles web search and browser-related operations using BrowserService.
"""

import logging
from shared.core.unified_logging import get_logger
from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, Depends

from .base import (
    AgentResponseFormatter,
    AgentErrorHandler,
    AgentPerformanceTracker,
    get_user_id,
    create_agent_metadata
)
from ...models.requests import BrowserSearchRequest
from ...models.responses import AgentResponse
from ...middleware import get_current_user
from ...di import get_browser_service
from ...services.browser_service import BrowserService

logger = get_logger(__name__)

router = APIRouter()


@router.post("/browser/search")
async def browser_search(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user),
    browser_service: BrowserService = Depends(get_browser_service)
) -> AgentResponse:
    """Execute browser search using the browser service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        # Validate request
        AgentErrorHandler.validate_request(request, ["query"])
        
        search_request = BrowserSearchRequest(
            query=request.get("query", ""),
            search_type=request.get("search_type", "web"),
            max_results=request.get("max_results", 10),
            parameters=request.get("parameters", {}),
            context=request.get("context", {})
        )
        
        # Execute browser search using service
        search_results = await browser_service.search_web(
            query=search_request.query,
            search_engine=search_request.search_type,
            max_results=search_request.max_results,
            parameters=search_request.parameters
        )
        
        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)
        
        return AgentResponseFormatter.format_success(
            agent_id="browser_search",
            result=search_results,
            processing_time=processing_time,
            metadata=create_agent_metadata(
                user_id=user_id,
                search_type=search_request.search_type,
                max_results=search_request.max_results
            ),
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="browser_search",
            error=e,
            operation="Browser search",
            user_id=get_user_id(current_user)
        )


@router.post("/browser/extract")
async def browser_extract_content(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user),
    browser_service: BrowserService = Depends(get_browser_service)
) -> AgentResponse:
    """Extract content from a URL using the browser service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        # Validate request
        AgentErrorHandler.validate_request(request, ["url"])
        
        url = request.get("url", "")
        extract_images = request.get("extract_images", False)
        extract_links = request.get("extract_links", True)
        
        # Extract content using service
        content_result = await browser_service.extract_content(
            url=url,
            extract_images=extract_images,
            extract_links=extract_links
        )
        
        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)
        
        return AgentResponseFormatter.format_success(
            agent_id="browser_extract",
            result=content_result,
            processing_time=processing_time,
            metadata=create_agent_metadata(
                user_id=user_id,
                url=url,
                extract_images=extract_images,
                extract_links=extract_links
            ),
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="browser_extract",
            error=e,
            operation="Content extraction",
            user_id=get_user_id(current_user)
        )


@router.post("/browser/browse")
async def browser_browse_page(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user),
    browser_service: BrowserService = Depends(get_browser_service)
) -> AgentResponse:
    """Browse a page and follow links using the browser service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        # Validate request
        AgentErrorHandler.validate_request(request, ["url"])
        
        url = request.get("url", "")
        follow_links = request.get("follow_links", False)
        max_links = request.get("max_links", 5)
        
        # Browse page using service
        browse_result = await browser_service.browse_page(
            url=url,
            follow_links=follow_links,
            max_links=max_links
        )
        
        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)
        
        return AgentResponseFormatter.format_success(
            agent_id="browser_browse",
            result=browse_result,
            processing_time=processing_time,
            metadata=create_agent_metadata(
                user_id=user_id,
                url=url,
                follow_links=follow_links,
                max_links=max_links
            ),
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="browser_browse",
            error=e,
            operation="Page browsing",
            user_id=get_user_id(current_user)
        )


@router.get("/browser/health")
async def browser_health(
    current_user=Depends(get_current_user),
    browser_service: BrowserService = Depends(get_browser_service)
) -> AgentResponse:
    """Get browser service health status."""
    try:
        health_status = await browser_service.health_check()
        
        return AgentResponseFormatter.format_success(
            agent_id="browser_health",
            result=health_status,
            processing_time=0.0,
            metadata=create_agent_metadata(
                user_id=get_user_id(current_user),
                health_check=True
            ),
            user_id=get_user_id(current_user)
        )
        
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="browser_health",
            error=e,
            operation="Health check",
            user_id=get_user_id(current_user)
        )


@router.get("/browser/status")
async def browser_status(
    current_user=Depends(get_current_user),
    browser_service: BrowserService = Depends(get_browser_service)
) -> AgentResponse:
    """Get browser service detailed status."""
    try:
        status_info = await browser_service.get_status()
        
        return AgentResponseFormatter.format_success(
            agent_id="browser_status",
            result=status_info,
            processing_time=0.0,
            metadata=create_agent_metadata(
                user_id=get_user_id(current_user),
                status_check=True
            ),
            user_id=get_user_id(current_user)
        )
        
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="browser_status",
            error=e,
            operation="Status check",
            user_id=get_user_id(current_user)
        ) 