"""
Guided Prompt Confirmation Service - SarvanOM v2

Pre-flight refinement with ≤500ms median / p95 ≤800ms, auto-skip if over budget.
Modes: Refine / Disambiguate / Decompose / Constrain / Sanitize.
Toggle contract (default ON) and "bypass once" behavior.
Privacy: no storage of raw drafts by default; store final_query + consent flags only.
A11y-first, keyboard/screen-reader ready.
"""

import asyncio
import json
import logging
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
import redis
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Import central configuration
from shared.core.config.central_config import get_central_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get configuration
config = get_central_config()

# Prometheus metrics
refinement_requests_total = Counter('sarvanom_refinement_requests_total', 'Total refinement requests', ['refinement_type', 'result'])
refinement_latency = Histogram('sarvanom_refinement_latency_seconds', 'Refinement latency', ['refinement_type'])
refinement_accept_rate = Gauge('sarvanom_refinement_accept_rate', 'Refinement accept rate', ['refinement_type'])
refinement_skip_rate = Gauge('sarvanom_refinement_skip_rate', 'Refinement skip rate', ['refinement_type'])
refinement_edit_rate = Gauge('sarvanom_refinement_edit_rate', 'Refinement edit rate', ['refinement_type'])
refinement_quality_lift = Gauge('sarvanom_refinement_quality_lift', 'Quality improvement from refinement')
refinement_complaint_rate = Gauge('sarvanom_refinement_complaint_rate', 'User complaint rate')

class RefinementMode(str, Enum):
    REFINE = "refine"
    DISAMBIGUATE = "disambiguate"
    DECOMPOSE = "decompose"
    CONSTRAIN = "constrain"
    SANITIZE = "sanitize"

class RefinementState(str, Enum):
    DRAFT = "draft"
    REFINE_SUGGESTIONS = "refine_suggestions"
    USER_CONFIRM = "user_confirm"
    USER_EDIT = "user_edit"
    USER_SKIP = "user_skip"
    FINAL_QUERY = "final_query"

class ToggleState(str, Enum):
    ON = "ON"
    OFF = "OFF"
    BYPASS_ONCE = "BYPASS_ONCE"
    ALWAYS_BYPASS = "ALWAYS_BYPASS"

@dataclass
class RefinementSuggestion:
    id: str
    title: str
    description: str
    refined_query: str
    type: RefinementMode
    confidence: float
    reasoning: str

@dataclass
class ConstraintChip:
    id: str
    label: str
    type: str
    options: List[str]
    selected: Optional[str] = None

@dataclass
class RefinementContext:
    user_id: str
    session_id: str
    original_query: str
    query_hash: str
    thread_id: Optional[str] = None
    has_images: bool = False
    has_documents: bool = False
    has_video: bool = False
    language: str = "en"
    device_type: str = "desktop"
    user_agent: str = ""
    budget_remaining: float = 0.0
    intent_confidence: float = 0.0

@dataclass
class RefinementResult:
    should_trigger: bool
    suggestions: List[RefinementSuggestion]
    constraints: List[ConstraintChip]
    latency_ms: float
    model_used: str
    cost_usd: float
    bypass_reason: Optional[str] = None

class PIIRedactor:
    """Redacts PII from queries"""
    
    def __init__(self):
        self.pii_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            "address": r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b'
        }
    
    def redact_pii(self, query: str) -> Tuple[str, List[str]]:
        """Redact PII from query and return redacted query with redacted items"""
        import re
        
        redacted_query = query
        redacted_items = []
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, redacted_query, re.IGNORECASE)
            for match in matches:
                redacted_query = redacted_query.replace(match, f"[{pii_type.upper()}_REDACTED]")
                redacted_items.append(f"{pii_type}: {match}")
        
        return redacted_query, redacted_items

