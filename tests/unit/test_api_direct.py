#!/usr/bin/env python3
"""
Test script to test the API directly and isolate the AgentResult error.
"""

import os
import sys
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, '.')

async def test_api_direct():
    """Test the API directly to isolate the AgentResult error."""
    try:
        from shared.core.agents.lead_orchestrator import LeadOrchestrator
        from shared.core.agents.base_agent import QueryContext
        
        print("🔄 Testing API directly...")
        
        # Initialize orchestrator
        orchestrator = LeadOrchestrator()
        print("✅ LeadOrchestrator initialized")
        
        # Test the process_query method directly
        try:
            print("\n🔄 Testing process_query method...")
            result = await orchestrator.process_query("What is artificial intelligence?")
            print("✅ process_query executed successfully")
            print(f"   Result keys: {list(result.keys()) if result else 'None'}")
            print(f"   Success: {result.get('success', 'N/A')}")
            print(f"   Answer length: {len(result.get('answer', ''))}")
            
        except Exception as e:
            print(f"❌ process_query failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n🎉 All tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the test."""
    print("🚀 Starting API direct test...")
    print("=" * 50)
    
    success = await test_api_direct()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed.")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main())) 