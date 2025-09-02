"""
Scoring-Based Model Router for SarvanOM Gateway

This module provides intelligent model selection based on scoring functions that weigh
quality, speed, cost, and context requirements. It respects environment-aware availability
and cost sensitivity while maintaining the existing provider registry structure.

Following MAANG/OpenAI/Perplexity standards for intelligent model orchestration.
"""

import json
import os
import time
import uuid
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from shared.core.logging import get_logger
from shared.llm.provider_order import get_provider_order
from services.gateway.providers import get_available_providers, is_provider_available

logger = get_logger(__name__)


class TaskComplexity(Enum):
    """Task complexity levels for model selection."""
    SIMPLE = 0.2
    MODERATE = 0.5
    COMPLEX = 0.8
    VERY_COMPLEX = 1.0


class ContextRequirement(Enum):
    """Context length requirements."""
    SHORT = 2048
    MEDIUM = 8192
    LONG = 32000
    VERY_LONG = 100000


@dataclass
class ModelCandidate:
    """Model candidate with scoring attributes."""
    name: str
    provider: str
    quality: float
    speed: float
    cost_normalized: float
    max_context: int
    tier: str
    capabilities: List[str]
    requires_key: bool
    enabled: bool
    score: float = 0.0
    availability_score: float = 0.0


@dataclass
class RoutingRequest:
    """Request context for model routing."""
    query: str
    task_complexity: float  # 0-1
    context_requirement: int
    latency_budget_ms: Optional[int] = None
    max_cost: Optional[float] = None
    user_id: Optional[str] = None
    trace_id: Optional[str] = None


@dataclass
class RoutingDecision:
    """Model routing decision result."""
    provider: str
    model: str
    score: float
    reasoning: str
    trace_id: str
    timestamp: float
    alternatives: List[Tuple[str, str, float]]  # (provider, model, score)


