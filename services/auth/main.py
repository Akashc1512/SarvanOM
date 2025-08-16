from __future__ import annotations

from shared.core.app_factory import create_app_factory
from services.auth.routes import router as auth_router

# Create the FastAPI app using the shared factory with auth routes
app = create_app_factory(
    service_name="auth",
    description="Authentication microservice",
    port=8014,
    additional_routes=[auth_router],
    health_prefix="auth",
    metrics_prefix="internal",
    root_prefix="auth"
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.auth.main:app", host="0.0.0.0", port=8014, reload=True)
