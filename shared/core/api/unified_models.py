"""
Unified API Models for MAANG Standards

Provides consistent request/response models across all endpoints
to ensure API consistency and maintainability.
"""

from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class QueryMode(str, Enum):
    """Query processing modes."""
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    ANALYTICAL = "analytical"
    RESEARCH = "research"
    FAST = "fast"


class QueryComplexity(str, Enum):
    """Query complexity levels."""
    SIMPLE = "simple"
    SIMPLE_FACTUAL = "simple_factual"
    MODERATE = "moderate"
    COMPLEX = "complex"
    COMPLEX_ANALYTICAL = "complex_analytical"
    RESEARCH_INTENSIVE = "research_intensive"
    RESEARCH_SYNTHESIS = "research_synthesis"
    MULTI_DOMAIN = "multi_domain"


class QueryCategory(str, Enum):
    """Query categories."""
    FACTUAL = "factual"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    COMPARATIVE = "comparative"
    PROCEDURAL = "procedural"
    OPINION = "opinion"
    CLARIFICATION = "clarification"
    UNKNOWN = "unknown"


class BaseQueryRequest(BaseModel):
    """Base query request model."""
    query: str = Field(..., description="The query text", min_length=1, max_length=1000)
    mode: Optional[QueryMode] = Field(QueryMode.STANDARD, description="Query processing mode")
    max_results: Optional[int] = Field(10, description="Maximum number of results", ge=1, le=100)
    user_id: Optional[str] = Field(None, description="User identifier")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")
    
    class Config:
        use_enum_values = True


class SearchRequest(BaseQueryRequest):
    """Search request model."""
    search_strategy: Optional[str] = Field("ai_enhanced_hybrid", description="Search strategy")
    include_metadata: Optional[bool] = Field(True, description="Include metadata in results")


class VectorSearchRequest(BaseQueryRequest):
    """Vector search request model."""
    similarity_threshold: Optional[float] = Field(0.7, description="Similarity threshold", ge=0.0, le=1.0)
    include_metadata: Optional[bool] = Field(True, description="Include metadata in results")
    vector_model: Optional[str] = Field("sentence-transformers/all-MiniLM-L6-v2", description="Vector model to use")


class KnowledgeGraphRequest(BaseQueryRequest):
    """Knowledge graph request model."""
    depth: Optional[int] = Field(2, description="Graph traversal depth", ge=1, le=5)
    include_relationships: Optional[bool] = Field(True, description="Include relationship data")
    topic: Optional[str] = Field(None, description="Specific topic to explore")


class LLMGenerateRequest(BaseQueryRequest):
    """LLM generation request model."""
    prompt: Optional[str] = Field(None, description="Prompt text (alternative to query)")
    max_tokens: Optional[int] = Field(1000, description="Maximum tokens to generate", ge=1, le=4000)
    temperature: Optional[float] = Field(0.7, description="Sampling temperature", ge=0.0, le=2.0)
    provider: Optional[str] = Field(None, description="Specific LLM provider to use")
    model: Optional[str] = Field(None, description="Specific model to use")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Use prompt if provided, otherwise use query
        if self.prompt is None and self.query:
            self.prompt = self.query


class ComprehensiveQueryRequest(BaseQueryRequest):
    """Comprehensive query request model."""
    include_vector_search: Optional[bool] = Field(True, description="Include vector search")
    include_knowledge_graph: Optional[bool] = Field(True, description="Include knowledge graph")
    include_llm_synthesis: Optional[bool] = Field(True, description="Include LLM synthesis")
    include_citations: Optional[bool] = Field(True, description="Include citations")
    parallel_processing: Optional[bool] = Field(True, description="Enable parallel processing")


# Response Models

class BaseResponse(BaseModel):
    """Base response model."""
    success: bool = Field(..., description="Whether the request was successful")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    trace_id: Optional[str] = Field(None, description="Request trace ID")


class ErrorResponse(BaseResponse):
    """Error response model."""
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    def __init__(self, error: str, **kwargs):
        super().__init__(success=False, error=error, **kwargs)


