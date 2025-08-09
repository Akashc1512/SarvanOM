from __future__ import annotations

import logging
from typing import Any, Dict

import httpx

from shared.core.config import get_central_config
from shared.contracts.query import RetrievalIndexRequest


logger = logging.getLogger(__name__)


async def call_retrieval_search(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Call retrieval microservice /search endpoint."""
    cfg = get_central_config()
    base = (
        str(cfg.search_service_url)
        if cfg.search_service_url
        else "http://localhost:8015"
    )
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
    base = (
        str(cfg.synthesis_service_url)
        if cfg.synthesis_service_url
        else "http://localhost:8012"
    )
    url = f"{base}/synthesize"
    timeout = httpx.Timeout(30.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()


async def call_retrieval_index(
    payload: RetrievalIndexRequest | Dict[str, Any]
) -> Dict[str, Any]:
    """Call retrieval microservice /index endpoint to upsert vectors."""
    cfg = get_central_config()
    base = (
        str(cfg.search_service_url)
        if cfg.search_service_url
        else "http://localhost:8002"
    )
    url = f"{base}/index"
    timeout = httpx.Timeout(30.0)
    json_payload = payload if isinstance(payload, dict) else payload.dict()
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=json_payload)
        resp.raise_for_status()
        return resp.json()
