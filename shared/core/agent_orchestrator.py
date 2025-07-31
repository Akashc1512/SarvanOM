"""
Agent Orchestrator - Universal Knowledge Platform
Enterprise-grade agent coordination with advanced patterns and observability.

Features:
- Advanced agent coordination patterns
- Stateful agent communication
- Performance optimization and caching
- Circuit breaker and retry patterns
- Event-driven agent interactions
- Comprehensive monitoring and tracing

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

from pydantic import BaseModel, Field
import structlog

from .orchestration import (
    WorkflowEngine,
    WorkflowContext,
    WorkflowResult,
    WorkflowStatus,
    AgentType,
    WorkflowStep,
)

logger = structlog.get_logger(__name__)


class AgentProtocol(Protocol):
    """Protocol for agent implementations."""

    async def process_task(
        self, task_data: Dict[str, Any], context: WorkflowContext
    ) -> Dict[str, Any]:
        """Process a task and return results."""
        ...


class AgentState(Enum):
    """Agent execution states."""

    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class AgentInfo:
    """Agent information and capabilities."""

    agent_type: AgentType
    name: str
    version: str
    capabilities: List[str]
    max_concurrent_tasks: int = 5
    timeout_seconds: int = 30
    retry_count: int = 3
    circuit_breaker_enabled: bool = True
    fallback_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentTask:
    """Agent task with context and metadata."""

    task_id: str
    agent_type: AgentType
    task_data: Dict[str, Any]
    context: WorkflowContext
    priority: int = 1
    timeout_seconds: int = 30
    retry_count: int = 3
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    dependencies: List[str] = field(default_factory=list)


@dataclass
class AgentResult:
    """Agent execution result."""

    task_id: str
    agent_type: AgentType
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    execution_time_ms: int = 0
    token_usage: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentOrchestrator:
    """Enterprise agent orchestrator with advanced coordination patterns."""

    def __init__(
        self,
        workflow_engine: WorkflowEngine,
        max_concurrent_agents: int = 10,
        enable_caching: bool = True,
        enable_monitoring: bool = True,
    ):
        self.workflow_engine = workflow_engine
        self.max_concurrent_agents = max_concurrent_agents
        self.enable_caching = enable_caching
        self.enable_monitoring = enable_monitoring

        # Agent registry
        self.agents: Dict[AgentType, AgentProtocol] = {}
        self.agent_info: Dict[AgentType, AgentInfo] = {}

        # Task management
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.active_tasks: Dict[str, AgentTask] = {}
        self.completed_tasks: Dict[str, AgentResult] = {}

        # Performance tracking
        self.agent_metrics: Dict[AgentType, Dict[str, Any]] = {}
        self.circuit_breakers: Dict[AgentType, "CircuitBreaker"] = {}

        # Caching
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes

        # Monitoring
        self.monitoring = AgentMonitoring() if enable_monitoring else None

        # Start task processor
        self._task_processor = asyncio.create_task(self._process_tasks())

    def register_agent(
        self, agent_type: AgentType, agent: AgentProtocol, info: AgentInfo
    ) -> None:
        """Register an agent with capabilities."""
        self.agents[agent_type] = agent
        self.agent_info[agent_type] = info

        # Initialize metrics
        self.agent_metrics[agent_type] = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "average_execution_time_ms": 0,
            "active_tasks": 0,
            "last_execution": None,
        }

        # Initialize circuit breaker
        if info.circuit_breaker_enabled:
            self.circuit_breakers[agent_type] = CircuitBreaker()

        logger.info(f"Registered agent: {agent_type.value}", info=info)

    async def execute_agent_task(
        self,
        agent_type: AgentType,
        task_data: Dict[str, Any],
        context: WorkflowContext,
        priority: int = 1,
        timeout_seconds: Optional[int] = None,
        cache_key: Optional[str] = None,
    ) -> AgentResult:
        """Execute a single agent task with full orchestration."""

        # Check if agent is registered
        if agent_type not in self.agents:
            raise ValueError(f"Agent {agent_type.value} not registered")

        # Check cache first
        if self.enable_caching and cache_key:
            cached_result = await self._get_cached_result(cache_key)
            if cached_result:
                logger.info(f"Cache hit for agent task: {agent_type.value}")
                return cached_result

        # Create task
        task = AgentTask(
            task_id=str(uuid.uuid4()),
            agent_type=agent_type,
            task_data=task_data,
            context=context,
            priority=priority,
            timeout_seconds=timeout_seconds
            or self.agent_info[agent_type].timeout_seconds,
        )

        # Add to queue
        await self.task_queue.put((priority, task))

        # Wait for completion
        result = await self._wait_for_task_completion(task.task_id)

        # Cache result if successful
        if self.enable_caching and cache_key and result.success:
            await self._cache_result(cache_key, result)

        return result

    async def execute_agent_pipeline(
        self,
        pipeline: List[Dict[str, Any]],
        context: WorkflowContext,
        execution_strategy: str = "sequential",
    ) -> Dict[str, AgentResult]:
        """Execute a pipeline of agent tasks."""

        if execution_strategy == "sequential":
            return await self._execute_sequential_pipeline(pipeline, context)
        elif execution_strategy == "parallel":
            return await self._execute_parallel_pipeline(pipeline, context)
        elif execution_strategy == "conditional":
            return await self._execute_conditional_pipeline(pipeline, context)
        else:
            raise ValueError(f"Unknown execution strategy: {execution_strategy}")

    async def _execute_sequential_pipeline(
        self, pipeline: List[Dict[str, Any]], context: WorkflowContext
    ) -> Dict[str, AgentResult]:
        """Execute pipeline sequentially with data flow."""
        results = {}
        current_data = {}

        for step_config in pipeline:
            agent_type = AgentType(step_config["agent_type"])
            task_data = {**step_config.get("task_data", {}), **current_data}

            # Execute task
            result = await self.execute_agent_task(
                agent_type=agent_type,
                task_data=task_data,
                context=context,
                priority=step_config.get("priority", 1),
                timeout_seconds=step_config.get("timeout_seconds"),
            )

            results[step_config["step_id"]] = result

            # Update data for next step
            if result.success:
                current_data.update(result.data)

        return results

    async def _execute_parallel_pipeline(
        self, pipeline: List[Dict[str, Any]], context: WorkflowContext
    ) -> Dict[str, AgentResult]:
        """Execute pipeline in parallel where possible."""
        # Group tasks by dependencies
        task_groups = self._group_tasks_by_dependencies(pipeline)

        results = {}

        for group in task_groups:
            # Execute group in parallel
            tasks = []
            for step_config in group:
                agent_type = AgentType(step_config["agent_type"])
                task_data = step_config.get("task_data", {})

                task = self.execute_agent_task(
                    agent_type=agent_type,
                    task_data=task_data,
                    context=context,
                    priority=step_config.get("priority", 1),
                    timeout_seconds=step_config.get("timeout_seconds"),
                )
                tasks.append((step_config["step_id"], task))

            # Wait for all tasks in group
            group_results = await asyncio.gather(*[task for _, task in tasks])

            # Store results
            for (step_id, _), result in zip(tasks, group_results):
                results[step_id] = result

        return results

    async def _execute_conditional_pipeline(
        self, pipeline: List[Dict[str, Any]], context: WorkflowContext
    ) -> Dict[str, AgentResult]:
        """Execute pipeline with conditional branching."""
        results = {}
        current_data = {}

        for step_config in pipeline:
            # Check condition
            condition = step_config.get("condition")
            if condition and not self._evaluate_condition(condition, current_data):
                logger.info(f"Skipping step {step_config['step_id']} due to condition")
                continue

            agent_type = AgentType(step_config["agent_type"])
            task_data = {**step_config.get("task_data", {}), **current_data}

            # Execute task
            result = await self.execute_agent_task(
                agent_type=agent_type,
                task_data=task_data,
                context=context,
                priority=step_config.get("priority", 1),
                timeout_seconds=step_config.get("timeout_seconds"),
            )

            results[step_config["step_id"]] = result

            # Update data for next step
            if result.success:
                current_data.update(result.data)

        return results

    def _group_tasks_by_dependencies(
        self, pipeline: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """Group tasks by dependencies for parallel execution."""
        # Simple implementation - group tasks without dependencies together
        groups = []
        current_group = []

        for step_config in pipeline:
            dependencies = step_config.get("dependencies", [])

            if not dependencies:
                current_group.append(step_config)
            else:
                if current_group:
                    groups.append(current_group)
                    current_group = []
                groups.append([step_config])

        if current_group:
            groups.append(current_group)

        return groups

    def _evaluate_condition(
        self, condition: Dict[str, Any], data: Dict[str, Any]
    ) -> bool:
        """Evaluate condition for conditional execution."""
        condition_type = condition.get("type", "field_exists")

        if condition_type == "field_exists":
            field_path = condition.get("field")
            return self._get_nested_value(data, field_path) is not None
        elif condition_type == "field_value":
            field_path = condition.get("field")
            expected_value = condition.get("value")
            actual_value = self._get_nested_value(data, field_path)
            return actual_value == expected_value
        elif condition_type == "custom":
            # Custom condition evaluation
            return condition.get("evaluate", lambda x: True)(data)
        else:
            return True

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get nested value from dictionary."""
        keys = path.split(".")
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current

    async def _process_tasks(self) -> None:
        """Background task processor."""
        while True:
            try:
                # Get next task
                priority, task = await self.task_queue.get()

                # Execute task
                result = await self._execute_task(task)

                # Store result
                self.completed_tasks[task.task_id] = result

                # Update metrics
                self._update_agent_metrics(task.agent_type, result)

                # Record in monitoring
                if self.monitoring:
                    await self.monitoring.record_task_execution(task, result)

                # Mark task as done
                self.task_queue.task_done()

            except Exception as e:
                logger.error(f"Task processing error: {e}")
                await asyncio.sleep(1)  # Prevent tight loop on errors

    async def _execute_task(self, task: AgentTask) -> AgentResult:
        """Execute a single agent task."""
        start_time = time.time()

        try:
            # Update active tasks
            self.active_tasks[task.task_id] = task
            self.agent_metrics[task.agent_type]["active_tasks"] += 1

            # Get agent
            agent = self.agents[task.agent_type]
            agent_info = self.agent_info[task.agent_type]

            # Execute with circuit breaker if enabled
            if agent_info.circuit_breaker_enabled:
                circuit_breaker = self.circuit_breakers[task.agent_type]
                async with circuit_breaker.get_circuit():
                    result_data = await self._execute_with_retry(
                        agent, task, agent_info.retry_count
                    )
            else:
                result_data = await self._execute_with_retry(
                    agent, task, agent_info.retry_count
                )

            execution_time_ms = int((time.time() - start_time) * 1000)

            return AgentResult(
                task_id=task.task_id,
                agent_type=task.agent_type,
                success=True,
                data=result_data,
                execution_time_ms=execution_time_ms,
            )

        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)

            # Handle fallback if enabled
            if self.agent_info[task.agent_type].fallback_enabled:
                fallback_data = await self._execute_fallback(task)
                return AgentResult(
                    task_id=task.task_id,
                    agent_type=task.agent_type,
                    success=False,
                    data=fallback_data,
                    error=str(e),
                    execution_time_ms=execution_time_ms,
                    metadata={"fallback_used": True},
                )
            else:
                return AgentResult(
                    task_id=task.task_id,
                    agent_type=task.agent_type,
                    success=False,
                    data={},
                    error=str(e),
                    execution_time_ms=execution_time_ms,
                )
        finally:
            # Clean up
            self.active_tasks.pop(task.task_id, None)
            self.agent_metrics[task.agent_type]["active_tasks"] -= 1

    async def _execute_with_retry(
        self, agent: AgentProtocol, task: AgentTask, max_retries: int
    ) -> Dict[str, Any]:
        """Execute agent task with retry logic."""
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                return await asyncio.wait_for(
                    agent.process_task(task.task_data, task.context),
                    timeout=task.timeout_seconds,
                )
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    await asyncio.sleep(2**attempt)  # Exponential backoff
                    logger.warning(f"Agent task retry {attempt + 1}/{max_retries}: {e}")

        raise last_exception

    async def _execute_fallback(self, task: AgentTask) -> Dict[str, Any]:
        """Execute fallback logic for failed task."""
        logger.warning(f"Executing fallback for task {task.task_id}")

        # Simple fallback - return empty result
        return {
            "fallback_used": True,
            "original_task_id": task.task_id,
            "error": "Task failed, using fallback",
        }

    async def _wait_for_task_completion(self, task_id: str) -> AgentResult:
        """Wait for task completion."""
        while task_id not in self.completed_tasks:
            await asyncio.sleep(0.1)

        return self.completed_tasks[task_id]

    async def _get_cached_result(self, cache_key: str) -> Optional[AgentResult]:
        """Get cached result."""
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now(timezone.utc) < cached_data["expires_at"]:
                return cached_data["result"]
            else:
                del self.cache[cache_key]
        return None

    async def _cache_result(self, cache_key: str, result: AgentResult) -> None:
        """Cache agent result."""
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.cache_ttl)
        self.cache[cache_key] = {"result": result, "expires_at": expires_at}

    def _update_agent_metrics(self, agent_type: AgentType, result: AgentResult) -> None:
        """Update agent performance metrics."""
        metrics = self.agent_metrics[agent_type]
        metrics["total_tasks"] += 1

        if result.success:
            metrics["successful_tasks"] += 1
        else:
            metrics["failed_tasks"] += 1

        metrics["last_execution"] = datetime.now(timezone.utc)

        # Update average execution time
        current_avg = metrics["average_execution_time_ms"]
        total_tasks = metrics["total_tasks"]
        new_avg = (
            (current_avg * (total_tasks - 1)) + result.execution_time_ms
        ) / total_tasks
        metrics["average_execution_time_ms"] = int(new_avg)

    async def get_agent_metrics(
        self, agent_type: Optional[AgentType] = None
    ) -> Dict[str, Any]:
        """Get agent performance metrics."""
        if agent_type:
            return self.agent_metrics.get(agent_type, {})
        return self.agent_metrics

    async def get_agent_status(self, agent_type: AgentType) -> Dict[str, Any]:
        """Get agent status and health."""
        if agent_type not in self.agents:
            return {"status": "not_registered"}

        metrics = self.agent_metrics.get(agent_type, {})
        active_tasks = metrics.get("active_tasks", 0)

        if active_tasks > 0:
            status = AgentState.BUSY
        elif metrics.get("failed_tasks", 0) > metrics.get("total_tasks", 0) * 0.5:
            status = AgentState.ERROR
        else:
            status = AgentState.IDLE

        return {
            "status": status.value,
            "metrics": metrics,
            "info": self.agent_info.get(agent_type),
        }

    async def shutdown(self) -> None:
        """Shutdown orchestrator gracefully."""
        logger.info("Shutting down agent orchestrator")

        # Cancel task processor
        self._task_processor.cancel()

        # Wait for active tasks to complete
        while self.active_tasks:
            await asyncio.sleep(0.1)