class SearchResult(BaseModel):
    """Individual search result."""
    id: str = Field(..., description="Result ID")
    title: str = Field(..., description="Result title")
    url: Optional[str] = Field(None, description="Result URL")
    snippet: str = Field(..., description="Result snippet")
    relevance_score: float = Field(..., description="Relevance score", ge=0.0, le=1.0)
    source_type: str = Field(..., description="Source type")
    publication_date: Optional[str] = Field(None, description="Publication date")
    author: Optional[str] = Field(None, description="Author")
    citations: Optional[int] = Field(None, description="Number of citations")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SearchResponse(BaseResponse):
    """Search response model."""
    query: str = Field(..., description="Original query")
    results: List[SearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")
    query_classification: Optional[QueryCategory] = Field(None, description="Query classification")
    complexity_score: Optional[QueryComplexity] = Field(None, description="Query complexity")
    selected_provider: Optional[str] = Field(None, description="Selected provider")
    search_strategy: Optional[str] = Field(None, description="Search strategy used")
    ai_analysis: Optional[str] = Field(None, description="AI analysis of results")
    
    class Config:
        use_enum_values = True


class VectorSearchResponse(BaseResponse):
    """Vector search response model."""
    query: str = Field(..., description="Original query")
    results: List[SearchResult] = Field(..., description="Vector search results")
    total_results: int = Field(..., description="Total number of results")
    similarity_threshold: float = Field(..., description="Similarity threshold used")
    vector_model: str = Field(..., description="Vector model used")
    embedding_time_ms: Optional[float] = Field(None, description="Embedding generation time")


class KnowledgeGraphResponse(BaseResponse):
    """Knowledge graph response model."""
    topic: str = Field(..., description="Original topic")
    entities: List[Dict[str, Any]] = Field(..., description="Graph entities")
    relationships: List[Dict[str, Any]] = Field(..., description="Graph relationships")
    depth: int = Field(..., description="Traversal depth")
    total_entities: int = Field(..., description="Total number of entities")
    total_relationships: int = Field(..., description="Total number of relationships")


class LLMGenerateResponse(BaseResponse):
    """LLM generation response model."""
    prompt: str = Field(..., description="Original prompt")
    response: str = Field(..., description="Generated response")
    provider: str = Field(..., description="LLM provider used")
    model: str = Field(..., description="Model used")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    finish_reason: Optional[str] = Field(None, description="Reason for completion")


class ComprehensiveQueryResponse(BaseResponse):
    """Comprehensive query response model."""
    query: str = Field(..., description="Original query")
    mode: str = Field(..., description="Query mode used")
    final_answer: Optional[str] = Field(None, description="Final synthesized answer")
    partial_results: Optional[Dict[str, Any]] = Field(None, description="Partial results from each lane")
    lane_results: Dict[str, Any] = Field(..., description="Results from each processing lane")
    summary: Dict[str, int] = Field(..., description="Summary of lane results")
    sla_compliance: Optional[Dict[str, Any]] = Field(None, description="SLA compliance metrics")
    gates_status: Optional[Dict[str, str]] = Field(None, description="Gate status")
    production_ready: bool = Field(False, description="Whether response is production ready")
    api_keys_used: bool = Field(False, description="Whether API keys were used")


class HealthStatus(BaseModel):
    """Health status model."""
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")
    uptime_s: Optional[float] = Field(None, description="Service uptime in seconds")
    version: Optional[str] = Field(None, description="Service version")
    services: Optional[Dict[str, Any]] = Field(None, description="Individual service status")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Service metrics")
    recommendations: Optional[List[str]] = Field(None, description="Health recommendations")


class AuthRequest(BaseModel):
    """Authentication request model."""
    username: str = Field(..., description="Username", min_length=3, max_length=50)
    password: str = Field(..., description="Password", min_length=8, max_length=100)


class AuthResponse(BaseResponse):
    """Authentication response model."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user: Dict[str, Any] = Field(..., description="User information")
    
    def __init__(self, access_token: str, expires_in: int, user: Dict[str, Any], **kwargs):
        super().__init__(success=True, access_token=access_token, expires_in=expires_in, user=user, **kwargs)
