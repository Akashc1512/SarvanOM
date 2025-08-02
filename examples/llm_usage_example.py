from ..\shared\core\api\config import get_settings
#!/usr/bin/env python3
settings = get_settings()
"""
LLM Usage Example
Demonstrates how to use Ollama and Hugging Face providers with the existing LLM client
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

from shared.core.llm_client_v3 import EnhancedLLMClientV3, LLMProvider, LLMConfig

async def example_usage():
    """Example usage of the enhanced LLM client with Ollama and Hugging Face."""
    
    print("🚀 LLM Usage Example with Ollama and Hugging Face")
    print("=" * 60)
    
    # Example 1: Using the default client (auto-detects available providers)
    print("\n📋 Example 1: Default Client (Auto-detection)")
    print("-" * 40)
    
    client = EnhancedLLMClientV3()
    
    # Test with a simple prompt
    try:
        response = await client.generate_text(
            prompt="Hello, how are you?",
            max_tokens=50,
            temperature=0.1
        )
        print(f"✅ Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 2: Explicit configuration with Ollama
    print("\n📋 Example 2: Explicit Ollama Configuration")
    print("-" * 40)
    
    ollama_config = LLMConfig(
        provider=LLMProvider.OLLAMA,
        model="llama3.2:3b",
        api_key="",  # No API key needed for local models
        base_url="http://localhost:11434",
        timeout=60
    )
    
    ollama_client = EnhancedLLMClientV3(configs=[ollama_config])
    
    try:
        response = await ollama_client.generate_text(
            prompt="What is the capital of France?",
            max_tokens=100,
            temperature=0.1
        )
        print(f"✅ Ollama Response: {response}")
    except Exception as e:
        print(f"❌ Ollama Error: {e}")
    
    # Example 3: Explicit configuration with Hugging Face
    print("\n📋 Example 3: Explicit Hugging Face Configuration")
    print("-" * 40)
    
    if settings.huggingface_api_key:
        hf_config = LLMConfig(
            provider=LLMProvider.HUGGINGFACE,
            model="microsoft/DialoGPT-medium",
            api_key=settings.huggingface_api_key,
            timeout=30
        )
        
        hf_client = EnhancedLLMClientV3(configs=[hf_config])
        
        try:
            response = await hf_client.generate_text(
                prompt="Write a simple Python function to add two numbers.",
                max_tokens=150,
                temperature=0.1
            )
            print(f"✅ Hugging Face Response: {response}")
        except Exception as e:
            print(f"❌ Hugging Face Error: {e}")
    else:
        print("⚠️  HUGGINGFACE_API_KEY not set, skipping Hugging Face example")
    
    # Example 4: Multi-provider setup with fallback
    print("\n📋 Example 4: Multi-Provider Setup with Fallback")
    print("-" * 40)
    
    multi_configs = []
    
    # Add Ollama if available
    if getattr(settings.ollama_enabled, 'value', "true") if hasattr(settings.ollama_enabled, 'value') else settings.ollama_enabled.lower() == "true":
        multi_configs.append(
            LLMConfig(
                provider=LLMProvider.OLLAMA,
                model="llama3.2:8b",
                api_key="",
                base_url="http://localhost:11434",
                timeout=60
            )
        )
    
    # Add Hugging Face if API key is available
    if settings.huggingface_api_key:
        multi_configs.append(
            LLMConfig(
                provider=LLMProvider.HUGGINGFACE,
                model="microsoft/DialoGPT-large",
                api_key=settings.huggingface_api_key,
                timeout=30
            )
        )
    
    if multi_configs:
        multi_client = EnhancedLLMClientV3(configs=multi_configs)
        
        try:
            response = await multi_client.generate_text(
                prompt="Explain the concept of machine learning in simple terms.",
                max_tokens=200,
                temperature=0.1
            )
            print(f"✅ Multi-Provider Response: {response}")
        except Exception as e:
            print(f"❌ Multi-Provider Error: {e}")
    else:
        print("⚠️  No providers configured for multi-provider example")
    
    # Example 5: Task-specific model selection
    print("\n📋 Example 5: Task-Specific Model Selection")
    print("-" * 40)
    
    # Define task-specific configurations
    task_configs = {
        "general": LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="llama3.2:3b",
            api_key="",
            base_url="http://localhost:11434"
        ),
        "code": LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="codellama:7b",
            api_key="",
            base_url="http://localhost:11434"
        ),
        "analysis": LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="llama3.2:8b",
            api_key="",
            base_url="http://localhost:11434"
        )
    }
    
    # Test different task types
    tasks = [
        ("general", "What is the weather like today?"),
        ("code", "Write a Python function to calculate fibonacci numbers"),
        ("analysis", "Analyze the benefits of renewable energy sources")
    ]
    
    for task_type, prompt in tasks:
        if task_type in task_configs:
            task_client = EnhancedLLMClientV3(configs=[task_configs[task_type]])
            
            try:
                response = await task_client.generate_text(
                    prompt=prompt,
                    max_tokens=100,
                    temperature=0.1
                )
                print(f"✅ {task_type.title()} Task: {response[:100]}...")
            except Exception as e:
                print(f"❌ {task_type.title()} Task Error: {e}")
    
    print("\n🎉 Usage Examples Complete!")

async def test_health_and_metrics():
    """Test health checks and metrics for the new providers."""
    
    print("\n🏥 Health Check and Metrics Test")
    print("=" * 40)
    
    client = EnhancedLLMClientV3()
    
    # Test health check
    try:
        health_status = await client.health_check()
        print("✅ Health Status:")
        for provider, status in health_status.items():
            print(f"  {provider}: {'🟢 Healthy' if status else '🔴 Unhealthy'}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test metrics
    try:
        metrics = client.get_metrics()
        print("\n📈 Metrics:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value}")
    except Exception as e:
        print(f"❌ Metrics failed: {e}")

def print_environment_setup():
    """Print environment setup instructions."""
    
    print("\n🔧 Environment Setup Instructions")
    print("=" * 40)
    
    print("\n1. Ollama Setup:")
    print("   curl -fsSL https://ollama.ai/install.sh | sh")
    print("   ollama pull llama3.2:3b")
    print("   ollama pull llama3.2:8b")
    print("   ollama pull codellama:7b")
    
    print("\n2. Environment Variables:")
    print("   export OLLAMA_ENABLED=true")
    print("   export OLLAMA_MODEL=llama3.2:3b")
    print("   export OLLAMA_BASE_URL=http://localhost:11434")
    print("   export HUGGINGFACE_API_KEY=your_key_here")
    print("   export HUGGINGFACE_MODEL=microsoft/DialoGPT-medium")
    
    print("\n3. Test the setup:")
    print("   python test_llm_integration.py")

async def main():
    """Main function."""
    
    print_environment_setup()
    
    # Run usage examples
    await example_usage()
    
    # Test health and metrics
    await test_health_and_metrics()
    
    print("\n✅ All examples completed successfully!")

if __name__ == "__main__":
    asyncio.run(main()) 