"""
Refactored Integration Layer with Single Responsibility Functions

This module refactors the main integration layer code into smaller, focused functions
that each handle a single responsibility. This improves readability and maintainability
while preserving all functionality.

Key improvements:
1. Query analysis separated into dedicated functions
2. Memory operations broken into focused methods
3. Retrieval and validation logic isolated
4. Orchestration coordination simplified
5. Result formatting and metrics in separate functions
6. Clear separation of concerns
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

from shared.core.unified_logging import get_logger
from shared.core.agents.refactored_orchestrator import RefactoredOrchestrator, PipelineConfig, PipelineResult

logger = get_logger(__name__)


class ProcessingStage(Enum):
    """Processing stages for the integration layer."""
    
    QUERY_ANALYSIS = "query_analysis"
    MEMORY_OPERATIONS = "memory_operations"
    HYBRID_RETRIEVAL = "hybrid_retrieval"
    EXPERT_VALIDATION = "expert_validation"
    ORCHESTRATION = "orchestration"
    MEMORY_UPDATE = "memory_update"
    METRICS_RECORDING = "metrics_recording"


@dataclass
class IntegrationRequest:
    """Request for the refactored integration layer."""
    
    query: str
    user_id: str
    session_id: str
    context: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    priority: str = "normal"
    timeout_seconds: int = 30
    model: str = "auto"


@dataclass
class IntegrationResponse:
    """Response from the refactored integration layer."""
    
    success: bool
    query_analysis: Optional[Dict[str, Any]] = None
    orchestration_result: Optional[PipelineResult] = None
    retrieval_result: Optional[Dict[str, Any]] = None
    validation_result: Optional[Dict[str, Any]] = None
    memory_operations: Dict[str, Any] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class RefactoredIntegrationLayer:
    """
    Refactored integration layer with single responsibility functions.
    
    This integration layer breaks down the main orchestration logic into smaller,
    focused functions that each handle a single responsibility:
    
    1. Query analysis and intelligence
    2. Memory operations management
    3. Hybrid retrieval coordination
    4. Expert validation processing
    5. Orchestration coordination
    6. Memory updates
    7. Metrics recording
    """
    
    def __init__(self):
        """Initialize the refactored integration layer."""
        logger.info("🚀 Initializing Refactored Integration Layer")
        
        # Initialize components
        self.orchestrator = RefactoredOrchestrator()
        self.query_intelligence = QueryIntelligenceLayer()
        self.memory_manager = MemoryManager()
        self.retrieval_service = HybridRetrievalService()
        self.validation_layer = ExpertValidationLayer()
        self.metrics_collector = MetricsCollector()
        
        logger.info("✅ Refactored Integration Layer initialized successfully")
    
    async def process_query(self, request: IntegrationRequest) -> IntegrationResponse:
        """
        Main entry point for processing queries.
        
        This function orchestrates the complete pipeline by calling focused helper functions
        in sequence, each handling a single responsibility.
        """
        start_time = time.time()
        
        try:
            logger.info(f"📝 Processing query: {request.query[:50]}...")
            
            # Step 1: Analyze query using intelligence layer
            query_analysis = await self._analyze_query_intelligence(request)
            
            # Step 2: Handle memory operations
            memory_operations = await self._handle_memory_operations(request, query_analysis)
            
            # Step 3: Perform hybrid retrieval
            retrieval_result = await self._perform_hybrid_retrieval(request, query_analysis)
            
            # Step 4: Perform expert validation
            validation_result = await self._perform_expert_validation(request, retrieval_result)
            
            # Step 5: Execute orchestration
            orchestration_result = await self._execute_orchestration(request, retrieval_result, validation_result)
            
            # Step 6: Update memory with results
            await self._update_memory_with_results(request, orchestration_result)
            
            # Step 7: Record comprehensive metrics
            await self._record_comprehensive_metrics(request, query_analysis, orchestration_result, retrieval_result, validation_result)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            # Create response
            response = await self._create_integration_response(
                request, query_analysis, orchestration_result, retrieval_result,
                validation_result, memory_operations, processing_time
            )
            
            logger.info(f"✅ Query processed successfully in {processing_time:.2f}ms")
            return response
            
        except Exception as e:
            logger.error(f"❌ Query processing failed: {e}")
            processing_time = (time.time() - start_time) * 1000
            return await self._create_error_response(request, str(e), processing_time)
    
    async def _analyze_query_intelligence(self, request: IntegrationRequest) -> Dict[str, Any]:
        """
        Analyze query using intelligence layer.
        
        Single responsibility: Query analysis and intelligence processing
        """
        try:
            context = {
                "user_id": request.user_id,
                "session_id": request.session_id,
                **request.context
            }
            
            analysis_result = await self.query_intelligence.process_query(request.query, context)
            
            logger.info(f"🔍 Query analyzed - Intent: {analysis_result.get('intent', 'unknown')}, "
                       f"Complexity: {analysis_result.get('complexity', 'unknown')}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            # Return fallback analysis
            return {
                "original": request.query,
                "intent": "factual",
                "complexity": "moderate",
                "domain": "general",
                "fingerprint": "fallback_fingerprint",
                "routing_decision": "direct",
                "error": str(e)
            }
    
    async def _handle_memory_operations(self, request: IntegrationRequest, query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle memory operations for the query.
        
        Single responsibility: Memory operations management
        """
        try:
            memory_operations = {
                "retrieved_memories": [],
                "stored_memories": [],
                "memory_stats": {}
            }
            
            # Retrieve relevant memories
            memory_key = f"user:{request.user_id}:session:{request.session_id}"
            retrieved_memories = await self.memory_manager.retrieve_relevant_memories(
                request.query, memory_key
            )
            memory_operations["retrieved_memories"] = retrieved_memories
            
            # Get memory statistics
            memory_stats = await self.memory_manager.get_memory_stats()
            memory_operations["memory_stats"] = memory_stats
            
            logger.info(f"🧠 Memory operations completed - Retrieved: {len(retrieved_memories)} memories")
            
            return memory_operations
            
        except Exception as e:
            logger.error(f"Memory operations failed: {e}")
            return {
                "retrieved_memories": [],
                "stored_memories": [],
                "memory_stats": {},
                "error": str(e)
            }
    
    async def _perform_hybrid_retrieval(self, request: IntegrationRequest, query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform hybrid retrieval for the query.
        
        Single responsibility: Hybrid retrieval coordination
        """
        try:
            # Determine fusion strategy based on query analysis
            fusion_strategy = self._determine_fusion_strategy(query_analysis)
            
            # Perform retrieval
            retrieval_result = await self.retrieval_service.retrieve(
                query=request.query,
                max_results=10,
                fusion_strategy=fusion_strategy,
                sources=["vector", "keyword", "web"]
            )
            
            logger.info(f"🔍 Hybrid retrieval completed - Found {len(retrieval_result.get('results', []))} results")
            
            return retrieval_result
            
        except Exception as e:
            logger.error(f"Hybrid retrieval failed: {e}")
            return {
                "results": [],
                "fusion_strategy": "fallback",
                "total_sources": 0,
                "processing_time_ms": 0,
                "error": str(e)
            }
    
    async def _perform_expert_validation(self, request: IntegrationRequest, retrieval_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Perform expert validation for the query.
        
        Single responsibility: Expert validation processing
        """
        try:
            # Check if validation is needed based on query analysis
            if not self._requires_validation(request.query):
                logger.info("🔍 Skipping expert validation - not required for this query")
                return None
            
            # Extract claims from retrieval results
            claims = self._extract_claims_from_retrieval(retrieval_result)
            
            if not claims:
                logger.info("🔍 No claims to validate")
                return None
            
            # Perform validation
            validation_result = await self.validation_layer.validate_claims(claims, {
                "user_id": request.user_id,
                "session_id": request.session_id,
                "retrieval_results": retrieval_result.get("results", [])
            })
            
            logger.info(f"🔍 Expert validation completed - Validated {len(claims)} claims")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Expert validation failed: {e}")
            return {
                "overall_status": "failed",
                "consensus_level": "none",
                "consensus_score": 0.0,
                "expert_validations": [],
                "final_confidence": 0.0,
                "reasoning": f"Validation failed: {str(e)}",
                "processing_time_ms": 0
            }
    
    async def _execute_orchestration(self, request: IntegrationRequest, retrieval_result: Dict[str, Any], validation_result: Optional[Dict[str, Any]]) -> PipelineResult:
        """
        Execute orchestration for the query.
        
        Single responsibility: Orchestration coordination
        """
        try:
            # Prepare user context for orchestration
            user_context = {
                "user_id": request.user_id,
                "session_id": request.session_id,
                "retrieval_results": retrieval_result.get("results", []),
                "validation_result": validation_result,
                "preferences": request.preferences,
                "model": request.model
            }
            
            # Execute orchestration
            orchestration_result = await self.orchestrator.process_query(
                query=request.query,
                user_context=user_context
            )
            
            logger.info(f"🎯 Orchestration completed - Success: {orchestration_result.success}, "
                       f"Confidence: {orchestration_result.confidence}")
            
            return orchestration_result
            
        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            return PipelineResult(
                success=False,
                errors=[str(e)],
                total_execution_time_ms=0
            )
    
    async def _update_memory_with_results(self, request: IntegrationRequest, orchestration_result: PipelineResult) -> None:
        """
        Update memory with orchestration results.
        
        Single responsibility: Memory updates with results
        """
        try:
            if not orchestration_result.success:
                logger.warning("Skipping memory update - orchestration failed")
                return
            
            # Store the query and result in memory
            memory_key = f"user:{request.user_id}:session:{request.session_id}"
            memory_data = {
                "query": request.query,
                "answer": orchestration_result.final_answer,
                "confidence": orchestration_result.confidence,
                "sources": orchestration_result.sources,
                "timestamp": time.time()
            }
            
            await self.memory_manager.store(
                key=memory_key,
                value=memory_data,
                memory_type="working",
                priority="medium"
            )
            
            logger.info("🧠 Memory updated with orchestration results")
            
        except Exception as e:
            logger.error(f"Memory update failed: {e}")
    
    async def _record_comprehensive_metrics(self, request: IntegrationRequest, query_analysis: Dict[str, Any], 
                                          orchestration_result: PipelineResult, retrieval_result: Dict[str, Any], 
                                          validation_result: Optional[Dict[str, Any]]) -> None:
        """
        Record comprehensive metrics for the query.
        
        Single responsibility: Metrics recording and analysis
        """
        try:
            metrics_data = {
                "query": request.query,
                "user_id": request.user_id,
                "session_id": request.session_id,
                "query_analysis": query_analysis,
                "orchestration_success": orchestration_result.success,
                "orchestration_confidence": orchestration_result.confidence,
                "retrieval_results_count": len(retrieval_result.get("results", [])),
                "validation_performed": validation_result is not None,
                "processing_time_ms": orchestration_result.total_execution_time_ms,
                "timestamp": time.time()
            }
            
            await self.metrics_collector.record_query_metrics(metrics_data)
            
            logger.info("📊 Comprehensive metrics recorded")
            
        except Exception as e:
            logger.error(f"Metrics recording failed: {e}")
    
    async def _create_integration_response(self, request: IntegrationRequest, query_analysis: Dict[str, Any],
                                         orchestration_result: PipelineResult, retrieval_result: Dict[str, Any],
                                         validation_result: Optional[Dict[str, Any]], memory_operations: Dict[str, Any],
                                         processing_time: float) -> IntegrationResponse:
        """
        Create the final integration response.
        
        Single responsibility: Response formatting and finalization
        """
        return IntegrationResponse(
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
                "components_used": ["query_intelligence", "orchestration", "retrieval", "validation", "memory"],
                "stages_completed": [stage.value for stage in ProcessingStage]
            }
        )
    
    async def _create_error_response(self, request: IntegrationRequest, error_message: str, processing_time: float) -> IntegrationResponse:
        """
        Create error response for failed processing.
        
        Single responsibility: Error response creation
        """
        return IntegrationResponse(
            success=False,
            processing_time_ms=processing_time,
            error_message=error_message,
            metadata={
                "user_id": request.user_id,
                "session_id": request.session_id,
                "error_type": "processing_failure"
            }
        )
    
    def _determine_fusion_strategy(self, query_analysis: Dict[str, Any]) -> str:
        """Determine fusion strategy based on query analysis."""
        intent = query_analysis.get("intent", "factual")
        complexity = query_analysis.get("complexity", "moderate")
        
        if complexity == "high":
            return "weighted"
        elif intent == "factual":
            return "consensus"
        else:
            return "simple"
    
    def _requires_validation(self, query: str) -> bool:
        """Determine if the query requires expert validation."""
        # Simple heuristic - could be enhanced with ML
        validation_keywords = ["fact", "true", "verify", "confirm", "accurate", "correct"]
        return any(keyword in query.lower() for keyword in validation_keywords)
    
    def _extract_claims_from_retrieval(self, retrieval_result: Dict[str, Any]) -> List[str]:
        """Extract claims from retrieval results for validation."""
        claims = []
        results = retrieval_result.get("results", [])
        
        for result in results:
            if isinstance(result, dict) and "content" in result:
                # Simple claim extraction - could be enhanced with NLP
                content = result["content"]
                if len(content) > 50:  # Only consider substantial content
                    claims.append(content[:200])  # Limit claim length
        
        return claims


