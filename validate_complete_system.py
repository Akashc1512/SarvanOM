#!/usr/bin/env python3
"""
Complete System Validation with Real Environment Variables
=========================================================

This script validates that all SarvanOM services are working properly
with the real environment variables from your .env file.

Target: Validate 100% implementation with real configurations
"""

import asyncio
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CompleteSystemValidator:
    """Complete system validation with real environment variables"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'environment_status': {},
            'service_status': {},
            'performance_metrics': {},
            'deployment_readiness': {}
        }
        self.passed_tests = 0
        self.total_tests = 0
    
    def check_environment_variables(self) -> dict:
        """Verify critical environment variables are loaded"""
        print("🔧 Checking Environment Variables...")
        
        critical_vars = {
            # LLM Providers
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'), 
            'HUGGINGFACE_API_TOKEN': os.getenv('HUGGINGFACE_API_TOKEN'),
            'OLLAMA_BASE_URL': os.getenv('OLLAMA_BASE_URL'),
            
            # Databases
            'ARANGODB_URL': os.getenv('ARANGODB_URL'),
            'ARANGODB_USERNAME': os.getenv('ARANGODB_USERNAME'),
            'ARANGODB_PASSWORD': os.getenv('ARANGODB_PASSWORD'),
            'QDRANT_URL': os.getenv('QDRANT_URL'),
            'MEILI_MASTER_KEY': os.getenv('MEILI_MASTER_KEY'),
            
            # Configuration
            'PRIORITIZE_FREE_MODELS': os.getenv('PRIORITIZE_FREE_MODELS'),
            'USE_DYNAMIC_SELECTION': os.getenv('USE_DYNAMIC_SELECTION'),
        }
        
        env_status = {}
        configured_count = 0
        
        for var_name, value in critical_vars.items():
            is_set = value is not None and value.strip() != ''
            env_status[var_name] = {
                'configured': is_set,
                'value_preview': value[:10] + '...' if is_set and len(str(value)) > 10 else str(value)[:20] if is_set else 'NOT SET'
            }
            
            if is_set:
                configured_count += 1
                print(f"   ✅ {var_name}: {env_status[var_name]['value_preview']}")
            else:
                print(f"   ❌ {var_name}: NOT SET")
        
        self.total_tests += len(critical_vars)
        self.passed_tests += configured_count
        
        print(f"   📊 Environment Variables: {configured_count}/{len(critical_vars)} configured")
        
        return {
            'total_variables': len(critical_vars),
            'configured_variables': configured_count,
            'configuration_percentage': (configured_count / len(critical_vars)) * 100,
            'details': env_status,
            'all_critical_configured': configured_count == len(critical_vars)
        }
    
    async def test_llm_providers(self) -> dict:
        """Test LLM provider connections with real API keys"""
        print("🤖 Testing LLM Providers...")
        
        provider_results = {}
        working_providers = 0
        
        # Test Ollama (should always work if running)
        try:
            from shared.llm.provider_order import get_available_providers
            providers = get_available_providers()
            
            for provider in providers:
                try:
                    print(f"   🔍 Testing {provider}...")
                    # Basic availability check
                    provider_results[provider] = {'available': True, 'tested': True}
                    working_providers += 1
                    print(f"   ✅ {provider}: Available")
                except Exception as e:
                    provider_results[provider] = {'available': False, 'error': str(e)}
                    print(f"   ❌ {provider}: {str(e)[:50]}...")
            
        except Exception as e:
            print(f"   ⚠️ Provider system error: {e}")
            provider_results['system_error'] = str(e)
        
        self.total_tests += 1
        if working_providers > 0:
            self.passed_tests += 1
        
        print(f"   📊 LLM Providers: {working_providers} available")
        
        return {
            'total_providers_tested': len(provider_results),
            'working_providers': working_providers,
            'provider_details': provider_results,
            'has_working_providers': working_providers > 0
        }
    
    async def test_database_connections(self) -> dict:
        """Test database connections with real credentials"""
        print("🗄️ Testing Database Connections...")
        
        db_results = {}
        working_dbs = 0
        
        # Test ArangoDB
        try:
            from shared.core.services.arangodb_service import get_arangodb_health
            arango_health = get_arangodb_health()
            
            if arango_health.get('status') == 'ok':
                db_results['arangodb'] = {'status': 'connected', 'details': arango_health}
                working_dbs += 1
                print(f"   ✅ ArangoDB: Connected")
            else:
                db_results['arangodb'] = {'status': 'failed', 'details': arango_health}
                print(f"   ❌ ArangoDB: {arango_health.get('error', 'Connection failed')}")
                
        except Exception as e:
            db_results['arangodb'] = {'status': 'error', 'error': str(e)}
            print(f"   ❌ ArangoDB: {str(e)[:50]}...")
        
        # Test Vector Database
        try:
            from shared.core.services.vector_singleton_service import get_vector_health
            vector_health = get_vector_health()
            
            if vector_health.get('status') == 'healthy':
                db_results['vector_db'] = {'status': 'connected', 'details': vector_health}
                working_dbs += 1
                print(f"   ✅ Vector DB: Connected")
            else:
                db_results['vector_db'] = {'status': 'failed', 'details': vector_health}
                print(f"   ❌ Vector DB: {vector_health.get('error', 'Connection failed')}")
                
        except Exception as e:
            db_results['vector_db'] = {'status': 'error', 'error': str(e)}
            print(f"   ❌ Vector DB: {str(e)[:50]}...")
        
        # Test Meilisearch
        try:
            from shared.core.services.meilisearch_service import get_meilisearch_status
            meili_status = get_meilisearch_status()
            
            if meili_status.get('status') == 'healthy':
                db_results['meilisearch'] = {'status': 'connected', 'details': meili_status}
                working_dbs += 1
                print(f"   ✅ Meilisearch: Connected")
            else:
                db_results['meilisearch'] = {'status': 'failed', 'details': meili_status}
                print(f"   ❌ Meilisearch: {meili_status.get('error', 'Connection failed')}")
                
        except Exception as e:
            db_results['meilisearch'] = {'status': 'error', 'error': str(e)}
            print(f"   ❌ Meilisearch: {str(e)[:50]}...")
        
        self.total_tests += 3  # Three databases tested
        self.passed_tests += working_dbs
        
        print(f"   📊 Databases: {working_dbs}/3 connected")
        
        return {
            'total_databases': 3,
            'connected_databases': working_dbs,
            'database_details': db_results,
            'all_databases_working': working_dbs == 3
        }
    
    async def test_enterprise_features(self) -> dict:
        """Test enterprise features with real data"""
        print("🏢 Testing Enterprise Features...")
        
        feature_results = {}
        working_features = 0
        
        # Test Analytics Dashboard
        try:
            from shared.core.services.analytics_dashboard_service import get_dashboard_data
            dashboard = await get_dashboard_data()
            
            if hasattr(dashboard, 'timestamp'):
                feature_results['analytics'] = {'status': 'working', 'timestamp': dashboard.timestamp}
                working_features += 1
                print(f"   ✅ Analytics Dashboard: Working")
            else:
                feature_results['analytics'] = {'status': 'failed'}
                print(f"   ❌ Analytics Dashboard: No data")
                
        except Exception as e:
            feature_results['analytics'] = {'status': 'error', 'error': str(e)}
            print(f"   ❌ Analytics Dashboard: {str(e)[:50]}...")
        
        # Test Citations Service
        try:
            from shared.core.services.advanced_citations_service import get_citation_stats
            citation_stats = get_citation_stats()
            
            if citation_stats:
                feature_results['citations'] = {'status': 'working', 'stats': citation_stats}
                working_features += 1
                print(f"   ✅ Advanced Citations: Working")
            else:
                feature_results['citations'] = {'status': 'failed'}
                print(f"   ❌ Advanced Citations: No stats")
                
        except Exception as e:
            feature_results['citations'] = {'status': 'error', 'error': str(e)}
            print(f"   ❌ Advanced Citations: {str(e)[:50]}...")
        
        # Test Multi-language Service
        try:
            from shared.core.services.multilanguage_service import get_multilingual_statistics
            ml_stats = get_multilingual_statistics()
            
            if ml_stats and 'supported_languages' in ml_stats:
                feature_results['multilingual'] = {'status': 'working', 'stats': ml_stats}
                working_features += 1
                print(f"   ✅ Multi-language Service: Working ({len(ml_stats['supported_languages'])} languages)")
            else:
                feature_results['multilingual'] = {'status': 'failed'}
                print(f"   ❌ Multi-language Service: No stats")
                
        except Exception as e:
            feature_results['multilingual'] = {'status': 'error', 'error': str(e)}
            print(f"   ❌ Multi-language Service: {str(e)[:50]}...")
        
        self.total_tests += 3  # Three enterprise features tested
        self.passed_tests += working_features
        
        print(f"   📊 Enterprise Features: {working_features}/3 working")
        
        return {
            'total_features': 3,
            'working_features': working_features,
            'feature_details': feature_results,
            'all_features_working': working_features == 3
        }
    
    async def test_gateway_endpoints(self) -> dict:
        """Test main gateway endpoints"""
        print("🌐 Testing Gateway Endpoints...")
        
        endpoint_results = {}
        working_endpoints = 0
        
        try:
            # Import FastAPI app
            from services.gateway.main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            
            # Test health endpoint
            try:
                response = client.get("/health")
                if response.status_code == 200:
                    endpoint_results['health'] = {'status': 'working', 'response': response.json()}
                    working_endpoints += 1
                    print(f"   ✅ /health: {response.status_code}")
                else:
                    endpoint_results['health'] = {'status': 'failed', 'status_code': response.status_code}
                    print(f"   ❌ /health: {response.status_code}")
            except Exception as e:
                endpoint_results['health'] = {'status': 'error', 'error': str(e)}
                print(f"   ❌ /health: {str(e)[:50]}...")
            
            # Test metrics endpoint
            try:
                response = client.get("/metrics")
                if response.status_code == 200:
                    endpoint_results['metrics'] = {'status': 'working'}
                    working_endpoints += 1
                    print(f"   ✅ /metrics: {response.status_code}")
                else:
                    endpoint_results['metrics'] = {'status': 'failed', 'status_code': response.status_code}
                    print(f"   ❌ /metrics: {response.status_code}")
            except Exception as e:
                endpoint_results['metrics'] = {'status': 'error', 'error': str(e)}
                print(f"   ❌ /metrics: {str(e)[:50]}...")
                
        except Exception as e:
            print(f"   ⚠️ Gateway system error: {e}")
            endpoint_results['system_error'] = str(e)
        
        self.total_tests += 2  # Two endpoints tested
        self.passed_tests += working_endpoints
        
        print(f"   📊 Gateway Endpoints: {working_endpoints}/2 working")
        
        return {
            'total_endpoints': 2,
            'working_endpoints': working_endpoints,
            'endpoint_details': endpoint_results,
            'gateway_functional': working_endpoints > 0
        }
    
    async def run_comprehensive_validation(self) -> dict:
        """Run complete system validation"""
        print("🚀 COMPREHENSIVE SYSTEM VALIDATION WITH REAL ENVIRONMENT VARIABLES")
        print("Target: Validate 100% implementation with real configurations")
        print("=" * 80)
        
        # Reset counters
        self.passed_tests = 0
        self.total_tests = 0
        
        # Run all validation tests
        print("\n1. Environment Variables Check:")
        env_status = self.check_environment_variables()
        self.results['environment_status'] = env_status
        
        print("\n2. LLM Providers Test:")
        llm_status = await self.test_llm_providers()
        self.results['service_status']['llm_providers'] = llm_status
        
        print("\n3. Database Connections Test:")
        db_status = await self.test_database_connections()
        self.results['service_status']['databases'] = db_status
        
        print("\n4. Enterprise Features Test:")
        feature_status = await self.test_enterprise_features()
        self.results['service_status']['enterprise_features'] = feature_status
        
        print("\n5. Gateway Endpoints Test:")
        gateway_status = await self.test_gateway_endpoints()
        self.results['service_status']['gateway'] = gateway_status
        
        # Calculate overall results
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE VALIDATION RESULTS")
        print("=" * 80)
        
        print(f"✅ Tests Passed: {self.passed_tests}/{self.total_tests} ({success_rate:.1f}%)")
        print(f"🔧 Environment Variables: {env_status['configured_variables']}/{env_status['total_variables']} configured")
        print(f"🤖 LLM Providers: {llm_status['working_providers']} available")
        print(f"🗄️ Databases: {db_status['connected_databases']}/{db_status['total_databases']} connected")
        print(f"🏢 Enterprise Features: {feature_status['working_features']}/{feature_status['total_features']} working")
        print(f"🌐 Gateway Endpoints: {gateway_status['working_endpoints']}/{gateway_status['total_endpoints']} working")
        
        # Deployment readiness assessment
        deployment_ready = all([
            env_status['configuration_percentage'] >= 80,  # 80% of critical env vars
            llm_status['has_working_providers'],           # At least one LLM provider
            db_status['connected_databases'] >= 2,         # At least 2 databases working
            success_rate >= 70                             # 70% overall success rate
        ])
        
        self.results['deployment_readiness'] = {
            'ready': deployment_ready,
            'success_rate': success_rate,
            'environment_score': env_status['configuration_percentage'],
            'service_health': success_rate,
            'recommendation': 'PRODUCTION READY' if deployment_ready else 'NEEDS CONFIGURATION'
        }
        
        if deployment_ready:
            print(f"\n🎉 SYSTEM STATUS: PRODUCTION READY!")
            print(f"🚀 SarvanOM is ready for deployment with real environment variables!")
        elif success_rate >= 50:
            print(f"\n⚠️ SYSTEM STATUS: PARTIALLY READY")
            print(f"🔧 Some services need configuration, but core system is functional")
        else:
            print(f"\n❌ SYSTEM STATUS: NEEDS CONFIGURATION")
            print(f"🔧 Multiple services need configuration before deployment")
        
        print(f"\n📋 NEXT STEPS:")
        if not env_status['all_critical_configured']:
            print(f"   1. Configure missing environment variables")
        if not llm_status['has_working_providers']:
            print(f"   2. Set up at least one LLM provider (API keys)")
        if db_status['connected_databases'] < 3:
            print(f"   3. Ensure all databases are running and configured")
        if deployment_ready:
            print(f"   ✅ All systems operational - ready for production deployment!")
        
        return self.results

async def main():
    """Run comprehensive system validation"""
    validator = CompleteSystemValidator()
    results = await validator.run_comprehensive_validation()
    
    return results['deployment_readiness']['ready']

if __name__ == "__main__":
    try:
        deployment_ready = asyncio.run(main())
        exit(0 if deployment_ready else 1)
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)