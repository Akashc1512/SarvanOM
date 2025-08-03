"""
Browser Agent Route Handler
Handles web search and browser-related operations.
"""

import logging
import aiohttp
import os
from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, Depends
from urllib.parse import quote_plus

from ..base import (
    AgentResponseFormatter,
    AgentErrorHandler,
    AgentPerformanceTracker,
    get_user_id,
    create_agent_metadata
)
from ...models.requests import BrowserSearchRequest
from ...middleware import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/browser/search")
async def browser_search(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user)
):
    """Execute browser search using the browser agent."""
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
        
        # Execute browser search
        search_results = await _execute_browser_search(search_request)
        
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


async def _execute_browser_search(search_request: BrowserSearchRequest) -> Dict[str, Any]:
    """Execute the actual browser search operation."""
    
    # Get search API configuration
    search_api_key = os.getenv('SEARCH_API_KEY', '')
    search_engine = search_request.search_type or 'google'
    
    if search_engine == 'google':
        return await _google_search(search_request, search_api_key)
    elif search_engine == 'bing':
        return await _bing_search(search_request)
    else:
        return await _fallback_search(search_request)


async def _google_search(search_request: BrowserSearchRequest, api_key: str) -> Dict[str, Any]:
    """Execute Google Custom Search."""
    if not api_key:
        logger.warning("Google API key not configured, using fallback search")
        return await _fallback_search(search_request)
    
    google_cse_id = os.getenv('GOOGLE_CSE_ID', '')
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': google_cse_id,
        'q': search_request.query,
        'num': min(search_request.max_results, 10)
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get('items', [])
                    
                    return {
                        "query": search_request.query,
                        "engine": "google",
                        "results": [
                            {
                                "title": item.get('title', ''),
                                "url": item.get('link', ''),
                                "snippet": item.get('snippet', '')
                            }
                            for item in items
                        ],
                        "total_results": data.get('searchInformation', {}).get('totalResults', 0)
                    }
                else:
                    logger.error(f"Google search failed with status {response.status}")
                    return await _fallback_search(search_request)
                    
    except Exception as e:
        logger.error(f"Google search error: {e}")
        return await _fallback_search(search_request)


async def _bing_search(search_request: BrowserSearchRequest) -> Dict[str, Any]:
    """Execute Bing search (placeholder implementation)."""
    logger.info("Bing search not implemented, using fallback")
    return await _fallback_search(search_request)


async def _fallback_search(search_request: BrowserSearchRequest) -> Dict[str, Any]:
    """Fallback search implementation with mock results."""
    return {
        "query": search_request.query,
        "engine": "fallback",
        "results": [
            {
                "title": f"Sample result for: {search_request.query}",
                "url": "https://example.com",
                "snippet": f"This is a sample search result for the query: {search_request.query}"
            }
        ],
        "total_results": 1,
        "note": "Using fallback search - configure API keys for real results"
    } 