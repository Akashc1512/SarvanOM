"""
Vector Singleton Service - Process-Level Singletons for Vector Operations
========================================================================

Eliminates cold-start penalty for vector operations by providing:
- Process-level singleton for embedding model
- Process-level singleton for vector store client
- In-memory LRU cache for embeddings with TTL
- Background warmup automation
- Performance metrics (TFTI, TTS)

Maps to Phase I2 requirements for sub-2s vector query performance.
"""

import os
import asyncio
import threading
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import lru_cache
import structlog
import hashlib

# Optional dependencies with graceful fallback
try:
    import sentence_transformers
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    sentence_transformers = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    chromadb = None
    CHROMADB_AVAILABLE = False

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams
    QDRANT_AVAILABLE = True
except ImportError:
    QdrantClient = None
    Distance = None
    VectorParams = None
    QDRANT_AVAILABLE = False

logger = structlog.get_logger(__name__)


@dataclass
class VectorConfig:
    """Vector service configuration from environment variables."""
    
    # Embedding Configuration
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_cache_size: int = 1000
    embedding_cache_ttl: int = 3600  # 1 hour
    
    # Vector Store Configuration
    vector_db_provider: str = "chroma"  # chroma, qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    vector_collection_name: str = "sarvanom_embeddings"
    chroma_persist_directory: str = "./chroma_db"
    
    # Performance Configuration
    vector_warmup_enabled: bool = True
    warmup_timeout: float = 30.0
    query_timeout: float = 2.0
    
    @classmethod
    def from_environment(cls) -> 'VectorConfig':
        """Load configuration from environment variables."""
        # Phase J3: Intelligent dev/prod environment detection
        environment = os.getenv('ENVIRONMENT', 'development').lower()
        default_provider = 'chroma' if environment in ['development', 'dev', 'local'] else 'qdrant'
        
        return cls(
            embedding_model=os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'),
            embedding_cache_size=int(os.getenv('EMBEDDING_CACHE_SIZE', '1000')),
            embedding_cache_ttl=int(os.getenv('EMBEDDING_CACHE_TTL', '3600')),
            vector_db_provider=os.getenv('VECTOR_DB_PROVIDER', default_provider).lower(),
            qdrant_url=os.getenv('QDRANT_URL', 'http://localhost:6333'),
            qdrant_api_key=os.getenv('QDRANT_API_KEY'),
            vector_collection_name=os.getenv('VECTOR_COLLECTION_NAME', 'sarvanom_embeddings'),
            chroma_persist_directory=os.getenv('CHROMA_PERSIST_DIRECTORY', './chroma_db'),
            vector_warmup_enabled=os.getenv('VECTOR_WARMUP_ENABLED', 'true').lower() == 'true',
            warmup_timeout=float(os.getenv('VECTOR_WARMUP_TIMEOUT', '30.0')),
            query_timeout=float(os.getenv('VECTOR_QUERY_TIMEOUT', '2.0'))
        )
    
    def get_redacted_config(self) -> Dict[str, Any]:
        """Return configuration with sensitive data redacted."""
        return {
            'embedding_model': self.embedding_model,
            'embedding_cache_size': self.embedding_cache_size,
            'embedding_cache_ttl': self.embedding_cache_ttl,
            'vector_db_provider': self.vector_db_provider,
            'qdrant_url': self.qdrant_url,
            'qdrant_api_key': '[REDACTED]' if self.qdrant_api_key else None,
            'vector_collection_name': self.vector_collection_name,
            'chroma_persist_directory': self.chroma_persist_directory,
            'vector_warmup_enabled': self.vector_warmup_enabled,
            'warmup_timeout': self.warmup_timeout,
            'query_timeout': self.query_timeout
        }


@dataclass
class CacheEntry:
    """Embedding cache entry with TTL."""
    embedding: List[float]
    created_at: datetime
    hits: int = 0
    
    def is_expired(self, ttl_seconds: int) -> bool:
        """Check if cache entry is expired."""
        return datetime.now() - self.created_at > timedelta(seconds=ttl_seconds)


