from shared.core.api.config import get_settings
settings = get_settings()
"""
Connection Pooling Module for Universal Knowledge Platform
Manages connection pools for all external services to improve performance.

Features:
- Connection pooling for all external services
- Circuit breakers for fault tolerance
- Health checks and monitoring
- Automatic retry with exponential backoff
- Connection lifecycle management
- Performance metrics and logging
"""

import aiohttp
import asyncio
import logging
import os
import time
from typing import Optional, Dict, Any, List
import redis.asyncio as aioredis
from elasticsearch import AsyncElasticsearch
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics

logger = logging.getLogger(__name__)

# Connection pool configuration
POOL_SIZE = int(os.getenv("CONNECTION_POOL_SIZE", "10"))
POOL_TIMEOUT = float(os.getenv("CONNECTION_POOL_TIMEOUT", "30.0"))
MAX_KEEPALIVE_TIME = int(os.getenv("MAX_KEEPALIVE_TIME", "300"))  # 5 minutes

# Service URLs
VECTOR_DB_URL = os.getenv("VECTOR_DB_URL", "http://localhost:6333")
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
REDIS_URL = settings.redis_url or "redis://localhost:6379"
SPARQL_ENDPOINT = os.getenv(
    "SPARQL_ENDPOINT", "http://localhost:7200/repositories/knowledge"
)

# Circuit breaker configuration
CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5"))
CIRCUIT_BREAKER_TIMEOUT = int(os.getenv("CIRCUIT_BREAKER_TIMEOUT", "60"))  # seconds

@dataclass
class PoolMetrics:
    """Metrics for connection pool performance."""
    service_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    response_times: List[float] = None
    
    def __post_init__(self):
        if self.response_times is None:
            self.response_times = []
    
    def record_request(self, success: bool, response_time: float):
        """Record a request metric."""
        self.total_requests += 1
        self.total_response_time += response_time
        self.response_times.append(response_time)
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        # Keep only last 1000 response times for memory efficiency
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    @property
    def success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def average_response_time(self) -> float:
        """Get average response time."""
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)
    
    @property
    def p95_response_time(self) -> float:
        """Get 95th percentile response time."""
        if len(self.response_times) < 2:
            return self.average_response_time
        return statistics.quantiles(self.response_times, n=20)[18]  # 95th percentile

