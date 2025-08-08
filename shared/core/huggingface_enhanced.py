"""
Enhanced Hugging Face Integration - SarvanOM

This module provides comprehensive integration with the Hugging Face ecosystem,
including models, datasets, spaces, and tools. It's designed to maximize the
advantages of Hugging Face's free tier and extensive model library.

Key Features:
- **Model Hub Integration**: Access to 500,000+ models
- **Dataset Integration**: Access to 100,000+ datasets
- **Spaces Integration**: Access to 50,000+ AI applications
- **Free Tier Optimization**: Maximize free API usage
- **Model Routing**: Smart model selection based on task
- **Embedding Models**: Access to state-of-the-art embeddings
- **Dataset Search**: Semantic search across datasets
- **Space Discovery**: Find relevant AI applications

Advantages:
- **Zero Cost**: Free API access with generous limits
- **Latest Models**: Access to cutting-edge research models
- **Diverse Tasks**: Text generation, translation, summarization, etc.
- **Community Driven**: Models from top AI researchers
- **Multi-language**: Support for 100+ languages
- **Specialized Models**: Domain-specific models for various tasks

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import asyncio
import aiohttp
import json
import time
import hashlib
import logging
from typing import Dict, Any, List, Optional, Union, AsyncGenerator, Tuple
from dataclasses import dataclass, field
from enum import Enum
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from shared.core.logging import get_logger
from shared.core.metrics import get_metrics_service

logger = get_logger(__name__)
metrics_service = get_metrics_service()


class HFModelType(str, Enum):
    """Hugging Face model types."""
    
    TEXT_GENERATION = "text-generation"
    TEXT_CLASSIFICATION = "text-classification"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question-answering"
    FILL_MASK = "fill-mask"
    TOKEN_CLASSIFICATION = "token-classification"
    ZERO_SHOT_CLASSIFICATION = "zero-shot-classification"
    SENTIMENT_ANALYSIS = "sentiment-analysis"
    NAMED_ENTITY_RECOGNITION = "ner"
    TEXT2TEXT_GENERATION = "text2text-generation"
    CONVERSATIONAL = "conversational"
    IMAGE_CLASSIFICATION = "image-classification"
    IMAGE_SEGMENTATION = "image-segmentation"
    OBJECT_DETECTION = "object-detection"
    AUDIO_CLASSIFICATION = "audio-classification"
    AUTOMATIC_SPEECH_RECOGNITION = "automatic-speech-recognition"
    TEXT_TO_SPEECH = "text-to-speech"


class HFModelCategory(str, Enum):
    """Hugging Face model categories."""
    
    # Text Generation
    CHATBOT = "chatbot"
    STORY_WRITING = "story-writing"
    CODE_GENERATION = "code-generation"
    CREATIVE_WRITING = "creative-writing"
    TECHNICAL_WRITING = "technical-writing"
    
    # Translation
    MULTILINGUAL = "multilingual"
    ENGLISH_TO_OTHER = "english-to-other"
    OTHER_TO_ENGLISH = "other-to-english"
    
    # Summarization
    NEWS_SUMMARIZATION = "news-summarization"
    DOCUMENT_SUMMARIZATION = "document-summarization"
    CONVERSATION_SUMMARIZATION = "conversation-summarization"
    
    # Question Answering
    READING_COMPREHENSION = "reading-comprehension"
    OPEN_DOMAIN_QA = "open-domain-qa"
    CLOSED_DOMAIN_QA = "closed-domain-qa"
    
    # Classification
    SENTIMENT_ANALYSIS = "sentiment-analysis"
    TOPIC_CLASSIFICATION = "topic-classification"
    INTENT_CLASSIFICATION = "intent-classification"
    EMOTION_CLASSIFICATION = "emotion-classification"
    
    # Specialized
    MEDICAL = "medical"
    LEGAL = "legal"
    FINANCIAL = "financial"
    SCIENTIFIC = "scientific"
    EDUCATIONAL = "educational"


@dataclass
class HFModelInfo:
    """Hugging Face model information."""
    
    model_id: str
    name: str
    description: str
    model_type: HFModelType
    category: HFModelCategory
    language: str = "en"
    license: str = "unknown"
    downloads: int = 0
    likes: int = 0
    tags: List[str] = field(default_factory=list)
    author: str = ""
    last_modified: str = ""
    size: Optional[int] = None
    parameters: Optional[int] = None
    
    # Performance metrics
    accuracy: Optional[float] = None
    latency_ms: Optional[float] = None
    throughput: Optional[float] = None
    
    # Usage info
    free_tier_compatible: bool = True
    api_endpoint: Optional[str] = None
    rate_limit: Optional[int] = None


@dataclass
class HFDatasetInfo:
    """Hugging Face dataset information."""
    
    dataset_id: str
    name: str
    description: str
    language: str = "en"
    license: str = "unknown"
    downloads: int = 0
    likes: int = 0
    tags: List[str] = field(default_factory=list)
    author: str = ""
    last_modified: str = ""
    size: Optional[int] = None
    num_rows: Optional[int] = None
    num_columns: Optional[int] = None
    
    # Dataset structure
    features: Dict[str, Any] = field(default_factory=dict)
    splits: Dict[str, int] = field(default_factory=dict)
    
    # Usage info
    free_tier_compatible: bool = True
    download_url: Optional[str] = None


@dataclass
class HFSpaceInfo:
    """Hugging Face space information."""
    
    space_id: str
    name: str
    description: str
    sdk: str = "gradio"  # gradio, streamlit, docker, etc.
    license: str = "unknown"
    likes: int = 0
    tags: List[str] = field(default_factory=list)
    author: str = ""
    last_modified: str = ""
    
    # Space details
    hardware: str = "cpu"  # cpu, gpu, t4, a10g, etc.
    visibility: str = "public"  # public, private
    status: str = "running"  # running, building, error
    
    # Usage info
    free_tier_compatible: bool = True
    space_url: Optional[str] = None


@dataclass
class HFRequest:
    """Hugging Face API request."""
    
    model_id: str
    inputs: Union[str, List[str], Dict[str, Any]]
    parameters: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None
    use_cache: bool = True
    wait_for_model: bool = False
    
    # Task-specific parameters
    task: Optional[HFModelType] = None
    max_length: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    do_sample: bool = True
    num_return_sequences: int = 1


@dataclass
class HFResponse:
    """Hugging Face API response."""
    
    outputs: Union[str, List[str], Dict[str, Any]]
    model_id: str
    task: HFModelType
    response_time_ms: float
    token_usage: Optional[Dict[str, int]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class HuggingFaceEnhancedClient:
    """Enhanced Hugging Face client with comprehensive features."""
    
    def __init__(self, api_key: str, base_url: str = "https://api-inference.huggingface.co"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=aiohttp.ClientTimeout(total=60)
        )
        
        # Cache for model info
        self._model_cache: Dict[str, HFModelInfo] = {}
        self._dataset_cache: Dict[str, HFDatasetInfo] = {}
        self._space_cache: Dict[str, HFSpaceInfo] = {}
        
        # Rate limiting
        self._request_count = 0
        self._last_reset = time.time()
        self._rate_limit = 30000  # Free tier: 30k requests/month
        
        logger.info("Enhanced Hugging Face client initialized")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def _make_request(self, endpoint: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
        """Make a request to Hugging Face API with retry logic."""
        url = f"{self.base_url}{endpoint}"
        
        async with self.session.request(method, url, **kwargs) as response:
            if response.status == 503:
                # Model is loading
                raise aiohttp.ClientError("Model is loading, please retry")
            elif response.status != 200:
                error_text = await response.text()
                raise aiohttp.ClientError(f"API error {response.status}: {error_text}")
            
            return await response.json()
    
    async def generate_text(self, request: HFRequest) -> HFResponse:
        """Generate text using Hugging Face models."""
        start_time = time.time()
        
        # Prepare payload
        payload = {
            "inputs": request.inputs,
            "parameters": request.parameters or {},
            "options": request.options or {},
            "use_cache": request.use_cache,
            "wait_for_model": request.wait_for_model
        }
        
        # Add task-specific parameters
        if request.max_length:
            payload["parameters"]["max_length"] = request.max_length
        if request.temperature:
            payload["parameters"]["temperature"] = request.temperature
        if request.top_p:
            payload["parameters"]["top_p"] = request.top_p
        if request.do_sample:
            payload["parameters"]["do_sample"] = request.do_sample
        if request.num_return_sequences:
            payload["parameters"]["num_return_sequences"] = request.num_return_sequences
        
        # Make request
        result = await self._make_request(
            f"/models/{request.model_id}",
            method="POST",
            json=payload
        )
        
        response_time = (time.time() - start_time) * 1000
        
        return HFResponse(
            outputs=result,
            model_id=request.model_id,
            task=request.task or HFModelType.TEXT_GENERATION,
            response_time_ms=response_time,
            metadata={"huggingface_response": result}
        )
    
    async def search_models(
        self,
        query: str,
        model_type: Optional[HFModelType] = None,
        category: Optional[HFModelCategory] = None,
        language: Optional[str] = None,
        limit: int = 20
    ) -> List[HFModelInfo]:
        """Search for models on Hugging Face Hub."""
        try:
            # Use Hugging Face Hub API to search models
            search_params = {
                "search": query,
                "limit": limit,
                "full": True
            }
            
            if model_type:
                search_params["filter"] = f"task:{model_type.value}"
            
            result = await self._make_request("/models", params=search_params)
            
            models = []
            for model_data in result.get("models", []):
                model_info = HFModelInfo(
                    model_id=model_data.get("id", ""),
                    name=model_data.get("name", ""),
                    description=model_data.get("description", ""),
                    model_type=HFModelType(model_data.get("pipeline_tag", "text-generation")),
                    category=self._infer_category(model_data),
                    language=model_data.get("language", "en"),
                    license=model_data.get("license", "unknown"),
                    downloads=model_data.get("downloads", 0),
                    likes=model_data.get("likes", 0),
                    tags=model_data.get("tags", []),
                    author=model_data.get("author", {}).get("name", ""),
                    last_modified=model_data.get("lastModified", ""),
                    size=model_data.get("model-index", [{}])[0].get("results", [{}])[0].get("metrics", {}).get("model_size", {}).get("value"),
                    parameters=model_data.get("model-index", [{}])[0].get("results", [{}])[0].get("metrics", {}).get("parameters", {}).get("value"),
                    free_tier_compatible=True  # Most models are free tier compatible
                )
                models.append(model_info)
            
            return models
            
        except Exception as e:
            logger.error(f"Error searching models: {e}")
            return []
    
    async def search_datasets(
        self,
        query: str,
        language: Optional[str] = None,
        limit: int = 20
    ) -> List[HFDatasetInfo]:
        """Search for datasets on Hugging Face Hub."""
        try:
            search_params = {
                "search": query,
                "limit": limit,
                "full": True
            }
            
            if language:
                search_params["filter"] = f"language:{language}"
            
            result = await self._make_request("/datasets", params=search_params)
            
            datasets = []
            for dataset_data in result.get("datasets", []):
                dataset_info = HFDatasetInfo(
                    dataset_id=dataset_data.get("id", ""),
                    name=dataset_data.get("name", ""),
                    description=dataset_data.get("description", ""),
                    language=dataset_data.get("language", "en"),
                    license=dataset_data.get("license", "unknown"),
                    downloads=dataset_data.get("downloads", 0),
                    likes=dataset_data.get("likes", 0),
                    tags=dataset_data.get("tags", []),
                    author=dataset_data.get("author", {}).get("name", ""),
                    last_modified=dataset_data.get("lastModified", ""),
                    size=dataset_data.get("size", 0),
                    num_rows=dataset_data.get("num_rows", 0),
                    num_columns=dataset_data.get("num_columns", 0),
                    features=dataset_data.get("features", {}),
                    splits=dataset_data.get("splits", {}),
                    free_tier_compatible=True
                )
                datasets.append(dataset_info)
            
            return datasets
            
        except Exception as e:
            logger.error(f"Error searching datasets: {e}")
            return []
    
    async def search_spaces(
        self,
        query: str,
        sdk: Optional[str] = None,
        hardware: Optional[str] = None,
        limit: int = 20
    ) -> List[HFSpaceInfo]:
        """Search for spaces on Hugging Face Hub."""
        try:
            search_params = {
                "search": query,
                "limit": limit,
                "full": True
            }
            
            if sdk:
                search_params["filter"] = f"sdk:{sdk}"
            if hardware:
                search_params["filter"] = f"hardware:{hardware}"
            
            result = await self._make_request("/spaces", params=search_params)
            
            spaces = []
            for space_data in result.get("spaces", []):
                space_info = HFSpaceInfo(
                    space_id=space_data.get("id", ""),
                    name=space_data.get("name", ""),
                    description=space_data.get("description", ""),
                    sdk=space_data.get("sdk", "gradio"),
                    license=space_data.get("license", "unknown"),
                    likes=space_data.get("likes", 0),
                    tags=space_data.get("tags", []),
                    author=space_data.get("author", {}).get("name", ""),
                    last_modified=space_data.get("lastModified", ""),
                    hardware=space_data.get("hardware", "cpu"),
                    visibility=space_data.get("visibility", "public"),
                    status=space_data.get("status", "running"),
                    free_tier_compatible=True
                )
                spaces.append(space_info)
            
            return spaces
            
        except Exception as e:
            logger.error(f"Error searching spaces: {e}")
            return []
    
    async def get_recommended_models(
        self,
        task: HFModelType,
        category: Optional[HFModelCategory] = None,
        language: str = "en",
        limit: int = 10
    ) -> List[HFModelInfo]:
        """Get recommended models for a specific task."""
        
        # Pre-defined recommendations based on task and category
        recommendations = {
            HFModelType.TEXT_GENERATION: {
                HFModelCategory.CHATBOT: [
                    "microsoft/DialoGPT-medium",
                    "microsoft/DialoGPT-large",
                    "facebook/blenderbot-400M-distill",
                    "EleutherAI/gpt-neo-125M",
                    "microsoft/DialoGPT-small"
                ],
                HFModelCategory.STORY_WRITING: [
                    "gpt2",
                    "EleutherAI/gpt-neo-125M",
                    "microsoft/DialoGPT-medium",
                    "distilgpt2"
                ],
                HFModelCategory.CODE_GENERATION: [
                    "Salesforce/codegen-350M-mono",
                    "Salesforce/codegen-2B-mono",
                    "microsoft/DialoGPT-medium"
                ]
            },
            HFModelType.TRANSLATION: {
                HFModelCategory.MULTILINGUAL: [
                    "Helsinki-NLP/opus-mt-en-es",
                    "Helsinki-NLP/opus-mt-en-fr",
                    "Helsinki-NLP/opus-mt-en-de",
                    "Helsinki-NLP/opus-mt-en-it"
                ]
            },
            HFModelType.SUMMARIZATION: {
                HFModelCategory.NEWS_SUMMARIZATION: [
                    "facebook/bart-large-cnn",
                    "google/pegasus-large",
                    "microsoft/DialoGPT-medium"
                ]
            },
            HFModelType.QUESTION_ANSWERING: {
                HFModelCategory.READING_COMPREHENSION: [
                    "deepset/roberta-base-squad2",
                    "distilbert-base-cased-distilled-squad",
                    "microsoft/DialoGPT-medium"
                ]
            },
            HFModelType.TEXT_CLASSIFICATION: {
                HFModelCategory.SENTIMENT_ANALYSIS: [
                    "cardiffnlp/twitter-roberta-base-sentiment",
                    "distilbert-base-uncased-finetuned-sst-2-english",
                    "microsoft/DialoGPT-medium"
                ]
            }
        }
        
        # Get recommendations for the task
        task_recommendations = recommendations.get(task, {})
        category_recommendations = task_recommendations.get(category, [])
        
        # If no specific category recommendations, use general task recommendations
        if not category_recommendations:
            category_recommendations = task_recommendations.get(None, [])
        
        # If still no recommendations, use fallback models
        if not category_recommendations:
            category_recommendations = [
                "microsoft/DialoGPT-medium",
                "gpt2",
                "distilgpt2",
                "EleutherAI/gpt-neo-125M"
            ]
        
        # Convert to model info objects
        models = []
        for model_id in category_recommendations[:limit]:
            model_info = HFModelInfo(
                model_id=model_id,
                name=model_id.split("/")[-1],
                description=f"Recommended model for {task.value}",
                model_type=task,
                category=category or HFModelCategory.CHATBOT,
                language=language,
                free_tier_compatible=True
            )
            models.append(model_info)
        
        return models
    
    async def get_model_info(self, model_id: str) -> Optional[HFModelInfo]:
        """Get detailed information about a specific model."""
        try:
            result = await self._make_request(f"/models/{model_id}")
            
            return HFModelInfo(
                model_id=model_id,
                name=result.get("name", model_id),
                description=result.get("description", ""),
                model_type=HFModelType(result.get("pipeline_tag", "text-generation")),
                category=self._infer_category(result),
                language=result.get("language", "en"),
                license=result.get("license", "unknown"),
                downloads=result.get("downloads", 0),
                likes=result.get("likes", 0),
                tags=result.get("tags", []),
                author=result.get("author", {}).get("name", ""),
                last_modified=result.get("lastModified", ""),
                free_tier_compatible=True
            )
            
        except Exception as e:
            logger.error(f"Error getting model info for {model_id}: {e}")
            return None
    
    def _infer_category(self, model_data: Dict[str, Any]) -> HFModelCategory:
        """Infer model category from model data."""
        tags = model_data.get("tags", [])
        description = model_data.get("description", "").lower()
        
        # Check for specific categories based on tags and description
        if any(tag in ["chatbot", "dialogue"] for tag in tags) or "chat" in description:
            return HFModelCategory.CHATBOT
        elif any(tag in ["code", "programming"] for tag in tags) or "code" in description:
            return HFModelCategory.CODE_GENERATION
        elif any(tag in ["story", "creative"] for tag in tags) or "story" in description:
            return HFModelCategory.STORY_WRITING
        elif any(tag in ["translation", "multilingual"] for tag in tags):
            return HFModelCategory.MULTILINGUAL
        elif any(tag in ["summarization", "summarize"] for tag in tags):
            return HFModelCategory.NEWS_SUMMARIZATION
        elif any(tag in ["qa", "question-answering"] for tag in tags):
            return HFModelCategory.READING_COMPREHENSION
        elif any(tag in ["sentiment", "emotion"] for tag in tags):
            return HFModelCategory.SENTIMENT_ANALYSIS
        else:
            return HFModelCategory.CHATBOT  # Default category
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics."""
        current_time = time.time()
        time_since_reset = current_time - self._last_reset
        
        # Reset counter if it's been more than a month
        if time_since_reset > 30 * 24 * 3600:  # 30 days
            self._request_count = 0
            self._last_reset = current_time
        
        return {
            "requests_used": self._request_count,
            "requests_remaining": self._rate_limit - self._request_count,
            "reset_time": self._last_reset + (30 * 24 * 3600),
            "time_until_reset": (30 * 24 * 3600) - time_since_reset
        }


