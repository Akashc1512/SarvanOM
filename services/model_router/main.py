"""
Model Router Service - SarvanOM v2

Routes queries to appropriate models based on intent, capabilities, and performance requirements.
Implements automatic model selection with fallback chains and cost optimization.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Import centralized configuration
from shared.core.config.central_config import get_central_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get configuration
config = get_central_config()

# Prometheus metrics
router_requests_total = Counter('sarvanom_router_requests_total', 'Total router requests', ['query_type', 'complexity'])
router_selection_time = Histogram('sarvanom_router_selection_time_seconds', 'Router selection time', ['query_type'])
router_fallback_count = Counter('sarvanom_router_fallback_total', 'Router fallback count', ['from_model', 'to_model'])
router_model_usage = Counter('sarvanom_router_model_usage_total', 'Router model usage', ['model_id', 'query_type', 'complexity'])

# PR-4: New router metrics with provider tags
router_metrics = {
    'model_family': Counter('sarvanom_router_model_family_total', 'Router model family usage', ['model_family', 'task', 'fallback']),
    'task_latency': Histogram('sarvanom_router_task_latency_ms', 'Router task latency', ['task', 'model_family']),
    'refinement_usage': Counter('sarvanom_router_refinement_total', 'Router refinement usage', ['refinement_type', 'budget_exceeded']),
    'provider_availability': Gauge('sarvanom_router_provider_available', 'Router provider availability', ['provider'])
}

class QueryType(str, Enum):
    SIMPLE = "simple"
    TECHNICAL = "technical"
    RESEARCH = "research"
    MULTIMEDIA = "multimedia"

class QueryComplexity(str, Enum):
    SIMPLE = "simple"  # 5s budget
    TECHNICAL = "technical"  # 7s budget
    RESEARCH = "research"  # 10s budget
    MULTIMEDIA = "multimedia"  # 10s budget

@dataclass
class QueryContext:
    query: str
    query_type: QueryType
    complexity: QueryComplexity
    has_images: bool = False
    has_documents: bool = False
    has_video: bool = False
    user_preferences: Dict[str, Any] = None
    budget_remaining: float = 0.0

    def __post_init__(self):
        if self.user_preferences is None:
            self.user_preferences = {}

@dataclass
class ModelSelection:
    model_id: str
    provider: str
    confidence: float
    fallback_models: List[str]
    estimated_cost: float
    estimated_latency: float
    error: Optional[str] = None
    ui_hint: Optional[str] = None

class QueryClassifier:
    """Classifies queries into appropriate types and complexity levels"""
    
    def __init__(self):
        self.multimodal_keywords = [
            "image", "picture", "photo", "diagram", "chart", "graph",
            "document", "pdf", "text", "analyze this", "what's in this",
            "describe", "explain this image", "extract text from",
            "screenshot", "video", "youtube", "upload"
        ]
        
        self.technical_keywords = [
            "code", "programming", "algorithm", "function", "class",
            "debug", "error", "exception", "api", "database", "sql",
            "javascript", "python", "react", "node", "docker", "kubernetes",
            "implementation", "architecture", "design pattern"
        ]
        
        self.research_keywords = [
            "analyze", "compare", "research", "study", "investigate",
            "comprehensive", "detailed", "in-depth", "thorough",
            "multiple sources", "evidence", "citations", "references",
            "literature review", "meta-analysis", "systematic review"
        ]
    
    def classify_query(self, query: str, context: Dict[str, Any] = None) -> Tuple[QueryType, QueryComplexity]:
        """Classify query into type and complexity"""
        query_lower = query.lower()
        
        # Check for multimodal content first
        if self._has_multimodal_content(query_lower, context):
            return QueryType.MULTIMEDIA, QueryComplexity.MULTIMEDIA
        
        # Check for technical content
        if self._has_technical_content(query_lower):
            return QueryType.TECHNICAL, QueryComplexity.TECHNICAL
        
        # Check for research content
        if self._has_research_content(query_lower):
            return QueryType.RESEARCH, QueryComplexity.RESEARCH
        
        # Default to simple
        return QueryType.SIMPLE, QueryComplexity.SIMPLE
    
    def _has_multimodal_content(self, query: str, context: Dict[str, Any] = None) -> bool:
        """Check if query requires multimodal capabilities"""
        # Check for file uploads in context
        if context and context.get("files"):
            return True
        
        # Check for multimodal keywords
        return any(keyword in query for keyword in self.multimodal_keywords)
    
    def _has_technical_content(self, query: str) -> bool:
        """Check if query is technical"""
        return any(keyword in query for keyword in self.technical_keywords)
    
    def _has_research_content(self, query: str) -> bool:
        """Check if query requires research capabilities"""
        return any(keyword in query for keyword in self.research_keywords)

class ModelRouter:
    """Routes queries to appropriate models with provider limits and fallback chains"""
    
    def __init__(self, config, registry_url: str = "http://localhost:8000"):
        self.registry_url = registry_url
        self.config = config
        self.classifier = QueryClassifier()
        self.http_client = httpx.AsyncClient()
        
        # Initialize provider availability
        self.provider_availability = self._check_provider_availability()
        
        # Model selection policies (limited to configured providers only)
        self.model_policies = self._build_model_policies()
        
        # Refinement model selection (for Guided Prompt)
        self.refinement_policies = self._build_refinement_policies()
    
    def _check_provider_availability(self) -> Dict[str, bool]:
        """Check which providers are available based on API keys"""
        availability = {
            "openai": bool(self.config.openai_api_key),
            "anthropic": bool(self.config.anthropic_api_key),
            "gemini": bool(getattr(self.config, 'google_api_key', None)),
            "huggingface": bool(self.config.huggingface_api_key or self.config.huggingface_read_token or self.config.huggingface_write_token)
        }
        
        # Log provider status
        for provider, available in availability.items():
            if available:
                logger.info(f"Provider '{provider}' is configured and available")
            else:
                logger.warning(f"Provider '{provider}' is not configured - will be marked as inactive")
        
        return availability
    
    def _build_model_policies(self) -> Dict[QueryType, Dict[str, Any]]:
        """Build model policies based on available providers"""
        policies = {}
        
        # Text LLMs: prefer OpenAI/Anthropic
        if self.provider_availability["openai"] and self.provider_availability["anthropic"]:
            # Both available - use both
            text_primary = ["gpt-4o-2024-08-06", "claude-3-5-sonnet-20241022"]
            text_fallback = ["gpt-4o-mini-2024-07-18", "claude-3-5-haiku-20241022"]
        elif self.provider_availability["openai"]:
            # Only OpenAI available
            text_primary = ["gpt-4o-2024-08-06", "gpt-4o-mini-2024-07-18"]
            text_fallback = ["gpt-3.5-turbo-0125"]
        elif self.provider_availability["anthropic"]:
            # Only Anthropic available
            text_primary = ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"]
            text_fallback = []
        else:
            # No text LLMs configured - this should fail gracefully
            text_primary = []
            text_fallback = []
            logger.error("No text LLM providers configured - text generation will be disabled")
        
        # Vision/LMM: prefer Gemini, fallback to OpenAI vision
        if self.provider_availability["gemini"]:
            vision_primary = ["gemini-1.5-pro"]
            vision_fallback = ["gpt-4o-2024-08-06"] if self.provider_availability["openai"] else []
        elif self.provider_availability["openai"]:
            vision_primary = ["gpt-4o-2024-08-06"]
            vision_fallback = []
        else:
            vision_primary = []
            vision_fallback = []
            logger.warning("No vision/LMM providers configured - vision features will be disabled")
        
        # Build policies
        policies[QueryType.SIMPLE] = {
            "primary": text_primary[:2] if text_primary else [],
            "fallback": text_fallback[:1] if text_fallback else [],
            "budget": 5.0,  # 5 seconds
            "requires_text_llm": True
        }
        
        policies[QueryType.TECHNICAL] = {
            "primary": text_primary[:2] if text_primary else [],
            "fallback": text_fallback[:1] if text_fallback else [],
            "budget": 7.0,  # 7 seconds
            "requires_text_llm": True
        }
        
        policies[QueryType.RESEARCH] = {
            "primary": text_primary[:2] if text_primary else [],
            "fallback": text_fallback[:1] if text_fallback else [],
            "budget": 10.0,  # 10 seconds
            "requires_text_llm": True
        }
        
        policies[QueryType.MULTIMEDIA] = {
            "primary": vision_primary,
            "fallback": vision_fallback,
            "budget": 10.0,  # 10 seconds
            "requires_vision": True,
            "disable_vision_hint": not vision_primary and not vision_fallback
        }
        
        return policies
    
    def _build_refinement_policies(self) -> Dict[str, Dict[str, Any]]:
        """Build refinement policies based on available providers"""
        policies = {}
        
        # Fast refinement: cheapest fast stable model
        if self.provider_availability["openai"]:
            fast_primary = ["gpt-3.5-turbo-0125"]
            fast_fallback = ["gpt-4o-mini-2024-07-18"]
        elif self.provider_availability["anthropic"]:
            fast_primary = ["claude-3-5-haiku-20241022"]
            fast_fallback = ["claude-3-5-sonnet-20241022"]
        else:
            fast_primary = []
            fast_fallback = []
        
        # Quality refinement: better models within budget
        if self.provider_availability["openai"] and self.provider_availability["anthropic"]:
            quality_primary = ["gpt-4o-mini-2024-07-18", "claude-3-5-haiku-20241022"]
            quality_fallback = ["gpt-3.5-turbo-0125", "claude-3-5-sonnet-20241022"]
        elif self.provider_availability["openai"]:
            quality_primary = ["gpt-4o-mini-2024-07-18"]
            quality_fallback = ["gpt-3.5-turbo-0125"]
        elif self.provider_availability["anthropic"]:
            quality_primary = ["claude-3-5-haiku-20241022"]
            quality_fallback = ["claude-3-5-sonnet-20241022"]
        else:
            quality_primary = []
            quality_fallback = []
        
        # LMM refinement: vision models
        if self.provider_availability["gemini"]:
            lmm_primary = ["gemini-1.5-pro"]
            lmm_fallback = ["gpt-4o-2024-08-06"] if self.provider_availability["openai"] else []
        elif self.provider_availability["openai"]:
            lmm_primary = ["gpt-4o-2024-08-06"]
            lmm_fallback = []
        else:
            lmm_primary = []
            lmm_fallback = []
        
        policies["fast"] = {
            "primary": fast_primary,
            "fallback": fast_fallback,
            "budget": 0.5,  # 500ms
            "p95_budget": 0.8  # 800ms
        }
        
        policies["quality"] = {
            "primary": quality_primary,
            "fallback": quality_fallback,
            "budget": 0.5,  # 500ms
            "p95_budget": 0.8  # 800ms
        }
        
        policies["lmm"] = {
            "primary": lmm_primary,
            "fallback": lmm_fallback,
            "budget": 0.5,  # 500ms
            "p95_budget": 0.8  # 800ms
        }
        
        return policies
    
    def _emit_router_metrics(self, task: str, model_family: str, latency_ms: float, fallback_used: bool = False):
        """Emit router metrics as specified in PR-4"""
        try:
            # Emit model family usage
            router_metrics['model_family'].labels(
                model_family=model_family,
                task=task,
                fallback=str(fallback_used).lower()
            ).inc()
            
            # Emit task latency
            router_metrics['task_latency'].labels(
                task=task,
                model_family=model_family
            ).observe(latency_ms)
            
        except Exception as e:
            logger.warning(f"Failed to emit router metrics: {e}")
    
    def _emit_provider_availability_metrics(self):
        """Emit provider availability metrics"""
        try:
            for provider, available in self.provider_availability.items():
                router_metrics['provider_availability'].labels(provider=provider).set(1 if available else 0)
        except Exception as e:
            logger.warning(f"Failed to emit provider availability metrics: {e}")
    
    def _emit_refinement_metrics(self, refinement_type: str, budget_exceeded: bool = False):
        """Emit refinement usage metrics"""
        try:
            router_metrics['refinement_usage'].labels(
                refinement_type=refinement_type,
                budget_exceeded=str(budget_exceeded).lower()
            ).inc()
        except Exception as e:
            logger.warning(f"Failed to emit refinement metrics: {e}")
    
    async def select_refinement_model(self, query: str, attachments: List[str] = None, budget_ms: float = 500) -> ModelSelection:
        """Select model for Guided Prompt refinement with budget constraints"""
        start_time = time.time()
        
        # Check for multimodal content
        has_multimodal = self._has_multimodal_content(query, attachments)
        
        # Select appropriate refinement policy
        if has_multimodal:
            policy = self.refinement_policies["lmm"]
            refinement_type = "lmm"
        else:
            # Try fast first, fallback to quality
            if budget_ms <= 500:
                policy = self.refinement_policies["fast"]
                refinement_type = "fast"
            else:
                policy = self.refinement_policies["quality"]
                refinement_type = "quality"
        
        # Check if policy has available models
        if not policy.get("primary") and not policy.get("fallback"):
            selection_time = (time.time() - start_time) * 1000
            return ModelSelection(
                model_id="none",
                provider="none",
                confidence=0.0,
                fallback_models=[],
                estimated_cost=0.0,
                estimated_latency=selection_time,
                error=f"No {refinement_type} refinement models available"
            )
        
        # Select best available model
        selected_model = None
        if policy.get("primary"):
            selected_model = policy["primary"][0]
        elif policy.get("fallback"):
            selected_model = policy["fallback"][0]
        
        if not selected_model:
            selection_time = (time.time() - start_time) * 1000
            return ModelSelection(
                model_id="none",
                provider="none",
                confidence=0.0,
                fallback_models=[],
                estimated_cost=0.0,
                estimated_latency=selection_time,
                error="No refinement models available"
            )
        
        # Check budget constraints
        budget_ok = self._check_refinement_budget(selected_model, budget_ms)
        if not budget_ok:
            # Try fallback models
            for fallback_model in policy.get("fallback", []):
                if self._check_refinement_budget(fallback_model, budget_ms):
                    selected_model = fallback_model
                    break
            else:
                # No models meet budget - return with bypass hint
                selection_time = (time.time() - start_time) * 1000
                return ModelSelection(
                    model_id=selected_model,
                    provider=self._get_provider_from_model(selected_model),
                    confidence=0.5,
                    fallback_models=policy.get("fallback", []),
                    estimated_cost=0.01,
                    estimated_latency=selection_time,
                    ui_hint="Refinement budget exceeded - auto-bypass recommended"
                )
        
        selection_time = (time.time() - start_time) * 1000
        
        # Emit refinement metrics
        self._emit_refinement_metrics(refinement_type, budget_exceeded=False)
        self._emit_router_metrics("refine", self._get_provider_from_model(selected_model), selection_time)
        
        return ModelSelection(
            model_id=selected_model,
            provider=self._get_provider_from_model(selected_model),
            confidence=0.9,
            fallback_models=policy.get("fallback", []),
            estimated_cost=0.01,
            estimated_latency=selection_time
        )
    
    def _has_multimodal_content(self, query: str, attachments: List[str] = None) -> bool:
        """Check if query has multimodal content"""
        if attachments:
            for attachment in attachments:
                if self._is_visual_file(attachment):
                    return True
        
        multimodal_keywords = [
            'image', 'picture', 'photo', 'diagram', 'chart', 'graph',
            'document', 'pdf', 'analyze this', 'what\'s in this'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in multimodal_keywords)
    
    def _is_visual_file(self, filename: str) -> bool:
        """Check if file is visual"""
        visual_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.pdf']
        return any(filename.lower().endswith(ext) for ext in visual_extensions)
    
    def _check_refinement_budget(self, model_id: str, budget_ms: float) -> bool:
        """Check if model can meet refinement budget constraints"""
        # Simple budget check based on model type
        if "gpt-3.5-turbo" in model_id:
            return budget_ms >= 500  # Fast model
        elif "gpt-4o-mini" in model_id or "claude-3-5-haiku" in model_id:
            return budget_ms >= 800  # Medium model
        elif "gpt-4o" in model_id or "claude-3-5-sonnet" in model_id or "gemini" in model_id:
            return budget_ms >= 1000  # Slower model
        else:
            return budget_ms >= 500  # Default
    
    def _get_provider_from_model(self, model_id: str) -> str:
        """Get provider name from model ID"""
        if "gpt" in model_id:
            return "openai"
        elif "claude" in model_id:
            return "anthropic"
        elif "gemini" in model_id:
            return "gemini"
        else:
            return "unknown"
    
    async def route_query(self, query: str, context: Dict[str, Any] = None) -> ModelSelection:
        """Route query to appropriate model with provider limits and graceful degradation"""
        start_time = time.time()
        
        # Classify query
        query_type, complexity = self.classifier.classify_query(query, context)
        
        # Create query context
        query_context = QueryContext(
            query=query,
            query_type=query_type,
            complexity=complexity,
            has_images=context.get("has_images", False) if context else False,
            has_documents=context.get("has_documents", False) if context else False,
            has_video=context.get("has_video", False) if context else False,
            user_preferences=context.get("user_preferences", {}) if context else {},
            budget_remaining=context.get("budget_remaining", 0.0) if context else 0.0
        )
        
        # Check if query type is supported with current provider configuration
        policy = self.model_policies.get(query_type, {})
        
        # Handle text LLM requirements
        if policy.get("requires_text_llm", False):
            if not policy.get("primary") and not policy.get("fallback"):
                # No text LLMs configured - return graceful error
                selection_time = (time.time() - start_time) * 1000
                return ModelSelection(
                    model_id="none",
                    provider="none",
                    confidence=0.0,
                    fallback_models=[],
                    estimated_cost=0.0,
                    estimated_latency=0.0,
                    error="No text LLM providers configured. Please configure OpenAI or Anthropic API keys."
                )
        
        # Handle vision requirements
        if policy.get("requires_vision", False):
            if policy.get("disable_vision_hint", False):
                # No vision providers configured - return graceful error with UI hint
                selection_time = (time.time() - start_time) * 1000
                return ModelSelection(
                    model_id="none",
                    provider="none",
                    confidence=0.0,
                    fallback_models=[],
                    estimated_cost=0.0,
                    estimated_latency=0.0,
                    error="Vision features are disabled. Please configure Gemini or OpenAI API keys for vision capabilities.",
                    ui_hint="Vision features unavailable - configure API keys to enable"
        )
        
        # Select model
        model_selection = await self._select_model(query_context)
        
        # Emit router metrics
        selection_time = (time.time() - start_time) * 1000
        task_type = "text" if query_type != QueryType.MULTIMEDIA else "vision"
        model_family = self._get_provider_from_model(model_selection.model_id)
        fallback_used = model_selection.model_id != policy.get("primary", [None])[0] if policy.get("primary") else False
        
        self._emit_router_metrics(task_type, model_family, selection_time, fallback_used)
        
        # Record metrics
        selection_time = time.time() - start_time
        router_requests_total.labels(
            query_type=query_type.value,
            complexity=complexity.value
        ).inc()
        
        router_selection_time.labels(
            query_type=query_type.value
        ).observe(selection_time)
        
        router_model_usage.labels(
            model_id=model_selection.model_id,
            query_type=query_type.value,
            complexity=complexity.value
        ).inc()
        
        return model_selection
    
    async def route_refinement_query(self, query: str, refinement_type: str = "fast") -> ModelSelection:
        """Route refinement query for Guided Prompt Confirmation"""
        start_time = time.time()
        
        # Get refinement policy
        policy = self.refinement_policies.get(refinement_type, self.refinement_policies["fast"])
        
        # Select refinement model
        model_selection = await self._select_refinement_model(policy, query)
        
        # Record metrics
        selection_time = time.time() - start_time
        router_requests_total.labels(
            query_type="refinement",
            complexity=refinement_type
        ).inc()
        
        router_selection_time.labels(
            query_type="refinement"
        ).observe(selection_time)
        
        return model_selection
    
    async def _select_model(self, context: QueryContext) -> ModelSelection:
        """Select appropriate model for query"""
        policy = self.model_policies[context.query_type]
        
        # Get available models from registry
        available_models = await self._get_available_models()
        
        # Select primary model
        primary_model = None
        for model_id in policy["primary"]:
            if model_id in available_models:
                primary_model = available_models[model_id]
                break
        
        if not primary_model:
            # Fallback to any available model
            for model_id in policy["fallback"]:
                if model_id in available_models:
                    primary_model = available_models[model_id]
                    break
        
        if not primary_model:
            raise HTTPException(status_code=503, detail="No suitable models available")
        
        # Calculate estimated cost and latency
        estimated_cost = self._calculate_estimated_cost(primary_model, context.query)
        estimated_latency = self._calculate_estimated_latency(primary_model, context.query)
        
        return ModelSelection(
            model_id=primary_model["model_id"],
            provider=primary_model["provider"],
            confidence=0.9,  # High confidence for primary selection
            fallback_models=policy["fallback"],
            estimated_cost=estimated_cost,
            estimated_latency=estimated_latency
        )
    
    async def _select_refinement_model(self, policy: Dict[str, Any], query: str) -> ModelSelection:
        """Select model for refinement queries"""
        # Get available refinement models
        available_models = await self._get_refinement_models()
        
        # Select primary refinement model
        primary_model = None
        for model_id in policy["primary"]:
            if model_id in available_models:
                primary_model = available_models[model_id]
                break
        
        if not primary_model:
            # Fallback to any available refinement model
            for model_id in policy["fallback"]:
                if model_id in available_models:
                    primary_model = available_models[model_id]
                    break
        
        if not primary_model:
            raise HTTPException(status_code=503, detail="No suitable refinement models available")
        
        # Calculate estimated cost and latency for refinement
        estimated_cost = self._calculate_estimated_cost(primary_model, query) * 0.1  # Refinement is cheaper
        estimated_latency = min(primary_model["performance"]["avg_completion_ms"] / 1000, policy["budget"])
        
        return ModelSelection(
            model_id=primary_model["model_id"],
            provider=primary_model["provider"],
            confidence=0.95,  # Very high confidence for refinement
            fallback_models=policy["fallback"],
            estimated_cost=estimated_cost,
            estimated_latency=estimated_latency
        )
    
    async def _get_available_models(self) -> Dict[str, Any]:
        """Get available models from registry"""
        try:
            response = await self.http_client.get(f"{self.registry_url}/models/stable")
            models = response.json()
            return {model["model_id"]: model for model in models}
        except Exception as e:
            logger.error(f"Failed to get models from registry: {e}")
            return {}
    
    async def _get_refinement_models(self) -> Dict[str, Any]:
        """Get refinement models from registry"""
        try:
            response = await self.http_client.get(f"{self.registry_url}/models/refiners")
            models = response.json()
            return {model["model_id"]: model for model in models}
        except Exception as e:
            logger.error(f"Failed to get refinement models from registry: {e}")
            return {}
    
    def _calculate_estimated_cost(self, model: Dict[str, Any], query: str) -> float:
        """Calculate estimated cost for query"""
        # Rough estimation based on query length
        estimated_tokens = len(query.split()) * 1.3  # Rough token estimation
        
        input_cost = (estimated_tokens / 1000) * model["costs"]["input_tokens_per_1k"]
        output_cost = (estimated_tokens / 1000) * model["costs"]["output_tokens_per_1k"]
        
        return input_cost + output_cost
    
    def _calculate_estimated_latency(self, model: Dict[str, Any], query: str) -> float:
        """Calculate estimated latency for query"""
        # Base latency from model performance
        base_latency = model["performance"]["avg_completion_ms"] / 1000
        
        # Adjust based on query complexity
        query_length = len(query.split())
        if query_length > 100:
            base_latency *= 1.5
        elif query_length > 50:
            base_latency *= 1.2
        
        return base_latency

# Create FastAPI app
app = FastAPI(
    title="Model Router Service",
    version="2.0.0",
    description="Routes queries to appropriate models based on intent, capabilities, and performance requirements"
)

# Set CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins if isinstance(config.cors_origins, list) else (config.cors_origins.split(",") if config.cors_origins else ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# App state / DI container
async def init_dependencies():
    """Initialize shared clients and dependencies"""
    logger.info("Initializing Model Router dependencies...")
    
    # Initialize HTTP client
    app.state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
    )
    
    # Initialize Model Router
    app.state.model_router = ModelRouter(config)
    logger.info("Model Router initialized successfully")

async def cleanup_dependencies():
    """Cleanup shared clients and dependencies"""
    logger.info("Cleaning up Model Router dependencies...")
    
    if hasattr(app.state, 'http_client'):
        try:
            await app.state.http_client.aclose()
            logger.info("HTTP client closed successfully")
        except Exception as e:
            logger.error(f"Error closing HTTP client: {e}")

# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    await init_dependencies()

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    await cleanup_dependencies()

# Pydantic models for API
class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

class RefinementRequest(BaseModel):
    query: str
    refinement_type: str = "fast"

class ModelSelectionResponse(BaseModel):
    model_id: str
    provider: str
    confidence: float
    fallback_models: List[str]
    estimated_cost: float
    estimated_latency: float

# Health & Config endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint - fast, no downstream calls"""
    return {"status": "healthy", "service": "model-router", "timestamp": datetime.now().isoformat()}

