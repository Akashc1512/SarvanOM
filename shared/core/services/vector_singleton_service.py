#!/usr/bin/env python3
"""
Vector Singleton Service - Process-Level Singletons + Cold-Start Killer

This service eliminates the 20-30s cold-start penalty by establishing:
- Process-level singleton embedder (preloaded at startup)
- Process-level singleton vector store clients (connection pooling)
- In-memory LRU embedding cache with TTL
- Background warmup tasks for optimal performance

Key Features:
- Sub-2s vector queries after warmup (≤800ms median on subsequent queries)
- Thread/async-safe singletons with proper lifecycle management
- Structured logging for TFTI (time-to-first-inference) and TTS (time-to-search)
- Environment-driven configuration
"""

import os
import asyncio
import threading
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import hashlib
from contextlib import asynccontextmanager

# LRU Cache with TTL
try:
    from cachetools import TTLCache
    CACHETOOLS_AVAILABLE = True
except ImportError:
    CACHETOOLS_AVAILABLE = False
    TTLCache = None

# Sentence Transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

# Vector Store Imports
try:
    from shared.vectorstores.vector_store_service import QdrantVectorStore, ChromaVectorStore, InMemoryVectorStore
    VECTOR_STORES_AVAILABLE = True
except ImportError:
    VECTOR_STORES_AVAILABLE = False
    QdrantVectorStore = None
    ChromaVectorStore = None
    InMemoryVectorStore = None

from shared.core.unified_logging import get_logger

logger = get_logger(__name__)

@dataclass
class VectorConfig:
    """Vector service configuration from environment variables."""
    
    # Embedding Configuration
    embedding_model: str
    embedding_dimension: int
    embedding_cache_size: int
    embedding_cache_ttl: int
    
    # Vector Store Configuration
    vector_db_provider: str
    vector_db_url: str
    vector_db_api_key: Optional[str]
    vector_collection_name: str
    
    # Performance Configuration
    warmup_enabled: bool
    warmup_queries: int
    max_workers: int
    search_timeout: float
    embedding_timeout: float
    
    @classmethod
    def from_environment(cls) -> 'VectorConfig':
        """Load configuration from environment variables."""
        return cls(
            # Embedding settings
            embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            embedding_dimension=int(os.getenv("EMBEDDING_DIMENSION", "384")),
            embedding_cache_size=int(os.getenv("EMBEDDING_CACHE_SIZE", "1000")),
            embedding_cache_ttl=int(os.getenv("EMBEDDING_CACHE_TTL", "3600")),  # 1 hour
            
            # Vector store settings
            vector_db_provider=os.getenv("VECTOR_DB_PROVIDER", "chroma"),
            vector_db_url=os.getenv("VECTOR_DB_URL", "http://localhost:6333"),
            vector_db_api_key=os.getenv("VECTOR_DB_API_KEY"),
            vector_collection_name=os.getenv("VECTOR_COLLECTION_NAME", "sarvanom_embeddings"),
            
            # Performance settings
            warmup_enabled=os.getenv("VECTOR_WARMUP_ENABLED", "true").lower() == "true",
            warmup_queries=int(os.getenv("VECTOR_WARMUP_QUERIES", "5")),
            max_workers=int(os.getenv("VECTOR_MAX_WORKERS", "4")),
            search_timeout=float(os.getenv("VECTOR_SEARCH_TIMEOUT", "2.0")),
            embedding_timeout=float(os.getenv("VECTOR_EMBEDDING_TIMEOUT", "0.8"))
        )


