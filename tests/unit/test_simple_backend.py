#!/usr/bin/env python3
"""
Simple test to check if the backend is working.
"""

import httpx
import asyncio
import pytest


@pytest.mark.asyncio
async def test_backend_simple():
    """Test if the backend is responding at all."""
    print("🧪 Testing backend connectivity...")

    try:
        # Test if server is responding using async HTTP client
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8000/", timeout=5.0)
            print(f"✅ Backend is responding (status: {response.status_code})")
            print(f"   Response: {response.text[:200]}...")
            return response.status_code == 200
    except httpx.ConnectError:
        print("❌ Backend is not responding (connection refused)")
        return False
    except Exception as e:
        print(f"❌ Backend error: {e}")
        return False


async def test_backend_health():
    """Test backend health endpoint."""
    print("🏥 Testing backend health endpoint...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8000/health", timeout=5.0)
            print(f"✅ Health endpoint responding (status: {response.status_code})")
            return response.status_code == 200
    except httpx.ConnectError:
        print("❌ Health endpoint not responding")
        return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False


async def test_backend_metrics():
    """Test backend metrics endpoint."""
    print("📊 Testing backend metrics endpoint...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8000/metrics", timeout=5.0)
            print(f"✅ Metrics endpoint responding (status: {response.status_code})")
            return response.status_code == 200
    except httpx.ConnectError:
        print("❌ Metrics endpoint not responding")
        return False
    except Exception as e:
        print(f"❌ Metrics endpoint error: {e}")
        return False


async def run_all_tests():
    """Run all backend tests."""
    print("🚀 Running comprehensive backend tests...")

    tests = [test_backend_simple(), test_backend_health(), test_backend_metrics()]

    results = await asyncio.gather(*tests, return_exceptions=True)

    passed = sum(1 for result in results if result is True)
    total = len(results)

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    # Run tests using asyncio
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
