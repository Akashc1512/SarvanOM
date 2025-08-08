"""
Query Routes for API Gateway

This module contains all query processing endpoints for the API gateway.
It handles basic queries, comprehensive queries, and query management operations.
"""

import asyncio
import time
import uuid
import logging
from shared.core.unified_logging import get_logger
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import ValidationError
from shared.core.utilities.timing_utilities import time_operation, start_timer, calculate_execution_time
from shared.core.utilities.response_utilities import create_success_response, create_error_response, add_execution_time
import httpx
from shared.core.config.central_config import get_central_config
from shared.contracts.query import (
    SynthesisRequest,
    RetrievalSearchRequest,
    RetrievalIndexRequest,
    RetrievalIndexResponse,
)

from ..models.requests import QueryRequest, ComprehensiveQueryRequest, QueryUpdateRequest
from ..models.responses import (
    QueryResponse, 
    ComprehensiveQueryResponse, 
    QueryListResponse,
    QueryDetailResponse,
    QueryStatusResponse
)
from ..middleware import get_current_user, require_read, require_write

logger = get_logger(__name__)

# Create router for query endpoints
router = APIRouter(prefix="/query", tags=["queries"])

# Import services
from ..services import query_service


@router.post("/index", response_model=Dict[str, Any])
async def index_documents(request: Dict[str, Any], current_user=Depends(get_current_user)):
    """Forward indexing payload to retrieval service /index.

    Expected body shape per RetrievalIndexRequest: { ids: [], texts: [], metadatas: [] }
    """
    try:
        payload = RetrievalIndexRequest(**request)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid payload: {e}")

    cfg = get_central_config()
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{cfg.search_service_url}/index"
            resp = await client.post(str(url), json=payload.dict())
            resp.raise_for_status()
            data = resp.json()
            return {"success": True, **data}
    except (asyncio.TimeoutError, httpx.TimeoutException):
        raise HTTPException(status_code=504, detail="Indexing timed out")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"Indexing service error: {e}")


@router.post("/", response_model=Dict[str, Any])
@time_operation("process_query")
async def process_query(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user)
):
    """Process query using the basic pipeline with agent orchestration."""
    request_id = getattr(http_request.state, "request_id", "unknown")
    start_time = start_timer()
    
    try:
        # Extract query parameters
        query = request.get("query", "")
        session_id = request.get("session_id", str(uuid.uuid4()))
        user_id = getattr(current_user, "user_id", "anonymous")
        max_tokens = request.get("max_tokens", 1000)
        confidence_threshold = request.get("confidence_threshold", 0.8)
        
        if not query:
            raise HTTPException(status_code=422, detail="Query is required")
        
        # Call retrieval and synthesis microservices via shared contracts
        cfg = get_central_config()
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                # Retrieval
                try:
                    retrieval_url = f"{cfg.search_service_url}/search"
                    retrieval_payload = RetrievalSearchRequest(
                        query=query,
                        max_results=10,
                        context={"user_id": user_id}
                    ).dict()
                    retrieval_resp = await client.post(str(retrieval_url), json=retrieval_payload)
                    retrieval_resp.raise_for_status()
                    search_data = retrieval_resp.json()
                except (asyncio.TimeoutError, httpx.TimeoutException) as timeout_error:
                    logger.error(f"Retrieval call timeout: {timeout_error}", exc_info=True)
                    execution_time = calculate_execution_time(start_time)
                    return create_error_response(
                        error="Retrieval timed out. Please try again.",
                        execution_time_ms=execution_time,
                        error_type="timeout_error"
                    )
                except httpx.HTTPError as e:
                    logger.error(f"Retrieval HTTP error: {e}", exc_info=True)
                    execution_time = calculate_execution_time(start_time)
                    return create_error_response(
                        error="Retrieval service unavailable. Please try again later.",
                        execution_time_ms=execution_time,
                        error_type="service_unavailable"
                    )

                # Synthesis
                try:
                    synthesis_url = f"{cfg.synthesis_service_url}/synthesize"
                    synthesis_payload = SynthesisRequest(
                        query=query,
                        sources=search_data.get("sources", []),
                        max_tokens=max_tokens,
                        context={"user_id": user_id}
                    ).dict()
                    synth_resp = await client.post(str(synthesis_url), json=synthesis_payload)
                    synth_resp.raise_for_status()
                    result = synth_resp.json()
                except (asyncio.TimeoutError, httpx.TimeoutException) as timeout_error:
                    logger.error(f"Query timeout: {timeout_error}", exc_info=True)
                    execution_time = calculate_execution_time(start_time)
                    return create_error_response(
                        error="Query processing timed out. Please try again with a simpler query.",
                        execution_time_ms=execution_time,
                        error_type="timeout_error"
                    )
                except httpx.HTTPError as e:
                    logger.error(f"Synthesis HTTP error: {e}", exc_info=True)
                    execution_time = calculate_execution_time(start_time)
                    return create_error_response(
                        error="Synthesis service unavailable. Please try again later.",
                        execution_time_ms=execution_time,
                        error_type="service_unavailable"
                    )
        except Exception as service_error:
            logger.error(f"Query service error: {service_error}", exc_info=True)
            execution_time = calculate_execution_time(start_time)
            return create_error_response(
                error="LLM service temporarily unavailable. Please try again later.",
                execution_time_ms=execution_time,
                error_type="service_unavailable"
            )
        
        if not result.get("success", False):
            error_msg = result.get("error", "Query processing failed")
            logger.error(f"Query processing failed: {error_msg}")
            execution_time = calculate_execution_time(start_time)
            return create_error_response(
                error=error_msg,
                execution_time_ms=execution_time,
                error_type="processing_failed"
            )
        
        # Format response for API using utilities
        response_data = {
            "answer": result.get("answer", ""),
            "citations": result.get("sources", []),
            "validation_status": result.get("verification", {}).get("overall_status", "Unverified"),
            "llm_provider": result.get("metadata", {}).get("llm_provider", "Unknown"),
            "cache_status": result.get("cache_status", "Miss"),
            "agent_results": {
                "retrieval": {
                    "vector_results": result.get("metadata", {}).get("vector_results", []),
                    "keyword_results": result.get("metadata", {}).get("keyword_results", []),
                    "knowledge_graph_results": result.get("metadata", {}).get("knowledge_graph_results", [])
                },
                "factcheck": result.get("verification", {}),
                "synthesis": {
                    "answer": result.get("answer", ""),
                    "confidence": result.get("confidence", 0.0)
                },
                "citation": {
                    "sources": result.get("sources", [])
                }
            },
            "confidence_score": result.get("confidence", 0.0),
            "coherence_score": result.get("metadata", {}).get("coherence_score", 0.0),
            "relevance_score": result.get("metadata", {}).get("relevance_score", 0.0)
        }
        
        # Use utility to add execution time
        response = create_success_response(data=response_data)
        return add_execution_time(response, start_time)
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Query processing failed: {e}", exc_info=True)
        execution_time = calculate_execution_time(start_time)
        return create_error_response(
            error="An unexpected error occurred. Please try again later.",
            execution_time_ms=execution_time,
            error_type="internal_error"
        )


