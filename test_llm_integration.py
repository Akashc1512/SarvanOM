from shared.core.api.config import get_settings
#!/usr/bin/env python3
settings = get_settings()
"""
Test LLM Integration
Verifies that Ollama and Hugging Face are properly integrated into the existing LLM client
"""

import asyncio
import os
import sys
from pathlib import Path
import logging

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

from shared.core.llm_client_v3 import EnhancedLLMClientV3, LLMProvider, LLMConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_llm_integration():
    """Test the integration of Ollama and Hugging Face with the existing LLM client."""
    
    logger.info("🧪 Testing LLM Integration with Ollama and Hugging Face")
    
    # Test configurations
    test_configs = []
    
    # Test Ollama if available
    if getattr(settings.ollama_enabled, 'value', "true") if hasattr(settings.ollama_enabled, 'value') else settings.ollama_enabled.lower() == "true":
        test_configs.append(
            LLMConfig(
                provider=LLMProvider.OLLAMA,
                model="llama3.2:3b",
                api_key="",
                base_url="http://localhost:11434",
                timeout=60
            )
        )
        logger.info("✅ Added Ollama test configuration")
    
    # Test Hugging Face if API key is available
    if settings.huggingface_api_key:
        test_configs.append(
            LLMConfig(
                provider=LLMProvider.HUGGINGFACE,
                model="microsoft/DialoGPT-medium",
                api_key=settings.huggingface_api_key,
                timeout=30
            )
        )
        logger.info("✅ Added Hugging Face test configuration")
    
    if not test_configs:
        logger.warning("⚠️  No test configurations available. Set OLLAMA_ENABLED=true or HUGGINGFACE_API_KEY")
        return
    
    # Create LLM client with test configurations
    client = EnhancedLLMClientV3(configs=test_configs)
    
    # Test prompts
    test_prompts = [
        "Hello, how are you?",
        "What is the capital of France?",
        "Write a simple Python function to add two numbers.",
        "Explain the concept of machine learning in one sentence."
    ]
    
    logger.info(f"📊 Testing with {len(test_configs)} providers")
    
    for i, prompt in enumerate(test_prompts, 1):
        logger.info(f"\n🔍 Test {i}: {prompt[:50]}...")
        
        try:
            # Test text generation
            response = await client.generate_text(
                prompt=prompt,
                max_tokens=100,
                temperature=0.1
            )
            
            logger.info(f"✅ Response: {response[:100]}...")
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
    
    # Test health check
    logger.info("\n🏥 Testing health check...")
    try:
        health_status = await client.health_check()
        logger.info(f"✅ Health status: {health_status}")
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
    
    # Test metrics
    logger.info("\n📈 Testing metrics...")
    try:
        metrics = client.get_metrics()
        logger.info(f"✅ Metrics: {metrics}")
    except Exception as e:
        logger.error(f"❌ Metrics failed: {e}")
    
    logger.info("\n🎉 LLM Integration Test Complete!")

async def test_provider_specific():
    """Test specific provider functionality."""
    
    logger.info("\n🔧 Testing Provider-Specific Functionality")
    
    # Test Ollama provider directly
    if getattr(settings.ollama_enabled, 'value', "true") if hasattr(settings.ollama_enabled, 'value') else settings.ollama_enabled.lower() == "true":
        logger.info("Testing Ollama Provider...")
        
        from shared.core.llm_client_v3 import OllamaProvider, LLMRequest
        
        ollama_config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="llama3.2:3b",
            api_key="",
            base_url="http://localhost:11434",
            timeout=60
        )
        
        try:
            ollama_provider = OllamaProvider(ollama_config)
            
            # Test health check
            health = await ollama_provider.health_check()
            logger.info(f"Ollama health: {health}")
            
            # Test provider info
            info = ollama_provider.get_provider_info()
            logger.info(f"Ollama info: {info}")
            
        except Exception as e:
            logger.error(f"Ollama provider test failed: {e}")
    
    # Test Hugging Face provider directly
    if settings.huggingface_api_key:
        logger.info("Testing Hugging Face Provider...")
        
        from shared.core.llm_client_v3 import HuggingFaceProvider
        
        hf_config = LLMConfig(
            provider=LLMProvider.HUGGINGFACE,
            model="microsoft/DialoGPT-medium",
            api_key=settings.huggingface_api_key,
            timeout=30
        )
        
        try:
            hf_provider = HuggingFaceProvider(hf_config)
            
            # Test health check
            health = await hf_provider.health_check()
            logger.info(f"Hugging Face health: {health}")
            
            # Test provider info
            info = hf_provider.get_provider_info()
            logger.info(f"Hugging Face info: {info}")
            
        except Exception as e:
            logger.error(f"Hugging Face provider test failed: {e}")

def print_setup_instructions():
    """Print setup instructions for the new providers."""
    
    logger.info("\n" + "="*60)
    logger.info("📋 SETUP INSTRUCTIONS")
    logger.info("="*60)
    
    logger.info("\n🔧 Ollama Setup:")
    logger.info("1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
    logger.info("2. Pull models: ollama pull llama3.2:3b")
    logger.info("3. Set environment: export OLLAMA_ENABLED=true")
    logger.info("4. Optional: export OLLAMA_MODEL=llama3.2:8b")
    
    logger.info("\n🔧 Hugging Face Setup:")
    logger.info("1. Get API key: https://huggingface.co/settings/tokens")
    logger.info("2. Set environment: export HUGGINGFACE_API_KEY='your_key'")
    logger.info("3. Optional: export HUGGINGFACE_MODEL='microsoft/DialoGPT-large'")
    
    logger.info("\n🔧 Environment Variables:")
    logger.info("OLLAMA_ENABLED=true")
    logger.info("OLLAMA_MODEL=llama3.2:3b")
    logger.info("OLLAMA_BASE_URL=http://localhost:11434")
    logger.info("HUGGINGFACE_API_KEY=your_key_here")
    logger.info("HUGGINGFACE_MODEL=microsoft/DialoGPT-medium")
    
    logger.info("\n💡 Usage Example:")
    logger.info("from shared.core.llm_client_v3 import EnhancedLLMClientV3")
    logger.info("client = EnhancedLLMClientV3()")
    logger.info("response = await client.generate_text('Hello, world!')")

async def main():
    """Main test function."""
    
    logger.info("🚀 Starting LLM Integration Tests")
    
    # Print setup instructions
    print_setup_instructions()
    
    # Test basic integration
    await test_llm_integration()
    
    # Test provider-specific functionality
    await test_provider_specific()
    
    logger.info("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 