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
    title=f"{config.service_name}-auth",
    version=config.app_version,
    description="Auth microservice",
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
        "service": "auth",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }


_t0 = time.time()


@app.get("/metrics")
async def metrics() -> dict:
    return {"service": "auth", "uptime_seconds": int(time.time() - _t0)}


@app.get("/")
async def root() -> dict:
    return {"service": "auth", "version": config.app_version, "status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("services.auth.main:app", host="0.0.0.0", port=8014, reload=True)
