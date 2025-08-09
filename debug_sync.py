import requests
import time


def debug_connection_sync():
    """Debug the connection between API Gateway and retrieval service using sync requests."""

    print("🔍 Debugging API Gateway to Retrieval Service Connection (Sync)")
    print("=" * 60)

    # Test 1: Direct retrieval service call
    print("\n1. Testing direct retrieval service call...")
    try:
        retrieval_url = "http://localhost:8002/search"
        retrieval_payload = {
            "query": "What is AI?",
            "max_results": 5,
            "context": {"user_id": "test"},
        }

        print(f"Calling: {retrieval_url}")
        print(f"Payload: {retrieval_payload}")

        start_time = time.time()
        response = requests.post(retrieval_url, json=retrieval_payload, timeout=30)
        end_time = time.time()

        print(f"Status: {response.status_code}")
        print(f"Response time: {(end_time - start_time)*1000:.2f}ms")
        print(f"Response: {response.json()}")

    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")

    # Test 2: Test synthesis service
    print("\n2. Testing synthesis service...")
    try:
        synthesis_url = "http://localhost:8003/synthesize"
        synthesis_payload = {
            "query": "What is AI?",
            "sources": [],
            "max_tokens": 100,
            "context": {"user_id": "test"},
        }

        print(f"Calling: {synthesis_url}")
        print(f"Payload: {synthesis_payload}")

        start_time = time.time()
        response = requests.post(synthesis_url, json=synthesis_payload, timeout=30)
        end_time = time.time()

        print(f"Status: {response.status_code}")
        print(f"Response time: {(end_time - start_time)*1000:.2f}ms")
        print(f"Response: {response.json()}")

    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")

    # Test 3: Test API Gateway query endpoint
    print("\n3. Testing API Gateway query endpoint...")
    try:
        gateway_url = "http://localhost:8000/query"
        gateway_payload = {
            "query": "What is AI?",
            "max_tokens": 100,
            "confidence_threshold": 0.7,
        }

        print(f"Calling: {gateway_url}")
        print(f"Payload: {gateway_payload}")

        start_time = time.time()
        response = requests.post(gateway_url, json=gateway_payload, timeout=30)
        end_time = time.time()

        print(f"Status: {response.status_code}")
        print(f"Response time: {(end_time - start_time)*1000:.2f}ms")
        print(f"Response: {response.json()}")

    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")

    print("\n" + "=" * 60)
    print("🏁 Connection Debug Complete")


if __name__ == "__main__":
    debug_connection_sync()
