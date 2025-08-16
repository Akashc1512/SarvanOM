from __future__ import annotations

import logging
from typing import Any, Dict

import httpx

from shared.core.config import get_central_config
from shared.contracts.query import (
    RetrievalIndexRequest,
    VectorEmbedRequest,
    VectorSearchRequest,
)
from shared.core.api.api_models import LoginRequest, RegisterRequest


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
    json_payload = payload if isinstance(payload, dict) else payload.model_dump()
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=json_payload)
        resp.raise_for_status()
        return resp.json()


async def call_retrieval_embed(
    payload: VectorEmbedRequest | Dict[str, Any]
) -> Dict[str, Any]:
    """Call retrieval microservice /embed endpoint for text embedding."""
    cfg = get_central_config()
    base = (
        str(cfg.search_service_url)
        if cfg.search_service_url
        else "http://localhost:8001"
    )
    url = f"{base}/embed"
    timeout = httpx.Timeout(15.0)
    json_payload = payload if isinstance(payload, dict) else payload.model_dump()
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=json_payload)
        resp.raise_for_status()
        return resp.json()


async def call_retrieval_vector_search(
    payload: VectorSearchRequest | Dict[str, Any]
) -> Dict[str, Any]:
    """Call retrieval microservice /vector-search endpoint for similarity search."""
    cfg = get_central_config()
    base = (
        str(cfg.search_service_url)
        if cfg.search_service_url
        else "http://localhost:8001"
    )
    url = f"{base}/vector-search"
    timeout = httpx.Timeout(15.0)
    json_payload = payload if isinstance(payload, dict) else payload.model_dump()
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=json_payload)
        resp.raise_for_status()
        return resp.json()


# Authentication service client functions
async def call_auth_login(payload: LoginRequest | Dict[str, Any]) -> Dict[str, Any]:
    """Call auth microservice /auth/login endpoint."""
    cfg = get_central_config()
    base = (
        str(cfg.auth_service_url)
        if cfg.auth_service_url
        else "http://localhost:8014"
    )
    url = f"{base}/auth/login"
    timeout = httpx.Timeout(15.0)
    json_payload = payload if isinstance(payload, dict) else payload.model_dump()
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=json_payload)
        resp.raise_for_status()
        return resp.json()


async def call_auth_register(payload: RegisterRequest | Dict[str, Any]) -> Dict[str, Any]:
    """Call auth microservice /auth/register endpoint."""
    cfg = get_central_config()
    base = (
        str(cfg.auth_service_url)
        if cfg.auth_service_url
        else "http://localhost:8014"
    )
    url = f"{base}/auth/register"
    timeout = httpx.Timeout(15.0)
    json_payload = payload if isinstance(payload, dict) else payload.model_dump()
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=json_payload)
        resp.raise_for_status()
        return resp.json()


async def call_auth_refresh(refresh_token: str) -> Dict[str, Any]:
    """Call auth microservice /auth/refresh endpoint."""
    cfg = get_central_config()
    base = (
        str(cfg.auth_service_url)
        if cfg.auth_service_url
        else "http://localhost:8014"
    )
    url = f"{base}/auth/refresh"
    timeout = httpx.Timeout(15.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, params={"refresh_token": refresh_token})
        resp.raise_for_status()
        return resp.json()


async def call_auth_logout() -> Dict[str, Any]:
    """Call auth microservice /auth/logout endpoint."""
    cfg = get_central_config()
    base = (
        str(cfg.auth_service_url)
        if cfg.auth_service_url
        else "http://localhost:8014"
    )
    url = f"{base}/auth/logout"
    timeout = httpx.Timeout(15.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url)
        resp.raise_for_status()
        return resp.json()


async def call_auth_me() -> Dict[str, Any]:
    """Call auth microservice /auth/me endpoint."""
    cfg = get_central_config()
    base = (
        str(cfg.auth_service_url)
        if cfg.auth_service_url
        else "http://localhost:8014"
    )
    url = f"{base}/auth/me"
    timeout = httpx.Timeout(15.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()


async def call_factcheck_verify(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Call fact-check microservice /verify endpoint."""
    cfg = get_central_config()
    base = (
        str(cfg.factcheck_service_url)
        if cfg.factcheck_service_url
        else "http://localhost:8013"
    )
    url = f"{base}/verify"
    timeout = httpx.Timeout(30.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()


async def call_synthesis_synthesize(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Call synthesis microservice /synthesize endpoint."""
    cfg = get_central_config()
    base = (
        str(cfg.synthesis_service_url)
        if cfg.synthesis_service_url
        else "http://localhost:8003"
    )
    url = f"{base}/synthesize"
    timeout = httpx.Timeout(60.0)  # Synthesis can take longer
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()


async def call_synthesis_citations(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Call synthesis microservice /citations endpoint."""
    cfg = get_central_config()
    base = (
        str(cfg.synthesis_service_url)
        if cfg.synthesis_service_url
        else "http://localhost:8003"
    )
    url = f"{base}/citations"
    timeout = httpx.Timeout(30.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()
