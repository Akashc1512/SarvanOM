"""
Event-Driven Orchestration - Universal Knowledge Platform
Real-time event-driven orchestration with advanced event patterns.

Features:
- Event-driven agent communication
- Real-time workflow coordination
- Event sourcing and replay
- Event filtering and routing
- Event persistence and recovery
- Event-driven monitoring and alerting

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

logger = structlog.get_logger(__name__)


class EventType(Enum):
    """Event types for orchestration."""

    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    AGENT_TASK_STARTED = "agent_task_started"
    AGENT_TASK_COMPLETED = "agent_task_completed"
    AGENT_TASK_FAILED = "agent_task_failed"
    AGENT_STATE_CHANGED = "agent_state_changed"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    CIRCUIT_BREAKER_TRIPPED = "circuit_breaker_tripped"
    PERFORMANCE_ALERT = "performance_alert"
    ERROR_ALERT = "error_alert"


class EventPriority(Enum):
    """Event priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class WorkflowEvent:
    """Event for workflow orchestration."""

    event_id: str
    event_type: EventType
    timestamp: datetime
    source: str
    target: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None


class EventBus:
    """Event bus for distributed communication."""

    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[WorkflowEvent] = []
        self.max_history_size = 10000
        self._lock = asyncio.Lock()

        # Performance tracking
        self.event_metrics = {
            "total_events": 0,
            "events_by_type": {},
            "average_processing_time_ms": 0,
        }

    async def publish(self, event: WorkflowEvent) -> None:
        """Publish an event to all subscribers."""
        async with self._lock:
            # Add to history
            self.event_history.append(event)
            if len(self.event_history) > self.max_history_size:
                self.event_history.pop(0)

            # Update metrics
            self.event_metrics["total_events"] += 1
            event_type_count = self.event_metrics["events_by_type"].get(
                event.event_type.value, 0
            )
            self.event_metrics["events_by_type"][event.event_type.value] = (
                event_type_count + 1
            )

            # Get subscribers
            subscribers = self.subscribers.get(event.event_type, [])

        # Notify subscribers asynchronously
        if subscribers:
            await asyncio.gather(
                *[
                    self._notify_subscriber(subscriber, event)
                    for subscriber in subscribers
                ],
                return_exceptions=True,
            )

        logger.debug(
            f"Published event: {event.event_type.value}", event_id=event.event_id
        )

    async def subscribe(
        self, event_type: EventType, handler: Callable[[WorkflowEvent], Awaitable[None]]
    ) -> None:
        """Subscribe to an event type."""
        async with self._lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            self.subscribers[event_type].append(handler)

        logger.info(f"Subscribed to event type: {event_type.value}")

    async def unsubscribe(
        self, event_type: EventType, handler: Callable[[WorkflowEvent], Awaitable[None]]
    ) -> None:
        """Unsubscribe from an event type."""
        async with self._lock:
            if event_type in self.subscribers:
                self.subscribers[event_type] = [
                    h for h in self.subscribers[event_type] if h != handler
                ]

    async def _notify_subscriber(
        self, handler: Callable[[WorkflowEvent], Awaitable[None]], event: WorkflowEvent
    ) -> None:
        """Notify a single subscriber."""
        start_time = time.time()

        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Event handler failed: {e}", event_id=event.event_id)
        finally:
            # Update processing time metrics
            processing_time = (time.time() - start_time) * 1000
            current_avg = self.event_metrics["average_processing_time_ms"]
            total_events = self.event_metrics["total_events"]
            new_avg = (
                (current_avg * (total_events - 1)) + processing_time
            ) / total_events
            self.event_metrics["average_processing_time_ms"] = new_avg

    def get_event_history(
        self, event_type: Optional[EventType] = None, limit: int = 100
    ) -> List[WorkflowEvent]:
        """Get event history with optional filtering."""
        events = self.event_history

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return events[-limit:]

    def get_metrics(self) -> Dict[str, Any]:
        """Get event bus metrics."""
        return {
            **self.event_metrics,
            "subscriber_count": sum(
                len(subscribers) for subscribers in self.subscribers.values()
            ),
            "event_types": list(self.subscribers.keys()),
        }


