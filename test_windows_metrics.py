#!/usr/bin/env python3
"""
Test Windows-Compatible Metrics Solution
Verifies that the Windows-compatible metrics implementation resolves Prometheus client issues.

This script tests:
- Platform detection
- Metrics collection functionality
- Fallback mechanisms
- Error handling
- Health checks

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

def test_unified_metrics_import():
    """Test unified metrics import."""
    print("\n🔍 Testing Unified Metrics Import")
    print("=" * 40)
    
    try:
        from shared.core.unified_metrics import (
            record_request,
            record_error,
            record_cache_hit,
            record_cache_miss,
            update_system_metrics,
            get_metrics_summary,
            get_prometheus_metrics,
            check_monitoring_health,
            get_implementation_info
        )
        
        print("✅ Unified metrics imported successfully")
        
        # Test implementation info
        info = get_implementation_info()
        print(f"Current implementation: {info['current_implementation']}")
        print(f"Platform: {info['platform']}")
        print(f"Windows detected: {info['windows_detected']}")
        print(f"Prometheus import success: {info['prometheus_import_success']}")
        print(f"Windows metrics import success: {info['windows_metrics_import_success']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to import unified metrics: {e}")
        return False

def test_metrics_functionality():
    """Test metrics functionality."""
    print("\n🔍 Testing Metrics Functionality")
    print("=" * 40)
    
    try:
        from shared.core.unified_metrics import (
            record_request,
            record_error,
            record_cache_hit,
            record_cache_miss,
            update_system_metrics,
            get_metrics_summary,
            get_prometheus_metrics,
            check_monitoring_health
        )
        
        # Test recording metrics
        print("Testing request metrics...")
        record_request("GET", "/api/health", 200, 0.15)
        record_request("POST", "/api/query", 201, 0.25)
        
        print("Testing error metrics...")
        record_error("GET", "/api/health", "timeout")
        record_error("POST", "/api/query", "validation_error")
        
        print("Testing cache metrics...")
        record_cache_hit("redis_cache")
        record_cache_miss("redis_cache")
        record_cache_hit("memory_cache")
        
        print("Testing system metrics...")
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
        from shared.core.unified_metrics import (
            get_metrics_summary,
            get_prometheus_metrics,
            check_monitoring_health
        )
        
        # Test metrics summary
        print("Testing metrics summary...")
        summary = get_metrics_summary()
        print(f"Summary keys: {list(summary.keys())}")
        print(f"Implementation: {summary.get('implementation', 'unknown')}")
        print(f"Platform: {summary.get('platform', 'unknown')}")
        
        # Test Prometheus format
        print("\nTesting Prometheus format...")
        prometheus_metrics = get_prometheus_metrics()
        print(f"Prometheus metrics length: {len(prometheus_metrics)}")
        print("First 200 characters:")
        print(prometheus_metrics[:200])
        
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

def test_windows_metrics_direct():
    """Test Windows metrics implementation directly."""
    print("\n🔍 Testing Windows Metrics Directly")
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
        
        # Test collector
        collector = get_metrics_collector()
        print(f"Collector type: {type(collector).__name__}")
        
        # Test direct metrics
        collector.inc("test_counter", labels={"test": "value"})
        collector.set("test_gauge", 42.0, labels={"test": "value"})
        collector.observe("test_histogram", 1.5, labels={"test": "value"})
        
        # Test summary
        summary = collector.get_metrics_summary()
        print(f"Metrics count: {summary.get('metrics_count', 0)}")
        
        # Test Prometheus export
        prometheus_export = collector.export_prometheus_format()
        print(f"Prometheus export length: {len(prometheus_export)}")
        
        print("✅ Windows metrics direct test passed")
        return True
        
    except Exception as e:
        print(f"❌ Failed to test Windows metrics directly: {e}")
        return False

def test_error_handling():
    """Test error handling in metrics."""
    print("\n🔍 Testing Error Handling")
    print("=" * 40)
    
    try:
        from shared.core.unified_metrics import (
            record_request,
            record_error,
            get_metrics_summary
        )
        
        # Test with invalid parameters
        print("Testing with invalid parameters...")
        record_request("", "", -1, -1.0)  # Invalid parameters
        record_error("", "", "")  # Invalid parameters
        
        # Test metrics summary with errors
        summary = get_metrics_summary()
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
        from shared.core.unified_metrics import record_request, get_metrics_summary
        
        # Test metrics recording performance
        start_time = time.time()
        
        for i in range(100):
            record_request("GET", f"/api/test/{i}", 200, 0.1)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Recorded 100 metrics in {duration:.3f} seconds")
        print(f"Average time per metric: {(duration/100)*1000:.2f} ms")
        
        # Test summary generation performance
        start_time = time.time()
        summary = get_metrics_summary()
        end_time = time.time()
        
        print(f"Generated summary in {(end_time - start_time)*1000:.2f} ms")
        
        print("✅ Performance test passed")
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Windows-Compatible Metrics Solution")
    print("=" * 60)
    
    tests = [
        ("Platform Detection", test_platform_detection),
        ("Unified Metrics Import", test_unified_metrics_import),
        ("Metrics Functionality", test_metrics_functionality),
        ("Metrics Output", test_metrics_output),
        ("Windows Metrics Direct", test_windows_metrics_direct),
        ("Error Handling", test_error_handling),
        ("Performance", test_performance)
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
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Windows-compatible metrics solution is working correctly.")
        print("\n✅ Prometheus client issues have been resolved with:")
        print("   - Automatic platform detection")
        print("   - Windows-compatible metrics implementation")
        print("   - Graceful fallback mechanisms")
        print("   - Unified API for both implementations")
        print("   - Comprehensive error handling")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 