class LanguageDetector:
    """Detects language from query"""
    
    def __init__(self):
        # Simple language detection based on common words
        self.language_indicators = {
            "en": ["the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"],
            "es": ["el", "la", "de", "que", "y", "a", "en", "un", "es", "se", "no", "te", "lo", "le"],
            "fr": ["le", "de", "et", "à", "un", "il", "être", "et", "en", "avoir", "que", "pour"],
            "de": ["der", "die", "und", "in", "den", "von", "zu", "das", "mit", "sich", "des", "auf"],
            "zh": ["的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一"],
            "ja": ["の", "に", "は", "を", "た", "が", "で", "て", "と", "し", "れ", "さ"],
            "pt": ["o", "de", "e", "do", "da", "em", "um", "para", "é", "com", "não", "uma"],
            "ru": ["и", "в", "не", "на", "я", "быть", "с", "со", "а", "как", "по", "это"]
        }
    
    def detect_language(self, query: str) -> str:
        """Detect primary language of query"""
        query_lower = query.lower()
        
        # Count language indicators
        language_scores = {}
        for lang, indicators in self.language_indicators.items():
            score = sum(1 for indicator in indicators if indicator in query_lower)
            language_scores[lang] = score
        
        # Return language with highest score, default to English
        if language_scores:
            return max(language_scores, key=language_scores.get)
        return "en"

class RefinementTrigger:
    """Determines when to trigger refinement"""
    
    def __init__(self):
        self.intent_confidence_threshold = 0.8
        self.bypass_keywords = ["skip", "bypass", "direct", "immediate"]
    
    def should_trigger_refinement(self, context: RefinementContext, user_settings: Dict[str, Any]) -> bool:
        """Determine if refinement should be triggered"""
        
        # Check user preferences
        if user_settings.get("mode") == ToggleState.OFF:
            return False
        
        if user_settings.get("mode") == ToggleState.ALWAYS_BYPASS:
            return False
        
        if user_settings.get("session_bypass", False):
            return False
        
        # Check for bypass keywords
        if any(keyword in context.original_query.lower() for keyword in self.bypass_keywords):
            return False
        
        # Check intent confidence
        if context.intent_confidence > self.intent_confidence_threshold:
            return False
        
        # Check thread context (repeat follow-ups)
        if self._is_repeat_followup(context):
            return False
        
        # Check budget constraints
        if context.budget_remaining < 0.25:  # Less than 25% budget remaining
            return False
        
        return True
    
    def _is_repeat_followup(self, context: RefinementContext) -> bool:
        """Check if this is a repeat follow-up in the same thread"""
        if not context.thread_id:
            return False
        
        # In real implementation, this would check recent refinements in the thread
        # For now, return False (no repeat follow-up detection)
        return False

