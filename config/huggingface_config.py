#!/usr/bin/env python3
"""
HuggingFace Configuration for SarvanOM
Loads tokens and configuration from environment variables
Following MAANG/OpenAI/Perplexity industry standards
"""

import os
from typing import Optional
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class HuggingFaceConfig:
    """HuggingFace configuration settings"""
    
    # Tokens
    read_token: Optional[str] = None
    write_token: Optional[str] = None
    api_token: Optional[str] = None
    
    # Model settings
    cache_dir: str = "./models_cache"
    device: str = "auto"
    max_models_in_memory: int = 5
    
    # Performance settings
    batch_size: int = 1
    max_length: int = 512
    temperature: float = 0.7
    
    # Cache settings
    enable_model_caching: bool = True
    cache_ttl: int = 3600
    
    # Logging
    enable_logging: bool = True
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Load configuration from environment variables"""
        # Load tokens from environment
        self.read_token = os.getenv("HUGGINGFACE_READ_TOKEN", self.read_token)
        self.write_token = os.getenv("HUGGINGFACE_WRITE_TOKEN", self.write_token)
        self.api_token = os.getenv("HUGGINGFACE_API_TOKEN", self.api_token)
        
        # Use API token as fallback for read/write tokens if not provided
        if not self.read_token and self.api_token:
            self.read_token = self.api_token
        if not self.write_token and self.api_token:
            self.write_token = self.api_token
        
        # Load other settings
        self.cache_dir = os.getenv("HF_CACHE_DIR", self.cache_dir)
        self.device = os.getenv("HF_DEVICE", self.device)
        self.max_models_in_memory = int(os.getenv("HF_MAX_MODELS", str(self.max_models_in_memory)))
        
        # Create cache directory if it doesn't exist
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
    
    def get_token_for_operation(self, operation: str) -> Optional[str]:
        """Get appropriate token for operation type"""
        if operation == "read":
            return self.read_token
        elif operation == "write":
            return self.write_token
        elif operation == "api":
            return self.api_token
        else:
            return self.api_token or self.read_token
    
    def is_authenticated(self) -> bool:
        """Check if HuggingFace is properly authenticated"""
        return bool(self.read_token or self.write_token or self.api_token)
    
    def get_auth_headers(self) -> dict:
        """Get authentication headers for API requests"""
        token = self.get_token_for_operation("api")
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}
    
    def validate_config(self) -> list:
        """Validate configuration and return any issues"""
        issues = []
        
        if not self.is_authenticated():
            issues.append("No HuggingFace tokens found. Set HUGGINGFACE_READ_TOKEN, HUGGINGFACE_WRITE_TOKEN, or HUGGINGFACE_API_TOKEN")
        
        if not os.path.exists(self.cache_dir):
            issues.append(f"Cache directory {self.cache_dir} does not exist and could not be created")
        
        return issues

# Global configuration instance
huggingface_config = HuggingFaceConfig()
