#!/usr/bin/env python3
"""
Final comprehensive test for all SarvanOM services.
"""

import os
import sys
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# Load environment variables
load_dotenv()

def test_all_services():
    """Test all services comprehensively."""
    print("🚀 SarvanOM Final Service Test")
    print("=" * 50)
    
    results = []
    
    # Test 1: Environment Variables
    print("\n🔍 Testing Environment Variables...")
    required_vars = ["ENVIRONMENT", "SECRET_KEY", "JWT_SECRET_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "PINECONE_API_KEY"]
    env_ok = all(os.getenv(var) for var in required_vars)
    results.append(("Environment Variables", env_ok))
    print(f"{'✅' if env_ok else '❌'} Environment Variables")
    
    # Test 2: OpenAI
    print("\n🤖 Testing OpenAI...")
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        client.models.list()
        results.append(("OpenAI", True))
        print("✅ OpenAI")
    except Exception as e:
        results.append(("OpenAI", False))
        print(f"❌ OpenAI: {e}")
    
    # Test 3: Anthropic
    print("\n🧠 Testing Anthropic...")
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        client.models.list()
        results.append(("Anthropic", True))
        print("✅ Anthropic")
    except Exception as e:
        results.append(("Anthropic", False))
        print(f"❌ Anthropic: {e}")
    
    # Test 4: Pinecone
    print("\n🌲 Testing Pinecone...")
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        pc.list_indexes()
        results.append(("Pinecone", True))
        print("✅ Pinecone")
    except Exception as e:
        results.append(("Pinecone", False))
        print(f"❌ Pinecone: {e}")
    
    # Test 5: Redis
    print("\n🔴 Testing Redis...")
    try:
        import redis
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        r.ping()
        results.append(("Redis", True))
        print("✅ Redis")
    except Exception as e:
        results.append(("Redis", False))
        print(f"❌ Redis: {e}")
    
    # Test 6: Elasticsearch
    print("\n🔍 Testing Elasticsearch...")
    try:
        cloud_url = os.getenv("ELASTICSEARCH_CLOUD_URL")
        local_url = os.getenv("ELASTICSEARCH_URL")
        es_url = cloud_url if cloud_url else local_url
        
        auth = HTTPBasicAuth(os.getenv("ELASTICSEARCH_USERNAME"), os.getenv("ELASTICSEARCH_PASSWORD"))
        response = requests.get(f"{es_url}/_cluster/health", auth=auth, timeout=10)
        
        if response.status_code == 200:
            results.append(("Elasticsearch", True))
            print("✅ Elasticsearch")
        else:
            results.append(("Elasticsearch", False))
            print(f"❌ Elasticsearch: {response.status_code}")
    except Exception as e:
        results.append(("Elasticsearch", False))
        print(f"❌ Elasticsearch: {e}")
    
    # Test 7: PostgreSQL
    print("\n🗄️ Testing PostgreSQL...")
    try:
        import psycopg2
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            conn = psycopg2.connect(db_url)
            conn.close()
            results.append(("PostgreSQL", True))
            print("✅ PostgreSQL")
        else:
            results.append(("PostgreSQL", False))
            print("❌ PostgreSQL: DATABASE_URL not set")
    except Exception as e:
        results.append(("PostgreSQL", False))
        print(f"❌ PostgreSQL: {e}")
    
    # Test 8: Email Configuration
    print("\n📧 Testing Email Configuration...")
    smtp_host = os.getenv("SMTP_HOST")
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if all([smtp_host, smtp_username, smtp_password]):
        try:
            import smtplib
            server = smtplib.SMTP(smtp_host, int(os.getenv("SMTP_PORT", "587")))
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.quit()
            results.append(("Email", True))
            print("✅ Email Configuration")
        except Exception as e:
            results.append(("Email", False))
            print(f"❌ Email Configuration: {e}")
    else:
        results.append(("Email", False))
        print("❌ Email Configuration: Incomplete setup")
    
    # Summary
    print("\n📊 Final Test Results:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for service, status in results:
        icon = "✅" if status else "❌"
        print(f"{icon} {service}")
        if status:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} services working")
    
    if passed == total:
        print("🎉 ALL SERVICES WORKING! Your SarvanOM is production-ready!")
    elif passed >= total * 0.8:
        print("✅ Most services working. Minor issues to resolve.")
    else:
        print("⚠️  Several services need attention.")
    
    return passed == total

if __name__ == "__main__":
    success = test_all_services()
    sys.exit(0 if success else 1) 