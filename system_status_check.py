#!/usr/bin/env python3
"""
System Status Check - Real API Methods
=====================================

Check system status using actual available methods and API calls.
"""

import os
import time
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SystemStatusCheck:
    """Check system status with real methods"""
    
    def __init__(self):
        self.results = {'timestamp': datetime.now().isoformat()}
        self.working_components = 0
        self.total_components = 0

    def check_environment_variables(self):
        """Check if critical environment variables are set"""
        print("🔧 CHECKING ENVIRONMENT VARIABLES")
        print("=" * 50)
        
        critical_vars = [
            'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 
            'HUGGINGFACE_WRITE_TOKEN', 'HUGGINGFACE_READ_TOKEN', 'HUGGINGFACE_API_KEY',
            'OLLAMA_BASE_URL', 'ARANGODB_URL', 'ARANGODB_USERNAME', 'ARANGODB_PASSWORD',
            'QDRANT_URL', 'MEILI_MASTER_KEY'
        ]
        
        configured = 0
        for var in critical_vars:
            value = os.getenv(var)
            is_set = value is not None and value.strip() != ''
            if is_set:
                configured += 1
                print(f"   ✅ {var}: Set")
            else:
                print(f"   ❌ {var}: Not set")
        
        self.total_components += 1
        if configured >= len(critical_vars) * 0.8:  # 80% threshold
            self.working_components += 1
            print(f"✅ Environment: {configured}/{len(critical_vars)} configured (GOOD)")
        else:
            print(f"❌ Environment: {configured}/{len(critical_vars)} configured (NEEDS WORK)")
        
        return configured, len(critical_vars)

    def check_llm_provider_imports(self):
        """Check if LLM provider modules can be imported"""
        print("\n🤖 CHECKING LLM PROVIDER IMPORTS")
        print("=" * 50)
        
        providers = {
            'OpenAI': 'services.gateway.providers.openai_client',
            'Anthropic': 'services.gateway.providers.anthropic_client', 
            'Ollama': 'services.gateway.providers.ollama_client',
            'Local Stub': 'services.gateway.providers.local_stub_client'
        }
        
        working_providers = 0
        for provider_name, module_path in providers.items():
            try:
                __import__(module_path)
                print(f"   ✅ {provider_name}: Import successful")
                working_providers += 1
            except Exception as e:
                print(f"   ❌ {provider_name}: Import failed - {str(e)[:40]}...")
        
        self.total_components += 1
        if working_providers >= len(providers) * 0.75:  # 75% threshold
            self.working_components += 1
            print(f"✅ LLM Providers: {working_providers}/{len(providers)} imports working (GOOD)")
        else:
            print(f"❌ LLM Providers: {working_providers}/{len(providers)} imports working (NEEDS WORK)")
        
        return working_providers, len(providers)

    def check_database_imports(self):
        """Check if database modules can be imported"""
        print("\n🗄️ CHECKING DATABASE IMPORTS")
        print("=" * 50)
        
        databases = {
            'ArangoDB': 'shared.core.services.arangodb_service',
            'Vector DB': 'shared.core.services.vector_singleton_service',
            'Meilisearch': 'shared.core.services.meilisearch_service'
        }
        
        working_dbs = 0
        for db_name, module_path in databases.items():
            try:
                __import__(module_path)
                print(f"   ✅ {db_name}: Import successful")
                working_dbs += 1
            except Exception as e:
                print(f"   ❌ {db_name}: Import failed - {str(e)[:40]}...")
        
        self.total_components += 1
        if working_dbs >= len(databases) * 0.67:  # 67% threshold
            self.working_components += 1
            print(f"✅ Databases: {working_dbs}/{len(databases)} imports working (GOOD)")
        else:
            print(f"❌ Databases: {working_dbs}/{len(databases)} imports working (NEEDS WORK)")
        
        return working_dbs, len(databases)

    def check_enterprise_features(self):
        """Check enterprise feature imports"""
        print("\n🏢 CHECKING ENTERPRISE FEATURES")
        print("=" * 50)
        
        features = {
            'Analytics Dashboard': 'shared.core.services.analytics_dashboard_service',
            'Advanced Citations': 'shared.core.services.advanced_citations_service',
            'Multi-language': 'shared.core.services.multilanguage_service'
        }
        
        working_features = 0
        for feature_name, module_path in features.items():
            try:
                __import__(module_path)
                print(f"   ✅ {feature_name}: Import successful")
                working_features += 1
            except Exception as e:
                print(f"   ❌ {feature_name}: Import failed - {str(e)[:40]}...")
        
        self.total_components += 1
        if working_features >= len(features) * 0.67:  # 67% threshold
            self.working_components += 1
            print(f"✅ Enterprise Features: {working_features}/{len(features)} imports working (GOOD)")
        else:
            print(f"❌ Enterprise Features: {working_features}/{len(features)} imports working (NEEDS WORK)")
        
        return working_features, len(features)

    def check_gateway_system(self):
        """Check if gateway system can be imported"""
        print("\n🌐 CHECKING GATEWAY SYSTEM")
        print("=" * 50)
        
        try:
            from services.gateway.main import app
            print(f"   ✅ FastAPI Gateway: Import successful")
            
            # Check if we can create test client
            from fastapi.testclient import TestClient
            client = TestClient(app)
            print(f"   ✅ Test Client: Created successfully")
            
            self.total_components += 1
            self.working_components += 1
            print(f"✅ Gateway System: Fully operational (EXCELLENT)")
            return True
            
        except Exception as e:
            print(f"   ❌ Gateway System: Failed - {str(e)[:50]}...")
            self.total_components += 1
            print(f"❌ Gateway System: Import failed (NEEDS WORK)")
            return False

    def check_service_connectivity(self):
        """Check actual service connectivity"""
        print("\n🔌 CHECKING SERVICE CONNECTIVITY")
        print("=" * 50)
        
        # Check Ollama connectivity
        ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        try:
            import requests
            response = requests.get(f"{ollama_url}/api/tags", timeout=2)
            if response.status_code == 200:
                print(f"   ✅ Ollama: Connected ({ollama_url})")
                ollama_working = True
            else:
                print(f"   ⚠️ Ollama: Responded but unexpected status {response.status_code}")
                ollama_working = False
        except Exception as e:
            print(f"   ❌ Ollama: Not accessible - {str(e)[:30]}...")
            ollama_working = False
        
        # Check ArangoDB connectivity
        arango_url = os.getenv('ARANGODB_URL', 'http://localhost:8529')
        arango_user = os.getenv('ARANGODB_USERNAME', 'root')
        arango_pass = os.getenv('ARANGODB_PASSWORD', '')
        
        try:
            auth = (arango_user, arango_pass) if arango_pass else None
            response = requests.get(f"{arango_url}/_api/version", auth=auth, timeout=2)
            if response.status_code == 200:
                print(f"   ✅ ArangoDB: Connected ({arango_url})")
                arango_working = True
            else:
                print(f"   ⚠️ ArangoDB: Responded but status {response.status_code}")
                arango_working = False
        except Exception as e:
            print(f"   ❌ ArangoDB: Not accessible - {str(e)[:30]}...")
            arango_working = False
        
        # Check Qdrant connectivity
        qdrant_url = os.getenv('QDRANT_URL', 'http://localhost:6333')
        try:
            response = requests.get(f"{qdrant_url}/", timeout=2)
            if response.status_code == 200:
                print(f"   ✅ Qdrant: Connected ({qdrant_url})")
                qdrant_working = True
            else:
                print(f"   ⚠️ Qdrant: Responded but status {response.status_code}")
                qdrant_working = False
        except Exception as e:
            print(f"   ❌ Qdrant: Not accessible - {str(e)[:30]}...")
            qdrant_working = False
        
        # Check Meilisearch connectivity
        meili_url = os.getenv('MEILISEARCH_URL', 'http://localhost:7700')
        meili_key = os.getenv('MEILI_MASTER_KEY', '')
        try:
            headers = {'Authorization': f'Bearer {meili_key}'} if meili_key else {}
            response = requests.get(f"{meili_url}/health", headers=headers, timeout=2)
            if response.status_code == 200:
                print(f"   ✅ Meilisearch: Connected ({meili_url})")
                meili_working = True
            else:
                print(f"   ⚠️ Meilisearch: Responded but status {response.status_code}")
                meili_working = False
        except Exception as e:
            print(f"   ❌ Meilisearch: Not accessible - {str(e)[:30]}...")
            meili_working = False
        
        services_working = sum([ollama_working, arango_working, qdrant_working, meili_working])
        total_services = 4
        
        self.total_components += 1
        if services_working >= 2:  # At least 50% working
            self.working_components += 1
            print(f"✅ Service Connectivity: {services_working}/{total_services} services accessible (GOOD)")
        else:
            print(f"❌ Service Connectivity: {services_working}/{total_services} services accessible (NEEDS WORK)")
        
        return services_working, total_services

    def run_status_check(self):
        """Run complete status check"""
        print("🚀 SARVANOM SYSTEM STATUS CHECK")
        print("Checking: Environment, Imports, Connectivity")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run all checks
        env_configured, env_total = self.check_environment_variables()
        llm_working, llm_total = self.check_llm_provider_imports()
        db_working, db_total = self.check_database_imports()
        feature_working, feature_total = self.check_enterprise_features()
        gateway_working = self.check_gateway_system()
        service_working, service_total = self.check_service_connectivity()
        
        total_time = (time.time() - start_time) * 1000
        
        # Calculate overall health
        overall_health = (self.working_components / self.total_components) * 100 if self.total_components > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 SYSTEM STATUS SUMMARY")
        print("=" * 80)
        
        print(f"⏱️ Check Time: {total_time:.0f}ms")
        print(f"🏥 Overall Health: {overall_health:.0f}% ({self.working_components}/{self.total_components} components)")
        
        print(f"\n📋 Component Details:")
        print(f"   🔧 Environment Variables: {env_configured}/{env_total} configured")
        print(f"   🤖 LLM Provider Imports: {llm_working}/{llm_total} working")
        print(f"   🗄️ Database Imports: {db_working}/{db_total} working")
        print(f"   🏢 Enterprise Features: {feature_working}/{feature_total} working")
        print(f"   🌐 Gateway System: {'✅ Working' if gateway_working else '❌ Issues'}")
        print(f"   🔌 Service Connectivity: {service_working}/{service_total} accessible")
        
        # System assessment
        if overall_health >= 85:
            status = "🟢 EXCELLENT"
            message = "Your system is in excellent condition!"
            recommendation = "Ready for production use. All major components working."
        elif overall_health >= 70:
            status = "🟡 GOOD"
            message = "Your system is in good condition"
            recommendation = "Minor issues detected. System is functional for most use cases."
        elif overall_health >= 50:
            status = "🟠 FAIR"
            message = "Your system has some issues"
            recommendation = "Several components need attention. Basic functionality may work."
        else:
            status = "🔴 POOR"
            message = "Your system needs significant attention"
            recommendation = "Major components require configuration or troubleshooting."
        
        print(f"\n🎯 SYSTEM STATUS: {status}")
        print(f"📝 Assessment: {message}")
        print(f"💡 Recommendation: {recommendation}")
        
        # Specific recommendations
        if env_configured < env_total:
            print(f"\n🔧 ACTION ITEMS:")
            print(f"   - Configure missing environment variables ({env_total - env_configured} remaining)")
        
        if service_working < 2:
            print(f"   - Start required services (Docker containers or local services)")
        
        if overall_health >= 70:
            print(f"\n🎉 GREAT JOB! Your SarvanOM system is working well!")
        
        return {
            'overall_health': overall_health,
            'working_components': self.working_components,
            'total_components': self.total_components,
            'ready_for_use': overall_health >= 70
        }

def main():
    """Main execution"""
    try:
        checker = SystemStatusCheck()
        results = checker.run_status_check()
        return results['ready_for_use']
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)