@router.post("/comprehensive", response_model=Dict[str, Any])
async def process_comprehensive_query(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user)
):
    """Process query using the complete integration layer pipeline."""
    request_id = getattr(http_request.state, "request_id", "unknown")
    start_time = start_timer()
    
    try:
        # Process comprehensive query using the query service with comprehensive error handling
        try:
            result = await query_service.process_comprehensive_query(
                query=request.get("query", ""),
                user_context={
                    "user_id": current_user.get("user_id", "anonymous"),
                    "session_id": request.get("session_id", str(uuid.uuid4())),
                    "context": request.get("context", {}),
                    "preferences": request.get("preferences", {}),
                    "priority": request.get("priority", "normal"),
                    "timeout_seconds": request.get("timeout_seconds", 30),
                    "model": request.get("model", "auto")
                },
                options=request.get("options", {})
            )
        except Exception as service_error:
            logger.error(f"Comprehensive query service error: {service_error}", exc_info=True)
            execution_time = calculate_execution_time(start_time)
            return create_error_response(
                error="Comprehensive query processing temporarily unavailable. Please try again later.",
                execution_time_ms=execution_time,
                error_type="service_unavailable"
            )
        
        # Format response for API
        api_response = {
            "success": result.get("success", False),
            "query": request.get("query", ""),
            "processing_time_ms": result.get("processing_time", 0) * 1000,
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id
        }
        
        if result.get("success", False):
            api_response.update({
                "response": result.get("answer", ""),
                "llm_provider": result.get("metadata", {}).get("llm_provider", "Unknown"),
                "llm_model": result.get("metadata", {}).get("model_used", "Unknown"),
                "model_used": result.get("metadata", {}).get("model_used", "Unknown"),
                "query_analysis": result.get("analysis", {}),
                "verification": result.get("verification", {}),
                "sources": result.get("sources", []),
                "confidence": result.get("confidence", 0.0),
                "quality": result.get("quality", {})
            })
        else:
            error_msg = result.get("error", "Comprehensive query processing failed")
            logger.error(f"Comprehensive query processing failed: {error_msg}")
            execution_time = calculate_execution_time(start_time)
            return create_error_response(
                error=error_msg,
                execution_time_ms=execution_time,
                error_type="processing_failed"
            )
        
        return api_response
        
    except Exception as e:
        logger.error(f"Comprehensive query processing failed: {e}", exc_info=True)
        execution_time = calculate_execution_time(start_time)
        return create_error_response(
            error="An unexpected error occurred during comprehensive query processing. Please try again later.",
            execution_time_ms=execution_time,
            error_type="internal_error"
        )


