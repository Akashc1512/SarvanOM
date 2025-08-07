"""
Orchestration Utilities - Common Orchestration Patterns for Agents

This module provides utilities for common orchestration patterns found across
orchestrators, workflow managers, and agent execution systems.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from shared.core.unified_logging import get_logger

logger = get_logger(__name__)


class OrchestrationStatus(str, Enum):
    """Orchestration status enumeration."""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    PARTIAL_SUCCESS = "partial_success"
    CANCELLED = "cancelled"


@dataclass
class OrchestrationResult:
    """Standardized orchestration result."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: int = 0
    status: OrchestrationStatus = OrchestrationStatus.SUCCESS
    metadata: Dict[str, Any] = field(default_factory=dict)
    partial_results: Dict[str, Any] = field(default_factory=dict)


class AgentExecutionWorkflow:
    """Standardized agent execution workflow."""
    
    def __init__(self, orchestrator_id: str):
        self.orchestrator_id = orchestrator_id
        self.logger = get_logger(f"{__name__}.workflow.{orchestrator_id}")
    
    async def execute_agent_with_timeout(
        self,
        agent,
        context: Any,
        agent_type: str,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
        fallback_enabled: bool = True
    ) -> OrchestrationResult:
        """
        Execute a single agent with timeout and error handling.
        
        Args:
            agent: Agent instance to execute
            context: Execution context
            agent_type: Type of agent for logging
            timeout_seconds: Execution timeout
            max_retries: Maximum retry attempts
            fallback_enabled: Whether to use fallback on failure
            
        Returns:
            OrchestrationResult with execution results
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting {agent_type} execution")
            
            # Execute with timeout and retries
            result = await self._execute_with_retry(
                agent,
                context,
                timeout=timeout_seconds,
                max_retries=max_retries
            )
            
            execution_time = int((time.time() - start_time) * 1000)
            
            self.logger.info(f"Completed {agent_type} execution in {execution_time}ms")
            
            return OrchestrationResult(
                success=True,
                data=result,
                execution_time_ms=execution_time,
                status=OrchestrationStatus.SUCCESS,
                metadata={
                    "orchestrator_id": self.orchestrator_id,
                    "agent_type": agent_type,
                    "retries_used": 0  # Would be tracked in actual implementation
                }
            )
            
        except asyncio.TimeoutError:
            execution_time = int((time.time() - start_time) * 1000)
            self.logger.error(f"Agent {agent_type} timed out after {timeout_seconds}s")
            
            # Try fallback if enabled
            if fallback_enabled:
                try:
                    fallback_result = await self._execute_fallback(agent, context, agent_type)
                    return OrchestrationResult(
                        success=True,
                        data=fallback_result,
                        execution_time_ms=execution_time,
                        status=OrchestrationStatus.PARTIAL_SUCCESS,
                        metadata={
                            "orchestrator_id": self.orchestrator_id,
                            "agent_type": agent_type,
                            "fallback_used": True,
                            "timeout": True
                        }
                    )
                except Exception as e:
                    self.logger.error(f"Fallback for {agent_type} also failed: {e}")
            
            return OrchestrationResult(
                success=False,
                error=f"Agent {agent_type} timed out after {timeout_seconds} seconds",
                execution_time_ms=execution_time,
                status=OrchestrationStatus.TIMEOUT
            )
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self.logger.error(f"Agent {agent_type} execution failed: {e}")
            
            return OrchestrationResult(
                success=False,
                error=f"Agent {agent_type} execution failed: {str(e)}",
                execution_time_ms=execution_time,
                status=OrchestrationStatus.FAILED
            )
    
    async def _execute_with_retry(
        self,
        agent,
        context: Any,
        timeout: float = 30.0,
        max_retries: int = 3
    ) -> Any:
        """Execute agent with retry logic."""
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return await asyncio.wait_for(
                    agent.execute(context),
                    timeout=timeout
                )
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    self.logger.warning(f"Retry {attempt + 1}/{max_retries} for {agent.__class__.__name__}: {e}")
        
        raise last_exception
    
    async def _execute_fallback(self, agent, context: Any, agent_type: str) -> Any:
        """Execute fallback logic for agent."""
        # Implement fallback logic here
        # This could be a simplified version of the agent's logic
        return {"fallback": True, "agent_type": agent_type}


class PipelineOrchestrator:
    """Standardized pipeline orchestration."""
    
    def __init__(self, pipeline_id: str):
        self.pipeline_id = pipeline_id
        self.logger = get_logger(f"{__name__}.pipeline.{pipeline_id}")
        self.execution_workflow = AgentExecutionWorkflow(pipeline_id)
    
    async def execute_pipeline(
        self,
        agents: List[Any],
        context: Any,
        pipeline_config: Dict[str, Any]
    ) -> OrchestrationResult:
        """
        Execute a pipeline of agents with proper error handling and timeouts.
        
        Args:
            agents: List of agents to execute
            context: Execution context
            pipeline_config: Pipeline configuration
            
        Returns:
            OrchestrationResult with pipeline results
        """
        start_time = time.time()
        results = {}
        partial_results = {}
        
        try:
            for i, agent in enumerate(agents):
                agent_type = getattr(agent, 'agent_type', f'agent_{i}').value
                
                # Execute agent with timeout
                result = await self.execution_workflow.execute_agent_with_timeout(
                    agent=agent,
                    context=context,
                    agent_type=agent_type,
                    timeout_seconds=pipeline_config.get('agent_timeout', 30.0),
                    max_retries=pipeline_config.get('max_retries', 3),
                    fallback_enabled=pipeline_config.get('fallback_enabled', True)
                )
                
                results[agent_type] = result
                
                # Store partial results even if some agents fail
                if result.success:
                    partial_results[agent_type] = result.data
                else:
                    partial_results[agent_type] = {"error": result.error}
                
                # Check if we should continue on partial failures
                if not result.success and not pipeline_config.get('continue_on_failure', True):
                    break
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Determine overall success
            successful_agents = sum(1 for r in results.values() if r.success)
            total_agents = len(agents)
            
            if successful_agents == total_agents:
                status = OrchestrationStatus.SUCCESS
            elif successful_agents > 0:
                status = OrchestrationStatus.PARTIAL_SUCCESS
            else:
                status = OrchestrationStatus.FAILED
            
            return OrchestrationResult(
                success=successful_agents > 0,
                data=partial_results,
                execution_time_ms=execution_time,
                status=status,
                metadata={
                    "pipeline_id": self.pipeline_id,
                    "total_agents": total_agents,
                    "successful_agents": successful_agents,
                    "failed_agents": total_agents - successful_agents
                },
                partial_results=results
            )
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self.logger.error(f"Pipeline execution failed: {e}")
            
            return OrchestrationResult(
                success=False,
                error=f"Pipeline execution failed: {str(e)}",
                execution_time_ms=execution_time,
                status=OrchestrationStatus.FAILED,
                partial_results=results
            )


class WorkflowManager:
    """Standardized workflow management."""
    
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.logger = get_logger(f"{__name__}.workflow.{workflow_id}")
    
    async def execute_workflow(
        self,
        workflow_steps: List[Dict[str, Any]],
        input_data: Dict[str, Any],
        context: Any
    ) -> OrchestrationResult:
        """
        Execute a workflow with multiple steps.
        
        Args:
            workflow_steps: List of workflow steps
            input_data: Input data for the workflow
            context: Execution context
            
        Returns:
            OrchestrationResult with workflow results
        """
        start_time = time.time()
        step_results = {}
        current_data = input_data.copy()
        
        try:
            for i, step in enumerate(workflow_steps):
                step_id = step.get('id', f'step_{i}')
                step_type = step.get('type', 'unknown')
                
                self.logger.info(f"Executing workflow step {step_id} ({step_type})")
                
                # Execute step
                step_result = await self._execute_workflow_step(
                    step=step,
                    input_data=current_data,
                    context=context
                )
                
                step_results[step_id] = step_result
                
                # Update current data for next step
                if step_result.success:
                    current_data.update(step_result.data or {})
                else:
                    # Handle step failure based on workflow configuration
                    if not step.get('continue_on_failure', False):
                        break
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Determine overall success
            successful_steps = sum(1 for r in step_results.values() if r.success)
            total_steps = len(workflow_steps)
            
            if successful_steps == total_steps:
                status = OrchestrationStatus.SUCCESS
            elif successful_steps > 0:
                status = OrchestrationStatus.PARTIAL_SUCCESS
            else:
                status = OrchestrationStatus.FAILED
            
            return OrchestrationResult(
                success=successful_steps > 0,
                data=current_data,
                execution_time_ms=execution_time,
                status=status,
                metadata={
                    "workflow_id": self.workflow_id,
                    "total_steps": total_steps,
                    "successful_steps": successful_steps,
                    "failed_steps": total_steps - successful_steps
                },
                partial_results=step_results
            )
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self.logger.error(f"Workflow execution failed: {e}")
            
            return OrchestrationResult(
                success=False,
                error=f"Workflow execution failed: {str(e)}",
                execution_time_ms=execution_time,
                status=OrchestrationStatus.FAILED,
                partial_results=step_results
            )
    
    async def _execute_workflow_step(
        self,
        step: Dict[str, Any],
        input_data: Dict[str, Any],
        context: Any
    ) -> OrchestrationResult:
        """Execute a single workflow step."""
        start_time = time.time()
        
        try:
            step_type = step.get('type', 'unknown')
            step_timeout = step.get('timeout', 30.0)
            
            # Execute step based on type
            if step_type == 'agent':
                result = await self._execute_agent_step(step, input_data, context)
            elif step_type == 'function':
                result = await self._execute_function_step(step, input_data, context)
            elif step_type == 'condition':
                result = await self._execute_condition_step(step, input_data, context)
            else:
                raise ValueError(f"Unknown step type: {step_type}")
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return OrchestrationResult(
                success=True,
                data=result,
                execution_time_ms=execution_time,
                status=OrchestrationStatus.SUCCESS
            )
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self.logger.error(f"Workflow step failed: {e}")
            
            return OrchestrationResult(
                success=False,
                error=f"Workflow step failed: {str(e)}",
                execution_time_ms=execution_time,
                status=OrchestrationStatus.FAILED
            )
    
    async def _execute_agent_step(
        self,
        step: Dict[str, Any],
        input_data: Dict[str, Any],
        context: Any
    ) -> Dict[str, Any]:
        """Execute an agent step."""
        # Implementation would depend on agent availability
        return {"agent_result": "mock_result"}
    
    async def _execute_function_step(
        self,
        step: Dict[str, Any],
        input_data: Dict[str, Any],
        context: Any
    ) -> Dict[str, Any]:
        """Execute a function step."""
        # Implementation would depend on function availability
        return {"function_result": "mock_result"}
    
    async def _execute_condition_step(
        self,
        step: Dict[str, Any],
        input_data: Dict[str, Any],
        context: Any
    ) -> Dict[str, Any]:
        """Execute a condition step."""
        # Implementation would evaluate conditions
        return {"condition_result": True}


# Utility functions

def create_agent_execution_workflow(orchestrator_id: str) -> AgentExecutionWorkflow:
    """Create agent execution workflow."""
    return AgentExecutionWorkflow(orchestrator_id)


def create_pipeline_orchestrator(pipeline_id: str) -> PipelineOrchestrator:
    """Create pipeline orchestrator."""
    return PipelineOrchestrator(pipeline_id)


def create_workflow_manager(workflow_id: str) -> WorkflowManager:
    """Create workflow manager."""
    return WorkflowManager(workflow_id)


def time_orchestration(operation_name: str):
    """Decorator to time orchestration operations."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                logger.info(
                    f"Orchestration {operation_name} completed in {execution_time:.2f}ms",
                    operation=operation_name,
                    execution_time_ms=execution_time
                )
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                logger.error(
                    f"Orchestration {operation_name} failed after {execution_time:.2f}ms: {str(e)}",
                    operation=operation_name,
                    execution_time_ms=execution_time,
                    error=str(e)
                )
                raise
        return wrapper
    return decorator


def format_orchestration_result(
    success: bool,
    data: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    execution_time_ms: int = 0,
    status: OrchestrationStatus = OrchestrationStatus.SUCCESS,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Format orchestration result in standard format."""
    return {
        "success": success,
        "data": data or {},
        "error": error,
        "execution_time_ms": execution_time_ms,
        "status": status.value,
        "metadata": metadata or {}
    } 