"""
Database Router for Clean Architecture Backend

This module provides the database router that includes all database-related endpoints.
Migrated from the original services/api_gateway/routes structure.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request

from ..dependencies import get_database_service, get_current_user
from ...services.core.database_service import DatabaseService
from ...models.requests.database_requests import DatabaseQueryRequest, DatabaseAnalysisRequest
from ...models.responses.database_responses import DatabaseResponse, DatabaseListResponse
from ...utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/database", tags=["database"])


class DatabaseResponseFormatter:
    """Handles consistent response formatting for database operations."""
    
    @staticmethod
    def format_success(
        operation: str,
        result: Dict[str, Any],
        processing_time: float,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous"
    ) -> DatabaseResponse:
        """Format a successful database response."""
        if metadata is None:
            metadata = {}
        
        metadata["user_id"] = user_id
        metadata["operation"] = operation
        
        return DatabaseResponse(
            success=True,
            data=result,
            processing_time=processing_time,
            metadata=metadata,
            timestamp=datetime.now()
        )
    
    @staticmethod
    def format_error(
        operation: str,
        error_message: str,
        processing_time: float,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous"
    ) -> DatabaseResponse:
        """Format an error response."""
        if metadata is None:
            metadata = {}
        
        metadata["user_id"] = user_id
        metadata["operation"] = operation
        metadata["error"] = error_message
        
        return DatabaseResponse(
            success=False,
            error=error_message,
            processing_time=processing_time,
            metadata=metadata,
            timestamp=datetime.now()
        )


class DatabaseErrorHandler:
    """Handles error processing for database operations."""
    
    @staticmethod
    def handle_database_error(
        operation: str,
        error: Exception,
        user_id: str = "anonymous"
    ) -> DatabaseResponse:
        """Handle and format database errors."""
        error_message = f"{operation} failed: {str(error)}"
        logger.error(f"Database {operation} error: {error_message}")
        
        return DatabaseResponseFormatter.format_error(
            operation=operation,
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


class DatabasePerformanceTracker:
    """Tracks performance metrics for database operations."""
    
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


def create_database_metadata(
    user_id: str,
    **additional_metadata
) -> Dict[str, Any]:
    """Create metadata for database operations."""
    metadata = {
        "user_id": user_id,
        "timestamp": datetime.now().isoformat()
    }
    metadata.update(additional_metadata)
    return metadata


# Database endpoints

@router.get("/health")
async def database_health_check(
    current_user = Depends(get_current_user),
    database_service: DatabaseService = Depends(get_database_service)
) -> DatabaseResponse:
    """Health check for database service."""
    tracker = DatabasePerformanceTracker()
    tracker.start_tracking()
    
    try:
        health_status = await database_service.health_check()
        
        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)
        
        return DatabaseResponseFormatter.format_success(
            operation="health_check",
            result=health_status,
            processing_time=processing_time,
            metadata=create_database_metadata(user_id, service="database"),
            user_id=user_id
        )
        
    except Exception as e:
        processing_time = tracker.get_processing_time()
        return DatabaseErrorHandler.handle_database_error(
            operation="health check",
            error=e,
            user_id=get_user_id(current_user)
        )


@router.get("/metrics")
async def database_metrics(
    current_user = Depends(get_current_user),
    database_service: DatabaseService = Depends(get_database_service)
) -> DatabaseResponse:
    """Get database service metrics."""
    tracker = DatabasePerformanceTracker()
    tracker.start_tracking()
    
    try:
        metrics = await database_service.get_metrics()
        
        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)
        
        return DatabaseResponseFormatter.format_success(
            operation="get_metrics",
            result=metrics,
            processing_time=processing_time,
            metadata=create_database_metadata(user_id, service="database"),
            user_id=user_id
        )
        
    except Exception as e:
        processing_time = tracker.get_processing_time()
        return DatabaseErrorHandler.handle_database_error(
            operation="get metrics",
            error=e,
            user_id=get_user_id(current_user)
        )


@router.post("/query")
async def execute_database_query(
    request: DatabaseQueryRequest,
    current_user = Depends(get_current_user),
    database_service: DatabaseService = Depends(get_database_service)
) -> DatabaseResponse:
    """Execute a database query."""
    tracker = DatabasePerformanceTracker()
    tracker.start_tracking()
    
    try:
        # Validate request
        DatabaseErrorHandler.validate_request(
            request.dict(), 
            ["database_name", "query"]
        )
        
        # Execute query
        result = await database_service.execute_query(
            database_name=request.database_name,
            query=request.query,
            params=request.params,
            timeout=request.timeout
        )
        
        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)
        
        return DatabaseResponseFormatter.format_success(
            operation="execute_query",
            result={
                "success": result.success,
                "data": result.data,
                "row_count": result.row_count,
                "columns": result.columns,
                "query": result.query,
                "database_name": result.database_name,
                "processing_time": result.processing_time
            },
            processing_time=processing_time,
            metadata=create_database_metadata(
                user_id=user_id,
                database_name=request.database_name,
                query=request.query
            ),
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return DatabaseErrorHandler.handle_database_error(
            operation="Database query execution",
            error=e,
            user_id=get_user_id(current_user)
        )


@router.get("/{database_name}/schema")
async def get_database_schema(
    database_name: str,
    current_user = Depends(get_current_user),
    database_service: DatabaseService = Depends(get_database_service)
) -> DatabaseResponse:
    """Get database schema information."""
    tracker = DatabasePerformanceTracker()
    tracker.start_tracking()
    
    try:
        schema_info = await database_service.get_schema(database_name)
        
        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)
        
        return DatabaseResponseFormatter.format_success(
            operation="get_schema",
            result={
                "database_name": schema_info.database_name,
                "tables": schema_info.tables,
                "views": schema_info.views,
                "indexes": schema_info.indexes,
                "constraints": schema_info.constraints,
                "error": schema_info.error
            },
            processing_time=processing_time,
            metadata=create_database_metadata(
                user_id=user_id,
                database_name=database_name
            ),
            user_id=user_id
        )
        
    except Exception as e:
        return DatabaseErrorHandler.handle_database_error(
            operation="Schema retrieval",
            error=e,
            user_id=get_user_id(current_user)
        )


@router.post("/{database_name}/analyze")
async def analyze_database_data(
    database_name: str,
    request: DatabaseAnalysisRequest,
    current_user = Depends(get_current_user),
    database_service: DatabaseService = Depends(get_database_service)
) -> DatabaseResponse:
    """Analyze database table data."""
    tracker = DatabasePerformanceTracker()
    tracker.start_tracking()
    
    try:
        # Validate request
        DatabaseErrorHandler.validate_request(
            request.dict(), 
            ["table_name"]
        )
        
        analysis = await database_service.analyze_data(
            database_name=database_name,
            table_name=request.table_name,
            columns=request.columns
        )
        
        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)
        
        return DatabaseResponseFormatter.format_success(
            operation="analyze_data",
            result={
                "database_name": analysis.database_name,
                "table_name": analysis.table_name,
                "row_count": analysis.row_count,
                "column_stats": analysis.column_stats,
                "data_types": analysis.data_types,
                "missing_values": analysis.missing_values,
                "unique_values": analysis.unique_values,
                "error": analysis.error
            },
            processing_time=processing_time,
            metadata=create_database_metadata(
                user_id=user_id,
                database_name=database_name,
                table_name=request.table_name
            ),
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return DatabaseErrorHandler.handle_database_error(
            operation="Data analysis",
            error=e,
            user_id=get_user_id(current_user)
        )


@router.post("/{database_name}/optimize")
async def optimize_database_query(
    database_name: str,
    request: DatabaseQueryRequest,
    current_user = Depends(get_current_user),
    database_service: DatabaseService = Depends(get_database_service)
) -> DatabaseResponse:
    """Optimize a database query."""
    tracker = DatabasePerformanceTracker()
    tracker.start_tracking()
    
    try:
        # Validate request
        DatabaseErrorHandler.validate_request(
            request.dict(), 
            ["query"]
        )
        
        optimization = await database_service.optimize_query(
            database_name=database_name,
            query=request.query
        )
        
        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)
        
        return DatabaseResponseFormatter.format_success(
            operation="optimize_query",
            result=optimization,
            processing_time=processing_time,
            metadata=create_database_metadata(
                user_id=user_id,
                database_name=database_name,
                query=request.query
            ),
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return DatabaseErrorHandler.handle_database_error(
            operation="Query optimization",
            error=e,
            user_id=get_user_id(current_user)
        )


@router.get("/list")
async def list_databases(
    current_user = Depends(get_current_user),
    database_service: DatabaseService = Depends(get_database_service)
) -> DatabaseListResponse:
    """List available databases."""
    tracker = DatabasePerformanceTracker()
    tracker.start_tracking()
    
    try:
        databases = await database_service.list_databases()
        
        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)
        
        return DatabaseListResponse(
            success=True,
            databases=databases.get("databases", []),
            total_count=databases.get("total_count", 0),
            connected_count=databases.get("connected_count", 0),
            processing_time=processing_time,
            metadata=create_database_metadata(user_id, service="database"),
            timestamp=datetime.now()
        )
        
    except Exception as e:
        return DatabaseListResponse(
            success=False,
            error=str(e),
            databases=[],
            total_count=0,
            connected_count=0,
            processing_time=tracker.get_processing_time(),
            metadata=create_database_metadata(get_user_id(current_user), service="database"),
            timestamp=datetime.now()
        )


@router.get("/{database_name}/test")
async def test_database_connection(
    database_name: str,
    current_user = Depends(get_current_user),
    database_service: DatabaseService = Depends(get_database_service)
) -> DatabaseResponse:
    """Test database connection."""
    tracker = DatabasePerformanceTracker()
    tracker.start_tracking()
    
    try:
        test_result = await database_service.test_connection(database_name)
        
        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)
        
        return DatabaseResponseFormatter.format_success(
            operation="test_connection",
            result=test_result,
            processing_time=processing_time,
            metadata=create_database_metadata(
                user_id=user_id,
                database_name=database_name
            ),
            user_id=user_id
        )
        
    except Exception as e:
        return DatabaseErrorHandler.handle_database_error(
            operation="Connection test",
            error=e,
            user_id=get_user_id(current_user)
        ) 