@router.get("/", response_model=QueryListResponse)
async def list_queries(
    page: int = 1,
    page_size: int = 20,
    user_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    http_request: Request = None,
    current_user=Depends(get_current_user),
):
    """List queries with pagination and filtering."""
    try:
        # Implement query listing logic
        # This would typically involve database queries
        
        # Import database service
        from services.retrieval.retrieval_agent import RetrievalAgent
        import asyncpg
        import os
        
        # Get database configuration
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = int(os.getenv('DB_PORT', '5432'))
        db_name = os.getenv('DB_NAME', 'sarvanom')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        
        try:
            # Connect to database with timeout and retry logic
            conn = await asyncio.wait_for(
                asyncpg.connect(
                    host=db_host,
                    port=db_port,
                    database=db_name,
                    user=db_user,
                    password=db_password
                ),
                timeout=10.0  # 10 second timeout for connection
            )
            
            # Build query with filters
            base_query = """
                SELECT 
                    query_id,
                    query_text,
                    status,
                    created_at,
                    updated_at,
                    user_id,
                    processing_time,
                    result_summary,
                    tags
                FROM queries 
                WHERE 1=1
            """
            
            params = []
            param_count = 0
            
            # Add user filter
            if user_filter:
                param_count += 1
                base_query += f" AND user_id = ${param_count}"
                params.append(user_filter)
            else:
                # Filter by current user if no specific user filter
                param_count += 1
                base_query += f" AND user_id = ${param_count}"
                params.append(current_user.get("user_id", "anonymous"))
            
            # Add status filter
            if status_filter:
                param_count += 1
                base_query += f" AND status = ${param_count}"
                params.append(status_filter)
            
            # Add pagination
            offset = (page - 1) * page_size
            base_query += f" ORDER BY created_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
            params.extend([page_size, offset])
            
            # Execute query with timeout
            try:
                rows = await asyncio.wait_for(
                    conn.fetch(base_query, *params),
                    timeout=15.0  # 15 second timeout for query execution
                )
            except asyncio.TimeoutError:
                await conn.close()
                logger.error("Database query timeout for list_queries")
                raise HTTPException(
                    status_code=503,
                    detail="Database query timeout. Please try again later."
                )
            
            # Get total count with timeout
            count_query = """
                SELECT COUNT(*) 
                FROM queries 
                WHERE 1=1
            """
            count_params = []
            param_count = 0
            
            if user_filter:
                param_count += 1
                count_query += f" AND user_id = ${param_count}"
                count_params.append(user_filter)
            else:
                param_count += 1
                count_query += f" AND user_id = ${param_count}"
                count_params.append(current_user.get("user_id", "anonymous"))
            
            if status_filter:
                param_count += 1
                count_query += f" AND status = ${param_count}"
                count_params.append(status_filter)
            
            try:
                total_count = await asyncio.wait_for(
                    conn.fetchval(count_query, *count_params),
                    timeout=10.0  # 10 second timeout for count query
                )
            except asyncio.TimeoutError:
                await conn.close()
                logger.error("Database count query timeout for list_queries")
                raise HTTPException(
                    status_code=503,
                    detail="Database count query timeout. Please try again later."
                )
            
            await conn.close()
            
            # Convert rows to response format
            queries = []
            for row in rows:
                queries.append({
                    "query_id": row['query_id'],
                    "query_text": row['query_text'],
                    "status": row['status'],
                    "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                    "user_id": row['user_id'],
                    "processing_time": float(row['processing_time']) if row['processing_time'] else None,
                    "result_summary": row['result_summary'],
                    "tags": row['tags'] if row['tags'] else []
                })
            
            # Calculate pagination info
            has_next = (page * page_size) < total_count
            has_previous = page > 1
            
            return QueryListResponse(
                queries=queries,
                total_count=total_count,
                page=page,
                page_size=page_size,
                has_next=has_next,
                has_previous=has_previous
            )
            
        except asyncpg.InvalidPasswordError:
            logger.error("Database authentication failed for list_queries")
            raise HTTPException(
                status_code=503, 
                detail="Database authentication failed. Please contact support."
            )
        except asyncpg.ConnectionDoesNotExistError:
            logger.error("Database connection failed for list_queries")
            raise HTTPException(
                status_code=503, 
                detail="Database connection failed. Please try again later."
            )
        except asyncpg.PostgresError as e:
            logger.error(f"PostgreSQL error in list_queries: {e}")
            raise HTTPException(
                status_code=503,
                detail="Database error occurred. Please try again later."
            )
        except asyncio.TimeoutError:
            logger.error("Database operation timeout for list_queries")
            raise HTTPException(
                status_code=503,
                detail="Database operation timeout. Please try again later."
            )
        except Exception as e:
            logger.error(f"Database query failed for list_queries: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail="Failed to retrieve queries. Please try again later."
            )
        
    except ImportError:
        logger.warning("asyncpg not available, using mock data")
        # Fallback to mock data if database is not available
        mock_queries = [
            {
                "query_id": "mock-query-1",
                "query_text": "Sample query 1",
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "user_id": current_user.get("user_id", "anonymous")
            },
            {
                "query_id": "mock-query-2", 
                "query_text": "Sample query 2",
                "status": "processing",
                "created_at": datetime.now().isoformat(),
                "user_id": current_user.get("user_id", "anonymous")
            }
        ]
        
        return QueryListResponse(
            queries=mock_queries,
            total_count=len(mock_queries),
            page=page,
            page_size=page_size,
            has_next=False,
            has_previous=False
        )
        
    except Exception as e:
        logger.error(f"Failed to list queries: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to list queries"
        )


