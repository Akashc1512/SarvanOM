from __future__ import annotations

import logging
from typing import Any, Dict

import httpx

from shared.core.config.central_config import get_central_config


logger = logging.getLogger(__name__)


async def call_retrieval_search(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Call retrieval microservice /search endpoint."""
    cfg = get_central_config()
    base = str(cfg.search_service_url) if cfg.search_service_url else "http://localhost:8015"
    # Prefer dedicated retrieval URL if present
    base = str(cfg.search_service_url)
    url = f"{base}/search"
    timeout = httpx.Timeout(15.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()


async def call_synthesis_generate(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Call synthesis microservice /synthesize endpoint."""
    cfg = get_central_config()
    base = str(cfg.synthesis_service_url) if cfg.synthesis_service_url else "http://localhost:8012"
    url = f"{base}/synthesize"
    timeout = httpx.Timeout(30.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()