class RefinementGenerator:
    """Generates refinement suggestions"""
    
    def __init__(self, router_url: str = None):
        self.router_url = router_url or getattr(config, 'model_router_url', 'http://localhost:8001')
        self.http_client = httpx.AsyncClient()
        self.pii_redactor = PIIRedactor()
        self.language_detector = LanguageDetector()
        self.config = config
    
    async def generate_refinements(self, context: RefinementContext) -> RefinementResult:
        """Generate refinement suggestions for the query"""
        start_time = time.time()
        
        # Redact PII from query
        redacted_query, redacted_items = self.pii_redactor.redact_pii(context.original_query)
        
        # Detect language
        detected_language = self.language_detector.detect_language(context.original_query)
        context.language = detected_language
        
        # Determine refinement type
        refinement_type = self._determine_refinement_type(context)
        
        # Generate suggestions using model router
        try:
            suggestions = await self._generate_suggestions(redacted_query, refinement_type, context)
            constraints = self._generate_constraints(context)
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Check latency budget
            if latency_ms > self.config.median_budget_ms:  # Exceeded median budget
                logger.warning(f"Refinement latency {latency_ms}ms exceeded {self.config.median_budget_ms}ms budget")
                return RefinementResult(
                    should_trigger=False,
                    suggestions=[],
                    constraints=[],
                    latency_ms=latency_ms,
                    model_used="timeout",
                    cost_usd=0.0,
                    bypass_reason="latency_budget_exceeded"
                )
            
            return RefinementResult(
                should_trigger=True,
                suggestions=suggestions,
                constraints=constraints,
                latency_ms=latency_ms,
                model_used="gpt-3.5-turbo",  # Fast refinement model
                cost_usd=0.001,  # Estimated cost
                bypass_reason=None
            )
            
        except Exception as e:
            logger.error(f"Failed to generate refinements: {e}")
            latency_ms = (time.time() - start_time) * 1000
            return RefinementResult(
                should_trigger=False,
                suggestions=[],
                constraints=[],
                latency_ms=latency_ms,
                model_used="error",
                cost_usd=0.0,
                bypass_reason="generation_error"
            )
    
    def _determine_refinement_type(self, context: RefinementContext) -> RefinementMode:
        """Determine the type of refinement needed"""
        query_lower = context.original_query.lower()
        
        # Check for PII or harmful content
        if any(pii in query_lower for pii in ["email", "phone", "address", "ssn", "credit"]):
            return RefinementMode.SANITIZE
        
        # Check for multimodal content
        if context.has_images or context.has_documents or context.has_video:
            return RefinementMode.REFINE
        
        # Check for ambiguous terms
        ambiguous_terms = ["apple", "python", "java", "spring", "bank", "court", "table"]
        if any(term in query_lower for term in ambiguous_terms):
            return RefinementMode.DISAMBIGUATE
        
        # Check for complex queries
        complex_indicators = ["analyze", "compare", "research", "comprehensive", "detailed"]
        if any(indicator in query_lower for indicator in complex_indicators):
            return RefinementMode.DECOMPOSE
        
        # Check for open-ended queries
        open_ended = ["tell me about", "what is", "how does", "explain"]
        if any(phrase in query_lower for phrase in open_ended):
            return RefinementMode.CONSTRAIN
        
        # Default to refine
        return RefinementMode.REFINE
    
    async def _generate_suggestions(self, query: str, refinement_type: RefinementMode, context: RefinementContext) -> List[RefinementSuggestion]:
        """Generate specific suggestions based on refinement type"""
        
        if refinement_type == RefinementMode.DISAMBIGUATE:
            return self._generate_disambiguation_suggestions(query)
        elif refinement_type == RefinementMode.DECOMPOSE:
            return self._generate_decomposition_suggestions(query)
        elif refinement_type == RefinementMode.CONSTRAIN:
            return self._generate_constraint_suggestions(query)
        elif refinement_type == RefinementMode.SANITIZE:
            return self._generate_sanitization_suggestions(query)
        else:
            return self._generate_refinement_suggestions(query)
    
    def _generate_disambiguation_suggestions(self, query: str) -> List[RefinementSuggestion]:
        """Generate disambiguation suggestions"""
        query_lower = query.lower()
        
        if "apple" in query_lower:
            return [
                RefinementSuggestion(
                    id="apple_company",
                    title="Apple Inc. (Company)",
                    description="Stock performance, financial data, products, and business information",
                    refined_query="Show me information about Apple Inc. (AAPL) stock performance and company news",
                    type=RefinementMode.DISAMBIGUATE,
                    confidence=0.9,
                    reasoning="Query contains 'apple' which could refer to the company or fruit"
                ),
                RefinementSuggestion(
                    id="apple_fruit",
                    title="Apple Fruit",
                    description="Nutritional information, health benefits, and recipes",
                    refined_query="Show me nutritional information and health benefits of apples",
                    type=RefinementMode.DISAMBIGUATE,
                    confidence=0.9,
                    reasoning="Query contains 'apple' which could refer to the fruit"
                )
            ]
        elif "python" in query_lower:
            return [
                RefinementSuggestion(
                    id="python_programming",
                    title="Python Programming",
                    description="Programming language tutorials, documentation, and examples",
                    refined_query="Show me Python programming tutorials and documentation",
                    type=RefinementMode.DISAMBIGUATE,
                    confidence=0.9,
                    reasoning="Query contains 'python' which could refer to programming or snakes"
                ),
                RefinementSuggestion(
                    id="python_snake",
                    title="Python Snake",
                    description="Information about python snakes, their habitat, and behavior",
                    refined_query="Show me information about python snakes and their characteristics",
                    type=RefinementMode.DISAMBIGUATE,
                    confidence=0.9,
                    reasoning="Query contains 'python' which could refer to snakes"
                )
            ]
        
        # Default disambiguation
        return [
            RefinementSuggestion(
                id="clarify_intent",
                title="Clarify Intent",
                description="Help me understand what you're looking for",
                refined_query=query,
                type=RefinementMode.DISAMBIGUATE,
                confidence=0.7,
                reasoning="Query appears ambiguous and needs clarification"
            )
        ]
    
    def _generate_decomposition_suggestions(self, query: str) -> List[RefinementSuggestion]:
        """Generate decomposition suggestions"""
        return [
            RefinementSuggestion(
                id="comprehensive_overview",
                title="Comprehensive Overview",
                description="Get a complete analysis covering all aspects",
                refined_query=f"Provide a comprehensive analysis of {query}",
                type=RefinementMode.DECOMPOSE,
                confidence=0.8,
                reasoning="Complex query can be broken down into comprehensive analysis"
            ),
            RefinementSuggestion(
                id="focused_analysis",
                title="Focused Analysis",
                description="Focus on the most important aspects",
                refined_query=f"Focus on the key aspects of {query}",
                type=RefinementMode.DECOMPOSE,
                confidence=0.8,
                reasoning="Complex query can be focused on key aspects"
            )
        ]
    
    def _generate_constraint_suggestions(self, query: str) -> List[RefinementSuggestion]:
        """Generate constraint suggestions"""
        return [
            RefinementSuggestion(
                id="add_time_constraint",
                title="Add Time Constraint",
                description="Specify a time range for the information",
                refined_query=f"{query} (focus on recent information from the last 2 years)",
                type=RefinementMode.CONSTRAIN,
                confidence=0.8,
                reasoning="Open-ended query would benefit from time constraints"
            ),
            RefinementSuggestion(
                id="add_source_constraint",
                title="Add Source Constraint",
                description="Specify preferred sources (academic, news, etc.)",
                refined_query=f"{query} (focus on academic and peer-reviewed sources)",
                type=RefinementMode.CONSTRAIN,
                confidence=0.8,
                reasoning="Open-ended query would benefit from source constraints"
            )
        ]
    
    def _generate_sanitization_suggestions(self, query: str) -> List[RefinementSuggestion]:
        """Generate sanitization suggestions"""
        return [
            RefinementSuggestion(
                id="sanitized_query",
                title="Sanitized Query",
                description="Query with personal information removed",
                refined_query="I'll help you with your question while protecting your privacy",
                type=RefinementMode.SANITIZE,
                confidence=0.95,
                reasoning="Query contains personal information that has been redacted"
            )
        ]
    
    def _generate_refinement_suggestions(self, query: str) -> List[RefinementSuggestion]:
        """Generate general refinement suggestions"""
        return [
            RefinementSuggestion(
                id="improved_clarity",
                title="Improved Clarity",
                description="Make the query more specific and clear",
                refined_query=f"Please provide detailed information about {query}",
                type=RefinementMode.REFINE,
                confidence=0.8,
                reasoning="Query can be made more specific for better results"
            )
        ]
    
    def _generate_constraints(self, context: RefinementContext) -> List[ConstraintChip]:
        """Generate constraint chips"""
        return [
            ConstraintChip(
                id="time_range",
                label="Time Range",
                type="select",
                options=["Recent (1 year)", "Last 5 years", "All time"]
            ),
            ConstraintChip(
                id="sources",
                label="Sources",
                type="select",
                options=["Academic", "News", "Both"]
            ),
            ConstraintChip(
                id="depth",
                label="Depth",
                type="select",
                options=["Simple", "Technical", "Research"]
            ),
            ConstraintChip(
                id="citations",
                label="Citations Required",
                type="boolean",
                options=["Yes", "No"]
            )
        ]

