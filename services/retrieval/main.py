from __future__ import annotations

import time
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
from bs4 import BeautifulSoup
import numpy as np

from shared.core.config import get_central_config
from shared.core.logging import get_logger
from shared.core.cache import get_cache_manager
from shared.embeddings.local_embedder import embed_texts
from shared.vectorstores.vector_store_service import (
    ChromaVectorStore,
    QdrantVectorStore,
    InMemoryVectorStore,
    VectorDocument,
)
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from shared.contracts.query import (
    RetrievalSearchRequest,
    RetrievalSearchResponse,
    RetrievalIndexRequest,
    RetrievalIndexResponse,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


# Ensure environment variables from .env are loaded for this service
load_dotenv()
config = get_central_config()

app = FastAPI(
    title=f"{config.service_name}-retrieval",
    version=config.app_version,
    description="Retrieval microservice with real vector search",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=bool(config.cors_credentials),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {
        "service": "retrieval",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }


_service_start = time.time()
REQUEST_COUNTER = Counter("retrieval_requests_total", "Total retrieval requests")
REQUEST_LATENCY = Histogram(
    "retrieval_request_latency_seconds", "Retrieval request latency"
)


def _init_vector_store():
    cfg = get_central_config()
    # Default to in-memory when no corpus is provided
    provider = getattr(cfg, "vector_db_provider", "inmemory").lower()
    if provider == "qdrant":
        # Try Qdrant first, fallback to Chroma if unavailable
        try:
            return QdrantVectorStore(
                url=str(cfg.qdrant_url),
                api_key=(
                    cfg.qdrant_api_key.get_secret_value()
                    if cfg.qdrant_api_key
                    else None
                ),
                collection=str(cfg.qdrant_collection),
                vector_size=int(getattr(cfg, "embedding_dimension", 384)),
            )
        except Exception as qerr:
            logger.error("Qdrant unavailable, falling back to Chroma", error=str(qerr))
            return ChromaVectorStore(collection_name="knowledge")
    elif provider == "inmemory" or provider == "memory":
        return InMemoryVectorStore()
    # default to chroma (local/in-process)
    return ChromaVectorStore(collection_name="knowledge")


VECTOR_STORE = _init_vector_store()


@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
async def root() -> dict:
    return {
        "service": "retrieval",
        "version": config.app_version,
        "status": "ok",
    }


@app.post("/search", response_model=RetrievalSearchResponse)
async def search(payload: RetrievalSearchRequest) -> RetrievalSearchResponse:
    REQUEST_COUNTER.inc()

    with REQUEST_LATENCY.time():
        try:
            # Get cache
            cache = get_cache_manager()

            # Create cache key
            cache_key = f"search:{hash(payload.query)}:{payload.max_results}"

            # Check cache first
            cached_result = await cache.get(cache_key)
            if cached_result:
                logger.info("Cache hit for search", query=payload.query[:100])
                return RetrievalSearchResponse(**cached_result)

            # Generate embeddings for query
            query_embedding = embed_texts([payload.query])[0]

            # Perform vector search (may be empty if no corpus indexed)
            search_results = await VECTOR_STORE.search(
                query_embedding=query_embedding, top_k=payload.max_results
            )

            # Format results
            sources = []
            relevance_scores = []

            for result in search_results:
                if isinstance(result, tuple):
                    doc, score = result
                    sources.append(
                        {
                            "id": doc.id,
                            "content": doc.text,
                            "metadata": doc.metadata,
                            "score": score,
                        }
                    )
                    relevance_scores.append(score)
                else:
                    # Handle dict format
                    sources.append(result)
                    relevance_scores.append(result.get("score", 0.0))

            # If no results, try ephemeral web search (Brave/SerpAPI) without persistence
            if len(sources) == 0:
                ephemeral_sources = _ephemeral_web_search(
                    payload.query, payload.max_results
                )
                sources = ephemeral_sources
                relevance_scores = [s.get("score", 0.0) for s in sources]
                method = "web_search_ephemeral"
            else:
                method = "vector_search"

            # Create response
            response = RetrievalSearchResponse(
                sources=sources,
                method=method,
                total_results=len(sources),
                relevance_scores=relevance_scores,
                limit=payload.max_results,
            )

            # Cache result for 1 hour
            await cache.set(cache_key, response.dict())

            logger.info(
                "Search completed",
                query=payload.query[:100],
                results_count=len(sources),
            )

            return response

        except Exception as e:
            logger.error("Search failed", error=str(e), query=payload.query[:100])
            # Fallback to empty results
            return RetrievalSearchResponse(
                sources=[],
                method="stub_search_fallback",
                total_results=0,
                relevance_scores=[],
                limit=payload.max_results,
            )


def _ephemeral_web_search(query: str, top_k: int) -> list[dict]:
    """Perform a web search and construct in-memory snippets without persistence."""
    urls = []
    results = []
    brave_key = os.getenv("BRAVE_SEARCH_API_KEY")
    serpapi_key = os.getenv("SERPAPI_KEY")

    try:
        if brave_key:
            headers = {"X-Subscription-Token": brave_key}
            params = {"q": query, "count": max(top_k, 3)}
            r = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
                timeout=10,
            )
            if r.ok:
                data = r.json()
                for item in (data.get("web", {}).get("results", []) or [])[: top_k * 2]:
                    url = item.get("url")
                    if url:
                        urls.append(
                            (item.get("title", url), url, item.get("description", ""))
                        )
        elif serpapi_key:
            params = {
                "engine": "google",
                "q": query,
                "api_key": serpapi_key,
                "num": max(top_k, 3),
            }
            r = requests.get(
                "https://serpapi.com/search.json", params=params, timeout=10
            )
            if r.ok:
                data = r.json()
                for item in (data.get("organic_results", []) or [])[: top_k * 2]:
                    url = item.get("link")
                    if url:
                        urls.append(
                            (item.get("title", url), url, item.get("snippet", ""))
                        )
    except Exception:
        pass

    # Fetch and build snippets
    query_vec = np.array(embed_texts([query])[0], dtype=float)
    scored = []
    for title, url, snippet in urls[: top_k * 2]:
        try:
            page_text = _fetch_text(url)
            text = (snippet + "\n\n" + page_text)[:2000]
            doc_vec = np.array(embed_texts([text])[0], dtype=float)
            sim = float(
                np.dot(query_vec, doc_vec)
                / (np.linalg.norm(query_vec) * (np.linalg.norm(doc_vec) + 1e-9))
            )
            scored.append(
                {
                    "id": url,
                    "content": text,
                    "metadata": {"title": title, "url": url},
                    "score": sim,
                }
            )
        except Exception:
            continue

    scored.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    return scored[:top_k]


def _fetch_text(url: str) -> str:
    r = requests.get(url, headers={"User-Agent": "SarvanOMBot/1.0"}, timeout=10)
    if not r.ok:
        return ""
    soup = BeautifulSoup(r.text, "html.parser")
    # Remove scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = " ".join(soup.get_text(separator=" ").split())
    return text


@app.post("/index", response_model=RetrievalIndexResponse)
async def index(payload: RetrievalIndexRequest) -> RetrievalIndexResponse:
    try:
        # Validate input
        payload.validate_lengths()

        # Generate embeddings
        embeddings = embed_texts(payload.texts)

        # Create vector documents
        documents = []
        for i, (doc_id, text, embedding) in enumerate(
            zip(payload.ids, payload.texts, embeddings)
        ):
            metadata = payload.metadatas[i] if i < len(payload.metadatas) else {}
            documents.append(
                VectorDocument(
                    id=doc_id, text=text, embedding=embedding, metadata=metadata
                )
            )

        # Index documents
        upserted_count = await VECTOR_STORE.upsert(documents)

        logger.info(
            "Indexing completed",
            documents_count=len(documents),
            upserted_count=upserted_count,
        )

        return RetrievalIndexResponse(upserted=upserted_count)

    except Exception as e:
        logger.error("Indexing failed", error=str(e))
        return RetrievalIndexResponse(upserted=0)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("services.retrieval.main:app", host="0.0.0.0", port=8001, reload=True)
