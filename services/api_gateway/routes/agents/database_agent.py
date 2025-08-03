"""
Database query agent routes.
Handles database queries, schema exploration, and data analysis using DatabaseService.
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
from ...di import get_database_service
from ...services.database_service import DatabaseService

logger = logging.getLogger(__name__)

database_router = APIRouter(prefix="/database", tags=["database-query"])


@database_router.post("/query")
async def execute_database_query(
    request: Dict[str, Any],
    current_user = Depends(get_current_user),
    database_service: DatabaseService = Depends(get_database_service)
) -> AgentResponse:
    """
    Execute a database query and return results using database service.
    
    Expected request format:
    {
        "query": "SELECT * FROM users WHERE age > 25",
        "database_name": "my_database",
        "params": {"optional": "parameters"},
        "timeout": 30
    }
    """
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        user_id = get_user_id(current_user)
        
        # Validate request
        AgentErrorHandler.validate_request(request, ["query", "database_name"])
        
        query = request.get("query", "")
        database_name = request.get("database_name", "")
        params = request.get("params", {})
        timeout = request.get("timeout", 30)
        
        # Execute the query using service
        result = await database_service.execute_query(
            database_name=database_name,
            query=query,
            params=params,
            timeout=timeout
        )
        
        processing_time = tracker.get_processing_time()
        metadata = create_agent_metadata(
            user_id, 
            database_name=database_name, 
            timeout=timeout,
            query_length=len(query)
        )
        
        return AgentResponseFormatter.format_success(
            agent_id="database-query",
            result=result,
            processing_time=processing_time,
            metadata=metadata,
            user_id=user_id
        )
        
    except Exception as e:
        processing_time = tracker.get_processing_time()
        return AgentErrorHandler.handle_agent_error(
            agent_id="database-query",
            error=e,
            operation="database query execution",
            user_id=get_user_id(current_user)
        )


@database_router.post("/schema")
async def get_database_schema(
    request: Dict[str, Any],
    current_user = Depends(get_current_user),
    database_service: DatabaseService = Depends(get_database_service)
) -> AgentResponse:
    """
    Get database schema information using database service.
    
    Expected request format:
    {
        "database_name": "my_database"
    }
    """
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        user_id = get_user_id(current_user)
        
        # Validate request
        AgentErrorHandler.validate_request(request, ["database_name"])
        
        database_name = request.get("database_name", "")
        
        # Get schema using service
        result = await database_service.get_schema(database_name=database_name)
        
        processing_time = tracker.get_processing_time()
        metadata = create_agent_metadata(user_id, database_name=database_name)
        
        return AgentResponseFormatter.format_success(
            agent_id="database-schema",
            result=result,
            processing_time=processing_time,
            metadata=metadata,
            user_id=user_id
        )
        
    except Exception as e:
        processing_time = tracker.get_processing_time()
        return AgentErrorHandler.handle_agent_error(
            agent_id="database-schema",
            error=e,
            operation="database schema retrieval",
            user_id=get_user_id(current_user)
        )


@database_router.post("/analyze")
async def analyze_database_data(
    request: Dict[str, Any],
    current_user = Depends(get_current_user),
    database_service: DatabaseService = Depends(get_database_service)
) -> AgentResponse:
    """
    Analyze database data using database service.
    
    Expected request format:
    {
        "database_name": "my_database",
        "table_name": "users",
        "columns": ["optional", "columns", "to", "analyze"]
    }
    """
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        user_id = get_user_id(current_user)
        
        # Validate request
        AgentErrorHandler.validate_request(request, ["database_name", "table_name"])
        
        database_name = request.get("database_name", "")
        table_name = request.get("table_name", "")
        columns = request.get("columns", None)
        
        # Analyze data using service
        result = await database_service.analyze_data(
            database_name=database_name,
            table_name=table_name,
            columns=columns
        )
        
        processing_time = tracker.get_processing_time()
        metadata = create_agent_metadata(
            user_id, 
            database_name=database_name,
            table_name=table_name
        )
        
        return AgentResponseFormatter.format_success(
            agent_id="database-analyzer",
            result=result,
            processing_time=processing_time,
            metadata=metadata,
            user_id=user_id
        )
        
    except Exception as e:
        processing_time = tracker.get_processing_time()
        return AgentErrorHandler.handle_agent_error(
            agent_id="database-analyzer",
            error=e,
            operation="database data analysis",
            user_id=get_user_id(current_user)
        )


@database_router.post("/optimize")
async def optimize_database_query(
    request: Dict[str, Any],
    current_user = Depends(get_current_user),
    database_service: DatabaseService = Depends(get_database_service)
) -> AgentResponse:
    """
    Optimize database query using database service.
    
    Expected request format:
    {
        "database_name": "my_database",
        "query": "SELECT * FROM users WHERE age > 25"
    }
    """
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        user_id = get_user_id(current_user)
        
        # Validate request
        AgentErrorHandler.validate_request(request, ["database_name", "query"])
        
        database_name = request.get("database_name", "")
        query = request.get("query", "")
        
        # Optimize query using service
        result = await database_service.optimize_query(
            database_name=database_name,
            query=query
        )
        
        processing_time = tracker.get_processing_time()
        metadata = create_agent_metadata(
            user_id, 
            database_name=database_name,
            query_length=len(query)
        )
        
        return AgentResponseFormatter.format_success(
            agent_id="database-optimizer",
            result=result,
            processing_time=processing_time,
            metadata=metadata,
            user_id=user_id
        )
        
    except Exception as e:
        processing_time = tracker.get_processing_time()
        return AgentErrorHandler.handle_agent_error(
            agent_id="database-optimizer",
            error=e,
            operation="database query optimization",
            user_id=get_user_id(current_user)
        )


@database_router.get("/databases")
async def list_databases(
    current_user = Depends(get_current_user),
    database_service: DatabaseService = Depends(get_database_service)
) -> AgentResponse:
    """List available databases using database service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        user_id = get_user_id(current_user)
        
        # List databases using service
        result = await database_service.list_databases()
        
        processing_time = tracker.get_processing_time()
        metadata = create_agent_metadata(user_id)
        
        return AgentResponseFormatter.format_success(
            agent_id="database-lister",
            result=result,
            processing_time=processing_time,
            metadata=metadata,
            user_id=user_id
        )
        
    except Exception as e:
        processing_time = tracker.get_processing_time()
        return AgentErrorHandler.handle_agent_error(
            agent_id="database-lister",
            error=e,
            operation="database listing",
            user_id=get_user_id(current_user)
        )


