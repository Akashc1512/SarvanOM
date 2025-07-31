"""
Universal Knowledge Hub - Agents Module
Core agent implementations for the knowledge platform.

This module provides:
- Base agent classes and interfaces
- Specialized agents (Retrieval, Synthesis, FactCheck, Citation)
- LLM client integration
- Data models for agent communication

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

from .base_agent import BaseAgent, AgentType, AgentMessage, AgentResult, QueryContext
from .retrieval_agent import RetrievalAgent
from .synthesis_agent import SynthesisAgent
from .factcheck_agent import FactCheckAgent
from .citation_agent import CitationAgent
from .lead_orchestrator import LeadOrchestrator
from .data_models import *
from .llm_client import LLMClient

__all__ = [
    "BaseAgent",
    "AgentType", 
    "AgentMessage",
    "AgentResult",
    "QueryContext",
    "RetrievalAgent",
    "SynthesisAgent",
    "FactCheckAgent",
    "CitationAgent",
    "LeadOrchestrator",
    "LLMClient",
] 