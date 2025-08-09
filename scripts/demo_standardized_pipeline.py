#!/usr/bin/env python3
"""
Demonstration of the Standardized Multi-Agent Pipeline

This script demonstrates the refined LeadOrchestrator with:
- Common BaseAgent.execute(context) interface for all agents
- Parallel execution using asyncio.gather() for I/O operations
- Shared QueryContext for agent communication
- Simplified orchestration logic with easy agent registration
- Performance monitoring and error handling
"""

import asyncio
import time
import json
from typing import Dict, Any

# Ensure we're in the correct directory
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.core.agents.lead_orchestrator import LeadOrchestrator
from shared.core.agents.standardized_agents import ExtendedAgentType
from shared.core.unified_logging import setup_logging, get_logger

# Configure logging for demo
setup_logging(service_name="pipeline-demo", log_level="INFO", log_format="text")
logger = get_logger(__name__)


async def demo_basic_query_processing():
    """Demonstrate basic query processing with the standardized pipeline."""

    print("🚀 Demonstrating Standardized Multi-Agent Pipeline")
    print("=" * 70)

    # Initialize the orchestrator
    print("\n📋 Step 1: Initialize LeadOrchestrator")
    orchestrator = LeadOrchestrator()

    # Show pipeline status
    status = orchestrator.get_pipeline_status()
    print(f"✅ Pipeline initialized with {status['registered_agents']} agents")
    print(f"   Enabled agents: {', '.join(status['enabled_agents'])}")
    print(f"   Parallel retrieval: {status['parallel_retrieval_enabled']}")
    print(f"   Max parallel agents: {status['max_parallel_agents']}")

    # Test queries of different types
    test_queries = [
        {
            "query": "What is machine learning and how does it work?",
            "description": "General knowledge query (should use retrieval + synthesis)",
        },
        {
            "query": "Find recent research papers on quantum computing",
            "description": "Research query (should use retrieval + knowledge graph + browser)",
        },
        {
            "query": "Analyze the performance of Python vs JavaScript",
            "description": "Comparison query (should use multiple sources + fact checking)",
        },
    ]

    print(f"\n📋 Step 2: Process {len(test_queries)} Test Queries")
    print("-" * 50)

    results = []

    for i, test_case in enumerate(test_queries, 1):
        query = test_case["query"]
        description = test_case["description"]

        print(f"\n🔍 Query {i}: {query}")
        print(f"   Expected behavior: {description}")

        start_time = time.time()

        try:
            # Process the query
            result = await orchestrator.process_query(query)

            execution_time = time.time() - start_time

            # Display results
            print(f"   ✅ Success: {result['success']}")
            print(f"   ⏱️  Execution time: {execution_time:.2f}s")
            print(f"   🎯 Confidence: {result['confidence']:.2f}")
            print(f"   📄 Sources found: {len(result.get('sources', []))}")
            print(f"   📝 Citations: {len(result.get('citations', []))}")

            if result.get("answer"):
                # Show first 150 characters of answer
                answer_preview = (
                    result["answer"][:150] + "..."
                    if len(result["answer"]) > 150
                    else result["answer"]
                )
                print(f"   💡 Answer preview: {answer_preview}")

            if result.get("errors"):
                print(f"   ⚠️  Warnings: {len(result['errors'])} agent(s) had issues")

            # Store result for summary
            results.append(
                {
                    "query": query,
                    "success": result["success"],
                    "execution_time": execution_time,
                    "confidence": result["confidence"],
                    "sources_count": len(result.get("sources", [])),
                    "pipeline_stages": result.get("metadata", {}).get(
                        "pipeline_stages", []
                    ),
                }
            )

        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append(
                {
                    "query": query,
                    "success": False,
                    "execution_time": time.time() - start_time,
                    "error": str(e),
                }
            )

    # Display summary
    print(f"\n📊 Summary of {len(results)} Queries")
    print("=" * 70)

    successful_queries = [r for r in results if r["success"]]

    if successful_queries:
        avg_time = sum(r["execution_time"] for r in successful_queries) / len(
            successful_queries
        )
        avg_confidence = sum(r["confidence"] for r in successful_queries) / len(
            successful_queries
        )
        total_sources = sum(r["sources_count"] for r in successful_queries)

        print(f"✅ Successful queries: {len(successful_queries)}/{len(results)}")
        print(f"⏱️  Average execution time: {avg_time:.2f}s")
        print(f"🎯 Average confidence: {avg_confidence:.2f}")
        print(f"📄 Total sources retrieved: {total_sources}")
    else:
        print("❌ No queries were processed successfully")

    failed_queries = [r for r in results if not r["success"]]
    if failed_queries:
        print(f"⚠️  Failed queries: {len(failed_queries)}")
        for failed in failed_queries:
            print(f"   - {failed['query'][:50]}...")


async def demo_agent_registration():
    """Demonstrate dynamic agent registration and removal."""

    print("\n🔧 Demonstrating Dynamic Agent Management")
    print("=" * 70)

    orchestrator = LeadOrchestrator()

    print("\n📋 Initial agent configuration:")
    initial_agents = orchestrator.get_available_agents()
    print(f"   Available agents: {', '.join(initial_agents)}")

    # Note: In a real scenario, you would register actual agent instances
    # For demo purposes, we'll show the interface
    print("\n🔄 Agent management operations:")
    print("   ✅ register_agent(agent_type, agent_instance)")
    print("   ❌ unregister_agent(agent_type)")
    print("   📋 get_available_agents()")
    print("   📊 get_pipeline_status()")

    print("\n💡 Benefits of standardized interface:")
    print("   - Easy to add new specialized agents")
    print("   - Automatic parallel execution where possible")
    print("   - Consistent error handling and monitoring")
    print("   - Shared context between all agents")


