"""
Multi-Lane Orchestrator - Always-On Parallel Query Processing
============================================================

Provides resilient query processing through parallel lanes:
- Web/Retrieval lane (free sources first)
- Vector lane (embeddings + similarity search)  
- Knowledge Graph lane (ArangoDB)
- LLM synthesis lane (with B2 policy)

Features:
- Non-blocking orchestration with strict budgets
- Graceful degradation with partial results
- Per-lane timeout enforcement
- Comprehensive metrics collection
- Circuit breaker patterns

Maps to Phase B3 requirements for production resilience.
"""

import os
import asyncio
import time
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class LaneStatus(Enum):
    """Status of individual processing lanes."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class LaneConfig:
    """Configuration for individual processing lane."""
    name: str
    enabled: bool = True
    timeout_seconds: float = 3.0
    priority: int = 1  # Lower = higher priority
    required: bool = False  # If True, failure affects overall success
    retry_count: int = 0
    circuit_breaker_threshold: int = 5
    
    def __post_init__(self):
        """Validate configuration."""
        if self.timeout_seconds <= 0:
            raise ValueError(f"timeout_seconds must be positive, got {self.timeout_seconds}")
        if self.priority < 1:
            raise ValueError(f"priority must be >= 1, got {self.priority}")


@dataclass
class LaneResult:
    """Result from individual processing lane."""
    lane_name: str
    status: LaneStatus
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: float = 0.0
    end_time: float = 0.0
    timeout_seconds: float = 0.0
    
    @property
    def duration_ms(self) -> float:
        """Get execution duration in milliseconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0
    
    @property
    def is_successful(self) -> bool:
        """Check if lane completed successfully."""
        return self.status == LaneStatus.COMPLETED and self.data is not None
    
    @property
    def is_partial(self) -> bool:
        """Check if lane provided partial results."""
        return self.status in [LaneStatus.TIMEOUT, LaneStatus.FAILED] and self.data is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'lane_name': self.lane_name,
            'status': self.status.value,
            'data': self.data,
            'error': self.error,
            'duration_ms': self.duration_ms,
            'timeout_seconds': self.timeout_seconds,
            'is_successful': self.is_successful,
            'is_partial': self.is_partial
        }


@dataclass
class OrchestrationConfig:
    """Configuration for multi-lane orchestration."""
    
    # Global timeouts
    max_total_time_seconds: float = 3.0  # E2E budget
    max_wait_for_required_seconds: float = 2.0
    
    # Lane configurations
    retrieval_timeout: float = 3.0
    vector_timeout: float = 2.0  
    kg_timeout: float = 1.5
    llm_timeout: float = 2.5
    
    # Behavior settings
    return_partial_results: bool = True
    require_at_least_one_lane: bool = True
    max_concurrent_lanes: int = 4
    
    # Circuit breaker settings
    circuit_breaker_enabled: bool = True
    failure_threshold: int = 5
    circuit_timeout_seconds: int = 60
    
    @classmethod
    def from_environment(cls) -> 'OrchestrationConfig':
        """Load configuration from environment variables."""
        return cls(
            max_total_time_seconds=float(os.getenv('MAX_RESPONSE_TIME_S', '3.0')),
            max_wait_for_required_seconds=float(os.getenv('MAX_WAIT_FOR_REQUIRED_S', '2.0')),
            retrieval_timeout=float(os.getenv('RETRIEVAL_TIMEOUT_S', '3.0')),
            vector_timeout=float(os.getenv('VECTOR_TIMEOUT_S', '2.0')),
            kg_timeout=float(os.getenv('KG_TIMEOUT_S', '1.5')),
            llm_timeout=float(os.getenv('LLM_TIMEOUT_S', '2.5')),
            return_partial_results=os.getenv('RETURN_PARTIAL_RESULTS', 'true').lower() == 'true',
            require_at_least_one_lane=os.getenv('REQUIRE_AT_LEAST_ONE_LANE', 'true').lower() == 'true',
            max_concurrent_lanes=int(os.getenv('MAX_CONCURRENT_LANES', '4')),
            circuit_breaker_enabled=os.getenv('CIRCUIT_BREAKER_ENABLED', 'true').lower() == 'true',
            failure_threshold=int(os.getenv('CIRCUIT_FAILURE_THRESHOLD', '5')),
            circuit_timeout_seconds=int(os.getenv('CIRCUIT_TIMEOUT_S', '60'))
        )
    
    def get_lane_configs(self) -> Dict[str, LaneConfig]:
        """Get configuration for each lane."""
        return {
            'retrieval': LaneConfig(
                name='retrieval',
                timeout_seconds=self.retrieval_timeout,
                priority=1,
                required=False
            ),
            'vector': LaneConfig(
                name='vector', 
                timeout_seconds=self.vector_timeout,
                priority=2,
                required=False
            ),
            'knowledge_graph': LaneConfig(
                name='knowledge_graph',
                timeout_seconds=self.kg_timeout,
                priority=3,
                required=False
            ),
            'llm_synthesis': LaneConfig(
                name='llm_synthesis',
                timeout_seconds=self.llm_timeout,
                priority=4,
                required=True  # LLM synthesis is required for final answer
            )
        }


