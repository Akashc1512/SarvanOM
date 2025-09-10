#!/usr/bin/env python3
"""
Test script for Observability Service
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

class ObservabilityTester:
    """Test the observability service implementation"""
    
    def __init__(self):
        self.service_url = "http://localhost:8006"
        self.http_client = httpx.AsyncClient()
    
    async def test_service_health(self) -> bool:
        """Test service health check"""
        print("Testing Observability Service Health...")
        
        try:
            response = await self.http_client.get(f"{self.service_url}/health")
            assert response.status_code == 200
            health_data = response.json()
            assert health_data["status"] == "healthy"
            assert health_data["service"] == "observability"
            print("✓ Service health check passed")
            return True
            
        except Exception as e:
            print(f"✗ Service health check failed: {e}")
            return False
    
    async def test_sla_metrics_recording(self) -> bool:
        """Test SLA metrics recording"""
        print("\nTesting SLA Metrics Recording...")
        
        test_cases = [
            {
                "global_ms": 4500,
                "ttft_ms": 1200,
                "orchestrator_reserve_ms": 400,
                "llm_ms": 800,
                "web_ms": 900,
                "vector_ms": 700,
                "kg_ms": 850,
                "yt_ms": 0,
                "mode": "simple",
                "complexity": "low"
            },
            {
                "global_ms": 6500,
                "ttft_ms": 1400,
                "orchestrator_reserve_ms": 600,
                "llm_ms": 1200,
                "web_ms": 1300,
                "vector_ms": 1100,
                "kg_ms": 1250,
                "yt_ms": 0,
                "mode": "technical",
                "complexity": "medium"
            },
            {
                "global_ms": 9500,
                "ttft_ms": 1600,
                "orchestrator_reserve_ms": 800,
                "llm_ms": 1800,
                "web_ms": 1900,
                "vector_ms": 1700,
                "kg_ms": 1850,
                "yt_ms": 0,
                "mode": "research",
                "complexity": "high"
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases):
            try:
                print(f"  Test case {i+1}: {test_case['mode']} mode")
                
                response = await self.http_client.post(
                    f"{self.service_url}/metrics/sla",
                    json=test_case
                )
                
                assert response.status_code == 200
                result = response.json()
                assert result["status"] == "success"
                assert "SLA metrics recorded" in result["message"]
                
                print(f"    ✓ SLA metrics recorded for {test_case['mode']} mode")
                success_count += 1
                
            except Exception as e:
                print(f"    ✗ Test case {i+1} failed: {e}")
        
        print(f"✓ {success_count}/{len(test_cases)} SLA metrics tests passed")
        return success_count == len(test_cases)
    
    async def test_lane_metrics_recording(self) -> bool:
        """Test lane metrics recording"""
        print("\nTesting Lane Metrics Recording...")
        
        test_cases = [
            {
                "lane_name": "web_retrieval",
                "success_rate": 0.95,
                "timeout_rate": 0.03,
                "error_rate": 0.02,
                "avg_time": 800.0,
                "p95_time": 1200.0,
                "p99_time": 1500.0,
                "mode": "simple"
            },
            {
                "lane_name": "vector_search",
                "success_rate": 0.98,
                "timeout_rate": 0.01,
                "error_rate": 0.01,
                "avg_time": 600.0,
                "p95_time": 900.0,
                "p99_time": 1100.0,
                "mode": "technical"
            },
            {
                "lane_name": "llm_synthesis",
                "success_rate": 0.92,
                "timeout_rate": 0.05,
                "error_rate": 0.03,
                "avg_time": 1200.0,
                "p95_time": 1800.0,
                "p99_time": 2200.0,
                "mode": "research"
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases):
            try:
                print(f"  Test case {i+1}: {test_case['lane_name']} lane")
                
                response = await self.http_client.post(
                    f"{self.service_url}/metrics/lane",
                    json=test_case
                )
                
                assert response.status_code == 200
                result = response.json()
                assert result["status"] == "success"
                assert "Lane metrics recorded" in result["message"]
                
                print(f"    ✓ Lane metrics recorded for {test_case['lane_name']}")
                success_count += 1
                
            except Exception as e:
                print(f"    ✗ Test case {i+1} failed: {e}")
        
        print(f"✓ {success_count}/{len(test_cases)} lane metrics tests passed")
        return success_count == len(test_cases)
    
    async def test_guided_prompt_metrics_recording(self) -> bool:
        """Test Guided Prompt metrics recording"""
        print("\nTesting Guided Prompt Metrics Recording...")
        
        test_cases = [
            {
                "accept_rate": 0.35,
                "edit_rate": 0.45,
                "skip_rate": 0.20,
                "ttfr_ms": 450.0,
                "complaint_rate": 0.02,
                "mode": "simple"
            },
            {
                "accept_rate": 0.28,
                "edit_rate": 0.52,
                "skip_rate": 0.20,
                "ttfr_ms": 520.0,
                "complaint_rate": 0.03,
                "mode": "technical"
            },
            {
                "accept_rate": 0.25,
                "edit_rate": 0.55,
                "skip_rate": 0.20,
                "ttfr_ms": 580.0,
                "complaint_rate": 0.04,
                "mode": "research"
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases):
            try:
                print(f"  Test case {i+1}: {test_case['mode']} mode")
                
                response = await self.http_client.post(
                    f"{self.service_url}/metrics/guided-prompt",
                    json=test_case
                )
                
                assert response.status_code == 200
                result = response.json()
                assert result["status"] == "success"
                assert "Guided Prompt metrics recorded" in result["message"]
                
                print(f"    ✓ Guided Prompt metrics recorded for {test_case['mode']} mode")
                success_count += 1
                
            except Exception as e:
                print(f"    ✗ Test case {i+1} failed: {e}")
        
        print(f"✓ {success_count}/{len(test_cases)} Guided Prompt metrics tests passed")
        return success_count == len(test_cases)
    
    async def test_trace_management(self) -> bool:
        """Test trace management functionality"""
        print("\nTesting Trace Management...")
        
        try:
            # Test starting a new trace
            response = await self.http_client.post(
                f"{self.service_url}/trace/start",
                params={
                    "service_name": "test-service",
                    "request_id": "test-request-123"
                }
            )
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert "trace_context" in result
            
            trace_context = result["trace_context"]
            assert "trace_id" in trace_context
            assert "span_id" in trace_context
            assert "service_name" in trace_context
            assert "request_id" in trace_context
            
            print("    ✓ Trace creation successful")
            
            # Test creating a child span
            response = await self.http_client.post(
                f"{self.service_url}/trace/span",
                params={
                    "parent_trace_id": trace_context["trace_id"],
                    "parent_span_id": trace_context["span_id"],
                    "span_name": "child-span"
                },
                json={"test_attribute": "test_value"}
            )
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert "trace_context" in result
            
            child_context = result["trace_context"]
            assert child_context["trace_id"] == trace_context["trace_id"]
            assert child_context["parent_span_id"] == trace_context["span_id"]
            assert child_context["span_id"] != trace_context["span_id"]
            
            print("    ✓ Child span creation successful")
            print("✓ Trace management tests passed")
            return True
            
        except Exception as e:
            print(f"✗ Trace management test failed: {e}")
            return False
    
    async def test_dashboard_generation(self) -> bool:
        """Test dashboard generation"""
        print("\nTesting Dashboard Generation...")
        
        dashboards = [
            "system-health",
            "performance",
            "guided-prompt"
        ]
        
        success_count = 0
        
        for dashboard_name in dashboards:
            try:
                print(f"  Testing {dashboard_name} dashboard...")
                
                response = await self.http_client.get(f"{self.service_url}/dashboards/{dashboard_name}")
                
                assert response.status_code == 200
                dashboard = response.json()
                
                # Check dashboard structure
                assert "title" in dashboard
                assert "refresh_rate" in dashboard
                assert "layout" in dashboard
                assert "alerts" in dashboard
                
                # Check layout structure
                layout = dashboard["layout"]
                assert "rows" in layout
                assert isinstance(layout["rows"], list)
                assert len(layout["rows"]) > 0
                
                # Check alerts structure
                alerts = dashboard["alerts"]
                assert isinstance(alerts, list)
                
                print(f"    ✓ {dashboard_name} dashboard generated successfully")
                success_count += 1
                
            except Exception as e:
                print(f"    ✗ {dashboard_name} dashboard test failed: {e}")
        
        print(f"✓ {success_count}/{len(dashboards)} dashboard generation tests passed")
        return success_count == len(dashboards)
    
    async def test_prometheus_metrics(self) -> bool:
        """Test Prometheus metrics endpoint"""
        print("\nTesting Prometheus Metrics...")
        
        try:
            response = await self.http_client.get(f"{self.service_url}/metrics/prometheus")
            
            assert response.status_code == 200
            metrics_data = response.text
            
            # Check for key metrics
            assert "sarvanom_sla_global_ms" in metrics_data
            assert "sarvanom_sla_ttft_ms" in metrics_data
            assert "sarvanom_lane_success_rate" in metrics_data
            assert "sarvanom_guided_prompt_accept_rate" in metrics_data
            assert "sarvanom_trace_requests_total" in metrics_data
            
            print("✓ Prometheus metrics endpoint working correctly")
            return True
            
        except Exception as e:
            print(f"✗ Prometheus metrics test failed: {e}")
            return False
    
    async def test_metrics_aggregation(self) -> bool:
        """Test metrics aggregation and analysis"""
        print("\nTesting Metrics Aggregation...")
        
        try:
            # Record some test metrics first
            test_metrics = [
                {
                    "global_ms": 4000,
                    "ttft_ms": 1000,
                    "orchestrator_reserve_ms": 300,
                    "llm_ms": 700,
                    "web_ms": 800,
                    "vector_ms": 600,
                    "kg_ms": 750,
                    "yt_ms": 0,
                    "mode": "simple",
                    "complexity": "low"
                },
                {
                    "global_ms": 6000,
                    "ttft_ms": 1200,
                    "orchestrator_reserve_ms": 500,
                    "llm_ms": 1000,
                    "web_ms": 1100,
                    "vector_ms": 900,
                    "kg_ms": 1050,
                    "yt_ms": 0,
                    "mode": "technical",
                    "complexity": "medium"
                }
            ]
            
            # Record metrics
            for metrics in test_metrics:
                response = await self.http_client.post(
                    f"{self.service_url}/metrics/sla",
                    json=metrics
                )
                assert response.status_code == 200
            
            # Wait a moment for metrics to be processed
            await asyncio.sleep(1)
            
            # Check Prometheus metrics for aggregated data
            response = await self.http_client.get(f"{self.service_url}/metrics/prometheus")
            assert response.status_code == 200
            metrics_data = response.text
            
            # Check that metrics were recorded
            assert "sarvanom_sla_global_ms" in metrics_data
            assert "mode=\"simple\"" in metrics_data
            assert "mode=\"technical\"" in metrics_data
            
            print("✓ Metrics aggregation working correctly")
            return True
            
        except Exception as e:
            print(f"✗ Metrics aggregation test failed: {e}")
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling"""
        print("\nTesting Error Handling...")
        
        try:
            # Test invalid SLA metrics
            response = await self.http_client.post(
                f"{self.service_url}/metrics/sla",
                json={
                    "global_ms": "invalid",
                    "mode": "invalid_mode"
                }
            )
            assert response.status_code in [400, 422]
            print("    ✓ Invalid SLA metrics handled correctly")
            
            # Test invalid lane metrics
            response = await self.http_client.post(
                f"{self.service_url}/metrics/lane",
                json={
                    "lane_name": "invalid_lane",
                    "success_rate": "invalid"
                }
            )
            assert response.status_code in [400, 422]
            print("    ✓ Invalid lane metrics handled correctly")
            
            # Test invalid dashboard request
            response = await self.http_client.get(f"{self.service_url}/dashboards/invalid")
            assert response.status_code == 404
            print("    ✓ Invalid dashboard request handled correctly")
            
            print("✓ Error handling tests passed")
            return True
            
        except Exception as e:
            print(f"✗ Error handling test failed: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all tests"""
        print("Starting Observability Service Tests...")
        print("=" * 50)
        
        tests = [
            self.test_service_health,
            self.test_sla_metrics_recording,
            self.test_lane_metrics_recording,
            self.test_guided_prompt_metrics_recording,
            self.test_trace_management,
            self.test_dashboard_generation,
            self.test_prometheus_metrics,
            self.test_metrics_aggregation,
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
        print(f"SLA Metrics Recording: {'✓ PASS' if results[1] else '✗ FAIL'}")
        print(f"Lane Metrics Recording: {'✓ PASS' if results[2] else '✗ FAIL'}")
        print(f"Guided Prompt Metrics: {'✓ PASS' if results[3] else '✗ FAIL'}")
        print(f"Trace Management: {'✓ PASS' if results[4] else '✗ FAIL'}")
        print(f"Dashboard Generation: {'✓ PASS' if results[5] else '✗ FAIL'}")
        print(f"Prometheus Metrics: {'✓ PASS' if results[6] else '✗ FAIL'}")
        print(f"Metrics Aggregation: {'✓ PASS' if results[7] else '✗ FAIL'}")
        print(f"Error Handling: {'✓ PASS' if results[8] else '✗ FAIL'}")
        
        all_passed = all(results)
        print(f"\nOverall Result: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
        
        return all_passed

async def main():
    """Main test function"""
    tester = ObservabilityTester()
    
    # Wait for service to be ready
    print("Waiting for Observability service to be ready...")
    await asyncio.sleep(5)
    
    # Run tests
    success = await tester.run_all_tests()
    
    # Cleanup
    await tester.http_client.aclose()
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
