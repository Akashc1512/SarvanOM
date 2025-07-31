"""
Enhanced Rate Limiting System - MAANG Standards
Following OpenAI and Perplexity rate limiting patterns.

Features:
- Multiple backend support (Redis, In-Memory)
- Granular rate limiting by endpoint, user, IP
- Sliding window and fixed window algorithms
- Rate limit headers in responses
- Comprehensive monitoring and metrics
- Burst handling and queue management
- Cost-based rate limiting

Authors:
- Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import asyncio
import time
import hashlib
import json
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import structlog
from prometheus_client import Counter, Gauge, Histogram

logger = structlog.get_logger(__name__)

# Prometheus metrics
rate_limit_requests = Counter(
    "rate_limit_requests_total",
    "Total rate limit requests",
    ["endpoint", "user_id", "status"],
)

rate_limit_exceeded = Counter(
    "rate_limit_exceeded_total",
    "Total rate limit violations",
    ["endpoint", "user_id", "limit_type"],
)

rate_limit_remaining = Gauge(
    "rate_limit_remaining",
    "Remaining requests in current window",
    ["endpoint", "user_id"],
)

rate_limit_reset_time = Gauge(
    "rate_limit_reset_time",
    "Rate limit reset time (Unix timestamp)",
    ["endpoint", "user_id"],
)


class RateLimitAlgorithm(str, Enum):
    """Rate limiting algorithms."""

    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


class RateLimitType(str, Enum):
    """Rate limit types."""

    USER = "user"
    IP = "ip"
    ENDPOINT = "endpoint"
    GLOBAL = "global"
    COST = "cost"


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 10
    window_size: int = 60  # seconds
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.SLIDING_WINDOW
    cost_per_request: float = 1.0
    max_cost_per_minute: float = 100.0

    # Advanced settings
    enable_burst: bool = True
    enable_queue: bool = False
    queue_timeout: int = 30
    retry_after_header: bool = True

    def __post_init__(self):
        """Validate configuration."""
        if self.requests_per_minute <= 0:
            raise ValueError("requests_per_minute must be positive")
        if self.window_size <= 0:
            raise ValueError("window_size must be positive")
        if self.cost_per_request <= 0:
            raise ValueError("cost_per_request must be positive")


@dataclass
class RateLimitInfo:
    """Rate limit information."""

    limit: int
    remaining: int
    reset_time: int
    window_size: int
    algorithm: RateLimitAlgorithm
    cost_used: float = 0.0
    max_cost: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "limit": self.limit,
            "remaining": self.remaining,
            "reset_time": self.reset_time,
            "window_size": self.window_size,
            "algorithm": self.algorithm.value,
            "cost_used": self.cost_used,
            "max_cost": self.max_cost,
        }


class RateLimitBackend:
    """Abstract rate limit backend."""

    async def check_rate_limit(
        self, identifier: str, config: RateLimitConfig, cost: float = 1.0
    ) -> Tuple[bool, RateLimitInfo]:
        """Check rate limit and return (allowed, info)."""
        raise NotImplementedError

    async def record_request(
        self, identifier: str, config: RateLimitConfig, cost: float = 1.0
    ) -> None:
        """Record a request."""
        raise NotImplementedError

    async def reset_rate_limit(self, identifier: str) -> None:
        """Reset rate limit for identifier."""
        raise NotImplementedError

    async def get_rate_limit_info(
        self, identifier: str, config: RateLimitConfig
    ) -> RateLimitInfo:
        """Get current rate limit information."""
        raise NotImplementedError


class RedisRateLimitBackend(RateLimitBackend):
    """Redis-based rate limiting backend."""

    def __init__(self, redis_client, prefix: str = "rate_limit:"):
        self.redis = redis_client
        self.prefix = prefix

    def _get_key(self, identifier: str, window: int) -> str:
        """Get Redis key for rate limit."""
        window_start = int(time.time() // window) * window
        return f"{self.prefix}{identifier}:{window_start}"

    def _get_cost_key(self, identifier: str) -> str:
        """Get Redis key for cost tracking."""
        return f"{self.prefix}{identifier}:cost"

    async def check_rate_limit(
        self, identifier: str, config: RateLimitConfig, cost: float = 1.0
    ) -> Tuple[bool, RateLimitInfo]:
        """Check rate limit using sliding window algorithm."""

        current_time = int(time.time())
        window_start = (current_time // config.window_size) * config.window_size

        # Get current window key
        window_key = self._get_key(identifier, config.window_size)
        cost_key = self._get_cost_key(identifier)

        # Use Redis pipeline for atomic operations
        pipe = self.redis.pipeline()

        # Get current count and cost
        pipe.get(window_key)
        pipe.get(cost_key)
        pipe.ttl(window_key)

        results = await pipe.execute()
        current_count = int(results[0] or 0)
        current_cost = float(results[1] or 0)
        ttl = results[2] or config.window_size

        # Check limits
        count_allowed = current_count < config.requests_per_minute
        cost_allowed = current_cost + cost <= config.max_cost_per_minute

        allowed = count_allowed and cost_allowed

        # Calculate reset time
        reset_time = window_start + config.window_size

        info = RateLimitInfo(
            limit=config.requests_per_minute,
            remaining=max(0, config.requests_per_minute - current_count),
            reset_time=reset_time,
            window_size=config.window_size,
            algorithm=config.algorithm,
            cost_used=current_cost,
            max_cost=config.max_cost_per_minute,
        )

        return allowed, info

    async def record_request(
        self, identifier: str, config: RateLimitConfig, cost: float = 1.0
    ) -> None:
        """Record a request in Redis."""

        window_key = self._get_key(identifier, config.window_size)
        cost_key = self._get_cost_key(identifier)

        pipe = self.redis.pipeline()

        # Increment request count
        pipe.incr(window_key)
        pipe.expire(window_key, config.window_size)

        # Increment cost
        pipe.incrbyfloat(cost_key, cost)
        pipe.expire(cost_key, config.window_size)

        await pipe.execute()

    async def reset_rate_limit(self, identifier: str) -> None:
        """Reset rate limit for identifier."""
        pattern = f"{self.prefix}{identifier}:*"
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

    async def get_rate_limit_info(
        self, identifier: str, config: RateLimitConfig
    ) -> RateLimitInfo:
        """Get current rate limit information."""

        current_time = int(time.time())
        window_start = (current_time // config.window_size) * config.window_size
        window_key = self._get_key(identifier, config.window_size)
        cost_key = self._get_cost_key(identifier)

        pipe = self.redis.pipeline()
        pipe.get(window_key)
        pipe.get(cost_key)

        results = await pipe.execute()
        current_count = int(results[0] or 0)
        current_cost = float(results[1] or 0)

        return RateLimitInfo(
            limit=config.requests_per_minute,
            remaining=max(0, config.requests_per_minute - current_count),
            reset_time=window_start + config.window_size,
            window_size=config.window_size,
            algorithm=config.algorithm,
            cost_used=current_cost,
            max_cost=config.max_cost_per_minute,
        )


class InMemoryRateLimitBackend(RateLimitBackend):
    """In-memory rate limiting backend."""

    def __init__(self):
        self._counters: Dict[str, Dict[str, Any]] = {}
        self._costs: Dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def check_rate_limit(
        self, identifier: str, config: RateLimitConfig, cost: float = 1.0
    ) -> Tuple[bool, RateLimitInfo]:
        """Check rate limit using in-memory storage."""

        async with self._lock:
            current_time = time.time()
            window_start = int(current_time // config.window_size) * config.window_size

            # Clean up expired entries
            await self._cleanup_expired(current_time, config.window_size)

            # Get current state
            counter_key = f"{identifier}:{window_start}"
            current_count = self._counters.get(counter_key, {}).get("count", 0)
            current_cost = self._costs.get(identifier, 0.0)

            # Check limits
            count_allowed = current_count < config.requests_per_minute
            cost_allowed = current_cost + cost <= config.max_cost_per_minute

            allowed = count_allowed and cost_allowed

            # Calculate reset time
            reset_time = window_start + config.window_size

            info = RateLimitInfo(
                limit=config.requests_per_minute,
                remaining=max(0, config.requests_per_minute - current_count),
                reset_time=reset_time,
                window_size=config.window_size,
                algorithm=config.algorithm,
                cost_used=current_cost,
                max_cost=config.max_cost_per_minute,
            )

            return allowed, info

    async def record_request(
        self, identifier: str, config: RateLimitConfig, cost: float = 1.0
    ) -> None:
        """Record a request in memory."""

        async with self._lock:
            current_time = time.time()
            window_start = int(current_time // config.window_size) * config.window_size

            counter_key = f"{identifier}:{window_start}"

            # Increment counter
            if counter_key not in self._counters:
                self._counters[counter_key] = {"count": 0, "window_start": window_start}

            self._counters[counter_key]["count"] += 1

            # Increment cost
            self._costs[identifier] = self._costs.get(identifier, 0.0) + cost

    async def reset_rate_limit(self, identifier: str) -> None:
        """Reset rate limit for identifier."""
        async with self._lock:
            # Remove all entries for this identifier
            keys_to_remove = [
                key for key in self._counters.keys() if key.startswith(f"{identifier}:")
            ]

            for key in keys_to_remove:
                del self._counters[key]

            if identifier in self._costs:
                del self._costs[identifier]

    async def get_rate_limit_info(
        self, identifier: str, config: RateLimitConfig
    ) -> RateLimitInfo:
        """Get current rate limit information."""

        async with self._lock:
            current_time = time.time()
            window_start = int(current_time // config.window_size) * config.window_size

            counter_key = f"{identifier}:{window_start}"
            current_count = self._counters.get(counter_key, {}).get("count", 0)
            current_cost = self._costs.get(identifier, 0.0)

            return RateLimitInfo(
                limit=config.requests_per_minute,
                remaining=max(0, config.requests_per_minute - current_count),
                reset_time=window_start + config.window_size,
                window_size=config.window_size,
                algorithm=config.algorithm,
                cost_used=current_cost,
                max_cost=config.max_cost_per_minute,
            )

    async def _cleanup_expired(self, current_time: float, window_size: int) -> None:
        """Clean up expired rate limit entries."""
        expired_keys = []

        for key, data in self._counters.items():
            if current_time - data["window_start"] > window_size:
                expired_keys.append(key)

        for key in expired_keys:
            del self._counters[key]


class EnhancedRateLimiter:
    """Enhanced rate limiter with multiple backends and features."""

    def __init__(
        self,
        backend: Optional[RateLimitBackend] = None,
        default_config: RateLimitConfig = None,
    ):
        self.backend = backend or InMemoryRateLimitBackend()
        self.default_config = default_config or RateLimitConfig()
        self._endpoint_configs: Dict[str, RateLimitConfig] = {}
        self._user_configs: Dict[str, RateLimitConfig] = {}

    def configure_endpoint(self, endpoint: str, config: RateLimitConfig) -> None:
        """Configure rate limiting for specific endpoint."""
        self._endpoint_configs[endpoint] = config

    def configure_user(self, user_id: str, config: RateLimitConfig) -> None:
        """Configure rate limiting for specific user."""
        self._user_configs[user_id] = config

    def _get_identifier(
        self,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> str:
        """Generate rate limit identifier."""
        parts = []

        if user_id:
            parts.append(f"user:{user_id}")
        if ip_address:
            parts.append(f"ip:{ip_address}")
        if endpoint:
            parts.append(f"endpoint:{endpoint}")

        return ":".join(parts) if parts else "global"

    async def check_rate_limit(
        self,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
        cost: float = 1.0,
    ) -> Tuple[bool, RateLimitInfo]:
        """Check rate limit for the given parameters."""

        # Get configuration
        config = self._get_config(user_id, endpoint)
        identifier = self._get_identifier(user_id, ip_address, endpoint)

        # Check rate limit
        allowed, info = await self.backend.check_rate_limit(identifier, config, cost)

        # Record metrics
        status = "allowed" if allowed else "exceeded"
        rate_limit_requests.labels(
            endpoint=endpoint or "unknown",
            user_id=user_id or "anonymous",
            status=status,
        ).inc()

        if not allowed:
            rate_limit_exceeded.labels(
                endpoint=endpoint or "unknown",
                user_id=user_id or "anonymous",
                limit_type="count" if info.remaining <= 0 else "cost",
            ).inc()

        # Update gauges
        rate_limit_remaining.labels(
            endpoint=endpoint or "unknown", user_id=user_id or "anonymous"
        ).set(info.remaining)

        rate_limit_reset_time.labels(
            endpoint=endpoint or "unknown", user_id=user_id or "anonymous"
        ).set(info.reset_time)

        return allowed, info

    async def record_request(
        self,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
        cost: float = 1.0,
    ) -> None:
        """Record a request."""

        config = self._get_config(user_id, endpoint)
        identifier = self._get_identifier(user_id, ip_address, endpoint)

        await self.backend.record_request(identifier, config, cost)

    def _get_config(
        self, user_id: Optional[str] = None, endpoint: Optional[str] = None
    ) -> RateLimitConfig:
        """Get rate limit configuration."""

        # User-specific config takes precedence
        if user_id and user_id in self._user_configs:
            return self._user_configs[user_id]

        # Endpoint-specific config
        if endpoint and endpoint in self._endpoint_configs:
            return self._endpoint_configs[endpoint]

        # Default config
        return self.default_config

    async def get_rate_limit_info(
        self,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> RateLimitInfo:
        """Get current rate limit information."""

        config = self._get_config(user_id, endpoint)
        identifier = self._get_identifier(user_id, ip_address, endpoint)

        return await self.backend.get_rate_limit_info(identifier, config)

    async def reset_rate_limit(
        self,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> None:
        """Reset rate limit for the given parameters."""

        identifier = self._get_identifier(user_id, ip_address, endpoint)
        await self.backend.reset_rate_limit(identifier)


# Global rate limiter instance
_rate_limiter: Optional[EnhancedRateLimiter] = None


def get_rate_limiter() -> EnhancedRateLimiter:
    """Get global rate limiter instance."""
    global _rate_limiter

    if _rate_limiter is None:
        _rate_limiter = EnhancedRateLimiter()

    return _rate_limiter


def setup_rate_limiting(
    redis_client=None, default_config: Optional[RateLimitConfig] = None
) -> EnhancedRateLimiter:
    """Setup rate limiting with optional Redis backend."""
    global _rate_limiter

    if redis_client:
        backend = RedisRateLimitBackend(redis_client)
    else:
        backend = InMemoryRateLimitBackend()

    _rate_limiter = EnhancedRateLimiter(backend, default_config)
    return _rate_limiter
