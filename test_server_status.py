#!/usr/bin/env python3
"""
Test script to check server status and endpoints.
"""

import requests
import json
import time
import sys

def test_server_endpoints():
    """Test all available endpoints."""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Server Endpoints")
    print("=" * 40)
    
    # Test basic connectivity
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Root endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health endpoint: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   Components: {len(health_data.get('components', {}))}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
    
    # Test metrics endpoint
    try:
        response = requests.get(f"{base_url}/metrics", timeout=5)
        print(f"✅ Metrics endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Metrics endpoint failed: {e}")
    
    # Test system diagnostics
    try:
        response = requests.get(f"{base_url}/system/diagnostics", timeout=5)
        print(f"✅ System diagnostics: {response.status_code}")
    except Exception as e:
        print(f"❌ System diagnostics failed: {e}")
    
    # Test comprehensive query endpoint
    try:
        test_query = {
            "query": "What is artificial intelligence?",
            "user_id": "test_user",
            "session_id": "test_session"
        }
        response = requests.post(f"{base_url}/query/comprehensive", 
                               json=test_query, 
                               timeout=10)
        print(f"✅ Comprehensive query: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success', False)}")
    except Exception as e:
        print(f"❌ Comprehensive query failed: {e}")
    
    print("\n" + "=" * 40)
    print("🎯 Server Status Check Complete")

if __name__ == "__main__":
    print("🚀 Starting Server Status Check...")
    time.sleep(2)  # Give server time to start
    test_server_endpoints() 