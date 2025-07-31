"""
Workflow Manager - Universal Knowledge Platform
Enterprise workflow management with persistence, monitoring, and advanced patterns.

Features:
- Workflow persistence and recovery
- Advanced monitoring and alerting
- Workflow templates and patterns
- Performance optimization
- Distributed execution support
- Workflow versioning and migration

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

from pydantic import BaseModel, Field
import structlog

from .orchestration import (
    WorkflowEngine,
    WorkflowDefinition,
    WorkflowContext,
    WorkflowResult,
    WorkflowState,
    WorkflowStatus,
    AgentType,
)

logger = structlog.get_logger(__name__)


class WorkflowTemplate(BaseModel):
    """Workflow template for reusable patterns."""

    template_id: str
    name: str
    description: str
    version: str = "1.0.0"
    workflow_definition: Dict[str, Any]
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WorkflowExecution(BaseModel):
    """Workflow execution record."""

    execution_id: str
    workflow_id: str
    template_id: Optional[str] = None
    status: WorkflowStatus
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    execution_time_ms: int = 0
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowManager:
    """Enterprise workflow manager with persistence and monitoring."""

    def __init__(
        self,
        workflow_engine: WorkflowEngine,
        state_store: Optional["PersistentStateStore"] = None,
        monitoring: Optional["WorkflowMonitoring"] = None,
    ):
        self.workflow_engine = workflow_engine
        self.state_store = state_store or PersistentStateStore()
        self.monitoring = monitoring or WorkflowMonitoring()
        self.templates: Dict[str, WorkflowTemplate] = {}
        self.executions: Dict[str, WorkflowExecution] = {}

        # Performance tracking
        self.performance_metrics = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time_ms": 0,
            "active_executions": 0,
        }

    def register_template(self, template: WorkflowTemplate) -> None:
        """Register a workflow template."""
        self.templates[template.template_id] = template
        logger.info(f"Registered workflow template: {template.template_id}")

    async def execute_workflow_from_template(
        self,
        template_id: str,
        input_data: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> WorkflowResult:
        """Execute workflow from template with parameter substitution."""

        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")

        template = self.templates[template_id]

        # Create workflow definition from template
        workflow_def = self._create_workflow_from_template(template, parameters or {})

        # Register workflow if not already registered
        workflow_id = f"{template_id}_{uuid.uuid4().hex[:8]}"
        self.workflow_engine.register_workflow(workflow_id, workflow_def)

        # Create execution context
        context = WorkflowContext(
            workflow_id=workflow_id,
            trace_id=str(uuid.uuid4()),
            user_id=user_id,
            session_id=session_id,
            metadata={
                "template_id": template_id,
                "template_version": template.version,
                "parameters": parameters,
            },
        )

        # Record execution start
        execution = WorkflowExecution(
            execution_id=context.workflow_id,
            workflow_id=workflow_id,
            template_id=template_id,
            status=WorkflowStatus.PENDING,
            input_data=input_data,
            started_at=datetime.now(timezone.utc),
            user_id=user_id,
            session_id=session_id,
        )

        self.executions[execution.execution_id] = execution
        self.performance_metrics["total_executions"] += 1
        self.performance_metrics["active_executions"] += 1

        try:
            # Execute workflow
            result = await self.workflow_engine.execute_workflow(
                workflow_id, input_data, context
            )

            # Update execution record
            execution.status = result.status
            execution.output_data = result.final_result
            execution.completed_at = datetime.now(timezone.utc)
            execution.execution_time_ms = result.execution_time_ms
            execution.error = result.error

            # Update metrics
            if result.status == WorkflowStatus.COMPLETED:
                self.performance_metrics["successful_executions"] += 1
            else:
                self.performance_metrics["failed_executions"] += 1

            self.performance_metrics["active_executions"] -= 1

            # Update average execution time
            self._update_average_execution_time(result.execution_time_ms)

            # Record in monitoring
            await self.monitoring.record_execution(execution, result)

            return result

        except Exception as e:
            # Update execution record with error
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            execution.completed_at = datetime.now(timezone.utc)

            self.performance_metrics["failed_executions"] += 1
            self.performance_metrics["active_executions"] -= 1

            # Record error in monitoring
            await self.monitoring.record_error(execution, e)

            raise

    def _create_workflow_from_template(
        self, template: WorkflowTemplate, parameters: Dict[str, Any]
    ) -> WorkflowDefinition:
        """Create workflow definition from template with parameter substitution."""

        workflow_def = WorkflowDefinition(
            workflow_id=f"{template.template_id}_{uuid.uuid4().hex[:8]}",
            name=template.name,
        )

        # Apply parameter substitution to workflow definition
        workflow_config = self._substitute_parameters(
            template.workflow_definition, parameters
        )

        # Build workflow from configuration
        for step_config in workflow_config.get("steps", []):
            workflow_def.add_step(
                step_id=step_config["step_id"],
                agent_type=AgentType(step_config["agent_type"]),
                name=step_config["name"],
                dependencies=step_config.get("dependencies", []),
                timeout_seconds=step_config.get("timeout_seconds", 30),
                retry_count=step_config.get("retry_count", 3),
                retry_delay_seconds=step_config.get("retry_delay_seconds", 5),
                circuit_breaker_enabled=step_config.get(
                    "circuit_breaker_enabled", True
                ),
                fallback_enabled=step_config.get("fallback_enabled", True),
                metadata=step_config.get("metadata", {}),
            )

        return workflow_def

    def _substitute_parameters(
        self, template_data: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Substitute parameters in template data."""
        import re

        def substitute_value(value: Any) -> Any:
            if isinstance(value, str):
                # Replace parameter placeholders
                for param_name, param_value in parameters.items():
                    placeholder = f"${{{param_name}}}"
                    if placeholder in value:
                        value = value.replace(placeholder, str(param_value))
                return value
            elif isinstance(value, dict):
                return {k: substitute_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [substitute_value(v) for v in value]
            else:
                return value

        return substitute_value(template_data)

    def _update_average_execution_time(self, new_time_ms: int) -> None:
        """Update average execution time metric."""
        current_avg = self.performance_metrics["average_execution_time_ms"]
        total_executions = self.performance_metrics["successful_executions"]

        if total_executions > 0:
            new_avg = (
                (current_avg * (total_executions - 1)) + new_time_ms
            ) / total_executions
            self.performance_metrics["average_execution_time_ms"] = int(new_avg)

    async def get_execution_status(
        self, execution_id: str
    ) -> Optional[WorkflowExecution]:
        """Get execution status by ID."""
        return self.executions.get(execution_id)

    async def get_execution_history(
        self, user_id: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[WorkflowExecution]:
        """Get execution history with filtering."""
        executions = list(self.executions.values())

        # Filter by user if specified
        if user_id:
            executions = [e for e in executions if e.user_id == user_id]

        # Sort by start time (newest first)
        executions.sort(key=lambda e: e.started_at, reverse=True)

        # Apply pagination
        return executions[offset : offset + limit]

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return {
            **self.performance_metrics,
            "success_rate": (
                self.performance_metrics["successful_executions"]
                / max(self.performance_metrics["total_executions"], 1)
                * 100
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def cleanup_old_executions(self, days: int = 30) -> int:
        """Clean up old execution records."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        old_executions = [
            exec_id
            for exec_id, execution in self.executions.items()
            if execution.started_at < cutoff_date
        ]

        for exec_id in old_executions:
            del self.executions[exec_id]

        logger.info(f"Cleaned up {len(old_executions)} old execution records")
        return len(old_executions)


class PersistentStateStore:
    """Persistent state store with database integration."""

    def __init__(self, db_service=None):
        self.db_service = db_service
        self.cache: Dict[str, WorkflowState] = {}
        self.cache_ttl = 300  # 5 minutes

    async def save_state(self, workflow_id: str, state: WorkflowState) -> None:
        """Save workflow state to persistent storage."""
        # Update cache
        self.cache[workflow_id] = state

        # Save to database if available
        if self.db_service:
            try:
                await self.db_service.execute_raw_sql(
                    """
                    INSERT INTO workflow_states (workflow_id, state_data, created_at, updated_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (workflow_id) 
                    DO UPDATE SET 
                        state_data = EXCLUDED.state_data,
                        updated_at = EXCLUDED.updated_at
                    """,
                    {
                        "workflow_id": workflow_id,
                        "state_data": state.model_dump_json(),
                        "created_at": state.created_at,
                        "updated_at": state.updated_at,
                    },
                )
            except Exception as e:
                logger.error(f"Failed to save state to database: {e}")

    async def get_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get workflow state from cache or database."""
        # Check cache first
        if workflow_id in self.cache:
            return self.cache[workflow_id]

        # Load from database if available
        if self.db_service:
            try:
                result = await self.db_service.execute_raw_sql(
                    "SELECT state_data FROM workflow_states WHERE workflow_id = %s",
                    {"workflow_id": workflow_id},
                )

                if result:
                    state_data = json.loads(result[0]["state_data"])
                    state = WorkflowState(**state_data)
                    self.cache[workflow_id] = state
                    return state
            except Exception as e:
                logger.error(f"Failed to load state from database: {e}")

        return None

    async def delete_state(self, workflow_id: str) -> None:
        """Delete workflow state."""
        # Remove from cache
        self.cache.pop(workflow_id, None)

        # Delete from database if available
        if self.db_service:
            try:
                await self.db_service.execute_raw_sql(
                    "DELETE FROM workflow_states WHERE workflow_id = %s",
                    {"workflow_id": workflow_id},
                )
            except Exception as e:
                logger.error(f"Failed to delete state from database: {e}")


class WorkflowMonitoring:
    """Advanced workflow monitoring and alerting."""

    def __init__(self):
        self.alerts: List[Dict[str, Any]] = []
        self.metrics: Dict[str, Any] = {}
        self.thresholds = {
            "execution_time_ms": 300000,  # 5 minutes
            "error_rate": 0.1,  # 10%
            "success_rate": 0.9,  # 90%
        }

    async def record_execution(
        self, execution: WorkflowExecution, result: WorkflowResult
    ) -> None:
        """Record execution for monitoring."""
        # Update metrics
        self._update_execution_metrics(execution, result)

        # Check for alerts
        await self._check_alerts(execution, result)

    async def record_error(
        self, execution: WorkflowExecution, error: Exception
    ) -> None:
        """Record error for monitoring."""
        # Update error metrics
        self._update_error_metrics(execution, error)

        # Check for error alerts
        await self._check_error_alerts(execution, error)

    def _update_execution_metrics(
        self, execution: WorkflowExecution, result: WorkflowResult
    ) -> None:
        """Update execution metrics."""
        template_id = execution.template_id or "unknown"

        if template_id not in self.metrics:
            self.metrics[template_id] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "total_execution_time_ms": 0,
                "average_execution_time_ms": 0,
            }

        metrics = self.metrics[template_id]
        metrics["total_executions"] += 1

        if result.status == WorkflowStatus.COMPLETED:
            metrics["successful_executions"] += 1
        else:
            metrics["failed_executions"] += 1

        metrics["total_execution_time_ms"] += result.execution_time_ms
        metrics["average_execution_time_ms"] = (
            metrics["total_execution_time_ms"] / metrics["total_executions"]
        )

    def _update_error_metrics(
        self, execution: WorkflowExecution, error: Exception
    ) -> None:
        """Update error metrics."""
        template_id = execution.template_id or "unknown"

        if template_id not in self.metrics:
            self.metrics[template_id] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "errors": [],
            }

        self.metrics[template_id]["failed_executions"] += 1
        self.metrics[template_id]["errors"].append(
            {
                "execution_id": execution.execution_id,
                "error": str(error),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    async def _check_alerts(
        self, execution: WorkflowExecution, result: WorkflowResult
    ) -> None:
        """Check for performance alerts."""
        # Check execution time
        if result.execution_time_ms > self.thresholds["execution_time_ms"]:
            await self._create_alert(
                "SLOW_EXECUTION",
                f"Workflow {execution.workflow_id} took {result.execution_time_ms}ms",
                execution,
            )

        # Check success rate
        template_id = execution.template_id or "unknown"
        if template_id in self.metrics:
            metrics = self.metrics[template_id]
            success_rate = (
                metrics["successful_executions"] / metrics["total_executions"]
            )

            if success_rate < self.thresholds["success_rate"]:
                await self._create_alert(
                    "LOW_SUCCESS_RATE",
                    f"Template {template_id} success rate: {success_rate:.2%}",
                    execution,
                )

    async def _check_error_alerts(
        self, execution: WorkflowExecution, error: Exception
    ) -> None:
        """Check for error alerts."""
        template_id = execution.template_id or "unknown"

        if template_id in self.metrics:
            metrics = self.metrics[template_id]
            error_rate = metrics["failed_executions"] / metrics["total_executions"]

            if error_rate > self.thresholds["error_rate"]:
                await self._create_alert(
                    "HIGH_ERROR_RATE",
                    f"Template {template_id} error rate: {error_rate:.2%}",
                    execution,
                )

    async def _create_alert(
        self, alert_type: str, message: str, execution: WorkflowExecution
    ) -> None:
        """Create monitoring alert."""
        alert = {
            "alert_id": str(uuid.uuid4()),
            "alert_type": alert_type,
            "message": message,
            "execution_id": execution.execution_id,
            "workflow_id": execution.workflow_id,
            "template_id": execution.template_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": "WARNING" if alert_type in ["SLOW_EXECUTION"] else "ERROR",
        }

        self.alerts.append(alert)
        logger.warning(f"Workflow alert: {message}", alert=alert)

    def get_metrics(self, template_id: Optional[str] = None) -> Dict[str, Any]:
        """Get monitoring metrics."""
        if template_id:
            return self.metrics.get(template_id, {})
        return self.metrics

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


# Predefined workflow templates
class WorkflowTemplates:
    """Predefined workflow templates for common patterns."""

    @staticmethod
    def get_retrieval_synthesis_template() -> WorkflowTemplate:
        """Get retrieval + synthesis template."""
        return WorkflowTemplate(
            template_id="retrieval_synthesis",
            name="Retrieval and Synthesis",
            description="Basic retrieval and synthesis workflow",
            version="1.0.0",
            workflow_definition={
                "steps": [
                    {
                        "step_id": "retrieval",
                        "agent_type": "retrieval",
                        "name": "Document Retrieval",
                        "timeout_seconds": 30,
                        "retry_count": 2,
                    },
                    {
                        "step_id": "synthesis",
                        "agent_type": "synthesis",
                        "name": "Answer Synthesis",
                        "dependencies": ["retrieval"],
                        "timeout_seconds": 45,
                        "retry_count": 1,
                    },
                ]
            },
            parameters={"max_documents": 20, "synthesis_style": "concise"},
        )

    @staticmethod
    def get_comprehensive_template() -> WorkflowTemplate:
        """Get comprehensive analysis template."""
        return WorkflowTemplate(
            template_id="comprehensive",
            name="Comprehensive Analysis",
            description="Full analysis with fact-checking and citations",
            version="1.0.0",
            workflow_definition={
                "steps": [
                    {
                        "step_id": "retrieval",
                        "agent_type": "retrieval",
                        "name": "Document Retrieval",
                        "timeout_seconds": 30,
                    },
                    {
                        "step_id": "fact_check",
                        "agent_type": "fact_check",
                        "name": "Fact Checking",
                        "dependencies": ["retrieval"],
                        "timeout_seconds": 40,
                    },
                    {
                        "step_id": "synthesis",
                        "agent_type": "synthesis",
                        "name": "Answer Synthesis",
                        "dependencies": ["fact_check"],
                        "timeout_seconds": 45,
                    },
                    {
                        "step_id": "citation",
                        "agent_type": "citation",
                        "name": "Citation Generation",
                        "dependencies": ["synthesis", "retrieval"],
                        "timeout_seconds": 20,
                    },
                ]
            },
            parameters={
                "max_documents": 30,
                "synthesis_style": "comprehensive",
                "citation_style": "APA",
            },
        )

    @staticmethod
    def get_parallel_template() -> WorkflowTemplate:
        """Get parallel processing template."""
        return WorkflowTemplate(
            template_id="parallel",
            name="Parallel Processing",
            description="Parallel retrieval with result merging",
            version="1.0.0",
            workflow_definition={
                "steps": [
                    {
                        "step_id": "vector_retrieval",
                        "agent_type": "retrieval",
                        "name": "Vector Search",
                        "timeout_seconds": 25,
                        "metadata": {"search_type": "vector"},
                    },
                    {
                        "step_id": "keyword_retrieval",
                        "agent_type": "retrieval",
                        "name": "Keyword Search",
                        "timeout_seconds": 25,
                        "metadata": {"search_type": "keyword"},
                    },
                    {
                        "step_id": "merge_results",
                        "agent_type": "router",
                        "name": "Result Merging",
                        "dependencies": ["vector_retrieval", "keyword_retrieval"],
                        "timeout_seconds": 15,
                    },
                    {
                        "step_id": "synthesis",
                        "agent_type": "synthesis",
                        "name": "Answer Synthesis",
                        "dependencies": ["merge_results"],
                        "timeout_seconds": 45,
                    },
                ]
            },
            parameters={
                "vector_search_limit": 15,
                "keyword_search_limit": 15,
                "merge_strategy": "weighted",
            },
        )


# Export main classes
__all__ = [
    "WorkflowManager",
    "WorkflowTemplate",
    "WorkflowExecution",
    "PersistentStateStore",
    "WorkflowMonitoring",
    "WorkflowTemplates",
]
