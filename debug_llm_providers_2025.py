#!/usr/bin/env python3
"""
Debug LLM Providers - 2025 Latest Tech
Test each provider individually to identify issues
"""

import os
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_all_providers():
    """Test all LLM providers individually"""
    
    print("🔥 2025 LLM PROVIDERS DEBUG TEST")
    print("=" * 60)
    print("📅 Testing latest models post-Nov 2024")
    print()
    
    # Test environment variables
    print("🔐 ENVIRONMENT VARIABLES CHECK:")
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
    
    # Test HuggingFace (Primary)
    print("🚀 TESTING HUGGINGFACE (PRIMARY - FREE)")
    print("=" * 40)
    await test_huggingface()
    
    # Test OpenAI (Latest 2025 models)
    print("\n💰 TESTING OPENAI (LATEST 2025 MODELS)")
    print("=" * 40)
    await test_openai()
    
    # Test Anthropic (Latest Claude)
    print("\n💰 TESTING ANTHROPIC (LATEST CLAUDE)")
    print("=" * 40)
    await test_anthropic()
    
    # Test Ollama (Local)
    print("\n🔄 TESTING OLLAMA (LOCAL)")
    print("=" * 40)
    await test_ollama()

async def test_huggingface():
    """Test HuggingFace free models"""
    try:
        import aiohttp
        
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not api_key or api_key == "your_huggingface_api_key_here":
            print("   ❌ API Key not set - skipping")
            return
        
        # Test with GPT-2 (reliable free model)
        url = "https://api-inference.huggingface.co/models/gpt2"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {"inputs": "What is artificial intelligence?"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=30) as response:
                print(f"   📡 Status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    if isinstance(result, list) and len(result) > 0:
                        generated_text = result[0].get("generated_text", "")
                        print(f"   ✅ Success! Generated {len(generated_text)} chars")
                        print(f"   🎯 Preview: {generated_text[:100]}...")
                    else:
                        print(f"   ⚠️ Unexpected response format: {result}")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error: {error_text}")
                    
    except Exception as e:
        print(f"   ❌ Exception: {e}")

async def test_openai():
    """Test OpenAI latest 2025 models"""
    try:
        import openai
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            print("   ❌ API Key not set - skipping")
            return
        
        client = openai.OpenAI(api_key=api_key)
        
        # Test with GPT-4o-mini (latest cost-efficient model)
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "What is AI?"}],
            max_tokens=100,
            timeout=30
        )
        
        content = response.choices[0].message.content
        print(f"   ✅ GPT-4o-mini Success! Generated {len(content)} chars")
        print(f"   🎯 Preview: {content[:100]}...")
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")

async def test_anthropic():
    """Test Anthropic latest Claude models"""
    try:
        import anthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or api_key == "your_anthropic_api_key_here":
            print("   ❌ API Key not set - skipping")
            return
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Test with latest Claude 3.5 Haiku
        message = await asyncio.to_thread(
            client.messages.create,
            model="claude-3-5-haiku-20241022",
            max_tokens=100,
            messages=[{"role": "user", "content": "What is AI?"}]
        )
        
        content = message.content[0].text
        print(f"   ✅ Claude-3.5-Haiku Success! Generated {len(content)} chars")
        print(f"   🎯 Preview: {content[:100]}...")
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")

async def test_ollama():
    """Test Ollama local models"""
    try:
        import aiohttp
        
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Test connection
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/api/tags", timeout=10) as response:
                if response.status == 200:
                    models = await response.json()
                    model_names = [m["name"] for m in models.get("models", [])]
                    print(f"   ✅ Connected! Available models: {model_names}")
                    
                    if model_names:
                        # Test with first available model
                        test_model = model_names[0]
                        payload = {
                            "model": test_model,
                            "prompt": "What is AI?",
                            "stream": False
                        }
                        
                        async with session.post(
                            f"{base_url}/api/generate", 
                            json=payload, 
                            timeout=30
                        ) as gen_response:
                            if gen_response.status == 200:
                                result = await gen_response.json()
                                response_text = result.get("response", "")
                                print(f"   ✅ {test_model} Success! Generated {len(response_text)} chars")
                                print(f"   🎯 Preview: {response_text[:100]}...")
                            else:
                                error = await gen_response.text()
                                print(f"   ❌ Generation failed: {error}")
                    else:
                        print("   ⚠️ No models available")
                else:
                    print(f"   ❌ Connection failed: {response.status}")
                    
    except Exception as e:
        print(f"   ❌ Exception: {e}")

async def main():
    """Run all provider tests"""
    await test_all_providers()
    
    print("\n🎯 SUMMARY & RECOMMENDATIONS")
    print("=" * 60)
    print("1. Check which providers are working above")
    print("2. For non-working providers, verify API keys in .env")
    print("3. For Ollama, ensure it's running locally")
    print("4. HuggingFace should be primary (free)")
    print("5. OpenAI/Anthropic are paid fallbacks")
    print("\n✅ Debug complete!")

if __name__ == "__main__":
    asyncio.run(main())
