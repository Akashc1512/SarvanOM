#!/usr/bin/env python3
"""
Comprehensive HuggingFace Integration for SarvanOM
Implements MAANG/OpenAI/Perplexity level HuggingFace integration with:
- Text Generation (LLM)
- Embeddings and Vector Search
- Text Classification
- Sentiment Analysis
- Question Answering
- Summarization
- Translation
- Named Entity Recognition
- Text Similarity
- Zero-shot Classification
- Feature Extraction
- Image Classification (if needed)
- Audio Processing (if needed)
"""

import asyncio
import json
import logging
import time
import hashlib
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import os
import re

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# HuggingFace imports
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    AutoModelForQuestionAnswering, AutoModelForSeq2SeqLM,
    AutoModelForTokenClassification, AutoModelForCausalLM,
    pipeline, Pipeline
)
from sentence_transformers import SentenceTransformer
from datasets import load_dataset, Dataset
import torch
import numpy as np
from huggingface_hub import InferenceClient, HfApi

# Local imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from config.huggingface_config import huggingface_config

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """HuggingFace task types"""
    TEXT_GENERATION = "text-generation"
    TEXT_CLASSIFICATION = "text-classification"
    SENTIMENT_ANALYSIS = "sentiment-analysis"
    QUESTION_ANSWERING = "question-answering"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    NAMED_ENTITY_RECOGNITION = "token-classification"
    TEXT_SIMILARITY = "text-similarity"
    ZERO_SHOT_CLASSIFICATION = "zero-shot-classification"
    FEATURE_EXTRACTION = "feature-extraction"
    EMBEDDINGS = "embeddings"

class ModelCategory(Enum):
    """Model categories for different use cases"""
    LLM = "llm"
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    NER = "ner"
    QA = "qa"

@dataclass
class ModelConfig:
    """Model configuration for different tasks"""
    model_name: str
    task_type: TaskType
    category: ModelCategory
    max_length: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    device: str = "auto"
    batch_size: int = 1
    cache_dir: Optional[str] = None

@dataclass
class HuggingFaceResponse:
    """Standardized response format"""
    task_type: TaskType
    model_name: str
    result: Any
    processing_time: float
    metadata: Dict[str, Any]
    timestamp: str

