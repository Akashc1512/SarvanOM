import requests
import json

def test_query_endpoint():
    """Test the query endpoint to identify security middleware issues."""
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health check
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test 2: Simple query
    print("\n🔍 Testing simple query...")
    try:
        data = {"query": "What is the weather today?"}
        response = requests.post(f"{base_url}/query", json=data)
        print(f"Query Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Query endpoint working")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Query endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Query endpoint error: {e}")
    
    # Test 3: Query with different content
    print("\n🔍 Testing query with different content...")
    try:
        data = {"query": "Tell me about Python programming"}
        response = requests.post(f"{base_url}/query", json=data)
        print(f"Query Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Query endpoint working")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Query endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Query endpoint error: {e}")
    
    # Test 4: Check if server is responding
    print("\n🔍 Testing server availability...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Root Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    test_query_endpoint()
