#!/usr/bin/env python3
"""
LLM Cost Optimizer - P3 Phase 1: Advanced Cost Optimization
==========================================================

Real-time cost tracking and optimization for LLM providers:
- Real-time cost tracking per provider and query
- Dynamic circuit breakers for expensive providers
- Cost-aware routing with quality preservation
- Budget management and alerting
- ROI analysis and recommendations

Target: 30% cost reduction while maintaining quality
"""

import os
import time
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import structlog

logger = structlog.get_logger(__name__)

class CostTier(Enum):
    """Cost tiers for LLM providers"""
    FREE = "free"           # $0/token
    LOW = "low"            # $0.001-0.01/token
    MEDIUM = "medium"      # $0.01-0.05/token
    HIGH = "high"          # $0.05+/token

@dataclass
class ProviderCostConfig:
    """Cost configuration for each provider"""
    provider_name: str
    cost_tier: CostTier
    input_cost_per_1k_tokens: float  # USD per 1K input tokens
    output_cost_per_1k_tokens: float  # USD per 1K output tokens
    daily_budget_limit: float = 10.0  # USD per day
    rate_limit_rpm: int = 60  # Requests per minute
    quality_score: float = 0.8  # Quality rating 0-1
    enabled: bool = True

@dataclass
class QueryCostMetrics:
    """Cost metrics for a single query"""
    provider: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    response_time_ms: float
    quality_score: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class DailyCostSummary:
    """Daily cost summary per provider"""
    provider: str
    date: str
    total_queries: int
    total_cost: float
    avg_cost_per_query: float
    total_tokens: int
    avg_response_time_ms: float
    success_rate: float
    budget_utilization: float  # Percentage of daily budget used

