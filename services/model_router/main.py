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
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import httpx
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
router_requests_total = Counter('sarvanom_router_requests_total', 'Total router requests', ['query_type', 'complexity'])
router_selection_time = Histogram('sarvanom_router_selection_time_seconds', 'Router selection time', ['query_type'])
router_fallback_count = Counter('sarvanom_router_fallback_total', 'Router fallback count', ['from_model', 'to_model'])
router_model_usage = Counter('sarvanom_router_model_usage_total', 'Router model usage', ['model_id', 'query_type', 'complexity'])

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
    """Routes queries to appropriate models with fallback chains"""
    
    def __init__(self, registry_url: str = "http://localhost:8000"):
        self.registry_url = registry_url
        self.classifier = QueryClassifier()
        self.http_client = httpx.AsyncClient()
        
        # Model selection policies
        self.model_policies = {
            QueryType.SIMPLE: {
                "primary": ["gpt-3.5-turbo-0125", "claude-3-5-sonnet-20241022"],
                "fallback": ["gpt-4o-2024-08-06"],
                "budget": 5.0  # 5 seconds
            },
            QueryType.TECHNICAL: {
                "primary": ["claude-3-5-sonnet-20241022", "gpt-4o-2024-08-06"],
                "fallback": ["gpt-3.5-turbo-0125"],
                "budget": 7.0  # 7 seconds
            },
            QueryType.RESEARCH: {
                "primary": ["gpt-4o-2024-08-06", "claude-3-5-sonnet-20241022"],
                "fallback": ["gpt-3.5-turbo-0125"],
                "budget": 10.0  # 10 seconds
            },
            QueryType.MULTIMEDIA: {
                "primary": ["gpt-4o-2024-08-06"],  # Only multimodal model
                "fallback": ["claude-3-5-sonnet-20241022"],
                "budget": 10.0  # 10 seconds
            }
        }
        
        # Refinement model selection (for Guided Prompt)
        self.refinement_policies = {
            "fast": {
                "primary": ["gpt-3.5-turbo-0125"],
                "fallback": ["claude-3-5-sonnet-20241022"],
                "budget": 0.5  # 500ms
            },
            "quality": {
                "primary": ["claude-3-5-sonnet-20241022"],
                "fallback": ["gpt-4o-2024-08-06"],
                "budget": 0.8  # 800ms
            }
        }
    
    async def route_query(self, query: str, context: Dict[str, Any] = None) -> ModelSelection:
        """Route query to appropriate model"""
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
        
        # Select model
        model_selection = await self._select_model(query_context)
        
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

# FastAPI app
app = FastAPI(title="Model Router Service", version="2.0.0")

# Model router instance
model_router = ModelRouter()

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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "model-router"}

@app.post("/route", response_model=ModelSelectionResponse)
async def route_query(request: QueryRequest):
    """Route query to appropriate model"""
    try:
        selection = await model_router.route_query(request.query, request.context)
        return ModelSelectionResponse(**selection.__dict__)
    except Exception as e:
        logger.error(f"Failed to route query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/route/refinement", response_model=ModelSelectionResponse)
async def route_refinement_query(request: RefinementRequest):
    """Route refinement query for Guided Prompt Confirmation"""
    try:
        selection = await model_router.route_refinement_query(request.query, request.refinement_type)
        return ModelSelectionResponse(**selection.__dict__)
    except Exception as e:
        logger.error(f"Failed to route refinement query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/classify")
async def classify_query(query: str, context: Optional[Dict[str, Any]] = None):
    """Classify query type and complexity"""
    query_type, complexity = model_router.classifier.classify_query(query, context)
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

if __name__ == "__main__":
    # Start Prometheus metrics server
    start_http_server(8002)
    
    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8001)
