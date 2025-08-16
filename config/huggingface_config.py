#!/usr/bin/env python3
"""
HuggingFace Configuration for SarvanOM
MAANG/OpenAI/Perplexity Standards Implementation
Updated for August 2025
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class HuggingFaceConfig:
    """HuggingFace configuration with latest settings"""
    
    # API Configuration
    api_token: Optional[str] = None
    cache_dir: str = "./models/huggingface"
    device: str = "auto"
    
    # Model Settings
    default_text_model: str = "microsoft/DialoGPT-medium"
    default_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    default_sentiment_model: str = "distilbert-base-uncased-finetuned-sst-2-english"
    default_qa_model: str = "distilbert-base-cased-distilled-squad"
    default_summarization_model: str = "sshleifer/distilbart-cnn-12-6"
    default_translation_model: str = "Helsinki-NLP/opus-mt-en-es"
    default_ner_model: str = "dslim/bert-base-NER"
    
    # Performance Settings
    max_length: int = 512
    batch_size: int = 8
    temperature: float = 0.7
    top_p: float = 0.9
    
    # Feature Flags
    enable_embeddings: bool = True
    enable_sentiment_analysis: bool = True
    enable_qa: bool = True
    enable_summarization: bool = True
    enable_translation: bool = True
    enable_ner: bool = True
    enable_zero_shot: bool = True
    
    # Rate Limiting
    max_requests_per_minute: int = 60
    request_timeout: int = 30
    
    def __post_init__(self):
        """Initialize configuration from environment variables"""
        # Load API token from environment
        self.api_token = os.getenv("HUGGINGFACE_API_KEY", self.api_token)
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Set device based on availability
        if self.device == "auto":
            try:
                import torch
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                self.device = "cpu"
    
    def is_authenticated(self) -> bool:
        """Check if HuggingFace is authenticated"""
        return bool(self.api_token and self.api_token != "your_huggingface_token_here")
    
    def get_token_for_operation(self, operation: str) -> Optional[str]:
        """Get token for specific operation"""
        if self.is_authenticated():
            return self.api_token
        return None
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        if not self.is_authenticated():
            issues.append("HuggingFace API token not set - some features may be limited")
        
        if not os.path.exists(self.cache_dir):
            issues.append(f"Cache directory {self.cache_dir} does not exist")
        
        if self.max_length <= 0:
            issues.append("max_length must be positive")
        
        if self.batch_size <= 0:
            issues.append("batch_size must be positive")
        
        if not (0 <= self.temperature <= 2):
            issues.append("temperature must be between 0 and 2")
        
        if not (0 <= self.top_p <= 1):
            issues.append("top_p must be between 0 and 1")
        
        return issues
    
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """Get configuration for a specific model"""
        return {
            "model_name": model_name,
            "cache_dir": self.cache_dir,
            "device": self.device,
            "max_length": self.max_length,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "batch_size": self.batch_size
        }

# Create global configuration instance
huggingface_config = HuggingFaceConfig()