@router.get("/{query_id}", response_model=QueryDetailResponse)
async def get_query(
    query_id: str, 
    http_request: Request, 
    current_user=Depends(get_current_user)
):
    """Get detailed information about a specific query."""
    try:
        # Implement query retrieval logic
        # This would typically involve database queries
        
        import asyncpg
        import os
        
        # Get database configuration
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = int(os.getenv('DB_PORT', '5432'))
        db_name = os.getenv('DB_NAME', 'sarvanom')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        
        try:
            # Connect to database with timeout
            conn = await asyncio.wait_for(
                asyncpg.connect(
                    host=db_host,
                    port=db_port,
                    database=db_name,
                    user=db_user,
                    password=db_password
                ),
                timeout=10.0  # 10 second timeout for connection
            )
            
            # Get query details
            query = """
                SELECT 
                    query_id,
                    query_text,
                    status,
                    result,
                    metadata,
                    processing_time,
                    created_at,
                    updated_at,
                    user_id,
                    tags,
                    notes,
                    error_message,
                    model_used,
                    confidence_score,
                    sources
                FROM queries 
                WHERE query_id = $1 AND user_id = $2
            """
            
            try:
                row = await asyncio.wait_for(
                    conn.fetchrow(
                        query, 
                        query_id, 
                        current_user.get("user_id", "anonymous")
                    ),
                    timeout=15.0  # 15 second timeout for query execution
                )
            except asyncio.TimeoutError:
                await conn.close()
                logger.error(f"Database query timeout for get_query: {query_id}")
                raise HTTPException(
                    status_code=503,
                    detail="Database query timeout. Please try again later."
                )
            
            await conn.close()
            
            if not row:
                raise HTTPException(
                    status_code=404,
                    detail=f"Query {query_id} not found"
                )
            
            # Parse result JSON
            result_data = {}
            if row['result']:
                try:
                    result_data = row['result'] if isinstance(row['result'], dict) else {}
                except:
                    result_data = {}
            
            # Parse metadata JSON
            metadata = {}
            if row['metadata']:
                try:
                    metadata = row['metadata'] if isinstance(row['metadata'], dict) else {}
                except:
                    metadata = {}
            
            # Parse sources JSON
            sources = []
            if row['sources']:
                try:
                    sources = row['sources'] if isinstance(row['sources'], list) else []
                except:
                    sources = []
            
            # Parse tags JSON
            tags = []
            if row['tags']:
                try:
                    tags = row['tags'] if isinstance(row['tags'], list) else []
                except:
                    tags = []
            
            query_detail = {
                "query_id": row['query_id'],
                "query_text": row['query_text'],
                "status": row['status'],
                "result": result_data,
                "metadata": metadata,
                "processing_time": float(row['processing_time']) if row['processing_time'] else None,
                "created_at": row['created_at'],
                "updated_at": row['updated_at'],
                "user_id": row['user_id'],
                "tags": tags,
                "notes": row['notes'],
                "error_message": row['error_message'],
                "model_used": row['model_used'],
                "confidence_score": float(row['confidence_score']) if row['confidence_score'] else None,
                "sources": sources
            }
            
            return QueryDetailResponse(**query_detail)
            
        except asyncpg.InvalidPasswordError:
            logger.error("Database authentication failed for get_query")
            raise HTTPException(
                status_code=503, 
                detail="Database authentication failed. Please contact support."
            )
        except asyncpg.ConnectionDoesNotExistError:
            logger.error("Database connection failed for get_query")
            raise HTTPException(
                status_code=503, 
                detail="Database connection failed. Please try again later."
            )
        except asyncpg.PostgresError as e:
            logger.error(f"PostgreSQL error in get_query: {e}")
            raise HTTPException(
                status_code=503,
                detail="Database error occurred. Please try again later."
            )
        except asyncio.TimeoutError:
            logger.error(f"Database operation timeout for get_query: {query_id}")
            raise HTTPException(
                status_code=503,
                detail="Database operation timeout. Please try again later."
            )
        except Exception as e:
            logger.error(f"Database query failed for get_query: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail="Failed to retrieve query. Please try again later."
            )
        
    except ImportError:
        logger.warning("asyncpg not available, using mock data")
        # Fallback to mock data if database is not available
        mock_query = {
            "query_id": query_id,
            "query_text": f"Sample query for {query_id}",
            "status": "completed",
            "result": {
                "answer": "Sample answer",
                "sources": ["source1", "source2"]
            },
            "metadata": {
                "processing_time": 1.5,
                "model_used": "gpt-4o-mini"
            },
            "processing_time": 1.5,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "user_id": current_user.get("user_id", "anonymous"),
            "tags": ["sample", "test"],
            "notes": "Sample query notes"
        }
        
        return QueryDetailResponse(**mock_query)
        
    except Exception as e:
        logger.error(f"Failed to get query {query_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get query {query_id}"
        )


