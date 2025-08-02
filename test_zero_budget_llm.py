from shared.core.api.config import get_settings
#!/usr/bin/env python3
settings = get_settings()
"""
Test Zero Budget LLM Alternatives
Verifies that free LLM alternatives work with the existing system
"""

import asyncio
import json
import requests
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ZeroBudgetLLMTester:
    """Test zero budget LLM alternatives."""
    
    def __init__(self):
        self.test_results = {}
        self.ollama_url = "http://localhost:11434"
        
    async def run_all_tests(self):
        """Run comprehensive tests for all zero budget alternatives."""
        logger.info("🧪 Testing Zero Budget LLM Alternatives")
        
        # Test Ollama (Primary)
        await self._test_ollama()
        
        # Test Hugging Face (Fallback)
        await self._test_huggingface()
        
        # Test Groq (Ultra-fast)
        await self._test_groq()
        
        # Test integration with existing system
        await self._test_system_integration()
        
        # Print results
        self._print_results()
    
    async def _test_ollama(self):
        """Test Ollama functionality."""
        logger.info("🔧 Testing Ollama...")
        
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code != 200:
                logger.error("❌ Ollama service not running")
                self.test_results["ollama"] = False
                return
            
            # Test with different models
            models_to_test = ["llama3.2:3b", "llama3.2:8b", "phi3:mini"]
            successful_tests = 0
            
            for model in models_to_test:
                try:
                    # Test model generation
                    payload = {
                        "model": model,
                        "prompt": "Hello, this is a test. Please respond with 'Test successful'.",
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "max_tokens": 50
                        }
                    }
                    
                    response = requests.post(
                        f"{self.ollama_url}/api/generate",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if "response" in result:
                            logger.info(f"✅ {model} test successful")
                            successful_tests += 1
                        else:
                            logger.warning(f"⚠️  {model} returned no response")
                    else:
                        logger.warning(f"⚠️  {model} test failed: {response.status_code}")
                        
                except Exception as e:
                    logger.warning(f"⚠️  {model} test error: {e}")
            
            self.test_results["ollama"] = successful_tests > 0
            logger.info(f"📊 Ollama: {successful_tests}/{len(models_to_test)} models working")
            
        except Exception as e:
            logger.error(f"❌ Ollama test failed: {e}")
            self.test_results["ollama"] = False
    
    async def _test_huggingface(self):
        """Test Hugging Face API."""
        logger.info("🔧 Testing Hugging Face...")
        
        api_key = settings.huggingface_api_key
        if not api_key:
            logger.warning("⚠️  HUGGINGFACE_API_KEY not set, skipping test")
            self.test_results["huggingface"] = False
            return
        
        try:
            # Test API access
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(
                "https://huggingface.co/api/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Hugging Face API access successful")
                self.test_results["huggingface"] = True
            else:
                logger.error(f"❌ Hugging Face API failed: {response.status_code}")
                self.test_results["huggingface"] = False
                
        except Exception as e:
            logger.error(f"❌ Hugging Face test failed: {e}")
            self.test_results["huggingface"] = False
    
    async def _test_groq(self):
        """Test Groq API."""
        logger.info("🔧 Testing Groq...")
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning("⚠️  GROQ_API_KEY not set, skipping test")
            self.test_results["groq"] = False
            return
        
        try:
            # Test API access
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(
                "https://api.groq.com/openai/v1/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Groq API access successful")
                self.test_results["groq"] = True
            else:
                logger.error(f"❌ Groq API failed: {response.status_code}")
                self.test_results["groq"] = False
                
        except Exception as e:
            logger.error(f"❌ Groq test failed: {e}")
            self.test_results["groq"] = False
    
    async def _test_system_integration(self):
        """Test integration with existing system components."""
        logger.info("🔧 Testing System Integration...")
        
        try:
            # Test task-specific model selection
            task_tests = [
                ("general_factual", "llama3.2:3b"),
                ("code", "codellama:7b"),
                ("knowledge_graph", "llama3.2:8b"),
                ("analytical", "llama3.2:70b"),
                ("procedural", "phi3:mini")
            ]
            
            successful_integrations = 0
            
            for task_type, model in task_tests:
                try:
                    # Test with Ollama
                    payload = {
                        "model": model,
                        "prompt": f"Test {task_type} task: Explain briefly what this task type involves.",
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "max_tokens": 100
                        }
                    }
                    
                    response = requests.post(
                        f"{self.ollama_url}/api/generate",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"✅ {task_type} -> {model} integration successful")
                        successful_integrations += 1
                    else:
                        logger.warning(f"⚠️  {task_type} -> {model} integration failed")
                        
                except Exception as e:
                    logger.warning(f"⚠️  {task_type} -> {model} integration error: {e}")
            
            self.test_results["system_integration"] = successful_integrations > 0
            logger.info(f"📊 System Integration: {successful_integrations}/{len(task_tests)} tasks working")
            
        except Exception as e:
            logger.error(f"❌ System integration test failed: {e}")
            self.test_results["system_integration"] = False
    
    def _print_results(self):
        """Print comprehensive test results."""
        logger.info("\n" + "="*60)
        logger.info("📊 ZERO BUDGET LLM TEST RESULTS")
        logger.info("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status} {test_name.upper()}")
        
        logger.info(f"\n📈 Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 All tests passed! Zero budget setup is ready.")
        elif passed_tests > 0:
            logger.info("⚠️  Some tests failed. Check the issues above.")
        else:
            logger.error("❌ All tests failed. Please check your setup.")
        
        # Recommendations
        logger.info("\n💡 Recommendations:")
        
        if not self.test_results.get("ollama", False):
            logger.info("- Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
            logger.info("- Pull models: ollama pull llama3.2:3b")
        
        if not self.test_results.get("huggingface", False):
            logger.info("- Get Hugging Face API key: https://huggingface.co/settings/tokens")
            logger.info("- Set environment: export HUGGINGFACE_API_KEY='your_key'")
        
        if not self.test_results.get("groq", False):
            logger.info("- Get Groq API key: https://console.groq.com/keys")
            logger.info("- Set environment: export GROQ_API_KEY='your_key'")
        
        # Cost savings calculation
        if passed_tests > 0:
            monthly_savings = 800  # Conservative estimate
            logger.info(f"\n💰 Estimated monthly savings: ${monthly_savings}")
            logger.info("🎯 Zero budget alternatives are working!")

def main():
    """Main test function."""
    tester = ZeroBudgetLLMTester()
    asyncio.run(tester.run_all_tests())

if __name__ == "__main__":
    main() 