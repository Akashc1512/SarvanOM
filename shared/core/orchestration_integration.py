"""
Orchestration Integration - Universal Knowledge Platform
Unified enterprise orchestration system integrating all components.

Features:
- Unified orchestration interface
- Multi-pattern execution support
- Advanced monitoring and observability
- Performance optimization
- Enterprise-grade reliability
- Comprehensive debugging tools

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
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
from .workflow_manager import WorkflowManager, WorkflowTemplate, WorkflowExecution
from .agent_orchestrator import AgentOrchestrator, AgentInfo, AgentTask, AgentResult
from .langchain_integration import (
    LangChainOrchestrator,
    LangChainAgentConfig,
    WorkflowState,
)
from .event_driven_orchestration import (
    EventBus,
    EventDrivenWorkflowEngine,
    EventDrivenWorkflow,
    WorkflowEvent,
    EventType,
)

logger = structlog.get_logger(__name__)


class OrchestrationPattern(Enum):
    """Orchestration patterns."""

    TRADITIONAL = "traditional"
    EVENT_DRIVEN = "event_driven"
    LANGCHAIN = "langchain"
    HYBRID = "hybrid"


class ExecutionMode(Enum):
    """Execution modes."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    STREAMING = "streaming"


@dataclass
class OrchestrationConfig:
    """Configuration for orchestration system."""

    pattern: OrchestrationPattern = OrchestrationPattern.TRADITIONAL
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    enable_caching: bool = True
    enable_monitoring: bool = True
    enable_event_sourcing: bool = True
    max_concurrent_workflows: int = 100
    max_concurrent_agents: int = 50
    timeout_seconds: int = 300
    retry_count: int = 3
    circuit_breaker_enabled: bool = True


