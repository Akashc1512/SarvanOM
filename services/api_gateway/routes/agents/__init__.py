"""
Agent routers module.
Organizes all agent-specific route handlers.
"""

from .browser_agent import browser_router
from .pdf_agent import pdf_router
from .knowledge_agent import knowledge_router
from .code_agent import code_router
from .database_agent import database_router
from .crawler_agent import crawler_router

# Export all agent routers
__all__ = [
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