from __future__ import annotations

import time
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from shared.core.config.central_config import initialize_config, get_central_config
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from shared.contracts.query import RetrievalSearchRequest, RetrievalSearchResponse


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
        return RetrievalSearchResponse(
            sources=[{"title": "stub", "snippet": query[:80]}],
            method="stub_retrieval",
            total_results=1,
            relevance_scores=[0.5],
            limit=max_results,
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("services.retrieval.main:app", host="0.0.0.0", port=8011, reload=True)