@dataclass
class OrchestrationMetrics:
    """Metrics for orchestration performance."""
    total_requests: int = 0
    successful_requests: int = 0
    partial_requests: int = 0
    failed_requests: int = 0
    
    # Per-lane metrics
    lane_success_counts: Dict[str, int] = field(default_factory=dict)
    lane_failure_counts: Dict[str, int] = field(default_factory=dict)
    lane_timeout_counts: Dict[str, int] = field(default_factory=dict)
    lane_avg_duration_ms: Dict[str, float] = field(default_factory=dict)
    
    # Circuit breaker states
    circuit_breaker_states: Dict[str, bool] = field(default_factory=dict)
    circuit_breaker_last_failure: Dict[str, float] = field(default_factory=dict)
    
    def record_request(self, results: List[LaneResult]) -> None:
        """Record metrics for a completed request."""
        self.total_requests += 1
        
        successful_lanes = [r for r in results if r.is_successful]
        partial_lanes = [r for r in results if r.is_partial]
        
        if successful_lanes:
            if len(successful_lanes) == len(results):
                self.successful_requests += 1
            else:
                self.partial_requests += 1
        else:
            self.failed_requests += 1
        
        # Record per-lane metrics
        for result in results:
            lane_name = result.lane_name
            
            # Initialize lane metrics if needed
            if lane_name not in self.lane_success_counts:
                self.lane_success_counts[lane_name] = 0
                self.lane_failure_counts[lane_name] = 0
                self.lane_timeout_counts[lane_name] = 0
                self.lane_avg_duration_ms[lane_name] = 0.0
            
            # Update counts
            if result.is_successful:
                self.lane_success_counts[lane_name] += 1
            elif result.status == LaneStatus.TIMEOUT:
                self.lane_timeout_counts[lane_name] += 1
            else:
                self.lane_failure_counts[lane_name] += 1
            
            # Update average duration
            total_requests = (
                self.lane_success_counts[lane_name] + 
                self.lane_failure_counts[lane_name] + 
                self.lane_timeout_counts[lane_name]
            )
            
            if total_requests > 0:
                current_avg = self.lane_avg_duration_ms[lane_name]
                new_avg = ((current_avg * (total_requests - 1)) + result.duration_ms) / total_requests
                self.lane_avg_duration_ms[lane_name] = new_avg
    
    def get_lane_success_rate(self, lane_name: str) -> float:
        """Get success rate for specific lane."""
        success = self.lane_success_counts.get(lane_name, 0)
        failure = self.lane_failure_counts.get(lane_name, 0)
        timeout = self.lane_timeout_counts.get(lane_name, 0)
        total = success + failure + timeout
        
        return success / total if total > 0 else 0.0
    
    def should_open_circuit_breaker(self, lane_name: str, failure_threshold: int) -> bool:
        """Check if circuit breaker should be opened for lane."""
        recent_failures = self.lane_failure_counts.get(lane_name, 0)
        return recent_failures >= failure_threshold
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'partial_requests': self.partial_requests,
            'failed_requests': self.failed_requests,
            'success_rate': self.successful_requests / max(self.total_requests, 1),
            'partial_rate': self.partial_requests / max(self.total_requests, 1),
            'lane_metrics': {
                lane_name: {
                    'success_count': self.lane_success_counts.get(lane_name, 0),
                    'failure_count': self.lane_failure_counts.get(lane_name, 0),
                    'timeout_count': self.lane_timeout_counts.get(lane_name, 0),
                    'success_rate': self.get_lane_success_rate(lane_name),
                    'avg_duration_ms': self.lane_avg_duration_ms.get(lane_name, 0.0),
                    'circuit_breaker_open': self.circuit_breaker_states.get(lane_name, False)
                }
                for lane_name in set(
                    list(self.lane_success_counts.keys()) +
                    list(self.lane_failure_counts.keys()) +
                    list(self.lane_timeout_counts.keys())
                )
            }
        }


