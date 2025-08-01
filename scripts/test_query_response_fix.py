#!/usr/bin/env python3
"""
Test QueryResponse Fix Script
Validates that the QueryResponse model is working correctly with all required fields.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import the models
from shared.core.api.api_models import QueryResponse

def test_query_response_creation():
    """Test creating a QueryResponse with all required fields."""
    try:
        # Test 1: Create QueryResponse with all required fields
        response = QueryResponse(
            query_id="test_123",
            status="completed",
            answer="This is a test answer",
            confidence=0.85,
            sources=["source1", "source2"],
            processing_time=1.5,
            timestamp=datetime.now().isoformat(),
            tokens_used=150,
            cost=0.02,
            metadata={"test": True}
        )
        
        print("✅ QueryResponse creation successful")
        print(f"  Query ID: {response.query_id}")
        print(f"  Status: {response.status}")
        print(f"  Answer: {response.answer}")
        print(f"  Confidence: {response.confidence}")
        print(f"  Sources: {response.sources}")
        print(f"  Processing Time: {response.processing_time}")
        print(f"  Timestamp: {response.timestamp}")
        
        return True
        
    except Exception as e:
        print(f"❌ QueryResponse creation failed: {e}")
        return False

def test_query_response_serialization():
    """Test serializing QueryResponse to JSON."""
    try:
        response = QueryResponse(
            query_id="test_456",
            status="completed",
            answer="Serialization test answer",
            confidence=0.9,
            sources=["test_source"],
            processing_time=2.0,
            timestamp=datetime.now().isoformat(),
            tokens_used=200,
            cost=0.03,
            metadata={"serialization_test": True}
        )
        
        # Convert to dict
        response_dict = response.dict()
        print("✅ QueryResponse serialization successful")
        print(f"  Serialized keys: {list(response_dict.keys())}")
        
        # Convert to JSON
        response_json = response.json()
        print("✅ QueryResponse JSON conversion successful")
        
        return True
        
    except Exception as e:
        print(f"❌ QueryResponse serialization failed: {e}")
        return False

def test_query_response_validation():
    """Test QueryResponse validation with missing fields."""
    try:
        # This should fail
        response = QueryResponse(
            query_id="test_789",
            # Missing status
            answer="Test answer",
            confidence=0.8,
            # Missing sources
            processing_time=1.0,
            # Missing timestamp
        )
        print("❌ QueryResponse validation should have failed")
        return False
        
    except Exception as e:
        print("✅ QueryResponse validation working correctly")
        print(f"  Expected error: {e}")
        return True

def main():
    """Run all tests."""
    print("🧪 Testing QueryResponse Fixes")
    print("=" * 50)
    
    tests = [
        ("QueryResponse Creation", test_query_response_creation),
        ("QueryResponse Serialization", test_query_response_serialization),
        ("QueryResponse Validation", test_query_response_validation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! QueryResponse fix is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 