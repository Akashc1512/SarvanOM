import requests
import time

def test_api_gateway():
    """Test the API Gateway directly."""
    
    print("🔍 Testing API Gateway")
    print("=" * 30)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"Health Status: {response.status_code}")
        print(f"Health Response: {response.json()}")
    except Exception as e:
        print(f"Health Error: {e}")
    
    # Test 2: Query endpoint
    print("\n2. Testing query endpoint...")
    try:
        data = {
            "query": "What is AI?",
            "max_tokens": 100,
            "confidence_threshold": 0.7
        }
        print(f"Sending request: {data}")
        
        start_time = time.time()
        response = requests.post("http://localhost:8000/query", json=data, timeout=30)
        end_time = time.time()
        
        print(f"Query Status: {response.status_code}")
        print(f"Response Time: {(end_time - start_time)*1000:.2f}ms")
        print(f"Query Response: {response.json()}")
        
    except Exception as e:
        print(f"Query Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_gateway()
