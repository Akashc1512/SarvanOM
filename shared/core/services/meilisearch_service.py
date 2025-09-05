"""
Meilisearch Service - Production-Optimized Search (Phase J1)
===========================================================

Production-grade Meilisearch integration with domain-specific optimizations:
- Tuned index settings for docs/code/QA domains
- Batch updates with optimal chunk sizes
- Auto-refresh configuration for bulk operations
- Status endpoint for monitoring
- Performance metrics collection

Maps to Phase J1 requirements for fast keyword search results.
"""

import os
import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import structlog

# Optional dependency with graceful fallback
try:
    import meilisearch
    MEILISEARCH_AVAILABLE = True
except ImportError:
    meilisearch = None
    MEILISEARCH_AVAILABLE = False

logger = structlog.get_logger(__name__)


@dataclass
class MeilisearchConfig:
    """Configuration for Meilisearch service."""
    url: str = "http://localhost:7700"
    api_key: Optional[str] = None
    master_key: Optional[str] = None
    timeout: float = 5.0
    
    # Index configuration
    docs_index: str = "sarvanom_docs"
    code_index: str = "sarvanom_code" 
    qa_index: str = "sarvanom_qa"
    
    # Performance settings
    batch_size: int = 1000
    auto_refresh_enabled: bool = True
    max_total_hits: int = 10000
    
    @classmethod
    def from_environment(cls) -> 'MeilisearchConfig':
        """Load configuration from environment variables."""
        return cls(
            url=os.getenv('MEILISEARCH_URL', 'http://localhost:7700'),
            api_key=os.getenv('MEILISEARCH_API_KEY'),
            master_key=os.getenv('MEILI_MASTER_KEY'),  # Uses existing env var
            timeout=float(os.getenv('MEILISEARCH_TIMEOUT', '5.0')),
            docs_index=os.getenv('MEILISEARCH_DOCS_INDEX', 'sarvanom_docs'),
            code_index=os.getenv('MEILISEARCH_CODE_INDEX', 'sarvanom_code'),
            qa_index=os.getenv('MEILISEARCH_QA_INDEX', 'sarvanom_qa'),
            batch_size=int(os.getenv('MEILISEARCH_BATCH_SIZE', '1000')),
            auto_refresh_enabled=os.getenv('MEILISEARCH_AUTO_REFRESH', 'true').lower() == 'true',
            max_total_hits=int(os.getenv('MEILISEARCH_MAX_TOTAL_HITS', '10000'))
        )
    
    def get_redacted_config(self) -> Dict[str, Any]:
        """Get configuration with sensitive data redacted."""
        return {
            'url': self.url,
            'api_key': '[REDACTED]' if self.api_key else None,
            'master_key': '[REDACTED]' if self.master_key else None,
            'timeout': self.timeout,
            'docs_index': self.docs_index,
            'code_index': self.code_index,
            'qa_index': self.qa_index,
            'batch_size': self.batch_size,
            'auto_refresh_enabled': self.auto_refresh_enabled,
            'max_total_hits': self.max_total_hits
        }


@dataclass
class SearchMetrics:
    """Search performance metrics."""
    total_searches: int = 0
    total_indexing_operations: int = 0
    avg_search_time_ms: float = 0.0
    avg_indexing_time_ms: float = 0.0
    last_bulk_operation: Optional[datetime] = None
    index_sizes: Dict[str, int] = field(default_factory=dict)
    
    def record_search(self, duration_ms: float):
        """Record a search operation."""
        self.total_searches += 1
        self.avg_search_time_ms = (
            (self.avg_search_time_ms * (self.total_searches - 1) + duration_ms) 
            / self.total_searches
        )
    
    def record_indexing(self, duration_ms: float):
        """Record an indexing operation."""
        self.total_indexing_operations += 1
        self.avg_indexing_time_ms = (
            (self.avg_indexing_time_ms * (self.total_indexing_operations - 1) + duration_ms)
            / self.total_indexing_operations
        )
        self.last_bulk_operation = datetime.now()


