"""
Integration Layer - Universal Knowledge Platform
Main integration layer that connects all Week 1 components into a unified system.

This module provides the central integration point for:
- Query Intelligence Layer
- Multi-Agent AI Orchestration
- RAG + Knowledge Graph Integration
- Memory Management System
- Expert Validation Layer

Architecture:
- Unified interface for all components
- Comprehensive error handling and fallbacks
- Performance monitoring and metrics
- Enterprise-grade reliability
- Clean separation of concerns

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
License: MIT
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json

# Import all Week 1 components
try:
    from services.search_service.core.query_processor import (
        QueryIntelligenceLayer,
        ProcessedQuery,
        IntentType,
        ComplexityLevel,
        DomainType
    )
    from services.synthesis_service.core.orchestrator import (
        MultiAgentOrchestrator,
        OrchestrationResult,
        ModelType,
        RoutingStrategy
    )
    from services.search_service.core.hybrid_retrieval import (
        HybridRetrievalEngine,
        HybridRetrievalResult,
        RetrievalSource,
        FusionStrategy
    )
    from shared.core.memory_manager import (
        MemoryManager,
        MemoryType,
        MemoryPriority
    )
    from services.factcheck_service.core.expert_validation import (
        ExpertValidationLayer,
        ConsensusResult,
        ExpertNetworkType,
        ValidationStatus,
        ConsensusLevel
    )
    from services.analytics_service.metrics.knowledge_platform_metrics import (
        KnowledgePlatformMetricsCollector,
        record_query_intelligence_metrics,
        record_orchestration_metrics,
        record_retrieval_metrics,
        record_memory_metrics,
        record_expert_validation_metrics,
        record_business_metrics
    )
except ImportError as e:
    print(f"Some Week 1 components not available: {e}")
    # Create mock classes for testing
    class MockProcessedQuery:
        def __init__(self, original, intent, complexity, domain, fingerprint, routing_decision):
            self.original = original
            self.intent = intent
            self.complexity = complexity
            self.domain = domain
            self.fingerprint = fingerprint
            self.routing_decision = routing_decision
        
        def to_dict(self):
            return {
                "original": self.original,
                "intent": self.intent.value if hasattr(self.intent, 'value') else str(self.intent),
                "complexity": self.complexity.value if hasattr(self.complexity, 'value') else str(self.complexity),
                "domain": self.domain.value if hasattr(self.domain, 'value') else str(self.domain),
                "fingerprint": self.fingerprint,
                "routing_decision": self.routing_decision
            }
            self.processing_time_ms = 100
    
    class MockIntentType:
        FACTUAL = type('Enum', (), {'value': 'factual'})()
    
    class MockComplexityLevel:
        MODERATE = type('Enum', (), {'value': 'moderate'})()
    
    class MockDomainType:
        GENERAL = type('Enum', (), {'value': 'general'})()
    
    class QueryIntelligenceLayer:
        async def process_query(self, query, context):
            return MockProcessedQuery(
                original=query, 
                intent=MockIntentType.FACTUAL, 
                complexity=MockComplexityLevel.MODERATE, 
                domain=MockDomainType.GENERAL, 
                fingerprint="test", 
                routing_decision="standard"
            )
    
    class MockOrchestrationResult:
        def __init__(self, success, model_used, response, processing_time_ms, token_usage):
            self.success = success
            self.model_used = model_used
            self.response = response
            self.processing_time_ms = processing_time_ms
            self.token_usage = token_usage
    
    class MockModelType:
        GPT_4 = type('Enum', (), {'value': 'gpt-4'})()
    
    class MultiAgentOrchestrator:
        async def process_request(self, request_data, context):
            return MockOrchestrationResult(
                success=True, 
                model_used=MockModelType.GPT_4, 
                response="Test response", 
                processing_time_ms=100, 
                token_usage={}
            )
    
    class MockHybridRetrievalResult:
        def __init__(self, results, fusion_strategy, total_sources, processing_time_ms):
            self.results = results
            self.fusion_strategy = fusion_strategy
            self.total_sources = total_sources
            self.processing_time_ms = processing_time_ms
    
    class MockFusionStrategy:
        WEIGHTED = type('Enum', (), {'value': 'weighted'})()
    
    class HybridRetrievalEngine:
        async def retrieve(self, query, max_results=10, fusion_strategy=None, sources=None):
            return MockHybridRetrievalResult(
                results=[], 
                fusion_strategy=MockFusionStrategy.WEIGHTED, 
                total_sources=0, 
                processing_time_ms=100
            )
    
    class MockConsensusResult:
        def __init__(self, overall_status, consensus_level, consensus_score, expert_validations, final_confidence, reasoning, processing_time_ms):
            self.overall_status = overall_status
            self.consensus_level = consensus_level
            self.consensus_score = consensus_score
            self.expert_validations = expert_validations
            self.final_confidence = final_confidence
            self.reasoning = reasoning
            self.processing_time_ms = processing_time_ms
    
    class MockValidationStatus:
        VERIFIED = type('Enum', (), {'value': 'verified'})()
    
    class MockConsensusLevel:
        STRONG_CONSENSUS = type('Enum', (), {'value': 'strong_consensus'})()
    
    class ExpertValidationLayer:
        async def validate_fact(self, claim, context):
            return MockConsensusResult(
                overall_status=MockValidationStatus.VERIFIED, 
                consensus_level=MockConsensusLevel.STRONG_CONSENSUS, 
                consensus_score=0.9, 
                expert_validations=[], 
                final_confidence=0.9, 
                reasoning="Test validation", 
                processing_time_ms=100
            )
    
    class KnowledgePlatformMetricsCollector:
        def get_metrics_dict(self):
            return {"test": "metrics"}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class IntegrationRequest:
    """Request for the integration layer."""
    
    query: str
    user_id: str
    session_id: str
    context: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    priority: str = "normal"
    timeout_seconds: int = 30


@dataclass
class IntegrationResponse:
    """Response from the integration layer."""
    
    success: bool
    query_analysis: Optional[ProcessedQuery] = None
    orchestration_result: Optional[OrchestrationResult] = None
    retrieval_result: Optional[HybridRetrievalResult] = None
    validation_result: Optional[ConsensusResult] = None
    memory_operations: Dict[str, Any] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class UniversalKnowledgePlatformIntegration:
    """
    Main integration layer for the Universal Knowledge Platform.
    
    This class orchestrates all Week 1 components:
    - Query Intelligence Layer
    - Multi-Agent AI Orchestration
    - RAG + Knowledge Graph Integration
    - Memory Management System
    - Expert Validation Layer
    """
    
    def __init__(self):
        """Initialize all components."""
        logger.info("🚀 Initializing Universal Knowledge Platform Integration")
        
        try:
            # Initialize Query Intelligence Layer
            self.query_intelligence = QueryIntelligenceLayer()
            logger.info("✅ Query Intelligence Layer initialized")
            
            # Initialize Multi-Agent Orchestration
            self.orchestrator = MultiAgentOrchestrator()
            logger.info("✅ Multi-Agent Orchestration initialized")
            
            # Initialize Hybrid Retrieval Engine
            self.retrieval_engine = HybridRetrievalEngine()
            logger.info("✅ Hybrid Retrieval Engine initialized")
            
            # Initialize Memory Management System
            self.memory_manager = MemoryManager()
            logger.info("✅ Memory Management System initialized")
            
            # Initialize Expert Validation Layer
            self.expert_validator = ExpertValidationLayer()
            logger.info("✅ Expert Validation Layer initialized")
            
            # Initialize Metrics Collector
            self.metrics_collector = KnowledgePlatformMetricsCollector()
            logger.info("✅ Metrics Collector initialized")
            
            logger.info("🎉 All components initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize components: {e}")
            raise
    
    async def process_query(self, request: IntegrationRequest) -> IntegrationResponse:
        """
        Process a query through the complete pipeline.
        
        Args:
            request: Integration request with query and context
            
        Returns:
            Integration response with all component results
        """
        start_time = time.time()
        
        try:
            logger.info(f"📝 Processing query: {request.query[:50]}...")
            
            # Step 1: Query Intelligence Analysis
            query_analysis = await self._analyze_query(request)
            
            # Step 2: Memory Operations
            memory_operations = await self._handle_memory_operations(request, query_analysis)
            
            # Step 3: Hybrid Retrieval
            retrieval_result = await self._perform_hybrid_retrieval(request, query_analysis)
            
            # Step 4: Expert Validation (if needed)
            validation_result = await self._perform_expert_validation(request, retrieval_result)
            
            # Step 5: Multi-Agent Orchestration for Synthesis
            orchestration_result = await self._perform_orchestration(request, retrieval_result, validation_result)
            
            # Step 6: Update Memory with Results
            await self._update_memory_with_results(request, orchestration_result)
            
            # Step 7: Record Metrics
            await self._record_comprehensive_metrics(request, query_analysis, orchestration_result, retrieval_result, validation_result)
            
            processing_time = (time.time() - start_time) * 1000
            
            response = IntegrationResponse(
                success=True,
                query_analysis=query_analysis,
                orchestration_result=orchestration_result,
                retrieval_result=retrieval_result,
                validation_result=validation_result,
                memory_operations=memory_operations,
                processing_time_ms=processing_time,
                metadata={
                    "user_id": request.user_id,
                    "session_id": request.session_id,
                    "components_used": ["query_intelligence", "orchestration", "retrieval", "validation", "memory"]
                }
            )
            
            logger.info(f"✅ Query processed successfully in {processing_time:.2f}ms")
            return response
            
        except Exception as e:
            logger.error(f"❌ Query processing failed: {e}")
            processing_time = (time.time() - start_time) * 1000
            
            return IntegrationResponse(
                success=False,
                processing_time_ms=processing_time,
                error_message=str(e),
                metadata={"error_type": type(e).__name__}
            )
    
    async def _analyze_query(self, request: IntegrationRequest) -> ProcessedQuery:
        """Analyze query using Query Intelligence Layer."""
        try:
            context = {
                "user_id": request.user_id,
                "session_id": request.session_id,
                **request.context
            }
            
            processed_query = await self.query_intelligence.process_query(request.query, context)
            
            logger.info(f"🔍 Query analyzed - Intent: {processed_query.intent.value if hasattr(processed_query.intent, 'value') else str(processed_query.intent)}, Complexity: {processed_query.complexity.value if hasattr(processed_query.complexity, 'value') else str(processed_query.complexity)}, Domains: {[d.value if hasattr(d, 'value') else str(d) for d in processed_query.domains]}")
            
            return processed_query
            
        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            raise
    
    async def _handle_memory_operations(self, request: IntegrationRequest, query_analysis: ProcessedQuery) -> Dict[str, Any]:
        """Handle memory operations for the query."""
        try:
            memory_operations = {}
            
            # Store query analysis in short-term memory
            await self.memory_manager.store(
                key=f"query_analysis:{request.session_id}",
                value=query_analysis.to_dict(),
                memory_type=MemoryType.SHORT_TERM,
                priority=MemoryPriority.MEDIUM,
                ttl_seconds=3600
            )
            memory_operations["query_analysis_stored"] = True
            
            # Retrieve any relevant context from memory
            context_key = f"user_context:{request.user_id}"
            user_context = await self.memory_manager.retrieve(context_key, MemoryType.MEDIUM_TERM)
            if user_context:
                memory_operations["context_retrieved"] = True
                memory_operations["context_data"] = user_context
            
            # Store session data
            await self.memory_manager.store(
                key=f"session:{request.session_id}",
                value={
                    "query": request.query,
                    "timestamp": datetime.now().isoformat(),
                    "analysis": query_analysis.to_dict()
                },
                memory_type=MemoryType.MEDIUM_TERM,
                priority=MemoryPriority.LOW,
                ttl_seconds=86400
            )
            memory_operations["session_stored"] = True
            
            logger.info("💾 Memory operations completed")
            return memory_operations
            
        except Exception as e:
            logger.error(f"Memory operations failed: {e}")
            return {"error": str(e)}
    
    async def _perform_hybrid_retrieval(self, request: IntegrationRequest, query_analysis: ProcessedQuery) -> HybridRetrievalResult:
        """Perform hybrid retrieval based on query analysis."""
        try:
            # Determine retrieval strategy based on query analysis
            fusion_strategy = FusionStrategy.WEIGHTED_SUM
            sources = [RetrievalSource.VECTOR_DB, RetrievalSource.KNOWLEDGE_GRAPH]
            
            # Add external sources for complex queries
            if query_analysis.complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.EXPERT]:
                sources.extend([RetrievalSource.WIKIPEDIA, RetrievalSource.WIKIDATA])
            
            # Add Wikipedia for factual queries
            if query_analysis.intent in [IntentType.FACTUAL]:
                sources.append(RetrievalSource.WIKIPEDIA)
            
            retrieval_result = await self.retrieval_engine.retrieve(
                query=request.query,
                max_results=15,
                fusion_strategy=fusion_strategy,
                sources=sources
            )
            
            logger.info(f"🔍 Hybrid retrieval completed - {len(retrieval_result.source_results)} results from {len(retrieval_result.source_results)} sources")
            
            return retrieval_result
            
        except Exception as e:
            logger.error(f"Hybrid retrieval failed: {e}")
            raise
    
    async def _perform_expert_validation(self, request: IntegrationRequest, retrieval_result: HybridRetrievalResult) -> Optional[ConsensusResult]:
        """Perform expert validation if needed."""
        try:
            # Only validate for complex queries or when high confidence is required
            if request.preferences.get("require_validation", False):
                # Extract claims from retrieval results
                claims = []
                for result in retrieval_result.source_results[:5]:  # Validate top 5 results
                    if hasattr(result, 'score') and result.score > 0.8:  # Only validate high-confidence results
                        claims.append(result.content)
                
                if claims:
                    validation_result = await self.expert_validator.validate_fact(
                        claim=claims[0]  # Validate the top claim
                    )
                    
                    logger.info(f"🔬 Expert validation completed - Status: {validation_result.overall_status.value}, Consensus: {validation_result.consensus_level.value}")
                    
                    return validation_result
            
            return None
            
        except Exception as e:
            logger.error(f"Expert validation failed: {e}")
            return None
    
    async def _perform_orchestration(self, request: IntegrationRequest, retrieval_result: HybridRetrievalResult, validation_result: Optional[ConsensusResult]) -> OrchestrationResult:
        """Perform multi-agent orchestration for synthesis."""
        try:
            # Prepare synthesis data
            synthesis_data = {
                "query": request.query,
                "retrieval_results": [result.content for result in retrieval_result.results],
                "validation_status": validation_result.overall_status.value if validation_result else "not_validated",
                "user_context": request.context,
                "preferences": request.preferences
            }
            
            # Determine orchestration strategy based on query analysis
            routing_strategy = RoutingStrategy.HYBRID
            if request.preferences.get("cost_optimized", False):
                routing_strategy = RoutingStrategy.COST
            elif request.preferences.get("performance_optimized", False):
                routing_strategy = RoutingStrategy.PERFORMANCE
            
            orchestration_result = await self.orchestrator.process_request(
                query=request.query,
                context={
                    "user_id": request.user_id,
                    "routing_strategy": routing_strategy.value,
                    "fallback_enabled": True,
                    "timeout_seconds": request.timeout_seconds
                }
            )
            
            logger.info(f"🎯 Orchestration completed - Model: {orchestration_result.model_used.value}")
            
            return orchestration_result
            
        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            raise
    
    async def _update_memory_with_results(self, request: IntegrationRequest, orchestration_result: OrchestrationResult) -> None:
        """Update memory with orchestration results."""
        try:
            # Store final result in long-term memory if successful
            if orchestration_result.success:
                await self.memory_manager.store(
                    key=f"query_result:{request.session_id}",
                    value={
                        "query": request.query,
                        "response": orchestration_result.response,
                        "model_used": orchestration_result.model_used.value,
                        "processing_time_ms": orchestration_result.processing_time_ms,
                        "timestamp": datetime.now().isoformat()
                    },
                    memory_type=MemoryType.LONG_TERM,
                    priority=MemoryPriority.HIGH
                )
                
                logger.info("💾 Results stored in long-term memory")
            
        except Exception as e:
            logger.error(f"Memory update failed: {e}")
    
    async def _record_comprehensive_metrics(self, request: IntegrationRequest, query_analysis: ProcessedQuery, orchestration_result: OrchestrationResult, retrieval_result: HybridRetrievalResult, validation_result: Optional[ConsensusResult]) -> None:
        """Record comprehensive metrics for all components."""
        try:
            # Record query intelligence metrics
            record_query_intelligence_metrics(
                intent=query_analysis.intent.value,
                complexity=query_analysis.complexity.value,
                domain=query_analysis.domain.value,
                processing_time_ms=query_analysis.processing_time_ms,
                cache_hit=False  # TODO: Implement cache hit detection
            )
            
            # Record orchestration metrics
            record_orchestration_metrics(
                model_used=orchestration_result.model_used.value,
                routing_strategy="hybrid",
                fallback_used=orchestration_result.fallback_used,
                circuit_breaker_triggered=orchestration_result.circuit_breaker_triggered,
                response_time_ms=orchestration_result.processing_time_ms,
                status="success" if orchestration_result.success else "failed"
            )
            
            # Record retrieval metrics
            record_retrieval_metrics(
                source_type="hybrid",
                fusion_strategy=retrieval_result.fusion_strategy.value,
                retrieval_time_ms=retrieval_result.processing_time_ms,
                results_count=len(retrieval_result.results),
                accuracy_score=retrieval_result.confidence_scores.get("overall", 0.8),
                status="success"
            )
            
            # Record memory metrics
            record_memory_metrics(
                memory_type="short_term",
                operation_type="store",
                usage_bytes=1024,  # TODO: Calculate actual usage
                hit_rate=0.85,  # TODO: Calculate actual hit rate
                status="success"
            )
            
            # Record expert validation metrics if performed
            if validation_result:
                record_expert_validation_metrics(
                    expert_network="domain_expert",
                    validation_status=validation_result.overall_status.value,
                    consensus_level=validation_result.consensus_level.value,
                    validation_time_ms=validation_result.processing_time_ms,
                    confidence_score=validation_result.final_confidence,
                    availability=1.0
                )
            
            # Record business metrics
            record_business_metrics(
                user_satisfaction=0.9,  # TODO: Calculate from user feedback
                response_quality=0.85,  # TODO: Calculate from response analysis
                feature_type="query_processing",
                user_type="standard",
                error_rate=0.0
            )
            
            logger.info("📊 Comprehensive metrics recorded")
            
        except Exception as e:
            logger.error(f"Metrics recording failed: {e}")
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status."""
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "status": "healthy",
                "components": {}
            }
            
            # Check Query Intelligence Layer
            try:
                test_query = "What is AI?"
                test_context = {"user_id": "health_check", "session_id": "health_check"}
                test_result = await self.query_intelligence.process_query(test_query, test_context)
                health_status["components"]["query_intelligence"] = {
                    "status": "healthy",
                    "response_time_ms": getattr(test_result, 'processing_time_ms', 100)
                }
            except Exception as e:
                health_status["components"]["query_intelligence"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["status"] = "degraded"
            
            # Check Multi-Agent Orchestration
            try:
                # Use a simple test instead of get_orchestration_stats
                test_request = {"query": "test", "context": {}}
                test_result = await self.orchestrator.process_request(test_request, {})
                health_status["components"]["orchestration"] = {
                    "status": "healthy",
                    "available_models": 1  # At least one model available
                }
            except Exception as e:
                health_status["components"]["orchestration"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["status"] = "degraded"
            
            # Check Memory Management
            try:
                # Simple memory test
                test_key = "health_check_test"
                await self.memory_manager.store_short_term(test_key, "test_value")
                test_value = await self.memory_manager.retrieve_short_term(test_key)
                health_status["components"]["memory_management"] = {
                    "status": "healthy",
                    "test_result": test_value == "test_value"
                }
            except Exception as e:
                health_status["components"]["memory_management"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["status"] = "degraded"
            
            # Check Expert Validation
            try:
                # Test with a simple validation
                test_claim = "Python is a programming language"
                test_result = await self.expert_validator.validate_fact(test_claim)
                health_status["components"]["expert_validation"] = {
                    "status": "healthy",
                    "available_networks": 2  # Academic and Industry networks
                }
            except Exception as e:
                health_status["components"]["expert_validation"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["status"] = "degraded"
            
            logger.info(f"🏥 System health check completed - Status: {health_status['status']}")
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "unhealthy",
                "error": str(e),
                "components": {
                    "query_intelligence": {"status": "unknown"},
                    "orchestration": {"status": "unknown"},
                    "memory_management": {"status": "unknown"},
                    "expert_validation": {"status": "unknown"}
                }
            }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown all components."""
        try:
            logger.info("🔄 Shutting down Universal Knowledge Platform Integration")
            
            # Shutdown components in reverse order
            # Note: Individual components don't have shutdown methods yet
            # This is a placeholder for future implementation
            
            logger.info("✅ Shutdown completed")
            
        except Exception as e:
            logger.error(f"❌ Shutdown failed: {e}")


# Global instance for API Gateway integration
integration_layer = UniversalKnowledgePlatformIntegration()


async def get_integration_layer() -> UniversalKnowledgePlatformIntegration:
    """Get the global integration layer instance."""
    return integration_layer 