# Convenience functions
async def get_hf_client(api_key: str) -> HuggingFaceEnhancedClient:
    """Get an enhanced Hugging Face client."""
    return HuggingFaceEnhancedClient(api_key)


async def search_best_model(
    task: HFModelType,
    query: str,
    api_key: str,
    category: Optional[HFModelCategory] = None
) -> Optional[HFModelInfo]:
    """Search for the best model for a specific task and query."""
    async with HuggingFaceEnhancedClient(api_key) as client:
        # First try recommended models
        recommended = await client.get_recommended_models(task, category)
        if recommended:
            return recommended[0]
        
        # If no recommendations, search for models
        models = await client.search_models(query, task, category)
        if models:
            # Sort by downloads and likes
            models.sort(key=lambda m: (m.downloads, m.likes), reverse=True)
            return models[0]
        
        return None


async def generate_with_best_model(
    prompt: str,
    task: HFModelType,
    api_key: str,
    category: Optional[HFModelCategory] = None,
    **kwargs
) -> Optional[HFResponse]:
    """Generate text using the best available model for the task."""
    # Find the best model
    best_model = await search_best_model(task, prompt, api_key, category)
    if not best_model:
        return None
    
    # Generate text
    async with HuggingFaceEnhancedClient(api_key) as client:
        request = HFRequest(
            model_id=best_model.model_id,
            inputs=prompt,
            task=task,
            **kwargs
        )
        
        return await client.generate_text(request)
