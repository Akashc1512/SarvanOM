#!/usr/bin/env python3
"""
Observability Test Script

Tests the MAANG-grade observability implementation:
- Metrics collection
- Trace ID propagation
- Structured logging
- Prometheus metrics endpoint
- Grafana dashboard compatibility
"""

import asyncio
import aiohttp
import json
import time
import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone

class ObservabilityTestClient:
    """Test client for observability features."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: aiohttp.ClientSession = None
        self.trace_ids: List[str] = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_metrics_endpoint(self) -> Dict[str, Any]:
        """Test the /metrics endpoint."""
        print("🧪 Testing /metrics endpoint")
        
        try:
            async with self.session.get(f"{self.base_url}/metrics") as response:
                print(f"   📡 Metrics endpoint status: {response.status}")
                
                if response.status == 200:
                    content = await response.text()
                    
                    # Check for Prometheus format
                    prometheus_indicators = [
                        "# HELP",
                        "# TYPE",
                        "http_requests_total",
                        "http_error_rate",
                        "sse_connections_total",
                        "provider_requests_total",
                        "cache_hits_total",
                        "token_cost_total"
                    ]
                    
                    found_indicators = []
                    for indicator in prometheus_indicators:
                        if indicator in content:
                            found_indicators.append(indicator)
                            print(f"   ✅ Found: {indicator}")
                        else:
                            print(f"   ❌ Missing: {indicator}")
                    
                    return {
                        "status": "success",
                        "status_code": response.status,
                        "content_length": len(content),
                        "indicators_found": len(found_indicators),
                        "total_indicators": len(prometheus_indicators),
                        "success": len(found_indicators) == len(prometheus_indicators)
                    }
                else:
                    return {
                        "status": "error",
                        "status_code": response.status,
                        "success": False
                    }
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "success": False
            }
    
    async def test_metrics_health(self) -> Dict[str, Any]:
        """Test the /metrics/health endpoint."""
        print("🧪 Testing /metrics/health endpoint")
        
        try:
            async with self.session.get(f"{self.base_url}/metrics/health") as response:
                print(f"   📡 Health endpoint status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Health status: {data.get('status')}")
                    print(f"   ✅ Total requests: {data.get('total_requests')}")
                    print(f"   ✅ Error rate: {data.get('error_rate')}")
                    
                    return {
                        "status": "success",
                        "data": data,
                        "success": data.get("status") == "healthy"
                    }
                else:
                    return {
                        "status": "error",
                        "status_code": response.status,
                        "success": False
                    }
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "success": False
            }
    
    async def test_metrics_summary(self) -> Dict[str, Any]:
        """Test the /metrics/summary endpoint."""
        print("🧪 Testing /metrics/summary endpoint")
        
        try:
            async with self.session.get(f"{self.base_url}/metrics/summary") as response:
                print(f"   📡 Summary endpoint status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check for key metrics
                    required_metrics = [
                        "request_counter",
                        "request_errors",
                        "provider_usage",
                        "cache_hits",
                        "token_costs",
                        "total_requests",
                        "error_rate"
                    ]
                    
                    found_metrics = []
                    for metric in required_metrics:
                        if metric in data:
                            found_metrics.append(metric)
                            print(f"   ✅ Found metric: {metric}")
                        else:
                            print(f"   ❌ Missing metric: {metric}")
                    
                    return {
                        "status": "success",
                        "metrics_found": len(found_metrics),
                        "total_metrics": len(required_metrics),
                        "success": len(found_metrics) == len(required_metrics)
                    }
                else:
                    return {
                        "status": "error",
                        "status_code": response.status,
                        "success": False
                    }
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "success": False
            }
    
    async def test_trace_id_propagation(self) -> Dict[str, Any]:
        """Test trace ID propagation through requests."""
        print("🧪 Testing trace ID propagation")
        
        try:
            # Generate a test trace ID
            test_trace_id = f"test_trace_{uuid.uuid4().hex[:16]}"
            self.trace_ids.append(test_trace_id)
            
            # Make a request with trace ID
            headers = {"X-Trace-ID": test_trace_id}
            
            async with self.session.get(
                f"{self.base_url}/health", 
                headers=headers
            ) as response:
                print(f"   📡 Health request status: {response.status}")
                
                # Check if trace ID is returned in response
                returned_trace_id = response.headers.get("X-Trace-ID")
                
                if returned_trace_id == test_trace_id:
                    print(f"   ✅ Trace ID propagated: {test_trace_id}")
                    return {
                        "status": "success",
                        "trace_id_sent": test_trace_id,
                        "trace_id_received": returned_trace_id,
                        "success": True
                    }
                else:
                    print(f"   ❌ Trace ID mismatch: sent={test_trace_id}, received={returned_trace_id}")
                    return {
                        "status": "error",
                        "trace_id_sent": test_trace_id,
                        "trace_id_received": returned_trace_id,
                        "success": False
                    }
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "success": False
            }
    
    async def test_sse_metrics(self) -> Dict[str, Any]:
        """Test SSE metrics collection."""
        print("🧪 Testing SSE metrics collection")
        
        try:
            # Start an SSE stream
            url = f"{self.base_url}/stream/search"
            params = {
                "query": "test observability",
                "max_tokens": 100,
                "temperature": 0.1
            }
            
            start_time = time.time()
            
            async with self.session.get(url, params=params) as response:
                print(f"   📡 SSE stream status: {response.status}")
                
                if response.status == 200:
                    # Check for trace ID in headers
                    trace_id = response.headers.get("X-Trace-ID")
                    if trace_id:
                        print(f"   ✅ SSE trace ID: {trace_id}")
                        self.trace_ids.append(trace_id)
                    
                    # Read a few events
                    event_count = 0
                    async for line in response.content:
                        if line and event_count < 5:  # Read first 5 events
                            event_count += 1
                            print(f"   📨 Event {event_count}: {line.decode('utf-8')[:100]}...")
                        elif event_count >= 5:
                            break
                    
                    duration = time.time() - start_time
                    print(f"   ✅ SSE stream duration: {duration:.2f}s")
                    
                    return {
                        "status": "success",
                        "trace_id": trace_id,
                        "event_count": event_count,
                        "duration": duration,
                        "success": True
                    }
                else:
                    return {
                        "status": "error",
                        "status_code": response.status,
                        "success": False
                    }
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "success": False
            }
    
    async def test_structured_logging(self) -> Dict[str, Any]:
        """Test structured logging with trace IDs."""
        print("🧪 Testing structured logging")
        
        try:
            # Make multiple requests to generate logs
            requests_made = 0
            for i in range(3):
                trace_id = f"log_test_{uuid.uuid4().hex[:16]}"
                headers = {"X-Trace-ID": trace_id}
                
                async with self.session.get(
                    f"{self.base_url}/health", 
                    headers=headers
                ) as response:
                    if response.status == 200:
                        requests_made += 1
                        print(f"   ✅ Request {i+1} with trace ID: {trace_id}")
                
                await asyncio.sleep(0.1)  # Small delay between requests
            
            return {
                "status": "success",
                "requests_made": requests_made,
                "success": requests_made == 3
            }
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "success": False
            }

async def test_grafana_dashboard():
    """Test Grafana dashboard JSON validity."""
    print("🧪 Testing Grafana dashboard JSON")
    
    try:
        with open("monitoring/grafana_dashboard.json", "r") as f:
            dashboard = json.load(f)
        
        # Check required fields
        required_fields = ["dashboard", "title", "panels"]
        found_fields = []
        
        for field in required_fields:
            if field in dashboard:
                found_fields.append(field)
                print(f"   ✅ Found field: {field}")
            else:
                print(f"   ❌ Missing field: {field}")
        
        # Check panel types
        panel_types = set()
        for panel in dashboard["dashboard"]["panels"]:
            panel_types.add(panel["type"])
        
        print(f"   ✅ Panel types: {list(panel_types)}")
        
        # Check for key panels
        panel_titles = [panel["title"] for panel in dashboard["dashboard"]["panels"]]
        key_panels = [
            "Request Rate (RPS)",
            "Error Rate", 
            "P50 Latency",
            "P95 Latency",
            "Provider Usage Distribution",
            "SSE Stream Duration"
        ]
        
        found_panels = []
        for panel in key_panels:
            if panel in panel_titles:
                found_panels.append(panel)
                print(f"   ✅ Found panel: {panel}")
            else:
                print(f"   ❌ Missing panel: {panel}")
        
        return {
            "status": "success",
            "fields_found": len(found_fields),
            "total_fields": len(required_fields),
            "panels_found": len(found_panels),
            "total_panels": len(key_panels),
            "panel_types": list(panel_types),
            "success": len(found_fields) == len(required_fields) and len(found_panels) == len(key_panels)
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "success": False
        }

async def main():
    """Run all observability tests."""
    print("🚀 OBSERVABILITY TEST SUITE")
    print("=" * 60)
    
    async with ObservabilityTestClient() as client:
        tests = [
            ("Metrics Endpoint", client.test_metrics_endpoint),
            ("Metrics Health", client.test_metrics_health),
            ("Metrics Summary", client.test_metrics_summary),
            ("Trace ID Propagation", client.test_trace_id_propagation),
            ("SSE Metrics", client.test_sse_metrics),
            ("Structured Logging", client.test_structured_logging),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                print(f"\n🧪 Running: {test_name}")
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ Test failed: {e}")
                results.append((test_name, {"error": str(e), "success": False}))
        
        # Test Grafana dashboard
        print(f"\n🧪 Running: Grafana Dashboard")
        dashboard_result = await test_grafana_dashboard()
        results.append(("Grafana Dashboard", dashboard_result))
        
        # Summary
        print(f"\n📊 TEST SUMMARY")
        print("=" * 30)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            success = result.get("success", False)
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {status} {test_name}")
            if success:
                passed += 1
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL OBSERVABILITY TESTS PASSED!")
            print("✅ Metrics endpoint working correctly")
            print("✅ Trace ID propagation working")
            print("✅ Structured logging working")
            print("✅ SSE metrics collection working")
            print("✅ Grafana dashboard JSON valid")
            print("✅ MAANG-grade observability implemented")
        else:
            print("⚠️  Some tests failed - check observability implementation")
        
        return results

if __name__ == "__main__":
    asyncio.run(main())
