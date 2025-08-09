from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, conint, confloat


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[str] = None
    max_tokens: conint(ge=1, le=20000) = 1000
    confidence_threshold: confloat(ge=0.0, le=1.0) = 0.8


class RetrievalSearchRequest(BaseModel):
    query: str
    classification: Dict[str, Any] = Field(default_factory=dict)
    max_results: conint(ge=1, le=100) = 10
    context: Dict[str, Any] = Field(default_factory=dict)


class RetrievalSearchResponse(BaseModel):
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    method: str = ""
    total_results: int = 0
    relevance_scores: List[float] = Field(default_factory=list)
    limit: int = 10


class SynthesisRequest(BaseModel):
    query: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    verification: Dict[str, Any] = Field(default_factory=dict)
    max_tokens: conint(ge=1, le=20000) = 2000
    context: Dict[str, Any] = Field(default_factory=dict)


class SynthesisResponse(BaseModel):
    answer: str
    method: str = ""
    tokens: int = 0


class RetrievalIndexRequest(BaseModel):
    ids: List[str]
    texts: List[str]
    metadatas: List[Dict[str, Any]] = Field(default_factory=list)

    def validate_lengths(self) -> None:
        if not (
            len(self.ids) == len(self.texts)
            and (not self.metadatas or len(self.metadatas) == len(self.texts))
        ):
            raise ValueError(
                "ids, texts, and metadatas (if provided) must have equal length"
            )


class RetrievalIndexResponse(BaseModel):
    upserted: int
