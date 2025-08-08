"""
Agent Router for Clean Architecture Backend

This module provides the main agent router that includes all individual agent endpoints.
Migrated from the original services/api_gateway/routes/agents structure.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request

from ..dependencies import get_agent_service, get_current_user
from ...services.agents.agent_service import AgentService
from ...models.requests import AgentRequest
from ...models.responses import AgentResponse
from ...utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])


class AgentResponseFormatter:
    """Handles consistent response formatting for all agents."""
    
    @staticmethod
    def format_success(
        agent_id: str,
        result: Dict[str, Any],
        processing_time: float,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous"
    ) -> AgentResponse:
        """Format a successful agent response."""
        if metadata is None:
            metadata = {}
        
        metadata["user_id"] = user_id
        
        return AgentResponse(
            agent_id=agent_id,
            status="completed",
            result=result,
            processing_time=processing_time,
            metadata=metadata
        )
    
    @staticmethod
    def format_error(
        agent_id: str,
        error_message: str,
        processing_time: float,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous"
    ) -> AgentResponse:
        """Format an error response."""
        if metadata is None:
            metadata = {}
        
        metadata["user_id"] = user_id
        metadata["error"] = error_message
        
        return AgentResponse(
            agent_id=agent_id,
            status="failed",
            result={"error": error_message},
            processing_time=processing_time,
            metadata=metadata
        )


class AgentErrorHandler:
    """Handles error processing for agent operations."""
    
    @staticmethod
    def handle_agent_error(
        agent_id: str,
        error: Exception,
        operation: str,
        user_id: str = "anonymous"
    ) -> AgentResponse:
        """Handle and format agent errors."""
        error_message = f"{operation} failed: {str(error)}"
        logger.error(f"Agent {agent_id} error: {error_message}")
        
        return AgentResponseFormatter.format_error(
            agent_id=agent_id,
            error_message=error_message,
            processing_time=0.0,
            user_id=user_id
        )
    
    @staticmethod
    def validate_request(request: Dict[str, Any], required_fields: list) -> None:
        """Validate request has required fields."""
        missing_fields = [field for field in required_fields if not request.get(field)]
        
        if missing_fields:
            raise HTTPException(
                status_code=422,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )


class AgentPerformanceTracker:
    """Tracks performance metrics for agent operations."""
    
    def __init__(self):
        self.start_time = None
    
    def start_tracking(self) -> None:
        """Start tracking processing time."""
        self.start_time = datetime.now()
    
    def get_processing_time(self) -> float:
        """Get processing time in seconds."""
        if self.start_time is None:
            return 0.0
        return (datetime.now() - self.start_time).total_seconds()


def get_user_id(current_user) -> str:
    """Extract user ID from current user."""
    return current_user.get("user_id", "anonymous") if current_user else "anonymous"


def create_agent_metadata(
    user_id: str,
    **additional_metadata
) -> Dict[str, Any]:
    """Create metadata for agent operations."""
    metadata = {
        "user_id": user_id,
        "timestamp": datetime.now().isoformat()
    }
    metadata.update(additional_metadata)
    return metadata


# Main agent endpoints
@router.get("/health")
async def agents_health_check(
    current_user = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentResponse:
    """Health check for all agent services."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        # Check health of all agent services
        health_status = await agent_service.get_health_status()
        
        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)
        
        return AgentResponseFormatter.format_success(
            agent_id="agents-health-check",
            result=health_status,
            processing_time=processing_time,
            metadata={"service": "agents"},
            user_id=user_id
        )
        
    except Exception as e:
        processing_time = tracker.get_processing_time()
        return AgentErrorHandler.handle_agent_error(
            agent_id="agents-health-check",
            error=e,
            operation="health check",
            user_id=get_user_id(current_user)
        )


