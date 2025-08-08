"""
Agent Factory Service

This module creates and configures different types of agents.
"""

import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ...models.domain.agent import Agent, AgentType, AgentStatus, AgentCapability

logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory for creating different types of agents."""
    
    def __init__(self):
        self.agent_configs = self._initialize_agent_configs()
    
    async def create_agent(self, agent_type: AgentType) -> Agent:
        """Create an agent of the specified type."""
        try:
            config = self.agent_configs.get(agent_type)
            if not config:
                raise ValueError(f"Unknown agent type: {agent_type}")
            
            agent_id = str(uuid.uuid4())
            agent_name = config["name"]
            capabilities = config["capabilities"]
            agent_config = config.get("config", {})
            
            agent = Agent(
                id=agent_id,
                name=agent_name,
                agent_type=agent_type,
                capabilities=capabilities,
                config=agent_config
            )
            
            logger.info(f"Created agent {agent_id} of type {agent_type}")
            return agent
            
        except Exception as e:
            logger.error(f"Error creating agent {agent_type}: {e}", exc_info=True)
            raise
    
    def _initialize_agent_configs(self) -> Dict[AgentType, Dict[str, Any]]:
        """Initialize agent configurations."""
        return {
            AgentType.RETRIEVAL: {
                "name": "Retrieval Agent",
                "capabilities": [
                    AgentCapability(
                        name="information_retrieval",
                        description="Retrieve relevant information from various sources",
                        supported_inputs=["text_query", "structured_query"],
                        supported_outputs=["retrieved_documents", "relevance_scores"],
                        max_concurrent_tasks=5
                    ),
                    AgentCapability(
                        name="query_classification",
                        description="Classify and categorize queries",
                        supported_inputs=["text_query"],
                        supported_outputs=["query_intent", "query_domain"],
                        max_concurrent_tasks=3
                    )
                ],
                "config": {
                    "max_results": 10,
                    "relevance_threshold": 0.7,
                    "search_sources": ["web", "database", "vector_store"]
                }
            },
            
            AgentType.SYNTHESIS: {
                "name": "Synthesis Agent",
                "capabilities": [
                    AgentCapability(
                        name="answer_generation",
                        description="Generate comprehensive answers from retrieved information",
                        supported_inputs=["retrieved_documents", "query"],
                        supported_outputs=["generated_answer", "confidence_score"],
                        max_concurrent_tasks=3
                    ),
                    AgentCapability(
                        name="content_synthesis",
                        description="Synthesize information from multiple sources",
                        supported_inputs=["multiple_sources", "query"],
                        supported_outputs=["synthesized_content", "source_attribution"],
                        max_concurrent_tasks=2
                    )
                ],
                "config": {
                    "max_tokens": 2000,
                    "temperature": 0.7,
                    "include_sources": True
                }
            },
            
            AgentType.FACT_CHECK: {
                "name": "Fact Check Agent",
                "capabilities": [
                    AgentCapability(
                        name="fact_verification",
                        description="Verify factual claims against reliable sources",
                        supported_inputs=["factual_claim", "supporting_evidence"],
                        supported_outputs=["verification_result", "confidence_score"],
                        max_concurrent_tasks=2
                    ),
                    AgentCapability(
                        name="contradiction_detection",
                        description="Detect contradictions between sources",
                        supported_inputs=["multiple_sources"],
                        supported_outputs=["contradictions", "consensus_level"],
                        max_concurrent_tasks=2
                    )
                ],
                "config": {
                    "verification_sources": ["reliable_database", "fact_check_sites"],
                    "confidence_threshold": 0.8
                }
            },
            
            AgentType.KNOWLEDGE_GRAPH: {
                "name": "Knowledge Graph Agent",
                "capabilities": [
                    AgentCapability(
                        name="graph_query",
                        description="Query knowledge graph for relationships",
                        supported_inputs=["entity_query", "relationship_query"],
                        supported_outputs=["graph_results", "entity_relationships"],
                        max_concurrent_tasks=3
                    ),
                    AgentCapability(
                        name="graph_traversal",
                        description="Traverse knowledge graph for insights",
                        supported_inputs=["starting_entity", "traversal_depth"],
                        supported_outputs=["traversal_path", "discovered_entities"],
                        max_concurrent_tasks=2
                    )
                ],
                "config": {
                    "max_traversal_depth": 3,
                    "include_metadata": True
                }
            },
            
            AgentType.CODE_EXECUTOR: {
                "name": "Code Executor Agent",
                "capabilities": [
                    AgentCapability(
                        name="code_execution",
                        description="Execute code in a safe environment",
                        supported_inputs=["code_snippet", "execution_context"],
                        supported_outputs=["execution_result", "output_logs"],
                        max_concurrent_tasks=1
                    ),
                    AgentCapability(
                        name="code_analysis",
                        description="Analyze code for issues and improvements",
                        supported_inputs=["code_snippet"],
                        supported_outputs=["analysis_report", "suggestions"],
                        max_concurrent_tasks=2
                    )
                ],
                "config": {
                    "timeout_seconds": 30,
                    "memory_limit_mb": 512,
                    "allowed_languages": ["python", "javascript"]
                }
            },
            
            AgentType.BROWSER: {
                "name": "Browser Agent",
                "capabilities": [
                    AgentCapability(
                        name="web_navigation",
                        description="Navigate and interact with web pages",
                        supported_inputs=["url", "navigation_instructions"],
                        supported_outputs=["page_content", "navigation_log"],
                        max_concurrent_tasks=2
                    ),
                    AgentCapability(
                        name="content_extraction",
                        description="Extract structured content from web pages",
                        supported_inputs=["web_page", "extraction_rules"],
                        supported_outputs=["extracted_content", "metadata"],
                        max_concurrent_tasks=3
                    )
                ],
                "config": {
                    "timeout_seconds": 60,
                    "user_agent": "SarvanOM-Browser-Agent/1.0",
                    "follow_redirects": True
                }
            },
            
            AgentType.CRAWLER: {
                "name": "Crawler Agent",
                "capabilities": [
                    AgentCapability(
                        name="web_crawling",
                        description="Crawl websites for content",
                        supported_inputs=["start_url", "crawl_rules"],
                        supported_outputs=["crawled_pages", "crawl_statistics"],
                        max_concurrent_tasks=2
                    ),
                    AgentCapability(
                        name="content_discovery",
                        description="Discover new content and links",
                        supported_inputs=["base_url", "discovery_patterns"],
                        supported_outputs=["discovered_urls", "content_summary"],
                        max_concurrent_tasks=3
                    )
                ],
                "config": {
                    "max_depth": 3,
                    "max_pages": 100,
                    "respect_robots_txt": True,
                    "delay_between_requests": 1.0
                }
            },
            
            AgentType.PDF: {
                "name": "PDF Agent",
                "capabilities": [
                    AgentCapability(
                        name="pdf_processing",
                        description="Process and extract content from PDF files",
                        supported_inputs=["pdf_file", "extraction_options"],
                        supported_outputs=["extracted_text", "document_structure"],
                        max_concurrent_tasks=2
                    ),
                    AgentCapability(
                        name="pdf_analysis",
                        description="Analyze PDF content for insights",
                        supported_inputs=["pdf_content", "analysis_parameters"],
                        supported_outputs=["analysis_report", "key_insights"],
                        max_concurrent_tasks=2
                    )
                ],
                "config": {
                    "extract_images": False,
                    "extract_tables": True,
                    "maintain_formatting": True
                }
            }
        }
    
    def get_agent_config(self, agent_type: AgentType) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific agent type."""
        return self.agent_configs.get(agent_type)
    
    def get_supported_agent_types(self) -> list:
        """Get list of supported agent types."""
        return list(self.agent_configs.keys())
    
    def validate_agent_type(self, agent_type: AgentType) -> bool:
        """Validate if an agent type is supported."""
        return agent_type in self.agent_configs 