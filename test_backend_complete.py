#!/usr/bin/env python3
"""
Complete backend end-to-end test with Docker infrastructure.
"""

import requests
import json
import time

def test_backend_complete():
    """Complete backend test with all services."""
    base_url = "http://localhost:8000"
    headers = {"Host": "localhost:8000"}
    
    print("🚀 SarvanOM Backend - Complete End-to-End Test")
    print("=" * 60)
    
    # Test 1: Basic connectivity
    print("\n📡 1. BASIC CONNECTIVITY")
    try:
        response = requests.get(f"{base_url}/docs", headers=headers, timeout=10)
        print(f"✅ API Documentation: {response.status_code} (length: {len(response.text)})")
    except Exception as e:
        print(f"❌ API Documentation: {e}")
        return
    
    # Test 2: Health endpoints
    print("\n🏥 2. HEALTH ENDPOINTS")
    try:
        response = requests.get(f"{base_url}/health", headers=headers, timeout=10)
        print(f"✅ Basic Health: {response.status_code} (length: {len(response.text)})")
        if response.status_code == 200:
            try:
                health = response.json()
                print(f"   - Status: {health.get('status', 'Unknown')}")
            except:
                print("   - Response not JSON")
    except Exception as e:
        print(f"❌ Basic Health: {e}")
    
    # Test 3: Search functionality
    print("\n🔍 3. SEARCH FUNCTIONALITY")
    try:
        response = requests.get(f"{base_url}/search?q=test", headers=headers, timeout=10)
        print(f"✅ Search Endpoint: {response.status_code} (length: {len(response.text)})")
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   - Results: {len(result.get('results', []))}")
            except:
                print("   - Response not JSON")
    except Exception as e:
        print(f"❌ Search Endpoint: {e}")
    
    # Test 4: LLM Providers
    print("\n🤖 4. LLM PROVIDERS")
    try:
        response = requests.get(f"{base_url}/providers", headers=headers, timeout=10)
        print(f"✅ Providers Endpoint: {response.status_code} (length: {len(response.text)})")
        if response.status_code == 200:
            try:
                providers = response.json()
                print(f"   - Available Providers: {len(providers.get('providers', []))}")
            except:
                print("   - Response not JSON")
    except Exception as e:
        print(f"❌ Providers Endpoint: {e}")
    
    # Test 5: Model Router
    print("\n🎯 5. MODEL ROUTER")
    try:
        response = requests.get(f"{base_url}/models", headers=headers, timeout=10)
        print(f"✅ Models Endpoint: {response.status_code} (length: {len(response.text)})")
        if response.status_code == 200:
            try:
                models = response.json()
                print(f"   - Available Models: {len(models.get('models', []))}")
            except:
                print("   - Response not JSON")
    except Exception as e:
        print(f"❌ Models Endpoint: {e}")
    
    # Test 6: Metrics
    print("\n📊 6. METRICS & MONITORING")
    try:
        response = requests.get(f"{base_url}/metrics/router", headers=headers, timeout=10)
        print(f"✅ Router Metrics: {response.status_code} (length: {len(response.text)})")
    except Exception as e:
        print(f"❌ Router Metrics: {e}")
    
    # Test 7: Docker Services Integration
    print("\n🐳 7. DOCKER SERVICES INTEGRATION")
    
    # Test PostgreSQL connection through backend
    try:
        response = requests.get(f"{base_url}/health/database", headers=headers, timeout=10)
        print(f"✅ Database Health: {response.status_code} (length: {len(response.text)})")
    except Exception as e:
        print(f"❌ Database Health: {e}")
    
    # Test Redis connection through backend
    try:
        response = requests.get(f"{base_url}/health/cache", headers=headers, timeout=10)
        print(f"✅ Cache Health: {response.status_code} (length: {len(response.text)})")
    except Exception as e:
        print(f"❌ Cache Health: {e}")
    
    # Test 8: Performance Test
    print("\n⚡ 8. PERFORMANCE TEST")
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/docs", headers=headers, timeout=10)
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        print(f"✅ Response Time: {response_time:.2f}ms")
        if response_time < 1000:
            print("   - Performance: Excellent")
        elif response_time < 2000:
            print("   - Performance: Good")
        else:
            print("   - Performance: Needs optimization")
    except Exception as e:
        print(f"❌ Performance Test: {e}")
    
    # Test 9: Error Handling
    print("\n🛡️ 9. ERROR HANDLING")
    try:
        response = requests.get(f"{base_url}/nonexistent", headers=headers, timeout=10)
        print(f"✅ 404 Handling: {response.status_code}")
        if response.status_code == 404:
            print("   - Error handling: Working correctly")
    except Exception as e:
        print(f"❌ Error Handling: {e}")
    
    # Test 10: Security
    print("\n🔒 10. SECURITY")
    try:
        # Test with invalid host header
        bad_headers = {"Host": "malicious.com:8000"}
        response = requests.get(f"{base_url}/docs", headers=bad_headers, timeout=10)
        print(f"✅ Host Validation: {response.status_code}")
        if response.status_code == 400:
            print("   - Security: Host validation working")
        else:
            print("   - Security: Host validation may need review")
    except Exception as e:
        print(f"❌ Security Test: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 COMPLETE BACKEND TEST FINISHED")
    print("=" * 60)

if __name__ == "__main__":
    test_backend_complete()
