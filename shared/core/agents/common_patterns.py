"""
Common Patterns - Extracted Duplicate Logic for Reuse

This module contains extracted common patterns from various agents and services
that can be reused across the codebase without losing original functionality.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from shared.core.unified_logging import get_logger

logger = get_logger(__name__)


class ExecutionPattern:
    """Common execution pattern with timing and error handling."""

    @staticmethod
    async def execute_with_timing(
        operation_name: str,
        operation_func: Callable,
        *args,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
        fallback_func: Optional[Callable] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Execute operation with standardized timing and error handling.

        This preserves the original functionality while providing consistent patterns.
        """
        start_time = time.time()

        try:
            # Execute with timeout and retries
            result = await ExecutionPattern._execute_with_retry(
                operation_func,
                *args,
                timeout=timeout_seconds,
                max_retries=max_retries,
                **kwargs,
            )

            execution_time = int((time.time() - start_time) * 1000)

            return {
                "success": True,
                "data": result,
                "execution_time_ms": execution_time,
                "operation": operation_name,
            }

        except asyncio.TimeoutError:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(
                f"Operation {operation_name} timed out after {timeout_seconds}s"
            )

            # Try fallback if available
            if fallback_func:
                try:
                    fallback_result = await fallback_func(*args, **kwargs)
                    return {
                        "success": True,
                        "data": fallback_result,
                        "execution_time_ms": execution_time,
                        "operation": operation_name,
                        "fallback_used": True,
                    }
                except Exception as e:
                    logger.error(f"Fallback for {operation_name} also failed: {e}")

            return {
                "success": False,
                "error": f"Operation {operation_name} timed out after {timeout_seconds} seconds",
                "execution_time_ms": execution_time,
                "operation": operation_name,
            }

        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"Operation {operation_name} failed: {e}")

            return {
                "success": False,
                "error": f"Operation {operation_name} failed: {str(e)}",
                "execution_time_ms": execution_time,
                "operation": operation_name,
            }

    @staticmethod
    async def _execute_with_retry(
        func: Callable, *args, timeout: float = 30.0, max_retries: int = 3, **kwargs
    ) -> Any:
        """Execute function with retry logic."""
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    await asyncio.sleep(2**attempt)  # Exponential backoff
                    logger.warning(
                        f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}"
                    )

        raise last_exception


