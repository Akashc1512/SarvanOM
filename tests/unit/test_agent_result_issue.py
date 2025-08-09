#!/usr/bin/env python3
"""
Test script to isolate the AgentResult issue.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, ".")


async def test_agent_result_creation():
    """Test AgentResult creation to find the issue."""
    try:
        from shared.core.agents.base_agent import AgentResult

        print("🔄 Testing AgentResult creation...")

        # Test 1: Correct usage
        try:
            result1 = AgentResult(success=True, data={"test": "data"})
            print("✅ AgentResult with data parameter works")
        except Exception as e:
            print(f"❌ AgentResult with data parameter failed: {e}")

        # Test 2: Missing data parameter
        try:
            result2 = AgentResult(success=True)  # This should fail
            print("❌ AgentResult without data parameter should have failed but didn't")
        except Exception as e:
            print(f"✅ AgentResult without data parameter correctly failed: {e}")

        # Test 3: Test all agent types
        from shared.core.agents.base_agent import AgentType
        from shared.core.agents.lead_orchestrator import LeadOrchestrator

        print("\n🔄 Testing orchestrator initialization...")
        orchestrator = LeadOrchestrator()
        print("✅ LeadOrchestrator initialized successfully")

        # Test 4: Test agent initialization
        print("\n🔄 Testing agent initialization...")
        from shared.core.agents.retrieval_agent import RetrievalAgent
        from shared.core.agents.factcheck_agent import FactCheckAgent
        from shared.core.agents.synthesis_agent import SynthesisAgent
        from shared.core.agents.citation_agent import CitationAgent

        retrieval_agent = RetrievalAgent()
        print("✅ RetrievalAgent initialized")

        factcheck_agent = FactCheckAgent()
        print("✅ FactCheckAgent initialized")

        synthesis_agent = SynthesisAgent()
        print("✅ SynthesisAgent initialized")

        citation_agent = CitationAgent()
        print("✅ CitationAgent initialized")

        # Test 5: Test a simple query processing
        print("\n🔄 Testing simple query processing...")
        from shared.core.agents.base_agent import QueryContext

        context = QueryContext(query="What is AI?")

        # Test retrieval agent
        try:
            retrieval_task = {
                "query": "What is AI?",
                "search_type": "hybrid",
                "top_k": 5,
            }

            retrieval_result = await retrieval_agent.process_task(
                retrieval_task, context
            )
            print(f"✅ RetrievalAgent processed task successfully")
            print(f"   Success: {retrieval_result.success}")
            print(
                f"   Data keys: {list(retrieval_result.data.keys()) if retrieval_result.data else 'None'}"
            )

        except Exception as e:
            print(f"❌ RetrievalAgent failed: {e}")
            import traceback

            traceback.print_exc()

        print("\n🎉 All tests completed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run the test."""
    print("🚀 Starting AgentResult issue test...")
    print("=" * 50)

    success = await test_agent_result_creation()

    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed.")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
