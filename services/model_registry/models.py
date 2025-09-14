"""
Model Registry Pydantic Models - SarvanOM v2

Pydantic models for API responses.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class ModelResponse(BaseModel):
    model_id: str
    provider: str
    model_family: str
    version: str
    status: str
    capabilities: Dict[str, bool]
    performance: Dict[str, Any]
    costs: Dict[str, Any]
    limits: Dict[str, Any]
    health: Dict[str, Any]
    metadata: Dict[str, Any]

class ProviderResponse(BaseModel):
    provider_id: str
    name: str
    status: str
    api_base_url: str
    authentication: Dict[str, Any]
    health: Dict[str, Any]
    quotas: Dict[str, int]
    models: List[str]
