"""
Agent Utilities - Shared Functions for Agent Workflows

This module provides reusable utility functions to eliminate duplicate logic
across different agents. It includes common patterns for:

1. Task processing workflows
2. Error handling and response formatting
3. Timing and performance monitoring
4. Input validation
5. Result standardization
6. Logging and metrics

This reduces code duplication and ensures consistent behavior across agents.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps

from shared.core.unified_logging import get_logger

logger = get_logger(__name__)


class TaskStatus(Enum):
    """Task execution status."""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    VALIDATION_ERROR = "validation_error"


@dataclass
class TaskResult:
    """Standardized task result format."""
    
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    confidence: float = 0.0
    execution_time_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.SUCCESS


@dataclass
class ValidationResult:
    """Input validation result."""
    
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    sanitized_data: Dict[str, Any] = field(default_factory=dict)


class AgentTaskProcessor:
    """
    Standardized task processor for agents.
    
    This class provides a consistent workflow for processing agent tasks,
    including input validation, execution, error handling, and result formatting.
    """
    
    def __init__(self, agent_id: str):
        """Initialize the task processor."""
        self.agent_id = agent_id
        self.logger = get_logger(f"{__name__}.{agent_id}")
    
    async def process_task_with_workflow(
        self,
        task: Dict[str, Any],
        context: Any,
        processing_func: Callable,
        validation_func: Optional[Callable] = None,
        timeout_seconds: int = 30,
        **kwargs
    ) -> TaskResult:
        """
        Process a task using the standardized workflow.
        
        Args:
            task: Task data to process
            context: Query context
            processing_func: Function to execute the actual processing
            validation_func: Optional function to validate input
            timeout_seconds: Maximum execution time
            **kwargs: Additional arguments for processing function
            
        Returns:
            Standardized TaskResult
        """
        start_time = time.time()
        
        try:
            # Step 1: Validate input
            if validation_func:
                validation_result = await self._validate_input(task, context, validation_func)
                if not validation_result.is_valid:
                    return self._create_error_result(
                        validation_result.errors,
                        start_time,
                        TaskStatus.VALIDATION_ERROR
                    )
                task = validation_result.sanitized_data
            
            # Step 2: Execute processing with timeout
            result_data = await asyncio.wait_for(
                processing_func(task, context, **kwargs),
                timeout=timeout_seconds
            )
            
            # Step 3: Format successful result
            processing_time = time.time() - start_time
            return self._create_success_result(result_data, start_time)
            
        except asyncio.TimeoutError:
            self.logger.error(f"Task processing timed out after {timeout_seconds}s")
            return self._create_error_result(
                [f"Task processing timed out after {timeout_seconds} seconds"],
                start_time,
                TaskStatus.TIMEOUT
            )
        except Exception as e:
            self.logger.error(f"Task processing failed: {str(e)}")
            return self._create_error_result(
                [f"Task processing failed: {str(e)}"],
                start_time,
                TaskStatus.FAILED
            )
    
    async def _validate_input(
        self,
        task: Dict[str, Any],
        context: Any,
        validation_func: Callable
    ) -> ValidationResult:
        """Validate input using the provided validation function."""
        try:
            return await validation_func(task, context)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation failed: {str(e)}"]
            )
    
    def _create_success_result(self, data: Dict[str, Any], start_time: float) -> TaskResult:
        """Create a successful task result."""
        processing_time = int((time.time() - start_time) * 1000)
        
        return TaskResult(
            success=True,
            data=data,
            confidence=data.get("confidence", 0.0),
            execution_time_ms=processing_time,
            metadata={
                "agent_id": self.agent_id,
                "processing_time_ms": processing_time,
                "status": TaskStatus.SUCCESS.value
            }
        )
    
    def _create_error_result(
        self,
        errors: List[str],
        start_time: float,
        status: TaskStatus
    ) -> TaskResult:
        """Create an error task result."""
        processing_time = int((time.time() - start_time) * 1000)
        
        return TaskResult(
            success=False,
            error="; ".join(errors),
            confidence=0.0,
            execution_time_ms=processing_time,
            metadata={
                "agent_id": self.agent_id,
                "processing_time_ms": processing_time,
                "status": status.value,
                "errors": errors
            },
            status=status
        )


class CommonValidators:
    """Common validation functions for agent inputs."""
    
    @staticmethod
    async def validate_required_fields(
        task: Dict[str, Any],
        required_fields: List[str],
        context: Any = None
    ) -> ValidationResult:
        """Validate that required fields are present in the task."""
        missing_fields = []
        for field in required_fields:
            if field not in task or not task[field]:
                missing_fields.append(field)
        
        if missing_fields:
            return ValidationResult(
                is_valid=False,
                errors=[f"Missing required fields: {', '.join(missing_fields)}"]
            )
        
        return ValidationResult(is_valid=True, sanitized_data=task)
    
    @staticmethod
    async def validate_documents_input(
        task: Dict[str, Any],
        context: Any = None
    ) -> ValidationResult:
        """Validate documents input for agents that process documents."""
        documents = task.get("documents", [])
        
        if not documents:
            return ValidationResult(
                is_valid=False,
                errors=["No documents provided for processing"]
            )
        
        return ValidationResult(is_valid=True, sanitized_data=task)
    
    @staticmethod
    async def validate_query_input(
        task: Dict[str, Any],
        context: Any = None
    ) -> ValidationResult:
        """Validate query input for agents that process queries."""
        query = task.get("query", "")
        
        if not query or not query.strip():
            return ValidationResult(
                is_valid=False,
                errors=["No query provided for processing"]
            )
        
        return ValidationResult(is_valid=True, sanitized_data=task)
    
    @staticmethod
    async def validate_sources_input(
        task: Dict[str, Any],
        context: Any = None
    ) -> ValidationResult:
        """Validate sources input for citation agents."""
        sources = task.get("sources", [])
        
        if not sources:
            return ValidationResult(
                is_valid=False,
                errors=["No sources provided for citation processing"]
            )
        
        return ValidationResult(is_valid=True, sanitized_data=task)


class CommonProcessors:
    """Common processing functions for agents."""
    
    @staticmethod
    async def extract_task_data(
        task: Dict[str, Any],
        expected_fields: List[str]
    ) -> Dict[str, Any]:
        """Extract and validate task data."""
        extracted_data = {}
        for field in expected_fields:
            if field in task:
                extracted_data[field] = task[field]
            else:
                extracted_data[field] = None
        
        return extracted_data
    
    @staticmethod
    def calculate_confidence(
        data: Dict[str, Any],
        confidence_factors: List[str]
    ) -> float:
        """Calculate confidence based on multiple factors."""
        if not confidence_factors:
            return 0.0
        
        total_confidence = 0.0
        valid_factors = 0
        
        for factor in confidence_factors:
            if factor in data:
                factor_value = data[factor]
                if isinstance(factor_value, (int, float)):
                    total_confidence += factor_value
                    valid_factors += 1
                elif isinstance(factor_value, list):
                    # For lists, use length as confidence indicator
                    total_confidence += min(len(factor_value) / 10.0, 1.0)
                    valid_factors += 1
        
        return total_confidence / valid_factors if valid_factors > 0 else 0.0


class PerformanceMonitor:
    """Performance monitoring utilities for agents."""
    
    def __init__(self, agent_id: str):
        """Initialize performance monitor."""
        self.agent_id = agent_id
        self.logger = get_logger(f"{__name__}.performance.{agent_id}")
    
    def time_execution(self, func_name: str):
        """Decorator to time function execution."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    execution_time = (time.time() - start_time) * 1000
                    self.logger.info(
                        f"Function {func_name} completed in {execution_time:.2f}ms",
                        execution_time_ms=execution_time,
                        function=func_name
                    )
                    return result
                except Exception as e:
                    execution_time = (time.time() - start_time) * 1000
                    self.logger.error(
                        f"Function {func_name} failed after {execution_time:.2f}ms: {str(e)}",
                        execution_time_ms=execution_time,
                        function=func_name,
                        error=str(e)
                    )
                    raise
            return wrapper
        return decorator
    
    def log_processing_start(self, task_type: str, **kwargs):
        """Log the start of task processing."""
        self.logger.info(
            f"Starting {task_type} processing",
            task_type=task_type,
            agent_id=self.agent_id,
            **kwargs
        )
    
    def log_processing_complete(self, task_type: str, execution_time_ms: int, **kwargs):
        """Log the completion of task processing."""
        self.logger.info(
            f"Completed {task_type} processing in {execution_time_ms}ms",
            task_type=task_type,
            execution_time_ms=execution_time_ms,
            agent_id=self.agent_id,
            **kwargs
        )


