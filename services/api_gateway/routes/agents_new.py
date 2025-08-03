"""
Agent Routes - Modular Implementation
Main router that includes all individual agent route handlers.
This replaces the monolithic agents.py file.
"""

from fastapi import APIRouter
from .agents import AGENT_ROUTERS

# Create main agent router
router = APIRouter(prefix="/agents", tags=["agents"])

# Include all agent routers
for agent_name, agent_router in AGENT_ROUTERS.items():
    router.include_router(agent_router, prefix=f"/{agent_name}")


# Health check endpoint for agents
@router.get("/health")
async def agents_health():
    """Health check for all agent services."""
    return {
        "status": "healthy",
        "agents": list(AGENT_ROUTERS.keys()),
        "message": "All agent services are operational"
    }


# Agent status endpoint
@router.get("/status")
async def agents_status():
    """Get status of all agent services."""
    agent_statuses = {}
    
    for agent_name in AGENT_ROUTERS.keys():
        agent_statuses[agent_name] = {
            "status": "operational",
            "endpoints": [
                f"/agents/{agent_name}/search",
                f"/agents/{agent_name}/process",
                f"/agents/{agent_name}/query"
            ]
        }
    
    return {
        "agents": agent_statuses,
        "total_agents": len(agent_statuses)
    } 