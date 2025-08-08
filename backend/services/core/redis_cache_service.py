"""
Redis-backed Cache Service

Drop-in replacement for CacheService using Redis. Non-blocking via redis.asyncio.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Dict

from redis.asyncio import Redis

from shared.core.config.central_config import get_central_config


logger = logging.getLogger(__name__)


class RedisCacheService:
    def __init__(self, redis_url: Optional[str] = None, default_ttl: int = 3600):
        cfg = get_central_config()
        self.redis_url = redis_url or str(cfg.redis_url) if cfg.redis_url else "redis://localhost:6379/0"
        self._default_ttl = default_ttl
        self._client: Optional[Redis] = None

    async def _get_client(self) -> Redis:
        if self._client is None:
            self._client = Redis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
        return self._client

    async def get(self, key: str) -> Optional[Any]:
        try:
            client = await self._get_client()
            raw = await client.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as e:
            logger.error(f"RedisCacheService.get error: {e}", exc_info=True)
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            client = await self._get_client()
            payload = json.dumps(value, default=str)
            ttl = ttl or self._default_ttl
            await client.set(key, payload, ex=ttl)
            return True
        except Exception as e:
            logger.error(f"RedisCacheService.set error: {e}", exc_info=True)
            return False

    async def delete(self, key: str) -> bool:
        try:
            client = await self._get_client()
            res = await client.delete(key)
            return bool(res)
        except Exception as e:
            logger.error(f"RedisCacheService.delete error: {e}", exc_info=True)
            return False

    async def clear(self) -> bool:
        try:
            client = await self._get_client()
            await client.flushdb()
            return True
        except Exception as e:
            logger.error(f"RedisCacheService.clear error: {e}", exc_info=True)
            return False

    async def get_stats(self) -> Dict[str, Any]:
        try:
            client = await self._get_client()
            info = await client.info()
            return {
                "used_memory": info.get("used_memory_human"),
                "keys": info.get("db0", {}).get("keys") if info.get("db0") else None,
                "uptime": info.get("uptime_in_seconds"),
                "default_ttl": self._default_ttl,
            }
        except Exception as e:
            logger.error(f"RedisCacheService.get_stats error: {e}", exc_info=True)
            return {}


