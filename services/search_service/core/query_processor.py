"""
Query Intelligence Layer - Universal Knowledge Platform
Core query analysis and intelligence processing.
"""
import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse

import redis
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)


class IntentType(str, Enum):
    """Query intent classification types."""
    FACTUAL = "factual"
    ANALYTICAL = "analytical"
    COMPARATIVE = "comparative"
    CREATIVE = "creative"
    PROCEDURAL = "procedural"
    OPINION = "opinion"
    UNKNOWN = "unknown"


class ComplexityLevel(str, Enum):
    """Query complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXPERT = "expert"


class DomainType(str, Enum):
    """Domain classification types."""
    TECHNOLOGY = "technology"
    SCIENCE = "science"
    BUSINESS = "business"
    HEALTH = "health"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    POLITICS = "politics"
    SPORTS = "sports"
    GENERAL = "general"


@dataclass
class ProcessedQuery:
    """Processed query with intelligence metadata."""
    original_query: str
    intent: IntentType
    complexity: ComplexityLevel
    domains: List[DomainType]
    fingerprint: str
    confidence_score: float
    processing_time_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "original_query": self.original_query,
            "intent": self.intent.value if hasattr(self.intent, 'value') else str(self.intent),
            "complexity": self.complexity.value if hasattr(self.complexity, 'value') else str(self.complexity),
            "domains": [d.value if hasattr(d, 'value') else str(d) for d in self.domains],
            "fingerprint": self.fingerprint,
            "confidence_score": self.confidence_score,
            "processing_time_ms": self.processing_time_ms,
            "timestamp": self.timestamp.isoformat() if hasattr(self.timestamp, 'isoformat') else str(self.timestamp),
            "metadata": self.metadata
        }


class IntentClassifier:
    """Classifies query intent using keyword analysis and ML patterns."""
    
    def __init__(self):
        self.intent_keywords = {
            IntentType.FACTUAL: ["what", "when", "where", "who", "how many", "define", "explain"],
            IntentType.ANALYTICAL: ["analyze", "compare", "evaluate", "assess", "examine", "study"],
            IntentType.COMPARATIVE: ["vs", "versus", "compare", "difference", "similar", "better"],
            IntentType.CREATIVE: ["create", "design", "generate", "imagine", "brainstorm", "innovate"],
            IntentType.PROCEDURAL: ["how to", "steps", "process", "procedure", "guide", "tutorial"],
            IntentType.OPINION: ["opinion", "think", "believe", "feel", "view", "perspective"]
        }
        logger.info("IntentClassifier initialized")
    
    async def classify_intent(self, query: str) -> Tuple[IntentType, float]:
        """Classify query intent with confidence score."""
        start_time = time.time()
        
        query_lower = query.lower()
        scores = {}
        
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            scores[intent] = score / len(keywords) if keywords else 0
        
        # Find best match
        best_intent = max(scores.items(), key=lambda x: x[1])
        confidence = min(best_intent[1] * 2, 1.0)  # Scale confidence
        
        if confidence < 0.3:
            best_intent = (IntentType.UNKNOWN, 0.5)
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"Intent classified as {best_intent[0]} with confidence {confidence:.2f}")
        
        return best_intent[0], confidence


class ComplexityScorer:
    """Scores query complexity based on multiple factors."""
    
    def __init__(self):
        self.complexity_indicators = {
            ComplexityLevel.SIMPLE: ["basic", "simple", "easy", "quick"],
            ComplexityLevel.MODERATE: ["detailed", "explain", "describe", "understand"],
            ComplexityLevel.COMPLEX: ["analysis", "research", "study", "investigate", "comprehensive"],
            ComplexityLevel.EXPERT: ["expert", "advanced", "technical", "academic", "research"]
        }
        logger.info("ComplexityScorer initialized")
    
    async def score_complexity(self, query: str) -> Tuple[ComplexityLevel, float]:
        """Score query complexity with confidence."""
        start_time = time.time()
        
        query_lower = query.lower()
        word_count = len(query.split())
        
        # Base complexity on word count
        if word_count <= 3:
            base_complexity = ComplexityLevel.SIMPLE
        elif word_count <= 8:
            base_complexity = ComplexityLevel.MODERATE
        elif word_count <= 15:
            base_complexity = ComplexityLevel.COMPLEX
        else:
            base_complexity = ComplexityLevel.EXPERT
        
        # Adjust based on keywords
        for level, indicators in self.complexity_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                base_complexity = level
                break
        
        # Calculate confidence based on clarity
        confidence = min(word_count / 20.0, 1.0)
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"Complexity scored as {base_complexity} with confidence {confidence:.2f}")
        
        return base_complexity, confidence


class DomainDetector:
    """Detects query domains using keyword analysis."""
    
    def __init__(self):
        self.domain_keywords = {
            DomainType.TECHNOLOGY: ["tech", "software", "programming", "computer", "digital", "ai", "ml"],
            DomainType.SCIENCE: ["science", "research", "study", "experiment", "theory", "hypothesis"],
            DomainType.BUSINESS: ["business", "market", "company", "industry", "finance", "economics"],
            DomainType.HEALTH: ["health", "medical", "medicine", "disease", "treatment", "symptoms"],
            DomainType.EDUCATION: ["education", "learn", "teach", "school", "university", "course"],
            DomainType.ENTERTAINMENT: ["movie", "music", "game", "entertainment", "celebrity", "show"],
            DomainType.POLITICS: ["politics", "government", "policy", "election", "political", "law"],
            DomainType.SPORTS: ["sport", "game", "team", "player", "match", "tournament"]
        }
        logger.info("DomainDetector initialized")
    
    async def detect_domains(self, query: str) -> List[Tuple[DomainType, float]]:
        """Detect query domains with confidence scores."""
        start_time = time.time()
        
        query_lower = query.lower()
        domain_scores = []
        
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                confidence = min(score / len(keywords), 1.0)
                domain_scores.append((domain, confidence))
        
        # Sort by confidence and return top domains
        domain_scores.sort(key=lambda x: x[1], reverse=True)
        
        # If no specific domains detected, return general
        if not domain_scores:
            domain_scores = [(DomainType.GENERAL, 0.5)]
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"Detected domains: {[d[0] for d in domain_scores[:3]]}")
        
        return domain_scores[:3]  # Return top 3 domains


class QueryFingerprinter:
    """Creates unique fingerprints for queries."""
    
    def __init__(self):
        logger.info("QueryFingerprinter initialized")
    
    async def create_fingerprint(self, query: str) -> str:
        """Create a unique fingerprint for the query."""
        start_time = time.time()
        
        # Normalize query
        normalized = query.lower().strip()
        
        # Create hash
        fingerprint = hashlib.sha256(normalized.encode()).hexdigest()[:16]
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"Created fingerprint: {fingerprint}")
        
        return fingerprint


class QueryCache:
    """Caches processed queries for performance."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        try:
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()
            logger.info("QueryCache connected to Redis")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
    
    async def get_cached_result(self, fingerprint: str) -> Optional[ProcessedQuery]:
        """Get cached query result."""
        if not self.redis_client:
            return None
        
        try:
            cached_data = self.redis_client.get(f"query:{fingerprint}")
            if cached_data:
                data = json.loads(cached_data)
                return ProcessedQuery(**data)
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
        
        return None
    
    async def cache_result(self, fingerprint: str, result: ProcessedQuery, ttl: int = 3600):
        """Cache query result."""
        if not self.redis_client:
            return
        
        try:
            data = {
                "original_query": result.original_query,
                "intent": result.intent.value,
                "complexity": result.complexity.value,
                "domains": [d.value for d in result.domains],
                "fingerprint": result.fingerprint,
                "confidence_score": result.confidence_score,
                "processing_time_ms": result.processing_time_ms,
                "timestamp": result.timestamp.isoformat(),
                "metadata": result.metadata
            }
            self.redis_client.setex(f"query:{fingerprint}", ttl, json.dumps(data))
            logger.info(f"Cached query result: {fingerprint}")
        except Exception as e:
            logger.error(f"Cache storage error: {e}")