class ErrorHandler:
    """Standardized error handling for agents."""
    
    def __init__(self, agent_id: str):
        """Initialize error handler."""
        self.agent_id = agent_id
        self.logger = get_logger(f"{__name__}.error.{agent_id}")
    
    def handle_agent_error(
        self,
        error: Exception,
        operation: str,
        context: Dict[str, Any] = None
    ) -> TaskResult:
        """Handle agent errors and return standardized error result."""
        error_message = f"{operation} failed: {str(error)}"
        self.logger.error(
            error_message,
            operation=operation,
            agent_id=self.agent_id,
            error_type=type(error).__name__,
            context=context or {}
        )
        
        return TaskResult(
            success=False,
            error=error_message,
            confidence=0.0,
            metadata={
                "agent_id": self.agent_id,
                "operation": operation,
                "error_type": type(error).__name__,
                "status": TaskStatus.FAILED.value
            },
            status=TaskStatus.FAILED
        )
    
    def handle_validation_error(
        self,
        errors: List[str],
        operation: str
    ) -> TaskResult:
        """Handle validation errors."""
        error_message = f"{operation} validation failed: {'; '.join(errors)}"
        self.logger.warning(
            error_message,
            operation=operation,
            agent_id=self.agent_id,
            errors=errors
        )
        
        return TaskResult(
            success=False,
            error=error_message,
            confidence=0.0,
            metadata={
                "agent_id": self.agent_id,
                "operation": operation,
                "errors": errors,
                "status": TaskStatus.VALIDATION_ERROR.value
            },
            status=TaskStatus.VALIDATION_ERROR
        )