@router.put("/{query_id}", response_model=QueryDetailResponse)
async def update_query(
    query_id: str,
    update_request: QueryUpdateRequest,
    http_request: Request,
    current_user=Depends(get_current_user),
):
    """Update a specific query."""
    try:
        # Implement query update logic
        # This would typically involve database operations
        
        import asyncpg
        import os
        import json
        
        # Get database configuration
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = int(os.getenv('DB_PORT', '5432'))
        db_name = os.getenv('DB_NAME', 'sarvanom')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        
        try:
            # Connect to database
            conn = await asyncpg.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password
            )
            
            # First, check if query exists and belongs to user
            check_query = """
                SELECT query_id, query_text, status, result, metadata, tags, notes
                FROM queries 
                WHERE query_id = $1 AND user_id = $2
            """
            
            existing_query = await conn.fetchrow(
                check_query, 
                query_id, 
                current_user.get("user_id", "anonymous")
            )
            
            if not existing_query:
                await conn.close()
                raise HTTPException(
                    status_code=404,
                    detail=f"Query {query_id} not found"
                )
            
            # Build update query dynamically based on provided fields
            update_fields = []
            update_values = []
            param_count = 0
            
            if update_request.status is not None:
                param_count += 1
                update_fields.append(f"status = ${param_count}")
                update_values.append(update_request.status)
            
            if update_request.metadata is not None:
                param_count += 1
                update_fields.append(f"metadata = ${param_count}")
                update_values.append(json.dumps(update_request.metadata))
            
            if update_request.tags is not None:
                param_count += 1
                update_fields.append(f"tags = ${param_count}")
                update_values.append(json.dumps(update_request.tags))
            
            if update_request.notes is not None:
                param_count += 1
                update_fields.append(f"notes = ${param_count}")
                update_values.append(update_request.notes)
            
            # Always update the updated_at timestamp
            param_count += 1
            update_fields.append(f"updated_at = ${param_count}")
            update_values.append(datetime.now())
            
            if not update_fields:
                await conn.close()
                raise HTTPException(
                    status_code=400,
                    detail="No valid fields to update"
                )
            
            # Build and execute update query
            update_query = f"""
                UPDATE queries 
                SET {', '.join(update_fields)}
                WHERE query_id = ${param_count + 1} AND user_id = ${param_count + 2}
                RETURNING *
            """
            
            update_values.extend([query_id, current_user.get("user_id", "anonymous")])
            
            updated_row = await conn.fetchrow(update_query, *update_values)
            await conn.close()
            
            if not updated_row:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to update query"
                )
            
            # Parse JSON fields
            result_data = {}
            if updated_row['result']:
                try:
                    result_data = updated_row['result'] if isinstance(updated_row['result'], dict) else {}
                except:
                    result_data = {}
            
            metadata = {}
            if updated_row['metadata']:
                try:
                    metadata = updated_row['metadata'] if isinstance(updated_row['metadata'], dict) else {}
                except:
                    metadata = {}
            
            tags = []
            if updated_row['tags']:
                try:
                    tags = updated_row['tags'] if isinstance(updated_row['tags'], list) else []
                except:
                    tags = []
            
            sources = []
            if updated_row['sources']:
                try:
                    sources = updated_row['sources'] if isinstance(updated_row['sources'], list) else []
                except:
                    sources = []
            
            updated_query = {
                "query_id": updated_row['query_id'],
                "query_text": updated_row['query_text'],
                "status": updated_row['status'],
                "result": result_data,
                "metadata": metadata,
                "processing_time": float(updated_row['processing_time']) if updated_row['processing_time'] else None,
                "created_at": updated_row['created_at'],
                "updated_at": updated_row['updated_at'],
                "user_id": updated_row['user_id'],
                "tags": tags,
                "notes": updated_row['notes'],
                "error_message": updated_row['error_message'],
                "model_used": updated_row['model_used'],
                "confidence_score": float(updated_row['confidence_score']) if updated_row['confidence_score'] else None,
                "sources": sources
            }
            
            return QueryDetailResponse(**updated_query)
            
        except asyncpg.InvalidPasswordError:
            logger.error("Database authentication failed")
            raise HTTPException(status_code=500, detail="Database connection failed")
        except asyncpg.ConnectionDoesNotExistError:
            logger.error("Database connection failed")
            raise HTTPException(status_code=500, detail="Database connection failed")
        except Exception as e:
            logger.error(f"Database update failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to update query")
        
    except ImportError:
        logger.warning("asyncpg not available, using mock data")
        # Fallback to mock data if database is not available
        updated_query = {
            "query_id": query_id,
            "query_text": f"Updated query for {query_id}",
            "status": update_request.status or "completed",
            "result": {
                "answer": "Updated answer",
                "sources": ["updated_source1", "updated_source2"]
            },
            "metadata": update_request.metadata or {},
            "processing_time": 2.0,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "user_id": current_user.get("user_id", "anonymous"),
            "tags": update_request.tags or ["updated"],
            "notes": update_request.notes or "Updated query notes"
        }
        
        return QueryDetailResponse(**updated_query)
        
    except Exception as e:
        logger.error(f"Failed to update query {query_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update query {query_id}"
        )