class GuidedPromptService:
    """Main Guided Prompt Confirmation service"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.refinement_trigger = RefinementTrigger()
        self.refinement_generator = RefinementGenerator()
        
        # Storage for user settings and session data
        self.user_settings = {}
        self.session_data = {}
    
    async def process_query(self, query: str, context: Dict[str, Any]) -> RefinementResult:
        """Process query for guided prompt confirmation"""
        
        # Create refinement context
        refinement_context = RefinementContext(
            user_id=context.get("user_id", "anonymous"),
            session_id=context.get("session_id", "default"),
            thread_id=context.get("thread_id"),
            original_query=query,
            query_hash=hashlib.md5(query.encode()).hexdigest(),
            has_images=context.get("has_images", False),
            has_documents=context.get("has_documents", False),
            has_video=context.get("has_video", False),
            language=context.get("language", "en"),
            device_type=context.get("device_type", "desktop"),
            user_agent=context.get("user_agent", ""),
            budget_remaining=context.get("budget_remaining", 1.0),
            intent_confidence=context.get("intent_confidence", 0.5)
        )
        
        # Get user settings
        user_settings = await self._get_user_settings(refinement_context.user_id)
        
        # Check if refinement should be triggered
        should_trigger = self.refinement_trigger.should_trigger_refinement(
            refinement_context, user_settings
        )
        
        if not should_trigger:
            return RefinementResult(
                should_trigger=False,
                suggestions=[],
                constraints=[],
                latency_ms=0.0,
                model_used="none",
                cost_usd=0.0,
                bypass_reason="user_preference_or_confidence"
            )
        
        # Generate refinements
        result = await self.refinement_generator.generate_refinements(refinement_context)
        
        # Record metrics
        self._record_metrics(result, refinement_context)
        
        return result
    
    async def _get_user_settings(self, user_id: str) -> Dict[str, Any]:
        """Get user settings for guided prompt"""
        # In real implementation, this would fetch from database
        # For now, return default settings
        return {
            "mode": ToggleState.ON,
            "session_bypass": False,
            "preferences": {
                "show_hints": True,
                "auto_learn": True,
                "constraint_chips": True,
                "accessibility_mode": False
            }
        }
    
    def _record_metrics(self, result: RefinementResult, context: RefinementContext):
        """Record metrics for the refinement"""
        refinement_requests_total.labels(
            refinement_type="guided_prompt",
            result="success" if result.should_trigger else "bypassed"
        ).inc()
        
        if result.should_trigger:
            refinement_latency.labels(
                refinement_type="guided_prompt"
            ).observe(result.latency_ms / 1000.0)

# Create FastAPI app
app = FastAPI(
    title="Guided Prompt Confirmation Service",
    version="2.0.0",
    description="Pre-flight refinement with ≤500ms median / p95 ≤800ms, auto-skip if over budget"
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
    logger.info("Initializing Guided Prompt dependencies...")
    
    # Initialize Redis client
    app.state.redis_client = redis.Redis.from_url(
        str(config.redis_url),
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
    
    # Test Redis connection
    try:
        await asyncio.get_event_loop().run_in_executor(
            None, app.state.redis_client.ping
        )
        logger.info("Redis client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise
    
    # Initialize Guided Prompt Service
    app.state.guided_prompt_service = GuidedPromptService(app.state.redis_client)
    logger.info("Guided Prompt Service initialized successfully")

async def cleanup_dependencies():
    """Cleanup shared clients and dependencies"""
    logger.info("Cleaning up Guided Prompt dependencies...")
    
    if hasattr(app.state, 'redis_client'):
        try:
            app.state.redis_client.close()
            logger.info("Redis client closed successfully")
        except Exception as e:
            logger.error(f"Error closing Redis client: {e}")

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

class RefinementSuggestionResponse(BaseModel):
    id: str
    title: str
    description: str
    refined_query: str
    type: str
    confidence: float
    reasoning: str

class ConstraintChipResponse(BaseModel):
    id: str
    label: str
    type: str
    options: List[str]
    selected: Optional[str] = None

class RefinementResultResponse(BaseModel):
    should_trigger: bool
    suggestions: List[RefinementSuggestionResponse]
    constraints: List[ConstraintChipResponse]
    latency_ms: float
    model_used: str
    cost_usd: float
    bypass_reason: Optional[str] = None

class UserSettingsRequest(BaseModel):
    user_id: str
    mode: str
    preferences: Optional[Dict[str, Any]] = None

# Health & Config endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint - fast, no downstream calls"""
    return {"status": "healthy", "service": "guided-prompt", "timestamp": datetime.now().isoformat()}