class QueryIntelligenceLayer:
    """Main query intelligence processing layer."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.intent_classifier = IntentClassifier()
        self.complexity_scorer = ComplexityScorer()
        self.domain_detector = DomainDetector()
        self.fingerprinter = QueryFingerprinter()
        self.query_cache = QueryCache(redis_url)
        logger.info("QueryIntelligenceLayer initialized")
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> ProcessedQuery:
        """Process query through the intelligence layer."""
        start_time = time.time()
        
        # Create fingerprint first
        fingerprint = await self.fingerprinter.create_fingerprint(query)
        
        # Check cache
        cached_result = await self.query_cache.get_cached_result(fingerprint)
        if cached_result:
            logger.info("Returning cached query result")
            return cached_result
        
        # Process query
        intent, intent_confidence = await self.intent_classifier.classify_intent(query)
        complexity, complexity_confidence = await self.complexity_scorer.score_complexity(query)
        domains_with_confidence = await self.domain_detector.detect_domains(query)
        
        # Extract domain types
        domains = [domain for domain, _ in domains_with_confidence]
        
        # Calculate overall confidence
        confidence_score = (intent_confidence + complexity_confidence) / 2
        
        # Create result
        processing_time = (time.time() - start_time) * 1000
        result = ProcessedQuery(
            original_query=query,
            intent=intent,
            complexity=complexity,
            domains=domains,
            fingerprint=fingerprint,
            confidence_score=confidence_score,
            processing_time_ms=processing_time,
            metadata={
                "intent_confidence": intent_confidence,
                "complexity_confidence": complexity_confidence,
                "domain_confidences": domains_with_confidence,
                "context": context or {}
            }
        )
        
        # Cache result
        await self.query_cache.cache_result(fingerprint, result)
        
        logger.info(f"Query processed: {intent} {complexity} {domains}")
        return result
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            "cache_hits": 0,  # TODO: Implement cache hit tracking
            "cache_misses": 0,  # TODO: Implement cache miss tracking
            "average_processing_time": 0.0,  # TODO: Implement time tracking
            "total_queries_processed": 0  # TODO: Implement counter
        } 