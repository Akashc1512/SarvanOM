import httpx
import asyncio
import time

async def debug_connection():
    """Debug the connection between API Gateway and retrieval service."""
    
    print("🔍 Debugging API Gateway to Retrieval Service Connection")
    print("=" * 60)
    
    # Test 1: Direct retrieval service call
    print("\n1. Testing direct retrieval service call...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            retrieval_url = "http://localhost:8002/search"
            retrieval_payload = {
                "query": "What is AI?",
                "max_results": 5,
                "context": {"user_id": "test"}
            }
            
            print(f"Calling: {retrieval_url}")
            print(f"Payload: {retrieval_payload}")
            
            start_time = time.time()
            response = await client.post(retrieval_url, json=retrieval_payload)
            end_time = time.time()
            
            print(f"Status: {response.status_code}")
            print(f"Response time: {(end_time - start_time)*1000:.2f}ms")
            print(f"Response: {response.json()}")
            
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
    
    # Test 2: Test with shorter timeout
    print("\n2. Testing with shorter timeout (5 seconds)...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            retrieval_url = "http://localhost:8002/search"
            retrieval_payload = {
                "query": "What is AI?",
                "max_results": 5,
                "context": {"user_id": "test"}
            }
            
            start_time = time.time()
            response = await client.post(retrieval_url, json=retrieval_payload)
            end_time = time.time()
            
            print(f"Status: {response.status_code}")
            print(f"Response time: {(end_time - start_time)*1000:.2f}ms")
            print(f"Response: {response.json()}")
            
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
    
    # Test 3: Test synthesis service
    print("\n3. Testing synthesis service...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            synthesis_url = "http://localhost:8003/synthesize"
            synthesis_payload = {
                "query": "What is AI?",
                "sources": [],
                "max_tokens": 100,
                "context": {"user_id": "test"}
            }
            
            print(f"Calling: {synthesis_url}")
            print(f"Payload: {synthesis_payload}")
            
            start_time = time.time()
            response = await client.post(synthesis_url, json=synthesis_payload)
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
    asyncio.run(debug_connection())
