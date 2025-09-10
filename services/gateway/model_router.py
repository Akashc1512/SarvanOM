"""
Centralized Model Router for SarvanOM Gateway

This module provides a single source of truth for model routing decisions,
integrating with the existing model_selection.json configuration and
environment variables to ensure consistent model selection across all services.

Following MAANG/OpenAI/Perplexity standards for model orchestration.
"""

import json
import os
import time
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from shared.core.config import get_central_config
from shared.core.logging import get_logger

logger = get_logger(__name__)


class ModelTier(Enum):
    """Model performance tiers for routing decisions."""
    FAST = "fast"
    BALANCED = "balanced"
    POWERFUL = "powerful"


class QueryComplexity(Enum):
    """Query complexity levels for model selection."""
    SIMPLE = "simple"
    SIMPLE_FACTUAL = "simple_factual"
    MODERATE = "moderate"
    COMPLEX = "complex"
    COMPLEX_ANALYTICAL = "complex_analytical"
    RESEARCH_INTENSIVE = "research_intensive"
    RESEARCH_SYNTHESIS = "research_synthesis"
    MULTI_DOMAIN = "multi_domain"


class QueryCategory(Enum):
    """Query categories for specialized model routing."""
    GENERAL_FACTUAL = "general_factual"
    CODE = "code"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    ANALYTICAL = "analytical"
    COMPARATIVE = "comparative"
    PROCEDURAL = "procedural"
    CREATIVE = "creative"
    OPINION = "opinion"


@dataclass
class ModelSelection:
    """Model selection result with metadata."""
    model_name: str
    provider: str
    tier: ModelTier
    cost_per_1k_tokens: float
    max_tokens: int
    capabilities: List[str]
    fallback_models: List[str]
    selection_reason: str
    estimated_cost: float
    confidence_score: float


@dataclass
class RoutingContext:
    """Context for model routing decisions."""
    query: str
    query_length: int
    complexity: QueryComplexity
    category: QueryCategory
    user_id: Optional[str] = None
    max_cost: Optional[float] = None
    timeout_seconds: Optional[int] = None
    preferred_tier: Optional[ModelTier] = None