class CircuitBreaker:
    """Circuit breaker for agent fault tolerance."""

    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    @asynccontextmanager
    async def get_circuit(self):
        """Get circuit breaker context."""
        if self.state == "OPEN":
            if (
                datetime.now(timezone.utc) - self.last_failure_time
            ).seconds > self.timeout_seconds:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            yield
        except Exception as e:
            self.record_failure()
            raise
        else:
            self.record_success()

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


class AgentMonitoring:
    """Agent monitoring and alerting."""

    def __init__(self):
        self.alerts: List[Dict[str, Any]] = []
        self.thresholds = {
            "execution_time_ms": 30000,  # 30 seconds
            "error_rate": 0.2,  # 20%
            "success_rate": 0.8,  # 80%
        }

    async def record_task_execution(self, task: AgentTask, result: AgentResult) -> None:
        """Record task execution for monitoring."""
        # Check for performance alerts
        if result.execution_time_ms > self.thresholds["execution_time_ms"]:
            await self._create_alert(
                "SLOW_AGENT_EXECUTION",
                f"Agent {task.agent_type.value} took {result.execution_time_ms}ms",
                task,
                result,
            )

        # Check for error alerts
        if not result.success:
            await self._create_alert(
                "AGENT_EXECUTION_ERROR",
                f"Agent {task.agent_type.value} failed: {result.error}",
                task,
                result,
            )

    async def _create_alert(
        self, alert_type: str, message: str, task: AgentTask, result: AgentResult
    ) -> None:
        """Create monitoring alert."""
        alert = {
            "alert_id": str(uuid.uuid4()),
            "alert_type": alert_type,
            "message": message,
            "task_id": task.task_id,
            "agent_type": task.agent_type.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": "WARNING" if alert_type == "SLOW_AGENT_EXECUTION" else "ERROR",
        }

        self.alerts.append(alert)
        logger.warning(f"Agent alert: {message}", alert=alert)

    def get_alerts(
        self, alert_type: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get monitoring alerts."""
        alerts = self.alerts

        if alert_type:
            alerts = [a for a in alerts if a["alert_type"] == alert_type]

        # Sort by timestamp (newest first)
        alerts.sort(key=lambda a: a["timestamp"], reverse=True)

        return alerts[:limit]


# Export main classes
__all__ = [
    "AgentOrchestrator",
    "AgentProtocol",
    "AgentInfo",
    "AgentTask",
    "AgentResult",
    "AgentState",
    "CircuitBreaker",
    "AgentMonitoring",
]
