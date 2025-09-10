#!/usr/bin/env python3
"""
Test script for External Feeds Service
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

class FeedsTester:
    """Test the external feeds service implementation"""
    
    def __init__(self):
        self.service_url = "http://localhost:8005"
        self.http_client = httpx.AsyncClient()
    
    async def test_service_health(self) -> bool:
        """Test service health check"""
        print("Testing External Feeds Service Health...")
        
        try:
            response = await self.http_client.get(f"{self.service_url}/health")
            assert response.status_code == 200
            health_data = response.json()
            assert health_data["status"] == "healthy"
            assert health_data["service"] == "feeds"
            print("✓ Service health check passed")
            return True
            
        except Exception as e:
            print(f"✗ Service health check failed: {e}")
            return False
    
    async def test_provider_status(self) -> bool:
        """Test provider status endpoint"""
        print("\nTesting Provider Status...")
        
        try:
            response = await self.http_client.get(f"{self.service_url}/providers")
            assert response.status_code == 200
            providers_data = response.json()
            assert "news_providers" in providers_data
            assert "markets_providers" in providers_data
            assert "provider_health" in providers_data
            
            expected_news_providers = ["newsapi", "rss", "reddit"]
            expected_markets_providers = ["alphavantage", "yahoo", "coingecko"]
            
            for provider in expected_news_providers:
                assert provider in providers_data["news_providers"], f"Missing news provider: {provider}"
            
            for provider in expected_markets_providers:
                assert provider in providers_data["markets_providers"], f"Missing markets provider: {provider}"
            
            print(f"✓ Provider status check passed - Found {len(providers_data['news_providers'])} news providers and {len(providers_data['markets_providers'])} markets providers")
            return True
            
        except Exception as e:
            print(f"✗ Provider status check failed: {e}")
            return False
    
    async def test_constraints_support(self) -> bool:
        """Test supported constraints endpoint"""
        print("\nTesting Supported Constraints...")
        
        try:
            response = await self.http_client.get(f"{self.service_url}/constraints")
            assert response.status_code == 200
            constraints_data = response.json()
            
            # Check news constraints
            assert "news" in constraints_data
            news_constraints = constraints_data["news"]
            assert "region" in news_constraints
            assert "category" in news_constraints
            assert "language" in news_constraints
            assert "date_range" in news_constraints
            
            # Check markets constraints
            assert "markets" in constraints_data
            markets_constraints = constraints_data["markets"]
            assert "tickers" in markets_constraints
            assert "date_range" in markets_constraints
            assert "interval" in markets_constraints
            assert "indicators" in markets_constraints
            
            print("✓ Supported constraints check passed")
            return True
            
        except Exception as e:
            print(f"✗ Supported constraints check failed: {e}")
            return False
    
    async def test_news_fetching(self) -> bool:
        """Test news fetching functionality"""
        print("\nTesting News Fetching...")
        
        test_cases = [
            {
                "query": "artificial intelligence",
                "constraints": {
                    "category": "Technology",
                    "language": "English"
                }
            },
            {
                "query": "climate change",
                "constraints": {
                    "region": "Global",
                    "date_range": "Last 7 days"
                }
            },
            {
                "query": "stock market",
                "constraints": {
                    "sources": ["reuters", "bloomberg"]
                }
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases):
            try:
                print(f"  Test case {i+1}: {test_case['query']}")
                
                response = await self.http_client.post(
                    f"{self.service_url}/fetch",
                    json={
                        "query": test_case["query"],
                        "feed_type": "news",
                        "constraints": test_case["constraints"],
                        "user_id": "test_user",
                        "session_id": "test_session",
                        "trace_id": f"news_test_{i}"
                    }
                )
                
                assert response.status_code == 200
                results = response.json()
                
                # Check response structure
                assert isinstance(results, list), "Results should be a list"
                
                # Check each provider result
                for result in results:
                    assert "provider" in result
                    assert "status" in result
                    assert "items" in result
                    assert "latency_ms" in result
                    
                    # Check items structure
                    for item in result["items"]:
                        assert "id" in item
                        assert "title" in item
                        assert "content" in item
                        assert "url" in item
                        assert "source" in item
                        assert "attribution" in item
                
                total_items = sum(len(result["items"]) for result in results)
                print(f"    ✓ Fetched {total_items} news items from {len(results)} providers")
                success_count += 1
                
            except Exception as e:
                print(f"    ✗ Test case {i+1} failed: {e}")
        
        print(f"✓ {success_count}/{len(test_cases)} news fetching tests passed")
        return success_count == len(test_cases)
    
    async def test_markets_fetching(self) -> bool:
        """Test markets fetching functionality"""
        print("\nTesting Markets Fetching...")
        
        test_cases = [
            {
                "query": "AAPL stock price",
                "constraints": {
                    "tickers": ["AAPL"],
                    "date_range": "1 day"
                }
            },
            {
                "query": "bitcoin cryptocurrency",
                "constraints": {
                    "tickers": ["bitcoin"],
                    "interval": "1 hour"
                }
            },
            {
                "query": "tech stocks",
                "constraints": {
                    "tickers": ["AAPL", "GOOGL", "MSFT"],
                    "region": "US Markets"
                }
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases):
            try:
                print(f"  Test case {i+1}: {test_case['query']}")
                
                response = await self.http_client.post(
                    f"{self.service_url}/fetch",
                    json={
                        "query": test_case["query"],
                        "feed_type": "markets",
                        "constraints": test_case["constraints"],
                        "user_id": "test_user",
                        "session_id": "test_session",
                        "trace_id": f"markets_test_{i}"
                    }
                )
                
                assert response.status_code == 200
                results = response.json()
                
                # Check response structure
                assert isinstance(results, list), "Results should be a list"
                
                # Check each provider result
                for result in results:
                    assert "provider" in result
                    assert "status" in result
                    assert "items" in result
                    assert "latency_ms" in result
                    
                    # Check items structure
                    for item in result["items"]:
                        assert "id" in item
                        assert "title" in item
                        assert "content" in item
                        assert "url" in item
                        assert "source" in item
                        assert "attribution" in item
                        assert "metadata" in item
                
                total_items = sum(len(result["items"]) for result in results)
                print(f"    ✓ Fetched {total_items} market items from {len(results)} providers")
                success_count += 1
                
            except Exception as e:
                print(f"    ✗ Test case {i+1} failed: {e}")
        
        print(f"✓ {success_count}/{len(test_cases)} markets fetching tests passed")
        return success_count == len(test_cases)
    
    async def test_timeout_compliance(self) -> bool:
        """Test timeout compliance (800ms per provider)"""
        print("\nTesting Timeout Compliance...")
        
        try:
            start_time = time.time()
            
            response = await self.http_client.post(
                f"{self.service_url}/fetch",
                json={
                    "query": "test query",
                    "feed_type": "news",
                    "constraints": {},
                    "user_id": "test_user",
                    "session_id": "test_session",
                    "trace_id": "timeout_test"
                }
            )
            
            end_time = time.time()
            total_latency = (end_time - start_time) * 1000
            
            assert response.status_code == 200
            results = response.json()
            
            # Check individual provider latencies
            for result in results:
                assert result["latency_ms"] <= 800, f"Provider {result['provider']} exceeded 800ms timeout: {result['latency_ms']}ms"
            
            print(f"    ✓ All providers completed within 800ms timeout (total: {total_latency:.1f}ms)")
            print("✓ Timeout compliance test passed")
            return True
            
        except Exception as e:
            print(f"✗ Timeout compliance test failed: {e}")
            return False
    
    async def test_attribution_compliance(self) -> bool:
        """Test attribution compliance"""
        print("\nTesting Attribution Compliance...")
        
        try:
            response = await self.http_client.post(
                f"{self.service_url}/fetch",
                json={
                    "query": "test attribution",
                    "feed_type": "news",
                    "constraints": {},
                    "user_id": "test_user",
                    "session_id": "test_session",
                    "trace_id": "attribution_test"
                }
            )
            
            assert response.status_code == 200
            results = response.json()
            
            # Check attribution for each item
            for result in results:
                for item in result["items"]:
                    attribution = item.get("attribution", {})
                    
                    # Check required attribution fields
                    assert "source" in attribution, "Missing source attribution"
                    assert "article" in attribution, "Missing article attribution"
                    assert "license" in attribution, "Missing license attribution"
                    
                    # Check source attribution
                    source = attribution["source"]
                    assert "name" in source, "Missing source name"
                    assert "url" in source, "Missing source URL"
                    
                    # Check article attribution
                    article = attribution["article"]
                    assert "title" in article, "Missing article title"
                    assert "url" in article, "Missing article URL"
                    
                    # Check license attribution
                    license_info = attribution["license"]
                    assert "type" in license_info, "Missing license type"
                    assert "terms" in license_info, "Missing license terms"
            
            print("✓ Attribution compliance test passed")
            return True
            
        except Exception as e:
            print(f"✗ Attribution compliance test failed: {e}")
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling"""
        print("\nTesting Error Handling...")
        
        try:
            # Test invalid feed type
            response = await self.http_client.post(
                f"{self.service_url}/fetch",
                json={
                    "query": "test query",
                    "feed_type": "invalid",
                    "constraints": {},
                    "user_id": "test_user",
                    "session_id": "test_session",
                    "trace_id": "error_test"
                }
            )
            assert response.status_code == 400
            print("    ✓ Invalid feed type handled correctly")
            
            # Test missing required fields
            response = await self.http_client.post(
                f"{self.service_url}/fetch",
                json={
                    "query": "test query"
                    # Missing required fields
                }
            )
            assert response.status_code in [400, 422]
            print("    ✓ Missing fields handled correctly")
            
            print("✓ Error handling tests passed")
            return True
            
        except Exception as e:
            print(f"✗ Error handling test failed: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all tests"""
        print("Starting External Feeds Service Tests...")
        print("=" * 50)
        
        tests = [
            self.test_service_health,
            self.test_provider_status,
            self.test_constraints_support,
            self.test_news_fetching,
            self.test_markets_fetching,
            self.test_timeout_compliance,
            self.test_attribution_compliance,
            self.test_error_handling
        ]
        
        results = []
        for test in tests:
            try:
                result = await test()
                results.append(result)
            except Exception as e:
                print(f"✗ Test {test.__name__} failed with exception: {e}")
                results.append(False)
        
        print("\n" + "=" * 50)
        print("Test Results Summary:")
        print(f"Service Health: {'✓ PASS' if results[0] else '✗ FAIL'}")
        print(f"Provider Status: {'✓ PASS' if results[1] else '✗ FAIL'}")
        print(f"Constraints Support: {'✓ PASS' if results[2] else '✗ FAIL'}")
        print(f"News Fetching: {'✓ PASS' if results[3] else '✗ FAIL'}")
        print(f"Markets Fetching: {'✓ PASS' if results[4] else '✗ FAIL'}")
        print(f"Timeout Compliance: {'✓ PASS' if results[5] else '✗ FAIL'}")
        print(f"Attribution Compliance: {'✓ PASS' if results[6] else '✗ FAIL'}")
        print(f"Error Handling: {'✓ PASS' if results[7] else '✗ FAIL'}")
        
        all_passed = all(results)
        print(f"\nOverall Result: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
        
        return all_passed

async def main():
    """Main test function"""
    tester = FeedsTester()
    
    # Wait for service to be ready
    print("Waiting for External Feeds service to be ready...")
    await asyncio.sleep(5)
    
    # Run tests
    success = await tester.run_all_tests()
    
    # Cleanup
    await tester.http_client.aclose()
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
