"""
Feeds Router - SarvanOM v2 Model Registry

Router for news and markets endpoints with normalized schemas and parallel fan-out.
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
import asyncio
import time
import logging

from .feeds_models import (
    FeedsRequest, FeedsResponse, ProviderResult, 
    NormalizedNewsItem, NormalizedMarketsItem
)
from .feeds_adapters import NewsAdapter, MarketsAdapter

# Configure logging
logger = logging.getLogger(__name__)

# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

# Feeds metrics
feeds_requests_total = Counter(
    'sarvanom_feeds_requests_total',
    'Total feeds requests',
    ['endpoint', 'provider', 'keyless', 'cache_hit']
)

feeds_duration_seconds = Histogram(
    'sarvanom_feeds_duration_seconds',
    'Feeds request duration',
    ['endpoint', 'provider', 'keyless', 'cache_hit']
)

feeds_items_count = Gauge(
    'sarvanom_feeds_items_count',
    'Number of feeds items returned',
    ['endpoint', 'provider', 'keyless', 'cache_hit']
)

# Create router
router = APIRouter(prefix="/api/v1", tags=["feeds"])

@router.post("/news", response_model=FeedsResponse)
async def news_endpoint(request: FeedsRequest, http_request: Request):
    """
    Fetch news from multiple providers with normalized schema.
    Uses parallel fan-out with ≤800ms timeout per provider.
    """
    start_time = time.time()
    
    try:
        # Get news adapter from app state
        news_adapter = getattr(http_request.app.state, 'news_adapter', None)
        if not news_adapter:
            raise HTTPException(status_code=503, detail="News adapter not available")
        
        # Determine providers to use
        providers_to_use = request.providers
        if not providers_to_use:
            # Use all enabled providers
            providers_to_use = list(news_adapter.providers.keys())
        
        # Fetch from news adapter with parallel fan-out
        provider_results = await news_adapter.fetch_news(
            query=request.query,
            max_items=request.max_items,
            timeout_ms=request.timeout_ms
        )
        
        # Filter results by requested providers
        filtered_results = [
            result for result in provider_results 
            if result.provider in providers_to_use
        ]
        
        # Calculate totals
        total_items = sum(len(result.items) for result in filtered_results)
        processing_time = (time.time() - start_time) * 1000
        cache_hits = sum(1 for result in filtered_results if result.cache_hit)
        keyless_fallbacks = sum(1 for result in filtered_results if result.keyless)
        
        # Emit metrics for each provider
        for result in filtered_results:
            metrics_tags = {
                'endpoint': 'news',
                'provider': result.provider,
                'keyless': str(result.keyless).lower(),
                'cache_hit': str(result.cache_hit).lower()
            }
            
            feeds_requests_total.labels(**metrics_tags).inc()
            feeds_duration_seconds.labels(**metrics_tags).observe(result.latency_ms / 1000.0)
            feeds_items_count.labels(**metrics_tags).set(len(result.items))
        
        return FeedsResponse(
            query=request.query,
            total_items=total_items,
            providers_used=[result.provider for result in filtered_results],
            provider_results=filtered_results,
            processing_time_ms=processing_time,
            cache_hits=cache_hits,
            keyless_fallbacks=keyless_fallbacks
        )
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        logger.error(f"News endpoint error: {e}")
        
        return FeedsResponse(
            query=request.query,
            total_items=0,
            providers_used=[],
            provider_results=[],
            processing_time_ms=processing_time,
            cache_hits=0,
            keyless_fallbacks=0
        )

@router.post("/markets", response_model=FeedsResponse)
async def markets_endpoint(request: FeedsRequest, http_request: Request):
    """
    Fetch markets data from multiple providers with normalized schema.
    Uses parallel fan-out with ≤800ms timeout per provider.
    """
    start_time = time.time()
    
    try:
        # Get markets adapter from app state
        markets_adapter = getattr(http_request.app.state, 'markets_adapter', None)
        if not markets_adapter:
            raise HTTPException(status_code=503, detail="Markets adapter not available")
        
        # Determine providers to use
        providers_to_use = request.providers
        if not providers_to_use:
            # Use all enabled providers
            providers_to_use = list(markets_adapter.providers.keys())
        
        # Fetch from markets adapter with parallel fan-out
        provider_results = await markets_adapter.fetch_markets(
            query=request.query,
            max_items=request.max_items,
            timeout_ms=request.timeout_ms
        )
        
        # Filter results by requested providers
        filtered_results = [
            result for result in provider_results 
            if result.provider in providers_to_use
        ]
        
        # Calculate totals
        total_items = sum(len(result.items) for result in filtered_results)
        processing_time = (time.time() - start_time) * 1000
        cache_hits = sum(1 for result in filtered_results if result.cache_hit)
        keyless_fallbacks = sum(1 for result in filtered_results if result.keyless)
        
        # Emit metrics for each provider
        for result in filtered_results:
            metrics_tags = {
                'endpoint': 'markets',
                'provider': result.provider,
                'keyless': str(result.keyless).lower(),
                'cache_hit': str(result.cache_hit).lower()
            }
            
            feeds_requests_total.labels(**metrics_tags).inc()
            feeds_duration_seconds.labels(**metrics_tags).observe(result.latency_ms / 1000.0)
            feeds_items_count.labels(**metrics_tags).set(len(result.items))
        
        return FeedsResponse(
            query=request.query,
            total_items=total_items,
            providers_used=[result.provider for result in filtered_results],
            provider_results=filtered_results,
            processing_time_ms=processing_time,
            cache_hits=cache_hits,
            keyless_fallbacks=keyless_fallbacks
        )
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        logger.error(f"Markets endpoint error: {e}")
        
        return FeedsResponse(
            query=request.query,
            total_items=0,
            providers_used=[],
            provider_results=[],
            processing_time_ms=processing_time,
            cache_hits=0,
            keyless_fallbacks=0
        )

@router.get("/feeds/providers")
async def get_feeds_providers(http_request: Request):
    """Get available feeds providers and their status"""
    providers_info = {
        "news": {},
        "markets": {}
    }
    
    # Get news providers
    news_adapter = getattr(http_request.app.state, 'news_adapter', None)
    if news_adapter:
        for provider_name, config in news_adapter.providers.items():
            providers_info["news"][provider_name] = {
                "enabled": config.get('enabled', False),
                "keyless": config.get('keyless', True),
                "has_key": bool(config.get('key')),
                "base_url": config.get('base_url', 'N/A')
            }
    
    # Get markets providers
    markets_adapter = getattr(http_request.app.state, 'markets_adapter', None)
    if markets_adapter:
        for provider_name, config in markets_adapter.providers.items():
            providers_info["markets"][provider_name] = {
                "enabled": config.get('enabled', False),
                "keyless": config.get('keyless', True),
                "has_key": bool(config.get('key')),
                "base_url": config.get('base_url', 'N/A')
            }
    
    return providers_info

@router.get("/feeds/status")
async def get_feeds_status(http_request: Request):
    """Get feeds system status"""
    status = {
        "timestamp": time.time(),
        "news_adapter_available": hasattr(http_request.app.state, 'news_adapter'),
        "markets_adapter_available": hasattr(http_request.app.state, 'markets_adapter'),
        "redis_available": hasattr(http_request.app.state, 'redis_client'),
        "providers": {
            "news": {},
            "markets": {}
        }
    }
    
    # Check news providers
    news_adapter = getattr(http_request.app.state, 'news_adapter', None)
    if news_adapter:
        for provider_name, config in news_adapter.providers.items():
            status["providers"]["news"][provider_name] = {
                "enabled": config.get('enabled', False),
                "keyless": config.get('keyless', True),
                "has_key": bool(config.get('key'))
            }
    
    # Check markets providers
    markets_adapter = getattr(http_request.app.state, 'markets_adapter', None)
    if markets_adapter:
        for provider_name, config in markets_adapter.providers.items():
            status["providers"]["markets"][provider_name] = {
                "enabled": config.get('enabled', False),
                "keyless": config.get('keyless', True),
                "has_key": bool(config.get('key'))
            }
    
    return status
