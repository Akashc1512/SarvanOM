from __future__ import annotations

from fastapi import APIRouter
from shared.core.app_factory import create_app_factory
from shared.core.logging import get_logger
from shared.core.api.api_models import QueryRequest
from services.gateway.routes import ServiceResponse
from datetime import datetime
import time

logger = get_logger(__name__)

# Search Router - Routes to gateway agent orchestrator
search_router = APIRouter()


@search_router.post("/", response_model=ServiceResponse)
async def search(request: QueryRequest):
    """Search endpoint - routes to gateway agent orchestrator."""
    logger.info(f"🔍 Search service request: {request.query[:50]}...")
    
    try:
        # Import gateway agent orchestrator
        from services.gateway.agent_orchestrator import agent_orchestrator, QueryContext
        from services.gateway.real_llm_integration import QueryComplexity, real_llm_processor
        
        # Create query context
        context = QueryContext(
            trace_id=f"search_service_{int(time.time() * 1000)}",
            query=request.query,
            user_id=request.user_id,
            complexity=real_llm_processor.classify_query_complexity(request.query),
            timeout=30.0
        )
        
        # Process with agent orchestrator
        start_time = time.time()
        orchestration_result = await agent_orchestrator.process_query(context)
        processing_time = int((time.time() - start_time) * 1000)
        
        return ServiceResponse(
            status="success" if orchestration_result.get("success") else "partial_success",
            message="Search completed via gateway agent orchestrator",
            service="search",
            timestamp=datetime.now().isoformat(),
            data={
                **orchestration_result,
                "request_metadata": {
                    "orchestration_used": True,
                    "processing_time_ms": processing_time,
                    "service": "search_service",
                    "context": request.context,
                    "source": request.source,
                    "metadata": request.metadata
                }
            },
        )
        
    except Exception as e:
        logger.error(f"Search service error: {e}")
        return ServiceResponse(
            status="error",
            message=f"Search service failed: {str(e)[:100]}",
            service="search",
            timestamp=datetime.now().isoformat(),
            data={
                "query": request.query,
                "user_id": request.user_id,
                "error": str(e),
                "service": "search_service"
            },
        )


def add_search_routes(app):
    """Add search routes to the app."""
    app.include_router(search_router, prefix="/search", tags=["search"])


# Create the FastAPI app using the shared factory
app_factory = create_app_factory(
    service_name="search",
    description="Search microservice - routes to gateway agent orchestrator",
    additional_routes=[add_search_routes],
    health_prefix="search",
    metrics_prefix="internal",
    root_prefix="search"
)

app = app_factory()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.search.main:app", host="0.0.0.0", port=8015, reload=True)
