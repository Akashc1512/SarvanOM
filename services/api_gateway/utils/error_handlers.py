"""
Comprehensive Error Handling Utilities for API Gateway Routes.

This module provides centralized error handling utilities for common operations
like LLM calls, database operations, and external API calls.

Features:
    - LLM API error handling with fallbacks
    - Database operation error handling with timeouts
    - External API call error handling
    - Graceful degradation patterns
    - Structured error logging
    - Circuit breaker patterns

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    1.0.0 (2024-12-28)
"""

import asyncio
import time
import traceback
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from functools import wraps

import asyncpg
from fastapi import HTTPException
from shared.core.unified_logging import get_logger

logger = get_logger(__name__)

# Type variables for generic error handling
T = TypeVar("T")


class LLMErrorHandler:
    """Handler for LLM API errors with fallback mechanisms."""

    @staticmethod
    async def handle_llm_call(
        llm_function: Callable,
        *args,
        timeout: float = 60.0,
        max_retries: int = 3,
        fallback_response: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Any:
        """
        Safely execute an LLM call with comprehensive error handling.

        Args:
            llm_function: The LLM function to call
            timeout: Operation timeout in seconds
            max_retries: Maximum retry attempts
            fallback_response: Fallback response if all retries fail
            **kwargs: Additional arguments for the LLM function

        Returns:
            LLM response or fallback data
        """
        for attempt in range(max_retries):
            try:
                # Execute LLM call with timeout
                result = await asyncio.wait_for(
                    llm_function(*args, **kwargs), timeout=timeout
                )
                return result

            except asyncio.TimeoutError:
                logger.error(f"LLM call timeout on attempt {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    logger.error("LLM call failed after all retries")
                    if fallback_response:
                        return fallback_response
                    raise HTTPException(
                        status_code=503,
                        detail="LLM service timeout. Please try again later.",
                    )

            except Exception as e:
                logger.error(
                    f"LLM call error on attempt {attempt + 1}/{max_retries}: {e}"
                )
                if attempt == max_retries - 1:
                    logger.error("LLM call failed after all retries", exc_info=True)
                    if fallback_response:
                        return fallback_response
                    raise HTTPException(
                        status_code=503,
                        detail="LLM service temporarily unavailable. Please try again later.",
                    )

                # Wait before retry (exponential backoff)
                await asyncio.sleep(2**attempt)


class DatabaseErrorHandler:
    """Handler for database operation errors with timeouts."""

    @staticmethod
    async def execute_query(
        query_func: Callable,
        *args,
        timeout: float = 15.0,
        max_retries: int = 3,
        operation_name: str = "database_operation",
        **kwargs,
    ) -> Any:
        """
        Safely execute a database query with comprehensive error handling.

        Args:
            query_func: The database function to call
            timeout: Operation timeout in seconds
            max_retries: Maximum retry attempts
            operation_name: Name of the operation for logging
            **kwargs: Additional arguments for the database function

        Returns:
            Database query result
        """
        for attempt in range(max_retries):
            try:
                # Execute database query with timeout
                result = await asyncio.wait_for(
                    query_func(*args, **kwargs), timeout=timeout
                )
                return result

            except asyncio.TimeoutError:
                logger.error(
                    f"Database {operation_name} timeout on attempt {attempt + 1}/{max_retries}"
                )
                if attempt == max_retries - 1:
                    logger.error(f"Database {operation_name} failed after all retries")
                    raise HTTPException(
                        status_code=503,
                        detail="Database operation timeout. Please try again later.",
                    )

            except asyncpg.InvalidPasswordError:
                logger.error(f"Database authentication failed for {operation_name}")
                raise HTTPException(
                    status_code=503,
                    detail="Database authentication failed. Please contact support.",
                )

            except asyncpg.ConnectionDoesNotExistError:
                logger.error(f"Database connection failed for {operation_name}")
                if attempt == max_retries - 1:
                    raise HTTPException(
                        status_code=503,
                        detail="Database connection failed. Please try again later.",
                    )

            except asyncpg.PostgresError as e:
                logger.error(f"PostgreSQL error in {operation_name}: {e}")
                if attempt == max_retries - 1:
                    raise HTTPException(
                        status_code=503,
                        detail="Database error occurred. Please try again later.",
                    )

            except Exception as e:
                logger.error(
                    f"Database {operation_name} error on attempt {attempt + 1}/{max_retries}: {e}"
                )
                if attempt == max_retries - 1:
                    logger.error(
                        f"Database {operation_name} failed after all retries",
                        exc_info=True,
                    )
                    raise HTTPException(
                        status_code=500,
                        detail="Database operation failed. Please try again later.",
                    )

                # Wait before retry (exponential backoff)
                await asyncio.sleep(2**attempt)

    @staticmethod
    async def connect_with_timeout(
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        timeout: float = 10.0,
    ) -> asyncpg.Connection:
        """
        Connect to database with timeout and error handling.

        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
            timeout: Connection timeout in seconds

        Returns:
            Database connection
        """
        try:
            return await asyncio.wait_for(
                asyncpg.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password=password,
                ),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.error("Database connection timeout")
            raise HTTPException(
                status_code=503,
                detail="Database connection timeout. Please try again later.",
            )
        except asyncpg.InvalidPasswordError:
            logger.error("Database authentication failed")
            raise HTTPException(
                status_code=503,
                detail="Database authentication failed. Please contact support.",
            )
        except asyncpg.ConnectionDoesNotExistError:
            logger.error("Database connection failed")
            raise HTTPException(
                status_code=503,
                detail="Database connection failed. Please try again later.",
            )
        except Exception as e:
            logger.error(f"Database connection error: {e}", exc_info=True)
            raise HTTPException(
                status_code=503,
                detail="Database connection error. Please try again later.",
            )


class ExternalAPIErrorHandler:
    """Handler for external API call errors."""

    @staticmethod
    async def call_external_api(
        api_function: Callable,
        *args,
        timeout: float = 30.0,
        max_retries: int = 3,
        fallback_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Any:
        """
        Safely call an external API with comprehensive error handling.

        Args:
            api_function: The API function to call
            timeout: Operation timeout in seconds
            max_retries: Maximum retry attempts
            fallback_data: Fallback data if API call fails
            **kwargs: Additional arguments for the API function

        Returns:
            API response or fallback data
        """
        for attempt in range(max_retries):
            try:
                # Execute API call with timeout
                result = await asyncio.wait_for(
                    api_function(*args, **kwargs), timeout=timeout
                )
                return result

            except asyncio.TimeoutError:
                logger.error(
                    f"External API call timeout on attempt {attempt + 1}/{max_retries}"
                )
                if attempt == max_retries - 1:
                    logger.error("External API call failed after all retries")
                    if fallback_data:
                        return fallback_data
                    raise HTTPException(
                        status_code=503,
                        detail="External service timeout. Please try again later.",
                    )

            except Exception as e:
                logger.error(
                    f"External API call error on attempt {attempt + 1}/{max_retries}: {e}"
                )
                if attempt == max_retries - 1:
                    logger.error(
                        "External API call failed after all retries", exc_info=True
                    )
                    if fallback_data:
                        return fallback_data
                    raise HTTPException(
                        status_code=503,
                        detail="External service temporarily unavailable. Please try again later.",
                    )

                # Wait before retry (exponential backoff)
                await asyncio.sleep(2**attempt)


def safe_operation(
    operation_type: str = "api",
    timeout: float = 30.0,
    max_retries: int = 3,
    fallback_data: Optional[Dict[str, Any]] = None,
):
    """
    Decorator for wrapping operations with comprehensive error handling.

    Args:
        operation_type: Type of operation ("api", "llm", "database")
        timeout: Operation timeout in seconds
        max_retries: Maximum retry attempts
        fallback_data: Fallback data if operation fails
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            except asyncio.TimeoutError:
                logger.error(f"{operation_type} operation timeout: {func.__name__}")
                if fallback_data:
                    return fallback_data
                raise HTTPException(
                    status_code=503,
                    detail=f"{operation_type.title()} operation timeout. Please try again later.",
                )
            except Exception as e:
                logger.error(
                    f"{operation_type} operation error in {func.__name__}: {e}",
                    exc_info=True,
                )
                if fallback_data:
                    return fallback_data
                raise HTTPException(
                    status_code=503,
                    detail=f"{operation_type.title()} service temporarily unavailable. Please try again later.",
                )

        return wrapper

    return decorator


def log_operation_error(
    operation: str,
    error: Exception,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    additional_context: Optional[Dict[str, Any]] = None,
):
    """
    Log operation errors with structured information.

    Args:
        operation: Name of the operation
        error: The error that occurred
        request_id: Request identifier
        user_id: User identifier
        additional_context: Additional context information
    """
    log_data = {
        "operation": operation,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "request_id": request_id,
        "user_id": user_id,
    }

    if additional_context:
        log_data.update(additional_context)

    logger.error("Operation failed", **log_data, exc_info=True)


def create_error_response(
    error_message: str,
    error_type: str = "internal_error",
    status_code: int = 500,
    request_id: Optional[str] = None,
    fallback_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a standardized error response.

    Args:
        error_message: Error message for the client
        error_type: Type of error
        status_code: HTTP status code
        request_id: Request identifier
        fallback_data: Fallback data to include

    Returns:
        Standardized error response
    """
    response = {
        "success": False,
        "error": error_message,
        "error_type": error_type,
        "status_code": status_code,
        "timestamp": time.time(),
    }

    if request_id:
        response["request_id"] = request_id

    if fallback_data:
        response["fallback_data"] = fallback_data

    return response
