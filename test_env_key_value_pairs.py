#!/usr/bin/env python3
"""
Test script to verify all key-value pairs in .env file are working correctly.
"""

import os
import sys
import asyncio
from typing import Dict, List, Any, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_llm_configuration() -> Dict[str, Any]:
    """Test LLM configuration variables."""
    print("🔧 Testing LLM Configuration...")
    
    results = {}
    
    # Ollama Configuration
    ollama_enabled = os.getenv("OLLAMA_ENABLED", "false").lower() == "true"
    ollama_model = os.getenv("OLLAMA_MODEL")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL")
    
    results["ollama"] = {
        "enabled": ollama_enabled,
        "model": ollama_model,
        "base_url": ollama_base_url,
        "status": "✅ Configured" if ollama_enabled and ollama_model else "❌ Not configured"
    }
    
    # Hugging Face Configuration
    hf_write_token = os.getenv("HUGGINGFACE_WRITE_TOKEN")
    hf_read_token = os.getenv("HUGGINGFACE_READ_TOKEN")
    hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
    hf_model = os.getenv("HUGGINGFACE_MODEL")
    
    results["huggingface"] = {
        "write_token": "✅ Set" if hf_write_token else "❌ Not set",
        "read_token": "✅ Set" if hf_read_token else "❌ Not set",
        "api_key": "✅ Set" if hf_api_key else "❌ Not set",
        "model": hf_model,
        "status": "✅ Configured" if any([hf_write_token, hf_read_token, hf_api_key]) else "❌ Not configured"
    }
    
    # OpenAI Configuration
    openai_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_LLM_MODEL")
    
    results["openai"] = {
        "api_key": "✅ Set" if openai_key and openai_key != "test-key" else "❌ Not set or test key",
        "model": openai_model,
        "status": "✅ Configured" if openai_key and openai_key != "test-key" else "❌ Not configured"
    }
    
    # Anthropic Configuration
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    anthropic_model = os.getenv("ANTHROPIC_MODEL")
    
    results["anthropic"] = {
        "api_key": "✅ Set" if anthropic_key and anthropic_key != "test-key" else "❌ Not set or test key",
        "model": anthropic_model,
        "status": "✅ Configured" if anthropic_key and anthropic_key != "test-key" else "❌ Not configured"
    }
    
    # Model Selection Configuration
    use_dynamic = os.getenv("USE_DYNAMIC_SELECTION", "false").lower() == "true"
    prioritize_free = os.getenv("PRIORITIZE_FREE_MODELS", "false").lower() == "true"
    
    results["model_selection"] = {
        "dynamic_selection": "✅ Enabled" if use_dynamic else "❌ Disabled",
        "prioritize_free": "✅ Enabled" if prioritize_free else "❌ Disabled"
    }
    
    return results


def test_database_configuration() -> Dict[str, Any]:
    """Test database configuration variables."""
    print("🗄️ Testing Database Configuration...")
    
    results = {}
    
    # PostgreSQL Configuration
    postgres_host = os.getenv("POSTGRES_HOST")
    postgres_port = os.getenv("POSTGRES_PORT")
    postgres_db = os.getenv("POSTGRES_DB")
    postgres_user = os.getenv("POSTGRES_USER")
    postgres_password = os.getenv("POSTGRES_PASSWORD")
    
    results["postgresql"] = {
        "host": postgres_host,
        "port": postgres_port,
        "database": postgres_db,
        "user": postgres_user,
        "password": "✅ Set" if postgres_password else "❌ Not set",
        "status": "✅ Configured" if all([postgres_host, postgres_db, postgres_user]) else "❌ Not configured"
    }
    
    # SQLite Configuration
    database_url = os.getenv("DATABASE_URL")
    results["sqlite"] = {
        "database_url": database_url,
        "status": "✅ Configured" if database_url else "❌ Not configured"
    }
    
    return results


