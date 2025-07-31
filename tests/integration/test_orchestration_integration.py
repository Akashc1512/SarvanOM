"""
Integration Tests for Orchestration System
Comprehensive testing of orchestration components and patterns.

Tests:
- Traditional orchestration workflows
- Event-driven orchestration
- LangChain integration
- Hybrid orchestration patterns
- Performance and reliability
- Error handling and recovery

Authors:
    - Universal Knowledge Platform Engineering Team
    
Version:
    2.0.0 (2024-12-28)
"""

import pytest
import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any

from shared.core.orchestration import (
    WorkflowEngine, WorkflowDefinition, WorkflowContext,
    WorkflowStatus, AgentType, WorkflowStep
)
from shared.core.workflow_manager import (
    WorkflowManager, WorkflowTemplate, WorkflowExecution
)
from shared.core.agent_orchestrator import (
    AgentOrchestrator, AgentInfo, AgentTask, AgentResult
)
from shared.core.event_driven_orchestration import (
    EventBus, EventDrivenWorkflowEngine, EventDrivenWorkflow,
    WorkflowEvent, EventType
)
from shared.core.orchestration_integration import (
    UnifiedOrchestrator, OrchestrationConfig, OrchestrationPattern,
    ExecutionMode, OrchestrationMonitor, OrchestrationDebugger
)

