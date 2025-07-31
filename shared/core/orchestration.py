"""
Enterprise Orchestration System - Universal Knowledge Platform
Stateful, observable, and modular orchestration patterns for multi-agent workflows.

Features:
- Stateful workflow management with persistence
- Comprehensive observability and tracing
- Modular agent composition
- Circuit breaker and retry patterns
- Event-driven architecture
- Performance monitoring and metrics
- Graceful degradation and fallbacks

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import asyncio
import logging
import time
import uuid
from typing import (
    Dict,
    List,
    Any,
    Optional,
    Union,
    Callable,
    Awaitable,
    TypeVar,
    Generic,
    Protocol,
)
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
from contextlib import asynccontextmanager
import json
import traceback

from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger(__name__)

# Type variables
T = TypeVar("T")
WorkflowState = TypeVar("WorkflowState")


class WorkflowStatus(Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class AgentType(Enum):
    """Agent types for workflow orchestration."""

    RETRIEVAL = "retrieval"
    FACT_CHECK = "fact_check"
    SYNTHESIS = "synthesis"
    CITATION = "citation"
    ROUTER = "router"
    VALIDATOR = "validator"


@dataclass
class WorkflowContext:
    """Context for workflow execution."""

    workflow_id: str
    trace_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    timeout_seconds: int = 300  # 5 minutes default


@dataclass
class WorkflowStep:
    """Individual step in a workflow."""

    step_id: str
    agent_type: AgentType
    name: str
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 30
    retry_count: int = 3
    retry_delay_seconds: int = 5
    circuit_breaker_enabled: bool = True
    fallback_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowResult:
    """Result of workflow execution."""

    workflow_id: str
    status: WorkflowStatus
    steps_results: Dict[str, Any]
    final_result: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: int = 0
    token_usage: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowState(BaseModel):
    """Persistent workflow state."""

    workflow_id: str
    status: WorkflowStatus
    current_step: Optional[str] = None
    completed_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)
    step_results: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    timeout_at: Optional[datetime] = None


class AgentProtocol(Protocol):
    """Protocol for agent implementations."""

    async def process_task(
        self, task_data: Dict[str, Any], context: WorkflowContext
    ) -> Dict[str, Any]:
        """Process a task and return results."""
        ...


class WorkflowEngine:
    """Enterprise workflow engine with stateful execution."""

    def __init__(
        self,
        state_store: Optional["StateStore"] = None,
        observability: Optional["ObservabilityManager"] = None,
        circuit_breaker: Optional["CircuitBreaker"] = None,
    ):
        self.state_store = state_store or InMemoryStateStore()
        self.observability = observability or ObservabilityManager()
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.agents: Dict[AgentType, AgentProtocol] = {}
        self.workflows: Dict[str, "WorkflowDefinition"] = {}
        self._lock = asyncio.Lock()

    def register_agent(self, agent_type: AgentType, agent: AgentProtocol) -> None:
        """Register an agent implementation."""
        self.agents[agent_type] = agent
        logger.info(f"Registered agent: {agent_type.value}")

    def register_workflow(
        self, workflow_id: str, workflow: "WorkflowDefinition"
    ) -> None:
        """Register a workflow definition."""
        self.workflows[workflow_id] = workflow
        logger.info(f"Registered workflow: {workflow_id}")

    async def execute_workflow(
        self, workflow_id: str, input_data: Dict[str, Any], context: WorkflowContext
    ) -> WorkflowResult:
        """Execute a workflow with full observability and state management."""
        start_time = time.time()

        try:
            # Validate workflow exists
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")

            workflow = self.workflows[workflow_id]

            # Initialize workflow state
            state = WorkflowState(
                workflow_id=workflow_id,
                status=WorkflowStatus.PENDING,
                timeout_at=context.created_at
                + timedelta(seconds=context.timeout_seconds),
            )

            # Store initial state
            await self.state_store.save_state(context.workflow_id, state)

            # Start observability tracking
            await self.observability.start_workflow_trace(context, workflow)

            # Execute workflow
            result = await self._execute_workflow_steps(
                workflow, input_data, context, state
            )

            # Update final state
            state.status = WorkflowStatus.COMPLETED
            state.updated_at = datetime.now(timezone.utc)
            await self.state_store.save_state(context.workflow_id, state)

            # End observability tracking
            await self.observability.end_workflow_trace(context, result)

            return result

        except Exception as e:
            logger.error(
                f"Workflow execution failed: {e}",
                workflow_id=workflow_id,
                trace_id=context.trace_id,
            )

            # Update state with error
            state = await self.state_store.get_state(context.workflow_id)
            if state:
                state.status = WorkflowStatus.FAILED
                state.error = str(e)
                state.updated_at = datetime.now(timezone.utc)
                await self.state_store.save_state(context.workflow_id, state)

            # Record error in observability
            await self.observability.record_error(context, e)

            return WorkflowResult(
                workflow_id=workflow_id,
                status=WorkflowStatus.FAILED,
                steps_results={},
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
            )

    async def _execute_workflow_steps(
        self,
        workflow: "WorkflowDefinition",
        input_data: Dict[str, Any],
        context: WorkflowContext,
        state: WorkflowState,
    ) -> WorkflowResult:
        """Execute workflow steps with dependency resolution."""
        step_results = {}
        current_data = input_data.copy()

        # Execute steps in dependency order
        for step in workflow.get_execution_order():
            try:
                # Check timeout
                if state.timeout_at and datetime.now(timezone.utc) > state.timeout_at:
                    raise TimeoutError("Workflow execution timed out")

                # Update state
                state.current_step = step.step_id
                state.status = WorkflowStatus.RUNNING
                await self.state_store.save_state(context.workflow_id, state)

                # Execute step with circuit breaker
                step_result = await self._execute_step_with_circuit_breaker(
                    step, current_data, context
                )

                step_results[step.step_id] = step_result
                state.completed_steps.append(step.step_id)
                state.step_results[step.step_id] = step_result

                # Update data for next step
                current_data.update(step_result.get("output", {}))

                # Record step completion
                await self.observability.record_step_completion(
                    context, step, step_result
                )

            except Exception as e:
                logger.error(f"Step {step.step_id} failed: {e}")
                state.failed_steps.append(step.step_id)
                state.error = str(e)

                # Handle step failure
                if step.fallback_enabled:
                    step_result = await self._execute_fallback(
                        step, current_data, context
                    )
                    step_results[step.step_id] = step_result
                else:
                    raise e

        # Generate final result
        final_result = await workflow.generate_final_result(step_results, context)

        return WorkflowResult(
            workflow_id=workflow.workflow_id,
            status=WorkflowStatus.COMPLETED,
            steps_results=step_results,
            final_result=final_result,
            execution_time_ms=int(
                (time.time() - context.created_at.timestamp()) * 1000
            ),
        )

    async def _execute_step_with_circuit_breaker(
        self, step: WorkflowStep, input_data: Dict[str, Any], context: WorkflowContext
    ) -> Dict[str, Any]:
        """Execute step with circuit breaker protection."""
        if not step.circuit_breaker_enabled:
            return await self._execute_step(step, input_data, context)

        async with self.circuit_breaker.get_circuit(step.agent_type.value):
            return await self._execute_step_with_retry(step, input_data, context)

    async def _execute_step_with_retry(
        self, step: WorkflowStep, input_data: Dict[str, Any], context: WorkflowContext
    ) -> Dict[str, Any]:
        """Execute step with retry logic."""
        last_exception = None

        for attempt in range(step.retry_count + 1):
            try:
                return await self._execute_step(step, input_data, context)
            except Exception as e:
                last_exception = e
                if attempt < step.retry_count:
                    await asyncio.sleep(step.retry_delay_seconds * (attempt + 1))
                    logger.warning(
                        f"Step {step.step_id} attempt {attempt + 1} failed, retrying"
                    )

        raise last_exception

    async def _execute_step(
        self, step: WorkflowStep, input_data: Dict[str, Any], context: WorkflowContext
    ) -> Dict[str, Any]:
        """Execute a single workflow step."""
        if step.agent_type not in self.agents:
            raise ValueError(f"Agent {step.agent_type.value} not registered")

        agent = self.agents[step.agent_type]

        # Prepare task data
        task_data = {
            **input_data,
            **step.metadata,
            "step_id": step.step_id,
            "timeout_seconds": step.timeout_seconds,
        }

        # Execute with timeout
        try:
            result = await asyncio.wait_for(
                agent.process_task(task_data, context), timeout=step.timeout_seconds
            )

            return {
                "success": True,
                "output": result,
                "step_id": step.step_id,
                "agent_type": step.agent_type.value,
                "execution_time_ms": 0,  # Would be calculated in practice
            }

        except asyncio.TimeoutError:
            raise TimeoutError(
                f"Step {step.step_id} timed out after {step.timeout_seconds}s"
            )

    async def _execute_fallback(
        self, step: WorkflowStep, input_data: Dict[str, Any], context: WorkflowContext
    ) -> Dict[str, Any]:
        """Execute fallback logic for failed step."""
        logger.warning(f"Executing fallback for step {step.step_id}")

        # Simple fallback - return empty result
        return {
            "success": False,
            "output": {},
            "step_id": step.step_id,
            "agent_type": step.agent_type.value,
            "fallback_used": True,
            "error": "Step failed, using fallback",
        }


class WorkflowDefinition:
    """Workflow definition with dependency management."""

    def __init__(self, workflow_id: str, name: str):
        self.workflow_id = workflow_id
        self.name = name
        self.steps: List[WorkflowStep] = []
        self.step_map: Dict[str, WorkflowStep] = {}

    def add_step(
        self,
        step_id: str,
        agent_type: AgentType,
        name: str,
        dependencies: Optional[List[str]] = None,
        **kwargs,
    ) -> "WorkflowDefinition":
        """Add a step to the workflow."""
        step = WorkflowStep(
            step_id=step_id,
            agent_type=agent_type,
            name=name,
            dependencies=dependencies or [],
            **kwargs,
        )

        self.steps.append(step)
        self.step_map[step_id] = step
        return self

    def get_execution_order(self) -> List[WorkflowStep]:
        """Get steps in dependency order using topological sort."""
        # Build dependency graph
        graph = {step.step_id: step.dependencies for step in self.steps}

        # Topological sort
        visited = set()
        temp_visited = set()
        order = []

        def visit(step_id: str):
            if step_id in temp_visited:
                raise ValueError(f"Circular dependency detected: {step_id}")
            if step_id in visited:
                return

            temp_visited.add(step_id)

            for dep in graph.get(step_id, []):
                visit(dep)

            temp_visited.remove(step_id)
            visited.add(step_id)
            order.append(self.step_map[step_id])

        for step in self.steps:
            if step.step_id not in visited:
                visit(step.step_id)

        return order

    async def generate_final_result(
        self, step_results: Dict[str, Any], context: WorkflowContext
    ) -> Dict[str, Any]:
        """Generate final result from step results."""
        # Default implementation - combine all outputs
        final_output = {}

        for step_id, result in step_results.items():
            if result.get("success", False):
                final_output.update(result.get("output", {}))

        return final_output


class StateStore(Protocol):
    """Protocol for state storage."""

    async def save_state(self, workflow_id: str, state: WorkflowState) -> None:
        """Save workflow state."""
        ...

    async def get_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get workflow state."""
        ...

    async def delete_state(self, workflow_id: str) -> None:
        """Delete workflow state."""
        ...


