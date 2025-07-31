#!/usr/bin/env python3
"""
Test script to test the orchestrator pipeline specifically.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, '.')

async def test_orchestrator_pipeline():
    """Test the orchestrator pipeline to find the AgentResult issue."""
    try:
        from shared.core.agents.lead_orchestrator import LeadOrchestrator
from shared.core.agents.base_agent import QueryContext
        
        print("🔄 Testing orchestrator pipeline...")
        
        # Initialize orchestrator
        orchestrator = LeadOrchestrator()
        print("✅ LeadOrchestrator initialized")
        
        # Create context
        context = QueryContext(query="What is artificial intelligence?")
        print("✅ QueryContext created")
        
        # Test the full pipeline
        try:
            print("\n🔄 Testing full pipeline execution...")
            result = await orchestrator.process_query("What is artificial intelligence?")
            print("✅ Pipeline executed successfully")
            print(f"   Result keys: {list(result.keys()) if result else 'None'}")
            
        except Exception as e:
            print(f"❌ Pipeline failed: {e}")
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
    print("🚀 Starting orchestrator pipeline test...")
    print("=" * 50)
    
    success = await test_orchestrator_pipeline()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed.")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main())) 