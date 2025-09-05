#!/usr/bin/env python3
"""
Final Comprehensive Test - SarvanOM Backend + Docker Infrastructure
MAANG/OpenAI/Perplexity Standards Compliance
"""

import requests
import json
import time
import psycopg2
import redis
from datetime import datetime

def test_final_comprehensive():
    """Final comprehensive test of the complete system."""
    print("🚀 SARVANOM FINAL COMPREHENSIVE TEST")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Standards: MAANG/OpenAI/Perplexity Level")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    headers = {"Host": "localhost:8000"}
    
    # Test Results Tracking
    results = {
        "backend": {"passed": 0, "failed": 0, "total": 0},
        "docker": {"passed": 0, "failed": 0, "total": 0},
        "integration": {"passed": 0, "failed": 0, "total": 0}
    }
    
    def log_test(category, test_name, success, details=""):
        """Log test results."""
        results[category]["total"] += 1
        if success:
            results[category]["passed"] += 1
            print(f"✅ {test_name}")
            if details:
                print(f"   {details}")
        else:
            results[category]["failed"] += 1
            print(f"❌ {test_name}")
            if details:
                print(f"   {details}")
    
    # =============================================================================
    # 1. BACKEND API TESTING
    # =============================================================================
    print("\n🔧 1. BACKEND API TESTING")
    print("-" * 40)
    
    # Basic connectivity
    try:
        response = requests.get(f"{base_url}/", headers=headers, timeout=10)
        log_test("backend", "Root Endpoint", response.status_code == 200, 
                f"Status: {response.status_code}, Length: {len(response.text)}")
    except Exception as e:
        log_test("backend", "Root Endpoint", False, str(e))
    
    # Health endpoints
    try:
        response = requests.get(f"{base_url}/health", headers=headers, timeout=10)
        log_test("backend", "Health Check", response.status_code == 200,
                f"Status: {response.status_code}, Length: {len(response.text)}")
    except Exception as e:
        log_test("backend", "Health Check", False, str(e))
    
    try:
        response = requests.get(f"{base_url}/health/enhanced", headers=headers, timeout=10)
        log_test("backend", "Enhanced Health", response.status_code == 200,
                f"Status: {response.status_code}, Length: {len(response.text)}")
    except Exception as e:
        log_test("backend", "Enhanced Health", False, str(e))
    
    # Core functionality
    try:
        response = requests.get(f"{base_url}/search?q=test", headers=headers, timeout=10)
        log_test("backend", "Search Endpoint", response.status_code == 200,
                f"Status: {response.status_code}, Length: {len(response.text)}")
    except Exception as e:
        log_test("backend", "Search Endpoint", False, str(e))
    
    try:
        response = requests.get(f"{base_url}/providers", headers=headers, timeout=10)
        log_test("backend", "Providers Endpoint", response.status_code == 200,
                f"Status: {response.status_code}, Length: {len(response.text)}")
    except Exception as e:
        log_test("backend", "Providers Endpoint", False, str(e))
    
    try:
        response = requests.get(f"{base_url}/models", headers=headers, timeout=10)
        log_test("backend", "Models Endpoint", response.status_code == 200,
                f"Status: {response.status_code}, Length: {len(response.text)}")
    except Exception as e:
        log_test("backend", "Models Endpoint", False, str(e))
    
    # Monitoring
    try:
        response = requests.get(f"{base_url}/metrics/router", headers=headers, timeout=10)
        log_test("backend", "Router Metrics", response.status_code == 200,
                f"Status: {response.status_code}, Length: {len(response.text)}")
    except Exception as e:
        log_test("backend", "Router Metrics", False, str(e))
    
    # API Documentation
    try:
        response = requests.get(f"{base_url}/docs", headers=headers, timeout=10)
        log_test("backend", "API Documentation", response.status_code == 200,
                f"Status: {response.status_code}, Length: {len(response.text)}")
    except Exception as e:
        log_test("backend", "API Documentation", False, str(e))
    
    # =============================================================================
    # 2. DOCKER SERVICES TESTING
    # =============================================================================
    print("\n🐳 2. DOCKER SERVICES TESTING")
    print("-" * 40)
    
    # PostgreSQL
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="sarvanom",
            user="sarvanom",
            password="sarvanom123"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        log_test("docker", "PostgreSQL", True, f"Version: {version[:50]}...")
    except Exception as e:
        log_test("docker", "PostgreSQL", False, str(e))
    
    # Redis
    try:
        r = redis.Redis(host='localhost', port=6379, password='redis123', decode_responses=True)
        r.ping()
        info = r.info()
        log_test("docker", "Redis", True, f"Version: {info.get('redis_version', 'Unknown')}")
    except Exception as e:
        log_test("docker", "Redis", False, str(e))
    
    # ArangoDB
    try:
        response = requests.get("http://localhost:8529/_api/version", timeout=5)
        if response.status_code == 200:
            version = response.json()
            log_test("docker", "ArangoDB", True, f"Version: {version.get('version', 'Unknown')}")
        else:
            log_test("docker", "ArangoDB", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("docker", "ArangoDB", False, str(e))
    
    # Meilisearch
    try:
        response = requests.get("http://localhost:7700/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            log_test("docker", "Meilisearch", True, f"Status: {health.get('status', 'Unknown')}")
        else:
            log_test("docker", "Meilisearch", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("docker", "Meilisearch", False, str(e))
    
    # Qdrant
    try:
        response = requests.get("http://localhost:6333/", timeout=5)
        if response.status_code == 200:
            info = response.json()
            log_test("docker", "Qdrant", True, f"Version: {info.get('version', 'Unknown')}")
        else:
            log_test("docker", "Qdrant", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("docker", "Qdrant", False, str(e))
    
    # Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            model_count = len(models.get('models', []))
            log_test("docker", "Ollama", True, f"{model_count} models available")
        else:
            log_test("docker", "Ollama", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("docker", "Ollama", False, str(e))
    
    # MinIO
    try:
        response = requests.get("http://localhost:9000/minio/health/live", timeout=5)
        if response.status_code == 200:
            log_test("docker", "MinIO", True, "Object storage ready")
        else:
            log_test("docker", "MinIO", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("docker", "MinIO", False, str(e))
    
    # Prometheus
    try:
        response = requests.get("http://localhost:9090/-/healthy", timeout=5)
        if response.status_code == 200:
            log_test("docker", "Prometheus", True, "Monitoring ready")
        else:
            log_test("docker", "Prometheus", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("docker", "Prometheus", False, str(e))
    
    # Grafana
    try:
        response = requests.get("http://localhost:3000/api/health", timeout=5)
        if response.status_code == 200:
            log_test("docker", "Grafana", True, "Dashboard ready")
        else:
            log_test("docker", "Grafana", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("docker", "Grafana", False, str(e))
    
    # =============================================================================
    # 3. INTEGRATION TESTING
    # =============================================================================
    print("\n🔗 3. INTEGRATION TESTING")
    print("-" * 40)
    
    # Backend-Database Integration
    try:
        response = requests.get(f"{base_url}/health/database", headers=headers, timeout=10)
        log_test("integration", "Backend-Database", response.status_code == 200,
                f"Status: {response.status_code}")
    except Exception as e:
        log_test("integration", "Backend-Database", False, str(e))
    
    # Backend-Cache Integration
    try:
        response = requests.get(f"{base_url}/health/cache", headers=headers, timeout=10)
        log_test("integration", "Backend-Cache", response.status_code == 200,
                f"Status: {response.status_code}")
    except Exception as e:
        log_test("integration", "Backend-Cache", False, str(e))
    
    # Performance Test
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/health", headers=headers, timeout=10)
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        success = response.status_code == 200 and response_time < 5000  # 5 second threshold
        log_test("integration", "Performance", success,
                f"Response time: {response_time:.2f}ms")
    except Exception as e:
        log_test("integration", "Performance", False, str(e))
    
    # Error Handling
    try:
        response = requests.get(f"{base_url}/nonexistent", headers=headers, timeout=10)
        log_test("integration", "Error Handling", response.status_code == 404,
                f"Status: {response.status_code}")
    except Exception as e:
        log_test("integration", "Error Handling", False, str(e))
    
    # Security
    try:
        bad_headers = {"Host": "malicious.com:8000"}
        response = requests.get(f"{base_url}/health", headers=bad_headers, timeout=10)
        log_test("integration", "Security", response.status_code == 400,
                f"Status: {response.status_code}")
    except Exception as e:
        log_test("integration", "Security", False, str(e))
    
    # =============================================================================
    # 4. FINAL RESULTS
    # =============================================================================
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    
    total_passed = sum(cat["passed"] for cat in results.values())
    total_failed = sum(cat["failed"] for cat in results.values())
    total_tests = sum(cat["total"] for cat in results.values())
    
    print(f"🔧 Backend Tests:     {results['backend']['passed']}/{results['backend']['total']} passed")
    print(f"🐳 Docker Tests:      {results['docker']['passed']}/{results['docker']['total']} passed")
    print(f"🔗 Integration Tests: {results['integration']['passed']}/{results['integration']['total']} passed")
    print("-" * 60)
    print(f"📈 Overall:           {total_passed}/{total_tests} tests passed")
    print(f"📊 Success Rate:      {(total_passed/total_tests)*100:.1f}%")
    
    if total_failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ System is production-ready")
        print("🚀 Ready for deployment")
    else:
        print(f"\n⚠️  {total_failed} tests failed")
        print("🔧 Review failed tests before deployment")
    
    print("\n" + "=" * 60)
    print("🏆 SARVANOM COMPREHENSIVE TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_final_comprehensive()
