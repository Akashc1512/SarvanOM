from __future__ import annotations

import re
from dotenv import load_dotenv

from fastapi import FastAPI
from shared.core.app_factory import create_app_factory, with_request_metrics
from shared.core.config import get_central_config
from shared.core.logging import get_logger
from shared.core.agents.llm_client import LLMClient
from shared.core.cache import get_cache_manager
from shared.contracts.query import SynthesisRequest, SynthesisResponse

logger = get_logger(__name__)

# Ensure .env is loaded before reading central config
load_dotenv()


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


def add_synthesis_routes(app: FastAPI):
    """Add synthesis-specific routes to the app."""
    
    @app.post("/synthesize", response_model=SynthesisResponse)
    @with_request_metrics("synthesis")
    async def synthesize(payload: SynthesisRequest) -> SynthesisResponse:
        try:
            # Get LLM client and cache
            llm_client = LLMClient()
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
            from services.gateway.real_llm_integration import LLMRequest
            llm_request = LLMRequest(
                prompt=prompt,
                max_tokens=payload.max_tokens,
                temperature=0.3
            )
            response = await llm_client.generate_text(llm_request)
            response_content = response.text

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
            # Return error response without stub implementation
            answer = f"Synthesis failed: {str(e)}. Please check your configuration and try again."
            return SynthesisResponse(
                answer=answer,
                method="error_fallback",
                tokens=min(payload.max_tokens, len(answer)),
                citations=[],
                confidence=0.0,
            )


# Create the FastAPI app using the shared factory
app_factory = create_app_factory(
    service_name="synthesis",
    description="Synthesis microservice with real LLM integration",
    additional_routes=[add_synthesis_routes],
    health_prefix="synthesis",
    metrics_prefix="internal",
    root_prefix="synthesis"
)

app = app_factory()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("services.synthesis.main:app", host="0.0.0.0", port=8002, reload=True)