class ResponseFormatter:
    """Standardized response formatting for agents."""
    
    @staticmethod
    def format_agent_response(
        success: bool,
        data: Dict[str, Any],
        error: Optional[str] = None,
        confidence: float = 0.0,
        execution_time_ms: int = 0,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Format a standardized agent response."""
        response = {
            "success": success,
            "data": data,
            "confidence": confidence,
            "execution_time_ms": execution_time_ms,
            "metadata": metadata or {}
        }
        
        if error:
            response["error"] = error
        
        return response
    
    @staticmethod
    def format_retrieval_response(
        documents: List[Dict[str, Any]],
        search_type: str,
        total_hits: int,
        query_time_ms: int,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Format a standardized retrieval response."""
        return {
            "success": True,
            "data": {
                "documents": documents,
                "search_type": search_type,
                "total_hits": total_hits,
                "query_time_ms": query_time_ms
            },
            "confidence": min(len(documents) / 10.0, 1.0),
            "execution_time_ms": query_time_ms,
            "metadata": metadata or {}
        }
    
    @staticmethod
    def format_synthesis_response(
        answer: str,
        synthesis_method: str,
        fact_count: int,
        processing_time_ms: int,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Format a standardized synthesis response."""
        return {
            "success": True,
            "data": {
                "answer": answer,
                "synthesis_method": synthesis_method,
                "fact_count": fact_count,
                "processing_time_ms": processing_time_ms
            },
            "confidence": min(fact_count / 5.0, 1.0),
            "execution_time_ms": processing_time_ms,
            "metadata": metadata or {}
        }
    
    @staticmethod
    def format_citation_response(
        cited_content: str,
        citations: List[Dict[str, Any]],
        citation_format: str,
        processing_time_ms: int,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Format a standardized citation response."""
        return {
            "success": True,
            "data": {
                "cited_content": cited_content,
                "citations": citations,
                "citation_format": citation_format,
                "processing_time_ms": processing_time_ms
            },
            "confidence": min(len(citations) / 5.0, 1.0),
            "execution_time_ms": processing_time_ms,
            "metadata": metadata or {}
        }


# Convenience functions for easy integration
def create_task_processor(agent_id: str) -> AgentTaskProcessor:
    """Create a task processor for an agent."""
    return AgentTaskProcessor(agent_id)


def create_performance_monitor(agent_id: str) -> PerformanceMonitor:
    """Create a performance monitor for an agent."""
    return PerformanceMonitor(agent_id)


def create_error_handler(agent_id: str) -> ErrorHandler:
    """Create an error handler for an agent."""
    return ErrorHandler(agent_id)


def format_standard_response(
    success: bool,
    data: Dict[str, Any],
    error: Optional[str] = None,
    confidence: float = 0.0,
    execution_time_ms: int = 0,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Format a standardized response."""
    return ResponseFormatter.format_agent_response(
        success=success,
        data=data,
        error=error,
        confidence=confidence,
        execution_time_ms=execution_time_ms,
        metadata=metadata
    )


# Decorator for timing agent functions
def time_agent_function(agent_id: str):
    """Decorator to time agent function execution."""
    monitor = PerformanceMonitor(agent_id)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await monitor.time_execution(func.__name__)(func)(*args, **kwargs)
        return wrapper
    return decorator 