class EmbeddingSingleton:
    """Process-level singleton for embedding model with thread safety."""
    
    _instance: Optional['EmbeddingSingleton'] = None
    _lock = threading.Lock()
    
    def __init__(self, config: VectorConfig):
        """Initialize embedding singleton (called only once)."""
        self.config = config
        self.model: Optional[SentenceTransformer] = None
        self.executor: Optional[ThreadPoolExecutor] = None
        self.cache: Optional[TTLCache] = None
        self.warmup_completed = False
        self.load_time_ms = 0
        self.first_inference_time_ms = 0
        
        # Initialize components
        self._initialize_cache()
        self._initialize_executor()
        
        logger.info("EmbeddingSingleton initialized", config={
            "model": config.embedding_model,
            "dimension": config.embedding_dimension,
            "cache_size": config.embedding_cache_size,
            "cache_ttl": config.embedding_cache_ttl
        })
    
    @classmethod
    def get_instance(cls, config: Optional[VectorConfig] = None) -> 'EmbeddingSingleton':
        """Get or create singleton instance (thread-safe)."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    if config is None:
                        config = VectorConfig.from_environment()
                    cls._instance = cls(config)
        return cls._instance
    
    def _initialize_cache(self):
        """Initialize LRU cache with TTL."""
        if CACHETOOLS_AVAILABLE:
            self.cache = TTLCache(
                maxsize=self.config.embedding_cache_size,
                ttl=self.config.embedding_cache_ttl
            )
            logger.info("Embedding cache initialized", 
                       cache_size=self.config.embedding_cache_size,
                       ttl_seconds=self.config.embedding_cache_ttl)
        else:
            logger.warning("cachetools not available - using simple dict cache")
            self.cache = {}
    
    def _initialize_executor(self):
        """Initialize thread pool executor for embedding operations."""
        self.executor = ThreadPoolExecutor(
            max_workers=self.config.max_workers,
            thread_name_prefix="embedding"
        )
        logger.info("Embedding thread pool initialized", max_workers=self.config.max_workers)
    
    def _load_model_sync(self) -> bool:
        """Load embedding model (synchronous - called in thread)."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.error("sentence-transformers not available")
            return False
            
        if self.model is not None:
            return True
            
        try:
            load_start = time.time()
            
            logger.info("Loading embedding model", model=self.config.embedding_model)
            self.model = SentenceTransformer(self.config.embedding_model)
            
            self.load_time_ms = (time.time() - load_start) * 1000
            
            logger.info("Embedding model loaded successfully",
                       model=self.config.embedding_model,
                       load_time_ms=round(self.load_time_ms, 2))
            
            return True
            
        except Exception as e:
            logger.error("Failed to load embedding model", 
                        model=self.config.embedding_model,
                        error=str(e))
            return False
    
    def _dummy_inference_sync(self) -> bool:
        """Perform dummy inference to warm up model (synchronous)."""
        if self.model is None:
            return False
            
        try:
            inference_start = time.time()
            
            # Perform dummy inference to warm up GPU/CPU caches
            dummy_texts = [
                "This is a dummy text for model warmup",
                "Vector search warmup query",
                "Embedding model initialization"
            ]
            
            _ = self.model.encode(dummy_texts, normalize_embeddings=True)
            
            self.first_inference_time_ms = (time.time() - inference_start) * 1000
            
            logger.info("Model warmup inference completed",
                       first_inference_time_ms=round(self.first_inference_time_ms, 2))
            
            return True
            
        except Exception as e:
            logger.error("Model warmup inference failed", error=str(e))
            return False
    
    async def load_model(self) -> bool:
        """Load model asynchronously."""
        if self.model is not None:
            return True
            
        try:
            # Run model loading in thread pool
            success = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._load_model_sync
            )
            
            if success and self.config.warmup_enabled:
                # Perform warmup inference
                warmup_success = await asyncio.get_event_loop().run_in_executor(
                    self.executor, self._dummy_inference_sync
                )
                
                if warmup_success:
                    self.warmup_completed = True
                    logger.info("Embedding model warmup completed",
                               total_time_ms=round(self.load_time_ms + self.first_inference_time_ms, 2))
            
            return success
            
        except Exception as e:
            logger.error("Failed to load embedding model asynchronously", error=str(e))
            return False
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        normalized_text = text.strip().lower()
        return hashlib.md5(normalized_text.encode('utf-8')).hexdigest()
    
    def _embed_texts_sync(self, texts: List[str]) -> List[List[float]]:
        """Embed texts synchronously (called in thread pool)."""
        if self.model is None:
            raise RuntimeError("Embedding model not loaded")
            
        try:
            embeddings = self.model.encode(texts, normalize_embeddings=True)
            return embeddings.tolist()
            
        except Exception as e:
            logger.error("Embedding generation failed", error=str(e), text_count=len(texts))
            raise
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed texts with caching and performance optimization.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
            
        embed_start = time.time()
        
        # Check cache for each text
        cached_embeddings = {}
        texts_to_embed = []
        text_indices = []
        
        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            
            if self.cache and cache_key in self.cache:
                cached_embeddings[i] = self.cache[cache_key]
            else:
                texts_to_embed.append(text)
                text_indices.append(i)
        
        # Generate embeddings for uncached texts
        new_embeddings = []
        if texts_to_embed:
            try:
                # Run embedding in thread pool with timeout
                new_embeddings = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        self.executor, self._embed_texts_sync, texts_to_embed
                    ),
                    timeout=self.config.embedding_timeout
                )
                
                # Cache new embeddings
                if self.cache:
                    for text, embedding in zip(texts_to_embed, new_embeddings):
                        cache_key = self._get_cache_key(text)
                        self.cache[cache_key] = embedding
                
            except asyncio.TimeoutError:
                logger.error("Embedding generation timed out",
                           timeout=self.config.embedding_timeout,
                           text_count=len(texts_to_embed))
                raise TimeoutError(f"Embedding timed out after {self.config.embedding_timeout}s")
            except Exception as e:
                logger.error("Embedding generation failed", error=str(e))
                raise
        
        # Combine cached and new embeddings in original order
        result_embeddings = []
        new_embedding_index = 0
        
        for i in range(len(texts)):
            if i in cached_embeddings:
                result_embeddings.append(cached_embeddings[i])
            else:
                result_embeddings.append(new_embeddings[new_embedding_index])
                new_embedding_index += 1
        
        embed_time_ms = (time.time() - embed_start) * 1000
        
        logger.debug("Text embedding completed",
                    text_count=len(texts),
                    cached_count=len(cached_embeddings),
                    new_count=len(texts_to_embed),
                    embed_time_ms=round(embed_time_ms, 2))
        
        return result_embeddings
    
    async def health_check(self) -> Dict[str, Any]:
        """Get embedding service health status."""
        return {
            "service": "embedding_singleton",
            "model_loaded": self.model is not None,
            "warmup_completed": self.warmup_completed,
            "load_time_ms": self.load_time_ms,
            "first_inference_time_ms": self.first_inference_time_ms,
            "cache_size": len(self.cache) if self.cache else 0,
            "max_cache_size": self.config.embedding_cache_size if CACHETOOLS_AVAILABLE else "unlimited",
            "executor_active": self.executor is not None and not self.executor._shutdown
        }


