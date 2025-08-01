#!/usr/bin/env python3
"""
Test script to check Week 1 components integration with backend.
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_week1_integration():
    """Test all Week 1 components integration."""
    print("🚀 Testing Week 1 Components Integration")
    print("=" * 50)
    
    results = {}
    
    try:
        # Test 1: Query Intelligence Layer
        print("\n1. Testing Query Intelligence Layer...")
        try:
            from services.search_service.core.query_processor import QueryIntelligenceLayer
            
            qil = QueryIntelligenceLayer()
            test_query = "What is artificial intelligence?"
            test_context = {"user_id": "test_user", "session_id": "test_session"}
            
            result = await qil.process_query(test_query, test_context)
            print(f"✅ Query Intelligence: {result.intent} | {result.complexity}")
            results["query_intelligence"] = "PASSED"
            
        except Exception as e:
            print(f"❌ Query Intelligence failed: {e}")
            results["query_intelligence"] = f"FAILED: {e}"
        
        # Test 2: Multi-Agent Orchestration
        print("\n2. Testing Multi-Agent Orchestration...")
        try:
            from services.synthesis_service.core.orchestrator import MultiAgentOrchestrator
            
            orchestrator = MultiAgentOrchestrator()
            test_request = "Explain quantum computing"
            test_context = {"user_id": "test_user"}
            
            result = await orchestrator.process_request(test_request, context=test_context)
            print(f"✅ Orchestration: {result.model_used.value} | {result.processing_time_ms:.2f}ms")
            results["orchestration"] = "PASSED"
            
        except Exception as e:
            print(f"❌ Orchestration failed: {e}")
            results["orchestration"] = f"FAILED: {e}"
        
        # Test 3: Hybrid Retrieval
        print("\n3. Testing Hybrid Retrieval...")
        try:
            from services.search_service.core.hybrid_retrieval import HybridRetrievalEngine
            
            retrieval = HybridRetrievalEngine()
            test_query = "machine learning algorithms"
            
            result = await retrieval.retrieve(test_query, max_results=5)
            print(f"✅ Hybrid Retrieval: {len(result.source_results)} results | {result.processing_time_ms:.2f}ms")
            results["hybrid_retrieval"] = "PASSED"
            
        except Exception as e:
            print(f"❌ Hybrid Retrieval failed: {e}")
            results["hybrid_retrieval"] = f"FAILED: {e}"
        
        # Test 4: Memory Management
        print("\n4. Testing Memory Management...")
        try:
            from shared.core.memory_manager import MemoryManager, MemoryType
            
            memory = MemoryManager()
            test_key = "test_key"
            test_value = {"data": "test_value", "timestamp": datetime.now().isoformat()}
            
            # Store
            await memory.store(test_key, test_value, MemoryType.SHORT_TERM)
            
            # Retrieve
            retrieved = await memory.retrieve(test_key, MemoryType.SHORT_TERM)
            
            # Delete
            await memory.delete(test_key, MemoryType.SHORT_TERM)
            
            print(f"✅ Memory Management: Store/Retrieve/Delete operations successful")
            results["memory_management"] = "PASSED"
            
        except Exception as e:
            print(f"❌ Memory Management failed: {e}")
            results["memory_management"] = f"FAILED: {e}"
        
        # Test 5: Expert Validation
        print("\n5. Testing Expert Validation...")
        try:
            from services.factcheck_service.core.expert_validation import ExpertValidationLayer
            
            validator = ExpertValidationLayer()
            test_claim = "Python is a programming language"
            
            result = await validator.validate_fact(test_claim)
            print(f"✅ Expert Validation: {result.overall_status.value} | {result.consensus_level.value}")
            results["expert_validation"] = "PASSED"
            
        except Exception as e:
            print(f"❌ Expert Validation failed: {e}")
            results["expert_validation"] = f"FAILED: {e}"
        
        # Test 6: Integration Layer
        print("\n6. Testing Integration Layer...")
        try:
            from services.api_gateway.integration_layer import UniversalKnowledgePlatformIntegration
            
            integration = UniversalKnowledgePlatformIntegration()
            
            # Test system health
            health = await integration.get_system_health()
            print(f"✅ Integration Layer: {health['status']} | {len(health['components'])} components")
            results["integration_layer"] = "PASSED"
            
        except Exception as e:
            print(f"❌ Integration Layer failed: {e}")
            results["integration_layer"] = f"FAILED: {e}"
        
        # Test 7: Metrics Collection
        print("\n7. Testing Metrics Collection...")
        try:
            from services.analytics_service.metrics.knowledge_platform_metrics import KnowledgePlatformMetricsCollector
            
            metrics = KnowledgePlatformMetricsCollector()
            # Get metrics directly from the collector
            print(f"✅ Metrics Collection: Metrics collector initialized successfully")
            results["metrics_collection"] = "PASSED"
            
        except Exception as e:
            print(f"❌ Metrics Collection failed: {e}")
            results["metrics_collection"] = f"FAILED: {e}"
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 INTEGRATION TEST RESULTS")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for component, status in results.items():
            if "PASSED" in status:
                print(f"✅ {component}: PASSED")
                passed += 1
            else:
                print(f"❌ {component}: {status}")
        
        success_rate = (passed / total) * 100
        print(f"\n🎯 Success Rate: {success_rate:.1f}% ({passed}/{total} components)")
        
        if success_rate >= 80:
            print("🎉 Week 1 Integration: EXCELLENT!")
        elif success_rate >= 60:
            print("✅ Week 1 Integration: GOOD")
        else:
            print("⚠️ Week 1 Integration: NEEDS IMPROVEMENT")
        
        return success_rate >= 80
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    # Set UTF-8 encoding
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    
    # Run the test
    result = asyncio.run(test_week1_integration())
    sys.exit(0 if result else 1) 