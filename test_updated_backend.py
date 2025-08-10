#!/usr/bin/env python3
"""
Test script to verify the backend is working with all updated dependencies
"""

import requests
import json
import time

BASE_URL = "http://localhost:8002"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_system_status():
    """Test system status endpoint"""
    print("\n🔍 Testing System Status...")
    try:
        response = requests.get(f"{BASE_URL}/system/status", timeout=10)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Cache Status: {data['system_status']['cache']['redis_connected']}")
        print(f"HuggingFace Status: {data['system_status']['huggingface']['auth_status']['authenticated']}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_huggingface_models():
    """Test HuggingFace models endpoint"""
    print("\n🔍 Testing HuggingFace Models...")
    try:
        response = requests.get(f"{BASE_URL}/huggingface/models", timeout=10)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Available Models: {len(data['models']['text_generation'])} text generation models")
        print(f"Device: {data['device']}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_search_endpoint():
    """Test search endpoint with real LLM"""
    print("\n🔍 Testing Search Endpoint...")
    try:
        payload = {
            "query": "What is the birthplace of the current Prime Minister of India?",
            "user_id": "test_user",
            "session_id": "test_session"
        }
        response = requests.post(f"{BASE_URL}/search", json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Answer: {data.get('answer', 'No answer found')[:200]}...")
            print(f"Sources: {len(data.get('sources', []))} sources")
        else:
            print(f"Error Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_fact_check():
    """Test fact check endpoint"""
    print("\n🔍 Testing Fact Check Endpoint...")
    try:
        payload = {
            "content": "The current Prime Minister of India was born in Vadnagar, Gujarat",
            "context": "Information about Indian Prime Minister's birthplace",
            "user_id": "test_user"
        }
        response = requests.post(f"{BASE_URL}/fact-check", json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Verification: {data.get('verification', 'No verification found')}")
        else:
            print(f"Error Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_cache_stats():
    """Test cache statistics"""
    print("\n🔍 Testing Cache Statistics...")
    try:
        response = requests.get(f"{BASE_URL}/cache/stats", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Cache Hits: {data.get('hits', 0)}")
            print(f"Cache Misses: {data.get('misses', 0)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_huggingface_generate():
    """Test HuggingFace text generation"""
    print("\n🔍 Testing HuggingFace Text Generation...")
    try:
        # Use query parameters instead of JSON body
        params = {
            "prompt": "The capital of India is",
            "max_length": 50,
            "temperature": 0.7
        }
        response = requests.post(f"{BASE_URL}/huggingface/generate", params=params, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Generated Text: {data.get('generated_text', 'No text generated')}")
        else:
            print(f"Error Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Updated Backend with Latest Dependencies")
    print("=" * 60)
    
    tests = [
        test_health,
        test_system_status,
        test_huggingface_models,
        test_cache_stats,
        test_huggingface_generate,
        test_search_endpoint,
        test_fact_check
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            time.sleep(1)  # Brief pause between tests
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! Backend is working correctly with updated dependencies.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