# Mock implementations for the helper classes
class QueryIntelligenceLayer:
    """Mock query intelligence layer."""
    
    async def process_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "original": query,
            "intent": "factual",
            "complexity": "moderate",
            "domain": "general",
            "fingerprint": "mock_fingerprint",
            "routing_decision": "direct"
        }


class MemoryManager:
    """Mock memory manager."""
    
    async def retrieve_relevant_memories(self, query: str, memory_key: str) -> List[Dict[str, Any]]:
        return []
    
    async def store(self, key: str, value: Dict[str, Any], memory_type: str, priority: str) -> None:
        pass
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        return {"total_memories": 0, "memory_types": {}}


class HybridRetrievalService:
    """Mock hybrid retrieval service."""
    
    async def retrieve(self, query: str, max_results: int = 10, fusion_strategy: str = "simple", sources: List[str] = None) -> Dict[str, Any]:
        return {
            "results": [],
            "fusion_strategy": fusion_strategy,
            "total_sources": 0,
            "processing_time_ms": 0
        }


class ExpertValidationLayer:
    """Mock expert validation layer."""
    
    async def validate_claims(self, claims: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "overall_status": "verified",
            "consensus_level": "strong_consensus",
            "consensus_score": 0.9,
            "expert_validations": [],
            "final_confidence": 0.9,
            "reasoning": "Mock validation completed",
            "processing_time_ms": 0
        }


class MetricsCollector:
    """Mock metrics collector."""
    
    async def record_query_metrics(self, metrics_data: Dict[str, Any]) -> None:
        pass


async def get_refactored_integration_layer() -> RefactoredIntegrationLayer:
    """Get the refactored integration layer instance."""
    return RefactoredIntegrationLayer() 