class AgentProcessPattern:
    """Common agent process_task pattern."""

    @staticmethod
    async def process_with_standard_workflow(
        agent_id: str,
        task: Dict[str, Any],
        context: Any,
        processing_func: Callable,
        validation_func: Optional[Callable] = None,
        timeout_seconds: int = 30,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Standard agent process_task workflow.

        This preserves all original functionality while providing consistent patterns.
        """
        start_time = time.time()

        try:
            # Step 1: Validate input (if validation function provided)
            if validation_func:
                validation_result = await AgentProcessPattern._validate_input(
                    task, context, validation_func
                )
                if not validation_result["is_valid"]:
                    return AgentProcessPattern._create_error_result(
                        validation_result["errors"], start_time, agent_id
                    )
                task = validation_result["sanitized_data"]

            # Step 2: Execute processing with timeout
            result_data = await asyncio.wait_for(
                processing_func(task, context, **kwargs), timeout=timeout_seconds
            )

            # Step 3: Format successful result
            processing_time = int((time.time() - start_time) * 1000)
            return AgentProcessPattern._create_success_result(
                result_data, start_time, agent_id
            )

        except asyncio.TimeoutError:
            logger.error(f"Task processing timed out after {timeout_seconds}s")
            return AgentProcessPattern._create_error_result(
                [f"Task processing timed out after {timeout_seconds} seconds"],
                start_time,
                agent_id,
            )
        except Exception as e:
            logger.error(f"Task processing failed: {str(e)}")
            return AgentProcessPattern._create_error_result(
                [f"Task processing failed: {str(e)}"], start_time, agent_id
            )

    @staticmethod
    async def _validate_input(
        task: Dict[str, Any], context: Any, validation_func: Callable
    ) -> Dict[str, Any]:
        """Validate input using the provided validation function."""
        try:
            return await validation_func(task, context)
        except Exception as e:
            return {"is_valid": False, "errors": [f"Validation failed: {str(e)}"]}

    @staticmethod
    def _create_success_result(
        data: Dict[str, Any], start_time: float, agent_id: str
    ) -> Dict[str, Any]:
        """Create a successful task result."""
        processing_time = int((time.time() - start_time) * 1000)

        return {
            "success": True,
            "data": data,
            "confidence": data.get("confidence", 0.0),
            "execution_time_ms": processing_time,
            "metadata": {
                "agent_id": agent_id,
                "processing_time_ms": processing_time,
                "status": "success",
            },
        }

    @staticmethod
    def _create_error_result(
        errors: List[str], start_time: float, agent_id: str
    ) -> Dict[str, Any]:
        """Create an error task result."""
        processing_time = int((time.time() - start_time) * 1000)

        return {
            "success": False,
            "error": "; ".join(errors),
            "confidence": 0.0,
            "execution_time_ms": processing_time,
            "metadata": {
                "agent_id": agent_id,
                "processing_time_ms": processing_time,
                "status": "error",
                "errors": errors,
            },
        }


class ValidationPattern:
    """Common validation patterns."""

    @staticmethod
    async def validate_query_input(
        task: Dict[str, Any], context: Any = None
    ) -> Dict[str, Any]:
        """Validate query input."""
        query = task.get("query", "")

        if not query or not isinstance(query, str):
            return {"is_valid": False, "errors": ["Query must be a non-empty string"]}

        if len(query.strip()) == 0:
            return {"is_valid": False, "errors": ["Query cannot be empty"]}

        if len(query) > 10000:
            return {
                "is_valid": False,
                "errors": ["Query too long (max 10000 characters)"],
            }

        return {"is_valid": True, "sanitized_data": {"query": query.strip()}}

    @staticmethod
    async def validate_documents_input(
        task: Dict[str, Any], context: Any = None
    ) -> Dict[str, Any]:
        """Validate documents input."""
        documents = task.get("documents", [])

        if not documents:
            return {"is_valid": False, "errors": ["No documents provided"]}

        if not isinstance(documents, list):
            return {"is_valid": False, "errors": ["Documents must be a list"]}

        for i, doc in enumerate(documents):
            if not isinstance(doc, dict):
                return {
                    "is_valid": False,
                    "errors": [f"Document {i} must be a dictionary"],
                }
            if "content" not in doc:
                return {
                    "is_valid": False,
                    "errors": [f"Document {i} missing 'content' field"],
                }

        return {"is_valid": True, "sanitized_data": {"documents": documents}}

    @staticmethod
    async def validate_sources_input(
        task: Dict[str, Any], context: Any = None
    ) -> Dict[str, Any]:
        """Validate sources input."""
        sources = task.get("sources", [])

        if not sources:
            return {"is_valid": False, "errors": ["No sources provided"]}

        if not isinstance(sources, list):
            return {"is_valid": False, "errors": ["Sources must be a list"]}

        for i, source in enumerate(sources):
            if not isinstance(source, dict):
                return {
                    "is_valid": False,
                    "errors": [f"Source {i} must be a dictionary"],
                }

        return {"is_valid": True, "sanitized_data": {"sources": sources}}

    @staticmethod
    async def validate_required_fields(
        task: Dict[str, Any], required_fields: List[str], context: Any = None
    ) -> Dict[str, Any]:
        """Validate required fields."""
        missing_fields = []

        for field in required_fields:
            if field not in task or not task[field]:
                missing_fields.append(field)

        if missing_fields:
            return {
                "is_valid": False,
                "errors": [f"Missing required fields: {', '.join(missing_fields)}"],
            }

        return {"is_valid": True, "sanitized_data": task}


class OrchestrationPattern:
    """Common orchestration patterns."""

    @staticmethod
    async def execute_agent_with_timeout(
        agent,
        context: Any,
        agent_type: str,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
        fallback_enabled: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute a single agent with timeout and error handling.

        This preserves all original functionality while providing consistent patterns.
        """
        start_time = time.time()

        try:
            logger.info(f"Starting {agent_type} execution")

            # Execute with timeout and retries
            result = await OrchestrationPattern._execute_with_retry(
                agent, context, timeout=timeout_seconds, max_retries=max_retries
            )

            execution_time = int((time.time() - start_time) * 1000)

            logger.info(f"Completed {agent_type} execution in {execution_time}ms")

            return {
                "success": True,
                "data": result,
                "execution_time_ms": execution_time,
                "agent_type": agent_type,
            }

        except asyncio.TimeoutError:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"Agent {agent_type} timed out after {timeout_seconds}s")

            # Try fallback if enabled
            if fallback_enabled:
                try:
                    fallback_result = await OrchestrationPattern._execute_fallback(
                        agent, context, agent_type
                    )
                    return {
                        "success": True,
                        "data": fallback_result,
                        "execution_time_ms": execution_time,
                        "agent_type": agent_type,
                        "fallback_used": True,
                    }
                except Exception as e:
                    logger.error(f"Fallback for {agent_type} also failed: {e}")

            return {
                "success": False,
                "error": f"Agent {agent_type} timed out after {timeout_seconds} seconds",
                "execution_time_ms": execution_time,
                "agent_type": agent_type,
            }

        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"Agent {agent_type} execution failed: {e}")

            return {
                "success": False,
                "error": f"Agent {agent_type} execution failed: {str(e)}",
                "execution_time_ms": execution_time,
                "agent_type": agent_type,
            }

    @staticmethod
    async def _execute_with_retry(
        agent, context: Any, timeout: float = 30.0, max_retries: int = 3
    ) -> Any:
        """Execute agent with retry logic."""
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                return await asyncio.wait_for(agent.execute(context), timeout=timeout)
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    await asyncio.sleep(2**attempt)  # Exponential backoff
                    logger.warning(
                        f"Retry {attempt + 1}/{max_retries} for {agent.__class__.__name__}: {e}"
                    )

        raise last_exception

    @staticmethod
    async def _execute_fallback(agent, context: Any, agent_type: str) -> Any:
        """Execute fallback logic for agent."""
        # Implement fallback logic here
        # This could be a simplified version of the agent's logic
        return {"fallback": True, "agent_type": agent_type}


