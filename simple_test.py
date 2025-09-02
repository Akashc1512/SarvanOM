#!/usr/bin/env python3
"""
Simple test to check basic functionality
"""

def test_basic():
    print("🧪 Testing basic functionality...")
    
    # Test 1: Basic Python
    try:
        print("✅ Basic Python working")
    except Exception as e:
        print(f"❌ Basic Python failed: {e}")
        return False
    
    # Test 2: Check if we can import basic modules
    try:
        import os
        import sys
        print("✅ Basic imports working")
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return False
    
    # Test 3: Check environment
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        print(f"OpenAI API Key: {'✅ Set' if openai_key else '❌ Not set'}")
        print(f"Anthropic API Key: {'✅ Set' if anthropic_key else '❌ Not set'}")
    except Exception as e:
        print(f"❌ Environment check failed: {e}")
    
    # Test 4: Check if we can access the services directory
    try:
        import os
        if os.path.exists("services"):
            print("✅ Services directory accessible")
            services = os.listdir("services")
            print(f"   Available services: {services}")
        else:
            print("❌ Services directory not found")
    except Exception as e:
        print(f"❌ Services check failed: {e}")
    
    return True

if __name__ == "__main__":
    success = test_basic()
    if success:
        print("🎉 Basic functionality test passed!")
    else:
        print("⚠️  Basic functionality test failed!")