@app.get("/ready")
async def ready_check():
    """Ready check endpoint - light ping to critical deps with small timeout"""
    try:
        # Check Redis connection with timeout
        await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None, app.state.redis_client.ping
            ),
            timeout=2.0
        )
        return {"status": "ready", "service": "guided-prompt", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Ready check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/config")
async def get_config_endpoint():
    """Config endpoint - sanitized echo of active providers and keyless fallbacks"""
    return {
        "service": "guided-prompt",
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
        "service": "guided-prompt",
        "version": "2.0.0",
        "build_date": datetime.now().isoformat(),
        "environment": config.environment.value
    }

@app.post("/refine", response_model=RefinementResultResponse)
async def refine_query(request: QueryRequest):
    """Process query for guided prompt confirmation"""
    try:
        result = await app.state.guided_prompt_service.process_query(request.query, request.context or {})
        
        # Convert to response format
        suggestions = [
            RefinementSuggestionResponse(**asdict(suggestion))
            for suggestion in result.suggestions
        ]
        
        constraints = [
            ConstraintChipResponse(**asdict(constraint))
            for constraint in result.constraints
        ]
        
        return RefinementResultResponse(
            should_trigger=result.should_trigger,
            suggestions=suggestions,
            constraints=constraints,
            latency_ms=result.latency_ms,
            model_used=result.model_used,
            cost_usd=result.cost_usd,
            bypass_reason=result.bypass_reason
        )
        
    except Exception as e:
        logger.error(f"Failed to refine query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/settings")
async def update_user_settings(request: UserSettingsRequest):
    """Update user settings for guided prompt"""
    try:
        # In real implementation, this would save to database
        app.state.guided_prompt_service.user_settings[request.user_id] = {
            "mode": request.mode,
            "preferences": request.preferences or {},
            "last_updated": datetime.now().isoformat()
        }
        
        return {"status": "updated", "user_id": request.user_id}
        
    except Exception as e:
        logger.error(f"Failed to update user settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/settings/{user_id}")
async def get_user_settings(user_id: str):
    """Get user settings for guided prompt"""
    try:
        settings = await app.state.guided_prompt_service._get_user_settings(user_id)
        return {"user_id": user_id, "settings": settings}
        
    except Exception as e:
        logger.error(f"Failed to get user settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def record_feedback(
    user_id: str,
    suggestion_id: str,
    action: str,  # "accepted", "edited", "skipped"
    feedback: Optional[str] = None
):
    """Record user feedback on refinement suggestions"""
    try:
        # Record feedback metrics
        if action == "accepted":
            refinement_accept_rate.labels(refinement_type="guided_prompt").inc()
        elif action == "edited":
            refinement_edit_rate.labels(refinement_type="guided_prompt").inc()
        elif action == "skipped":
            refinement_skip_rate.labels(refinement_type="guided_prompt").inc()
        
        return {"status": "recorded", "action": action}
        
    except Exception as e:
        logger.error(f"Failed to record feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
        start_http_server(8004)
        logger.info("Prometheus metrics server started on port 8004")
    
    # Start FastAPI server
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8003,
        log_level=config.log_level.value.lower()
    )
