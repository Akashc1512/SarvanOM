"""
Universal Knowledge Hub - Agents Module
Core agent implementations for the knowledge platform.

This module provides:
- Base agent classes and interfaces
- Specialized agents (Retrieval, Synthesis, FactCheck, Citation)
- LLM client integration
- Data models for agent communication
- Graph database components (GraphDBClient, KnowledgeGraphService)

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

from .base_agent import BaseAgent, AgentType, AgentMessage, AgentResult, QueryContext
from .synthesis_agent import SynthesisAgent
from .factcheck_agent import FactCheckAgent
from .citation_agent import CitationAgent
from .retrieval_agent import RetrievalAgent

__all__ = [
    "BaseAgent",
    "AgentType",
    "AgentMessage",
    "AgentResult",
    "QueryContext",
    "SynthesisAgent",
    "FactCheckAgent",
    "CitationAgent",
    "RetrievalAgent",
]
