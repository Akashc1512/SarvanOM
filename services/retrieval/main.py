from __future__ import annotations

import time
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from shared.core.config.central_config import initialize_config, get_central_config
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from shared.contracts.query import (
    RetrievalSearchRequest,
    RetrievalSearchResponse,
    RetrievalIndexRequest,
    RetrievalIndexResponse,
)
from shared.embeddings.local_embedder import embed_texts
from shared.vectorstores.vector_store_service import (
    ChromaVectorStore,
    QdrantVectorStore,
    InMemoryVectorStore,
    VectorDocument,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


config = initialize_config()

app = FastAPI(
    title=f"{config.service_name}-retrieval",
    version=config.app_version,
    description="Retrieval microservice",
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
REQUEST_LATENCY = Histogram("retrieval_request_latency_seconds", "Retrieval request latency")
def _init_vector_store():
    cfg = get_central_config()
    provider = getattr(cfg, "vector_db_provider", "chroma").lower()
    if provider == "qdrant":
        return QdrantVectorStore(
            url=str(cfg.qdrant_url),
            api_key=(cfg.qdrant_api_key.get_secret_value() if cfg.qdrant_api_key else None),
            collection=str(cfg.qdrant_collection),
            vector_size=int(getattr(cfg, "embedding_dimension", 384)),
        )
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
        query = payload.query
        max_results = int(payload.max_results)
        # For a real system, compute embedding of query and search vector store
        # Here we compute an embedding and query Chroma
        q_vec = (await _embed_async([query]))[0]
        hits = await VECTOR_STORE.search(q_vec, top_k=max_results)
        sources = [
            {"id": d.id, "text": d.text, "score": score, **d.metadata}
            for (d, score) in hits
        ]
        return RetrievalSearchResponse(
            sources=sources,
            method="chroma_retrieval",
            total_results=len(sources),
            relevance_scores=[float(s["score"]) for s in sources],
            limit=max_results,
        )


@app.post("/index", response_model=RetrievalIndexResponse)
async def index(payload: RetrievalIndexRequest) -> RetrievalIndexResponse:
    payload.validate_lengths()
    # Embed texts locally
    vectors = await _embed_async(payload.texts)
    docs = [
        VectorDocument(id=i, text=t, embedding=v, metadata=(payload.metadatas[idx] if payload.metadatas else {}))
        for idx, (i, t, v) in enumerate(zip(payload.ids, payload.texts, vectors))
    ]
    upserted = await VECTOR_STORE.upsert(docs)
    return RetrievalIndexResponse(upserted=upserted)


async def _embed_async(texts: list[str]) -> list[list[float]]:
    # sentence-transformers is sync; run in a thread to avoid blocking the loop
    import anyio

    def _run():
        # Chunk to avoid large memory spikes
        CHUNK = 128
        if len(texts) <= CHUNK:
            return embed_texts(texts)
        out: list[list[float]] = []
        for i in range(0, len(texts), CHUNK):
            out.extend(embed_texts(texts[i : i + CHUNK]))
        return out

    return await anyio.to_thread.run_sync(_run)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("services.retrieval.main:app", host="0.0.0.0", port=8011, reload=True)


