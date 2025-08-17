#!/usr/bin/env python3
"""
Comprehensive Backend Components Test
MAANG/OpenAI/Perplexity Standards Implementation
Tests ALL components with latest stable versions as of August 16, 2025
"""

import os
import asyncio
import json
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_all_components():
    """Test ALL backend components comprehensively"""
    
    print("🔥 COMPREHENSIVE BACKEND COMPONENTS TEST")
    print("=" * 70)
    print("📋 MAANG/OpenAI/Perplexity Standards - August 16, 2025")
    print("🎯 Testing ALL Components for Production Readiness")
    print()
    
    # Test environment variables
    print("🔐 ENVIRONMENT VARIABLES:")
    print("=" * 40)
    await test_environment_variables()
    
    # Test database connections
    print("\n🗄️ DATABASE CONNECTIONS:")
    print("=" * 40)
    await test_database_connections()
    
    # Test vector databases
    print("\n🔍 VECTOR DATABASES:")
    print("=" * 40)
    await test_vector_databases()
    
    # Test search engines
    print("\n🔎 SEARCH ENGINES:")
    print("=" * 40)
    await test_search_engines()
    
    # Test LLM providers
    print("\n🤖 LLM PROVIDERS:")
    print("=" * 40)
    await test_llm_providers()
    
    # Test embeddings
    print("\n📊 EMBEDDINGS:")
    print("=" * 40)
    await test_embeddings()
    
    # Test caching
    print("\n⚡ CACHING:")
    print("=" * 40)
    await test_caching()
    
    # Test API endpoints
    print("\n🌐 API ENDPOINTS:")
    print("=" * 40)
    await test_api_endpoints()
    
    print("\n✅ ALL COMPONENTS TESTED!")
    print("🎉 PRODUCTION READINESS ASSESSMENT COMPLETE!")

async def test_environment_variables():
    """Test environment variable configuration"""
    try:
        # Core variables
        core_vars = [
            "HUGGINGFACE_API_KEY",
            "MEILI_MASTER_KEY",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY"
        ]
        
        for var in core_vars:
            value = os.getenv(var)
            status = "✅ SET" if value and value != "your_*_here" else "❌ MISSING"
            preview = f"({value[:10]}...)" if value and value != "your_*_here" else ""
            print(f"   {var}: {status} {preview}")
        
        # Database URLs
        db_vars = [
            "DATABASE_URL",
            "REDIS_URL",
            "QDRANT_URL",
            "MEILISEARCH_URL",
            "ARANGODB_URL"
        ]
        
        for var in db_vars:
            value = os.getenv(var)
            status = "✅ SET" if value else "❌ MISSING"
            print(f"   {var}: {status}")
        
        # Feature flags
        feature_vars = [
            "USE_DYNAMIC_SELECTION",
            "PRIORITIZE_FREE_MODELS",
            "MOCK_AI_RESPONSES"
        ]
        
        for var in feature_vars:
            value = os.getenv(var)
            status = "✅ SET" if value else "⚠️ DEFAULT"
            print(f"   {var}: {status} ({value or 'false'})")
            
    except Exception as e:
        print(f"   ❌ Environment test failed: {e}")

async def test_database_connections():
    """Test database connections"""
    try:
        # PostgreSQL
        print("   🐘 PostgreSQL:")
        postgres_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/sarvanom")
        if "localhost" in postgres_url:
            try:
                import psycopg2
                conn = psycopg2.connect(postgres_url)
                conn.close()
                print("      ✅ Connection successful")
            except Exception as e:
                print(f"      ❌ Connection failed: {e}")
        else:
            print("      ⚠️ Using external database")
        
        # Redis
        print("   🔴 Redis:")
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        if "localhost" in redis_url:
            try:
                import redis
                r = redis.from_url(redis_url)
                r.ping()
                print("      ✅ Connection successful")
            except Exception as e:
                print(f"      ❌ Connection failed: {e}")
        else:
            print("      ⚠️ Using external Redis")
            
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")

