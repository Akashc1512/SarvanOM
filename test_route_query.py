#!/usr/bin/env python3
"""
Test script for the route_query function in the API gateway.
This script tests the complete query routing pipeline.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_route_query():
    """Test the route_query function with a sample query."""
    
    try:
        # Import the route_query function
        from services.api_gateway.main import route_query
        
        # Test query
        test_query = "What is Python programming language and what are its main features?"
        
        print("🧪 Testing route_query function...")
        print(f"Query: {test_query}")
        print("-" * 50)
        
        # Call the route_query function
        result = await route_query(test_query)
        
        # Print results
        print("✅ Query routing completed!")
        print(f"Success: {result.get('success', False)}")
        print(f"Processing time: {result.get('processing_time', 0):.3f}s")
        
        if result.get('success'):
            print(f"Classification: {result.get('classification', {})}")
            print(f"Answer: {result.get('answer', '')[:200]}...")
            print(f"Confidence: {result.get('confidence', 0.0):.3f}")
            print(f"Total documents: {result.get('metadata', {}).get('total_documents', 0)}")
            print(f"Verified facts: {result.get('metadata', {}).get('verified_facts', 0)}")
            print(f"Use dynamic selection: {result.get('metadata', {}).get('use_dynamic_selection', False)}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_classification():
    """Test the query classification function."""
    
    try:
        from services.api_gateway.main import _classify_query
        
        test_queries = [
            "How to write a Python function?",
            "What are the latest news about AI?",
            "Explain quantum computing algorithms",
            "What is the weather like today?",
            "How to start a business in 2024?"
        ]
        
        print("\n🧪 Testing query classification...")
        print("-" * 50)
        
        for query in test_queries:
            classification = await _classify_query(query)
            print(f"Query: {query}")
            print(f"Classification: {classification}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Classification test failed: {str(e)}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting route_query function tests...")
    print("=" * 60)
    
    # Test classification
    classification_success = await test_classification()
    
    # Test full routing (only if classification works)
    if classification_success:
        routing_success = await test_route_query()
    else:
        routing_success = False
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"Classification test: {'✅ PASSED' if classification_success else '❌ FAILED'}")
    print(f"Routing test: {'✅ PASSED' if routing_success else '❌ FAILED'}")
    
    if classification_success and routing_success:
        print("\n🎉 All tests passed!")
        return True
    else:
        print("\n💥 Some tests failed!")
        return False

if __name__ == "__main__":
    # Set environment variables for testing
    os.environ.setdefault("USE_DYNAMIC_SELECTION", "true")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    
    # Run the tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 