from __future__ import annotations

import time
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from shared.core.config.central_config import initialize_config
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from shared.contracts.query import SynthesisRequest, SynthesisResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


config = initialize_config()

app = FastAPI(
    title=f"{config.service_name}-synthesis",
    version=config.app_version,
    description="Synthesis microservice",
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
    return {"service": "synthesis", "status": "healthy", "timestamp": datetime.now().isoformat()}


_t0 = time.time()
REQUEST_COUNTER = Counter("synthesis_requests_total", "Total synthesis requests")
REQUEST_LATENCY = Histogram("synthesis_request_latency_seconds", "Synthesis request latency")


@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
async def root() -> dict:
    return {"service": "synthesis", "version": config.app_version, "status": "ok"}


@app.post("/synthesize", response_model=SynthesisResponse)
async def synthesize(payload: SynthesisRequest) -> SynthesisResponse:
    REQUEST_COUNTER.inc()
    with REQUEST_LATENCY.time():
        query = payload.query
        sources = payload.sources
        max_tokens = int(payload.max_tokens)
        answer = f"SYNTHESIZED: {query[:100]} (using {len(sources)} sources)"
        return SynthesisResponse(
            answer=answer,
            method="stub_synthesis",
            tokens=min(max_tokens, len(answer)),
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("services.synthesis.main:app", host="0.0.0.0", port=8012, reload=True)


