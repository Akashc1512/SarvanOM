#!/usr/bin/env python3
"""
Environment configuration verification script.
Checks if all required environment variables are set correctly.
"""

import os
import sys
from typing import Dict, List, Any

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not available. Install with: pip install python-dotenv")

def check_environment_configuration():
    """Check environment configuration for the multi-source retrieval system."""
    
    print("🔧 Environment Configuration Verification")
    print("=" * 50)
    
    # Required environment variables
    required_vars = {
        "MEILISEARCH_URL": {
            "default": "http://localhost:7700",
            "description": "Meilisearch server URL",
            "required": False
        },
        "MEILISEARCH_MASTER_KEY": {
            "default": None,
            "description": "Meilisearch master key for authentication",
            "required": False
        },
        "MEILISEARCH_API_KEY": {
            "default": None,
            "description": "Meilisearch API key",
            "required": False
        },
        "ARANGO_URL": {
            "default": "http://localhost:8529",
            "description": "ArangoDB server URL",
            "required": False
        },
        "ARANGO_USERNAME": {
            "default": "root",
            "description": "ArangoDB username",
            "required": False
        },
        "ARANGO_PASSWORD": {
            "default": "",
            "description": "ArangoDB password",
            "required": False
        },
        "ARANGO_DATABASE": {
            "default": "knowledge_graph",
            "description": "ArangoDB database name",
            "required": False
        },
        "PINECONE_API_KEY": {
            "default": None,
            "description": "Pinecone API key for vector search",
            "required": False
        },
        "PINECONE_ENVIRONMENT": {
            "default": "us-west1-gcp",
            "description": "Pinecone environment",
            "required": False
        },
        "PINECONE_INDEX_NAME": {
            "default": "knowledge-base",
            "description": "Pinecone index name",
            "required": False
        },
        "GRAPH_UPDATE_ENABLED": {
            "default": "true",
            "description": "Enable graph updates",
            "required": False
        },
        "GRAPH_AUTO_EXTRACT_ENTITIES": {
            "default": "true",
            "description": "Auto-extract entities from documents",
            "required": False
        },
        "GRAPH_CONFIDENCE_THRESHOLD": {
            "default": "0.7",
            "description": "Confidence threshold for entity extraction",
            "required": False
        },
        "GRAPH_MAX_ENTITIES_PER_DOC": {
            "default": "10",
            "description": "Maximum entities per document",
            "required": False
        },
        "GRAPH_RELATIONSHIP_TYPES": {
            "default": "is_related_to,is_part_of,is_similar_to,enables,requires",
            "description": "Comma-separated list of relationship types",
            "required": False
        }
    }
    
    # Optional environment variables
    optional_vars = {
        "SERP_API_KEY": "SerpAPI key for web search",
        "GOOGLE_API_KEY": "Google API key for web search",
        "GOOGLE_CUSTOM_SEARCH_CX": "Google Custom Search Engine ID",
        "OPENAI_API_KEY": "OpenAI API key for LLM operations",
        "ANTHROPIC_API_KEY": "Anthropic API key for LLM operations",
        "OLLAMA_BASE_URL": "Ollama base URL for local LLM",
        "LOG_LEVEL": "Logging level (INFO, DEBUG, etc.)",
        "ENVIRONMENT": "Environment (development, production, etc.)",
        "DEBUG": "Debug mode (true/false)",
        "CACHE_SIMILARITY_THRESHOLD": "Cache similarity threshold",
        "MAX_RESULTS_PER_SEARCH": "Maximum results per search",
        "DIVERSITY_THRESHOLD": "Diversity threshold for results",
        "API_HOST": "API host address",
        "API_PORT": "API port number",
        "API_WORKERS": "Number of API workers",
        "API_TIMEOUT": "API timeout in seconds",
        "SECRET_KEY": "Application secret key",
        "JWT_SECRET": "JWT secret key",
        "CORS_ORIGINS": "CORS allowed origins",
        "PROMETHEUS_ENABLED": "Enable Prometheus metrics",
        "PROMETHEUS_PORT": "Prometheus port",
        "LOG_FORMAT": "Log format (json, text)",
        "LOG_FILE": "Log file path",
        "ENABLE_GRAPH_UPDATES": "Enable graph updates feature",
        "ENABLE_REAL_TIME_SYNC": "Enable real-time synchronization",
        "ENABLE_SEMANTIC_CACHE": "Enable semantic caching",
        "ENABLE_LLM_RERANKING": "Enable LLM reranking",
        "ENABLE_DIVERSITY_FILTERING": "Enable diversity filtering"
    }
    
    print("\n📋 Required Environment Variables:")
    print("-" * 40)
    
    missing_required = []
    configured_vars = {}
    
    for var_name, config in required_vars.items():
        value = os.getenv(var_name, config["default"])
        configured_vars[var_name] = value
        
        if config["required"] and not value:
            status = "❌ MISSING"
            missing_required.append(var_name)
        elif value:
            status = "✅ SET"
        else:
            status = "⚠️ DEFAULT"
        
        print(f"{status} {var_name}: {value or 'Not set'}")
        print(f"   Description: {config['description']}")
        print()
    
    print("\n📋 Optional Environment Variables:")
    print("-" * 40)
    
    for var_name, description in optional_vars.items():
        value = os.getenv(var_name)
        configured_vars[var_name] = value
        
        if value:
            status = "✅ SET"
        else:
            status = "⚠️ NOT SET"
        
        print(f"{status} {var_name}: {value or 'Not set'}")
        print(f"   Description: {description}")
        print()
    
    # Configuration summary
    print("\n📊 Configuration Summary:")
    print("-" * 30)
    
    total_vars = len(required_vars) + len(optional_vars)
    set_vars = sum(1 for v in configured_vars.values() if v is not None)
    
    print(f"Total variables: {total_vars}")
    print(f"Set variables: {set_vars}")
    print(f"Missing required: {len(missing_required)}")
    
    if missing_required:
        print(f"❌ Missing required variables: {', '.join(missing_required)}")
    else:
        print("✅ All required variables are configured")
    
    # Service-specific checks
    print("\n🔧 Service Configuration Status:")
    print("-" * 35)
    
    # Meilisearch
    meili_url = configured_vars.get("MEILISEARCH_URL")
    meili_key = configured_vars.get("MEILISEARCH_MASTER_KEY") or configured_vars.get("MEILISEARCH_API_KEY")
    print(f"Meilisearch: {'✅ Configured' if meili_url else '❌ Not configured'}")
    print(f"  URL: {meili_url}")
    print(f"  Authentication: {'✅ Set' if meili_key else '❌ Not set'}")
    
    # ArangoDB
    arango_url = configured_vars.get("ARANGO_URL")
    arango_user = configured_vars.get("ARANGO_USERNAME")
    arango_db = configured_vars.get("ARANGO_DATABASE")
    print(f"ArangoDB: {'✅ Configured' if arango_url else '❌ Not configured'}")
    print(f"  URL: {arango_url}")
    print(f"  Database: {arango_db}")
    print(f"  Username: {arango_user}")
    
    # Pinecone
    pinecone_key = configured_vars.get("PINECONE_API_KEY")
    pinecone_env = configured_vars.get("PINECONE_ENVIRONMENT")
    print(f"Pinecone: {'✅ Configured' if pinecone_key else '❌ Not configured'}")
    print(f"  API Key: {'✅ Set' if pinecone_key else '❌ Not set'}")
    print(f"  Environment: {pinecone_env}")
    
    # Graph updates
    graph_enabled = configured_vars.get("GRAPH_UPDATE_ENABLED", "true").lower() == "true"
    print(f"Graph Updates: {'✅ Enabled' if graph_enabled else '❌ Disabled'}")
    
    # Recommendations
    print("\n💡 Recommendations:")
    print("-" * 20)
    
    if not meili_url:
        print("❌ Set MEILISEARCH_URL for keyword search functionality")
    
    if not arango_url:
        print("❌ Set ARANGO_URL for knowledge graph functionality")
    
    if not pinecone_key:
        print("⚠️ Set PINECONE_API_KEY for vector search (optional)")
    
    if not graph_enabled:
        print("⚠️ Graph updates are disabled. Set GRAPH_UPDATE_ENABLED=true to enable")
    
    if set_vars < total_vars * 0.5:
        print("⚠️ Many environment variables are not set. Consider copying from .env.example")
    
    print("\n✅ Environment configuration verification completed!")
    
    return {
        "total_vars": total_vars,
        "set_vars": set_vars,
        "missing_required": missing_required,
        "configured_vars": configured_vars
    }


