"""
Hugging Face Inference API Fallback - SarvanOM v2

Free-tier friendly fallback using HF Inference API for refinement only.
Respects guided prompt budgets and auto-bypasses on rate limits.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import httpx
from prometheus_client import Counter, Histogram, Gauge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
hf_inference_requests = Counter('sarvanom_hf_inference_requests_total', 'Total HF inference requests', ['model', 'status'])
hf_inference_latency = Histogram('sarvanom_hf_inference_latency_ms', 'HF inference latency', ['model', 'operation'])
hf_inference_rate_limited = Counter('sarvanom_hf_inference_rate_limited_total', 'HF inference rate limited', ['model'])
refiner_latency_hf_api = Histogram('sarvanom_refiner_latency_hf_api_ms', 'Refiner latency via HF API', ['model'])

class FallbackStatus(str, Enum):
    AVAILABLE = "available"
    RATE_LIMITED = "rate_limited"
    UNAVAILABLE = "unavailable"
    BYPASSED = "bypassed"

@dataclass
class HFInferenceConfig:
    """Configuration for HF Inference API fallback"""
    api_key: Optional[str] = None
    base_url: str = "https://api-inference.huggingface.co/models"
    timeout_ms: int = 500  # Guided prompt budget
    max_retries: int = 2
    rate_limit_delay: float = 1.0
    enabled: bool = True
    models: List[str] = None
    
    def __post_init__(self):
        if self.models is None:
            # Free-tier friendly models for refinement
            self.models = [
                "microsoft/DialoGPT-medium",  # Fast, good for refinement
                "distilbert-base-uncased",    # Fast embeddings
                "facebook/blenderbot-400M-distill",  # Fast conversation
            ]

@dataclass
class RefinementRequest:
    """Request for refinement via HF Inference API"""
    query: str
    context: Optional[str] = None
    max_length: int = 100
    temperature: float = 0.7
    timeout_ms: int = 500

@dataclass
class RefinementResponse:
    """Response from HF Inference API refinement"""
    refined_query: str
    confidence: float
    model_used: str
    latency_ms: float
    status: str
    fallback_used: bool = True
    rate_limited: bool = False

class HFInferenceFallback:
    """Hugging Face Inference API fallback for guided prompt refinement"""
    
    def __init__(self, config: HFInferenceConfig = None):
        self.config = config or HFInferenceConfig()
        self.rate_limit_status = {}  # Track rate limit status per model
        self.last_request_time = {}  # Track last request time per model
        self.request_count = {}      # Track request count per model
        
        # Rate limiting thresholds (free-tier friendly)
        self.rate_limit_thresholds = {
            "requests_per_minute": 10,  # Conservative for free tier
            "requests_per_hour": 100,   # Conservative for free tier
        }
    
    async def refine_query(self, request: RefinementRequest) -> RefinementResponse:
        """Refine query using HF Inference API fallback"""
        start_time = time.time()
        
        try:
            # Check if fallback is available
            if not self._is_fallback_available():
                return self._create_fallback_response(
                    request.query, 
                    "unavailable", 
                    time.time() - start_time,
                    "Fallback not available"
                )
            
            # Select best model for refinement
            model = self._select_refinement_model()
            
            # Check rate limits
            if self._is_rate_limited(model):
                logger.warning(f"Rate limited for model {model}, bypassing")
                hf_inference_rate_limited.labels(model=model).inc()
                return self._create_fallback_response(
                    request.query,
                    "rate_limited",
                    time.time() - start_time,
                    f"Rate limited for {model}"
                )
            
            # Make inference request
            response = await self._make_inference_request(model, request)
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Update metrics
            hf_inference_requests.labels(model=model, status="success").inc()
            hf_inference_latency.labels(model=model, operation="refinement").observe(latency_ms)
            refiner_latency_hf_api.labels(model=model).observe(latency_ms)
            
            # Update rate limiting tracking
            self._update_rate_limit_tracking(model)
            
            return RefinementResponse(
                refined_query=response.get("refined_query", request.query),
                confidence=response.get("confidence", 0.5),
                model_used=model,
                latency_ms=latency_ms,
                status="success",
                fallback_used=True,
                rate_limited=False
            )
            
        except httpx.TimeoutException:
            logger.warning("HF Inference API timeout, bypassing")
            return self._create_fallback_response(
                request.query,
                "timeout",
                time.time() - start_time,
                "Request timeout"
            )
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Rate limited
                logger.warning("HF Inference API rate limited, bypassing")
                hf_inference_rate_limited.labels(model="unknown").inc()
                return self._create_fallback_response(
                    request.query,
                    "rate_limited",
                    time.time() - start_time,
                    "Rate limited by HF API"
                )
            else:
                logger.error(f"HF Inference API error: {e}")
                return self._create_fallback_response(
                    request.query,
                    "error",
                    time.time() - start_time,
                    f"API error: {e.response.status_code}"
                )
                
        except Exception as e:
            logger.error(f"HF Inference fallback error: {e}")
            return self._create_fallback_response(
                request.query,
                "error",
                time.time() - start_time,
                f"Unexpected error: {str(e)}"
            )
    
    def _is_fallback_available(self) -> bool:
        """Check if HF Inference fallback is available"""
        return (
            self.config.enabled and
            self.config.api_key is not None and
            len(self.config.models) > 0
        )
    
    def _select_refinement_model(self) -> str:
        """Select best model for refinement"""
        # For free-tier, prefer faster, smaller models
        available_models = [
            model for model in self.config.models
            if not self._is_rate_limited(model)
        ]
        
        if not available_models:
            # Fallback to any model if all are rate limited
            available_models = self.config.models
        
        # Prefer models optimized for refinement
        refinement_models = [
            "microsoft/DialoGPT-medium",
            "facebook/blenderbot-400M-distill",
            "distilbert-base-uncased"
        ]
        
        for model in refinement_models:
            if model in available_models:
                return model
        
        # Return first available model
        return available_models[0] if available_models else self.config.models[0]
    
    def _is_rate_limited(self, model: str) -> bool:
        """Check if model is rate limited"""
        if model not in self.rate_limit_status:
            return False
        
        status = self.rate_limit_status[model]
        return status == FallbackStatus.RATE_LIMITED
    
    async def _make_inference_request(self, model: str, request: RefinementRequest) -> Dict[str, Any]:
        """Make inference request to HF API"""
        url = f"{self.config.base_url}/{model}"
        
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        
        # Prepare payload for refinement
        payload = {
            "inputs": request.query,
            "parameters": {
                "max_length": request.max_length,
                "temperature": request.temperature,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        # Add context if provided
        if request.context:
            payload["inputs"] = f"Context: {request.context}\nQuery: {request.query}"
        
        async with httpx.AsyncClient(timeout=request.timeout_ms / 1000.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # Process response for refinement
            if isinstance(result, list) and len(result) > 0:
                refined_text = result[0].get("generated_text", request.query)
            elif isinstance(result, dict):
                refined_text = result.get("generated_text", request.query)
            else:
                refined_text = request.query
            
            # Calculate confidence (simple heuristic)
            confidence = self._calculate_refinement_confidence(request.query, refined_text)
            
            return {
                "refined_query": refined_text,
                "confidence": confidence,
                "raw_response": result
            }
    
    def _calculate_refinement_confidence(self, original: str, refined: str) -> float:
        """Calculate confidence score for refinement"""
        if not original or not refined:
            return 0.0
        
        # Simple confidence based on length and similarity
        original_words = set(original.lower().split())
        refined_words = set(refined.lower().split())
        
        # Word overlap ratio
        overlap = len(original_words.intersection(refined_words))
        total_words = len(original_words.union(refined_words))
        
        if total_words == 0:
            return 0.0
        
        overlap_ratio = overlap / total_words
        
        # Length ratio (refined should be similar or longer)
        length_ratio = min(len(refined) / len(original), 1.0) if original else 0.0
        
        # Combined confidence
        confidence = (overlap_ratio * 0.6) + (length_ratio * 0.4)
        
        return min(confidence, 1.0)
    
    def _update_rate_limit_tracking(self, model: str):
        """Update rate limiting tracking for model"""
        current_time = time.time()
        
        # Update request count
        if model not in self.request_count:
            self.request_count[model] = 0
        self.request_count[model] += 1
        
        # Update last request time
        self.last_request_time[model] = current_time
        
        # Check if rate limited
        if self._check_rate_limit_violation(model):
            self.rate_limit_status[model] = FallbackStatus.RATE_LIMITED
            logger.warning(f"Model {model} is now rate limited")
        else:
            self.rate_limit_status[model] = FallbackStatus.AVAILABLE
    
    def _check_rate_limit_violation(self, model: str) -> bool:
        """Check if model has violated rate limits"""
        current_time = time.time()
        
        # Check requests per minute
        if model in self.last_request_time:
            time_since_last = current_time - self.last_request_time[model]
            if time_since_last < 60:  # Within last minute
                requests_this_minute = self.request_count.get(model, 0)
                if requests_this_minute > self.rate_limit_thresholds["requests_per_minute"]:
                    return True
        
        # Check requests per hour (simplified)
        if model in self.request_count:
            if self.request_count[model] > self.rate_limit_thresholds["requests_per_hour"]:
                return True
        
        return False
    
    def _create_fallback_response(
        self, 
        original_query: str, 
        status: str, 
        latency: float, 
        error_message: str = None
    ) -> RefinementResponse:
        """Create fallback response when HF API is unavailable"""
        return RefinementResponse(
            refined_query=original_query,  # Return original query
            confidence=0.0,
            model_used="fallback",
            latency_ms=latency * 1000,
            status=status,
            fallback_used=True,
            rate_limited=status == "rate_limited"
        )
    
    async def check_model_availability(self, model: str) -> Dict[str, Any]:
        """Check availability of a specific model"""
        try:
            url = f"{self.config.base_url}/{model}"
            headers = {}
            
            if self.config.api_key:
                headers["Authorization"] = f"Bearer {self.config.api_key}"
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, headers=headers)
                
                return {
                    "model": model,
                    "available": response.status_code == 200,
                    "status_code": response.status_code,
                    "rate_limited": self._is_rate_limited(model)
                }
                
        except Exception as e:
            return {
                "model": model,
                "available": False,
                "error": str(e),
                "rate_limited": False
            }
    
    async def get_fallback_status(self) -> Dict[str, Any]:
        """Get overall fallback status"""
        return {
            "enabled": self.config.enabled,
            "api_key_configured": self.config.api_key is not None,
            "models_configured": len(self.config.models),
            "rate_limited_models": [
                model for model, status in self.rate_limit_status.items()
                if status == FallbackStatus.RATE_LIMITED
            ],
            "total_requests": sum(self.request_count.values()),
            "last_request": max(self.last_request_time.values()) if self.last_request_time else None
        }
    
    def reset_rate_limits(self):
        """Reset rate limiting for all models"""
        self.rate_limit_status.clear()
        self.last_request_time.clear()
        self.request_count.clear()
        logger.info("Rate limits reset for all models")

# Integration with model router
class HFRefinementFallback:
    """Integration class for HF refinement fallback in model router"""
    
    def __init__(self, hf_api_key: Optional[str] = None):
        self.hf_fallback = HFInferenceFallback(
            HFInferenceConfig(
                api_key=hf_api_key,
                enabled=hf_api_key is not None
            )
        )
    
    async def refine_with_fallback(self, query: str, context: str = None) -> Dict[str, Any]:
        """Refine query with HF fallback if available"""
        request = RefinementRequest(
            query=query,
            context=context,
            max_length=100,
            temperature=0.7,
            timeout_ms=500  # Guided prompt budget
        )
        
        response = await self.hf_fallback.refine_query(request)
        
        return {
            "refined_query": response.refined_query,
            "confidence": response.confidence,
            "fallback_used": response.fallback_used,
            "model_used": response.model_used,
            "latency_ms": response.latency_ms,
            "status": response.status,
            "rate_limited": response.rate_limited
        }

# Example usage
async def main():
    """Example usage of HF inference fallback"""
    # Initialize with API key (would come from environment)
    fallback = HFRefinementFallback(hf_api_key="your_hf_api_key_here")
    
    # Test refinement
    result = await fallback.refine_with_fallback(
        query="show me apple",
        context="You are helping with search queries"
    )
    
    print(f"Refinement result: {result}")
    
    # Check fallback status
    status = await fallback.hf_fallback.get_fallback_status()
    print(f"Fallback status: {status}")

if __name__ == "__main__":
    asyncio.run(main())