class ScoringRouter:
    """
    Intelligent model router that scores and selects the best model for each request.
    
    This router considers:
    - Task complexity (0-1)
    - Context length requirements
    - Latency budget
    - Cost sensitivity
    - Provider availability (key presence)
    - Quality, speed, and cost trade-offs
    """
    
    def __init__(self):
        """Initialize the scoring router with configuration."""
        self.model_catalog = {}
        self.scoring_weights = {}
        self.provider_order = []
        self.context_thresholds = {}
        self._load_configuration()
        
    def _load_configuration(self):
        """Load model catalog and scoring configuration."""
        try:
            # Load model catalog
            catalog_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "config", "model_catalog.json"
            )
            if os.path.exists(catalog_path):
                with open(catalog_path, 'r') as f:
                    catalog_data = json.load(f)
                    self.model_catalog = catalog_data.get("model_catalog", {}).get("models", {})
                    self.scoring_weights = catalog_data.get("model_catalog", {}).get("scoring_weights", {})
                    self.provider_order = catalog_data.get("model_catalog", {}).get("provider_order", {}).get("default", [])
                    self.context_thresholds = catalog_data.get("model_catalog", {}).get("context_thresholds", {})
                    logger.info(f"Loaded model catalog with {len(self.model_catalog)} providers")
            else:
                logger.warning("Model catalog not found, using fallback configuration")
                self._create_fallback_catalog()
                
        except Exception as e:
            logger.error(f"Failed to load model catalog: {e}")
            self._create_fallback_catalog()
    
    def _create_fallback_catalog(self):
        """Create fallback model catalog when config is unavailable."""
        self.model_catalog = {
            "ollama": {
                "llama3.2:3b": {
                    "name": "llama3.2:3b",
                    "provider": "ollama",
                    "quality": 0.6,
                    "speed": 0.9,
                    "cost_normalized": 0.0,
                    "max_context": 4096,
                    "tier": "fast",
                    "capabilities": ["general", "fast", "cost-effective"],
                    "requires_key": False,
                    "enabled": True
                }
            }
        }
        self.scoring_weights = {
            "quality": 0.4,
            "speed": 0.2,
            "cost": 0.3,
            "context_adequacy": 0.1
        }
        self.provider_order = ["ollama", "huggingface", "openai", "anthropic"]
        self.context_thresholds = {
            "short": 2048,
            "medium": 8192,
            "long": 32000,
            "very_long": 100000
        }
        logger.info("Using fallback model catalog")
    
    def _check_provider_availability(self, provider: str) -> bool:
        """Check if a provider is available (has required keys)."""
        if not is_provider_available(provider):
            return False
            
        # Check for API key requirements
        if provider == "openai":
            return bool(os.getenv("OPENAI_API_KEY"))
        elif provider == "anthropic":
            return bool(os.getenv("ANTHROPIC_API_KEY"))
        elif provider == "huggingface":
            # HuggingFace is generally available without keys for free models
            return True
        elif provider == "ollama":
            # Ollama is local, always available if running
            return True
        else:
            return True
    
    def _get_available_models(self, provider: str) -> List[ModelCandidate]:
        """Get available models for a provider."""
        if not self._check_provider_availability(provider):
            return []
            
        provider_models = self.model_catalog.get(provider, {})
        available_models = []
        
        for model_name, model_config in provider_models.items():
            if not model_config.get("enabled", True):
                continue
                
            # Check if model requires a key and if it's available
            if model_config.get("requires_key", False) and not self._check_provider_availability(provider):
                continue
                
            candidate = ModelCandidate(
                name=model_config["name"],
                provider=model_config["provider"],
                quality=model_config["quality"],
                speed=model_config["speed"],
                cost_normalized=model_config["cost_normalized"],
                max_context=model_config["max_context"],
                tier=model_config["tier"],
                capabilities=model_config["capabilities"],
                requires_key=model_config["requires_key"],
                enabled=model_config["enabled"]
            )
            available_models.append(candidate)
            
        return available_models
    
    def _calculate_model_score(
        self, 
        model: ModelCandidate, 
        request: RoutingRequest
    ) -> float:
        """Calculate comprehensive score for a model candidate."""
        weights = self.scoring_weights
        
        # Quality score (higher is better)
        quality_score = model.quality
        
        # Speed score (higher is better, but consider latency budget)
        speed_score = model.speed
        if request.latency_budget_ms and request.latency_budget_ms < 2000:
            # Boost speed for tight latency budgets
            speed_score = min(1.0, speed_score * 1.2)
        
        # Cost score (lower is better, inverted)
        cost_score = 1.0 - model.cost_normalized
        
        # Context adequacy score
        context_adequacy = min(1.0, model.max_context / max(request.context_requirement, 1))
        
        # Task complexity matching
        complexity_bonus = 0.0
        if request.task_complexity > 0.7 and model.tier in ["powerful", "balanced"]:
            complexity_bonus = 0.1
        elif request.task_complexity < 0.3 and model.tier == "fast":
            complexity_bonus = 0.1
        
        # Calculate weighted score
        base_score = (
            weights.get("quality", 0.4) * quality_score +
            weights.get("speed", 0.2) * speed_score +
            weights.get("cost", 0.3) * cost_score +
            weights.get("context_adequacy", 0.1) * context_adequacy
        )
        
        # Apply complexity bonus
        final_score = min(1.0, base_score + complexity_bonus)
        
        return final_score
    
    def _analyze_task_complexity(self, query: str) -> float:
        """Analyze task complexity from query content."""
        query_lower = query.lower()
        complexity_indicators = {
            "analyze": 0.3,
            "compare": 0.4,
            "explain": 0.3,
            "evaluate": 0.5,
            "synthesize": 0.6,
            "create": 0.4,
            "design": 0.5,
            "implement": 0.6,
            "optimize": 0.7,
            "debug": 0.5,
            "refactor": 0.6,
            "architect": 0.8,
            "complex": 0.7,
            "advanced": 0.6,
            "sophisticated": 0.7
        }
        
        # Base complexity from query length
        length_complexity = min(0.5, len(query) / 1000)
        
        # Add complexity from keywords
        keyword_complexity = 0.0
        for keyword, weight in complexity_indicators.items():
            if keyword in query_lower:
                keyword_complexity = max(keyword_complexity, weight)
        
        # Combine length and keyword complexity
        total_complexity = min(1.0, length_complexity + keyword_complexity)
        
        return max(0.1, total_complexity)  # Minimum complexity of 0.1
    
    def _estimate_context_requirement(self, query: str) -> int:
        """Estimate context length requirement from query."""
        # Base context from query length
        base_context = len(query) * 2
        
        # Add context for different query types
        query_lower = query.lower()
        if any(word in query_lower for word in ["analyze", "compare", "synthesize"]):
            base_context *= 3
        elif any(word in query_lower for word in ["code", "implement", "debug"]):
            base_context *= 2
        elif any(word in query_lower for word in ["summarize", "explain"]):
            base_context *= 1.5
        
        # Round to nearest threshold
        thresholds = [2048, 4096, 8192, 16384, 32000, 64000, 128000]
        for threshold in thresholds:
            if base_context <= threshold:
                return threshold
                
        return 128000  # Maximum context
    
    def select_model(self, request: RoutingRequest) -> RoutingDecision:
        """
        Select the best model for the given request using scoring.
        
        This is the main entry point for intelligent model selection.
        """
        trace_id = request.trace_id or str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Analyze request if not provided
            if request.task_complexity == 0:
                request.task_complexity = self._analyze_task_complexity(request.query)
            if request.context_requirement == 0:
                request.context_requirement = self._estimate_context_requirement(request.query)
            
            # Get all available models from all providers
            all_candidates = []
            for provider in self.provider_order:
                provider_models = self._get_available_models(provider)
                all_candidates.extend(provider_models)
            
            if not all_candidates:
                # Fallback to any available model
                logger.warning("No models available, using emergency fallback")
                return self._get_emergency_fallback(trace_id)
            
            # Score all candidates
            scored_candidates = []
            for candidate in all_candidates:
                candidate.score = self._calculate_model_score(candidate, request)
                scored_candidates.append(candidate)
            
            # Sort by score (descending)
            scored_candidates.sort(key=lambda x: x.score, reverse=True)
            
            # Select best candidate
            best_candidate = scored_candidates[0]
            
            # Prepare alternatives (top 3)
            alternatives = [
                (c.provider, c.name, c.score) 
                for c in scored_candidates[:3]
            ]
            
            # Generate reasoning
            reasoning = self._generate_reasoning(best_candidate, request, scored_candidates)
            
            # Create decision
            decision = RoutingDecision(
                provider=best_candidate.provider,
                model=best_candidate.name,
                score=best_candidate.score,
                reasoning=reasoning,
                trace_id=trace_id,
                timestamp=time.time(),
                alternatives=alternatives
            )
            
            # Log decision
            self._log_decision(decision, request)
            
            return decision
            
        except Exception as e:
            logger.error(f"Model selection failed: {e}")
            return self._get_emergency_fallback(trace_id)
    
    def _generate_reasoning(
        self, 
        best_candidate: ModelCandidate, 
        request: RoutingRequest,
        all_candidates: List[ModelCandidate]
    ) -> str:
        """Generate human-readable reasoning for the selection."""
        reasons = []
        
        # Quality reasoning
        if best_candidate.quality > 0.8:
            reasons.append("high quality")
        elif best_candidate.quality > 0.6:
            reasons.append("good quality")
        
        # Speed reasoning
        if best_candidate.speed > 0.8:
            reasons.append("fast response")
        elif request.latency_budget_ms and request.latency_budget_ms < 2000:
            reasons.append("meets latency budget")
        
        # Cost reasoning
        if best_candidate.cost_normalized == 0.0:
            reasons.append("free")
        elif best_candidate.cost_normalized < 0.3:
            reasons.append("cost-effective")
        
        # Context reasoning
        if best_candidate.max_context >= request.context_requirement:
            reasons.append("sufficient context")
        
        # Complexity reasoning
        if request.task_complexity > 0.7 and best_candidate.tier == "powerful":
            reasons.append("handles complex tasks")
        elif request.task_complexity < 0.3 and best_candidate.tier == "fast":
            reasons.append("efficient for simple tasks")
        
        if not reasons:
            reasons.append("best overall score")
        
        return f"Selected {best_candidate.provider}/{best_candidate.name} for {', '.join(reasons)}"
    
    def _log_decision(self, decision: RoutingDecision, request: RoutingRequest):
        """Log the routing decision with trace ID."""
        logger.info(
            f"Model routing decision: {decision.provider}/{decision.model} "
            f"(score: {decision.score:.3f}, trace: {decision.trace_id})",
            extra={
                "trace_id": decision.trace_id,
                "provider": decision.provider,
                "model": decision.model,
                "score": decision.score,
                "reasoning": decision.reasoning,
                "task_complexity": request.task_complexity,
                "context_requirement": request.context_requirement,
                "user_id": request.user_id,
                "alternatives": decision.alternatives
            }
        )
    
    def _get_emergency_fallback(self, trace_id: str) -> RoutingDecision:
        """Get emergency fallback when no models are available."""
        return RoutingDecision(
            provider="ollama",
            model="llama3.2:3b",
            score=0.5,
            reasoning="Emergency fallback - no other models available",
            trace_id=trace_id,
            timestamp=time.time(),
            alternatives=[("ollama", "llama3.2:3b", 0.5)]
        )
    
    def get_available_models_summary(self) -> Dict[str, Any]:
        """Get summary of available models by provider."""
        summary = {}
        for provider in self.provider_order:
            models = self._get_available_models(provider)
            summary[provider] = {
                "available": len(models) > 0,
                "model_count": len(models),
                "models": [m.name for m in models]
            }
        return summary


# Global scoring router instance
scoring_router = ScoringRouter()


def get_scoring_router() -> ScoringRouter:
    """Get the global scoring router instance."""
    return scoring_router


def select_model_with_scoring(
    query: str,
    task_complexity: Optional[float] = None,
    context_requirement: Optional[int] = None,
    latency_budget_ms: Optional[int] = None,
    max_cost: Optional[float] = None,
    user_id: Optional[str] = None,
    trace_id: Optional[str] = None
) -> RoutingDecision:
    """
    Convenience function for model selection with scoring.
    
    This is the main entry point for intelligent model selection.
    """
    router = get_scoring_router()
    
    request = RoutingRequest(
        query=query,
        task_complexity=task_complexity or 0.0,
        context_requirement=context_requirement or 0,
        latency_budget_ms=latency_budget_ms,
        max_cost=max_cost,
        user_id=user_id,
        trace_id=trace_id
    )
    
    return router.select_model(request)


# TODO: Add A/B testing framework for model selection
# TODO: Add real-time performance feedback integration
# TODO: Add cost tracking and budget enforcement
# TODO: Add model performance metrics collection
# TODO: Add dynamic weight adjustment based on user feedback
