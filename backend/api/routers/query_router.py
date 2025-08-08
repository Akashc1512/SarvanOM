"""
Query Router

This module contains all query-related API endpoints.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from ...models.requests.query_requests import (
    QueryRequest, 
    ComprehensiveQueryRequest, 
    QueryUpdateRequest,
    QueryListRequest,
    QueryReprocessRequest
)
from ...models.responses.query_responses import (
    QueryResponse, 
    ComprehensiveQueryResponse,
    QueryListResponse,
    QueryDetailResponse,
    QueryStatusResponse,
    QueryReprocessResponse,
    ErrorResponse
)
from ...services.query.query_orchestrator import QueryOrchestrator
from ..dependencies import get_query_orchestrator, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["queries"])


@router.post("/", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    http_request: Request,
    current_user=Depends(get_current_user),
    orchestrator: QueryOrchestrator = Depends(get_query_orchestrator)
) -> QueryResponse:
    """Process a basic query."""
    try:
        user_context = {
            "user_id": getattr(current_user, "user_id", "anonymous"),
            "session_id": request.session_id,
            "max_tokens": request.max_tokens,
            "confidence_threshold": request.confidence_threshold
        }
        
        result = await orchestrator.process_basic_query(request, user_context)
        return result
        
    except ValueError as e:
        logger.warning(f"Query validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/comprehensive", response_model=ComprehensiveQueryResponse)
async def process_comprehensive_query(
    request: ComprehensiveQueryRequest,
    http_request: Request,
    current_user=Depends(get_current_user),
    orchestrator: QueryOrchestrator = Depends(get_query_orchestrator)
) -> ComprehensiveQueryResponse:
    """Process a comprehensive query."""
    try:
        user_context = {
            "user_id": getattr(current_user, "user_id", "anonymous"),
            "session_id": request.session_id,
            "max_tokens": request.max_tokens,
            "confidence_threshold": request.confidence_threshold
        }
        
        result = await orchestrator.process_comprehensive_query(request, user_context)
        return result
        
    except ValueError as e:
        logger.warning(f"Comprehensive query validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing comprehensive query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=QueryListResponse)
async def list_queries(
    page: int = 1,
    page_size: int = 20,
    user_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    http_request: Request = None,
    current_user=Depends(get_current_user),
    orchestrator: QueryOrchestrator = Depends(get_query_orchestrator)
) -> QueryListResponse:
    """List queries with pagination and filtering."""
    try:
        # TODO: Implement query listing functionality
        # For now, return empty list
        return QueryListResponse(
            queries=[],
            total_count=0,
            page=page,
            page_size=page_size,
            total_pages=0
        )
        
    except Exception as e:
        logger.error(f"Error listing queries: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{query_id}", response_model=QueryDetailResponse)
async def get_query(
    query_id: str,
    http_request: Request,
    current_user=Depends(get_current_user),
    orchestrator: QueryOrchestrator = Depends(get_query_orchestrator)
) -> QueryDetailResponse:
    """Get detailed information about a specific query."""
    try:
        # TODO: Implement query detail retrieval
        # For now, return a placeholder response
        raise HTTPException(status_code=404, detail="Query not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting query {query_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{query_id}", response_model=QueryDetailResponse)
async def update_query(
    query_id: str,
    update_request: QueryUpdateRequest,
    http_request: Request,
    current_user=Depends(get_current_user),
    orchestrator: QueryOrchestrator = Depends(get_query_orchestrator)
) -> QueryDetailResponse:
    """Update a query."""
    try:
        # TODO: Implement query update functionality
        raise HTTPException(status_code=404, detail="Query not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating query {query_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{query_id}")
async def delete_query(
    query_id: str,
    http_request: Request,
    current_user=Depends(get_current_user),
    orchestrator: QueryOrchestrator = Depends(get_query_orchestrator)
):
    """Delete a query."""
    try:
        # TODO: Implement query deletion functionality
        raise HTTPException(status_code=404, detail="Query not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting query {query_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{query_id}/status", response_model=QueryStatusResponse)
async def get_query_status(
    query_id: str,
    http_request: Request,
    current_user=Depends(get_current_user),
    orchestrator: QueryOrchestrator = Depends(get_query_orchestrator)
) -> QueryStatusResponse:
    """Get the status of a query."""
    try:
        status_info = await orchestrator.get_query_status(query_id)
        
        return QueryStatusResponse(
            query_id=query_id,
            status=status_info.get("status", "unknown"),
            progress=status_info.get("progress", 0.0),
            estimated_completion=status_info.get("estimated_completion"),
            current_step=status_info.get("current_step"),
            error_message=status_info.get("error_message"),
            created_at=status_info.get("created_at"),
            updated_at=status_info.get("updated_at")
        )
        
    except ValueError as e:
        logger.warning(f"Query status error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting query status {query_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{query_id}/reprocess", response_model=QueryReprocessResponse)
async def reprocess_query(
    query_id: str,
    reprocess_request: QueryReprocessRequest,
    http_request: Request,
    current_user=Depends(get_current_user),
    orchestrator: QueryOrchestrator = Depends(get_query_orchestrator)
) -> QueryReprocessResponse:
    """Reprocess a query."""
    try:
        # TODO: Implement query reprocessing functionality
        raise HTTPException(status_code=404, detail="Query not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reprocessing query {query_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") 