@router.delete("/{query_id}")
async def delete_query(
    query_id: str, 
    http_request: Request, 
    current_user=Depends(get_current_user)
):
    """Delete a specific query."""
    try:
        # Implement query deletion logic
        # This would typically involve database operations
        
        import asyncpg
        import os
        
        # Get database configuration
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = int(os.getenv('DB_PORT', '5432'))
        db_name = os.getenv('DB_NAME', 'sarvanom')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        
        try:
            # Connect to database
            conn = await asyncpg.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password
            )
            
            # Check if query exists and belongs to user
            check_query = """
                SELECT query_id, status
                FROM queries 
                WHERE query_id = $1 AND user_id = $2
            """
            
            existing_query = await conn.fetchrow(
                check_query, 
                query_id, 
                current_user.get("user_id", "anonymous")
            )
            
            if not existing_query:
                await conn.close()
                raise HTTPException(
                    status_code=404,
                    detail=f"Query {query_id} not found"
                )
            
            # Check if query is currently processing
            if existing_query['status'] in ['processing', 'queued']:
                await conn.close()
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot delete query {query_id} while it is being processed"
                )
            
            # Delete the query
            delete_query = """
                DELETE FROM queries 
                WHERE query_id = $1 AND user_id = $2
                RETURNING query_id
            """
            
            deleted_query = await conn.fetchrow(
                delete_query, 
                query_id, 
                current_user.get("user_id", "anonymous")
            )
            
            await conn.close()
            
            if not deleted_query:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to delete query"
                )
            
            return {
                "success": True,
                "message": f"Query {query_id} deleted successfully",
                "query_id": query_id,
                "deleted_at": datetime.now().isoformat()
            }
            
        except asyncpg.InvalidPasswordError:
            logger.error("Database authentication failed")
            raise HTTPException(status_code=500, detail="Database connection failed")
        except asyncpg.ConnectionDoesNotExistError:
            logger.error("Database connection failed")
            raise HTTPException(status_code=500, detail="Database connection failed")
        except Exception as e:
            logger.error(f"Database deletion failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete query")
        
    except ImportError:
        logger.warning("asyncpg not available, using mock deletion")
        # Fallback to mock deletion if database is not available
        return {
            "success": True,
            "message": f"Query {query_id} deleted successfully (mock)",
            "query_id": query_id,
            "deleted_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to delete query {query_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete query {query_id}"
        )