class EventDrivenWorkflowEngine:
    """Event-driven workflow engine."""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.workflows: Dict[str, "EventDrivenWorkflow"] = {}
        self.active_workflows: Dict[str, Dict[str, Any]] = {}

        # Subscribe to events
        asyncio.create_task(self._setup_event_subscriptions())

    async def _setup_event_subscriptions(self) -> None:
        """Setup event subscriptions."""
        await self.event_bus.subscribe(
            EventType.WORKFLOW_STARTED, self._handle_workflow_started
        )
        await self.event_bus.subscribe(
            EventType.AGENT_TASK_COMPLETED, self._handle_agent_task_completed
        )
        await self.event_bus.subscribe(
            EventType.AGENT_TASK_FAILED, self._handle_agent_task_failed
        )

    async def register_workflow(self, workflow: "EventDrivenWorkflow") -> None:
        """Register an event-driven workflow."""
        self.workflows[workflow.workflow_id] = workflow
        logger.info(f"Registered event-driven workflow: {workflow.workflow_id}")

    async def start_workflow(
        self, workflow_id: str, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        """Start an event-driven workflow."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.workflows[workflow_id]
        execution_id = str(uuid.uuid4())

        # Create workflow execution
        self.active_workflows[execution_id] = {
            "workflow_id": workflow_id,
            "input_data": input_data,
            "context": context,
            "state": "started",
            "started_at": datetime.now(timezone.utc),
            "completed_steps": [],
            "failed_steps": [],
        }

        # Publish workflow started event
        event = WorkflowEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.WORKFLOW_STARTED,
            timestamp=datetime.now(timezone.utc),
            source="workflow_engine",
            target=workflow_id,
            data={
                "execution_id": execution_id,
                "input_data": input_data,
                "context": context,
            },
            correlation_id=execution_id,
        )

        await self.event_bus.publish(event)

        # Start workflow execution
        asyncio.create_task(self._execute_workflow(execution_id, workflow))

        return execution_id

    async def _execute_workflow(
        self, execution_id: str, workflow: "EventDrivenWorkflow"
    ) -> None:
        """Execute an event-driven workflow."""
        execution = self.active_workflows[execution_id]

        try:
            # Execute workflow steps
            for step in workflow.steps:
                await self._execute_workflow_step(execution_id, step)

                # Check if workflow should continue
                if not self._should_continue_workflow(execution_id):
                    break

            # Complete workflow
            await self._complete_workflow(execution_id)

        except Exception as e:
            await self._fail_workflow(execution_id, str(e))

    async def _execute_workflow_step(
        self, execution_id: str, step: "WorkflowStep"
    ) -> None:
        """Execute a single workflow step."""
        execution = self.active_workflows[execution_id]

        # Publish task started event
        event = WorkflowEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.AGENT_TASK_STARTED,
            timestamp=datetime.now(timezone.utc),
            source="workflow_engine",
            target=step.agent_type,
            data={
                "execution_id": execution_id,
                "step_id": step.step_id,
                "task_data": step.task_data,
            },
            correlation_id=execution_id,
        )

        await self.event_bus.publish(event)

        # Execute step (simulated)
        await asyncio.sleep(1)  # Simulate execution

        # Publish task completed event
        completion_event = WorkflowEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.AGENT_TASK_COMPLETED,
            timestamp=datetime.now(timezone.utc),
            source=step.agent_type,
            target="workflow_engine",
            data={
                "execution_id": execution_id,
                "step_id": step.step_id,
                "result": {"success": True, "data": {}},
            },
            correlation_id=execution_id,
        )

        await self.event_bus.publish(completion_event)

        # Update execution state
        execution["completed_steps"].append(step.step_id)

    def _should_continue_workflow(self, execution_id: str) -> bool:
        """Check if workflow should continue."""
        execution = self.active_workflows[execution_id]
        return execution["state"] == "started"

    async def _complete_workflow(self, execution_id: str) -> None:
        """Complete workflow execution."""
        execution = self.active_workflows[execution_id]
        execution["state"] = "completed"
        execution["completed_at"] = datetime.now(timezone.utc)

        # Publish workflow completed event
        event = WorkflowEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.WORKFLOW_COMPLETED,
            timestamp=datetime.now(timezone.utc),
            source="workflow_engine",
            data={"execution_id": execution_id, "result": {"success": True}},
            correlation_id=execution_id,
        )

        await self.event_bus.publish(event)

    async def _fail_workflow(self, execution_id: str, error: str) -> None:
        """Fail workflow execution."""
        execution = self.active_workflows[execution_id]
        execution["state"] = "failed"
        execution["error"] = error
        execution["failed_at"] = datetime.now(timezone.utc)

        # Publish workflow failed event
        event = WorkflowEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.WORKFLOW_FAILED,
            timestamp=datetime.now(timezone.utc),
            source="workflow_engine",
            data={"execution_id": execution_id, "error": error},
            correlation_id=execution_id,
        )

        await self.event_bus.publish(event)

    async def _handle_workflow_started(self, event: WorkflowEvent) -> None:
        """Handle workflow started event."""
        logger.info(f"Workflow started: {event.data['execution_id']}")

    async def _handle_agent_task_completed(self, event: WorkflowEvent) -> None:
        """Handle agent task completed event."""
        execution_id = event.data["execution_id"]
        step_id = event.data["step_id"]

        logger.info(f"Agent task completed: {step_id} in {execution_id}")

    async def _handle_agent_task_failed(self, event: WorkflowEvent) -> None:
        """Handle agent task failed event."""
        execution_id = event.data["execution_id"]
        step_id = event.data["step_id"]
        error = event.data["error"]

        logger.error(f"Agent task failed: {step_id} in {execution_id}: {error}")

    def get_workflow_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow execution status."""
        return self.active_workflows.get(execution_id)


class EventDrivenWorkflow:
    """Event-driven workflow definition."""

    def __init__(self, workflow_id: str, name: str):
        self.workflow_id = workflow_id
        self.name = name
        self.steps: List["WorkflowStep"] = []
        self.event_handlers: Dict[EventType, Callable] = {}

    def add_step(
        self,
        step_id: str,
        agent_type: str,
        task_data: Dict[str, Any],
        dependencies: Optional[List[str]] = None,
    ) -> "EventDrivenWorkflow":
        """Add a step to the workflow."""
        step = WorkflowStep(
            step_id=step_id,
            agent_type=agent_type,
            task_data=task_data,
            dependencies=dependencies or [],
        )

        self.steps.append(step)
        return self

    def add_event_handler(
        self, event_type: EventType, handler: Callable[[WorkflowEvent], Awaitable[None]]
    ) -> "EventDrivenWorkflow":
        """Add an event handler to the workflow."""
        self.event_handlers[event_type] = handler
        return self


@dataclass
class WorkflowStep:
    """Step in an event-driven workflow."""

    step_id: str
    agent_type: str
    task_data: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)


