#!/usr/bin/env python3
"""
Simple test to isolate the orchestrator issue
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_orchestrator_direct():
    """Test orchestrator directly"""
    try:
        from shared.core.agents.lead_orchestrator import LeadOrchestrator
        
        # Create orchestrator
        orchestrator = LeadOrchestrator()
        
        # Test simple query
        result = await orchestrator.process_query("What is AI?", {"user_id": "test"})
        
        print(f"✅ Orchestrator test successful: {result.get('success', False)}")
        print(f"   Answer: {result.get('answer', '')[:100]}...")
        print(f"   Error: {result.get('error', 'None')}")
        
        return True
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the test"""
    print("🔍 Testing orchestrator directly...")
    
    result = await test_orchestrator_direct()
    
    if result:
        print("\n🎉 Orchestrator test passed!")
    else:
        print("\n⚠️  Orchestrator test failed!")

if __name__ == "__main__":
    asyncio.run(main()) 