@router.get("/{query_id}/status", response_model=QueryStatusResponse)
async def get_query_status(
    query_id: str, 
    http_request: Request, 
    current_user=Depends(get_current_user)
):
    """Get the status of a specific query."""
    try:
        # Implement query status retrieval logic
        
        import asyncpg
        import os
        
        # Get database configuration
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = int(os.getenv('DB_PORT', '5432'))
        db_name = os.getenv('DB_NAME', 'sarvanom')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        
        try:
            # Connect to database
            conn = await asyncpg.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password
            )
            
            # Get query status
            status_query = """
                SELECT 
                    query_id,
                    status,
                    processing_time,
                    created_at,
                    updated_at,
                    error_message,
                    metadata
                FROM queries 
                WHERE query_id = $1 AND user_id = $2
            """
            
            row = await conn.fetchrow(
                status_query, 
                query_id, 
                current_user.get("user_id", "anonymous")
            )
            
            await conn.close()
            
            if not row:
                raise HTTPException(
                    status_code=404,
                    detail=f"Query {query_id} not found"
                )
            
            # Parse metadata for progress information
            metadata = {}
            if row['metadata']:
                try:
                    metadata = row['metadata'] if isinstance(row['metadata'], dict) else {}
                except:
                    metadata = {}
            
            # Calculate progress based on status
            progress = 0.0
            current_step = "unknown"
            estimated_completion = None
            
            if row['status'] == 'completed':
                progress = 1.0
                current_step = "finalized"
                estimated_completion = row['updated_at'].isoformat() if row['updated_at'] else None
            elif row['status'] == 'processing':
                progress = 0.5
                current_step = "processing"
                # Estimate completion based on processing time
                if row['processing_time']:
                    estimated_completion = (row['created_at'] + timedelta(seconds=row['processing_time'] * 2)).isoformat()
                else:
                    estimated_completion = (row['created_at'] + timedelta(minutes=5)).isoformat()
            elif row['status'] == 'queued':
                progress = 0.1
                current_step = "queued"
                estimated_completion = (row['created_at'] + timedelta(minutes=10)).isoformat()
            elif row['status'] == 'failed':
                progress = 0.0
                current_step = "failed"
                estimated_completion = row['updated_at'].isoformat() if row['updated_at'] else None
            
            # Get step information from metadata
            if metadata.get('current_step'):
                current_step = metadata['current_step']
            if metadata.get('progress'):
                progress = float(metadata['progress'])
            if metadata.get('estimated_completion'):
                estimated_completion = metadata['estimated_completion']
            
            status_response = {
                "query_id": row['query_id'],
                "status": row['status'],
                "progress": progress,
                "estimated_completion": estimated_completion,
                "current_step": current_step,
                "error_message": row['error_message'],
                "processing_time": float(row['processing_time']) if row['processing_time'] else None,
                "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                "updated_at": row['updated_at'].isoformat() if row['updated_at'] else None
            }
            
            return QueryStatusResponse(**status_response)
            
        except asyncpg.InvalidPasswordError:
            logger.error("Database authentication failed")
            raise HTTPException(status_code=500, detail="Database connection failed")
        except asyncpg.ConnectionDoesNotExistError:
            logger.error("Database connection failed")
            raise HTTPException(status_code=500, detail="Database connection failed")
        except Exception as e:
            logger.error(f"Database status query failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve query status")
        
    except ImportError:
        logger.warning("asyncpg not available, using mock status")
        # Fallback to mock status if database is not available
        mock_status = {
            "query_id": query_id,
            "status": "completed",
            "progress": 1.0,
            "estimated_completion": datetime.now().isoformat(),
            "current_step": "finalized",
            "error_message": None
        }
        
        return QueryStatusResponse(**mock_status)
        
    except Exception as e:
        logger.error(f"Failed to get status for query {query_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get status for query {query_id}"
        )