@dataclass
class PerformanceMetrics:
    """Performance metrics for vector operations."""
    tfti_ms: float = 0.0  # Time to first inference
    tts_ms: float = 0.0   # Time to search
    cache_hits: int = 0
    cache_misses: int = 0
    total_queries: int = 0
    avg_embedding_time_ms: float = 0.0
    avg_search_time_ms: float = 0.0
    warmup_completed: bool = False
    warmup_duration_ms: float = 0.0
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'tfti_ms': self.tfti_ms,
            'tts_ms': self.tts_ms,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'total_queries': self.total_queries,
            'cache_hit_rate': self.cache_hit_rate,
            'avg_embedding_time_ms': self.avg_embedding_time_ms,
            'avg_search_time_ms': self.avg_search_time_ms,
            'warmup_completed': self.warmup_completed,
            'warmup_duration_ms': self.warmup_duration_ms
        }


class EmbeddingSingleton:
    """
    Process-level singleton for embedding model.
    
    Features:
    - Thread-safe initialization
    - LRU cache with TTL
    - Performance metrics collection
    - Graceful fallback if model unavailable
    """
    
    _instance: Optional['EmbeddingSingleton'] = None
    _lock = threading.Lock()
    
    def __new__(cls, config: VectorConfig) -> 'EmbeddingSingleton':
        """Thread-safe singleton implementation."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, config: VectorConfig):
        """Initialize embedding singleton."""
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.config = config
        self.model = None
        self.cache: Dict[str, CacheEntry] = {}
        self.metrics = PerformanceMetrics()
        self._model_loaded = False
        self._warmup_completed = False
        self._lock = threading.Lock()
        self._initialized = True
        
        logger.info("EmbeddingSingleton initialized", 
                   config=config.get_redacted_config())
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for consistent caching."""
        return text.strip().lower()
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        normalized = self._normalize_text(text)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _cleanup_expired_cache(self):
        """Remove expired cache entries."""
        current_time = datetime.now()
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired(self.config.embedding_cache_ttl)
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.debug("Cleaned up expired cache entries", 
                        count=len(expired_keys),
                        remaining=len(self.cache))
    
    def _manage_cache_size(self):
        """Ensure cache doesn't exceed size limit."""
        while len(self.cache) > self.config.embedding_cache_size:
            # Remove least recently used (lowest hits)
            lru_key = min(self.cache.keys(), 
                         key=lambda k: (self.cache[k].hits, self.cache[k].created_at))
            del self.cache[lru_key]
    
    async def load_model(self) -> bool:
        """Load embedding model with timeout."""
        if self._model_loaded:
            return True
            
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.warning("sentence-transformers not available, embedding disabled")
            return False
        
        start_time = time.time()
        
        try:
            # Load model with timeout
            load_task = asyncio.to_thread(
                sentence_transformers.SentenceTransformer,
                self.config.embedding_model
            )
            
            self.model = await asyncio.wait_for(
                load_task,
                timeout=self.config.warmup_timeout
            )
            
            self._model_loaded = True
            load_time_ms = (time.time() - start_time) * 1000
            
            # Record TFTI (Time to First Inference)
            if self.metrics.tfti_ms == 0.0:
                self.metrics.tfti_ms = load_time_ms
            
            logger.info("Embedding model loaded successfully",
                       model=self.config.embedding_model,
                       load_time_ms=round(load_time_ms, 2))
            
            return True
            
        except asyncio.TimeoutError:
            logger.error("Embedding model load timeout",
                        model=self.config.embedding_model,
                        timeout=self.config.warmup_timeout)
            return False
        except Exception as e:
            logger.error("Failed to load embedding model",
                        model=self.config.embedding_model,
                        error=str(e))
            return False
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text (alias for compatibility)."""
        return await self.embed_text(text)
    
    async def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for text with caching.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if failed
        """
        if not text or not text.strip():
            return None
        
        start_time = time.time()
        cache_key = self._get_cache_key(text)
        
        # Check cache first
        with self._lock:
            self._cleanup_expired_cache()
            
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                entry.hits += 1
                self.metrics.cache_hits += 1
                
                logger.debug("Cache hit for embedding",
                           cache_key=cache_key[:8],
                           hits=entry.hits)
                
                return entry.embedding
        
        # Cache miss - generate embedding
        self.metrics.cache_misses += 1
        
        if not self._model_loaded:
            await self.load_model()
        
        if not self._model_loaded or self.model is None:
            return None
        
        try:
            # Generate embedding
            embed_task = asyncio.to_thread(
                self.model.encode,
                [text],
                convert_to_tensor=False
            )
            
            embeddings = await asyncio.wait_for(
                embed_task,
                timeout=self.config.query_timeout
            )
            
            embedding = embeddings[0].tolist()
            embed_time_ms = (time.time() - start_time) * 1000
            
            # Update metrics
            self.metrics.total_queries += 1
            self.metrics.avg_embedding_time_ms = (
                (self.metrics.avg_embedding_time_ms * (self.metrics.total_queries - 1) + embed_time_ms) 
                / self.metrics.total_queries
            )
            
            # Cache the result
            with self._lock:
                self.cache[cache_key] = CacheEntry(
                    embedding=embedding,
                    created_at=datetime.now(),
                    hits=1
                )
                self._manage_cache_size()
            
            logger.debug("Generated new embedding",
                        text_length=len(text),
                        embedding_dim=len(embedding),
                        time_ms=round(embed_time_ms, 2))
            
            return embedding
            
        except asyncio.TimeoutError:
            logger.warning("Embedding generation timeout",
                          text_length=len(text),
                          timeout=self.config.query_timeout)
            return None
        except Exception as e:
            logger.error("Embedding generation failed",
                        text_length=len(text),
                        error=str(e))
            return None
    
    async def warmup(self) -> bool:
        """Warmup embedding model with dummy text."""
        if self._warmup_completed:
            return True
        
        start_time = time.time()
        
        # Load model
        if not await self.load_model():
            return False
        
        # Generate dummy embedding for warmup
        dummy_texts = [
            "This is a test query for warming up the embedding model.",
            "Vector search performance optimization.",
            "Knowledge graph integration test."
        ]
        
        warmup_success = True
        for text in dummy_texts:
            embedding = await self.embed_text(text)
            if embedding is None:
                warmup_success = False
                break
        
        warmup_time_ms = (time.time() - start_time) * 1000
        self.metrics.warmup_duration_ms = warmup_time_ms
        self.metrics.warmup_completed = warmup_success
        self._warmup_completed = warmup_success
        
        if warmup_success:
            logger.info("Embedding model warmup completed",
                       warmup_time_ms=round(warmup_time_ms, 2),
                       cache_entries=len(self.cache))
        else:
            logger.error("Embedding model warmup failed",
                        warmup_time_ms=round(warmup_time_ms, 2))
        
        return warmup_success
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get embedding service health status."""
        return {
            'model_loaded': self._model_loaded,
            'warmup_completed': self._warmup_completed,
            'cache_size': len(self.cache),
            'cache_capacity': self.config.embedding_cache_size,
            'model_name': self.config.embedding_model,
            'metrics': self.metrics.to_dict()
        }


class VectorStoreSingleton:
    """
    Process-level singleton for vector store client.
    
    Features:
    - Support for Qdrant and Chroma
    - Connection pooling and health checks
    - Performance metrics collection
    - Graceful degradation on failures
    """
    
    _instance: Optional['VectorStoreSingleton'] = None
    _lock = threading.Lock()
    
    def __new__(cls, config: VectorConfig) -> 'VectorStoreSingleton':
        """Thread-safe singleton implementation."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, config: VectorConfig):
        """Initialize vector store singleton."""
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.config = config
        self.client = None
        self.collection = None
        self._connected = False
        self._warmup_completed = False
        self._lock = threading.Lock()
        self._initialized = True
        
        logger.info("VectorStoreSingleton initialized",
                   provider=config.vector_db_provider,
                   config=config.get_redacted_config())
    
    async def connect(self) -> bool:
        """Connect to vector store."""
        if self._connected:
            return True
        
        try:
            if self.config.vector_db_provider == "qdrant":
                return await self._connect_qdrant()
            elif self.config.vector_db_provider == "chroma":
                return await self._connect_chroma()
            else:
                logger.error("Unsupported vector database provider",
                           provider=self.config.vector_db_provider)
                return False
                
        except Exception as e:
            logger.error("Vector store connection failed",
                        provider=self.config.vector_db_provider,
                        error=str(e))
            return False
    
    async def _connect_qdrant(self) -> bool:
        """Connect to Qdrant vector database with production optimizations."""
        if not QDRANT_AVAILABLE:
            logger.warning("Qdrant client not available, install qdrant-client")
            return False
        
        try:
            # Initialize Qdrant client with production settings (Phase J2)
            connect_task = asyncio.to_thread(
                QdrantClient,
                url=self.config.qdrant_url,
                api_key=self.config.qdrant_api_key,
                timeout=self.config.query_timeout,
                # Production optimizations
                prefer_grpc=True,  # Use gRPC for better performance
                https=True if self.config.qdrant_url.startswith('https') else False
            )
            
            self.client = await asyncio.wait_for(
                connect_task,
                timeout=self.config.warmup_timeout
            )
            
            # Test connection and get collection info
            info_task = asyncio.to_thread(self.client.get_collections)
            collections_info = await asyncio.wait_for(info_task, timeout=5.0)
            
            # Ensure collection exists with proper configuration
            await self._ensure_qdrant_collection_optimal()
            
            self._connected = True
            
            logger.info("Connected to Qdrant with production optimizations",
                       url=self.config.qdrant_url,
                       collection=self.config.vector_collection_name,
                       collections_count=len(collections_info.collections))
            
            return True
            
        except Exception as e:
            logger.error("Qdrant connection failed",
                        url=self.config.qdrant_url,
                        error=str(e))
            return False
    
    async def _ensure_qdrant_collection_optimal(self) -> None:
        """Ensure Qdrant collection exists with optimal production settings."""
        try:
            from qdrant_client.models import VectorParams, Distance
            
            collection_name = self.config.vector_collection_name
            
            # Check if collection exists
            collections_task = asyncio.to_thread(self.client.get_collections)
            collections_info = await collections_task
            
            collection_exists = any(
                col.name == collection_name 
                for col in collections_info.collections
            )
            
            if not collection_exists:
                # Create collection with optimal settings
                vector_size = 384  # Standard sentence-transformers dimension
                
                create_task = asyncio.to_thread(
                    self.client.create_collection,
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE,
                        # Production optimizations
                        hnsw_config={
                            "m": 16,  # Number of bi-directional links for each node
                            "ef_construct": 200,  # Size of dynamic candidate list
                            "full_scan_threshold": 10000  # Threshold for full scan
                        },
                        on_disk=True  # Store vectors on disk for large collections
                    )
                )
                
                await create_task
                
                logger.info("Created Qdrant collection with production settings",
                           collection=collection_name,
                           vector_size=vector_size,
                           distance="COSINE")
            else:
                # Verify collection configuration
                collection_info_task = asyncio.to_thread(
                    self.client.get_collection,
                    collection_name
                )
                collection_info = await collection_info_task
                
                logger.info("Qdrant collection verified",
                           collection=collection_name,
                           vectors_count=collection_info.vectors_count,
                           points_count=collection_info.points_count)
        
        except Exception as e:
            logger.warning("Could not optimize Qdrant collection",
                          collection=self.config.vector_collection_name,
                          error=str(e))
    
    async def _connect_chroma(self) -> bool:
        """Connect to Chroma vector database."""
        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB not available, install chromadb")
            return False
        
        try:
            # Initialize Chroma client
            connect_task = asyncio.to_thread(
                chromadb.PersistentClient,
                path=self.config.chroma_persist_directory
            )
            
            self.client = await asyncio.wait_for(
                connect_task,
                timeout=self.config.warmup_timeout
            )
            
            # Get or create collection
            collection_task = asyncio.to_thread(
                self.client.get_or_create_collection,
                name=self.config.vector_collection_name
            )
            
            self.collection = await asyncio.wait_for(
                collection_task,
                timeout=5.0
            )
            
            self._connected = True
            
            logger.info("Connected to ChromaDB",
                       path=self.config.chroma_persist_directory,
                       collection=self.config.vector_collection_name)
            
            return True
            
        except Exception as e:
            logger.error("ChromaDB connection failed",
                        path=self.config.chroma_persist_directory,
                        error=str(e))
            return False
    
    async def search_similar(self, embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of similar documents with scores
        """
        if not self._connected:
            await self.connect()
        
        if not self._connected:
            return []
        
        start_time = time.time()
        
        try:
            if self.config.vector_db_provider == "qdrant":
                return await self._search_qdrant(embedding, top_k)
            elif self.config.vector_db_provider == "chroma":
                return await self._search_chroma(embedding, top_k)
            else:
                return []
                
        except asyncio.TimeoutError:
            search_time_ms = (time.time() - start_time) * 1000
            logger.warning("Vector search timeout",
                          time_ms=round(search_time_ms, 2),
                          timeout=self.config.query_timeout)
            return []
        except Exception as e:
            search_time_ms = (time.time() - start_time) * 1000
            logger.error("Vector search failed",
                        provider=self.config.vector_db_provider,
                        error=str(e),
                        time_ms=round(search_time_ms, 2))
            return []
    
    async def _search_qdrant(self, embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """Search in Qdrant vector database."""
        search_task = asyncio.to_thread(
            self.client.search,
            collection_name=self.config.vector_collection_name,
            query_vector=embedding,
            limit=top_k
        )
        
        results = await asyncio.wait_for(
            search_task,
            timeout=self.config.query_timeout
        )
        
        return [
            {
                'id': result.id,
                'score': result.score,
                'payload': result.payload or {}
            }
            for result in results
        ]
    
    async def _search_chroma(self, embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """Search in ChromaDB vector database."""
        if not self.collection:
            return []
        
        search_task = asyncio.to_thread(
            self.collection.query,
            query_embeddings=[embedding],
            n_results=top_k
        )
        
        results = await asyncio.wait_for(
            search_task,
            timeout=self.config.query_timeout
        )
        
        # Convert ChromaDB format to standard format
        documents = results.get('documents', [[]])[0]
        distances = results.get('distances', [[]])[0]
        ids = results.get('ids', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]
        
        return [
            {
                'id': doc_id,
                'score': 1.0 - distance,  # Convert distance to similarity
                'payload': {
                    'document': document,
                    'metadata': metadata or {}
                }
            }
            for doc_id, document, distance, metadata in zip(ids, documents, distances, metadatas)
        ]
    
    async def warmup(self) -> bool:
        """Warmup vector store with dummy search."""
        if self._warmup_completed:
            return True
        
        # Connect to vector store
        if not await self.connect():
            return False
        
        # Perform dummy search for warmup
        try:
            dummy_embedding = [0.1] * 384  # Standard embedding dimension
            await self.search_similar(dummy_embedding, top_k=1)
            
            self._warmup_completed = True
            logger.info("Vector store warmup completed",
                       provider=self.config.vector_db_provider)
            return True
            
        except Exception as e:
            logger.error("Vector store warmup failed",
                        provider=self.config.vector_db_provider,
                        error=str(e))
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get vector store health status."""
        return {
            'connected': self._connected,
            'warmup_completed': self._warmup_completed,
            'provider': self.config.vector_db_provider,
            'collection_name': self.config.vector_collection_name
        }


class VectorSingletonService:
    """
    Coordinated service for vector operations combining embedding and vector store.
    
    Features:
    - Coordinates embedding generation and vector search
    - Performance metrics aggregation
    - Unified health monitoring
    - Background warmup coordination
    """
    
    def __init__(self):
        """Initialize vector singleton service."""
        self.config = VectorConfig.from_environment()
        self.embedding_singleton = EmbeddingSingleton(self.config)
        self.vector_store_singleton = VectorStoreSingleton(self.config)
        self._service_initialized = False
        
        logger.info("VectorSingletonService initialized",
                   config=self.config.get_redacted_config())
    
    async def initialize(self) -> bool:
        """Initialize both embedding and vector store services."""
        if self._service_initialized:
            return True
        
        embedding_ready = await self.embedding_singleton.load_model()
        vector_ready = await self.vector_store_singleton.connect()
        
        self._service_initialized = embedding_ready or vector_ready
        
        logger.info("VectorSingletonService initialization complete",
                   embedding_ready=embedding_ready,
                   vector_ready=vector_ready,
                   service_ready=self._service_initialized)
        
        return self._service_initialized
    
    def get_health(self) -> Dict[str, Any]:
        """Get comprehensive health status for the vector service."""
        embedding_health = self.embedding_singleton.get_health_status()
        vector_health = self.vector_store_singleton.get_health_status()
        
        # Determine overall status
        embedding_ok = embedding_health.get('model_loaded', False)
        vector_ok = vector_health.get('connected', False)
        
        if embedding_ok and vector_ok:
            status = 'healthy'
        elif embedding_ok or vector_ok:
            status = 'degraded'
        else:
            status = 'unhealthy'
        
        return {
            'status': status,
            'service_initialized': self._service_initialized,
            'provider': self.config.vector_db_provider,
            'embedding': embedding_health,
            'vector_store': vector_health,
            'config': {
                'model': self.config.embedding_model,
                'collection': self.config.vector_collection_name,
                'cache_size': self.config.embedding_cache_size
            }
        }
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text (delegates to embedding singleton)."""
        return await self.embedding_singleton.embed_text(text)
    
    async def warmup(self) -> bool:
        """Perform complete warmup of vector services."""
        if not self.config.vector_warmup_enabled:
            logger.info("Vector warmup disabled by configuration")
            return True
        
        start_time = time.time()
        
        # Initialize services
        await self.initialize()
        
        # Warmup both services
        embedding_warmup = await self.embedding_singleton.warmup()
        vector_warmup = await self.vector_store_singleton.warmup()
        
        warmup_time_ms = (time.time() - start_time) * 1000
        warmup_success = embedding_warmup or vector_warmup
        
        # Record TTS (Time to Search) metric
        if warmup_success and self.embedding_singleton.metrics.tts_ms == 0.0:
            self.embedding_singleton.metrics.tts_ms = warmup_time_ms
        
        logger.info("Vector services warmup completed",
                   embedding_success=embedding_warmup,
                   vector_success=vector_warmup,
                   overall_success=warmup_success,
                   warmup_time_ms=round(warmup_time_ms, 2))
        
        return warmup_success
    
    async def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform semantic search with embedding and vector search.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            
        Returns:
            List of search results with scores
        """
        start_time = time.time()
        
        # Generate embedding for query
        embedding = await self.embedding_singleton.embed_text(query)
        if not embedding:
            logger.warning("Failed to generate embedding for query",
                          query_length=len(query))
            return []
        
        # Search vector store
        results = await self.vector_store_singleton.search_similar(embedding, top_k)
        
        search_time_ms = (time.time() - start_time) * 1000
        
        # Update search metrics
        metrics = self.embedding_singleton.metrics
        metrics.total_queries += 1
        metrics.avg_search_time_ms = (
            (metrics.avg_search_time_ms * (metrics.total_queries - 1) + search_time_ms)
            / metrics.total_queries
        )
        
        logger.debug("Semantic search completed",
                    query_length=len(query),
                    results_count=len(results),
                    search_time_ms=round(search_time_ms, 2))
        
        return results
    
    async def health_check(self) -> Dict[str, Any]:
        """Get comprehensive health status of vector services."""
        embedding_health = self.embedding_singleton.get_health_status()
        vector_health = self.vector_store_singleton.get_health_status()
        
        overall_initialized = (
            embedding_health.get('model_loaded', False) or
            vector_health.get('connected', False)
        )
        
        return {
            'initialized': overall_initialized,
            'service_ready': self._service_initialized,
            'embedding': embedding_health,
            'vector_store': vector_health,
            'config': self.config.get_redacted_config()
        }


# Global service instance
_vector_singleton_service: Optional[VectorSingletonService] = None
_service_lock = threading.Lock()

def get_vector_singleton_service() -> VectorSingletonService:
    """Get or create global vector singleton service."""
    global _vector_singleton_service
    
    with _service_lock:
        if _vector_singleton_service is None:
            _vector_singleton_service = VectorSingletonService()
    
    return _vector_singleton_service

async def get_vector_singleton_health() -> Dict[str, Any]:
    """Get vector singleton service health for health check endpoints."""
    service = get_vector_singleton_service()
    return service.get_health()  # This is not async

async def warmup_vector_singleton() -> Dict[str, Any]:
    """Execute vector singleton warmup tasks."""
    service = get_vector_singleton_service()
    success = await service.warmup()
    
    return {
        'status': 'completed' if success else 'failed',
        'warmup_completed': success,
        'health': await service.health_check()
    }

# Export public interface
__all__ = [
    'VectorConfig',
    'VectorSingletonService',
    'get_vector_singleton_service',
    'get_vector_singleton_health',
    'warmup_vector_singleton'
]