async def test_vector_databases():
    """Test vector database connections"""
    try:
        # Qdrant
        print("   🎯 Qdrant:")
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        try:
            response = requests.get(f"{qdrant_url}/health", timeout=5)
            if response.status_code == 200:
                print("      ✅ Connection successful")
                version = response.json().get("version", "Unknown")
                print(f"      📊 Version: {version}")
            else:
                print(f"      ❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"      ❌ Connection failed: {e}")
        
        # ArangoDB
        print("   🌐 ArangoDB:")
        arango_url = os.getenv("ARANGODB_URL", "http://localhost:8529")
        try:
            response = requests.get(f"{arango_url}/_api/version", timeout=5)
            if response.status_code == 200:
                print("      ✅ Connection successful")
                version = response.json().get("version", "Unknown")
                print(f"      📊 Version: {version}")
            else:
                print(f"      ❌ Version check failed: {response.status_code}")
        except Exception as e:
            print(f"      ❌ Connection failed: {e}")
            
    except Exception as e:
        print(f"   ❌ Vector database test failed: {e}")

async def test_search_engines():
    """Test search engine connections"""
    try:
        # Meilisearch
        print("   🔍 Meilisearch:")
        meili_url = os.getenv("MEILISEARCH_URL", "http://localhost:7700")
        try:
            response = requests.get(f"{meili_url}/version", timeout=5)
            if response.status_code == 200:
                print("      ✅ Connection successful")
                version = response.json().get("pkgVersion", "Unknown")
                print(f"      📊 Version: {version}")
            else:
                print(f"      ❌ Version check failed: {response.status_code}")
        except Exception as e:
            print(f"      ❌ Connection failed: {e}")
            
    except Exception as e:
        print(f"   ❌ Search engine test failed: {e}")

async def test_llm_providers():
    """Test LLM provider connections"""
    try:
        # Ollama
        print("   🤖 Ollama:")
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        try:
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                print("      ✅ Connection successful")
                models = response.json().get("models", [])
                print(f"      📊 Models available: {len(models)}")
                for model in models[:3]:  # Show first 3
                    print(f"         - {model.get('name', 'Unknown')}")
            else:
                print(f"      ❌ Models check failed: {response.status_code}")
        except Exception as e:
            print(f"      ❌ Connection failed: {e}")
        
        # HuggingFace
        print("   🤗 HuggingFace:")
        hf_token = os.getenv("HUGGINGFACE_API_KEY")
        if hf_token and hf_token != "your_*_here":
            try:
                headers = {"Authorization": f"Bearer {hf_token}"}
                response = requests.get("https://huggingface.co/api/whoami", headers=headers, timeout=10)
                if response.status_code == 200:
                    print("      ✅ Authentication successful")
                    user_info = response.json()
                    print(f"      👤 User: {user_info.get('name', 'Unknown')}")
                else:
                    print(f"      ❌ Authentication failed: {response.status_code}")
            except Exception as e:
                print(f"      ❌ Connection failed: {e}")
        else:
            print("      ⚠️ No API token configured")
            
    except Exception as e:
        print(f"   ❌ LLM provider test failed: {e}")

async def test_embeddings():
    """Test embedding functionality"""
    try:
        print("   📊 Testing Embeddings:")
        
        # Test HuggingFace embeddings
        try:
            from services.gateway.huggingface_integration import HuggingFaceIntegration
            
            hf_integration = HuggingFaceIntegration()
            await hf_integration.initialize()
            
            texts = ["Test embedding", "Another test"]
            response = await hf_integration.get_embeddings(texts)
            
            print("      ✅ HuggingFace embeddings working")
            print(f"      📊 Vector dimensions: {len(response.result[0])}")
            print(f"      ⏱️ Processing time: {response.processing_time:.2f}s")
            
        except Exception as e:
            print(f"      ❌ HuggingFace embeddings failed: {e}")
            
    except Exception as e:
        print(f"   ❌ Embeddings test failed: {e}")

async def test_caching():
    """Test caching functionality"""
    try:
        print("   ⚡ Testing Caching:")
        
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        if "localhost" in redis_url:
            try:
                import redis
                r = redis.from_url(redis_url)
                
                # Test basic operations
                r.set("test_key", "test_value", ex=60)
                value = r.get("test_key")
                r.delete("test_key")
                
                if value == b"test_value":
                    print("      ✅ Redis caching working")
                else:
                    print("      ❌ Redis caching failed")
                    
            except Exception as e:
                print(f"      ❌ Redis test failed: {e}")
        else:
            print("      ⚠️ Using external Redis")
            
    except Exception as e:
        print(f"   ❌ Caching test failed: {e}")

async def test_api_endpoints():
    """Test API endpoints"""
    try:
        print("   🌐 Testing API Endpoints:")
        
        # Test backend health
        backend_urls = [
            "http://localhost:8000",
            "http://localhost:8001", 
            "http://localhost:8002",
            "http://localhost:8003",
            "http://localhost:8004",
            "http://localhost:8005",
            "http://localhost:8006"
        ]
        
        for url in backend_urls:
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"      ✅ {url}/health - OK")
                else:
                    print(f"      ⚠️ {url}/health - {response.status_code}")
            except Exception as e:
                print(f"      ❌ {url}/health - Connection failed")
        
        # Test search endpoint
        try:
            search_url = "http://localhost:8005/search"
            payload = {
                "query": "test query",
                "provider": "huggingface"
            }
            response = requests.post(search_url, json=payload, timeout=30)
            if response.status_code == 200:
                print("      ✅ Search endpoint working")
            else:
                print(f"      ⚠️ Search endpoint: {response.status_code}")
        except Exception as e:
            print(f"      ❌ Search endpoint failed: {e}")
            
    except Exception as e:
        print(f"   ❌ API endpoint test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_all_components())

