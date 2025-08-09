#!/usr/bin/env python3
"""
Test script for Universal Knowledge Hub Backend
"""

import asyncio
import httpx
import json
import time

BASE_URL = "http://127.0.0.1:8000"


async def test_endpoint(client, endpoint, method="GET", data=None):
    """Test an endpoint and return the response."""
    url = f"{BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = await client.get(url)
        elif method == "POST":
            headers = {"Content-Type": "application/json"}
            response = await client.post(url, json=data, headers=headers)

        print(f"✅ {method} {endpoint} - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {e}")
        return False


async def main():
    """Test all endpoints."""
    print("🧪 Testing Universal Knowledge Hub Backend")
    print("=" * 50)

    async with httpx.AsyncClient() as client:
        # Test GET endpoints
        await test_endpoint(client, "/")
        await test_endpoint(client, "/health")
        await test_endpoint(client, "/test")
        await test_endpoint(client, "/metrics")

        # Test POST endpoints
        query_data = {
            "query": "What is Python 3.13.5?",
            "max_tokens": 1000,
            "confidence_threshold": 0.8,
        }
        await test_endpoint(client, "/query", "POST", query_data)

        auth_data = {"username": "admin", "password": "password"}
        await test_endpoint(client, "/auth/login", "POST", auth_data)

    print("\n" + "=" * 50)
    print("🎉 Backend testing completed!")
    print(f"🌐 API Documentation: {BASE_URL}/docs")
    print(f"📋 OpenAPI Schema: {BASE_URL}/openapi.json")


if __name__ == "__main__":
    asyncio.run(main())