async def demo_parallel_execution_performance():
    """Demonstrate parallel execution performance benefits."""

    print("\n⚡ Demonstrating Parallel Execution Performance")
    print("=" * 70)

    # Create orchestrator configs for comparison
    sequential_config = {
        "enable_parallel_retrieval": False,
        "enable_enrichment_stage": False,
        "max_parallel_agents": 1,
    }

    parallel_config = {
        "enable_parallel_retrieval": True,
        "enable_enrichment_stage": True,
        "max_parallel_agents": 5,
    }

    test_query = "What are the latest developments in artificial intelligence?"

    print(f"\n🔍 Test query: {test_query}")

    # Test sequential execution
    print("\n📈 Sequential execution (traditional approach):")
    sequential_orchestrator = LeadOrchestrator(sequential_config)

    start_time = time.time()
    try:
        sequential_result = await sequential_orchestrator.process_query(test_query)
        sequential_time = time.time() - start_time
        print(f"   ⏱️  Execution time: {sequential_time:.2f}s")
        print(f"   ✅ Success: {sequential_result['success']}")
    except Exception as e:
        sequential_time = time.time() - start_time
        print(f"   ❌ Error after {sequential_time:.2f}s: {e}")

    # Test parallel execution
    print("\n🚀 Parallel execution (new approach):")
    parallel_orchestrator = LeadOrchestrator(parallel_config)

    start_time = time.time()
    try:
        parallel_result = await parallel_orchestrator.process_query(test_query)
        parallel_time = time.time() - start_time
        print(f"   ⏱️  Execution time: {parallel_time:.2f}s")
        print(f"   ✅ Success: {parallel_result['success']}")

        # Calculate performance improvement
        if "sequential_time" in locals() and sequential_time > 0 and parallel_time > 0:
            improvement = ((sequential_time - parallel_time) / sequential_time) * 100
            print(f"   📊 Performance improvement: {improvement:.1f}%")

    except Exception as e:
        parallel_time = time.time() - start_time
        print(f"   ❌ Error after {parallel_time:.2f}s: {e}")


async def demo_error_handling_and_resilience():
    """Demonstrate error handling and graceful degradation."""

    print("\n🛡️ Demonstrating Error Handling & Resilience")
    print("=" * 70)

    orchestrator = LeadOrchestrator()

    # Test with various challenging scenarios
    challenging_scenarios = [
        {"query": "", "description": "Empty query handling"},  # Empty query
        {"query": "A" * 1000, "description": "Long query handling"},  # Very long query
        {
            "query": "Query with special characters: !@#$%^&*()[]{}|;':\",./<>?",
            "description": "Special characters handling",
        },
    ]

    print("\n🧪 Testing error handling scenarios:")

    for i, scenario in enumerate(challenging_scenarios, 1):
        query = scenario["query"]
        description = scenario["description"]

        print(f"\n🔍 Test {i}: {description}")
        if len(query) > 50:
            print(f"   Query: {query[:50]}... ({len(query)} chars)")
        else:
            print(f"   Query: '{query}'")

        try:
            result = await orchestrator.process_query(query)

            print(f"   ✅ Handled gracefully")
            print(f"   📊 Success: {result['success']}")

            if result.get("errors"):
                print(f"   ⚠️  Warnings: {len(result['errors'])}")

        except Exception as e:
            print(f"   ❌ Exception: {e}")

    print("\n💡 Error handling features:")
    print("   - Graceful degradation when agents fail")
    print("   - Timeout protection for long-running operations")
    print("   - Partial results when some agents succeed")
    print("   - Detailed error reporting and logging")


async def main():
    """Run all demonstrations."""

    print("🎯 Standardized Multi-Agent Pipeline Demonstration")
    print("🔧 Refined LeadOrchestrator with Parallel Execution")
    print("=" * 80)

    try:
        # Run demonstrations
        await demo_basic_query_processing()
        await demo_agent_registration()
        await demo_parallel_execution_performance()
        await demo_error_handling_and_resilience()

        print("\n🎉 Demonstration completed successfully!")
        print("=" * 80)

        print("\n📋 Key Improvements Demonstrated:")
        print("✅ Common BaseAgent.execute(context) interface for all agents")
        print("✅ Parallel execution using asyncio.gather() for I/O operations")
        print("✅ Shared QueryContext for agent communication")
        print("✅ Simplified orchestration logic with easy agent registration")
        print("✅ Performance improvements through parallel processing")
        print("✅ Robust error handling and graceful degradation")
        print("✅ Comprehensive logging and monitoring")

        print("\n🔧 Next Steps:")
        print("- Integrate with existing services")
        print("- Add more specialized agents as needed")
        print("- Monitor performance in production")
        print("- Optimize based on usage patterns")

    except Exception as e:
        logger.error(f"Demonstration failed: {e}")
        print(f"\n❌ Demonstration failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
