#!/usr/bin/env python3
"""
Test Docker services connectivity and functionality.
"""

import requests
import psycopg2
import redis
import time

def test_docker_services():
    """Test all Docker services."""
    print("🐳 Testing Docker Services")
    print("=" * 50)
    
    # Test PostgreSQL
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="sarvanom",
            user="postgres",
            password="sarvanom123"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL: Connected - {version[:50]}...")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ PostgreSQL: Failed - {e}")
    
    # Test Redis
    try:
        r = redis.Redis(host='localhost', port=6379, password='redis123', decode_responses=True)
        r.ping()
        info = r.info()
        print(f"✅ Redis: Connected - Version {info.get('redis_version', 'Unknown')}")
    except Exception as e:
        print(f"❌ Redis: Failed - {e}")
    
    # Test ArangoDB
    try:
        response = requests.get("http://localhost:8529/_api/version", timeout=5)
        if response.status_code == 200:
            version = response.json()
            print(f"✅ ArangoDB: Connected - Version {version.get('version', 'Unknown')}")
        else:
            print(f"❌ ArangoDB: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ ArangoDB: Failed - {e}")
    
    # Test Meilisearch
    try:
        response = requests.get("http://localhost:7700/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Meilisearch: Connected - Status {health.get('status', 'Unknown')}")
        else:
            print(f"❌ Meilisearch: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Meilisearch: Failed - {e}")
    
    # Test Qdrant
    try:
        response = requests.get("http://localhost:6333/", timeout=5)
        if response.status_code == 200:
            info = response.json()
            print(f"✅ Qdrant: Connected - Version {info.get('version', 'Unknown')}")
        else:
            print(f"❌ Qdrant: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Qdrant: Failed - {e}")
    
    # Test Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            model_count = len(models.get('models', []))
            print(f"✅ Ollama: Connected - {model_count} models available")
        else:
            print(f"❌ Ollama: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Ollama: Failed - {e}")
    
    # Test MinIO
    try:
        response = requests.get("http://localhost:9000/minio/health/live", timeout=5)
        if response.status_code == 200:
            print(f"✅ MinIO: Connected - Object storage ready")
        else:
            print(f"❌ MinIO: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ MinIO: Failed - {e}")
    
    # Test Prometheus
    try:
        response = requests.get("http://localhost:9090/-/healthy", timeout=5)
        if response.status_code == 200:
            print(f"✅ Prometheus: Connected - Monitoring ready")
        else:
            print(f"❌ Prometheus: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Prometheus: Failed - {e}")
    
    # Test Grafana
    try:
        response = requests.get("http://localhost:3000/api/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Grafana: Connected - Dashboard ready")
        else:
            print(f"❌ Grafana: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Grafana: Failed - {e}")
    
    print("\n🎯 Docker Services Test Complete")

if __name__ == "__main__":
    test_docker_services()
