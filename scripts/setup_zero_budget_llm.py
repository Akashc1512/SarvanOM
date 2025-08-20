#!/usr/bin/env python3
"""
Zero-budget LLM setup script for Universal Knowledge Hub.
"""

import asyncio
import os
import sys
import subprocess
import time
import json
import httpx
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZeroBudgetLLMSetup:
    """Setup and configure zero-budget LLM alternatives."""

    def __init__(self):
        self.config_path = Path("config/zero_budget_llm_alternatives.json")
        self.setup_status = {"ollama": False, "huggingface": False, "groq": False}

    async def run_setup(self):
        """Run the complete setup process."""
        logger.info("🚀 Starting Zero-Budget LLM Setup")
        logger.info("=" * 50)

        # Check system requirements
        if not self._check_system_requirements():
            logger.error("❌ System requirements not met")
            return False

        # Setup Ollama
        if not self._check_ollama_installed():
            self._install_ollama()

        await self._start_ollama_service()
        self._pull_ollama_models()

        # Setup APIs
        await self._setup_huggingface()
        await self._setup_groq()

        # Update configuration
        self._update_model_config()

        # Test setup
        await self._test_setup()

        # Print summary
        self._print_summary()

        return True

    def _check_system_requirements(self):
        """Check if system meets requirements for local models."""
        logger.info("🔍 Checking system requirements...")

        # Check available RAM
        try:
            import psutil

            ram_gb = psutil.virtual_memory().total / (1024**3)
            logger.info(f"📊 Available RAM: {ram_gb:.1f} GB")

            if ram_gb < 8:
                logger.warning(
                    "⚠️  Warning: Less than 8GB RAM detected. Some models may not work optimally."
                )
            elif ram_gb >= 16:
                logger.info("✅ Sufficient RAM for all models")
            else:
                logger.info("✅ Adequate RAM for most models")

        except ImportError:
            logger.warning("⚠️  psutil not available. Cannot check RAM.")

        # Check available storage
        try:
            import shutil

            free_space_gb = shutil.disk_usage("/").free / (1024**3)
            logger.info(f"💾 Available storage: {free_space_gb:.1f} GB")

            if free_space_gb < 10:
                logger.warning(
                    "⚠️  Warning: Less than 10GB free space. Consider freeing up space."
                )
            else:
                logger.info("✅ Sufficient storage space")

        except Exception as e:
            logger.warning(f"⚠️  Could not check storage: {e}")

    def _check_ollama_installed(self) -> bool:
        """Check if Ollama is installed."""
        try:
            result = subprocess.run(
                ["ollama", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _install_ollama(self):
        """Install Ollama."""
        try:
            if sys.platform == "win32":
                logger.info("📥 Installing Ollama on Windows...")
                # Windows installation
                subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        r"Invoke-WebRequest -Uri https://ollama.ai/install.ps1 -OutFile install.ps1; .\install.ps1",
                    ],
                    check=True,
                )
            else:
                logger.info("📥 Installing Ollama...")
                subprocess.run(
                    ["curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"],
                    check=True,
                )
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install Ollama: {e}")
            raise

    async def _start_ollama_service(self):
        """Start Ollama service."""
        try:
            # Check if Ollama is running
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://localhost:11434/api/tags", timeout=5.0
                )
                if response.status_code == 200:
                    logger.info("✅ Ollama service is running")
                    return
        except Exception:
            pass

        logger.info("🚀 Starting Ollama service...")
        try:
            # Start Ollama in background
            if sys.platform == "win32":
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

            # Wait for service to start
            for i in range(30):
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(
                            "http://localhost:11434/api/tags", timeout=2.0
                        )
                        if response.status_code == 200:
                            logger.info("✅ Ollama service started successfully")
                            return
                except Exception:
                    pass
                await asyncio.sleep(1)

            logger.warning("⚠️  Ollama service may not have started properly")

        except Exception as e:
            logger.error(f"❌ Failed to start Ollama service: {e}")

    def _pull_ollama_models(self):
        """Pull required Ollama models."""
        required_models = ["llama3.2:3b", "llama3.2:8b", "codellama:7b", "phi3:mini"]

        logger.info("📥 Pulling required models...")

        for model in required_models:
            logger.info(f"📥 Pulling {model}...")
            try:
                subprocess.run(
                    ["ollama", "pull", model], check=True, timeout=300
                )  # 5 minute timeout
                logger.info(f"✅ {model} pulled successfully")
            except subprocess.TimeoutExpired:
                logger.warning(
                    f"⚠️  Timeout pulling {model}. You can pull it manually later."
                )
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to pull {model}: {e}")

    async def _setup_huggingface(self):
        """Setup Hugging Face API access."""
        logger.info("🔧 Setting up Hugging Face...")

        api_key = settings.huggingface_api_key
        if not api_key:
            logger.info(
                "📝 Please get your Hugging Face API key from: https://huggingface.co/settings/tokens"
            )
            logger.info("💡 Set it as environment variable: HUGGINGFACE_API_KEY")
            logger.warning("⚠️  Hugging Face setup incomplete - API key required")
            return

        # Test API key
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://huggingface.co/api/models", headers=headers, timeout=10.0
                )
                if response.status_code == 200:
                    logger.info("✅ Hugging Face API key is valid")
                    self.setup_status["huggingface"] = True
                else:
                    logger.error("❌ Invalid Hugging Face API key")
        except Exception as e:
            logger.error(f"❌ Failed to test Hugging Face API: {e}")

    async def _setup_groq(self):
        """Setup Groq API access."""
        logger.info("🔧 Setting up Groq...")

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.info(
                "📝 Please get your Groq API key from: https://console.groq.com/keys"
            )
            logger.info("💡 Set it as environment variable: GROQ_API_KEY")
            logger.warning("⚠️  Groq setup incomplete - API key required")
            return

        # Test API key
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.groq.com/openai/v1/models",
                    headers=headers,
                    timeout=10.0,
                )
                if response.status_code == 200:
                    logger.info("✅ Groq API key is valid")
                    self.setup_status["groq"] = True
                else:
                    logger.error("❌ Invalid Groq API key")
        except Exception as e:
            logger.error(f"❌ Failed to test Groq API: {e}")

    def _update_model_config(self):
        """Update the model selection configuration to include zero-budget alternatives."""
        logger.info("⚙️  Updating model configuration...")

        # Load current config
        model_config_path = Path("config/model_selection.json")
        if model_config_path.exists():
            with open(model_config_path, "r") as f:
                config = json.load(f)
        else:
            logger.warning("⚠️  Model selection config not found, creating new one")
            config = {"model_selection": {"enabled": True}}

        # Load zero budget config
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                zero_budget_config = json.load(f)
        else:
            logger.error("❌ Zero budget config not found")
            return

        # Add zero budget models to the configuration
        zero_budget_models = zero_budget_config["zero_budget_alternatives"]["providers"]

        # Add Ollama models
        if self.setup_status["ollama"]:
            for tier, models in zero_budget_models["ollama"]["models"].items():
                for model_name, model_config in models.items():
                    config["model_selection"]["model_configs"][model_name] = {
                        "provider": "ollama",
                        "tier": tier.replace("_tier", ""),
                        "cost_per_1k_tokens": 0.0,
                        "max_tokens": model_config["max_tokens"],
                        "capabilities": model_config["capabilities"],
                        "fallback_models": [],
                        "enabled": True,
                    }

        # Add Hugging Face models
        if self.setup_status["huggingface"]:
            for tier, models in zero_budget_models["huggingface"]["models"].items():
                for model_name, model_config in models.items():
                    config["model_selection"]["model_configs"][model_name] = {
                        "provider": "huggingface",
                        "tier": tier.replace("_tier", ""),
                        "cost_per_1k_tokens": 0.0,
                        "max_tokens": model_config["max_tokens"],
                        "capabilities": model_config["capabilities"],
                        "fallback_models": [],
                        "enabled": True,
                    }

        # Add Groq models
        if self.setup_status["groq"]:
            for tier, models in zero_budget_models["groq"]["models"].items():
                for model_name, model_config in models.items():
                    config["model_selection"]["model_configs"][model_name] = {
                        "provider": "groq",
                        "tier": tier.replace("_tier", ""),
                        "cost_per_1k_tokens": 0.0,
                        "max_tokens": model_config["max_tokens"],
                        "capabilities": model_config["capabilities"],
                        "fallback_models": [],
                        "enabled": True,
                    }

        # Save updated config
        with open(model_config_path, "w") as f:
            json.dump(config, f, indent=2)

        logger.info("✅ Model configuration updated")

    async def _test_setup(self):
        """Test the zero budget LLM setup."""
        logger.info("🧪 Testing setup...")

        test_results = {}

        # Test Ollama
        if self.setup_status["ollama"]:
            test_results["ollama"] = await self._test_ollama()

        # Test Hugging Face
        if self.setup_status["huggingface"]:
            test_results["huggingface"] = await self._test_huggingface()

        # Test Groq
        if self.setup_status["groq"]:
            test_results["groq"] = await self._test_groq()

        # Print test results
        logger.info("📊 Test Results:")
        for provider, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"  {provider}: {status}")

    async def _test_ollama(self) -> bool:
        """Test Ollama functionality."""
        logger.info("🧪 Testing Ollama...")

        try:
            # Test basic API
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://localhost:11434/api/tags", timeout=5.0
                )
                if response.status_code != 200:
                    logger.error("❌ Ollama API not responding")
                    return False

            # Test model generation
            test_prompt = "Hello, how are you?"
            test_data = {"model": "llama3.2:3b", "prompt": test_prompt, "stream": False}

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:11434/api/generate", json=test_data, timeout=30.0
                )
                if response.status_code == 200:
                    logger.info("✅ Ollama test successful")
                    return True
                else:
                    logger.error(f"❌ Ollama generation failed: {response.status_code}")
                    return False

        except Exception as e:
            logger.error(f"❌ Ollama test failed: {e}")
            return False

    async def _test_huggingface(self) -> bool:
        """Test Hugging Face API."""
        logger.info("🧪 Testing Hugging Face...")

        try:
            api_key = settings.huggingface_api_key
            if not api_key:
                logger.warning("⚠️  No Hugging Face API key configured")
                return False

            headers = {"Authorization": f"Bearer {api_key}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://huggingface.co/api/models", headers=headers, timeout=10.0
                )
                if response.status_code == 200:
                    logger.info("✅ Hugging Face test successful")
                    return True
                else:
                    logger.error(f"❌ Hugging Face test failed: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"❌ Hugging Face test failed: {e}")
            return False

    async def _test_groq(self) -> bool:
        """Test Groq API."""
        logger.info("🧪 Testing Groq...")

        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                logger.warning("⚠️  No Groq API key configured")
                return False

            headers = {"Authorization": f"Bearer {api_key}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.groq.com/openai/v1/models",
                    headers=headers,
                    timeout=10.0,
                )
                if response.status_code == 200:
                    logger.info("✅ Groq test successful")
                    return True
                else:
                    logger.error(f"❌ Groq test failed: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"❌ Groq test failed: {e}")
            return False

    def _print_summary(self):
        """Print setup summary."""
        logger.info("\n" + "=" * 50)
        logger.info("🎉 ZERO BUDGET LLM SETUP SUMMARY")
        logger.info("=" * 50)

        for provider, status in self.setup_status.items():
            status_icon = "✅" if status else "❌"
            logger.info(
                f"{status_icon} {provider.upper()}: {'Ready' if status else 'Not Ready'}"
            )

        logger.info("\n📋 Next Steps:")
        logger.info("1. Set environment variables for API keys (if not done)")
        logger.info("2. Test your agents with the new models")
        logger.info("3. Monitor performance and adjust model selection")

        logger.info("\n💡 Tips:")
        logger.info("- Ollama models run locally - no internet required")
        logger.info("- Hugging Face has 30k requests/month free")
        logger.info("- Groq has 10k requests/day free")
        logger.info("- Use smaller models for faster responses")

        logger.info("\n🔗 Useful Links:")
        logger.info("- Ollama: https://ollama.ai")
        logger.info("- Hugging Face: https://huggingface.co")
        logger.info("- Groq: https://console.groq.com")


async def main():
    """Main function."""
    setup = ZeroBudgetLLMSetup()
    success = await setup.run_setup()
    return success


if __name__ == "__main__":
    asyncio.run(main())