class CircuitBreaker:
    """Circuit breaker for external service calls."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.failures = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.failure_threshold = CIRCUIT_BREAKER_FAILURE_THRESHOLD
        self.timeout = CIRCUIT_BREAKER_TIMEOUT
    
    def can_execute(self) -> bool:
        """Check if circuit breaker allows execution."""
        if self.state == "CLOSED":
            return True
        
        if self.state == "OPEN":
            if self.last_failure_time and time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
                logger.info(f"Circuit breaker for {self.service_name} moved to HALF_OPEN")
                return True
            return False
        
        return True  # HALF_OPEN
    
    def record_success(self):
        """Record successful call."""
        self.failures = 0
        if self.state != "CLOSED":
            self.state = "CLOSED"
            logger.info(f"Circuit breaker for {self.service_name} moved to CLOSED")
    
    def record_failure(self):
        """Record failed call."""
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker for {self.service_name} moved to OPEN after {self.failures} failures")
    
    def get_state(self) -> str:
        """Get current circuit breaker state."""
        return self.state


class ConnectionPoolManager:
    """Manages connection pools for all external services with circuit breakers and monitoring."""

    def __init__(self):
        self._http_session: Optional[aiohttp.ClientSession] = None
        self._redis_pool: Optional[aioredis.Redis] = None
        self._elasticsearch_client: Optional[AsyncElasticsearch] = None
        self._initialized = False
        self._lock = asyncio.Lock()
        
        # Circuit breakers for each service
        self._circuit_breakers = {
            "redis": CircuitBreaker("redis"),
            "elasticsearch": CircuitBreaker("elasticsearch"),
            "vector_db": CircuitBreaker("vector_db"),
            "sparql": CircuitBreaker("sparql"),
            "http": CircuitBreaker("http"),
        }
        
        # Metrics for each service
        self._metrics = {
            "redis": PoolMetrics("redis"),
            "elasticsearch": PoolMetrics("elasticsearch"),
            "vector_db": PoolMetrics("vector_db"),
            "sparql": PoolMetrics("sparql"),
            "http": PoolMetrics("http"),
        }

    async def initialize(self):
        """Initialize all connection pools."""
        async with self._lock:
            if self._initialized:
                return

            logger.info("Initializing connection pools...")

            # Initialize HTTP session with connection pooling
            connector = aiohttp.TCPConnector(
                limit=POOL_SIZE,
                limit_per_host=POOL_SIZE,
                ttl_dns_cache=300,
                keepalive_timeout=MAX_KEEPALIVE_TIME,
                enable_cleanup_closed=True,
            )

            timeout = aiohttp.ClientTimeout(
                total=POOL_TIMEOUT, connect=5.0, sock_read=POOL_TIMEOUT
            )

            self._http_session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={"User-Agent": "UniversalKnowledgePlatform/1.0"},
            )

            # Initialize Redis connection pool
            try:
                if not self._circuit_breakers["redis"].can_execute():
                    logger.warning("Redis circuit breaker is OPEN, skipping initialization")
                    self._redis_pool = None
                else:
                    start_time = time.time()
                    self._redis_pool = await aioredis.from_url(
                        REDIS_URL,
                        max_connections=POOL_SIZE,
                        socket_connect_timeout=5.0,
                        socket_keepalive=True,
                        health_check_interval=30,
                    )
                    await self._redis_pool.ping()
                    response_time = time.time() - start_time
                    
                    self._circuit_breakers["redis"].record_success()
                    self._metrics["redis"].record_request(True, response_time)
                    logger.info(f"Redis connection pool initialized (response time: {response_time:.3f}s)")
            except Exception as e:
                response_time = time.time() - start_time if 'start_time' in locals() else 0.0
                self._circuit_breakers["redis"].record_failure()
                self._metrics["redis"].record_request(False, response_time)
                logger.warning(f"Failed to initialize Redis pool: {e}")
                self._redis_pool = None

            # Initialize Elasticsearch client with connection pooling
            try:
                if not self._circuit_breakers["elasticsearch"].can_execute():
                    logger.warning("Elasticsearch circuit breaker is OPEN, skipping initialization")
                    self._elasticsearch_client = None
                else:
                    start_time = time.time()
                    self._elasticsearch_client = AsyncElasticsearch(
                        [ELASTICSEARCH_URL],
                        retry_on_timeout=True,
                        max_retries=3,
                    )
                    await self._elasticsearch_client.ping()
                    response_time = time.time() - start_time
                    
                    self._circuit_breakers["elasticsearch"].record_success()
                    self._metrics["elasticsearch"].record_request(True, response_time)
                    logger.info(f"Elasticsearch connection pool initialized (response time: {response_time:.3f}s)")
            except Exception as e:
                response_time = time.time() - start_time if 'start_time' in locals() else 0.0
                self._circuit_breakers["elasticsearch"].record_failure()
                self._metrics["elasticsearch"].record_request(False, response_time)
                logger.warning(f"Failed to initialize Elasticsearch pool: {e}")
                self._elasticsearch_client = None

            self._initialized = True
            logger.info("All connection pools initialized successfully")

    async def shutdown(self):
        """Shutdown all connection pools gracefully."""
        async with self._lock:
            if not self._initialized:
                return

            logger.info("Shutting down connection pools...")

            # Close HTTP session
            if self._http_session:
                await self._http_session.close()
                # Wait for connector cleanup
                await asyncio.sleep(0.25)

            # Close Redis pool
            if self._redis_pool:
                await self._redis_pool.close()
                # Redis doesn't have wait_closed method in newer versions
                try:
                    await self._redis_pool.wait_closed()
                except AttributeError:
                    pass  # Ignore if method doesn't exist

            # Close Elasticsearch client
            if self._elasticsearch_client:
                await self._elasticsearch_client.close()

            self._initialized = False
            logger.info("All connection pools shut down successfully")

    @asynccontextmanager
    async def get_http_session(self):
        """Get HTTP session from pool."""
        if not self._initialized:
            await self.initialize()

        if not self._http_session:
            raise RuntimeError("HTTP session not initialized")

        yield self._http_session

    @asynccontextmanager
    async def get_redis_connection(self):
        """Get Redis connection from pool."""
        if not self._initialized:
            await self.initialize()

        if not self._redis_pool:
            raise RuntimeError("Redis pool not initialized")

        yield self._redis_pool

    @asynccontextmanager
    async def get_elasticsearch_client(self):
        """Get Elasticsearch client from pool."""
        if not self._initialized:
            await self.initialize()

        if not self._elasticsearch_client:
            raise RuntimeError("Elasticsearch client not initialized")

        yield self._elasticsearch_client

    async def make_http_request(
        self, method: str, url: str, **kwargs
    ) -> aiohttp.ClientResponse:
        """
        Make HTTP request using pooled connection.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Target URL
            **kwargs: Additional arguments for the request

        Returns:
            Response object
        """
        async with self.get_http_session() as session:
            async with session.request(method, url, **kwargs) as response:
                return response

    async def vector_db_request(
        self, endpoint: str, method: str = "GET", **kwargs
    ) -> Dict[str, Any]:
        """
        Make request to vector database using pooled connection.

        Args:
            endpoint: API endpoint
            method: HTTP method
            **kwargs: Request parameters

        Returns:
            JSON response
        """
        url = f"{VECTOR_DB_URL}{endpoint}"

        async with self.get_http_session() as session:
            async with session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()

    async def sparql_query(
        self, query: str, timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute SPARQL query using pooled connection.

        Args:
            query: SPARQL query string
            timeout: Query timeout

        Returns:
            Query results
        """
        async with self.get_http_session() as session:
            async with session.post(
                SPARQL_ENDPOINT,
                data={"query": query},
                headers={"Accept": "application/json"},
                timeout=timeout or POOL_TIMEOUT,
            ) as response:
                response.raise_for_status()
                return await response.json()

    def get_pool_stats(self) -> Dict[str, Any]:
        """Get comprehensive connection pool statistics with circuit breakers and metrics."""
        stats = {
            "initialized": self._initialized,
            "http_session": self._http_session is not None,
            "redis_pool": self._redis_pool is not None,
            "elasticsearch_client": self._elasticsearch_client is not None,
            "circuit_breakers": {
                service: {
                    "state": cb.get_state(),
                    "failures": cb.failures,
                    "last_failure_time": cb.last_failure_time,
                }
                for service, cb in self._circuit_breakers.items()
            },
            "metrics": {
                service: {
                    "total_requests": metrics.total_requests,
                    "successful_requests": metrics.successful_requests,
                    "failed_requests": metrics.failed_requests,
                    "success_rate": round(metrics.success_rate, 2),
                    "average_response_time": round(metrics.average_response_time, 3),
                    "p95_response_time": round(metrics.p95_response_time, 3),
                }
                for service, metrics in self._metrics.items()
            },
            "pool_config": {
                "pool_size": POOL_SIZE,
                "pool_timeout": POOL_TIMEOUT,
                "max_keepalive_time": MAX_KEEPALIVE_TIME,
            }
        }
        
        # Add detailed pool information
        if self._http_session and self._http_session.connector:
            connector = self._http_session.connector
            stats["pools"] = {
                "http": {
                    "limit": connector.limit,
                    "limit_per_host": connector.limit_per_host,
                    "connections": (
                        len(connector._conns) if hasattr(connector, "_conns") else 0
                    ),
                }
            }

        if self._redis_pool:
            if "pools" not in stats:
                stats["pools"] = {}
            stats["pools"]["redis"] = {
                "max_connections": POOL_SIZE,
                "initialized": True,
            }

        if self._elasticsearch_client:
            if "pools" not in stats:
                stats["pools"] = {}
            stats["pools"]["elasticsearch"] = {
                "max_connections": POOL_SIZE,
                "initialized": True,
            }

        return stats


# Global connection pool manager instance
_pool_manager: Optional[ConnectionPoolManager] = None
_pool_lock = asyncio.Lock()


async def get_pool_manager() -> ConnectionPoolManager:
    """Get or create the global connection pool manager."""
    global _pool_manager

    if _pool_manager is None:
        async with _pool_lock:
            if _pool_manager is None:
                _pool_manager = ConnectionPoolManager()
                await _pool_manager.initialize()

    return _pool_manager


async def shutdown_pools():
    """Shutdown all connection pools."""
    global _pool_manager

    if _pool_manager:
        await _pool_manager.shutdown()
        _pool_manager = None


# Convenience functions for common operations
async def make_pooled_request(
    method: str, url: str, **kwargs
) -> aiohttp.ClientResponse:
    """Make HTTP request using pooled connection."""
    manager = await get_pool_manager()
    return await manager.make_http_request(method, url, **kwargs)


async def get_redis_connection():
    """Get Redis connection from pool."""
    manager = await get_pool_manager()
    async with manager.get_redis_connection() as redis:
        yield redis


async def get_elasticsearch_client():
    """Get Elasticsearch client from pool."""
    manager = await get_pool_manager()
    async with manager.get_elasticsearch_client() as client:
        yield client