def test_vector_database_configuration() -> Dict[str, Any]:
    """Test vector database configuration variables."""
    print("🔍 Testing Vector Database Configuration...")
    
    results = {}
    
    # Qdrant Configuration
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_collection = os.getenv("QDRANT_COLLECTION")
    
    results["qdrant"] = {
        "url": qdrant_url,
        "collection": qdrant_collection,
        "status": "✅ Configured" if qdrant_url else "❌ Not configured"
    }
    
    # Pinecone Configuration
    pinecone_key = os.getenv("PINECONE_API_KEY")
    pinecone_env = os.getenv("PINECONE_ENVIRONMENT")
    pinecone_index = os.getenv("PINECONE_INDEX_NAME")
    
    results["pinecone"] = {
        "api_key": "✅ Set" if pinecone_key else "❌ Not set",
        "environment": pinecone_env,
        "index_name": pinecone_index,
        "status": "✅ Configured" if pinecone_key else "❌ Not configured"
    }
    
    return results


def test_search_configuration() -> Dict[str, Any]:
    """Test search configuration variables."""
    print("🔎 Testing Search Configuration...")
    
    results = {}
    
    # Meilisearch Configuration
    meili_url = os.getenv("MEILISEARCH_URL")
    meili_master_key = os.getenv("MEILI_MASTER_KEY")
    
    results["meilisearch"] = {
        "url": meili_url,
        "master_key": "✅ Set" if meili_master_key else "❌ Not set",
        "status": "✅ Configured" if meili_url else "❌ Not configured"
    }
    
    # ArangoDB Configuration
    arango_url = os.getenv("ARANGO_URL")
    arango_user = os.getenv("ARANGO_USER")
    arango_pass = os.getenv("ARANGO_PASS")
    arango_db = os.getenv("ARANGO_DB")
    
    results["arangodb"] = {
        "url": arango_url,
        "user": arango_user,
        "password": "✅ Set" if arango_pass else "❌ Not set",
        "database": arango_db,
        "status": "✅ Configured" if all([arango_url, arango_user, arango_db]) else "❌ Not configured"
    }
    
    # Knowledge Graph Configuration
    sparql_endpoint = os.getenv("SPARQL_ENDPOINT")
    
    results["knowledge_graph"] = {
        "sparql_endpoint": sparql_endpoint,
        "status": "✅ Configured" if sparql_endpoint else "❌ Not configured"
    }
    
    return results


def test_system_configuration() -> Dict[str, Any]:
    """Test system configuration variables."""
    print("⚙️ Testing System Configuration...")
    
    results = {}
    
    # Environment and Logging
    environment = os.getenv("ENVIRONMENT")
    log_level = os.getenv("LOG_LEVEL")
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    results["system"] = {
        "environment": environment,
        "log_level": log_level,
        "debug": "✅ Enabled" if debug else "❌ Disabled",
        "status": "✅ Configured"
    }
    
    # Security Configuration
    secret_key = os.getenv("SECRET_KEY")
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    jwt_algorithm = os.getenv("JWT_ALGORITHM")
    
    results["security"] = {
        "secret_key": "✅ Set" if secret_key else "❌ Not set",
        "jwt_secret": "✅ Set" if jwt_secret else "❌ Not set",
        "jwt_algorithm": jwt_algorithm,
        "status": "✅ Configured" if secret_key and jwt_secret else "❌ Not configured"
    }
    
    # CORS Configuration
    cors_origins = os.getenv("CORS_ORIGINS")
    cors_allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"
    
    results["cors"] = {
        "origins": cors_origins,
        "allow_credentials": "✅ Enabled" if cors_allow_credentials else "❌ Disabled",
        "status": "✅ Configured" if cors_origins else "❌ Not configured"
    }
    
    return results