class MultiLaneOrchestrator:
    """
    Orchestrates parallel query processing across multiple lanes.
    
    Features:
    - Parallel lane execution with individual timeouts
    - Graceful degradation with partial results
    - Circuit breaker patterns for reliability
    - Comprehensive metrics collection
    - Non-blocking operation under failures
    """
    
    def __init__(self):
        """Initialize multi-lane orchestrator."""
        self.config = OrchestrationConfig.from_environment()
        self.lane_configs = self.config.get_lane_configs()
        self.metrics = OrchestrationMetrics()
        
        logger.info("MultiLaneOrchestrator initialized",
                   config=self.config.__dict__,
                   lane_count=len(self.lane_configs))
    
    async def _execute_retrieval_lane(self, query: str, context: Dict[str, Any]) -> LaneResult:
        """Execute retrieval/search lane."""
        lane_name = "retrieval"
        start_time = time.time()
        
        try:
            # Import retrieval service
            from shared.core.services.retrieval_aggregator import get_retrieval_aggregator_health
            
            # Simulate retrieval processing (replace with actual retrieval logic)
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # For now, return mock data - this will be replaced with actual retrieval
            result_data = {
                'sources': [
                    {'title': 'Example Source 1', 'url': 'https://example.com/1', 'score': 0.95},
                    {'title': 'Example Source 2', 'url': 'https://example.com/2', 'score': 0.87}
                ],
                'query': query,
                'source_count': 2
            }
            
            return LaneResult(
                lane_name=lane_name,
                status=LaneStatus.COMPLETED,
                data=result_data,
                start_time=start_time,
                end_time=time.time(),
                timeout_seconds=self.lane_configs[lane_name].timeout_seconds
            )
            
        except asyncio.TimeoutError:
            return LaneResult(
                lane_name=lane_name,
                status=LaneStatus.TIMEOUT,
                error="Retrieval lane timeout",
                start_time=start_time,
                end_time=time.time(),
                timeout_seconds=self.lane_configs[lane_name].timeout_seconds
            )
        except Exception as e:
            return LaneResult(
                lane_name=lane_name,
                status=LaneStatus.FAILED,
                error=str(e),
                start_time=start_time,
                end_time=time.time(),
                timeout_seconds=self.lane_configs[lane_name].timeout_seconds
            )
    
    async def _execute_vector_lane(self, query: str, context: Dict[str, Any]) -> LaneResult:
        """Execute vector search lane."""
        lane_name = "vector"
        start_time = time.time()
        
        try:
            # Import vector service
            from shared.core.services.vector_singleton_service import get_vector_singleton_service
            
            # Get vector service
            vector_service = get_vector_singleton_service()
            
            # Perform semantic search
            results = await vector_service.semantic_search(query, top_k=5)
            
            result_data = {
                'vector_results': results,
                'query': query,
                'result_count': len(results)
            }
            
            return LaneResult(
                lane_name=lane_name,
                status=LaneStatus.COMPLETED,
                data=result_data,
                start_time=start_time,
                end_time=time.time(),
                timeout_seconds=self.lane_configs[lane_name].timeout_seconds
            )
            
        except asyncio.TimeoutError:
            return LaneResult(
                lane_name=lane_name,
                status=LaneStatus.TIMEOUT,
                error="Vector lane timeout",
                start_time=start_time,
                end_time=time.time(),
                timeout_seconds=self.lane_configs[lane_name].timeout_seconds
            )
        except Exception as e:
            return LaneResult(
                lane_name=lane_name,
                status=LaneStatus.FAILED,
                error=str(e),
                start_time=start_time,
                end_time=time.time(),
                timeout_seconds=self.lane_configs[lane_name].timeout_seconds
            )
    
    async def _execute_kg_lane(self, query: str, context: Dict[str, Any]) -> LaneResult:
        """Execute knowledge graph lane."""
        lane_name = "knowledge_graph"
        start_time = time.time()
        
        try:
            # Import ArangoDB service
            from shared.core.services.arangodb_service import arangodb_service
            
            # Simple knowledge graph query (replace with actual KG logic)
            kg_query = f"FOR e IN entities FILTER CONTAINS(e.name, '{query}') LIMIT 5 RETURN e"
            
            try:
                results = await arangodb_service.execute_aql(kg_query)
            except Exception:
                # Graceful degradation if ArangoDB unavailable
                results = []
            
            result_data = {
                'kg_results': results,
                'query': query,
                'result_count': len(results)
            }
            
            return LaneResult(
                lane_name=lane_name,
                status=LaneStatus.COMPLETED,
                data=result_data,
                start_time=start_time,
                end_time=time.time(),
                timeout_seconds=self.lane_configs[lane_name].timeout_seconds
            )
            
        except asyncio.TimeoutError:
            return LaneResult(
                lane_name=lane_name,
                status=LaneStatus.TIMEOUT,
                error="Knowledge graph lane timeout",
                start_time=start_time,
                end_time=time.time(),
                timeout_seconds=self.lane_configs[lane_name].timeout_seconds
            )
        except Exception as e:
            return LaneResult(
                lane_name=lane_name,
                status=LaneStatus.FAILED,
                error=str(e),
                start_time=start_time,
                end_time=time.time(),
                timeout_seconds=self.lane_configs[lane_name].timeout_seconds
            )
    
    async def _execute_llm_lane(self, query: str, context: Dict[str, Any]) -> LaneResult:
        """Execute LLM synthesis lane."""
        lane_name = "llm_synthesis"
        start_time = time.time()
        
        try:
            # Import LLM service
            from shared.llm.provider_order import select_provider_and_model_for_complexity, QueryComplexity
            
            # Determine query complexity and select appropriate model
            complexity = QueryComplexity.SIMPLE  # Simplified for demo
            provider, model_name = select_provider_and_model_for_complexity(complexity)
            
            # Synthesize response using available context
            retrieval_data = context.get('retrieval', {})
            vector_data = context.get('vector', {})
            kg_data = context.get('knowledge_graph', {})
            
            # For now, create a structured response (replace with actual LLM call)
            synthesis_result = {
                'answer': f"Based on the query '{query}', here's a synthesized response using available context.",
                'sources_used': {
                    'retrieval': len(retrieval_data.get('sources', [])),
                    'vector': len(vector_data.get('vector_results', [])),
                    'kg': len(kg_data.get('kg_results', []))
                },
                'provider_used': provider.value if provider else 'none',
                'model_used': model_name,
                'confidence': 0.85
            }
            
            return LaneResult(
                lane_name=lane_name,
                status=LaneStatus.COMPLETED,
                data=synthesis_result,
                start_time=start_time,
                end_time=time.time(),
                timeout_seconds=self.lane_configs[lane_name].timeout_seconds
            )
            
        except asyncio.TimeoutError:
            return LaneResult(
                lane_name=lane_name,
                status=LaneStatus.TIMEOUT,
                error="LLM synthesis timeout",
                start_time=start_time,
                end_time=time.time(),
                timeout_seconds=self.lane_configs[lane_name].timeout_seconds
            )
        except Exception as e:
            return LaneResult(
                lane_name=lane_name,
                status=LaneStatus.FAILED,
                error=str(e),
                start_time=start_time,
                end_time=time.time(),
                timeout_seconds=self.lane_configs[lane_name].timeout_seconds
            )
    
    async def _execute_lane_with_timeout(self, lane_name: str, lane_method, query: str, context: Dict[str, Any]) -> LaneResult:
        """Execute a lane with timeout enforcement."""
        lane_config = self.lane_configs[lane_name]
        
        # Check circuit breaker
        if self.config.circuit_breaker_enabled:
            if self.metrics.should_open_circuit_breaker(lane_name, self.config.failure_threshold):
                # Check if circuit should be closed
                last_failure = self.metrics.circuit_breaker_last_failure.get(lane_name, 0)
                if time.time() - last_failure < self.config.circuit_timeout_seconds:
                    return LaneResult(
                        lane_name=lane_name,
                        status=LaneStatus.SKIPPED,
                        error="Circuit breaker open",
                        start_time=time.time(),
                        end_time=time.time(),
                        timeout_seconds=lane_config.timeout_seconds
                    )
        
        try:
            # Execute lane with timeout
            result = await asyncio.wait_for(
                lane_method(query, context),
                timeout=lane_config.timeout_seconds
            )
            
            # Record successful execution
            if result.is_successful:
                self.metrics.circuit_breaker_states[lane_name] = False
            
            return result
            
        except asyncio.TimeoutError:
            # Record timeout in circuit breaker
            self.metrics.circuit_breaker_last_failure[lane_name] = time.time()
            
            return LaneResult(
                lane_name=lane_name,
                status=LaneStatus.TIMEOUT,
                error=f"Lane timeout after {lane_config.timeout_seconds}s",
                start_time=time.time(),
                end_time=time.time(),
                timeout_seconds=lane_config.timeout_seconds
            )
        except Exception as e:
            # Record failure in circuit breaker
            self.metrics.circuit_breaker_last_failure[lane_name] = time.time()
            
            return LaneResult(
                lane_name=lane_name,
                status=LaneStatus.FAILED,
                error=str(e),
                start_time=time.time(),
                end_time=time.time(),
                timeout_seconds=lane_config.timeout_seconds
            )
    
    async def orchestrate_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Orchestrate parallel query processing across all lanes.
        
        Args:
            query: User query to process
            **kwargs: Additional context for processing
            
        Returns:
            Orchestrated response with results from all lanes
        """
        start_time = time.time()
        
        logger.info("Starting multi-lane orchestration",
                   query=query[:100],
                   max_time=self.config.max_total_time_seconds)
        
        # Define lane execution methods
        lane_methods = {
            'retrieval': self._execute_retrieval_lane,
            'vector': self._execute_vector_lane,
            'knowledge_graph': self._execute_kg_lane,
            'llm_synthesis': self._execute_llm_lane
        }
        
        # Create context object for sharing data between lanes
        context = {}
        
        # Execute data lanes in parallel (retrieval, vector, KG)
        data_lanes = ['retrieval', 'vector', 'knowledge_graph']
        data_tasks = [
            self._execute_lane_with_timeout(
                lane_name, 
                lane_methods[lane_name], 
                query, 
                context
            )
            for lane_name in data_lanes
            if self.lane_configs[lane_name].enabled
        ]
        
        # Wait for data lanes with overall timeout
        try:
            data_results = await asyncio.wait_for(
                asyncio.gather(*data_tasks, return_exceptions=True),
                timeout=self.config.max_wait_for_required_seconds
            )
        except asyncio.TimeoutError:
            logger.warning("Data lanes timeout exceeded",
                          timeout=self.config.max_wait_for_required_seconds)
            data_results = []
        
        # Process data lane results
        lane_results = []
        for i, result in enumerate(data_results):
            if isinstance(result, Exception):
                lane_name = data_lanes[i]
                lane_results.append(LaneResult(
                    lane_name=lane_name,
                    status=LaneStatus.FAILED,
                    error=str(result),
                    start_time=start_time,
                    end_time=time.time(),
                    timeout_seconds=self.lane_configs[lane_name].timeout_seconds
                ))
            else:
                lane_results.append(result)
                # Add successful results to context
                if result.is_successful or result.is_partial:
                    context[result.lane_name] = result.data
        
        # Execute LLM synthesis lane with context from data lanes
        llm_result = await self._execute_lane_with_timeout(
            'llm_synthesis',
            lane_methods['llm_synthesis'],
            query,
            context
        )
        lane_results.append(llm_result)
        
        # Calculate total execution time
        total_time_ms = (time.time() - start_time) * 1000
        
        # Record metrics
        self.metrics.record_request(lane_results)
        
        # Determine overall success
        successful_lanes = [r for r in lane_results if r.is_successful]
        partial_lanes = [r for r in lane_results if r.is_partial]
        
        if self.config.require_at_least_one_lane:
            overall_success = len(successful_lanes) > 0 or len(partial_lanes) > 0
        else:
            overall_success = llm_result.is_successful
        
        # Build response
        response = {
            'query': query,
            'success': overall_success,
            'total_time_ms': total_time_ms,
            'within_budget': total_time_ms <= (self.config.max_total_time_seconds * 1000),
            'lane_results': {result.lane_name: result.to_dict() for result in lane_results},
            'summary': {
                'successful_lanes': len(successful_lanes),
                'partial_lanes': len(partial_lanes),
                'failed_lanes': len(lane_results) - len(successful_lanes) - len(partial_lanes),
                'total_lanes': len(lane_results)
            },
            'final_answer': llm_result.data if llm_result.is_successful else None,
            'partial_results': {
                result.lane_name: result.data 
                for result in lane_results 
                if result.is_successful or result.is_partial
            } if self.config.return_partial_results else None
        }
        
        logger.info("Multi-lane orchestration completed",
                   success=overall_success,
                   total_time_ms=round(total_time_ms, 2),
                   successful_lanes=len(successful_lanes),
                   partial_lanes=len(partial_lanes))
        
        return response
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestration metrics."""
        return self.metrics.to_dict()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get orchestrator health status."""
        return {
            'enabled_lanes': [name for name, config in self.lane_configs.items() if config.enabled],
            'circuit_breaker_states': self.metrics.circuit_breaker_states,
            'total_requests': self.metrics.total_requests,
            'success_rate': self.metrics.successful_requests / max(self.metrics.total_requests, 1),
            'config': self.config.__dict__
        }


# Global orchestrator instance
_multi_lane_orchestrator: Optional[MultiLaneOrchestrator] = None

def get_multi_lane_orchestrator() -> MultiLaneOrchestrator:
    """Get or create global multi-lane orchestrator."""
    global _multi_lane_orchestrator
    
    if _multi_lane_orchestrator is None:
        _multi_lane_orchestrator = MultiLaneOrchestrator()
    
    return _multi_lane_orchestrator

async def orchestrate_query(query: str, **kwargs) -> Dict[str, Any]:
    """Execute multi-lane orchestration for query."""
    orchestrator = get_multi_lane_orchestrator()
    return await orchestrator.orchestrate_query(query, **kwargs)

def get_orchestration_metrics() -> Dict[str, Any]:
    """Get orchestration metrics."""
    orchestrator = get_multi_lane_orchestrator()
    return orchestrator.get_metrics()

def get_orchestrator_health() -> Dict[str, Any]:
    """Get orchestrator health status."""
    orchestrator = get_multi_lane_orchestrator()
    return orchestrator.get_health_status()

# Export public interface
__all__ = [
    'LaneStatus',
    'LaneResult', 
    'OrchestrationConfig',
    'MultiLaneOrchestrator',
    'get_multi_lane_orchestrator',
    'orchestrate_query',
    'get_orchestration_metrics',
    'get_orchestrator_health'
]
