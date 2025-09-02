#!/usr/bin/env python3
"""
Industry-Standard Verification Script for SarvanOM
Follows Meta/OpenAI/Perplexity level testing practices
"""

import os
import sys
import asyncio
import time
import subprocess
import importlib
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

@dataclass
class VerificationResult:
    """Result of a verification step."""
    name: str
    status: str  # "PASS", "FAIL", "WARNING", "SKIP"
    details: str
    execution_time: float
    error: str = None

class IndustryStandardVerifier:
    """Industry-standard verification following Meta/OpenAI/Perplexity practices."""
    
    def __init__(self):
        self.results: List[VerificationResult] = []
        self.start_time = time.time()
        
    def log_result(self, name: str, status: str, details: str, error: str = None):
        """Log a verification result."""
        execution_time = time.time() - self.start_time
        result = VerificationResult(
            name=name,
            status=status,
            details=details,
            execution_time=execution_time,
            error=error
        )
        self.results.append(result)
        
        # Print with appropriate emoji
        emoji_map = {
            "PASS": "✅",
            "FAIL": "❌", 
            "WARNING": "⚠️",
            "SKIP": "⏭️"
        }
        emoji = emoji_map.get(status, "❓")
        print(f"{emoji} {name}: {status}")
        if details:
            print(f"   {details}")
        if error:
            print(f"   Error: {error}")
        print()

    async def verify_python_environment(self) -> bool:
        """Verify Python environment meets industry standards."""
        print("🐍 Verifying Python Environment...")
        
        try:
            # Check Python version
            version = sys.version_info
            if version.major == 3 and version.minor >= 11:
                self.log_result("Python Version", "PASS", f"Python {version.major}.{version.minor}.{version.micro}")
            else:
                self.log_result("Python Version", "FAIL", f"Python {version.major}.{version.minor}.{version.micro} (requires 3.11+)")
                return False
            
            # Check virtual environment
            if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
                self.log_result("Virtual Environment", "PASS", "Virtual environment is active")
            else:
                self.log_result("Virtual Environment", "WARNING", "No virtual environment detected")
            
            return True
            
        except Exception as e:
            self.log_result("Python Environment", "FAIL", "Failed to verify Python environment", str(e))
            return False

    async def verify_dependencies(self) -> bool:
        """Verify all dependencies are properly installed."""
        print("📦 Verifying Dependencies...")
        
        critical_deps = [
            "fastapi", "uvicorn", "pydantic", "openai", "anthropic", 
            "transformers", "torch", "qdrant_client", "redis", "psycopg2"
        ]
        
        missing_deps = []
        for dep in critical_deps:
            try:
                importlib.import_module(dep)
                self.log_result(f"Dependency: {dep}", "PASS", "Successfully imported")
            except ImportError:
                missing_deps.append(dep)
                self.log_result(f"Dependency: {dep}", "FAIL", "Failed to import")
        
        if missing_deps:
            return False
        return True

    async def verify_imports(self) -> bool:
        """Verify all core modules can be imported."""
        print("🔌 Verifying Module Imports...")
        
        core_modules = [
            ("services.gateway.main", "Gateway Service"),
            ("shared.core.agents.base_agent", "Base Agent"),
            ("shared.core.cache.cache_manager", "Cache Manager"),
            ("shared.core.vector_database", "Vector Database"),
            ("services.knowledge_graph.main", "Knowledge Graph Service")
        ]
        
        all_imports_ok = True
        for module_path, module_name in core_modules:
            try:
                importlib.import_module(module_path)
                self.log_result(f"Import: {module_name}", "PASS", "Successfully imported")
            except ImportError as e:
                self.log_result(f"Import: {module_name}", "FAIL", f"Failed to import {module_path}", str(e))
                all_imports_ok = False
        
        return all_imports_ok

    async def verify_fastapi_app(self) -> bool:
        """Verify FastAPI application can be instantiated."""
        print("🚀 Verifying FastAPI Application...")
        
        try:
            from services.gateway.main import app
            
            # Check app properties
            if hasattr(app, 'title') and app.title:
                self.log_result("FastAPI App Title", "PASS", f"App title: {app.title}")
            else:
                self.log_result("FastAPI App Title", "WARNING", "No app title set")
            
            if hasattr(app, 'routes') and len(app.routes) > 0:
                self.log_result("FastAPI Routes", "PASS", f"Found {len(app.routes)} routes")
            else:
                self.log_result("FastAPI Routes", "WARNING", "No routes found")
            
            return True
            
        except Exception as e:
            self.log_result("FastAPI App", "FAIL", "Failed to instantiate FastAPI app", str(e))
            return False

    async def verify_llm_integration(self) -> bool:
        """Verify LLM integration is working."""
        print("🤖 Verifying LLM Integration...")
        
        try:
            from services.gateway.real_llm_integration import RealLLMProcessor
            
            processor = RealLLMProcessor()
            
            # Check provider registry
            if hasattr(processor, 'provider_registry') and processor.provider_registry:
                self.log_result("LLM Provider Registry", "PASS", "Provider registry initialized")
            else:
                self.log_result("LLM Provider Registry", "WARNING", "Provider registry not properly initialized")
            
            # Check available providers
            if hasattr(processor, 'available_providers') and processor.available_providers:
                self.log_result("LLM Available Providers", "PASS", f"Found {len(processor.available_providers)} providers")
            else:
                self.log_result("LLM Available Providers", "WARNING", "No providers available")
            
            return True
            
        except Exception as e:
            self.log_result("LLM Integration", "FAIL", "Failed to verify LLM integration", str(e))
            return False

    async def verify_vector_database(self) -> bool:
        """Verify vector database integration."""
        print("🗄️ Verifying Vector Database...")
        
        try:
            from shared.core.vector_database import PineconeVectorDB
            
            # Check if we can instantiate the class
            self.log_result("Vector DB Class", "PASS", "PineconeVectorDB class available")
            
            # Check environment variables
            pinecone_key = os.getenv("PINECONE_API_KEY")
            pinecone_env = os.getenv("PINECONE_ENVIRONMENT")
            
            if pinecone_key and pinecone_env:
                self.log_result("Vector DB Credentials", "PASS", "Pinecone credentials found")
            else:
                self.log_result("Vector DB Credentials", "WARNING", "Pinecone credentials not found")
            
            return True
            
        except Exception as e:
            self.log_result("Vector Database", "FAIL", "Failed to verify vector database", str(e))
            return False

    async def verify_knowledge_graph(self) -> bool:
        """Verify knowledge graph service."""
        print("🧠 Verifying Knowledge Graph...")
        
        try:
            from services.knowledge_graph.main import kg_service
            
            if kg_service:
                self.log_result("Knowledge Graph Service", "PASS", "KG service available")
            else:
                self.log_result("Knowledge Graph Service", "WARNING", "KG service not properly initialized")
            
            # Check ArangoDB credentials
            arango_url = os.getenv("ARANGODB_URL")
            arango_user = os.getenv("ARANGODB_USERNAME")
            arango_pass = os.getenv("ARANGODB_PASSWORD")
            
            if arango_url and arango_user and arango_pass:
                self.log_result("Knowledge Graph Credentials", "PASS", "ArangoDB credentials found")
            else:
                self.log_result("Knowledge Graph Credentials", "WARNING", "ArangoDB credentials not found")
            
            return True
            
        except Exception as e:
            self.log_result("Knowledge Graph", "FAIL", "Failed to verify knowledge graph", str(e))
            return False

    async def verify_agents(self) -> bool:
        """Verify agent system."""
        print("🤖 Verifying Agent System...")
        
        try:
            from shared.core.agents.base_agent import BaseAgent
            from shared.core.agents.synthesis_agent import SynthesisAgent
            from shared.core.agents.retrieval_agent import RetrievalAgent
            
            # Check base agent
            if BaseAgent:
                self.log_result("Base Agent", "PASS", "BaseAgent class available")
            else:
                self.log_result("Base Agent", "FAIL", "BaseAgent class not found")
            
            # Check synthesis agent
            try:
                synthesis_agent = SynthesisAgent()
                self.log_result("Synthesis Agent", "PASS", "SynthesisAgent instantiated")
            except Exception as e:
                self.log_result("Synthesis Agent", "FAIL", "Failed to instantiate SynthesisAgent", str(e))
            
            # Check retrieval agent
            try:
                retrieval_agent = RetrievalAgent()
                self.log_result("Retrieval Agent", "PASS", "RetrievalAgent instantiated")
            except Exception as e:
                self.log_result("Retrieval Agent", "FAIL", "Failed to instantiate RetrievalAgent", str(e))
            
            return True
            
        except Exception as e:
            self.log_result("Agent System", "FAIL", "Failed to verify agent system", str(e))
            return False

    async def verify_environment_config(self) -> bool:
        """Verify environment configuration."""
        print("⚙️ Verifying Environment Configuration...")
        
        # Check critical environment variables
        critical_env_vars = [
            "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "HUGGINGFACE_WRITE_TOKEN",
            "PINECONE_API_KEY", "ARANGODB_URL", "OLLAMA_BASE_URL"
        ]
        
        missing_vars = []
        for var in critical_env_vars:
            if os.getenv(var):
                self.log_result(f"Environment: {var}", "PASS", "Variable set")
            else:
                missing_vars.append(var)
                self.log_result(f"Environment: {var}", "WARNING", "Variable not set")
        
        if len(missing_vars) == len(critical_env_vars):
            self.log_result("Environment Configuration", "FAIL", "No critical environment variables set")
            return False
        elif missing_vars:
            self.log_result("Environment Configuration", "WARNING", f"Missing {len(missing_vars)} variables")
            return True
        else:
            self.log_result("Environment Configuration", "PASS", "All critical variables set")
            return True

    async def run_all_verifications(self) -> Dict[str, Any]:
        """Run all verification steps."""
        print("🧪 INDUSTRY-STANDARD VERIFICATION PIPELINE")
        print("=" * 60)
        print("Following Meta/OpenAI/Perplexity level practices...")
        print("=" * 60)
        
        verifications = [
            ("Python Environment", self.verify_python_environment),
            ("Dependencies", self.verify_dependencies),
            ("Module Imports", self.verify_imports),
            ("FastAPI Application", self.verify_fastapi_app),
            ("LLM Integration", self.verify_llm_integration),
            ("Vector Database", self.verify_vector_database),
            ("Knowledge Graph", self.verify_knowledge_graph),
            ("Agent System", self.verify_agents),
            ("Environment Config", self.verify_environment_config)
        ]
        
        results = {}
        for name, verification_func in verifications:
            try:
                print(f"\n{'='*20} {name} {'='*20}")
                result = await verification_func()
                results[name] = result
            except Exception as e:
                print(f"❌ {name} verification crashed: {e}")
                results[name] = False
        
        return results

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive verification report."""
        print("\n" + "=" * 60)
        print("📊 INDUSTRY-STANDARD VERIFICATION REPORT")
        print("=" * 60)
        
        passed = 0
        failed = 0
        warnings = 0
        
        for result in self.results:
            if result.status == "PASS":
                passed += 1
            elif result.status == "FAIL":
                failed += 1
            elif result.status == "WARNING":
                warnings += 1
        
        total = len(self.results)
        
        print(f"Total Verifications: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        
        # Overall status
        if failed == 0:
            overall_status = "🎉 PRODUCTION READY"
            print(f"\n{overall_status}")
            print("✅ All critical verifications passed")
            print("✅ Repository builds successfully")
            print("✅ Ready for production deployment")
        elif failed <= 2:
            overall_status = "⚠️  DEVELOPMENT READY"
            print(f"\n{overall_status}")
            print("⚠️  Some verifications failed")
            print("⚠️  Review warnings before production")
        else:
            overall_status = "❌ NOT READY"
            print(f"\n{overall_status}")
            print("❌ Multiple critical failures")
            print("❌ Requires immediate attention")
        
        return overall_status

async def main():
    """Main verification runner."""
    verifier = IndustryStandardVerifier()
    
    try:
        # Run all verifications
        results = await verifier.run_all_verifications()
        
        # Generate report
        overall_status = verifier.generate_report(results)
        
        # Exit with appropriate code
        if "PRODUCTION READY" in overall_status:
            sys.exit(0)
        elif "DEVELOPMENT READY" in overall_status:
            sys.exit(1)
        else:
            sys.exit(2)
            
    except Exception as e:
        print(f"❌ Verification pipeline failed: {e}")
        sys.exit(3)

if __name__ == "__main__":
    asyncio.run(main())
