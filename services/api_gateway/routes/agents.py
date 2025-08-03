"""
Agent Routes for API Gateway - Modular Implementation

This module provides the main agent router that includes all individual agent modules.
It replaces the monolithic agents.py with a clean, modular structure.
"""

from .agents_new import agents_router

# Export the main agents router for backward compatibility
router = agents_router

# Import agent handlers (will be injected)
_agent_handler = None


def set_dependencies(agent_handler_func):
    """Set dependencies for the agent routes."""
    global _agent_handler
    _agent_handler = agent_handler_func


# Legacy compatibility - these functions are now handled by individual agent modules
async def agent_handler(*args, **kwargs):
    """
    Legacy agent handler for backward compatibility.
    This function is deprecated and will be removed in future versions.
    Use the individual agent modules instead.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("agent_handler is deprecated. Use individual agent modules instead.")
    
    # Return a mock response for backward compatibility
    return {
        "success": False,
        "error": "agent_handler is deprecated. Use individual agent modules instead.",
        "message": "Please update your code to use the new modular agent structure."
    } 