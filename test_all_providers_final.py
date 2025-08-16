#!/usr/bin/env python3
"""
Final Comprehensive Test - All LLM Providers with Dynamic Selection
MAANG/OpenAI/Perplexity Standards Implementation
"""

import os
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_all_providers_final():
    """Test all LLM providers with proper dynamic selection"""
    
    print("🔥 FINAL COMPREHENSIVE LLM PROVIDERS TEST")
    print("=" * 60)
    print("📋 MAANG/OpenAI/Perplexity Standards Implementation")
    print()
    
    # Test environment variables
    print("🔐 ENVIRONMENT VARIABLES:")
    print("=" * 40)
    
    providers = {
        "HuggingFace": os.getenv("HUGGINGFACE_API_KEY"),
        "OpenAI": os.getenv("OPENAI_API_KEY"), 
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "Ollama": "http://localhost:11434"
    }
    
    for name, key in providers.items():
        status = "✅ SET" if key and key != "disabled" and key != "your_*_here" else "❌ DISABLED/MISSING"
        preview = f"({key[:10]}...)" if key and key != "disabled" and key != "your_*_here" else ""
        print(f"   {name:12}: {status} {preview}")
    
    print(f"   Priority Free: {os.getenv('PRIORITIZE_FREE_MODELS', 'Not Set')}")
    print(f"   Dynamic Select: {os.getenv('USE_DYNAMIC_SELECTION', 'Not Set')}")
    print()
    
    # Test scenarios
    print("🧪 TESTING SCENARIOS:")
    print("=" * 40)
    
    # Scenario 1: All providers available (free-first)
    print("\n🚀 SCENARIO 1: All Providers Available (Free-First)")
    print("-" * 50)
    await test_scenario("all_available", "What is artificial intelligence?")
    
    # Scenario 2: OpenAI disabled (should use HuggingFace)
    print("\n🚀 SCENARIO 2: OpenAI Disabled (Should Use HuggingFace)")
    print("-" * 50)
    await test_scenario("openai_disabled", "What is machine learning?")
    
    # Scenario 3: HuggingFace disabled (should use Ollama)
    print("\n🔄 SCENARIO 3: HuggingFace Disabled (Should Use Ollama)")
    print("-" * 50)
    await test_scenario("huggingface_disabled", "What is deep learning?")
    
    # Scenario 4: Only Ollama available
    print("\n🔄 SCENARIO 4: Only Ollama Available")
    print("-" * 50)
    await test_scenario("ollama_only", "What is natural language processing?")
    
    print("\n✅ COMPREHENSIVE TEST COMPLETE!")

async def test_scenario(scenario: str, query: str):
    """Test a specific scenario"""
    try:
        import aiohttp
        
        # Set environment variables for scenario
        if scenario == "all_available":
            os.environ["OPENAI_API_KEY"] = "sk-test-key"
            os.environ["HUGGINGFACE_API_KEY"] = "hf-test-key"
            os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test-key"
        elif scenario == "openai_disabled":
            os.environ["OPENAI_API_KEY"] = "disabled"
            os.environ["HUGGINGFACE_API_KEY"] = "hf-test-key"
            os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test-key"
        elif scenario == "huggingface_disabled":
            os.environ["OPENAI_API_KEY"] = "disabled"
            os.environ["HUGGINGFACE_API_KEY"] = "disabled"
            os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test-key"
        elif scenario == "ollama_only":
            os.environ["OPENAI_API_KEY"] = "disabled"
            os.environ["HUGGINGFACE_API_KEY"] = "disabled"
            os.environ["ANTHROPIC_API_KEY"] = "disabled"
        
        os.environ["PRIORITIZE_FREE_MODELS"] = "true"
        os.environ["USE_DYNAMIC_SELECTION"] = "true"
        
        # Create request payload
        payload = {
            "query": query,
            "user_id": "test_user"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://127.0.0.1:8002/search",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    selected_provider = result.get("selected_provider", "unknown")
                    processing_time = result.get("processing_time_ms", 0)
                    print(f"   ✅ Success! Provider: {selected_provider}, Time: {processing_time}ms")
                    
                    # Validate provider selection
                    expected_provider = get_expected_provider(scenario)
                    if selected_provider == expected_provider:
                        print(f"   ✅ Provider selection correct: {selected_provider}")
                    else:
                        print(f"   ⚠️ Provider selection unexpected: {selected_provider} (expected: {expected_provider})")
                    
                else:
                    print(f"   ❌ HTTP {response.status}: {await response.text()}")
                    
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def get_expected_provider(scenario: str) -> str:
    """Get expected provider for each scenario"""
    if scenario == "all_available":
        return "huggingface"  # Free-first strategy
    elif scenario == "openai_disabled":
        return "huggingface"  # Free-first strategy
    elif scenario == "huggingface_disabled":
        return "ollama"  # Local model
    elif scenario == "ollama_only":
        return "ollama"  # Only available
    return "unknown"

if __name__ == "__main__":
    asyncio.run(test_all_providers_final())
