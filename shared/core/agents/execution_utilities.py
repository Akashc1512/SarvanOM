"""
Execution Utilities - Common Execution Patterns for Agents

This module provides utilities for common execution patterns found across agents,
including timing, error handling, result formatting, and execution workflows.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from shared.core.unified_logging import get_logger

logger = get_logger(__name__)


class ExecutionStatus(str, Enum):
    """Execution status enumeration."""

    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    VALIDATION_ERROR = "validation_error"
    PROCESSING_ERROR = "processing_error"


@dataclass
class ExecutionResult:
    """Standardized execution result."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: int = 0
    status: ExecutionStatus = ExecutionStatus.SUCCESS
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExecutionTimer:
    """Context manager for timing operations."""

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.logger = get_logger(f"{__name__}.timer")

    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Starting {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (time.time() - self.start_time) * 1000
        if exc_type is None:
            self.logger.info(f"Completed {self.operation_name} in {duration:.2f}ms")
        else:
            self.logger.error(
                f"Failed {self.operation_name} after {duration:.2f}ms: {exc_val}"
            )
        return False  # Don't suppress exceptions


class ExecutionWorkflow:
    """Standardized execution workflow for agents."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.logger = get_logger(f"{__name__}.workflow.{agent_id}")

    async def execute_with_workflow(
        self,
        operation_name: str,
        operation_func: Callable,
        *args,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
        fallback_func: Optional[Callable] = None,
        **kwargs,
    ) -> ExecutionResult:
        """
        Execute operation with standardized workflow.

        Args:
            operation_name: Name of the operation for logging
            operation_func: Function to execute
            timeout_seconds: Operation timeout
            max_retries: Maximum retry attempts
            fallback_func: Optional fallback function
            **kwargs: Additional arguments for operation

        Returns:
            ExecutionResult with standardized format
        """
        start_time = time.time()

        try:
            # Execute with timeout and retries
            result = await self._execute_with_retry(
                operation_func,
                *args,
                timeout=timeout_seconds,
                max_retries=max_retries,
                **kwargs,
            )

            execution_time = int((time.time() - start_time) * 1000)

            return ExecutionResult(
                success=True,
                data=result,
                execution_time_ms=execution_time,
                status=ExecutionStatus.SUCCESS,
                metadata={
                    "agent_id": self.agent_id,
                    "operation": operation_name,
                    "retries_used": 0,  # Would be tracked in actual implementation
                },
            )

        except asyncio.TimeoutError:
            execution_time = int((time.time() - start_time) * 1000)
            self.logger.error(
                f"Operation {operation_name} timed out after {timeout_seconds}s"
            )

            # Try fallback if available
            if fallback_func:
                try:
                    fallback_result = await fallback_func(*args, **kwargs)
                    return ExecutionResult(
                        success=True,
                        data=fallback_result,
                        execution_time_ms=execution_time,
                        status=ExecutionStatus.SUCCESS,
                        metadata={
                            "agent_id": self.agent_id,
                            "operation": operation_name,
                            "fallback_used": True,
                        },
                    )
                except Exception as e:
                    self.logger.error(f"Fallback for {operation_name} also failed: {e}")

            return ExecutionResult(
                success=False,
                error=f"Operation {operation_name} timed out after {timeout_seconds} seconds",
                execution_time_ms=execution_time,
                status=ExecutionStatus.TIMEOUT,
            )

        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self.logger.error(f"Operation {operation_name} failed: {e}")

            return ExecutionResult(
                success=False,
                error=f"Operation {operation_name} failed: {str(e)}",
                execution_time_ms=execution_time,
                status=ExecutionStatus.FAILED,
            )

    async def _execute_with_retry(
        self,
        func: Callable,
        *args,
        timeout: float = 30.0,
        max_retries: int = 3,
        **kwargs,
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
                    self.logger.warning(
                        f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}"
                    )

        raise last_exception


class ResultFormatter:
    """Standardized result formatting utilities."""

    @staticmethod
    def format_agent_result(
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        confidence: float = 0.0,
        execution_time_ms: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Format agent result in standard format."""
        return {
            "success": success,
            "data": data or {},
            "error": error,
            "confidence": confidence,
            "execution_time_ms": execution_time_ms,
            "metadata": metadata or {},
        }

    @staticmethod
    def format_error_result(
        error: str,
        execution_time_ms: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Format error result in standard format."""
        return {
            "success": False,
            "data": {},
            "error": error,
            "confidence": 0.0,
            "execution_time_ms": execution_time_ms,
            "metadata": metadata or {},
        }

    @staticmethod
    def format_success_result(
        data: Dict[str, Any],
        confidence: float = 1.0,
        execution_time_ms: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Format success result in standard format."""
        return {
            "success": True,
            "data": data,
            "error": None,
            "confidence": confidence,
            "execution_time_ms": execution_time_ms,
            "metadata": metadata or {},
        }


def time_execution(operation_name: str):
    """Decorator to time function execution."""

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


def handle_execution_errors(func):
    """Decorator to handle execution errors with standardized response."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = int((time.time() - start_time) * 1000)

            # Ensure result has standard format
            if isinstance(result, dict) and "success" in result:
                result["execution_time_ms"] = execution_time
                return result
            else:
                return ResultFormatter.format_success_result(
                    data=result, execution_time_ms=execution_time
                )

        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"Function {func.__name__} failed: {str(e)}")

            return ResultFormatter.format_error_result(
                error=str(e), execution_time_ms=execution_time
            )

    return wrapper


class ExecutionMetrics:
    """Execution metrics tracking."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.metrics = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_execution_time_ms": 0,
            "average_execution_time_ms": 0,
        }

    def record_execution(self, success: bool, execution_time_ms: int):
        """Record execution metrics."""
        self.metrics["total_executions"] += 1
        self.metrics["total_execution_time_ms"] += execution_time_ms

        if success:
            self.metrics["successful_executions"] += 1
        else:
            self.metrics["failed_executions"] += 1

        # Update average
        if self.metrics["total_executions"] > 0:
            self.metrics["average_execution_time_ms"] = (
                self.metrics["total_execution_time_ms"]
                / self.metrics["total_executions"]
            )

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return {
            "agent_id": self.agent_id,
            **self.metrics,
            "success_rate": (
                self.metrics["successful_executions"] / self.metrics["total_executions"]
                if self.metrics["total_executions"] > 0
                else 0
            ),
        }


# Utility functions for common patterns


def create_execution_workflow(agent_id: str) -> ExecutionWorkflow:
    """Create execution workflow for an agent."""
    return ExecutionWorkflow(agent_id)


def create_execution_metrics(agent_id: str) -> ExecutionMetrics:
    """Create execution metrics for an agent."""
    return ExecutionMetrics(agent_id)


def format_execution_result(
    success: bool,
    data: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    confidence: float = 0.0,
    execution_time_ms: int = 0,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Format execution result in standard format."""
    return ResultFormatter.format_agent_result(
        success=success,
        data=data,
        error=error,
        confidence=confidence,
        execution_time_ms=execution_time_ms,
        metadata=metadata,
    )