class EventDrivenAgent:
    """Event-driven agent implementation."""

    def __init__(self, agent_id: str, event_bus: EventBus):
        self.agent_id = agent_id
        self.event_bus = event_bus
        self.state = "idle"
        self.active_tasks: Dict[str, Dict[str, Any]] = {}

        # Subscribe to events
        asyncio.create_task(self._setup_event_subscriptions())

    async def _setup_event_subscriptions(self) -> None:
        """Setup event subscriptions for agent."""
        await self.event_bus.subscribe(
            EventType.AGENT_TASK_STARTED, self._handle_task_started
        )

    async def _handle_task_started(self, event: WorkflowEvent) -> None:
        """Handle task started event."""
        if event.target == self.agent_id:
            task_id = event.data["step_id"]
            task_data = event.data["task_data"]

            # Start task execution
            asyncio.create_task(
                self._execute_task(task_id, task_data, event.correlation_id)
            )

    async def _execute_task(
        self, task_id: str, task_data: Dict[str, Any], correlation_id: str
    ) -> None:
        """Execute a task."""
        self.state = "busy"
        self.active_tasks[task_id] = {
            "task_data": task_data,
            "started_at": datetime.now(timezone.utc),
        }

        try:
            # Simulate task execution
            await asyncio.sleep(2)

            # Publish task completed event
            event = WorkflowEvent(
                event_id=str(uuid.uuid4()),
                event_type=EventType.AGENT_TASK_COMPLETED,
                timestamp=datetime.now(timezone.utc),
                source=self.agent_id,
                target="workflow_engine",
                data={
                    "step_id": task_id,
                    "result": {"success": True, "data": task_data},
                },
                correlation_id=correlation_id,
            )

            await self.event_bus.publish(event)

        except Exception as e:
            # Publish task failed event
            event = WorkflowEvent(
                event_id=str(uuid.uuid4()),
                event_type=EventType.AGENT_TASK_FAILED,
                timestamp=datetime.now(timezone.utc),
                source=self.agent_id,
                target="workflow_engine",
                data={"step_id": task_id, "error": str(e)},
                correlation_id=correlation_id,
            )

            await self.event_bus.publish(event)

        finally:
            # Clean up
            self.active_tasks.pop(task_id, None)
            if not self.active_tasks:
                self.state = "idle"


