#!/usr/bin/env python3
"""
Enhanced LLM Router Service - Policy-Based Routing + Telemetry (Phase I3)

This service enhances the provider router with:
- Policy-based routing: free/local first, escalate on complexity
- Auto-fallback on errors/timeouts with circuit breaker
- Comprehensive telemetry: provider chosen, reason, latency, tokens
- Vision support and JSON mode routing
- RPM/TPM budget management

Key Features:
- Zero-budget optimization with graceful escalation
- Circuit breaker pattern for provider reliability
- Structured telemetry for monitoring and optimization
- Dynamic routing based on query complexity and capabilities
"""

import os
import time
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json

from shared.llm.provider_order import (
    LLMProvider, 
    QueryComplexity, 
    LLMRole, 
    ModelConfig,
    ProviderRegistry,
    select_provider_and_model_for_complexity
)
from shared.core.unified_logging import get_logger

logger = get_logger(__name__)

class RoutingReason(str, Enum):
    """Reasons for provider selection."""
    FREE_FIRST = "free_first"
    COMPLEXITY_ESCALATION = "complexity_escalation"
    CAPABILITY_REQUIRED = "capability_required"
    FALLBACK_ERROR = "fallback_error"
    FALLBACK_TIMEOUT = "fallback_timeout"
    CIRCUIT_BREAKER = "circuit_breaker"
    BUDGET_EXHAUSTED = "budget_exhausted"
    POLICY_OVERRIDE = "policy_override"

class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, blocked
    HALF_OPEN = "half_open" # Testing if recovered

