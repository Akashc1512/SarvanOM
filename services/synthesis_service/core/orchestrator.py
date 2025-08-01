"""
Multi-Agent AI Orchestration - Universal Knowledge Platform
Advanced orchestration with multi-model routing, fallback, and circuit breaking.
"""
import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse

import aiohttp
import redis
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)


class ModelType(str, Enum):
    """Available model types for routing."""
    GPT_4 = "gpt-4"
    GPT_3_5 = "gpt-3.5-turbo"
    CLAUDE_3 = "claude-3"
    CLAUDE_2 = "claude-2"
    GEMINI = "gemini-pro"
    MISTRAL = "mistral"
    FALLBACK = "fallback"


class RoutingStrategy(str, Enum):
    """Routing strategies for model selection."""
    ROUND_ROBIN = "round_robin"
    LOAD_BALANCED = "load_balanced"
    COST_OPTIMIZED = "cost_optimized"
    QUALITY_OPTIMIZED = "quality_optimized"
    ADAPTIVE = "adaptive"
    FALLBACK = "fallback"


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class OrchestrationResult:
    """Result from orchestration process."""
    model_used: ModelType
    response: str
    confidence_score: float
    processing_time_ms: float
    tokens_used: int
    cost_estimate: float
    fallback_used: bool = False
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class CircuitBreaker:
    """Circuit breaker pattern for model reliability."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        logger.info("CircuitBreaker initialized")
    
    def record_success(self):
        """Record successful operation."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        logger.debug("Circuit breaker: success recorded")
    
    def record_failure(self):
        """Record failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def can_execute(self) -> bool:
        """Check if operation can be executed."""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker: attempting half-open")
                return True
            return False
        
        # HALF_OPEN state
        return True
    
    def get_state(self) -> CircuitState:
        """Get current circuit breaker state."""
        return self.state


class ModelRouter:
    """Routes requests to appropriate models based on strategy."""
    
    def __init__(self):
        self.models = {
            ModelType.GPT_4: {"cost": 0.03, "quality": 0.95, "speed": 0.8},
            ModelType.GPT_3_5: {"cost": 0.002, "quality": 0.85, "speed": 0.9},
            ModelType.CLAUDE_3: {"cost": 0.015, "quality": 0.92, "speed": 0.85},
            ModelType.CLAUDE_2: {"cost": 0.008, "quality": 0.88, "speed": 0.88},
            ModelType.GEMINI: {"cost": 0.001, "quality": 0.87, "speed": 0.92},
            ModelType.MISTRAL: {"cost": 0.0005, "quality": 0.83, "speed": 0.95},
            ModelType.FALLBACK: {"cost": 0.001, "quality": 0.75, "speed": 0.98}
        }
        self.circuit_breakers = {model: CircuitBreaker() for model in self.models}
        logger.info("ModelRouter initialized")
    
    async def select_model(self, strategy: RoutingStrategy, context: Dict[str, Any]) -> ModelType:
        """Select model based on routing strategy."""
        available_models = [
            model for model in self.models.keys()
            if self.circuit_breakers[model].can_execute()
        ]
        
        if not available_models:
            logger.warning("No available models, using fallback")
            return ModelType.FALLBACK
        
        if strategy == RoutingStrategy.ROUND_ROBIN:
            return self._round_robin_select(available_models)
        elif strategy == RoutingStrategy.LOAD_BALANCED:
            return self._load_balanced_select(available_models)
        elif strategy == RoutingStrategy.COST_OPTIMIZED:
            return self._cost_optimized_select(available_models)
        elif strategy == RoutingStrategy.QUALITY_OPTIMIZED:
            return self._quality_optimized_select(available_models)
        elif strategy == RoutingStrategy.ADAPTIVE:
            return self._adaptive_select(available_models, context)
        else:
            return available_models[0]
    
    def _round_robin_select(self, available_models: List[ModelType]) -> ModelType:
        """Round-robin model selection."""
        # Simple round-robin implementation
        return available_models[0]
    
    def _load_balanced_select(self, available_models: List[ModelType]) -> ModelType:
        """Load-balanced model selection."""
        # Select model with best speed/quality ratio
        best_model = max(available_models, key=lambda m: self.models[m]["speed"])
        return best_model
    
    def _cost_optimized_select(self, available_models: List[ModelType]) -> ModelType:
        """Cost-optimized model selection."""
        # Select model with lowest cost
        best_model = min(available_models, key=lambda m: self.models[m]["cost"])
        return best_model
    
    def _quality_optimized_select(self, available_models: List[ModelType]) -> ModelType:
        """Quality-optimized model selection."""
        # Select model with highest quality
        best_model = max(available_models, key=lambda m: self.models[m]["quality"])
        return best_model
    
    def _adaptive_select(self, available_models: List[ModelType], context: Dict[str, Any]) -> ModelType:
        """Adaptive model selection based on context."""
        query_complexity = context.get("complexity", "moderate")
        user_preference = context.get("preference", "balanced")
        
        if query_complexity == "expert" or user_preference == "quality":
            return self._quality_optimized_select(available_models)
        elif user_preference == "cost":
            return self._cost_optimized_select(available_models)
        elif user_preference == "speed":
            return self._load_balanced_select(available_models)
        else:
            # Balanced approach
            return available_models[0]


class FallbackManager:
    """Manages fallback strategies when primary models fail."""
    
    def __init__(self):
        self.fallback_chain = [
            ModelType.GPT_4,
            ModelType.CLAUDE_3,
            ModelType.GPT_3_5,
            ModelType.CLAUDE_2,
            ModelType.GEMINI,
            ModelType.MISTRAL,
            ModelType.FALLBACK
        ]
        logger.info("FallbackManager initialized")
    
    async def get_fallback_model(self, failed_model: ModelType) -> Optional[ModelType]:
        """Get next model in fallback chain."""
        try:
            current_index = self.fallback_chain.index(failed_model)
            next_index = current_index + 1
            if next_index < len(self.fallback_chain):
                return self.fallback_chain[next_index]
        except ValueError:
            pass
        return None
    
    async def should_retry(self, attempt: int, max_attempts: int = 3) -> bool:
        """Determine if retry should be attempted."""
        return attempt < max_attempts


class RetryManager:
    """Manages retry logic with exponential backoff."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        logger.info("RetryManager initialized")
    
    async def execute_with_retry(self, func, *args, **kwargs) -> Any:
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries + 1} attempts failed")
                    raise last_exception
        
        raise last_exception


