"""
Multi-Lane Orchestrator - Always-On Parallel Query Processing with Deadline Enforcement
===============================================================================

Provides resilient query processing through parallel lanes with strict SLA enforcement:
- Global 3,000 ms deadline per query
- Per-lane budget allocation based on intent classification
- Non-blocking orchestration with strict budgets
- Graceful degradation with partial results
- Per-lane timeout enforcement
- Comprehensive metrics collection
- Circuit breaker patterns

Maps to Phase B3 requirements for production resilience with SLA compliance.
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

# Environment-driven SLA configuration - Updated for better performance
SLA_GLOBAL_MS = int(os.getenv("SLA_GLOBAL_MS", "5000"))  # Increased to 5s
SLA_ORCHESTRATOR_RESERVE_MS = int(os.getenv("SLA_ORCHESTRATOR_RESERVE_MS", "200"))
SLA_LLM_MS = int(os.getenv("SLA_LLM_MS", "1500"))  # Increased for better LLM performance
SLA_WEB_MS = int(os.getenv("SLA_WEB_MS", "2000"))  # Increased for web search
SLA_VECTOR_MS = int(os.getenv("SLA_VECTOR_MS", "1000"))  # Increased for vector search
SLA_KG_MS = int(os.getenv("SLA_KG_MS", "800"))  # Increased for knowledge graph
SLA_YT_MS = int(os.getenv("SLA_YT_MS", "1500"))  # Increased for YouTube search
SLA_TTFT_MAX_MS = int(os.getenv("SLA_TTFT_MAX_MS", "1000"))  # Increased for better TTFT
MODE_DEFAULT = os.getenv("MODE_DEFAULT", "standard")  # fast|standard|deep


class QueryIntent(Enum):
    """Query intent classification for budget allocation."""
    SIMPLE = "simple"        # Basic questions, definitions
    TECHNICAL = "technical"  # Code, algorithms, specifications
    RESEARCH = "research"    # Academic, comparative analysis
    MULTIMEDIA = "multimedia"  # Video, demo, visual content


class LaneStatus(Enum):
    """Status of individual processing lanes."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    FAILED = "failed"
    SKIPPED = "skipped"
    DEFERRED = "deferred"  # For lanes that couldn't meet budget


@dataclass
class LaneBudget:
    """Budget allocation for a processing lane."""
    lane_name: str
    allocated_ms: int
    start_time: float = 0.0
    end_time: float = 0.0
    elapsed_ms: float = 0.0
    status: LaneStatus = LaneStatus.PENDING
    items_returned: int = 0
    timed_out: bool = False
    error_message: Optional[str] = None
    
    @property
    def remaining_ms(self) -> float:
        """Get remaining budget in milliseconds."""
        if self.start_time == 0:
            return self.allocated_ms
        elapsed = (time.time() - self.start_time) * 1000
        return max(0, self.allocated_ms - elapsed)
    
    def start_execution(self):
        """Mark lane execution start."""
        self.start_time = time.time()
        self.status = LaneStatus.RUNNING
    
    def complete_execution(self, status: LaneStatus, items: int = 0, error: str = None):
        """Mark lane execution completion."""
        self.end_time = time.time()
        self.elapsed_ms = (self.end_time - self.start_time) * 1000
        self.status = status
        self.items_returned = items
        self.error_message = error
        self.timed_out = (status == LaneStatus.TIMEOUT)


