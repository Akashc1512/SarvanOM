#!/usr/bin/env python3
"""
Service Health Check Script

This script checks the health of all backend services and reports their status.
"""

import asyncio
import aiohttp
import time
from typing import Dict, Any

async def check_service_health(service_name: str, url: str, timeout: float = 5.0) -> Dict[str, Any]:
    """Check health of a specific service."""
    start_time = time.time()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                response_time = time.time() - start_time
                return {
                    "service": service_name,
                    "url": url,
                    "status": "healthy" if response.status == 200 else "unhealthy",
                    "response_time": response_time,
                    "status_code": response.status,
                    "error": None
                }
    except Exception as e:
        response_time = time.time() - start_time
        return {
            "service": service_name,
            "url": url,
            "status": "unreachable",
            "response_time": response_time,
            "status_code": None,
            "error": str(e)
        }

async def check_all_services():
    """Check health of all services."""
    services = [
        ("API Gateway", "http://localhost:8000/health"),
        ("Search Service", "http://localhost:8001/health"),
        ("Factcheck Service", "http://localhost:8002/health"),
        ("Synthesis Service", "http://localhost:8003/health"),
        ("Meilisearch", "http://localhost:7700/health"),
        ("ArangoDB", "http://localhost:8529/_api/version"),
        ("Redis", "http://localhost:6379"),  # Redis doesn't have HTTP health
    ]
    
    print("🔍 Checking service health...")
    results = []
    
    for service_name, url in services:
        result = await check_service_health(service_name, url)
        results.append(result)
        
        status_icon = "✅" if result["status"] == "healthy" else "❌"
        print(f"{status_icon} {service_name}: {result['status']} ({result['response_time']:.3f}s)")
        
        if result["error"]:
            print(f"   Error: {result['error']}")
    
    # Summary
    healthy_count = sum(1 for r in results if r["status"] == "healthy")
    total_count = len(results)
    
    print(f"\\n📊 Summary: {healthy_count}/{total_count} services healthy")
    
    if healthy_count == total_count:
        print("🎉 All services are healthy!")
    elif healthy_count > 0:
        print("⚠️ Some services are unhealthy")
    else:
        print("❌ No services are healthy")
    
    return results

if __name__ == "__main__":
    asyncio.run(check_all_services())