class MultiAgentOrchestrator:
    """Main orchestrator for multi-agent AI operations."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.model_router = ModelRouter()
        self.fallback_manager = FallbackManager()
        self.retry_manager = RetryManager()
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()
            logger.info("MultiAgentOrchestrator connected to Redis")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
        
        logger.info("MultiAgentOrchestrator initialized")
    
    async def process_request(
        self,
        query: str,
        strategy: RoutingStrategy = RoutingStrategy.ADAPTIVE,
        context: Dict[str, Any] = None
    ) -> OrchestrationResult:
        """Orchestrate query processing with multiple models."""
        start_time = time.time()
        context = context or {}
        
        # Select initial model
        selected_model = await self.model_router.select_model(strategy, context)
        logger.info(f"Selected model: {selected_model}")
        
        # Process with retry and fallback
        result = await self._process_with_fallback(str(query), selected_model, context)
        
        # Calculate metrics
        processing_time = (time.time() - start_time) * 1000
        tokens_used = len(str(query).split()) * 1.5  # Rough estimate
        cost_estimate = self._estimate_cost(selected_model, tokens_used)
        
        return OrchestrationResult(
            model_used=selected_model,
            response=result,
            confidence_score=0.85,  # TODO: Implement confidence scoring
            processing_time_ms=processing_time,
            tokens_used=int(tokens_used),
            cost_estimate=cost_estimate,
            fallback_used=False,  # Simplified for now
            metadata={
                "strategy": strategy.value if hasattr(strategy, 'value') else str(strategy),
                "context": context
            }
        )
    
    async def _process_with_fallback(
        self,
        query: str,
        initial_model: ModelType,
        context: Dict[str, Any]
    ) -> str:
        """Process query with fallback chain."""
        current_model = initial_model
        attempt = 0
        
        while current_model and attempt < 3:
            try:
                # Simulate model processing
                response = await self._call_model(current_model, query, context)
                
                # Record success
                self.model_router.circuit_breakers[current_model].record_success()
                
                return response
                
            except Exception as e:
                logger.warning(f"Model {current_model} failed: {e}")
                
                # Record failure
                self.model_router.circuit_breakers[current_model].record_failure()
                
                # Get fallback model
                current_model = await self.fallback_manager.get_fallback_model(current_model)
                attempt += 1
        
        # All models failed, return fallback response
        return f"Fallback response for: {query}"
    
    async def _call_model(self, model: ModelType, query: str, context: Dict[str, Any]) -> str:
        """Call specific model (simulated)."""
        # Simulate API call delay
        await asyncio.sleep(0.1)
        
        # Simulate occasional failures
        if model == ModelType.GPT_4 and "error" in query.lower():
            raise Exception("Simulated GPT-4 error")
        
        return f"Response from {model.value}: {query}"
    
    def _estimate_cost(self, model: ModelType, tokens: int) -> float:
        """Estimate cost for model usage."""
        base_cost = self.model_router.models[model]["cost"]
        return base_cost * (tokens / 1000)  # Cost per 1K tokens
    
    async def get_orchestration_stats(self) -> Dict[str, Any]:
        """Get orchestration statistics."""
        stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "average_response_time": 0.0,
            "model_usage": {},
            "circuit_breaker_states": {}
        }
        
        # Get circuit breaker states
        for model, cb in self.model_router.circuit_breakers.items():
            stats["circuit_breaker_states"][model.value] = cb.get_state().value
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of orchestration system."""
        health_status = {
            "status": "healthy",
            "available_models": [],
            "circuit_breakers": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Check available models
        for model, cb in self.model_router.circuit_breakers.items():
            if cb.can_execute():
                health_status["available_models"].append(model.value)
            health_status["circuit_breakers"][model.value] = cb.get_state().value
        
        # Determine overall health
        if not health_status["available_models"]:
            health_status["status"] = "unhealthy"
        elif len(health_status["available_models"]) < 3:
            health_status["status"] = "degraded"
        
        return health_status 