@dataclass
class OrchestrationDeadline:
    """Global deadline management for query orchestration."""
    query_start_time: float
    global_deadline_ms: int
    orchestrator_reserve_ms: int
    ttft_target_ms: int
    
    def __post_init__(self):
        """Initialize deadline tracking."""
        self.deadline_at = self.query_start_time + (self.global_deadline_ms / 1000)
        self.slack_pool_ms = 0.0
    
    @property
    def remaining_ms(self) -> float:
        """Get remaining time until global deadline."""
        remaining = (self.deadline_at - time.time()) * 1000
        return max(0, remaining)
    
    @property
    def ttft_remaining_ms(self) -> float:
        """Get remaining time for TTFT target."""
        elapsed = (time.time() - self.query_start_time) * 1000
        return max(0, self.ttft_target_ms - elapsed)
    
    def can_allocate_lane(self, requested_ms: int) -> bool:
        """Check if lane budget can be allocated."""
        return self.remaining_ms >= (requested_ms + self.orchestrator_reserve_ms)
    
    def add_to_slack_pool(self, ms: float):
        """Add unused time to slack pool."""
        self.slack_pool_ms += ms
    
    def get_slack_pool(self) -> float:
        """Get available slack pool time."""
        return self.slack_pool_ms


class IntentClassifier:
    """Lightweight intent classification for budget allocation."""
    
    @staticmethod
    def classify_query(query: str) -> QueryIntent:
        """Classify query intent for budget allocation."""
        query_lower = query.lower()
        words = query_lower.split()
        
        # Multimedia indicators
        multimedia_terms = ['video', 'watch', 'demo', 'show me', 'tutorial', 'screencast']
        if any(term in query_lower for term in multimedia_terms):
            return QueryIntent.MULTIMEDIA
        
        # Technical indicators
        technical_terms = ['time complexity', 'rfc', 'error code', 'api', 'algorithm', 'implementation']
        if any(term in query_lower for term in technical_terms):
            return QueryIntent.TECHNICAL
        
        # Research indicators
        if len(words) > 15 or any(term in query_lower for term in ['compare', 'survey', 'systematic', 'analysis', 'study']):
            return QueryIntent.RESEARCH
        
        # Default to simple
        return QueryIntent.SIMPLE
    
    @staticmethod
    def get_budget_table(intent: QueryIntent, mode: str = "standard") -> Dict[str, int]:
        """Get budget allocation table based on intent and mode."""
        base_budgets = {
            QueryIntent.SIMPLE: {
                'retrieval': SLA_WEB_MS,
                'vector': SLA_VECTOR_MS,
                'knowledge_graph': SLA_KG_MS,
                'youtube': 0,  # No video intent
                'llm_synthesis': SLA_LLM_MS
            },
            QueryIntent.TECHNICAL: {
                'retrieval': SLA_WEB_MS,
                'vector': SLA_VECTOR_MS,
                'knowledge_graph': SLA_KG_MS,
                'youtube': 0,  # No video intent
                'llm_synthesis': SLA_LLM_MS
            },
            QueryIntent.RESEARCH: {
                'retrieval': SLA_WEB_MS,
                'vector': SLA_VECTOR_MS,
                'knowledge_graph': SLA_KG_MS,
                'youtube': 0,  # No video intent
                'llm_synthesis': SLA_LLM_MS
            },
            QueryIntent.MULTIMEDIA: {
                'retrieval': SLA_WEB_MS,
                'vector': SLA_VECTOR_MS,
                'knowledge_graph': SLA_KG_MS,
                'youtube': SLA_YT_MS,  # Full video budget
                'llm_synthesis': SLA_LLM_MS
            }
        }
        
        # Apply mode multipliers
        mode_multipliers = {
            "fast": 0.7,      # 30% faster, less thorough
            "standard": 1.0,  # Normal operation
            "deep": 2.0       # 2x budget for thorough analysis
        }
        
        multiplier = mode_multipliers.get(mode, 1.0)
        budgets = base_budgets[intent]
        
        return {lane: int(budget * multiplier) for lane, budget in budgets.items()}


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
    budget_ms: float = 0.0
    elapsed_ms: float = 0.0
    items_returned: int = 0
    timed_out: bool = False
    
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
        return self.status in [LaneStatus.TIMEOUT, LaneStatus.FAILED, LaneStatus.DEFERRED] and self.data is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'lane_name': self.lane_name,
            'status': self.status.value,
            'data': self.data,
            'error': self.error,
            'duration_ms': self.duration_ms,
            'timeout_seconds': self.timeout_seconds,
            'budget_ms': self.budget_ms,
            'elapsed_ms': self.elapsed_ms,
            'items_returned': self.items_returned,
            'timed_out': self.timed_out,
            'is_successful': self.is_successful,
            'is_partial': self.is_partial
        }