@app.get("/ready")
async def ready_check():
    """Ready check endpoint - light ping to critical deps with small timeout"""
    try:
        # Check HTTP client and model router availability
        if not hasattr(app.state, 'model_router') or not hasattr(app.state, 'http_client'):
            raise HTTPException(status_code=503, detail="Dependencies not initialized")
        
        # Test HTTP client with a quick request
        await asyncio.wait_for(
            app.state.http_client.get("http://httpbin.org/status/200"),
            timeout=2.0
        )
        return {"status": "ready", "service": "model-router", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Ready check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/config")
async def get_config_endpoint():
    """Config endpoint - sanitized echo of active providers and keyless fallbacks"""
    return {
        "service": "model-router",
        "active_providers": {
            "openai": bool(config.openai_api_key),
            "anthropic": bool(config.anthropic_api_key),
            "gemini": bool(getattr(config, 'google_api_key', None)),
            "huggingface": bool(config.huggingface_api_key or config.huggingface_read_token or config.huggingface_write_token),
            "ollama": bool(config.ollama_base_url)
        },
        "keyless_fallbacks_enabled": getattr(config, 'keyless_fallbacks_enabled', True),
        "environment": getattr(config, 'environment', 'development'),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/version")
async def get_version():
    """Version endpoint"""
    return {
        "service": "model-router",
        "version": "2.0.0",
        "build_date": datetime.now().isoformat(),
        "environment": config.environment.value
    }

# API endpoints
@app.post("/route", response_model=ModelSelectionResponse)
async def route_query(request: QueryRequest):
    """Route query to appropriate model"""
    try:
        selection = await app.state.model_router.route_query(request.query, request.context)
        return ModelSelectionResponse(**selection.__dict__)
    except Exception as e:
        logger.error(f"Failed to route query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/route/refinement", response_model=ModelSelectionResponse)
async def route_refinement_query(request: RefinementRequest):
    """Route refinement query for Guided Prompt Confirmation"""
    try:
        selection = await app.state.model_router.route_refinement_query(request.query, request.refinement_type)
        return ModelSelectionResponse(**selection.__dict__)
    except Exception as e:
        logger.error(f"Failed to route refinement query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/classify")
async def classify_query(query: str, context: Optional[Dict[str, Any]] = None):
    """Classify query type and complexity"""
    query_type, complexity = app.state.model_router.classifier.classify_query(query, context)
    return {
        "query_type": query_type.value,
        "complexity": complexity.value,
        "budget_seconds": {
            "simple": 5.0,
            "technical": 7.0,
            "research": 10.0,
            "multimedia": 10.0
        }[complexity.value]
    }

# Observability middleware
if config.metrics_enabled:
    # Mount Prometheus metrics
    from prometheus_client import make_asgi_app
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    logger.info("Prometheus metrics enabled")

if getattr(config, 'tracing_enabled', False) and getattr(config, 'jaeger_agent_host', None):
    # Mount tracing middleware
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.jaeger.thrift import JaegerExporter
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        
        # Configure Jaeger tracing
        trace.set_tracer_provider(TracerProvider())
        jaeger_exporter = JaegerExporter(
            agent_host_name=config.jaeger_agent_host,
            agent_port=int(config.jaeger_agent_port) if config.jaeger_agent_port else 6831,
        )
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(app)
        logger.info("Jaeger tracing enabled")
    except ImportError:
        logger.warning("OpenTelemetry packages not available, tracing disabled")
    except Exception as e:
        logger.error(f"Failed to enable tracing: {e}")

if __name__ == "__main__":
    # Start Prometheus metrics server if enabled
    if config.metrics_enabled:
        start_http_server(8002)
        logger.info("Prometheus metrics server started on port 8002")
    
    # Start FastAPI server
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,
        log_level=config.log_level.value.lower()
    )