class UnifiedOrchestrator:
    """Unified orchestration system integrating all patterns."""

    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.event_bus = EventBus()

        # Initialize orchestration components
        self.workflow_engine = WorkflowEngine()
        self.workflow_manager = WorkflowManager(self.workflow_engine)
        self.agent_orchestrator = AgentOrchestrator(
            self.workflow_engine,
            max_concurrent_agents=config.max_concurrent_agents,
            enable_caching=config.enable_caching,
            enable_monitoring=config.enable_monitoring,
        )

        # Initialize LangChain orchestrator if available
        self.langchain_orchestrator = None
        try:
            from .langchain_integration import LangChainOrchestrator

            self.langchain_orchestrator = LangChainOrchestrator()
        except ImportError:
            logger.warning("LangChain not available")

        # Initialize event-driven orchestrator
        self.event_driven_engine = EventDrivenWorkflowEngine(self.event_bus)

        # Performance tracking
        self.performance_metrics = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time_ms": 0,
            "active_executions": 0,
            "cache_hit_rate": 0.0,
            "circuit_breaker_trips": 0,
        }

        # Register event handlers
        asyncio.create_task(self._setup_event_handlers())

        logger.info("Unified Orchestrator initialized", config=config)

    async def _setup_event_handlers(self) -> None:
        """Setup event handlers for monitoring."""
        await self.event_bus.subscribe(
            EventType.WORKFLOW_COMPLETED, self._handle_workflow_completed
        )
        await self.event_bus.subscribe(
            EventType.WORKFLOW_FAILED, self._handle_workflow_failed
        )
        await self.event_bus.subscribe(
            EventType.CIRCUIT_BREAKER_TRIPPED, self._handle_circuit_breaker_tripped
        )

    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        pattern: Optional[OrchestrationPattern] = None,
        mode: Optional[ExecutionMode] = None,
    ) -> Dict[str, Any]:
        """Execute workflow using specified pattern and mode."""
        start_time = time.time()

        # Use default pattern if not specified
        pattern = pattern or self.config.pattern
        mode = mode or self.config.execution_mode

        try:
            # Update metrics
            self.performance_metrics["total_executions"] += 1
            self.performance_metrics["active_executions"] += 1

            # Execute based on pattern
            if pattern == OrchestrationPattern.TRADITIONAL:
                result = await self._execute_traditional_workflow(
                    workflow_id, input_data, context, mode
                )
            elif pattern == OrchestrationPattern.EVENT_DRIVEN:
                result = await self._execute_event_driven_workflow(
                    workflow_id, input_data, context, mode
                )
            elif pattern == OrchestrationPattern.LANGCHAIN:
                result = await self._execute_langchain_workflow(
                    workflow_id, input_data, context, mode
                )
            elif pattern == OrchestrationPattern.HYBRID:
                result = await self._execute_hybrid_workflow(
                    workflow_id, input_data, context, mode
                )
            else:
                raise ValueError(f"Unknown orchestration pattern: {pattern}")

            # Update success metrics
            self.performance_metrics["successful_executions"] += 1

            return result

        except Exception as e:
            # Update failure metrics
            self.performance_metrics["failed_executions"] += 1
            logger.error(f"Workflow execution failed: {e}")
            raise
        finally:
            # Update execution time and active count
            execution_time = int((time.time() - start_time) * 1000)
            self._update_execution_time_metrics(execution_time)
            self.performance_metrics["active_executions"] -= 1

    async def _execute_traditional_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        mode: ExecutionMode,
    ) -> Dict[str, Any]:
        """Execute workflow using traditional orchestration."""
        workflow_context = WorkflowContext(
            workflow_id=workflow_id,
            trace_id=str(uuid.uuid4()),
            user_context=context or {},
            timeout_seconds=self.config.timeout_seconds,
        )

        # Execute workflow
        result = await self.workflow_engine.execute_workflow(
            workflow_id, input_data, workflow_context
        )

        return {
            "pattern": "traditional",
            "mode": mode.value,
            "success": result.status == WorkflowStatus.COMPLETED,
            "result": result.final_result,
            "execution_time_ms": result.execution_time_ms,
            "trace_id": workflow_context.trace_id,
        }

    async def _execute_event_driven_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        mode: ExecutionMode,
    ) -> Dict[str, Any]:
        """Execute workflow using event-driven orchestration."""
        execution_id = await self.event_driven_engine.start_workflow(
            workflow_id, input_data, context or {}
        )

        # Wait for completion
        while True:
            status = self.event_driven_engine.get_workflow_status(execution_id)
            if status and status["state"] in ["completed", "failed"]:
                break
            await asyncio.sleep(0.1)

        return {
            "pattern": "event_driven",
            "mode": mode.value,
            "execution_id": execution_id,
            "success": status["state"] == "completed",
            "result": status.get("result", {}),
            "trace_id": execution_id,
        }

    async def _execute_langchain_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        mode: ExecutionMode,
    ) -> Dict[str, Any]:
        """Execute workflow using LangChain orchestration."""
        if not self.langchain_orchestrator:
            raise RuntimeError("LangChain orchestrator not available")

        result = await self.langchain_orchestrator.execute_workflow(
            workflow_id, input_data, context or {}
        )

        return {
            "pattern": "langchain",
            "mode": mode.value,
            "success": result.get("success", False),
            "result": result.get("result", {}),
            "trace_id": result.get("trace_id", ""),
        }

    async def _execute_hybrid_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        mode: ExecutionMode,
    ) -> Dict[str, Any]:
        """Execute workflow using hybrid orchestration."""
        # Start with traditional orchestration
        traditional_result = await self._execute_traditional_workflow(
            workflow_id, input_data, context, mode
        )

        # Enhance with event-driven monitoring
        if traditional_result["success"]:
            # Publish completion event
            event = WorkflowEvent(
                event_id=str(uuid.uuid4()),
                event_type=EventType.WORKFLOW_COMPLETED,
                timestamp=datetime.now(timezone.utc),
                source="unified_orchestrator",
                data={"workflow_id": workflow_id, "result": traditional_result},
            )
            await self.event_bus.publish(event)

        return traditional_result

    def register_agent(
        self, agent_type: AgentType, agent: Any, info: AgentInfo
    ) -> None:
        """Register an agent with all orchestrators."""
        # Register with traditional orchestrator
        self.workflow_engine.register_agent(agent_type, agent)

        # Register with agent orchestrator
        self.agent_orchestrator.register_agent(agent_type, agent, info)

        # Register with LangChain orchestrator if available
        if self.langchain_orchestrator:
            langchain_config = self._create_langchain_config(agent_type, info)
            self.langchain_orchestrator.register_agent(langchain_config)

        logger.info(f"Registered agent with all orchestrators: {agent_type.value}")

    def _create_langchain_config(
        self, agent_type: AgentType, info: AgentInfo
    ) -> LangChainAgentConfig:
        """Create LangChain agent configuration."""
        return LangChainAgentConfig(
            agent_type=agent_type.value,
            name=info.name,
            description=info.description,
            max_iterations=info.retry_count,
            verbose=info.metadata.get("verbose", False),
        )

    def register_workflow(
        self,
        workflow_id: str,
        workflow: WorkflowDefinition,
        pattern: OrchestrationPattern = OrchestrationPattern.TRADITIONAL,
    ) -> None:
        """Register workflow with appropriate orchestrator."""
        if pattern == OrchestrationPattern.TRADITIONAL:
            self.workflow_engine.register_workflow(workflow_id, workflow)
        elif pattern == OrchestrationPattern.EVENT_DRIVEN:
            event_workflow = self._create_event_workflow(workflow_id, workflow)
            asyncio.create_task(
                self.event_driven_engine.register_workflow(event_workflow)
            )
        elif pattern == OrchestrationPattern.LANGCHAIN:
            if self.langchain_orchestrator:
                langchain_workflow = self._create_langchain_workflow(
                    workflow_id, workflow
                )
                self.langchain_orchestrator.register_workflow(
                    workflow_id, langchain_workflow
                )

        logger.info(f"Registered workflow: {workflow_id} with pattern: {pattern.value}")

    def _create_event_workflow(
        self, workflow_id: str, workflow: WorkflowDefinition
    ) -> EventDrivenWorkflow:
        """Create event-driven workflow from traditional workflow."""
        event_workflow = EventDrivenWorkflow(workflow_id, workflow.name)

        for step in workflow.steps:
            event_workflow.add_step(
                step_id=step.step_id,
                agent_type=step.agent_type.value,
                task_data={},
                dependencies=step.dependencies,
            )

        return event_workflow

    def _create_langchain_workflow(
        self, workflow_id: str, workflow: WorkflowDefinition
    ) -> StateGraph:
        """Create LangGraph workflow from traditional workflow."""
        if not self.langchain_orchestrator:
            raise RuntimeError("LangChain orchestrator not available")

        steps = []
        for step in workflow.steps:
            steps.append(
                {
                    "step_id": step.step_id,
                    "agent_type": step.agent_type.value,
                    "dependencies": step.dependencies,
                }
            )

        return self.langchain_orchestrator.create_workflow_graph(workflow_id, steps)

    async def _handle_workflow_completed(self, event: WorkflowEvent) -> None:
        """Handle workflow completion event."""
        logger.info(f"Workflow completed: {event.data.get('workflow_id', 'unknown')}")

    async def _handle_workflow_failed(self, event: WorkflowEvent) -> None:
        """Handle workflow failure event."""
        logger.error(f"Workflow failed: {event.data.get('workflow_id', 'unknown')}")

    async def _handle_circuit_breaker_tripped(self, event: WorkflowEvent) -> None:
        """Handle circuit breaker trip event."""
        self.performance_metrics["circuit_breaker_trips"] += 1
        logger.warning(f"Circuit breaker tripped: {event.data}")

    def _update_execution_time_metrics(self, new_time_ms: int) -> None:
        """Update execution time metrics."""
        current_avg = self.performance_metrics["average_execution_time_ms"]
        total_executions = self.performance_metrics["total_executions"]

        if total_executions > 0:
            new_avg = (
                (current_avg * (total_executions - 1)) + new_time_ms
            ) / total_executions
            self.performance_metrics["average_execution_time_ms"] = int(new_avg)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        return {
            **self.performance_metrics,
            "success_rate": (
                self.performance_metrics["successful_executions"]
                / max(self.performance_metrics["total_executions"], 1)
                * 100
            ),
            "active_workflows": self.performance_metrics["active_executions"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status."""
        return {
            "status": (
                "healthy"
                if self.performance_metrics["successful_executions"] > 0
                else "degraded"
            ),
            "active_executions": self.performance_metrics["active_executions"],
            "circuit_breaker_trips": self.performance_metrics["circuit_breaker_trips"],
            "cache_hit_rate": self.performance_metrics["cache_hit_rate"],
            "last_execution": datetime.now(timezone.utc).isoformat(),
        }


class OrchestrationMonitor:
    """Advanced monitoring for orchestration system."""

    def __init__(self, orchestrator: UnifiedOrchestrator):
        self.orchestrator = orchestrator
        self.alerts: List[Dict[str, Any]] = []
        self.thresholds = {
            "execution_time_ms": 60000,  # 1 minute
            "error_rate": 0.1,  # 10%
            "success_rate": 0.9,  # 90%
            "active_executions": 80,  # 80% of max
        }

    async def monitor_performance(self) -> None:
        """Monitor orchestration performance."""
        metrics = self.orchestrator.get_performance_metrics()

        # Check execution time
        if metrics["average_execution_time_ms"] > self.thresholds["execution_time_ms"]:
            await self._create_alert(
                "SLOW_EXECUTION",
                f"Average execution time: {metrics['average_execution_time_ms']}ms",
            )

        # Check success rate
        success_rate = metrics["success_rate"]
        if success_rate < self.thresholds["success_rate"] * 100:
            await self._create_alert(
                "LOW_SUCCESS_RATE", f"Success rate: {success_rate:.2f}%"
            )

        # Check active executions
        active_executions = metrics["active_workflows"]
        max_executions = self.orchestrator.config.max_concurrent_workflows
        if (
            active_executions
            > max_executions * self.thresholds["active_executions"] / 100
        ):
            await self._create_alert(
                "HIGH_LOAD", f"Active executions: {active_executions}/{max_executions}"
            )

    async def _create_alert(self, alert_type: str, message: str) -> None:
        """Create monitoring alert."""
        alert = {
            "alert_id": str(uuid.uuid4()),
            "alert_type": alert_type,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": "WARNING" if alert_type in ["SLOW_EXECUTION"] else "ERROR",
        }

        self.alerts.append(alert)
        logger.warning(f"Orchestration alert: {message}", alert=alert)

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


class OrchestrationDebugger:
    """Advanced debugging tools for orchestration."""

    def __init__(self, orchestrator: UnifiedOrchestrator):
        self.orchestrator = orchestrator
        self.debug_sessions: Dict[str, Dict[str, Any]] = {}

    def start_debug_session(self, workflow_id: str) -> str:
        """Start a debug session for a workflow."""
        session_id = str(uuid.uuid4())

        self.debug_sessions[session_id] = {
            "workflow_id": workflow_id,
            "started_at": datetime.now(timezone.utc),
            "events": [],
            "breakpoints": [],
            "state_snapshots": [],
        }

        logger.info(f"Started debug session: {session_id} for workflow: {workflow_id}")
        return session_id

    def add_breakpoint(
        self, session_id: str, step_id: str, condition: Optional[str] = None
    ) -> None:
        """Add a breakpoint to debug session."""
        if session_id in self.debug_sessions:
            self.debug_sessions[session_id]["breakpoints"].append(
                {
                    "step_id": step_id,
                    "condition": condition,
                    "created_at": datetime.now(timezone.utc),
                }
            )

    def capture_state_snapshot(self, session_id: str, state: Dict[str, Any]) -> None:
        """Capture state snapshot for debugging."""
        if session_id in self.debug_sessions:
            self.debug_sessions[session_id]["state_snapshots"].append(
                {"state": state, "timestamp": datetime.now(timezone.utc)}
            )

    def get_debug_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get debug session information."""
        return self.debug_sessions.get(session_id)

    def end_debug_session(self, session_id: str) -> None:
        """End debug session."""
        if session_id in self.debug_sessions:
            session = self.debug_sessions[session_id]
            session["ended_at"] = datetime.now(timezone.utc)
            session["duration"] = (
                session["ended_at"] - session["started_at"]
            ).total_seconds()

            logger.info(
                f"Ended debug session: {session_id}", duration=session["duration"]
            )


# Export main classes
__all__ = [
    "UnifiedOrchestrator",
    "OrchestrationConfig",
    "OrchestrationPattern",
    "ExecutionMode",
    "OrchestrationMonitor",
    "OrchestrationDebugger",
]
