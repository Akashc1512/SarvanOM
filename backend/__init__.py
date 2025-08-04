"""
Backend Services Package

This package contains all the modular backend services for the knowledge platform:
- retrieval: Search and retrieval services
- fact_check: Fact checking and validation services  
- synthesis: Content synthesis and generation services
- auth: Authentication and authorization services
- crawler: Web crawling and data collection services
- vector: Vector database and embedding services
- graph: Knowledge graph and relationship services
- gateway: API gateway and routing services

Each service is designed to be independent and communicate through the gateway layer.
"""

__version__ = "1.0.0"
__author__ = "Universal Knowledge Platform Engineering Team"

from . import retrieval
from . import fact_check
from . import synthesis
from . import auth
from . import crawler
from . import vector
from . import graph
from . import gateway

__all__ = [
    "retrieval",
    "fact_check", 
    "synthesis",
    "auth",
    "crawler",
    "vector",
    "graph",
    "gateway"
] 