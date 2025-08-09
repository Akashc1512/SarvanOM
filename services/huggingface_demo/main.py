"""
Hugging Face Enhanced Demo Service - SarvanOM

This service demonstrates the enhanced Hugging Face integration capabilities
including model discovery, intelligent model selection, and multi-task support.

Features:
- Model discovery and search
- Intelligent model selection based on task
- Multi-language support
- Dataset integration
- Space discovery
- Free tier optimization

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

from __future__ import annotations

import time
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, Response, HTTPException
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from shared.core.config import get_central_config
from shared.core.logging import get_logger
from shared.core.huggingface_enhanced import (
    HuggingFaceEnhancedClient,
    HFModelType,
    HFModelCategory,
    HFRequest,
    HFResponse,
    HFModelInfo,
    HFDatasetInfo,
    HFSpaceInfo,
)
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


# Load .env before reading central config, so HF tokens are present
load_dotenv()
config = get_central_config()

app = FastAPI(
    title=f"{config.service_name}-huggingface-demo",
    version=config.app_version,
    description="Enhanced Hugging Face Integration Demo Service",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=bool(config.cors_credentials),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics
REQUEST_COUNTER = Counter("hf_demo_requests_total", "Total HF demo requests")
REQUEST_LATENCY = Histogram(
    "hf_demo_request_latency_seconds", "HF demo request latency"
)


# Pydantic models
class ModelSearchRequest(BaseModel):
    query: str
    model_type: Optional[str] = None
    category: Optional[str] = None
    language: Optional[str] = None
    limit: int = 10


class TextGenerationRequest(BaseModel):
    prompt: str
    task: Optional[str] = "text-generation"
    max_length: Optional[int] = 100
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9


class DatasetSearchRequest(BaseModel):
    query: str
    language: Optional[str] = None
    limit: int = 10


class SpaceSearchRequest(BaseModel):
    query: str
    sdk: Optional[str] = None
    hardware: Optional[str] = None
    limit: int = 10


class ModelRecommendationRequest(BaseModel):
    task: str
    category: Optional[str] = None
    language: str = "en"
    limit: int = 5


# Health check
@app.get("/health")
async def health() -> dict:
    return {
        "service": "huggingface-demo",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "model_discovery",
            "intelligent_model_selection",
            "dataset_search",
            "space_discovery",
            "multi_task_support",
        ],
    }


@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
async def root() -> dict:
    return {
        "service": "huggingface-demo",
        "version": config.app_version,
        "status": "ok",
        "description": "Enhanced Hugging Face Integration Demo",
    }


@app.post("/search/models")
async def search_models(request: ModelSearchRequest) -> Dict[str, Any]:
    """Search for Hugging Face models."""
    REQUEST_COUNTER.inc()

    with REQUEST_LATENCY.time():
        try:
            # Get Hugging Face API key
            api_key = (
                config.huggingface_write_token
                or config.huggingface_read_token
                or config.huggingface_api_key
            )
            if not api_key:
                raise HTTPException(
                    status_code=500, detail="Hugging Face API key not configured"
                )

            async with HuggingFaceEnhancedClient(api_key.get_secret_value()) as client:
                model_type = (
                    HFModelType(request.model_type) if request.model_type else None
                )
                category = (
                    HFModelCategory(request.category) if request.category else None
                )

                models = await client.search_models(
                    query=request.query,
                    model_type=model_type,
                    category=category,
                    language=request.language,
                    limit=request.limit,
                )

                return {
                    "models": [
                        {
                            "model_id": model.model_id,
                            "name": model.name,
                            "description": model.description,
                            "model_type": model.model_type.value,
                            "category": model.category.value,
                            "language": model.language,
                            "downloads": model.downloads,
                            "likes": model.likes,
                            "free_tier_compatible": model.free_tier_compatible,
                        }
                        for model in models
                    ],
                    "total_found": len(models),
                    "query": request.query,
                }

        except Exception as e:
            logger.error(f"Error searching models: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error searching models: {str(e)}"
            )


@app.post("/generate/text")
async def generate_text(request: TextGenerationRequest) -> Dict[str, Any]:
    """Generate text using intelligent model selection."""
    REQUEST_COUNTER.inc()

    with REQUEST_LATENCY.time():
        try:
            # Get Hugging Face API key
            api_key = (
                config.huggingface_write_token
                or config.huggingface_read_token
                or config.huggingface_api_key
            )
            if not api_key:
                raise HTTPException(
                    status_code=500, detail="Hugging Face API key not configured"
                )

            async with HuggingFaceEnhancedClient(api_key.get_secret_value()) as client:
                # Create HF request
                hf_request = HFRequest(
                    model_id="",  # Will be selected intelligently
                    inputs=request.prompt,
                    task=HFModelType(request.task),
                    max_length=request.max_length,
                    temperature=request.temperature,
                    top_p=request.top_p,
                )

                # Generate text
                response = await client.generate_text(hf_request)

                return {
                    "generated_text": response.outputs,
                    "model_used": response.model_id,
                    "task": response.task.value,
                    "response_time_ms": response.response_time_ms,
                    "metadata": response.metadata,
                }

        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error generating text: {str(e)}"
            )


@app.post("/search/datasets")
async def search_datasets(request: DatasetSearchRequest) -> Dict[str, Any]:
    """Search for Hugging Face datasets."""
    REQUEST_COUNTER.inc()

    with REQUEST_LATENCY.time():
        try:
            # Get Hugging Face API key
            api_key = (
                config.huggingface_write_token
                or config.huggingface_read_token
                or config.huggingface_api_key
            )
            if not api_key:
                raise HTTPException(
                    status_code=500, detail="Hugging Face API key not configured"
                )

            async with HuggingFaceEnhancedClient(api_key.get_secret_value()) as client:
                datasets = await client.search_datasets(
                    query=request.query, language=request.language, limit=request.limit
                )

                return {
                    "datasets": [
                        {
                            "dataset_id": dataset.dataset_id,
                            "name": dataset.name,
                            "description": dataset.description,
                            "language": dataset.language,
                            "downloads": dataset.downloads,
                            "likes": dataset.likes,
                            "size": dataset.size,
                            "num_rows": dataset.num_rows,
                            "num_columns": dataset.num_columns,
                            "free_tier_compatible": dataset.free_tier_compatible,
                        }
                        for dataset in datasets
                    ],
                    "total_found": len(datasets),
                    "query": request.query,
                }

        except Exception as e:
            logger.error(f"Error searching datasets: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error searching datasets: {str(e)}"
            )


@app.post("/search/spaces")
async def search_spaces(request: SpaceSearchRequest) -> Dict[str, Any]:
    """Search for Hugging Face spaces."""
    REQUEST_COUNTER.inc()

    with REQUEST_LATENCY.time():
        try:
            # Get Hugging Face API key
            api_key = (
                config.huggingface_write_token
                or config.huggingface_read_token
                or config.huggingface_api_key
            )
            if not api_key:
                raise HTTPException(
                    status_code=500, detail="Hugging Face API key not configured"
                )

            async with HuggingFaceEnhancedClient(api_key.get_secret_value()) as client:
                spaces = await client.search_spaces(
                    query=request.query,
                    sdk=request.sdk,
                    hardware=request.hardware,
                    limit=request.limit,
                )

                return {
                    "spaces": [
                        {
                            "space_id": space.space_id,
                            "name": space.name,
                            "description": space.description,
                            "sdk": space.sdk,
                            "hardware": space.hardware,
                            "likes": space.likes,
                            "status": space.status,
                            "free_tier_compatible": space.free_tier_compatible,
                        }
                        for space in spaces
                    ],
                    "total_found": len(spaces),
                    "query": request.query,
                }

        except Exception as e:
            logger.error(f"Error searching spaces: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error searching spaces: {str(e)}"
            )


@app.post("/recommend/models")
async def recommend_models(request: ModelRecommendationRequest) -> Dict[str, Any]:
    """Get recommended models for a specific task."""
    REQUEST_COUNTER.inc()

    with REQUEST_LATENCY.time():
        try:
            # Get Hugging Face API key
            api_key = (
                config.huggingface_write_token
                or config.huggingface_read_token
                or config.huggingface_api_key
            )
            if not api_key:
                raise HTTPException(
                    status_code=500, detail="Hugging Face API key not configured"
                )

            async with HuggingFaceEnhancedClient(api_key.get_secret_value()) as client:
                model_type = HFModelType(request.task)
                category = (
                    HFModelCategory(request.category) if request.category else None
                )

                models = await client.get_recommended_models(
                    task=model_type,
                    category=category,
                    language=request.language,
                    limit=request.limit,
                )

                return {
                    "recommended_models": [
                        {
                            "model_id": model.model_id,
                            "name": model.name,
                            "description": model.description,
                            "model_type": model.model_type.value,
                            "category": model.category.value,
                            "language": model.language,
                            "free_tier_compatible": model.free_tier_compatible,
                        }
                        for model in models
                    ],
                    "task": request.task,
                    "category": request.category,
                    "language": request.language,
                    "total_recommendations": len(models),
                }

        except Exception as e:
            logger.error(f"Error getting model recommendations: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error getting model recommendations: {str(e)}"
            )


@app.get("/capabilities")
async def get_capabilities() -> Dict[str, Any]:
    """Get the capabilities of the enhanced Hugging Face integration."""
    return {
        "enhanced_features": {
            "model_discovery": {
                "description": "Search and discover models from Hugging Face Hub",
                "endpoint": "/search/models",
                "supported_filters": ["model_type", "category", "language"],
            },
            "intelligent_model_selection": {
                "description": "Automatically select the best model for the task",
                "endpoint": "/generate/text",
                "supported_tasks": [
                    "text-generation",
                    "translation",
                    "summarization",
                    "question-answering",
                    "text-classification",
                    "code-generation",
                ],
            },
            "dataset_integration": {
                "description": "Search and discover datasets from Hugging Face Hub",
                "endpoint": "/search/datasets",
                "supported_filters": ["language"],
            },
            "space_discovery": {
                "description": "Search and discover AI applications from Hugging Face Spaces",
                "endpoint": "/search/spaces",
                "supported_filters": ["sdk", "hardware"],
            },
            "model_recommendations": {
                "description": "Get recommended models for specific tasks",
                "endpoint": "/recommend/models",
                "supported_tasks": [
                    "text-generation",
                    "translation",
                    "summarization",
                    "question-answering",
                    "text-classification",
                ],
            },
        },
        "free_tier_advantages": {
            "requests_per_month": 30000,
            "models_available": "500,000+",
            "datasets_available": "100,000+",
            "spaces_available": "50,000+",
            "languages_supported": "100+",
            "cost": "Free",
        },
        "supported_model_types": [
            "text-generation",
            "translation",
            "summarization",
            "question-answering",
            "text-classification",
            "code-generation",
            "sentiment-analysis",
            "named-entity-recognition",
            "fill-mask",
            "zero-shot-classification",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8006)