class InMemoryStateStore:
    """In-memory state store for development."""

    def __init__(self):
        self.states: Dict[str, WorkflowState] = {}

    async def save_state(self, workflow_id: str, state: WorkflowState) -> None:
        """Save workflow state."""
        self.states[workflow_id] = state

    async def get_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get workflow state."""
        return self.states.get(workflow_id)

    async def delete_state(self, workflow_id: str) -> None:
        """Delete workflow state."""
        self.states.pop(workflow_id, None)


class ObservabilityManager:
    """Comprehensive observability and tracing."""

    def __init__(self):
        self.traces: Dict[str, Dict[str, Any]] = {}
        self.metrics = {}

    async def start_workflow_trace(
        self, context: WorkflowContext, workflow: WorkflowDefinition
    ) -> None:
        """Start tracing for workflow execution."""
        trace = {
            "workflow_id": workflow.workflow_id,
            "trace_id": context.trace_id,
            "user_id": context.user_id,
            "start_time": datetime.now(timezone.utc),
            "steps": [],
            "metadata": context.metadata,
        }

        self.traces[context.trace_id] = trace
        logger.info(f"Started workflow trace", trace_id=context.trace_id)

    async def record_step_completion(
        self, context: WorkflowContext, step: WorkflowStep, result: Dict[str, Any]
    ) -> None:
        """Record step completion."""
        if context.trace_id in self.traces:
            self.traces[context.trace_id]["steps"].append(
                {
                    "step_id": step.step_id,
                    "agent_type": step.agent_type.value,
                    "success": result.get("success", False),
                    "execution_time_ms": result.get("execution_time_ms", 0),
                    "timestamp": datetime.now(timezone.utc),
                }
            )

    async def end_workflow_trace(
        self, context: WorkflowContext, result: WorkflowResult
    ) -> None:
        """End workflow tracing."""
        if context.trace_id in self.traces:
            trace = self.traces[context.trace_id]
            trace["end_time"] = datetime.now(timezone.utc)
            trace["status"] = result.status.value
            trace["execution_time_ms"] = result.execution_time_ms

            logger.info(
                f"Completed workflow trace",
                trace_id=context.trace_id,
                status=result.status.value,
                execution_time_ms=result.execution_time_ms,
            )

    async def record_error(self, context: WorkflowContext, error: Exception) -> None:
        """Record error in trace."""
        if context.trace_id in self.traces:
            self.traces[context.trace_id]["error"] = {
                "message": str(error),
                "type": type(error).__name__,
                "timestamp": datetime.now(timezone.utc),
            }

    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get trace by ID."""
        return self.traces.get(trace_id)


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance."""

    def __init__(self):
        self.circuits: Dict[str, "Circuit"] = {}

    @asynccontextmanager
    async def get_circuit(self, circuit_id: str):
        """Get circuit breaker context."""
        if circuit_id not in self.circuits:
            self.circuits[circuit_id] = Circuit()

        circuit = self.circuits[circuit_id]

        try:
            await circuit.call()
            yield
        except Exception as e:
            circuit.record_failure()
            raise
        else:
            circuit.record_success()


class Circuit:
    """Individual circuit breaker."""

    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self):
        """Check if circuit is open."""
        if self.state == "OPEN":
            if (
                datetime.now(timezone.utc) - self.last_failure_time
            ).seconds > self.timeout_seconds:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")

    def record_success(self):
        """Record successful call."""
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            self.failure_count = 0

    def record_failure(self):
        """Record failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now(timezone.utc)

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


