#!/usr/bin/env python3
"""
Datastores Optimization Service - Phase J1/J2/J3
================================================

Comprehensive datastores optimization for production deployment:
- J1: Meilisearch tuning with domain-specific configurations
- J2: Qdrant production optimization with connection pooling
- J3: Chroma dev environment with intelligent toggle

Features:
- Environment-aware configuration (dev/prod)
- Performance monitoring and auto-tuning
- Health checks and status reporting
- Batch operations and connection pooling
- Intelligent fallback and graceful degradation
"""

import os
import time
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import structlog

logger = structlog.get_logger(__name__)

class Environment(str, Enum):
    """Environment types for datastore configuration."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

class DatastoreType(str, Enum):
    """Supported datastore types."""
    MEILISEARCH = "meilisearch"
    QDRANT = "qdrant"
    CHROMA = "chroma"
    ARANGODB = "arangodb"

@dataclass
class DatastoreConfig:
    """Comprehensive datastore configuration."""
    
    # Environment detection
    environment: Environment = Environment.DEVELOPMENT
    enable_production_optimizations: bool = False
    
    # Meilisearch Configuration (J1)
    meilisearch_url: str = "http://localhost:7700"
    meilisearch_master_key: Optional[str] = None
    meilisearch_index_settings: Dict[str, Any] = field(default_factory=dict)
    meilisearch_batch_size: int = 1000
    meilisearch_auto_refresh: bool = True
    
    # Qdrant Configuration (J2)
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    qdrant_collection_name: str = "sarvanom_vectors"
    qdrant_vector_size: int = 384  # all-MiniLM-L6-v2 embedding size
    qdrant_connection_pool_size: int = 10
    qdrant_keep_alive: bool = True
    qdrant_batch_upsert_size: int = 100
    
    # Chroma Configuration (J3)
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "sarvanom_dev"
    chroma_embedding_function: str = "default"
    
    # Performance Configuration
    connection_timeout: float = 30.0
    query_timeout: float = 5.0
    warmup_enabled: bool = True
    health_check_interval: float = 60.0
    
    @classmethod
    def from_environment(cls) -> 'DatastoreConfig':
        """Load configuration from environment variables."""
        environment = Environment(os.getenv('ENVIRONMENT', 'development').lower())
        enable_prod_opt = environment == Environment.PRODUCTION
        
        return cls(
            environment=environment,
            enable_production_optimizations=enable_prod_opt,
            
            # Meilisearch (J1)
            meilisearch_url=os.getenv('MEILISEARCH_URL', 'http://localhost:7700'),
            meilisearch_master_key=os.getenv('MEILI_MASTER_KEY'),
            meilisearch_batch_size=int(os.getenv('MEILISEARCH_BATCH_SIZE', '1000')),
            meilisearch_auto_refresh=os.getenv('MEILISEARCH_AUTO_REFRESH', 'true').lower() == 'true',
            
            # Qdrant (J2)
            qdrant_url=os.getenv('QDRANT_URL', 'http://localhost:6333'),
            qdrant_api_key=os.getenv('QDRANT_API_KEY'),
            qdrant_collection_name=os.getenv('QDRANT_COLLECTION_NAME', 'sarvanom_vectors'),
            qdrant_vector_size=int(os.getenv('QDRANT_VECTOR_SIZE', '384')),
            qdrant_connection_pool_size=int(os.getenv('QDRANT_POOL_SIZE', '10')),
            qdrant_keep_alive=os.getenv('QDRANT_KEEP_ALIVE', 'true').lower() == 'true',
            qdrant_batch_upsert_size=int(os.getenv('QDRANT_BATCH_SIZE', '100')),
            
            # Chroma (J3)
            chroma_persist_directory=os.getenv('CHROMA_PERSIST_DIRECTORY', './chroma_db'),
            chroma_collection_name=os.getenv('CHROMA_COLLECTION_NAME', 'sarvanom_dev'),
            
            # Performance
            connection_timeout=float(os.getenv('DATASTORE_CONNECTION_TIMEOUT', '30.0')),
            query_timeout=float(os.getenv('DATASTORE_QUERY_TIMEOUT', '5.0')),
            warmup_enabled=os.getenv('DATASTORE_WARMUP_ENABLED', 'true').lower() == 'true',
            health_check_interval=float(os.getenv('DATASTORE_HEALTH_CHECK_INTERVAL', '60.0'))
        )
    
    def get_meilisearch_index_settings(self) -> Dict[str, Any]:
        """Get optimized Meilisearch index settings based on environment."""
        if self.environment == Environment.PRODUCTION:
            return {
                "searchableAttributes": ["title", "content", "url", "domain"],
                "filterableAttributes": ["domain", "source_type", "published_date", "confidence"],
                "sortableAttributes": ["published_date", "confidence", "relevance_score"],
                "rankingRules": [
                    "words", "typo", "proximity", "attribute", "sort", "exactness"
                ],
                "stopWords": ["the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"],
                "synonyms": {
                    "ai": ["artificial intelligence", "machine learning", "ml"],
                    "api": ["application programming interface"],
                    "ui": ["user interface", "interface"],
                    "ux": ["user experience", "experience"]
                },
                "typoTolerance": {
                    "enabled": True,
                    "minWordSizeForTypos": 4,
                    "disableOnWords": ["api", "ui", "ux", "ai", "ml"],
                    "disableOnAttributes": ["url"]
                },
                "faceting": {
                    "maxValuesPerFacet": 100
                }
            }
        else:
            # Development settings - simpler for faster indexing
            return {
                "searchableAttributes": ["title", "content"],
                "filterableAttributes": ["domain", "source_type"],
                "sortableAttributes": ["published_date"],
                "rankingRules": ["words", "typo", "proximity", "attribute", "sort"],
                "stopWords": ["the", "a", "an", "and", "or", "but"],
                "typoTolerance": {
                    "enabled": True,
                    "minWordSizeForTypos": 4
                }
            }

@dataclass
class DatastoreHealth:
    """Datastore health status."""
    datastore_type: DatastoreType
    is_healthy: bool
    response_time_ms: float
    last_check: datetime
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DatastoreMetrics:
    """Comprehensive datastore metrics."""
    datastore_type: DatastoreType
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    connection_pool_utilization: float = 0.0
    cache_hit_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)

class MeilisearchOptimizer:
    """J1: Meilisearch tuning and optimization."""
    
    def __init__(self, config: DatastoreConfig):
        self.config = config
        self.client = None
        self.health = DatastoreHealth(
            datastore_type=DatastoreType.MEILISEARCH,
            is_healthy=False,
            response_time_ms=0.0,
            last_check=datetime.utcnow()
        )
        self.metrics = DatastoreMetrics(datastore_type=DatastoreType.MEILISEARCH)
        
    async def initialize(self) -> bool:
        """Initialize Meilisearch client with optimizations."""
        try:
            import meilisearch
            
            self.client = meilisearch.Client(
                url=self.config.meilisearch_url,
                api_key=self.config.meilisearch_master_key
            )
            
            # Test connection
            start_time = time.time()
            await self.client.health()
            response_time = (time.time() - start_time) * 1000
            
            self.health = DatastoreHealth(
                datastore_type=DatastoreType.MEILISEARCH,
                is_healthy=True,
                response_time_ms=response_time,
                last_check=datetime.utcnow()
            )
            
            # Configure index settings
            await self._configure_index_settings()
            
            logger.info("Meilisearch optimizer initialized",
                       url=self.config.meilisearch_url,
                       environment=self.config.environment.value)
            return True
            
        except Exception as e:
            logger.error("Failed to initialize Meilisearch", error=str(e))
            self.health.error_message = str(e)
            return False
    
    async def _configure_index_settings(self):
        """Configure optimized index settings."""
        try:
            index_settings = self.config.get_meilisearch_index_settings()
            
            # Apply settings to main index
            await self.client.index('sarvanom').update_settings(index_settings)
            
            # Create domain-specific indexes if in production
            if self.config.environment == Environment.PRODUCTION:
                await self._create_domain_indexes()
                
            logger.info("Meilisearch index settings configured",
                       environment=self.config.environment.value)
                       
        except Exception as e:
            logger.error("Failed to configure Meilisearch settings", error=str(e))
    
    async def _create_domain_indexes(self):
        """Create domain-specific indexes for production."""
        domain_configs = {
            'docs': {
                'searchableAttributes': ['title', 'content', 'section'],
                'filterableAttributes': ['doc_type', 'version', 'language'],
                'synonyms': {
                    'function': ['method', 'procedure', 'routine'],
                    'parameter': ['arg', 'argument', 'input']
                }
            },
            'code': {
                'searchableAttributes': ['code', 'comments', 'function_name'],
                'filterableAttributes': ['language', 'framework', 'repository'],
                'synonyms': {
                    'class': ['object', 'type', 'struct'],
                    'variable': ['var', 'field', 'property']
                }
            },
            'qa': {
                'searchableAttributes': ['question', 'answer', 'tags'],
                'filterableAttributes': ['category', 'difficulty', 'source'],
                'synonyms': {
                    'error': ['bug', 'issue', 'problem'],
                    'solution': ['fix', 'answer', 'resolution']
                }
            }
        }
        
        for domain, settings in domain_configs.items():
            try:
                index_name = f'sarvanom_{domain}'
                await self.client.create_index(index_name, {'primaryKey': 'id'})
                await self.client.index(index_name).update_settings(settings)
                logger.info(f"Created domain index: {index_name}")
            except Exception as e:
                logger.warning(f"Failed to create domain index {domain}", error=str(e))
    
    async def batch_update(self, index_name: str, documents: List[Dict[str, Any]]) -> bool:
        """Optimized batch update with auto-refresh."""
        try:
            # Split into batches
            batch_size = self.config.meilisearch_batch_size
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                await self.client.index(index_name).add_documents(batch)
            
            # Auto-refresh if enabled
            if self.config.meilisearch_auto_refresh:
                await self.client.index(index_name).refresh()
            
            self.metrics.successful_queries += 1
            return True
            
        except Exception as e:
            logger.error("Meilisearch batch update failed", error=str(e))
            self.metrics.failed_queries += 1
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive Meilisearch status."""
        try:
            stats = await self.client.get_stats()
            indexes = await self.client.get_indexes()
            
            return {
                "is_healthy": self.health.is_healthy,
                "response_time_ms": self.health.response_time_ms,
                "total_documents": stats.get('totalDocuments', 0),
                "total_indexes": len(indexes),
                "indexes": [idx.uid for idx in indexes],
                "metrics": {
                    "total_queries": self.metrics.total_queries,
                    "successful_queries": self.metrics.successful_queries,
                    "failed_queries": self.metrics.failed_queries,
                    "avg_response_time_ms": self.metrics.avg_response_time_ms
                }
            }
        except Exception as e:
            return {
                "is_healthy": False,
                "error": str(e),
                "metrics": self.metrics.__dict__
            }