class ModelRouter:
    """
    Centralized model router that provides a single source of truth
    for model selection across all services.
    """
    
    def __init__(self):
        """Initialize the model router with configuration."""
        self.config = None
        self.model_configs = {}
        self.selection_history = []
        self.max_history_size = 1000
        self._load_configuration()
        
    def _load_configuration(self):
        """Load model configuration from config files and environment."""
        try:
            # Load from model_selection.json
            config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "model_selection.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
                    self.model_configs = self.config.get("model_selection", {}).get("model_configs", {})
                    logger.info(f"Loaded {len(self.model_configs)} model configurations")
            else:
                logger.warning("model_selection.json not found, using fallback configuration")
                self._create_fallback_config()
                
            # Override with environment variables
            self._apply_environment_overrides()
            
        except Exception as e:
            logger.error(f"Failed to load model configuration: {e}")
            self._create_fallback_config()
    
    def _create_fallback_config(self):
        """Create fallback configuration when config files are unavailable."""
        self.config = {
            "model_selection": {
                "enabled": True,
                "default_behavior": "dynamic",
                "fallback_behavior": "fast",
                "cost_optimization": {
                    "enabled": True,
                    "max_cost_per_query": 0.20,
                    "prefer_fast_models": True
                },
                "model_configs": {
                    "gpt-3.5-turbo": {
                        "provider": "openai",
                        "tier": "fast",
                        "cost_per_1k_tokens": 0.0015,
                        "max_tokens": 4096,
                        "capabilities": ["general", "fast", "cost-effective"],
                        "fallback_models": ["gpt-4o-mini", "claude-3-haiku"],
                        "enabled": True
                    },
                    "llama3.2:3b": {
                        "provider": "ollama",
                        "tier": "fast",
                        "cost_per_1k_tokens": 0.0,
                        "max_tokens": 4096,
                        "capabilities": ["general", "fast", "cost-effective"],
                        "fallback_models": ["llama3.2:8b", "phi3:mini"],
                        "enabled": True
                    }
                }
            }
        }
        self.model_configs = self.config["model_selection"]["model_configs"]
        logger.info("Using fallback model configuration")
    
    def _apply_environment_overrides(self):
        """Apply environment variable overrides to configuration."""
        # Check for environment-based model preferences
        preferred_provider = os.getenv("PREFERRED_MODEL_PROVIDER")
        if preferred_provider:
            logger.info(f"Environment override: preferred provider = {preferred_provider}")
        
        # Check for cost optimization settings
        max_cost = os.getenv("MAX_COST_PER_QUERY")
        if max_cost:
            try:
                self.config["model_selection"]["cost_optimization"]["max_cost_per_query"] = float(max_cost)
                logger.info(f"Environment override: max cost per query = {max_cost}")
            except ValueError:
                logger.warning(f"Invalid MAX_COST_PER_QUERY value: {max_cost}")
        
        # Check for model enablement flags
        use_ollama = os.getenv("USE_OLLAMA", "true").lower() == "true"
        use_openai = os.getenv("USE_OPENAI", "true").lower() == "true"
        use_anthropic = os.getenv("USE_ANTHROPIC", "true").lower() == "true"
        
        # Disable models based on environment flags
        for model_name, config in self.model_configs.items():
            provider = config.get("provider", "").lower()
            if provider == "ollama" and not use_ollama:
                config["enabled"] = False
            elif provider == "openai" and not use_openai:
                config["enabled"] = False
            elif provider == "anthropic" and not use_anthropic:
                config["enabled"] = False
    
    def analyze_query_complexity(self, query: str) -> QueryComplexity:
        """Analyze query complexity based on length and content."""
        query_length = len(query)
        
        # Simple heuristics for complexity analysis
        if query_length <= 100:
            return QueryComplexity.SIMPLE
        elif query_length <= 500:
            return QueryComplexity.MODERATE
        else:
            return QueryComplexity.COMPLEX
    
    def categorize_query(self, query: str) -> QueryCategory:
        """Categorize query based on content analysis."""
        query_lower = query.lower()
        
        # Simple keyword-based categorization
        if any(keyword in query_lower for keyword in ["code", "programming", "function", "class", "api"]):
            return QueryCategory.CODE
        elif any(keyword in query_lower for keyword in ["graph", "relationship", "connection", "network"]):
            return QueryCategory.KNOWLEDGE_GRAPH
        elif any(keyword in query_lower for keyword in ["analyze", "analysis", "compare", "evaluate"]):
            return QueryCategory.ANALYTICAL
        elif any(keyword in query_lower for keyword in ["compare", "versus", "vs", "difference"]):
            return QueryCategory.COMPARATIVE
        elif any(keyword in query_lower for keyword in ["how to", "steps", "process", "procedure"]):
            return QueryCategory.PROCEDURAL
        elif any(keyword in query_lower for keyword in ["creative", "imagine", "design", "write"]):
            return QueryCategory.CREATIVE
        elif any(keyword in query_lower for keyword in ["opinion", "think", "believe", "feel"]):
            return QueryCategory.OPINION
        else:
            return QueryCategory.GENERAL_FACTUAL
    
    def select_model(self, context: RoutingContext) -> ModelSelection:
        """
        Select the optimal model based on routing context.
        
        This is the main method that provides a single source of truth
        for model selection across all services.
        """
        try:
            # Get category preferences
            category_prefs = self.config["model_selection"].get("category_preferences", {})
            category_key = context.category.value
            
            if category_key in category_prefs:
                preferred_tier = ModelTier(category_prefs[category_key]["preferred_tier"])
                fallback_tier = ModelTier(category_prefs[category_key]["fallback_tier"])
            else:
                # Use complexity-based selection
                complexity_thresholds = self.config["model_selection"].get("complexity_thresholds", {})
                complexity_key = context.complexity.value
                
                if complexity_key in complexity_thresholds:
                    preferred_tier = ModelTier(complexity_thresholds[complexity_key]["preferred_tier"])
                else:
                    preferred_tier = ModelTier.FAST  # Default fallback
            
            # Find best model for the tier
            selected_model = self._find_best_model_for_tier(
                preferred_tier, 
                context.max_cost,
                context.query_length
            )
            
            if not selected_model:
                # Fallback to any available model
                selected_model = self._find_any_available_model()
            
            if not selected_model:
                raise ValueError("No models available for selection")
            
            # Calculate estimated cost
            estimated_tokens = min(context.query_length * 2, selected_model["max_tokens"])
            estimated_cost = (estimated_tokens / 1000) * selected_model["cost_per_1k_tokens"]
            
            # Create selection result
            selection = ModelSelection(
                model_name=selected_model["name"],
                provider=selected_model["provider"],
                tier=ModelTier(selected_model["tier"]),
                cost_per_1k_tokens=selected_model["cost_per_1k_tokens"],
                max_tokens=selected_model["max_tokens"],
                capabilities=selected_model["capabilities"],
                fallback_models=selected_model["fallback_models"],
                selection_reason=f"Selected {selected_model['tier']} tier model for {context.complexity.value} {context.category.value} query",
                estimated_cost=estimated_cost,
                confidence_score=0.9 if selected_model["tier"] == preferred_tier.value else 0.7
            )
            
            # Record selection for monitoring
            self._record_selection(selection, context)
            
            logger.info(
                f"Model selected: {selection.model_name} "
                f"(tier: {selection.tier.value}, cost: ${selection.estimated_cost:.4f})",
                extra={
                    "model_name": selection.model_name,
                    "provider": selection.provider,
                    "tier": selection.tier.value,
                    "estimated_cost": selection.estimated_cost,
                    "selection_reason": selection.selection_reason
                }
            )
            
            return selection
            
        except Exception as e:
            logger.error(f"Model selection failed: {e}")
            # Return emergency fallback
            return self._get_emergency_fallback()
    
    def _find_best_model_for_tier(self, tier: ModelTier, max_cost: Optional[float], query_length: int) -> Optional[Dict[str, Any]]:
        """Find the best model for a specific tier."""
        available_models = []
        
        for model_name, config in self.model_configs.items():
            if not config.get("enabled", True):
                continue
                
            if config.get("tier") != tier.value:
                continue
            
            # Check cost constraints
            if max_cost is not None:
                estimated_tokens = min(query_length * 2, config["max_tokens"])
                estimated_cost = (estimated_tokens / 1000) * config["cost_per_1k_tokens"]
                if estimated_cost > max_cost:
                    continue
            
            # Prefer free models (cost = 0)
            priority = 0 if config["cost_per_1k_tokens"] == 0 else 1
            
            available_models.append({
                "name": model_name,
                "priority": priority,
                **config
            })
        
        if not available_models:
            return None
        
        # Sort by priority (free models first) and cost
        available_models.sort(key=lambda x: (x["priority"], x["cost_per_1k_tokens"]))
        return available_models[0]
    
    def _find_any_available_model(self) -> Optional[Dict[str, Any]]:
        """Find any available model as last resort."""
        for model_name, config in self.model_configs.items():
            if config.get("enabled", True):
                return {"name": model_name, **config}
        return None
    
    def _get_emergency_fallback(self) -> ModelSelection:
        """Get emergency fallback model selection."""
        return ModelSelection(
            model_name="llama3.2:3b",
            provider="ollama",
            tier=ModelTier.FAST,
            cost_per_1k_tokens=0.0,
            max_tokens=4096,
            capabilities=["general", "fast", "cost-effective"],
            fallback_models=[],
            selection_reason="Emergency fallback - no other models available",
            estimated_cost=0.0,
            confidence_score=0.5
        )
    
    def _record_selection(self, selection: ModelSelection, context: RoutingContext):
        """Record model selection for monitoring and analytics."""
        record = {
            "timestamp": time.time(),
            "model_name": selection.model_name,
            "provider": selection.provider,
            "tier": selection.tier.value,
            "query_length": context.query_length,
            "complexity": context.complexity.value,
            "category": context.category.value,
            "estimated_cost": selection.estimated_cost,
            "confidence_score": selection.confidence_score,
            "user_id": context.user_id
        }
        
        self.selection_history.append(record)
        
        # Maintain history size limit
        if len(self.selection_history) > self.max_history_size:
            self.selection_history = self.selection_history[-self.max_history_size:]
    
    def get_selection_stats(self) -> Dict[str, Any]:
        """Get statistics about model selections."""
        if not self.selection_history:
            return {"total_selections": 0}
        
        # Calculate statistics
        total_selections = len(self.selection_history)
        model_counts = {}
        provider_counts = {}
        tier_counts = {}
        total_cost = 0.0
        
        for record in self.selection_history:
            model_name = record["model_name"]
            provider = record["provider"]
            tier = record["tier"]
            cost = record["estimated_cost"]
            
            model_counts[model_name] = model_counts.get(model_name, 0) + 1
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            total_cost += cost
        
        return {
            "total_selections": total_selections,
            "model_distribution": model_counts,
            "provider_distribution": provider_counts,
            "tier_distribution": tier_counts,
            "total_estimated_cost": total_cost,
            "average_cost_per_selection": total_cost / total_selections if total_selections > 0 else 0.0
        }
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models with their configurations."""
        available = {}
        for model_name, config in self.model_configs.items():
            if config.get("enabled", True):
                available[model_name] = {
                    "provider": config["provider"],
                    "tier": config["tier"],
                    "cost_per_1k_tokens": config["cost_per_1k_tokens"],
                    "max_tokens": config["max_tokens"],
                    "capabilities": config["capabilities"],
                    "fallback_models": config["fallback_models"]
                }
        return available


# Global model router instance
model_router = ModelRouter()


def get_model_router() -> ModelRouter:
    """Get the global model router instance."""
    return model_router


def select_model_for_query(
    query: str,
    user_id: Optional[str] = None,
    max_cost: Optional[float] = None,
    timeout_seconds: Optional[int] = None,
    preferred_tier: Optional[ModelTier] = None
) -> ModelSelection:
    """
    Convenience function for model selection.
    
    This is the main entry point for model selection across all services.
    """
    router = get_model_router()
    
    # Create routing context
    context = RoutingContext(
        query=query,
        query_length=len(query),
        complexity=router.analyze_query_complexity(query),
        category=router.categorize_query(query),
        user_id=user_id,
        max_cost=max_cost,
        timeout_seconds=timeout_seconds,
        preferred_tier=preferred_tier
    )
    
    return router.select_model(context)


# TODO: Add integration with existing provider clients
# TODO: Add circuit breaker integration for model failures
# TODO: Add A/B testing framework for model selection
# TODO: Add real-time cost tracking and budget enforcement
# TODO: Add model performance metrics collection
