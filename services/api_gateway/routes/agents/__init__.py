"""
Agent routers module.
Organizes all agent-specific route handlers.
"""

from fastapi import APIRouter

from .browser_agent import router as browser_router
from .pdf_agent import router as pdf_router
from .knowledge_agent import router as knowledge_router
from .code_agent import code_router
from .database_agent import database_router
from .crawler_agent import crawler_router

# Create a combined router for all agents
router = APIRouter(prefix="/agents", tags=["agents"])

# Include all agent routers
router.include_router(browser_router, prefix="/browser", tags=["browser-agent"])
router.include_router(pdf_router, prefix="/pdf", tags=["pdf-agent"])
router.include_router(knowledge_router, prefix="/knowledge", tags=["knowledge-agent"])
router.include_router(code_router, prefix="/code", tags=["code-agent"])
router.include_router(database_router, prefix="/database", tags=["database-agent"])
router.include_router(crawler_router, prefix="/crawler", tags=["crawler-agent"])

# Export all agent routers
__all__ = [
    "router",
    "browser_router",
    "pdf_router", 
    "knowledge_router",
    "code_router",
    "database_router",
    "crawler_router"
]

# Dictionary for easy registration
AGENT_ROUTERS = {
    "browser": browser_router,
    "pdf": pdf_router,
    "knowledge": knowledge_router,
    "code": code_router,
    "database": database_router,
    "crawler": crawler_router
} 