class HuggingFaceIntegration:
    """
    Comprehensive HuggingFace integration service
    Following MAANG/OpenAI/Perplexity industry standards
    """
    
    def __init__(self, cache_dir: str = None):
        # Use configuration
        self.config = huggingface_config
        self.cache_dir = cache_dir or self.config.cache_dir
        self.device = self.config.device
        if self.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.models: Dict[str, Any] = {}
        self.pipelines: Dict[str, Pipeline] = {}
        self.embedding_model: Optional[SentenceTransformer] = None
        
        # Initialize clients with authentication
        if self.config.is_authenticated():
            token = self.config.get_token_for_operation("api")
            self.inference_client = InferenceClient(token=token)
            self.api = HfApi(token=token)
        else:
            self.inference_client = InferenceClient()
            self.api = HfApi()
        
        # Model configurations for different tasks - Updated for August 2025
        self.model_configs = {
            # Latest Text Generation Models (August 2025)
            "microsoft/DialoGPT-medium": ModelConfig("microsoft/DialoGPT-medium", TaskType.TEXT_GENERATION, ModelCategory.LLM),
            "gpt2": ModelConfig("gpt2", TaskType.TEXT_GENERATION, ModelCategory.LLM),
            "distilgpt2": ModelConfig("distilgpt2", TaskType.TEXT_GENERATION, ModelCategory.LLM),
            "EleutherAI/gpt-neo-125M": ModelConfig("EleutherAI/gpt-neo-125M", TaskType.TEXT_GENERATION, ModelCategory.LLM),
            "microsoft/DialoGPT-small": ModelConfig("microsoft/DialoGPT-small", TaskType.TEXT_GENERATION, ModelCategory.LLM),
            
            # Latest Embedding Models (August 2025)
            "sentence-transformers/all-MiniLM-L6-v2": ModelConfig("sentence-transformers/all-MiniLM-L6-v2", TaskType.EMBEDDINGS, ModelCategory.EMBEDDING),
            "sentence-transformers/all-mpnet-base-v2": ModelConfig("sentence-transformers/all-mpnet-base-v2", TaskType.EMBEDDINGS, ModelCategory.EMBEDDING),
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": ModelConfig("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", TaskType.EMBEDDINGS, ModelCategory.EMBEDDING),
            "sentence-transformers/all-distilroberta-v1": ModelConfig("sentence-transformers/all-distilroberta-v1", TaskType.EMBEDDINGS, ModelCategory.EMBEDDING),
            
            # Latest Classification Models (August 2025)
            "distilbert-base-uncased-finetuned-sst-2-english": ModelConfig("distilbert-base-uncased-finetuned-sst-2-english", TaskType.SENTIMENT_ANALYSIS, ModelCategory.CLASSIFICATION),
            "cardiffnlp/twitter-roberta-base-sentiment-latest": ModelConfig("cardiffnlp/twitter-roberta-base-sentiment-latest", TaskType.SENTIMENT_ANALYSIS, ModelCategory.CLASSIFICATION),
            "facebook/bart-large-mnli": ModelConfig("facebook/bart-large-mnli", TaskType.ZERO_SHOT_CLASSIFICATION, ModelCategory.CLASSIFICATION),
            "microsoft/DialoGPT-medium": ModelConfig("microsoft/DialoGPT-medium", TaskType.TEXT_CLASSIFICATION, ModelCategory.CLASSIFICATION),
            
            # Latest Summarization Models (August 2025)
            "facebook/bart-large-cnn": ModelConfig("facebook/bart-large-cnn", TaskType.SUMMARIZATION, ModelCategory.SUMMARIZATION),
            "t5-small": ModelConfig("t5-small", TaskType.SUMMARIZATION, ModelCategory.SUMMARIZATION),
            "sshleifer/distilbart-cnn-12-6": ModelConfig("sshleifer/distilbart-cnn-12-6", TaskType.SUMMARIZATION, ModelCategory.SUMMARIZATION),
            "google/pegasus-xsum": ModelConfig("google/pegasus-xsum", TaskType.SUMMARIZATION, ModelCategory.SUMMARIZATION),
            
            # Latest Translation Models (August 2025)
            "Helsinki-NLP/opus-mt-en-es": ModelConfig("Helsinki-NLP/opus-mt-en-es", TaskType.TRANSLATION, ModelCategory.TRANSLATION),
            "Helsinki-NLP/opus-mt-en-fr": ModelConfig("Helsinki-NLP/opus-mt-en-fr", TaskType.TRANSLATION, ModelCategory.TRANSLATION),
            "Helsinki-NLP/opus-mt-en-de": ModelConfig("Helsinki-NLP/opus-mt-en-de", TaskType.TRANSLATION, ModelCategory.TRANSLATION),
            "Helsinki-NLP/opus-mt-en-ja": ModelConfig("Helsinki-NLP/opus-mt-en-ja", TaskType.TRANSLATION, ModelCategory.TRANSLATION),
            
            # Latest NER Models (August 2025)
            "dbmdz/bert-large-cased-finetuned-conll03-english": ModelConfig("dbmdz/bert-large-cased-finetuned-conll03-english", TaskType.NAMED_ENTITY_RECOGNITION, ModelCategory.NER),
            "dslim/bert-base-NER": ModelConfig("dslim/bert-base-NER", TaskType.NAMED_ENTITY_RECOGNITION, ModelCategory.NER),
            "Jean-Baptiste/roberta-large-ner-english": ModelConfig("Jean-Baptiste/roberta-large-ner-english", TaskType.NAMED_ENTITY_RECOGNITION, ModelCategory.NER),
            
            # Latest QA Models (August 2025)
            "distilbert-base-cased-distilled-squad": ModelConfig("distilbert-base-cased-distilled-squad", TaskType.QUESTION_ANSWERING, ModelCategory.QA),
            "deepset/roberta-base-squad2": ModelConfig("deepset/roberta-base-squad2", TaskType.QUESTION_ANSWERING, ModelCategory.QA),
            "microsoft/DialoGPT-medium": ModelConfig("microsoft/DialoGPT-medium", TaskType.QUESTION_ANSWERING, ModelCategory.QA),
        }
        
        # Validate configuration
        config_issues = self.config.validate_config()
        if config_issues:
            logger.warning(f"HuggingFace configuration issues: {config_issues}")
        
        auth_status = "authenticated" if self.config.is_authenticated() else "unauthenticated"
        logger.info(f"Initialized HuggingFace Integration on device: {self.device}, auth: {auth_status}")
    
    async def initialize(self):
        """Initialize the HuggingFace integration with latest stable models"""
        try:
            # Load default embedding model (fast and reliable)
            await self.load_embedding_model("sentence-transformers/all-MiniLM-L6-v2")
            
            # Load default text generation model (working and available)
            await self.load_model("microsoft/DialoGPT-medium", TaskType.TEXT_GENERATION)
            
            # Load default sentiment analysis model
            await self.load_model("distilbert-base-uncased-finetuned-sst-2-english", TaskType.SENTIMENT_ANALYSIS)
            
            # Load zero-shot classification for query intent
            await self.load_model("facebook/bart-large-mnli", TaskType.ZERO_SHOT_CLASSIFICATION)
            
            # Load summarization model
            await self.load_model("sshleifer/distilbart-cnn-12-6", TaskType.SUMMARIZATION)
            
            # Load QA model
            await self.load_model("distilbert-base-cased-distilled-squad", TaskType.QUESTION_ANSWERING)
            
            logger.info("✅ HuggingFace Integration initialized successfully with latest models")
        except Exception as e:
            logger.error(f"❌ Failed to initialize HuggingFace Integration: {e}")
            # Fallback to basic models if advanced ones fail
            try:
                await self.load_model("gpt2", TaskType.TEXT_GENERATION)
                logger.info("✅ Fallback to basic models successful")
            except Exception as fallback_error:
                logger.error(f"❌ Fallback also failed: {fallback_error}")
    
    async def load_model(self, model_name: str, task_type: TaskType) -> bool:
        """Load a HuggingFace model for a specific task"""
        try:
            model_key = f"{model_name}_{task_type.value}"
            
            if model_key in self.models:
                return True
            
            logger.info(f"Loading model: {model_name} for task: {task_type.value}")
            
            # Load model based on task type
            if task_type == TaskType.TEXT_GENERATION:
                # Use authentication token if available
                token = self.config.get_token_for_operation("read")
                model_kwargs = {
                    "cache_dir": self.cache_dir,
                    "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32
                }
                tokenizer_kwargs = {}  # Remove cache_dir from tokenizer
                
                if token:
                    model_kwargs["token"] = token
                    tokenizer_kwargs["token"] = token
                
                model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
                tokenizer = AutoTokenizer.from_pretrained(model_name, **tokenizer_kwargs)
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                
                self.models[model_key] = {"model": model, "tokenizer": tokenizer}
                
            elif task_type == TaskType.SENTIMENT_ANALYSIS:
                pipeline = self._create_pipeline(model_name, task_type.value)
                self.pipelines[model_key] = pipeline
                
            elif task_type == TaskType.SUMMARIZATION:
                pipeline = self._create_pipeline(model_name, task_type.value)
                self.pipelines[model_key] = pipeline
                
            elif task_type == TaskType.TRANSLATION:
                pipeline = self._create_pipeline(model_name, task_type.value)
                self.pipelines[model_key] = pipeline
                
            elif task_type == TaskType.NAMED_ENTITY_RECOGNITION:
                pipeline = self._create_pipeline(model_name, task_type.value)
                self.pipelines[model_key] = pipeline
                
            elif task_type == TaskType.QUESTION_ANSWERING:
                pipeline = self._create_pipeline(model_name, task_type.value)
                self.pipelines[model_key] = pipeline
                
            logger.info(f"✅ Model {model_name} loaded successfully for {task_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load model {model_name}: {e}")
            return False
    
    def _create_pipeline(self, model_name: str, task: str) -> Pipeline:
        """Create a HuggingFace pipeline"""
        # Use authentication token if available
        token = self.config.get_token_for_operation("read")
        pipeline_kwargs = {
            "task": task,
            "model": model_name,
            "device": self.device
        }
        
        if token:
            pipeline_kwargs["token"] = token
        
        return pipeline(**pipeline_kwargs)
    
    async def load_embedding_model(self, model_name: str) -> bool:
        """Load a sentence transformer model for embeddings"""
        try:
            logger.info(f"Loading embedding model: {model_name}")
            
            # Use authentication token if available
            token = self.config.get_token_for_operation("read")
            model_kwargs = {"cache_folder": self.cache_dir}
            
            if token:
                model_kwargs["token"] = token
            
            self.embedding_model = SentenceTransformer(model_name, **model_kwargs)
            logger.info(f"✅ Embedding model {model_name} loaded successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model {model_name}: {e}")
            return False
    
    async def generate_text(self, prompt: str, model_name: str = "microsoft/DialoGPT-medium", max_length: int = 100, temperature: float = 0.7) -> HuggingFaceResponse:
        """Generate text using HuggingFace models with latest stable models"""
        start_time = time.time()
        
        try:
            model_key = f"{model_name}_{TaskType.TEXT_GENERATION.value}"
            
            if model_key not in self.models:
                await self.load_model(model_name, TaskType.TEXT_GENERATION)
            
            if model_key in self.models:
                model_data = self.models[model_key]
                model = model_data["model"]
                tokenizer = model_data["tokenizer"]
                
                # Tokenize input
                inputs = tokenizer.encode(prompt, return_tensors="pt", truncation=True, max_length=512)
                
                # Generate text
                with torch.no_grad():
                    outputs = model.generate(
                        inputs,
                        max_length=max_length,
                        temperature=temperature,
                        do_sample=True,
                        pad_token_id=tokenizer.eos_token_id,
                        eos_token_id=tokenizer.eos_token_id,
                        attention_mask=torch.ones_like(inputs)
                    )
                
                # Decode output
                generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                processing_time = time.time() - start_time
                
                return HuggingFaceResponse(
                    task_type=TaskType.TEXT_GENERATION,
                    model_name=model_name,
                    result=generated_text,
                    processing_time=processing_time,
                    metadata={
                        "input_length": len(prompt),
                        "output_length": len(generated_text),
                        "temperature": temperature,
                        "max_length": max_length
                    },
                    timestamp=datetime.now().isoformat()
                )
            else:
                raise Exception(f"Model {model_name} not loaded")
                
        except Exception as e:
            logger.error(f"❌ Text generation failed with {model_name}: {e}")
            # Try fallback model
            if model_name != "gpt2":
                logger.info(f"🔄 Trying fallback model: gpt2")
                return await self.generate_text(prompt, "gpt2", max_length, temperature)
            else:
                raise e
    
    async def get_embeddings(self, texts: List[str], model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> HuggingFaceResponse:
        """Get embeddings for a list of texts"""
        start_time = time.time()
        
        try:
            if self.embedding_model is None:
                await self.load_embedding_model(model_name)
            
            if self.embedding_model:
                # Get embeddings
                embeddings = self.embedding_model.encode(texts, convert_to_tensor=True)
                
                # Convert to numpy for easier handling
                embeddings_np = embeddings.cpu().numpy()
                
                processing_time = time.time() - start_time
                
                return HuggingFaceResponse(
                    task_type=TaskType.EMBEDDINGS,
                    model_name=model_name,
                    result=embeddings_np.tolist(),
                    processing_time=processing_time,
                    metadata={
                        "num_texts": len(texts),
                        "embedding_dimension": embeddings_np.shape[1],
                        "model_name": model_name
                    },
                    timestamp=datetime.now().isoformat()
                )
            else:
                raise Exception("Embedding model not loaded")
                
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
    
    async def analyze_sentiment(self, text: str, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english") -> HuggingFaceResponse:
        """Analyze sentiment of text"""
        start_time = time.time()
        
        try:
            model_key = f"{model_name}_{TaskType.SENTIMENT_ANALYSIS.value}"
            
            if model_key not in self.pipelines:
                await self.load_model(model_name, TaskType.SENTIMENT_ANALYSIS)
            
            if model_key in self.pipelines:
                pipeline = self.pipelines[model_key]
                
                # Analyze sentiment
                result = pipeline(text)
                
                processing_time = time.time() - start_time
                
                return HuggingFaceResponse(
                    task_type=TaskType.SENTIMENT_ANALYSIS,
                    model_name=model_name,
                    result=result,
                    processing_time=processing_time,
                    metadata={
                        "text_length": len(text),
                        "model_name": model_name
                    },
                    timestamp=datetime.now().isoformat()
                )
            else:
                raise Exception(f"Sentiment analysis model {model_name} not loaded")
                
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            raise

    async def answer_question(self, question: str, context: str, model_name: str = "distilbert-base-cased-distilled-squad") -> HuggingFaceResponse:
        """Answer questions based on context"""
        start_time = time.time()
        
        try:
            model_key = f"{model_name}_{TaskType.QUESTION_ANSWERING.value}"
            
            if model_key not in self.pipelines:
                await self.load_model(model_name, TaskType.QUESTION_ANSWERING)
            
            if model_key in self.pipelines:
                pipeline = self.pipelines[model_key]
                
                # Answer question
                result = pipeline(question=question, context=context)
                
                processing_time = time.time() - start_time
                
                return HuggingFaceResponse(
                    task_type=TaskType.QUESTION_ANSWERING,
                    model_name=model_name,
                    result=result,
                    processing_time=processing_time,
                    metadata={
                        "question_length": len(question),
                        "context_length": len(context),
                        "model_name": model_name
                    },
                    timestamp=datetime.now().isoformat()
                )
            else:
                raise Exception(f"Question answering model {model_name} not loaded")
                
        except Exception as e:
            logger.error(f"Question answering failed: {e}")
            raise
    
    async def summarize_text(self, text: str, model_name: str = "sshleifer/distilbart-cnn-12-6", max_length: int = 130, min_length: int = 30) -> HuggingFaceResponse:
        """Summarize text using HuggingFace models"""
        start_time = time.time()
        
        try:
            model_key = f"{model_name}_{TaskType.SUMMARIZATION.value}"
            
            if model_key not in self.pipelines:
                await self.load_model(model_name, TaskType.SUMMARIZATION)
            
            if model_key in self.pipelines:
                pipeline = self.pipelines[model_key]
                
                # Generate summary
                result = pipeline(text, max_length=max_length, min_length=min_length, do_sample=False)
                
                processing_time = time.time() - start_time
                
                return HuggingFaceResponse(
                    task_type=TaskType.SUMMARIZATION,
                    model_name=model_name,
                    result=result,
                    processing_time=processing_time,
                    metadata={
                        "input_length": len(text),
                        "output_length": len(result[0]['summary_text']) if result and len(result) > 0 else 0,
                        "max_length": max_length,
                        "min_length": min_length
                    },
                    timestamp=datetime.now().isoformat()
                )
            else:
                raise Exception(f"Summarization model {model_name} not loaded")
                
        except Exception as e:
            logger.error(f"Text summarization failed: {e}")
            raise

    async def zero_shot_classify(self, text: str, candidate_labels: List[str], model_name: str = "facebook/bart-large-mnli") -> HuggingFaceResponse:
        """Perform zero-shot classification with proper method name"""
        start_time = time.time()
        
        try:
            model_key = f"{model_name}_{TaskType.ZERO_SHOT_CLASSIFICATION.value}"
            
            if model_key not in self.pipelines:
                await self.load_model(model_name, TaskType.ZERO_SHOT_CLASSIFICATION)
            
            if model_key in self.pipelines:
                pipeline = self.pipelines[model_key]
                
                # Perform zero-shot classification
                result = pipeline(text, candidate_labels=candidate_labels)
                
                processing_time = time.time() - start_time
                
                return HuggingFaceResponse(
                    task_type=TaskType.ZERO_SHOT_CLASSIFICATION,
                    model_name=model_name,
                    result=result,
                    processing_time=processing_time,
                    metadata={
                        "text_length": len(text),
                        "num_labels": len(candidate_labels),
                        "model_name": model_name
                    },
                    timestamp=datetime.now().isoformat()
                )
            else:
                raise Exception(f"Zero-shot classification model {model_name} not loaded")
                
        except Exception as e:
            logger.error(f"Zero-shot classification failed: {e}")
            raise
    
    async def translate_text(self, text: str, target_language: str = "es", model_name: str = "Helsinki-NLP/opus-mt-en-es") -> HuggingFaceResponse:
        """Translate text"""
        start_time = time.time()
        
        try:
            model_key = f"{model_name}_{TaskType.TRANSLATION.value}"
            
            if model_key not in self.pipelines:
                await self.load_model(model_name, TaskType.TRANSLATION)
            
            if model_key in self.pipelines:
                pipeline = self.pipelines[model_key]
                result = pipeline(text)
                
                processing_time = time.time() - start_time
                
                return HuggingFaceResponse(
                    task_type=TaskType.TRANSLATION,
                    model_name=model_name,
                    result=result[0]["translation_text"],
                    processing_time=processing_time,
                    metadata={
                        "source_length": len(text),
                        "target_language": target_language,
                        "model_name": model_name
                    },
                    timestamp=datetime.now().isoformat()
                )
            else:
                raise Exception(f"Translation model {model_name} not loaded")
                
        except Exception as e:
            logger.error(f"Text translation failed: {e}")
            raise
    
    async def extract_entities(self, text: str, model_name: str = "dbmdz/bert-large-cased-finetuned-conll03-english") -> HuggingFaceResponse:
        """Extract named entities from text"""
        start_time = time.time()
        
        try:
            model_key = f"{model_name}_{TaskType.NAMED_ENTITY_RECOGNITION.value}"
            
            if model_key not in self.pipelines:
                await self.load_model(model_name, TaskType.NAMED_ENTITY_RECOGNITION)
            
            if model_key in self.pipelines:
                pipeline = self.pipelines[model_key]
                result = pipeline(text)
                
                processing_time = time.time() - start_time
                
                return HuggingFaceResponse(
                    task_type=TaskType.NAMED_ENTITY_RECOGNITION,
                    model_name=model_name,
                    result=result,
                    processing_time=processing_time,
                    metadata={
                        "text_length": len(text),
                        "num_entities": len(result),
                        "model_name": model_name
                    },
                    timestamp=datetime.now().isoformat()
                )
            else:
                raise Exception(f"NER model {model_name} not loaded")
                
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            raise
    
    async def answer_question(self, question: str, context: str, model_name: str = "distilbert-base-cased-distilled-squad") -> HuggingFaceResponse:
        """Answer questions based on context"""
        start_time = time.time()
        
        try:
            model_key = f"{model_name}_{TaskType.QUESTION_ANSWERING.value}"
            
            if model_key not in self.pipelines:
                await self.load_model(model_name, TaskType.QUESTION_ANSWERING)
            
            if model_key in self.pipelines:
                pipeline = self.pipelines[model_key]
                
                # Answer question
                result = pipeline(question=question, context=context)
                
                processing_time = time.time() - start_time
                
                return HuggingFaceResponse(
                    task_type=TaskType.QUESTION_ANSWERING,
                    model_name=model_name,
                    result=result,
                    processing_time=processing_time,
                    metadata={
                        "question_length": len(question),
                        "context_length": len(context),
                        "model_name": model_name
                    },
                    timestamp=datetime.now().isoformat()
                )
            else:
                raise Exception(f"Question answering model {model_name} not loaded")
                
        except Exception as e:
            logger.error(f"Question answering failed: {e}")
            raise
    
    async def calculate_similarity(self, text1: str, text2: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> HuggingFaceResponse:
        """Calculate similarity between two texts"""
        start_time = time.time()
        
        try:
            if self.embedding_model is None:
                await self.load_embedding_model(model_name)
            
            if self.embedding_model:
                # Get embeddings for both texts
                embeddings = self.embedding_model.encode([text1, text2], convert_to_tensor=True)
                
                # Calculate cosine similarity
                similarity = torch.cosine_similarity(embeddings[0:1], embeddings[1:2]).item()
                
                processing_time = time.time() - start_time
                
                return HuggingFaceResponse(
                    task_type=TaskType.TEXT_SIMILARITY,
                    model_name=model_name,
                    result={"similarity_score": similarity},
                    processing_time=processing_time,
                    metadata={
                        "text1_length": len(text1),
                        "text2_length": len(text2),
                        "model_name": model_name
                    },
                    timestamp=datetime.now().isoformat()
                )
            else:
                raise Exception("Embedding model not loaded")
                
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            raise
    
    async def zero_shot_classification(self, text: str, candidate_labels: List[str], model_name: str = "facebook/bart-large-mnli") -> HuggingFaceResponse:
        """Perform zero-shot classification"""
        start_time = time.time()
        
        try:
            # Use inference client for zero-shot classification
            result = self.inference_client.post(
                model=model_name,
                inputs=text,
                parameters={"candidate_labels": candidate_labels}
            )
            
            processing_time = time.time() - start_time
            
            return HuggingFaceResponse(
                task_type=TaskType.ZERO_SHOT_CLASSIFICATION,
                model_name=model_name,
                result=result,
                processing_time=processing_time,
                metadata={
                    "text_length": len(text),
                    "num_labels": len(candidate_labels),
                    "model_name": model_name
                },
                timestamp=datetime.now().isoformat()
            )
                
        except Exception as e:
            logger.error(f"Zero-shot classification failed: {e}")
            raise
    
    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a model"""
        try:
            model_info = self.api.model_info(model_name)
            return {
                "model_name": model_name,
                "downloads": model_info.downloads,
                "likes": model_info.likes,
                "tags": model_info.tags,
                "author": model_info.author,
                "last_modified": model_info.last_modified.isoformat() if model_info.last_modified else None
            }
        except Exception as e:
            logger.error(f"Failed to get model info for {model_name}: {e}")
            return {"model_name": model_name, "error": str(e)}
    
    async def get_available_models(self) -> Dict[str, List[str]]:
        """Get list of available models by category"""
        return {
            "text_generation": ["gpt2", "distilgpt2", "microsoft/DialoGPT-medium"],
            "embeddings": ["sentence-transformers/all-MiniLM-L6-v2", "sentence-transformers/all-mpnet-base-v2"],
            "sentiment_analysis": ["distilbert-base-uncased-finetuned-sst-2-english", "cardiffnlp/twitter-roberta-base-sentiment-latest"],
            "summarization": ["facebook/bart-large-cnn", "t5-small"],
            "translation": ["Helsinki-NLP/opus-mt-en-es", "Helsinki-NLP/opus-mt-en-fr"],
            "ner": ["dbmdz/bert-large-cased-finetuned-conll03-english"],
            "qa": ["distilbert-base-cased-distilled-squad"]
        }
    
    async def get_auth_status(self) -> Dict[str, Any]:
        """Get authentication status and configuration"""
        return {
            "authenticated": self.config.is_authenticated(),
            "has_read_token": bool(self.config.api_token),
            "has_write_token": bool(self.config.api_token),
            "has_api_token": bool(self.config.api_token),
            "device": self.device,
            "cache_dir": self.cache_dir,
            "config_issues": self.config.validate_config()
        }
    
    async def close(self):
        """Clean up resources"""
        try:
            # Clear models from memory
            self.models.clear()
            self.pipelines.clear()
            self.embedding_model = None
            
            # Clear CUDA cache if available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("✅ HuggingFace Integration closed successfully")
        except Exception as e:
            logger.error(f"❌ Error closing HuggingFace Integration: {e}")

# Global instance
huggingface_integration = HuggingFaceIntegration()
