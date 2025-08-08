#!/usr/bin/env python3
"""
Simple test script to verify utilities work correctly.
"""

import time
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_timing_utilities():
    """Test timing utilities."""
    print("🔍 Testing timing utilities...")
    
    try:
        from shared.core.utilities.timing_utilities import start_timer, calculate_execution_time
        
        # Test basic timing
        start = start_timer()
        time.sleep(0.1)  # Simulate work
        exec_time = calculate_execution_time(start)
        
        print(f"✅ Timing utilities work correctly")
        print(f"   Execution time: {exec_time}ms")
        
        return True
    except Exception as e:
        print(f"❌ Timing utilities failed: {e}")
        return False

def test_response_utilities():
    """Test response utilities."""
    print("🔍 Testing response utilities...")
    
    try:
        from shared.core.utilities.response_utilities import create_success_response, create_error_response, add_execution_time
        
        # Test success response
        success_response = create_success_response(
            data={"test": "data"},
            confidence=0.9,
            execution_time_ms=100
        )
        
        # Test error response
        error_response = create_error_response(
            error="Test error",
            execution_time_ms=50
        )
        
        # Test adding execution time
        start = time.time()
        time.sleep(0.05)
        response_with_time = add_execution_time(success_response, start)
        
        print(f"✅ Response utilities work correctly")
        print(f"   Success response: {success_response}")
        print(f"   Error response: {error_response}")
        print(f"   Response with time: {response_with_time}")
        
        return True
    except Exception as e:
        print(f"❌ Response utilities failed: {e}")
        return False

def test_validation_utilities():
    """Test validation utilities."""
    print("🔍 Testing validation utilities...")
    
    try:
        from shared.core.utilities.validation_utilities import validate_string, validate_required_fields
        
        # Test string validation
        string_result = validate_string("test", "test_field", max_length=10)
        
        # Test required fields validation
        fields_result = validate_required_fields(
            {"field1": "value1", "field2": "value2"},
            ["field1", "field2"]
        )
        
        print(f"✅ Validation utilities work correctly")
        print(f"   String validation: {string_result}")
        print(f"   Fields validation: {fields_result}")
        
        return True
    except Exception as e:
        print(f"❌ Validation utilities failed: {e}")
        return False

def main():
    """Run all utility tests."""
    print("🎯 Testing Shared Utilities")
    print("=" * 50)
    
    tests = [
        test_timing_utilities,
        test_response_utilities,
        test_validation_utilities
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("📊 Test Results:")
    print(f"   Passed: {passed}/{total}")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("✅ All utilities working correctly!")
        return True
    else:
        print("❌ Some utilities have issues")
        return False

if __name__ == "__main__":
    main() 