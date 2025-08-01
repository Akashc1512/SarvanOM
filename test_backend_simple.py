#!/usr/bin/env python3
"""
Simple Backend Test Script
Tests the basic functionality of the Universal Knowledge Platform backend.
"""

import asyncio
import aiohttp
import json
import sys
import time
from datetime import datetime

async def test_backend():
    """Test the backend endpoints."""
    
    base_url = "http://localhost:8000"
    test_results = []
    
    print("🔍 Testing Universal Knowledge Platform Backend")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Health Check
        print("\n1. Testing Health Check...")
        try:
            async with session.get(f"{base_url}/health", timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check passed: {data.get('status', 'unknown')}")
                    test_results.append(("Health Check", "PASS"))
                else:
                    error_text = await response.text()
                    print(f"❌ Health check failed: {response.status}")
                    print(f"Error details: {error_text[:200]}...")
                    test_results.append(("Health Check", "FAIL"))
        except Exception as e:
            print(f"❌ Health check error: {e}")
            test_results.append(("Health Check", "ERROR"))
        
        # Test 2: Root Endpoint
        print("\n2. Testing Root Endpoint...")
        try:
            async with session.get(f"{base_url}/", timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Root endpoint working: {data.get('message', 'unknown')}")
                    test_results.append(("Root Endpoint", "PASS"))
                else:
                    error_text = await response.text()
                    print(f"❌ Root endpoint failed: {response.status}")
                    print(f"Error details: {error_text[:200]}...")
                    test_results.append(("Root Endpoint", "FAIL"))
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
            test_results.append(("Root Endpoint", "ERROR"))
        
        # Test 3: Metrics Endpoint
        print("\n3. Testing Metrics Endpoint...")
        try:
            async with session.get(f"{base_url}/metrics", timeout=10) as response:
                if response.status == 200:
                    print("✅ Metrics endpoint working")
                    test_results.append(("Metrics", "PASS"))
                else:
                    error_text = await response.text()
                    print(f"❌ Metrics endpoint failed: {response.status}")
                    print(f"Error details: {error_text[:200]}...")
                    test_results.append(("Metrics", "FAIL"))
        except Exception as e:
            print(f"❌ Metrics endpoint error: {e}")
            test_results.append(("Metrics", "ERROR"))
        
        # Test 4: System Diagnostics
        print("\n4. Testing System Diagnostics...")
        try:
            async with session.get(f"{base_url}/system/diagnostics", timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ System diagnostics working: {data.get('status', 'unknown')}")
                    test_results.append(("System Diagnostics", "PASS"))
                else:
                    error_text = await response.text()
                    print(f"❌ System diagnostics failed: {response.status}")
                    print(f"Error details: {error_text[:200]}...")
                    test_results.append(("System Diagnostics", "FAIL"))
        except Exception as e:
            print(f"❌ System diagnostics error: {e}")
            test_results.append(("System Diagnostics", "ERROR"))
    
    # Print Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    failed = 0
    errors = 0
    
    for test_name, result in test_results:
        if result == "PASS":
            print(f"✅ {test_name}: PASS")
            passed += 1
        elif result == "FAIL":
            print(f"❌ {test_name}: FAIL")
            failed += 1
        else:
            print(f"⚠️ {test_name}: ERROR")
            errors += 1
    
    print(f"\n📈 Results: {passed} passed, {failed} failed, {errors} errors")
    
    if failed == 0 and errors == 0:
        print("🎉 All tests passed! Backend is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the backend configuration.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_backend())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1) 