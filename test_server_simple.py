#!/usr/bin/env python3
"""
Simple server test to verify basic functionality.
"""

import requests
import json

def test_server():
    """Test basic server functionality."""
    base_url = "http://localhost:8000"
    headers = {"Host": "localhost:8000"}
    
    print("🧪 Testing SarvanOM Backend Server")
    print("=" * 50)
    
    # Test 1: Docs endpoint
    try:
        response = requests.get(f"{base_url}/docs", headers=headers, timeout=10)
        print(f"✅ Docs endpoint: {response.status_code} (length: {len(response.text)})")
    except Exception as e:
        print(f"❌ Docs endpoint failed: {e}")
    
    # Test 2: OpenAPI spec
    try:
        response = requests.get(f"{base_url}/openapi.json", headers=headers, timeout=10)
        print(f"✅ OpenAPI spec: {response.status_code} (length: {len(response.text)})")
        if response.status_code == 200:
            try:
                spec = response.json()
                print(f"   - Paths: {len(spec.get('paths', {}))}")
                print(f"   - Info: {spec.get('info', {}).get('title', 'Unknown')}")
            except:
                print("   - Invalid JSON response")
    except Exception as e:
        print(f"❌ OpenAPI spec failed: {e}")
    
    # Test 3: Health endpoint
    try:
        response = requests.get(f"{base_url}/health", headers=headers, timeout=10)
        print(f"✅ Health endpoint: {response.status_code} (length: {len(response.text)})")
        if response.status_code == 200:
            try:
                health = response.json()
                print(f"   - Status: {health.get('status', 'Unknown')}")
            except:
                print("   - Invalid JSON response")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
    
    # Test 4: Enhanced health endpoint
    try:
        response = requests.get(f"{base_url}/health/enhanced", headers=headers, timeout=10)
        print(f"✅ Enhanced health: {response.status_code} (length: {len(response.text)})")
        if response.status_code == 200:
            try:
                health = response.json()
                print(f"   - Status: {health.get('status', 'Unknown')}")
            except:
                print("   - Invalid JSON response")
    except Exception as e:
        print(f"❌ Enhanced health failed: {e}")
    
    # Test 5: Search endpoint
    try:
        response = requests.get(f"{base_url}/search?q=test", headers=headers, timeout=10)
        print(f"✅ Search endpoint: {response.status_code} (length: {len(response.text)})")
    except Exception as e:
        print(f"❌ Search endpoint failed: {e}")
    
    # Test 6: Metrics endpoint
    try:
        response = requests.get(f"{base_url}/metrics/router", headers=headers, timeout=10)
        print(f"✅ Router metrics: {response.status_code} (length: {len(response.text)})")
    except Exception as e:
        print(f"❌ Router metrics failed: {e}")
    
    print("\n🎯 Server Test Complete")

if __name__ == "__main__":
    test_server()
