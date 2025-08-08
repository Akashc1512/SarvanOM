from __future__ import annotations

import time
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.core.config.central_config import initialize_config


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


@app.get("/metrics")
async def metrics() -> dict:
    return {"service": "synthesis", "uptime_seconds": int(time.time() - _t0)}


@app.get("/")
async def root() -> dict:
    return {"service": "synthesis", "version": config.app_version, "status": "ok"}


@app.post("/synthesize")
async def synthesize(payload: dict) -> dict:
    query = payload.get("query", "")
    sources = payload.get("sources", [])
    max_tokens = int(payload.get("max_tokens", 256))
    # Stub response for now
    answer = f"SYNTHESIZED: {query[:100]} (using {len(sources)} sources)"
    return {
        "answer": answer,
        "method": "stub_synthesis",
        "tokens": min(max_tokens, len(answer)),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("services.synthesis.main:app", host="0.0.0.0", port=8012, reload=True)