# Predefined workflow patterns
class WorkflowPatterns:
    """Common workflow patterns for different use cases."""

    @staticmethod
    def create_retrieval_synthesis_workflow() -> WorkflowDefinition:
        """Create retrieval + synthesis workflow."""
        workflow = WorkflowDefinition("retrieval_synthesis", "Retrieval and Synthesis")

        workflow.add_step(
            step_id="retrieval",
            agent_type=AgentType.RETRIEVAL,
            name="Document Retrieval",
            timeout_seconds=30,
            retry_count=2,
        ).add_step(
            step_id="synthesis",
            agent_type=AgentType.SYNTHESIS,
            name="Answer Synthesis",
            dependencies=["retrieval"],
            timeout_seconds=45,
            retry_count=1,
        )

        return workflow

    @staticmethod
    def create_comprehensive_workflow() -> WorkflowDefinition:
        """Create comprehensive workflow with all agents."""
        workflow = WorkflowDefinition("comprehensive", "Comprehensive Analysis")

        workflow.add_step(
            step_id="retrieval",
            agent_type=AgentType.RETRIEVAL,
            name="Document Retrieval",
            timeout_seconds=30,
        ).add_step(
            step_id="fact_check",
            agent_type=AgentType.FACT_CHECK,
            name="Fact Checking",
            dependencies=["retrieval"],
            timeout_seconds=40,
        ).add_step(
            step_id="synthesis",
            agent_type=AgentType.SYNTHESIS,
            name="Answer Synthesis",
            dependencies=["fact_check"],
            timeout_seconds=45,
        ).add_step(
            step_id="citation",
            agent_type=AgentType.CITATION,
            name="Citation Generation",
            dependencies=["synthesis", "retrieval"],
            timeout_seconds=20,
        )

        return workflow

    @staticmethod
    def create_parallel_workflow() -> WorkflowDefinition:
        """Create workflow with parallel execution."""
        workflow = WorkflowDefinition("parallel", "Parallel Processing")

        # Parallel retrieval steps
        workflow.add_step(
            step_id="vector_retrieval",
            agent_type=AgentType.RETRIEVAL,
            name="Vector Search",
            timeout_seconds=25,
        ).add_step(
            step_id="keyword_retrieval",
            agent_type=AgentType.RETRIEVAL,
            name="Keyword Search",
            timeout_seconds=25,
        ).add_step(
            step_id="merge_results",
            agent_type=AgentType.ROUTER,
            name="Result Merging",
            dependencies=["vector_retrieval", "keyword_retrieval"],
            timeout_seconds=15,
        ).add_step(
            step_id="synthesis",
            agent_type=AgentType.SYNTHESIS,
            name="Answer Synthesis",
            dependencies=["merge_results"],
            timeout_seconds=45,
        )

        return workflow


# Export main classes
__all__ = [
    "WorkflowEngine",
    "WorkflowDefinition",
    "WorkflowContext",
    "WorkflowResult",
    "WorkflowState",
    "WorkflowStatus",
    "AgentType",
    "WorkflowStep",
    "ObservabilityManager",
    "CircuitBreaker",
    "WorkflowPatterns",
    "StateStore",
    "InMemoryStateStore",
]
