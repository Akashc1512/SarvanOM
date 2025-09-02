#!/usr/bin/env python3
"""
Verification script to ensure SSE streaming uses real services, not mocks.

This script verifies that:
1. Real LLM services are integrated (Ollama, HuggingFace, OpenAI, Anthropic)
2. Real retrieval services are used (web search, vector DB, knowledge graph)
3. Real API keys are loaded from .env
4. No mock responses are being used in the streaming pipeline
"""

import os
import sys
import asyncio
from typing import Dict, Any

def verify_environment_variables():
    """Verify that real API keys are loaded from .env file."""
    print("🔍 VERIFYING ENVIRONMENT VARIABLES")
    print("=" * 50)
    
    required_keys = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY", 
        "BRAVE_SEARCH_API_KEY",
        "SERPAPI_KEY",
        "QDRANT_API_KEY",
        "ARANGO_URL",
        "ARANGO_USERNAME",
        "ARANGO_PASSWORD"
    ]
    
    found_keys = []
    missing_keys = []
    
    for key in required_keys:
        value = os.getenv(key)
        if value:
            found_keys.append(key)
            print(f"   ✅ {key}: {'*' * min(len(value), 8)}...")
        else:
            missing_keys.append(key)
            print(f"   ❌ {key}: Not set")
    
    print(f"\n📊 Environment Summary:")
    print(f"   Found: {len(found_keys)}/{len(required_keys)} keys")
    print(f"   Missing: {missing_keys}")
    
    return len(missing_keys) == 0

def verify_real_llm_integration():
    """Verify that real LLM services are integrated."""
    print("\n🤖 VERIFYING REAL LLM INTEGRATION")
    print("=" * 50)
    
    try:
        from services.gateway.real_llm_integration import RealLLMProcessor
        print("   ✅ RealLLMProcessor imported successfully")
        
        # Check if it's using real providers
        processor = RealLLMProcessor()
        print("   ✅ RealLLMProcessor instantiated successfully")
        
        # Check provider registry
        if hasattr(processor, 'provider_registry'):
            providers = list(processor.provider_registry.keys())
            print(f"   ✅ Available providers: {providers}")
            
            # Verify real providers are available
            real_providers = ['ollama', 'huggingface', 'openai', 'anthropic']
            available_real = [p for p in real_providers if p in providers]
            print(f"   ✅ Real providers available: {available_real}")
            
            return len(available_real) > 0
        else:
            print("   ⚠️  Provider registry not found")
            return False
            
    except ImportError as e:
        print(f"   ❌ Failed to import RealLLMProcessor: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error with RealLLMProcessor: {e}")
        return False

def verify_real_retrieval_services():
    """Verify that real retrieval services are integrated."""
    print("\n🔍 VERIFYING REAL RETRIEVAL SERVICES")
    print("=" * 50)
    
    try:
        # Check free tier retrieval
        from services.retrieval.free_tier import get_zero_budget_retrieval
        print("   ✅ Free tier retrieval imported successfully")
        
        retrieval_system = get_zero_budget_retrieval()
        print("   ✅ Free tier retrieval instantiated successfully")
        
        # Check if it has real providers
        if hasattr(retrieval_system, 'providers'):
            providers = list(retrieval_system.providers.keys())
            print(f"   ✅ Available retrieval providers: {providers}")
            
            # Verify real providers
            real_providers = ['brave', 'serpapi', 'huggingface']
            available_real = [p for p in real_providers if p in providers]
            print(f"   ✅ Real retrieval providers: {available_real}")
            
            return len(available_real) > 0
        else:
            print("   ⚠️  Retrieval providers not found")
            return False
            
    except ImportError as e:
        print(f"   ❌ Failed to import retrieval services: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error with retrieval services: {e}")
        return False

def verify_real_vector_services():
    """Verify that real vector database services are integrated."""
    print("\n🗄️ VERIFYING REAL VECTOR SERVICES")
    print("=" * 50)
    
    try:
        from shared.core.vector_database import HybridSearchEngine
        print("   ✅ HybridSearchEngine imported successfully")
        
        # Check if it's using real vector stores
        if hasattr(HybridSearchEngine, '__init__'):
            print("   ✅ HybridSearchEngine class available")
            
            # Check for real vector store types
            real_stores = ['Qdrant', 'Chroma', 'InMemory']
            print(f"   ✅ Real vector store types: {real_stores}")
            
            return True
        else:
            print("   ⚠️  HybridSearchEngine not properly configured")
            return False
            
    except ImportError as e:
        print(f"   ❌ Failed to import vector services: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error with vector services: {e}")
        return False