class ServicePattern:
    """Common service patterns."""

    @staticmethod
    async def execute_service_operation(
        service_name: str,
        operation_name: str,
        operation_func: Callable,
        *args,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
        fallback_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Execute service operation with standardized error handling.

        This preserves all original functionality while providing consistent patterns.
        """
        start_time = time.time()

        try:
            # Execute operation with timeout and retries
            result = await ServicePattern._execute_with_retry(
                operation_func,
                *args,
                timeout=timeout_seconds,
                max_retries=max_retries,
                **kwargs,
            )

            execution_time = int((time.time() - start_time) * 1000)

            return {
                "success": True,
                "data": result,
                "execution_time_ms": execution_time,
                "service": service_name,
                "operation": operation_name,
            }

        except asyncio.TimeoutError:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(
                f"Service {service_name}.{operation_name} timed out after {timeout_seconds}s"
            )

            return {
                "success": False,
                "error": f"Service {service_name}.{operation_name} timed out after {timeout_seconds} seconds",
                "execution_time_ms": execution_time,
                "service": service_name,
                "operation": operation_name,
                "fallback_data": fallback_data,
            }

        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"Service {service_name}.{operation_name} failed: {e}")

            return {
                "success": False,
                "error": f"Service {service_name}.{operation_name} failed: {str(e)}",
                "execution_time_ms": execution_time,
                "service": service_name,
                "operation": operation_name,
                "fallback_data": fallback_data,
            }

    @staticmethod
    async def _execute_with_retry(
        func: Callable, *args, timeout: float = 30.0, max_retries: int = 3, **kwargs
    ) -> Any:
        """Execute function with retry logic."""
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    await asyncio.sleep(2**attempt)  # Exponential backoff
                    logger.warning(
                        f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}"
                    )

        raise last_exception


# Decorators for common patterns


def time_operation(operation_name: str):
    """Decorator to time operations."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                logger.info(
                    f"Operation {operation_name} completed in {execution_time:.2f}ms",
                    operation=operation_name,
                    execution_time_ms=execution_time,
                )
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                logger.error(
                    f"Operation {operation_name} failed after {execution_time:.2f}ms: {str(e)}",
                    operation=operation_name,
                    execution_time_ms=execution_time,
                    error=str(e),
                )
                raise

        return wrapper

    return decorator


def handle_errors_with_fallback(fallback_data: Optional[Dict[str, Any]] = None):
    """Decorator to handle errors with fallback."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Function {func.__name__} failed: {str(e)}")
                if fallback_data:
                    return fallback_data
                raise

        return wrapper

    return decorator


# Utility functions for easy integration


def create_agent_process_workflow(agent_id: str) -> Callable:
    """Create agent process workflow function."""

    def workflow(
        task: Dict[str, Any], context: Any, processing_func: Callable, **kwargs
    ) -> Dict[str, Any]:
        return AgentProcessPattern.process_with_standard_workflow(
            agent_id=agent_id,
            task=task,
            context=context,
            processing_func=processing_func,
            **kwargs,
        )

    return workflow


def create_service_operation(service_name: str) -> Callable:
    """Create service operation function."""

    def operation(
        operation_name: str, operation_func: Callable, **kwargs
    ) -> Dict[str, Any]:
        return ServicePattern.execute_service_operation(
            service_name=service_name,
            operation_name=operation_name,
            operation_func=operation_func,
            **kwargs,
        )

    return operation


def create_orchestration_workflow() -> Callable:
    """Create orchestration workflow function."""

    def workflow(agent, context: Any, agent_type: str, **kwargs) -> Dict[str, Any]:
        return OrchestrationPattern.execute_agent_with_timeout(
            agent=agent, context=context, agent_type=agent_type, **kwargs
        )

    return workflow
