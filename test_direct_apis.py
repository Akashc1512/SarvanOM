#!/usr/bin/env python3
"""
Direct API Testing - Test each provider individually
To identify why responses are slow even with working API keys
"""

import asyncio
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_openai_direct():
    """Test OpenAI API directly for speed"""
    print("🚀 TESTING OPENAI DIRECT")
    print("=" * 40)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or "your_" in api_key:
        print("❌ OpenAI API key not set")
        return False
    
    try:
        import openai
        
        client = openai.OpenAI(api_key=api_key)
        
        start_time = time.time()
        
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4o-mini",  # Fast, cost-efficient model
            messages=[{"role": "user", "content": "What is AI? (brief answer)"}],
            max_tokens=100,
            temperature=0.7,
            timeout=10
        )
        
        elapsed = time.time() - start_time
        content = response.choices[0].message.content
        
        print(f"⏱️ Response Time: {elapsed:.2f}s")
        print(f"🤖 Content: {content}")
        print(f"✅ Success: {elapsed <= 5}")
        
        return elapsed <= 5
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Error after {elapsed:.2f}s: {e}")
        return False

async def test_anthropic_direct():
    """Test Anthropic API directly for speed"""
    print("\n🚀 TESTING ANTHROPIC DIRECT")
    print("=" * 40)
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or "your_" in api_key:
        print("❌ Anthropic API key not set")
        return False
    
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=api_key)
        
        start_time = time.time()
        
        message = await asyncio.to_thread(
            client.messages.create,
            model="claude-3-5-haiku-20241022",  # Fast model
            max_tokens=100,
            messages=[{"role": "user", "content": "What is AI? (brief answer)"}]
        )
        
        elapsed = time.time() - start_time
        content = message.content[0].text
        
        print(f"⏱️ Response Time: {elapsed:.2f}s")
        print(f"🤖 Content: {content}")
        print(f"✅ Success: {elapsed <= 5}")
        
        return elapsed <= 5
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Error after {elapsed:.2f}s: {e}")
        return False

async def test_huggingface_direct():
    """Test HuggingFace API directly for speed"""
    print("\n🚀 TESTING HUGGINGFACE DIRECT")
    print("=" * 40)
    
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key or "your_" in api_key:
        print("❌ HuggingFace API key not set")
        return False
    
    try:
        import aiohttp
        
        url = "https://api-inference.huggingface.co/models/gpt2"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {"inputs": "What is AI?", "parameters": {"max_length": 50}}
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=10) as response:
                elapsed = time.time() - start_time
                
                print(f"⏱️ Response Time: {elapsed:.2f}s")
                print(f"📡 Status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    if isinstance(result, list) and len(result) > 0:
                        content = result[0].get("generated_text", "")
                        print(f"🤖 Content: {content}")
                        print(f"✅ Success: {elapsed <= 5}")
                        return elapsed <= 5
                    else:
                        print(f"⚠️ Unexpected format: {result}")
                        return False
                else:
                    error = await response.text()
                    print(f"❌ Error: {error}")
                    return False
                    
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Error after {elapsed:.2f}s: {e}")
        return False

async def main():
    """Test all providers directly"""
    print("🎯 DIRECT API SPEED TEST")
    print("🎯 Target: < 5 seconds per call")
    print("=" * 60)
    
    results = {}
    
    # Test each provider
    results["openai"] = await test_openai_direct()
    results["anthropic"] = await test_anthropic_direct()
    results["huggingface"] = await test_huggingface_direct()
    
    print("\n🎯 SUMMARY")
    print("=" * 40)
    working_providers = [name for name, success in results.items() if success]
    
    for provider, success in results.items():
        status = "✅ FAST" if success else "❌ SLOW/FAILED"
        print(f"{provider.upper()}: {status}")
    
    if working_providers:
        print(f"\n🚀 WORKING FAST PROVIDERS: {', '.join(working_providers).upper()}")
        print("💡 The backend should use these for 5-second responses")
    else:
        print("\n❌ NO FAST PROVIDERS FOUND")
        print("🔧 All APIs are slow or not working")

if __name__ == "__main__":
    asyncio.run(main())