async def test_service_connectivity():
    """Test connectivity to configured services."""
    print("\n🔍 Testing Service Connectivity")
    print("=" * 40)
    
    try:
        from services.search_service.retrieval_agent import RetrievalAgent
        
        print("📦 Initializing RetrievalAgent...")
        agent = RetrievalAgent()
        print("✅ RetrievalAgent initialized successfully")
        
        # Test basic functionality
        print("\n🧪 Testing basic functionality...")
        
        # Test entity extraction
        test_query = "What is machine learning?"
        entities = await agent._extract_entities(test_query)
        print(f"✅ Entity extraction: {len(entities)} entities found")
        
        # Test Meilisearch
        try:
            meili_result = await agent.meilisearch_search("test", top_k=1)
            print(f"✅ Meilisearch: {'Working' if meili_result.documents else 'No results'}")
        except Exception as e:
            print(f"❌ Meilisearch: {e}")
        
        # Test ArangoDB
        try:
            arango_result = await agent.arangodb_graph_search("test", top_k=1)
            print(f"✅ ArangoDB: {'Working' if arango_result.documents else 'No results'}")
        except Exception as e:
            print(f"❌ ArangoDB: {e}")
        
        print("\n✅ Service connectivity test completed!")
        
    except Exception as e:
        print(f"❌ Service connectivity test failed: {e}")


async def main():
    """Run environment verification."""
    print("🚀 Environment Configuration Verification")
    print("=" * 60)
    
    # Check environment configuration
    config_result = check_environment_configuration()
    
    # Test service connectivity
    await test_service_connectivity()
    
    print("\n🎉 Environment verification completed!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 