class LLMCostOptimizer:
    """
    Advanced LLM cost optimization service.
    
    Features:
    - Real-time cost tracking per query
    - Dynamic budget management
    - Circuit breakers for expensive providers
    - Cost-aware provider routing
    - Performance vs cost optimization
    - Budget alerts and recommendations
    """
    
    def __init__(self):
        """Initialize cost optimizer"""
        self.cost_configs = self._load_provider_configs()
        self.daily_costs = {}  # provider -> DailyCostSummary
        self.query_history = []  # List of QueryCostMetrics
        self.circuit_breakers = {}  # provider -> circuit state
        
        logger.info("LLMCostOptimizer initialized",
                   providers=len(self.cost_configs),
                   cost_tracking="enabled")
    
    def _load_provider_configs(self) -> Dict[str, ProviderCostConfig]:
        """Load provider cost configurations"""
        configs = {
            'openai': ProviderCostConfig(
                provider_name='openai',
                cost_tier=CostTier.MEDIUM,
                input_cost_per_1k_tokens=0.03,   # GPT-4o pricing
                output_cost_per_1k_tokens=0.06,
                daily_budget_limit=float(os.getenv('OPENAI_DAILY_BUDGET', '10.0')),
                rate_limit_rpm=60,
                quality_score=0.95,  # High quality
                enabled=True
            ),
            'anthropic': ProviderCostConfig(
                provider_name='anthropic',
                cost_tier=CostTier.MEDIUM,
                input_cost_per_1k_tokens=0.025,  # Claude pricing
                output_cost_per_1k_tokens=0.075,
                daily_budget_limit=float(os.getenv('ANTHROPIC_DAILY_BUDGET', '10.0')),
                rate_limit_rpm=50,
                quality_score=0.92,  # High quality
                enabled=True
            ),
            'huggingface': ProviderCostConfig(
                provider_name='huggingface',
                cost_tier=CostTier.LOW,
                input_cost_per_1k_tokens=0.002,  # HF Inference API
                output_cost_per_1k_tokens=0.002,
                daily_budget_limit=float(os.getenv('HUGGINGFACE_DAILY_BUDGET', '5.0')),
                rate_limit_rpm=100,
                quality_score=0.75,  # Good quality
                enabled=True
            ),
            'ollama': ProviderCostConfig(
                provider_name='ollama',
                cost_tier=CostTier.FREE,
                input_cost_per_1k_tokens=0.0,  # Local models - free
                output_cost_per_1k_tokens=0.0,
                daily_budget_limit=1000.0,  # Unlimited
                rate_limit_rpm=200,
                quality_score=0.70,  # Decent quality
                enabled=True
            ),
            'local_stub': ProviderCostConfig(
                provider_name='local_stub',
                cost_tier=CostTier.FREE,
                input_cost_per_1k_tokens=0.0,  # Local fallback - free
                output_cost_per_1k_tokens=0.0,
                daily_budget_limit=1000.0,  # Unlimited
                rate_limit_rpm=1000,
                quality_score=0.30,  # Basic fallback
                enabled=True
            )
        }
        
        return configs
    
    def calculate_query_cost(self, provider: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a specific query"""
        if provider not in self.cost_configs:
            return 0.0
        
        config = self.cost_configs[provider]
        
        input_cost = (input_tokens / 1000) * config.input_cost_per_1k_tokens
        output_cost = (output_tokens / 1000) * config.output_cost_per_1k_tokens
        
        return input_cost + output_cost
    
    def record_query_cost(self, provider: str, input_tokens: int, output_tokens: int, 
                         response_time_ms: float, quality_score: Optional[float] = None) -> QueryCostMetrics:
        """Record cost metrics for a query"""
        config = self.cost_configs.get(provider)
        if not config:
            logger.warning("Unknown provider for cost tracking", provider=provider)
            return None
        
        input_cost = (input_tokens / 1000) * config.input_cost_per_1k_tokens
        output_cost = (output_tokens / 1000) * config.output_cost_per_1k_tokens
        total_cost = input_cost + output_cost
        
        metrics = QueryCostMetrics(
            provider=provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            response_time_ms=response_time_ms,
            quality_score=quality_score or config.quality_score
        )
        
        # Add to history
        self.query_history.append(metrics)
        
        # Update daily summary
        self._update_daily_summary(metrics)
        
        # Check budget limits
        self._check_budget_limits(provider)
        
        logger.info("Query cost recorded",
                   provider=provider,
                   total_cost=total_cost,
                   input_tokens=input_tokens,
                   output_tokens=output_tokens,
                   response_time_ms=response_time_ms)
        
        return metrics
    
    def _update_daily_summary(self, metrics: QueryCostMetrics):
        """Update daily cost summary"""
        provider = metrics.provider
        today = datetime.now().date().isoformat()
        
        if provider not in self.daily_costs:
            self.daily_costs[provider] = {}
        
        if today not in self.daily_costs[provider]:
            self.daily_costs[provider][today] = DailyCostSummary(
                provider=provider,
                date=today,
                total_queries=0,
                total_cost=0.0,
                avg_cost_per_query=0.0,
                total_tokens=0,
                avg_response_time_ms=0.0,
                success_rate=1.0,
                budget_utilization=0.0
            )
        
        summary = self.daily_costs[provider][today]
        
        # Update counters
        summary.total_queries += 1
        summary.total_cost += metrics.total_cost
        summary.total_tokens += metrics.input_tokens + metrics.output_tokens
        
        # Update averages
        summary.avg_cost_per_query = summary.total_cost / summary.total_queries
        summary.avg_response_time_ms = (
            (summary.avg_response_time_ms * (summary.total_queries - 1) + metrics.response_time_ms) 
            / summary.total_queries
        )
        
        # Update budget utilization
        config = self.cost_configs[provider]
        summary.budget_utilization = (summary.total_cost / config.daily_budget_limit) * 100
    
    def _check_budget_limits(self, provider: str):
        """Check if provider is approaching budget limits"""
        today = datetime.now().date().isoformat()
        
        if (provider in self.daily_costs and 
            today in self.daily_costs[provider]):
            
            summary = self.daily_costs[provider][today]
            config = self.cost_configs[provider]
            
            utilization = summary.budget_utilization
            
            # Budget alerts
            if utilization >= 90:
                logger.warning("Provider budget nearly exhausted",
                             provider=provider,
                             utilization_percent=utilization,
                             daily_cost=summary.total_cost,
                             budget_limit=config.daily_budget_limit)
                
                # Trigger circuit breaker
                self._trigger_circuit_breaker(provider, "budget_limit")
                
            elif utilization >= 75:
                logger.warning("Provider budget high usage",
                             provider=provider,
                             utilization_percent=utilization)
    
    def _trigger_circuit_breaker(self, provider: str, reason: str):
        """Trigger circuit breaker for a provider"""
        self.circuit_breakers[provider] = {
            'status': 'open',
            'reason': reason,
            'triggered_at': datetime.now(),
            'retry_after': datetime.now() + timedelta(hours=1)
        }
        
        logger.warning("Circuit breaker triggered",
                     provider=provider,
                     reason=reason)
    
    def is_provider_available(self, provider: str) -> bool:
        """Check if provider is available (not circuit broken)"""
        if provider not in self.circuit_breakers:
            return True
        
        breaker = self.circuit_breakers[provider]
        
        if breaker['status'] == 'open':
            # Check if retry time has passed
            if datetime.now() > breaker['retry_after']:
                # Reset circuit breaker
                self.circuit_breakers[provider]['status'] = 'closed'
                logger.info("Circuit breaker reset", provider=provider)
                return True
            else:
                return False
        
        return True
    
    def get_cost_optimized_provider_order(self, query_complexity: str = "medium") -> List[str]:
        """Get provider order optimized for cost while maintaining quality"""
        available_providers = []
        
        for provider, config in self.cost_configs.items():
            if not config.enabled:
                continue
                
            if not self.is_provider_available(provider):
                continue
            
            # Calculate cost-quality score
            cost_factor = 1.0
            if config.cost_tier == CostTier.FREE:
                cost_factor = 0.0
            elif config.cost_tier == CostTier.LOW:
                cost_factor = 0.2
            elif config.cost_tier == CostTier.MEDIUM:
                cost_factor = 0.6
            elif config.cost_tier == CostTier.HIGH:
                cost_factor = 1.0
            
            # Score = quality / (1 + cost_factor)
            # Higher quality and lower cost = better score
            optimization_score = config.quality_score / (1 + cost_factor)
            
            available_providers.append({
                'provider': provider,
                'score': optimization_score,
                'cost_tier': config.cost_tier.value,
                'quality': config.quality_score
            })
        
        # Sort by optimization score (best first)
        available_providers.sort(key=lambda x: x['score'], reverse=True)
        
        provider_order = [p['provider'] for p in available_providers]
        
        logger.info("Cost-optimized provider order calculated",
                   order=provider_order,
                   query_complexity=query_complexity)
        
        return provider_order
    
    def get_daily_cost_report(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Generate daily cost report"""
        if date is None:
            date = datetime.now().date().isoformat()
        
        report = {
            'date': date,
            'total_cost': 0.0,
            'total_queries': 0,
            'providers': {},
            'cost_savings': 0.0,
            'recommendations': []
        }
        
        for provider in self.daily_costs:
            if date in self.daily_costs[provider]:
                summary = self.daily_costs[provider][date]
                report['providers'][provider] = {
                    'cost': summary.total_cost,
                    'queries': summary.total_queries,
                    'avg_cost': summary.avg_cost_per_query,
                    'budget_utilization': summary.budget_utilization,
                    'tokens': summary.total_tokens
                }
                
                report['total_cost'] += summary.total_cost
                report['total_queries'] += summary.total_queries
        
        # Calculate potential savings
        free_queries = report['providers'].get('ollama', {}).get('queries', 0)
        free_queries += report['providers'].get('local_stub', {}).get('queries', 0)
        
        if report['total_queries'] > 0:
            free_percentage = (free_queries / report['total_queries']) * 100
            
            # Estimate savings if more queries used free providers
            if free_percentage < 70:  # Target 70% free usage
                potential_savings = report['total_cost'] * 0.3  # 30% savings target
                report['cost_savings'] = potential_savings
                
                report['recommendations'].append(
                    f"Route {70 - free_percentage:.1f}% more queries to free providers for ${potential_savings:.2f} daily savings"
                )
        
        return report
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get cost optimization recommendations"""
        recommendations = []
        
        # Analyze recent query patterns
        recent_queries = [q for q in self.query_history if 
                         q.timestamp > datetime.now() - timedelta(days=1)]
        
        if not recent_queries:
            return ["No recent queries to analyze"]
        
        # Provider usage analysis
        provider_counts = {}
        total_cost = 0.0
        
        for query in recent_queries:
            provider_counts[query.provider] = provider_counts.get(query.provider, 0) + 1
            total_cost += query.total_cost
        
        total_queries = len(recent_queries)
        
        # Analyze free vs paid usage
        free_queries = provider_counts.get('ollama', 0) + provider_counts.get('local_stub', 0)
        free_percentage = (free_queries / total_queries) * 100
        
        if free_percentage < 50:
            recommendations.append(
                f"Increase free provider usage from {free_percentage:.1f}% to 70% for better cost efficiency"
            )
        
        # Budget utilization warnings
        for provider, config in self.cost_configs.items():
            today = datetime.now().date().isoformat()
            if (provider in self.daily_costs and 
                today in self.daily_costs[provider]):
                
                summary = self.daily_costs[provider][today]
                if summary.budget_utilization > 80:
                    recommendations.append(
                        f"Provider {provider} at {summary.budget_utilization:.1f}% budget - consider alternatives"
                    )
        
        # Performance vs cost recommendations
        if total_cost > 1.0:  # More than $1/day
            recommendations.append(
                "Consider implementing query complexity routing for better cost optimization"
            )
        
        return recommendations if recommendations else ["Cost optimization is performing well"]

# Global cost optimizer instance
cost_optimizer = LLMCostOptimizer()

async def get_cost_optimized_providers(query_complexity: str = "medium") -> List[str]:
    """Get cost-optimized provider order for a query"""
    return cost_optimizer.get_cost_optimized_provider_order(query_complexity)

async def record_llm_cost(provider: str, input_tokens: int, output_tokens: int, 
                         response_time_ms: float, quality_score: Optional[float] = None) -> QueryCostMetrics:
    """Record LLM cost for a query"""
    return cost_optimizer.record_query_cost(provider, input_tokens, output_tokens, 
                                           response_time_ms, quality_score)

async def get_daily_cost_summary(date: Optional[str] = None) -> Dict[str, Any]:
    """Get daily cost summary"""
    return cost_optimizer.get_daily_cost_report(date)

async def get_cost_recommendations() -> List[str]:
    """Get cost optimization recommendations"""
    return cost_optimizer.get_optimization_recommendations()
