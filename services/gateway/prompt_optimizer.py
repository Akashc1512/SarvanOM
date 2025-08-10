#!/usr/bin/env python3
"""
Advanced Prompt Optimization System for SarvanOM
Implements MAANG/OpenAI/Perplexity level prompt optimization for faster responses
"""

import asyncio
import json
import logging
import time
import hashlib
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import re
import pickle
from collections import defaultdict
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

class PromptType(Enum):
    """Prompt types for different use cases"""
    SEARCH = "search"
    FACT_CHECK = "fact_check"
    SYNTHESIS = "synthesis"
    ANALYSIS = "analysis"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    CODE_GENERATION = "code_generation"

class PromptComplexity(Enum):
    """Prompt complexity levels"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    EXPERT = "expert"

class OptimizationStrategy(Enum):
    """Prompt optimization strategies"""
    LENGTH_REDUCTION = "length_reduction"
    CLARITY_IMPROVEMENT = "clarity_improvement"
    CONTEXT_OPTIMIZATION = "context_optimization"
    TOKEN_EFFICIENCY = "token_efficiency"
    RESPONSE_QUALITY = "response_quality"

@dataclass
class OptimizedPrompt:
    """Optimized prompt structure"""
    original_prompt: str
    optimized_prompt: str
    prompt_type: PromptType
    complexity: PromptComplexity
    optimization_strategies: List[OptimizationStrategy]
    token_count_original: int
    token_count_optimized: int
    performance_metrics: Dict[str, float]
    created_at: datetime
    usage_count: int = 0
    average_response_time: float = 0.0
    success_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "original_prompt": self.original_prompt,
            "optimized_prompt": self.optimized_prompt,
            "prompt_type": self.prompt_type.value,
            "complexity": self.complexity.value,
            "optimization_strategies": [s.value for s in self.optimization_strategies],
            "token_count_original": self.token_count_original,
            "token_count_optimized": self.token_count_optimized,
            "performance_metrics": self.performance_metrics,
            "created_at": self.created_at.isoformat(),
            "usage_count": self.usage_count,
            "average_response_time": self.average_response_time,
            "success_rate": self.success_rate
        }

class PromptOptimizer:
    """
    Advanced prompt optimization system for faster and better responses
    Following MAANG/OpenAI/Perplexity industry standards
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        enable_caching: bool = True,
        enable_analytics: bool = True,
        max_prompt_length: int = 4000,
        min_prompt_length: int = 10,
        optimization_threshold: float = 0.1,  # 10% improvement required
        cache_ttl: int = 86400  # 24 hours
    ):
        self.redis_url = redis_url
        self.redis_client: Optional[aioredis.Redis] = None
        self.enable_caching = enable_caching
        self.enable_analytics = enable_analytics
        self.max_prompt_length = max_prompt_length
        self.min_prompt_length = min_prompt_length
        self.optimization_threshold = optimization_threshold
        self.cache_ttl = cache_ttl
        
        # Prompt templates and patterns
        self.prompt_templates = self._load_prompt_templates()
        self.optimization_patterns = self._load_optimization_patterns()
        
        # Performance tracking
        self.performance_history: Dict[str, List[float]] = defaultdict(list)
        self.optimization_cache: Dict[str, OptimizedPrompt] = {}
        
        # Metrics
        self.metrics = {
            "total_optimizations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_optimization_time": 0.0,
            "total_time_saved": 0.0,
            "successful_optimizations": 0
        }
    
    async def initialize(self) -> None:
        """Initialize Redis connection for caching"""
        try:
            if self.redis_url and self.enable_caching:
                self.redis_client = aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=False,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                await self.redis_client.ping()
                logger.info("✅ Redis cache initialized for prompt optimization")
            else:
                logger.info("ℹ️ Using in-memory prompt optimization only")
        except Exception as e:
            logger.error(f"❌ Redis initialization failed: {e}")
            self.redis_client = None
    
    def _load_prompt_templates(self) -> Dict[PromptType, Dict[str, str]]:
        """Load optimized prompt templates"""
        return {
            PromptType.SEARCH: {
                "simple": "Find information about: {query}",
                "medium": "Search for comprehensive information on: {query}. Include key facts and sources.",
                "complex": "Conduct an in-depth search for: {query}. Provide detailed analysis with multiple perspectives, key findings, and reliable sources.",
                "expert": "Perform expert-level research on: {query}. Include comprehensive analysis, multiple viewpoints, statistical data, expert opinions, and authoritative sources with detailed explanations."
            },
            PromptType.FACT_CHECK: {
                "simple": "Verify: {claim}",
                "medium": "Fact-check this claim: {claim}. Provide evidence and sources.",
                "complex": "Conduct thorough fact-checking on: {claim}. Analyze multiple sources, identify biases, and provide confidence levels.",
                "expert": "Perform comprehensive fact verification for: {claim}. Include source credibility analysis, bias assessment, conflicting evidence evaluation, and confidence scoring with detailed reasoning."
            },
            PromptType.SYNTHESIS: {
                "simple": "Summarize: {content}",
                "medium": "Synthesize and summarize: {content}. Include key points and conclusions.",
                "complex": "Create a comprehensive synthesis of: {content}. Integrate multiple perspectives and provide detailed analysis.",
                "expert": "Generate expert-level synthesis of: {content}. Include comprehensive analysis, integration of multiple sources, critical evaluation, and detailed conclusions with supporting evidence."
            },
            PromptType.ANALYSIS: {
                "simple": "Analyze: {content}",
                "medium": "Provide detailed analysis of: {content}. Include key insights and implications.",
                "complex": "Conduct comprehensive analysis of: {content}. Include multiple perspectives, implications, and recommendations.",
                "expert": "Perform expert analysis of: {content}. Include comprehensive evaluation, multiple analytical frameworks, detailed insights, and actionable recommendations."
            }
        }
    
    def _load_optimization_patterns(self) -> Dict[str, List[Tuple[str, str]]]:
        """Load optimization patterns and replacements"""
        return {
            "redundancy_removal": [
                (r"\b(very|extremely|really|quite)\s+", ""),
                (r"\b(in order to|so as to)\b", "to"),
                (r"\b(due to the fact that|because of the fact that)\b", "because"),
                (r"\b(at this point in time|at the present time)\b", "now"),
                (r"\b(in the event that|in case)\b", "if"),
            ],
            "clarity_improvement": [
                (r"\b(utilize|utilization)\b", "use"),
                (r"\b(implement|implementation)\b", "put into practice"),
                (r"\b(commence|initiate)\b", "start"),
                (r"\b(terminate|cease)\b", "stop"),
                (r"\b(endeavor|attempt)\b", "try"),
            ],
            "structure_optimization": [
                (r"Please\s+", ""),
                (r"Kindly\s+", ""),
                (r"Would you mind\s+", ""),
                (r"I would like you to\s+", ""),
                (r"Could you please\s+", ""),
            ],
            "context_enhancement": [
                (r"explain\b", "provide detailed explanation of"),
                (r"describe\b", "give comprehensive description of"),
                (r"analyze\b", "conduct thorough analysis of"),
                (r"compare\b", "provide detailed comparison of"),
                (r"evaluate\b", "conduct comprehensive evaluation of"),
            ]
        }
    
    async def optimize_prompt(
        self,
        prompt: str,
        prompt_type: PromptType,
        complexity: PromptComplexity = PromptComplexity.MEDIUM,
        target_length: Optional[int] = None,
        optimization_strategies: Optional[List[OptimizationStrategy]] = None
    ) -> OptimizedPrompt:
        """Optimize a prompt for better performance"""
        start_time = time.time()
        
        # Check cache first
        cache_key = self._generate_cache_key(prompt, prompt_type, complexity)
        cached_result = await self._get_cached_optimization(cache_key)
        if cached_result:
            self.metrics["cache_hits"] += 1
            return cached_result
        
        self.metrics["cache_misses"] += 1
        
        # Apply optimization strategies
        optimized_prompt = prompt
        applied_strategies = []
        
        if optimization_strategies is None:
            optimization_strategies = [
                OptimizationStrategy.LENGTH_REDUCTION,
                OptimizationStrategy.CLARITY_IMPROVEMENT,
                OptimizationStrategy.TOKEN_EFFICIENCY
            ]
        
        # Apply template-based optimization
        if prompt_type in self.prompt_templates:
            template = self.prompt_templates[prompt_type].get(complexity.value)
            if template and self._should_use_template(prompt, template):
                optimized_prompt = template.format(query=prompt)
                applied_strategies.append(OptimizationStrategy.CONTEXT_OPTIMIZATION)
        
        # Apply pattern-based optimizations
        for strategy in optimization_strategies:
            if strategy == OptimizationStrategy.LENGTH_REDUCTION:
                optimized_prompt = self._apply_length_reduction(optimized_prompt)
                applied_strategies.append(strategy)
            elif strategy == OptimizationStrategy.CLARITY_IMPROVEMENT:
                optimized_prompt = self._apply_clarity_improvement(optimized_prompt)
                applied_strategies.append(strategy)
            elif strategy == OptimizationStrategy.TOKEN_EFFICIENCY:
                optimized_prompt = self._apply_token_efficiency(optimized_prompt)
                applied_strategies.append(strategy)
        
        # Apply target length optimization if specified
        if target_length and len(optimized_prompt) > target_length:
            optimized_prompt = self._truncate_to_length(optimized_prompt, target_length)
            applied_strategies.append(OptimizationStrategy.LENGTH_REDUCTION)
        
        # Calculate metrics
        token_count_original = self._estimate_tokens(prompt)
        token_count_optimized = self._estimate_tokens(optimized_prompt)
        
        optimization_time = time.time() - start_time
        self.metrics["total_optimizations"] += 1
        self.metrics["average_optimization_time"] = (
            (self.metrics["average_optimization_time"] * (self.metrics["total_optimizations"] - 1) + optimization_time) /
            self.metrics["total_optimizations"]
        )
        
        # Create optimized prompt object
        optimized_prompt_obj = OptimizedPrompt(
            original_prompt=prompt,
            optimized_prompt=optimized_prompt,
            prompt_type=prompt_type,
            complexity=complexity,
            optimization_strategies=applied_strategies,
            token_count_original=token_count_original,
            token_count_optimized=token_count_optimized,
            performance_metrics={
                "length_reduction": (len(prompt) - len(optimized_prompt)) / len(prompt) * 100,
                "token_reduction": (token_count_original - token_count_optimized) / token_count_original * 100,
                "optimization_time": optimization_time
            },
            created_at=datetime.now()
        )
        
        # Cache the result
        await self._cache_optimization(cache_key, optimized_prompt_obj)
        
        # Update performance history
        self.performance_history[prompt_type.value].append(optimization_time)
        
        logger.info(f"✅ Prompt optimized: {len(prompt)} -> {len(optimized_prompt)} chars, {token_count_original} -> {token_count_optimized} tokens")
        
        return optimized_prompt_obj
    
    def _apply_length_reduction(self, prompt: str) -> str:
        """Apply length reduction optimizations"""
        optimized = prompt
        
        # Apply redundancy removal patterns
        for pattern, replacement in self.optimization_patterns["redundancy_removal"]:
            optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
        
        # Remove excessive whitespace
        optimized = re.sub(r'\s+', ' ', optimized).strip()
        
        # Remove unnecessary punctuation
        optimized = re.sub(r'[.!?]+', '.', optimized)
        
        return optimized
    
    def _apply_clarity_improvement(self, prompt: str) -> str:
        """Apply clarity improvement optimizations"""
        optimized = prompt
        
        # Apply clarity patterns
        for pattern, replacement in self.optimization_patterns["clarity_improvement"]:
            optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
        
        # Apply structure optimization
        for pattern, replacement in self.optimization_patterns["structure_optimization"]:
            optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
        
        return optimized
    
    def _apply_token_efficiency(self, prompt: str) -> str:
        """Apply token efficiency optimizations"""
        optimized = prompt
        
        # Use shorter synonyms for common phrases
        token_efficiency_map = {
            "in order to": "to",
            "due to the fact that": "because",
            "at this point in time": "now",
            "in the event that": "if",
            "with regard to": "regarding",
            "in terms of": "for",
            "as far as": "for",
            "in the case of": "for",
        }
        
        for long_phrase, short_phrase in token_efficiency_map.items():
            optimized = re.sub(rf'\b{re.escape(long_phrase)}\b', short_phrase, optimized, flags=re.IGNORECASE)
        
        return optimized
    
    def _should_use_template(self, prompt: str, template: str) -> bool:
        """Determine if template should be used"""
        # Use template if prompt is too short or lacks structure
        return len(prompt) < 50 or not any(keyword in prompt.lower() for keyword in ["search", "find", "analyze", "check", "verify"])
    
    def _truncate_to_length(self, prompt: str, target_length: int) -> str:
        """Truncate prompt to target length while preserving meaning"""
        if len(prompt) <= target_length:
            return prompt
        
        # Try to truncate at sentence boundaries
        sentences = re.split(r'[.!?]+', prompt)
        truncated = ""
        
        for sentence in sentences:
            if len(truncated + sentence) <= target_length:
                truncated += sentence + "."
            else:
                break
        
        return truncated.strip() or prompt[:target_length]
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    def _generate_cache_key(self, prompt: str, prompt_type: PromptType, complexity: PromptComplexity) -> str:
        """Generate cache key for optimization"""
        key_data = f"{prompt_type.value}:{complexity.value}:{prompt}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    async def _get_cached_optimization(self, cache_key: str) -> Optional[OptimizedPrompt]:
        """Get cached optimization result"""
        if not self.enable_caching:
            return None
        
        try:
            if self.redis_client:
                cached_data = await self.redis_client.get(f"prompt_opt:{cache_key}")
                if cached_data:
                    return pickle.loads(cached_data)
            else:
                return self.optimization_cache.get(cache_key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        
        return None
    
    async def _cache_optimization(self, cache_key: str, optimized_prompt: OptimizedPrompt) -> None:
        """Cache optimization result"""
        if not self.enable_caching:
            return
        
        try:
            if self.redis_client:
                await self.redis_client.setex(
                    f"prompt_opt:{cache_key}",
                    self.cache_ttl,
                    pickle.dumps(optimized_prompt)
                )
            else:
                self.optimization_cache[cache_key] = optimized_prompt
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    async def update_performance_metrics(
        self,
        prompt_hash: str,
        response_time: float,
        success: bool
    ) -> None:
        """Update performance metrics for a prompt"""
        try:
            if self.redis_client:
                # Update Redis metrics
                metrics_key = f"prompt_metrics:{prompt_hash}"
                metrics_data = await self.redis_client.get(metrics_key)
                
                if metrics_data:
                    metrics = pickle.loads(metrics_data)
                else:
                    metrics = {
                        "usage_count": 0,
                        "total_response_time": 0.0,
                        "successful_responses": 0,
                        "total_responses": 0
                    }
                
                metrics["usage_count"] += 1
                metrics["total_response_time"] += response_time
                metrics["total_responses"] += 1
                if success:
                    metrics["successful_responses"] += 1
                
                metrics["average_response_time"] = metrics["total_response_time"] / metrics["usage_count"]
                metrics["success_rate"] = metrics["successful_responses"] / metrics["total_responses"] * 100
                
                await self.redis_client.setex(
                    metrics_key,
                    self.cache_ttl,
                    pickle.dumps(metrics)
                )
        except Exception as e:
            logger.error(f"Performance metrics update error: {e}")
    
    async def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        return {
            "total_optimizations": self.metrics["total_optimizations"],
            "cache_hits": self.metrics["cache_hits"],
            "cache_misses": self.metrics["cache_misses"],
            "cache_hit_rate": (
                self.metrics["cache_hits"] / (self.metrics["cache_hits"] + self.metrics["cache_misses"]) * 100
                if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0 else 0
            ),
            "average_optimization_time": self.metrics["average_optimization_time"],
            "total_time_saved": self.metrics["total_time_saved"],
            "successful_optimizations": self.metrics["successful_optimizations"],
            "performance_history": dict(self.performance_history),
            "cache_size": len(self.optimization_cache) if not self.redis_client else "unknown"
        }
    
    async def clear_cache(self) -> None:
        """Clear optimization cache"""
        try:
            if self.redis_client:
                # Clear Redis cache (this would clear all keys, be careful in production)
                keys = await self.redis_client.keys("prompt_opt:*")
                if keys:
                    await self.redis_client.delete(*keys)
            else:
                self.optimization_cache.clear()
            
            logger.info("Prompt optimization cache cleared")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
    
    async def close(self) -> None:
        """Close prompt optimizer"""
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Prompt optimizer closed")

# Global prompt optimizer instance
prompt_optimizer = PromptOptimizer()
