"""
Model Caching Implementation for MAANG Standards

Provides intelligent model caching to reduce cold start times
and improve system performance.
"""

import os
import time
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass
import threading
import asyncio

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ModelCacheEntry:
    """Model cache entry with metadata."""
    model: Any
    last_used: float
    access_count: int
    memory_usage_mb: float
    model_name: str
    device: str


class ModelCache:
    """
    Intelligent model caching system following MAANG performance standards.
    
    Provides model caching with LRU eviction, memory management,
    and automatic warm-up capabilities.
    """
    
    def __init__(
        self,
        cache_dir: str = "./models_cache",
        max_cache_size: int = 3,
        max_memory_mb: int = 2048,
        warmup_enabled: bool = True
    ):
        """
        Initialize model cache.
        
        Args:
            cache_dir: Directory to store cached models
            max_cache_size: Maximum number of models to cache
            max_memory_mb: Maximum memory usage in MB
            warmup_enabled: Enable automatic model warmup
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.max_cache_size = max_cache_size
        self.max_memory_mb = max_memory_mb
        self.warmup_enabled = warmup_enabled
        
        self._cache: Dict[str, ModelCacheEntry] = {}
        self._lock = threading.RLock()
        self._warmup_models = [
            "sentence-transformers/all-MiniLM-L6-v2",
            "sentence-transformers/all-mpnet-base-v2",
            "distilgpt2"
        ]
        
        logger.info(f"Model cache initialized: max_size={max_cache_size}, max_memory={max_memory_mb}MB")
        
        if self.warmup_enabled:
            self._start_warmup()
    
    def _start_warmup(self):
        """Start model warmup in background thread."""
        def warmup_worker():
            try:
                for model_name in self._warmup_models:
                    try:
                        logger.info(f"Warming up model: {model_name}")
                        self.get_model(model_name)
                        logger.info(f"Model warmed up successfully: {model_name}")
                    except Exception as e:
                        logger.warning(f"Failed to warm up model {model_name}: {e}")
            except Exception as e:
                logger.error(f"Model warmup failed: {e}")
        
        warmup_thread = threading.Thread(target=warmup_worker, daemon=True)
        warmup_thread.start()
        logger.info("Model warmup started in background")
    
    def get_model(self, model_name: str, device: str = "cpu") -> Optional[Any]:
        """
        Get model from cache or load it.
        
        Args:
            model_name: Name of the model to load
            device: Device to load model on
            
        Returns:
            Loaded model or None if failed
        """
        cache_key = f"{model_name}_{device}"
        
        with self._lock:
            # Check if model is in cache
            if cache_key in self._cache:
                entry = self._cache[cache_key]
                entry.last_used = time.time()
                entry.access_count += 1
                logger.debug(f"Model cache hit: {model_name}")
                return entry.model
            
            # Load model if not in cache
            try:
                logger.info(f"Loading model: {model_name} on {device}")
                start_time = time.time()
                
                if "sentence-transformers" in model_name:
                    model = self._load_sentence_transformer(model_name, device)
                elif "gpt" in model_name.lower():
                    model = self._load_gpt_model(model_name, device)
                else:
                    logger.warning(f"Unknown model type: {model_name}")
                    return None
                
                load_time = time.time() - start_time
                memory_usage = self._estimate_memory_usage(model)
                
                # Create cache entry
                entry = ModelCacheEntry(
                    model=model,
                    last_used=time.time(),
                    access_count=1,
                    memory_usage_mb=memory_usage,
                    model_name=model_name,
                    device=device
                )
                
                # Check if we need to evict models
                self._evict_if_needed(entry)
                
                # Add to cache
                self._cache[cache_key] = entry
                
                logger.info(f"Model loaded successfully: {model_name} in {load_time:.2f}s, {memory_usage:.1f}MB")
                return model
                
            except Exception as e:
                logger.error(f"Failed to load model {model_name}: {e}")
                return None
    
    def _load_sentence_transformer(self, model_name: str, device: str) -> Any:
        """Load sentence transformer model."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers not available")
        
        # Check if model is cached locally
        local_path = self.cache_dir / model_name.replace("/", "_")
        if local_path.exists():
            logger.info(f"Loading cached model from: {local_path}")
            return SentenceTransformer(str(local_path))
        else:
            # Download and cache model
            logger.info(f"Downloading model: {model_name}")
            model = SentenceTransformer(model_name)
            
            # Save to local cache
            try:
                model.save(str(local_path))
                logger.info(f"Model cached to: {local_path}")
            except Exception as e:
                logger.warning(f"Failed to cache model: {e}")
            
            return model
    
    def _load_gpt_model(self, model_name: str, device: str) -> Any:
        """Load GPT model."""
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch not available")
        
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            # Check if model is cached locally
            local_path = self.cache_dir / model_name.replace("/", "_")
            if local_path.exists():
                logger.info(f"Loading cached GPT model from: {local_path}")
                tokenizer = AutoTokenizer.from_pretrained(str(local_path))
                model = AutoModelForCausalLM.from_pretrained(str(local_path))
            else:
                # Download and cache model
                logger.info(f"Downloading GPT model: {model_name}")
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForCausalLM.from_pretrained(model_name)
                
                # Save to local cache
                try:
                    tokenizer.save_pretrained(str(local_path))
                    model.save_pretrained(str(local_path))
                    logger.info(f"GPT model cached to: {local_path}")
                except Exception as e:
                    logger.warning(f"Failed to cache GPT model: {e}")
            
            return {"tokenizer": tokenizer, "model": model}
            
        except ImportError:
            raise ImportError("transformers not available")
    
    def _estimate_memory_usage(self, model: Any) -> float:
        """Estimate model memory usage in MB."""
        try:
            if TORCH_AVAILABLE and hasattr(model, 'parameters'):
                total_params = sum(p.numel() for p in model.parameters())
                # Rough estimate: 4 bytes per parameter (float32)
                memory_mb = (total_params * 4) / (1024 * 1024)
                return memory_mb
            else:
                # Fallback estimate
                return 100.0
        except Exception:
            return 100.0
    
    def _evict_if_needed(self, new_entry: ModelCacheEntry):
        """Evict models if cache is full or memory limit exceeded."""
        current_memory = sum(entry.memory_usage_mb for entry in self._cache.values())
        
        # Check memory limit
        if current_memory + new_entry.memory_usage_mb > self.max_memory_mb:
            self._evict_by_memory()
        
        # Check cache size limit
        if len(self._cache) >= self.max_cache_size:
            self._evict_by_lru()
    
    def _evict_by_memory(self):
        """Evict models to free memory."""
        # Sort by memory usage (largest first)
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].memory_usage_mb,
            reverse=True
        )
        
        for cache_key, entry in sorted_entries:
            del self._cache[cache_key]
            logger.info(f"Evicted model from cache: {entry.model_name} ({entry.memory_usage_mb:.1f}MB)")
            
            # Check if we have enough memory now
            current_memory = sum(e.memory_usage_mb for e in self._cache.values())
            if current_memory < self.max_memory_mb * 0.8:  # Keep 20% buffer
                break
    
    def _evict_by_lru(self):
        """Evict least recently used model."""
        if not self._cache:
            return
        
        # Find least recently used entry
        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_used
        )
        
        entry = self._cache[lru_key]
        del self._cache[lru_key]
        logger.info(f"Evicted LRU model from cache: {entry.model_name}")
    
    def clear_cache(self):
        """Clear all cached models."""
        with self._lock:
            self._cache.clear()
            logger.info("Model cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_memory = sum(entry.memory_usage_mb for entry in self._cache.values())
            total_accesses = sum(entry.access_count for entry in self._cache.values())
            
            return {
                "cache_size": len(self._cache),
                "max_cache_size": self.max_cache_size,
                "total_memory_mb": total_memory,
                "max_memory_mb": self.max_memory_mb,
                "total_accesses": total_accesses,
                "models": [
                    {
                        "name": entry.model_name,
                        "device": entry.device,
                        "memory_mb": entry.memory_usage_mb,
                        "access_count": entry.access_count,
                        "last_used": entry.last_used
                    }
                    for entry in self._cache.values()
                ]
            }
    
    def preload_model(self, model_name: str, device: str = "cpu"):
        """Preload a model into cache."""
        def preload_worker():
            try:
                self.get_model(model_name, device)
                logger.info(f"Model preloaded: {model_name}")
            except Exception as e:
                logger.error(f"Failed to preload model {model_name}: {e}")
        
        preload_thread = threading.Thread(target=preload_worker, daemon=True)
        preload_thread.start()


# Global model cache instance
_model_cache: Optional[ModelCache] = None


def get_model_cache() -> ModelCache:
    """Get global model cache instance."""
    global _model_cache
    
    if _model_cache is None:
        _model_cache = ModelCache()
    
    return _model_cache


def clear_model_cache():
    """Clear global model cache."""
    global _model_cache
    
    if _model_cache:
        _model_cache.clear_cache()
        _model_cache = None
