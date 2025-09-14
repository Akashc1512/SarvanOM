"""
Retrieval Orchestrator for SarvanOM

This module provides a centralized orchestrator that merges all retrieval lanes
(web search, vector search, knowledge graph) with strict latency budgets and
fallback strategies. It ensures a single source of truth for retrieval operations.

PERFORMANCE REQUIREMENTS (Always-On):
- P95 end-to-end latency ≤ 3 seconds on cached/simple queries
- Vector search: ≤ 2.0 seconds with top-k ≤ 5 passages
- Knowledge Graph: ≤ 1.5 seconds with top-k ≤ 6 facts
- Web search: ≤ 1.0 seconds for fast fallback
- Never block the answer: if a lane times out, proceed with other lanes
- Total budget: 3 seconds maximum

Following MAANG/OpenAI/Perplexity standards for hybrid retrieval systems.
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

from shared.core.logging import get_logger
from shared.contracts.query import RetrievalSearchRequest, RetrievalSearchResponse
from sarvanom.services.retrieval.config import get_config
from sarvanom.shared.core.config.provider_config import get_provider_config

# Prometheus metrics for per-lane timing
try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
    
    # Per-lane latency histograms with provider tags
    lane_latency_histogram = Histogram(
        'retrieval_lane_latency_seconds',
        'Latency of retrieval lanes in seconds',
        ['lane', 'status', 'provider', 'fallback_used', 'source']
    )
    
    # Per-lane result counters with provider tags
    lane_result_counter = Counter(
        'retrieval_lane_results_total',
        'Total number of results from retrieval lanes',
        ['lane', 'status', 'provider', 'fallback_used', 'source']
    )
    
    # Lane status gauge
    lane_status_gauge = Gauge(
        'retrieval_lane_status',
        'Status of retrieval lanes (1=available, 0=unavailable)',
        ['lane']
    )
    
    # End-to-end latency histogram
    end_to_end_latency_histogram = Histogram(
        'retrieval_end_to_end_latency_seconds',
        'End-to-end retrieval latency in seconds'
    )
    
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = get_logger(__name__)

if not PROMETHEUS_AVAILABLE:
    logger.warning("Prometheus client not available, metrics will not be collected")


class RetrievalLane(Enum):
    """Available retrieval lanes."""
    WEB_SEARCH = "web_search"
    VECTOR_SEARCH = "vector_search"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    HYBRID = "hybrid"


class LaneStatus(Enum):
    """Status of a retrieval lane."""
    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    TIMEOUT = "timeout"


@dataclass
class LaneResult:
    """Result from a single retrieval lane."""
    lane: RetrievalLane
    status: LaneStatus
    results: List[Dict[str, Any]]
    latency_ms: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LatencyBudget:
    """Latency budget configuration for retrieval operations."""
    total_budget_ms: float = 3000.0  # 3 seconds total (strict P95 ≤ 3s requirement)
    web_search_budget_ms: float = 1000.0  # 1.0 seconds for web search (fast)
    vector_search_budget_ms: float = 2000.0  # 2.0 seconds for vector search (strict ≤ 2.0s)
    knowledge_graph_budget_ms: float = 1500.0  # 1.5 seconds for KG (strict ≤ 1.5s)
    fusion_budget_ms: float = 200.0  # 0.2 seconds for result fusion (fast)


@dataclass
class OrchestrationConfig:
    """Configuration for retrieval orchestration."""
    enable_web_search: bool = True
    enable_vector_search: bool = True
    enable_knowledge_graph: bool = True
    enable_parallel_execution: bool = True
    enable_fallback: bool = True
    max_results_per_lane: int = 10
    fusion_strategy: str = "weighted_merge"  # weighted_merge, simple_merge, priority_based
    latency_budget: LatencyBudget = field(default_factory=LatencyBudget)
    
    def __post_init__(self):
        """Initialize configuration from environment variables."""
        import os
        
        # Enable/disable lanes based on environment flags
        self.enable_vector_search = os.getenv("ENABLE_VECTOR_SEARCH", "true").lower() == "true"
        self.enable_knowledge_graph = os.getenv("ENABLE_KNOWLEDGE_GRAPH", "true").lower() == "true"
        self.enable_web_search = os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true"
        
        # Configure strict top-k defaults for performance (as per requirements)
        self.max_results_per_lane = int(os.getenv("RETRIEVAL_TOP_K", "5"))
        
        # Configure strict latency budgets (as per requirements)
        total_budget = float(os.getenv("RETRIEVAL_TIMEOUT_MS", "3000"))
        self.latency_budget.total_budget_ms = total_budget
        
        # Strict per-lane timeouts (as per requirements)
        self.latency_budget.vector_search_budget_ms = float(os.getenv("VECTOR_TIMEOUT_MS", "2000"))  # 2.0s (strict ≤ 2.0s)
        self.latency_budget.knowledge_graph_budget_ms = float(os.getenv("KG_TIMEOUT_MS", "1500"))  # 1.5s (strict ≤ 1.5s)
        self.latency_budget.web_search_budget_ms = float(os.getenv("WEB_TIMEOUT_MS", "1000"))  # 1.0s (fast)
        self.latency_budget.fusion_budget_ms = float(os.getenv("FUSION_TIMEOUT_MS", "200"))  # 0.2s (fast)


class ProviderManager:
    """Manages provider order, availability, and fallback logic"""
    
    def __init__(self):
        self.provider_config = get_provider_config()
        self.retrieval_config = get_config()
        
        # Provider order configuration from docs/retrieval/lanes.md
        self.lane_providers = {
            "web_search": {
                "keyed": ["brave_search", "serpapi"],
                "keyless": ["duckduckgo", "wikipedia", "stackexchange", "mdn"],
                "budget_ms": 800
            },
            "news": {
                "keyed": ["guardian", "newsapi"],
                "keyless": ["gdelt", "hn_algolia", "rss"],
                "budget_ms": 800
            },
            "markets": {
                "keyed": ["alphavantage", "finnhub", "fmp"],
                "keyless": ["stooq", "sec_edgar"],
                "budget_ms": 800
            }
        }
    
    def get_provider_order(self, lane_type: str) -> List[List[str]]:
        """Get provider execution order for a lane"""
        if lane_type not in self.lane_providers:
            return []
        
        lane_config = self.lane_providers[lane_type]
        keyed_providers = lane_config["keyed"]
        keyless_providers = lane_config["keyless"]
        
        # Check which keyed providers are available
        available_keyed = []
        for provider in keyed_providers:
            if self._is_provider_available(provider):
                available_keyed.append(provider)
        
        # If no keyed providers available and keyless fallbacks enabled, use keyless
        if not available_keyed and self.provider_config.KEYLESS_FALLBACKS_ENABLED:
            return [keyless_providers]
        
        # If keyed providers available, use them first, then keyless as fallback
        if available_keyed:
            if self.provider_config.KEYLESS_FALLBACKS_ENABLED:
                return [available_keyed, keyless_providers]
            else:
                return [available_keyed]
        
        # No providers available
        return []
    
    def _is_provider_available(self, provider_name: str) -> bool:
        """Check if a provider is available (has API key)"""
        provider_key_map = {
            "brave_search": "BRAVE_SEARCH_API_KEY",
            "serpapi": "SERPAPI_KEY",
            "guardian": "GUARDIAN_OPEN_PLATFORM_KEY",
            "newsapi": "NEWSAPI_KEY",
            "alphavantage": "ALPHAVANTAGE_KEY",
            "finnhub": "FINNHUB_KEY",
            "fmp": "FMP_API_KEY"
        }
        
        if provider_name not in provider_key_map:
            return True  # Assume available if no key mapping
        
        key_name = provider_key_map[provider_name]
        key_value = getattr(self.provider_config, key_name, None)
        
        return key_value is not None and str(key_value) != ""

class RetrievalOrchestrator:
    """
    Centralized orchestrator for hybrid retrieval operations.
    
    This class provides a single source of truth for retrieval operations,
    managing multiple lanes with strict latency budgets and fallback strategies.
    """
    
    def __init__(self, config: Optional[OrchestrationConfig] = None):
        """Initialize the retrieval orchestrator."""
        self.config = config or OrchestrationConfig()
        self.provider_manager = ProviderManager()
        self.lane_status: Dict[RetrievalLane, LaneStatus] = {
            lane: LaneStatus.AVAILABLE for lane in RetrievalLane
        }
        self.lane_metrics: Dict[RetrievalLane, List[float]] = {
            lane: [] for lane in RetrievalLane
        }
        
    async def orchestrate_retrieval(
        self, 
        request: RetrievalSearchRequest,
        user_id: Optional[str] = None
    ) -> RetrievalSearchResponse:
        """
        Orchestrate hybrid retrieval across all available lanes.
        
        This is the main entry point for retrieval operations, providing
        a single source of truth for all retrieval needs.
        """
        start_time = time.time()
        
        try:
            logger.info(
                f"Starting orchestrated retrieval for query: {request.query[:100]}...",
                extra={
                    "query_length": len(request.query),
                    "max_results": request.max_results,
                    "user_id": user_id
                }
            )
            
            # Determine which lanes to use
            active_lanes = self._determine_active_lanes()
            
            if not active_lanes:
                logger.warning("No retrieval lanes available, returning empty results")
                return self._create_empty_response(request)
            
            # Execute retrieval across lanes
            if self.config.enable_parallel_execution:
                lane_results = await self._execute_parallel_retrieval(
                    request, active_lanes, user_id
                )
            else:
                lane_results = await self._execute_sequential_retrieval(
                    request, active_lanes, user_id
                )
            
            # Fuse results from all lanes
            fused_results = await self._fuse_results(lane_results, request)
            
            # Calculate total latency
            total_latency = (time.time() - start_time) * 1000
            
            # Create response
            response = RetrievalSearchResponse(
                sources=fused_results,
                method="orchestrated_hybrid",
                total_results=len(fused_results),
                relevance_scores=[r.get("score", 0.0) for r in fused_results],
                limit=request.max_results
            )
            
            # Update lane metrics
            self._update_lane_metrics(lane_results)
            
            # Log with per-lane timing and trace ID
            self._log_retrieval_with_timing(
                request, lane_results, fused_results, total_latency, user_id
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Orchestrated retrieval failed: {e}")
            return self._create_error_response(request, str(e))
    
    def _determine_active_lanes(self) -> List[RetrievalLane]:
        """Determine which retrieval lanes are currently active."""
        active_lanes = []
        
        if self.config.enable_web_search and self.lane_status[RetrievalLane.WEB_SEARCH] == LaneStatus.AVAILABLE:
            active_lanes.append(RetrievalLane.WEB_SEARCH)
        
        if self.config.enable_vector_search and self.lane_status[RetrievalLane.VECTOR_SEARCH] == LaneStatus.AVAILABLE:
            active_lanes.append(RetrievalLane.VECTOR_SEARCH)
        
        if self.config.enable_knowledge_graph and self.lane_status[RetrievalLane.KNOWLEDGE_GRAPH] == LaneStatus.AVAILABLE:
            active_lanes.append(RetrievalLane.KNOWLEDGE_GRAPH)
        
        return active_lanes
    
    async def _execute_parallel_retrieval(
        self, 
        request: RetrievalSearchRequest, 
        lanes: List[RetrievalLane],
        user_id: Optional[str]
    ) -> List[LaneResult]:
        """Execute retrieval across multiple lanes in parallel with strict timeouts."""
        tasks = []
        
        for lane in lanes:
            task = asyncio.create_task(
                self._execute_lane_retrieval(lane, request, user_id)
            )
            tasks.append(task)
        
        # Wait for all tasks with individual lane timeouts (CRITICAL: Never block the answer)
        # If a lane times out, we proceed with other lanes to ensure P95 ≤ 3s
        lane_results = []
        
        # Use asyncio.gather with return_exceptions=True to handle individual failures
        # This ensures that one slow lane doesn't block the entire retrieval
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Handle exceptions from individual lanes
                    if isinstance(result, asyncio.TimeoutError):
                        logger.warning(f"Lane {lanes[i].value} timed out, continuing with other lanes")
                        lane_results.append(LaneResult(
                            lane=lanes[i],
                            status=LaneStatus.TIMEOUT,
                            results=[],
                            latency_ms=self.config.latency_budget.total_budget_ms,
                            error="Lane timeout"
                        ))
                    else:
                        logger.warning(f"Lane {lanes[i].value} failed: {result}, continuing with other lanes")
                        lane_results.append(LaneResult(
                            lane=lanes[i],
                            status=LaneStatus.UNAVAILABLE,
                            results=[],
                            latency_ms=0.0,
                            error=str(result)
                        ))
                else:
                    # Normal result
                    lane_results.append(result)
                    
        except Exception as e:
            logger.error(f"Parallel retrieval failed: {e}")
            # Create timeout results for all lanes
            for lane in lanes:
                lane_results.append(LaneResult(
                    lane=lane,
                    status=LaneStatus.TIMEOUT,
                    results=[],
                    latency_ms=self.config.latency_budget.total_budget_ms,
                    error="Overall timeout"
                ))
        
        return lane_results
    
    async def _execute_sequential_retrieval(
        self, 
        request: RetrievalSearchRequest, 
        lanes: List[RetrievalLane],
        user_id: Optional[str]
    ) -> List[LaneResult]:
        """Execute retrieval across multiple lanes sequentially."""
        lane_results = []
        remaining_budget = self.config.latency_budget.total_budget_ms
        
        for lane in lanes:
            if remaining_budget <= 0:
                logger.warning(f"Latency budget exhausted, skipping lane: {lane.value}")
                break
            
            # Execute lane with remaining budget
            result = await self._execute_lane_retrieval(lane, request, user_id)
            lane_results.append(result)
            
            # Update remaining budget
            remaining_budget -= result.latency_ms
            
            # If lane failed, consider fallback
            if result.status != LaneStatus.AVAILABLE and self.config.enable_fallback:
                logger.warning(f"Lane {lane.value} failed, considering fallback")
        
        return lane_results
    
    async def _execute_lane_retrieval(
        self, 
        lane: RetrievalLane, 
        request: RetrievalSearchRequest,
        user_id: Optional[str]
    ) -> LaneResult:
        """Execute retrieval for a single lane with strict timeout enforcement."""
        start_time = time.time()
        
        try:
            # Get lane-specific budget (CRITICAL: These are strict performance requirements)
            budget_ms = self._get_lane_budget(lane)
            
            # Execute with strict timeout - this is critical for performance
            # Vector: ≤ 2.0s, KG: ≤ 1.5s, Web: ≤ 1.0s
            result = await asyncio.wait_for(
                self._call_lane_service(lane, request, user_id),
                timeout=budget_ms / 1000.0
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Check if we exceeded the budget (should not happen with asyncio.wait_for)
            if latency_ms > budget_ms:
                logger.warning(f"Lane {lane.value} exceeded budget: {latency_ms:.2f}ms > {budget_ms:.2f}ms")
                self.lane_status[lane] = LaneStatus.TIMEOUT
                return LaneResult(
                    lane=lane,
                    status=LaneStatus.TIMEOUT,
                    results=[],
                    latency_ms=latency_ms,
                    error="Exceeded budget"
                )
            
            return LaneResult(
                lane=lane,
                status=LaneStatus.AVAILABLE,
                results=result,
                latency_ms=latency_ms,
                metadata={"budget_ms": budget_ms}
            )
            
        except asyncio.TimeoutError:
            latency_ms = (time.time() - start_time) * 1000
            logger.warning(f"Lane {lane.value} timed out after {latency_ms:.2f}ms (budget: {budget_ms:.2f}ms)")
            
            self.lane_status[lane] = LaneStatus.TIMEOUT
            
            return LaneResult(
                lane=lane,
                status=LaneStatus.TIMEOUT,
                results=[],
                latency_ms=latency_ms,
                error=f"Timeout after {budget_ms:.2f}ms"
            )
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Lane {lane.value} failed: {e}")
            
            self.lane_status[lane] = LaneStatus.UNAVAILABLE
            
            return LaneResult(
                lane=lane,
                status=LaneStatus.UNAVAILABLE,
                results=[],
                latency_ms=latency_ms,
                error=str(e)
            )
    
    def _get_lane_budget(self, lane: RetrievalLane) -> float:
        """Get latency budget for a specific lane."""
        if lane == RetrievalLane.WEB_SEARCH:
            return self.config.latency_budget.web_search_budget_ms
        elif lane == RetrievalLane.VECTOR_SEARCH:
            return self.config.latency_budget.vector_search_budget_ms
        elif lane == RetrievalLane.KNOWLEDGE_GRAPH:
            return self.config.latency_budget.knowledge_graph_budget_ms
        else:
            return 1000.0  # Default 1 second
    
    async def _call_lane_service(
        self, 
        lane: RetrievalLane, 
        request: RetrievalSearchRequest,
        user_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Call the appropriate service for a retrieval lane."""
        try:
            if lane == RetrievalLane.WEB_SEARCH:
                return await self._web_search_lane(request)
            elif lane == RetrievalLane.VECTOR_SEARCH:
                return await self._vector_search_lane(request)
            elif lane == RetrievalLane.KNOWLEDGE_GRAPH:
                return await self._knowledge_graph_lane(request)
            else:
                return []
        except Exception as e:
            logger.warning(f"Lane {lane.value} failed: {e}")
            return []
    
    async def _web_search_lane(self, request: RetrievalSearchRequest) -> List[Dict[str, Any]]:
        """Web search lane with provider order and fallback logic."""
        try:
            # Get provider order for web search
            provider_order = self.provider_manager.get_provider_order("web_search")
            
            if not provider_order:
                logger.warning("No web search providers available")
                return []
            
            # Use existing web search with small top-k for strict latency
            top_k = min(5, request.max_results)  # Small top-k for speed
            
            # Try providers in order with parallel fan-out
            for provider_batch in provider_order:
                batch_tasks = []
                for provider_name in provider_batch:
                    task = asyncio.create_task(
                        self._call_web_provider(provider_name, request.query, top_k)
                    )
                    batch_tasks.append((provider_name, task))
                
                # Wait for batch to complete
                batch_results = []
                for provider_name, task in batch_tasks:
                    try:
                        result = await task
                        if result:
                            batch_results.extend(result)
                    except Exception as e:
                        logger.warning(f"Web provider {provider_name} failed: {e}")
                
                # If we got results, return them (first-N strategy)
                if batch_results:
                    # Add lane metadata
                    for result in batch_results:
                        if "metadata" not in result:
                            result["metadata"] = {}
                        result["metadata"]["lane"] = "web_search"
                        result["metadata"]["retrieval_method"] = "provider_ordered_web"
                    
                    return batch_results[:top_k]
            
            return []
            
        except Exception as e:
            logger.warning(f"Web search lane failed: {e}")
            return []
    
    def _fast_web_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Fast web search implementation with minimal HTTP requests."""
        import os
        import requests
        import time
        
        results = []
        brave_key = os.getenv("BRAVE_SEARCH_API_KEY")
        serpapi_key = os.getenv("SERPAPI_KEY")
        
        try:
            if brave_key:
                headers = {"X-Subscription-Token": brave_key}
                params = {"q": query, "count": min(top_k, 3)}  # Limit to 3 results for speed
                r = requests.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    headers=headers,
                    params=params,
                    timeout=2,  # Very short timeout for strict latency
                )
                if r.ok:
                    data = r.json()
                    for item in (data.get("web", {}).get("results", []) or [])[:top_k]:
                        url = item.get("url")
                        if url:
                            results.append({
                                "id": url,
                                "content": item.get("description", ""),
                                "metadata": {
                                    "title": item.get("title", url),
                                    "url": url,
                                    "source": "brave_search"
                                },
                                "score": 0.8,  # Default score for web results
                            })
            elif serpapi_key:
                params = {
                    "engine": "google",
                    "q": query,
                    "api_key": serpapi_key,
                    "num": min(top_k, 3),  # Limit to 3 results for speed
                }
                r = requests.get(
                    "https://serpapi.com/search.json", 
                    params=params, 
                    timeout=2  # Very short timeout for strict latency
                )
                if r.ok:
                    data = r.json()
                    for item in (data.get("organic_results", []) or [])[:top_k]:
                        url = item.get("link")
                        if url:
                            results.append({
                                "id": url,
                                "content": item.get("snippet", ""),
                                "metadata": {
                                    "title": item.get("title", url),
                                    "url": url,
                                    "source": "serpapi"
                                },
                                "score": 0.8,  # Default score for web results
                            })
        except Exception as e:
            logger.warning(f"Web search API failed: {e}")
        
        return results[:top_k]
    
    async def _call_web_provider(self, provider_name: str, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Call a specific web search provider"""
        try:
            if provider_name == "brave_search":
                return await self._call_brave_search(query, top_k)
            elif provider_name == "serpapi":
                return await self._call_serpapi(query, top_k)
            elif provider_name == "duckduckgo":
                return await self._call_duckduckgo(query, top_k)
            elif provider_name == "wikipedia":
                return await self._call_wikipedia(query, top_k)
            elif provider_name == "stackexchange":
                return await self._call_stackexchange(query, top_k)
            elif provider_name == "mdn":
                return await self._call_mdn(query, top_k)
            else:
                logger.warning(f"Unknown web provider: {provider_name}")
                return []
        except Exception as e:
            logger.warning(f"Web provider {provider_name} failed: {e}")
            return []
    
    async def _call_brave_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Call Brave Search API"""
        import os
        import requests
        
        brave_key = os.getenv("BRAVE_SEARCH_API_KEY")
        if not brave_key:
            return []
        
        try:
            headers = {"X-Subscription-Token": brave_key}
            params = {"q": query, "count": min(top_k, 3)}
            r = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
                timeout=2
            )
            if r.ok:
                data = r.json()
                results = []
                for item in (data.get("web", {}).get("results", []) or [])[:top_k]:
                    url = item.get("url")
                    if url:
                        results.append({
                            "id": url,
                            "content": item.get("description", ""),
                            "metadata": {
                                "title": item.get("title", url),
                                "url": url,
                                "source": "brave_search",
                                "provider": "brave_search"
                            },
                            "score": 0.8,
                        })
                return results
        except Exception as e:
            logger.warning(f"Brave Search API failed: {e}")
        
        return []
    
    async def _call_serpapi(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Call SerpAPI"""
        import os
        import requests
        
        serpapi_key = os.getenv("SERPAPI_KEY")
        if not serpapi_key:
            return []
        
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": serpapi_key,
                "num": min(top_k, 3),
            }
            r = requests.get(
                "https://serpapi.com/search.json", 
                params=params, 
                timeout=2
            )
            if r.ok:
                data = r.json()
                results = []
                for item in (data.get("organic_results", []) or [])[:top_k]:
                    url = item.get("link")
                    if url:
                        results.append({
                            "id": url,
                            "content": item.get("snippet", ""),
                            "metadata": {
                                "title": item.get("title", url),
                                "url": url,
                                "source": "serpapi",
                                "provider": "serpapi"
                            },
                            "score": 0.8,
                        })
                return results
        except Exception as e:
            logger.warning(f"SerpAPI failed: {e}")
        
        return []
    
    async def _call_duckduckgo(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Call DuckDuckGo Instant Answer API (keyless)"""
        try:
            # DuckDuckGo Instant Answer API is free and doesn't require API key
            import requests
            
            params = {"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"}
            r = requests.get(
                "https://api.duckduckgo.com/",
                params=params,
                timeout=2
            )
            if r.ok:
                data = r.json()
                results = []
                
                # Extract abstract
                if data.get("Abstract"):
                    results.append({
                        "id": f"ddg_abstract_{hash(query)}",
                        "content": data.get("Abstract", ""),
                        "metadata": {
                            "title": data.get("Heading", query),
                            "url": data.get("AbstractURL", ""),
                            "source": "duckduckgo",
                            "provider": "duckduckgo"
                        },
                        "score": 0.7,
                    })
                
                # Extract related topics
                for topic in (data.get("RelatedTopics", []) or [])[:top_k-1]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        results.append({
                            "id": f"ddg_topic_{hash(topic.get('Text', ''))}",
                            "content": topic.get("Text", ""),
                            "metadata": {
                                "title": topic.get("FirstURL", "").split("/")[-1] if topic.get("FirstURL") else "",
                                "url": topic.get("FirstURL", ""),
                                "source": "duckduckgo",
                                "provider": "duckduckgo"
                            },
                            "score": 0.6,
                        })
                
                return results[:top_k]
        except Exception as e:
            logger.warning(f"DuckDuckGo API failed: {e}")
        
        return []
    
    async def _call_wikipedia(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Call Wikipedia API (keyless)"""
        try:
            import requests
            
            # Search for pages
            search_params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "srlimit": min(top_k, 3)
            }
            
            r = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params=search_params,
                timeout=2
            )
            
            if r.ok:
                data = r.json()
                results = []
                
                for item in (data.get("query", {}).get("search", []) or [])[:top_k]:
                    page_id = item.get("pageid")
                    title = item.get("title", "")
                    
                    if page_id and title:
                        # Get page content
                        content_params = {
                            "action": "query",
                            "format": "json",
                            "pageids": page_id,
                            "prop": "extracts",
                            "exintro": "1",
                            "explaintext": "1"
                        }
                        
                        content_r = requests.get(
                            "https://en.wikipedia.org/w/api.php",
                            params=content_params,
                            timeout=2
                        )
                        
                        if content_r.ok:
                            content_data = content_r.json()
                            extract = content_data.get("query", {}).get("pages", {}).get(str(page_id), {}).get("extract", "")
                            
                            if extract:
                                results.append({
                                    "id": f"wiki_{page_id}",
                                    "content": extract[:500] + "..." if len(extract) > 500 else extract,
                                    "metadata": {
                                        "title": title,
                                        "url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                                        "source": "wikipedia",
                                        "provider": "wikipedia"
                                    },
                                    "score": 0.9,  # High score for Wikipedia
                                })
                
                return results
        except Exception as e:
            logger.warning(f"Wikipedia API failed: {e}")
        
        return []
    
    async def _call_stackexchange(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Call Stack Exchange API (keyless)"""
        try:
            import requests
            
            # Search Stack Overflow
            params = {
                "order": "desc",
                "sort": "relevance",
                "intitle": query,
                "site": "stackoverflow",
                "pagesize": min(top_k, 3)
            }
            
            r = requests.get(
                "https://api.stackexchange.com/2.3/search",
                params=params,
                timeout=2
            )
            
            if r.ok:
                data = r.json()
                results = []
                
                for item in (data.get("items", []) or [])[:top_k]:
                    question_id = item.get("question_id")
                    title = item.get("title", "")
                    
                    if question_id and title:
                        results.append({
                            "id": f"so_{question_id}",
                            "content": title,
                            "metadata": {
                                "title": title,
                                "url": f"https://stackoverflow.com/questions/{question_id}",
                                "source": "stackoverflow",
                                "provider": "stackexchange"
                            },
                            "score": 0.8,
                        })
                
                return results
        except Exception as e:
            logger.warning(f"Stack Exchange API failed: {e}")
        
        return []
    
    async def _call_mdn(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Call MDN Web Docs API (keyless)"""
        try:
            import requests
            
            # Search MDN
            params = {
                "q": query,
                "locale": "en-US",
                "size": min(top_k, 3)
            }
            
            r = requests.get(
                "https://developer.mozilla.org/api/v1/search",
                params=params,
                timeout=2
            )
            
            if r.ok:
                data = r.json()
                results = []
                
                for item in (data.get("documents", []) or [])[:top_k]:
                    title = item.get("title", "")
                    summary = item.get("summary", "")
                    url = item.get("mdn_url", "")
                    
                    if title and url:
                        results.append({
                            "id": f"mdn_{hash(url)}",
                            "content": summary,
                            "metadata": {
                                "title": title,
                                "url": f"https://developer.mozilla.org{url}",
                                "source": "mdn",
                                "provider": "mdn"
                            },
                            "score": 0.85,
                        })
                
                return results
        except Exception as e:
            logger.warning(f"MDN API failed: {e}")
        
        return []
    
    async def _vector_search_lane(self, request: RetrievalSearchRequest) -> List[Dict[str, Any]]:
        """Vector passage search lane using optimized singleton service."""
        try:
            # Import singleton vector service (Phase I2 optimization)
            from shared.core.services.vector_singleton_service import get_vector_singleton_service
            
            # Get singleton service (already initialized and warmed up)
            vector_service = await get_vector_singleton_service()
            
            # CRITICAL: Enforce strict top-k ≤ 5 requirement for performance
            top_k = min(5, request.max_results)  # Strict ≤ 5 passages for performance
            
            # Complete pipeline with singleton service (embed + search)
            # This uses the optimized singleton with caching and warmup
            embeddings, search_results = await vector_service.embed_and_search(
                query=request.query,
                top_k=top_k
            )
            
            # Format results
            results = []
            for result in search_results:
                if isinstance(result, tuple):
                    doc, score = result
                    results.append({
                        "id": doc.id,
                        "content": doc.text,
                        "metadata": {
                            **doc.metadata,
                            "lane": "vector_search",
                            "retrieval_method": "vector_similarity",
                            "embedding_model": "sentence-transformers/all-MiniLM-L3-v2"
                        },
                        "score": score,
                    })
                else:
                    # Handle dict format
                    if "metadata" not in result:
                        result["metadata"] = {}
                    result["metadata"]["lane"] = "vector_search"
                    result["metadata"]["retrieval_method"] = "vector_similarity"
                    results.append(result)
            
            # Validate we don't exceed the 5 passages limit
            if len(results) > 5:
                logger.warning(f"Vector lane exceeded 5 passages limit: {len(results)}, truncating")
                results = results[:5]
            
            return results
            
        except Exception as e:
            logger.warning(f"Vector search lane failed: {e}", exc_info=True)
            return []
    
    async def _knowledge_graph_lane(self, request: RetrievalSearchRequest) -> List[Dict[str, Any]]:
        """Knowledge graph fact lookup lane with thin wrapper around existing KG service."""
        try:
            # Import knowledge graph service directly to avoid circular imports
            from shared.core.agents.knowledge_graph_service import KnowledgeGraphService
            
            # Initialize KG service
            kg_service = KnowledgeGraphService()
            
            # Query knowledge graph with small top-k for strict latency
            # Call async method directly with strict timeout (1.0s)
            kg_result = await asyncio.wait_for(
                kg_service.query(request.query, "entity_relationship"),
                timeout=1.0
            )
            
            # Convert KG results to standard format
            results = []
            
            # Add entities as results (≤ 6 facts total as required for performance)
            # CRITICAL: This enforces the strict top-k ≤ 6 requirement
            max_entities = min(3, len(kg_result.entities))  # Up to 3 entities for ≤ 6 total
            for entity in kg_result.entities[:max_entities]:
                results.append({
                    "id": f"kg_entity_{entity.id}",
                    "content": f"{entity.name}: {entity.properties.get('description', 'No description available')}",
                    "metadata": {
                        "lane": "knowledge_graph",
                        "retrieval_method": "kg_fact_lookup",
                        "entity_type": entity.type,
                        "entity_id": entity.id,
                        "confidence": kg_result.confidence
                    },
                    "score": kg_result.confidence * 0.8,  # Scale confidence to score
                })
            
            # Add relationships as results (≤ 6 facts total as required)
            max_relationships = min(3, len(kg_result.relationships))  # Up to 3 relationships for ≤ 6 total
            for relationship in kg_result.relationships[:max_relationships]:
                results.append({
                    "id": f"kg_rel_{relationship.id}",
                    "content": f"{relationship.source_entity} {relationship.relationship_type} {relationship.target_entity}",
                    "metadata": {
                        "lane": "knowledge_graph",
                        "retrieval_method": "kg_relationship",
                        "relationship_type": relationship.relationship_type,
                        "confidence": kg_result.confidence
                    },
                    "score": kg_result.confidence * 0.7,  # Scale confidence to score
                })
            
            # Validate we don't exceed the 6 facts limit
            if len(results) > 6:
                logger.warning(f"KG lane exceeded 6 facts limit: {len(results)}, truncating")
                results = results[:6]
            
            return results
            
        except Exception as e:
            logger.warning(f"Knowledge graph lane failed: {e}", exc_info=True)
            return []
    
    async def _fuse_results(
        self, 
        lane_results: List[LaneResult], 
        request: RetrievalSearchRequest
    ) -> List[Dict[str, Any]]:
        """Fuse results from multiple lanes with deduplication."""
        if not lane_results:
            return []
        
        # Collect all results
        all_results = []
        for lane_result in lane_results:
            if lane_result.status == LaneStatus.AVAILABLE:
                all_results.extend(lane_result.results)
        
        if not all_results:
            return []
        
        # Deduplicate results using URL + normalized title similarity
        deduplicated_results = self._deduplicate_results(all_results)
        
        # Apply fusion strategy
        if self.config.fusion_strategy == "weighted_merge":
            return self._weighted_merge_fusion(deduplicated_results, request.max_results)
        elif self.config.fusion_strategy == "priority_based":
            return self._priority_based_fusion(deduplicated_results, request.max_results)
        else:
            return self._simple_merge_fusion(deduplicated_results, request.max_results)
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate results using URL + normalized title similarity."""
        if not results:
            return []
        
        # Group results by URL and normalized title
        seen_urls = set()
        seen_titles = set()
        deduplicated = []
        
        for result in results:
            # Get URL and title
            url = result.get("metadata", {}).get("url", "")
            title = result.get("metadata", {}).get("title", "")
            
            # Normalize title (lowercase, strip whitespace)
            normalized_title = title.lower().strip() if title else ""
            
            # Check for duplicates
            is_duplicate = False
            
            # Check URL similarity
            if url:
                for seen_url in seen_urls:
                    if self._urls_similar(url, seen_url):
                        is_duplicate = True
                        break
            
            # Check title similarity
            if not is_duplicate and normalized_title:
                for seen_title in seen_titles:
                    if self._titles_similar(normalized_title, seen_title):
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                deduplicated.append(result)
                if url:
                    seen_urls.add(url)
                if normalized_title:
                    seen_titles.add(normalized_title)
        
        return deduplicated
    
    def _urls_similar(self, url1: str, url2: str) -> bool:
        """Check if two URLs are similar (same domain and path)."""
        try:
            from urllib.parse import urlparse
            parsed1 = urlparse(url1)
            parsed2 = urlparse(url2)
            
            # Compare domain and path
            return (parsed1.netloc == parsed2.netloc and 
                   parsed1.path == parsed2.path)
        except:
            return False
    
    def _titles_similar(self, title1: str, title2: str) -> bool:
        """Check if two titles are similar (high overlap)."""
        if not title1 or not title2:
            return False
        
        # Simple similarity check - if one title contains the other
        return (title1 in title2 or title2 in title1 or 
                self._jaccard_similarity(title1, title2) > 0.8)
    
    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _log_retrieval_with_timing(
        self,
        request: RetrievalSearchRequest,
        lane_results: List[LaneResult],
        fused_results: List[Dict[str, Any]],
        total_latency: float,
        user_id: Optional[str]
    ):
        """Log retrieval results with per-lane timing, trace ID, and Prometheus metrics."""
        import uuid
        
        # Generate trace ID for this retrieval operation
        trace_id = str(uuid.uuid4())
        
        # Extract per-lane timing
        lane_timings = {}
        for result in lane_results:
            lane_timings[result.lane.value] = {
                "latency_ms": result.latency_ms,
                "status": result.status.value,
                "result_count": len(result.results),
                "error": result.error
            }
        
        # Log comprehensive retrieval information with per-lane timing
        logger.info(
            f"Retrieval orchestration completed (trace: {trace_id})",
            extra={
                "trace_id": trace_id,
                "query": request.query[:100],
                "query_length": len(request.query),
                "user_id": user_id,
                "total_latency_ms": total_latency,
                "total_results": len(fused_results),
                "lane_timings": lane_timings,
                "web_ms": lane_timings.get("web_search", {}).get("latency_ms", 0),
                "vector_ms": lane_timings.get("vector_search", {}).get("latency_ms", 0),
                "kg_ms": lane_timings.get("knowledge_graph", {}).get("latency_ms", 0),
                "successful_lanes": len([r for r in lane_results if r.status == LaneStatus.AVAILABLE]),
                "failed_lanes": len([r for r in lane_results if r.status != LaneStatus.AVAILABLE]),
                "fusion_strategy": self.config.fusion_strategy,
                "latency_budget_ms": self.config.latency_budget.total_budget_ms
            }
        )
        
        # Emit Prometheus metrics for per-lane timing with provider tags
        if PROMETHEUS_AVAILABLE:
            # End-to-end latency
            end_to_end_latency_histogram.observe(total_latency / 1000.0)
            
            # Per-lane metrics with provider tags
            for result in lane_results:
                lane_name = result.lane.value
                status = result.status.value
                latency_seconds = result.latency_ms / 1000.0
                
                # Extract provider information from results
                providers_used = set()
                fallback_used = False
                for res in result.results:
                    provider = res.get("metadata", {}).get("provider", "unknown")
                    providers_used.add(provider)
                    if provider in ["duckduckgo", "wikipedia", "stackexchange", "mdn", "gdelt", "hn_algolia", "rss", "stooq", "sec_edgar"]:
                        fallback_used = True
                
                # Lane latency histogram with provider tags
                for provider in providers_used:
                    lane_latency_histogram.labels(
                        lane=lane_name, 
                        status=status,
                        provider=provider,
                        fallback_used=str(fallback_used).lower(),
                        source="keyless" if fallback_used else "keyed"
                    ).observe(latency_seconds)
                
                # Lane result counter with provider tags
                for provider in providers_used:
                    lane_result_counter.labels(
                        lane=lane_name, 
                        status=status,
                        provider=provider,
                        fallback_used=str(fallback_used).lower(),
                        source="keyless" if fallback_used else "keyed"
                    ).inc(len(result.results))
                
                # Lane status gauge
                status_value = 1 if result.status == LaneStatus.AVAILABLE else 0
                lane_status_gauge.labels(lane=lane_name).set(status_value)
        
        # Log individual lane results for debugging
        for result in lane_results:
            logger.debug(
                f"Lane {result.lane.value} completed (trace: {trace_id})",
                extra={
                    "trace_id": trace_id,
                    "lane": result.lane.value,
                    "status": result.status.value,
                    "latency_ms": result.latency_ms,
                    "result_count": len(result.results),
                    "error": result.error
                }
            )
    
    def _weighted_merge_fusion(
        self, 
        results: List[Dict[str, Any]], 
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Fuse results using weighted scoring."""
        # Apply source-specific weights
        source_weights = {
            "web_search": 1.0,
            "vector_search": 0.9,
            "knowledge_graph": 0.8
        }
        
        # Recalculate scores with weights
        for result in results:
            source = result.get("metadata", {}).get("source", "unknown")
            weight = source_weights.get(source, 0.5)
            result["weighted_score"] = result.get("score", 0.0) * weight
        
        # Sort by weighted score
        results.sort(key=lambda x: x.get("weighted_score", 0.0), reverse=True)
        
        return results[:max_results]
    
    def _priority_based_fusion(
        self, 
        results: List[Dict[str, Any]], 
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Fuse results using priority-based selection."""
        # Define source priorities
        source_priority = {
            "knowledge_graph": 1,
            "vector_search": 2,
            "web_search": 3
        }
        
        # Group by source
        by_source = {}
        for result in results:
            source = result.get("metadata", {}).get("source", "unknown")
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(result)
        
        # Sort sources by priority
        sorted_sources = sorted(
            by_source.keys(), 
            key=lambda x: source_priority.get(x, 999)
        )
        
        # Select results in priority order
        fused_results = []
        for source in sorted_sources:
            source_results = sorted(
                by_source[source], 
                key=lambda x: x.get("score", 0.0), 
                reverse=True
            )
            fused_results.extend(source_results[:max_results // len(sorted_sources)])
            
            if len(fused_results) >= max_results:
                break
        
        return fused_results[:max_results]
    
    def _simple_merge_fusion(
        self, 
        results: List[Dict[str, Any]], 
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Simple merge fusion - just sort by score."""
        results.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        return results[:max_results]
    
    def _update_lane_metrics(self, lane_results: List[LaneResult]):
        """Update metrics for each lane."""
        for result in lane_results:
            self.lane_metrics[result.lane].append(result.latency_ms)
            
            # Keep only recent metrics (last 100)
            if len(self.lane_metrics[result.lane]) > 100:
                self.lane_metrics[result.lane] = self.lane_metrics[result.lane][-100:]
    
    def _create_empty_response(self, request: RetrievalSearchRequest) -> RetrievalSearchResponse:
        """Create an empty response when no lanes are available."""
        return RetrievalSearchResponse(
            sources=[],
            method="no_lanes_available",
            total_results=0,
            relevance_scores=[],
            limit=request.max_results
        )
    
    def _create_error_response(self, request: RetrievalSearchRequest, error: str) -> RetrievalSearchResponse:
        """Create an error response."""
        return RetrievalSearchResponse(
            sources=[],
            method="error",
            total_results=0,
            relevance_scores=[],
            limit=request.max_results
        )
    
    def get_lane_status(self) -> Dict[str, Any]:
        """Get current status of all retrieval lanes."""
        return {
            lane.value: {
                "status": status.value,
                "avg_latency_ms": sum(self.lane_metrics[lane]) / len(self.lane_metrics[lane]) if self.lane_metrics[lane] else 0.0,
                "total_requests": len(self.lane_metrics[lane])
            }
            for lane, status in self.lane_status.items()
        }
    
    def get_orchestration_stats(self) -> Dict[str, Any]:
        """Get orchestration statistics."""
        total_requests = sum(len(metrics) for metrics in self.lane_metrics.values())
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics()
        
        return {
            "total_requests": total_requests,
            "lane_status": self.get_lane_status(),
            "performance_requirements": {
                "p95_latency_target_ms": 3000,  # 3 seconds target
                "vector_timeout_target_ms": 2000,  # 2.0 seconds target
                "kg_timeout_target_ms": 1500,  # 1.5 seconds target
                "vector_top_k_limit": 5,  # ≤ 5 passages
                "kg_top_k_limit": 6,  # ≤ 6 facts
            },
            "performance_metrics": performance_metrics,
            "config": {
                "enable_web_search": self.config.enable_web_search,
                "enable_vector_search": self.config.enable_vector_search,
                "enable_knowledge_graph": self.config.enable_knowledge_graph,
                "enable_parallel_execution": self.config.enable_parallel_execution,
                "fusion_strategy": self.config.fusion_strategy
            },
            "latency_budget": {
                "total_budget_ms": self.config.latency_budget.total_budget_ms,
                "web_search_budget_ms": self.config.latency_budget.web_search_budget_ms,
                "vector_search_budget_ms": self.config.latency_budget.vector_search_budget_ms,
                "knowledge_graph_budget_ms": self.config.latency_budget.knowledge_graph_budget_ms
            }
        }
    
    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics to check if requirements are being met."""
        metrics = {}
        
        for lane in RetrievalLane:
            if lane in self.lane_metrics and self.lane_metrics[lane]:
                latencies = self.lane_metrics[lane]
                if latencies:
                    # Calculate P95 latency
                    sorted_latencies = sorted(latencies)
                    p95_index = int(len(sorted_latencies) * 0.95)
                    p95_latency = sorted_latencies[p95_index] if p95_index < len(sorted_latencies) else 0
                    
                    metrics[lane.value] = {
                        "p95_latency_ms": p95_latency,
                        "avg_latency_ms": sum(latencies) / len(latencies),
                        "total_requests": len(latencies),
                        "meets_vector_timeout": lane == RetrievalLane.VECTOR_SEARCH and p95_latency <= 2000,
                        "meets_kg_timeout": lane == RetrievalLane.KNOWLEDGE_GRAPH and p95_latency <= 1500,
                        "meets_total_budget": p95_latency <= 3000
                    }
        
        return metrics
    
    def check_performance_requirements(self) -> Dict[str, Any]:
        """Check if current performance meets the strict requirements."""
        performance_metrics = self._calculate_performance_metrics()
        
        # Check if requirements are met
        requirements_met = {
            "vector_search": {
                "timeout_2s": False,
                "top_k_5": self.config.max_results_per_lane <= 5,
                "status": "unknown"
            },
            "knowledge_graph": {
                "timeout_1_5s": False,
                "top_k_6": True,  # Enforced in code
                "status": "unknown"
            },
            "total_budget": {
                "p95_3s": False,
                "status": "unknown"
            }
        }
        
        # Check vector search requirements
        if "vector_search" in performance_metrics:
            vector_metrics = performance_metrics["vector_search"]
            requirements_met["vector_search"]["timeout_2s"] = vector_metrics["meets_vector_timeout"]
            requirements_met["vector_search"]["status"] = "meets_requirements" if vector_metrics["meets_vector_timeout"] else "exceeds_timeout"
        
        # Check knowledge graph requirements
        if "knowledge_graph" in performance_metrics:
            kg_metrics = performance_metrics["knowledge_graph"]
            requirements_met["knowledge_graph"]["timeout_1_5s"] = kg_metrics["meets_kg_timeout"]
            requirements_met["knowledge_graph"]["status"] = "meets_requirements" if kg_metrics["meets_kg_timeout"] else "exceeds_timeout"
        
        # Check total budget requirements
        all_meet_budget = all(
            metrics["meets_total_budget"] 
            for metrics in performance_metrics.values()
        )
        requirements_met["total_budget"]["p95_3s"] = all_meet_budget
        requirements_met["total_budget"]["status"] = "meets_requirements" if all_meet_budget else "exceeds_budget"
        
        return {
            "requirements_met": requirements_met,
            "performance_metrics": performance_metrics,
            "configuration": {
                "vector_timeout_ms": self.config.latency_budget.vector_search_budget_ms,
                "kg_timeout_ms": self.config.latency_budget.knowledge_graph_budget_ms,
                "total_budget_ms": self.config.latency_budget.total_budget_ms,
                "max_results_per_lane": self.config.max_results_per_lane
            }
        }


# Global orchestrator instance
orchestrator = RetrievalOrchestrator()


def get_orchestrator() -> RetrievalOrchestrator:
    """Get the global retrieval orchestrator instance."""
    return orchestrator


# TODO: Integrate with actual web search services (Brave, SerpAPI)
# TODO: Integrate with actual vector search services (Qdrant, Chroma)
# TODO: Integrate with actual knowledge graph services (ArangoDB)
# TODO: Add circuit breaker for lane failures
# TODO: Add adaptive latency budgets based on performance
# TODO: Add result deduplication across lanes
# TODO: Add query classification for lane selection