@router.get("/status")
async def agents_status(
    current_user = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentResponse:
    """Get detailed status of all agent services."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        # Get detailed status of all agent services
        status_info = await agent_service.get_status_info()
        
        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)
        
        return AgentResponseFormatter.format_success(
            agent_id="agents-status",
            result=status_info,
            processing_time=processing_time,
            metadata={"service": "agents"},
            user_id=user_id
        )
        
    except Exception as e:
        processing_time = tracker.get_processing_time()
        return AgentErrorHandler.handle_agent_error(
            agent_id="agents-status",
            error=e,
            operation="status check",
            user_id=get_user_id(current_user)
        )


# Browser Agent endpoints
@router.post("/browser/search")
async def browser_search(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentResponse:
    """Execute browser search using the agent service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        # Validate request
        AgentErrorHandler.validate_request(request, ["query"])
        
        # Execute browser search using service
        search_results = await agent_service.execute_browser_search(
            query=request.get("query", ""),
            search_type=request.get("search_type", "web"),
            max_results=request.get("max_results", 10),
            parameters=request.get("parameters", {})
        )
        
        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)
        
        return AgentResponseFormatter.format_success(
            agent_id="browser_search",
            result=search_results,
            processing_time=processing_time,
            metadata=create_agent_metadata(
                user_id=user_id,
                search_type=request.get("search_type", "web"),
                max_results=request.get("max_results", 10)
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
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentResponse:
    """Extract content from a URL using the agent service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        # Validate request
        AgentErrorHandler.validate_request(request, ["url"])
        
        # Extract content using service
        extraction_results = await agent_service.extract_browser_content(
            url=request.get("url", ""),
            extraction_type=request.get("extraction_type", "full"),
            parameters=request.get("parameters", {})
        )
        
        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)
        
        return AgentResponseFormatter.format_success(
            agent_id="browser_extract",
            result=extraction_results,
            processing_time=processing_time,
            metadata=create_agent_metadata(
                user_id=user_id,
                url=request.get("url", ""),
                extraction_type=request.get("extraction_type", "full")
            ),
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="browser_extract",
            error=e,
            operation="Browser content extraction",
            user_id=get_user_id(current_user)
        )


# PDF Agent endpoints
@router.post("/pdf/process")
async def pdf_process(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentResponse:
    """Process PDF documents using the agent service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        # Validate request
        AgentErrorHandler.validate_request(request, ["file_data"])
        
        # Process PDF using service
        processing_results = await agent_service.process_pdf(
            file_data=request.get("file_data"),
            processing_options=request.get("processing_options", {}),
            extraction_type=request.get("extraction_type", "text")
        )
        
        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)
        
        return AgentResponseFormatter.format_success(
            agent_id="pdf_process",
            result=processing_results,
            processing_time=processing_time,
            metadata=create_agent_metadata(
                user_id=user_id,
                extraction_type=request.get("extraction_type", "text")
            ),
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="pdf_process",
            error=e,
            operation="PDF processing",
            user_id=get_user_id(current_user)
        )


# Knowledge Graph Agent endpoints
@router.post("/knowledge/query")
async def knowledge_query(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentResponse:
    """Query knowledge graph using the agent service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        # Validate request
        AgentErrorHandler.validate_request(request, ["query"])
        
        # Query knowledge graph using service
        query_results = await agent_service.query_knowledge_graph(
            query=request.get("query", ""),
            query_type=request.get("query_type", "entities"),
            parameters=request.get("parameters", {})
        )
        
        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)
        
        return AgentResponseFormatter.format_success(
            agent_id="knowledge_query",
            result=query_results,
            processing_time=processing_time,
            metadata=create_agent_metadata(
                user_id=user_id,
                query_type=request.get("query_type", "entities")
            ),
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="knowledge_query",
            error=e,
            operation="Knowledge graph query",
            user_id=get_user_id(current_user)
        )


# Code Agent endpoints
@router.post("/code/execute")
async def code_execute(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentResponse:
    """Execute code using the agent service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        # Validate request
        AgentErrorHandler.validate_request(request, ["code"])
        
        # Execute code using service
        execution_results = await agent_service.execute_code(
            code=request.get("code", ""),
            language=request.get("language", "python"),
            parameters=request.get("parameters", {})
        )
        
        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)
        
        return AgentResponseFormatter.format_success(
            agent_id="code_execute",
            result=execution_results,
            processing_time=processing_time,
            metadata=create_agent_metadata(
                user_id=user_id,
                language=request.get("language", "python")
            ),
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="code_execute",
            error=e,
            operation="Code execution",
            user_id=get_user_id(current_user)
        )


# Database Agent endpoints
@router.post("/database/query")
async def database_query(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentResponse:
    """Execute database query using the agent service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        # Validate request
        AgentErrorHandler.validate_request(request, ["query"])
        
        # Execute database query using service
        query_results = await agent_service.execute_database_query(
            query=request.get("query", ""),
            database_type=request.get("database_type", "postgres"),
            parameters=request.get("parameters", {})
        )
        
        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)
        
        return AgentResponseFormatter.format_success(
            agent_id="database_query",
            result=query_results,
            processing_time=processing_time,
            metadata=create_agent_metadata(
                user_id=user_id,
                database_type=request.get("database_type", "postgres")
            ),
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="database_query",
            error=e,
            operation="Database query",
            user_id=get_user_id(current_user)
        )


# Crawler Agent endpoints
@router.post("/crawler/crawl")
async def crawler_crawl(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentResponse:
    """Crawl websites using the agent service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        # Validate request
        AgentErrorHandler.validate_request(request, ["url"])
        
        # Crawl website using service
        crawl_results = await agent_service.crawl_website(
            url=request.get("url", ""),
            crawl_type=request.get("crawl_type", "full"),
            parameters=request.get("parameters", {})
        )
        
        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)
        
        return AgentResponseFormatter.format_success(
            agent_id="crawler_crawl",
            result=crawl_results,
            processing_time=processing_time,
            metadata=create_agent_metadata(
                user_id=user_id,
                url=request.get("url", ""),
                crawl_type=request.get("crawl_type", "full")
            ),
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="crawler_crawl",
            error=e,
            operation="Website crawling",
            user_id=get_user_id(current_user)
        ) 