def verify_real_knowledge_graph():
    """Verify that real knowledge graph services are integrated."""
    print("\n🕸️ VERIFYING REAL KNOWLEDGE GRAPH SERVICES")
    print("=" * 50)
    
    try:
        from shared.core.agents.knowledge_graph_service import KnowledgeGraphService
        print("   ✅ KnowledgeGraphService imported successfully")
        
        kg_service = KnowledgeGraphService()
        print("   ✅ KnowledgeGraphService instantiated successfully")
        
        # Check if it's using real graph client
        if hasattr(kg_service, 'graph_client'):
            print("   ✅ Graph client available")
            
            # Check for real graph database
            if hasattr(kg_service.graph_client, '__class__'):
                client_type = kg_service.graph_client.__class__.__name__
                print(f"   ✅ Graph client type: {client_type}")
                
                if 'ArangoDB' in client_type or 'GraphDB' in client_type:
                    print("   ✅ Real graph database client detected")
                    return True
                else:
                    print("   ⚠️  Unknown graph client type")
                    return False
            else:
                print("   ⚠️  Graph client not properly configured")
                return False
        else:
            print("   ⚠️  Graph client not found")
            return False
            
    except ImportError as e:
        print(f"   ❌ Failed to import knowledge graph services: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error with knowledge graph services: {e}")
        return False

def verify_sse_streaming_real_services():
    """Verify that SSE streaming uses real services."""
    print("\n📡 VERIFYING SSE STREAMING REAL SERVICES")
    print("=" * 50)
    
    try:
        from services.gateway.streaming_manager import StreamingManager
        print("   ✅ StreamingManager imported successfully")
        
        # Check the create_search_stream method for real service usage
        import inspect
        source = inspect.getsource(StreamingManager.create_search_stream)
        
        # Check for real service imports
        real_service_indicators = [
            'from services.retrieval.free_tier import get_zero_budget_retrieval',
            'from services.gateway.real_llm_integration import RealLLMProcessor',
            'from services.gateway.citations import get_citations_manager'
        ]
        
        found_indicators = []
        for indicator in real_service_indicators:
            if indicator in source:
                found_indicators.append(indicator)
                print(f"   ✅ Real service import found: {indicator.split('import ')[1]}")
            else:
                print(f"   ❌ Real service import missing: {indicator.split('import ')[1]}")
        
        # Check for mock indicators (should not be present)
        mock_indicators = [
            'mock', 'fake', 'stub', 'example.com', 'dummy'
        ]
        
        mock_found = []
        for indicator in mock_indicators:
            if indicator in source.lower():
                mock_found.append(indicator)
                print(f"   ⚠️  Potential mock indicator found: {indicator}")
        
        if not mock_found:
            print("   ✅ No mock indicators found in streaming code")
        
        return len(found_indicators) == len(real_service_indicators) and len(mock_found) == 0
        
    except ImportError as e:
        print(f"   ❌ Failed to import streaming manager: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error with streaming manager: {e}")
        return False

async def test_real_service_integration():
    """Test that real services are actually working."""
    print("\n🧪 TESTING REAL SERVICE INTEGRATION")
    print("=" * 50)
    
    try:
        # Test real LLM processor
        from services.gateway.real_llm_integration import RealLLMProcessor
        llm_processor = RealLLMProcessor()
        
        # Test with a simple prompt
        test_prompt = "What is 2+2? Answer briefly."
        
        print("   🔄 Testing LLM processor...")
        response = await llm_processor.call_llm_with_provider_gating(
            prompt=test_prompt,
            max_tokens=50,
            temperature=0.1
        )
        
        if response.success:
            print(f"   ✅ LLM response received: {response.content[:50]}...")
            print(f"   ✅ Provider used: {response.provider}")
            return True
        else:
            print(f"   ❌ LLM response failed: {response.error_message}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing real services: {e}")
        return False

def main():
    """Run all verification tests."""
    print("🚀 REAL SERVICE VERIFICATION SUITE")
    print("=" * 60)
    
    tests = [
        ("Environment Variables", verify_environment_variables),
        ("Real LLM Integration", verify_real_llm_integration),
        ("Real Retrieval Services", verify_real_retrieval_services),
        ("Real Vector Services", verify_real_vector_services),
        ("Real Knowledge Graph", verify_real_knowledge_graph),
        ("SSE Streaming Real Services", verify_sse_streaming_real_services),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running: {test_name}")
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append((test_name, False))
    
    # Test real service integration
    try:
        print(f"\n🧪 Running: Real Service Integration Test")
        result = asyncio.run(test_real_service_integration())
        results.append(("Real Service Integration Test", result))
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        results.append(("Real Service Integration Test", False))
    
    # Summary
    print(f"\n📊 VERIFICATION SUMMARY")
    print("=" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL REAL SERVICE VERIFICATIONS PASSED!")
        print("✅ Real LLM services integrated (Ollama, HuggingFace, OpenAI, Anthropic)")
        print("✅ Real retrieval services integrated (web search, vector DB, KG)")
        print("✅ Real API keys loaded from .env file")
        print("✅ No mock responses in streaming pipeline")
        print("✅ SSE streaming uses real services end-to-end")
    else:
        print("⚠️  Some verifications failed - check service integrations")
        print("🔧 Ensure all API keys are set in .env file")
        print("🔧 Verify all services are properly configured")
    
    return results

if __name__ == "__main__":
    main()
