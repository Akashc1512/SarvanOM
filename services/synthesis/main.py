from __future__ import annotations

import time
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from shared.core.config import get_central_config
from shared.core.logging import get_logger
from shared.core.llm_client_v3 import get_llm_client_v3
from shared.core.cache import get_cache_manager
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from shared.contracts.query import SynthesisRequest, SynthesisResponse

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


# Ensure .env is loaded before reading central config
load_dotenv()
config = get_central_config()

app = FastAPI(
    title=f"{config.service_name}-synthesis",
    version=config.app_version,
    description="Synthesis microservice with real LLM integration",
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
        "service": "synthesis",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }


_t0 = time.time()
REQUEST_COUNTER = Counter("synthesis_requests_total", "Total synthesis requests")
REQUEST_LATENCY = Histogram(
    "synthesis_request_latency_seconds", "Synthesis request latency"
)


@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
async def root() -> dict:
    return {"service": "synthesis", "version": config.app_version, "status": "ok"}


def format_sources_for_llm(sources: list) -> str:
    """Format sources for LLM consumption."""
    formatted_sources = []
    for i, source in enumerate(sources, 1):
        formatted_sources.append(f"Source {i}: {source.get('content', '')}")
    return "\n\n".join(formatted_sources)


def extract_citations(content: str) -> list:
    """Extract citations from LLM response."""
    import re

    citations = []
    # Look for citation pattern 【source†Lx-Ly】
    citation_pattern = r"【([^†]+)†L(\d+)-L(\d+)】"
    matches = re.findall(citation_pattern, content)
    for match in matches:
        citations.append(
            {"source": match[0], "start_line": int(match[1]), "end_line": int(match[2])}
        )
    return citations


def calculate_confidence(content: str, sources: list) -> float:
    """Calculate confidence score for synthesis."""
    # Simple confidence calculation based on content length and source count
    if not sources:
        return 0.0

    content_length = len(content)
    source_count = len(sources)

    # Basic confidence calculation
    base_confidence = min(0.9, source_count * 0.1)
    length_confidence = min(0.1, content_length / 1000 * 0.1)

    return min(1.0, base_confidence + length_confidence)


@app.post("/synthesize", response_model=SynthesisResponse)
async def synthesize(payload: SynthesisRequest) -> SynthesisResponse:
    REQUEST_COUNTER.inc()

    with REQUEST_LATENCY.time():
        try:
            # Get LLM client and cache
            llm_client = get_llm_client_v3()
            cache = get_cache_manager()

            # Create cache key
            cache_key = f"synthesis:{hash(payload.query)}:{hash(str(payload.sources))}"

            # Check cache first
            cached_result = await cache.get(cache_key)
            if cached_result:
                logger.info("Cache hit for synthesis", query=payload.query[:100])
                return SynthesisResponse(**cached_result)

            # Format sources for LLM
            sources_text = format_sources_for_llm(payload.sources)

            # Create synthesis prompt
            prompt = f"""
            Query: {payload.query}
            
            Sources:
            {sources_text}
            
            Instructions:
            1. Generate a comprehensive answer using ONLY the provided sources
            2. Include citations in format 【source†Lx-Ly】
            3. If information is missing from sources, say so
            4. Structure the answer clearly with headings if needed
            5. Maximum {payload.max_tokens} tokens
            6. Be accurate and factual
            """

            # Call LLM
            response_content = await llm_client.generate_text(
                prompt=prompt, max_tokens=payload.max_tokens, temperature=0.3
            )

            # Extract citations
            citations = extract_citations(response_content)

            # Calculate confidence
            confidence = calculate_confidence(response_content, payload.sources)

            # Create result
            result = SynthesisResponse(
                answer=response_content,
                method="llm_synthesis",
                tokens=len(response_content),
                citations=citations,
                confidence=confidence,
            )

            # Cache result for 1 hour
            await cache.set(cache_key, result.dict())

            logger.info(
                "Synthesis completed",
                query=payload.query[:100],
                tokens=result.tokens,
                confidence=confidence,
            )

            return result

        except Exception as e:
            logger.error("Synthesis failed", error=str(e), query=payload.query[:100])
            # Fallback to stub implementation
            answer = f"SYNTHESIZED: {payload.query[:100]} (using {len(payload.sources)} sources) - Error: {str(e)}"
            return SynthesisResponse(
                answer=answer,
                method="stub_synthesis_fallback",
                tokens=min(payload.max_tokens, len(answer)),
                citations=[],
                confidence=0.0,
            )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("services.synthesis.main:app", host="0.0.0.0", port=8002, reload=True)
