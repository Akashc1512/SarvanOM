#!/usr/bin/env python3
"""
Simple test of the standardized pipeline core functionality.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test that all core imports work."""
    print("🧪 Testing imports...")

    try:
        from shared.core.agents.standardized_agents import (
            ExtendedAgentType,
            create_agent,
        )

        print("✅ standardized_agents import successful")

        from shared.core.agents.refined_lead_orchestrator import (
            RefinedLeadOrchestrator,
            PipelineConfig,
        )

        print("✅ refined_lead_orchestrator import successful")

        from shared.core.agents.lead_orchestrator import LeadOrchestrator

        print("✅ lead_orchestrator import successful")

        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def test_orchestrator_creation():
    """Test orchestrator creation."""
    print("\n🧪 Testing orchestrator creation...")

    try:
        from shared.core.agents.lead_orchestrator import LeadOrchestrator

        orchestrator = LeadOrchestrator()
        print("✅ LeadOrchestrator created successfully")

        status = orchestrator.get_pipeline_status()
        print(f"✅ Pipeline status: {len(status['enabled_agents'])} agents enabled")

        return True
    except Exception as e:
        print(f"❌ Orchestrator creation error: {e}")
        return False


def test_agent_types():
    """Test agent type enumeration."""
    print("\n🧪 Testing agent types...")

    try:
        from shared.core.agents.standardized_agents import ExtendedAgentType

        agent_types = list(ExtendedAgentType)
        print(f"✅ Found {len(agent_types)} agent types:")
        for agent_type in agent_types:
            print(f"   - {agent_type.value}")

        return True
    except Exception as e:
        print(f"❌ Agent types error: {e}")
        return False


def main():
    """Run all tests."""
    print("🎯 Testing Standardized Multi-Agent Pipeline Core")
    print("=" * 60)

    tests = [test_imports, test_orchestrator_creation, test_agent_types]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All core functionality tests passed!")
        print("\n✅ Standardized Multi-Agent Pipeline is ready for use")
        return 0
    else:
        print("⚠️ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
