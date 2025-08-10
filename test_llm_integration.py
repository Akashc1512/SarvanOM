#!/usr/bin/env python3
"""
Test script for backend LLM integration
"""

import requests
import json
import time

def test_backend_llm_integration():
    """Test the backend with real LLM integration"""
    
    base_url = "http://localhost:8001"
    
    print("🚀 Testing Backend with Real LLM Integration")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health Check: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return
    
    # Test 2: Root endpoint
    print("\n2. Testing Root Endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root Endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Root Endpoint Failed: {e}")
    
    # Test 3: Search with LLM
    print("\n3. Testing Search with Real LLM...")
    search_data = {
        "query": "What is artificial intelligence?",
        "user_id": "test_user_123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/search",
            json=search_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Search Request: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Search Request Failed: {e}")
    
    # Test 4: Fact Check with LLM
    print("\n4. Testing Fact Check with Real LLM...")
    fact_check_data = {
        "content": "The Earth is flat and the moon landing was fake.",
        "user_id": "test_user_123",
        "context": "Testing fact checking capabilities"
    }
    
    try:
        response = requests.post(
            f"{base_url}/fact-check",
            json=fact_check_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Fact Check Request: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Fact Check Request Failed: {e}")
    
    # Test 5: Synthesis with LLM
    print("\n5. Testing Synthesis with Real LLM...")
    synthesis_data = {
        "query": "Explain quantum computing in simple terms",
        "user_id": "test_user_123",
        "sources": ["https://example.com/quantum-computing"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/synthesize",
            json=synthesis_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Synthesis Request: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Synthesis Request Failed: {e}")
    
    # Test 6: Vector Search
    print("\n6. Testing Vector Search...")
    vector_data = {
        "query": "machine learning algorithms",
        "limit": 5,
        "user_id": "test_user_123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/vector/search",
            json=vector_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Vector Search Request: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Vector Search Request Failed: {e}")
    
    # Test 7: Analytics
    print("\n7. Testing Analytics...")
    try:
        response = requests.get(f"{base_url}/analytics")
        print(f"✅ Analytics Request: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Analytics Request Failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Backend LLM Integration Test Complete!")

if __name__ == "__main__":
    test_backend_llm_integration()