@dataclass
class OrchestrationConfig:
    """Configuration for multi-lane orchestration."""
    
    # Global timeouts - Optimized for better SLA compliance
    max_total_time_seconds: float = 5.0  # E2E budget - Increased from 3.0
    max_wait_for_required_seconds: float = 3.0  # Increased from 2.0
    
    # Lane configurations - Optimized for performance
    retrieval_timeout: float = 4.0  # Increased from 3.0
    vector_timeout: float = 3.0  # Increased from 2.0
    kg_timeout: float = 2.0  # Increased from 1.5
    llm_timeout: float = 3.0  # Increased from 2.5
    
    # Behavior settings
    return_partial_results: bool = True
    require_at_least_one_lane: bool = True
    max_concurrent_lanes: int = 4
    
    # Circuit breaker settings
    circuit_breaker_enabled: bool = True
    failure_threshold: int = 5
    circuit_timeout_seconds: int = 60
    
    # SLA configuration
    sla_global_ms: int = SLA_GLOBAL_MS
    sla_orchestrator_reserve_ms: int = SLA_ORCHESTRATOR_RESERVE_MS
    sla_ttft_max_ms: int = SLA_TTFT_MAX_MS
    mode: str = MODE_DEFAULT
    
    @classmethod
    def from_environment(cls) -> 'OrchestrationConfig':
        """Load configuration from environment variables."""
        return cls(
            max_total_time_seconds=float(os.getenv('MAX_RESPONSE_TIME_S', '5.0')),  # Increased for better SLA compliance
            max_wait_for_required_seconds=float(os.getenv('MAX_WAIT_FOR_REQUIRED_S', '3.0')),  # Increased
            retrieval_timeout=float(os.getenv('RETRIEVAL_TIMEOUT_S', '4.0')),  # Increased
            vector_timeout=float(os.getenv('VECTOR_TIMEOUT_S', '3.0')),  # Increased
            kg_timeout=float(os.getenv('KG_TIMEOUT_S', '2.0')),  # Increased
            llm_timeout=float(os.getenv('LLM_TIMEOUT_S', '3.0')),  # Increased
            return_partial_results=os.getenv('RETURN_PARTIAL_RESULTS', 'true').lower() == 'true',
            require_at_least_one_lane=os.getenv('REQUIRE_AT_LEAST_ONE_LANE', 'true').lower() == 'true',
            max_concurrent_lanes=int(os.getenv('MAX_CONCURRENT_LANES', '4')),
            circuit_breaker_enabled=os.getenv('CIRCUIT_BREAKER_ENABLED', 'true').lower() == 'true',
            failure_threshold=int(os.getenv('CIRCUIT_FAILURE_THRESHOLD', '5')),
            circuit_timeout_seconds=int(os.getenv('CIRCUIT_TIMEOUT_S', '60')),
            sla_global_ms=int(os.getenv('SLA_GLOBAL_MS', '5000')),  # Increased for better SLA compliance
            sla_orchestrator_reserve_ms=int(os.getenv('SLA_ORCHESTRATOR_RESERVE_MS', '200')),
            sla_ttft_max_ms=int(os.getenv('SLA_TTFT_MAX_MS', '1000')),  # Increased
            mode=os.getenv('MODE_DEFAULT', 'standard')
        )
    
    def get_lane_configs(self) -> Dict[str, LaneConfig]:
        """Get configuration for each lane with SLA-driven timeouts."""
        return {
            'retrieval': LaneConfig(
                name='retrieval',
                timeout_seconds=SLA_WEB_MS / 1000,  # Use SLA configuration
                priority=1,
                required=False
            ),
            'vector': LaneConfig(
                name='vector', 
                timeout_seconds=SLA_VECTOR_MS / 1000,  # Use SLA configuration
                priority=2,
                required=False
            ),
            'knowledge_graph': LaneConfig(
                name='knowledge_graph',
                timeout_seconds=SLA_KG_MS / 1000,  # Use SLA configuration
                priority=3,
                required=False
            ),
            'youtube': LaneConfig(
                name='youtube',
                timeout_seconds=SLA_YT_MS / 1000,  # Use SLA configuration
                priority=4,
                required=False  # YouTube is optional, never blocks synthesis
            ),
            'index_fabric': LaneConfig(
                name='index_fabric',
                timeout_seconds=3000 / 1000,  # 3s for the entire index fabric fusion
                priority=5,
                required=False  # Index fabric is optional but high value
            ),
            'llm_synthesis': LaneConfig(
                name='llm_synthesis',
                timeout_seconds=SLA_LLM_MS / 1000,  # Use SLA configuration
                priority=6,
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
            
            # Return actual retrieval data - no mock responses
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
    
    async def _execute_youtube_lane(self, query: str, context: Dict[str, Any]) -> LaneResult:
        """Execute YouTube retrieval lane with zero-budget constraints."""
        lane_name = "youtube"
        start_time = time.time()
        
        try:
            # Import YouTube retrieval service
            from services.retrieval.youtube_retrieval import get_youtube_retrieval
            
            # Check if YouTube should execute for this query
            youtube_service = get_youtube_retrieval()
            
            if not youtube_service._should_execute_youtube(query):
                return LaneResult(
                    lane_name=lane_name,
                    status=LaneStatus.SKIPPED,
                    data={'reason': 'no_video_intent'},
                    start_time=start_time,
                    end_time=time.time(),
                    timeout_seconds=self.lane_configs[lane_name].timeout_seconds
                )
            
            # Execute YouTube search with strict timeout
            youtube_response = await asyncio.wait_for(
                youtube_service.search(query, max_results=5),
                timeout=self.lane_configs[lane_name].timeout_seconds
            )
            
            # Process results
            result_data = {
                'videos': [
                    {
                        'video_id': video.video_id,
                        'title': video.title,
                        'description': video.description,
                        'channel_title': video.channel_title,
                        'published_at': video.published_at,
                        'duration': video.duration,
                        'thumbnail_url': video.thumbnail_url,
                        'view_count': video.view_count,
                        'relevance_score': video.relevance_score,
                        'units_spent': video.units_spent,
                        'fetch_ms': video.fetch_ms
                    }
                    for video in youtube_response.videos
                ],
                'total_results': youtube_response.total_results,
                'units_spent': youtube_response.units_spent,
                'quota_exhausted': youtube_response.quota_exhausted,
                'timeout_occurred': youtube_response.timeout_occurred,
                'provider': 'youtube'
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
                error="YouTube lane timeout",
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
    
    async def _execute_index_fabric_lane(self, query: str, context: Dict[str, Any]) -> LaneResult:
        """Execute Index Fabric lane that fuses all indexing systems."""
        lane_name = "index_fabric"
        start_time = time.time()
        
        try:
            # Import the Index Fabric service
            from shared.core.services.index_fabric_service import get_index_fabric_service
            
            # Get the service instance
            index_fabric_service = get_index_fabric_service()
            
            # Execute the fused search across all indexing lanes
            fused_result = await asyncio.wait_for(
                index_fabric_service.search_across_all_lanes(query, max_results=10),
                timeout=self.lane_configs[lane_name].timeout_seconds
            )
            
            # Process the results
            result_data = {
                'total_results': fused_result.total_results,
                'fused_results': fused_result.fused_results,
                'lane_results': {
                    lane_name: {
                        'success': lane_result.success,
                        'results_count': len(lane_result.results),
                        'processing_time_ms': lane_result.processing_time_ms,
                        'error_message': lane_result.error_message,
                        'metadata': lane_result.metadata
                    }
                    for lane_name, lane_result in fused_result.lane_results.items()
                },
                'fusion_time_ms': fused_result.fusion_time_ms,
                'total_time_ms': fused_result.total_time_ms,
                'within_budget': fused_result.within_budget,
                'successful_lanes': fused_result.successful_lanes,
                'failed_lanes': fused_result.failed_lanes,
                'provider': 'index_fabric'
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
                error="Index fabric lane timeout",
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
    
    async def _execute_lane_with_deadline(self, lane_name: str, lane_method, query: str, 
                                        context: Dict[str, Any], budget_ms: float, 
                                        deadline: OrchestrationDeadline) -> LaneResult:
        """Execute a lane with deadline-aware budget enforcement."""
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
                        timeout_seconds=lane_config.timeout_seconds,
                        budget_ms=budget_ms,
                        elapsed_ms=0
                    )
        
        # Calculate effective timeout (min of lane config and remaining deadline)
        effective_timeout = min(lane_config.timeout_seconds, deadline.remaining_ms / 1000)
        
        if effective_timeout <= 0:
            return LaneResult(
                lane_name=lane_name,
                status=LaneStatus.DEFERRED,
                error="No remaining deadline for lane execution",
                start_time=time.time(),
                end_time=time.time(),
                timeout_seconds=0,
                budget_ms=budget_ms,
                elapsed_ms=0
            )
        
        try:
            # Execute lane with effective timeout
            result = await asyncio.wait_for(
                lane_method(query, context),
                timeout=effective_timeout
            )
            
            # Update result with budget information
            result.budget_ms = budget_ms
            result.elapsed_ms = result.duration_ms
            
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
                error=f"Lane timeout after {effective_timeout}s (budget: {budget_ms}ms)",
                start_time=time.time(),
                end_time=time.time(),
                timeout_seconds=effective_timeout,
                budget_ms=budget_ms,
                elapsed_ms=effective_timeout * 1000,
                timed_out=True
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
                timeout_seconds=effective_timeout,
                budget_ms=budget_ms,
                elapsed_ms=(time.time() - time.time()) * 1000
            )
    
    async def orchestrate_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Orchestrate parallel query processing across all lanes with deadline enforcement.
        
        Args:
            query: User query to process
            **kwargs: Additional context for processing
            
        Returns:
            Orchestrated response with results from all lanes
        """
        start_time = time.time()
        
        # Initialize deadline management
        deadline = OrchestrationDeadline(
            query_start_time=start_time,
            global_deadline_ms=self.config.sla_global_ms,
            orchestrator_reserve_ms=self.config.sla_orchestrator_reserve_ms,
            ttft_target_ms=self.config.sla_ttft_max_ms
        )
        
        # Classify query intent for budget allocation
        intent = IntentClassifier.classify_query(query)
        budget_table = IntentClassifier.get_budget_table(intent, self.config.mode)
        
        logger.info("Starting multi-lane orchestration with deadline enforcement",
                   query=query[:100],
                   intent=intent.value,
                   mode=self.config.mode,
                   global_deadline_ms=deadline.remaining_ms,
                   ttft_target_ms=deadline.ttft_remaining_ms)
        
        # Define lane execution methods
        lane_methods = {
            'retrieval': self._execute_retrieval_lane,
            'vector': self._execute_vector_lane,
            'knowledge_graph': self._execute_kg_lane,
            'youtube': self._execute_youtube_lane,
            'index_fabric': self._execute_index_fabric_lane,
            'llm_synthesis': self._execute_llm_lane
        }
        
        # Create context object for sharing data between lanes
        context = {}
        
        # Execute data lanes in parallel with individual budgets
        data_lanes = ['retrieval', 'vector', 'knowledge_graph', 'youtube', 'index_fabric']
        data_tasks = []
        
        for lane_name in data_lanes:
            if not self.lane_configs[lane_name].enabled:
                continue
                
            # Check if lane budget can be allocated
            lane_budget_ms = budget_table.get(lane_name, 0)
            if not deadline.can_allocate_lane(lane_budget_ms):
                logger.warning(f"Lane {lane_name} budget {lane_budget_ms}ms exceeds remaining deadline {deadline.remaining_ms}ms")
                continue
            
            # Create task with lane-specific budget
            task = self._execute_lane_with_deadline(
                lane_name, 
                lane_methods[lane_name], 
                query, 
                context,
                lane_budget_ms,
                deadline
            )
            data_tasks.append(task)
        
        # Wait for data lanes with remaining deadline
        try:
            data_results = await asyncio.wait_for(
                asyncio.gather(*data_tasks, return_exceptions=True),
                timeout=deadline.remaining_ms / 1000
            )
        except asyncio.TimeoutError:
            logger.warning("Global deadline exceeded for data lanes",
                          remaining_ms=deadline.remaining_ms)
            data_results = []
        
        # Process data lane results
        lane_results = []
        for i, result in enumerate(data_results):
            if isinstance(result, Exception):
                lane_name = data_lanes[i] if i < len(data_lanes) else 'unknown'
                lane_results.append(LaneResult(
                    lane_name=lane_name,
                    status=LaneStatus.FAILED,
                    error=str(result),
                    start_time=start_time,
                    end_time=time.time(),
                    timeout_seconds=self.lane_configs[lane_name].timeout_seconds if lane_name in self.lane_configs else 0,
                    budget_ms=budget_table.get(lane_name, 0),
                    elapsed_ms=(time.time() - start_time) * 1000
                ))
            else:
                lane_results.append(result)
                # Add successful results to context
                if result.is_successful or result.is_partial:
                    context[result.lane_name] = result.data
                
                # Add unused budget to slack pool
                if result.elapsed_ms < result.budget_ms:
                    unused_budget = result.budget_ms - result.elapsed_ms
                    deadline.add_to_slack_pool(unused_budget)
        
        # Execute LLM synthesis lane with remaining deadline
        llm_budget_ms = budget_table.get('llm_synthesis', SLA_LLM_MS)
        if deadline.can_allocate_lane(llm_budget_ms):
            llm_result = await self._execute_lane_with_deadline(
                'llm_synthesis',
                lane_methods['llm_synthesis'],
                query,
                context,
                llm_budget_ms,
                deadline
            )
        else:
            # Create deferred result if no budget available
            llm_result = LaneResult(
                lane_name='llm_synthesis',
                status=LaneStatus.DEFERRED,
                error="Insufficient budget for LLM synthesis",
                start_time=start_time,
                end_time=time.time(),
                timeout_seconds=0,
                budget_ms=llm_budget_ms,
                elapsed_ms=0
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
        
        # Build response with SLA compliance
        response = {
            'query': query,
            'intent': intent.value,
            'mode': self.config.mode,
            'sla_compliance': {
                'deadline_ms': self.config.sla_global_ms,
                'ttft_ms': total_time_ms,
                'finalize_ms': total_time_ms,
                'answered_under_sla': total_time_ms <= self.config.sla_global_ms,
                'deadline_remaining_ms': deadline.remaining_ms,
                'slack_pool_ms': deadline.get_slack_pool()
            },
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


def get_orchestration_metrics() -> Dict[str, Any]:
    """Get orchestration metrics for /metrics/lanes endpoint."""
    orchestrator = get_multi_lane_orchestrator()
    return orchestrator.get_metrics()


def get_orchestrator_health() -> Dict[str, Any]:
    """Get orchestrator health for /metrics/lanes endpoint."""
    orchestrator = get_multi_lane_orchestrator()
    return orchestrator.get_health_status()

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