class VectorStoreSingleton:
    """Process-level singleton for vector store clients with connection pooling."""
    
    _instance: Optional['VectorStoreSingleton'] = None
    _lock = threading.Lock()
    
    def __init__(self, config: VectorConfig):
        """Initialize vector store singleton."""
        self.config = config
        self.vector_store = None
        self.connected = False
        self.warmup_completed = False
        self.connection_time_ms = 0
        self.first_search_time_ms = 0
        
        logger.info("VectorStoreSingleton initialized", config={
            "provider": config.vector_db_provider,
            "url": config.vector_db_url,
            "collection": config.vector_collection_name
        })
    
    @classmethod
    def get_instance(cls, config: Optional[VectorConfig] = None) -> 'VectorStoreSingleton':
        """Get or create singleton instance (thread-safe)."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    if config is None:
                        config = VectorConfig.from_environment()
                    cls._instance = cls(config)
        return cls._instance
    
    async def connect(self) -> bool:
        """Connect to vector store with connection pooling."""
        if self.connected and self.vector_store is not None:
            return True
            
        if not VECTOR_STORES_AVAILABLE:
            logger.error("Vector store implementations not available")
            return False
            
        connect_start = time.time()
        
        try:
            provider = self.config.vector_db_provider.lower()
            
            if provider == "qdrant":
                self.vector_store = QdrantVectorStore(
                    url=self.config.vector_db_url,
                    api_key=self.config.vector_db_api_key,
                    collection=self.config.vector_collection_name,
                    vector_size=self.config.embedding_dimension
                )
            elif provider == "chroma":
                self.vector_store = ChromaVectorStore(
                    collection_name=self.config.vector_collection_name
                )
            else:
                logger.warning(f"Unknown vector provider {provider}, falling back to in-memory")
                self.vector_store = InMemoryVectorStore()
            
            self.connection_time_ms = (time.time() - connect_start) * 1000
            self.connected = True
            
            logger.info("Vector store connected successfully",
                       provider=provider,
                       connection_time_ms=round(self.connection_time_ms, 2))
            
            return True
            
        except Exception as e:
            logger.error("Vector store connection failed",
                        provider=self.config.vector_db_provider,
                        error=str(e))
            self.connected = False
            return False
    
    async def warmup_search(self) -> bool:
        """Perform warmup searches to prime caches."""
        if not self.connected or self.vector_store is None:
            return False
            
        try:
            warmup_start = time.time()
            
            # Create dummy embedding for warmup
            dummy_embedding = [0.1] * self.config.embedding_dimension
            
            # Perform multiple warmup searches
            for i in range(self.config.warmup_queries):
                try:
                    await asyncio.wait_for(
                        self.vector_store.search(
                            query_embedding=dummy_embedding,
                            top_k=1
                        ),
                        timeout=1.0
                    )
                except Exception as e:
                    logger.debug(f"Warmup search {i+1} failed (expected): {e}")
                    continue
            
            self.first_search_time_ms = (time.time() - warmup_start) * 1000
            self.warmup_completed = True
            
            logger.info("Vector store warmup completed",
                       warmup_queries=self.config.warmup_queries,
                       warmup_time_ms=round(self.first_search_time_ms, 2))
            
            return True
            
        except Exception as e:
            logger.error("Vector store warmup failed", error=str(e))
            return False
    
    async def search(self, query_embedding: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Perform vector search with timeout and performance logging.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of search results
        """
        if not self.connected or self.vector_store is None:
            raise RuntimeError("Vector store not connected")
            
        search_start = time.time()
        
        try:
            # Perform search with timeout
            results = await asyncio.wait_for(
                self.vector_store.search(
                    query_embedding=query_embedding,
                    top_k=top_k
                ),
                timeout=self.config.search_timeout
            )
            
            search_time_ms = (time.time() - search_start) * 1000
            
            logger.debug("Vector search completed",
                        result_count=len(results) if results else 0,
                        search_time_ms=round(search_time_ms, 2),
                        top_k=top_k)
            
            return results or []
            
        except asyncio.TimeoutError:
            logger.error("Vector search timed out",
                        timeout=self.config.search_timeout,
                        top_k=top_k)
            raise TimeoutError(f"Vector search timed out after {self.config.search_timeout}s")
        except Exception as e:
            logger.error("Vector search failed", error=str(e), top_k=top_k)
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Get vector store health status."""
        return {
            "service": "vector_store_singleton",
            "provider": self.config.vector_db_provider,
            "connected": self.connected,
            "warmup_completed": self.warmup_completed,
            "connection_time_ms": self.connection_time_ms,
            "first_search_time_ms": self.first_search_time_ms,
            "collection": self.config.vector_collection_name
        }


class VectorSingletonService:
    """High-level vector service combining embedding and vector store singletons."""
    
    def __init__(self, config: Optional[VectorConfig] = None):
        """Initialize vector singleton service."""
        self.config = config or VectorConfig.from_environment()
        self.embedding_singleton = EmbeddingSingleton.get_instance(self.config)
        self.vector_store_singleton = VectorStoreSingleton.get_instance(self.config)
        self.initialization_completed = False
        
        logger.info("VectorSingletonService created")
    
    async def initialize(self) -> bool:
        """Initialize all components with full warmup."""
        if self.initialization_completed:
            return True
            
        init_start = time.time()
        
        try:
            # Initialize embedding model
            embedding_success = await self.embedding_singleton.load_model()
            if not embedding_success:
                logger.error("Failed to initialize embedding model")
                return False
            
            # Initialize vector store
            vector_success = await self.vector_store_singleton.connect()
            if not vector_success:
                logger.error("Failed to initialize vector store")
                return False
            
            # Perform warmup if enabled
            if self.config.warmup_enabled:
                warmup_success = await self.vector_store_singleton.warmup_search()
                if not warmup_success:
                    logger.warning("Vector store warmup failed, but continuing")
            
            init_time_ms = (time.time() - init_start) * 1000
            self.initialization_completed = True
            
            logger.info("Vector singleton service initialized successfully",
                       init_time_ms=round(init_time_ms, 2),
                       warmup_enabled=self.config.warmup_enabled)
            
            return True
            
        except Exception as e:
            logger.error("Vector singleton service initialization failed", error=str(e))
            return False
    
    async def embed_and_search(self, query: str, top_k: int = 10) -> Tuple[List[List[float]], List[Dict[str, Any]]]:
        """
        Complete embed and search pipeline with performance logging.
        
        Args:
            query: Query text
            top_k: Number of results
            
        Returns:
            Tuple of (embeddings, search_results)
        """
        if not self.initialization_completed:
            raise RuntimeError("Vector service not initialized")
            
        pipeline_start = time.time()
        
        try:
            # TFTI: Time-to-first-inference (embedding)
            tfti_start = time.time()
            embeddings = await self.embedding_singleton.embed_texts([query])
            tfti_ms = (time.time() - tfti_start) * 1000
            
            # TTS: Time-to-search
            tts_start = time.time()
            results = await self.vector_store_singleton.search(embeddings[0], top_k)
            tts_ms = (time.time() - tts_start) * 1000
            
            total_time_ms = (time.time() - pipeline_start) * 1000
            
            logger.info("Vector pipeline completed",
                       query=query[:100] + "..." if len(query) > 100 else query,
                       tfti_ms=round(tfti_ms, 2),
                       tts_ms=round(tts_ms, 2),
                       total_time_ms=round(total_time_ms, 2),
                       result_count=len(results))
            
            return embeddings, results
            
        except Exception as e:
            logger.error("Vector pipeline failed", query=query[:100], error=str(e))
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        embedding_health = await self.embedding_singleton.health_check()
        vector_health = await self.vector_store_singleton.health_check()
        
        return {
            "service": "vector_singleton_service",
            "initialized": self.initialization_completed,
            "embedding": embedding_health,
            "vector_store": vector_health,
            "config": {
                "embedding_model": self.config.embedding_model,
                "vector_provider": self.config.vector_db_provider,
                "warmup_enabled": self.config.warmup_enabled
            }
        }


# Global service instance
_vector_singleton_service: Optional[VectorSingletonService] = None

async def get_vector_singleton_service() -> VectorSingletonService:
    """Get or create global vector singleton service."""
    global _vector_singleton_service
    
    if _vector_singleton_service is None:
        _vector_singleton_service = VectorSingletonService()
        await _vector_singleton_service.initialize()
    
    return _vector_singleton_service

async def get_vector_singleton_health() -> Dict[str, Any]:
    """Get vector singleton service health for /health endpoint."""
    try:
        service = await get_vector_singleton_service()
        return await service.health_check()
    except Exception as e:
        logger.error("Failed to get vector singleton health", error=str(e))
        return {
            "service": "vector_singleton_service",
            "status": "error",
            "error": str(e),
            "initialized": False
        }