@dataclass
class ProviderMetrics:
    """Metrics for provider performance tracking."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0
    total_latency_ms: float = 0.0
    total_tokens: int = 0
    total_cost: float = 0.0
    
    # Budget tracking
    requests_this_minute: int = 0
    tokens_this_minute: int = 0
    minute_window_start: datetime = field(default_factory=datetime.now)
    
    # Circuit breaker state
    circuit_state: CircuitBreakerState = CircuitBreakerState.CLOSED
    circuit_open_until: Optional[datetime] = None
    consecutive_failures: int = 0
    last_failure_time: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests
    
    @property
    def avg_latency_ms(self) -> float:
        """Calculate average latency."""
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency_ms / self.successful_requests
    
    @property
    def avg_cost_per_request(self) -> float:
        """Calculate average cost per request."""
        if self.successful_requests == 0:
            return 0.0
        return self.total_cost / self.successful_requests

@dataclass
class RoutingRequest:
    """Request for provider routing."""
    prompt: str
    complexity: QueryComplexity
    role: LLMRole
    max_tokens: int = 1000
    temperature: float = 0.7
    requires_vision: bool = False
    requires_json_mode: bool = False
    requires_function_calling: bool = False
    prefer_free: bool = True
    timeout_seconds: float = 15.0
    trace_id: Optional[str] = None

@dataclass
class RoutingResponse:
    """Response from provider routing."""
    provider: LLMProvider
    model: ModelConfig
    reason: RoutingReason
    fallback_count: int = 0
    routing_time_ms: float = 0.0
    estimated_cost: float = 0.0
    estimated_tokens: int = 0
    circuit_breaker_bypassed: List[LLMProvider] = field(default_factory=list)

@dataclass
class RoutingTelemetry:
    """Telemetry data for routing decision."""
    trace_id: str
    provider_chosen: LLMProvider
    model_chosen: str
    reason: RoutingReason
    complexity: QueryComplexity
    role: LLMRole
    routing_latency_ms: float
    request_time: datetime
    fallback_count: int
    circuit_breakers_hit: List[LLMProvider]
    estimated_cost: float
    estimated_tokens: int
    requires_vision: bool
    requires_json_mode: bool
    requires_function_calling: bool


class EnhancedRouterService:
    """Enhanced LLM router with policy-based routing and comprehensive telemetry."""
    
    def __init__(self):
        """Initialize enhanced router service."""
        self.provider_registry = ProviderRegistry()
        self.provider_metrics: Dict[LLMProvider, ProviderMetrics] = {}
        self.telemetry_buffer: List[RoutingTelemetry] = []
        self.max_telemetry_buffer = 1000
        
        # Configuration
        self.default_free_first = os.getenv("PRIORITIZE_FREE_MODELS", "true").lower() == "true"
        self.auto_escalate_on_complexity = os.getenv("AUTO_ESCALATE_COMPLEXITY", "true").lower() == "true"
        self.circuit_breaker_enabled = os.getenv("CIRCUIT_BREAKER_ENABLED", "true").lower() == "true"
        
        # Initialize metrics for all providers
        self._initialize_provider_metrics()
        
        logger.info("EnhancedRouterService initialized", 
                   free_first=self.default_free_first,
                   auto_escalate=self.auto_escalate_on_complexity,
                   circuit_breaker=self.circuit_breaker_enabled)
    
    def _initialize_provider_metrics(self):
        """Initialize metrics for all providers."""
        for provider in LLMProvider:
            self.provider_metrics[provider] = ProviderMetrics()
    
    def _is_provider_available(self, provider: LLMProvider) -> bool:
        """Check if provider is available (has API key, etc.)."""
        availability_map = {
            LLMProvider.OPENAI: os.getenv("OPENAI_API_KEY") is not None,
            LLMProvider.ANTHROPIC: os.getenv("ANTHROPIC_API_KEY") is not None,
            LLMProvider.HUGGINGFACE: True,  # Free tier always available
            LLMProvider.OLLAMA: True,       # Local always available
            LLMProvider.LOCAL_STUB: True    # Always available fallback
        }
        return availability_map.get(provider, False)
    
    def _is_circuit_breaker_open(self, provider: LLMProvider) -> bool:
        """Check if circuit breaker is open for provider."""
        if not self.circuit_breaker_enabled:
            return False
            
        metrics = self.provider_metrics[provider]
        
        if metrics.circuit_state == CircuitBreakerState.CLOSED:
            return False
        elif metrics.circuit_state == CircuitBreakerState.OPEN:
            # Check if timeout has passed
            if metrics.circuit_open_until and datetime.now() > metrics.circuit_open_until:
                metrics.circuit_state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker moved to half-open", provider=provider.value)
                return False
            return True
        elif metrics.circuit_state == CircuitBreakerState.HALF_OPEN:
            return False
        
        return False
    
    def _update_circuit_breaker(self, provider: LLMProvider, success: bool, latency_ms: float):
        """Update circuit breaker state based on request outcome."""
        if not self.circuit_breaker_enabled:
            return
            
        metrics = self.provider_metrics[provider]
        
        if success:
            # Reset on success
            metrics.consecutive_failures = 0
            if metrics.circuit_state != CircuitBreakerState.CLOSED:
                metrics.circuit_state = CircuitBreakerState.CLOSED
                metrics.circuit_open_until = None
                logger.info("Circuit breaker closed", provider=provider.value)
        else:
            # Increment failures
            metrics.consecutive_failures += 1
            metrics.last_failure_time = datetime.now()
            
            # Check if should open circuit
            failure_threshold = 5  # Default from ModelConfig
            if metrics.consecutive_failures >= failure_threshold:
                metrics.circuit_state = CircuitBreakerState.OPEN
                circuit_timeout = 60  # Default from ModelConfig
                metrics.circuit_open_until = datetime.now() + timedelta(seconds=circuit_timeout)
                
                logger.warning("Circuit breaker opened", 
                              provider=provider.value,
                              consecutive_failures=metrics.consecutive_failures,
                              timeout_until=metrics.circuit_open_until.isoformat())
    
    def _check_budget_limits(self, provider: LLMProvider, model: ModelConfig, 
                           estimated_tokens: int) -> bool:
        """Check if provider is within budget limits."""
        metrics = self.provider_metrics[provider]
        now = datetime.now()
        
        # Reset minute window if needed
        if (now - metrics.minute_window_start).total_seconds() >= 60:
            metrics.requests_this_minute = 0
            metrics.tokens_this_minute = 0
            metrics.minute_window_start = now
        
        # Check RPM limit
        if model.max_rpm and metrics.requests_this_minute >= model.max_rpm:
            logger.warning("RPM limit exceeded", 
                          provider=provider.value,
                          requests_this_minute=metrics.requests_this_minute,
                          max_rpm=model.max_rpm)
            return False
        
        # Check TPM limit
        if model.max_tpm and (metrics.tokens_this_minute + estimated_tokens) > model.max_tpm:
            logger.warning("TPM limit would be exceeded",
                          provider=provider.value,
                          tokens_this_minute=metrics.tokens_this_minute,
                          estimated_tokens=estimated_tokens,
                          max_tpm=model.max_tpm)
            return False
        
        return True
    
    def _get_capability_score(self, model: ModelConfig, request: RoutingRequest) -> float:
        """Score model based on capability requirements."""
        score = 1.0
        
        # Required capabilities
        if request.requires_vision and not model.supports_vision:
            return 0.0  # Hard requirement
        if request.requires_json_mode and not model.supports_json_mode:
            return 0.0  # Hard requirement
        if request.requires_function_calling and not model.supports_function_calling:
            return 0.0  # Hard requirement
        
        # Preferred capabilities (soft scoring)
        if request.role == LLMRole.REASONING and model.reasoning_capability > 0.8:
            score += 0.2
        if request.role == LLMRole.TOOL and model.tool_capability > 0.8:
            score += 0.2
        
        # Cost considerations
        if request.prefer_free and model.is_free:
            score += 0.3
        elif not request.prefer_free and model.cost_tier == "premium":
            score += 0.1
        
        return min(score, 2.0)  # Cap at 2.0
    
    async def route_request(self, request: RoutingRequest) -> RoutingResponse:
        """
        Route request to optimal provider with policy-based selection.
        
        Args:
            request: Routing request with requirements
            
        Returns:
            RoutingResponse with selected provider and telemetry
        """
        routing_start = time.time()
        trace_id = request.trace_id or f"route_{int(time.time())}"
        fallback_count = 0
        circuit_breakers_hit = []
        
        logger.info("Starting provider routing",
                   trace_id=trace_id,
                   complexity=request.complexity.value,
                   role=request.role.value,
                   prefer_free=request.prefer_free,
                   requires_vision=request.requires_vision,
                   requires_json=request.requires_json_mode,
                   requires_function_calling=request.requires_function_calling)
        
        # Get provider order based on policy
        if request.prefer_free or self.default_free_first:
            providers = self.provider_registry.get_free_first_order()
            primary_reason = RoutingReason.FREE_FIRST
        else:
            providers = self.provider_registry.get_provider_order()
            primary_reason = RoutingReason.COMPLEXITY_ESCALATION
        
        # Try providers in order
        for provider in providers:
            try:
                # Check availability
                if not self._is_provider_available(provider):
                    logger.debug("Provider not available", provider=provider.value, trace_id=trace_id)
                    continue
                
                # Check circuit breaker
                if self._is_circuit_breaker_open(provider):
                    circuit_breakers_hit.append(provider)
                    logger.debug("Circuit breaker open", provider=provider.value, trace_id=trace_id)
                    continue
                
                # Get best model for role/complexity
                try:
                    selected_provider, selected_model = select_provider_and_model_for_complexity(
                        request.complexity, request.role, prefer_free=request.prefer_free
                    )
                    
                    if selected_provider != provider:
                        continue  # Not the best model for this provider
                        
                except Exception as e:
                    logger.debug("Model selection failed", provider=provider.value, error=str(e))
                    continue
                
                # Check capability requirements
                capability_score = self._get_capability_score(selected_model, request)
                if capability_score <= 0:
                    logger.debug("Capability requirements not met", 
                               provider=provider.value,
                               model=selected_model.name,
                               trace_id=trace_id)
                    continue
                
                # Estimate token usage
                estimated_tokens = min(request.max_tokens, selected_model.max_tokens)
                
                # Check budget limits
                if not self._check_budget_limits(provider, selected_model, estimated_tokens):
                    logger.debug("Budget limits exceeded", provider=provider.value, trace_id=trace_id)
                    fallback_count += 1
                    continue
                
                # Provider selected successfully
                routing_time_ms = (time.time() - routing_start) * 1000
                estimated_cost = (estimated_tokens / 1000) * selected_model.cost_per_1k_tokens
                
                # Determine final reason
                final_reason = primary_reason
                if fallback_count > 0:
                    final_reason = RoutingReason.FALLBACK_ERROR
                if request.requires_vision or request.requires_json_mode or request.requires_function_calling:
                    final_reason = RoutingReason.CAPABILITY_REQUIRED
                
                response = RoutingResponse(
                    provider=provider,
                    model=selected_model,
                    reason=final_reason,
                    fallback_count=fallback_count,
                    routing_time_ms=routing_time_ms,
                    estimated_cost=estimated_cost,
                    estimated_tokens=estimated_tokens,
                    circuit_breaker_bypassed=circuit_breakers_hit
                )
                
                # Record telemetry
                await self._record_telemetry(request, response, trace_id)
                
                logger.info("Provider routing completed",
                           trace_id=trace_id,
                           provider=provider.value,
                           model=selected_model.name,
                           reason=final_reason.value,
                           routing_time_ms=round(routing_time_ms, 2),
                           fallback_count=fallback_count)
                
                return response
                
            except Exception as e:
                logger.warning("Provider routing attempt failed",
                              provider=provider.value,
                              error=str(e),
                              trace_id=trace_id)
                fallback_count += 1
                continue
        
        # All providers failed - fallback to local stub
        routing_time_ms = (time.time() - routing_start) * 1000
        
        # Create fallback model config
        fallback_model = ModelConfig(
            name="local_stub",
            provider=LLMProvider.LOCAL_STUB,
            role=request.role,
            max_tokens=request.max_tokens,
            avg_latency_ms=100,
            cost_per_1k_tokens=0.0,
            supports_streaming=False,
            supports_tools=False,
            is_free=True,
            context_window=4096,
            reasoning_capability=0.3,
            tool_capability=0.1,
            supports_vision=False,
            supports_json_mode=True,  # Can always return JSON
            supports_function_calling=False
        )
        
        response = RoutingResponse(
            provider=LLMProvider.LOCAL_STUB,
            model=fallback_model,
            reason=RoutingReason.FALLBACK_ERROR,
            fallback_count=fallback_count,
            routing_time_ms=routing_time_ms,
            estimated_cost=0.0,
            estimated_tokens=request.max_tokens,
            circuit_breaker_bypassed=circuit_breakers_hit
        )
        
        # Record telemetry
        await self._record_telemetry(request, response, trace_id)
        
        logger.warning("All providers failed - using local stub",
                      trace_id=trace_id,
                      fallback_count=fallback_count,
                      circuit_breakers_hit=[p.value for p in circuit_breakers_hit])
        
        return response
    
    async def _record_telemetry(self, request: RoutingRequest, response: RoutingResponse, trace_id: str):
        """Record telemetry data for monitoring and optimization."""
        telemetry = RoutingTelemetry(
            trace_id=trace_id,
            provider_chosen=response.provider,
            model_chosen=response.model.name,
            reason=response.reason,
            complexity=request.complexity,
            role=request.role,
            routing_latency_ms=response.routing_time_ms,
            request_time=datetime.now(),
            fallback_count=response.fallback_count,
            circuit_breakers_hit=response.circuit_breaker_bypassed,
            estimated_cost=response.estimated_cost,
            estimated_tokens=response.estimated_tokens,
            requires_vision=request.requires_vision,
            requires_json_mode=request.requires_json_mode,
            requires_function_calling=request.requires_function_calling
        )
        
        # Add to buffer
        self.telemetry_buffer.append(telemetry)
        
        # Trim buffer if too large
        if len(self.telemetry_buffer) > self.max_telemetry_buffer:
            self.telemetry_buffer = self.telemetry_buffer[-self.max_telemetry_buffer:]
        
        # Log structured telemetry
        logger.info("Routing telemetry recorded",
                   trace_id=trace_id,
                   provider=response.provider.value,
                   model=response.model.name,
                   reason=response.reason.value,
                   routing_latency_ms=round(response.routing_time_ms, 2),
                   estimated_cost=response.estimated_cost,
                   fallback_count=response.fallback_count)
    
    def record_request_outcome(self, provider: LLMProvider, success: bool, 
                              latency_ms: float, tokens_used: int, actual_cost: float):
        """Record the outcome of a request for metrics and circuit breaker."""
        metrics = self.provider_metrics[provider]
        
        # Update basic metrics
        metrics.total_requests += 1
        metrics.total_latency_ms += latency_ms
        metrics.total_tokens += tokens_used
        metrics.total_cost += actual_cost
        
        # Update minute window
        now = datetime.now()
        if (now - metrics.minute_window_start).total_seconds() >= 60:
            metrics.requests_this_minute = 0
            metrics.tokens_this_minute = 0
            metrics.minute_window_start = now
        
        metrics.requests_this_minute += 1
        metrics.tokens_this_minute += tokens_used
        
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
        
        # Update circuit breaker
        self._update_circuit_breaker(provider, success, latency_ms)
        
        logger.debug("Request outcome recorded",
                    provider=provider.value,
                    success=success,
                    latency_ms=round(latency_ms, 2),
                    tokens_used=tokens_used,
                    cost=actual_cost)
    
    def get_routing_metrics(self) -> Dict[str, Any]:
        """Get comprehensive routing metrics."""
        total_requests = sum(m.total_requests for m in self.provider_metrics.values())
        total_cost = sum(m.total_cost for m in self.provider_metrics.values())
        
        provider_stats = {}
        for provider, metrics in self.provider_metrics.items():
            provider_stats[provider.value] = {
                "total_requests": metrics.total_requests,
                "success_rate": metrics.success_rate,
                "avg_latency_ms": metrics.avg_latency_ms,
                "total_cost": metrics.total_cost,
                "avg_cost_per_request": metrics.avg_cost_per_request,
                "circuit_state": metrics.circuit_state.value,
                "consecutive_failures": metrics.consecutive_failures,
                "requests_this_minute": metrics.requests_this_minute,
                "tokens_this_minute": metrics.tokens_this_minute
            }
        
        # Recent telemetry summary
        recent_telemetry = self.telemetry_buffer[-100:] if self.telemetry_buffer else []
        reason_counts = {}
        for t in recent_telemetry:
            reason = t.reason.value
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        return {
            "total_requests": total_requests,
            "total_cost": total_cost,
            "provider_stats": provider_stats,
            "recent_routing_reasons": reason_counts,
            "telemetry_buffer_size": len(self.telemetry_buffer),
            "circuit_breaker_enabled": self.circuit_breaker_enabled,
            "free_first_enabled": self.default_free_first
        }


# Global service instance
_enhanced_router_service: Optional[EnhancedRouterService] = None

def get_enhanced_router_service() -> EnhancedRouterService:
    """Get or create global enhanced router service."""
    global _enhanced_router_service
    
    if _enhanced_router_service is None:
        _enhanced_router_service = EnhancedRouterService()
    
    return _enhanced_router_service
