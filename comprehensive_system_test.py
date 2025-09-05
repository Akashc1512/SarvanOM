#!/usr/bin/env python3
"""
Comprehensive System Test - All Components
==========================================

Test all LLM providers, models, databases, and knowledge graph
with real environment variables and actual API calls.
"""

import asyncio
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class ComprehensiveSystemTest:
    """Test all system components comprehensively"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'llm_providers': {},
            'databases': {},
            'knowledge_graph': {},
            'models': {},
            'performance': {}
        }
        self.total_tests = 0
        self.passed_tests = 0

    async def test_llm_providers(self):
        """Test all LLM providers with real API calls"""
        print("🤖 TESTING ALL LLM PROVIDERS")
        print("=" * 50)
        
        provider_results = {}
        
        # Test OpenAI
        print("1. Testing OpenAI...")
        try:
            from services.gateway.providers.openai_client import OpenAIClient
            
            openai_client = OpenAIClient()
            if openai_client.api_key:
                # Test simple completion
                test_prompt = "What is AI?"
                start_time = time.time()
                try:
                    response = await openai_client.generate_completion(test_prompt, max_tokens=50)
                    response_time = (time.time() - start_time) * 1000
                    
                    provider_results['openai'] = {
                        'status': 'working',
                        'response_time_ms': response_time,
                        'response_length': len(response) if response else 0,
                        'test_successful': bool(response)
                    }
                    print(f"   ✅ OpenAI: Working ({response_time:.0f}ms)")
                    self.passed_tests += 1
                except Exception as e:
                    provider_results['openai'] = {'status': 'error', 'error': str(e)[:100]}
                    print(f"   ❌ OpenAI API call failed: {str(e)[:50]}...")
            else:
                provider_results['openai'] = {'status': 'no_api_key'}
                print(f"   ⚠️ OpenAI: No API key")
                
        except Exception as e:
            provider_results['openai'] = {'status': 'import_error', 'error': str(e)}
            print(f"   ❌ OpenAI import failed: {str(e)[:50]}...")
        
        self.total_tests += 1
        
        # Test Anthropic
        print("2. Testing Anthropic...")
        try:
            from services.gateway.providers.anthropic_client import AnthropicClient
            
            anthropic_client = AnthropicClient()
            if anthropic_client.api_key:
                test_prompt = "What is machine learning?"
                start_time = time.time()
                try:
                    response = await anthropic_client.generate_completion(test_prompt, max_tokens=50)
                    response_time = (time.time() - start_time) * 1000
                    
                    provider_results['anthropic'] = {
                        'status': 'working',
                        'response_time_ms': response_time,
                        'response_length': len(response) if response else 0,
                        'test_successful': bool(response)
                    }
                    print(f"   ✅ Anthropic: Working ({response_time:.0f}ms)")
                    self.passed_tests += 1
                except Exception as e:
                    provider_results['anthropic'] = {'status': 'error', 'error': str(e)[:100]}
                    print(f"   ❌ Anthropic API call failed: {str(e)[:50]}...")
            else:
                provider_results['anthropic'] = {'status': 'no_api_key'}
                print(f"   ⚠️ Anthropic: No API key")
                
        except Exception as e:
            provider_results['anthropic'] = {'status': 'import_error', 'error': str(e)}
            print(f"   ❌ Anthropic import failed: {str(e)[:50]}...")
        
        self.total_tests += 1
        
        # Test Hugging Face
        print("3. Testing Hugging Face...")
        try:
            from services.gateway.providers.huggingface_client import HuggingFaceClient
            
            hf_client = HuggingFaceClient()
            # Check for any of your Hugging Face tokens
            has_token = any([
                os.getenv('HUGGINGFACE_WRITE_TOKEN'),
                os.getenv('HUGGINGFACE_READ_TOKEN'),
                os.getenv('HUGGINGFACE_API_KEY')
            ])
            
            if has_token:
                test_prompt = "Explain deep learning"
                start_time = time.time()
                try:
                    response = await hf_client.generate_completion(test_prompt, max_tokens=30)
                    response_time = (time.time() - start_time) * 1000
                    
                    provider_results['huggingface'] = {
                        'status': 'working',
                        'response_time_ms': response_time,
                        'response_length': len(response) if response else 0,
                        'test_successful': bool(response)
                    }
                    print(f"   ✅ Hugging Face: Working ({response_time:.0f}ms)")
                    self.passed_tests += 1
                except Exception as e:
                    provider_results['huggingface'] = {'status': 'error', 'error': str(e)[:100]}
                    print(f"   ❌ Hugging Face API call failed: {str(e)[:50]}...")
            else:
                provider_results['huggingface'] = {'status': 'no_tokens'}
                print(f"   ⚠️ Hugging Face: No tokens found")
                
        except Exception as e:
            provider_results['huggingface'] = {'status': 'import_error', 'error': str(e)}
            print(f"   ❌ Hugging Face import failed: {str(e)[:50]}...")
        
        self.total_tests += 1
        
        # Test Ollama
        print("4. Testing Ollama...")
        try:
            from services.gateway.providers.ollama_client import OllamaClient
            
            ollama_client = OllamaClient()
            test_prompt = "What is neural network?"
            start_time = time.time()
            try:
                response = await ollama_client.generate_completion(test_prompt, max_tokens=30)
                response_time = (time.time() - start_time) * 1000
                
                provider_results['ollama'] = {
                    'status': 'working',
                    'response_time_ms': response_time,
                    'response_length': len(response) if response else 0,
                    'test_successful': bool(response)
                }
                print(f"   ✅ Ollama: Working ({response_time:.0f}ms)")
                self.passed_tests += 1
            except Exception as e:
                provider_results['ollama'] = {'status': 'connection_error', 'error': str(e)[:100]}
                print(f"   ❌ Ollama connection failed: {str(e)[:50]}...")
                
        except Exception as e:
            provider_results['ollama'] = {'status': 'import_error', 'error': str(e)}
            print(f"   ❌ Ollama import failed: {str(e)[:50]}...")
        
        self.total_tests += 1
        
        self.results['llm_providers'] = provider_results
        working_providers = len([p for p in provider_results.values() if p.get('status') == 'working'])
        print(f"\n📊 LLM Providers: {working_providers}/{len(provider_results)} working")
        
        return provider_results

    async def test_databases(self):
        """Test all database connections"""
        print("\n🗄️ TESTING ALL DATABASES")
        print("=" * 50)
        
        db_results = {}
        
        # Test ArangoDB
        print("1. Testing ArangoDB (Knowledge Graph)...")
        try:
            from shared.core.services.arangodb_service import ArangoDBService
            
            arango_service = ArangoDBService()
            start_time = time.time()
            
            # Test connection and basic operations
            health_status = await arango_service.get_health()
            connection_time = (time.time() - start_time) * 1000
            
            if health_status.get('status') == 'ok':
                db_results['arangodb'] = {
                    'status': 'connected',
                    'connection_time_ms': connection_time,
                    'database': health_status.get('database'),
                    'version': health_status.get('version'),
                    'collections': health_status.get('collections', [])
                }
                print(f"   ✅ ArangoDB: Connected ({connection_time:.0f}ms)")
                print(f"      Database: {health_status.get('database')}")
                print(f"      Collections: {len(health_status.get('collections', []))}")
                self.passed_tests += 1
            else:
                db_results['arangodb'] = {'status': 'unhealthy', 'details': health_status}
                print(f"   ❌ ArangoDB: Unhealthy - {health_status.get('error', 'Unknown issue')}")
                
        except Exception as e:
            db_results['arangodb'] = {'status': 'error', 'error': str(e)}
            print(f"   ❌ ArangoDB error: {str(e)[:50]}...")
        
        self.total_tests += 1
        
        # Test Qdrant (Vector Database)
        print("2. Testing Qdrant (Vector Database)...")
        try:
            from shared.core.services.vector_singleton_service import VectorSingletonService
            
            vector_service = VectorSingletonService()
            start_time = time.time()
            
            # Test vector operations
            test_text = "artificial intelligence machine learning"
            embedding = await vector_service.get_embedding(test_text)
            embedding_time = (time.time() - start_time) * 1000
            
            if embedding and len(embedding) > 0:
                db_results['qdrant'] = {
                    'status': 'working',
                    'embedding_time_ms': embedding_time,
                    'embedding_dimension': len(embedding),
                    'test_successful': True
                }
                print(f"   ✅ Qdrant: Working ({embedding_time:.0f}ms)")
                print(f"      Embedding dimension: {len(embedding)}")
                self.passed_tests += 1
            else:
                db_results['qdrant'] = {'status': 'no_embedding', 'embedding_time_ms': embedding_time}
                print(f"   ❌ Qdrant: No embedding generated")
                
        except Exception as e:
            db_results['qdrant'] = {'status': 'error', 'error': str(e)}
            print(f"   ❌ Qdrant error: {str(e)[:50]}...")
        
        self.total_tests += 1
        
        # Test Meilisearch
        print("3. Testing Meilisearch (Full-text Search)...")
        try:
            from shared.core.services.meilisearch_service import MeilisearchService
            
            meili_service = MeilisearchService()
            start_time = time.time()
            
            # Test search functionality
            status = await meili_service.get_status()
            status_time = (time.time() - start_time) * 1000
            
            if status.get('status') == 'healthy':
                # Test indexing
                test_docs = [
                    {'id': 'test1', 'title': 'AI Overview', 'content': 'Artificial intelligence basics'},
                    {'id': 'test2', 'title': 'ML Guide', 'content': 'Machine learning fundamentals'}
                ]
                
                index_start = time.time()
                await meili_service.index_documents('test_index', test_docs)
                index_time = (time.time() - index_start) * 1000
                
                db_results['meilisearch'] = {
                    'status': 'working',
                    'connection_time_ms': status_time,
                    'index_time_ms': index_time,
                    'version': status.get('version'),
                    'test_successful': True
                }
                print(f"   ✅ Meilisearch: Working ({status_time:.0f}ms connection, {index_time:.0f}ms indexing)")
                self.passed_tests += 1
            else:
                db_results['meilisearch'] = {'status': 'unhealthy', 'details': status}
                print(f"   ❌ Meilisearch: Unhealthy")
                
        except Exception as e:
            db_results['meilisearch'] = {'status': 'error', 'error': str(e)}
            print(f"   ❌ Meilisearch error: {str(e)[:50]}...")
        
        self.total_tests += 1
        
        self.results['databases'] = db_results
        working_dbs = len([db for db in db_results.values() if db.get('status') in ['connected', 'working']])
        print(f"\n📊 Databases: {working_dbs}/{len(db_results)} working")
        
        return db_results

    async def test_knowledge_graph(self):
        """Test Knowledge Graph functionality"""
        print("\n🕸️ TESTING KNOWLEDGE GRAPH")
        print("=" * 50)
        
        kg_results = {}
        
        try:
            from shared.core.services.arangodb_service import ArangoDBService
            
            arango_service = ArangoDBService()
            
            # Test basic KG operations
            print("1. Testing Knowledge Graph Queries...")
            start_time = time.time()
            
            # Test entity creation
            test_entity = {
                'name': 'Artificial Intelligence',
                'type': 'concept',
                'description': 'Computer systems able to perform tasks that typically require human intelligence'
            }
            
            entity_result = await arango_service.create_entity(test_entity)
            kg_time = (time.time() - start_time) * 1000
            
            if entity_result:
                kg_results['entity_creation'] = {
                    'status': 'working',
                    'creation_time_ms': kg_time,
                    'entity_id': entity_result.get('_id') if isinstance(entity_result, dict) else 'created'
                }
                print(f"   ✅ Entity Creation: Working ({kg_time:.0f}ms)")
                self.passed_tests += 1
            else:
                kg_results['entity_creation'] = {'status': 'failed', 'creation_time_ms': kg_time}
                print(f"   ❌ Entity Creation: Failed")
            
            # Test relationship queries
            print("2. Testing Relationship Queries...")
            try:
                query_start = time.time()
                relationships = await arango_service.query_relationships('Artificial Intelligence')
                query_time = (time.time() - query_start) * 1000
                
                kg_results['relationship_queries'] = {
                    'status': 'working',
                    'query_time_ms': query_time,
                    'relationships_found': len(relationships) if relationships else 0
                }
                print(f"   ✅ Relationship Queries: Working ({query_time:.0f}ms)")
                self.passed_tests += 1
            except Exception as e:
                kg_results['relationship_queries'] = {'status': 'error', 'error': str(e)[:100]}
                print(f"   ❌ Relationship Queries: {str(e)[:50]}...")
                
        except Exception as e:
            kg_results['knowledge_graph'] = {'status': 'error', 'error': str(e)}
            print(f"   ❌ Knowledge Graph error: {str(e)[:50]}...")
        
        self.total_tests += 2  # Two KG tests
        self.results['knowledge_graph'] = kg_results
        working_kg = len([kg for kg in kg_results.values() if kg.get('status') == 'working'])
        print(f"\n📊 Knowledge Graph: {working_kg}/{len(kg_results)} components working")
        
        return kg_results

    async def test_model_availability(self):
        """Test specific model availability and performance"""
        print("\n🔬 TESTING MODEL AVAILABILITY")
        print("=" * 50)
        
        model_results = {}
        
        # Test different model types
        test_models = [
            {'provider': 'openai', 'model': 'gpt-4o-mini', 'type': 'completion'},
            {'provider': 'anthropic', 'model': 'claude-3-haiku-20240307', 'type': 'completion'},
            {'provider': 'huggingface', 'model': 'microsoft/DialoGPT-medium', 'type': 'completion'},
            {'provider': 'ollama', 'model': 'llama3.2:3b', 'type': 'completion'}
        ]
        
        for i, model_config in enumerate(test_models, 1):
            provider = model_config['provider']
            model_name = model_config['model']
            
            print(f"{i}. Testing {provider.title()} - {model_name}...")
            
            try:
                if provider == 'openai':
                    from services.gateway.providers.openai_client import OpenAIClient
                    client = OpenAIClient()
                    if client.api_key:
                        start_time = time.time()
                        response = await client.generate_completion("Test prompt", model=model_name, max_tokens=10)
                        response_time = (time.time() - start_time) * 1000
                        
                        model_results[f'{provider}_{model_name}'] = {
                            'status': 'available',
                            'response_time_ms': response_time,
                            'response_received': bool(response)
                        }
                        print(f"   ✅ {model_name}: Available ({response_time:.0f}ms)")
                        self.passed_tests += 1
                    else:
                        model_results[f'{provider}_{model_name}'] = {'status': 'no_api_key'}
                        print(f"   ⚠️ {model_name}: No API key")
                        
                elif provider == 'anthropic':
                    from services.gateway.providers.anthropic_client import AnthropicClient
                    client = AnthropicClient()
                    if client.api_key:
                        start_time = time.time()
                        response = await client.generate_completion("Test prompt", model=model_name, max_tokens=10)
                        response_time = (time.time() - start_time) * 1000
                        
                        model_results[f'{provider}_{model_name}'] = {
                            'status': 'available',
                            'response_time_ms': response_time,
                            'response_received': bool(response)
                        }
                        print(f"   ✅ {model_name}: Available ({response_time:.0f}ms)")
                        self.passed_tests += 1
                    else:
                        model_results[f'{provider}_{model_name}'] = {'status': 'no_api_key'}
                        print(f"   ⚠️ {model_name}: No API key")
                        
                else:
                    # For HuggingFace and Ollama, just check if provider is working
                    model_results[f'{provider}_{model_name}'] = {'status': 'provider_dependent'}
                    print(f"   📋 {model_name}: Depends on {provider} provider status")
                    
            except Exception as e:
                model_results[f'{provider}_{model_name}'] = {'status': 'error', 'error': str(e)[:100]}
                print(f"   ❌ {model_name}: {str(e)[:50]}...")
            
            self.total_tests += 1
        
        self.results['models'] = model_results
        available_models = len([m for m in model_results.values() if m.get('status') == 'available'])
        print(f"\n📊 Models: {available_models}/{len(model_results)} directly available")
        
        return model_results

    async def run_comprehensive_test(self):
        """Run all comprehensive tests"""
        print("🚀 COMPREHENSIVE SYSTEM TEST - ALL COMPONENTS")
        print("Testing: LLM Providers, Models, Databases, Knowledge Graph")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run all tests
        llm_results = await self.test_llm_providers()
        db_results = await self.test_databases()
        kg_results = await self.test_knowledge_graph()
        model_results = await self.test_model_availability()
        
        total_time = (time.time() - start_time) * 1000
        
        # Calculate overall results
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        
        print(f"⏱️ Total Test Time: {total_time:.0f}ms")
        print(f"✅ Tests Passed: {self.passed_tests}/{self.total_tests} ({success_rate:.1f}%)")
        
        # Component summaries
        working_providers = len([p for p in llm_results.values() if p.get('status') == 'working'])
        working_dbs = len([db for db in db_results.values() if db.get('status') in ['connected', 'working']])
        working_kg = len([kg for kg in kg_results.values() if kg.get('status') == 'working'])
        available_models = len([m for m in model_results.values() if m.get('status') == 'available'])
        
        print(f"🤖 LLM Providers: {working_providers}/{len(llm_results)} working")
        print(f"🗄️ Databases: {working_dbs}/{len(db_results)} working")
        print(f"🕸️ Knowledge Graph: {working_kg}/{len(kg_results)} components working")
        print(f"🔬 Models: {available_models}/{len(model_results)} directly available")
        
        # System health assessment
        if success_rate >= 80:
            health_status = "🟢 EXCELLENT"
        elif success_rate >= 60:
            health_status = "🟡 GOOD"
        else:
            health_status = "🔴 NEEDS ATTENTION"
        
        print(f"\n🏥 System Health: {health_status} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 RESULT: Your system is in excellent condition!")
            print("🚀 All major components are working properly")
        elif success_rate >= 60:
            print("✅ RESULT: Your system is in good condition")
            print("🔧 Some components may need minor configuration")
        else:
            print("⚠️ RESULT: System needs attention")
            print("🔧 Several components require configuration or troubleshooting")
        
        # Performance summary
        self.results['performance'] = {
            'total_time_ms': total_time,
            'success_rate': success_rate,
            'working_providers': working_providers,
            'working_databases': working_dbs,
            'working_kg_components': working_kg,
            'available_models': available_models
        }
        
        return self.results

async def main():
    """Main execution"""
    tester = ComprehensiveSystemTest()
    results = await tester.run_comprehensive_test()
    
    return results['performance']['success_rate'] >= 80

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Comprehensive test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)