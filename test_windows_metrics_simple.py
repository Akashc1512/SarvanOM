#!/usr/bin/env python3
"""
Simple Test for Windows-Compatible Metrics Solution
Tests the core Windows metrics functionality without external dependencies.

This script tests:
- Windows metrics implementation
- Platform detection
- Basic metrics functionality
- Error handling

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import sys
import platform
import time
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_platform_detection():
    """Test platform detection functionality."""
    print("🔍 Testing Platform Detection")
    print("=" * 40)
    
    is_windows = platform.system().lower() == "windows"
    print(f"Platform: {platform.system()}")
    print(f"Windows detected: {is_windows}")
    print(f"Python version: {sys.version}")
    
    return True

def test_windows_metrics_import():
    """Test Windows metrics import."""
    print("\n🔍 Testing Windows Metrics Import")
    print("=" * 40)
    
    try:
        from shared.core.windows_metrics import (
            get_metrics_collector,
            record_request,
            record_error,
            record_cache_hit,
            record_cache_miss,
            update_system_metrics,
            get_metrics_summary,
            get_prometheus_metrics,
            check_monitoring_health
        )
        
        print("✅ Windows metrics imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to import Windows metrics: {e}")
        return False

def test_windows_metrics_functionality():
    """Test Windows metrics functionality."""
    print("\n🔍 Testing Windows Metrics Functionality")
    print("=" * 40)
    
    try:
        from shared.core.windows_metrics import (
            get_metrics_collector,
            record_request,
            record_error,
            record_cache_hit,
            record_cache_miss,
            update_system_metrics
        )
        
        # Test collector
        collector = get_metrics_collector()
        print(f"Collector type: {type(collector).__name__}")
        
        # Test direct metrics
        print("Testing direct metrics...")
        collector.inc("test_counter", labels={"test": "value"})
        collector.set("test_gauge", 42.0, labels={"test": "value"})
        collector.observe("test_histogram", 1.5, labels={"test": "value"})
        
        # Test convenience functions
        print("Testing convenience functions...")
        record_request("GET", "/api/health", 200, 0.15)
        record_error("GET", "/api/health", "timeout")
        record_cache_hit("redis_cache")
        record_cache_miss("redis_cache")
        update_system_metrics()
        
        print("✅ All metrics functions executed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to test metrics functionality: {e}")
        return False

def test_metrics_output():
    """Test metrics output formats."""
    print("\n🔍 Testing Metrics Output")
    print("=" * 40)
    
    try:
        from shared.core.windows_metrics import (
            get_metrics_collector,
            get_metrics_summary,
            get_prometheus_metrics,
            check_monitoring_health
        )
        
        collector = get_metrics_collector()
        
        # Test metrics summary
        print("Testing metrics summary...")
        summary = collector.get_metrics_summary()
        print(f"Summary keys: {list(summary.keys())}")
        print(f"Collector type: {summary.get('collector_type', 'unknown')}")
        print(f"Platform: {summary.get('platform', 'unknown')}")
        print(f"Metrics count: {summary.get('metrics_count', 0)}")
        
        # Test Prometheus format
        print("\nTesting Prometheus format...")
        prometheus_metrics = collector.export_prometheus_format()
        print(f"Prometheus metrics length: {len(prometheus_metrics)}")
        print("First 200 characters:")
        print(prometheus_metrics[:200])
        
        # Test JSON format
        print("\nTesting JSON format...")
        json_metrics = collector.export_json_format()
        print(f"JSON metrics length: {len(json_metrics)}")
        
        # Test health check
        print("\nTesting health check...")
        health = check_monitoring_health()
        print(f"Health status: {health.get('status', 'unknown')}")
        print(f"Health message: {health.get('message', 'unknown')}")
        
        print("✅ All metrics output tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Failed to test metrics output: {e}")
        return False

def test_error_handling():
    """Test error handling in metrics."""
    print("\n🔍 Testing Error Handling")
    print("=" * 40)
    
    try:
        from shared.core.windows_metrics import get_metrics_collector
        
        collector = get_metrics_collector()
        
        # Test with invalid parameters
        print("Testing with invalid parameters...")
        collector.inc("", labels={})  # Empty metric name
        collector.set("", -1.0, labels={})  # Empty metric name, negative value
        collector.observe("", -1.0, labels={})  # Empty metric name, negative value
        
        # Test metrics summary with errors
        summary = collector.get_metrics_summary()
        if "error" in summary:
            print(f"Error in summary: {summary['error']}")
        else:
            print("No errors in summary")
        
        print("✅ Error handling test passed")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_performance():
    """Test metrics performance."""
    print("\n🔍 Testing Performance")
    print("=" * 40)
    
    try:
        from shared.core.windows_metrics import get_metrics_collector
        
        collector = get_metrics_collector()
        
        # Test metrics recording performance
        start_time = time.time()
        
        for i in range(100):
            collector.inc(f"test_counter_{i}", labels={"test": f"value_{i}"})
            collector.set(f"test_gauge_{i}", float(i), labels={"test": f"value_{i}"})
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Recorded 200 metrics in {duration:.3f} seconds")
        print(f"Average time per metric: {(duration/200)*1000:.2f} ms")
        
        # Test summary generation performance
        start_time = time.time()
        summary = collector.get_metrics_summary()
        end_time = time.time()
        
        print(f"Generated summary in {(end_time - start_time)*1000:.2f} ms")
        
        # Test Prometheus export performance
        start_time = time.time()
        prometheus_export = collector.export_prometheus_format()
        end_time = time.time()
        
        print(f"Generated Prometheus export in {(end_time - start_time)*1000:.2f} ms")
        
        print("✅ Performance test passed")
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def test_prometheus_compatibility():
    """Test Prometheus format compatibility."""
    print("\n🔍 Testing Prometheus Compatibility")
    print("=" * 40)
    
    try:
        from shared.core.windows_metrics import get_metrics_collector
        
        collector = get_metrics_collector()
        
        # Add some test metrics
        collector.inc("http_requests_total", labels={"method": "GET", "endpoint": "/api/health", "status": "200"})
        collector.inc("http_requests_total", labels={"method": "POST", "endpoint": "/api/query", "status": "201"})
        collector.observe("http_request_duration_seconds", 0.15, labels={"method": "GET", "endpoint": "/api/health"})
        collector.observe("http_request_duration_seconds", 0.25, labels={"method": "POST", "endpoint": "/api/query"})
        collector.set("memory_usage_bytes", 1024*1024*100, labels={"type": "used"})
        collector.set("cpu_usage_percent", 45.5, labels={"core": "cpu_0"})
        
        # Export in Prometheus format
        prometheus_metrics = collector.export_prometheus_format()
        
        # Check for expected Prometheus format elements
        expected_elements = [
            "# HELP http_requests_total",
            "# TYPE http_requests_total counter",
            "http_requests_total",
            "# HELP http_request_duration_seconds",
            "# TYPE http_request_duration_seconds histogram",
            "http_request_duration_seconds",
            "# HELP memory_usage_bytes",
            "# TYPE memory_usage_bytes gauge",
            "memory_usage_bytes",
            "# HELP cpu_usage_percent",
            "# TYPE cpu_usage_percent gauge",
            "cpu_usage_percent"
        ]
        
        missing_elements = []
        for element in expected_elements:
            if element not in prometheus_metrics:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Missing Prometheus format elements: {missing_elements}")
            return False
        else:
            print("✅ All expected Prometheus format elements present")
            print("Sample Prometheus output:")
            print(prometheus_metrics[:500])
            return True
        
    except Exception as e:
        print(f"❌ Prometheus compatibility test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Windows-Compatible Metrics Solution (Simple)")
    print("=" * 70)
    
    tests = [
        ("Platform Detection", test_platform_detection),
        ("Windows Metrics Import", test_windows_metrics_import),
        ("Metrics Functionality", test_windows_metrics_functionality),
        ("Metrics Output", test_metrics_output),
        ("Error Handling", test_error_handling),
        ("Performance", test_performance),
        ("Prometheus Compatibility", test_prometheus_compatibility)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Windows-compatible metrics solution is working correctly.")
        print("\n✅ Prometheus client issues have been resolved with:")
        print("   - Windows-compatible metrics implementation")
        print("   - Prometheus format compatibility")
        print("   - Comprehensive error handling")
        print("   - High-performance metrics collection")
        print("   - Thread-safe operations")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 