#!/usr/bin/env python3
"""
SarvanOM Test Runner API Endpoints
REST API endpoints for test execution and metrics retrieval
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sys
import os

# Add project root to path
sys.path.append('.')

from shared.core.metrics_tracer import metrics_tracer

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/tests", tags=["tests"])

# Pydantic models
class TestRunRequest(BaseModel):
    scenarios: Optional[List[str]] = None
    base_url: str = "http://localhost:8000"
    config_path: str = "scenarios/scenario_config.yaml"
    parallel: int = 5

class TestRunResponse(BaseModel):
    run_id: str
    status: str
    message: str
    estimated_duration: Optional[int] = None

class LastRunSummary(BaseModel):
    trace_id: str
    test_id: str
    scenario_id: str
    timestamp: str
    duration_ms: float
    overall_success: bool
    total_lanes: int
    successful_lanes: int
    failed_lanes: int
    timeout_lanes: int
    lane_success_rate: float
    budget_compliant_lanes: int
    budget_efficiency_percent: float
    total_budget_allocated_ms: float
    total_budget_consumed_ms: float
    circuit_breaker_events: int
    total_retries: int
    degradation_flags: List[str]
    uncertainty_flags: List[str]
    provider_availability: Dict[str, bool]
    system_resources: Dict[str, Any]

class PerformanceMetrics(BaseModel):
    total_runs: int
    latency_percentiles: Dict[str, float]
    ttft_percentiles: Dict[str, float]
    throughput_percentiles: Dict[str, float]
    error_rate_percentiles: Dict[str, float]
    average_latency_ms: float
    average_ttft_ms: float
    average_throughput_qps: float
    average_error_rate_percent: float

@router.get("/last-run", response_model=LastRunSummary)
async def get_last_run_summary():
    """
    Get summary KPIs for the last completed test run
    
    Returns comprehensive metrics including:
    - Execution timing and success rates
    - Lane performance and budget compliance
    - Circuit breaker and retry activity
    - System resource utilization
    - Provider availability status
    """
    try:
        summary = metrics_tracer.get_last_run_summary()
        
        if "error" in summary:
            raise HTTPException(status_code=404, detail=summary["error"])
        
        return LastRunSummary(**summary)
        
    except Exception as e:
        logger.error(f"Failed to get last run summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve last run summary: {str(e)}")

@router.get("/last-run/detailed")
async def get_last_run_detailed():
    """
    Get detailed information for the last completed test run
    
    Returns the complete trace including:
    - Individual lane traces with timing and status
    - Retry attempts and circuit breaker events
    - Budget allocation and consumption details
    - Environment snapshot at execution time
    """
    try:
        summary = metrics_tracer.get_last_run_summary()
        
        if "error" in summary:
            raise HTTPException(status_code=404, detail=summary["error"])
        
        # Get the detailed trace
        trace_id = summary["trace_id"]
        detailed_trace = metrics_tracer.export_trace(trace_id)
        
        if not detailed_trace:
            raise HTTPException(status_code=404, detail="Detailed trace not found")
        
        return detailed_trace
        
    except Exception as e:
        logger.error(f"Failed to get last run detailed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve detailed trace: {str(e)}")

@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics():
    """
    Get aggregated performance metrics across all test runs
    
    Returns statistical analysis including:
    - Latency percentiles (P50, P95, P99)
    - Time-to-first-token percentiles
    - Throughput and error rate analysis
    - Average performance indicators
    """
    try:
        metrics = metrics_tracer.get_performance_metrics()
        
        if "error" in metrics:
            raise HTTPException(status_code=404, detail=metrics["error"])
        
        return PerformanceMetrics(**metrics)
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve performance metrics: {str(e)}")

@router.get("/traces")
async def list_all_traces():
    """
    List all completed test traces
    
    Returns a summary of all test runs with basic information
    """
    try:
        traces = metrics_tracer.export_all_traces()
        
        # Return simplified trace information
        trace_summaries = []
        for trace in traces:
            trace_summaries.append({
                "trace_id": trace["trace_id"],
                "test_id": trace["test_id"],
                "scenario_id": trace["scenario_id"],
                "timestamp": trace["environment_snapshot"]["timestamp"],
                "duration_ms": trace["total_duration_ms"],
                "overall_success": trace["overall_success"],
                "total_lanes": len(trace["lane_traces"]),
                "degradation_flags": trace["degradation_flags"],
                "uncertainty_flags": trace["uncertainty_flags"]
            })
        
        return {
            "total_traces": len(trace_summaries),
            "traces": trace_summaries
        }
        
    except Exception as e:
        logger.error(f"Failed to list traces: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list traces: {str(e)}")

@router.get("/traces/{trace_id}")
async def get_trace_by_id(trace_id: str):
    """
    Get detailed trace information by trace ID
    
    Returns the complete trace data for the specified trace ID
    """
    try:
        trace = metrics_tracer.export_trace(trace_id)
        
        if not trace:
            raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")
        
        return trace
        
    except Exception as e:
        logger.error(f"Failed to get trace {trace_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trace: {str(e)}")

@router.get("/health")
async def get_tests_health():
    """
    Get health status of the test runner system
    
    Returns system health information including:
    - Active traces count
    - Completed traces count
    - System resource status
    - Provider availability
    """
    try:
        # Get current environment snapshot
        env_snapshot = metrics_tracer.capture_environment_snapshot()
        
        # Get system status
        active_traces = len(metrics_tracer.active_traces)
        completed_traces = len(metrics_tracer.completed_traces)
        
        # Check system health
        system_healthy = True
        health_issues = []
        
        # Check CPU usage
        cpu_usage = env_snapshot.system_resources.get("cpu_percent", 0)
        if cpu_usage > 90:
            system_healthy = False
            health_issues.append(f"High CPU usage: {cpu_usage}%")
        
        # Check memory usage
        memory_usage = env_snapshot.system_resources.get("memory_percent", 0)
        if memory_usage > 90:
            system_healthy = False
            health_issues.append(f"High memory usage: {memory_usage}%")
        
        # Check disk usage
        disk_usage = env_snapshot.system_resources.get("disk_usage", 0)
        if disk_usage > 90:
            system_healthy = False
            health_issues.append(f"High disk usage: {disk_usage}%")
        
        # Check provider availability
        unavailable_providers = [
            provider for provider, available in env_snapshot.provider_availability.items()
            if not available
        ]
        
        if unavailable_providers:
            system_healthy = False
            health_issues.append(f"Unavailable providers: {', '.join(unavailable_providers)}")
        
        return {
            "status": "healthy" if system_healthy else "degraded",
            "timestamp": env_snapshot.timestamp,
            "active_traces": active_traces,
            "completed_traces": completed_traces,
            "system_resources": env_snapshot.system_resources,
            "provider_availability": env_snapshot.provider_availability,
            "health_issues": health_issues,
            "system_healthy": system_healthy
        }
        
    except Exception as e:
        logger.error(f"Failed to get tests health: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve health status: {str(e)}")

@router.post("/start", response_model=TestRunResponse)
async def start_test_run(request: TestRunRequest, background_tasks: BackgroundTasks):
    """
    Start a new test run (placeholder for future implementation)
    
    This endpoint would integrate with the test runner to start new test executions.
    Currently returns a placeholder response.
    """
    try:
        # This would integrate with the actual test runner
        # For now, return a placeholder response
        
        run_id = f"test_run_{int(__import__('time').time())}"
        
        return TestRunResponse(
            run_id=run_id,
            status="started",
            message="Test run started successfully (placeholder implementation)",
            estimated_duration=300
        )
        
    except Exception as e:
        logger.error(f"Failed to start test run: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start test run: {str(e)}")

@router.get("/scenarios")
async def list_available_scenarios():
    """
    List available test scenarios
    
    Returns a list of all available scenario files
    """
    try:
        scenarios_dir = "scenarios"
        if not os.path.exists(scenarios_dir):
            return {"scenarios": []}
        
        scenario_files = []
        for file in os.listdir(scenarios_dir):
            if file.endswith('.yaml') and file != 'scenario_config.yaml':
                scenario_name = file.replace('.yaml', '')
                scenario_files.append(scenario_name)
        
        return {"scenarios": sorted(scenario_files)}
        
    except Exception as e:
        logger.error(f"Failed to list scenarios: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list scenarios: {str(e)}")

@router.get("/config")
async def get_test_config():
    """
    Get current test configuration
    
    Returns the current test runner configuration
    """
    try:
        config_path = "test_runner_config.yaml"
        if not os.path.exists(config_path):
            return {"error": "Configuration file not found"}
        
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
        
    except Exception as e:
        logger.error(f"Failed to get test config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve configuration: {str(e)}")
