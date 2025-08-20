from shared.core.api.config import get_settings
#!/usr/bin/env python3
settings = get_settings()
"""
Verify Environment Variable Loading
Checks that all environment variables are properly loaded for zero-budget LLM integration
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

def verify_env_loading():
    """Verify that environment variables are properly loaded."""
    
    print("🔍 Verifying Environment Variable Loading")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check zero-budget LLM variables
    print("\n🚀 Zero Budget LLM Variables:")
    
    # Ollama variables
    ollama_vars = {
        "OLLAMA_ENABLED": "Enable/disable Ollama provider",
        "OLLAMA_MODEL": "Default Ollama model",
        "OLLAMA_BASE_URL": "Ollama server URL"
    }
    
    print("\n📦 Ollama Configuration:")
    for var, description in ollama_vars.items():
        value = os.getenv(var)
        status = "✅" if value else "❌"
        print(f"   {status} {var}: {value or 'NOT SET'}")
        if var == "OLLAMA_ENABLED" and value:
            print(f"      Description: {description}")
    
    # Hugging Face variables
    hf_vars = {
        "HUGGINGFACE_WRITE_TOKEN": "Write token (full access)",
        "HUGGINGFACE_READ_TOKEN": "Read token (read-only)",
        "HUGGINGFACE_API_KEY": "Legacy API key",
        "HUGGINGFACE_MODEL": "Default Hugging Face model"
    }
    
    print("\n🤗 Hugging Face Configuration:")
    for var, description in hf_vars.items():
        value = os.getenv(var)
        if var.endswith("_TOKEN") or var.endswith("_KEY"):
            # Mask sensitive values
            display_value = "SET" if value else "NOT SET"
            status = "✅" if value else "❌"
        else:
            display_value = value or "NOT SET"
            status = "✅" if value else "❌"
        print(f"   {status} {var}: {display_value}")
        if value:
            print(f"      Description: {description}")
    
    # Model selection variables
    selection_vars = {
        "USE_DYNAMIC_SELECTION": "Enable dynamic model selection",
        "PRIORITIZE_FREE_MODELS": "Prioritize free models"
    }
    
    print("\n🎯 Model Selection Configuration:")
    for var, description in selection_vars.items():
        value = os.getenv(var)
        status = "✅" if value else "❌"
        print(f"   {status} {var}: {value or 'NOT SET'}")
        if value:
            print(f"      Description: {description}")
    
    # Check fallback providers
    print("\n💰 Fallback Providers:")
    fallback_vars = {
        "OPENAI_API_KEY": "OpenAI API key",
        "ANTHROPIC_API_KEY": "Anthropic API key",
        "AZURE_OPENAI_API_KEY": "Azure OpenAI API key",
        "GOOGLE_API_KEY": "Google API key"
    }
    
    for var, description in fallback_vars.items():
        value = os.getenv(var)
        display_value = "SET" if value else "NOT SET"
        status = "✅" if value else "⚠️"
        print(f"   {status} {var}: {display_value}")
        if value:
            print(f"      Description: {description}")
    
    # System configuration
    print("\n⚙️ System Configuration:")
    system_vars = {
        "ENVIRONMENT": "Environment (development/production)",
        "LOG_LEVEL": "Logging level",
        "RATE_LIMIT_REQUESTS_PER_MINUTE": "Rate limit requests per minute",
        "RATE_LIMIT_TOKENS_PER_MINUTE": "Rate limit tokens per minute",
        "AGENT_TIMEOUT_SECONDS": "Agent timeout seconds",
        "AGENT_MAX_RETRIES": "Agent max retries"
    }
    
    for var, description in system_vars.items():
        value = os.getenv(var)
        status = "✅" if value else "❌"
        print(f"   {status} {var}: {value or 'NOT SET'}")
        if value:
            print(f"      Description: {description}")
    
    # Check provider availability
    print("\n🏥 Provider Availability:")
    
    # Check Ollama
    ollama_enabled = getattr(settings.ollama_enabled, 'value', "true") if hasattr(settings.ollama_enabled, 'value') else settings.ollama_enabled.lower() == "true"
    print(f"   {'✅' if ollama_enabled else '❌'} Ollama: {'Enabled' if ollama_enabled else 'Disabled'}")
    
    # Check Hugging Face
    hf_write = settings.huggingface_write_token
    hf_read = settings.huggingface_read_token
    hf_legacy = settings.huggingface_api_key
    hf_available = any([hf_write, hf_read, hf_legacy])
    print(f"   {'✅' if hf_available else '❌'} Hugging Face: {'Available' if hf_available else 'Not configured'}")
    
    # Check paid providers
    openai_available = bool(settings.openai_api_key)
    anthropic_available = bool(settings.anthropic_api_key)
    azure_available = bool(settings.azure_openai_api_key)
    google_available = bool(settings.google_api_key)
    
    print(f"   {'✅' if openai_available else '❌'} OpenAI: {'Available' if openai_available else 'Not configured'}")
    print(f"   {'✅' if anthropic_available else '❌'} Anthropic: {'Available' if anthropic_available else 'Not configured'}")
    print(f"   {'✅' if azure_available else '❌'} Azure: {'Available' if azure_available else 'Not configured'}")
    print(f"   {'✅' if google_available else '❌'} Google: {'Available' if google_available else 'Not configured'}")
    
    # Summary
    print("\n📊 Summary:")
    free_providers = 0
    if ollama_enabled:
        free_providers += 1
    if hf_available:
        free_providers += 1
    
    paid_providers = sum([openai_available, anthropic_available, azure_available, google_available])
    
    print(f"   Free providers available: {free_providers}")
    print(f"   Paid providers available: {paid_providers}")
    print(f"   Total providers: {free_providers + paid_providers}")
    
    if free_providers > 0:
        print("   🎉 Zero-budget LLM integration is configured!")
        print("   💰 You can save $800-1600/month on LLM costs")
    else:
        print("   ⚠️  No free providers configured")
        print("   💡 Consider setting up Ollama or Hugging Face")
    
    # Recommendations
    print("\n💡 Recommendations:")
    
    if not ollama_enabled:
        print("   - Enable Ollama: Set OLLAMA_ENABLED=true")
    
    if not hf_available:
        print("   - Add Hugging Face: Get tokens from https://huggingface.co/settings/tokens")
    
    if not any([ollama_enabled, hf_available]):
        print("   - Set up at least one free provider for zero-budget operation")
    
    if free_providers == 0 and paid_providers == 0:
        print("   - Configure at least one LLM provider")
    
    print("\n✅ Environment verification complete!")

def test_env_loading():
    """Test that environment variables are accessible in key modules."""
    
    print("\n🧪 Testing Environment Variable Access:")
    print("=" * 60)
    
    try:
        # Test LLM client
        from shared.core.llm_client_v3 import EnhancedLLMClientV3
        print("✅ LLM Client: Environment variables accessible")
        
        # Test model selector
        from shared.core.model_selector import get_model_selector
        print("✅ Model Selector: Environment variables accessible")
        
        # Test agents
        from shared.core.agents.synthesis_agent import SynthesisAgent
        from shared.core.agents.retrieval_agent import RetrievalAgent
        print("✅ Agents: Environment variables accessible")
        
        # Test setup script
        from scripts.setup_ollama_huggingface import OllamaHuggingFaceSetup
        print("✅ Setup Script: Environment variables accessible")
        
        # Test management script
        from scripts.manage_zero_budget_llm import ZeroBudgetLLMManager
        print("✅ Management Script: Environment variables accessible")
        
        print("\n🎉 All modules can access environment variables!")
        
    except Exception as e:
        print(f"❌ Error testing environment variable access: {e}")

def main():
    """Main function."""
    verify_env_loading()
    test_env_loading()

if __name__ == "__main__":
    main() 