def test_monitoring_configuration() -> Dict[str, Any]:
    """Test monitoring configuration variables."""
    print("📊 Testing Monitoring Configuration...")
    
    results = {}
    
    # Prometheus Configuration
    prometheus_enabled = os.getenv("PROMETHEUS_ENABLED", "false").lower() == "true"
    prometheus_port = os.getenv("PROMETHEUS_PORT")
    
    results["prometheus"] = {
        "enabled": "✅ Enabled" if prometheus_enabled else "❌ Disabled",
        "port": prometheus_port,
        "status": "✅ Configured" if prometheus_enabled else "❌ Not configured"
    }
    
    # Grafana Configuration
    grafana_enabled = os.getenv("GRAFANA_ENABLED", "false").lower() == "true"
    grafana_port = os.getenv("GRAFANA_PORT")
    
    results["grafana"] = {
        "enabled": "✅ Enabled" if grafana_enabled else "❌ Disabled",
        "port": grafana_port,
        "status": "✅ Configured" if grafana_enabled else "❌ Not configured"
    }
    
    # Logging Configuration
    log_format = os.getenv("LOG_FORMAT")
    log_level_root = os.getenv("LOG_LEVEL_ROOT")
    log_level_services = os.getenv("LOG_LEVEL_SERVICES")
    
    results["logging"] = {
        "format": log_format,
        "level_root": log_level_root,
        "level_services": log_level_services,
        "status": "✅ Configured" if log_format else "❌ Not configured"
    }
    
    return results


def test_api_configuration() -> Dict[str, Any]:
    """Test API configuration variables."""
    print("🌐 Testing API Configuration...")
    
    results = {}
    
    # API Gateway Configuration
    api_gateway_port = os.getenv("API_GATEWAY_PORT")
    api_gateway_host = os.getenv("API_GATEWAY_HOST")
    
    results["api_gateway"] = {
        "port": api_gateway_port,
        "host": api_gateway_host,
        "status": "✅ Configured" if api_gateway_port else "❌ Not configured"
    }
    
    # Rate Limiting Configuration
    rate_limit_requests = os.getenv("RATE_LIMIT_REQUESTS")
    rate_limit_tokens = os.getenv("RATE_LIMIT_TOKENS")
    rate_limit_window = os.getenv("RATE_LIMIT_WINDOW")
    
    results["rate_limiting"] = {
        "requests": rate_limit_requests,
        "tokens": rate_limit_tokens,
        "window": rate_limit_window,
        "status": "✅ Configured" if rate_limit_requests else "❌ Not configured"
    }
    
    return results


def test_cache_configuration() -> Dict[str, Any]:
    """Test cache configuration variables."""
    print("💾 Testing Cache Configuration...")
    
    results = {}
    
    # Redis Configuration
    redis_url = os.getenv("REDIS_URL")
    redis_db = os.getenv("REDIS_DB")
    
    results["redis"] = {
        "url": redis_url,
        "database": redis_db,
        "status": "✅ Configured" if redis_url else "❌ Not configured"
    }
    
    return results


def test_development_configuration() -> Dict[str, Any]:
    """Test development configuration variables."""
    print("🛠️ Testing Development Configuration...")
    
    results = {}
    
    # Development Settings
    mock_ai_responses = os.getenv("MOCK_AI_RESPONSES", "false").lower() == "true"
    skip_authentication = os.getenv("SKIP_AUTHENTICATION", "false").lower() == "true"
    enable_debug_endpoints = os.getenv("ENABLE_DEBUG_ENDPOINTS", "false").lower() == "true"
    auto_reload = os.getenv("AUTO_RELOAD", "false").lower() == "true"
    test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
    mock_providers = os.getenv("MOCK_PROVIDERS", "false").lower() == "true"
    
    results["development"] = {
        "mock_ai_responses": "✅ Enabled" if mock_ai_responses else "❌ Disabled",
        "skip_authentication": "✅ Enabled" if skip_authentication else "❌ Disabled",
        "enable_debug_endpoints": "✅ Enabled" if enable_debug_endpoints else "❌ Disabled",
        "auto_reload": "✅ Enabled" if auto_reload else "❌ Disabled",
        "test_mode": "✅ Enabled" if test_mode else "❌ Disabled",
        "mock_providers": "✅ Enabled" if mock_providers else "❌ Disabled"
    }
    
    return results


