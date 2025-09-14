"""
Feeds Models - SarvanOM v2 Model Registry

Pydantic models for normalized news and markets data schemas.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime

class SourceInfo(BaseModel):
    """Source information for news items"""
    name: str = Field(..., description="Source name")
    domain: str = Field(..., description="Source domain")
    authority_score: float = Field(..., description="Authority score (0.0-1.0)")

class SentimentInfo(BaseModel):
    """Sentiment analysis for news items"""
    score: float = Field(..., description="Sentiment score (-1.0 to 1.0)")
    label: str = Field(..., description="Sentiment label (positive/negative/neutral)")

class NewsMetadata(BaseModel):
    """Metadata for news items"""
    provider: str = Field(..., description="Provider name")
    provider_id: str = Field(..., description="Provider-specific ID")
    ingested_at: datetime = Field(..., description="Ingestion timestamp")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")

class NormalizedNewsItem(BaseModel):
    """Normalized news item schema"""
    id: str = Field(..., description="Unique item ID")
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Article content")
    excerpt: str = Field(..., description="Article excerpt")
    url: str = Field(..., description="Article URL")
    source: SourceInfo = Field(..., description="Source information")
    author: Optional[str] = Field(None, description="Author name")
    published_at: datetime = Field(..., description="Publication timestamp")
    language: str = Field("en", description="Language code")
    category: str = Field(..., description="Article category")
    tags: List[str] = Field(default_factory=list, description="Article tags")
    sentiment: Optional[SentimentInfo] = Field(None, description="Sentiment analysis")
    metadata: NewsMetadata = Field(..., description="Item metadata")

class PriceInfo(BaseModel):
    """Price information for market items"""
    current: float = Field(..., description="Current price")
    open: float = Field(..., description="Opening price")
    high: float = Field(..., description="High price")
    low: float = Field(..., description="Low price")
    previous_close: float = Field(..., description="Previous close price")

class ChangeInfo(BaseModel):
    """Change information for market items"""
    absolute: float = Field(..., description="Absolute change")
    percentage: float = Field(..., description="Percentage change")

class MarketsMetadata(BaseModel):
    """Metadata for market items"""
    provider: str = Field(..., description="Provider name")
    provider_id: str = Field(..., description="Provider-specific ID")
    ingested_at: datetime = Field(..., description="Ingestion timestamp")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")

class NormalizedMarketsItem(BaseModel):
    """Normalized markets item schema"""
    id: str = Field(..., description="Unique item ID")
    symbol: str = Field(..., description="Symbol/ticker")
    name: str = Field(..., description="Company/asset name")
    type: str = Field(..., description="Asset type (stock, crypto, etc.)")
    price: PriceInfo = Field(..., description="Price information")
    change: ChangeInfo = Field(..., description="Change information")
    volume: int = Field(..., description="Trading volume")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    currency: str = Field("USD", description="Currency code")
    exchange: str = Field(..., description="Exchange name")
    sector: Optional[str] = Field(None, description="Sector")
    industry: Optional[str] = Field(None, description="Industry")
    timestamp: datetime = Field(..., description="Data timestamp")
    metadata: MarketsMetadata = Field(..., description="Item metadata")

class ProviderResult(BaseModel):
    """Result from a single provider"""
    provider: str = Field(..., description="Provider name")
    status: str = Field(..., description="Status (success, error, timeout)")
    items: List[Union[NormalizedNewsItem, NormalizedMarketsItem]] = Field(default_factory=list, description="Items from provider")
    latency_ms: float = Field(..., description="Response latency in milliseconds")
    error: Optional[str] = Field(None, description="Error message if failed")
    rate_limit_remaining: Optional[int] = Field(None, description="Remaining rate limit")
    cache_hit: bool = Field(False, description="Whether result was from cache")
    keyless: bool = Field(False, description="Whether keyless fallback was used")

class FeedsResponse(BaseModel):
    """Response from feeds endpoints"""
    query: str = Field(..., description="Original query")
    total_items: int = Field(..., description="Total number of items")
    providers_used: List[str] = Field(..., description="Providers that were queried")
    provider_results: List[ProviderResult] = Field(..., description="Results from each provider")
    processing_time_ms: float = Field(..., description="Total processing time")
    cache_hits: int = Field(0, description="Number of cache hits")
    keyless_fallbacks: int = Field(0, description="Number of keyless fallbacks used")

class FeedsRequest(BaseModel):
    """Request for feeds endpoints"""
    query: str = Field(..., description="Search query")
    max_items: int = Field(50, description="Maximum items to return")
    providers: Optional[List[str]] = Field(None, description="Specific providers to use")
    use_cache: bool = Field(True, description="Whether to use cache")
    timeout_ms: int = Field(800, description="Timeout per provider in milliseconds")
