#!/usr/bin/env python3
"""
Test All LLM Providers - Comprehensive Check
"""

import os
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_llm_providers():
    """Test all LLM providers in the system"""
    
    print("🔥 COMPREHENSIVE LLM PROVIDERS TEST")
    print("=" * 60)
    
    # Test environment variables
    print("🔐 ENVIRONMENT VARIABLES:")
    print("=" * 40)
    
    providers = {
        "HuggingFace": os.getenv("HUGGINGFACE_API_KEY"),
        "OpenAI": os.getenv("OPENAI_API_KEY"), 
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "Ollama": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    }
    
    for name, key in providers.items():
        status = "✅ SET" if key and key != "your_*_here" else "❌ MISSING"
        preview = f"({key[:10]}...)" if key and key != "your_*_here" else ""
        print(f"   {name:12}: {status} {preview}")
    
    print(f"   Priority Free: {os.getenv('PRIORITIZE_FREE_MODELS', 'Not Set')}")
    print(f"   Dynamic Select: {os.getenv('USE_DYNAMIC_SELECTION', 'Not Set')}")
    print()
    
    # Test each provider individually
    print("🧪 TESTING INDIVIDUAL PROVIDERS:")
    print("=" * 40)
    
    # Test HuggingFace
    print("\n🚀 TESTING HUGGINGFACE:")
    await test_provider("huggingface", "What is artificial intelligence?")
    
    # Test OpenAI
    print("\n💰 TESTING OPENAI:")
    await test_provider("openai", "What is machine learning?")
    
    # Test Anthropic
    print("\n💰 TESTING ANTHROPIC:")
    await test_provider("anthropic", "What is deep learning?")
    
    # Test Ollama
    print("\n🔄 TESTING OLLAMA:")
    await test_provider("ollama", "What is natural language processing?")
    
    print("\n✅ COMPREHENSIVE TEST COMPLETE!")

async def test_provider(provider_name: str, query: str):
    """Test a specific provider"""
    try:
        import aiohttp
        
        # Set environment variables for this test
        os.environ["PRIORITIZE_FREE_MODELS"] = "true"
        os.environ["USE_DYNAMIC_SELECTION"] = "true"
        
        # Create request payload
        payload = {
            "query": query,
            "user_id": "test_user",
            "provider": provider_name
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://127.0.0.1:8001/search",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    selected_provider = result.get("selected_provider", "unknown")
                    processing_time = result.get("processing_time_ms", 0)
                    print(f"   ✅ Success! Provider: {selected_provider}, Time: {processing_time}ms")
                    
                    # Show AI analysis preview
                    ai_analysis = result.get("ai_analysis", "")
                    if ai_analysis:
                        # Extract key info from JSON
                        try:
                            analysis_data = json.loads(ai_analysis.replace("```json\n", "").replace("\n```", ""))
                            complexity = analysis_data.get("complexity_assessment", "unknown")
                            intent = analysis_data.get("query_intent_classification", "unknown")
                            print(f"   📊 Analysis: {intent} query, {complexity} complexity")
                        except:
                            print(f"   📊 Analysis: {ai_analysis[:100]}...")
                else:
                    print(f"   ❌ HTTP {response.status}: {await response.text()}")
                    
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_llm_providers())
