#!/usr/bin/env python3
"""
Cost-Aware LLM Router - P3 Phase 1 Integration
=============================================

Integrates cost optimization with existing LLM provider routing:
- Real-time cost tracking integration
- Dynamic provider selection based on cost and quality
- Budget-aware circuit breakers
- Performance monitoring with cost metrics
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import structlog

# Import existing LLM integration
try:
    from services.gateway.real_llm_integration import RealLLMProcessor
    LLM_INTEGRATION_AVAILABLE = True
except ImportError:
    LLM_INTEGRATION_AVAILABLE = False

# Import our cost optimizer
from shared.core.services.llm_cost_optimizer import (
    cost_optimizer, 
    get_cost_optimized_providers,
    record_llm_cost
)

logger = structlog.get_logger(__name__)

@dataclass
class CostAwareQuery:
    """Query with cost awareness metadata"""
    query: str
    complexity: str = "medium"  # simple, medium, complex
    max_budget: float = 0.10    # Max cost per query in USD
    quality_threshold: float = 0.7  # Minimum quality score
    timeout_seconds: float = 10.0

@dataclass
class CostAwareResponse:
    """Response with cost and performance metrics"""
    response: str
    provider_used: str
    cost_usd: float
    input_tokens: int
    output_tokens: int
    response_time_ms: float
    quality_score: float
    budget_remaining: float
    success: bool
    error: Optional[str] = None

class CostAwareLLMRouter:
    """
    Cost-aware LLM router that optimizes for cost while maintaining quality.
    
    Features:
    - Dynamic provider selection based on cost and quality
    - Real-time budget tracking and enforcement
    - Circuit breakers for expensive providers
    - Fallback routing when budget limits hit
    - Performance and cost analytics
    """
    
    def __init__(self):
        """Initialize cost-aware router"""
        self.llm_processor = None
        self.daily_budget_used = 0.0
        self.daily_budget_limit = 50.0  # $50 daily limit
        
        if LLM_INTEGRATION_AVAILABLE:
            try:
                self.llm_processor = RealLLMProcessor()
                logger.info("Cost-aware LLM router initialized with real integration")
            except Exception as e:
                logger.warning("Failed to initialize LLM processor", error=str(e))
        else:
            logger.info("Cost-aware LLM router initialized in simulation mode")
    
    def estimate_token_count(self, text: str) -> int:
        """Estimate token count for text (rough approximation)"""
        # Rough estimation: ~4 characters per token for English text
        return max(1, len(text) // 4)
    
    async def process_cost_aware_query(self, query: CostAwareQuery) -> CostAwareResponse:
        """Process query with cost awareness and optimization"""
        start_time = time.time()
        
        logger.info("Processing cost-aware query",
                   query_length=len(query.query),
                   complexity=query.complexity,
                   max_budget=query.max_budget)
        
        # Check daily budget
        if self.daily_budget_used >= self.daily_budget_limit:
            return CostAwareResponse(
                response="Daily budget limit reached. Please try again tomorrow.",
                provider_used="budget_limit",
                cost_usd=0.0,
                input_tokens=0,
                output_tokens=0,
                response_time_ms=(time.time() - start_time) * 1000,
                quality_score=0.0,
                budget_remaining=0.0,
                success=False,
                error="Daily budget exhausted"
            )
        
        # Get cost-optimized provider order
        provider_order = await get_cost_optimized_providers(query.complexity)
        
        if not provider_order:
            return CostAwareResponse(
                response="No providers available",
                provider_used="none",
                cost_usd=0.0,
                input_tokens=0,
                output_tokens=0,
                response_time_ms=(time.time() - start_time) * 1000,
                quality_score=0.0,
                budget_remaining=self.daily_budget_limit - self.daily_budget_used,
                success=False,
                error="No providers available"
            )
        
        # Try providers in cost-optimized order
        for provider in provider_order:
            try:
                response = await self._try_provider(provider, query, start_time)
                if response.success:
                    # Update daily budget tracking
                    self.daily_budget_used += response.cost_usd
                    
                    logger.info("Cost-aware query completed",
                               provider=provider,
                               cost=response.cost_usd,
                               response_time_ms=response.response_time_ms,
                               quality_score=response.quality_score)
                    
                    return response
                    
            except Exception as e:
                logger.warning("Provider failed", provider=provider, error=str(e))
                continue
        
        # All providers failed
        return CostAwareResponse(
            response="All providers failed. Please try again later.",
            provider_used="fallback",
            cost_usd=0.0,
            input_tokens=0,
            output_tokens=0,
            response_time_ms=(time.time() - start_time) * 1000,
            quality_score=0.0,
            budget_remaining=self.daily_budget_limit - self.daily_budget_used,
            success=False,
            error="All providers failed"
        )
    
    async def _try_provider(self, provider: str, query: CostAwareQuery, start_time: float) -> CostAwareResponse:
        """Try processing query with a specific provider"""
        
        # Estimate input tokens
        input_tokens = self.estimate_token_count(query.query)
        
        # Check if provider is available (not circuit broken)
        if not cost_optimizer.is_provider_available(provider):
            raise Exception(f"Provider {provider} circuit breaker is open")
        
        # Estimate cost before processing
        estimated_cost = cost_optimizer.calculate_query_cost(provider, input_tokens, input_tokens)
        
        # Check if estimated cost exceeds query budget
        if estimated_cost > query.max_budget:
            raise Exception(f"Provider {provider} estimated cost ${estimated_cost:.4f} exceeds budget ${query.max_budget:.4f}")
        
        # Check if remaining daily budget is sufficient
        if self.daily_budget_used + estimated_cost > self.daily_budget_limit:
            raise Exception(f"Provider {provider} would exceed daily budget limit")
        
        # Process query (simulation or real)
        if self.llm_processor and provider != 'simulation':
            # Real LLM processing would go here
            # For now, simulate with realistic metrics
            response_text = await self._simulate_llm_response(provider, query.query)
        else:
            # Simulation mode
            response_text = await self._simulate_llm_response(provider, query.query)
        
        response_time_ms = (time.time() - start_time) * 1000
        
        # Estimate output tokens
        output_tokens = self.estimate_token_count(response_text)
        
        # Calculate actual cost
        actual_cost = cost_optimizer.calculate_query_cost(provider, input_tokens, output_tokens)
        
        # Get provider quality score
        provider_config = cost_optimizer.cost_configs.get(provider)
        quality_score = provider_config.quality_score if provider_config else 0.5
        
        # Check if quality meets threshold
        if quality_score < query.quality_threshold:
            raise Exception(f"Provider {provider} quality {quality_score} below threshold {query.quality_threshold}")
        
        # Record cost metrics
        await record_llm_cost(provider, input_tokens, output_tokens, response_time_ms, quality_score)
        
        return CostAwareResponse(
            response=response_text,
            provider_used=provider,
            cost_usd=actual_cost,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            response_time_ms=response_time_ms,
            quality_score=quality_score,
            budget_remaining=self.daily_budget_limit - self.daily_budget_used - actual_cost,
            success=True
        )
    
    async def _simulate_llm_response(self, provider: str, query: str) -> str:
        """Simulate LLM response for testing"""
        # Simulate processing time based on provider
        if provider == 'ollama':
            await asyncio.sleep(0.5)  # Local model - slower but free
        elif provider == 'openai':
            await asyncio.sleep(0.2)  # Fast API
        elif provider == 'anthropic':
            await asyncio.sleep(0.3)  # Fast API
        elif provider == 'huggingface':
            await asyncio.sleep(0.4)  # HF Inference API
        else:
            await asyncio.sleep(0.1)  # Local stub - fastest
        
        # Generate response based on provider characteristics
        if provider == 'openai':
            return f"[OpenAI] Comprehensive analysis of '{query[:50]}...': This is a detailed, high-quality response with citations and structured information."
        elif provider == 'anthropic':
            return f"[Claude] Thoughtful response to '{query[:50]}...': Here's a well-reasoned analysis with ethical considerations and multiple perspectives."
        elif provider == 'huggingface':
            return f"[HuggingFace] Response to '{query[:50]}...': A good quality answer using open-source models with decent accuracy."
        elif provider == 'ollama':
            return f"[Ollama Local] Analysis of '{query[:50]}...': Local model response that's free but may be less comprehensive."
        else:
            return f"[Fallback] Basic response to '{query[:50]}...': Simple answer as a system fallback."
    
    async def get_cost_analytics(self) -> Dict[str, Any]:
        """Get cost analytics and optimization insights"""
        daily_report = await cost_optimizer.get_daily_cost_report()
        recommendations = await cost_optimizer.get_optimization_recommendations()
        
        analytics = {
            'daily_budget': {
                'limit': self.daily_budget_limit,
                'used': self.daily_budget_used,
                'remaining': self.daily_budget_limit - self.daily_budget_used,
                'utilization_percent': (self.daily_budget_used / self.daily_budget_limit) * 100
            },
            'daily_report': daily_report,
            'recommendations': recommendations,
            'circuit_breakers': {
                provider: breaker for provider, breaker in cost_optimizer.circuit_breakers.items()
                if breaker.get('status') == 'open'
            },
            'provider_availability': {
                provider: cost_optimizer.is_provider_available(provider)
                for provider in cost_optimizer.cost_configs.keys()
            }
        }
        
        return analytics
    
    async def reset_daily_budget(self):
        """Reset daily budget (called by scheduler)"""
        self.daily_budget_used = 0.0
        logger.info("Daily budget reset", limit=self.daily_budget_limit)

# Global cost-aware router instance
cost_aware_router = CostAwareLLMRouter()

async def process_cost_optimized_query(query: str, complexity: str = "medium", 
                                     max_budget: float = 0.10) -> CostAwareResponse:
    """Process query with cost optimization"""
    cost_query = CostAwareQuery(
        query=query,
        complexity=complexity,
        max_budget=max_budget
    )
    
    return await cost_aware_router.process_cost_aware_query(cost_query)

async def get_cost_analytics() -> Dict[str, Any]:
    """Get cost analytics"""
    return await cost_aware_router.get_cost_analytics()
