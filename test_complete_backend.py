import requests
import json
import time

def test_complete_backend():
    """Test the complete backend with real responses and detailed debugging."""
    
    base_url = "http://localhost:8000"
    
    print("🚀 Testing Complete SarvanOM Backend")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n🔍 Test 1: Health Check")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test 2: Direct service health checks
    print("\n🔍 Test 2: Direct Service Health Checks")
    
    # Test retrieval service
    try:
        response = requests.get("http://localhost:8002/health")
        print(f"Retrieval Service: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Retrieval Service Error: {e}")
    
    # Test synthesis service
    try:
        response = requests.get("http://localhost:8003/health")
        print(f"Synthesis Service: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Synthesis Service Error: {e}")
    
    # Test 3: Query with real backend
    print("\n🔍 Test 3: Query with Real Backend")
    try:
        data = {
            "query": "What is artificial intelligence?",
            "max_tokens": 500,
            "confidence_threshold": 0.7
        }
        response = requests.post(f"{base_url}/query", json=data)
        print(f"Query Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Query endpoint working")
            print(f"Success: {result.get('success', False)}")
            print(f"Error: {result.get('error', 'None')}")
            print(f"Confidence: {result.get('confidence', 0)}")
            print(f"Execution Time: {result.get('execution_time_ms', 0)}ms")
            
            if result.get('success'):
                print("🎉 REAL BACKEND RESPONSE RECEIVED!")
                print(f"Answer: {result.get('answer', 'No answer')}")
                print(f"Sources: {result.get('sources', [])}")
            else:
                print("⚠️ Query failed - checking why...")
        else:
            print(f"❌ Query endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Query endpoint error: {e}")
    
    # Test 4: Test different query types
    print("\n🔍 Test 4: Different Query Types")
    
    test_queries = [
        "Explain machine learning in simple terms",
        "What are the benefits of renewable energy?",
        "How does blockchain technology work?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test Query {i}: {query[:50]}...")
        try:
            data = {"query": query}
            response = requests.post(f"{base_url}/query", json=data)
            result = response.json()
            print(f"Status: {response.status_code}")
            print(f"Success: {result.get('success', False)}")
            if result.get('success'):
                print("✅ Real response received!")
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Backend Testing Complete")

if __name__ == "__main__":
    test_complete_backend()