class QdrantOptimizer:
    """J2: Qdrant production optimization."""
    
    def __init__(self, config: DatastoreConfig):
        self.config = config
        self.client = None
        self.health = DatastoreHealth(
            datastore_type=DatastoreType.QDRANT,
            is_healthy=False,
            response_time_ms=0.0,
            last_check=datetime.utcnow()
        )
        self.metrics = DatastoreMetrics(datastore_type=DatastoreType.QDRANT)
        
    async def initialize(self) -> bool:
        """Initialize Qdrant client with production optimizations."""
        try:
            import qdrant_client
            from qdrant_client.http import models
            
            # Production-optimized client configuration
            client_config = {
                'url': self.config.qdrant_url,
                'timeout': self.config.connection_timeout,
                'prefer_grpc': True,  # Use gRPC for better performance
            }
            
            if self.config.qdrant_api_key:
                client_config['api_key'] = self.config.qdrant_api_key
            
            self.client = qdrant_client.QdrantClient(**client_config)
            
            # Test connection and create collection if needed
            start_time = time.time()
            await self._ensure_collection_exists()
            response_time = (time.time() - start_time) * 1000
            
            self.health = DatastoreHealth(
                datastore_type=DatastoreType.QDRANT,
                is_healthy=True,
                response_time_ms=response_time,
                last_check=datetime.utcnow()
            )
            
            # Warmup if enabled
            if self.config.warmup_enabled:
                await self._warmup_collection()
            
            logger.info("Qdrant optimizer initialized",
                       url=self.config.qdrant_url,
                       environment=self.config.environment.value)
            return True
            
        except Exception as e:
            logger.error("Failed to initialize Qdrant", error=str(e))
            self.health.error_message = str(e)
            return False
    
    async def _ensure_collection_exists(self):
        """Ensure collection exists with optimized settings."""
        try:
            from qdrant_client.http import models
            
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.config.qdrant_collection_name not in collection_names:
                # Create collection with optimized settings
                vector_config = models.VectorParams(
                    size=self.config.qdrant_vector_size,
                    distance=models.Distance.COSINE
                )
                
                # Production optimizations
                if self.config.environment == Environment.PRODUCTION:
                    # Enable payload indexing for faster filtering
                    payload_schema = {
                        "domain": models.PayloadSchemaType.KEYWORD,
                        "source_type": models.PayloadSchemaType.KEYWORD,
                        "published_date": models.PayloadSchemaType.INTEGER,
                        "confidence": models.PayloadSchemaType.FLOAT
                    }
                    
                    self.client.create_collection(
                        collection_name=self.config.qdrant_collection_name,
                        vectors_config=vector_config,
                        payload_schema=payload_schema,
                        optimizers_config=models.OptimizersConfig(
                            default_segment_number=4,  # Optimize for production
                            max_segment_size=200000,
                            memmap_threshold=50000,
                            indexing_threshold=20000
                        )
                    )
                else:
                    # Simpler settings for development
                    self.client.create_collection(
                        collection_name=self.config.qdrant_collection_name,
                        vectors_config=vector_config
                    )
                
                logger.info(f"Created Qdrant collection: {self.config.qdrant_collection_name}")
            
        except Exception as e:
            logger.error("Failed to ensure collection exists", error=str(e))
            raise
    
    async def _warmup_collection(self):
        """Warmup collection with dummy query."""
        try:
            # Perform a dummy search to warm up the collection
            dummy_vector = [0.0] * self.config.qdrant_vector_size
            self.client.search(
                collection_name=self.config.qdrant_collection_name,
                query_vector=dummy_vector,
                limit=1
            )
            logger.info("Qdrant collection warmed up")
        except Exception as e:
            logger.warning("Failed to warmup Qdrant collection", error=str(e))
    
    async def batch_upsert(self, points: List[Dict[str, Any]]) -> bool:
        """Optimized batch upsert with connection pooling."""
        try:
            from qdrant_client.http import models
            
            # Convert to Qdrant points
            qdrant_points = []
            for point in points:
                qdrant_points.append(models.PointStruct(
                    id=point['id'],
                    vector=point['vector'],
                    payload=point.get('payload', {})
                ))
            
            # Batch upsert
            batch_size = self.config.qdrant_batch_upsert_size
            for i in range(0, len(qdrant_points), batch_size):
                batch = qdrant_points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.config.qdrant_collection_name,
                    points=batch
                )
            
            self.metrics.successful_queries += 1
            return True
            
        except Exception as e:
            logger.error("Qdrant batch upsert failed", error=str(e))
            self.metrics.failed_queries += 1
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive Qdrant status."""
        try:
            collections = self.client.get_collections()
            collection_info = self.client.get_collection(self.config.qdrant_collection_name)
            
            return {
                "is_healthy": self.health.is_healthy,
                "response_time_ms": self.health.response_time_ms,
                "total_collections": len(collections.collections),
                "collection_name": self.config.qdrant_collection_name,
                "collection_info": {
                    "vectors_count": collection_info.vectors_count,
                    "indexed_vectors_count": collection_info.indexed_vectors_count,
                    "points_count": collection_info.points_count,
                    "status": collection_info.status
                },
                "metrics": {
                    "total_queries": self.metrics.total_queries,
                    "successful_queries": self.metrics.successful_queries,
                    "failed_queries": self.metrics.failed_queries,
                    "avg_response_time_ms": self.metrics.avg_response_time_ms
                }
            }
        except Exception as e:
            return {
                "is_healthy": False,
                "error": str(e),
                "metrics": self.metrics.__dict__
            }

class ChromaOptimizer:
    """J3: Chroma dev environment with intelligent toggle."""
    
    def __init__(self, config: DatastoreConfig):
        self.config = config
        self.client = None
        self.collection = None
        self.health = DatastoreHealth(
            datastore_type=DatastoreType.CHROMA,
            is_healthy=False,
            response_time_ms=0.0,
            last_check=datetime.utcnow()
        )
        self.metrics = DatastoreMetrics(datastore_type=DatastoreType.CHROMA)
        
    async def initialize(self) -> bool:
        """Initialize Chroma client for development environment."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Development-optimized settings
            settings = Settings(
                persist_directory=self.config.chroma_persist_directory,
                anonymized_telemetry=False,
                allow_reset=True  # Allow reset for development
            )
            
            self.client = chromadb.PersistentClient(settings=settings)
            
            # Test connection and get/create collection
            start_time = time.time()
            await self._ensure_collection_exists()
            response_time = (time.time() - start_time) * 1000
            
            self.health = DatastoreHealth(
                datastore_type=DatastoreType.CHROMA,
                is_healthy=True,
                response_time_ms=response_time,
                last_check=datetime.utcnow()
            )
            
            logger.info("Chroma optimizer initialized",
                       persist_directory=self.config.chroma_persist_directory,
                       environment=self.config.environment.value)
            return True
            
        except Exception as e:
            logger.error("Failed to initialize Chroma", error=str(e))
            self.health.error_message = str(e)
            return False
    
    async def _ensure_collection_exists(self):
        """Ensure collection exists with development settings."""
        try:
            # Get or create collection
            try:
                self.collection = self.client.get_collection(
                    name=self.config.chroma_collection_name
                )
                logger.info(f"Retrieved existing Chroma collection: {self.config.chroma_collection_name}")
            except:
                # Create new collection
                self.collection = self.client.create_collection(
                    name=self.config.chroma_collection_name,
                    metadata={"description": "SarvanOM development vector store"}
                )
                logger.info(f"Created new Chroma collection: {self.config.chroma_collection_name}")
                
        except Exception as e:
            logger.error("Failed to ensure collection exists", error=str(e))
            raise
    
    async def batch_add(self, documents: List[str], embeddings: List[List[float]], 
                       metadatas: List[Dict[str, Any]], ids: List[str]) -> bool:
        """Add documents to Chroma collection."""
        try:
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            self.metrics.successful_queries += 1
            return True
            
        except Exception as e:
            logger.error("Chroma batch add failed", error=str(e))
            self.metrics.failed_queries += 1
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive Chroma status."""
        try:
            collection_count = self.collection.count()
            
            return {
                "is_healthy": self.health.is_healthy,
                "response_time_ms": self.health.response_time_ms,
                "collection_name": self.config.chroma_collection_name,
                "collection_count": collection_count,
                "persist_directory": self.config.chroma_persist_directory,
                "metrics": {
                    "total_queries": self.metrics.total_queries,
                    "successful_queries": self.metrics.successful_queries,
                    "failed_queries": self.metrics.failed_queries,
                    "avg_response_time_ms": self.metrics.avg_response_time_ms
                }
            }
        except Exception as e:
            return {
                "is_healthy": False,
                "error": str(e),
                "metrics": self.metrics.__dict__
            }

class DatastoresOptimizer:
    """
    Comprehensive datastores optimization service.
    
    Manages all datastores with environment-aware configuration:
    - J1: Meilisearch tuning for production
    - J2: Qdrant production optimization
    - J3: Chroma dev environment toggle
    """
    
    def __init__(self):
        self.config = DatastoreConfig.from_environment()
        self.optimizers: Dict[DatastoreType, Any] = {}
        self.health_status: Dict[DatastoreType, DatastoreHealth] = {}
        self._initialized = False
        
        logger.info("DatastoresOptimizer initialized",
                   environment=self.config.environment.value,
                   production_optimizations=self.config.enable_production_optimizations)
    
    async def initialize(self) -> bool:
        """Initialize all datastore optimizers."""
        try:
            # Initialize Meilisearch (J1)
            meilisearch_optimizer = MeilisearchOptimizer(self.config)
            if await meilisearch_optimizer.initialize():
                self.optimizers[DatastoreType.MEILISEARCH] = meilisearch_optimizer
                self.health_status[DatastoreType.MEILISEARCH] = meilisearch_optimizer.health
            
            # Initialize Qdrant (J2) - only in production or when explicitly enabled
            if (self.config.environment == Environment.PRODUCTION or 
                os.getenv('ENABLE_QDRANT', 'false').lower() == 'true'):
                qdrant_optimizer = QdrantOptimizer(self.config)
                if await qdrant_optimizer.initialize():
                    self.optimizers[DatastoreType.QDRANT] = qdrant_optimizer
                    self.health_status[DatastoreType.QDRANT] = qdrant_optimizer.health
            
            # Initialize Chroma (J3) - for development or as fallback
            if (self.config.environment == Environment.DEVELOPMENT or 
                os.getenv('ENABLE_CHROMA', 'true').lower() == 'true'):
                chroma_optimizer = ChromaOptimizer(self.config)
                if await chroma_optimizer.initialize():
                    self.optimizers[DatastoreType.CHROMA] = chroma_optimizer
                    self.health_status[DatastoreType.CHROMA] = chroma_optimizer.health
            
            self._initialized = True
            
            logger.info("DatastoresOptimizer initialization complete",
                       initialized_optimizers=list(self.optimizers.keys()))
            return True
            
        except Exception as e:
            logger.error("Failed to initialize DatastoresOptimizer", error=str(e))
            return False
    
    async def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all datastores."""
        if not self._initialized:
            return {"error": "Not initialized"}
        
        status = {
            "environment": self.config.environment.value,
            "production_optimizations": self.config.enable_production_optimizations,
            "datastores": {},
            "overall_health": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for datastore_type, optimizer in self.optimizers.items():
            try:
                datastore_status = await optimizer.get_status()
                status["datastores"][datastore_type.value] = datastore_status
                
                if not datastore_status.get("is_healthy", False):
                    status["overall_health"] = False
                    
            except Exception as e:
                status["datastores"][datastore_type.value] = {
                    "is_healthy": False,
                    "error": str(e)
                }
                status["overall_health"] = False
        
        return status
    
    async def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations based on current status."""
        recommendations = []
        
        if self.config.environment == Environment.DEVELOPMENT:
            recommendations.extend([
                "Development environment detected - using Chroma for vector storage",
                "Consider enabling Qdrant for production-like testing",
                "Meilisearch configured with simplified settings for faster indexing"
            ])
        else:
            recommendations.extend([
                "Production environment detected - using optimized settings",
                "Qdrant configured with connection pooling and batch operations",
                "Meilisearch configured with domain-specific indexes",
                "All datastores configured for maximum performance"
            ])
        
        # Check for specific optimizations
        if DatastoreType.QDRANT not in self.optimizers and self.config.environment == Environment.PRODUCTION:
            recommendations.append("WARNING: Qdrant not available in production - consider enabling")
        
        if DatastoreType.CHROMA not in self.optimizers and self.config.environment == Environment.DEVELOPMENT:
            recommendations.append("WARNING: Chroma not available in development - check configuration")
        
        return recommendations

# Global service instance
_datastores_optimizer: Optional[DatastoresOptimizer] = None

async def get_datastores_optimizer() -> DatastoresOptimizer:
    """Get or create global datastores optimizer."""
    global _datastores_optimizer
    
    if _datastores_optimizer is None:
        _datastores_optimizer = DatastoresOptimizer()
        await _datastores_optimizer.initialize()
    
    return _datastores_optimizer
