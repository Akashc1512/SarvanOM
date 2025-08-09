"""
Standardized Agent Interface Implementations

This module implements the standardized agent interface for all specialized agents,
ensuring they all implement the common BaseAgent.execute(context) method.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from .base_agent import BaseAgent, AgentResult, QueryContext, AgentType
from ..unified_logging import get_logger, log_agent_lifecycle, log_execution_time

logger = get_logger(__name__)


# Extend AgentType enum to include all agent types
class ExtendedAgentType(Enum):
    """Extended agent types for all specialized agents."""

    # Core agents
    ORCHESTRATOR = "orchestrator"
    RETRIEVAL = "retrieval"
    FACT_CHECK = "fact_check"
    SYNTHESIS = "synthesis"
    CITATION = "citation"

    # Specialized agents
    BROWSER = "browser"
    PDF = "pdf"
    CODE = "code"
    DATABASE = "database"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    CRAWLER = "crawler"
    WEB_SEARCH = "web_search"


@dataclass
class AgentCapabilities:
    """Defines what an agent can do and its requirements."""

    can_run_parallel: bool = True
    requires_internet: bool = False
    requires_database: bool = False
    max_concurrent_tasks: int = 5
    timeout_seconds: int = 30
    dependencies: List[ExtendedAgentType] = field(default_factory=list)
    output_types: List[str] = field(default_factory=list)


class StandardizedBrowserAgent(BaseAgent):
    """Standardized browser automation agent."""

    def __init__(self):
        super().__init__("browser_agent", ExtendedAgentType.BROWSER)
        self.capabilities = AgentCapabilities(
            requires_internet=True,
            output_types=["webpage_content", "search_results", "screenshots"],
        )

    async def process_task(
        self, task: Dict[str, Any], context: QueryContext
    ) -> Dict[str, Any]:
        """Process browser automation task."""
        try:
            # Import browser service
            from services.api_gateway.di.providers import get_service_provider

            service_provider = get_service_provider()
            browser_service = service_provider.get_browser_service()

            query = task.get("query", context.query)

            log_agent_lifecycle(
                logger,
                "browser",
                "started",
                task_type=task.get("type", "browser_search"),
                query=query,
            )

            # Perform browser search/automation
            result = await browser_service.search_web(
                query=query,
                max_results=task.get("max_results", 5),
                include_content=task.get("include_content", True),
            )

            log_agent_lifecycle(
                logger,
                "browser",
                "completed",
                results_count=len(result.get("results", [])),
            )

            return {
                "success": True,
                "data": result,
                "confidence": 0.8,
                "metadata": {
                    "agent_type": "browser",
                    "results_count": len(result.get("results", [])),
                    "search_query": query,
                },
            }

        except Exception as e:
            logger.error(f"Browser agent error: {e}", agent="browser", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "metadata": {"agent_type": "browser", "error_type": type(e).__name__},
            }


class StandardizedPDFAgent(BaseAgent):
    """Standardized PDF processing agent."""

    def __init__(self):
        super().__init__("pdf_agent", ExtendedAgentType.PDF)
        self.capabilities = AgentCapabilities(
            output_types=["extracted_text", "document_metadata", "structured_content"]
        )

    async def process_task(
        self, task: Dict[str, Any], context: QueryContext
    ) -> Dict[str, Any]:
        """Process PDF extraction/analysis task."""
        try:
            from services.api_gateway.di.providers import get_service_provider

            service_provider = get_service_provider()
            pdf_service = service_provider.get_pdf_service()

            pdf_data = task.get("pdf_data")
            pdf_url = task.get("pdf_url")

            log_agent_lifecycle(
                logger, "pdf", "started", has_data=bool(pdf_data), has_url=bool(pdf_url)
            )

            if pdf_data:
                result = await pdf_service.extract_text_from_data(pdf_data)
            elif pdf_url:
                result = await pdf_service.extract_text_from_url(pdf_url)
            else:
                return {
                    "success": False,
                    "error": "No PDF data or URL provided",
                    "metadata": {"agent_type": "pdf"},
                }

            log_agent_lifecycle(
                logger, "pdf", "completed", text_length=len(result.get("text", ""))
            )

            return {
                "success": True,
                "data": result,
                "confidence": 0.9,
                "metadata": {
                    "agent_type": "pdf",
                    "text_length": len(result.get("text", "")),
                    "page_count": result.get("page_count", 0),
                },
            }

        except Exception as e:
            logger.error(f"PDF agent error: {e}", agent="pdf", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "metadata": {"agent_type": "pdf", "error_type": type(e).__name__},
            }


class StandardizedCodeAgent(BaseAgent):
    """Standardized code execution and analysis agent."""

    def __init__(self):
        super().__init__("code_agent", ExtendedAgentType.CODE)
        self.capabilities = AgentCapabilities(
            output_types=["code_execution_result", "code_analysis", "error_trace"]
        )

    async def process_task(
        self, task: Dict[str, Any], context: QueryContext
    ) -> Dict[str, Any]:
        """Process code execution/analysis task."""
        try:
            from services.api_gateway.di.providers import get_service_provider

            service_provider = get_service_provider()
            code_service = service_provider.get_code_service()

            code = task.get("code")
            language = task.get("language", "python")

            log_agent_lifecycle(
                logger,
                "code",
                "started",
                language=language,
                code_length=len(code) if code else 0,
            )

            if not code:
                return {
                    "success": False,
                    "error": "No code provided for execution",
                    "metadata": {"agent_type": "code"},
                }

            result = await code_service.execute_code(
                code=code, language=language, timeout=task.get("timeout", 10)
            )

            log_agent_lifecycle(
                logger, "code", "completed", success=result.get("success", False)
            )

            return {
                "success": True,
                "data": result,
                "confidence": 0.85,
                "metadata": {
                    "agent_type": "code",
                    "language": language,
                    "execution_time": result.get("execution_time", 0),
                },
            }

        except Exception as e:
            logger.error(f"Code agent error: {e}", agent="code", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "metadata": {"agent_type": "code", "error_type": type(e).__name__},
            }


class StandardizedDatabaseAgent(BaseAgent):
    """Standardized database query and analysis agent."""

    def __init__(self):
        super().__init__("database_agent", ExtendedAgentType.DATABASE)
        self.capabilities = AgentCapabilities(
            requires_database=True,
            output_types=["query_results", "database_schema", "data_analysis"],
        )

    async def process_task(
        self, task: Dict[str, Any], context: QueryContext
    ) -> Dict[str, Any]:
        """Process database query/analysis task."""
        try:
            from services.api_gateway.di.providers import get_service_provider

            service_provider = get_service_provider()
            database_service = service_provider.get_database_service()

            query_text = task.get("query", context.query)
            operation = task.get("operation", "search")

            log_agent_lifecycle(
                logger, "database", "started", operation=operation, query=query_text
            )

            if operation == "search":
                result = await database_service.search_knowledge(query_text)
            elif operation == "query":
                sql_query = task.get("sql_query")
                result = await database_service.execute_query(sql_query)
            else:
                return {
                    "success": False,
                    "error": f"Unknown database operation: {operation}",
                    "metadata": {"agent_type": "database"},
                }

            log_agent_lifecycle(
                logger,
                "database",
                "completed",
                results_count=len(result.get("results", [])),
            )

            return {
                "success": True,
                "data": result,
                "confidence": 0.9,
                "metadata": {
                    "agent_type": "database",
                    "operation": operation,
                    "results_count": len(result.get("results", [])),
                },
            }

        except Exception as e:
            logger.error(f"Database agent error: {e}", agent="database", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "metadata": {"agent_type": "database", "error_type": type(e).__name__},
            }


class StandardizedKnowledgeGraphAgent(BaseAgent):
    """Standardized knowledge graph agent."""

    def __init__(self):
        super().__init__("knowledge_graph_agent", ExtendedAgentType.KNOWLEDGE_GRAPH)
        self.capabilities = AgentCapabilities(
            requires_database=True,
            output_types=["graph_nodes", "relationships", "graph_analysis"],
        )

    async def process_task(
        self, task: Dict[str, Any], context: QueryContext
    ) -> Dict[str, Any]:
        """Process knowledge graph task."""
        try:
            from services.api_gateway.di.providers import get_service_provider

            service_provider = get_service_provider()
            knowledge_service = service_provider.get_knowledge_service()

            query = task.get("query", context.query)
            operation = task.get("operation", "search")

            log_agent_lifecycle(
                logger, "knowledge_graph", "started", operation=operation, query=query
            )

            if operation == "search":
                result = await knowledge_service.search_graph(query)
            elif operation == "traverse":
                start_node = task.get("start_node")
                result = await knowledge_service.traverse_graph(start_node, query)
            else:
                return {
                    "success": False,
                    "error": f"Unknown knowledge graph operation: {operation}",
                    "metadata": {"agent_type": "knowledge_graph"},
                }

            log_agent_lifecycle(
                logger,
                "knowledge_graph",
                "completed",
                nodes_count=len(result.get("nodes", [])),
            )

            return {
                "success": True,
                "data": result,
                "confidence": 0.85,
                "metadata": {
                    "agent_type": "knowledge_graph",
                    "operation": operation,
                    "nodes_count": len(result.get("nodes", [])),
                    "relationships_count": len(result.get("relationships", [])),
                },
            }

        except Exception as e:
            logger.error(
                f"Knowledge graph agent error: {e}",
                agent="knowledge_graph",
                error=str(e),
            )
            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "agent_type": "knowledge_graph",
                    "error_type": type(e).__name__,
                },
            }


class StandardizedCrawlerAgent(BaseAgent):
    """Standardized web crawler agent."""

    def __init__(self):
        super().__init__("crawler_agent", ExtendedAgentType.CRAWLER)
        self.capabilities = AgentCapabilities(
            requires_internet=True,
            output_types=["crawled_content", "site_structure", "extracted_data"],
        )

    async def process_task(
        self, task: Dict[str, Any], context: QueryContext
    ) -> Dict[str, Any]:
        """Process web crawling task."""
        try:
            from services.api_gateway.di.providers import get_service_provider

            service_provider = get_service_provider()
            crawler_service = service_provider.get_crawler_service()

            url = task.get("url")
            depth = task.get("depth", 1)

            log_agent_lifecycle(logger, "crawler", "started", url=url, depth=depth)

            if not url:
                return {
                    "success": False,
                    "error": "No URL provided for crawling",
                    "metadata": {"agent_type": "crawler"},
                }

            result = await crawler_service.crawl_website(
                url=url, max_depth=depth, max_pages=task.get("max_pages", 10)
            )

            log_agent_lifecycle(
                logger,
                "crawler",
                "completed",
                pages_crawled=len(result.get("pages", [])),
            )

            return {
                "success": True,
                "data": result,
                "confidence": 0.8,
                "metadata": {
                    "agent_type": "crawler",
                    "url": url,
                    "pages_crawled": len(result.get("pages", [])),
                    "depth": depth,
                },
            }

        except Exception as e:
            logger.error(f"Crawler agent error: {e}", agent="crawler", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "metadata": {"agent_type": "crawler", "error_type": type(e).__name__},
            }


# Agent registry for easy access
STANDARDIZED_AGENTS = {
    ExtendedAgentType.BROWSER: StandardizedBrowserAgent,
    ExtendedAgentType.PDF: StandardizedPDFAgent,
    ExtendedAgentType.CODE: StandardizedCodeAgent,
    ExtendedAgentType.DATABASE: StandardizedDatabaseAgent,
    ExtendedAgentType.KNOWLEDGE_GRAPH: StandardizedKnowledgeGraphAgent,
    ExtendedAgentType.CRAWLER: StandardizedCrawlerAgent,
}


def create_agent(agent_type: ExtendedAgentType) -> BaseAgent:
    """Factory function to create standardized agent instances."""
    if agent_type not in STANDARDIZED_AGENTS:
        raise ValueError(f"Unknown agent type: {agent_type}")

    return STANDARDIZED_AGENTS[agent_type]()


def get_agent_capabilities(agent_type: ExtendedAgentType) -> AgentCapabilities:
    """Get capabilities for a specific agent type."""
    agent = create_agent(agent_type)
    return agent.capabilities


# Export main classes and functions
__all__ = [
    "ExtendedAgentType",
    "AgentCapabilities",
    "StandardizedBrowserAgent",
    "StandardizedPDFAgent",
    "StandardizedCodeAgent",
    "StandardizedDatabaseAgent",
    "StandardizedKnowledgeGraphAgent",
    "StandardizedCrawlerAgent",
    "STANDARDIZED_AGENTS",
    "create_agent",
    "get_agent_capabilities",
]
