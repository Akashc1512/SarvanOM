#!/usr/bin/env python3
"""
Test script for standardized multi-agent pipeline
"""

import asyncio
import logging
import time
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_standardized_pipeline():
    """Test the standardized pipeline with various queries."""
    
    # Import the standardized orchestrator
    from shared.core.agents.lead_orchestrator import StandardizedLeadOrchestrator
    
    print("🧪 Testing Standardized Multi-Agent Pipeline")
    print("=" * 60)
    
    # Initialize the orchestrator
    orchestrator = StandardizedLeadOrchestrator()
    
    # Test queries
    test_queries = [
        {
            "query": "What is machine learning?",
            "user_context": {"user_id": "test_user_1", "model": "auto"},
            "description": "Basic factual query"
        },
        {
            "query": "How does climate change affect biodiversity?",
            "user_context": {"user_id": "test_user_2", "model": "gpt-4"},
            "description": "Complex analytical query"
        },
        {
            "query": "What are the latest developments in quantum computing?",
            "user_context": {"user_id": "test_user_3", "model": "auto"},
            "description": "Current events query"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📋 Test Case {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")
        
        try:
            start_time = time.time()
            
            # Process the query
            result = await orchestrator.process_query(
                query=test_case["query"],
                user_context=test_case["user_context"]
            )
            
            processing_time = time.time() - start_time
            
            # Analyze results
            if result.get("success", False):
                print(f"✅ Query processed successfully in {processing_time:.2f}s")
                print(f"   Answer length: {len(result.get('answer', ''))} characters")
                print(f"   Confidence: {result.get('confidence', 0.0):.2f}")
                print(f"   Citations: {len(result.get('citations', []))}")
                print(f"   Pipeline stages: {result.get('metadata', {}).get('pipeline_stages', [])}")
                
                # Check pipeline stages
                stages = result.get('metadata', {}).get('pipeline_stages', [])
                expected_stages = ['retrieval', 'fact_check', 'synthesis', 'citation']
                missing_stages = [stage for stage in expected_stages if stage not in stages]
                if missing_stages:
                    print(f"   ⚠️ Missing stages: {missing_stages}")
                else:
                    print(f"   ✅ All expected stages completed")
                
                # Check timing
                stage_timings = result.get('metadata', {}).get('stage_timings', {})
                if stage_timings:
                    print(f"   Stage timings:")
                    for stage, timing in stage_timings.items():
                        print(f"     - {stage}: {timing:.3f}s")
                
            else:
                print(f"❌ Query processing failed")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                print(f"   Error type: {result.get('error_type', 'unknown')}")
            
        except Exception as e:
            print(f"❌ Exception during processing: {e}")
    
    # Test pipeline status
    print(f"\n📊 Pipeline Status:")
    try:
        status = await orchestrator.get_pipeline_status()
        print(f"   Registered agents: {status.get('registered_agents', [])}")
        print(f"   Pipeline stages: {status.get('pipeline_stages', [])}")
        print(f"   Parallel groups: {status.get('parallel_groups', [])}")
    except Exception as e:
        print(f"   ❌ Error getting pipeline status: {e}")
    
    # Test agent registration
    print(f"\n🔧 Testing Agent Registration:")
    try:
        # Test registering a new agent (mock)
        from shared.core.agents.base_agent import AgentType, BaseAgent
        
        class MockAgent(BaseAgent):
            def __init__(self):
                super().__init__("mock_agent", AgentType.RETRIEVAL)
            
            async def process_task(self, task, context):
                return {
                    "success": True,
                    "data": {"mock_result": "test"},
                    "confidence": 0.8,
                    "token_usage": {"prompt": 10, "completion": 5},
                    "metadata": {"agent_type": "mock"}
                }
        
        mock_agent = MockAgent()
        await orchestrator.register_agent(AgentType.RETRIEVAL, mock_agent)
        print(f"   ✅ Mock agent registered successfully")
        
        # Test unregistering
        await orchestrator.unregister_agent(AgentType.RETRIEVAL)
        print(f"   ✅ Mock agent unregistered successfully")
        
    except Exception as e:
        print(f"   ❌ Error testing agent registration: {e}")
    
    # Cleanup
    try:
        await orchestrator.shutdown()
        print(f"\n✅ Orchestrator shutdown completed")
    except Exception as e:
        print(f"\n❌ Error during shutdown: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"✅ Standardized Pipeline Tests Completed!")

async def test_parallel_execution():
    """Test parallel execution capabilities."""
    
    print(f"\n🔄 Testing Parallel Execution")
    print("=" * 40)
    
    from shared.core.agents.lead_orchestrator import StandardizedLeadOrchestrator
    
    orchestrator = StandardizedLeadOrchestrator()
    
    try:
        # Test a query that should trigger parallel execution
        query = "What are the latest developments in artificial intelligence?"
        user_context = {"user_id": "parallel_test_user", "model": "auto"}
        
        start_time = time.time()
        result = await orchestrator.process_query(query, user_context)
        total_time = time.time() - start_time
        
        print(f"Query: {query}")
        print(f"Total processing time: {total_time:.2f}s")
        
        if result.get("success", False):
            print(f"✅ Parallel execution test successful")
            
            # Check if parallel stages were executed
            stage_timings = result.get('metadata', {}).get('stage_timings', {})
            if 'retrieval' in stage_timings and 'knowledge_graph' in stage_timings:
                retrieval_time = stage_timings.get('retrieval', 0)
                knowledge_time = stage_timings.get('knowledge_graph', 0)
                max_parallel_time = max(retrieval_time, knowledge_time)
                sequential_time = retrieval_time + knowledge_time
                
                print(f"   Retrieval time: {retrieval_time:.3f}s")
                print(f"   Knowledge graph time: {knowledge_time:.3f}s")
                print(f"   Sequential time would be: {sequential_time:.3f}s")
                print(f"   Actual parallel time: {max_parallel_time:.3f}s")
                print(f"   Time saved: {sequential_time - max_parallel_time:.3f}s")
                
                if max_parallel_time < sequential_time:
                    print(f"   ✅ Parallel execution confirmed")
                else:
                    print(f"   ⚠️ No parallel execution detected")
        else:
            print(f"❌ Parallel execution test failed")
            
    except Exception as e:
        print(f"❌ Error in parallel execution test: {e}")
    
    finally:
        await orchestrator.shutdown()

async def main():
    """Run all tests."""
    print("🚀 Starting Standardized Pipeline Tests")
    
    await test_standardized_pipeline()
    await test_parallel_execution()
    
    print(f"\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 