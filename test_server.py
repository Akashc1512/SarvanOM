#!/usr/bin/env python3
"""
Test script to check if the server is running
"""

import asyncio
import httpx

async def test_server():
    """Test if the server is responding."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get('http://localhost:8000/health', timeout=5.0)
            print(f"✅ Server responding: {response.status_code}")
            return True
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_server()) 