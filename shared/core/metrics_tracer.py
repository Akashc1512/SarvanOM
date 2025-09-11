#!/usr/bin/env python3
"""
SarvanOM Metrics & Tracing System
Comprehensive metrics capture with global trace_id, environment snapshots, and performance tracking
"""

import time
import uuid
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import asyncio
import os
import threading
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class LaneStatus(Enum):
    """Lane execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    FAILED = "failed"
    SKIPPED = "skipped"
    CIRCUIT_OPEN = "circuit_open"

class BreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class EnvironmentSnapshot:
    """Environment state at test execution time"""
    timestamp: str
    provider_availability: Dict[str, bool]
    endpoint_urls: Dict[str, str]
    model_names: Dict[str, List[str]]
    system_resources: Dict[str, Any]
    configuration: Dict[str, Any]

@dataclass
class LaneBudget:
    """Lane budget allocation and consumption"""
    lane_name: str
    allocated_ms: float
    consumed_ms: float
    remaining_ms: float
    budget_exceeded: bool
    efficiency_ratio: float

@dataclass
class RetryAttempt:
    """Retry attempt information"""
    attempt_number: int
    timestamp: str
    error_message: str
    backoff_delay_ms: float
    success: bool

@dataclass
class CircuitBreakerEvent:
    """Circuit breaker state change event"""
    timestamp: str
    breaker_name: str
    old_state: BreakerState
    new_state: BreakerState
    failure_count: int
    success_count: int
    trigger_reason: str

@dataclass
class LaneTrace:
    """Detailed trace for a single lane execution"""
    lane_name: str
    trace_id: str
    start_time: float
    end_time: float
    duration_ms: float
    status: LaneStatus
    error_message: Optional[str] = None
    retry_attempts: List[RetryAttempt] = field(default_factory=list)
    circuit_breaker_events: List[CircuitBreakerEvent] = field(default_factory=list)
    budget: Optional[LaneBudget] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GlobalTrace:
    """Global trace for entire test execution"""
    trace_id: str
    test_id: str
    scenario_id: str
    start_time: float
    end_time: float
    total_duration_ms: float
    environment_snapshot: EnvironmentSnapshot
    lane_traces: List[LaneTrace] = field(default_factory=list)
    global_budget_used: Dict[str, float] = field(default_factory=dict)
    overall_success: bool = False
    degradation_flags: List[str] = field(default_factory=list)
    uncertainty_flags: List[str] = field(default_factory=list)

class MetricsTracer:
    """Main metrics and tracing system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.active_traces: Dict[str, GlobalTrace] = {}
        self.completed_traces: List[GlobalTrace] = []
        self._lock = threading.Lock()
        
        # Circuit breaker state tracking
        self.breaker_states: Dict[str, BreakerState] = {}
        self.breaker_failure_counts: Dict[str, int] = {}
        self.breaker_success_counts: Dict[str, int] = {}
        
        # Performance metrics
        self.performance_metrics: Dict[str, List[float]] = {
            "latency": [],
            "ttft": [],
            "throughput": [],
            "error_rate": []
        }
        
        logger.info("MetricsTracer initialized")
    
    def generate_trace_id(self) -> str:
        """Generate unique trace ID"""
        return f"trace_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    def capture_environment_snapshot(self) -> EnvironmentSnapshot:
        """Capture current environment state"""
        try:
            # Provider availability (would be populated from actual health checks)
            provider_availability = {
                "openai": self._check_provider_health("openai"),
                "anthropic": self._check_provider_health("anthropic"),
                "huggingface": self._check_provider_health("huggingface"),
                "ollama": self._check_provider_health("ollama")
            }
            
            # Endpoint URLs
            endpoint_urls = {
                "gateway": os.getenv("GATEWAY_URL", "http://localhost:8000"),
                "qdrant": os.getenv("QDRANT_URL", "http://localhost:6333"),
                "arango": os.getenv("ARANGO_URL", "http://localhost:8529"),
                "meilisearch": os.getenv("MEILI_URL", "http://localhost:7700"),
                "postgres": os.getenv("POSTGRES_URL", "postgresql://localhost:5432/sarvanom")
            }
            
            # Model names
            model_names = {
                "openai": ["gpt-4", "gpt-3.5-turbo"],
                "anthropic": ["claude-3-opus", "claude-3-sonnet"],
                "huggingface": ["microsoft/DialoGPT-medium"],
                "ollama": ["llama2", "codellama"]
            }
            
            # System resources
            system_resources = {
                "cpu_percent": self._get_cpu_usage(),
                "memory_percent": self._get_memory_usage(),
                "disk_usage": self._get_disk_usage()
            }
            
            # Configuration
            configuration = {
                "max_tokens": int(os.getenv("MAX_TOKENS", "2000")),
                "temperature": float(os.getenv("TEMPERATURE", "0.7")),
                "timeout": int(os.getenv("TIMEOUT", "30")),
                "retry_attempts": int(os.getenv("RETRY_ATTEMPTS", "3"))
            }
            
            return EnvironmentSnapshot(
                timestamp=datetime.now(timezone.utc).isoformat(),
                provider_availability=provider_availability,
                endpoint_urls=endpoint_urls,
                model_names=model_names,
                system_resources=system_resources,
                configuration=configuration
            )
            
        except Exception as e:
            logger.error(f"Failed to capture environment snapshot: {e}")
            return EnvironmentSnapshot(
                timestamp=datetime.now(timezone.utc).isoformat(),
                provider_availability={},
                endpoint_urls={},
                model_names={},
                system_resources={},
                configuration={}
            )
    
    def _check_provider_health(self, provider: str) -> bool:
        """Check if provider is healthy (placeholder implementation)"""
        # In real implementation, this would check actual provider health
        return True
    
    def _get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        try:
            import psutil
            return psutil.cpu_percent()
        except ImportError:
            return 0.0
    
    def _get_memory_usage(self) -> float:
        """Get memory usage percentage"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except ImportError:
            return 0.0
    
    def _get_disk_usage(self) -> float:
        """Get disk usage percentage"""
        try:
            import psutil
            return psutil.disk_usage('/').percent
        except ImportError:
            return 0.0
    
    @asynccontextmanager
    async def start_global_trace(self, test_id: str, scenario_id: str):
        """Start a new global trace"""
        trace_id = self.generate_trace_id()
        start_time = time.time()
        
        # Capture environment snapshot
        env_snapshot = self.capture_environment_snapshot()
        
        # Create global trace
        global_trace = GlobalTrace(
            trace_id=trace_id,
            test_id=test_id,
            scenario_id=scenario_id,
            start_time=start_time,
            end_time=0,
            total_duration_ms=0,
            environment_snapshot=env_snapshot
        )
        
        with self._lock:
            self.active_traces[trace_id] = global_trace
        
        logger.info(f"Started global trace: {trace_id}")
        
        try:
            yield global_trace
        finally:
            # Complete the trace
            end_time = time.time()
            global_trace.end_time = end_time
            global_trace.total_duration_ms = (end_time - start_time) * 1000
            
            with self._lock:
                self.completed_traces.append(global_trace)
                if trace_id in self.active_traces:
                    del self.active_traces[trace_id]
            
            logger.info(f"Completed global trace: {trace_id} ({global_trace.total_duration_ms:.1f}ms)")
    
    @asynccontextmanager
    async def start_lane_trace(self, global_trace: GlobalTrace, lane_name: str, 
                             allocated_budget_ms: float = 0):
        """Start a lane trace within a global trace"""
        lane_trace = LaneTrace(
            lane_name=lane_name,
            trace_id=global_trace.trace_id,
            start_time=time.time(),
            end_time=0,
            duration_ms=0,
            status=LaneStatus.PENDING,
            budget=LaneBudget(
                lane_name=lane_name,
                allocated_ms=allocated_budget_ms,
                consumed_ms=0,
                remaining_ms=allocated_budget_ms,
                budget_exceeded=False,
                efficiency_ratio=0
            ) if allocated_budget_ms > 0 else None
        )
        
        # Add to global trace
        with self._lock:
            global_trace.lane_traces.append(lane_trace)
        
        logger.debug(f"Started lane trace: {lane_name} in {global_trace.trace_id}")
        
        try:
            lane_trace.status = LaneStatus.RUNNING
            yield lane_trace
        except Exception as e:
            lane_trace.status = LaneStatus.FAILED
            lane_trace.error_message = str(e)
            raise
        finally:
            # Complete the lane trace
            end_time = time.time()
            lane_trace.end_time = end_time
            lane_trace.duration_ms = (end_time - lane_trace.start_time) * 1000
            
            # Update budget information
            if lane_trace.budget:
                lane_trace.budget.consumed_ms = lane_trace.duration_ms
                lane_trace.budget.remaining_ms = max(0, lane_trace.budget.allocated_ms - lane_trace.duration_ms)
                lane_trace.budget.budget_exceeded = lane_trace.duration_ms > lane_trace.budget.allocated_ms
                lane_trace.budget.efficiency_ratio = lane_trace.budget.consumed_ms / max(lane_trace.budget.allocated_ms, 1)
            
            if lane_trace.status == LaneStatus.RUNNING:
                lane_trace.status = LaneStatus.COMPLETED
            
            logger.debug(f"Completed lane trace: {lane_name} ({lane_trace.duration_ms:.1f}ms)")
    
    def record_retry_attempt(self, lane_trace: LaneTrace, attempt_number: int, 
                           error_message: str, backoff_delay_ms: float, success: bool):
        """Record a retry attempt"""
        retry_attempt = RetryAttempt(
            attempt_number=attempt_number,
            timestamp=datetime.now(timezone.utc).isoformat(),
            error_message=error_message,
            backoff_delay_ms=backoff_delay_ms,
            success=success
        )
        
        lane_trace.retry_attempts.append(retry_attempt)
        logger.debug(f"Recorded retry attempt {attempt_number} for {lane_trace.lane_name}")
    
    def record_circuit_breaker_event(self, lane_trace: LaneTrace, breaker_name: str,
                                   old_state: BreakerState, new_state: BreakerState,
                                   failure_count: int, success_count: int, trigger_reason: str):
        """Record a circuit breaker state change"""
        event = CircuitBreakerEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            breaker_name=breaker_name,
            old_state=old_state,
            new_state=new_state,
            failure_count=failure_count,
            success_count=success_count,
            trigger_reason=trigger_reason
        )
        
        lane_trace.circuit_breaker_events.append(event)
        
        # Update global breaker state
        self.breaker_states[breaker_name] = new_state
        self.breaker_failure_counts[breaker_name] = failure_count
        self.breaker_success_counts[breaker_name] = success_count
        
        logger.info(f"Circuit breaker {breaker_name} changed from {old_state.value} to {new_state.value}")
    
    def add_degradation_flag(self, global_trace: GlobalTrace, flag: str):
        """Add a degradation flag to the global trace"""
        if flag not in global_trace.degradation_flags:
            global_trace.degradation_flags.append(flag)
            logger.warning(f"Added degradation flag: {flag}")
    
    def add_uncertainty_flag(self, global_trace: GlobalTrace, flag: str):
        """Add an uncertainty flag to the global trace"""
        if flag not in global_trace.uncertainty_flags:
            global_trace.uncertainty_flags.append(flag)
            logger.warning(f"Added uncertainty flag: {flag}")
    
    def update_global_budget(self, global_trace: GlobalTrace, budget_type: str, used_ms: float):
        """Update global budget consumption"""
        global_trace.global_budget_used[budget_type] = used_ms
        logger.debug(f"Updated global budget {budget_type}: {used_ms}ms")
    
    def get_last_run_summary(self) -> Dict[str, Any]:
        """Get summary KPIs for the last completed run"""
        if not self.completed_traces:
            return {"error": "No completed runs found"}
        
        last_trace = self.completed_traces[-1]
        
        # Calculate KPIs
        total_lanes = len(last_trace.lane_traces)
        successful_lanes = sum(1 for lt in last_trace.lane_traces if lt.status == LaneStatus.COMPLETED)
        failed_lanes = sum(1 for lt in last_trace.lane_traces if lt.status == LaneStatus.FAILED)
        timeout_lanes = sum(1 for lt in last_trace.lane_traces if lt.status == LaneStatus.TIMEOUT)
        
        # Budget compliance
        budget_compliant_lanes = 0
        total_budget_allocated = 0
        total_budget_consumed = 0
        
        for lt in last_trace.lane_traces:
            if lt.budget:
                total_budget_allocated += lt.budget.allocated_ms
                total_budget_consumed += lt.budget.consumed_ms
                if not lt.budget.budget_exceeded:
                    budget_compliant_lanes += 1
        
        budget_efficiency = (total_budget_consumed / max(total_budget_allocated, 1)) * 100
        
        # Circuit breaker activity
        total_breaker_events = sum(len(lt.circuit_breaker_events) for lt in last_trace.lane_traces)
        
        # Retry activity
        total_retries = sum(len(lt.retry_attempts) for lt in last_trace.lane_traces)
        
        return {
            "trace_id": last_trace.trace_id,
            "test_id": last_trace.test_id,
            "scenario_id": last_trace.scenario_id,
            "timestamp": last_trace.environment_snapshot.timestamp,
            "duration_ms": last_trace.total_duration_ms,
            "overall_success": last_trace.overall_success,
            
            # Lane metrics
            "total_lanes": total_lanes,
            "successful_lanes": successful_lanes,
            "failed_lanes": failed_lanes,
            "timeout_lanes": timeout_lanes,
            "lane_success_rate": (successful_lanes / max(total_lanes, 1)) * 100,
            
            # Budget metrics
            "budget_compliant_lanes": budget_compliant_lanes,
            "budget_efficiency_percent": budget_efficiency,
            "total_budget_allocated_ms": total_budget_allocated,
            "total_budget_consumed_ms": total_budget_consumed,
            
            # System metrics
            "circuit_breaker_events": total_breaker_events,
            "total_retries": total_retries,
            "degradation_flags": last_trace.degradation_flags,
            "uncertainty_flags": last_trace.uncertainty_flags,
            
            # Environment
            "provider_availability": last_trace.environment_snapshot.provider_availability,
            "system_resources": last_trace.environment_snapshot.system_resources
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get aggregated performance metrics"""
        if not self.completed_traces:
            return {"error": "No completed runs found"}
        
        # Aggregate metrics from all traces
        all_latencies = []
        all_ttfts = []
        all_throughputs = []
        all_error_rates = []
        
        for trace in self.completed_traces:
            all_latencies.append(trace.total_duration_ms)
            
            # Calculate TTFT from lane traces
            ttft_lanes = [lt for lt in trace.lane_traces if lt.lane_name == "llm"]
            if ttft_lanes:
                all_ttfts.append(ttft_lanes[0].duration_ms)
            
            # Calculate throughput (queries per second)
            throughput = 1 / (trace.total_duration_ms / 1000) if trace.total_duration_ms > 0 else 0
            all_throughputs.append(throughput)
            
            # Calculate error rate
            failed_lanes = sum(1 for lt in trace.lane_traces if lt.status in [LaneStatus.FAILED, LaneStatus.TIMEOUT])
            error_rate = (failed_lanes / max(len(trace.lane_traces), 1)) * 100
            all_error_rates.append(error_rate)
        
        def calculate_percentiles(values: List[float], percentiles: List[int]) -> Dict[str, float]:
            if not values:
                return {f"p{p}": 0.0 for p in percentiles}
            
            sorted_values = sorted(values)
            result = {}
            for p in percentiles:
                index = int((p / 100) * (len(sorted_values) - 1))
                result[f"p{p}"] = sorted_values[index]
            return result
        
        return {
            "total_runs": len(self.completed_traces),
            "latency_percentiles": calculate_percentiles(all_latencies, [50, 95, 99]),
            "ttft_percentiles": calculate_percentiles(all_ttfts, [50, 95, 99]),
            "throughput_percentiles": calculate_percentiles(all_throughputs, [50, 95, 99]),
            "error_rate_percentiles": calculate_percentiles(all_error_rates, [50, 95, 99]),
            "average_latency_ms": sum(all_latencies) / len(all_latencies) if all_latencies else 0,
            "average_ttft_ms": sum(all_ttfts) / len(all_ttfts) if all_ttfts else 0,
            "average_throughput_qps": sum(all_throughputs) / len(all_throughputs) if all_throughputs else 0,
            "average_error_rate_percent": sum(all_error_rates) / len(all_error_rates) if all_error_rates else 0
        }
    
    def export_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Export a specific trace as JSON"""
        for trace in self.completed_traces:
            if trace.trace_id == trace_id:
                return asdict(trace)
        return None
    
    def export_all_traces(self) -> List[Dict[str, Any]]:
        """Export all completed traces as JSON"""
        return [asdict(trace) for trace in self.completed_traces]

# Global metrics tracer instance
metrics_tracer = MetricsTracer()