async def test_service_connectivity() -> Dict[str, Any]:
    """Test connectivity to configured services."""
    print("🔗 Testing Service Connectivity...")
    
    results = {}
    
    try:
        from services.search_service.retrieval_agent import RetrievalAgent
        
        print("📦 Initializing RetrievalAgent...")
        agent = RetrievalAgent()
        
        # Test Meilisearch
        try:
            meili_result = await agent.meilisearch_search("test", top_k=1)
            results["meilisearch_connectivity"] = {
                "status": "✅ Connected",
                "details": f"Found {len(meili_result.documents)} results"
            }
        except Exception as e:
            results["meilisearch_connectivity"] = {
                "status": "❌ Connection failed",
                "details": str(e)
            }
        
        # Test ArangoDB
        try:
            arango_result = await agent.arangodb_graph_search("test", top_k=1)
            results["arangodb_connectivity"] = {
                "status": "✅ Connected",
                "details": f"Found {len(arango_result.documents)} results"
            }
        except Exception as e:
            results["arangodb_connectivity"] = {
                "status": "❌ Connection failed",
                "details": str(e)
            }
        
        # Test Vector Search
        try:
            vector_result = await agent.vector_search("test", top_k=1)
            results["vector_search_connectivity"] = {
                "status": "✅ Connected",
                "details": f"Found {len(vector_result.documents)} results"
            }
        except Exception as e:
            results["vector_search_connectivity"] = {
                "status": "❌ Connection failed",
                "details": str(e)
            }
        
    except Exception as e:
        results["retrieval_agent"] = {
            "status": "❌ Initialization failed",
            "details": str(e)
        }
    
    return results


def print_results(results: Dict[str, Any], title: str):
    """Print test results in a formatted way."""
    print(f"\n📋 {title}")
    print("=" * 50)
    
    for category, config in results.items():
        print(f"\n🔹 {category.upper()}:")
        for key, value in config.items():
            if key != "status":
                print(f"   {key}: {value}")
        print(f"   Status: {config.get('status', '❓ Unknown')}")


async def main():
    """Run comprehensive environment variable testing."""
    print("🚀 Environment Variable Testing")
    print("=" * 60)
    
    # Test all configurations
    llm_results = test_llm_configuration()
    db_results = test_database_configuration()
    vector_results = test_vector_database_configuration()
    search_results = test_search_configuration()
    system_results = test_system_configuration()
    monitoring_results = test_monitoring_configuration()
    api_results = test_api_configuration()
    cache_results = test_cache_configuration()
    dev_results = test_development_configuration()
    
    # Test service connectivity
    connectivity_results = await test_service_connectivity()
    
    # Print all results
    print_results(llm_results, "LLM Configuration")
    print_results(db_results, "Database Configuration")
    print_results(vector_results, "Vector Database Configuration")
    print_results(search_results, "Search Configuration")
    print_results(system_results, "System Configuration")
    print_results(monitoring_results, "Monitoring Configuration")
    print_results(api_results, "API Configuration")
    print_results(cache_results, "Cache Configuration")
    print_results(dev_results, "Development Configuration")
    print_results(connectivity_results, "Service Connectivity")
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 30)
    
    all_results = {
        "LLM": llm_results,
        "Database": db_results,
        "Vector DB": vector_results,
        "Search": search_results,
        "System": system_results,
        "Monitoring": monitoring_results,
        "API": api_results,
        "Cache": cache_results,
        "Development": dev_results,
        "Connectivity": connectivity_results
    }
    
    total_configs = 0
    working_configs = 0
    
    for category, results in all_results.items():
        for subcategory, config in results.items():
            total_configs += 1
            if config.get("status", "").startswith("✅"):
                working_configs += 1
    
    print(f"Total configurations: {total_configs}")
    print(f"Working configurations: {working_configs}")
    print(f"Success rate: {(working_configs/total_configs)*100:.1f}%" if total_configs > 0 else "No configurations found")
    
    print("\n🎉 Environment variable testing completed!")


if __name__ == "__main__":
    asyncio.run(main()) 