#!/usr/bin/env python3
"""
Test the refined multi-agent pipeline with real agent instances.
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_pipeline_components():
    """Test individual pipeline components."""
    print("🧪 Testing Pipeline Components")
    print("=" * 50)

    try:
        # Test imports
        print("📦 Testing imports...")
        from shared.core.agents.refined_lead_orchestrator import (
            RefinedLeadOrchestrator,
            PipelineConfig,
        )
        from shared.core.agents.standardized_agents import ExtendedAgentType
        from shared.core.agents.base_agent import QueryContext

        print("✅ All imports successful")

        # Test pipeline configuration
        print("\n⚙️ Testing pipeline configuration...")
        config = PipelineConfig(
            max_parallel_agents=3,
            enable_parallel_retrieval=True,
            enable_enrichment_stage=False,  # Disable to avoid service dependencies
            enabled_agents={
                ExtendedAgentType.RETRIEVAL,
                ExtendedAgentType.FACT_CHECK,
                ExtendedAgentType.SYNTHESIS,
                ExtendedAgentType.CITATION,
            },
        )
        print("✅ Pipeline configuration created")

        # Test orchestrator initialization
        print("\n🚀 Testing orchestrator initialization...")
        orchestrator = RefinedLeadOrchestrator(config)
        print(
            f"✅ Orchestrator initialized with {len(orchestrator.agent_registry)} agents"
        )

        # List registered agents
        registered_agents = list(orchestrator.agent_registry.keys())
        print(f"📋 Registered agents: {[agent.value for agent in registered_agents]}")

        # Test context creation
        print("\n📝 Testing query context...")
        context = QueryContext(
            query="What is machine learning?",
            user_context={"test": True},
            metadata={"test_mode": True},
        )
        print("✅ Query context created")

        return orchestrator, context

    except Exception as e:
        print(f"❌ Component test failed: {e}")
        import traceback

        traceback.print_exc()
        return None, None


async def test_single_agent_execution():
    """Test executing a single agent."""
    print("\n🔍 Testing Single Agent Execution")
    print("=" * 50)

    try:
        from shared.core.agents.retrieval_agent import RetrievalAgent
        from shared.core.agents.base_agent import QueryContext

        # Create a retrieval agent
        agent = RetrievalAgent()
        print("✅ RetrievalAgent created")

        # Create test context
        context = QueryContext(
            query="What is artificial intelligence?",
            user_context={"test": True},
            metadata={"test_mode": True},
        )

        # Test the execute method
        print("⚡ Testing agent.execute(context)...")
        result = await agent.execute(context)

        print(f"✅ Agent execution completed:")
        print(f"   Success: {result.success}")
        print(f"   Execution time: {result.execution_time_ms}ms")
        if result.error:
            print(f"   Error: {result.error}")
        if result.data:
            print(f"   Data available: {type(result.data)}")

        return result.success

    except Exception as e:
        print(f"❌ Single agent test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_parallel_execution():
    """Test parallel agent execution."""
    print("\n⚡ Testing Parallel Execution")
    print("=" * 50)

    try:
        from shared.core.agents.retrieval_agent import RetrievalAgent
        from shared.core.agents.synthesis_agent import SynthesisAgent
        from shared.core.agents.base_agent import QueryContext

        # Create agents
        retrieval_agent = RetrievalAgent()
        synthesis_agent = SynthesisAgent()
        print("✅ Agents created")

        # Create test context
        context = QueryContext(
            query="Explain quantum computing",
            user_context={"test": True},
            metadata={"test_mode": True},
        )

        # Test parallel execution
        print("⚡ Testing parallel execution with asyncio.gather...")
        start_time = asyncio.get_event_loop().time()

        # Run agents in parallel
        results = await asyncio.gather(
            retrieval_agent.execute(context),
            synthesis_agent.execute(context),
            return_exceptions=True,
        )

        end_time = asyncio.get_event_loop().time()
        execution_time = (end_time - start_time) * 1000

        print(f"✅ Parallel execution completed in {execution_time:.1f}ms")

        # Check results
        successful_agents = 0
        for i, result in enumerate(results):
            agent_name = ["RetrievalAgent", "SynthesisAgent"][i]
            if isinstance(result, Exception):
                print(f"   ❌ {agent_name}: {result}")
            else:
                print(f"   ✅ {agent_name}: Success={result.success}")
                if result.success:
                    successful_agents += 1

        print(f"📊 {successful_agents}/{len(results)} agents completed successfully")
        return successful_agents > 0

    except Exception as e:
        print(f"❌ Parallel execution test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_full_pipeline():
    """Test the full refined pipeline."""
    print("\n🎯 Testing Full Refined Pipeline")
    print("=" * 50)

    try:
        # Get orchestrator from component test
        orchestrator, context = await test_pipeline_components()
        if not orchestrator or not context:
            print("❌ Cannot test pipeline - component initialization failed")
            return False

        # Test pipeline execution
        print("⚡ Testing full pipeline execution...")
        start_time = asyncio.get_event_loop().time()

        result = await orchestrator.process_query(
            query="What are the benefits of renewable energy?",
            user_context={"test": True},
        )

        end_time = asyncio.get_event_loop().time()
        execution_time = (end_time - start_time) * 1000

        print(f"✅ Pipeline execution completed in {execution_time:.1f}ms")
        print(f"📊 Pipeline Results:")
        print(f"   Success: {result.success}")
        print(f"   Confidence: {result.confidence}")
        print(f"   Total execution time: {result.total_execution_time_ms}ms")
        print(f"   Sources found: {len(result.sources)}")
        print(f"   Citations: {len(result.citations)}")

        if result.errors:
            print(f"   ⚠️ Errors: {len(result.errors)}")
            for error in result.errors[:3]:  # Show first 3 errors
                print(f"      - {error}")

        if result.failed_agents:
            print(f"   ⚠️ Failed agents: {result.failed_agents}")

        # Show pipeline stages that completed
        completed_stages = list(result.stage_results.keys())
        print(f"   📋 Completed stages: {completed_stages}")

        if result.final_answer:
            answer_preview = (
                result.final_answer[:100] + "..."
                if len(result.final_answer) > 100
                else result.final_answer
            )
            print(f"   💡 Answer preview: {answer_preview}")

        return result.success

    except Exception as e:
        print(f"❌ Full pipeline test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("🎯 Refined Multi-Agent Pipeline Testing")
    print("🔧 Testing Core Functionality")
    print("=" * 70)

    test_results = []

    # Test 1: Component initialization
    print("\n1️⃣ COMPONENT INITIALIZATION TEST")
    orchestrator, context = await test_pipeline_components()
    test_results.append(orchestrator is not None and context is not None)

    # Test 2: Single agent execution
    print("\n2️⃣ SINGLE AGENT EXECUTION TEST")
    single_agent_success = await test_single_agent_execution()
    test_results.append(single_agent_success)

    # Test 3: Parallel execution
    print("\n3️⃣ PARALLEL EXECUTION TEST")
    parallel_success = await test_parallel_execution()
    test_results.append(parallel_success)

    # Test 4: Full pipeline (only if basics work)
    if all(test_results):
        print("\n4️⃣ FULL PIPELINE TEST")
        pipeline_success = await test_full_pipeline()
        test_results.append(pipeline_success)
    else:
        print("\n4️⃣ FULL PIPELINE TEST - SKIPPED (basic tests failed)")
        test_results.append(False)

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    test_names = [
        "Component Initialization",
        "Single Agent Execution",
        "Parallel Execution",
        "Full Pipeline",
    ]

    passed = sum(test_results)
    total = len(test_results)

    for i, (name, result) in enumerate(zip(test_names, test_results), 1):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i}. {name}: {status}")

    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Refined pipeline is working correctly.")
        print("\n✅ Key Features Verified:")
        print("   - Component initialization and configuration")
        print("   - BaseAgent.execute(context) interface compatibility")
        print("   - Parallel execution using asyncio.gather()")
        print("   - Full pipeline orchestration with error handling")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting Tips:")
        print("   - Ensure all required dependencies are installed")
        print("   - Check that services are properly configured")
        print("   - Verify agent implementations have required methods")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