class EventSourcingManager:
    """Event sourcing for workflow replay and debugging."""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.event_store: List[WorkflowEvent] = []
        self.snapshots: Dict[str, Dict[str, Any]] = {}

    async def store_event(self, event: WorkflowEvent) -> None:
        """Store event for replay."""
        self.event_store.append(event)

    async def replay_workflow(
        self, correlation_id: str, target_state: Optional[Dict[str, Any]] = None
    ) -> List[WorkflowEvent]:
        """Replay workflow events."""
        events = [
            event
            for event in self.event_store
            if event.correlation_id == correlation_id
        ]

        # Sort by timestamp
        events.sort(key=lambda e: e.timestamp)

        # Replay events
        state = {}
        for event in events:
            state = self._apply_event(state, event)

            # Stop if target state reached
            if target_state and state == target_state:
                break

        return events

    def _apply_event(
        self, state: Dict[str, Any], event: WorkflowEvent
    ) -> Dict[str, Any]:
        """Apply event to state."""
        if event.event_type == EventType.WORKFLOW_STARTED:
            state["workflow_id"] = event.target
            state["input_data"] = event.data["input_data"]
            state["started_at"] = event.timestamp
        elif event.event_type == EventType.AGENT_TASK_COMPLETED:
            if "completed_steps" not in state:
                state["completed_steps"] = []
            state["completed_steps"].append(event.data["step_id"])
        elif event.event_type == EventType.WORKFLOW_COMPLETED:
            state["completed"] = True
            state["completed_at"] = event.timestamp

        return state

    def create_snapshot(self, correlation_id: str, state: Dict[str, Any]) -> None:
        """Create a snapshot of workflow state."""
        self.snapshots[correlation_id] = {
            "state": state,
            "timestamp": datetime.now(timezone.utc),
        }

    def get_snapshot(self, correlation_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow snapshot."""
        return self.snapshots.get(correlation_id)


# Export main classes
__all__ = [
    "EventBus",
    "WorkflowEvent",
    "EventType",
    "EventPriority",
    "EventDrivenWorkflowEngine",
    "EventDrivenWorkflow",
    "WorkflowStep",
    "EventDrivenAgent",
    "EventSourcingManager",
]