class MockAgent:
    """Mock agent for testing."""
    
    def __init__(self, agent_type: str, success_rate: float = 1.0):
        self.agent_type = agent_type
        self.success_rate = success_rate
        self.execution_count = 0
    
    async def process_task(self, task_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Process a task with simulated execution."""
        self.execution_count += 1
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Simulate success/failure
        if self.success_rate >= 1.0 or (self.execution_count % int(1/self.success_rate)) != 0:
            return {
                'success': True,
                'data': {
                    'result': f"Mock {self.agent_type} result",
                    'execution_count': self.execution_count
                }
            }
        else:
            raise Exception(f"Mock {self.agent_type} failed")

@pytest.fixture
def orchestration_config():
    """Create orchestration configuration for testing."""
    return OrchestrationConfig(
        pattern=OrchestrationPattern.TRADITIONAL,
        execution_mode=ExecutionMode.SEQUENTIAL,
        enable_caching=True,
        enable_monitoring=True,
        enable_event_sourcing=True,
        max_concurrent_workflows=10,
        max_concurrent_agents=5,
        timeout_seconds=30,
        retry_count=2,
        circuit_breaker_enabled=True
    )

@pytest.fixture
def unified_orchestrator(orchestration_config):
    """Create unified orchestrator for testing."""
    return UnifiedOrchestrator(orchestration_config)

@pytest.fixture
def mock_agents():
    """Create mock agents for testing."""
    return {
        AgentType.RETRIEVAL: MockAgent("retrieval", success_rate=0.9),
        AgentType.SYNTHESIS: MockAgent("synthesis", success_rate=0.95),
        AgentType.FACT_CHECK: MockAgent("fact_check", success_rate=0.8),
        AgentType.CITATION: MockAgent("citation", success_rate=0.9)
    }

@pytest.fixture
def basic_workflow():
    """Create basic workflow for testing."""
    workflow = WorkflowDefinition("test_workflow", "Test Workflow")
    
    workflow.add_step(
        step_id="retrieval",
        agent_type=AgentType.RETRIEVAL,
        name="Document Retrieval",
        timeout_seconds=10,
        retry_count=2
    ).add_step(
        step_id="synthesis",
        agent_type=AgentType.SYNTHESIS,
        name="Answer Synthesis",
        dependencies=["retrieval"],
        timeout_seconds=15,
        retry_count=1
    )
    
    return workflow

class TestTraditionalOrchestration:
    """Test traditional orchestration patterns."""
    
    @pytest.mark.asyncio
    async def test_basic_workflow_execution(self, unified_orchestrator, mock_agents, basic_workflow):
        """Test basic workflow execution."""
        # Register agents
        for agent_type, agent in mock_agents.items():
            info = AgentInfo(
                agent_type=agent_type,
                name=f"Mock {agent_type.value}",
                description=f"Mock {agent_type.value} agent",
                capabilities=[agent_type.value],
                max_concurrent_tasks=3
            )
            unified_orchestrator.register_agent(agent_type, agent, info)
        
        # Register workflow
        unified_orchestrator.register_workflow("test_workflow", basic_workflow)
        
        # Execute workflow
        result = await unified_orchestrator.execute_workflow(
            "test_workflow",
            {"query": "test query"},
            {"user_id": "test_user"}
        )
        
        # Verify result
        assert result["success"] is True
        assert result["pattern"] == "traditional"
        assert result["mode"] == "sequential"
        assert "trace_id" in result
    
    @pytest.mark.asyncio
    async def test_workflow_with_failure_recovery(self, unified_orchestrator, mock_agents):
        """Test workflow execution with failure recovery."""
        # Create workflow with failing agent
        failing_agent = MockAgent("failing", success_rate=0.3)
        
        workflow = WorkflowDefinition("failure_test", "Failure Test Workflow")
        workflow.add_step(
            step_id="failing_step",
            agent_type=AgentType.RETRIEVAL,
            name="Failing Step",
            timeout_seconds=5,
            retry_count=3
        )
        
        # Register agents
        info = AgentInfo(
            agent_type=AgentType.RETRIEVAL,
            name="Failing Agent",
            description="Agent that fails sometimes",
            capabilities=["retrieval"],
            max_concurrent_tasks=1
        )
        unified_orchestrator.register_agent(AgentType.RETRIEVAL, failing_agent, info)
        unified_orchestrator.register_workflow("failure_test", workflow)
        
        # Execute workflow
        result = await unified_orchestrator.execute_workflow("failure_test", {"query": "test"})
        
        # Should succeed due to retries
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_parallel_execution(self, unified_orchestrator, mock_agents):
        """Test parallel workflow execution."""
        # Create workflow with parallel steps
        workflow = WorkflowDefinition("parallel_test", "Parallel Test Workflow")
        
        # Add parallel steps
        workflow.add_step(
            step_id="step1",
            agent_type=AgentType.RETRIEVAL,
            name="Step 1"
        ).add_step(
            step_id="step2",
            agent_type=AgentType.SYNTHESIS,
            name="Step 2"
        ).add_step(
            step_id="merge",
            agent_type=AgentType.CITATION,
            name="Merge Results",
            dependencies=["step1", "step2"]
        )
        
        # Register agents
        for agent_type, agent in mock_agents.items():
            info = AgentInfo(
                agent_type=agent_type,
                name=f"Mock {agent_type.value}",
                description=f"Mock {agent_type.value} agent",
                capabilities=[agent_type.value]
            )
            unified_orchestrator.register_agent(agent_type, agent, info)
        
        unified_orchestrator.register_workflow("parallel_test", workflow)
        
        # Execute with parallel mode
        result = await unified_orchestrator.execute_workflow(
            "parallel_test",
            {"query": "test"},
            mode=ExecutionMode.PARALLEL
        )
        
        assert result["success"] is True
        assert result["mode"] == "parallel"

class TestEventDrivenOrchestration:
    """Test event-driven orchestration patterns."""
    
    @pytest.mark.asyncio
    async def test_event_driven_workflow(self, unified_orchestrator):
        """Test event-driven workflow execution."""
        # Create event-driven workflow
        workflow = EventDrivenWorkflow("event_test", "Event Test Workflow")
        workflow.add_step(
            step_id="retrieval",
            agent_type="retrieval",
            task_data={"query": "test"}
        ).add_step(
            step_id="synthesis",
            agent_type="synthesis",
            task_data={},
            dependencies=["retrieval"]
        )
        
        # Register workflow
        await unified_orchestrator.event_driven_engine.register_workflow(workflow)
        
        # Execute workflow
        result = await unified_orchestrator.execute_workflow(
            "event_test",
            {"query": "test query"},
            pattern=OrchestrationPattern.EVENT_DRIVEN
        )
        
        assert result["pattern"] == "event_driven"
        assert "execution_id" in result
    
    @pytest.mark.asyncio
    async def test_event_bus_communication(self):
        """Test event bus communication."""
        event_bus = EventBus()
        events_received = []
        
        async def event_handler(event: WorkflowEvent):
            events_received.append(event)
        
        # Subscribe to events
        await event_bus.subscribe(EventType.WORKFLOW_STARTED, event_handler)
        
        # Publish event
        event = WorkflowEvent(
            event_id="test_event",
            event_type=EventType.WORKFLOW_STARTED,
            timestamp=datetime.now(timezone.utc),
            source="test",
            data={"test": "data"}
        )
        
        await event_bus.publish(event)
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        assert len(events_received) == 1
        assert events_received[0].event_id == "test_event"

class TestPerformanceAndReliability:
    """Test performance and reliability features."""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_pattern(self, unified_orchestrator):
        """Test circuit breaker pattern."""
        # Create agent that fails frequently
        failing_agent = MockAgent("failing", success_rate=0.1)
        
        info = AgentInfo(
            agent_type=AgentType.RETRIEVAL,
            name="Failing Agent",
            description="Agent that fails frequently",
            capabilities=["retrieval"],
            circuit_breaker_enabled=True
        )
        
        unified_orchestrator.register_agent(AgentType.RETRIEVAL, failing_agent, info)
        
        # Create simple workflow
        workflow = WorkflowDefinition("circuit_test", "Circuit Test Workflow")
        workflow.add_step(
            step_id="failing_step",
            agent_type=AgentType.RETRIEVAL,
            name="Failing Step",
            timeout_seconds=5,
            retry_count=2
        )
        
        unified_orchestrator.register_workflow("circuit_test", workflow)
        
        # Execute multiple times to trigger circuit breaker
        results = []
        for _ in range(5):
            result = await unified_orchestrator.execute_workflow("circuit_test", {"query": "test"})
            results.append(result)
        
        # Check that circuit breaker was triggered
        metrics = unified_orchestrator.get_performance_metrics()
        assert metrics['circuit_breaker_trips'] > 0
    
    @pytest.mark.asyncio
    async def test_caching_effectiveness(self, unified_orchestrator, mock_agents, basic_workflow):
        """Test caching effectiveness."""
        # Register agents and workflow
        for agent_type, agent in mock_agents.items():
            info = AgentInfo(
                agent_type=agent_type,
                name=f"Mock {agent_type.value}",
                description=f"Mock {agent_type.value} agent",
                capabilities=[agent_type.value]
            )
            unified_orchestrator.register_agent(agent_type, agent, info)
        
        unified_orchestrator.register_workflow("cache_test", basic_workflow)
        
        # Execute same workflow multiple times
        start_time = time.time()
        
        for _ in range(3):
            result = await unified_orchestrator.execute_workflow(
                "cache_test",
                {"query": "same query"},
                {"user_id": "test_user"}
            )
            assert result["success"] is True
        
        total_time = time.time() - start_time
        
        # Subsequent executions should be faster due to caching
        assert total_time < 3.0  # Should be much faster than 3 seconds
    
    @pytest.mark.asyncio
    async def test_concurrent_execution_limits(self, unified_orchestrator, mock_agents):
        """Test concurrent execution limits."""
        # Create simple workflow
        workflow = WorkflowDefinition("concurrent_test", "Concurrent Test Workflow")
        workflow.add_step(
            step_id="step1",
            agent_type=AgentType.RETRIEVAL,
            name="Step 1",
            timeout_seconds=2
        )
        
        # Register agents and workflow
        for agent_type, agent in mock_agents.items():
            info = AgentInfo(
                agent_type=agent_type,
                name=f"Mock {agent_type.value}",
                description=f"Mock {agent_type.value} agent",
                capabilities=[agent_type.value]
            )
            unified_orchestrator.register_agent(agent_type, agent, info)
        
        unified_orchestrator.register_workflow("concurrent_test", workflow)
        
        # Execute multiple workflows concurrently
        tasks = []
        for i in range(5):
            task = unified_orchestrator.execute_workflow(
                "concurrent_test",
                {"query": f"test {i}"}
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        for result in results:
            assert result["success"] is True
        
        # Check that limits were respected
        metrics = unified_orchestrator.get_performance_metrics()
        assert metrics['active_workflows'] == 0  # All completed

class TestMonitoringAndDebugging:
    """Test monitoring and debugging features."""
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self, unified_orchestrator, mock_agents, basic_workflow):
        """Test performance monitoring."""
        # Register agents and workflow
        for agent_type, agent in mock_agents.items():
            info = AgentInfo(
                agent_type=agent_type,
                name=f"Mock {agent_type.value}",
                description=f"Mock {agent_type.value} agent",
                capabilities=[agent_type.value]
            )
            unified_orchestrator.register_agent(agent_type, agent, info)
        
        unified_orchestrator.register_workflow("monitor_test", basic_workflow)
        
        # Execute workflow
        await unified_orchestrator.execute_workflow("monitor_test", {"query": "test"})
        
        # Check metrics
        metrics = unified_orchestrator.get_performance_metrics()
        
        assert metrics['total_executions'] > 0
        assert metrics['successful_executions'] > 0
        assert metrics['average_execution_time_ms'] > 0
        assert metrics['success_rate'] > 0
    
    @pytest.mark.asyncio
    async def test_system_health_check(self, unified_orchestrator):
        """Test system health check."""
        health = unified_orchestrator.get_system_health()
        
        assert 'status' in health
        assert 'active_executions' in health
        assert 'circuit_breaker_trips' in health
        assert 'cache_hit_rate' in health
        assert 'last_execution' in health
    
    @pytest.mark.asyncio
    async def test_debug_session(self, unified_orchestrator):
        """Test debug session functionality."""
        debugger = OrchestrationDebugger(unified_orchestrator)
        
        # Start debug session
        session_id = debugger.start_debug_session("test_workflow")
        
        # Add breakpoint
        debugger.add_breakpoint(session_id, "test_step", "condition")
        
        # Capture state snapshot
        debugger.capture_state_snapshot(session_id, {"test": "state"})
        
        # Get session info
        session = debugger.get_debug_session(session_id)
        
        assert session is not None
        assert session['workflow_id'] == "test_workflow"
        assert len(session['breakpoints']) == 1
        assert len(session['state_snapshots']) == 1
        
        # End session
        debugger.end_debug_session(session_id)
        
        session = debugger.get_debug_session(session_id)
        assert session['ended_at'] is not None
        assert session['duration'] > 0

class TestErrorHandlingAndRecovery:
    """Test error handling and recovery mechanisms."""
    
    @pytest.mark.asyncio
    async def test_workflow_timeout_handling(self, unified_orchestrator):
        """Test workflow timeout handling."""
        # Create slow agent
        slow_agent = MockAgent("slow")
        
        # Override process_task to be slow
        async def slow_process_task(task_data, context):
            await asyncio.sleep(5)  # Exceed timeout
            return {"success": True, "data": {}}
        
        slow_agent.process_task = slow_process_task
        
        info = AgentInfo(
            agent_type=AgentType.RETRIEVAL,
            name="Slow Agent",
            description="Agent that takes too long",
            capabilities=["retrieval"]
        )
        
        unified_orchestrator.register_agent(AgentType.RETRIEVAL, slow_agent, info)
        
        # Create workflow with short timeout
        workflow = WorkflowDefinition("timeout_test", "Timeout Test Workflow")
        workflow.add_step(
            step_id="slow_step",
            agent_type=AgentType.RETRIEVAL,
            name="Slow Step",
            timeout_seconds=1  # Short timeout
        )
        
        unified_orchestrator.register_workflow("timeout_test", workflow)
        
        # Execute workflow
        result = await unified_orchestrator.execute_workflow("timeout_test", {"query": "test"})
        
        # Should handle timeout gracefully
        assert result["success"] is False or "timeout" in str(result).lower()
    
    @pytest.mark.asyncio
    async def test_agent_failure_recovery(self, unified_orchestrator):
        """Test agent failure recovery."""
        # Create agent that fails initially but succeeds on retry
        class RetryAgent(MockAgent):
            def __init__(self):
                super().__init__("retry")
                self.fail_count = 0
            
            async def process_task(self, task_data, context):
                self.fail_count += 1
                if self.fail_count <= 2:
                    raise Exception("Temporary failure")
                return {"success": True, "data": {"retry_count": self.fail_count}}
        
        retry_agent = RetryAgent()
        
        info = AgentInfo(
            agent_type=AgentType.RETRIEVAL,
            name="Retry Agent",
            description="Agent that fails then succeeds",
            capabilities=["retrieval"]
        )
        
        unified_orchestrator.register_agent(AgentType.RETRIEVAL, retry_agent, info)
        
        # Create workflow
        workflow = WorkflowDefinition("retry_test", "Retry Test Workflow")
        workflow.add_step(
            step_id="retry_step",
            agent_type=AgentType.RETRIEVAL,
            name="Retry Step",
            timeout_seconds=10,
            retry_count=3
        )
        
        unified_orchestrator.register_workflow("retry_test", workflow)
        
        # Execute workflow
        result = await unified_orchestrator.execute_workflow("retry_test", {"query": "test"})
        
        # Should succeed after retries
        assert result["success"] is True
        assert retry_agent.fail_count > 1  # Should have retried

class TestIntegrationPatterns:
    """Test integration patterns and workflows."""
    
    @pytest.mark.asyncio
    async def test_hybrid_orchestration(self, unified_orchestrator, mock_agents):
        """Test hybrid orchestration pattern."""
        # Register agents
        for agent_type, agent in mock_agents.items():
            info = AgentInfo(
                agent_type=agent_type,
                name=f"Mock {agent_type.value}",
                description=f"Mock {agent_type.value} agent",
                capabilities=[agent_type.value]
            )
            unified_orchestrator.register_agent(agent_type, agent, info)
        
        # Create workflow
        workflow = WorkflowDefinition("hybrid_test", "Hybrid Test Workflow")
        workflow.add_step(
            step_id="retrieval",
            agent_type=AgentType.RETRIEVAL,
            name="Document Retrieval"
        ).add_step(
            step_id="synthesis",
            agent_type=AgentType.SYNTHESIS,
            name="Answer Synthesis",
            dependencies=["retrieval"]
        )
        
        unified_orchestrator.register_workflow("hybrid_test", workflow)
        
        # Execute with hybrid pattern
        result = await unified_orchestrator.execute_workflow(
            "hybrid_test",
            {"query": "test query"},
            pattern=OrchestrationPattern.HYBRID
        )
        
        assert result["success"] is True
        assert result["pattern"] == "hybrid"
    
    @pytest.mark.asyncio
    async def test_comprehensive_workflow(self, unified_orchestrator, mock_agents):
        """Test comprehensive workflow with all agents."""
        # Register all agents
        for agent_type, agent in mock_agents.items():
            info = AgentInfo(
                agent_type=agent_type,
                name=f"Mock {agent_type.value}",
                description=f"Mock {agent_type.value} agent",
                capabilities=[agent_type.value]
            )
            unified_orchestrator.register_agent(agent_type, agent, info)
        
        # Create comprehensive workflow
        workflow = WorkflowDefinition("comprehensive_test", "Comprehensive Test Workflow")
        workflow.add_step(
            step_id="retrieval",
            agent_type=AgentType.RETRIEVAL,
            name="Document Retrieval"
        ).add_step(
            step_id="fact_check",
            agent_type=AgentType.FACT_CHECK,
            name="Fact Checking",
            dependencies=["retrieval"]
        ).add_step(
            step_id="synthesis",
            agent_type=AgentType.SYNTHESIS,
            name="Answer Synthesis",
            dependencies=["fact_check"]
        ).add_step(
            step_id="citation",
            agent_type=AgentType.CITATION,
            name="Citation Generation",
            dependencies=["synthesis", "retrieval"]
        )
        
        unified_orchestrator.register_workflow("comprehensive_test", workflow)
        
        # Execute comprehensive workflow
        result = await unified_orchestrator.execute_workflow(
            "comprehensive_test",
            {"query": "comprehensive test query"},
            {"user_id": "test_user", "detailed": True}
        )
        
        assert result["success"] is True
        assert "trace_id" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 