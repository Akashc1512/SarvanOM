#!/usr/bin/env python3
"""
Detailed backend test to see error details
"""
import asyncio
import httpx
import json

async def test_backend_detailed():
    """Test backend with detailed error reporting."""
    try:
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            response = await client.get('http://127.0.0.1:8000/health', timeout=5.0)
            print(f"Health endpoint - Status: {response.status_code}")
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    print(f"Error details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Error text: {response.text}")
            
            # Test root endpoint
            response = await client.get('http://127.0.0.1:8000/', timeout=5.0)
            print(f"Root endpoint - Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                except:
                    print(f"Response text: {response.text}")
            
            # Test test endpoint
            response = await client.get('http://127.0.0.1:8000/test', timeout=5.0)
            print(f"Test endpoint - Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                except:
                    print(f"Response text: {response.text}")
                    
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_backend_detailed()) 