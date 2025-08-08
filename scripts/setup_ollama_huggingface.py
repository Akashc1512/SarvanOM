
#!/usr/bin/env python3
"""
Ollama and Hugging Face setup script for Universal Knowledge Hub.
"""

import asyncio
import os
import sys
import subprocess
import platform
import time
import json
import httpx
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OllamaHuggingFaceSetup:
    """Setup and configure Ollama and Hugging Face for the system."""
    
    def __init__(self):
        self.setup_status = {
            "ollama": {"installed": False, "models": [], "health": False},
            "huggingface": {"configured": False, "api_key": False, "health": False}
        }
        self.required_ollama_models = [
            "llama3.2:3b",
            "llama3.2:8b", 
            "codellama:7b",
            "phi3:mini"
        ]
        self.optional_ollama_models = [
            "llama3.2:70b",
            "mixtral:8x7b"
        ]
    
    async def run_complete_setup(self):
        """Run the complete setup process."""
        logger.info("🚀 Starting Ollama & Hugging Face Setup")
        logger.info("=" * 50)
        
        # Check system requirements
        await self._check_system_requirements()
        
        # Setup Ollama
        self._setup_ollama()
        
        # Setup Hugging Face
        await self._setup_huggingface()
        
        # Update environment configuration
        self._update_environment_config()
        
        # Test setup
        await self._test_setup()
        
        # Print summary
        self._print_setup_summary()
        
        logger.info("✅ Setup complete!")
    
    async def _check_system_requirements(self):
        """Check if system meets requirements for local models."""
        logger.info("🔍 Checking system requirements...")
        
        # Check available RAM
        try:
            import psutil
            ram_gb = psutil.virtual_memory().total / (1024**3)
            logger.info(f"📊 Available RAM: {ram_gb:.1f} GB")
            
            if ram_gb < 8:
                logger.warning("⚠️  Warning: Less than 8GB RAM detected. Some models may not work optimally.")
            elif ram_gb >= 16:
                logger.info("✅ Sufficient RAM for all models")
            else:
                logger.info("✅ Adequate RAM for most models")
                
        except ImportError:
            logger.warning("⚠️  psutil not available. Cannot check RAM.")
        
        # Check available storage
        try:
            import shutil
            free_space_gb = shutil.disk_usage('/').free / (1024**3)
            logger.info(f"💾 Available storage: {free_space_gb:.1f} GB")
            
            if free_space_gb < 10:
                logger.warning("⚠️  Warning: Less than 10GB free space. Consider freeing up space.")
            else:
                logger.info("✅ Sufficient storage space")
                
        except Exception as e:
            logger.warning(f"⚠️  Could not check storage: {e}")
        
        # Check internet connectivity
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://ollama.ai", timeout=5.0)
                if response.status_code == 200:
                    logger.info("✅ Internet connectivity: Good")
                else:
                    logger.warning("⚠️  Internet connectivity: Limited")
        except Exception:
            logger.warning("⚠️  Internet connectivity: Poor")
    
    def _setup_ollama(self):
        """Setup Ollama for local model inference."""
        logger.info("🔧 Setting up Ollama...")
        
        # Check if Ollama is already installed
        if self._check_ollama_installed():
            logger.info("✅ Ollama already installed")
            self.setup_status["ollama"]["installed"] = True
        else:
            logger.info("📥 Installing Ollama...")
            if self._install_ollama():
                self.setup_status["ollama"]["installed"] = True
            else:
                logger.error("❌ Ollama installation failed")
                return
        
        # Start Ollama service
        if self._start_ollama_service():
            self.setup_status["ollama"]["health"] = True
        
        # Pull required models
        self._pull_ollama_models()
        
        logger.info("✅ Ollama setup complete")
    
    def _check_ollama_installed(self) -> bool:
        """Check if Ollama is installed."""
        try:
            result = subprocess.run(["ollama", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _install_ollama(self) -> bool:
        """Install Ollama based on the operating system."""
        try:
            os_name = platform.system().lower()
            
            if os_name == "windows":
                logger.info("📥 Installing Ollama on Windows...")
                # Windows installation
                install_script = """
                Invoke-WebRequest -Uri https://ollama.ai/install.ps1 -OutFile install.ps1
                .\\install.ps1
                """
                subprocess.run(["powershell", "-Command", install_script], check=True)
                
            elif os_name == "darwin":  # macOS
                logger.info("📥 Installing Ollama on macOS...")
                subprocess.run(["curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"], check=True)
                
            else:  # Linux
                logger.info("📥 Installing Ollama on Linux...")
                subprocess.run(["curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"], check=True)
            
            # Verify installation
            time.sleep(2)
            if self._check_ollama_installed():
                logger.info("✅ Ollama installed successfully")
                return True
            else:
                logger.error("❌ Ollama installation verification failed")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Ollama installation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error during Ollama installation: {e}")
            return False
    
    async def _start_ollama_service(self) -> bool:
        """Start Ollama service."""
        try:
            # Check if Ollama is running
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:11434/api/tags", timeout=5.0)
                if response.status_code == 200:
                    logger.info("✅ Ollama service is running")
                    return True
        except Exception:
            pass
        
        logger.info("🚀 Starting Ollama service...")
        try:
            # Start Ollama in background
            if platform.system().lower() == "windows":
                subprocess.Popen(["ollama", "serve"], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen(["ollama", "serve"], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            
            # Wait for service to start
            for i in range(30):
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get("http://localhost:11434/api/tags", timeout=2.0)
                        if response.status_code == 200:
                            logger.info("✅ Ollama service started successfully")
                            return True
                except Exception:
                    pass
                await asyncio.sleep(1)
            
            logger.warning("⚠️  Ollama service may not have started properly")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to start Ollama service: {e}")
            return False
    
    def _pull_ollama_models(self):
        """Pull required and optional Ollama models."""
        logger.info("📥 Pulling Ollama models...")
        
        # Pull required models
        logger.info("📥 Pulling required models...")
        for model in self.required_ollama_models:
            if self._pull_model(model):
                self.setup_status["ollama"]["models"].append(model)
        
        # Ask user about optional models
        print("\n🤔 Optional Models (require more RAM):")
        print("   - llama3.2:70b (40GB RAM)")
        print("   - mixtral:8x7b (32GB RAM)")
        
        try:
            import psutil
            ram_gb = psutil.virtual_memory().total / (1024**3)
            
            if ram_gb >= 32:
                response = input("   Pull optional models? (y/N): ").lower().strip()
                if response == 'y':
                    logger.info("📥 Pulling optional models...")
                    for model in self.optional_ollama_models:
                        if self._pull_model(model):
                            self.setup_status["ollama"]["models"].append(model)
            else:
                logger.info("⚠️  Skipping optional models due to insufficient RAM")
                
        except ImportError:
            logger.info("⚠️  Cannot check RAM, skipping optional models")
    
    def _pull_model(self, model: str) -> bool:
        """Pull a specific Ollama model."""
        try:
            logger.info(f"📥 Pulling {model}...")
            subprocess.run(["ollama", "pull", model], 
                          check=True, timeout=300)  # 5 minute timeout
            logger.info(f"✅ {model} pulled successfully")
            return True
        except subprocess.TimeoutExpired:
            logger.warning(f"⚠️  Timeout pulling {model}. You can pull it manually later.")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to pull {model}: {e}")
            return False
    
    async def _setup_huggingface(self):
        """Setup Hugging Face API access."""
        logger.info("🔧 Setting up Hugging Face...")
        
        # Get API key from user
        api_key = input("📝 Enter your Hugging Face API key (or press Enter to skip): ").strip()
        
        if not api_key:
            logger.info("💡 You can get your API key from: https://huggingface.co/settings/tokens")
            logger.warning("⚠️  Hugging Face setup skipped")
            return
        
        # Test API key
        if await self._test_huggingface_api_key(api_key):
            logger.info("✅ Hugging Face API key is valid")
            self.setup_status["huggingface"]["configured"] = True
            
            # Save to environment
            self._save_api_key_to_env("HUGGINGFACE_API_KEY", api_key)
            
            # Test health
            if await self._test_huggingface_health():
                self.setup_status["huggingface"]["health"] = True
                logger.info("✅ Hugging Face setup complete")
            else:
                logger.warning("⚠️  Hugging Face health check failed")
        else:
            logger.error("❌ Invalid Hugging Face API key")
    
    async def _test_huggingface_api_key(self, api_key: str) -> bool:
        """Test if the Hugging Face API key is valid."""
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            async with httpx.AsyncClient() as client:
                response = await client.get("https://huggingface.co/api/models", 
                                  headers=headers, timeout=10.0)
            return response.status_code == 200
        except Exception:
            return False
    
    async def _test_huggingface_health(self) -> bool:
        """Test Hugging Face API health."""
        try:
            api_key = os.getenv("HUGGINGFACE_API_KEY")
            if not api_key:
                return False
            
            headers = {"Authorization": f"Bearer {api_key}"}
            async with httpx.AsyncClient() as client:
                response = await client.get("https://huggingface.co/api/models", 
                                  headers=headers, timeout=10.0)
            return response.status_code == 200
        except Exception:
            return False
    
    def _save_api_key_to_env(self, key_name: str, value: str):
        """Save API key to environment file."""
        try:
            env_file = Path(".env")
            if env_file.exists():
                # Read existing file
                with open(env_file, 'r') as f:
                    lines = f.readlines()
                
                # Check if key already exists
                key_exists = any(line.startswith(f"{key_name}=") for line in lines)
                
                if key_exists:
                    # Update existing key
                    for i, line in enumerate(lines):
                        if line.startswith(f"{key_name}="):
                            lines[i] = f"{key_name}={value}\n"
                            break
                else:
                    # Add new key
                    lines.append(f"{key_name}={value}\n")
                
                # Write back to file
                with open(env_file, 'w') as f:
                    f.writelines(lines)
            else:
                # Create new .env file
                with open(env_file, 'w') as f:
                    f.write(f"{key_name}={value}\n")
            
            logger.info(f"✅ Saved {key_name} to .env file")
            
        except Exception as e:
            logger.warning(f"⚠️  Could not save to .env file: {e}")
    
    def _update_environment_config(self):
        """Update environment configuration."""
        logger.info("⚙️  Updating environment configuration...")
        
        # Create or update .env file with Ollama settings
        env_settings = [
            "OLLAMA_ENABLED=true",
            "OLLAMA_MODEL=llama3.2:3b",
            "OLLAMA_BASE_URL=http://localhost:11434"
        ]
        
        # Add Hugging Face settings if configured
        if self.setup_status["huggingface"]["configured"]:
            env_settings.extend([
                "HUGGINGFACE_MODEL=microsoft/DialoGPT-medium"
            ])
            
            # Add token settings based on what's available
            if os.getenv("HUGGINGFACE_WRITE_TOKEN"):
                env_settings.append("# HUGGINGFACE_WRITE_TOKEN=your_write_token_here")
            if os.getenv("HUGGINGFACE_READ_TOKEN"):
                env_settings.append("# HUGGINGFACE_READ_TOKEN=your_read_token_here")
            if os.getenv("HUGGINGFACE_API_KEY"):
                env_settings.append("# HUGGINGFACE_API_KEY=your_legacy_api_key_here")
        
        # Write to .env file
        try:
            env_file = Path(".env")
            existing_lines = []
            
            if env_file.exists():
                with open(env_file, 'r') as f:
                    existing_lines = f.readlines()
            
            # Add new settings if they don't exist
            for setting in env_settings:
                key = setting.split('=')[0]
                if not any(line.startswith(f"{key}=") for line in existing_lines):
                    existing_lines.append(f"{setting}\n")
            
            with open(env_file, 'w') as f:
                f.writelines(existing_lines)
            
            logger.info("✅ Environment configuration updated")
            
        except Exception as e:
            logger.warning(f"⚠️  Could not update environment configuration: {e}")
    
    async def _test_setup(self):
        """Test the complete setup."""
        logger.info("🧪 Testing setup...")
        
        # Test Ollama
        if self.setup_status["ollama"]["installed"]:
            logger.info("🧪 Testing Ollama...")
            if await self._test_ollama_models():
                self.setup_status["ollama"]["tested"] = True
                logger.info("✅ Ollama test successful")
            else:
                logger.error("❌ Ollama test failed")
        
        # Test Hugging Face
        if self.setup_status["huggingface"]["configured"]:
            logger.info("🧪 Testing Hugging Face...")
            if await self._test_huggingface_models():
                self.setup_status["huggingface"]["tested"] = True
                logger.info("✅ Hugging Face test successful")
            else:
                logger.error("❌ Hugging Face test failed")
    
    async def _test_ollama_models(self) -> bool:
        """Test Ollama model functionality."""
        try:
            # Test basic API
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:11434/api/tags", timeout=5.0)
                if response.status_code != 200:
                    logger.error("❌ Ollama API not responding")
                    return False
            
            # Test model generation
            test_data = {
                "model": "llama3.2:3b",
                "prompt": "Hello, how are you?",
                "stream": False
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post("http://localhost:11434/api/generate", 
                                          json=test_data, timeout=30.0)
                if response.status_code == 200:
                    logger.info("✅ Ollama model test successful")
                    return True
                else:
                    logger.error(f"❌ Ollama model test failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Ollama model test failed: {e}")
            return False

    async def _test_huggingface_models(self) -> bool:
        """Test Hugging Face model access."""
        try:
            api_key = os.getenv("HUGGINGFACE_API_KEY")
            if not api_key:
                logger.warning("⚠️  No Hugging Face API key configured")
                return False
            
            headers = {"Authorization": f"Bearer {api_key}"}
            async with httpx.AsyncClient() as client:
                response = await client.get("https://huggingface.co/api/models", 
                                         headers=headers, timeout=10.0)
                if response.status_code == 200:
                    logger.info("✅ Hugging Face model test successful")
                    return True
                else:
                    logger.error(f"❌ Hugging Face model test failed: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"❌ Hugging Face model test failed: {e}")
            return False
    
    def _print_setup_summary(self):
        """Print comprehensive setup summary."""
        print("\n" + "=" * 60)
        print("📊 SETUP SUMMARY")
        print("=" * 60)
        
        # Ollama status
        print(f"\n🔧 Ollama Status:")
        print(f"   Installed: {'✅' if self.setup_status['ollama']['installed'] else '❌'}")
        print(f"   Service: {'✅' if self.setup_status['ollama']['health'] else '❌'}")
        print(f"   Models: {len(self.setup_status['ollama']['models'])} available")
        for model in self.setup_status['ollama']['models']:
            print(f"     - {model}")
        
        # Hugging Face status
        print(f"\n🔧 Hugging Face Status:")
        print(f"   Configured: {'✅' if self.setup_status['huggingface']['configured'] else '❌'}")
        print(f"   API Key: {'✅' if self.setup_status['huggingface']['api_key'] else '❌'}")
        print(f"   Health: {'✅' if self.setup_status['huggingface']['health'] else '❌'}")
        
        # Cost savings
        total_models = len(self.setup_status['ollama']['models'])
        if total_models > 0 or self.setup_status['huggingface']['configured']:
            print(f"\n💰 Cost Savings:")
            print(f"   Free models available: {total_models + (1 if self.setup_status['huggingface']['configured'] else 0)}")
            print(f"   Estimated monthly savings: $800-1600")
            print(f"   Zero ongoing costs for LLM inference")
        
        # Next steps
        print(f"\n🚀 Next Steps:")
        print(f"   1. Test the integration: python test_updated_logic.py")
        print(f"   2. Run your agents: python run_server.py")
        print(f"   3. Monitor performance and adjust as needed")
        
        # Troubleshooting
        print(f"\n🔧 Troubleshooting:")
        if not self.setup_status['ollama']['health']:
            print(f"   - Ollama service not running: ollama serve")
        if not self.setup_status['huggingface']['configured']:
            print(f"   - Get Hugging Face API key: https://huggingface.co/settings/tokens")
        print(f"   - Check logs for detailed error messages")
        print(f"   - Test individual components: python test_llm_integration.py")

async def main():
    """Main function."""
    setup = OllamaHuggingFaceSetup()
    await setup.run_complete_setup()

if __name__ == "__main__":
    asyncio.run(main()) 