@database_router.post("/test-connection")
async def test_database_connection(
    request: Dict[str, Any],
    current_user = Depends(get_current_user),
    database_service: DatabaseService = Depends(get_database_service)
) -> AgentResponse:
    """
    Test database connection using database service.
    
    Expected request format:
    {
        "database_name": "my_database"
    }
    """
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        user_id = get_user_id(current_user)
        
        # Validate request
        AgentErrorHandler.validate_request(request, ["database_name"])
        
        database_name = request.get("database_name", "")
        
        # Test connection using service
        result = await database_service.test_connection(database_name=database_name)
        
        processing_time = tracker.get_processing_time()
        metadata = create_agent_metadata(user_id, database_name=database_name)
        
        return AgentResponseFormatter.format_success(
            agent_id="database-connection-tester",
            result=result,
            processing_time=processing_time,
            metadata=metadata,
            user_id=user_id
        )
        
    except Exception as e:
        processing_time = tracker.get_processing_time()
        return AgentErrorHandler.handle_agent_error(
            agent_id="database-connection-tester",
            error=e,
            operation="database connection testing",
            user_id=get_user_id(current_user)
        )


@database_router.get("/health")
async def database_health(
    current_user = Depends(get_current_user),
    database_service: DatabaseService = Depends(get_database_service)
) -> AgentResponse:
    """Get database service health status."""
    try:
        health_status = await database_service.health_check()
        
        return AgentResponseFormatter.format_success(
            agent_id="database-health",
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
            agent_id="database-health",
            error=e,
            operation="health check",
            user_id=get_user_id(current_user)
        )


@database_router.get("/status")
async def database_status(
    current_user = Depends(get_current_user),
    database_service: DatabaseService = Depends(get_database_service)
) -> AgentResponse:
    """Get database service detailed status."""
    try:
        status_info = await database_service.get_status()
        
        return AgentResponseFormatter.format_success(
            agent_id="database-status",
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
            agent_id="database-status",
            error=e,
            operation="status check",
            user_id=get_user_id(current_user)
        ) 