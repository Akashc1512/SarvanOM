#!/usr/bin/env python3
"""
Simple test to debug server endpoint issues.
"""

import requests
import json
import time

def test_endpoints():
    """Test various endpoints to identify the issue."""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing server endpoints...")
    
    # Test 1: Basic connectivity
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Root endpoint: {response.status_code}")
        if response.status_code != 200:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # Test 2: Health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health endpoint: {response.status_code}")
        if response.status_code != 200:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
    
    # Test 3: Basic health endpoint
    try:
        response = requests.get(f"{base_url}/health/basic", timeout=5)
        print(f"✅ Basic health endpoint: {response.status_code}")
        if response.status_code != 200:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Basic health endpoint failed: {e}")
    
    # Test 4: Docs endpoint
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        print(f"✅ Docs endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Docs endpoint failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting endpoint tests...")
    time.sleep(2)  # Wait for server to be ready
    test_endpoints()
    print("✅ Endpoint tests completed!") 