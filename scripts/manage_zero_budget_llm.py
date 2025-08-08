#!/usr/bin/env python3
"""
Manage Zero Budget LLM
Monitoring and management script for Ollama and Hugging Face integration
"""

import asyncio
import os
import sys
import time
import json
import httpx
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging
from pathlib import Path
import psutil
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

from shared.core.llm_client_v3 import EnhancedLLMClientV3
from shared.core.model_selector import get_model_selector

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ZeroBudgetLLMManager:
    """Manage and monitor zero-budget LLM providers."""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.hf_api_url = "https://api-inference.huggingface.co"
        self.metrics = {
            "ollama": {"requests": 0, "errors": 0, "last_check": None},
            "huggingface": {"requests": 0, "errors": 0, "last_check": None},
            "cost_savings": {"estimated_savings": 0.0, "last_calculation": None}
        }
    
    async def run_monitoring_dashboard(self):
        """Run the monitoring dashboard."""
        logger.info("📊 Starting Zero Budget LLM Monitoring Dashboard")
        print("=" * 60)
        
        while True:
            try:
                # Clear screen (works on most terminals)
                os.system('cls' if os.name == 'nt' else 'clear')
                
                # Display dashboard
                self._display_dashboard()
                
                # Check provider health
                await self._check_provider_health()
                
                # Update metrics
                await self._update_metrics()
                
                # Wait before next update
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except KeyboardInterrupt:
                logger.info("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(10)
    
    def _display_dashboard(self):
        """Display the monitoring dashboard."""
        print(f"\n📊 Zero Budget LLM Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Provider Status
        print("\n🏥 Provider Status:")
        ollama_status = "🟢 Online" if self._check_ollama_health() else "🔴 Offline"
        hf_status = "🟢 Online" if self._check_hf_health() else "🔴 Offline"
        
        print(f"   Ollama: {ollama_status}")
        print(f"   Hugging Face: {hf_status}")
        
        # Model Information
        print("\n🤖 Available Models:")
        ollama_models = self._get_ollama_models()
        hf_models = self._get_hf_models()
        
        print("   Ollama Models:")
        for model in ollama_models:
            print(f"     - {model}")
        
        print("   Hugging Face Models:")
        for model in hf_models:
            print(f"     - {model}")
        
        # Usage Metrics
        print("\n📈 Usage Metrics:")
        print(f"   Ollama Requests: {self.metrics['ollama']['requests']}")
        print(f"   Hugging Face Requests: {self.metrics['huggingface']['requests']}")
        print(f"   Total Errors: {self.metrics['ollama']['errors'] + self.metrics['huggingface']['errors']}")
        
        # Cost Savings
        print("\n💰 Cost Savings:")
        savings = self.metrics['cost_savings']['estimated_savings']
        print(f"   Estimated Savings: ${savings:.2f}")
        print(f"   Monthly Projection: ${savings * 30:.2f}")
        
        # System Resources
        print("\n💻 System Resources:")
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        print(f"   CPU Usage: {cpu_percent:.1f}%")
        print(f"   Memory Usage: {memory.percent:.1f}% ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)")
        
        # Quick Actions
        print("\n⚡ Quick Actions:")
        print("   Press 'q' to quit")
        print("   Press 't' to test providers")
        print("   Press 'r' to restart Ollama")
        print("   Press 'm' to show model details")
        
        print("\n" + "=" * 60)
    
    async def _check_ollama_health(self) -> bool:
        """Check if Ollama is healthy."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ollama_url}/api/tags", timeout=5.0)
                return response.status_code == 200
        except Exception:
            return False
    
    async def _check_hf_health(self) -> bool:
        """Check if Hugging Face API is healthy."""
        try:
            # Check for any available token
            write_token = settings.huggingface_write_token
            read_token = settings.huggingface_read_token
            legacy_api_key = settings.huggingface_api_key
            
            token = write_token or read_token or legacy_api_key
            if not token:
                return False
            
            headers = {"Authorization": f"Bearer {token}"}
            async with httpx.AsyncClient() as client:
                response = await client.get("https://huggingface.co/api/models", 
                                          headers=headers, timeout=10.0)
                return response.status_code == 200
        except Exception:
            return False
    
    async def _get_ollama_models(self) -> list:
        """Get list of available Ollama models."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ollama_url}/api/tags", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    return [model['name'] for model in data.get('models', [])]
        except Exception:
            pass
        return []
    
    def _get_hf_models(self) -> list:
        """Get list of available Hugging Face models."""
        return [
            "microsoft/DialoGPT-medium",
            "microsoft/DialoGPT-large",
            "distilgpt2",
            "EleutherAI/gpt-neo-125M",
            "Salesforce/codegen-350M-mono"
        ]
    
    async def _check_provider_health(self):
        """Check health of all providers."""
        # Check Ollama
        if await self._check_ollama_health():
            self.metrics['ollama']['last_check'] = datetime.now()
        else:
            self.metrics['ollama']['errors'] += 1
        
        # Check Hugging Face
        if await self._check_hf_health():
            self.metrics['huggingface']['last_check'] = datetime.now()
        else:
            self.metrics['huggingface']['errors'] += 1
    
    async def _update_metrics(self):
        """Update usage metrics."""
        # Simulate request tracking (in real implementation, this would come from actual usage)
        if await self._check_ollama_health():
            self.metrics['ollama']['requests'] += 1
        
        if await self._check_hf_health():
            self.metrics['huggingface']['requests'] += 1
        
        # Calculate cost savings
        total_requests = self.metrics['ollama']['requests'] + self.metrics['huggingface']['requests']
        # Assume average cost of $0.01 per request for paid models
        self.metrics['cost_savings']['estimated_savings'] = total_requests * 0.01
        self.metrics['cost_savings']['last_calculation'] = datetime.now()
    
    async def test_providers(self):
        """Test all providers with sample requests."""
        logger.info("🧪 Testing providers...")
        
        # Test Ollama
        if await self._check_ollama_health():
            try:
                client = EnhancedLLMClientV3()
                response = await client.generate_text(
                    prompt="Hello, this is a test.",
                    max_tokens=20,
                    temperature=0.1
                )
                logger.info("✅ Ollama test successful")
                print(f"   Response: {response[:50]}...")
            except Exception as e:
                logger.error(f"❌ Ollama test failed: {e}")
        else:
            logger.warning("⚠️  Ollama not available for testing")
        
        # Test Hugging Face
        if await self._check_hf_health():
            try:
                # Test with a simple model
                model_name = "microsoft/DialoGPT-medium"
                headers = {"Authorization": f"Bearer {settings.huggingface_api_key}"}
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"https://api-inference.huggingface.co/models/{model_name}",
                        json={"inputs": "Hello, how are you?"},
                        headers=headers,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        logger.info("✅ Hugging Face test successful")
                        print(f"   Response: {response.json()[:50]}...")
                    else:
                        logger.error(f"❌ Hugging Face test failed: {response.status_code}")
            except Exception as e:
                logger.error(f"❌ Hugging Face test failed: {e}")
        else:
            logger.warning("⚠️  Hugging Face not available for testing")
    
    def restart_ollama(self):
        """Restart Ollama service."""
        logger.info("🔄 Restarting Ollama...")
        
        try:
            # Stop Ollama
            subprocess.run(["pkill", "ollama"], capture_output=True)
            time.sleep(2)
            
            # Start Ollama
            subprocess.Popen(["ollama", "serve"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
            # Wait for service to start
            for i in range(30):
                if self._check_ollama_health():
                    logger.info("✅ Ollama restarted successfully")
                    return True
                time.sleep(1)
            
            logger.error("❌ Ollama restart failed")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to restart Ollama: {e}")
            return False
    
    def show_model_details(self):
        """Show detailed information about available models."""
        logger.info("📋 Model Details:")
        
        print("\n🤖 Ollama Models (Local):")
        ollama_models = self._get_ollama_models()
        for model in ollama_models:
            print(f"   - {model}")
            print(f"     Cost: $0.00/1K tokens")
            print(f"     Type: Local inference")
            print(f"     Status: {'Available' if self._check_ollama_health() else 'Unavailable'}")
        
        print("\n🤖 Hugging Face Models (API):")
        hf_models = self._get_hf_models()
        for model in hf_models:
            print(f"   - {model}")
            print(f"     Cost: $0.00/1K tokens")
            print(f"     Type: API inference")
            print(f"     Status: {'Available' if self._check_hf_health() else 'Unavailable'}")
        
        print("\n💰 Cost Comparison:")
        print("   Paid Models (for reference):")
        print("   - GPT-4: $0.03/1K tokens")
        print("   - Claude: $0.015/1K tokens")
        print("   - GPT-3.5: $0.0015/1K tokens")
        print("\n   Free Models:")
        print("   - Ollama: $0.00/1K tokens")
        print("   - Hugging Face: $0.00/1K tokens")
    
    async def run_interactive_mode(self):
        """Run interactive management mode."""
        logger.info("🎮 Starting Interactive Mode")
        print("=" * 60)
        
        while True:
            print("\n📊 Zero Budget LLM Manager")
            print("1. Show Dashboard")
            print("2. Test Providers")
            print("3. Restart Ollama")
            print("4. Show Model Details")
            print("5. Run Performance Test")
            print("6. Export Metrics")
            print("7. Quit")
            
            choice = input("\nSelect option (1-7): ").strip()
            
            if choice == "1":
                self._display_dashboard()
            elif choice == "2":
                await self.test_providers()
            elif choice == "3":
                self.restart_ollama()
            elif choice == "4":
                self.show_model_details()
            elif choice == "5":
                await self.run_performance_test()
            elif choice == "6":
                self.export_metrics()
            elif choice == "7":
                logger.info("👋 Goodbye!")
                break
            else:
                print("❌ Invalid option")
    
    async def run_performance_test(self):
        """Run performance test on available providers."""
        logger.info("⚡ Running Performance Test...")
        
        test_prompts = [
            "Hello, how are you?",
            "What is the capital of France?",
            "Write a simple Python function to add two numbers.",
            "Explain the concept of machine learning in one sentence."
        ]
        
        client = EnhancedLLMClientV3()
        
        for i, prompt in enumerate(test_prompts, 1):
            try:
                start_time = time.time()
                response = await client.generate_text(
                    prompt=prompt,
                    max_tokens=50,
                    temperature=0.1
                )
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                print(f"✅ Test {i}: {response_time:.0f}ms - {response[:50]}...")
                
            except Exception as e:
                print(f"❌ Test {i} failed: {e}")
    
    def export_metrics(self):
        """Export metrics to JSON file."""
        try:
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "metrics": self.metrics,
                "providers": {
                    "ollama": {
                        "health": self._check_ollama_health(),
                        "models": self._get_ollama_models()
                    },
                    "huggingface": {
                        "health": self._check_hf_health(),
                        "models": self._get_hf_models()
                    }
                }
            }
            
            filename = f"llm_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"✅ Metrics exported to {filename}")
            
        except Exception as e:
            logger.error(f"❌ Failed to export metrics: {e}")

async def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage Zero Budget LLM Providers")
    parser.add_argument("--dashboard", action="store_true", help="Run monitoring dashboard")
    parser.add_argument("--interactive", action="store_true", help="Run interactive mode")
    parser.add_argument("--test", action="store_true", help="Test providers")
    parser.add_argument("--restart-ollama", action="store_true", help="Restart Ollama service")
    parser.add_argument("--models", action="store_true", help="Show model details")
    
    args = parser.parse_args()
    
    manager = ZeroBudgetLLMManager()
    
    if args.dashboard:
        await manager.run_monitoring_dashboard()
    elif args.interactive:
        await manager.run_interactive_mode()
    elif args.test:
        await manager.test_providers()
    elif args.restart_ollama:
        manager.restart_ollama()
    elif args.models:
        manager.show_model_details()
    else:
        # Default to interactive mode
        await manager.run_interactive_mode()

if __name__ == "__main__":
    asyncio.run(main()) 