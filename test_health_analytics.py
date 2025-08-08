#!/usr/bin/env python3
"""
Test script for health endpoints and analytics tracking
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any

async def test_health_endpoints():
    """Test the health endpoints."""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        print("🔍 Testing Health Endpoints...")
        
        # Test basic health endpoint
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Basic health endpoint:", data.get("status"))
                    print(f"   Response time: {data.get('response_time_ms', 0)}ms")
                    print(f"   Overall healthy: {data.get('overall_healthy', False)}")
                else:
                    print(f"❌ Basic health endpoint failed: {response.status}")
        except Exception as e:
            print(f"❌ Basic health endpoint error: {e}")
        
        # Test detailed health endpoint
        try:
            async with session.get(f"{base_url}/health/detailed") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Detailed health endpoint:", data.get("status"))
                    print(f"   Services: {len(data.get('services', {}).get('external', {}))} external, {len(data.get('services', {}).get('agents', {}))} agents")
                    print(f"   Performance: {data.get('performance', {})}")
                    print(f"   Recommendations: {len(data.get('recommendations', []))}")
                else:
                    print(f"❌ Detailed health endpoint failed: {response.status}")
        except Exception as e:
            print(f"❌ Detailed health endpoint error: {e}")

async def test_analytics_endpoints():
    """Test the analytics endpoints."""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        print("\n📊 Testing Analytics Endpoints...")
        
        # Test analytics endpoint
        try:
            async with session.get(f"{base_url}/analytics") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Analytics endpoint:", data.get("platform_status"))
                    print(f"   Data sources: {len(data.get('data_sources', {}))}")
                else:
                    print(f"❌ Analytics endpoint failed: {response.status}")
        except Exception as e:
            print(f"❌ Analytics endpoint error: {e}")
        
        # Test analytics summary endpoint
        try:
            async with session.get(f"{base_url}/analytics/summary?time_range=7d") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Analytics summary endpoint:", data.get("time_range"))
                    print(f"   Total queries: {data.get('total_queries', 0)}")
                    print(f"   Success rate: {data.get('success_rate', 0)}")
                else:
                    print(f"❌ Analytics summary endpoint failed: {response.status}")
        except Exception as e:
            print(f"❌ Analytics summary endpoint error: {e}")

async def test_service_endpoints_with_analytics():
    """Test service endpoints to trigger analytics tracking."""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        print("\n🚀 Testing Service Endpoints with Analytics...")
        
        # Test search endpoint
        try:
            search_data = {
                "query": "test query for analytics",
                "user_id": "test_user_123"
            }
            async with session.post(f"{base_url}/search", json=search_data) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Search endpoint with analytics:", data.get("message"))
                    print(f"   Processing time: {data.get('processing_time_ms', 0)}ms")
                else:
                    print(f"❌ Search endpoint failed: {response.status}")
        except Exception as e:
            print(f"❌ Search endpoint error: {e}")
        
        # Test fact-check endpoint
        try:
            fact_check_data = {
                "content": "This is a test claim for fact-checking analytics",
                "user_id": "test_user_123"
            }
            async with session.post(f"{base_url}/fact-check", json=fact_check_data) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Fact-check endpoint with analytics:", data.get("status"))
                    print(f"   Processing time: {data.get('processing_time_ms', 0)}ms")
                else:
                    print(f"❌ Fact-check endpoint failed: {response.status}")
        except Exception as e:
            print(f"❌ Fact-check endpoint error: {e}")
        
        # Test synthesis endpoint
        try:
            synthesis_data = {
                "query": "test synthesis query",
                "user_id": "test_user_123",
                "sources": ["source1.com", "source2.org"]
            }
            async with session.post(f"{base_url}/synthesize", json=synthesis_data) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Synthesis endpoint with analytics:", data.get("message"))
                    print(f"   Processing time: {data.get('processing_time_ms', 0)}ms")
                else:
                    print(f"❌ Synthesis endpoint failed: {response.status}")
        except Exception as e:
            print(f"❌ Synthesis endpoint error: {e}")

async def main():
    """Run all tests."""
    print("🧪 Starting Health and Analytics Tests...")
    print("=" * 50)
    
    await test_health_endpoints()
    await test_analytics_endpoints()
    await test_service_endpoints_with_analytics()
    
    print("\n" + "=" * 50)
    print("✅ Health and Analytics Tests Completed!")

if __name__ == "__main__":
    asyncio.run(main()) 