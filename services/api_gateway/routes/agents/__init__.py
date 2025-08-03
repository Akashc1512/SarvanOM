"""
Agent Routes Package
Contains all individual agent route handlers.
"""

from .browser_agent import router as browser_router
from .pdf_agent import router as pdf_router
from .knowledge_agent import router as knowledge_router

# Export all agent routers
__all__ = [
    "browser_router",
    "pdf_router", 
    "knowledge_router"
]

# Agent router mapping for easy registration
AGENT_ROUTERS = {
    "browser": browser_router,
    "pdf": pdf_router,
    "knowledge": knowledge_router
} 