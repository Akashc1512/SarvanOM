#!/usr/bin/env python3
"""
Simple backend status test
"""
import asyncio
import httpx
import sys

async def test_backend():
    """Test if backend is running."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get('http://127.0.0.1:8000/health', timeout=5.0)
            print(f"✅ Backend is running - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {data}")
            return True
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_backend())
    sys.exit(0 if success else 1) 