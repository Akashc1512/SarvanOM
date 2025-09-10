#!/usr/bin/env python3
"""
Test script for Retrieval Service
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

class RetrievalTester:
    """Test the retrieval service implementation"""
    
    def __init__(self):
        self.service_url = "http://localhost:8004"
        self.http_client = httpx.AsyncClient()
    
    async def test_service_health(self) -> bool:
        """Test service health check"""
        print("Testing Retrieval Service Health...")
        
        try:
            response = await self.http_client.get(f"{self.service_url}/health")
            assert response.status_code == 200
            health_data = response.json()
            assert health_data["status"] == "healthy"
            assert health_data["service"] == "retrieval"
            print("✓ Service health check passed")
            return True
            
        except Exception as e:
            print(f"✗ Service health check failed: {e}")
            return False
    
    async def test_lane_status(self) -> bool:
        """Test lane status endpoint"""
        print("\nTesting Lane Status...")
        
        try:
            response = await self.http_client.get(f"{self.service_url}/lanes")
            assert response.status_code == 200
            lanes_data = response.json()
            assert "lanes" in lanes_data
            assert "status" in lanes_data
            assert "budget_allocations" in lanes_data
            
            expected_lanes = ["web", "vector", "keyword", "knowledge_graph", "news", "markets", "preflight"]
            for lane in expected_lanes:
                assert lane in lanes_data["lanes"], f"Missing lane: {lane}"
            
            print(f"✓ Lane status check passed - Found {len(lanes_data['lanes'])} lanes")
            return True
            
        except Exception as e:
            print(f"✗ Lane status check failed: {e}")
            return False
    
    async def test_retrieval_processing(self) -> bool:
        """Test retrieval processing"""
        print("\nTesting Retrieval Processing...")
        
        test_cases = [
            {
                "query": "What is machine learning?",
                "complexity": "simple",
                "constraints": []
            },
            {
                "query": "Explain neural networks in detail",
                "complexity": "technical",
                "constraints": [
                    {
                        "id": "time_range",
                        "label": "Time Range",
                        "type": "select",
                        "options": ["Recent (1 year)", "Last 5 years", "All time"],
                        "selected": "Recent (1 year)"
                    }
                ]
            },
            {
                "query": "Comprehensive analysis of climate change",
                "complexity": "research",
                "constraints": [
                    {
                        "id": "sources",
                        "label": "Sources",
                        "type": "select",
                        "options": ["Academic", "News", "Both"],
                        "selected": "Academic"
                    },
                    {
                        "id": "citations_required",
                        "label": "Citations Required",
                        "type": "boolean",
                        "options": ["Yes", "No"],
                        "selected": "Yes"
                    }
                ]
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases):
            try:
                print(f"  Test case {i+1}: {test_case['query']}")
                
                response = await self.http_client.post(
                    f"{self.service_url}/retrieve",
                    json={
                        "query": test_case["query"],
                        "complexity": test_case["complexity"],
                        "constraints": test_case["constraints"],
                        "user_id": "test_user",
                        "session_id": "test_session",
                        "trace_id": f"test_trace_{i}",
                        "budget_remaining": 1.0
                    }
                )
                
                assert response.status_code == 200
                result = response.json()
                
                # Check response structure
                assert "results" in result
                assert "fusion_metadata" in result
                assert "citations" in result
                assert "disagreements" in result
                assert "total_results" in result
                assert "unique_domains" in result
                assert "fusion_time_ms" in result
                
                # Check fusion metadata
                fusion_meta = result["fusion_metadata"]
                assert "total_lanes" in fusion_meta
                assert "successful_lanes" in fusion_meta
                assert "rrf_k" in fusion_meta
                
                # Check results
                assert len(result["results"]) > 0, "Should have results"
                assert result["total_results"] > 0, "Should have total results count"
                assert result["unique_domains"] > 0, "Should have unique domains"
                
                print(f"    ✓ Processed successfully (results: {result['total_results']}, domains: {result['unique_domains']}, fusion: {result['fusion_time_ms']:.1f}ms)")
                success_count += 1
                
            except Exception as e:
                print(f"    ✗ Test case {i+1} failed: {e}")
        
        print(f"✓ {success_count}/{len(test_cases)} retrieval tests passed")
        return success_count == len(test_cases)
    
    async def test_budget_compliance(self) -> bool:
        """Test budget compliance"""
        print("\nTesting Budget Compliance...")
        
        try:
            # Test simple query (5s budget)
            start_time = time.time()
            response = await self.http_client.post(
                f"{self.service_url}/retrieve",
                json={
                    "query": "What is Python?",
                    "complexity": "simple",
                    "constraints": [],
                    "user_id": "test_user",
                    "session_id": "test_session",
                    "trace_id": "budget_test",
                    "budget_remaining": 1.0
                }
            )
            end_time = time.time()
            total_latency = (end_time - start_time) * 1000
            
            assert response.status_code == 200
            result = response.json()
            
            # Check that fusion time is reasonable
            assert result["fusion_time_ms"] < 1000, f"Fusion time {result['fusion_time_ms']}ms too high"
            
            print(f"    ✓ Simple query processed in {total_latency:.1f}ms (fusion: {result['fusion_time_ms']:.1f}ms)")
            
            # Test technical query (7s budget)
            start_time = time.time()
            response = await self.http_client.post(
                f"{self.service_url}/retrieve",
                json={
                    "query": "Explain deep learning algorithms",
                    "complexity": "technical",
                    "constraints": [],
                    "user_id": "test_user",
                    "session_id": "test_session",
                    "trace_id": "budget_test_2",
                    "budget_remaining": 1.0
                }
            )
            end_time = time.time()
            total_latency = (end_time - start_time) * 1000
            
            assert response.status_code == 200
            result = response.json()
            
            print(f"    ✓ Technical query processed in {total_latency:.1f}ms (fusion: {result['fusion_time_ms']:.1f}ms)")
            
            print("✓ Budget compliance tests passed")
            return True
            
        except Exception as e:
            print(f"✗ Budget compliance test failed: {e}")
            return False
    
    async def test_constraint_binding(self) -> bool:
        """Test constraint binding"""
        print("\nTesting Constraint Binding...")
        
        try:
            # Test with time range constraint
            response = await self.http_client.post(
                f"{self.service_url}/retrieve",
                json={
                    "query": "AI developments",
                    "complexity": "research",
                    "constraints": [
                        {
                            "id": "time_range",
                            "label": "Time Range",
                            "type": "select",
                            "options": ["Recent (1 year)", "Last 5 years", "All time"],
                            "selected": "Recent (1 year)"
                        }
                    ],
                    "user_id": "test_user",
                    "session_id": "test_session",
                    "trace_id": "constraint_test",
                    "budget_remaining": 1.0
                }
            )
            
            assert response.status_code == 200
            result = response.json()
            assert len(result["results"]) > 0, "Should have results with time constraint"
            
            # Test with source constraint
            response = await self.http_client.post(
                f"{self.service_url}/retrieve",
                json={
                    "query": "machine learning research",
                    "complexity": "technical",
                    "constraints": [
                        {
                            "id": "sources",
                            "label": "Sources",
                            "type": "select",
                            "options": ["Academic", "News", "Both"],
                            "selected": "Academic"
                        }
                    ],
                    "user_id": "test_user",
                    "session_id": "test_session",
                    "trace_id": "constraint_test_2",
                    "budget_remaining": 1.0
                }
            )
            
            assert response.status_code == 200
            result = response.json()
            assert len(result["results"]) > 0, "Should have results with source constraint"
            
            print("✓ Constraint binding tests passed")
            return True
            
        except Exception as e:
            print(f"✗ Constraint binding test failed: {e}")
            return False
    
    async def test_citation_generation(self) -> bool:
        """Test citation generation"""
        print("\nTesting Citation Generation...")
        
        try:
            response = await self.http_client.post(
                f"{self.service_url}/retrieve",
                json={
                    "query": "climate change research",
                    "complexity": "research",
                    "constraints": [
                        {
                            "id": "citations_required",
                            "label": "Citations Required",
                            "type": "boolean",
                            "options": ["Yes", "No"],
                            "selected": "Yes"
                        }
                    ],
                    "user_id": "test_user",
                    "session_id": "test_session",
                    "trace_id": "citation_test",
                    "budget_remaining": 1.0
                }
            )
            
            assert response.status_code == 200
            result = response.json()
            
            # Check citations
            assert "citations" in result
            assert len(result["citations"]) > 0, "Should have citations"
            
            # Check citation structure
            for citation in result["citations"]:
                assert "id" in citation
                assert "title" in citation
                assert "url" in citation
                assert "domain" in citation
                assert "relevance_score" in citation
                assert "authority_score" in citation
            
            print(f"✓ Citation generation test passed - Generated {len(result['citations'])} citations")
            return True
            
        except Exception as e:
            print(f"✗ Citation generation test failed: {e}")
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling"""
        print("\nTesting Error Handling...")
        
        try:
            # Test invalid complexity
            response = await self.http_client.post(
                f"{self.service_url}/retrieve",
                json={
                    "query": "test query",
                    "complexity": "invalid",
                    "constraints": [],
                    "user_id": "test_user",
                    "session_id": "test_session",
                    "trace_id": "error_test",
                    "budget_remaining": 1.0
                }
            )
            # Should handle gracefully
            assert response.status_code in [200, 400, 422]
            print("    ✓ Invalid complexity handled gracefully")
            
            # Test missing required fields
            response = await self.http_client.post(
                f"{self.service_url}/retrieve",
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
        print("Starting Retrieval Service Tests...")
        print("=" * 50)
        
        tests = [
            self.test_service_health,
            self.test_lane_status,
            self.test_retrieval_processing,
            self.test_budget_compliance,
            self.test_constraint_binding,
            self.test_citation_generation,
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
        print(f"Lane Status: {'✓ PASS' if results[1] else '✗ FAIL'}")
        print(f"Retrieval Processing: {'✓ PASS' if results[2] else '✗ FAIL'}")
        print(f"Budget Compliance: {'✓ PASS' if results[3] else '✗ FAIL'}")
        print(f"Constraint Binding: {'✓ PASS' if results[4] else '✗ FAIL'}")
        print(f"Citation Generation: {'✓ PASS' if results[5] else '✗ FAIL'}")
        print(f"Error Handling: {'✓ PASS' if results[6] else '✗ FAIL'}")
        
        all_passed = all(results)
        print(f"\nOverall Result: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
        
        return all_passed

async def main():
    """Main test function"""
    tester = RetrievalTester()
    
    # Wait for service to be ready
    print("Waiting for Retrieval service to be ready...")
    await asyncio.sleep(5)
    
    # Run tests
    success = await tester.run_all_tests()
    
    # Cleanup
    await tester.http_client.aclose()
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
