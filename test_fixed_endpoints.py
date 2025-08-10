#!/usr/bin/env python3
"""
Test script to verify fixed endpoints
"""

import requests
import json

def test_fixed_endpoints():
    base_url = "http://localhost:8001"
    
    print("🧪 Testing Fixed Endpoints")
    print("=" * 50)
    
    # Test 1: Background Task (should work now)
    print("\n1. Testing Background Task...")
    try:
        response = requests.post(
            f"{base_url}/background/task",
            params={
                "task_type": "search",
                "query": "What is quantum computing?",
                "user_id": "test_user_123",
                "priority": "normal"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Background task submitted: {result['task_id']}")
        else:
            print(f"❌ Background task failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Background task error: {e}")
    
    # Test 2: Search endpoint
    print("\n2. Testing Search Endpoint...")
    try:
        response = requests.post(
            f"{base_url}/search",
            json={
                "query": "What is quantum computing?",
                "user_id": "test_user_123"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Search successful: {len(result.get('results', []))} results")
        else:
            print(f"❌ Search failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Search error: {e}")
    
    # Test 3: Fact-check endpoint
    print("\n3. Testing Fact-check Endpoint...")
    try:
        response = requests.post(
            f"{base_url}/fact-check",
            json={
                "content": "Quantum computing can solve all problems instantly",
                "user_id": "test_user_123"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Fact-check successful: {result.get('verdict', 'Unknown')}")
        else:
            print(f"❌ Fact-check failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Fact-check error: {e}")
    
    # Test 4: Prompt Optimization
    print("\n4. Testing Prompt Optimization...")
    try:
        response = requests.post(
            f"{base_url}/optimize/prompt",
            params={
                "prompt": "Please provide a comprehensive analysis of quantum computing",
                "prompt_type": "analysis",
                "complexity": "expert"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Prompt optimization successful")
            print(f"   Original: {len(result['optimized_prompt']['original_prompt'])} chars")
            print(f"   Optimized: {len(result['optimized_prompt']['optimized_prompt'])} chars")
        else:
            print(f"❌ Prompt optimization failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Prompt optimization error: {e}")
    
    # Test 5: Cache Stats
    print("\n5. Testing Cache Stats...")
    try:
        response = requests.get(f"{base_url}/cache/stats")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Cache stats: {result['cache_stats']['hit_rate']}% hit rate")
            print(f"   Redis connected: {result['cache_stats']['redis_connected']}")
        else:
            print(f"❌ Cache stats failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Cache stats error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Fixed Endpoints Test Complete!")

if __name__ == "__main__":
    test_fixed_endpoints()
