"""
Dynamic Model Selector - Universal Knowledge Platform
Intelligently selects the optimal LLM model based on query characteristics.

This module provides dynamic model selection functionality that analyzes query
complexity and type to choose the most appropriate LLM model for optimal
performance and cost efficiency.

Features:
- Query complexity analysis
- Model selection based on query type
- Cost optimization
- Fallback mechanisms
- Configurable thresholds
- Performance monitoring

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import os
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from shared.core.query_classifier import (
    QueryClassifier,
    QueryCategory,
    QueryComplexity,
    QueryClassification,
)
from shared.core.llm_client_v3 import LLMProvider, LLMModel

logger = logging.getLogger(__name__)


class ModelTier(str, Enum):
    """Model tiers for different complexity levels."""

    FAST = "fast"  # Fast, cost-effective models for simple queries
    BALANCED = "balanced"  # Balanced models for moderate complexity
    POWERFUL = "powerful"  # High-performance models for complex queries
    SPECIALIZED = "specialized"  # Specialized models for specific domains


@dataclass
class ModelConfig:
    """Configuration for a specific model."""

    provider: LLMProvider
    model: str
    tier: ModelTier
    cost_per_1k_tokens: float
    max_tokens: int
    capabilities: List[str] = field(default_factory=list)
    fallback_models: List[str] = field(default_factory=list)
    enabled: bool = True


@dataclass
class ModelSelectionResult:
    """Result of model selection process."""

    selected_model: str
    selected_provider: LLMProvider
    model_tier: ModelTier
    confidence: float
    reasoning: str
    fallback_models: List[str] = field(default_factory=list)
    estimated_cost: float = 0.0
    selection_time_ms: float = 0.0


class DynamicModelSelector:
    """
    Intelligently selects the optimal LLM model based on query characteristics.

    Uses query classification and complexity analysis to choose the most
    appropriate model for optimal performance and cost efficiency.
    """

    def __init__(self):
        """Initialize the model selector with configuration."""
        self.query_classifier = QueryClassifier()
        self.model_configs = self._initialize_model_configs()
        self.selection_thresholds = self._load_selection_thresholds()
        self.selection_history = []

        logger.info("✅ DynamicModelSelector initialized successfully")

    def _initialize_model_configs(self) -> Dict[str, ModelConfig]:
        """Initialize model configurations with capabilities and costs."""
        configs = {
            # Fast models for simple queries
            "gpt-3.5-turbo": ModelConfig(
                provider=LLMProvider.OPENAI,
                model="gpt-3.5-turbo",
                tier=ModelTier.FAST,
                cost_per_1k_tokens=0.0015,  # $0.0015 per 1K tokens
                max_tokens=4096,
                capabilities=["general", "fast", "cost-effective"],
                fallback_models=["gpt-4o-mini", "claude-3-haiku"],
            ),
            "gpt-4o-mini": ModelConfig(
                provider=LLMProvider.OPENAI,
                model="gpt-4o-mini",
                tier=ModelTier.FAST,
                cost_per_1k_tokens=0.00015,  # $0.00015 per 1K tokens
                max_tokens=128000,
                capabilities=["general", "fast", "very-cost-effective"],
                fallback_models=["gpt-3.5-turbo", "claude-3-haiku"],
            ),
            "claude-3-haiku": ModelConfig(
                provider=LLMProvider.ANTHROPIC,
                model="claude-3-haiku-20240307",
                tier=ModelTier.FAST,
                cost_per_1k_tokens=0.00025,  # $0.00025 per 1K tokens
                max_tokens=200000,
                capabilities=["general", "fast", "cost-effective"],
                fallback_models=["gpt-3.5-turbo", "gpt-4o-mini"],
            ),
            # Balanced models for moderate complexity
            "gpt-4": ModelConfig(
                provider=LLMProvider.OPENAI,
                model="gpt-4",
                tier=ModelTier.BALANCED,
                cost_per_1k_tokens=0.03,  # $0.03 per 1K tokens
                max_tokens=8192,
                capabilities=["general", "reasoning", "analysis"],
                fallback_models=["gpt-4o", "claude-3-sonnet"],
            ),
            "gpt-4o": ModelConfig(
                provider=LLMProvider.OPENAI,
                model="gpt-4o",
                tier=ModelTier.BALANCED,
                cost_per_1k_tokens=0.005,  # $0.005 per 1K tokens
                max_tokens=128000,
                capabilities=["general", "reasoning", "analysis", "vision"],
                fallback_models=["gpt-4", "claude-3-sonnet"],
            ),
            "claude-3-sonnet": ModelConfig(
                provider=LLMProvider.ANTHROPIC,
                model="claude-3-sonnet-20240229",
                tier=ModelTier.BALANCED,
                cost_per_1k_tokens=0.003,  # $0.003 per 1K tokens
                max_tokens=200000,
                capabilities=["general", "reasoning", "analysis"],
                fallback_models=["gpt-4", "gpt-4o"],
            ),
            # Powerful models for complex queries
            "gpt-4-turbo": ModelConfig(
                provider=LLMProvider.OPENAI,
                model="gpt-4-turbo-preview",
                tier=ModelTier.POWERFUL,
                cost_per_1k_tokens=0.01,  # $0.01 per 1K tokens
                max_tokens=128000,
                capabilities=["general", "advanced-reasoning", "complex-analysis"],
                fallback_models=["gpt-4", "claude-3-opus"],
            ),
            "claude-3-opus": ModelConfig(
                provider=LLMProvider.ANTHROPIC,
                model="claude-3-opus-20240229",
                tier=ModelTier.POWERFUL,
                cost_per_1k_tokens=0.015,  # $0.015 per 1K tokens
                max_tokens=200000,
                capabilities=["general", "advanced-reasoning", "complex-analysis"],
                fallback_models=["gpt-4-turbo", "gpt-4"],
            ),
            # Specialized models for specific domains
            "code-davinci": ModelConfig(
                provider=LLMProvider.OPENAI,
                model="code-davinci-002",  # Note: This model may be deprecated
                tier=ModelTier.SPECIALIZED,
                cost_per_1k_tokens=0.02,  # $0.02 per 1K tokens
                max_tokens=8000,
                capabilities=["code", "programming", "technical"],
                fallback_models=["gpt-4", "claude-3-sonnet"],
                enabled=False,  # Disabled as it may be deprecated
            ),
            # Ollama models (Local - Free)
            "llama3.2:3b": ModelConfig(
                provider=LLMProvider.OLLAMA,
                model="llama3.2:3b",
                tier=ModelTier.FAST,
                cost_per_1k_tokens=0.0,  # Free local inference
                max_tokens=4096,
                capabilities=["general", "fast", "cost-effective"],
                fallback_models=["llama3.2:8b", "phi3:mini"],
            ),
            "llama3.2:8b": ModelConfig(
                provider=LLMProvider.OLLAMA,
                model="llama3.2:8b",
                tier=ModelTier.BALANCED,
                cost_per_1k_tokens=0.0,  # Free local inference
                max_tokens=8192,
                capabilities=["general", "reasoning", "analysis"],
                fallback_models=["llama3.2:3b", "codellama:7b"],
            ),
            "codellama:7b": ModelConfig(
                provider=LLMProvider.OLLAMA,
                model="codellama:7b",
                tier=ModelTier.BALANCED,
                cost_per_1k_tokens=0.0,  # Free local inference
                max_tokens=8192,
                capabilities=["code", "reasoning", "analysis"],
                fallback_models=["llama3.2:8b", "llama3.2:3b"],
            ),
            "phi3:mini": ModelConfig(
                provider=LLMProvider.OLLAMA,
                model="phi3:mini",
                tier=ModelTier.FAST,
                cost_per_1k_tokens=0.0,  # Free local inference
                max_tokens=2048,
                capabilities=["general", "fast", "very-cost-effective"],
                fallback_models=["llama3.2:3b", "llama3.2:8b"],
            ),
            "llama3.2:70b": ModelConfig(
                provider=LLMProvider.OLLAMA,
                model="llama3.2:70b",
                tier=ModelTier.POWERFUL,
                cost_per_1k_tokens=0.0,  # Free local inference
                max_tokens=16384,
                capabilities=["general", "advanced-reasoning", "complex-analysis"],
                fallback_models=["llama3.2:8b", "mixtral:8x7b"],
            ),
            "mixtral:8x7b": ModelConfig(
                provider=LLMProvider.OLLAMA,
                model="mixtral:8x7b",
                tier=ModelTier.POWERFUL,
                cost_per_1k_tokens=0.0,  # Free local inference
                max_tokens=16384,
                capabilities=["general", "advanced-reasoning", "complex-analysis"],
                fallback_models=["llama3.2:70b", "llama3.2:8b"],
            ),
            # Hugging Face models (Free API)
            "microsoft/DialoGPT-medium": ModelConfig(
                provider=LLMProvider.HUGGINGFACE,
                model="microsoft/DialoGPT-medium",
                tier=ModelTier.FAST,
                cost_per_1k_tokens=0.0,  # Free API tier
                max_tokens=1024,
                capabilities=["general", "fast", "conversation"],
                fallback_models=["microsoft/DialoGPT-large", "distilgpt2"],
            ),
            "microsoft/DialoGPT-large": ModelConfig(
                provider=LLMProvider.HUGGINGFACE,
                model="microsoft/DialoGPT-large",
                tier=ModelTier.BALANCED,
                cost_per_1k_tokens=0.0,  # Free API tier
                max_tokens=2048,
                capabilities=["general", "reasoning", "conversation"],
                fallback_models=[
                    "microsoft/DialoGPT-medium",
                    "EleutherAI/gpt-neo-125M",
                ],
            ),
            "distilgpt2": ModelConfig(
                provider=LLMProvider.HUGGINGFACE,
                model="distilgpt2",
                tier=ModelTier.FAST,
                cost_per_1k_tokens=0.0,  # Free API tier
                max_tokens=1024,
                capabilities=["general", "fast", "text-generation"],
                fallback_models=[
                    "microsoft/DialoGPT-medium",
                    "EleutherAI/gpt-neo-125M",
                ],
            ),
            "EleutherAI/gpt-neo-125M": ModelConfig(
                provider=LLMProvider.HUGGINGFACE,
                model="EleutherAI/gpt-neo-125M",
                tier=ModelTier.BALANCED,
                cost_per_1k_tokens=0.0,  # Free API tier
                max_tokens=2048,
                capabilities=["general", "reasoning", "text-generation"],
                fallback_models=[
                    "microsoft/DialoGPT-large",
                    "microsoft/DialoGPT-medium",
                ],
            ),
            "Salesforce/codegen-350M-mono": ModelConfig(
                provider=LLMProvider.HUGGINGFACE,
                model="Salesforce/codegen-350M-mono",
                tier=ModelTier.BALANCED,
                cost_per_1k_tokens=0.0,  # Free API tier
                max_tokens=2048,
                capabilities=["code", "programming", "generation"],
                fallback_models=["codellama:7b", "llama3.2:8b"],
            ),
        }

        return configs

    def _load_selection_thresholds(self) -> Dict[str, Any]:
        """Load selection thresholds from environment or use defaults."""
        return {
            "complexity_thresholds": {
                "simple": {
                    "max_tokens": 1000,
                    "preferred_tier": ModelTier.FAST,
                    "max_cost_per_query": 0.01,
                },
                "moderate": {
                    "max_tokens": 3000,
                    "preferred_tier": ModelTier.BALANCED,
                    "max_cost_per_query": 0.05,
                },
                "complex": {
                    "max_tokens": 8000,
                    "preferred_tier": ModelTier.POWERFUL,
                    "max_cost_per_query": 0.20,
                },
            },
            "category_preferences": {
                QueryCategory.GENERAL_FACTUAL: {
                    "preferred_tier": ModelTier.FAST,
                    "fallback_tier": ModelTier.BALANCED,
                },
                QueryCategory.CODE: {
                    "preferred_tier": ModelTier.BALANCED,
                    "fallback_tier": ModelTier.POWERFUL,
                },
                QueryCategory.KNOWLEDGE_GRAPH: {
                    "preferred_tier": ModelTier.BALANCED,
                    "fallback_tier": ModelTier.POWERFUL,
                },
                QueryCategory.ANALYTICAL: {
                    "preferred_tier": ModelTier.POWERFUL,
                    "fallback_tier": ModelTier.BALANCED,
                },
                QueryCategory.COMPARATIVE: {
                    "preferred_tier": ModelTier.BALANCED,
                    "fallback_tier": ModelTier.POWERFUL,
                },
                QueryCategory.PROCEDURAL: {
                    "preferred_tier": ModelTier.BALANCED,
                    "fallback_tier": ModelTier.FAST,
                },
                QueryCategory.CREATIVE: {
                    "preferred_tier": ModelTier.POWERFUL,
                    "fallback_tier": ModelTier.BALANCED,
                },
                QueryCategory.OPINION: {
                    "preferred_tier": ModelTier.BALANCED,
                    "fallback_tier": ModelTier.FAST,
                },
            },
        }

    async def select_model(
        self,
        query: str,
        estimated_tokens: Optional[int] = None,
        force_tier: Optional[ModelTier] = None,
    ) -> ModelSelectionResult:
        """
        Select the optimal model based on query characteristics.

        Args:
            query: The user query
            estimated_tokens: Estimated token count for the request
            force_tier: Force selection of a specific tier (for testing)

        Returns:
            ModelSelectionResult with selected model and reasoning
        """
        start_time = datetime.now()

        try:
            # Classify the query
            classification = await self.query_classifier.classify_query(query)

            # Estimate tokens if not provided
            if estimated_tokens is None:
                estimated_tokens = self._estimate_tokens(query)

            # Determine optimal tier
            if force_tier:
                optimal_tier = force_tier
                reasoning = f"Forced tier selection: {force_tier}"
            else:
                optimal_tier = self._determine_optimal_tier(
                    classification, estimated_tokens
                )
                reasoning = self._generate_selection_reasoning(
                    classification, estimated_tokens, optimal_tier
                )

            # Select the best model for the tier
            selected_model, confidence = self._select_best_model_for_tier(
                optimal_tier, classification.category, estimated_tokens
            )

            # Get model configuration
            model_config = self.model_configs.get(selected_model)
            if not model_config:
                raise ValueError(f"Model {selected_model} not found in configuration")

            # Calculate estimated cost
            estimated_cost = self._calculate_estimated_cost(
                model_config, estimated_tokens
            )

            # Get fallback models
            fallback_models = self._get_fallback_models(model_config, optimal_tier)

            selection_time = (datetime.now() - start_time).total_seconds() * 1000

            result = ModelSelectionResult(
                selected_model=selected_model,
                selected_provider=model_config.provider,
                model_tier=optimal_tier,
                confidence=confidence,
                reasoning=reasoning,
                fallback_models=fallback_models,
                estimated_cost=estimated_cost,
                selection_time_ms=selection_time,
            )

            # Log selection for monitoring
            self._log_model_selection(result, classification, estimated_tokens)

            return result

        except Exception as e:
            logger.error(f"Model selection failed: {e}")
            # Return a safe fallback
            return self._get_fallback_selection()

    def _determine_optimal_tier(
        self, classification: QueryClassification, estimated_tokens: int
    ) -> ModelTier:
        """Determine the optimal model tier based on query characteristics."""

        # Get category preferences
        category_prefs = self.selection_thresholds["category_preferences"].get(
            classification.category,
            {"preferred_tier": ModelTier.BALANCED, "fallback_tier": ModelTier.FAST},
        )

        # Get complexity thresholds
        complexity_thresholds = self.selection_thresholds["complexity_thresholds"]

        # Determine tier based on complexity and category
        if classification.complexity == QueryComplexity.SIMPLE:
            # Simple queries can use fast models unless category requires more
            if category_prefs["preferred_tier"] == ModelTier.FAST:
                return ModelTier.FAST
            else:
                return category_prefs["preferred_tier"]

        elif classification.complexity == QueryComplexity.MODERATE:
            # Moderate queries use balanced models or category preference
            return category_prefs["preferred_tier"]

        elif classification.complexity == QueryComplexity.COMPLEX:
            # Complex queries use powerful models
            return ModelTier.POWERFUL

        # Default to balanced
        return ModelTier.BALANCED

    def _select_best_model_for_tier(
        self, tier: ModelTier, category: QueryCategory, estimated_tokens: int
    ) -> Tuple[str, float]:
        """Select the best model for a given tier and category."""

        # Get available models for the tier
        available_models = [
            model_name
            for model_name, config in self.model_configs.items()
            if config.tier == tier and config.enabled
        ]

        if not available_models:
            # Fallback to balanced tier if no models available
            available_models = [
                model_name
                for model_name, config in self.model_configs.items()
                if config.tier == ModelTier.BALANCED and config.enabled
            ]

        if not available_models:
            # Final fallback to any available model
            available_models = [
                model_name
                for model_name, config in self.model_configs.items()
                if config.enabled
            ]

        if not available_models:
            raise ValueError("No available models found")

        # Score models based on category and cost
        model_scores = {}
        for model_name in available_models:
            config = self.model_configs[model_name]
            score = self._calculate_model_score(config, category, estimated_tokens)
            model_scores[model_name] = score

        # Select the best model
        best_model = max(model_scores, key=model_scores.get)
        confidence = model_scores[best_model]

        return best_model, confidence

    def _calculate_model_score(
        self, config: ModelConfig, category: QueryCategory, estimated_tokens: int
    ) -> float:
        """Calculate a score for a model based on various factors."""
        score = 0.0

        # Free model bonus (significant priority for zero-cost models)
        if config.cost_per_1k_tokens == 0.0:
            score += 0.5  # Major bonus for free models

        # Provider preference (prioritize free providers)
        if config.provider in [LLMProvider.OLLAMA, LLMProvider.HUGGINGFACE]:
            score += 0.3  # Bonus for free providers
        elif config.provider in [LLMProvider.OPENAI, LLMProvider.ANTHROPIC]:
            score += 0.1  # Standard reliability bonus

        # Base score for capability match
        if category == QueryCategory.CODE and "code" in config.capabilities:
            score += 0.3
        elif category == QueryCategory.ANALYTICAL and "analysis" in config.capabilities:
            score += 0.3
        elif "general" in config.capabilities:
            score += 0.2

        # Cost efficiency score (lower cost = higher score)
        max_cost = self.selection_thresholds["complexity_thresholds"]["complex"][
            "max_cost_per_query"
        ]
        if config.cost_per_1k_tokens > 0:
            cost_efficiency = (
                1.0 - (config.cost_per_1k_tokens * estimated_tokens / 1000) / max_cost
            )
            score += cost_efficiency * 0.2
        else:
            score += 0.2  # Full score for free models

        # Token capacity score
        if estimated_tokens <= config.max_tokens:
            score += 0.2
        else:
            score -= 0.3  # Penalty for insufficient capacity

        # Capability bonuses
        if "fast" in config.capabilities:
            score += 0.1
        if "cost-effective" in config.capabilities:
            score += 0.1
        if "very-cost-effective" in config.capabilities:
            score += 0.15

        return max(0.0, min(1.0, score))

    def _get_fallback_models(
        self, model_config: ModelConfig, tier: ModelTier
    ) -> List[str]:
        """Get fallback models for a given model configuration."""
        fallbacks = []

        # Add explicit fallbacks from config
        fallbacks.extend(model_config.fallback_models)

        # Add tier-based fallbacks
        if tier == ModelTier.POWERFUL:
            # Powerful models can fallback to balanced
            fallbacks.extend(
                [
                    model_name
                    for model_name, config in self.model_configs.items()
                    if config.tier == ModelTier.BALANCED and config.enabled
                ]
            )

        # Add fast models as ultimate fallback
        fallbacks.extend(
            [
                model_name
                for model_name, config in self.model_configs.items()
                if config.tier == ModelTier.FAST and config.enabled
            ]
        )

        # Remove duplicates and the current model
        fallbacks = list(set(fallbacks))
        if model_config.model in fallbacks:
            fallbacks.remove(model_config.model)

        return fallbacks[:3]  # Limit to top 3 fallbacks

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Rough estimation: 1 token ≈ 4 characters for English text
        return len(text) // 4

    def _calculate_estimated_cost(
        self, config: ModelConfig, estimated_tokens: int
    ) -> float:
        """Calculate estimated cost for a request."""
        return (config.cost_per_1k_tokens * estimated_tokens) / 1000

    def _generate_selection_reasoning(
        self,
        classification: QueryClassification,
        estimated_tokens: int,
        tier: ModelTier,
    ) -> str:
        """Generate human-readable reasoning for model selection."""
        reasoning_parts = []

        reasoning_parts.append(f"Query category: {classification.category.value}")
        reasoning_parts.append(f"Complexity: {classification.complexity.value}")
        reasoning_parts.append(f"Confidence: {classification.confidence:.2f}")
        reasoning_parts.append(f"Estimated tokens: {estimated_tokens}")
        reasoning_parts.append(f"Selected tier: {tier.value}")

        if classification.complexity == QueryComplexity.SIMPLE:
            reasoning_parts.append("Simple query - using fast, cost-effective model")
        elif classification.complexity == QueryComplexity.COMPLEX:
            reasoning_parts.append(
                "Complex query - using powerful model for better reasoning"
            )

        if classification.category == QueryCategory.CODE:
            reasoning_parts.append(
                "Code-related query - prioritizing models with code capabilities"
            )
        elif classification.category == QueryCategory.ANALYTICAL:
            reasoning_parts.append(
                "Analytical query - using model with strong reasoning capabilities"
            )

        return "; ".join(reasoning_parts)

    def _get_fallback_selection(self) -> ModelSelectionResult:
        """Get a safe fallback model selection."""
        # Default to GPT-3.5-turbo as a safe fallback
        fallback_config = self.model_configs.get("gpt-3.5-turbo")
        if not fallback_config:
            # If GPT-3.5-turbo not available, get any available model
            available_models = [
                (name, config)
                for name, config in self.model_configs.items()
                if config.enabled
            ]
            if available_models:
                fallback_name, fallback_config = available_models[0]
            else:
                raise ValueError("No available models for fallback")

        return ModelSelectionResult(
            selected_model=fallback_config.model,
            selected_provider=fallback_config.provider,
            model_tier=fallback_config.tier,
            confidence=0.5,
            reasoning="Fallback selection due to error in model selection",
            fallback_models=[],
            estimated_cost=0.0,
            selection_time_ms=0.0,
        )

    def _log_model_selection(
        self,
        result: ModelSelectionResult,
        classification: QueryClassification,
        estimated_tokens: int,
    ):
        """Log model selection for monitoring and analytics."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "selected_model": result.selected_model,
            "model_tier": result.model_tier.value,
            "query_category": classification.category.value,
            "query_complexity": classification.complexity.value,
            "confidence": result.confidence,
            "estimated_tokens": estimated_tokens,
            "estimated_cost": result.estimated_cost,
            "selection_time_ms": result.selection_time_ms,
            "reasoning": result.reasoning,
        }

        self.selection_history.append(log_entry)

        # Keep only last 1000 entries
        if len(self.selection_history) > 1000:
            self.selection_history = self.selection_history[-1000:]

        logger.info(
            f"Model selection: {result.selected_model} ({result.model_tier.value}) "
            f"for {classification.category.value} query "
            f"(complexity: {classification.complexity.value}, "
            f"confidence: {result.confidence:.2f}, "
            f"estimated cost: ${result.estimated_cost:.4f})"
        )

    def get_selection_metrics(self) -> Dict[str, Any]:
        """Get metrics about model selection performance."""
        if not self.selection_history:
            return {}

        # Calculate metrics
        total_selections = len(self.selection_history)
        tier_distribution = {}
        category_distribution = {}
        avg_selection_time = 0.0
        total_cost = 0.0

        for entry in self.selection_history:
            tier = entry["model_tier"]
            category = entry["query_category"]

            tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
            category_distribution[category] = category_distribution.get(category, 0) + 1
            avg_selection_time += entry["selection_time_ms"]
            total_cost += entry["estimated_cost"]

        avg_selection_time /= total_selections

        return {
            "total_selections": total_selections,
            "tier_distribution": tier_distribution,
            "category_distribution": category_distribution,
            "avg_selection_time_ms": avg_selection_time,
            "total_estimated_cost": total_cost,
            "avg_confidence": sum(
                entry["confidence"] for entry in self.selection_history
            )
            / total_selections,
        }


# Global instance for easy access
_model_selector = None


def get_model_selector() -> DynamicModelSelector:
    """Get the global model selector instance."""
    global _model_selector
    if _model_selector is None:
        _model_selector = DynamicModelSelector()
    return _model_selector