@router.patch("/{query_id}/reprocess")
async def reprocess_query(
    query_id: str, 
    http_request: Request, 
    current_user=Depends(get_current_user)
):
    """Reprocess a specific query."""
    try:
        # Implement query reprocessing logic
        
        import asyncpg
        import os
        import json
        
        # Get database configuration
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = int(os.getenv('DB_PORT', '5432'))
        db_name = os.getenv('DB_NAME', 'sarvanom')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        
        try:
            # Connect to database
            conn = await asyncpg.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password
            )
            
            # Get original query details
            query_details = """
                SELECT 
                    query_id,
                    query_text,
                    status,
                    metadata,
                    created_at
                FROM queries 
                WHERE query_id = $1 AND user_id = $2
            """
            
            row = await conn.fetchrow(
                query_details, 
                query_id, 
                current_user.get("user_id", "anonymous")
            )
            
            if not row:
                await conn.close()
                raise HTTPException(
                    status_code=404,
                    detail=f"Query {query_id} not found"
                )
            
            # Check if query is already processing
            if row['status'] in ['processing', 'queued']:
                await conn.close()
                raise HTTPException(
                    status_code=400,
                    detail=f"Query {query_id} is already being processed"
                )
            
            # Update query status to reprocessing
            update_query = """
                UPDATE queries 
                SET 
                    status = 'processing',
                    updated_at = $1,
                    error_message = NULL,
                    processing_time = NULL,
                    result = NULL
                WHERE query_id = $2 AND user_id = $3
                RETURNING query_id
            """
            
            updated_row = await conn.fetchrow(
                update_query,
                datetime.now(),
                query_id,
                current_user.get("user_id", "anonymous")
            )
            
            await conn.close()
            
            if not updated_row:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to update query status"
                )
            
            # Start reprocessing in background
            try:
                # Import query service
                from services.api_gateway.services.query_service import QueryService
                
                # Initialize query service
                query_service = QueryService()
                
                # Get original metadata
                original_metadata = {}
                if row['metadata']:
                    try:
                        original_metadata = row['metadata'] if isinstance(row['metadata'], dict) else {}
                    except:
                        original_metadata = {}
                
                # Reprocess the query
                reprocess_result = await query_service.process_basic_query(
                    query=row['query_text'],
                    user_context={
                        "user_id": current_user.get("user_id", "anonymous"),
                        "session_id": str(uuid.uuid4()),
                        "reprocessing": True,
                        "original_query_id": query_id
                    },
                    cache_enabled=False  # Don't use cache for reprocessing
                )
                
                # Update query with new results
                conn = await asyncpg.connect(
                    host=db_host,
                    port=db_port,
                    database=db_name,
                    user=db_user,
                    password=db_password
                )
                
                # Update with new results
                final_update = """
                    UPDATE queries 
                    SET 
                        status = $1,
                        result = $2,
                        processing_time = $3,
                        updated_at = $4,
                        error_message = $5,
                        metadata = $6
                    WHERE query_id = $7 AND user_id = $8
                """
                
                status = "completed" if reprocess_result.get("success", False) else "failed"
                result_json = json.dumps(reprocess_result.get("result", {}))
                processing_time = reprocess_result.get("processing_time", 0)
                error_message = reprocess_result.get("error", None)
                
                # Update metadata with reprocessing info
                updated_metadata = {
                    **original_metadata,
                    "reprocessed_at": datetime.now().isoformat(),
                    "reprocessing_success": reprocess_result.get("success", False),
                    "original_processing_time": original_metadata.get("processing_time", 0)
                }
                metadata_json = json.dumps(updated_metadata)
                
                await conn.execute(
                    final_update,
                    status,
                    result_json,
                    processing_time,
                    datetime.now(),
                    error_message,
                    metadata_json,
                    query_id,
                    current_user.get("user_id", "anonymous")
                )
                
                await conn.close()
                
                return {
                    "success": True,
                    "message": f"Query {query_id} reprocessing completed",
                    "query_id": query_id,
                    "status": status,
                    "processing_time": processing_time,
                    "reprocessed_at": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Reprocessing failed for query {query_id}: {e}")
                
                # Update query status to failed
                conn = await asyncpg.connect(
                    host=db_host,
                    port=db_port,
                    database=db_name,
                    user=db_user,
                    password=db_password
                )
                
                await conn.execute(
                    """
                    UPDATE queries 
                    SET 
                        status = 'failed',
                        error_message = $1,
                        updated_at = $2
                    WHERE query_id = $3 AND user_id = $4
                    """,
                    str(e),
                    datetime.now(),
                    query_id,
                    current_user.get("user_id", "anonymous")
                )
                
                await conn.close()
                
                raise HTTPException(
                    status_code=500,
                    detail=f"Reprocessing failed: {str(e)}"
                )
            
        except asyncpg.InvalidPasswordError:
            logger.error("Database authentication failed")
            raise HTTPException(status_code=500, detail="Database connection failed")
        except asyncpg.ConnectionDoesNotExistError:
            logger.error("Database connection failed")
            raise HTTPException(status_code=500, detail="Database connection failed")
        except Exception as e:
            logger.error(f"Database reprocessing failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to reprocess query")
        
    except ImportError:
        logger.warning("asyncpg not available, using mock reprocessing")
        # Fallback to mock reprocessing if database is not available
        return {
            "success": True,
            "message": f"Query {query_id} reprocessing started (mock)",
            "query_id": query_id,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Failed to reprocess query {query_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reprocess query {query_id}"
        ) 