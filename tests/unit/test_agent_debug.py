#!/usr/bin/env python3
"""
Simple test script to debug the AgentResult issue
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_agent_result():
    """Test AgentResult creation"""
    try:
        from shared.core.agents.base_agent import AgentResult
        
        # Test basic AgentResult creation
        result = AgentResult(success=True, data={"test": "data"})
        print(f"✅ Basic AgentResult creation successful: {result}")
        
        # Test error AgentResult creation
        error_result = AgentResult(success=False, data={}, error="test error")
        print(f"✅ Error AgentResult creation successful: {error_result}")
        
        return True
    except Exception as e:
        print(f"❌ AgentResult test failed: {e}")
        return False

async def test_agent_initialization():
    """Test agent initialization"""
    try:
        from shared.core.agents.lead_orchestrator import LeadOrchestrator
        
        # Test orchestrator initialization
        orchestrator = LeadOrchestrator()
        print(f"✅ LeadOrchestrator initialization successful")
        
        return True
    except Exception as e:
        print(f"❌ Agent initialization test failed: {e}")
        return False

async def test_simple_query():
    """Test a simple query processing"""
    try:
        from shared.core.agents.lead_orchestrator import LeadOrchestrator
        
        orchestrator = LeadOrchestrator()
        
        # Test simple query
        result = await orchestrator.process_query("What is AI?", {"user_id": "test"})
        print(f"✅ Simple query processing successful: {result.get('success', False)}")
        
        return True
    except Exception as e:
        print(f"❌ Simple query test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🔍 Starting AgentResult debug tests...")
    
    # Test 1: AgentResult creation
    print("\n1. Testing AgentResult creation...")
    test1_result = await test_agent_result()
    
    # Test 2: Agent initialization
    print("\n2. Testing agent initialization...")
    test2_result = await test_agent_initialization()
    
    # Test 3: Simple query processing
    print("\n3. Testing simple query processing...")
    test3_result = await test_simple_query()
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"   AgentResult creation: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"   Agent initialization: {'✅ PASS' if test2_result else '❌ FAIL'}")
    print(f"   Simple query: {'✅ PASS' if test3_result else '❌ FAIL'}")
    
    if all([test1_result, test2_result, test3_result]):
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")

if __name__ == "__main__":
    asyncio.run(main()) 