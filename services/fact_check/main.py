from __future__ import annotations

from shared.core.app_factory import create_app_factory
from .routes import router as fact_check_router

# Create the FastAPI app using the shared factory
app = create_app_factory(
    service_name="fact_check",
    description="Fact-check microservice",
    additional_routes=[fact_check_router],
    health_prefix="fact-check",
    metrics_prefix="internal",
    root_prefix="fact-check"
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.fact_check.main:app", host="0.0.0.0", port=8013, reload=True)
