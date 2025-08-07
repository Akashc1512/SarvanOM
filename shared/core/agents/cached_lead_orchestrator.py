"""
Cached Lead Orchestrator

This module integrates the refined LeadOrchestrator with the comprehensive caching system
to provide optimal performance for the multi-agent pipeline.
"""

from typing import Dict, Any, Optional
from .refined_lead_orchestrator import RefinedLeadOrchestrator, PipelineConfig
from .standardized_agents import ExtendedAgentType
from ..cache.cached_retrieval_agent import CachedRetrievalAgent
from ..cache.cached_agents import CachedSynthesisAgent, CachedFactCheckAgent, CachedKnowledgeGraphAgent
from ..cache.cache_invalidation import get_invalidation_manager
from ..cache.cache_metrics import get_metrics_collector
from ..unified_logging import get_logger

logger = get_logger(__name__)


class CachedLeadOrchestrator(RefinedLeadOrchestrator):
    """
    Enhanced LeadOrchestrator with comprehensive caching integration.
    
    This orchestrator uses cached versions of all agents to provide:
    - Faster response times for repeated queries
    - Reduced API calls to expensive services
    - Better resource utilization
    - Comprehensive performance monitoring
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """Initialize the cached orchestrator."""
        super().__init__(config)
        
        # Replace agents with cached versions
        self._replace_agents_with_cached_versions()
        
        # Initialize cache monitoring
        self.metrics_collector = get_metrics_collector()
        self.invalidation_manager = get_invalidation_manager()
        
        logger.info("Initialized CachedLeadOrchestrator with comprehensive caching")
    
    def _replace_agents_with_cached_versions(self):
        """Replace standard agents with cached versions."""
        try:
            # Replace retrieval agent with cached version
            self.agent_registry[ExtendedAgentType.RETRIEVAL] = CachedRetrievalAgent()
            logger.info("✅ Replaced RetrievalAgent with CachedRetrievalAgent")
            
            # Replace synthesis agent with cached version
            self.agent_registry[ExtendedAgentType.SYNTHESIS] = CachedSynthesisAgent()
            logger.info("✅ Replaced SynthesisAgent with CachedSynthesisAgent")
            
            # Replace fact-check agent with cached version
            self.agent_registry[ExtendedAgentType.FACT_CHECK] = CachedFactCheckAgent()
            logger.info("✅ Replaced FactCheckAgent with CachedFactCheckAgent")
            
            # Replace knowledge graph agent with cached version
            if ExtendedAgentType.KNOWLEDGE_GRAPH in self.agent_registry:
                self.agent_registry[ExtendedAgentType.KNOWLEDGE_GRAPH] = CachedKnowledgeGraphAgent()
                logger.info("✅ Replaced KnowledgeGraphAgent with CachedKnowledgeGraphAgent")
            
        except Exception as e:
            logger.warning(f"Some cached agents could not be initialized: {e}")
    
    async def process_query(self, query: str, user_context: Dict[str, Any] = None):
        """Process query with caching and performance monitoring."""
        
        # Record query start
        self.metrics_collector.record_cache_operation(
            "query_processing", 
            ExtendedAgentType.RETRIEVAL, 
            0, 
            True
        )
        
        # Process query using parent method
        result = await super().process_query(query, user_context)
        
        # Record query completion
        if result.success:
            self.metrics_collector.record_hit(ExtendedAgentType.RETRIEVAL)
        else:
            self.metrics_collector.record_miss(ExtendedAgentType.RETRIEVAL)
        
        # Add cache statistics to result
        result.metadata["cache_stats"] = self.get_comprehensive_cache_stats()
        
        return result
    
    def get_comprehensive_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics from all cached agents."""
        stats = {}
        
        # Get individual agent cache stats
        for agent_type, agent in self.agent_registry.items():
            if hasattr(agent, 'get_cache_stats'):
                try:
                    agent_stats = agent.get_cache_stats()
                    stats[agent_type.value] = agent_stats
                except Exception as e:
                    logger.warning(f"Could not get cache stats for {agent_type.value}: {e}")
        
        # Get overall performance metrics
        try:
            performance_metrics = self.metrics_collector.get_all_performance_metrics()
            stats["performance_metrics"] = performance_metrics
        except Exception as e:
            logger.warning(f"Could not get performance metrics: {e}")
        
        # Get invalidation stats
        try:
            invalidation_stats = self.invalidation_manager.get_invalidation_stats()
            stats["invalidation_stats"] = invalidation_stats
        except Exception as e:
            logger.warning(f"Could not get invalidation stats: {e}")
        
        return stats
    
    async def warm_cache(self, common_queries: list):
        """Warm the cache with common queries."""
        logger.info(f"Warming cache with {len(common_queries)} common queries")
        
        from ..cache.cached_agents import warm_agent_caches
        
        try:
            # Create agent map for warming
            agents = {}
            
            if ExtendedAgentType.RETRIEVAL in self.agent_registry:
                agents["retrieval"] = self.agent_registry[ExtendedAgentType.RETRIEVAL]
            
            if ExtendedAgentType.SYNTHESIS in self.agent_registry:
                agents["synthesis"] = self.agent_registry[ExtendedAgentType.SYNTHESIS]
            
            if ExtendedAgentType.FACT_CHECK in self.agent_registry:
                agents["factcheck"] = self.agent_registry[ExtendedAgentType.FACT_CHECK]
            
            # Warm caches
            await warm_agent_caches(common_queries, agents)
            
            logger.info("Cache warming completed")
            
        except Exception as e:
            logger.error(f"Error during cache warming: {e}")
    
    async def invalidate_cache(self, query: str = None):
        """Invalidate cache for specific query or all caches."""
        from ..cache.cache_invalidation import invalidate_query_cache
        
        try:
            if query:
                await invalidate_query_cache(query)
                logger.info(f"Invalidated cache for query: {query[:50]}...")
            else:
                # Invalidate all agent caches
                for agent in self.agent_registry.values():
                    if hasattr(agent, 'invalidate_cache'):
                        await agent.invalidate_cache()
                
                logger.info("Invalidated all agent caches")
                
        except Exception as e:
            logger.error(f"Error during cache invalidation: {e}")
    
    def get_cache_insights(self) -> Dict[str, Any]:
        """Get actionable cache performance insights."""
        try:
            return self.metrics_collector.get_cache_insights()
        except Exception as e:
            logger.error(f"Error getting cache insights: {e}")
            return {"error": str(e)}


# Update the main LeadOrchestrator to use caching by default
class LeadOrchestrator(CachedLeadOrchestrator):
    """
    Main LeadOrchestrator class with caching enabled by default.
    
    This provides backward compatibility while enabling comprehensive caching
    for optimal performance.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with caching enabled."""
        
        # Convert dict config to PipelineConfig if needed
        if isinstance(config, dict):
            pipeline_config = PipelineConfig()
            if "max_parallel_agents" in config:
                pipeline_config.max_parallel_agents = config["max_parallel_agents"]
            if "enable_parallel_retrieval" in config:
                pipeline_config.enable_parallel_retrieval = config["enable_parallel_retrieval"]
            if "enable_enrichment_stage" in config:
                pipeline_config.enable_enrichment_stage = config["enable_enrichment_stage"]
        else:
            pipeline_config = config
        
        super().__init__(pipeline_config)


# Export main classes
__all__ = [
    'CachedLeadOrchestrator',
    'LeadOrchestrator'
]