class MeilisearchService:
    """
    Production-optimized Meilisearch service.
    
    Features:
    - Domain-specific index optimization (docs, code, QA)
    - Batch operations with optimal performance
    - Auto-refresh configuration
    - Comprehensive monitoring and metrics
    - Production-grade error handling
    """
    
    def __init__(self):
        """Initialize Meilisearch service."""
        self.config = MeilisearchConfig.from_environment()
        self.client = None
        self.metrics = SearchMetrics()
        self._indexes = {}
        self._connected = False
        
        logger.info("MeilisearchService initialized",
                   config=self.config.get_redacted_config())
    
    async def connect(self) -> bool:
        """Connect to Meilisearch and initialize indexes."""
        if not MEILISEARCH_AVAILABLE:
            logger.warning("Meilisearch not available, install meilisearch")
            return False
        
        try:
            # Initialize client
            api_key = self.config.master_key or self.config.api_key
            self.client = meilisearch.Client(
                self.config.url,
                api_key,
                timeout=self.config.timeout
            )
            
            # Test connection
            health = await asyncio.to_thread(self.client.health)
            if health.get('status') != 'available':
                logger.error("Meilisearch not available",
                           health=health)
                return False
            
            # Initialize domain-specific indexes
            await self._initialize_indexes()
            
            self._connected = True
            
            logger.info("Connected to Meilisearch",
                       url=self.config.url,
                       indexes=list(self._indexes.keys()))
            
            return True
            
        except Exception as e:
            logger.error("Meilisearch connection failed",
                        url=self.config.url,
                        error=str(e))
            return False
    
    async def _initialize_indexes(self):
        """Initialize and configure domain-specific indexes."""
        index_configs = {
            self.config.docs_index: self._get_docs_index_config(),
            self.config.code_index: self._get_code_index_config(),
            self.config.qa_index: self._get_qa_index_config()
        }
        
        for index_name, config in index_configs.items():
            try:
                # Create or get index
                index = await asyncio.to_thread(
                    self.client.index,
                    index_name
                )
                
                # Apply configuration
                await self._configure_index(index, config)
                
                self._indexes[index_name] = index
                
                # Update metrics
                stats = await asyncio.to_thread(index.get_stats)
                self.metrics.index_sizes[index_name] = stats.get('numberOfDocuments', 0)
                
                logger.info("Initialized Meilisearch index",
                           index=index_name,
                           documents=self.metrics.index_sizes[index_name])
                
            except Exception as e:
                logger.error("Failed to initialize index",
                           index=index_name,
                           error=str(e))
    
    def _get_docs_index_config(self) -> Dict[str, Any]:
        """Get configuration for documentation index."""
        return {
            'searchableAttributes': [
                'title',
                'content',
                'description',
                'tags'
            ],
            'sortableAttributes': [
                'created_at',
                'updated_at',
                'relevance_score'
            ],
            'filterableAttributes': [
                'category',
                'author',
                'type',
                'language'
            ],
            'stopWords': [
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was'
            ],
            'synonyms': {
                'ai': ['artificial intelligence', 'machine learning'],
                'ml': ['machine learning', 'artificial intelligence'],
                'api': ['application programming interface'],
                'ui': ['user interface', 'frontend'],
                'ux': ['user experience']
            },
            'pagination': {
                'maxTotalHits': self.config.max_total_hits
            }
        }
    
    def _get_code_index_config(self) -> Dict[str, Any]:
        """Get configuration for code index."""
        return {
            'searchableAttributes': [
                'function_name',
                'class_name',
                'file_path',
                'content',
                'docstring',
                'comments'
            ],
            'sortableAttributes': [
                'file_path',
                'line_number',
                'complexity_score'
            ],
            'filterableAttributes': [
                'language',
                'file_type',
                'repository',
                'framework'
            ],
            'stopWords': [
                'def', 'class', 'import', 'from', 'if', 'else', 'elif',
                'for', 'while', 'try', 'except', 'finally', 'return'
            ],
            'synonyms': {
                'function': ['func', 'method', 'procedure'],
                'class': ['object', 'type'],
                'variable': ['var', 'parameter', 'param'],
                'array': ['list', 'collection'],
                'dict': ['dictionary', 'map', 'object']
            },
            'pagination': {
                'maxTotalHits': self.config.max_total_hits
            }
        }
    
    def _get_qa_index_config(self) -> Dict[str, Any]:
        """Get configuration for Q&A index."""
        return {
            'searchableAttributes': [
                'question',
                'answer',
                'title',
                'tags'
            ],
            'sortableAttributes': [
                'score',
                'created_at',
                'view_count',
                'answer_count'
            ],
            'filterableAttributes': [
                'category',
                'difficulty',
                'has_accepted_answer',
                'source'
            ],
            'stopWords': [
                'how', 'what', 'when', 'where', 'why', 'who', 'which',
                'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were'
            ],
            'synonyms': {
                'how to': ['tutorial', 'guide', 'instructions'],
                'error': ['exception', 'bug', 'issue', 'problem'],
                'fix': ['solve', 'resolve', 'repair'],
                'install': ['setup', 'configure', 'deploy']
            },
            'pagination': {
                'maxTotalHits': self.config.max_total_hits
            }
        }
    
    async def _configure_index(self, index, config: Dict[str, Any]):
        """Apply configuration to an index."""
        try:
            # Configure searchable attributes
            if 'searchableAttributes' in config:
                await asyncio.to_thread(
                    index.update_searchable_attributes,
                    config['searchableAttributes']
                )
            
            # Configure sortable attributes
            if 'sortableAttributes' in config:
                await asyncio.to_thread(
                    index.update_sortable_attributes,
                    config['sortableAttributes']
                )
            
            # Configure filterable attributes
            if 'filterableAttributes' in config:
                await asyncio.to_thread(
                    index.update_filterable_attributes,
                    config['filterableAttributes']
                )
            
            # Configure stop words
            if 'stopWords' in config:
                await asyncio.to_thread(
                    index.update_stop_words,
                    config['stopWords']
                )
            
            # Configure synonyms
            if 'synonyms' in config:
                await asyncio.to_thread(
                    index.update_synonyms,
                    config['synonyms']
                )
            
            # Configure pagination
            if 'pagination' in config:
                await asyncio.to_thread(
                    index.update_pagination,
                    config['pagination']
                )
            
        except Exception as e:
            logger.warning("Failed to configure index",
                          error=str(e))
    
    async def search(self, query: str, index_name: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform optimized search with performance tracking."""
        if not self._connected:
            await self.connect()
        
        if index_name not in self._indexes:
            raise ValueError(f"Index {index_name} not available")
        
        start_time = time.time()
        
        try:
            index = self._indexes[index_name]
            search_options = options or {}
            
            # Default search options for performance
            search_options.setdefault('limit', 20)
            search_options.setdefault('offset', 0)
            search_options.setdefault('attributesToHighlight', ['*'])
            
            # Perform search
            results = await asyncio.to_thread(
                index.search,
                query,
                search_options
            )
            
            # Record performance metrics
            search_time_ms = (time.time() - start_time) * 1000
            self.metrics.record_search(search_time_ms)
            
            logger.debug("Meilisearch query completed",
                        query=query[:50],
                        index=index_name,
                        hits=len(results.get('hits', [])),
                        time_ms=round(search_time_ms, 2))
            
            return results
            
        except Exception as e:
            search_time_ms = (time.time() - start_time) * 1000
            logger.error("Meilisearch query failed",
                        query=query[:50],
                        index=index_name,
                        error=str(e),
                        time_ms=round(search_time_ms, 2))
            raise
    
    async def bulk_index_documents(self, documents: List[Dict[str, Any]], index_name: str) -> Dict[str, Any]:
        """Perform optimized bulk indexing with batch processing."""
        if not self._connected:
            await self.connect()
        
        if index_name not in self._indexes:
            raise ValueError(f"Index {index_name} not available")
        
        start_time = time.time()
        
        try:
            index = self._indexes[index_name]
            
            # Process in batches for optimal performance
            total_processed = 0
            batch_results = []
            
            for i in range(0, len(documents), self.config.batch_size):
                batch = documents[i:i + self.config.batch_size]
                
                # Disable auto-refresh for bulk operations
                if self.config.auto_refresh_enabled and i == 0:
                    await asyncio.to_thread(
                        index.update_settings,
                        {'autoRefresh': False}
                    )
                
                # Add batch
                task_info = await asyncio.to_thread(
                    index.add_documents,
                    batch
                )
                
                # Wait for task completion if it's a task object
                if hasattr(task_info, 'task_uid'):
                    await asyncio.to_thread(
                        self.client.wait_for_task,
                        task_info.task_uid
                    )
                
                batch_results.append(task_info)
                total_processed += len(batch)
                
                logger.debug("Processed batch",
                           batch_size=len(batch),
                           total_processed=total_processed,
                           total_documents=len(documents))
            
            # Re-enable auto-refresh
            if self.config.auto_refresh_enabled:
                await asyncio.to_thread(
                    index.update_settings,
                    {'autoRefresh': True}
                )
            
            # Record performance metrics
            indexing_time_ms = (time.time() - start_time) * 1000
            self.metrics.record_indexing(indexing_time_ms)
            
            # Update index size metrics
            stats = await asyncio.to_thread(index.get_stats)
            self.metrics.index_sizes[index_name] = stats.get('numberOfDocuments', 0)
            
            logger.info("Bulk indexing completed",
                       index=index_name,
                       documents_processed=total_processed,
                       time_ms=round(indexing_time_ms, 2),
                       total_documents_in_index=self.metrics.index_sizes[index_name])
            
            return {
                'documents_processed': total_processed,
                'indexing_time_ms': indexing_time_ms,
                'batch_results': batch_results,
                'total_documents_in_index': self.metrics.index_sizes[index_name]
            }
            
        except Exception as e:
            indexing_time_ms = (time.time() - start_time) * 1000
            logger.error("Bulk indexing failed",
                        index=index_name,
                        documents_count=len(documents),
                        error=str(e),
                        time_ms=round(indexing_time_ms, 2))
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive search service status."""
        try:
            if not self._connected:
                return {
                    'status': 'disconnected',
                    'error': 'Not connected to Meilisearch'
                }
            
            # Get overall health
            health = await asyncio.to_thread(self.client.health)
            
            # Get index stats
            index_stats = {}
            for index_name, index in self._indexes.items():
                try:
                    stats = await asyncio.to_thread(index.get_stats)
                    index_stats[index_name] = {
                        'numberOfDocuments': stats.get('numberOfDocuments', 0),
                        'isIndexing': stats.get('isIndexing', False),
                        'fieldsDistribution': stats.get('fieldsDistribution', {})
                    }
                except Exception as e:
                    index_stats[index_name] = {'error': str(e)}
            
            return {
                'status': 'healthy' if health.get('status') == 'available' else 'degraded',
                'meilisearch_health': health,
                'index_stats': index_stats,
                'performance_metrics': {
                    'total_searches': self.metrics.total_searches,
                    'total_indexing_operations': self.metrics.total_indexing_operations,
                    'avg_search_time_ms': round(self.metrics.avg_search_time_ms, 2),
                    'avg_indexing_time_ms': round(self.metrics.avg_indexing_time_ms, 2),
                    'last_bulk_operation': self.metrics.last_bulk_operation.isoformat() if self.metrics.last_bulk_operation else None
                },
                'configuration': self.config.get_redacted_config()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }


# Global service instance
_meilisearch_service: Optional[MeilisearchService] = None

def get_meilisearch_service() -> MeilisearchService:
    """Get or create global Meilisearch service."""
    global _meilisearch_service
    
    if _meilisearch_service is None:
        _meilisearch_service = MeilisearchService()
    
    return _meilisearch_service

async def get_search_status() -> Dict[str, Any]:
    """Get search service status for monitoring."""
    service = get_meilisearch_service()
    return await service.get_status()

async def get_meilisearch_status() -> Dict[str, Any]:
    """Get Meilisearch status (alias for compatibility)."""
    return await get_search_status()

# Export public interface
__all__ = [
    'MeilisearchService',
    'MeilisearchConfig',
    'get_meilisearch_service',
    'get_search_status',
    'get_meilisearch_status'
]
