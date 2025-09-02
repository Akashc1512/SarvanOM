"""
Simple Agent Task Processor

This module provides a basic task processor for agents to use while we consolidate
the workflow management functionality.
"""

import time
import asyncio
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass


@dataclass
class TaskResult:
    """Result of a task processing operation."""
    
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    confidence: float = 0.0
    execution_time_ms: int = 0
    metadata: Optional[Dict[str, Any]] = None


class AgentTaskProcessor:
    """Simple task processor for agents."""
    
    def __init__(self, agent_id: str):
        """Initialize the task processor."""
        self.agent_id = agent_id
        
    async def process_task_with_workflow(
        self,
        task: Dict[str, Any],
        context: Any,
        processing_func: Callable,
        validation_func: Optional[Callable] = None,
        timeout_seconds: int = 60,
        **kwargs
    ) -> TaskResult:
        """
        Process a task using the specified workflow.
        
        Args:
            task: Task data to process
            context: Context for the task
            processing_func: Function to process the task
            validation_func: Optional validation function
            timeout_seconds: Timeout for the task
            **kwargs: Additional arguments
            
        Returns:
            TaskResult with the processing results
        """
        start_time = time.time()
        
        try:
            # Validate input if validation function provided
            if validation_func:
                validation_result = await validation_func(task, context)
                if not validation_result.is_valid:
                    return TaskResult(
                        success=False,
                        error=f"Validation failed: {validation_result.errors}",
                        execution_time_ms=int((time.time() - start_time) * 1000)
                    )
            
            # Process the task with timeout
            result = await asyncio.wait_for(
                processing_func(task, context),
                timeout=timeout_seconds
            )
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            return TaskResult(
                success=True,
                data=result,
                confidence=result.get("confidence", 0.8),
                execution_time_ms=execution_time_ms,
                metadata={"agent_id": self.agent_id}
            )
            
        except asyncio.TimeoutError:
            return TaskResult(
                success=False,
                error="Task processing timed out",
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        except Exception as e:
            return TaskResult(
                success=False,
                error=f"Task processing failed: {str(e)}",
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
