from __future__ import annotations

from shared.core.app_factory import create_app_factory
from services.auth.routes import router as auth_router

# Create a function to mount the auth router
def mount_auth_routes(app):
    """Mount authentication routes to the FastAPI app"""
    app.include_router(auth_router)

# Create the FastAPI app using the shared factory with auth routes
app_factory = create_app_factory(
    service_name="auth",
    description="Authentication microservice",
    additional_routes=[mount_auth_routes],
    health_prefix="auth",
    metrics_prefix="internal",
    root_prefix="auth"
)

app = app_factory()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.auth.main:app", host="0.0.0.0", port=8012, reload=True)
