"""
Model Registry Router - SarvanOM v2

Router for model registry endpoints including models and providers.
"""

from typing import Dict, List, Optional, Any
from dataclasses import asdict
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

# Import models from models file
from .models import ModelResponse, ProviderResponse

# Create router
router = APIRouter(prefix="/api/v1", tags=["model-registry"])

@router.get("/models", response_model=List[ModelResponse])
async def get_models(request: Request):
    """Get all models"""
    return [ModelResponse(**asdict(model)) for model in request.app.state.model_registry.models.values()]

@router.get("/models/{model_id}", response_model=ModelResponse)
async def get_model(model_id: str, request: Request):
    """Get specific model"""
    model = request.app.state.model_registry.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return ModelResponse(**asdict(model))

@router.get("/models/capability/{capability}", response_model=List[ModelResponse])
async def get_models_by_capability(capability: str, request: Request):
    """Get models by capability"""
    models = request.app.state.model_registry.get_models_by_capability(capability)
    return [ModelResponse(**asdict(model)) for model in models]

@router.get("/models/provider/{provider}", response_model=List[ModelResponse])
async def get_models_by_provider(provider: str, request: Request):
    """Get models by provider"""
    models = request.app.state.model_registry.get_models_by_provider(provider)
    return [ModelResponse(**asdict(model)) for model in models]

@router.get("/models/stable", response_model=List[ModelResponse])
async def get_stable_models(request: Request):
    """Get all stable models"""
    models = request.app.state.model_registry.get_stable_models()
    return [ModelResponse(**asdict(model)) for model in models]

@router.get("/models/refiners", response_model=List[ModelResponse])
async def get_refiner_models(request: Request):
    """Get models suitable for refinement"""
    models = request.app.state.model_registry.get_refiner_models()
    return [ModelResponse(**asdict(model)) for model in models]

@router.get("/providers", response_model=List[ProviderResponse])
async def get_providers(request: Request):
    """Get all providers"""
    return [ProviderResponse(**asdict(provider)) for provider in request.app.state.model_registry.providers.values()]

@router.get("/providers/{provider_id}", response_model=ProviderResponse)
async def get_provider(provider_id: str, request: Request):
    """Get specific provider"""
    provider = request.app.state.model_registry.providers.get(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return ProviderResponse(**asdict(provider))

@router.post("/models/{model_id}/usage")
async def record_model_usage(
    model_id: str,
    query_type: str,
    response_time: float,
    cost_usd: float,
    request: Request
):
    """Record model usage"""
    request.app.state.model_registry.record_model_usage(model_id, query_type, response_time, cost_usd)
    return {"status": "recorded"}
