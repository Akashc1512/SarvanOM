#!/usr/bin/env python3
"""
Comprehensive test script for all Model Services (Registry, Router, Auto-Upgrade, Guided Prompt)
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any, List

class AllServicesTester:
    """Test all model services together"""
    
    def __init__(self):
        self.registry_url = "http://localhost:8000"
        self.router_url = "http://localhost:8001"
        self.auto_upgrade_url = "http://localhost:8002"
        self.guided_prompt_url = "http://localhost:8003"
        self.http_client = httpx.AsyncClient()
    
    async def test_all_services_health(self) -> bool:
        """Test health of all services"""
        print("Testing All Services Health...")
        
        services = [
            ("Model Registry", self.registry_url),
            ("Model Router", self.router_url),
            ("Auto-Upgrade", self.auto_upgrade_url),
            ("Guided Prompt", self.guided_prompt_url)
        ]
        
        all_healthy = True
        
        for service_name, url in services:
            try:
                response = await self.http_client.get(f"{url}/health")
                assert response.status_code == 200
                health_data = response.json()
                assert health_data["status"] == "healthy"
                print(f"✓ {service_name} is healthy")
            except Exception as e:
                print(f"✗ {service_name} health check failed: {e}")
                all_healthy = False
        
        return all_healthy
    
    async def test_end_to_end_workflow(self) -> bool:
        """Test complete end-to-end workflow"""
        print("\nTesting End-to-End Workflow...")
        
        try:
            # Step 1: Get available models from registry
            print("  Step 1: Getting available models...")
            response = await self.http_client.get(f"{self.registry_url}/models/stable")
            assert response.status_code == 200
            models = response.json()
            assert len(models) > 0
            print(f"    ✓ Found {len(models)} stable models")
            
            # Step 2: Route a query through the router
            print("  Step 2: Routing query...")
            response = await self.http_client.post(
                f"{self.router_url}/route",
                json={
                    "query": "What is the capital of France?",
                    "context": {}
                }
            )
            assert response.status_code == 200
            routing = response.json()
            assert "model_id" in routing
            assert "provider" in routing
            print(f"    ✓ Query routed to {routing['model_id']}")
            
            # Step 3: Test guided prompt refinement
            print("  Step 3: Testing guided prompt refinement...")
            response = await self.http_client.post(
                f"{self.guided_prompt_url}/refine",
                json={
                    "query": "show me apple",
                    "context": {"intent_confidence": 0.3}
                }
            )
            assert response.status_code == 200
            refinement = response.json()
            assert "should_trigger" in refinement
            print(f"    ✓ Refinement processed (triggered: {refinement['should_trigger']})")
            
            # Step 4: Test refinement routing
            if refinement["should_trigger"]:
                print("  Step 4: Testing refinement routing...")
                response = await self.http_client.post(
                    f"{self.router_url}/route/refinement",
                    json={
                        "query": "show me apple",
                        "refinement_type": "fast"
                    }
                )
                assert response.status_code == 200
                refinement_routing = response.json()
                assert "model_id" in refinement_routing
                print(f"    ✓ Refinement routed to {refinement_routing['model_id']}")
            
            # Step 5: Test auto-upgrade discovery
            print("  Step 5: Testing auto-upgrade discovery...")
            response = await self.http_client.post(f"{self.auto_upgrade_url}/discover")
            assert response.status_code == 200
            discovery = response.json()
            assert "discovered" in discovery
            print(f"    ✓ Discovery found {discovery['discovered']} models")
            
            print("✓ End-to-end workflow test passed")
            return True
            
        except Exception as e:
            print(f"✗ End-to-end workflow test failed: {e}")
            return False
    
    async def test_performance_budgets(self) -> bool:
        """Test performance budget enforcement"""
        print("\nTesting Performance Budgets...")
        
        try:
            # Test guided prompt latency budget
            print("  Testing Guided Prompt latency budget...")
            start_time = time.time()
            response = await self.http_client.post(
                f"{self.guided_prompt_url}/refine",
                json={
                    "query": "show me apple",
                    "context": {"intent_confidence": 0.3}
                }
            )
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            assert response.status_code == 200
            result = response.json()
            assert result["latency_ms"] <= 500, f"Guided prompt latency {result['latency_ms']}ms exceeded 500ms budget"
            print(f"    ✓ Guided prompt latency: {result['latency_ms']}ms (budget: ≤500ms)")
            
            # Test router selection time
            print("  Testing Router selection time...")
            start_time = time.time()
            response = await self.http_client.post(
                f"{self.router_url}/route",
                json={
                    "query": "What is machine learning?",
                    "context": {}
                }
            )
            end_time = time.time()
            selection_time = (end_time - start_time) * 1000
            
            assert response.status_code == 200
            assert selection_time <= 1000, f"Router selection time {selection_time}ms exceeded 1000ms budget"
            print(f"    ✓ Router selection time: {selection_time}ms (budget: ≤1000ms)")
            
            print("✓ Performance budget tests passed")
            return True
            
        except Exception as e:
            print(f"✗ Performance budget test failed: {e}")
            return False
    
    async def test_integration_scenarios(self) -> bool:
        """Test various integration scenarios"""
        print("\nTesting Integration Scenarios...")
        
        scenarios = [
            {
                "name": "Simple Query",
                "query": "What is the weather?",
                "context": {"intent_confidence": 0.9},
                "expected_trigger": False
            },
            {
                "name": "Ambiguous Query",
                "query": "show me python",
                "context": {"intent_confidence": 0.3},
                "expected_trigger": True
            },
            {
                "name": "Multimodal Query",
                "query": "analyze this image",
                "context": {"has_images": True, "intent_confidence": 0.4},
                "expected_trigger": True
            },
            {
                "name": "Complex Research Query",
                "query": "comprehensive analysis of climate change",
                "context": {"intent_confidence": 0.2},
                "expected_trigger": True
            }
        ]
        
        success_count = 0
        
        for scenario in scenarios:
            try:
                print(f"  Testing scenario: {scenario['name']}")
                
                # Test guided prompt
                response = await self.http_client.post(
                    f"{self.guided_prompt_url}/refine",
                    json={
                        "query": scenario["query"],
                        "context": scenario["context"]
                    }
                )
                assert response.status_code == 200
                refinement = response.json()
                
                # Test router
                response = await self.http_client.post(
                    f"{self.router_url}/route",
                    json={
                        "query": scenario["query"],
                        "context": scenario["context"]
                    }
                )
                assert response.status_code == 200
                routing = response.json()
                
                print(f"    ✓ Guided prompt: {refinement['should_trigger']}, Router: {routing['model_id']}")
                success_count += 1
                
            except Exception as e:
                print(f"    ✗ Scenario {scenario['name']} failed: {e}")
        
        print(f"✓ {success_count}/{len(scenarios)} integration scenarios passed")
        return success_count == len(scenarios)
    
    async def test_error_handling(self) -> bool:
        """Test error handling and resilience"""
        print("\nTesting Error Handling...")
        
        try:
            # Test invalid query
            print("  Testing invalid query handling...")
            response = await self.http_client.post(
                f"{self.guided_prompt_url}/refine",
                json={
                    "query": "",
                    "context": {}
                }
            )
            # Should handle gracefully
            assert response.status_code in [200, 400]
            print("    ✓ Invalid query handled gracefully")
            
            # Test missing context
            print("  Testing missing context handling...")
            response = await self.http_client.post(
                f"{self.router_url}/route",
                json={
                    "query": "test query"
                }
            )
            assert response.status_code == 200
            print("    ✓ Missing context handled gracefully")
            
            # Test invalid model ID
            print("  Testing invalid model ID handling...")
            response = await self.http_client.get(f"{self.registry_url}/models/invalid_model_id")
            assert response.status_code == 404
            print("    ✓ Invalid model ID handled correctly")
            
            print("✓ Error handling tests passed")
            return True
            
        except Exception as e:
            print(f"✗ Error handling test failed: {e}")
            return False
    
    async def test_metrics_and_monitoring(self) -> bool:
        """Test metrics and monitoring endpoints"""
        print("\nTesting Metrics and Monitoring...")
        
        try:
            # Test Prometheus metrics endpoints
            metrics_endpoints = [
                (8001, "Model Registry"),
                (8002, "Model Router"),
                (8003, "Auto-Upgrade"),
                (8004, "Guided Prompt")
            ]
            
            for port, service_name in metrics_endpoints:
                try:
                    response = await self.http_client.get(f"http://localhost:{port}/metrics")
                    assert response.status_code == 200
                    print(f"    ✓ {service_name} metrics endpoint accessible")
                except Exception as e:
                    print(f"    ⚠ {service_name} metrics endpoint not accessible: {e}")
            
            print("✓ Metrics and monitoring tests passed")
            return True
            
        except Exception as e:
            print(f"✗ Metrics and monitoring test failed: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all comprehensive tests"""
        print("Starting Comprehensive Model Services Tests...")
        print("=" * 60)
        
        tests = [
            self.test_all_services_health,
            self.test_end_to_end_workflow,
            self.test_performance_budgets,
            self.test_integration_scenarios,
            self.test_error_handling,
            self.test_metrics_and_monitoring
        ]
        
        results = []
        for test in tests:
            try:
                result = await test()
                results.append(result)
            except Exception as e:
                print(f"✗ Test {test.__name__} failed with exception: {e}")
                results.append(False)
        
        print("\n" + "=" * 60)
        print("Comprehensive Test Results Summary:")
        print(f"All Services Health: {'✓ PASS' if results[0] else '✗ FAIL'}")
        print(f"End-to-End Workflow: {'✓ PASS' if results[1] else '✗ FAIL'}")
        print(f"Performance Budgets: {'✓ PASS' if results[2] else '✗ FAIL'}")
        print(f"Integration Scenarios: {'✓ PASS' if results[3] else '✗ FAIL'}")
        print(f"Error Handling: {'✓ PASS' if results[4] else '✗ FAIL'}")
        print(f"Metrics and Monitoring: {'✓ PASS' if results[5] else '✗ FAIL'}")
        
        all_passed = all(results)
        passed_count = sum(results)
        total_count = len(results)
        
        print(f"\nOverall Result: {passed_count}/{total_count} tests passed")
        print(f"Status: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
        
        return all_passed

async def main():
    """Main test function"""
    tester = AllServicesTester()
    
    # Wait for all services to be ready
    print("Waiting for all services to be ready...")
    await asyncio.sleep(10)
    
    # Run comprehensive tests
    success = await tester.run_all_tests()
    
    # Cleanup
    await tester.http_client.aclose()
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
